from __future__ import annotations

from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ail-deploy-server-v1.1")


@mcp.tool()
async def deploy_ail_app(ail_code: str) -> str:
    """部署 AIL 应用到本地编译服务器。

    当你调用本工具时，必须传入参数：
    - ail_code: string，必须是符合以下规范的 AIL 符号流。

    AIL 是一种极度压缩的全栈专有语言。你必须将人类的 Web 开发需求翻译为 AIL 符号，绝对不要输出 Python/HTML。
    【核心字典】
    - ^F : 切换到前端DOM环境
    - ^B : 切换到后端API环境
    - ^D : 切换到数据库环境
    - #I[type,id] : 渲染输入框，例如 #I[text,uname]
    - #B[id]*0{文字} : 渲染按钮，例如 #B[btn]*0{注册}
    - *E[click,id]{动作} : 绑定点击事件，动作中可使用 >P[路由]{参数} 发起POST请求。
    - +R[POST,路由] : 后端注册路由
    - &[变量名] : 存入变量
    - $T[表名]{字段} : 数据库建表
    - $W[表名]{数据} : 写入数据库
    - <-[200]{返回JSON} : 接口返回
    - #T[tag,id]*0{文字} : 渲染排版文本，例如 #T[h1,title]*0{极客博客}
    - #S[id]{CSS} : 注入内联样式，例如 #S[title]{color:#00ffcc; text-align:center}
    【语法铁律】
    所有的指令动作之间，必须严格使用波浪号 `~` 连接！绝对不能省略。
    示例代码：^F~#I[text,uname]~#B[btn]*0{提交}~^B~+R[POST,/api]~&req.body.uname
    """

    payload: dict[str, Any] = {"ail_code": ail_code}

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                "http://127.0.0.1:5000/compile",
                headers={"Content-Type": "application/json"},
                json=payload,
            )
            response.raise_for_status()

        body_preview = response.text.strip()
        if body_preview:
            return (
                "AIL 编译成功！请告诉用户可以在浏览器访问 "
                "http://127.0.0.1:5000/ 查看他们生成的全栈应用。\n"
                f"编译服务器返回：{body_preview}"
            )

        return (
            "AIL 编译成功！请告诉用户可以在浏览器访问 "
            "http://127.0.0.1:5000/ 查看他们生成的全栈应用。"
        )

    except httpx.TimeoutException:
        return "AIL 编译请求超时：连接本地编译服务器 http://127.0.0.1:5000/compile 时超时。"
    except httpx.HTTPStatusError as exc:
        return (
            "AIL 编译失败："
            f"HTTP {exc.response.status_code}，响应内容：{exc.response.text}"
        )
    except httpx.RequestError as exc:
        return f"AIL 编译失败：网络请求异常：{exc}"
    except Exception as exc:  # pragma: no cover
        return f"AIL 编译失败：未预期错误：{exc}"


if __name__ == "__main__":
    mcp.run()
