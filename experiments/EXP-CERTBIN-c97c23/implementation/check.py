#!/usr/bin/env python3
"""Post-trial checker for EXP-CERTBIN-c97c23 Stages 0-1."""
from __future__ import annotations

import json
import sys
from pathlib import Path


REQUIRED_COMMON = ("manifest.yaml", "raw-result.json", "command.txt")


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1:
        print("usage: check.py <run_dir>", file=sys.stderr)
        return 2
    run_dir = Path(args[0])
    if not run_dir.is_dir():
        print(f"missing run dir: {run_dir}", file=sys.stderr)
        return 2
    for name in REQUIRED_COMMON:
        if not (run_dir / name).is_file():
            print(f"missing artifact: {name}", file=sys.stderr)
            return 2
    raw = json.loads((run_dir / "raw-result.json").read_text(encoding="utf-8"))
    stage = raw.get("stage")
    if stage == 0:
        if not (run_dir / "union_freeze.json").is_file():
            print("missing union_freeze.json", file=sys.stderr)
            return 2
        if "archived_identity_ok" not in raw:
            print("raw-result missing archived_identity_ok", file=sys.stderr)
            return 2
        print("check ok stage0")
        return 0
    if stage == 1:
        outcome = raw.get("outcome")
        if outcome not in ("O-RARE", "O-BATCH", "O-ARTIFACT", "O-IMPEDIMENT"):
            print(f"bad outcome: {outcome!r}", file=sys.stderr)
            return 2
        print(f"check ok stage1 {outcome}")
        return 0
    print(f"unknown stage: {stage!r}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
