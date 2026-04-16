from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

MANAGED_ROOTS = [
    "src/views/generated/",
    "src/router/generated/",
    "backend/generated/",
    "src/ail_generated/",
    "frontend/src/ail-managed/",
]

USER_ROOTS = [
    "src/custom/",
    "src/extensions/",
    "src/theme/",
    "backend/custom/",
    "frontend/src/ail-overrides/",
    "frontend/public/ail-overrides/",
]


@dataclass(frozen=True)
class ProjectContext:
    root: Path
    ail_dir: Path
    source_file: Path
    manifest_file: Path
    last_build_file: Path
    patches_dir: Path
    project_id: str

    @classmethod
    def discover(cls, start: Path | None = None, allow_uninitialized: bool = False) -> "ProjectContext":
        current = (start or Path.cwd()).resolve()
        for candidate in [current, *current.parents]:
            ail_dir = candidate / ".ail"
            if ail_dir.exists() and ail_dir.is_dir():
                return cls.from_root(candidate)
        if allow_uninitialized:
            return cls.from_root(current)
        raise FileNotFoundError("AIL project not initialized. Run 'ail init' first.")

    @classmethod
    def from_root(cls, root: Path) -> "ProjectContext":
        root = root.resolve()
        ail_dir = root / ".ail"
        return cls(
            root=root,
            ail_dir=ail_dir,
            source_file=ail_dir / "source.ail",
            manifest_file=ail_dir / "manifest.json",
            last_build_file=ail_dir / "last_build.json",
            patches_dir=ail_dir / "patches",
            project_id=_slugify_project_id(root.name),
        )

    def to_relative(self, path: Path) -> str:
        return path.resolve().relative_to(self.root).as_posix()

    def is_managed_relpath(self, relpath: str) -> bool:
        normalized = _normalize_relpath(relpath)
        return any(normalized.startswith(prefix) for prefix in MANAGED_ROOTS)

    def is_user_relpath(self, relpath: str) -> bool:
        normalized = _normalize_relpath(relpath)
        return any(normalized.startswith(prefix) for prefix in USER_ROOTS)

    def resolve_managed_path(self, relpath: str) -> Path:
        normalized = _normalize_relpath(relpath)
        if not self.is_managed_relpath(normalized):
            raise ValueError(f"Path is not inside a managed root: {relpath}")
        if self.is_user_relpath(normalized):
            raise ValueError(f"Path targets a user zone: {relpath}")
        target = (self.root / normalized).resolve()
        try:
            target.relative_to(self.root)
        except ValueError as exc:
            raise ValueError(f"Path escapes project root: {relpath}") from exc
        return target


def _slugify_project_id(name: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_]+", "_", (name or "project").strip())
    slug = re.sub(r"_+", "_", slug).strip("_") or "project"
    return f"proj_{slug}"


def _normalize_relpath(relpath: str) -> str:
    normalized = (relpath or "").replace("\\", "/").lstrip("/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    if normalized.startswith("../") or "/../" in normalized or normalized == "..":
        raise ValueError(f"Path traversal is not allowed: {relpath}")
    return normalized
