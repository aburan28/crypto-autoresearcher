#!/usr/bin/env python3
"""
TASK-20260806-ca4377 / BATCH-f19c37 / GOAL-MLKEM-005
AM-1 measurement under the NOTARIZED pre-registration.

Governed by, and NOT modified by, this file:
  coordination/goals/GOAL-MLKEM-005/batches/BATCH-f19c37/tasks/
      TASK-20260806-5930ec/prereg.md
  sha256 cc7f3e1992d9fc250c05b02fe0a2a03463ea2e795e1f236fbd1c72d0d731b302
  notarized by TASK-20260806-53ad5c (archives/.../snapshot-receipt.json),
  committed BEFORE this task was dispatched.

This script loads that file READ-ONLY, re-hashes it, compares against the
notarized receipt, and ABORTS on mismatch.  It re-derives none of its
thresholds and adds, removes or re-spaces no grid point.

Carried VERBATIM from BATCH-436ddd / TASK-20260806-09ec68 `b2a.py`
(the frozen instrument): the four cells, k = d/2, q = 3329, CBD_{eta=2},
R = ||Q^T e||^2/||e||^2 on the orthonormal tail-beta GSO frame, the frozen
empirical quantile estimator at N = 2^20, 8 draws per arm, GATE_K = 4.0, every
seed formula, the Haar null arm, the Gaussian-error null of the null, the
null-arm-first read order, P1/P2, the beta-trend at BKZ-40, and the reduction
worker `reduce_one` byte for byte.

CHANGED, and only as prereg.md §2 and §4.1 freeze it:
  * the `t` grid: 7 points -> the 13 AM-1 points, verbatim;
  * G3: strict monotonicity -> tie-tolerant, scored under BOTH the paired and
    the unpaired step SE, recording the MORE SEVERE reading;
  * (S_j, G_j) are drawn ONCE per (d, beta, j) from seed_graded, BEFORE and
    INDEPENDENTLY of the t list, and reused across every t  (prereg §1.1).
    This is bit-identical to BATCH-436ddd's `graded_frames`, which drew them
    from a fresh rng seeded by (d, beta, j) with t consumed only afterwards;
    hoisting the draw makes the independence structural rather than incidental.
ADDED, as prereg §5.1(b) and §6 require:
  * V = sum_a P_aa^2 - beta^2/d computed EXACTLY (zero error draws) for every
    frame this script touches, with E[V]_haar = 2 beta (d-beta)/(d(d+2));
  * the per-cell detection floor as a MEASURED BRACKET in V units;
  * F-A (L2 ordering/shape on the graded path), scored twice: over all points,
    and over the 25-point NOVEL subset alone, which is the only admissible
    test of L2;
  * F-B (the beta trend) scored against BOTH L1 and L2;
  * the shared-point reproduction check against BATCH-436ddd.

Observations only.  No status change, no interpretation, no claim about ML-KEM
or any FIPS 203 parameter set.  Claim tier TOY.
This script performs no git operation and writes only inside its task directory
(results.json) plus an explicitly-passed --tables path.
"""

import argparse
import hashlib
import itertools
import json
import os
import platform
import resource
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
from scipy.special import betainc, betaincinv

TASK_DIR = os.path.dirname(os.path.abspath(__file__))
TASKS_DIR = os.path.normpath(os.path.join(TASK_DIR, ".."))
BATCH_DIR = os.path.normpath(os.path.join(TASKS_DIR, ".."))
BATCHES_DIR = os.path.normpath(os.path.join(BATCH_DIR, ".."))

PREREG_PATH = os.path.join(TASKS_DIR, "TASK-20260806-5930ec", "prereg.md")
RECEIPT_PATH = os.path.normpath(os.path.join(
    BATCH_DIR, "archives", "TASK-20260806-53ad5c", "snapshot-receipt.json"))
PREREG_REL = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-f19c37/tasks/"
              "TASK-20260806-5930ec/prereg.md")
PRIOR_436 = os.path.normpath(os.path.join(
    BATCHES_DIR, "BATCH-436ddd", "tasks", "TASK-20260806-09ec68",
    "b2a_results.json"))
PRIOR_A51 = os.path.normpath(os.path.join(
    BATCHES_DIR, "BATCH-a51f91", "tasks", "TASK-20260805-708b70",
    "results.json"))

# ------------------------------------------------- carried constants [carried]
Q_MOD = 3329
ETA = 2
P_TAIL = [2.0 ** -10, 2.0 ** -16]
BODY_LO, BODY_HI = 0.01, 0.99
CELLS = [(100, 30), (100, 40), (140, 30), (140, 40)]
EXT_D = [100, 140]
EXT_BKZ = 40
EXT_BETAS = [30, 40, 50, 60]
BETA_MAX = 60
GATE_K = 4.0
N_DRAW = 8

# ------------------------------------------- the AM-1 grid, prereg.md §2, VERBATIM
GRADED_T = [0.0, 0.0025, 0.005, 0.0075, 0.01, 0.015, 0.02, 0.03,
            0.05, 0.1, 0.25, 0.5, 1.0]
# prereg.md §4.1: tie tolerance is 1.0 * SE_step at 8 draws per arm.
G3_TIE_K = 1.0
# prereg.md §6.2: the F-A2 declared band.
FA2_BAND = (0.5, 2.0)
# prereg.md §6.3: carried CONSISTENT band and artifact-tell threshold.
FB_BAND = 0.25
FB_ARTIFACT_TELL = 0.90

# prereg.md §6.2 novelty accounting, declared before this run.
SHARED_T_436 = [0.0, 0.05, 0.1, 0.25, 0.5, 1.0]
NOVEL_ALL_CELLS = [0.0025, 0.0075, 0.015, 0.03]
NOVEL_EXCEPT_100_30 = [0.005, 0.01, 0.02]


def tkey(t):
    return f"{t:.4f}"


def arm_t(t):
    return f"graded_t{tkey(t)}"


GAUSS_ARMS = ["haar_null", "unreduced", "lll_only", "real_bkz",
              arm_t(0.0), arm_t(0.5)]


def is_novel(d, beta, t):
    """prereg.md §6.2.  25 points: 4 t in all four cells + 3 t in the three
    cells other than (100,30)."""
    if any(abs(t - x) < 1e-12 for x in NOVEL_ALL_CELLS):
        return True
    if any(abs(t - x) < 1e-12 for x in NOVEL_EXCEPT_100_30) \
            and (d, beta) != (100, 30):
        return True
    return False


# ====================================================================== seeds
def seed_basis(d, beta, i):
    return 700000 + d * 1000 + beta * 10 + i


def seed_error(d):
    return 20260805 + d


def seed_haar(d, beta, j):
    return 900000 + d * 1000 + beta * 10 + j


def seed_graded(d, beta, j):
    return 500000 + d * 1000 + beta * 10 + j


def seed_gauss_error(d):
    return 20260806 + d


# ================================================================= error laws
_POPCNT4 = np.array([bin(v).count("1") for v in range(16)], dtype=np.int8)


def cbd_eta2(rng, n, d):
    r = rng.integers(0, 16, size=(n, d), dtype=np.uint8)
    return (_POPCNT4[r & 3] - _POPCNT4[r >> 2]).astype(np.int8)


# ========================================================== reduction worker
# Carried byte for byte from BATCH-436ddd b2a.py `reduce_one`.
def reduce_one(job):
    d, beta, i = job
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    from fpylll import IntegerMatrix, LLL, GSO, BKZ, FPLLL
    from fpylll.fplll.bkz_param import Strategy
    from fpylll.algorithms.bkz2 import BKZReduction

    tag = f"d{d}_b{beta}_i{i}"
    s = seed_basis(d, beta, i)
    FPLLL.set_random_seed(s)
    A = IntegerMatrix.random(d, "qary", k=d // 2, q=Q_MOD)

    def to_np(M):
        return np.array([[M[r, c] for c in range(d)] for r in range(d)],
                        dtype=np.float64)

    def tail(M):
        Qf, Rm = np.linalg.qr(to_np(M).T)
        return (np.ascontiguousarray(Qf[:, d - BETA_MAX:], dtype=np.float32),
                np.abs(np.diag(Rm)))

    Q_raw, gs_raw = tail(A)
    t0 = time.time()
    LLL.reduction(A)
    t1 = time.time()
    Q_lll, gs_lll = tail(A)
    strategies = [Strategy(b) for b in range(beta + 1)]
    par = BKZ.Param(block_size=beta, strategies=strategies,
                    max_loops=2, flags=BKZ.MAX_LOOPS)
    BKZReduction(A)(par)
    t2 = time.time()
    Q_bkz, gs_bkz = tail(A)

    M = GSO.Mat(A, float_type="d")
    M.update_gso()
    gs_fp = np.sqrt(np.array([M.get_r(j, j) for j in range(d)]))
    gso_rel_err = float(np.max(np.abs(gs_bkz - gs_fp) / gs_fp))
    orth = float(np.max(np.abs(Q_bkz.T.astype(np.float64) @ Q_bkz.astype(np.float64)
                               - np.eye(BETA_MAX))))
    lg = np.log2(gs_bkz)
    meta = {
        "tag": tag, "d": d, "beta": beta, "basis_index": i, "fplll_seed": s,
        "lll_seconds": round(t1 - t0, 3), "bkz_seconds": round(t2 - t1, 3),
        "b0_norm": float(gs_bkz[0]),
        "gso_log2_slope_per_index": float(np.polyfit(np.arange(d), lg, 1)[0]),
        "root_hermite_delta": float(2.0 ** ((lg[0] - float(np.mean(lg))) / d)),
        "instrument_qr_vs_fpylll_gso_max_rel_err": gso_rel_err,
        "instrument_Q_orthonormality_max_abs_dev": orth,
        "b0_norm_raw": float(gs_raw[0]),
        "b0_norm_lll": float(gs_lll[0]),
        "gso_log2_slope_lll": float(np.polyfit(np.arange(d), np.log2(gs_lll), 1)[0]),
        "gso_log2_slope_raw": float(np.polyfit(np.arange(d), np.log2(gs_raw), 1)[0]),
    }
    return tag, Q_raw, Q_lll, Q_bkz, meta


# ================================================================= statistics
def sigma_over_mu(beta, d):
    """sd(R)/E[R] under Beta(beta/2,(d-beta)/2), exactly.  L1's s(beta,d)."""
    return float(np.sqrt(2.0 * (d - beta) / (beta * (d + 2.0))))


def emp_quantile(sorted_R, p):
    n = sorted_R.shape[0]
    k = max(1, min(n, int(round(p * n))))
    return float(sorted_R[k - 1]), k


def order_stat_ci(sorted_R, p, level=0.95):
    from scipy.stats import binom
    n = sorted_R.shape[0]
    a = (1.0 - level) / 2.0
    lo = max(1, min(n, int(binom.ppf(a, n, p))))
    hi = max(1, min(n, int(binom.ppf(1.0 - a, n, p)) + 1))
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
    return float(max(np.max(np.abs(idx / n - F)),
                     np.max(np.abs((idx + 1.0) / n - F))))


def arm_stats(R, a, b, qb, want_pooled=True):
    n, g = R.shape
    per = []
    for j in range(g):
        col = np.sort(R[:, j].astype(np.float64))
        rec = {"mean": float(col.mean()), "var": float(col.var(ddof=1)),
               "min": float(col[0]), "ks_body": ks_body(col, a, b)}
        for p in P_TAIL:
            q, k = emp_quantile(col, p)
            lo, hi = order_stat_ci(col, p)
            rec[f"p2em{int(round(-np.log2(p)))}"] = {
                "q_emp": q, "order_stat_k": k, "ratio": q / qb[p],
                "ratio_ci95": [lo / qb[p], hi / qb[p]]}
        per.append(rec)

    out = {"per_draw": per}
    if want_pooled:
        flat = np.sort(R.reshape(-1).astype(np.float64))
        pooled = {"n_samples": int(flat.shape[0]), "mean": float(flat.mean()),
                  "var": float(flat.var(ddof=1)), "min": float(flat[0]),
                  "ks_body": ks_body(flat, a, b)}
        for p in P_TAIL:
            q, k = emp_quantile(flat, p)
            lo, hi = order_stat_ci(flat, p)
            pooled[f"p2em{int(round(-np.log2(p)))}"] = {
                "q_emp": q, "order_stat_k": k, "ratio": q / qb[p],
                "ratio_ci95": [lo / qb[p], hi / qb[p]]}
        out["pooled"] = pooled

    means = np.array([r["mean"] for r in per])
    within = float(np.mean([r["var"] for r in per]))
    between = float(means.var(ddof=1))
    total = between + within
    between_corr = max(0.0, between - within / n)
    out["variance_decomposition"] = {
        "n_groups": g, "n_per_group": n,
        "var_within_mean": within, "var_between_raw": between,
        "var_between_bias_corrected": between_corr, "var_total": total,
        "between_fraction_raw": between / total if total > 0 else None,
        "between_fraction_bias_corrected":
            between_corr / (between_corr + within) if within > 0 else None,
        "group_means": means.tolist(),
        "note": ("All G groups share the SAME N error vectors, so the sampling "
                 "noise in the group means is common-mode and largely cancels "
                 "in var_between."),
    }
    for p in P_TAIL:
        key = f"p2em{int(round(-np.log2(p)))}"
        rr = np.array([r[key]["ratio"] for r in per])
        out[f"ratio_{key}_over_draws"] = {
            "mean": float(rr.mean()), "sd": float(rr.std(ddof=1)),
            "min": float(rr.min()), "max": float(rr.max()),
            "values": rr.tolist()}
    return out


def gate(arm, haar, k=GATE_K, n=N_DRAW):
    """prereg.md §3.  Pooled two-arm SE of the difference, 8 draws each."""
    ma = arm["ratio_p2em10_over_draws"]["mean"]
    sa = arm["ratio_p2em10_over_draws"]["sd"]
    mh = haar["ratio_p2em10_over_draws"]["mean"]
    sh = haar["ratio_p2em10_over_draws"]["sd"]
    se = float(np.sqrt(sa * sa / n + sh * sh / n))
    shift = float(ma - mh)
    return {"arm_mean": ma, "arm_sd": sa, "haar_mean": mh, "haar_sd": sh,
            "n_draws_each": n, "se_of_difference": se,
            "shift_arm_minus_haar": shift,
            "shift_in_units_of_se_of_difference":
                (shift / se) if se > 0 else None,
            "threshold_k": k, "threshold_abs": k * se,
            "upper_bound_statement_if_not_cleared":
                f"|D| < {k:.1f} x SE_diff = {k * se:.6f} "
                f"(upper bound at {n} draws, N = 2^20)",
            "cleared": bool(se > 0 and abs(shift) >= k * se)}


# ================================================================ projections
def project(Ef, n2, Q, n_draw, betap, chunk):
    N = Ef.shape[0]
    R = np.empty((N, n_draw), dtype=np.float32)
    for s0 in range(0, N, chunk):
        s1 = min(N, s0 + chunk)
        S = Ef[s0:s1] @ Q
        S *= S
        R[s0:s1] = S.reshape(s1 - s0, n_draw, betap).sum(axis=2) / n2[s0:s1, None]
        del S
    return R


def haar_frames(d, betap, n_draw):
    cols = []
    for j in range(n_draw):
        g = np.random.default_rng(seed_haar(d, betap, j))
        cols.append(np.linalg.qr(g.standard_normal((d, betap)))[0].astype(np.float32))
    return np.concatenate(cols, axis=1)


def graded_paths(d, betap, n_draw):
    """prereg.md §1.1: (S_j, G_j) drawn ONCE from seed_graded(d,beta,j), BEFORE
    and INDEPENDENTLY of the t list.  Bit-identical to BATCH-436ddd's draw
    order: fresh rng per j, then `choice` then `standard_normal`."""
    paths = []
    for j in range(n_draw):
        g = np.random.default_rng(seed_graded(d, betap, j))
        S = g.choice(d, size=betap, replace=False)
        G = g.standard_normal((d, betap))
        E = np.zeros((d, betap))
        E[S, np.arange(betap)] = 1.0
        paths.append((E, G))
    return paths


def graded_frames_from_paths(paths, t):
    cols = []
    for (E, G) in paths:
        Mx = np.sqrt(1.0 - t) * E + np.sqrt(t) * G
        cols.append(np.linalg.qr(Mx)[0].astype(np.float32))
    return np.concatenate(cols, axis=1)


def tail_slice(Qfull, betap):
    return np.ascontiguousarray(Qfull[:, BETA_MAX - betap:])


def stack(frames, betap):
    return np.ascontiguousarray(np.concatenate(
        [tail_slice(f, betap) for f in frames], axis=1))


# ============================================= V, the deterministic frame scalar
def frame_V(Qstack, d, betap, n_draw=N_DRAW):
    """prereg.md §5.1(b).  V = sum_a P_aa^2 - beta^2/d for P = Q Q^T.
    Deterministic: ZERO error draws.  Computed in float64 from the exact
    float32 frame the projection consumes."""
    per = []
    for j in range(n_draw):
        Q = Qstack[:, j * betap:(j + 1) * betap].astype(np.float64)
        pdiag = np.einsum("ij,ij->i", Q, Q)          # P_aa
        per.append(float((pdiag ** 2).sum() - betap * betap / d))
    arr = np.array(per)
    ev = 2.0 * betap * (d - betap) / (d * (d + 2.0))
    sd = float(arr.std(ddof=1))
    return {"per_draw": per, "mean": float(arr.mean()), "sd": sd,
            "E_V_haar_exact": ev, "excess_over_E_V_haar": float(arr.mean() - ev),
            "excess_in_sd_of_mean": (float(arr.mean() - ev) / (sd / np.sqrt(n_draw)))
            if sd > 0 else None,
            "n_error_draws_used": 0}


# ================================================== L2: the geometry law, D_pred
def d_pred_from_V(V, d, beta, p=2.0 ** -10):
    """prereg.md §6.1 L2, zero fitted parameters."""
    mu = beta / d
    nu = d / 2.0 + 1.0
    a, b = beta / 2.0, (d - beta) / 2.0
    f = 1.0 - V / (4.0 * beta * (1.0 - mu))
    f_clipped = max(f, 0.0)
    if f_clipped <= 0.0:
        return {"V": V, "f": f, "f_clipped": f_clipped, "D_pred": None,
                "note": "f clipped at 0; D_pred undefined"}
    nup = nu / f_clipped
    ap = mu * (nup - 1.0)
    bp = (1.0 - mu) * (nup - 1.0)
    q0 = float(betaincinv(a, b, p))
    q1 = float(betaincinv(ap, bp, p))
    return {"V": V, "f": f, "f_clipped": f_clipped,
            "nu": nu, "nu_prime": nup, "a_prime": ap, "b_prime": bp,
            "q_base": q0, "q_deflated": q1, "D_pred": q1 / q0 - 1.0}


# ============================================================ G3, tie-tolerant
def g3_scores(means, values, sds, n=N_DRAW, tol=G3_TIE_K):
    """prereg.md §4.1.  Steps over consecutive grid pairs; SE_step computed
    BOTH paired and unpaired; the recorded outcome is the MORE SEVERE reading
    (FAIL > TIE > PASS).  Adjacency is irrelevant."""
    steps = []
    for i in range(len(means) - 1):
        delta = means[i + 1] - means[i]
        v0 = np.array(values[i], dtype=np.float64)
        v1 = np.array(values[i + 1], dtype=np.float64)
        se_paired = float((v1 - v0).std(ddof=1) / np.sqrt(n))
        se_unpaired = float(np.sqrt(sds[i + 1] ** 2 / n + sds[i] ** 2 / n))
        steps.append({
            "i": i, "delta": float(delta),
            "se_step_paired": se_paired, "se_step_unpaired": se_unpaired,
            "delta_in_se_paired": (float(delta) / se_paired) if se_paired > 0 else None,
            "delta_in_se_unpaired": (float(delta) / se_unpaired) if se_unpaired > 0 else None,
            "is_increase": bool(delta > 0),
        })

    def score(conv):
        key = f"se_step_{conv}"
        incs = [s for s in steps if s["is_increase"]]
        if not incs:
            return {"outcome": "PASS", "n_increases": 0,
                    "max_increase_in_se": 0.0, "violations": []}
        worst = 0.0
        viol = []
        for s in incs:
            se = s[key]
            r = (s["delta"] / se) if se > 0 else float("inf")
            worst = max(worst, r)
            if r > tol:
                viol.append({"i": s["i"], "delta": s["delta"],
                             "se_step": se, "delta_in_se": r})
        return {"outcome": "FAIL" if viol else "TIE",
                "n_increases": len(incs),
                "max_increase_in_se": worst,
                "violations": viol}

    sp = score("paired")
    su = score("unpaired")
    rank = {"PASS": 0, "TIE": 1, "FAIL": 2}
    severe = sp if rank[sp["outcome"]] >= rank[su["outcome"]] else su
    return {"tie_tolerance_k": tol, "steps": steps,
            "paired": sp, "unpaired": su,
            "recorded_outcome": severe["outcome"],
            "recorded_convention": "paired" if severe is sp else "unpaired",
            "note": ("prereg.md §4.1: the recorded G3 outcome is the MORE "
                     "SEVERE of the two SE conventions. Adjacency is "
                     "irrelevant; consecutive ties do not promote TIE to FAIL.")}


# ================================================================ F-A scoring
def fa1(frames, tol=1.0, n=N_DRAW):
    """prereg.md §6.2 F-A1.  Over gate-clearing frames only: L2 is FALSIFIED if
    some pair has V_1 > V_2 and D_1 < D_2 - tol*SE(D_1 - D_2).  Both SE
    conventions are reported; the smaller SE makes falsification EASIER, so
    reporting both is the conservative choice against L2."""
    elig = [f for f in frames if f["gate_cleared"]]
    out = {"n_frames_considered": len(frames), "n_gate_clearing": len(elig),
           "frame_names": [f["name"] for f in elig]}
    if len(elig) < 2:
        out["verdict_unpaired"] = "NOT EVALUABLE -- fewer than two gate-clearing frames"
        out["verdict_paired"] = out["verdict_unpaired"]
        return out
    for conv in ("unpaired", "paired"):
        worst = None
        n_viol = 0
        for f1, f2 in itertools.permutations(elig, 2):
            if not (f1["V"] > f2["V"]):
                continue
            if conv == "unpaired":
                se = float(np.sqrt(f1["sd"] ** 2 / n + f2["sd"] ** 2 / n))
            else:
                v1 = np.array(f1["values"], dtype=np.float64)
                v2 = np.array(f2["values"], dtype=np.float64)
                se = float((v1 - v2).std(ddof=1) / np.sqrt(n))
            margin = ((f2["D"] - f1["D"]) / se) if se > 0 else None
            if margin is None:
                continue
            if worst is None or margin > worst["inversion_in_se"]:
                worst = {"higher_V_frame": f1["name"], "lower_V_frame": f2["name"],
                         "V_high": f1["V"], "V_low": f2["V"],
                         "D_at_high_V": f1["D"], "D_at_low_V": f2["D"],
                         "se": se, "inversion_in_se": margin}
            if margin > tol:
                n_viol += 1
        out[f"largest_inversion_{conv}"] = worst
        out[f"n_violating_pairs_{conv}"] = n_viol
        out[f"verdict_{conv}"] = "FALSIFIED" if n_viol > 0 else "CONSISTENT"
    return out


def fa2(points, band=FA2_BAND):
    """prereg.md §6.2 F-A2.  rho(t) = [D_meas(t)/D_meas(0)] / [D_pred(V(t))/D_pred(V(0))]
    over gate-clearing grid points.  Not falsifying on its own."""
    ref = next((p for p in points if abs(p["t"]) < 1e-12), None)
    if ref is None or not ref["gate_cleared"] or not ref["D_pred"]:
        return {"verdict": "NOT EVALUABLE -- t=0 reference does not clear its gate",
                "points": []}
    rows = []
    for p in points:
        if not p["gate_cleared"] or p["D_pred"] in (None, 0.0):
            continue
        rho = (p["D"] / ref["D"]) / (p["D_pred"] / ref["D_pred"])
        rows.append({"t": p["t"], "novel": p["novel"], "V": p["V"],
                     "D_meas": p["D"], "D_pred": p["D_pred"], "rho": rho,
                     "abs_log2_rho": abs(float(np.log2(abs(rho)))) if rho > 0 else None,
                     "in_band": bool(band[0] <= rho <= band[1])})
    if not rows:
        return {"verdict": "NOT EVALUABLE -- no scored points", "points": []}
    ok = all(r["in_band"] for r in rows)
    return {"band": list(band), "verdict": "CONSISTENT" if ok else "SHAPE-DISTORTED",
            "max_abs_log2_rho": max(r["abs_log2_rho"] for r in rows
                                    if r["abs_log2_rho"] is not None),
            "n_points": len(rows), "points": rows}


# ====================================================================== main
def cpu_seconds():
    a = resource.getrusage(resource.RUSAGE_SELF)
    b = resource.getrusage(resource.RUSAGE_CHILDREN)
    return (a.ru_utime + a.ru_stime + b.ru_utime + b.ru_stime)


def reduction_reproduction(res):
    """THE SEEDS ARE THE CACHE.  Join this run's 32 regenerated reductions to
    the committed metadata of the prior batches by tag and compare.  Pure
    post-processing of recorded values: no lattice is reduced here."""
    for label, path in (("BATCH_436ddd", PRIOR_436), ("BATCH_a51f91", PRIOR_A51)):
        if not os.path.exists(path):
            res["instrument_checks"][f"reduction_reproduction_vs_{label}"] = {
                "status": f"NOT EVALUATED -- {path} not found"}
            print(f"[repro] {label}: NOT EVALUATED, file not found: {path}")
            continue
        pj = {m["tag"]: m for m in json.load(open(path))["reductions"]}
        dev = []
        for m in res["reductions"]:
            if m["tag"] in pj:
                p = pj[m["tag"]]
                dev.append({
                    "tag": m["tag"],
                    "b0_norm_rel_dev": abs(m["b0_norm"] - p["b0_norm"]) / p["b0_norm"],
                    "slope_abs_dev": abs(m["gso_log2_slope_per_index"]
                                         - p["gso_log2_slope_per_index"]),
                })
        blk = {
            "n_compared": len(dev),
            "max_b0_norm_rel_dev": max(x["b0_norm_rel_dev"] for x in dev) if dev else None,
            "max_gso_slope_abs_dev": max(x["slope_abs_dev"] for x in dev) if dev else None,
            "note": ("No .npz reduction cache exists anywhere in the "
                     "repository. THE SEEDS ARE THE CACHE: all 32 reductions "
                     "were regenerated from seed_basis(d,beta,i) at the same "
                     "fpylll version (0.6.4), and this check is what makes "
                     "'the same bases' verified rather than asserted."),
            "per_tag": dev,
        }
        res["instrument_checks"][f"reduction_reproduction_vs_{label}"] = blk
        print(f"[repro] {label}: n={blk['n_compared']} max |b0| rel dev "
              f"{blk['max_b0_norm_rel_dev']}  max slope abs dev "
              f"{blk['max_gso_slope_abs_dev']}")
    return res


def shared_point_reproduction(res):
    """prereg.md §1.1.  The six t shared with BATCH-436ddd must land on the SAME
    paths.  A shared-point difference above 1 x SE_diff is an INSTRUMENT
    DISCREPANCY, not a result.  Pure post-processing of recorded values."""
    if not os.path.exists(PRIOR_436):
        res["reproduction_vs_BATCH_436ddd"] = {
            "status": f"NOT EVALUATED -- {PRIOR_436} not found"}
        print(f"[repro] shared points: NOT EVALUATED, file not found: {PRIOR_436}")
        return res
    pj = json.load(open(PRIOR_436))
    rep = {}
    for ckey, cell in res["cells"].items():
        if ckey not in pj.get("cells", {}):
            continue
        old = pj["cells"][ckey]["sensitivity_demonstration"]["per_t"]
        rows = []
        for t in SHARED_T_436:
            ok = f"{t:.2f}"
            if ok not in old:
                continue
            new = cell["sensitivity_demonstration"]["per_t"][tkey(t)]
            dm = new["ratio_2em10_mean"] - old[ok]["ratio_2em10_mean"]
            se = float(np.sqrt(new["ratio_2em10_sd"] ** 2 / N_DRAW
                               + old[ok]["ratio_2em10_sd"] ** 2 / N_DRAW))
            rows.append({
                "t": t,
                "mean_r_2em10_this_run": new["ratio_2em10_mean"],
                "mean_r_2em10_BATCH_436ddd": old[ok]["ratio_2em10_mean"],
                "difference": dm,
                "se_diff": se,
                "difference_in_se_diff": (dm / se) if se > 0 else (0.0 if dm == 0 else None),
                "bitwise_identical": bool(dm == 0.0),
                "instrument_discrepancy": bool(se > 0 and abs(dm) > se),
            })
        rep[ckey] = {
            "rows": rows,
            "all_bitwise_identical": bool(all(r["bitwise_identical"] for r in rows)),
            "any_instrument_discrepancy":
                bool(any(r["instrument_discrepancy"] for r in rows)),
            "rule": ("prereg.md §1.1: a shared-point difference exceeding "
                     "1 x SE_diff is an INSTRUMENT DISCREPANCY, not a result "
                     "about anything."),
        }
    res["reproduction_vs_BATCH_436ddd"] = rep
    print("[repro] shared points vs BATCH-436ddd: "
          + "  ".join(f"{k}:{'IDENTICAL' if v['all_bitwise_identical'] else 'DIFFERS'}"
                      for k, v in rep.items()))
    return res


def verify_prereg():
    """Load prereg.md READ-ONLY, re-hash, compare against the notarized
    receipt.  ABORT on mismatch (prereg.md §9)."""
    with open(PREREG_PATH, "rb") as f:
        raw = f.read()
    got = hashlib.sha256(raw).hexdigest()
    with open(RECEIPT_PATH, "rb") as f:
        rec = json.load(f)
    want_receipt = rec["archive"]["path_sha256"][PREREG_REL]
    want_field = rec["prereg_sha256"]
    sidecar = os.path.join(os.path.dirname(PREREG_PATH), "prereg_sha256.txt")
    want_sidecar = None
    if os.path.exists(sidecar):
        want_sidecar = open(sidecar).read().split()[0].strip()
    ok = (got == want_receipt == want_field
          and (want_sidecar is None or want_sidecar == got))
    return {
        "prereg_path": PREREG_REL,
        "prereg_bytes": len(raw),
        "recomputed_sha256": got,
        "notarized_receipt_path_sha256": want_receipt,
        "notarized_receipt_prereg_sha256_field": want_field,
        "producer_prereg_sha256_txt": want_sidecar,
        "receipt_task_id": rec["task_id"],
        "receipt_parent_sha": rec["archive"]["parent_sha"],
        "match": bool(ok),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["full", "smoke"], default="full")
    ap.add_argument("--out", default=os.path.join(TASK_DIR, "results.json"))
    ap.add_argument("--tables", default=None)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--core-seconds-budget", type=float, default=3000.0)
    ap.add_argument("--postcheck", metavar="RESULTS_JSON", default=None,
                    help=("Recompute ONLY the two reproduction comparisons from "
                          "an existing results.json and write them back. Pure "
                          "post-processing of values already recorded by the "
                          "measurement run: no lattice is reduced, no error is "
                          "drawn, no arm statistic is recomputed. Exists "
                          "because the first execution carried a wrong relative "
                          "path to the prior batches and silently skipped both "
                          "comparisons."))
    args = ap.parse_args()

    if args.postcheck:
        res = json.load(open(args.postcheck))
        ver = verify_prereg()
        if not ver["match"]:
            print("ABORT: prereg.md sha256 does NOT match the notarized receipt.")
            return 2
        reduction_reproduction(res)
        shared_point_reproduction(res)
        res.setdefault("postcheck", {})["reproduction_blocks_recomputed_utc"] = \
            time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        res["postcheck"]["reason"] = (
            "The measurement execution resolved PRIOR_436/PRIOR_A51 one "
            "directory level too high and silently skipped both reproduction "
            "comparisons. The paths were corrected and the two comparisons "
            "recomputed FROM THE VALUES THIS RUN ALREADY RECORDED. No lattice "
            "was reduced, no error drawn and no arm statistic recomputed; every "
            "measured number in this file is from the single authorised run.")
        with open(args.postcheck, "w") as f:
            json.dump(res, f, indent=1, sort_keys=False)
        if args.tables:
            write_tables(res, args.tables)
        print(f"[postcheck] rewrote {args.postcheck}")
        return 0

    t_start = time.time()
    c_start = cpu_seconds()

    # ------------------------------------------------- GATE: notarized prereg
    ver = verify_prereg()
    print("=" * 78)
    print("NOTARIZED PRE-REGISTRATION VERIFICATION (prereg.md §9)")
    for k, v in ver.items():
        print(f"  {k:38s}: {v}")
    if not ver["match"]:
        print("ABORT: prereg.md sha256 does NOT match the notarized receipt.")
        print("This is a harness failure, not a result. The run does not proceed.")
        return 2
    print("  VERIFIED. The frozen specification is loaded read-only and unmodified.")
    print(f"  grid (13 pts, verbatim): {GRADED_T}")
    print(f"  gate: |D| >= {GATE_K} x SE_diff at {N_DRAW} draws/arm, pooled two-arm SE")
    print(f"  G3: tie-tolerant at {G3_TIE_K} x SE_step, MORE SEVERE of "
          "paired/unpaired, adjacency irrelevant")
    print("  V reported EXACTLY for every frame; floor is a MEASURED bracket")
    print("  FORCED: E[R] = beta/d for EVERY projector. Zero information.")
    print("=" * 78)
    sys.stdout.flush()

    if args.mode == "smoke":
        cells = [(60, 20)]
        ext_d, ext_bkz, ext_betas = [60], 20, [20, 24, 28, 32]
        n_err, chunk = 1 << 14, 1 << 13
    else:
        cells = CELLS
        ext_d, ext_bkz, ext_betas = EXT_D, EXT_BKZ, EXT_BETAS
        n_err, chunk = 1 << 20, 1 << 15

    res = {
        "task_id": "TASK-20260806-ca4377",
        "batch_id": "BATCH-f19c37",
        "goal_id": "GOAL-MLKEM-005",
        "role": "executor",
        "claim_tier": "toy",
        "governed_by": "prereg.md of TASK-20260806-5930ec, notarized by TASK-20260806-53ad5c",
        "prereg_verification": ver,
        "instrument_carried_from": "BATCH-436ddd / TASK-20260806-09ec68 b2a.py",
        "mode": args.mode,
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "read_order": [
            "0. prereg.md loaded read-only, re-hashed, compared to the notarized receipt",
            "1. reductions regenerated FROM SEEDS and verified against BATCH-436ddd/a51f91",
            "2. instrument checks (orthonormality, QR vs fpylll GSO, CBD pmf)",
            "3. GAUSSIAN-ERROR NULL OF THE NULL (instrument check, not a control)",
            "4. Haar null arm; P1/P2 on the null arm FIRST",
            "5. graded family on the 13-point AM-1 grid; G1/G2/G3 tie-tolerant",
            "6. V for every frame; detection floor as a measured bracket",
            "7. real / LLL-only / unreduced arms read only after 5",
            "8. F-A (novel subset scored separately from the reproduction subset)",
            "9. beta-trend and F-B (L1 vs L2)",
        ],
        "config": {"q": Q_MOD, "eta": ETA, "cells": cells, "graded_t": GRADED_T,
                   "ext_d": ext_d, "ext_bkz_blocksize": ext_bkz,
                   "ext_betas": ext_betas, "errors_per_cell": n_err,
                   "draws_per_arm": N_DRAW, "chunk": chunk,
                   "tail_levels": P_TAIL, "gate_k": GATE_K,
                   "g3_tie_tolerance_k": G3_TIE_K,
                   "fa2_band": list(FA2_BAND), "fb_band": FB_BAND,
                   "fb_artifact_tell": FB_ARTIFACT_TELL,
                   "gauss_arms": GAUSS_ARMS},
        "novelty_accounting": {
            "shared_with_BATCH_436ddd": SHARED_T_436,
            "novel_all_cells": NOVEL_ALL_CELLS,
            "novel_except_100_30": NOVEL_EXCEPT_100_30,
            "statement": ("Only the 25-point NOVEL subset is admissible as a "
                          "test of L2. The shared points and the whole beta "
                          "trend are REPRODUCTION, because L2 postdates those "
                          "numbers."),
        },
        "seed_scheme": {
            "fplll_basis_seed": "700000 + d*1000 + beta*10 + i",
            "numpy_cbd_error_seed": "20260805 + d",
            "numpy_haar_seed": "900000 + d*1000 + betap*10 + j",
            "numpy_graded_seed": "500000 + d*1000 + betap*10 + j",
            "numpy_gauss_error_seed": "20260806 + d",
            "note": "THE SEEDS ARE THE CACHE. No .npz reduction cache exists.",
        },
        "instrument_checks": {},
        "reductions": [],
        "cells": {},
        "beta_trend": {},
        "reproduction_vs_BATCH_436ddd": {},
        "timings": {},
    }

    # ------------------------------------------------ stage A: reductions
    jobs = [(d, b, i) for (d, b) in cells for i in range(N_DRAW)]
    print(f"[stage A] {len(jobs)} reductions regenerated FROM SEEDS on "
          f"{args.workers} workers (the seeds are the cache)")
    sys.stdout.flush()
    tA = time.time()
    FR = {}
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for tag, Qr, Ql, Qb, meta in ex.map(reduce_one, jobs):
            FR[tag] = {"unreduced": Qr, "lll_only": Ql, "real_bkz": Qb}
            res["reductions"].append(meta)
            print(f"  {tag}: LLL {meta['lll_seconds']}s BKZ {meta['bkz_seconds']}s "
                  f"||b0||={meta['b0_norm']:.1f}")
            sys.stdout.flush()
    res["timings"]["stage_A_reduction_wall_seconds"] = round(time.time() - tA, 2)
    res["timings"]["stage_A_cpu_seconds"] = round(cpu_seconds() - c_start, 2)
    print(f"[stage A] wall {res['timings']['stage_A_reduction_wall_seconds']}s "
          f"cpu {res['timings']['stage_A_cpu_seconds']}s")

    res["instrument_checks"]["qr_vs_fpylll_gso_max_rel_err"] = max(
        m["instrument_qr_vs_fpylll_gso_max_rel_err"] for m in res["reductions"])
    res["instrument_checks"]["tail_frame_orthonormality_max_abs_dev"] = max(
        m["instrument_Q_orthonormality_max_abs_dev"] for m in res["reductions"])

    reduction_reproduction(res)
    sys.stdout.flush()

    # ------------------------------------------------ stages B/C, per cell
    for (d, beta) in cells:
        key = f"d{d}_b{beta}"
        used = cpu_seconds() - c_start
        if used > args.core_seconds_budget:
            res["aborted_reason"] = (
                f"core-second budget exhausted before {key} "
                "-- INFRASTRUCTURE OUTCOME, never a result (AGENTS.md rule 3)")
            break
        a, b = beta / 2.0, (d - beta) / 2.0
        qb = {p: float(betaincinv(a, b, p)) for p in P_TAIL}
        cell = {"d": d, "beta": beta, "k": d // 2, "q": Q_MOD,
                "forced_values": {
                    "E_R_forced": beta / d,
                    "E_R_forced_label": "FORCED for every projector. ZERO INFORMATION.",
                    "Var_R_under_Beta_derived":
                        2.0 * beta * (d - beta) / (d ** 2 * (d + 2)),
                    "sigma_over_mu_under_Beta": sigma_over_mu(beta, d),
                    "E_V_haar_exact": 2.0 * beta * (d - beta) / (d * (d + 2.0)),
                    "V_coordinate_aligned_exact": beta * (1.0 - beta / d),
                    "beta_params": {"a": a, "b": b},
                    "beta_quantiles": {f"p2em{int(round(-np.log2(p)))}": qb[p]
                                       for p in P_TAIL}},
                "arms_cbd": {}, "arms_gauss": {}, "frame_V": {}}

        frames = {
            "unreduced": [FR[f"{key}_i{j}"]["unreduced"] for j in range(N_DRAW)],
            "lll_only": [FR[f"{key}_i{j}"]["lll_only"] for j in range(N_DRAW)],
            "real_bkz": [FR[f"{key}_i{j}"]["real_bkz"] for j in range(N_DRAW)],
        }
        Qs = {k2: stack(v, beta) for k2, v in frames.items()}
        Qs["haar_null"] = haar_frames(d, beta, N_DRAW)
        paths = graded_paths(d, beta, N_DRAW)      # BEFORE and INDEPENDENT of t
        for t in GRADED_T:
            Qs[arm_t(t)] = graded_frames_from_paths(paths, t)
        del paths

        # V for every frame, exactly, zero error draws
        for nm, QQ in Qs.items():
            cell["frame_V"][nm] = frame_V(QQ, d, beta)

        for law in ("gauss", "cbd"):          # null-of-the-null read FIRST
            tB = time.time()
            if law == "cbd":
                rng = np.random.default_rng(seed_error(d))
                Ef = np.empty((n_err, d), dtype=np.float32)
                n2 = np.empty(n_err, dtype=np.float64)
                hist = np.zeros(5, dtype=np.int64)
                for s0 in range(0, n_err, chunk):
                    s1 = min(n_err, s0 + chunk)
                    Ei = cbd_eta2(rng, s1 - s0, d)
                    hist += np.bincount((Ei.astype(np.int32) + 2).ravel(), minlength=5)
                    n2[s0:s1] = (Ei.astype(np.int32) ** 2).sum(1)
                    Ef[s0:s1] = Ei
                pm = hist / hist.sum()
                res["instrument_checks"][f"cbd_pmf_{key}"] = {
                    "measured": pm.tolist(),
                    "exact_fips203_cbd_eta2": [1/16, 4/16, 6/16, 4/16, 1/16],
                    "measured_per_coordinate_variance":
                        float(sum(pm[i] * (i - 2) ** 2 for i in range(5))),
                    "measured_per_coordinate_fourth_moment":
                        float(sum(pm[i] * (i - 2) ** 4 for i in range(5))),
                    "exact_per_coordinate_variance": 1.0,
                    "exact_per_coordinate_fourth_moment": 2.5}
                names = list(Qs.keys())
            else:
                g = np.random.default_rng(seed_gauss_error(d))
                Ef = np.empty((n_err, d), dtype=np.float32)
                n2 = np.empty(n_err, dtype=np.float64)
                for s0 in range(0, n_err, chunk):
                    s1 = min(n_err, s0 + chunk)
                    Ef[s0:s1] = g.standard_normal((s1 - s0, d))
                    n2[s0:s1] = (Ef[s0:s1].astype(np.float64) ** 2).sum(1)
                names = [nm for nm in GAUSS_ARMS if nm in Qs]
            tgen = time.time() - tB

            store = cell["arms_cbd"] if law == "cbd" else cell["arms_gauss"]
            tP = time.time()
            for nm in names:
                R = project(Ef, n2, Qs[nm], N_DRAW, beta, chunk)
                store[nm] = arm_stats(R, a, b, qb, want_pooled=(law == "cbd"))
                del R
            del Ef, n2
            cell.setdefault("timing_seconds", {})[f"{law}_generate"] = round(tgen, 2)
            cell["timing_seconds"][f"{law}_project_and_stats"] = round(time.time() - tP, 2)

        # -------- null of the null (instrument check, NOT a control)
        gh = cell["arms_gauss"]["haar_null"]
        nn = {"status": ("INSTRUMENT CHECK, NOT A CONTROL. For a rotationally "
                         "invariant error and any fixed rank-beta projector, "
                         "R ~ Beta(beta/2,(d-beta)/2) exactly, so this cannot "
                         "fail unless the code is wrong."),
              "tolerances": {"p2em10": 0.05, "p2em16": 0.10}, "arms": {}}
        for nm, arm in cell["arms_gauss"].items():
            r10 = arm["ratio_p2em10_over_draws"]["mean"]
            r16 = arm["ratio_p2em16_over_draws"]["mean"]
            nn["arms"][nm] = {
                "ratio_2em10_mean_over_draws": r10,
                "ratio_2em16_mean_over_draws": r16,
                "dev_2em10": abs(r10 - 1.0), "dev_2em16": abs(r16 - 1.0),
                "N1_pass": bool(abs(r10 - 1.0) <= 0.05 and abs(r16 - 1.0) <= 0.10),
                "gate_vs_gauss_haar": gate(arm, gh)}
        nn["N1_all_arms_pass"] = bool(all(v["N1_pass"] for v in nn["arms"].values()))
        c0 = arm_t(0.0)
        nn["N2_coord_gate_does_not_clear"] = (
            bool(not nn["arms"][c0]["gate_vs_gauss_haar"]["cleared"])
            if c0 in nn["arms"] else None)
        nn["verdict"] = ("PASS" if (nn["N1_all_arms_pass"] and
                                    nn["N2_coord_gate_does_not_clear"])
                         else "FAIL -- INSTRUMENT ERROR, not a result")
        cell["null_of_the_null"] = nn
        print(f"  [null-of-null]  {key} N1={nn['N1_all_arms_pass']} "
              f"N2={nn['N2_coord_gate_does_not_clear']} -> {nn['verdict']}")

        # -------- null arm first
        def verdict(arm):
            r10 = arm["pooled"]["p2em10"]["ratio"]
            r16 = arm["pooled"]["p2em16"]["ratio"]
            bf = arm["variance_decomposition"]["between_fraction_raw"]
            return {"P1": {"ratio_2em10_pooled": r10, "dev_2em10": abs(r10 - 1.0),
                           "ratio_2em16_pooled": r16, "dev_2em16": abs(r16 - 1.0),
                           "pass_2em10": bool(abs(r10 - 1.0) <= 0.05),
                           "pass_2em16": bool(abs(r16 - 1.0) <= 0.10),
                           "pass": bool(abs(r10 - 1.0) <= 0.05
                                        and abs(r16 - 1.0) <= 0.10)},
                    "P2": {"between_fraction": bf,
                           "pass": bool(bf is not None and bf <= 0.20)}}

        hcbd = cell["arms_cbd"]["haar_null"]
        cell["verdict_on_the_null_arm_FIRST"] = verdict(hcbd)
        cell["P1_P2_status"] = ("Reported. NOT an adjudicating predicate: "
                                "DEC-20260806-00deff AM-2 records that P1/P2 "
                                "return identical verdicts on the Haar null arm "
                                "and the real arm in all four cells.")
        print(f"  [null-arm-first] {key} haar_null "
              f"P1={cell['verdict_on_the_null_arm_FIRST']['P1']['pass']} "
              f"P2={cell['verdict_on_the_null_arm_FIRST']['P2']['pass']}")

        # -------- the graded family on the 13-point AM-1 grid
        gr = {}
        for t in GRADED_T:
            nm = arm_t(t)
            arm = cell["arms_cbd"][nm]
            g_ = gate(arm, hcbd)
            Vd = cell["frame_V"][nm]
            dp = d_pred_from_V(Vd["mean"], d, beta)
            gr[tkey(t)] = {
                "t": t,
                "novel": bool(is_novel(d, beta, t)),
                "shared_with_BATCH_436ddd":
                    bool(any(abs(t - x) < 1e-12 for x in SHARED_T_436)),
                "ratio_2em10_mean": arm["ratio_p2em10_over_draws"]["mean"],
                "ratio_2em10_sd": arm["ratio_p2em10_over_draws"]["sd"],
                "ratio_2em10_values": arm["ratio_p2em10_over_draws"]["values"],
                "ratio_2em16_mean": arm["ratio_p2em16_over_draws"]["mean"],
                "V": Vd, "L2_prediction": dp, "gate": g_}
        means = [gr[tkey(t)]["ratio_2em10_mean"] for t in GRADED_T]
        sds = [gr[tkey(t)]["ratio_2em10_sd"] for t in GRADED_T]
        vals = [gr[tkey(t)]["ratio_2em10_values"] for t in GRADED_T]
        G3 = g3_scores(means, vals, sds)
        G1 = gr[tkey(0.0)]["gate"]["cleared"]
        G2 = not gr[tkey(1.0)]["gate"]["cleared"]
        se0 = gr[tkey(0.0)]["gate"]["se_of_difference"]

        if not G1 or not G2:
            cverdict = "INVALID"
        elif G3["recorded_outcome"] == "PASS":
            cverdict = "VALID"
        elif G3["recorded_outcome"] == "TIE":
            cverdict = "PARTIAL"
        else:
            cverdict = "INVALID"

        # detection floor: measured bracket in V units (prereg §5.1b)
        clearing = [gr[tkey(t)] for t in GRADED_T if gr[tkey(t)]["gate"]["cleared"]]
        not_clearing = [gr[tkey(t)] for t in GRADED_T
                        if not gr[tkey(t)]["gate"]["cleared"]]
        vmax_nc = max((p["V"]["mean"] for p in not_clearing), default=None)
        vmin_c = min((p["V"]["mean"] for p in clearing), default=None)
        floor = {
            "unit": "V = sum_a P_aa^2 - beta^2/d, deterministic, zero error draws",
            "largest_V_not_clearing": vmax_nc,
            "largest_V_not_clearing_t": next(
                (p["t"] for p in not_clearing if p["V"]["mean"] == vmax_nc), None),
            "smallest_V_clearing": vmin_c,
            "smallest_V_clearing_t": next(
                (p["t"] for p in clearing if p["V"]["mean"] == vmin_c), None),
            "bracket": [vmax_nc, vmin_c] if (vmax_nc is not None and vmin_c is not None) else None,
            "midpoint_estimate": ((vmax_nc + vmin_c) / 2.0)
            if (vmax_nc is not None and vmin_c is not None) else None,
            "in_statistic_units": f"{GATE_K} x SE_diff, per arm, at {N_DRAW} draws",
            "note": ("Every non-clearing arm is reported as "
                     "|D| < 4.0 x SE_diff = <number>, an upper bound at 8 draws."),
        }

        sens = {
            "family": "Q_t = QR( sqrt(1-t)*E_S + sqrt(t)*G ), (S_j,G_j) drawn "
                      "from seed_graded BEFORE and INDEPENDENTLY of the t list",
            "t_values": GRADED_T,
            "per_t": gr,
            "G1_high_end_t0_gate_clears": bool(G1),
            "G2_low_end_t1_gate_does_not_clear": bool(G2),
            "G3_tie_tolerant": G3,
            "dynamic_range_abs": means[0] - means[-1],
            "dynamic_range_in_se_of_difference_at_t0":
                (means[0] - means[-1]) / se0 if se0 > 0 else None,
            "cell_verdict": cverdict,
            "detection_floor": floor,
        }
        cell["sensitivity_demonstration"] = sens
        print(f"  [graded]        {key} G1={G1} G2={G2} "
              f"G3={G3['recorded_outcome']}({G3['recorded_convention']}) "
              f"-> {cverdict}  t0 {gr[tkey(0.0)]['gate']['shift_in_units_of_se_of_difference']:.2f} SE"
              f"  t1 {gr[tkey(1.0)]['gate']['shift_in_units_of_se_of_difference']:.2f} SE"
              f"  floor V in [{vmax_nc}, {vmin_c}]")
        print(f"                  G3 paired={G3['paired']['outcome']} "
              f"(max {G3['paired']['max_increase_in_se']:.3f} SE)  "
              f"unpaired={G3['unpaired']['outcome']} "
              f"(max {G3['unpaired']['max_increase_in_se']:.3f} SE)")

        # -------- only now: the real / lll / unreduced arms
        cell["verdicts_after_the_demonstration"] = {
            nm: verdict(cell["arms_cbd"][nm])
            for nm in ("real_bkz", "lll_only", "unreduced")}
        cell["gates_vs_haar_null"] = {
            nm: gate(cell["arms_cbd"][nm], hcbd)
            for nm in ("real_bkz", "lll_only", "unreduced", arm_t(0.0))}
        cell["L2_prediction_real_arms"] = {
            nm: d_pred_from_V(cell["frame_V"][nm]["mean"], d, beta)
            for nm in ("real_bkz", "lll_only", "unreduced")}
        for nm in ("real_bkz", "lll_only", "unreduced"):
            v = cell["verdicts_after_the_demonstration"][nm]
            g_ = cell["gates_vs_haar_null"][nm]
            print(f"  [{nm:>10}]   {key} r10={v['P1']['ratio_2em10_pooled']:.5f} "
                  f"shift={g_['shift_in_units_of_se_of_difference']:.2f} SE "
                  f"gate={g_['cleared']} V={cell['frame_V'][nm]['mean']:.4f} "
                  f"(E[V]_haar={cell['frame_V'][nm]['E_V_haar_exact']:.4f})")

        # -------- F-A: L2 on the graded path + the real arms
        fa_frames = []
        for t in GRADED_T:
            p = gr[tkey(t)]
            fa_frames.append({
                "name": f"graded_t={t}", "kind": "graded", "t": t,
                "novel": p["novel"], "V": p["V"]["mean"],
                "D": p["gate"]["shift_arm_minus_haar"],
                "sd": p["ratio_2em10_sd"], "values": p["ratio_2em10_values"],
                "gate_cleared": p["gate"]["cleared"],
                "D_pred": p["L2_prediction"]["D_pred"]})
        for nm in ("unreduced", "lll_only", "real_bkz"):
            g_ = cell["gates_vs_haar_null"][nm]
            fa_frames.append({
                "name": nm, "kind": "lattice", "t": None, "novel": False,
                "V": cell["frame_V"][nm]["mean"],
                "D": g_["shift_arm_minus_haar"],
                "sd": cell["arms_cbd"][nm]["ratio_p2em10_over_draws"]["sd"],
                "values": cell["arms_cbd"][nm]["ratio_p2em10_over_draws"]["values"],
                "gate_cleared": g_["cleared"],
                "D_pred": cell["L2_prediction_real_arms"][nm]["D_pred"]})
        novel_frames = [f for f in fa_frames if f["novel"]]
        cell["F_A"] = {
            "scope": ("Frames at this cell's (d, beta): the 13 graded grid "
                      "points plus unreduced / lll_only / real_bkz. The "
                      "beta-trend frames are scored in F-B."),
            "F_A1_all_points": fa1(fa_frames),
            "F_A1_novel_subset_only": fa1(novel_frames),
            "F_A2_all_points": fa2([f for f in fa_frames if f["kind"] == "graded"]),
            "F_A2_novel_subset_only": fa2(
                [f for f in fa_frames if f["kind"] == "graded" and
                 (f["novel"] or abs(f["t"]) < 1e-12)]),
            "F_A3_magnitude_diagnostic_only": [
                {"name": f["name"], "V": f["V"], "D_meas": f["D"],
                 "D_pred": f["D_pred"],
                 "ratio_meas_over_pred": (f["D"] / f["D_pred"])
                 if f["D_pred"] not in (None, 0.0) else None,
                 "gate_cleared": f["gate_cleared"], "novel": f["novel"]}
                for f in fa_frames],
            "admissibility": ("Only the NOVEL-subset result is admissible as a "
                              "test of L2. The all-points result is a "
                              "reproduction check, because L2 was formulated "
                              "after the shared points were measured."),
        }
        print(f"  [F-A]           {key} novel-only F-A1 "
              f"unpaired={cell['F_A']['F_A1_novel_subset_only'].get('verdict_unpaired')} "
              f"paired={cell['F_A']['F_A1_novel_subset_only'].get('verdict_paired')} | "
              f"all-points F-A1 unpaired={cell['F_A']['F_A1_all_points'].get('verdict_unpaired')} "
              f"| F-A2 novel={cell['F_A']['F_A2_novel_subset_only'].get('verdict')}")
        sys.stdout.flush()
        res["cells"][key] = cell
        del Qs, frames

    shared_point_reproduction(res)
    sys.stdout.flush()

    # ------------------------------------------------ stage D: beta trend
    b_lo, b_hi = ext_betas[0], ext_betas[-1]
    for d in ext_d:
        key = f"d{d}_b{ext_bkz}"
        if f"{key}_i0" not in FR:
            continue
        used = cpu_seconds() - c_start
        if used > args.core_seconds_budget:
            res.setdefault("aborted_reason",
                           f"core-second budget exhausted before beta-trend d={d} "
                           "-- INFRASTRUCTURE OUTCOME, never a result")
            break
        rng = np.random.default_rng(seed_error(d))
        Ef = np.empty((n_err, d), dtype=np.float32)
        n2 = np.empty(n_err, dtype=np.float64)
        for s0 in range(0, n_err, chunk):
            s1 = min(n_err, s0 + chunk)
            Ei = cbd_eta2(rng, s1 - s0, d)
            n2[s0:s1] = (Ei.astype(np.int32) ** 2).sum(1)
            Ef[s0:s1] = Ei
        tr = {}
        rb = f"real_bkz{ext_bkz}"
        for bp in ext_betas:
            aa, bb = bp / 2.0, (d - bp) / 2.0
            qbp = {p: float(betaincinv(aa, bb, p)) for p in P_TAIL}
            Q = {"unreduced": stack([FR[f"{key}_i{j}"]["unreduced"] for j in range(N_DRAW)], bp),
                 "lll_only": stack([FR[f"{key}_i{j}"]["lll_only"] for j in range(N_DRAW)], bp),
                 rb: stack([FR[f"{key}_i{j}"]["real_bkz"] for j in range(N_DRAW)], bp),
                 "haar_null": haar_frames(d, bp, N_DRAW),
                 "coord_t0": graded_frames_from_paths(graded_paths(d, bp, N_DRAW), 0.0)}
            Vs = {nm: frame_V(QQ, d, bp) for nm, QQ in Q.items()}
            arms = {}
            for nm, QQ in Q.items():
                R = project(Ef, n2, QQ, N_DRAW, bp, chunk)
                arms[nm] = arm_stats(R, aa, bb, qbp, want_pooled=False)
                del R
            hh = arms["haar_null"]
            tr[str(bp)] = {
                "beta": bp, "d": d,
                "sigma_over_mu_under_Beta": sigma_over_mu(bp, d),
                "arms": {nm: {"ratio_2em10_mean": arms[nm]["ratio_p2em10_over_draws"]["mean"],
                              "ratio_2em10_sd": arms[nm]["ratio_p2em10_over_draws"]["sd"],
                              "V": Vs[nm],
                              "L2_prediction": d_pred_from_V(Vs[nm]["mean"], d, bp),
                              "gate_vs_haar": gate(arms[nm], hh)}
                         for nm in Q}}
            print(f"  [beta-trend] d={d} beta={bp}: " + "  ".join(
                f"{nm}={tr[str(bp)]['arms'][nm]['ratio_2em10_mean']:.5f}"
                f"(V={Vs[nm]['mean']:.3f})" for nm in Q))
            sys.stdout.flush()
        del Ef, n2

        # F-B: adjudicate L1 and L2 (prereg.md §6.3)
        s_lo = sigma_over_mu(b_lo, d)
        fal = {}
        for nm in ("unreduced", "lll_only", rb, "coord_t0"):
            glo = tr[str(b_lo)]["arms"][nm]["gate_vs_haar"]
            D = {str(bp): tr[str(bp)]["arms"][nm]["gate_vs_haar"]["shift_arm_minus_haar"]
                 for bp in ext_betas}
            pred_l1 = {str(bp): sigma_over_mu(bp, d) / s_lo for bp in ext_betas}
            dp = {str(bp): tr[str(bp)]["arms"][nm]["L2_prediction"]["D_pred"]
                  for bp in ext_betas}
            r_l1 = pred_l1[str(b_hi)]
            r_l2 = (dp[str(b_hi)] / dp[str(b_lo)]) if dp[str(b_lo)] else None
            entry = {"beta_lo": b_lo, "beta_hi": b_hi,
                     "departure_D_by_beta": D,
                     "V_by_beta": {str(bp): tr[str(bp)]["arms"][nm]["V"]["mean"]
                                   for bp in ext_betas},
                     "L2_D_pred_by_beta": dp,
                     "L1_predicted_ratio_to_beta_lo": pred_l1,
                     "ratio_L1": r_l1, "ratio_L2": r_l2,
                     "Dlo_gate_cleared": glo["cleared"],
                     "Dlo_shift_in_se": glo["shift_in_units_of_se_of_difference"],
                     "Dlo_upper_bound_if_not_cleared":
                         None if glo["cleared"] else glo["upper_bound_statement_if_not_cleared"],
                     "discriminating":
                         (nm != "coord_t0")}
            if not glo["cleared"]:
                entry["ratio_meas"] = None
                entry["L1_verdict"] = (f"NOT APPLICABLE -- D(beta={b_lo}) does not clear "
                                       "its own 4.0 x SE_diff gate; reported as an "
                                       "upper bound at the floor")
                entry["L2_verdict"] = entry["L1_verdict"]
            else:
                ratio = D[str(b_hi)] / D[str(b_lo)]
                entry["ratio_meas"] = ratio
                in_l1 = abs(ratio - r_l1) <= FB_BAND * abs(r_l1)
                in_l2 = (r_l2 is not None and abs(ratio - r_l2) <= FB_BAND * abs(r_l2))
                if in_l1 and in_l2:
                    lv, l2v = "NOT DISCRIMINATING", "NOT DISCRIMINATING"
                elif in_l1 and not in_l2:
                    lv, l2v = "CONSISTENT", "FALSIFIED"
                elif in_l2 and not in_l1:
                    lv, l2v = "FALSIFIED", "CONSISTENT"
                else:
                    lv, l2v = "FALSIFIED", "FALSIFIED"
                if ratio >= FB_ARTIFACT_TELL and r_l1 <= 0.7:
                    lv = ("FALSIFIED -- the departure fails to decay when the "
                          "parameter meant to destroy it doubles (artifact tell)")
                entry["in_L1_band"] = bool(in_l1)
                entry["in_L2_band"] = bool(in_l2)
                entry["L1_verdict"] = lv
                entry["L2_verdict"] = l2v
                if nm == "coord_t0":
                    entry["L1_verdict"] = "NOT DISCRIMINATING (arm, by prereg §6.3)"
                    entry["L2_verdict"] = "NOT DISCRIMINATING (arm, by prereg §6.3)"
                    entry["raw_L1_verdict_had_the_arm_discriminated"] = lv
                    entry["raw_L2_verdict_had_the_arm_discriminated"] = l2v
                entry["L1_L2_separation"] = (abs(r_l1 - r_l2) / abs(r_l1)) if r_l2 else None
            fal[nm] = entry
            print(f"  [F-B] d={d} {nm}: L1={entry['L1_verdict']} | L2={entry['L2_verdict']}"
                  + (f"  meas={entry['ratio_meas']:.4f} L1={r_l1:.4f} "
                     f"L2={r_l2:.4f}" if entry.get("ratio_meas") is not None
                     and r_l2 is not None else ""))
        res["beta_trend"][f"d{d}"] = {
            "reduction_held_fixed_at": f"LLL + BKZ-{ext_bkz}",
            "basis_set_note": ("The beta trend reads seed_basis(d, 40, i) "
                               "because the reduction is held at BKZ-40. Its "
                               "beta=30 row is therefore a DIFFERENT BASIS SET "
                               "from the (d, 30) cell tables, and its D(30) is "
                               "NOT the cell-table headline."),
            "novelty": ("F-B is a REPRODUCTION. These arms were all measured in "
                        "BATCH-436ddd and L2 was formulated after those "
                        "measurements were seen. F-B tests reproducibility and "
                        "L1 (genuinely pre-registered), and does NOT constitute "
                        "an independent test of L2."),
            "by_beta": tr, "falsifier": fal}
        sys.stdout.flush()

    # ------------------------------------------------ close out
    res["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    res["timings"]["total_wall_seconds"] = round(time.time() - t_start, 2)
    res["timings"]["total_cpu_core_seconds"] = round(cpu_seconds() - c_start, 2)
    res["timings"]["core_seconds_budget"] = args.core_seconds_budget
    res["timings"]["core_seconds_budget_exhausted"] = bool(
        (cpu_seconds() - c_start) > args.core_seconds_budget)
    res["peak_rss_gb"] = round(
        resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024.0 ** 2), 3)
    res["peak_rss_children_gb"] = round(
        resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / (1024.0 ** 2), 3)
    res["environment"] = {
        "python": sys.version, "platform": platform.platform(),
        "numpy": np.__version__, "scipy": __import__("scipy").__version__}
    try:
        import fpylll
        res["environment"]["fpylll"] = fpylll.__version__
    except Exception:
        pass
    try:
        res["environment"]["git_commit"] = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=TASK_DIR).decode().strip()
        res["environment"]["git_branch"] = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=TASK_DIR).decode().strip()
        res["environment"]["git_dirty"] = bool(subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=TASK_DIR).decode().strip())
    except Exception:
        pass

    with open(args.out, "w") as f:
        json.dump(res, f, indent=1, sort_keys=False)
    if args.tables:
        write_tables(res, args.tables)
    print(f"[done] {args.out} wall={res['timings']['total_wall_seconds']}s "
          f"cpu={res['timings']['total_cpu_core_seconds']}s "
          f"rss={res['peak_rss_gb']}GB")
    return 0


# ================================================== markdown table generation
def write_tables(res, path):
    L = []
    A = L.append
    A("## graded family, 13 AM-1 grid points, per cell\n")
    for ck, c in res["cells"].items():
        s = c["sensitivity_demonstration"]
        A(f"\n### {ck}  (E[V]_haar = {c['forced_values']['E_V_haar_exact']:.6f}, "
          f"V_coord_aligned = {c['forced_values']['V_coordinate_aligned_exact']:.4f})\n")
        A("| t | novel | mean r(2^-10) | sd | shift D | shift/SE_diff | gate | "
          "V (mean) | V excess | D_pred(V) |")
        A("|---|---|---|---|---|---|---|---|---|---|")
        for t in res["config"]["graded_t"]:
            p = s["per_t"][f"{t:.4f}"]
            g = p["gate"]
            dp = p["L2_prediction"]["D_pred"]
            A(f"| {t} | {'NOVEL' if p['novel'] else 'repro' if p['shared_with_BATCH_436ddd'] else 'probe'} "
              f"| {p['ratio_2em10_mean']:.6f} | {p['ratio_2em10_sd']:.6f} "
              f"| {g['shift_arm_minus_haar']:+.6f} | {g['shift_in_units_of_se_of_difference']:+.2f} "
              f"| {'CLEARS' if g['cleared'] else 'no'} | {p['V']['mean']:.4f} "
              f"| {p['V']['excess_over_E_V_haar']:+.4f} | {dp:.6f} |")
        g3 = s["G3_tie_tolerant"]
        A(f"\nG1 = {s['G1_high_end_t0_gate_clears']}, G2 = {s['G2_low_end_t1_gate_does_not_clear']}, "
          f"G3 paired = {g3['paired']['outcome']} (max +{g3['paired']['max_increase_in_se']:.3f} SE_step, "
          f"{g3['paired']['n_increases']} increases), "
          f"G3 unpaired = {g3['unpaired']['outcome']} (max +{g3['unpaired']['max_increase_in_se']:.3f} SE_step), "
          f"RECORDED = {g3['recorded_outcome']} ({g3['recorded_convention']}) -> **{s['cell_verdict']}**")
        A(f"\nDR = {s['dynamic_range_abs']:.6f} = {s['dynamic_range_in_se_of_difference_at_t0']:.2f} SE_diff(t=0)")
        f = s["detection_floor"]
        A(f"\nfloor bracket: V in [{f['largest_V_not_clearing']}, {f['smallest_V_clearing']}] "
          f"(t = {f['largest_V_not_clearing_t']} -> {f['smallest_V_clearing_t']}), "
          f"midpoint {f['midpoint_estimate']}")
        A("\n#### G3 steps\n")
        A("| step | t_i -> t_i+1 | Delta | SE_paired | Delta/SE_p | SE_unpaired | Delta/SE_u |")
        A("|---|---|---|---|---|---|---|")
        tg = res["config"]["graded_t"]
        for st in g3["steps"]:
            i = st["i"]
            A(f"| {i} | {tg[i]} -> {tg[i+1]} | {st['delta']:+.6f} | {st['se_step_paired']:.6f} "
              f"| {st['delta_in_se_paired']:+.3f} | {st['se_step_unpaired']:.6f} "
              f"| {st['delta_in_se_unpaired']:+.3f} |")
        A("\n#### lattice arms\n")
        A("| arm | pooled r(2^-10) | shift D | shift/SE_diff | gate | upper bound if not cleared | V | V excess | V excess / sd(mean) | D_pred(V) |")
        A("|---|---|---|---|---|---|---|---|---|---|")
        for nm in ("unreduced", "lll_only", "real_bkz"):
            g = c["gates_vs_haar_null"][nm]
            v = c["frame_V"][nm]
            vv = c["verdicts_after_the_demonstration"][nm]
            dp = c["L2_prediction_real_arms"][nm]["D_pred"]
            A(f"| {nm} | {vv['P1']['ratio_2em10_pooled']:.6f} | {g['shift_arm_minus_haar']:+.6f} "
              f"| {g['shift_in_units_of_se_of_difference']:+.2f} | {'CLEARS' if g['cleared'] else 'no'} "
              f"| {'--' if g['cleared'] else g['upper_bound_statement_if_not_cleared']} "
              f"| {v['mean']:.4f} | {v['excess_over_E_V_haar']:+.4f} "
              f"| {v['excess_in_sd_of_mean']:+.1f} | {dp:.6f} |")
        A("\n#### F-A\n")
        fa = c["F_A"]
        for lbl in ("F_A1_all_points", "F_A1_novel_subset_only"):
            e = fa[lbl]
            A(f"* `{lbl}`: n_clearing={e.get('n_gate_clearing')} "
              f"unpaired={e.get('verdict_unpaired')} paired={e.get('verdict_paired')} "
              f"largest inversion (unpaired) = "
              f"{(e.get('largest_inversion_unpaired') or {}).get('inversion_in_se')}")
        for lbl in ("F_A2_all_points", "F_A2_novel_subset_only"):
            e = fa[lbl]
            A(f"* `{lbl}`: {e.get('verdict')} max|log2 rho| = {e.get('max_abs_log2_rho')} "
              f"over {e.get('n_points')} points")
    A("\n## reproduction vs BATCH-436ddd at the six shared t\n")
    for ck, r in res.get("reproduction_vs_BATCH_436ddd", {}).items():
        A(f"\n**{ck}** all_bitwise_identical = {r['all_bitwise_identical']}, "
          f"any_instrument_discrepancy = {r['any_instrument_discrepancy']}\n")
        A("| t | this run | BATCH-436ddd | diff | diff/SE_diff |")
        A("|---|---|---|---|---|")
        for row in r["rows"]:
            A(f"| {row['t']} | {row['mean_r_2em10_this_run']:.8f} "
              f"| {row['mean_r_2em10_BATCH_436ddd']:.8f} | {row['difference']:+.2e} "
              f"| {row['difference_in_se_diff']} |")
    A("\n## beta trend (F-B)\n")
    for dk, bt in res.get("beta_trend", {}).items():
        A(f"\n### {dk} — reduction held at {bt['reduction_held_fixed_at']}\n")
        ebs = [str(x) for x in res["config"]["ext_betas"]]
        A("| arm | " + " | ".join(f"D({b})" for b in ebs)
          + f" | V({ebs[0]}) | V({ebs[-1]}) | ratio_meas | ratio_L1 | ratio_L2 | L1 | L2 |")
        A("|---|" + "---|" * (len(ebs) + 6))
        for nm, e in bt["falsifier"].items():
            D = e["departure_D_by_beta"]
            V = e["V_by_beta"]
            rm = e.get("ratio_meas")
            A(f"| {nm} | " + " | ".join(f"{D[b]:+.6f}" for b in ebs)
              + f" | {V[ebs[0]]:.3f} | {V[ebs[-1]]:.3f} "
              f"| {('%.4f' % rm) if rm is not None else 'n/a'} "
              f"| {e['ratio_L1']:.4f} | {('%.4f' % e['ratio_L2']) if e['ratio_L2'] else 'n/a'} "
              f"| {e['L1_verdict']} | {e['L2_verdict']} |")
        A("\nper-beta gate detail:\n")
        A("| beta | arm | mean r | shift/SE | gate | V | D_pred(V) |")
        A("|---|---|---|---|---|---|---|")
        for bkey, row in bt["by_beta"].items():
            for nm, arm in row["arms"].items():
                g = arm["gate_vs_haar"]
                A(f"| {bkey} | {nm} | {arm['ratio_2em10_mean']:.6f} "
                  f"| {g['shift_in_units_of_se_of_difference']:+.2f} "
                  f"| {'CLEARS' if g['cleared'] else 'no'} | {arm['V']['mean']:.3f} "
                  f"| {arm['L2_prediction']['D_pred']:.6f} |")
    with open(path, "w") as f:
        f.write("\n".join(L) + "\n")
    print(f"[tables] {path}")


if __name__ == "__main__":
    sys.exit(main())
