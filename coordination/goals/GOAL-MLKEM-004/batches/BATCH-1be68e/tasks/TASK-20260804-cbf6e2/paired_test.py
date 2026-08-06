#!/usr/bin/env python3
"""
paired_test.py  — TASK-20260804-cbf6e2 / BATCH-1be68e / GOAL-MLKEM-004
Batch 5 of 6 — paired correlation test (decisive H1 vs H2 discriminant).

For each of 50 runs (SAME sieve vectors reused):
  1. Build LWE instance (instance_seed=20260803001, fpylll_seed=20260803005).
  2. Run bgj1_sieve with seed siever_seeds[i]:
         numpy.random.default_rng(20260804003).integers(0, 2**32, size=50).tolist()
  3. On the SAME sieve vectors, compute BOTH:
       T_N_correct_i = sum cos(2π · center_mod(x·b − y·s, q)/q)       [correct secret]
       T_N_null_i    = sum cos(2π · center_mod(x·b − y·s_wrong, q)/q)  [wrong secret]
       where s_wrong = centered_binomial(rng(20260804999), eta=2, n=25)

After all runs, compute:
  - Pearson correlation r = numpy.corrcoef(TN_correct, TN_null)[0,1]
  - Spearman rho (scipy.stats.spearmanr)
  - OLS regression TN_null ~ a + b*TN_correct (regression_slope, intercept)
  - Var[T_N_correct - T_N_null] across runs
  - Mean(T_N_correct), Mean(T_N_null)

Prediction discriminant (pre-registered):
  H1 (QEMU environmental): Corr ≈ 1.0  — run quality affects both equally
  H2 (genuine sieve correlation): Corr ≈ 0  — variance is about sieve vectors'
      joint distribution; T_N_correct ∝ x·e while T_N_null ∝ x·e + y·(s−s*)

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
from scipy.stats import spearmanr

from fpylll import IntegerMatrix, LLL, FPLLL
from g6k import Siever, SieverParams

SCRIPT_VERSION = "1.0.0"
TASK  = "TASK-20260804-cbf6e2"
BATCH = "BATCH-1be68e"
GOAL  = "GOAL-MLKEM-004"

# ---- Frozen LWE parameters (identical to all prior batches)
M, N_LWE, Q = 35, 25, 127
D            = M + N_LWE   # 60
ETA          = 2
SIGMA        = 2.0
INSTANCE_SEED  = 20260803001
FPYLLL_SEED    = 20260803005
SIEVE_ALGO     = "bgj1_sieve"
SIEVE_THREADS  = 1

# ---- Pre-registered seed expressions (verbatim)
SIEVER_SEEDS_EXPRESSION = (
    "numpy.random.default_rng(20260804003).integers(0, 2**32, size=50).tolist()"
)
WRONG_SECRET_SEED = 20260804999

N_RUNS_REQUESTED = 50

# Materialise siever seeds at module load — deterministic
SIEVER_SEEDS = (
    np.random.default_rng(20260804003).integers(0, 2**32, size=50).tolist()
)


# ---------------------------------------------------------------------------
# Utility functions (identical logic to prior batches for reproducibility)
# ---------------------------------------------------------------------------

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
    return np.array(
        [[A[i, j] for j in range(A.ncols)] for i in range(A.nrows)],
        dtype=np.int64,
    )


def build_instance_and_lll():
    """Build LWE instance + LLL-reduced basis.  Returns (A, s, e, b, Bred_fp)."""
    rng = np.random.default_rng(INSTANCE_SEED)
    A   = rng.integers(0, Q, size=(M, N_LWE), dtype=np.int64)
    s   = centered_binomial(rng, ETA, N_LWE)
    e   = rounded_gaussian(rng, SIGMA, M)
    b   = np.mod(A.dot(s) + e, Q)

    Bnp  = build_dual_basis(A, Q, M, N_LWE)
    Bfp  = to_intmat(Bnp)
    FPLLL.set_random_seed(FPYLLL_SEED)
    Bred_fp = LLL.reduction(Bfp)
    return A, s, e, b, Bred_fp


def generate_wrong_secret(s_correct):
    """Generate s_wrong from WRONG_SECRET_SEED; assert s_wrong != s_correct."""
    rng_w  = np.random.default_rng(WRONG_SECRET_SEED)
    s_wrong = centered_binomial(rng_w, ETA, N_LWE)
    if np.array_equal(s_wrong, s_correct):
        raise RuntimeError(
            "s_wrong == s_correct; probability ≈ 1/|S|^n; virtually impossible"
        )
    return s_wrong


def run_single_sieve(Bred_fp, siever_seed):
    """Run bgj1_sieve.  Returns (coeffs, Bused, N, t_sieve)."""
    g = Siever(Bred_fp, SieverParams(threads=SIEVE_THREADS), seed=siever_seed)
    g.initialize_local(0, 0, D)
    t0 = time.time()
    g.bgj1_sieve()
    t_sieve = time.time() - t0
    coeffs = np.array([tuple(v) for v in g.itervalues()], dtype=np.int64)
    Bused  = from_intmat(g.M.B)
    return coeffs, Bused, coeffs.shape[0], t_sieve


def compute_TN_and_scores(coeffs, Bused, b, s_candidate, q, m, n):
    """T_N = sum of cosine scores; also returns per-vector score array."""
    V      = coeffs.dot(Bused)          # N × d
    X      = V[:, :m]                   # N × m
    Y      = V[:, m:]                   # N × n
    phases = center_mod(X.dot(b) - Y.dot(s_candidate), q)
    scores = np.cos(2.0 * np.pi * phases / q)
    T_N    = float(scores.sum())
    return T_N, int(V.shape[0]), scores


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir",   default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--repo-root", default=None)
    ap.add_argument("--n-runs",    type=int, default=N_RUNS_REQUESTED)
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

    say("paired_test.py %s  PAIRED CORRELATION — H1 vs H2 discriminant" % SCRIPT_VERSION)
    say("TASK=%s  BATCH=%s  GOAL=%s" % (TASK, BATCH, GOAL))
    say("instance_seed=%d  fpylll_seed=%d" % (INSTANCE_SEED, FPYLLL_SEED))
    say("siever_seeds_expression: %s" % SIEVER_SEEDS_EXPRESSION)
    say("wrong_secret_seed=%d" % WRONG_SECRET_SEED)
    say("first 5 siever_seeds: %s" % SIEVER_SEEDS[:5])
    say("platform: %s" % platform.platform())

    # -------------------------------------------------------------------
    # Build LWE instance ONCE
    # -------------------------------------------------------------------
    A, s_correct, e, b, Bred_fp = build_instance_and_lll()
    say("instance built: |s|_inf=%d  |e|_inf=%d" % (
        int(np.abs(s_correct).max()), int(np.abs(e).max())))

    # Generate wrong secret
    s_wrong = generate_wrong_secret(s_correct)
    n_coords_diff = int(np.sum(s_wrong != s_correct))
    say("s_wrong generated: wrong_secret_seed=%d  n_coords_different=%d  s_wrong!=s_correct: %s" % (
        WRONG_SECRET_SEED, n_coords_diff, not np.array_equal(s_wrong, s_correct)))

    # -------------------------------------------------------------------
    # 50-run paired loop
    # -------------------------------------------------------------------
    n_runs_actual = min(args.n_runs, len(SIEVER_SEEDS))

    TN_correct_values = []
    TN_null_values    = []
    run_records       = []
    n_runs_completed  = 0

    # Run-0 scalar variance quantities (for variance_stats)
    single_score_var_correct = None
    single_score_var_null    = None
    N_vectors_run0           = None

    for i in range(n_runs_actual):
        seed_i = SIEVER_SEEDS[i]
        t0_run = time.time()

        try:
            coeffs, Bused, N_i, t_sieve = run_single_sieve(Bred_fp, seed_i)

            # Correct-secret score
            T_N_correct_i, n_vec_c, scores_correct = compute_TN_and_scores(
                coeffs, Bused, b, s_correct, Q, M, N_LWE)

            # Null-secret score (SAME sieve vectors, different secret)
            T_N_null_i, n_vec_n, scores_null = compute_TN_and_scores(
                coeffs, Bused, b, s_wrong, Q, M, N_LWE)

            t_run = time.time() - t0_run

            # Run-0 single-score variances
            if i == 0:
                single_score_var_correct = float(np.var(scores_correct, ddof=1))
                single_score_var_null    = float(np.var(scores_null, ddof=1))
                N_vectors_run0           = n_vec_c
                say(("run-0 single-score-var: correct=%.6f  null=%.6f  N=%d") % (
                    single_score_var_correct, single_score_var_null, N_vectors_run0))

            TN_correct_values.append(T_N_correct_i)
            TN_null_values.append(T_N_null_i)
            n_runs_completed += 1

            run_records.append({
                "run_index": i,
                "siever_seed": seed_i,
                "N_vectors": n_vec_c,
                "T_N_correct": T_N_correct_i,
                "T_N_null": T_N_null_i,
                "diff_TN": T_N_correct_i - T_N_null_i,
                "sieve_seconds": round(t_sieve, 3),
                "run_wall_seconds": round(t_run, 3),
                "valid": True,
            })

            say("run %02d/%d: seed=%u  N=%d  TN_c=%.3f  TN_n=%.3f  diff=%.3f  sieve=%.1fs" % (
                i, n_runs_actual - 1, seed_i, n_vec_c,
                T_N_correct_i, T_N_null_i,
                T_N_correct_i - T_N_null_i,
                t_sieve))

        except Exception as exc:
            t_run = time.time() - t0_run
            say("run %02d/%d: seed=%u  FAILED: %s" % (i, n_runs_actual - 1, seed_i, exc))
            run_records.append({
                "run_index":   i,
                "siever_seed": seed_i,
                "N_vectors":   None,
                "T_N_correct": None,
                "T_N_null":    None,
                "diff_TN":     None,
                "error":       str(exc),
                "run_wall_seconds": round(t_run, 3),
                "valid": False,
            })

    say("Paired loop complete: %d/%d runs succeeded" % (n_runs_completed, n_runs_actual))

    # -------------------------------------------------------------------
    # Correlation and regression statistics
    # -------------------------------------------------------------------
    pearson_r  = None
    pearson_p  = None
    spearman_r = None
    spearman_p = None
    reg_slope  = None
    reg_intercept = None

    var_TN_correct = None
    var_TN_null    = None
    var_TN_diff    = None
    mean_TN_correct = None
    mean_TN_null    = None
    predicted_var_diff = None

    if n_runs_completed >= 3:
        arr_c = np.array(TN_correct_values, dtype=np.float64)
        arr_n = np.array(TN_null_values,    dtype=np.float64)
        arr_diff = arr_c - arr_n

        # Pearson
        pr = scipy.stats.pearsonr(arr_c, arr_n)
        pearson_r = float(pr[0])
        pearson_p = float(pr[1])

        # Spearman
        sr = spearmanr(arr_c, arr_n)
        spearman_r = float(sr.statistic)
        spearman_p = float(sr.pvalue)

        # OLS regression: TN_null ~ a + b * TN_correct
        A_reg = np.column_stack([np.ones(len(arr_c)), arr_c])
        coeffs_reg, *_ = np.linalg.lstsq(A_reg, arr_n, rcond=None)
        reg_intercept = float(coeffs_reg[0])
        reg_slope     = float(coeffs_reg[1])

        # Variance statistics
        var_TN_correct  = float(np.var(arr_c,    ddof=1))
        var_TN_null     = float(np.var(arr_n,    ddof=1))
        var_TN_diff     = float(np.var(arr_diff, ddof=1))
        mean_TN_correct = float(np.mean(arr_c))
        mean_TN_null    = float(np.mean(arr_n))

        # Predicted Var[T_N_correct - T_N_null] under independence:
        # = N0 * (Var[s_correct_i] + Var[s_null_i] - 2*Cov[s_correct, s_null])
        # For same sieve vectors: Cov[score_c, score_n] is the empirical
        # per-vector covariance from run-0 (cross-term; we approximate from
        # run-0 score arrays if they were retained — here we must re-compute).
        # NOTE: we do not retain run-0 score arrays at this point; we use the
        # variance-only formula noting that for a wrong secret the cross-covariance
        # is a separate quantity we cannot recover without the run-0 scores arrays.
        # We record single_score_var for both and set cross_cov = None to be honest.
        if (N_vectors_run0 is not None and
                single_score_var_correct is not None and
                single_score_var_null is not None):
            # Uncorrelated approximation (Cov=0):
            predicted_var_diff = N_vectors_run0 * (
                single_score_var_correct + single_score_var_null
            )

        say("Pearson r=%.4f  p=%.6f" % (pearson_r, pearson_p))
        say("Spearman rho=%.4f  p=%.6f" % (spearman_r, spearman_p))
        say("OLS slope=%.6f  intercept=%.6f" % (reg_slope, reg_intercept))
        say("Var[TN_correct]=%.4f  Var[TN_null]=%.4f  Var[TN_diff]=%.4f" % (
            var_TN_correct, var_TN_null, var_TN_diff))
        say("Mean[TN_correct]=%.3f  Mean[TN_null]=%.3f" % (
            mean_TN_correct, mean_TN_null))
        if predicted_var_diff is not None:
            say("Predicted Var[TN_diff] (Cov=0 approx)=%.4f  ratio=%.4f" % (
                predicted_var_diff, var_TN_diff / predicted_var_diff))
    else:
        say("Fewer than 3 valid runs; skipping correlation statistics")

    # -------------------------------------------------------------------
    # Assemble paired_results.json
    # -------------------------------------------------------------------
    paired_results = {
        "task":  TASK,
        "batch": BATCH,
        "goal":  GOAL,
        "script_version": SCRIPT_VERSION,
        "states_a_finding": False,
        "compared_against_matzov_nf": False,
        "rule12_status": "UNMET and UNWAIVED",
        "parameters": {
            "m": M, "n": N_LWE, "q": Q, "eta": ETA, "sigma": SIGMA,
            "instance_seed": INSTANCE_SEED,
            "fpylll_seed":   FPYLLL_SEED,
            "wrong_secret_seed": WRONG_SECRET_SEED,
            "siever_seeds_expression": SIEVER_SEEDS_EXPRESSION,
            "sieve_algo":    SIEVE_ALGO,
            "sieve_threads": SIEVE_THREADS,
            "n_runs_requested": N_RUNS_REQUESTED,
            "n_runs_completed": n_runs_completed,
            "wrong_secret_info": {
                "n_coords_different_from_correct": n_coords_diff,
                "s_wrong_neq_s_correct": not np.array_equal(s_wrong, s_correct),
            },
        },
        "TN_correct": TN_correct_values,
        "TN_null":    TN_null_values,
        "correlation": {
            "pearson_r":          pearson_r,
            "pearson_p":          pearson_p,
            "spearman_r":         spearman_r,
            "spearman_p":         spearman_p,
            "regression_slope":   reg_slope,
            "regression_intercept": reg_intercept,
        },
        "variance_stats": {
            "var_TN_correct":         var_TN_correct,
            "var_TN_null":            var_TN_null,
            "var_TN_diff":            var_TN_diff,
            "N_vectors_run0":         N_vectors_run0,
            "single_score_var_correct": single_score_var_correct,
            "single_score_var_null":    single_score_var_null,
            "predicted_var_diff": predicted_var_diff,
            "note_predicted_var_diff": (
                "Approximated as N0*(Var[score_correct]+Var[score_null]) "
                "with Cov=0; cross-covariance not separately estimated."
            ),
        },
        "mean_TN_correct": mean_TN_correct,
        "mean_TN_null":    mean_TN_null,
        "run_records": run_records,
        "platform": platform.platform(),
        "wall_seconds": round(time.time() - t_start, 3),
        "log": log,
    }

    out_path = os.path.join(args.out_dir, "paired_results.json")
    with open(out_path, "w") as f:
        json.dump(paired_results, f, indent=2)
    say("wrote %s" % out_path)

    say("paired_test.py COMPLETE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
