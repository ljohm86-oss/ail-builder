from flask import Flask, request, jsonify
from ail_engine_v5 import AILParserV5, AILProjectGeneratorV5
from cli.manifest_service import ManifestService
from pathlib import Path
from datetime import datetime, timezone
import json
import hashlib
import os
import re
import time
import traceback
import httpx
from typing import Any, Optional

app = Flask(__name__)
port_env_default = os.getenv("AIL_SERVER_PORT", "5002").strip()
try:
    app.config["AIL_PORT"] = int(port_env_default)
except ValueError:
    app.config["AIL_PORT"] = 5002

# 默认使用 Moonshot API（如有需要可设置环境变量覆盖）
if not os.getenv("LLM_BASE_URL"):
    os.environ["LLM_BASE_URL"] = "https://api.moonshot.cn/v1"
if not os.getenv("LLM_MODEL"):
    os.environ["LLM_MODEL"] = "moonshot-v1-32k"


def _resolve_base_url() -> str:
    configured_port = app.config.get("AIL_PORT")
    if configured_port:
        scheme = request.scheme or "http"
        # 强制使用 127.0.0.1 避免 localhost/IPv6 被 AirPlay 拦截
        return f"{scheme}://127.0.0.1:{configured_port}"
    # fallback: 替换 localhost 为 127.0.0.1
    return (
        (request.host_url.rstrip("/") or "")
        .replace("http://localhost", "http://127.0.0.1")
        .replace("https://localhost", "https://127.0.0.1")
    )


def _extract_rbac_summary(project_root: Path) -> dict:
    roles_path = project_root / "frontend" / "src" / "router" / "roles.generated.ts"
    if not roles_path.exists():
        return {
            "has_rbac": False,
            "has_or_roles": False,
            "role_required": {},
            "nav_pages": [],
        }

    text = roles_path.read_text(encoding="utf-8")

    role_required: dict[str, str] = {}
    role_block_match = re.search(
        r"export\s+const\s+roleRequired\s*:\s*Record<[^>]+>\s*=\s*\{(.*?)\};",
        text,
        re.S,
    )
    if role_block_match:
        role_block = role_block_match.group(1)
        for key, value in re.findall(r'"([^"]+)"\s*:\s*"([^"]+)"', role_block):
            role_required[key] = value

    nav_pages: list[dict] = []
    nav_block_match = re.search(
        r"export\s+const\s+navPages(?:\s*:\s*[^=]+)?\s*=\s*\[(.*?)\];",
        text,
        re.S,
    )
    if nav_block_match:
        nav_block = nav_block_match.group(1)
        for entry in re.findall(r"\{([^{}]+)\}", nav_block):
            path_match = re.search(r'path\s*:\s*"([^"]+)"', entry)
            label_match = re.search(r'label\s*:\s*"([^"]+)"', entry)
            if not path_match or not label_match:
                continue
            page_item: dict[str, object] = {
                "path": path_match.group(1),
                "label": label_match.group(1),
            }
            role_match = re.search(r'role\s*:\s*"([^"]+)"', entry)
            if role_match:
                page_item["role"] = role_match.group(1)
            if re.search(r"public\s*:\s*true", entry):
                page_item["public"] = True
            if re.search(r"requiresAuth\s*:\s*true", entry):
                page_item["requiresAuth"] = True
            nav_pages.append(page_item)

    has_rbac = bool(role_required)
    has_or_roles = any("|" in role for role in role_required.values())
    if not has_or_roles:
        for page in nav_pages:
            role_val = str(page.get("role", ""))
            if "|" in role_val:
                has_or_roles = True
                break

    return {
        "has_rbac": has_rbac,
        "has_or_roles": has_or_roles,
        "role_required": role_required,
        "nav_pages": nav_pages,
    }


def _clean_ail_output(raw_text: str) -> str:
    text = (raw_text or "").strip()
    text = re.sub(r"^\s*```[A-Za-z0-9_-]*\s*", "", text)
    text = re.sub(r"\s*```\s*$", "", text)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines).strip()


def _api_store_root() -> Path:
    return Path("./output_projects/.ail_api").resolve()


def _build_store_path(build_id: str) -> Path:
    return _api_store_root() / "builds" / f"{build_id}.json"


def _project_store_path(project_id: str) -> Path:
    return _api_store_root() / "projects" / f"{project_id}.json"


def _persist_v1_build_record(data: dict) -> None:
    build_id = str(data.get("build_id") or "").strip()
    project_id = str(data.get("project_id") or "").strip()
    if not build_id or not project_id:
        return

    build_record = {
        "build_id": build_id,
        "project_id": project_id,
        "mode": data.get("mode", "full"),
        "status": "succeeded",
        "created_at": data.get("created_at"),
        "diff_summary": data.get("diff_summary") or {"added": 0, "updated": 0, "deleted": 0},
        "artifact_available": bool(data.get("source_project_root")),
        "manifest_version": int((data.get("manifest") or {}).get("manifest_version", 0) or 0),
        "source_project_root": data.get("source_project_root"),
        "server_info": data.get("server_info") or {},
    }

    build_path = _build_store_path(build_id)
    build_path.parent.mkdir(parents=True, exist_ok=True)
    build_path.write_text(json.dumps(build_record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    project_path = _project_store_path(project_id)
    existing = {}
    if project_path.exists():
        try:
            existing = json.loads(project_path.read_text(encoding="utf-8"))
        except Exception:
            existing = {}

    items = list(existing.get("items") or [])
    items = [item for item in items if item.get("build_id") != build_id]
    items.insert(
        0,
        {
            "build_id": build_id,
            "mode": build_record["mode"],
            "status": build_record["status"],
            "created_at": build_record["created_at"],
        },
    )
    project_record = {
        "project_id": project_id,
        "latest_build_id": build_id,
        "latest_manifest_version": build_record["manifest_version"],
        "created_at": existing.get("created_at") or build_record["created_at"],
        "updated_at": build_record["created_at"],
        "items": items[:50],
    }
    project_path.parent.mkdir(parents=True, exist_ok=True)
    project_path.write_text(json.dumps(project_record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _load_v1_build_record(build_id: str) -> Optional[dict]:
    path = _build_store_path(build_id)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _load_v1_project_record(project_id: str) -> Optional[dict]:
    path = _project_store_path(project_id)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_sha256(project_root: Path) -> str:
    digest = hashlib.sha256()
    excluded_parts = {
        "node_modules",
        "__pycache__",
        ".git",
        ".cache",
        ".vite",
        ".vite-temp",
        ".venv",
        "venv",
    }
    for path in sorted(project_root.rglob("*")):
        if any(part in excluded_parts for part in path.parts):
            continue
        try:
            if not path.is_file() or path.is_symlink():
                continue
        except OSError:
            continue
        if path.name == "ail_data.db" or path.suffix == ".db":
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        rel = path.relative_to(project_root).as_posix()
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        try:
            with path.open("rb") as f:
                while True:
                    chunk = f.read(65536)
                    if not chunk:
                        break
                    digest.update(chunk)
        except (FileNotFoundError, PermissionError, OSError):
            continue
        digest.update(b"\0")
    return digest.hexdigest()


def _build_v1_artifact_descriptor(build_record: dict) -> Optional[dict]:
    build_id = str(build_record.get("build_id") or "").strip()
    project_root_raw = str(build_record.get("source_project_root") or "").strip()
    if not build_id or not project_root_raw:
        return None
    project_root = Path(project_root_raw)
    if not project_root.exists():
        return None
    return {
        "build_id": build_id,
        "artifact_id": f"artifact_{build_id}",
        "download_url": None,
        "expires_at": None,
        "sha256": _artifact_sha256(project_root),
        "format": "directory_descriptor",
        "local_path": str(project_root),
    }


def _collect_generated_files(project_root: Path, manifest_service: ManifestService) -> list[dict]:
    files: list[dict] = []

    view_root = project_root / "frontend" / "src" / "views"
    if view_root.exists():
        for view_file in sorted(view_root.glob("*.vue")):
            content = view_file.read_text(encoding="utf-8")
            files.append(
                {
                    "path": f"src/views/generated/{view_file.name}",
                    "content": content,
                    "sha256": manifest_service.sha256_text(content),
                }
            )

    router_root = project_root / "frontend" / "src" / "router"
    if router_root.exists():
        for router_file in sorted(router_root.glob("*.generated.ts")):
            content = router_file.read_text(encoding="utf-8")
            files.append(
                {
                    "path": f"src/router/generated/{router_file.name}",
                    "content": content,
                    "sha256": manifest_service.sha256_text(content),
                }
            )

    backend_root = project_root / "backend"
    if backend_root.exists():
        for backend_file in sorted(backend_root.rglob("*")):
            if not backend_file.is_file():
                continue
            if backend_file.name == "ail_data.db" or backend_file.suffix == ".db":
                continue
            if "__pycache__" in backend_file.parts or backend_file.suffix == ".pyc":
                continue
            content = backend_file.read_text(encoding="utf-8")
            relative_backend = backend_file.relative_to(backend_root).as_posix()
            files.append(
                {
                    "path": f"backend/generated/{relative_backend}",
                    "content": content,
                    "sha256": manifest_service.sha256_text(content),
                }
            )

    files.sort(key=lambda item: item["path"])
    return files


def _build_v1_compile_data(
    project_id: str,
    project_root: Path,
    server_info: dict,
    legacy_response: dict,
    client_manifest_version: int,
) -> dict:
    manifest_service = ManifestService()
    files = _collect_generated_files(project_root, manifest_service)
    current_build_id = f"build_{server_info['timestamp'].replace('-', '').replace(':', '').replace('T', '_').replace('+00:00', 'Z').replace('.', '_')}"
    manifest = manifest_service.build_manifest(project_id, current_build_id, files, client_manifest_version)
    diff_summary = {
        "added": len(files),
        "updated": 0,
        "deleted": 0,
    }
    return {
        "build_id": current_build_id,
        "project_id": project_id,
        "mode": "full",
        "created_at": server_info["timestamp"],
        "files": files,
        "deleted_files": [],
        "manifest": manifest,
        "diff_summary": diff_summary,
        "artifact": None,
        "source_project_root": str(project_root),
        "server_info": server_info,
        "legacy_summary": legacy_response.get("summary") or {},
        "legacy_build_report": legacy_response.get("build_report") or {},
    }


def _compile_payload(payload: dict) -> tuple[dict, int]:
    server_info = {
        "base_url": _resolve_base_url(),
        "pid": os.getpid(),
        "version": "v5",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    ail_code = payload.get("ail_code") or payload.get("ail") or payload.get("ail_source") or ""
    if not ail_code:
        return {"status": "error", "message": "空指令", "server_info": server_info}, 400

    ast = AILParserV5(ail_code).parse()
    raw_profiles = ast.get("profiles", [])
    profiles_used: list[str] = []
    if isinstance(raw_profiles, list):
        seen_profiles: set[str] = set()
        for item in raw_profiles:
            profile_name = str(item).strip().lower()
            if profile_name and profile_name not in seen_profiles:
                seen_profiles.add(profile_name)
                profiles_used.append(profile_name)

    generator = AILProjectGeneratorV5(ast, base_dir="./output_projects")
    project_path = generator.base_dir / generator.system_name
    print("DEBUG: about to build project")
    print("DEBUG: target path =", project_path)
    project_path = generator.build_project()
    print("DEBUG: path exists?", os.path.exists(project_path))
    print("DEBUG: absolute path =", os.path.abspath(project_path))

    if not os.path.exists(project_path):
        return {
            "status": "error",
            "error": "Project directory was not created",
            "project_root": str(project_path),
            "server_info": server_info,
        }, 500

    project_root = Path(project_path).resolve()
    backend_main_rel = "backend/main.py"
    backend_main_path = project_root / backend_main_rel
    routes_rel = "frontend/src/router/routes.generated.ts"
    routes_path = project_root / routes_rel
    views_dir = project_root / "frontend" / "src" / "views"

    openapi_paths: list[str] = []
    if backend_main_path.exists():
        backend_main_text = backend_main_path.read_text(encoding="utf-8")
        path_matches = re.findall(r'@app\.(?:get|post|put|patch|delete)\("([^"]+)"\)', backend_main_text)
        openapi_paths = list(dict.fromkeys(path_matches))

    views: list[str] = []
    if views_dir.exists():
        views = sorted([p.name for p in views_dir.glob("*.vue") if p.is_file()])

    build_report = {
        "system": generator.system_name,
        "backend": {
            "main_py": backend_main_rel,
            "openapi_paths": openapi_paths,
            "db_file": "backend/ail_data.db",
        },
        "frontend": {
            "views": views,
            "routes_generated": routes_rel,
            "routes_generated_exists": routes_path.exists(),
        },
    }
    summary = {
        "project": build_report["system"],
        "server": server_info["base_url"],
        "backend_paths": build_report["backend"]["openapi_paths"],
        "pages": [Path(view).stem for view in build_report["frontend"]["views"]],
        "routes_file": build_report["frontend"]["routes_generated"],
        "has_verify_script": (project_root / "verify_api.sh").exists(),
        "profiles_used": profiles_used,
        "profile_resolution": "explicit" if profiles_used else "fallback",
    }
    summary.update(_extract_rbac_summary(project_root))

    legacy_payload = {
        "status": "ok",
        "message": "🚀 V5.0 Vue3 前端编译成功！后端已注入 JWT 鉴权与外键关联。",
        "project_root": str(project_root),
        "build_report": build_report,
        "server_info": server_info,
        "summary": summary,
    }
    return legacy_payload, 200


@app.route('/generate_ail', methods=['POST'])
def generate_ail():
    try:
        payload = request.get_json(silent=True) or {}
        prompt = payload.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            return jsonify({"status": "error", "error": "Missing prompt"}), 400
        prompt_text = prompt.strip()
        prompt_lower = prompt_text.lower()
        profile_pattern = re.compile(r"#PROFILE\[\s*([A-Za-z0-9_]+)\s*\]")
        supported_profiles = {"ecom_min", "after_sales", "landing", "app_min"}

        def _extract_profiles_from_text(text: str) -> list[str]:
            found: list[str] = []
            seen: set[str] = set()
            for match in profile_pattern.finditer(text or ""):
                profile_name = match.group(1).strip().lower()
                if profile_name in supported_profiles and profile_name not in seen:
                    seen.add(profile_name)
                    found.append(profile_name)
            return found

        def _extract_profiles_from_lines(lines: list[str]) -> list[str]:
            found: list[str] = []
            seen: set[str] = set()
            for raw_line in lines:
                token = raw_line.strip()
                match = re.match(r"^#PROFILE\[([^\]]+)\]$", token)
                if not match:
                    continue
                profile_name = match.group(1).strip().lower()
                if profile_name in supported_profiles and profile_name not in seen:
                    seen.add(profile_name)
                    found.append(profile_name)
            return found

        def _resolve_profile_modes(
            explicit_profiles: list[str],
            fallback_ecom: bool,
            fallback_after_sales: bool,
            fallback_landing: bool,
        ) -> tuple[bool, bool, bool, bool, bool, bool]:
            explicit = bool(explicit_profiles)
            if explicit:
                profile_set = set(explicit_profiles)
                mode_app = "app_min" in profile_set
                if mode_app:
                    return explicit, False, False, False, False, True
                mode_landing = "landing" in profile_set
                if mode_landing:
                    # landing profile is an explicit standalone frontend profile
                    return explicit, False, False, False, True, False
                mode_ecom = "ecom_min" in profile_set
                mode_after_sales = "after_sales" in profile_set
                include_after_sales = mode_after_sales
                return explicit, mode_ecom, mode_after_sales, include_after_sales, False, False

            mode_landing = fallback_landing
            if mode_landing:
                return explicit, False, False, False, True, False
            mode_ecom = fallback_ecom
            mode_after_sales = fallback_after_sales
            include_after_sales = mode_after_sales or mode_ecom
            return explicit, mode_ecom, mode_after_sales, include_after_sales, False, False

        fallback_ecom_mode = any(
            keyword in prompt_text
            for keyword in [
                "电商",
                "购物",
                "商城",
                "淘宝风格",
                "商品详情",
                "购物车",
                "结算页",
            ]
        ) or any(keyword in prompt_lower for keyword in ["ecom", "checkout", "product/:id"])
        fallback_after_sales_mode = any(
            keyword in prompt_text for keyword in ["售后", "退款", "换货", "联系客服", "客服"]
        ) or any(keyword in prompt_lower for keyword in ["after-sales", "after_sales"])
        fallback_landing_mode = any(
            keyword in prompt_text for keyword in ["品牌官网", "独立站", "营销站", "落地页", "产品官网", "官网"]
        ) or any(keyword in prompt_lower for keyword in ["landing", "brand site", "saas site", "marketing site"])
        prompt_profiles = _extract_profiles_from_text(prompt_text)
        explicit_profile_mode, ecom_mode, after_sales_mode, include_after_sales_mode, landing_mode, app_mode = _resolve_profile_modes(
            prompt_profiles,
            fallback_ecom_mode,
            fallback_after_sales_mode,
            fallback_landing_mode,
        )

        llm_base_url = os.getenv("LLM_BASE_URL", "").strip().rstrip("/")
        llm_api_key = os.getenv("LLM_API_KEY", "").strip()
        llm_model = os.getenv("LLM_MODEL", "moonshot-v1-32k").strip()
        llm_timeout_raw = os.getenv("LLM_TIMEOUT_S", "120").strip()
        try:
            llm_timeout_s = float(llm_timeout_raw)
        except ValueError:
            llm_timeout_s = 120.0
        if llm_timeout_s <= 0:
            llm_timeout_s = 120.0
        try:
            llm_timeout = httpx.Timeout(
                total=llm_timeout_s,
                connect=10.0,
                read=llm_timeout_s,
                write=llm_timeout_s,
            )
        except TypeError:
            llm_timeout = httpx.Timeout(
                timeout=llm_timeout_s,
                connect=10.0,
                read=llm_timeout_s,
                write=llm_timeout_s,
            )
        if not llm_base_url or not llm_api_key or not llm_model:
            return jsonify({"status": "error", "error": "Missing LLM environment variables"}), 500

        chat_url = f"{llm_base_url}/chat/completions"
        model_lower = llm_model.lower()
        llm_temperature = 1 if ("kimi" in model_lower or "moonshot" in model_lower) else 0.1
        strict_system_prompt = (
            "你是 AIL V5 生成器。\n"
            "你必须只输出 AIL 纯文本，禁止输出解释、禁止输出代码块、禁止输出 JSON。\n"
            "禁止输出 YAML、Markdown code fence（```）或任何包裹格式。\n"
            "^SYS 只能是严格格式：^SYS[SystemName]\n"
            "SystemName 只能包含字母、数字、下划线（推荐不用连字符）。\n"
            "禁止 ^SYS[...] 后跟任何字符（尤其是 {、}、,）。\n"
            "你只能使用以下动作/符号（其余一律禁止）：\n"
            "^SYS[...]\n"
            "#PROFILE[app_min]\n"
            "#PROFILE[ecom_min]\n"
            "#PROFILE[after_sales]\n"
            "#PROFILE[landing]\n"
            "#LIB[...]\n"
            ">DB_TABLE[...]{...}\n"
            ">DB_REL[...]\n"
            "@API[METHOD,ROUTE]{...}\n"
            "  其中 METHOD 只能是 GET/POST/PUT/DELETE/AUTH\n"
            "  行为只能使用：>DB_AUTH[table]、>DB_INS[table]、>DB_SEL[table]\n"
            "  鉴权只能用 *AUTH\n"
            "@PAGE[Name,Route]\n"
            "#UI[lib:Component]{...}\n"
            "【硬规则 - DB_TABLE 字段格式】\n"
            ">DB_TABLE 的字段块必须是：>DB_TABLE[table]{col:type,col2:type2}\n"
            "- 禁止出现 'fields=' 或 'columns=' 或任何 key=\n"
            "- 禁止出现嵌套 JSON / YAML\n"
            "【硬规则 - 字段类型】\n"
            "允许的 type 只能是（全部小写）：str | int | text | datetime | bool | float\n"
            "- 禁止 varchar / VARCHAR / char / string(255) / int64 等任何 SQL 类型\n"
            "- 禁止携带括号参数，如 varchar(255)\n"
            "【硬规则 - 字段名】\n"
            "- 只能是 a-zA-Z0-9_，不得含空格\n"
            "- 必须全部小写输出\n"
            "【正确示例】\n"
            "✅ >DB_TABLE[users]{username:str,pwd:str}\n"
            "✅ >DB_TABLE[tools]{name:str,description:text,author_id:int}\n"
            "✅ >DB_TABLE[posts]{title:str,content:text,user_id:int,created_at:datetime}\n"
            "【错误示例 - 禁止输出】\n"
            "❌ >DB_TABLE[users]{fields=username:VARCHAR(255)}\n"
            "❌ >DB_TABLE[users]{columns:{username:varchar(255)}}\n"
            "❌ >DB_TABLE[users]{username:string}\n"
            "❌ >DB_TABLE[users]{\"username\":\"varchar(255\")}\n"
            "【硬规则 - API 动作格式】\n"
            "@API 块格式：@API[method,route]{>DB_XXX[table]*AUTH}\n"
            "- 注册接口：@API[POST,/api/register]{>DB_INS[users]*AUTH}\n"
            "- 登录接口：@API[POST,/api/login]{>DB_AUTH[users]*AUTH}\n"
            "- 获取当前用户：@API[GET,/api/me]{>DB_SEL[users]*AUTH}\n"
            "- 查询列表：@API[GET,/api/items]{>DB_SEL[items]*AUTH}\n"
            "- 禁止在花括号外出现任何内容\n"
            "【正确示例】\n"
            "✅ @API[POST,/api/register]{>DB_INS[users]*AUTH}\n"
            "✅ @API[POST,/api/login]{>DB_AUTH[users]*AUTH}\n"
            "✅ @API[GET,/api/me]{>DB_SEL[users]*AUTH}\n"
            "【错误示例 - 禁止输出】\n"
            "❌ @API[POST,/api/register]*AUTH\n>DB_INS[users]\n"
            "❌ @API[POST,/api/register]{*AUTH}\n>DB_INS[users]\n"
            "❌ @API[POST,/api/register]{>DB_INS[users]}\n"
            "【硬规则 - DB_INS/DB_SEL 格式】\n"
            ">DB_INS[table] 和 >DB_SEL[table] 后面禁止加任何内容，包括花括号\n"
            "【正确示例】\n"
            "✅ >DB_INS[users]\n"
            "✅ >DB_SEL[users]\n"
            "【错误示例 - 禁止输出】\n"
            "❌ >DB_INS[users]{username,password}\n"
            "❌ >DB_SEL[users]{username}\n"
            "❌ >DB_SEL[users]{id,username}\n"
            "【错误示例 - 禁止输出】\n"
            "❌ @API[POST,/api/register]{{\"username\":\"str\",\"pwd\":\"str\"}}\n"
            "❌ @API[POST,/api/login]{username:str,pwd:str}\n"
            "❌ @API[GET,/api/me]{>DB_SEL[users],token:str}\n"
            "【硬规则 - #UI 格式】\n"
            "#UI 块内禁止出现嵌套 JSON 或任意文本\n"
            "【硬规则 - @PAGE 和 #UI 顺序】\n"
            "#UI 必须紧跟在 @PAGE 后面，不能单独出现或出现在 @PAGE 之前\n"
            "【正确示例】\n"
            "✅ @PAGE[Register,/register]\n#UI[lib:Register]{}\n"
            "✅ @PAGE[Login,/login]\n#UI[lib:Login]{}\n"
            "✅ @PAGE[Home,/]\n#UI[lib:Home]{}\n"
            "【错误示例 - 禁止输出】\n"
            "❌ #UI[lib:Register]{}\n@PAGE[Register,/register]\n"
            "❌ @API[POST,/api/register]{>DB_INS[users]*AUTH}\n#UI[lib:Register]{}\n@PAGE[Register,/register]\n"
            "【硬规则 - #UI 格式】\n"
            "#UI 只能紧跟在 @PAGE 后面，用来声明该页面使用的 UI 组件\n"
            "【正确示例】\n"
            "✅ #UI[lib:Home]{}\n"
            "✅ #UI[lib:Login]{}\n"
            "✅ #UI[lib:Tools]{}\n"
            "【错误示例 - 禁止输出】\n"
            "❌ #UI[Home]{lib:Page}\n"
            "❌ #UI[lib:Home]{<Home />}\n"
            "【硬规则 - DB_AUTH 格式】\n"
            ">DB_AUTH[table] 后面禁止加任何内容，包括花括号\n"
            "【正确示例】\n"
            "✅ >DB_AUTH[users]\n"
            "【错误示例 - 禁止输出】\n"
            "❌ >DB_AUTH[users]{pwd}\n"
            "❌ >DB_AUTH[users]{jwt}\n"
            "❌ >DB_AUTH[users]{secret}\n"
            "【硬规则 - DB_INS/DB_SEL 格式】\n"
            ">DB_INS[table] 和 >DB_SEL[table] 后面禁止加任何内容，包括花括号\n"
            "【正确示例】\n"
            "✅ >DB_INS[users]\n"
            "✅ >DB_SEL[users]\n"
            "【错误示例 - 禁止输出】\n"
            "❌ >DB_INS[users]{username:str,pwd:str}\n"
            "❌ >DB_SEL[users]{username}\n"
            "❌ >DB_SEL[users]{id,username}\n"
            "【硬规则 - 括号必须匹配】\n"
            "每一行中 [ 和 ] 必须成对出现，{ 和 } 必须成对出现\n"
            "禁止出现不匹配的括号\n"
            "【正确示例】\n"
            "✅ >DB_AUTH[users]\n"
            "✅ >DB_INS[users]\n"
            "✅ >DB_SEL[users]\n"
            "【错误示例 - 禁止输出】\n"
            "❌ >DB_AUTH[users\n"
            "❌ >DB_INS[users\n"
            "❌ @API[POST,/api/register]*AUTH\n"
            "输出必须以 ^SYS[ 开头，且每条指令占一行。\n"
            "不要输出任何不存在的动作（如 DB_INSERT/DB_SELECT/validate/auth[jwt] 等）。"
        )
        print(f"LLM_BASE_URL={llm_base_url}")
        print(f"LLM_MODEL={llm_model}")
        print(f"LLM_TIMEOUT_S={llm_timeout_s}")
        print(f"LLM_TEMPERATURE={llm_temperature}")
        print('LLM_MODE="strict_ail_v5"')

        def _is_broken_prefix(line: str) -> bool:
            token = (line or "").strip()
            if not token:
                return False
            if token.startswith(">DB"):
                return token in {">DB", ">DB_"} or (token.startswith(">DB_") and "[" not in token)
            if token.startswith("@API") or token.startswith("@PAGE") or token.startswith(">DB_TABLE"):
                return token.count("[") > token.count("]") or token.count("{") > token.count("}")
            return False

        def _normalize_sys_line(lines: list[str]) -> tuple[list[str], str, str]:
            if not lines:
                return ["^SYS[AutoProject]"], "", "^SYS[AutoProject]"

            original_first = lines[0].strip()
            if not original_first.startswith("^SYS["):
                return ["^SYS[AutoProject]"] + lines, original_first, "^SYS[AutoProject]"

            match = re.match(r"^\^SYS\[(.*?)\]", original_first)
            if match:
                system_name = match.group(1)
            else:
                system_name = original_first[5:]

            if "," in system_name:
                system_name = system_name.split(",", 1)[0]
            system_name = system_name.replace(" ", "_")
            system_name = re.sub(r"[^A-Za-z0-9_]", "", system_name)
            if not system_name:
                system_name = "AutoProject"

            fixed_first = f"^SYS[{system_name}]"
            fixed_lines = lines[:]
            fixed_lines[0] = fixed_first
            return fixed_lines, original_first, fixed_first

        def sanitize_ail_v5(text: str) -> dict:
            allowed_methods = {"GET", "POST", "PUT", "DELETE", "AUTH"}
            raw_lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
            before_count = len(raw_lines)
            fallback_applied = False

            def _sanitize_ident(value: str, default: str = "") -> str:
                cleaned = (value or "").strip()
                if "," in cleaned:
                    cleaned = cleaned.split(",", 1)[0]
                cleaned = cleaned.replace(" ", "_")
                cleaned = re.sub(r"[^A-Za-z0-9_]", "", cleaned)
                return cleaned or default

            def _map_field_type(raw_type: str) -> str:
                t = (raw_type or "").strip().lower()
                t = re.sub(r"\(.*?\)", "", t).strip()
                t = t.replace(" ", "")
                if t in {"int", "integer", "bigint", "smallint", "tinyint"}:
                    return "int"
                if t in {"datetime", "timestamp", "date"}:
                    return "datetime"
                if t in {"float", "double", "decimal", "numeric", "real"}:
                    return "float"
                if t in {"bool", "boolean"}:
                    return "bool"
                if t in {"text"}:
                    return "text"
                if "varchar" in t or t in {"char", "string", "str", "texttype"}:
                    return "str"
                return "str"

            sys_line = "^SYS[AutoProject]"
            sys_seen = False
            sanitized_body_lines: list[str] = []
            page_open_for_ui = False

            for line in raw_lines:
                token = line.strip()
                if not token:
                    continue

                if token.startswith("^SYS["):
                    m = re.match(r"^\^SYS\[(.*?)\]", token)
                    sys_name_raw = m.group(1) if m else token[5:]
                    sys_name = _sanitize_ident(sys_name_raw, "AutoProject")
                    sys_line = f"^SYS[{sys_name}]"
                    sys_seen = True
                    continue

                profile_match = re.match(r"^#PROFILE\[([^\]]+)\]\s*$", token)
                if profile_match:
                    profile_name = profile_match.group(1).strip().lower()
                    if profile_name in supported_profiles:
                        sanitized_body_lines.append(f"#PROFILE[{profile_name}]")
                    page_open_for_ui = False
                    continue

                if token.startswith("#LIB["):
                    lib_match = re.match(r"^#LIB\[([^\]]+)\]\s*$", token)
                    if lib_match:
                        lib_name = re.sub(r"[^A-Za-z0-9_-]", "", lib_match.group(1).strip())
                        if lib_name:
                            sanitized_body_lines.append(f"#LIB[{lib_name}]")
                    page_open_for_ui = False
                    continue

                if token.startswith(">DB_TABLE["):
                    m = re.match(r"^>DB_TABLE\[(.*?)\]\{(.*)\}$", token)
                    if not m:
                        continue
                    table_name = _sanitize_ident(m.group(1).lower(), "table")
                    fields_blob = m.group(2).strip()
                    fields_blob = re.sub(r"^(fields|columns)\s*=\s*", "", fields_blob, flags=re.I)
                    fields_blob = fields_blob.replace("/", ",").replace(";", ",")
                    field_items = [item.strip().strip("{}") for item in fields_blob.split(",") if item.strip()]
                    normalized_fields: list[str] = []
                    used_names: set[str] = set()
                    for item in field_items:
                        if ":" in item:
                            key_raw, type_raw = item.split(":", 1)
                        elif "=" in item:
                            key_raw, type_raw = item.split("=", 1)
                        else:
                            continue
                        field_name = _sanitize_ident(key_raw.lower(), "")
                        if not field_name or field_name in used_names:
                            continue
                        used_names.add(field_name)
                        field_type = _map_field_type(type_raw)
                        normalized_fields.append(f"{field_name}:{field_type}")
                    if not normalized_fields:
                        continue
                    sanitized_body_lines.append(f">DB_TABLE[{table_name}]{{{','.join(normalized_fields)}}}")
                    page_open_for_ui = False
                    continue

                if token.startswith(">DB_REL["):
                    if re.match(r"^>DB_REL\[[^\]]+\]$", token):
                        sanitized_body_lines.append(token)
                    page_open_for_ui = False
                    continue

                if token.startswith("@API["):
                    m = re.match(r"^@API\[\s*([^,\]]+)\s*,\s*([^\]]+)\s*\]\s*\{(.*)\}\s*$", token)
                    if not m:
                        continue
                    method = m.group(1).strip().upper()
                    route = m.group(2).strip()
                    body = m.group(3).strip().replace(" ", "")
                    body = re.sub(r">DB_INSERT\[", ">DB_INS[", body, count=1, flags=re.I)
                    body = re.sub(r">DB_SELECT\[", ">DB_SEL[", body, count=1, flags=re.I)
                    if method not in allowed_methods:
                        continue
                    if not route:
                        continue
                    if not route.startswith("/"):
                        route = "/" + route.lstrip("/")

                    base_match = re.match(r"^(>DB_(?:AUTH|INS|SEL)\[[A-Za-z_][A-Za-z0-9_]*\])", body)
                    if not base_match:
                        continue
                    action_base = base_match.group(1)
                    rest = body[len(action_base):]
                    modifiers: list[str] = []
                    valid_modifiers = True
                    while rest:
                        if rest.startswith("*AUTH"):
                            if "*AUTH" not in modifiers:
                                modifiers.append("*AUTH")
                            rest = rest[len("*AUTH"):]
                            continue
                        role_match = re.match(r"^\*ROLE\[([^\]]+)\]", rest)
                        if role_match:
                            raw_roles = role_match.group(1)
                            role_parts: list[str] = []
                            for part in raw_roles.split("|"):
                                role = re.sub(r"[^A-Za-z0-9_]", "", part.strip())
                                if role:
                                    role_parts.append(role)
                            if role_parts:
                                role_value = "|".join(role_parts)
                                role_modifier = f"*ROLE[{role_value}]"
                                if role_modifier not in modifiers:
                                    modifiers.append(role_modifier)
                            rest = rest[role_match.end():]
                            continue
                        valid_modifiers = False
                        break
                    if not valid_modifiers:
                        continue
                    action = action_base + "".join(modifiers)
                    sanitized_body_lines.append(f"@API[{method},{route}]{{{action}}}")
                    page_open_for_ui = False
                    continue

                if token.startswith("@PAGE["):
                    m = re.match(r"^@PAGE\[\s*([^,\]]+)\s*,\s*([^\]]+)\s*\]\s*(\*ROLE\[[^\]]+\])?\s*$", token)
                    if not m:
                        continue
                    page_name = _sanitize_ident(m.group(1), "Page")
                    route = m.group(2).strip()
                    if not route:
                        continue
                    if not route.startswith("/"):
                        route = "/" + route.lstrip("/")
                    role_suffix = ""
                    role_raw = m.group(3)
                    if role_raw:
                        role_body_match = re.match(r"^\*ROLE\[([^\]]+)\]$", role_raw.strip())
                        if role_body_match:
                            role_parts: list[str] = []
                            for part in role_body_match.group(1).split("|"):
                                role = re.sub(r"[^A-Za-z0-9_]", "", part.strip())
                                if role:
                                    role_parts.append(role)
                            if role_parts:
                                role_suffix = f"*ROLE[{'|'.join(role_parts)}]"
                    sanitized_body_lines.append(f"@PAGE[{page_name},{route}]{role_suffix}")
                    page_open_for_ui = True
                    continue

                if token.startswith("#UI["):
                    if not page_open_for_ui:
                        continue
                    ui_match = re.match(r"^#UI\[([^:\]]+):([^\]]+)\]\{(.*)\}\s*$", token, re.S)
                    if not ui_match:
                        continue
                    source_raw, comp_raw, config_raw = ui_match.groups()
                    source = re.sub(r"[^A-Za-z0-9_-]", "", source_raw.strip())
                    component = re.sub(r"[^A-Za-z0-9_]", "", comp_raw.strip())
                    if not source or not component:
                        continue
                    config = config_raw.strip()
                    sanitized_body_lines.append(f"#UI[{source}:{component}]{{{config}}}")
                    continue

            auth_users_patched = False
            has_auth_users_api = any(
                re.match(r"^@API\[AUTH,[^\]]+\]\{>DB_AUTH\[users\](?:\*AUTH)?(?:\*ROLE\[[^\]]+\])?\}$", line)
                for line in sanitized_body_lines
            )
            if has_auth_users_api:
                users_index = -1
                users_fields_order: list[str] = []
                users_fields_map: dict[str, str] = {}
                for idx, line in enumerate(sanitized_body_lines):
                    m_users = re.match(r"^>DB_TABLE\[users\]\{(.*)\}$", line)
                    if not m_users:
                        continue
                    users_index = idx
                    fields_blob = m_users.group(1).strip()
                    items = [item.strip() for item in fields_blob.split(",") if item.strip()]
                    for item in items:
                        if ":" not in item:
                            continue
                        key_raw, type_raw = item.split(":", 1)
                        key = _sanitize_ident(key_raw.lower(), "")
                        if not key or key in users_fields_map:
                            continue
                        users_fields_order.append(key)
                        users_fields_map[key] = _map_field_type(type_raw)
                    break

                if users_index == -1:
                    sanitized_body_lines.insert(0, ">DB_TABLE[users]{username:str,pwd:str}")
                    auth_users_patched = True
                else:
                    changed = False
                    if "username" not in users_fields_map:
                        users_fields_order.append("username")
                        users_fields_map["username"] = "str"
                        changed = True
                    if "pwd" not in users_fields_map:
                        users_fields_order.append("pwd")
                        users_fields_map["pwd"] = "str"
                        changed = True
                    if changed:
                        rebuilt = ",".join(f"{name}:{users_fields_map[name]}" for name in users_fields_order)
                        sanitized_body_lines[users_index] = f">DB_TABLE[users]{{{rebuilt}}}"
                        auth_users_patched = True

            if auth_users_patched:
                print("SANITIZE_AUTH_USERS_PATCHED=1")

            final_lines = [sys_line] + sanitized_body_lines
            if final_lines:
                last_line = final_lines[-1]
                if last_line.count("[") > last_line.count("]") or last_line.count("{") > last_line.count("}"):
                    final_lines = final_lines[:-1]

            if len(final_lines) <= 1:
                fallback_applied = True
                if app_mode:
                    final_lines = [
                        final_lines[0] if final_lines else "^SYS[AIChatMini]",
                        "#PROFILE[app_min]",
                        "#LIB[tailwind]",
                        ">DB_TABLE[chats]{id:str,title:str,last_message:str,time:str,unread:int}",
                        ">DB_TABLE[contacts]{id:str,name:str,status:str}",
                        ">DB_TABLE[user_profile]{id:str,name:str,bio:text}",
                        "@PAGE[Home,/]",
                        '#UI[app:TopBar]{title:"AI Chat"}',
                        '#UI[app:BottomTab]{items:"chats|contacts|discover|me"}',
                        '#UI[app:List]{source:"chats",item:"chat_card",tab:"chats"}',
                        '#UI[app:List]{source:"contacts",item:"contact_card",tab:"contacts"}',
                        '#UI[app:Card]{title:"发现 AI 工具",subtitle:"探索更多玩法",tab:"discover"}',
                        '#UI[app:Card]{title:"我的资料",subtitle:"查看个人信息",tab:"me"}',
                        '#UI[app:ChatWindow]{title:"对话窗口",input:"on"}',
                    ]
                elif landing_mode:
                    final_lines = [
                        final_lines[0] if final_lines else "^SYS[BrandSite]",
                        "#PROFILE[landing]",
                        "#LIB[tailwind]",
                        "@PAGE[Home,/]",
                        '#UI[landing:Header]{brand:"Nova AI",links:"Features|Pricing|Contact"}',
                        '#UI[landing:Hero]{title:"AI 驱动的高效工作平台",subtitle:"帮助团队更快完成复杂任务",cta_primary:"立即体验",cta_secondary:"查看介绍"}',
                        '#UI[landing:FeatureGrid]{title:"核心能力",items:"快速生成|流程自动化|更低成本|可扩展"}',
                        '#UI[landing:Testimonial]{title:"用户评价",items:"部署更快|协作更顺畅|上线效率提升"}',
                        '#UI[landing:CTA]{title:"现在开始使用",button:"免费开始"}',
                        '#UI[landing:Footer]{brand:"Nova AI",links:"About|Pricing|Contact"}',
                        "@PAGE[About,/about]",
                        '#UI[landing:Hero]{title:"关于我们",subtitle:"我们专注于 AI 产品与效率系统"}',
                        "@PAGE[Features,/features]",
                        '#UI[landing:FeatureGrid]{title:"功能介绍",items:"智能生成|模板能力|多场景支持|低成本交付"}',
                        "@PAGE[Pricing,/pricing]",
                        '#UI[landing:Pricing]{title:"价格方案",plans:"基础版|专业版|企业版"}',
                        "@PAGE[Contact,/contact]",
                        '#UI[landing:Contact]{title:"联系我们",fields:"name|email|message"}',
                    ]
                elif ecom_mode:
                    final_lines = [
                        final_lines[0] if final_lines else "^SYS[ChinaShopLite]",
                        "#PROFILE[ecom_min]",
                        "#LIB[tailwind]",
                        ">DB_TABLE[products]{id:str,title:str,price:int,sales:int,image:str,shop_id:str,shop_name:str,category:str,tag:str,detail:text}",
                        ">DB_TABLE[carts]{item_id:str,product_id:str,title:str,price:int,quantity:int,image:str,tag:str}",
                        ">DB_TABLE[orders]{order_id:str,total:int,status:str,address:str,items:text}",
                        "@API[GET,/api/products]{>DB_SEL[products]}",
                        "@API[GET,/api/cart]{>DB_SEL[carts]}",
                        "@API[POST,/api/cart/add]{>DB_INS[carts]}",
                        "@API[POST,/api/order/submit]{>DB_INS[orders]}",
                        "@PAGE[Home,/]",
                        "#UI[ecom:Header]{brand:\"橙购商城\",search:\"on\",cart:\"on\"}",
                        "#UI[ecom:Banner]{title:\"限时优惠\",subtitle:\"爆款推荐\",theme:\"orange_red\"}",
                        "#UI[ecom:CategoryNav]{items:\"女装|家电|鞋靴|家居|数码|食品\"}",
                        "#UI[ecom:ProductGrid]{source:\"/api/products\",sections:\"热销商品|推荐商品\",mock_count:\"12\"}",
                        "@PAGE[Product,/product/:id]",
                        "#UI[ecom:ProductDetail]{source:\"/api/products\",actions:\"add_cart|buy_now\"}",
                        "@PAGE[Cart,/cart]",
                        "#UI[ecom:CartPanel]{source:\"/api/cart\",checkout:\"/checkout\"}",
                        "@PAGE[Checkout,/checkout]",
                        "#UI[ecom:CheckoutPanel]{submit:\"/api/order/submit\",effect:\"loading|success|clear_cart|go_home\"}",
                        "@PAGE[Category,/category/:name]",
                        "#UI[ecom:CategoryGrid]{source:\"/api/products\"}",
                        "@PAGE[Shop,/shop/:id]",
                        "#UI[ecom:ShopHeader]{source:\"/api/products\"}",
                        "#UI[ecom:ShopProductGrid]{source:\"/api/products\"}",
                        "@PAGE[Search,/search]",
                        "#UI[ecom:SearchResultGrid]{source:\"/api/products\"}",
                    ]
                    if include_after_sales_mode:
                        final_lines.extend(
                            [
                                "#PROFILE[after_sales]",
                                "@PAGE[AfterSales,/after-sales]",
                                "#UI[ecom:AfterSalesEntry]{title:\"售后服务中心\"}",
                            ]
                        )
                elif after_sales_mode:
                    final_lines = [
                        final_lines[0] if final_lines else "^SYS[AfterSalesLite]",
                        "#PROFILE[after_sales]",
                        "@PAGE[AfterSales,/after-sales]",
                        "#UI[ecom:AfterSalesEntry]{title:\"售后服务中心\"}",
                    ]
                else:
                    final_lines = [
                        final_lines[0] if final_lines else "^SYS[AutoProject]",
                        ">DB_TABLE[users]{username:str,pwd:str}",
                        "@API[AUTH,/api/login]{>DB_AUTH[users]}",
                        "@PAGE[Home,/]",
                    ]

            after_count = len(final_lines)
            kept_lines = (1 if sys_seen else 0) + len(sanitized_body_lines)
            dropped_count = max(before_count - kept_lines, 0)
            return {
                "text": "\n".join(final_lines).strip(),
                "before_lines": before_count,
                "after_lines": after_count,
                "dropped_lines": dropped_count,
                "fallback_applied": fallback_applied,
            }

        def _request_and_process(user_prompt: str) -> dict:
            start_ts = time.perf_counter()
            import asyncio

            async def _do_request() -> httpx.Response:
                async with httpx.AsyncClient(timeout=llm_timeout) as client:
                    return await client.post(
                        chat_url,
                        headers={
                            "Authorization": f"Bearer {llm_api_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": llm_model,
                            "messages": [
                                {
                                    "role": "system",
                                    "content": strict_system_prompt,
                                },
                                {"role": "user", "content": user_prompt},
                            ],
                            "temperature": llm_temperature,
                            "max_tokens": 800,
                        },
                    )

            response = asyncio.run(_do_request())
            elapsed_ms = int((time.perf_counter() - start_ts) * 1000)
            if response.status_code != 200:
                print(f"LLM_REQUEST_MS={elapsed_ms}")
                print("LLM_RESPONSE_CHARS=0")
                print("AIL_LINES=0")
                return {
                    "ok": False,
                    "error": f"LLM request failed: {response.status_code} {response.text}",
                    "ail_text": "",
                }

            data = response.json()
            raw_ail = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )
            cleaned = _clean_ail_output(str(raw_ail))
            raw_lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
            last_line = raw_lines[-1] if raw_lines else ""
            has_unclosed_bracket = last_line.count("[") > last_line.count("]")
            has_unclosed_brace = last_line.count("{") > last_line.count("}")
            has_unclosed_pairs = has_unclosed_bracket or has_unclosed_brace

            lines = raw_lines
            if lines and has_unclosed_pairs:
                lines = lines[:-1]
            lines, sys_before, sys_after = _normalize_sys_line(lines)
            ail_text = "\n".join(lines).strip()
            ail_lines = [line for line in ail_text.splitlines() if line.strip()]
            ail_line_count = len(ail_lines)
            ail_last_line = ail_lines[-1] if ail_lines else ""

            print(f"LLM_REQUEST_MS={elapsed_ms}")
            print(f"LLM_RESPONSE_CHARS={len(ail_text)}")
            print(f"AIL_LINES={ail_line_count}")
            sys_before_log = sys_before.replace('"', '\\"')
            sys_after_log = sys_after.replace('"', '\\"')
            print(f'SYS_LINE_BEFORE="{sys_before_log}"')
            print(f'SYS_LINE_AFTER="{sys_after_log}"')
            return {
                "ok": True,
                "error": "",
                "ail_text": ail_text,
                "ail_lines_count": ail_line_count,
                "ail_last_line": ail_last_line,
            }

        if app_mode:
            phase1_prompt = (
                "你只输出 AIL 骨架（8-14行），必须包含且仅包含以下结构：\n"
                "1) ^SYS[SystemName]\n"
                "2) #PROFILE[app_min]\n"
                "3) #LIB[tailwind]\n"
                "4) >DB_TABLE[chats]{id:str,title:str,last_message:str,time:str,unread:int}\n"
                "5) >DB_TABLE[contacts]{id:str,name:str,status:str}\n"
                "6) >DB_TABLE[user_profile]{id:str,name:str,bio:text}\n"
                "7) @PAGE[Home,/] + #UI[app:TopBar]/#UI[app:BottomTab]/#UI[app:List]/#UI[app:Card]/#UI[app:ChatWindow]\n"
                "禁止输出电商页面、禁止输出 landing 页面、禁止输出登录页、禁止输出 JSON/解释。"
            )
        elif landing_mode:
            phase1_prompt = (
                "你只输出 AIL 骨架（10-18行），必须包含且仅包含以下结构：\n"
                "1) ^SYS[SystemName]\n"
                "2) #PROFILE[landing]\n"
                "3) #LIB[tailwind]\n"
                "4) @PAGE[Home,/] + #UI[landing:Header]/#UI[landing:Hero]/#UI[landing:FeatureGrid]/#UI[landing:Testimonial]/#UI[landing:CTA]/#UI[landing:Footer]\n"
                "5) @PAGE[About,/about] + #UI[landing:Hero]\n"
                "6) @PAGE[Features,/features] + #UI[landing:FeatureGrid]\n"
                "7) @PAGE[Pricing,/pricing] + #UI[landing:Pricing]\n"
                "8) @PAGE[Contact,/contact] + #UI[landing:Contact]\n"
                "禁止输出电商页面、禁止输出购物车/订单 API、禁止输出登录页、禁止输出 JSON/解释。"
            )
        elif ecom_mode:
            phase1_prompt = (
                "你只输出 AIL 骨架（22-32行），必须包含且仅包含以下结构：\n"
                "1) ^SYS[SystemName]\n"
                "2) #PROFILE[ecom_min]\n"
                "3) #LIB[tailwind]\n"
                "4) >DB_TABLE[products]{id:str,title:str,price:int,sales:int,image:str,shop_id:str,shop_name:str,category:str,tag:str,detail:text}\n"
                "5) >DB_TABLE[carts]{item_id:str,product_id:str,title:str,price:int,quantity:int,image:str,tag:str}\n"
                "6) >DB_TABLE[orders]{order_id:str,total:int,status:str,address:str,items:text}\n"
                "7) @API[GET,/api/products]{>DB_SEL[products]}\n"
                "8) @API[GET,/api/cart]{>DB_SEL[carts]}\n"
                "9) @API[POST,/api/cart/add]{>DB_INS[carts]}\n"
                "10) @API[POST,/api/order/submit]{>DB_INS[orders]}\n"
                "11) @PAGE[Home,/] + #UI[ecom:Header]/#UI[ecom:Banner]/#UI[ecom:CategoryNav]/#UI[ecom:ProductGrid]\n"
                "12) @PAGE[Product,/product/:id] + #UI[ecom:ProductDetail]\n"
                "13) @PAGE[Cart,/cart] + #UI[ecom:CartPanel]\n"
                "14) @PAGE[Checkout,/checkout] + #UI[ecom:CheckoutPanel]\n"
                "15) @PAGE[Category,/category/:name] + #UI[ecom:CategoryGrid]\n"
                "16) @PAGE[Shop,/shop/:id] + #UI[ecom:ShopHeader]/#UI[ecom:ShopProductGrid]\n"
                "17) @PAGE[Search,/search] + #UI[ecom:SearchResultGrid]\n"
                + ("18) #PROFILE[after_sales] + @PAGE[AfterSales,/after-sales] + #UI[ecom:AfterSalesEntry]\n" if include_after_sales_mode else "")
                + "禁止输出登录页、403页、tools 表、DB_REL、解释、JSON。"
            )
        elif after_sales_mode:
            phase1_prompt = (
                "你只输出 AIL 骨架（4-8行），必须包含且仅包含以下结构：\n"
                "1) ^SYS[SystemName]\n"
                "2) #PROFILE[after_sales]\n"
                "3) @PAGE[AfterSales,/after-sales]\n"
                "4) #UI[ecom:AfterSalesEntry]{title:\"售后服务中心\"}\n"
                "禁止输出电商主站页面、禁止输出登录页、禁止输出 JSON/解释。"
            )
        else:
            phase1_prompt = (
                "你只输出 AIL 骨架（12-18行），必须包含且仅包含以下结构（可以调整 SystemName/表名/路径，但结构不许缺）：\n"
                "1) ^SYS[SystemName]\n"
                "2) >DB_TABLE[users]{username:str,pwd:str}\n"
                "3) @API[AUTH,/api/login]{>DB_AUTH[users]}\n"
                "4) @API[POST,/api/register]{>DB_INS[users]}\n"
                "5) @API[GET,/api/me]{>DB_SEL[users]*AUTH}\n"
                "6) @PAGE[Home,/]\n"
                "7) @PAGE[Login,/login]\n"
                "8) @PAGE[Forbidden,/403]\n"
                "禁止输出 tools 表、禁止输出 DB_REL、禁止输出解释、禁止输出 JSON。"
            )

        phase1_result = _request_and_process(phase1_prompt)
        if not phase1_result["ok"]:
            return jsonify({"status": "error", "error": phase1_result["error"]}), 500

        phase1_sanitize = sanitize_ail_v5(phase1_result.get("ail_text", ""))
        print(f"SANITIZE_BEFORE_LINES={phase1_sanitize['before_lines']}")
        print(f"SANITIZE_AFTER_LINES={phase1_sanitize['after_lines']}")
        print(f"SANITIZE_DROPPED_LINES={phase1_sanitize['dropped_lines']}")
        if phase1_sanitize["fallback_applied"]:
            print("SANITIZE_FALLBACK_APPLIED=1")

        skeleton_ail = phase1_sanitize["text"]
        skeleton_lines = [line for line in skeleton_ail.splitlines() if line.strip()]
        phase1_profiles = _extract_profiles_from_lines(skeleton_lines)
        if phase1_profiles:
            explicit_profile_mode, ecom_mode, after_sales_mode, include_after_sales_mode, landing_mode, app_mode = _resolve_profile_modes(
                phase1_profiles,
                fallback_ecom_mode,
                fallback_after_sales_mode,
                fallback_landing_mode,
            )
        if app_mode:
            min_phase1_lines = 7
        elif landing_mode:
            min_phase1_lines = 8
        elif ecom_mode or not after_sales_mode:
            min_phase1_lines = 8
        else:
            min_phase1_lines = 4
        if len(skeleton_lines) < min_phase1_lines:
            print("AIL_PHASE1_FALLBACK=1")
            if app_mode:
                skeleton_lines = [
                    "^SYS[AIChatMini]",
                    "#PROFILE[app_min]",
                    "#LIB[tailwind]",
                    ">DB_TABLE[chats]{id:str,title:str,last_message:str,time:str,unread:int}",
                    ">DB_TABLE[contacts]{id:str,name:str,status:str}",
                    ">DB_TABLE[user_profile]{id:str,name:str,bio:text}",
                    "@PAGE[Home,/]",
                    '#UI[app:TopBar]{title:"AI Chat"}',
                    '#UI[app:BottomTab]{items:"chats|contacts|discover|me"}',
                    '#UI[app:List]{source:"chats",item:"chat_card",tab:"chats"}',
                    '#UI[app:List]{source:"contacts",item:"contact_card",tab:"contacts"}',
                    '#UI[app:Card]{title:"发现 AI 工具",subtitle:"探索更多玩法",tab:"discover"}',
                    '#UI[app:Card]{title:"我的资料",subtitle:"查看个人信息",tab:"me"}',
                    '#UI[app:ChatWindow]{title:"对话窗口",input:"on"}',
                ]
            elif landing_mode:
                skeleton_lines = [
                    "^SYS[BrandSite]",
                    "#PROFILE[landing]",
                    "#LIB[tailwind]",
                    "@PAGE[Home,/]",
                    '#UI[landing:Header]{brand:"Nova AI",links:"Features|Pricing|Contact"}',
                    '#UI[landing:Hero]{title:"AI 驱动的高效工作平台",subtitle:"帮助团队更快完成复杂任务",cta_primary:"立即体验",cta_secondary:"查看介绍"}',
                    '#UI[landing:FeatureGrid]{title:"核心能力",items:"快速生成|流程自动化|更低成本|可扩展"}',
                    '#UI[landing:Testimonial]{title:"用户评价",items:"部署更快|协作更顺畅|上线效率提升"}',
                    '#UI[landing:CTA]{title:"现在开始使用",button:"免费开始"}',
                    '#UI[landing:Footer]{brand:"Nova AI",links:"About|Pricing|Contact"}',
                    "@PAGE[About,/about]",
                    '#UI[landing:Hero]{title:"关于我们",subtitle:"我们专注于 AI 产品与效率系统"}',
                    "@PAGE[Features,/features]",
                    '#UI[landing:FeatureGrid]{title:"功能介绍",items:"智能生成|模板能力|多场景支持|低成本交付"}',
                    "@PAGE[Pricing,/pricing]",
                    '#UI[landing:Pricing]{title:"价格方案",plans:"基础版|专业版|企业版"}',
                    "@PAGE[Contact,/contact]",
                    '#UI[landing:Contact]{title:"联系我们",fields:"name|email|message"}',
                ]
            elif ecom_mode:
                skeleton_lines = [
                    "^SYS[ChinaShopLite]",
                    "#PROFILE[ecom_min]",
                    "#LIB[tailwind]",
                    ">DB_TABLE[products]{id:str,title:str,price:int,sales:int,image:str,shop_id:str,shop_name:str,category:str,tag:str,detail:text}",
                    ">DB_TABLE[carts]{item_id:str,product_id:str,title:str,price:int,quantity:int,image:str,tag:str}",
                    ">DB_TABLE[orders]{order_id:str,total:int,status:str,address:str,items:text}",
                    "@API[GET,/api/products]{>DB_SEL[products]}",
                    "@API[GET,/api/cart]{>DB_SEL[carts]}",
                    "@API[POST,/api/cart/add]{>DB_INS[carts]}",
                    "@API[POST,/api/order/submit]{>DB_INS[orders]}",
                    "@PAGE[Home,/]",
                    "#UI[ecom:Header]{brand:\"橙购商城\",search:\"on\",cart:\"on\",orders:\"on\",service:\"on\"}",
                    "#UI[ecom:Banner]{title:\"限时优惠\",subtitle:\"爆款推荐\",theme:\"orange_red\"}",
                    "#UI[ecom:CategoryNav]{items:\"女装|家电|鞋靴|家居|数码|食品\"}",
                    "#UI[ecom:ProductGrid]{source:\"/api/products\",sections:\"热销商品|推荐商品\",mock_count:\"12\"}",
                    "@PAGE[Product,/product/:id]",
                    "#UI[ecom:ProductDetail]{source:\"/api/products\",actions:\"add_cart|buy_now\"}",
                    "@PAGE[Cart,/cart]",
                    "#UI[ecom:CartPanel]{source:\"/api/cart\",checkout:\"/checkout\"}",
                    "@PAGE[Checkout,/checkout]",
                    "#UI[ecom:CheckoutPanel]{submit:\"/api/order/submit\",effect:\"loading|success|clear_cart|go_home\"}",
                    "@PAGE[Category,/category/:name]",
                    "#UI[ecom:CategoryGrid]{source:\"/api/products\"}",
                    "@PAGE[Shop,/shop/:id]",
                    "#UI[ecom:ShopHeader]{source:\"/api/products\"}",
                    "#UI[ecom:ShopProductGrid]{source:\"/api/products\"}",
                    "@PAGE[Search,/search]",
                    "#UI[ecom:SearchResultGrid]{source:\"/api/products\"}",
                ]
                if include_after_sales_mode:
                    skeleton_lines.extend(
                        [
                            "#PROFILE[after_sales]",
                            "@PAGE[AfterSales,/after-sales]",
                            "#UI[ecom:AfterSalesEntry]{title:\"售后服务中心\"}",
                        ]
                    )
            elif after_sales_mode:
                skeleton_lines = [
                    "^SYS[AfterSalesLite]",
                    "#PROFILE[after_sales]",
                    "@PAGE[AfterSales,/after-sales]",
                    "#UI[ecom:AfterSalesEntry]{title:\"售后服务中心\"}",
                ]
            else:
                skeleton_lines = [
                    "^SYS[AutoProject]",
                    ">DB_TABLE[users]{username:str,pwd:str}",
                    "@API[AUTH,/api/login]{>DB_AUTH[users]}",
                    "@API[POST,/api/register]{>DB_INS[users]}",
                    "@API[GET,/api/me]{>DB_SEL[users]*AUTH}",
                    "@PAGE[Home,/]",
                    "@PAGE[Login,/login]",
                    "@PAGE[Forbidden,/403]",
                ]
            skeleton_ail = "\n".join(skeleton_lines)
        print(f"AIL_PHASE1_LINES={len(skeleton_lines)}")

        phase2_prompt = (
            "下面是已确定的 AIL 骨架，你只能在其后追加新行，禁止修改或删除骨架已有行：\n"
            f"{skeleton_ail}\n\n"
            "用户需求：\n"
            f"{prompt_text}\n\n"
            "只允许追加：\n"
            "- 新的 >DB_TABLE[...] 行（字段类型仅 str/int/text/datetime/bool/float）\n"
            "- 新的 @API[...] 行（仅允许 >DB_AUTH / >DB_INS / >DB_SEL）\n"
            "- 新的 @PAGE[...] 行\n"
            + ("- 新的 #UI[lib:Component]{...} 行（必须紧跟在对应 @PAGE 后）\n" if (app_mode or landing_mode or ecom_mode or after_sales_mode) else "")
            + "禁止输出 JSON/解释/代码块。\n"
            + "输出必须是完整 AIL 纯文本。"
        )

        phase2_result = _request_and_process(phase2_prompt)
        if not phase2_result["ok"]:
            return jsonify({"status": "error", "error": phase2_result["error"]}), 500

        phase2_sanitize = sanitize_ail_v5(phase2_result.get("ail_text", ""))
        print(f"SANITIZE_BEFORE_LINES={phase2_sanitize['before_lines']}")
        print(f"SANITIZE_AFTER_LINES={phase2_sanitize['after_lines']}")
        print(f"SANITIZE_DROPPED_LINES={phase2_sanitize['dropped_lines']}")
        if phase2_sanitize["fallback_applied"]:
            print("SANITIZE_FALLBACK_APPLIED=1")

        phase2_lines = [line for line in phase2_sanitize["text"].splitlines() if line.strip()]
        print(f"AIL_PHASE2_LINES={len(phase2_lines)}")
        phase2_profiles = _extract_profiles_from_lines(phase2_lines)
        if phase2_profiles:
            explicit_profile_mode, ecom_mode, after_sales_mode, include_after_sales_mode, landing_mode, app_mode = _resolve_profile_modes(
                phase2_profiles,
                fallback_ecom_mode,
                fallback_after_sales_mode,
                fallback_landing_mode,
            )

        skeleton_lines = [line for line in skeleton_ail.splitlines() if line.strip()]
        skeleton_tables: set[str] = set()
        if app_mode and explicit_profile_mode:
            allowed_tables: set[str] = {"chats", "contacts", "user_profile"}
        elif landing_mode and explicit_profile_mode:
            allowed_tables: set[str] = set()
        elif ecom_mode:
            allowed_tables: set[str] = {"products", "carts", "orders"}
        elif after_sales_mode and explicit_profile_mode:
            allowed_tables = set()
        else:
            allowed_tables = {"users"}
        skeleton_api_paths: set[str] = set()
        for line in skeleton_lines:
            table_match = re.match(r"^>DB_TABLE\[([A-Za-z_][A-Za-z0-9_]*)\]\{", line)
            if table_match:
                table_name = table_match.group(1)
                skeleton_tables.add(table_name)
                allowed_tables.add(table_name.lower())
            api_match = re.match(r"^@API\[[A-Z]+,([^\]]+)\]\{", line)
            if api_match:
                skeleton_api_paths.add(api_match.group(1).strip())

        for table_name in re.findall(r"([A-Za-z0-9_]+)\s*表", prompt_text):
            cleaned = re.sub(r"[^A-Za-z0-9_]", "", table_name).lower()
            if cleaned:
                allowed_tables.add(cleaned)
        for table_name in re.findall(r"DB_(?:TABLE|INS|SEL)\[([A-Za-z0-9_]+)\]", prompt_text, flags=re.I):
            cleaned = re.sub(r"[^A-Za-z0-9_]", "", table_name).lower()
            if cleaned:
                allowed_tables.add(cleaned)
        if "用户表" in prompt_text:
            allowed_tables.add("users")
        if "订单表" in prompt_text:
            allowed_tables.add("orders")
        if "工具表" in prompt_text:
            allowed_tables.add("tools")
        if "文章表" in prompt_text:
            allowed_tables.add("posts")
        if app_mode:
            allowed_tables.update({"chats", "contacts", "user_profile"})
        if ecom_mode:
            allowed_tables.update({"products", "carts", "orders"})

        if app_mode and explicit_profile_mode:
            allowed_api_paths: set[str] = set()
        elif landing_mode and explicit_profile_mode:
            allowed_api_paths: set[str] = set()
        elif ecom_mode:
            allowed_api_paths: set[str] = {"/api/products", "/api/cart", "/api/cart/add", "/api/order/submit"}
        elif after_sales_mode and explicit_profile_mode:
            allowed_api_paths = set()
        else:
            allowed_api_paths = {"/api/login", "/api/register", "/api/me"}
        for path in re.findall(r"/api/[A-Za-z0-9_/-]+", prompt_text):
            if path.startswith("/") and len(path) <= 60:
                allowed_api_paths.add(path)

        phase2_drop_dup_table = 0
        phase2_drop_extra_api = 0
        api_drop_not_allowed_count = 0
        filtered_phase2_lines: list[str] = []
        for line in phase2_lines:
            table_match = re.match(r"^>DB_TABLE\[([A-Za-z_][A-Za-z0-9_]*)\]\{", line)
            if table_match and table_match.group(1) in skeleton_tables:
                phase2_drop_dup_table += 1
                continue

            api_match = re.match(r"^@API\[[A-Z]+,([^\]]+)\]\{", line)
            if api_match:
                api_path = api_match.group(1).strip()
                if api_path not in allowed_api_paths:
                    api_drop_not_allowed_count += 1
                    phase2_drop_extra_api += 1
                    continue

            filtered_phase2_lines.append(line)

        print(f"PHASE2_DROP_DUP_TABLE={phase2_drop_dup_table}")
        print(f"PHASE2_DROP_EXTRA_API={phase2_drop_extra_api}")

        merged_lines = [line for line in skeleton_ail.splitlines() if line.strip()]
        seen = set(merged_lines)
        for line in filtered_phase2_lines:
            if line.startswith("^SYS["):
                continue
            if line in seen:
                continue
            merged_lines.append(line)
            seen.add(line)

        db_table_drop_not_allowed_count = 0
        api_drop_table_not_allowed_count = 0
        rel_drop_table_not_allowed_count = 0
        db_table_filtered_lines: list[str] = []
        for line in merged_lines:
            m_table = re.match(r"^>DB_TABLE\[([A-Za-z_][A-Za-z0-9_]*)\]\{", line)
            if m_table:
                table_name = m_table.group(1).lower()
                if table_name not in allowed_tables:
                    db_table_drop_not_allowed_count += 1
                    continue
            m_api_ref = re.match(r"^@API\[[A-Z]+,[^\]]+\]\{(.*)\}$", line)
            if m_api_ref:
                action_body = m_api_ref.group(1)
                action_table_match = re.search(r">DB_(?:AUTH|INS|SEL)\[([A-Za-z0-9_]+)\]", action_body)
                if action_table_match:
                    action_table = action_table_match.group(1).lower()
                    if action_table not in allowed_tables:
                        api_drop_table_not_allowed_count += 1
                        continue
            m_rel = re.match(r"^>DB_REL\[([A-Za-z0-9_]+)\(1\)->([A-Za-z0-9_]+)\(N\)\]$", line)
            if m_rel:
                left_table = m_rel.group(1).lower()
                right_table = m_rel.group(2).lower()
                if left_table not in allowed_tables or right_table not in allowed_tables:
                    rel_drop_table_not_allowed_count += 1
                    continue
            db_table_filtered_lines.append(line)
        merged_lines = db_table_filtered_lines
        print("DB_TABLE_FILTER=1")
        print(f"DB_TABLE_DROP_NOT_ALLOWED_COUNT={db_table_drop_not_allowed_count}")
        print(f"DB_TABLE_ALLOWED_COUNT={len(allowed_tables)}")
        print("DB_REF_FILTER=1")
        print(f"API_DROP_TABLE_NOT_ALLOWED_COUNT={api_drop_table_not_allowed_count}")
        print(f"REL_DROP_TABLE_NOT_ALLOWED_COUNT={rel_drop_table_not_allowed_count}")

        users_schema_forced = False
        users_schema_before = ""
        users_schema_after = ""
        for i, line in enumerate(merged_lines):
            m_users = re.match(r"^>DB_TABLE\[users\]\{(.*)\}$", line)
            if not m_users:
                continue
            fields_blob = m_users.group(1)
            field_order: list[str] = []
            field_types: dict[str, str] = {}
            for item in [x.strip() for x in fields_blob.split(",") if x.strip()]:
                if ":" not in item:
                    continue
                key_raw, type_raw = item.split(":", 1)
                key = re.sub(r"[^A-Za-z0-9_]", "", key_raw.strip().lower())
                if not key or key in field_types:
                    continue
                typ = re.sub(r"\(.*?\)", "", type_raw.strip().lower())
                typ = re.sub(r"[^a-z0-9_]", "", typ)
                field_order.append(key)
                field_types[key] = typ

            if "username" not in field_types:
                field_order.append("username")
                field_types["username"] = "str"
            else:
                field_types["username"] = "str"
            if "pwd" not in field_types:
                field_order.append("pwd")
                field_types["pwd"] = "str"
            else:
                field_types["pwd"] = "str"

            rebuilt_fields = ",".join(f"{name}:{field_types[name]}" for name in field_order)
            rebuilt_line = f">DB_TABLE[users]{{{rebuilt_fields}}}"
            if rebuilt_line != line:
                if not users_schema_forced:
                    users_schema_before = line
                    users_schema_after = rebuilt_line
                users_schema_forced = True
                merged_lines[i] = rebuilt_line

        if users_schema_forced:
            print("USERS_SCHEMA_FORCED=1")
            print(f'USERS_SCHEMA_BEFORE="{users_schema_before}"')
            print(f'USERS_SCHEMA_AFTER="{users_schema_after}"')

        if app_mode and explicit_profile_mode:
            canonical_api_lines = {}
        elif landing_mode and explicit_profile_mode:
            canonical_api_lines = {}
        elif ecom_mode:
            canonical_api_lines = {
                "/api/products": "@API[GET,/api/products]{>DB_SEL[products]}",
                "/api/cart": "@API[GET,/api/cart]{>DB_SEL[carts]}",
                "/api/cart/add": "@API[POST,/api/cart/add]{>DB_INS[carts]}",
                "/api/order/submit": "@API[POST,/api/order/submit]{>DB_INS[orders]}",
            }
        elif after_sales_mode and explicit_profile_mode:
            canonical_api_lines = {}
        else:
            canonical_api_lines = {
                "/api/login": "@API[AUTH,/api/login]{>DB_AUTH[users]}",
                "/api/register": "@API[POST,/api/register]{>DB_INS[users]}",
                "/api/me": "@API[GET,/api/me]{>DB_SEL[users]*AUTH}",
            }
        api_fix_count = 0
        for path, canonical_line in canonical_api_lines.items():
            found_idx = -1
            for idx, line in enumerate(merged_lines):
                m_api = re.match(r"^@API\[([A-Z]+),([^\]]+)\]\{(.*)\}$", line)
                if not m_api:
                    continue
                line_path = m_api.group(2).strip()
                if line_path == path:
                    found_idx = idx
                    break
            if found_idx >= 0:
                if merged_lines[found_idx] != canonical_line:
                    merged_lines[found_idx] = canonical_line
                    api_fix_count += 1
            else:
                merged_lines.append(canonical_line)
                api_fix_count += 1

        deduped_lines: list[str] = []
        seen_api_paths: set[str] = set()
        api_drop_dup_count = 0
        for line in merged_lines:
            m_api = re.match(r"^@API\[([A-Z]+),([^\]]+)\]\{(.*)\}$", line)
            if not m_api:
                deduped_lines.append(line)
                continue
            api_path = m_api.group(2).strip()
            if api_path not in allowed_api_paths:
                api_drop_not_allowed_count += 1
                continue
            if api_path in seen_api_paths:
                api_drop_dup_count += 1
                continue
            seen_api_paths.add(api_path)
            deduped_lines.append(line)
        merged_lines = deduped_lines

        if api_fix_count > 0 or api_drop_dup_count > 0 or api_drop_not_allowed_count > 0:
            print("API_CANONICAL_FORCED=1")
        print(f"API_DROP_DUP_COUNT={api_drop_dup_count}")
        print(f"API_FIX_COUNT={api_fix_count}")
        print(f"API_DROP_NOT_ALLOWED_COUNT={api_drop_not_allowed_count}")

        page_fix_count = 0
        page_drop_dup_count = 0

        def _normalize_page_name(name: str) -> str:
            cleaned = (name or "").strip().replace(" ", "_")
            cleaned = re.sub(r"[^A-Za-z0-9_]", "", cleaned)
            return cleaned or "Page"

        def _normalize_page_path(path: str) -> str:
            normalized = (path or "").strip()
            if not normalized.startswith("/"):
                normalized = "/" + normalized.lstrip("/")
            normalized = re.sub(r"[^A-Za-z0-9_/:-]", "", normalized)
            normalized = re.sub(r"/{2,}", "/", normalized)
            if not normalized:
                normalized = "/"
            if not normalized.startswith("/"):
                normalized = "/" + normalized
            return normalized

        non_page_lines: list[str] = []
        page_blocks: list[dict[str, Any]] = []
        current_page_idx: int | None = None

        for line in merged_lines:
            if line.startswith("@PAGE["):
                m_page = re.match(r"^@PAGE\[\s*([^,\]]+)\s*,\s*([^\]]+)\s*\](?:\*ROLE\[[^\]]+\])?\s*$", line)
                if not m_page:
                    page_fix_count += 1
                    current_page_idx = None
                    continue
                page_name = _normalize_page_name(m_page.group(1))
                page_path = _normalize_page_path(m_page.group(2))
                page_blocks.append({"name": page_name, "path": page_path, "ui": []})
                current_page_idx = len(page_blocks) - 1
                continue

            if line.startswith("#UI["):
                ui_match = re.match(r"^#UI\[([^:\]]+):([^\]]+)\]\{(.*)\}\s*$", line, re.S)
                if current_page_idx is None or not ui_match:
                    page_fix_count += 1
                    continue
                source_raw, comp_raw, config_raw = ui_match.groups()
                source = re.sub(r"[^A-Za-z0-9_-]", "", source_raw.strip())
                component = re.sub(r"[^A-Za-z0-9_]", "", comp_raw.strip())
                if not source or not component:
                    page_fix_count += 1
                    continue
                normalized_ui = f"#UI[{source}:{component}]{{{config_raw.strip()}}}"
                page_blocks[current_page_idx]["ui"].append(normalized_ui)
                continue

            current_page_idx = None
            non_page_lines.append(line)

        if app_mode and explicit_profile_mode:
            canonical_pages = [
                ("/", "Home"),
            ]
            allowed_page_paths: set[str] = {"/"}
        elif ecom_mode:
            canonical_pages = [
                ("/", "Home"),
                ("/product/:id", "Product"),
                ("/cart", "Cart"),
                ("/checkout", "Checkout"),
                ("/category/:name", "Category"),
                ("/shop/:id", "Shop"),
                ("/search", "Search"),
            ]
            if include_after_sales_mode:
                canonical_pages.append(("/after-sales", "AfterSales"))
            allowed_page_paths: set[str] = {path for path, _ in canonical_pages}
        elif landing_mode and explicit_profile_mode:
            canonical_pages = [
                ("/", "Home"),
                ("/about", "About"),
                ("/features", "Features"),
                ("/pricing", "Pricing"),
                ("/contact", "Contact"),
            ]
            allowed_page_paths = {path for path, _ in canonical_pages}
        elif after_sales_mode and explicit_profile_mode:
            canonical_pages = [
                ("/after-sales", "AfterSales"),
            ]
            allowed_page_paths = {"/after-sales"}
        else:
            canonical_pages = [
                ("/", "Home"),
                ("/login", "Login"),
                ("/403", "Forbidden"),
            ]
            allowed_page_paths = {"/", "/login", "/403"}

        for path in re.findall(r"/(?:[A-Za-z0-9_:-]+)(?:/(?:[A-Za-z0-9_:-]+))*", prompt_text):
            if path.startswith("/") and len(path) <= 60:
                allowed_page_paths.add(path)

        blocks_by_path: dict[str, dict[str, Any]] = {}
        page_drop_not_allowed_count = 0
        for block in page_blocks:
            page_path = str(block.get("path", "")).strip()
            if page_path in blocks_by_path:
                page_drop_dup_count += 1
                continue
            if page_path not in allowed_page_paths:
                page_drop_not_allowed_count += 1
                continue
            blocks_by_path[page_path] = block

        default_ecom_ui = {
            "/": [
                '#UI[ecom:Header]{brand:"橙购商城",search:"on",cart:"on",orders:"on",service:"on"}',
                '#UI[ecom:Banner]{title:"限时优惠",subtitle:"爆款推荐",theme:"orange_red"}',
                '#UI[ecom:CategoryNav]{items:"女装|家电|鞋靴|家居|数码|食品"}',
                '#UI[ecom:ProductGrid]{source:"/api/products",sections:"热销商品|推荐商品",mock_count:"12",theme:"orange_red"}',
            ],
            "/product/:id": [
                '#UI[ecom:ProductDetail]{source:"/api/products",show:"image|title|price|sales|spec|qty|detail",actions:"add_cart|buy_now"}'
            ],
            "/cart": [
                '#UI[ecom:CartPanel]{source:"/api/cart",actions:"qty_plus|qty_minus|remove",summary:"on",checkout:"/checkout"}'
            ],
            "/checkout": [
                '#UI[ecom:CheckoutPanel]{address_mock:"on",items_source:"/api/cart",submit:"/api/order/submit",effect:"loading|success|clear_cart|go_home"}'
            ],
            "/category/:name": [
                '#UI[ecom:CategoryGrid]{source:"/api/products",title:"分类商品"}'
            ],
            "/shop/:id": [
                '#UI[ecom:ShopHeader]{source:"/api/products",title:"店铺首页"}',
                '#UI[ecom:ShopProductGrid]{source:"/api/products",sections:"店铺商品|店铺推荐"}',
            ],
            "/search": [
                '#UI[ecom:SearchResultGrid]{source:"/api/products",title:"搜索结果"}'
            ],
        }
        if include_after_sales_mode:
            default_ecom_ui["/after-sales"] = [
                '#UI[ecom:AfterSalesEntry]{title:"售后服务中心"}'
            ]
        default_app_ui = {
            "/": [
                '#UI[app:TopBar]{title:"AI Chat"}',
                '#UI[app:BottomTab]{items:"chats|contacts|discover|me"}',
                '#UI[app:List]{source:"chats",item:"chat_card",tab:"chats"}',
                '#UI[app:List]{source:"contacts",item:"contact_card",tab:"contacts"}',
                '#UI[app:Card]{title:"发现 AI 工具",subtitle:"探索更多玩法",tab:"discover"}',
                '#UI[app:Card]{title:"我的资料",subtitle:"查看个人信息",tab:"me"}',
                '#UI[app:ChatWindow]{title:"对话窗口",input:"on"}',
            ],
        }
        default_landing_ui = {
            "/": [
                '#UI[landing:Header]{brand:"Nova AI",links:"Features|Pricing|Contact"}',
                '#UI[landing:Hero]{title:"AI 驱动的高效工作平台",subtitle:"帮助团队更快完成复杂任务",cta_primary:"立即体验",cta_secondary:"查看介绍"}',
                '#UI[landing:FeatureGrid]{title:"核心能力",items:"快速生成|流程自动化|更低成本|可扩展"}',
                '#UI[landing:Testimonial]{title:"用户评价",items:"部署更快|协作更顺畅|上线效率提升"}',
                '#UI[landing:CTA]{title:"现在开始使用",button:"免费开始"}',
                '#UI[landing:Footer]{brand:"Nova AI",links:"About|Pricing|Contact"}',
            ],
            "/about": [
                '#UI[landing:Hero]{title:"关于我们",subtitle:"我们专注于 AI 产品与效率系统"}',
            ],
            "/features": [
                '#UI[landing:FeatureGrid]{title:"功能介绍",items:"智能生成|模板能力|多场景支持|低成本交付"}',
            ],
            "/pricing": [
                '#UI[landing:Pricing]{title:"价格方案",plans:"基础版|专业版|企业版"}',
            ],
            "/contact": [
                '#UI[landing:Contact]{title:"联系我们",fields:"name|email|message"}',
            ],
        }

        final_page_blocks: list[dict[str, Any]] = []
        used_page_paths: set[str] = set()
        for canonical_path, canonical_name in canonical_pages:
            block = blocks_by_path.pop(canonical_path, None)
            if block is None:
                page_fix_count += 1
                block = {"name": canonical_name, "path": canonical_path, "ui": []}
            elif block.get("name") != canonical_name:
                page_fix_count += 1
                block["name"] = canonical_name

            should_inject_default_ui = (
                (app_mode and not block.get("ui"))
                or (landing_mode and not block.get("ui"))
                or (ecom_mode and not block.get("ui"))
                or (
                    after_sales_mode
                    and canonical_path == "/after-sales"
                    and not block.get("ui")
                )
            )
            if should_inject_default_ui:
                if app_mode:
                    block["ui"] = default_app_ui.get(canonical_path, [])
                elif landing_mode:
                    block["ui"] = default_landing_ui.get(canonical_path, [])
                else:
                    block["ui"] = default_ecom_ui.get(canonical_path, [])
                if block["ui"]:
                    page_fix_count += 1

            used_page_paths.add(canonical_path)
            final_page_blocks.append(block)

        if not app_mode and not landing_mode and not ecom_mode and not (after_sales_mode and explicit_profile_mode):
            for page_path, block in blocks_by_path.items():
                if page_path in used_page_paths:
                    page_drop_dup_count += 1
                    continue
                final_page_blocks.append(block)

        rebuilt_page_lines: list[str] = []
        for block in final_page_blocks:
            rebuilt_page_lines.append(f"@PAGE[{block['name']},{block['path']}]")
            rebuilt_page_lines.extend(block.get("ui", []))

        merged_lines = non_page_lines + rebuilt_page_lines
        if page_fix_count > 0 or page_drop_dup_count > 0 or page_drop_not_allowed_count > 0:
            print("PAGE_CANONICAL_FORCED=1")
        print(f"PAGE_DROP_DUP_COUNT={page_drop_dup_count}")
        print(f"PAGE_FIX_COUNT={page_fix_count}")
        print(f"PAGE_DROP_NOT_ALLOWED_COUNT={page_drop_not_allowed_count}")

        dbtable_type_forced_count = 0
        db_drop_non_table_count = 0
        db_sanitize_test_enabled = os.getenv("AIL_SANITIZE_TEST", "0").strip() == "1"
        if db_sanitize_test_enabled:
            print("DB_SANITIZE_TEST=1")
            merged_lines = merged_lines + [
                ">DB",
                ">DB_TABLE[Bad]{a:VARCHAR(255),b:JSON,c:UUID}",
            ]
            print("DB_SANITIZE_TEST_INJECTED=2")

        def _map_db_type_final(raw_type: str) -> str:
            t = (raw_type or "").strip().lower()
            t = re.sub(r"\(.*?\)", "", t)
            t = re.sub(r"[^a-z0-9_]", "", t)
            if t == "text":
                return "text"
            if t in {"datetime", "timestamp", "date"}:
                return "datetime"
            if t in {"int", "integer", "bigint", "smallint", "tinyint"}:
                return "int"
            if t in {"float", "double", "decimal", "numeric", "real"}:
                return "float"
            if t in {"bool", "boolean"}:
                return "bool"
            if t in {"varchar", "char", "string", "uuid", "json", "email", "password", "str"}:
                return "str"
            if "varchar" in t or "char" in t or "string" in t:
                return "str"
            return "str"

        db_sanitized_lines: list[str] = []
        for line in merged_lines:
            if line.startswith(">"):
                if line.startswith(">DB_REL["):
                    db_sanitized_lines.append(line)
                    continue
                if not line.startswith(">DB_TABLE["):
                    db_drop_non_table_count += 1
                    continue
                m_table = re.match(r"^>DB_TABLE\[([A-Za-z_][A-Za-z0-9_]*)\]\{(.*)\}$", line)
                if not m_table:
                    db_drop_non_table_count += 1
                    continue
                table_name = re.sub(r"[^A-Za-z0-9_]", "", m_table.group(1).strip())
                if not table_name:
                    table_name = "table"
                fields_blob = m_table.group(2)
                field_order: list[str] = []
                field_types: dict[str, str] = {}
                for item in [x.strip() for x in fields_blob.split(",") if x.strip()]:
                    if ":" not in item:
                        continue
                    key_raw, type_raw = item.split(":", 1)
                    key = re.sub(r"[^a-z0-9_]", "", key_raw.strip().lower())
                    if not key or key in field_types:
                        continue
                    field_order.append(key)
                    field_types[key] = _map_db_type_final(type_raw)
                if not field_order:
                    db_drop_non_table_count += 1
                    continue
                rebuilt_fields = ",".join(f"{name}:{field_types[name]}" for name in field_order)
                rebuilt_line = f">DB_TABLE[{table_name}]{{{rebuilt_fields}}}"
                if rebuilt_line != line:
                    dbtable_type_forced_count += 1
                db_sanitized_lines.append(rebuilt_line)
                continue
            db_sanitized_lines.append(line)
        merged_lines = db_sanitized_lines

        if dbtable_type_forced_count > 0 or db_drop_non_table_count > 0:
            print("DB_SANITIZE_FORCED=1")
        print(f"DBTABLE_TYPE_FORCED_COUNT={dbtable_type_forced_count}")
        print(f"DB_DROP_NON_TABLE_COUNT={db_drop_non_table_count}")

        ail_text = "\n".join(merged_lines).strip()
        print(f"AIL_FINAL_LINES={len(merged_lines)}")

        return jsonify({
            "status": "ok",
            "ail": ail_text,
            "model": llm_model,
            "server_info": {
                "base_url": _resolve_base_url(),
                "pid": os.getpid(),
                "version": "v5",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        })
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/compile', methods=['POST'])
def compile_ail():
    try:
        payload = request.get_json(silent=True) or {}
        response_payload, status_code = _compile_payload(payload)
        return jsonify(response_payload), status_code
    except Exception as e:
        trace = traceback.format_exc()
        print(trace)
        fallback_server_info = {
            "base_url": _resolve_base_url(),
            "pid": os.getpid(),
            "version": "v5",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        return jsonify({"status": "error", "error": str(e), "trace": trace, "server_info": fallback_server_info}), 500


@app.route('/api/v1/compile', methods=['POST'])
def compile_ail_v1():
    try:
        payload = request.get_json(silent=True) or {}
        project_id = str(payload.get("project_id") or "proj_auto")
        client_manifest_version = int(payload.get("client_manifest_version") or 0)
        legacy_payload, status_code = _compile_payload(payload)
        if status_code != 200:
            error_message = legacy_payload.get("error") or legacy_payload.get("message") or "compile failed"
            return jsonify(
                {
                    "status": "error",
                    "error": {
                        "code": "compile_failed",
                        "message": str(error_message),
                        "details": {
                            "server_info": legacy_payload.get("server_info") or {},
                        },
                    },
                }
            ), status_code

        project_root = Path(str(legacy_payload["project_root"])).resolve()
        data = _build_v1_compile_data(
            project_id=project_id,
            project_root=project_root,
            server_info=legacy_payload["server_info"],
            legacy_response=legacy_payload,
            client_manifest_version=client_manifest_version,
        )
        _persist_v1_build_record(data)
        return jsonify({"status": "ok", "data": data}), 200
    except Exception as e:
        trace = traceback.format_exc()
        print(trace)
        fallback_server_info = {
            "base_url": _resolve_base_url(),
            "pid": os.getpid(),
            "version": "v5",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        return jsonify(
            {
                "status": "error",
                "error": {
                    "code": "compile_failed",
                    "message": str(e),
                    "details": {
                        "trace": trace,
                        "server_info": fallback_server_info,
                    },
                },
            }
        ), 500


@app.route('/api/v1/build/<build_id>', methods=['GET'])
def get_v1_build(build_id: str):
    try:
        record = _load_v1_build_record(build_id)
        if not record:
            return jsonify(
                {
                    "status": "error",
                    "error": {
                        "code": "build_not_found",
                        "message": f"Build not found: {build_id}",
                        "details": {},
                    },
                }
            ), 404
        return jsonify({"status": "ok", "data": record}), 200
    except Exception as e:
        trace = traceback.format_exc()
        print(trace)
        return jsonify(
            {
                "status": "error",
                "error": {
                    "code": "build_query_failed",
                    "message": str(e),
                    "details": {"trace": trace},
                },
            }
        ), 500


@app.route('/api/v1/project/<project_id>/builds', methods=['GET'])
def get_v1_project_builds(project_id: str):
    try:
        record = _load_v1_project_record(project_id)
        if not record:
            return jsonify(
                {
                    "status": "error",
                    "error": {
                        "code": "project_not_found",
                        "message": f"Project not found: {project_id}",
                        "details": {},
                    },
                }
            ), 404

        items = list(record.get("items") or [])
        mode = (request.args.get("mode") or "").strip().lower()
        if mode:
            items = [item for item in items if str(item.get("mode") or "").lower() == mode]

        cursor_raw = (request.args.get("cursor") or "").strip()
        start_index = 0
        if cursor_raw:
            try:
                start_index = max(int(cursor_raw), 0)
            except ValueError:
                start_index = 0

        limit_raw = (request.args.get("limit") or "").strip()
        limit = 20
        if limit_raw:
            try:
                limit = max(min(int(limit_raw), 100), 1)
            except ValueError:
                limit = 20

        sliced = items[start_index:start_index + limit]
        next_cursor = None
        if start_index + limit < len(items):
            next_cursor = str(start_index + limit)

        return jsonify(
            {
                "status": "ok",
                "data": {
                    "items": sliced,
                    "next_cursor": next_cursor,
                },
            }
        ), 200
    except Exception as e:
        trace = traceback.format_exc()
        print(trace)
        return jsonify(
            {
                "status": "error",
                "error": {
                    "code": "project_builds_query_failed",
                    "message": str(e),
                    "details": {"trace": trace},
                },
            }
        ), 500


@app.route('/api/v1/project/<project_id>', methods=['GET'])
def get_v1_project(project_id: str):
    try:
        record = _load_v1_project_record(project_id)
        if not record:
            return jsonify(
                {
                    "status": "error",
                    "error": {
                        "code": "project_not_found",
                        "message": f"Project not found: {project_id}",
                        "details": {},
                    },
                }
            ), 404

        data = {
            "project_id": record.get("project_id"),
            "latest_build_id": record.get("latest_build_id"),
            "latest_manifest_version": record.get("latest_manifest_version"),
            "created_at": record.get("created_at"),
            "updated_at": record.get("updated_at"),
        }
        return jsonify({"status": "ok", "data": data}), 200
    except Exception as e:
        trace = traceback.format_exc()
        print(trace)
        return jsonify(
            {
                "status": "error",
                "error": {
                    "code": "project_query_failed",
                    "message": str(e),
                    "details": {"trace": trace},
                },
            }
        ), 500


@app.route('/api/v1/build/<build_id>/artifact', methods=['GET'])
def get_v1_build_artifact(build_id: str):
    try:
        record = _load_v1_build_record(build_id)
        if not record:
            return jsonify(
                {
                    "status": "error",
                    "error": {
                        "code": "build_not_found",
                        "message": f"Build not found: {build_id}",
                        "details": {},
                    },
                }
            ), 404

        descriptor = _build_v1_artifact_descriptor(record)
        if not descriptor:
            return jsonify(
                {
                    "status": "error",
                    "error": {
                        "code": "artifact_not_available",
                        "message": f"Artifact not available for build: {build_id}",
                        "details": {},
                    },
                }
            ), 404

        return jsonify({"status": "ok", "data": descriptor}), 200
    except Exception as e:
        trace = traceback.format_exc()
        print(trace)
        return jsonify(
            {
                "status": "error",
                "error": {
                    "code": "artifact_query_failed",
                    "message": str(e),
                    "details": {"trace": trace},
                },
            }
        ), 500

if __name__ == '__main__':
    port_env = os.getenv("AIL_SERVER_PORT", "5002").strip()
    try:
        port = int(port_env)
    except ValueError:
        port = 5002
    app.config["AIL_PORT"] = port
    print(f"Listening on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port)
