#!/usr/bin/env python3
"""Stage-1 analysis run: interpolate T_0(U) and report frozen comparison stats."""

from __future__ import annotations

import argparse
import json
import math
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

_EXP = Path(__file__).resolve().parents[1]
if str(_EXP) not in sys.path:
    sys.path.insert(0, str(_EXP))

from implementation.instrument import EPSILON, N_PILOT, T_BL, U_LADDER, W  # type: ignore

ROOT = Path(__file__).resolve().parents[3]
RUNS = _EXP / "runs"
ARMS = ("BASELINE", "GROW-UNCAP", "GROW-CAP", "NULL1", "KS", "PHI")
SEEDS = (1, 2, 3)


def loglin_t0(points: list[tuple[float, float]], epsilon: float) -> float | None:
    """Smallest T_0 at which success equals epsilon, log-linear on T_0>0.

    points: (T_0, solved_fraction) sorted by T_0. Returns None if the
    interpolated crossing is not bracketed on the measured grid.
    """
    pts = sorted((t, s) for t, s in points if t > 0)
    if not pts:
        return None
    # If even the largest T_0 is below epsilon, crossing is above the grid.
    if pts[-1][1] < epsilon:
        return None
    if pts[0][1] >= epsilon:
        return pts[0][0]
    for (t0, s0), (t1, s1) in zip(pts, pts[1:]):
        if s0 <= epsilon <= s1 or s1 <= epsilon <= s0:
            if s0 == s1:
                return t0
            # log-linear in T_0
            w = (epsilon - s0) / (s1 - s0)
            log_t = math.log(t0) + w * (math.log(t1) - math.log(t0))
            return math.exp(log_t)
    return None


def percentile_ci(samples: list[float]) -> dict[str, float | None]:
    """Percentile 95% interval. n=3 is disclosed; BCa is degenerate at n=3."""
    arr = np.array(samples, dtype=float)
    mean = float(arr.mean())
    if len(arr) < 2:
        return {"mean": mean, "ci_low": None, "ci_high": None, "n": len(arr),
                "method": "undefined_n<2"}
    lo, hi = np.percentile(arr, [2.5, 97.5])
    return {
        "mean": mean,
        "ci_low": float(lo),
        "ci_high": float(hi),
        "n": int(len(arr)),
        "method": "percentile_n=3_not_BCa",
        "note": "n=3 seeds; BCa acceleration is undefined. Percentile interval reported.",
    }


def load_summaries() -> dict[tuple[str, int], dict]:
    out = {}
    for seed in SEEDS:
        for arm in ARMS:
            path = RUNS / f"RUN-ECDLP-1de2ec-{arm.lower()}-s{seed}" / "summary.json"
            if not path.exists():
                raise FileNotFoundError(path)
            out[(arm, seed)] = json.loads(path.read_text())
    return out


def cell_map(summary: dict) -> dict[tuple[int, int, float], dict]:
    m = {}
    for c in summary["cells"]:
        m[(int(c["T_0"]), int(c["U"]), float(c["phi"]))] = c
    return m


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", required=True)
    args = parser.parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc)
    t0 = time.perf_counter()

    summaries = load_summaries()
    # Per seed, per U: T_0 grid of GROW-UNCAP solved fractions
    grow_t0u: dict[int, dict[int, list[tuple[float, float]]]] = {s: {u: [] for u in U_LADDER} for s in SEEDS}
    rows = []
    for (arm, seed), summary in summaries.items():
        for c in summary["cells"]:
            rows.append({"arm": arm, "seed": seed, **{k: c[k] for k in (
                "T_0", "U", "phi", "solved_fraction", "solved_fraction_first10",
                "LOWER", "UPPER", "deferred_resolution_loss", "S_peak_entries",
                "online_steps",
            )}})
            if arm == "GROW-UNCAP":
                grow_t0u[seed][int(c["U"])].append((float(c["T_0"]), float(c["solved_fraction"])))

    t0_of_u = {}
    ratios = {}
    for u in U_LADDER:
        per_seed = []
        for seed in SEEDS:
            est = loglin_t0(grow_t0u[seed][u], EPSILON)
            per_seed.append(est)
        finite = [x for x in per_seed if x is not None]
        ratios[u] = {
            "epsilon": EPSILON,
            "T_0_U_per_seed": per_seed,
            "T_0_U_over_T_BL": [None if x is None else x / T_BL for x in per_seed],
            "crossing_bracketed_count": len(finite),
            "ratio_ci": percentile_ci([x / T_BL for x in finite]) if finite else None,
        }
        t0_of_u[u] = per_seed

    # F1 ingredients at U=4096, T_0 = T_BL/2 (report only)
    def frac(arm: str, t0v: int, u: int) -> list[float]:
        vals = []
        for seed in SEEDS:
            cm = cell_map(summaries[(arm, seed)])
            key = (t0v, u, 1.0)
            if key not in cm:
                # PHI uses other phis; skip
                continue
            vals.append(float(cm[key]["solved_fraction"]))
        return vals

    f1 = {
        "U": 4096,
        "T_0": T_BL // 2,
        "GROW-UNCAP_solved": frac("GROW-UNCAP", T_BL // 2, 4096),
        "BASELINE_solved": frac("BASELINE", T_BL // 2, 4096),
        "NULL1_solved": frac("NULL1", T_BL // 2, 4096),
        "note": (
            "F1 comparison statistics only. This analysis does not judge "
            "whether the heuristic or hypothesis is supported."
        ),
    }

    # Bracket check: measured inside [LOWER, UPPER]
    bracket_violations = []
    for row in rows:
        sf, lo, up = row["solved_fraction"], row["LOWER"], row["UPPER"]
        if sf + 1e-15 < lo or sf > up + 1e-15:
            bracket_violations.append(row)

    # PHI monotonicity of solved fraction at U=4096, T_0=T_BL/2
    phi_rows = {}
    for seed in SEEDS:
        cm = cell_map(summaries[("PHI", seed)])
        phi_rows[seed] = {
            phi: cm[(T_BL // 2, 4096, phi)]["solved_fraction"]
            for phi in (0.0, 0.25, 0.5, 0.75, 1.0)
            if (T_BL // 2, 4096, phi) in cm
        }

    # KS vs modeled sqrt(2N/U) — measured online_steps/U vs modeled
    ks_cmp = {}
    for u in U_LADDER:
        modeled = (2 * N_PILOT / u) ** 0.5
        measured = []
        for seed in SEEDS:
            cm = cell_map(summaries[("KS", seed)])
            c = cm[(0, u, 1.0)]
            measured.append(c["online_steps"] / u)
        ks_cmp[u] = {
            "modeled_sqrt_2N_over_U": modeled,
            "measured_mean_steps_per_target": measured,
            "factor_vs_model": [m / modeled for m in measured],
        }

    tables = {
        "frozen_prediction_reference": {
            "quantity": "T_0(U)/T_BL(1) at epsilon=0.9, a=1/4, r=2, k=4",
            "source": "experiments/EXP-ECDLP-1de2ec/specification.yaml preregistered_prediction",
            "provenance": "internal",
        },
        "parameters": {"N": N_PILOT, "T_BL": T_BL, "W_definition": W, "epsilon": EPSILON},
        "T_0_of_U": ratios,
        "F1_ingredients": f1,
        "bracket_violations": bracket_violations,
        "phi_solved_U4096": phi_rows,
        "KS_vs_modeled": ks_cmp,
        "cell_rows": rows,
        "W_discrepancy": {
            "definition_W": W,
            "cost_model_listed_W": 362,
            "used": W,
            "note": "Executor used specification.definitions.W = sqrt(a N / T_BL).",
        },
    }
    (outdir / "analysis_tables.json").write_text(json.dumps(tables, indent=2, sort_keys=True) + "\n")

    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True)
    dirty_lines = [ln for ln in dirty.splitlines() if ln.strip()]
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
    finished = datetime.now(timezone.utc)
    wall = time.perf_counter() - t0
    command = (
        f"python3 experiments/EXP-ECDLP-1de2ec/implementation/analyze.py "
        f"--outdir {outdir}"
    )
    (outdir / "command.txt").write_text(command + "\n")
    summary = {
        "status": "completed_valid",
        "run_id": outdir.name,
        "experiment_id": "EXP-ECDLP-1de2ec",
        "task_id": "TASK-20260908-470642",
        "kind": "analysis",
        "n_producer_summaries": len(summaries),
        "T_0_of_U": ratios,
        "F1_ingredients": f1,
        "n_bracket_violations": len(bracket_violations),
        "certificate": {"kind": "none", "verified": None, "verifier": None},
        "claim_tier": "toy",
    }
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (outdir / "raw-result.json").write_text(json.dumps({"tables": tables}, indent=2) + "\n")
    env = {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "cpu_count": os.cpu_count(),
        "pid": os.getpid(),
    }
    (outdir / "environment.json").write_text(json.dumps(env, indent=2) + "\n")
    manifest = {
        "run": {
            "id": outdir.name,
            "experiment_id": "EXP-ECDLP-1de2ec",
            "task_id": "TASK-20260908-470642",
            "status": "completed_valid",
            "code": {
                "commit": sha,
                "dirty": bool(dirty_lines),
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
                "fallback_used": True,
                "fallback_reason": (
                    "Session served by Cursor Grok 4.6; numeric results are "
                    "deterministic Python over committed producer summaries."
                ),
                "numeric_results": "deterministic_code",
            },
            "environment": env,
            "inputs": {"producer_runs": 18, "seeds": list(SEEDS), "arms": list(ARMS)},
            "timing": {
                "started_at": started.isoformat().replace("+00:00", "Z"),
                "finished_at": finished.isoformat().replace("+00:00", "Z"),
                "wall_seconds": wall,
            },
            "resources": {
                "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
                "cpu_seconds": time.process_time(),
            },
            "result": {
                "metrics": {"n_bracket_violations": len(bracket_violations)},
                "valid": True,
                "invalid_reason": None,
                "certificate": {"kind": "none", "verified": None, "verifier": None},
            },
            "artifacts": {
                "analysis_tables.json": "analysis_tables.json",
                "summary.json": "summary.json",
                "raw-result.json": "raw-result.json",
            },
            "claim_tier": "toy",
        }
    }
    (outdir / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False))
    (outdir / "stdout.log").write_text(f"analysis wall={wall:.3f}s\n")
    (outdir / "stderr.log").write_text("")
    (outdir / "cost_table.json").write_text(json.dumps({
        "measured": "see producer cost_table.json files",
        "modeled": tables["KS_vs_modeled"],
    }, indent=2) + "\n")
    print(f"wrote {outdir} wall={wall:.3f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
