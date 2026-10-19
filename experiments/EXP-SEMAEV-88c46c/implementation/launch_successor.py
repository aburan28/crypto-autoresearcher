"""EXP-SEMAEV-88c46c trial driver: the parent's launch.py, unmodified, with
the manifest's experiment id set to this successor.

    python3 launch_successor.py <launch.py arguments>

Dependencies are named relative to this experiment's runs/ directory, so the
parent's output-validated mtic-007/008 runs are passed as
``--dep mtic-007=../../EXP-SEMAEV-93d5cc/runs/RUN-SEMAEV-2a8498`` (resolved and
hash-checked by launch.unpack_dependency against their arms-manifest.json).
"""
from __future__ import annotations

import sys
from pathlib import Path

PARENT_IMPL = Path(__file__).resolve().parents[2] / "EXP-SEMAEV-93d5cc" / "implementation"
sys.path.insert(0, str(PARENT_IMPL))

import launch  # noqa: E402  -- the parent's hash-bound launcher

launch.EXP_ID = "EXP-SEMAEV-88c46c"

if __name__ == "__main__":
    raise SystemExit(launch.main())
