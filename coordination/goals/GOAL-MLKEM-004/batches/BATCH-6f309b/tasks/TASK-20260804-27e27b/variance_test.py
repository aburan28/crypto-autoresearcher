#!/usr/bin/env python3
"""
Variance test for TASK-20260804-27e27b / BATCH-6f309b / GOAL-MLKEM-004.

Run 50 independent bgj1_sieve runs on the SAME LWE instance (instance_seed=20260803001)
with 50 DIFFERENT g6k Siever seeds (siever_seeds = list(range(50))).

For each run:
1. Re-generate the SAME LWE instance (A, s, e) from instance_seed=20260803001.
2. Re-run LLL with fpylll_seed=20260803005.
3. Run bgj1_sieve with siever_seeds[i].
4. Score the correct secret s against b = A*s + e.
5. Compute T_N_i = sum of all N correct-candidate cosine scores.

After all runs:
- Compute empirical_var_TN = Var(T_N_0, ..., T_N_49) (sample variance, ddof=1).
- Load batch-1 raw_scores.json for the single-score variance:
  single_scores = [cos(2*pi*t/127) for t in phases_t of correct candidate / MAIN]
  single_score_var = Var(single_scores) (sample variance, ddof=1)
  independence_predicted_var = TARGET_N * single_score_var
- Compute variance_ratio = empirical_var_TN / independence_predicted_var.

OUTPUTS ONLY observations. States no finding. No comparison against MATZOV.Nf.

INFRASTRUCTURE NOTE: This script requires g6k 0.1.2. g6k uses x86-specific SIMD
intrinsics and cannot be built on ARM64 (Apple Silicon) macOS. This script is written
correctly for execution on Linux x86_64 (the batch-1 environment). On ARM64 it will
fail at import with ImportError: No module named 'g6k'. That is an infrastructure_error.
"""

import argparse
import hashlib
import json
import os
import platform
import resource
import sys
import time

import numpy as np

from fpylll import IntegerMatrix, LLL, FPLLL
from g6k import Siever, SieverParams  # requires x86 Linux build

SCRIPT_VERSION = "1.0.0"
TASK = "TASK-20260804-27e27b"
BATCH = "BATCH-6f309b"
GOAL = "GOAL-MLKEM-004"

# ---- Frozen parameters (identical to batch-1 for everything except siever_seed)
M, N_LWE, Q = 35, 25, 127
D = M + N_LWE          # lattice dimension = 60
ETA = 2                # CB secret eta
SIGMA = 2.0            # error std dev
INSTANCE_SEED = 20260803001   # FIXED across all 50 runs
FPYLLL_SEED = 20260803005     # FIXED across all 50 runs
SIEVE_ALGO = "bgj1_sieve"
SIEVE_THREADS = 1
TARGET_N = 17919       # match batch-1 expected sieve vector count

# 50 different Siever seeds
SIEVER_SEEDS = list(range(50))   # 0, 1, 2, ..., 49

BATCH1_RAW_DEFAULT = (
    "coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/"
    "tasks/TASK-20260803-e53ce2/raw_scores.json"
)


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


def compute_TN(coeffs, Bused, b, s, q, m, n):
    """Compute T_N = sum of cosine scores for the correct secret s."""
    V = coeffs.dot(Bused)    # N x d
    X = V[:, :m]             # N x m
    Y = V[:, m:]             # N x n
    xb = X.dot(b)
    ys = Y.dot(s)
    phases = center_mod(xb - ys, q)
    scores = np.cos(2.0 * np.pi * phases / q)
    T_N = float(scores.sum())
    return T_N, int(V.shape[0])


def load_batch1_single_scores(batch1_raw_path):
    """
    Load batch-1 raw_scores.json and extract single cosine scores for the
    correct candidate under the MAIN_lwe_sigma2 target.
    Returns list of float cosine scores, length = TARGET_N.
    """
    with open(batch1_raw_path) as f:
        raw = json.load(f)

    # Find MAIN_lwe_sigma2 target
    main_target = None
    for tgt in raw["targets"]:
        if tgt["name"].startswith("MAIN_lwe"):
            main_target = tgt
            break
    if main_target is None:
        raise ValueError("MAIN_lwe target not found in batch-1 raw_scores.json")

    # Find correct candidate (index 0)
    correct_cand = None
    for pc in main_target["per_candidate"]:
        if pc["candidate_index"] == 0:
            correct_cand = pc
            break
    if correct_cand is None:
        raise ValueError("correct candidate (index 0) not found in MAIN target")

    if "scores_cos" in correct_cand:
        return correct_cand["scores_cos"]
    elif "phases_t" in correct_cand:
        phases = np.array(correct_cand["phases_t"], dtype=np.int64)
        q = raw["parameters"]["q"]
        scores = np.cos(2.0 * np.pi * phases / q)
        return scores.tolist()
    else:
        raise ValueError("No scores_cos or phases_t for correct candidate")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--batch1-raw", default=None,
                    help="Path to batch-1 raw_scores.json")
    ap.add_argument("--repo-root", default=None,
                    help="Repository root for resolving default batch1-raw path")
    ap.add_argument("--n-runs", type=int, default=50,
                    help="Number of sieve runs (default: 50)")
    ap.add_argument("--mem-cap-gb", type=float, default=6.0)
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

    say("variance_test.py %s: %d runs, sieve=%s" % (SCRIPT_VERSION, args.n_runs, SIEVE_ALGO))
    say("instance_seed=%d fpylll_seed=%d" % (INSTANCE_SEED, FPYLLL_SEED))
    say("siever_seeds: range(0, %d)" % args.n_runs)
    say("platform: %s" % platform.platform())

    # Resolve batch-1 raw path
    batch1_raw = args.batch1_raw
    if batch1_raw is None:
        repo_root = args.repo_root or os.path.abspath(
            os.path.join(os.path.dirname(__file__), *['..'] * 5))
        batch1_raw = os.path.join(repo_root, BATCH1_RAW_DEFAULT)
    say("batch1_raw: %s" % batch1_raw)

    # Build instance (ONCE, reuse across all runs)
    A, s, e, b, Bred_fp = build_instance_and_lll()
    say("instance built: |s|_inf=%d |e|_inf=%d" % (
        int(np.abs(s).max()), int(np.abs(e).max())))

    # 50-run variance measurement
    TN_values = []
    run_records = []
    n_runs_completed = 0

    for i in range(args.n_runs):
        seed_i = SIEVER_SEEDS[i]
        t0_run = time.time()
        try:
            coeffs, Bused, N_i, t_sieve = run_single_sieve(Bred_fp, seed_i)
            T_N_i, n_vec = compute_TN(coeffs, Bused, b, s, Q, M, N_LWE)
            t_run = time.time() - t0_run
            run_records.append({
                "run_index": i,
                "siever_seed": seed_i,
                "N_vectors": n_vec,
                "T_N": T_N_i,
                "sieve_seconds": round(t_sieve, 3),
                "run_wall_seconds": round(t_run, 3),
                "valid": True,
            })
            TN_values.append(T_N_i)
            n_runs_completed += 1
            say("run %02d/49: seed=%d N=%d T_N=%.3f sieve=%.1fs" % (
                i, seed_i, n_vec, T_N_i, t_sieve))
        except Exception as exc:
            t_run = time.time() - t0_run
            say("run %02d/49: seed=%d FAILED: %s" % (i, seed_i, exc))
            run_records.append({
                "run_index": i,
                "siever_seed": seed_i,
                "N_vectors": None,
                "T_N": None,
                "error": str(exc),
                "run_wall_seconds": round(t_run, 3),
                "valid": False,
            })

    say("Completed %d/%d runs" % (n_runs_completed, args.n_runs))

    # Variance statistics
    if len(TN_values) < 2:
        say("ERROR: fewer than 2 valid runs; cannot compute variance")
        empirical_var_TN = None
        mean_TN = None
        std_TN = None
        min_TN = None
        max_TN = None
    else:
        TN_arr = np.array(TN_values, dtype=np.float64)
        empirical_var_TN = float(np.var(TN_arr, ddof=1))
        mean_TN = float(np.mean(TN_arr))
        std_TN = float(np.std(TN_arr, ddof=1))
        min_TN = float(np.min(TN_arr))
        max_TN = float(np.max(TN_arr))
        say("T_N stats: mean=%.3f std=%.3f var=%.3f min=%.3f max=%.3f" % (
            mean_TN, std_TN, empirical_var_TN, min_TN, max_TN))

    # Load batch-1 single scores for independence prediction
    say("Loading batch-1 single scores for independence prediction...")
    single_score_var = None
    independence_predicted_var = None
    variance_ratio = None
    batch1_load_error = None

    try:
        single_scores = load_batch1_single_scores(batch1_raw)
        ss_arr = np.array(single_scores, dtype=np.float64)
        single_score_var = float(np.var(ss_arr, ddof=1))
        single_score_mean = float(np.mean(ss_arr))
        single_score_N = len(ss_arr)
        independence_predicted_var = TARGET_N * single_score_var

        say("batch-1 single scores: N=%d mean=%.6f var=%.6f" % (
            single_score_N, single_score_mean, single_score_var))
        say("independence_predicted_var = %d * %.6f = %.6f" % (
            TARGET_N, single_score_var, independence_predicted_var))

        if empirical_var_TN is not None and independence_predicted_var > 0:
            variance_ratio = empirical_var_TN / independence_predicted_var
            say("variance_ratio = Var[T_N] / (N * Var[s_i]) = %.3f" % variance_ratio)
    except Exception as exc:
        batch1_load_error = str(exc)
        say("batch-1 load error: %s" % exc)

    # Write results
    variance_results = {
        "task": TASK,
        "batch": BATCH,
        "goal": GOAL,
        "script_version": SCRIPT_VERSION,
        "states_a_finding": False,
        "compared_against_matzov_nf": False,
        "parameters": {
            "m": M, "n": N_LWE, "q": Q, "eta": ETA, "sigma": SIGMA,
            "instance_seed": INSTANCE_SEED, "fpylll_seed": FPYLLL_SEED,
            "sieve_algo": SIEVE_ALGO, "sieve_threads": SIEVE_THREADS,
            "siever_seeds": SIEVER_SEEDS[:args.n_runs],
            "target_N": TARGET_N,
            "n_runs_requested": args.n_runs,
            "n_runs_completed": n_runs_completed,
        },
        "TN_values": TN_values,
        "TN_statistics": {
            "empirical_var_TN": empirical_var_TN,
            "mean_TN": mean_TN,
            "std_TN": std_TN,
            "min_TN": min_TN,
            "max_TN": max_TN,
        },
        "independence_test": {
            "batch1_raw_path": batch1_raw,
            "batch1_load_error": batch1_load_error,
            "single_score_var": single_score_var,
            "target_N_for_prediction": TARGET_N,
            "independence_predicted_var": independence_predicted_var,
            "variance_ratio": variance_ratio,
            "interpretation_note": (
                "ratio=1.0 is consistent with i.i.d.; ratio>1.0 means more variance "
                "than independence predicts; ratio<1.0 means less. "
                "No conclusion is drawn here."
            ),
        },
        "run_records": run_records,
        "log": log,
        "platform": platform.platform(),
        "wall_seconds": round(time.time() - t_start, 3),
    }

    out_path = os.path.join(args.out_dir, "variance_results.json")
    with open(out_path, "w") as f:
        json.dump(variance_results, f, indent=2)
    say("wrote %s" % out_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
