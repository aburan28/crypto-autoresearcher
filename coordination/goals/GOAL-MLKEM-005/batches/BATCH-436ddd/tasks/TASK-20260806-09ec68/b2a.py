#!/usr/bin/env python3
"""
TASK-20260806-09ec68 / BATCH-436ddd / GOAL-MLKEM-005
B2-A: re-run the TASK-20260805-708b70 (T2) instrument with a sensitivity
demonstration that CAN FAIL, and with the three comparison arms whose absence
made the previous real arm uninterpretable.

Governed by DEC-20260805-4823db `next_actions`.

KEPT IDENTICAL TO BATCH-a51f91 / TASK-20260805-708b70
  * the four cells (d, beta) in {100,140} x {30,40}, k = d/2, q = 3329
  * the statistic  R = ||Q^T e||^2 / ||e||^2, Q the tail-beta GSO frame
  * the frozen empirical quantile estimator  q_emp(p) = sort(R)[round(p*N)-1]
  * P1 (|r(2^-10)-1| <= 0.05 and |r(2^-16)-1| <= 0.10, pooled, real arm, all
    four cells) and P2 (between-basis fraction <= 0.20)
  * the Haar null arm and its seeds -> the same 8 subspaces, bit for bit
  * the CBD_{eta=2} error draws and their seed -> the same 2^20 errors
  * the basis seeds -> the same 32 lattices
  * the NULL-ARM-FIRST discipline: P1/P2 are computed and emitted on the null
    arm before the real arm is read.

REPLACED
  * the sensitivity demonstration.  The old one manipulated the ERROR LAW while
    the null removed the PROJECTOR (DF-1); under a Haar projector the marginal
    law of R is exactly Beta for any error covariance, so it could not fail.
    The new one manipulates the projector: the graded family
        Q_t = QR( sqrt(1-t) * E_S + sqrt(t) * G ),   t in {0,.05,.10,.25,.50,.75,1}
    E_S a d x beta coordinate-selector for a random beta-subset S, G a d x beta
    iid standard Gaussian.  t = 0 is coordinate-aligned, t = 1 is Haar.
  * the threshold, which is now in units of the SE OF THE DIFFERENCE of the two
    arm means at the declared draw count, not in per-draw sds of one arm (DF-2).

ADDED
  * arm `unreduced` : tail-beta GSO frame of the RAW q-ary basis
  * arm `lll_only`  : tail-beta GSO frame after LLL, before BKZ
  * a GAUSSIAN-ERROR NULL OF THE NULL: every arm re-measured with an iid
    N(0,1) error.  R is then exactly Beta(beta/2,(d-beta)/2) for ANY fixed
    projector, so every arm must return 1.000.  Any departure there is
    instrument error and nothing else.
  * a beta-trend at beta in {30,40,50,60} for the pre-registered ~1/sqrt(beta)
    decay FALSIFIER.

The pre-registration below is frozen in this file, sha256'd, emitted before any
research number is computed, and written verbatim into b2a_report.md by
`--phase prereg` BEFORE `--phase measure` is run.

This script performs no git operation and writes only inside its task directory.
"""

import argparse
import hashlib
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
REPORT_PATH = os.path.join(TASK_DIR, "b2a_report.md")
PREREG_BEGIN = "<!-- BEGIN FROZEN PRE-REGISTRATION -->"
PREREG_END = "<!-- END FROZEN PRE-REGISTRATION -->"

Q_MOD = 3329
ETA = 2
P_TAIL = [2.0 ** -10, 2.0 ** -16]
BODY_LO, BODY_HI = 0.01, 0.99

CELLS = [(100, 30), (100, 40), (140, 30), (140, 40)]
GRADED_T = [0.0, 0.05, 0.10, 0.25, 0.50, 0.75, 1.00]
EXT_D = [100, 140]
EXT_BKZ = 40                      # the beta-trend reads the BKZ-40 basis set
EXT_BETAS = [30, 40, 50, 60]      # 50 and 60 are the two values beyond {30,40}
BETA_MAX = 60                     # tail columns retained per basis
GATE_K = 4.0                      # gate is K * SE(difference of arm means)
N_DRAW = 8

GAUSS_ARMS = ["haar_null", "unreduced", "lll_only", "real_bkz",
              "graded_t0.00", "graded_t0.50"]


# ===================================================================== PREREG
def sigma_over_mu(beta, d):
    """sd(R)/E[R] under the Beta(beta/2,(d-beta)/2) law, exactly."""
    return float(np.sqrt(2.0 * (d - beta) / (beta * (d + 2.0))))


def _decay_table():
    rows = []
    for d in EXT_D:
        s30 = sigma_over_mu(30, d)
        for b in EXT_BETAS:
            s = sigma_over_mu(b, d)
            rows.append((d, b, round(s, 5), round(s / s30, 4)))
    return rows


_DT = _decay_table()
_DT100 = {b: r for (dd, b, s, r) in _DT if dd == 100}
_DT140 = {b: r for (dd, b, s, r) in _DT if dd == 140}

PREREG_MD = """
## Part 1 -- Frozen pre-registration

Everything in this Part is fixed before any research number in this task is
computed.  It is stored as the constant `PREREG_MD` in `b2a.py`, its sha256 is
printed by the script before it touches a lattice, and `b2a.py --phase prereg`
writes it into this report as its own first act.  `b2a_results.json` carries the
same hash under `prereg_sha256`.  Nothing below was chosen after seeing data.

### 1.1 What is kept identical

The four cells `(d, beta)` in `{100,140} x {30,40}`, `k = d/2`, `q = 3329`; the
statistic `R = ||Q^T e||^2 / ||e||^2` with `Q` the orthonormal tail-`beta` GSO
frame; the frozen estimator `q_emp(p) = sort(R)[round(p*N)-1]` at `N = 2^20`, so
`k = 1024` at `p = 2^-10` and `k = 16` at `p = 2^-16`; the Haar null arm and its
seed family; the CBD_{eta=2} error draws and their seed; the 32 basis seeds; and
the null-arm-first discipline.  `P1` and `P2` are carried over verbatim from
`prediction_frozen.json` of `TASK-20260805-708b70`:

* **P1** -- on the real arm, in all four cells, `|r(2^-10) - 1| <= 0.05` and
  `|r(2^-16) - 1| <= 0.10`, judged on the pooled-over-8-bases quantile.
* **P2** -- on the real arm, the between-basis component of `Var(R)` is
  `<= 20%` of the total, in all four cells.

`E[R] = beta/d` is FORCED for every projector, reduced or not, and carries zero
information.  `Var(R) = 2 beta (d-beta) / (d^2 (d+2))` under the Beta law is
DERIVED here in advance; agreement with it is not a discovery.

### 1.2 The replacement sensitivity demonstration

`Q_t = QR( sqrt(1-t) * E_S + sqrt(t) * G )` at
`t in {0, 0.05, 0.10, 0.25, 0.50, 0.75, 1.00}`, where `E_S` is the `d x beta`
selector of a uniformly random `beta`-subset `S` of coordinates and `G` is
`d x beta` iid standard normal.  Per draw `j` the pair `(S_j, G_j)` is drawn
once and reused across all seven `t`, so the family is a path, not seven
unrelated arms.  `t = 0` gives a coordinate-aligned projector; `t = 1` gives a
Haar projector drawn independently of the null arm's.

This manipulates the object the null removes -- the provenance of the
projector -- which the superseded demonstration did not (DF-1).

### 1.3 Threshold, declared now, in SE-of-the-difference units

For any arm `A` compared against the Haar null arm, with `G_A = G_haar = 8`
draws and `sd` the between-draw sample sd (`ddof=1`) of `r(2^-10)`:

```
SE_diff(A) = sqrt( sd_A^2 / 8 + sd_haar^2 / 8 )
shift(A)   = mean_j r_A(2^-10) - mean_j r_haar(2^-10)
gate(A)    = |shift(A)| >= 4 * SE_diff(A)
```

This is the correction demanded by DF-2: the previous gate used the Haar arm's
own per-draw sd, the one arm whose between-draw location variance is
structurally near zero, which turned a nominal `4 s` into a ~2.0-2.5 sigma test.

### 1.4 Validity of the demonstration -- three conditions, declared now

* **G1 (high end).** `gate(t=0)` clears in all four cells.
* **G2 (low end).** `gate(t=1)` does NOT clear in any of the four cells.
  `t = 1` is a Haar projector drawn independently of the null arm's, so the two
  arms share a law and the gate must not fire.  **This is the condition the
  superseded demonstration could not have failed, and it is the reason this one
  can: an instrument that fires here is broken.**
* **G3 (monotonicity).** `mean_j r_A(2^-10)` is non-increasing across the seven
  `t` in every cell.

The demonstration is **VALID** iff `G1 and G2 and G3`.  If it is **INVALID**,
the outcome is an INSTRUMENT OUTCOME, no mathematical conclusion is recorded,
and the real arm is reported as measured but not interpreted.  A third branch is
declared explicitly, because a decision rule must partition the space of
outcomes and not the range of a quantity (DF-3): if `G1` holds, `G2` holds and
`G3` fails only at non-adjacent interior points within `1 * SE_diff`, the
outcome is **PARTIAL**, and is reported as PARTIAL rather than forced into
either branch.

The dynamic range actually spanned is reported as
`DR = mean r(t=0) - mean r(t=1)`, in absolute units and in units of
`SE_diff(t=0)`.

### 1.5 The Gaussian-error null of the null

Every arm is re-measured with an iid `N(0,1)` error in place of CBD_{eta=2}.
For a rotationally invariant error and ANY fixed rank-`beta` projector,
`R ~ Beta(beta/2,(d-beta)/2)` exactly.  Declared now:

* **N1** -- every arm under the Gaussian error returns `|r(2^-10) - 1| <= 0.05`
  and `|r(2^-16) - 1| <= 0.10`, the same tolerances as P1.
* **N2** -- under the Gaussian error, `gate(t=0)` does NOT clear.  Coordinate
  alignment produces no departure when the error is spherical.

`N1` or `N2` failing is instrument error and is reported as such; it is not a
result about lattices.

### 1.6 The falsifier: ~1/sqrt(beta) decay of the alignment departure

The parameter that should destroy an alignment departure is `beta`.  The
departure is a relative-dispersion effect: a coordinate-aligned `R` is
under-dispersed relative to Beta by the CBD kurtosis factor
`(E[e^4]-1)/2 = 0.75` in variance, and the lower-tail quantile ratio therefore
moves by an amount proportional, to leading order, to the Beta law's own
coefficient of variation

```
s(beta,d) = sd(R)/E[R] = sqrt( 2 (d - beta) / (beta (d + 2)) )
```

which is `~1/sqrt(beta)` at fixed `beta/d`.  Define, for an arm `A`,

```
D_A(beta,d)  = mean_j r_A(2^-10) - mean_j r_haar(2^-10)      (the departure)
Dn_A(beta,d) = D_A(beta,d) / s(beta,d)                       (normalised)
```

**Prediction, declared now:** `Dn_A` is approximately constant in `beta`, i.e.
`D_A(beta) / D_A(30)` tracks `s(beta)/s(30)`.  The predicted ratios, computed
from the formula alone:

| d | beta=30 | beta=40 | beta=50 | beta=60 |
|---|---|---|---|---|
| 100 | 1.0000 | @r100_40@ | @r100_50@ | @r100_60@ |
| 140 | 1.0000 | @r140_40@ | @r140_50@ | @r140_60@ |

**Tested at `beta in {30, 40, 50, 60}`** -- two values beyond `{30,40}` -- on
the tail-`beta` GSO frames of the BKZ-40 basis set at each `d`, on the LLL-only
and unreduced frames of the same bases, and on the coordinate-aligned (`t=0`)
projector.  Holding the reduction fixed at BKZ-40 while `beta` varies is
deliberate: it varies only the parameter the falsifier is about.

**Three-way verdict, declared now, per arm and per `d`:**

* **FALSIFIED** -- `D_A(60)/D_A(30) >= 0.90`.  The departure fails to decay
  when the parameter meant to destroy it doubles.  This is the canonical
  artifact tell and is recorded as one.
* **CONSISTENT** -- `D_A(60)/D_A(30)` lies within `+-25%` of the predicted
  ratio, i.e. in `[@lo100@, @hi100@]` at `d = 100` and `[@lo140@, @hi140@]` at
  `d = 140`.
* **NEITHER** -- decays, but not at the predicted rate.  Reported as NEITHER,
  never rounded into either of the other two.
* **NOT APPLICABLE** -- `D_A(30)` does not clear its own `4 * SE_diff` gate, so
  there is no departure to decay.  This branch is declared in advance because
  the superseded run's real arm had `r ~ 1.000`, and an arm with no departure
  must not be scored as though it had one.

### 1.7 What this task may not do

No status change, no interpretation beyond the declared verdicts, no claim
about ML-KEM security or any FIPS 203 parameter set, and no transport of any
number measured at `d <= 140, beta <= 60` to `beta = 606, d = 1420`.  The
beta-trend is four points at two `d`, not a law.  P1/P2 are not re-scored
against any rule other than the one frozen in BATCH-a51f91.
"""

_SUBS = {
    "r100_40": f"{_DT100[40]:.4f}", "r100_50": f"{_DT100[50]:.4f}",
    "r100_60": f"{_DT100[60]:.4f}",
    "r140_40": f"{_DT140[40]:.4f}", "r140_50": f"{_DT140[50]:.4f}",
    "r140_60": f"{_DT140[60]:.4f}",
    "lo100": f"{0.75 * _DT100[60]:.4f}", "hi100": f"{1.25 * _DT100[60]:.4f}",
    "lo140": f"{0.75 * _DT140[60]:.4f}", "hi140": f"{1.25 * _DT140[60]:.4f}",
}
for _k, _v in _SUBS.items():
    PREREG_MD = PREREG_MD.replace("@" + _k + "@", _v)

PREREG_SHA256 = hashlib.sha256(PREREG_MD.encode("utf-8")).hexdigest()


# ====================================================================== seeds
def seed_basis(d, beta, i):
    return 700000 + d * 1000 + beta * 10 + i            # identical to BATCH-a51f91


def seed_error(d):
    return 20260805 + d                                 # identical to BATCH-a51f91


def seed_haar(d, beta, j):
    return 900000 + d * 1000 + beta * 10 + j            # identical to BATCH-a51f91


def seed_graded(d, beta, j):
    return 500000 + d * 1000 + beta * 10 + j            # new in B2-A


def seed_gauss_error(d):
    return 20260806 + d                                 # new in B2-A


# ================================================================ error laws
_POPCNT4 = np.array([bin(v).count("1") for v in range(16)], dtype=np.int8)


def cbd_eta2(rng, n, d):
    r = rng.integers(0, 16, size=(n, d), dtype=np.uint8)
    return (_POPCNT4[r & 3] - _POPCNT4[r >> 2]).astype(np.int8)


# =========================================================== reduction worker
def reduce_one(job):
    """One q-ary basis; return the last BETA_MAX orthonormal tail-GSO columns at
    three reduction levels (raw, LLL, LLL+BKZ-beta) plus diagnostics."""
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
    # KN-TECH-14efa5: BKZ.DEFAULT_STRATEGY points at a path absent from the
    # wheel, so strategies are built in-process (pruning-free).
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


# ================================================================ statistics
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
    """R: (N,G).  All G columns share the SAME N error vectors."""
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
    """Threshold in units of the SE of the DIFFERENCE of the two arm means."""
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
            "cleared": bool(se > 0 and abs(shift) >= k * se)}


# ================================================================ projections
def project(Ef, n2, Q, n_draw, betap, chunk):
    """R[i,j] = ||Q_j^T e_i||^2 / ||e_i||^2 for j = 0..n_draw-1."""
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


def graded_frames(d, betap, n_draw, t):
    cols = []
    for j in range(n_draw):
        g = np.random.default_rng(seed_graded(d, betap, j))
        S = g.choice(d, size=betap, replace=False)     # same S_j, G_j for all t
        G = g.standard_normal((d, betap))
        E = np.zeros((d, betap))
        E[S, np.arange(betap)] = 1.0
        Mx = np.sqrt(1.0 - t) * E + np.sqrt(t) * G
        cols.append(np.linalg.qr(Mx)[0].astype(np.float32))
    return np.concatenate(cols, axis=1)


def tail_slice(Qfull, betap):
    """Qfull is the last BETA_MAX GSO columns; take its last betap columns."""
    return np.ascontiguousarray(Qfull[:, BETA_MAX - betap:])


def stack(frames, betap):
    return np.ascontiguousarray(np.concatenate(
        [tail_slice(f, betap) for f in frames], axis=1))


# ====================================================================== main
def cpu_seconds():
    a = resource.getrusage(resource.RUSAGE_SELF)
    b = resource.getrusage(resource.RUSAGE_CHILDREN)
    return (a.ru_utime + a.ru_stime + b.ru_utime + b.ru_stime)


def phase_prereg():
    body = ("# B2-A -- T2 instrument re-run with a sensitivity demonstration "
            "that can fail\n\n"
            "TASK-20260806-09ec68 / BATCH-436ddd / GOAL-MLKEM-005\n\n"
            "Executor artifact. Observations only.\n\n"
            + PREREG_BEGIN + "\n" + PREREG_MD + "\n" + PREREG_END + "\n")
    with open(REPORT_PATH, "w") as f:
        f.write(body)
    print("PRE-REGISTRATION WRITTEN")
    print("  path        :", REPORT_PATH)
    print("  prereg_sha256 (of PREREG_MD, the bytes between the markers):",
          PREREG_SHA256)
    print("  file_sha256 at freeze time:",
          hashlib.sha256(open(REPORT_PATH, "rb").read()).hexdigest())
    print("  written_utc :", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["prereg", "measure"], default="measure")
    ap.add_argument("--mode", choices=["full", "smoke"], default="full")
    ap.add_argument("--out", default=os.path.join(TASK_DIR, "b2a_results.json"))
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--core-seconds-budget", type=float, default=4000.0)
    args = ap.parse_args()

    if args.phase == "prereg":
        return phase_prereg()

    t_start = time.time()
    c_start = cpu_seconds()

    # ---- gate: the pre-registration is emitted before any research number ----
    print("=" * 78)
    print("FROZEN PRE-REGISTRATION (emitted before any lattice is touched)")
    print("  prereg_sha256 :", PREREG_SHA256)
    if os.path.exists(REPORT_PATH):
        raw = open(REPORT_PATH, "rb").read().decode("utf-8")
        if PREREG_BEGIN in raw and PREREG_END in raw:
            seg = raw.split(PREREG_BEGIN, 1)[1].split(PREREG_END, 1)[0]
            seg = seg[1:] if seg.startswith("\n") else seg
            seg = seg[:-1] if seg.endswith("\n") else seg
            match = hashlib.sha256(seg.encode("utf-8")).hexdigest() == PREREG_SHA256
            print("  report Part 1 matches PREREG_MD byte for byte:", match)
            if not match:
                print("ABORT: b2a_report.md Part 1 is not the frozen text.")
                return 2
        else:
            print("ABORT: b2a_report.md carries no frozen pre-registration.")
            return 2
    else:
        print("ABORT: run --phase prereg first.")
        return 2
    print("  gate          : |mean_A - mean_haar| >= 4 * SE(difference), 8 draws")
    print("  G1 t=0 clears / G2 t=1 does NOT clear / G3 monotone in t")
    print("  falsifier     : D(beta)/D(30) tracks s(beta)/s(30), tested to beta=60")
    print("  FORCED        : E[R] = beta/d for EVERY projector. Zero information.")
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
        "task_id": "TASK-20260806-09ec68",
        "batch_id": "BATCH-436ddd",
        "goal_id": "GOAL-MLKEM-005",
        "supersedes_instrument_of": "TASK-20260805-708b70 (BATCH-a51f91)",
        "governed_by": "DEC-20260805-4823db next_actions",
        "mode": args.mode,
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "prereg_sha256": PREREG_SHA256,
        "prereg_emitted_before_any_research_number": True,
        "prereg_text": PREREG_MD,
        "read_order": [
            "1. pre-registration emitted and hash-checked against b2a_report.md",
            "2. instrument checks (reduction reproduction, orthonormality, CBD pmf)",
            "3. GAUSSIAN-ERROR NULL OF THE NULL, every arm",
            "4. Haar null arm, P1/P2 on the null arm FIRST",
            "5. graded sensitivity demonstration, G1/G2/G3 adjudicated",
            "6. real / LLL-only / unreduced arms read only after 5",
            "7. beta-trend falsifier",
        ],
        "config": {"q": Q_MOD, "eta": ETA, "cells": cells, "graded_t": GRADED_T,
                   "ext_d": ext_d, "ext_bkz_blocksize": ext_bkz,
                   "ext_betas": ext_betas, "errors_per_cell": n_err,
                   "draws_per_arm": N_DRAW, "chunk": chunk,
                   "tail_levels": P_TAIL, "gate_k": GATE_K,
                   "gauss_arms": GAUSS_ARMS},
        "seed_scheme": {
            "fplll_basis_seed": "700000 + d*1000 + beta*10 + i  (identical to BATCH-a51f91)",
            "numpy_cbd_error_seed": "20260805 + d  (identical to BATCH-a51f91)",
            "numpy_haar_seed": "900000 + d*1000 + betap*10 + j  (identical to BATCH-a51f91 at betap = beta)",
            "numpy_graded_seed": "500000 + d*1000 + betap*10 + j  (new)",
            "numpy_gauss_error_seed": "20260806 + d  (new)",
        },
        "instrument_checks": {},
        "reductions": [],
        "cells": {},
        "beta_trend": {},
        "timings": {},
    }

    # ------------------------------------------------ stage A: reductions
    jobs = [(d, b, i) for (d, b) in cells for i in range(N_DRAW)]
    print(f"[stage A] {len(jobs)} reductions (raw + LLL + BKZ) on {args.workers} workers")
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

    # reproduction check against BATCH-a51f91 (the .npz cache is gone; the
    # SEEDS are the cache)
    prior = os.path.join(os.path.dirname(TASK_DIR), "..", "..", "BATCH-a51f91",
                         "tasks", "TASK-20260805-708b70", "results.json")
    prior = os.path.normpath(prior)
    if os.path.exists(prior) and args.mode == "full":
        pj = {m["tag"]: m for m in json.load(open(prior))["reductions"]}
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
        res["instrument_checks"]["reduction_reproduction_vs_BATCH_a51f91"] = {
            "n_compared": len(dev),
            "max_b0_norm_rel_dev": max(x["b0_norm_rel_dev"] for x in dev) if dev else None,
            "max_gso_slope_abs_dev": max(x["slope_abs_dev"] for x in dev) if dev else None,
            "note": ("The BATCH-a51f91 .npz reduction cache lived in an ephemeral "
                     "session scratchpad that no longer exists, so the reductions "
                     "were recomputed from the SAME seeds with the same fpylll "
                     "version. This check is what makes 'the same bases' a "
                     "verified statement rather than an assertion."),
            "per_tag": dev,
        }
        print("[stage A] reproduction vs BATCH-a51f91: max |b0| rel dev "
              f"{res['instrument_checks']['reduction_reproduction_vs_BATCH_a51f91']['max_b0_norm_rel_dev']}")

    # ------------------------------------------------ stages B/C, per cell
    for (d, beta) in cells:
        key = f"d{d}_b{beta}"
        used = cpu_seconds() - c_start
        if used > args.core_seconds_budget:
            res["aborted_reason"] = f"core-second budget exhausted before {key}"
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
                    "beta_params": {"a": a, "b": b},
                    "beta_quantiles": {f"p2em{int(round(-np.log2(p)))}": qb[p]
                                       for p in P_TAIL}},
                "arms_cbd": {}, "arms_gauss": {}}

        frames = {
            "unreduced": [FR[f"{key}_i{j}"]["unreduced"] for j in range(N_DRAW)],
            "lll_only": [FR[f"{key}_i{j}"]["lll_only"] for j in range(N_DRAW)],
            "real_bkz": [FR[f"{key}_i{j}"]["real_bkz"] for j in range(N_DRAW)],
        }
        Qs = {k: stack(v, beta) for k, v in frames.items()}
        Qs["haar_null"] = haar_frames(d, beta, N_DRAW)
        for t in GRADED_T:
            Qs[f"graded_t{t:.2f}"] = graded_frames(d, beta, N_DRAW, t)

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
                    # n2 from the SAME float32 values the projection consumes
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

        # -------- null of the null, adjudicated
        gh = cell["arms_gauss"]["haar_null"]
        nn = {"tolerances": {"p2em10": 0.05, "p2em16": 0.10}, "arms": {}}
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
        c0 = "graded_t0.00"
        nn["N2_coord_gate_does_not_clear"] = (
            bool(not nn["arms"][c0]["gate_vs_gauss_haar"]["cleared"])
            if c0 in nn["arms"] else None)
        nn["verdict"] = ("PASS" if (nn["N1_all_arms_pass"] and
                                    nn["N2_coord_gate_does_not_clear"])
                         else "FAIL -- INSTRUMENT ERROR, not a result")
        cell["null_of_the_null"] = nn
        print(f"  [null-of-null]  {key} N1={nn['N1_all_arms_pass']} "
              f"N2={nn['N2_coord_gate_does_not_clear']} -> {nn['verdict']}")

        # -------- null arm first: P1/P2 on the Haar arm before the real arm
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
        print(f"  [null-arm-first] {key} haar_null "
              f"P1={cell['verdict_on_the_null_arm_FIRST']['P1']['pass']} "
              f"P2={cell['verdict_on_the_null_arm_FIRST']['P2']['pass']} "
              "(P1 here passes BY CONSTRUCTION; it is the unit test that is NOT "
              "a control)")

        # -------- the sensitivity demonstration
        gr = {}
        for t in GRADED_T:
            nm = f"graded_t{t:.2f}"
            gr[f"{t:.2f}"] = {
                "t": t,
                "ratio_2em10_mean": cell["arms_cbd"][nm]["ratio_p2em10_over_draws"]["mean"],
                "ratio_2em10_sd": cell["arms_cbd"][nm]["ratio_p2em10_over_draws"]["sd"],
                "ratio_2em16_mean": cell["arms_cbd"][nm]["ratio_p2em16_over_draws"]["mean"],
                "gate": gate(cell["arms_cbd"][nm], hcbd)}
        means = [gr[f"{t:.2f}"]["ratio_2em10_mean"] for t in GRADED_T]
        diffs = [means[i + 1] - means[i] for i in range(len(means) - 1)]
        G1 = gr["0.00"]["gate"]["cleared"]
        G2 = not gr["1.00"]["gate"]["cleared"]
        G3 = all(x <= 0 for x in diffs)
        strict = all(x < 0 for x in diffs)
        se0 = gr["0.00"]["gate"]["se_of_difference"]
        viol = [{"from_t": GRADED_T[i], "to_t": GRADED_T[i + 1], "increase": diffs[i],
                 "increase_in_se0": diffs[i] / se0 if se0 > 0 else None}
                for i in range(len(diffs)) if diffs[i] > 0]
        partial = (G1 and G2 and not G3
                   and all(abs(v["increase_in_se0"]) <= 1.0 for v in viol)
                   and all(abs(GRADED_T.index(viol[i]["to_t"])
                               - GRADED_T.index(viol[i - 1]["to_t"])) > 1
                           for i in range(1, len(viol))))
        sens = {
            "family": "Q_t = QR( sqrt(1-t)*E_S + sqrt(t)*G ), same (S_j,G_j) across t",
            "t_values": GRADED_T,
            "per_t": gr,
            "successive_differences_in_mean_ratio_2em10": diffs,
            "G1_high_end_t0_gate_clears": bool(G1),
            "G2_low_end_t1_gate_does_not_clear": bool(G2),
            "G3_monotone_non_increasing_in_t": bool(G3),
            "monotone_strictly_decreasing": bool(strict),
            "monotonicity_violations": viol,
            "dynamic_range_abs": means[0] - means[-1],
            "dynamic_range_in_se_of_difference_at_t0":
                (means[0] - means[-1]) / se0 if se0 > 0 else None,
            "verdict": ("VALID" if (G1 and G2 and G3)
                        else ("PARTIAL" if partial else "INVALID")),
        }
        cell["sensitivity_demonstration"] = sens
        print(f"  [sensitivity]   {key} G1={G1} G2={G2} G3={G3} -> {sens['verdict']}"
              f"  t0 shift {gr['0.00']['gate']['shift_in_units_of_se_of_difference']:.1f} SE,"
              f"  t1 shift {gr['1.00']['gate']['shift_in_units_of_se_of_difference']:.1f} SE")

        # -------- only now: the real / lll / unreduced arms
        cell["verdicts_after_the_demonstration"] = {
            nm: verdict(cell["arms_cbd"][nm])
            for nm in ("real_bkz", "lll_only", "unreduced")}
        cell["gates_vs_haar_null"] = {
            nm: gate(cell["arms_cbd"][nm], hcbd)
            for nm in ("real_bkz", "lll_only", "unreduced", "graded_t0.00")}
        for nm in ("real_bkz", "lll_only", "unreduced"):
            v = cell["verdicts_after_the_demonstration"][nm]
            g_ = cell["gates_vs_haar_null"][nm]
            print(f"  [{nm:>10}]   {key} P1={v['P1']['pass']} P2={v['P2']['pass']} "
                  f"r10={v['P1']['ratio_2em10_pooled']:.5f} "
                  f"shift={g_['shift_in_units_of_se_of_difference']:.1f} SE "
                  f"gate={g_['cleared']}")
        sys.stdout.flush()
        res["cells"][key] = cell
        del Qs, frames

    # ------------------------------------------------ stage D: beta trend
    b_lo, b_hi = ext_betas[0], ext_betas[-1]
    for d in ext_d:
        key = f"d{d}_b{ext_bkz}"
        if f"{key}_i0" not in FR:
            continue
        used = cpu_seconds() - c_start
        if used > args.core_seconds_budget:
            res.setdefault("aborted_reason",
                           f"core-second budget exhausted before beta-trend d={d}")
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
        for bp in ext_betas:
            aa, bb = bp / 2.0, (d - bp) / 2.0
            qbp = {p: float(betaincinv(aa, bb, p)) for p in P_TAIL}
            rb = f"real_bkz{ext_bkz}"
            Q = {"unreduced": stack([FR[f"{key}_i{j}"]["unreduced"] for j in range(N_DRAW)], bp),
                 "lll_only": stack([FR[f"{key}_i{j}"]["lll_only"] for j in range(N_DRAW)], bp),
                 rb: stack([FR[f"{key}_i{j}"]["real_bkz"] for j in range(N_DRAW)], bp),
                 "haar_null": haar_frames(d, bp, N_DRAW),
                 "coord_t0": graded_frames(d, bp, N_DRAW, 0.0)}
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
                              "gate_vs_haar": gate(arms[nm], hh)}
                         for nm in Q}}
            print(f"  [beta-trend] d={d} beta={bp}: " + "  ".join(
                f"{nm}={tr[str(bp)]['arms'][nm]['ratio_2em10_mean']:.5f}"
                for nm in Q))
            sys.stdout.flush()
        del Ef, n2

        # falsifier adjudication
        s_lo = sigma_over_mu(b_lo, d)
        fal = {}
        for nm in ("unreduced", "lll_only", rb, "coord_t0"):
            glo = tr[str(b_lo)]["arms"][nm]["gate_vs_haar"]
            D = {str(bp): tr[str(bp)]["arms"][nm]["gate_vs_haar"]["shift_arm_minus_haar"]
                 for bp in ext_betas}
            pred = {str(bp): sigma_over_mu(bp, d) / s_lo for bp in ext_betas}
            if not glo["cleared"]:
                v = (f"NOT APPLICABLE -- D(beta={b_lo}) does not clear its own "
                     "4*SE gate, so there is no departure to decay")
                ratio = None
            else:
                ratio = D[str(b_hi)] / D[str(b_lo)]
                if ratio >= 0.90:
                    v = "FALSIFIED -- fails to decay"
                elif 0.75 * pred[str(b_hi)] <= ratio <= 1.25 * pred[str(b_hi)]:
                    v = "CONSISTENT"
                else:
                    v = "NEITHER -- decays, but not at the predicted rate"
            fal[nm] = {"beta_lo": b_lo, "beta_hi": b_hi,
                       "departure_D_by_beta": D,
                       "normalised_Dn_by_beta":
                           {k2: (D[k2] / sigma_over_mu(int(k2), d)) for k2 in D},
                       "predicted_ratio_to_beta_lo": pred,
                       "observed_ratio_Dhi_over_Dlo": ratio,
                       "Dlo_gate_cleared": glo["cleared"],
                       "Dlo_shift_in_se": glo["shift_in_units_of_se_of_difference"],
                       "verdict": v}
            print(f"  [falsifier] d={d} {nm}: {v}"
                  + (f"  D{b_hi}/D{b_lo}={ratio:.4f} vs predicted "
                     f"{pred[str(b_hi)]:.4f}" if ratio is not None else ""))
        res["beta_trend"][f"d{d}"] = {
            "reduction_held_fixed_at": f"LLL + BKZ-{ext_bkz}",
            "why_fixed": ("The falsifier varies beta only. Re-reducing at "
                          "BKZ-50/60 would vary reduction strength at the same "
                          "time and is out of budget besides; the measured BKZ "
                          "times in `reductions` show the cost."),
            "by_beta": tr, "falsifier": fal}

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
    except Exception:
        pass

    with open(args.out, "w") as f:
        json.dump(res, f, indent=1, sort_keys=False)
    print(f"[done] {args.out} wall={res['timings']['total_wall_seconds']}s "
          f"cpu={res['timings']['total_cpu_core_seconds']}s "
          f"rss={res['peak_rss_gb']}GB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
