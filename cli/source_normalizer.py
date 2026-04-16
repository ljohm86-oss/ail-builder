from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable


@dataclass(frozen=True)
class NormalizationResult:
    text: str
    removed_flow: bool
    normalized_ui: bool
    inserted_sys: bool
    inserted_sys_name: str

    @property
    def warnings(self) -> list[str]:
        messages: list[str] = []
        if self.removed_flow:
            messages.append("removed #FLOW lines for current compiler compatibility")
        if self.normalized_ui:
            messages.append("normalized bare #UI tokens to #UI[...]{} for current compiler compatibility")
        if self.inserted_sys:
            messages.append(f"inserted ^SYS[{self.inserted_sys_name}] for current compiler compatibility")
        return messages


@dataclass(frozen=True)
class UserSourceNormalizationResult:
    text: str
    removed_sys: bool

    @property
    def warnings(self) -> list[str]:
        if self.removed_sys:
            return ["removed ^SYS lines before persisting user source"]
        return []


def normalize_for_user_source(ail_text: str | Iterable[str]) -> UserSourceNormalizationResult:
    if isinstance(ail_text, str):
        lines = [line.strip() for line in ail_text.splitlines() if line.strip()]
    else:
        lines = [str(line).strip() for line in ail_text if str(line).strip()]

    filtered: list[str] = []
    removed_sys = False
    for line in lines:
        if line.startswith("^SYS["):
            removed_sys = True
            continue
        filtered.append(line)

    return UserSourceNormalizationResult(
        text="\n".join(filtered).strip(),
        removed_sys=removed_sys,
    )


def normalize_for_current_compile(ail_text: str | Iterable[str], *, system_name: str = "CLIProject") -> NormalizationResult:
    if isinstance(ail_text, str):
        lines = [line for line in ail_text.splitlines() if line.strip()]
    else:
        lines = [str(line).strip() for line in ail_text if str(line).strip()]

    filtered: list[str] = []
    removed_flow = False
    normalized_ui = False
    inserted_sys = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#FLOW["):
            removed_flow = True
            continue
        if stripped.startswith("#UI[") and "{" not in stripped and stripped.endswith("]"):
            filtered.append(f"{stripped}{{}}")
            normalized_ui = True
            continue
        filtered.append(stripped)

    safe_system_name = _normalize_system_name(system_name)
    if filtered and not filtered[0].startswith("^SYS["):
        filtered.insert(0, f"^SYS[{safe_system_name}]")
        inserted_sys = True

    return NormalizationResult(
        text="\n".join(filtered).strip(),
        removed_flow=removed_flow,
        normalized_ui=normalized_ui,
        inserted_sys=inserted_sys,
        inserted_sys_name=safe_system_name,
    )


def _normalize_system_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_]", "", (value or "").strip().replace(" ", "_"))
    cleaned = cleaned or "CLIProject"
    if cleaned[0].isdigit():
        cleaned = f"Project_{cleaned}"
    return cleaned
