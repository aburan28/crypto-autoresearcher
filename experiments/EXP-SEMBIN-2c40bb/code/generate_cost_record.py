#!/usr/bin/env python3
"""Build COST-SEMBIN-e9960c.yaml FROM the run's JSON artifacts (never by hand), and
emit a figure map that verify_new_record.py re-checks against the same JSON files.

Every numeric figure in the record is copied programmatically from a named JSON path;
the map (path in YAML -> path in JSON) is written beside the record so the checker can
re-read both sides independently of this script's in-memory values.
"""

from __future__ import annotations

import argparse
import json
import os

import yaml

U = "unceiled_n_over_m_as_in_table3"
C = "ceil_n_over_m"
R = "record_point_M1_w30"
O = "own_curve_product_minimum"
X = "sect113r2_calibrated_ratio"
ST = ["dense_row_echelon", "semaev_sparse", "rows_times_cols_dense", "nonzeros_with_index_sparse"]


def load(run_dir, name):
    return json.load(open(os.path.join(run_dir, name)))


def jget(obj, path):
    for p in path:
        obj = obj[p]
    return obj


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--record-id", default="COST-SEMBIN-e9960c")
    args = ap.parse_args()
    rd = args.run_dir
    gate = load(rd, "reproduction-gate.json")
    surf = load(rd, "surface.json")
    armb = load(rd, "arm-b-coherent-baseline.json")
    armf = load(rd, "arm-f-fixed-budget.json")
    armi = load(rd, "sparse-implementation-comparison.json")
    ctrl = load(rd, "controls.json")
    meas = load(rd, "measurement-comparison.json")
    sens = load(rd, "sensitivities.json")

    figmap = {}   # yaml dotted path -> (json file, json path)

    def put(yaml_path, fname, jpath, src):
        figmap[yaml_path] = {"file": fname, "path": jpath}
        return jget(src, jpath)

    rec = {"concrete_cost": {
        "id": args.record_id,
        "hypothesis_id": "H-SEMBIN-97ea23",
        "experiment_id": "EXP-SEMBIN-2c40bb",
        "run_id": "RUN-SEMBIN-3ae91c",
        "supersedes_in_scope": "COST-SEMBIN-8d123b (its arithmetic is reproduced, not impeached; its one-slice framing is replaced by the surface)",
        "claim_tier": "heuristic_estimate",
        "bound_kind": "closed-form log2 estimates under stated heuristics; nothing computed at scale",
        "cost_unit": {"time": "log2 group operations (Semaev's field-operation counts converted at kappa)",
                      "memory": "log2 bits"},
        "algorithm_ref": "Semaev 2015 chained summation-polynomial index calculus, inputs/SEMAEV-2015-310/",
        "comparator_ref": ("van Oorschot-Wiener parallel collision search under HEUR-VOW-CURVE "
                           "(UNVALIDATED; internal restatement; primary paper NOT opened by any agent)"),
        "cell_label_fields": ["metric", "store_log2", "processors_log2", "baseline_charging_mode",
                              "kappa", "cofactor_h", "storage_reading", "k_reading", "m_selection"],
        "scan_domain_n": [3, 700],
        "reproduction_gate": {},
        "surface_ranges_per_storage_reading": {},
        "coherent_baseline": {},
        "fixed_memory_budget": {},
        "alpha_flip_threshold_at_409": {},
        "sparse_second_implementation": {},
        "matched_null_decomposition_product_metric": {},
        "measurement_comparison_C10": {},
        "kappa_and_cofactor_at_record_point_product_sparse": {},
        "degree_bound_sensitivity_GIVEN_not_measured": {},
        "controls": {},
        "optimistic_assumptions_semaev": [
            "Assumption 1 (degree bound 4) holds at every (n, m); degree is a GIVEN parameter here, never measured (IMP-SEMBIN-ENGINE)",
            "the block Groebner step costs n^(4 omega) as the paper asserts without implementation",
            "eq. (11)'s yield is realised (the 1/P factor is charged but no shortfall beyond it)",
            "relation store at m k + 2n bits per relation with no index overhead",
            "stage 2 at 2^(k omega') with omega' = 2",
            "un-ceiled k = n/m in TIME (Table 3's reading) while the relation store pays ceil(n/m); the ceiled reading is a labelled axis",
            "kappa = 1 treats one field operation as one group operation; kappa 10 and 100 are labelled axes",
        ],
        "optimistic_assumptions_baseline": [
            "HEUR-VOW-CURVE: T = W (1/M + 1/w), Mem = 3n max(w, M); an internal restatement, unvalidated against the primary paper",
            "near-linear parallel speedup at every processor count",
            "cofactor h = 1 overcharges the baseline by 0.5 log2(h) bits; h in {2, 4} are labelled axes (direction: baseline gets cheaper)",
            "no Frobenius discount except in the K-409 / K-571 sensitivity rows (0.5 log2 n bits, KN-TECH-018 reading)",
            "the walk constant 0.886 is relayed from KN-TECH-006 / KN-LIT-012",
        ],
        "interpretation_limits": [
            "NOTHING HERE IS A STATEMENT ABOUT THE SECURITY OF ANY CURVE IN EITHER DIRECTION; two heuristic cost models are compared",
            "a crossover is quoted only with its full cell label; the value alone is not a deliverable",
            "control C6 (prime-field nearby object) is UNREACHED; every row is reported without it",
            "agreement with recomputations.json is a comparison against this experiment's own input, not independent corroboration",
        ],
        "status": "observations_only; awaiting independent review",
    }}
    cc = rec["concrete_cost"]

    # --- reproduction gate
    g = cc["reproduction_gate"]
    g["cell"] = gate["cell"]
    g["passed"] = put("reproduction_gate.passed", "reproduction-gate.json", ["gate", "passed"], gate)
    g["largest_disagreement_vs_record_bits"] = put("reproduction_gate.largest_disagreement_vs_record_bits", "reproduction-gate.json",
                                                   ["largest_disagreement_vs_record_bits"], gate)
    g["largest_disagreement_vs_red_team_bits"] = put("reproduction_gate.largest_disagreement_vs_red_team_bits", "reproduction-gate.json",
                                                     ["largest_disagreement_vs_red_team_recomputations_bits"], gate)
    g["crossovers"] = {}
    for pm, rs in (("time_only_zero_memory_weight", "dense"), ("time_only_zero_memory_weight", "semaev_sparse"),
                   ("time_memory_product", "dense"), ("time_memory_product", "semaev_sparse")):
        g["crossovers"][f"{pm}/{rs}"] = put(f"reproduction_gate.crossovers.{pm}/{rs}", "reproduction-gate.json",
                                            ["crossovers", pm, rs, "recomputed"], gate)
    for k in ("time_only", "product_dense", "product_sparse"):
        g[f"margin_409_{k}"] = put(f"reproduction_gate.margin_409_{k}", "reproduction-gate.json", ["n409", k], gate)

    # --- surface ranges
    for st in ST:
        for kr in (U, C):
            e = surf["crossover_ranges"][st][kr]["stage1_argmin/persistent_crossover_n"]
            key = f"{st}/{kr}"
            d = {}
            for fld, short in (("over_store_declared_grid_30_40_48_60_product_metric", "store_declared_grid_range"),
                               ("over_store_full_grid_product_metric", "store_full_grid_range"),
                               ("over_parent_metric_set_time_only_and_product_at_store30", "parent_metric_set_range"),
                               ("over_full_metric_set_28_instances_at_store30", "full_metric_set_range"),
                               ("over_processors_product_metric_store30", "processors_range"),
                               ("over_baseline_mode_product_metric_store30", "baseline_mode_range"),
                               ("over_kappa_product_metric_store30", "kappa_range"),
                               ("over_cofactor_product_metric_store30", "cofactor_range")):
                d[short] = put(f"surface_ranges_per_storage_reading.{key}.{short}", "surface.json",
                               ["crossover_ranges", st, kr, "stage1_argmin/persistent_crossover_n", fld, "range"], surf)
                d[short + "_values"] = put(f"surface_ranges_per_storage_reading.{key}.{short}_values", "surface.json",
                                           ["crossover_ranges", st, kr, "stage1_argmin/persistent_crossover_n", fld, "values"], surf)
            d["store_range_exceeds_parent_metric_range"] = put(
                f"surface_ranges_per_storage_reading.{key}.store_range_exceeds_parent_metric_range", "surface.json",
                ["crossover_ranges", st, kr, "stage1_argmin/persistent_crossover_n",
                 "store_range_exceeds_metric_range_declared_grid_vs_parent_metric_set"], surf)
            d["cell_label_fixed"] = {"processors_log2": 0, "kappa": 1, "cofactor_h": 1, "baseline_charging_mode": R,
                                     "storage_reading": st, "k_reading": kr, "m_selection": "stage1_argmin",
                                     "metric_for_store_sweeps": "time_memory_product", "store_log2_for_metric_sweeps": 30,
                                     "crossover_definition": "persistent_crossover_n over [3,700]"}
            cc["surface_ranges_per_storage_reading"][key] = d
    cc["collision_pairs_total"] = put("collision_pairs_total", "surface.json", ["collisions", "total_colliding_pairs"], surf)

    # --- coherent baseline
    for st in ST:
        for kr in (U,):
            for msel in ("stage1_argmin", "metric_reoptimised"):
                key = f"{st}/{kr}/{msel}"
                d = {"cell_label_fixed": {"metric": "time_memory_product", "store_log2": 30, "processors_log2": 0,
                                          "kappa": 1, "cofactor_h": 1, "storage_reading": st, "k_reading": kr, "m_selection": msel}}
                for mode in (R, O, X):
                    for f in ("persistent_crossover_n", "margin_409_bits", "margin_571_bits"):
                        d[f"{mode}.{f}"] = put(f"coherent_baseline.{key}.{mode}.{f}", "arm-b-coherent-baseline.json",
                                               ["per_k_reading", kr, st, "modes", f"{mode}/{msel}", f], armb)
                d["shift_record_to_own_curve_in_n"] = put(f"coherent_baseline.{key}.shift_record_to_own_curve_in_n", "arm-b-coherent-baseline.json",
                                                           ["per_k_reading", kr, st, f"shift_record_to_own_curve/{msel}", "in_n_persistent"], armb)
                d["shift_record_to_own_curve_in_bits_at_409"] = put(f"coherent_baseline.{key}.shift_record_to_own_curve_in_bits_at_409", "arm-b-coherent-baseline.json",
                                                                     ["per_k_reading", kr, st, f"shift_record_to_own_curve/{msel}", "in_bits_at_409"], armb)
                cc["coherent_baseline"][key] = d
    cc["coherent_baseline"]["vow_product_excess_bits_per_n"] = {
        n: put(f"coherent_baseline.vow_product_excess_bits_per_n.{n}", "arm-b-coherent-baseline.json",
               ["vow_product_excess_per_n", n, "excess_bits"], armb) for n in armb["vow_product_excess_per_n"]}
    cc["coherent_baseline"]["sect113r2_excess_bits_per_n"] = {
        n: put(f"coherent_baseline.sect113r2_excess_bits_per_n.{n}", "arm-b-coherent-baseline.json",
               ["vow_product_excess_per_n", n, "sect113r2_excess_bits"], armb) for n in armb["vow_product_excess_per_n"]}
    cc["coherent_baseline"]["pareto_min_of_own_curves_at_409"] = {}
    for st in ST:
        for f in ("semaev_min_product_log2", "m_attaining", "m_within_1_bit", "margin_vs_vow_min_product_bits"):
            cc["coherent_baseline"]["pareto_min_of_own_curves_at_409"][f"{st}.{f}"] = put(
                f"coherent_baseline.pareto_min_of_own_curves_at_409.{st}.{f}", "arm-b-coherent-baseline.json",
                ["pareto_min_of_own_curves_at_fips_n", "409", f"{st}/{U}", f], armb)

    # --- fixed budget
    for n in ("409", "571"):
        for st in ST:
            key = f"n{n}/{st}/{U}/{R}"
            d = {"cell_label_fixed": {"store_log2": 30, "processors_log2": 0, "kappa": 1, "cofactor_h": 1,
                                      "baseline_charging_mode": R, "storage_reading": st, "k_reading": U,
                                      "m_selection": "metric_reoptimised"}}
            for f in ("semaev_cheapest_memory_log2_bits", "m_attaining_cheapest_memory", "m_within_1_bit_of_cheapest_memory",
                      "hard_budget_threshold_log2_bits", "hard_threshold_m", "soft_budget_threshold_log2_bits", "soft_threshold_m"):
                d[f] = put(f"fixed_memory_budget.{key}.{f}", "arm-f-fixed-budget.json", ["per_fips_n", n, f"{st}/{U}/{R}", f], armf)
            d["hard_verdicts_by_budget_log2"] = {B: put(f"fixed_memory_budget.{key}.hard_verdicts_by_budget_log2.{B}", "arm-f-fixed-budget.json",
                                                        ["per_fips_n", n, f"{st}/{U}/{R}", "hard_verdict_by_budget", B, "verdict"], armf)
                                                 for B in armf["per_fips_n"][n][f"{st}/{U}/{R}"]["hard_verdict_by_budget"]}
            d["soft_verdicts_by_budget_log2"] = {B: put(f"fixed_memory_budget.{key}.soft_verdicts_by_budget_log2.{B}", "arm-f-fixed-budget.json",
                                                        ["per_fips_n", n, f"{st}/{U}/{R}", "soft_verdict_by_budget", B, "verdict"], armf)
                                                 for B in armf["per_fips_n"][n][f"{st}/{U}/{R}"]["soft_verdict_by_budget"]}
            cc["fixed_memory_budget"][key] = d
        for pair in ("dense_row_echelon|semaev_sparse", "rows_times_cols_dense|nonzeros_with_index_sparse"):
            for reading in ("hard", "soft"):
                bkey = f"{pair}/{U}/{R}/{reading}"
                cc["fixed_memory_budget"][f"disagreement_band_n{n}/{bkey}"] = put(
                    f"fixed_memory_budget.disagreement_band_n{n}/{bkey}", "arm-f-fixed-budget.json",
                    ["disagreement_bands", n, bkey], armf)

    # --- alpha flip
    for st in ST:
        for f in ("alpha_star_closed_form_stage1_argmin_m", "flip_inside_0_1_stage1_argmin",
                  "first_alpha_where_semaev_loses_metric_reoptimised_m_step_0p001"):
            cc["alpha_flip_threshold_at_409"][f"{st}.{f}"] = put(f"alpha_flip_threshold_at_409.{st}.{f}", "arm-f-fixed-budget.json",
                                                                 ["alpha_flip", "409", f"{st}/{U}/{R}", f], armf)
    cc["alpha_flip_threshold_at_409"]["cell_label_fixed"] = {"metric": "memory_weighted_time_alpha", "store_log2": 30,
                                                             "processors_log2": 0, "baseline_charging_mode": R, "kappa": 1,
                                                             "cofactor_h": 1, "k_reading": U}

    # --- ARM I
    si = cc["sparse_second_implementation"]
    si["largest_cellwise_disagreement_bits"] = put("sparse_second_implementation.largest_cellwise_disagreement_bits",
                                                   "sparse-implementation-comparison.json", ["largest_cellwise_disagreement_bits"], armi)
    si["cells_compared"] = put("sparse_second_implementation.cells_compared", "sparse-implementation-comparison.json", ["cells_compared"], armi)
    for f in ("columns_log2", "nonzeros_per_row_log2", "total_nonzeros_log2"):
        si[f"n571_{f}"] = put(f"sparse_second_implementation.n571_{f}", "sparse-implementation-comparison.json",
                              ["kn_lit_e77232_n571_check", "recomputed", f], armi)
    si["n571_agrees_with_KN_LIT_e77232_at_printed_precision"] = put(
        "sparse_second_implementation.n571_agrees_with_KN_LIT_e77232_at_printed_precision",
        "sparse-implementation-comparison.json", ["kn_lit_e77232_n571_check", "all_agree"], armi)
    si["independence_deviation"] = armi["independence_deviation"]

    # --- matched null
    for st in ST:
        key = f"time_memory_product/{st}/{U}"
        e = ctrl["C3_informative_matched_null"]["per_metric_and_storage"][key]
        d = {"cell": e["cell"]}
        for f in e["decomposition_in_n"]:
            d[f"in_n: {f}"] = put(f"matched_null_decomposition_product_metric.{st}.in_n: {f}", "controls.json",
                                  ["C3_informative_matched_null", "per_metric_and_storage", key, "decomposition_in_n", f], ctrl)
        d["zero_memory_comparator"] = e["zero_memory_comparator"]["status"]
        cc["matched_null_decomposition_product_metric"][st] = d

    # --- C10
    m = cc["measurement_comparison_C10"]
    m["rows_compared"] = put("measurement_comparison_C10.rows_compared", "measurement-comparison.json", ["rows_compared"], meas)
    for st in ST:
        for f in ("reading_A_upper_bounds_every_row", "reading_A_rows_exceeded", "reading_B_upper_bounds_every_row",
                  "reading_B_rows_exceeded", "min_residual_A", "min_residual_B"):
            m[f"{st}.{f}"] = put(f"measurement_comparison_C10.{st}.{f}", "measurement-comparison.json",
                                 ["upper_bound_check_per_reading", st, f], meas)
    m["column_reading_dispute_NOT_settled"] = meas["column_reading_dispute_NOT_settled"]
    m["dense_minus_sparse_gap_bits"] = {str(gp["n"]) + f"/t{gp['t']}": gp["dense_minus_sparse_bits"]
                                        for gp in meas["dense_minus_sparse_gap_measured_scale_to_fips"]}

    # --- kappa / cofactor / degree
    kc = cc["kappa_and_cofactor_at_record_point_product_sparse"]
    for i, r in enumerate(sens["kappa"]):
        c = r["cell"]
        if c["metric"] == "time_memory_product" and c["storage_reading"] == "semaev_sparse":
            kc[f"kappa_{c['kappa']}_persistent_crossover_n"] = put(
                f"kappa_and_cofactor_at_record_point_product_sparse.kappa_{c['kappa']}_persistent_crossover_n",
                "sensitivities.json", ["kappa", i, "persistent_crossover_n"], sens)
    for i, r in enumerate(sens["cofactor"]):
        c = r["cell"]
        if c["metric"] == "time_memory_product" and c["storage_reading"] == "semaev_sparse":
            kc[f"cofactor_h{c['cofactor_h']}_persistent_crossover_n"] = put(
                f"kappa_and_cofactor_at_record_point_product_sparse.cofactor_h{c['cofactor_h']}_persistent_crossover_n",
                "sensitivities.json", ["cofactor", i, "persistent_crossover_n"], sens)
    kc["cell_label_fixed"] = {"metric": "time_memory_product", "store_log2": 30, "processors_log2": 0,
                              "baseline_charging_mode": R, "storage_reading": "semaev_sparse", "k_reading": U,
                              "m_selection": "stage1_argmin"}
    kc["cofactor_direction"] = "baseline time - 0.5 log2(h); the baseline gets cheaper; crossover moves UP"
    for i, r in enumerate(sens["curve_labels"]):
        c = r["cell"]
        if c["metric"] == "time_memory_product" and c["baseline_charging_mode"] == R and c["storage_reading"] == "semaev_sparse":
            kc[f"{r['curve_label']}_margin_bits_cofactor_and_frobenius"] = put(
                f"kappa_and_cofactor_at_record_point_product_sparse.{r['curve_label']}_margin_bits_cofactor_and_frobenius",
                "sensitivities.json", ["curve_labels", i, "margin_bits_cofactor_and_frobenius"], sens)
            kc[f"{r['curve_label']}_frobenius_discount_bits"] = put(
                f"kappa_and_cofactor_at_record_point_product_sparse.{r['curve_label']}_frobenius_discount_bits",
                "sensitivities.json", ["curve_labels", i, "frobenius_discount_bits"], sens)
    kc["curve_cofactor_provenance"] = sens["curve_labels"][0]["cofactor_provenance"]
    dg = cc["degree_bound_sensitivity_GIVEN_not_measured"]
    for i, r in enumerate(sens["omega_x_degree"]):
        c = r["cell"]
        if (c["metric"] == "time_memory_product" and c["baseline_charging_mode"] == R and c["omega"] == 3.0
                and c["storage_reading"] in ("dense_row_echelon", "semaev_sparse")):
            dg[f"{c['storage_reading']}_degree_{c['degree_bound_GIVEN_not_measured']}_persistent_crossover_n"] = put(
                f"degree_bound_sensitivity_GIVEN_not_measured.{c['storage_reading']}_degree_{c['degree_bound_GIVEN_not_measured']}_persistent_crossover_n",
                "sensitivities.json", ["omega_x_degree", i, "persistent_crossover_n"], sens)
            dg[f"{c['storage_reading']}_degree_{c['degree_bound_GIVEN_not_measured']}_margin_409_bits"] = put(
                f"degree_bound_sensitivity_GIVEN_not_measured.{c['storage_reading']}_degree_{c['degree_bound_GIVEN_not_measured']}_margin_409_bits",
                "sensitivities.json", ["omega_x_degree", i, "margin_409_bits"], sens)
    dg["note"] = ("the semaev_sparse formula (nm)^4/24 x n^3/m contains no degree, so it is degree-INSENSITIVE by construction; "
                  "only the Macaulay-width readings move with the given bound")

    # --- controls
    cs = cc["controls"]
    cs["C1_reproduction_gate_passed"] = put("controls.C1_reproduction_gate_passed", "controls.json", ["C1_reproduction_gate", "passed"], ctrl)
    cs["C2_table3_cells_truncated_3sf"] = put("controls.C2_table3_cells_truncated_3sf", "controls.json",
                                              ["C2_table3_baseline_reproduction", "cells_agreeing_truncated_3sf"], ctrl)
    cs["C2_table3_cells_within_0p7pct"] = put("controls.C2_table3_cells_within_0p7pct", "controls.json",
                                              ["C2_table3_baseline_reproduction", "cells_within_0p7pct"], ctrl)
    cs["C2_crossover_papers_convention"] = put("controls.C2_crossover_papers_convention", "controls.json",
                                               ["C2_table3_baseline_reproduction", "crossover_papers_own_convention_stage1_vs_bare_2_pow_n_half"], ctrl)
    cs["C3_baseline_store_contribution_near_zero"] = put("controls.C3_baseline_store_contribution_near_zero", "controls.json",
                                                         ["C3_informative_matched_null", "baseline_store_contribution_near_zero"], ctrl)
    cs["C3_zero_memory_comparator_under_memory_metrics"] = "DEGENERATE (log2(0) = -inf); reported as such, never as a share"
    cs["C4_free_yield_passed"] = put("controls.C4_free_yield_passed", "controls.json", ["C4_known_false_free_yield", "passed"], ctrl)
    cs["C5_eq4_typo_detector_passed_by_bits"] = [put(f"controls.C5_eq4_typo_detector_passed_by_bits[{i}]", "controls.json",
                                                     ["C5_known_false_eq4_typo_detector", "rows", i, "margin_bits"], ctrl) for i in range(3)]
    cs["C5_status"] = "typo detector only; NOT a validity check on the cost model"
    cs["C6_prime_field_nearby_object"] = "UNREACHED -- see arm-n-prime-field-control.json for the concrete missing pieces"
    cs["C7_sparse_second_implementation_largest_disagreement_bits"] = si["largest_cellwise_disagreement_bits"]
    cs["C8_scan_domain"] = [3, 700]
    cs["C9_invalid_input_rejection_passed"] = put("controls.C9_invalid_input_rejection_passed", "controls.json",
                                                  ["C9_invalid_input_rejection", "passed"], ctrl)
    cs["C10_see"] = "measurement_comparison_C10"

    out_yaml = os.path.join(rd, f"{args.record_id}.yaml")
    with open(out_yaml, "w") as fh:
        yaml.safe_dump(rec, fh, sort_keys=False, width=110, allow_unicode=True)
    with open(os.path.join(rd, f"{args.record_id}.figure-map.json"), "w") as fh:
        json.dump(figmap, fh, indent=1)
    print(f"wrote {out_yaml} with {len(figmap)} mapped figures")


if __name__ == "__main__":
    main()
