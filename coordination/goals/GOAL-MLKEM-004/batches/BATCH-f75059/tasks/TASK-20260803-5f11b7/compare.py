#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TASK-20260803-5f11b7 / BATCH-f75059 (batch 2 of 6) / GOAL-MLKEM-004

Make the comparison against the dual-attack cost law WELL-POSED, then run it.

This script MEASURES and RECORDS. It states no conclusion about whether the
independence heuristic is validated or refuted; that judgement belongs to the
Reviewer and the Coordinator (agents/executor.md responsibility 13).

TOY SCALE. m=35, n=25, d=60, q=127 against FIPS 203's n=256k, q=3329. Nothing
computed here is a statement about FIPS 203 dimensions or about ML-KEM's
security. No attack is implemented, no break is claimed, no speedup is claimed.

------------------------------------------------------------------------------
WHAT IS COMPUTED, SECTION BY SECTION
------------------------------------------------------------------------------
S1  P1b  KNOWN-ANSWER CONTROL on `estimator.lwe_dual.matzov` itself, the
         callable four batches of the predecessor campaign argued about and
         none ever covered (inherited CTRL-RT-4 / CTRL-RT-6). Includes an
         explicit CALLABLE-IDENTITY check: `estimator/lwe.py:13` binds the
         public name `LWE.dual_hybrid` to the MATZOV instance, while
         `estimator.lwe_dual.dual_hybrid` is a different attack (DualHybrid,
         [INDOCRYPT:EspJouKha20]).

S2  P1   WELL-POSEDNESS. Exhaustively enumerates every admissible
         (k_enum, k_fft) and tests the two requirements the measured design
         imposes. Reports the exact tuple if one exists, or reports that the
         admissible set is EMPTY. Also reproduces, under contract, the spread
         of N_pred across admissible readings of the log-term.

S3       Instance, LLL, bgj1 sieve, dual-membership certificate re-verified by
         integer arithmetic independent of g6k, plus an independent algebraic
         re-derivation tying the scores to the certificate.

S4  P3   vectors.json: x and y for every sieve vector.

S5  P3   Per-candidate-GROUP statistics with mean +/- sd over >= 1000 fresh
         error draws. NEVER pooled across groups.

S6       INGREDIENT 1 of the law: the per-vector advantage
         exp(-2 pi^2 sigma_e^2 ||x||^2 / q^2), tested across ||x||^2 deciles.

S7       INGREDIENT 2 of the law: the iid noise model for wrong candidates,
         sd = sqrt(Var(score)/N), per candidate group.

S8  P2   NULLS. Every null names, in the artifact, the OBJECT whose removal it
         tests (corrective rule from DEC-20260803-d810d0 PD-1).

S9       Replicate instances (inherited CTRL-RT-5), to bound the one uncertainty
         neither batch-1 reviewer could bound: instance-to-instance variation.

------------------------------------------------------------------------------
CONVENTIONS
------------------------------------------------------------------------------
LWE (row convention):  A in Z_q^{m x n},  b = A s + e mod q.
Dual lattice, d = m+n: L = {(x,y) in Z^m x Z^n : y == A^T x (mod q)}
Score of vector i against candidate s':
    t_i(s') = centre_mod(x_i . b - y_i . s', q),  score_i = cos(2 pi t_i / q)
Identity used for the fast path (re-verified in S3):
    x_i . b - y_i . s'  ==  x_i . e + y_i . (s - s')   (mod q)
"""

import argparse
import hashlib
import json
import os
import platform
import resource
import subprocess
import sys
import time

import numpy as np

from fpylll import IntegerMatrix, LLL, FPLLL
from g6k import Siever, SieverParams

SCRIPT_VERSION = "2.0.0"
TWOPI = 2.0 * np.pi


# ===========================================================================
# helpers
# ===========================================================================
def centered_binomial(rng, eta, size):
    a = rng.integers(0, 2, size=(size, eta), dtype=np.int64).sum(axis=1)
    b = rng.integers(0, 2, size=(size, eta), dtype=np.int64).sum(axis=1)
    return (a - b).astype(np.int64)


def rounded_gaussian(rng, sigma, size):
    return np.rint(rng.normal(0.0, sigma, size=size)).astype(np.int64)


def center_mod(v, q):
    r = np.mod(v, q)
    return np.where(r > q // 2, r - q, r).astype(np.int64)


def to_intmat(M):
    A = IntegerMatrix(M.shape[0], M.shape[1])
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            A[i, j] = int(M[i, j])
    return A


def from_intmat(A):
    return np.array([[A[i, j] for j in range(A.ncols)] for i in range(A.nrows)],
                    dtype=np.int64)


def ms(a):
    """mean +/- sd of a 1-D sample, reported with its own sample size."""
    a = np.asarray(a, dtype=float)
    return dict(mean=float(a.mean()),
                sd=float(a.std(ddof=1)) if a.size > 1 else None,
                n_draws=int(a.size))


def build_dual_basis(A, q, m, n):
    d = m + n
    B = np.zeros((d, d), dtype=np.int64)
    B[:m, :m] = np.eye(m, dtype=np.int64)
    B[:m, m:] = A
    B[m:, m:] = q * np.eye(n, dtype=np.int64)
    return B


def run_sieve(A, q, m, n, sieve_name, fpylll_seed, sieve_seed):
    """LLL + g6k sieve on the dual lattice; returns (X, Y, timings, basis)."""
    d = m + n
    Bnp = build_dual_basis(A, q, m, n)
    Bfp = to_intmat(Bnp)
    FPLLL.set_random_seed(fpylll_seed)
    t0 = time.time()
    Bred = LLL.reduction(Bfp)
    t_lll = time.time() - t0
    g = Siever(Bred, SieverParams(threads=1), seed=sieve_seed)
    g.initialize_local(0, 0, d)
    t0 = time.time()
    getattr(g, sieve_name)()
    t_sieve = time.time() - t0
    coeffs = np.array([tuple(v) for v in g.itervalues()], dtype=np.int64)
    Bused = from_intmat(g.M.B)
    V = coeffs.dot(Bused)
    return V[:, :m], V[:, m:], V, dict(lll_seconds=round(t_lll, 3),
                                       sieve_seconds=round(t_sieve, 3))


def make_candidates(rng, s, q, n, eta, n_unif, n_sdist, n_near):
    """(label, group, vector). Group 'reference_zero' is reported separately and
    is never pooled into the three wrong-candidate groups."""
    cands = [("correct", "correct", s.copy())]
    for i in range(n_unif):
        cands.append(("uniform_%02d" % i, "uniform",
                      rng.integers(0, q, size=n, dtype=np.int64)))
    for i in range(n_sdist):
        cands.append(("secretdist_%02d" % i, "secret_distribution",
                      centered_binomial(rng, eta, n)))
    for i in range(n_near):
        c = s.copy()
        c[i % n] = c[i % n] + 1
        cands.append(("nearmiss_%02d" % i, "near_miss", c))
    # reference candidate for the "pure distinguisher" reading of the law
    # (phase = x.b, i.e. no candidate subtraction at all -- see S2 reading R-A)
    cands.append(("zero_vector", "reference_zero", np.zeros(n, dtype=np.int64)))
    return cands


# ===========================================================================
# S1 -- P1b: known-answer control on estimator.lwe_dual.matzov
# ===========================================================================
def s1_known_answer_control(cfg, say, estimator_path, kyber_timeout):
    out = dict(
        purpose="Inherited CTRL-RT-4 / CTRL-RT-6: a known-answer control on the "
                "estimator callable itself, BEFORE its output is differenced "
                "against anything. Four batches of GOAL-MLKEM-003 argued about "
                "this callable and none covered it.",
        checks=[], passed=None)
    sys.path.insert(0, estimator_path)
    import estimator as est
    from estimator import LWE, ND
    from estimator import lwe_dual as ld
    from estimator.lwe_parameters import LWEParameters
    from estimator.reduction import ReductionCost

    rev = subprocess.run(["git", "-C", estimator_path, "rev-parse", "HEAD"],
                         capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", estimator_path, "status", "--porcelain"],
                           capture_output=True, text=True).stdout.strip()
    out["estimator_commit"] = rev
    out["estimator_dirty"] = bool(dirty)
    out["estimator_path"] = estimator_path

    def add(cid, desc, expected, observed, ok, note=None):
        out["checks"].append(dict(id=cid, description=desc, expected=expected,
                                  observed=observed, passed=bool(ok), note=note))
        say("  KA %-6s %-58s %s" % (cid, desc[:58], "PASS" if ok else "FAIL"))

    # ---- KA-0  CALLABLE IDENTITY -----------------------------------------
    same = LWE.dual_hybrid is ld.matzov
    is_matzov = type(LWE.dual_hybrid).__name__ == "MATZOV"
    mod_dh_is_func = callable(getattr(ld, "dual_hybrid", None)) and \
        type(getattr(ld, "dual_hybrid")).__name__ == "function"
    distinct = LWE.dual_hybrid is not getattr(ld, "dual_hybrid", None)
    add("KA-0a", "public LWE.dual_hybrid IS estimator.lwe_dual.matzov",
        True, same, same,
        "estimator/lwe.py:13 -- `from .lwe_dual import matzov as dual_hybrid`")
    add("KA-0b", "type(LWE.dual_hybrid).__name__ == 'MATZOV'",
        "MATZOV", type(LWE.dual_hybrid).__name__, is_matzov)
    add("KA-0c", "estimator.lwe_dual.dual_hybrid is a DIFFERENT callable",
        "distinct function object (DualHybrid, EspJouKha20)",
        dict(is_function=mod_dh_is_func, distinct_from_public=distinct),
        mod_dh_is_func and distinct,
        "This is the name collision the predecessor campaign argued about: the "
        "module-level `dual_hybrid` in lwe_dual.py wraps DH = DualHybrid(), a "
        "different attack from the MATZOV instance the public name resolves to.")
    add("KA-0d", "matzov.Nf is MATZOV.Nf (bound classmethod identity)",
        True, ld.matzov.Nf == ld.MATZOV.Nf, ld.matzov.Nf == ld.MATZOV.Nf)

    # ---- parameters of the measured design --------------------------------
    m, n, q = cfg["m"], cfg["n"], cfg["q"]
    Xs = ND.CenteredBinomial(cfg["eta_secret"])
    Xe = ND.DiscreteGaussian(cfg["sigma_main"])
    params = LWEParameters(n=n, q=q, Xs=Xs, Xe=Xe, m=m)
    out["params_repr"] = repr(params)
    out["Xs_stddev"] = float(Xs.stddev)
    out["Xe_stddev"] = float(Xe.stddev)

    # ---- KA-1  Hf against an independent reimplementation -----------------
    sd = float(Xs.stddev)
    my_H_bits = (0.5 + np.log(np.sqrt(2 * np.pi) * sd)
                 + np.log(1.0 / np.tanh(np.pi ** 2 * sd ** 2))) / np.log(2.0)
    est_H = float(ld.MATZOV.Hf(Xs))
    ok = abs(my_H_bits - est_H) < 1e-9
    add("KA-1", "MATZOV.Hf == independent numpy reimplementation",
        my_H_bits, est_H, ok,
        "MATZOV.Hf(Xs) = (1/2 + ln(sqrt(2 pi) sigma) + ln(coth(pi^2 sigma^2)))/ln 2")

    # ---- KA-2  Nf against an independent reimplementation on a grid -------
    def my_delta(beta):
        return (beta / (2 * np.pi * np.e) * (np.pi * beta) ** (1.0 / beta)) \
            ** (1.0 / (2.0 * (beta - 1)))

    def my_Nf(m_, beta_bkz, beta_sieve, k_enum, k_fft, p):
        k_lat = n - k_fft - k_enum
        ls = (float(Xe.stddev) ** (m_ / (m_ + k_lat))
              * (float(Xs.stddev) * q) ** (k_lat / (m_ + k_lat))
              * np.sqrt(4 / 3.0) * np.sqrt(beta_sieve / 2 / np.pi / np.e)
              * my_delta(beta_bkz) ** (m_ + k_lat - beta_sieve))
        return (np.exp(4 * (ls * np.pi / q) ** 2)
                * np.exp(k_fft / 3.0 * (float(Xs.stddev) * np.pi / p) ** 2)
                * (k_enum * my_H_bits + k_fft * np.log(p) + np.log(2.0)))

    grid, worst = [], 0.0
    for (mm, bb, bs, ke, kf, pp) in [(35, 45, 41, 0, 0, 2), (35, 60, 50, 5, 5, 3),
                                     (35, 80, 60, 0, 10, 7), (60, 100, 90, 10, 5, 5),
                                     (35, 41, 41, 12, 13, 127), (35, 200, 150, 3, 2, 11)]:
        a = float(ld.MATZOV.Nf(params, mm, bb, bs, ke, kf, pp))
        b_ = float(my_Nf(mm, bb, bs, ke, kf, pp))
        rel = abs(a - b_) / a
        worst = max(worst, rel)
        grid.append(dict(m=mm, beta_bkz=bb, beta_sieve=bs, k_enum=ke, k_fft=kf,
                         p=pp, estimator=a, independent=b_, rel_err=rel))
    out["KA2_grid"] = grid
    add("KA-2", "MATZOV.Nf == independent reimplementation over a 6-point grid",
        "max rel err < 1e-9", worst, worst < 1e-9,
        "independent reimplementation includes an independent deltaf for beta>40, "
        "deltaf(beta) = (beta/(2 pi e) (pi beta)^(1/beta))^(1/(2(beta-1)))")

    # ---- KA-3  p-invariance when k_fft == 0 --------------------------------
    a = float(ld.MATZOV.Nf(params, 35, 60, 60, 0, 0, 2))
    b_ = float(ld.MATZOV.Nf(params, 35, 60, 60, 0, 0, q))
    add("KA-3", "Nf is independent of p when k_fft == 0",
        "Nf(p=2) == Nf(p=q)", dict(p2=a, pq=b_), abs(a - b_) < 1e-12,
        "Known answer by inspection of the formula: with k_fft=0 both p-bearing "
        "terms (k_fft*log p, exp(k_fft/3 (sigma_s pi/p)^2)) vanish. Confirms "
        "OBJ-1: with no FFT sub-block split, p has NO referent in this design.")

    # ---- KA-4  unit audit: Hf is in BITS, log p and log(1/mu) in NATS -------
    ratio = est_H / (my_H_bits * np.log(2.0))
    add("KA-4", "Hf returns BITS while log(p), log(1/mu) are NATURAL logs",
        "Hf == nat_entropy / ln 2, i.e. ratio 1/ln2 = 1.442695",
        dict(Hf_bits=est_H, nat_entropy=my_H_bits * np.log(2.0),
             ratio_bits_over_nats=float(ratio)),
        abs(ratio - 1.0 / np.log(2.0)) < 1e-9,
        "RECORDED OBSERVATION, not a claim that the estimator is wrong: the sum "
        "k_enum*Hf(Xs) + k_fft*log(p) + log(1/mu) adds a term in bits to two "
        "terms in nats. MATZOV.cost's T_guess uses 2**(k_enum*H), which confirms "
        "H is intended in bits. Consequence for this task: any reading of the "
        "log-term that uses k_enum carries an additional factor-ln2 ambiguity "
        "beyond the referent ambiguity of OBJ-1.")

    # ---- KA-5  beta_bkz-invariance when beta_sieve == m + k_lat ------------
    a = float(ld.MATZOV.Nf(params, m, 45, m + n, 0, 0, 2))
    b_ = float(ld.MATZOV.Nf(params, m, 300, m + n, 0, 0, 2))
    add("KA-5", "Nf independent of beta_bkz when beta_sieve == m + k_lat",
        "Nf(beta_bkz=45) == Nf(beta_bkz=300)", dict(b45=a, b300=b_),
        abs(a - b_) / a < 1e-12,
        "Known answer by inspection: the factor deltaf(beta_bkz)^(m+k_lat-beta_sieve) "
        "has exponent 0. This is why the length sub-comparison in S2 is free of "
        "the beta ambiguity: the measured run sieved the FULL d=60 lattice.")

    # ---- KA-6  round trip against the repository's own documented value ----
    ka6 = dict(id="KA-6",
               description="LWE.dual_hybrid(Kyber512, RC.ADPS16) against the "
                           "estimator's own documented value in estimator/lwe.py "
                           "docstring line 55: rop ~ 2^115.5, beta 395, p 5, "
                           "zeta 0, t 40, beta' 395",
               expected=dict(log2_rop=115.5, beta=395, p=5, zeta=0, t=40),
               observed=None, passed=None, note=None)
    try:
        from estimator import schemes
        from estimator.reduction import RC
        t0 = time.time()
        cost = ld.matzov(schemes.Kyber512, red_cost_model=RC.ADPS16)
        el = time.time() - t0
        obs = dict(log2_rop=float(np.log2(float(cost["rop"]))),
                   beta=int(cost["beta"]), p=int(cost["p"]),
                   zeta=int(cost["zeta"]), t=int(cost["t"]),
                   seconds=round(el, 1))
        ka6["observed"] = obs
        ka6["passed"] = bool(abs(obs["log2_rop"] - 115.5) < 0.1
                             and obs["beta"] == 395 and obs["p"] == 5
                             and obs["zeta"] == 0 and obs["t"] == 40)
        ka6["note"] = ("Strongest form of the control: the exact public callable "
                       "reproduces a value documented in the pinned repository "
                       "itself, at cryptographic parameters.")
    except Exception as ex:                                  # pragma: no cover
        ka6["passed"] = None
        ka6["note"] = ("NOT RUN / FAILED, recorded rather than omitted: %s: %s"
                       % (type(ex).__name__, ex))
    out["checks"].append(ka6)
    say("  KA %-6s %-58s %s" % ("KA-6", "Kyber512 round trip vs repo's own doctest",
                                {True: "PASS", False: "FAIL", None: "NOT RUN"}[ka6["passed"]]))

    dets = [c["passed"] for c in out["checks"] if c["passed"] is not None]
    out["passed"] = bool(all(dets))
    out["n_checks_run"] = len(dets)
    out["n_checks_not_run"] = len(out["checks"]) - len(dets)
    return out, (est, LWE, ND, ld, params, my_H_bits)


# ===========================================================================
# S2 -- P1: well-posedness
# ===========================================================================
def s2_wellposedness(cfg, say, ld, params, my_H_bits, meas, np_):
    m, n, q = cfg["m"], cfg["n"], cfg["q"]
    d = m + n
    out = dict(
        question="Does an (m, k_enum, k_fft, p, beta_bkz, beta_sieve) tuple exist "
                 "that makes MATZOV.Nf well-posed on the measured design?",
        design_facts=dict(
            lwe_samples_m=m, secret_dimension_n=n, sieved_lattice_dimension=d,
            sieve="LLL then g6k bgj1_sieve over the FULL d=%d dual lattice" % d,
            candidates_differ_on_coordinates=n,
            fft_sub_block_split=False,
            note="The design scores candidate secrets that differ from s on any "
                 "of all n coordinates, and it obtains its vectors from a sieve "
                 "run on the full (m+n)-dimensional dual lattice, in which the "
                 "y-part of every vector is short."),
    )

    # --- the two requirements the measured design imposes on the tuple ------
    # R1: MATZOV's reduced/sieved lattice has dimension m + k_lat. The measured
    #     lattice has dimension m + n. Hence k_lat = n, i.e. k_enum + k_fft = 0.
    # R2: MATZOV guesses k_enum coordinates and FFTs k_fft of them; the measured
    #     design varies candidates over all n coordinates, so k_enum + k_fft = n.
    admissible = []
    for k_enum in range(0, n + 1):
        for k_fft in range(0, n - k_enum + 1):
            k_lat = n - k_enum - k_fft
            r1 = (m + k_lat == d)                # sieved dimension matches
            r2 = (k_enum + k_fft == n)           # guessed coordinates match
            if r1 and r2:
                admissible.append(dict(k_enum=k_enum, k_fft=k_fft, k_lat=k_lat))
    out["admissible_tuples_enumerated"] = (n + 1) * (n + 2) // 2
    out["admissible_tuples_found"] = admissible
    out["tuple_exists"] = bool(admissible)
    out["impossibility_argument"] = (
        "MATZOV.Nf line 540 fixes k_lat = n - k_fft - k_enum, so "
        "k_lat + k_fft + k_enum = n identically. Requirement R1 (the sieved "
        "lattice has dimension m + k_lat, and the measured one has dimension "
        "m + n) forces k_lat = n, hence k_enum + k_fft = 0. Requirement R2 "
        "(candidates are enumerated over all n secret coordinates) forces "
        "k_enum + k_fft = n = %d. Both hold only if n = 0. The admissible set "
        "is EMPTY, verified by exhaustive enumeration over all %d integer pairs "
        "(k_enum, k_fft) with k_enum + k_fft <= n." % (n, (n + 1) * (n + 2) // 2))

    # --- what IS pinned by the run, and what is not -------------------------
    out["pinned_by_the_run"] = dict(
        m=m,
        beta_sieve=d,
        beta_bkz="IRRELEVANT (not a free choice, and not a fit): the only place "
                 "beta_bkz enters Nf is deltaf(beta_bkz)^(m + k_lat - beta_sieve), "
                 "whose exponent is 0 when beta_sieve = m + k_lat = d = %d. "
                 "Verified as known-answer control KA-5." % d,
        note="These three ARE determined by the measured run. The obstruction is "
             "confined to (k_enum, k_fft, p), and through k_lat it then "
             "contaminates the length model too -- see 'sub_comparison_C'.")
    out["p_has_no_referent"] = (
        "The design performs no FFT sub-block split, so k_fft = 0 under any "
        "reading that respects the vector family, and then Nf is identically "
        "independent of p (known-answer control KA-3). The factor "
        "exp(k_fft/3 (sigma_s pi/p)^2) -- which exists precisely to charge the "
        "adjacent-FFT-bin penalty, i.e. the very near-miss phenomenon batch 1 "
        "observed -- is therefore identically 1 and untestable here.")

    # --- reproduce the factor-29 spread under contract ----------------------
    sd_s = float(params.Xs.stddev)
    readings = []

    def log_term(k_enum, k_fft, p, label, why):
        val = k_enum * my_H_bits + (k_fft * np.log(p) if k_fft else 0.0) + np.log(2.0)
        readings.append(dict(label=label, rationale=why, k_enum=k_enum,
                             k_fft=k_fft, p=p, log_term=float(val)))
        return val

    log_term(0, 0, 2, "L1 pure distinguisher",
             "k_enum=k_fft=0: the law asks only for advantage mu=0.5, no candidate axis")
    L2 = np.log(2.0) + np.log(meas["n_candidates_scored"])
    readings.append(dict(label="L2 union bound over the tested candidates",
                         rationale="log(1/mu) + log(#candidates); the reading "
                                   "RT-20260803-4064e1 used",
                         k_enum=None, k_fft=None, p=None, log_term=float(L2)))
    log_term(n, 0, 2, "L3 whole secret enumerated",
             "k_enum=n: every candidate coordinate guessed, no FFT")
    log_term(0, n, q, "L4 whole secret FFT'd at p=q",
             "k_fft=n, p=q: the largest admissible reading")

    # prefactor readings
    ax_meas = meas["a_x_measured"]
    pre = []
    ls_lat_n = float(ld.MATZOV.Nf(params, m, 60, d, 0, 0, 2)) / np.log(2.0)
    # recompute lsigma_s explicitly for both k_lat readings
    def lsigma(k_lat, beta_sieve, beta_bkz=60):
        from estimator.reduction import ReductionCost
        dl = float(ReductionCost.delta(beta_bkz))
        return (float(params.Xe.stddev) ** (m / (m + k_lat))
                * (sd_s * q) ** (k_lat / (m + k_lat))
                * np.sqrt(4 / 3.0) * np.sqrt(beta_sieve / 2 / np.pi / np.e)
                * dl ** (m + k_lat - beta_sieve))
    ls_A = lsigma(n, d)
    ls_B = lsigma(0, m)
    pre.append(dict(label="P-A modeled length, k_lat=n, beta_sieve=d=%d" % d,
                    lsigma_s=float(ls_A),
                    prefactor=float(np.exp(4 * (ls_A * np.pi / q) ** 2))))
    pre.append(dict(label="P-B modeled length, k_lat=0, beta_sieve=m=%d" % m,
                    lsigma_s=float(ls_B),
                    prefactor=float(np.exp(4 * (ls_B * np.pi / q) ** 2))))
    pre.append(dict(label="P-C MEASURED length (a_x from the sieve database)",
                    lsigma_s=float(q * np.sqrt(ax_meas / 2.0) / np.pi),
                    prefactor=float(np.exp(2 * ax_meas))))
    out["log_term_readings"] = readings
    out["prefactor_readings"] = pre

    cells = []
    for r in readings:
        for pf in pre:
            cells.append(dict(log_term=r["label"], prefactor=pf["label"],
                              N_pred=float(pf["prefactor"] * r["log_term"])))
    vals = [c["N_pred"] for c in cells]
    out["N_pred_grid"] = cells
    out["N_pred_min"] = float(min(vals))
    out["N_pred_max"] = float(max(vals))
    out["N_pred_spread_factor"] = float(max(vals) / min(vals))
    out["N_pred_RT_reproduction"] = dict(
        note="RT-20260803-4064e1 OBJ-1 reported 24.9 to 723 across ITS admissible "
             "readings, both using the measured-length prefactor. Reproduced here "
             "under contract with the pinned callable.",
        RT_low_reproduced=float(np.exp(2 * ax_meas) * L2),
        RT_high_reproduced=float(np.exp(2 * ax_meas)
                                 * (n * np.log(q) + np.log(2.0))))

    # --- the one sub-comparison that IS well-posed --------------------------
    out["sub_comparison_C"] = dict(
        name="the LENGTH model, under the reading that matches the vector family",
        why_well_posed=(
            "Under reading R-A (k_lat = n, k_enum = k_fft = 0) the vector family "
            "Nf describes IS the measured one: a sieve over the m+k_lat = d = %d "
            "dimensional dual lattice. beta_sieve = %d is a fact of the run, not a "
            "fit, and beta_bkz drops out (KA-5). So lsigma_s is fully determined "
            "with no free parameter." % (d, d)),
        what_is_still_not_well_posed=(
            "R-A's log-term is log(1/mu) alone: under R-A no candidate is "
            "enumerated, so the measurement's candidate axis has no counterpart. "
            "This sub-comparison therefore tests the LENGTH/advantage half of the "
            "law only, which is exactly INGREDIENT 1."),
        modeled_lsigma_s=float(ls_A),
        modeled_per_vector_advantage=float(np.exp(-2 * (ls_A * np.pi / q) ** 2)),
        measurement_reference="S6 / S5 reference_zero group")
    out["answer"] = ("NO SUCH TUPLE EXISTS. The admissible set is empty by "
                     "exhaustive enumeration. (m, beta_sieve, beta_bkz) are pinned "
                     "by the run; (k_enum, k_fft, p) admit no consistent "
                     "assignment. The comparison is therefore made against the "
                     "law's two SEPARABLE INGREDIENTS.")
    return out


# ===========================================================================
# scoring core
# ===========================================================================
def score_means_over_draws(X, Ydiff_phase, q, rng, sigma, D, chunk=100,
                           decile_masks=None, correct_col=0):
    """For each of D fresh error draws, the per-candidate MEAN score over the
    whole database. Ydiff_phase is (K, N): the precomputed y_i.(s - c_j) mod q.

    Returns means (D, K); decile means (D, n_dec) for the correct candidate;
    per-vector score variance per draw (D,) for the correct candidate."""
    N, m = X.shape
    K = Ydiff_phase.shape[0]
    means = np.empty((D, K), dtype=np.float64)
    ndec = len(decile_masks) if decile_masks is not None else 0
    dec = np.empty((D, ndec), dtype=np.float64) if ndec else None
    pvvar = np.empty(D, dtype=np.float64)
    done = 0
    while done < D:
        b = min(chunk, D - done)
        E = np.rint(rng.normal(0.0, sigma, size=(m, b))).astype(np.int64)
        U = (X.dot(E)) % q                                     # (N, b)
        for j in range(K):
            P = (U + Ydiff_phase[j][:, None]) % q
            S = np.cos(TWOPI * P / q)
            means[done:done + b, j] = S.mean(axis=0)
            if j == correct_col:
                pvvar[done:done + b] = S.var(axis=0, ddof=1)
                if ndec:
                    for k, msk in enumerate(decile_masks):
                        dec[done:done + b, k] = S[msk].mean(axis=0)
        done += b
    return means, dec, pvvar


def surrogate_means_over_draws(Xs_float, q, rng, sigma, D, chunk=200):
    """Correct-secret statistic for a surrogate vector family (no y-part):
    mean_i cos(2 pi (x'_i . e)/q), for D fresh error draws."""
    N, m = Xs_float.shape
    means = np.empty(D, dtype=np.float64)
    pvvar = np.empty(D, dtype=np.float64)
    done = 0
    while done < D:
        b = min(chunk, D - done)
        E = np.rint(rng.normal(0.0, sigma, size=(m, b))).astype(np.float64)
        U = Xs_float.dot(E)
        S = np.cos(TWOPI * U / q)
        means[done:done + b] = S.mean(axis=0)
        pvvar[done:done + b] = S.var(axis=0, ddof=1)
        done += b
    return means, pvvar


def random_directions(rng, norms, m):
    G = rng.normal(0.0, 1.0, size=(norms.size, m))
    G /= np.linalg.norm(G, axis=1, keepdims=True)
    return G * norms[:, None]


# ===========================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--out-dir", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--mem-cap-gb", type=float, default=6.0)
    ap.add_argument("--estimator-path", default="/tmp/le")
    ap.add_argument("--max-seconds", type=float, default=1500.0,
                    help="soft guard: replicate instances stop when exceeded")
    args = ap.parse_args()

    t_start = time.time()
    if args.mem_cap_gb > 0:
        cap = int(args.mem_cap_gb * (1 << 30))
        resource.setrlimit(resource.RLIMIT_AS, (cap, cap))

    if args.smoke:
        cfg = dict(m=24, n=16, q=127, sieve="bgj1_sieve", eta_secret=2,
                   sigma_main=2.0, n_unif=4, n_sdist=2, n_near=2,
                   draws_primary=60, draws_null=60, draws_curve=40,
                   n_replicates=1, draws_replicate=30,
                   m_sweep=[24, 48], N_sweep=[500, 1000])
    else:
        cfg = dict(m=35, n=25, q=127, sieve="bgj1_sieve", eta_secret=2,
                   sigma_main=2.0, n_unif=16, n_sdist=8, n_near=8,
                   draws_primary=2000, draws_null=1000, draws_curve=1000,
                   n_replicates=9, draws_replicate=500,
                   m_sweep=[35, 70, 140, 280], N_sweep=[1000, 5000, 17919, 60000])

    SEEDS = dict(
        instance=20260803001,       # A, s   (batch-1 values: same instance)
        candidates=20260803002,     # wrong-candidate draws (batch-1 values)
        sieve=0x6D4C4B454D,         # g6k Siever RNG (batch-1 value)
        fpylll=20260803005,         # fpylll RNG (batch-1 value)
        error_draws=20260803201,    # the >=1000 fresh error draws (S5-S7)
        null_target=20260803202,    # uniform b for the target-null
        surrogate=20260803203,      # random directions for the vector-null
        iid_null=20260803204,       # independent per-vector errors
        sweep=20260803205,          # m-sweep and N-sweep surrogates
        replicates=20260803206,     # replicate instance seeds
    )

    m, n, q = cfg["m"], cfg["n"], cfg["q"]
    d = m + n
    sigma = cfg["sigma_main"]
    log = []

    def say(msg):
        line = "[%7.1fs] %s" % (time.time() - t_start, msg)
        print(line, flush=True)
        log.append(line)

    say("compare.py %s  smoke=%s" % (SCRIPT_VERSION, args.smoke))
    say("config m=%d n=%d d=%d q=%d sieve=%s sigma_e=%.4g eta_s=%d"
        % (m, n, d, q, cfg["sieve"], sigma, cfg["eta_secret"]))
    say("seeds %s" % SEEDS)
    say("NOTE: the instance/candidate/sieve/fpylll seeds are batch 1's, so the "
        "primary database is the SAME 17,919-vector object BATCH-d2a728 measured "
        "and both batch-1 reviewers reconstructed. This is deliberate: it makes "
        "the batch-2 statistics directly comparable and gives a free "
        "reproduction check of the batch-1 database.")

    # =======================================================================
    say("S3  building instance, LLL, sieve")
    rng_inst = np.random.default_rng(SEEDS["instance"])
    A = rng_inst.integers(0, q, size=(m, n), dtype=np.int64)
    s = centered_binomial(rng_inst, cfg["eta_secret"], n)
    e_batch1 = rounded_gaussian(rng_inst, sigma, m)     # batch 1's realisation

    X, Y, V, tim = run_sieve(A, q, m, n, cfg["sieve"], SEEDS["fpylll"], SEEDS["sieve"])
    N = X.shape[0]
    say("SIEVE %s dim=%d: %d vectors  (LLL %.2fs, sieve %.2fs)"
        % (cfg["sieve"], d, N, tim["lll_seconds"], tim["sieve_seconds"]))

    # ---- certificate, re-verified independently of g6k ---------------------
    t0 = time.time()
    resid = np.mod(X.dot(A) - Y, q)
    n_bad = int(np.count_nonzero(resid))
    n_zero = int(np.count_nonzero(np.all(V == 0, axis=1)))
    n_dup_y = int(N - len(set(map(tuple, Y.tolist()))))
    cert = dict(
        kind="lattice_membership",
        statement="every emitted vector v=(x,y) satisfies y == A^T x (mod q), "
                  "i.e. lies in the dual lattice L",
        checked_vectors=int(N), checked_entries=int(N * n),
        violating_entries=n_bad, all_zero_vectors=n_zero,
        duplicate_y_parts=n_dup_y,
        verified=bool(n_bad == 0 and n_zero == 0),
        method="integer arithmetic on numpy int64 from A and the reconstructed "
               "lattice vectors, independent of g6k's internal representation",
        solve_claim_certificate="none -- this run claims no discrete-log solve "
                                "and no factor-base relation. certificate.kind "
                                "is lattice_membership only; it certifies the "
                                "vectors, not any inference from their scores.",
        check_seconds=round(time.time() - t0, 3))
    say("CERTIFICATE lattice_membership: violating_entries=%d zero_vectors=%d "
        "duplicate_y=%d verified=%s" % (n_bad, n_zero, n_dup_y, cert["verified"]))
    if not cert["verified"]:
        say("CERTIFICATE FAILED -- aborting before any score is reported")
        json.dump(dict(certificate=cert, log=log, aborted=True),
                  open(os.path.join(args.out_dir, "results.json"), "w"), indent=2)
        sys.exit(3)

    xn2 = (X * X).sum(axis=1)
    yn2 = (Y * Y).sum(axis=1)
    vn2 = (V * V).sum(axis=1)

    # ---- candidates --------------------------------------------------------
    rng_c = np.random.default_rng(SEEDS["candidates"])
    cands = make_candidates(rng_c, s, q, n, cfg["eta_secret"],
                            cfg["n_unif"], cfg["n_sdist"], cfg["n_near"])
    labels = [c[0] for c in cands]
    groups = [c[1] for c in cands]
    C = np.array([c[2] for c in cands], dtype=np.int64)
    K = len(cands)
    coincid = [labels[i] for i in range(1, K) if np.array_equal(C[i], s)]
    say("candidates: %d (1 correct + %d wrong + 1 reference_zero); "
        "coincidences_with_secret=%s"
        % (K, K - 2, coincid if coincid else "none"))

    # phase offsets  y_i . (s - c_j)  mod q
    Dphase = np.mod(Y.dot((s[None, :] - C).T), q).T.astype(np.int64)   # (K, N)

    # ---- independent algebraic re-derivation tying scores to the certificate
    t_direct = center_mod(X.dot(np.mod(A.dot(s) + e_batch1, q))[:, None]
                          - Y.dot(C.T), q).T
    t_fast = center_mod((X.dot(e_batch1)[None, :] + Dphase), q)
    identity_ok = bool(np.array_equal(t_direct, t_fast))
    say("identity check  x.b - y.c == x.e + y.(s-c) (mod q) for all %d x %d: %s"
        % (K, N, identity_ok))
    if not identity_ok:
        say("IDENTITY CHECK FAILED -- aborting")
        sys.exit(4)

    # =======================================================================
    say("S1  P1b known-answer control on estimator.lwe_dual.matzov")
    s1, (est, LWE, ND, ld, params, my_H_bits) = s1_known_answer_control(
        cfg, say, args.estimator_path, 600)
    say("S1  known-answer control: %d checks run, %d not run, all_passed=%s"
        % (s1["n_checks_run"], s1["n_checks_not_run"], s1["passed"]))

    # =======================================================================
    say("S5  per-candidate-group statistics over %d fresh error draws"
        % cfg["draws_primary"])
    order = np.argsort(xn2, kind="stable")
    n_dec = 10 if not args.smoke else 4
    dec_masks, dec_info = [], []
    for k in range(n_dec):
        sel = order[k * N // n_dec:(k + 1) * N // n_dec]
        msk = np.zeros(N, dtype=bool); msk[sel] = True
        dec_masks.append(msk)
        dec_info.append(dict(decile=k + 1, count=int(msk.sum()),
                             xnorm2_min=int(xn2[sel].min()),
                             xnorm2_max=int(xn2[sel].max()),
                             xnorm2_mean=float(xn2[sel].mean()),
                             predicted_advantage=float(
                                 np.mean(np.exp(-2 * np.pi ** 2 * sigma ** 2
                                                * xn2[sel] / q ** 2)))))
    rng_e = np.random.default_rng(SEEDS["error_draws"])
    means, decm, pvvar = score_means_over_draws(
        X, Dphase, q, rng_e, sigma, cfg["draws_primary"],
        decile_masks=dec_masks, correct_col=0)
    say("S5  scoring done")

    gidx = {g: [i for i in range(K) if groups[i] == g] for g in set(groups)}
    a_x_meas = float(2 * np.pi ** 2 * sigma ** 2 * xn2.mean() / q ** 2)
    a_y_meas = float(2 * np.pi ** 2 * 1.0 * yn2.mean() / q ** 2)

    # per-group statistics, NEVER pooled
    per_group = {}
    for g, idxs in gidx.items():
        gm = means[:, idxs]                      # (D, |g|)
        per_group[g] = dict(
            n_candidates=len(idxs),
            candidate_labels=[labels[i] for i in idxs],
            group_mean_score=ms(gm.mean(axis=1)),
            per_candidate_mean_score={
                labels[i]: ms(means[:, i]) for i in idxs},
            spread_across_candidates_within_draw=(
                ms(gm.std(axis=1, ddof=1)) if len(idxs) > 1 else None),
            P_correct_beats_every_member_of_group=float(
                np.mean(np.all(means[:, [0]] > gm, axis=1))) if g != "correct" else None,
            n_draws=int(cfg["draws_primary"]))

    # correct vs each wrong group: paired difference with its own error bar
    paired = {}
    for g in ["uniform", "secret_distribution", "near_miss"]:
        if g not in gidx:
            continue
        gm = means[:, gidx[g]]
        paired[g] = dict(
            paired_delta_correct_minus_group_mean=ms(means[:, 0] - gm.mean(axis=1)),
            paired_delta_correct_minus_BEST_member=ms(means[:, 0] - gm.max(axis=1)),
            P_correct_first_within_group=float(np.mean(means[:, 0] > gm.max(axis=1))),
            rank_of_correct_within_group=ms(1 + (gm > means[:, [0]]).sum(axis=1)),
            n_draws=int(cfg["draws_primary"]))

    # where batch 1's single realisation sits
    t1 = center_mod(X.dot(e_batch1)[None, :] + Dphase, q)
    b1_means = np.cos(TWOPI * t1 / q).mean(axis=1)
    batch1_position = {}
    for i in range(K):
        mu_, sd_ = means[:, i].mean(), means[:, i].std(ddof=1)
        batch1_position[labels[i]] = dict(
            batch1_single_draw=float(b1_means[i]),
            resampled_mean=float(mu_), resampled_sd=float(sd_),
            z_of_batch1_draw=float((b1_means[i] - mu_) / sd_) if sd_ > 0 else None)

    # =======================================================================
    say("S6  ingredient 1 -- per-vector advantage law across ||x||^2 deciles")
    dec_rows = []
    global_ratio = means[:, 0] / np.mean(
        np.exp(-2 * np.pi ** 2 * sigma ** 2 * xn2 / q ** 2))
    for k in range(n_dec):
        pred = dec_info[k]["predicted_advantage"]
        meas_k = decm[:, k]
        ratio = meas_k / pred
        shape = ratio / global_ratio        # common-mode removed
        dec_rows.append(dict(
            **dec_info[k],
            measured=ms(meas_k), ratio_measured_over_predicted=ms(ratio),
            shape_ratio_common_mode_removed=ms(shape)))
    xs = np.array([r["xnorm2_mean"] for r in dec_rows])
    rr = np.array([r["shape_ratio_common_mode_removed"]["mean"] for r in dec_rows])
    ing1 = dict(
        law="per-vector advantage  E_e[cos(2 pi x.e/q)] = exp(-2 pi^2 sigma_e^2 ||x||^2 / q^2)",
        law_source="MATZOV.Nf's exponential factor exp(4 (l sigma pi/q)^2) is "
                   "1/advantage^2 with advantage = exp(-2 (l sigma pi/q)^2); this "
                   "is the per-vector half of the law, and it is separable from "
                   "the log-term that has no referent here (S2).",
        deciles=dec_rows,
        xnorm2_range_factor=float(xs.max() / xs.min()),
        global_ratio=ms(global_ratio),
        shape_trend_corr_with_xnorm2=float(np.corrcoef(xs, rr)[0, 1]),
        shape_ratio_min=float(rr.min()), shape_ratio_max=float(rr.max()),
        n_draws=int(cfg["draws_primary"]))

    # sub-comparison C: modeled length vs measured, on the reference_zero group
    zi = labels.index("zero_vector")
    var_phase_meas = float(sigma ** 2 * xn2.mean() + 1.0 * yn2.mean())
    ing1["sub_comparison_C_length_model"] = dict(
        note="Well-posed piece identified in S2. MODELED quantities are labelled; "
             "MEASURED quantities are labelled.",
        modeled_lsigma_s=None,           # filled from S2 below
        measured_effective_lsigma_s=float(np.sqrt(var_phase_meas)),
        measured_reference_zero_mean_score=ms(means[:, zi]),
        measured_mean_xnorm2=float(xn2.mean()),
        measured_mean_ynorm2=float(yn2.mean()),
        measured_mean_vnorm2=float(vn2.mean()))

    # =======================================================================
    say("S7  ingredient 2 -- iid noise model for wrong candidates, per group")
    var_uniform_phase = 0.5          # Var(cos(uniform phase)) = 1/2
    ing2 = dict(
        law="wrong-candidate mean scores are the average of N independent "
            "contributions, so sd = sqrt(Var(score)/N); for a candidate whose "
            "phase is uniform mod q this is sqrt(1/(2N)).",
        N=int(N),
        iid_sd_prediction_uniform_phase=float(np.sqrt(var_uniform_phase / N)),
        groups={})
    for g in ["uniform", "secret_distribution", "near_miss"]:
        if g not in gidx:
            continue
        gm = means[:, gidx[g]]
        sd_across = gm.std(axis=1, ddof=1)
        ing2["groups"][g] = dict(
            n_candidates=len(gidx[g]),
            mean_of_group_mean_scores=ms(gm.mean(axis=1)),
            sd_across_candidates_within_draw=ms(sd_across),
            ratio_to_iid_prediction=ms(sd_across / np.sqrt(var_uniform_phase / N)),
            sd_of_one_candidate_over_draws_averaged_across_candidates=dict(
                mean=float(np.mean([means[:, i].std(ddof=1) for i in gidx[g]])),
                spread_across_candidates=float(
                    np.std([means[:, i].std(ddof=1) for i in gidx[g]], ddof=1))
                if len(gidx[g]) > 1 else None,
                n_candidates=len(gidx[g]), n_draws=int(cfg["draws_primary"])),
            n_draws=int(cfg["draws_primary"]))
    ing2["note_on_offsets"] = (
        "The secret_distribution and near_miss groups are NOT centred at 0: "
        "their phases retain y.(s-c) with s-c small, so exp(-a_y)-type retention "
        "applies. a_y (measured) = %.4f, exp(-a_y) = %.4f."
        % (a_y_meas, float(np.exp(-a_y_meas))))

    # =======================================================================
    say("S8  P2 nulls -- each names the object whose removal it tests")
    nulls = []

    # ---- NULL-V : the VECTOR null (the one batch 1 did not run) ------------
    rng_s = np.random.default_rng(SEEDS["surrogate"])
    Xsur = random_directions(rng_s, np.sqrt(xn2.astype(float)), m)
    rng_sv = np.random.default_rng(SEEDS["error_draws"] + 1)   # PAIRED: identical error sequence to the sieve-database arm
    sur_means, sur_pv = surrogate_means_over_draws(Xsur, q, rng_sv, sigma,
                                                   cfg["draws_null"])
    rng_db = np.random.default_rng(SEEDS["error_draws"] + 1)
    db_means, db_pv = surrogate_means_over_draws(X.astype(float), q, rng_db,
                                                 sigma, cfg["draws_null"])

    def neff(mean_arr, pv_arr, Nv):
        sd = float(np.std(mean_arr, ddof=1))
        pv = float(np.mean(pv_arr))
        return dict(mean=float(np.mean(mean_arr)), sd=sd,
                    per_vector_variance=pv,
                    iid_sd_prediction=float(np.sqrt(pv / Nv)),
                    variance_inflation=float(sd ** 2 / (pv / Nv)),
                    N_eff=float(pv / sd ** 2), n_draws=int(mean_arr.size))

    # analytic prediction, DERIVED IN THIS TASK (modeled, not measured)
    def analytic_sd(mean_score, a_x, m_):
        return float(mean_score * a_x * np.sqrt(2.0 / m_))

    nulls.append(dict(
        id="NULL-V",
        name="vector-null: random directions of matched ||x||",
        removes_object="THE SIEVE DATABASE ITSELF -- its lattice membership, its "
                       "integrality, the exact 3-term algebraic relations among "
                       "its vectors, and its ball saturation structure. This is "
                       "the object whose independence MATZOV.Nf asserts.",
        preserves="N, m, q, sigma_e, and the exact empirical ||x|| distribution "
                  "(each surrogate vector has the norm of the sieve vector it "
                  "replaces), hence a_x is identical by construction.",
        can_it_fail="YES. If the sieve database's concentration behaviour were a "
                    "property of sieving, the surrogate would not reproduce it.",
        statistic="mean_i cos(2 pi x_i.e / q) for the correct secret, over "
                  "%d fresh error draws" % cfg["draws_null"],
        sieve_database=neff(db_means, db_pv, N),
        random_direction_surrogate=neff(sur_means, sur_pv, N),
        modeled_analytic_sd_this_task=dict(
            value=analytic_sd(float(db_means.mean()), a_x_meas, m),
            derivation="MODELED, derived in this task and not taken from MATZOV: "
                       "for vectors spread over directions, the database mean "
                       "depends on e essentially through ||e||^2 only, "
                       "S(e) ~ exp(-a_x ||e||^2/(m sigma^2)); with "
                       "Var(||e||^2) = 2 m sigma^4 this gives "
                       "sd(S) ~ S * a_x * sqrt(2/m), independent of N.",
            a_x_measured=a_x_meas)))

    # ---- NULL-IID : the shared error vector removed ------------------------
    rng_i = np.random.default_rng(SEEDS["iid_null"])
    Dn = cfg["draws_null"]
    iid_means = np.empty(Dn); iid_pv = np.empty(Dn)
    for t in range(Dn):
        Ei = np.rint(rng_i.normal(0.0, sigma, size=(N, m)))
        S = np.cos(TWOPI * (X * Ei).sum(axis=1) / q)
        iid_means[t] = S.mean(); iid_pv[t] = S.var(ddof=1)
    nulls.append(dict(
        id="NULL-IID",
        name="independent-error null: the law taken literally",
        removes_object="THE SHARED m-DIMENSIONAL ERROR VECTOR e -- the single "
                       "object that couples the N per-vector contributions. Each "
                       "vector is scored against its own fresh error draw, which "
                       "is what 'N independent samples' literally means.",
        preserves="the sieve database exactly, N, m, q, sigma_e.",
        can_it_fail="YES. If the coupling were negligible, this would match the "
                    "sieve database's variance.",
        statistic="mean_i cos(2 pi x_i.e_i / q), independent e_i per vector, "
                  "over %d draws" % Dn,
        result=neff(iid_means, iid_pv, N)))

    # ---- NULL-T : batch 1's target null, reproduced and labelled ------------
    rng_nt = np.random.default_rng(SEEDS["null_target"])
    Dt = cfg["draws_null"]
    tnull_means = np.empty((Dt, K))
    for t in range(Dt):
        bu = rng_nt.integers(0, q, size=m, dtype=np.int64)
        P = np.mod(X.dot(bu)[:, None] - Y.dot(C.T), q)
        tnull_means[t] = np.cos(TWOPI * P / q).mean(axis=0)
    tn_groups = {}
    for g, idxs in gidx.items():
        gm = tnull_means[:, idxs]
        tn_groups[g] = dict(n_candidates=len(idxs),
                            group_mean_score=ms(gm.mean(axis=1)),
                            n_draws=int(Dt))
    tn_rank = {}
    for g in ["uniform", "secret_distribution", "near_miss"]:
        if g in gidx:
            gm = tnull_means[:, gidx[g]]
            tn_rank[g] = dict(
                rank_of_nominal_secret_within_group=ms(
                    1 + (gm > tnull_means[:, [0]]).sum(axis=1)),
                P_nominal_secret_first_within_group=float(
                    np.mean(tnull_means[:, 0] > gm.max(axis=1))),
                n_draws=int(Dt))
    nulls.append(dict(
        id="NULL-T",
        name="target-null: b replaced by uniform on Z_q^m (BATCH-d2a728's null)",
        removes_object="THE LWE STRUCTURE IN THE TARGET b. It does NOT remove or "
                       "perturb the sieve database.",
        preserves="the sieve database exactly, the candidates, and the scoring code.",
        can_it_fail="NO -- and this is why it is reproduced here only for "
                    "continuity and reported with that label attached. With b "
                    "uniform on Z_q^m, x.b is uniform mod q for every fixed "
                    "nonzero x, so every phase is uniform and every mean score is "
                    "0 in expectation. Any code that reads b passes it. "
                    "(RT-20260803-4064e1 OBJ-2; DEC-20260803-d810d0 PD-1.)",
        statistic="per-candidate mean score over %d fresh uniform targets" % Dt,
        per_group=tn_groups, rank_within_group=tn_rank,
        pooled_statistic_deliberately_not_reported=(
            "Batch 1's '18 of 33' pooled three populations its own producer calls "
            "non-exchangeable. Per group is reported above; no pooled rank is "
            "computed here.")))

    # ---- m-sweep and N-sweep (CTRL-RT-2) -----------------------------------
    say("S8  m-sweep and N-sweep on the surrogate")
    rng_w = np.random.default_rng(SEEDS["sweep"])
    norms = np.sqrt(xn2.astype(float))
    msweep = []
    for mm in cfg["m_sweep"]:
        Xw = random_directions(rng_w, norms, mm)
        mw, pw = surrogate_means_over_draws(Xw, q, rng_w, sigma, cfg["draws_null"])
        r = neff(mw, pw, norms.size)
        r["m"] = int(mm); r["N"] = int(norms.size)
        r["modeled_analytic_sd_this_task"] = analytic_sd(r["mean"], a_x_meas, mm)
        msweep.append(r)
    Nsweep = []
    for NN in cfg["N_sweep"]:
        idx = rng_w.integers(0, norms.size, size=NN)
        Xw = random_directions(rng_w, norms[idx], m)
        mw, pw = surrogate_means_over_draws(Xw, q, rng_w, sigma, cfg["draws_null"])
        r = neff(mw, pw, NN)
        r["m"] = int(m); r["N"] = int(NN)
        r["modeled_analytic_sd_this_task"] = analytic_sd(r["mean"], a_x_meas, m)
        Nsweep.append(r)
    nulls.append(dict(
        id="NULL-SWEEP",
        name="m-sweep and N-sweep of the vector-null surrogate (CTRL-RT-2)",
        removes_object="THE SIEVE DATABASE (as NULL-V) while additionally VARYING "
                       "m and N, the two parameters that would have to control the "
                       "effect if it were, respectively, a small-dimension artifact "
                       "or a genuine loss of independent samples.",
        preserves="a_x, by reusing the measured ||x|| distribution at every m.",
        can_it_fail="YES. If the variance inflation were a loss of independent "
                    "samples from the database, N_eff would depend on N.",
        m_sweep=msweep, N_sweep=Nsweep))

    # =======================================================================
    say("S4  writing vectors.json")
    vec_obj = dict(
        task="TASK-20260803-5f11b7", batch="BATCH-f75059", goal="GOAL-MLKEM-004",
        note="x and y for every sieve-produced dual vector, emitted so that a "
             "reviewer can score any candidate and re-verify the certificate "
             "without re-running the sieve (RT-20260803-4064e1 OBJ-3).",
        parameters=dict(m=m, n=n, d=d, q=q, sieve=cfg["sieve"],
                        secret_distribution="centered_binomial(eta=%d)" % cfg["eta_secret"],
                        error_distribution="rounded_gaussian(sigma=%.4g)" % sigma,
                        n_vectors=int(N), seeds=SEEDS),
        A=[[int(z) for z in r] for r in A], secret=[int(z) for z in s],
        e_batch1_realisation=[int(z) for z in e_batch1],
        candidates=[dict(index=i, label=labels[i], group=groups[i],
                         vector=[int(z) for z in C[i]]) for i in range(K)],
        certificate=cert,
        x=[[int(z) for z in r] for r in X],
        y=[[int(z) for z in r] for r in Y])
    vp = os.path.join(args.out_dir,
                      "smoke_vectors.json" if args.smoke else "vectors.json")
    json.dump(vec_obj, open(vp, "w"))
    say("S4  wrote %s (%d bytes)" % (vp, os.path.getsize(vp)))

    # =======================================================================
    say("S2  P1 well-posedness")
    meas_for_s2 = dict(n_candidates_scored=K - 1, a_x_measured=a_x_meas)
    s2 = s2_wellposedness(cfg, say, ld, params, my_H_bits, meas_for_s2, np)
    ing1["sub_comparison_C_length_model"]["modeled_lsigma_s"] = \
        s2["sub_comparison_C"]["modeled_lsigma_s"]
    ing1["sub_comparison_C_length_model"]["modeled_over_measured_length"] = float(
        s2["sub_comparison_C"]["modeled_lsigma_s"]
        / ing1["sub_comparison_C_length_model"]["measured_effective_lsigma_s"])
    ing1["sub_comparison_C_length_model"]["modeled_advantage_vs_measured"] = dict(
        modeled=s2["sub_comparison_C"]["modeled_per_vector_advantage"],
        measured=ing1["sub_comparison_C_length_model"][
            "measured_reference_zero_mean_score"])
    say("S2  tuple_exists=%s  N_pred spread factor %.1f (%.3g .. %.3g)"
        % (s2["tuple_exists"], s2["N_pred_spread_factor"],
           s2["N_pred_min"], s2["N_pred_max"]))

    # =======================================================================
    say("S5b success probability vs subsample size N', per candidate group")
    cells = [c for c in [25, 100, 400, 1600, 6400, N] if c <= N]
    curve = {g: {str(c): 0 for c in cells} for g in
             ["uniform", "secret_distribution", "near_miss"] if g in gidx}
    rng_cv = np.random.default_rng(SEEDS["error_draws"] + 7)
    Dc = cfg["draws_curve"]
    for t in range(Dc):
        et = np.rint(rng_cv.normal(0.0, sigma, size=m)).astype(np.int64)
        u = (X.dot(et)) % q
        S = np.cos(TWOPI * ((u[None, :] + Dphase) % q) / q)      # (K, N)
        perm = rng_cv.permutation(N)
        cs = np.cumsum(S[:, perm], axis=1)
        for c in cells:
            mu_ = cs[:, c - 1] / c
            for g in curve:
                if mu_[0] > mu_[gidx[g]].max():
                    curve[g][str(c)] += 1
    curve_out = {g: {c: dict(P_correct_beats_group=v / Dc, n_draws=int(Dc),
                             binomial_sd=float(np.sqrt(max(v / Dc * (1 - v / Dc), 0) / Dc)))
                     for c, v in cc.items()} for g, cc in curve.items()}

    # =======================================================================
    reps = []
    if cfg["n_replicates"] > 0:
        say("S9  replicate instances (inherited CTRL-RT-5)")
        for r in range(cfg["n_replicates"]):
            if time.time() - t_start > args.max_seconds:
                say("S9  STOPPING after %d replicates: soft wall-clock guard "
                    "%.0fs reached. Recorded, not hidden." % (r, args.max_seconds))
                break
            sd_ = SEEDS["replicates"] + 1000 * r
            rgi = np.random.default_rng(sd_)
            Ar = rgi.integers(0, q, size=(m, n), dtype=np.int64)
            sr = centered_binomial(rgi, cfg["eta_secret"], n)
            Xr, Yr, Vr, tr = run_sieve(Ar, q, m, n, cfg["sieve"], sd_ + 1, sd_ + 2)
            Nr = Xr.shape[0]
            bad = int(np.count_nonzero(np.mod(Xr.dot(Ar) - Yr, q)))
            rgc = np.random.default_rng(sd_ + 3)
            cr = make_candidates(rgc, sr, q, n, cfg["eta_secret"],
                                 max(4, cfg["n_unif"] // 2), max(2, cfg["n_sdist"] // 2),
                                 cfg["n_near"])
            lr = [c[0] for c in cr]; gr = [c[1] for c in cr]
            Cr = np.array([c[2] for c in cr], dtype=np.int64)
            Dr = np.mod(Yr.dot((sr[None, :] - Cr).T), q).T.astype(np.int64)
            xr2 = (Xr * Xr).sum(axis=1)
            rge = np.random.default_rng(sd_ + 4)
            mr, _, pvr = score_means_over_draws(Xr, Dr, q, rge, sigma,
                                                cfg["draws_replicate"],
                                                decile_masks=None, correct_col=0)
            gi = {g: [i for i in range(len(cr)) if gr[i] == g] for g in set(gr)}
            axr = float(2 * np.pi ** 2 * sigma ** 2 * xr2.mean() / q ** 2)
            predr = float(np.mean(np.exp(-2 * np.pi ** 2 * sigma ** 2 * xr2 / q ** 2)))
            nm = mr[:, gi["near_miss"]]
            un = mr[:, gi["uniform"]]
            reps.append(dict(
                replicate=r, seed=sd_, n_vectors=int(Nr),
                certificate_violating_entries=bad,
                certificate_verified=bool(bad == 0),
                sieve_seconds=tr["sieve_seconds"],
                a_x_measured=axr,
                correct_mean_score=ms(mr[:, 0]),
                ingredient1_global_ratio=ms(mr[:, 0] / predr),
                ingredient2_uniform_sd_ratio=ms(
                    un.std(axis=1, ddof=1) / np.sqrt(0.5 / Nr)),
                near_miss_paired_delta_vs_best=ms(mr[:, 0] - nm.max(axis=1)),
                P_correct_first_within_near_miss=float(
                    np.mean(mr[:, 0] > nm.max(axis=1))),
                P_correct_first_within_uniform=float(
                    np.mean(mr[:, 0] > un.max(axis=1))),
                n_draws=int(cfg["draws_replicate"])))
            say("S9  replicate %d: N=%d cert_ok=%s correct=%.4f+-%.4f "
                "ing1_ratio=%.4f near-miss delta=%+.5f"
                % (r, Nr, bad == 0, reps[-1]["correct_mean_score"]["mean"],
                   reps[-1]["correct_mean_score"]["sd"],
                   reps[-1]["ingredient1_global_ratio"]["mean"],
                   reps[-1]["near_miss_paired_delta_vs_best"]["mean"]))

    rep_summary = None
    if reps:
        def across(key, sub="mean"):
            v = np.array([r[key][sub] for r in reps], dtype=float)
            return dict(mean=float(v.mean()),
                        sd_across_instances=float(v.std(ddof=1)) if v.size > 1 else None,
                        min=float(v.min()), max=float(v.max()),
                        n_instances=int(v.size))
        rep_summary = dict(
            n_instances=len(reps),
            draws_per_instance=int(cfg["draws_replicate"]),
            total_error_draws=int(len(reps) * cfg["draws_replicate"]),
            note="Each per-instance number already carries mean +/- sd over "
                 "%d error draws; the 'sd_across_instances' column below is the "
                 "instance-to-instance spread, which is the uncertainty neither "
                 "batch-1 reviewer could bound. The primary instance is NOT "
                 "included in these %d."
                 % (cfg["draws_replicate"], len(reps)),
            correct_mean_score=across("correct_mean_score"),
            ingredient1_global_ratio=across("ingredient1_global_ratio"),
            ingredient2_uniform_sd_ratio=across("ingredient2_uniform_sd_ratio"),
            near_miss_paired_delta_vs_best=across("near_miss_paired_delta_vs_best"),
            P_correct_first_within_near_miss=dict(
                values=[r["P_correct_first_within_near_miss"] for r in reps]),
            P_correct_first_within_uniform=dict(
                values=[r["P_correct_first_within_uniform"] for r in reps]),
            all_certificates_verified=bool(all(r["certificate_verified"] for r in reps)))

    # =======================================================================
    env = dict(python=sys.version, platform=platform.platform(),
               numpy=np.__version__, fpylll=__import__("fpylll").__version__,
               g6k="0.1.2", venv=sys.prefix,
               sage_version=__import__("sage.version", fromlist=["version"]).version,
               estimator_path=args.estimator_path,
               estimator_commit=s1["estimator_commit"],
               estimator_dirty=s1["estimator_dirty"])
    git_sha = subprocess.run(["git", "-C", os.path.dirname(os.path.abspath(__file__)),
                              "rev-parse", "HEAD"], capture_output=True,
                             text=True).stdout.strip()
    git_dirty = subprocess.run(["git", "-C", os.path.dirname(os.path.abspath(__file__)),
                                "status", "--porcelain"], capture_output=True,
                               text=True).stdout.strip()

    results = dict(
        task="TASK-20260803-5f11b7", batch="BATCH-f75059", goal="GOAL-MLKEM-004",
        script_version=SCRIPT_VERSION, smoke=bool(args.smoke),
        states_a_conclusion=False,
        scope="TOY SCALE: m=%d n=%d d=%d q=%d, one sieve algorithm, "
              "distinguishing form only. NOT crypto scale. No statement about "
              "FIPS 203 dimensions, no ML-KEM break claim, no security claim, "
              "no cost claim, no speedup." % (m, n, d, q),
        rule12_status="AGENTS.md rule 12 UNMET and UNWAIVED, inherited. No status "
                      "change to any EV-MLKEM-* or KN-* record.",
        run=dict(m=m, n=n, d=d, q=q, sieve_algorithm=cfg["sieve"],
                 secret_distribution="centered_binomial(eta=%d)" % cfg["eta_secret"],
                 error_distribution="rounded_gaussian(sigma=%.4g)" % sigma,
                 n_sieve_vectors=int(N), seeds=SEEDS,
                 lll_seconds=tim["lll_seconds"], sieve_seconds=tim["sieve_seconds"],
                 sieve_threads=1, total_wall_seconds=None,
                 peak_rss_mb=None, memory_cap_gb=args.mem_cap_gb,
                 git_commit=git_sha, git_dirty=bool(git_dirty),
                 git_dirty_paths=git_dirty.splitlines()),
        certificate=cert,
        certificate_independent_identity_check=dict(
            statement="x.b - y.c == x.e + y.(s-c) (mod q) recomputed by two "
                      "different routes for all %d candidates x %d vectors" % (K, N),
            passed=identity_ok),
        vector_geometry=dict(
            n_vectors=int(N),
            xnorm2=dict(min=int(xn2.min()), mean=float(xn2.mean()),
                        median=float(np.median(xn2)), max=int(xn2.max())),
            ynorm2=dict(min=int(yn2.min()), mean=float(yn2.mean()),
                        median=float(np.median(yn2)), max=int(yn2.max())),
            vnorm2=dict(min=int(vn2.min()), mean=float(vn2.mean()),
                        median=float(np.median(vn2)), max=int(vn2.max())),
            a_x_measured=a_x_meas, a_y_measured=a_y_meas,
            a_x_definition="2 pi^2 sigma_e^2 <||x||^2> / q^2",
            a_y_definition="2 pi^2 Var(s) <||y||^2> / q^2, Var(s)=eta/2=1"),
        S1_known_answer_control_P1b=s1,
        S2_wellposedness_P1=s2,
        S5_per_candidate_group_P3=dict(
            n_draws=int(cfg["draws_primary"]),
            never_pooled="Statistics are reported per candidate group only. No "
                         "pooled wrong-candidate statistic is computed anywhere "
                         "in this file (INT-3, DEC-20260803-d810d0).",
            groups=per_group, paired_against_correct=paired,
            batch1_single_draw_position=batch1_position),
        S5b_success_vs_subsample_size=dict(
            note="Success = correct secret's mean score exceeds every member of "
                 "the named group, on a random subsample of size N'. Subsampling "
                 "holds the LENGTH distribution fixed, whereas a genuinely "
                 "smaller sieve returns SHORTER vectors and would do better "
                 "(RT OBJ-5).",
            per_group=curve_out),
        S6_ingredient1_per_vector_advantage=ing1,
        S7_ingredient2_iid_candidate_noise=ing2,
        S8_nulls_P2=dict(
            corrective_rule="DEC-20260803-d810d0 PD-1: every null names the "
                            "OBJECT whose removal it tests.",
            nulls=nulls),
        S9_replicate_instances=dict(per_instance=reps, summary=rep_summary),
        environment=env, log=log)

    results["run"]["total_wall_seconds"] = round(time.time() - t_start, 3)
    results["run"]["peak_rss_mb"] = round(
        resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)
    with open(vp, "rb") as f:
        results["vectors_json_sha256"] = hashlib.sha256(f.read()).hexdigest()
    results["vectors_json_bytes"] = os.path.getsize(vp)

    rp = os.path.join(args.out_dir,
                      "smoke_results.json" if args.smoke else "results.json")
    json.dump(results, open(rp, "w"), indent=2)
    say("wrote %s" % rp)
    say("TOTAL %.1fs  peak RSS %.1f MB"
        % (results["run"]["total_wall_seconds"], results["run"]["peak_rss_mb"]))


if __name__ == "__main__":
    main()
