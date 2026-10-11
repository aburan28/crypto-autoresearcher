"""Exact statistics for EXP-CERTBIN-3f06d1 (tail_checks RC-3).

NEW MODULE. Every binomial / hypergeometric tail below is an exact rational
(Python ints and fractions.Fraction); Clopper-Pearson bounds are found by
bisection with the binomial sums evaluated in decimal arithmetic at 80
significant digits. No floating survival function is used. Tails are reported
as exact fractions (numerator/denominator digits are not stored; the value is
reported as log10 to 30 significant digits and as a float).
"""
from decimal import Decimal, getcontext
from fractions import Fraction
from functools import lru_cache
from math import comb

getcontext().prec = 80
D0, D1 = Decimal(0), Decimal(1)


def log10_fraction(fr):
    fr = Fraction(fr)
    if fr == 0:
        return None
    if fr == 1:
        return "0"
    v = (Decimal(fr.numerator).ln() - Decimal(fr.denominator).ln()) / Decimal(10).ln()
    return f"{v:.30g}"


def frac_report(fr):
    fr = Fraction(fr)
    return {"value": float(fr), "log10": (None if fr == 0 else float(Decimal(log10_fraction(fr)))),
            "log10_str": log10_fraction(fr), "exact": "rational (python Fraction)"}


# ---------------------------------------------------------------------------
# binomial with p = 1/2: exact integer arithmetic
# ---------------------------------------------------------------------------
EXACT_BAND_MAX_N = 40000


@lru_cache(maxsize=None)
def band_half(n, tail=Fraction(1, 2000)):
    """Two-sided 99.9% band of Bin(n, 1/2): the integer interval [lo, hi]
    with lo the LARGEST integer with P[X < lo] <= 0.0005 and hi the SMALLEST
    integer with P[X > hi] <= 0.0005. Exact integer comparison for
    n <= 40000; above that, log-space summation in 80-digit decimal arithmetic
    (band_half_large; RC-3 allows log-space summation at >= 50 digits)."""
    if n == 0:
        return (0, 0)
    if n > EXACT_BAND_MAX_N:
        return band_half_large(n, tail)
    tot = 1 << n
    tn, td = tail.numerator, tail.denominator
    # lo: largest l with P[X < l] <= tail, i.e. td * sum_{j<l} C(n, j) <= tn * 2^n
    c = 1
    cum = 0
    lo = 0
    j = 0
    while j <= n:
        if td * (cum + c) <= tn * tot:
            cum += c
            j += 1
            lo = j
            c = c * (n - j + 1) // j
        else:
            break
    # by symmetry of Bin(n, 1/2): P[X > h] = P[X < n - h], so hi = n - lo
    return (lo, n - lo)


_BERN = [Fraction(1, 6), Fraction(-1, 30), Fraction(1, 42), Fraction(-1, 30), Fraction(5, 66),
         Fraction(-691, 2730), Fraction(7, 6), Fraction(-3617, 510), Fraction(43867, 798)]


def _dec_pi():
    """pi to the current decimal precision (Python decimal documentation recipe)."""
    getcontext().prec += 2
    three = Decimal(3)
    lasts, t, s, n, na, d, da = 0, three, 3, 1, 0, 0, 24
    while s != lasts:
        lasts = s
        n, na = n + na, na + 8
        d, da = d + da, da + 32
        t = (t * n) / d
        s += t
    getcontext().prec -= 2
    return +s


_LN2PI = None


def _ln_fact(m):
    """ln(m!) in 80-digit decimal: Stirling series with 9 Bernoulli terms
    (m >= 10^4; truncation error < 10^-70)."""
    global _LN2PI
    if _LN2PI is None:
        _LN2PI = (2 * _dec_pi()).ln()
    assert m >= 10000
    M = Decimal(m)
    s = (M + Decimal("0.5")) * M.ln() - M + _LN2PI / 2
    for i, B in enumerate(_BERN, start=1):
        k2 = 2 * i
        s += Decimal(B.numerator) / Decimal(B.denominator) / (Decimal(k2 * (k2 - 1)) * M ** (k2 - 1))
    return s


def _cdf_half_large(k, n):
    """P[Bin(n, 1/2) <= k] for k < n/2, by log-space pmf at k and the ratio
    recurrence downwards, summed until the terms are < 10^-75 of the sum."""
    lp = _ln_fact(n) - _ln_fact(k) - _ln_fact(n - k) - n * Decimal(2).ln()
    term = lp.exp()
    s = term
    j = k
    eps = Decimal(10) ** -75
    while j > 0:
        term = term * Decimal(j) / Decimal(n - j + 1)
        s += term
        j -= 1
        if term < s * eps:
            break
    return s


@lru_cache(maxsize=None)
def band_half_large(n, tail=Fraction(1, 2000)):
    t = Decimal(tail.numerator) / Decimal(tail.denominator)
    # lo = largest l with P[X <= l - 1] <= tail; binary search on l in [1, n//2]
    import math
    L, H = n // 2 - 10 * math.isqrt(n), n // 2  # 10 sd below the mean: P[X <= L-1] < 1e-22
    assert L >= 10001 and _cdf_half_large(L - 1, n) <= t
    while L < H:
        mid = (L + H + 1) // 2
        if _cdf_half_large(mid - 1, n) <= t:
            L = mid
        else:
            H = mid - 1
    return (L, n - L)


@lru_cache(maxsize=None)
def band_binom(n, p, tail=Fraction(1, 2000)):
    """Exact two-sided 99.9% band of Bin(n, p) for rational p."""
    p = Fraction(p)
    pmf = [Fraction(comb(n, i)) * p ** i * (1 - p) ** (n - i) for i in range(n + 1)]
    lo = 0
    acc = Fraction(0)
    while lo + 1 <= n and acc + pmf[lo] <= tail:
        acc += pmf[lo]
        lo += 1
    hi = n
    acc = Fraction(0)
    while hi - 1 >= 0 and acc + pmf[hi] <= tail:
        acc += pmf[hi]
        hi -= 1
    return (lo, hi)


def binom_sf_exact(k, n, p):
    """P[Bin(n, p) >= k], exact Fraction."""
    p = Fraction(p)
    if k <= 0:
        return Fraction(1)
    if k > n:
        return Fraction(0)
    return sum(Fraction(comb(n, i)) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def fisher_one_sided_greater(a, b, c, d):
    """Exact one-sided Fisher test for the 2x2 table [[a, b], [c, d]] (rows:
    group 1, group 2; columns: success, failure), alternative: group-1 success
    rate higher. p = P[X >= a], X ~ Hypergeometric(N = a+b+c+d, K = a+c
    successes, n = a+b draws). Exact Fraction."""
    N = a + b + c + d
    K = a + c
    n = a + b
    den = comb(N, n)
    lo = max(0, n - (N - K))
    hi = min(n, K)
    num = sum(comb(K, i) * comb(N - K, n - i) for i in range(max(a, lo), hi + 1))
    return Fraction(num, den)


# ---------------------------------------------------------------------------
# Clopper-Pearson in 80-digit decimal arithmetic
# ---------------------------------------------------------------------------
def _cdf_dec(x, n, p):
    """P[Bin(n, p) <= x] in Decimal."""
    if x < 0:
        return D0
    if x >= n:
        return D1
    q = D1 - p
    if p == D0:
        return D1
    if q == D0:
        return D0
    term = q ** n
    s = term
    r = p / q
    for i in range(0, x):
        term = term * Decimal(n - i) / Decimal(i + 1) * r
        s += term
    return s


def _sf_dec(x, n, p):
    """P[Bin(n, p) >= x] in Decimal (summed directly over the upper tail)."""
    if x <= 0:
        return D1
    if x > n:
        return D0
    if p == D0:
        return D0
    if p == D1:
        return D1
    q = D1 - p
    term = p ** n
    s = term
    r = q / p
    for i in range(n, x, -1):
        term = term * Decimal(i) / Decimal(n - i + 1) * r
        s += term
    return s


def _sf_any(x, n, p):
    """P[X >= x], summing the shorter tail (80-digit decimal)."""
    if x <= n - x:
        return D1 - _cdf_dec(x - 1, n, p)
    return _sf_dec(x, n, p)


def _cdf_any(x, n, p):
    """P[X <= x], summing the shorter tail (80-digit decimal)."""
    if x <= n - x:
        return _cdf_dec(x, n, p)
    return D1 - _sf_dec(x + 1, n, p)


@lru_cache(maxsize=None)
def clopper_pearson(x, n, alpha_str="0.05", iters=120):
    """Exact CP interval (decimal bisection, 80 digits, 120 halvings). Returns
    [lo, hi] as floats plus 25-digit strings."""
    if n == 0:
        return None
    a2 = Decimal(alpha_str) / 2
    if x == 0:
        lo = D0
    else:
        L, H = D0, D1
        for _ in range(iters):
            m = (L + H) / 2
            if _sf_any(x, n, m) >= a2:
                H = m
            else:
                L = m
        lo = (L + H) / 2
    if x == n:
        hi = D1
    else:
        L, H = D0, D1
        for _ in range(iters):
            m = (L + H) / 2
            if _cdf_any(x, n, m) <= a2:
                H = m
            else:
                L = m
        hi = (L + H) / 2
    return {"lo": float(lo), "hi": float(hi), "lo_str": f"{lo:.25g}", "hi_str": f"{hi:.25g}",
            "method": "Clopper-Pearson 95%, decimal bisection at 80 significant digits, 120 halvings"}


def cp_pair(x, n):
    r = clopper_pearson(x, n)
    return None if r is None else [r["lo"], r["hi"]]
