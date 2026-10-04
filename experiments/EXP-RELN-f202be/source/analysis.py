"""Stage-4 analysis for EXP-RELN-f202be: Delta, bootstrap CIs, z-scores
against the analytic (INV-3) and Monte Carlo (NULL-A) nulls, k-rich counts,
predicate lifts, Holm correction, growth-fit slope, and control verdicts.

Pure statistics/arithmetic over already-computed cell summaries (E_3, M, N,
histograms) produced by direct_enumerator.py / zn_integer_arms.py / e_arms.py
and cross-checked by spectral_crosscheck.py. This module does not itself
enumerate any base.
"""
from __future__ import annotations

import math
import statistics
from typing import Sequence

import numpy as np


def delta_of(E3: float, M: float, N: float) -> float:
    mu = M / N
    return E3 / M - mu


def bootstrap_ci(values: Sequence[float], n_boot: int = 2000, seed: int = 0,
                  alpha: float = 0.05) -> dict:
    if len(values) == 0:
        return {"mean": None, "lo": None, "hi": None, "n": 0}
    rng = np.random.Generator(np.random.PCG64(seed))
    arr = np.asarray(values, dtype=np.float64)
    n = len(arr)
    boots = np.empty(n_boot)
    for b in range(n_boot):
        idx = rng.integers(0, n, size=n)
        boots[b] = arr[idx].mean()
    lo = float(np.percentile(boots, 100 * alpha / 2))
    hi = float(np.percentile(boots, 100 * (1 - alpha / 2)))
    return {"mean": float(arr.mean()), "lo": lo, "hi": hi, "n": int(n)}


def null_band(null_deltas: Sequence[float], width_sd: float = 3.0) -> dict:
    arr = np.asarray(null_deltas, dtype=np.float64)
    mean = float(arr.mean())
    sd = float(arr.std(ddof=1)) if len(arr) > 1 else 0.0
    return {"mean": mean, "sd": sd, "lo": mean - width_sd * sd, "hi": mean + width_sd * sd,
            "n": len(arr), "width_sd": width_sd}


def in_band(value: float, band: dict) -> bool:
    return band["lo"] <= value <= band["hi"]


def z_delta(delta: float, band: dict) -> float | None:
    if band["sd"] == 0:
        return None
    return (delta - band["mean"]) / band["sd"]


def analytic_null_sd(sigma: float, M: float) -> float:
    return math.sqrt((1 - sigma) / (sigma * M))


def z_analytic(rho: float, sigma: float, M: float) -> float:
    return (rho - 1.0) * math.sqrt(sigma * M / (1 - sigma))


def rho_lambda(T_S: int, sigma: float, M: float, coverage_ge1_in_S: float | None = None,
                coverage_ge1_all: float | None = None) -> dict:
    rho = T_S / (sigma * M) if sigma * M != 0 else None
    out = {"rho": rho}
    if coverage_ge1_in_S is not None and coverage_ge1_all is not None and coverage_ge1_all != 0:
        out["lambda"] = coverage_ge1_in_S / coverage_ge1_all
    return out


def holm_correction(pvalues: Sequence[float], alpha: float = 0.05) -> dict:
    """Holm-Bonferroni step-down. Returns per-index reject flags (input
    order preserved) and adjusted (Holm-corrected) p-values."""
    n = len(pvalues)
    order = sorted(range(n), key=lambda i: pvalues[i])
    adjusted = [0.0] * n
    reject = [False] * n
    running_max = 0.0
    for rank, i in enumerate(order):
        m_minus_rank = n - rank
        adj = pvalues[i] * m_minus_rank
        running_max = max(running_max, adj)
        adjusted[i] = min(1.0, running_max)
    # Holm rejection: sequential, stop at first non-rejection
    still_rejecting = True
    for rank, i in enumerate(order):
        m_minus_rank = n - rank
        crit = alpha / m_minus_rank
        if still_rejecting and pvalues[i] <= crit:
            reject[i] = True
        else:
            still_rejecting = False
            reject[i] = False
    return {"adjusted_pvalues": adjusted, "reject": reject, "alpha": alpha}


def two_sided_pvalue_from_z(z: float) -> float:
    from math import erf, sqrt
    return 2.0 * (1.0 - 0.5 * (1 + erf(abs(z) / sqrt(2))))


def k_rich_from_array(count_vector: np.ndarray, ks: Sequence[int]) -> dict:
    out = {}
    for k in ks:
        out[str(k)] = int(np.count_nonzero(count_vector >= k))
    return out


def chebyshev_bound(N: int, mu: float, delta: float, k: int) -> float | None:
    if k <= mu:
        return None
    return N * mu * delta / ((k - mu) ** 2)


def poisson_tail_prob(mu: float, k: int) -> float:
    s = 0.0
    term = math.exp(-mu)
    s += term
    for i in range(1, k):
        term *= mu / i
        s += term
    return max(0.0, 1.0 - s)


def growth_fit(log_N: Sequence[float], log_excess: Sequence[float], n_boot: int = 2000,
               seed: int = 0) -> dict:
    """OLS slope of log_excess vs log_N, with a naive bootstrap CI over the
    (already rung-level-averaged) points. With only 1-2 rungs this is
    reported as insufficient_rungs rather than a fabricated interval."""
    n = len(log_N)
    if n < 3:
        return {"slope": None, "lo": None, "hi": None, "insufficient_rungs": True, "n_rungs": n}
    x = np.asarray(log_N, dtype=np.float64)
    y = np.asarray(log_excess, dtype=np.float64)
    slope, intercept = np.polyfit(x, y, 1)
    rng = np.random.Generator(np.random.PCG64(seed))
    slopes = np.empty(n_boot)
    idxs = np.arange(n)
    for b in range(n_boot):
        take = rng.integers(0, n, size=n)
        try:
            s, _ = np.polyfit(x[take], y[take], 1)
        except Exception:
            s = np.nan
        slopes[b] = s
    slopes = slopes[~np.isnan(slopes)]
    lo = float(np.percentile(slopes, 2.5)) if len(slopes) else None
    hi = float(np.percentile(slopes, 97.5)) if len(slopes) else None
    return {"slope": float(slope), "lo": lo, "hi": hi, "insufficient_rungs": False, "n_rungs": n,
            "contains_zero": (lo is not None and hi is not None and lo <= 0.0 <= hi)}


def ks_statistic(sample_a: Sequence[float], sample_b: Sequence[float]) -> dict:
    """Two-sample KS statistic (no scipy dependency; simple ECDF comparison).
    Returns D and an approximate p-value via the asymptotic Kolmogorov
    distribution."""
    a = np.sort(np.asarray(sample_a, dtype=np.float64))
    b = np.sort(np.asarray(sample_b, dtype=np.float64))
    all_vals = np.concatenate([a, b])
    all_vals.sort()
    cdf_a = np.searchsorted(a, all_vals, side="right") / len(a)
    cdf_b = np.searchsorted(b, all_vals, side="right") / len(b)
    D = float(np.max(np.abs(cdf_a - cdf_b)))
    n_eff = len(a) * len(b) / (len(a) + len(b))
    lam = (math.sqrt(n_eff) + 0.12 + 0.11 / math.sqrt(n_eff)) * D
    # Kolmogorov asymptotic p-value
    p = 0.0
    for k in range(1, 101):
        p += 2 * (-1) ** (k - 1) * math.exp(-2 * k * k * lam * lam)
    p = max(0.0, min(1.0, p))
    return {"D": D, "p_value_asymptotic": p}
