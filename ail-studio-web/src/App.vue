<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { Terminal } from 'xterm'
import { FitAddon } from 'xterm-addon-fit'
import 'xterm/css/xterm.css'

type MessageRole = 'user' | 'assistant' | 'system'
type MessageKind = 'prompt' | 'ail' | 'status' | 'error'
type AppState = 'IDLE' | 'GENERATING' | 'COMPILING'

type ChatMessage = {
  id: string
  role: MessageRole
  kind: MessageKind
  text: string
  ts: number
}

type CompileResult = {
  system: string
  projectRoot: string
  backendPaths: string[]
  hasRbac?: boolean
  hasOrRoles?: boolean
}

type RunStatus = {
  running: boolean
  pid: number | null
  frontend_url: string | null
  backend_url: string | null
  detect_state: 'found' | 'pending' | 'timeout'
  tail: string[]
}

type Session = {
  id: string
  name: string
  createdAt: number
  updatedAt: number
  messages: ChatMessage[]
  lastAil: string
  ailModels: Record<string, string>
  compileResult: CompileResult | null
  runStatus: RunStatus | null
  lastStatusPollTs: number | null
  lastError: string | null
  streamState: 'disconnected' | 'connecting' | 'connected' | 'ended'
  streamError: string | null
  streamLastEventTs: number | null
  logPaused: boolean
  logFilter: 'all' | 'errors'
  logDroppedCount: number
  logLastClearTs: number | null
  generateDraft: string
  generateStreaming: boolean
  generateStreamError: string | null
  generateStreamTs: number | null
}

const API_KEY_STORAGE = 'ail_llm_api_key'
const MODEL_STORAGE = 'ail_llm_model'
const PROJECT_STORAGE = 'ail_project_name'
const PREVIEW_STORAGE = 'ail_preview_url'
const SAFE_EMPTY_PREVIEW_URL = 'about:blank'
const DEFAULT_PREVIEW_URL = 'http://127.0.0.1:5173'
const SESSIONS_STORAGE = 'ail_studio_sessions_v1'
const ACTIVE_SESSION_STORAGE = 'ail_studio_active_session_v1'

const GENERATE_URL = '/mothership/generate_ail'
const COMPILE_URL = '/mothership/compile'
const RUN_PROXY_BASE = '/proxy'
const RUN_URL = `${RUN_PROXY_BASE}/run`
const STOP_URL = `${RUN_PROXY_BASE}/stop`
const STOP_ALL_URL = `${RUN_PROXY_BASE}/stop_all`
const STATUS_URL = `${RUN_PROXY_BASE}/status`

const apiKey = ref('')
const model = ref('moonshot-v1-32k')
const projectName = ref('AutoProject')
const previewUrl = ref(DEFAULT_PREVIEW_URL)
const promptInput = ref('')
const showApiKey = ref(false)
const settingsOpen = ref(false)
const state = ref<AppState>('IDLE')
const iframeKey = ref<number>(Date.now())
const chatListRef = ref<HTMLElement | null>(null)
const xtermContainerRef = ref<HTMLElement | null>(null)
const xtermMirror = ref<string[]>([])

const sessions = ref<Session[]>([])
const activeSessionId = ref('')

const activeSession = computed(() => sessions.value.find((session) => session.id === activeSessionId.value) ?? null)
const currentMessages = computed(() => activeSession.value?.messages ?? [])
const currentLastAil = computed(() => activeSession.value?.lastAil ?? '')
const currentAilModels = computed(() => activeSession.value?.ailModels ?? {})
const currentCompileResult = computed(() => activeSession.value?.compileResult ?? null)
const currentLastError = computed(() => activeSession.value?.lastError ?? null)
const currentStreamState = computed(() => activeSession.value?.streamState ?? 'disconnected')
const currentLogPaused = computed(() => activeSession.value?.logPaused ?? false)
const currentLogFilter = computed<'all' | 'errors'>({
  get() {
    return activeSession.value?.logFilter ?? 'all'
  },
  set(next) {
    const sid = activeSessionId.value
    if (!sid) return
    applySessionUpdateById(sid, (session) => {
      session.logFilter = next
    })
  },
})
const effectiveRunStatus = computed<RunStatus>(() => {
  return (
    activeSession.value?.runStatus ?? {
      running: false,
      pid: null,
      frontend_url: null,
      backend_url: null,
      detect_state: 'timeout',
      tail: [],
    }
  )
})
const lastStatusPollTs = computed<number | null>(() => activeSession.value?.lastStatusPollTs ?? null)

let term: Terminal | null = null
let fitAddon: FitAddon | null = null
let resizeHandler: (() => void) | null = null
let resizeFitTimer: number | null = null
let pasteHandler: ((event: ClipboardEvent) => void) | null = null
let xtermTextareaEl: HTMLTextAreaElement | null = null
let persistTimer: number | null = null
const sessionStreams = new Map<string, EventSource>()
const sessionStreamReconnectTimers = new Map<string, number>()
const sessionStreamReconnectAttempts = new Map<string, number>()
const sessionPollTimers = new Map<string, number>()
const sessionPollInFlight = new Set<string>()
const sessionPendingSince = new Map<string, number>()
const sessionHintShown = new Set<string>()
const ERROR_KEYWORDS = ['error', 'traceback', 'exception', 'failed', 'eaddrinuse', 'econnrefused']
const sessionGenerateControllers = new Map<string, AbortController>()
const sessionGenerateReplayTimers = new Map<string, number>()
const sessionGenerateTokens = new Map<string, number>()
const sessionGenerateDraftBuffers = new Map<string, string>()
const sessionGenerateDraftFlushTimers = new Map<string, number>()

function createId(): string {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID()
  }
  return `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`
}

function createWelcomeMessage(): ChatMessage {
  return {
    id: createId(),
    role: 'system',
    kind: 'status',
    text: 'AIL Studio ready. Enter your prompt to generate AIL.',
    ts: Date.now(),
  }
}

function createSession(name: string): Session {
  const now = Date.now()
  return {
    id: createId(),
    name,
    createdAt: now,
    updatedAt: now,
    messages: [createWelcomeMessage()],
    lastAil: '',
    ailModels: {},
    compileResult: null,
    runStatus: null,
    lastStatusPollTs: null,
    lastError: null,
    streamState: 'disconnected',
    streamError: null,
    streamLastEventTs: null,
    logPaused: false,
    logFilter: 'all',
    logDroppedCount: 0,
    logLastClearTs: null,
    generateDraft: '',
    generateStreaming: false,
    generateStreamError: null,
    generateStreamTs: null,
  }
}

function getNextSessionName(): string {
  let max = 0
  for (const session of sessions.value) {
    const match = /^Session\s+(\d+)$/i.exec(session.name.trim())
    if (!match) continue
    const num = Number(match[1])
    if (Number.isFinite(num) && num > max) {
      max = num
    }
  }
  return `Session ${max + 1}`
}

function getFallbackSession(): Session {
  const fresh = createSession('Session 1')
  sessions.value = [fresh]
  activeSessionId.value = fresh.id
  return fresh
}

function getActiveSessionOrCreate(): Session {
  return activeSession.value ?? getFallbackSession()
}

function touchSession(session: Session): void {
  session.updatedAt = Date.now()
}

function applySessionUpdate(mutator: (session: Session) => void): void {
  const session = getActiveSessionOrCreate()
  mutator(session)
  touchSession(session)
}

function getSessionById(sessionId: string): Session | null {
  return sessions.value.find((session) => session.id === sessionId) ?? null
}

function applySessionUpdateById(sessionId: string, mutator: (session: Session) => void): void {
  const target = getSessionById(sessionId) ?? getActiveSessionOrCreate()
  mutator(target)
  touchSession(target)
}

function setSessionError(sessionId: string, scope: 'generate' | 'compile' | 'run' | 'status' | 'stop', message: string): void {
  const next = `${scope}: ${message}`
  if (getSessionById(sessionId)?.lastError === next) return
  applySessionUpdateById(sessionId, (session) => {
    session.lastError = next
  })
}

function resetPendingHint(sessionId: string): void {
  sessionPendingSince.delete(sessionId)
  sessionHintShown.delete(sessionId)
}

function stopSessionPoller(sessionId: string): void {
  const timer = sessionPollTimers.get(sessionId)
  if (timer !== undefined) {
    window.clearTimeout(timer)
    sessionPollTimers.delete(sessionId)
  }
  resetPendingHint(sessionId)
}

function stopAllSessionPollers(): void {
  for (const sid of sessionPollTimers.keys()) {
    stopSessionPoller(sid)
  }
}

function isLocked(): boolean {
  return state.value === 'GENERATING' || state.value === 'COMPILING'
}

function maskedKey(value: string): string {
  if (!value) return ''
  if (value.length <= 8) return '****'
  return `${value.slice(0, 4)}****${value.slice(-4)}`
}

function nowStamp(): string {
  const d = new Date()
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  const ss = String(d.getSeconds()).padStart(2, '0')
  return `${hh}:${mm}:${ss}`
}

function normalizeLoopbackUrl(url: string): string {
  return url.replace('http://localhost', 'http://127.0.0.1').replace('https://localhost', 'https://127.0.0.1')
}

function normalizeUrlForCompare(url: string): string {
  return normalizeLoopbackUrl(url).replace(/\/+$/, '')
}

function isStudioPreviewUrl(url: string): boolean {
  if (!url.trim()) return false
  try {
    const normalized = normalizeUrlForCompare(new URL(url, window.location.origin).toString())
    return normalized === normalizeUrlForCompare(window.location.origin)
  } catch {
    return false
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => window.setTimeout(resolve, ms))
}

function formatLocalTime(ts: number): string {
  return new Date(ts).toLocaleString()
}

function formatTime(ts: number | null): string {
  if (!ts) return '-'
  const d = new Date(ts)
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  const ss = String(d.getSeconds()).padStart(2, '0')
  return `${hh}:${mm}:${ss}`
}

function getProjectRootForSession(sessionId: string): string {
  return getSessionById(sessionId)?.compileResult?.projectRoot?.trim() ?? ''
}

function appendToTerminal(line: string): void {
  if (xtermMirror.value.length >= 200) {
    xtermMirror.value.splice(0, xtermMirror.value.length - 199)
  }
  xtermMirror.value.push(line)
  if (!term) return
  term.writeln(line)
}

function isErrorLine(line: string): boolean {
  const lower = line.toLowerCase()
  if (lower.includes('[ui]')) {
    return lower.includes(' error') || lower.includes(' failed')
  }
  return ERROR_KEYWORDS.some((keyword) => lower.includes(keyword))
}

function writeSessionLog(
  sessionId: string,
  line: string,
  options?: { bypassFilter?: boolean },
): void {
  const session = getSessionById(sessionId)
  if (!session) return
  if (session.logPaused) {
    session.logDroppedCount += 1
    return
  }
  if (sessionId !== activeSessionId.value) {
    return
  }
  if (!options?.bypassFilter && session.logFilter === 'errors' && !isErrorLine(line)) {
    return
  }
  appendToTerminal(line)
}

function pushMessage(payload: Omit<ChatMessage, 'id' | 'ts'>, sessionId?: string): string {
  const id = createId()
  const sid = sessionId ?? activeSessionId.value
  const writer = sid ? applySessionUpdateById.bind(null, sid) : applySessionUpdate
  writer((session) => {
    session.messages.push({
      ...payload,
      id,
      ts: Date.now(),
    })
  })
  void nextTick(() => {
    if (chatListRef.value) {
      chatListRef.value.scrollTop = chatListRef.value.scrollHeight
    }
  })
  return id
}

function termWrite(message: string, sessionId = activeSessionId.value, options?: { bypassFilter?: boolean }): void {
  const line = `[${nowStamp()}] ${message}`
  writeSessionLog(sessionId, line, options)
}

function termWriteRaw(message: string, sessionId = activeSessionId.value): void {
  writeSessionLog(sessionId, message)
}

function clearGenerateReplayTimer(sessionId: string): void {
  const timer = sessionGenerateReplayTimers.get(sessionId)
  if (timer !== undefined) {
    window.clearTimeout(timer)
    sessionGenerateReplayTimers.delete(sessionId)
  }
}

function flushGenerateDraftNow(sessionId: string): void {
  const pending = sessionGenerateDraftBuffers.get(sessionId)
  if (!pending) return
  sessionGenerateDraftBuffers.delete(sessionId)
  applySessionUpdateById(sessionId, (session) => {
    session.generateDraft += pending
    session.generateStreamTs = Date.now()
  })
}

function clearGenerateDraftFlushTimer(sessionId: string): void {
  const timer = sessionGenerateDraftFlushTimers.get(sessionId)
  if (timer !== undefined) {
    window.clearTimeout(timer)
    sessionGenerateDraftFlushTimers.delete(sessionId)
  }
}

function scheduleGenerateDraftFlush(sessionId: string): void {
  if (sessionGenerateDraftFlushTimers.has(sessionId)) return
  const timer = window.setTimeout(() => {
    sessionGenerateDraftFlushTimers.delete(sessionId)
    flushGenerateDraftNow(sessionId)
  }, 80)
  sessionGenerateDraftFlushTimers.set(sessionId, timer)
}

function nextGenerateToken(sessionId: string): number {
  const next = (sessionGenerateTokens.get(sessionId) ?? 0) + 1
  sessionGenerateTokens.set(sessionId, next)
  return next
}

function isGenerateTokenActive(sessionId: string, token: number): boolean {
  return sessionGenerateTokens.get(sessionId) === token
}

function cancelSessionGenerate(sessionId: string, bumpToken = true): void {
  clearGenerateReplayTimer(sessionId)
  clearGenerateDraftFlushTimer(sessionId)
  sessionGenerateDraftBuffers.delete(sessionId)
  const controller = sessionGenerateControllers.get(sessionId)
  if (controller) {
    controller.abort()
    sessionGenerateControllers.delete(sessionId)
  }
  setGenerateState(sessionId, {
    generateStreaming: false,
    generateStreamTs: Date.now(),
  })
  if (bumpToken) {
    nextGenerateToken(sessionId)
  }
}

function cancelAllGenerateOperations(): void {
  for (const sid of new Set([...sessionGenerateControllers.keys(), ...sessionGenerateReplayTimers.keys()])) {
    cancelSessionGenerate(sid)
  }
}

function appendGenerateDraft(sessionId: string, chunk: string): void {
  if (!chunk) return
  const prev = sessionGenerateDraftBuffers.get(sessionId) ?? ''
  sessionGenerateDraftBuffers.set(sessionId, `${prev}${chunk}`)
  scheduleGenerateDraftFlush(sessionId)
}

function setGenerateState(
  sessionId: string,
  patch: Partial<Pick<Session, 'generateDraft' | 'generateStreaming' | 'generateStreamError' | 'generateStreamTs'>>,
): void {
  applySessionUpdateById(sessionId, (session) => {
    if (typeof patch.generateDraft === 'string') {
      session.generateDraft = patch.generateDraft
    }
    if (typeof patch.generateStreaming === 'boolean') {
      session.generateStreaming = patch.generateStreaming
    }
    if (patch.generateStreamError !== undefined) {
      session.generateStreamError = patch.generateStreamError
    }
    if (patch.generateStreamTs !== undefined) {
      session.generateStreamTs = patch.generateStreamTs
    }
  })
}

async function replayGenerateDraft(sessionId: string, token: number, content: string): Promise<boolean> {
  let cursor = 0
  while (cursor < content.length) {
    if (!isGenerateTokenActive(sessionId, token)) return false
    const step = Math.min(content.length - cursor, Math.floor(Math.random() * 41) + 20)
    const chunk = content.slice(cursor, cursor + step)
    appendGenerateDraft(sessionId, chunk)
    cursor += step
    await new Promise<void>((resolve) => {
      const timer = window.setTimeout(() => {
        sessionGenerateReplayTimers.delete(sessionId)
        resolve()
      }, 15)
      sessionGenerateReplayTimers.set(sessionId, timer)
    })
  }
  clearGenerateReplayTimer(sessionId)
  flushGenerateDraftNow(sessionId)
  return true
}

function parseSseDataBlock(block: string): string | null {
  const dataParts: string[] = []
  const lines = block.split('\n')
  for (const rawLine of lines) {
    const line = rawLine.endsWith('\r') ? rawLine.slice(0, -1) : rawLine
    if (!line.startsWith('data:')) continue
    let data = line.slice(5)
    if (data.startsWith(' ')) data = data.slice(1)
    dataParts.push(data)
  }
  if (dataParts.length === 0) return null
  return dataParts.join('\n')
}

function clearStreamReconnectTimer(sessionId: string): void {
  const timer = sessionStreamReconnectTimers.get(sessionId)
  if (timer !== undefined) {
    window.clearTimeout(timer)
    sessionStreamReconnectTimers.delete(sessionId)
  }
}

function closeSessionStream(sessionId: string, nextState: 'disconnected' | 'ended' = 'disconnected'): void {
  clearStreamReconnectTimer(sessionId)
  sessionStreamReconnectAttempts.delete(sessionId)

  const source = sessionStreams.get(sessionId)
  if (source) {
    source.close()
    sessionStreams.delete(sessionId)
  }

  if (!getSessionById(sessionId)) return
  applySessionUpdateById(sessionId, (session) => {
    session.streamState = nextState
    if (nextState === 'ended') {
      session.streamError = null
      session.streamLastEventTs = Date.now()
    } else if (nextState === 'disconnected' && !session.runStatus?.running) {
      session.streamError = null
    }
  })
}

function closeAllSessionStreams(): void {
  for (const sid of sessionStreams.keys()) {
    closeSessionStream(sid, 'disconnected')
  }
}

function scheduleStreamReconnect(sessionId: string, projectRoot: string): void {
  const session = getSessionById(sessionId)
  if (!session || !session.runStatus?.running || session.streamState === 'ended') {
    return
  }
  clearStreamReconnectTimer(sessionId)

  const attempt = (sessionStreamReconnectAttempts.get(sessionId) ?? 0) + 1
  sessionStreamReconnectAttempts.set(sessionId, attempt)
  const delay = attempt <= 1 ? 1000 : attempt === 2 ? 2000 : 5000

  if (sessionId === activeSessionId.value) {
    termWrite(`[ui] stream reconnecting... attempt=${attempt}`, sessionId)
  }

  const timer = window.setTimeout(() => {
    sessionStreamReconnectTimers.delete(sessionId)
    connectSessionStream(sessionId, projectRoot)
  }, delay)
  sessionStreamReconnectTimers.set(sessionId, timer)
}

function connectSessionStream(sessionId: string, projectRoot: string): void {
  const session = getSessionById(sessionId)
  const root = projectRoot.trim()
  if (!session || !root || !session.runStatus?.running) return

  const existing = sessionStreams.get(sessionId)
  if (existing) {
    existing.close()
    sessionStreams.delete(sessionId)
  }
  clearStreamReconnectTimer(sessionId)

  applySessionUpdateById(sessionId, (current) => {
    current.streamState = 'connecting'
    current.streamError = null
  })

  const url = `${RUN_PROXY_BASE}/stream?project_root=${encodeURIComponent(root)}`
  const source = new EventSource(url)
  sessionStreams.set(sessionId, source)

  source.onopen = () => {
    if (sessionStreams.get(sessionId) !== source) return
    sessionStreamReconnectAttempts.set(sessionId, 0)
    applySessionUpdateById(sessionId, (current) => {
      current.streamState = 'connected'
      current.streamError = null
      current.streamLastEventTs = Date.now()
    })
    if (sessionId === activeSessionId.value) {
      termWrite('[ui] stream connected', sessionId)
    }
  }

  source.onmessage = (event: MessageEvent<string>) => {
    if (sessionStreams.get(sessionId) !== source || !event.data) return
    applySessionUpdateById(sessionId, (current) => {
      current.streamLastEventTs = Date.now()
    })
    if (sessionId === activeSessionId.value) {
      termWriteRaw(event.data, sessionId)
    }
  }

  source.addEventListener('end', () => {
    if (sessionStreams.get(sessionId) !== source) return
    closeSessionStream(sessionId, 'ended')
    if (sessionId === activeSessionId.value) {
      termWrite('[ui] stream ended', sessionId)
    }
  })

  source.onerror = () => {
    if (sessionStreams.get(sessionId) !== source) return
    source.close()
    sessionStreams.delete(sessionId)
    applySessionUpdateById(sessionId, (current) => {
      current.streamState = 'disconnected'
      current.streamError = 'stream disconnected'
    })
    if (sessionId === activeSessionId.value) {
      termWrite('[ui] stream disconnected', sessionId)
    }
    scheduleStreamReconnect(sessionId, root)
  }
}

function initXterm(): void {
  if (!xtermContainerRef.value) return
  term = new Terminal({
    convertEol: true,
    cursorBlink: false,
    disableStdin: true,
    fontFamily: 'Menlo, Monaco, Consolas, monospace',
    fontSize: 12,
    theme: {
      background: '#000000',
      foreground: '#22c55e',
    },
  })
  fitAddon = new FitAddon()
  term.loadAddon(fitAddon)
  term.open(xtermContainerRef.value)
  fitAddon.fit()
  pasteHandler = (event: ClipboardEvent) => {
    event.preventDefault()
  }
  xtermTextareaEl = xtermContainerRef.value.querySelector('textarea')
  if (xtermTextareaEl) {
    xtermTextareaEl.addEventListener('paste', pasteHandler)
  }
  termWrite('[ui] terminal ready')
  resizeHandler = () => {
    if (resizeFitTimer !== null) {
      window.clearTimeout(resizeFitTimer)
    }
    resizeFitTimer = window.setTimeout(() => fitAddon?.fit(), 200)
  }
  window.addEventListener('resize', resizeHandler)
}

function disposeXterm(): void {
  if (resizeHandler) {
    window.removeEventListener('resize', resizeHandler)
    resizeHandler = null
  }
  if (term) {
    term.dispose()
    term = null
  }
  if (resizeFitTimer !== null) {
    window.clearTimeout(resizeFitTimer)
    resizeFitTimer = null
  }
  if (xtermTextareaEl && pasteHandler) {
    xtermTextareaEl.removeEventListener('paste', pasteHandler)
    pasteHandler = null
  }
  xtermTextareaEl = null
  fitAddon = null
}

async function copyText(value: string, successLog = '[ui] copied to clipboard'): Promise<boolean> {
  if (!value) return false
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(value)
      termWrite(successLog)
      return true
    }
  } catch {
    // fallback below
  }

  try {
    const ta = document.createElement('textarea')
    ta.value = value
    ta.setAttribute('readonly', 'true')
    ta.style.position = 'absolute'
    ta.style.left = '-9999px'
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
    termWrite(successLog)
    return true
  } catch {
    return false
  }
}

function buildReproReport(): string {
  const session = getActiveSessionOrCreate()
  const latestPrompt = [...session.messages].reverse().find((msg) => msg.kind === 'prompt')?.text ?? ''
  const latestAilMessage = [...session.messages].reverse().find((msg) => msg.kind === 'ail')
  const usedModel = latestAilMessage ? session.ailModels[latestAilMessage.id] || model.value : model.value

  const backendPaths = session.compileResult?.backendPaths ?? []
  const hasRbac = typeof session.compileResult?.hasRbac === 'boolean' ? session.compileResult.hasRbac : null
  const hasOrRoles = typeof session.compileResult?.hasOrRoles === 'boolean' ? session.compileResult.hasOrRoles : null

  return [
    '# AIL Studio Repro Report',
    '',
    `- Session ID: ${session.id}`,
    `- Session Name: ${session.name}`,
    `- Updated At: ${formatLocalTime(session.updatedAt)}`,
    `- LLM Model: ${usedModel}`,
    '',
    '## Last Prompt',
    latestPrompt || '(empty)',
    '',
    '## Last AIL',
    '```',
    session.lastAil || '(empty)',
    '```',
    '',
    '## Compile Result',
    `- system: ${session.compileResult?.system ?? ''}`,
    `- project_root: ${session.compileResult?.projectRoot ?? ''}`,
    `- backend_paths: ${backendPaths.length > 0 ? backendPaths.join(', ') : ''}`,
    `- has_rbac: ${hasRbac === null ? '' : String(hasRbac)}`,
    `- has_or_roles: ${hasOrRoles === null ? '' : String(hasOrRoles)}`,
    '',
    '## Preview',
    `- preview_url: ${previewUrl.value}`,
  ].join('\n')
}

async function handleCopyReproReport(): Promise<void> {
  const report = buildReproReport()
  const copied = await copyText(report, '[ui] copied repro report')
  if (copied) {
    pushMessage({
      role: 'system',
      kind: 'status',
      text: 'Repro report copied.',
    })
  }
}

async function handleGenerate(): Promise<void> {
  const sid = activeSessionId.value
  const prompt = promptInput.value.trim()
  if (!prompt || isLocked()) return

  cancelSessionGenerate(sid, false)
  const token = nextGenerateToken(sid)
  const controller = new AbortController()
  sessionGenerateControllers.set(sid, controller)
  const isActive = () => isGenerateTokenActive(sid, token)

  pushMessage({
    role: 'user',
    kind: 'prompt',
    text: prompt,
  }, sid)

  promptInput.value = ''
  state.value = 'GENERATING'
  termWrite('[ui] generating...', sid)
  setGenerateState(sid, {
    generateDraft: '',
    generateStreaming: true,
    generateStreamError: null,
    generateStreamTs: Date.now(),
  })

  try {
    const response = await fetch(GENERATE_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt,
        api_key: apiKey.value,
        model: model.value,
        project_name: projectName.value,
      }),
      signal: controller.signal,
    })
    if (!isActive()) return
    const contentType = response.headers.get('content-type')?.toLowerCase() ?? ''
    const isStreamResponse =
      !!response.body &&
      (contentType.includes('text/event-stream') || contentType.includes('text/plain'))

    if (isStreamResponse && response.body) {
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      const isSse = contentType.includes('text/event-stream')
      let sseBuffer = ''
      let lastLogAt = Date.now()
      let reachedDone = false
      while (true) {
        if (!isActive()) return
        const { done, value } = await reader.read()
        if (done) break
        const chunkText = decoder.decode(value, { stream: true })
        if (!chunkText) continue
        if (isSse) {
          sseBuffer += chunkText.replace(/\r\n/g, '\n')
          while (true) {
            const boundary = sseBuffer.indexOf('\n\n')
            if (boundary === -1) break
            const block = sseBuffer.slice(0, boundary)
            sseBuffer = sseBuffer.slice(boundary + 2)
            const dataPart = parseSseDataBlock(block)
            if (!dataPart) continue
            if (dataPart === '[DONE]') {
              reachedDone = true
              break
            }
            appendGenerateDraft(sid, `${dataPart}\n`)
          }
          if (reachedDone) break
        } else {
          appendGenerateDraft(sid, chunkText)
        }
        const now = Date.now()
        if (now - lastLogAt >= 800) {
          termWrite('[ui] generate_ail streaming...', sid)
          lastLogAt = now
        }
      }
      if (isSse && sseBuffer.trim()) {
        const trailing = parseSseDataBlock(sseBuffer)
        if (trailing && trailing !== '[DONE]' && isActive()) {
          appendGenerateDraft(sid, `${trailing}\n`)
        }
      }
      flushGenerateDraftNow(sid)
      if (!isActive()) return
      const streamedAil = (getSessionById(sid)?.generateDraft ?? '').trim()
      if (!response.ok || !streamedAil) {
        const streamError = `generate_ail stream failed with status ${response.status}`
        setSessionError(sid, 'generate', streamError)
        setGenerateState(sid, {
          generateStreaming: false,
          generateStreamError: streamError,
          generateStreamTs: Date.now(),
        })
        pushMessage(
          {
            role: 'assistant',
            kind: 'error',
            text: streamError,
          },
          sid,
        )
        termWrite(`[ui] generate_ail stream error ${streamError}`, sid)
        return
      }
      const usedModel = model.value
      const ailLines = streamedAil.split('\n').filter((line) => line.trim()).length
      const msgId = createId()
      const msgTs = Date.now()
      applySessionUpdateById(sid, (session) => {
        session.lastAil = streamedAil
        session.compileResult = null
        session.lastError = null
        session.generateStreaming = false
        session.generateStreamError = null
        session.generateStreamTs = Date.now()
        session.messages.push({
          id: msgId,
          role: 'assistant',
          kind: 'ail',
          text: streamedAil,
          ts: msgTs,
        })
        session.ailModels[msgId] = usedModel
      })
      void nextTick(() => {
        if (chatListRef.value) {
          chatListRef.value.scrollTop = chatListRef.value.scrollHeight
        }
      })
      termWrite(`[ui] generate_ail ok lines=${ailLines} model=${usedModel}`, sid)
      return
    }

    const data = await response.json().catch(() => ({}))
    if (!isActive()) return
    const ok =
      response.status === 200 &&
      data?.status === 'ok' &&
      typeof data?.ail === 'string' &&
      data.ail.trim().length > 0

    if (!ok) {
      const errorText = data?.error || `generate_ail failed with status ${response.status}`
      setSessionError(sid, 'generate', String(errorText))
      setGenerateState(sid, {
        generateStreaming: false,
        generateStreamError: String(errorText),
        generateStreamTs: Date.now(),
      })
      pushMessage(
        {
          role: 'assistant',
          kind: 'error',
          text: String(errorText),
        },
        sid,
      )
      termWrite(`[ui] generate_ail error ${String(errorText)}`, sid)
      return
    }

    const ailText = String(data.ail)
    const replayed = await replayGenerateDraft(sid, token, ailText)
    if (!replayed || !isActive()) return
    const ailLines = ailText.split('\n').filter((line) => line.trim()).length
    const usedModel = typeof data?.model === 'string' && data.model ? data.model : model.value
    const msgId = createId()
    const msgTs = Date.now()
    applySessionUpdateById(sid, (session) => {
      session.lastAil = ailText
      session.compileResult = null
      session.lastError = null
      session.generateStreaming = false
      session.generateStreamError = null
      session.generateStreamTs = Date.now()
      session.messages.push({
        id: msgId,
        role: 'assistant',
        kind: 'ail',
        text: ailText,
        ts: msgTs,
      })
      session.ailModels[msgId] = usedModel
    })
    void nextTick(() => {
      if (chatListRef.value) {
        chatListRef.value.scrollTop = chatListRef.value.scrollHeight
      }
    })
    termWrite(`[ui] generate_ail ok lines=${ailLines} model=${usedModel}`, sid)
  } catch (error) {
    if (!isActive()) return
    if (error instanceof DOMException && error.name === 'AbortError') {
      return
    }
    const text = error instanceof Error ? error.message : 'Unexpected network error'
    setSessionError(sid, 'generate', text)
    setGenerateState(sid, {
      generateStreaming: false,
      generateStreamError: text,
      generateStreamTs: Date.now(),
    })
    pushMessage(
      {
        role: 'assistant',
        kind: 'error',
        text,
      },
      sid,
    )
    termWrite(`[ui] generate_ail stream error ${text}`, sid)
  } finally {
    const currentController = sessionGenerateControllers.get(sid)
    if (currentController === controller) {
      clearGenerateReplayTimer(sid)
      clearGenerateDraftFlushTimer(sid)
      flushGenerateDraftNow(sid)
      sessionGenerateControllers.delete(sid)
      setGenerateState(sid, {
        generateStreaming: false,
        generateStreamTs: Date.now(),
      })
      state.value = 'IDLE'
    }
  }
}

async function handleCompile(): Promise<void> {
  const sid = activeSessionId.value
  const sourceSession = getSessionById(sid)
  const compileAil = sourceSession?.lastAil ?? currentLastAil.value
  const ailText = compileAil.trim()
  if (!ailText || isLocked()) return

  state.value = 'COMPILING'
  termWrite('[ui] compiling...', sid)

  try {
    const response = await fetch(COMPILE_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ail: compileAil,
        ail_code: compileAil,
        project_name: projectName.value,
      }),
    })

    const data = await response.json().catch(() => ({}))
    const ok =
      response.status === 200 &&
      data?.status === 'ok' &&
      typeof data?.project_root === 'string' &&
      data.project_root.trim().length > 0

    if (!ok) {
      const errorText = data?.error || `compile failed with status ${response.status}`
      setSessionError(sid, 'compile', String(errorText))
      pushMessage({
        role: 'assistant',
        kind: 'error',
        text: String(errorText),
      }, sid)
      termWrite(`[ui] compile error ${String(errorText)}`, sid)
      return
    }

    const systemName = data?.build_report?.system || 'UnknownSystem'
    const projectRoot = data.project_root
    const backendPaths = Array.isArray(data?.summary?.backend_paths) ? data.summary.backend_paths : []
    closeSessionStream(sid, 'disconnected')
    applySessionUpdateById(sid, (session) => {
      session.compileResult = {
        system: String(systemName),
        projectRoot: String(projectRoot),
        backendPaths,
        hasRbac: typeof data?.summary?.has_rbac === 'boolean' ? data.summary.has_rbac : undefined,
        hasOrRoles: typeof data?.summary?.has_or_roles === 'boolean' ? data.summary.has_or_roles : undefined,
      }
      session.runStatus = {
        running: false,
        pid: null,
        frontend_url: null,
        backend_url: null,
        detect_state: 'pending',
        tail: [],
      }
      session.lastStatusPollTs = null
      session.lastError = null
      session.streamState = 'disconnected'
      session.streamError = null
      session.streamLastEventTs = null
      session.messages.push({
        id: createId(),
        role: 'system',
        kind: 'status',
        text: `Compile OK: system=${systemName} project_root=${projectRoot}`,
        ts: Date.now(),
      })
    })
    void nextTick(() => {
      if (chatListRef.value) {
        chatListRef.value.scrollTop = chatListRef.value.scrollHeight
      }
    })

    termWrite('[ui] compile ok', sid)
    termWrite(`status=${String(data?.status ?? '')}`, sid)
    termWrite(`system=${String(systemName)}`, sid)
    termWrite(`project_root=${String(projectRoot)}`, sid)
    if (backendPaths.length > 0) {
      termWrite(`backend_paths=${backendPaths.join(',')}`, sid)
    }
    if (typeof data?.summary?.has_rbac === 'boolean') {
      termWrite(`summary.has_rbac=${String(data.summary.has_rbac)}`, sid)
    }
    if (typeof data?.summary?.has_or_roles === 'boolean') {
      termWrite(`summary.has_or_roles=${String(data.summary.has_or_roles)}`, sid)
    }

    previewUrl.value = SAFE_EMPTY_PREVIEW_URL
    iframeKey.value = Date.now()
    void pollDetectAfterCompile(sid, projectRoot)
  } catch (error) {
    const text = error instanceof Error ? error.message : 'Unexpected network error'
    setSessionError(sid, 'compile', text)
    pushMessage({
      role: 'assistant',
      kind: 'error',
      text,
    }, sid)
    termWrite(`[ui] compile error ${text}`, sid)
  } finally {
    state.value = 'IDLE'
  }
}

async function requestRunStatus(
  projectRoot: string,
): Promise<{ status: RunStatus | null; error: string | null }> {
  try {
    const response = await fetch(`${STATUS_URL}?project_root=${encodeURIComponent(projectRoot)}`)
    const data = await response.json().catch(() => ({}))
    if (response.status !== 200) {
      return {
        status: null,
        error: `status http ${response.status}`,
      }
    }
    return {
      status: {
        running: Boolean(data?.running),
        pid: typeof data?.pid === 'number' ? data.pid : null,
        frontend_url:
          typeof data?.frontend_url === 'string' && data.frontend_url.trim()
            ? normalizeLoopbackUrl(data.frontend_url.trim())
            : null,
        backend_url:
          typeof data?.backend_url === 'string' && data.backend_url.trim()
            ? normalizeLoopbackUrl(data.backend_url.trim())
            : null,
        detect_state:
          data?.detect_state === 'found' || data?.detect_state === 'pending' || data?.detect_state === 'timeout'
            ? data.detect_state
            : 'timeout',
        tail: Array.isArray(data?.tail) ? data.tail.filter((line: unknown): line is string => typeof line === 'string') : [],
      },
      error: null,
    }
  } catch (error) {
    return {
      status: null,
      error: error instanceof Error ? error.message : 'status request failed',
    }
  }
}

async function refreshRunStatus(sessionId: string, projectRoot: string, logDetect: boolean): Promise<RunStatus | null> {
  const { status, error } = await requestRunStatus(projectRoot)
  if (!status) {
    setSessionError(sessionId, 'status', error ?? 'failed to fetch /proxy/status')
    return null
  }
  applySessionUpdateById(sessionId, (session) => {
    session.runStatus = status
    session.lastStatusPollTs = Date.now()
  })
  applyRunStatus(sessionId, status, logDetect)
  return status
}

function handlePendingDetectHint(sessionId: string, status: RunStatus): void {
  if (!status.running || status.detect_state === 'found') {
    resetPendingHint(sessionId)
    return
  }
  const now = Date.now()
  const pendingSince = sessionPendingSince.get(sessionId) ?? now
  sessionPendingSince.set(sessionId, pendingSince)
  if (now - pendingSince >= 30_000 && !sessionHintShown.has(sessionId)) {
    sessionHintShown.add(sessionId)
    termWrite('[ui] hint: detect pending >30s. Try clicking Detect, or check start.sh output in logs.', sessionId)
  }
}

function scheduleSessionPoll(sessionId: string, delayMs: number): void {
  const existing = sessionPollTimers.get(sessionId)
  if (existing !== undefined) {
    window.clearTimeout(existing)
  }
  const timer = window.setTimeout(() => {
    sessionPollTimers.delete(sessionId)
    void runSessionPollTick(sessionId)
  }, Math.max(delayMs, 0))
  sessionPollTimers.set(sessionId, timer)
}

function startSessionPoller(sessionId: string, delayMs = 0): void {
  const session = getSessionById(sessionId)
  const root = session?.compileResult?.projectRoot?.trim() ?? ''
  if (!session || !root || !session.runStatus?.running) {
    stopSessionPoller(sessionId)
    return
  }
  scheduleSessionPoll(sessionId, delayMs)
}

async function runSessionPollTick(sessionId: string): Promise<void> {
  if (sessionPollInFlight.has(sessionId)) return
  const session = getSessionById(sessionId)
  const root = session?.compileResult?.projectRoot?.trim() ?? ''
  if (!session || !root || !session.runStatus?.running) {
    stopSessionPoller(sessionId)
    return
  }

  sessionPollInFlight.add(sessionId)
  try {
    const status = await refreshRunStatus(sessionId, root, false)
    if (!status) {
      scheduleSessionPoll(sessionId, 1000)
      return
    }
    handlePendingDetectHint(sessionId, status)
    if (!status.running) {
      stopSessionPoller(sessionId)
      return
    }
    scheduleSessionPoll(sessionId, status.detect_state === 'found' ? 5000 : 1000)
  } finally {
    sessionPollInFlight.delete(sessionId)
  }
}

function applyRunStatus(sessionId: string, status: RunStatus, logDetect: boolean): void {
  if (status.frontend_url) {
    previewUrl.value = status.frontend_url
    iframeKey.value = Date.now()
    if (logDetect) {
      termWrite(
        `[ui] detected frontend_url=${status.frontend_url} backend_url=${status.backend_url ?? ''}`,
        sessionId,
      )
    }
  }
}

async function pollDetectAfterCompile(sessionId: string, projectRoot: string): Promise<void> {
  const root = projectRoot.trim()
  if (!root) return

  // Keep initial compile state as pending briefly before first proxy poll.
  await sleep(1000)

  for (let i = 0; i < 30; i += 1) {
    const status = await refreshRunStatus(sessionId, root, false)
    if (status) {
      const foundFrontend = Boolean(status.frontend_url)
      if (foundFrontend) {
        applyRunStatus(sessionId, status, true)
      }
      if (foundFrontend) return
    }
    await sleep(1000)
  }
  termWrite('[ui] detect timeout', sessionId)
}

async function handleDetect(): Promise<void> {
  if (isLocked()) return
  const sid = activeSessionId.value
  const root = getProjectRootForSession(sid)
  if (!root) return
  const status = await refreshRunStatus(sid, root, false)
  if (!status) {
    setSessionError(sid, 'status', 'failed to fetch /proxy/status')
    termWrite('[ui] detect failed', sid)
    return
  }
  if (status.frontend_url) {
    applyRunStatus(sid, status, true)
  }
  if (!status.frontend_url) {
    termWrite(`[ui] detect state=${status.detect_state}`, sid)
  }
  if (status.running) {
    startSessionPoller(sid, 1000)
  }
}

async function handleRun(): Promise<void> {
  if (isLocked()) return
  const sid = activeSessionId.value
  const root = getProjectRootForSession(sid)
  if (!root) return
  termWrite('[ui] run starting...', sid)
  try {
    const response = await fetch(RUN_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        project_root: root,
      }),
    })
    const data = await response.json().catch(() => ({}))
    const ok = response.status === 200 && data?.status === 'ok'
    if (!ok) {
      setSessionError(sid, 'run', String(data?.error || response.status))
      termWrite(`[ui] run error ${String(data?.error || response.status)}`, sid)
      return
    }
    const pid = typeof data?.pid === 'number' ? data.pid : null
    termWrite(`[ui] run pid=${pid ?? ''}`, sid)
    const status = await refreshRunStatus(sid, root, false)
    if (!status) {
      applySessionUpdateById(sid, (session) => {
        session.runStatus = {
          running: true,
          pid,
          frontend_url: session.runStatus?.frontend_url ?? null,
          backend_url: session.runStatus?.backend_url ?? null,
          detect_state: 'pending',
          tail: [],
        }
      })
    }
    startSessionPoller(sid, 1000)
    connectSessionStream(sid, root)
  } catch (error) {
    const text = error instanceof Error ? error.message : 'Unexpected run error'
    setSessionError(sid, 'run', text)
    termWrite(`[ui] run error ${text}`, sid)
  }
}

async function handleStop(): Promise<void> {
  if (isLocked()) return
  const sid = activeSessionId.value
  const root = getProjectRootForSession(sid)
  if (!root) return
  closeSessionStream(sid, 'disconnected')
  try {
    const response = await fetch(STOP_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        project_root: root,
      }),
    })
    const data = await response.json().catch(() => ({}))
    const ok = response.status === 200 && data?.status === 'ok'
    if (!ok) {
      setSessionError(sid, 'stop', String(data?.error || response.status))
      termWrite(`[ui] stop error ${String(data?.error || response.status)}`, sid)
      return
    }
    const latest = await refreshRunStatus(sid, root, false)
    if (!latest) {
      applySessionUpdateById(sid, (session) => {
        session.runStatus = {
          running: false,
          pid: null,
          frontend_url: session.runStatus?.frontend_url ?? null,
          backend_url: session.runStatus?.backend_url ?? null,
          detect_state: 'timeout',
          tail: [],
        }
        session.lastStatusPollTs = Date.now()
      })
      stopSessionPoller(sid)
    } else if (!latest.running) {
      resetPendingHint(sid)
      stopSessionPoller(sid)
    } else {
      startSessionPoller(sid, 1000)
    }
    termWrite('[ui] stop ok', sid)
  } catch (error) {
    const text = error instanceof Error ? error.message : 'Unexpected stop error'
    setSessionError(sid, 'stop', text)
    termWrite(`[ui] stop error ${text}`, sid)
  }
}

async function handleStopAll(): Promise<void> {
  if (isLocked()) return
  const sid = activeSessionId.value
  try {
    const response = await fetch(STOP_ALL_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    const data = await response.json().catch(() => ({}))
    const ok = response.status === 200 && data?.status === 'ok'
    if (!ok) {
      const text = String(data?.error || response.status)
      setSessionError(sid, 'stop', `stop_all: ${text}`)
      termWrite(`[ui] stop_all error ${text}`, sid)
      return
    }

    closeAllSessionStreams()
    stopAllSessionPollers()

    const now = Date.now()
    sessions.value = sessions.value.map((session) => ({
      ...session,
      runStatus: session.runStatus
        ? {
            ...session.runStatus,
            running: false,
            pid: null,
            detect_state: 'timeout',
          }
        : session.runStatus,
      lastStatusPollTs: now,
      streamState: 'disconnected',
      streamError: null,
    }))

    const stopped = typeof data?.stopped === 'number' ? data.stopped : 0
    termWrite(`[ui] stop_all ok stopped=${stopped}`, sid)
    const root = getProjectRootForSession(sid)
    if (root) {
      await refreshRunStatus(sid, root, false)
    }
  } catch (error) {
    const text = error instanceof Error ? error.message : 'Unexpected stop_all error'
    setSessionError(sid, 'stop', `stop_all: ${text}`)
    termWrite(`[ui] stop_all error ${text}`, sid)
  }
}

function handleResetPreview(): void {
  localStorage.removeItem(PREVIEW_STORAGE)
  previewUrl.value = SAFE_EMPTY_PREVIEW_URL
  iframeKey.value = Date.now()
  termWrite('[ui] preview reset')
}

function handleLogPauseToggle(): void {
  const sid = activeSessionId.value
  const session = getSessionById(sid)
  if (!sid || !session) return

  if (session.logPaused) {
    const dropped = session.logDroppedCount
    applySessionUpdateById(sid, (current) => {
      current.logPaused = false
      current.logDroppedCount = 0
    })
    termWrite(`[ui] resumed, dropped=${dropped}`, sid, { bypassFilter: true })
    return
  }

  applySessionUpdateById(sid, (current) => {
    current.logPaused = true
  })
}

function handleLogClear(): void {
  const sid = activeSessionId.value
  if (!sid || !getSessionById(sid)) return

  xtermMirror.value = []
  if (term) {
    term.clear()
    term.reset()
  }
  applySessionUpdateById(sid, (session) => {
    session.logLastClearTs = Date.now()
  })
  termWrite('[ui] log cleared', sid, { bypassFilter: true })
}

function reloadPreview(): void {
  if (isLocked()) return
  iframeKey.value = Date.now()
  termWrite('[ui] preview reloaded')
}

function onPromptKeydown(event: KeyboardEvent): void {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    void handleGenerate()
  }
}

function loadSettingsFromStorage(): void {
  const savedApiKey = localStorage.getItem(API_KEY_STORAGE)
  const savedModel = localStorage.getItem(MODEL_STORAGE)
  const savedProject = localStorage.getItem(PROJECT_STORAGE)
  const savedPreviewUrl = localStorage.getItem(PREVIEW_STORAGE)

  if (savedApiKey !== null) apiKey.value = savedApiKey
  if (savedModel !== null && savedModel.trim()) model.value = savedModel
  if (savedProject !== null && savedProject.trim()) projectName.value = savedProject
  if (savedPreviewUrl !== null && savedPreviewUrl.trim()) previewUrl.value = savedPreviewUrl
}

function sanitizeSession(input: unknown): Session | null {
  if (!input || typeof input !== 'object') return null
  const src = input as Record<string, unknown>
  const id = typeof src.id === 'string' && src.id ? src.id : createId()
  const name = typeof src.name === 'string' && src.name.trim() ? src.name.trim() : 'Session'
  const createdAt = typeof src.createdAt === 'number' && Number.isFinite(src.createdAt) ? src.createdAt : Date.now()
  const updatedAt = typeof src.updatedAt === 'number' && Number.isFinite(src.updatedAt) ? src.updatedAt : createdAt

  const msgArr = Array.isArray(src.messages) ? src.messages : []
  const messages: ChatMessage[] = msgArr
    .map((msg) => {
      if (!msg || typeof msg !== 'object') return null
      const item = msg as Record<string, unknown>
      const role = item.role === 'user' || item.role === 'assistant' || item.role === 'system' ? item.role : null
      const kind =
        item.kind === 'prompt' || item.kind === 'ail' || item.kind === 'status' || item.kind === 'error'
          ? item.kind
          : null
      const text = typeof item.text === 'string' ? item.text : ''
      const ts = typeof item.ts === 'number' && Number.isFinite(item.ts) ? item.ts : Date.now()
      if (!role || !kind) return null
      return {
        id: typeof item.id === 'string' && item.id ? item.id : createId(),
        role,
        kind,
        text,
        ts,
      }
    })
    .filter((item): item is ChatMessage => item !== null)

  const compileObj = src.compileResult
  let compileResult: CompileResult | null = null
  if (compileObj && typeof compileObj === 'object') {
    const cr = compileObj as Record<string, unknown>
    const system = typeof cr.system === 'string' ? cr.system : ''
    const projectRoot = typeof cr.projectRoot === 'string' ? cr.projectRoot : ''
    if (system && projectRoot) {
      compileResult = {
        system,
        projectRoot,
        backendPaths: Array.isArray(cr.backendPaths)
          ? cr.backendPaths.filter((v): v is string => typeof v === 'string')
          : [],
        hasRbac: typeof cr.hasRbac === 'boolean' ? cr.hasRbac : undefined,
        hasOrRoles: typeof cr.hasOrRoles === 'boolean' ? cr.hasOrRoles : undefined,
      }
    }
  }

  const runStatusObj = src.runStatus
  let runStatus: RunStatus | null = null
  if (runStatusObj && typeof runStatusObj === 'object') {
    const rs = runStatusObj as Record<string, unknown>
    runStatus = {
      running: Boolean(rs.running),
      pid: typeof rs.pid === 'number' ? rs.pid : null,
      frontend_url: typeof rs.frontend_url === 'string' && rs.frontend_url.trim() ? rs.frontend_url : null,
      backend_url: typeof rs.backend_url === 'string' && rs.backend_url.trim() ? rs.backend_url : null,
      detect_state:
        rs.detect_state === 'found' || rs.detect_state === 'pending' || rs.detect_state === 'timeout'
          ? rs.detect_state
          : 'timeout',
      tail: Array.isArray(rs.tail) ? rs.tail.filter((v): v is string => typeof v === 'string') : [],
    }
  }

  const ailModelsRaw = src.ailModels
  const ailModels: Record<string, string> = {}
  if (ailModelsRaw && typeof ailModelsRaw === 'object') {
    for (const [key, value] of Object.entries(ailModelsRaw as Record<string, unknown>)) {
      if (typeof value === 'string') ailModels[key] = value
    }
  }

  const safeMessages = messages.length > 0 ? messages : [createWelcomeMessage()]

  return {
    id,
    name,
    createdAt,
    updatedAt,
    messages: safeMessages,
    lastAil: typeof src.lastAil === 'string' ? src.lastAil : '',
    ailModels,
    compileResult,
    runStatus,
    lastStatusPollTs:
      typeof src.lastStatusPollTs === 'number' && Number.isFinite(src.lastStatusPollTs)
        ? src.lastStatusPollTs
        : null,
    lastError: typeof src.lastError === 'string' && src.lastError.trim() ? src.lastError : null,
    streamState:
      src.streamState === 'connecting' || src.streamState === 'connected' || src.streamState === 'ended'
        ? src.streamState
        : 'disconnected',
    streamError: typeof src.streamError === 'string' && src.streamError.trim() ? src.streamError : null,
    streamLastEventTs:
      typeof src.streamLastEventTs === 'number' && Number.isFinite(src.streamLastEventTs)
        ? src.streamLastEventTs
        : null,
    logPaused: Boolean(src.logPaused),
    logFilter: src.logFilter === 'errors' ? 'errors' : 'all',
    logDroppedCount:
      typeof src.logDroppedCount === 'number' && Number.isFinite(src.logDroppedCount)
        ? Math.max(0, Math.floor(src.logDroppedCount))
        : 0,
    logLastClearTs:
      typeof src.logLastClearTs === 'number' && Number.isFinite(src.logLastClearTs)
        ? src.logLastClearTs
        : null,
    generateDraft: typeof src.generateDraft === 'string' ? src.generateDraft : '',
    generateStreaming: Boolean(src.generateStreaming),
    generateStreamError:
      typeof src.generateStreamError === 'string' && src.generateStreamError.trim()
        ? src.generateStreamError
        : null,
    generateStreamTs:
      typeof src.generateStreamTs === 'number' && Number.isFinite(src.generateStreamTs)
        ? src.generateStreamTs
        : null,
  }
}

function loadSessionsFromStorage(): void {
  const raw = localStorage.getItem(SESSIONS_STORAGE)
  const activeRaw = localStorage.getItem(ACTIVE_SESSION_STORAGE)

  let loaded: Session[] = []
  if (raw) {
    try {
      const parsed = JSON.parse(raw)
      if (Array.isArray(parsed)) {
        loaded = parsed.map((item) => sanitizeSession(item)).filter((item): item is Session => item !== null)
      }
    } catch {
      loaded = []
    }
  }

  if (loaded.length === 0) {
    const initial = createSession('Session 1')
    sessions.value = [initial]
    activeSessionId.value = initial.id
    return
  }

  sessions.value = loaded

  if (activeRaw && sessions.value.some((session) => session.id === activeRaw)) {
    activeSessionId.value = activeRaw
    return
  }

  const latest = [...sessions.value].sort((a, b) => b.updatedAt - a.updatedAt)[0]
  activeSessionId.value = latest.id
}

function createNewSession(): void {
  if (isLocked()) return
  const session = createSession(getNextSessionName())
  sessions.value.push(session)
  activeSessionId.value = session.id
  void nextTick(() => {
    if (chatListRef.value) {
      chatListRef.value.scrollTop = chatListRef.value.scrollHeight
    }
  })
}

function schedulePersistSessions(): void {
  if (persistTimer !== null) {
    window.clearTimeout(persistTimer)
  }
  persistTimer = window.setTimeout(() => {
    localStorage.setItem(SESSIONS_STORAGE, JSON.stringify(sessions.value))
    localStorage.setItem(ACTIVE_SESSION_STORAGE, activeSessionId.value)
  }, 200)
}

onMounted(() => {
  loadSettingsFromStorage()
  loadSessionsFromStorage()
  initXterm()
  if (isStudioPreviewUrl(previewUrl.value)) {
    previewUrl.value = SAFE_EMPTY_PREVIEW_URL
    localStorage.removeItem(PREVIEW_STORAGE)
    termWrite('[ui] preview url pointed to studio, reset')
  }
  if (activeSessionId.value && getSessionById(activeSessionId.value)?.runStatus?.running) {
    startSessionPoller(activeSessionId.value, 0)
    const root = getProjectRootForSession(activeSessionId.value)
    if (root) {
      connectSessionStream(activeSessionId.value, root)
    }
  }

  void nextTick(() => {
    if (chatListRef.value) {
      chatListRef.value.scrollTop = chatListRef.value.scrollHeight
    }
    fitAddon?.fit()
  })
})

onBeforeUnmount(() => {
  cancelAllGenerateOperations()
  closeAllSessionStreams()
  stopAllSessionPollers()
  if (persistTimer !== null) {
    window.clearTimeout(persistTimer)
    persistTimer = null
  }
  disposeXterm()
})

watch(apiKey, (value) => localStorage.setItem(API_KEY_STORAGE, value))
watch(model, (value) => localStorage.setItem(MODEL_STORAGE, value))
watch(projectName, (value) => localStorage.setItem(PROJECT_STORAGE, value))
watch(previewUrl, (value) => localStorage.setItem(PREVIEW_STORAGE, value))
watch(
  [sessions, activeSessionId],
  () => {
    schedulePersistSessions()
  },
  { deep: true },
)
watch(activeSessionId, (nextId, prevId) => {
  if (prevId) {
    cancelSessionGenerate(prevId)
    stopSessionPoller(prevId)
  }
  if (nextId && getSessionById(nextId)?.runStatus?.running) {
    startSessionPoller(nextId, 0)
    const root = getProjectRootForSession(nextId)
    if (root) {
      connectSessionStream(nextId, root)
    }
  }
  void nextTick(() => {
    if (chatListRef.value) {
      chatListRef.value.scrollTop = chatListRef.value.scrollHeight
    }
  })
})
</script>

<template>
  <div class="h-screen w-screen overflow-hidden bg-slate-950 text-slate-100">
    <div class="grid h-full grid-cols-[35%_65%]">
      <aside class="flex h-full min-h-0 flex-col border-r border-slate-800 bg-slate-950">
        <header class="space-y-3 border-b border-slate-800 bg-slate-950 p-4">
          <div class="flex items-center justify-between">
            <h1 class="text-lg font-semibold tracking-wide text-slate-100">AIL Studio</h1>
            <button
              type="button"
              class="rounded-md border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-200 hover:bg-slate-800"
              @click="settingsOpen = true"
            >
              Settings
            </button>
          </div>
          <div class="grid grid-cols-[1fr_auto] gap-2">
            <select
              v-model="activeSessionId"
              :disabled="isLocked()"
              data-testid="session-select"
              class="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none focus:border-slate-500 disabled:cursor-not-allowed disabled:bg-slate-900 disabled:opacity-60"
            >
              <option v-for="session in sessions" :key="session.id" :value="session.id">
                {{ session.name }}
              </option>
            </select>
            <button
              type="button"
              :disabled="isLocked()"
              data-testid="session-new"
              class="rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-xs text-slate-200 hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-900 disabled:opacity-60"
              @click="createNewSession"
            >
              New
            </button>
          </div>
        </header>

        <section
          v-if="activeSession?.generateStreaming || activeSession?.generateDraft?.trim()"
          class="border-b border-slate-800 bg-slate-950 p-3"
        >
          <div class="mb-2 flex items-center justify-between text-xs text-slate-400">
            <span>{{ activeSession?.generateStreaming ? 'Generating AIL...' : 'Latest AIL Draft' }}</span>
            <button
              type="button"
              class="rounded-md border border-slate-700 bg-slate-900 px-2 py-1 text-[11px] text-slate-300 hover:bg-slate-800"
              @click="
                activeSessionId &&
                applySessionUpdateById(activeSessionId, (session) => {
                  session.generateDraft = ''
                  session.generateStreamError = null
                  session.generateStreaming = false
                  session.generateStreamTs = Date.now()
                })
              "
            >
              Clear Draft
            </button>
          </div>
          <pre class="max-h-40 overflow-y-auto rounded-md border border-slate-800 bg-black p-2 font-mono text-[11px] text-emerald-300">{{
            activeSession?.generateDraft || ''
          }}</pre>
        </section>

        <section ref="chatListRef" class="min-h-0 flex-1 space-y-2 overflow-y-auto bg-slate-950 p-4">
          <div
            v-for="message in currentMessages"
            :key="message.id"
            :data-testid="`chat-msg-${message.kind}`"
            class="rounded-md border border-slate-800 bg-slate-900 p-3"
            :class="{
              'border-red-800 bg-red-950/30 text-red-200': message.kind === 'error',
            }"
          >
            <p class="mb-1 text-[11px] uppercase tracking-wide text-slate-400">
              <template v-if="message.kind === 'prompt'">User prompt</template>
              <template v-else-if="message.kind === 'ail'">
                AIL output ({{ currentAilModels[message.id] || model }})
              </template>
              <template v-else-if="message.kind === 'error'">Error</template>
              <template v-else>Status</template>
            </p>
            <details v-if="message.kind === 'ail'">
              <summary class="cursor-pointer text-sm text-slate-300">Show generated AIL</summary>
              <pre class="mt-2 whitespace-pre-wrap text-xs text-slate-200">{{ message.text }}</pre>
            </details>
            <p v-else class="whitespace-pre-wrap text-sm">{{ message.text }}</p>
          </div>
        </section>

        <footer class="border-t border-slate-800 bg-slate-950 p-4">
          <div class="space-y-3">
            <textarea
              v-model="promptInput"
              rows="3"
              :disabled="isLocked()"
              data-testid="prompt-input"
              placeholder="Describe what you want to build..."
              class="w-full resize-none rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-600 outline-none focus:border-slate-500 disabled:cursor-not-allowed disabled:bg-slate-900 disabled:opacity-60"
              @keydown="onPromptKeydown"
            />
            <div class="grid grid-cols-2 gap-2">
              <button
                type="button"
                :disabled="isLocked() || !promptInput.trim()"
                data-testid="btn-send"
                class="w-full rounded-md bg-slate-100 px-4 py-2 text-sm font-medium text-slate-950 transition hover:bg-white disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400 disabled:opacity-60"
                @click="handleGenerate"
              >
                {{ state === 'GENERATING' ? 'Generating…' : 'Send' }}
              </button>
              <button
                type="button"
                :disabled="isLocked() || !currentLastAil.trim()"
                data-testid="btn-compile"
                class="w-full rounded-md border border-slate-700 bg-slate-900 px-4 py-2 text-sm font-medium text-slate-200 transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-900 disabled:text-slate-500 disabled:opacity-60"
                @click="handleCompile"
              >
                {{ state === 'COMPILING' ? 'Compiling…' : 'Compile' }}
              </button>
            </div>
          </div>
        </footer>
      </aside>

      <section class="flex h-full min-h-0 flex-col bg-slate-950 p-4">
        <div class="mb-3 flex items-center gap-2 rounded-md border border-slate-800 bg-slate-900 p-2">
          <label class="whitespace-nowrap text-xs text-slate-400">Preview URL</label>
          <input
            v-model="previewUrl"
            type="text"
            :disabled="isLocked()"
            class="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-1.5 text-xs text-slate-100 placeholder:text-slate-600 outline-none focus:border-slate-500 disabled:cursor-not-allowed disabled:bg-slate-900 disabled:opacity-60"
          />
          <button
            type="button"
            :disabled="isLocked()"
            class="rounded-md border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-200 hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-900 disabled:opacity-60"
            @click="reloadPreview"
          >
            Reload
          </button>
          <button
            type="button"
            :disabled="isLocked()"
            class="rounded-md border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-200 hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-900 disabled:opacity-60"
            @click="copyText(previewUrl)"
          >
            Copy Preview URL
          </button>
          <button
            type="button"
            :disabled="isLocked()"
            data-testid="btn-reset-preview"
            class="rounded-md border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-200 hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-900 disabled:opacity-60"
            @click="handleResetPreview"
          >
            Reset Preview
          </button>
        </div>

        <div
          v-if="currentCompileResult"
          data-testid="compile-card"
          class="mb-3 rounded-md border border-slate-800 bg-slate-900 p-3 text-xs text-slate-200"
        >
          <div class="flex flex-wrap items-center gap-3">
            <span><span class="text-slate-400">system:</span> {{ currentCompileResult.system }}</span>
            <span class="truncate"><span class="text-slate-400">project_root:</span> {{ currentCompileResult.projectRoot }}</span>
            <div class="ml-auto flex flex-wrap gap-2">
              <button
                type="button"
                class="rounded-md border border-slate-700 bg-slate-900 px-2 py-1 text-xs text-slate-200 hover:bg-slate-800"
                @click="copyText(currentCompileResult.projectRoot)"
              >
                Copy Path
              </button>
              <button
                type="button"
                class="rounded-md border border-slate-700 bg-slate-900 px-2 py-1 text-xs text-slate-200 hover:bg-slate-800"
                @click="handleCopyReproReport"
              >
                Copy Repro Report
              </button>
              <button
                type="button"
                :disabled="isLocked()"
                data-testid="btn-run"
                class="rounded-md border border-slate-700 bg-slate-900 px-2 py-1 text-xs text-slate-200 hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-900 disabled:opacity-60"
                @click="handleRun"
              >
                Run
              </button>
              <button
                type="button"
                :disabled="isLocked()"
                data-testid="btn-stop"
                class="rounded-md border border-slate-700 bg-slate-900 px-2 py-1 text-xs text-slate-200 hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-900 disabled:opacity-60"
                @click="handleStop"
              >
                Stop
              </button>
              <button
                type="button"
                :disabled="isLocked()"
                data-testid="btn-detect"
                class="rounded-md border border-slate-700 bg-slate-900 px-2 py-1 text-xs text-slate-200 hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-900 disabled:opacity-60"
                @click="handleDetect"
              >
                Detect
              </button>
              <button
                type="button"
                :disabled="isLocked()"
                data-testid="btn-stop-all"
                class="rounded-md border border-slate-700 bg-slate-900 px-2 py-1 text-xs text-slate-200 hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-900 disabled:opacity-60"
                @click="handleStopAll"
              >
                Stop All
              </button>
            </div>
          </div>
          <div data-testid="run-status" class="mt-2 rounded-md border border-slate-800 bg-slate-950 p-2 text-xs">
            <div class="flex flex-wrap items-center gap-3">
              <div class="flex items-center gap-1">
                <span
                  class="inline-block h-2 w-2 rounded-full"
                  :class="effectiveRunStatus.running ? 'bg-emerald-400' : 'bg-slate-500'"
                />
                <span class="text-slate-400">running:</span>
                <span data-testid="run-running">{{ effectiveRunStatus.running ? 'true' : 'false' }}</span>
              </div>
              <div>
                <span class="text-slate-400">pid:</span>
                <span data-testid="run-pid">{{ effectiveRunStatus.pid ?? '-' }}</span>
              </div>
              <div class="flex items-center gap-1">
                <span
                  data-testid="run-detect"
                  class="rounded px-1.5 py-0.5 text-[11px]"
                  :class="
                    effectiveRunStatus.detect_state === 'found'
                      ? 'bg-emerald-950 text-emerald-300'
                      : effectiveRunStatus.detect_state === 'pending'
                        ? 'bg-amber-950 text-amber-300'
                        : 'bg-slate-800 text-slate-300'
                  "
                >
                  {{ effectiveRunStatus.detect_state }}
                </span>
              </div>
              <div>
                <span class="text-slate-400">polled:</span>
                <span data-testid="run-polled">{{ formatTime(lastStatusPollTs) }}</span>
              </div>
            </div>
            <div class="mt-2 grid grid-cols-1 gap-1 md:grid-cols-2">
              <div class="flex items-center gap-1">
                <span class="text-slate-400">frontend:</span>
                <button
                  v-if="effectiveRunStatus.frontend_url"
                  type="button"
                  data-testid="run-frontend-url"
                  class="truncate text-left text-slate-200 underline-offset-2 hover:underline"
                  @click="copyText(effectiveRunStatus.frontend_url, '[ui] copied frontend_url')"
                >
                  {{ effectiveRunStatus.frontend_url }}
                </button>
                <span v-else data-testid="run-frontend-url">-</span>
              </div>
              <div class="flex items-center gap-1">
                <span class="text-slate-400">backend:</span>
                <button
                  v-if="effectiveRunStatus.backend_url"
                  type="button"
                  data-testid="run-backend-url"
                  class="truncate text-left text-slate-200 underline-offset-2 hover:underline"
                  @click="copyText(effectiveRunStatus.backend_url, '[ui] copied backend_url')"
                >
                  {{ effectiveRunStatus.backend_url }}
                </button>
                <span v-else data-testid="run-backend-url">-</span>
              </div>
            </div>
            <div class="mt-2 flex items-center gap-1 text-[11px] text-slate-300">
              <span class="text-slate-400">last_error:</span>
              <span class="truncate">{{ currentLastError || '-' }}</span>
            </div>
            <div class="mt-1 flex items-center gap-1 text-[11px] text-slate-300">
              <span class="text-slate-400">stream:</span>
              <span>{{ currentStreamState }}</span>
            </div>
          </div>
          <details class="mt-2">
            <summary class="cursor-pointer text-slate-300">Start Project</summary>
            <pre class="mt-2 whitespace-pre-wrap rounded-md bg-black p-2 font-mono text-[11px] text-emerald-400">cd {{ currentCompileResult.projectRoot }}
./start.sh</pre>
          </details>
        </div>

        <div class="min-h-0 flex-[3] rounded-md border border-slate-800 bg-slate-900 p-2">
          <iframe
            :key="iframeKey"
            title="Preview"
            :src="previewUrl"
            class="h-full w-full rounded-md border border-slate-800 bg-white"
          />
        </div>

        <div class="mt-3 flex items-center gap-2 rounded-md border border-slate-800 bg-slate-900 px-3 py-2 text-xs">
          <button
            type="button"
            data-testid="btn-log-pause"
            class="rounded-md border border-slate-700 bg-slate-900 px-2 py-1 text-slate-200 hover:bg-slate-800"
            @click="handleLogPauseToggle"
          >
            {{ currentLogPaused ? 'Resume' : 'Pause' }}
          </button>
          <select
            v-model="currentLogFilter"
            data-testid="log-filter"
            class="rounded-md border border-slate-700 bg-slate-950 px-2 py-1 text-slate-200 outline-none focus:border-slate-500"
          >
            <option value="all">all</option>
            <option value="errors">errors</option>
          </select>
          <button
            type="button"
            data-testid="btn-log-clear"
            class="rounded-md border border-slate-700 bg-slate-900 px-2 py-1 text-slate-200 hover:bg-slate-800"
            @click="handleLogClear"
          >
            Clear
          </button>
        </div>

        <div class="mt-4 min-h-0 flex-1 overflow-hidden rounded-md border border-slate-800 bg-black p-2">
          <div ref="xtermContainerRef" data-testid="xterm" class="h-full w-full bg-black" />
        </div>
        <div data-testid="xterm-mirror" class="hidden">{{ xtermMirror.join('\n') }}</div>
      </section>
    </div>

    <div
      v-if="settingsOpen"
      class="fixed inset-0 z-50 flex items-start justify-end bg-black/60 p-4"
      @click.self="settingsOpen = false"
    >
      <div class="w-full max-w-md rounded-lg border border-slate-700 bg-slate-900 p-4 shadow-2xl">
        <div class="mb-3 flex items-center justify-between">
          <h2 class="text-sm font-semibold text-slate-100">Settings</h2>
          <button
            type="button"
            class="rounded-md border border-slate-700 bg-slate-900 px-2 py-1 text-xs text-slate-200 hover:bg-slate-800"
            @click="settingsOpen = false"
          >
            Close
          </button>
        </div>
        <div class="space-y-3">
          <div class="space-y-1">
            <label class="text-xs text-slate-400">LLM API Key (BYOK)</label>
            <div class="flex gap-2">
              <input
                v-model="apiKey"
                :type="showApiKey ? 'text' : 'password'"
                :disabled="isLocked()"
                placeholder="sk-..."
                class="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-600 outline-none focus:border-slate-500 disabled:cursor-not-allowed disabled:bg-slate-900 disabled:opacity-60"
              />
              <button
                type="button"
                :disabled="isLocked()"
                class="rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-xs text-slate-200 hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-900 disabled:opacity-60"
                @click="showApiKey = !showApiKey"
              >
                {{ showApiKey ? 'Hide' : 'Show' }}
              </button>
            </div>
            <p v-if="apiKey" class="text-[11px] text-slate-500">
              Saved: {{ maskedKey(apiKey) }}
            </p>
          </div>
          <div class="space-y-1">
            <label class="text-xs text-slate-400">LLM Model</label>
            <input
              v-model="model"
              type="text"
              :disabled="isLocked()"
              placeholder="moonshot-v1-32k"
              class="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-600 outline-none focus:border-slate-500 disabled:cursor-not-allowed disabled:bg-slate-900 disabled:opacity-60"
            />
          </div>
          <div class="space-y-1">
            <label class="text-xs text-slate-400">Project Name</label>
            <input
              v-model="projectName"
              type="text"
              :disabled="isLocked()"
              placeholder="AutoProject"
              class="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-600 outline-none focus:border-slate-500 disabled:cursor-not-allowed disabled:bg-slate-900 disabled:opacity-60"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
