#!/usr/bin/env python3
"""RC-1: zero-run static recomputation of the committed v4 cost chain."""
import json
from pathlib import Path

SOURCE = Path("experiments/EXP-JINV-bd141d/amendments/v4-cost-worksheet.json")
FACTORS = (1, 2, 12000, 1000000000)


def ceil_div(a, b):
    return (a + b - 1) // b


def main():
    worksheet = json.loads(SOURCE.read_text())
    card = worksheet["exact_cardinalities"]
    retained = worksheet["retained_artifact_upper_bytes"]
    model = worksheet["serialization_upper_bound_model"]["bytes_per_item_upper"]
    caps = worksheet["resource_caps"]
    baseline_pairs = card["all_replacement_pairs_upper"]["value"]
    baseline_retained = retained["total"]
    fixed = baseline_retained - retained["replacement_pairs"]
    assert baseline_pairs * model["replacement_pair_max"] == retained["replacement_pairs"]
    assert fixed + retained["replacement_pairs"] == baseline_retained
    assert baseline_retained == card["retained_artifact_bytes_upper"]["value"]
    assert ceil_div(baseline_retained, caps["individual_artifact_bytes_max"]) == card["minimum_artifact_shards_by_individual_cap"]["value"]
    assert baseline_retained * 3 == card["total_logical_io_bytes_upper"]["value"]

    cases = []
    for factor in FACTORS:
        pairs = baseline_pairs // factor
        replacement_bytes = pairs * model["replacement_pair_max"]
        retained_bytes = fixed + replacement_bytes
        individual_bytes = replacement_bytes
        shards = ceil_div(retained_bytes, caps["individual_artifact_bytes_max"])
        logical_io = retained_bytes * 3
        cases.append({
            "factor": factor,
            "changed_field": "all_replacement_pairs_upper",
            "all_replacement_pairs_upper": pairs,
            "replacement_pair_bytes": model["replacement_pair_max"],
            "replacement_pairs_subtotal_bytes": replacement_bytes,
            "fixed_residual_bytes": fixed,
            "E4_retained_bytes": retained_bytes,
            "E5_individual_artifact_bytes": individual_bytes,
            "E6_shard_count": shards,
            "E7_logical_io_bytes": logical_io,
            "rounding": "floor_division_for_integer_cardinality; exact_ceiling_for_shards",
        })
    report = {
        "task_id": "TASK-20260824-5d12b1",
        "experiment_id": "EXP-JINV-bd141d",
        "run_kind": "zero_run_static_RC1_perturbation",
        "experiment_runs": 0,
        "source": str(SOURCE),
        "baseline_verified": True,
        "formulas": {
            "E4_retained_bytes": "fixed_residual_bytes + all_replacement_pairs_upper * replacement_pair_max",
            "E5_individual_artifact_bytes": "all_replacement_pairs_upper * replacement_pair_max",
            "E6_shard_count": "ceil(E4_retained_bytes / individual_artifact_bytes_max)",
            "E7_logical_io_bytes": "3 * E4_retained_bytes",
        },
        "baseline": cases[0],
        "perturbations": cases[1:],
        "observation": "The replacement-pair term decreases under each perturbation, but the fixed residual remains unchanged.",
        "comparison": "E4 and E7 retain the unchanged residual; E5 follows the perturbed replacement-pair term; E6 applies exact ceiling.",
        "inference": "Static formula propagation only; no scientific or experimental inference.",
        "limitation": "No experiment, target, curve, JINV, transport, or instrument access occurred.",
    }
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
