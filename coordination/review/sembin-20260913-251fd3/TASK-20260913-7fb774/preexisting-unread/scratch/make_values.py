#!/usr/bin/env python3
"""Reshape scratch/rederive-output.json into the deliverable rederived-values.json."""
import json
import math

raw = json.load(open("scratch/rederive-output.json"))


def r6(x):
    if isinstance(x, str):
        return x
    if x is None:
        return None
    return round(x, 6)


T4_READINGS = {
    "arith": "lambda = E[prod #Fb_i]/p^n = p^{k m - n}; expectation of the PRODUCT (HEUR-2's own form; lambda = 1 at exact m)",
    "arith_cond_P1": "as arith but conditioned on every coset nonempty, P1 model: lambda = (E[X|X>0])^m / p^n",
    "geo_cond_P1": "expectation of the LOGARITHM, P1 = 2*Bin(p^k,1/2), conditioned on nonempty: log2 lambda = m E[log2 X | X>0] - n",
    "geo_cond_P2": "geometric, P2 = Bin(2 p^k, 1/2), conditioned on nonempty",
    "geo_cond_P3": "geometric, P3 = Poisson(p^k), conditioned on nonempty",
    "geo_uncond_P1": "geometric WITHOUT conditioning: E[log2 X] = -inf since P[X=0] > 0 => T4 = +inf (degenerate); P[all nonempty] reported",
    "inst_avg_cond_P1": "instance-averaged success probability: T4 = -log2 E[1 - exp(-lambda) | all nonempty], P1, exact grid convolution (integer m only)",
    "inst_avg_uncond_P1": "inst_avg_cond_P1 times P[all cosets nonempty] (an empty coset gives lambda = 0)",
    "inst_avg_cond_P3": "instance-averaged, P3 = Poisson(p^k), conditioned",
    "inst_avg_uncond_P3": "instance-averaged, P3, unconditioned",
    "nagao_literal_Pr_1_reference_only": "Pr = 1 (Nagao's 'O(1)' read as 1). NOT a HEUR-2 reading; equals the ARM M free-yield null; reference only",
}

out = {
    "task_id": raw["task_id"],
    "review_round_id": raw["review_round_id"],
    "attempt": raw["attempt"],
    "joint": "blind_rederivation",
    "precision_note": "values rounded to 6 decimals; computed in double precision from exact integer binomials (math.comb) at integer N and lgamma at non-integer N",
    "units": raw["units"],
    "statement_conventions": {
        "monomials": "C(N + 4, 4), N = n(m - 1), m = n / C_0",
        "T1": "log2 monomials", "T2": "(omega - 1) T1", "T3": "log2 #Fb, #Fb = m p^{C_0}",
        "T4": "log2(1/Pr), Pr = 1 - exp(-lambda), lambda = prod #Fb_i / p^n",
        "T5_frozen": "T1 (field elements)", "T5_dense": "2 T1 (field elements)",
        "time": "log2(2^{T1+T2+T3+T4} + 2^{omega T3})",
        "vow_time_only": "log2 W, W = 0.886 * 2^{n/2}, at M = 1, w -> inf",
        "vow_product_minimum": "min_{w,M} T*Mem = 6 n W, attained on the whole line w = M",
        "margin_time_only": "time - vow_time_only",
        "margin_product_frozen": "(time + T5_frozen) - vow_product_minimum",
        "margin_product_dense": "(time + T5_dense) - vow_product_minimum",
        "no_unit_conversion": "no conversion between F_2 operations and group operations, nor between F_2 elements and bits (identical for p = 2)",
    },
    "m_rounding_conventions": {
        "floor": "m = floor(n/C_0); then k m < n and lambda_arith = 2^{k m - n} < 1",
        "ceil": "m = ceil(n/C_0); then k m > n and lambda_arith > 1",
        "exact": "m = n/C_0 kept fractional (Semaev-Table-3 style un-ceiled parameter); N, #Fb fractional; C(N+4,4) via lgamma; lambda_arith = 1 exactly",
        "round_nearest": "equals floor at both cells (71.375 -> 71, 190.333 -> 190); not carried separately",
    },
    "T4_readings": T4_READINGS,
    "coset_size_models": {
        "P1": "#Fb_i = 2 * Bin(p^k, 1/2): x-map 2-to-1 onto a density-1/2 set, the justification HEUR-1 itself gives. mean p^k, var p^k. PRIMARY.",
        "P2": "#Fb_i = Bin(2 p^k, 1/2): literal 'binomial with mean p^k'. mean p^k, var p^k/2.",
        "P3": "#Fb_i = Poisson(p^k) (limit of Bin(#E, p^{k-n})). mean p^k, var p^k.",
    },
    "vow_n571": {k: (r6(v) if isinstance(v, float) else v) for k, v in raw["vow_n571"].items()},
    "cells": {},
}

for cname, c in raw["cells"].items():
    cell = {
        "parameters": {k: c[k] for k in ("p", "n", "omega", "C_0", "d_F", "p_pow_C0", "m_exact")},
        "coset_models": {mod: {k: r6(v) for k, v in st.items()} for mod, st in c["coset_models"].items()},
        "roundings": {},
    }
    for rname, rd in c["readings"].items():
        t4 = {k: r6(v["T4"]) for k, v in rd["T4"].items() if k in T4_READINGS}
        t4_detail = {}
        for k, v in rd["T4"].items():
            if k not in T4_READINGS:
                continue
            d = {}
            for f in ("log2_lambda", "sd_log2_lambda_across_instances", "P_all_cosets_nonempty",
                      "E_Pr_given_all_nonempty", "E_Pr"):
                if f in v:
                    d[f] = r6(v[f])
            if d:
                t4_detail[k] = d
        mc = rd["T4"].get("inst_avg_cond_P1_montecarlo_check")
        block = {
            "m": rd["m"],
            "k_m_minus_n": rd["k_m_minus_n"],
            "N": rd["N"],
            "N_alt_mk_plus_m_minus_2_n": rd["N_alt_mk_plus_m_minus_2_n"],
            "T1": r6(rd["T1"]),
            "T1_at_N_alt": r6(rd["T1_at_N_alt"]),
            "T1_squarefree_sum_C_N_d_le_4": r6(rd["T1_squarefree_sum_C_N_d"]),
            "T1_nagao_loose_4log2N_reference": r6(rd["T1_nagao_loose_log2_N_pow_dF_reference"]),
            "T2": r6(rd["T2"]),
            "T1_plus_T2_one_solve": r6(rd["T1_plus_T2_one_solve"]),
            "Fb": rd["Fb"],
            "T3": r6(rd["T3"]),
            "T3_plus1_log2_Fb_plus_1": r6(rd["T3_plus1"]),
            "linear_algebra_omega_T3": r6(rd["linear_algebra_omega_T3"]),
            "T4": t4,
            "T4_detail": t4_detail,
            "T5_frozen": r6(rd["T5_frozen"]),
            "T5_dense": r6(rd["T5_dense"]),
            "time": {k: r6(v["time"]) for k, v in rd["time"].items() if k in T4_READINGS},
            "time_with_T3_plus1": {k: r6(v["time_with_T3_plus1"]) for k, v in rd["time"].items() if k in T4_READINGS},
            "vow_time_only": r6(rd["vow_time_only"]),
            "vow_product_minimum": r6(rd["vow_product_minimum"]),
            "margin_time_only": {k: r6(v["margin_time_only"]) for k, v in rd["margins"].items() if k in T4_READINGS},
            "margin_product_frozen": {k: r6(v["margin_product_frozen"]) for k, v in rd["margins"].items() if k in T4_READINGS},
            "margin_product_dense": {k: r6(v["margin_product_dense"]) for k, v in rd["margins"].items() if k in T4_READINGS},
        }
        if mc:
            block["inst_avg_cond_P1_montecarlo_check"] = {
                "T4": r6(mc["T4"]), "E_Pr": r6(mc["E_Pr_given_all_nonempty"]),
                "standard_error": mc["standard_error"], "samples": mc["samples_conditioned"],
                "note": "consistency check only; deterministic grid-convolution value is the reported one",
            }
        cell["roundings"][rname] = block

    ex = c["readings"]["exact"]
    cell["reading_implied_by_hypothesis_text"] = {
        "basis": "HEUR-2 formal_statement fixes the operating point prod #Fb_i ~ #E, lambda ~ 1, i.e. exact m = n/C_0 with the arithmetic expectation; this block is that reading, NOT a privileged truth",
        "rounding": "exact",
        "T4_reading": "arith",
        "m": ex["m"], "N": ex["N"],
        "T1": r6(ex["T1"]), "T2": r6(ex["T2"]), "T3": r6(ex["T3"]), "T4": r6(ex["T4"]["arith"]["T4"]),
        "T5_frozen": r6(ex["T5_frozen"]), "T5_dense": r6(ex["T5_dense"]),
        "time": r6(ex["time"]["arith"]["time"]),
        "vow_time_only": r6(ex["vow_time_only"]), "vow_product_minimum": r6(ex["vow_product_minimum"]),
        "margin_time_only": r6(ex["margins"]["arith"]["margin_time_only"]),
        "margin_product_frozen": r6(ex["margins"]["arith"]["margin_product_frozen"]),
        "margin_product_dense": r6(ex["margins"]["arith"]["margin_product_dense"]),
    }
    # spreads across readings
    fl, ce = c["readings"]["floor"], c["readings"]["ceil"]
    cell["spreads_bits"] = {
        "T1_floor_to_ceil": r6(ce["T1"] - fl["T1"]),
        "T3_floor_to_ceil": r6(ce["T3"] - fl["T3"]),
        "T4_arith_floor_minus_ceil": r6(fl["T4"]["arith"]["T4"] - ce["T4"]["arith"]["T4"]),
        "T4_geo_cond_P1_minus_arith_at_exact_m": r6(ex["T4"]["geo_cond_P1"]["T4"] - ex["T4"]["arith"]["T4"]),
        "T4_inst_avg_cond_P1_minus_arith_at_floor_m": r6(fl["T4"]["inst_avg_cond_P1"]["T4"] - fl["T4"]["arith"]["T4"]),
        "time_arith_floor_minus_ceil": r6(fl["time"]["arith"]["time"] - ce["time"]["arith"]["time"]),
        "time_range_over_all_finite_HEUR2_readings_and_roundings": [
            r6(min(v["time"] for rd in c["readings"].values() for k, v in rd["time"].items()
                   if k in T4_READINGS and k != "nagao_literal_Pr_1_reference_only" and not isinstance(v["time"], str))),
            r6(max(v["time"] for rd in c["readings"].values() for k, v in rd["time"].items()
                   if k in T4_READINGS and k != "nagao_literal_Pr_1_reference_only" and not isinstance(v["time"], str))),
        ],
    }
    out["cells"][cname] = cell

json.dump(out, open("rederived-values.json", "w"), indent=2)
print("wrote rederived-values.json")
