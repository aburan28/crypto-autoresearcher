#!/usr/bin/env python3
"""
TASK-20260805-708b70 / BATCH-a51f91 / GOAL-MLKEM-005

Measure  R = ||pi_{d-beta}(e)||^2 / ||e||^2  for CBD_{eta=2} errors against REAL
BKZ-reduced q-ary bases, and adjudicate its LEFT TAIL against Beta(beta/2,(d-beta)/2).

Three arms, identical statistic and identical code path on all three:

  real       projector = span of the last beta Gram-Schmidt vectors of an
             LLL+BKZ-beta reduced q-ary basis (8 independent bases per cell)
  haar       NULL ARM.  projector = Haar-random beta-dim subspace (QR of a
             Gaussian d x beta matrix), 8 independent draws, SAME error vectors.
             Object removed: the PROVENANCE OF THE PROJECTOR.
             Object preserved: the error law, beta, d, the statistic, the errors.
  demo       SENSITIVITY DEMONSTRATION.  projector stays Haar (same 8 draws),
             error becomes two-block anisotropic at matched total variance
             (per-coordinate sd ratio 2:1 between halves).

The frozen pre-registered prediction is in prediction_frozen.json; this script
refuses to run if its sha256 does not match the value recorded at freeze time,
and prints the freeze timestamp before computing any research number.

RULE DISCIPLINE
  * E[R] = beta/d is FORCED for every basis, reduced or not.  Reported, never
    read as agreement.
  * The Beta law is DERIVED, not fitted; its variance is quoted in advance.
  * The haar arm reproducing Beta is an INSTRUMENT CHECK, never a control that
    passed (KN-TECH-1a5b7e).
  * Nothing measured here is transported to beta = 606, d = 1420.

No git commit is performed by this script.
"""

import argparse
import hashlib
import json
import os
import platform
import resource
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
from scipy.special import betainc, betaincinv

TASK_DIR = os.path.dirname(os.path.abspath(__file__))
FROZEN_PATH = os.path.join(TASK_DIR, "prediction_frozen.json")
FROZEN_SHA256 = "29797476fef01ab9f1691bb09623b7a5592642ae1db57df66ba642d5387cd8ce"

Q_MOD = 3329
ETA = 2
P_TAIL = [2.0 ** -10, 2.0 ** -16]
BODY_LO, BODY_HI = 0.01, 0.99
C1 = float(np.sqrt(1.6))   # anisotropic scale, first half
C2 = float(np.sqrt(0.4))   # anisotropic scale, second half

# ---------------------------------------------------------------- seeds
# Every source of randomness in this script is one of these three families.
def seed_basis(d, beta, i):
    return 700000 + d * 1000 + beta * 10 + i          # fplll RNG, per (d,beta,i)


def seed_error(d):
    return 20260805 + d                                # numpy PCG64, per d


def seed_haar(d, beta, j):
    return 900000 + d * 1000 + beta * 10 + j           # numpy PCG64, per (d,beta,j)


# ---------------------------------------------------------------- CBD sampler
_POPCNT4 = np.array([bin(v).count("1") for v in range(16)], dtype=np.int8)


def cbd_eta2(rng, n, d):
    """FIPS 203 CBD_{eta=2}: e = popcount(a) - popcount(b), a,b two random bits.
    Returns int8 array (n,d), support {-2..2}, mean 0, variance eta/2 = 1."""
    r = rng.integers(0, 16, size=(n, d), dtype=np.uint8)
    return (_POPCNT4[r & 3] - _POPCNT4[r >> 2]).astype(np.int8)


# ---------------------------------------------------------------- reduction worker
def reduce_one(job):
    """LLL then BKZ-beta on an independent random q-ary basis; return the
    orthonormal tail-GSO frame Q (d x beta) plus instrument diagnostics."""
    d, beta, i, cache_dir = job
    tag = f"d{d}_b{beta}_i{i}"
    cpath = os.path.join(cache_dir, tag + ".npz") if cache_dir else None
    if cpath and os.path.exists(cpath):
        z = np.load(cpath, allow_pickle=True)
        return tag, z["Q"], json.loads(str(z["meta"]))

    os.environ.setdefault("OMP_NUM_THREADS", "1")
    from fpylll import IntegerMatrix, LLL, GSO, BKZ, FPLLL
    from fpylll.fplll.bkz_param import Strategy
    from fpylll.algorithms.bkz2 import BKZReduction

    s = seed_basis(d, beta, i)
    FPLLL.set_random_seed(s)
    A = IntegerMatrix.random(d, "qary", k=d // 2, q=Q_MOD)

    t0 = time.time()
    LLL.reduction(A)
    t1 = time.time()
    # KN-TECH-14efa5: BKZ.DEFAULT_STRATEGY points at a path absent from the
    # wheel, so strategies are built in-process (pruning-free).
    strategies = [Strategy(b) for b in range(beta + 1)]
    par = BKZ.Param(block_size=beta, strategies=strategies,
                    max_loops=2, flags=BKZ.MAX_LOOPS)
    BKZReduction(A)(par)
    t2 = time.time()

    B = np.array([[A[r, c] for c in range(d)] for r in range(d)],
                 dtype=np.float64)
    # B^T = Q Rm  =>  Q[:,i] = +-b*_i/||b*_i||, |Rm[i,i]| = ||b*_i||
    Qf, Rm = np.linalg.qr(B.T)
    gs_np = np.abs(np.diag(Rm))

    M = GSO.Mat(A, float_type="d")
    M.update_gso()
    gs_fp = np.sqrt(np.array([M.get_r(j, j) for j in range(d)]))
    gso_rel_err = float(np.max(np.abs(gs_np - gs_fp) / gs_fp))

    Q = np.ascontiguousarray(Qf[:, d - beta:], dtype=np.float32)
    orth = float(np.max(np.abs(Q.T.astype(np.float64) @ Q.astype(np.float64)
                               - np.eye(beta))))
    lg = np.log2(gs_np)
    slope = float(np.polyfit(np.arange(d), lg, 1)[0])
    meta = {
        "tag": tag, "d": d, "beta": beta, "basis_index": i, "fplll_seed": s,
        "lll_seconds": round(t1 - t0, 3), "bkz_seconds": round(t2 - t1, 3),
        "b0_norm": float(gs_np[0]),
        "gso_log2_slope_per_index": slope,
        "root_hermite_delta": float(2.0 ** ((lg[0] - float(np.mean(lg))) / d)),
        "instrument_qr_vs_fpylll_gso_max_rel_err": gso_rel_err,
        "instrument_Q_orthonormality_max_abs_dev": orth,
    }
    if cpath:
        np.savez_compressed(cpath, Q=Q, meta=json.dumps(meta))
    return tag, Q, meta


# ---------------------------------------------------------------- statistics
def emp_quantile(sorted_R, p):
    """FROZEN estimator: k = round(p*N); q_emp = sorted_R[k-1]."""
    n = sorted_R.shape[0]
    k = int(round(p * n))
    k = max(1, min(n, k))
    return float(sorted_R[k - 1]), k


def order_stat_ci(sorted_R, p, level=0.95):
    """Distribution-free CI for the p-quantile from binomial order statistics."""
    from scipy.stats import binom
    n = sorted_R.shape[0]
    a = (1.0 - level) / 2.0
    lo = int(binom.ppf(a, n, p))
    hi = int(binom.ppf(1.0 - a, n, p)) + 1
    lo = max(1, min(n, lo))
    hi = max(1, min(n, hi))
    return float(sorted_R[lo - 1]), float(sorted_R[hi - 1])


def ks_body(sorted_R, a, b):
    """sup|F_emp - F_Beta| restricted to {x : BODY_LO <= F_Beta(x) <= BODY_HI}."""
    n = sorted_R.shape[0]
    xlo = betaincinv(a, b, BODY_LO)
    xhi = betaincinv(a, b, BODY_HI)
    i0 = int(np.searchsorted(sorted_R, xlo, side="left"))
    i1 = int(np.searchsorted(sorted_R, xhi, side="right"))
    if i1 <= i0:
        return None
    x = sorted_R[i0:i1].astype(np.float64)
    F = betainc(a, b, x)
    idx = np.arange(i0, i1, dtype=np.float64)
    d1 = np.max(np.abs(idx / n - F))
    d2 = np.max(np.abs((idx + 1.0) / n - F))
    return float(max(d1, d2))


def arm_stats(R, a, b, qb):
    """R: (N,G) float32 -- N error draws x G projector draws.  All G columns
    share the SAME N error vectors, by construction."""
    n, g = R.shape
    per = []
    for j in range(g):
        col = np.sort(R[:, j].astype(np.float64))
        rec = {"mean": float(col.mean()), "var": float(col.var(ddof=1)),
               "min": float(col[0]), "ks_body": ks_body(col, a, b)}
        for p in P_TAIL:
            q, k = emp_quantile(col, p)
            lo, hi = order_stat_ci(col, p)
            key = f"p2em{int(round(-np.log2(p)))}"
            rec[key] = {"q_emp": q, "order_stat_k": k, "ratio": q / qb[p],
                        "ratio_ci95": [lo / qb[p], hi / qb[p]]}
        per.append(rec)

    flat = np.sort(R.reshape(-1).astype(np.float64))
    pooled = {"n_samples": int(flat.shape[0]), "mean": float(flat.mean()),
              "var": float(flat.var(ddof=1)), "min": float(flat[0]),
              "ks_body": ks_body(flat, a, b)}
    for p in P_TAIL:
        q, k = emp_quantile(flat, p)
        lo, hi = order_stat_ci(flat, p)
        key = f"p2em{int(round(-np.log2(p)))}"
        pooled[key] = {"q_emp": q, "order_stat_k": k, "ratio": q / qb[p],
                       "ratio_ci95": [lo / qb[p], hi / qb[p]]}

    means = np.array([r["mean"] for r in per])
    within = float(np.mean([r["var"] for r in per]))
    between = float(means.var(ddof=1))
    total = between + within
    between_corr = max(0.0, between - within / n)
    vd = {
        "n_groups": g, "n_per_group": n,
        "var_within_mean": within,
        "var_between_raw": between,
        "var_between_bias_corrected": between_corr,
        "var_total": total,
        "between_fraction_raw": between / total if total > 0 else None,
        "between_fraction_bias_corrected":
            between_corr / (between_corr + within) if within > 0 else None,
        "group_means": means.tolist(),
        "note": ("All G groups share the SAME N error vectors, so the sampling "
                 "noise in the group means is common-mode and largely cancels "
                 "in var_between; the raw figure is therefore already close to "
                 "the pure projector effect. Bias-corrected variant reported "
                 "beside it."),
    }
    ratios10 = np.array([r["p2em10"]["ratio"] for r in per])
    ratios16 = np.array([r["p2em16"]["ratio"] for r in per])
    return {
        "per_draw": per,
        "pooled": pooled,
        "variance_decomposition": vd,
        "ratio_2em10_over_draws": {"mean": float(ratios10.mean()),
                                   "sd": float(ratios10.std(ddof=1)),
                                   "min": float(ratios10.min()),
                                   "max": float(ratios10.max())},
        "ratio_2em16_over_draws": {"mean": float(ratios16.mean()),
                                   "sd": float(ratios16.std(ddof=1)),
                                   "min": float(ratios16.min()),
                                   "max": float(ratios16.max())},
    }


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["full", "smoke"], default="full")
    ap.add_argument("--out", default=os.path.join(TASK_DIR, "results.json"))
    ap.add_argument("--cache-dir", default=None)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--deadline-seconds", type=float, default=2900.0)
    args = ap.parse_args()

    t_start = time.time()

    # ---- gate 1: the frozen prediction, printed BEFORE any research number
    raw = open(FROZEN_PATH, "rb").read()
    sha = hashlib.sha256(raw).hexdigest()
    frozen = json.loads(raw)
    print("=" * 78)
    print("FROZEN PRE-REGISTERED PREDICTION")
    print("  path        :", FROZEN_PATH)
    print("  sha256      :", sha)
    print("  expected    :", FROZEN_SHA256)
    print("  frozen_at   :", frozen["frozen_at_utc"], "(git",
          frozen["frozen_at_git_commit"][:12] + ")")
    print("  run started :", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    print("  P1          :", frozen["P1"]["statement"])
    print("  P2          :", frozen["P2"]["statement"])
    print("  4s threshold:", frozen["null_sufficiency"]
          ["sensitivity_threshold_DECLARED_NOW"])
    print("  FORCED      : E[R] = beta/d for EVERY basis, reduced or not.")
    print("  FORCED      : Var(R) under Beta = 2b(d-b)/(d^2(d+2)), quoted in advance.")
    print("=" * 78)
    sys.stdout.flush()
    if sha != FROZEN_SHA256:
        print("ABORT: frozen prediction hash mismatch. Refusing to measure.")
        return 2

    if args.mode == "full":
        cells = [(100, 30), (100, 40), (140, 30), (140, 40)]
        n_err, n_draw = 1 << 20, 8
        chunk = 1 << 16
    else:
        cells = [(40, 12)]
        n_err, n_draw = 1 << 14, 3
        chunk = 1 << 13

    if args.cache_dir:
        os.makedirs(args.cache_dir, exist_ok=True)

    results = {
        "task_id": "TASK-20260805-708b70",
        "batch_id": "BATCH-a51f91",
        "goal_id": "GOAL-MLKEM-005",
        "mode": args.mode,
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "frozen_prediction_sha256": sha,
        "frozen_prediction_verified": True,
        "frozen_at_utc": frozen["frozen_at_utc"],
        "frozen_prediction": frozen,
        "config": {"q": Q_MOD, "eta": ETA, "cells": cells,
                   "errors_per_basis": n_err, "draws_per_cell": n_draw,
                   "chunk": chunk, "aniso_scales": [C1, C2],
                   "tail_levels": P_TAIL, "body_range": [BODY_LO, BODY_HI]},
        "seed_scheme": {
            "fplll_basis_seed": "700000 + d*1000 + beta*10 + i",
            "numpy_error_seed": "20260805 + d  (PCG64)",
            "numpy_haar_seed": "900000 + d*1000 + beta*10 + j  (PCG64)",
            "note": "These three families are the ONLY sources of randomness.",
        },
        "instrument_checks": {},
        "reductions": [],
        "cells": {},
    }

    # ---- stage A: reductions (parallel, 1 BLAS thread per worker)
    jobs = [(d, b, i, args.cache_dir) for (d, b) in cells for i in range(n_draw)]
    print(f"[stage A] {len(jobs)} LLL+BKZ reductions on {args.workers} workers")
    sys.stdout.flush()
    tA = time.time()
    QREAL = {}
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for tag, Q, meta in ex.map(reduce_one, jobs):
            QREAL[tag] = Q
            results["reductions"].append(meta)
            print(f"  {tag}: LLL {meta['lll_seconds']}s BKZ {meta['bkz_seconds']}s "
                  f"||b0||={meta['b0_norm']:.1f} "
                  f"gso_rel_err={meta['instrument_qr_vs_fpylll_gso_max_rel_err']:.2e}")
            sys.stdout.flush()
    tA = time.time() - tA
    print(f"[stage A] {tA:.1f}s")
    results["timing_stage_A_reduction_seconds"] = round(tA, 2)

    gso_err = max(m["instrument_qr_vs_fpylll_gso_max_rel_err"]
                  for m in results["reductions"])
    orth_err = max(m["instrument_Q_orthonormality_max_abs_dev"]
                   for m in results["reductions"])
    results["instrument_checks"]["qr_vs_fpylll_gso_max_rel_err"] = gso_err
    results["instrument_checks"]["tail_frame_orthonormality_max_abs_dev"] = orth_err

    # ---- stage B/C: errors, projections, statistics
    for (d, beta) in cells:
        if time.time() - t_start > args.deadline_seconds:
            results["aborted_reason"] = "deadline"
            break
        key = f"d{d}_b{beta}"
        print(f"[cell {key}] generating {n_err} CBD_eta2 errors (d={d})")
        sys.stdout.flush()
        tB = time.time()
        rng = np.random.default_rng(seed_error(d))

        Ef = np.empty((n_err, d), dtype=np.float32)
        n2 = np.empty(n_err, dtype=np.float64)
        n2a = np.empty(n_err, dtype=np.float64)
        hist = np.zeros(5, dtype=np.int64)
        h = d // 2
        for s0 in range(0, n_err, chunk):
            s1 = min(n_err, s0 + chunk)
            Ei = cbd_eta2(rng, s1 - s0, d)
            hist += np.bincount((Ei.astype(np.int32) + 2).ravel(), minlength=5)
            sq = (Ei.astype(np.int32) ** 2)
            n2[s0:s1] = sq.sum(1)
            n2a[s0:s1] = 1.6 * sq[:, :h].sum(1) + 0.4 * sq[:, h:].sum(1)
            Ef[s0:s1] = Ei

        # instrument check on the sampler (not a control)
        tot = hist.sum()
        pm = hist / tot
        results["instrument_checks"][f"cbd_pmf_{key}"] = {
            "measured": pm.tolist(),
            "exact_fips203_cbd_eta2": [1 / 16, 4 / 16, 6 / 16, 4 / 16, 1 / 16],
            "measured_per_coordinate_variance":
                float(sum(pm[i] * (i - 2) ** 2 for i in range(5))),
            "exact_per_coordinate_variance": 1.0,
        }

        # projector frames: real | haar | haar-with-anisotropic-error
        Qr = np.concatenate([QREAL[f"{key}_i{j}"] for j in range(n_draw)], axis=1)
        Qh = []
        for j in range(n_draw):
            g = np.random.default_rng(seed_haar(d, beta, j))
            Qh.append(np.linalg.qr(g.standard_normal((d, beta)))[0]
                      .astype(np.float32))
        Qh = np.concatenate(Qh, axis=1)
        scale = np.empty(d, dtype=np.float32)
        scale[:h] = C1
        scale[h:] = C2
        Qa = Qh * scale[:, None]     # ||Q^T S e||^2 == ||(S Q)^T e||^2
        Qall = np.ascontiguousarray(np.concatenate([Qr, Qh, Qa], axis=1))

        nb = n_draw * beta
        Rr = np.empty((n_err, n_draw), dtype=np.float32)
        Rh = np.empty((n_err, n_draw), dtype=np.float32)
        Ra = np.empty((n_err, n_draw), dtype=np.float32)
        for s0 in range(0, n_err, chunk):
            s1 = min(n_err, s0 + chunk)
            S = Ef[s0:s1] @ Qall
            S *= S
            G = S.reshape(s1 - s0, 3 * n_draw, beta).sum(axis=2)
            Rr[s0:s1] = G[:, :n_draw] / n2[s0:s1, None]
            Rh[s0:s1] = G[:, n_draw:2 * n_draw] / n2[s0:s1, None]
            Ra[s0:s1] = G[:, 2 * n_draw:] / n2a[s0:s1, None]
            del S, G
        del Ef
        tB = time.time() - tB
        print(f"[cell {key}] projections {tB:.1f}s; computing statistics")
        sys.stdout.flush()

        a, b = beta / 2.0, (d - beta) / 2.0
        qb = {p: float(betaincinv(a, b, p)) for p in P_TAIL}
        tC = time.time()
        arms = {"real": arm_stats(Rr, a, b, qb),
                "haar_null": arm_stats(Rh, a, b, qb),
                "demo_anisotropic": arm_stats(Ra, a, b, qb)}
        tC = time.time() - tC
        del Rr, Rh, Ra

        # ---- sensitivity adjudication (4s), per the frozen threshold
        s_spread = arms["haar_null"]["ratio_2em10_over_draws"]["sd"]
        delta = abs(arms["demo_anisotropic"]["ratio_2em10_over_draws"]["mean"]
                    - arms["haar_null"]["ratio_2em10_over_draws"]["mean"])
        sens = {
            "comparator_by_name": "haar_null (the arm the null is ABOUT)",
            "s_between_draw_sd_of_ratio_2em10_on_haar_arm": s_spread,
            "haar_ratio_2em10_mean": arms["haar_null"]["ratio_2em10_over_draws"]["mean"],
            "demo_ratio_2em10_mean": arms["demo_anisotropic"]["ratio_2em10_over_draws"]["mean"],
            "signed_shift_demo_minus_haar":
                arms["demo_anisotropic"]["ratio_2em10_over_draws"]["mean"]
                - arms["haar_null"]["ratio_2em10_over_draws"]["mean"],
            "abs_shift": delta,
            "threshold_4s": 4.0 * s_spread,
            "shift_in_units_of_s": (delta / s_spread) if s_spread > 0 else None,
            "met": bool(s_spread > 0 and delta >= 4.0 * s_spread),
            "comparator_n_draws": n_draw,
        }

        # ---- P1/P2, evaluated on the NULL ARM FIRST (KN-TECH-1a5b7e mode 4)
        def verdict(arm):
            r10 = arm["pooled"]["p2em10"]["ratio"]
            r16 = arm["pooled"]["p2em16"]["ratio"]
            bf = arm["variance_decomposition"]["between_fraction_raw"]
            return {
                "P1": {"ratio_2em10_pooled": r10, "dev_2em10": abs(r10 - 1.0),
                       "ratio_2em16_pooled": r16, "dev_2em16": abs(r16 - 1.0),
                       "pass_2em10": bool(abs(r10 - 1.0) <= 0.05),
                       "pass_2em16": bool(abs(r16 - 1.0) <= 0.10),
                       "pass": bool(abs(r10 - 1.0) <= 0.05
                                    and abs(r16 - 1.0) <= 0.10)},
                "P2": {"between_fraction": bf,
                       "pass": bool(bf is not None and bf <= 0.20)},
            }

        v_null = verdict(arms["haar_null"])
        v_real = verdict(arms["real"])
        print(f"  [null-arm-first] {key} haar_null  P1={v_null['P1']['pass']} "
              f"P2={v_null['P2']['pass']}  (P1 here is EXPECTED to pass by "
              f"construction: it is the unit test that is NOT a control)")
        print(f"  [real arm]       {key} real       P1={v_real['P1']['pass']} "
              f"P2={v_real['P2']['pass']}")
        print(f"  [sensitivity]    {key} shift={delta:.4f} s={s_spread:.5f} "
              f"4s={4*s_spread:.5f} met={sens['met']}")
        sys.stdout.flush()

        results["cells"][key] = {
            "d": d, "beta": beta, "k": d // 2, "q": Q_MOD,
            "forced_values": {
                "E_R_forced": beta / d,
                "E_R_forced_label": ("FORCED. Holds for EVERY basis, reduced or "
                                     "not, and for the Haar arm. ZERO INFORMATION."),
                "Var_R_under_Beta_derived": 2.0 * beta * (d - beta) / (d ** 2 * (d + 2)),
                "Var_R_label": ("DERIVED IN ADVANCE, not fitted. Agreement is not "
                                "a discovery."),
                "beta_params": {"a": a, "b": b},
                "beta_quantiles": {f"p2em{int(round(-np.log2(p)))}": qb[p]
                                   for p in P_TAIL},
            },
            "arms": arms,
            "sensitivity_demonstration": sens,
            "verdict_on_the_null_arm_FIRST": v_null,
            "verdict_on_the_real_arm": v_real,
            "timing_seconds": {"projections": round(tB, 2),
                               "statistics": round(tC, 2)},
        }

    results["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    results["wall_clock_seconds"] = round(time.time() - t_start, 2)
    results["peak_rss_gb"] = round(
        resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024.0 ** 2), 3)
    results["peak_rss_children_gb"] = round(
        resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / (1024.0 ** 2), 3)
    results["environment"] = {
        "python": sys.version, "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": __import__("scipy").__version__,
    }
    try:
        import fpylll
        results["environment"]["fpylll"] = fpylll.__version__
    except Exception:
        pass

    with open(args.out, "w") as f:
        json.dump(results, f, indent=1, sort_keys=False)
    print(f"[done] {args.out}  wall={results['wall_clock_seconds']}s "
          f"peak_rss={results['peak_rss_gb']}GB "
          f"children={results['peak_rss_children_gb']}GB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
