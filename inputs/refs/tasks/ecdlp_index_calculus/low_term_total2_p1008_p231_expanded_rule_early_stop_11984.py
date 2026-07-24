#!/usr/bin/env python3
"""P1008 early-stop audit for the frozen P1007 expanded-source rule."""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005
import low_term_total2_p1007_p231_expanded_source_policy_compatibility as p1007


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1008_p231_expanded_rule_early_stop_11984.md"
DEFAULT_P1007 = STATE_DIR / "low_term_total2_p1007_p231_expanded_source_policy_compatibility_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1008_p231_expanded_rule_early_stop_11984_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1008_p231_expanded_rule_early_stop_11984.v1"
DEFAULT_TARGET = "22050.cf1@11731"
RULE_NAME = "selector=mode_low_term_support_total5 AND topk=7"
ORDER_TRAIN_WINDOWS = [
    *p1007.TRAIN_WINDOWS,
    p1007.CONTROL_WINDOW,
    p1007.VALIDATION_WINDOW,
]
VALIDATION_WINDOW = "11984_11991"


OrderKey = Callable[[dict[str, Any]], tuple[Any, ...]]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def features(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("features") or {}


def source_case(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("source_case") or {}


def leaf_tuple(row: dict[str, Any]) -> tuple[int, ...]:
    return tuple(int_value(value) for value in features(row).get("unique_leaf_indices") or [])


def selected_ops(row: dict[str, Any]) -> float:
    return float(source_case(row).get("source_ops_over_rho") or 0.0)


def row_key_signature(row: dict[str, Any]) -> str:
    return p1005.p996.row_key_signature(row)


def frozen_rule(row: dict[str, Any]) -> bool:
    return str(features(row).get("leaf_selector")) == "mode_low_term_support_total5" and int_value(
        features(row).get("top_k")
    ) == 7


def build_rows(windows: list[str], targets: str, min_source_rank: int) -> tuple[list[dict[str, Any]], dict[str, bool]]:
    p1007.install_expanded_source_paths()
    out: list[dict[str, Any]] = []
    exists: dict[str, bool] = {}
    for window in windows:
        path = p1007.expanded_source_path(window)
        exists[window] = path.exists()
        if path.exists():
            out.extend(p1007.build_examples(window, targets, min_source_rank))
    return out, exists


def selected_for_windows(windows: list[str], targets: str, min_source_rank: int) -> tuple[list[dict[str, Any]], dict[str, bool]]:
    rows, exists = build_rows(windows, targets, min_source_rank)
    return [row for row in rows if frozen_rule(row)], exists


def order_candidates() -> list[dict[str, Any]]:
    return [
        {
            "description": "source ops/rho ascending, then transfer",
            "key": lambda row: (
                selected_ops(row),
                int_value(source_case(row).get("transfer_index")),
                row_key_signature(row),
                str(row.get("case_id")),
            ),
            "name": "ops_asc_transfer",
        },
        {
            "description": "transfer index ascending, then source ops/rho",
            "key": lambda row: (
                int_value(source_case(row).get("transfer_index")),
                selected_ops(row),
                row_key_signature(row),
                str(row.get("case_id")),
            ),
            "name": "transfer_asc_ops",
        },
        {
            "description": "transfer index descending, then source ops/rho",
            "key": lambda row: (
                -int_value(source_case(row).get("transfer_index")),
                selected_ops(row),
                row_key_signature(row),
                str(row.get("case_id")),
            ),
            "name": "transfer_desc_ops",
        },
        {
            "description": "salt gap ascending, then source ops/rho",
            "key": lambda row: (
                int_value(features(row).get("salt_gap")),
                selected_ops(row),
                int_value(source_case(row).get("transfer_index")),
                row_key_signature(row),
                str(row.get("case_id")),
            ),
            "name": "salt_gap_asc_ops",
        },
        {
            "description": "salt gap descending, then source ops/rho",
            "key": lambda row: (
                -int_value(features(row).get("salt_gap")),
                selected_ops(row),
                int_value(source_case(row).get("transfer_index")),
                row_key_signature(row),
                str(row.get("case_id")),
            ),
            "name": "salt_gap_desc_ops",
        },
        {
            "description": "leaf tuple lexicographic, then source ops/rho",
            "key": lambda row: (
                leaf_tuple(row),
                selected_ops(row),
                int_value(source_case(row).get("transfer_index")),
                row_key_signature(row),
                str(row.get("case_id")),
            ),
            "name": "leaf_tuple_ops",
        },
        {
            "description": "source rank descending, then source ops/rho; diagnostic because rank is source-verifier metadata",
            "diagnostic": True,
            "key": lambda row: (
                -int_value(source_case(row).get("source_rank")),
                selected_ops(row),
                int_value(source_case(row).get("transfer_index")),
                row_key_signature(row),
                str(row.get("case_id")),
            ),
            "name": "diagnostic_rank_desc_ops",
        },
    ]


def scalar_valid_groups(selected: list[dict[str, Any]], metadata: dict[str, Any], baseline_rank: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    return p1005.scalar_valid_groups(selected, metadata, baseline_rank)


def first_hit_summary(selected: list[dict[str, Any]], groups: list[dict[str, Any]], order: dict[str, Any]) -> dict[str, Any]:
    valid_groups = []
    for group in groups:
        case_ids = {str(case_id) for case_id in group.get("case_ids") or []}
        if case_ids:
            valid_groups.append((case_ids, group))
    ordered = sorted(selected, key=order["key"])
    seen: set[str] = set()
    charge = 0.0
    first = None
    for index, row in enumerate(ordered, start=1):
        seen.add(str(row.get("case_id")))
        charge += selected_ops(row)
        for case_ids, group in valid_groups:
            if case_ids <= seen:
                first = {
                    "charged_ops_over_rho": round(charge, 8),
                    "direct_group_amortized_ops_over_rho": group.get("selected_case_amortized_ops_over_rho"),
                    "first_case_id": row.get("case_id"),
                    "group_case_ids": sorted(case_ids),
                    "group_key": group.get("group_key"),
                    "group_type": group.get("group_type"),
                    "ordered_index": index,
                    "public_fingerprint": group.get("public_fingerprint"),
                    "row_keys": group.get("row_keys"),
                    "derived_secret": group.get("derived_secret"),
                }
                break
        if first:
            break
    return {
        "diagnostic_order": bool(order.get("diagnostic")),
        "first_scalar_valid_group": first,
        "first_scalar_valid_group_below_rho": bool(first and float(first["charged_ops_over_rho"]) < 1.0),
        "order_description": order["description"],
        "order_name": order["name"],
        "ordered_case_count": len(ordered),
        "total_selected_ops_over_rho": round(sum(selected_ops(row) for row in selected), 8),
    }


def score_order(order: dict[str, Any], lane_records: list[dict[str, Any]]) -> dict[str, Any]:
    hits = []
    misses = 0
    for lane in lane_records:
        summary = first_hit_summary(lane["selected"], lane["groups"], order)
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
        "diagnostic_order": bool(order.get("diagnostic")),
        "hit_count": len(hits),
        "lane_hits": hits,
        "max_charge": max(charges) if charges else None,
        "mean_charge": round(sum(charges) / len(charges), 8) if charges else None,
        "miss_count": misses,
        "order_description": order["description"],
        "order_name": order["name"],
    }


def choose_order(lane_records: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    orders = order_candidates()
    scored = [score_order(order, lane_records) for order in orders]
    scored.sort(
        key=lambda row: (
            bool(row.get("diagnostic_order")),
            -int_value(row.get("below_rho_hit_count")),
            -int_value(row.get("hit_count")),
            float(row.get("mean_charge") if row.get("mean_charge") is not None else 10**9),
            float(row.get("max_charge") if row.get("max_charge") is not None else 10**9),
            str(row.get("order_name")),
        )
    )
    by_name = {order["name"]: order for order in orders}
    return by_name[str(scored[0]["order_name"])], scored


def selected_case_summary(row: dict[str, Any]) -> dict[str, Any]:
    f = features(row)
    c = source_case(row)
    return {
        "case_id": row.get("case_id"),
        "label_positive": row.get("label_positive"),
        "source_ops_over_rho": c.get("source_ops_over_rho"),
        "source_public_key_verified": c.get("source_public_key_verified"),
        "source_rank": c.get("source_rank"),
        "top_k": f.get("top_k"),
        "transfer_index": c.get("transfer_index"),
        "unique_leaf_indices": f.get("unique_leaf_indices"),
        "window": row.get("window"),
    }


def lane_record(name: str, windows: list[str], targets: str, min_source_rank: int, baseline_rank: int) -> dict[str, Any]:
    selected, exists = selected_for_windows(windows, targets, min_source_rank)
    analysis, groups = scalar_valid_groups(selected, {"lane": name, "rule": RULE_NAME}, baseline_rank)
    return {
        "analysis_summary": analysis.get("summary"),
        "exists": exists,
        "groups": groups,
        "metadata": {"lane": name, "rule": RULE_NAME, "windows": windows},
        "scalar_valid_groups": [p1005.compact_group(group) for group in groups[:12]],
        "selected": selected,
        "selected_cases": [selected_case_summary(row) for row in selected],
    }


def determine_claim(control_pass: bool, validation: dict[str, Any], chosen_validation: dict[str, Any]) -> str:
    if not control_pass:
        return "NEGATIVE_RESULT_P1008_P1007_CONTROL_FAILURE"
    summary = validation.get("analysis_summary") or {}
    if int_value(summary.get("selected_count")) == 0:
        return "NEGATIVE_RESULT_P1008_FROZEN_RULE_SELECTS_NO_HOLDOUT_ROWS"
    if int_value(summary.get("context_safe_scalar_valid_group_count")) == 0:
        return "NEGATIVE_RESULT_P1008_FROZEN_RULE_NO_HOLDOUT_SCALAR_VALID_GROUP"
    first = chosen_validation.get("first_scalar_valid_group")
    if first and float(first.get("charged_ops_over_rho") or 10**9) < 1.0:
        return "P1008_EXPANDED_RULE_EARLY_STOP_BELOW_RHO"
    if first:
        return "NEGATIVE_RESULT_P1008_EXPANDED_RULE_EARLY_STOP_ABOVE_RHO"
    return "NEGATIVE_RESULT_P1008_EXPANDED_RULE_NO_ORDER_HIT"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p1007_payload = load_json(Path(args.p1007))
    control_pass = p1007_payload.get("claim_status") == "P1007_EXPANDED_SOURCE_POLICY_CONTEXT_SAFE_BELOW_RHO"
    train_record = lane_record("order_train_expanded_prior", ORDER_TRAIN_WINDOWS, args.targets, args.min_source_rank, args.baseline_rank)
    control_record = lane_record("positive_control_11976_11983", [p1007.VALIDATION_WINDOW], args.targets, args.min_source_rank, args.baseline_rank)
    validation_record = lane_record("validation_11984_11991", [VALIDATION_WINDOW], args.targets, args.min_source_rank, args.baseline_rank)
    chosen_order, order_scores = choose_order([train_record, control_record])
    validation_first = first_hit_summary(validation_record["selected"], validation_record["groups"], chosen_order)
    all_validation_orders = [
        first_hit_summary(validation_record["selected"], validation_record["groups"], order)
        for order in order_candidates()
    ]
    all_validation_orders.sort(
        key=lambda row: (
            not row.get("first_scalar_valid_group_below_rho"),
            (row.get("first_scalar_valid_group") or {}).get("charged_ops_over_rho", 10**9),
            row.get("order_name"),
        )
    )
    claim = determine_claim(control_pass, validation_record, validation_first)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p1007_source": str(args.p1007),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": p1005.sha256_file(Path(args.contract)),
            "p1007_source_sha256": p1005.sha256_file(Path(args.p1007)),
            "script_sha256": p1005.sha256_file(Path(__file__)),
            "validation_source_sha256": p1005.sha256_file(p1007.expanded_source_path(VALIDATION_WINDOW)),
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1008_") else "NEGATIVE RESULT",
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "RULE-FROZEN BOUNDARY: selector is fixed from P1007 before scoring 11984_11991.",
            "ORDER-TRAINING BOUNDARY: primary order is chosen from prior lanes only.",
            "EARLY-STOP BOUNDARY: if no scalar-valid group exists, ordering is not exercised.",
            "FULL-ALGORITHM BOUNDARY: this is not relation collection, sparse linear algebra, target descent, or cryptographic-size evidence.",
        ],
        "lanes": {
            "control": {
                **{key: value for key, value in control_record.items() if key not in {"groups", "selected"}},
                "first_hit_chosen_order": first_hit_summary(control_record["selected"], control_record["groups"], chosen_order),
            },
            "train": {
                **{key: value for key, value in train_record.items() if key not in {"groups", "selected"}},
                "first_hit_chosen_order": first_hit_summary(train_record["selected"], train_record["groups"], chosen_order),
            },
            "validation": {
                **{key: value for key, value in validation_record.items() if key not in {"groups", "selected"}},
                "all_order_diagnostic": all_validation_orders,
                "first_hit_chosen_order": validation_first,
            },
        },
        "method": "p1008_p231_expanded_rule_early_stop_11984",
        "order_search": {
            "chosen_order": {
                "description": chosen_order["description"],
                "diagnostic_order": bool(chosen_order.get("diagnostic")),
                "name": chosen_order["name"],
            },
            "training_scores": order_scores,
        },
        "p1007_control": {
            "claim_status": p1007_payload.get("claim_status"),
            "summary": p1007_payload.get("summary"),
        },
        "parameters": {
            "baseline_rank": args.baseline_rank,
            "min_source_rank": args.min_source_rank,
            "order_train_windows": ORDER_TRAIN_WINDOWS,
            "rule": RULE_NAME,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
            "validation_window": VALIDATION_WINDOW,
        },
        "schema": SCHEMA,
        "source": {
            "control": p1007.source_summary(p1007.VALIDATION_WINDOW),
            "validation": p1007.source_summary(VALIDATION_WINDOW),
        },
        "summary": {
            "chosen_order_name": chosen_order["name"],
            "claim_status": claim,
            "control_context_safe_scalar_valid_group_count": (control_record.get("analysis_summary") or {}).get(
                "context_safe_scalar_valid_group_count"
            ),
            "control_selected_count": (control_record.get("analysis_summary") or {}).get("selected_count"),
            "control_pass": control_pass,
            "validation_best_scalar_valid_amortized_ops_over_rho": (validation_record.get("analysis_summary") or {}).get(
                "scalar_valid_best_amortized_ops_over_rho"
            ),
            "validation_chosen_first_charge": (validation_first.get("first_scalar_valid_group") or {}).get(
                "charged_ops_over_rho"
            ),
            "validation_context_safe_scalar_valid_group_count": (validation_record.get("analysis_summary") or {}).get(
                "context_safe_scalar_valid_group_count"
            ),
            "validation_selected_count": (validation_record.get("analysis_summary") or {}).get("selected_count"),
            "validation_selected_source_positive_count": (validation_record.get("analysis_summary") or {}).get(
                "selected_source_positive_count"
            ),
            "validation_total_selected_ops_over_rho": (validation_record.get("analysis_summary") or {}).get(
                "selected_direct_sum_ops_over_rho"
            ),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-rank", type=int, default=8, help="Rank baseline for group summaries")
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P1008 contract path")
    parser.add_argument("--min-source-rank", type=int, default=2, help="Minimum source rank for source-positive labels")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--p1007", default=str(DEFAULT_P1007), help="P1007 source JSON")
    parser.add_argument("--targets", default=DEFAULT_TARGET, help="Comma-separated target filter")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    print(
        "claim={claim} order={order} control_selected={control_selected} control_groups={control_groups} "
        "validation_selected={validation_selected} validation_pos={validation_pos} validation_groups={validation_groups} "
        "validation_best={validation_best} validation_first={validation_first} out={out}".format(
            claim=payload["claim_status"],
            order=summary["chosen_order_name"],
            control_selected=summary["control_selected_count"],
            control_groups=summary["control_context_safe_scalar_valid_group_count"],
            validation_selected=summary["validation_selected_count"],
            validation_pos=summary["validation_selected_source_positive_count"],
            validation_groups=summary["validation_context_safe_scalar_valid_group_count"],
            validation_best=summary["validation_best_scalar_valid_amortized_ops_over_rho"],
            validation_first=summary["validation_chosen_first_charge"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
