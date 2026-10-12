#!/usr/bin/env python3
"""Schema check for an EXP-ECDLP-903c48 stage-0 observation.

Exit 0 when the three artifacts exist and name this cell.
The scientific pass/fail is a field in the observation, not this exit code.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED = (
    "p",
    "a",
    "b",
    "point",
    "window_end",
    "on_curve",
    "group_law_order",
    "first_positive_zero",
    "zeros",
    "zeros_match_order_multiples",
    "w1",
    "w2",
    "w12",
)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: check.py RUN_DIR")
    run_dir = Path(sys.argv[1])
    for name in ("manifest.yaml", "raw-result.json", "RESULTS.md"):
        if not (run_dir / name).is_file():
            raise SystemExit(f"missing {name}")
    payload = json.loads((run_dir / "raw-result.json").read_text(encoding="utf-8"))
    if payload.get("schema") != "crypto.autoresearch.exp-ecdlp-903c48.stage0.v1":
        raise SystemExit("unexpected schema")
    if payload.get("experiment_id") != "EXP-ECDLP-903c48":
        raise SystemExit("unexpected experiment id")
    if payload.get("p") != 11 or payload.get("window_end") != 24:
        raise SystemExit("cell is not the preregistered (p, window) = (11, 24)")
    if payload.get("point") != [1, 5]:
        raise SystemExit("point does not match the freeze")
    missing = [key for key in REQUIRED if key not in payload]
    if missing:
        raise SystemExit(f"missing fields: {', '.join(missing)}")
    manifest = (run_dir / "manifest.yaml").read_text(encoding="utf-8")
    if "RUN-ECDLP-4616a2" not in manifest or "EXP-ECDLP-903c48" not in manifest:
        raise SystemExit("manifest does not name this run")
    text = (run_dir / "RESULTS.md").read_text(encoding="utf-8")
    if "mutual-information" not in text:
        raise SystemExit("RESULTS.md is missing the claim-boundary sentence")


if __name__ == "__main__":
    main()
