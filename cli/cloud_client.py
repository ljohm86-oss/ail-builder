from __future__ import annotations

import contextlib
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
import sys
from typing import Any
from urllib import error as urllib_error
from urllib import request as urllib_request
from urllib.parse import urlencode

from .context import MANAGED_ROOTS
from .manifest_service import ManifestService
from .source_normalizer import normalize_for_current_compile


class CloudClientError(RuntimeError):
    pass


class AILCloudClient:
    def __init__(self, base_url: str | None = None, timeout_s: float = 60.0) -> None:
        resolved_base_url = base_url or os.getenv("AIL_CLOUD_BASE_URL") or "http://127.0.0.1:5002"
        self.base_url = resolved_base_url.rstrip("/")
        self.timeout_s = timeout_s
        self.manifest_service = ManifestService()
        self.last_generate_info: dict[str, Any] = {}
        self.last_compile_info: dict[str, Any] = {}
        self.last_query_info: dict[str, Any] = {}

    def generate_ail(self, requirement: str) -> str:
        requirement = (requirement or "").strip()
        if not requirement:
            raise CloudClientError("Requirement is empty.")
        self.last_generate_info = {
            "used_fallback": False,
            "fallback_reason": "",
            "base_url": self.base_url,
            "endpoint": "/generate_ail",
            "api_variant": "legacy_generate",
        }
        try:
            response = self._post_json("/generate_ail", {"prompt": requirement})
            ail_text = str(response.get("ail") or "").strip()
            if not ail_text:
                raise CloudClientError("Cloud generator returned empty AIL.")
            return ail_text
        except Exception as exc:
            self.last_generate_info = {
                "used_fallback": True,
                "fallback_reason": str(exc),
                "base_url": self.base_url,
                "endpoint": "/generate_ail",
                "api_variant": "fallback_generate",
            }
            return _fallback_generate_ail(requirement).strip()

    def compile_ail(
        self,
        project_id: str,
        ail_source: str,
        current_manifest: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        normalized = normalize_for_current_compile(ail_source, system_name=_compile_system_name(project_id))
        common_info = {
            "removed_flow": normalized.removed_flow,
            "normalized_ui": normalized.normalized_ui,
            "inserted_sys": normalized.inserted_sys,
            "inserted_sys_name": normalized.inserted_sys_name,
            "warnings": normalized.warnings,
            "base_url": self.base_url,
        }
        manifest_version = int((current_manifest or {}).get("manifest_version", 0) or 0)
        client_build_id = (current_manifest or {}).get("current_build_id") or ""

        compile_attempts = [
            (
                "/api/v1/compile",
                {
                    "project_id": project_id,
                    "mode": "full",
                    "ail_source": normalized.text,
                    "client_manifest_version": manifest_version,
                    "client_build_id": client_build_id,
                    "options": {
                        "include_artifact": False,
                        "dry_run": False,
                    },
                },
                "v1_compile",
            ),
            (
                "/compile",
                {
                    "project_id": project_id,
                    "mode": "full",
                    "ail": normalized.text,
                    "client_manifest_version": manifest_version,
                    "client_build_id": client_build_id,
                },
                "legacy_compile",
            ),
        ]
        response, endpoint, api_variant = self._post_json_candidates(compile_attempts)
        self.last_compile_info = {
            **common_info,
            "endpoint": endpoint,
            "api_variant": api_variant,
        }
        return self._normalize_compile_response(project_id, response, current_manifest or {})

    def get_build(self, build_id: str) -> dict[str, Any]:
        build_id = (build_id or "").strip()
        if not build_id:
            raise CloudClientError("Build id is empty.")
        endpoint = f"/api/v1/build/{build_id}"
        response = self._get_json(endpoint)
        data = response.get("data")
        if not isinstance(data, dict):
            raise CloudClientError("Build query did not return a valid data payload.")
        self.last_query_info = {
            "base_url": self.base_url,
            "endpoint": endpoint,
            "api_variant": "v1_build_query",
        }
        return data

    def get_build_artifact(self, build_id: str) -> dict[str, Any]:
        build_id = (build_id or "").strip()
        if not build_id:
            raise CloudClientError("Build id is empty.")
        endpoint = f"/api/v1/build/{build_id}/artifact"
        response = self._get_json(endpoint)
        data = response.get("data")
        if not isinstance(data, dict):
            raise CloudClientError("Build artifact query did not return a valid data payload.")
        self.last_query_info = {
            "base_url": self.base_url,
            "endpoint": endpoint,
            "api_variant": "v1_build_artifact_query",
        }
        return data

    def get_project(self, project_id: str) -> dict[str, Any]:
        project_id = (project_id or "").strip()
        if not project_id:
            raise CloudClientError("Project id is empty.")
        endpoint = f"/api/v1/project/{project_id}"
        response = self._get_json(endpoint)
        data = response.get("data")
        if not isinstance(data, dict):
            raise CloudClientError("Project query did not return a valid data payload.")
        self.last_query_info = {
            "base_url": self.base_url,
            "endpoint": endpoint,
            "api_variant": "v1_project_query",
        }
        return data

    def get_project_builds(
        self,
        project_id: str,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        mode: str | None = None,
    ) -> dict[str, Any]:
        project_id = (project_id or "").strip()
        if not project_id:
            raise CloudClientError("Project id is empty.")
        params: dict[str, str] = {}
        if limit is not None:
            params["limit"] = str(limit)
        if cursor:
            params["cursor"] = str(cursor)
        if mode:
            params["mode"] = str(mode)
        endpoint = f"/api/v1/project/{project_id}/builds"
        if params:
            endpoint = f"{endpoint}?{urlencode(params)}"
        response = self._get_json(endpoint)
        data = response.get("data")
        if not isinstance(data, dict):
            raise CloudClientError("Project builds query did not return a valid data payload.")
        self.last_query_info = {
            "base_url": self.base_url,
            "endpoint": endpoint,
            "api_variant": "v1_project_builds_query",
        }
        return data

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        if self.base_url == "embedded://local":
            return self._post_json_embedded(path, payload)
        url = f"{self.base_url}{path}"
        req = urllib_request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib_request.urlopen(req, timeout=self.timeout_s) as resp:
                body = resp.read().decode("utf-8")
        except urllib_error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise CloudClientError(f"Cloud API request failed ({exc.code}): {body}") from exc
        except urllib_error.URLError as exc:
            raise CloudClientError(f"Cloud API unavailable at {url}: {exc.reason}") from exc
        data = json.loads(body)
        if data.get("status") != "ok":
            raise CloudClientError(data.get("error") or data.get("message") or "Cloud API returned error status.")
        return data

    def _get_json(self, path: str) -> dict[str, Any]:
        if self.base_url == "embedded://local":
            return self._get_json_embedded(path)
        url = f"{self.base_url}{path}"
        req = urllib_request.Request(
            url,
            headers={"Content-Type": "application/json"},
            method="GET",
        )
        try:
            with urllib_request.urlopen(req, timeout=self.timeout_s) as resp:
                body = resp.read().decode("utf-8")
        except urllib_error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise CloudClientError(f"Cloud API request failed ({exc.code}): {body}") from exc
        except urllib_error.URLError as exc:
            raise CloudClientError(f"Cloud API unavailable at {url}: {exc.reason}") from exc
        data = json.loads(body)
        if data.get("status") != "ok":
            raise CloudClientError(data.get("error") or data.get("message") or "Cloud API returned error status.")
        return data

    def _post_json_candidates(self, attempts: list[tuple[str, dict[str, Any], str]]) -> tuple[dict[str, Any], str, str]:
        errors: list[str] = []
        for path, payload, variant in attempts:
            try:
                return self._post_json(path, payload), path, variant
            except CloudClientError as exc:
                errors.append(f"{variant} via {path}: {exc}")
        joined = " | ".join(errors) if errors else "no compile endpoints attempted"
        raise CloudClientError(f"Cloud compile failed across supported API variants: {joined}")

    def _post_json_embedded(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            from ail_server_v5 import app
        except Exception as exc:
            raise CloudClientError(f"Embedded server import failed: {exc}") from exc
        with app.test_client() as client:
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                response = client.post(path, json=payload)
            data = response.get_json(silent=True) or {}
            if response.status_code >= 400:
                raise CloudClientError(data.get("error") or data.get("message") or f"Embedded request failed: {response.status_code}")
            if data.get("status") != "ok":
                raise CloudClientError(data.get("error") or data.get("message") or "Embedded API returned error.")
            return data

    def _get_json_embedded(self, path: str) -> dict[str, Any]:
        try:
            from ail_server_v5 import app
        except Exception as exc:
            raise CloudClientError(f"Embedded server import failed: {exc}") from exc
        with app.test_client() as client:
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                response = client.get(path)
            data = response.get_json(silent=True) or {}
            if response.status_code >= 400:
                raise CloudClientError(data.get("error") or data.get("message") or f"Embedded request failed: {response.status_code}")
            if data.get("status") != "ok":
                raise CloudClientError(data.get("error") or data.get("message") or "Embedded API returned error.")
            return data

    def _normalize_compile_response(
        self,
        project_id: str,
        response: dict[str, Any],
        current_manifest: dict[str, Any],
    ) -> dict[str, Any]:
        if response.get("data") and response.get("data", {}).get("files"):
            return response["data"]

        project_root_raw = response.get("project_root")
        if not project_root_raw:
            raise CloudClientError("Compile response did not contain project_root or normalized build data.")
        project_root = Path(project_root_raw)
        if not project_root.exists():
            raise CloudClientError(f"Compiled project path does not exist: {project_root}")

        files = self._collect_generated_files(project_root)
        previous_files = ((current_manifest or {}).get("managed_files") or {})
        previous_version = int((current_manifest or {}).get("manifest_version", 0) or 0)
        current_build_id = self._derive_build_id(response)
        current_paths = {item["path"] for item in files}
        previous_paths = set(previous_files.keys())
        deleted_files = sorted(previous_paths - current_paths)
        diff_summary = {
            "added": sum(1 for item in files if item["path"] not in previous_files),
            "updated": sum(
                1
                for item in files
                if item["path"] in previous_files and previous_files[item["path"]].get("sha256") != item["sha256"]
            ),
            "deleted": len(deleted_files),
        }
        manifest = self.manifest_service.build_manifest(project_id, current_build_id, files, previous_version)
        return {
            "build_id": current_build_id,
            "project_id": project_id,
            "created_at": _utc_now(),
            "files": files,
            "deleted_files": deleted_files,
            "manifest": manifest,
            "diff_summary": diff_summary,
            "source_project_root": str(project_root.resolve()),
            "server_response": response,
        }

    def _collect_generated_files(self, project_root: Path) -> list[dict[str, Any]]:
        files: list[dict[str, Any]] = []
        view_root = project_root / "frontend" / "src" / "views"
        if view_root.exists():
            for view_file in sorted(view_root.glob("*.vue")):
                files.append(self._make_file_entry(f"src/views/generated/{view_file.name}", view_file))

        router_root = project_root / "frontend" / "src" / "router"
        if router_root.exists():
            for router_file in sorted(router_root.glob("*.generated.ts")):
                files.append(self._make_file_entry(f"src/router/generated/{router_file.name}", router_file))

        backend_root = project_root / "backend"
        if backend_root.exists():
            for backend_file in sorted(backend_root.rglob("*")):
                if not backend_file.is_file():
                    continue
                if backend_file.name == "ail_data.db" or backend_file.suffix == ".db":
                    continue
                if "__pycache__" in backend_file.parts or backend_file.suffix == ".pyc":
                    continue
                relative_backend = backend_file.relative_to(backend_root).as_posix()
                files.append(self._make_file_entry(f"backend/generated/{relative_backend}", backend_file))

        files.sort(key=lambda item: item["path"])
        return files

    def _make_file_entry(self, relpath: str, source_path: Path) -> dict[str, Any]:
        content = source_path.read_text(encoding="utf-8")
        return {
            "path": relpath,
            "content": content,
            "sha256": self.manifest_service.sha256_text(content),
        }

    def _derive_build_id(self, response: dict[str, Any]) -> str:
        manifest = response.get("manifest") or {}
        if manifest.get("current_build_id"):
            return str(manifest["current_build_id"])
        server_info = response.get("server_info") or {}
        timestamp = str(server_info.get("timestamp") or "")
        if timestamp:
            sanitized = (
                timestamp.replace("-", "")
                .replace(":", "")
                .replace("T", "_")
                .replace("+00:00", "Z")
                .replace(".", "_")
            )
            return f"build_{sanitized}"
        return f"build_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"


def _compile_system_name(project_id: str) -> str:
    raw = (project_id or "CLIProject").strip()
    if raw.startswith("proj_"):
        raw = raw[5:]
    parts = [segment for segment in raw.replace("-", "_").split("_") if segment]
    if not parts:
        return "CLIProject"
    return "".join(part[:1].upper() + part[1:] for part in parts) or "CLIProject"

def _fallback_generate_ail(requirement: str) -> str:
    text = requirement.strip()
    lower = text.lower()
    if any(keyword in text for keyword in ["售后", "退款", "换货", "客服"]) or "after_sales" in lower:
        lines = [
            "^SYS[AfterSalesProject]",
            "#PROFILE[after_sales]",
            "@PAGE[AfterSales,/after-sales]",
            "#UI[after_sales:Entry]{}",
        ]
        if any(keyword in text for keyword in ["退款"]):
            lines.append("#UI[after_sales:Refund]{}")
        if any(keyword in text for keyword in ["换货"]):
            lines.append("#UI[after_sales:Exchange]{}")
        if any(keyword in text for keyword in ["投诉", "升级"]):
            lines.append("#UI[after_sales:Complaint]{}")
        if any(keyword in text for keyword in ["客服", "support", "联系客服"]):
            lines.append("#UI[after_sales:Support]{}")
        return "\n".join(lines)
    if any(keyword in text for keyword in ["商城", "电商", "购物车", "商品", "结算"]) or "ecom" in lower:
        lines = [
            "^SYS[EcomProject]",
            "#PROFILE[ecom_min]",
            "@PAGE[Home,/]",
            "#UI[ecom:Header]{}",
        ]
        if any(keyword in text for keyword in ["横幅", "banner", "首页横幅", "促销"]):
            lines.append("#UI[ecom:Banner]{}")
        if any(keyword in text for keyword in ["分类", "分类导航", "筛选", "filters"]):
            lines.append("#UI[ecom:CategoryNav]{}")
        lines.extend(
            [
                "#UI[ecom:ProductGrid]{}",
                "@PAGE[Product,/product/:id]",
                "#UI[ecom:ProductDetail]{}",
                "@PAGE[Cart,/cart]",
                "#UI[ecom:CartPanel]{}",
                "@PAGE[Checkout,/checkout]",
                "#UI[ecom:CheckoutPanel]{}",
            ]
        )
        if any(keyword in text for keyword in ["店铺", "店铺页", "shop", "品牌店铺"]):
            lines.extend(
                [
                    "@PAGE[Shop,/shop/:id]",
                    "#UI[ecom:ShopHeader]{}",
                    "#UI[ecom:ProductGrid]{}",
                ]
            )
        if any(keyword in text for keyword in ["搜索", "搜索结果", "搜索结果页", "search", "search results"]):
            lines.extend(
                [
                    "@PAGE[Search,/search]",
                    "#UI[ecom:SearchResultGrid]{}",
                ]
            )
        if any(keyword in text for keyword in ["分类", "分类导航", "分类页"]):
            lines.extend(
                [
                    "@PAGE[Category,/category/:name]",
                    "#UI[ecom:CategoryNav]{}",
                    "#UI[ecom:ProductGrid]{}",
                ]
            )
        return "\n".join(lines)
    if any(keyword in text for keyword in ["app", "聊天", "联系人", "待办", "消息"]) or "app_min" in lower:
        lines = [
            "^SYS[AppProject]",
            "#PROFILE[app_min]",
            "@PAGE[Home,/]",
            "#UI[app:TopBar]{}",
            "#UI[app:BottomTab]{}",
            "#UI[app:List]{}",
        ]
        if any(keyword in text for keyword in ["搜索", "search", "查找"]):
            lines.append("#UI[app:SearchBar]{}")
        if any(keyword in text for keyword in ["新增", "编辑", "输入", "composer"]):
            lines.append("#UI[app:Composer]{}")
        if any(keyword in text for keyword in ["聊天", "消息"]):
            lines.append("#UI[app:ChatWindow]{}")
        else:
            lines.append("#UI[app:Card]{}")
        return "\n".join(lines)

    lines = [
        "^SYS[LandingProject]",
        "#PROFILE[landing]",
        "@PAGE[Home,/]",
        "#UI[landing:Header]{}",
        "#UI[landing:Hero]{}",
        "#UI[landing:FeatureGrid]{}",
        "#UI[landing:CTA]{}",
        "#UI[landing:Footer]{}",
    ]
    if any(keyword in text for keyword in ["联系我们", "联系", "contact"]):
        lines.append("#UI[landing:Contact]{}")
    if any(
        keyword in text
        for keyword in [
            "客户评价",
            "用户评价",
            "评价",
            "用户反馈",
            "客户反馈",
            "口碑",
            "review block",
            "customer review",
            "testimonial",
            "testimonials",
        ]
    ):
        lines.append("#UI[landing:Testimonial]{}")
    if any(keyword in text for keyword in ["职位", "职位展示", "职位列表", "招聘", "招聘岗位", "招聘信息", "jobs", "careers", "join us"]):
        lines.append("#UI[landing:Jobs]{}")
    if any(keyword in text for keyword in ["作品集", "项目作品", "项目案例", "作品展示", "案例", "案例展示", "portfolio", "case studies"]):
        lines.append("#UI[landing:Portfolio]{}")
    if any(keyword in text for keyword in ["团队", "团队介绍", "成员", "关于我们", "关于团队", "team"]):
        lines.append("#UI[landing:Team]{}")
    if any(keyword in text for keyword in ["FAQ", "常见问题", "常见问答", "问答"]):
        lines.append("#UI[landing:FAQ]{}")
    if any(keyword in text for keyword in ["stats", "data", "metrics", "数据", "统计", "数字", "数据展示", "公司数据展示", "关键数据"]):
        lines.append("#UI[landing:Stats]{}")
    if any(
        keyword in text
        for keyword in [
            "客户 Logo",
            "客户标识",
            "客户 logos",
            "合作伙伴",
            "合作伙伴 logo",
            "partners",
            "partner logos",
            "品牌墙",
            "客户墙",
            "logo",
            "logos",
            "logo wall",
        ]
    ):
        lines.append("#UI[landing:LogoCloud]{}")
    return "\n".join(lines)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
