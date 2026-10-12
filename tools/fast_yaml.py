"""`orchestration.fast_yaml` for scripts run as `python3 tools/<name>.py`.

Such a script has tools/ on sys.path, not the repository root. Put this
checkout first so an installed package from another checkout cannot shadow
the source and prevent experiment entry points from starting. The
implementation is in orchestration/fast_yaml.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

repo_root = str(Path(__file__).resolve().parents[1])
if repo_root in sys.path:
    sys.path.remove(repo_root)
sys.path.insert(0, repo_root)

from orchestration.fast_yaml import CSafeLoader, safe_load

__all__ = ["CSafeLoader", "safe_load"]
