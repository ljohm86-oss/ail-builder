from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any


class AILParserV4:
    ROLE_EXPR = r"([A-Za-z_][A-Za-z0-9_]*(?:\|[A-Za-z_][A-Za-z0-9_]*)*)"
    SYS_PATTERN = re.compile(r"^\^SYS\[([^\]]+)\]$")
    DB_TABLE_PATTERN = re.compile(r"^>DB_TABLE\[([^\]]+)\]\{(.*)\}$", re.S)
    DB_REL_PATTERN = re.compile(r"^>DB_REL\[([A-Za-z_]+)\(1\)->([A-Za-z_]+)\(N\)\]$")
    API_PATTERN = re.compile(r"^@API\[([^,\]]+),([^\]]+)\]\{(.*)\}$", re.S)
    API_ACTION_PATTERN = re.compile(
        rf"^(>DB_(SEL|INS|AUTH)\[([^\]]+)\])(\*AUTH)?(\*ROLE\[{ROLE_EXPR}\])?$"
    )
    PAGE_PATTERN = re.compile(
        rf"^@PAGE\[([^,\]]+),([^\]]+)\](\*ROLE\[{ROLE_EXPR}\])?$"
    )
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
            "relations": [],
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

            db_table_match = self.DB_TABLE_PATTERN.fullmatch(action)
            if db_table_match:
                table_name = db_table_match.group(1).strip()
                if not self.IDENT_PATTERN.fullmatch(table_name):
                    raise ValueError(f"Invalid table name: {table_name}")
                ast["database"][table_name] = self._parse_fields(
                    db_table_match.group(2).strip(),
                    table_name,
                )
                continue

            rel_match = self.DB_REL_PATTERN.fullmatch(action)
            if rel_match:
                one_table, many_table = rel_match.groups()
                ast["relations"].append({"one": one_table, "many": many_table})
                continue

            api_match = self.API_PATTERN.fullmatch(action)
            if api_match:
                method = api_match.group(1).strip().upper()
                route = api_match.group(2).strip()
                action_expr = api_match.group(3).strip()

                if not re.fullmatch(r"GET|POST|PUT|PATCH|DELETE|AUTH", method):
                    raise ValueError(f"Invalid API method: {method}")
                if not route.startswith("/"):
                    raise ValueError(f"Invalid API route: {route}")

                action_match = self.API_ACTION_PATTERN.fullmatch(action_expr)
                if not action_match:
                    raise ValueError(
                        "Invalid API action: use >DB_SEL[table], >DB_INS[table], >DB_AUTH[table], optional *AUTH and *ROLE[role]"
                    )

                base_action, action_kind, table_name, auth_suffix, _, auth_role = action_match.groups()
                requires_auth = auth_suffix is not None or auth_role is not None

                if not self.IDENT_PATTERN.fullmatch(table_name):
                    raise ValueError(f"Invalid API action table name: {table_name}")
                if method == "AUTH" and action_kind != "AUTH":
                    raise ValueError("@API[AUTH,...] must use >DB_AUTH[table]")

                ast["backend_apis"].append(
                    {
                        "method": method,
                        "route": route,
                        "action": base_action,
                        "action_kind": action_kind,
                        "table": table_name,
                        "requires_auth": requires_auth,
                        "auth_role": auth_role or "",
                    }
                )
                continue

            page_match = self.PAGE_PATTERN.fullmatch(action)
            if page_match:
                page_name = page_match.group(1).strip()
                page_path = page_match.group(2).strip()
                page_role = (page_match.group(4) or "").strip()
                if not page_name:
                    raise ValueError("Page name cannot be empty")
                if not page_path.startswith("/"):
                    raise ValueError(f"Invalid page path: {page_path}")

                current_page = {
                    "name": page_name,
                    "path": page_path,
                    "components": [],
                }
                if page_role:
                    current_page["page_role"] = page_role
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


class AILProjectGeneratorV4:
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
            view_name = f"{self._sanitize_file_stem(str(page.get('name', 'Page')))}.vue"
            (frontend_views_dir / view_name).write_text(self._generate_vue_view(page), encoding="utf-8")

        self._write_setup_ui_script(project_root)
        self._write_start_script(project_root)
        return project_root

    def _require_system_name(self) -> str:
        name = str(self.ast.get("system_name", "")).strip()
        if not name:
            raise ValueError("AST missing required field: system_name")
        return name

    def _database_schema(self) -> dict[str, dict[str, str]]:
        raw = self.ast.get("database", {})
        if not isinstance(raw, dict):
            raise ValueError("AST field 'database' must be a dict")

        normalized: dict[str, dict[str, str]] = {}
        for table_name, fields in raw.items():
            if not isinstance(table_name, str) or not isinstance(fields, dict):
                continue
            typed: dict[str, str] = {}
            for field_name, field_type in fields.items():
                if not isinstance(field_name, str):
                    continue
                typed[field_name] = self._normalize_ast_type(str(field_type))
            normalized[table_name] = typed
        return normalized

    def _relations(self) -> list[dict[str, str]]:
        raw = self.ast.get("relations", [])
        if not isinstance(raw, list):
            return []
        relations: list[dict[str, str]] = []
        for item in raw:
            if isinstance(item, dict) and isinstance(item.get("one"), str) and isinstance(item.get("many"), str):
                relations.append({"one": item["one"], "many": item["many"]})
        return relations

    def _backend_apis(self) -> list[dict[str, Any]]:
        raw = self.ast.get("backend_apis", [])
        if not isinstance(raw, list):
            raise ValueError("AST field 'backend_apis' must be a list")

        apis: list[dict[str, Any]] = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            action = str(item.get("action", "")).strip()
            method = str(item.get("method", "GET")).upper()
            route = str(item.get("route", "/"))
            requires_auth = bool(item.get("requires_auth", False))
            raw_auth_role = item.get("auth_role", "")
            auth_role = raw_auth_role.strip() if isinstance(raw_auth_role, str) else ""

            action_kind = str(item.get("action_kind", "")).strip().upper()
            table = str(item.get("table", "")).strip()

            if not action_kind or not table:
                action_match = re.fullmatch(
                    r"(>DB_(SEL|INS|AUTH)\[([^\]]+)\])(\*AUTH)?(\*ROLE\[([A-Za-z_][A-Za-z0-9_]*(?:\|[A-Za-z_][A-Za-z0-9_]*)*)\])?",
                    action,
                )
                if action_match:
                    _, action_kind, table, auth_suffix, _, role_suffix = action_match.groups()
                    if auth_suffix is not None or role_suffix:
                        requires_auth = True
                    if role_suffix:
                        auth_role = role_suffix

            apis.append(
                {
                    "method": method,
                    "route": route,
                    "action": action,
                    "action_kind": action_kind,
                    "table": table,
                    "requires_auth": requires_auth,
                    "auth_role": auth_role,
                }
            )
        return apis

    def _frontend_pages(self) -> list[dict[str, Any]]:
        pages = self.ast.get("frontend_pages", [])
        if not isinstance(pages, list):
            raise ValueError("AST field 'frontend_pages' must be a list")
        return [p for p in pages if isinstance(p, dict)]

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

        for part in [p.strip() for p in config.split(",") if p.strip()]:
            if ":" in part:
                key, value = part.split(":", 1)
                props[key.strip()] = value.strip()
            elif "=" in part:
                key, value = part.split("=", 1)
                props[key.strip()] = value.strip()
            else:
                props[part] = "true"
        return props

    @staticmethod
    def _singularize(name: str) -> str:
        lower = name.lower()
        if lower.endswith("ies") and len(name) > 3:
            return name[:-3] + "y"
        if lower.endswith("s") and len(name) > 1:
            return name[:-1]
        return name

    @staticmethod
    def _resolve_table_name(name: str, table_names: list[str]) -> str | None:
        if name in table_names:
            return name
        lowered = name.lower()
        for table_name in table_names:
            if table_name.lower() == lowered:
                return table_name
        return None

    @staticmethod
    def _pick_identifier_field(field_names: list[str]) -> str:
        preferred = ["username", "email", "name", "uid"]
        lowered_map = {field.lower(): field for field in field_names}
        for key in preferred:
            if key in lowered_map:
                return lowered_map[key]
        for field in field_names:
            if "password" not in field.lower():
                return field
        return "username"

    @staticmethod
    def _pick_password_storage_field(field_names: list[str]) -> str:
        lowered_map = {field.lower(): field for field in field_names}
        for key in ["pwd", "password_hash", "password"]:
            if key in lowered_map:
                return lowered_map[key]
        return "pwd"

    def _build_relation_maps(
        self,
        table_names: list[str],
        class_name_map: dict[str, str],
    ) -> tuple[dict[str, list[dict[str, str]]], dict[str, list[dict[str, str]]]]:
        one_map: dict[str, list[dict[str, str]]] = {}
        many_map: dict[str, list[dict[str, str]]] = {}

        for rel in self._relations():
            resolved_one = self._resolve_table_name(rel["one"], table_names)
            resolved_many = self._resolve_table_name(rel["many"], table_names)
            if resolved_one is None or resolved_many is None:
                continue

            parent_attr = self._to_snake_case(self._singularize(resolved_one))
            children_attr = f"{self._to_snake_case(resolved_many)}_items"
            fk_field = f"{parent_attr}_id"

            entry = {
                "one_table": resolved_one,
                "many_table": resolved_many,
                "one_class": class_name_map[resolved_one],
                "many_class": class_name_map[resolved_many],
                "parent_attr": parent_attr,
                "children_attr": children_attr,
                "fk_field": fk_field,
            }

            many_map.setdefault(resolved_many, []).append(entry)
            one_map.setdefault(resolved_one, []).append(entry)

        return one_map, many_map

    def _generate_backend_main_py(self) -> str:
        database = self._database_schema()
        backend_apis = self._backend_apis()
        injected_role_tables: set[str] = set()

        users_table: str | None = None
        for table_name in database:
            if table_name.lower() == "users":
                users_table = table_name
                break
        if users_table is not None:
            users_fields = database.get(users_table, {})
            if isinstance(users_fields, dict):
                has_role = any(str(field_name).strip().lower() == "role" for field_name in users_fields)
                if not has_role:
                    users_fields["role"] = "str"
                    injected_role_tables.add(users_table)

        table_names = list(database.keys())
        class_name_map = {table: self._to_pascal_case(table) for table in table_names}
        schema_name_map = {table: f"{self._to_pascal_case(table)}Schema" for table in table_names}

        one_rel_map, many_rel_map = self._build_relation_maps(table_names, class_name_map)

        lines: list[str] = []
        lines.append("from datetime import datetime, timedelta, timezone")
        lines.append("import jwt")
        lines.append("from fastapi import FastAPI, Depends, HTTPException, status")
        lines.append("from fastapi.security import OAuth2PasswordBearer")
        lines.append("from passlib.context import CryptContext")
        lines.append("from pydantic import BaseModel")
        lines.append("from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey")
        lines.append("from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship")
        lines.append("")
        lines.append('SQLALCHEMY_DATABASE_URL = "sqlite:///./ail_data.db"')
        lines.append('engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})')
        lines.append("SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)")
        lines.append("Base = declarative_base()")
        lines.append("")
        lines.append("SECRET_KEY = \"change-this-secret-in-production\"")
        lines.append("ALGORITHM = \"HS256\"")
        lines.append("ACCESS_TOKEN_EXPIRE_MINUTES = 120")
        lines.append("pwd_context = CryptContext(schemes=[\"bcrypt\"], deprecated=\"auto\")")
        lines.append("pwd_fallback_context = CryptContext(schemes=[\"pbkdf2_sha256\"], deprecated=\"auto\")")
        lines.append("oauth2_scheme = OAuth2PasswordBearer(tokenUrl=\"/api/login\")")
        lines.append("")
        lines.append("def get_db():")
        lines.append("    db = SessionLocal()")
        lines.append("    try:")
        lines.append("        yield db")
        lines.append("    finally:")
        lines.append("        db.close()")
        lines.append("")

        table_field_names: dict[str, list[str]] = {}
        relation_fk_fields: dict[str, list[str]] = {}

        for table_name, fields in database.items():
            class_name = class_name_map[table_name]
            relation_entries_many = many_rel_map.get(table_name, [])
            relation_entries_one = one_rel_map.get(table_name, [])

            declared_fields: list[tuple[str, str]] = []
            for field_name, field_type in fields.items():
                declared_fields.append((self._to_snake_case(field_name), field_type))

            field_name_set = {field_name for field_name, _ in declared_fields}
            fk_fields_for_table: list[str] = []
            for rel_entry in relation_entries_many:
                fk_field = rel_entry["fk_field"]
                if fk_field not in field_name_set and fk_field not in fk_fields_for_table:
                    fk_fields_for_table.append(fk_field)

            relation_fk_fields[table_name] = fk_fields_for_table
            table_field_names[table_name] = [field_name for field_name, _ in declared_fields] + fk_fields_for_table

            lines.append(f"class {class_name}(Base):")
            lines.append(f'    __tablename__ = "{table_name}"')
            lines.append("    id = Column(Integer, primary_key=True, index=True)")

            for field_name, field_type in declared_fields:
                if (
                    table_name in injected_role_tables
                    and field_name == "role"
                    and self._normalize_ast_type(field_type) == "str"
                ):
                    lines.append('    role = Column(String, default="user")')
                else:
                    lines.append(f"    {field_name} = Column({self._to_sqlalchemy_type(field_type)})")

            for rel_entry in relation_entries_many:
                fk_field = rel_entry["fk_field"]
                if fk_field in field_name_set:
                    continue
                lines.append(
                    f'    {fk_field} = Column(Integer, ForeignKey("{rel_entry["one_table"]}.id"))'
                )

            for rel_entry in relation_entries_many:
                lines.append(
                    f'    {rel_entry["parent_attr"]} = relationship("{rel_entry["one_class"]}", '
                    f'back_populates="{rel_entry["children_attr"]}")'
                )

            for rel_entry in relation_entries_one:
                lines.append(
                    f'    {rel_entry["children_attr"]} = relationship("{rel_entry["many_class"]}", '
                    f'back_populates="{rel_entry["parent_attr"]}")'
                )

            lines.append("")

            schema_name = schema_name_map[table_name]
            lines.append(f"class {schema_name}(BaseModel):")
            if not declared_fields:
                lines.append("    pass")
            else:
                for field_name, field_type in declared_fields:
                    lines.append(f"    {field_name}: {self._to_python_type(field_type)}")
            lines.append("")

        auth_apis = [api for api in backend_apis if str(api.get("action_kind", "")).upper() == "AUTH"]
        has_auth = any(
            str(api.get("action_kind", "")).upper() == "AUTH"
            or str(api.get("action", "")).strip().startswith(">DB_AUTH[")
            for api in backend_apis
        )
        has_role_guard = any(isinstance(api.get("auth_role"), str) and api.get("auth_role").strip() for api in backend_apis)
        auth_tables: list[str] = []
        for api in auth_apis:
            table_name = str(api.get("table", "")).strip()
            resolved = self._resolve_table_name(table_name, table_names)
            if resolved and resolved not in auth_tables:
                auth_tables.append(resolved)

        if has_auth and not auth_tables:
            if "users" in class_name_map:
                auth_tables.append("users")
            elif table_names:
                auth_tables.append(table_names[0])

        auth_schema_meta: dict[str, dict[str, str]] = {}
        for auth_table in auth_tables:
            request_name = f"{class_name_map[auth_table]}AuthRequest"
            field_names = table_field_names.get(auth_table, [])
            identifier_field = self._pick_identifier_field(field_names)
            password_input_field = "password"
            password_storage_field = self._pick_password_storage_field(field_names)

            lines.append(f"class {request_name}(BaseModel):")
            lines.append(f"    {identifier_field}: str")
            lines.append(f"    {password_input_field}: str")
            lines.append("")

            auth_schema_meta[auth_table] = {
                "request_name": request_name,
                "identifier_field": identifier_field,
                "password_input_field": password_input_field,
                "password_storage_field": password_storage_field,
            }

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

        if has_auth and auth_tables:
            primary_auth_table = "users" if "users" in class_name_map else auth_tables[0]
            primary_auth_class = class_name_map[primary_auth_table]
            primary_auth_meta = auth_schema_meta.get(primary_auth_table, {})
            primary_fields = table_field_names.get(primary_auth_table, [])
            register_identifier_field = "username" if "username" in primary_fields else str(
                primary_auth_meta.get("identifier_field", "username")
            )
            register_password_field = "pwd" if "pwd" in primary_fields else str(
                primary_auth_meta.get("password_storage_field", "pwd")
            )
            register_role_field = "role" if "role" in primary_fields else None

            lines.append("def verify_password(plain_password: str, hashed_password: str) -> bool:")
            lines.append("    try:")
            lines.append("        return pwd_context.verify(plain_password, hashed_password)")
            lines.append("    except Exception:")
            lines.append("        try:")
            lines.append("            return pwd_fallback_context.verify(plain_password, hashed_password)")
            lines.append("        except Exception:")
            lines.append("            return False")
            lines.append("")

            lines.append("def get_password_hash(password: str) -> str:")
            lines.append("    try:")
            lines.append("        return pwd_context.hash(password)")
            lines.append("    except Exception:")
            lines.append("        return pwd_fallback_context.hash(password)")
            lines.append("")

            lines.append("class RegisterRequest(BaseModel):")
            lines.append("    username: str")
            lines.append("    password: str")
            lines.append("    role: str | None = None")
            lines.append("")

            lines.append("def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:")
            lines.append("    to_encode = data.copy()")
            lines.append("    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))")
            lines.append("    to_encode.update({\"exp\": expire})")
            lines.append("    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)")
            lines.append("")

            lines.append("def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> dict:")
            lines.append("    credentials_exception = HTTPException(")
            lines.append("        status_code=status.HTTP_401_UNAUTHORIZED,")
            lines.append("        detail=\"Could not validate credentials\",")
            lines.append("        headers={\"WWW-Authenticate\": \"Bearer\"},")
            lines.append("    )")
            lines.append("    try:")
            lines.append("        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])")
            lines.append("        user_id = payload.get(\"sub\")")
            lines.append("        if user_id is None:")
            lines.append("            raise credentials_exception")
            lines.append("        user_id = int(user_id)")
            lines.append("    except Exception:")
            lines.append("        raise credentials_exception")
            lines.append("")
            lines.append(f"    user = db.query({primary_auth_class}).filter({primary_auth_class}.id == user_id).first()")
            lines.append("    if user is None:")
            lines.append("        raise credentials_exception")
            lines.append(f"    username = getattr(user, \"{register_identifier_field}\", None) or getattr(user, \"username\", \"\")")
            lines.append('    role = getattr(user, "role", "user") or "user"')
            lines.append('    return {"id": user.id, "username": username, "role": role}')
            lines.append("")

            if has_role_guard:
                lines.append("def require_role(required: str):")
                lines.append("    def _checker(current_user: dict = Depends(get_current_user)) -> dict:")
                lines.append('        current_role = str(current_user.get("role", "")).strip().lower()')
                lines.append('        allowed_roles = [r.strip().lower() for r in str(required).split("|") if r.strip()]')
                lines.append("        if not allowed_roles:")
                lines.append('            raise HTTPException(status_code=403, detail="Forbidden")')
                lines.append("        if current_role not in allowed_roles:")
                lines.append('            raise HTTPException(status_code=403, detail="Forbidden")')
                lines.append("        return current_user")
                lines.append("    return _checker")
            lines.append("")

            has_register_route = any(
                str(api.get("route", "")).strip() == "/api/register"
                and str(api.get("method", "GET")).upper() in {"POST", "AUTH"}
                for api in backend_apis
            )
            has_me_route = any(
                str(api.get("route", "")).strip() == "/api/me"
                and str(api.get("method", "GET")).upper() in {"GET", "AUTH"}
                for api in backend_apis
            )
            if not has_me_route:
                lines.append("@app.get(\"/api/me\")")
                lines.append("async def get_api_me(current_user: dict = Depends(get_current_user)):")
                lines.append(
                    '    return {"id": current_user.get("id"), '
                    '"username": current_user.get("username", ""), '
                    '"role": current_user.get("role", "user")}'
                )
                lines.append("")
            if not has_register_route:
                lines.append("@app.post(\"/api/register\")")
                lines.append("async def post_api_register(payload: RegisterRequest, db: Session = Depends(get_db)):")
                lines.append(
                    f"    existing_user = db.query({primary_auth_class}).filter("
                    f"{primary_auth_class}.{register_identifier_field} == payload.username"
                    ").first()"
                )
                lines.append("    if existing_user is not None:")
                lines.append("        raise HTTPException(status_code=409, detail=\"Username already exists\")")
                lines.append("    requested_role = (payload.role or \"user\").strip().lower()")
                lines.append("    if requested_role != \"user\":")
                lines.append("        raise HTTPException(status_code=403, detail=\"Only user role can be self-registered\")")
                lines.append("    hashed = get_password_hash(payload.password)")
                if register_role_field:
                    lines.append(
                        f"    new_user = {primary_auth_class}("
                        f"{register_identifier_field}=payload.username, {register_password_field}=hashed, "
                        f"{register_role_field}=requested_role"
                        ")"
                    )
                else:
                    lines.append(
                        f"    new_user = {primary_auth_class}("
                        f"{register_identifier_field}=payload.username, {register_password_field}=hashed"
                        ")"
                    )
                lines.append("    db.add(new_user)")
                lines.append("    db.commit()")
                lines.append("    db.refresh(new_user)")
                lines.append(
                    f"    return {{\"id\": new_user.id, \"username\": getattr(new_user, \"{register_identifier_field}\", payload.username)}}"
                )
                lines.append("")
        elif any(bool(api.get("requires_auth")) for api in backend_apis):
            lines.append("def get_current_user() -> dict:")
            lines.append("    raise HTTPException(status_code=503, detail=\"Auth backend not configured\")")
            lines.append("")

        auth_fk_by_table: dict[str, str] = {}
        for table_name in table_names:
            for rel_entry in many_rel_map.get(table_name, []):
                if rel_entry["one_table"] in auth_tables:
                    auth_fk_by_table[table_name] = rel_entry["fk_field"]
                    break

        for api in backend_apis:
            method = str(api.get("method", "GET")).upper()
            route = str(api.get("route", "/"))
            action = str(api.get("action", ""))
            action_kind = str(api.get("action_kind", "")).upper()
            table_name = str(api.get("table", ""))
            requires_auth = bool(api.get("requires_auth", False))
            raw_auth_role = api.get("auth_role", "")
            auth_role = raw_auth_role.strip() if isinstance(raw_auth_role, str) else ""
            if auth_role:
                requires_auth = True

            resolved_table = self._resolve_table_name(table_name, table_names)
            model_name = class_name_map.get(resolved_table) if resolved_table else None
            schema_name = schema_name_map.get(resolved_table) if resolved_table else None

            route_slug = route.strip("/").replace("/", "_") or "root"
            func_name = self._to_snake_case(f"{method.lower()}_{route_slug}")

            decorator_method = "post" if method == "AUTH" else method.lower()
            if decorator_method not in {"get", "post", "put", "patch", "delete"}:
                decorator_method = "post"
            lines.append(f"@app.{decorator_method}(\"{route}\")")

            params: list[str] = []
            if action_kind == "INS":
                params.append(f"payload: {schema_name or 'dict'}")
            elif action_kind == "AUTH":
                if resolved_table and resolved_table in auth_schema_meta:
                    params.append(f"payload: {auth_schema_meta[resolved_table]['request_name']}")
                else:
                    params.append("payload: dict")

            params.append("db: Session = Depends(get_db)")
            if requires_auth:
                params.append("current_user: dict = Depends(get_current_user)")
            if auth_role:
                params.append(f'role_guard: dict = Depends(require_role("{auth_role}"))')

            lines.append(f"async def {func_name}({', '.join(params)}):")

            if action_kind == "SEL" and model_name:
                lines.append(f"    query = db.query({model_name})")
                if requires_auth and resolved_table in auth_fk_by_table:
                    fk_field = auth_fk_by_table[resolved_table]
                    lines.append(f"    query = query.filter({model_name}.{fk_field} == current_user[\"id\"])")
                lines.append("    rows = query.all()")
                fields_list = table_field_names.get(resolved_table, []) if resolved_table else []
                fields_literal = ", ".join(f'\"{field}\"' for field in fields_list)
                lines.append(f"    fields = [{fields_literal}]")
                lines.append("    return [_serialize_row(row, fields) for row in rows]")
            elif action_kind == "INS" and model_name:
                lines.append("    payload_data = _model_dump(payload) if isinstance(payload, BaseModel) else payload")
                fields_list = table_field_names.get(resolved_table, []) if resolved_table else []
                owner_fields: list[str] = []
                if requires_auth:
                    for owner_field in ("author_id", "user_id", "owner_id"):
                        if owner_field in fields_list:
                            owner_fields.append(owner_field)
                            lines.append(f"    payload_data[\"{owner_field}\"] = current_user[\"id\"]")
                if requires_auth and resolved_table in auth_fk_by_table:
                    fk_field = auth_fk_by_table[resolved_table]
                    if fk_field not in owner_fields:
                        lines.append(f"    payload_data[\"{fk_field}\"] = current_user[\"id\"]")
                lines.append(f"    record = {model_name}(**payload_data)")
                lines.append("    db.add(record)")
                lines.append("    db.commit()")
                lines.append("    db.refresh(record)")
                fields_literal = ", ".join(f'\"{field}\"' for field in fields_list)
                lines.append(f"    fields = [{fields_literal}]")
                lines.append("    return _serialize_row(record, fields)")
            elif action_kind == "AUTH" and model_name and resolved_table in auth_schema_meta:
                meta = auth_schema_meta[resolved_table]
                identifier_field = meta["identifier_field"]
                password_input_field = meta["password_input_field"]
                password_storage_field = meta["password_storage_field"]
                lines.append("    payload_data = _model_dump(payload) if isinstance(payload, BaseModel) else payload")
                lines.append(f"    identifier = payload_data.get(\"{identifier_field}\")")
                lines.append(f"    plain_password = payload_data.get(\"{password_input_field}\", \"\")")
                lines.append("    if not identifier or not plain_password:")
                lines.append("        raise HTTPException(status_code=400, detail=\"Missing credentials\")")
                lines.append(f"    user = db.query({model_name}).filter({model_name}.{identifier_field} == identifier).first()")
                lines.append("    if user is None:")
                lines.append("        raise HTTPException(status_code=401, detail=\"Invalid credentials\")")
                lines.append(
                    f"    stored_password = getattr(user, \"{password_storage_field}\", None) "
                    "or getattr(user, \"pwd\", None) "
                    "or getattr(user, \"password_hash\", None) "
                    "or getattr(user, \"password\", None)"
                )
                lines.append("    if not stored_password or not verify_password(plain_password, stored_password):")
                lines.append("        raise HTTPException(status_code=401, detail=\"Invalid credentials\")")
                lines.append("    access_token = create_access_token({\"sub\": str(user.id)})")
                lines.append("    return {\"access_token\": access_token, \"token_type\": \"bearer\", \"user_id\": user.id}")
            else:
                lines.append(f"    # TODO: execute {action}")
                lines.append("    return {\"status\": \"ok\"}")

            lines.append("")

        return "\n".join(lines).rstrip() + "\n"

    def _generate_vue_view(self, page: dict[str, Any]) -> str:
        components = page.get("components", [])
        if not isinstance(components, list):
            components = []

        imports: list[str] = []
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
                        imports.append(
                            f"import {component_name} from '@/components/ui/{module_name}/{component_name}.vue'"
                        )
                        imported.add(key)
                else:
                    key = (source or "local", component_name)
                    if key not in imported:
                        imports.append(f"import {component_name} from '@/components/{component_name}.vue'")
                        imported.add(key)

                props = self._parse_component_config(config)
                attrs = " ".join(f'{k}="{html.escape(v, quote=True)}"' for k, v in props.items())
                if attrs:
                    template_lines.append(f"    <{component_name} {attrs} />")
                else:
                    template_lines.append(f"    <{component_name} />")
            else:
                comp_type = str(item.get("type", "Component")).strip() or "Component"
                config = str(item.get("config", "")).strip()
                component_name = self._sanitize_vue_component_identifier(comp_type)

                key = ("legacy", component_name)
                if key not in imported:
                    imports.append(f"import {component_name} from '@/components/{component_name}.vue'")
                    imported.add(key)

                props = self._parse_component_config(config)
                attrs = " ".join(f'{k}="{html.escape(v, quote=True)}"' for k, v in props.items())
                if attrs:
                    template_lines.append(f"    <{component_name} {attrs} />")
                else:
                    template_lines.append(f"    <{component_name} />")

        if not template_lines:
            template_lines.append("    <div>No components declared.</div>")

        template_block = "\n".join(template_lines)
        script_block = "\n".join(imports)

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
        components: list[str] = []
        seen: set[str] = set()

        for page in self._frontend_pages():
            items = page.get("components", [])
            if not isinstance(items, list):
                continue

            for item in items:
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
                    components.append(kebab)

        return components

    def _write_setup_ui_script(self, project_root: Path) -> None:
        components = self._collect_shadcn_components()
        lines = ["#!/bin/bash", "set -e"]
        if components:
            for component in components:
                lines.append(f"npx shadcn-vue@latest add {component}")
        else:
            lines.append("# no shadcn components detected")

        script_path = project_root / "setup_ui.sh"
        script_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        script_path.chmod(0o755)

    def _write_start_script(self, project_root: Path) -> None:
        lines = [
            "#!/bin/bash",
            "set -euo pipefail",
            "",
            'echo "🚀 正在点燃 AIL 全栈引擎..."',
            'cd "$(dirname "$0")"',
            "",
            "(",
            "  cd backend",
            "  uvicorn main:app --reload --port 8000",
            ") &",
            "BACKEND_PID=$!",
            'echo "🛰️ 后端已启动，PID: ${BACKEND_PID}"',
            "",
            "(",
            "  cd frontend",
            "  npm run dev",
            ") &",
            "FRONTEND_PID=$!",
            'echo "🎨 前端已启动，PID: ${FRONTEND_PID}"',
            "",
            "cleanup() {",
            '  echo ""',
            '  echo "🛑 捕获退出信号，正在优雅关闭前后端进程..."',
            "  kill \"${BACKEND_PID}\" \"${FRONTEND_PID}\" 2>/dev/null || true",
            "  wait \"${BACKEND_PID}\" \"${FRONTEND_PID}\" 2>/dev/null || true",
            '  echo "✅ 全栈引擎已安全熄火。"',
            "}",
            "",
            "trap cleanup SIGINT SIGTERM",
            "wait",
        ]

        script_path = project_root / "start.sh"
        script_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        script_path.chmod(0o755)


if __name__ == "__main__":
    ail_code = (
        "^SYS[BlogV4]"
        "~#LIB[shadcn-vue]"
        "~>DB_TABLE[users]{username:str,password_hash:str}"
        "~>DB_TABLE[posts]{title:str,content:text}"
        "~>DB_REL[users(1)->posts(N)]"
        "~@API[AUTH,/api/login]{>DB_AUTH[users]}"
        "~@API[POST,/api/posts]{>DB_INS[posts]*AUTH}"
        "~@API[GET,/api/posts]{>DB_SEL[posts]*AUTH}"
        "~@PAGE[Home,/]"
        "~#UI[shadcn:Navbar]{theme:dark}"
        "~#UI[shadcn:Card]{layout:grid}"
    )

    parser = AILParserV4(ail_code)
    ast = parser.parse()
    print(json.dumps(ast, indent=4, ensure_ascii=False))

    generator = AILProjectGeneratorV4(ast)
    output_path = generator.build_project()
    print(f"Generated project: {output_path}")
