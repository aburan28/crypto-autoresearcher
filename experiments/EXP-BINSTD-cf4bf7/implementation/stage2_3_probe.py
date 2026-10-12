#!/usr/bin/env python3
"""Optional Stages 2–3: probe WDSat/CNF-XOR; write instrument_unavailable if absent."""
from __future__ import annotations

import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from runpack import EXP_ROOT, dump_text, dump_yaml, peak_rss_bytes, utc_now, write_run_package

RUN_STAGE2 = "RUN-BINSTD-068959"
RUN_STAGE3 = "RUN-BINSTD-c302de"


def probe_engine() -> dict:
    names = ["wdsat", "cadical", "cryptominisat5", "cryptominisat", "kissat", "glucose"]
    found = {}
    for name in names:
        path = shutil.which(name)
        found[name] = path
    # Also check experiment-local tools/
    tools = EXP_ROOT / "tools"
    local = []
    if tools.is_dir():
        local = sorted(p.name for p in tools.iterdir())
    available = any(v for v in found.values()) or bool(local)
    # Spec requires CNF-XOR / WDSat specifically for conflict-ratio instrument.
    wdsat_available = bool(found.get("wdsat"))
    return {
        "probed_names": found,
        "local_tools_dir": str(tools) if tools.is_dir() else None,
        "local_tools": local,
        "any_sat_binary_on_path": any(v for v in found.values()),
        "wdsat_available": wdsat_available,
        "cnf_xor_wdsat_instrument_available": wdsat_available,
        "available": wdsat_available,
    }


def main() -> None:
    started = utc_now()
    t0 = time.time()
    stage2 = EXP_ROOT / "stage2"
    stage3 = EXP_ROOT / "stage3"
    stage2.mkdir(parents=True, exist_ok=True)
    stage3.mkdir(parents=True, exist_ok=True)

    probe = probe_engine()
    dump_yaml(
        stage2 / "engine-probe.yaml",
        {
            "experiment_id": "EXP-BINSTD-cf4bf7",
            "task_id": "TASK-20261001-18804b",
            "stage": 2,
            "probe": probe,
            "impediment_ref": "IMP-WDSat-9e5383",
        },
    )

    if not probe["available"]:
        dump_yaml(
            stage2 / "instrument_unavailable.yaml",
            {
                "experiment_id": "EXP-BINSTD-cf4bf7",
                "task_id": "TASK-20261001-18804b",
                "stage": 2,
                "status": "instrument_unavailable",
                "classification": "infrastructure",
                "asserts_nothing_about": (
                    "Stage 0/1/4 arithmetic, ord/f census, corrected ladder, "
                    "or H1 mathematical content"
                ),
                "probe": probe,
                "modeled_prior_not_recorded_as_measured": True,
                "no_break_claim": True,
            },
        )
        dump_text(
            stage3 / "skip-with-stage2.md",
            """# Stage 3 skipped with Stage 2

Stage 2 WDSat/CNF-XOR instrument is unavailable (`instrument_unavailable`).
Stage 3 within-curve non-stable control requires the same instrument and is
therefore skipped.

This is infrastructure (IMP-WDSat-9e5383), not negative mathematical evidence
and not falsification of H1.
""",
        )
        dump_yaml(
            stage3 / "skip-note.yaml",
            {
                "experiment_id": "EXP-BINSTD-cf4bf7",
                "task_id": "TASK-20261001-18804b",
                "stage": 3,
                "status": "skipped_with_stage2",
                "reason": "Stage 2 instrument_unavailable",
                "classification": "infrastructure",
            },
        )
        termination = "instrument_unavailable"
        status_override = "failed_infrastructure"
        valid = True  # protocol-satisfying optional-arm outcome
        # Spec: instrument_unavailable satisfies optional arm; not invalid_measurement.
        # Use status failed_infrastructure for the probe run, with valid metrics noting unavailability.
    else:
        # Engine present — still out of scope for this executor pass to run full PDP
        # unless explicitly required; record availability for Coordinator.
        dump_yaml(
            stage2 / "engine-available-not-executed.yaml",
            {
                "experiment_id": "EXP-BINSTD-cf4bf7",
                "task_id": "TASK-20261001-18804b",
                "stage": 2,
                "status": "engine_available",
                "note": (
                    "WDSat binary found; full conflict-ratio measurement not executed "
                    "in this required Stages 0/1/4 pass. Optional arm may be resumed."
                ),
                "probe": probe,
            },
        )
        termination = "completed"
        status_override = None
        valid = True

    finished = utc_now()
    wall = time.time() - t0
    stdout = f"wdsat_available={probe['available']}\nprobe={probe}\n"

    write_run_package(
        RUN_STAGE2,
        stage=2,
        arm="wdsat_probe",
        seed=None,
        command="python3 experiments/EXP-BINSTD-cf4bf7/implementation/stage2_3_probe.py",
        parameters={"optional": True},
        metrics={
            "sat_engine_available": probe["available"],
            "wdsat_available": probe["wdsat_available"],
            "peak_rss_bytes": peak_rss_bytes(),
            "wall_s": wall,
        },
        valid=valid,
        invalid_reason=None,
        termination_reason=termination,
        stdout_text=stdout,
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate={"kind": "none", "verified": None, "verifier": None, "artifact": None},
        status_override=status_override if not probe["available"] else status_override,
    )
    write_run_package(
        RUN_STAGE3,
        stage=3,
        arm="within_curve_nonstable_skip",
        seed=None,
        command="python3 experiments/EXP-BINSTD-cf4bf7/implementation/stage2_3_probe.py",
        parameters={"optional": True, "depends_on_stage2": True},
        metrics={
            "skipped_with_stage2": not probe["available"],
            "peak_rss_bytes": peak_rss_bytes(),
            "wall_s": wall,
        },
        valid=True,
        invalid_reason=None,
        termination_reason="instrument_unavailable" if not probe["available"] else "completed",
        stdout_text=stdout,
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate={"kind": "none", "verified": None, "verifier": None, "artifact": None},
        status_override="failed_infrastructure" if not probe["available"] else None,
    )
    print(stdout)


if __name__ == "__main__":
    main()
