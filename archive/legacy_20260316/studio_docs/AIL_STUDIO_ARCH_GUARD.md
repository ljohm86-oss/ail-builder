🧨 AIL Studio 架构崩坏预警信号表（Architecture Guard v1.0）

作用：在系统开始“悄悄变坏”之前就发现它。
这是比 Freeze Line 更早期的预警层。

⸻

一、红色警报（出现任意一条必须立即停手）

🔴 1. 出现“全局状态回流”

症状：
	•	某个 async 逻辑写 activeSession 而不是 sid
	•	runStatus 被提到全局
	•	poller 不再按 session 维度管理
	•	SSE 连接不再按 sid 绑定

后果：

会话污染
状态错写
难以复现的幽灵 bug

处理：
	•	立刻回滚
	•	不允许“顺手修一下”

⸻

🔴 2. 日志绕过 writeSessionLog

任何地方出现：

term.writeln(...)

而没有经过：

writeSessionLog

这是严重违规。

后果：
	•	Pause 失效
	•	Filter 失效
	•	mirror 不一致
	•	E2E 断言漂移

⸻

🔴 3. iframe 刷新逻辑被改

只要出现：
	•	contentWindow.reload
	•	直接修改 src
	•	postMessage 强刷

立即回滚。

⸻

🔴 4. Playwright 变成“伪 E2E”

如果测试开始：
	•	使用 page.request 代替 UI 操作
	•	删除失败诊断
	•	移除 SSE 断言
	•	把 timeout 改很大掩盖问题

这是架构退化。

⸻

二、黄色预警（需要审视）

🟡 1. watch 数量持续增加

如果 watch 超过：

12 个以上

说明：
	•	状态边界开始模糊
	•	数据流不再清晰

⸻

🟡 2. 出现“辅助状态”

比如：
	•	isRunning
	•	hasCompiled
	•	shouldPoll
	•	isStreaming

而这些状态可以从已有状态推导。

这叫“状态膨胀”。

⸻

🟡 3. 日志控制逻辑分散

如果：
	•	Pause 逻辑出现在 3 个函数
	•	Filter 逻辑出现在 2 个以上位置

说明管线开始碎裂。

⸻

🟡 4. Session 结构超过 15 个字段

Session 现在已经很复杂：
	•	runStatus
	•	logPaused
	•	logFilter
	•	logDroppedCount
	•	streamState
	•	lastError
	•	compileResult
	•	…

超过 15 个字段 → 需要拆子结构。

⸻

三、蓝色信号（性能退化）

🔵 1. poller 多实例存在

打开 DevTools → Network

如果看到：
	•	同时多个 /status 在跑
	•	同时多个 /stream 在跑

说明 poller 泄漏。

⸻

🔵 2. xterm 渲染卡顿

症状：
	•	输入卡顿
	•	滚动掉帧

可能原因：
	•	mirror 没有限制
	•	filter 逻辑 O(n²)
	•	未做批量写入

⸻

🔵 3. localStorage 写入频率异常

如果：
	•	每秒写多次
	•	切 session 卡顿

说明持久化策略失控。

⸻

四、架构健康指标（Healthy Signals）

如果系统健康，你应该看到：
	•	E2E 全绿
	•	Session 切换无串状态
	•	Run → Detect → Stop 无 race
	•	SSE 重连可预测
	•	xterm mirror 与真实输出一致
	•	刷新页面后 session 恢复正常

⸻

五、系统熵增模型

任何系统都会“熵增”。

AIL Studio 的熵来源：
	1.	Async 回写
	2.	多 session 并发
	3.	SSE 重连
	4.	Poller 生命周期
	5.	状态条可视化增强
	6.	日志过滤

Freeze Line 控制“结构熵”，
Architecture Guard 控制“行为熵”。

⸻

六、崩坏前的典型征兆

系统崩坏前通常会出现：
	•	偶发性无法 reproduce 的 bug
	•	E2E 偶发 fail
	•	偶发 detect=timeout 但进程在跑
	•	偶发 SSE 不 reconnect
	•	Stop 后仍有日志进来

如果你看到这些：

不要 patch
先查生命周期

⸻

七、强制回滚规则

当满足任意：
	•	2 个红色警报
	•	3 个黄色预警
	•	1 个红 + 2 个蓝

必须：
	1.	暂停新功能
	2.	回滚到上一个绿版
	3.	重新画数据流图

⸻

八、未来升级条件（解除 Freeze 的门槛）

允许架构升级（比如 WebSocket 替换 SSE）的条件：
	•	连续 30 天 E2E 稳定
	•	无 session 污染
	•	无 poller 泄漏
	•	日志系统 100% 可控
	•	代码无绕管线写入

否则不动。

⸻

最重要的一句话

不可预测 = 架构开始失控。

当你开始“解释 bug”而不是“复现 bug”，
那说明架构边界已经模糊。

⸻
