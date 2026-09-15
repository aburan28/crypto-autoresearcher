#!/usr/bin/env python3
"""Statistics for EXP-SEMBIN-354a75, standard library plus numpy only.

Two ratios are reported for every cell and they are NOT interchangeable:

  ratio_zero   measured fraction of R with at least one decomposition, over
               eq. (11)'s P. eq. (11) is a statement about exactly that
               fraction, so this is the directly comparable quantity and it is
               the HEADLINE ratio.
  ratio_mean   measured mean decomposition count over the modelled mean
               2^{tk-n}/t!. A ratio built from means can agree while the zero
               fraction disagrees, which is why the contract asks for both.

Intervals are Wilson score intervals for the proportion and normal intervals
for the mean, both at 95%, divided by the modelled quantity. Wilson rather than
Wald because several cells have hit fractions near 0, where a Wald interval
leaves the unit interval and would fabricate precision.
"""
from __future__ import annotations

import math
from math import comb, exp, lgamma

import numpy as np

Z95 = 1.959963984540054


# --------------------------------------------------------------------------
# eq. (11) and its class-count variants
# --------------------------------------------------------------------------
def class_count(variant: str, v_size: int, t: int) -> float:
    """K, the number of classes of t-tuples from V under permutation."""
    if variant == "semaev_v_to_the_t_over_t_factorial":
        return v_size ** t / math.factorial(t)
    if variant == "exact_multiset_count_binom_V_plus_t_minus_1_choose_t":
        return float(comb(v_size + t - 1, t))
    if variant == "known_false_v_to_the_t_no_symmetry":
        return float(v_size ** t)
    raise ValueError(f"unknown class-count variant {variant}")


def eq11(n: int, t: int, k: int,
         variant: str = "semaev_v_to_the_t_over_t_factorial") -> dict:
    """P = 1 - exp(-K/q); with Semaev's K this is 1 - exp(-2^{tk-n}/t!)."""
    q = float(1 << n)
    K = class_count(variant, 1 << k, t)
    lam = K / q
    return {"class_count": K, "lambda": lam, "P": 1.0 - exp(-lam)}


# --------------------------------------------------------------------------
# Intervals
# --------------------------------------------------------------------------
def wilson(successes: int, trials: int, z: float = Z95) -> tuple[float, float]:
    if trials == 0:
        return (0.0, 1.0)
    p = successes / trials
    d = 1.0 + z * z / trials
    centre = (p + z * z / (2 * trials)) / d
    half = z * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials * trials)) / d
    return (max(0.0, centre - half), min(1.0, centre + half))


def mean_interval(counts: np.ndarray, z: float = Z95) -> tuple[float, float]:
    nobs = counts.size
    if nobs == 0:
        return (0.0, 0.0)
    m = float(counts.mean())
    sd = float(counts.std(ddof=1)) if nobs > 1 else 0.0
    half = z * sd / math.sqrt(nobs)
    return (max(0.0, m - half), m + half)


# --------------------------------------------------------------------------
# Poisson fit
# --------------------------------------------------------------------------
def _gammq(a: float, x: float) -> float:
    """Regularised upper incomplete gamma Q(a, x); series/continued fraction."""
    if x < 0 or a <= 0:
        raise ValueError("bad arguments")
    if x == 0:
        return 1.0
    if x < a + 1:
        ap, total, term = a, 1.0 / a, 1.0 / a
        for _ in range(1000):
            ap += 1
            term *= x / ap
            total += term
            if abs(term) < abs(total) * 1e-14:
                break
        return 1.0 - total * exp(-x + a * math.log(x) - lgamma(a))
    tiny = 1e-300
    b, c, d = x + 1.0 - a, 1.0 / 1e-300, 1.0 / (x + 1.0 - a)
    h = d
    for i in range(1, 1000):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-14:
            break
    return exp(-x + a * math.log(x) - lgamma(a)) * h


def chi2_sf(stat: float, dof: int) -> float:
    if dof <= 0:
        return float("nan")
    return _gammq(dof / 2.0, stat / 2.0)


def poisson_pmf(k: int, lam: float) -> float:
    if lam <= 0:
        return 1.0 if k == 0 else 0.0
    return exp(-lam + k * math.log(lam) - lgamma(k + 1))


def poisson_sf(k: int, lam: float) -> float:
    """P[X >= k] for X ~ Poisson(lam)."""
    if k <= 0:
        return 1.0
    total = 0.0
    for i in range(0, k):
        total += poisson_pmf(i, lam)
    return max(0.0, 1.0 - total)


def poisson_fit(counts: np.ndarray) -> dict:
    """Chi-square goodness of fit of the per-R counts to Poisson(mean).

    Bins are pooled from the tail down until every expected cell is at least 5,
    which is the condition under which the chi-square reference distribution is
    usable at all; the number of pooled bins is reported so a reader can see
    how much resolution the test actually had.
    """
    nobs = int(counts.size)
    lam = float(counts.mean())
    if nobs == 0:
        return {"applicable": False, "reason": "no draws"}
    if lam == 0.0:
        return {"applicable": False, "reason": "every count is zero",
                "fitted_lambda": 0.0}
    top = int(counts.max())
    observed = np.bincount(counts.astype(np.int64), minlength=top + 1).astype(float)
    expected = np.array([poisson_pmf(i, lam) * nobs for i in range(top + 1)])
    expected = np.append(expected, max(0.0, nobs - expected.sum()))
    observed = np.append(observed, 0.0)
    obs, exp_, i = [], [], 0
    while i < expected.size:
        o, e = observed[i], expected[i]
        while e < 5.0 and i + 1 < expected.size:
            i += 1
            o += observed[i]
            e += expected[i]
        obs.append(o)
        exp_.append(e)
        i += 1
    if len(obs) > 1 and exp_[-1] < 5.0:
        obs[-2] += obs[-1]; exp_[-2] += exp_[-1]
        obs.pop(); exp_.pop()
    if len(obs) < 2:
        return {"applicable": False, "reason": "fewer than two usable bins",
                "fitted_lambda": lam}
    stat = float(sum((o - e) ** 2 / e for o, e in zip(obs, exp_)))
    dof = len(obs) - 1 - 1          # one parameter (lambda) estimated
    if dof <= 0:
        return {"applicable": False, "reason": "no degrees of freedom",
                "fitted_lambda": lam}
    return {"applicable": True, "fitted_lambda": lam, "chi2": stat,
            "dof": dof, "p_value": chi2_sf(stat, dof), "bins": len(obs),
            "observed_pooled": [float(v) for v in obs],
            "expected_pooled": [float(v) for v in exp_]}


def extreme_tail_check(counts: np.ndarray) -> dict:
    """Is the largest observed count plausible under the fitted Poisson law?

    A bulk fit can pass while the tail is wrong, which indicates the wrong law
    rather than a wrong constant; this is the contract's first tail check.
    """
    nobs = int(counts.size)
    if nobs == 0:
        return {"applicable": False}
    lam = float(counts.mean())
    top = int(counts.max())
    p_ge = poisson_sf(top, lam) if lam > 0 else (1.0 if top == 0 else 0.0)
    p_any = 1.0 - (1.0 - p_ge) ** nobs if 0.0 <= p_ge <= 1.0 else float("nan")
    return {"applicable": True, "max_count": top, "fitted_lambda": lam,
            "p_single_draw_at_least_max": p_ge,
            "p_any_of_n_draws_at_least_max": p_any, "draws": nobs}


# --------------------------------------------------------------------------
# The ratio block
# --------------------------------------------------------------------------
def ratio_block(counts: np.ndarray, n: int, t: int, k: int,
                variant: str) -> dict:
    model = eq11(n, t, k, variant)
    nobs = int(counts.size)
    hits = int(np.count_nonzero(counts > 0))
    frac = hits / nobs if nobs else float("nan")
    lo, hi = wilson(hits, nobs)
    mlo, mhi = mean_interval(counts)
    mean = float(counts.mean()) if nobs else float("nan")
    P, lam = model["P"], model["lambda"]
    return {
        "class_count_variant": variant,
        "modelled_class_count": model["class_count"],
        "modelled_lambda": lam,
        "modelled_P_zero_complement": P,
        "measured_hit_fraction": frac,
        "measured_hit_fraction_ci95": [lo, hi],
        "measured_zero_fraction": 1.0 - frac if nobs else float("nan"),
        "measured_mean_count": mean,
        "measured_mean_ci95": [mlo, mhi],
        "ratio_zero_headline": frac / P if P > 0 else float("nan"),
        "ratio_zero_ci95": [lo / P, hi / P] if P > 0 else [float("nan")] * 2,
        "ratio_mean": mean / lam if lam > 0 else float("nan"),
        "ratio_mean_ci95": ([mlo / lam, mhi / lam] if lam > 0
                            else [float("nan")] * 2),
        "hits": hits, "draws": nobs,
    }
