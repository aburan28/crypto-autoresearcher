#!/usr/bin/env python3
"""P782 held-out scaling stress for the P781 descent proxy."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P780_SCRIPT = TASK_DIR / "low_term_total2_p780_threshold_stability_descent_proxy.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P779_SUMMARY = STATE_DIR / "low_term_total2_p779_prospective_public_trim10_exception_rule_summary.json"
DEFAULT_P781_SUMMARY = STATE_DIR / "low_term_total2_p781_full_population_heldout_descent_audit_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p782_heldout_scaling_stress_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p782_heldout_scaling_stress.md"
SCHEMA = "ecdlp.low_term_total2_p782_heldout_scaling_stress.v1"

TRAIN_SELECTED_COUNT = 1024
SEED_COUNT = 1536
POOL_COUNT = 1536
MAX_HOLDOUT_COUNT = 512
HOLDOUT_CHECKPOINTS = [128, 256, 384, 512]
TRIM12_DELTA = -12
TRIM10_DELTA = -10
PUBLIC_WEIGHT2_THRESHOLD = 1.0
DEFAULT_GROUPS = [
    "fb96|23232.cr1@9643",
    "fb96|21175.bc1@8089",
    "fb112|23232.cr1@8431",
    "fb96|23232.cr1@9277",
    "fb96|114224.v1@9613",
    "fb112|21175.bc1@8467",
    "fb112|23232.cr1@8467",
    "fb96|22050.cf1@10531",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def stat(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "min": None}
    return {"count": len(values), "max": max(values), "mean": round(mean(values), 8), "min": min(values)}


def slug(value: str) -> str:
    text = "".join(ch if ch.isalnum() else "_" for ch in value)
    return "_".join(part for part in text.split("_") if part)


def delta_tag(delta: int) -> str:
    return f"dm{abs(delta)}" if delta < 0 else f"dp{delta}"


def csv_strings(text: str) -> list[str]:
    return [item.strip() for item in text.split(",") if item.strip()]


def csv_ints(text: str) -> list[int]:
    return [int(item.strip()) for item in text.split(",") if item.strip()]


def group_key(item: dict[str, Any]) -> str:
    return f"fb{int(item['factor_base_size'])}|{item['target']}"


def factor_bucket(item: dict[str, Any]) -> str:
    return f"fb{int(item['factor_base_size'])}"


def cost_for_weight(item: dict[str, Any], key: str = "costs_by_field_weight", weight: int = 2) -> dict[str, Any]:
    for cost in item.get(key) or []:
        if int(cost.get("field_op_weight") or 0) == weight:
            return cost
    return {}


def aggregate_selected(cases: list[dict[str, Any]]) -> dict[str, Any]:
    total = sum(int(item.get("total_unit_cost") or 0) for item in cases)
    rho = sum(int(item.get("selected_rho_baseline") or 0) for item in cases)
    return {
        "aggregate_weight2_total_over_selected_rho": ratio(total, rho),
        "scan_group_additions": sum(int(item.get("scan_group_additions") or 0) for item in cases),
        "selected_rho_baseline": rho,
        "sparse_solve_field_ops": sum(int(item.get("solve_field_ops") or 0) for item in cases),
        "substitution_field_ops": sum(int(item.get("substitution_field_ops") or 0) for item in cases),
        "total_unit_cost": total,
        "weighted_sparse_field_ops": sum(int(item.get("weighted_sparse_field_ops") or 0) for item in cases),
    }


def aggregate_checkpoints(cases: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for checkpoint in HOLDOUT_CHECKPOINTS:
        key = str(checkpoint)
        checkpoint_items = [
            item["heldout_checkpoints"][key]
            for item in cases
            if key in item.get("heldout_checkpoints", {})
        ]
        marginal = sum(int(item.get("marginal_total_unit_cost") or 0) for item in checkpoint_items)
        heldout_rho = sum(int(item.get("heldout_rho_baseline") or 0) for item in checkpoint_items)
        recovered_rho = sum(int(item.get("recovered_rho_baseline") or 0) for item in checkpoint_items)
        combined_total = sum(int(item.get("combined_total_unit_cost") or 0) for item in checkpoint_items)
        combined_rho = sum(int(item.get("combined_recovered_rho_baseline") or 0) for item in checkpoint_items)
        out[key] = {
            "case_count": len(checkpoint_items),
            "combined_recovered_rho_baseline": combined_rho,
            "combined_total_unit_cost": combined_total,
            "combined_total_unit_cost_over_recovered_rho": ratio(combined_total, combined_rho),
            "heldout_recovery_ok_count": sum(1 for item in checkpoint_items if item.get("heldout_recovery_ok")),
            "heldout_rho_baseline": heldout_rho,
            "marginal_total_unit_cost": marginal,
            "marginal_total_unit_cost_over_heldout_rho": ratio(marginal, heldout_rho),
            "marginal_total_unit_cost_over_recovered_rho": ratio(marginal, recovered_rho),
            "mismatch_count": sum(int(item.get("mismatch_count") or 0) for item in checkpoint_items),
            "recovered_count": sum(int(item.get("recovered_count") or 0) for item in checkpoint_items),
            "recovered_rho_baseline": recovered_rho,
            "target_count": sum(int(item.get("target_count") or 0) for item in checkpoint_items),
        }
    return out


def bucket_counts(cases: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for item in cases:
        bucket_key = str(item[key])
        bucket = out.setdefault(
            bucket_key,
            {
                "case_count": 0,
                "capacity_ok_count": 0,
                "selected_recovery_ok_count": 0,
                "selected_strict_pass_count": 0,
            },
        )
        bucket["case_count"] += 1
        bucket["capacity_ok_count"] += int(item["capacity_ok"])
        bucket["selected_recovery_ok_count"] += int(item["recovery_ok"])
        bucket["selected_strict_pass_count"] += int(item["selected_strict_pass"])
    return out


def requested_groups(text: str) -> list[str]:
    groups = csv_strings(text)
    return groups or list(DEFAULT_GROUPS)


def p777_normalized_groups(path: Path, groups: list[str]) -> dict[str, dict[str, Any]]:
    payload = load_json(path)
    normalized = ((payload.get("summary") or {}).get("normalized_cases")) or []
    by_key = {str(item.get("group_key") or group_key(item)): item for item in normalized}
    missing = sorted(set(groups) - set(by_key))
    if missing:
        raise ValueError(f"P777 normalized summary is missing groups: {missing}")
    return {group: by_key[group] for group in groups}


def p781_reference_cases(path: Path) -> dict[str, dict[str, Any]]:
    payload = load_json(path)
    return {
        str(item.get("group_key")): item
        for item in ((payload.get("summary") or {}).get("selected_cases") or [])
    }


def case_from_group(item: dict[str, Any], delta: int, namespace: str, budget: int | None = None) -> dict[str, Any]:
    fb = factor_bucket(item)
    dtag = delta_tag(delta)
    target = str(item["target"])
    target_slug = slug(target)
    return {
        "arm": f"{fb}_s1024_{dtag}",
        "budget": int(item["budget"] if budget is None else budget),
        "budget_delta": delta,
        "factor_base_size": int(item["factor_base_size"]),
        "label": f"{fb}_s1024_{dtag}_{target_slug}",
        "pool_count": POOL_COUNT,
        "seed_count": SEED_COUNT,
        "seed_prefix": f"ecdlp-p782-{namespace}-{fb}-s1024-{dtag}-{target_slug}-v1",
        "selected_count": TRAIN_SELECTED_COUNT,
        "source_group_key": str(item.get("group_key") or group_key(item)),
        "target": target,
    }


def choose_holdout_rows(p755: Any, rows: list[dict[str, Any]], selected_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected_ids = {str(row.get("seed_label")) for row in selected_rows}
    pool = p755.sorted_rows(rows)[: min(POOL_COUNT, len(rows))]
    return [
        row
        for row in pool
        if str(row.get("seed_label")) not in selected_ids and p755.form_count(row) >= 1
    ][:MAX_HOLDOUT_COUNT]


def heldout_checkpoint_cost(
    rows: list[dict[str, Any]],
    substitution: dict[str, Any],
    selected_total_unit_cost: int,
    selected_rho_baseline: int,
    field_weight: int = 2,
) -> dict[str, Any]:
    rho = int(rows[0]["generic_rho_steps"]) if rows else 0
    online = sum(int(row["cost_model"]["collection_online_group_additions"]) for row in rows)
    sub_ops = int((substitution.get("operation_counts") or {}).get("total_field_ops") or 0)
    recovered = int(substitution.get("recovered_count") or 0)
    selected_rho = len(rows) * rho
    recovered_rho = recovered * rho
    marginal_total = online + field_weight * sub_ops
    combined_total = selected_total_unit_cost + marginal_total
    combined_rho = selected_rho_baseline + recovered_rho
    return {
        "combined_recovered_rho_baseline": combined_rho,
        "combined_total_unit_cost": combined_total,
        "combined_total_unit_cost_over_recovered_rho": ratio(combined_total, combined_rho),
        "field_op_weight": field_weight,
        "heldout_online_group_additions": online,
        "heldout_recovery_ok": bool(
            rows
            and recovered == len(rows)
            and int(substitution.get("mismatch_count") or 0) == 0
        ),
        "heldout_rho_baseline": selected_rho,
        "marginal_total_unit_cost": marginal_total,
        "marginal_total_unit_cost_over_heldout_rho": ratio(marginal_total, selected_rho),
        "marginal_total_unit_cost_over_recovered_rho": ratio(marginal_total, recovered_rho),
        "mismatch_count": int(substitution.get("mismatch_count") or 0),
        "recovered_count": recovered,
        "recovered_rho_baseline": recovered_rho,
        "substitution_field_ops": sub_ops,
        "target_count": len(rows),
        "weighted_substitution_field_ops": field_weight * sub_ops,
    }


def relation_support_stats(p748: Any, p752: Any, selected_rows: list[dict[str, Any]], order: int, factor_count: int) -> dict[str, Any]:
    relations = p752.annotated_relations(
        p748.factor_eliminated_relations(selected_rows, order, factor_count),
        order,
    )
    active_columns: set[int] = set()
    for relation in relations:
        for index, value in enumerate(relation.get("coeffs") or []):
            if int(value) % order:
                active_columns.add(index)
    return {
        "active_column_count": len(active_columns),
        "factor_relation_count": len(relations),
        "max_active_column": max(active_columns) if active_columns else None,
    }


def evaluate_candidate(stack: dict[str, Any], case: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    p746 = stack["p746"]
    p748 = stack["p748"]
    p750 = stack["p750"]
    p751 = stack["p751"]
    p752 = stack["p752"]
    p755 = stack["p755"]
    p760 = stack["p760"]
    relprobe = stack["relprobe"]
    sparse_policies = csv_strings(args.sparse_policies)
    field_weights = sorted(set(csv_ints(args.field_weights) + [2]))
    rows, order = p750.collect_target_rows(
        p746,
        p748,
        relprobe,
        str(case["target"]),
        int(case["budget"]),
        int(case["seed_count"]),
        int(case["factor_base_size"]),
        int(args.width),
        str(args.walk_mode),
        str(case["seed_prefix"]),
        int(args.max_relations),
        int(args.max_subsets),
    )
    selection = p755.select_rows(rows, TRAIN_SELECTED_COUNT, POOL_COUNT, args.row_policy)
    selected_rows = selection["selected_rows"]
    scanned_rows = selection["scanned_rows"]
    if not selected_rows:
        raise RuntimeError(f"no selected rows for {case['label']}")
    public_solves = [
        p760.solve_sparse_policy(
            p748,
            p752,
            selected_rows,
            policy,
            field_weights,
            order,
            scanned_rows,
            args.public_substitution_ops_per_selected,
        )
        for policy in sparse_policies
    ]
    public_selected_solve = p760.public_choice(public_solves, TRAIN_SELECTED_COUNT)
    verified = [
        p760.verify_sparse_policy(
            p751,
            p755,
            selected_rows,
            scanned_rows,
            solved,
            field_weights,
            order,
        )
        for solved in public_solves
    ]
    selected_verified = next(
        item for item in verified if item["sparse_policy"] == public_selected_solve["sparse_policy"]
    )
    oracle_best = p760.oracle_best(verified, TRAIN_SELECTED_COUNT)
    selected_cost = cost_for_weight(selected_verified, "costs_by_field_weight", 2)
    selected_public_cost = cost_for_weight(selected_verified, "public_costs_by_field_weight", 2)
    factor_count = max((len(form["coeffs"]) - 1 for row in selected_rows for form in row.get("forms") or []), default=0)
    support = relation_support_stats(p748, p752, selected_rows, order, factor_count)
    selected_total_unit_cost = int(selected_cost.get("total_unit_cost_group_additions_plus_weighted_field_ops") or 0)
    selected_rho_baseline = int(selected_cost.get("selected_rho_baseline") or 0)
    holdout_rows = choose_holdout_rows(p755, rows, selected_rows)
    selected_ids = {str(row.get("seed_label")) for row in selected_rows}
    holdout_ids = {str(row.get("seed_label")) for row in holdout_rows}
    holdout_checkpoints: dict[str, dict[str, Any]] = {}
    for checkpoint in HOLDOUT_CHECKPOINTS:
        prefix_rows = holdout_rows[:checkpoint]
        if public_selected_solve["solve"]["full_rank"]:
            holdout_substitution = p751.substitution_recovery(
                prefix_rows,
                public_selected_solve["solve"]["factor_values"],
                order,
            )
        else:
            holdout_substitution = {
                "mismatch_count": len(prefix_rows),
                "operation_counts": {"total_field_ops": 0},
                "recovered_count": 0,
                "recovered_sample": [],
            }
        checkpoint_cost = heldout_checkpoint_cost(
            prefix_rows,
            holdout_substitution,
            selected_total_unit_cost,
            selected_rho_baseline,
            2,
        )
        checkpoint_cost["checkpoint"] = checkpoint
        checkpoint_cost["enough_rows"] = len(prefix_rows) == checkpoint
        checkpoint_cost["heldout_disjoint_from_solve"] = holdout_ids.isdisjoint(selected_ids)
        checkpoint_cost["heldout_recovery_ok"] = bool(
            checkpoint_cost["enough_rows"]
            and checkpoint_cost["heldout_disjoint_from_solve"]
            and checkpoint_cost["recovered_count"] == checkpoint
            and checkpoint_cost["mismatch_count"] == 0
        )
        holdout_checkpoints[str(checkpoint)] = checkpoint_cost
    selected_strict = bool(
        len(selected_rows) == TRAIN_SELECTED_COUNT
        and selected_verified["success"]
        and int(selected_verified["substitution"]["recovered_count"]) == TRAIN_SELECTED_COUNT
        and int(selected_verified["substitution"]["mismatch_count"]) == 0
        and (selected_cost.get("total_unit_cost_over_selected_rho") or 10**18) < 1.0
    )
    selected_recovery_ok = bool(
        selected_verified["success"]
        and int((selected_verified["solve"] or {}).get("rank") or 0) == int(case["factor_base_size"])
        and int(selected_verified["substitution"]["recovered_count"]) == TRAIN_SELECTED_COUNT
        and int(selected_verified["substitution"]["mismatch_count"]) == 0
    )
    capacity_ok = bool(
        factor_count == int(case["factor_base_size"])
        and int(support["active_column_count"]) == int(case["factor_base_size"])
    )
    max_checkpoint = holdout_checkpoints[str(max(HOLDOUT_CHECKPOINTS))]
    return {
        "active_column_count": support["active_column_count"],
        "budget": int(case["budget"]),
        "budget_delta": int(case["budget_delta"]),
        "capacity_ok": capacity_ok,
        "case": case["label"],
        "factor_base_size": int(case["factor_base_size"]),
        "factor_bucket": f"fb{int(case['factor_base_size'])}",
        "failure_class": "pass" if selected_strict and max_checkpoint["heldout_recovery_ok"] else "selected_or_holdout_failure",
        "generic_rho_steps": int(selected_rows[0]["generic_rho_steps"]) if selected_rows else None,
        "group_key": str(case["source_group_key"]),
        "heldout_available_count": len(holdout_rows),
        "heldout_checkpoints": holdout_checkpoints,
        "heldout_seed_sample": [row.get("seed_label") for row in holdout_rows[:12]],
        "oracle_best_policy": oracle_best["sparse_policy"],
        "oracle_best_weight2_over_selected_rho": cost_for_weight(oracle_best, "costs_by_field_weight", 2).get(
            "total_unit_cost_over_selected_rho"
        ),
        "policy": selected_verified["sparse_policy"],
        "public_sparse_selector_gap": bool(
            p760.policy_passes(oracle_best, TRAIN_SELECTED_COUNT)
            and not p760.policy_passes(selected_verified, TRAIN_SELECTED_COUNT)
        ),
        "public_weight2_over_selected_rho": selected_public_cost.get("total_unit_cost_over_selected_rho"),
        "rank": int((selected_verified["solve"] or {}).get("rank") or 0),
        "recovered_count": int(selected_verified["substitution"]["recovered_count"]),
        "recovery_ok": selected_recovery_ok,
        "rows_collected": len(rows),
        "scan_group_additions": selected_cost.get("candidate_scan_group_addition_cost"),
        "scanned_count": len(scanned_rows),
        "selected_count": len(selected_rows),
        "selected_count_ok": len(selected_rows) == TRAIN_SELECTED_COUNT,
        "selected_rho_baseline": selected_rho_baseline,
        "selected_seed_sample": selection["selected_seed_labels"][:12],
        "selected_strict_pass": selected_strict,
        "solve_field_ops": selected_cost.get("sparse_solve_field_ops"),
        "source": f"p782_{delta_tag(int(case['budget_delta']))}",
        "substitution_field_ops": selected_cost.get("substitution_field_ops"),
        "target": str(case["target"]),
        "total_unit_cost": selected_total_unit_cost,
        "weight2_over_selected_rho": selected_cost.get("total_unit_cost_over_selected_rho"),
        "weighted_sparse_field_ops": selected_cost.get("weighted_sparse_field_ops"),
    }


def determine_claim(summary: dict[str, Any]) -> str:
    total = int(summary["selected_group_count"])
    strict = int(summary["selected_strict_pass_count"])
    recovery = int(summary["selected_recovery_ok_count"])
    capacity = int(summary["selected_capacity_ok_count"])
    selected_agg = summary["selected_aggregate_cost"]["aggregate_weight2_total_over_selected_rho"]
    max_selected = summary["selected_weight2_stats"]["max"]
    checkpoint_costs = summary["checkpoint_aggregate_costs"]
    all_checkpoint_ok = all(
        item["case_count"] == total
        and item["heldout_recovery_ok_count"] == total
        and item["mismatch_count"] == 0
        and item["marginal_total_unit_cost_over_heldout_rho"] is not None
        and float(item["marginal_total_unit_cost_over_heldout_rho"]) < 1.0
        and item["combined_total_unit_cost_over_recovered_rho"] is not None
        and float(item["combined_total_unit_cost_over_recovered_rho"]) < 1.0
        for item in checkpoint_costs.values()
    )
    if (
        total
        and strict == total
        and recovery == total
        and capacity == total
        and selected_agg is not None
        and float(selected_agg) < 1.0
        and max_selected is not None
        and float(max_selected) < 1.0
        and all_checkpoint_ok
    ):
        return "P782_HELDOUT_SCALING_STRESS_SIGNAL"
    if (
        total
        and recovery == total
        and capacity == total
        and selected_agg is not None
        and float(selected_agg) < 1.0
    ):
        return "P782_SELECTED_SIGNAL_HELDOUT_SCALING_OPEN"
    if any(item["mismatch_count"] for item in checkpoint_costs.values()):
        return "NEGATIVE_RESULT_P782_HELDOUT_MISMATCH"
    return "NEGATIVE_RESULT_P782_HELDOUT_SCALING_STRESS"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p780 = load_module("ecdlp_p780_for_p782", P780_SCRIPT)
    groups = requested_groups(args.groups)
    base_groups = p777_normalized_groups(args.p777_summary, groups)
    p781_cases = p781_reference_cases(args.p781_summary)
    stack = p780.load_stack()
    trim12_cases = {
        group: evaluate_candidate(
            stack,
            case_from_group(base_groups[group], TRIM12_DELTA, args.seed_namespace),
            args,
        )
        for group in groups
    }
    flagged = []
    trim10_cases: dict[str, dict[str, Any]] = {}
    for group in groups:
        trim12 = trim12_cases[group]
        public_weight = trim12.get("public_weight2_over_selected_rho")
        if public_weight is not None and float(public_weight) >= PUBLIC_WEIGHT2_THRESHOLD:
            flagged.append(
                {
                    "group_key": group,
                    "trim12_case": trim12["case"],
                    "trim12_public_weight2_over_selected_rho": public_weight,
                    "trim12_weight2_over_selected_rho": trim12.get("weight2_over_selected_rho"),
                }
            )
            trim10_cases[group] = evaluate_candidate(
                stack,
                case_from_group(
                    base_groups[group],
                    TRIM10_DELTA,
                    args.seed_namespace,
                    budget=int(base_groups[group]["budget"]) + 2,
                ),
                args,
            )
    selected_cases = []
    for group in groups:
        flag = any(item["group_key"] == group for item in flagged)
        chosen = trim10_cases.get(group) if flag else trim12_cases[group]
        if chosen is None:
            chosen = trim12_cases[group]
        chosen = dict(chosen)
        chosen["exception_flag"] = flag
        chosen["p781_reference_weight2_over_selected_rho"] = (p781_cases.get(group) or {}).get(
            "weight2_over_selected_rho"
        )
        chosen["rule_selected_delta"] = int(chosen["budget_delta"])
        selected_cases.append(chosen)
    selected_cases = sorted(selected_cases, key=lambda item: item["group_key"])
    selected_weights = [
        float(item["weight2_over_selected_rho"])
        for item in selected_cases
        if item.get("weight2_over_selected_rho") is not None
    ]
    delta_counts = Counter(str(item["rule_selected_delta"]) for item in selected_cases)
    checkpoint_aggregate_costs = aggregate_checkpoints(selected_cases)
    summary = {
        "checkpoint_aggregate_costs": checkpoint_aggregate_costs,
        "checkpoint_count": len(HOLDOUT_CHECKPOINTS),
        "checkpoint_values": HOLDOUT_CHECKPOINTS,
        "factor_summaries": bucket_counts(selected_cases, "factor_bucket"),
        "flagged_group_count": len(flagged),
        "flagged_groups": flagged,
        "fresh_trim10_case_count": len(trim10_cases),
        "fresh_trim12_case_count": len(trim12_cases),
        "heldout_available_min": min((int(item["heldout_available_count"]) for item in selected_cases), default=0),
        "heldout_available_stats": stat([float(item["heldout_available_count"]) for item in selected_cases]),
        "max_checkpoint": max(HOLDOUT_CHECKPOINTS),
        "public_sparse_selector_gap_count": sum(1 for item in selected_cases if item["public_sparse_selector_gap"]),
        "public_threshold": PUBLIC_WEIGHT2_THRESHOLD,
        "requested_group_count": len(groups),
        "requested_groups": groups,
        "selected_aggregate_cost": aggregate_selected(selected_cases),
        "selected_capacity_ok_count": sum(1 for item in selected_cases if item["capacity_ok"]),
        "selected_cases": selected_cases,
        "selected_delta_counts": {key: delta_counts[key] for key in sorted(delta_counts, key=lambda value: int(value))},
        "selected_group_count": len(selected_cases),
        "selected_recovery_ok_count": sum(1 for item in selected_cases if item["recovery_ok"]),
        "selected_strict_pass_count": sum(1 for item in selected_cases if item["selected_strict_pass"]),
        "selected_weight2_stats": stat(selected_weights),
        "source_summaries": bucket_counts(selected_cases, "source"),
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p777_summary": str(args.p777_summary),
            "p779_summary": str(args.p779_summary),
            "p781_summary": str(args.p781_summary),
            "script": str(Path(__file__)),
            "shared_stack": str(P780_SCRIPT),
        },
        "claim_status": determine_claim(summary),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "REPRESENTATIVE-SUBSET: P782 stresses eight groups selected from P781 high-risk and control cases, not the full 36-group population.",
            "FRESH-PROSPECTIVE: all rows use fresh P782 seed prefixes and are not selected from P781 artifacts.",
            "PUBLIC-THRESHOLD: trim10 exception collection is triggered only by public trim12 weight-2 cost.",
            "HELDOUT-SCALING-PROXY: held-out rows are excluded from the factor solve, but remain same-distribution synthetic rows, not arbitrary cryptographic-size target descent.",
            "PRIVATE-VERIFY-ONLY: expected secrets verify selected and held-out substitution after public choices are made.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p782_heldout_scaling_stress",
        "parameters": {
            "field_weights": csv_ints(args.field_weights),
            "holdout_checkpoints": HOLDOUT_CHECKPOINTS,
            "max_holdout_count": MAX_HOLDOUT_COUNT,
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "pool_count": POOL_COUNT,
            "public_substitution_ops_per_selected": args.public_substitution_ops_per_selected,
            "public_weight2_threshold": PUBLIC_WEIGHT2_THRESHOLD,
            "row_policy": args.row_policy,
            "seed_count": SEED_COUNT,
            "seed_namespace": args.seed_namespace,
            "sparse_policies": csv_strings(args.sparse_policies),
            "train_selected_count": TRAIN_SELECTED_COUNT,
            "walk_mode": args.walk_mode,
            "width": args.width,
        },
        "schema": SCHEMA,
        "summary": summary,
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": f"{SCHEMA}.summary",
        "artifacts": payload["artifacts"],
        "claim_status": payload["claim_status"],
        "created_at": payload["created_at"],
        "honesty_boundary": payload["honesty_boundary"],
        "method": payload["method"],
        "parameters": payload["parameters"],
        "summary": payload["summary"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p777-summary", type=Path, default=DEFAULT_P777_SUMMARY)
    parser.add_argument("--p779-summary", type=Path, default=DEFAULT_P779_SUMMARY)
    parser.add_argument("--p781-summary", type=Path, default=DEFAULT_P781_SUMMARY)
    parser.add_argument("--groups", default="")
    parser.add_argument("--seed-namespace", default="scaling-v1")
    parser.add_argument("--row-policy", default="sequential_min_forms_ge_1")
    parser.add_argument("--sparse-policies", default="natural,support_asc,support_span_asc,pivot_low,pivot_high,coefficient_weight_asc")
    parser.add_argument("--width", type=int, default=2)
    parser.add_argument("--walk-mode", default="hash6")
    parser.add_argument("--max-relations", type=int, default=96)
    parser.add_argument("--max-subsets", type=int, default=25000)
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
                "checkpoint_aggregate_costs": summary["summary"]["checkpoint_aggregate_costs"],
                "claim_status": summary["claim_status"],
                "flagged_group_count": summary["summary"]["flagged_group_count"],
                "fresh_trim10_case_count": summary["summary"]["fresh_trim10_case_count"],
                "fresh_trim12_case_count": summary["summary"]["fresh_trim12_case_count"],
                "heldout_available_min": summary["summary"]["heldout_available_min"],
                "selected_aggregate_weight2": summary["summary"]["selected_aggregate_cost"][
                    "aggregate_weight2_total_over_selected_rho"
                ],
                "selected_delta_counts": summary["summary"]["selected_delta_counts"],
                "selected_group_count": summary["summary"]["selected_group_count"],
                "selected_strict_pass_count": summary["summary"]["selected_strict_pass_count"],
                "selected_weight2_max": summary["summary"]["selected_weight2_stats"]["max"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
