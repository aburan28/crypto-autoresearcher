#!/usr/bin/env python3
"""Calibration harness for the v2 amendment to EXP-HQC-982268.

TASK-20260806-dbadc8 (executor) / BATCH-c5703d / GOAL-HQC-001.

WHAT THIS SCRIPT IS
-------------------
It sizes decision rules.  Every random draw it makes is from an EXPLICIT,
FULLY SPECIFIED NULL LAW -- S ~ Binomial(n_e, q) with q a Stage-A-measured
number -- or from an explicitly declared ALTERNATIVE family used only to
measure power.  It constructs no HQC object: no ring, no fixed-weight
sampler, no truncation, no Reed-Muller decoder, no error vector.

WHAT THIS SCRIPT DELIBERATELY DOES NOT DO
-----------------------------------------
It does NOT compute log2_A_k or log2_A_m on any space-(T) arm, and it does
not compute any quantity from which one follows.  In particular it never
forms Var(S) on a (T) S-histogram: on {0..n_e},

    E[C(S,2)] = (E[S^2] - E[S]) / 2   =>   A_2 = mubar_2 / q^2

is a two-line function of Var(S), so evaluating the (T) second moment would
BE the k=2 measurement.  TASK-20260806-dbadc8 is not authorized to produce
it.  Where a statistic of this script needs that second moment, the script
says so and stops, rather than computing it (see phase R2).

Only the FIRST moments of the (T) arms are read from the committed run
record -- q_hat and the per-block failure counts -- both of which are
chartered Stage-A diagnostics already published in
experiments/EXP-HQC-982268/runs/RUN-HQC-982268-STAGEA-a/raw-result.json.

Nothing here is a statement about HQC, about assumption A17 or A5, about any
decoding-failure rate, or about any standardized HQC parameter set.
Claim tier: TOY, hard ceiling.  A crash or budget exhaustion is an
INFRASTRUCTURE outcome, never a mathematical result (AGENTS.md rule 5).

THE COMPUTATIONAL TRICK THAT MAKES THIS AFFORDABLE
--------------------------------------------------
Every statistic in the contract's null arms is a function of the histogram
of S over n_e+1 bins (and, for the jackknife, of B=200 per-batch histograms).
For T i.i.d. trials with S ~ Binomial(n_e,q), that histogram is EXACTLY
Multinomial(T, pmf).  So a null replicate at T = 1e8 costs one multinomial
draw over n_e+1 categories, not 1e8 trials.  The calibration is therefore
O(1) in T and exact in distribution -- not an approximation.

Re-run:
    PYTHONDONTWRITEBYTECODE=1 python3 calibration.py --out calibration_results.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import platform
import resource
import subprocess
import sys
import time
from fractions import Fraction

import numpy as np

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", "..", ".."))
STAGE_A = os.path.join(
    REPO, "coordination", "goals", "GOAL-HQC-001", "batches", "BATCH-6fddee",
    "tasks", "TASK-20260806-64b506", "stage_a.py")
RAW_RESULT = os.path.join(
    REPO, "experiments", "EXP-HQC-982268", "runs", "RUN-HQC-982268-STAGEA-a",
    "raw-result.json")

N_JACK_BATCHES = 200          # stage_a.N_JACK_BATCHES, verbatim
NOMINAL_ALPHA = 0.0026997960632601866   # two-sided normal tail at 3 sigma
MASTER_SEED = 20260806        # this task's id date; fixed before any draw


# --------------------------------------------------------------------------
# import the EXACT estimator under test
# --------------------------------------------------------------------------

def load_stage_a():
    spec = importlib.util.spec_from_file_location("stage_a_under_test", STAGE_A)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --------------------------------------------------------------------------
# vectorised re-implementation of the estimator, verified against stage_a
# --------------------------------------------------------------------------

def comb_col(n_e: int, k: int) -> np.ndarray:
    return np.array([float(math.comb(s, k)) if s >= k else 0.0
                     for s in range(n_e + 1)])


def log2A_vec(H: np.ndarray, n_e: int, k: int) -> np.ndarray:
    """log2 Ahat_k for each histogram along the last axis of H.

    Identical algebra to stage_a.log2_A_from_hist:
        q   = (sum_s s*H_s) / T / n_e
        mu  = (sum_s C(s,k)*H_s) / T / C(n_e,k)
        out = log2(mu) - k*log2(q)
    """
    Hf = np.asarray(H, dtype=np.float64)
    T = Hf.sum(axis=-1)
    svec = np.arange(n_e + 1, dtype=np.float64)
    ck = comb_col(n_e, k)
    with np.errstate(divide="ignore", invalid="ignore"):
        q = (Hf @ svec) / T / n_e
        mu = (Hf @ ck) / T / float(math.comb(n_e, k))
        ok = (q > 0) & (mu > 0) & (T > 0)
        out = np.where(ok, np.log2(np.where(mu > 0, mu, 1.0))
                       - k * np.log2(np.where(q > 0, q, 1.0)), np.nan)
    return out


def jack_vec(BH: np.ndarray, n_e: int, k: int):
    """Point estimate and delete-one jackknife SE over the B batches.

    Identical algebra to stage_a.jackknife_log2_A with bh = BH[r].
    BH has shape (R, B, n_e+1).  Returns (point[R], se[R]).
    """
    total = BH.sum(axis=1)
    point = log2A_vec(total, n_e, k)
    loo = total[:, None, :] - BH
    vals = log2A_vec(loo, n_e, k)
    b = BH.shape[1]
    mean = np.nanmean(vals, axis=1)
    se = np.sqrt((b - 1) / b * np.nansum((vals - mean[:, None]) ** 2, axis=1))
    bad = np.isnan(vals).any(axis=1)
    se = np.where(bad, np.nan, se)
    return point, se


# --------------------------------------------------------------------------
# null and alternative laws
# --------------------------------------------------------------------------

def binom_pmf(n_e: int, q: float) -> np.ndarray:
    p = np.array([math.comb(n_e, s) * q ** s * (1.0 - q) ** (n_e - s)
                  for s in range(n_e + 1)], dtype=np.float64)
    return p / p.sum()


def mixture_pmf(n_e: int, q: float, eps: float, q1: float) -> np.ndarray:
    """Two-point latent common-mode mixture: with prob eps the blocks are
    i.i.d. Bernoulli(q1), otherwise i.i.d. Bernoulli(q0), with the overall
    marginal held at q.  This is the M+ (common-mode) mechanism the contract
    names.  It is ONE declared alternative family, not a general alternative."""
    q0 = (q - eps * q1) / (1.0 - eps)
    if not (0.0 < q0 < 1.0 and 0.0 < q1 < 1.0):
        return None
    return eps * binom_pmf(n_e, q1) + (1.0 - eps) * binom_pmf(n_e, q0)


def mixture_log2A(n_e: int, q: float, eps: float, q1: float, k: int):
    q0 = (q - eps * q1) / (1.0 - eps)
    if not (0.0 < q0 < 1.0 and 0.0 < q1 < 1.0):
        return None
    a = (eps * q1 ** k + (1.0 - eps) * q0 ** k) / q ** k
    return math.log2(a)


def solve_mixture_for_effect(n_e: int, q: float, eps: float, k: int,
                             target_log2A: float):
    """Find q1 > q giving log2 A_k = target (monotone increasing in q1)."""
    lo, hi = q, min(1.0 - 1e-12, q / eps - 1e-12)
    if mixture_log2A(n_e, q, eps, hi, k) is None:
        return None
    if mixture_log2A(n_e, q, eps, hi, k) < target_log2A:
        return None
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        v = mixture_log2A(n_e, q, eps, mid, k)
        if v is None or v < target_log2A:
            lo = mid
        else:
            hi = mid
    return hi


# --------------------------------------------------------------------------
# draw helpers
# --------------------------------------------------------------------------

def draw_totals(rng, T: int, pmf: np.ndarray, R: int, chunk: int = 50000):
    """R independent histograms of T i.i.d. draws from pmf, in chunks."""
    i = 0
    while i < R:
        j = min(R, i + chunk)
        yield rng.multinomial(T, pmf, size=(j - i))
        i = j


def log2A_samples(rng, T: int, pmf: np.ndarray, R: int, n_e: int, ks):
    """R independent null/alternative replicates of log2 Ahat_k, for every k
    in ks, drawn from ONE set of histograms.  Memory is O(R * |ks|), not
    O(R * n_e)."""
    acc = {k: [] for k in ks}
    for H in draw_totals(rng, T, pmf, R):
        for k in ks:
            acc[k].append(log2A_vec(H, n_e, k))
    return {k: np.concatenate(v) for k, v in acc.items()}


def draw_batched(rng, T: int, pmf: np.ndarray, R: int, B: int, chunk: int = 250):
    """R independent (B, n_e+1) batch-histogram arrays, B batches of T//B
    trials each with the remainder placed in batch 0.  Exactly the law of
    stage_a.batch_hists applied to T i.i.d. trials."""
    tb = T // B
    rem = T - tb * B
    for i in range(0, R, chunk):
        r = min(chunk, R - i)
        BH = rng.multinomial(tb, pmf, size=(r, B))
        if rem:
            BH[:, 0, :] += rng.multinomial(rem, pmf, size=(r,))
        yield BH


def wilson(k: int, n: int, z: float = 1.959963985):
    if n == 0:
        return None, None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


# --------------------------------------------------------------------------
# parameter sets: every number below is copied from the committed record
# --------------------------------------------------------------------------

def load_committed():
    with open(RAW_RESULT) as fh:
        raw = json.load(fh)
    sets = {}
    for sid, d in raw["diagnostics_T"].items():
        sets[sid] = dict(
            id=sid,
            q_hat_T=d["q_hat"],                       # (T)-arm FIRST moment
            T_stage_a=d["trials"],
            p_hat=d["p_hat"],
            gamma_hat=d["gamma_hat"],
            gamma_hat_se=d["gamma_hat_se_approx"],
            D3_cap=d["D3"]["cap"],
            D3_max_observed=d["D3"]["max_w_etilde_observed"],
            block_failure_counts=d["block_failure_counts"],
            trials_per_core_second=d["trials_per_core_second"],
            tie_rate=d["tie_rate"],
        )
    for sid, d in raw["null_M"].items():
        sets[sid]["nullM_q_hat"] = d["q_hat"]
        sets[sid]["nullM_T"] = d["trials"]
        sets[sid]["nullM_gamma_hat"] = d["gamma_hat"]
    return raw, sets


STATIC = {
    # from experiments/EXP-HQC-982268/specification.yaml, verbatim
    "PS-A":  dict(n_e=46, m=16, N=17664, T_alloc=100_000_000, stage="stage_B1_PS_A",
                  modelled_core_seconds=33500, k_report=[2, 3, 4], k_sd=3,
                  q_for_sizing=0.0004993,
                  contract_SE_at_allocated_T={2: 0.0092, 3: 0.108}),
    "PS-R1": dict(n_e=46, m=16, N=5888,  T_alloc=100_000_000, stage="stage_B2_PS_R1",
                  modelled_core_seconds=11700, k_report=[2, 6, 9, 11, 14, 16, 18],
                  k_sd=16, q_for_sizing=0.2306,
                  contract_SE_at_allocated_T={16: 0.0321}),
    "PS-R3": dict(n_e=56, m=17, N=7168,  T_alloc=20_000_000,  stage="stage_B3_PS_R3",
                  modelled_core_seconds=2940, k_report=[2, 10, 17, 22, 25],
                  k_sd=17, q_for_sizing=0.3704,
                  contract_SE_at_allocated_T={17: 0.008}),
    "PS-R5": dict(n_e=90, m=30, N=11520, T_alloc=20_000_000,  stage="stage_B4_PS_R5",
                  modelled_core_seconds=4940, k_report=[2, 15, 30, 35],
                  k_sd=30, q_for_sizing=0.473,
                  contract_SE_at_allocated_T={30: 0.0259}),
}


# ==========================================================================
# PHASE 0 -- self-test: the vectorised estimator must equal stage_a's
# ==========================================================================

def phase0_selftest(sa, rng):
    out = {"purpose": "the sizes measured below are sizes of stage_a.py's OWN "
                      "rule, so the vectorised re-implementation must agree "
                      "with stage_a.log2_A_from_hist / jackknife_log2_A"}
    rows = []
    for sid, st in STATIC.items():
        n_e = st["n_e"]
        q = 0.25 if sid != "PS-A" else 0.002
        pmf = binom_pmf(n_e, q)
        BH = rng.multinomial(5000, pmf, size=(3, N_JACK_BATCHES))
        for k in (2, 5, 9):
            if k > n_e:
                continue
            mine_pt, mine_se = jack_vec(BH, n_e, k)
            for r in range(BH.shape[0]):
                pt, se, _b, _n = sa.jackknife_log2_A(BH[r], n_e, k)
                if pt is None:
                    continue
                dp = abs(pt - mine_pt[r])
                ds = (abs(se - mine_se[r]) if se is not None
                      and not math.isnan(mine_se[r]) else 0.0)
                rows.append(dict(set=sid, k=k, rep=r,
                                 abs_diff_point=dp, abs_diff_se=ds))
    out["max_abs_diff_point"] = max(r["abs_diff_point"] for r in rows)
    out["max_abs_diff_se"] = max(r["abs_diff_se"] for r in rows)
    out["n_comparisons"] = len(rows)
    out["verdict"] = ("AGREES" if out["max_abs_diff_point"] < 1e-12
                      and out["max_abs_diff_se"] < 1e-12 else "DISAGREES")
    return out


# ==========================================================================
# PHASE 1 -- A17 <=> Binomial: what the calibration null actually is
# ==========================================================================

def phase1_null_identity():
    """A_k = 1 for k = 1..n_e  <=>  S ~ Binomial(n_e, q) EXACTLY.

    Factorial moments E[(S)_k], k = 0..n_e, determine a distribution on
    {0..n_e} by a triangular linear system.  A_k = 1 for every k pins every
    factorial moment to the binomial value, hence pins the pmf.  Verified
    numerically by inverting the system.
    """
    out = {"claim": "A_k = 1 for all k in 1..n_e  <=>  S ~ Bin(n_e, q); "
                    "hence calibrating INV-NULL against Bin(n_e, q_hat) is "
                    "not a modelling approximation, it is the frozen "
                    "prediction's own full content",
           "caveat": "the contract measures k <= k_max < n_e, so a rule "
                     "calibrated this way tests a SUB-FAMILY of A17; the "
                     "reference law is exact, the coverage is partial"}
    rows = []
    for n_e, q in ((10, 0.3), (12, 0.07), (8, 0.55)):
        # target factorial moments of Bin(n_e,q): E[C(S,k)] = C(n_e,k) q^k
        M = np.array([[float(math.comb(s, k)) for s in range(n_e + 1)]
                      for k in range(n_e + 1)])
        rhs = np.array([float(math.comb(n_e, k)) * q ** k
                        for k in range(n_e + 1)])
        pmf_rec = np.linalg.solve(M, rhs)
        pmf_true = binom_pmf(n_e, q)
        rows.append(dict(n_e=n_e, q=q,
                         max_abs_pmf_diff=float(np.max(np.abs(
                             pmf_rec - pmf_true)))))
    out["reconstructions"] = rows
    out["max_abs_pmf_diff_overall"] = max(r["max_abs_pmf_diff"] for r in rows)
    out["verdict"] = ("CONFIRMED" if out["max_abs_pmf_diff_overall"] < 1e-9
                      else "NOT CONFIRMED")
    return out


# ==========================================================================
# PHASE 2 -- realized size of the CURRENT rule |log2 Ahat_k| > 3*SE_jack
# ==========================================================================

def wald_size(rng, n_e, q, T, ks, R, B=N_JACK_BATCHES):
    pmf = binom_pmf(n_e, q)
    acc = {k: dict(fire=0, n=0, pts=[], ses=[]) for k in ks}
    for BH in draw_batched(rng, T, pmf, R, B):
        for k in ks:
            pt, se = jack_vec(BH, n_e, k)
            good = np.isfinite(pt) & np.isfinite(se) & (se > 0)
            acc[k]["n"] += int(good.sum())
            acc[k]["fire"] += int((np.abs(pt[good]) > 3.0 * se[good]).sum())
            acc[k]["pts"].append(pt[good])
            acc[k]["ses"].append(se[good])
    rows = []
    for k in ks:
        a = acc[k]
        if a["n"] == 0:
            rows.append(dict(k=k, evaluable=False,
                             reason="estimator undefined on every replicate "
                                    "(no trial reached S >= k)"))
            continue
        pts = np.concatenate(a["pts"])
        ses = np.concatenate(a["ses"])
        lo, hi = wilson(a["fire"], a["n"])
        rows.append(dict(
            k=k, evaluable=True, replicates=a["n"], firings=a["fire"],
            realized_size=a["fire"] / a["n"],
            realized_size_ci95=[lo, hi],
            nominal_size=NOMINAL_ALPHA,
            size_ratio_to_nominal=(a["fire"] / a["n"]) / NOMINAL_ALPHA,
            null_mean_log2A=float(pts.mean()),
            null_sd_log2A=float(pts.std(ddof=1)),
            mean_SE_jack=float(ses.mean()),
            sd_over_meanSE=float(pts.std(ddof=1) / ses.mean()),
            corr_absdev_SEjack=float(np.corrcoef(
                np.abs(pts - pts.mean()), ses)[0, 1]),
        ))
    return rows


# ==========================================================================
# PHASE 3 -- INV-NULL-v2: Monte-Carlo-calibrated critical region
# ==========================================================================

def calibrated_rule(rng, n_e, q, T, ks, n_cal, n_val, alpha=NOMINAL_ALPHA):
    """Freeze [c_lo, c_hi] as the equal-tailed alpha/2 empirical quantiles of
    log2 Ahat_k under S ~ Bin(n_e, q) at T, from n_cal draws.  Then MEASURE
    the realized size on n_val INDEPENDENT draws.  No jackknife anywhere."""
    pmf = binom_pmf(n_e, q)
    cal = log2A_samples(rng, T, pmf, n_cal, n_e, ks)
    val = log2A_samples(rng, T, pmf, n_val, n_e, ks)
    rows = []
    for k in ks:
        c = cal[k]
        v = val[k]
        cg = c[np.isfinite(c)]
        vg = v[np.isfinite(v)]
        if cg.size < 1000 or vg.size == 0:
            rows.append(dict(k=k, evaluable=False,
                             reason="fewer than 1000 finite calibration "
                                    "replicates: the estimator is undefined "
                                    "too often at this (T, q, k)",
                             finite_calibration_replicates=int(cg.size)))
            continue
        c_lo = float(np.quantile(cg, alpha / 2.0))
        c_hi = float(np.quantile(cg, 1.0 - alpha / 2.0))
        fire = int(((vg < c_lo) | (vg > c_hi)).sum())
        # undefined replicates are counted as non-firing but reported
        lo, hi = wilson(fire, vg.size)
        rows.append(dict(
            k=k, evaluable=True,
            c_lo=c_lo, c_hi=c_hi,
            width_bits=c_hi - c_lo,
            null_median=float(np.median(cg)),
            null_mean=float(cg.mean()),
            null_sd=float(cg.std(ddof=1)),
            equivalent_z_threshold_lo=float((c_lo - cg.mean())
                                            / cg.std(ddof=1)),
            equivalent_z_threshold_hi=float((c_hi - cg.mean())
                                            / cg.std(ddof=1)),
            calibration_replicates=int(cg.size),
            validation_replicates=int(vg.size),
            undefined_validation_replicates=int(v.size - vg.size),
            firings=fire,
            realized_size_out_of_sample=fire / vg.size,
            realized_size_ci95=[lo, hi],
            nominal_size=alpha,
        ))
    return rows


def q_sensitivity(rng, n_e, q, T, ks, n_cal, dq_rel):
    """How far do the frozen critical values move if the true q differs from
    q_hat by the stated relative amount?"""
    rows = []
    for sgn in (-1.0, +1.0):
        qq = q * (1.0 + sgn * dq_rel)
        pmf = binom_pmf(n_e, qq)
        cal = log2A_samples(rng, T, pmf, n_cal, n_e, ks)
        for k in ks:
            cg = cal[k][np.isfinite(cal[k])]
            if cg.size < 1000:
                continue
            rows.append(dict(k=k, q_used=qq, rel_shift=sgn * dq_rel,
                             c_lo=float(np.quantile(cg, NOMINAL_ALPHA / 2)),
                             c_hi=float(np.quantile(cg, 1 - NOMINAL_ALPHA / 2))))
    return rows


# ==========================================================================
# PHASE 4 -- power of the calibrated rule against a declared alternative
# ==========================================================================

def power_curve(rng, n_e, q, T, k, c_lo, c_hi, eps, targets, R):
    rows = []
    for tgt in targets:
        q1 = solve_mixture_for_effect(n_e, q, eps, k, tgt)
        if q1 is None:
            rows.append(dict(target_log2A=tgt, reachable=False,
                             reason="alternative family cannot reach this "
                                    "effect size at this eps"))
            continue
        pmf = mixture_pmf(n_e, q, eps, q1)
        achieved = mixture_log2A(n_e, q, eps, q1, k)
        v = log2A_samples(rng, T, pmf, R, n_e, [k])[k]
        vg = v[np.isfinite(v)]
        if vg.size == 0:
            continue
        rej = int(((vg < c_lo) | (vg > c_hi)).sum())
        rows.append(dict(target_log2A=tgt, reachable=True,
                         achieved_log2A_exact=achieved,
                         eps=eps, q1=q1,
                         replicates=int(vg.size), rejections=rej,
                         power=rej / vg.size))
    return rows


# ==========================================================================
# PHASE 5 -- R4: allocation arithmetic at the MEASURED q_hat
# ==========================================================================

def t_stab(n_e, q, k, threshold=30.0):
    pmf = binom_pmf(n_e, q)
    contrib = np.array([pmf[s] * math.comb(s, k) if s >= k else 0.0
                        for s in range(n_e + 1)])
    tot = contrib.sum()
    if tot <= 0:
        return None, None
    s90 = int(np.searchsorted(np.cumsum(contrib), 0.90 * tot))
    tail = float(pmf[s90:].sum())
    return s90, (threshold / tail if tail > 0 else None)


def rel_variance_V(n_e, q, k):
    try:
        s = sum(math.comb(k, j) * math.comb(n_e - k, j) * q ** (k + j)
                for j in range(k + 1))
        v = s / (math.comb(n_e, k) * q ** (2 * k)) - 1.0
        return v if math.isfinite(v) else None
    except (OverflowError, ZeroDivisionError, ValueError):
        return None


def measured_sd_scaling(rng, n_e, q, k, Ts, R):
    rows = []
    pmf = binom_pmf(n_e, q)
    for T in Ts:
        v = log2A_samples(rng, int(T), pmf, R, n_e, [k])[k]
        vg = v[np.isfinite(v)]
        if vg.size < 100:
            rows.append(dict(T=float(T), evaluable=False,
                             finite_replicates=int(vg.size)))
            continue
        Vform = rel_variance_V(n_e, q, k)
        se_form = (math.sqrt(Vform / T) / math.log(2)) if Vform else None
        rows.append(dict(T=float(T), replicates=int(vg.size),
                         measured_sd=float(vg.std(ddof=1)),
                         measured_mean=float(vg.mean()),
                         contract_formula_SE=se_form,
                         ratio_measured_over_formula=(
                             float(vg.std(ddof=1)) / se_form
                             if se_form else None)))
    return rows


# ==========================================================================
# PHASE 6 -- R2: CTRL-POSHOM, positional-homogeneity control
# ==========================================================================

def poshom(rng, sid, n_e, counts, T, q_hat, R_null, defect_grid):
    """Clause (a): block-marginal positional homogeneity.

    FORCED VALUE (analytic, exact, stated before any number is computed):
      e'' = x*r_2 - r_1*y + e in R = F_2[X]/(X^n - 1) satisfies
      e'' =d= X^s * e'' for every s in Z_n, because (X^s x, X^s y, X^s e,
      r_1, r_2) has the same law as (x, y, e, r_1, r_2).  Block j occupies
      coordinates [j*L, (j+1)*L) with L = n_2*dup and n_e*L = N < n, so the
      block-j window is the block-0 window shifted by s = j*L, a legal ring
      shift.  Hence  E[F_j] = q  for EVERY j, exactly.

      Q_raw := sum_j (n_j - nbar)^2 / (T * q_hat * (1 - q_hat)),
      with n_j the per-block failure count.  Under positional homogeneity
      AND independent blocks, E[Q_raw] = n_e - 1.

    THE CALIBRATION CONSTANT THIS TASK MAY NOT COMPUTE.  With dependent
    blocks, E[Q_raw] = (n_e - 1) * (1 - c/v), c = Cov(F_j, F_j'), v = q(1-q).
    c is a (T)-arm second moment, and on {0..n_e}
        A_2 = mubar_2/q^2 = [Var(S) + (n_e q)^2 - n_e q] / (2 C(n_e,2) q^2),
    so evaluating c WOULD BE the k=2 measurement.  TASK-20260806-dbadc8 is
    not authorized to produce it.  Q_raw is therefore reported against the
    INDEPENDENT-BLOCKS reference only, as a CAN-FAIL sensitivity
    demonstration, never as a pass/fail verdict on the Stage-A data.  The
    exact null distribution is obtained at Stage B by bootstrapping whole
    trials from the recorded indicator matrix, which needs no knowledge of c.
    """
    counts = np.asarray(counts, dtype=np.float64)
    nbar = counts.mean()
    denom = T * q_hat * (1.0 - q_hat)
    Q_obs = float(((counts - nbar) ** 2).sum() / denom)

    # null distribution of Q_raw under INDEPENDENT blocks, by simulation
    null = np.empty(R_null)
    for i in range(0, R_null, 20000):
        r = min(20000, R_null - i)
        C = rng.binomial(T, q_hat, size=(r, n_e)).astype(np.float64)
        null[i:i + r] = ((C - C.mean(axis=1, keepdims=True)) ** 2).sum(axis=1) / denom
    crit = float(np.quantile(null, 1.0 - NOMINAL_ALPHA))

    # CAN-FAIL demonstration: bias ONE block's marginal by a relative delta
    power = []
    for delta in defect_grid:
        qj = q_hat * (1.0 + delta)
        if not (0.0 < qj < 1.0):
            continue
        R = 4000
        C = rng.binomial(T, q_hat, size=(R, n_e)).astype(np.float64)
        C[:, 0] = rng.binomial(T, qj, size=R)
        Q = ((C - C.mean(axis=1, keepdims=True)) ** 2).sum(axis=1) / denom
        power.append(dict(single_block_relative_bias=delta,
                          power_at_alpha=float((Q > crit).mean())))
    return dict(
        set=sid, n_e=n_e, T=T, q_hat_used=q_hat,
        forced_value="E[F_j] = q for every block j, exactly, by ring-shift "
                     "invariance of e'' (see docstring)",
        Q_raw_observed=Q_obs,
        Q_raw_over_df=Q_obs / (n_e - 1),
        independent_blocks_null_mean=float(null.mean()),
        independent_blocks_critical_value=crit,
        null_replicates=R_null,
        exceeds_independent_blocks_critical=bool(Q_obs > crit),
        verdict="SENSITIVITY DEMONSTRATION ONLY -- the correctly scaled "
                "reference needs the (T) second moment, which this task is "
                "not authorized to evaluate (it determines log2 A_2)",
        can_fail_power_curve=power,
    )


# ==========================================================================
# PHASE 7 -- R5: the oracle gate's machinery, self-tested on an exact law
# ==========================================================================

def oracle_gate_selftest(sa):
    """CTRL-ORACLE-v2 machinery: an EXACT RATIONAL law of S, scaled by the
    lcm of its denominators to exact integer pseudo-counts, pushed through
    stage_a.log2_A_from_hist, compared against the exact rational log2 A_k.

    This verifies the GATE, not the oracle: the oracle package lives in
    BATCH-003 and is outside this task's read scope, so the sibling files
    are neither read nor re-run here.  The exact laws below are constructed
    in this file and are strongly OFF-NULL at both signs, which is the
    property the current tautological gate lacks.
    """
    cases = []
    # exchangeable two-point mixture with exact rational parameters (A_k >= 1
    # by Jensen) PLUS point-mass laws, which give A_k < 1.  Both signs are
    # exercised: that is exactly the property the v1 gate lacks.
    specs = [
        dict(kind="mix", name="mix-positive-strong", n_e=12, eps=Fraction(1, 8),
             q1=Fraction(3, 5), q0=Fraction(1, 50)),
        dict(kind="mix", name="mix-positive-mild", n_e=16, eps=Fraction(1, 4),
             q1=Fraction(1, 4), q0=Fraction(3, 20)),
        dict(kind="mix", name="binomial-exact-null", n_e=10, eps=Fraction(1, 2),
             q1=Fraction(2, 5), q0=Fraction(2, 5)),   # = binomial, A_k = 1
        dict(kind="mix", name="mix-extreme-positive", n_e=20, eps=Fraction(1, 100),
             q1=Fraction(9, 10), q0=Fraction(1, 100)),
        # S degenerate at c: A_k = C(c,k) / (C(n_e,k) (c/n_e)^k) < 1 for k >= 2
        dict(kind="point", name="degenerate-S-negative-strong", n_e=20, c=6),
        dict(kind="point", name="degenerate-S-negative-mild", n_e=40, c=20),
        # two point masses, tuned to sit just below the null
        dict(kind="twopoint", name="twopoint-negative", n_e=24,
             c0=6, c1=10, w=Fraction(1, 3)),
    ]
    for sp in specs:
        n_e = sp["n_e"]
        law = [Fraction(0)] * (n_e + 1)
        if sp["kind"] == "mix":
            eps, q1, q0 = sp["eps"], sp["q1"], sp["q0"]
            for s in range(n_e + 1):
                law[s] = (eps * math.comb(n_e, s) * q1 ** s * (1 - q1) ** (n_e - s)
                          + (1 - eps) * math.comb(n_e, s) * q0 ** s
                          * (1 - q0) ** (n_e - s))
        elif sp["kind"] == "point":
            law[sp["c"]] = Fraction(1)
        else:
            law[sp["c0"]] = sp["w"]
            law[sp["c1"]] = 1 - sp["w"]
        assert sum(law) == 1, "exact law must sum to 1"
        den = 1
        for p in law:
            den = den * p.denominator // math.gcd(den, p.denominator)
        counts = np.array([int(p * den) for p in law], dtype=object)
        assert int(sum(counts)) == den
        q_exact = sum(law[s] * s for s in range(n_e + 1)) / n_e
        for k in (2, 3, 5, 7):
            if k > n_e:
                continue
            mu_exact = (sum(law[s] * math.comb(s, k) for s in range(n_e + 1))
                        / math.comb(n_e, k))
            if mu_exact == 0:
                continue
            a_exact = mu_exact / q_exact ** k
            exact_bits = math.log2(a_exact.numerator) - math.log2(a_exact.denominator)
            hist = np.array([float(c) for c in counts], dtype=np.float64)
            got = sa.log2_A_from_hist(hist, n_e, k)
            cases.append(dict(configuration=sp["name"], n_e=n_e, k=k,
                              exact_log2_A_k=exact_bits,
                              stage_a_log2_A_k=got,
                              abs_diff=abs(got - exact_bits)))
    return dict(
        gate="CTRL-ORACLE-v2",
        construction="exact rational law_of_S -> lcm-scaled exact integer "
                     "pseudo-counts -> stage_a.log2_A_from_hist, compared "
                     "against the exact rational log2 A_k",
        scope_note="verifies the GATE MACHINERY on laws constructed in this "
                   "file. The oracle package (BATCH-003) is OUTSIDE this "
                   "task's read scope and was neither read nor re-run. The "
                   "passing measurement against the real oracle is the red "
                   "team's (TASK-20260806-dd901b section 5, 40 cells, max "
                   "diff 1.2e-14), not this task's.",
        cells=len(cases),
        max_abs_diff=max(c["abs_diff"] for c in cases),
        off_null_range_bits=[min(c["exact_log2_A_k"] for c in cases),
                             max(c["exact_log2_A_k"] for c in cases)],
        rows=cases,
    )


# ==========================================================================
# PHASE 9 -- R4: cost / resolution / power curve for the Coordinator
# ==========================================================================

POWER_GRID = [0.02, 0.05, 0.1, 0.2, 0.4, 0.8]


def interp_mde(rows, level=0.80):
    """Linear interpolation of the 80%-power effect size in log-effect space.
    Returns None if the grid does not bracket `level`."""
    pts = [(r["achieved_log2A_exact"], r["power"]) for r in rows
           if r.get("reachable")]
    pts.sort()
    for (e0, p0), (e1, p1) in zip(pts, pts[1:]):
        if p0 <= level <= p1 and p1 > p0:
            f = (level - p0) / (p1 - p0)
            return math.exp(math.log(e0) + f * (math.log(e1) - math.log(e0)))
    return None


def cost_resolution_curve(rng, n_e, q, k, Ts, tps, n_cal, n_val, R_pow, eps):
    rows = []
    for T in Ts:
        T = int(T)
        cal = calibrated_rule(rng, n_e, q, T, [k], n_cal, n_val)[0]
        if not cal.get("evaluable"):
            rows.append(dict(T=T, evaluable=False, reason=cal["reason"]))
            continue
        pw = power_curve(rng, n_e, q, T, k, cal["c_lo"], cal["c_hi"], eps,
                         POWER_GRID, R_pow)
        rows.append(dict(
            T=T,
            core_seconds_at_measured_throughput=T / tps,
            c_lo=cal["c_lo"], c_hi=cal["c_hi"],
            width_bits=cal["width_bits"],
            measured_size=cal["realized_size_out_of_sample"],
            measured_size_ci95=cal["realized_size_ci95"],
            null_sd=cal["null_sd"],
            power_grid=pw,
            mde_80pct_log2A_bits=interp_mde(pw, 0.80)))
    return rows


# ==========================================================================
# main
# ==========================================================================

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "calibration_results.json"))
    ap.add_argument("--wald-reps", type=int, default=3000)
    ap.add_argument("--cal-reps", type=int, default=200000)
    ap.add_argument("--val-reps", type=int, default=200000)
    ap.add_argument("--power-reps", type=int, default=20000)
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args(argv)
    if args.quick:
        args.wald_reps, args.cal_reps, args.val_reps, args.power_reps = 200, 20000, 20000, 4000

    t0, c0 = time.time(), time.process_time()
    timings = {}

    def mark(name, tw, tc):
        timings[name] = dict(wall_seconds=time.time() - tw,
                             cpu_seconds=time.process_time() - tc)

    raw, sets = load_committed()
    sa = load_stage_a()
    rng = np.random.default_rng(MASTER_SEED)

    res = {
        "task_id": "TASK-20260806-dbadc8",
        "batch": "BATCH-c5703d",
        "goal": "GOAL-HQC-001",
        "experiment_id": "EXP-HQC-982268",
        "role": "executor",
        "claim_tier": "toy",
        "measurement_prohibition":
            "No log2_A_k or log2_A_m is computed on any space-(T) arm. Every "
            "joint-moment number in this file is computed on a synthetic law "
            "drawn under an EXPLICIT null or an EXPLICITLY DECLARED "
            "alternative. The (T) arms contribute FIRST MOMENTS ONLY "
            "(q_hat, per-block failure counts). Var(S) on a (T) histogram is "
            "never formed: it determines log2 A_2 exactly.",
        "constructs_no_hqc_object": True,
        "master_seed": MASTER_SEED,
        "source_run": "RUN-HQC-982268-STAGEA-a",
        "started_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "environment": dict(python=sys.version.split()[0], numpy=np.__version__,
                            platform=platform.platform()),
        "settings": vars(args),
    }

    # ---------------- phase 0 ----------------
    tw, tc = time.time(), time.process_time()
    res["phase0_estimator_selftest"] = phase0_selftest(sa, rng)
    mark("phase0_estimator_selftest", tw, tc)

    # ---------------- phase 1 ----------------
    tw, tc = time.time(), time.process_time()
    res["phase1_null_identity"] = phase1_null_identity()
    mark("phase1_null_identity", tw, tc)

    # ---------------- phase 2: R1, current rule ----------------
    tw, tc = time.time(), time.process_time()
    r2 = {"rule": "INV-NULL v1: fire if |log2 Ahat_k| > 3 * SE_jack, "
                  "SE_jack = delete-one jackknife over 200 contiguous "
                  "trial batches (stage_a.jackknife_log2_A)",
          "null": "S ~ Binomial(n_e, q_hat) -- exactly the law NULL-P and "
                  "NULL-M instantiate",
          "at_stage_A_T": {}, "at_stage_B_T": {}}
    for sid, st in STATIC.items():
        s = sets[sid]
        ks = [k for k in st["k_report"] if k <= st["n_e"]]
        r2["at_stage_A_T"][sid] = dict(
            arm="NULL-M", n_e=st["n_e"], m=st["m"],
            q=s["nullM_q_hat"], T=s["nullM_T"],
            rows=wald_size(rng, st["n_e"], s["nullM_q_hat"], s["nullM_T"],
                           ks, args.wald_reps))
    for sid, st in STATIC.items():
        s = sets[sid]
        ks = sorted({st["m"], 2})
        ks = [k for k in ks if k <= st["n_e"]]
        r2["at_stage_B_T"][sid] = dict(
            arm="null law at the CONTRACTED Stage-B allocation",
            n_e=st["n_e"], m=st["m"], q=s["q_hat_T"], T=st["T_alloc"],
            rows=wald_size(rng, st["n_e"], s["q_hat_T"], st["T_alloc"],
                           ks, max(500, args.wald_reps // 3)))
    res["phase2_current_rule_size"] = r2
    mark("phase2_current_rule_size", tw, tc)

    # ---------------- phase 3: R1, proposed rule ----------------
    tw, tc = time.time(), time.process_time()
    r3 = {"rule": "INV-NULL v2: fire if log2 Ahat_k lies outside "
                  "[c_lo, c_hi], the equal-tailed 0.135%/99.865% quantiles "
                  "of the estimator's OWN null sampling distribution at "
                  "(n_e, q_hat, T, batching), obtained by Monte-Carlo from "
                  "S ~ Bin(n_e, q_hat). No jackknife, no Wald ratio, no "
                  "division by a random quantity.",
          "size_measurement": "critical values from n_cal draws; realized "
                              "size measured OUT OF SAMPLE on n_val "
                              "independent draws",
          "at_stage_A_T": {}, "at_stage_B_T": {}, "q_sensitivity": {}}
    for sid, st in STATIC.items():
        s = sets[sid]
        ks = [k for k in st["k_report"] if k <= st["n_e"]]
        r3["at_stage_A_T"][sid] = dict(
            arm="NULL-M", n_e=st["n_e"], m=st["m"],
            q=s["nullM_q_hat"], T=s["nullM_T"],
            rows=calibrated_rule(rng, st["n_e"], s["nullM_q_hat"],
                                 s["nullM_T"], ks, args.cal_reps,
                                 args.val_reps))
    for sid, st in STATIC.items():
        s = sets[sid]
        ks = sorted(set(st["k_report"]) | {st["m"]})
        ks = [k for k in ks if k <= st["n_e"]]
        r3["at_stage_B_T"][sid] = dict(
            n_e=st["n_e"], m=st["m"], q=s["q_hat_T"], T=st["T_alloc"],
            rows=calibrated_rule(rng, st["n_e"], s["q_hat_T"], st["T_alloc"],
                                 ks, args.cal_reps, args.val_reps))
        # how far do frozen critical values move under q_hat uncertainty?
        # SE(q_hat) upper bound using the INDEPENDENT-blocks variance (using
        # the measured Var(S) is forbidden: it determines log2 A_2).
        se_q = math.sqrt(s["q_hat_T"] * (1 - s["q_hat_T"])
                         / (st["n_e"] * s["T_stage_a"]))
        rel = 3.0 * se_q / s["q_hat_T"]
        r3["q_sensitivity"][sid] = dict(
            se_q_hat_independent_blocks_bound=se_q,
            relative_shift_tested=rel,
            note="3 SE(q_hat) at the STAGE-A T, using the independent-blocks "
                 "variance as the bound (the measured Var(S) is a (T) second "
                 "moment and is not evaluated here)",
            rows=q_sensitivity(rng, st["n_e"], s["q_hat_T"], st["T_alloc"],
                               [st["m"]] if st["m"] <= st["n_e"] else [],
                               max(20000, args.cal_reps // 5), rel))
    res["phase3_proposed_rule"] = r3
    mark("phase3_proposed_rule", tw, tc)

    # ---------------- phase 4: power ----------------
    tw, tc = time.time(), time.process_time()
    r4 = {"alternative_family": "two-point latent common-mode mixture: with "
                                "probability eps the n_e blocks are i.i.d. "
                                "Bernoulli(q1), otherwise i.i.d. "
                                "Bernoulli(q0), overall marginal held at "
                                "q_hat. ONE declared family (the M+ "
                                "mechanism), not a general alternative.",
          "eps": 0.05, "sets": {}}
    for sid, st in STATIC.items():
        s = sets[sid]
        k = st["m"]
        if k > st["n_e"]:
            continue
        rowsB = r3["at_stage_B_T"][sid]["rows"]
        row = next((r for r in rowsB if r["k"] == k and r.get("evaluable")), None)
        if row is None:
            r4["sets"][sid] = dict(k=k, evaluable=False,
                                   reason="no calibrated critical region at "
                                          "k = m at the allocated T")
            continue
        r4["sets"][sid] = dict(
            k=k, T=st["T_alloc"], q=s["q_hat_T"],
            c_lo=row["c_lo"], c_hi=row["c_hi"],
            rows=power_curve(rng, st["n_e"], s["q_hat_T"], st["T_alloc"], k,
                             row["c_lo"], row["c_hi"], 0.05,
                             [0.05, 0.1, 0.2, 0.4, 0.8, 1.6],
                             args.power_reps))
    res["phase4_power"] = r4
    mark("phase4_power", tw, tc)

    # ---------------- phase 5: R4 allocations ----------------
    tw, tc = time.time(), time.process_time()
    r5 = {"formula": "T_stab = 30 / P[S >= s_90], s_90 = min{s : "
                     "sum_{s'<=s} P[S=s'] C(s',k) >= 0.90 E[C(S,k)]}, "
                     "S ~ Bin(n_e, q_hat) -- the contract's own "
                     "sample_size_derivation, evaluated at the MEASURED "
                     "q_hat instead of the modelled q_for_sizing",
          "sets": {}}
    for sid, st in STATIC.items():
        s = sets[sid]
        n_e, m, q = st["n_e"], st["m"], s["q_hat_T"]
        ks = sorted({2, 3, m, m + 1} & set(range(2, n_e + 1)))
        rows = []
        for k in ks:
            s90, ts = t_stab(n_e, q, k)
            V = rel_variance_V(n_e, q, k)
            rows.append(dict(k=k, s_90=s90, T_stab=ts,
                             V_contract_formula=V,
                             T_alloc=st["T_alloc"],
                             reachable_at_allocation=(ts is not None
                                                      and ts <= st["T_alloc"]),
                             shortfall_factor=(ts / st["T_alloc"]
                                               if ts else None)))
        # largest k reachable at the allocation
        kmax = None
        for k in range(2, n_e + 1):
            _s90, ts = t_stab(n_e, q, k)
            if ts is None or ts > st["T_alloc"]:
                break
            kmax = k
        core_s_per_trial = 1.0 / s["trials_per_core_second"]
        rows_needed = next((r for r in rows if r["k"] == m), None)
        need = rows_needed["T_stab"] if rows_needed else None
        r5["sets"][sid] = dict(
            n_e=n_e, m=m, q_hat_measured=q,
            q_for_sizing_contract=None,
            T_alloc=st["T_alloc"], stage=st["stage"],
            k_max_at_allocation=kmax,
            measured_trials_per_core_second=s["trials_per_core_second"],
            modelled_core_seconds_contract=st["modelled_core_seconds"],
            core_seconds_at_allocation_measured_throughput=(
                st["T_alloc"] * core_s_per_trial),
            core_seconds_to_fund_k_equals_m=(need * core_s_per_trial
                                             if need else None),
            rows=rows)
        # measured (not formula) null SD scaling at the load-bearing order
        k_sd = st["k_sd"]
        Ts = [st["T_alloc"] / 10, st["T_alloc"] / 3, st["T_alloc"],
              st["T_alloc"] * 3]
        r5["sets"][sid]["k_for_sd_check"] = k_sd
        r5["sets"][sid]["contract_SE_at_allocated_T"] = \
            st["contract_SE_at_allocated_T"]
        r5["sets"][sid]["q_for_sizing_contract"] = st["q_for_sizing"]
        r5["sets"][sid]["contract_SE_recomputed_at_measured_q"] = (
            (math.sqrt(rel_variance_V(n_e, q, k_sd) / st["T_alloc"])
             / math.log(2)) if rel_variance_V(n_e, q, k_sd) else None)
        r5["sets"][sid]["measured_null_sd_vs_formula"] = \
            measured_sd_scaling(rng, n_e, q, k_sd, Ts, 20000)
        # what a FUNDED allocation would buy: calibrated interval at T_stab(m)
        if need is not None and need < 1e12:
            Tf = int(math.ceil(need))
            r5["sets"][sid]["calibrated_interval_at_funded_T"] = dict(
                T_funded=Tf, k=m,
                rows=calibrated_rule(rng, n_e, q, Tf, [m],
                                     max(50000, args.cal_reps // 4),
                                     max(50000, args.val_reps // 4)))
    res["phase5_allocations"] = r5
    mark("phase5_allocations", tw, tc)

    # ---------------- phase 6: R2 CTRL-POSHOM ----------------
    tw, tc = time.time(), time.process_time()
    r6 = {"control": "CTRL-POSHOM clause (a) -- block-marginal positional "
                     "homogeneity", "sets": {}}
    grid = [0.0, 0.002, 0.005, 0.01, 0.02, 0.05, 0.10, 0.20]
    for sid, st in STATIC.items():
        s = sets[sid]
        r6["sets"][sid] = poshom(rng, sid, st["n_e"],
                                 s["block_failure_counts"], s["T_stage_a"],
                                 s["q_hat_T"], 100000, grid)
        # projection: same control's detection floor at the Stage-B allocation
        synth = np.full(st["n_e"], st["T_alloc"] * s["q_hat_T"])
        proj = poshom(rng, sid, st["n_e"], synth, st["T_alloc"],
                      s["q_hat_T"], 40000, grid)
        r6["sets"][sid]["stage_B_projection"] = dict(
            T=st["T_alloc"],
            note="detection floor only. Q_raw_observed here is computed on a "
                 "SYNTHETIC exactly-homogeneous count vector and is a "
                 "placeholder, not a measurement; only the power curve and "
                 "the critical value are meaningful.",
            independent_blocks_critical_value=proj[
                "independent_blocks_critical_value"],
            can_fail_power_curve=proj["can_fail_power_curve"])
    res["phase6_ctrl_poshom"] = r6
    mark("phase6_ctrl_poshom", tw, tc)

    # ---------------- phase 7: R5 oracle gate ----------------
    tw, tc = time.time(), time.process_time()
    res["phase7_oracle_gate"] = oracle_gate_selftest(sa)
    mark("phase7_oracle_gate", tw, tc)

    # ---------------- phase 8: R3 D3 / D1 arithmetic ----------------
    tw, tc = time.time(), time.process_time()
    r8 = {"D3": {}, "D1": {}}
    for sid, st in STATIC.items():
        s = sets[sid]
        N, p = st["N"], s["p_hat"]
        mu_M = N * p
        sd_M = math.sqrt(N * p * (1 - p))
        cap = s["D3_cap"]
        r8["D3"][sid] = dict(
            cap=cap, N=N, p_hat=p,
            M_space_mean_w=mu_M, M_space_sd_w=sd_M,
            cap_minus_M_mean_in_M_sigma=(cap - mu_M) / sd_M,
            max_w_observed_on_T=s["D3_max_observed"],
            max_w_observed_in_M_sigma=(s["D3_max_observed"] - mu_M) / sd_M,
            P_violation_on_M_normal_approx_log10=(
                -((cap - mu_M) / sd_M) ** 2 / 2 / math.log(10)),
            verdict="D3 CANNOT FIRE ON (M): the cap sits far above the (M) "
                    "mean of w(e-tilde), so it is a hard support invariant, "
                    "not a (T)-vs-(M) discriminator")
        g, gse = s["gamma_hat"], s["gamma_hat_se"]
        r8["D1"][sid] = dict(
            gamma_hat_T=g, gamma_hat_se=gse,
            gamma_on_M_exact=1.0,
            separation_in_SE=(1.0 - g) / gse,
            gamma_hat_on_NULL_M_positive_control=s["nullM_gamma_hat"],
            alarm_band=[0.95, 1.05],
            margin_to_alarm_band_in_SE=(0.95 - g) / gse)
    res["phase8_D3_D1"] = r8
    mark("phase8_D3_D1", tw, tc)

    # ---------------- phase 9: R4 cost / resolution / power ----------------
    tw, tc = time.time(), time.process_time()
    T_GRID = {
        "PS-A":  [5.34e7, 1e8, 3e8],
        "PS-R1": [1e8, 1.452e8, 3e8, 1e9],
        "PS-R3": [1e6, 2e6, 5e6, 1e7, 2e7],
        "PS-R5": [2e7, 2.554e7, 5e7, 1e8],
    }
    r9 = {"purpose": "cost / resolution / power at the load-bearing order, "
                     "so the Coordinator can choose an allocation on measured "
                     "numbers rather than modelled ones",
          "alternative_family": r4["alternative_family"], "eps": 0.05,
          "power_grid_log2A_bits": POWER_GRID,
          "mde_definition": "effect size at which the calibrated rule has "
                            "80% power AGAINST THE DECLARED FAMILY; a "
                            "different mechanism at the same |log2 A_m| can "
                            "give different power",
          "sets": {}}
    for sid, st in STATIC.items():
        s = sets[sid]
        k = st["k_sd"]
        r9["sets"][sid] = dict(
            k=k, n_e=st["n_e"], q=s["q_hat_T"],
            trials_per_core_second=s["trials_per_core_second"],
            contract_allocation=st["T_alloc"],
            rows=cost_resolution_curve(
                rng, st["n_e"], s["q_hat_T"], k, T_GRID[sid],
                s["trials_per_core_second"],
                max(100000, args.cal_reps // 5),
                max(100000, args.val_reps // 5),
                max(10000, args.power_reps // 5), 0.05))
    res["phase9_cost_resolution"] = r9
    mark("phase9_cost_resolution", tw, tc)

    res["timing"] = timings
    ru = resource.getrusage(resource.RUSAGE_SELF)
    res["timing"]["total"] = dict(
        wall_seconds=time.time() - t0,
        process_cpu_seconds=time.process_time() - c0,
        rusage_user_plus_sys=ru.ru_utime + ru.ru_stime,
        peak_rss_mb=ru.ru_maxrss / 1024.0,
        budget_core_seconds=1200)
    res["finished_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    try:
        res["git_commit"] = subprocess.check_output(
            ["git", "-C", REPO, "rev-parse", "HEAD"], text=True).strip()
        res["git_dirty"] = bool(subprocess.check_output(
            ["git", "-C", REPO, "status", "--porcelain"], text=True).strip())
    except Exception as exc:                                   # noqa: BLE001
        res["git_commit"] = f"unavailable: {exc}"

    with open(args.out, "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=False, default=float)
    print(json.dumps(res["timing"], indent=1))
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
