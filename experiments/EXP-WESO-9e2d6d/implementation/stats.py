"""Statistics for EXP-WESO-9e2d6d (no scipy on this host; mpmath/numpy only).

Choices (the specification names the test, not always its realisation; these
are fixed before Stage C and recorded in implementation.md):
  * Wilson score interval, two-sided 99% (z = 2.5758293035489).
  * Clopper-Pearson exact interval, two-sided 99% (beta quantiles by bisection
    on the regularized incomplete beta, Numerical Recipes continued fraction).
  * Poisson exact (Garwood) two-sided 99% interval; the 'upper 99% bound' of
    TC-2 is its upper end (0.995 quantile).
  * Two-sample KS: D = sup |F1 - F2| over the pooled support (ties handled
    exactly); p-value from the asymptotic Kolmogorov distribution with the
    Stephens correction lambda = (en + 0.12 + 0.11/en) D, en = sqrt(n m/(n+m)).
  * Two-sample smooth-count test: pooled two-proportion z-test, two-sided.
  * Chi-square survival via regularized upper incomplete gamma.
  * OLS slope with two-sided 99% t interval (df = n - 2).
"""
import math

import mpmath
import numpy as np

Z99 = 2.5758293035489004


def wilson(k, n, z=Z99):
    if n == 0:
        return (float("nan"), float("nan"))
    ph = k / n
    den = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / den
    h = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return (max(0.0, c - h), min(1.0, c + h))


def _betacf(a, b, x):
    """Continued fraction for the incomplete beta (Numerical Recipes 6.4, modified Lentz)."""
    MAXIT, EPS, FPMIN = 100000, 1e-15, 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    if abs(d) < FPMIN:
        d = FPMIN
    d = 1.0 / d
    h = d
    for m in range(1, MAXIT + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = FPMIN if abs(d) < FPMIN else d
        c = 1.0 + aa / c
        c = FPMIN if abs(c) < FPMIN else c
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = FPMIN if abs(d) < FPMIN else d
        c = 1.0 + aa / c
        c = FPMIN if abs(c) < FPMIN else c
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1.0) < EPS:
            return h
    raise RuntimeError("betacf did not converge")


def betai(a, b, x):
    """Regularized incomplete beta I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x)
    if x < (a + 1.0) / (a + b + 2.0):
        return math.exp(lbt) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbt) * _betacf(b, a, 1.0 - x) / b


def _beta_ppf(q, a, b):
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if betai(a, b, mid) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def clopper_pearson(k, n, alpha=0.01):
    lo = 0.0 if k == 0 else _beta_ppf(alpha / 2, k, n - k + 1)
    hi = 1.0 if k == n else _beta_ppf(1 - alpha / 2, k + 1, n - k)
    return (lo, hi)


def ratio_interval(s1, s2, alpha=0.01):
    """T = s1/s2 with interval from Clopper-Pearson on s1/(s1+s2), theta -> theta/(1-theta)."""
    n = s1 + s2
    if n == 0:
        return (float("nan"), (float("nan"), float("nan")))
    lo, hi = clopper_pearson(s1, n, alpha)
    f = lambda t: (t / (1 - t)) if t < 1 else float("inf")
    point = (s1 / s2) if s2 > 0 else float("inf")
    return (point, (f(lo), f(hi)))


def poisson_interval(c, conf=0.99):
    """Garwood exact two-sided interval for a Poisson mean given count c."""
    mpmath.mp.dps = 30
    a = (1 - conf) / 2

    def cdf(lmb, x):  # P(X <= x; lmb) = Q(x+1, lmb)
        return mpmath.gammainc(x + 1, lmb, mpmath.inf, regularized=True)

    # upper: cdf(U, c) = a
    lo, hi = mpmath.mpf(0), mpmath.mpf(c + 50 + 10 * math.sqrt(c + 1))
    for _ in range(200):
        mid = (lo + hi) / 2
        if cdf(mid, c) > a:
            lo = mid
        else:
            hi = mid
    upper = float((lo + hi) / 2)
    if c == 0:
        lower = 0.0
    else:
        lo, hi = mpmath.mpf(0), mpmath.mpf(c + 1)
        for _ in range(200):
            mid = (lo + hi) / 2
            if 1 - cdf(mid, c - 1) < a:
                lo = mid
            else:
                hi = mid
        lower = float((lo + hi) / 2)
    return (lower, upper)


def chi2_sf(x, df):
    mpmath.mp.dps = 30
    return float(mpmath.gammainc(df / 2.0, x / 2.0, mpmath.inf, regularized=True))


def kolmogorov_sf(lam):
    if lam <= 0:
        return 1.0
    s = 0.0
    for j in range(1, 200):
        t = 2 * (-1) ** (j - 1) * math.exp(-2 * j * j * lam * lam)
        s += t
        if abs(t) < 1e-18:
            break
    return min(1.0, max(0.0, s))


def ks_2samp(a, b):
    a = np.sort(np.asarray(a, dtype=float))
    b = np.sort(np.asarray(b, dtype=float))
    n, m = len(a), len(b)
    allv = np.concatenate([a, b])
    fa = np.searchsorted(a, allv, side="right") / n
    fb = np.searchsorted(b, allv, side="right") / m
    d = float(np.max(np.abs(fa - fb)))
    en = math.sqrt(n * m / (n + m))
    p = kolmogorov_sf((en + 0.12 + 0.11 / en) * d)
    return d, p


def two_prop_z(k1, n1, k2, n2):
    p1, p2 = k1 / n1, k2 / n2
    pp = (k1 + k2) / (n1 + n2)
    se = math.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2))
    if se == 0:
        return 0.0, 1.0
    z = (p1 - p2) / se
    return z, math.erfc(abs(z) / math.sqrt(2))


def diff_prop_wald(k1, n1, k2, n2, z=Z99):
    p1, p2 = k1 / n1, k2 / n2
    se = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    d = p1 - p2
    return d, (d - z * se, d + z * se)


def t_ppf(q, df):
    def cdf(t):
        x = df / (df + t * t)
        tail = 0.5 * betai(df / 2.0, 0.5, x)
        return 1 - tail if t >= 0 else tail
    lo, hi = -1e3, 1e3
    for _ in range(200):
        mid = (lo + hi) / 2
        if cdf(mid) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def ols_slope(x, y, conf=0.99):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    n = len(x)
    if n < 3:
        return {"n": n, "slope": None, "ci": None, "note": "fewer than 3 points"}
    xm, ym = x.mean(), y.mean()
    sxx = float(((x - xm) ** 2).sum())
    b = float(((x - xm) * (y - ym)).sum() / sxx)
    a = ym - b * xm
    res = y - (a + b * x)
    s2 = float((res ** 2).sum() / (n - 2))
    se = math.sqrt(s2 / sxx)
    t = t_ppf(1 - (1 - conf) / 2, n - 2)
    return {"n": n, "slope": b, "intercept": float(a), "se": se, "ci": [b - t * se, b + t * se], "t_quantile": t}
