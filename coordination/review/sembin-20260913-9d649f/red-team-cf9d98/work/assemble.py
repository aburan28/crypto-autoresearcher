#!/usr/bin/env python3
"""Assemble recomputations.json for TASK-20260913-cf9d98 from the work outputs."""

from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "recomputations.json")


def load(name):
    with open(os.path.join(HERE, name)) as fh:
        return json.load(fh)


p1 = load("out.json")
p2 = load("out2.json")
p3 = load("out3.json")
p4 = load("out4.json")
p5 = load("out5.json")
pn = load("plan_N_check.json")
ps = load("plan_sparse_check.json")

doc = {
    "task_id": "TASK-20260913-cf9d98",
    "review_round": "REVIEW-SEMBIN-20260913-9d649f",
    "role": "red-team",
    "joints_owned": ["J2", "J3", "J5", "J6"],
    "generated_by": [
        "work/redteam_recompute.py",
        "work/redteam_recompute2.py",
        "work/redteam_combined.py",
        "work/redteam_extend.py",
        "work/redteam_pf_store.py",
    ],
    "independence": {
        "imports_producer_code": False,
        "checked_how": ("grep of every import statement in the five scripts: "
                        "json, math, os, re, statistics and this task's own "
                        "modules only"),
        "producer_artifacts_read_as_DATA_not_code": [
            "experiments/EXP-SEMBIN-f4a17b/runs/RUN-SEMBIN-121b59/raw-result.json",
            "experiments/EXP-SEMBIN-f4a17b/runs/RUN-SEMBIN-121b59/COST-SEMBIN-8d123b.yaml",
            "experiments/EXP-SEMBIN-f4a17b/runs/RUN-SEMBIN-121b59/manifest.yaml",
            "experiments/EXP-SEMBIN-81dc96/runs/RUN-SEMBIN-aa5161/raw-result.json",
            "experiments/EXP-SEMBIN-81dc96/runs/RUN-SEMBIN-aa5161/manifest.yaml",
            "experiments/EXP-PFDR-c04716/runs/STATIC-001/concrete-cost.yaml",
        ],
        "limitation": (
            "the memory MODEL is taken as the record states it -- J1 owns the "
            "accounting, this task owns the comparison. The sparse "
            "working-set restatement was fitted to reproduce the record and is "
            "validated against raw-result.json at the five (n, m) pairs that "
            "file exposes, all at the time-argmin m; off-argmin agreement is "
            "bounded in J3_sparse_restatement_robustness and not assumed."),
    },

    "step0_reproduction_of_the_record": {
        "worst_absolute_disagreement_bits":
            p1["step0_validation_against_the_record"]["worst_abs_diff_bits"],
        "reproduces_every_quoted_crossover":
            p1["step0_validation_against_the_record"]["reproduces_record"],
        "crossovers_recomputed":
            p1["step0_validation_against_the_record"]["crossovers_recomputed"],
        "per_n": p1["step0_validation_against_the_record"]["per_n"],
        "reading": ("an independent reimplementation reproduces all 35 quoted "
                    "figures to 4.8e-5 bits and all four crossovers exactly, "
                    "so every objection below is about the MODEL"),
    },

    "J2_baseline_charged_symmetrically": {
        "verdict": "breaks",
        "a_store_log2_sweep": p1["J2_store_sweep"],
        "b_coherent_vow_operating_point": p1["J2_coherent_vow_tradeoff"],
        "b_dp_time_penalty_at_the_records_own_operating_point":
            p1["J2_dp_time_penalty"],
        "c_walk_constant_and_d_fips_cofactor": p1["J2_small_corrections"],
        "attribution_control_rerun": p1["J2_matched_null_rerun"],
        "attribution_decomposition_the_record_owes":
            p2["F_attribution_decomposition"],
        "combined_scenarios_both_directions": p3,
        "headline_numbers": {
            "crossover_range_over_store_log2_0_to_60_dense": 522 - 342,
            "crossover_range_over_store_log2_0_to_60_sparse": 462 - 279,
            "crossover_range_over_the_metric_choice_dense": 435 - 303,
            "crossover_range_over_the_metric_choice_sparse": 375 - 303,
            "bits_the_record_overcharges_vow_memory_vs_its_own_curve_minimum": 29.0,
            "crossover_at_the_coherent_vow_point": {"dense": 520,
                                                    "sparse": 460},
            "shift_in_n_attributable_to_the_baseline_store": -87,
            "net_shift_the_record_reports": {"dense": 132, "sparse": 72},
            "dp_tail_time_penalty_bits_at_M_equals_1": 0.0,
            "walk_constant_effect_bits": 0.1746,
            "walk_constant_effect_in_n": 1,
            "fips_cofactor_effect_bits": {"h=2": 0.5, "h=4": 1.0},
            "fips_cofactor_effect_in_n": {"h=2": 1, "h=4": 3},
            "fips_cofactor_direction_in_record": "flatters the BASELINE",
            "fips_cofactor_direction_recomputed": "flatters SEMAEV",
        },
    },

    "J3_metric_set_and_the_409_flip": {
        "verdict": "breaks",
        "a_metric_degeneracy": p1["J3_metric_degeneracy"],
        "b_memory_weighted_metric": p1["J3_weighted_memory_metric"],
        "b_fixed_memory_budget_first_pass": p1["J3_fixed_memory_budget"],
        "b_fixed_memory_budget_second_pass": p2["A_fixed_memory_budget_metric"],
        "b_m_reoptimised_under_the_metric": p2["B_m_reoptimised_under_the_metric"],
        "b_ceiled_k_under_the_product": p2["C_ceiled_k_under_product"],
        "b_unit_conversion": p2["D_unit_conversion_sensitivity"],
        "b_pareto_minimum_of_each_own_curve": p2["E_pareto_min_of_own_curves"],
        "sparse_restatement_robustness": p4["J3_sparse_restatement_robustness"],
        "headline_numbers": {
            "declared_metrics": 4,
            "algebraically_distinct_metrics_here": 2,
            "AT_equals_product_by_construction": True,
            "max_equals_time_only_in_the_whole_swept_range": True,
            "alpha_at_which_409_flips_dense": 0.8112,
            "alpha_at_which_409_flips_sparse": 1.0,
            "hard_budget_2^40_bits_semaev_feasible_at_409": False,
            "hard_budget_2^40_bits_verdict_409_both_readings": "vow",
            "semaev_minimum_memory_log2_bits_at_409_over_m_2_to_30":
                {"dense": 80.068, "sparse": 65.331},
            "smallest_hard_budget_admitting_semaev_at_409_log2_bits":
                {"dense": "between 2^80 and 2^90", "sparse":
                 "between 2^64 and 2^70"},
            "soft_budget_log2_at_which_409_turns_semaev":
                p2["A_fixed_memory_budget_metric"][
                    "soft_budget_log2_bits_at_which_409_turns_semaev"],
            "scenarios_in_which_the_two_storage_readings_AGREE_at_409":
                p3["_readings_agree_at_409"],
        },
    },

    "J5_declined_stopping_rule": {
        "verdict": "holds",
        "a_independent_c_fit_first_pass": p1["J5_c_fit"],
        "a_convergence_with_a_guilty_null":
            p4["J5_convergence_with_guilty_null"],
        "b_m_star_law": p1["J5_m_star_law"],
        "headline_numbers": {
            "c_published_eq17": 1.698644,
            "argmin_m_agreement_with_the_records_ladder":
                "8/8 checked points (1e3..1e13): 16, 43, 120, 344, 1002, "
                "8739, 78425, 717005",
            "c_fitted_at_1e7": 1.481478,
            "c_fitted_at_1e13": 1.552477,
            "c_fitted_at_1e300": 1.688531,
            "gap_to_asymptote_at_1e7": 0.217166,
            "gap_to_asymptote_at_1e300": 0.010113,
            "gap_shrink_factor_1e20_to_1e300": 10.159,
            "two_parameter_extrapolated_limit_offset_true_model": -0.002651,
            "rms_residual_of_that_fit": 0.0008773,
            "rms_of_a_constant_offset_model": 0.0311157,
            "limit_offset_of_the_guilty_nulls":
                p4["J5_convergence_with_guilty_null"]["discrimination"][
                    "limit_offset_nulls"],
            "stirling_identity_worst_error_bits":
                p4["J5_convergence_with_guilty_null"]["TRUE_MODEL"][
                    "worst_stirling_prediction_error"],
            "m_star_law_understates_argmin_pct_recomputed": [5.09, 10.14],
            "m_star_law_understates_argmin_pct_claimed_by_record": [4, 15],
        },
    },

    "J6_substituted_control": {
        "verdict": "breaks",
        "a_family_membership": {
            "eq4_is_in_the_same_family_as_the_object_under_test": True,
            "assessment": "inadequate",
        },
        "b_prime_field_cost_model_located_in_this_repository":
            p4["J6_prime_field_control_from_corpus"],
        "b_prime_field_control_localised_to_the_store_size": p5,
        "b_corpus_search_trail": {
            "search_knowledge_mcp": "NOT AVAILABLE in this checkout; the "
                                    "derived retrieval index is empty here, so "
                                    "absence of a search result is not "
                                    "evidence of absence",
            "greps_run": [
                "rg -il 'index calculus' knowledge/literature knowledge/techniques -> 222 files",
                "rg -l 'prime.field' knowledge/literature knowledge/techniques -> 289 files",
                "intersection filtered for a complexity/cost statement",
                "rg -il 'summation polynomial' knowledge/",
                "find experiments knowledge -name 'COST-*'",
                "rg -il 'concrete_cost' experiments --glob '*.yaml'",
            ],
            "qualitative_ordering_found_in_the_corpus": [
                "KN-TECH-003: 'Prime fields GF(p): no good structured factor "
                "base is known; decomposition probability and Groebner cost "
                "make it uncompetitive with rho'",
                "KN-OPEN-001: 'Does index calculus beat Pollard rho for "
                "prime-field ECDLP?' -- current state: No",
                "KN-LIT-006 (Galbraith-Gaudry 2016 survey): over prime fields "
                "no algorithm beats generic square-root methods",
            ],
            "computable_cost_model_found": (
                "experiments/EXP-PFDR-c04716/runs/STATIC-001/"
                "concrete-cost.yaml, committed 6e38a5b07 -- 54 cells of a "
                "prime-field digit-presentation index-calculus cost model at "
                "log2 N in {64, 128, 256}, charging time AND memory, against "
                "the SAME 0.886 van Oorschot-Wiener baseline convention this "
                "record uses"),
            "nearest_non_cost_model_artifacts": [
                "EXP-PFGB-d630f6: prime-field Semaev solving-degree census, "
                "status review_required, execution_authorized false, toy "
                "scale (8-20 field bits), explicitly 'not a wall-time "
                "comparison to rho' -- not a cost model and could not have "
                "served",
                "KN-LIT-002 (Gaudry 2009): extension-field exponents "
                "O~(q^{4/3}) over GF(q^3), relayed from the abstract; a "
                "non-family nearby object with a known-in-advance ordering "
                "that was available and unused",
            ],
        },
        "c_eq4_detection_threshold": p4["J6_eq4_detection_threshold"],
        "headline_numbers": {
            "eq4_margin_bits": {"310": 1957.303, "409": 3431.834,
                                "571": 5976.83},
            "smallest_degree_bound_D_at_which_eq4_control_would_fail":
                {"310": 553, "409": 1130, "571": 2397},
            "records_own_live_failure_mode_costs_bits":
                {"D=5 at 409": 19.356, "D=6 at 409": 38.186},
            "prime_field_cells_where_IC_beats_rho_time_only_at_256_bits": 4,
            "prime_field_cells_where_IC_beats_rho_under_the_product":
                {"64": 1, "128": 1, "256": 1},
            "best_product_margin_for_prime_field_IC_bits":
                {"64": 8.4939, "128": 6.8444, "256": 4.7665},
            "smallest_store_log2_at_which_the_prime_field_ordering_inverts":
                p5["smallest_store_log2_at_which_the_prime_field_ordering_"
                   "inverts"],
            "store_log2_the_record_charges": 30,
            "D3_stopping_rule_fires": True,
        },
    },

    "round_setup_observation_not_a_joint": {
        "what": ("the review plan's blind_rederivation.parameters block does "
                 "not specify the record's memory model, so a re-derivation "
                 "following it literally cannot agree with the record on the "
                 "load-bearing quantity"),
        "two_sub_defects": [
            "N is given as m*ceil(n/m) + 2n, which is the relation store's ROW "
            "WIDTH in bits, not the working set's variable count; the record "
            "uses (m-2)n + m*ceil(n/m) (2790, 4099, 6286 at the three labels, "
            "which the plan's J1 text quotes correctly)",
            "the sparse reading is given in the J1 joint text as 'width bits', "
            "which does not reproduce the record's sparse figures under EITHER "
            "variable count",
        ],
        "dense_working_set_disagreement": pn,
        "sparse_and_load_bearing_quantity_disagreement": ps,
        "consequence": ("a literal re-derivation obtains crossover 306 and a "
                        "+29.77-bit margin at n = 409 where the record says "
                        "375 and +11.52; the 69-in-n and 18.25-bit "
                        "disagreement is a property of the plan text, not of "
                        "either implementation, and must not be composed as a "
                        "producer defect"),
        "derived_from": ("the review plan and the committed record only; no "
                         "sibling report was read"),
    },
}

with open(OUT, "w") as fh:
    json.dump(doc, fh, indent=2)
    fh.write("\n")
print("wrote", os.path.normpath(OUT), os.path.getsize(OUT), "bytes")
