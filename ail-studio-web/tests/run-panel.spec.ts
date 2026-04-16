import { expect, test, type Page } from '@playwright/test'

const DEFAULT_PROMPT = '请生成最小可编译 AIL：users(username:str,pwd:str)，API 仅 /api/login /api/register /api/me，页面仅 / /login /403'
const DEFAULT_MODEL = process.env.AIL_LLM_MODEL || 'moonshot-v1-32k'
const DEFAULT_PROJECT = process.env.AIL_PROJECT_NAME || 'AutoProject'
const DEFAULT_API_KEY = process.env.AIL_LLM_API_KEY || ''

function hasNonUiLine(text: string): boolean {
  return text
    .split('\n')
    .map((line) => line.trim())
    .some((line) => line.length > 0 && !line.includes('[ui]'))
}

async function assertServiceUp(page: Page, name: string, url: string): Promise<void> {
  try {
    const resp = await page.request.get(url, {
      failOnStatusCode: false,
      timeout: 5000,
    })
    if (!resp) {
      throw new Error('no response')
    }
  } catch {
    throw new Error(`${name} is not reachable at ${url}. Start required services before running E2E.`)
  }
}

async function openFreshApp(
  page: Page,
  options?: {
    previewUrl?: string
  },
): Promise<void> {
  await assertServiceUp(page, 'AIL mothership', 'http://127.0.0.1:5002/compile')
  // Probe proxy port reachability only; this does not validate /status query semantics.
  await assertServiceUp(
    page,
    'Run proxy',
    'http://127.0.0.1:5050/status?project_root=%2FUsers%2Fcarwynmac%2Fai-cl%2Foutput_projects',
  )

  await page.addInitScript(({ apiKey, model, projectName, previewUrl }) => {
    window.localStorage.clear()
    if (apiKey) window.localStorage.setItem('ail_llm_api_key', apiKey)
    if (model) window.localStorage.setItem('ail_llm_model', model)
    if (projectName) window.localStorage.setItem('ail_project_name', projectName)
    if (previewUrl) window.localStorage.setItem('ail_preview_url', previewUrl)
  }, { apiKey: DEFAULT_API_KEY, model: DEFAULT_MODEL, projectName: DEFAULT_PROJECT, previewUrl: options?.previewUrl || '' })
  await page.goto('/')
  await expect(page.getByTestId('session-select')).toBeVisible()
}

async function generateAndCompile(page: Page, prompt = DEFAULT_PROMPT): Promise<void> {
  const compileButton = page.getByTestId('btn-compile')

  for (let attempt = 1; attempt <= 2; attempt += 1) {
    const generateErrorCountBefore = await page.getByTestId('chat-msg-error').count()
    await page.getByTestId('prompt-input').fill(prompt)
    await page.getByTestId('btn-send').click()

    const generateDeadline = Date.now() + 120_000
    while (Date.now() < generateDeadline) {
      if (await compileButton.isEnabled()) {
        break
      }
      const errorCount = await page.getByTestId('chat-msg-error').count()
      if (errorCount > generateErrorCountBefore) {
        const errorText = (await page.getByTestId('chat-msg-error').last().innerText()).trim()
        throw new Error(
          `generate_ail returned an error before AIL output. ${errorText || 'Set AIL_LLM_API_KEY and ensure 5002 is healthy.'}`,
        )
      }
      await page.waitForTimeout(500)
    }

    if (!(await compileButton.isEnabled())) {
      throw new Error('generate_ail did not produce AIL within 120s. Check AIL_LLM_API_KEY and 5002 service.')
    }

    const compileErrorCountBefore = await page.getByTestId('chat-msg-error').count()
    await compileButton.click()

    const compileDeadline = Date.now() + 120_000
    while (Date.now() < compileDeadline) {
      if ((await page.getByTestId('compile-card').count()) > 0) {
        await expect(page.getByTestId('compile-card')).toBeVisible()
        return
      }
      const errorCount = await page.getByTestId('chat-msg-error').count()
      if (errorCount > compileErrorCountBefore) {
        const errorText = (await page.getByTestId('chat-msg-error').last().innerText()).trim()
        if (attempt === 2) {
          throw new Error(`compile returned an error: ${errorText || 'unknown compile error'}`)
        }
        break
      }
      await page.waitForTimeout(500)
    }
  }

  throw new Error('compile-card did not appear after retry')
}

async function runProject(page: Page): Promise<void> {
  await page.getByTestId('btn-run').click()

  const deadline = Date.now() + 30_000
  while (Date.now() < deadline) {
    const running = (await page.getByTestId('run-running').textContent())?.trim()
    const pid = (await page.getByTestId('run-pid').textContent())?.trim()
    if (running === 'true' && pid && /^\d+$/.test(pid)) {
      return
    }

    const xtermText = (await page.getByTestId('xterm-mirror').textContent()) ?? ''
    if (xtermText.includes('[ui] run error')) {
      const lines = xtermText
        .split('\n')
        .map((line) => line.trim())
        .filter(Boolean)
      const lastError = lines.reverse().find((line) => line.includes('[ui] run error')) || '[ui] run error'
      throw new Error(`run failed: ${lastError}`)
    }
    await page.waitForTimeout(500)
  }

  throw new Error('run did not reach running=true with numeric pid within 30s')
}

async function safeStop(page: Page): Promise<void> {
  if ((await page.getByTestId('compile-card').count()) === 0) {
    return
  }

  const stopButton = page.getByTestId('btn-stop')
  if (!(await stopButton.isEnabled())) {
    return
  }

  await stopButton.click()
  await expect(page.getByTestId('run-running')).toHaveText('false', { timeout: 15_000 })
}

test.describe.serial('Run panel acceptance', () => {
  test('1) compile 后状态条初始值', async ({ page }) => {
    await openFreshApp(page)

    await page.getByTestId('session-new').click()
    await generateAndCompile(page)

    await expect(page.getByTestId('run-status')).toBeVisible()
    await expect(page.getByTestId('run-running')).toHaveText('false')
    await expect(page.getByTestId('run-pid')).toHaveText('-')

    const detectState = (await page.getByTestId('run-detect').textContent())?.trim()
    expect(detectState).toBe('pending')

    const polled = (await page.getByTestId('run-polled').textContent())?.trim() ?? ''
    expect(['', '-']).toContain(polled)
  })

  test('2) Session A Run 后切到 Session B，不串状态', async ({ page }) => {
    await openFreshApp(page)
    await generateAndCompile(page)

    const sessionSelect = page.getByTestId('session-select')
    const sessionAValue = await sessionSelect.inputValue()

    await runProject(page)

    await page.getByTestId('session-new').click()
    await expect(page.getByTestId('compile-card')).toHaveCount(0)

    await sessionSelect.selectOption(sessionAValue)
    await expect(page.getByTestId('run-running')).toHaveText('true', { timeout: 10_000 })
    await expect(page.getByTestId('run-pid')).toHaveText(/\d+/, { timeout: 10_000 })

    await safeStop(page)
  })

  test('3) Detect + URL 复制 + xterm 文案', async ({ page }) => {
    await openFreshApp(page)
    await generateAndCompile(page)
    const mirrorBeforeRun = (await page.getByTestId('xterm-mirror').textContent()) ?? ''
    await runProject(page)

    await expect
      .poll(async () => {
        const mirrorNow = (await page.getByTestId('xterm-mirror').textContent()) ?? ''
        const delta = mirrorNow.slice(mirrorBeforeRun.length)
        return hasNonUiLine(delta)
      }, {
        timeout: 20_000,
        message: 'sse log not received; check /proxy/stream',
      })
      .toBe(true)

    await page.getByTestId('btn-detect').click()
    await expect(page.getByTestId('run-detect')).toHaveText('found', { timeout: 40_000 })
    const polledBefore = (await page.getByTestId('run-polled').textContent())?.trim() ?? '-'
    await page.waitForTimeout(6500)
    let polledAfter = (await page.getByTestId('run-polled').textContent())?.trim() ?? '-'
    if (polledAfter === polledBefore) {
      await page.waitForTimeout(2500)
      polledAfter = (await page.getByTestId('run-polled').textContent())?.trim() ?? '-'
    }
    expect(polledAfter).not.toBe('-')
    expect(polledAfter).not.toBe(polledBefore)

    const frontendUrl = page.getByTestId('run-frontend-url')
    const backendUrl = page.getByTestId('run-backend-url')

    await expect(frontendUrl).not.toHaveText('-')
    await expect(backendUrl).not.toHaveText('-')

    await frontendUrl.click()
    await expect(page.getByTestId('xterm-mirror')).toContainText('[ui] copied frontend_url', { timeout: 10_000 })

    await backendUrl.click()
    await expect(page.getByTestId('xterm-mirror')).toContainText('[ui] copied backend_url', { timeout: 10_000 })

    await safeStop(page)
  })

  test('4) Stop 后状态回落', async ({ page }) => {
    await openFreshApp(page)
    await generateAndCompile(page)
    await runProject(page)

    await page.getByTestId('btn-stop').click()

    await expect(page.getByTestId('run-running')).toHaveText('false', { timeout: 15_000 })
    await expect(page.getByTestId('run-pid')).toHaveText('-', { timeout: 15_000 })
    await expect(page.getByTestId('run-detect')).toHaveText('timeout', { timeout: 15_000 })
    await expect(page.getByTestId('xterm-mirror')).toContainText('[ui] stop ok', { timeout: 10_000 })
  })

  test('5) 日志控制：Pause/Filter/Clear 生效', async ({ page }) => {
    await openFreshApp(page)
    await generateAndCompile(page)
    await runProject(page)

    await expect
      .poll(async () => {
        const mirror = (await page.getByTestId('xterm-mirror').textContent()) ?? ''
        return mirror.trim().length > 0
      }, { timeout: 20_000 })
      .toBe(true)

    await page.getByTestId('btn-log-pause').click()
    const pausedSnapshot = (await page.getByTestId('xterm-mirror').textContent()) ?? ''

    await page.waitForTimeout(3000)
    const afterPauseSnapshot = (await page.getByTestId('xterm-mirror').textContent()) ?? ''
    expect(afterPauseSnapshot).toBe(pausedSnapshot)

    await page.getByTestId('log-filter').selectOption('errors')
    await page.getByTestId('btn-log-pause').click()
    await expect(page.getByTestId('xterm-mirror')).toContainText('[ui] resumed, dropped=', { timeout: 10_000 })

    await page.getByTestId('btn-log-clear').click()
    await expect(page.getByTestId('xterm-mirror')).toContainText('[ui] log cleared', { timeout: 10_000 })

    await safeStop(page)
  })

  test('6) Preview reset 防呆生效', async ({ page }) => {
    await openFreshApp(page, { previewUrl: 'http://127.0.0.1:4173' })

    await expect(page.getByTestId('xterm-mirror')).toContainText(
      '[ui] preview url pointed to studio, reset',
      { timeout: 10_000 },
    )

    await page.getByTestId('btn-reset-preview').click()
    await expect(page.getByTestId('xterm-mirror')).toContainText('[ui] preview reset', { timeout: 10_000 })
  })
})
