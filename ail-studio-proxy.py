from __future__ import annotations

import os
import queue
import re
import signal
import subprocess
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Deque, Dict, Optional, Set, Tuple

from flask import Flask, Response, jsonify, request, stream_with_context

app = Flask(__name__)

REPO_ROOT = Path(os.environ.get("AIL_REPO_ROOT", Path(__file__).resolve().parent)).expanduser().resolve()
BASE_PROJECTS_ROOT = (REPO_ROOT / "output_projects").resolve()
MAX_TAIL_LINES = 200
MAX_LINE_CHARS = 2048
DETECT_TIMEOUT_SECONDS = 30

ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
FRONTEND_RE = re.compile(r"FRONTEND_URL=(https?://(?:127\.0\.0\.1|localhost):\d+)")
BACKEND_RE = re.compile(r"BACKEND_URL=(https?://(?:127\.0\.0\.1|localhost):\d+)")
URL_RE = re.compile(r"https?://(?:127\.0\.0\.1|localhost):\d+")


@dataclass
class RunnerState:
    project_root: str
    process: subprocess.Popen[str]
    started_at: float
    tail: Deque[str] = field(default_factory=lambda: deque(maxlen=MAX_TAIL_LINES))
    frontend_url: Optional[str] = None
    backend_url: Optional[str] = None
    lock: threading.Lock = field(default_factory=threading.Lock)
    subscribers: Set[queue.Queue[Optional[str]]] = field(default_factory=set)


RUNNERS: Dict[str, RunnerState] = {}
RUNNERS_LOCK = threading.Lock()


def _normalize_url(url: str) -> str:
    return url.replace("http://localhost", "http://127.0.0.1").replace("https://localhost", "https://127.0.0.1")


def _sanitize_line(line: str) -> str:
    cleaned = ANSI_RE.sub("", line.rstrip("\r\n"))
    if len(cleaned) > MAX_LINE_CHARS:
        return cleaned[:MAX_LINE_CHARS] + "..."
    return cleaned


def _sse_event(data: str, event: Optional[str] = None) -> str:
    parts = []
    if event:
        parts.append(f"event: {event}")
    for single in data.splitlines() or [""]:
        parts.append(f"data: {single}")
    return "\n".join(parts) + "\n\n"


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def _is_running(state: RunnerState) -> bool:
    return state.process.poll() is None and _pid_alive(state.process.pid)


def _detect_state_for(state: Optional[RunnerState], running: bool, frontend_url: Optional[str]) -> str:
    if frontend_url:
        return "found"
    if running:
        return "pending"
    if state is not None and time.time() - state.started_at < DETECT_TIMEOUT_SECONDS:
        return "pending"
    return "timeout"


def _validate_project_root(raw_root: str, require_existing: bool = True) -> Tuple[Optional[Path], Optional[str]]:
    if not raw_root:
        return None, "project_root is required"

    root_str = raw_root.strip()
    raw_path = Path(root_str)
    if not raw_path.is_absolute():
        return None, "project_root must be an absolute path"

    if ".." in raw_path.parts:
        return None, "project_root must not contain '..'"

    resolved = raw_path.expanduser().resolve()

    try:
        common = os.path.commonpath([str(BASE_PROJECTS_ROOT), str(resolved)])
    except ValueError:
        return None, "project_root must be inside output_projects"

    if common != str(BASE_PROJECTS_ROOT):
        return None, f"project_root must be inside {BASE_PROJECTS_ROOT}"

    if require_existing and not resolved.exists():
        return None, "project_root does not exist"

    if require_existing and not resolved.is_dir():
        return None, "project_root must be a directory"

    return resolved, None


def _validate_start_script(root_path: Path) -> Tuple[Optional[Path], Optional[str]]:
    start_script = root_path / "start.sh"
    if not start_script.is_file():
        return None, "project_root/start.sh not found"
    if not os.access(start_script, os.X_OK):
        return None, "project_root/start.sh must be executable"
    return start_script, None


def _stop_runner(state: RunnerState) -> None:
    pid = state.process.pid
    if not _pid_alive(pid):
        return

    try:
        pgid = os.getpgid(pid)
    except ProcessLookupError:
        return

    try:
        os.killpg(pgid, signal.SIGTERM)
    except PermissionError:
        try:
            state.process.terminate()
        except Exception:
            return
    except ProcessLookupError:
        return
    except Exception:
        return

    deadline = time.time() + 1.0
    while time.time() < deadline:
        if not _pid_alive(pid):
            return
        time.sleep(0.05)

    if _pid_alive(pid):
        try:
            os.killpg(pgid, signal.SIGKILL)
        except PermissionError:
            try:
                state.process.kill()
            except Exception:
                return
        except ProcessLookupError:
            return
        except Exception:
            return


def _cleanup_dead_runners() -> None:
    dead_states: list[RunnerState] = []
    with RUNNERS_LOCK:
        dead_roots = [root for root, state in RUNNERS.items() if not _is_running(state)]
        for root in dead_roots:
            state = RUNNERS.pop(root, None)
            if state:
                dead_states.append(state)
    for state in dead_states:
        _close_subscribers(state)


def _stop_all_runners() -> None:
    with RUNNERS_LOCK:
        states = list(RUNNERS.values())
        RUNNERS.clear()

    for state in states:
        _stop_runner(state)
        _close_subscribers(state)


def _broadcast_line(state: RunnerState, line: str) -> None:
    with state.lock:
        dead_subscribers: list[queue.Queue[Optional[str]]] = []
        for subscriber in list(state.subscribers):
            try:
                subscriber.put_nowait(line)
            except queue.Full:
                dead_subscribers.append(subscriber)
            except Exception:
                dead_subscribers.append(subscriber)
        for sub in dead_subscribers:
            state.subscribers.discard(sub)


def _close_subscribers(state: RunnerState) -> None:
    with state.lock:
        subscribers = list(state.subscribers)
        state.subscribers.clear()
    for subscriber in subscribers:
        try:
            subscriber.put_nowait(None)
        except Exception:
            pass


def _tail_reader(state: RunnerState) -> None:
    stream = state.process.stdout
    if stream is None:
        return

    for raw_line in iter(stream.readline, ""):
        line = _sanitize_line(raw_line)
        with state.lock:
            state.tail.append(line)

            m_front = FRONTEND_RE.search(line)
            if m_front:
                state.frontend_url = _normalize_url(m_front.group(1))

            m_back = BACKEND_RE.search(line)
            if m_back:
                state.backend_url = _normalize_url(m_back.group(1))

            if state.frontend_url is None or state.backend_url is None:
                m_url = URL_RE.search(line)
                if m_url:
                    url = _normalize_url(m_url.group(0))
                    lower = line.lower()
                    if state.frontend_url is None and (
                        "vite" in lower or "frontend" in lower or "local:" in lower or "network:" in lower
                    ):
                        state.frontend_url = url
                    if state.backend_url is None and ("uvicorn" in lower or "backend" in lower):
                        state.backend_url = url
        _broadcast_line(state, line)
    _close_subscribers(state)


def _get_runner(project_root: str) -> Optional[RunnerState]:
    _cleanup_dead_runners()
    with RUNNERS_LOCK:
        state = RUNNERS.get(project_root)
    if state and not _is_running(state):
        with RUNNERS_LOCK:
            RUNNERS.pop(project_root, None)
        return None
    return state


@app.route("/run", methods=["POST"])
def run_project():
    payload = request.get_json(silent=True) or {}
    resolved_root, err = _validate_project_root(str(payload.get("project_root", "")), require_existing=True)
    if err:
        return jsonify({"status": "error", "error": err}), 400

    assert resolved_root is not None
    _, start_err = _validate_start_script(resolved_root)
    if start_err:
        return jsonify({"status": "error", "error": start_err}), 400

    project_root = str(resolved_root)

    # Single-project policy: stop any running project before starting a new one.
    _stop_all_runners()

    proc = subprocess.Popen(
        ["bash", "-lc", "./start.sh"],
        cwd=project_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        preexec_fn=os.setsid,
    )
    state = RunnerState(project_root=project_root, process=proc, started_at=time.time())

    with RUNNERS_LOCK:
        RUNNERS[project_root] = state

    thread = threading.Thread(target=_tail_reader, args=(state,), daemon=True)
    thread.start()

    return jsonify({"status": "ok", "pid": proc.pid, "started": True})


@app.route("/stop", methods=["POST"])
def stop_project():
    payload = request.get_json(silent=True) or {}
    resolved_root, err = _validate_project_root(str(payload.get("project_root", "")), require_existing=True)
    if err:
        return jsonify({"status": "error", "error": err}), 400

    assert resolved_root is not None
    project_root = str(resolved_root)

    with RUNNERS_LOCK:
        state = RUNNERS.pop(project_root, None)

    if state:
        _stop_runner(state)

    return jsonify({"status": "ok"})

@app.route("/stop_all", methods=["POST"])
def stop_all_projects():
    with RUNNERS_LOCK:
        states = list(RUNNERS.values())
        RUNNERS.clear()

    stopped = 0
    for state in states:
        if _is_running(state):
            stopped += 1
        _stop_runner(state)
        _close_subscribers(state)

    return jsonify({"status": "ok", "stopped": stopped})


@app.route("/status", methods=["GET"])
def status_project():
    resolved_root, err = _validate_project_root(str(request.args.get("project_root", "")), require_existing=True)
    if err:
        return jsonify({"status": "error", "error": err}), 400

    assert resolved_root is not None
    project_root = str(resolved_root)
    state = _get_runner(project_root)

    if not state:
        return jsonify(
            {
                "running": False,
                "pid": None,
                "frontend_url": None,
                "backend_url": None,
                "tail": [],
                "detect_state": "timeout",
            }
        )

    running = _is_running(state)
    with state.lock:
        tail = list(state.tail)
        frontend_url = state.frontend_url
        backend_url = state.backend_url

    return jsonify(
        {
            "running": running,
            "pid": state.process.pid if running else None,
            "frontend_url": frontend_url,
            "backend_url": backend_url,
            "tail": tail,
            "detect_state": _detect_state_for(state, running, frontend_url),
        }
    )


@app.route("/stream", methods=["GET"])
def stream_project():
    resolved_root, err = _validate_project_root(str(request.args.get("project_root", "")), require_existing=True)
    if err:
        return jsonify({"status": "error", "error": err}), 400

    assert resolved_root is not None
    project_root = str(resolved_root)
    state = _get_runner(project_root)
    if not state:
        return jsonify({"status": "error", "error": "project is not running"}), 404

    subscriber: queue.Queue[Optional[str]] = queue.Queue(maxsize=256)
    with state.lock:
        snapshot = list(state.tail)
        state.subscribers.add(subscriber)

    @stream_with_context
    def generate():
        try:
            for line in snapshot:
                yield _sse_event(line)

            while True:
                try:
                    item = subscriber.get(timeout=1.0)
                except queue.Empty:
                    if not _is_running(state):
                        yield _sse_event("stream_closed", "end")
                        break
                    yield ": keepalive\n\n"
                    continue

                if item is None:
                    yield _sse_event("stream_closed", "end")
                    break
                yield _sse_event(item)
        finally:
            with state.lock:
                state.subscribers.discard(subscriber)

    return Response(
        generate(),
        status=200,
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


if __name__ == "__main__":
    print("AIL Studio proxy listening on http://127.0.0.1:5050")
    app.run(host="127.0.0.1", port=5050, debug=False)
