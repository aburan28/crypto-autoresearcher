#!/usr/bin/env python3
"""
TASK-20260806-b51ac8 / BATCH-5a4656 / GOAL-MLKEM-005

REPAIRED sensitivity demonstration for the projected-error tail-statistic
instrument built by BATCH-a51f91's TASK-20260805-708b70. That instrument's own
demonstration was ruled an INSTRUMENT FAILURE two independent ways (RT-20260806-d008e0
OBJ-3/OBJ-4; VAL-20260806-bb0559 DEF-1/DEF-3): the demonstration manipulated the
ERROR LAW while the null the design declared removes the PROJECTOR's provenance
(so its expected contrast was exactly zero to leading order by Haar rotation
invariance), and its 4s threshold was expressed in the per-draw sd of the arm
with structurally near-zero between-draw variance (making "4s" a ~2.0-2.5 sigma
test, not 4 sigma).

THE FIX (this script): manipulate the PROJECTOR, not the error law, via a graded
family Q_t = QR(sqrt(1-t) E_S + sqrt(t) G) interpolating a coordinate-aligned
projector (t=0) and a Haar-random one (t=1); declare the sensitivity threshold in
units of the SE OF THE (unpaired) DIFFERENCE of arm means at the declared draw
count; add three arms BATCH-a51f91 lacked (unreduced q-ary tail GSO, LLL-only
tail GSO, a Gaussian-error null of the null); and pre-register a ~1/sqrt(beta)
decay falsifier for the coordinate-alignment departure.

Same four cells, same frozen P1/P2, same Haar null (now graded(t=1)), same
null-arm-first discipline, same 2^20 CBD_{eta=2} errors shared across arms
within a cell, as BATCH-a51f91.

The frozen pre-registered prediction is in prediction_frozen.json; this script
refuses to run if its sha256 does not match the value recorded at freeze time,
and prints the freeze timestamp before computing any research number.

RULE DISCIPLINE
  * E[R] = beta/d is FORCED for every basis and every projector. Reported, never
    read as agreement.
  * The Beta law is DERIVED, not fitted; its variance is quoted in advance.
  * P4 (Gaussian null-of-the-null) is adjudicated FIRST. If it fails, this script
    still finishes the run (so nothing is silently discarded) but report.md must
    stop interpretation there.
  * Nothing measured here is transported to beta = 606, d = 1420.
  * No RT-20260806-d008e0 probe number is copied into this script or its output;
    every number here is freshly computed by THIS protocol run.

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
FROZEN_SHA256 = "780a2b44ca8cfa4a62e8586341e9bef790eb5dc86e39de2a6bf4634f4ad5b84f"

Q_MOD = 3329
ETA = 2
P_TAIL = [2.0 ** -10, 2.0 ** -16]
BODY_LO, BODY_HI = 0.01, 0.99
T_GRID = [0.00, 0.05, 0.10, 0.25, 0.50, 0.75, 1.00]
N_DRAW = 8


# ---------------------------------------------------------------- seeds
# Every source of randomness in this script is one of these families, all
# deterministic functions of (d, beta, index).
def seed_basis(d, beta, i):
    return 700000 + d * 1000 + beta * 10 + i            # fplll RNG (SAME as BATCH-a51f91)


def seed_error(d):
    return 20260805 + d                                  # numpy PCG64, CBD errors (SAME as BATCH-a51f91)


def seed_error_gauss(d):
    return 520260806 + d                                 # numpy PCG64, Gaussian errors (NEW, P4 only)


def seed_ES(d, beta, j):
    return 910000 + d * 1000 + beta * 10 + j             # numpy PCG64, coordinate-selector permutation


def seed_G(d, beta, j):
    return 920000 + d * 1000 + beta * 10 + j             # numpy PCG64, Gaussian d x beta matrix


# ---------------------------------------------------------------- CBD sampler
_POPCNT4 = np.array([bin(v).count("1") for v in range(16)], dtype=np.int8)


def cbd_eta2(rng, n, d):
    """FIPS 203 CBD_{eta=2}: e = popcount(a) - popcount(b), a,b two random bits.
    Returns int8 array (n,d), support {-2..2}, mean 0, variance eta/2 = 1."""
    r = rng.integers(0, 16, size=(n, d), dtype=np.uint8)
    return (_POPCNT4[r & 3] - _POPCNT4[r >> 2]).astype(np.int8)


# ---------------------------------------------------------------- reduction worker
def reduce_one(job):
    """Progressive reduction of ONE random q-ary basis: unreduced -> LLL -> BKZ-beta.
    Returns the orthonormal tail-GSO frame Q (d x beta) at ALL THREE stages plus
    instrument diagnostics. This is ONE reduction pass, not three independent ones."""
    d, beta, i, cache_dir = job
    tag = f"d{d}_b{beta}_i{i}"
    cpath = os.path.join(cache_dir, tag + ".npz") if cache_dir else None
    if cpath and os.path.exists(cpath):
        z = np.load(cpath, allow_pickle=True)
        return tag, z["Q_unred"], z["Q_lll"], z["Q_real"], json.loads(str(z["meta"]))

    os.environ.setdefault("OMP_NUM_THREADS", "1")
    from fpylll import IntegerMatrix, LLL, GSO, BKZ, FPLLL
    from fpylll.fplll.bkz_param import Strategy
    from fpylll.algorithms.bkz2 import BKZReduction

    def gso_tail(A_):
        B = np.array([[A_[r, c] for c in range(d)] for r in range(d)], dtype=np.float64)
        Qf, Rm = np.linalg.qr(B.T)
        gs_np = np.abs(np.diag(Rm))
        Q_ = np.ascontiguousarray(Qf[:, d - beta:], dtype=np.float32)
        orth_ = float(np.max(np.abs(Q_.T.astype(np.float64) @ Q_.astype(np.float64)
                                    - np.eye(beta))))
        return Q_, gs_np, orth_

    s = seed_basis(d, beta, i)
    FPLLL.set_random_seed(s)
    A = IntegerMatrix.random(d, "qary", k=d // 2, q=Q_MOD)

    Q_unred, gs_unred, orth_unred = gso_tail(A)

    t0 = time.time()
    LLL.reduction(A)
    t1 = time.time()
    Q_lll, gs_lll, orth_lll = gso_tail(A)

    # KN-TECH-14efa5: BKZ.DEFAULT_STRATEGY points at a path absent from the
    # wheel, so strategies are built in-process (pruning-free). SAME as
    # BATCH-a51f91's T2.
    strategies = [Strategy(b) for b in range(beta + 1)]
    par = BKZ.Param(block_size=beta, strategies=strategies,
                    max_loops=2, flags=BKZ.MAX_LOOPS)
    BKZReduction(A)(par)
    t2 = time.time()
    Q_real, gs_real, orth_real = gso_tail(A)

    # instrument cross-check on the FINAL (BKZ-reduced) stage only, against
    # fpylll's own GSO.Mat -- matches BATCH-a51f91's D5 diagnostic.
    M = GSO.Mat(A, float_type="d")
    M.update_gso()
    gs_fp = np.sqrt(np.array([M.get_r(j, j) for j in range(d)]))
    gso_rel_err = float(np.max(np.abs(gs_real - gs_fp) / gs_fp))

    lg = np.log2(gs_real)
    slope = float(np.polyfit(np.arange(d), lg, 1)[0])
    meta = {
        "tag": tag, "d": d, "beta": beta, "basis_index": i, "fplll_seed": s,
        "lll_seconds": round(t1 - t0, 3), "bkz_seconds": round(t2 - t1, 3),
        "b0_norm_unreduced": float(gs_unred[0]),
        "b0_norm_lll": float(gs_lll[0]),
        "b0_norm_real": float(gs_real[0]),
        "gso_log2_slope_per_index_real": slope,
        "root_hermite_delta_real": float(2.0 ** ((lg[0] - float(np.mean(lg))) / d)),
        "instrument_qr_vs_fpylll_gso_max_rel_err_real": gso_rel_err,
        "instrument_Q_orthonormality_max_abs_dev": {
            "unreduced": orth_unred, "lll": orth_lll, "real": orth_real,
        },
    }
    if cpath:
        np.savez_compressed(cpath, Q_unred=Q_unred, Q_lll=Q_lll, Q_real=Q_real,
                            meta=json.dumps(meta))
    return tag, Q_unred, Q_lll, Q_real, meta


# ---------------------------------------------------------------- graded projector family
def build_graded_Q(d, beta, t):
    """Return the d x (N_DRAW*beta) concatenated projector frame for grid point t,
    built from the SAME per-replicate (E_S, G) seeds across all t (coupling_across_t
    in prediction_frozen.json).

    G_NORMALIZATION (deviation D-1, recorded in receipt.json): G's columns are
    normalised to unit L2 norm before mixing, so that E_S (unit-norm columns by
    construction) and G sit on a COMPARABLE scale and sqrt(1-t)/sqrt(t) behave as
    genuine convex-combination-like mixing weights. Standard (unpivoted) QR is
    invariant under any INDEPENDENT POSITIVE per-column rescaling of its input
    (each Gram-Schmidt step's orthogonal complement scales linearly with that
    column's own factor and the unit-normalisation in the QR step cancels it
    exactly), so this normalisation leaves Q at t=0 (pure E_S, G does not even
    enter) and Q at t=1 (pure G, now G/||G_col||, a per-column positive rescaling
    of the unnormalised G) UNCHANGED relative to the unnormalised construction --
    it changes ONLY the interior t in (0,1). P3, P4 and P5 depend on t=0 and t=1
    alone, so they are bit-identical whether or not this normalisation is applied;
    it exists purely to make the interior graded-family dynamic-range/monotonicity
    diagnostic (KN-TECH-1a5b7e's 3-interior-point refinement) meaningful rather
    than a near-vertical cliff concentrated below t~0.02 (see receipt.json D-1 for
    the principal-angle diagnostic that found this)."""
    cols = []
    for j in range(N_DRAW):
        rng_es = np.random.default_rng(seed_ES(d, beta, j))
        perm = rng_es.permutation(d)
        S = perm[:beta]
        E_S = np.zeros((d, beta), dtype=np.float64)
        E_S[S, np.arange(beta)] = 1.0

        rng_g = np.random.default_rng(seed_G(d, beta, j))
        G = rng_g.standard_normal((d, beta))
        G = G / np.linalg.norm(G, axis=0, keepdims=True)

        M = np.sqrt(1.0 - t) * E_S + np.sqrt(t) * G
        Qf, _ = np.linalg.qr(M)
        cols.append(Qf.astype(np.float32))
    return np.ascontiguousarray(np.concatenate(cols, axis=1))


# ---------------------------------------------------------------- statistics
def emp_quantile(sorted_R, p):
    """FROZEN estimator, identical to BATCH-a51f91: k = round(p*N); q_emp = sorted_R[k-1]."""
    n = sorted_R.shape[0]
    k = int(round(p * n))
    k = max(1, min(n, k))
    return float(sorted_R[k - 1]), k


def order_stat_ci(sorted_R, p, level=0.95):
    from scipy.stats import binom
    n = sorted_R.shape[0]
    a = (1.0 - level) / 2.0
    lo = int(binom.ppf(a, n, p))
    hi = int(binom.ppf(1.0 - a, n, p)) + 1
    lo = max(1, min(n, lo))
    hi = max(1, min(n, hi))
    return float(sorted_R[lo - 1]), float(sorted_R[hi - 1])


def ks_body(sorted_R, a, b):
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
    """R: (N,G) float32 -- N error draws x G projector draws, all G columns sharing
    the SAME N error vectors. IDENTICAL to BATCH-a51f91's arm_stats."""
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
    ap.add_argument("--mode", choices=["full", "smoke"], default="full")
    ap.add_argument("--out", default=os.path.join(TASK_DIR, "results.json"))
    ap.add_argument("--cache-dir", default=None)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--deadline-seconds", type=float, default=4200.0)
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
    print("  P3          :", frozen["P3"]["statement"])
    print("  P4          :", frozen["P4"]["statement"])
    print("  P5 (falsifier):", frozen["P5_falsifier"]["statement_verbatim_from_handoff"])
    print("  P5 predicted decay ratio (beta40/beta30):",
          frozen["P5_falsifier"]["predicted_decay_ratio_beta40_over_beta30_at_fixed_d"])
    print("  FORCED      : E[R] = beta/d for EVERY basis and EVERY projector.")
    print("  FORCED      : Var(R) under Beta = 2b(d-b)/(d^2(d+2)), quoted in advance.")
    print("=" * 78)
    sys.stdout.flush()
    if sha != FROZEN_SHA256:
        print("ABORT: frozen prediction hash mismatch. Refusing to measure.")
        return 2

    if args.mode == "full":
        cells = [(100, 30), (100, 40), (140, 30), (140, 40)]
        n_err = 1 << 20
        chunk = 1 << 15
    else:
        cells = [(40, 12)]
        n_err = 1 << 14
        chunk = 1 << 13

    if args.cache_dir:
        os.makedirs(args.cache_dir, exist_ok=True)

    results = {
        "task_id": "TASK-20260806-b51ac8",
        "batch_id": "BATCH-5a4656",
        "goal_id": "GOAL-MLKEM-005",
        "repairs": "TASK-20260805-708b70 / BATCH-a51f91",
        "mode": args.mode,
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "frozen_prediction_sha256": sha,
        "frozen_prediction_verified": True,
        "frozen_at_utc": frozen["frozen_at_utc"],
        "frozen_prediction": frozen,
        "config": {"q": Q_MOD, "eta": ETA, "cells": cells,
                   "errors_per_basis": n_err, "draws_per_cell": N_DRAW,
                   "t_grid": T_GRID, "chunk": chunk,
                   "tail_levels": P_TAIL, "body_range": [BODY_LO, BODY_HI]},
        "seed_scheme": {
            "fplll_basis_seed": "700000 + d*1000 + beta*10 + i",
            "numpy_error_seed_cbd": "20260805 + d  (PCG64)",
            "numpy_error_seed_gaussian": "520260806 + d  (PCG64, P4 only)",
            "numpy_ES_seed": "910000 + d*1000 + beta*10 + j  (PCG64, coordinate-selector permutation)",
            "numpy_G_seed": "920000 + d*1000 + beta*10 + j  (PCG64, Gaussian d x beta matrix)",
            "note": "These five families are the ONLY sources of randomness.",
        },
        "instrument_checks": {},
        "reductions": [],
        "cells": {},
    }

    # ---- stage A: reductions (parallel, 1 BLAS thread per worker)
    jobs = [(d, b, i, args.cache_dir) for (d, b) in cells for i in range(N_DRAW)]
    print(f"[stage A] {len(jobs)} progressive (unreduced->LLL->BKZ) reductions on "
          f"{args.workers} workers")
    sys.stdout.flush()
    tA = time.time()
    QUNRED, QLLL, QREAL = {}, {}, {}
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for tag, Qu, Ql, Qr, meta in ex.map(reduce_one, jobs):
            QUNRED[tag], QLLL[tag], QREAL[tag] = Qu, Ql, Qr
            results["reductions"].append(meta)
            print(f"  {tag}: LLL {meta['lll_seconds']}s BKZ {meta['bkz_seconds']}s "
                  f"||b0|| unred={meta['b0_norm_unreduced']:.1f} "
                  f"lll={meta['b0_norm_lll']:.1f} real={meta['b0_norm_real']:.1f} "
                  f"gso_rel_err={meta['instrument_qr_vs_fpylll_gso_max_rel_err_real']:.2e}")
            sys.stdout.flush()
    tA = time.time() - tA
    print(f"[stage A] {tA:.1f}s")
    results["timing_stage_A_reduction_seconds"] = round(tA, 2)

    gso_err = max(m["instrument_qr_vs_fpylll_gso_max_rel_err_real"]
                  for m in results["reductions"])
    results["instrument_checks"]["qr_vs_fpylll_gso_max_rel_err_real"] = gso_err

    # ---- stage B/C: errors, projections, statistics
    for (d, beta) in cells:
        if time.time() - t_start > args.deadline_seconds:
            results["aborted_reason"] = "deadline"
            break
        key = f"d{d}_b{beta}"
        print(f"[cell {key}] generating {n_err} CBD_eta2 + Gaussian errors (d={d})")
        sys.stdout.flush()
        tB = time.time()

        # -- CBD errors (shared across ALL CBD-based arms in this cell) --
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

        # -- Gaussian errors (P4 only) --
        rngG = np.random.default_rng(seed_error_gauss(d))
        Efg = np.empty((n_err, d), dtype=np.float32)
        n2g = np.empty(n_err, dtype=np.float64)
        for s0 in range(0, n_err, chunk):
            s1 = min(n_err, s0 + chunk)
            Gi = rngG.standard_normal((s1 - s0, d)).astype(np.float32)
            n2g[s0:s1] = (Gi.astype(np.float64) ** 2).sum(1)
            Efg[s0:s1] = Gi
        results["instrument_checks"][f"gaussian_var_{key}"] = {
            "measured_per_coordinate_variance": float(np.mean(Efg.astype(np.float64) ** 2)),
            "target_per_coordinate_variance": 1.0,
        }

        # -- projector frames: real | unreduced | lll | graded(t) for each t --
        Qr = np.concatenate([QREAL[f"{key}_i{j}"] for j in range(N_DRAW)], axis=1)
        Qu = np.concatenate([QUNRED[f"{key}_i{j}"] for j in range(N_DRAW)], axis=1)
        Ql = np.concatenate([QLLL[f"{key}_i{j}"] for j in range(N_DRAW)], axis=1)

        Qgraded = {}
        for t in T_GRID:
            Qgraded[t] = build_graded_Q(d, beta, t)
        Q_t0 = Qgraded[0.00]   # reused for the P4 Gaussian-null arm

        Qall_cbd = np.ascontiguousarray(
            np.concatenate([Qr, Qu, Ql] + [Qgraded[t] for t in T_GRID], axis=1))
        n_blocks_cbd = 3 + len(T_GRID)   # real, unreduced, lll, then 7 graded t-values

        nb = N_DRAW * beta
        R_cbd = np.empty((n_err, n_blocks_cbd * N_DRAW), dtype=np.float32)
        for s0 in range(0, n_err, chunk):
            s1 = min(n_err, s0 + chunk)
            S = Ef[s0:s1] @ Qall_cbd
            S *= S
            G = S.reshape(s1 - s0, n_blocks_cbd * N_DRAW, beta).sum(axis=2)
            R_cbd[s0:s1] = G / n2[s0:s1, None]
            del S, G
        del Ef

        R_gauss_t0 = np.empty((n_err, N_DRAW), dtype=np.float32)
        for s0 in range(0, n_err, chunk):
            s1 = min(n_err, s0 + chunk)
            S = Efg[s0:s1] @ Q_t0
            S *= S
            R_gauss_t0[s0:s1] = S.reshape(s1 - s0, N_DRAW, beta).sum(axis=2) / n2g[s0:s1, None]
            del S
        del Efg

        tB = time.time() - tB
        print(f"[cell {key}] projections {tB:.1f}s; computing statistics")
        sys.stdout.flush()

        a, b = beta / 2.0, (d - beta) / 2.0
        qb = {p: float(betaincinv(a, b, p)) for p in P_TAIL}
        tC = time.time()

        def slice_block(k):
            return R_cbd[:, k * N_DRAW:(k + 1) * N_DRAW]

        arms = {
            "real": arm_stats(slice_block(0), a, b, qb),
            "unreduced_qary": arm_stats(slice_block(1), a, b, qb),
            "lll_only": arm_stats(slice_block(2), a, b, qb),
        }
        graded_arms = {}
        for idx, t in enumerate(T_GRID):
            graded_arms[f"t{t:.2f}"] = arm_stats(slice_block(3 + idx), a, b, qb)
        arms["graded"] = graded_arms
        arms["haar_null"] = graded_arms["t1.00"]        # identification, per prediction_frozen.json
        arms["coord_aligned"] = graded_arms["t0.00"]
        arms["gaussian_null_of_null"] = arm_stats(R_gauss_t0, a, b, qb)

        tC = time.time() - tC
        del R_cbd, R_gauss_t0

        # ---- P4: Gaussian null-of-the-null, adjudicated FIRST -------------
        gn = arms["gaussian_null_of_null"]["ratio_2em10_over_draws"]
        se_p4 = gn["sd"] / np.sqrt(N_DRAW)
        p4_dev = abs(gn["mean"] - 1.0)
        p4 = {
            "mean_ratio_2em10": gn["mean"], "sd_over_8_draws": gn["sd"],
            "SE_of_mean": float(se_p4), "abs_dev_from_1": float(p4_dev),
            "dev_in_units_of_SE": float(p4_dev / se_p4) if se_p4 > 0 else None,
            "threshold_multiplier": 4.0,
            "met": bool(se_p4 > 0 and p4_dev <= 4.0 * se_p4),
        }

        # ---- P3: coordinate-aligned (t=0) vs Haar (t=1), unpaired SE ------
        r0 = arms["coord_aligned"]["ratio_2em10_over_draws"]
        r1 = arms["haar_null"]["ratio_2em10_over_draws"]
        se_p3 = float(np.sqrt(r0["sd"] ** 2 + r1["sd"] ** 2) / np.sqrt(N_DRAW))
        shift_p3 = r0["mean"] - r1["mean"]
        p3 = {
            "comparator_by_name": "graded(t=1.00) == haar_null (the arm the null is ABOUT)",
            "mean_ratio_2em10_t0": r0["mean"], "sd_t0": r0["sd"],
            "mean_ratio_2em10_t1_haar": r1["mean"], "sd_t1_haar": r1["sd"],
            "SE_unpaired": se_p3,
            "signed_shift_t0_minus_t1": float(shift_p3),
            "threshold_4SE": 4.0 * se_p3,
            "shift_in_units_of_SE": float(shift_p3 / se_p3) if se_p3 > 0 else None,
            "met_directional": bool(se_p3 > 0 and shift_p3 >= 4.0 * se_p3),
            "met_two_sided": bool(se_p3 > 0 and abs(shift_p3) >= 4.0 * se_p3),
            "comparator_n_draws": N_DRAW,
        }

        # ---- graded-family full 7-point dynamic range + monotonicity ------
        seq = [float(graded_arms[f"t{t:.2f}"]["ratio_2em10_over_draws"]["mean"]) for t in T_GRID]
        diffs = np.diff(seq)
        monotone_nonincreasing = bool(np.all(diffs <= 1e-12))
        n_interior_strictly_decreasing = int(np.sum(diffs < -1e-12))
        graded_summary = {
            "t_grid": T_GRID,
            "ratio_2em10_mean_over_draws": seq,
            "ratio_2em10_sd_over_draws": [float(graded_arms[f"t{t:.2f}"]["ratio_2em10_over_draws"]["sd"])
                                          for t in T_GRID],
            "monotone_nonincreasing": monotone_nonincreasing,
            "n_interior_strictly_decreasing_steps": n_interior_strictly_decreasing,
            "n_steps_total": len(diffs),
        }

        # ---- P1/P2, evaluated on the NULL ARM (haar, t=1) FIRST ------------
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
        print(f"  [P4 first ] {key} gaussian_null_of_null mean={gn['mean']:.6f} "
              f"dev={p4_dev:.6f} SE={se_p4:.6f} met={p4['met']}")
        print(f"  [P3       ] {key} shift={shift_p3:.5f} SE={se_p3:.5f} "
              f"4SE={4*se_p3:.5f} met_directional={p3['met_directional']}")
        print(f"  [null-arm-first] {key} haar_null  P1={v_null['P1']['pass']} "
              f"P2={v_null['P2']['pass']}")
        print(f"  [real arm] {key} real       P1={v_real['P1']['pass']} "
              f"P2={v_real['P2']['pass']}")
        sys.stdout.flush()

        results["cells"][key] = {
            "d": d, "beta": beta, "k": d // 2, "q": Q_MOD,
            "forced_values": {
                "E_R_forced": beta / d,
                "Var_R_under_Beta_derived": 2.0 * beta * (d - beta) / (d ** 2 * (d + 2)),
                "beta_params": {"a": a, "b": b},
                "beta_quantiles": {f"p2em{int(round(-np.log2(p)))}": qb[p]
                                   for p in P_TAIL},
            },
            "arms": arms,
            "graded_family_summary": graded_summary,
            "P4_gaussian_null_of_null": p4,
            "P3_sensitivity": p3,
            "verdict_on_the_null_arm_FIRST": v_null,
            "verdict_on_the_real_arm": v_real,
            "timing_seconds": {"projections": round(tB, 2),
                               "statistics": round(tC, 2)},
        }

    # ---- P5: falsifier, cross-cell (needs all 4 cells) --------------------
    if all(f"d{d}_b{beta}" in results["cells"] for d in (100, 140) for beta in (30, 40)):
        p5 = {}
        for d in (100, 140):
            dep30 = results["cells"][f"d{d}_b30"]["P3_sensitivity"]["signed_shift_t0_minus_t1"]
            dep40 = results["cells"][f"d{d}_b40"]["P3_sensitivity"]["signed_shift_t0_minus_t1"]
            predicted = frozen["P5_falsifier"]["predicted_decay_ratio_beta40_over_beta30_at_fixed_d"][f"d{d}"]
            measured_ratio = (dep40 / dep30) if dep30 != 0 else None
            p5[f"d{d}"] = {
                "departure_beta30": dep30, "departure_beta40": dep40,
                "both_positive": bool(dep30 > 0 and dep40 > 0),
                "decays_beta40_lt_beta30": bool(abs(dep40) < abs(dep30)),
                "measured_ratio_beta40_over_beta30": measured_ratio,
                "predicted_ratio_beta40_over_beta30": predicted,
                "relative_discrepancy_from_prediction":
                    (measured_ratio / predicted - 1.0)
                    if (measured_ratio is not None and predicted) else None,
            }
        results["P5_falsifier_adjudication"] = p5
        print("[P5 falsifier]", json.dumps(p5, indent=1))
        sys.stdout.flush()

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
