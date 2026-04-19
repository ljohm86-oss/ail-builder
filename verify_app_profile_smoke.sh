#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
ROOT_DIR="${AIL_REPO_ROOT:-$SCRIPT_DIR}"
PROJECT_ROOT="${ROOT_DIR}/output_projects/AIChatMini"
ARTIFACT_DIR="${ROOT_DIR}/output/playwright/app_min_smoke"
LOG_PATH="${ARTIFACT_DIR}/start.log"

mkdir -p "${ARTIFACT_DIR}"

export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export PWCLI="${CODEX_HOME}/skills/playwright/scripts/playwright_cli.sh"
export PLAYWRIGHT_CLI_SESSION="app-min-smoke"

pwcli() {
  bash "${PWCLI}" "$@"
}

if ! command -v npx >/dev/null 2>&1; then
  echo "FAIL: npx not found"
  exit 10
fi

if [ ! -f "${PWCLI}" ]; then
  echo "FAIL: missing Playwright wrapper: ${PWCLI}"
  exit 11
fi

SKIP_RUN_CHECK=1 bash "${ROOT_DIR}/verify_app_profile.sh"

if [ ! -f "${PROJECT_ROOT}/start.sh" ]; then
  echo "FAIL: missing generated start.sh at ${PROJECT_ROOT}"
  exit 12
fi

cleanup() {
  pwcli close >/dev/null 2>&1 || true
  if [ -n "${WRAPPER_PID:-}" ]; then
    kill "${WRAPPER_PID}" >/dev/null 2>&1 || true
    wait "${WRAPPER_PID}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

bash "${PROJECT_ROOT}/start.sh" >"${LOG_PATH}" 2>&1 &
WRAPPER_PID=$!

FRONTEND_URL=""
for _ in $(seq 1 40); do
  sleep 1
  if grep -q 'FRONTEND_URL=http://127.0.0.1:' "${LOG_PATH}"; then
    FRONTEND_URL="$(grep -E '^FRONTEND_URL=http://127\.0\.0\.1:[0-9]+$' "${LOG_PATH}" | tail -n 1 | cut -d= -f2-)"
    if [ -n "${FRONTEND_URL}" ]; then
      break
    fi
  fi
done

if [ -z "${FRONTEND_URL}" ]; then
  echo "FAIL: FRONTEND_URL not found"
  tail -n 80 "${LOG_PATH}" || true
  exit 13
fi

READY=0
for _ in $(seq 1 40); do
  STATUS="$(curl -sS -o /dev/null -w "%{http_code}" "${FRONTEND_URL}/" || true)"
  if [ "${STATUS}" = "200" ]; then
    READY=1
    break
  fi
  sleep 1
done

if [ "${READY}" != "1" ]; then
  echo "FAIL: frontend route not ready at ${FRONTEND_URL}/"
  tail -n 80 "${LOG_PATH}" || true
  exit 14
fi

pwcli close >/dev/null 2>&1 || true
pwcli open "${FRONTEND_URL}/"
pwcli resize 430 932
pwcli snapshot >/dev/null

pwcli run-code "await page.getByTestId('app-topbar').waitFor(); await page.getByTestId('app-bottom-tab').waitFor(); await page.getByTestId('panel-chats').waitFor(); return 'ok';" >/dev/null

pwcli run-code "await page.getByTestId('btn-tab-contacts').click(); await page.getByTestId('panel-contacts').waitFor(); return 'contacts';" >/dev/null
pwcli run-code "await page.getByTestId('btn-tab-discover').click(); await page.getByTestId('panel-discover').waitFor(); return 'discover';" >/dev/null
pwcli run-code "await page.getByTestId('btn-tab-me').click(); await page.getByTestId('panel-me').waitFor(); return 'me';" >/dev/null

pwcli run-code "await page.getByTestId('btn-tab-chats').click(); await page.getByTestId('panel-chats').waitFor(); await page.getByTestId('chat-item-c1').click(); await page.getByTestId('chat-window').waitFor(); return 'chat-open';" >/dev/null
pwcli run-code "await page.getByTestId('btn-close-chat').click(); await page.waitForFunction(() => !document.querySelector('[data-testid=\"chat-window\"]')); return 'chat-closed';" >/dev/null

echo "PASS: app_min smoke test passed"
