#!/usr/bin/env python3
# analysis.py -- TASK-20260805-d408ac (BATCH-015, GOAL-AES-003).
#
# Exact conditional-binomial (Poisson-ratio) machinery + Garwood Poisson CIs
# + Clopper-Pearson intervals, written for this task. BEFORE computing any
# new statistic it reproduces the figures published in EV-AES-e4c091
# (14 vs 1: p=9.765625e-4, ratio 14, ratio CI [2.130, 592.0]) and in
# BATCH-014's RESULTS.json self_check block, and the Garwood intervals
# EV-AES-e4c091 published for its N1/N2 arms (x=1 -> [0.025, 5.572];
# x=6 at m=8 -> R CI [0.275, 1.632]). No scipy dependency: exact binomial
# tails via fractions, chi-square quantiles via an implemented regularized
# incomplete gamma inverse.
#
# Pure arithmetic on already-written run JSONs. No status assignment.
import json, math, sys
from fractions import Fraction

def _gammap_series(a, x):
    if x == 0.0: return 0.0
    ap = a; s = 1.0 / a; d = s
    for _ in range(1000):
        ap += 1.0; d *= x / ap; s += d
        if abs(d) < abs(s) * 1e-15: break
    return s * math.exp(-x + a * math.log(x) - math.lgamma(a))

def _gammaq_cf(a, x):
    b = x + 1.0 - a; c = 1e300; d = 1.0 / b; h = d
    for i in range(1, 1000):
        an = -i * (i - a); b += 2.0
        d = an * d + b; d = 1e-300 if abs(d) < 1e-300 else d
        c = b + an / c; c = 1e-300 if abs(c) < 1e-300 else c
        d = 1.0 / d; de = d * c; h *= de
        if abs(de - 1.0) < 1e-15: break
    return h * math.exp(-x + a * math.log(x) - math.lgamma(a))

def gammainc_reg(a, x):
    if x < 0: return 0.0
    if x == 0: return 0.0
    return _gammap_series(a, x) if x < a + 1.0 else 1.0 - _gammaq_cf(a, x)

def qchisq(p, df):
    lo, hi = 0.0, df + 50.0 * math.sqrt(2.0 * df) + 200.0
    while gammainc_reg(df / 2.0, hi / 2.0) < p: hi *= 2
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if gammainc_reg(df / 2.0, mid / 2.0) < p: lo = mid
        else: hi = mid
    return 0.5 * (lo + hi)

def garwood_ci(x, m):
    lo = 0.0 if x == 0 else 0.5 * qchisq(0.025, 2 * x) / m
    hi = 0.5 * qchisq(0.975, 2 * x + 2) / m
    return [lo, hi]

def binom_tail_exact_ge(k, n, p_frac):
    q = Fraction(1) - p_frac
    s = Fraction(0)
    for i in range(k, n + 1):
        s += Fraction(math.comb(n, i)) * p_frac ** i * q ** (n - i)
    return s

def binom_cdf_float(k, n, p):
    s = 0.0
    for i in range(0, k + 1):
        s += math.exp(math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)
                      + i * math.log(p) + (n - i) * math.log1p(-p)) if 0 < p < 1 else (1.0 if (i == n if p == 1 else i == 0) else 0.0)
    return s

def clopper_pearson(x, n):
    if n == 0: return [0.0, 1.0]
    lo = 0.0 if x == 0 else _solve(lambda p: 1.0 - binom_cdf_float(x - 1, n, p) - 0.025)
    hi = 1.0 if x == n else _solve(lambda p: binom_cdf_float(x, n, p) - 0.025)
    return [lo, hi]

def _solve(f):
    lo, hi = 0.0, 1.0
    flo, fhi = f(lo + 1e-16), f(hi - 1e-16)
    for _ in range(300):
        mid = 0.5 * (lo + hi); fm = f(mid)
        if (flo <= 0 and fm <= 0) or (flo > 0 and fm > 0): lo, flo = mid, fm
        else: hi, fhi = mid, fm
    return 0.5 * (lo + hi)

def comparison(x_aes, nontriv_aes, x_sub, nontriv_sub):
    m_aes = Fraction(nontriv_aes * 4, 2 ** 32)
    m_sub = Fraction(nontriv_sub * 4, 2 ** 32)
    n = x_aes + x_sub
    p0 = m_aes / (m_aes + m_sub)
    if n == 0:
        p_val = 1.0
    else:
        tail_ge = binom_tail_exact_ge(x_aes, n, p0)
        tail_le = binom_tail_exact_ge(n - x_aes, n, Fraction(1) - p0)
        p_val = float(min(Fraction(1), 2 * min(tail_ge, tail_le)))
    cp = clopper_pearson(x_aes, n) if n > 0 else [0.0, 1.0]
    scale = float(m_sub / m_aes)
    ratio_point = (float('inf') if x_sub == 0 else (x_aes / float(m_aes)) / (x_sub / float(m_sub)))
    ratio_lo = (cp[0] / (1 - cp[0])) * scale if cp[0] < 1 else float('inf')
    ratio_hi = (cp[1] / (1 - cp[1])) * scale if cp[1] < 1 else float('inf')
    R = x_sub / float(m_sub)
    Rci = garwood_ci(x_sub, float(m_sub))
    return {
        "x_aes": x_aes, "x_sub": x_sub,
        "m_aes": float(m_aes), "m_sub": float(m_sub),
        "nontriv_aes": nontriv_aes, "nontriv_sub": nontriv_sub,
        "n": n, "p0_exact": str(p0), "p0_float": float(p0),
        "p_value": p_val,
        "cp_p_ci": cp,
        "ratio_point": ratio_point,
        "ratio_ci": [ratio_lo, ratio_hi],
        "R_sub_point": R,
        "R_sub_garwood_95ci": Rci,
        "R_ci_contains_1": Rci[0] <= 1.0 <= Rci[1],
        "R_ci_lower_gt_1": Rci[0] > 1.0,
    }

def outcome(cmp):
    if cmp["R_ci_contains_1"] and cmp["p_value"] < 0.01: return "OUTCOME-A''"
    if cmp["R_ci_lower_gt_1"] and cmp["p_value"] >= 0.01: return "OUTCOME-B''"
    return "OUTCOME-C''"

def main():
    runs = sys.argv[1] if len(sys.argv) > 1 else "runs"
    out = {"self_checks": {}, "comparisons": {}, "decision_rule": {}}

    sc = out["self_checks"]
    c1 = comparison(14, 2 ** 30, 1, 2 ** 30)
    sc["ev_e4c091_14_vs_1"] = {
        "p_value": c1["p_value"], "expected": 0.0009765625,
        "ratio_point": c1["ratio_point"], "ratio_ci": c1["ratio_ci"],
        "cp_p_ci": c1["cp_p_ci"],
        "published_ratio_ci": [2.1300416502432267, 591.9684937326185],
        "match_p": abs(c1["p_value"] - 0.0009765625) < 1e-12,
        "match_ratio_ci": abs(c1["ratio_ci"][0] - 2.1300416502432267) < 1e-6
                          and abs(c1["ratio_ci"][1] - 591.9684937326185) < 1e-6,
    }
    c2 = comparison(14, 1073741824, 0, 1073741823)   # BATCH-014 M1-vs-r5 exact inputs
    sc["batch014_M1_14_vs_0"] = {
        "p_value": c2["p_value"], "expected": 0.0001220703125,
        "p0_float": c2["p0_float"], "expected_p0": 0.500000000225,
        "ratio_ci": c2["ratio_ci"],
        "published_ratio_ci_lower": 3.3171226765018393,
        "match_p": abs(c2["p_value"] - 0.0001220703125) < 1e-9,
        "match_ratio_ci_lower": abs(c2["ratio_ci"][0] - 3.3171226765018393) < 1e-6,
    }
    g1 = garwood_ci(1, 1.0)
    g6 = garwood_ci(6, 8.0)
    sc["garwood_ev_e4c091_N1"] = {"ci": g1, "published": [0.025, 5.572],
        "match": round(g1[0], 3) == 0.025 and round(g1[1], 3) == 5.572}
    sc["garwood_ev_e4c091_N2_R"] = {"ci": g6, "published": [0.275, 1.632],
        "match": round(g6[0], 3) == 0.275 and round(g6[1], 3) == 1.632}
    sc["all_pass"] = (sc["ev_e4c091_14_vs_1"]["match_p"] and sc["ev_e4c091_14_vs_1"]["match_ratio_ci"] and
        sc["batch014_M1_14_vs_0"]["match_p"] and sc["batch014_M1_14_vs_0"]["match_ratio_ci_lower"] and
        sc["garwood_ev_e4c091_N1"]["match"] and sc["garwood_ev_e4c091_N2_R"]["match"])

    L1 = json.load(open(f"{runs}/L1-AES-R5-P30.json"))
    M1 = json.load(open(f"{runs}/M1-FF-P30.json"))
    frozen = {"W_ge1_nontrivial": 14, "nontrivial_trials": 1073741824}

    cmp_primary = comparison(L1["W_ge1_nontrivial"], L1["nontrivial_trials"],
                             M1["W_ge1_nontrivial"], M1["nontrivial_trials"])
    cmp_primary["outcome"] = outcome(cmp_primary)
    out["comparisons"]["L1_vs_M1_matched_2p30"] = cmp_primary

    cmp_frozen = comparison(frozen["W_ge1_nontrivial"], frozen["nontrivial_trials"],
                            M1["W_ge1_nontrivial"], M1["nontrivial_trials"])
    cmp_frozen["outcome"] = outcome(cmp_frozen)
    cmp_frozen["note"] = "cross-anchor vs frozen P1-R5-PAIR reading (verified directly from source file)"
    out["comparisons"]["frozen_r5_vs_M1"] = cmp_frozen

    try:
        M2 = json.load(open(f"{runs}/M2-FF-P33.json"))
        cmp_m2 = comparison(L1["W_ge1_nontrivial"], L1["nontrivial_trials"],
                            M2["W_ge1_nontrivial"], M2["nontrivial_trials"])
        cmp_m2["outcome"] = outcome(cmp_m2)
        cmp_m2["note"] = "asymmetric exposure (L1 at 2^30, M2 at 2^33); exposure-weighted p0; reported separately, never pooled with M1 (OBS-B9-5 non-independence class)"
        out["comparisons"]["L1_vs_M2_8x"] = cmp_m2
        cmp_m2f = comparison(frozen["W_ge1_nontrivial"], frozen["nontrivial_trials"],
                             M2["W_ge1_nontrivial"], M2["nontrivial_trials"])
        cmp_m2f["outcome"] = outcome(cmp_m2f)
        cmp_m2f["note"] = "cross-anchor vs frozen r5 at asymmetric exposure; exposure-weighted p0"
        out["comparisons"]["frozen_r5_vs_M2"] = cmp_m2f
        out["M2_available"] = True
    except FileNotFoundError:
        out["M2_available"] = False

    out["decision_rule"] = {
        "source": "PREREGISTRATION.md section 5 (structural mirror of EV-AES-e4c091's Rank-1 rule and BATCH-014's OUTCOME-A'/B'/C' rule)",
        "OUTCOME_A_pp": "R_sub Garwood 95% CI contains 1 AND exact conditional-binomial test p < 0.01 (excess absent)",
        "OUTCOME_B_pp": "R_sub Garwood 95% CI lower bound > 1 AND test does not reject at p < 0.01 (excess reappears)",
        "OUTCOME_C_pp": "anything else (ambiguous)",
        "primary_result": out["comparisons"]["L1_vs_M1_matched_2p30"]["outcome"],
    }
    with open(f"{runs}/decision_analysis.json", "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out["self_checks"], indent=1))
    print("PRIMARY:", out["comparisons"]["L1_vs_M1_matched_2p30"])
    print("OUTCOME:", out["decision_rule"]["primary_result"])

if __name__ == "__main__":
    main()
