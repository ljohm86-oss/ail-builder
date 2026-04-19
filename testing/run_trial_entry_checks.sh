#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
ROOT_DIR="${AIL_REPO_ROOT:-$(cd -- "${SCRIPT_DIR}/.." && pwd)}"
RESULTS_DIR="$ROOT_DIR/testing/results"
OUTPUT_JSON="$RESULTS_DIR/trial_run_smoke_results.json"
TMP_DIR=$(mktemp -d /tmp/ail_trial_entry_checks.XXXXXX)
trap 'rm -rf "$TMP_DIR"' EXIT

mkdir -p "$RESULTS_DIR"

scenarios=(landing ecom_min after_sales)
status="ok"

for scenario in "${scenarios[@]}"; do
  out="$TMP_DIR/${scenario}.json"
  if ! PYTHONPATH="$ROOT_DIR" python3 -m cli trial-run --scenario "$scenario" --base-url embedded://local --json > "$out"; then
    status="error"
  fi
done

python3 - "$TMP_DIR" "$OUTPUT_JSON" <<'PY'
import json
import sys
from pathlib import Path

tmp_dir = Path(sys.argv[1])
out_path = Path(sys.argv[2])
expected = {
    "landing": "landing",
    "ecom_min": "ecom_min",
    "after_sales": "after_sales",
}
checks = {}
all_ok = True
scenarios = []
for name, expected_profile in expected.items():
    path = tmp_dir / f"{name}.json"
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"status": "missing"}
    scenario_ok = (
        data.get("status") == "ok"
        and data.get("detected_profile") == expected_profile
        and data.get("repair_used") is False
        and int(data.get("managed_files_written", 0)) > 0
    )
    checks[f"{name}_ok"] = scenario_ok
    all_ok = all_ok and scenario_ok
    scenarios.append(
        {
            "scenario": name,
            "status": data.get("status", "missing"),
            "detected_profile": data.get("detected_profile"),
            "repair_used": data.get("repair_used"),
            "managed_files_written": data.get("managed_files_written"),
            "project_path": data.get("project_path"),
        }
    )

payload = {
    "status": "ok" if all_ok else "error",
    "checks": checks,
    "scenarios": scenarios,
}
out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(payload, indent=2, ensure_ascii=False))
sys.exit(0 if all_ok else 1)
PY
