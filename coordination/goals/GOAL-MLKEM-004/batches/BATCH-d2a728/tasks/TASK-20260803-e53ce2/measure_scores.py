#!/usr/bin/env python3
"""
TASK-20260803-e53ce2 / BATCH-d2a728 / GOAL-MLKEM-004

MEASURE the per-vector dual-attack score distribution of SIEVE-PRODUCED dual
vectors on an LWE instance whose secret is known to this harness by
construction.

This script MEASURES AND EMITS RAW DATA ONLY.
 - It states no finding.
 - It performs no comparison against any cost model's assumed advantage law
   (in particular NOT against estimator/lwe_dual.py class MATZOV method Nf).
   That comparison is a later batch, after this raw data is independently
   reviewed.
 - Reduced-dimension measurement is not crypto-scale evidence and this script
   makes no statement about FIPS 203 parameter sets.

------------------------------------------------------------------------------
WHAT IS COMPUTED
------------------------------------------------------------------------------
LWE instance (row convention):   A in Z_q^{m x n},  b = A s + e  mod q.

Dual lattice (dimension d = m + n, determinant q^n):

    L = { (x, y) in Z^m x Z^n  :  y == A^T x   (mod q) }

    row basis    B = [ I_m   A    ]
                     [ 0     q I_n]

For any (x, y) in L and any candidate secret s':

    x.b - y.s'  ==  (A^T x - y).s + x.e  ==  x.e + y.(s - s')   (mod q)

so for the CORRECT secret the phase collapses to x.e, which is small when the
dual vector is short and the error is small; for a wrong candidate it picks up
the extra term y.(s - s').

Per-vector score (the standard dual-sieve score contribution):

    score_i(s') = cos( 2*pi * t_i(s') / q ),
    t_i(s')     = ((x_i.b - y_i.s') mod q) centred into (-q/2, q/2]

RAW OUTPUT: for every sieve-produced vector i we emit t_i(s') for the correct
secret and for every wrong candidate, plus ||v_i||^2, ||x_i||^2, ||y_i||^2 and
x_i.e. The cosine score is an exact deterministic function of t_i, so a
reviewer can recompute any statistic they wish (a different score function, a
norm-conditioned subpopulation, cross-candidate correlations, tails, ...).
Cosine arrays are ALSO emitted for the two primary targets so that "scores"
are literally present and not merely recomputable.

------------------------------------------------------------------------------
CONTROLS RUN (see report.md)
------------------------------------------------------------------------------
 NULL  : identical pipeline, identical dual vectors, identical candidates and
         identical scoring code, with the SIGNAL REMOVED -- b replaced by a
         uniformly random vector in Z_q^m. No LWE structure remains, so a
         pipeline that still "finds" the nominal secret is measuring itself.
 DECAY : the same pipeline with the error standard deviation swept upward, the
         parameter meant to destroy the signal. A quantity that fails to decay
         as sigma grows is the canonical artifact tell.
 CERT  : every sieve-produced vector is re-verified to lie in L by integer
         arithmetic (y == A^T x mod q) computed independently of g6k, and the
         sieve's coefficient-to-lattice-vector interpretation is checked
         against a direct recomputation of the basis product.
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
from g6k import Siever, SieverParams

SCRIPT_VERSION = "1.0.0"


# --------------------------------------------------------------------------
# instance generation -- every source of randomness is seeded and recorded
# --------------------------------------------------------------------------
def centered_binomial(rng, eta, size):
    """ML-KEM-style centred binomial, entries in [-eta, eta], stddev sqrt(eta/2)."""
    a = rng.integers(0, 2, size=(size, eta), dtype=np.int64).sum(axis=1)
    b = rng.integers(0, 2, size=(size, eta), dtype=np.int64).sum(axis=1)
    return (a - b).astype(np.int64)


def rounded_gaussian(rng, sigma, size):
    """Rounded (discretised) Gaussian of the requested standard deviation."""
    return np.rint(rng.normal(0.0, sigma, size=size)).astype(np.int64)


def center_mod(v, q):
    """Centre residues into (-q/2, q/2]."""
    r = np.mod(v, q)
    r = np.where(r > q // 2, r - q, r)
    return r.astype(np.int64)


# --------------------------------------------------------------------------
def build_dual_basis(A, q, m, n):
    """Row basis of L = {(x,y) : y == A^T x mod q}, dimension d = m+n."""
    d = m + n
    B = np.zeros((d, d), dtype=np.int64)
    B[:m, :m] = np.eye(m, dtype=np.int64)
    B[:m, m:] = A                       # row i -> x = e_i, y = A^T e_i = A[i,:]
    B[m:, m:] = q * np.eye(n, dtype=np.int64)
    return B


def to_intmat(M):
    A = IntegerMatrix(M.shape[0], M.shape[1])
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            A[i, j] = int(M[i, j])
    return A


def from_intmat(A):
    return np.array([[A[i, j] for j in range(A.ncols)] for i in range(A.nrows)],
                    dtype=np.int64)


# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true",
                    help="tiny configuration used to exercise the pipeline")
    ap.add_argument("--out-dir", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--tag", default="main")
    ap.add_argument("--mem-cap-gb", type=float, default=6.0,
                    help="hard address-space cap (task budget); 0 disables")
    args = ap.parse_args()

    t_start = time.time()

    # Hard memory cap from the task budget, enforced by the OS on this process.
    if args.mem_cap_gb > 0:
        cap = int(args.mem_cap_gb * (1 << 30))
        resource.setrlimit(resource.RLIMIT_AS, (cap, cap))

    # ---------------- frozen run parameters ----------------
    if args.smoke:
        cfg = dict(m=24, n=16, q=127, sieve="bgj1_sieve",
                   eta_secret=2, sigma_main=2.0,
                   n_cand_uniform=4, n_cand_secretdist=2, n_cand_nearmiss=2,
                   decay_sigmas=[1.0, 8.0], decay_uniform_error=True,
                   decay_n_candidates=2)
    else:
        cfg = dict(m=35, n=25, q=127, sieve="bgj1_sieve",
                   eta_secret=2, sigma_main=2.0,
                   n_cand_uniform=16, n_cand_secretdist=8, n_cand_nearmiss=8,
                   decay_sigmas=[0.5, 1.0, 4.0, 8.0, 16.0],
                   decay_uniform_error=True,
                   decay_n_candidates=4)

    SEEDS = dict(instance=20260803001,     # A, s, e_main
                 candidates=20260803002,   # wrong-candidate draws
                 null_target=20260803003,  # uniform b for the NULL control
                 decay_errors=20260803004, # error draws for the decay sweep
                 sieve=0x6D4C4B454D)       # g6k Siever RNG seed
    FPLLL_SEED = 20260803005

    m, n, q = cfg["m"], cfg["n"], cfg["q"]
    d = m + n

    log = []

    def say(msg):
        line = "[%7.1fs] %s" % (time.time() - t_start, msg)
        print(line, flush=True)
        log.append(line)

    say("script %s  smoke=%s" % (SCRIPT_VERSION, args.smoke))
    say("config: m=%d n=%d d=%d q=%d sieve=%s" % (m, n, d, q, cfg["sieve"]))
    say("seeds: %s  fpll_seed=%d" % (SEEDS, FPLLL_SEED))

    # ---------------- LWE instance, known secret ----------------
    rng_inst = np.random.default_rng(SEEDS["instance"])
    A = rng_inst.integers(0, q, size=(m, n), dtype=np.int64)
    s = centered_binomial(rng_inst, cfg["eta_secret"], n)
    e_main = rounded_gaussian(rng_inst, cfg["sigma_main"], m)
    b_main = np.mod(A.dot(s) + e_main, q)

    say("instance built: |s|_inf=%d  |e|_inf=%d  e_stddev_empirical=%.3f"
        % (int(np.abs(s).max()), int(np.abs(e_main).max()), float(e_main.std())))

    # ---------------- dual lattice, LLL, SIEVE ----------------
    Bnp = build_dual_basis(A, q, m, n)
    Bfp = to_intmat(Bnp)

    FPLLL.set_random_seed(FPLLL_SEED)
    t0 = time.time()
    Bred_fp = LLL.reduction(Bfp)
    t_lll = time.time() - t0
    say("LLL done in %.2fs" % t_lll)

    g = Siever(Bred_fp, SieverParams(threads=1), seed=SEEDS["sieve"])
    g.initialize_local(0, 0, d)
    t0 = time.time()
    getattr(g, cfg["sieve"])()
    t_sieve = time.time() - t0

    coeffs = np.array([tuple(v) for v in g.itervalues()], dtype=np.int64)
    N = coeffs.shape[0]
    say("SIEVE %s dim=%d: %d vectors in %.2fs" % (cfg["sieve"], d, N, t_sieve))

    # basis actually used by the siever (it may transform internally)
    Bused = from_intmat(g.M.B)
    V = coeffs.dot(Bused)                      # N x d lattice vectors
    X = V[:, :m]
    Y = V[:, m:]

    # ---------------- CERTIFICATE: independent lattice-membership check ----
    t0 = time.time()
    resid = np.mod(X.dot(A) - Y, q)
    n_bad = int(np.count_nonzero(resid))
    n_zero_rows = int(np.count_nonzero(np.all(V == 0, axis=1)))
    cert = dict(
        kind="lattice_membership",
        statement="every emitted vector v=(x,y) satisfies y == A^T x (mod q), "
                  "i.e. lies in the dual lattice L",
        checked_vectors=N,
        violating_entries=n_bad,
        all_zero_vectors=n_zero_rows,
        verified=bool(n_bad == 0 and n_zero_rows == 0),
        method="integer arithmetic on numpy int64, computed from A and the "
               "reconstructed lattice vectors, independent of g6k's internal "
               "representation",
        check_seconds=None,
    )
    cert["check_seconds"] = round(time.time() - t0, 3)
    say("CERTIFICATE lattice_membership: violating_entries=%d zero_vectors=%d verified=%s"
        % (n_bad, n_zero_rows, cert["verified"]))
    if not cert["verified"]:
        say("CERTIFICATE FAILED -- aborting before any score is reported")
        out = dict(certificate=cert, log=log, aborted=True)
        with open(os.path.join(args.out_dir, "results.json"), "w") as f:
            json.dump(out, f, indent=2)
        sys.exit(3)

    norms2 = (V * V).sum(axis=1)
    xnorms2 = (X * X).sum(axis=1)
    ynorms2 = (Y * Y).sum(axis=1)
    say("vector norms: ||v||^2 min=%d med=%d max=%d"
        % (int(norms2.min()), int(np.median(norms2)), int(norms2.max())))

    # ---------------- candidate secrets ----------------
    rng_cand = np.random.default_rng(SEEDS["candidates"])
    candidates = []          # list of (label, type, vector)
    candidates.append(("correct", "correct_secret", s.copy()))
    for i in range(cfg["n_cand_uniform"]):
        candidates.append(("uniform_%02d" % i, "uniform_Zq",
                           rng_cand.integers(0, q, size=n, dtype=np.int64)))
    for i in range(cfg["n_cand_secretdist"]):
        candidates.append(("secretdist_%02d" % i, "centered_binomial_eta%d" % cfg["eta_secret"],
                           centered_binomial(rng_cand, cfg["eta_secret"], n)))
    for i in range(cfg["n_cand_nearmiss"]):
        c = s.copy()
        c[i % n] = c[i % n] + 1
        candidates.append(("nearmiss_%02d" % i, "correct_secret_plus_1_at_coord_%d" % (i % n), c))

    # a wrong candidate may coincide with s by chance -- record it, never hide it
    coincidences = [lab for (lab, typ, c) in candidates[1:] if np.array_equal(c, s)]
    say("candidates: %d total (1 correct + %d wrong); coincidences_with_secret=%s"
        % (len(candidates), len(candidates) - 1, coincidences if coincidences else "none"))

    cand_meta = [dict(index=i, label=lab, type=typ, vector=[int(z) for z in c],
                      equals_correct_secret=bool(np.array_equal(c, s)))
                 for i, (lab, typ, c) in enumerate(candidates)]
    Cmat = np.array([c for (_, _, c) in candidates], dtype=np.int64)   # K x n

    # ---------------- scoring ----------------
    def phases_for_target(bvec, cand_matrix):
        """t_i(s') centred in (-q/2, q/2], shape (n_cand, N)."""
        xb = X.dot(bvec)                      # N
        ys = Y.dot(cand_matrix.T)             # N x K
        return center_mod(xb[:, None] - ys, q).T

    def scores_from_phases(T):
        return np.cos(2.0 * np.pi * T / q)

    targets = []

    # ---- MAIN: the LWE target
    targets.append(dict(
        name="MAIN_lwe_sigma%.4g" % cfg["sigma_main"],
        role="signal",
        description="b = A s + e mod q, e ~ rounded Gaussian sigma=%.4g" % cfg["sigma_main"],
        b=b_main, error_distribution="rounded_gaussian(sigma=%.4g)" % cfg["sigma_main"],
        sigma=cfg["sigma_main"], seed=SEEDS["instance"],
        candidate_subset=list(range(len(candidates))), emit_cosines=True,
        e=e_main))

    # ---- NULL: identical pipeline, signal removed
    rng_null = np.random.default_rng(SEEDS["null_target"])
    b_null = rng_null.integers(0, q, size=m, dtype=np.int64)
    targets.append(dict(
        name="NULL_uniform_target",
        role="null",
        description="SIGNAL REMOVED: b drawn uniformly from Z_q^m, no LWE "
                    "structure; same A, same dual vectors, same candidates, "
                    "same scoring code. 'correct' below is the nominal secret "
                    "s, which is NOT a solution to this target.",
        b=b_null, error_distribution="none (target is uniform on Z_q^m)",
        sigma=None, seed=SEEDS["null_target"],
        candidate_subset=list(range(len(candidates))), emit_cosines=True,
        e=None))

    # ---- DECAY: sweep the parameter meant to destroy the signal
    rng_decay = np.random.default_rng(SEEDS["decay_errors"])
    dsub = [0] + list(range(1, 1 + cfg["decay_n_candidates"]))
    for sig in cfg["decay_sigmas"]:
        e_d = rounded_gaussian(rng_decay, sig, m)
        targets.append(dict(
            name="DECAY_sigma%.4g" % sig, role="decay_control",
            description="b = A s + e mod q with sigma=%.4g (same s)" % sig,
            b=np.mod(A.dot(s) + e_d, q),
            error_distribution="rounded_gaussian(sigma=%.4g)" % sig,
            sigma=sig, seed=SEEDS["decay_errors"],
            candidate_subset=dsub, emit_cosines=False, e=e_d))
    if cfg["decay_uniform_error"]:
        e_u = center_mod(rng_decay.integers(0, q, size=m, dtype=np.int64), q)
        targets.append(dict(
            name="DECAY_uniform_error", role="decay_control",
            description="b = A s + e mod q with e uniform on Z_q (error as "
                        "large as the modulus allows: signal fully destroyed)",
            b=np.mod(A.dot(s) + e_u, q),
            error_distribution="uniform_Zq", sigma=None,
            seed=SEEDS["decay_errors"],
            candidate_subset=dsub, emit_cosines=False, e=e_u))

    raw_targets = []
    summary_targets = []

    for tg in targets:
        t0 = time.time()
        sub = tg["candidate_subset"]
        T = phases_for_target(tg["b"], Cmat[sub])          # (len(sub), N)
        S = scores_from_phases(T)
        el = time.time() - t0

        per_cand = []
        for j, ci in enumerate(sub):
            per_cand.append(dict(
                candidate_index=int(ci),
                candidate_label=cand_meta[ci]["label"],
                candidate_type=cand_meta[ci]["type"],
                phases_t=[int(z) for z in T[j]],
            ))
            if tg["emit_cosines"]:
                per_cand[-1]["scores_cos"] = [round(float(z), 6) for z in S[j]]
            elif ci == 0:
                per_cand[-1]["scores_cos"] = [round(float(z), 6) for z in S[j]]

        raw_targets.append(dict(
            name=tg["name"], role=tg["role"], description=tg["description"],
            error_distribution=tg["error_distribution"], sigma=tg["sigma"],
            seed=tg["seed"],
            b=[int(z) for z in tg["b"]],
            error_vector=([int(z) for z in tg["e"]] if tg["e"] is not None else None),
            n_vectors=int(N),
            score_definition="score_i = cos(2*pi*phases_t[i]/q), q=%d" % q,
            per_candidate=per_cand,
            scoring_seconds=round(el, 3),
        ))

        # summaries are CONVENIENCE ONLY; every number here is recomputable
        # from the raw arrays above.
        means = S.mean(axis=1)
        summ = dict(
            name=tg["name"], role=tg["role"], n_vectors=int(N),
            per_candidate_mean_score={
                cand_meta[ci]["label"]: round(float(means[j]), 6)
                for j, ci in enumerate(sub)},
            correct_label_mean=round(float(means[0]), 6),
            wrong_mean_of_means=(round(float(means[1:].mean()), 6)
                                 if len(sub) > 1 else None),
            wrong_max_mean=(round(float(means[1:].max()), 6)
                            if len(sub) > 1 else None),
            wrong_min_mean=(round(float(means[1:].min()), 6)
                            if len(sub) > 1 else None),
            wrong_sd_of_means=(round(float(means[1:].std(ddof=1)), 6)
                               if len(sub) > 2 else None),
            rank_of_correct_label_by_mean=int(1 + (means[1:] > means[0]).sum()),
            n_candidates_scored=len(sub),
        )
        summary_targets.append(summ)
        say("target %-26s scored %d cand x %d vec in %.2fs | mean@nominal=%+.4f "
            "| wrong mean-of-means=%s | rank=%d/%d"
            % (tg["name"], len(sub), N, el, summ["correct_label_mean"],
               ("%+.4f" % summ["wrong_mean_of_means"]) if summ["wrong_mean_of_means"] is not None else "n/a",
               summ["rank_of_correct_label_by_mean"], len(sub)))

    # ---------------- write artifacts ----------------
    env = dict(
        python=sys.version,
        platform=platform.platform(),
        numpy=np.__version__,
        fpylll=__import__("fpylll").__version__,
        g6k="0.1.2",
        venv="/tmp/sagevenv",
    )

    raw = dict(
        task="TASK-20260803-e53ce2",
        script_version=SCRIPT_VERSION,
        emitted="RAW PER-VECTOR DATA. No finding is stated. No comparison "
                "against any assumed advantage law is performed.",
        score_definition="score_i(s') = cos(2*pi*t_i(s')/q) where "
                         "t_i(s') = centre_mod(x_i.b - y_i.s', q). The cosine "
                         "score is an exact function of the emitted integer "
                         "phase, so any alternative score function or "
                         "conditional statistic is recomputable by the reader.",
        parameters=dict(m=m, n=n, d=d, q=q, sieve_algorithm=cfg["sieve"],
                        secret_distribution="centered_binomial(eta=%d)" % cfg["eta_secret"],
                        main_error_distribution="rounded_gaussian(sigma=%.4g)" % cfg["sigma_main"],
                        n_sieve_vectors=int(N), seeds=SEEDS, fpylll_seed=FPLLL_SEED),
        secret=[int(z) for z in s],
        A=[[int(z) for z in row] for row in A],
        certificate=cert,
        per_vector=dict(
            note="index-aligned with every phases_t / scores_cos array below",
            norm2_v=[int(z) for z in norms2],
            norm2_x=[int(z) for z in xnorms2],
            norm2_y=[int(z) for z in ynorms2],
            x_dot_e_main=[int(z) for z in center_mod(X.dot(e_main), q)],
        ),
        candidates=cand_meta,
        targets=raw_targets,
    )

    results = dict(
        task="TASK-20260803-e53ce2",
        batch="BATCH-d2a728",
        goal="GOAL-MLKEM-004",
        script_version=SCRIPT_VERSION,
        smoke=bool(args.smoke),
        states_a_finding=False,
        compared_against_assumed_law=False,
        run=dict(
            sieve_algorithm=cfg["sieve"],
            lattice_dimension=d,
            lwe_m=m, lwe_n=n, modulus=q,
            secret_distribution="centered_binomial(eta=%d)" % cfg["eta_secret"],
            error_distribution_main="rounded_gaussian(sigma=%.4g)" % cfg["sigma_main"],
            sieve_vector_count=int(N),
            seeds=SEEDS, fpylll_seed=FPLLL_SEED,
            sieve_threads=1,
            lll_seconds=round(t_lll, 3),
            sieve_seconds=round(t_sieve, 3),
            total_wall_seconds=None,
            peak_rss_mb=round(
                resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1),
            memory_cap_gb=args.mem_cap_gb,
        ),
        certificate=cert,
        vector_norms=dict(min=int(norms2.min()), median=float(np.median(norms2)),
                          max=int(norms2.max()), mean=round(float(norms2.mean()), 3)),
        candidates=cand_meta,
        target_summaries=summary_targets,
        environment=env,
        log=log,
    )

    raw_path = os.path.join(args.out_dir, "raw_scores.json")
    res_path = os.path.join(args.out_dir, "results.json")
    if args.smoke:
        raw_path = os.path.join(args.out_dir, "smoke_raw_scores.json")
        res_path = os.path.join(args.out_dir, "smoke_results.json")

    with open(raw_path, "w") as f:
        json.dump(raw, f)
    results["run"]["total_wall_seconds"] = round(time.time() - t_start, 3)
    results["raw_scores_bytes"] = os.path.getsize(raw_path)
    with open(raw_path, "rb") as f:
        results["raw_scores_sha256"] = hashlib.sha256(f.read()).hexdigest()
    with open(res_path, "w") as f:
        json.dump(results, f, indent=2)

    say("wrote %s (%d bytes)" % (raw_path, results["raw_scores_bytes"]))
    say("wrote %s" % res_path)
    say("TOTAL %.1fs" % (time.time() - t_start))


if __name__ == "__main__":
    main()
