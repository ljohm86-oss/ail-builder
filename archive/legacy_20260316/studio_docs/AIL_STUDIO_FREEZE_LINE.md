🧊 AIL Studio 技术冻结线（Freeze Line）规范 v1.0

目的：把系统“不可变的核心”冻结住，保证任何迭代都只能在可控边界内发生。
该文档优先级高于所有任务单/PR 描述/个人习惯。

⸻

0. 冻结对象与范围

0.1 永久冻结（不得改动协议/语义）
	1.	AIL 母舰（5002）

	•	POST /generate_ail
	•	POST /compile
	•	返回 JSON 字段结构、关键字段命名与语义全部冻结
	•	禁止添加新字段要求前端依赖
	•	禁止改变字段含义（即使字段名不变）

	2.	AIL V5 编译引擎

	•	sanitize/phase1/phase2 行为与日志口径冻结
	•	编译产物目录结构（backend/main.py、frontend/routes.generated.ts 等）冻结

解释：任何变化都会让“可复现证据链”失效，造成工程不可控。

⸻

1. 本地 MVP 冻结前提（环境约束）
	1.	仅本机运行

	•	所有服务只允许 127.0.0.1
	•	不处理公网/鉴权/多租户

	2.	端口约束

	•	母舰：127.0.0.1:5002
	•	Proxy：127.0.0.1:5050
	•	Web 壳：127.0.0.1:4173（E2E 固定）

	3.	不在 MVP 阶段上云

	•	不做网关、不做反代配置管理、不做部署脚本产品化

⸻

2. 前端冻结线（AIL Studio Web）

2.1 禁止事项（红线）
	1.	禁止代码编辑器

	•	禁止 Monaco
	•	禁止文件树
	•	禁止展示生成源码
	•	修改必须走对话输入（Prompt → AIL → Compile）

	2.	BYOK 冻结

	•	不允许后端硬编码任何 LLM Key
	•	Key 只存在浏览器 LocalStorage
	•	请求时随 body 发送给母舰（或同源 proxy 转发）

	3.	单向状态机冻结

	•	IDLE / GENERATING / COMPILING（以及后续 RUN 相关状态）
	•	任一忙碌态必须锁死 UI 输入
	•	禁止并发 generate/compile/run

	4.	iframe 刷新铁律

	•	compile 成功或 Reload：只能通过更新 iframeKey 强刷
	•	禁止 contentWindow.reload()
	•	禁止通过复杂消息协议“热注入”

⸻

3. Proxy 冻结线（ail-studio-proxy.py）

3.1 核心职责冻结

Proxy 只做三类事（不得扩权）：
	1.	run/stop：启动与停止 ./start.sh
	2.	status：返回运行信息 + tail（或 detect_state）
	3.	stream（SSE）：推送 stdout/stderr

3.2 安全冻结要求
	1.	project_root 严格校验（必须保持）

	•	必须绝对路径
	•	禁止 ..
	•	必须在 /Users/carwynmac/ai-cl/output_projects 下
	•	必须存在且是目录
	•	/run 要求 start.sh 存在且可执行

	2.	进程组停止策略冻结

	•	SIGTERM → 1s → SIGKILL 兜底
	•	优先 killpg，fallback terminate/kill

	3.	单项目运行策略冻结

	•	/run 必须先 stop 所有正在运行项目
	•	不允许并行跑多个 project_root

⸻

4. 同源策略冻结（解决 CORS 的唯一方式）

4.1 MVP 唯一允许的跨域解决方案
	•	只允许在 Web 壳（vite dev server）做同源 proxy
	•	不允许：
	•	Playwright --disable-web-security
	•	通过 page.request 绕过 UI 流程作为主路径
	•	让母舰临时加 CORS（上云阶段再统一做）

4.2 路由命名冻结（建议固定）
	•	/mothership/* → http://127.0.0.1:5002/*
	•	/proxy/* → http://127.0.0.1:5050/*

前端 fetch 一律走相对路径：
	•	POST /mothership/generate_ail
	•	POST /mothership/compile
	•	/proxy/run|stop|status|stream

⸻

5. Session 冻结线（多会话一致性）

5.1 Session 级隔离必须保持
	•	generate/compile/run/status/stop/SSE 事件都必须绑定 sid
	•	禁止回写 activeSession 造成串会话

5.2 日志与状态展示冻结原则
	•	UI 只展示 当前 active session
	•	后台 session 不允许写入当前终端（避免污染）
	•	允许“后台只更新 session 数据”，但不写 xterm

⸻

6. 日志系统冻结线（xterm + mirror + controls）

6.1 统一日志管线冻结

任何输出必须经过：
	•	writeSessionLog -> appendToTerminal -> xterm/mirror

禁止：
	•	直接 term.writeln() 绕过管线
	•	mirror 与 xterm 不一致

6.2 xterm-mirror 冻结
	•	mirror 仅用于可测性与诊断
	•	只保留最后 200 行
	•	Playwright 只断言 mirror，不读 xterm DOM

6.3 日志控制冻结（如果已引入）
	•	Pause：不写 xterm/mirror，只累计 dropped
	•	Resume：输出 [ui] resumed, dropped=<count>
	•	Clear：输出 [ui] log cleared

⸻

7. Playwright 冻结线（E2E 的“真标准”）

7.1 必须保持的验收项（Run Panel 1~4）
	1.	compile 后状态条初始值（pending + running=false + pid=’-’）
	2.	Session A Run → 切 Session B 不串
	3.	Detect found + URL 点击复制 + mirror 文案出现
	4.	Stop 后回落 timeout + [ui] stop ok

7.2 测试必须具备的诊断能力

失败必须明确属于：
	•	服务不可达（5002/5050）
	•	CORS/网络失败（Failed to fetch）
	•	generate/compile 返回 error
	•	run/stop/status 失败
	•	SSE 无日志（弱断言失败）

⸻

8. 允许演进的区域（非冻结区）

只有以下方向允许继续迭代：
	1.	UI/交互（不破坏单向状态机）
	2.	可靠性增强（poller、SSE 重连、诊断提示）
	3.	可测性增强（data-testid、mirror、稳定断言）
	4.	Beta 功能补齐（在 guardrails 内）

⸻

9. 违反冻结线的处理（强制规则）

触发任意一条：
	•	改动母舰接口协议
	•	引入代码编辑器/源码可见
	•	BYOK 变成后端持 key
	•	Playwright 绕过浏览器安全策略
	•	iframe 刷新铁律被破坏

必须：
	1.	立即停止合并
	2.	回滚到上一个绿版
	3.	重新走 Freeze Evidence Log

⸻

10. 交付口径（给协作者/外包/模型）

协作者（含 Codex/Minimax）所有 PR 描述必须包含：
	•	变更文件列表（必须可审计）
	•	是否触碰冻结线（必须声明 No）
	•	Playwright 结果（必须贴 14 或 15）
	•	失败时诊断（必须可定位）

