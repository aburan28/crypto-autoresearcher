"""Exact one-sided Poisson test and exact (Garwood) Poisson confidence
interval, per specification.yaml Stage 3. No scipy is available in this
environment; mpmath (bundled with sympy, already a repository dependency)
supplies the regularized incomplete gamma function these formulas reduce
to, and bisection inverts it -- exact to the precision mpmath is configured
for, not a normal-approximation shortcut.

Standard identities used (Garwood 1936; e.g. Ulm 1990):
  P(Poisson(mu) <= k) = Q(k+1, mu)   (regularized upper incomplete gamma)
  P(Poisson(mu) >= k) = P(k, mu)     (regularized LOWER incomplete gamma;
                                      equals 1 - P(Poisson(mu) <= k-1))
  Exact CI for observed count k at level 1-alpha:
    lower = 0                                  if k == 0
    lower = gammaincinv_lower(k, alpha/2)      otherwise
    upper = gammaincinv_lower(k+1, 1-alpha/2)
  where gammaincinv_lower(a, q) solves P(a, x) = q for x (P = regularized
  LOWER incomplete gamma), found here by bisection since mpmath has no
  built-in inverse.
"""
from __future__ import annotations

import mpmath

mpmath.mp.dps = 50


def poisson_sf(k: int, mu) -> float:
    """P(Poisson(mu) >= k), exact via the regularized LOWER incomplete
    gamma function P(k, mu) = 1 - P(Poisson(mu) <= k-1)."""
    mu = mpmath.mpf(mu)
    if k <= 0:
        return 1.0
    return float(mpmath.gammainc(k, 0, mu, regularized=True))


def _lower_reg_gamma(a, x):
    return mpmath.gammainc(a, 0, x, regularized=True)


def _gammaincinv_lower(a, q, hi_start=None):
    """Solve P(a, x) = q for x >= 0 by bisection (P is strictly increasing
    in x for a > 0, 0 < q < 1)."""
    a = mpmath.mpf(a)
    q = mpmath.mpf(q)
    if q <= 0:
        return 0.0
    if q >= 1:
        raise ValueError("_gammaincinv_lower: q must be < 1")
    lo = mpmath.mpf(0)
    hi = mpmath.mpf(hi_start if hi_start else max(float(a) * 4 + 10, 10))
    while _lower_reg_gamma(a, hi) < q:
        hi *= 2
    for _ in range(200):
        mid = (lo + hi) / 2
        if _lower_reg_gamma(a, mid) < q:
            lo = mid
        else:
            hi = mid
    return float((lo + hi) / 2)


def poisson_exact_ci(k: int, alpha: float = 0.01) -> tuple[float, float]:
    """Exact (Garwood) two-sided (1-alpha) confidence interval on the
    Poisson rate parameter given an observed count k."""
    if k < 0:
        raise ValueError("poisson_exact_ci: k must be >= 0")
    lower = 0.0 if k == 0 else _gammaincinv_lower(k, alpha / 2)
    upper = _gammaincinv_lower(k + 1, 1 - alpha / 2, hi_start=max(k * 4 + 10, 10))
    return lower, upper


def rho_hat_with_ci(k: int, mu0: float, alpha: float = 0.01) -> dict:
    """rho_hat = k/mu0 with its 95%-style exact-Poisson CI (CI on the mean
    divided by mu0), plus the one-sided p-value for H0: mean=mu0 against a
    higher-rate alternative (used for the joint alpha=0.01/effect>=3
    falsification bar)."""
    if mu0 <= 0:
        return {"k": k, "mu0": mu0, "rho_hat": None, "ci_low": None,
                "ci_high": None, "one_sided_p_ge_k": None}
    lo, hi = poisson_exact_ci(k, alpha=0.05)  # 95% CI, per spec wording
    p_value = poisson_sf(k, mu0)  # one-sided: P(X >= k | mean=mu0)
    return {
        "k": k, "mu0": mu0, "rho_hat": k / mu0,
        "ci_low": lo / mu0, "ci_high": hi / mu0,
        "one_sided_p_ge_k_at_mu0": p_value,
    }
