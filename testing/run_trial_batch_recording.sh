#!/usr/bin/env bash
set -euo pipefail

ROOT="${AIL_REPO_ROOT:-$(cd -- "$(dirname -- "$0")/.." && pwd)}"
export AIL_REPO_ROOT="$ROOT"
RESULTS_DIR="$ROOT/testing/results"
BASE_URL="embedded://local"
SCENARIOS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base-url)
      BASE_URL="${2:-}"
      shift 2
      ;;
    --scenario)
      SCENARIOS+=("${2:-}")
      shift 2
      ;;
    *)
      echo "error: unsupported argument: $1" >&2
      exit 2
      ;;
  esac
done

if [[ ${#SCENARIOS[@]} -eq 0 ]]; then
  SCENARIOS=(landing ecom_min after_sales)
fi

mkdir -p "$RESULTS_DIR"

TMP_DIR=$(mktemp -d /tmp/ail_trial_batch_recording.XXXXXX)
trap 'rm -rf "$TMP_DIR"' EXIT

for scenario in "${SCENARIOS[@]}"; do
  before_file="$TMP_DIR/${scenario}_before.txt"
  after_file="$TMP_DIR/${scenario}_after.txt"
  ls -1 "$RESULTS_DIR"/first_user_trial_results_*.md 2>/dev/null | sort > "$before_file" || true
  bash "$ROOT/testing/run_trial_recording.sh" --scenario "$scenario" --base-url "$BASE_URL" >/tmp/ail_trial_recording_${scenario}.log
  ls -1 "$RESULTS_DIR"/first_user_trial_results_*.md 2>/dev/null | sort > "$after_file" || true
  python3 - "$before_file" "$after_file" "$TMP_DIR/${scenario}_new.txt" <<'PY'
import sys
from pathlib import Path

before = set(Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()) if Path(sys.argv[1]).exists() else set()
after = set(Path(sys.argv[2]).read_text(encoding="utf-8").splitlines()) if Path(sys.argv[2]).exists() else set()
new_items = sorted(item for item in after - before if item.strip())
Path(sys.argv[3]).write_text("\n".join(new_items) + ("\n" if new_items else ""), encoding="utf-8")
PY
done

SUMMARY_MD="$RESULTS_DIR/first_user_trial_batch_recorded_summary_20260317.md"
SUMMARY_JSON="$RESULTS_DIR/first_user_trial_batch_recorded_summary_20260317.json"

python3 - "$TMP_DIR" "$SUMMARY_MD" "$SUMMARY_JSON" "${SCENARIOS[@]}" <<'PY'
import json
import re
import sys
from pathlib import Path

tmp_dir = Path(sys.argv[1])
summary_md = Path(sys.argv[2])
summary_json = Path(sys.argv[3])
scenarios = list(sys.argv[4:])

records = []
for scenario in scenarios:
    new_list_path = tmp_dir / f"{scenario}_new.txt"
    if not new_list_path.exists():
        continue
    for raw_path in [line.strip() for line in new_list_path.read_text(encoding="utf-8").splitlines() if line.strip()]:
        path = Path(raw_path)
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        def pick(label):
            match = re.search(rf"^- {re.escape(label)}: (.*)$", text, re.M)
            return match.group(1).strip() if match else ""

        records.append(
            {
                "scenario": scenario,
                "path": str(path),
                "selected_profile": pick("selected_profile"),
                "completed": pick("completed"),
                "reached_repair": pick("reached_repair"),
                "trial_result": pick("trial_result"),
                "main_reason": pick("main_reason"),
                "doctor_status": pick("doctor_status"),
                "recommended_action": pick("recommended_action"),
                "recommended_primary_action": pick("recommended_primary_action"),
                "recommended_primary_command": pick("recommended_primary_command"),
                "recommended_primary_reason": pick("recommended_primary_reason"),
                "route_taken": pick("route_taken"),
                "route_reason": pick("route_reason"),
            }
        )

completed = sum(1 for item in records if item["completed"] == "yes")
repair_required = sum(1 for item in records if item["reached_repair"] == "yes")
success = sum(1 for item in records if item["trial_result"] == "success")
recommended_primary_action_distribution = {}
route_taken_distribution = {}
for item in records:
    action = item.get("recommended_primary_action") or "unknown"
    recommended_primary_action_distribution[action] = recommended_primary_action_distribution.get(action, 0) + 1
    route = item.get("route_taken") or "unknown"
    route_taken_distribution[route] = route_taken_distribution.get(route, 0) + 1

payload = {
    "status": "ok",
    "scenario_count": len(scenarios),
    "record_count": len(records),
    "completed_count": completed,
    "repair_required_count": repair_required,
    "success_count": success,
    "scenarios": scenarios,
    "records": records,
    "recommended_primary_action_distribution": recommended_primary_action_distribution,
    "route_taken_distribution": route_taken_distribution,
}

summary_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

lines = [
    "# First User Trial Batch Recorded Summary 2026-03-17",
    "",
    "## Purpose",
    "",
    "This document summarizes the latest automated recorded frozen-profile batch.",
    "It is generated from `run_trial_recording.sh` outputs and exists to give a single view of the newest recorded trial set.",
    "",
    "## Scope",
    "",
    f"- scenarios_run: `{len(scenarios)}`",
    f"- records_created: `{len(records)}`",
    "",
    "Scenarios:",
]
for scenario in scenarios:
    lines.append(f"- `{scenario}`")

lines.extend(
    [
        "",
        "## Results",
        "",
        f"- completed_count: `{completed}`",
        f"- success_count: `{success}`",
        f"- repair_required_count: `{repair_required}`",
        "",
        "## Recommended Primary Action Distribution",
        "",
    ]
)

for action, count in sorted(recommended_primary_action_distribution.items()):
    lines.append(f"- `{action}`: `{count}`")

lines.extend(
    [
        "",
        "## Route Taken Distribution",
        "",
    ]
)

for route, count in sorted(route_taken_distribution.items()):
    lines.append(f"- `{route}`: `{count}`")

lines.extend(
    [
        "",
        "",
        "## Recorded Files",
        "",
    ]
)

for item in records:
    lines.append(
        f"- `{item['scenario']}` -> `{item['path']}` | profile=`{item['selected_profile']}` | completed=`{item['completed']}` | repair=`{item['reached_repair']}` | result=`{item['trial_result']}` | primary_action=`{item['recommended_primary_action']}` | route_taken=`{item['route_taken']}`"
    )

lines.extend(
    [
        "",
        "## Interpretation",
        "",
    ]
)

if records and success == len(records):
    lines.extend(
        [
            "- The latest recorded frozen-profile batch completed successfully.",
            "- These runs now leave both structured capture JSON and markdown result records automatically.",
        ]
    )
else:
    lines.extend(
        [
            "- At least one recorded trial in this batch did not finish cleanly.",
            "- Review the individual result files before using this batch as a baseline.",
        ]
    )

lines.extend(
    [
        "",
        "## Artifacts",
        "",
        f"- summary_json: `{summary_json}`",
        f"- results_dir: `{Path(__import__("os").environ["AIL_REPO_ROOT"]) / "testing" / "results"}`",
        "",
        "## Command",
        "",
        "```bash",
        f"bash {Path(__import__("os").environ["AIL_REPO_ROOT"]) / "testing" / "run_trial_batch_recording.sh"}",
        "```",
    ]
)

summary_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(summary_md)
PY

echo "Recorded batch summary: $SUMMARY_MD"
echo "Recorded batch summary JSON: $SUMMARY_JSON"
