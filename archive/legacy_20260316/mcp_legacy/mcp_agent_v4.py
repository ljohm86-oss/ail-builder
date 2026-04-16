from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("AIL_Deployer_V4")


@mcp.tool()
async def deploy_ail_app(ail_code: str) -> str:
    """
核心脚手架生成工具。必须严格使用 AIL V4.0 语法。
【终极铁律】：绝对不允许生成任何原生 HTML、CSS、JS 或 Vue 代码！只做架构级抽象规划，把 Token 消耗降到最低！

【AIL V4.0 核心架构字典】：
- ^SYS[项目名] : 定义系统
- >DB_TABLE[表名]{字段:类型} : 定义数据表(类型限 str/int/text)
- @PAGE[页面名,路径] : 定义前端页面
- #LIB[生态库名] : 全局引入开源组件库（如 #LIB[shadcn-vue]）
- #UI[来源:组件名]{配置} : 页面内声明使用 UI 组件（如 #UI[shadcn:Navbar]{theme:dark}）

【V4.0 深水区核心逻辑（新增）】：
1. 数据库关系映射：
   - >DB_REL[主表(1)->从表(N)] : 建立一对多级联外键关系。例如：>DB_REL[users(1)->posts(N)]
2. JWT 鉴权体系：
   - @API[AUTH,路由]{>DB_AUTH[表名]} : 指定登录表并生成带 JWT 签发的登录接口。例如：@API[AUTH,/api/login]{>DB_AUTH[users]}
3. 接口路由守卫：
   - *AUTH : 放在 action 尾部，表示该接口必须携带 JWT Token 才能访问。例如：@API[POST,/api/posts]{>DB_INS[posts]*AUTH}
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
