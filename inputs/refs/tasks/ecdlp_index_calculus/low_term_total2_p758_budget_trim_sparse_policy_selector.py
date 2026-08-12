#!/usr/bin/env python3
"""P758 budget-trim plus public sparse-policy selection over P757 rows."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P755_SCRIPT = TASK_DIR / "low_term_total2_p755_public_row_quality_selector.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P757_PROBE = STATE_DIR / "low_term_total2_p757_public_selector_cross_order_stress_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p758_budget_trim_sparse_policy_selector_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p758_budget_trim_sparse_policy_selector.md"
SCHEMA = "ecdlp.low_term_total2_p758_budget_trim_sparse_policy_selector.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


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
    return [int(item.strip()) for item in text.split(",") if item.strip()]


def csv_strings(text: str) -> list[str]:
    return [item.strip() for item in text.split(",") if item.strip()]


def parse_cases(raw: str) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        parts = item.split("|")
        if len(parts) != 3:
            raise argparse.ArgumentTypeError(
                "cases must be label|target|max_budget comma-separated entries"
            )
        label, target, max_budget = (part.strip() for part in parts)
        cases.append({"label": label, "max_budget": int(max_budget), "target": target})
    if not cases:
        raise argparse.ArgumentTypeError("at least one case is required")
    return cases


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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def cost_for_weight(costs: list[dict[str, Any]], weight: int) -> dict[str, Any]:
    return next(cost for cost in costs if int(cost["field_op_weight"]) == weight)


def weight2_ratio(costs: list[dict[str, Any]]) -> float | None:
    return cost_for_weight(costs, 2).get("total_unit_cost_over_selected_rho")


def budget_grid(max_budget: int, deltas: list[int], minimum_budget: int) -> list[int]:
    budgets = sorted({max(minimum_budget, max_budget - delta) for delta in deltas}, reverse=True)
    return [budget for budget in budgets if budget <= max_budget]


def online_group_additions_for_budget(row: dict[str, Any], order: int, budget: int) -> int:
    bit_length = max(1, int(order).bit_length())
    delta_setup = int((row.get("cost_model") or {}).get("delta_setup_group_additions") or 0)
    return (2 * bit_length) + 1 + delta_setup + max(0, int(budget) - 1)


def trim_row(row: dict[str, Any], order: int, budget: int) -> dict[str, Any]:
    copied = copy.deepcopy(row)
    forms = [
        form
        for form in (copied.get("forms") or [])
        if int(form.get("trial") or 0) <= int(budget)
    ]
    copied["forms"] = forms
    copied["accepted_mixed_relations"] = len(forms)
    copied["decomposition_hits"] = len(forms)
    copied["configured_trials"] = int(budget)
    copied["relation_trials"] = int(budget)
    copied["scanned_trials"] = int(budget)
    copied["derived"] = False
    copied["mixed_wide_relation_rank"] = 0
    copied["observed_decomposition_rate"] = round(len(forms) / float(max(1, int(budget))), 8)
    copied["trials_to_derive_secret"] = None

    cost_model = dict(copied.get("cost_model") or {})
    setup = int(cost_model.get("subset_group_additions") or 0)
    online = online_group_additions_for_budget(copied, order, budget)
    cost_model["collection_online_group_additions"] = online
    cost_model["collection_one_shot_group_additions"] = setup + online
    cost_model["solve_attempt_online_group_additions"] = online
    cost_model["solve_attempt_one_shot_group_additions"] = setup + online
    cost_model["first_derive_online_group_additions"] = None
    cost_model["first_derive_online_group_additions_beats_rho"] = False
    copied["cost_model"] = cost_model
    return copied


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
    total = group_total + (field_weight * field_ops)
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
    field_ops = solve_ops + (len(selected_rows) * int(substitution_ops_per_selected))
    if field_ops <= 0:
        return None
    return round((len(selected_rows) * rho - group_total) / field_ops, 8)


def selected_feature_stats(p755: Any, rows: list[dict[str, Any]]) -> dict[str, Any]:
    features = [p755.public_feature(row) for row in rows]
    return {
        "accepted_mixed_relations": stat([item["accepted_mixed_relations"] for item in features]),
        "form_count": stat([item["form_count"] for item in features]),
        "first_form_trial": stat([item["first_form_trial"] for item in features if item["first_form_trial"] is not None]),
        "last_form_trial": stat([item["last_form_trial"] for item in features if item["last_form_trial"] is not None]),
        "zero_form_rows": [item["seed_label"] for item in features if int(item["form_count"]) == 0],
    }


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


def evaluate_sparse_policy(
    p748: Any,
    p751: Any,
    p752: Any,
    p755: Any,
    selected_rows: list[dict[str, Any]],
    scanned_rows: list[dict[str, Any]],
    sparse_policy: str,
    field_weights: list[int],
    order: int,
    substitution_ops_per_selected: int,
) -> dict[str, Any]:
    factor_count = max((len(form["coeffs"]) - 1 for row in selected_rows for form in row.get("forms") or []), default=0)
    relations = p752.annotated_relations(
        p748.factor_eliminated_relations(selected_rows, order, factor_count),
        order,
    )
    ordered = p752.order_relations(relations, sparse_policy)
    solve = p752.sparse_incremental_solve(ordered, factor_count, order)
    substitution = p751.substitution_recovery(selected_rows, solve["factor_values"], order) if solve["full_rank"] else failed_substitution(len(selected_rows))
    verified_success = bool(
        solve["full_rank"]
        and substitution["mismatch_count"] == 0
        and substitution["recovered_count"] == len(selected_rows)
    )
    verified_costs = [
        p755.operation_costs(selected_rows, scanned_rows, solve, substitution, weight)
        for weight in field_weights
    ]
    public_costs = [
        public_operation_costs(selected_rows, scanned_rows, solve, weight, substitution_ops_per_selected)
        for weight in field_weights
    ]
    return {
        "factor_relation_count": len(relations),
        "factor_variable_count": factor_count,
        "public": {
            "costs_by_field_weight": public_costs,
            "eligible_for_selection": bool(len(selected_rows) > 0 and solve["full_rank"]),
            "max_field_op_weight_below_selected_rho": public_safe_weight(
                selected_rows,
                scanned_rows,
                solve,
                substitution_ops_per_selected,
            )
            if solve["full_rank"]
            else None,
            "solve": solve_summary(solve),
        },
        "sparse_policy": sparse_policy,
        "verified": {
            "costs_by_field_weight": verified_costs,
            "max_field_op_weight_below_selected_rho": p755.safe_weight_threshold(
                selected_rows,
                scanned_rows,
                solve,
                substitution,
            )
            if verified_success
            else None,
            "solve": solve_summary(solve),
            "substitution": {
                "mismatch_count": substitution["mismatch_count"],
                "operation_counts": substitution["operation_counts"],
                "recovered_count": substitution["recovered_count"],
            },
            "success": verified_success,
        },
    }


def verified_passes(evaluation: dict[str, Any] | None, selected_count: int) -> bool:
    if evaluation is None:
        return False
    verified = evaluation["verified"]
    weight2 = weight2_ratio(verified["costs_by_field_weight"])
    return bool(
        evaluation["selected_count"] == selected_count
        and verified["success"]
        and verified["substitution"]["recovered_count"] == selected_count
        and verified["substitution"]["mismatch_count"] == 0
        and (weight2 or 10**18) < 1.0
    )


def public_choice(evaluations: list[dict[str, Any]], selected_count: int) -> dict[str, Any] | None:
    eligible = [
        item
        for item in evaluations
        if item["selected_count"] == selected_count and item["public"]["eligible_for_selection"]
    ]
    if not eligible:
        return None
    return min(
        eligible,
        key=lambda item: (
            weight2_ratio(item["public"]["costs_by_field_weight"]) or 10**18,
            item["budget"],
            item["sparse_policy"],
        ),
    )


def oracle_choice(evaluations: list[dict[str, Any]], selected_count: int) -> dict[str, Any] | None:
    eligible = [
        item
        for item in evaluations
        if item["selected_count"] == selected_count and item["verified"]["success"]
    ]
    if not eligible:
        return None
    return min(
        eligible,
        key=lambda item: (
            weight2_ratio(item["verified"]["costs_by_field_weight"]) or 10**18,
            item["budget"],
            item["sparse_policy"],
        ),
    )


def slim_evaluation(item: dict[str, Any] | None) -> dict[str, Any] | None:
    if item is None:
        return None
    return {
        "budget": item["budget"],
        "dropped_from_scanned": item["dropped_from_scanned"][:48],
        "factor_relation_count": item["factor_relation_count"],
        "factor_variable_count": item["factor_variable_count"],
        "public": {
            "costs_by_field_weight": item["public"]["costs_by_field_weight"],
            "eligible_for_selection": item["public"]["eligible_for_selection"],
            "max_field_op_weight_below_selected_rho": item["public"]["max_field_op_weight_below_selected_rho"],
            "solve": item["public"]["solve"],
        },
        "scanned_count": item["scanned_count"],
        "selected_count": item["selected_count"],
        "selected_feature_stats": item["selected_feature_stats"],
        "sparse_policy": item["sparse_policy"],
        "verified": item["verified"],
    }


def evaluate_budget(
    p748: Any,
    p751: Any,
    p752: Any,
    p755: Any,
    rows: list[dict[str, Any]],
    order: int,
    budget: int,
    args: argparse.Namespace,
    sparse_policies: list[str],
    field_weights: list[int],
) -> list[dict[str, Any]]:
    trimmed_rows = [trim_row(row, order, budget) for row in rows]
    selection = p755.select_rows(trimmed_rows, args.selected_count, args.pool_count, args.row_policy)
    selected_rows = selection["selected_rows"]
    scanned_rows = selection["scanned_rows"]
    out = []
    for sparse_policy in sparse_policies:
        if selected_rows:
            evaluated = evaluate_sparse_policy(
                p748,
                p751,
                p752,
                p755,
                selected_rows,
                scanned_rows,
                sparse_policy,
                field_weights,
                order,
                args.public_substitution_ops_per_selected,
            )
        else:
            evaluated = {
                "factor_relation_count": 0,
                "factor_variable_count": 0,
                "public": {
                    "costs_by_field_weight": [],
                    "eligible_for_selection": False,
                    "max_field_op_weight_below_selected_rho": None,
                    "solve": {"full_rank": False, "operation_counts": {}, "rank": 0, "scanned_to_full_rank": None},
                },
                "sparse_policy": sparse_policy,
                "verified": {
                    "costs_by_field_weight": [],
                    "max_field_op_weight_below_selected_rho": None,
                    "solve": {"full_rank": False, "operation_counts": {}, "rank": 0, "scanned_to_full_rank": None},
                    "substitution": failed_substitution(0),
                    "success": False,
                },
            }
        evaluated.update(
            {
                "budget": int(budget),
                "dropped_from_scanned": selection["dropped_from_scanned"][:48],
                "scanned_count": len(scanned_rows),
                "scanned_seed_max": selection["scanned_seed_max"],
                "selected_count": len(selected_rows),
                "selected_feature_stats": selected_feature_stats(p755, selected_rows),
            }
        )
        out.append(evaluated)
    return out


def evaluate_case(
    p746: Any,
    p748: Any,
    p751: Any,
    p752: Any,
    p755: Any,
    relprobe: Any,
    p757_payload: dict[str, Any],
    case: dict[str, Any],
    args: argparse.Namespace,
    sparse_policies: list[str],
    field_weights: list[int],
) -> dict[str, Any]:
    raw_rows = (p757_payload.get("results") or {}).get(case["label"])
    if raw_rows is None:
        raise KeyError(f"P757 source has no rows for case {case['label']!r}")
    _verifier, _record, inv = p746.load_target(relprobe, case["target"])
    order = int(inv["base_order"])
    rows = p751.add_expected_secrets(p746, relprobe, {case["target"]: raw_rows})[case["target"]]
    budgets = budget_grid(int(case["max_budget"]), csv_ints(args.budget_deltas), args.minimum_budget)
    evaluations: list[dict[str, Any]] = []
    for budget in budgets:
        evaluations.extend(
            evaluate_budget(
                p748,
                p751,
                p752,
                p755,
                rows,
                order,
                budget,
                args,
                sparse_policies,
                field_weights,
            )
        )
    selected_public = public_choice(evaluations, args.selected_count)
    selected_oracle = oracle_choice(evaluations, args.selected_count)
    public_pass = verified_passes(selected_public, args.selected_count)
    oracle_pass = verified_passes(selected_oracle, args.selected_count)
    return {
        "base_order": order,
        "budget_grid": budgets,
        "case": case["label"],
        "evaluations": [slim_evaluation(item) for item in evaluations],
        "generic_rho_steps": int(rows[0]["generic_rho_steps"]) if rows else None,
        "max_budget": int(case["max_budget"]),
        "oracle_best_pass_weight2_below_rho": oracle_pass,
        "oracle_best_selection": slim_evaluation(selected_oracle),
        "public_selector_pass_weight2_below_rho": public_pass,
        "public_selector_selection": slim_evaluation(selected_public),
        "row_policy": args.row_policy,
        "source_row_count": len(rows),
        "target": case["target"],
    }


def determine_claim(case_summaries: list[dict[str, Any]]) -> str:
    total = len(case_summaries)
    public_pass = sum(1 for item in case_summaries if item["public_selector_pass_weight2_below_rho"])
    oracle_pass = sum(1 for item in case_summaries if item["oracle_best_pass_weight2_below_rho"])
    if total and public_pass == total:
        return "P758_PUBLIC_BUDGET_POLICY_SELECTOR_ALL_CROSS_ORDER_WEIGHT2_SIGNAL"
    if public_pass >= 4:
        return "P758_PUBLIC_BUDGET_POLICY_SELECTOR_PARTIAL_CROSS_ORDER_WEIGHT2_SIGNAL"
    if oracle_pass >= 4:
        return "P758_ORACLE_BUDGET_POLICY_SIGNAL_PUBLIC_SELECTOR_GAP"
    if public_pass:
        return "P758_PARTIAL_PUBLIC_BUDGET_POLICY_SIGNAL"
    return "NEGATIVE_RESULT_P758_BUDGET_TRIM_SPARSE_SELECTOR"


def p757_control(payload: dict[str, Any]) -> dict[str, Any]:
    out = []
    for item in (((payload.get("summary") or {}).get("case_summaries")) or []):
        best = item.get("best_sparse_policy") or {}
        frozen = item.get("frozen_sparse_policy") or {}
        out.append(
            {
                "best_policy": best.get("sparse_policy"),
                "best_weight2_total_over_selected_rho": weight2_ratio(best.get("costs_by_field_weight") or []),
                "case": item.get("case"),
                "frozen_weight2_total_over_selected_rho": weight2_ratio(frozen.get("costs_by_field_weight") or []),
                "target": item.get("target"),
            }
        )
    return {
        "claim_status": payload.get("claim_status"),
        "cases": out,
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p755 = load_module("ecdlp_p755_public_selector", P755_SCRIPT)
    p746 = p755.load_module("ecdlp_p746_incremental_walk", p755.P746_SCRIPT)
    p748 = p755.load_module("ecdlp_p748_matrix_bridge", p755.P748_SCRIPT)
    p751 = p755.load_module("ecdlp_p751_factor_first", p755.P751_SCRIPT)
    p752 = p755.load_module("ecdlp_p752_sparse_factor_basis", p755.P752_SCRIPT)
    relprobe = p746.load_relation_probe_module()
    p757_payload = load_json(args.p757_probe)
    cases = parse_cases(args.cases)
    sparse_policies = csv_strings(args.sparse_policies)
    field_weights = csv_ints(args.field_weights)
    if 2 not in field_weights:
        field_weights.append(2)
        field_weights = sorted(set(field_weights))
    case_summaries = [
        evaluate_case(
            p746,
            p748,
            p751,
            p752,
            p755,
            relprobe,
            p757_payload,
            case,
            args,
            sparse_policies,
            field_weights,
        )
        for case in cases
    ]
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p757_probe": str(args.p757_probe),
            "p757_probe_sha256": sha256_file(args.p757_probe),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(case_summaries),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "BUDGET-PREFIX-REPLAY: P758 replays P757 saved rows with trial prefixes instead of recollecting fresh walks.",
            "PUBLIC-SELECTION: budget and sparse policy are selected from public row/form features, full-rank status, and counted solve cost.",
            "PRIVATE-VERIFY-ONLY: deterministic expected secrets are rehydrated only after public selection to verify recovery/mismatches.",
            "SCANNED-POOL-CHARGED: replacement selection pays group cost for all scanned candidate rows at the selected budget.",
            "SPARSE-WEIGHT MODEL: field-operation weights are accounting stress tests, not calibrated hardware timings.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling or production-key relevance is implied.",
        ],
        "method": "p758_budget_trim_sparse_policy_selector",
        "parameters": {
            "budget_deltas": csv_ints(args.budget_deltas),
            "cases": cases,
            "field_weights": field_weights,
            "minimum_budget": args.minimum_budget,
            "pool_count": args.pool_count,
            "public_substitution_ops_per_selected": args.public_substitution_ops_per_selected,
            "row_policy": args.row_policy,
            "selected_count": args.selected_count,
            "sparse_policies": sparse_policies,
        },
        "p757_control": p757_control(p757_payload),
        "schema": SCHEMA,
        "summary": {
            "case_count": len(case_summaries),
            "case_summaries": case_summaries,
            "oracle_best_pass_count": sum(1 for item in case_summaries if item["oracle_best_pass_weight2_below_rho"]),
            "public_selector_pass_count": sum(1 for item in case_summaries if item["public_selector_pass_weight2_below_rho"]),
            "public_selector_gap_count": sum(
                1
                for item in case_summaries
                if item["oracle_best_pass_weight2_below_rho"] and not item["public_selector_pass_weight2_below_rho"]
            ),
        },
    }


def slim_choice(choice: dict[str, Any] | None) -> dict[str, Any] | None:
    if choice is None:
        return None
    public_weight2 = cost_for_weight(choice["public"]["costs_by_field_weight"], 2)
    verified_weight2 = cost_for_weight(choice["verified"]["costs_by_field_weight"], 2)
    return {
        "budget": choice["budget"],
        "factor_relation_count": choice["factor_relation_count"],
        "policy": choice["sparse_policy"],
        "public_max_field_op_weight_below_selected_rho": choice["public"]["max_field_op_weight_below_selected_rho"],
        "public_rank": choice["public"]["solve"]["rank"],
        "public_weight2_cost": public_weight2,
        "scanned_count": choice["scanned_count"],
        "selected_count": choice["selected_count"],
        "verified_max_field_op_weight_below_selected_rho": choice["verified"]["max_field_op_weight_below_selected_rho"],
        "verified_mismatch_count": choice["verified"]["substitution"]["mismatch_count"],
        "verified_rank": choice["verified"]["solve"]["rank"],
        "verified_recovered_count": choice["verified"]["substitution"]["recovered_count"],
        "verified_success": choice["verified"]["success"],
        "verified_weight2_cost": verified_weight2,
    }


def slim_case(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "base_order": item["base_order"],
        "budget_grid": item["budget_grid"],
        "case": item["case"],
        "generic_rho_steps": item["generic_rho_steps"],
        "max_budget": item["max_budget"],
        "oracle_best_pass_weight2_below_rho": item["oracle_best_pass_weight2_below_rho"],
        "oracle_best_selection": slim_choice(item["oracle_best_selection"]),
        "public_selector_pass_weight2_below_rho": item["public_selector_pass_weight2_below_rho"],
        "public_selector_selection": slim_choice(item["public_selector_selection"]),
        "source_row_count": item["source_row_count"],
        "target": item["target"],
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": f"{SCHEMA}.summary",
        "artifacts": payload["artifacts"],
        "claim_status": payload["claim_status"],
        "created_at": payload["created_at"],
        "honesty_boundary": payload["honesty_boundary"],
        "method": payload["method"],
        "p757_control": payload["p757_control"],
        "parameters": payload["parameters"],
        "summary": {
            "case_count": payload["summary"]["case_count"],
            "case_summaries": [slim_case(item) for item in payload["summary"]["case_summaries"]],
            "oracle_best_pass_count": payload["summary"]["oracle_best_pass_count"],
            "public_selector_gap_count": payload["summary"]["public_selector_gap_count"],
            "public_selector_pass_count": payload["summary"]["public_selector_pass_count"],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p757-probe", type=Path, default=DEFAULT_P757_PROBE)
    parser.add_argument(
        "--cases",
        default=(
            "order9887_67|67.a1@9803|72,"
            "order10639_22050|22050.cf1@10531|72,"
            "order9521_114224|114224.v1@9341|70,"
            "order8161_21175|21175.bc1@8089|64,"
            "order8521_23232|23232.cr1@8467|66"
        ),
    )
    parser.add_argument("--budget-deltas", default="0,1,2,3,4,5,6")
    parser.add_argument("--minimum-budget", type=int, default=1)
    parser.add_argument("--selected-count", type=int, default=640)
    parser.add_argument("--pool-count", type=int, default=768)
    parser.add_argument("--row-policy", default="sequential_min_forms_ge_1")
    parser.add_argument("--sparse-policies", default="natural,support_asc,support_span_asc,pivot_low,pivot_high,coefficient_weight_asc")
    parser.add_argument("--field-weights", default="1,2")
    parser.add_argument("--public-substitution-ops-per-selected", type=int, default=6)
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
                "cases": [
                    {
                        "case": item["case"],
                        "oracle": item["oracle_best_selection"],
                        "public": item["public_selector_selection"],
                        "public_pass": item["public_selector_pass_weight2_below_rho"],
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
