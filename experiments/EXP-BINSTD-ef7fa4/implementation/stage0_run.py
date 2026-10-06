#!/usr/bin/env python3
"""Stage 0 runner: record arithmetic artifacts already written; emit run package.

MUST complete before Stage 1. certificate.kind: none.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from runpack import EXP_ROOT, dump_yaml, peak_rss_bytes, utc_now, write_run_package

RUN_ID = "RUN-BINSTD-fd509d"


def main() -> None:
    started = utc_now()
    t0 = time.time()
    stage0 = EXP_ROOT / "stage0"
    required = [
        "dimension-table-n131.yaml",
        "dimension-table-rc1.yaml",
        "preregistered-predictions.yaml",
        "methodological-note.md",
        "subfield-proves-too-much.yaml",
    ]
    missing = [r for r in required if not (stage0 / r).exists()]
    if missing:
        raise SystemExit(f"Stage 0 artifacts missing: {missing}")

    # Verify n=131 arithmetic quickly
    def dim(l, k, n=131):
        return min(k * (l - 1) + 1, n)

    cells = [
        (5, 23, [23, 45, 67, 89, 111], 335, 115),
        (5, 28, [28, 55, 82, 109, 131], 405, 140),
    ]
    ok = True
    for m, l, pred, s, ml in cells:
        dims = [dim(l, k) for k in range(1, m + 1)]
        if dims != pred or sum(dims) != s or m * l != ml:
            ok = False

    metrics = {
        "stage0_artifacts_present": True,
        "n131_table_match": ok,
        "peak_rss_bytes": peak_rss_bytes(),
        "wall_clock_s": time.time() - t0,
        "termination_reason": "completed",
    }
    finished = utc_now()
    wall = time.time() - t0
    stdout = f"Stage 0 complete. artifacts={required} n131_match={ok}\n"
    write_run_package(
        RUN_ID,
        stage=0,
        arm="stage0-arithmetic",
        seed=None,
        command="python3 experiments/EXP-BINSTD-ef7fa4/implementation/stage0_run.py",
        parameters={"required_artifacts": required},
        metrics=metrics,
        valid=ok,
        invalid_reason=None if ok else "n131 arithmetic mismatch",
        termination_reason="completed",
        stdout_text=stdout,
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate={"kind": "none", "verified": None, "note": "Stage-0 dimension arithmetic"},
    )
    dump_yaml(
        EXP_ROOT / "stage0" / "stage0-run-receipt.yaml",
        {"run_id": RUN_ID, "metrics": metrics, "artifacts": required},
    )
    print(stdout)


if __name__ == "__main__":
    main()
