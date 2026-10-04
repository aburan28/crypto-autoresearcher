"""Exact binomial intervals (RC-3): Clopper-Pearson 95% bounds by bisection on
the exact binomial tail, evaluated with math.comb and fractions.Fraction.
No floating-point survival function is used. Bounds are bracketed to width
< 2^-80 and reported as decimal strings (15 significant digits) together with
the exact bracketing rationals' decimal endpoints."""
from fractions import Fraction
from math import comb

ALPHA_HALF = Fraction(1, 40)   # 0.025


def cdf_le(x, n, p):
    """P(X <= x), X ~ Bin(n, p), exact."""
    q = 1 - p
    return sum(comb(n, i) * p ** i * q ** (n - i) for i in range(0, x + 1))


def _bisect(f, lo, hi, iters=80):
    # f increasing on [lo, hi]; find root of f(p) = 0
    for _ in range(iters):
        mid = (lo + hi) / 2
        if f(mid) < 0:
            lo = mid
        else:
            hi = mid
    return lo, hi


def _dec(fr, digits=15):
    # exact rational to decimal string with 'digits' significant digits
    from decimal import Decimal, getcontext
    getcontext().prec = 40
    return format(Decimal(fr.numerator) / Decimal(fr.denominator), f".{digits}g")


def clopper_pearson(x, n):
    if n == 0:
        return {"x": x, "n": n, "lower": None, "upper": None, "note": "n = 0"}
    if x == 0:
        lo = (Fraction(0), Fraction(0))
    else:
        # lower: P(X >= x | p) = 0.025  <=>  1 - cdf_le(x-1) - 0.025 = 0 (increasing in p)
        lo = _bisect(lambda p: (1 - cdf_le(x - 1, n, p)) - ALPHA_HALF, Fraction(0), Fraction(1))
    if x == n:
        hi = (Fraction(1), Fraction(1))
    else:
        # upper: P(X <= x | p) = 0.025 ; cdf decreasing in p -> use 0.025 - cdf (increasing)
        hi = _bisect(lambda p: ALPHA_HALF - cdf_le(x, n, p), Fraction(0), Fraction(1))
    return {"x": x, "n": n, "rate": _dec(Fraction(x, n)),
            "lower": _dec(lo[0]), "upper": _dec(hi[1]),
            "lower_bracket": [_dec(lo[0], 25), _dec(lo[1], 25)],
            "upper_bracket": [_dec(hi[0], 25), _dec(hi[1], 25)],
            "_lower_exact_lo": lo[0], "_upper_exact_hi": hi[1],
            "method": "Clopper-Pearson 95% (two-sided, 0.025 per tail), exact rational bisection to width < 2^-80"}


def public(ci):
    return {k: v for k, v in ci.items() if not k.startswith("_")}


def separated(ci_u, ci_null):
    """CP95 lower bound of U strictly exceeds CP95 upper bound of the null.
    Uses conservative bracket ends: U lower's LOW end vs null upper's HIGH end."""
    if ci_u["n"] == 0 or ci_null["n"] == 0:
        return None
    return ci_u["_lower_exact_lo"] > ci_null["_upper_exact_hi"]
