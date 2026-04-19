#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
ROOT_DIR="${AIL_REPO_ROOT:-$(cd -- "${SCRIPT_DIR}/.." && pwd)}"
python3 "${ROOT_DIR}/benchmark/run_benchmark.py"
