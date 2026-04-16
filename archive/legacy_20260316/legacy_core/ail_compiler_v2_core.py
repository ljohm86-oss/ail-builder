from __future__ import annotations

import json
import re
from dataclasses import dataclass


@dataclass
class APIAction:
    method: str
    route: str
    action: str


class AILParserV2:
    SYS_PATTERN = re.compile(r"^\^SYS\[([^\]]+)\]$")
    DB_TABLE_PATTERN = re.compile(r"^>DB_TABLE\[([^\]]+)\]\{(.*)\}$", re.S)
    API_PATTERN = re.compile(r"^@API\[([^,\]]+),([^\]]+)\]\{(.*)\}$", re.S)
    API_ACTION_PATTERN = re.compile(r"^>DB_(SEL|INS)\[([^\]]+)\]$")
    PAGE_PATTERN = re.compile(r"^@PAGE\[([^,\]]+),([^\]]+)\]$")
    COMP_PATTERN = re.compile(r"^#COMP\[([^\]]+)\]\{(.*)\}$", re.S)
    FIELD_PATTERN = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)(?::(str|int|text))?$")
    IDENT_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

    def __init__(self, ail_code: str) -> None:
        self.ail_code = ail_code

    def split_actions(self) -> list[str]:
        """Split by '~' while ignoring separators inside quotes and bracket scopes."""
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

    def parse(self) -> dict[str, object]:
        ast: dict[str, object] = {
            "system_name": None,
            "database": {},
            "backend_apis": [],
            "frontend_pages": [],
        }

        current_page: dict[str, object] | None = None

        for raw_action in self.split_actions():
            action = raw_action.strip()

            sys_match = self.SYS_PATTERN.fullmatch(action)
            if sys_match:
                ast["system_name"] = sys_match.group(1).strip()
                continue

            db_match = self.DB_TABLE_PATTERN.fullmatch(action)
            if db_match:
                table_name = db_match.group(1).strip()
                if not self.IDENT_PATTERN.fullmatch(table_name):
                    raise ValueError(f"Invalid table name: {table_name}")
                fields = self._parse_fields(db_match.group(2).strip(), table_name)
                database = ast["database"]
                assert isinstance(database, dict)
                database[table_name] = fields
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
                    raise ValueError(
                        "Invalid API action: must be >DB_SEL[table] or >DB_INS[table]"
                    )
                action_table = action_match.group(2).strip()
                if not self.IDENT_PATTERN.fullmatch(action_table):
                    raise ValueError(f"Invalid API action table name: {action_table}")

                backend_apis = ast["backend_apis"]
                assert isinstance(backend_apis, list)
                backend_apis.append(
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

                current_page = {
                    "name": page_name,
                    "path": page_path,
                    "components": [],
                }
                frontend_pages = ast["frontend_pages"]
                assert isinstance(frontend_pages, list)
                frontend_pages.append(current_page)
                continue

            comp_match = self.COMP_PATTERN.fullmatch(action)
            if comp_match:
                if current_page is None:
                    raise ValueError("#COMP must appear after @PAGE")

                component_type = comp_match.group(1).strip()
                config = comp_match.group(2).strip()
                if not component_type:
                    raise ValueError("Component type cannot be empty")

                components = current_page["components"]
                assert isinstance(components, list)
                components.append(
                    {
                        "type": component_type,
                        "config": config,
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
        segments = [segment.strip() for segment in fields_blob.split(",") if segment.strip()]
        if not segments:
            raise ValueError(f"Table {table_name} must declare at least one field")

        for segment in segments:
            field_match = self.FIELD_PATTERN.fullmatch(segment)
            if not field_match:
                raise ValueError(f"Invalid field declaration in {table_name}: {segment}")

            field_name, field_type = field_match.groups()
            if field_name in fields:
                raise ValueError(f"Duplicate field name in {table_name}: {field_name}")
            fields[field_name] = field_type or "str"

        return fields


if __name__ == "__main__":
    ail_code = "^SYS[CSDN_Clone]~>DB_TABLE[users]{uid:int,name:str}~>DB_TABLE[posts]{title:str,content:text}~@API[GET,/api/posts]{>DB_SEL[posts]}~@PAGE[Home,/]~#COMP[Navbar]{auth=true}~#COMP[List]{api=/api/posts}"

    parser = AILParserV2(ail_code)
    ast = parser.parse()
    print(json.dumps(ast, indent=4, ensure_ascii=False))
