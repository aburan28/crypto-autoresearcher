#!/usr/bin/env python3
"""EXP-SEMBIN-35bf67 statistics (OP-STATS, OP-NULL, OP-SEP). Pure Python, no numpy/scipy."""
import math
import random


def _binom_cdf(x, n, p):
    if x < 0:
        return 0.0
    if x >= n:
        return 1.0
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(x + 1))


def clopper_pearson(x, n, alpha=0.05):
    """Exact two-sided (1-alpha) interval for a binomial proportion."""
    if n == 0:
        return (None, None)

    # bisection on the monotone binomial tail functions
    if x == 0:
        lower = 0.0
    else:
        lo, hi = 0.0, 1.0
        for _ in range(200):
            mid = (lo + hi) / 2
            if 1 - _binom_cdf(x - 1, n, mid) < alpha / 2:
                lo = mid
            else:
                hi = mid
        lower = (lo + hi) / 2
    if x == n:
        upper = 1.0
    else:
        lo, hi = 0.0, 1.0
        for _ in range(200):
            mid = (lo + hi) / 2
            if _binom_cdf(x, n, mid) > alpha / 2:
                lo = mid
            else:
                hi = mid
        upper = (lo + hi) / 2
    return (round(lower, 6), round(upper, 6))


def bootstrap_rate(outcomes, B=10000, seed=20261005, alpha=0.05):
    """Percentile bootstrap interval for the mean of 0/1 outcomes."""
    n = len(outcomes)
    if n == 0:
        return (None, None)
    rng = random.Random(seed)
    k = sum(outcomes)
    means = []
    for _ in range(B):
        c = 0
        for _ in range(n):
            if rng.randrange(n) < k:
                c += 1
        means.append(c / n)
    means.sort()
    lo = means[int(math.floor(alpha / 2 * B))]
    hi = means[min(B - 1, int(math.ceil((1 - alpha / 2) * B)) - 1)]
    return (lo, hi)


def fisher_two_sided(a, b, c, d):
    """Two-sided Fisher exact p for [[a, b], [c, d]] (sum of tables with P <= P_obs)."""
    r1, r2, c1 = a + b, c + d, a + c
    n = r1 + r2
    if n == 0:
        return None

    def p_of(x):
        return math.comb(r1, x) * math.comb(r2, c1 - x) / math.comb(n, c1)

    lo, hi = max(0, c1 - r2), min(r1, c1)
    pobs = p_of(a)
    tot = sum(p_of(x) for x in range(lo, hi + 1) if p_of(x) <= pobs * (1 + 1e-9))
    return min(1.0, tot)


def rate_block(outcomes_fail):
    """outcomes_fail: list of 0/1 (1 = NOT SOLV4)."""
    n = len(outcomes_fail)
    k = sum(outcomes_fail)
    return {"n": n, "failures": k, "rate": (k / n) if n else None,
            "clopper_pearson_95": clopper_pearson(k, n) if n else None,
            "bootstrap_percentile_95": bootstrap_rate(outcomes_fail) if n else None}
