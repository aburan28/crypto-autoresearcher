#!/usr/bin/env python3
"""P827 cost-reduction and target-descent sensitivity audit for P826."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P826_PROBE = STATE_DIR / "low_term_total2_p826_frozen_shared_pilot_validation_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p827_cost_descent_sensitivity_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p827_cost_descent_sensitivity_audit.md"
SCHEMA = "ecdlp.low_term_total2_p827_cost_descent_sensitivity_audit.v1"

FROZEN_PUBLIC_POLICY_NAME = "shared_core_score_hash_membership_rows_equal_remaining_p16"
ORACLE_POLICY_NAME = "shared_core_score_hash_oracle_pilot_rho_oracle_rho_weighted_remaining_p16"
DEFAULT_RELATION_SPEEDUPS = (1, 2, 4, 8, 16, 32, 64)
DEFAULT_AMORTIZATION_FACTORS = (1, 2, 4, 8, 16, 32, 64)


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def csv_ints(raw: str) -> list[int]:
    values = []
    for part in str(raw).split(","):
        part = part.strip()
        if part:
            values.append(int(part))
    return values


def policy_results(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return list(payload["summary"]["policy_results"])


def find_policy(payload: dict[str, Any], policy_name: str) -> dict[str, Any] | None:
    for item in policy_results(payload):
        if item.get("policy", {}).get("name") == policy_name:
            return item
    return None


def best_by_kind(payload: dict[str, Any], kind: str) -> dict[str, Any] | None:
    candidates = [item for item in policy_results(payload) if item.get("policy", {}).get("kind") == kind]
    viable = [
        item
        for item in candidates
        if item.get("aggregate", {}).get("post_hit_scan_once_train_total_unit_cost_over_recovered_rho") is not None
    ]
    if not viable:
        return None
    return min(
        viable,
        key=lambda item: item["aggregate"]["post_hit_scan_once_train_total_unit_cost_over_recovered_rho"],
    )


def compact_policy(item: dict[str, Any] | None) -> dict[str, Any] | None:
    if item is None:
        return None
    aggregate = item["aggregate"]
    return {
        "aggregate": {
            "covered_target_count": int(aggregate.get("covered_target_count") or 0),
            "pool_row_count": int(aggregate.get("pool_row_count") or 0),
            "post_hit_scan_once_train_total_unit_cost": int(
                aggregate.get("post_hit_scan_once_train_total_unit_cost") or 0
            ),
            "post_hit_scan_once_train_total_unit_cost_over_recovered_rho": aggregate.get(
                "post_hit_scan_once_train_total_unit_cost_over_recovered_rho"
            ),
            "recovered_rho_baseline": int(aggregate.get("recovered_rho_baseline") or 0),
            "recovered_row_count": int(aggregate.get("recovered_row_count") or 0),
            "selected_row_count": int(aggregate.get("selected_row_count") or 0),
        },
        "policy": {
            "kind": item["policy"].get("kind"),
            "name": item["policy"].get("name"),
        },
        "policy_claim": item.get("policy_claim"),
    }


def weighted_field_components(aggregate: dict[str, Any]) -> dict[str, Any]:
    total = int(aggregate["post_hit_scan_once_train_total_unit_cost"])
    train_online = int(aggregate.get("target_once_train_calibration_online_group_additions") or 0)
    setup = int(aggregate.get("target_once_setup_group_additions") or 0)
    relation_online = int(aggregate.get("pool_online_group_additions") or 0)
    train_field_ops = int(aggregate.get("target_once_train_calibration_field_ops") or 0)
    scoring_field_ops = int(aggregate.get("scoring_field_ops") or 0)
    field_ops = train_field_ops + scoring_field_ops
    residual = total - train_online - setup - relation_online
    field_weight = 0.0 if field_ops <= 0 else float(residual) / float(field_ops)
    train_field_weighted = field_weight * train_field_ops
    scoring_field_weighted = field_weight * scoring_field_ops
    return {
        "field_weight_inferred": round(field_weight, 8),
        "scoring_field_ops": scoring_field_ops,
        "scoring_field_weighted_cost": round(scoring_field_weighted, 8),
        "target_once_train_calibration_field_ops": train_field_ops,
        "target_once_train_field_weighted_cost": round(train_field_weighted, 8),
    }


def component_breakdown(item: dict[str, Any]) -> dict[str, Any]:
    aggregate = item["aggregate"]
    total = int(aggregate["post_hit_scan_once_train_total_unit_cost"])
    rho = int(aggregate["recovered_rho_baseline"])
    field = weighted_field_components(aggregate)
    target_once_train_online = int(aggregate.get("target_once_train_calibration_online_group_additions") or 0)
    target_once_setup = int(aggregate.get("target_once_setup_group_additions") or 0)
    relation_online = int(aggregate.get("pool_online_group_additions") or 0)
    target_once_fixed = (
        target_once_train_online
        + target_once_setup
        + float(field["target_once_train_field_weighted_cost"])
    )
    relation_variable = relation_online + float(field["scoring_field_weighted_cost"])
    components = {
        "relation_online_generation": relation_online,
        "scoring_field_weighted": field["scoring_field_weighted_cost"],
        "target_once_setup_group_additions": target_once_setup,
        "target_once_train_calibration_online_group_additions": target_once_train_online,
        "target_once_train_field_weighted": field["target_once_train_field_weighted_cost"],
    }
    return {
        "component_share_of_total": {key: ratio(value, total) for key, value in components.items()},
        "components": components,
        "current_cost_over_rho": ratio(total, rho),
        "field_weight_inferred": field["field_weight_inferred"],
        "post_hit_total_cost": total,
        "recovered_rho_baseline": rho,
        "relation_variable_cost": round(relation_variable, 8),
        "target_once_fixed_cost": round(target_once_fixed, 8),
    }


def source_split(item: dict[str, Any]) -> dict[str, Any]:
    choices = item.get("shared_pilot_choices") or []
    if not choices:
        return {}
    rows_by_policy: dict[str, int] = {}
    online_by_policy: dict[str, int] = {}
    continuation_online_total = 0
    synthetic_online_total = 0
    for choice in choices:
        policy = str(choice["selected_policy"])
        rows_by_policy[policy] = rows_by_policy.get(policy, 0) + int(choice.get("synthetic_pool_row_count") or 0)
        online_by_policy[policy] = online_by_policy.get(policy, 0) + int(choice.get("synthetic_pool_online_group_additions") or 0)
        continuation_online_total += int(choice.get("continuation_online_group_additions") or 0)
        synthetic_online_total += int(choice.get("synthetic_pool_online_group_additions") or 0)
    return {
        "choice_level_boundary": (
            "Continuation online counts are pre-merge support-family scans; synthetic pool online counts are post-merge "
            "pilot-plus-continuation totals. The difference is a useful bottleneck proxy, not a row-level proof."
        ),
        "continuation_online_group_additions_sum": continuation_online_total,
        "pilot_or_merge_residual_online_group_additions": synthetic_online_total - continuation_online_total,
        "selected_policy_count": {policy: sum(1 for choice in choices if choice["selected_policy"] == policy) for policy in rows_by_policy},
        "synthetic_online_group_additions_by_selected_policy": online_by_policy,
        "synthetic_pool_online_group_additions_sum": synthetic_online_total,
        "synthetic_rows_by_selected_policy": rows_by_policy,
    }


def threshold_audit(
    breakdown: dict[str, Any],
    relation_speedups: list[int],
    amortization_factors: list[int],
) -> dict[str, Any]:
    fixed = float(breakdown["target_once_fixed_cost"])
    variable = float(breakdown["relation_variable_cost"])
    rho = float(breakdown["recovered_rho_baseline"])
    total = float(breakdown["post_hit_total_cost"])
    relation_only_possible = fixed < rho
    relation_only_speedup = None
    if relation_only_possible:
        relation_only_speedup = ratio(variable, rho - fixed)

    grid = []
    best_no_descent = None
    for amortization in amortization_factors:
        for speedup in relation_speedups:
            reduced_total = fixed / float(amortization) + variable / float(speedup)
            cost_over_rho = ratio(reduced_total, rho)
            target_multiplier = None if cost_over_rho is None else max(1.0, float(cost_over_rho))
            item = {
                "below_rho_without_target_descent": bool(cost_over_rho is not None and cost_over_rho < 1.0),
                "cost_over_rho": cost_over_rho,
                "minimum_target_descent_multiplier_to_cross_rho": target_multiplier,
                "relation_variable_speedup": int(speedup),
                "target_once_amortization_factor": int(amortization),
            }
            grid.append(item)
            if item["below_rho_without_target_descent"]:
                if best_no_descent is None or (
                    int(amortization) * int(speedup),
                    int(amortization),
                    int(speedup),
                ) < (
                    int(best_no_descent["target_once_amortization_factor"]) * int(best_no_descent["relation_variable_speedup"]),
                    int(best_no_descent["target_once_amortization_factor"]),
                    int(best_no_descent["relation_variable_speedup"]),
                ):
                    best_no_descent = item

    speedup_required_by_amortization = []
    for amortization in amortization_factors:
        reduced_fixed = fixed / float(amortization)
        remaining = rho - reduced_fixed
        if remaining <= 0:
            required = None
        else:
            required = ratio(variable, remaining)
        speedup_required_by_amortization.append(
            {
                "minimum_relation_variable_speedup_without_target_descent": required,
                "target_once_amortization_factor": int(amortization),
            }
        )

    return {
        "best_grid_crossing_without_target_descent": best_no_descent,
        "current_target_descent_multiplier_required_if_cost_unchanged": ratio(total, rho),
        "minimum_uniform_cost_speedup_required": ratio(total, rho),
        "relation_generation_only_crosses_rho": bool(relation_only_possible),
        "relation_generation_only_minimum_speedup": relation_only_speedup,
        "scenario_grid": grid,
        "speedup_required_by_amortization": speedup_required_by_amortization,
    }


def determine_claim(breakdown: dict[str, Any], thresholds: dict[str, Any]) -> str:
    if (breakdown["current_cost_over_rho"] or 10**9) < 1.0:
        return "P827_CURRENT_P826_SOURCE_BELOW_RHO"
    if not thresholds["relation_generation_only_crosses_rho"] and thresholds["best_grid_crossing_without_target_descent"]:
        return "P827_COST_AUDIT_REQUIRES_JOINT_AMORTIZATION_AND_GENERATION_SPEEDUP"
    if not thresholds["relation_generation_only_crosses_rho"]:
        return "P827_COST_AUDIT_REQUIRES_TARGET_DESCENT_OR_FIXED_COST_REDUCTION"
    return "P827_COST_AUDIT_FINDS_RELATION_GENERATION_SPEEDUP_FRONTIER"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p826 = load_json(args.p826_probe)
    frozen = find_policy(p826, FROZEN_PUBLIC_POLICY_NAME)
    if frozen is None:
        raise ValueError(f"missing frozen public policy {FROZEN_PUBLIC_POLICY_NAME}")
    full_pool = find_policy(p826, "equal_full_pool")
    best_hash = best_by_kind(p826, "hash_control")
    best_adaptive = best_by_kind(p826, "adaptive_prefix_gate")
    oracle = find_policy(p826, ORACLE_POLICY_NAME)
    breakdown = component_breakdown(frozen)
    thresholds = threshold_audit(
        breakdown,
        csv_ints(args.relation_speedups),
        csv_ints(args.amortization_factors),
    )
    claim_status = determine_claim(breakdown, thresholds)
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p826_probe": str(args.p826_probe),
            "script": str(Path(__file__)),
        },
        "claim_status": claim_status,
        "cost_component_audit": breakdown,
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "MODEL-BOUND: P827 is a sensitivity audit over the P826 cost model, not a new relation generator.",
            "NO BELOW-RHO CLAIM: the current frozen P826 public relation source remains above Pollard rho.",
            "TARGET-DESCENT UNTESTED: multipliers are break-even requirements, not measured target descent.",
            "SPARSE-LA UNTESTED: matrix/rank costs are still a proof obligation for a complete index-calculus algorithm.",
        ],
        "method": "p827_cost_descent_sensitivity_audit",
        "parameters": {
            "amortization_factors": csv_ints(args.amortization_factors),
            "frozen_public_policy_name": FROZEN_PUBLIC_POLICY_NAME,
            "oracle_policy_name": ORACLE_POLICY_NAME,
            "relation_speedups": csv_ints(args.relation_speedups),
        },
        "policy_comparison": {
            "best_adaptive_control": compact_policy(best_adaptive),
            "best_hash_control": compact_policy(best_hash),
            "frozen_public_shared_pilot": compact_policy(frozen),
            "full_pool": compact_policy(full_pool),
            "oracle_sketch_ceiling": compact_policy(oracle),
        },
        "schema": SCHEMA,
        "source_split_audit": source_split(frozen),
        "threshold_audit": thresholds,
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    thresholds = payload["threshold_audit"]
    compact_grid = [
        item
        for item in thresholds["scenario_grid"]
        if item["target_once_amortization_factor"] in {1, 4, 8, 16, 32}
        and item["relation_variable_speedup"] in {1, 4, 8, 16, 32}
    ]
    return {
        **payload,
        "schema": f"{SCHEMA}.summary",
        "threshold_audit": {
            **thresholds,
            "scenario_grid": compact_grid,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p826-probe", type=Path, default=DEFAULT_P826_PROBE)
    parser.add_argument("--relation-speedups", default=",".join(str(value) for value in DEFAULT_RELATION_SPEEDUPS))
    parser.add_argument("--amortization-factors", default=",".join(str(value) for value in DEFAULT_AMORTIZATION_FACTORS))
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--summary-out", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary_out = args.summary_out or args.out.with_name(args.out.stem.replace("_probe", "_summary") + args.out.suffix)
    summary = summary_from_payload(payload)
    write_json(summary_out, summary)
    print(f"wrote {args.out}")
    print(f"wrote {summary_out}")
    print(
        json.dumps(
            {
                "claim_status": payload["claim_status"],
                "cost_component_audit": payload["cost_component_audit"],
                "source_split_audit": payload["source_split_audit"],
                "threshold_audit": {
                    "best_grid_crossing_without_target_descent": payload["threshold_audit"][
                        "best_grid_crossing_without_target_descent"
                    ],
                    "current_target_descent_multiplier_required_if_cost_unchanged": payload["threshold_audit"][
                        "current_target_descent_multiplier_required_if_cost_unchanged"
                    ],
                    "relation_generation_only_crosses_rho": payload["threshold_audit"][
                        "relation_generation_only_crosses_rho"
                    ],
                    "speedup_required_by_amortization": payload["threshold_audit"][
                        "speedup_required_by_amortization"
                    ],
                },
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
