"""
Permutation p-value, Holm-Bonferroni correction, Fisher exact test, and the
pre-registered Fisher-combined panel-level statistic for EXP-MONO-b19c6b,
per specification.yaml `arms_and_controls.measured_null`,
`multiplicity_correction`, and `arms_and_controls.fisher_combined_panel_statistic`.

`permutation_pvalue` and `holm_bonferroni` are the same frozen formulas as
EXP-MONO-670aa6 used (this contract does not change either definition, only
the panel/seed derivation upstream of them). `fisher_combined_pvalue` is NEW:
-2*sum(ln(p_i)) ~ chi2(2k) under the null (Fisher's method), evaluated via
the exact closed-form chi-squared survival function for even degrees of
freedom (df=2k is always even), so no scipy dependency is needed.
"""
import math


def permutation_pvalue(stat_treatment, null_stats):
    """p = (1 + #{null draws with |stat_null - median(null)| >= |stat_treatment
    - median(null)|}) / (len(null_stats) + 1), two-sided, per the frozen
    formula. `null_stats` is the list of the 20000 matched-null statistic
    values for this curve/statistic/family; `stat_treatment` is either the
    real-arm value (Stage 3) or the null-object-pick value (Stage 2)."""
    n = len(null_stats)
    med = _median(null_stats)
    dev_t = abs(stat_treatment - med)
    count = sum(1 for s in null_stats if abs(s - med) >= dev_t)
    return (1 + count) / (n + 1)


def _median(xs):
    s = sorted(xs)
    n = len(s)
    if n % 2 == 1:
        return s[n // 2]
    return (s[n // 2 - 1] + s[n // 2]) / 2.0


def holm_bonferroni(pvalues, alpha=0.05):
    """Standard Holm step-down procedure. Returns (significant: list[bool]
    in ORIGINAL order, adjusted_pvalues: list[float] in ORIGINAL order,
    n_significant: int). adjusted_p_(i) = max_{j<=i}((n-j+1)*p_(j)), capped
    at 1.0, non-decreasing by construction (the standard Holm adjustment)."""
    n = len(pvalues)
    if n == 0:
        return [], [], 0
    order = sorted(range(n), key=lambda i: pvalues[i])
    adjusted_sorted = []
    running_max = 0.0
    for rank, idx in enumerate(order):  # rank is 0-indexed
        raw_adj = (n - rank) * pvalues[idx]
        running_max = max(running_max, raw_adj)
        adjusted_sorted.append(min(1.0, running_max))
    adjusted = [0.0] * n
    for rank, idx in enumerate(order):
        adjusted[idx] = adjusted_sorted[rank]
    significant = [adjusted[i] < alpha for i in range(n)]
    return significant, adjusted, sum(significant)


def fisher_exact_2x2(a, b, c, d):
    """Two-sided Fisher exact test p-value for the 2x2 table
    [[a,b],[c,d]] via direct hypergeometric summation (a,b,c,d small
    integers at this panel size, exact combinatorics, no scipy dependency)."""
    def log_fact(n):
        return math.lgamma(n + 1)

    n1 = a + b
    n2 = c + d
    m1 = a + c
    N = n1 + n2

    def log_p(x):
        return (log_fact(n1) + log_fact(n2) + log_fact(m1) + log_fact(N - m1)
                - log_fact(N) - log_fact(x) - log_fact(n1 - x)
                - log_fact(m1 - x) - log_fact(n2 - m1 + x))

    lo = max(0, m1 - n2)
    hi = min(n1, m1)
    obs_log_p = log_p(a)
    total = 0.0
    eps = 1e-9
    for x in range(lo, hi + 1):
        lp = log_p(x)
        if lp <= obs_log_p + eps:
            total += math.exp(lp)
    return min(1.0, total)


def chi2_sf_even_df(x, df):
    """Exact survival function P(X > x) for a chi-squared distribution with
    EVEN degrees of freedom df=2k: P(X > x) = exp(-x/2) * sum_{i=0}^{k-1}
    (x/2)^i / i!. Fisher's combined statistic always has df=2k for k pooled
    p-values, so this closed form is exact (no scipy dependency, no
    numerical integration)."""
    assert df % 2 == 0 and df > 0
    k = df // 2
    if x <= 0:
        return 1.0
    half_x = x / 2.0
    # Guard against overflow for large half_x/k by working in log-space when
    # the term sum could be large; at this panel's scale (k<=100, x modest)
    # direct summation is numerically safe, but use log-sum-exp for safety.
    log_terms = []
    log_term = -half_x  # i=0 term: exp(-x/2) * (x/2)^0/0! in log form partially
    # Build log of each term of exp(-x/2) * (x/2)^i / i! directly:
    for i in range(k):
        log_ti = -half_x + i * math.log(half_x) - math.lgamma(i + 1)
        log_terms.append(log_ti)
    m = max(log_terms)
    s = sum(math.exp(t - m) for t in log_terms)
    result = math.exp(m) * s
    return min(1.0, max(0.0, result))


def fisher_combined_pvalue(pvalues):
    """Fisher's method: statistic = -2*sum(ln(p_i)) ~ chi2(2k) under the
    null, for k pooled independent p-values. Returns (statistic, df,
    combined_pvalue) where combined_pvalue = P(chi2(2k) > statistic),
    evaluated via the exact even-df closed form. Floor-immune: a continuous
    statistic with no permutation-count floor, unlike the per-curve
    permutation test."""
    k = len(pvalues)
    if k == 0:
        return 0.0, 0, 1.0
    # Guard p=0 (should not occur with the frozen (1+count)/(n+1) formula,
    # which has floor 1/(n+1) > 0, but guard defensively against log(0)).
    eps = 1e-300
    stat = -2.0 * sum(math.log(max(p, eps)) for p in pvalues)
    df = 2 * k
    combined_p = chi2_sf_even_df(stat, df)
    return stat, df, combined_p
