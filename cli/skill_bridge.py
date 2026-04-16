from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
REPAIR_MODULE_PATH = ROOT / "testing" / "repair_smoke_runner.py"


def load_repair_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("repair_smoke_runner", REPAIR_MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load repair module from {REPAIR_MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
