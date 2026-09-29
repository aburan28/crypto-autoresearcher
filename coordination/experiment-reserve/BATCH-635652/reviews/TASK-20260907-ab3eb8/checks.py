#!/usr/bin/env python3
"""Fixed, zero-scientific-run checks for TASK-20260907-ab3eb8.

The checks use only the five declared amendment inputs.  A passing check named
``detect_*`` means that the stated protocol gap was reproduced; it does not mean
that the protocol passed review.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[5]
AMENDMENT_DIR = ROOT / (
    "coordination/experiment-reserve/BATCH-c26423/amendments/"
    "TASK-20260907-e11ec7"
)
EXPERIMENT_IDS = (
    "EXP-ECDLP-184fc4",
    "EXP-ECDLP-0c717c",
    "EXP-ECDLP-1e6502",
    "EXP-ECDLP-2c3d20",
    "EXP-ECDLP-709063",
)


def load_amendment(experiment_id: str) -> tuple[dict[str, Any], str]:
    path = AMENDMENT_DIR / f"{experiment_id}.yaml"
    text = path.read_text(encoding="utf-8")
    return yaml.safe_load(text)["protocol_amendment"], text


def main() -> int:
    amendments: dict[str, dict[str, Any]] = {}
    texts: dict[str, str] = {}
    for experiment_id in EXPERIMENT_IDS:
        amendments[experiment_id], texts[experiment_id] = load_amendment(
            experiment_id
        )

    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, detail: dict[str, Any]) -> None:
        checks.append({"name": name, "passed": bool(condition), "detail": detail})

    a184 = amendments["EXP-ECDLP-184fc4"]["effective_contract"]
    library_count = sum((2, 3, 4, 5, 7, 8, 16, 32, 64, 128, 256))
    library_count += sum((2, 4, 8)) + 9 + 16 + 3
    check(
        "EXP-ECDLP-184fc4_library_count",
        library_count == a184["frozen_library"]["member_count"] == 567,
        {"recomputed": library_count, "declared": 567},
    )
    observed_184 = 7 * 2 * 3 * 567
    null_184 = observed_184 * 64
    accounting_184 = a184["exact_cell_accounting"]
    check(
        "EXP-ECDLP-184fc4_cell_accounting",
        observed_184 == accounting_184["observed_member_spectra"]
        and null_184 == accounting_184["permutation_null_spectra"]
        and accounting_184["primary_curve_bundles"] == 42,
        {
            "observed_recomputed": observed_184,
            "null_recomputed": null_184,
            "bundles_recomputed": 42,
        },
    )
    per_member_184 = a184["permutation_null_and_inference"]["per_member_outputs"]
    null_block_184 = a184["permutation_null_and_inference"]
    check(
        "detect_EXP-ECDLP-184fc4_missing_percentile_rule",
        "declared order-statistic rule" in per_member_184
        and not any("percentile" in key for key in null_block_184 if key != "per_member_outputs"),
        {
            "resamples": 64,
            "finding": "median and 2.5/97.5 percentiles are requested without the referenced order-statistic rule",
        },
    )

    a0c = amendments["EXP-ECDLP-0c717c"]["effective_contract"]
    bundles_0c = 4 * 2 * 3
    null_permutations_0c = (3 * 2 * 3 * 2 * 32) + (1 * 2 * 3 * 2 * 8)
    accounting_0c = a0c["exact_cell_accounting"]
    check(
        "EXP-ECDLP-0c717c_cell_accounting",
        bundles_0c == accounting_0c["primary_curve_bundles"]
        and bundles_0c * 4 == accounting_0c["primary_base_cells"]
        and null_permutations_0c == accounting_0c["underlying_null_permutations"]
        and 2 * null_permutations_0c == accounting_0c["null_base_evaluations"]
        and 4 * null_permutations_0c == accounting_0c["null_envelope_values"],
        {
            "bundles_recomputed": bundles_0c,
            "null_permutations_recomputed": null_permutations_0c,
            "null_bases_recomputed": 2 * null_permutations_0c,
            "null_envelopes_recomputed": 4 * null_permutations_0c,
        },
    )
    percentile_indices = {
        str(r): [
            __import__("math").ceil(0.025 * r),
            __import__("math").ceil(0.975 * r),
        ]
        for r in (32, 8)
    }
    check(
        "EXP-ECDLP-0c717c_finite_percentile_indices",
        percentile_indices == {"32": [1, 32], "8": [1, 8]},
        {"one_based_indices": percentile_indices},
    )
    bootstrap_0c = a0c["slope_definition"]["intervals"]
    check(
        "detect_EXP-ECDLP-0c717c_unresolved_bootstrap_key",
        "analysis-key" in bootstrap_0c
        and "analysis-key" not in a0c.get("independent_variables", {}),
        {
            "finding": "the RNG domain contains the literal placeholder analysis-key but defines no serialization of gamma, base family, envelope, or stratum",
        },
    )

    a1e = amendments["EXP-ECDLP-1e6502"]["effective_contract"]
    check(
        "EXP-ECDLP-1e6502_member_counts",
        a1e["sixteen_post_functions"]["per_digit_count"] == 16
        and a1e["sixteen_post_functions"]["total_post_function_members"] == 8 * 16
        and 6 + 6 * 16 == 102
        and 8 + 8 * 16 == 136,
        {
            "precision_2_members_recomputed": 102,
            "precision_3_members_recomputed": 136,
        },
    )
    observed_1e = 36 * (102 + 136)
    accounting_1e = a1e["exact_cell_accounting"]
    check(
        "EXP-ECDLP-1e6502_cell_accounting",
        observed_1e == accounting_1e["observed_nonanomalous_spectra"]
        and observed_1e * 64 == accounting_1e["permutation_null_spectra"]
        and 24 * 20 == accounting_1e["anomalous_scalar_instances_target"],
        {
            "observed_recomputed": observed_1e,
            "null_recomputed": observed_1e * 64,
            "anomalous_recoveries_recomputed": 24 * 20,
        },
    )
    p, canonical_c, c0, j = 5, 32, 2, 2
    numerator = canonical_c - c0
    first_digit = (canonical_c // p) % p
    correct_second_digit = (canonical_c // (p**2)) % p
    check(
        "detect_EXP-ECDLP-1e6502_higher_digit_domain_failure",
        numerator % (p**j) != 0 and first_digit == 1 and correct_second_digit == 1,
        {
            "p": p,
            "C": canonical_c,
            "c0": c0,
            "j": j,
            "declared_numerator": numerator,
            "declared_divisor": p**j,
            "declared_divisible": False,
            "base_p_digits_low_to_high": [c0, first_digit, correct_second_digit],
        },
    )
    sc4 = next(
        row["exact_test"]
        for row in a1e["five_blocking_self_checks"]
        if row["id"] == "SC4_first_order_translation"
    )
    check(
        "detect_EXP-ECDLP-1e6502_SC4_missing_R_schedule",
        "10,000 deterministic pairs (R,z)" in sc4
        and "formal-z|j" in sc4
        and "SHA256(tag|R" not in sc4,
        {"finding": "SC4 fixes z_j but gives no deterministic selection or cycling rule for the eligible points R"},
    )

    a2c = amendments["EXP-ECDLP-2c3d20"]
    bundles_2c = 7 * 2 * 3
    true_maps_2c = bundles_2c * 4
    null_maps_2c = true_maps_2c * 64
    check(
        "EXP-ECDLP-2c3d20_cell_accounting",
        bundles_2c == 42
        and true_maps_2c == 168
        and null_maps_2c == 10752
        and true_maps_2c * 40 == 6720
        and null_maps_2c * 40 == 430080
        and 2 * 3 * 4 * 40 == 960
        and 960 * 64 == 61440,
        {
            "bundles_recomputed": bundles_2c,
            "true_maps_recomputed": true_maps_2c,
            "null_maps_recomputed": null_maps_2c,
            "true_lumped_recomputed": true_maps_2c * 40,
            "null_lumped_recomputed": null_maps_2c * 40,
        },
    )
    true_size = 100
    null_sizes = [10, 190]
    eligible = [n for n in null_sizes if 0.8 <= n / true_size <= 1.2]
    check(
        "EXP-ECDLP-2c3d20_unmatched_class_mock",
        eligible == [],
        {
            "true_class_size": true_size,
            "null_class_sizes": null_sizes,
            "eligible_matches": eligible,
        },
    )
    matching_text = a2c["itinerary_statistics"]["deterministic_size_matching"]
    rank_text = a2c["null_inference_and_decisions"]["ranks"]
    check(
        "detect_EXP-ECDLP-2c3d20_fixed_rank_with_unmatched_classes",
        "Unmatched classes" in matching_text and "/65" in rank_text,
        {
            "finding": "class matching permits missing null values, but the rank rule always assumes 64 null values plus the observation",
        },
    )
    standardized_occurrences = texts["EXP-ECDLP-2c3d20"].count("standardized effect")
    check(
        "detect_EXP-ECDLP-2c3d20_undefined_standardized_effect",
        standardized_occurrences == 1,
        {
            "occurrences": standardized_occurrences,
            "finding": "the review threshold invokes absolute standardized effect at least 2 without a centering, scale, or zero-dispersion rule",
        },
    )
    modeled_n = 2**23
    simultaneous_transition_bytes = 4 * (1 + 64) * modeled_n * 4
    check(
        "detect_EXP-ECDLP-2c3d20_memory_lifetime_gap",
        simultaneous_transition_bytes > 8 * 2**30
        and "bytes_per_index" not in texts["EXP-ECDLP-2c3d20"]
        and "stream" not in a2c["required_artifacts_for_future_execution"][5],
        {
            "fixed_mock_N": modeled_n,
            "maps_per_bundle": 4 * (1 + 64),
            "assumed_uint32_bytes_per_transition": 4,
            "simultaneous_bytes": simultaneous_transition_bytes,
            "eight_GiB": 8 * 2**30,
            "finding": "the contract requires transition-map artifacts but freezes no width, streaming order, or object lifetime that makes the 8 GiB guard checkable",
        },
    )

    a709 = amendments["EXP-ECDLP-709063"]
    capacities = []
    for budget in (8, 4096, 32768, 262144):
        slots = budget // 16
        capacities.append(
            {
                "budget_bytes": budget,
                "slots": slots,
                "usable_entries": 7 * slots // 10,
                "allocated_table_bytes": 16 * slots,
            }
        )
    check(
        "EXP-ECDLP-709063_capacity_table",
        capacities == a709["portable_fixed_physical_table"]["exact_capacities"],
        {"recomputed": capacities},
    )
    total_rows_709 = 16 + 256 + 48 + 48
    accounting_709 = a709["exact_cell_accounting"]
    check(
        "EXP-ECDLP-709063_cell_accounting",
        total_rows_709 == accounting_709["total_algorithm_rows"] == 368
        and accounting_709["total_representation_control_records"] == 8,
        {"algorithm_rows_recomputed": total_rows_709, "control_records": 8},
    )
    rho_rule = a709["rho_baseline"]["run_rule"]
    check(
        "detect_EXP-ECDLP-709063_deferred_rho_iteration_limit",
        "freeze the exact maximum-iteration formula" in rho_rule
        and "before launch" in rho_rule,
        {
            "finding": "the amendment does not itself freeze the rho maximum-iteration formula even though it affects censoring and medians",
        },
    )
    charged_total = a709["charged_group_operation_convention"]["total"]
    modeled_values = a709["metrics_and_decisions"]["modeled_values"]
    check(
        "detect_EXP-ECDLP-709063_incomplete_charged_model",
        "certificate" in charged_total
        and "D_model(N)=E+ceil(N/E)-c_ref*sqrt(N)" in modeled_values
        and "certificate" not in modeled_values
        and "scalar" not in modeled_values,
        {
            "finding": "D_model omits the separately charged [E]P scalar precompute, exact baby-step count convention, termination-dependent giant steps, and final certificate",
        },
    )

    first_three = [a184, a0c, a1e]
    check(
        "detect_first_three_missing_stage_cost_plan",
        all("maximum_memory_gb" in contract for contract in first_three)
        and all("wall_clock_seconds" not in contract for contract in first_three)
        and all("total_cpu" not in contract for contract in first_three),
        {
            "experiments": list(EXPERIMENT_IDS[:3]),
            "finding": "the complete replacements retain an 8 GiB number and measured-cost outputs but omit a stage cost plan, wall estimate, CPU estimate, and memory enforcement/lifetime rule",
        },
    )

    passed = sum(1 for row in checks if row["passed"])
    output = {
        "task_id": "TASK-20260907-ab3eb8",
        "scientific_runs": 0,
        "fixed_synthetic_or_mock_checks": len(checks),
        "checks_passed": passed,
        "checks_failed": len(checks) - passed,
        "checks": checks,
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
