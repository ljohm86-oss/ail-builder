#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
ROOT="${AIL_REPO_ROOT:-$(cd -- "${SCRIPT_DIR}/.." && pwd)}"
export AIL_REPO_ROOT="$ROOT"
RESULTS_DIR="$ROOT/testing/results"
OUTPUT_JSON="$RESULTS_DIR/readiness_snapshot.json"
OUTPUT_MD="$RESULTS_DIR/readiness_snapshot.md"

mkdir -p "$RESULTS_DIR"

python3 - "$OUTPUT_JSON" "$OUTPUT_MD" <<'PY'
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

output_json = Path(sys.argv[1])
output_md = Path(sys.argv[2])
repo_root = Path(os.environ["AIL_REPO_ROOT"]).resolve()


def load_json(path_str: str):
    path = Path(path_str)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def latest_glob(pattern: str):
    matches = sorted(glob.glob(pattern))
    return matches[-1] if matches else None


def run_project_summary_probe():
    root = Path(tempfile.mkdtemp(prefix="ail_readiness_summary."))
    env = dict(os.environ)
    env["PYTHONPATH"] = str(repo_root)
    env["AIL_CLOUD_BASE_URL"] = "embedded://local"
    try:
        subprocess.run(
            ["python3", "-m", "cli", "init"],
            cwd=root,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            [
                "python3",
                "-m",
                "cli",
                "generate",
                "做一个 AI SaaS 官网，包含首页、功能介绍、FAQ、联系我们。",
            ],
            cwd=root,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["python3", "-m", "cli", "project", "continue", "--compile-sync", "--json"],
            cwd=root,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
        result = subprocess.run(
            ["python3", "-m", "cli", "project", "summary", "--json"],
            cwd=root,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        return {
            "ok": True,
            "recommended_primary_action": payload.get("recommended_primary_action"),
            "recommended_primary_command": payload.get("recommended_primary_command"),
            "recommended_primary_reason": payload.get("recommended_primary_reason"),
            "doctor_status": payload.get("doctor_status"),
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": str(exc),
        }
    finally:
        shutil.rmtree(root, ignore_errors=True)


rc = load_json(str(repo_root / "testing" / "results" / "rc_checks_results.json")) or {}
trial_batch_path = latest_glob(str(repo_root / "testing" / "results" / "first_user_trial_batch_recorded_summary_*.json"))
trial_batch = load_json(trial_batch_path) if trial_batch_path else {}
trial_smoke = load_json(str(repo_root / "testing" / "results" / "trial_run_smoke_results.json")) or {}
raw = load_json(str(repo_root / "testing" / "results" / "raw_model_outputs_results.json")) or {}
evolution = load_json(str(repo_root / "testing" / "results" / "patch_candidates_v3.json")) or {}
benchmark = load_json(str(repo_root / "benchmark" / "results" / "latest" / "benchmark_results.json")) or {}
repair = load_json(str(repo_root / "testing" / "results" / "repair_smoke_results.json")) or {}
project_summary_probe = run_project_summary_probe()
trial_primary_distribution = trial_batch.get("recommended_primary_action_distribution") or {}
trial_primary_actions = [key for key, value in trial_primary_distribution.items() if value]
trial_route_distribution = trial_batch.get("route_taken_distribution") or {}
trial_routes = [key for key, value in trial_route_distribution.items() if value]
project_workbench_primary_action_converged = (
    bool(trial_batch.get("status") == "ok")
    and len(trial_primary_actions) == 1
    and trial_primary_actions[0] == project_summary_probe.get("recommended_primary_action")
)
trial_entry_route_converged = (
    bool(trial_batch.get("status") == "ok")
    and len(trial_routes) == 1
    and trial_routes[0] == "trial_run_canonical_flow"
)

raw_summary = raw.get("summary") or {}
evolution_summary = evolution.get("summary") or {}
rc_metrics = rc.get("metrics") or {}
release_baseline = benchmark.get("release_baseline") or {}

benchmark_release_baseline_ok = release_baseline.get("ok")
if benchmark_release_baseline_ok is None:
    benchmark_release_baseline_ok = rc_metrics.get("benchmark_release_baseline_ok")

benchmark_release_baseline_passed = release_baseline.get("passed")
if benchmark_release_baseline_passed is None:
    benchmark_release_baseline_passed = rc_metrics.get("benchmark_release_baseline_passed")

benchmark_release_baseline_failed = release_baseline.get("failed")
if benchmark_release_baseline_failed is None:
    benchmark_release_baseline_failed = rc_metrics.get("benchmark_release_baseline_failed")

benchmark_release_decision = benchmark.get("release_decision")
if benchmark_release_decision is None:
    benchmark_release_decision = rc_metrics.get("benchmark_release_decision")

snapshot = {
    "status": "ok",
    "stage": "frozen_profile_product_closure",
    "rc_gate_ok": rc.get("status") == "ok",
    "project_workbench_ok": (
        bool((rc.get("checks") or {}).get("website_check_ok"))
        and bool((rc.get("checks") or {}).get("website_check_out_of_scope_ok"))
        and bool((rc.get("checks") or {}).get("project_check_ok"))
        and bool((rc.get("checks") or {}).get("project_check_conflict_ok"))
        and bool((rc.get("checks") or {}).get("project_doctor_ok"))
        and bool((rc.get("checks") or {}).get("project_doctor_validation_ok"))
        and bool((rc.get("checks") or {}).get("project_doctor_apply_safe_noop_ok"))
        and bool((rc.get("checks") or {}).get("project_doctor_apply_safe_repair_ok"))
        and bool((rc.get("checks") or {}).get("project_doctor_apply_safe_continue_noop_ok"))
        and bool((rc.get("checks") or {}).get("project_doctor_apply_safe_continue_repair_ok"))
        and bool((rc.get("checks") or {}).get("project_continue_auto_repair_ok"))
        and bool((rc.get("checks") or {}).get("project_continue_auto_no_repair_ok"))
        and bool((rc.get("checks") or {}).get("project_preview_ok"))
        and bool((rc.get("checks") or {}).get("project_preview_conflict_ok"))
        and bool((rc.get("checks") or {}).get("project_open_target_ok"))
        and bool((rc.get("checks") or {}).get("project_open_target_default_ok"))
        and bool((rc.get("checks") or {}).get("project_inspect_target_ok"))
        and bool((rc.get("checks") or {}).get("project_inspect_target_default_ok"))
        and bool((rc.get("checks") or {}).get("project_run_inspect_command_ok"))
        and bool((rc.get("checks") or {}).get("project_run_inspect_command_default_ok"))
        and bool((rc.get("checks") or {}).get("project_export_handoff_ok"))
        and bool((rc.get("checks") or {}).get("project_export_handoff_conflict_ok"))
        and bool((rc.get("checks") or {}).get("project_go_ok"))
        and bool((rc.get("checks") or {}).get("project_go_repair_ok"))
        and bool((rc.get("checks") or {}).get("project_go_conflict_ok"))
        and bool((rc.get("checks") or {}).get("workspace_preview_ok"))
        and bool((rc.get("checks") or {}).get("workspace_preview_project_ok"))
        and bool((rc.get("checks") or {}).get("workspace_open_target_ok"))
        and bool((rc.get("checks") or {}).get("workspace_open_target_project_ok"))
        and bool((rc.get("checks") or {}).get("workspace_inspect_target_ok"))
        and bool((rc.get("checks") or {}).get("workspace_inspect_target_project_ok"))
        and bool((rc.get("checks") or {}).get("workspace_run_inspect_command_ok"))
        and bool((rc.get("checks") or {}).get("workspace_run_inspect_command_project_ok"))
        and bool((rc.get("checks") or {}).get("workspace_export_handoff_ok"))
        and bool((rc.get("checks") or {}).get("workspace_export_handoff_project_ok"))
        and bool((rc.get("checks") or {}).get("workspace_doctor_ok"))
        and bool((rc.get("checks") or {}).get("workspace_doctor_project_ok"))
        and bool((rc.get("checks") or {}).get("workspace_continue_ok"))
        and bool((rc.get("checks") or {}).get("workspace_continue_project_ok"))
        and bool((rc.get("checks") or {}).get("workspace_go_ok"))
        and bool((rc.get("checks") or {}).get("workspace_go_project_ok"))
        and bool((rc.get("checks") or {}).get("rc_go_ok"))
        and bool((rc.get("checks") or {}).get("rc_go_refresh_ok"))
    ),
    "trial_batch_ok": trial_batch.get("status") == "ok",
    "trial_entry_ok": trial_smoke.get("status") == "ok",
    "frozen_profiles": ["landing", "ecom_min", "after_sales"],
    "experimental_profiles": ["app_min"],
    "signals": {
        "raw_total_samples": raw_summary.get("total_samples"),
        "raw_final_compile_candidates": raw_summary.get("final_compile_candidates"),
        "repair_success_rate": repair.get("success_rate"),
        "active_patch_pressure_count": evolution_summary.get("active_patch_pressure_count"),
        "active_suggested_tokens": evolution_summary.get("active_suggested_tokens"),
        "website_check_smoke_ok": (rc.get("metrics") or {}).get("website_check_smoke_ok"),
        "website_check_out_of_scope_smoke_ok": (rc.get("metrics") or {}).get("website_check_out_of_scope_smoke_ok"),
        "website_assets_smoke_ok": (rc.get("metrics") or {}).get("website_assets_smoke_ok"),
        "website_assets_pack_smoke_ok": (rc.get("metrics") or {}).get("website_assets_pack_smoke_ok"),
        "website_open_asset_smoke_ok": (rc.get("metrics") or {}).get("website_open_asset_smoke_ok"),
        "website_open_asset_pack_smoke_ok": (rc.get("metrics") or {}).get("website_open_asset_pack_smoke_ok"),
        "website_inspect_asset_smoke_ok": (rc.get("metrics") or {}).get("website_inspect_asset_smoke_ok"),
        "website_inspect_asset_pack_smoke_ok": (rc.get("metrics") or {}).get("website_inspect_asset_pack_smoke_ok"),
        "website_preview_smoke_ok": (rc.get("metrics") or {}).get("website_preview_smoke_ok"),
        "website_preview_pack_smoke_ok": (rc.get("metrics") or {}).get("website_preview_pack_smoke_ok"),
        "website_run_inspect_command_smoke_ok": (rc.get("metrics") or {}).get("website_run_inspect_command_smoke_ok"),
        "website_run_inspect_command_pack_smoke_ok": (rc.get("metrics") or {}).get("website_run_inspect_command_pack_smoke_ok"),
        "website_export_handoff_smoke_ok": (rc.get("metrics") or {}).get("website_export_handoff_smoke_ok"),
        "website_export_handoff_pack_smoke_ok": (rc.get("metrics") or {}).get("website_export_handoff_pack_smoke_ok"),
        "website_summary_smoke_ok": (rc.get("metrics") or {}).get("website_summary_smoke_ok"),
        "website_go_smoke_ok": (rc.get("metrics") or {}).get("website_go_smoke_ok"),
        "project_check_smoke_ok": (rc.get("metrics") or {}).get("project_check_smoke_ok"),
        "project_check_conflict_smoke_ok": (rc.get("metrics") or {}).get("project_check_conflict_smoke_ok"),
        "project_doctor_smoke_ok": (rc.get("metrics") or {}).get("project_doctor_smoke_ok"),
        "project_doctor_validation_smoke_ok": (rc.get("metrics") or {}).get("project_doctor_validation_smoke_ok"),
        "project_doctor_apply_safe_noop_smoke_ok": (rc.get("metrics") or {}).get("project_doctor_apply_safe_noop_smoke_ok"),
        "project_doctor_apply_safe_repair_smoke_ok": (rc.get("metrics") or {}).get("project_doctor_apply_safe_repair_smoke_ok"),
        "project_doctor_apply_safe_continue_noop_smoke_ok": (rc.get("metrics") or {}).get("project_doctor_apply_safe_continue_noop_smoke_ok"),
        "project_doctor_apply_safe_continue_repair_smoke_ok": (rc.get("metrics") or {}).get("project_doctor_apply_safe_continue_repair_smoke_ok"),
        "project_continue_auto_repair_smoke_ok": (rc.get("metrics") or {}).get("project_continue_auto_repair_smoke_ok"),
        "project_continue_auto_no_repair_smoke_ok": (rc.get("metrics") or {}).get("project_continue_auto_no_repair_smoke_ok"),
        "project_preview_smoke_ok": (rc.get("metrics") or {}).get("project_preview_smoke_ok"),
        "project_preview_conflict_smoke_ok": (rc.get("metrics") or {}).get("project_preview_conflict_smoke_ok"),
        "project_open_target_smoke_ok": (rc.get("metrics") or {}).get("project_open_target_smoke_ok"),
        "project_open_target_default_smoke_ok": (rc.get("metrics") or {}).get("project_open_target_default_smoke_ok"),
        "project_inspect_target_smoke_ok": (rc.get("metrics") or {}).get("project_inspect_target_smoke_ok"),
        "project_inspect_target_default_smoke_ok": (rc.get("metrics") or {}).get("project_inspect_target_default_smoke_ok"),
        "project_run_inspect_command_smoke_ok": (rc.get("metrics") or {}).get("project_run_inspect_command_smoke_ok"),
        "project_run_inspect_command_default_smoke_ok": (rc.get("metrics") or {}).get("project_run_inspect_command_default_smoke_ok"),
        "project_export_handoff_smoke_ok": (rc.get("metrics") or {}).get("project_export_handoff_smoke_ok"),
        "project_export_handoff_conflict_smoke_ok": (rc.get("metrics") or {}).get("project_export_handoff_conflict_smoke_ok"),
        "project_go_smoke_ok": (rc.get("metrics") or {}).get("project_go_smoke_ok"),
        "project_go_repair_smoke_ok": (rc.get("metrics") or {}).get("project_go_repair_smoke_ok"),
        "project_go_conflict_smoke_ok": (rc.get("metrics") or {}).get("project_go_conflict_smoke_ok"),
        "workspace_preview_smoke_ok": (rc.get("metrics") or {}).get("workspace_preview_smoke_ok"),
        "workspace_preview_project_smoke_ok": (rc.get("metrics") or {}).get("workspace_preview_project_smoke_ok"),
        "workspace_open_target_smoke_ok": (rc.get("metrics") or {}).get("workspace_open_target_smoke_ok"),
        "workspace_open_target_project_smoke_ok": (rc.get("metrics") or {}).get("workspace_open_target_project_smoke_ok"),
        "workspace_inspect_target_smoke_ok": (rc.get("metrics") or {}).get("workspace_inspect_target_smoke_ok"),
        "workspace_inspect_target_project_smoke_ok": (rc.get("metrics") or {}).get("workspace_inspect_target_project_smoke_ok"),
        "workspace_run_inspect_command_smoke_ok": (rc.get("metrics") or {}).get("workspace_run_inspect_command_smoke_ok"),
        "workspace_run_inspect_command_project_smoke_ok": (rc.get("metrics") or {}).get("workspace_run_inspect_command_project_smoke_ok"),
        "workspace_export_handoff_smoke_ok": (rc.get("metrics") or {}).get("workspace_export_handoff_smoke_ok"),
        "workspace_export_handoff_project_smoke_ok": (rc.get("metrics") or {}).get("workspace_export_handoff_project_smoke_ok"),
        "workspace_doctor_smoke_ok": (rc.get("metrics") or {}).get("workspace_doctor_smoke_ok"),
        "workspace_doctor_project_smoke_ok": (rc.get("metrics") or {}).get("workspace_doctor_project_smoke_ok"),
        "workspace_continue_smoke_ok": (rc.get("metrics") or {}).get("workspace_continue_smoke_ok"),
        "workspace_continue_project_smoke_ok": (rc.get("metrics") or {}).get("workspace_continue_project_smoke_ok"),
        "workspace_go_smoke_ok": (rc.get("metrics") or {}).get("workspace_go_smoke_ok"),
        "workspace_go_project_smoke_ok": (rc.get("metrics") or {}).get("workspace_go_project_smoke_ok"),
        "rc_go_smoke_ok": (rc.get("metrics") or {}).get("rc_go_smoke_ok"),
        "rc_go_refresh_smoke_ok": (rc.get("metrics") or {}).get("rc_go_refresh_smoke_ok"),
        "benchmark_release_baseline_ok": benchmark_release_baseline_ok,
        "benchmark_release_baseline_passed": benchmark_release_baseline_passed,
        "benchmark_release_baseline_failed": benchmark_release_baseline_failed,
        "benchmark_release_decision": benchmark_release_decision,
        "trial_batch_record_count": trial_batch.get("record_count"),
        "trial_batch_success_count": trial_batch.get("success_count"),
        "trial_batch_repair_required_count": trial_batch.get("repair_required_count"),
        "project_summary_probe_ok": project_summary_probe.get("ok"),
        "project_workbench_primary_action_converged": project_workbench_primary_action_converged,
        "trial_entry_route_converged": trial_entry_route_converged,
    },
    "artifacts": {
        "rc_checks_json": str(repo_root / "testing" / "results" / "rc_checks_results.json"),
        "rc_checks_report": str(repo_root / "testing" / "results" / "rc_checks_report.md"),
        "trial_batch_summary_json": trial_batch_path,
        "trial_run_smoke_results": str(repo_root / "testing" / "results" / "trial_run_smoke_results.json"),
        "raw_model_outputs_results": str(repo_root / "testing" / "results" / "raw_model_outputs_results.json"),
        "patch_candidates_v3": str(repo_root / "testing" / "results" / "patch_candidates_v3.json"),
        "benchmark_results": str(repo_root / "benchmark" / "results" / "latest" / "benchmark_results.json"),
    },
    "project_workbench_primary_action": {
        "recommended_primary_action": project_summary_probe.get("recommended_primary_action"),
        "recommended_primary_command": project_summary_probe.get("recommended_primary_command"),
        "recommended_primary_reason": project_summary_probe.get("recommended_primary_reason"),
        "doctor_status": project_summary_probe.get("doctor_status"),
        "probe_error": project_summary_probe.get("error"),
        "trial_batch_distribution": trial_primary_distribution,
        "converged": project_workbench_primary_action_converged,
    },
    "trial_entry_route": {
        "expected_route": "trial_run_canonical_flow",
        "trial_batch_distribution": trial_route_distribution,
        "converged": trial_entry_route_converged,
    },
    "recommendation": "",
}

all_green = (
    snapshot["rc_gate_ok"]
    and snapshot["project_workbench_ok"]
    and snapshot["trial_batch_ok"]
    and snapshot["trial_entry_ok"]
    and snapshot["signals"]["project_summary_probe_ok"] is True
    and snapshot["signals"]["project_workbench_primary_action_converged"] is True
    and snapshot["signals"]["trial_entry_route_converged"] is True
    and snapshot["signals"]["active_patch_pressure_count"] == 0
    and snapshot["signals"]["benchmark_release_baseline_ok"] is True
)

if all_green:
    snapshot["recommendation"] = "Current frozen-profile surface is ready for continued controlled trials and RC-style review."
else:
    snapshot["status"] = "attention"
    snapshot["recommendation"] = "Do not expand trial scope until the non-green signals in this snapshot are resolved."

output_json.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

lines = [
    "# Readiness Snapshot",
    "",
    "## Status",
    "",
    f"- overall_status: `{snapshot['status']}`",
    f"- stage: `{snapshot['stage']}`",
    f"- rc_gate_ok: `{str(snapshot['rc_gate_ok']).lower()}`",
    f"- project_workbench_ok: `{str(snapshot['project_workbench_ok']).lower()}`",
    f"- trial_batch_ok: `{str(snapshot['trial_batch_ok']).lower()}`",
    f"- trial_entry_ok: `{str(snapshot['trial_entry_ok']).lower()}`",
    "",
    "## Product Surface",
    "",
    f"- frozen_profiles: `{', '.join(snapshot['frozen_profiles'])}`",
    f"- experimental_profiles: `{', '.join(snapshot['experimental_profiles'])}`",
    "",
    "## Signals",
    "",
]

for key, value in snapshot["signals"].items():
    lines.append(f"- {key}: `{value}`")

lines.extend(
    [
        "",
        "## Project Workbench Primary Action",
        "",
        f"- recommended_primary_action: `{snapshot['project_workbench_primary_action']['recommended_primary_action']}`",
        f"- recommended_primary_command: `{snapshot['project_workbench_primary_action']['recommended_primary_command']}`",
        f"- recommended_primary_reason: `{snapshot['project_workbench_primary_action']['recommended_primary_reason']}`",
        f"- doctor_status: `{snapshot['project_workbench_primary_action']['doctor_status']}`",
        f"- converged: `{snapshot['project_workbench_primary_action']['converged']}`",
        f"- trial_batch_distribution: `{snapshot['project_workbench_primary_action']['trial_batch_distribution']}`",
        f"- probe_error: `{snapshot['project_workbench_primary_action']['probe_error']}`",
        "",
        "## Trial Entry Route",
        "",
        f"- expected_route: `{snapshot['trial_entry_route']['expected_route']}`",
        f"- converged: `{snapshot['trial_entry_route']['converged']}`",
        f"- trial_batch_distribution: `{snapshot['trial_entry_route']['trial_batch_distribution']}`",
        "",
        "## Recommendation",
        "",
        f"- {snapshot['recommendation']}",
        "",
        "## Artifacts",
        "",
    ]
)

for key, value in snapshot["artifacts"].items():
    lines.append(f"- {key}: `{value}`")

lines.extend(
    [
        "",
        "## Command",
        "",
        "```bash",
        f"bash {repo_root / 'testing' / 'run_readiness_snapshot.sh'}",
        "```",
    ]
)

output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(output_json)
print(output_md)
PY
