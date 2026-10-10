#!/usr/bin/env python3
"""Independent checker for EXP-ECDLP-daee4d Stage 0-1 artifacts."""
from __future__ import annotations

import json
import sys
from pathlib import Path

EXPERIMENT_ID = "EXP-ECDLP-daee4d"
STAGE0_OK = {"S0-FREEZE-OK"}
STAGE1_OK = {"O-FLOOR", "O-EXCESS", "O-MIXED", "O-CONTROL-FAIL", "O-IMPEDIMENT"}


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check.py RUN_DIR", file=sys.stderr)
        return 2
    run_dir = Path(sys.argv[1])
    raw = json.loads((run_dir / "raw-result.json").read_text(encoding="utf-8"))
    stage = raw.get("stage")
    outcome = raw.get("outcome")
    if stage == 0:
        if outcome not in STAGE0_OK:
            print(f"bad stage0 outcome {outcome}", file=sys.stderr)
            return 1
        freeze = Path("experiments/EXP-ECDLP-daee4d/stage0/protocol-freeze.json")
        if not freeze.exists():
            print("missing stage0 freeze", file=sys.stderr)
            return 1
        print("CHECK_OK stage0")
        return 0
    if stage == 1:
        if outcome not in STAGE1_OK:
            print(f"bad stage1 outcome {outcome}", file=sys.stderr)
            return 1
        if outcome != "O-IMPEDIMENT":
            for name in ("census.json", "control-table.json"):
                if not (Path("experiments/EXP-ECDLP-daee4d/stage1") / name).exists():
                    print(f"missing stage1/{name}", file=sys.stderr)
                    return 1
        print(f"CHECK_OK stage1 {outcome}")
        return 0
    print(f"unknown stage {stage}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
