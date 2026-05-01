#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
ROOT="${AIL_REPO_ROOT:-$(cd -- "${SCRIPT_DIR}/.." && pwd)}"
export AIL_REPO_ROOT="$ROOT"
export AIL_CLOUD_BASE_URL="${AIL_CLOUD_BASE_URL:-embedded://local}"

bash "$ROOT/testing/cli_smoke.sh"
