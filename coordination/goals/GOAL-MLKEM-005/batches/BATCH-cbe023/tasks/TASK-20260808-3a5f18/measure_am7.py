#!/usr/bin/env python3
"""
TASK-20260808-3a5f18 / BATCH-cbe023 / GOAL-MLKEM-005
SECTION C of the notarized pre-registration -- AM-7: the matched-`V`
cross-family comparison REBUILT with an SE that contains the variance the
superseded instrument omitted.

Governed by, and NOT modified by, this file:
  coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/tasks/
      TASK-20260808-35efa3/prereg.md
  sha256 2da554914e5d78146c1e6cafcdbd109aacbc1a1624ed1f8e94ae769f757fc4f8
  notarized by TASK-20260808-e725b4 in commit 4f7c63703..., asserted here to
  be an ancestor of HEAD -- the NOTARIZING COMMIT ITSELF, not its parent
  (prereg.md 0.3 / correction V-7).

This script loads that file READ-ONLY, re-hashes it, compares against the
notarized receipt, the producer sidecar and the blob inside the notarizing
commit, and ABORTS on mismatch.  It re-derives none of its thresholds.

WHAT IS REBUILT (prereg.md 4.2, 4.3, 4.5, 4.6, 4.7):
  * TL supports AND pairings are drawn AFRESH per index from
    default_rng([5, d, beta, s]) -- the superseded vmatch.py's `tl_frame` was
    deterministic on ONE fixed support, so all 8 TL draws shared it.
  * E = 4 INDEPENDENT ERROR POOLS per cell, so `D` is no longer one order
    statistic of a single shared pool.
  * The SE comes from a two-way random-effects decomposition over
    S = 8 supports x E = 4 pools, with Satterthwaite nu_eff, and all three
    variance components are MANDATORY REPORTING.
  * THREE nulls (N-A TL vs TL'', N-B GR vs permuted GR, N-C Gaussian errors),
    replicated in 5 disjoint pool-quadruple clusters, to ESTIMATE a
    false-falsification rate with a Wilson interval AND a cluster bootstrap.
  * A relative-effect floor tau_rel = 0.15, above the null's own median.
  * A delta_min POSITIVE CONTROL at EVERY target with the frozen
    delta = 0.50 admissibility clause.

BINDING CARRY (prereg.md 4.1, 1.3.2): BATCH-a44d08's Section C verdict is VOID
IN BOTH DIRECTIONS.  It is not cited, not reproduced as a baseline, and not
used as a prior anywhere in this script or its output.  Its non-firing pairs'
detection floors do not exist here.  This run REBUILDS THE INSTRUMENT.

BOUNDARY CARRY (prereg.md 4.1): Var(e^T P e) = 2 beta + (mu_4 - 3)(V +
beta^2/d) IS a function of `V` alone, so L2's derivation is correct AT SECOND
ORDER and nothing here touches it.  What is open is only whether the 2^-10
tail quantile inherits that.

Observations only.  No status change, no hypothesis movement, no evidence
record, no interpretation beyond the declared verdicts of prereg.md 4.4/4.6/4.7.
Claim tier TOY: nothing here bears on ML-KEM security, on any FIPS 203
parameter set, on any attack cost, or on any cost model.  V, m3 and D are
properties of a basis PRESENTATION, not of a lattice, and no verdict here is
offered as an AM-4 adjudicator.
certificate.kind: none -- no discrete-log solve and no factor-base relation is
claimed or produced.

This script performs no git write, makes no commit, and writes exactly one
file, inside its own task directory: results_am7.json.
"""

import os

# Budget discipline: the host is shared and heavily loaded.  Pin every BLAS
# backend to a single thread BEFORE numpy is imported.
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS",
           "ACCELERATE_MAX_THREADS"):
    os.environ[_v] = "1"

import argparse
import hashlib
import json
import platform
import resource
import subprocess
import sys
import time

import numpy as np
from scipy.special import betaincinv
from scipy.stats import t as student_t

TASK_DIR = os.path.dirname(os.path.abspath(__file__))
TASKS_DIR = os.path.normpath(os.path.join(TASK_DIR, ".."))
BATCH_DIR = os.path.normpath(os.path.join(TASKS_DIR, ".."))
BATCHES_DIR = os.path.normpath(os.path.join(BATCH_DIR, ".."))
REPO_ROOT = os.path.normpath(os.path.join(BATCHES_DIR, "..", "..", "..", ".."))

PREREG_PATH = os.path.join(TASKS_DIR, "TASK-20260808-35efa3", "prereg.md")
PREREG_SIDECAR = os.path.join(TASKS_DIR, "TASK-20260808-35efa3",
                              "prereg_sha256.txt")
RECEIPT_PATH = os.path.join(BATCH_DIR, "archives", "TASK-20260808-e725b4",
                            "snapshot-receipt.json")
PREREG_REL = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/tasks/"
              "TASK-20260808-35efa3/prereg.md")
NOTARIZING_COMMIT = "4f7c63703"
EXPECTED_PREREG_SHA256 = (
    "2da554914e5d78146c1e6cafcdbd109aacbc1a1624ed1f8e94ae769f757fc4f8")

COMMITTED_F19 = os.path.join(
    BATCHES_DIR, "BATCH-f19c37", "tasks", "TASK-20260806-ca4377",
    "results.json")

# ------------------------------------------------------- carried constants
Q_MOD = 3329                                     # [carried]
CELLS = [(100, 30), (100, 40), (140, 30), (140, 40)]      # [carried]
N_DRAW = 8                                       # [carried] S = 8 supports
N_ERR = 1 << 20                                  # [carried] N = 2^20
CHUNK = 1 << 15                                  # [carried] committed chunking
P_TAIL = 2.0 ** -10                              # [carried]
BETA_MAX = 60                                    # [carried] tail slice width
GRADED_T = [0.0, 0.0025, 0.005, 0.0075, 0.01, 0.015, 0.02, 0.03,
            0.05, 0.1, 0.25, 0.5, 1.0]           # [carried] AM-1 13-point grid
ORDER_IDX = max(1, min(N_ERR, int(round(P_TAIL * N_ERR)))) - 1   # 1023

# --------------------------------- SECTION C constants, prereg.md 4, FROZEN
N_POOL = 4                     # 4.3   E = 4 independent error pools per cell
V_MATCH_TOL = 1e-9             # 4.2
DEGEN_TOL = 1e-9               # 4.4
TAU_REL = 0.15                 # 4.4   relative-effect floor
M3_SEPARATION = 0.10           # 4.4   [carried] informativeness
SUGGESTIVE_FRAC = 0.8          # 4.4   |t| in [0.8 tcrit, tcrit)
FAMILY_ALPHA = 0.10            # 4.4   family-wise level
NC_DECLARED = 11               # 4.4   8 graded + 3 unreduced
ALPHA_PAIR = FAMILY_ALPHA / NC_DECLARED         # 0.0090909090909...
NULL_CELLS = [(100, 40), (140, 40)]             # 4.5
R_TARGET = 300                 # 4.5
R_MIN = 200                    # 4.5/4.6 HARD FLOOR
N_CLUSTER = 5                  # 4.5   5 disjoint pool quadruples
POOL_BANK = 20                 # 4.5   20 pools per cell
R_TARGET_NC = 60               # 4.5   N-C, secondary
G_CAL = 0.040                  # 4.6   calibration gate
DELTA_GRID = [0.05, 0.10, 0.15, 0.20, 0.30, 0.50]          # 4.7
DELTA_ADMISSIBILITY = 0.50     # 4.7   frozen admissibility clause
EXACTNESS_TOL = 1e-12          # 4.5   |V - V''| and |m3 - m3''|
Z95 = 1.959963984540054        # [closed form] normal 97.5 percentile
BOOT_B = 20000                 # cluster bootstrap replicates
BOOT_SEED = 20260808

# Ladder, prereg.md 4.9
WALL_BUDGET = 5400.0
CHECKPOINT = 4200.0
STAGES = [40, 20]              # replicates per cluster per stage: 200 then 300

FORBIDDEN_WORDS = ["absent", "no departure", "vanishes",
                   "consistent with zero", "negligible difference"]


# ================================================================== seeds
def seed_basis(d, beta, i):
    return 700000 + d * 1000 + beta * 10 + i


def seed_error(d):
    return 20260805 + d


def seed_graded(d, beta, j):
    return 500000 + d * 1000 + beta * 10 + j


# ============================================================== error law
_POPCNT4 = np.array([bin(v).count("1") for v in range(16)], dtype=np.int8)


def cbd_eta2(rng, n, d):
    r = rng.integers(0, 16, size=(n, d), dtype=np.uint8)
    return (_POPCNT4[r & 3] - _POPCNT4[r >> 2]).astype(np.int8)


def make_cbd_pool(d, seed_obj):
    """[carried] The committed CBD error stream in the committed chunk order.
    Returns (float32 pool, float64 squared norms, integer pmf histogram)."""
    rng = np.random.default_rng(seed_obj)
    Ef = np.empty((N_ERR, d), dtype=np.float32)
    n2 = np.empty(N_ERR, dtype=np.float64)
    hist = np.zeros(5, dtype=np.int64)
    for s0 in range(0, N_ERR, CHUNK):
        s1 = min(N_ERR, s0 + CHUNK)
        Ei = cbd_eta2(rng, s1 - s0, d)
        hist += np.bincount((Ei.astype(np.int32) + 2).ravel(), minlength=5)
        n2[s0:s1] = (Ei.astype(np.int32) ** 2).sum(1)
        Ef[s0:s1] = Ei
    return Ef, n2, hist


def make_gauss_pool(d, p):
    """N-C, prereg.md 4.5: i.i.d. N(0,1) errors, default_rng([8, d, p])."""
    rng = np.random.default_rng([8, d, p])
    Ef = np.empty((N_ERR, d), dtype=np.float32)
    n2 = np.empty(N_ERR, dtype=np.float64)
    for s0 in range(0, N_ERR, CHUNK):
        s1 = min(N_ERR, s0 + CHUNK)
        x = rng.standard_normal((s1 - s0, d), dtype=np.float32)
        Ef[s0:s1] = x
        n2[s0:s1] = (x.astype(np.float64) ** 2).sum(1)
    return Ef, n2


# ================================================================ frames
def graded_paths(d, beta, n_draw=N_DRAW):
    """[carried] (S_j, G_j) drawn ONCE per (d,beta,j) from seed_graded, BEFORE
    and INDEPENDENTLY of the t list, reused across every t."""
    out = []
    for j in range(n_draw):
        g = np.random.default_rng(seed_graded(d, beta, j))
        S = g.choice(d, size=beta, replace=False)
        G = g.standard_normal((d, beta))
        E = np.zeros((d, beta))
        E[S, np.arange(beta)] = 1.0
        out.append((E, G))
    return out


def graded_frames(paths, t):
    """[carried] float64 QR, cast to float32 exactly as the committed
    instrument does, so the GR arm reproduces the committed record."""
    return [np.linalg.qr(np.sqrt(1.0 - t) * E + np.sqrt(t) * G)[0]
            .astype(np.float32) for (E, G) in paths]


def unreduced_frames(d, beta, n_draw=N_DRAW):
    """[carried] The committed unreduced arm, read BEFORE any reduction.
    NO LLL AND NO BKZ IS RUN.  AM-9 nomenclature: the generator's `k` counts
    the q-SCALED rows (|K_q|), written k_fpylll; here k_fpylll = d//2, and at
    k = d/2 the identity-block reading |K_I| = d/2 coincides with it."""
    from fpylll import IntegerMatrix, FPLLL
    out = []
    for i in range(n_draw):
        FPLLL.set_random_seed(seed_basis(d, beta, i))
        A = IntegerMatrix.random(d, "qary", k=d // 2, q=Q_MOD)
        M = np.array([[A[r, c] for c in range(d)] for r in range(d)],
                     dtype=np.float64)
        Qf, _ = np.linalg.qr(M.T)
        Q60 = np.ascontiguousarray(Qf[:, d - BETA_MAX:], dtype=np.float32)
        out.append(np.ascontiguousarray(Q60[:, BETA_MAX - beta:]))
    return out


# ============================================ TL, the two-level family, 4.2
def v_tl(u, d, beta):
    m = beta / d
    return (beta * ((u - m) ** 2 + (1.0 - u - m) ** 2)
            + (d - 2 * beta) * m * m)


def m3_tl(u, d, beta):
    m = beta / d
    return (beta * ((u - m) ** 3 + (1.0 - u - m) ** 3)
            + (d - 2 * beta) * (-m) ** 3)


def u_from_v(V, d, beta):
    """4.2 closed-form inverse, float64.  None if V is outside the reachable
    interval [V_TL(1/2), V_TL(1)] (declared UNREACHABLE)."""
    m = beta / d
    S = (V - (d - 2 * beta) * m * m) / beta
    x = S / 2.0 - (0.5 - m) ** 2
    if x < 0.0:
        return None
    u = 0.5 + np.sqrt(x)
    if u > 1.0:
        return None
    return float(u)


def tl_support(tag, d, beta, s, r=None):
    """4.2 THE REPAIR, frozen: BOTH the support AND the pairing are drawn
    afresh at every index from default_rng([TAG, d, beta, s]).  For the
    replicated nulls the replicate index r is appended -- see the report's
    implementation-completion note; the frozen text fixes TAG 5 (real arm)
    and TAG 6 (null N-A) but not the replicate coordinate."""
    key = [tag, d, beta, s] if r is None else [tag, d, beta, s, r]
    rng = np.random.default_rng(key)
    perm = rng.permutation(d)
    support = perm[0:2 * beta]
    return (np.ascontiguousarray(support[0::2]),
            np.ascontiguousarray(support[1::2]))


def tl_frame64(u, d, beta, a_idx, b_idx):
    """4.2: beta mutually orthogonal rank-1 projectors on the drawn coordinate
    PAIRS, each with diagonal (u, 1-u) and off-diagonal +sqrt(u(1-u)).
    FLOAT64 THROUGHOUT -- the frozen 1e-9 V-match is unattainable at the
    committed float32 frame precision (prereg.md 4.2)."""
    Q = np.zeros((d, beta), dtype=np.float64)
    m = np.arange(beta)
    Q[a_idx, m] = np.sqrt(u)
    Q[b_idx, m] = np.sqrt(1.0 - u)
    return Q


# ============================================================ frame scalars
def diag_moments(Q, d, beta):
    """V = sum_a (P_aa - beta/d)^2 and m3 = sum_a (P_aa - beta/d)^3 for
    P = Q Q^T.  Deterministic: ZERO error draws.  float64 arithmetic."""
    Qd = np.asarray(Q, dtype=np.float64)
    pd = np.einsum("ij,ij->i", Qd, Qd)
    c = pd - beta / d
    return float(np.sum(c * c)), float(np.sum(c ** 3))


# ============================================================== projection
def project_D(Ef, n2, frames, d, beta, qb, full_sort_check=False):
    """[carried] The committed projection and estimator: stack the 8 frames
    into a d x (8*beta) float32 array, chunk the error matrix at 2^15,
    accumulate R in float32, then D_j = sort(R_j)[1023]/q_Beta(2^-10) - 1.

    np.partition(kth=1023) selects the identical order statistic as
    np.sort()[1023]; float32 -> float64 is exact and monotone, so partitioning
    on float32 and casting the selected value is identical to sorting the cast
    array.  `full_sort_check` verifies that against the committed np.sort path
    and the run reports the check."""
    nf = len(frames)
    Q = np.ascontiguousarray(np.concatenate(
        [np.asarray(F, dtype=np.float32) for F in frames], axis=1))
    R = np.empty((N_ERR, nf), dtype=np.float32)
    for s0 in range(0, N_ERR, CHUNK):
        s1 = min(N_ERR, s0 + CHUNK)
        S = Ef[s0:s1] @ Q
        S *= S
        R[s0:s1] = S.reshape(s1 - s0, nf, beta).sum(axis=2) / n2[s0:s1, None]
        del S
    D, qe = [], []
    chk = None
    for j in range(nf):
        v = float(np.partition(R[:, j], ORDER_IDX)[ORDER_IDX])
        qe.append(v)
        D.append(v / qb - 1.0)
    if full_sort_check:
        chk = float(max(abs(np.sort(R[:, j].astype(np.float64))[ORDER_IDX]
                            - qe[j]) for j in range(nf)))
    del R
    return D, qe, chk


def project_D_tl_exact(Ef, n2, sup, us, qb):
    """INSTRUMENT CHECK ONLY (not the frozen estimator).  For a TL frame the
    statistic is exactly
        R = [ u*sum e_a^2 + (1-u)*sum e_b^2 + 2 sqrt(u(1-u)) sum e_a e_b ]/|e|^2
    computed here in float64 on integer-valued inputs, so the TL frame is NOT
    rounded to float32 at all.  Comparing this with project_D MEASURES the
    consequence of the committed float32 frame convention on D, instead of
    quoting a bound for it."""
    out = []
    for (a_idx, b_idx), u in zip(sup, us):
        ca, cb, cc = np.sqrt(u), np.sqrt(1.0 - u), 2.0 * np.sqrt(u * (1.0 - u))
        R = np.empty(N_ERR, dtype=np.float64)
        for s0 in range(0, N_ERR, CHUNK):
            s1 = min(N_ERR, s0 + CHUNK)
            ea = Ef[s0:s1, a_idx].astype(np.float64)
            eb = Ef[s0:s1, b_idx].astype(np.float64)
            R[s0:s1] = (u * (ea * ea).sum(1) + (1.0 - u) * (eb * eb).sum(1)
                        + cc * (ea * eb).sum(1)) / n2[s0:s1]
            del ea, eb
        out.append(float(np.partition(R, ORDER_IDX)[ORDER_IDX]) / qb - 1.0)
        del R
    _ = (ca, cb)
    return out


# ================================================= 4.3 the SE decomposition
def se_decomposition(Delta):
    """Two-way random-effects decomposition on the S x E table of paired
    differences (supports and pools crossed, no interaction term modelled),
    prereg.md 4.3.  MANDATORY REPORTING of all three components."""
    S, E = Delta.shape
    gm = float(Delta.mean())
    row = Delta.mean(axis=1)
    col = Delta.mean(axis=0)
    MS_S = float(E * ((row - gm) ** 2).sum() / (S - 1))
    MS_P = float(S * ((col - gm) ** 2).sum() / (E - 1))
    resid = Delta - row[:, None] - col[None, :] + gm
    MS_res = float((resid ** 2).sum() / ((S - 1) * (E - 1)))
    num = MS_S + MS_P - MS_res
    negflag = bool(num <= 0.0)
    if negflag:
        var = MS_res / (S * E)
        nu = float((S - 1) * (E - 1))
    else:
        var = num / (S * E)
        den = (MS_S ** 2 / (S - 1) + MS_P ** 2 / (E - 1)
               + MS_res ** 2 / ((S - 1) * (E - 1)))
        nu = float(num ** 2 / den) if den > 0 else float((S - 1) * (E - 1))
    nu = max(1.0, nu)
    sig_e = MS_res
    sig_S = (MS_S - MS_res) / E
    sig_P = (MS_P - MS_res) / S
    c_S, c_P, c_e = sig_S / S, sig_P / E, sig_e / (S * E)
    tot = c_S + c_P + c_e
    return {
        "S": S, "E": E,
        "MS_S": MS_S, "MS_P": MS_P, "MS_res": MS_res,
        "MS_S_df": S - 1, "MS_P_df": E - 1, "MS_res_df": (S - 1) * (E - 1),
        "sigma2_support": sig_S, "sigma2_pool": sig_P, "sigma2_resid": sig_e,
        "contrib_support_abs": c_S, "contrib_pool_abs": c_P,
        "contrib_resid_abs": c_e,
        "contrib_support_pct": (100.0 * c_S / tot) if tot != 0 else None,
        "contrib_pool_pct": (100.0 * c_P / tot) if tot != 0 else None,
        "contrib_resid_pct": (100.0 * c_e / tot) if tot != 0 else None,
        "structural_pct_support_plus_pool":
            (100.0 * (c_S + c_P) / tot) if tot != 0 else None,
        "contrib_pct_interpretable": bool(not negflag and tot > 0),
        "contrib_pct_note": (
            "the percentages are shares of the RAW total "
            "(MS_S + MS_P - MS_res)/(S*E), which is not positive here, so they "
            "are printed for audit but are not interpretable as shares"
            if negflag else None),
        "var_Delta_bar": float(var),
        "SE_Delta_bar": float(np.sqrt(var)),
        "nu_eff": nu,
        "NEGATIVE_VARIANCE_COMPONENT": negflag,
        "negative_variance_note": (
            "MS_S + MS_P - MS_res <= 0: the estimate is replaced by "
            "MS_res/(S*E) and nu_eff by the residual df (S-1)(E-1) = 21, "
            "prereg.md 4.3 degenerate branch; the raw mean squares are "
            "printed above." if negflag else None),
        "Delta_bar": gm,
        "row_means_over_supports": row.tolist(),
        "col_means_over_pools": col.tolist(),
    }


# ======================================================= interval estimates
def wilson(x, n, z=Z95):
    if n <= 0:
        return {"n": n, "x": x, "point": None, "lower": None, "upper": None}
    p = x / n
    c = z * z / n
    centre = (p + c / 2.0) / (1.0 + c)
    half = (z / (1.0 + c)) * np.sqrt(p * (1.0 - p) / n + c / (4.0 * n))
    return {"n": int(n), "x": int(x), "point": float(p),
            "lower": float(max(0.0, centre - half)),
            "upper": float(min(1.0, centre + half))}


def cluster_bootstrap(fires_by_cluster, B=BOOT_B, seed=BOOT_SEED):
    """Resample the pool-quadruple CLUSTERS with replacement.  Replicates that
    share a pool quadruple are NOT independent, so the Wilson interval is a
    LOWER BOUND on the true uncertainty; this is the interval that does not
    assume independence across the shared pools."""
    k = len(fires_by_cluster)
    if k == 0:
        return {"n_clusters": 0, "lower": None, "upper": None,
                "per_cluster_rate": [], "cluster_rate_sd": None}
    xs = np.array([c[0] for c in fires_by_cluster], dtype=np.float64)
    ns = np.array([c[1] for c in fires_by_cluster], dtype=np.float64)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, k, size=(B, k))
    num = xs[idx].sum(axis=1)
    den = ns[idx].sum(axis=1)
    rates = np.where(den > 0, num / np.maximum(den, 1.0), np.nan)
    rates = rates[~np.isnan(rates)]
    per = [(float(x / n) if n > 0 else None) for x, n in zip(xs, ns)]
    per_ok = [p for p in per if p is not None]
    return {
        "n_clusters": k,
        "B": B,
        "per_cluster_x": [int(x) for x in xs],
        "per_cluster_n": [int(n) for n in ns],
        "per_cluster_rate": per,
        "cluster_rate_min": (min(per_ok) if per_ok else None),
        "cluster_rate_max": (max(per_ok) if per_ok else None),
        "cluster_rate_sd": (float(np.std(per_ok, ddof=1))
                            if len(per_ok) > 1 else None),
        "lower": float(np.percentile(rates, 2.5)) if rates.size else None,
        "upper": float(np.percentile(rates, 97.5)) if rates.size else None,
    }


# ==================================================== 4.4 the pair criterion
def score_pair(Delta_table, D_GR_mean, D_TL_mean, alpha_pair=ALPHA_PAIR):
    """The IDENTICAL criterion for a real target and for a null replicate."""
    dec = se_decomposition(Delta_table)
    dbar = dec["Delta_bar"]
    se = dec["SE_Delta_bar"]
    nu = dec["nu_eff"]
    tcrit = float(student_t.ppf(1.0 - alpha_pair / 2.0, nu))
    M = max(abs(D_GR_mean), abs(D_TL_mean))
    at = (abs(dbar) / se) if se > 0 else None
    rel = (abs(dbar) / M) if M > 0 else None
    cond_i = bool(at is not None and at > tcrit)
    cond_ii = bool(rel is not None and rel > TAU_REL)
    sugg = bool(at is not None and cond_ii
                and SUGGESTIVE_FRAC * tcrit <= at < tcrit)
    floor = (tcrit * se / M) if M > 0 else None
    return {
        "decomposition": dec,
        "Delta_bar": dbar, "SE_Delta_bar": se, "nu_eff": nu,
        "t_crit": tcrit, "abs_t": at,
        "denominator_M_max_abs_D": M,
        "relative_difference": rel,
        "condition_i_t": cond_i,
        "condition_ii_relative": cond_ii,
        "FALSIFYING_PAIR": bool(cond_i and cond_ii),
        "SUGGESTIVE_NOT_FALSIFYING": sugg,
        "detection_floor_relative": floor,
        "floor_below_tau_rel": (bool(floor < TAU_REL)
                                if floor is not None else None),
    }


def delta_min_control(sc):
    """4.7 the positive control, closed form.  A constant additive offset
    a = sign(Delta_bar)*delta*M injected into every TL value leaves
    SE(Delta_bar), all three variance components and nu_eff UNCHANGED and moves
    |Delta_bar| to |Delta_bar| + delta*M."""
    se, tcrit, M = sc["SE_Delta_bar"], sc["t_crit"], sc["denominator_M_max_abs_D"]
    if M <= 0:
        return {"status": "UNDEFINED -- M = max(|D_GR|,|D_TL|) is 0"}
    rel = abs(sc["Delta_bar"]) / M
    term_floor = (tcrit * se - abs(sc["Delta_bar"])) / M
    term_tau = TAU_REL - rel
    dmin = max(term_floor, term_tau, 0.0)
    grid = []
    for dl in DELTA_GRID:
        post_abs = abs(sc["Delta_bar"]) + dl * M
        post_rel = rel + dl
        fires = bool((post_abs / se > tcrit if se > 0 else False)
                     and post_rel > TAU_REL)
        grid.append({"delta": dl,
                     "post_injection_abs_Delta_bar": post_abs,
                     "post_injection_abs_t": (post_abs / se) if se > 0 else None,
                     "post_injection_relative_difference": post_rel,
                     "fires": fires})
    return {
        "delta_min": float(dmin),
        "term_detection_floor_minus_realized": float(term_floor),
        "term_tau_rel_minus_realized": float(term_tau),
        "binding_term": ("detection floor" if term_floor >= term_tau
                         else "tau_rel"),
        "realized_relative_difference": float(rel),
        "power_grid": grid,
        "fires_at_delta_0_50": bool(grid[-1]["fires"]),
    }


# ============================================================ verification
def verify_prereg():
    with open(PREREG_PATH, "rb") as f:
        raw = f.read()
    got = hashlib.sha256(raw).hexdigest()
    want_sidecar = open(PREREG_SIDECAR).read().split()[0].strip()
    want_receipt = want_field = None
    if os.path.exists(RECEIPT_PATH):
        rec = json.load(open(RECEIPT_PATH))
        want_receipt = rec.get("archive", {}).get("path_sha256",
                                                  {}).get(PREREG_REL)
        want_field = rec.get("prereg_sha256")
    blob = subprocess.run(
        ["git", "-C", REPO_ROOT, "cat-file", "-p",
         f"{NOTARIZING_COMMIT}:{PREREG_REL}"], capture_output=True)
    in_commit = (hashlib.sha256(blob.stdout).hexdigest()
                 if blob.returncode == 0 else None)
    sources = {"recomputed_from_worktree": got,
               "producer_sidecar_prereg_sha256_txt": want_sidecar,
               "notarized_receipt_path_sha256": want_receipt,
               "notarized_receipt_prereg_sha256_field": want_field,
               "blob_inside_notarizing_commit": in_commit,
               "expected_from_dispatch_task_card": EXPECTED_PREREG_SHA256}
    present = [v for v in sources.values() if v]
    ok = len(set(present)) == 1 and got == EXPECTED_PREREG_SHA256
    return {"prereg_path": PREREG_REL, "prereg_bytes": len(raw),
            "sources": sources, "all_present_sources_agree": bool(ok),
            "match": bool(ok)}


def git_state():
    def g(*a):
        return subprocess.run(["git", "-C", REPO_ROOT] + list(a),
                              capture_output=True, text=True)
    anc = g("merge-base", "--is-ancestor", NOTARIZING_COMMIT, "HEAD")
    dirty = g("status", "--porcelain").stdout.strip()
    return {
        "head_commit": g("rev-parse", "HEAD").stdout.strip(),
        "notarizing_commit_asserted":
            g("rev-parse", NOTARIZING_COMMIT).stdout.strip(),
        "assertion": ("git merge-base --is-ancestor <NOTARIZING COMMIT ITSELF> "
                      "HEAD -- correction V-7: the notarizing commit, NOT its "
                      "parent"),
        "notarizing_commit_is_ancestor_of_head": bool(anc.returncode == 0),
        "worktree_dirty": bool(dirty),
        "worktree_dirty_paths": dirty.splitlines(),
        "branch": g("rev-parse", "--abbrev-ref", "HEAD").stdout.strip(),
    }


def env_record():
    try:
        import fpylll
        fp = fpylll.__version__
    except Exception as e:                                   # pragma: no cover
        fp = f"NOT INSTALLED: {e}"
    try:
        import gmpy2                                         # noqa: F401
        gm = gmpy2.version()
    except Exception:
        gm = "NOT INSTALLED (declared: nothing here depends on it)"
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
        "numpy": np.__version__,
        "scipy": __import__("scipy").__version__,
        "fpylll": fp,
        "gmpy2": gm,
        "blas_threads_pinned_to": 1,
        "blas_backend": "Accelerate (numpy build config: accelerate)",
        "thread_env": {v: os.environ.get(v) for v in
                       ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                        "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
                        "NUMEXPR_NUM_THREADS", "ACCELERATE_MAX_THREADS")},
        "loadavg_at_start": list(os.getloadavg()),
        "n_cpu": os.cpu_count(),
    }


def rss_gib():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1 << 30)


# ====================================================================== main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TASK_DIR,
                                                  "results_am7.json"))
    ap.add_argument("--wall-budget-seconds", type=float, default=WALL_BUDGET)
    ap.add_argument("--checkpoint-seconds", type=float, default=CHECKPOINT)
    args = ap.parse_args()
    t_start = time.time()

    def el():
        return time.time() - t_start

    # ------------------------------------------- GATE 1: notarized prereg
    ver = verify_prereg()
    print("=" * 78)
    print("NOTARIZED PRE-REGISTRATION VERIFICATION (prereg.md 7)")
    for k, v in ver["sources"].items():
        print(f"  {k:42s}: {v}")
    print(f"  {'all_present_sources_agree':42s}: {ver['all_present_sources_agree']}")
    if not ver["match"]:
        print("ABORT: prereg.md sha256 does NOT match the notarized receipt.")
        print("Harness failure, not a result. The run does not proceed.")
        return 2
    git = git_state()
    print("GIT STATE")
    for k, v in git.items():
        print(f"  {k:42s}: {v}")
    if not git["notarizing_commit_is_ancestor_of_head"]:
        print("ABORT: the notarizing commit is NOT an ancestor of HEAD.")
        return 2
    print("  VERIFIED. Section C is loaded read-only and unmodified.")
    print("=" * 78)
    sys.stdout.flush()

    committed = json.load(open(COMMITTED_F19))

    res = {
        "task_id": "TASK-20260808-3a5f18",
        "batch_id": "BATCH-cbe023",
        "goal_id": "GOAL-MLKEM-005",
        "role": "executor",
        "claim_tier": "toy",
        "certificate": {"kind": "none", "reason":
                        "no discrete-log solve and no factor-base relation is "
                        "claimed or produced; the independent re-verifications "
                        "carried here are INSTRUMENT CHECKS and are labelled as "
                        "such, never as certificates"},
        "section": ("C -- AM-7: the matched-V cross-family comparison rebuilt "
                    "with an SE that contains the variance it omitted"),
        "governed_by": ("prereg.md section 4 of TASK-20260808-35efa3, "
                        "notarized by TASK-20260808-e725b4 in commit "
                        + NOTARIZING_COMMIT),
        "prereg_verification": ver,
        "git": git,
        "environment": env_record(),
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "binding_carries": {
            "batch_a44d08_section_C_verdict":
                "VOID IN BOTH DIRECTIONS. It is not cited, not reproduced as a "
                "baseline and not used as a prior anywhere in this run. Neither "
                "'falsified' nor 'consistent' nor its non-firing pairs' floors "
                "exist for this run. This run REBUILDS THE INSTRUMENT.",
            "second_order_derivation":
                "Var(e^T P e) = 2 beta + (mu_4 - 3)(V + beta^2/d) IS a function "
                "of V alone, so L2's derivation is correct AT SECOND ORDER and "
                "nothing in this run touches it. What is open is only whether "
                "the 2^-10 tail quantile inherits that. Any falsification below "
                "refutes the TAIL-LEVEL claim only.",
            "claim_tier":
                "TOY, unconditionally. No number here is transported to "
                "beta = 606, d = 1420, to any FIPS 203 parameter set, to any "
                "attack cost, or to any other parameter set.",
            "am4": "No verdict here is offered as an AM-4 adjudicator; V, m3 "
                   "and D are properties of a basis PRESENTATION.",
            "infrastructure":
                "Budget exhaustion, timeout, crash or a missing dependency is "
                "INFRASTRUCTURE SIGNAL and is NEVER negative mathematical "
                "evidence (AGENTS.md rule 3).",
        },
        "frozen_constants": {
            "cells": CELLS, "null_cells": NULL_CELLS, "q": Q_MOD,
            "S_supports": N_DRAW, "E_pools": N_POOL,
            "errors_per_pool": N_ERR, "chunk": CHUNK,
            "tail_level": P_TAIL, "order_stat_index": ORDER_IDX,
            "graded_t_grid": GRADED_T,
            "V_match_tolerance_abs": V_MATCH_TOL,
            "degeneracy_exclusion_tolerance_abs": DEGEN_TOL,
            "tau_rel": TAU_REL,
            "m3_separation_requirement": M3_SEPARATION,
            "suggestive_band_fraction_of_tcrit": SUGGESTIVE_FRAC,
            "family_wise_alpha": FAMILY_ALPHA,
            "nC_declared": NC_DECLARED, "alpha_pair": ALPHA_PAIR,
            "R_target": R_TARGET, "R_min": R_MIN, "clusters": N_CLUSTER,
            "pool_bank": POOL_BANK, "R_target_NC": R_TARGET_NC,
            "G_CAL": G_CAL, "delta_grid": DELTA_GRID,
            "delta_admissibility_clause": DELTA_ADMISSIBILITY,
            "exactness_tolerance": EXACTNESS_TOL,
            "seed_scheme": {
                "seed_basis": "700000 + d*1000 + beta*10 + i",
                "seed_error": "20260805 + d  (error pool p = 0 of the main arm)",
                "seed_graded": "500000 + d*1000 + beta*10 + j",
                "TAG5_TL_support_real_arm": "default_rng([5, d, beta, s])",
                "TAG6_TL_support_null_NA": "default_rng([6, d, beta, s, r])",
                "TAG5_TL_support_null_NA_side_A":
                    "default_rng([5, d, beta, s, r])",
                "TAG7_error_pool_bank": "default_rng([7, d, p]), p = 0..19",
                "TAG8_gaussian_pool_bank_NC": "default_rng([8, d, p])",
                "TAG10_ambient_permutation_NB":
                    "default_rng([10, d, beta, r]), 8 permutations drawn in "
                    "sequence, one per support index j",
            },
        },
        "cells": {},
        "targets": [],
        "nulls": {},
        "protocol_deviations": [],
        "objections_recorded_and_run_anyway": [],
        "implementation_completions": [],
        "timings": {},
    }

    res["implementation_completions"] = [
        {"what": "replicate coordinate in the null TL support seeds",
         "frozen_text": "prereg.md 4.2 fixes default_rng([5, d, beta, s]) for "
                        "the real arm and TAG 6 for null N-A, but does not fix "
                        "a replicate coordinate for the R = 300 replicated "
                        "null.",
         "completion": "null N-A replicate r draws side A from "
                       "default_rng([5, d, beta, s, r]) and side B from "
                       "default_rng([6, d, beta, s, r]). These 5-element keys "
                       "are distinct streams from the real arm's 4-element "
                       "[5, d, beta, s], so no stream is reused. BOTH sides are "
                       "drawn afresh per replicate, which makes the replicates "
                       "independent up to the shared pool quadruple.",
         "effect_on_any_threshold": "none"},
        {"what": "the 8 permutations of null N-B",
         "frozen_text": "prereg.md 4.5 fixes default_rng([10, d, beta, r]) for "
                        "the ambient coordinate permutation of N-B.",
         "completion": "one rng is created per replicate from that key and 8 "
                       "permutations are drawn from it in sequence, one per "
                       "support index j, so the 8 permuted frames of a "
                       "replicate are not all the same permutation.",
         "effect_on_any_threshold": "none"},
        {"what": "nu_eff in the NEGATIVE-VARIANCE-COMPONENT branch",
         "frozen_text": "prereg.md 4.3 fixes the variance substitution "
                        "MS_res/(S*E) but not the df to use with it.",
         "completion": "nu_eff = (S-1)(E-1) = 21, the residual df of the "
                       "substituted estimator. Every such pair is FLAGGED and "
                       "its raw mean squares are printed.",
         "effect_on_any_threshold": "none; the flag is reported per pair"},
        {"what": "the m3 informativeness filter is NOT applied to a null",
         "frozen_text": "prereg.md 4.4 excludes non-informative pairs "
                        "(|m3_GR - m3_TL| <= 0.1 max|m3|) from n_C; 4.5 "
                        "requires every null to be scored through the "
                        "IDENTICAL criterion.",
         "completion": "N-A and N-B are EXACT nulls precisely because m3 (and "
                       "V) agree between the two sides, so their m3 separation "
                       "is 0 by construction. Applying the informativeness "
                       "filter to a null would exclude every null replicate and "
                       "make the calibration unmeasurable. The FALSIFYING-PAIR "
                       "criterion (4.4 conditions (i) and (ii), the same "
                       "alpha_pair at the declared n_C = 11, the same "
                       "tau_rel = 0.15 and the same SE construction) is applied "
                       "identically; the informativeness rule governs which "
                       "REAL targets enter n_C.",
         "effect_on_any_threshold": "none"},
        {"what": "order-statistic selection by np.partition",
         "frozen_text": "the committed estimator is sort(R)[1023].",
         "completion": "np.partition(R, 1023)[1023] selects the identical "
                       "order statistic and float32 -> float64 is exact and "
                       "monotone. The equality is VERIFIED against the "
                       "committed np.sort path and reported per cell.",
         "effect_on_any_threshold": "none"},
    ]

    # ---------------------------------------------------- fpylll availability
    try:
        import fpylll                                         # noqa: F401
        fpylll_ok = True
    except Exception as e:
        fpylll_ok = False
        res["protocol_deviations"].append({
            "kind": "infrastructure",
            "what": f"fpylll not importable: {e}",
            "effect": "the unreduced real-lattice targets are NOT MEASURED; "
                      "the declared n_C = 8 branch of prereg.md 4.4 applies. "
                      "Infrastructure, never a result (AGENTS.md rule 3)."})
    res["fpylll_available"] = fpylll_ok
    res["declared_nC"] = NC_DECLARED if fpylll_ok else 8
    res["declared_alpha_pair"] = FAMILY_ALPHA / res["declared_nC"]
    alpha_pair = res["declared_alpha_pair"]

    # =================================================================
    # STAGE 1 -- the main matched-V comparison at every target
    # =================================================================
    all_targets = []
    for (d, beta) in CELLS:
        ckey = f"d{d}_b{beta}"
        tc0 = time.time()
        a, b = beta / 2.0, (d - beta) / 2.0
        qb = float(betaincinv(a, b, P_TAIL))
        m = beta / d
        V_lo, V_hi = v_tl(0.5, d, beta), v_tl(1.0, d, beta)
        V_degen = beta * (1.0 - beta / d)
        cell = {
            "d": d, "beta": beta, "m_beta_over_d": m, "q_Beta_2em10": qb,
            "V_reachable_interval_TL": [V_lo, V_hi],
            "V_degenerate_coordinate_projector": V_degen,
            "E_V_haar_exact": 2.0 * beta * (d - beta) / (d * (d + 2.0)),
        }
        print(f"\n[cell {ckey}] q_Beta(2^-10) = {qb:.17g}  TL reachable V in "
              f"[{V_lo:.6f}, {V_hi:.6f}]  degenerate V = {V_degen:.6f}")
        sys.stdout.flush()

        paths = graded_paths(d, beta)
        gframes = {t: graded_frames(paths, t) for t in GRADED_T}
        del paths

        grid = []
        for t in GRADED_T:
            mom = [diag_moments(Q, d, beta) for Q in gframes[t]]
            Vs = [x[0] for x in mom]
            Vm = float(np.mean(Vs))
            grid.append({
                "t": t, "V_mean": Vm, "V_per_draw": Vs,
                "m3_mean": float(np.mean([x[1] for x in mom])),
                "degenerate": bool(abs(Vm - V_degen) <= DEGEN_TOL),
                "reachable_by_mean_V": bool(V_lo <= Vm <= V_hi),
                "n_draws_reachable": int(sum(V_lo <= v <= V_hi for v in Vs)),
            })
        cell["graded_grid_V"] = grid

        survivors = [g for g in grid
                     if g["reachable_by_mean_V"] and not g["degenerate"]]
        survivors.sort(key=lambda g: g["t"])
        keep = {id(g) for g in survivors}
        excl = [{"t": g["t"],
                 "reason": ("DEGENERATE (|V - beta(1-beta/d)| <= 1e-9)"
                            if g["degenerate"] else "UNREACHABLE for TL"),
                 "V_mean": g["V_mean"]}
                for g in grid if id(g) not in keep]
        if len(survivors) >= 3:
            chosen, rule = [survivors[0], survivors[2]], \
                "first and third survivor by t ascending"
        else:
            chosen, rule = survivors, "fewer than three survive -> take all"
        cell["target_selection"] = {
            "rule_applied": rule, "n_survivors": len(survivors),
            "survivor_t": [g["t"] for g in survivors],
            "chosen_t": [g["t"] for g in chosen], "exclusions": excl}
        print(f"  survivors t = {[g['t'] for g in survivors]} -> chosen "
              f"{[g['t'] for g in chosen]}  ({rule})")

        targets = [{"kind": "graded", "t": g["t"],
                    "label": f"graded_t{g['t']:.4f}",
                    "frames": gframes[g["t"]]} for g in chosen]
        if fpylll_ok:
            uf = unreduced_frames(d, beta)
            uV = [diag_moments(Q, d, beta)[0] for Q in uf]
            uVm = float(np.mean(uV))
            reach = all(V_lo <= v <= V_hi for v in uV)
            cell["unreduced_arm"] = {
                "V_mean": uVm, "V_per_draw": uV,
                "k_convention_AM9": ("k_fpylll = d//2 counts the q-scaled rows "
                                     "|K_q|; at k = d/2 the identity-block "
                                     "reading |K_I| = d/2 coincides with it"),
                "reachable_all_8_draws": bool(reach)}
            if reach:
                targets.append({"kind": "unreduced", "t": None,
                                "label": "unreduced", "frames": uf})
            else:
                note = (f"UNREACHABLE BY THE FROZEN RULE: the committed "
                        f"unreduced arm has V = {uVm:.6f}, below "
                        f"V_TL(1/2) = {V_lo:.6f}. prereg.md 4.4 declares this "
                        f"cell's unreduced target unreachable in advance.")
                cell["unreduced_arm"]["exclusion"] = note
                print("  " + note)

        # ---- the E = 4 independent error pools of this cell
        pool_keys = [("seed_error", seed_error(d))] + \
                    [(f"bank_p{p}", [7, d, p]) for p in (1, 2, 3)]
        n_t = len(targets)
        D_GR = np.zeros((n_t, N_DRAW, N_POOL))
        D_TL = np.zeros((n_t, N_DRAW, N_POOL))
        D_GR0 = np.zeros((N_DRAW, N_POOL))       # degenerate check, GR t=0
        D_TL1 = np.zeros((N_DRAW, N_POOL))       # degenerate check, TL u=1
        tl_meta = []
        for ti, tg in enumerate(targets):
            Vg = [diag_moments(Q, d, beta)[0] for Q in tg["frames"]]
            us, sup, f64, f32, resid64, resid32 = [], [], [], [], [], []
            ok = True
            for j, v in enumerate(Vg):
                u = u_from_v(v, d, beta)
                if u is None:
                    ok = False
                    break
                a_idx, b_idx = tl_support(5, d, beta, j)
                Q64 = tl_frame64(u, d, beta, a_idx, b_idx)
                Q32 = Q64.astype(np.float32)
                us.append(u)
                sup.append((a_idx, b_idx))
                f64.append(Q64)
                f32.append(Q32)
                resid64.append(abs(diag_moments(Q64, d, beta)[0] - v))
                resid32.append(abs(diag_moments(Q32, d, beta)[0] - v))
            tl_meta.append({"ok": ok, "u": us, "sup": sup, "f64": f64,
                            "f32": f32, "resid64": resid64,
                            "resid32": resid32, "Vg": Vg})

        exact_check = {}
        sort_check = None
        for pi, (pname, pseed) in enumerate(pool_keys):
            tp = time.time()
            Ef, n2, hist = make_cbd_pool(d, pseed)
            if pi == 0:
                pm = hist / hist.sum()
                cell["cbd_pmf_check"] = {
                    "measured": pm.tolist(),
                    "exact_fips203_cbd_eta2": [1 / 16, 4 / 16, 6 / 16,
                                               4 / 16, 1 / 16],
                    "measured_mu4": float(sum(pm[i] * (i - 2) ** 4
                                              for i in range(5))),
                    "exact_mu4": 2.5}
            for ti, tg in enumerate(targets):
                Dg, _, chk = project_D(Ef, n2, tg["frames"], d, beta, qb,
                                       full_sort_check=(pi == 0 and ti == 0))
                if chk is not None:
                    sort_check = chk
                D_GR[ti, :, pi] = Dg
                if tl_meta[ti]["ok"]:
                    Dt, _, _ = project_D(Ef, n2, tl_meta[ti]["f32"], d, beta,
                                         qb)
                    D_TL[ti, :, pi] = Dt
                    if pi == 0 and ti == 0:
                        Dex = project_D_tl_exact(Ef, n2, tl_meta[ti]["sup"],
                                                 tl_meta[ti]["u"], qb)
                        exact_check = {
                            "target": tg["label"],
                            "pool": pname,
                            "D_TL_float32_frame": Dt,
                            "D_TL_exact_float64_no_frame_rounding": Dex,
                            "max_abs_difference":
                                float(max(abs(x - y)
                                          for x, y in zip(Dt, Dex))),
                            "meaning":
                                "MEASURES, rather than quoting a bound for, the "
                                "consequence on D of the committed float32 "
                                "frame convention. The V-match itself is done "
                                "in float64 (prereg.md 4.2) and is reported at "
                                "both precisions."}
            Dg0, _, _ = project_D(Ef, n2, gframes[0.0], d, beta, qb)
            D_GR0[:, pi] = Dg0
            a1, b1 = tl_support(5, d, beta, 0)
            Q1 = tl_frame64(1.0, d, beta, a1, b1).astype(np.float32)
            Dt1, _, _ = project_D(Ef, n2, [Q1] * N_DRAW, d, beta, qb)
            D_TL1[:, pi] = Dt1
            del Ef, n2
            print(f"    pool {pname:12s} done  {time.time()-tp:6.1f} s  "
                  f"elapsed {el():7.1f} s  RSS {rss_gib():.2f} GiB")
            sys.stdout.flush()

        cell["order_statistic_partition_vs_sort_max_abs_diff"] = sort_check
        cell["tl_float32_frame_consequence_instrument_check"] = exact_check

        # ---- reproduction of the committed GR / unreduced arms (pool p = 0)
        rep = []
        cm = committed["cells"][ckey]
        for ti, tg in enumerate(targets):
            nm = tg["label"]
            if nm not in cm["arms_cbd"]:
                continue
            old = [x - 1.0 for x in
                   cm["arms_cbd"][nm]["ratio_p2em10_over_draws"]["values"]]
            oldV = cm["frame_V"][nm]["per_draw"]
            rep.append({
                "arm": nm,
                "max_abs_D_dev_vs_committed":
                    float(max(abs(x - y) for x, y in zip(D_GR[ti, :, 0], old))),
                "max_abs_V_dev_vs_committed":
                    float(max(abs(x - y) for x, y in
                              zip(tl_meta[ti]["Vg"], oldV))),
                "bitwise_identical_D":
                    bool(all(x == y for x, y in zip(D_GR[ti, :, 0], old)))})
        cell["reproduction_vs_committed_BATCH_f19c37"] = {
            "source": "BATCH-f19c37/tasks/TASK-20260806-ca4377/results.json",
            "pool": "p = 0, seed_error(d) = 20260805 + d",
            "rows": rep,
            "all_bitwise_identical": bool(rep) and
                bool(all(r["bitwise_identical_D"] for r in rep)),
            "max_abs_D_dev_over_all_arms":
                (float(max(r["max_abs_D_dev_vs_committed"] for r in rep))
                 if rep else None),
            "meaning": ("An INSTRUMENT CHECK that the GR side and the "
                        "unreduced arm this run regenerates from the committed "
                        "seeds are the committed frames. Any deviation is "
                        "reported at full precision and is NOT rounded.")}

        # ---- degenerate instrument check (prereg.md 4.10 Form 4)
        dg = D_GR0 - D_TL1
        sc_dg = score_pair(dg, float(D_GR0.mean()), float(D_TL1.mean()),
                           alpha_pair)
        cell["degenerate_instrument_check"] = {
            "status": ("INSTRUMENT CHECK, NEVER SUPPORT FOR ANYTHING. At "
                       "V = beta(1 - beta/d) both families ARE the same object "
                       "-- a coordinate projector on beta axes -- so agreement "
                       "is forced by identity, not by mechanism. Excluded from "
                       "the scored family BY RULE at 1e-9 before any data."),
            "D_GR_t0_mean": float(D_GR0.mean()),
            "D_TL_u1_mean": float(D_TL1.mean()),
            "Delta_bar": sc_dg["Delta_bar"],
            "SE_Delta_bar": sc_dg["SE_Delta_bar"],
            "abs_t": sc_dg["abs_t"],
            "relative_difference": sc_dg["relative_difference"],
            "FALSIFYING_PAIR_if_it_had_been_scored":
                sc_dg["FALSIFYING_PAIR"]}

        # ---- score every target
        cell_pairs = []
        for ti, tg in enumerate(targets):
            tm = tl_meta[ti]
            if not tm["ok"]:
                cell_pairs.append({"target": tg["label"],
                                   "status": "EXCLUDED -- UNREACHABLE at some "
                                             "draw"})
                continue
            m3_GR = float(np.mean([diag_moments(Q, d, beta)[1]
                                   for Q in tg["frames"]]))
            m3_TL = float(np.mean([diag_moments(Q, d, beta)[1]
                                   for Q in tm["f64"]]))
            den = max(abs(m3_GR), abs(m3_TL))
            m3sep = (abs(m3_GR - m3_TL) / den) if den > 0 else None
            Delta = D_GR[ti] - D_TL[ti]
            sc = score_pair(Delta, float(D_GR[ti].mean()),
                            float(D_TL[ti].mean()), alpha_pair)
            pr = {
                "cell": ckey, "d": d, "beta": beta,
                "target": tg["label"], "target_kind": tg["kind"],
                "t": tg["t"],
                "V_GR_per_draw": tm["Vg"],
                "V_GR_mean": float(np.mean(tm["Vg"])),
                "u_per_draw": tm["u"],
                "V_TL_closed_form_per_draw":
                    [v_tl(u, d, beta) for u in tm["u"]],
                "V_match_residual_float64_max": float(max(tm["resid64"])),
                "V_match_residual_float64_per_draw": tm["resid64"],
                "V_match_within_frozen_1e9_tolerance":
                    bool(max(tm["resid64"]) <= V_MATCH_TOL),
                "V_match_residual_float32_realized_max":
                    float(max(tm["resid32"])),
                "V_match_float32_note":
                    ("The frozen 1e-9 is achieved in float64, which is what "
                     "prereg.md 4.2 requires. The float32 frame actually "
                     "consumed by the committed projection realizes a coarser "
                     "V; the consequence on D is MEASURED in "
                     "tl_float32_frame_consequence_instrument_check."),
                "m3_GR_mean": m3_GR, "m3_TL_mean": m3_TL,
                "m3_separation": m3sep,
                "INFORMATIVE": bool(m3sep is not None
                                    and m3sep > M3_SEPARATION),
                "D_GR_table_S_by_E": D_GR[ti].tolist(),
                "D_TL_table_S_by_E": D_TL[ti].tolist(),
                "D_GR_mean": float(D_GR[ti].mean()),
                "D_TL_mean": float(D_TL[ti].mean()),
                "Delta_table_S_by_E": Delta.tolist(),
                "scoring": sc,
                "delta_min_positive_control": delta_min_control(sc),
            }
            cell_pairs.append(pr)
            all_targets.append(pr)
            dec = sc["decomposition"]
            print(f"  [{tg['label']:<18s}] V={pr['V_GR_mean']:9.6f} "
                  f"|dV|64={pr['V_match_residual_float64_max']:.2e} "
                  f"D_GR={pr['D_GR_mean']:+.8f} D_TL={pr['D_TL_mean']:+.8f} "
                  f"Delta={sc['Delta_bar']:+.8f} SE={sc['SE_Delta_bar']:.3e} "
                  f"nu={sc['nu_eff']:.2f} |t|={sc['abs_t']:.3f} "
                  f"rel={100*(sc['relative_difference'] or 0):.2f}% "
                  f"[S%={dec['contrib_support_pct']:.1f} "
                  f"P%={dec['contrib_pool_pct']:.1f} "
                  f"e%={dec['contrib_resid_pct']:.1f}] "
                  f"FALS={sc['FALSIFYING_PAIR']}")
            sys.stdout.flush()
        cell["pairs"] = cell_pairs
        cell["timing_cell_wall_seconds"] = round(time.time() - tc0, 2)
        res["cells"][ckey] = cell
        del gframes

    res["targets"] = all_targets
    res["timings"]["stage1_main_comparison_seconds"] = round(el(), 2)
    print(f"\nSTAGE 1 complete at {el():.1f} s   RSS {rss_gib():.2f} GiB")
    sys.stdout.flush()

    # =================================================================
    # STAGE 2 -- the replicated null calibration
    # =================================================================
    # Per-cell null configuration: the u vector and the GR frames of the
    # cell's FIRST graded target, so both nulls sit at the supports and u
    # values the real targets occupy (prereg.md 4.10 Form 3 guard (b)).
    null_cfg = {}
    for (d, beta) in NULL_CELLS:
        ckey = f"d{d}_b{beta}"
        first = None
        for pr in all_targets:
            if pr["cell"] == ckey and pr["target_kind"] == "graded":
                first = pr
                break
        if first is None:
            continue
        qb = res["cells"][ckey]["q_Beta_2em10"]
        paths = graded_paths(d, beta)
        gf = graded_frames(paths, first["t"])
        null_cfg[ckey] = {"d": d, "beta": beta, "qb": qb,
                          "u": first["u_per_draw"], "t": first["t"],
                          "gr_frames": gf,
                          "target_label": first["target"]}
        del paths

    def null_frames(kind, d, beta, cfg, r):
        """Returns (framesA, framesB, meta) for one null replicate."""
        us = cfg["u"]
        if kind == "N-A":
            fa, fb, sa, sb = [], [], [], []
            for j, u in enumerate(us):
                a1, b1 = tl_support(5, d, beta, j, r)
                a2, b2 = tl_support(6, d, beta, j, r)
                fa.append(tl_frame64(u, d, beta, a1, b1))
                fb.append(tl_frame64(u, d, beta, a2, b2))
                sa.append((a1, b1))
                sb.append((a2, b2))
            return fa, fb, {"supA": sa, "supB": sb}
        if kind in ("N-B",):
            rng = np.random.default_rng([10, d, beta, r])
            fa = cfg["gr_frames"]
            fb = []
            for j in range(N_DRAW):
                perm = rng.permutation(d)
                fb.append(np.ascontiguousarray(fa[j][perm, :]))
            return fa, fb, {}
        if kind == "N-C":
            fa = cfg["gr_frames"]
            fb = []
            for j, u in enumerate(us):
                a1, b1 = tl_support(5, d, beta, j, r)
                fb.append(tl_frame64(u, d, beta, a1, b1).astype(np.float32))
            return fa, fb, {}
        raise ValueError(kind)

    def exactness(kind, fa, fb, d, beta):
        va = [diag_moments(Q, d, beta) for Q in fa]
        vb = [diag_moments(Q, d, beta) for Q in fb]
        return (float(max(abs(x[0] - y[0]) for x, y in zip(va, vb))),
                float(max(abs(x[1] - y[1]) for x, y in zip(va, vb))))

    null_plan = [("N-A", c) for c in NULL_CELLS] + \
                [("N-B", c) for c in NULL_CELLS]
    null_state = {}
    for kind, (d, beta) in null_plan:
        null_state[(kind, d, beta)] = {
            "fires": [[0, 0] for _ in range(N_CLUSTER)],     # [x, n]
            "abs_t": [], "rel": [], "se": [], "nu": [],
            "contrib_sp": [], "negvar": 0,
            "exact_V_max": 0.0, "exact_m3_max": 0.0,
            "replicates": []}

    ladder_notes = []
    cluster_cost = {}

    def run_null_unit(kind, d, beta, stage_idx, n_per_cluster):
        """One (null, cell, stage) unit: 5 clusters x n_per_cluster
        replicates, pools held one at a time."""
        ckey = f"d{d}_b{beta}"
        cfg = null_cfg[ckey]
        qb = cfg["qb"]
        st = null_state[(kind, d, beta)]
        offset = sum(STAGES[:stage_idx])
        cached_A = (kind in ("N-B", "N-C"))
        for c in range(N_CLUSTER):
            if el() > args.checkpoint_seconds:
                ladder_notes.append(
                    f"{kind} {ckey} stage {stage_idx} cluster {c}: NOT RUN -- "
                    f"the {args.checkpoint_seconds:.0f} s checkpoint of "
                    f"prereg.md 4.9 bound at {el():.1f} s. INFRASTRUCTURE.")
                return False
            est = cluster_cost.get((kind, ckey), 400.0) * n_per_cluster / \
                max(1, cluster_cost.get((kind, ckey, "n"), n_per_cluster))
            if el() + est > args.wall_budget_seconds - 300.0:
                ladder_notes.append(
                    f"{kind} {ckey} stage {stage_idx} cluster {c}: NOT RUN -- "
                    f"projected cluster cost {est:.0f} s would exceed the "
                    f"{args.wall_budget_seconds:.0f} s hard budget at "
                    f"{el():.1f} s. INFRASTRUCTURE, never a result.")
                return False
            reps = [c + N_CLUSTER * (offset + k) for k in range(n_per_cluster)]
            pool_ids = [(4 * c + i) % POOL_BANK for i in range(N_POOL)]
            DA = np.zeros((len(reps), N_DRAW, N_POOL))
            DB = np.zeros((len(reps), N_DRAW, N_POOL))
            t0c = time.time()
            for pi, p in enumerate(pool_ids):
                if kind == "N-C":
                    Ef, n2 = make_gauss_pool(d, p)
                else:
                    Ef, n2, _ = make_cbd_pool(d, [7, d, p])
                if cached_A:
                    Da, _, _ = project_D(Ef, n2, cfg["gr_frames"], d, beta, qb)
                for ri, r in enumerate(reps):
                    fa, fb, _meta = null_frames(kind, d, beta, cfg, r)
                    if pi == 0 and kind in ("N-A", "N-B"):
                        eV, em3 = exactness(kind, fa, fb, d, beta)
                        st["exact_V_max"] = max(st["exact_V_max"], eV)
                        st["exact_m3_max"] = max(st["exact_m3_max"], em3)
                    if cached_A:
                        DA[ri, :, pi] = Da
                    else:
                        Da2, _, _ = project_D(Ef, n2, fa, d, beta, qb)
                        DA[ri, :, pi] = Da2
                    Db, _, _ = project_D(Ef, n2, fb, d, beta, qb)
                    DB[ri, :, pi] = Db
                del Ef, n2
            for ri, r in enumerate(reps):
                Delta = DA[ri] - DB[ri]
                sc = score_pair(Delta, float(DA[ri].mean()),
                                float(DB[ri].mean()), alpha_pair)
                st["fires"][c][1] += 1
                if sc["FALSIFYING_PAIR"]:
                    st["fires"][c][0] += 1
                st["abs_t"].append(sc["abs_t"])
                st["rel"].append(sc["relative_difference"])
                st["se"].append(sc["SE_Delta_bar"])
                st["nu"].append(sc["nu_eff"])
                st["contrib_sp"].append(
                    sc["decomposition"]["structural_pct_support_plus_pool"])
                if sc["decomposition"]["NEGATIVE_VARIANCE_COMPONENT"]:
                    st["negvar"] += 1
                st["replicates"].append({
                    "r": r, "cluster": c, "pools": pool_ids,
                    "Delta_bar": sc["Delta_bar"], "SE": sc["SE_Delta_bar"],
                    "nu_eff": sc["nu_eff"], "abs_t": sc["abs_t"],
                    "relative_difference": sc["relative_difference"],
                    "FALSIFYING_PAIR": sc["FALSIFYING_PAIR"]})
            cluster_cost[(kind, ckey)] = time.time() - t0c
            cluster_cost[(kind, ckey, "n")] = len(reps)
            x = sum(f[0] for f in st["fires"])
            n = sum(f[1] for f in st["fires"])
            print(f"    {kind} {ckey} stage{stage_idx} cluster{c} pools"
                  f"{pool_ids} {len(reps)} reps in {time.time()-t0c:6.1f} s -> "
                  f"running {x}/{n}   elapsed {el():7.1f} s  "
                  f"RSS {rss_gib():.2f} GiB")
            sys.stdout.flush()
        return True

    print("\nSTAGE 2 -- replicated null calibration "
          "(stage 1 of each unit takes every unit to R_min = 200 before any "
          "unit is topped up to R_target = 300)")
    sys.stdout.flush()
    for stage_idx, n_per in enumerate(STAGES):
        for kind, (d, beta) in null_plan:
            if f"d{d}_b{beta}" not in null_cfg:
                continue
            run_null_unit(kind, d, beta, stage_idx, n_per)

    # ---- N-C, secondary
    nc_state = {}
    for (d, beta) in NULL_CELLS:
        ckey = f"d{d}_b{beta}"
        if ckey not in null_cfg:
            continue
        null_state[("N-C", d, beta)] = {
            "fires": [[0, 0] for _ in range(N_CLUSTER)],
            "abs_t": [], "rel": [], "se": [], "nu": [], "contrib_sp": [],
            "negvar": 0, "exact_V_max": None, "exact_m3_max": None,
            "replicates": []}
        run_null_unit("N-C", d, beta, 0, R_TARGET_NC // N_CLUSTER)
    _ = nc_state

    res["timings"]["stage2_nulls_seconds"] = round(
        el() - res["timings"]["stage1_main_comparison_seconds"], 2)

    # ---- summarize the nulls
    def summarize(kind, d, beta):
        st = null_state.get((kind, d, beta))
        if st is None:
            return None
        x = sum(f[0] for f in st["fires"])
        n = sum(f[1] for f in st["fires"])
        at = [v for v in st["abs_t"] if v is not None]
        rl = [v for v in st["rel"] if v is not None]
        sp = [v for v in st["contrib_sp"] if v is not None]
        return {
            "null": kind, "cell": f"d{d}_b{beta}",
            "target_label": null_cfg[f"d{d}_b{beta}"]["target_label"],
            "R_realized": int(n), "x_falsifying": int(x),
            "R_target": (R_TARGET if kind in ("N-A", "N-B") else R_TARGET_NC),
            "R_min": (R_MIN if kind in ("N-A", "N-B") else None),
            "R_min_met": (bool(n >= R_MIN) if kind in ("N-A", "N-B") else None),
            "point_rate": (x / n) if n else None,
            "wilson95": wilson(x, n),
            "wilson_upper_is_a_LOWER_BOUND_on_uncertainty":
                "replicates sharing a pool quadruple are NOT independent, so "
                "the Wilson interval understates the true uncertainty; the "
                "cluster bootstrap below does not assume that independence",
            "cluster_bootstrap95": cluster_bootstrap(st["fires"]),
            "median_abs_t": (float(np.median(at)) if at else None),
            "p95_abs_t": (float(np.percentile(at, 95)) if at else None),
            "median_relative_difference": (float(np.median(rl)) if rl else None),
            "p95_relative_difference":
                (float(np.percentile(rl, 95)) if rl else None),
            "median_SE": (float(np.median(st["se"])) if st["se"] else None),
            "median_nu_eff": (float(np.median(st["nu"])) if st["nu"] else None),
            "median_structural_pct_support_plus_pool":
                (float(np.median(sp)) if sp else None),
            "n_negative_variance_component": st["negvar"],
            "exactness_max_abs_V_difference": st["exact_V_max"],
            "exactness_max_abs_m3_difference": st["exact_m3_max"],
            "exactness_within_1e12": (
                None if st["exact_V_max"] is None else
                bool(st["exact_V_max"] <= EXACTNESS_TOL
                     and st["exact_m3_max"] <= EXACTNESS_TOL)),
            "replicates": st["replicates"],
        }

    for kind in ("N-A", "N-B", "N-C"):
        for (d, beta) in NULL_CELLS:
            s = summarize(kind, d, beta)
            if s:
                res["nulls"][f"{kind}__d{d}_b{beta}"] = s

    # ---- G-CAL
    gcal_rows = []
    for kind in ("N-A", "N-B"):
        for (d, beta) in NULL_CELLS:
            key = f"{kind}__d{d}_b{beta}"
            s = res["nulls"].get(key)
            if s is None:
                gcal_rows.append({"unit": key, "status": "NOT MEASURED"})
                continue
            undec = s["R_realized"] < R_MIN
            gcal_rows.append({
                "unit": key, "R": s["R_realized"], "x": s["x_falsifying"],
                "point_rate": s["point_rate"],
                "wilson_upper": s["wilson95"]["upper"],
                "cluster_bootstrap_upper": s["cluster_bootstrap95"]["upper"],
                "R_min_met": not undec,
                "passes_G_CAL": (None if undec else
                                 bool(s["wilson95"]["upper"] <= G_CAL)),
                "status": ("UNDECIDED -- realized R below the hard floor 200"
                           if undec else
                           ("PASS" if s["wilson95"]["upper"] <= G_CAL
                            else "FAIL"))})
    all_dec = (len(gcal_rows) == 4
               and all(bool(r.get("R_min_met")) for r in gcal_rows))
    gcal_pass = all_dec and all(r.get("passes_G_CAL") for r in gcal_rows)
    res["G_CAL"] = {
        "threshold": G_CAL,
        "rule": ("CALIBRATED iff, for BOTH N-A and N-B, in BOTH null cells, "
                 "the WILSON 95% UPPER BOUND of the estimated per-pair "
                 "false-falsification rate is <= 0.040 (prereg.md 4.6)"),
        "rows": gcal_rows,
        "all_four_units_decidable": bool(all_dec),
        "PASSES": bool(gcal_pass),
        "status": ("PASS" if gcal_pass else
                   ("UNDECIDED" if not all_dec else "FAIL")),
        "reachability_computed_in_advance_prereg_4_6": {
            "R200_x0": 0.01885, "R200_x1": 0.02777, "R200_x2": 0.03572,
            "R200_x3_refuses": 0.04317, "R100_x0": 0.03699,
            "recomputed_here": {"R200_x0": wilson(0, 200)["upper"],
                                "R200_x1": wilson(1, 200)["upper"],
                                "R200_x2": wilson(2, 200)["upper"],
                                "R200_x3": wilson(3, 200)["upper"],
                                "R100_x0": wilson(0, 100)["upper"],
                                "R300_x5": wilson(5, 300)["upper"],
                                "R300_x6": wilson(6, 300)["upper"]}},
    }

    # =================================================================
    # STAGE 3 -- scoring and the frozen verdict
    # =================================================================
    scored = [p for p in all_targets if p["INFORMATIVE"]]
    noninf = [p for p in all_targets if not p["INFORMATIVE"]]
    nC_realized = len(scored)
    alpha_realized = (FAMILY_ALPHA / nC_realized) if nC_realized else None
    realized_rows = []
    for p in scored:
        sc2 = score_pair(np.array(p["Delta_table_S_by_E"]), p["D_GR_mean"],
                         p["D_TL_mean"], alpha_realized) \
            if alpha_realized else None
        realized_rows.append({
            "cell": p["cell"], "target": p["target"],
            "abs_t": p["scoring"]["abs_t"],
            "t_crit_realized": (sc2["t_crit"] if sc2 else None),
            "FALSIFYING_PAIR_realized": (sc2["FALSIFYING_PAIR"] if sc2
                                         else None)})

    falsifying = [p for p in scored if p["scoring"]["FALSIFYING_PAIR"]]
    suggestive = [p for p in scored
                  if p["scoring"]["SUGGESTIVE_NOT_FALSIFYING"]]
    floors = [p["scoring"]["detection_floor_relative"] for p in scored
              if p["scoring"]["detection_floor_relative"] is not None]
    any_informative_below_tau = any(f < TAU_REL for f in floors)

    pc_all_fire = all(p["delta_min_positive_control"].get("fires_at_delta_0_50")
                      for p in all_targets) and bool(all_targets)
    res["positive_control_delta_min"] = {
        "clause": ("FROZEN ADMISSIBILITY CLAUSE (prereg.md 4.7): if the "
                   "criterion does not fire at delta = 0.50 at EVERY target, "
                   "the rebuilt instrument is UNDERPOWERED BY CONSTRUCTION and "
                   "the Section C verdict is WITHHELD."),
        "fires_at_delta_0_50_at_every_target": bool(pc_all_fire),
        "n_targets": len(all_targets),
        "rows": [{"cell": p["cell"], "target": p["target"],
                  "delta_min": p["delta_min_positive_control"].get("delta_min"),
                  "binding_term":
                      p["delta_min_positive_control"].get("binding_term"),
                  "realized_relative_difference":
                      p["delta_min_positive_control"].get(
                          "realized_relative_difference"),
                  "detection_floor_relative":
                      p["scoring"]["detection_floor_relative"],
                  "fires": {g["delta"]: g["fires"] for g in
                            p["delta_min_positive_control"].get(
                                "power_grid", [])},
                  "post_injection_relative_at_0_50":
                      (p["delta_min_positive_control"]["power_grid"][-1][
                          "post_injection_relative_difference"]
                       if p["delta_min_positive_control"].get("power_grid")
                       else None)}
                 for p in all_targets],
    }

    if not res["G_CAL"]["PASSES"]:
        verdict = "WITHHELD -- INSTRUMENT UNCALIBRATED"
        vreason = ("the calibration gate G-CAL of prereg.md 4.6 did not PASS "
                   f"(status {res['G_CAL']['status']}). No verdict on the "
                   "proposition is stated in either direction; this batch's "
                   "Section C result is the estimated false-falsification rate "
                   "with its intervals, and the proposition stays open exactly "
                   "as it is now.")
    elif not pc_all_fire:
        verdict = "WITHHELD -- UNDERPOWERED BY CONSTRUCTION"
        vreason = ("the frozen delta = 0.50 admissibility clause of prereg.md "
                   "4.7 did not fire at every target.")
    elif falsifying:
        verdict = "L2 TAIL-SUFFICIENCY FALSIFIED AT THE 2^-10 QUANTILE"
        vreason = (f"{len(falsifying)} FALSIFYING PAIR(S) and G-CAL PASSED. "
                   "This refutes the TAIL-LEVEL claim only and explicitly NOT "
                   "the second-order derivation Var(e^T P e) = 2 beta + "
                   "(mu_4 - 3)(V + beta^2/d), which is a function of V alone "
                   "and is untouched.")
    elif any_informative_below_tau:
        verdict = "CONSISTENT"
        vreason = ("no FALSIFYING PAIR, G-CAL PASSED, and at least one "
                   "INFORMATIVE pair has detection floor < tau_rel = 0.15.")
    elif scored:
        verdict = "UNDERPOWERED -- UPPER BOUND"
        vreason = ("no FALSIFYING PAIR and the detection floor is at or above "
                   "tau_rel = 0.15 at every pair. This is NEVER reported as "
                   "CONSISTENT and never as an absence.")
    else:
        verdict = "NOT EVALUABLE -- no informative pair"
        vreason = "no target survived the informativeness rule."

    res["scoring"] = {
        "declared_nC": res["declared_nC"],
        "declared_alpha_pair": alpha_pair,
        "realized_nC_after_reachability_and_informativeness": nC_realized,
        "realized_alpha_pair": alpha_realized,
        "primary_reading": ("DECLARED n_C -- the declared level is the smaller "
                            "alpha_pair whenever realized n_C <= declared n_C, "
                            "hence the larger |t| crit and the more "
                            "conservative against falsification [carried "
                            "convention]"),
        "secondary_realized_nC_rows": realized_rows,
        "n_targets_measured": len(all_targets),
        "n_noninformative_excluded": len(noninf),
        "noninformative_pairs": [
            {"cell": p["cell"], "target": p["target"],
             "m3_GR": p["m3_GR_mean"], "m3_TL": p["m3_TL_mean"],
             "m3_separation": p["m3_separation"],
             "abs_t": p["scoring"]["abs_t"],
             "relative_difference": p["scoring"]["relative_difference"]}
            for p in noninf],
        "n_falsifying": len(falsifying),
        "falsifying_pairs": [{"cell": p["cell"], "target": p["target"],
                              "abs_t": p["scoring"]["abs_t"],
                              "t_crit": p["scoring"]["t_crit"],
                              "relative_difference":
                                  p["scoring"]["relative_difference"]}
                             for p in falsifying],
        "n_suggestive_not_falsifying": len(suggestive),
        "suggestive_pairs": [{"cell": p["cell"], "target": p["target"],
                              "abs_t": p["scoring"]["abs_t"],
                              "t_crit": p["scoring"]["t_crit"],
                              "relative_difference":
                                  p["scoring"]["relative_difference"]}
                             for p in suggestive],
        "detection_floors_relative": {
            f"{p['cell']}/{p['target']}":
                p["scoring"]["detection_floor_relative"] for p in all_targets},
        "tightest_detection_floor_relative": (min(floors) if floors else None),
        "VERDICT": verdict,
        "verdict_reason": vreason,
        "upper_bound_statement": (
            None if verdict.startswith("L2 TAIL") or not floors else
            f"any matched-V cross-family difference not detected here is "
            f"bounded above by {100*min(floors):.2f} percent relative at "
            f"S = {N_DRAW} supports, E = {N_POOL} pools, N = 2^20"),
    }

    # ---- PRED-C1 / C2 / C3, frozen predictions
    sp = [p["scoring"]["decomposition"]["structural_pct_support_plus_pool"]
          for p in all_targets
          if p["scoring"]["decomposition"]["structural_pct_support_plus_pool"]
          is not None]
    sp_ok = [p["scoring"]["decomposition"]["structural_pct_support_plus_pool"]
             for p in all_targets
             if p["scoring"]["decomposition"]["contrib_pct_interpretable"]]
    n_flagged = sum(1 for p in all_targets
                    if p["scoring"]["decomposition"][
                        "NEGATIVE_VARIANCE_COMPONENT"])
    nc_fires = sum(res["nulls"].get(f"N-C__d{d}_b{beta}", {})
                   .get("x_falsifying", 0) for (d, beta) in NULL_CELLS)
    nc_R = sum(res["nulls"].get(f"N-C__d{d}_b{beta}", {}).get("R_realized", 0)
               for (d, beta) in NULL_CELLS)
    res["pre_registered_predictions"] = {
        "PRED-C1": {
            "statement": "with the rebuilt SE, both N-A and N-B satisfy G-CAL "
                         "in both cells",
            "outcome": res["G_CAL"]["status"],
            "falsifier": "any Wilson upper bound above 0.040"},
        "PRED-C2": {
            "statement": "the between-support and between-pool components "
                         "together contribute >= 50% of SE^2(Delta_bar) at a "
                         "majority of targets",
            "per_target_pct": sp,
            "n_targets_at_or_above_50pct": int(sum(1 for v in sp if v >= 50.0)),
            "n_targets": len(sp),
            "n_targets_flagged_NEGATIVE_VARIANCE_COMPONENT": int(n_flagged),
            "per_target_pct_interpretable_only": sp_ok,
            "n_interpretable_at_or_above_50pct":
                int(sum(1 for v in sp_ok if v >= 50.0)),
            "n_interpretable_targets": len(sp_ok),
            "outcome_all_targets": (
                None if not sp else
                ("HOLDS" if sum(1 for v in sp if v >= 50.0) > len(sp) / 2
                 else "FAILS")),
            "outcome_interpretable_targets_only": (
                None if not sp_ok else
                ("HOLDS" if sum(1 for v in sp_ok if v >= 50.0) > len(sp_ok) / 2
                 else "FAILS")),
            "both_readings_reported_because":
                "a target flagged NEGATIVE-VARIANCE-COMPONENT has a raw total "
                "that is not positive, so its percentage shares are printed "
                "for audit but are not interpretable as shares; neither "
                "reading is selected over the other"},
        "PRED-C3": {
            "statement": "under N-C's Gaussian errors the paired |Delta_bar| "
                         "collapses to the sampling floor: 0 FALSIFYING pairs "
                         "of 60 per cell",
            "x_falsifying_total": int(nc_fires), "R_total": int(nc_R),
            "outcome": (None if nc_R == 0 else
                        ("HOLDS" if nc_fires == 0 else "FAILS"))},
        "no_prediction_about_the_proposition":
            "prereg.md 4.8: whether D depends on the frame only through V at "
            "the 2^-10 quantile is OPEN and no expected direction is declared.",
    }

    res["ladder_notes"] = ladder_notes
    if ladder_notes:
        res["protocol_deviations"].append({
            "kind": "infrastructure",
            "what": "the prereg.md 4.9 wall-clock ladder bound",
            "effect": "; ".join(ladder_notes)})
    res["protocol_deviations"].append({
        "kind": "protocol_deviation_recorded",
        "what": "the order in which the four (null, cell) units were computed",
        "frozen_text": "prereg.md 4.9 lists N-A (100,40), then N-A (140,40), "
                       "then N-B in the same two cells, and declares the "
                       "priority order 'N-A both cells first, then N-B, then "
                       "N-C' if the budget binds.",
        "what_was_done": "each unit was taken to the hard floor R_min = 200 "
                         "first, in exactly the declared priority order, and "
                         "only then topped up to R_target = 300 in the same "
                         "order. Replicate r is the same object whenever it is "
                         "computed: its supports, permutations and pool "
                         "quadruple are functions of r alone.",
        "why": "G-CAL is UNDECIDED, and the Section C verdict WITHHELD, unless "
               "ALL FOUR units reach R_min = 200. Running one unit to 300 "
               "before another reaches 200 risks an instrument outcome that "
               "the staged order avoids at zero cost to any threshold.",
        "effect_on_any_threshold": "none. No seed, no replicate identity, no "
                                   "cluster membership, no criterion and no "
                                   "threshold changes.",
        "recorded_because": "AGENTS.md: deviations are recorded, never "
                            "discarded."})

    # ---------------------------------------------------- wording scan
    blob = json.dumps(res).lower()
    res["forbidden_wording_scan"] = {
        "words": FORBIDDEN_WORDS,
        "hits_in_this_json": [w for w in FORBIDDEN_WORDS if w in blob],
        "rule": ("prereg.md 5.4: no 'absent', 'no departure', 'vanishes', "
                 "'consistent with zero' or synonym applied to a measured arm "
                 "without its floor.")}

    ru = resource.getrusage(resource.RUSAGE_SELF)
    res["timings"]["total_wall_seconds"] = round(el(), 2)
    res["timings"]["cpu_seconds"] = round(ru.ru_utime + ru.ru_stime, 2)
    res["resources"] = {
        "max_rss_bytes": ru.ru_maxrss,
        "max_rss_gib": round(ru.ru_maxrss / (1 << 30), 3),
        "wall_budget_seconds": args.wall_budget_seconds,
        "checkpoint_seconds": args.checkpoint_seconds,
        "memory_budget_gib": 4.0,
        "maximum_runs": 1,
        "loadavg_at_end": list(os.getloadavg())}
    res["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    with open(args.out, "w") as f:
        json.dump(res, f, indent=1)

    # ------------------------------------------------------------ summary
    print("\n" + "=" * 78)
    print("SECTION C (AM-7) SUMMARY -- observations only, no interpretation")
    print("=" * 78)
    print(f"declared n_C = {res['declared_nC']}  alpha_pair = {alpha_pair:.12f}")
    print(f"realized n_C = {nC_realized}  targets measured = "
          f"{len(all_targets)}  non-informative = {len(noninf)}")
    print("\n--- SE DECOMPOSITION, MANDATORY REPORTING (prereg.md 4.3) ---")
    print("%-10s %-18s %11s %11s %11s %9s %8s %7s %7s %7s" %
          ("cell", "target", "MS_S", "MS_P", "MS_res", "SE", "nu_eff",
           "S%", "P%", "e%"))
    for p in all_targets:
        dc = p["scoring"]["decomposition"]
        print("%-10s %-18s %11.4e %11.4e %11.4e %9.3e %8.2f %7.1f %7.1f %7.1f" %
              (p["cell"], p["target"], dc["MS_S"], dc["MS_P"], dc["MS_res"],
               dc["SE_Delta_bar"], dc["nu_eff"], dc["contrib_support_pct"],
               dc["contrib_pool_pct"], dc["contrib_resid_pct"]))
    print("\n--- TARGETS ---")
    print("%-10s %-18s %9s %10s %12s %12s %12s %8s %8s %8s %6s" %
          ("cell", "target", "V", "|dV|64", "D_GR", "D_TL", "Delta",
           "|t|", "tcrit", "rel%", "FALS"))
    for p in all_targets:
        s = p["scoring"]
        print("%-10s %-18s %9.6f %10.2e %+12.8f %+12.8f %+12.8f %8.3f %8.3f "
              "%8.3f %6s" %
              (p["cell"], p["target"], p["V_GR_mean"],
               p["V_match_residual_float64_max"], p["D_GR_mean"],
               p["D_TL_mean"], s["Delta_bar"], s["abs_t"] or 0.0, s["t_crit"],
               100 * (s["relative_difference"] or 0.0), s["FALSIFYING_PAIR"]))
    print("\n--- delta_min POSITIVE CONTROL AT EVERY TARGET (prereg.md 4.7) ---")
    print("%-10s %-18s %10s %10s %22s %s" %
          ("cell", "target", "floor%", "delta_min", "binding term",
           "fires at delta ="))
    for p in all_targets:
        pc = p["delta_min_positive_control"]
        fires = [g["delta"] for g in pc.get("power_grid", []) if g["fires"]]
        print("%-10s %-18s %10.2f %10.4f %22s %s" %
              (p["cell"], p["target"],
               100 * (p["scoring"]["detection_floor_relative"] or 0.0),
               pc.get("delta_min", float("nan")),
               pc.get("binding_term", "UNDEFINED"), fires))
    print(f"  fires at delta = 0.50 at EVERY target: {pc_all_fire}")
    print("\n--- NULL CALIBRATION (prereg.md 4.5/4.6) ---")
    print("%-16s %6s %5s %9s %10s %10s %10s %9s %9s" %
          ("unit", "R", "x", "rate", "wilsonLO", "wilsonUP", "bootUP",
           "med|t|", "medrel%"))
    for k, s in res["nulls"].items():
        print("%-16s %6d %5d %9.5f %10.5f %10.5f %10s %9.3f %9.2f" %
              (k, s["R_realized"], s["x_falsifying"], s["point_rate"] or 0.0,
               s["wilson95"]["lower"] or 0.0, s["wilson95"]["upper"] or 0.0,
               ("%.5f" % s["cluster_bootstrap95"]["upper"])
               if s["cluster_bootstrap95"]["upper"] is not None else "n/a",
               s["median_abs_t"] or 0.0,
               100 * (s["median_relative_difference"] or 0.0)))
    print(f"\nG-CAL ({G_CAL}) status: {res['G_CAL']['status']}")
    for r in res["G_CAL"]["rows"]:
        print("   ", r)
    print(f"\nVERDICT: {verdict}")
    print(f"  reason: {vreason}")
    if res["scoring"]["upper_bound_statement"]:
        print("  " + res["scoring"]["upper_bound_statement"])
    print(f"\nwall {res['timings']['total_wall_seconds']} s   "
          f"cpu {res['timings']['cpu_seconds']} s   "
          f"max RSS {res['resources']['max_rss_gib']} GiB")
    print(f"written: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
