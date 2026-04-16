from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any


class AILParserV3:
    SYS_PATTERN = re.compile(r"^\^SYS\[([^\]]+)\]$")
    DB_TABLE_PATTERN = re.compile(r"^>DB_TABLE\[([^\]]+)\]\{(.*)\}$", re.S)
    API_PATTERN = re.compile(r"^@API\[([^,\]]+),([^\]]+)\]\{(.*)\}$", re.S)
    API_ACTION_PATTERN = re.compile(r"^>DB_(SEL|INS)\[([^\]]+)\]$")
    PAGE_PATTERN = re.compile(r"^@PAGE\[([^,\]]+),([^\]]+)\]$")
    COMP_PATTERN = re.compile(r"^#COMP\[([^\]]+)\]\{(.*)\}$", re.S)
    LIB_PATTERN = re.compile(r"^#LIB\[([^\]]+)\]$")
    UI_PATTERN = re.compile(r"^#UI\[([^:]+):([^\]]+)\]\{(.*)\}$", re.S)
    FIELD_PATTERN = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)(?::(str|int|text))?$")
    IDENT_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

    def __init__(self, ail_code: str) -> None:
        self.ail_code = ail_code

    def split_actions(self) -> list[str]:
        actions: list[str] = []
        current: list[str] = []
        quote_char: str | None = None
        escape = False
        round_depth = 0
        square_depth = 0
        curly_depth = 0

        for char in self.ail_code:
            if quote_char is not None:
                current.append(char)
                if escape:
                    escape = False
                elif char == "\\":
                    escape = True
                elif char == quote_char:
                    quote_char = None
                continue

            if char in ('"', "'"):
                quote_char = char
                current.append(char)
                continue

            if char == "(":
                round_depth += 1
            elif char == ")":
                round_depth = max(0, round_depth - 1)
            elif char == "[":
                square_depth += 1
            elif char == "]":
                square_depth = max(0, square_depth - 1)
            elif char == "{":
                curly_depth += 1
            elif char == "}":
                curly_depth = max(0, curly_depth - 1)

            if char == "~" and round_depth == 0 and square_depth == 0 and curly_depth == 0:
                token = "".join(current).strip()
                if token:
                    actions.append(token)
                current = []
                continue

            current.append(char)

        tail = "".join(current).strip()
        if tail:
            actions.append(tail)
        return actions

    def parse(self) -> dict[str, Any]:
        ast: dict[str, Any] = {
            "system_name": None,
            "database": {},
            "backend_apis": [],
            "frontend_pages": [],
            "libraries": [],
        }

        current_page: dict[str, Any] | None = None

        for raw_action in self.split_actions():
            action = raw_action.strip()

            sys_match = self.SYS_PATTERN.fullmatch(action)
            if sys_match:
                ast["system_name"] = sys_match.group(1).strip()
                continue

            lib_match = self.LIB_PATTERN.fullmatch(action)
            if lib_match:
                lib_name = lib_match.group(1).strip()
                if not lib_name:
                    raise ValueError("#LIB cannot be empty")
                if lib_name not in ast["libraries"]:
                    ast["libraries"].append(lib_name)
                continue

            db_match = self.DB_TABLE_PATTERN.fullmatch(action)
            if db_match:
                table_name = db_match.group(1).strip()
                if not self.IDENT_PATTERN.fullmatch(table_name):
                    raise ValueError(f"Invalid table name: {table_name}")
                fields = self._parse_fields(db_match.group(2).strip(), table_name)
                ast["database"][table_name] = fields
                continue

            api_match = self.API_PATTERN.fullmatch(action)
            if api_match:
                method = api_match.group(1).strip().upper()
                route = api_match.group(2).strip()
                api_action = api_match.group(3).strip()

                if not re.fullmatch(r"GET|POST|PUT|PATCH|DELETE", method):
                    raise ValueError(f"Invalid API method: {method}")
                if not route.startswith("/"):
                    raise ValueError(f"Invalid API route: {route}")

                action_match = self.API_ACTION_PATTERN.fullmatch(api_action)
                if not action_match:
                    raise ValueError("Invalid API action: must be >DB_SEL[table] or >DB_INS[table]")

                action_table = action_match.group(2).strip()
                if not self.IDENT_PATTERN.fullmatch(action_table):
                    raise ValueError(f"Invalid API action table name: {action_table}")

                ast["backend_apis"].append(
                    {
                        "method": method,
                        "route": route,
                        "action": api_action,
                    }
                )
                continue

            page_match = self.PAGE_PATTERN.fullmatch(action)
            if page_match:
                page_name = page_match.group(1).strip()
                page_path = page_match.group(2).strip()
                if not page_name:
                    raise ValueError("Page name cannot be empty")
                if not page_path.startswith("/"):
                    raise ValueError(f"Invalid page path: {page_path}")

                current_page = {"name": page_name, "path": page_path, "components": []}
                ast["frontend_pages"].append(current_page)
                continue

            ui_match = self.UI_PATTERN.fullmatch(action)
            if ui_match:
                if current_page is None:
                    raise ValueError("#UI must appear after @PAGE")
                source, name, config = ui_match.groups()
                source = source.strip()
                name = name.strip()
                if not source or not name:
                    raise ValueError("#UI source and component name cannot be empty")
                current_page["components"].append(
                    {
                        "source": source,
                        "name": name,
                        "config": config.strip(),
                    }
                )
                continue

            comp_match = self.COMP_PATTERN.fullmatch(action)
            if comp_match:
                if current_page is None:
                    raise ValueError("#COMP must appear after @PAGE")
                comp_type, config = comp_match.groups()
                comp_type = comp_type.strip()
                if not comp_type:
                    raise ValueError("Component type cannot be empty")
                current_page["components"].append(
                    {
                        "type": comp_type,
                        "config": config.strip(),
                    }
                )
                continue

            raise ValueError(f"Unsupported AIL action: {action}")

        if ast["system_name"] is None:
            raise ValueError("Missing required instruction: ^SYS[项目名]")

        return ast

    def _parse_fields(self, fields_blob: str, table_name: str) -> dict[str, str]:
        if not fields_blob:
            raise ValueError(f"Table {table_name} must declare at least one field")

        fields: dict[str, str] = {}
        parts = [part.strip() for part in fields_blob.split(",") if part.strip()]
        if not parts:
            raise ValueError(f"Table {table_name} must declare at least one field")

        for part in parts:
            match = self.FIELD_PATTERN.fullmatch(part)
            if not match:
                raise ValueError(f"Invalid field declaration in {table_name}: {part}")
            field_name, field_type = match.groups()
            if field_name in fields:
                raise ValueError(f"Duplicate field name in {table_name}: {field_name}")
            fields[field_name] = field_type or "str"

        return fields


class AILProjectGeneratorV3:
    def __init__(self, ast: dict[str, Any], base_dir: str = "./output_projects") -> None:
        self.ast = ast
        self.base_dir = Path(base_dir)
        self.system_name = self._require_system_name()

    def build_project(self) -> Path:
        project_root = self.base_dir / self.system_name
        backend_dir = project_root / "backend"
        frontend_views_dir = project_root / "frontend" / "src" / "views"

        backend_dir.mkdir(parents=True, exist_ok=True)
        frontend_views_dir.mkdir(parents=True, exist_ok=True)

        (backend_dir / "main.py").write_text(self._generate_backend_main_py(), encoding="utf-8")

        for page in self._frontend_pages():
            filename = f"{self._sanitize_file_stem(str(page.get('name', 'Page')))}.vue"
            (frontend_views_dir / filename).write_text(self._generate_vue_view(page), encoding="utf-8")

        self._write_setup_ui_script(project_root)
        return project_root

    def _require_system_name(self) -> str:
        name = str(self.ast.get("system_name", "")).strip()
        if not name:
            raise ValueError("AST missing required field: system_name")
        return name

    def _database_schema(self) -> dict[str, dict[str, str]]:
        db = self.ast.get("database", {})
        if not isinstance(db, dict):
            raise ValueError("AST field 'database' must be a dict")

        normalized: dict[str, dict[str, str]] = {}
        for table_name, fields in db.items():
            if not isinstance(table_name, str) or not isinstance(fields, dict):
                continue
            typed_fields: dict[str, str] = {}
            for field_name, field_type in fields.items():
                if not isinstance(field_name, str):
                    continue
                typed_fields[field_name] = self._normalize_ast_type(str(field_type))
            normalized[table_name] = typed_fields
        return normalized

    def _backend_apis(self) -> list[dict[str, str]]:
        raw = self.ast.get("backend_apis", [])
        if not isinstance(raw, list):
            raise ValueError("AST field 'backend_apis' must be a list")

        apis: list[dict[str, str]] = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            apis.append(
                {
                    "method": str(item.get("method", "GET")).upper(),
                    "route": str(item.get("route", "/")),
                    "action": str(item.get("action", "")),
                }
            )
        return apis

    def _frontend_pages(self) -> list[dict[str, Any]]:
        pages = self.ast.get("frontend_pages", [])
        if not isinstance(pages, list):
            raise ValueError("AST field 'frontend_pages' must be a list")
        return [page for page in pages if isinstance(page, dict)]

    @staticmethod
    def _normalize_ast_type(field_type: str) -> str:
        normalized = field_type.strip().lower()
        return normalized if normalized in {"str", "int", "text"} else "str"

    @staticmethod
    def _to_python_type(field_type: str) -> str:
        return {"str": "str", "int": "int", "text": "str"}.get(field_type, "str")

    @staticmethod
    def _to_sqlalchemy_type(field_type: str) -> str:
        return {"str": "String", "int": "Integer", "text": "Text"}.get(field_type, "String")

    @staticmethod
    def _to_pascal_case(name: str) -> str:
        parts = re.split(r"[^A-Za-z0-9]+", name)
        result = "".join(part[:1].upper() + part[1:] for part in parts if part)
        if not result:
            result = "Generated"
        if result[0].isdigit():
            result = f"Model{result}"
        return result

    @staticmethod
    def _to_snake_case(name: str) -> str:
        snake = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").lower()
        if not snake:
            snake = "generated"
        if snake[0].isdigit():
            snake = f"route_{snake}"
        return snake

    @staticmethod
    def _to_kebab_case(name: str) -> str:
        interim = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", name)
        interim = re.sub(r"[^A-Za-z0-9]+", "-", interim)
        kebab = interim.strip("-").lower()
        return kebab or "component"

    @staticmethod
    def _sanitize_file_stem(name: str) -> str:
        stem = re.sub(r"[^A-Za-z0-9_-]+", "", name)
        return stem or "Page"

    @staticmethod
    def _sanitize_vue_component_identifier(name: str) -> str:
        cleaned = re.sub(r"[^A-Za-z0-9_]", "", name)
        if not cleaned:
            cleaned = "GeneratedComponent"
        if cleaned[0].isdigit():
            cleaned = f"Comp{cleaned}"
        return cleaned

    @staticmethod
    def _parse_component_config(config: str) -> dict[str, str]:
        props: dict[str, str] = {}
        if not config.strip():
            return props

        for part in [x.strip() for x in config.split(",") if x.strip()]:
            if ":" in part:
                key, value = part.split(":", 1)
                props[key.strip()] = value.strip()
            elif "=" in part:
                key, value = part.split("=", 1)
                props[key.strip()] = value.strip()
            else:
                props[part] = "true"
        return props

    def _generate_backend_main_py(self) -> str:
        database = self._database_schema()
        backend_apis = self._backend_apis()

        lines: list[str] = []
        lines.append("from fastapi import FastAPI, Depends")
        lines.append("from pydantic import BaseModel")
        lines.append("from sqlalchemy import create_engine, Column, Integer, String, Text")
        lines.append("from sqlalchemy.orm import declarative_base, sessionmaker, Session")
        lines.append("")
        lines.append('SQLALCHEMY_DATABASE_URL = "sqlite:///./ail_data.db"')
        lines.append('engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})')
        lines.append("SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)")
        lines.append("Base = declarative_base()")
        lines.append("")
        lines.append("def get_db():")
        lines.append("    db = SessionLocal()")
        lines.append("    try:")
        lines.append("        yield db")
        lines.append("    finally:")
        lines.append("        db.close()")
        lines.append("")

        orm_name_map: dict[str, str] = {}
        schema_name_map: dict[str, str] = {}
        fields_name_map: dict[str, list[tuple[str, str]]] = {}

        for table_name, fields in database.items():
            orm_model_name = self._to_pascal_case(table_name)
            schema_model_name = f"{self._to_pascal_case(table_name)}Schema"
            orm_name_map[table_name] = orm_model_name
            schema_name_map[table_name] = schema_model_name

            normalized_fields: list[tuple[str, str]] = []
            for field_name, raw_type in fields.items():
                normalized_fields.append((self._to_snake_case(field_name), raw_type))
            fields_name_map[table_name] = normalized_fields

            lines.append(f"class {orm_model_name}(Base):")
            lines.append(f'    __tablename__ = "{table_name}"')
            lines.append("    id = Column(Integer, primary_key=True, index=True)")
            for field_name, raw_type in normalized_fields:
                lines.append(f"    {field_name} = Column({self._to_sqlalchemy_type(raw_type)})")
            lines.append("")

            lines.append(f"class {schema_model_name}(BaseModel):")
            if not normalized_fields:
                lines.append("    pass")
            else:
                for field_name, raw_type in normalized_fields:
                    lines.append(f"    {field_name}: {self._to_python_type(raw_type)}")
            lines.append("")

        lines.append("Base.metadata.create_all(bind=engine)")
        lines.append("")
        lines.append(f'app = FastAPI(title="{self.system_name}")')
        lines.append("")
        lines.append("def _model_dump(payload: BaseModel) -> dict:")
        lines.append("    if hasattr(payload, \"model_dump\"):")
        lines.append("        return payload.model_dump()")
        lines.append("    return payload.dict()")
        lines.append("")
        lines.append("def _serialize_row(row, field_names: list[str]) -> dict:")
        lines.append("    data = {\"id\": row.id}")
        lines.append("    for field in field_names:")
        lines.append("        data[field] = getattr(row, field)")
        lines.append("    return data")
        lines.append("")

        for api in backend_apis:
            method = api["method"].lower()
            route = api["route"]
            action = api["action"]
            route_slug = route.strip("/").replace("/", "_") or "root"
            func_name = self._to_snake_case(f"{method}_{route_slug}")

            lines.append(f"@app.{method}(\"{route}\")")
            action_match = re.fullmatch(r">DB_(SEL|INS)\[([^\]]+)\]", action)

            if action_match:
                action_kind, table_name = action_match.groups()
                orm_model_name = orm_name_map.get(table_name)
                schema_model_name = schema_name_map.get(table_name)
                table_fields = fields_name_map.get(table_name, [])

                if action_kind == "SEL" and orm_model_name:
                    lines.append(f"async def {func_name}(db: Session = Depends(get_db)):")
                    lines.append(f"    rows = db.query({orm_model_name}).all()")
                    fields_literal = ", ".join(f'\"{field}\"' for field, _ in table_fields)
                    lines.append(f"    fields = [{fields_literal}]")
                    lines.append("    return [_serialize_row(row, fields) for row in rows]")
                elif action_kind == "INS" and orm_model_name:
                    payload_type = schema_model_name or "dict"
                    lines.append(f"async def {func_name}(payload: {payload_type}, db: Session = Depends(get_db)):")
                    lines.append("    payload_data = _model_dump(payload) if isinstance(payload, BaseModel) else payload")
                    lines.append(f"    record = {orm_model_name}(**payload_data)")
                    lines.append("    db.add(record)")
                    lines.append("    db.commit()")
                    lines.append("    db.refresh(record)")
                    fields_literal = ", ".join(f'\"{field}\"' for field, _ in table_fields)
                    lines.append(f"    fields = [{fields_literal}]")
                    lines.append("    return _serialize_row(record, fields)")
                else:
                    lines.append(f"async def {func_name}(db: Session = Depends(get_db)):")
                    lines.append(f"    # TODO: execute {action}")
                    lines.append("    return {\"status\": \"ok\"}")
            else:
                lines.append(f"async def {func_name}(db: Session = Depends(get_db)):")
                lines.append(f"    # TODO: execute {action}")
                lines.append("    return {\"status\": \"ok\"}")
            lines.append("")

        return "\n".join(lines).rstrip() + "\n"

    def _generate_vue_view(self, page: dict[str, Any]) -> str:
        components = page.get("components", [])
        if not isinstance(components, list):
            components = []

        import_lines: list[str] = []
        template_lines: list[str] = []
        imported: set[tuple[str, str]] = set()

        for item in components:
            if not isinstance(item, dict):
                continue

            if "source" in item and "name" in item:
                source = str(item.get("source", "")).strip().lower()
                raw_name = str(item.get("name", "")).strip()
                config = str(item.get("config", "")).strip()
                component_name = self._sanitize_vue_component_identifier(raw_name)

                if source == "shadcn":
                    module_name = self._to_kebab_case(component_name)
                    key = ("shadcn", component_name)
                    if key not in imported:
                        import_lines.append(
                            f"import {{ {component_name} }} from '@/components/ui/{module_name}'"
                        )
                        imported.add(key)
                else:
                    key = (source or "local", component_name)
                    if key not in imported:
                        import_lines.append(
                            f"import {component_name} from '@/components/{component_name}.vue'"
                        )
                        imported.add(key)

                props = self._parse_component_config(config)
                attrs = " ".join(
                    f'{k}="{html.escape(v, quote=True)}"' for k, v in props.items()
                )
                if attrs:
                    template_lines.append(f"    <{component_name} {attrs} />")
                else:
                    template_lines.append(f"    <{component_name} />")
            else:
                raw_type = str(item.get("type", "Component")).strip() or "Component"
                config = str(item.get("config", "")).strip()
                component_name = self._sanitize_vue_component_identifier(raw_type)
                key = ("legacy", component_name)
                if key not in imported:
                    import_lines.append(
                        f"import {component_name} from '@/components/{component_name}.vue'"
                    )
                    imported.add(key)

                props = self._parse_component_config(config)
                attrs = " ".join(
                    f'{k}="{html.escape(v, quote=True)}"' for k, v in props.items()
                )
                if attrs:
                    template_lines.append(f"    <{component_name} {attrs} />")
                else:
                    template_lines.append(f"    <{component_name} />")

        if not template_lines:
            template_lines.append("    <div>No components declared.</div>")

        script_block = "\n".join(import_lines)
        template_block = "\n".join(template_lines)

        return (
            "<template>\n"
            "  <section class=\"page-root\">\n"
            f"{template_block}\n"
            "  </section>\n"
            "</template>\n\n"
            "<script setup>\n"
            f"{script_block}\n"
            "</script>\n\n"
            "<style scoped>\n"
            ".page-root {\n"
            "  display: flex;\n"
            "  flex-direction: column;\n"
            "  gap: 12px;\n"
            "}\n"
            "</style>\n"
        )

    def _collect_shadcn_components(self) -> list[str]:
        collected: list[str] = []
        seen: set[str] = set()

        for page in self._frontend_pages():
            components = page.get("components", [])
            if not isinstance(components, list):
                continue
            for item in components:
                if not isinstance(item, dict):
                    continue
                source = str(item.get("source", "")).strip().lower()
                if source != "shadcn":
                    continue
                name = str(item.get("name", "")).strip()
                if not name:
                    continue
                kebab = self._to_kebab_case(name)
                if kebab not in seen:
                    seen.add(kebab)
                    collected.append(kebab)

        return collected

    def _write_setup_ui_script(self, project_root: Path) -> None:
        shadcn_components = self._collect_shadcn_components()
        script_lines = ["#!/bin/bash", "set -e"]

        if shadcn_components:
            for component in shadcn_components:
                script_lines.append(f"npx shadcn-vue@latest add {component}")
        else:
            script_lines.append("# no shadcn components detected")

        script_path = project_root / "setup_ui.sh"
        script_path.write_text("\n".join(script_lines) + "\n", encoding="utf-8")
        script_path.chmod(0o755)


if __name__ == "__main__":
    ail_code = (
        "^SYS[CSDN_Clone_V3]"
        "~#LIB[shadcn-vue]"
        "~>DB_TABLE[posts]{title:str,content:text}"
        "~@API[GET,/api/posts]{>DB_SEL[posts]}"
        "~@API[POST,/api/posts]{>DB_INS[posts]}"
        "~@PAGE[Home,/]"
        "~#UI[shadcn:Navbar]{theme:dark}"
        "~#UI[shadcn:Card]{data:posts,layout:grid}"
    )

    ast = AILParserV3(ail_code).parse()
    print(json.dumps(ast, indent=4, ensure_ascii=False))

    generator = AILProjectGeneratorV3(ast)
    output = generator.build_project()
    print(f"Project generated at: {output}")
