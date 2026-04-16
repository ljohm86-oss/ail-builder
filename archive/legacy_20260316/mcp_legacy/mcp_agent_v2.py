from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("AIL_Deployer_V2")


@mcp.tool()
async def deploy_ail_app(ail_code: str) -> str:
    """
核心脚手架生成工具。必须使用 AIL V2.0 语法。所有指令用波浪号 `~` 连接。不要生成任何 HTML 或前端代码，只生成宏观架构指令！

【AIL V2.0 宏观架构字典】：
- ^SYS[项目名] : 定义系统名称。例如：^SYS[CSDN_Clone]
- >DB_TABLE[表名]{字段1:类型,字段2:类型} : 定义数据表(类型仅限 str/int/text)。例如：>DB_TABLE[users]{uid:int,name:str}
- @API[方法,路由]{动作} : 定义后端接口。动作必须是 >DB_SEL[表名] 或 >DB_INS[表名]。例如：@API[GET,/api/posts]{>DB_SEL[posts]}
- @PAGE[页面名,路径] : 定义前端页面路由。例如：@PAGE[Home,/]
- #COMP[组件名]{配置} : 在当前 @PAGE 下声明页面组件。例如：#COMP[Navbar]{auth=true}
"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "http://127.0.0.1:5000/compile",
                json={"ail_code": ail_code},
            )
            response.raise_for_status()
            return response.text
    except httpx.TimeoutException:
        return "部署失败：请求超时（10 秒内未收到编译引擎响应）。"
    except httpx.HTTPStatusError as exc:
        return f"部署失败：HTTP {exc.response.status_code}，响应：{exc.response.text}"
    except httpx.RequestError as exc:
        return f"部署失败：网络请求异常：{exc}"
    except Exception as exc:  # pragma: no cover
        return f"部署失败：未预期错误：{exc}"


if __name__ == "__main__":
    mcp.run()
