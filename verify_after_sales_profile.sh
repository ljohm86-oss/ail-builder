#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
ROOT_DIR="${AIL_REPO_ROOT:-$SCRIPT_DIR}"
AIL_FILE="${ROOT_DIR}/profile_examples/after_sales_min.ail"

if [ ! -f "${AIL_FILE}" ]; then
  echo "FAIL: missing after_sales sample AIL: ${AIL_FILE}"
  exit 10
fi

python3 - "${ROOT_DIR}" "${AIL_FILE}" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
ail_file = Path(sys.argv[2])
ail_text = ail_file.read_text(encoding="utf-8")

sys.path.insert(0, str(root))
from ail_server_v5 import app  # type: ignore

with app.test_client() as client:
    resp = client.post("/compile", json={"ail_code": ail_text})
    if resp.status_code != 200:
        print(f"FAIL: /compile status_code={resp.status_code}")
        print(resp.get_data(as_text=True))
        sys.exit(11)
    data = resp.get_json() or {}

if data.get("status") != "ok":
    print("FAIL: compile status is not ok")
    print(json.dumps(data, ensure_ascii=False, indent=2))
    sys.exit(12)

summary = data.get("summary", {}) or {}
profiles_used = summary.get("profiles_used", [])
profile_resolution = summary.get("profile_resolution")
if "after_sales" not in profiles_used:
    print(f"FAIL: summary.profiles_used missing after_sales: {profiles_used}")
    sys.exit(13)
if profile_resolution != "explicit":
    print(f"FAIL: summary.profile_resolution expected explicit, got {profile_resolution}")
    sys.exit(14)

project_root = Path(str(data.get("project_root", ""))).resolve()
routes_path = project_root / "frontend" / "src" / "router" / "routes.generated.ts"
if not routes_path.exists():
    print(f"FAIL: routes file missing: {routes_path}")
    sys.exit(15)

routes_text = routes_path.read_text(encoding="utf-8")
if "/after-sales" not in routes_text:
    print("FAIL: /after-sales route missing for after_sales profile")
    sys.exit(16)

for forbidden in ["/product/:id", "/cart", "/checkout", "/shop/:id", "/search"]:
    if forbidden in routes_text:
        print(f"FAIL: unexpected ecom route present in after_sales-only profile: {forbidden}")
        sys.exit(17)

print("PASS: after_sales profile verify passed")
PY
