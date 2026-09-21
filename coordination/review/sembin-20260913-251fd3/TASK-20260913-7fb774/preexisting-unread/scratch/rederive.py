#!/usr/bin/env python3
"""Blind re-derivation, TASK-20260913-7fb774 (attempt 2).

Derives the Nagao 2015/984 Theorem 1 costing of H-SEMBIN-4a80f3 at

    cell A: p = 2, n = 571, omega = 2.807, C_0 = 8
    cell B: p = 2, n = 571, omega = 3.0,   C_0 = 3

from the STATEMENT in the task card and the frozen Nagao text alone. Nothing is
imported from any experiments/ directory. Exact integer arithmetic (math.comb)
is used for log2 of binomials at integer N, and lgamma at non-integer N.

Every ambiguity met is carried as a keyed reading rather than resolved.
"""
import json
import math
import sys

import numpy as np

LN2 = math.log(2.0)

# ---------------------------------------------------------------- helpers ---


def log2_binom_int(top, d):
    """log2 C(top, d), exact integer binomial then log2 (double precision)."""
    return math.log2(math.comb(top, d))


def log2_binom_real(top, d):
    """log2 C(top, d) for real top via lgamma."""
    return (math.lgamma(top + 1) - math.lgamma(d + 1) - math.lgamma(top - d + 1)) / LN2


def log2_squarefree_count(N, d):
    """log2 sum_{e=0}^{d} C(N, e): monomials reduced mod X^2 = X (p = 2)."""
    return math.log2(sum(math.comb(N, e) for e in range(d + 1)))


def log2_add(*bits):
    mx = max(bits)
    return mx + math.log2(sum(2.0 ** (b - mx) for b in bits))


def t4_from_log2_lambda(L):
    """T4 = -log2(1 - exp(-lambda)), lambda = 2^L; stable at both ends."""
    if L == float("-inf"):
        return float("inf")
    lam = 2.0 ** L
    pr = -math.expm1(-lam)  # 1 - exp(-lam)
    if pr <= 0.0:
        return float("inf")
    return -math.log2(pr)


# --------------------------------------------- per-coset random models ------
# HEUR-1: #Fb_i is "a binomial count with mean ~ p^k". Three parametrisations
# with that mean are carried:
#   P1  X = 2 * Bin(p^k, 1/2)   -- x-map 2-to-1 onto a density-1/2 set (the
#                                  justification HEUR-1 itself gives); var p^k
#   P2  X = Bin(2 p^k, 1/2)     -- literal "binomial with mean p^k"; var p^k/2
#   P3  X = Poisson(p^k)        -- each of ~p^n points lands in the coset with
#                                  prob p^{k-n}; Bin(p^n, p^{k-n}) ~ Poisson


def coset_pmf(model, M):
    """Return (support values x, probabilities) for #Fb_i under a model, M = p^k."""
    if model == "P1":
        xs = [2 * j for j in range(M + 1)]
        ps = [math.comb(M, j) / 2.0 ** M for j in range(M + 1)]
    elif model == "P2":
        xs = list(range(2 * M + 1))
        ps = [math.comb(2 * M, j) / 2.0 ** (2 * M) for j in range(2 * M + 1)]
    elif model == "P3":
        top = int(M + 40 * math.sqrt(M) + 40)
        xs = list(range(top + 1))
        ps = [math.exp(-M + j * math.log(M) - math.lgamma(j + 1)) for j in xs]
    else:
        raise ValueError(model)
    return xs, ps


def coset_stats(model, M):
    xs, ps = coset_pmf(model, M)
    p0 = ps[0]
    mean = sum(x * p for x, p in zip(xs, ps))
    # conditional on nonempty
    z = 1.0 - p0
    e_log = sum(math.log2(x) * p for x, p in zip(xs, ps) if x > 0) / z
    e_log2 = sum(math.log2(x) ** 2 * p for x, p in zip(xs, ps) if x > 0) / z
    var_log = e_log2 - e_log ** 2
    mean_cond = sum(x * p for x, p in zip(xs, ps) if x > 0) / z
    return {
        "P_empty": p0,
        "mean": mean,
        "mean_given_nonempty": mean_cond,
        "E_log2_given_nonempty": e_log,
        "Var_log2_given_nonempty": var_log,
        "log2_mean_minus_E_log2": math.log2(M) - e_log,
    }


# ------------------- instance-averaged success probability (exact-ish) ------


def instance_averaged_pr(model, M, m, n, step_bits=2.0 ** -10):
    """E[1 - exp(-lambda) | all m cosets nonempty], lambda = prod X_i / 2^n.

    Distribution of S = sum_i log2 X_i (conditioned X_i > 0) is obtained by
    m-fold convolution on a fine grid (each atom split between its two
    neighbouring grid points so the MEAN is preserved exactly), via FFT.
    Returns (E[Pr | all nonempty], P[all nonempty]).
    """
    xs, ps = coset_pmf(model, M)
    p0 = ps[0]
    z = 1.0 - p0
    atoms = [(math.log2(x), p / z) for x, p in zip(xs, ps) if x > 0]
    max_bits = max(a for a, _ in atoms) * m
    size = int(2 ** math.ceil(math.log2(max_bits / step_bits + 16)))
    base = np.zeros(size)
    for a, p in atoms:
        pos = a / step_bits
        lo = int(math.floor(pos))
        frac = pos - lo
        base[lo] += p * (1.0 - frac)
        base[lo + 1] += p * frac
    F = np.fft.rfft(base)
    conv = np.fft.irfft(F ** m, n=size)
    conv = np.clip(conv, 0.0, None)
    conv /= conv.sum()
    grid = np.arange(size) * step_bits  # S in bits
    L = grid - n  # log2 lambda
    lam = np.exp2(L)
    pr = -np.expm1(-lam)
    e_pr = float(np.sum(conv * pr))
    p_all = z ** m
    mean_S = float(np.sum(conv * grid))
    return e_pr, p_all, mean_S


def instance_averaged_pr_mc(model, M, m, n, samples=1_000_000, chunk=50_000, seed=20260914):
    """Monte Carlo cross-check of instance_averaged_pr (conditioned on nonempty)."""
    rng = np.random.default_rng(seed)
    tot = 0.0
    tot2 = 0.0
    cnt = 0
    empties = 0
    drawn = 0
    while cnt < samples:
        s = min(chunk, samples - cnt)
        if model == "P1":
            X = 2 * rng.binomial(M, 0.5, size=(s, m))
        elif model == "P2":
            X = rng.binomial(2 * M, 0.5, size=(s, m))
        else:
            X = rng.poisson(M, size=(s, m))
        drawn += s
        ok = np.all(X > 0, axis=1)
        empties += int((~ok).sum())
        X = X[ok]
        if X.shape[0] == 0:
            continue
        S = np.log2(X).sum(axis=1)
        pr = -np.expm1(-np.exp2(S - n))
        tot += float(pr.sum())
        tot2 += float((pr ** 2).sum())
        cnt += X.shape[0]
    mean = tot / cnt
    var = tot2 / cnt - mean ** 2
    se = math.sqrt(max(var, 0.0) / cnt)
    return mean, se, 1.0 - empties / drawn


# --------------------------------------------------------------- vOW --------


def vow(n, W_const=0.886):
    log2W = n / 2.0 + math.log2(W_const)
    # product T*Mem = 3n W (a/M + a/w), a = max(w,M): minimum 2*3n*W at w = M
    log2_prod_min_analytic = math.log2(6.0 * n) + log2W
    # numeric confirmation on a grid over (log2 w, log2 M) in [0, 80]^2
    best = float("inf")
    arg = None
    for lw in range(0, 81):
        for lM in range(0, 81):
            w, Mst = 2.0 ** lw, 2.0 ** lM
            lt = log2W + math.log2(1.0 / Mst + 1.0 / w)
            lmem = math.log2(3.0 * n * max(w, Mst))
            v = lt + lmem
            if v < best:
                best = v
                arg = (lw, lM)
    return {
        "W_const": W_const,
        "log2_W": log2W,
        "time_only_bits": log2W,
        "time_only_point": "M = 1, w -> infinity: T = W(1/1 + 0) = W",
        "product_min_bits_analytic": log2_prod_min_analytic,
        "product_min_bits_grid": best,
        "product_min_grid_argmin_log2_w_log2_M": arg,
        "product_min_locus": "every point with w = M (any common value); T*Mem = 6 n W there",
        "memory_unit": "bits (3n bits per stored/held point)",
    }


# --------------------------------------------------------------- cells ------


def derive_cell(name, p, n, omega, C0, dF=4, do_inst=True):
    k = C0
    M = p ** k
    m_exact = n / C0
    roundings = {
        "floor": math.floor(m_exact),
        "ceil": math.ceil(m_exact),
        "exact": m_exact,
    }
    out = {
        "cell": name,
        "p": p,
        "n": n,
        "omega": omega,
        "C_0": C0,
        "d_F": dF,
        "p_pow_C0": M,
        "m_exact": m_exact,
        "m_round_nearest_equals": "floor" if round(m_exact) == roundings["floor"] else "ceil",
        "coset_models": {},
        "readings": {},
    }
    for model in ("P1", "P2", "P3"):
        out["coset_models"][model] = coset_stats(model, M)

    for rname, m in roundings.items():
        is_int = isinstance(m, int)
        N = n * (m - 1)  # card's statement
        if is_int:
            T1 = log2_binom_int(N + dF, dF)
            T1_squarefree = log2_squarefree_count(N, dF)
            N_alt = m * k + (m - 2) * n  # literal variable count mk + (m-2)n
            T1_Nalt = log2_binom_int(N_alt + dF, dF)
        else:
            T1 = log2_binom_real(N + dF, dF)
            T1_squarefree = None
            N_alt = m * k + (m - 2) * n
            T1_Nalt = log2_binom_real(N_alt + dF, dF)
        T2 = (omega - 1.0) * T1
        Fb = m * M
        T3 = math.log2(Fb)
        T3_plus1 = math.log2(Fb + 1)
        T5_frozen = T1
        T5_dense = 2.0 * T1
        km_minus_n = k * m - n

        # ---- T4 readings
        t4 = {}
        # (a) arithmetic: E[prod #Fb_i] = (p^k)^m, / p^n
        L_arith = km_minus_n
        t4["arith"] = {
            "log2_lambda": L_arith,
            "lambda": 2.0 ** L_arith,
            "Pr": -math.expm1(-(2.0 ** L_arith)),
            "T4": t4_from_log2_lambda(L_arith),
            "definition": "lambda = E[prod_i #Fb_i]/p^n = p^{k m - n} (mean p^k per coset; any of P1/P2/P3)",
        }
        for model in ("P1", "P2", "P3"):
            st = out["coset_models"][model]
            # (a') arithmetic conditioned on all cosets nonempty
            L_ac = m * math.log2(st["mean_given_nonempty"]) - n
            t4[f"arith_cond_{model}"] = {
                "log2_lambda": L_ac,
                "T4": t4_from_log2_lambda(L_ac),
                "definition": "lambda = E[prod #Fb_i | all nonempty]/p^n = (E[X|X>0])^m / p^n",
            }
            # (b) geometric, conditioned on nonempty
            L_geo = m * st["E_log2_given_nonempty"] - n
            sd_geo = math.sqrt(m * st["Var_log2_given_nonempty"])
            t4[f"geo_cond_{model}"] = {
                "log2_lambda": L_geo,
                "sd_log2_lambda_across_instances": sd_geo,
                "T4": t4_from_log2_lambda(L_geo),
                "definition": "log2 lambda = sum_i E[log2 #Fb_i | #Fb_i > 0] - n (typical instance)",
            }
            # (b') geometric unconditioned: P(X=0) > 0 => E[log2 X] = -inf
            p_all = (1.0 - st["P_empty"]) ** m
            t4[f"geo_uncond_{model}"] = {
                "log2_lambda": float("-inf"),
                "T4": float("inf"),
                "P_all_cosets_nonempty": p_all,
                "definition": "E[log2 #Fb_i] = -inf since P[#Fb_i = 0] > 0; degenerate; P[all nonempty] reported instead",
            }
        # (c) instance-averaged success probability (integer m only)
        if is_int and do_inst:
            for model in ("P1", "P3"):
                e_pr, p_all, mean_S = instance_averaged_pr(model, M, m, n)
                t4[f"inst_avg_cond_{model}"] = {
                    "E_Pr_given_all_nonempty": e_pr,
                    "T4": -math.log2(e_pr),
                    "check_mean_log2_prod_from_grid": mean_S,
                    "definition": "T4 = -log2 E_instances[1 - exp(-lambda) | all cosets nonempty], FFT convolution on a 2^-10-bit grid",
                }
                t4[f"inst_avg_uncond_{model}"] = {
                    "E_Pr": e_pr * p_all,
                    "T4": -math.log2(e_pr * p_all),
                    "definition": "as inst_avg_cond times P[all nonempty] (an empty coset gives lambda = 0)",
                }
            mc_mean, mc_se, mc_pall = instance_averaged_pr_mc("P1", M, m, n)
            t4["inst_avg_cond_P1_montecarlo_check"] = {
                "E_Pr_given_all_nonempty": mc_mean,
                "standard_error": mc_se,
                "T4": -math.log2(mc_mean),
                "T4_pm_1se": [-math.log2(mc_mean + mc_se), -math.log2(mc_mean - mc_se)],
                "P_all_nonempty_empirical": mc_pall,
                "samples_conditioned": 1_000_000,
            }
        # (d) Nagao literal: "probability ... is O(1)" read as 1 -- NOT a HEUR-2 reading
        t4["nagao_literal_Pr_1_reference_only"] = {"T4": 0.0,
            "definition": "Pr = 1; not a HEUR-2 reading; equals ARM M's free-yield null; reference only"}

        # ---- time and margins per T4 reading (T3 without +1 is the card's statement)
        LA = omega * T3
        times = {}
        for key, val in t4.items():
            T4v = val["T4"]
            if math.isinf(T4v):
                times[key] = {"time": float("inf"), "time_with_T3_plus1": float("inf")}
                continue
            tm = log2_add(T1 + T2 + T3 + T4v, LA)
            tm1 = log2_add(T1 + T2 + T3_plus1 + T4v, omega * T3_plus1)
            times[key] = {"time": tm, "time_with_T3_plus1": tm1}

        out["readings"][rname] = {
            "m": m,
            "k_m_minus_n": km_minus_n,
            "N": N,
            "N_alt_mk_plus_m_minus_2_n": N_alt,
            "T1": T1,
            "T1_at_N_alt": T1_Nalt,
            "T1_squarefree_sum_C_N_d": T1_squarefree,
            "T1_nagao_loose_log2_N_pow_dF_reference": dF * math.log2(N),
            "T2": T2,
            "T1_plus_T2_one_solve": T1 + T2,
            "Fb": Fb,
            "T3": T3,
            "T3_plus1": T3_plus1,
            "linear_algebra_omega_T3": LA,
            "T4": t4,
            "T5_frozen": T5_frozen,
            "T5_dense": T5_dense,
            "time": times,
        }
    return out


def attach_margins(cell, vw):
    for rname, rd in cell["readings"].items():
        margins = {}
        for key, tv in rd["time"].items():
            t = tv["time"]
            margins[key] = {
                "margin_time_only": t - vw["time_only_bits"],
                "margin_product_frozen": (t + rd["T5_frozen"]) - vw["product_min_bits_analytic"],
                "margin_product_dense": (t + rd["T5_dense"]) - vw["product_min_bits_analytic"],
            }
        rd["margins"] = margins
        rd["vow_time_only"] = vw["time_only_bits"]
        rd["vow_product_minimum"] = vw["product_min_bits_analytic"]


def main():
    n = 571
    vw = vow(n)
    cells = {
        "cell_A": derive_cell("A", 2, n, 2.807, 8),
        "cell_B": derive_cell("B", 2, n, 3.0, 3),
    }
    for c in cells.values():
        attach_margins(c, vw)
    result = {
        "task_id": "TASK-20260913-7fb774",
        "review_round_id": "REVIEW-SEMBIN-20260913-251fd3",
        "attempt": 2,
        "units": {
            "T1..T4, time": "log2 of a count of F_2 (Weil-descent) operations / solves; no conversion to group operations",
            "T5": "log2 of a count of F_2 field elements (= bits for p = 2)",
            "vOW time": "log2 group operations (W = 0.886 * 2^{n/2})",
            "vOW memory": "log2 bits (3n per point)",
            "margins": "bits, Nagao minus vOW, positive = Nagao worse; NO unit conversion applied on either axis",
        },
        "vow_n571": vw,
        "cells": cells,
    }

    def clean(o):
        if isinstance(o, dict):
            return {k: clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [clean(v) for v in o]
        if isinstance(o, float):
            if math.isinf(o):
                return "+inf" if o > 0 else "-inf"
            return o
        return o

    json.dump(clean(result), sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
