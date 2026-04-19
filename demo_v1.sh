#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
ROOT_DIR="${AIL_REPO_ROOT:-$SCRIPT_DIR}"
PYTHONPATH="$ROOT_DIR" python3 -m cli trial-run "$@"
