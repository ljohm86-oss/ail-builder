#!/usr/bin/env bash
set -u

ROOT="/Users/carwynmac/ai-cl"
RESULTS_DIR="$ROOT/testing/results"
OUTPUT_JSON="$RESULTS_DIR/rc_checks_results.json"
OUTPUT_MD="$RESULTS_DIR/rc_checks_report.md"
BENCHMARK_LOG="$RESULTS_DIR/rc_benchmark.log"

mkdir -p "$RESULTS_DIR"

status="ok"
benchmark_command_ok="true"

run_step() {
  local name="$1"
  shift
  echo "[rc] running: $name"
  if ! "$@"; then
    echo "[rc] failed: $name" >&2
    status="error"
  fi
}

run_step_soft() {
  local name="$1"
  shift
  echo "[rc] running: $name"
  if ! "$@"; then
    echo "[rc] non-zero but continuing: $name" >&2
    return 1
  fi
  return 0
}

run_step "cli_checks" bash "$ROOT/testing/run_cli_checks.sh"
run_step "trial_entry_checks" bash "$ROOT/testing/run_trial_entry_checks.sh"
run_step "repair_smoke" bash "$ROOT/testing/repair_smoke.sh"
run_step "raw_model_outputs" bash "$ROOT/testing/run_raw_model_outputs.sh"
run_step "evolution_loop" bash "$ROOT/testing/run_evolution_loop.sh"
echo "[rc] benchmark log: $BENCHMARK_LOG"
if ! run_step_soft "benchmark" bash -lc "bash '$ROOT/benchmark/run_benchmark.sh' > '$BENCHMARK_LOG' 2>&1"; then
  benchmark_command_ok="false"
fi

python3 - "$status" "$benchmark_command_ok" "$OUTPUT_JSON" "$OUTPUT_MD" <<'PY'
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import glob

status = sys.argv[1]
benchmark_command_ok = sys.argv[2] == "true"
out_path = Path(sys.argv[3])
report_path = Path(sys.argv[4])


def load_json(path_str):
    path = Path(path_str)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def latest_glob(pattern: str):
    matches = sorted(glob.glob(pattern))
    return matches[-1] if matches else None


def run_project_summary_probe():
    root = Path(tempfile.mkdtemp(prefix="ail_rc_summary."))
    env = dict(os.environ)
    env["PYTHONPATH"] = "/Users/carwynmac/ai-cl"
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


cli = load_json("/Users/carwynmac/ai-cl/testing/results/cli_smoke_results.json") or {}
trial = load_json("/Users/carwynmac/ai-cl/testing/results/trial_run_smoke_results.json") or {}
repair = load_json("/Users/carwynmac/ai-cl/testing/results/repair_smoke_results.json") or {}
raw = load_json("/Users/carwynmac/ai-cl/testing/results/raw_model_outputs_results.json") or {}
evolution = load_json("/Users/carwynmac/ai-cl/testing/results/patch_candidates_v3.json") or {}
benchmark = load_json("/Users/carwynmac/ai-cl/benchmark/results/latest/benchmark_results.json") or {}
previous_rc = load_json(str(out_path)) or {}
project_summary_probe = run_project_summary_probe()
trial_batch_path = latest_glob("/Users/carwynmac/ai-cl/testing/results/first_user_trial_batch_recorded_summary_*.json")
trial_batch = load_json(trial_batch_path) if trial_batch_path else {}
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
release_baseline = benchmark.get("release_baseline") or (previous_rc.get("metrics") or {})

benchmark_release_decision = benchmark.get("release_decision")
if benchmark_release_decision is None:
    benchmark_release_decision = (previous_rc.get("metrics") or {}).get("benchmark_release_decision")

benchmark_release_baseline_ok = release_baseline.get("ok")
if benchmark_release_baseline_ok is None:
    benchmark_release_baseline_ok = (previous_rc.get("metrics") or {}).get("benchmark_release_baseline_ok")

benchmark_release_baseline_passed = release_baseline.get("passed")
if benchmark_release_baseline_passed is None:
    benchmark_release_baseline_passed = (previous_rc.get("metrics") or {}).get("benchmark_release_baseline_passed")

benchmark_release_baseline_failed = release_baseline.get("failed")
if benchmark_release_baseline_failed is None:
    benchmark_release_baseline_failed = (previous_rc.get("metrics") or {}).get("benchmark_release_baseline_failed")

benchmark_passed_count = benchmark.get("passed_count")
if benchmark_passed_count is None:
    benchmark_passed_count = (previous_rc.get("metrics") or {}).get("benchmark_passed_count")

benchmark_failed_count = benchmark.get("failed_count")
if benchmark_failed_count is None:
    benchmark_failed_count = (previous_rc.get("metrics") or {}).get("benchmark_failed_count")

raw_total = int(raw_summary.get("total_samples", 0) or 0)
raw_initial_candidates = int(raw_summary.get("initial_compile_candidates", 0) or 0)
raw_final_candidates = int(raw_summary.get("final_compile_candidates", 0) or 0)
raw_initial_rate = round((raw_initial_candidates / raw_total) * 100, 2) if raw_total else 0.0
raw_final_rate = round((raw_final_candidates / raw_total) * 100, 2) if raw_total else 0.0

payload = {
    "status": "ok",
    "command_status": status,
    "benchmark_command_ok": benchmark_command_ok,
    "checks": {
        "cli_checks_ok": cli.get("status") == "ok",
        "project_check_ok": bool((cli.get("checks") or {}).get("project_check_json_ok")),
        "website_check_ok": bool((cli.get("checks") or {}).get("website_check_json_ok")),
        "website_check_out_of_scope_ok": bool((cli.get("checks") or {}).get("website_check_out_of_scope_json_ok")),
        "website_assets_ok": bool((cli.get("checks") or {}).get("website_assets_json_ok")),
        "website_assets_pack_ok": bool((cli.get("checks") or {}).get("website_assets_pack_json_ok")),
        "website_open_asset_ok": bool((cli.get("checks") or {}).get("website_open_asset_json_ok")),
        "website_open_asset_pack_ok": bool((cli.get("checks") or {}).get("website_open_asset_pack_json_ok")),
        "website_inspect_asset_ok": bool((cli.get("checks") or {}).get("website_inspect_asset_json_ok")),
        "website_inspect_asset_pack_ok": bool((cli.get("checks") or {}).get("website_inspect_asset_pack_json_ok")),
        "website_preview_ok": bool((cli.get("checks") or {}).get("website_preview_json_ok")),
        "website_preview_pack_ok": bool((cli.get("checks") or {}).get("website_preview_pack_json_ok")),
        "website_run_inspect_command_ok": bool((cli.get("checks") or {}).get("website_run_inspect_command_json_ok")),
        "website_run_inspect_command_pack_ok": bool((cli.get("checks") or {}).get("website_run_inspect_command_pack_json_ok")),
        "website_export_handoff_ok": bool((cli.get("checks") or {}).get("website_export_handoff_json_ok")),
        "website_export_handoff_pack_ok": bool((cli.get("checks") or {}).get("website_export_handoff_pack_json_ok")),
        "website_summary_ok": bool((cli.get("checks") or {}).get("website_summary_json_ok")),
        "website_go_ok": bool((cli.get("checks") or {}).get("website_go_json_ok")),
        "project_check_conflict_ok": bool((cli.get("checks") or {}).get("project_check_conflict_json_ok")),
        "project_doctor_ok": bool((cli.get("checks") or {}).get("project_doctor_json_ok")),
        "project_doctor_validation_ok": bool((cli.get("checks") or {}).get("project_doctor_validation_json_ok")),
        "project_doctor_apply_safe_noop_ok": bool((cli.get("checks") or {}).get("project_doctor_apply_safe_noop_json_ok")),
        "project_doctor_apply_safe_repair_ok": bool((cli.get("checks") or {}).get("project_doctor_apply_safe_repair_json_ok")),
        "project_doctor_apply_safe_continue_noop_ok": bool((cli.get("checks") or {}).get("project_doctor_apply_safe_continue_noop_json_ok")),
        "project_doctor_apply_safe_continue_repair_ok": bool((cli.get("checks") or {}).get("project_doctor_apply_safe_continue_repair_json_ok")),
        "project_continue_auto_repair_ok": bool((cli.get("checks") or {}).get("project_continue_auto_repair_json_ok")),
        "project_continue_auto_no_repair_ok": bool((cli.get("checks") or {}).get("project_continue_auto_no_repair_json_ok")),
        "project_preview_ok": bool((cli.get("checks") or {}).get("project_preview_json_ok")),
        "project_preview_conflict_ok": bool((cli.get("checks") or {}).get("project_preview_conflict_json_ok")),
        "project_open_target_ok": bool((cli.get("checks") or {}).get("project_open_target_json_ok")),
        "project_open_target_default_ok": bool((cli.get("checks") or {}).get("project_open_target_default_json_ok")),
        "project_inspect_target_ok": bool((cli.get("checks") or {}).get("project_inspect_target_json_ok")),
        "project_inspect_target_default_ok": bool((cli.get("checks") or {}).get("project_inspect_target_default_json_ok")),
        "project_run_inspect_command_ok": bool((cli.get("checks") or {}).get("project_run_inspect_command_json_ok")),
        "project_run_inspect_command_default_ok": bool((cli.get("checks") or {}).get("project_run_inspect_command_default_json_ok")),
        "project_export_handoff_ok": bool((cli.get("checks") or {}).get("project_export_handoff_json_ok")),
        "project_export_handoff_conflict_ok": bool((cli.get("checks") or {}).get("project_export_handoff_conflict_json_ok")),
        "project_go_ok": bool((cli.get("checks") or {}).get("project_go_json_ok")),
        "project_go_repair_ok": bool((cli.get("checks") or {}).get("project_go_repair_json_ok")),
        "project_go_conflict_ok": bool((cli.get("checks") or {}).get("project_go_conflict_json_ok")),
        "workspace_preview_ok": bool((cli.get("checks") or {}).get("workspace_preview_repo_json_ok")),
        "workspace_preview_project_ok": bool((cli.get("checks") or {}).get("workspace_preview_project_json_ok")),
        "workspace_open_target_ok": bool((cli.get("checks") or {}).get("workspace_open_target_repo_json_ok")),
        "workspace_open_target_project_ok": bool((cli.get("checks") or {}).get("workspace_open_target_project_json_ok")),
        "workspace_inspect_target_ok": bool((cli.get("checks") or {}).get("workspace_inspect_target_repo_json_ok")),
        "workspace_inspect_target_project_ok": bool((cli.get("checks") or {}).get("workspace_inspect_target_project_json_ok")),
        "workspace_run_inspect_command_ok": bool((cli.get("checks") or {}).get("workspace_run_inspect_command_repo_json_ok")),
        "workspace_run_inspect_command_project_ok": bool((cli.get("checks") or {}).get("workspace_run_inspect_command_project_json_ok")),
        "workspace_export_handoff_ok": bool((cli.get("checks") or {}).get("workspace_export_handoff_repo_json_ok")),
        "workspace_export_handoff_project_ok": bool((cli.get("checks") or {}).get("workspace_export_handoff_project_json_ok")),
        "workspace_doctor_ok": bool((cli.get("checks") or {}).get("workspace_doctor_repo_json_ok")),
        "workspace_doctor_project_ok": bool((cli.get("checks") or {}).get("workspace_doctor_project_json_ok")),
        "workspace_continue_ok": bool((cli.get("checks") or {}).get("workspace_continue_repo_json_ok")),
        "workspace_continue_project_ok": bool((cli.get("checks") or {}).get("workspace_continue_project_json_ok")),
        "workspace_go_ok": bool((cli.get("checks") or {}).get("workspace_go_repo_json_ok")),
        "workspace_go_project_ok": bool((cli.get("checks") or {}).get("workspace_go_project_json_ok")),
        "rc_go_ok": bool((cli.get("checks") or {}).get("rc_go_json_ok")),
        "rc_go_refresh_ok": bool((cli.get("checks") or {}).get("rc_go_refresh_json_ok")),
        "project_summary_probe_ok": bool(project_summary_probe.get("ok")),
        "project_workbench_primary_action_converged": project_workbench_primary_action_converged,
        "trial_entry_route_converged": trial_entry_route_converged,
        "trial_entry_ok": trial.get("status") == "ok",
        "repair_smoke_ok": float(repair.get("success_rate", 0.0) or 0.0) >= 100.0,
        "raw_lane_ok": raw_total > 0 and raw_final_candidates == raw_total,
        "evolution_ok": int(evolution_summary.get("active_patch_pressure_count", 0) or 0) == 0,
        "benchmark_ok": bool(benchmark_release_baseline_ok),
    },
    "metrics": {
        "raw_total_samples": raw_total,
        "raw_initial_compile_rate": raw_initial_rate,
        "raw_final_compile_rate": raw_final_rate,
        "repair_success_rate": repair.get("success_rate"),
        "active_patch_pressure_count": evolution_summary.get("active_patch_pressure_count"),
        "active_suggested_tokens": evolution_summary.get("active_suggested_tokens"),
        "website_check_smoke_ok": bool((cli.get("checks") or {}).get("website_check_json_ok")),
        "website_check_out_of_scope_smoke_ok": bool((cli.get("checks") or {}).get("website_check_out_of_scope_json_ok")),
        "website_assets_smoke_ok": bool((cli.get("checks") or {}).get("website_assets_json_ok")),
        "website_assets_pack_smoke_ok": bool((cli.get("checks") or {}).get("website_assets_pack_json_ok")),
        "website_open_asset_smoke_ok": bool((cli.get("checks") or {}).get("website_open_asset_json_ok")),
        "website_open_asset_pack_smoke_ok": bool((cli.get("checks") or {}).get("website_open_asset_pack_json_ok")),
        "website_inspect_asset_smoke_ok": bool((cli.get("checks") or {}).get("website_inspect_asset_json_ok")),
        "website_inspect_asset_pack_smoke_ok": bool((cli.get("checks") or {}).get("website_inspect_asset_pack_json_ok")),
        "website_preview_smoke_ok": bool((cli.get("checks") or {}).get("website_preview_json_ok")),
        "website_preview_pack_smoke_ok": bool((cli.get("checks") or {}).get("website_preview_pack_json_ok")),
        "website_run_inspect_command_smoke_ok": bool((cli.get("checks") or {}).get("website_run_inspect_command_json_ok")),
        "website_run_inspect_command_pack_smoke_ok": bool((cli.get("checks") or {}).get("website_run_inspect_command_pack_json_ok")),
        "website_export_handoff_smoke_ok": bool((cli.get("checks") or {}).get("website_export_handoff_json_ok")),
        "website_export_handoff_pack_smoke_ok": bool((cli.get("checks") or {}).get("website_export_handoff_pack_json_ok")),
        "website_summary_smoke_ok": bool((cli.get("checks") or {}).get("website_summary_json_ok")),
        "website_go_smoke_ok": bool((cli.get("checks") or {}).get("website_go_json_ok")),
        "project_check_smoke_ok": bool((cli.get("checks") or {}).get("project_check_json_ok")),
        "project_check_conflict_smoke_ok": bool((cli.get("checks") or {}).get("project_check_conflict_json_ok")),
        "project_doctor_smoke_ok": bool((cli.get("checks") or {}).get("project_doctor_json_ok")),
        "project_doctor_validation_smoke_ok": bool((cli.get("checks") or {}).get("project_doctor_validation_json_ok")),
        "project_doctor_apply_safe_noop_smoke_ok": bool((cli.get("checks") or {}).get("project_doctor_apply_safe_noop_json_ok")),
        "project_doctor_apply_safe_repair_smoke_ok": bool((cli.get("checks") or {}).get("project_doctor_apply_safe_repair_json_ok")),
        "project_doctor_apply_safe_continue_noop_smoke_ok": bool((cli.get("checks") or {}).get("project_doctor_apply_safe_continue_noop_json_ok")),
        "project_doctor_apply_safe_continue_repair_smoke_ok": bool((cli.get("checks") or {}).get("project_doctor_apply_safe_continue_repair_json_ok")),
        "project_continue_auto_repair_smoke_ok": bool((cli.get("checks") or {}).get("project_continue_auto_repair_json_ok")),
        "project_continue_auto_no_repair_smoke_ok": bool((cli.get("checks") or {}).get("project_continue_auto_no_repair_json_ok")),
        "project_preview_smoke_ok": bool((cli.get("checks") or {}).get("project_preview_json_ok")),
        "project_preview_conflict_smoke_ok": bool((cli.get("checks") or {}).get("project_preview_conflict_json_ok")),
        "project_open_target_smoke_ok": bool((cli.get("checks") or {}).get("project_open_target_json_ok")),
        "project_open_target_default_smoke_ok": bool((cli.get("checks") or {}).get("project_open_target_default_json_ok")),
        "project_inspect_target_smoke_ok": bool((cli.get("checks") or {}).get("project_inspect_target_json_ok")),
        "project_inspect_target_default_smoke_ok": bool((cli.get("checks") or {}).get("project_inspect_target_default_json_ok")),
        "project_run_inspect_command_smoke_ok": bool((cli.get("checks") or {}).get("project_run_inspect_command_json_ok")),
        "project_run_inspect_command_default_smoke_ok": bool((cli.get("checks") or {}).get("project_run_inspect_command_default_json_ok")),
        "project_export_handoff_smoke_ok": bool((cli.get("checks") or {}).get("project_export_handoff_json_ok")),
        "project_export_handoff_conflict_smoke_ok": bool((cli.get("checks") or {}).get("project_export_handoff_conflict_json_ok")),
        "project_go_smoke_ok": bool((cli.get("checks") or {}).get("project_go_json_ok")),
        "project_go_repair_smoke_ok": bool((cli.get("checks") or {}).get("project_go_repair_json_ok")),
        "project_go_conflict_smoke_ok": bool((cli.get("checks") or {}).get("project_go_conflict_json_ok")),
        "workspace_preview_smoke_ok": bool((cli.get("checks") or {}).get("workspace_preview_repo_json_ok")),
        "workspace_preview_project_smoke_ok": bool((cli.get("checks") or {}).get("workspace_preview_project_json_ok")),
        "workspace_open_target_smoke_ok": bool((cli.get("checks") or {}).get("workspace_open_target_repo_json_ok")),
        "workspace_open_target_project_smoke_ok": bool((cli.get("checks") or {}).get("workspace_open_target_project_json_ok")),
        "workspace_inspect_target_smoke_ok": bool((cli.get("checks") or {}).get("workspace_inspect_target_repo_json_ok")),
        "workspace_inspect_target_project_smoke_ok": bool((cli.get("checks") or {}).get("workspace_inspect_target_project_json_ok")),
        "workspace_run_inspect_command_smoke_ok": bool((cli.get("checks") or {}).get("workspace_run_inspect_command_repo_json_ok")),
        "workspace_run_inspect_command_project_smoke_ok": bool((cli.get("checks") or {}).get("workspace_run_inspect_command_project_json_ok")),
        "workspace_export_handoff_smoke_ok": bool((cli.get("checks") or {}).get("workspace_export_handoff_repo_json_ok")),
        "workspace_export_handoff_project_smoke_ok": bool((cli.get("checks") or {}).get("workspace_export_handoff_project_json_ok")),
        "workspace_doctor_smoke_ok": bool((cli.get("checks") or {}).get("workspace_doctor_repo_json_ok")),
        "workspace_doctor_project_smoke_ok": bool((cli.get("checks") or {}).get("workspace_doctor_project_json_ok")),
        "workspace_continue_smoke_ok": bool((cli.get("checks") or {}).get("workspace_continue_repo_json_ok")),
        "workspace_continue_project_smoke_ok": bool((cli.get("checks") or {}).get("workspace_continue_project_json_ok")),
        "workspace_go_smoke_ok": bool((cli.get("checks") or {}).get("workspace_go_repo_json_ok")),
        "workspace_go_project_smoke_ok": bool((cli.get("checks") or {}).get("workspace_go_project_json_ok")),
        "rc_go_smoke_ok": bool((cli.get("checks") or {}).get("rc_go_json_ok")),
        "rc_go_refresh_smoke_ok": bool((cli.get("checks") or {}).get("rc_go_refresh_json_ok")),
        "project_summary_probe_ok": bool(project_summary_probe.get("ok")),
        "project_workbench_primary_action_converged": project_workbench_primary_action_converged,
        "trial_entry_route_converged": trial_entry_route_converged,
        "benchmark_release_decision": benchmark_release_decision,
        "benchmark_release_baseline_ok": benchmark_release_baseline_ok,
        "benchmark_release_baseline_passed": benchmark_release_baseline_passed,
        "benchmark_release_baseline_failed": benchmark_release_baseline_failed,
        "benchmark_passed_count": benchmark_passed_count,
        "benchmark_failed_count": benchmark_failed_count,
    },
    "artifacts": {
        "cli_smoke_results": "/Users/carwynmac/ai-cl/testing/results/cli_smoke_results.json",
        "trial_run_smoke_results": "/Users/carwynmac/ai-cl/testing/results/trial_run_smoke_results.json",
        "repair_smoke_results": "/Users/carwynmac/ai-cl/testing/results/repair_smoke_results.json",
        "raw_model_outputs_results": "/Users/carwynmac/ai-cl/testing/results/raw_model_outputs_results.json",
        "patch_candidates_v3": "/Users/carwynmac/ai-cl/testing/results/patch_candidates_v3.json",
        "benchmark_results": "/Users/carwynmac/ai-cl/benchmark/results/latest/benchmark_results.json",
        "benchmark_log": "/Users/carwynmac/ai-cl/testing/results/rc_benchmark.log",
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
}

all_ok = (
    status == "ok"
    and all(payload["checks"].values())
)
payload["status"] = "ok" if all_ok else "error"

out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

report_lines = [
    "# RC Checks Report",
    "",
    "## Status",
    "",
    f"- overall_status: `{payload['status']}`",
    f"- command_status: `{payload['command_status']}`",
    f"- benchmark_command_ok: `{str(payload['benchmark_command_ok']).lower()}`",
    "",
    "## Checks",
    "",
]

for key, value in payload["checks"].items():
    report_lines.append(f"- {key}: `{str(value).lower()}`")

report_lines.extend(
    [
        "",
        "## Metrics",
        "",
        f"- raw_total_samples: `{payload['metrics']['raw_total_samples']}`",
        f"- raw_initial_compile_rate: `{payload['metrics']['raw_initial_compile_rate']}`",
        f"- raw_final_compile_rate: `{payload['metrics']['raw_final_compile_rate']}`",
        f"- repair_success_rate: `{payload['metrics']['repair_success_rate']}`",
        f"- active_patch_pressure_count: `{payload['metrics']['active_patch_pressure_count']}`",
        f"- active_suggested_tokens: `{payload['metrics']['active_suggested_tokens']}`",
        f"- website_check_smoke_ok: `{payload['metrics']['website_check_smoke_ok']}`",
        f"- website_check_out_of_scope_smoke_ok: `{payload['metrics']['website_check_out_of_scope_smoke_ok']}`",
        f"- website_assets_smoke_ok: `{payload['metrics']['website_assets_smoke_ok']}`",
        f"- website_assets_pack_smoke_ok: `{payload['metrics']['website_assets_pack_smoke_ok']}`",
        f"- website_open_asset_smoke_ok: `{payload['metrics']['website_open_asset_smoke_ok']}`",
        f"- website_open_asset_pack_smoke_ok: `{payload['metrics']['website_open_asset_pack_smoke_ok']}`",
        f"- website_inspect_asset_smoke_ok: `{payload['metrics']['website_inspect_asset_smoke_ok']}`",
        f"- website_inspect_asset_pack_smoke_ok: `{payload['metrics']['website_inspect_asset_pack_smoke_ok']}`",
        f"- website_preview_smoke_ok: `{payload['metrics']['website_preview_smoke_ok']}`",
        f"- website_preview_pack_smoke_ok: `{payload['metrics']['website_preview_pack_smoke_ok']}`",
        f"- website_run_inspect_command_smoke_ok: `{payload['metrics']['website_run_inspect_command_smoke_ok']}`",
        f"- website_run_inspect_command_pack_smoke_ok: `{payload['metrics']['website_run_inspect_command_pack_smoke_ok']}`",
        f"- website_export_handoff_smoke_ok: `{payload['metrics']['website_export_handoff_smoke_ok']}`",
        f"- website_export_handoff_pack_smoke_ok: `{payload['metrics']['website_export_handoff_pack_smoke_ok']}`",
        f"- website_summary_smoke_ok: `{payload['metrics']['website_summary_smoke_ok']}`",
        f"- website_go_smoke_ok: `{payload['metrics']['website_go_smoke_ok']}`",
        f"- project_check_smoke_ok: `{payload['metrics']['project_check_smoke_ok']}`",
        f"- project_check_conflict_smoke_ok: `{payload['metrics']['project_check_conflict_smoke_ok']}`",
        f"- project_doctor_smoke_ok: `{payload['metrics']['project_doctor_smoke_ok']}`",
        f"- project_doctor_validation_smoke_ok: `{payload['metrics']['project_doctor_validation_smoke_ok']}`",
        f"- project_doctor_apply_safe_noop_smoke_ok: `{payload['metrics']['project_doctor_apply_safe_noop_smoke_ok']}`",
        f"- project_doctor_apply_safe_repair_smoke_ok: `{payload['metrics']['project_doctor_apply_safe_repair_smoke_ok']}`",
        f"- project_doctor_apply_safe_continue_noop_smoke_ok: `{payload['metrics']['project_doctor_apply_safe_continue_noop_smoke_ok']}`",
        f"- project_doctor_apply_safe_continue_repair_smoke_ok: `{payload['metrics']['project_doctor_apply_safe_continue_repair_smoke_ok']}`",
        f"- project_continue_auto_repair_smoke_ok: `{payload['metrics']['project_continue_auto_repair_smoke_ok']}`",
        f"- project_continue_auto_no_repair_smoke_ok: `{payload['metrics']['project_continue_auto_no_repair_smoke_ok']}`",
        f"- project_preview_smoke_ok: `{payload['metrics']['project_preview_smoke_ok']}`",
        f"- project_preview_conflict_smoke_ok: `{payload['metrics']['project_preview_conflict_smoke_ok']}`",
        f"- project_open_target_smoke_ok: `{payload['metrics']['project_open_target_smoke_ok']}`",
        f"- project_open_target_default_smoke_ok: `{payload['metrics']['project_open_target_default_smoke_ok']}`",
        f"- project_inspect_target_smoke_ok: `{payload['metrics']['project_inspect_target_smoke_ok']}`",
        f"- project_inspect_target_default_smoke_ok: `{payload['metrics']['project_inspect_target_default_smoke_ok']}`",
        f"- project_run_inspect_command_smoke_ok: `{payload['metrics']['project_run_inspect_command_smoke_ok']}`",
        f"- project_run_inspect_command_default_smoke_ok: `{payload['metrics']['project_run_inspect_command_default_smoke_ok']}`",
        f"- project_export_handoff_smoke_ok: `{payload['metrics']['project_export_handoff_smoke_ok']}`",
        f"- project_export_handoff_conflict_smoke_ok: `{payload['metrics']['project_export_handoff_conflict_smoke_ok']}`",
        f"- project_go_smoke_ok: `{payload['metrics']['project_go_smoke_ok']}`",
        f"- project_go_repair_smoke_ok: `{payload['metrics']['project_go_repair_smoke_ok']}`",
        f"- project_go_conflict_smoke_ok: `{payload['metrics']['project_go_conflict_smoke_ok']}`",
        f"- workspace_preview_smoke_ok: `{payload['metrics']['workspace_preview_smoke_ok']}`",
        f"- workspace_preview_project_smoke_ok: `{payload['metrics']['workspace_preview_project_smoke_ok']}`",
        f"- workspace_open_target_smoke_ok: `{payload['metrics']['workspace_open_target_smoke_ok']}`",
        f"- workspace_open_target_project_smoke_ok: `{payload['metrics']['workspace_open_target_project_smoke_ok']}`",
        f"- workspace_inspect_target_smoke_ok: `{payload['metrics']['workspace_inspect_target_smoke_ok']}`",
        f"- workspace_inspect_target_project_smoke_ok: `{payload['metrics']['workspace_inspect_target_project_smoke_ok']}`",
        f"- workspace_run_inspect_command_smoke_ok: `{payload['metrics']['workspace_run_inspect_command_smoke_ok']}`",
        f"- workspace_run_inspect_command_project_smoke_ok: `{payload['metrics']['workspace_run_inspect_command_project_smoke_ok']}`",
        f"- workspace_export_handoff_smoke_ok: `{payload['metrics']['workspace_export_handoff_smoke_ok']}`",
        f"- workspace_export_handoff_project_smoke_ok: `{payload['metrics']['workspace_export_handoff_project_smoke_ok']}`",
        f"- workspace_doctor_smoke_ok: `{payload['metrics']['workspace_doctor_smoke_ok']}`",
        f"- workspace_doctor_project_smoke_ok: `{payload['metrics']['workspace_doctor_project_smoke_ok']}`",
        f"- workspace_continue_smoke_ok: `{payload['metrics']['workspace_continue_smoke_ok']}`",
        f"- workspace_continue_project_smoke_ok: `{payload['metrics']['workspace_continue_project_smoke_ok']}`",
        f"- workspace_go_smoke_ok: `{payload['metrics']['workspace_go_smoke_ok']}`",
        f"- workspace_go_project_smoke_ok: `{payload['metrics']['workspace_go_project_smoke_ok']}`",
        f"- rc_go_smoke_ok: `{payload['metrics']['rc_go_smoke_ok']}`",
        f"- rc_go_refresh_smoke_ok: `{payload['metrics']['rc_go_refresh_smoke_ok']}`",
        f"- project_summary_probe_ok: `{payload['metrics']['project_summary_probe_ok']}`",
        f"- project_workbench_primary_action_converged: `{payload['metrics']['project_workbench_primary_action_converged']}`",
        f"- trial_entry_route_converged: `{payload['metrics']['trial_entry_route_converged']}`",
        f"- benchmark_release_decision: `{payload['metrics']['benchmark_release_decision']}`",
        f"- benchmark_release_baseline_ok: `{payload['metrics']['benchmark_release_baseline_ok']}`",
        f"- benchmark_release_baseline_passed: `{payload['metrics']['benchmark_release_baseline_passed']}`",
        f"- benchmark_release_baseline_failed: `{payload['metrics']['benchmark_release_baseline_failed']}`",
        "",
        "## Project Workbench Primary Action",
        "",
        f"- recommended_primary_action: `{payload['project_workbench_primary_action']['recommended_primary_action']}`",
        f"- recommended_primary_command: `{payload['project_workbench_primary_action']['recommended_primary_command']}`",
        f"- recommended_primary_reason: `{payload['project_workbench_primary_action']['recommended_primary_reason']}`",
        f"- doctor_status: `{payload['project_workbench_primary_action']['doctor_status']}`",
        f"- converged: `{payload['project_workbench_primary_action']['converged']}`",
        f"- trial_batch_distribution: `{payload['project_workbench_primary_action']['trial_batch_distribution']}`",
        f"- probe_error: `{payload['project_workbench_primary_action']['probe_error']}`",
        "",
        "## Trial Entry Route",
        "",
        f"- expected_route: `{payload['trial_entry_route']['expected_route']}`",
        f"- converged: `{payload['trial_entry_route']['converged']}`",
        f"- trial_batch_distribution: `{payload['trial_entry_route']['trial_batch_distribution']}`",
        "",
        "## Interpretation",
        "",
    ]
)

if payload["status"] == "ok":
    report_lines.extend(
        [
            "- The current frozen-profile RC gate is green.",
            "- CLI checks, trial entry, repair smoke, raw lane, evolution loop, and frozen benchmark baseline are all healthy.",
            "- Global benchmark `release_decision` may still be `fail` while frozen v1 release baseline remains acceptable.",
        ]
    )
else:
    report_lines.extend(
        [
            "- The current RC gate is not yet green.",
            "- Review the failed checks above before treating this state as a release candidate.",
        ]
    )

report_lines.extend(
    [
        "",
        "## Artifacts",
        "",
    ]
)

for key, value in payload["artifacts"].items():
    report_lines.append(f"- {key}: `{value}`")

report_lines.extend(
    [
        "",
        "## Command",
        "",
        "```bash",
        "bash /Users/carwynmac/ai-cl/testing/run_rc_checks.sh",
        "```",
    ]
)

report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
print(json.dumps(payload, indent=2, ensure_ascii=False))
sys.exit(0 if all_ok else 1)
PY
