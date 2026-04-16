from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("AIL_Deployer_V3")


@mcp.tool()
async def deploy_ail_app(ail_code: str) -> str:
    """
核心脚手架生成工具。必须严格使用 AIL V3.0 语法。所有指令用波浪号 `~` 连接。
【终极铁律】：绝对不允许生成任何原生 HTML、CSS、JS 或 Vue 模板代码！你的目标是把 Token 消耗降到最低，只做架构级抽象规划！

【AIL V3.0 核心架构字典】：
- ^SYS[项目名] : 定义系统名称。例如：^SYS[CSDN_Clone]
- >DB_TABLE[表名]{字段:类型} : 定义数据表(类型限 str/int/text)。例如：>DB_TABLE[users]{uid:int,name:str}
- @API[方法,路由]{动作} : 定义接口。动作限 >DB_SEL[表] 或 >DB_INS[表]。例如：@API[GET,/api/posts]{>DB_SEL[posts]}
- @PAGE[页面名,路径] : 定义前端页面。例如：@PAGE[Home,/]

【V3.0 生态与 UI 连接器（新增）】：
不要手写 UI，直接通过以下指令召唤开源组件库：
- #LIB[生态库名] : 全局声明需要安装的 UI 组件库。例如：#LIB[shadcn-vue] 或 #LIB[tailwind]
- #UI[来源:组件名]{配置} : 在当前 @PAGE 下声明使用该库的具体组件。例如：#UI[shadcn:Navbar]{theme:dark} 或 #UI[shadcn:Card]{data:posts, layout:grid}
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
