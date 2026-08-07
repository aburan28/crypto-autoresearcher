#!/usr/bin/env python3
"""TASK-20260803-48a239 -- SUPPLEMENTARY statistics.

Everything in this file is computed AFTER the preregistered tests T1-T5 and
CHANGES NONE OF THEM. Nothing here re-scores a completed run against an
adjusted prediction; these are descriptive sensitivity statements that make the
preregistered null result interpretable. They are labelled post_hoc in the
output and in RESULTS.json.
"""
import json
import math
import os

import stats_lib as S

D = os.path.dirname(os.path.abspath(__file__))
core = json.load(open(os.path.join(D, "results_core.json")))
i1 = core["item_1_deconfound"]
by = i1["per_sbox_counts_by_block"]
blocks = i1["completed_blocks"]
nblk = len(blocks)

out = {"post_hoc": True,
       "disclaimer": "Computed after the preregistered tests. Changes no preregistered test, adjusts no frozen prediction, and re-scores no completed run."}

# 1. within-S-box (key-to-key) heterogeneity, per S-box
within = {}
for t in ("AES", "R1", "R2"):
    c = [by[t][b] for b in blocks]
    g, df, p = S.g2_equal_exposure(c)
    within[t] = {"counts_by_block": dict(zip(blocks, c)), "G2": g, "df": df, "p_value": p,
                 "min": min(c), "max": max(c), "range": max(c) - min(c)}
out["within_sbox_key_to_key_heterogeneity"] = within
out["between_sbox_pooled_range"] = {
    "pooled": i1["pooled_by_sbox"],
    "range": max(i1["pooled_by_sbox"].values()) - min(i1["pooled_by_sbox"].values()),
    "note": "pooled counts sit at 3x the exposure of a single arm, so this range is NOT directly comparable to the within-S-box ranges above; the scaled comparison is in scaled_spread_comparison",
}
# scaled: express each as a coefficient of variation relative to Poisson expectation
out["scaled_spread_comparison"] = {}
for t in ("AES", "R1", "R2"):
    c = [by[t][b] for b in blocks]
    m = sum(c) / len(c)
    var = sum((x - m) ** 2 for x in c) / (len(c) - 1) if len(c) > 1 else None
    out["scaled_spread_comparison"]["within_" + t] = {
        "mean_per_arm": m, "sample_variance": var,
        "poisson_expected_variance_equals_mean": m,
        "index_of_dispersion_var_over_mean": (var / m) if (var is not None and m) else None}
pooled = [i1["pooled_by_sbox"][t] for t in ("AES", "R1", "R2")]
mp = sum(pooled) / 3
varp = sum((x - mp) ** 2 for x in pooled) / 2
out["scaled_spread_comparison"]["between_sbox_pooled"] = {
    "mean": mp, "sample_variance": varp,
    "poisson_expected_variance_equals_mean": mp,
    "index_of_dispersion_var_over_mean": varp / mp if mp else None}

# 2. POWER of T4 to detect the BATCH-004 R1:R2 ratio at this exposure.
#    Exact: enumerate Poisson(lam1) x Poisson(lam2) and sum the mass where the
#    conditional binomial two-sided p < 0.05.
def power_T4(lam1, lam2, alpha=0.05, cap=400):
    tot = 0.0
    for a in range(cap):
        pa = S.pois_pmf(a, lam1)
        if pa < 1e-18 and a > lam1:
            continue
        for b in range(cap):
            pb = S.pois_pmf(b, lam2)
            if pb < 1e-18 and b > lam2:
                continue
            n = a + b
            if n == 0:
                continue
            p = S.exact_binom_two_sided_half(a, n)
            if p is not None and p < alpha:
                tot += pa * pb
    return tot

# BATCH-004 rates per 2^30 trials: R1 11.0 hits, R2 20.5 hits
exposure_blocks = nblk
lam_R1 = 11.0 * exposure_blocks
lam_R2 = 20.5 * exposure_blocks
out["power_of_T4_at_this_exposure"] = {
    "what": "Probability that the preregistered T4 exact test would have rejected at alpha=0.05 IF the BATCH-004 R1 and R2 rates (11.0x and 20.5x per 2^30) were the true S-box-specific rates.",
    "assumed_lambda_R1_pooled": lam_R1,
    "assumed_lambda_R2_pooled": lam_R2,
    "assumed_rate_ratio": round(20.5 / 11.0, 4),
    "power": power_T4(lam_R1, lam_R2),
    "reading": "A high value means the null result is informative rather than merely underpowered. A low value would mean this design could not have seen the BATCH-004 difference either way, and the honest report would be inconclusive.",
}
# also: smallest rate ratio detectable with 80% power at this exposure
lo, hi = 1.0, 4.0
for _ in range(14):
    mid = (lo + hi) / 2
    base = 14.11  # observed pooled mean per 2^30 across all 9 arms
    pw = power_T4(base * exposure_blocks, base * mid * exposure_blocks)
    if pw < 0.80:
        lo = mid
    else:
        hi = mid
out["power_of_T4_at_this_exposure"]["rate_ratio_detectable_with_80pct_power"] = round((lo + hi) / 2, 3)
out["power_of_T4_at_this_exposure"]["baseline_rate_used_per_2p30"] = 14.11

# 3. Does each S-box's rate here differ from its BATCH-004 rate?
#    Exact conditional binomial with UNEQUAL exposure: BATCH-004 arm ran 2^31,
#    this task ran nblk * 2^30, so p = 2 / (2 + nblk) under equality of rate.
b4 = {"AES": 27, "R1": 22, "R2": 41}
cmp_rows = {}
for t in ("AES", "R1", "R2"):
    a = b4[t]
    b = i1["pooled_by_sbox"][t]
    n = a + b
    p0 = 2.0 / (2.0 + nblk)
    lo_t = sum(S.binom_pmf(k, n, p0) for k in range(0, a + 1))
    hi_t = sum(S.binom_pmf(k, n, p0) for k in range(a, n + 1))
    cmp_rows[t] = {
        "BATCH_004_hits_at_2p31": a, "BATCH_004_excess_factor": round(a / 2.0, 2),
        "this_task_hits_at_%dx2p30" % nblk: b,
        "this_task_excess_factor": round(b / float(nblk), 3),
        "exact_two_sided_p_rate_unchanged": min(1.0, 2 * min(lo_t, hi_t)),
        "note": "unequal exposure handled by the binomial success probability 2/(2+%d)" % nblk,
    }
out["per_sbox_rate_this_task_vs_BATCH_004"] = cmp_rows

# 4. Grand pooled rate here vs BATCH-004 grand pooled rate
a, b = 90, sum(i1["pooled_by_sbox"].values())
n = a + b
p0 = 6.0 / (6.0 + 3.0 * nblk)
lo_t = sum(S.binom_pmf(k, n, p0) for k in range(0, a + 1))
hi_t = sum(S.binom_pmf(k, n, p0) for k in range(a, n + 1))
out["grand_pooled_rate_vs_BATCH_004"] = {
    "BATCH_004_hits": a, "BATCH_004_exposure_trials": 3 * 2 ** 31,
    "BATCH_004_excess_factor": round(a / 6.0, 3),
    "this_task_hits": b, "this_task_exposure_trials": 3 * nblk * 2 ** 30,
    "this_task_excess_factor": round(b / (3.0 * nblk), 3),
    "exact_two_sided_p_rate_unchanged": min(1.0, 2 * min(lo_t, hi_t)),
}

json.dump(out, open(os.path.join(D, "results_extras.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
