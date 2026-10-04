"""Clopper-Pearson exact two-sided interval (equal tails), by bisection on the
exact binomial CDF. Cross-checked in the self-tests against mpmath's
regularized incomplete beta (Beta quantile form)."""
from math import comb


def binom_cdf(x: int, n: int, p: float) -> float:
    if x < 0:
        return 0.0
    if x >= n:
        return 1.0
    return sum(comb(n, i) * p ** i * (1.0 - p) ** (n - i) for i in range(x + 1))


def _bisect(f, lo=0.0, hi=1.0, iters=200):
    # f increasing in p with a single sign change
    for _ in range(iters):
        mid = (lo + hi) / 2
        if f(mid) < 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def clopper_pearson(x: int, n: int, alpha: float = 0.05):
    if n == 0:
        return None
    a2 = alpha / 2
    if x == 0:
        lo = 0.0
    else:
        # P(X >= x ; p) = a2, increasing in p
        lo = _bisect(lambda p: (1.0 - binom_cdf(x - 1, n, p)) - a2)
    if x == n:
        hi = 1.0
    else:
        # P(X <= x ; p) = a2, decreasing in p
        hi = _bisect(lambda p: a2 - binom_cdf(x, n, p))
    return [lo, hi]
