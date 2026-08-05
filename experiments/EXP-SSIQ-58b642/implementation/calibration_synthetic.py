#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXP-SSIQ-58b642 -- PHASE 0 / C-CAL-GAP: calibration of the M-GAP pipeline on
synthetic hitting-time pairs with KNOWN true exponents, before any real
graph is built or any real data is fetched.

Implements experiments/EXP-SSIQ-58b642/specification.yaml
controls.C-CAL-GAP EXACTLY as frozen:

  (i)  CONSTANT-OFFSET variant: h_random(N) = N^0.5 + c,
       h_greedy(N)  = N^0.25 + c, for at least two values of c.
  (ii) SATURATING/CAPPED variant: h_greedy_capped(N) = min(N^0.25, D(N)),
       against the same h_random(N) = N^0.5.

Both variants are PURE SYNTHETIC ARITHMETIC -- no field theory, no graph
construction, no fetch -- but they exercise the EXACT SAME estimator code
as the real pipeline: ols_loglog_fit and population_median_with_sentinel
are IMPORTED from descent_hitting_time.py, not reimplemented, which is
what makes this a calibration of the actual pipeline rather than a
parallel implementation that could silently diverge.

N-WINDOW: the 12 pre-registered primes' graph sizes N = floor(p/12),
pinned in PRIMES_N below (same values used in Phase 1), so the window
shape matches selection_rule_pf3_corrected_and_pf5_narrowed exactly.

RECOVERY TOLERANCE: +-0.10 of the true gap (0.25 in both illustrative
cases), per synthetic pair, independently.  ALL synthetic pairs must pass
for C-CAL-GAP to pass overall (controls.C-CAL-GAP.failure_consequence: "IF
EITHER SYNTHETIC PAIR'S RECOVERED M-GAP FALLS OUTSIDE +-0.10 ... STOP").

WHY EACH SYNTHETIC POPULATION EXERCISES population_median_with_sentinel
FOR REAL (not just the deterministic formula):
Rather than plugging h(N) directly into the OLS fit (which would test only
the OLS step), each N gets a synthetic POPULATION of "per-vertex" hitting
times (an Exponential distribution whose analytic median equals h(N)),
and the pipeline's own median-with-sentinel function computes the
population median from that finite sample -- exercising real sampling
noise and, for variant (ii), REAL right-censoring: samples exceeding D(N)
are replaced by the sentinel D(N) exactly as a trapped greedy start would
be, and trapped_fraction(N) is computed and reported, so this gate also
demonstrates whether a trapped_fraction that grows with N (PF-2's
artifact signature) corrupts the recovered gap within the actual
pre-registered N-window, not just whether the algebraic minimum formula
would recover it.
"""

import math
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from descent_hitting_time import ols_loglog_fit, population_median_with_sentinel  # noqa: E402

PRIMES_N = [203, 324, 478, 611, 741, 888, 1045, 1199, 1349, 1504, 1643, 1800]
TRUE_GAP = 0.25
TOLERANCE = 0.10
POPULATION_SIZE = 2000
CALIBRATION_SEED = 20260805


def exponential_with_median(rng, median, n):
    """n iid samples of an Exponential distribution with EXACT analytic
    median = `median` (rate = ln2 / median): X = -median * ln(U) / ln(2),
    U ~ Uniform(0,1).  Right-skewed (heavy tail), a deliberately non-trivial
    noise model so the population median is not simply "the formula value
    plus symmetric jitter"."""
    ln2 = math.log(2.0)
    out = []
    for _ in range(n):
        u = rng.random()
        while u <= 0.0:
            u = rng.random()
        out.append(-median * math.log(u) / ln2)
    return out


def diameter_like_cap(N):
    """D(N): the synthetic stand-in for M-GAMMA-GREEDY.pf2_censoring_rule's
    sentinel (the graph's own BFS-computed diameter).  A 3-regular graph's
    BFS tree from a root has branching factor ~2 after the first step (each
    non-root vertex has 2 new neighbours, having arrived via the third), so
    diameter is standardly O(log N) with base ~2; D(N) = ceil(log2(N)) + 2
    is used here as a documented, stated estimate (not fitted to make this
    gate pass or fail either way) -- consistent with
    inputs.graph_construction.method's non-backtracking branching-factor-2
    structure."""
    return math.ceil(math.log2(N)) + 2


def calibrate_offset_variant(c, rng):
    """h_random(N) = N^0.5 + c, h_greedy(N) = N^0.25 + c.  No censoring."""
    N_med_random = []
    N_med_greedy = []
    per_N = []
    for N in PRIMES_N:
        target_random = N ** 0.5 + c
        target_greedy = N ** 0.25 + c
        raw_r = exponential_with_median(rng, target_random, POPULATION_SIZE)
        raw_g = exponential_with_median(rng, target_greedy, POPULATION_SIZE)
        med_r, tf_r = population_median_with_sentinel(
            raw_r, [False] * POPULATION_SIZE, target_random)
        med_g, tf_g = population_median_with_sentinel(
            raw_g, [False] * POPULATION_SIZE, target_greedy)
        N_med_random.append(med_r)
        N_med_greedy.append(med_g)
        per_N.append({
            "N": N, "target_random": target_random, "target_greedy": target_greedy,
            "sampled_median_random": med_r, "sampled_median_greedy": med_g,
            "trapped_fraction_random": tf_r, "trapped_fraction_greedy": tf_g,
        })
    fit_random = ols_loglog_fit(PRIMES_N, N_med_random)
    fit_greedy = ols_loglog_fit(PRIMES_N, N_med_greedy)
    m_gap = fit_random["gamma"] - fit_greedy["gamma"]
    recovered_ok = abs(m_gap - TRUE_GAP) <= TOLERANCE
    return {
        "variant": "constant_offset", "c": c,
        "gamma_random_fit": fit_random["gamma"], "se_gamma_random": fit_random["se_gamma"],
        "gamma_greedy_fit": fit_greedy["gamma"], "se_gamma_greedy": fit_greedy["se_gamma"],
        "m_gap_recovered": m_gap, "true_gap": TRUE_GAP,
        "abs_error": abs(m_gap - TRUE_GAP), "tolerance": TOLERANCE,
        "pass": bool(recovered_ok),
        "per_N": per_N,
        "r_squared_random": fit_random["r_squared"], "r_squared_greedy": fit_greedy["r_squared"],
    }


def calibrate_capped_variant(rng):
    """h_random(N) = N^0.5 (no offset).
    h_greedy_capped(N) = min(N^0.25, D(N)): the UNCAPPED nominal median is
    N^0.25; individual samples exceeding D(N) are capped to the sentinel
    D(N) (a right-censoring exactly matching M-GAMMA-GREEDY's trapped-start
    sentinel convention), and trapped_fraction(N) is the fraction of the
    population so capped."""
    N_med_random = []
    N_med_greedy_capped = []
    per_N = []
    for N in PRIMES_N:
        target_random = N ** 0.5
        target_greedy_uncapped = N ** 0.25
        D_N = diameter_like_cap(N)
        raw_r = exponential_with_median(rng, target_random, POPULATION_SIZE)
        raw_g = exponential_with_median(rng, target_greedy_uncapped, POPULATION_SIZE)
        trapped_mask_g = [x > D_N for x in raw_g]
        med_r, tf_r = population_median_with_sentinel(
            raw_r, [False] * POPULATION_SIZE, target_random)
        med_g, tf_g = population_median_with_sentinel(raw_g, trapped_mask_g, D_N)
        N_med_random.append(med_r)
        N_med_greedy_capped.append(med_g)
        per_N.append({
            "N": N, "target_random": target_random,
            "target_greedy_uncapped": target_greedy_uncapped, "D_N": D_N,
            "sampled_median_random": med_r,
            "sampled_median_greedy_capped": med_g,
            "trapped_fraction_greedy": tf_g,
            "formula_min_N025_DN": min(target_greedy_uncapped, D_N),
        })
    fit_random = ols_loglog_fit(PRIMES_N, N_med_random)
    fit_greedy = ols_loglog_fit(PRIMES_N, N_med_greedy_capped)
    m_gap = fit_random["gamma"] - fit_greedy["gamma"]
    recovered_ok = abs(m_gap - TRUE_GAP) <= TOLERANCE
    trapped_fracs = [row["trapped_fraction_greedy"] for row in per_N]
    trapped_grows_with_N = all(
        trapped_fracs[i] <= trapped_fracs[i + 1] + 1e-9
        for i in range(len(trapped_fracs) - 1)) and trapped_fracs[-1] > trapped_fracs[0]
    return {
        "variant": "saturating_capped",
        "gamma_random_fit": fit_random["gamma"], "se_gamma_random": fit_random["se_gamma"],
        "gamma_greedy_fit": fit_greedy["gamma"], "se_gamma_greedy": fit_greedy["se_gamma"],
        "m_gap_recovered": m_gap, "true_gap": TRUE_GAP,
        "abs_error": abs(m_gap - TRUE_GAP), "tolerance": TOLERANCE,
        "pass": bool(recovered_ok),
        "per_N": per_N,
        "trapped_fraction_by_N": trapped_fracs,
        "trapped_fraction_grows_with_N": bool(trapped_grows_with_N),
        "pf2_artifact_signature_flag": bool(trapped_grows_with_N and recovered_ok),
        "r_squared_random": fit_random["r_squared"], "r_squared_greedy": fit_greedy["r_squared"],
    }


def run_calibration(seed=CALIBRATION_SEED):
    rng = random.Random(seed)
    results = []
    results.append(calibrate_offset_variant(1, rng))
    smallest_N_diam = diameter_like_cap(PRIMES_N[0])
    results.append(calibrate_offset_variant(smallest_N_diam, rng))
    results.append(calibrate_capped_variant(rng))
    overall_pass = all(r["pass"] for r in results)
    return {
        "seed": seed,
        "N_window": PRIMES_N,
        "population_size": POPULATION_SIZE,
        "true_gap": TRUE_GAP,
        "tolerance": TOLERANCE,
        "synthetic_pairs": results,
        "overall_pass": bool(overall_pass),
        "smallest_N_diameter_like_c": smallest_N_diam,
    }


def main():
    import json
    result = run_calibration()
    print(json.dumps(result, indent=1))
    print("C-CAL-GAP overall_pass:", result["overall_pass"])
    for r in result["synthetic_pairs"]:
        label = r["variant"] + (("(c=%s)" % r["c"]) if "c" in r else "")
        print(" %-30s m_gap=%.6f abs_error=%.6f pass=%s"
              % (label, r["m_gap_recovered"], r["abs_error"], r["pass"]))
    return 0 if result["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
