"""EXP-MTBK-306bdb full dataset driver v3 (protocol v1 per AMEND-001).

Usage: python3 experiments/EXP-MTBK-306bdb/code/run_mtbk_dataset.py

Implements the corrected falsifiable content after AMEND-001: measure, per
(seed, b, m) cell, the mean full-check ratio between the std and BKK
enumerators for (a) first-success target descent and (b) relation-collection,
and report the retention gamma and net speedup factor.  Compares against the
sweep-theorem ratio 2^(m-1) and the previous (m+1)/2 net claim.

Design-honesty frame (from the amendment):
  - The rescue window (K*(std)=inf, K*(BKK) finite) is EMPTY at toy sizes.
  - The falsifiable question is now whether the BKK channel approaches the
    sweep domain factor 2^(m-1), i.e. > 0.9 x 2^(m-1), or the geometric
    factor ~1.0-1.1.
No hypothesis status changes; this is Executor-style measurement only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import random
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    os.pardir, os.pardir, os.pardir))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from harness.toycurve import generate_instance  # noqa: E402

EXP_ID = "EXP-MTBK-306bdb"
EXP_DIR = os.path.join(REPO, "experiments", EXP_ID)
RUNS_DIR = os.path.join(EXP_DIR, "runs")

MODEL = {
    "requested": "executor-implementation",
    "resolved_model": "deepseek-v4-flash-free",
    "model_verified": True,
}

TARGETS_PER_CELL = 12
RELATIONS_PER_CELL = 40
BUDGET_PER_DESCENT = 400_000
BUDGET_COLLECT = 4_000_000


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def sha256_obj(obj) -> str:
    return hashlib.sha256(canon(obj).encode()).hexdigest()


def iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def git_state() -> dict:
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                            capture_output=True, text=True).stdout.strip() or "unknown"
    out = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"],
                         cwd=REPO, capture_output=True, text=True).stdout
    dirty = bool([l for l in out.splitlines() if l.strip()])
    return {"commit": commit, "dirty": dirty}


def environment() -> dict:
    return {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
    }


def build_threshold_base(inst, b_exp: float):
    E = inst.curve()
    p = E.p
    B_target = max(4, round(p ** b_exp))
    xs: list[int] = []
    x = 0
    while len(xs) < B_target and x < p:
        if E.lift_x(x) is not None:
            xs.append(x)
        x += 1
    return xs, (x if x < p else p)


def first_success(E, dom, xset, m, R, budget):
    """Ordered (m-1)-tuple enumeration that stops at the first successful
    target decomposition; returns (found, checks). Honors m via recursion."""
    checks = 0

    def rec(depth, prefix_sum):
        nonlocal checks
        if checks > budget:
            return False
        if depth == m - 1:
            checks += 1
            rest = E.add(R, E.negate(prefix_sum))
            return rest is not None and rest[0] in xset
        for x in dom:
            P = E.lift_x(x)
            if P is None:
                continue
            S = P if prefix_sum is None else E.add(prefix_sum, P)
            if rec(depth + 1, S):
                return True
        return False

    return rec(0, None), checks


def collect_relations(E, dom, xset, m, rel_target, budget):
    """Relation collection honoring m: enumerate (m-1)-tuples over dom, count
    those whose m-fold sum's negation lands in the base x-set."""
    checks = 0
    found = 0

    def rec(depth, prefix_sum):
        nonlocal checks, found
        if found >= rel_target or checks > budget:
            return
        if depth == m - 1:
            checks += 1
            neg = E.negate(prefix_sum)
            if neg is not None and neg[0] in xset:
                found += 1
            return
        for x in dom:
            P = E.lift_x(x)
            if P is None:
                continue
            S = P if prefix_sum is None else E.add(prefix_sum, P)
            rec(depth + 1, S)

    rec(0, None)
    return checks, found


def run_cell(inst, b_exp, m, seed):
    E = inst.curve()
    p = E.p
    N = E.order()
    F, t = build_threshold_base(inst, b_exp)
    xset = set(F)
    half = max(1, len(F) // 2)
    F_half = F[:half]

    per_cell_targets = max(4, TARGETS_PER_CELL // (m - 2))
    targets = []
    for i in range(per_cell_targets):
        j = (inst.seed * 7 + i * 13 + seed * 5) % max(inst.n, 1)
        R = E.mul(j + 1, inst.P)
        if R is not None:
            targets.append(R)

    t_rows = []
    jointly = 0
    for R in targets:
        fs, cs = first_success(E, F, xset, m, R, BUDGET_PER_DESCENT)
        fb, cb = first_success(E, F_half, xset, m, R, BUDGET_PER_DESCENT)
        if fs and fb and cb > 0:
            jointly += 1
        t_rows.append({"std_found": fs, "bkk_found": fb,
                       "std_checks": cs, "bkk_checks": cb})

    jointly_found = sum(1 for r in t_rows if r["std_found"] and r["bkk_found"])
    ratios = [r["std_checks"] / r["bkk_checks"] for r in t_rows
              if r["std_found"] and r["bkk_found"] and r["bkk_checks"] > 0]

    c_std, f_std = collect_relations(E, F, xset, m, RELATIONS_PER_CELL, BUDGET_COLLECT)
    c_bkk, f_bkk = collect_relations(E, F_half, xset, m, RELATIONS_PER_CELL, BUDGET_COLLECT)

    domain_ratio_theorem = 2 ** (m - 1)
    return {
        "cell": {"b_exp": b_exp, "m": m, "seed": seed},
        "curve": {"p": p, "N": N, "B": len(F), "half": half, "t": t},
        "targets": {
            "n": len(targets),
            "jointly_found": jointly,
            "descent_check_ratio": {
                "mean_full_check": (round(sum(ratios) / len(ratios), 4) if ratios else None),
                "min": (round(min(ratios), 4) if ratios else None),
                "max": (round(max(ratios), 4) if ratios else None),
                "jointly_rows": len(ratios),
            },
        },
        "relations": {
            "std_checks": c_std, "std_found": f_std,
            "bkk_checks": c_bkk, "bkk_found": f_bkk,
            "ratio_full_check_over_bkk": (round((c_std * max(f_bkk, 1)) /
                                         (c_bkk * max(f_std, 1)), 4)
                                   if f_std and f_bkk else None),
        },
        "reference": {
            "sweep_domain_ratio": domain_ratio_theorem,
            "sweep_net_speedup_m1over2": (m + 1) / 2,
            "geometric_model_N_over_B": round(N / len(F), 1),
            "sqrtN": round(math.sqrt(N), 1),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--curve-seeds", default="1,2,3,4,5")
    ap.add_argument("--bs", default="0.4,0.5,0.6")
    ap.add_argument("--ms", default="3,4")
    ap.add_argument("--seeds", default="1,2")
    ap.add_argument("--field-bits", type=int, default=10)
    ap.add_argument("--out-root", default=None)
    args = ap.parse_args()

    t0 = time.time()
    try:
        cell_results = []
        for cseed in (int(s) for s in args.curve_seeds.split(",")):
            inst = generate_instance(seed=cseed, field_bits=args.field_bits)
            for b in (float(s) for s in args.bs.split(",")):
                for m in (int(s) for s in args.ms.split(",")):
                    for seed in (int(s) for s in args.seeds.split(",")):
                        cell_results.append(run_cell(inst, b, m, seed))

        result = {
            "run_kind": "v3_corrected_dataset",
            "protocol_version": 1,
            "amendment": "AMEND-EXP-MTBK-306bdb-001",
            "factors": {"b": args.bs, "m": args.ms,
                        "curve_seeds": args.curve_seeds, "seed": args.seeds,
                        "field_bits": args.field_bits},
            "cells": cell_results,
            "summary": {
                "n_cells": len(cell_results),
                "descent_ratio_mean_over_cells": _agg(cell_results, "descent"),
                "relation_ratio_mean_over_cells": _agg(cell_results, "relations"),
            },
        }
        success = True
    except Exception:
        result = {"error": traceback.format_exc()}
        success = False

    elapsed = time.time() - t0
    if args.out_root is None:
        run_dir = os.path.join(RUNS_DIR, "RUN-MTBK-306bdb-cellgrid")
    else:
        run_dir = os.path.join(args.out_root, "RUN-MTBK-306bdb-cellgrid")
    os.makedirs(run_dir, exist_ok=True)

    manifest = {
        "run_id": "RUN-MTBK-306bdb-cellgrid",
        "experiment_id": EXP_ID,
        "status": "completed" if success else "failed_infrastructure",
        "started_at": iso(t0),
        "finished_at": iso(time.time()),
        "elapsed_seconds": round(elapsed, 3),
        "command": "python3 " + os.path.relpath(__file__, REPO),
        "git": git_state(),
        "environment": environment(),
        "policy": MODEL,
        "parameters": {"curve_seeds": args.curve_seeds, "bs": args.bs,
                       "ms": args.ms, "seeds": args.seeds,
                       "field_bits": args.field_bits},
        "result_sha256": sha256_obj(result),
        "validity": {"status": "valid" if success else "infrastructure_error",
                     "reason": None},
    }
    with open(os.path.join(run_dir, "manifest.yaml"), "w") as f:
        json.dump(manifest, f, indent=2, default=str)
    with open(os.path.join(run_dir, "result.json"), "w") as f:
        json.dump(result, f, indent=2, default=str)
    with open(os.path.join(run_dir, "command.txt"), "w") as f:
        f.write(os.path.relpath(__file__, REPO) + "\n")
    with open(os.path.join(run_dir, "stdout.txt"), "w") as f:
        json.dump(result, f, indent=2, default=str)
    with open(os.path.join(run_dir, "stderr.txt"), "w") as f:
        f.write("(no stderr captured)\n")

    print(json.dumps(result["summary"] if success else result, indent=2, default=str))
    return 0 if success else 1


def _agg(cells, key):
    vals = []
    for c in cells:
        e = c["targets"]["descent_check_ratio"] if key == "descent" else c["relations"]
        if key == "descent":
            if e.get("mean_full_check") is not None:
                vals.append(e["mean_full_check"])
        else:
            if e.get("ratio_full_check_over_bkk") is not None:
                vals.append(e["ratio_full_check_over_bkk"])
    return (round(sum(vals) / len(vals), 4) if vals else None)


if __name__ == "__main__":
    sys.exit(main())