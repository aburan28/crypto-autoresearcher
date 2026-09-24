"""Exact statistics for EXP-CERTBIN-a58c63 (RC-3): every binomial and Poisson
interval and tail is computed in exact rational/integer arithmetic or with
mpmath at 60 significant digits, and small tails are reported as log10.
No floating-point survival function is used."""
import math
from fractions import Fraction
from collections import Counter

import mpmath

mpmath.mp.dps = 60
DPS = 60


def _mpf(x):
    if isinstance(x, Fraction):
        return mpmath.mpf(x.numerator) / x.denominator
    return mpmath.mpf(x)


def binom_cdf_mp(k, n, p):
    """P[Bin(n, p) <= k] at 60 digits (p an mpf/Fraction/int)."""
    p = _mpf(p)
    if k < 0:
        return mpmath.mpf(0)
    if k >= n:
        return mpmath.mpf(1)
    q = 1 - p
    s = mpmath.mpf(0)
    for i in range(0, k + 1):
        s += mpmath.binomial(n, i) * p ** i * q ** (n - i)
    return s


def binom_sf_mp(k, n, p):
    """P[Bin(n, p) >= k]."""
    if k <= 0:
        return mpmath.mpf(1)
    if k > n:
        return mpmath.mpf(0)
    p = _mpf(p)
    q = 1 - p
    s = mpmath.mpf(0)
    for i in range(k, n + 1):
        s += mpmath.binomial(n, i) * p ** i * q ** (n - i)
    return s


def _bisect(f, lo, hi, it=200):
    lo, hi = mpmath.mpf(lo), mpmath.mpf(hi)
    for _ in range(it):
        mid = (lo + hi) / 2
        if f(mid):
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def clopper_pearson(x, n, level=Fraction(95, 100)):
    """Exact two-sided CP interval; returned as [float, float] plus strings at
    30 digits (the float is for display; the string is the exact-arithmetic value)."""
    if n == 0:
        return None
    a = (1 - _mpf(level)) / 2
    lo = mpmath.mpf(0) if x == 0 else _bisect(lambda p: binom_sf_mp(x, n, p) >= a, 0, 1)
    hi = mpmath.mpf(1) if x == n else _bisect(lambda p: binom_cdf_mp(x, n, p) <= a, 0, 1)
    return {"lo": float(lo), "hi": float(hi), "lo_str": mpmath.nstr(lo, 30), "hi_str": mpmath.nstr(hi, 30),
            "x": x, "n": n, "level": str(level), "method": "Clopper-Pearson, mpmath 60 digits, bisection"}


def binom_tail_exact(m, p, o):
    """P[Bin(m, p) >= o] exactly (Fraction) and its log10."""
    p = Fraction(p)
    q = 1 - p
    s = Fraction(0)
    for i in range(o, m + 1):
        s += math.comb(m, i) * p ** i * q ** (m - i)
    return s


def frac_log10(fr):
    if fr == 0:
        return None
    return float(mpmath.log10(_mpf(fr)))


def binom_band_half(N, alpha=Fraction(1, 1000)):
    """Exact two-sided (1 - alpha) acceptance band [lo, hi] of Bin(N, 1/2):
    lo = the largest integer with P[X < lo] <= alpha/2, hi = the smallest with
    P[X > hi] <= alpha/2 (integer arithmetic)."""
    return binom_band(N, Fraction(1, 2), alpha)


def binom_band(N, p, alpha=Fraction(1, 1000)):
    p = Fraction(p)
    q = 1 - p
    half = alpha / 2
    pm = [math.comb(N, i) * p ** i * q ** (N - i) for i in range(N + 1)] if N <= 3000 else None
    if pm is None:
        raise ValueError("N too large for exact band")
    cum = Fraction(0)
    lo = 0
    # P[X < lo] = sum_{i < lo} pm[i]
    while lo <= N and cum + pm[lo] <= half:
        cum += pm[lo]
        lo += 1
    cum = Fraction(0)
    hi = N
    while hi >= 0 and cum + pm[hi] <= half:
        cum += pm[hi]
        hi -= 1
    return lo, hi


def poisson_cdf_mp(k, mu):
    mu = _mpf(mu)
    if k < 0:
        return mpmath.mpf(0)
    s = mpmath.mpf(0)
    term = mpmath.e ** (-mu)
    for i in range(0, k + 1):
        if i > 0:
            term = term * mu / i
        s += term
    return s


def poisson_interval(mu, level=Fraction(999, 1000)):
    """Exact two-sided acceptance interval [lo, hi] for a Poisson(mu) count:
    lo = the largest integer with P[X < lo] <= (1 - level)/2, hi = the smallest
    with P[X > hi] <= (1 - level)/2 (60-digit arithmetic; mu rational)."""
    a = (1 - _mpf(level)) / 2
    lo = 0
    while poisson_cdf_mp(lo, mu) <= a:   # P[X < lo + 1] <= a  -> lo + 1 admissible
        lo += 1
    hi = 0
    while 1 - poisson_cdf_mp(hi, mu) > a:
        hi += 1
    return {"lo": lo, "hi": hi, "mu": str(mu) if isinstance(mu, Fraction) else mpmath.nstr(_mpf(mu), 30),
            "mu_float": float(_mpf(mu)), "level": str(level),
            "definition": "lo = largest integer with P[X < lo] <= (1-level)/2; hi = smallest with P[X > hi] <= (1-level)/2"}


def poisson_ratio_interval(x19, n19, x17, n17, level=Fraction(95, 100)):
    """Exact conditional-binomial interval for rate19/rate17 (rates x/N):
    given T = x19 + x17, x19 ~ Bin(T, pi), pi = n19*rho / (n17 + n19*rho).
    CP interval for pi mapped to rho = pi*n17 / ((1 - pi)*n19)."""
    T = x19 + x17
    if T == 0:
        return {"lo": 0.0, "hi": math.inf, "lo_str": "0", "hi_str": "inf", "T": 0,
                "note": "no events in either cell: the interval is [0, inf)"}
    cp = clopper_pearson(x19, T, level)
    lo_pi = mpmath.mpf(cp["lo_str"])
    hi_pi = mpmath.mpf(cp["hi_str"])

    def rho(pi):
        if pi >= 1:
            return mpmath.inf
        return pi * n17 / ((1 - pi) * n19)
    lo, hi = rho(lo_pi), rho(hi_pi)
    return {"lo": float(lo), "hi": float(hi), "lo_str": mpmath.nstr(lo, 30), "hi_str": mpmath.nstr(hi, 30),
            "T": T, "x19": x19, "x17": x17, "n19": n19, "n17": n17, "point": (x19 / n19) / (x17 / n17) if x17 and n19 else None}


def median(xs):
    xs = sorted(xs)
    n = len(xs)
    if n == 0:
        return None
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


def entropy_bits(labels):
    c = Counter(labels)
    n = sum(c.values())
    if n == 0:
        return None, 0, 0, 0
    h = -sum((v / n) * math.log2(v / n) for v in c.values())
    return h, len(c), n, max(c.values())


def _log_pmf(i, N, lp, lq):
    return mpmath.loggamma(N + 1) - mpmath.loggamma(i + 1) - mpmath.loggamma(N - i + 1) + i * lp + (N - i) * lq


def binom_tail_logspace(k, N, p, lower=True):
    """P[X <= k] (lower=True, k below the mean) or P[X >= k] (lower=False, k
    above the mean) for X ~ Bin(N, p), at 60 digits: terms summed from k
    outward while they decrease geometrically; the remainder is bounded by
    term * r / (1 - r) with r the (decreasing) term ratio and stops below
    1e-80 relative. Returns an mpf."""
    p = _mpf(p)
    lp, lq = mpmath.log(p), mpmath.log(1 - p)
    if lower:
        if k < 0:
            return mpmath.mpf(0)
        i = k
        t = mpmath.exp(_log_pmf(i, N, lp, lq))
        s = t
        while i > 0:
            r = mpmath.mpf(i) * (1 - p) / ((N - i + 1) * p)
            t = t * r
            i -= 1
            s += t
            if r < 1 and t * r / (1 - r) < s * mpmath.mpf(10) ** -80:
                break
        return s
    else:
        if k > N:
            return mpmath.mpf(0)
        i = k
        t = mpmath.exp(_log_pmf(i, N, lp, lq))
        s = t
        while i < N:
            r = mpmath.mpf(N - i) * p / ((i + 1) * (1 - p))
            t = t * r
            i += 1
            s += t
            if r < 1 and t * r / (1 - r) < s * mpmath.mpf(10) ** -80:
                break
        return s


def binom_band_mp(N, p, alpha=Fraction(1, 1000)):
    """Two-sided (1 - alpha) acceptance band of Bin(N, p) at 60 digits:
    lo = largest integer with P[X < lo] <= alpha/2; hi = smallest with
    P[X > hi] <= alpha/2. Uses the exact rational band when N <= 3000."""
    if N <= 3000:
        return binom_band(N, p, alpha)
    a = _mpf(alpha) / 2
    mean = N * _mpf(p)
    lo_l, lo_h = 0, int(mean)
    while lo_h - lo_l > 1:
        mid = (lo_l + lo_h) // 2
        if binom_tail_logspace(mid - 1, N, p, lower=True) <= a:
            lo_l = mid
        else:
            lo_h = mid
    hi_l, hi_h = int(mean), N
    while hi_h - hi_l > 1:
        mid = (hi_l + hi_h) // 2
        if binom_tail_logspace(mid + 1, N, p, lower=False) <= a:
            hi_h = mid
        else:
            hi_l = mid
    return lo_l, hi_h
