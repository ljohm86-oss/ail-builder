#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/carwynmac/ai-cl"
RESULTS_DIR="$ROOT/testing/results"
BASE_URL="embedded://local"
INCLUDE_PARTIAL="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base-url)
      BASE_URL="${2:-}"
      shift 2
      ;;
    --include-partial)
      INCLUDE_PARTIAL="true"
      shift 1
      ;;
    *)
      echo "error: unsupported argument: $1" >&2
      exit 2
      ;;
  esac
done

mkdir -p "$RESULTS_DIR"

SUMMARY_JSON="$RESULTS_DIR/website_demo_pack_run_20260319.json"
SUMMARY_MD="$RESULTS_DIR/website_demo_pack_run_20260319.md"

python3 - "$ROOT" "$BASE_URL" "$INCLUDE_PARTIAL" "$SUMMARY_JSON" "$SUMMARY_MD" <<'PY'
import json
import os
import subprocess
import sys
from pathlib import Path

root = Path(sys.argv[1])
base_url = sys.argv[2]
include_partial = sys.argv[3].lower() == "true"
summary_json = Path(sys.argv[4])
summary_md = Path(sys.argv[5])

env = os.environ.copy()
env["PYTHONPATH"] = str(root)

cases = [
    {
        "id": "company_product",
        "pack": "Company / Product Website Pack",
        "support_level": "Supported",
        "requirement": "做一个企业产品官网，包含首页、产品优势、团队介绍、客户评价、FAQ、数据展示、合作伙伴 Logo、联系我们。",
        "expected_profile": "landing",
    },
    {
        "id": "personal_independent",
        "pack": "Personal Independent Site Pack",
        "support_level": "Supported",
        "requirement": "做一个个人独立站，包含首页、个人介绍、服务介绍、作品展示、联系方式。",
        "expected_profile": "landing",
    },
    {
        "id": "ecom_storefront",
        "pack": "Ecommerce Independent Storefront Pack",
        "support_level": "Supported",
        "requirement": "做一个服装独立站，包含首页横幅、分类导航、商品列表、商品详情、购物车、结算。",
        "expected_profile": "ecom_min",
    },
    {
        "id": "after_sales",
        "pack": "After-Sales Service Website Pack",
        "support_level": "Supported",
        "requirement": "做一个品牌售后服务网站，包含退款申请、换货申请、投诉提交、进度查询说明、联系客服。",
        "expected_profile": "after_sales",
    },
]

if include_partial:
    cases.append(
        {
            "id": "blog_style_partial",
            "pack": "Personal Blog-Style Site Pack",
            "support_level": "Partial",
            "requirement": "做一个个人博客风格网站，包含首页、文章列表、关于我、联系方式。",
            "expected_profile": "landing",
        }
    )


def run_json(cmd, cwd):
    proc = subprocess.run(cmd, cwd=str(cwd), env=env, capture_output=True, text=True)
    raw = proc.stdout.strip() or proc.stderr.strip()
    try:
        payload = json.loads(raw)
    except Exception as exc:
        raise RuntimeError(
            f"Failed to parse JSON for command: {cmd}\nexit={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}"
        ) from exc
    return proc.returncode, payload


results = []
for case in cases:
    trial_code, trial = run_json(
        ["python3", "-m", "cli", "trial-run", "--requirement", case["requirement"], "--base-url", base_url, "--json"],
        root,
    )
    project_path = Path(trial["project_path"])
    go_code, go = run_json(
        ["python3", "-m", "cli", "project", "go", "--base-url", base_url, "--json"],
        project_path,
    )
    preview_code, preview = run_json(
        ["python3", "-m", "cli", "project", "preview", "--base-url", base_url, "--json"],
        project_path,
    )
    export_code, export = run_json(
        ["python3", "-m", "cli", "project", "export-handoff", "--base-url", base_url, "--json"],
        project_path,
    )

    profile = str(trial.get("detected_profile") or "")
    profile_ok = profile == case["expected_profile"]
    flow_ok = all(item.get("status") == "ok" for item in (trial, go, preview, export))
    demo_ready = bool(profile_ok and flow_ok)

    results.append(
        {
            "id": case["id"],
            "pack": case["pack"],
            "support_level": case["support_level"],
            "requirement": case["requirement"],
            "expected_profile": case["expected_profile"],
            "trial_run": {
                "exit_code": trial_code,
                "status": trial.get("status"),
                "detected_profile": profile,
                "repair_used": trial.get("repair_used"),
                "managed_files_written": trial.get("managed_files_written"),
            },
            "project_go": {
                "exit_code": go_code,
                "status": go.get("status"),
                "route_taken": go.get("route_taken"),
            },
            "project_preview": {
                "exit_code": preview_code,
                "status": preview.get("status"),
                "primary_target": ((preview.get("preview_handoff") or {}).get("primary_target") or {}).get("label"),
            },
            "project_export_handoff": {
                "exit_code": export_code,
                "status": export.get("status"),
                "primary_target_label": export.get("primary_target_label"),
            },
            "validation": {
                "profile_ok": profile_ok,
                "flow_ok": flow_ok,
                "demo_ready": demo_ready,
            },
        }
    )

summary = {
    "status": "ok" if all(item["validation"]["demo_ready"] for item in results) else "attention",
    "date": "2026-03-19",
    "base_url": base_url,
    "include_partial": include_partial,
    "case_count": len(results),
    "demo_ready_count": sum(1 for item in results if item["validation"]["demo_ready"]),
    "supported_demo_ready_count": sum(
        1 for item in results if item["support_level"] == "Supported" and item["validation"]["demo_ready"]
    ),
    "partial_demo_ready_count": sum(
        1 for item in results if item["support_level"] == "Partial" and item["validation"]["demo_ready"]
    ),
}

payload = {
    "summary": summary,
    "cases": results,
}
summary_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

lines = [
    "# Website Demo Pack Run 2026-03-19",
    "",
    "## Summary",
    "",
    f"- status: `{summary['status']}`",
    f"- base_url: `{summary['base_url']}`",
    f"- include_partial: `{summary['include_partial']}`",
    f"- case_count: `{summary['case_count']}`",
    f"- demo_ready_count: `{summary['demo_ready_count']}`",
    f"- supported_demo_ready_count: `{summary['supported_demo_ready_count']}`",
    f"- partial_demo_ready_count: `{summary['partial_demo_ready_count']}`",
    "",
    "## Cases",
    "",
]

for item in results:
    lines.extend(
        [
            f"### {item['pack']}",
            "",
            f"- support_level: `{item['support_level']}`",
            f"- requirement: `{item['requirement']}`",
            f"- expected_profile: `{item['expected_profile']}`",
            f"- detected_profile: `{item['trial_run']['detected_profile']}`",
            f"- trial_status: `{item['trial_run']['status']}`",
            f"- repair_used: `{item['trial_run']['repair_used']}`",
            f"- managed_files_written: `{item['trial_run']['managed_files_written']}`",
            f"- project_go_route: `{item['project_go']['route_taken']}`",
            f"- preview_primary_target: `{item['project_preview']['primary_target']}`",
            f"- export_primary_target_label: `{item['project_export_handoff']['primary_target_label']}`",
            f"- demo_ready: `{item['validation']['demo_ready']}`",
            "",
        ]
    )

lines.extend(
    [
        "## Notes",
        "",
        "- This script follows the current stable demo order: `trial-run -> project go -> project preview -> project export-handoff`.",
        "- The partial blog-style case is excluded by default and can be enabled with `--include-partial`.",
        "",
        "## Artifacts",
        "",
        f"- summary_json: `{summary_json}`",
        f"- summary_md: `{summary_md}`",
    ]
)

summary_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(summary_md)
print(summary_json)
PY

echo "Website demo pack summary: $SUMMARY_MD"
echo "Website demo pack summary JSON: $SUMMARY_JSON"
