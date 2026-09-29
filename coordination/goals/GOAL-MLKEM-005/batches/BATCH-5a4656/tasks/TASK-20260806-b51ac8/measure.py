#!/usr/bin/env python3
"""
TASK-20260806-b51ac8 / BATCH-5a4656 / GOAL-MLKEM-005

Repaired C3 instrument. Extends BATCH-a51f91's TASK-20260805-708b70/measure.py
at the SAME four cells with the SAME frozen P1/P2 and the SAME Haar null,
replacing ONLY the sensitivity demonstration (the graded-projector family,
P3/P5) and adding the arms whose absence made the real arm uninterpretable
(unreduced q-ary tail GSO, LLL-only tail GSO, Gaussian-error null of the
null, P4).

Arms per cell, all sharing ONE realized set of 2^20 CBD_{eta=2} error
vectors (except the Gaussian-error null of the null, which uses a SEPARATE
Gaussian error array at matched per-coordinate variance):

  real              BKZ-reduced tail GSO frame (8 independent bases).
  haar_null         Haar-random beta-subspace (8 draws). Also serves as the
                    graded family's t=1.00 point (identical construction).
  graded_t{TAG}     Q_t = QR(sqrt(1-t) E_S + sqrt(t) G), t in
                    {0, 0.05, 0.10, 0.25, 0.50, 0.75}; t=1.00 is haar_null.
  unreduced_qary    tail GSO of the SAME 8 raw q-ary bases, before any LLL
                    or BKZ call.
  lll_only          tail GSO of the SAME 8 bases after LLL only.
  gaussian_null     the t=0 (coordinate-aligned) projector frame applied to
                    a FRESH Gaussian error array at matched variance
                    (eta/2 = 1). Predicts ratio ~= 1.000 (P4).

The frozen pre-registered prediction is in prediction_frozen.json; this
script refuses to run if its sha256 does not match the value recorded at
freeze time, and prints the freeze timestamp before computing any research
number.

RULE DISCIPLINE
  * E[R] = beta/d is FORCED for every projector arm. Reported, never read
    as agreement.
  * The Beta law is DERIVED, not fitted.
  * P4 must be adjudicated BEFORE P3, P5, or the real arm are read. If P4
    fails in a cell, this script still computes everything (so the failure
    mode itself is fully recorded), but flags that cell's real-arm reading
    as UNINTERPRETABLE per the frozen branches -- the interpretive stop is
    enforced in report.md, not by refusing to measure.
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
FROZEN_SHA256 = "a88e4224001a1e3195c7e2f757d13587bf92e768950bf44db8f83cc01b2a3222"

Q_MOD = 3329
ETA = 2
P_TAIL = [2.0 ** -10, 2.0 ** -16]
BODY_LO, BODY_HI = 0.01, 0.99
GRADED_T = [0.0, 0.05, 0.10, 0.25, 0.50, 0.75]   # t=1.00 is haar_null

# ---------------------------------------------------------------- seeds
# Every source of randomness in this script is one of SIX families, each a
# deterministic function of (d, beta[, t_index], j). Three are UNCHANGED
# from BATCH-a51f91 (basis, error, haar); three are NEW (graded_perm,
# graded_gauss, gaussian_null_error). All are printed in results.json.
def seed_basis(d, beta, i):
    return 700000 + d * 1000 + beta * 10 + i          # fplll RNG, per (d,beta,i)


def seed_error(d):
    return 20260805 + d                                # numpy PCG64, per d


def seed_haar(d, beta, j):
    return 900000 + d * 1000 + beta * 10 + j           # numpy PCG64, per (d,beta,j)


def seed_graded_perm(d, beta, j):
    return 910000 + d * 1000 + beta * 10 + j           # numpy PCG64, per (d,beta,j)


def seed_graded_gauss(d, beta, t_index, j):
    return 920000 + d * 1000 + beta * 10 + t_index * 100 + j


def seed_gaussian_null_error(d):
    return 930000 + d                                  # numpy PCG64, per d


# ---------------------------------------------------------------- CBD sampler
_POPCNT4 = np.array([bin(v).count("1") for v in range(16)], dtype=np.int8)


def cbd_eta2(rng, n, d):
    """FIPS 203 CBD_{eta=2}: e = popcount(a) - popcount(b), a,b two random bits.
    Returns int8 array (n,d), support {-2..2}, mean 0, variance eta/2 = 1."""
    r = rng.integers(0, 16, size=(n, d), dtype=np.uint8)
    return (_POPCNT4[r & 3] - _POPCNT4[r >> 2]).astype(np.int8)


# ---------------------------------------------------------------- graded family
def qr_signfix(M):
    """Reduced QR with sign convention diag(R) >= 0, so Q is uniquely
    determined and QR(Gaussian) is a standard Haar-random-frame sampler."""
    Q, R = np.linalg.qr(M)
    s = np.sign(np.diag(R))
    s[s == 0] = 1.0
    return Q * s[None, :], np.min(np.abs(np.diag(R)))


def graded_frame(d, beta, t, rng_perm, rng_gauss):
    """Q_t = QR(sqrt(1-t) E_S + sqrt(t) G). E_S: first beta columns of a
    random d x d permutation matrix (a random coordinate subset, already
    orthonormal). G: d x beta iid standard Gaussian. Returns (Q, min_pivot)."""
    perm = rng_perm.permutation(d)
    ES = np.zeros((d, beta), dtype=np.float64)
    ES[perm[:beta], np.arange(beta)] = 1.0
    if t <= 0.0:
        return ES.astype(np.float32), 1.0
    G = rng_gauss.standard_normal((d, beta))
    M = np.sqrt(1.0 - t) * ES + np.sqrt(t) * G
    Q, piv = qr_signfix(M)
    return Q.astype(np.float32), float(piv)


# ---------------------------------------------------------------- reduction worker
def tail_frame_from_integer_matrix(A, d, beta):
    """Numpy Householder QR tail-GSO frame of a d x d fpylll IntegerMatrix,
    at whatever reduction stage A currently is. Returns (Q_tail, gs_norms)."""
    B = np.array([[A[r, c] for c in range(d)] for r in range(d)],
                 dtype=np.float64)
    Qf, Rm = np.linalg.qr(B.T)
    gs = np.abs(np.diag(Rm))
    Q = np.ascontiguousarray(Qf[:, d - beta:], dtype=np.float32)
    return Q, gs


def reduce_one(job):
    """Generate one random q-ary basis; return tail-GSO frames at THREE
    stages (unreduced, LLL-only, LLL+BKZ-beta) from the SAME basis, plus
    instrument diagnostics on the final (BKZ) stage."""
    d, beta, i, cache_dir = job
    tag = f"d{d}_b{beta}_i{i}"
    cpath = os.path.join(cache_dir, tag + ".npz") if cache_dir else None
    if cpath and os.path.exists(cpath):
        z = np.load(cpath, allow_pickle=True)
        return (tag, z["Q_unred"], z["Q_lll"], z["Q_bkz"],
                json.loads(str(z["meta"])))

    os.environ.setdefault("OMP_NUM_THREADS", "1")
    from fpylll import IntegerMatrix, LLL, GSO, BKZ, FPLLL
    from fpylll.fplll.bkz_param import Strategy
    from fpylll.algorithms.bkz2 import BKZReduction

    s = seed_basis(d, beta, i)
    FPLLL.set_random_seed(s)
    A_unred = IntegerMatrix.random(d, "qary", k=d // 2, q=Q_MOD)

    Q_unred, gs_unred = tail_frame_from_integer_matrix(A_unred, d, beta)

    A_lll = IntegerMatrix.from_matrix(A_unred)
    t0 = time.time()
    LLL.reduction(A_lll)
    t1 = time.time()
    Q_lll, gs_lll = tail_frame_from_integer_matrix(A_lll, d, beta)

    A_bkz = IntegerMatrix.from_matrix(A_lll)
    # KN-TECH-14efa5: BKZ.DEFAULT_STRATEGY points at a path absent from the
    # wheel, so strategies are built in-process (pruning-free).
    strategies = [Strategy(b) for b in range(beta + 1)]
    par = BKZ.Param(block_size=beta, strategies=strategies,
                    max_loops=2, flags=BKZ.MAX_LOOPS)
    BKZReduction(A_bkz)(par)
    t2 = time.time()
    Q_bkz, gs_bkz = tail_frame_from_integer_matrix(A_bkz, d, beta)

    M = GSO.Mat(A_bkz, float_type="d")
    M.update_gso()
    gs_fp = np.sqrt(np.array([M.get_r(j, j) for j in range(d)]))
    gso_rel_err = float(np.max(np.abs(gs_bkz - gs_fp) / gs_fp))
    orth = float(np.max(np.abs(Q_bkz.T.astype(np.float64) @ Q_bkz.astype(np.float64)
                               - np.eye(beta))))

    lg = np.log2(gs_bkz)
    slope = float(np.polyfit(np.arange(d), lg, 1)[0])
    meta = {
        "tag": tag, "d": d, "beta": beta, "basis_index": i, "fplll_seed": s,
        "lll_seconds": round(t1 - t0, 3), "bkz_seconds": round(t2 - t1, 3),
        "b0_norm_unreduced": float(gs_unred[0]),
        "b0_norm_lll": float(gs_lll[0]),
        "b0_norm_bkz": float(gs_bkz[0]),
        "gso_log2_slope_per_index_bkz": slope,
        "root_hermite_delta_bkz": float(2.0 ** ((lg[0] - float(np.mean(lg))) / d)),
        "instrument_qr_vs_fpylll_gso_max_rel_err_bkz": gso_rel_err,
        "instrument_Q_orthonormality_max_abs_dev_bkz": orth,
    }
    if cpath:
        np.savez_compressed(cpath, Q_unred=Q_unred, Q_lll=Q_lll, Q_bkz=Q_bkz,
                            meta=json.dumps(meta))
    return tag, Q_unred, Q_lll, Q_bkz, meta


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
    """R: (N,G) float32 -- N error draws x G projector draws. All G columns
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
    ap.add_argument("--mode", choices=["full", "smoke", "medium"], default="full")
    ap.add_argument("--out", default=os.path.join(TASK_DIR, "results.json"))
    ap.add_argument("--cache-dir", default=None)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--deadline-seconds", type=float, default=4300.0)
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
    print("  P3          :", frozen["P3"]["statement"])
    print("  P4          :", frozen["P4"]["statement"])
    print("  P5 falsifier predicted decay ratios:",
          frozen["the_falsifier_P5_numeric_predictions_frozen_before_measuring"]
          ["predicted_decay_ratio_beta30_over_beta40_at_fixed_d"])
    print("  FORCED      : E[R] = beta/d for EVERY projector arm.")
    print("=" * 78)
    sys.stdout.flush()
    if sha != FROZEN_SHA256:
        print("ABORT: frozen prediction hash mismatch. Refusing to measure.")
        return 2

    if args.mode == "full":
        cells = [(100, 30), (100, 40), (140, 30), (140, 40)]
        n_err, n_draw = 1 << 20, 8
        chunk = 1 << 16
    elif args.mode == "medium":
        # NOT a protocol run: real (d, beta) at reduced N for code-path /
        # timing validation only. Never written into the deliverables.
        cells = [(100, 30)]
        n_err, n_draw = 1 << 16, 8
        chunk = 1 << 14
    else:
        cells = [(40, 12)]
        n_err, n_draw = 1 << 14, 3
        chunk = 1 << 13

    if args.cache_dir:
        os.makedirs(args.cache_dir, exist_ok=True)

    results = {
        "task_id": "TASK-20260806-b51ac8",
        "batch_id": "BATCH-5a4656",
        "goal_id": "GOAL-MLKEM-005",
        "mode": args.mode,
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "frozen_prediction_sha256": sha,
        "frozen_prediction_verified": True,
        "frozen_at_utc": frozen["frozen_at_utc"],
        "config": {"q": Q_MOD, "eta": ETA, "cells": cells,
                   "errors_per_basis": n_err, "draws_per_cell": n_draw,
                   "chunk": chunk, "graded_t": GRADED_T,
                   "tail_levels": P_TAIL, "body_range": [BODY_LO, BODY_HI]},
        "seed_scheme": {
            "fplll_basis_seed": "700000 + d*1000 + beta*10 + i",
            "numpy_error_seed": "20260805 + d  (PCG64)",
            "numpy_haar_seed": "900000 + d*1000 + beta*10 + j  (PCG64)",
            "numpy_graded_perm_seed": "910000 + d*1000 + beta*10 + j  (PCG64)",
            "numpy_graded_gauss_seed": "920000 + d*1000 + beta*10 + t_index*100 + j  (PCG64)",
            "numpy_gaussian_null_error_seed": "930000 + d  (PCG64)",
            "note": "Six families total; three unchanged from BATCH-a51f91, three new. Only these are sources of randomness.",
        },
        "instrument_checks": {},
        "reductions": [],
        "cells": {},
    }

    # ---- stage A: reductions (parallel, 1 BLAS thread per worker)
    jobs = [(d, b, i, args.cache_dir) for (d, b) in cells for i in range(n_draw)]
    print(f"[stage A] {len(jobs)} basis generations (unreduced/LLL/BKZ each) "
          f"on {args.workers} workers")
    sys.stdout.flush()
    tA = time.time()
    QUNRED, QLLL, QBKZ = {}, {}, {}
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for tag, Qu, Ql, Qb, meta in ex.map(reduce_one, jobs):
            QUNRED[tag] = Qu
            QLLL[tag] = Ql
            QBKZ[tag] = Qb
            results["reductions"].append(meta)
            print(f"  {tag}: LLL {meta['lll_seconds']}s BKZ {meta['bkz_seconds']}s "
                  f"||b0|| unred={meta['b0_norm_unreduced']:.1f} "
                  f"lll={meta['b0_norm_lll']:.1f} bkz={meta['b0_norm_bkz']:.1f} "
                  f"gso_rel_err={meta['instrument_qr_vs_fpylll_gso_max_rel_err_bkz']:.2e}")
            sys.stdout.flush()
    tA = time.time() - tA
    print(f"[stage A] {tA:.1f}s")
    results["timing_stage_A_reduction_seconds"] = round(tA, 2)

    gso_err = max(m["instrument_qr_vs_fpylll_gso_max_rel_err_bkz"]
                  for m in results["reductions"])
    orth_err = max(m["instrument_Q_orthonormality_max_abs_dev_bkz"]
                   for m in results["reductions"])
    results["instrument_checks"]["qr_vs_fpylll_gso_max_rel_err_bkz"] = gso_err
    results["instrument_checks"]["tail_frame_orthonormality_max_abs_dev_bkz"] = orth_err

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
        hist = np.zeros(5, dtype=np.int64)
        for s0 in range(0, n_err, chunk):
            s1 = min(n_err, s0 + chunk)
            Ei = cbd_eta2(rng, s1 - s0, d)
            hist += np.bincount((Ei.astype(np.int32) + 2).ravel(), minlength=5)
            sq = (Ei.astype(np.int32) ** 2)
            n2[s0:s1] = sq.sum(1)
            Ef[s0:s1] = Ei

        tot = hist.sum()
        pm = hist / tot
        results["instrument_checks"][f"cbd_pmf_{key}"] = {
            "measured": pm.tolist(),
            "exact_fips203_cbd_eta2": [1 / 16, 4 / 16, 6 / 16, 4 / 16, 1 / 16],
            "measured_per_coordinate_variance":
                float(sum(pm[i] * (i - 2) ** 2 for i in range(5))),
            "exact_per_coordinate_variance": 1.0,
        }

        # ---- Gaussian error array for P4, SAME N, matched variance = 1
        rngG = np.random.default_rng(seed_gaussian_null_error(d))
        EfG = rngG.standard_normal((n_err, d)).astype(np.float32)
        n2G = (EfG.astype(np.float64) ** 2).sum(1)

        # ---- build all projector frames for this cell
        Qr = np.concatenate([QBKZ[f"{key}_i{j}"] for j in range(n_draw)], axis=1)
        Qunred = np.concatenate([QUNRED[f"{key}_i{j}"] for j in range(n_draw)], axis=1)
        Qlll = np.concatenate([QLLL[f"{key}_i{j}"] for j in range(n_draw)], axis=1)

        Qh = []
        for j in range(n_draw):
            g = np.random.default_rng(seed_haar(d, beta, j))
            Qh.append(np.linalg.qr(g.standard_normal((d, beta)))[0]
                      .astype(np.float32))
        Qh = np.concatenate(Qh, axis=1)

        graded_pivots = {}
        Qg = {}          # t -> (d, n_draw*beta) concatenated frame
        for t_index, t in enumerate(GRADED_T):
            cols = []
            pivots = []
            for j in range(n_draw):
                rp = np.random.default_rng(seed_graded_perm(d, beta, j))
                rg = (np.random.default_rng(seed_graded_gauss(d, beta, t_index, j))
                      if t > 0.0 else None)
                Q, piv = graded_frame(d, beta, t, rp, rg)
                cols.append(Q)
                pivots.append(piv)
            Qg[t] = np.concatenate(cols, axis=1)
            graded_pivots[f"t{t:.2f}"] = {"min_pivot_over_draws": min(pivots),
                                          "pivots": pivots}
        results["instrument_checks"][f"graded_family_pivots_{key}"] = graded_pivots

        # t=0 frame is reused for the Gaussian null of the null
        Qt0 = Qg[0.0]

        # ---- project: pack everything sharing the CBD error array Ef
        arm_names_cbd = (["real", "haar_null", "unreduced_qary", "lll_only"]
                         + [f"graded_t{t:.2f}" for t in GRADED_T])
        Qall = np.ascontiguousarray(
            np.concatenate([Qr, Qh, Qunred, Qlll]
                           + [Qg[t] for t in GRADED_T], axis=1))
        n_arms_cbd = len(arm_names_cbd)
        R = {name: np.empty((n_err, n_draw), dtype=np.float32)
             for name in arm_names_cbd}
        for s0 in range(0, n_err, chunk):
            s1 = min(n_err, s0 + chunk)
            S = Ef[s0:s1] @ Qall
            S *= S
            G = S.reshape(s1 - s0, n_arms_cbd * n_draw, beta).sum(axis=2)
            for ai, name in enumerate(arm_names_cbd):
                R[name][s0:s1] = (G[:, ai * n_draw:(ai + 1) * n_draw]
                                  / n2[s0:s1, None])
            del S, G

        # ---- Gaussian-error null of the null: t=0 projector, Gaussian error
        Rgn = np.empty((n_err, n_draw), dtype=np.float32)
        for s0 in range(0, n_err, chunk):
            s1 = min(n_err, s0 + chunk)
            S = EfG[s0:s1] @ Qt0
            S *= S
            G = S.reshape(s1 - s0, n_draw, beta).sum(axis=2)
            Rgn[s0:s1] = G / n2G[s0:s1, None]
            del S, G

        del Ef, EfG
        tB = time.time() - tB
        print(f"[cell {key}] projections {tB:.1f}s; computing statistics")
        sys.stdout.flush()

        a, b = beta / 2.0, (d - beta) / 2.0
        qb = {p: float(betaincinv(a, b, p)) for p in P_TAIL}
        tC = time.time()
        arms = {name: arm_stats(R[name], a, b, qb) for name in arm_names_cbd}
        arms["gaussian_null"] = arm_stats(Rgn, a, b, qb)
        tC = time.time() - tC
        del R, Rgn

        # ---- P4: Gaussian null of the null, must return ~1.000
        gn = arms["gaussian_null"]["ratio_2em10_over_draws"]
        gn_sd_of_mean = gn["sd"] / np.sqrt(n_draw)
        p4 = {
            "gaussian_null_ratio_2em10_mean": gn["mean"],
            "gaussian_null_ratio_2em10_sd_over_draws": gn["sd"],
            "gaussian_null_ratio_2em10_sd_of_mean": float(gn_sd_of_mean),
            "abs_deviation_from_1": abs(gn["mean"] - 1.0),
            "declared_ci95_half_width_approx": float(1.96 * gn_sd_of_mean),
            "PASS": bool(abs(gn["mean"] - 1.0) <= 1.96 * gn_sd_of_mean
                        or abs(gn["mean"] - 1.0) <= 0.02),
            "pass_note": ("PASS if the deviation from 1.000 is within the "
                         "8-draw 95% CI of the mean, OR within an absolute "
                         "2% band (guards against a degenerate near-zero CI "
                         "at n=8). Both criteria and their inputs are shown."),
        }

        # ---- P3: t=0 vs haar_null, UNPAIRED SE-of-the-difference (declared
        # in advance in prediction_frozen.json); PAIRED reported as diagnostic.
        r10_t0 = arms["graded_t0.00"]["ratio_2em10_over_draws"]
        r10_haar = arms["haar_null"]["ratio_2em10_over_draws"]
        se_unpaired = float(np.sqrt(r10_t0["sd"] ** 2 + r10_haar["sd"] ** 2)
                            / np.sqrt(n_draw))
        per_t0 = np.array([r["p2em10"]["ratio"]
                           for r in arms["graded_t0.00"]["per_draw"]])
        per_haar = np.array([r["p2em10"]["ratio"]
                             for r in arms["haar_null"]["per_draw"]])
        cov_paired = float(np.cov(per_t0, per_haar, ddof=1)[0, 1])
        se_paired = float(np.sqrt(r10_t0["sd"] ** 2 + r10_haar["sd"] ** 2
                                  - 2 * cov_paired) / np.sqrt(n_draw)) \
            if (r10_t0["sd"] ** 2 + r10_haar["sd"] ** 2 - 2 * cov_paired) >= 0 \
            else None
        shift = r10_t0["mean"] - r10_haar["mean"]
        p3 = {
            "comparator_by_name": "haar_null (t=1.00 of the graded family; the arm the null is ABOUT)",
            "t0_ratio_2em10_mean": r10_t0["mean"], "t0_ratio_2em10_sd": r10_t0["sd"],
            "haar_ratio_2em10_mean": r10_haar["mean"], "haar_ratio_2em10_sd": r10_haar["sd"],
            "signed_shift_t0_minus_haar": shift,
            "se_unpaired_DECLARED_GATE": se_unpaired,
            "se_paired_diagnostic_only": se_paired,
            "cov_paired_diagnostic_only": cov_paired,
            "threshold_4SE": 4.0 * se_unpaired,
            "shift_in_units_of_SE_unpaired": (shift / se_unpaired) if se_unpaired > 0 else None,
            "MET": bool(se_unpaired > 0 and shift >= 4.0 * se_unpaired),
            "comparator_n_draws": n_draw,
        }

        # ---- coordinate-alignment departure (for P5) and full graded curve
        graded_curve = {}
        for t in GRADED_T + [1.00]:
            name = "haar_null" if t >= 1.0 else f"graded_t{t:.2f}"
            rr = arms[name]["ratio_2em10_over_draws"]
            graded_curve[f"t{t:.2f}"] = {"mean": rr["mean"], "sd": rr["sd"]}
        departure_beta = abs(r10_t0["mean"] - r10_haar["mean"])

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
        v_unred = verdict(arms["unreduced_qary"])
        v_lll = verdict(arms["lll_only"])
        print(f"  [P4]  {key} gaussian_null ratio={gn['mean']:.6f} "
              f"dev={p4['abs_deviation_from_1']:.5f} PASS={p4['PASS']}")
        print(f"  [P3]  {key} t0={r10_t0['mean']:.5f} haar={r10_haar['mean']:.5f} "
              f"shift={shift:.5f} SE={se_unpaired:.5f} MET={p3['MET']}")
        print(f"  [real]{key} P1={v_real['P1']['pass']} P2={v_real['P2']['pass']}")
        sys.stdout.flush()

        results["cells"][key] = {
            "d": d, "beta": beta, "k": d // 2, "q": Q_MOD,
            "forced_values": {
                "E_R_forced": beta / d,
                "E_R_forced_label": "FORCED. Holds for every projector arm. ZERO INFORMATION.",
                "Var_R_under_Beta_derived": 2.0 * beta * (d - beta) / (d ** 2 * (d + 2)),
                "beta_params": {"a": a, "b": b},
                "beta_quantiles": {f"p2em{int(round(-np.log2(p)))}": qb[p]
                                   for p in P_TAIL},
                "predicted_relative_departure_scale":
                    float(np.sqrt(2.0 * (d - beta) / (beta * (d + 2)))),
            },
            "arms": arms,
            "P4_gaussian_null_of_the_null": p4,
            "P3_sensitivity_demonstration": p3,
            "graded_curve_ratio_2em10_mean_sd": graded_curve,
            "coordinate_alignment_departure_ratio_2em10": departure_beta,
            "verdict_on_the_null_arm_FIRST": v_null,
            "verdict_on_the_real_arm": v_real,
            "verdict_on_unreduced_qary_arm": v_unred,
            "verdict_on_lll_only_arm": v_lll,
            "timing_seconds": {"projections": round(tB, 2),
                               "statistics": round(tC, 2)},
        }

    # ---- P5: cross-cell falsifier check (needs both beta=30 and beta=40
    # at the same d, so computed once all cells are in)
    p5 = {}
    for d in sorted(set(c[0] for c in cells)):
        k30, k40 = f"d{d}_b30", f"d{d}_b40"
        if k30 in results["cells"] and k40 in results["cells"]:
            dep30 = results["cells"][k30]["coordinate_alignment_departure_ratio_2em10"]
            dep40 = results["cells"][k40]["coordinate_alignment_departure_ratio_2em10"]
            measured_ratio = (dep30 / dep40) if dep40 > 0 else None
            predicted_ratio = (frozen["the_falsifier_P5_numeric_predictions_frozen_before_measuring"]
                              ["predicted_decay_ratio_beta30_over_beta40_at_fixed_d"][f"d{d}"])
            p5[f"d{d}"] = {
                "departure_beta30": dep30, "departure_beta40": dep40,
                "measured_ratio_30_over_40": measured_ratio,
                "predicted_ratio_30_over_40": predicted_ratio,
                "decays_as_predicted_order_of_magnitude":
                    bool(measured_ratio is not None and 0.6 <= measured_ratio
                        <= max(predicted_ratio * 1.5, 1.8)) if measured_ratio else None,
                "flat_or_inverted_artifact_tell":
                    bool(measured_ratio is not None and measured_ratio <= 1.0),
            }
    results["P5_falsifier_check"] = p5

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
