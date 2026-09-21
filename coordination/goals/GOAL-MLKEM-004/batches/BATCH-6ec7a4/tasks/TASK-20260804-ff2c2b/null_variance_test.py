#!/usr/bin/env python3
"""
null_variance_test.py  — TASK-20260804-ff2c2b / BATCH-6ec7a4 / GOAL-MLKEM-004
Batch 4 of 6 — decisive null control and outlier seed re-run.

TEST A — NULL CONTROL (decisive for OBJ-QEMU):
  Same LWE instance (instance_seed=20260803001, fpylll_seed=20260803005).
  Wrong secret s_wrong generated from numpy.random.default_rng(20260804999).
  50 bgj1_sieve realizations with seeds:
      numpy.random.default_rng(20260804002).integers(0, 2**32, size=50).tolist()
  For each run compute T_N_null = sum cos(2π · center_mod(x·b - y·s_wrong, q) / q).
  Since s_wrong ≠ s: phase = x·(As+e) - y·s_wrong = x·e + y·(s-s_wrong) ≠ x·e.
  Baseline: single_score_var_null from run-0 null scores.
  variance_ratio_null = Var[T_N_null] / (N0 * single_score_var_null).
  chi2_null = (n-1) * Var[T_N_null] / (N0 * single_score_var_null).

TEST B — OUTLIER SEED RE-RUN:
  Same LWE instance.
  4 seeds: [2941775225, 26883012, 2418421570, 1873347320].
  For CORRECT secret: T_N_correct (batch-3 reproduction).
  For WRONG secret s_wrong: T_N_wrong.

states_a_finding: false
compared_against_matzov_nf: false
rule12_status: UNMET and UNWAIVED
"""

import argparse
import json
import os
import platform
import resource
import sys
import time

import numpy as np
import scipy.stats

from fpylll import IntegerMatrix, LLL, FPLLL
from g6k import Siever, SieverParams

SCRIPT_VERSION = "1.0.0"
TASK = "TASK-20260804-ff2c2b"
BATCH = "BATCH-6ec7a4"
GOAL = "GOAL-MLKEM-004"

# ---- Frozen LWE parameters (identical to batch-3)
M, N_LWE, Q = 35, 25, 127
D = M + N_LWE          # lattice dimension = 60
ETA = 2
SIGMA = 2.0
INSTANCE_SEED = 20260803001
FPYLLL_SEED   = 20260803005
SIEVE_ALGO    = "bgj1_sieve"
SIEVE_THREADS = 1
TARGET_N      = 17919

# ---- Pre-registered expressions (verbatim)
NULL_SEEDS_EXPRESSION  = "numpy.random.default_rng(20260804002).integers(0, 2**32, size=50).tolist()"
WRONG_SECRET_SEED      = 20260804999

# Outlier seeds from batch-3 (3 high-T_N seeds + run-0 seed)
OUTLIER_SEEDS = [2941775225, 26883012, 2418421570, 1873347320]

# Batch-3 T_N values at these seeds (for consistency comparison)
BATCH3_OUTLIER_TN = {
    2941775225: 7789.567405817314,
    26883012:   7791.775311646041,
    2418421570: 7789.812131511126,
    1873347320: 7420.548667265,       # run-0, not an outlier — baseline
}


# ---- RNG utilities
def centered_binomial(rng, eta, size):
    a = rng.integers(0, 2, size=(size, eta), dtype=np.int64).sum(axis=1)
    b = rng.integers(0, 2, size=(size, eta), dtype=np.int64).sum(axis=1)
    return (a - b).astype(np.int64)


def rounded_gaussian(rng, sigma, size):
    return np.rint(rng.normal(0.0, sigma, size=size)).astype(np.int64)


def center_mod(v, q):
    r = np.mod(v, q)
    r = np.where(r > q // 2, r - q, r)
    return r.astype(np.int64)


# ---- Lattice utilities
def build_dual_basis(A, q, m, n):
    d = m + n
    B = np.zeros((d, d), dtype=np.int64)
    B[:m, :m] = np.eye(m, dtype=np.int64)
    B[:m, m:] = A
    B[m:, m:] = q * np.eye(n, dtype=np.int64)
    return B


def to_intmat(M_np):
    A = IntegerMatrix(M_np.shape[0], M_np.shape[1])
    for i in range(M_np.shape[0]):
        for j in range(M_np.shape[1]):
            A[i, j] = int(M_np[i, j])
    return A


def from_intmat(A):
    return np.array([[A[i, j] for j in range(A.ncols)] for i in range(A.nrows)],
                    dtype=np.int64)


def build_instance_and_lll():
    """Build LWE instance + LLL-reduced basis; returns (A, s, e, b, Bred_fp)."""
    rng = np.random.default_rng(INSTANCE_SEED)
    A = rng.integers(0, Q, size=(M, N_LWE), dtype=np.int64)
    s = centered_binomial(rng, ETA, N_LWE)
    e = rounded_gaussian(rng, SIGMA, M)
    b = np.mod(A.dot(s) + e, Q)

    Bnp = build_dual_basis(A, Q, M, N_LWE)
    Bfp = to_intmat(Bnp)
    FPLLL.set_random_seed(FPYLLL_SEED)
    Bred_fp = LLL.reduction(Bfp)
    return A, s, e, b, Bred_fp


def generate_wrong_secret(s_correct):
    """Generate s_wrong using wrong_secret_seed; verify s_wrong != s_correct."""
    rng_w = np.random.default_rng(WRONG_SECRET_SEED)
    s_wrong = centered_binomial(rng_w, ETA, N_LWE)
    equal = np.array_equal(s_wrong, s_correct)
    if equal:
        raise RuntimeError("s_wrong == s_correct (probability 1/|S|^n, effectively impossible)")
    return s_wrong


def run_single_sieve(Bred_fp, siever_seed):
    """Run bgj1_sieve with given seed. Returns (coeffs, Bused, N, t_sieve)."""
    g = Siever(Bred_fp, SieverParams(threads=SIEVE_THREADS), seed=siever_seed)
    g.initialize_local(0, 0, D)
    t0 = time.time()
    g.bgj1_sieve()
    t_sieve = time.time() - t0
    coeffs = np.array([tuple(v) for v in g.itervalues()], dtype=np.int64)
    Bused = from_intmat(g.M.B)
    return coeffs, Bused, coeffs.shape[0], t_sieve


def compute_TN_secret(coeffs, Bused, b, s_candidate, q, m, n):
    """Compute T_N = sum of cosine scores for a given secret candidate.
    Also returns the per-vector score array."""
    V = coeffs.dot(Bused)   # N x d
    X = V[:, :m]            # N x m
    Y = V[:, m:]            # N x n
    phases = center_mod(X.dot(b) - Y.dot(s_candidate), q)
    scores = np.cos(2.0 * np.pi * phases / q)
    T_N = float(scores.sum())
    return T_N, int(V.shape[0]), scores


def chi2_test(TN_values, predicted_var_per_sample, n_completed):
    """Return variance_ratio, chi2_stat, p_value, CI for variance."""
    arr = np.array(TN_values, dtype=np.float64)
    empirical_var = float(np.var(arr, ddof=1))
    df = n_completed - 1
    chi2_stat = df * empirical_var / predicted_var_per_sample
    p_value = float(1.0 - scipy.stats.chi2.cdf(chi2_stat, df=df))
    variance_ratio = empirical_var / predicted_var_per_sample
    ci_lower = empirical_var * df / scipy.stats.chi2.ppf(0.975, df)
    ci_upper = empirical_var * df / scipy.stats.chi2.ppf(0.025, df)
    variance_ratio_ci = [ci_lower / predicted_var_per_sample,
                         ci_upper / predicted_var_per_sample]
    return {
        "empirical_var": empirical_var,
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr, ddof=1)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "predicted_var": predicted_var_per_sample,
        "variance_ratio": variance_ratio,
        "chi2_stat": chi2_stat,
        "chi2_df": df,
        "p_value": p_value,
        "ci_lower_var": ci_lower,
        "ci_upper_var": ci_upper,
        "variance_ratio_95ci": variance_ratio_ci,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--repo-root", default=None)
    ap.add_argument("--mem-cap-gb", type=float, default=7.0)
    args = ap.parse_args()

    t_start = time.time()

    if args.mem_cap_gb > 0:
        cap = int(args.mem_cap_gb * (1 << 30))
        resource.setrlimit(resource.RLIMIT_AS, (cap, cap))

    log = []

    def say(msg):
        line = "[%7.1fs] %s" % (time.time() - t_start, msg)
        print(line, flush=True)
        log.append(line)

    say("null_variance_test.py %s: TEST A (50 null runs) + TEST B (4 outlier seeds)" % SCRIPT_VERSION)
    say("TASK=%s BATCH=%s GOAL=%s" % (TASK, BATCH, GOAL))
    say("instance_seed=%d fpylll_seed=%d" % (INSTANCE_SEED, FPYLLL_SEED))
    say("null_seeds_expression: %s" % NULL_SEEDS_EXPRESSION)
    say("wrong_secret_seed=%d" % WRONG_SECRET_SEED)
    say("outlier_seeds=%s" % OUTLIER_SEEDS)
    say("platform: %s" % platform.platform())

    # -----------------------------------------------------------------------
    # Build LWE instance ONCE
    # -----------------------------------------------------------------------
    A, s_correct, e, b, Bred_fp = build_instance_and_lll()
    say("instance built: |s|_inf=%d |e|_inf=%d" % (
        int(np.abs(s_correct).max()), int(np.abs(e).max())))

    # Generate wrong secret and verify it differs
    s_wrong = generate_wrong_secret(s_correct)
    diff = int(np.sum(s_wrong != s_correct))
    say("s_wrong generated: wrong_secret_seed=%d  n_coords_different=%d (expected>0)" % (
        WRONG_SECRET_SEED, diff))
    say("s_wrong != s_correct: %s" % (not np.array_equal(s_wrong, s_correct)))

    # Pre-registered null seeds
    null_seeds = np.random.default_rng(20260804002).integers(0, 2**32, size=50).tolist()
    say("first 5 null_seeds: %s" % null_seeds[:5])

    # -----------------------------------------------------------------------
    # TEST A: 50 NULL-control runs (WRONG SECRET)
    # -----------------------------------------------------------------------
    say("=== TEST A: 50 NULL-CONTROL RUNS (wrong secret s_wrong) ===")

    TN_null_values = []
    null_run_records = []
    n_null_completed = 0

    # Single-score baseline for null control (from run-0 null scores)
    null_single_score_var = None
    null_single_score_mean = None
    null_N_run0 = None
    null_predicted_var = None

    for i, seed_i in enumerate(null_seeds):
        t0_run = time.time()
        try:
            coeffs, Bused, N_i, t_sieve = run_single_sieve(Bred_fp, seed_i)
            T_N_null_i, n_vec, scores_null_i = compute_TN_secret(
                coeffs, Bused, b, s_wrong, Q, M, N_LWE)

            # After run 0: compute within-environment null single-score variance
            if i == 0:
                null_single_score_var = float(np.var(scores_null_i, ddof=1))
                null_single_score_mean = float(np.mean(scores_null_i))
                null_N_run0 = int(scores_null_i.shape[0])
                null_predicted_var = null_N_run0 * null_single_score_var
                say("null run-0: N_0=%d null_ssv=%.6f null_ssm=%.6f null_pred_var=%.3f" % (
                    null_N_run0, null_single_score_var, null_single_score_mean,
                    null_predicted_var))

            t_run = time.time() - t0_run
            TN_null_values.append(T_N_null_i)
            n_null_completed += 1
            null_run_records.append({
                "run_index": i,
                "siever_seed": seed_i,
                "N_vectors": n_vec,
                "T_N_null": T_N_null_i,
                "sieve_seconds": round(t_sieve, 3),
                "run_wall_seconds": round(t_run, 3),
                "valid": True,
            })
            say("null run %02d/%d: seed=%u N=%d T_N_null=%.3f sieve=%.1fs" % (
                i, len(null_seeds) - 1, seed_i, n_vec, T_N_null_i, t_sieve))

        except Exception as exc:
            t_run = time.time() - t0_run
            say("null run %02d/%d: seed=%u FAILED: %s" % (
                i, len(null_seeds) - 1, seed_i, exc))
            null_run_records.append({
                "run_index": i,
                "siever_seed": seed_i,
                "N_vectors": None,
                "T_N_null": None,
                "error": str(exc),
                "run_wall_seconds": round(t_run, 3),
                "valid": False,
            })

    say("Test A completed: %d/%d null runs" % (n_null_completed, len(null_seeds)))

    # Compute null variance statistics
    null_stats = None
    if n_null_completed >= 2 and null_predicted_var is not None and null_predicted_var > 0:
        null_stats = chi2_test(TN_null_values, null_predicted_var, n_null_completed)
        say("TEST A: variance_ratio_null=%.4f chi2=%.4f df=%d p=%.6f" % (
            null_stats["variance_ratio"], null_stats["chi2_stat"],
            null_stats["chi2_df"], null_stats["p_value"]))
        say("TEST A 95%% CI for variance_ratio: [%.4f, %.4f]" % (
            null_stats["variance_ratio_95ci"][0], null_stats["variance_ratio_95ci"][1]))
    else:
        say("TEST A: insufficient data for chi2 test (%d completed runs)" % n_null_completed)

    # -----------------------------------------------------------------------
    # TEST B: Outlier seed re-run (CORRECT + WRONG)
    # -----------------------------------------------------------------------
    say("=== TEST B: OUTLIER SEED RE-RUN (correct + wrong secret) ===")

    outlier_records = []
    for seed_i in OUTLIER_SEEDS:
        t0_run = time.time()
        b3_TN = BATCH3_OUTLIER_TN.get(seed_i)
        try:
            coeffs, Bused, N_i, t_sieve = run_single_sieve(Bred_fp, seed_i)

            T_N_correct, n_vec_c, scores_correct = compute_TN_secret(
                coeffs, Bused, b, s_correct, Q, M, N_LWE)
            T_N_wrong, n_vec_w, scores_wrong = compute_TN_secret(
                coeffs, Bused, b, s_wrong, Q, M, N_LWE)

            t_run = time.time() - t0_run

            # Reproducibility delta vs batch-3
            delta_vs_b3 = (T_N_correct - b3_TN) if b3_TN is not None else None

            outlier_records.append({
                "siever_seed": seed_i,
                "N_vectors": n_vec_c,
                "T_N_correct": T_N_correct,
                "T_N_wrong": T_N_wrong,
                "batch3_T_N_correct": b3_TN,
                "delta_T_N_correct_vs_batch3": round(delta_vs_b3, 6) if delta_vs_b3 is not None else None,
                "sieve_seconds": round(t_sieve, 3),
                "run_wall_seconds": round(t_run, 3),
                "valid": True,
            })
            say("outlier seed %u: N=%d T_N_correct=%.3f T_N_wrong=%.3f b3=%.3f delta=%.3f sieve=%.1fs" % (
                seed_i, n_vec_c, T_N_correct, T_N_wrong,
                b3_TN if b3_TN is not None else float("nan"),
                delta_vs_b3 if delta_vs_b3 is not None else float("nan"),
                t_sieve))

        except Exception as exc:
            t_run = time.time() - t0_run
            say("outlier seed %u: FAILED: %s" % (seed_i, exc))
            outlier_records.append({
                "siever_seed": seed_i,
                "N_vectors": None,
                "T_N_correct": None,
                "T_N_wrong": None,
                "batch3_T_N_correct": b3_TN,
                "delta_T_N_correct_vs_batch3": None,
                "error": str(exc),
                "run_wall_seconds": round(t_run, 3),
                "valid": False,
            })

    say("Test B completed: %d/4 outlier seeds" % sum(r["valid"] for r in outlier_records))

    # -----------------------------------------------------------------------
    # Write null_control_results.json  (Test A)
    # -----------------------------------------------------------------------
    null_control_out = {
        "task": TASK,
        "batch": BATCH,
        "goal": GOAL,
        "script_version": SCRIPT_VERSION,
        "states_a_finding": False,
        "compared_against_matzov_nf": False,
        "test": "TEST_A_NULL_CONTROL",
        "description": (
            "Null control: score WRONG secret s_wrong against the real LWE b=A*s+e. "
            "Hypothesis under test: if QEMU environment inflates variance for ALL "
            "cosine-score sums, then variance_ratio_null should also be > 1. "
            "If variance_ratio_null ≈ 1 while batch-3 variance_ratio ≈ 1.39, "
            "the inflation is specific to the correct-secret signal."
        ),
        "parameters": {
            "m": M, "n": N_LWE, "q": Q, "eta": ETA, "sigma": SIGMA,
            "instance_seed": INSTANCE_SEED,
            "fpylll_seed": FPYLLL_SEED,
            "sieve_algo": SIEVE_ALGO,
            "sieve_threads": SIEVE_THREADS,
            "null_seeds_expression": NULL_SEEDS_EXPRESSION,
            "null_seeds": null_seeds,
            "wrong_secret_seed": WRONG_SECRET_SEED,
            "n_runs_requested": 50,
            "n_runs_completed": n_null_completed,
        },
        "wrong_secret_info": {
            "wrong_secret_seed": WRONG_SECRET_SEED,
            "n_coords_different_from_correct": diff,
            "s_wrong_neq_s_correct": not np.array_equal(s_wrong, s_correct),
        },
        "TN_null_values": TN_null_values,
        "TN_null_statistics": {
            "empirical_var": null_stats["empirical_var"] if null_stats else None,
            "mean": null_stats["mean"] if null_stats else None,
            "std": null_stats["std"] if null_stats else None,
            "min": null_stats["min"] if null_stats else None,
            "max": null_stats["max"] if null_stats else None,
        },
        "null_single_score_baseline": {
            "null_single_score_var": null_single_score_var,
            "null_single_score_mean": null_single_score_mean,
            "null_N_run0": null_N_run0,
            "null_predicted_var": null_predicted_var,
        },
        "null_variance_test": {
            "variance_ratio_null": null_stats["variance_ratio"] if null_stats else None,
            "chi2_stat": null_stats["chi2_stat"] if null_stats else None,
            "chi2_df": null_stats["chi2_df"] if null_stats else None,
            "p_value_null": null_stats["p_value"] if null_stats else None,
            "variance_ratio_95ci": null_stats["variance_ratio_95ci"] if null_stats else None,
            "batch3_variance_ratio_correct": 1.3915756694338621,
            "batch3_p_value_correct": 0.001122555172757167,
            "interpretation_note": (
                "OBSERVATION ONLY. states_a_finding=false. "
                "If variance_ratio_null≈1.0: null signal variance is indistinguishable "
                "from independence prediction; inflation is specific to correct-secret signal. "
                "If variance_ratio_null>>1.0: variance inflation is environmental. "
                "No conclusion is drawn here."
            ),
        },
        "null_run_records": null_run_records,
        "platform": platform.platform(),
        "wall_seconds_test_a": round(time.time() - t_start, 3),
        "log": log,
    }

    out_null = os.path.join(args.out_dir, "null_control_results.json")
    with open(out_null, "w") as f:
        json.dump(null_control_out, f, indent=2)
    say("wrote %s" % out_null)

    # -----------------------------------------------------------------------
    # Write outlier_rerun_results.json  (Test B)
    # -----------------------------------------------------------------------
    outlier_out = {
        "task": TASK,
        "batch": BATCH,
        "goal": GOAL,
        "script_version": SCRIPT_VERSION,
        "states_a_finding": False,
        "compared_against_matzov_nf": False,
        "test": "TEST_B_OUTLIER_RERUN",
        "description": (
            "Re-run the 3 high-T_N seeds (2941775225, 26883012, 2418421570) and "
            "run-0 seed (1873347320) from batch-3. Report T_N for both correct and "
            "wrong secret. Assessing whether high T_N values are seed-consistent or "
            "one-time fluctuations."
        ),
        "parameters": {
            "m": M, "n": N_LWE, "q": Q, "eta": ETA, "sigma": SIGMA,
            "instance_seed": INSTANCE_SEED,
            "fpylll_seed": FPYLLL_SEED,
            "sieve_algo": SIEVE_ALGO,
            "sieve_threads": SIEVE_THREADS,
            "outlier_seeds_retested": OUTLIER_SEEDS,
            "wrong_secret_seed": WRONG_SECRET_SEED,
        },
        "batch3_reference": {
            "variance_ratio": 1.3915756694338621,
            "chi2_stat": 207.34477474564545,
            "chi2_df": 149,
            "p_value": 0.001122555172757167,
            "batch3_outlier_TN": BATCH3_OUTLIER_TN,
        },
        "outlier_run_records": outlier_records,
        "interpretation_note": (
            "OBSERVATION ONLY. states_a_finding=false. "
            "Consistency of T_N_correct across batch-3 and this rerun is recorded. "
            "T_N_wrong is a null object control: expected near batch-3 T_N mean (~7551) "
            "if wrong-secret scores are unstructured. No conclusion is drawn."
        ),
        "platform": platform.platform(),
        "wall_seconds_total": round(time.time() - t_start, 3),
        "log": log,
    }

    out_outlier = os.path.join(args.out_dir, "outlier_rerun_results.json")
    with open(out_outlier, "w") as f:
        json.dump(outlier_out, f, indent=2)
    say("wrote %s" % out_outlier)

    say("ALL TESTS COMPLETE: %d null runs + %d outlier reruns" % (
        n_null_completed, sum(r["valid"] for r in outlier_records)))

    return 0


if __name__ == "__main__":
    sys.exit(main())
