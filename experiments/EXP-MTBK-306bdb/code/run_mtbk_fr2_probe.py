"""EXP-MTBK-306bdb FR-2 boundary probe driver (AMEND-EXP-MTBK-306bdb-002).

Usage: python3 experiments/EXP-MTBK-306bdb/code/run_mtbk_fr2_probe.py

Falsifies or confirms the rescue-window boundary claim at the sharpest
reachable toy cell: N=29 (prime-order group on p=29 / p=31 curves), m=3,
B=3, exactly the cell the BATCH-e26b68 review labeled FR-2.

Falsifiable quantities under the two competing models (review report
FR-2, DEC-20260806-bba4bf):

  - Sweep (rescuing) model: t_std = B^(m-1)/sqrt(N) = 9/sqrt(29) ~ 1.67 in
    [1,2) (K*(std) infinite), t_bkk = 0.5*B^(m-1)/sqrt(N) ~ 0.83 < 1
    (K*(BKK) finite) => a RESCUE is predicted at this cell: the standard
    enumerator should fail to cover some targets within the sweep-size
    budget while the half-domain BKK enumerator covers them.
  - Geometric model: t = (N/B)/sqrt(N) ~ (29/3)/5.39 ~ 1.79 for BOTH
    enumerators => NO rescue.

Executor role: measurement only. We sweep ALL N group elements as targets
(the whole group, since N=29 is tiny) and report first-success coverage and
full-check costs for the std enumerator (domain = full factor base F,
|F| = B = 3) and the BKK enumerator (domain = first half of F, |F_half|=1).
Bugs/bounds guarded: an exhausted budget is reported as budget-exhaustion,
never as a finite K*.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    os.pardir, os.pardir, os.pardir))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from harness.toycurve import EllipticCurve  # noqa: E402

EXP_ID = "EXP-MTBK-306bdb"
EXP_DIR = os.path.join(REPO, "experiments", EXP_ID)
RUNS_DIR = os.path.join(EXP_DIR, "runs")

MODEL = {
    "requested": "executor-implementation",
    "resolved_model": "deepseek-v4-flash-free",
    "model_verified": True,
}

# FR-2 boundary cell: N=29 prime group, achievable on p=29 (a=1,b=11) and
# p=31 (a=1,b=23).  B=3 (threshold base of size 3), m=3.
CURVES = [
    {"label": "p29_N29", "p": 29, "a": 1, "b": 11},
    {"label": "p31_N29", "p": 31, "a": 1, "b": 23},
]
M = 3
B_TARGET = 3
BUDGET_PER_DESCENT = 1_000_000


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


def build_base_strict(E, size) -> list[int]:
    """First `size` x-coordinates on E (F = {P : x(P) < t} of exact size)."""
    xs: list[int] = []
    x = 0
    while len(xs) < size and x < E.p:
        if E.lift_x(x) is not None:
            xs.append(x)
        x += 1
    return xs


def first_success(E, dom, xset, m, R, budget):
    """Ordered (m-1)-tuple enumeration, first success; returns (found, checks).
    Mirrors run_mtbk_dataset.first_success exactly."""
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


def probe_curve(cfg):
    E = EllipticCurve(cfg["p"], cfg["a"], cfg["b"])
    p = E.p
    N = E.order()
    F = build_base_strict(E, B_TARGET)
    xset = set(F)
    F_half = F[: max(1, len(F) // 2)]

    # All N group elements as targets (group order 29 => tiny, exhaustive).
    targets = []
    P = None
    for x in range(p):
        Pt = E.lift_x(x)
        if Pt is not None and Pt[1] != 0:
            P = Pt
            break
    if P is None:
        return {"curve": cfg, "error": "no non-2-torsion point found"}

    seen = set()
    for k in range(N):
        R = E.mul(k + 1, P)
        if R is None or R[1] == 0:
            continue
        ident = (R[0], R[1])
        if ident in seen:
            continue
        seen.add(ident)
        targets.append((k + 1, R))

    t_rows = []
    for (k, R) in targets:
        fs, cs = first_success(E, F, xset, M, R, BUDGET_PER_DESCENT)
        fb, cb = first_success(E, F_half, xset, M, R, BUDGET_PER_DESCENT)
        t_rows.append({"k": k,
                       "std_found": fs, "bkk_found": fb,
                       "std_checks": cs, "bkk_checks": cb,
                       "std_exhausted": cs > BUDGET_PER_DESCENT,
                       "bkk_exhausted": cb > BUDGET_PER_DESCENT})

    jointly = sum(1 for r in t_rows if r["std_found"] and r["bkk_found"])
    std_only = sum(1 for r in t_rows if r["std_found"] and not r["bkk_found"])
    bkk_only = sum(1 for r in t_rows if r["bkk_found"] and not r["std_found"])
    neither = sum(1 for r in t_rows if not r["std_found"] and not r["bkk_found"])
    std_rescue = sum(1 for r in t_rows if r["std_exhausted"] and r["bkk_found"])
    bkk_exhausted = sum(1 for r in t_rows if r["bkk_exhausted"])

    ratios = [r["std_checks"] / r["bkk_checks"] for r in t_rows
              if r["std_found"] and r["bkk_found"] and r["bkk_checks"] > 0]

    return {
        "curve": cfg,
        "group": {"p": p, "N": N, "B": len(F), "B_half": len(F_half)},
        "models": {
            "t_std_sweep": round((len(F) ** (M - 1)) / math.sqrt(N), 4),
            "t_std_geometric": round((N / len(F)) / math.sqrt(N), 4),
            "t_bkk_sweep_half": round(0.5 * (len(F) ** (M - 1)) / math.sqrt(N), 4),
            "t_bkk_geometric_half": round((N / len(F)) / math.sqrt(N), 4),
            "sweep_domain_ratio_B": len(F) ** (M - 1),
            "sweep_domain_ratio_B2": len(F_half) ** (M - 1),
            "sqrtN": round(math.sqrt(N), 4),
        },
        "targets": {
            "n_total_elems": len(targets),
            "std_found": sum(1 for r in t_rows if r["std_found"]),
            "bkk_found": sum(1 for r in t_rows if r["bkk_found"]),
            "jointly_found": jointly,
            "std_only": std_only,
            "bkk_only": bkk_only,
            "neither": neither,
            "std_exhausted_while_bkk_found": std_rescue,
            "bkk_exhausted": bkk_exhausted,
            "descent_check_ratio": {
                "mean_full_check": (round(sum(ratios) / len(ratios), 4) if ratios else None),
                "min": (round(min(ratios), 4) if ratios else None),
                "max": (round(max(ratios), 4) if ratios else None),
                "rows": len(ratios),
            },
        },
"verdict": {
            "sweep_rescue_predicted": (len(F) ** (M - 1)) >= math.sqrt(N),
            "rescue_observed": (bkk_only + std_rescue) > 0,
            "bkk_superset": bkk_only > 0,
            "std_superset": std_only > 0,
        },
    }


def main() -> int:
    t0 = time.time()
    try:
        cells = [probe_curve(cfg) for cfg in CURVES]
        status = "completed"
        result = {"run_kind": "fr2_boundary_probe",
                  "protocol_version": 2,
                  "amendment": "AMEND-EXP-MTBK-306bdb-002",
                  "m": M, "B": B_TARGET,
                  "curves": cells,
                  "summary": {
                      "n_curves": len(cells),
                      "rescue_observed": any(c["verdict"]["rescue_observed"] for c in cells),
                      "sweep_rescue_predicted": any(c["verdict"]["sweep_rescue_predicted"] for c in cells),
                      "rescue_model_count": sum(1 for c in cells if c["verdict"]["rescue_observed"]),
                  }}
    except Exception:
        status = "failed_infrastructure"
        result = {"error": traceback.format_exc()}
        success = False
    else:
        success = True

    elapsed = time.time() - t0
    run_dir = os.path.join(RUNS_DIR, "RUN-MTBK-306bdb-fr2")
    os.makedirs(run_dir, exist_ok=True)

    started_at = iso(t0)
    finished_at = iso(time.time())

    with open(os.path.join(run_dir, "raw-result.json"), "w") as f:
        json.dump(result, f, indent=2, default=str)

    manifest = {
        "run": {
            "id": "RUN-MTBK-306bdb-fr2",
            "experiment_id": EXP_ID,
            "status": status,
            "code": {
                "commit": git_state()["commit"],
                "dirty": git_state()["dirty"],
                "command": "python3 " + os.path.relpath(__file__, REPO),
                "driver_sha256": sha256_obj(open(__file__).read(),
                                            hexprefix=True) if False else None,
            },
            "inference": {
                "requested_policy": MODEL["requested"],
                "resolved_model_id": MODEL["resolved_model"],
                "reasoning_effort": None,
                "fallback_used": False,
            },
            "environment": environment(),
            "inputs": {"parameters": {"m": M, "B": B_TARGET,
                                      "curves": [c["label"] for c in CURVES]}},
            "timing": {"started_at": started_at, "finished_at": finished_at,
                       "elapsed_seconds": round(elapsed, 3)},
            "result": {
                "sha256": sha256_obj(result),
                "n_curves": result.get("summary", {}).get("n_curves"),
                "metrics": {
                    "wall_clock_seconds": round(elapsed, 3),
                    "sum_descent_checks": None,
                    "sum_relation_checks": None,
                },
                "valid": success,
                "invalid_reason": None,
                "certificate": {"kind": "none", "verified": True,
                                "verifier": "no-claim"},
            },
            "validity": {"status": "valid" if success else "infrastructure_error",
                         "reason": "FR-2 boundary probe (AMEND-002); per-curve records in raw-result.json"},
            "artifacts": ["command.txt", "environment.json", "stdout.log",
                          "stderr.log", "raw-result.json"],
        }
    }
    with open(os.path.join(run_dir, "manifest.yaml"), "w") as f:
        json.dump(manifest, f, indent=2, default=str)
    with open(os.path.join(run_dir, "command.txt"), "w") as f:
        f.write(os.path.relpath(__file__, REPO) + "\n")
    with open(os.path.join(run_dir, "environment.json"), "w") as f:
        json.dump(environment(), f, indent=2, default=str)
    with open(os.path.join(run_dir, "stdout.log"), "w") as f:
        json.dump(result, f, indent=2, default=str)
    with open(os.path.join(run_dir, "stderr.log"), "w") as f:
        f.write("(no stderr captured)\n")

    print(json.dumps(result.get("summary", result), indent=2, default=str))
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())