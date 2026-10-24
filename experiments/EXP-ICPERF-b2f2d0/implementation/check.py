#!/usr/bin/env python3
"""Schema check for an EXP-ICPERF-b2f2d0 stage-0 observation.

Exit 0 when the artifacts exist and name this cell.
The scientific pass or fail is a field in the observation, not this exit code.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED = (
    "seed",
    "p_den",
    "n_targets",
    "sample_sum",
    "sum_squares",
    "median",
    "cv_in_band",
    "median_ratio_in_band",
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
    if payload.get("schema") != "crypto.autoresearch.exp-icperf-b2f2d0.stage0.v1":
        raise SystemExit("unexpected schema")
    if payload.get("experiment_id") != "EXP-ICPERF-b2f2d0":
        raise SystemExit("unexpected experiment id")
    if payload.get("trial_id") != "geometric-probe-sample":
        raise SystemExit("trial id does not match the freeze")
    if payload.get("seed") != 20261017 or payload.get("p_den") != 50:
        raise SystemExit("seed or success denominator is not the freeze")
    if payload.get("n_targets") != 64:
        raise SystemExit("sample size is not 64")
    missing = [key for key in REQUIRED if key not in payload]
    if missing:
        raise SystemExit(f"missing fields: {', '.join(missing)}")
    manifest = (run_dir / "manifest.yaml").read_text(encoding="utf-8")
    if "RUN-ICPERF-b09be8" not in manifest or "EXP-ICPERF-b2f2d0" not in manifest:
        raise SystemExit("manifest does not name this run")
    text = (run_dir / "RESULTS.md").read_text(encoding="utf-8")
    if "host latency" not in text:
        raise SystemExit("RESULTS.md is missing the claim-boundary sentence")


if __name__ == "__main__":
    main()
