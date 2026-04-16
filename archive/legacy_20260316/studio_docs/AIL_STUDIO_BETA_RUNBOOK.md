# 🧰 AIL Studio Beta Runbook v1.0（启动 / 排障 / 验收）

> 适用范围：AIL Studio 本机 Beta（127.0.0.1），包含：
> - 母舰（AIL V5 引擎）：5002
> - Proxy（Run/Stop/Detect/SSE）：5050
> - Web 壳（Vue/Vite）：4173
>
> 约束：
> - 不改 5002/5050 协议语义
> - 默认浏览器安全策略（不使用 disable-web-security）
> - iframe 刷新只能改 iframeKey（不调用 contentWindow.reload）

---

## 0) 环境前置

### 必备版本（建议）
- Node.js：18+（建议 20+）
- Python：3.10+
- macOS / Linux 均可（本说明以 macOS 路径为例）

### 目录约定
- AIL Studio Web：`/Users/carwynmac/ai-cl/ail-studio-web`
- 生成项目根目录：`/Users/carwynmac/ai-cl/output_projects/*`

---

## 1) 一键启动顺序（必须按顺序）

> ✅ 总原则：先后端（5002、5050）→ 再前端（4173）

### 1.1 启动母舰（5002）
```bash
cd /Users/carwynmac/ai-cl
AIL_SANITIZE_TEST=1 python3 ail_server_v5.py

验证端口可达（405 也算可达）：

curl -i http://127.0.0.1:5002/compile
```

⸻

1.2 启动 Proxy（5050）

```bash
cd /Users/carwynmac/ai-cl
python3 /Users/carwynmac/ai-cl/ail-studio-proxy.py
```

验证 proxy 可达：

```bash
curl -i "http://127.0.0.1:5050/status?project_root=/Users/carwynmac/ai-cl/output_projects"
```

⸻

1.3 启动 Web 壳（4173）

```bash
cd /Users/carwynmac/ai-cl/ail-studio-web
npm install
npm run dev -- --host 127.0.0.1 --port 4173
```

打开：
	•	http://127.0.0.1:4173/

⸻

2) Web 端标准操作流程（闭环）

2.1 Generate → Compile
	1.	输入 BYOK API Key（仅保存在 LocalStorage）
	2.	输入 prompt，点击 Send
	3.	生成出 AIL 后，点击 Compile
	4.	右侧出现 compile 成功卡片（system / project_root / Start Project）

2.2 Run → Detect → Preview
	1.	在 compile 卡片上点击 Run
	2.	等待状态条出现 running=true 且 pid 有值
	3.	点击 Detect（或 compile 后自动 detect）
	4.	发现 frontend_url 后：
	•	Preview URL 自动更新
	•	iframe 通过 iframeKey 强刷显示新项目

2.3 SSE 日志（Phase B）
	•	Run 后会通过 /proxy/stream 持续写日志到 xterm
	•	Stop 或 event:end 会关闭流

⸻

3) 端到端验收（Playwright）

3.1 安装浏览器

```bash
cd /Users/carwynmac/ai-cl/ail-studio-web
npm run pw:install
```

3.2 运行 E2E

确保 5002、5050、4173 都在跑，然后：

```bash
cd /Users/carwynmac/ai-cl/ail-studio-web
npm run test:e2e
```

验收标准：所有测试用例通过（至少 1~4 + 日志控制用例如已纳入）。

⸻

4) 常见问题与排障

4.1 页面提示 Failed to fetch（CORS）

现象
	•	浏览器里 generate/compile 请求失败：Failed to fetch
	•	curl 正常

原因
	•	真实浏览器跨域（4173 → 5002 / 5050）被 CORS 拦截

正确解法（Beta 方案）
	•	必须走同源代理：
	•	Web -> /mothership/* 转发到 http://127.0.0.1:5002/*
	•	Web -> /proxy/* 转发到 http://127.0.0.1:5050/*

禁止用 disable-web-security 绕过。

⸻

4.2 5002 端口占用 / Address already in use

查占用：

```bash
lsof -nP -iTCP:5002 -sTCP:LISTEN
```

杀掉进程（谨慎）：

```bash
kill -9 <PID>
```


⸻

4.3 Run 后 detect 一直 pending（超过 30s）

现象
	•	状态条 detect_state=pending
	•	xterm 可能出现：[ui] hint: detect pending >30s...

优先排查
	1.	proxy 是否还在跑（5050）
	2.	project_root 是否合法且存在 start.sh
	3.	start.sh 是否启动了前端（会输出 FRONTEND_URL=… 或类似日志）
	4.	点击 Detect 手动再拉一次

⸻

4.4 Stop 后仍在输出日志（SSE 未关闭）

期望
	•	Stop 后：
	•	running=false
	•	SSE 收到 event:end 或连接关闭
	•	xterm 不再追加新行

排查
	•	proxy /stop 返回是否为 ok
	•	status 是否回落 running=false
	•	页面是否有多个 session 残留 EventSource（应当 session 级管理）

⸻

4.5 node_modules / lockfile 引发的奇怪问题

建议“清洁安装”：

```bash
cd /Users/carwynmac/ai-cl/ail-studio-web
rm -rf node_modules package-lock.json
npm cache verify
npm install
```


⸻

5) 诊断产物（必须能导出）

5.1 Repro Report

compile 成功卡片中点击 Copy Repro Report，粘贴到 Issue/PR，包含：
	•	prompt
	•	AIL
	•	system / project_root
	•	frontend_url / backend_url
	•	preview_url
	•	has_rbac / has_or_roles

5.2 xterm-mirror（用于测试断言）

页面隐藏 xterm-mirror 保留最后 200 行，E2E 只断言 mirror，避免直接读 xterm DOM 不稳定。

⸻

6) Beta 放行最小 Checklist（粘贴到 PR 描述）
	•	5002/5050/4173 启动顺序文档可复跑
	•	Prompt → Generate → Compile → Run → Detect → Preview 可跑通
	•	Run/Stop 10 次循环无 500，状态可回落
	•	Playwright 全绿（附输出）
	•	Repro Report 可复制（附示例）
	•	未破坏 Freeze Line（No protocol change / No editor / BYOK ok / iframeKey ok）
