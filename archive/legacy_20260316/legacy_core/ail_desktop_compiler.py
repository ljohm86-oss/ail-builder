from __future__ import annotations

import re
import sys
from functools import partial

import requests
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class PostWorker(QThread):
    finished = pyqtSignal(bool, str, str)

    def __init__(self, url: str, payload: dict[str, str]) -> None:
        super().__init__()
        self.url = url
        self.payload = payload

    def run(self) -> None:
        try:
            # 你的穿甲弹请求
            response = requests.post(
                self.url, 
                json=self.payload, 
                timeout=20,
                proxies={"http": None, "https": None}
            )
            response.raise_for_status()
            
            # 【全新解码逻辑】：处理 Flask 的嵌套 JSON 和 Unicode 中文转义
            import json
            try:
                raw_data = response.json()
                # 如果后端把返回体包在了 "message" 字符串里，我们给它剥离出来
                if "message" in raw_data and isinstance(raw_data["message"], str) and raw_data["message"].startswith("{"):
                    clean_data = json.loads(raw_data["message"])
                    # ensure_ascii=False 是还原中文的终极魔法
                    body = json.dumps(clean_data, indent=4, ensure_ascii=False)
                else:
                    body = json.dumps(raw_data, indent=4, ensure_ascii=False)
            except ValueError:
                # 万一后端返回的不是标准 JSON，兜底直接用 utf-8 解码文本
                body = response.text.encode('utf-8').decode('unicode_escape', errors='replace')
                
            self.finished.emit(True, "高维响应", body)
        except requests.exceptions.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else "unknown"
            detail = exc.response.text if exc.response is not None else str(exc)
            self.finished.emit(False, "Request Failed", f"HTTP {status}: {detail}")
        except requests.exceptions.Timeout:
            self.finished.emit(False, "Request Failed", "Network timeout while contacting server")
        except requests.exceptions.RequestException as exc:
            self.finished.emit(False, "Request Failed", f"Network error: {exc}")
        except Exception as exc:  # pragma: no cover
            self.finished.emit(False, "Request Failed", f"Unexpected error: {exc}")


class DesktopEngine:
    API_BASE = "http://127.0.0.1:5000"

    def __init__(self, ail_code: str) -> None:
        self.ail_code = ail_code
        self.widgets: dict[str, QWidget] = {}
        self.window: QWidget | None = None
        self.layout: QVBoxLayout | None = None
        self._threads: list[PostWorker] = []

    def split_actions(self, code: str) -> list[str]:
        actions: list[str] = []
        current: list[str] = []
        quote_char: str | None = None
        escape = False
        round_depth = 0
        square_depth = 0
        curly_depth = 0

        for char in code:
            if quote_char:
                current.append(char)
                if escape:
                    escape = False
                elif char == "\\":
                    escape = True
                elif char == quote_char:
                    quote_char = None
                continue

            if char in ('"', "'"):
                quote_char = char
                current.append(char)
                continue

            if char == "(":
                round_depth += 1
            elif char == ")":
                round_depth = max(0, round_depth - 1)
            elif char == "[":
                square_depth += 1
            elif char == "]":
                square_depth = max(0, square_depth - 1)
            elif char == "{":
                curly_depth += 1
            elif char == "}":
                curly_depth = max(0, curly_depth - 1)

            if char == "~" and round_depth == 0 and square_depth == 0 and curly_depth == 0:
                token = "".join(current).strip()
                if token:
                    actions.append(token)
                current = []
                continue

            current.append(char)

        tail = "".join(current).strip()
        if tail:
            actions.append(tail)

        return actions

    def _ensure_window(self) -> QWidget:
        if self.window is None:
            raise RuntimeError("Window not initialized. Use ^F before UI commands.")
        return self.window

    def _ensure_layout(self) -> QVBoxLayout:
        if self.layout is None:
            raise RuntimeError("Layout not initialized. Use ^F before UI commands.")
        return self.layout

    def _append_style(self, widget: QWidget, css: str) -> None:
        previous = widget.styleSheet().strip()
        merged = f"{previous}; {css}" if previous else css
        widget.setStyleSheet(merged)

    def _create_root(self) -> None:
        self.window = QWidget()
        self.window.setWindowTitle("AIL Desktop App")
        self.window.resize(900, 600)
        self.window.setStyleSheet(
            """
            QWidget {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: "Menlo", "Consolas", "Monaco";
                font-size: 14px;
            }
            QLabel {
                background: transparent;
                padding: 2px 0;
            }
            QLineEdit {
                background-color: #252526;
                color: #f3f3f3;
                border: none;
                border-bottom: 1px solid #3c3c3c;
                padding: 10px 8px;
                selection-background-color: #0e639c;
            }
            QLineEdit:focus {
                border-bottom: 1px solid #00ffcc;
            }
            QPushButton {
                background-color: #0e639c;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 10px 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0a4f7d;
            }
            """
        )

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(24, 24, 24, 24)
        self.layout.setSpacing(12)
        self.window.setLayout(self.layout)

    def _render_text(self, action: str) -> None:
        match = re.fullmatch(r"#T\[(h1|h2),([^\]]+)\]\*0\{(.*)\}", action)
        if not match:
            raise ValueError(f"Invalid #T syntax: {action}")

        tag, widget_id, text = match.groups()

        label = QLabel(text)
        if tag == "h1":
            label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        else:
            label.setFont(QFont("Arial", 16, QFont.Weight.Medium))

        self._ensure_layout().addWidget(label)
        self.widgets[widget_id] = label

    def _apply_style(self, action: str) -> None:
        match = re.fullmatch(r"#S\[([^\]]+)\]\{(.*)\}", action)
        if not match:
            raise ValueError(f"Invalid #S syntax: {action}")

        widget_id, css = match.groups()
        widget = self.widgets.get(widget_id)
        if widget is None:
            raise KeyError(f"Widget not found for style: {widget_id}")

        color_match = re.search(r"color\s*:\s*(#[0-9a-fA-F]{3,8})", css)
        if color_match:
            color = color_match.group(1)
            self._append_style(widget, f"color: {color};")

    def _render_input(self, action: str) -> None:
        match = re.fullmatch(r"#I\[([^,\]]+),([^\]]+)\]", action)
        if not match:
            raise ValueError(f"Invalid #I syntax: {action}")

        _input_type, widget_id = match.groups()

        entry = QLineEdit()
        entry.setPlaceholderText(widget_id)
        self._ensure_layout().addWidget(entry)
        self.widgets[widget_id] = entry

    def _render_button(self, action: str) -> None:
        match = re.fullmatch(r"#B\[([^\]]+)\]\*0\{(.*)\}", action)
        if not match:
            raise ValueError(f"Invalid #B syntax: {action}")

        widget_id, text = match.groups()

        button = QPushButton(text)
        self._ensure_layout().addWidget(button)
        self.widgets[widget_id] = button

    def _collect_input_payload(self) -> dict[str, str]:
        payload: dict[str, str] = {}
        for widget_id, widget in self.widgets.items():
            if isinstance(widget, QLineEdit):
                payload[widget_id] = widget.text()
        return payload

    def _on_request_finished(self, ok: bool, title: str, body: str) -> None:
        window = self._ensure_window()
        if ok:
            QMessageBox.information(window, title, body)
        else:
            QMessageBox.warning(window, title, body)

    def _cleanup_thread(self, thread: PostWorker) -> None:
        if thread in self._threads:
            self._threads.remove(thread)
        thread.deleteLater()

    def _trigger_post(self, route: str) -> None:
        payload = self._collect_input_payload()
        url = f"{self.API_BASE}{route}"

        worker = PostWorker(url, payload)
        worker.finished.connect(self._on_request_finished)
        worker.finished.connect(lambda *_: self._cleanup_thread(worker))
        self._threads.append(worker)
        worker.start()

    def _bind_event(self, action: str) -> None:
        match = re.fullmatch(r"\*E\[click,([^\]]+)\]\{>P\[([^\]]+)\]\}", action)
        if not match:
            raise ValueError(f"Invalid *E syntax: {action}")

        widget_id, route = match.groups()
        widget = self.widgets.get(widget_id)
        if widget is None:
            raise KeyError(f"Widget not found for event binding: {widget_id}")
        if not isinstance(widget, QPushButton):
            raise TypeError(
                f"*E click can only bind to QPushButton, got: {type(widget).__name__}"
            )

        widget.clicked.connect(partial(self._trigger_post, route))

    def execute(self) -> None:
        actions = self.split_actions(self.ail_code)
        if not actions:
            raise ValueError("No AIL actions found")

        for action in actions:
            if action == "^F":
                self._create_root()
            elif action.startswith("#T["):
                self._render_text(action)
            elif action.startswith("#S["):
                self._apply_style(action)
            elif action.startswith("#I["):
                self._render_input(action)
            elif action.startswith("#B["):
                self._render_button(action)
            elif action.startswith("*E["):
                self._bind_event(action)
            else:
                raise ValueError(f"Unsupported AIL action: {action}")

    def run(self) -> int:
        try:
            self.execute()
            window = self._ensure_window()
            window.show()
            return 0
        except Exception as exc:
            print(f"Engine Error: {exc}")
            return 1


if __name__ == "__main__":
    ail_code = "^F~#T[h1,main-title]*0{极客星际博客}~#S[main-title]{color:#00ffcc}~#T[h2,sub-title]*0{最新高维文章}~#S[sub-title]{color:#ffffff}~#I[text,read-input]~#B[read-btn]*0{提取记忆}~*E[click,read-btn]{>P[/api/read]}"

    app = QApplication(sys.argv)
    engine = DesktopEngine(ail_code)
    init_code = engine.run()
    if init_code != 0:
        sys.exit(init_code)
    sys.exit(app.exec())
