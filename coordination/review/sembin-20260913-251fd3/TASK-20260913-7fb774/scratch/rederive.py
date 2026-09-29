#!/usr/bin/env python3
"""Blind re-derivation for TASK-20260913-7fb774 (attempt 2), v2.

Written from the task statement, Nagao 2015/984 (Section 7, Lemma 2,
Proposition 5, Algorithm 2) and H-SEMBIN-4a80f3 (HEUR-1, HEUR-2) only.
Nothing here is imported or copied from any experiments/ directory.

Everything is in the log2 domain ("bits") unless stated otherwise.
No unit conversion between F_2 operations and group operations is applied.
"""
from __future__ import annotations

import json
import math
import random
import sys
from fractions import Fraction

LN2 = math.log(2.0)

CELLS = {
    "A": {"p": 2, "n": 571, "omega": 2.807, "C0": 8},
    "B": {"p": 2, "n": 571, "omega": 3.0, "C0": 3},
}
D_F = 4
VOW_CONST = 0.886


# ---------------------------------------------------------------- log2 helpers
def log2_int(x: int) -> float:
    if x <= 0:
        raise ValueError("log2 of non-positive integer")
    b = x.bit_length()
    if b <= 1000:
        return math.log2(x)
    shift = b - 1000
    return math.log2(x >> shift) + shift


def log2_binom_int(N: int, d: int) -> float:
    return log2_int(math.comb(N, d))


def log2_binom_real(N: float, d: int) -> float:
    return (math.lgamma(N + 1.0) - math.lgamma(N - d + 1.0) - math.lgamma(d + 1.0)) / LN2


def log2_add(a: float, b: float) -> float:
    if a == float("inf") or b == float("inf"):
        return float("inf")
    hi, lo = max(a, b), min(a, b)
    if hi - lo > 1200:
        return hi
    return hi + math.log2(1.0 + 2.0 ** (lo - hi))


def log2_one_minus_exp_neg(lam: float) -> float:
    """log2(1 - exp(-lam)), lam >= 0."""
    if lam <= 0:
        return float("-inf")
    if lam < 1e-4:
        return math.log2(lam * (1.0 - lam / 2.0 + lam * lam / 6.0))
    return math.log(-math.expm1(-lam)) / LN2


def t4_from_log2_lambda(log2_lam: float) -> float:
    """T4 = log2(1 / Pr), Pr = 1 - exp(-lambda)."""
    if log2_lam == float("-inf"):
        return float("inf")
    if log2_lam > 20:  # lam >= 2^20: Pr = 1 to any precision that matters
        return 0.0
    if log2_lam < -60:  # Pr ~ lam
        return -log2_lam
    return -log2_one_minus_exp_neg(2.0**log2_lam)


# --------------------------------------------- HEUR-1 per-coset size models
# P-b "point-into-coset": #Fb_i ~ Bin(#E ~ p^n, p^{C0-n}) -> Poisson(p^{C0})
#      to within O(p^{-n}); its empty probability exp(-p^{C0}) is the form
#      HEUR-1's "p^k = Omega(log m)" coupon-collector wording presumes.
# P-a "x-coordinate pairs" (p = 2 only): each of the 2^{C0} x-values in the
#      coset is on the curve with probability ~1/2 and then carries 2 points,
#      so #Fb_i = 2 * Bin(2^{C0}, 1/2).  Mean 2^{C0}, variance 2^{C0}.
# Both have mean p^{C0}; they differ in the empty-coset probability, which is
# what the geometric (E[log]) reading of T4 is sensitive to.
def per_coset_stats_poisson(mu: float) -> dict:
    kmax = int(mu + 60 * math.sqrt(mu) + 80)
    pmf = [math.exp(-mu + j * math.log(mu) - math.lgamma(j + 1)) for j in range(kmax + 1)]
    p0 = pmf[0]
    mass_pos = sum(pmf[1:])
    e_ln = sum(pmf[j] * math.log(j) for j in range(1, kmax + 1)) / mass_pos
    e_ln2 = sum(pmf[j] * math.log(j) ** 2 for j in range(1, kmax + 1)) / mass_pos
    return {
        "model": "Poisson(p^{C0}) point-into-coset",
        "mean": mu,
        "P_empty": p0,
        "E_log2_X_given_nonempty": e_ln / LN2,
        "sd_log2_X_given_nonempty": math.sqrt(max(0.0, e_ln2 - e_ln**2)) / LN2,
        "jensen_deficit_bits_per_coset": math.log2(mu) - e_ln / LN2,
        "pmf_tail_mass_dropped": max(0.0, 1.0 - sum(pmf)),
    }


def per_coset_stats_pairs(k: int) -> dict:
    trials = 2**k
    denom = 2**trials
    pmf = [Fraction(math.comb(trials, j), denom) for j in range(trials + 1)]
    p0 = float(pmf[0])
    mass_pos = 1.0 - p0
    e_ln = sum(float(pmf[j]) * math.log(2 * j) for j in range(1, trials + 1)) / mass_pos
    e_ln2 = sum(float(pmf[j]) * math.log(2 * j) ** 2 for j in range(1, trials + 1)) / mass_pos
    return {
        "model": "2 * Bin(2^{C0}, 1/2) x-coordinate pairs (exact)",
        "mean": float(trials),
        "P_empty": p0,
        "E_log2_X_given_nonempty": e_ln / LN2,
        "sd_log2_X_given_nonempty": math.sqrt(max(0.0, e_ln2 - e_ln**2)) / LN2,
        "jensen_deficit_bits_per_coset": k - e_ln / LN2,
        "pmf_tail_mass_dropped": 0.0,
    }


# --------------------------------------------------------------- MC samplers
def sample_pairs(rng: random.Random, k: int) -> int:
    return 2 * rng.getrandbits(2**k).bit_count()


def sample_poisson(rng: random.Random, mu: float) -> int:
    if mu < 30:
        L, kk, pr = math.exp(-mu), 0, 1.0
        while True:
            pr *= rng.random()
            if pr <= L:
                return kk
            kk += 1
    slam, loglam = math.sqrt(mu), math.log(mu)
    b = 0.931 + 2.53 * slam
    a = -0.059 + 0.02483 * b
    invalpha = 1.1239 + 1.1328 / (b - 3.4)
    vr = 0.9277 - 3.6224 / (b - 2)
    while True:
        u = rng.random() - 0.5
        v = rng.random()
        us = 0.5 - abs(u)
        kk = int(math.floor((2 * a / us + b) * u + mu + 0.43))
        if us >= 0.07 and v <= vr:
            return kk
        if kk < 0 or (us < 0.013 and v > us):
            continue
        if (math.log(v) + math.log(invalpha) - math.log(a / (us * us) + b)
                <= -mu + kk * loglam - math.lgamma(kk + 1)):
            return kk


def monte_carlo(rng, n, C0, m_int, which, samples):
    """Sample m independent coset sizes, form log2 lambda = sum log2 #Fb_i - n,
    and report BOTH expectations of the success probability:
      unconditional  E[1 - exp(-lambda)]  over all factor-base draws, and
      conditional    E[... | every coset nonempty].
    A draw with an empty coset has lambda = 0 exactly: for that factor base NO
    R has a decomposition of this shape, so its success probability is 0 and
    its contribution to 1/Pr is infinite."""
    mu = float(2**C0)
    tot, cond_tot, n_ok = 0.0, 0.0, 0
    l2s = []
    for _ in range(samples):
        s, empty = 0.0, False
        for _ in range(m_int):
            x = sample_pairs(rng, C0) if which == "pairs" else sample_poisson(rng, mu)
            if x == 0:
                empty = True
                break
            s += math.log2(x)
        if empty:
            continue
        l2 = s - n
        l2s.append(l2)
        pr = -math.expm1(-(2.0**l2)) if l2 > -1000 else 0.0
        tot += pr
        cond_tot += pr
        n_ok += 1
    l2s.sort()
    p_ok = n_ok / samples
    e_uncond = tot / samples
    e_cond = cond_tot / n_ok if n_ok else 0.0

    def q(f):
        return l2s[min(len(l2s) - 1, int(f * len(l2s)))] if l2s else None

    return {
        "samples": samples,
        "P_all_cosets_nonempty_empirical": p_ok,
        "E_success_prob_unconditional": e_uncond,
        "T4_bits_from_E_success_unconditional": (-math.log2(e_uncond) if e_uncond > 0 else float("inf")),
        "E_success_prob_given_all_nonempty": e_cond,
        "T4_bits_from_E_success_given_all_nonempty": (-math.log2(e_cond) if e_cond > 0 else float("inf")),
        "log2_lambda_quantiles_given_all_nonempty": {"p05": q(0.05), "p50": q(0.50), "p95": q(0.95)},
        "mean_log2_lambda_given_all_nonempty": (sum(l2s) / len(l2s) if l2s else None),
    }


# ---------------------------------------------------------------- vOW charge
def vow_charges(n: int) -> dict:
    """W = 0.886 * 2^{n/2} group operations; T = W(1/M + 1/w); Mem = 3n max(w, M).
    T*Mem = 3n W (1/M + 1/w) max(w, M) = 3n W (max/M + max/w) >= 6 n W,
    with equality exactly on w = M (any common value)."""
    log2_W = n / 2.0 + math.log2(VOW_CONST)
    return {
        "log2_W_group_operations": log2_W,
        "time_only_bits": log2_W,
        "time_only_point": "M = 1, w -> infinity: T -> W(1/1 + 0) = W, so log2 T = log2 W",
        "time_memory_product_min_bits__mem_in_bits": math.log2(6.0 * n) + log2_W,
        "time_memory_product_min_bits__mem_in_points": math.log2(2.0) + log2_W,
        "product_min_locus": "the whole ray w = M > 0; T*Mem = 3nW(max(w,M)/M + max(w,M)/w) = 6nW there and is strictly larger off it",
        "product_min_derivation": "let r = w/M; T*Mem/(3nW) = max(r,1)/r*... = (1/M + 1/w) max(w,M) = 1 + max(r, 1/r) >= 2",
        "memory_unit_note": "Mem = 3n max(w,M) counts BITS (3n bits per stored point). The mem_in_points variant divides by 3n and is reported only to expose the unit choice.",
    }


# --------------------------------------------------------------- the charging
def charge(solve_bits, T3_bits, T4_bits, omega, T1_bits, vow) -> dict:
    decompose = solve_bits + T3_bits + T4_bits
    la = omega * T3_bits
    time_bits = log2_add(decompose, la)
    la_contrib = (time_bits - decompose) if math.isfinite(decompose) else None
    out = {
        "T4_bits_used": T4_bits,
        "decompose_bits_T1_T2_T3_T4": decompose,
        "linear_algebra_bits_omega_T3": la,
        "time_bits": time_bits,
        "linear_algebra_log_add_contribution_bits": la_contrib,
        "memory_frozen_bits_T5": T1_bits,
        "memory_dense_bits_T5": 2.0 * T1_bits,
        "vow_time_only_bits": vow["time_only_bits"],
        "vow_product_minimum_bits": vow["time_memory_product_min_bits__mem_in_bits"],
        "margin_time_only_bits": time_bits - vow["time_only_bits"],
        "margin_product_frozen_bits": (time_bits + T1_bits) - vow["time_memory_product_min_bits__mem_in_bits"],
        "margin_product_dense_bits": (time_bits + 2.0 * T1_bits) - vow["time_memory_product_min_bits__mem_in_bits"],
        "margin_product_frozen_bits__vow_mem_in_points": (time_bits + T1_bits) - vow["time_memory_product_min_bits__mem_in_points"],
        "margin_product_dense_bits__vow_mem_in_points": (time_bits + 2.0 * T1_bits) - vow["time_memory_product_min_bits__mem_in_points"],
    }
    return out


def derive_cell(label, cell, rng, mc_samples) -> dict:
    p, n, omega, C0 = cell["p"], cell["n"], cell["omega"], cell["C0"]
    m_exact = Fraction(n, C0)
    roundings = {
        "floor": math.floor(m_exact),
        "ceil": math.ceil(m_exact),
        "nearest": int(round(float(m_exact))),
        "exact_real": float(m_exact),
    }
    coset_models = {"P-b_poisson": per_coset_stats_poisson(float(p**C0))}
    if p == 2:
        coset_models["P-a_pairs"] = per_coset_stats_pairs(C0)

    vow = vow_charges(n)
    out = {
        "cell": label,
        "inputs": {"p": p, "n": n, "omega": omega, "C0": C0, "d_F": D_F},
        "m_exact": {"rational": f"{m_exact.numerator}/{m_exact.denominator}", "real": float(m_exact)},
        "per_coset_models_HEUR1": coset_models,
        "vow": vow,
        "by_rounding": {},
    }

    for rname, m in roundings.items():
        is_int = isinstance(m, int)
        N = n * (m - 1)
        if is_int:
            T1 = log2_binom_int(N + D_F, D_F)
            N_alt = m * C0 + n * (m - 2)  # exact EQS4 variable count when m C0 != n
            T1_alt = log2_binom_int(N_alt + D_F, D_F)
            T1_sqfree = log2_int(sum(math.comb(N, d) for d in range(D_F + 1)))
            T1_nagao_loose = D_F * math.log2(N)  # Lemma 2's O(N^{d_F}) form, for contrast only
        else:
            T1 = log2_binom_real(N + D_F, D_F)
            N_alt = T1_alt = T1_sqfree = None
            T1_nagao_loose = D_F * math.log2(N)
        T2 = (omega - 1.0) * T1
        solve = T1 + T2

        Fb = m * (p**C0)
        T3 = math.log2(Fb)
        T3p1 = math.log2(Fb + 1)

        km_n = m * C0 - n
        log2_lam_arith = km_n * math.log2(p)
        T4: dict = {
            "R1_nominal_lambda_equals_1": {
                "log2_lambda": 0.0,
                "T4_bits": t4_from_log2_lambda(0.0),
                "basis": "HEUR-2 read at its stated operating point prod #Fb_i ~ #E, i.e. lambda := 1; independent of how m is rounded",
            },
            "R2_arithmetic_E_of_product": {
                "log2_lambda": log2_lam_arith,
                "T4_bits": t4_from_log2_lambda(log2_lam_arith),
                "basis": "E[prod_i #Fb_i]/p^n = p^{m C0 - n} (independent cosets, each mean p^{C0}); this is E[lambda], NOT E[Pr]",
            },
        }
        for cname, cm in coset_models.items():
            l2_geo = m * cm["E_log2_X_given_nonempty"] - n * math.log2(p)
            p_all = (1.0 - cm["P_empty"]) ** m
            T4[f"R3_geometric_E_of_log_product__{cname}"] = {
                "log2_lambda_given_all_nonempty": l2_geo,
                "T4_bits_given_all_nonempty": t4_from_log2_lambda(l2_geo),
                "P_all_m_cosets_nonempty": p_all,
                "expected_factor_base_draws_to_get_all_nonempty": (1.0 / p_all if p_all > 0 else float("inf")),
                "sd_log2_lambda_over_m_cosets_bits": math.sqrt(m * cm["sd_log2_X_given_nonempty"] ** 2),
                "jensen_deficit_total_bits": m * cm["jensen_deficit_bits_per_coset"],
                "T4_bits_unconditional": float("inf"),
                "unconditional_note": "P[#Fb_i = 0] > 0 for every i, so E[log2 prod #Fb_i] = -inf and the unconditional geometric reading gives T4 = +inf",
            }
        if is_int and mc_samples > 0:
            for cname, which in (("P-b_poisson", "poisson"), ("P-a_pairs", "pairs")):
                if which == "pairs" and p != 2:
                    continue
                T4[f"R4_monte_carlo_E_of_success_probability__{cname}"] = \
                    monte_carlo(rng, n, C0, m, which, mc_samples)

        entry = {
            "m": m,
            "m_is_integer": is_int,
            "m_times_C0_minus_n": km_n,
            "N_variables_statement_n_times_m_minus_1": N,
            "T1_bits": T1,
            "T2_bits": T2,
            "T1_plus_T2_one_solve_bits": solve,
            "T1_variants": {
                "exact_EQS4_variable_count_mC0_plus_n_m_minus_2": {"N": N_alt, "T1_bits": T1_alt},
                "squarefree_sum_d_le_4_C_N_d_bits": T1_sqfree,
                "nagao_lemma2_loose_N_to_the_dF_bits": T1_nagao_loose,
            },
            "Fb_size": float(Fb),
            "T3_bits": T3,
            "T3_bits_plus_one_relation": T3p1,
            "T5_frozen_bits": T1,
            "T5_dense_bits": 2.0 * T1,
            "omega_times_T3_bits": omega * T3,
            "T4": T4,
            "charged": {},
        }
        for name, blk in T4.items():
            if name.startswith("R4_"):
                for tag, key in (("unconditional", "T4_bits_from_E_success_unconditional"),
                                 ("given_all_nonempty", "T4_bits_from_E_success_given_all_nonempty")):
                    entry["charged"][f"{name}__{tag}"] = charge(solve, T3, blk[key], omega, T1, vow)
                continue
            key = "T4_bits" if "T4_bits" in blk else "T4_bits_given_all_nonempty"
            entry["charged"][name] = charge(solve, T3, blk[key], omega, T1, vow)
        out["by_rounding"][rname] = entry
    return out


def self_checks() -> dict:
    """Hand-verifiable anchors, so a reader can spot-check the machinery."""
    return {
        "log2_C(39974,4)_vs_4log2(39970)-log2(24)": [
            log2_binom_int(39974, 4), 4 * math.log2(39970) - math.log2(24)],
        "T4_at_lambda_1_should_be_minus_log2(1-1/e)": [
            t4_from_log2_lambda(0.0), -math.log2(1.0 - 1.0 / math.e)],
        "log2_add(100,60)_minus_100_should_be_about_2^-40": log2_add(100.0, 60.0) - 100.0,
        "log2_W_at_n_571": 571 / 2 + math.log2(0.886),
        "log2_6n_at_n_571": math.log2(6 * 571),
        "poisson_mu_8_P_empty_vs_exp(-8)": [per_coset_stats_poisson(8.0)["P_empty"], math.exp(-8.0)],
        "pairs_C0_3_P_empty_vs_2^-8": [per_coset_stats_pairs(3)["P_empty"], 2.0**-8],
        "log2_binom_real_vs_int_at_N_40000": [log2_binom_real(40004.0, 4), log2_binom_int(40004, 4)],
    }


def main():
    mc = int(sys.argv[1]) if len(sys.argv) > 1 else 200000
    rng = random.Random(20260914)
    res = {
        "task": "TASK-20260913-7fb774",
        "review_round": "REVIEW-SEMBIN-20260913-251fd3",
        "attempt": 2,
        "seed": 20260914,
        "monte_carlo_samples": mc,
        "conventions": {
            "monomials": "C(N + d_F, d_F) with d_F = 4 and N = n(m-1) (the statement's binomial reading); exact math.comb for integer N, lgamma for the real-m variant",
            "T1": "log2(monomials)",
            "T2": "(omega - 1) * T1, so T1 + T2 = omega * log2(monomials) = one solve",
            "T3": "log2(#Fb) with #Fb = m * p^{C0}; the +1 relation of Algorithm 2 is reported as a variant",
            "T4": "log2(1/Pr), Pr = 1 - exp(-lambda), lambda = prod_i #Fb_i / #E with #E ~ p^n; four readings R1-R4",
            "T5": "memory in field elements: frozen = T1, dense = 2*T1 (at p = 2 an F_2 element is one bit only if bit-packed)",
            "time": "log2(2^{T1+T2+T3+T4} + 2^{omega*T3})",
            "vow": "W = 0.886 * 2^{n/2} group ops; T = W(1/M + 1/w); Mem = 3n max(w,M) bits",
            "units": "NO conversion is applied between F_2 operations and group operations, nor between field elements and bits on the vOW side.",
        },
        "self_checks": self_checks(),
        "cells": {},
    }
    for label, cell in CELLS.items():
        res["cells"][label] = derive_cell(label, cell, rng, mc)
    json.dump(res, sys.stdout, indent=1, default=str)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
