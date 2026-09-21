"""
Permutation p-value and Holm-Bonferroni correction for EXP-MONO-670aa6,
per specification.yaml `arms_and_controls.measured_null` and
`multiplicity_correction`.
"""
import math


def permutation_pvalue(stat_treatment, null_stats):
    """p = (1 + #{null draws with |stat_null - median(null)| >= |stat_treatment
    - median(null)|}) / (len(null_stats) + 1), two-sided, per the frozen
    formula. `null_stats` is the list of the 200 matched-null statistic
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
        # table with row sums n1,n2 and column sum m1 fixed, cell (0,0)=x
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
