"""
ks.py -- two-sample Kolmogorov-Smirnov statistic (stdlib only, no scipy/numpy
available in this environment) and its standard ASYMPTOTIC critical value, used as
the frozen primary decision statistic (spec.decision_table.primary_statistic).

PRE-REGISTERED (before any run, per spec.analysis_plan): alpha=0.05, using the
standard large-sample KS critical-value approximation
  D_crit(alpha) = c(alpha) * sqrt((n+m)/(n*m)),  c(0.05)=1.36
(Massey 1951 / standard reference asymptotic formula). DISCLOSED CAVEAT: this is an
asymptotic approximation; at n=m=8 (this experiment's sample sizes) it is the
standard practical choice in the absence of an exact small-sample KS table (no
external stats library available in this pure-Python, no-CAS environment -- see
MANIFEST.md precedent), but is not an exact small-sample critical value. Reported
alongside the raw statistic, never silently treated as exact.
"""
import math

ALPHA = 0.05
C_ALPHA = 1.36  # standard constant for alpha=0.05


def ks_two_sample(sample1, sample2):
    """Two-sample KS statistic D = sup_x |F1(x)-F2(x)|, plus the asymptotic
    critical value and reject/do-not-reject call at ALPHA. `inf` values in either
    sample are excluded from the numeric KS computation (reported separately as a
    censored count -- an unbounded ratio cannot be placed on a finite CDF), matching
    the same "never silently drop, never fabricate a finite value" discipline
    reused/analysis.py already applies to zero-median ratios."""
    s1 = sorted(x for x in sample1 if x != float("inf"))
    s2 = sorted(x for x in sample2 if x != float("inf"))
    inf_censored_1 = sum(1 for x in sample1 if x == float("inf"))
    inf_censored_2 = sum(1 for x in sample2 if x == float("inf"))
    n, m = len(s1), len(s2)
    if n == 0 or m == 0:
        return {
            "D": None, "n": n, "m": m,
            "inf_censored_1": inf_censored_1, "inf_censored_2": inf_censored_2,
            "d_crit": None, "rejects": None,
            "note": "one sample entirely censored (all ratios were inf); KS undefined",
        }
    all_vals = sorted(set(s1 + s2))
    D = 0.0
    i = j = 0
    for x in all_vals:
        while i < n and s1[i] <= x:
            i += 1
        while j < m and s2[j] <= x:
            j += 1
        F1 = i / n
        F2 = j / m
        D = max(D, abs(F1 - F2))
    d_crit = C_ALPHA * math.sqrt((n + m) / (n * m))
    rejects = D > d_crit
    return {
        "D": D, "n": n, "m": m,
        "inf_censored_1": inf_censored_1, "inf_censored_2": inf_censored_2,
        "d_crit": d_crit, "alpha": ALPHA, "rejects": rejects,
        "method": "asymptotic large-sample approximation D_crit=1.36*sqrt((n+m)/(n*m)), "
                  "disclosed as not an exact small-sample critical value",
    }
