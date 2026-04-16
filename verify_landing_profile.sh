#!/bin/bash
set -euo pipefail

ROOT_DIR="/Users/carwynmac/ai-cl"
AIL_FILE="${ROOT_DIR}/profile_examples/landing_min.ail"

if [ ! -f "${AIL_FILE}" ]; then
  echo "FAIL: missing landing sample AIL: ${AIL_FILE}"
  exit 10
fi

python3 - "${ROOT_DIR}" "${AIL_FILE}" <<'PY'
import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
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
if "landing" not in profiles_used:
    print(f"FAIL: summary.profiles_used missing landing: {profiles_used}")
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
required_routes = ["/", "/about", "/features", "/pricing", "/contact"]
for route in required_routes:
    if route not in routes_text:
        print(f"FAIL: required route missing: {route}")
        sys.exit(16)

forbidden_routes = ["/product/:id", "/cart", "/checkout", "/shop/:id", "/search", "/after-sales"]
for route in forbidden_routes:
    if route in routes_text:
        print(f"FAIL: forbidden route present in landing profile: {route}")
        sys.exit(17)

skip_run = os.getenv("SKIP_RUN_CHECK", "0").strip() == "1"
if skip_run:
    print("PASS: landing compile checks passed (run check skipped)")
    sys.exit(0)

start_script = project_root / "start.sh"
if not start_script.exists():
    print(f"FAIL: start.sh missing: {start_script}")
    sys.exit(18)

tmp_dir = Path(tempfile.mkdtemp(prefix="verify_landing_"))
log_path = tmp_dir / "start.log"
with log_path.open("w", encoding="utf-8") as log_file:
    proc = subprocess.Popen(
        ["bash", str(start_script)],
        cwd=str(project_root),
        stdout=log_file,
        stderr=subprocess.STDOUT,
        preexec_fn=os.setsid,
    )

frontend_url = None
try:
    for _ in range(35):
        time.sleep(1)
        log_text = log_path.read_text(encoding="utf-8", errors="ignore")
        match = re.search(r"FRONTEND_URL=(http://127\.0\.0\.1:\d+)", log_text)
        if match:
            frontend_url = match.group(1)
            break
    if not frontend_url:
        print("FAIL: FRONTEND_URL not found in start.sh log")
        print(log_path.read_text(encoding="utf-8", errors="ignore"))
        sys.exit(19)

    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    for route in required_routes:
        target = f"{frontend_url}{route}"
        status = None
        for _ in range(20):
            try:
                with opener.open(target, timeout=10) as r:
                    status = int(r.status)
            except urllib.error.HTTPError as e:
                status = int(e.code)
            except Exception:
                status = None
            if status == 200:
                break
            time.sleep(1)
        if status != 200:
            print(f"FAIL: route check {target} status={status}")
            sys.exit(20)
finally:
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    except Exception:
        pass
    try:
        proc.wait(timeout=8)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except Exception:
            pass
        proc.wait(timeout=5)

print("PASS: landing profile verify passed")
PY
