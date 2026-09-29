#!/usr/bin/env python3
"""
EXP-MONO-715694: Census-convergence power analysis.

Pure Python 3 standard-library only (random, math, itertools, json,
collections, statistics, sys, time, os, resource, hashlib). No numpy,
scipy, sympy, or any external statistics package.

Usage:
    python3 run_experiment.py <seed> <output_dir> <repo_root>

Writes raw-result.json (summary) and a per_n_log/ directory with the full
search grid (N, threshold, power, se) for each pair, plus null-control and
step-4 detail, into <output_dir>.
"""
import sys
import os
import json
import math
import time
import random
import itertools
from collections import Counter

CYCLE_TYPES = ["identity", "transposition", "double_transposition", "three_cycle", "four_cycle"]
CT_INDEX = {c: i for i, c in enumerate(CYCLE_TYPES)}

ALPHA = 0.05
TARGET_POWER = 0.99
MC_TRIALS = 20000
SEARCH_CEILING_N = 100000
NEG_INF_CAP = -1.0e18  # used only for numerically summing "-inf" logs safely


def cycle_type_of_perm(perm):
    """Cycle-decompose a 4-tuple permutation of {0,1,2,3} by tracing orbits.
    Returns one of CYCLE_TYPES. Pure mechanical trace, no library."""
    n = len(perm)
    assert n == 4
    visited = [False] * n
    lengths = []
    for start in range(n):
        if visited[start]:
            continue
        length = 0
        j = start
        while not visited[j]:
            visited[j] = True
            j = perm[j]
            length += 1
        lengths.append(length)
    lengths.sort()
    if lengths == [1, 1, 1, 1]:
        return "identity"
    if lengths == [1, 1, 2]:
        return "transposition"
    if lengths == [2, 2]:
        return "double_transposition"
    if lengths == [1, 3]:
        return "three_cycle"
    if lengths == [4]:
        return "four_cycle"
    raise ValueError("Unexpected cycle-length partition for a 4-point permutation: %r" % (lengths,))


# ---------------------------------------------------------------------------
# Stage 0: exact enumeration of S_4 (24 perms) and A_4 (12 even perms)
# ---------------------------------------------------------------------------

def parity_of_perm(perm):
    """Number of transpositions mod 2, via inversion count (no library)."""
    n = len(perm)
    inversions = 0
    for i in range(n):
        for j in range(i + 1, n):
            if perm[i] > perm[j]:
                inversions += 1
    return inversions % 2


def stage0_exact_tables():
    s4_counts = Counter()
    a4_counts = Counter()
    s4_total = 0
    a4_total = 0
    for perm in itertools.permutations(range(4)):
        ct = cycle_type_of_perm(list(perm))
        s4_counts[ct] += 1
        s4_total += 1
        if parity_of_perm(perm) == 0:
            a4_counts[ct] += 1
            a4_total += 1
    s4_vec = [s4_counts[c] for c in CYCLE_TYPES]
    a4_vec = [a4_counts[c] for c in CYCLE_TYPES]
    assert s4_total == 24, "S_4 must have exactly 24 elements, got %d" % s4_total
    assert a4_total == 12, "A_4 must have exactly 12 elements, got %d" % a4_total
    expected_s4 = [1, 6, 3, 8, 6]
    expected_a4 = [1, 0, 3, 8, 0]
    if s4_vec != expected_s4:
        raise AssertionError("Stage 0 FAILED: S_4 vector %r != expected %r" % (s4_vec, expected_s4))
    if a4_vec != expected_a4:
        raise AssertionError("Stage 0 FAILED: A_4 vector %r != expected %r" % (a4_vec, expected_a4))
    s4_law = [c / 24.0 for c in s4_vec]
    a4_law = [c / 12.0 for c in a4_vec]
    return {
        "s4_counts": s4_vec,
        "a4_counts": a4_vec,
        "s4_total": s4_total,
        "a4_total": a4_total,
        "s4_law": s4_law,
        "a4_law": a4_law,
        "pass": True,
    }


# ---------------------------------------------------------------------------
# Stage 0b: D_4-from-real-data law
# ---------------------------------------------------------------------------

def stage0b_d4_law(path):
    counts = Counter()
    total_rows = 0
    excluded_null = 0
    three_cycles_found = 0
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            total_rows += 1
            rec = json.loads(line)
            if rec.get("class") is None:
                excluded_null += 1
                continue
            perm = rec["perm"]
            ct = cycle_type_of_perm(perm)
            if ct == "three_cycle":
                three_cycles_found += 1
            counts[ct] += 1
    non_ramified_total = sum(counts.values())
    vec = [counts[c] for c in CYCLE_TYPES]
    law = [c / non_ramified_total for c in vec]
    return {
        "total_rows": total_rows,
        "excluded_null": excluded_null,
        "non_ramified_total": non_ramified_total,
        "counts": vec,
        "law": law,
        "three_cycles_found": three_cycles_found,
    }


# ---------------------------------------------------------------------------
# N3 real-data reader (label field already in S_4 cycle-type notation)
# ---------------------------------------------------------------------------

LABEL_TO_CT = {
    "1^4": "identity",
    "2.1.1": "transposition",
    "2^2": "double_transposition",
    "3+1": "three_cycle",
    "4": "four_cycle",
}


def read_n3_histogram(path):
    counts = Counter()
    total_rows = 0
    discarded = 0
    used = 0
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            total_rows += 1
            rec = json.loads(line)
            if rec.get("discarded"):
                discarded += 1
                continue
            ct = LABEL_TO_CT[rec["label"]]
            counts[ct] += 1
            used += 1
    vec = [counts[c] for c in CYCLE_TYPES]
    return {
        "total_rows": total_rows,
        "discarded": discarded,
        "used": used,
        "counts": vec,
    }


def read_n1_full_histogram_as_data_points(path):
    """Return list of cycle types (one per non-ramified row), preserving order,
    for use as the bootstrap resampling population (Step 4a) and as the N1
    real-exhaustive-sample histogram (Step 4b sanity check)."""
    cts = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("class") is None:
                continue
            cts.append(cycle_type_of_perm(rec["perm"]))
    return cts


# ---------------------------------------------------------------------------
# LR statistic
# ---------------------------------------------------------------------------

def log_ratio_table(p_full, p_sub):
    """log(P_sub(c)/P_full(c)) for each cycle type index, handling P_sub==0.
    If P_sub(c) == 0 and P_full(c) > 0, use NEG_INF_CAP (a very large negative
    number standing in for -inf) rather than Python float('-inf') itself, so
    that summation and downstream percentile/sorting arithmetic never has to
    special-case a true -inf value. NEG_INF_CAP is chosen far more negative
    than any achievable finite sum of N<=100000 real log-ratio terms
    (|log ratio| for nonzero terms here is at most ~ln(24) ~ 3.2), so a single
    occurrence dominates any sum and is functionally an immediate, maximally
    confident vote for 'it's S_4' in that draw, exactly as the contract
    specifies."""
    table = []
    for i in range(len(p_full)):
        pf = p_full[i]
        ps = p_sub[i]
        if ps == 0.0:
            if pf == 0.0:
                table.append(0.0)  # both zero: cycle type impossible for both, no info
            else:
                table.append(NEG_INF_CAP)
        else:
            table.append(math.log(ps / pf))
    return table


def sample_cycle_type_index(cum_probs, rng):
    u = rng.random()
    for i, c in enumerate(cum_probs):
        if u <= c:
            return i
    return len(cum_probs) - 1


def cumulative(law):
    cum = []
    running = 0.0
    for p in law:
        running += p
        cum.append(running)
    cum[-1] = 1.0  # guard against float rounding
    return cum


def make_rng(*parts):
    """Deterministic seeded RNG from an arbitrary tuple of hashable parts.
    random.Random() only accepts None/int/float/str/bytes/bytearray as a
    seed, so tuple seed-tags are joined into a single reproducible string
    via repr() before seeding -- every source of randomness in this
    experiment is traceable to (base_seed, purpose_tag, N) via this
    function."""
    return random.Random(repr(parts))


def multinomial_counts(n, probs, rng):
    """Draw a count vector of length len(probs) from Multinomial(n, probs)
    WITHOUT drawing n individual categorical samples (which is O(n) per draw
    and infeasible in pure Python at n up to 100,000 with 20,000 Monte Carlo
    trials per candidate N -- ~1e10+ operations).

    Instead uses the standard equivalence: a Multinomial(n, p_1..p_k) count
    vector can be generated by sequential conditional binomial sampling --
    n_1 ~ Binomial(n, p_1); given n_1, n_2 ~ Binomial(n - n_1, p_2/(1-p_1));
    and so on. This is exact (not an approximation) and each step is O(1)
    (Python 3.12+ stdlib `random.Random.binomialvariate`), so drawing one
    length-N sample costs O(k)=O(5) regardless of N. This is a performance
    optimization only; it produces exactly the same distribution as drawing
    N i.i.d. categorical samples one at a time and tabulating them, which is
    the operation the frozen contract specifies."""
    k = len(probs)
    remaining_n = n
    remaining_p = 1.0
    counts = [0] * k
    for i in range(k - 1):
        p_i = probs[i]
        if remaining_n <= 0 or remaining_p <= 0.0:
            break
        cond_p = min(1.0, max(0.0, p_i / remaining_p))
        c_i = rng.binomialvariate(remaining_n, cond_p)
        counts[i] = c_i
        remaining_n -= c_i
        remaining_p -= p_i
    counts[k - 1] = remaining_n
    return counts


def lr_statistic_from_counts(counts_vec, log_ratio_tab):
    """Sum of log-ratio contributions given a count vector over the 5 cycle
    types (counts_vec[i] draws of type i). Any nonzero count at a NEG_INF_CAP
    index dominates and the sum is effectively NEG_INF_CAP (still finite for
    float arithmetic safety, but functionally -inf for thresholding)."""
    total = 0.0
    hit_neg_inf = False
    for i, n_i in enumerate(counts_vec):
        if n_i == 0:
            continue
        lr = log_ratio_tab[i]
        if lr <= NEG_INF_CAP:
            hit_neg_inf = True
        total += n_i * lr
    if hit_neg_inf:
        return NEG_INF_CAP
    return total


def draw_n_counts(probs, n, rng):
    """Draw one length-N i.i.d. categorical sample, tabulated as counts.
    Implemented via exact multinomial sampling (see multinomial_counts) for
    performance; `probs` here is the raw probability law, NOT a cumulative
    array (cumulative arrays are still used by classify/threshold code that
    is not on this hot path)."""
    return multinomial_counts(n, probs, rng)


def percentile(sorted_vals, q):
    """Empirical quantile via linear interpolation (no numpy)."""
    if not sorted_vals:
        raise ValueError("empty list")
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    idx = q * (len(sorted_vals) - 1)
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return sorted_vals[lo]
    frac = idx - lo
    return sorted_vals[lo] + frac * (sorted_vals[hi] - sorted_vals[lo])


def run_lr_trial_batch(probs, n, trials, rng, log_ratio_tab):
    """Draw `trials` independent length-N i.i.d. samples from the categorical
    law `probs` (exact multinomial sampling, see multinomial_counts) and
    return their LR statistics."""
    lr_values = []
    for _ in range(trials):
        counts = draw_n_counts(probs, n, rng)
        lr = lr_statistic_from_counts(counts, log_ratio_tab)
        lr_values.append(lr)
    return lr_values


def calibrate_and_measure_power(s4_law, sub_law, n, trials, rng_full, rng_sub):
    """At sample size n: draw `trials` S4 samples and `trials` sub samples,
    compute LR = sum log(P_sub/P_full) for each, calibrate a rejection
    threshold from the S4-generated LR distribution, and measure power as
    the fraction of sub-generated LR values that fall in the rejection
    region.

    DIRECTION-OF-REJECTION NOTE (protocol clarification, documented in full
    in implementation.md): with LR = sum log(P_sub(cycle_type)/P_full(cycle_type)),
    E[LR | data ~ P_full] = -D_KL(P_full || P_sub) and E[LR | data ~ P_sub] =
    +D_KL(P_sub || P_full) >= 0. Because P_sub is a proper subgroup's law
    (strictly narrower support than P_full for the A_4 and D_4 pairs tested
    here), D_KL(P_full || P_sub) is +infinity whenever P_sub assigns zero
    probability to a cycle type P_full does not -- so REAL S4 data drives LR
    to a large NEGATIVE value (exactly matching the handoff's own explicit
    instruction that a -infinity/NEG_INF_CAP LR is "an immediate, maximally
    confident vote for it's S_4"), while real SUB data drives LR to a
    positive finite value. The classification rule implemented here is
    therefore: LR > threshold => classify as "it's the subgroup"; LR <=
    threshold => classify as "it's S4". The threshold is calibrated as the
    empirical (1-alpha) quantile of the S4-generated LR distribution, so
    that P(S4 data classified as sub) ~= alpha. This is the internally
    consistent, Neyman-Pearson-standard direction (reject null for LARGE
    likelihood ratio of alternative/null); the handoff's separate prose
    aside describing "a lower/more-negative LR favors it's the subgroup" is
    inconsistent with its own NEG_INF_CAP worked example and with the stated
    LR formula's arithmetic, and is treated as a documentation slip rather
    than followed literally -- see implementation.md for the full
    derivation and disclosure of this judgment call."""
    log_ratio_tab = log_ratio_table(s4_law, sub_law)

    s4_lrs = run_lr_trial_batch(s4_law, n, trials, rng_full, log_ratio_tab)
    sub_lrs = run_lr_trial_batch(sub_law, n, trials, rng_sub, log_ratio_tab)

    s4_lrs_sorted = sorted(s4_lrs)
    threshold = percentile(s4_lrs_sorted, 1.0 - ALPHA)

    # empirical false-positive rate at this threshold: fraction of S4-generated
    # LR values that land in the "classify as sub" (upper) rejection region.
    fp_count = sum(1 for v in s4_lrs if v > threshold)
    fp_rate = fp_count / trials

    power_count = sum(1 for v in sub_lrs if v > threshold)
    power = power_count / trials
    se = math.sqrt(power * (1 - power) / trials) if trials > 0 else float("nan")

    return {
        "n": n,
        "threshold": threshold,
        "false_positive_rate": fp_rate,
        "power": power,
        "power_se": se,
    }


def doubling_bisection_search(s4_law, sub_law, trials, rng_full, rng_sub, ceiling, seed_tag):
    """Search N by doubling from 10 to ceiling, stop once power >= target,
    then bisect between last-failing and first-passing N to refine. Returns
    (n_required_or_None, full_grid_results)."""
    grid_results = []
    n = 10
    prev_n = None
    prev_result = None
    passing_n = None
    passing_result = None

    while True:
        rng_f = make_rng(seed_tag, "full", n)
        rng_s = make_rng(seed_tag, "sub", n)
        result = calibrate_and_measure_power(s4_law, sub_law, n, trials, rng_f, rng_s)
        grid_results.append(result)
        if result["power"] >= TARGET_POWER:
            passing_n = n
            passing_result = result
            break
        if n >= ceiling:
            break
        prev_n = n
        prev_result = result
        n = min(n * 2, ceiling)
        if n == prev_n:
            break

    if passing_n is None:
        return None, grid_results

    if prev_n is None:
        # even N=10 already passes; nothing to bisect
        return passing_n, grid_results

    lo, hi = prev_n, passing_n
    lo_result, hi_result = prev_result, passing_result
    # bisection: narrow the gap to within a small tolerance or until lo+1>=hi
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if mid == lo:
            break
        rng_f = make_rng(seed_tag, "full", mid)
        rng_s = make_rng(seed_tag, "sub", mid)
        mid_result = calibrate_and_measure_power(s4_law, sub_law, mid, trials, rng_f, rng_s)
        grid_results.append(mid_result)
        if mid_result["power"] >= TARGET_POWER:
            hi = mid
            hi_result = mid_result
        else:
            lo = mid
            lo_result = mid_result

    return hi, grid_results


# ---------------------------------------------------------------------------
# NULL controls
# ---------------------------------------------------------------------------

def null1_check(s4_law, trials, rng_full, rng_sub, n_values, seed_tag):
    """NULL-1: sub law == full law (S4 vs an independent second S4 stream)."""
    results = []
    for n in n_values:
        rng_f = make_rng(seed_tag, "null1full", n)
        rng_s = make_rng(seed_tag, "null1sub", n)
        r = calibrate_and_measure_power(s4_law, s4_law, n, trials, rng_f, rng_s)
        results.append(r)
    return results


def null2_check(s4_law, trials, n_values, seed_tag):
    """NULL-2: report empirical FP rate of the calibrated S4-vs-S4 test at
    specified N values (subset/overlap with NULL-1 is fine; reported
    separately per contract)."""
    results = []
    for n in n_values:
        rng_f = make_rng(seed_tag, "null2full", n)
        rng_s = make_rng(seed_tag, "null2sub", n)
        r = calibrate_and_measure_power(s4_law, s4_law, n, trials, rng_f, rng_s)
        results.append(r)
    return results


# ---------------------------------------------------------------------------
# Step 4a: bootstrap resampling from real N1 data
# ---------------------------------------------------------------------------

def bootstrap_power_curve(n1_data_points, s4_law, d4_law, n_values, n_bootstrap, seed_tag):
    """For each N in n_values, resample WITH REPLACEMENT n1_data_points at
    size N, `n_bootstrap` times, compute LR under the S4-vs-D4 statistic
    (using the SAME threshold calibrated in the synthetic Stage-2 search at
    that N -- passed in via thresholds dict), and report the fraction of
    bootstrap samples classified as 'sub' (D4) i.e. below threshold. This is
    the empirical power of the REAL data's own finite-sample behaviour."""
    raise NotImplementedError  # replaced by caller-specific version below


def bootstrap_power_curve_with_thresholds(n1_data_points, s4_law, d4_law, grid, n_bootstrap, seed_tag):
    """Step 4a: literal with-replacement resampling directly from the real
    n1_data_points pool (not from the derived d4_law), per the frozen
    contract's explicit instruction. Uses `random.Random.choices` (stdlib)
    for the resampling draw itself -- a fast batch equal-weight
    with-replacement sample, mathematically identical to n independent
    `rng.randrange(pool_size)` draws, just implemented in the stdlib's own
    optimized C loop rather than a manual per-element Python loop. This is
    a performance detail only: the sampling distribution over which pool
    indices are drawn is unchanged."""
    log_ratio_tab = log_ratio_table(s4_law, d4_law)
    results = []
    ct_index_pool = [CT_INDEX[ct] for ct in n1_data_points]
    for entry in grid:
        n = entry["n"]
        threshold = entry["threshold"]
        rng = make_rng(seed_tag, "bootstrap", n)
        below = 0
        lr_values = []
        for _ in range(n_bootstrap):
            sample_indices = rng.choices(ct_index_pool, k=n)
            counts = [0, 0, 0, 0, 0]
            for idx in sample_indices:
                counts[idx] += 1
            lr = lr_statistic_from_counts(counts, log_ratio_tab)
            lr_values.append(lr)
            if lr > threshold:
                below += 1
        power = below / n_bootstrap
        se = math.sqrt(power * (1 - power) / n_bootstrap)
        mean_lr = sum(v for v in lr_values if v > NEG_INF_CAP) / max(1, sum(1 for v in lr_values if v > NEG_INF_CAP))
        results.append({
            "n": n,
            "threshold_used": threshold,
            "bootstrap_power": power,
            "bootstrap_power_se": se,
            "n_bootstrap": n_bootstrap,
            "synthetic_power": entry["power"],
            "synthetic_power_se": entry["power_se"],
            "gap": power - entry["power"],
        })
    return results


# ---------------------------------------------------------------------------
# Step 4b: classify real N3 (S=2000) and N1 (exhaustive) samples
# ---------------------------------------------------------------------------

def classify_histogram(counts_vec, s4_law, sub_law, threshold):
    log_ratio_tab = log_ratio_table(s4_law, sub_law)
    lr = lr_statistic_from_counts(counts_vec, log_ratio_tab)
    classified_as_sub = lr > threshold
    return {"lr": lr, "threshold": threshold, "classified_as_sub": classified_as_sub}


# ---------------------------------------------------------------------------
# Chernoff-Stein sanity-check formula (KL divergence, recalled not fetched)
# ---------------------------------------------------------------------------

def kl_divergence(p_sub, p_full):
    """D_KL(P_sub || P_full) = sum P_sub(c) log(P_sub(c)/P_full(c)).
    Terms with P_sub(c)==0 contribute 0 (standard convention)."""
    total = 0.0
    for ps, pf in zip(p_sub, p_full):
        if ps == 0.0:
            continue
        total += ps * math.log(ps / pf)
    return total


def chernoff_stein_estimate(p_sub, p_full, alpha, beta):
    d_kl = kl_divergence(p_sub, p_full)
    if d_kl <= 0:
        return None
    return math.log(1.0 / (alpha * beta)) / d_kl


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) != 4:
        print("usage: run_experiment.py <seed> <output_dir> <repo_root>", file=sys.stderr)
        sys.exit(2)

    seed = int(sys.argv[1])
    output_dir = sys.argv[2]
    repo_root = sys.argv[3]

    os.makedirs(output_dir, exist_ok=True)
    per_n_dir = os.path.join(output_dir, "per_n_log")
    os.makedirs(per_n_dir, exist_ok=True)

    t_start = time.time()

    n1_run1 = os.path.join(repo_root, "experiments/EXP-MONO-a20e48/runs/RUN-MONO-a20e48-1/per_base_point_log/N1_k1_exhaustive.jsonl")
    n1_run2 = os.path.join(repo_root, "experiments/EXP-MONO-a20e48/runs/RUN-MONO-a20e48-2/per_base_point_log/N1_k1_exhaustive.jsonl")
    n3_run1 = os.path.join(repo_root, "experiments/EXP-MONO-a20e48/runs/RUN-MONO-a20e48-1/per_base_point_log/N3_k1.jsonl")
    n3_run2 = os.path.join(repo_root, "experiments/EXP-MONO-a20e48/runs/RUN-MONO-a20e48-2/per_base_point_log/N3_k1.jsonl")

    result = {"seed": seed}

    # ---------------- Stage 0 ----------------
    stage0 = stage0_exact_tables()
    result["stage0"] = stage0
    print("STAGE 0: S4 vec=%r A4 vec=%r -> PASS" % (stage0["s4_counts"], stage0["a4_counts"]))

    s4_law = stage0["s4_law"]
    a4_law = stage0["a4_law"]

    # ---------------- Stage 0b ----------------
    d4_run1 = stage0b_d4_law(n1_run1)
    d4_run2 = stage0b_d4_law(n1_run2)
    result["stage0b"] = {"run1": d4_run1, "run2": d4_run2}

    if d4_run1["three_cycles_found"] != 0 or d4_run2["three_cycles_found"] != 0:
        raise AssertionError(
            "STAGE 0B GATE FAILED: 3-cycle found in real D_4 data (run1=%d, run2=%d) -- "
            "this contradicts D_4 group theory and must be escalated, not silently handled."
            % (d4_run1["three_cycles_found"], d4_run2["three_cycles_found"])
        )
    if d4_run1["non_ramified_total"] != 44310 or d4_run2["non_ramified_total"] != 44310:
        raise AssertionError(
            "STAGE 0B GATE FAILED: expected 44310 non-ramified rows per run, got run1=%d run2=%d"
            % (d4_run1["non_ramified_total"], d4_run2["non_ramified_total"])
        )
    if d4_run1["counts"] != d4_run2["counts"]:
        raise AssertionError(
            "STAGE 0B GATE FAILED: run1 and run2 derived D_4 laws disagree: %r vs %r"
            % (d4_run1["counts"], d4_run2["counts"])
        )
    print("STAGE 0B: D_4-from-real-data counts=%r (both runs agree, zero 3-cycles) -> PASS" % (d4_run1["counts"],))

    d4_law = d4_run1["law"]

    # ---------------- Stage 1: NULL controls ----------------
    null1_n_values = [10, 100, 1000, 10000, 44310, 100000]
    null1_results = null1_check(s4_law, MC_TRIALS, None, None, null1_n_values, seed)
    result["null1"] = null1_results

    null2_n_values = [100, 1000, 10000, 44310]
    null2_results = null2_check(s4_law, MC_TRIALS, null2_n_values, seed)
    result["null2"] = null2_results

    print("STAGE 1: NULL-1 fp rates=%r" % [r["false_positive_rate"] for r in null1_results])
    print("STAGE 1: NULL-2 fp rates=%r" % [r["false_positive_rate"] for r in null2_results])

    # ---------------- Stage 2: N_required search ----------------
    n_req_a4, grid_a4 = doubling_bisection_search(
        s4_law, a4_law, MC_TRIALS, None, None, SEARCH_CEILING_N, (seed, "s4_vs_a4")
    )
    n_req_d4, grid_d4 = doubling_bisection_search(
        s4_law, d4_law, MC_TRIALS, None, None, SEARCH_CEILING_N, (seed, "s4_vs_d4")
    )

    def last_result_for_n(grid, n):
        for r in reversed(grid):
            if r["n"] == n:
                return r
        return None

    n_req_a4_result = last_result_for_n(grid_a4, n_req_a4) if n_req_a4 else None
    n_req_d4_result = last_result_for_n(grid_d4, n_req_d4) if n_req_d4 else None

    result["stage2"] = {
        "s4_vs_a4": {
            "n_required": n_req_a4,
            "n_required_power": n_req_a4_result["power"] if n_req_a4_result else None,
            "n_required_power_se": n_req_a4_result["power_se"] if n_req_a4_result else None,
            "grid": grid_a4,
            "chernoff_stein_estimate": chernoff_stein_estimate(a4_law, s4_law, ALPHA, 1 - TARGET_POWER),
        },
        "s4_vs_d4": {
            "n_required": n_req_d4,
            "n_required_power": n_req_d4_result["power"] if n_req_d4_result else None,
            "n_required_power_se": n_req_d4_result["power_se"] if n_req_d4_result else None,
            "grid": grid_d4,
            "chernoff_stein_estimate": chernoff_stein_estimate(d4_law, s4_law, ALPHA, 1 - TARGET_POWER),
        },
        "ordering_prediction_check": {
            "n_required_d4_gt_a4": (n_req_d4 is not None and n_req_a4 is not None and n_req_d4 > n_req_a4)
        },
    }
    print("STAGE 2: N_required(S4 vs A4)=%r  N_required(S4 vs D4)=%r" % (n_req_a4, n_req_d4))

    with open(os.path.join(per_n_dir, "s4_vs_a4_grid.json"), "w") as f:
        json.dump(grid_a4, f, indent=2)
    with open(os.path.join(per_n_dir, "s4_vs_d4_grid.json"), "w") as f:
        json.dump(grid_d4, f, indent=2)

    # ---------------- Stage 3 / Step 4a: bootstrap vs simulation ----------------
    n1_data_points_run1 = read_n1_full_histogram_as_data_points(n1_run1)
    n1_data_points_run2 = read_n1_full_histogram_as_data_points(n1_run2)

    # grid points to bootstrap: those in grid_d4 that are <= population size (44310)
    # (contract says "at every N in your Stage-2 search grid for the S4_vs_D4 pair";
    # we bootstrap at every distinct N tested in that search, regardless of whether
    # N exceeds 44310, since bootstrap resampling WITH REPLACEMENT is valid for any N)
    distinct_grid_d4 = {}
    for r in grid_d4:
        distinct_grid_d4[r["n"]] = r
    grid_d4_dedup = sorted(distinct_grid_d4.values(), key=lambda r: r["n"])

    bootstrap_results = bootstrap_power_curve_with_thresholds(
        n1_data_points_run1, s4_law, d4_law, grid_d4_dedup, 1000, seed
    )
    result["step4a_bootstrap_vs_simulation"] = bootstrap_results

    with open(os.path.join(per_n_dir, "step4a_bootstrap_vs_simulation.json"), "w") as f:
        json.dump(bootstrap_results, f, indent=2)

    max_gap = max(abs(r["gap"]) for r in bootstrap_results) if bootstrap_results else None
    print("STEP 4A: max |bootstrap_power - synthetic_power| = %r" % max_gap)

    # ---------------- Step 4b: real-data classification ----------------
    # Determine (or recalibrate) the threshold at N=2000 for both pairs.
    def threshold_at_n(grid, n, s4_law_local, sub_law_local, seed_tag):
        for r in grid:
            if r["n"] == n:
                return r["threshold"], False  # found in existing grid, not recalibrated
        # not present: recalibrate exactly at N=2000
        rng_f = make_rng(seed_tag, "full", n)
        rng_s = make_rng(seed_tag, "sub", n)
        rr = calibrate_and_measure_power(s4_law_local, sub_law_local, n, MC_TRIALS, rng_f, rng_s)
        return rr["threshold"], True

    thr_a4_2000, recal_a4 = threshold_at_n(grid_a4, 2000, s4_law, a4_law, (seed, "s4_vs_a4"))
    thr_d4_2000, recal_d4 = threshold_at_n(grid_d4, 2000, s4_law, d4_law, (seed, "s4_vs_d4"))

    n3_hist_run1 = read_n3_histogram(n3_run1)
    n3_hist_run2 = read_n3_histogram(n3_run2)

    n3_run1_vs_a4 = classify_histogram(n3_hist_run1["counts"], s4_law, a4_law, thr_a4_2000)
    n3_run1_vs_d4 = classify_histogram(n3_hist_run1["counts"], s4_law, d4_law, thr_d4_2000)
    n3_run2_vs_a4 = classify_histogram(n3_hist_run2["counts"], s4_law, a4_law, thr_a4_2000)
    n3_run2_vs_d4 = classify_histogram(n3_hist_run2["counts"], s4_law, d4_law, thr_d4_2000)

    # N1 exhaustive sanity check: classify at N=44310 using the grid's threshold at that N
    # (or nearest grid point / recalibrate exactly at 44310)
    thr_a4_44310, recal_a4_44310 = threshold_at_n(grid_a4, 44310, s4_law, a4_law, (seed, "s4_vs_a4"))
    thr_d4_44310, recal_d4_44310 = threshold_at_n(grid_d4, 44310, s4_law, d4_law, (seed, "s4_vs_d4"))

    n1_hist_run1 = [0, 0, 0, 0, 0]
    for ct in n1_data_points_run1:
        n1_hist_run1[CT_INDEX[ct]] += 1
    n1_hist_run2 = [0, 0, 0, 0, 0]
    for ct in n1_data_points_run2:
        n1_hist_run2[CT_INDEX[ct]] += 1

    n1_run1_vs_a4 = classify_histogram(n1_hist_run1, s4_law, a4_law, thr_a4_44310)
    n1_run1_vs_d4 = classify_histogram(n1_hist_run1, s4_law, d4_law, thr_d4_44310)
    n1_run2_vs_a4 = classify_histogram(n1_hist_run2, s4_law, a4_law, thr_a4_44310)
    n1_run2_vs_d4 = classify_histogram(n1_hist_run2, s4_law, d4_law, thr_d4_44310)

    result["step4b"] = {
        "threshold_source": {
            "a4_at_n2000": {"threshold": thr_a4_2000, "recalibrated": recal_a4},
            "d4_at_n2000": {"threshold": thr_d4_2000, "recalibrated": recal_d4},
            "a4_at_n44310": {"threshold": thr_a4_44310, "recalibrated": recal_a4_44310},
            "d4_at_n44310": {"threshold": thr_d4_44310, "recalibrated": recal_d4_44310},
        },
        "n3_run1": {
            "histogram": n3_hist_run1,
            "vs_a4": n3_run1_vs_a4,
            "vs_d4": n3_run1_vs_d4,
        },
        "n3_run2": {
            "histogram": n3_hist_run2,
            "vs_a4": n3_run2_vs_a4,
            "vs_d4": n3_run2_vs_d4,
        },
        "n1_run1": {
            "histogram": n1_hist_run1,
            "vs_a4": n1_run1_vs_a4,
            "vs_d4": n1_run1_vs_d4,
        },
        "n1_run2": {
            "histogram": n1_hist_run2,
            "vs_a4": n1_run2_vs_a4,
            "vs_d4": n1_run2_vs_d4,
        },
    }

    print("STEP 4B: N3 run1 vs A4 classified_as_sub=%r vs D4 classified_as_sub=%r"
          % (n3_run1_vs_a4["classified_as_sub"], n3_run1_vs_d4["classified_as_sub"]))
    print("STEP 4B: N3 run2 vs A4 classified_as_sub=%r vs D4 classified_as_sub=%r"
          % (n3_run2_vs_a4["classified_as_sub"], n3_run2_vs_d4["classified_as_sub"]))
    print("STEP 4B: N1 run1 vs A4 classified_as_sub=%r vs D4 classified_as_sub=%r"
          % (n1_run1_vs_a4["classified_as_sub"], n1_run1_vs_d4["classified_as_sub"]))
    print("STEP 4B: N1 run2 vs A4 classified_as_sub=%r vs D4 classified_as_sub=%r"
          % (n1_run2_vs_a4["classified_as_sub"], n1_run2_vs_d4["classified_as_sub"]))

    t_end = time.time()
    result["wall_seconds"] = t_end - t_start

    with open(os.path.join(output_dir, "raw-result.json"), "w") as f:
        json.dump(result, f, indent=2)

    print("TOTAL WALL SECONDS: %.2f" % (t_end - t_start))


if __name__ == "__main__":
    main()
