#!/usr/bin/env python3
"""Project rederive-output.json onto the deliverable schema for
rederived-values.json (task TASK-20260913-7fb774), and print a readable digest."""
from __future__ import annotations

import json
import math
import sys

SRC = "rederive-output.json"
DST = "../rederived-values.json"

R_KEYS = [
    ("R1_nominal_lambda_equals_1", "R1_nominal_lambda_1"),
    ("R2_arithmetic_E_of_product", "R2_arithmetic_E_product"),
    ("R3_geometric_E_of_log_product__P-b_poisson", "R3_geometric_conditional_poisson"),
    ("R3_geometric_E_of_log_product__P-a_pairs", "R3_geometric_conditional_pairs"),
    ("R4_monte_carlo_E_of_success_probability__P-b_poisson", "R4_mc_E_of_Pr_poisson"),
    ("R4_monte_carlo_E_of_success_probability__P-a_pairs", "R4_mc_E_of_Pr_pairs"),
]


def r3(x):
    if x is None:
        return None
    if isinstance(x, str):
        return x
    if isinstance(x, float) and (math.isinf(x) or math.isnan(x)):
        return "inf" if x > 0 else "-inf"
    return round(float(x), 4)


def main():
    src = json.load(open(SRC))
    out = {
        "task_id": "TASK-20260913-7fb774",
        "review_round_id": "REVIEW-SEMBIN-20260913-251fd3",
        "attempt": 2,
        "produced_by": "blind re-derivation; scratch/rederive.py, seed 20260914, "
                       f"{src['monte_carlo_samples']} Monte Carlo samples per (cell, coset model)",
        "units": src["conventions"]["units"],
        "conventions": src["conventions"],
        "all_values_in": "bits (log2 domain)",
        "cells": {},
    }

    for label, cd in src["cells"].items():
        vow = cd["vow"]
        cell_out = {
            "inputs": cd["inputs"],
            "m_exact": cd["m_exact"],
            "m_by_rounding": {k: v["m"] for k, v in cd["by_rounding"].items()},
            "heur1_per_coset_models": {
                k: {kk: r3(vv) if kk != "model" else vv for kk, vv in v.items()}
                for k, v in cd["per_coset_models_HEUR1"].items()
            },
            "vow_time_only": r3(vow["time_only_bits"]),
            "vow_product_minimum": r3(vow["time_memory_product_min_bits__mem_in_bits"]),
            "vow_product_minimum_variant_mem_in_points": r3(vow["time_memory_product_min_bits__mem_in_points"]),
            "vow_log2_W": r3(vow["log2_W_group_operations"]),
            "vow_product_min_locus": vow["product_min_locus"],
            "by_rounding": {},
        }
        for rname, e in cd["by_rounding"].items():
            t4 = {}
            for src_key, short in R_KEYS:
                blk = e["T4"].get(src_key)
                if blk is None:
                    continue
                if src_key.startswith("R4_"):
                    t4[short + "__unconditional"] = r3(blk["T4_bits_from_E_success_unconditional"])
                    t4[short + "__given_all_nonempty"] = r3(blk["T4_bits_from_E_success_given_all_nonempty"])
                elif src_key.startswith("R3_"):
                    t4[short] = r3(blk["T4_bits_given_all_nonempty"])
                    t4[short + "__unconditional"] = "inf"
                else:
                    t4[short] = r3(blk["T4_bits"])
            charged = {}
            for cname, ch in e["charged"].items():
                short = cname
                for src_key, s in R_KEYS:
                    short = short.replace(src_key, s)
                charged[short] = {
                    "T4_used": r3(ch["T4_bits_used"]),
                    "time": r3(ch["time_bits"]),
                    "margin_time_only": r3(ch["margin_time_only_bits"]),
                    "margin_product_frozen": r3(ch["margin_product_frozen_bits"]),
                    "margin_product_dense": r3(ch["margin_product_dense_bits"]),
                    "margin_product_frozen__vow_mem_in_points": r3(ch["margin_product_frozen_bits__vow_mem_in_points"]),
                    "margin_product_dense__vow_mem_in_points": r3(ch["margin_product_dense_bits__vow_mem_in_points"]),
                }
            cell_out["by_rounding"][rname] = {
                "m": e["m"],
                "m_is_integer": e["m_is_integer"],
                "m_times_C0_minus_n": e["m_times_C0_minus_n"],
                "N": e["N_variables_statement_n_times_m_minus_1"],
                "T1": r3(e["T1_bits"]),
                "T2": r3(e["T2_bits"]),
                "T1_plus_T2_one_solve": r3(e["T1_plus_T2_one_solve_bits"]),
                "T1_variants": {
                    "exact_EQS4_variable_count": {
                        "N": e["T1_variants"]["exact_EQS4_variable_count_mC0_plus_n_m_minus_2"]["N"],
                        "T1": r3(e["T1_variants"]["exact_EQS4_variable_count_mC0_plus_n_m_minus_2"]["T1_bits"]),
                    },
                    "squarefree_sum_C_N_d": r3(e["T1_variants"]["squarefree_sum_d_le_4_C_N_d_bits"]),
                    "nagao_lemma2_loose_N_to_dF": r3(e["T1_variants"]["nagao_lemma2_loose_N_to_the_dF_bits"]),
                },
                "Fb_size": e["Fb_size"],
                "T3": r3(e["T3_bits"]),
                "T3_plus_one_relation": r3(e["T3_bits_plus_one_relation"]),
                "T4_by_reading": t4,
                "T5_frozen": r3(e["T5_frozen_bits"]),
                "T5_dense": r3(e["T5_dense_bits"]),
                "omega_times_T3": r3(e["omega_times_T3_bits"]),
                "linear_algebra_log_add_contribution": r3(
                    list(e["charged"].values())[0]["linear_algebra_log_add_contribution_bits"]),
                "charged_by_T4_reading": charged,
            }
        out["cells"][label] = cell_out

    # flat block: exactly the field names the task card asks for, one record per
    # (m rounding, T4 reading) pair, so no reading is silently privileged.
    for label, cd in out["cells"].items():
        flat = {}
        for rname, e in cd["by_rounding"].items():
            for cname, ch in e["charged_by_T4_reading"].items():
                flat[f"m_rounding={rname} | T4_reading={cname}"] = {
                    "m": e["m"],
                    "N": e["N"],
                    "T1": e["T1"],
                    "T2": e["T2"],
                    "T3": e["T3"],
                    "T4": ch["T4_used"],
                    "T5_frozen": e["T5_frozen"],
                    "T5_dense": e["T5_dense"],
                    "time": ch["time"],
                    "vow_time_only": cd["vow_time_only"],
                    "vow_product_minimum": cd["vow_product_minimum"],
                    "margin_time_only": ch["margin_time_only"],
                    "margin_product_frozen": ch["margin_product_frozen"],
                    "margin_product_dense": ch["margin_product_dense"],
                }
        # the degenerate unconditional geometric reading, recorded rather than dropped
        for rname, e in cd["by_rounding"].items():
            for key in e["T4_by_reading"]:
                if key.endswith("__unconditional") and e["T4_by_reading"][key] == "inf":
                    flat[f"m_rounding={rname} | T4_reading={key}"] = {
                        "m": e["m"], "N": e["N"], "T1": e["T1"], "T2": e["T2"], "T3": e["T3"],
                        "T4": "inf", "T5_frozen": e["T5_frozen"], "T5_dense": e["T5_dense"],
                        "time": "inf",
                        "vow_time_only": cd["vow_time_only"],
                        "vow_product_minimum": cd["vow_product_minimum"],
                        "margin_time_only": "inf",
                        "margin_product_frozen": "inf",
                        "margin_product_dense": "inf",
                        "note": "E[log2 #Fb_i] = -inf because P[#Fb_i = 0] > 0, so lambda = 0 on a "
                                "positive-probability set of factor bases and no R decomposes at all "
                                "for those; recorded, not dropped",
                    }
        cd["flat_by_rounding_and_reading"] = flat

    # spreads: how much each ambiguity is worth, per cell
    for label, cd in out["cells"].items():
        times, t4s = [], []
        for rname, e in cd["by_rounding"].items():
            for cname, ch in e["charged_by_T4_reading"].items():
                if isinstance(ch["time"], str):
                    continue
                times.append((ch["time"], rname, cname))
                t4s.append((ch["T4_used"], rname, cname))
        tmin, tmax = min(times), max(times)
        int_r = [r for r in cd["by_rounding"] if cd["by_rounding"][r]["m_is_integer"]] \
            if any("m_is_integer" in v for v in cd["by_rounding"].values()) else None
        rd = cd["by_rounding"]
        cd["spreads_bits"] = {
            "time_over_all_readings": {"min": tmin[0], "at_min": [tmin[1], tmin[2]],
                                       "max": tmax[0], "at_max": [tmax[1], tmax[2]],
                                       "spread": round(tmax[0] - tmin[0], 4)},
            "T4_over_all_readings": {"min": min(t4s)[0], "max": max(t4s)[0],
                                     "spread": round(max(t4s)[0] - min(t4s)[0], 4)},
            "T1_over_m_roundings": round(max(v["T1"] for v in rd.values())
                                         - min(v["T1"] for v in rd.values()), 4),
            "T3_over_m_roundings": round(max(v["T3"] for v in rd.values())
                                         - min(v["T3"] for v in rd.values()), 4),
        }

    json.dump(out, open(DST, "w"), indent=1)

    # digest
    for label, cd in out["cells"].items():
        print("=" * 78)
        print("CELL", label, cd["inputs"], "m_exact", cd["m_exact"]["rational"])
        print(" vOW: time_only=%s  product_min=%s (mem in bits)  product_min(points)=%s"
              % (cd["vow_time_only"], cd["vow_product_minimum"],
                 cd["vow_product_minimum_variant_mem_in_points"]))
        print(" spreads:", json.dumps(cd["spreads_bits"]))
        for rname, e in cd["by_rounding"].items():
            print(" --", rname, "m=", e["m"], "mC0-n=", e["m_times_C0_minus_n"], "N=", e["N"])
            print("    T1=%s T2=%s solve=%s T3=%s T5f=%s T5d=%s wT3=%s"
                  % (e["T1"], e["T2"], e["T1_plus_T2_one_solve"], e["T3"],
                     e["T5_frozen"], e["T5_dense"], e["omega_times_T3"]))
            print("    T4:", json.dumps(e["T4_by_reading"]))
            for cname, ch in e["charged_by_T4_reading"].items():
                print("      %-58s time=%-10s to=%-10s pf=%-10s pd=%s"
                      % (cname, ch["time"], ch["margin_time_only"],
                         ch["margin_product_frozen"], ch["margin_product_dense"]))
    print("\nwrote", DST)


if __name__ == "__main__":
    sys.exit(main())
