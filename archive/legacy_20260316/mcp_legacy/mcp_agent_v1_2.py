from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("AIL_Deployer_V1_2")


@mcp.tool()
async def deploy_ail_app(ail_code: str) -> str:
    """
核心部署工具。必须使用 AIL V1.2 语法。
所有的 AIL 指令必须使用波浪号 `~` 连接。

【AIL V1.2 核心字典】：
- ^F : 切换到前端环境。
- ^B : 切换到后端环境。
- #T[标签,id]*0{内容} : 生成文本。例如：#T[h1,title]*0{极客博客}
- #S[id]{样式} : 注入 CSS 样式。例如：#S[title]{color:#00ffcc;}
- #I[类型,id] : 生成输入框。例如：#I[text,uname]
- #B[id]*0{文字} : 生成按钮。例如：#B[submit-btn]*0{发布文章}
- *E[click,按钮id]{>P[路由]} : 给按钮绑定点击事件，发起POST请求。例如：*E[click,submit-btn]{>P[/api/add]}

【V1.2 全新数据驱动指令】：
- #D[id] : 渲染一个空的 DOM 容器，用于装载列表。例如：#D[article-list]
- #L[容器id,路由]{模板} : 列表渲染。向该GET路由请求JSON数组，遍历渲染模板后插入到容器。例如：#L[article-list,/api/posts]{ <h3>{title}</h3><p>{content}</p> }
- >DB_INIT[表名]{字段1,字段2} : 在后端建表。例如：>DB_INIT[posts]{title,content}
- >DB_INSERT[表名] : 必须在 POST 路由后使用。自动把前端发来的 JSON 数据存入该表。例如：+R[POST,/api/add]~>DB_INSERT[posts]
- >DB_SELECT[表名] : 必须在 GET 路由后使用。自动把该表所有数据查出并返回 JSON 数组。例如：+R[GET,/api/posts]~>DB_SELECT[posts]
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
