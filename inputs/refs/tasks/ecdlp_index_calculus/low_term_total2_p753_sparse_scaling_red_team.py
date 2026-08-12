#!/usr/bin/env python3
"""P753 red-team scaling check for P752 sparse factor-basis selection."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P746_SCRIPT = TASK_DIR / "low_term_total2_p746_incremental_walk_online_cost.py"
P748_SCRIPT = TASK_DIR / "low_term_total2_p748_setup_amortization_matrix_bridge.py"
P751_SCRIPT = TASK_DIR / "low_term_total2_p751_factor_first_linear_algebra.py"
P752_SCRIPT = TASK_DIR / "low_term_total2_p752_sparse_factor_basis_selection.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P750 = STATE_DIR / "low_term_total2_p750_prospective_prefix_linear_algebra_charge_probe.json"
DEFAULT_P751 = STATE_DIR / "low_term_total2_p751_factor_first_linear_algebra_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p753_sparse_scaling_red_team_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_order11779_p753_sparse_scaling_red_team.md"
SCHEMA = "ecdlp.low_term_total2_p753_sparse_scaling_red_team.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def csv_ints(text: str) -> list[int]:
    out = []
    for item in text.split(","):
        item = item.strip()
        if item:
            out.append(int(item))
    return out


def csv_strings(text: str) -> list[str]:
    return [item.strip() for item in text.split(",") if item.strip()]


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def row_sort_key(row: dict[str, Any]) -> tuple[int, str]:
    label = str(row.get("seed_label") or row.get("seed") or "")
    match = re.search(r"(\d+)$", label)
    if match:
        return (int(match.group(1)), label)
    return (10**9, label)


def operation_costs(
    rows: list[dict[str, Any]],
    solve: dict[str, Any],
    substitution: dict[str, Any],
    field_weight: int,
) -> dict[str, Any]:
    rho = int(rows[0]["generic_rho_steps"]) if rows else 0
    setup = int(rows[0]["cost_model"]["subset_group_additions"]) if rows else 0
    group_total = setup + sum(int(row["cost_model"]["collection_online_group_additions"]) for row in rows)
    selected = len(rows)
    recovered = int(substitution["recovered_count"])
    solve_ops = int(solve["operation_counts"]["total_field_ops"])
    substitution_ops = int(substitution["operation_counts"].get("total_field_ops", 0))
    field_ops = solve_ops + substitution_ops
    selected_rho = selected * rho
    recovered_rho = recovered * rho
    weighted_field_ops = field_weight * field_ops
    total = group_total + weighted_field_ops
    return {
        "field_op_weight": field_weight,
        "group_addition_cost": group_total,
        "group_addition_cost_over_selected_rho": ratio(group_total, selected_rho),
        "recovered_rho_baseline": recovered_rho,
        "rho": rho,
        "selected_challenge_count": selected,
        "selected_rho_baseline": selected_rho,
        "sparse_factor_first_field_ops": field_ops,
        "sparse_solve_field_ops": solve_ops,
        "substitution_field_ops": substitution_ops,
        "total_unit_cost_group_additions_plus_weighted_field_ops": total,
        "total_unit_cost_over_recovered_rho": ratio(total, recovered_rho),
        "total_unit_cost_over_selected_rho": ratio(total, selected_rho),
        "weighted_sparse_field_ops": weighted_field_ops,
    }


def safe_weight_threshold(rows: list[dict[str, Any]], solve: dict[str, Any], substitution: dict[str, Any]) -> float | None:
    rho = int(rows[0]["generic_rho_steps"]) if rows else 0
    selected_rho = len(rows) * rho
    setup = int(rows[0]["cost_model"]["subset_group_additions"]) if rows else 0
    group_total = setup + sum(int(row["cost_model"]["collection_online_group_additions"]) for row in rows)
    field_ops = int(solve["operation_counts"]["total_field_ops"]) + int(substitution["operation_counts"].get("total_field_ops", 0))
    if field_ops <= 0:
        return None
    return round((selected_rho - group_total) / field_ops, 8)


def evaluate_policy(
    p751: Any,
    p752: Any,
    policy: str,
    relations: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    factor_count: int,
    order: int,
    field_weights: list[int],
) -> dict[str, Any]:
    ordered = p752.order_relations(relations, policy)
    solve = p752.sparse_incremental_solve(ordered, factor_count, order)
    substitution = p751.substitution_recovery(rows, solve["factor_values"], order) if solve["full_rank"] else {
        "mismatch_count": len(rows),
        "operation_counts": {"total_field_ops": 0},
        "recovered_count": 0,
        "recovered_sample": [],
    }
    success = bool(solve["full_rank"] and substitution["mismatch_count"] == 0 and substitution["recovered_count"] == len(rows))
    return {
        "costs_by_field_weight": [
            operation_costs(rows, solve, substitution, weight)
            for weight in field_weights
        ],
        "max_field_op_weight_below_selected_rho": safe_weight_threshold(rows, solve, substitution) if success else None,
        "policy": policy,
        "solve": {
            "full_rank": solve["full_rank"],
            "operation_counts": solve["operation_counts"],
            "rank": solve["rank"],
            "scanned_to_full_rank": solve["scanned_to_full_rank"],
        },
        "substitution": {
            "mismatch_count": substitution["mismatch_count"],
            "operation_counts": substitution["operation_counts"],
            "recovered_count": substitution["recovered_count"],
        },
        "success": success,
    }


def best_for_weight(evaluations: list[dict[str, Any]], weight: int) -> dict[str, Any]:
    def key(item: dict[str, Any]) -> tuple[Any, ...]:
        cost = next(cost for cost in item["costs_by_field_weight"] if cost["field_op_weight"] == weight)
        success_rank = 0 if item["success"] else 1
        return (
            success_rank,
            cost.get("total_unit_cost_over_selected_rho") or 10**18,
            item["substitution"]["mismatch_count"],
            item["policy"],
        )

    best = min(evaluations, key=key)
    return {
        "cost": next(cost for cost in best["costs_by_field_weight"] if cost["field_op_weight"] == weight),
        "policy": best["policy"],
        "rank": best["solve"]["rank"],
        "recovered_count": best["substitution"]["recovered_count"],
        "success": best["success"],
    }


def evaluate_prefix(
    p748: Any,
    p751: Any,
    p752: Any,
    target: str,
    rows: list[dict[str, Any]],
    prefix: int,
    policies: list[str],
    field_weights: list[int],
    order: int,
) -> dict[str, Any]:
    selected_rows = sorted(rows, key=row_sort_key)[: min(prefix, len(rows))]
    factor_count = max((len(form["coeffs"]) - 1 for row in selected_rows for form in row.get("forms") or []), default=0)
    relations = p752.annotated_relations(p748.factor_eliminated_relations(selected_rows, order, factor_count), order)
    evaluations = [
        evaluate_policy(p751, p752, policy, relations, selected_rows, factor_count, order, field_weights)
        for policy in policies
    ]
    best_by_weight = {str(weight): best_for_weight(evaluations, weight) for weight in field_weights}
    successful = [item for item in evaluations if item["success"]]
    max_safe_weight = max(
        (item["max_field_op_weight_below_selected_rho"] for item in successful if item["max_field_op_weight_below_selected_rho"] is not None),
        default=None,
    )
    weight1 = best_by_weight.get("1") or best_by_weight[str(field_weights[0])]
    return {
        "best_by_field_weight": best_by_weight,
        "factor_relation_count": len(relations),
        "factor_variable_count": factor_count,
        "max_field_op_weight_below_selected_rho": max_safe_weight,
        "policy_evaluations": evaluations,
        "prefix_count": len(selected_rows),
        "target": target,
        "weight1_success_below_selected_rho": bool(
            weight1["success"] and (weight1["cost"].get("total_unit_cost_over_selected_rho") or 10**18) < 1.0
        ),
    }


def determine_claim(target_summaries: list[dict[str, Any]], full_prefix: int) -> str:
    full_entries = [
        item
        for target in target_summaries
        for item in target["prefix_evaluations"]
        if item["prefix_count"] == full_prefix
    ]
    reproduced = bool(full_entries) and all(
        item["best_by_field_weight"]["1"]["success"]
        and (item["best_by_field_weight"]["1"]["cost"].get("total_unit_cost_over_selected_rho") or 10**18) < 1.0
        for item in full_entries
    )
    weight2_all = bool(full_entries) and all(
        item["best_by_field_weight"].get("2", {}).get("success")
        and (item["best_by_field_weight"]["2"]["cost"].get("total_unit_cost_over_selected_rho") or 10**18) < 1.0
        for item in full_entries
    )
    smaller_any = any(
        item["prefix_count"] < full_prefix and item["weight1_success_below_selected_rho"]
        for target in target_summaries
        for item in target["prefix_evaluations"]
    )
    if reproduced and weight2_all and smaller_any:
        return "P753_SPARSE_SIGNAL_ROBUST_TO_WEIGHT2_AND_SMALLER_PREFIX"
    if reproduced and (weight2_all or smaller_any):
        return "P753_SPARSE_SIGNAL_PARTIALLY_ROBUST"
    if reproduced:
        return "P753_REPRODUCES_P752_BUT_WEIGHT_AND_PREFIX_FRAGILE"
    return "NEGATIVE_RESULT_P753_FAILED_TO_REPRODUCE_P752"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p746 = load_module("ecdlp_p746_incremental_walk", P746_SCRIPT)
    p748 = load_module("ecdlp_p748_matrix_bridge", P748_SCRIPT)
    p751 = load_module("ecdlp_p751_factor_first", P751_SCRIPT)
    p752 = load_module("ecdlp_p752_sparse_factor_basis", P752_SCRIPT)
    relprobe = p746.load_relation_probe_module()
    p750 = load_json(args.p750_probe)
    rows_by_target = p751.add_expected_secrets(p746, relprobe, p750["results"])
    policies = csv_strings(args.policies)
    prefixes = sorted(set(csv_ints(args.prefixes)))
    field_weights = sorted(set(csv_ints(args.field_weights)))
    target_summaries = []
    for target, rows in rows_by_target.items():
        _verifier, _record, inv = p746.load_target(relprobe, target)
        order = int(inv["base_order"])
        prefix_evaluations = [
            evaluate_prefix(p748, p751, p752, target, rows, prefix, policies, field_weights, order)
            for prefix in prefixes
            if prefix <= len(rows)
        ]
        full_prefix = max(item["prefix_count"] for item in prefix_evaluations)
        full_entry = next(item for item in prefix_evaluations if item["prefix_count"] == full_prefix)
        target_summaries.append(
            {
                "full_prefix_count": full_prefix,
                "full_prefix_max_field_op_weight_below_selected_rho": full_entry["max_field_op_weight_below_selected_rho"],
                "prefix_evaluations": prefix_evaluations,
                "target": target,
                "weight1_below_rho_prefixes": [
                    item["prefix_count"]
                    for item in prefix_evaluations
                    if item["weight1_success_below_selected_rho"]
                ],
            }
        )
    full_prefix = min(item["full_prefix_count"] for item in target_summaries)
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p750_probe": str(args.p750_probe),
            "p751_summary": str(args.p751_summary),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(target_summaries, full_prefix),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled order-11779 ECDLP harness only.",
            "RED-TEAM: this tests sensitivity of P752, not novelty or deployment relevance.",
            "PUBLIC-PREFIX MODEL: prefixes use deterministic public seed-label order from P750 rows.",
            "SPARSE-WEIGHT MODEL: field-operation multipliers are accounting stress tests, not hardware measurements.",
            "MANY-TARGET MODEL: factor variables are solved from batches sharing one target factor base.",
        ],
        "method": "p753_sparse_scaling_red_team",
        "parameters": {
            "field_weights": field_weights,
            "p750_probe": str(args.p750_probe),
            "p751_summary": str(args.p751_summary),
            "policies": policies,
            "prefixes": prefixes,
        },
        "schema": SCHEMA,
        "summary": {
            "target_summaries": target_summaries,
        },
    }


def slim_prefix(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "best_by_field_weight": item["best_by_field_weight"],
        "factor_relation_count": item["factor_relation_count"],
        "factor_variable_count": item["factor_variable_count"],
        "max_field_op_weight_below_selected_rho": item["max_field_op_weight_below_selected_rho"],
        "prefix_count": item["prefix_count"],
        "target": item["target"],
        "weight1_success_below_selected_rho": item["weight1_success_below_selected_rho"],
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": f"{SCHEMA}.summary",
        "created_at": payload["created_at"],
        "claim_status": payload["claim_status"],
        "honesty_boundary": payload["honesty_boundary"],
        "method": payload["method"],
        "parameters": payload["parameters"],
        "summary": {
            "target_summaries": [
                {
                    "full_prefix_count": target["full_prefix_count"],
                    "full_prefix_max_field_op_weight_below_selected_rho": target["full_prefix_max_field_op_weight_below_selected_rho"],
                    "prefix_evaluations": [slim_prefix(item) for item in target["prefix_evaluations"]],
                    "target": target["target"],
                    "weight1_below_rho_prefixes": target["weight1_below_rho_prefixes"],
                }
                for target in payload["summary"]["target_summaries"]
            ]
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p750-probe", type=Path, default=DEFAULT_P750)
    parser.add_argument("--p751-summary", type=Path, default=DEFAULT_P751)
    parser.add_argument("--prefixes", default="32,64,128,256")
    parser.add_argument("--field-weights", default="1,2,4,8,16")
    parser.add_argument("--policies", default="natural,support_asc,support_span_asc,pivot_low,pivot_high,coefficient_weight_asc")
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
                "claim_status": summary["claim_status"],
                "targets": [
                    {
                        "full_prefix_max_weight": target["full_prefix_max_field_op_weight_below_selected_rho"],
                        "target": target["target"],
                        "weight1_below_rho_prefixes": target["weight1_below_rho_prefixes"],
                    }
                    for target in summary["summary"]["target_summaries"]
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
