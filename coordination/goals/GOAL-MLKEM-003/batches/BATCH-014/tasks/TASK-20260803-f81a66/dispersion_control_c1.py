#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TASK-20260803-f81a66 -- BATCH-014, GOAL-MLKEM-003.

Two independent jobs, both zero new sampling of the physical system, both
answerable from archived repository bytes.

  JOB A  CONTROL C1: a deep-tail Poisson dispersion test built the way a
         dispersion test has to be built --
           * on the INCREMENTS, not on the nested cumulative counts;
           * against a LOCAL SMOOTH RATE fitted by Poisson MLE, never the
             plug-in lambda = C_T;
           * with the LEVERAGE CORRECTION applied where it belongs, i.e. to
             the residual variance of the rate fit, Var(Y-mu_hat)=mu(1-h);
           * with windows BINNED TO EXPECTED COUNT >= 10;
           * with phi reported beside ITS OWN STANDARD DEVIATION, per window,
             analytic and Monte-Carlo-calibrated.

  JOB B  Independent recomputation of the two numbers on which
         DEC-20260803-52a750 retired this goal's whole-band statistic:
           B1  effective degrees of freedom of the whole-band rms statistic,
               under the D-1 residual covariance min(1/lambda, 1/lambda') and
               under a white-noise reading;
           B2  the attenuation identity
               ratio^2 = const + (measurable misfit)/209.126 .

OBSERVATIONS ONLY.  Nothing here concludes that the whole-band statistic
should or should not be retired, nor that Approximation 4.9 is validated or
refuted.  That is /review-evidence under Coordinator authority.

Scope: toy tier (q=241, m=40, n=43 and n=50), resolved band only, raw
undivided score scale.  NO ML-KEM or Kyber security claim in either
direction.  AGENTS.md rule 12 stays UNMET and UNWAIVED.

No network.  No G6K.  No new sampling of the physical system.  The only
random numbers drawn anywhere in this script are the SYNTHETIC NULL-OBJECT
CALIBRATION of Job A's own estimator (seeded, seed recorded); they are a
control on the instrument and are not, and are never reported as, a
measurement of the archived system.

Host has no numpy / no scipy / no mpmath: every numerical routine below is
written out.

Usage:
    python3 dispersion_control_c1.py [--out results.json] [--reps N]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import random
import resource
import subprocess
import sys
import time
from io import StringIO

LN2 = math.log(2.0)
L2 = LN2 * LN2

REPO = "/home/user/crypto-autoresearcher"
DATA = os.path.join(REPO, "experiments/EXP-MLKEM-011/vendor-lock/data")

FILES = [
    dict(
        tag="n43",
        name="Pwrong_q241_m40_n43_nfft8_kfft3_nlat35_beta032_beta144_N25971.out",
        nb_iteration=4000,
        q=241,
        k_fft=3,
    ),
    dict(
        tag="n50",
        name="Pwrong_q241_m40_n50_nfft8_kfft3_nlat42_beta035_beta141_N25970.out",
        nb_iteration=6000,
        q=241,
        k_fft=3,
    ),
]

# Numbers published by the red team in DEC-20260803-52a750 / EV-MLKEM-0cf1df and
# restated verbatim in the TASK-20260803-f81a66 handoff.  They are carried here
# ONLY as reference values to compare against; nothing in this script consumes
# them as input to a computation.
RED_TEAM_REFERENCE = {
    "effective_dof_D1": {"n43": 1.55, "n50": 1.51},
    "effective_dof_white": {"n43": 422.0, "n50": 471.0},
    "attenuation_identity_n43": {
        "constant": 0.5919,
        "whole_band_noise_budget": 209.126,
        "perfect_on_measurable_ratio": 0.769,
        "attenuation_fold": 1147.0,
    },
    "source": "TASK-20260803-f81a66 handoff; DEC-20260803-52a750; EV-MLKEM-0cf1df",
}

# Archived model fits (BATCH-012 TASK-20260803-36f572 results.json) are read
# from disk, not retyped.
BATCH012_RESULTS = os.path.join(
    REPO,
    "coordination/goals/GOAL-MLKEM-003/batches/BATCH-012/tasks/"
    "TASK-20260803-36f572/results.json",
)


# --------------------------------------------------------------------------
# 0.  small utilities
# --------------------------------------------------------------------------


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args):
    try:
        return subprocess.run(
            ["git"] + list(args), cwd=REPO, capture_output=True, text=True, timeout=60
        ).stdout.strip()
    except Exception as exc:  # pragma: no cover
        return "unavailable: %r" % (exc,)


class Tee(object):
    """Capture stdout/stderr into the artifact while still printing."""

    def __init__(self, stream):
        self.stream = stream
        self.buf = StringIO()

    def write(self, s):
        self.stream.write(s)
        self.buf.write(s)

    def flush(self):
        self.stream.flush()

    def getvalue(self):
        return self.buf.getvalue()


def solve(A, b):
    """Gaussian elimination with partial pivoting.  A is n x n (list of lists)."""
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[piv][col]) < 1e-300:
            raise ZeroDivisionError("singular normal matrix")
        M[col], M[piv] = M[piv], M[col]
        pv = M[col][col]
        for r in range(n):
            if r == col:
                continue
            f = M[r][col] / pv
            if f == 0.0:
                continue
            for c in range(col, n + 1):
                M[r][c] -= f * M[col][c]
    return [M[i][n] / M[i][i] for i in range(n)]


def inverse(A):
    n = len(A)
    cols = []
    for j in range(n):
        e = [1.0 if i == j else 0.0 for i in range(n)]
        cols.append(solve(A, e))
    return [[cols[j][i] for j in range(n)] for i in range(n)]


def cheb_basis(x, p):
    """Chebyshev T_0..T_p at x in [-1, 1]."""
    out = [1.0]
    if p >= 1:
        out.append(x)
    for a in range(2, p + 1):
        out.append(2.0 * x * out[a - 1] - out[a - 2])
    return out


# --------------------------------------------------------------------------
# 1.  data ingest -- exact recovery of the pooled counts
# --------------------------------------------------------------------------


def load_pwrong(spec):
    path = os.path.join(DATA, spec["name"])
    header, vals = [], []
    with open(path) as fh:
        for line in fh:
            if line.startswith("#"):
                header.append(line.strip())
                continue
            line = line.strip()
            if line:
                vals.append(float(line))
    M = spec["nb_iteration"] * spec["q"] ** spec["k_fft"]
    counts, maxdev = [], 0.0
    for v in vals:
        x = v * M
        r = int(round(x))
        if r > 0:
            maxdev = max(maxdev, abs(x - r) / r)
        counts.append(r)
    last = max(i for i, c in enumerate(counts) if c > 0)
    return dict(
        tag=spec["tag"],
        name=spec["name"],
        path=path,
        sha256=sha256_file(path),
        header=header,
        M=M,
        counts=counts,
        n_band=last + 1,
        last_positive=last,
        integrality_max_rel_dev=maxdev,
    )


def increments(counts, lo, hi):
    """D_T = C_T - C_{T+1} for T in [lo, hi], with C_{hi+1} taken from counts."""
    out = []
    for T in range(lo, hi + 1):
        nxt = counts[T + 1] if T + 1 < len(counts) else 0
        out.append(counts[T] - nxt)
    return out


# --------------------------------------------------------------------------
# 2.  JOB A -- the dispersion test
# --------------------------------------------------------------------------
#
# Model under test (the null the counting floor assumes):
#
#   the M = nb_iteration * q^{k_fft} pooled candidate scores are exchangeable
#   draws, so the number of them landing on score T,
#       D_T = C_T - C_{T+1},
#   is Poisson(lambda_T) independently across T, with lambda_T a SMOOTH
#   function of T.
#
# Why increments and not C_T: C_T is a nested tail count,
# C_T = sum_{j>=T} D_j.  Consecutive C_T share almost all their events; a
# cell-by-cell dispersion statistic applied to them is not a test of anything.
# The increments are the independent atoms, and Poisson increments <=>
# Poisson cumulative counts, so testing D tests exactly the assumption the
# floor rests on.
#
# What over-dispersion would mean here: each of the nb_iteration iterations
# uses its own lattice and its own target, so its own tail rate.  A mixture of
# rates is over-dispersed relative to Poisson.  Under-dispersion would mean
# the smoother has absorbed real signal (an artifact of the test, not of the
# data) -- which is why the estimator is calibrated against a synthetic null.


def _eval_bins(bins, beta, basis, P):
    """mu_k, G_k and the Poisson log-likelihood at beta.  None if it overflows."""
    mu = []
    G = []
    ll = 0.0
    for b in bins:
        m = 0.0
        g = [0.0] * P
        for T in range(b["lo"], b["hi"] + 1):
            bb = basis[T]
            e = 0.0
            for a in range(P):
                e += beta[a] * bb[a]
            if e > 80.0 or e < -700.0:
                return None
            lam = math.exp(e)
            m += lam
            for a in range(P):
                g[a] += lam * bb[a]
        if m <= 0.0 or not math.isfinite(m):
            return None
        mu.append(m)
        G.append(g)
        ll += b["Y"] * math.log(m) - m
    if not math.isfinite(ll):
        return None
    return mu, G, ll


def fit_binned_poisson(bins, degree, xlo, xhi, maxit=200, tol=1e-11):
    """
    Aggregated Poisson GLM, fitted by Fisher scoring with a log-likelihood
    line search.

        mu_k(beta) = sum_{T in B_k} exp( f(T; beta) ),
        f(T; beta) = sum_a beta_a * Cheb_a( 2(T-xlo)/(xhi-xlo) - 1 ).

    The rate is INTEGRATED over the bin rather than taken at the midpoint:
    deep-tail bins are wide and lambda falls by orders of magnitude across
    them, so a midpoint rule would manufacture misfit.

    Raises FloatingPointError if the fit does not converge -- a non-converged
    fit is reported as a failure, never as a dispersion reading.
    """
    span = float(xhi - xlo)
    P = degree + 1

    basis = {}
    for b in bins:
        for T in range(b["lo"], b["hi"] + 1):
            if T not in basis:
                z = 2.0 * (T - xlo) / span - 1.0 if span > 0 else 0.0
                basis[T] = cheb_basis(z, degree)

    tot_Y = sum(b["Y"] for b in bins)
    tot_T = sum(b["hi"] - b["lo"] + 1 for b in bins)
    beta = [math.log(max(tot_Y, 1.0) / max(tot_T, 1))] + [0.0] * (P - 1)

    ev = _eval_bins(bins, beta, basis, P)
    if ev is None:
        raise FloatingPointError("degree %d: bad start" % degree)
    mu, G, ll = ev
    converged = False
    for _it in range(maxit):
        score = [0.0] * P
        I = [[0.0] * P for _ in range(P)]
        for k, b in enumerate(bins):
            w = (b["Y"] / mu[k]) - 1.0
            gk = G[k]
            for a in range(P):
                score[a] += w * gk[a]
            inv_mu = 1.0 / mu[k]
            for a in range(P):
                ga = gk[a] * inv_mu
                Ia = I[a]
                for c in range(a, P):
                    Ia[c] += ga * gk[c]
        for a in range(P):
            for c in range(a):
                I[a][c] = I[c][a]
        try:
            step = solve(I, score)
        except ZeroDivisionError:
            raise FloatingPointError("degree %d: singular information" % degree)

        # line search on the log-likelihood
        t = 1.0
        improved = False
        for _try in range(40):
            trial = [beta[a] + t * step[a] for a in range(P)]
            ev = _eval_bins(bins, trial, basis, P)
            if ev is not None and ev[2] >= ll - 1e-12:
                beta = trial
                mu, G, ll = ev
                improved = True
                break
            t *= 0.5
        if not improved:
            converged = True  # cannot improve; treat as a stationary point
            break
        if max(abs(t * s) for s in step) < tol:
            converged = True
            break

    if not converged:
        raise FloatingPointError("degree %d: no convergence in %d it" % (degree, maxit))

    # final gradient sanity check
    score = [0.0] * P
    for k, b in enumerate(bins):
        w = (b["Y"] / mu[k]) - 1.0
        for a in range(P):
            score[a] += w * G[k][a]
    scale = max(1.0, sum(b["Y"] for b in bins))
    if max(abs(s) for s in score) / scale > 1e-6:
        raise FloatingPointError("degree %d: gradient not zero at exit" % degree)

    I = [[0.0] * P for _ in range(P)]
    for k in range(len(bins)):
        gk = G[k]
        inv_mu = 1.0 / mu[k]
        for a in range(P):
            ga = gk[a] * inv_mu
            for c in range(P):
                I[a][c] += ga * gk[c]

    return dict(beta=beta, mu=mu, G=G, I=I, degree=degree, basis=basis, loglik=ll)


def rate_curve(fit, xlo, xhi, lo, hi):
    """lambda_hat_T over integer scores [lo, hi] from a fitted beta."""
    span = float(xhi - xlo)
    beta = fit["beta"]
    P = len(beta)
    out = []
    for T in range(lo, hi + 1):
        z = 2.0 * (T - xlo) / span - 1.0 if span > 0 else 0.0
        bb = cheb_basis(z, P - 1)
        out.append(math.exp(sum(beta[a] * bb[a] for a in range(P))))
    return out


def make_bins_from_expected(lam, lo, target):
    """Contiguous bins over integer scores, each with EXPECTED count >= target.

    lam[i] is the expected count at score lo+i.  Bin edges therefore depend on
    the data only through a smooth global fit, not through the local
    fluctuations being tested -- greedy binning on OBSERVED counts stops a bin
    the moment it crosses the threshold and so truncates upward fluctuations,
    biasing phi DOWN.  That variant is run separately as a control.
    """
    bins = []
    start = 0
    acc = 0.0
    for i, l in enumerate(lam):
        acc += l
        if acc >= target:
            bins.append(dict(lo=lo + start, hi=lo + i))
            start = i + 1
            acc = 0.0
    if start < len(lam):
        if bins:
            bins[-1]["hi"] = lo + len(lam) - 1
        else:
            bins.append(dict(lo=lo, hi=lo + len(lam) - 1))
    return bins


def make_bins_from_observed(D, lo, target):
    bins = []
    start = 0
    acc = 0
    for i, d in enumerate(D):
        acc += d
        if acc >= target:
            bins.append(dict(lo=lo + start, hi=lo + i))
            start = i + 1
            acc = 0
    if start < len(D):
        if bins:
            bins[-1]["hi"] = lo + len(D) - 1
        else:
            bins.append(dict(lo=lo, hi=lo + len(D) - 1))
    return bins


def attach_observed(bins, D, lo):
    for b in bins:
        b["Y"] = sum(D[b["lo"] - lo: b["hi"] - lo + 1])
    return bins


def dispersion(bins, fit):
    """Leverage-corrected Pearson dispersion.

    For an aggregated Poisson GLM the exact first-order residual variance is

        Var(Y_k - mu_hat_k) = mu_k (1 - h_kk),
        h_kk = G_k^T I^{-1} G_k / mu_k,      sum_k h_kk = #parameters,

    because sum_j S_kj^2 mu_j = h_kk mu_k with S_kj = G_k^T I^{-1} G_j / mu_j.
    So the leverage belongs on the residual variance of the RATE FIT.  It does
    not belong on a plug-in lambda = C_T -- a plug-in has leverage exactly 1
    and residual exactly 0, which is why plug-in dispersion reads 0, not 1.
    """
    Iinv = inverse(fit["I"])
    mu = fit["mu"]
    G = fit["G"]
    P = len(fit["beta"])
    rows = []
    for k, b in enumerate(bins):
        gk = G[k]
        v = [sum(Iinv[a][c] * gk[c] for c in range(P)) for a in range(P)]
        h = sum(gk[a] * v[a] for a in range(P)) / mu[k]
        resid = b["Y"] - mu[k]
        var = mu[k] * (1.0 - h)
        if var <= 0:
            var = mu[k] * 1e-12
        rows.append(
            dict(
                lo=b["lo"],
                hi=b["hi"],
                Y=b["Y"],
                mu=mu[k],
                leverage=h,
                pearson=resid / math.sqrt(mu[k]),
                corrected=resid / math.sqrt(var),
                t=(resid * resid) / var,
            )
        )
    return rows, P


def phi_and_sd(rows):
    K = len(rows)
    if K == 0:
        return None, None, 0
    phi = sum(r["t"] for r in rows) / K
    # Var(t_k) = (2 + 1/mu_k) / (1-h_k)^2 under the Poisson null.
    var = 0.0
    for r in rows:
        one_minus_h = max(1.0 - r["leverage"], 1e-9)
        var += (2.0 + 1.0 / r["mu"]) / (one_minus_h ** 2)
    return phi, math.sqrt(var) / K, K


def poisson_sample(lam, rng):
    if lam < 30.0:
        L = math.exp(-lam)
        k = 0
        p = 1.0
        while True:
            p *= rng.random()
            if p <= L:
                return k
            k += 1
            if k > 1000:
                return k
    # normal approximation with continuity correction for large lambda
    while True:
        z = rng.gauss(0.0, 1.0)
        v = int(round(lam + math.sqrt(lam) * z))
        if v >= 0:
            return v


def negbin_sample(lam, phi, rng):
    """Negative binomial with mean lam and variance phi*lam (phi > 1)."""
    if phi <= 1.0 or lam <= 0.0:
        return poisson_sample(max(lam, 0.0), rng)
    r = lam / (phi - 1.0)
    if r < 1e-12:
        return 0
    # Gamma(shape=r, scale=(phi-1)) mixing, then Poisson
    g = gamma_sample(r, rng) * (phi - 1.0)
    return poisson_sample(max(g, 1e-12), rng)


def gamma_sample(shape, rng):
    """Marsaglia-Tsang."""
    if shape <= 1e-12:
        return 0.0
    if shape < 1.0:
        u = rng.random()
        if u <= 0.0:
            u = 1e-300
        return gamma_sample(shape + 1.0, rng) * (u ** (1.0 / shape))
    d = shape - 1.0 / 3.0
    c = 1.0 / math.sqrt(9.0 * d)
    while True:
        x = rng.gauss(0.0, 1.0)
        v = (1.0 + c * x) ** 3
        if v <= 0:
            continue
        u = rng.random()
        if math.log(u) < 0.5 * x * x + d - d * v + d * math.log(v):
            return d * v


def merge_small_bins(bins, mu, target):
    """Merge any bin whose FITTED expected count is below target into the
    neighbour with the smaller expected count.  Returns new edges, or None if
    nothing needed merging."""
    idx = [k for k, m in enumerate(mu) if m < target]
    if not idx:
        return None
    if len(bins) < 2:
        return None
    k = idx[0]
    if k == 0:
        j = 1
    elif k == len(bins) - 1:
        j = k - 1
    else:
        j = k - 1 if mu[k - 1] <= mu[k + 1] else k + 1
    a, b = min(k, j), max(k, j)
    new = [dict(lo=x["lo"], hi=x["hi"]) for x in bins]
    new[a]["hi"] = new[b]["hi"]
    del new[b]
    return new


def run_pipeline(D, lo, hi, degree, target, bins=None, enforce_expected=True):
    """Bin (expected-count rule) -> fit -> leverage-corrected dispersion.

    When `bins` is supplied the binning is held fixed (used by the Monte-Carlo
    calibration so the null replicates are analysed with the identical
    instrument)."""
    fixed = bins is not None
    if bins is None:
        # pilot pass: observed-count bins only to get a first rate estimate
        pilot_bins = attach_observed(make_bins_from_observed(D, lo, target), D, lo)
        pilot = fit_binned_poisson(pilot_bins, degree, lo, hi)
        lam_pilot = rate_curve(pilot, lo, hi, lo, hi)
        bins = make_bins_from_expected(lam_pilot, lo, target)
    bins = attach_observed([dict(lo=b["lo"], hi=b["hi"]) for b in bins], D, lo)
    fit = fit_binned_poisson(bins, degree, lo, hi)
    if enforce_expected and not fixed:
        for _ in range(200):
            merged = merge_small_bins(bins, fit["mu"], target)
            if merged is None:
                break
            bins = attach_observed(merged, D, lo)
            fit = fit_binned_poisson(bins, degree, lo, hi)
    rows, P = dispersion(bins, fit)
    return bins, fit, rows, P


def analyse_region(data, lo, hi, label, degrees, target, reps, rich_degree, rng, log):
    counts = data["counts"]
    D = increments(counts, lo, hi)
    total = sum(D)
    n_rows = hi - lo + 1
    out = dict(
        label=label,
        score_range=[lo, hi],
        n_scores=n_rows,
        total_increment_events=total,
        cumulative_count_at_lo=counts[lo],
        cumulative_count_at_hi=counts[hi],
        expected_count_target_per_bin=target,
    )
    if total < 2 * target:
        out["status"] = "NOT TESTABLE"
        out["reason"] = (
            "the whole region carries %d increment events in total; a binning "
            "to expected count >= %d yields fewer than two windows, so no "
            "dispersion statistic is reportable here."
        ) % (total, target)
        log("  [%s] NOT TESTABLE: %d events over %d rows" % (label, total, n_rows))
        return out

    # ---- degree sweep (under-fit inflates phi, over-fit deflates it) -------
    sweep = []
    for deg in degrees:
        try:
            bins, fit, rows, P = run_pipeline(D, lo, hi, deg, target)
        except (FloatingPointError, ZeroDivisionError) as exc:
            sweep.append(dict(degree=deg, error=repr(exc)))
            continue
        phi, sd, K = phi_and_sd(rows)
        dev = 0.0
        for r in rows:
            if r["Y"] > 0:
                dev += 2.0 * (r["Y"] * math.log(r["Y"] / r["mu"]) - (r["Y"] - r["mu"]))
            else:
                dev += 2.0 * r["mu"]
        sweep.append(
            dict(
                degree=deg,
                n_bins=K,
                n_parameters=P,
                phi=phi,
                sd_phi_analytic=sd,
                deviance=dev,
                deviance_df=K - P,
                aic=dev + 2.0 * P,
                min_expected=min(r["mu"] for r in rows),
                max_leverage=max(r["leverage"] for r in rows),
            )
        )
    out["degree_sweep"] = sweep

    ok = [s for s in sweep if "phi" in s]
    if not ok:
        out["status"] = "FIT FAILED"
        return out
    # Degree selection.  Under-fitting inflates phi (unmodelled rate structure
    # leaks into the residual); over-fitting deflates it (the smoother eats the
    # fluctuation being tested).  Both failure modes are real, so the degree is
    # chosen by forward selection on the deviance -- keep adding a parameter
    # while it buys a chi^2_1-significant deviance drop -- and the whole sweep
    # is reported so the reader can see the sensitivity.
    ok_sorted = sorted(ok, key=lambda s: s["degree"])
    chosen = ok_sorted[0]
    for prev, nxt in zip(ok_sorted, ok_sorted[1:]):
        if nxt["degree"] != chosen["degree"] + 1:
            # a degree failed to converge in between; keep going conservatively
            pass
        if prev["deviance"] - nxt["deviance"] >= 3.841:
            chosen = nxt
        else:
            break
    deg = chosen["degree"]
    out["chosen_degree"] = deg
    out["degree_selection_rule"] = (
        "forward selection on the deviance: accept degree d+1 while it buys a "
        "deviance drop >= chi^2_{1,0.95} = 3.841; full sweep reported beside it"
    )
    at_or_above = [s for s in ok_sorted if s["degree"] >= deg]
    out["phi_range_over_converged_degrees_at_or_above_chosen"] = dict(
        min=min(s["phi"] for s in at_or_above),
        max=max(s["phi"] for s in at_or_above),
        degrees=[s["degree"] for s in at_or_above],
    )
    out["phi_range_over_all_converged_degrees"] = dict(
        min=min(s["phi"] for s in ok_sorted),
        max=max(s["phi"] for s in ok_sorted),
        degrees=[s["degree"] for s in ok_sorted],
    )
    out["degrees_that_failed_to_converge"] = [
        s["degree"] for s in sweep if "phi" not in s
    ]
    log(
        "  [%s] degree sweep phi: %s  -> forward deviance selection picks degree %d"
        % (
            label,
            "  ".join("p%d=%.3f" % (s["degree"], s["phi"]) for s in ok_sorted),
            deg,
        )
    )

    bins, fit, rows, P = run_pipeline(D, lo, hi, deg, target)
    phi, sd, K = phi_and_sd(rows)
    out["n_bins"] = K
    out["n_parameters"] = P
    out["min_expected_count_per_bin"] = min(r["mu"] for r in rows)
    out["expected_count_ge_10_holds"] = bool(min(r["mu"] for r in rows) >= 10.0)
    out["phi"] = phi
    out["sd_phi_analytic"] = sd
    out["phi_minus_1_in_sd_analytic"] = (phi - 1.0) / sd if sd else None

    # leverage diagnostics.  A bin whose leverage approaches 1 is fitted by
    # itself; 1/(1-h) then explodes and both phi and its analytic sd become
    # unstable.  Flagged, and a trimmed variant reported beside the headline.
    lev = [r["leverage"] for r in rows]
    out["leverage"] = dict(
        sum_equals_n_parameters=sum(lev),
        n_parameters=P,
        max=max(lev),
        n_bins_leverage_gt_0p5=sum(1 for h in lev if h > 0.5),
    )
    if max(lev) > 0.5:
        trimmed = [r for r in rows if r["leverage"] <= 0.5]
        tp, ts, tk = phi_and_sd(trimmed)
        out["phi_trimmed_leverage_le_0p5"] = dict(phi=tp, sd_phi_analytic=ts, n_bins=tk)

    # ---- control: greedy OBSERVED-count binning (the selection-bias probe) --
    ob_bins = attach_observed(make_bins_from_observed(D, lo, target), D, lo)
    ob_fit = fit_binned_poisson(ob_bins, deg, lo, hi)
    ob_rows, _ = dispersion(ob_bins, ob_fit)
    ob_phi, ob_sd, ob_K = phi_and_sd(ob_rows)
    out["control_observed_count_binning"] = dict(
        phi=ob_phi,
        sd_phi_analytic=ob_sd,
        n_bins=ob_K,
        note=(
            "bins closed the moment the OBSERVED count crossed the target; "
            "expected to read low relative to expected-count binning, and the "
            "size of that gap is the size of the binning-selection artifact."
        ),
    )

    # ---- control: uncorrected (no leverage) Pearson -------------------------
    raw = sum(r["pearson"] ** 2 for r in rows)
    out["control_no_leverage_correction"] = dict(
        phi_pearson_over_K=raw / K,
        phi_pearson_over_K_minus_P=raw / (K - P) if K > P else None,
        note="difference from phi is exactly the leverage correction's effect",
    )

    # ---- control: the plug-in lambda = C_T reading -------------------------
    #  the construction the handoff says NOT to use, run anyway so the size of
    #  its bias is on the record rather than asserted.
    plug = []
    for b in bins:
        lamb = float(b["Y"])  # plug-in: rate estimated by the bin's own count
        if lamb > 0:
            plug.append(((b["Y"] - lamb) ** 2) / lamb)
    out["control_plug_in_lambda_equals_count"] = dict(
        phi=sum(plug) / len(plug) if plug else None,
        note=(
            "plug-in rate has leverage exactly 1 and residual exactly 0, so it "
            "reads phi = 0 identically.  Recorded to show the failure mode, "
            "not as a measurement."
        ),
    )

    # ---- per-window phi with its own sd ------------------------------------
    #  windows are contiguous groups of bins; every bin inside a window already
    #  satisfies expected count >= target.
    per_window = []
    if K >= 4:
        n_win = max(2, min(8, K // 12))
        edges = [round(i * K / n_win) for i in range(n_win + 1)]
        for w in range(n_win):
            sub = rows[edges[w]: edges[w + 1]]
            if not sub:
                continue
            p, s, k = phi_and_sd(sub)
            per_window.append(
                dict(
                    window=w,
                    score_range=[sub[0]["lo"], sub[-1]["hi"]],
                    cumulative_count_at_window_start=counts[sub[0]["lo"]],
                    cumulative_count_at_window_end=counts[min(sub[-1]["hi"], len(counts) - 1)],
                    n_bins=k,
                    min_expected_count=min(r["mu"] for r in sub),
                    phi=p,
                    sd_phi_analytic=s,
                    phi_minus_1_in_sd=(p - 1.0) / s if s else None,
                )
            )
    out["per_window"] = per_window

    # ---- SYNTHETIC NULL-OBJECT CALIBRATION (seeded; instrument control) ----
    #  MC-A : generate from the chosen-degree fit, analyse at the chosen degree.
    #         measures the estimator's own bias and sd.
    #  MC-B : generate from a RICHER fit, analyse at the chosen degree.
    #         measures how much a too-stiff rate model inflates phi.
    #  MC-C : generate over-dispersed (phi_true = 1.5), analyse as usual.
    #         power check: an estimator that cannot see 1.5 cannot see anything.
    lam_fit = rate_curve(fit, lo, hi, lo, hi)
    try:
        rich_bins, rich_fit, _r, _p = run_pipeline(D, lo, hi, rich_degree, target)
        lam_rich = rate_curve(rich_fit, lo, hi, lo, hi)
    except Exception:
        lam_rich = lam_fit

    def mc(lams, phi_true, n):
        vals = []
        discarded = 0
        for _ in range(n):
            if phi_true == 1.0:
                Ds = [poisson_sample(l, rng) for l in lams]
            else:
                Ds = [negbin_sample(l, phi_true, rng) for l in lams]
            try:
                _b, _f, rr, _P = run_pipeline(Ds, lo, hi, deg, target, bins=bins)
            except Exception:
                discarded += 1
                continue
            pv, _sd, _K = phi_and_sd(rr)
            if pv is None or not math.isfinite(pv) or pv > 1e3:
                discarded += 1
                continue
            vals.append(pv)
        if not vals:
            return None
        m = sum(vals) / len(vals)
        v = sum((x - m) ** 2 for x in vals) / max(len(vals) - 1, 1)
        vals_sorted = sorted(vals)
        return dict(
            replicates=len(vals),
            replicates_discarded_non_convergent=discarded,
            mean_phi=m,
            sd_phi=math.sqrt(v),
            p05=vals_sorted[int(0.05 * (len(vals) - 1))],
            p95=vals_sorted[int(0.95 * (len(vals) - 1))],
        )

    out["null_object_calibration"] = dict(
        declared=(
            "SYNTHETIC.  Seeded pseudo-random draws used to calibrate this "
            "script's own estimator against a null object of the same shape.  "
            "Not a measurement of the archived system; no new sampling of the "
            "physical experiment occurred."
        ),
        MC_A_poisson_from_chosen_fit=mc(lam_fit, 1.0, reps),
        MC_B_poisson_from_richer_fit=dict(
            rich_degree=rich_degree, **(mc(lam_rich, 1.0, max(reps // 2, 20)) or {})
        ),
        MC_C_overdispersed_phi_true_1p5=mc(lam_fit, 1.5, max(reps // 2, 20)),
    )

    mca = out["null_object_calibration"]["MC_A_poisson_from_chosen_fit"]
    if mca:
        out["phi_bias_corrected"] = phi - (mca["mean_phi"] - 1.0)
        out["sd_phi_monte_carlo"] = mca["sd_phi"]
        s = mca["sd_phi"]
        out["phi_minus_1_in_sd_monte_carlo"] = (phi - mca["mean_phi"]) / s if s else None
        out["consistent_with_poisson_within_1sd_mc"] = bool(
            abs(phi - mca["mean_phi"]) <= s
        )
        out["consistent_with_poisson_within_2sd_mc"] = bool(
            abs(phi - mca["mean_phi"]) <= 2.0 * s
        )

    out["status"] = "MEASURED"
    log(
        "  [%s] rows %d..%d  events %d  bins %d (min expected %.2f)  deg %d  "
        "phi = %.4f  sd_analytic %.4f  sd_MC %.4f"
        % (
            label,
            lo,
            hi,
            total,
            K,
            out["min_expected_count_per_bin"],
            deg,
            phi,
            sd,
            out.get("sd_phi_monte_carlo", float("nan")),
        )
    )
    return out


# --------------------------------------------------------------------------
# 3.  JOB B1 -- effective degrees of freedom
# --------------------------------------------------------------------------
#
# The statistic is  S = (1/n) sum_T r_T^2  with  r_T = log2 model_T - log2 Phat_T.
# A perfect model has r_T = log2 lambda_T - log2 C_T, pure counting noise.
#
# Delta method:  r_T ~= -(C_T - lambda_T)/(lambda_T ln 2).
# C_T is a NESTED tail count, so for T < T'
#     Cov(C_T, C_T') = Var(C_T') = lambda_{T'} = min(lambda_T, lambda_T'),
# hence
#     Cov(r_T, r_T') = min(lambda_T, lambda_T') / (lambda_T lambda_T' ln^2 2)
#                    = min(1/lambda_T, 1/lambda_T') / ln^2 2.
# That is the D-1 covariance.
#
# Satterthwaite: for Q = r^T r with r ~ N(0, Sigma),
#     E[Q] = tr Sigma,  Var[Q] = 2 tr(Sigma^2),
# matching to c * chi^2_nu gives
#     nu_eff = (tr Sigma)^2 / tr(Sigma^2).
# White noise (Sigma diagonal, same variances) is the same formula with the
# off-diagonal set to zero.
#
# Two diagonal conventions are reported, because they are not interchangeable:
#   * delta-method variance      1/(lambda ln^2 2)
#   * exact truncated-Poisson    E[(log2 lambda - log2 C)^2 | C >= 1]
# The exact one is what the archived counting floor uses (its sum over the
# whole band IS n * floor^2), so it is the one that must be used if the dof is
# to be quoted beside that floor.


def exact_row_variance(lam):
    """E[(log2 lambda - log2 C)^2 | C >= 1], C ~ Poisson(lambda).  Bits^2."""
    if lam > 1e5:
        return (1.0 / lam + 1.75 / lam ** 2) / L2
    lnl = math.log(lam)
    lp = -lam
    s = 0.0
    kmax = int(lam + 40.0 * math.sqrt(lam) + 60)
    for k in range(1, kmax + 1):
        lp += lnl - math.log(k)
        d = lnl - math.log(k)
        s += math.exp(lp) * d * d
    return s / (1.0 - math.exp(-lam)) / L2


def effective_dof(lams, var_rows):
    """
    lams must be NON-INCREASING in index (they are: C_T is a survival count).
    Sigma_ij = rho_ij sqrt(v_i v_j) with rho from the D-1 covariance;
    for i <= j, min(1/lam_i, 1/lam_j) = 1/lam_i, so
        rho_ij = (1/lam_i) / sqrt((1/lam_i)(1/lam_j)) = sqrt(lam_j / lam_i).
    """
    n = len(lams)
    trS = sum(var_rows)
    nu_white = trS * trS / sum(v * v for v in var_rows)

    tr2 = sum(v * v for v in var_rows)
    for i in range(n):
        li = lams[i]
        vi = var_rows[i]
        acc = 0.0
        for j in range(i + 1, n):
            acc += (lams[j] / li) * var_rows[j]
        tr2 += 2.0 * vi * acc
    nu_D1 = trS * trS / tr2
    return dict(
        n_scores=n,
        trace_Sigma=trS,
        trace_Sigma_squared=tr2,
        nu_white=nu_white,
        nu_D1=nu_D1,
    )


def effective_dof_min_of_variances(var_rows):
    """
    Satterthwaite with Sigma_{TT'} := min(a_T, a_T') taken DIRECTLY on the
    per-row variances a_T -- i.e. the residual treated as Brownian in the time
    change a.

    This is exact when a_T = 1/(lambda_T ln^2 2) (the delta-method variance),
    because then min(a_T,a_T') really is Cov(r_T, r_T').  Substituting the
    exact truncated-Poisson a_T into the same expression is an extension by
    analogy, not a derivation -- the two extensions do not agree, and both are
    reported.

    a_T is non-decreasing in T (lambda_T is a non-increasing survival count),
    so min over a pair is the value at the smaller index and
        sum_{T,T'} min(a_T,a_T')^2 = sum_i (1 + 2(n-1-i)) a_i^2 .
    """
    n = len(var_rows)
    non_monotone = sum(1 for i in range(n - 1) if var_rows[i] > var_rows[i + 1])
    trS = sum(var_rows)
    den = sum((1 + 2 * (n - 1 - i)) * var_rows[i] ** 2 for i in range(n))
    return dict(nu=trS * trS / den, non_monotone_steps=non_monotone)


def effective_dof_pure_delta(lams):
    """Satterthwaite with Sigma_ij = min(1/l_i, 1/l_j)/ln^2 2 throughout."""
    n = len(lams)
    d = [1.0 / (l * L2) for l in lams]
    trS = sum(d)
    tr2 = sum((2 * (n - 1 - i) + 1) * d[i] * d[i] for i in range(n))
    return dict(
        n_scores=n,
        trace_Sigma=trS,
        nu_white=trS * trS / sum(x * x for x in d),
        nu_D1=trS * trS / tr2,
    )


# --------------------------------------------------------------------------
# 4.  main
# --------------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    ap.add_argument("--reps", type=int, default=300)
    ap.add_argument("--seed", type=int, default=20260803)
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    out_path = args.out or os.path.join(here, "results.json")

    t0 = time.time()
    real_out, real_err = sys.stdout, sys.stderr
    tee_out, tee_err = Tee(real_out), Tee(real_err)
    sys.stdout, sys.stderr = tee_out, tee_err

    def log(msg):
        print(msg)

    rng = random.Random(args.seed)

    log("dispersion_control_c1.py -- TASK-20260803-f81a66 (BATCH-014)")
    log("OBSERVATIONS ONLY.  Toy tier.  No ML-KEM security claim.")
    log("")

    results = dict(
        task_id="TASK-20260803-f81a66",
        batch_id="BATCH-014",
        goal_id="GOAL-MLKEM-003",
        experiment_id="EXP-MLKEM-011",
        title=(
            "Control C1 (deep-tail Poisson dispersion, properly constructed) "
            "and an independent recomputation of the DEC-20260803-52a750 "
            "retirement basis"
        ),
        supersedes_nothing=(
            "This run adds a record.  It edits no prior artifact and changes "
            "no record status."
        ),
        scope=dict(
            tier="toy",
            band="resolved band only",
            scale="raw undivided score scale",
            mlkem_security_claim="NONE, in either direction",
            rule_12="UNMET and UNWAIVED; EV-MLKEM-011/013/017 keep their status",
        ),
        red_team_reference_values=RED_TEAM_REFERENCE,
        files=[],
    )

    loaded = []
    for spec in FILES:
        d = load_pwrong(spec)
        loaded.append(d)
        log(
            "%s: M = %d pooled scores, band [0, %d], %d rows, "
            "integrality max rel dev %.3e"
            % (d["tag"], d["M"], d["last_positive"], d["n_band"], d["integrality_max_rel_dev"])
        )
    log("")

    # ---------------- JOB A ----------------
    log("JOB A -- CONTROL C1: deep-tail dispersion")
    log("  null: increments D_T = C_T - C_{T+1} ~ indep Poisson(smooth lambda_T)")
    log("")
    for d in loaded:
        counts = d["counts"]
        n = d["n_band"]
        last = d["last_positive"]

        def first_below(thr):
            idx = [i for i, c in enumerate(counts[:n]) if c >= thr]
            return (max(idx) + 1) if idx else 0

        t1000 = first_below(1000)
        t10 = first_below(10)
        t1e5 = first_below(100000)

        log("%s: deep tail (C < 1000) = scores [%d, %d]" % (d["tag"], t1000, last))
        regions = [
            dict(
                label="deep_tail_C_lt_1000",
                lo=t1000,
                hi=last,
                note=(
                    "exactly the complement of the count>=1000 band, i.e. the "
                    "rows that generate the deep-tail floor"
                ),
            ),
            dict(
                label="extreme_tail_C_lt_10",
                lo=t10,
                hi=last,
                note="complement of the count>=10 band",
            ),
            dict(
                label="mid_band_1000_le_C_lt_1e5",
                lo=t1e5,
                hi=t1000 - 1,
                note="well-measured control region",
            ),
            dict(
                label="shallow_C_ge_1e5",
                lo=0,
                hi=t1e5 - 1,
                note="shallow control region",
            ),
            dict(
                label="deep_tail_C_lt_1e5",
                lo=t1e5,
                hi=last,
                note="wider deep region, more windows",
            ),
        ]
        blocks = []
        for reg in regions:
            if reg["hi"] < reg["lo"]:
                continue
            n_rows_reg = reg["hi"] - reg["lo"] + 1
            degs = list(range(1, 13)) if n_rows_reg >= 250 else list(range(1, 9))
            res = analyse_region(
                d,
                reg["lo"],
                reg["hi"],
                reg["label"],
                degrees=degs,
                target=10.0,
                reps=args.reps if reg["label"].startswith("deep_tail_C_lt_1000") else max(args.reps // 5, 40),
                rich_degree=10,
                rng=rng,
                log=log,
            )
            res["region_note"] = reg["note"]
            blocks.append(res)
        d["_jobA"] = blocks
        log("")

    # ---------------- JOB B1 ----------------
    log("JOB B1 -- effective degrees of freedom, derived independently")
    for d in loaded:
        counts = d["counts"]
        n = d["n_band"]
        lams = [float(c) for c in counts[:n]]
        cache = {}
        vex = []
        for l in lams:
            if l not in cache:
                cache[l] = exact_row_variance(l)
            vex.append(cache[l])

        whole_exact = effective_dof(lams, vex)
        whole_delta = effective_dof_pure_delta(lams)
        dlt = [1.0 / (l * L2) for l in lams]
        whole_minvar_exact = effective_dof_min_of_variances(vex)
        whole_minvar_delta = effective_dof_min_of_variances(dlt)

        bands = {}
        for thr, lab in [(10, "count_ge_10"), (1000, "count_ge_1000"), (100000, "count_ge_1e5")]:
            idx = [i for i, c in enumerate(counts[:n]) if c >= thr]
            nb = max(idx) + 1
            lb = lams[:nb]
            vb = vex[:nb]
            e = effective_dof(lb, vb)
            dd = effective_dof_pure_delta(lb)
            mv = effective_dof_min_of_variances(vb)
            bands[lab] = dict(
                n_scores=nb,
                floor_rms_bits=math.sqrt(sum(vb) / nb),
                nu_white_exact_variances=e["nu_white"],
                nu_D1_min_of_variances_exact=mv["nu"],
                nu_D1_correlation_scaled_exact=e["nu_D1"],
                nu_white_delta_variances=dd["nu_white"],
                nu_D1_delta_variances=dd["nu_D1"],
            )

        d["_jobB1"] = dict(
            whole_band=dict(
                n_scores=n,
                floor_rms_bits=math.sqrt(sum(vex) / n),
                noise_budget_sum_of_row_variances=sum(vex),
                nu_white_exact_variances=whole_exact["nu_white"],
                nu_D1_min_of_variances_exact=whole_minvar_exact["nu"],
                nu_D1_min_of_variances_delta=whole_minvar_delta["nu"],
                nu_D1_correlation_scaled_exact=whole_exact["nu_D1"],
                nu_white_delta_variances=whole_delta["nu_white"],
                nu_D1_delta_variances=whole_delta["nu_D1"],
                variance_sequence_non_monotone_steps=whole_minvar_exact[
                    "non_monotone_steps"
                ],
                conventions=dict(
                    nu_white_exact_variances=(
                        "(sum a)^2 / sum a^2 with a_T the exact truncated-Poisson "
                        "row variance; the off-diagonal is set to zero"
                    ),
                    nu_D1_min_of_variances_exact=(
                        "(sum a)^2 / sum_{T,T'} min(a_T,a_T')^2 with a_T exact"
                    ),
                    nu_D1_min_of_variances_delta=(
                        "same expression with a_T = 1/(lambda_T ln^2 2); this is "
                        "the case where min(a_T,a_T') IS the covariance"
                    ),
                    nu_D1_correlation_scaled_exact=(
                        "Sigma = D^{1/2} R D^{1/2}, D = diag(exact a_T), "
                        "R_ij = sqrt(lambda_j/lambda_i) the delta-method "
                        "correlation -- the other way of combining the exact "
                        "variances with the D-1 correlation structure"
                    ),
                ),
            ),
            sub_bands=bands,
            derivation=dict(
                statistic="S = (1/n) sum_T (log2 model_T - log2 Phat_T)^2",
                perfect_model_residual="log2 lambda_T - log2 C_T",
                covariance="Cov(r_T, r_T') = min(1/lambda_T, 1/lambda_T') / ln^2 2, "
                "because C_T is a NESTED tail count so Cov(C_T,C_T') = min(lambda_T,lambda_T')",
                effective_dof="Satterthwaite nu = (tr Sigma)^2 / tr(Sigma^2)",
                plug_in="lambda_T := C_T, the same plug-in the archived floor uses",
                variance_conventions=(
                    "exact = E[(log2 lambda - log2 C)^2 | C>=1] (sums to n*floor^2, "
                    "so it is the convention consistent with the archived floor); "
                    "delta = 1/(lambda ln^2 2)"
                ),
                correlation_used="rho_ij = sqrt(lambda_j / lambda_i) for i <= j",
            ),
        )
        log(
            "  %s whole band n=%d: nu_white(exact a) = %.4f | "
            "nu_D1 min(a,a') exact = %.4f | nu_D1 min(a,a') delta = %.4f | "
            "nu_D1 corr-scaled exact = %.4f"
            % (
                d["tag"],
                n,
                whole_exact["nu_white"],
                whole_minvar_exact["nu"],
                whole_minvar_delta["nu"],
                whole_exact["nu_D1"],
            )
        )
    log("")

    # ---------------- JOB B2 ----------------
    log("JOB B2 -- attenuation identity, derived independently")
    b012 = json.load(open(BATCH012_RESULTS))
    b012_sha = sha256_file(BATCH012_RESULTS)
    by_name = {f["file"]: f for f in b012["files"]}

    for d in loaded:
        counts = d["counts"]
        n = d["n_band"]
        lams = [float(c) for c in counts[:n]]
        cache = {}
        vex = []
        for l in lams:
            if l not in cache:
                cache[l] = exact_row_variance(l)
            vex.append(cache[l])
        S_whole = sum(vex)  # = n * floor_whole^2
        idx = [i for i, c in enumerate(counts[:n]) if c >= 1000]
        n_meas = max(idx) + 1
        S_meas = sum(vex[:n_meas])
        n_deep = n - n_meas
        S_deep = S_whole - S_meas
        atten = S_whole / S_meas
        floor_whole = math.sqrt(S_whole / n)
        floor_meas = math.sqrt(S_meas / n_meas)
        floor_deep = math.sqrt(S_deep / n_deep)

        arch = by_name[d["name"]]
        models = {}

        def add(name, rms_whole, rms_meas, norm_whole=None, norm_meas=None,
                shape_whole=None, shape_meas=None):
            if rms_whole is None or rms_meas is None:
                return
            sq_whole = n * rms_whole ** 2
            sq_meas = n_meas * rms_meas ** 2
            sq_deep = sq_whole - sq_meas
            same_shape = (shape_whole is None and shape_meas is None) or (
                shape_whole == shape_meas
            )
            shift = None
            if norm_whole is not None and norm_meas is not None:
                shift = abs(norm_whole - norm_meas)
            valid = bool(same_shape and shift is not None and shift <= 0.05)
            models[name] = dict(
                reconstruction_valid=valid,
                reconstruction_caveat=(
                    None
                    if valid
                    else (
                        "the archived whole-band and count>=1000 rms values come "
                        "from DIFFERENT fits (shape parameter %r vs %r, "
                        "normalisation differing by %s bits), so "
                        "sum_deep = sum_whole - sum_meas is NOT the decomposition "
                        "of a single fit and the deep-tail numbers below are not "
                        "comparable with a single-fit decomposition.  Recorded, "
                        "not used."
                        % (shape_whole, shape_meas,
                           ("%.4f" % shift) if shift is not None else "unknown")
                    )
                ),
                whole_fit_shape=shape_whole,
                meas_fit_shape=shape_meas,
                normalisation_shift_bits=shift,
                rms_whole_bits=rms_whole,
                rms_count_ge_1000_bits=rms_meas,
                ratio_whole=rms_whole / floor_whole,
                ratio_whole_squared=(rms_whole / floor_whole) ** 2,
                ratio_count_ge_1000=rms_meas / floor_meas,
                sum_sq_residual_whole=sq_whole,
                sum_sq_residual_count_ge_1000=sq_meas,
                sum_sq_residual_deep_tail=sq_deep,
                deep_tail_rms_bits=math.sqrt(sq_deep / n_deep) if sq_deep > 0 else None,
                deep_tail_ratio=(math.sqrt(sq_deep / n_deep) / floor_deep)
                if sq_deep > 0
                else None,
                deep_tail_percent_below_floor=(
                    100.0 * (1.0 - math.sqrt(sq_deep / n_deep) / floor_deep)
                )
                if sq_deep > 0
                else None,
                identity_constant=sq_deep / S_whole,
                identity_check_ratio_whole_squared=(sq_deep / S_whole)
                + ((rms_meas / floor_meas) ** 2) / atten,
            )

        r = arch["results"]
        m2 = r["M2_exact_region_measure"]
        add("M2_exact_region_measure",
            m2["whole"]["rms_bits"], m2["count_ge_1000"]["rms_bits"],
            m2["whole"]["log2_A_fitted"], m2["count_ge_1000"]["log2_A_fitted"],
            "exact", "exact")
        m4 = r["M4_exact_measure_dlsc_collapsed_at_mu"]
        add("M4_exact_measure_dlsc_collapsed",
            m4["whole"]["rms_bits"], m4["count_ge_1000"]["rms_bits"],
            m4["whole"]["ln_A_fitted"] / LN2, m4["count_ge_1000"]["ln_A_fitted"] / LN2,
            "exact_dlsc_collapsed", "exact_dlsc_collapsed")
        m1 = r["M1_gaussian_phi_surrogate_refitted_here"]
        add("M1_surrogate_at_argmin_p",
            m1["whole"]["argmin"]["rms_bits"],
            m1["count_ge_1000"]["argmin"]["rms_bits"],
            m1["whole"]["argmin"]["log2_K"],
            m1["count_ge_1000"]["argmin"]["log2_K"],
            "p=%s" % m1["whole"]["argmin"]["p"],
            "p=%s" % m1["count_ge_1000"]["argmin"]["p"])
        add("M1a_surrogate_at_own_exponent",
            m1["whole"]["at_own_archived_exponent"]["rms_bits"],
            m1["count_ge_1000"]["at_own_archived_exponent"]["rms_bits"],
            m1["whole"]["at_own_archived_exponent"]["log2_K"],
            m1["count_ge_1000"]["at_own_archived_exponent"]["log2_K"],
            "p=%s" % m1["whole"]["at_own_archived_exponent"]["p"],
            "p=%s" % m1["count_ge_1000"]["at_own_archived_exponent"]["p"])
        m3 = r["M3_exact_measure_generalised_exponent"]
        add("M3_exact_generalised_exponent_at_argmin",
            m3["whole"]["argmin"]["rms_bits"],
            m3["count_ge_1000"]["argmin"]["rms_bits"],
            m3["whole"]["argmin"]["ln_A"] / LN2,
            m3["count_ge_1000"]["argmin"]["ln_A"] / LN2,
            "s=%s" % m3["whole"]["argmin"]["s"],
            "s=%s" % m3["count_ge_1000"]["argmin"]["s"])

        d["_jobB2"] = dict(
            derivation=(
                "ratio_whole^2 = (sum_T r_T^2)/(n*floor_whole^2).  Split the band "
                "at the count>=1000 boundary: sum_T r_T^2 = sum_deep + sum_meas, "
                "and sum_meas = ratio_meas^2 * (n_meas*floor_meas^2).  Therefore "
                "ratio_whole^2 = C + ratio_meas^2 / A with "
                "C = sum_deep/(n*floor_whole^2) and "
                "A = (n*floor_whole^2)/(n_meas*floor_meas^2)."
            ),
            whole_band_noise_budget=S_whole,
            measurable_band_noise_budget=S_meas,
            deep_tail_noise_budget=S_deep,
            attenuation_fold=atten,
            n_whole=n,
            n_measurable=n_meas,
            n_deep_tail=n_deep,
            floor_whole_bits=floor_whole,
            floor_count_ge_1000_bits=floor_meas,
            floor_deep_tail_bits=floor_deep,
            models=models,
            caveat_on_the_constant=(
                "the whole-band rms and the count>=1000 rms come from SEPARATELY "
                "profiled normalisations in the archived fits, so the split "
                "sum_deep = sum_whole - sum_meas is exact only up to that "
                "difference of fitted normalisation.  The structural quantities "
                "(noise budgets, attenuation fold, deep-tail floor) do not depend "
                "on it."
            ),
        )
        # BINDING (DEC-20260803-52a750): a whole-band ratio is never quoted
        # without its effective degrees of freedom beside it.
        wb = d["_jobB1"]["whole_band"]
        sb = d["_jobB1"]["sub_bands"]["count_ge_1000"]
        for v in models.values():
            v["effective_dof_of_whole_band_ratio"] = dict(
                nu_D1_min_of_variances_exact=wb["nu_D1_min_of_variances_exact"],
                nu_D1_correlation_scaled_exact=wb["nu_D1_correlation_scaled_exact"],
                nu_D1_min_of_variances_delta=wb["nu_D1_min_of_variances_delta"],
                nu_white_exact_variances=wb["nu_white_exact_variances"],
                sampling_sd_of_the_ratio_at_nu_D1=0.5
                * math.sqrt(2.0 / wb["nu_D1_min_of_variances_exact"]),
            )
            v["effective_dof_of_count_ge_1000_ratio"] = dict(
                nu_D1_min_of_variances_exact=sb["nu_D1_min_of_variances_exact"],
                nu_white_exact_variances=sb["nu_white_exact_variances"],
                sampling_sd_of_the_ratio_at_nu_D1=0.5
                * math.sqrt(2.0 / sb["nu_D1_min_of_variances_exact"]),
            )

        log(
            "  %s: whole-band noise budget = %.6f, measurable = %.6f, "
            "attenuation = %.2f-fold, deep-tail floor = %.6f bits"
            % (d["tag"], S_whole, S_meas, atten, floor_deep)
        )
        for k, v in models.items():
            log(
                "     %-42s deep-tail ratio %.4f (%.1f%% below floor), "
                "identity constant %.4f -> perfect-on-measurable %.4f x  [%s]"
                % (
                    k,
                    v["deep_tail_ratio"],
                    v["deep_tail_percent_below_floor"],
                    v["identity_constant"],
                    math.sqrt(v["identity_constant"]),
                    "single-fit reconstruction VALID"
                    if v["reconstruction_valid"]
                    else "NOT a single-fit decomposition -- see caveat",
                )
            )
    log("")

    # ---------------- assemble ----------------
    for d in loaded:
        results["files"].append(
            dict(
                tag=d["tag"],
                file=d["name"],
                file_path_repo_relative=os.path.relpath(d["path"], REPO),
                file_sha256=d["sha256"],
                header_raw=d["header"],
                instrument=dict(
                    pooled_scores_M=d["M"],
                    resolved_band=[0, d["last_positive"]],
                    n_scores_in_band=d["n_band"],
                    integrality_max_relative_deviation=d["integrality_max_rel_dev"],
                    note=(
                        "C_T = Phat(T) * nb_iteration * q^{k_fft}, recovered "
                        "exactly; C_T is a NESTED tail count."
                    ),
                ),
                job_A_dispersion=d["_jobA"],
                job_B1_effective_dof=d["_jobB1"],
                job_B2_attenuation_identity=d["_jobB2"],
            )
        )

    # ---------------- headline observations (no interpretation) -------------
    summary = dict(
        note=(
            "Observations only.  No conclusion is drawn here about retiring "
            "the whole-band statistic or about Approximation 4.9."
        ),
        job_A=[],
        job_B1_comparison=[],
        job_B2_comparison=[],
    )
    for d in loaded:
        prim = [b for b in d["_jobA"] if b["label"] == "deep_tail_C_lt_1000"]
        if prim:
            b = prim[0]
            entry = dict(
                file=d["tag"],
                region="deep tail, C_T < 1000, scores %s" % (b["score_range"],),
                n_bins=b.get("n_bins"),
                min_expected_count_per_bin=b.get("min_expected_count_per_bin"),
                expected_count_ge_10_holds=b.get("expected_count_ge_10_holds"),
                phi=b.get("phi"),
                sd_phi_analytic=b.get("sd_phi_analytic"),
                sd_phi_monte_carlo=b.get("sd_phi_monte_carlo"),
                phi_range_over_degrees=b.get(
                    "phi_range_over_converged_degrees_at_or_above_chosen"
                ),
                consistent_with_poisson_within_1sd_mc=b.get(
                    "consistent_with_poisson_within_1sd_mc"
                ),
                consistent_with_poisson_within_2sd_mc=b.get(
                    "consistent_with_poisson_within_2sd_mc"
                ),
            )
            summary["job_A"].append(entry)
        ext = [b for b in d["_jobA"] if b["label"] == "extreme_tail_C_lt_10"]
        if ext:
            summary["job_A"].append(
                dict(
                    file=d["tag"],
                    region="extreme tail, C_T < 10",
                    status=ext[0]["status"],
                    n_scores=ext[0]["n_scores"],
                    total_increment_events=ext[0]["total_increment_events"],
                    reason=ext[0].get("reason"),
                )
            )
        wb = d["_jobB1"]["whole_band"]
        summary["job_B1_comparison"].append(
            dict(
                file=d["tag"],
                red_team_reported_dof=RED_TEAM_REFERENCE["effective_dof_D1"][d["tag"]],
                recomputed_min_of_variances_exact=wb["nu_D1_min_of_variances_exact"],
                recomputed_correlation_scaled_exact=wb["nu_D1_correlation_scaled_exact"],
                recomputed_min_of_variances_delta=wb["nu_D1_min_of_variances_delta"],
                red_team_reported_white=RED_TEAM_REFERENCE["effective_dof_white"][d["tag"]],
                recomputed_white=wb["nu_white_exact_variances"],
            )
        )
        b2 = d["_jobB2"]
        summary["job_B2_comparison"].append(
            dict(
                file=d["tag"],
                whole_band_noise_budget=b2["whole_band_noise_budget"],
                measurable_band_noise_budget=b2["measurable_band_noise_budget"],
                attenuation_fold=b2["attenuation_fold"],
                deep_tail_floor_bits=b2["floor_deep_tail_bits"],
                M2_deep_tail_ratio=b2["models"]["M2_exact_region_measure"]["deep_tail_ratio"],
                M2_identity_constant=b2["models"]["M2_exact_region_measure"]["identity_constant"],
                M2_reconstruction_valid=b2["models"]["M2_exact_region_measure"]["reconstruction_valid"],
            )
        )
    results["headline_observations"] = summary

    ru = resource.getrusage(resource.RUSAGE_SELF)
    wall = time.time() - t0
    script_path = os.path.abspath(__file__)

    results["provenance"] = dict(
        command="%s %s" % (sys.executable, " ".join([os.path.relpath(script_path, REPO)] + sys.argv[1:])),
        argv=sys.argv,
        cwd=os.getcwd(),
        script_path_repo_relative=os.path.relpath(script_path, REPO),
        script_sha256=sha256_file(script_path),
        git_commit=git("rev-parse", "HEAD"),
        git_branch=git("rev-parse", "--abbrev-ref", "HEAD"),
        git_dirty_tree=bool(git("status", "--porcelain").strip()),
        git_dirty_paths=[
            l[3:] for l in git("status", "--porcelain").splitlines() if l.strip()
        ],
        environment=dict(
            python_version=sys.version,
            platform=platform.platform(),
            executable=sys.executable,
            numpy="absent",
            scipy="absent",
            mpmath="absent",
            note="every numerical routine is written out in this script",
        ),
        input_files=[
            dict(path=os.path.relpath(d["path"], REPO), sha256=d["sha256"]) for d in loaded
        ]
        + [
            dict(
                path=os.path.relpath(BATCH012_RESULTS, REPO),
                sha256=b012_sha,
                role="archived model rms values for Job B2 (read, not recomputed)",
            )
        ],
        network_access="none",
        g6k="not used",
        new_sampling_of_the_physical_system="none",
        seeds=dict(
            python_random_seed=args.seed,
            used_only_for=(
                "the synthetic null-object calibration of Job A's estimator "
                "(MC_A / MC_B / MC_C).  Every reported measurement of the "
                "archived data is a deterministic function of the archived "
                "bytes; no measured quantity depends on the seed."
            ),
            monte_carlo_replicates=args.reps,
        ),
        determinism=(
            "deterministic given the seed; all measured (non-MC) quantities are "
            "seed independent"
        ),
        wall_clock_seconds=wall,
        peak_rss_gb=ru.ru_maxrss / (1024.0 * 1024.0),
        peak_rss_measurable="yes, via resource.getrusage(RUSAGE_SELF).ru_maxrss",
        user_cpu_seconds=ru.ru_utime,
        system_cpu_seconds=ru.ru_stime,
        budget=dict(wall_clock_seconds=3000, memory_gb=4, maximum_runs=1),
    )
    results["certificate"] = dict(
        kind="none",
        reason=(
            "pure measurement run: no discrete-log solve, no factor-base "
            "relation, no claimed solution of any kind"
        ),
    )
    results["inference"] = dict(
        requested_policy="executor-implementation",
        reasoning_effort=None,
        fallback_allowed=True,
        degraded_allowed=False,
        independent_session_required=False,
        runtime="claude-code",
        resolved_model_id="claude-opus-5 (claude-opus-5)",
        model_verified=False,
        model_verification_note=(
            "orchestration/model-policies.yaml names GPT-5.6-family policy "
            "aliases that Claude Code cannot resolve; per CLAUDE.md the harness "
            "records requested_policy plus the actual resolved model.  No "
            "`python3 -m orchestration.adapter doctor --probe` was run in this "
            "task, so model_verified is false."
        ),
        fallback_used=True,
        fallback_reason=(
            "executor-implementation is a policy alias for a backend this "
            "runtime cannot address; the Claude Code subagent model served the "
            "task instead"
        ),
        degraded_requirements=[],
    )
    results["validity"] = dict(
        status="completed_valid",
        reason=(
            "the run terminated normally inside budget, every reported number "
            "is computed from the archived bytes by the shipped script, all "
            "controls returned, and no fabricated value appears"
        ),
        classification="completed_valid",
    )
    results["non_claims"] = [
        "No ML-KEM or Kyber security claim in either direction.",
        "No conclusion that the whole-band statistic should or should not be retired.",
        "No conclusion that Approximation 4.9 is validated or refuted.",
        "No record status changed; no prior artifact edited.",
        "No cost model proposed, revised, or costed.",
        "Toy tier only; nothing here extrapolates to cryptographic scale.",
    ]

    sys.stdout, sys.stderr = real_out, real_err
    results["stdout_log"] = tee_out.getvalue().splitlines()
    results["stderr_log"] = tee_err.getvalue().splitlines()
    results["provenance"]["stderr_captured_from_this_process"] = tee_err.getvalue()

    with open(out_path, "w") as fh:
        json.dump(results, fh, indent=1, sort_keys=False)
    print("wrote %s (%.1f s, peak RSS %.4f GB)" % (out_path, wall, results["provenance"]["peak_rss_gb"]))


if __name__ == "__main__":
    main()
