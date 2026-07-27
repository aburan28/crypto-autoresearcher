#!/usr/bin/env python3
"""P784 disjoint target raw-transfer stress."""

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
P782_SCRIPT = TASK_DIR / "low_term_total2_p782_heldout_scaling_stress.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p784_disjoint_target_raw_transfer_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p784_disjoint_target_raw_transfer.md"
SCHEMA = "ecdlp.low_term_total2_p784_disjoint_target_raw_transfer.v1"

TRAIN_SELECTED_COUNT = 1024
SOURCE_SEED_COUNT = 1152
SOURCE_POOL_COUNT = 1152
DEST_SEED_COUNT = 512
DEST_POOL_COUNT = 512
CONTROL_HOLDOUT_COUNT = 128
DEST_TRANSFER_COUNT = 128
TRIM12_DELTA = -12
TRIM10_DELTA = -10
PUBLIC_WEIGHT2_THRESHOLD = 1.0
DEFAULT_PAIRS = [
    "fb96|114224.v1@9341->fb96|114224.v1@9421",
    "fb96|23232.cr1@8431->fb96|23232.cr1@8467",
    "fb112|67.a1@9377->fb112|67.a1@9829",
    "fb96|22050.cf1@10531->fb96|67.a1@9803",
    "fb112|23232.cr1@9277->fb112|21175.bc1@8467",
    "fb112|114224.v1@9613->fb112|22050.cf1@10321",
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


def factor_bucket(item: dict[str, Any]) -> str:
    return f"fb{int(item['factor_base_size'])}"


def group_key(item: dict[str, Any]) -> str:
    return f"fb{int(item['factor_base_size'])}|{item['target']}"


def cost_for_weight(item: dict[str, Any], key: str = "costs_by_field_weight", weight: int = 2) -> dict[str, Any]:
    for cost in item.get(key) or []:
        if int(cost.get("field_op_weight") or 0) == weight:
            return cost
    return {}


def parse_pairs(text: str) -> list[tuple[str, str]]:
    raw_pairs = csv_strings(text) or list(DEFAULT_PAIRS)
    pairs = []
    for raw in raw_pairs:
        left, sep, right = raw.partition("->")
        if not sep or not left.strip() or not right.strip():
            raise argparse.ArgumentTypeError(f"pair must have source->dest shape, got {raw!r}")
        pairs.append((left.strip(), right.strip()))
    return pairs


def normalized_groups(path: Path, required: list[str]) -> dict[str, dict[str, Any]]:
    payload = load_json(path)
    normalized = ((payload.get("summary") or {}).get("normalized_cases")) or []
    by_key = {str(item.get("group_key") or group_key(item)): item for item in normalized}
    missing = sorted(set(required) - set(by_key))
    if missing:
        raise ValueError(f"P777 normalized summary is missing groups: {missing}")
    return {group: by_key[group] for group in required}


def case_from_group(
    item: dict[str, Any],
    delta: int,
    namespace: str,
    role: str,
    seed_count: int,
    pool_count: int,
    budget: int | None = None,
) -> dict[str, Any]:
    fb = factor_bucket(item)
    dtag = delta_tag(delta)
    target = str(item["target"])
    target_slug = slug(target)
    return {
        "arm": f"{fb}_s1024_{dtag}",
        "budget": int(item["budget"] if budget is None else budget),
        "budget_delta": delta,
        "factor_base_size": int(item["factor_base_size"]),
        "label": f"{role}_{fb}_s1024_{dtag}_{target_slug}",
        "pool_count": pool_count,
        "seed_count": seed_count,
        "seed_prefix": f"ecdlp-p784-{role}-{namespace}-{fb}-s1024-{dtag}-{target_slug}-v1",
        "selected_count": TRAIN_SELECTED_COUNT,
        "source_group_key": str(item.get("group_key") or group_key(item)),
        "target": target,
    }


def target_metadata(p746: Any, relprobe: Any, target: str) -> dict[str, Any]:
    _verifier, _record, inv = p746.load_target(relprobe, target)
    return {
        "base_order": int(inv["base_order"]),
        "label": str(inv["label"]),
        "p": int(inv["p"]),
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


def same_target_holdout_rows(p755: Any, rows: list[dict[str, Any]], selected_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected_ids = {str(row.get("seed_label")) for row in selected_rows}
    pool = p755.sorted_rows(rows)[: min(SOURCE_POOL_COUNT, len(rows))]
    return [
        row
        for row in pool
        if str(row.get("seed_label")) not in selected_ids and p755.form_count(row) >= 1
    ][:CONTROL_HOLDOUT_COUNT]


def destination_rows(p755: Any, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pool = p755.sorted_rows(rows)[: min(DEST_POOL_COUNT, len(rows))]
    return [row for row in pool if p755.form_count(row) >= 1][:DEST_TRANSFER_COUNT]


def heldout_cost(
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
    target_rho = len(rows) * rho
    recovered_rho = recovered * rho
    marginal_total = online + field_weight * sub_ops
    combined_total = selected_total_unit_cost + marginal_total
    return {
        "combined_recovered_rho_baseline": selected_rho_baseline + recovered_rho,
        "combined_target_rho_baseline": selected_rho_baseline + target_rho,
        "combined_total_unit_cost": combined_total,
        "combined_total_unit_cost_over_recovered_rho": ratio(combined_total, selected_rho_baseline + recovered_rho),
        "combined_total_unit_cost_over_selected_plus_target_rho": ratio(combined_total, selected_rho_baseline + target_rho),
        "field_op_weight": field_weight,
        "marginal_total_unit_cost": marginal_total,
        "marginal_total_unit_cost_over_recovered_rho": ratio(marginal_total, recovered_rho),
        "marginal_total_unit_cost_over_target_rho": ratio(marginal_total, target_rho),
        "mismatch_count": int(substitution.get("mismatch_count") or 0),
        "online_group_additions": online,
        "recovered_count": recovered,
        "recovered_rho_baseline": recovered_rho,
        "substitution_field_ops": sub_ops,
        "target_count": len(rows),
        "target_rho_baseline": target_rho,
        "weighted_substitution_field_ops": field_weight * sub_ops,
    }


def evaluate_source_candidate(stack: dict[str, Any], case: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
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
    selection = p755.select_rows(rows, TRAIN_SELECTED_COUNT, SOURCE_POOL_COUNT, args.row_policy)
    selected_rows = selection["selected_rows"]
    scanned_rows = selection["scanned_rows"]
    if not selected_rows:
        raise RuntimeError(f"no selected source rows for {case['label']}")
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
    control_rows = same_target_holdout_rows(p755, rows, selected_rows)
    if public_selected_solve["solve"]["full_rank"]:
        control_substitution = p751.substitution_recovery(
            control_rows,
            public_selected_solve["solve"]["factor_values"],
            order,
        )
    else:
        control_substitution = {
            "mismatch_count": len(control_rows),
            "operation_counts": {"total_field_ops": 0},
            "recovered_count": 0,
            "recovered_sample": [],
        }
    control_cost = heldout_cost(control_rows, control_substitution, selected_total_unit_cost, selected_rho_baseline, 2)
    selected_strict = bool(
        len(selected_rows) == TRAIN_SELECTED_COUNT
        and selected_verified["success"]
        and int(selected_verified["substitution"]["recovered_count"]) == TRAIN_SELECTED_COUNT
        and int(selected_verified["substitution"]["mismatch_count"]) == 0
        and (selected_cost.get("total_unit_cost_over_selected_rho") or 10**18) < 1.0
    )
    recovery_ok = bool(
        selected_verified["success"]
        and int((selected_verified["solve"] or {}).get("rank") or 0) == int(case["factor_base_size"])
        and int(selected_verified["substitution"]["recovered_count"]) == TRAIN_SELECTED_COUNT
        and int(selected_verified["substitution"]["mismatch_count"]) == 0
    )
    capacity_ok = bool(
        factor_count == int(case["factor_base_size"])
        and int(support["active_column_count"]) == int(case["factor_base_size"])
    )
    control_ok = bool(
        len(control_rows) == CONTROL_HOLDOUT_COUNT
        and int(control_substitution["recovered_count"]) == CONTROL_HOLDOUT_COUNT
        and int(control_substitution["mismatch_count"]) == 0
    )
    return {
        "case": case["label"],
        "control_cost": control_cost,
        "control_mismatch_count": int(control_substitution["mismatch_count"]),
        "control_recovered_count": int(control_substitution["recovered_count"]),
        "control_target_count": len(control_rows),
        "control_ok": control_ok,
        "factor_base_size": int(case["factor_base_size"]),
        "factor_bucket": f"fb{int(case['factor_base_size'])}",
        "factor_values": public_selected_solve["solve"]["factor_values"],
        "group_key": str(case["source_group_key"]),
        "order": order,
        "policy": selected_verified["sparse_policy"],
        "public_sparse_selector_gap": bool(
            p760.policy_passes(oracle_best, TRAIN_SELECTED_COUNT)
            and not p760.policy_passes(selected_verified, TRAIN_SELECTED_COUNT)
        ),
        "public_weight2_over_selected_rho": selected_public_cost.get("total_unit_cost_over_selected_rho"),
        "rank": int((selected_verified["solve"] or {}).get("rank") or 0),
        "recovery_ok": recovery_ok,
        "selected_count": len(selected_rows),
        "selected_rho_baseline": selected_rho_baseline,
        "selected_strict_pass": selected_strict,
        "selected_total_unit_cost": selected_total_unit_cost,
        "selected_weight2_over_rho": selected_cost.get("total_unit_cost_over_selected_rho"),
        "solve_field_ops": selected_cost.get("sparse_solve_field_ops"),
        "source_case": dict(case),
        "source_metadata": None,
        "support_active_column_count": support["active_column_count"],
        "target": str(case["target"]),
    }


def collect_destination(stack: dict[str, Any], case: dict[str, Any], args: argparse.Namespace) -> tuple[list[dict[str, Any]], int]:
    p746 = stack["p746"]
    p748 = stack["p748"]
    p750 = stack["p750"]
    p755 = stack["p755"]
    relprobe = stack["relprobe"]
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
    return destination_rows(p755, rows), order


def evaluate_pair(
    stack: dict[str, Any],
    base_groups: dict[str, dict[str, Any]],
    source_group: str,
    dest_group: str,
    args: argparse.Namespace,
) -> dict[str, Any]:
    p746 = stack["p746"]
    p751 = stack["p751"]
    relprobe = stack["relprobe"]
    source_item = base_groups[source_group]
    dest_item = base_groups[dest_group]
    if int(source_item["factor_base_size"]) != int(dest_item["factor_base_size"]):
        raise ValueError(f"source/dest factor-base mismatch: {source_group} -> {dest_group}")
    source_trim12 = evaluate_source_candidate(
        stack,
        case_from_group(
            source_item,
            TRIM12_DELTA,
            args.seed_namespace,
            "source",
            SOURCE_SEED_COUNT,
            SOURCE_POOL_COUNT,
        ),
        args,
    )
    source_selected = source_trim12
    trim10_evaluated = False
    public_weight = source_trim12.get("public_weight2_over_selected_rho")
    if public_weight is not None and float(public_weight) >= PUBLIC_WEIGHT2_THRESHOLD:
        source_selected = evaluate_source_candidate(
            stack,
            case_from_group(
                source_item,
                TRIM10_DELTA,
                args.seed_namespace,
                "source",
                SOURCE_SEED_COUNT,
                SOURCE_POOL_COUNT,
                budget=int(source_item["budget"]) + 2,
            ),
            args,
        )
        trim10_evaluated = True
    dest_case = case_from_group(
        dest_item,
        TRIM12_DELTA,
        args.seed_namespace,
        "dest",
        DEST_SEED_COUNT,
        DEST_POOL_COUNT,
    )
    dest_rows, dest_order = collect_destination(stack, dest_case, args)
    if source_selected["rank"] == int(source_selected["factor_base_size"]):
        transfer_substitution = p751.substitution_recovery(
            dest_rows,
            source_selected["factor_values"],
            dest_order,
        )
    else:
        transfer_substitution = {
            "mismatch_count": len(dest_rows),
            "operation_counts": {"total_field_ops": 0},
            "recovered_count": 0,
            "recovered_sample": [],
        }
    transfer_cost = heldout_cost(
        dest_rows,
        transfer_substitution,
        int(source_selected["selected_total_unit_cost"]),
        int(source_selected["selected_rho_baseline"]),
        2,
    )
    source_meta = target_metadata(p746, relprobe, str(source_item["target"]))
    dest_meta = target_metadata(p746, relprobe, str(dest_item["target"]))
    expected_random = ratio(len(dest_rows), dest_order)
    source_public_over = source_trim12.get("public_weight2_over_selected_rho")
    return {
        "dest_case": dest_case,
        "dest_group_key": dest_group,
        "dest_metadata": dest_meta,
        "dest_order": dest_order,
        "dest_rows_available": len(dest_rows),
        "dest_target": str(dest_item["target"]),
        "expected_random_recovered": expected_random,
        "factor_bucket": f"fb{int(source_item['factor_base_size'])}",
        "same_label": source_meta["label"] == dest_meta["label"],
        "same_order": source_meta["base_order"] == dest_meta["base_order"],
        "same_prime": source_meta["p"] == dest_meta["p"],
        "source_budget_delta": int(source_selected["source_case"]["budget_delta"]),
        "source_control_cost": source_selected["control_cost"],
        "source_control_mismatch_count": source_selected["control_mismatch_count"],
        "source_control_ok": source_selected["control_ok"],
        "source_control_recovered_count": source_selected["control_recovered_count"],
        "source_control_target_count": source_selected["control_target_count"],
        "source_group_key": source_group,
        "source_metadata": source_meta,
        "source_order": source_selected["order"],
        "source_policy": source_selected["policy"],
        "source_public_trim12_weight2_over_rho": source_public_over,
        "source_rank": source_selected["rank"],
        "source_recovery_ok": source_selected["recovery_ok"],
        "source_selected_strict_pass": source_selected["selected_strict_pass"],
        "source_selected_weight2_over_rho": source_selected["selected_weight2_over_rho"],
        "source_target": str(source_item["target"]),
        "trim10_evaluated": trim10_evaluated,
        "transfer_cost": transfer_cost,
        "transfer_mismatch_count": int(transfer_substitution["mismatch_count"]),
        "transfer_recovered_count": int(transfer_substitution["recovered_count"]),
        "transfer_recovered_sample": transfer_substitution.get("recovered_sample") or [],
        "transfer_target_count": len(dest_rows),
    }


def aggregate_pairs(pairs: list[dict[str, Any]]) -> dict[str, Any]:
    target_count = sum(int(item["transfer_target_count"]) for item in pairs)
    recovered = sum(int(item["transfer_recovered_count"]) for item in pairs)
    mismatches = sum(int(item["transfer_mismatch_count"]) for item in pairs)
    target_rho = sum(int((item["transfer_cost"] or {}).get("target_rho_baseline") or 0) for item in pairs)
    marginal = sum(int((item["transfer_cost"] or {}).get("marginal_total_unit_cost") or 0) for item in pairs)
    combined_total = sum(int((item["transfer_cost"] or {}).get("combined_total_unit_cost") or 0) for item in pairs)
    combined_target_rho = sum(int((item["transfer_cost"] or {}).get("combined_target_rho_baseline") or 0) for item in pairs)
    return {
        "combined_source_plus_dest_total_unit_cost": combined_total,
        "combined_source_plus_dest_total_over_target_rho": ratio(combined_total, combined_target_rho),
        "dest_target_count": target_count,
        "factor_bucket_counts": dict(Counter(str(item["factor_bucket"]) for item in pairs)),
        "marginal_total_unit_cost": marginal,
        "marginal_total_unit_cost_over_dest_target_rho": ratio(marginal, target_rho),
        "pair_count": len(pairs),
        "same_label_pair_count": sum(1 for item in pairs if item["same_label"]),
        "same_order_pair_count": sum(1 for item in pairs if item["same_order"]),
        "same_prime_pair_count": sum(1 for item in pairs if item["same_prime"]),
        "transfer_mismatch_count": mismatches,
        "transfer_recovered_count": recovered,
        "transfer_target_rho_baseline": target_rho,
    }


def determine_claim(summary: dict[str, Any]) -> str:
    pair_count = int(summary["pair_count"])
    controls_ok = int(summary["source_control_ok_count"]) == pair_count
    strict_ok = int(summary["source_selected_strict_pass_count"]) == pair_count
    dest_ready = int(summary["dest_capacity_ok_count"]) == pair_count
    recovered = int(summary["transfer_aggregate"]["transfer_recovered_count"])
    target_count = int(summary["transfer_aggregate"]["dest_target_count"])
    mismatches = int(summary["transfer_aggregate"]["transfer_mismatch_count"])
    if controls_ok and strict_ok and dest_ready and recovered == 0 and mismatches == target_count:
        return "NEGATIVE_RESULT_P784_RAW_DISJOINT_TARGET_TRANSFER_FAILS_WITH_CONTROLS"
    if controls_ok and strict_ok and dest_ready and recovered > 0:
        return "P784_RAW_DISJOINT_TARGET_TRANSFER_PARTIAL_SIGNAL"
    if not controls_ok:
        return "NEGATIVE_RESULT_P784_SOURCE_CONTROL_FAILURE"
    return "NEGATIVE_RESULT_P784_RAW_DISJOINT_TARGET_TRANSFER_INCONCLUSIVE"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p782 = load_module("ecdlp_p782_for_p784", P782_SCRIPT)
    p780 = p782.load_module("ecdlp_p780_for_p784", p782.P780_SCRIPT)
    stack = p780.load_stack()
    pairs = parse_pairs(args.pairs)
    required = sorted({group for pair in pairs for group in pair})
    base_groups = normalized_groups(args.p777_summary, required)
    pair_results = [
        evaluate_pair(stack, base_groups, source, dest, args)
        for source, dest in pairs
    ]
    source_weights = [
        float(item["source_selected_weight2_over_rho"])
        for item in pair_results
        if item.get("source_selected_weight2_over_rho") is not None
    ]
    transfer_margins = [
        float(item["transfer_cost"]["marginal_total_unit_cost_over_dest_target_rho"])
        for item in pair_results
        if item.get("transfer_cost") and item["transfer_cost"].get("marginal_total_unit_cost_over_dest_target_rho") is not None
    ]
    summary = {
        "dest_capacity_ok_count": sum(1 for item in pair_results if int(item["dest_rows_available"]) == DEST_TRANSFER_COUNT),
        "dest_transfer_count": DEST_TRANSFER_COUNT,
        "pair_count": len(pair_results),
        "pairs": pair_results,
        "public_threshold": PUBLIC_WEIGHT2_THRESHOLD,
        "source_control_ok_count": sum(1 for item in pair_results if item["source_control_ok"]),
        "source_control_recovered_count": sum(int(item["source_control_recovered_count"]) for item in pair_results),
        "source_control_target_count": sum(int(item["source_control_target_count"]) for item in pair_results),
        "source_selected_strict_pass_count": sum(1 for item in pair_results if item["source_selected_strict_pass"]),
        "source_selected_weight2_stats": stat(source_weights),
        "source_trim10_case_count": sum(1 for item in pair_results if item["trim10_evaluated"]),
        "source_trim12_case_count": len(pair_results),
        "transfer_aggregate": aggregate_pairs(pair_results),
        "transfer_margin_stats": stat(transfer_margins),
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p777_summary": str(args.p777_summary),
            "script": str(Path(__file__)),
            "shared_scaling_evaluator": str(P782_SCRIPT),
        },
        "claim_status": determine_claim(summary),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "RAW-TRANSFER-STRESS: P784 directly reuses source factor values on disjoint target rows; it does not implement a factor-basis alignment map.",
            "POSITIVE-CONTROL: source same-target held-out rows must recover before interpreting cross-target failure.",
            "MODEL-BOUND: direct source values are reduced modulo the destination order for substitution, which is intentionally a raw-reuse negative control.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p784_disjoint_target_raw_transfer",
        "parameters": {
            "control_holdout_count": CONTROL_HOLDOUT_COUNT,
            "dest_pool_count": DEST_POOL_COUNT,
            "dest_seed_count": DEST_SEED_COUNT,
            "dest_transfer_count": DEST_TRANSFER_COUNT,
            "field_weights": csv_ints(args.field_weights),
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "pairs": [f"{source}->{dest}" for source, dest in pairs],
            "public_substitution_ops_per_selected": args.public_substitution_ops_per_selected,
            "public_weight2_threshold": PUBLIC_WEIGHT2_THRESHOLD,
            "row_policy": args.row_policy,
            "seed_namespace": args.seed_namespace,
            "source_pool_count": SOURCE_POOL_COUNT,
            "source_seed_count": SOURCE_SEED_COUNT,
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
    parser.add_argument("--pairs", default="")
    parser.add_argument("--seed-namespace", default="rawxfer-v1")
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
                "dest_capacity_ok_count": summary["summary"]["dest_capacity_ok_count"],
                "pair_count": summary["summary"]["pair_count"],
                "source_control_ok_count": summary["summary"]["source_control_ok_count"],
                "source_selected_strict_pass_count": summary["summary"]["source_selected_strict_pass_count"],
                "source_trim10_case_count": summary["summary"]["source_trim10_case_count"],
                "transfer_aggregate": summary["summary"]["transfer_aggregate"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
