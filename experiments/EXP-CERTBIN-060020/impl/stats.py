"""Exact statistics (tail_checks RC-3): binomial tails as exact rationals
(math.comb, fractions), Clopper-Pearson bounds by bisection on exact-sum
tails evaluated with mpmath at 60 significant digits, one-sided Fisher exact
test as an exact rational."""
from __future__ import annotations

import math
from fractions import Fraction

import mpmath

mpmath.mp.dps = 60


def binom_tail_ge(k, n, p):
    """P(X >= k), X ~ Bin(n, p), p a Fraction -> Fraction (exact)."""
    q = 1 - p
    return sum((Fraction(math.comb(n, i)) * p ** i * q ** (n - i) for i in range(max(k, 0), n + 1)),
               Fraction(0))


def binom_tail_le(k, n, p):
    q = 1 - p
    return sum((Fraction(math.comb(n, i)) * p ** i * q ** (n - i) for i in range(0, min(k, n) + 1)),
               Fraction(0))


def fmt(fr):
    """Fraction -> dict with a 30-digit decimal and log10 (for tiny values)."""
    if fr == 0:
        return {"value": "0", "log10": None}
    v = mpmath.mpf(fr.numerator) / mpmath.mpf(fr.denominator)
    lg = mpmath.log10(v)
    return {"value": mpmath.nstr(v, 30), "log10": mpmath.nstr(lg, 20)}


def _mp_tail_ge(k, n, p):
    return mpmath.fsum(mpmath.mpf(math.comb(n, i)) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def _mp_tail_le(k, n, p):
    return mpmath.fsum(mpmath.mpf(math.comb(n, i)) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1))


def cp95(k, n, alpha=Fraction(1, 20)):
    """Exact Clopper-Pearson two-sided (1 - alpha) interval for k / n."""
    if n == 0:
        return None
    a2 = mpmath.mpf(alpha.numerator) / mpmath.mpf(alpha.denominator) / 2
    if k == 0:
        lo = mpmath.mpf(0)
    else:
        a, b = mpmath.mpf(0), mpmath.mpf(1)
        for _ in range(200):
            m = (a + b) / 2
            if _mp_tail_ge(k, n, m) < a2:
                a = m
            else:
                b = m
        lo = (a + b) / 2
    if k == n:
        hi = mpmath.mpf(1)
    else:
        a, b = mpmath.mpf(0), mpmath.mpf(1)
        for _ in range(200):
            m = (a + b) / 2
            if _mp_tail_le(k, n, m) > a2:
                a = m
            else:
                b = m
        hi = (a + b) / 2
    return [float(lo), float(hi), mpmath.nstr(lo, 20), mpmath.nstr(hi, 20)]


def fisher_one_sided_greater(a, b, c, d):
    """Table [[a, b], [c, d]] (group 1: a successes, b failures; group 2: c, d).
    Exact P(X >= a) under the hypergeometric null with fixed margins."""
    n1, n2 = a + b, c + d
    k = a + c
    N = n1 + n2
    den = math.comb(N, k)
    p = Fraction(0)
    for x in range(a, min(n1, k) + 1):
        if k - x > n2 or k - x < 0:
            continue
        p += Fraction(math.comb(n1, x) * math.comb(n2, k - x), den)
    return p


def power_table():
    ps = ["0.02", "0.05", "0.10", "0.50", "0.84", "0.90", "0.95", "0.99"]
    rows = []
    for ps_ in ps:
        p = Fraction(ps_)
        rows.append({
            "p": ps_,
            "N400_P(w>=360)": fmt(binom_tail_ge(360, 400, p)),
            "N400_P(w<=40)": fmt(binom_tail_le(40, 400, p)),
            "N400_P(w<=200)": fmt(binom_tail_le(200, 400, p)),
            "n200_P(count>=180)": fmt(binom_tail_ge(180, 200, p)),
            "n200_P(count<=20)": fmt(binom_tail_le(20, 200, p)),
        })
    cps = {f"{k}/{n}": cp95(k, n) for k, n in [(0, 200), (200, 200), (0, 400), (400, 400), (386, 386)]}
    return {"method": "exact rational binomial sums (math.comb, fractions); decimals and log10 via mpmath at 60 digits; "
                      "Clopper-Pearson by 200-step bisection on exact-sum tails at 60 digits",
            "thresholds": {"PERSIST": "w >= ceil(0.9 N) = 360", "DECAY": "w <= floor(0.1 N) = 40",
                           "E-PERSIST falsified": "w <= floor(N/2) = 200", "arm n = 200": ">= 180 / <= 20"},
            "rows": rows, "cp95_bounds": cps}
