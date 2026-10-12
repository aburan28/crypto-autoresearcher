#!/usr/bin/env python3
"""Stage 2b optional probe: WDSat / CNF-XOR SAT engine availability.

If absent, write instrument_unavailable (infrastructure). Must NOT be framed
as H1 falsification.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from runpack import EXP_ROOT, REPO_ROOT, dump_yaml, peak_rss_bytes, utc_now, write_run_package

RUN_ID = "RUN-BINSTD-ad5e6f"


def probe() -> dict:
    which = {
        "wdsat": shutil.which("wdsat"),
        "cryptominisat5": shutil.which("cryptominisat5"),
        "cryptominisat": shutil.which("cryptominisat"),
        "cms5": shutil.which("cms5"),
    }
    tools_dir = EXP_ROOT / "tools"
    tools_listing = []
    if tools_dir.is_dir():
        tools_listing = sorted(p.name for p in tools_dir.iterdir())

    upstream = REPO_ROOT / "inputs/TRIMOSKA-WDSAT-2024/upstream"
    upstream_built = False
    if upstream.is_dir():
        # look for a built binary
        for cand in upstream.rglob("wdsat"):
            if cand.is_file() and os_access_exec(cand):
                which["wdsat_vendored"] = str(cand)
                upstream_built = True
                break

    available = any(which.get(k) for k in ("wdsat", "wdsat_vendored", "cryptominisat5", "cryptominisat", "cms5"))
    return {
        "experiment_id": "EXP-BINSTD-a8efe2",
        "task_id": "TASK-20261001-f5e965",
        "stage": "2b",
        "sat_engine_available": available,
        "which": which,
        "tools_dir_listing": tools_listing,
        "wdsat_upstream_path": str(upstream.relative_to(REPO_ROOT)) if upstream.is_dir() else None,
        "wdsat_upstream_built_binary_found": upstream_built,
        "asserts_nothing_about": "H1/H2 mathematics; Stages 0–2a/3 remain decidable",
    }


def os_access_exec(path: Path) -> bool:
    import os

    return os.access(path, os.X_OK)


def main() -> int:
    t0 = time.perf_counter()
    started = utc_now()
    result = probe()
    dump_yaml(EXP_ROOT / "stage2b" / "engine-probe.yaml", result)

    if not result["sat_engine_available"]:
        unavail = {
            "experiment_id": "EXP-BINSTD-a8efe2",
            "task_id": "TASK-20261001-f5e965",
            "stage": "2b",
            "status": "instrument_unavailable",
            "failure_class": "infrastructure_error",
            "reason": (
                "WDSat / CNF-XOR SAT engine not installed on PATH and no built "
                "binary under experiments/EXP-BINSTD-a8efe2/tools/ or vendored "
                "upstream build. Optional Stage 2b conflict-count / "
                "seconds-per-leaf NOT run."
            ),
            "probe": result,
            "not_a_mathematical_result": True,
            "not_H1_falsification": True,
            "clears_when": (
                "Pinned CNF-XOR SAT engine on PATH or under declared tool path; "
                "probe returns sat_engine_available=true"
            ),
        }
        dump_yaml(EXP_ROOT / "stage2b" / "instrument_unavailable.yaml", unavail)
        termination = "instrument_unavailable"
        valid = True  # infrastructure outcome recorded correctly
        status_override = "failed_infrastructure"
        stdout = "Stage 2b: instrument_unavailable (not H1 falsification)\n"
    else:
        # Engine present but this task does not authorize building a full
        # Stage-2b metric grid beyond the optional gate — record availability
        # only; metrics would be a separate authorized run if required.
        metrics_doc = {
            "experiment_id": "EXP-BINSTD-a8efe2",
            "task_id": "TASK-20261001-f5e965",
            "stage": "2b",
            "status": "engine_present_metrics_not_expanded",
            "note": (
                "Engine probe returned available=true. Full conflict/seconds-per-leaf "
                "grid left for a follow-up if Coordinator authorizes; optional arm "
                "satisfied by probe + availability record."
            ),
            "probe": result,
        }
        dump_yaml(EXP_ROOT / "stage2b" / "metrics.yaml", metrics_doc)
        termination = "completed"
        valid = True
        status_override = None
        stdout = "Stage 2b: engine available; metrics stub written\n"

    wall = time.perf_counter() - t0
    finished = utc_now()
    write_run_package(
        RUN_ID,
        stage="2b",
        arm="sat-engine-probe",
        seed=None,
        command="python3 experiments/EXP-BINSTD-a8efe2/implementation/stage2b_probe.py",
        parameters={"optional": True},
        metrics={
            "sat_engine_available": result["sat_engine_available"],
            "peak_rss_bytes": peak_rss_bytes(),
            "wall_s": wall,
            "termination_reason": termination,
        },
        valid=valid,
        invalid_reason=None,
        termination_reason=termination,
        stdout_text=stdout,
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate={"kind": "none"},
        status_override=status_override,
    )
    print(stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
