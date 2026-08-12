#!/usr/bin/env python3
"""P760 prospective public sparse-policy selector."""

from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P755_SCRIPT = TASK_DIR / "low_term_total2_p755_public_row_quality_selector.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P759_SUMMARY = STATE_DIR / "low_term_total2_p759_prospective_budget_policy_validation_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p760_public_sparse_policy_selector_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p760_public_sparse_policy_selector.md"
SCHEMA = "ecdlp.low_term_total2_p760_public_sparse_policy_selector.v1"


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


def csv_strings(text: str) -> list[str]:
    return [item.strip() for item in text.split(",") if item.strip()]


def csv_ints(text: str) -> list[int]:
    return [int(item.strip()) for item in text.split(",") if item.strip()]


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def stat(values: list[int | float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "median": None, "min": None}
    return {
        "count": len(values),
        "max": max(values),
        "mean": round(mean(values), 8),
        "median": median(values),
        "min": min(values),
    }


def parse_cases(raw: str) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        parts = item.split("|")
        if len(parts) != 5:
            raise argparse.ArgumentTypeError(
                "cases must be label|target|budget|seed_prefix|role entries"
            )
        label, target, budget, seed_prefix, role = (part.strip() for part in parts)
        cases.append(
            {
                "budget": int(budget),
                "label": label,
                "role": role,
                "seed_prefix": seed_prefix,
                "target": target,
            }
        )
    if not cases:
        raise argparse.ArgumentTypeError("at least one case is required")
    return cases


def cost_for_weight(evaluation: dict[str, Any], weight: int, key: str = "costs_by_field_weight") -> dict[str, Any]:
    return next(cost for cost in evaluation[key] if int(cost["field_op_weight"]) == weight)


def weight2_ratio(evaluation: dict[str, Any], key: str = "costs_by_field_weight") -> float | None:
    return cost_for_weight(evaluation, 2, key).get("total_unit_cost_over_selected_rho")


def selected_feature_stats(p755: Any, rows: list[dict[str, Any]]) -> dict[str, Any]:
    features = [p755.public_feature(row) for row in rows]
    return {
        "accepted_mixed_relations": stat([item["accepted_mixed_relations"] for item in features]),
        "decomposition_hits": stat([item["decomposition_hits"] for item in features]),
        "form_count": stat([item["form_count"] for item in features]),
        "first_form_trial": stat([item["first_form_trial"] for item in features if item["first_form_trial"] is not None]),
        "last_form_trial": stat([item["last_form_trial"] for item in features if item["last_form_trial"] is not None]),
        "mixed_wide_relation_rank": stat([item["mixed_wide_relation_rank"] for item in features]),
        "zero_form_rows": [item["seed_label"] for item in features if int(item["form_count"]) == 0],
    }


def public_operation_costs(
    selected_rows: list[dict[str, Any]],
    scanned_rows: list[dict[str, Any]],
    solve: dict[str, Any],
    field_weight: int,
    substitution_ops_per_selected: int,
) -> dict[str, Any]:
    rho = int(selected_rows[0]["generic_rho_steps"]) if selected_rows else 0
    setup = int(selected_rows[0]["cost_model"]["subset_group_additions"]) if selected_rows else 0
    group_total = setup + sum(int(row["cost_model"]["collection_online_group_additions"]) for row in scanned_rows)
    selected_count = len(selected_rows)
    solve_ops = int((solve.get("operation_counts") or {}).get("total_field_ops") or 0)
    substitution_proxy_ops = selected_count * int(substitution_ops_per_selected)
    field_ops = solve_ops + substitution_proxy_ops
    selected_rho = selected_count * rho
    total = group_total + field_weight * field_ops
    return {
        "candidate_scan_group_addition_cost": group_total,
        "field_op_weight": field_weight,
        "group_addition_cost_over_selected_rho": ratio(group_total, selected_rho),
        "public_predicted_factor_first_field_ops": field_ops,
        "public_predicted_sparse_solve_field_ops": solve_ops,
        "public_predicted_substitution_field_ops": substitution_proxy_ops,
        "rho": rho,
        "scanned_challenge_count": len(scanned_rows),
        "selected_challenge_count": selected_count,
        "selected_rho_baseline": selected_rho,
        "total_unit_cost_group_additions_plus_weighted_field_ops": total,
        "total_unit_cost_over_selected_rho": ratio(total, selected_rho),
        "weighted_sparse_field_ops": field_weight * field_ops,
    }


def public_safe_weight(
    selected_rows: list[dict[str, Any]],
    scanned_rows: list[dict[str, Any]],
    solve: dict[str, Any],
    substitution_ops_per_selected: int,
) -> float | None:
    rho = int(selected_rows[0]["generic_rho_steps"]) if selected_rows else 0
    setup = int(selected_rows[0]["cost_model"]["subset_group_additions"]) if selected_rows else 0
    group_total = setup + sum(int(row["cost_model"]["collection_online_group_additions"]) for row in scanned_rows)
    solve_ops = int((solve.get("operation_counts") or {}).get("total_field_ops") or 0)
    field_ops = solve_ops + len(selected_rows) * int(substitution_ops_per_selected)
    if field_ops <= 0:
        return None
    return round((len(selected_rows) * rho - group_total) / field_ops, 8)


def solve_summary(solve: dict[str, Any]) -> dict[str, Any]:
    return {
        "full_rank": bool(solve.get("full_rank")),
        "operation_counts": solve.get("operation_counts") or {},
        "rank": int(solve.get("rank") or 0),
        "scanned_to_full_rank": solve.get("scanned_to_full_rank"),
    }


def failed_substitution(selected_count: int) -> dict[str, Any]:
    return {
        "mismatch_count": selected_count,
        "operation_counts": {"total_field_ops": 0},
        "recovered_count": 0,
        "recovered_sample": [],
    }


def solve_sparse_policy(
    p748: Any,
    p752: Any,
    selected_rows: list[dict[str, Any]],
    sparse_policy: str,
    field_weights: list[int],
    order: int,
    scanned_rows: list[dict[str, Any]],
    substitution_ops_per_selected: int,
) -> dict[str, Any]:
    factor_count = max((len(form["coeffs"]) - 1 for row in selected_rows for form in row.get("forms") or []), default=0)
    relations = p752.annotated_relations(
        p748.factor_eliminated_relations(selected_rows, order, factor_count),
        order,
    )
    solve = p752.sparse_incremental_solve(
        p752.order_relations(relations, sparse_policy),
        factor_count,
        order,
    )
    return {
        "factor_relation_count": len(relations),
        "factor_variable_count": factor_count,
        "public_costs_by_field_weight": [
            public_operation_costs(
                selected_rows,
                scanned_rows,
                solve,
                weight,
                substitution_ops_per_selected,
            )
            for weight in field_weights
        ],
        "public_max_field_op_weight_below_selected_rho": public_safe_weight(
            selected_rows,
            scanned_rows,
            solve,
            substitution_ops_per_selected,
        )
        if solve["full_rank"]
        else None,
        "selected_count": len(selected_rows),
        "solve": solve,
        "sparse_policy": sparse_policy,
    }


def public_choice(evaluations: list[dict[str, Any]], selected_count: int) -> dict[str, Any]:
    eligible = [
        item
        for item in evaluations
        if item["selected_count"] == selected_count and item["solve"]["full_rank"]
    ]
    if not eligible:
        return min(
            evaluations,
            key=lambda item: (
                0 if item["solve"]["full_rank"] else 1,
                -int(item["solve"].get("rank") or 0),
                item["sparse_policy"],
            ),
        )
    return min(
        eligible,
        key=lambda item: (
            weight2_ratio(item, "public_costs_by_field_weight") or 10**18,
            int(item["solve"]["operation_counts"].get("total_field_ops") or 10**18),
            item["sparse_policy"],
        ),
    )


def verify_sparse_policy(
    p751: Any,
    p755: Any,
    selected_rows: list[dict[str, Any]],
    scanned_rows: list[dict[str, Any]],
    solved: dict[str, Any],
    field_weights: list[int],
    order: int,
) -> dict[str, Any]:
    solve = solved["solve"]
    substitution = p751.substitution_recovery(selected_rows, solve["factor_values"], order) if solve["full_rank"] else failed_substitution(len(selected_rows))
    success = bool(
        solve["full_rank"]
        and substitution["mismatch_count"] == 0
        and substitution["recovered_count"] == len(selected_rows)
    )
    costs = [
        p755.operation_costs(selected_rows, scanned_rows, solve, substitution, weight)
        for weight in field_weights
    ]
    return {
        "costs_by_field_weight": costs,
        "factor_relation_count": solved["factor_relation_count"],
        "factor_variable_count": solved["factor_variable_count"],
        "max_field_op_weight_below_selected_rho": p755.safe_weight_threshold(
            selected_rows,
            scanned_rows,
            solve,
            substitution,
        )
        if success
        else None,
        "public_costs_by_field_weight": solved["public_costs_by_field_weight"],
        "public_max_field_op_weight_below_selected_rho": solved["public_max_field_op_weight_below_selected_rho"],
        "solve": solve_summary(solve),
        "sparse_policy": solved["sparse_policy"],
        "substitution": {
            "mismatch_count": substitution["mismatch_count"],
            "operation_counts": substitution["operation_counts"],
            "recovered_count": substitution["recovered_count"],
        },
        "success": success,
    }


def policy_passes(evaluation: dict[str, Any], selected_count: int) -> bool:
    cost = cost_for_weight(evaluation, 2)
    return bool(
        evaluation["success"]
        and evaluation["substitution"]["recovered_count"] == selected_count
        and evaluation["substitution"]["mismatch_count"] == 0
        and (cost.get("total_unit_cost_over_selected_rho") or 10**18) < 1.0
    )


def oracle_best(evaluations: list[dict[str, Any]], selected_count: int) -> dict[str, Any]:
    return min(
        evaluations,
        key=lambda item: (
            0 if policy_passes(item, selected_count) else 1,
            weight2_ratio(item) or 10**18,
            0 if item["success"] else 1,
            item["substitution"]["mismatch_count"],
            item["sparse_policy"],
        ),
    )


def slim_sparse_result(evaluation: dict[str, Any]) -> dict[str, Any]:
    return {
        "costs_by_field_weight": evaluation["costs_by_field_weight"],
        "factor_relation_count": evaluation["factor_relation_count"],
        "factor_variable_count": evaluation.get("factor_variable_count"),
        "max_field_op_weight_below_selected_rho": evaluation["max_field_op_weight_below_selected_rho"],
        "public_costs_by_field_weight": evaluation["public_costs_by_field_weight"],
        "public_max_field_op_weight_below_selected_rho": evaluation["public_max_field_op_weight_below_selected_rho"],
        "sparse_policy": evaluation["sparse_policy"],
        "solve": evaluation["solve"],
        "substitution": evaluation["substitution"],
        "success": evaluation["success"],
    }


def evaluate_case(
    p755: Any,
    p748: Any,
    p750: Any,
    p751: Any,
    p752: Any,
    p746: Any,
    relprobe: Any,
    case: dict[str, Any],
    args: argparse.Namespace,
    sparse_policies: list[str],
    field_weights: list[int],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    rows, order = p750.collect_target_rows(
        p746,
        p748,
        relprobe,
        case["target"],
        int(case["budget"]),
        args.seed_count,
        args.factor_base_size,
        args.width,
        args.walk_mode,
        str(case["seed_prefix"]),
        args.max_relations,
        args.max_subsets,
    )
    selection = p755.select_rows(rows, args.selected_count, args.pool_count, args.row_policy)
    selected_rows = selection["selected_rows"]
    scanned_rows = selection["scanned_rows"]
    public_evaluations = [
        solve_sparse_policy(
            p748,
            p752,
            selected_rows,
            sparse_policy,
            field_weights,
            order,
            scanned_rows,
            args.public_substitution_ops_per_selected,
        )
        for sparse_policy in sparse_policies
        if selected_rows
    ]
    if not public_evaluations:
        raise RuntimeError(f"no selected rows for {case['label']}")
    public_selected_solve = public_choice(public_evaluations, args.selected_count)
    verified_evaluations = [
        verify_sparse_policy(
            p751,
            p755,
            selected_rows,
            scanned_rows,
            item,
            field_weights,
            order,
        )
        for item in public_evaluations
    ]
    selected_verified = next(
        item
        for item in verified_evaluations
        if item["sparse_policy"] == public_selected_solve["sparse_policy"]
    )
    best = oracle_best(verified_evaluations, args.selected_count)
    selected_pass = (
        len(selected_rows) == args.selected_count
        and len(scanned_rows) >= len(selected_rows)
        and policy_passes(selected_verified, args.selected_count)
    )
    oracle_pass = (
        len(selected_rows) == args.selected_count
        and len(scanned_rows) >= len(selected_rows)
        and policy_passes(best, args.selected_count)
    )
    recovery_ok = bool(
        selected_verified["success"]
        and selected_verified["substitution"]["recovered_count"] == args.selected_count
        and selected_verified["substitution"]["mismatch_count"] == 0
        and selected_verified["solve"]["rank"] == args.factor_base_size
    )
    return {
        "base_order": order,
        "budget": int(case["budget"]),
        "case": case["label"],
        "dropped_from_scanned": selection["dropped_from_scanned"][:48],
        "generic_rho_steps": int(selected_rows[0]["generic_rho_steps"]) if selected_rows else None,
        "oracle_best_pass_weight2_below_rho": oracle_pass,
        "oracle_best_sparse_policy": slim_sparse_result(best),
        "pool_count": selection["pool_count"],
        "public_selector_pass_weight2_below_rho": selected_pass,
        "public_selector_recovery_ok": recovery_ok,
        "public_selector_sparse_policy": slim_sparse_result(selected_verified),
        "role": case["role"],
        "row_policy": args.row_policy,
        "rows_collected": len(rows),
        "scanned_count": len(scanned_rows),
        "scanned_seed_max": selection["scanned_seed_max"],
        "selected_count": len(selected_rows),
        "selected_feature_stats": selected_feature_stats(p755, selected_rows),
        "selected_seed_sample": selection["selected_seed_labels"][:12],
        "seed_prefix": case["seed_prefix"],
        "sparse_policy_evaluations": [slim_sparse_result(item) for item in verified_evaluations],
        "target": case["target"],
    }, rows


def determine_claim(case_summaries: list[dict[str, Any]], primary_threshold: int) -> str:
    total = len(case_summaries)
    selected_pass = sum(1 for item in case_summaries if item["public_selector_pass_weight2_below_rho"])
    oracle_pass = sum(1 for item in case_summaries if item["oracle_best_pass_weight2_below_rho"])
    recovery_ok = sum(1 for item in case_summaries if item["public_selector_recovery_ok"])
    if total and selected_pass == total:
        return "P760_PUBLIC_SPARSE_POLICY_SELECTOR_ALL_CASE_SIGNAL"
    if selected_pass >= primary_threshold:
        return "P760_PUBLIC_SPARSE_POLICY_SELECTOR_PRIMARY_SIGNAL"
    if oracle_pass >= primary_threshold:
        return "P760_PUBLIC_SPARSE_POLICY_SELECTOR_GAP"
    if recovery_ok >= primary_threshold:
        return "P760_PUBLIC_SELECTOR_RECOVERY_OK_COST_MARGIN_NEGATIVE"
    return "NEGATIVE_RESULT_P760_PUBLIC_SPARSE_POLICY_SELECTOR"


def p759_control(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    cases = []
    for item in (((payload.get("summary") or {}).get("case_summaries")) or []):
        best = item.get("best_sparse_policy") or {}
        fixed = item.get("fixed_sparse_policy") or {}
        cases.append(
            {
                "best_policy": best.get("policy"),
                "best_weight2_total_over_selected_rho": ((best.get("weight2_cost") or {}).get("total_unit_cost_over_selected_rho")),
                "case": item.get("case"),
                "fixed_policy": fixed.get("policy"),
                "fixed_weight2_total_over_selected_rho": ((fixed.get("weight2_cost") or {}).get("total_unit_cost_over_selected_rho")),
                "target": item.get("target"),
            }
        )
    return {
        "best_comparator_pass_count": ((payload.get("summary") or {}).get("best_comparator_pass_count")),
        "claim_status": payload.get("claim_status"),
        "fixed_policy_pass_count": ((payload.get("summary") or {}).get("fixed_policy_pass_count")),
        "fixed_policy_recovery_ok_count": ((payload.get("summary") or {}).get("fixed_policy_recovery_ok_count")),
        "cases": cases,
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p755 = load_module("ecdlp_p755_public_selector", P755_SCRIPT)
    p746 = p755.load_module("ecdlp_p746_incremental_walk", p755.P746_SCRIPT)
    p748 = p755.load_module("ecdlp_p748_matrix_bridge", p755.P748_SCRIPT)
    p750 = p755.load_module("ecdlp_p750_prospective_prefix", p755.P750_SCRIPT)
    p751 = p755.load_module("ecdlp_p751_factor_first", p755.P751_SCRIPT)
    p752 = p755.load_module("ecdlp_p752_sparse_factor_basis", p755.P752_SCRIPT)
    relprobe = p746.load_relation_probe_module()
    cases = parse_cases(args.cases)
    sparse_policies = csv_strings(args.sparse_policies)
    field_weights = csv_ints(args.field_weights)
    if 2 not in field_weights:
        field_weights.append(2)
        field_weights = sorted(set(field_weights))
    case_summaries: list[dict[str, Any]] = []
    raw_results: dict[str, list[dict[str, Any]]] = {}
    for case in cases:
        summary, rows = evaluate_case(
            p755,
            p748,
            p750,
            p751,
            p752,
            p746,
            relprobe,
            case,
            args,
            sparse_policies,
            field_weights,
        )
        case_summaries.append(summary)
        raw_results[str(case["label"])] = [p750.strip_private(row) for row in rows]
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p759_summary": str(args.p759_summary),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(case_summaries, args.primary_threshold),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "PROSPECTIVE-COLLECTION: rows are freshly collected from P760 seed prefixes, not replayed from earlier row pools.",
            "PUBLIC-SELECTION: sparse policy is selected before substitution verification from public full-rank solve cost plus a fixed substitution proxy.",
            "PRIVATE-VERIFY-ONLY: expected secrets are used only after public policy selection to verify recovery and mismatches.",
            "SCANNED-POOL-CHARGED: replacement policies pay group cost for all scanned candidate rows.",
            "SPARSE-WEIGHT MODEL: field-operation weights are accounting stress tests, not calibrated hardware timings.",
            "MANY-TARGET MODEL: the signal is a batched factor-basis recovery component, not a single-target break.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling or production-key relevance is implied.",
        ],
        "method": "p760_public_sparse_policy_selector",
        "parameters": {
            "cases": cases,
            "factor_base_size": args.factor_base_size,
            "field_weights": field_weights,
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "pool_count": args.pool_count,
            "primary_threshold": args.primary_threshold,
            "public_substitution_ops_per_selected": args.public_substitution_ops_per_selected,
            "row_policy": args.row_policy,
            "seed_count": args.seed_count,
            "selected_count": args.selected_count,
            "sparse_policies": sparse_policies,
            "walk_mode": args.walk_mode,
            "width": args.width,
        },
        "p759_control": p759_control(args.p759_summary),
        "results": raw_results,
        "schema": SCHEMA,
        "summary": {
            "case_count": len(case_summaries),
            "case_summaries": case_summaries,
            "oracle_best_pass_count": sum(1 for item in case_summaries if item["oracle_best_pass_weight2_below_rho"]),
            "public_selector_gap_count": sum(
                1
                for item in case_summaries
                if item["oracle_best_pass_weight2_below_rho"] and not item["public_selector_pass_weight2_below_rho"]
            ),
            "public_selector_pass_count": sum(1 for item in case_summaries if item["public_selector_pass_weight2_below_rho"]),
            "public_selector_recovery_ok_count": sum(1 for item in case_summaries if item["public_selector_recovery_ok"]),
        },
    }


def slim_sparse_for_summary(item: dict[str, Any]) -> dict[str, Any]:
    weight2 = cost_for_weight(item, 2)
    public_weight2 = cost_for_weight(item, 2, "public_costs_by_field_weight")
    return {
        "factor_relation_count": item["factor_relation_count"],
        "max_field_op_weight_below_selected_rho": item["max_field_op_weight_below_selected_rho"],
        "mismatch_count": item["substitution"]["mismatch_count"],
        "policy": item["sparse_policy"],
        "public_max_field_op_weight_below_selected_rho": item["public_max_field_op_weight_below_selected_rho"],
        "public_weight2_cost": public_weight2,
        "rank": item["solve"]["rank"],
        "recovered_count": item["substitution"]["recovered_count"],
        "success": item["success"],
        "weight2_cost": weight2,
    }


def slim_case(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "base_order": item["base_order"],
        "budget": item["budget"],
        "case": item["case"],
        "dropped_from_scanned": item["dropped_from_scanned"],
        "generic_rho_steps": item["generic_rho_steps"],
        "oracle_best_pass_weight2_below_rho": item["oracle_best_pass_weight2_below_rho"],
        "oracle_best_sparse_policy": slim_sparse_for_summary(item["oracle_best_sparse_policy"]),
        "public_selector_pass_weight2_below_rho": item["public_selector_pass_weight2_below_rho"],
        "public_selector_recovery_ok": item["public_selector_recovery_ok"],
        "public_selector_sparse_policy": slim_sparse_for_summary(item["public_selector_sparse_policy"]),
        "role": item["role"],
        "scanned_count": item["scanned_count"],
        "selected_count": item["selected_count"],
        "target": item["target"],
        "zero_form_selected_rows": item["selected_feature_stats"]["zero_form_rows"],
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": f"{SCHEMA}.summary",
        "artifacts": payload["artifacts"],
        "claim_status": payload["claim_status"],
        "created_at": payload["created_at"],
        "honesty_boundary": payload["honesty_boundary"],
        "method": payload["method"],
        "p759_control": payload["p759_control"],
        "parameters": payload["parameters"],
        "summary": {
            "case_count": payload["summary"]["case_count"],
            "case_summaries": [slim_case(item) for item in payload["summary"]["case_summaries"]],
            "oracle_best_pass_count": payload["summary"]["oracle_best_pass_count"],
            "public_selector_gap_count": payload["summary"]["public_selector_gap_count"],
            "public_selector_pass_count": payload["summary"]["public_selector_pass_count"],
            "public_selector_recovery_ok_count": payload["summary"]["public_selector_recovery_ok_count"],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cases",
        default=(
            "selector_order9887_67|67.a1@9803|66|ecdlp-p760-order9887-selector-v1|p760_selector,"
            "selector_order10639_22050|22050.cf1@10531|66|ecdlp-p760-order10639-selector-v1|p760_selector,"
            "selector_order9521_114224|114224.v1@9341|64|ecdlp-p760-order9521-selector-v1|p760_selector,"
            "selector_order8161_21175|21175.bc1@8089|58|ecdlp-p760-order8161-selector-v1|p760_selector,"
            "selector_order8521_23232|23232.cr1@8467|60|ecdlp-p760-order8521-selector-v1|p760_selector,"
            "selector_order9733_23232|23232.cr1@9643|64|ecdlp-p760-order9733-selector-v1|p760_selector,"
            "selector_order12049_67|67.a1@11923|72|ecdlp-p760-order12049-selector-v1|p760_selector"
        ),
    )
    parser.add_argument("--p759-summary", type=Path, default=DEFAULT_P759_SUMMARY)
    parser.add_argument("--seed-count", type=int, default=768)
    parser.add_argument("--selected-count", type=int, default=640)
    parser.add_argument("--pool-count", type=int, default=768)
    parser.add_argument("--row-policy", default="sequential_min_forms_ge_1")
    parser.add_argument("--sparse-policies", default="natural,support_asc,support_span_asc,pivot_low,pivot_high,coefficient_weight_asc")
    parser.add_argument("--factor-base-size", type=int, default=48)
    parser.add_argument("--width", type=int, default=2)
    parser.add_argument("--walk-mode", default="hash6")
    parser.add_argument("--max-relations", type=int, default=96)
    parser.add_argument("--max-subsets", type=int, default=25000)
    parser.add_argument("--field-weights", default="1,2")
    parser.add_argument("--public-substitution-ops-per-selected", type=int, default=6)
    parser.add_argument("--primary-threshold", type=int, default=6)
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
                "oracle_best_pass_count": summary["summary"]["oracle_best_pass_count"],
                "public_selector_gap_count": summary["summary"]["public_selector_gap_count"],
                "public_selector_pass_count": summary["summary"]["public_selector_pass_count"],
                "public_selector_recovery_ok_count": summary["summary"]["public_selector_recovery_ok_count"],
                "cases": [
                    {
                        "case": item["case"],
                        "oracle_policy": item["oracle_best_sparse_policy"]["policy"],
                        "oracle_weight2": item["oracle_best_sparse_policy"]["weight2_cost"].get("total_unit_cost_over_selected_rho"),
                        "public_pass": item["public_selector_pass_weight2_below_rho"],
                        "public_policy": item["public_selector_sparse_policy"]["policy"],
                        "public_predicted_weight2": item["public_selector_sparse_policy"]["public_weight2_cost"].get("total_unit_cost_over_selected_rho"),
                        "verified_weight2": item["public_selector_sparse_policy"]["weight2_cost"].get("total_unit_cost_over_selected_rho"),
                        "order": item["base_order"],
                        "target": item["target"],
                    }
                    for item in summary["summary"]["case_summaries"]
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
