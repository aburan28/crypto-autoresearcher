#!/usr/bin/env python3
"""Batch driver for EXP-BINSTD-5d3ec0 Stages 1-2 (Stage 0 already committed)."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMPL = Path(__file__).resolve().parent

# Pre-minted RUN ids (allocate_id --check OK). Stage0 used 6a2c31.
STAGE1_RUNS = [
    # (arm, w, l_prime, run_id)
    ("koblitz", 1, 8, "RUN-BINSTD-0dea37"),
    ("koblitz", 1, 10, "RUN-BINSTD-40ce4d"),
    ("koblitz", 1, 12, "RUN-BINSTD-338f54"),
    ("koblitz", 2, 8, "RUN-BINSTD-c23c45"),
    ("koblitz", 2, 10, "RUN-BINSTD-7f876b"),
    ("koblitz", 2, 12, "RUN-BINSTD-332c2d"),
    ("ordinary", 1, 8, "RUN-BINSTD-06d553"),
    ("ordinary", 1, 10, "RUN-BINSTD-0649c6"),
    ("ordinary", 1, 12, "RUN-BINSTD-2ef3d5"),
    ("ordinary", 2, 8, "RUN-BINSTD-15607c"),
    ("ordinary", 2, 10, "RUN-BINSTD-c47958"),
    ("ordinary", 2, 12, "RUN-BINSTD-0a24dd"),
    ("relabelled", 1, 8, "RUN-BINSTD-3acf74"),
    ("relabelled", 1, 10, "RUN-BINSTD-0fddb6"),
    ("relabelled", 1, 12, "RUN-BINSTD-d3fe10"),
    ("relabelled", 2, 8, "RUN-BINSTD-9a580a"),
    ("relabelled", 2, 10, "RUN-BINSTD-cf1370"),
    ("relabelled", 2, 12, "RUN-BINSTD-ca1217"),
]

STAGE2_RUNS = [
    (8, "RUN-BINSTD-f0e531"),
    (10, "RUN-BINSTD-83687b"),
    (12, "RUN-BINSTD-e024b1"),
]


def run_cmd(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    r = subprocess.run(cmd, cwd="/workspace")
    if r.returncode != 0:
        raise SystemExit(f"command failed ({r.returncode}): {cmd}")


def main():
    t0 = time.time()
    # Ensure Stage 0 artifacts exist
    for p in (
        "stage0/product-law-n131.yaml",
        "stage0/n19-order-check.yaml",
        "stage0/preregistered-predictions.yaml",
        "stage0/methodological-note.md",
        "stage0/w1-baseline-row.yaml",
    ):
        if not (ROOT / p).exists():
            raise SystemExit(f"Stage 0 missing {p}; refuse Stage 1")

    for arm, w, lp, rid in STAGE1_RUNS:
        run_dir = ROOT / "runs" / rid
        if run_dir.exists():
            print(f"skip existing {rid}", flush=True)
            continue
        run_cmd(
            [
                sys.executable,
                str(IMPL / "stage1_collision.py"),
                "--arm",
                arm,
                "--w",
                str(w),
                "--l-prime",
                str(lp),
                "--run-id",
                rid,
            ]
        )

    for lp, rid in STAGE2_RUNS:
        run_dir = ROOT / "runs" / rid
        if run_dir.exists():
            print(f"skip existing {rid}", flush=True)
            continue
        run_cmd(
            [
                sys.executable,
                str(IMPL / "stage2_coupled.py"),
                "--l-prime",
                str(lp),
                "--run-id",
                rid,
            ]
        )

    print(json.dumps({"driver_wall_s": time.time() - t0, "stage1_cells": len(STAGE1_RUNS),
                      "stage2_cells": len(STAGE2_RUNS)}))


if __name__ == "__main__":
    main()
