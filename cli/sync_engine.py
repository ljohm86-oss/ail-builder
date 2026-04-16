from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .context import ProjectContext
from .manifest_service import ManifestService


class SyncError(RuntimeError):
    pass


@dataclass
class SyncResult:
    written: int
    deleted: int
    conflicts: list[dict[str, str]]
    backups_created: list[str]
    conflict_summary: str | None = None


class SyncEngine:
    def __init__(self, manifest_service: ManifestService | None = None) -> None:
        self.manifest_service = manifest_service or ManifestService()

    def detect_conflicts(
        self,
        context: ProjectContext,
        build_payload: dict[str, Any],
        current_manifest: dict[str, Any],
    ) -> list[dict[str, str]]:
        files = list(build_payload.get("files") or [])
        deleted_files = list(build_payload.get("deleted_files") or [])
        incoming_manifest = build_payload.get("manifest") or {}
        self._validate_build_payload(context, files, deleted_files, incoming_manifest)
        return self._detect_conflicts(context, files, deleted_files, current_manifest)

    def sync(
        self,
        context: ProjectContext,
        build_payload: dict[str, Any],
        current_manifest: dict[str, Any],
        *,
        backup_and_overwrite: bool = False,
    ) -> SyncResult:
        files = list(build_payload.get("files") or [])
        deleted_files = list(build_payload.get("deleted_files") or [])
        incoming_manifest = build_payload.get("manifest") or {}
        self._validate_build_payload(context, files, deleted_files, incoming_manifest)

        conflicts = self._detect_conflicts(context, files, deleted_files, current_manifest)
        if conflicts:
            if not backup_and_overwrite:
                raise SyncError(self._format_conflict_error(conflicts))
            backups_created, conflict_summary = self._backup_conflicts(context, build_payload, conflicts)
        else:
            backups_created = []
            conflict_summary = None

        written = 0
        for item in files:
            target = context.resolve_managed_path(item["path"])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(item["content"], encoding="utf-8")
            written += 1

        deleted = 0
        for relpath in deleted_files:
            target = context.resolve_managed_path(relpath)
            if target.exists():
                target.unlink()
                deleted += 1

        return SyncResult(
            written=written,
            deleted=deleted,
            conflicts=conflicts,
            backups_created=backups_created,
            conflict_summary=conflict_summary,
        )

    def _validate_build_payload(
        self,
        context: ProjectContext,
        files: list[dict[str, Any]],
        deleted_files: list[str],
        manifest: dict[str, Any],
    ) -> None:
        if not manifest:
            raise SyncError("Last build payload does not contain manifest data.")
        for item in files:
            relpath = item.get("path") or ""
            context.resolve_managed_path(relpath)
        for relpath in deleted_files:
            context.resolve_managed_path(relpath)

    def _detect_conflicts(
        self,
        context: ProjectContext,
        files: list[dict[str, Any]],
        deleted_files: list[str],
        current_manifest: dict[str, Any],
    ) -> list[dict[str, str]]:
        conflicts: list[dict[str, str]] = []
        managed_files = (current_manifest or {}).get("managed_files") or {}

        for item in files:
            relpath = item["path"]
            local_path = context.resolve_managed_path(relpath)
            manifest_entry = managed_files.get(relpath)
            if not manifest_entry or not local_path.exists():
                continue
            manifest_sha = str(manifest_entry.get("sha256") or "")
            local_sha = self.manifest_service.sha256_file(local_path)
            if local_sha != manifest_sha:
                conflicts.append({"path": relpath, "level": "2", "reason": "local drift detected"})

        for relpath in deleted_files:
            local_path = context.resolve_managed_path(relpath)
            manifest_entry = managed_files.get(relpath)
            if not manifest_entry or not local_path.exists():
                continue
            manifest_sha = str(manifest_entry.get("sha256") or "")
            local_sha = self.manifest_service.sha256_file(local_path)
            if local_sha != manifest_sha:
                conflicts.append({"path": relpath, "level": "3", "reason": "local drift on file scheduled for deletion"})

        return conflicts

    def _backup_conflicts(
        self,
        context: ProjectContext,
        build_payload: dict[str, Any],
        conflicts: list[dict[str, str]],
    ) -> tuple[list[str], str]:
        build_id = str(build_payload.get("build_id") or "unknown_build")
        created: list[str] = []
        for item in conflicts:
            relpath = item["path"]
            source = context.resolve_managed_path(relpath)
            if not source.exists():
                continue
            backup_relpath = self._backup_relpath(relpath)
            backup_target = context.ail_dir / "conflicts" / build_id / backup_relpath
            backup_target.parent.mkdir(parents=True, exist_ok=True)
            backup_target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            created.append(backup_target.relative_to(context.root).as_posix())
        summary_relpath = f".ail/conflicts/{build_id}/summary.md"
        summary_target = context.root / summary_relpath
        summary_target.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "# Managed Conflict Backup Summary",
            "",
            "The following managed files were locally modified before sync and were backed up.",
            "",
            "Recommended next step:",
            "",
            "- move structure/content changes back into `.ail/source.ail`",
            "- move visual customization into `frontend/src/ail-overrides/theme.tokens.css` or `frontend/src/ail-overrides/custom.css`",
            "",
            "Backed up files:",
            "",
        ]
        for item in conflicts:
            lines.append(f"- `{item['path']}` | Level {item['level']} | {item['reason']}")
        lines.append("")
        lines.append("Backup copies:")
        lines.append("")
        for item in created:
            lines.append(f"- `{item}`")
        summary_target.write_text("\n".join(lines) + "\n", encoding="utf-8")
        created.append(summary_relpath)
        return created, summary_relpath

    def _backup_relpath(self, relpath: str) -> str:
        path = Path(relpath)
        suffixes = path.suffixes
        if suffixes:
            full_suffix = "".join(suffixes)
            backup_name = f"{path.name[:-len(full_suffix)]}.local{full_suffix}"
        else:
            backup_name = f"{path.name}.local"
        return path.with_name(backup_name).as_posix()

    def _format_conflict_error(self, conflicts: list[dict[str, str]]) -> str:
        details = "; ".join(
            f"{item['path']} (Level {item['level']}: {item['reason']})" for item in conflicts
        )
        return (
            "Conflict detected. Refusing to silently overwrite locally modified managed files: "
            f"{details}. Move durable changes into .ail/source.ail or frontend/src/ail-overrides/, "
            "or rerun with --backup-and-overwrite to save copies under .ail/conflicts/<build_id>/ before overwrite."
        )
