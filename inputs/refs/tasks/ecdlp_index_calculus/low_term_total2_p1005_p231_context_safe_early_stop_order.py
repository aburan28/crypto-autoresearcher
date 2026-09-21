#!/usr/bin/env python3
"""P1005 public early-stop ordering for context-safe p231 scalar-valid groups."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p996_p231_early_stop_recall_split as p996
import low_term_total2_p998_p231_branch_ensemble_selector as p998
import low_term_total2_p999_p231_hash_basis_quality as p999
import low_term_total2_p1000_p231_relaxed_hash_leaf_salt_order as p1000
import low_term_total2_p1001_p231_phase_shifted_hash_tuple as p1001
import low_term_total2_p1003_p231_context_safe_grouping_replay as p1003


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1005_p231_context_safe_early_stop_order.md"
DEFAULT_P1004 = STATE_DIR / "low_term_total2_p1004_p231_context_safe_forward_11968_11975_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1005_p231_context_safe_early_stop_order_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1005_p231_context_safe_early_stop_order.v1"
DEFAULT_TARGET = "22050.cf1@11731"
VALIDATION_WINDOW = "11968_11975"


OrderKey = Callable[[dict[str, Any]], tuple[Any, ...]]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def selected_ops(row: dict[str, Any]) -> float:
    return float((row.get("source_case") or {}).get("source_ops_over_rho") or 0.0)


def features(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("features") or {}


def case(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("source_case") or {}


def leaf_indices(row: dict[str, Any]) -> list[int]:
    return [int_value(value) for value in features(row).get("unique_leaf_indices") or []]


def leaf_gaps(row: dict[str, Any]) -> list[int]:
    return [int_value(value) for value in features(row).get("leaf_gap_tuple") or []]


def max_leaf_gap(row: dict[str, Any]) -> int:
    gaps = leaf_gaps(row)
    return max(gaps) if gaps else -1


def contains_leaf89(row: dict[str, Any]) -> bool:
    return 89 in set(leaf_indices(row))


def selector_priority(row: dict[str, Any]) -> int:
    selector = str(features(row).get("leaf_selector"))
    return {
        "mode_hash_leaf_total6": 0,
        "mode_hybrid_support_monic_b_total6": 1,
        "mode_low_term_span_total10": 2,
        "mode_low_term_span_total3": 3,
    }.get(selector, 99)


def base_tail(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        tuple(leaf_indices(row)),
        tuple(leaf_gaps(row)),
        p996.row_key_signature(row),
        str(row.get("case_id")),
    )


def order_candidates() -> list[dict[str, Any]]:
    return [
        {
            "name": "p996_public_order",
            "description": "existing P996 public order: top_k, selector priority, transfer, salt gap",
            "key": p996.public_order_key,
        },
        {
            "name": "salt_topk_transfer",
            "description": "salt gap, top-k, transfer index",
            "key": lambda row: (
                int_value(features(row).get("salt_gap")),
                int_value(features(row).get("top_k")),
                int_value(case(row).get("transfer_index")),
                selector_priority(row),
                *base_tail(row),
            ),
        },
        {
            "name": "salt_desc_topk_transfer",
            "description": "descending salt gap, top-k, transfer index",
            "key": lambda row: (
                -int_value(features(row).get("salt_gap")),
                int_value(features(row).get("top_k")),
                int_value(case(row).get("transfer_index")),
                selector_priority(row),
                *base_tail(row),
            ),
        },
        {
            "name": "topk_salt_transfer",
            "description": "top-k, salt gap, transfer index",
            "key": lambda row: (
                int_value(features(row).get("top_k")),
                int_value(features(row).get("salt_gap")),
                int_value(case(row).get("transfer_index")),
                selector_priority(row),
                *base_tail(row),
            ),
        },
        {
            "name": "leaf89_first_gap_desc",
            "description": "leaf89 rows first, then descending max leaf gap, salt gap, top-k",
            "key": lambda row: (
                0 if contains_leaf89(row) else 1,
                -max_leaf_gap(row),
                int_value(features(row).get("salt_gap")),
                int_value(features(row).get("top_k")),
                int_value(case(row).get("transfer_index")),
                *base_tail(row),
            ),
        },
        {
            "name": "hash_first_salt_topk",
            "description": "hash-leaf rows first, then salt gap, top-k",
            "key": lambda row: (
                0 if str(features(row).get("leaf_selector")) == "mode_hash_leaf_total6" else 1,
                int_value(features(row).get("salt_gap")),
                int_value(features(row).get("top_k")),
                int_value(case(row).get("transfer_index")),
                *base_tail(row),
            ),
        },
        {
            "name": "gap_desc_salt_topk",
            "description": "descending max leaf gap, salt gap, top-k",
            "key": lambda row: (
                -max_leaf_gap(row),
                int_value(features(row).get("salt_gap")),
                int_value(features(row).get("top_k")),
                int_value(case(row).get("transfer_index")),
                selector_priority(row),
                *base_tail(row),
            ),
        },
        {
            "name": "gap_asc_salt_topk",
            "description": "ascending max leaf gap, salt gap, top-k",
            "key": lambda row: (
                max_leaf_gap(row),
                int_value(features(row).get("salt_gap")),
                int_value(features(row).get("top_k")),
                int_value(case(row).get("transfer_index")),
                selector_priority(row),
                *base_tail(row),
            ),
        },
    ]


def p998_selected(window: str, targets: str, min_source_rank: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    train_windows = [item.strip() for item in p998.DEFAULT_TRAIN_WINDOWS.split(",") if item.strip()]
    training_examples, train_exists = p998.load_examples(train_windows, targets, min_source_rank)
    chosen, predicate, _scored = p998.choose_rule(training_examples)
    examples = p998.build_window_examples(window, targets, min_source_rank)
    return [row for row in examples if predicate(features(row))], {
        "lane": f"p998_branch_{window}",
        "rule": chosen.get("name"),
        "train_exists": train_exists,
        "window": window,
    }


def p1000_control_selected(targets: str, min_source_rank: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    examples = p999.build_validation_examples(p1000.DEFAULT_CONTROL_WINDOW, targets, min_source_rank)
    return [row for row in examples if p1000.frozen_rule(features(row))], {
        "lane": "p1000_control_relaxed_top7",
        "rule": "mode_hash_leaf_total6_top7_leaves_34_47_56",
        "window": p1000.DEFAULT_CONTROL_WINDOW,
    }


def p1001_control_selected(targets: str, min_source_rank: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    examples = p999.build_validation_examples(p1001.DEFAULT_CONTROL_WINDOW, targets, min_source_rank)
    return [row for row in examples if p1001.shifted_rule(features(row))], {
        "lane": "p1001_control_phase_tuple",
        "rule": "mode_hash_leaf_total6_top12_16_leaves_47_56_84",
        "window": p1001.DEFAULT_CONTROL_WINDOW,
    }


def scalar_valid_groups(selected: list[dict[str, Any]], metadata: dict[str, Any], baseline_rank: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    lane = p1003.analyze_lane(selected, metadata, baseline_rank)
    reconstructed, verifier, built_by_row = p1003.reconstruct_selected(selected)
    all_forms = [form for case_row in reconstructed for form in case_row.get("form_records") or []]
    unique_forms = p1003.p990.unique_forms(all_forms)
    orders = sorted({int_value(form.get("order")) for form in unique_forms if int_value(form.get("order"))})
    order = orders[0] if len(orders) == 1 else 0
    costs = p1003.p990.case_costs(reconstructed)
    safe = p1003.safe_group_summaries(unique_forms, costs, order, verifier, built_by_row, baseline_rank) if unique_forms else []
    valid = [
        group
        for group in safe
        if group.get("mixed_wide_relations_derive_secret")
        and (group.get("context_scalar_validation") or {}).get("context_consistent_scalar_valid")
    ]
    return lane, valid


def selected_case_summary(row: dict[str, Any]) -> dict[str, Any]:
    f = features(row)
    c = case(row)
    return {
        "case_id": row.get("case_id"),
        "label_positive": row.get("label_positive"),
        "leaf_gap_tuple": f.get("leaf_gap_tuple"),
        "leaf_selector": f.get("leaf_selector"),
        "max_leaf_gap": max_leaf_gap(row),
        "row_key_signature": p996.row_key_signature(row),
        "salt_gap": f.get("salt_gap"),
        "source_ops_over_rho": c.get("source_ops_over_rho"),
        "source_public_key_verified": c.get("source_public_key_verified"),
        "source_rank": c.get("source_rank"),
        "top_k": f.get("top_k"),
        "transfer_index": c.get("transfer_index"),
        "unique_leaf_indices": f.get("unique_leaf_indices"),
    }


def first_hit_summary(selected: list[dict[str, Any]], groups: list[dict[str, Any]], order: dict[str, Any]) -> dict[str, Any]:
    valid_groups = []
    for group in groups:
        case_ids = {str(case_id) for case_id in group.get("case_ids") or []}
        if not case_ids:
            continue
        valid_groups.append((case_ids, group))
    ordered = sorted(selected, key=order["key"])
    seen: set[str] = set()
    cumulative = 0.0
    first = None
    for index, row in enumerate(ordered, start=1):
        seen.add(str(row.get("case_id")))
        cumulative += selected_ops(row)
        for case_ids, group in valid_groups:
            if case_ids <= seen:
                first = {
                    "charged_ops_over_rho": round(cumulative, 8),
                    "direct_group_amortized_ops_over_rho": group.get("selected_case_amortized_ops_over_rho"),
                    "derived_secret": group.get("derived_secret"),
                    "first_case_id": row.get("case_id"),
                    "group_case_ids": sorted(case_ids),
                    "group_key": group.get("group_key"),
                    "group_type": group.get("group_type"),
                    "ordered_index": index,
                    "public_fingerprint": group.get("public_fingerprint"),
                    "row_keys": group.get("row_keys"),
                }
                break
        if first:
            break
    return {
        "first_scalar_valid_group": first,
        "first_scalar_valid_group_below_rho": bool(first and first["charged_ops_over_rho"] < 1.0),
        "order_description": order["description"],
        "order_name": order["name"],
        "ordered_case_count": len(ordered),
        "ordered_cases": [selected_case_summary(row) for row in ordered],
        "scalar_valid_group_count": len(valid_groups),
        "total_selected_ops_over_rho": round(sum(selected_ops(row) for row in selected), 8),
    }


def score_order_on_training(order: dict[str, Any], training: list[dict[str, Any]]) -> dict[str, Any]:
    hits = []
    misses = 0
    for lane in training:
        summary = first_hit_summary(lane["selected"], lane["scalar_valid_groups"], order)
        first = summary.get("first_scalar_valid_group")
        if first:
            hits.append(
                {
                    "charged_ops_over_rho": first.get("charged_ops_over_rho"),
                    "lane": lane["metadata"]["lane"],
                    "ordered_index": first.get("ordered_index"),
                }
            )
        else:
            misses += 1
    charges = [float(row["charged_ops_over_rho"]) for row in hits]
    return {
        "below_rho_hit_count": sum(1 for value in charges if value < 1.0),
        "hit_count": len(hits),
        "lane_hits": hits,
        "max_charge": max(charges) if charges else None,
        "mean_charge": round(sum(charges) / len(charges), 8) if charges else None,
        "miss_count": misses,
        "order_description": order["description"],
        "order_name": order["name"],
    }


def choose_order(training: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    orders = order_candidates()
    scored = [score_order_on_training(order, training) for order in orders]
    scored.sort(
        key=lambda row: (
            -int_value(row.get("below_rho_hit_count")),
            -int_value(row.get("hit_count")),
            float(row.get("mean_charge") if row.get("mean_charge") is not None else 10**9),
            float(row.get("max_charge") if row.get("max_charge") is not None else 10**9),
            str(row.get("order_name")),
        )
    )
    by_name = {order["name"]: order for order in orders}
    return by_name[str(scored[0]["order_name"])], scored


def lane_record(selected: list[dict[str, Any]], metadata: dict[str, Any], baseline_rank: int) -> dict[str, Any]:
    analysis, groups = scalar_valid_groups(selected, metadata, baseline_rank)
    return {
        "analysis_summary": analysis.get("summary"),
        "metadata": metadata,
        "scalar_valid_groups": groups,
        "selected": selected,
    }


def compact_group(group: dict[str, Any]) -> dict[str, Any]:
    context = group.get("context_scalar_validation") or {}
    return {
        "case_ids": group.get("case_ids"),
        "derived_secret": group.get("derived_secret"),
        "group_key": group.get("group_key"),
        "group_type": group.get("group_type"),
        "public_fingerprint": group.get("public_fingerprint"),
        "row_keys": group.get("row_keys"),
        "selected_case_amortized_ops_over_rho": group.get("selected_case_amortized_ops_over_rho"),
        "distinct_known_secrets": context.get("distinct_known_secrets"),
    }


def determine_claim(control_pass: bool, validation: dict[str, Any]) -> str:
    if not control_pass:
        return "NEGATIVE_RESULT_P1005_P1004_CONTROL_FAILURE"
    first = validation.get("first_scalar_valid_group")
    if not first:
        return "NEGATIVE_RESULT_P1005_NO_SCALAR_VALID_GROUP_IN_VALIDATION"
    if float(first.get("charged_ops_over_rho") or 10**9) < 1.0:
        return "P1005_CONTEXT_SAFE_EARLY_STOP_BELOW_RHO"
    return "NEGATIVE_RESULT_P1005_TRAINED_PUBLIC_ORDER_ABOVE_RHO"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p1004_payload = load_json(Path(args.p1004))
    control_pass = p1004_payload.get("claim_status") == "P1004_CONTEXT_SAFE_FORWARD_SCALAR_VALID_BELOW_RHO"
    train_specs = [
        p998_selected("11936_11943", args.targets, args.min_source_rank),
        p1000_control_selected(args.targets, args.min_source_rank),
        p1001_control_selected(args.targets, args.min_source_rank),
    ]
    training = [lane_record(selected, metadata, args.baseline_rank) for selected, metadata in train_specs]
    chosen_order, order_scores = choose_order(training)
    validation_selected, validation_metadata = p998_selected(VALIDATION_WINDOW, args.targets, args.min_source_rank)
    validation_record = lane_record(validation_selected, validation_metadata, args.baseline_rank)
    validation_summary = first_hit_summary(validation_record["selected"], validation_record["scalar_valid_groups"], chosen_order)
    all_validation_orders = [
        first_hit_summary(validation_record["selected"], validation_record["scalar_valid_groups"], order)
        for order in order_candidates()
    ]
    all_validation_orders.sort(
        key=lambda row: (
            not row.get("first_scalar_valid_group_below_rho"),
            (row.get("first_scalar_valid_group") or {}).get("charged_ops_over_rho", 10**9),
            row.get("order_name"),
        )
    )
    claim = determine_claim(control_pass, validation_summary)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p1004_source": str(args.p1004),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": sha256_file(Path(args.contract)),
            "p1004_source_sha256": sha256_file(Path(args.p1004)),
            "script_sha256": sha256_file(Path(__file__)),
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1005_") else "NEGATIVE RESULT",
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ORDER-TRAINING BOUNDARY: primary order is chosen only from prior lanes, not validation scalar-valid positions.",
            "PUBLIC-ORDER BOUNDARY: order keys use public row features only.",
            "FULL-ALGORITHM BOUNDARY: below-rho first hit is not yet full relation collection, sparse linear algebra, or target descent.",
        ],
        "method": "p1005_p231_context_safe_early_stop_order",
        "order_search": {
            "all_validation_orders_diagnostic": all_validation_orders,
            "chosen_order": {
                "description": chosen_order["description"],
                "name": chosen_order["name"],
            },
            "training_scores": order_scores,
        },
        "p1004_control": {
            "claim_status": p1004_payload.get("claim_status"),
            "summary": p1004_payload.get("summary"),
        },
        "parameters": {
            "baseline_rank": args.baseline_rank,
            "min_source_rank": args.min_source_rank,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
            "validation_window": VALIDATION_WINDOW,
        },
        "schema": SCHEMA,
        "summary": {
            "chosen_order_name": chosen_order["name"],
            "claim_status": claim,
            "control_pass": control_pass,
            "training_lane_count": len(training),
            "validation_first_scalar_valid_charge": (validation_summary.get("first_scalar_valid_group") or {}).get("charged_ops_over_rho"),
            "validation_first_scalar_valid_index": (validation_summary.get("first_scalar_valid_group") or {}).get("ordered_index"),
            "validation_scalar_valid_group_count": len(validation_record["scalar_valid_groups"]),
            "validation_selected_count": len(validation_record["selected"]),
            "validation_total_selected_ops_over_rho": validation_summary.get("total_selected_ops_over_rho"),
        },
        "training_lanes": [
            {
                "analysis_summary": lane["analysis_summary"],
                "metadata": lane["metadata"],
                "scalar_valid_groups": [compact_group(group) for group in lane["scalar_valid_groups"][:12]],
                "selected_count": len(lane["selected"]),
            }
            for lane in training
        ],
        "validation": {
            "analysis_summary": validation_record["analysis_summary"],
            "first_hit": validation_summary,
            "metadata": validation_metadata,
            "scalar_valid_groups": [compact_group(group) for group in validation_record["scalar_valid_groups"][:16]],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-rank", type=int, default=8, help="Rank baseline for group summaries")
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P1005 contract path")
    parser.add_argument("--min-source-rank", type=int, default=2, help="Minimum source rank for source-positive labels")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--p1004", default=str(DEFAULT_P1004), help="P1004 source JSON")
    parser.add_argument("--targets", default=DEFAULT_TARGET, help="Comma-separated target filter")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    print(
        "claim={claim} order={order} selected={selected} scalar_groups={groups} "
        "first_charge={charge} first_index={index} total={total} out={out}".format(
            claim=payload["claim_status"],
            order=summary["chosen_order_name"],
            selected=summary["validation_selected_count"],
            groups=summary["validation_scalar_valid_group_count"],
            charge=summary["validation_first_scalar_valid_charge"],
            index=summary["validation_first_scalar_valid_index"],
            total=summary["validation_total_selected_ops_over_rho"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
