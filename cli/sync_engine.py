from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .context import ProjectContext
from .manifest_service import ManifestService


class SyncError(RuntimeError):
    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.details = details or {}


@dataclass
class SyncResult:
    written: int
    deleted: int
    conflicts: list[dict[str, Any]]
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
    ) -> list[dict[str, Any]]:
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
                raise SyncError(
                    self._format_conflict_error(conflicts),
                    details=self.explain_conflicts(conflicts),
                )
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
    ) -> list[dict[str, Any]]:
        conflicts: list[dict[str, Any]] = []
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
                conflicts.append(self._managed_drift_conflict(relpath, "2", "local drift detected"))

        for relpath in deleted_files:
            local_path = context.resolve_managed_path(relpath)
            manifest_entry = managed_files.get(relpath)
            if not manifest_entry or not local_path.exists():
                continue
            manifest_sha = str(manifest_entry.get("sha256") or "")
            local_sha = self.manifest_service.sha256_file(local_path)
            if local_sha != manifest_sha:
                conflicts.append(
                    self._managed_drift_conflict(
                        relpath,
                        "3",
                        "local drift on file scheduled for deletion",
                        scheduled_for_deletion=True,
                    )
                )

        return conflicts

    def _managed_drift_conflict(
        self,
        relpath: str,
        level: str,
        reason: str,
        *,
        scheduled_for_deletion: bool = False,
    ) -> dict[str, Any]:
        action = (
            "Inspect this file before syncing. If the local change matters, move it into .ail/source.ail or "
            "frontend/src/ail-overrides/, or rerun sync with --backup-and-overwrite to preserve a copy first."
        )
        summary = "Managed file differs from the recorded manifest."
        if scheduled_for_deletion:
            summary = "Managed file differs from the manifest and the incoming build wants to delete it."
        return {
            "path": relpath,
            "level": level,
            "reason": reason,
            "category": "managed_file_drift",
            "summary": summary,
            "user_message": (
                "AIL Builder will not silently overwrite this generated managed file. "
                "This is a sync safety guard, not proof that website generation failed."
            ),
            "recommended_action": action,
            "blocks_safe_sync": True,
            "blocks_existing_output_review": False,
        }

    @staticmethod
    def explain_conflicts(conflicts: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "message": (
                "Managed-file drift was detected. This is a sync safety guard, "
                "not necessarily a website generation failure."
            ),
            "explanation": (
                "One or more generated managed files differ from the manifest AIL Builder recorded earlier. "
                "The CLI stops before overwriting them so local edits are not lost."
            ),
            "blocks_safe_sync": True,
            "blocks_existing_output_review": False,
            "conflict_count": len(conflicts),
            "recommended_next_steps": [
                "Inspect the listed files or run `python3 -m cli conflicts --json`.",
                "If the current website output looks useful, preview it before changing sync state.",
                "Move durable source/content changes into `.ail/source.ail`.",
                "Move visual overrides into `frontend/src/ail-overrides/`.",
                "Use `python3 -m cli sync --backup-and-overwrite` only when you want backup copies before overwrite.",
            ],
        }

    def _backup_conflicts(
        self,
        context: ProjectContext,
        build_payload: dict[str, Any],
        conflicts: list[dict[str, Any]],
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
            "AIL Builder detected managed-file drift before sync and backed up the local versions.",
            "",
            "This is a sync safety guard. It does not necessarily mean website generation failed.",
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

    def _format_conflict_error(self, conflicts: list[dict[str, Any]]) -> str:
        details = "; ".join(
            f"{item['path']} (Level {item['level']}: {item['reason']})" for item in conflicts
        )
        return (
            "Managed-file drift detected. This is a sync safety guard, not necessarily a website generation "
            "failure. AIL Builder will not silently overwrite generated managed files that changed locally: "
            f"{details}. You can still inspect the existing output. Before syncing again, move durable changes "
            "into .ail/source.ail or frontend/src/ail-overrides/, or rerun with --backup-and-overwrite to save "
            "copies under .ail/conflicts/<build_id>/ before overwrite."
        )
