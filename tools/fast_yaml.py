"""`orchestration.fast_yaml` for scripts run as `python3 tools/<name>.py`.

Such a script has tools/ on sys.path, not the repository root, and the
package is not installed in every workflow (pages, sync-main), so the root is
appended when `orchestration` is not importable. The implementation and its
rationale are in orchestration/fast_yaml.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    from orchestration.fast_yaml import CSafeLoader, safe_load
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from orchestration.fast_yaml import CSafeLoader, safe_load

__all__ = ["CSafeLoader", "safe_load"]
