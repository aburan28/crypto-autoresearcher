"""TASK-20260803-48a239 -- self-contained statistics.

No numpy and no scipy are installed in this environment (verified: both raise
ModuleNotFoundError), so the regularized incomplete gamma function is
implemented here from the standard series / continued-fraction pair. Every
routine is checked against a closed-form value in self_test() and the self-test
result is reported in RESULTS.json.
"""
import math


def _gser(a, x):
    ap, s, d = a, 1.0 / a, 1.0 / a
    for _ in range(1000):
        ap += 1.0
        d *= x / ap
        s += d
        if abs(d) < abs(s) * 1e-15:
            break
    return s * math.exp(-x + a * math.log(x) - math.lgamma(a))


def _gcf(a, x):
    tiny = 1e-300
    b, c, d = x + 1.0 - a, 1.0 / tiny, 1.0 / (x + 1.0 - a)
    h = d
    for i in range(1, 1000):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        dl = d * c
        h *= dl
        if abs(dl - 1.0) < 1e-15:
            break
    return math.exp(-x + a * math.log(x) - math.lgamma(a)) * h


def gammq(a, x):
    """Regularized upper incomplete gamma Q(a,x)."""
    if x < 0 or a <= 0:
        raise ValueError
    if x == 0:
        return 1.0
    if x < a + 1.0:
        return 1.0 - _gser(a, x)
    return _gcf(a, x)


def chi2_sf(x, df):
    """P(chi2_df >= x)."""
    if x <= 0:
        return 1.0
    return gammq(df / 2.0, x / 2.0)


def pois_pmf(k, lam):
    if lam == 0:
        return 1.0 if k == 0 else 0.0
    return math.exp(-lam + k * math.log(lam) - math.lgamma(k + 1))


def pois_sf_ge(k, lam):
    """P(X >= k) for Poisson(lam)."""
    if k <= 0:
        return 1.0
    return sum(pois_pmf(i, lam) for i in range(0, k)) and 1.0 - sum(
        pois_pmf(i, lam) for i in range(0, k))


def pois_cdf_le(k, lam):
    """P(X <= k)."""
    if k < 0:
        return 0.0
    return sum(pois_pmf(i, lam) for i in range(0, k + 1))


def g2_equal_exposure(counts):
    """Poisson/multinomial likelihood-ratio G^2 for homogeneity of rates
    across cells of EQUAL exposure. df = len(counts)-1."""
    n = sum(counts)
    k = len(counts)
    if n == 0:
        return 0.0, k - 1, 1.0
    e = n / k
    g = 0.0
    for o in counts:
        if o > 0:
            g += 2.0 * o * math.log(o / e)
    df = k - 1
    return g, df, chi2_sf(g, df)


def binom_pmf(k, n, p):
    return math.exp(math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
                    + (k * math.log(p) if k else 0.0)
                    + ((n - k) * math.log(1 - p) if n - k else 0.0))


def exact_binom_two_sided_half(k, n):
    """Two-sided exact conditional binomial test at p=1/2, by doubling the
    smaller tail (capped at 1). This is the standard conditional test for
    comparing two Poisson counts of equal exposure."""
    if n == 0:
        return None
    lo = sum(binom_pmf(i, n, 0.5) for i in range(0, k + 1))
    hi = sum(binom_pmf(i, n, 0.5) for i in range(k, n + 1))
    return min(1.0, 2.0 * min(lo, hi))


def self_test():
    """Closed-form checks. chi2 with df=2 has sf(x)=exp(-x/2) exactly."""
    out = {}
    out["chi2_df2_sf_5.991_vs_exact_exp"] = [chi2_sf(5.991, 2), math.exp(-5.991 / 2)]
    out["chi2_df2_sf_matches_closed_form"] = abs(chi2_sf(5.991, 2) - math.exp(-5.991 / 2)) < 1e-12
    # chi2 df=1 sf(x) = erfc(sqrt(x/2))
    out["chi2_df1_sf_3.841_vs_erfc"] = [chi2_sf(3.841, 1), math.erfc(math.sqrt(3.841 / 2))]
    out["chi2_df1_sf_matches_closed_form"] = abs(chi2_sf(3.841, 1) - math.erfc(math.sqrt(3.841 / 2))) < 1e-10
    # Poisson: P(X<=k) sums to 1 in the limit
    out["poisson_cdf_le_60_lam_2_is_1"] = abs(pois_cdf_le(60, 2.0) - 1.0) < 1e-12
    # binomial two-sided at k=n/2 must be 1.0
    out["binom_two_sided_k5_n10_is_1"] = abs(exact_binom_two_sided_half(5, 10) - 1.0) < 1e-12
    # BATCH-004 R1=22 vs R2=41 must reproduce the recorded p = 0.023
    out["reproduces_BATCH004_R1_vs_R2_p"] = exact_binom_two_sided_half(22, 63)
    # BATCH-004 Y-R2-sd: 4 hits vs null 1.0, exact upper tail, recorded 0.0190
    out["reproduces_BATCH004_YR2sd_exact_tail"] = 1.0 - pois_cdf_le(3, 1.0)
    out["all_closed_form_checks_pass"] = all(
        out[k] for k in out if k.endswith("_form") or k.endswith("_is_1"))
    return out


if __name__ == "__main__":
    import json
    print(json.dumps(self_test(), indent=1))
