#!/usr/bin/env python3
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def load_prompt_map(tasks_path: Path) -> dict[str, str]:
    payload = json.loads(tasks_path.read_text(encoding="utf-8"))
    prompt_map: dict[str, str] = {}
    for task in payload.get("tasks", []):
        prompt = str(task.get("prompt", "")).strip()
        profile = str(task.get("expected_profile", "")).strip()
        if prompt and profile:
            prompt_map[prompt] = profile
    return prompt_map


def load_fixtures(profile_examples_dir: Path) -> dict[str, str]:
    return {
        "landing": (profile_examples_dir / "landing_min.ail").read_text(encoding="utf-8"),
        "ecom_min": (profile_examples_dir / "ecom_min.ail").read_text(encoding="utf-8"),
        "after_sales": (profile_examples_dir / "after_sales_min.ail").read_text(encoding="utf-8"),
        "app_min": (profile_examples_dir / "app_min.ail").read_text(encoding="utf-8"),
    }


def make_handler(prompt_map: dict[str, str], fixtures: dict[str, str]):
    class Handler(BaseHTTPRequestHandler):
        def _json(self, status: int, payload: dict) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            if self.path == "/health":
                self._json(200, {"status": "ok"})
                return
            self._json(404, {"error": "not_found"})

        def do_POST(self) -> None:
            if self.path != "/v1/chat/completions":
                self._json(404, {"error": "not_found"})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length) if length > 0 else b"{}"
                payload = json.loads(raw.decode("utf-8"))
            except Exception:
                self._json(400, {"error": "bad_json"})
                return

            messages = payload.get("messages", [])
            user_prompt = ""
            if isinstance(messages, list):
                for item in reversed(messages):
                    if isinstance(item, dict) and item.get("role") == "user":
                        user_prompt = str(item.get("content", "")).strip()
                        break

            profile = prompt_map.get(user_prompt)
            if not profile:
                prompt_lower = user_prompt.lower()
                if any(token in user_prompt for token in ["售后", "退款", "换货", "客服"]):
                    profile = "after_sales"
                elif any(token in prompt_lower for token in ["app", "chat"]) or "聊天" in user_prompt or "通讯" in user_prompt:
                    profile = "app_min"
                elif any(token in user_prompt for token in ["电商", "商城", "购物", "商品详情", "购物车", "结算"]):
                    profile = "ecom_min"
                else:
                    profile = "landing"

            content = fixtures[profile]
            self._json(
                200,
                {
                    "id": "mock-chatcmpl-1",
                    "object": "chat.completion",
                    "model": payload.get("model", "mock-benchmark"),
                    "choices": [
                        {
                            "index": 0,
                            "finish_reason": "stop",
                            "message": {
                                "role": "assistant",
                                "content": content,
                            },
                        }
                    ],
                },
            )

        def log_message(self, fmt: str, *args) -> None:
            return

    return Handler


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks-file", required=True)
    parser.add_argument("--profile-examples-dir", required=True)
    parser.add_argument("--port", type=int, default=18082)
    args = parser.parse_args()

    tasks_path = Path(args.tasks_file)
    examples_dir = Path(args.profile_examples_dir)
    prompt_map = load_prompt_map(tasks_path)
    fixtures = load_fixtures(examples_dir)

    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(prompt_map, fixtures))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
