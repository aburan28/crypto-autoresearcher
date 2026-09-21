#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TASK-20260806-518328 -- BATCH-e41719, GOAL-MLKEM-003, EXP-MLKEM-011.  Executor.

JOB A -- THE JOINT NULL.  BATCH-017's validator (VAL-20260806-03e199, recorded
as EV-MLKEM-890e2a W-10) established that N2 -- Binomial(nb, mu/nb) -- is the
PER-CELL minimum-variance member of the independent-iteration family and NOT the
joint one: it is independent across cells, while the physical process couples
cells within an iteration.  Neither N1 nor N2 carries any cross-cell dependence.
This task builds nulls that do, and re-runs against them the two statistics that
currently carry this lane's only surviving positive finding:

  (A) the 164-cell low-occupancy mean Pearson term, observed 0.6811;
  (B) the MODEL-FREE linearly-detrended var/mean on the last 25/50/100 cells of
      the n=43 mid band, observed 0.453 / 0.561 / 0.660.

JOB B -- BREAK THE OCCUPANCY / SCORE-POSITION CONFOUND AS FAR AS THE DESIGN
ALLOWS (EV-MLKEM-890e2a W-8), using the fact that the two archived files map
occupancy onto position differently, and report how far it CANNOT be broken.

OBSERVATIONS ONLY.  Nothing here concludes that the deficit is or is not real,
nor that Approximation 4.9 is validated or refuted.  That is Coordinator
authority under /review-evidence.

SCOPE: toy tier (q=241, m=40, n=43 and n=50), mid band only, raw undivided score
scale.  NO ML-KEM or Kyber security claim in either direction.  AGENTS.md rule
12 stays UNMET and UNWAIVED: EV-MLKEM-011, EV-MLKEM-013 and EV-MLKEM-017 keep
their status; KN-FIND-031 stays withdrawn.

ZERO NEW SAMPLING of the physical system.  No network.  No G6K.  No new .out
bytes.  Every random number drawn here belongs to a SEEDED SYNTHETIC NULL OBJECT
used to calibrate this script's own statistics; seeds are recorded in
results.json -> seeds and are never reported as a measurement of the archived
system.

IMPORTS, not retyped (handoff constraint 7): ingest, regions, increments, glm,
phi_of, pearson_residuals, floors, poisson_sample, binomial_sample,
gamma_sample, negbin_sample, solve, inverse, mean_sd, quantile, FILES and
DOF_BINDING all come from

  coordination/goals/GOAL-MLKEM-003/batches/BATCH-015/tasks/
      TASK-20260803-d9afbd/anom5_investigation.py

loaded by importlib from that path with sys.dont_write_bytecode set FIRST, so no
__pycache__ is written into that archived, immutable directory (BATCH-017 D-11).

DISCLOSED INHERITED INEXACTNESS (handoff constraint 9): BATCH-015's
`poisson_sample` is NOT a Poisson sampler for lambda >= 30 -- it returns
round(lambda + sqrt(lambda)*Z) with a non-negativity reject.  BATCH-015's own
report.md discloses this (section 5 item 4, "inversion below `lambda = 30` and a
rounded normal above"); the BATCH-017 validator's D-8 called it undisclosed in
BOTH packages, which is not accurate for BATCH-015.  Measured effect on E[t] and
Var[t] is under 0.5 % (BATCH-017 D-8).  This script does not silently inherit
it: null N1x below re-runs N1 with an EXACT inversion sampler for every
lambda < 700 (which covers every cell of the 164-cell subset and every
model-free window), and the N1 vs N1x difference is reported.  N2, JN-2 and JN-3
do not call poisson_sample at all.

Usage (the declared run):
    PYTHONDONTWRITEBYTECODE=1 python3 joint_null.py \
        > stdout.txt 2> stderr.txt
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True  # BEFORE any import of the archived module

import importlib.util
import json
import math
import os
import platform
import random
import resource
import subprocess
import time
from bisect import bisect_left

T_START = time.time()
WALL_BUDGET_S = 3600.0
GUARD_S = 3200.0  # graceful abort margin inside the hard budget

REPO = "/home/user/crypto-autoresearcher"
HERE = os.path.dirname(os.path.abspath(__file__))
B015_PATH = os.path.join(
    REPO,
    "coordination/goals/GOAL-MLKEM-003/batches/BATCH-015/tasks/"
    "TASK-20260803-d9afbd/anom5_investigation.py",
)

_spec = importlib.util.spec_from_file_location("b015_anom5", B015_PATH)
b015 = importlib.util.module_from_spec(_spec)
sys.modules["b015_anom5"] = b015
_spec.loader.exec_module(b015)

# ---------------------------------------------------------------------------
# Frozen analysis constants.  Fixed before any null was run.
# ---------------------------------------------------------------------------
DEGREE = {"n43": 5, "n50": 3}          # inherited from BATCH-014's forward
                                       # deviance selection; NOT chosen here
OCC_THRESHOLD = 0.02                   # the BATCH-017 validator's subset rule
MODEL_FREE_L = [25, 50, 75, 100, 150]  # last-L windows
REPS = {
    "n43_main": 800,
    "n50_main": 400,
    "n50_jn3": 200,
    "jn4": 300,
    "jobB_N2": 400,
    "jobB_JN3": 120,
}
SEED_BASE = 518328                     # the task token, in decimal
SEEDS = {}                             # filled as streams are created

# BATCH-017 reference values, carried ONLY for comparison.  Nothing here
# consumes them as an input to a computation.
REFERENCE = {
    "source": "EV-MLKEM-890e2a W-1 and BATCH-017 TASK-20260803-001a04 "
              "validation_notes.md sections 3 and 8",
    "n43_lowocc_164_mean_t": 0.6811,
    "n43_lowocc_164_null_N1": [0.9959, 0.1084],
    "n43_lowocc_164_null_N2": [0.9995, 0.1114],
    "n43_lowocc_164_z_N1": -2.91,
    "n43_lowocc_164_z_N2": -2.86,
    "n43_model_free_detrended_var_over_mean": {"25": 0.453, "50": 0.561,
                                               "75": 0.688, "100": 0.660,
                                               "150": 1.551},
    "n43_model_free_sampling_sd_sqrt_2_over_L_minus_1": {"25": 0.289,
                                                         "50": 0.202,
                                                         "75": 0.164,
                                                         "100": 0.142},
    "n50_model_free_detrended_var_over_mean": {"25": 1.042, "50": 0.961,
                                               "100": 1.192},
    "observed_lag1_autocorr_of_pearson_residuals_n43_mid": 0.104,
    "observed_lag1_autocorr_of_t_n43_mid": 0.0147,
}


def rng_for(name):
    """One seeded stream per (statistic, null) pair; every seed recorded."""
    s = SEED_BASE + sum((i + 1) * ord(ch) for i, ch in enumerate(name))
    SEEDS[name] = s
    return random.Random(s)


def log(*a):
    print(*a)
    sys.stdout.flush()


def elapsed():
    return time.time() - T_START


def mean_sd(v):
    return b015.mean_sd(v)


def acf(v, kmax):
    n = len(v)
    m = sum(v) / n
    den = sum((x - m) ** 2 for x in v)
    if den <= 0:
        return [0.0] * kmax
    return [sum((v[i] - m) * (v[i + k] - m) for i in range(n - k)) / den
            for k in range(1, kmax + 1)]


def newey_west_factor(v, q):
    """Bartlett-kernel variance inflation for the MEAN of the series v."""
    a = acf(v, q)
    return 1.0 + 2.0 * sum((1.0 - (j + 1.0) / (q + 1.0)) * a[j]
                           for j in range(q))


# ===========================================================================
# 1.  The archived data and the observed statistics
# ===========================================================================

def load(tag):
    spec = [f for f in b015.FILES if f["tag"] == tag][0]
    d = b015.ingest(spec)
    R = b015.regions(d)
    lo, hi = R["mid"]
    D = b015.increments(d, lo, hi)
    deg = DEGREE[tag]
    beta, mu, h, P = b015.glm(D, lo, hi, deg)
    nb = d["nb_iteration"]
    occ = [m / nb for m in mu]
    K = len(D)
    sel = [i for i in range(K) if occ[i] < OCC_THRESHOLD]
    return dict(tag=tag, data=d, lo=lo, hi=hi, D=D, K=K, nb=nb, M=d["M"],
                degree=deg, P=P, mu=mu, h=h, occ=occ, sel=sel,
                S=sum(mu), counts=d["counts"], sha256=d["sha256"])


def terms(D, mu, h):
    return [(D[i] - mu[i]) ** 2 / (mu[i] * (1.0 - h[i])) for i in range(len(D))]


def stat_A(Dv, F, sel_fixed):
    """The 164-cell low-occupancy mean Pearson term, through the IDENTICAL
    instrument: full GLM refit at the inherited degree, leverage correction,
    then the mean of t over the subset.  Two subset conventions are reported:
    FIXED (the observed design's subset, primary) and RESELECTED (the rule
    re-applied to each replicate's own fitted occupancy)."""
    beta, mu, h, P = b015.glm(Dv, F["lo"], F["hi"], F["degree"])
    t = terms(Dv, mu, h)
    K = len(Dv)
    mA = sum(t[i] for i in sel_fixed) / len(sel_fixed)
    sel2 = [i for i in range(K) if mu[i] / F["nb"] < OCC_THRESHOLD]
    mA2 = (sum(t[i] for i in sel2) / len(sel2)) if sel2 else float("nan")
    ts = [t[i] for i in sel_fixed]
    return dict(mean_t_fixed_subset=mA, mean_t_reselected_subset=mA2,
                n_reselected=len(sel2), phi_whole_band=sum(t) / K,
                lag1_t_subset=acf(ts, 1)[0],
                nw6_t_subset=newey_west_factor(ts, 6))


def stat_B(Dv, Ls):
    """MODEL-FREE linearly-detrended var/mean on the last L cells.

    Convention identified by reproducing the BATCH-017 validator's archived
    values 0.453 / 0.561 / 0.688 / 0.660 / 1.551: OLS line in the within-window
    index, residual sum of squares divided by (L - 2), divided by the window
    mean of the RAW increments.  No rate model enters the OBSERVED value."""
    out = {}
    n_all = len(Dv)
    for L in Ls:
        if L > n_all:
            continue
        y = Dv[n_all - L:]
        xs = list(range(L))
        xb = (L - 1) / 2.0
        yb = sum(y) / L
        sxx = sum((x - xb) ** 2 for x in xs)
        sxy = sum((xs[i] - xb) * (y[i] - yb) for i in range(L))
        bb = sxy / sxx
        aa = yb - bb * xb
        rss = sum((y[i] - (aa + bb * xs[i])) ** 2 for i in range(L))
        out[str(L)] = (rss / (L - 2)) / yb if yb > 0 else float("nan")
    return out


# ===========================================================================
# 2.  The null objects
# ===========================================================================
#
# DEPENDENCE STRUCTURE OF EACH NULL -- stated here, verified numerically below.
#
#   N1   independent Poisson(mu_T).                      Cov = 0.
#   N1x  as N1 but with an EXACT inversion Poisson sampler for lambda < 700,
#        so the rounded-Gaussian inexactness of BATCH-015's poisson_sample is
#        not silently inherited.                          Cov = 0.
#   N2   independent Binomial(nb, mu_T/nb) -- the PER-CELL minimum-variance
#        member of the independent-iteration family.      Cov = 0.
#   JN-P the PHYSICAL joint null: every iteration deposits exactly q^k_fft
#        candidates across the WHOLE score support, allocated multinomially.
#        Var(D_T) = mu_T (1 - mu_T/M), Cov(D_T,D_T') = -mu_T mu_T'/M with
#        M = nb * q^k_fft.  Treated ANALYTICALLY (section 4): both effects are
#        O(mu/M) <= 6e-8 on this band, so JN-P is numerically independent
#        Poisson.  BATCH-015 already excluded the marginal half of this as
#        mechanism M-a1 (archived floor_multinomial_over_pooled_scores =
#        0.9999999941601551 for the n43 mid band); the covariance half is added
#        here.  NOT claimed as new.
#   JN-2 the handoff's named construction: RESAMPLE WHOLE ITERATIONS with each
#        iteration's BAND total preserved.  Each of the nb iterations deposits
#        a fixed budget B_i into the mid band (sum B_i = the observed band
#        total S exactly), each candidate choosing a cell with probability
#        p_T = mu_T/S.  Equivalent to Multinomial(S, p).  This is the MAXIMAL
#        sum-preserving negative cross-cell dependence available:
#        Var(D_T) = mu_T (1 - p_T), Cov(D_T,D_T') = -mu_T mu_T'/S.
#        It is deliberately OVER-constrained relative to physics -- the process
#        fixes the per-iteration total over ALL scores, not over the band --
#        and is reported as a bound, not as a description of the process.
#   JN-3 the JOINT MINIMUM-VARIANCE object.  Each iteration deposits AT MOST
#        ONE candidate per cell (which is what attains the per-cell floor) AND
#        carries a near-fixed per-iteration band budget.  Implemented as
#        systematic pi-ps sampling with inclusion probabilities pi_T = mu_T/nb
#        and a fresh random cell order per iteration, so the per-iteration cell
#        indicators are EXACTLY Bernoulli(pi_T) -- giving marginals identical
#        to N2 -- while the per-iteration total is floor/ceil(sum pi) and the
#        cells compete within an iteration.  Var(D_T) = mu_T(1 - occ_T)
#        exactly, plus negative cross-cell dependence.  Doubly over-constrained
#        (0/1 per cell AND a near-fixed band budget): the extreme lower
#        envelope of the joint family.
#   JN-4 the ADVERSARIAL WIDENER: spatially correlated dispersion.  A smooth
#        latent field psi_T = exp(sigma g_T - sigma^2/2), g an AR(1) with
#        lag-1 correlation exp(-1/ell), E[psi] = 1, gives Var(D_T) = mu_T psi_T
#        with POSITIVE cross-cell dependence.  This is the only direction in
#        which a joint null can WIDEN the null and rescue the finding's
#        rejection, so it is run as a grid and compared against the observed
#        autocorrelation of the t series.
#
# WHY THIS IS THE RIGHT FAMILY FOR A CUMULATIVE COUNTING PROCESS.  The archived
# .out file is a pooled SURVIVAL curve C_T over nb iterations; the increments
# D_T = C_T - C_{T+1} are the per-cell counts.  The only coupling the process
# imposes within an iteration is the shared candidate budget q^k_fft allocated
# across the score support (JN-P), plus whatever the scores' joint law adds.  A
# joint null for a cumulative counting process therefore has to (i) preserve the
# iteration as the unit of resampling, (ii) let cells inside an iteration
# compete for that iteration's budget, and (iii) leave the per-cell marginal at
# or above the per-cell floor.  JN-2 and JN-3 do exactly that at two different
# strengths of the budget constraint; JN-P does it faithfully and turns out to
# be inert.  JN-4 covers the opposite sign of dependence, which the
# budget-preserving family cannot produce.

def exact_poisson(lam, rng):
    """Knuth inversion -- exact -- for lambda < 700; falls back to BATCH-015's
    rounded-Gaussian above (no cell of the 164-cell subset and no model-free
    window reaches lambda = 700, so every number this script leans on is drawn
    from the exact branch)."""
    if lam < 700.0:
        L = math.exp(-lam)
        k = 0
        p = 1.0
        while True:
            p *= rng.random()
            if p <= L:
                return k
            k += 1
            if k > 20000:
                return k
    return b015.poisson_sample(lam, rng)


def make_gen(kind, F, rng, **kw):
    mu, nb, K = F["mu"], F["nb"], F["K"]

    if kind == "N1":
        return lambda: [b015.poisson_sample(m, rng) for m in mu]

    if kind == "N1x":
        return lambda: [exact_poisson(m, rng) for m in mu]

    if kind == "N2":
        return lambda: [b015.binomial_sample(nb, m / nb, rng) for m in mu]

    if kind == "JN2":
        S = int(round(sum(mu)))
        cum = []
        c = 0.0
        for m in mu:
            c += m
            cum.append(c / sum(mu))
        cum[-1] = 1.0
        # deterministic per-iteration budgets summing EXACTLY to S
        base, extra = divmod(S, nb)
        budgets = [base + 1] * extra + [base] * (nb - extra)

        def gen():
            cnt = [0] * K
            r = rng.random
            bl = bisect_left
            for B in budgets:
                for _ in range(B):
                    cnt[bl(cum, r())] += 1
            return cnt
        return gen

    if kind == "JN3":
        pi = [m / nb for m in mu]
        assert max(pi) <= 1.0
        idx = list(range(K))

        def gen():
            cnt = [0] * K
            sh = rng.shuffle
            r = rng.random
            for _ in range(nb):
                sh(idx)
                c = 0.0
                target = r()
                for cell in idx:
                    c += pi[cell]
                    if c > target:
                        cnt[cell] += 1
                        target += 1.0
            return cnt
        return gen

    if kind == "JN4":
        sigma = kw["sigma"]
        ell = kw["ell"]
        rho = math.exp(-1.0 / ell)
        srho = math.sqrt(max(0.0, 1.0 - rho * rho))
        half = 0.5 * sigma * sigma

        def gen():
            g = rng.gauss(0.0, 1.0)
            out = []
            for m in mu:
                g = rho * g + srho * rng.gauss(0.0, 1.0)
                psi = math.exp(sigma * g - half)
                if psi > 1.0:
                    out.append(b015.negbin_sample(m, psi, rng))
                else:
                    n2 = max(1, int(round(m / max(1e-9, 1.0 - psi))))
                    if n2 < m:
                        n2 = int(math.ceil(m))
                    out.append(b015.binomial_sample(n2, m / n2, rng))
            return out
        return gen

    raise ValueError(kind)


# ===========================================================================
# 3.  Replicate driver
# ===========================================================================

def run_null(kind, F, reps, label, **kw):
    rng = rng_for(label)
    gen = make_gen(kind, F, rng, **kw)
    sel = F["sel"]
    accA, accA2, accPhi, accLag, accNW = [], [], [], [], []
    accB = {str(L): [] for L in MODEL_FREE_L if L <= F["K"]}
    cellsum = [0.0] * F["K"]
    cellsq = [0.0] * F["K"]
    tot = []
    subtot = []
    discarded = 0
    t0 = time.time()
    for rep in range(reps):
        Dv = gen()
        for i in range(F["K"]):
            cellsum[i] += Dv[i]
            cellsq[i] += Dv[i] * Dv[i]
        tot.append(sum(Dv))
        subtot.append(float(sum(Dv[i] for i in sel)))
        try:
            a = stat_A(Dv, F, sel)
        except (FloatingPointError, ZeroDivisionError, OverflowError,
                ValueError):
            discarded += 1
            continue
        if not math.isfinite(a["mean_t_fixed_subset"]):
            discarded += 1
            continue
        accA.append(a["mean_t_fixed_subset"])
        accA2.append(a["mean_t_reselected_subset"])
        accPhi.append(a["phi_whole_band"])
        accLag.append(a["lag1_t_subset"])
        accNW.append(a["nw6_t_subset"])
        b = stat_B(Dv, MODEL_FREE_L)
        for k, v in b.items():
            accB[k].append(v)
        if elapsed() > GUARD_S:
            log("  !! wall-clock guard hit at rep %d of %d for %s"
                % (rep + 1, reps, label))
            break
    n = len(accA)
    mA, sA = mean_sd(accA)
    mA2, sA2 = mean_sd(accA2)
    mP, sP = mean_sd(accPhi)
    mL, sL = mean_sd(accLag)
    mN, sN = mean_sd(accNW)
    mT, sT = mean_sd([float(x) for x in tot])
    # measured marginal variance ratio per cell, on the subset
    nrep = len(tot)
    vr = []
    sumvar = 0.0
    for i in sel:
        e = cellsum[i] / nrep
        v = (cellsq[i] - nrep * e * e) / max(nrep - 1, 1)
        sumvar += v
        vr.append(v / F["mu"][i])
    mvr, svr = mean_sd(vr)
    # AGGREGATE CROSS-CELL DEPENDENCE, measured, on the low-occupancy subset:
    #   Var(sum_{i in A} D_i) / sum_{i in A} Var(D_i)
    # = 1 for an independent null, < 1 for negative cross-cell dependence,
    # > 1 for positive.  This is the direct instrument check that each null
    # carries the dependence structure claimed for it.
    _msub, ssub = mean_sd(subtot)
    dep_ratio = (ssub * ssub / sumvar) if sumvar > 0 else None
    out = dict(
        null=kind, label=label, kwargs={k: v for k, v in kw.items()},
        seed=SEEDS[label], replicates=n, replicates_discarded=discarded,
        seconds=time.time() - t0,
        stat_A_mean=mA, stat_A_sd=sA,
        stat_A_reselected_mean=mA2, stat_A_reselected_sd=sA2,
        phi_whole_band_mean=mP, phi_whole_band_sd=sP,
        lag1_t_subset_mean=mL, lag1_t_subset_sd=sL,
        nw6_t_subset_mean=mN, nw6_t_subset_sd=sN,
        band_total_mean=mT, band_total_sd=sT,
        measured_var_over_mu_on_subset_mean=mvr,
        measured_var_over_mu_on_subset_sd=svr,
        measured_cross_cell_dependence_ratio_on_subset=dep_ratio,
        measured_cross_cell_dependence_ratio_definition=(
            "Var(sum_{i in subset} D_i) / sum_{i in subset} Var(D_i); "
            "1 = independent, <1 = negative cross-cell dependence, "
            ">1 = positive"),
        stat_B={k: dict(zip(("mean", "sd"), mean_sd(v)))
                for k, v in accB.items() if v},
        stat_B_p05={k: b015.quantile(sorted(v), 0.05)
                    for k, v in accB.items() if v},
    )
    return out, accA, accB


def z_of(obs, m, s):
    return (obs - m) / s if s else None


# ===========================================================================
# 4.  Analytic block: what each joint constraint can and cannot do
# ===========================================================================

def analytic(F):
    mu, nb, M, S = F["mu"], F["nb"], F["M"], F["S"]
    sel = F["sel"]

    def summarise(varratio, covscale, name):
        # varratio[i] = Var(D_i)/mu_i ; covscale = the divisor N in
        # Cov(D_i,D_j) = -mu_i mu_j / N
        sub = [varratio[i] for i in sel]
        cor = []
        for a in range(0, len(sel), 17):
            for b in range(a + 1, len(sel), 17):
                i, j = sel[a], sel[b]
                pi_, pj = mu[i] / covscale, mu[j] / covscale
                cor.append(-math.sqrt(pi_ * pj / ((1 - pi_) * (1 - pj))))
        return dict(
            null=name,
            var_over_mu_band_min=min(varratio), var_over_mu_band_max=max(varratio),
            var_over_mu_subset_min=min(sub), var_over_mu_subset_max=max(sub),
            var_over_mu_subset_mean=sum(sub) / len(sub),
            max_abs_pair_correlation_in_subset=(max(abs(c) for c in cor)
                                                if cor else 0.0),
            covariance_divisor=covscale)

    return dict(
        JN_P_physical=summarise([1.0 - m / M for m in mu], M,
                                "JN-P physical full-support multinomial"),
        JN_2_band_total=summarise([1.0 - m / S for m in mu], S,
                                  "JN-2 band-total-preserving multinomial"),
        JN_3_iteration=dict(
            null="JN-3 joint minimum-variance (0/1 per cell per iteration)",
            var_over_mu_band_min=min(1.0 - m / nb for m in mu),
            var_over_mu_band_max=max(1.0 - m / nb for m in mu),
            var_over_mu_subset_min=min(1.0 - mu[i] / nb for i in sel),
            var_over_mu_subset_max=max(1.0 - mu[i] / nb for i in sel),
            var_over_mu_subset_mean=sum(1.0 - mu[i] / nb for i in sel) / len(sel),
            note=("identical per-cell variance to N2 by construction; the "
                  "coupling is in the cross-cell terms only")),
        pinning_theorem=(
            "Var(D_T) is a functional of the MARGINAL law of D_T alone, so no "
            "cross-cell coupling can lower it.  Any joint null whose per-cell "
            "marginals are the per-cell minimum-variance member has exactly "
            "N2's per-cell variances, hence (up to the refit's response) the "
            "same E[t_T] and the same null MEAN for any unweighted average of "
            "t.  The entire room a joint null has to move a z therefore lies "
            "in the null SD, and sum-preserving coupling makes that SD "
            "SMALLER, not larger."),
        sd_needed_for_z_above_minus_2=None,  # filled in main()
    )


# ===========================================================================
# 5.  JOB B -- occupancy versus score position across the two files
# ===========================================================================

def ols_weights(X, K):
    """Return (XtX)^-1 Xt as a list of rows; row p gives beta_p = sum_i c_i y_i."""
    P = len(X[0])
    XtX = [[sum(X[i][a] * X[i][c] for i in range(K)) for c in range(P)]
           for a in range(P)]
    Inv = b015.inverse(XtX)
    C = [[sum(Inv[a][c] * X[i][c] for c in range(P)) for i in range(K)]
         for a in range(P)]
    return C


def cheb_terms(u, deg):
    """Chebyshev polynomials of the first kind on u in [-1,1], orders 1..deg."""
    out = []
    Tm1, T0 = 1.0, u
    for d in range(1, deg + 1):
        if d == 1:
            out.append(u)
        else:
            Tn = 2.0 * u * T0 - Tm1
            Tm1, T0 = T0, Tn
            out.append(Tn)
    return out


def jobB_designs(F43, F50):
    """Build the pooled cell table and every (coordinate, specification) design.

    Coordinates -- three inequivalent ways to say 'the same score position' in
    two files whose score scales differ:
      pos_norm : (T - lo)/(hi - lo), normalised position inside the mid band
      logC     : log10 of the cumulative survival count C_T (the band DEFINING
                 variable; both bands span 1e3..1e5 by construction)
      T_raw    : the raw undivided score (n43 551..851, n50 636..1131)
    """
    rows = []
    for F in (F43, F50):
        lo, hi, cnt = F["lo"], F["hi"], F["counts"]
        for i in range(F["K"]):
            T = lo + i
            rows.append(dict(file=F["tag"], i=i, T=T, C=cnt[T],
                             occ=F["occ"][i], mu=F["mu"][i]))
    coords = {}
    for name in ("pos_norm", "logC", "T_raw"):
        vals = []
        for r in rows:
            if name == "pos_norm":
                F = F43 if r["file"] == "n43" else F50
                vals.append((r["T"] - F["lo"]) / float(F["hi"] - F["lo"]))
            elif name == "logC":
                vals.append(math.log10(max(r["C"], 1)))
            else:
                vals.append(float(r["T"]))
        lo_v, hi_v = min(vals), max(vals)
        coords[name] = [2.0 * (v - lo_v) / (hi_v - lo_v) - 1.0 for v in vals]

    isA = [1.0 if r["file"] == "n43" else 0.0 for r in rows]
    occ = [r["occ"] for r in rows]
    K = len(rows)

    designs = {}
    for cname, u in coords.items():
        for deg in (1, 2, 3, 5):
            for filespec in (False, True):
                X = []
                for i in range(K):
                    row = [1.0, isA[i]]
                    ct = cheb_terms(u[i], deg)
                    if filespec:
                        row += [c * isA[i] for c in ct]
                        row += [c * (1.0 - isA[i]) for c in ct]
                    else:
                        row += ct
                    row.append(occ[i])
                    X.append(row)
                key = "%s|deg%d|%s" % (cname, deg,
                                       "file_specific" if filespec else "common")
                designs[key] = X
    return rows, coords, designs, K


def jobB_static(rows, coords, designs, K, F43, F50):
    """Everything about JOB B that does not need a null: monotonicity, the
    cross-file occupancy contrast at matched position, and, for every
    specification, the occupancy coefficient's effective design size, its
    collinearity, and its exact linear weights."""
    out = {}

    # (B1) within-file confounding
    b1 = {}
    for F in (F43, F50):
        occ = F["occ"]
        nonmono = sum(1 for i in range(F["K"] - 1) if occ[i] < occ[i + 1])
        b1[F["tag"]] = dict(
            cells=F["K"], non_monotone_steps_of_occupancy_in_score_index=nonmono,
            occupancy_min=min(occ), occupancy_max=max(occ),
            occupancy_ratio_max_over_min=max(occ) / min(occ))
    out["B1_within_file_monotonicity"] = b1

    # (B2) cross-file occupancy contrast at matched coordinate, 10 bins
    b2 = {}
    for cname, u in coords.items():
        bins = [[[], []] for _ in range(10)]
        tvals = {"n43": None, "n50": None}
        for j, r in enumerate(rows):
            k = min(9, int((u[j] + 1.0) / 2.0 * 10))
            bins[k][0 if r["file"] == "n43" else 1].append(r["occ"])
        rec = []
        for k in range(10):
            a, b = bins[k]
            rec.append(dict(bin=k, n43_cells=len(a), n50_cells=len(b),
                            n43_mean_occ=(sum(a) / len(a)) if a else None,
                            n50_mean_occ=(sum(b) / len(b)) if b else None,
                            occ_ratio=((sum(a) / len(a)) / (sum(b) / len(b)))
                            if a and b and sum(b) > 0 else None))
        ratios = [x["occ_ratio"] for x in rec if x["occ_ratio"]]
        b2[cname] = dict(bins=rec,
                         bins_with_both_files=len(ratios),
                         occ_ratio_min=min(ratios) if ratios else None,
                         occ_ratio_max=max(ratios) if ratios else None,
                         occ_ratio_geomean=(math.exp(sum(math.log(x)
                                                         for x in ratios)
                                                     / len(ratios))
                                            if ratios else None))
    out["B2_cross_file_occupancy_contrast_at_matched_position"] = b2

    # (B3) per specification: occupancy coefficient weights, effective design
    #      size (participation ratio), collinearity
    b3 = {}
    occ = [r["occ"] for r in rows]
    for key, X in designs.items():
        P = len(X[0])
        try:
            C = ols_weights(X, K)
        except ZeroDivisionError:
            b3[key] = dict(status="singular_design")
            continue
        c = C[P - 1]                              # weights of the occ coefficient
        ssq = sum(x * x for x in c)
        s4 = sum(x ** 4 for x in c)
        eff = (ssq * ssq / s4) if s4 > 0 else None  # 1/sum(w^2), w = c^2/sum c^2
        # collinearity of occ on the rest of the design
        Xr = [row[:P - 1] for row in X]
        Cr = ols_weights(Xr, K)
        fit = [sum(Cr[a][i] * occ[i] for i in range(K)) for a in range(P - 1)]
        pred = [sum(Xr[i][a] * fit[a] for a in range(P - 1)) for i in range(K)]
        ob = sum(occ) / K
        sst = sum((o - ob) ** 2 for o in occ)
        sse = sum((occ[i] - pred[i]) ** 2 for i in range(K))
        r2 = 1.0 - sse / sst
        b3[key] = dict(status="ok", n_parameters=P,
                       effective_design_size_participation_ratio=eff,
                       pooled_cells=K,
                       R2_of_occupancy_on_the_rest_of_the_design=r2,
                       variance_inflation_factor=(1.0 / (1.0 - r2))
                       if r2 < 1 else None,
                       sum_c_squared=ssq)
    out["B3_specification_diagnostics"] = b3
    return out, [r["occ"] for r in rows]


def jobB_beta(designs, tvec):
    beta = {}
    for key, X in designs.items():
        K = len(X)
        P = len(X[0])
        try:
            C = ols_weights(X, K)
        except ZeroDivisionError:
            continue
        beta[key] = sum(C[P - 1][i] * tvec[i] for i in range(K))
    return beta


# ===========================================================================
# 6.  main
# ===========================================================================

def main():
    log("=" * 78)
    log("TASK-20260806-518328 -- joint null and cross-file identification")
    log("BATCH-e41719, GOAL-MLKEM-003, EXP-MLKEM-011.  OBSERVATIONS ONLY.")
    log("Toy tier; raw undivided score scale; no ML-KEM claim in either "
        "direction.")
    log("Zero new sampling of the physical system.")
    log("=" * 78)

    R = dict(
        task="TASK-20260806-518328", batch="BATCH-e41719",
        goal="GOAL-MLKEM-003", experiment="EXP-MLKEM-011",
        scope=("toy tier; q=241 m=40 n=43 and n=50; mid band only; raw "
               "undivided score scale; NO ML-KEM or Kyber claim in either "
               "direction"),
        rule_12_status="UNMET AND UNWAIVED",
        imported_module=B015_PATH,
        imported_symbols=["ingest", "regions", "increments", "glm", "phi_of",
                          "pearson_residuals", "floors", "poisson_sample",
                          "binomial_sample", "gamma_sample", "negbin_sample",
                          "solve", "inverse", "mean_sd", "quantile", "FILES",
                          "DOF_BINDING"],
        dof_binding=b015.DOF_BINDING,
        reference_values_carried_for_comparison_only=REFERENCE,
    )

    # ---- observed -------------------------------------------------------
    F43 = load("n43")
    F50 = load("n50")
    R["files"] = {}
    obs = {}
    for F in (F43, F50):
        t = terms(F["D"], F["mu"], F["h"])
        selt = [t[i] for i in F["sel"]]
        o = dict(
            tag=F["tag"], sha256=F["sha256"], nb_iteration=F["nb"], M=F["M"],
            mid_band=[F["lo"], F["hi"]], cells=F["K"], band_total=sum(F["D"]),
            degree=F["degree"], degree_provenance=(
                "inherited from BATCH-014 dispersion_control_c1.py forward "
                "deviance selection at chi2_{1,0.95}=3.841; NOT chosen here"),
            phi_whole_band=sum(t) / F["K"],
            occupancy_min=min(F["occ"]), occupancy_max=max(F["occ"]),
            occupancy_mean=sum(F["occ"]) / F["K"],
            sum_of_occupancies_over_band=sum(F["occ"]),
            low_occupancy_subset_rule="fitted occupancy < %.2f" % OCC_THRESHOLD,
            low_occupancy_subset_cells=len(F["sel"]),
            low_occupancy_subset_is_contiguous=(
                F["sel"] == list(range(min(F["sel"]), max(F["sel"]) + 1))),
            low_occupancy_subset_index_range=[min(F["sel"]), max(F["sel"])],
            low_occupancy_subset_mean_t=sum(selt) / len(selt),
            cells_with_mu_ge_30=sum(1 for m in F["mu"] if m >= 30.0),
            subset_cells_with_mu_ge_30=sum(1 for i in F["sel"]
                                           if F["mu"][i] >= 30.0),
            subset_max_mu=max(F["mu"][i] for i in F["sel"]),
            model_free_detrended_var_over_mean=stat_B(F["D"], MODEL_FREE_L),
            lag1_autocorr_pearson_residuals_band=acf(
                b015.pearson_residuals(F["D"], F["mu"], F["h"]), 1)[0],
            acf_t_band_1_to_10=acf(t, 10),
            acf_t_subset_1_to_12=acf(selt, 12),
            newey_west_factor_t_subset={
                str(q): newey_west_factor(selt, q) for q in (1, 3, 6, 12, 20)},
            sampling_sd_of_each_autocorrelation=1.0 / math.sqrt(len(selt)),
            floors=b015.floors(F["mu"], F["nb"], F["M"]),
        )
        R["files"][F["tag"]] = o
        obs[F["tag"]] = o
        log("")
        log("[observed %s] mid band %s, %d cells, total %d, nb=%d, M=%d"
            % (F["tag"], (F["lo"], F["hi"]), F["K"], sum(F["D"]), F["nb"],
               F["M"]))
        log("  degree %d (inherited).  phi_whole_band = %.6f"
            % (F["degree"], o["phi_whole_band"]))
        log("  occupancy min/mean/max = %.6f / %.6f / %.6f ; sum over band "
            "= %.4f" % (o["occupancy_min"], o["occupancy_mean"],
                        o["occupancy_max"], o["sum_of_occupancies_over_band"]))
        log("  low-occupancy subset (occ<%.2f): %d cells, contiguous=%s, "
            "mean t = %.6f" % (OCC_THRESHOLD, o["low_occupancy_subset_cells"],
                               o["low_occupancy_subset_is_contiguous"],
                               o["low_occupancy_subset_mean_t"]))
        log("  model-free detrended var/mean: %s"
            % {k: round(v, 4) for k, v
               in o["model_free_detrended_var_over_mean"].items()})
        log("  cells with mu>=30: %d of %d (band), %d of %d (subset), subset "
            "max mu = %.1f" % (o["cells_with_mu_ge_30"], F["K"],
                               o["subset_cells_with_mu_ge_30"],
                               len(F["sel"]), o["subset_max_mu"]))
        log("  lag-1 acf of t on the subset = %+.4f  (sampling sd %.4f);"
            % (o["acf_t_subset_1_to_12"][0],
               o["sampling_sd_of_each_autocorrelation"]))
        log("  Newey-West inflation of Var(mean t) on the subset: %s"
            % {k: round(v, 4) for k, v in o["newey_west_factor_t_subset"].items()})

    # reproduction check against the archived reference numbers
    R["reproduction_of_archived_reference_values"] = dict(
        n43_lowocc_164_mean_t=dict(
            archived=REFERENCE["n43_lowocc_164_mean_t"],
            recomputed=obs["n43"]["low_occupancy_subset_mean_t"],
            cells_archived=164,
            cells_recomputed=obs["n43"]["low_occupancy_subset_cells"]),
        n43_model_free=dict(
            archived=REFERENCE["n43_model_free_detrended_var_over_mean"],
            recomputed=obs["n43"]["model_free_detrended_var_over_mean"],
            convention_identified=("residual sum of squares / (L-2), divided "
                                   "by the window mean of the raw increments")),
        n50_model_free=dict(
            archived=REFERENCE["n50_model_free_detrended_var_over_mean"],
            recomputed={k: v for k, v
                        in obs["n50"]["model_free_detrended_var_over_mean"].items()
                        if k in ("25", "50", "100")}),
        n43_lag1_acf_of_t_band=dict(
            archived=REFERENCE["observed_lag1_autocorr_of_t_n43_mid"],
            recomputed=obs["n43"]["acf_t_band_1_to_10"][0]),
        n43_lag1_acf_of_pearson_residuals_band=dict(
            archived=REFERENCE["observed_lag1_autocorr_of_pearson_residuals_n43_mid"],
            recomputed=obs["n43"]["lag1_autocorr_pearson_residuals_band"]),
    )

    # ---- analytic -------------------------------------------------------
    log("")
    log("[analytic] what each joint constraint can do to the MARGINAL variance")
    R["analytic"] = {"n43": analytic(F43), "n50": analytic(F50)}
    for tag in ("n43", "n50"):
        a = R["analytic"][tag]
        log("  %s JN-P (physical, full-support multinomial): Var/mu on the "
            "subset in [%.10f, %.10f]; max |pair corr| %.3e"
            % (tag, a["JN_P_physical"]["var_over_mu_subset_min"],
               a["JN_P_physical"]["var_over_mu_subset_max"],
               a["JN_P_physical"]["max_abs_pair_correlation_in_subset"]))
        log("  %s JN-2 (band total fixed):                   Var/mu on the "
            "subset in [%.6f, %.6f]; max |pair corr| %.3e"
            % (tag, a["JN_2_band_total"]["var_over_mu_subset_min"],
               a["JN_2_band_total"]["var_over_mu_subset_max"],
               a["JN_2_band_total"]["max_abs_pair_correlation_in_subset"]))
        log("  %s JN-3 (0/1 per cell per iteration):         Var/mu on the "
            "subset in [%.6f, %.6f]  (= N2's per-cell floor)"
            % (tag, a["JN_3_iteration"]["var_over_mu_subset_min"],
               a["JN_3_iteration"]["var_over_mu_subset_max"]))

    # ---- JOB A: the nulls ----------------------------------------------
    log("")
    log("[JOB A] running the nulls")
    R["job_A"] = {}
    plan = [
        ("n43", F43, "N1", REPS["n43_main"], {}),
        ("n43", F43, "N1x", REPS["n43_main"], {}),
        ("n43", F43, "N2", REPS["n43_main"], {}),
        ("n43", F43, "JN2", REPS["n43_main"], {}),
        ("n43", F43, "JN3", REPS["n43_main"], {}),
        ("n50", F50, "N1x", REPS["n50_main"], {}),
        ("n50", F50, "N2", REPS["n50_main"], {}),
        ("n50", F50, "JN2", REPS["n50_main"], {}),
        ("n50", F50, "JN3", REPS["n50_jn3"], {}),
    ]
    for tag, F, kind, reps, kw in plan:
        label = "%s|%s" % (tag, kind)
        res, _, _ = run_null(kind, F, reps, label, **kw)
        o = obs[tag]
        res["observed_stat_A"] = o["low_occupancy_subset_mean_t"]
        res["z_stat_A"] = z_of(o["low_occupancy_subset_mean_t"],
                               res["stat_A_mean"], res["stat_A_sd"])
        res["z_stat_A_reselected"] = z_of(o["low_occupancy_subset_mean_t"],
                                          res["stat_A_reselected_mean"],
                                          res["stat_A_reselected_sd"])
        res["z_stat_B"] = {}
        for L, v in res["stat_B"].items():
            ov = o["model_free_detrended_var_over_mean"].get(L)
            res["z_stat_B"][L] = dict(
                observed=ov, null_mean=v["mean"], null_sd=v["sd"],
                z=z_of(ov, v["mean"], v["sd"]))
        R["job_A"]["%s_%s" % (tag, kind)] = res
        log("  %-9s reps=%4d  %6.1fs  statA null %.4f +/- %.4f  z=%+.2f  "
            "(reselected %.4f +/- %.4f, z=%+.2f)"
            % (label, res["replicates"], res["seconds"], res["stat_A_mean"],
               res["stat_A_sd"], res["z_stat_A"] or 0.0,
               res["stat_A_reselected_mean"], res["stat_A_reselected_sd"],
               res["z_stat_A_reselected"] or 0.0))
        log("             instrument: Var/mu(subset)=%.4f  cross-cell "
            "dependence ratio=%.4f  lag1(t)=%+.4f  band-total sd=%.1f"
            % (res["measured_var_over_mu_on_subset_mean"],
               res["measured_cross_cell_dependence_ratio_on_subset"],
               res["lag1_t_subset_mean"], res["band_total_sd"]))
        for L in ("25", "50", "100"):
            if L in res["z_stat_B"]:
                d = res["z_stat_B"][L]
                log("             model-free L=%-3s obs %.4f null %.4f +/- "
                    "%.4f  z=%+.2f" % (L, d["observed"], d["null_mean"],
                                       d["null_sd"], d["z"]))

    # how wide would the null have to be?
    n2 = R["job_A"]["n43_N2"]
    needed = abs(n2["stat_A_mean"] - obs["n43"]["low_occupancy_subset_mean_t"]) / 2.0
    R["analytic"]["n43"]["sd_needed_for_z_above_minus_2"] = dict(
        null_mean_used=n2["stat_A_mean"], observed=obs["n43"]["low_occupancy_subset_mean_t"],
        sd_required=needed, sd_measured_under_N2=n2["stat_A_sd"],
        sd_inflation_factor_required=needed / n2["stat_A_sd"],
        variance_inflation_factor_required=(needed / n2["stat_A_sd"]) ** 2)
    log("")
    log("  to bring the 164-cell z above -2 the null sd would have to be "
        "%.4f, i.e. %.2fx the measured N2 sd %.4f (variance inflation %.2fx)"
        % (needed, needed / n2["stat_A_sd"], n2["stat_A_sd"],
           (needed / n2["stat_A_sd"]) ** 2))

    # ---- JN-4 grid: the only direction that can widen the null ----------
    log("")
    log("[JOB A] JN-4 grid -- spatially correlated dispersion (POSITIVE "
        "cross-cell dependence)")
    R["job_A_JN4"] = {}
    for sigma in (0.10, 0.20, 0.35, 0.55):
        for ell in (1.0, 5.0, 25.0):
            if elapsed() > GUARD_S:
                log("  !! wall-clock guard: JN-4 grid truncated")
                break
            label = "n43|JN4|s%.2f|l%.0f" % (sigma, ell)
            res, _, _ = run_null("JN4", F43, REPS["jn4"], label,
                                 sigma=sigma, ell=ell)
            o = obs["n43"]
            res["observed_stat_A"] = o["low_occupancy_subset_mean_t"]
            res["z_stat_A"] = z_of(o["low_occupancy_subset_mean_t"],
                                   res["stat_A_mean"], res["stat_A_sd"])
            res["z_stat_B"] = {}
            for L, v in res["stat_B"].items():
                ov = o["model_free_detrended_var_over_mean"].get(L)
                res["z_stat_B"][L] = dict(observed=ov, null_mean=v["mean"],
                                          null_sd=v["sd"],
                                          z=z_of(ov, v["mean"], v["sd"]))
            res["observed_lag1_t_subset"] = o["acf_t_subset_1_to_12"][0]
            res["observed_lag1_z_against_this_null"] = z_of(
                o["acf_t_subset_1_to_12"][0], res["lag1_t_subset_mean"],
                res["lag1_t_subset_sd"])
            R["job_A_JN4"]["s%.2f_l%.0f" % (sigma, ell)] = res
            log("  sigma=%.2f ell=%4.0f  statA null %.4f +/- %.4f  z=%+.2f | "
                "null lag1(t)=%+.4f +/- %.4f, observed %+.4f is z=%+.2f there "
                "| L=25 z=%+.2f"
                % (sigma, ell, res["stat_A_mean"], res["stat_A_sd"],
                   res["z_stat_A"], res["lag1_t_subset_mean"],
                   res["lag1_t_subset_sd"], res["observed_lag1_t_subset"],
                   res["observed_lag1_z_against_this_null"],
                   res["z_stat_B"]["25"]["z"] if "25" in res["z_stat_B"] else 0.0))

    # ---- JOB B ----------------------------------------------------------
    log("")
    log("[JOB B] occupancy versus score position")
    rows, coords, designs, Kp = jobB_designs(F43, F50)
    b, occ_vec = jobB_static(rows, coords, designs, Kp, F43, F50)
    R["job_B"] = b
    R["job_B"]["pooled_cells"] = Kp

    t43 = terms(F43["D"], F43["mu"], F43["h"])
    t50 = terms(F50["D"], F50["mu"], F50["h"])
    tvec = t43 + t50
    beta_obs = jobB_beta(designs, tvec)
    R["job_B"]["B4_observed_occupancy_coefficients"] = beta_obs

    log("  within-file: %s" % json.dumps(b["B1_within_file_monotonicity"]))
    for cname, d in b["B2_cross_file_occupancy_contrast_at_matched_position"].items():
        log("  coordinate %-9s bins with both files %d/10, occupancy ratio "
            "n43/n50 across bins: min %.3f max %.3f geomean %.3f"
            % (cname, d["bins_with_both_files"],
               d["occ_ratio_min"] or 0.0, d["occ_ratio_max"] or 0.0,
               d["occ_ratio_geomean"] or 0.0))

    # calibrate the occupancy coefficient under N2 (independent) and JN3 (joint)
    log("  calibrating the occupancy coefficient ...")
    R["job_B"]["B5_calibrated_occupancy_coefficient"] = {}
    for nullkind, reps in (("N2", REPS["jobB_N2"]), ("JN3", REPS["jobB_JN3"])):
        if elapsed() > GUARD_S:
            log("  !! wall-clock guard: Job B calibration truncated at %s"
                % nullkind)
            break
        r43 = rng_for("jobB|%s|n43" % nullkind)
        r50 = rng_for("jobB|%s|n50" % nullkind)
        g43 = make_gen(nullkind, F43, r43)
        g50 = make_gen(nullkind, F50, r50)
        acc = {k: [] for k in designs}
        nok = 0
        t0 = time.time()
        for _ in range(reps):
            try:
                D43, D50 = g43(), g50()
                _b, m43, h43, _P = b015.glm(D43, F43["lo"], F43["hi"],
                                            F43["degree"])
                _b, m50, h50, _P = b015.glm(D50, F50["lo"], F50["hi"],
                                            F50["degree"])
                tv = terms(D43, m43, h43) + terms(D50, m50, h50)
            except (FloatingPointError, ZeroDivisionError, OverflowError):
                continue
            bb = jobB_beta(designs, tv)
            for k, v in bb.items():
                acc[k].append(v)
            nok += 1
            if elapsed() > GUARD_S:
                break
        rec = {}
        for k, v in acc.items():
            if not v:
                continue
            m, s = mean_sd(v)
            rec[k] = dict(null_mean=m, null_sd=s, observed=beta_obs.get(k),
                          z=z_of(beta_obs.get(k), m, s))
        R["job_B"]["B5_calibrated_occupancy_coefficient"][nullkind] = dict(
            replicates=nok, seconds=time.time() - t0, per_spec=rec,
            seeds=[SEEDS["jobB|%s|n43" % nullkind],
                   SEEDS["jobB|%s|n50" % nullkind]])
        log("  [%s] %d replicates, %.1fs" % (nullkind, nok, time.time() - t0))
        for k in sorted(rec):
            d3 = b["B3_specification_diagnostics"][k]
            log("    %-28s beta=%+9.4f null %+8.4f +/- %7.4f z=%+6.2f | "
                "eff design size %8.2f of %d | VIF %10.1f"
                % (k, rec[k]["observed"], rec[k]["null_mean"],
                   rec[k]["null_sd"], rec[k]["z"],
                   d3.get("effective_design_size_participation_ratio") or -1,
                   Kp, d3.get("variance_inflation_factor") or -1))

    # ---- provenance ------------------------------------------------------
    R["seeds"] = dict(SEEDS)
    R["seed_scheme"] = ("seed(name) = %d + sum_i (i+1)*ord(name[i]); every "
                        "stream name and its integer seed is listed in "
                        "results.json -> seeds" % SEED_BASE)
    R["replicate_plan"] = REPS
    try:
        commit = subprocess.check_output(
            ["git", "-C", REPO, "rev-parse", "HEAD"]).decode().strip()
        dirty = subprocess.check_output(
            ["git", "-C", REPO, "status", "--porcelain"]).decode()
    except Exception as exc:                      # pragma: no cover
        commit, dirty = "unavailable: %s" % exc, ""
    ru = resource.getrusage(resource.RUSAGE_SELF)
    receipt = dict(
        task="TASK-20260806-518328",
        wall_clock_seconds=elapsed(),
        wall_clock_budget_seconds=WALL_BUDGET_S,
        peak_rss_bytes=ru.ru_maxrss * 1024,
        peak_rss_mb=ru.ru_maxrss / 1024.0,
        memory_budget_gb=4,
        user_cpu_seconds=ru.ru_utime, system_cpu_seconds=ru.ru_stime,
        python=platform.python_version(),
        platform=platform.platform(),
        git_commit=commit,
        git_tree_dirty=bool(dirty.strip()),
        git_status_porcelain_lines=len([x for x in dirty.splitlines() if x]),
        command=("PYTHONDONTWRITEBYTECODE=1 python3 joint_null.py "
                 "> stdout.txt 2> stderr.txt"),
        runs_declared=1,
        no_new_sampling_of_the_physical_system=True,
        input_sha256={F["tag"]: F["sha256"] for F in (F43, F50)},
    )
    R["provenance"] = receipt
    with open(os.path.join(HERE, "results.json"), "w") as fh:
        json.dump(R, fh, indent=1, sort_keys=True)
    with open(os.path.join(HERE, "resource_receipt.json"), "w") as fh:
        json.dump(receipt, fh, indent=1, sort_keys=True)
    log("")
    log("wrote results.json and resource_receipt.json")
    log("wall clock %.1f s of %.0f s budget; peak RSS %.1f MB of 4096 MB"
        % (receipt["wall_clock_seconds"], WALL_BUDGET_S,
           receipt["peak_rss_mb"]))
    log("OBSERVATIONS ONLY.  No conclusion is drawn here about whether the "
        "deficit is real, nor about Approximation 4.9.")


if __name__ == "__main__":
    main()
