#!/usr/bin/env python3
"""TASK-20260803-05e072 -- statistics for RC-9 (round profile) and RC-10 (k-byte
null scaling). Exact methods only; no normal approximations, no scipy.

NESTING NOTE (load-bearing for the intervals): the k-byte-prefix events are
NESTED -- a trial counted at k=j is necessarily counted at every k<j. So n_k are
NOT independent Poissons and the usual two-Poisson ratio test does not apply.
Conditional on n_k, the count n_{k+1} is Binomial(n_k, q_k) with
q_k = p_{k+1}/p_k under the independence model. Intervals on q_k are exact
Clopper-Pearson; the successive ratio R_k = n_k/n_{k+1} = 1/q_k_hat and its
interval is the inverted Clopper-Pearson interval. This is exact given nesting.
"""
import json, math, os
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "runs")


def load(name):
    with open(os.path.join(RUNS, name + ".json")) as f:
        return json.load(f)


# ---------- exact Beta / F quantiles via bisection on the regularized inc beta
def betacf(a, b, x):
    MAXIT, EPS, FPMIN = 500, 3.0e-16, 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < FPMIN:
        d = FPMIN
    d = 1.0 / d
    h = d
    for m in range(1, MAXIT + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN:
            d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN:
            d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1.0) < EPS:
            break
    return h


def betai(a, b, x):
    """regularized incomplete beta I_x(a,b)"""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    bt = math.exp(lbeta + a * math.log(x) + b * math.log1p(-x))
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * betacf(a, b, x) / a
    return 1.0 - bt * betacf(b, a, 1.0 - x) / b


def beta_quantile(p, a, b):
    lo, hi = 0.0, 1.0
    for _ in range(300):
        mid = 0.5 * (lo + hi)
        if betai(a, b, mid) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def clopper_pearson(k, n, alpha=0.05):
    """exact two-sided 100(1-alpha)% interval on a binomial proportion"""
    lo = 0.0 if k == 0 else beta_quantile(alpha / 2.0, k, n - k + 1)
    hi = 1.0 if k == n else beta_quantile(1.0 - alpha / 2.0, k + 1, n - k)
    return lo, hi


def gamma_quantile_chi2(p, k2):
    """quantile of Chi2 with k2 df, by bisection on the regularized gamma P"""
    if k2 <= 0:
        return 0.0
    a = k2 / 2.0
    lo, hi = 0.0, 1.0
    while gammap(a, hi / 2.0) < p:
        hi *= 2.0
        if hi > 1e12:
            break
    for _ in range(400):
        mid = 0.5 * (lo + hi)
        if gammap(a, mid / 2.0) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def gammap(a, x):
    """regularized lower incomplete gamma P(a,x)"""
    if x < 0 or a <= 0:
        raise ValueError
    if x == 0:
        return 0.0
    if x < a + 1.0:
        ap, s, de = a, 1.0 / a, 1.0 / a
        for _ in range(2000):
            ap += 1.0
            de *= x / ap
            s += de
            if abs(de) < abs(s) * 1e-16:
                break
        return s * math.exp(-x + a * math.log(x) - math.lgamma(a))
    # continued fraction for Q
    FPMIN = 1e-300
    b = x + 1.0 - a
    c = 1.0 / FPMIN
    d = 1.0 / b
    h = d
    for i in range(1, 2000):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < FPMIN:
            d = FPMIN
        c = b + an / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1.0) < 1e-16:
            break
    q = math.exp(-x + a * math.log(x) - math.lgamma(a)) * h
    return 1.0 - q


def poisson_ci(n, alpha=0.05):
    """exact (Garwood) two-sided interval on a Poisson mean from a count n"""
    lo = 0.0 if n == 0 else 0.5 * gamma_quantile_chi2(alpha / 2.0, 2 * n)
    hi = 0.5 * gamma_quantile_chi2(1.0 - alpha / 2.0, 2 * (n + 1))
    return lo, hi


def poisson_cdf(k, lam):
    if k < 0:
        return 0.0
    return 1.0 - gammap(k + 1, lam) if lam > 0 else 1.0


P = [1.0 - (1.0 - 2.0 ** (-8 * k)) ** 4 for k in (1, 2, 3, 4)]   # exact model
UNION = [4.0 * 2.0 ** (-8 * k) for k in (1, 2, 3, 4)]            # union bound


def arm_table(a):
    T = a["nontrivial_trials"]
    n = a["W_ge1_prefix_k"]
    rows = []
    for i in range(4):
        exp = T * P[i]
        lo, hi = poisson_ci(n[i])
        rows.append({
            "k": i + 1,
            "count": n[i],
            "exposure_nontrivial_trials": T,
            "rate_measured": n[i] / T,
            "rate_model_exact": P[i],
            "expected_count_model_exact": exp,
            "expected_count_union_bound": T * UNION[i],
            "obs_over_model": (n[i] / exp) if exp > 0 else None,
            "obs_over_model_ci95_exact_poisson": [lo / exp, hi / exp] if exp > 0 else None,
        })
    return rows


def ratio_rows(a):
    """successive ratios R_k = n_k / n_{k+1}, exact via the nesting binomial"""
    n = a["W_ge1_prefix_k"]
    out = []
    for i in range(3):
        nk, nk1 = n[i], n[i + 1]
        model_R = P[i] / P[i + 1]
        model_union_R = 256.0
        if nk == 0:
            out.append({"k_from": i + 1, "k_to": i + 2, "n_k": nk, "n_k_plus_1": nk1,
                        "ratio_point": None, "ratio_ci95": None,
                        "model_ratio_exact": model_R,
                        "note": "no events at k; ratio undefined"})
            continue
        qlo, qhi = clopper_pearson(nk1, nk)
        rlo = (1.0 / qhi) if qhi > 0 else float("inf")
        rhi = (1.0 / qlo) if qlo > 0 else float("inf")
        out.append({
            "k_from": i + 1, "k_to": i + 2,
            "n_k": nk, "n_k_plus_1": nk1,
            "ratio_point": (nk / nk1) if nk1 > 0 else None,
            "ratio_ci95_exact_clopper_pearson_inverted": [rlo, rhi],
            "model_ratio_exact": model_R,
            "model_ratio_union_bound": model_union_R,
            "model_ratio_inside_ci95": (rlo <= model_R <= rhi),
            "union_bound_256_inside_ci95": (rlo <= model_union_R <= rhi),
            "method": "n_{k+1} | n_k ~ Binomial(n_k, q); exact CP interval on q, inverted to R=1/q",
        })
    return out


def compare_arms(live, null_):
    """r=5 vs r=10 at matched exposure, per k. Unpaired exact conditional binomial."""
    out = []
    nl, nn = live["W_ge1_prefix_k"], null_["W_ge1_prefix_k"]
    Tl, Tn = live["nontrivial_trials"], null_["nontrivial_trials"]
    for i in range(4):
        m = nl[i] + nn[i]
        if m == 0:
            out.append({"k": i + 1, "live": nl[i], "null": nn[i], "rate_ratio_point": None,
                        "note": "no events in either arm"})
            continue
        plo, phi = clopper_pearson(nl[i], m)
        f = Tn / Tl   # exposure correction (equal here)
        def to_r(p):
            return float("inf") if p >= 1.0 else (p / (1.0 - p)) * f
        out.append({
            "k": i + 1,
            "live_r5_count": nl[i], "null_r10_count": nn[i],
            "rate_ratio_point_r5_over_r10": (nl[i] / nn[i] * f) if nn[i] > 0 else None,
            "rate_ratio_ci95_exact": [to_r(plo), to_r(phi)],
            "one_inside_ci95": (to_r(plo) <= 1.0 <= to_r(phi)),
            "caveat": ("the two arms consume IDENTICAL plaintext/swap streams "
                       "(same seed, armid, thread_seeds), so this comparison is "
                       "paired BY DESIGN but analysed UNPAIRED because trial "
                       "indices are not logged (RC-11 is unrun)."),
        })
    return out


if __name__ == "__main__":
    arms = ["K-EQUIV-R5-K1-A2", "K-R10-NULL", "K-R5-LIVE", "K-R10-NULL-P30"]
    res = {"model": {"exact_p_k": P, "union_bound_p_k": UNION,
                     "exact_successive_ratios": [P[i] / P[i + 1] for i in range(3)]},
           "arms": {}, "ratios": {}, "r5_vs_r10_matched_2p30": None,
           "r5_vs_r10_matched_2p24": None}
    A = {}
    for name in arms:
        a = load(name)
        A[name] = a
        res["arms"][name] = {"rounds": a["rounds"], "log2N": a["log2N"],
                             "prefix_k_table": arm_table(a),
                             "W_ge1_nontrivial": a["W_ge1_nontrivial"],
                             "prefix_k4_equals_W_ge1": a["prefix_k4_equals_W_ge1"]}
        res["ratios"][name] = ratio_rows(a)
    res["r5_vs_r10_matched_2p30"] = compare_arms(A["K-EQUIV-R5-K1-A2"], A["K-R10-NULL-P30"])
    res["r5_vs_r10_matched_2p24"] = compare_arms(A["K-R5-LIVE"], A["K-R10-NULL"])
    with open(os.path.join(HERE, "stats.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))
