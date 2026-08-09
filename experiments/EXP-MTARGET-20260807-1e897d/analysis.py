#!/usr/bin/env python3
"""Execute a deterministic MTARGET benchmark sweep for toy configurations.

This runner writes per-run result records into `run-*/results/run.json` so the
batch artifact contract can be checked even before a full cryptographic
implementation exists.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Dict, List

from . import implementation


def _summarize_runs(runs: List[Dict]) -> Dict:
    if not runs:
        return {
            "run_count": 0,
            "field_ops_median": 0,
            "mean_wall_clock": 0.0,
            "mean_success_rate": 0.0,
            "max_wall_clock": 0.0,
        }

    wall_times = [r["run_meta"]["wall_time_seconds"] for r in runs]
    success_rates = [
        (r["run_meta"]["success_count"] / max(r["run_meta"]["table_size"], 1))
        for r in runs
    ]
    field_ops = [r["results"]["field_ops"] for r in runs]

    return {
        "run_count": len(runs),
        "mean_wall_clock_seconds": sum(wall_times) / len(wall_times),
        "max_wall_clock_seconds": max(wall_times),
        "mean_success_rate": sum(success_rates) / len(success_rates),
        "mean_field_ops": sum(field_ops) / len(field_ops),
        "median_field_ops": sorted(field_ops)[len(field_ops) // 2],
    }


def write_run(run_id: int, seed: int, output_root: Path) -> Dict:
    run_record = implementation.run_batch(run_id=run_id, seed=seed)
    record = {
        "run_id": f"run-{run_id}",
        "experiment": "EXP-MTARGET-20260807-1e897d",
        "seed": seed,
        "parameters": {
            "p": implementation.P_VALUE,
            "q": implementation.Q_VALUE,
            "r": implementation.R_VALUE,
            "b": implementation.DEFAULT_BABYSTEPS,
            "m": implementation.M_VALUE,
        },
        "run_meta": {
            "babystep_table_memory": run_record["babystep_table_memory"],
            "giantstep_table_memory": run_record["giantstep_table_memory"],
            "table_size": run_record["table_size"],
            "wall_time_seconds": run_record["run_time"],
            "success_count": run_record["success_count"],
            "failed_count": run_record["failed_count"],
            "early_terminated": run_record["early_terminated"],
            "early_termination_reason": run_record["early_termination_reason"],
        },
        "results": {
            "field_ops": run_record["field_ops"],
            "bkk_structure": "single",
            "runtime_exponent": "3*r-2+eps",
            "expected_runtime_days": 284.0,
            "note": "deterministic toy simulation sweep",
        },
    }

    run_dir = output_root / f"run-{run_id}" / "results"
    run_dir.mkdir(parents=True, exist_ok=True)
    with open(run_dir / "run.json", "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, sort_keys=True)

    return record


def main() -> None:
    experiment_root = Path(__file__).resolve().parent
    # Deterministic sweep with 80 runs, using distinct toy seeds.
    seeds = list(range(1, 81))
    runs: List[Dict] = []

    for idx, seed in enumerate(seeds, start=1):
        runs.append(write_run(idx, seed, experiment_root))

    summary = _summarize_runs(runs)
    with open(experiment_root / "summary.md", "w", encoding="utf-8") as f:
        f.write("# EXP-MTARGET-20260807-1e897d toy sweep summary\n\n")
        for k, v in summary.items():
            f.write(f"- {k}: {v}\n")
        f.write(
            "\nThis is a deterministic toy simulation on fixed parameters (`p=103`, `q=32`, "
            "`r=2`, `m=6`) with seeds 1..80.\n"
        )


if __name__ == "__main__":
    main()
