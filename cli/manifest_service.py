from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

from .context import MANAGED_ROOTS


class ManifestService:
    def load_manifest(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        return self._read_json(path)

    def save_manifest(self, path: Path, manifest: dict[str, Any]) -> None:
        self._write_json(path, manifest)

    def load_last_build(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        return self._read_json(path)

    def save_last_build(self, path: Path, payload: dict[str, Any]) -> None:
        self._write_json(path, payload)

    def make_initial_manifest(self, project_id: str) -> dict[str, Any]:
        return {
            "project_id": project_id,
            "manifest_version": 0,
            "current_build_id": "",
            "managed_roots": list(MANAGED_ROOTS),
            "managed_files": {},
            "updated_at": _utc_now(),
        }

    def make_initial_last_build(self, project_id: str) -> dict[str, Any]:
        return {
            "project_id": project_id,
            "build_id": "",
            "status": "not_built",
            "created_at": None,
            "files": [],
            "deleted_files": [],
            "manifest": self.make_initial_manifest(project_id),
            "diff_summary": {"added": 0, "updated": 0, "deleted": 0},
        }

    def sha256_text(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def sha256_file(self, path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def build_manifest(
        self,
        project_id: str,
        build_id: str,
        files: list[dict[str, Any]],
        previous_version: int,
    ) -> dict[str, Any]:
        managed_files: dict[str, Any] = {}
        timestamp = _utc_now()
        for item in files:
            managed_files[item["path"]] = {
                "sha256": item["sha256"],
                "build_id": build_id,
                "generated_at": timestamp,
            }
        return {
            "project_id": project_id,
            "manifest_version": max(previous_version, 0) + 1,
            "current_build_id": build_id,
            "managed_roots": list(MANAGED_ROOTS),
            "managed_files": managed_files,
            "updated_at": timestamp,
        }

    def _read_json(self, path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    def _write_json(self, path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_suffix(path.suffix + ".tmp")
        temp_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        temp_path.replace(path)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
