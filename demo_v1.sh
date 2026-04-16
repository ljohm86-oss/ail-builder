#!/bin/zsh
set -euo pipefail

ROOT_DIR="/Users/carwynmac/ai-cl"
PYTHONPATH="$ROOT_DIR" python3 -m cli trial-run "$@"
