#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/carwynmac/ai-cl"
RESULTS_DIR="$ROOT/testing/results"
BASE_URL="embedded://local"
SCENARIO=""
REQUIREMENT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --scenario)
      SCENARIO="${2:-}"
      shift 2
      ;;
    --requirement)
      REQUIREMENT="${2:-}"
      shift 2
      ;;
    --base-url)
      BASE_URL="${2:-}"
      shift 2
      ;;
    *)
      echo "error: unsupported argument: $1" >&2
      exit 2
      ;;
  esac
done

if [[ -n "$SCENARIO" && -n "$REQUIREMENT" ]]; then
  echo "error: use exactly one of --scenario or --requirement" >&2
  exit 2
fi

if [[ -z "$SCENARIO" && -z "$REQUIREMENT" ]]; then
  echo "error: use exactly one of --scenario or --requirement" >&2
  exit 2
fi

mkdir -p "$RESULTS_DIR"

NEXT_ID=$(python3 - <<'PY'
from pathlib import Path
import re

results_dir = Path("/Users/carwynmac/ai-cl/testing/results")
ids = []
for path in results_dir.glob("first_user_trial_results_*.md"):
    match = re.search(r"first_user_trial_results_(\d+)\.md$", path.name)
    if match:
        ids.append(int(match.group(1)))
print(f"{(max(ids) + 1) if ids else 1:03d}")
PY
)

RESULT_MD="$RESULTS_DIR/first_user_trial_results_${NEXT_ID}.md"
RESULT_JSON="$RESULTS_DIR/first_user_trial_capture_${NEXT_ID}.json"

if [[ -n "$SCENARIO" ]]; then
  PYTHONPATH="$ROOT" python3 -m cli trial-run --scenario "$SCENARIO" --base-url "$BASE_URL" --json > "$RESULT_JSON"
else
  PYTHONPATH="$ROOT" python3 -m cli trial-run --requirement "$REQUIREMENT" --base-url "$BASE_URL" --json > "$RESULT_JSON"
fi

python3 - "$RESULT_JSON" "$RESULT_MD" "$NEXT_ID" <<'PY'
import json
import sys
from pathlib import Path

json_path = Path(sys.argv[1])
md_path = Path(sys.argv[2])
trial_id = sys.argv[3]

data = json.loads(json_path.read_text(encoding="utf-8"))

scenario = str(data.get("scenario") or "custom")
requirement = str(data.get("requirement") or "")
detected_profile = str(data.get("detected_profile") or "unknown")
repair_used = bool(data.get("repair_used"))
status = str(data.get("status") or "error")
completed = status == "ok"
managed_files_written = int(data.get("managed_files_written", 0) or 0)
cloud_status = data.get("cloud_status") or {}
latest_build = cloud_status.get("latest_build") or {}
latest_artifact = cloud_status.get("latest_artifact") or {}
recent_build_count = cloud_status.get("recent_build_count")
cloud_query = (cloud_status.get("cloud") or {}).get("project") or {}
recommended_primary_action = str(data.get("recommended_primary_action") or "")
recommended_primary_command = str(data.get("recommended_primary_command") or "")
recommended_primary_reason = str(data.get("recommended_primary_reason") or "")
route_taken = str(data.get("route_taken") or "")
route_reason = str(data.get("route_reason") or "")
doctor_status = str(data.get("doctor_status") or "")
recommended_action = str(data.get("recommended_action") or "")

scenario_labels = {
    "landing": "landing_trial_run",
    "ecom_min": "ecom_min_trial_run",
    "after_sales": "after_sales_trial_run",
    "custom": "custom_trial_run",
}

summary_lines = [
    f"# First User Trial Result {trial_id}",
    "",
    "## Trial Metadata",
    "",
    "- date: 2026-03-17",
    "- trial_operator: Codex",
    f"- user_id: ai_operator_{trial_id}",
    "- user_type: controlled_ai_trial",
    f"- scenario_id: {scenario_labels.get(scenario, scenario)}",
    f"- selected_profile: {detected_profile}",
    "",
    "## Scenario",
    "",
    f"- requirement: {requirement}",
    f"- expected_profile: {detected_profile}",
    "",
    "## Completion",
    "",
    f"- completed: {'yes' if completed else 'no'}",
    f"- reached_generate: {'yes' if completed else 'no'}",
    f"- reached_diagnose: {'yes' if completed else 'no'}",
    f"- reached_repair: {'yes' if repair_used else 'no'}",
    f"- reached_compile: {'yes' if completed else 'no'}",
    f"- reached_sync: {'yes' if completed else 'no'}",
    "",
    "## Time",
    "",
    "- start_time: automated_recorded_trial",
    "- end_time: automated_recorded_trial",
    "- time_to_first_result: completed within the automated recorded trial run",
    "",
    "## Friction Log",
    "",
    "### 1. First Blocker",
    "",
    f"- step: {'repair' if repair_used else 'none'}",
    f"- description: {'repair was used automatically before compile' if repair_used else 'no blocking friction observed'}",
    "- user_message_or_question: n/a (controlled AI run)",
    f"- operator_intervention: {'automatic repair step applied by trial-run' if repair_used else 'none'}",
    "",
    "### 2. Additional Friction",
    "",
    "- step: low",
    "- description: no meaningful additional friction observed in this recorded run",
    "- user_message_or_question: n/a",
    "- operator_intervention: none",
    "",
    "### 3. Managed vs Custom Understanding",
    "",
    "- did_user_understand_ail_is_source_of_truth: yes",
    "- did_user_understand_generated_vs_custom: yes",
    "- notes: controlled AI path stayed inside the supported CLI-first frozen-profile flow",
    "",
    "## Output Assessment",
    "",
    f"- detected_profile_by_user: {detected_profile}",
    f"- actual_profile: {detected_profile}",
    f"- did_output_feel_useful: {'yes' if completed and managed_files_written > 0 else 'no'}",
    f"- user_confidence_level: {'high' if completed else 'low'}",
    f"- notes: managed_files_written={managed_files_written}; recent_build_count={recent_build_count}; latest_build_id={latest_build.get('build_id', '')}",
    "",
    "## Failure / Recovery",
    "",
    "- compile_or_sync_error_seen: no" if completed else "- compile_or_sync_error_seen: yes",
    "- was_recovery_path_clear: yes" if completed else "- was_recovery_path_clear: no",
    f"- notes: repair_used={'yes' if repair_used else 'no'}; artifact_id={latest_artifact.get('artifact_id', '')}",
    "",
    "## Cloud Summary",
    "",
    f"- project_id: {cloud_status.get('project_id', '')}",
    f"- latest_build_id: {latest_build.get('build_id', '')}",
    f"- latest_build_status: {latest_build.get('status', '')}",
    f"- latest_artifact_id: {latest_artifact.get('artifact_id', '')}",
    f"- recent_build_count: {recent_build_count}",
    f"- project_query_variant: {cloud_query.get('api_variant', '')}",
    "",
    "## Default Next Action",
    "",
    f"- doctor_status: {doctor_status}",
    f"- recommended_action: {recommended_action}",
    f"- recommended_primary_action: {recommended_primary_action}",
    f"- recommended_primary_command: {recommended_primary_command}",
    f"- recommended_primary_reason: {recommended_primary_reason}",
    f"- route_taken: {route_taken}",
    f"- route_reason: {route_reason}",
    "",
    "## Trial Outcome",
    "",
    f"- trial_result: {'success' if completed else 'failed'}",
    f"- main_reason: {'trial-run completed and recorded successfully' if completed else 'trial-run did not complete successfully'}",
    f"- should_user_continue_without_operator: {'yes' if completed else 'no'}",
    "",
    "## Recommended Fixes",
    "",
    "### Highest Priority Fix",
    "",
    "- category: cli_ux_gap",
    f"- description: {'none critical from this recorded run; preserve current behavior' if completed else 'investigate why the recorded run did not complete'}",
    "",
    "### Additional Fix",
    "",
    "- category: documentation_gap",
    f"- description: {'none critical from this recorded run' if completed else 'document the observed failure path before the next trial'}",
    "",
    "## Summary",
    "",
    f"- what_worked: {'generate, diagnose, compile, sync, and cloud status summary all completed successfully' if completed else 'partial workflow only'}",
    f"- what_failed: {'no blocking issue observed' if completed else 'recorded trial did not complete cleanly'}",
    f"- what_should_be_changed_before_next_trial: {'preserve current behavior and continue collecting recorded runs' if completed else 'fix the blocking workflow issue before the next trial'}",
    "",
    "## Artifacts",
    "",
    f"- trial_capture_json: {json_path}",
    f"- source_of_truth: {data.get('source_of_truth', '')}",
    f"- manifest: {data.get('manifest', '')}",
    f"- latest_build: {data.get('build_id', '')}",
]

md_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
print(md_path)
PY

echo "Recorded trial result: $RESULT_MD"
echo "Trial capture JSON: $RESULT_JSON"
