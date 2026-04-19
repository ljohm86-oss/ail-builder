#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


ROOT_DIR = Path(os.environ.get("AIL_REPO_ROOT", Path(__file__).resolve().parents[1])).expanduser().resolve()
BENCH_DIR = ROOT_DIR / "benchmark"
TASKS_PATH = BENCH_DIR / "tasks_v0_1.json"
POLICY_PATH = BENCH_DIR / "benchmark_baseline.json"
RESULTS_DIR = BENCH_DIR / "results" / "latest"
ARTIFACTS_DIR = RESULTS_DIR / "artifacts"


def ensure_clean_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def run_script(path: Path) -> tuple[bool, str]:
    proc = subprocess.run(
        ["bash", str(path)],
        cwd=str(ROOT_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.returncode == 0, proc.stdout


def load_prompt_map(tasks: list[dict[str, Any]]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for task in tasks:
        prompt = str(task.get("prompt", "")).strip()
        profile = str(task.get("expected_profile", "")).strip()
        if prompt and profile:
            mapping[prompt] = profile
    return mapping


def load_fixtures() -> dict[str, str]:
    examples_dir = ROOT_DIR / "profile_examples"
    return {
        "landing": (examples_dir / "landing_min.ail").read_text(encoding="utf-8"),
        "ecom_min": (examples_dir / "ecom_min.ail").read_text(encoding="utf-8"),
        "after_sales": (examples_dir / "after_sales_min.ail").read_text(encoding="utf-8"),
        "app_min": (examples_dir / "app_min.ail").read_text(encoding="utf-8"),
    }


class MockResponse:
    def __init__(self, payload: dict[str, Any], status_code: int = 200):
        self._payload = payload
        self.status_code = status_code
        self.text = json.dumps(payload, ensure_ascii=False)

    def json(self) -> dict[str, Any]:
        return self._payload


def make_mock_async_client(prompt_map: dict[str, str], fixtures: dict[str, str]):
    profile_tokens = {
        "#PROFILE[landing]": "landing",
        "#PROFILE[ecom_min]": "ecom_min",
        "#PROFILE[after_sales]": "after_sales",
        "#PROFILE[app_min]": "app_min",
    }

    class MockAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(
            self,
            url: str,
            headers: Optional[dict[str, str]] = None,
            json: Optional[dict[str, Any]] = None,
        ):
            payload = json or {}
            user_prompt = ""
            for item in reversed(payload.get("messages", [])):
                if isinstance(item, dict) and item.get("role") == "user":
                    user_prompt = str(item.get("content", "")).strip()
                    break
            profile = None
            for token, name in profile_tokens.items():
                if token in user_prompt:
                    profile = name
                    break
            if not profile:
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
            return MockResponse(
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
                                "content": fixtures[profile],
                            },
                        }
                    ],
                }
            )

    return MockAsyncClient


def main() -> int:
    ensure_clean_dir(RESULTS_DIR)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    tasks_payload = json.loads(TASKS_PATH.read_text(encoding="utf-8"))
    tasks = tasks_payload.get("tasks", [])
    policy_payload = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    baseline_task_ids = set(policy_payload.get("release_baseline_task_ids", []))
    experimental_task_ids = set(policy_payload.get("experimental_task_ids", []))
    all_policy_ids = baseline_task_ids | experimental_task_ids

    try:
        os.environ["LLM_BASE_URL"] = "http://127.0.0.1/mock-benchmark/v1"
        os.environ["LLM_API_KEY"] = "mock-benchmark-key"
        os.environ["LLM_MODEL"] = "mock-benchmark"

        sys.path.insert(0, str(ROOT_DIR))
        import ail_server_v5  # type: ignore

        prompt_map = load_prompt_map(tasks)
        fixtures = load_fixtures()
        ail_server_v5.httpx.AsyncClient = make_mock_async_client(prompt_map, fixtures)  # type: ignore[attr-defined]
        app = ail_server_v5.app

        results: list[dict] = []
        started_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        with app.test_client() as client:
            for task in tasks:
                task_id = task["task_id"]
                prompt = task["prompt"]
                expected_profile = task["expected_profile"]
                expected_keywords = task.get("expected_keywords", [])
                expected_routes = task.get("expected_routes", [])
                forbidden_routes = task.get("forbidden_routes", [])

                task_result: dict[str, object] = {
                    "task_id": task_id,
                    "category": task["category"],
                    "status": "frozen" if task_id in baseline_task_ids else "experimental",
                    "release_gate": task_id in baseline_task_ids,
                    "title": task["title"],
                    "expected_profile": expected_profile,
                    "generate_ok": False,
                    "compile_ok": False,
                    "keywords_ok": False,
                    "routes_ok": False,
                    "overall_ok": False,
                    "failure_reason": "",
                }

                generate_resp = client.post("/generate_ail", json={"prompt": prompt})
                generate_text = generate_resp.get_data(as_text=True)
                generate_json = {}
                try:
                    generate_json = generate_resp.get_json() or {}
                except Exception:
                    generate_json = {}
                (ARTIFACTS_DIR / f"{task_id}_generate.json").write_text(generate_text, encoding="utf-8")

                ail_text = str(generate_json.get("ail", "")).strip()
                (ARTIFACTS_DIR / f"{task_id}.ail").write_text(ail_text + ("\n" if ail_text else ""), encoding="utf-8")

                generate_ok = generate_resp.status_code == 200 and generate_json.get("status") == "ok" and bool(ail_text)
                keywords_ok = generate_ok and all(keyword in ail_text for keyword in expected_keywords)

                task_result["generate_ok"] = generate_ok
                task_result["keywords_ok"] = keywords_ok
                task_result["generate_status_code"] = generate_resp.status_code

                if not generate_ok:
                    task_result["failure_reason"] = generate_json.get("error", "generate_failed")
                    results.append(task_result)
                    continue

                compile_resp = client.post("/compile", json={"ail_code": ail_text})
                compile_text = compile_resp.get_data(as_text=True)
                compile_json = {}
                try:
                    compile_json = compile_resp.get_json() or {}
                except Exception:
                    compile_json = {}
                (ARTIFACTS_DIR / f"{task_id}_compile.json").write_text(compile_text, encoding="utf-8")

                compile_ok = compile_resp.status_code == 200 and compile_json.get("status") == "ok"
                task_result["compile_ok"] = compile_ok
                task_result["compile_status_code"] = compile_resp.status_code

                if not compile_ok:
                    task_result["failure_reason"] = compile_json.get("error", "compile_failed")
                    results.append(task_result)
                    continue

                summary = compile_json.get("summary", {}) or {}
                profiles_used = summary.get("profiles_used", [])
                profile_ok = expected_profile in profiles_used

                project_root = Path(str(compile_json.get("project_root", ""))).resolve()
                routes_path = project_root / "frontend" / "src" / "router" / "routes.generated.ts"
                routes_text = routes_path.read_text(encoding="utf-8") if routes_path.exists() else ""
                routes_ok = all(route in routes_text for route in expected_routes) and all(
                    route not in routes_text for route in forbidden_routes
                )

                task_result["profile_ok"] = profile_ok
                task_result["routes_ok"] = routes_ok
                task_result["profiles_used"] = profiles_used
                task_result["profile_resolution"] = summary.get("profile_resolution")
                task_result["project_root"] = str(project_root)
                task_result["overall_ok"] = bool(generate_ok and keywords_ok and compile_ok and profile_ok and routes_ok)
                if not task_result["overall_ok"]:
                    reasons = []
                    if not keywords_ok:
                        reasons.append("keyword_mismatch")
                    if not profile_ok:
                        reasons.append("profile_mismatch")
                    if not routes_ok:
                        reasons.append("route_mismatch")
                    task_result["failure_reason"] = ",".join(reasons) or "unknown"
                results.append(task_result)

        gate_checks = {}
        for name, script in [
            ("verify_profiles", ROOT_DIR / "verify_profiles.sh"),
            ("verify_app_profile", ROOT_DIR / "verify_app_profile.sh"),
            ("verify_app_profile_smoke", ROOT_DIR / "verify_app_profile_smoke.sh"),
        ]:
            ok, output = run_script(script)
            gate_checks[name] = {"ok": ok, "output": output}
            (ARTIFACTS_DIR / f"{name}.log").write_text(output, encoding="utf-8")

        total = len(results)
        passed = sum(1 for item in results if item["overall_ok"])
        by_category = {}
        by_status = {}
        for item in results:
            cat = item["category"]
            info = by_category.setdefault(cat, {"total": 0, "passed": 0})
            info["total"] += 1
            if item["overall_ok"]:
                info["passed"] += 1
            status_key = item["status"]
            status_info = by_status.setdefault(status_key, {"total": 0, "passed": 0})
            status_info["total"] += 1
            if item["overall_ok"]:
                status_info["passed"] += 1

        release_baseline_tasks = [item["task_id"] for item in results if item["release_gate"]]
        release_baseline_total = len(release_baseline_tasks)
        release_baseline_passed = sum(1 for item in results if item["release_gate"] and item["overall_ok"])
        policy_unassigned_task_ids = [item["task_id"] for item in results if item["task_id"] not in all_policy_ids]
        policy_unknown_task_ids = sorted(all_policy_ids - {str(item["task_id"]) for item in results})
        release_ok = (
            release_baseline_passed == release_baseline_total
            and len(policy_unassigned_task_ids) == 0
            and len(policy_unknown_task_ids) == 0
            and all(item["ok"] for item in gate_checks.values())
        )

        report_payload = {
            "benchmark_version": tasks_payload.get("benchmark_version", "0.1"),
            "policy_version": policy_payload.get("version", "v0.1"),
            "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "started_at_utc": started_at,
            "release_decision": "pass" if release_ok else "fail",
            "task_count": total,
            "passed_count": passed,
            "failed_count": total - passed,
            "by_category": by_category,
            "by_status": by_status,
            "release_baseline": {
                "task_ids": release_baseline_tasks,
                "total": release_baseline_total,
                "passed": release_baseline_passed,
                "failed": release_baseline_total - release_baseline_passed,
                "ok": release_baseline_passed == release_baseline_total,
            },
            "policy_checks": {
                "all_tasks_accounted_for": len(policy_unassigned_task_ids) == 0,
                "no_unknown_task_ids": len(policy_unknown_task_ids) == 0,
                "unassigned_task_ids": policy_unassigned_task_ids,
                "unknown_task_ids": policy_unknown_task_ids,
            },
            "gate_checks": {k: {"ok": v["ok"]} for k, v in gate_checks.items()},
            "results": results,
        }
        (RESULTS_DIR / "benchmark_results.json").write_text(
            json.dumps(report_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        lines = [
            "# Benchmark Report",
            "",
            f"- benchmark_version: `{report_payload['benchmark_version']}`",
            f"- policy_version: `{report_payload['policy_version']}`",
            f"- generated_at_utc: `{report_payload['generated_at_utc']}`",
            f"- release_decision: `{report_payload['release_decision']}`",
            f"- task_count: `{total}`",
            f"- passed_count: `{passed}`",
            f"- failed_count: `{total - passed}`",
            "",
            "## By Status",
            "",
        ]
        for status_key in ["frozen", "experimental"]:
            stats = by_status.get(status_key, {"total": 0, "passed": 0})
            lines.append(f"- `{status_key}`: {stats['passed']}/{stats['total']} passed")
        lines.extend([
            "",
            "## Release Baseline",
            "",
            f"- baseline_total: `{release_baseline_total}`",
            f"- baseline_passed: `{release_baseline_passed}`",
            f"- baseline_failed: `{release_baseline_total - release_baseline_passed}`",
            f"- baseline_ok: `{report_payload['release_baseline']['ok']}`",
            f"- baseline_task_ids: `{', '.join(release_baseline_tasks)}`",
            "",
            "## Policy Checks",
            "",
            f"- all_tasks_accounted_for: `{report_payload['policy_checks']['all_tasks_accounted_for']}`",
            f"- no_unknown_task_ids: `{report_payload['policy_checks']['no_unknown_task_ids']}`",
            f"- unassigned_task_ids: `{', '.join(policy_unassigned_task_ids) if policy_unassigned_task_ids else 'none'}`",
            f"- unknown_task_ids: `{', '.join(policy_unknown_task_ids) if policy_unknown_task_ids else 'none'}`",
            "",
            "## By Category",
            "",
        ])
        for cat in ["landing", "ecom_min", "after_sales", "app_min"]:
            stats = by_category.get(cat, {"total": 0, "passed": 0})
            lines.append(f"- `{cat}`: {stats['passed']}/{stats['total']} passed")
        lines.extend(["", "## Gate Checks", ""])
        for name, info in gate_checks.items():
            lines.append(f"- `{name}`: {'PASS' if info['ok'] else 'FAIL'}")
        lines.extend(["", "## Task Results", ""])
        for item in results:
            status = "PASS" if item["overall_ok"] else "FAIL"
            reason = item.get("failure_reason") or "none"
            lines.append(
                f"- `{item['task_id']}` `{item['category']}` `{item['status']}` gate={item['release_gate']} `{item['title']}`: {status} "
                f"(generate={item['generate_ok']}, compile={item['compile_ok']}, routes={item['routes_ok']}, reason={reason})"
            )
        (RESULTS_DIR / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

        print(f"BENCHMARK_DONE total={total} passed={passed} failed={total - passed}")
        return 0 if release_ok else 1
    finally:
        pass


if __name__ == "__main__":
    raise SystemExit(main())
