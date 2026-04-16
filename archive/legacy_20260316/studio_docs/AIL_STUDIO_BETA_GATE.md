🚦 AIL Studio Beta Release Gate（Beta 放行门槛）v1.0

目标：定义“可以叫 Beta”的最低标准。
任何 PR/里程碑如果达不到此门槛，统一不得宣称 Beta。

⸻

0. Beta 定义（必须同时满足）

当且仅当同时满足以下三条，才允许对外称为 Beta：
	1.	闭环可复跑：从 Prompt → AIL → Compile → Run → 预览展示，全链路可在本机稳定复跑
	2.	可诊断可复现：出现失败能给出明确错误归因，并能一键导出复现报告
	3.	可自动验收：Playwright E2E 绿灯 + 可在新机器/新环境按文档跑通

⸻

1. 冻结线合规（硬门槛）
	•	必须符合《技术冻结线（Freeze Line）规范 v1.0》
	•	必须明确声明：未改 5002/5050 协议语义、未引入编辑器、BYOK 未破坏、iframe 刷新铁律未破坏
	•	违反任何冻结线 ⇒ 直接判定 不可 Beta

⸻

2. 必备服务拓扑（本机 Beta）

Beta 期默认形态必须固定为：
	•	Web 壳：http://127.0.0.1:4173
	•	母舰：http://127.0.0.1:5002
	•	Proxy：http://127.0.0.1:5050
	•	同源代理：Web 壳通过 /mothership/* 与 /proxy/* 访问后端（解决浏览器 CORS）

禁止：
	•	Playwright 加 --disable-web-security
	•	通过 page.request 绕过 UI 流程作为主链路

⸻

3. Beta 功能最小集（必须全有）

3.1 核心链路（必须）
	1.	generate：输入 prompt → 产出 AIL（展示为折叠内容）
	2.	compile：AIL → 编译成功卡片（system/project_root/Start Project）
	3.	run panel：Run / Stop / Detect
	4.	preview：Detect 到 frontend_url 后自动更新 Preview URL，并用 iframeKey 强刷
	5.	session：至少支持多 session，不串状态（generate/compile/run/status/stop/SSE 都按 sid）

3.2 诊断能力（必须）
	1.	Repro Report：一键复制 Markdown 复现报告（含 prompt/AIL/system/project_root/urls）
	2.	lastError：每个 session 有 lastError，且不会串会话
	3.	30s pending hint：detect pending 超 30s 给一次提示（不刷屏）

3.3 日志能力（Beta 必须）
	1.	SSE 实时日志接入 /proxy/stream（至少能看到 start.sh 输出）
	2.	日志控制（PR-4A）：Pause/Resume + Filter(all/errors) + Clear
	3.	xterm-mirror：隐藏 mirror 用于测试断言（200 行 ring buffer）

⸻

4. 稳定性指标（必须）

4.1 连续跑通率（必须）

在同一台机器上，按标准步骤连续运行 10 次：
	•	Prompt → Generate → Compile → Run → Detect → Preview
要求：成功 ≥ 9/10（允许 1 次失败，但失败必须可诊断可复现）

4.2 Run/Stop 循环（必须）

同一个 project_root 上：
	•	run → stop → status 循环 10 次
要求：
	•	5050 不得出现 500
	•	stop 必须能把 running 拉回 false
	•	不得残留孤儿进程（至少通过 pid 状态可见）

⸻

5. Playwright 放行门槛（必须）

5.1 必须通过的用例集
	•	run-panel.spec.ts 必须全绿（至少包含 1~4 + 日志控制用例）
	•	基础集（硬性）：
	1.	compile 后状态条初始值
	2.	Session A/B 不串状态
	3.	Detect found + URL copy + xterm-mirror 文案
	4.	Stop 后回落 + stop ok
	5.	日志控制：Pause/Filter/Clear 生效（如果已纳入 Beta 功能集）

5.2 失败诊断必须明确

Playwright 失败信息必须能归因到：
	•	服务不可达（5002/5050）
	•	CORS/网络失败（Failed to fetch，且提示同源代理方案）
	•	generate/compile/run/stop/status 的错误
	•	SSE 无日志（弱断言失败）

⸻

6. Beta 发布包要求（必须有文档）

必须提供一份 一页启动说明（README/Runbook），包含：
	1.	启动顺序（5002 → 5050 → 4173）
	2.	完整命令（含端口、host）
	3.	常见故障与定位（CORS、端口占用、run pending、SSE 断流）
	4.	一键验收命令（npm run test:e2e）

⸻

7. Beta 允许的“已知限制”（允许存在）

Beta 阶段允许明确写在 README 的限制（不算缺陷）：
	•	仅本机运行（127.0.0.1）
	•	不做账号/权限/多租户
	•	不做云部署与网关
	•	不保证所有生成项目都能 run 成功（但必须可诊断）

⸻

8. Beta 不允许出现的问题（出现即否决）
	•	任意冻结线破坏（见 Freeze Line）
	•	生成/编译阶段 UI 未锁死导致并发请求
	•	session 串数据（特别是 lastAil/compileResult/runStatus/log）
	•	stop 后仍持续写 SSE 日志（流未关闭）
	•	Playwright 需要 disable-web-security 才能绿

⸻

9. Beta 放行 Checklist（一页勾选）

发布前必须贴出以下勾选清单（全 ✅ 才放行）：
	•	Freeze Line 合规声明（No protocol change / No editor / BYOK ok / iframeKey ok）
	•	同源代理已启用（/mothership, /proxy）
	•	10 次闭环跑通率 ≥ 9/10（附记录）
	•	Run/Stop 循环 10 次无 500（附记录）
	•	Playwright 全绿（附输出）
	•	Repro Report 可复制（附示例）
	•	README/Runbook 完整（启动 + 故障定位 + 验收命令）

⸻
