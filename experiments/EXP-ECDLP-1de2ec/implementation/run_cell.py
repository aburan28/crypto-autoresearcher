#!/usr/bin/env python3
"""Execute one Stage-1 (seed, arm) cell of EXP-ECDLP-1de2ec."""

from __future__ import annotations

import argparse
import gzip
import json
import os
import platform
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[3]
_EXP = Path(__file__).resolve().parents[1]
if str(_EXP) not in sys.path:
    sys.path.insert(0, str(_EXP))

from implementation.instrument import (  # type: ignore
    A_PILOT,
    CAP,
    EPSILON,
    K_PILOT,
    N_PILOT,
    R_PILOT,
    T0_GRID,
    T_BL,
    U_LADDER,
    W,
    exact_basins,
    generate_pool,
    run_arm,
)


def git_state() -> tuple[str, bool, list[str], str]:
    sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    dirty = subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    )
    branch = subprocess.check_output(
        ["git", "branch", "--show-current"], cwd=ROOT, text=True
    ).strip()
    lines = [ln for ln in dirty.splitlines() if ln.strip()]
    return sha, bool(lines), lines, branch


def rss_bytes() -> int:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024


def write_json(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, default=str) + "\n")


def cells_for_arm(arm: str) -> list[tuple[int, int, float]]:
    arm = arm.upper()
    out: list[tuple[int, int, float]] = []
    if arm == "KS":
        for u in U_LADDER:
            out.append((0, u, 1.0))
        return out
    if arm == "PHI":
        for phi in (0.0, 0.25, 0.5, 0.75, 1.0):
            for u in U_LADDER:
                out.append((T_BL // 2, u, phi))
        return out
    if arm == "BASELINE":
        t0s = (T_BL, T_BL // 2)
    elif arm == "GROW-UNCAP":
        t0s = T0_GRID
    elif arm in {"GROW-CAP", "NULL1"}:
        t0s = (T_BL, T_BL // 2)
    else:
        raise SystemExit(f"unknown arm {arm}")
    for t0 in t0s:
        for u in U_LADDER:
            out.append((t0, u, 1.0))
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", required=True)
    parser.add_argument("--seed", type=int, required=True, choices=(1, 2, 3))
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--basins", action="store_true")
    args = parser.parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    started = datetime.now(timezone.utc)
    t0 = time.perf_counter()
    cpu0 = time.process_time()
    sha, dirty, dirty_lines, branch = git_state()

    pool = generate_pool(args.seed)
    basin_info = None
    if args.basins:
        basin_info = exact_basins(pool)
        hist_path = outdir / "basin_histogram.json.gz"
        with gzip.open(hist_path, "wt", encoding="utf-8") as handle:
            json.dump(basin_info, handle)

    cells = []
    raw_records = []
    invalid = False
    invalid_reason = None
    for t0_val, u, phi in cells_for_arm(args.arm):
        cell = run_arm(
            seed=args.seed,
            arm=args.arm,
            t0=t0_val,
            u=u,
            phi=phi,
            pool=pool,
        )
        if cell["exceeds_upper"]:
            invalid = True
            invalid_reason = (
                f"measured solved fraction {cell['solved_fraction']} "
                f"exceeds UPPER {cell['UPPER']} at T_0={t0_val} U={u}"
            )
        slim = dict(cell)
        records = slim.pop("records")
        cells.append(slim)
        raw_records.append({
            "T_0": t0_val,
            "U": u,
            "phi": phi,
            "records": records,
        })

    finished = datetime.now(timezone.utc)
    wall = time.perf_counter() - t0
    cpu = time.process_time() - cpu0

    run_id = outdir.name
    command = (
        f"python3 experiments/EXP-ECDLP-1de2ec/implementation/run_cell.py "
        f"--arm {args.arm} --seed {args.seed} --outdir {outdir}"
        + (" --basins" if args.basins else "")
    )
    (outdir / "command.txt").write_text(command + "\n")

    summary = {
        "status": "completed_invalid" if invalid else "completed_valid",
        "run_id": run_id,
        "experiment_id": "EXP-ECDLP-1de2ec",
        "task_id": "TASK-20260908-470642",
        "arm": args.arm.upper(),
        "seed": args.seed,
        "parameters": {
            "N": N_PILOT,
            "T_BL": T_BL,
            "W_definition": W,
            "W_source": "sqrt(a*N/T_BL) from specification.definitions",
            "cost_model_listed_W": 362,
            "cap": CAP,
            "a": A_PILOT,
            "r": R_PILOT,
            "k": K_PILOT,
            "epsilon": EPSILON,
            "U_ladder": list(U_LADDER),
        },
        "pool": {
            "P": pool["P"],
            "generation_walks": pool["generation_walks"],
            "n_distinct": pool["n_distinct"],
        },
        "cells": cells,
        "certificate": {"kind": "none", "verified": None, "verifier": None},
        "claim_tier": "toy",
    }
    write_json(outdir / "summary.json", summary)

    raw = {
        "run_id": run_id,
        "arm": args.arm.upper(),
        "seed": args.seed,
        "pool_keys": {"walk_key": pool["walk_key"], "dp_key": pool["dp_key"]},
        "cells": raw_records,
        "certificate": {"kind": "none"},
    }
    write_json(outdir / "raw-result.json", raw)

    cost = {
        "measured": {
            "P_generation_walk_steps": pool["P"],
            "online_steps_by_cell": [
                {"T_0": c["T_0"], "U": c["U"], "phi": c["phi"], "online_steps": c["online_steps"]}
                for c in cells
            ],
            "union_find_ops_by_cell": [
                {"T_0": c["T_0"], "U": c["U"], "ops": c["union_find_ops"]}
                for c in cells
            ],
        },
        "modeled": {
            "W_definition": W,
            "theta": 1.0 / W,
            "KS_order_sqrt_2N_over_U": {
                str(u): (2 * N_PILOT / u) ** 0.5 for u in U_LADDER
            },
            "note": "Modeled columns are formulas; not mixed with measured counts.",
        },
    }
    write_json(outdir / "cost_table.json", cost)

    env = {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "hostname": platform.node(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "numpy_version": np.__version__,
        "cpu_count": os.cpu_count(),
        "pid": os.getpid(),
        "dependencies": {
            "python": sys.version,
            "numpy": np.__version__,
            "pyyaml": yaml.__version__,
        },
    }
    write_json(outdir / "environment.json", env)

    manifest = {
        "run": {
            "id": run_id,
            "experiment_id": "EXP-ECDLP-1de2ec",
            "task_id": "TASK-20260908-470642",
            "arm": args.arm.upper(),
            "status": "completed_invalid" if invalid else "completed_valid",
            "code": {
                "commit": sha,
                "dirty": dirty,
                "dirty_tree": dirty_lines,
                "branch": branch,
                "command": command,
            },
            "inference": {
                "requested_policy": "executor-implementation",
                "canonical_policy": "executor-implementation",
                "backend": "cursor",
                "provider": "cursor",
                "resolved_model_id": "grok-4.6",
                "model_provenance": "operator-supplied",
                "model_verified": False,
                "requested_reasoning_effort": "medium",
                "reasoning_effort": "medium",
                "fallback_used": True,
                "fallback_reason": (
                    "Handoff requested executor-implementation "
                    "(orchestration.adapter resolve: anthropic:claude-sonnet-5). "
                    "This executor session is served by Cursor Grok 4.6. "
                    "Handoff fallback_allowed is false; recorded as a "
                    "protocol_deviation. Numeric results are deterministic Python."
                ),
                "degraded_requirements": [],
                "independent_session": False,
                "adapter_version": "1.1.0",
                "config_digest": None,
                "session_model_self_report": "Cursor Grok 4.6",
                "numeric_results": "deterministic_code",
            },
            "environment": env,
            "inputs": {
                "curve_id": None,
                "instrument_class": "generic keyed-random-function on Z_N",
                "seed": args.seed,
                "parameters": summary["parameters"],
                "seed_streams": {
                    "walk_key_tag": 1,
                    "dp_key_tag": 2,
                    "pool_starts_tag": 3,
                    "target_seed": 100 + args.seed,
                    "union_find_tie_break": 200 + args.seed,
                    "phi_stream": 400 + args.seed,
                    "finaliser": "splitmix64",
                },
            },
            "timing": {
                "started_at": started.isoformat().replace("+00:00", "Z"),
                "finished_at": finished.isoformat().replace("+00:00", "Z"),
                "wall_seconds": wall,
            },
            "resources": {
                "peak_rss_bytes": rss_bytes(),
                "cpu_seconds": cpu,
            },
            "result": {
                "metrics": {
                    "n_cells": len(cells),
                    "solved_fractions": [
                        {
                            "T_0": c["T_0"],
                            "U": c["U"],
                            "phi": c["phi"],
                            "solved_fraction": c["solved_fraction"],
                            "LOWER": c["LOWER"],
                            "UPPER": c["UPPER"],
                        }
                        for c in cells
                    ],
                },
                "valid": not invalid,
                "invalid_reason": invalid_reason,
                "failure_class": "invalid_measurement" if invalid else None,
                "certificate": {"kind": "none", "verified": None, "verifier": None},
            },
            "artifacts": {
                "raw-result.json": "raw-result.json",
                "summary.json": "summary.json",
                "cost_table.json": "cost_table.json",
                **({"basin_histogram.json.gz": "basin_histogram.json.gz"} if args.basins else {}),
            },
            "claim_tier": "toy",
        }
    }
    (outdir / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False))
    (outdir / "stdout.log").write_text(
        f"{run_id} arm={args.arm} seed={args.seed} cells={len(cells)} "
        f"valid={not invalid} wall={wall:.3f}s\n"
    )
    (outdir / "stderr.log").write_text("" if not invalid else (invalid_reason or "") + "\n")
    print(f"wrote {outdir} valid={not invalid} cells={len(cells)} wall={wall:.3f}s")
    return 0 if not invalid else 2


if __name__ == "__main__":
    raise SystemExit(main())
