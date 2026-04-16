from __future__ import annotations

from pathlib import Path
import html
import re
from typing import Any


class AILProjectGenerator:
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

        backend_main = self._generate_backend_main_py()
        (backend_dir / "main.py").write_text(backend_main, encoding="utf-8")

        for page in self._frontend_pages():
            view_filename = f"{self._sanitize_file_stem(str(page.get('name', 'Page')))}.vue"
            view_source = self._generate_vue_view(page)
            (frontend_views_dir / view_filename).write_text(view_source, encoding="utf-8")

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
            method = str(item.get("method", "GET")).upper()
            route = str(item.get("route", "/"))
            action = str(item.get("action", ""))
            apis.append({"method": method, "route": route, "action": action})
        return apis

    def _frontend_pages(self) -> list[dict[str, Any]]:
        raw = self.ast.get("frontend_pages", [])
        if not isinstance(raw, list):
            raise ValueError("AST field 'frontend_pages' must be a list")

        pages: list[dict[str, Any]] = []
        for page in raw:
            if isinstance(page, dict):
                pages.append(page)
        return pages

    @staticmethod
    def _normalize_ast_type(field_type: str) -> str:
        normalized = field_type.strip().lower()
        if normalized not in {"str", "int", "text"}:
            return "str"
        return normalized

    @staticmethod
    def _to_python_type(field_type: str) -> str:
        mapping = {
            "str": "str",
            "int": "int",
            "text": "str",
        }
        return mapping.get(field_type, "str")

    @staticmethod
    def _to_sqlalchemy_type(field_type: str) -> str:
        mapping = {
            "str": "String",
            "int": "Integer",
            "text": "Text",
        }
        return mapping.get(field_type, "String")

    @staticmethod
    def _to_pascal_case(name: str) -> str:
        parts = re.split(r"[^A-Za-z0-9]+", name)
        pascal = "".join(part[:1].upper() + part[1:] for part in parts if part)
        if not pascal:
            pascal = "Generated"
        if pascal[0].isdigit():
            pascal = f"Model{pascal}"
        return pascal

    @staticmethod
    def _to_snake_case(name: str) -> str:
        snake = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").lower()
        if not snake:
            snake = "generated"
        if snake[0].isdigit():
            snake = f"route_{snake}"
        return snake

    @staticmethod
    def _sanitize_file_stem(name: str) -> str:
        stem = re.sub(r"[^A-Za-z0-9_-]+", "", name)
        return stem or "Page"

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
                sql_type = self._to_sqlalchemy_type(raw_type)
                lines.append(f"    {field_name} = Column({sql_type})")
            lines.append("")

            lines.append(f"class {schema_model_name}(BaseModel):")
            if not normalized_fields:
                lines.append("    pass")
            else:
                for field_name, raw_type in normalized_fields:
                    py_type = self._to_python_type(raw_type)
                    lines.append(f"    {field_name}: {py_type}")
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
            decorator = f"@app.{method}(\"{route}\")"
            lines.append(decorator)

            action_table_match = re.fullmatch(r">DB_(SEL|INS)\[([^\]]+)\]", action)
            if action_table_match:
                action_kind = action_table_match.group(1)
                table_name = action_table_match.group(2)
                orm_model_name = orm_name_map.get(table_name)
                schema_model_name = schema_name_map.get(table_name)
                table_fields = fields_name_map.get(table_name, [])

                if action_kind == "SEL":
                    if orm_model_name:
                        lines.append(f"async def {func_name}(db: Session = Depends(get_db)):")
                        lines.append(f"    rows = db.query({orm_model_name}).all()")
                        row_fields = ", ".join(f"\"{f[0]}\"" for f in table_fields)
                        lines.append(f"    fields = [{row_fields}]")
                        lines.append("    return [_serialize_row(row, fields) for row in rows]")
                    else:
                        lines.append(f"async def {func_name}(db: Session = Depends(get_db)):")
                        lines.append(f"    # TODO: execute {action}")
                        lines.append("    return []")
                elif action_kind == "INS":
                    payload_type = schema_model_name or "dict"
                    lines.append(f"async def {func_name}(payload: {payload_type}, db: Session = Depends(get_db)):")
                    if orm_model_name:
                        lines.append("    payload_data = _model_dump(payload) if isinstance(payload, BaseModel) else payload")
                        lines.append(f"    record = {orm_model_name}(**payload_data)")
                        lines.append("    db.add(record)")
                        lines.append("    db.commit()")
                        lines.append("    db.refresh(record)")
                        row_fields = ", ".join(f"\"{f[0]}\"" for f in table_fields)
                        lines.append(f"    fields = [{row_fields}]")
                        lines.append("    return _serialize_row(record, fields)")
                    else:
                        lines.append(f"    # TODO: execute {action}")
                        lines.append("    return {\"status\": \"ok\"}")
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

    @staticmethod
    def _parse_component_config(config: str) -> dict[str, str]:
        props: dict[str, str] = {}
        if not config.strip():
            return props

        for segment in config.split(","):
            part = segment.strip()
            if not part:
                continue
            if "=" in part:
                key, value = part.split("=", 1)
                props[key.strip()] = value.strip()
            else:
                props[part] = "true"
        return props

    @staticmethod
    def _sanitize_vue_component_identifier(name: str) -> str:
        cleaned = re.sub(r"[^A-Za-z0-9_]", "", name)
        if not cleaned:
            cleaned = "GeneratedComponent"
        if cleaned[0].isdigit():
            cleaned = f"Comp{cleaned}"
        return cleaned

    def _generate_vue_view(self, page: dict[str, Any]) -> str:
        components = page.get("components", [])
        if not isinstance(components, list):
            components = []

        import_lines: list[str] = []
        template_lines: list[str] = []
        imported: set[str] = set()

        for item in components:
            if not isinstance(item, dict):
                continue
            raw_type = str(item.get("type", "Component")).strip() or "Component"
            component_id = self._sanitize_vue_component_identifier(raw_type)
            if component_id not in imported:
                import_lines.append(f'import {component_id} from "@/components/{component_id}.vue"')
                imported.add(component_id)

            config = str(item.get("config", "")).strip()
            props = self._parse_component_config(config)
            attrs = " ".join(f'{key}="{html.escape(value, quote=True)}"' for key, value in props.items())
            if attrs:
                template_lines.append(f"    <{component_id} {attrs} />")
            else:
                template_lines.append(f"    <{component_id} />")

        if not template_lines:
            template_lines.append("    <div>No components declared.</div>")

        script_block = "\n".join(import_lines) if import_lines else ""

        return (
            "<template>\n"
            "  <section class=\"page-root\">\n"
            f"{chr(10).join(template_lines)}\n"
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


if __name__ == "__main__":
    from ail_compiler_v2_core import AILParserV2

    ail_code = "^SYS[CSDN_Clone]~>DB_TABLE[users]{uid:int,name:str}~>DB_TABLE[posts]{title:str,content:text}~@API[GET,/api/posts]{>DB_SEL[posts]}~@API[POST,/api/posts]{>DB_INS[posts]}~@PAGE[Home,/]~#COMP[Navbar]{auth=true}~#COMP[List]{api=/api/posts}"
    ast = AILParserV2(ail_code).parse()
    generator = AILProjectGenerator(ast)
    generator.build_project()
    print(f"✅ 项目 {ast['system_name']} 骨架生成完毕！请查看 output_projects 目录。")
