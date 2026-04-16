#!/bin/bash
set -euo pipefail

echo "🚀 正在点燃 AIL 全栈引擎..."
cd "$(dirname "$0")"

if [ -n "${BACKEND_PORT:-}" ]; then
  BACKEND_SOURCE="env"
else
  BACKEND_SOURCE="default"
fi
if [ -n "${FRONTEND_PORT:-}" ]; then
  FRONTEND_SOURCE="env"
else
  FRONTEND_SOURCE="default"
fi
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"
echo "BACKEND_PORT=${BACKEND_PORT} (source=${BACKEND_SOURCE})"
echo "FRONTEND_PORT=${FRONTEND_PORT} (source=${FRONTEND_SOURCE})"
MAX_FRONTEND_PORT_TRIES=20

is_port_in_use() {
  lsof -tiTCP:"$1" -sTCP:LISTEN >/dev/null 2>&1
}

SELECTED_FRONTEND_PORT=""
for offset in $(seq 0 $((MAX_FRONTEND_PORT_TRIES - 1))); do
  candidate_port=$((FRONTEND_PORT + offset))
  if ! is_port_in_use "${candidate_port}"; then
    SELECTED_FRONTEND_PORT="${candidate_port}"
    break
  fi
done

if [ -z "${SELECTED_FRONTEND_PORT}" ]; then
  echo "❌ 未找到可用前端端口：${FRONTEND_PORT}-$((FRONTEND_PORT + MAX_FRONTEND_PORT_TRIES - 1))"
  exit 1
fi

(
  cd backend
  uvicorn main:app --reload --port "${BACKEND_PORT}" >/tmp/ail_uvicorn.log 2>&1
) &
BACKEND_PID=$!
echo "🛰️ 后端已启动，PID: ${BACKEND_PID}"

(
  cd frontend
  node ./node_modules/vite/bin/vite.js --host 0.0.0.0 --port "${SELECTED_FRONTEND_PORT}" >/tmp/ail_vite.log 2>&1
) &
FRONTEND_PID=$!
echo "🎨 前端已启动，PID: ${FRONTEND_PID}"
echo "FRONTEND_URL=http://127.0.0.1:${SELECTED_FRONTEND_PORT}"
echo "BACKEND_URL=http://127.0.0.1:${BACKEND_PORT}"

CLEANED_UP=0

cleanup() {
  if [ "${CLEANED_UP}" = "1" ]; then
    return
  fi
  CLEANED_UP=1
  echo ""
  echo "🛑 捕获退出信号，正在优雅关闭前后端进程..."
  kill "${BACKEND_PID}" "${FRONTEND_PID}" 2>/dev/null || true
  wait "${BACKEND_PID}" "${FRONTEND_PID}" 2>/dev/null || true
  echo "✅ 全栈引擎已安全熄火。"
}

trap cleanup SIGINT SIGTERM EXIT
wait
