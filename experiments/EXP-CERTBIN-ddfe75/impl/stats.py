"""Exact statistics (tail_checks RC-3): binomial tails as exact rationals
(fractions, math.comb) and Clopper-Pearson 95% bounds by bisection on the
exact tail evaluated with mpmath at 60 significant digits. No floating-point
survival function is used."""
from __future__ import annotations

from fractions import Fraction
from math import comb

import mpmath

mpmath.mp.dps = 60


def binom_cdf_exact(k, n, p):
    """P(X <= k), X ~ Bin(n, p), p a Fraction -> Fraction."""
    p = Fraction(p)
    q = 1 - p
    return sum((comb(n, i) * p ** i * q ** (n - i) for i in range(0, k + 1)), Fraction(0))


def binom_sf_exact(k, n, p):
    """P(X >= k) -> Fraction."""
    p = Fraction(p)
    q = 1 - p
    return sum((comb(n, i) * p ** i * q ** (n - i) for i in range(k, n + 1)), Fraction(0))


def _mp_tail_ge(k, n, p):
    return mpmath.fsum(mpmath.binomial(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def _mp_tail_le(k, n, p):
    return mpmath.fsum(mpmath.binomial(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1))


def cp95(x, n, alpha=Fraction(1, 20)):
    """Exact Clopper-Pearson two-sided (1-alpha) interval -> (lo, hi) as mpf."""
    if n == 0:
        return (mpmath.mpf(0), mpmath.mpf(1))
    a2 = mpmath.mpf(alpha.numerator) / alpha.denominator / 2

    def bisect(f, lo, hi):
        # f(lo) < 0 < f(hi) or reversed; 200 halvings -> < 1e-60
        flo = f(lo)
        for _ in range(200):
            mid = (lo + hi) / 2
            fm = f(mid)
            if (fm < 0) == (flo < 0):
                lo, flo = mid, fm
            else:
                hi = mid
        return (lo + hi) / 2

    if x == 0:
        lo = mpmath.mpf(0)
    else:
        # P(X >= x | p) = alpha/2, increasing in p
        lo = bisect(lambda p: _mp_tail_ge(x, n, p) - a2, mpmath.mpf(0), mpmath.mpf(1))
    if x == n:
        hi = mpmath.mpf(1)
    else:
        # P(X <= x | p) = alpha/2, decreasing in p
        hi = bisect(lambda p: a2 - _mp_tail_le(x, n, p), mpmath.mpf(0), mpmath.mpf(1))
    return lo, hi


def fmt(x, digits=6):
    return float(mpmath.nstr(x, 20)) if x is not None else None


def cp95_json(x, n):
    lo, hi = cp95(x, n)
    return {"x": x, "n": n, "rate": (x / n) if n else None,
            "cp95": [round(float(lo), 6), round(float(hi), 6)],
            "cp95_exact_20dig": [mpmath.nstr(lo, 20), mpmath.nstr(hi, 20)]}


def log10_str(fr):
    if fr == 0:
        return "-inf"
    return mpmath.nstr(mpmath.log10(mpmath.mpf(fr.numerator)) - mpmath.log10(mpmath.mpf(fr.denominator)), 15)


def power_table(n=144):
    t_hi = -(-9 * n // 10)  # ceil(0.9 n)
    t_lo = n // 10
    t_half = n // 2
    rows = []
    for ps in ["3/100", "1/10", "1/2", "9/10", "97/100"]:
        p = Fraction(ps)
        a = binom_sf_exact(t_hi, n, p)
        b = binom_cdf_exact(t_lo, n, p)
        c = binom_cdf_exact(t_half, n, p)
        rows.append({
            "p": ps,
            f"P(w >= {t_hi})": {"value": mpmath.nstr(mpmath.mpf(a.numerator) / a.denominator, 20),
                                "log10": log10_str(a)},
            f"P(w <= {t_lo})": {"value": mpmath.nstr(mpmath.mpf(b.numerator) / b.denominator, 20),
                                "log10": log10_str(b)},
            f"P(w <= {t_half})": {"value": mpmath.nstr(mpmath.mpf(c.numerator) / c.denominator, 20),
                                  "log10": log10_str(c)},
        })
    return {"n": n, "thresholds": {"tensor_ceil_0.9n": t_hi, "linear_floor_0.1n": t_lo,
                                   "half_floor_n/2": t_half},
            "method": "exact rationals (fractions.Fraction, math.comb); decimal via mpmath at 60 digits",
            "rows": rows}
