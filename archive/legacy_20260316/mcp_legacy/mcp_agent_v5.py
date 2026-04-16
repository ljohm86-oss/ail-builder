from mcp.server.fastmcp import FastMCP
import os
import json
import httpx

mcp = FastMCP("AIL_Deployer_V5")
BASE_URL = os.getenv("AIL_SERVER_URL", "http://127.0.0.1:5002").rstrip("/")
BASE_URL = BASE_URL.replace("http://localhost", "http://127.0.0.1").replace(
    "https://localhost", "https://127.0.0.1"
)
COMPILE_URL = f"{BASE_URL}/compile"
MCP_AGENT_BUILD = "2026-02-28-1"


def _debug_block(
    *,
    status: str,
    server: str = "",
    content_type: str = "",
    date: str = "",
    body_text: str = "",
) -> str:
    body = body_text or ""
    return "\n".join(
        [
            f'MCP_AGENT_BUILD="{MCP_AGENT_BUILD}"',
            f"FINAL_COMPILE_URL={COMPILE_URL}",
            f"status={status}",
            f"server={server}",
            f"content_type={content_type}",
            f"date={date}",
            f"body_len={len(body)}",
            f"body_preview={body[:200]}",
        ]
    )


@mcp.tool()
async def deploy_ail_app(ail_code: str) -> str:
    """
核心脚手架生成工具。必须严格使用 AIL 符号语法。
【终极铁律】：绝对不允许生成任何原生代码（HTML/CSS/JS/Vue/Python业务实现），只允许输出 AIL 符号指令！

【AIL 核心语法字典】：
- ^SYS[项目名] : 定义系统名称
- >DB_TABLE[表名]{字段:类型} : 定义数据库表结构（类型限 str/int/text）
- >DB_REL[主表(1)->从表(N)] : 定义一对多关系映射
- @API[AUTH,路由]{>DB_AUTH[表名]} : 定义登录鉴权接口
- @API[POST,路由]{>DB_INS[表名]*AUTH} : 定义需要 JWT 路由守卫的写入接口
- @PAGE[页面名,路径] : 定义前端页面路由
- #UI[来源:组件名]{配置} : 在页面中声明 UI 组件
"""
    try:
        print(f"Using AIL_SERVER_URL={BASE_URL}")
        print(f"POST {COMPILE_URL}")
        print(f"FINAL_COMPILE_URL={COMPILE_URL}")
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                COMPILE_URL,
                json={"ail_code": ail_code},
            )

        if response.status_code == 200:
            try:
                payload = response.json()
                if isinstance(payload, dict):
                    debug = payload.get("debug")
                    if not isinstance(debug, dict):
                        debug = {}
                    debug["final_compile_url"] = COMPILE_URL
                    debug["mcp_agent_build"] = MCP_AGENT_BUILD
                    payload["debug"] = debug
                    return json.dumps(payload, ensure_ascii=False)
            except ValueError:
                pass
            return (
                f'MCP_AGENT_BUILD="{MCP_AGENT_BUILD}"\n'
                f"FINAL_COMPILE_URL={COMPILE_URL}\n"
                f"{response.text}"
            )

        body_text = response.text or ""
        print(f"status={response.status_code} body_len={len(body_text)}")
        print(f"server={response.headers.get('server', '')}")
        print(f"content_type={response.headers.get('content-type', '')}")
        print(f"date={response.headers.get('date', '')}")
        print(f"response_text_head={body_text[:200]!r}")

        return _debug_block(
            status=str(response.status_code),
            server=response.headers.get("server", ""),
            content_type=response.headers.get("content-type", ""),
            date=response.headers.get("date", ""),
            body_text=body_text,
        )
    except httpx.TimeoutException:
        return _debug_block(
            status="timeout",
            body_text="部署失败：请求超时（10 秒内未收到编译引擎响应）。",
        )
    except httpx.RequestError as exc:
        return _debug_block(
            status=f"request_error:{exc.__class__.__name__}",
            body_text=f"部署失败：网络请求异常：{exc}",
        )
    except Exception as exc:  # pragma: no cover
        return _debug_block(
            status=f"exception:{exc.__class__.__name__}",
            body_text=f"部署失败：未预期错误：{exc}",
        )


if __name__ == "__main__":
    mcp.run()
