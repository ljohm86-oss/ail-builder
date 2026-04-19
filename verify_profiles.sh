#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
ROOT_DIR="${AIL_REPO_ROOT:-$SCRIPT_DIR}"

echo "[1/3] verify landing profile"
"${ROOT_DIR}/verify_landing_profile.sh"

echo "[2/3] verify ecom_min profile"
"${ROOT_DIR}/verify_ecom_profile.sh"

echo "[3/3] verify after_sales profile"
"${ROOT_DIR}/verify_after_sales_profile.sh"

echo "PASS: all profile verifications passed"
