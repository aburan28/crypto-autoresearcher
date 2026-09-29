#!/usr/bin/env python3
"""Assemble independent-figures.json from this task's own scratch outputs.
Pure re-packaging: every number here already exists in one of the own_*.json
files, which remain the primary record."""
import json

L = lambda f: json.load(open(f))
b = L("own_bounds2.json"); enum = L("own_enum.json"); z = L("own_zscores.json"); v = L("own_vow.json")
n3 = L("own_n3.json"); n3b = L("own_n3b.json"); n4 = L("own_n4.json"); n4b = L("own_n4b.json")
n4c = L("own_n4c.json"); mono = L("own_monotone.json")

fig = {
    "task_id": "TASK-20260913-3b91d0",
    "review_round_id": "REVIEW-SEMBIN-20260913-251fd3",
    "attempt": 2,
    "note": "Validator's independently recomputed figures for joints N1-N4 of RUN-SEMBIN-251fd3. "
            "Each block names the scratch file it is copied from; those files are the primary record.",
    "N1": {
        "source_files": ["own_bounds2.json", "own_enum.json", "own_zscores.json"],
        "model": b["model"],
        "bound_A_C0_by_n": {n: d["eps=0.05"] for n, d in b["bound_A"].items()},
        "bound_B_C0_by_n_tol_1bit_conditional": {n: d["tol=1.0_cond"] for n, d in b["bound_B"].items()},
        "bound_B_first_satisfying_without_monotone_closure": b["bound_B_first_satisfying_not_closure"],
        "sensitivity": {
            "bound_A": b["bound_A"],
            "bound_B": b["bound_B"]},
        "asymptotic_check": b["asymptotic_check"],
        "enumeration_cells": enum,
        "z_scores": z,
    },
    "N2": {
        "source_files": ["own_vow.json"],
        "derived_vow_pareto_minima_log2": v["derived_pareto_minima"],
        "committed_time_only_check": v["committed_time_only_check"],
        "o6_overcharge_bits_by_n": v["o6_overcharge"],
        "AT_with_processor_area_counterfactual_n571": v["at_counterfactual"],
        "surface_checks": v["checks"],
    },
    "N3": {
        "source_files": ["own_n3.json", "own_n3b.json"],
        "gate_cells_from_committed_records": n3["gate_cells_mine"],
        "gate_under_literal_1e_3": {k: val for k, val in n3["gate_under_literal_1e_3"].items() if k != "cells"},
        "gate_literal_1e_3_failing_cells": n3["gate_under_literal_1e_3"]["cells"],
        "m_only_control": n3["m_only_control"],
        "arm_k": n3["arm_k"],
        "arm_k_note": "my_pred_mem_rise under the loose reading in these rows applied the reading to T5 and is "
                      "WRONG by 2.32 bits; column_definitions fixes T5 as binomial under both readings, so the "
                      "correct prediction is log2((N+5)/5) = the JSON's, residual < 2e-11 bits (report N3(3)).",
        "arm_p": n3["arm_p"],
        "arm_m": n3["arm_m"],
        "manifest_vs_disk": {k: val for k, val in n3b.items() if k in (
            "manifest_artifacts_listed", "run_dir_files", "manifest_all_match", "manifest_all_bytes_match",
            "in_run_dir_not_in_manifest", "in_manifest_not_on_disk", "receipt_vs_disk",
            "manifest_and_receipt_agree_on", "declared_source_artifacts_present")},
        "manifest_hash_rows": n3b["manifest_vs_disk"],
        "artifact_policy_fields": n3b["artifact_policy_fields"],
        "driver_diff_raw_result": n3b["driver_diff_raw_result"],
        "driver_diff_reproduction": {k: val for k, val in n3b["driver_diff_reproduction"].items()},
        "control_flag_exec1_vs_exec2": {"exec1_eq11_pipeline_reproduces_any_uncorrected_figure": n3b["control_flag_exec1"],
                                        "exec2_..._where_it_differs_from_corrected": n3b["control_flag_exec2"]},
        "gate_passed_both_executions": n3b["gate_pass_both_executions"],
        "shared_numeric_leaves_raw_result": 42650,
        "frozen_nagao_sha256_on_disk": "337fae555450162e56432ee137d0cb4bb20e2bd901c29f69b38a2f949e913218",
        "snapshot_commit": {"sha": "a2cdafc67", "descends_from_manifest_head_0ac05e30": True,
                            "git_diff_against_run_package_empty": True},
        "pd4": n3["pd4"],
    },
    "N4": {
        "source_files": ["own_n4.json", "own_n4b.json", "own_n4c.json", "own_monotone.json"],
        "recompute_all_320_cells": n4["recompute_all_320_cells"],
        "six_cells": n4["six_cells"],
        "flag_counts": n4["flag_counts"],
        "flag_120_distribution": n4["flag_120_distribution"],
        "flag_120_by_n_omega": n4["flag_120_by_n_omega"],
        "flag_120_C0_map": n4["flag_120_C0_map"],
        "T6_at_the_120_summary": {k: val for k, val in n4["T6_at_the_120"].items() if k != "rows"},
        "spreads_at_571": n4["spreads_at_571"],
        "theorem_form_omega_spread_571": n4["theorem_form_omega_spread_571"],
        "crossover_sample_24": n4b["crossover_sample_24"],
        "crossover_ranges": n4b["crossover_ranges"],
        "monotone_flag_full_scan_disagreements": mono["full_disagreements"],
        "non_monotone_characterisation": {k: val for k, val in n4c.items() if k != "rows"},
    },
}
json.dump(fig, open("independent-figures.json", "w"), indent=1, default=str)
print("wrote independent-figures.json;", sum(len(json.dumps(fig[k], default=str)) for k in ("N1", "N2", "N3", "N4")), "chars")
