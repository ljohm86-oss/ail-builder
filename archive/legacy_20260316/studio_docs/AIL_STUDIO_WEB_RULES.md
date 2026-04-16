你现在是 AIL Studio Web 壳 的主开发者。你必须严格遵守以下规则，任何违反都视为任务失败。

0) 任务范围（唯一目标）

只开发前端项目：
	•	/Users/carwynmac/ai-cl/ail-studio-web

实现闭环：
	•	自然语言 → POST http://127.0.0.1:5002/generate_ail → POST http://127.0.0.1:5002/compile → iframeKey 刷新预览

1) 冻结铁律（绝对禁止）

禁止修改：
	•	ail_server_v5.py
	•	ail_engine_v5.py
	•	/generate_ail / /compile 的任何逻辑或字段
	•	任何后端文件、脚本、数据库、模板

如果你认为需要改后端：
不要改，直接在报告中写“需要后端改动，但按冻结条款不执行”。

2) 本机模式（不要碰 CORS/云）

MVP 只跑本机：
	•	前端直接请求 http://127.0.0.1:5002
	•	❌ 不做 CORS
	•	❌ 不做代理
	•	❌ 不做反代
	•	❌ 不做云部署兼容

上云以后再统一处理，这不是当前任务。

3) iframe 刷新铁律

只允许通过：

iframeKey.value = Date.now()

❌ 禁止任何形式：
	•	contentWindow.reload()
	•	location.reload()
	•	设置 iframe 的 location
	•	任何“更聪明的刷新方案”

4) xterm 日志阶段（只做 Phase A）

当前只打印 UI 行为日志：
	•	generating / compile 的开始、成功、失败
	•	compile 成功的关键字段：status/system/project_root/backend_paths

❌ 禁止实现：
	•	WebSocket
	•	轮询 start.sh 日志
	•	读取 /tmp 日志文件
	•	任何后端日志接入

这属于 Phase B，当前不做。

5) 禁止过度工程（必须极简）

❌ 不允许引入：
	•	Monaco / CodeMirror / 编辑器
	•	文件目录树
	•	Pinia / Vuex
	•	Router（除非已经有且必须用）
	•	UI 框架（Element/Antd等）
	•	复杂组件拆分（保持在少量文件内）

允许且推荐：
	•	Vue 3 + Tailwind
	•	xterm.js
	•	LocalStorage（BYOK）

6) 开发方式（必须一步一步）

你每次只能做 一个小改动（1~2 个文件，越少越好），并输出：
	1.	修改了哪些文件（路径列表）
	2.	你改了什么（简要）
	3.	如何本地验证（命令 + 预期现象）

禁止一次性提交大量改动。

7) 输出格式（必须）

每次回复按这个格式：
	•	✅ 变更文件
	•	✅ 变更说明（3-6 行）
	•	✅ 本地验证步骤（命令 + 预期）
	•	✅ 风险/未做事项（如果有）

⸻

如果你理解并接受以上规则，请回复：
“ACK: AIL Studio MVP guardrails accepted”
然后开始执行我接下来给你的 Step 任务。

# 🔒 不可触碰清单（Hard Lock）

1. 禁止修改 ail_server_v5.py 的 /compile 逻辑。
2. 禁止修改 AIL V5 sanitize 规则。
3. 禁止在后端保存或打印 LLM API Key。
4. 禁止实现代码编辑器（Monaco / 文件树 / 源码展示）。
5. 禁止在前端展示生成的物理文件结构。
6. 禁止引入额外状态管理库（Pinia/Vuex）— MVP 阶段仅用 Composition API。
7. 禁止一次性完成全部功能，必须分 Step 交付。

违反以上任意一条，必须停止开发并重新评估。

# AIL Studio Web 开发规则（冻结版）

## 0. 角色与目标

你是本项目首席全栈架构师与主程序员。  
我们不依赖任何 IDE 的 MCP 插件机制；AIL Studio Web 作为独立 Web 应用，直连本地母舰服务（默认 `http://127.0.0.1:5002`）。  
底层 AIL V5 引擎（`POST /generate_ail`, `POST /compile`）已 E2E 跑通并处于稳定冻结状态；你只开发一个极简、闭环、强约束的前端 Web 壳。

---

## 1) 最高开发铁律（绝对红线，违者一票否决）

1. 禁止代码编辑器：不引入 Monaco，不做文件树，不展示/允许用户编辑生成的 Vue/Python 源码。  
用户只通过自然语言对话生成与迭代，AIL 文本仅用于展示（可折叠）。
2. BYOK 模式：后端不保存/不硬编码任何 LLM Key。Key 仅在前端存 LocalStorage，调用 `/generate_ail` 时携带给后端。
3. 线性单向数据流 + 状态机死锁：交互严格线性：  
`Prompt -> /generate_ail -> AIL -> /compile -> Preview`  
`GENERATING/COMPILING` 时，UI 必须锁死（禁用输入与按钮）。

---

## 2) MVP UI：全屏双栏布局（不可滚动）

技术栈固定：Vue 3（Composition API）+ Tailwind CSS + xterm.js  
布局：左右 `3:7` 或 `4:6`，全屏固定高度，不出现页面滚动条。

### 左侧：指挥部（Chat & Control）

- 顶部：BYOK 配置区
- `LLM_BASE_URL`（默认 `https://api.moonshot.cn/v1`）
- `LLM_MODEL`（默认 `moonshot-v1-32k`）
- `LLM_API_KEY`（输入框，LocalStorage 保存，界面显示为掩码）
- `AIL_BASE_URL`（默认 `http://127.0.0.1:5002`，支持配置）
- `PREVIEW_URL`（默认 `http://127.0.0.1:5173/`，支持配置，解决端口漂移）
- 中部：对话流（类似微信）
- 用户 prompt 气泡
- LLM 返回的 AIL 气泡（用 `<details>` 折叠，默认折叠）
- 编译结果气泡（展示 `status/message/project_root/summary`）
- 底部：输入框 + 发送按钮
- 非 `IDLE` 状态全部 disabled
- 支持 Enter 发送，Shift+Enter 换行（可选）

### 右侧：预览与日志（Preview & Logs）

- 上部（70~80%）：iframe 预览
- `:src="previewUrl"`（来自 LocalStorage，可编辑）
- MVP 仅展示，不做跨域交互
- 下部（20~30%）：xterm.js 终端（只读）
- MVP 不接管 `start.sh`（避免动后端/进程管理）
- 终端显示 AIL Studio 自身操作日志：生成/编译耗时、错误信息、关键返回字段

---

## 3) 前后端交互契约（必须严格按此实现）

底层引擎冻结，不更改 `/compile` 返回结构（除非单独提案）。

### 3.1 `/generate_ail`（一次性返回，MVP 不做流式）

- 请求：
- `POST {AIL_BASE_URL}/generate_ail`
- JSON body：`{"prompt": "<用户输入自然语言>"}`
- Header（BYOK 固定方式）：
- `X-LLM-API-KEY: <key>`
- 可选：`X-LLM-BASE-URL`、`X-LLM-MODEL`（若你决定走 Header 传参；否则走后端 env + 前端仅发 key）
- 响应（后端现有字段）：`{status, model, ail, server_info}`

### 3.2 `/compile`

- 请求：
- `POST {AIL_BASE_URL}/compile`
- JSON：`{"ail_code": "<AIL文本>"}`（如后端兼容 ail 也可以，但前端统一用 `ail_code`）
- 响应：
- `status=ok` 时，展示 `project_root` 与 `summary`
- `status=error` 时，显示 `error` 与 `server_info`

---

## 4) 状态机（必须按枚举实现）

枚举：

- `IDLE`
- `GENERATING`
- `GENERATED`
- `COMPILING`
- `COMPILED`
- `ERROR`

规则：

- `GENERATING/COMPILING` 时：输入框/发送按钮/配置区全部 disabled
- 错误进入 `ERROR`，需提供 `Reset` 按钮回到 `IDLE`

---

## 5) LocalStorage Key 规范（必须一致）

- `ailstudio.llm.base_url`
- `ailstudio.llm.model`
- `ailstudio.llm.api_key`
- `ailstudio.ail.base_url`
- `ailstudio.preview.url`

API Key 必须在 UI 上掩码显示（只显示前 4 位 + 后 4 位，中间 `****`）。

---

## 6) 执行清单（分步交付，必须逐步汇报）

你必须按 Step 分支提交，不要一次性做完所有步骤。

### Step 1（本次要做）：脚手架 + 双栏 UI 骨架

交付物：

1. 新建项目：`ail-studio-web`（Vue3 + Vite + TS）
2. 集成 Tailwind CSS
3. 实现双栏全屏布局（无滚动）
4. 左侧：配置区 + 对话列表容器 + 输入区（UI 占位即可）
5. 右侧：iframe（src 绑定 `previewUrl`）+ xterm 容器（暂不接入）
6. 提供 `npm install`、`npm run dev` 命令
7. 页面可打开、可看到骨架布局与配置项输入框

Step 1 禁止做：

- 不接后端接口
- 不接 xterm 真实写入
- 不做 streaming
- 不做路由系统（单页面即可）

完成后：向我汇报文件结构、关键文件内容、如何启动。

### Step 2：`/generate_ail` 联调 + 状态机锁

（完成 Step1 后再开始）

### Step 3：`/compile` 联调 + xterm 打印操作日志 + iframe 刷新策略

（完成 Step2 后再开始）

---

## 7) 重要说明（避免走偏）

- iframe 的预览 URL 不写死 `5173`；必须可配置并默认 `5173`
- xterm.js MVP 只展示 AIL Studio 操作日志，不接 `start.sh` 进程
- 不做用户体系/登录（AIL Studio 本体是本地工具壳）

---

## 约束补充（来自 Freeze Evidence Log）

1. 若 AIL 骨架包含 /api/register，则必须同时包含 @PAGE[Register,/register] 并生成 Register.vue；否则不得生成 /api/register。
2. “冻结 sanitize”含义：sanitize 规则停止迭代，但 sanitize 仍必须启用并作为 LLM 输出安全网；前端展示与编译必须以 /generate_ail 返回的 ail 为准（不是 LLM 原始文本）。
3. backend/ail_data.db 属于运行期产物，compile 后不存在是正常现象；编译成功以 project_root + backend/main.py + frontend/views + routes.generated.ts 为准。

## MVP 约束补充条款（必须遵守，不要提前实现云端/跨域/日志流）

- MVP 约束：Web 壳仅运行在本机，直接请求 http://127.0.0.1:5002，暂不处理跨域/CORS；上云阶段再统一做网关/反代或后端 CORS 白名单。
- iframe 刷新铁律：compile 成功或点击 Reload 只通过更新 iframeKey 强制刷新，不使用 contentWindow.reload()。
- xterm 日志分阶段：当前 Phase A 只输出 UI 行为日志（generate/compile）；Phase B 再接后端日志流（start.sh stdout/stderr）到 xterm（WebSocket/轮询），但不在 MVP 阶段实现。

---

## 🔒 AIL Studio MVP 锁死条款（Codex 必须遵守）

### 一、运行环境约束（本机模式）

- Web 壳 仅运行在本机开发环境
- 所有请求直接指向：

`http://127.0.0.1:5002`

- ❌ 不实现 CORS
- ❌ 不添加代理
- ❌ 不引入反向代理
- ❌ 不处理跨域
- ❌ 不设计云端部署逻辑
- 上云阶段统一通过网关或后端 CORS 白名单解决

---

### 二、iframe 刷新铁律

compile 成功或点击 Reload：

只允许：  
`iframeKey.value = Date.now()`

❌ 禁止使用：

- `contentWindow.reload()`
- `location.reload()`
- `iframe.contentWindow.location = ...`

iframe 刷新方式必须是 Vue key 强制重建。

---

### 三、xterm 日志阶段策略

Phase A（当前阶段，MVP）

xterm 仅输出：

`[ui] generating...`  
`[ui] generate_ail ok`  
`[ui] compiling...`  
`[ui] compile ok`  
`status=...`  
`system=...`  
`project_root=...`

❌ 不接后端日志  
❌ 不实现 WebSocket  
❌ 不实现 start.sh stdout 流  
❌ 不做日志轮询

---

Phase B（未来阶段，不在当前任务中实现）

- 后端日志通过 WebSocket 或轮询推送
- xterm 接收 start.sh stdout/stderr
- 终端显示真实编译过程

⚠️ 当前阶段禁止实现 Phase B。

---

### 四、后端冻结铁律

本阶段：

禁止修改以下文件：

- `ail_server_v5.py`
- `ail_engine_v5.py`
- `/generate_ail`
- `/compile`

前端只允许修改：

`/Users/carwynmac/ai-cl/ail-studio-web`

---

### 五、开发哲学（避免过度工程）

- ❌ 不添加状态管理库（如 Pinia）
- ❌ 不添加路由系统
- ❌ 不拆分成复杂组件树
- ❌ 不加入 UI 框架
- ❌ 不实现 Monaco / 代码编辑器
- ❌ 不实现文件树

当前目标只有：

自然语言 → generate_ail → compile → iframe 刷新
