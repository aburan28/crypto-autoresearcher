#!/usr/bin/env python3
"""Schema check for an EXP-ICPERF-e467a5 stage-0 observation.

Exit 0 when the artifacts exist and name this cell.
The scientific pass or fail is a field in the observation, not this exit code.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED = (
    "c_probe_ns",
    "c_state_ns",
    "c_step_ns",
    "bl_num",
    "bl_den",
    "states",
    "price_ratio_num",
    "price_ratio_den",
    "cells",
    "ratios_agree",
    "all_match_bsgs",
    "trial_id",
)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: check.py RUN_DIR")
    run_dir = Path(sys.argv[1])
    for name in ("manifest.yaml", "raw-result.json", "RESULTS.md"):
        if not (run_dir / name).is_file():
            raise SystemExit(f"missing {name}")
    payload = json.loads((run_dir / "raw-result.json").read_text(encoding="utf-8"))
    if payload.get("schema") != "crypto.autoresearch.exp-icperf-e467a5.stage0.v1":
        raise SystemExit("unexpected schema")
    if payload.get("experiment_id") != "EXP-ICPERF-e467a5":
        raise SystemExit("unexpected experiment id")
    if payload.get("trial_id") != "price-ratio-identity":
        raise SystemExit("trial id does not match the freeze")
    if payload.get("c_probe_ns") != 370 or payload.get("c_step_ns") != 40:
        raise SystemExit("prices are not the preregistered pair")
    if payload.get("states") != 10 or payload.get("bl_num") != 21:
        raise SystemExit("table size or BL constant is not the freeze")
    cells = payload.get("cells")
    if not isinstance(cells, list) or [row.get("name") for row in cells] != [
        "r1000_a2",
        "r4000_a2",
        "r1000_a4",
    ]:
        raise SystemExit("cells are not the three preregistered names")
    missing = [key for key in REQUIRED if key not in payload]
    if missing:
        raise SystemExit(f"missing fields: {', '.join(missing)}")
    manifest = (run_dir / "manifest.yaml").read_text(encoding="utf-8")
    if "RUN-ICPERF-943efa" not in manifest or "EXP-ICPERF-e467a5" not in manifest:
        raise SystemExit("manifest does not name this run")
    text = (run_dir / "RESULTS.md").read_text(encoding="utf-8")
    if "n=83" not in text:
        raise SystemExit("RESULTS.md is missing the claim-boundary sentence")


if __name__ == "__main__":
    main()
