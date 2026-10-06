"""Small numerical library (no scipy): regularized incomplete gamma, Poisson tails,
Poisson-binomial tail by exact DP, compound-Poisson pmf by FFT, Fisher exact test.
All exact up to floating point; no randomness.
"""
import math

import numpy as np


def gammainc_lower_reg(a, x):
    """P(a, x) = gamma(a, x)/Gamma(a), regularized lower incomplete gamma (a > 0, x >= 0).
    Series for x < a + 1, continued fraction otherwise (Numerical-Recipes-style)."""
    if x <= 0:
        return 0.0
    gln = math.lgamma(a)
    if x < a + 1:
        ap, s, d = a, 1.0 / a, 1.0 / a
        for _ in range(100000):
            ap += 1
            d *= x / ap
            s += d
            if abs(d) < abs(s) * 1e-16:
                break
        return s * math.exp(-x + a * math.log(x) - gln)
    b = x + 1 - a
    c = 1e300
    d = 1 / b
    h = d
    for i in range(1, 100000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        if abs(d) < 1e-300:
            d = 1e-300
        c = b + an / c
        if abs(c) < 1e-300:
            c = 1e-300
        d = 1 / d
        de = d * c
        h *= de
        if abs(de - 1) < 1e-16:
            break
    return 1.0 - math.exp(-x + a * math.log(x) - gln) * h


def poisson_sf(k, lam):
    """P(Poisson(lam) >= k) for integer k >= 0 (= P(Gamma(k, 1) <= lam) for k >= 1)."""
    if k <= 0:
        return 1.0
    return gammainc_lower_reg(k, lam)


def poisson_binomial_tail(ps, k):
    """P(sum of independent Bernoulli(p_i) >= k), exact DP."""
    dist = np.zeros(len(ps) + 1)
    dist[0] = 1.0
    for p in ps:
        dist[1:] = dist[1:] * (1 - p) + dist[:-1] * p
        dist[0] *= (1 - p)
    return float(dist[k:].sum()) if k > 0 else 1.0


def cp_pmf(lam, jump_pmf, L=None):
    """pmf of a compound Poisson sum: K ~ Poisson(lam), jumps i.i.d. with pmf jump_pmf
    (jump_pmf[j] = P(J = j), j >= 1). FFT on a grid of length L (power of two) chosen so
    the mass beyond L is negligible; returns a non-negative, renormalised array."""
    jump_pmf = np.asarray(jump_pmf, dtype=float)
    mean = lam * float(np.dot(np.arange(len(jump_pmf)), jump_pmf))
    var = lam * float(np.dot(np.arange(len(jump_pmf)) ** 2, jump_pmf))
    if L is None:
        need = int(mean + 40 * math.sqrt(var + 1) + len(jump_pmf) * 4 + 64)
        L = 1 << max(10, (need - 1).bit_length())
    g = np.zeros(L)
    n = min(len(jump_pmf), L)
    g[:n] = jump_pmf[:n]
    phi = np.fft.rfft(g)
    f = np.fft.irfft(np.exp(lam * (phi - 1.0)), n=L)
    f = np.clip(f, 0.0, None)
    s = f.sum()
    return f / s if s > 0 else f


def fisher_exact(a, b, c, d):
    """2x2 table [[a, b], [c, d]] (rows: group 1, group 2; cols: event, no event).
    Returns (p_two_sided, p_greater) where 'greater' = group 1 has the higher event rate."""
    n1, n2, k = a + b, c + d, a + c
    n = n1 + n2

    def pmf(x):
        return math.comb(n1, x) * math.comb(n2, k - x) / math.comb(n, k)
    lo, hi = max(0, k - n2), min(k, n1)
    p_obs = pmf(a)
    two = sum(pmf(x) for x in range(lo, hi + 1) if pmf(x) <= p_obs * (1 + 1e-12))
    greater = sum(pmf(x) for x in range(a, hi + 1))
    return min(1.0, two), min(1.0, greater)
