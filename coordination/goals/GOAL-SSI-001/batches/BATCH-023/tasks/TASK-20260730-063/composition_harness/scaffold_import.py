"""Resolve BATCH-022 scaffold for read-only import (do not modify that tree)."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

# composition_harness/ -> TASK -> tasks -> BATCH -> batches -> GOAL -> goals -> coordination -> repo
_REPO_ROOT = Path(__file__).resolve().parents[8]
_BATCH022_TASK = (
    _REPO_ROOT
    / "coordination"
    / "goals"
    / "GOAL-SSI-001"
    / "batches"
    / "BATCH-022"
    / "tasks"
    / "TASK-20260730-059"
)


def ensure_batch022_scaffold_on_path() -> Path:
    """Insert BATCH-022 task dir so `import scaffold` resolves read-only."""
    path = str(_BATCH022_TASK)
    if path not in sys.path:
        sys.path.insert(0, path)
    return _BATCH022_TASK


def import_scaffold_modules():
    """Import BATCH-022 scaffold modules after path setup."""
    ensure_batch022_scaffold_on_path()
    types_mod = importlib.import_module("scaffold.types")
    verify_mod = importlib.import_module("scaffold.verify")
    lifetime_mod = importlib.import_module("scaffold.lifetime_hooks")
    state_mod = importlib.import_module("scaffold.state_machine")
    return {
        "types": types_mod,
        "verify": verify_mod,
        "lifetime_hooks": lifetime_mod,
        "state_machine": state_mod,
        "batch022_task_dir": str(_BATCH022_TASK.relative_to(_REPO_ROOT)),
    }
