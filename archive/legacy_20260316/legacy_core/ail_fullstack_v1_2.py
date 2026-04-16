from __future__ import annotations

import html
import json
import re
import sqlite3
from dataclasses import dataclass

from flask import Flask, jsonify, request

DB_FILE = "ail_data.db"


@dataclass
class RouteSpec:
    method: str
    path: str
    db_insert_table: str | None = None
    db_select_table: str | None = None


class AILFullstackEngine:
    def __init__(self, ail_code: str) -> None:
        self.ail_code = ail_code
        self.frontend_nodes: list[str] = []
        self.style_rules: dict[str, list[str]] = {}
        self.click_events: list[tuple[str, str]] = []
        self.list_render_specs: list[tuple[str, str, str]] = []
        self.route_specs: list[RouteSpec] = []
        self.db_init_specs: list[tuple[str, list[str]]] = []
        self._current_route: RouteSpec | None = None

    def split_actions(self, code: str) -> list[str]:
        actions: list[str] = []
        current: list[str] = []
        quote_char: str | None = None
        escape = False
        round_depth = 0
        square_depth = 0
        curly_depth = 0

        for char in code:
            if quote_char is not None:
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

    def parse(self) -> None:
        for action in self.split_actions(self.ail_code):
            if action in {"^F", "^B", "^D"}:
                continue

            if action.startswith("#T["):
                self._parse_text(action)
            elif action.startswith("#S["):
                self._parse_style(action)
            elif action.startswith("#I["):
                self._parse_input(action)
            elif action.startswith("#B["):
                self._parse_button(action)
            elif action.startswith("#D["):
                self._parse_div(action)
            elif action.startswith("#L["):
                self._parse_list_render(action)
            elif action.startswith("*E["):
                self._parse_click_event(action)
            elif action.startswith("+R["):
                self._parse_route(action)
            elif action.startswith(">DB_INIT["):
                self._parse_db_init(action)
            elif action.startswith(">DB_INSERT["):
                self._parse_db_insert(action)
            elif action.startswith(">DB_SELECT["):
                self._parse_db_select(action)
            else:
                # Unsupported instructions are ignored to keep the engine forward-compatible.
                continue

    def _parse_text(self, action: str) -> None:
        match = re.fullmatch(r"#T\[([^,\]]+),([^\]]+)\]\*0\{(.*)\}", action, flags=re.S)
        if not match:
            raise ValueError(f"Invalid #T action: {action}")

        tag, widget_id, text = match.groups()
        safe_tag = tag if re.fullmatch(r"[a-zA-Z][a-zA-Z0-9]*", tag) else "div"
        safe_text = html.escape(text)
        self.frontend_nodes.append(f'<{safe_tag} id="{widget_id}">{safe_text}</{safe_tag}>')

    def _parse_style(self, action: str) -> None:
        match = re.fullmatch(r"#S\[([^\]]+)\]\{(.*)\}", action, flags=re.S)
        if not match:
            raise ValueError(f"Invalid #S action: {action}")

        widget_id, css = match.groups()
        self.style_rules.setdefault(widget_id, []).append(css.strip())

    def _parse_input(self, action: str) -> None:
        match = re.fullmatch(r"#I\[([^,\]]+),([^\]]+)\]", action)
        if not match:
            raise ValueError(f"Invalid #I action: {action}")

        input_type, widget_id = match.groups()
        safe_input_type = input_type if re.fullmatch(r"[a-zA-Z0-9_-]+", input_type) else "text"
        self.frontend_nodes.append(
            f'<input id="{widget_id}" type="{safe_input_type}" placeholder="{widget_id}" />'
        )

    def _parse_button(self, action: str) -> None:
        match = re.fullmatch(r"#B\[([^\]]+)\]\*0\{(.*)\}", action, flags=re.S)
        if not match:
            raise ValueError(f"Invalid #B action: {action}")

        button_id, text = match.groups()
        safe_text = html.escape(text)
        self.frontend_nodes.append(f'<button id="{button_id}">{safe_text}</button>')

    def _parse_div(self, action: str) -> None:
        match = re.fullmatch(r"#D\[([^\]]+)\]", action)
        if not match:
            raise ValueError(f"Invalid #D action: {action}")

        div_id = match.group(1)
        self.frontend_nodes.append(f'<div id="{div_id}"></div>')

    def _parse_list_render(self, action: str) -> None:
        match = re.fullmatch(r"#L\[([^,\]]+),([^\]]+)\]\{(.*)\}", action, flags=re.S)
        if not match:
            raise ValueError(f"Invalid #L action: {action}")

        container_id, route, template = match.groups()
        self.list_render_specs.append((container_id, route, template))

    def _parse_click_event(self, action: str) -> None:
        match = re.fullmatch(r"\*E\[click,([^\]]+)\]\{>P\[([^\]]+)\](?:\{.*\})?\}", action, flags=re.S)
        if not match:
            raise ValueError(f"Invalid *E click action: {action}")

        button_id, route = match.groups()
        self.click_events.append((button_id, route))

    def _parse_route(self, action: str) -> None:
        match = re.fullmatch(r"\+R\[([^,\]]+),([^\]]+)\]", action)
        if not match:
            raise ValueError(f"Invalid +R action: {action}")

        method, path = match.groups()
        route = RouteSpec(method=method.upper().strip(), path=path.strip())
        self.route_specs.append(route)
        self._current_route = route

    def _parse_db_init(self, action: str) -> None:
        match = re.fullmatch(r">DB_INIT\[([^\]]+)\]\{(.*)\}", action, flags=re.S)
        if not match:
            raise ValueError(f"Invalid >DB_INIT action: {action}")

        table_name, fields_blob = match.groups()
        fields = [field.strip() for field in fields_blob.split(",") if field.strip()]
        if not fields:
            raise ValueError(">DB_INIT requires at least one field")

        self.db_init_specs.append((table_name.strip(), fields))

    def _parse_db_insert(self, action: str) -> None:
        match = re.fullmatch(r">DB_INSERT\[([^\]]+)\]", action)
        if not match:
            raise ValueError(f"Invalid >DB_INSERT action: {action}")
        if self._current_route is None:
            raise ValueError(">DB_INSERT must appear after +R")

        self._current_route.db_insert_table = match.group(1).strip()

    def _parse_db_select(self, action: str) -> None:
        match = re.fullmatch(r">DB_SELECT\[([^\]]+)\]", action)
        if not match:
            raise ValueError(f"Invalid >DB_SELECT action: {action}")
        if self._current_route is None:
            raise ValueError(">DB_SELECT must appear after +R")

        self._current_route.db_select_table = match.group(1).strip()

    def _render_styles(self) -> str:
        base_styles = [
            "body { background: #121212; color: #e5e5e5; font-family: Arial, sans-serif; padding: 24px; }",
            "input { background: #1f1f1f; color: #f2f2f2; border: 1px solid #3b3b3b; padding: 8px; margin: 8px 0; display: block; width: 320px; }",
            "button { background: #0e639c; color: white; border: none; padding: 10px 14px; cursor: pointer; margin: 8px 0; }",
            "button:hover { background: #1177bb; }",
            "#app { max-width: 920px; }",
        ]

        for widget_id, css_list in self.style_rules.items():
            merged = "; ".join(css_list)
            base_styles.append(f"#{widget_id} {{{merged}}}")

        return "\n".join(base_styles)

    def render_html(self) -> str:
        html_body = "\n".join(self.frontend_nodes)

        click_bindings = "\n".join(
            f"bindClickPost({json.dumps(button_id)}, {json.dumps(route)});"
            for button_id, route in self.click_events
        )

        list_render_calls = "\n".join(
            f"renderList({json.dumps(container_id)}, {json.dumps(route)}, {json.dumps(template)});"
            for container_id, route, template in self.list_render_specs
        )

        script = f"""
        <script>
        function collectInputs() {{
            const payload = {{}};
            document.querySelectorAll('input[id]').forEach((input) => {{
                payload[input.id] = input.value;
            }});
            return payload;
        }}

        function fillTemplate(template, item) {{
            return template.replace(/\\{{([^}}]+)\\}}/g, (_, key) => {{
                const k = key.trim();
                return Object.prototype.hasOwnProperty.call(item, k) ? item[k] : '';
            }});
        }}

        async function renderList(containerId, route, template) {{
            const container = document.getElementById(containerId);
            if (!container) return;
            try {{
                const resp = await fetch(route, {{ method: 'GET' }});
                if (!resp.ok) {{
                    throw new Error(`HTTP ${{resp.status}}`);
                }}
                const data = await resp.json();
                if (!Array.isArray(data)) {{
                    container.innerHTML = '<p>Invalid list payload</p>';
                    return;
                }}
                container.innerHTML = data.map((item) => fillTemplate(template, item)).join('');
            }} catch (err) {{
                container.innerHTML = `<p>List load failed: ${{err}}</p>`;
            }}
        }}

        function bindClickPost(buttonId, route) {{
            const btn = document.getElementById(buttonId);
            if (!btn) return;

            btn.addEventListener('click', async () => {{
                try {{
                    const resp = await fetch(route, {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify(collectInputs())
                    }});
                    const text = await resp.text();
                    alert(text);
                }} catch (err) {{
                    alert(`Request failed: ${{err}}`);
                }}
            }});
        }}

        document.addEventListener('DOMContentLoaded', () => {{
            {click_bindings}
            {list_render_calls}
        }});
        </script>
        """

        return f"""
        <!doctype html>
        <html>
        <head>
            <meta charset=\"utf-8\" />
            <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />
            <title>AIL Fullstack v1.2</title>
            <style>
            {self._render_styles()}
            </style>
        </head>
        <body>
            <div id=\"app\">{html_body}</div>
            {script}
        </body>
        </html>
        """


class SQLiteRuntime:
    def __init__(self, db_file: str = DB_FILE) -> None:
        self.db_file = db_file

    @staticmethod
    def _validate_identifier(value: str, label: str) -> str:
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
            raise ValueError(f"invalid {label}: {value}")
        return value

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn

    def init_tables(self, init_specs: list[tuple[str, list[str]]]) -> None:
        with self.connect() as conn:
            cur = conn.cursor()
            for table_name, fields in init_specs:
                safe_table_name = self._validate_identifier(table_name, "table name")
                normalized_fields = [
                    f'"{self._validate_identifier(field, "column name")}" TEXT' for field in fields
                ]
                if not normalized_fields:
                    continue

                sql = (
                    f'CREATE TABLE IF NOT EXISTS "{safe_table_name}" '
                    f'(id INTEGER PRIMARY KEY AUTOINCREMENT, {", ".join(normalized_fields)})'
                )
                cur.execute(sql)
            conn.commit()

    def insert_row(self, table_name: str, payload: dict[str, object]) -> None:
        safe_table_name = self._validate_identifier(table_name, "table name")
        keys = [str(k) for k in payload.keys() if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", str(k))]
        if not keys:
            raise ValueError("request.json must contain at least one valid key")

        placeholders = ", ".join("?" for _ in keys)
        columns = ", ".join(f'"{key}"' for key in keys)
        values = [payload[key] for key in keys]

        with self.connect() as conn:
            conn.execute(
                f'INSERT INTO "{safe_table_name}" ({columns}) VALUES ({placeholders})',
                values,
            )
            conn.commit()

    def select_all(self, table_name: str) -> list[dict[str, object]]:
        safe_table_name = self._validate_identifier(table_name, "table name")
        with self.connect() as conn:
            rows = conn.execute(f'SELECT * FROM "{safe_table_name}"').fetchall()
        return [dict(row) for row in rows]


def create_app(ail_code: str) -> Flask:
    engine = AILFullstackEngine(ail_code)
    engine.parse()

    runtime = SQLiteRuntime(DB_FILE)
    runtime.init_tables(engine.db_init_specs)

    app = Flask(__name__)

    @app.get("/")
    def index() -> str:
        return engine.render_html()

    for idx, spec in enumerate(engine.route_specs):
        endpoint_name = f"ail_route_{idx}_{spec.method}_{spec.path.strip('/').replace('/', '_') or 'root'}"

        def handler(route_spec: RouteSpec = spec):
            try:
                if route_spec.db_insert_table is not None:
                    if route_spec.method != "POST":
                        return jsonify({"error": ">DB_INSERT requires POST route"}), 400

                    payload = request.get_json(silent=True) or {}
                    if not isinstance(payload, dict):
                        return jsonify({"error": "request.json must be an object"}), 400

                    runtime.insert_row(route_spec.db_insert_table, payload)
                    return jsonify({"status": "ok"})

                if route_spec.db_select_table is not None:
                    if route_spec.method != "GET":
                        return jsonify({"error": ">DB_SELECT requires GET route"}), 400

                    data = runtime.select_all(route_spec.db_select_table)
                    return jsonify(data)

                return jsonify({"status": "ok"})
            except sqlite3.Error as exc:
                return jsonify({"error": f"sqlite error: {exc}"}), 500
            except ValueError as exc:
                return jsonify({"error": str(exc)}), 400
            except Exception as exc:  # pragma: no cover
                return jsonify({"error": f"unexpected error: {exc}"}), 500

        app.add_url_rule(spec.path, endpoint_name, handler, methods=[spec.method])

    return app


if __name__ == "__main__":
    from werkzeug.serving import run_simple
    from werkzeug.wrappers import Request, Response
    import json

    class AILHotSwapServer:
        """极其硬核的 WSGI 热重载中间件"""
        def __init__(self):
            print("🚀 AIL V1.2 云端引擎已启动！等待大模型注入灵魂...")
            # 初始状态给一个空界面
            self.current_app = create_app("^F~#T[h1,wait]*0{等待大模型部署...}~#S[wait]{color:#00ffcc; text-align:center}")

        def __call__(self, environ, start_response):
            req = Request(environ)
            
            # 拦截 MCP 发来的编译请求
            if req.path == '/compile' and req.method == 'POST':
                data = json.loads(req.get_data(as_text=True))
                ail_code = data.get('ail_code', '')
                print(f"\n📡 [MCP] 接收到 V1.2 高维指令！正在进行 0 毫秒热重载...")
                
                try:
                    # 瞬间生成全新的 Flask 实例，覆盖旧实例
                    self.current_app = create_app(ail_code)
                    print("✅ [核心引擎] 路由与 SQLite 数据库动态挂载完毕！")
                    res = Response(json.dumps({
                        "status": "ok", 
                        "message": "AIL V1.2 全栈编译成功！",
                        "preview_url": "http://127.0.0.1:5000/"
                    }), mimetype='application/json')
                except Exception as e:
                    import traceback
                    print(f"❌ 编译失败:\n{traceback.format_exc()}")
                    res = Response(json.dumps({"error": str(e)}), status=500, mimetype='application/json')
                
                return res(environ, start_response)
            
            # 正常的业务请求，全部透传给当前最新的 Flask 子应用
            return self.current_app(environ, start_response)

    # 启动基于 WSGI 的多维拦截服务器
    run_simple('127.0.0.1', 5000, AILHotSwapServer(), use_debugger=True, use_reloader=False)
