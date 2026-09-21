#!/usr/bin/env python3
"""P780 focused threshold-stability and held-out descent proxy."""

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
P760_SCRIPT = TASK_DIR / "low_term_total2_p760_public_sparse_policy_selector.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P763_SUMMARY = STATE_DIR / "low_term_total2_p763_factor_base_limit_extension_smoke_summary.json"
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P779_SUMMARY = STATE_DIR / "low_term_total2_p779_prospective_public_trim10_exception_rule_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p780_threshold_stability_descent_proxy_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p780_threshold_stability_descent_proxy.md"
SCHEMA = "ecdlp.low_term_total2_p780_threshold_stability_descent_proxy.v1"

TRAIN_SELECTED_COUNT = 1024
HOLDOUT_COUNT = 128
SEED_COUNT = 1152
POOL_COUNT = 1152
TRIM12_DELTA = -12
TRIM10_DELTA = -10
PUBLIC_WEIGHT2_THRESHOLD = 1.0


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


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def slug(value: str) -> str:
    text = "".join(ch if ch.isalnum() else "_" for ch in value)
    return "_".join(part for part in text.split("_") if part)


def delta_tag(delta: int) -> str:
    return f"dm{abs(delta)}" if delta < 0 else f"dp{delta}"


def csv_strings(text: str) -> list[str]:
    return [item.strip() for item in text.split(",") if item.strip()]


def csv_ints(text: str) -> list[int]:
    return [int(item.strip()) for item in text.split(",") if item.strip()]


def stat(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "min": None}
    return {"count": len(values), "max": max(values), "mean": round(mean(values), 8), "min": min(values)}


def group_key(item: dict[str, Any]) -> str:
    return f"fb{int(item['factor_base_size'])}|{item['target']}"


def factor_bucket(item: dict[str, Any]) -> str:
    return f"fb{int(item['factor_base_size'])}"


def cost_for_weight(item: dict[str, Any], key: str = "costs_by_field_weight", weight: int = 2) -> dict[str, Any]:
    for cost in item.get(key) or []:
        if int(cost.get("field_op_weight") or 0) == weight:
            return cost
    return {}


def p779_risk_groups(path: Path, explicit: str = "") -> list[str]:
    if explicit:
        return sorted(set(csv_strings(explicit)))
    payload = load_json(path)
    summary = payload.get("summary") or {}
    flagged = {str(item["group_key"]) for item in summary.get("flagged_groups") or []}
    selected = summary.get("selected_cases") or []
    if selected:
        max_case = max(
            selected,
            key=lambda item: float(item.get("weight2_over_selected_rho") or -1.0),
        )
        flagged.add(str(max_case["group_key"]))
    return sorted(flagged)


def p777_normalized_groups(path: Path, risk_groups: list[str]) -> dict[str, dict[str, Any]]:
    payload = load_json(path)
    normalized = ((payload.get("summary") or {}).get("normalized_cases")) or []
    by_key = {str(item.get("group_key") or group_key(item)): item for item in normalized}
    missing = sorted(set(risk_groups) - set(by_key))
    if missing:
        raise ValueError(f"P777 normalized summary is missing risk groups: {missing}")
    return {group: by_key[group] for group in risk_groups}


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
        "seed_prefix": f"ecdlp-p780-{namespace}-{fb}-s1024-{dtag}-{target_slug}-v1",
        "selected_count": TRAIN_SELECTED_COUNT,
        "source_group_key": str(item.get("group_key") or group_key(item)),
        "target": target,
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


def choose_holdout_rows(p755: Any, rows: list[dict[str, Any]], selected_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected_ids = {str(row.get("seed_label")) for row in selected_rows}
    pool = p755.sorted_rows(rows)[: min(POOL_COUNT, len(rows))]
    return [
        row
        for row in pool
        if str(row.get("seed_label")) not in selected_ids and p755.form_count(row) >= 1
    ][:HOLDOUT_COUNT]


def heldout_cost(rows: list[dict[str, Any]], substitution: dict[str, Any], field_weight: int = 2) -> dict[str, Any]:
    rho = int(rows[0]["generic_rho_steps"]) if rows else 0
    setup = int(rows[0]["cost_model"]["subset_group_additions"]) if rows else 0
    online = sum(int(row["cost_model"]["collection_online_group_additions"]) for row in rows)
    sub_ops = int((substitution.get("operation_counts") or {}).get("total_field_ops") or 0)
    recovered = int(substitution.get("recovered_count") or 0)
    selected_rho = len(rows) * rho
    recovered_rho = recovered * rho
    marginal_total = online + field_weight * sub_ops
    with_setup_total = setup + marginal_total
    return {
        "field_op_weight": field_weight,
        "heldout_online_group_additions": online,
        "heldout_rho_baseline": selected_rho,
        "heldout_setup_group_additions": setup,
        "marginal_total_unit_cost": marginal_total,
        "marginal_total_unit_cost_over_heldout_rho": ratio(marginal_total, selected_rho),
        "marginal_total_unit_cost_over_recovered_rho": ratio(marginal_total, recovered_rho),
        "recovered_rho_baseline": recovered_rho,
        "substitution_field_ops": sub_ops,
        "weighted_substitution_field_ops": field_weight * sub_ops,
        "with_setup_total_unit_cost": with_setup_total,
        "with_setup_total_unit_cost_over_heldout_rho": ratio(with_setup_total, selected_rho),
    }


def load_stack() -> dict[str, Any]:
    p760 = load_module("ecdlp_p760_for_p780", P760_SCRIPT)
    p755 = p760.load_module("ecdlp_p755_for_p780", p760.P755_SCRIPT)
    p746 = p755.load_module("ecdlp_p746_for_p780", p755.P746_SCRIPT)
    p748 = p755.load_module("ecdlp_p748_for_p780", p755.P748_SCRIPT)
    p750 = p755.load_module("ecdlp_p750_for_p780", p755.P750_SCRIPT)
    p751 = p755.load_module("ecdlp_p751_for_p780", p755.P751_SCRIPT)
    p752 = p755.load_module("ecdlp_p752_for_p780", p755.P752_SCRIPT)
    relprobe = p746.load_relation_probe_module()
    return {
        "p746": p746,
        "p748": p748,
        "p750": p750,
        "p751": p751,
        "p752": p752,
        "p755": p755,
        "p760": p760,
        "relprobe": relprobe,
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
    holdout_rows = choose_holdout_rows(p755, rows, selected_rows)
    if public_selected_solve["solve"]["full_rank"]:
        holdout_substitution = p751.substitution_recovery(
            holdout_rows,
            public_selected_solve["solve"]["factor_values"],
            order,
        )
    else:
        holdout_substitution = {
            "mismatch_count": len(holdout_rows),
            "operation_counts": {"total_field_ops": 0},
            "recovered_count": 0,
            "recovered_sample": [],
        }
    holdout_ids = {str(row.get("seed_label")) for row in holdout_rows}
    selected_ids = {str(row.get("seed_label")) for row in selected_rows}
    holdout_cost_summary = heldout_cost(holdout_rows, holdout_substitution, 2)
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
    holdout_recovery_ok = bool(
        len(holdout_rows) == HOLDOUT_COUNT
        and holdout_ids.isdisjoint(selected_ids)
        and int(holdout_substitution["recovered_count"]) == len(holdout_rows)
        and int(holdout_substitution["mismatch_count"]) == 0
    )
    return {
        "active_column_count": support["active_column_count"],
        "budget": int(case["budget"]),
        "budget_delta": int(case["budget_delta"]),
        "capacity_ok": capacity_ok,
        "case": case["label"],
        "factor_base_size": int(case["factor_base_size"]),
        "factor_bucket": f"fb{int(case['factor_base_size'])}",
        "failure_class": "pass" if selected_strict else "selected_or_cost_failure",
        "generic_rho_steps": int(selected_rows[0]["generic_rho_steps"]) if selected_rows else None,
        "group_key": str(case["source_group_key"]),
        "heldout_cost": holdout_cost_summary,
        "heldout_disjoint_from_solve": holdout_ids.isdisjoint(selected_ids),
        "heldout_mismatch_count": int(holdout_substitution["mismatch_count"]),
        "heldout_recovered_count": int(holdout_substitution["recovered_count"]),
        "heldout_recovery_ok": holdout_recovery_ok,
        "heldout_seed_sample": [row.get("seed_label") for row in holdout_rows[:12]],
        "heldout_target_count": len(holdout_rows),
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
        "selected_rho_baseline": selected_cost.get("selected_rho_baseline"),
        "selected_seed_sample": selection["selected_seed_labels"][:12],
        "selected_strict_pass": selected_strict,
        "solve_field_ops": selected_cost.get("sparse_solve_field_ops"),
        "source": f"p780_{delta_tag(int(case['budget_delta']))}",
        "substitution_field_ops": selected_cost.get("substitution_field_ops"),
        "target": str(case["target"]),
        "total_unit_cost": selected_cost.get("total_unit_cost_group_additions_plus_weighted_field_ops"),
        "train_plus_holdout": {
            "combined_recovered_rho_baseline": (selected_cost.get("selected_rho_baseline") or 0)
            + holdout_cost_summary["recovered_rho_baseline"],
            "combined_total_unit_cost": (selected_cost.get("total_unit_cost_group_additions_plus_weighted_field_ops") or 0)
            + holdout_cost_summary["marginal_total_unit_cost"],
            "combined_total_unit_cost_over_recovered_rho": ratio(
                (selected_cost.get("total_unit_cost_group_additions_plus_weighted_field_ops") or 0)
                + holdout_cost_summary["marginal_total_unit_cost"],
                (selected_cost.get("selected_rho_baseline") or 0) + holdout_cost_summary["recovered_rho_baseline"],
            ),
        },
        "weight2_over_selected_rho": selected_cost.get("total_unit_cost_over_selected_rho"),
        "weighted_sparse_field_ops": selected_cost.get("weighted_sparse_field_ops"),
    }


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


def aggregate_holdout(cases: list[dict[str, Any]]) -> dict[str, Any]:
    marginal = sum(int((item.get("heldout_cost") or {}).get("marginal_total_unit_cost") or 0) for item in cases)
    rho = sum(int((item.get("heldout_cost") or {}).get("heldout_rho_baseline") or 0) for item in cases)
    recovered_rho = sum(int((item.get("heldout_cost") or {}).get("recovered_rho_baseline") or 0) for item in cases)
    combined_total = sum(int((item.get("train_plus_holdout") or {}).get("combined_total_unit_cost") or 0) for item in cases)
    combined_rho = sum(int((item.get("train_plus_holdout") or {}).get("combined_recovered_rho_baseline") or 0) for item in cases)
    return {
        "combined_total_unit_cost": combined_total,
        "combined_total_unit_cost_over_recovered_rho": ratio(combined_total, combined_rho),
        "combined_recovered_rho_baseline": combined_rho,
        "heldout_rho_baseline": rho,
        "marginal_total_unit_cost": marginal,
        "marginal_total_unit_cost_over_heldout_rho": ratio(marginal, rho),
        "marginal_total_unit_cost_over_recovered_rho": ratio(marginal, recovered_rho),
        "recovered_rho_baseline": recovered_rho,
    }


def bucket_counts(cases: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for item in cases:
        bucket_key = str(item[key])
        bucket = out.setdefault(
            bucket_key,
            {
                "case_count": 0,
                "capacity_ok_count": 0,
                "heldout_recovery_ok_count": 0,
                "recovery_ok_count": 0,
                "selected_strict_pass_count": 0,
            },
        )
        bucket["case_count"] += 1
        bucket["capacity_ok_count"] += int(item["capacity_ok"])
        bucket["heldout_recovery_ok_count"] += int(item["heldout_recovery_ok"])
        bucket["recovery_ok_count"] += int(item["recovery_ok"])
        bucket["selected_strict_pass_count"] += int(item["selected_strict_pass"])
    return out


def determine_claim(summary: dict[str, Any]) -> str:
    total = int(summary["risk_group_count"])
    selected = int(summary["selected_group_count"])
    strict = int(summary["selected_strict_pass_count"])
    recovery = int(summary["selected_recovery_ok_count"])
    capacity = int(summary["selected_capacity_ok_count"])
    holdout = int(summary["heldout_recovery_ok_count"])
    missing = int(summary["missing_switch_candidate_count"])
    selected_agg = summary["selected_aggregate_cost"]["aggregate_weight2_total_over_selected_rho"]
    holdout_agg = summary["heldout_aggregate_cost"]["marginal_total_unit_cost_over_heldout_rho"]
    combined_agg = summary["heldout_aggregate_cost"]["combined_total_unit_cost_over_recovered_rho"]
    max_selected = summary["selected_weight2_stats"]["max"]
    if (
        total
        and selected == total
        and strict == total
        and recovery == total
        and capacity == total
        and holdout == total
        and missing == 0
        and selected_agg is not None
        and float(selected_agg) < 1.0
        and max_selected is not None
        and float(max_selected) < 1.0
        and holdout_agg is not None
        and float(holdout_agg) < 1.0
        and combined_agg is not None
        and float(combined_agg) < 1.0
    ):
        return "P780_THRESHOLD_STABILITY_DESCENT_PROXY_ALL_RISK_SIGNAL"
    if (
        total
        and selected == total
        and strict == total
        and recovery == total
        and capacity == total
        and missing == 0
        and selected_agg is not None
        and float(selected_agg) < 1.0
    ):
        return "P780_THRESHOLD_STABILITY_SELECTED_SIGNAL_HELDOUT_OPEN"
    if missing:
        return "P780_THRESHOLD_STABILITY_MISSING_SWITCH"
    if recovery == selected and capacity == selected:
        return "P780_THRESHOLD_STABILITY_RECOVERY_OK_COST_NEGATIVE"
    return "NEGATIVE_RESULT_P780_THRESHOLD_STABILITY_DESCENT_PROXY"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    risk_groups = p779_risk_groups(args.p779_summary, args.risk_groups)
    base_groups = p777_normalized_groups(args.p777_summary, risk_groups)
    stack = load_stack()
    trim12_cases = {
        group: evaluate_candidate(
            stack,
            case_from_group(base_groups[group], TRIM12_DELTA, args.seed_namespace),
            args,
        )
        for group in risk_groups
    }
    flagged = []
    trim10_cases: dict[str, dict[str, Any]] = {}
    for group in risk_groups:
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
    missing_switches = []
    for group in risk_groups:
        chosen = trim12_cases[group]
        flag = any(item["group_key"] == group for item in flagged)
        if flag:
            chosen = trim10_cases.get(group) or trim12_cases[group]
            if group not in trim10_cases:
                missing_switches.append({"group_key": group, "missing": "trim10"})
        chosen = dict(chosen)
        chosen["exception_flag"] = flag
        chosen["rule_selected_delta"] = int(chosen["budget_delta"])
        selected_cases.append(chosen)
    selected_cases = sorted(selected_cases, key=lambda item: item["group_key"])
    selected_weights = [
        float(item["weight2_over_selected_rho"])
        for item in selected_cases
        if item.get("weight2_over_selected_rho") is not None
    ]
    holdout_margins = [
        float((item["heldout_cost"] or {}).get("marginal_total_unit_cost_over_heldout_rho"))
        for item in selected_cases
        if (item["heldout_cost"] or {}).get("marginal_total_unit_cost_over_heldout_rho") is not None
    ]
    delta_counts = Counter(str(item["rule_selected_delta"]) for item in selected_cases)
    p779_summary = (load_json(args.p779_summary).get("summary") or {})
    p779_flagged = {str(item["group_key"]) for item in p779_summary.get("flagged_groups") or []}
    p780_flagged = {str(item["group_key"]) for item in flagged}
    summary = {
        "factor_summaries": bucket_counts(selected_cases, "factor_bucket"),
        "flagged_group_count": len(flagged),
        "flagged_groups": flagged,
        "fresh_trim10_case_count": len(trim10_cases),
        "fresh_trim12_case_count": len(trim12_cases),
        "heldout_aggregate_cost": aggregate_holdout(selected_cases),
        "heldout_mismatch_count": sum(int(item["heldout_mismatch_count"]) for item in selected_cases),
        "heldout_recovered_count": sum(int(item["heldout_recovered_count"]) for item in selected_cases),
        "heldout_recovery_ok_count": sum(1 for item in selected_cases if item["heldout_recovery_ok"]),
        "heldout_target_count": sum(int(item["heldout_target_count"]) for item in selected_cases),
        "heldout_weight2_margin_stats": stat(holdout_margins),
        "missing_switch_candidate_count": len(missing_switches),
        "missing_switch_candidates": missing_switches,
        "p779_flagged_groups": sorted(p779_flagged),
        "public_sparse_selector_gap_count": sum(1 for item in selected_cases if item["public_sparse_selector_gap"]),
        "public_threshold": PUBLIC_WEIGHT2_THRESHOLD,
        "risk_group_count": len(risk_groups),
        "risk_groups": risk_groups,
        "selected_aggregate_cost": aggregate_selected(selected_cases),
        "selected_capacity_ok_count": sum(1 for item in selected_cases if item["capacity_ok"]),
        "selected_cases": selected_cases,
        "selected_delta_counts": {key: delta_counts[key] for key in sorted(delta_counts, key=lambda value: int(value))},
        "selected_group_count": len(selected_cases),
        "selected_recovery_ok_count": sum(1 for item in selected_cases if item["recovery_ok"]),
        "selected_strict_pass_count": sum(1 for item in selected_cases if item["selected_strict_pass"]),
        "selected_weight2_stats": stat(selected_weights),
        "source_summaries": bucket_counts(selected_cases, "source"),
        "threshold_overlap_with_p779": {
            "intersection": sorted(p779_flagged & p780_flagged),
            "newly_flagged_in_p780": sorted(p780_flagged - p779_flagged),
            "p779_flagged_absent_in_p780": sorted((p779_flagged & set(risk_groups)) - p780_flagged),
        },
        "trim10_cases": [trim10_cases[group] for group in sorted(trim10_cases)],
        "trim12_cases": [trim12_cases[group] for group in sorted(trim12_cases)],
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p763_summary": str(args.p763_summary),
            "p777_summary": str(args.p777_summary),
            "p779_summary": str(args.p779_summary),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(summary),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "FOCUSED-RISK-SUBSET: P780 tests P779 flagged groups plus the previous maximum-cost selected group, not the full 36-group population.",
            "FRESH-PROSPECTIVE: all rows use fresh P780 seed prefixes and are not selected from P779 artifacts.",
            "PUBLIC-THRESHOLD: trim10 exception collection is triggered only by public trim12 weight-2 cost.",
            "HELDOUT-PROXY: held-out rows are excluded from the factor solve, but they are same-distribution synthetic challenge rows, not arbitrary target descent at cryptographic size.",
            "PRIVATE-VERIFY-ONLY: expected secrets verify selected and held-out substitution after public choices are made.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p780_threshold_stability_descent_proxy",
        "parameters": {
            "field_weights": csv_ints(args.field_weights),
            "holdout_count": HOLDOUT_COUNT,
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
    parser.add_argument("--p763-summary", type=Path, default=DEFAULT_P763_SUMMARY)
    parser.add_argument("--p777-summary", type=Path, default=DEFAULT_P777_SUMMARY)
    parser.add_argument("--p779-summary", type=Path, default=DEFAULT_P779_SUMMARY)
    parser.add_argument("--risk-groups", default="")
    parser.add_argument("--seed-namespace", default="risk-v1")
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
                "claim_status": summary["claim_status"],
                "flagged_group_count": summary["summary"]["flagged_group_count"],
                "fresh_trim10_case_count": summary["summary"]["fresh_trim10_case_count"],
                "fresh_trim12_case_count": summary["summary"]["fresh_trim12_case_count"],
                "heldout_marginal_total_over_rho": summary["summary"]["heldout_aggregate_cost"][
                    "marginal_total_unit_cost_over_heldout_rho"
                ],
                "heldout_mismatch_count": summary["summary"]["heldout_mismatch_count"],
                "heldout_recovered_count": summary["summary"]["heldout_recovered_count"],
                "heldout_target_count": summary["summary"]["heldout_target_count"],
                "risk_group_count": summary["summary"]["risk_group_count"],
                "selected_aggregate_weight2": summary["summary"]["selected_aggregate_cost"][
                    "aggregate_weight2_total_over_selected_rho"
                ],
                "selected_delta_counts": summary["summary"]["selected_delta_counts"],
                "selected_strict_pass_count": summary["summary"]["selected_strict_pass_count"],
                "selected_weight2_max": summary["summary"]["selected_weight2_stats"]["max"],
                "threshold_overlap_with_p779": summary["summary"]["threshold_overlap_with_p779"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
