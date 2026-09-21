#!/usr/bin/env python3
"""P1073 public ordering compression for P1072 top-k7 stage 2."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p1055_p231_source_charged_rank_audit as p1055
import low_term_total2_p1063_p231_free_column_source_construction as p1063
import low_term_total2_p1069_p231_forward_transfer_descent_accounting as p1069
import low_term_total2_p1071_p231_remaining_column_source_expansion as p1071
import low_term_total2_p1072_p231_topk7_split_validation as p1072


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1073_p231_topk7_order_compression.md"
DEFAULT_P1059 = STATE_DIR / "low_term_total2_p1059_p231_rowkey_prefix_shared_source_probe.json"
DEFAULT_P1067 = STATE_DIR / "low_term_total2_p1067_p231_post_carrier_source_refresh_probe.json"
DEFAULT_P1069 = STATE_DIR / "low_term_total2_p1069_p231_forward_transfer_descent_accounting_probe.json"
DEFAULT_P1072 = STATE_DIR / "low_term_total2_p1072_p231_topk7_split_validation_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1073_p231_topk7_order_compression_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1073_p231_topk7_order_compression.v1"


PolicyKey = Callable[[dict[str, Any]], tuple[Any, ...]]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def salts(ref: dict[str, Any]) -> list[int]:
    return p1055.extract_salts(ref.get("row_keys") or [])


def salt_sum(ref: dict[str, Any]) -> int:
    values = salts(ref)
    return sum(values) if values else -1


def salt_min(ref: dict[str, Any]) -> int:
    values = salts(ref)
    return min(values) if values else 10**9


def salt_max(ref: dict[str, Any]) -> int:
    values = salts(ref)
    return max(values) if values else -1


def salt_span(ref: dict[str, Any]) -> int:
    values = salts(ref)
    return max(values) - min(values) if values else -1


def direct_ops(ref: dict[str, Any]) -> float:
    return p1055.float_value(ref.get("direct_ops_over_rho")) or float("inf")


def support(ref: dict[str, Any]) -> set[int]:
    return {p1055.int_value(item) for item in ref.get("selected_term_support") or []}


def priority_count(ref: dict[str, Any]) -> int:
    return len(ref.get("priority_hits") or [])


def base_key(ref: dict[str, Any]) -> tuple[Any, ...]:
    return (ref["window_start"], ref["transfer_index"], ref["case_id"])


def policy_catalog() -> list[dict[str, Any]]:
    return [
        {"name": "chronological", "key": lambda ref: base_key(ref), "direct_ops_order": False},
        {"name": "latest_transfer", "key": lambda ref: (-ref["transfer_index"], ref["case_id"]), "direct_ops_order": False},
        {"name": "low_direct_ops", "key": lambda ref: (direct_ops(ref),) + base_key(ref), "direct_ops_order": True},
        {"name": "high_direct_ops", "key": lambda ref: (-direct_ops(ref),) + base_key(ref), "direct_ops_order": True},
        {"name": "high_salt_sum", "key": lambda ref: (-salt_sum(ref),) + base_key(ref), "direct_ops_order": False},
        {"name": "low_salt_sum", "key": lambda ref: (salt_sum(ref),) + base_key(ref), "direct_ops_order": False},
        {"name": "high_salt_max", "key": lambda ref: (-salt_max(ref),) + base_key(ref), "direct_ops_order": False},
        {"name": "low_salt_min", "key": lambda ref: (salt_min(ref),) + base_key(ref), "direct_ops_order": False},
        {"name": "high_salt_span", "key": lambda ref: (-salt_span(ref),) + base_key(ref), "direct_ops_order": False},
        {"name": "low_salt_span", "key": lambda ref: (salt_span(ref),) + base_key(ref), "direct_ops_order": False},
        {"name": "priority_count_desc", "key": lambda ref: (-priority_count(ref),) + base_key(ref), "direct_ops_order": False},
        {"name": "support_size_asc", "key": lambda ref: (len(support(ref)),) + base_key(ref), "direct_ops_order": False},
        {"name": "support_size_desc", "key": lambda ref: (-len(support(ref)),) + base_key(ref), "direct_ops_order": False},
        {"name": "support_has_15_then_low_ops", "key": lambda ref: (15 not in support(ref), direct_ops(ref)) + base_key(ref), "direct_ops_order": True},
        {"name": "support_has_14_15_then_low_ops", "key": lambda ref: (not ({14, 15} <= support(ref)), direct_ops(ref)) + base_key(ref), "direct_ops_order": True},
        {"name": "high_salt_max_then_low_ops", "key": lambda ref: (-salt_max(ref), direct_ops(ref)) + base_key(ref), "direct_ops_order": True},
        {"name": "high_salt_sum_then_low_ops", "key": lambda ref: (-salt_sum(ref), direct_ops(ref)) + base_key(ref), "direct_ops_order": True},
        {"name": "low_support_high_salt_sum", "key": lambda ref: (len(support(ref)), -salt_sum(ref)) + base_key(ref), "direct_ops_order": False},
    ]


def build_context(args: argparse.Namespace) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, Any],
    dict[str, dict[str, Any]],
    dict[Path, list[dict[str, Any]]],
    dict[str, Any],
    list[Path],
    list[Path],
]:
    p1067_payload = load_json(args.p1067)
    p1069_payload = load_json(args.p1069)
    train_ref = p1071.ref_from_existing((p1067_payload.get("summary") or {})["best_single_rank_case"], args, args.source)
    promotion_ref = p1071.ref_from_existing((p1069_payload.get("parameters") or {})["promotion_case"], args, args.source)
    promotion_window_end = p1069.window_end(promotion_ref)
    factor_rows, factor_paths = p1071.load_factor_rows(args)
    expanded_refs, inventory, selected_paths = p1071.load_expanded_refs(args, factor_rows, promotion_window_end)
    selected_rowkey = p1063.selected_rowkey_from_p1059(args.p1059)
    anchor_ref = {
        "case_id": f"{args.promoted_selector}:{args.promoted_top_k}:18464_18471:18465:{'|'.join(selected_rowkey)}",
        "direct_ops_over_rho": 0.83211679,
        "direct_public_key_verified": True,
        "priority_hits": [6, 15],
        "row_keys": list(selected_rowkey),
        "selected_term_support": [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        "selector": args.promoted_selector,
        "source": args.source,
        "target": args.target,
        "top_k": args.promoted_top_k,
        "transfer_index": 18465,
        "window": "18464_18471",
        "window_end": 18471,
        "window_start": 18464,
    }
    promoted_refs = [anchor_ref, train_ref, promotion_ref]
    family_refs = [
        ref
        for ref in expanded_refs
        if ref["selector"] == args.selector and p1055.int_value(ref.get("top_k"), -1) == args.top_k
    ]
    family_refs.sort(key=base_key)
    cache: dict[Path, list[dict[str, Any]]] = {}
    promoted_packet = p1071.evaluate_refs(promoted_refs, factor_rows, cache, args)
    stage1_ref = None
    for ref in family_refs:
        result = p1071.evaluate_refs(promoted_refs + [ref], factor_rows, cache, args)
        stats = p1063.marginal_stats(promoted_packet, result, [int(item) for item in args.priority_columns.split(",") if item.strip()])
        if (
            (stats["marginal_rank_gain"] > 0 or stats["removed_free_columns"])
            and stats["marginal_charge_over_rho"] < 1.0
        ):
            stage1_ref = ref
            break
    if stage1_ref is None:
        raise ValueError("no below-rho stage1 carrier found for frozen family")
    stage1_refs = promoted_refs + [stage1_ref]
    stage1_packet = p1071.evaluate_refs(stage1_refs, factor_rows, cache, args)
    validation_refs = [ref for ref in family_refs if ref["window_start"] > p1069.window_end(stage1_ref)]
    return stage1_refs, validation_refs, stage1_packet, factor_rows, cache, inventory, factor_paths, selected_paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--p1059", type=Path, default=DEFAULT_P1059)
    parser.add_argument("--p1067", type=Path, default=STATE_DIR / "low_term_total2_p1067_p231_post_carrier_source_refresh_probe.json")
    parser.add_argument("--p1069", type=Path, default=DEFAULT_P1069)
    parser.add_argument("--p1072", type=Path, default=DEFAULT_P1072)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--factor-glob", default=p1055.DEFAULT_FACTOR_GLOB)
    parser.add_argument("--selected-glob", default=p1055.DEFAULT_SELECTED_GLOB)
    parser.add_argument("--order", type=int, default=11779)
    parser.add_argument("--column", type=int, default=15)
    parser.add_argument("--priority-columns", default="6,7,10,14,15")
    parser.add_argument("--target-column", type=int, default=15)
    parser.add_argument("--target", default="22050.cf1@11731")
    parser.add_argument("--source", default="direct_source")
    parser.add_argument("--selector", default="mode_low_term_support_total5")
    parser.add_argument("--top-k", type=int, default=7)
    parser.add_argument("--promoted-selector", default="mode_low_term_support_total5")
    parser.add_argument("--promoted-top-k", type=int, default=16)
    parser.add_argument("--train-min-start", type=int, default=10000)
    parser.add_argument("--train-max-start", type=int, default=11887)
    parser.add_argument("--gap-min-start", type=int, default=11888)
    parser.add_argument("--gap-max-start", type=int, default=11983)
    parser.add_argument("--forward-min-start", type=int, default=12200)
    args = parser.parse_args()

    priority_columns = [int(item) for item in args.priority_columns.split(",") if item.strip()]
    p1072_payload = load_json(args.p1072)
    stage1_refs, validation_refs, stage1_packet, factor_rows, cache, inventory, factor_paths, selected_paths = build_context(args)

    policy_results = []
    for policy in policy_catalog():
        ordered = sorted(validation_refs, key=policy["key"])
        result = p1072.prefix_scan(
            ordered,
            stage1_refs,
            stage1_packet,
            factor_rows,
            cache,
            args,
            priority_columns,
            args.target_column,
        )
        first = result.get("first_target_column_prefix")
        policy_results.append(
            {
                "direct_ops_order": policy["direct_ops_order"],
                "first_target_column_prefix": first,
                "ordered_case_ids": result["ordered_case_ids"][:12],
                "ordered_case_ids_truncated": len(result["ordered_case_ids"]) > 12,
                "policy": policy["name"],
                "selected_case_count": len(ordered),
            }
        )

    winners = [
        item
        for item in policy_results
        if item.get("first_target_column_prefix")
        and (p1055.float_value(item["first_target_column_prefix"].get("marginal_charge_over_rho")) or float("inf")) < 1.0
    ]
    winners.sort(
        key=lambda item: (
            item["first_target_column_prefix"]["marginal_charge_over_rho"],
            item["first_target_column_prefix"]["length"],
            item["policy"],
        )
    )
    weak = [item for item in policy_results if item.get("first_target_column_prefix")]
    weak.sort(
        key=lambda item: (
            p1055.float_value(item["first_target_column_prefix"].get("marginal_charge_over_rho")) or float("inf"),
            item["first_target_column_prefix"]["length"],
            item["policy"],
        )
    )
    if winners:
        claim_status = "POSITIVE_SIGNAL_P1073_TOPK7_ORDER_COMPRESSES_COLUMN15_BELOW_RHO"
    else:
        claim_status = "NEGATIVE_RESULT_P1073_NO_PUBLIC_ORDER_BELOW_RHO"

    payload = {
        "artifact_hashes": {
            "contract": p1069.sha256_file(args.contract) if args.contract.exists() else None,
            "factor_artifact_count": len(factor_paths),
            "factor_artifact_digest": p1069.digest_paths(factor_paths),
            "p1059": p1069.sha256_file(args.p1059) if args.p1059.exists() else None,
            "p1067": p1069.sha256_file(args.p1067) if args.p1067.exists() else None,
            "p1069": p1069.sha256_file(args.p1069) if args.p1069.exists() else None,
            "p1072": p1069.sha256_file(args.p1072) if args.p1072.exists() else None,
            "script": p1069.sha256_file(Path(__file__)),
            "selected_artifact_count": len(selected_paths),
            "selected_artifact_digest": p1069.digest_paths(selected_paths),
        },
        "artifacts": {
            "contract": str(args.contract),
            "p1059": str(args.p1059),
            "p1067": str(args.p1067),
            "p1069": str(args.p1069),
            "p1072": str(args.p1072),
            "script": str(Path(__file__)),
        },
        "claim_status": claim_status,
        "claim_taxonomy": [
            "TOY-EVIDENCE",
            "MODEL-BOUND",
            "POLICY-CATALOG",
            "SINGLE-TARGET",
            "POLLARD-RHO-BOUNDARY",
            "DIRECT-OPS-CAVEAT",
        ],
        "expanded_source_inventory": inventory,
        "honesty_boundary": {
            "cryptographic_scale_unproved": True,
            "fresh_target_artifacts_available": bool(inventory["fresh_target_available_in_selected_source_family"]),
            "not_a_complete_index_calculus_algorithm": True,
            "not_a_deployed_curve_break": True,
            "policy_catalog_not_exhaustive": True,
            "target_descent_closed": False,
        },
        "parameters": {
            "family_selector": args.selector,
            "family_top_k": args.top_k,
            "policy_count": len(policy_results),
            "source": args.source,
            "target": args.target,
            "target_column": args.target_column,
        },
        "policy_results": policy_results,
        "record_counts": {
            "policy_count": len(policy_results),
            "validation_case_count": len(validation_refs),
            "winner_count": len(winners),
            "weak_policy_count": len(weak),
        },
        "schema": SCHEMA,
        "strict_success": bool(winners),
        "summary": {
            "best_policy": winners[0] if winners else None,
            "best_weak_policy": weak[0] if weak else None,
            "claim_status": claim_status,
            "fresh_target_artifacts_available": inventory["fresh_target_available_in_selected_source_family"],
            "p1072_chronological_first_target": (p1072_payload.get("summary") or {}).get("first_stage2_target_column_prefix"),
            "policy_count": len(policy_results),
            "strict_success": bool(winners),
            "validation_case_count": len(validation_refs),
            "winner_count": len(winners),
        },
        "timestamp_utc": p1071.now_iso(),
    }
    write_json(args.out, payload)
    print(
        "claim={claim} success={success} winners={winners} best={best} validation_cases={cases} out={out}".format(
            claim=claim_status,
            success=bool(winners),
            winners=len(winners),
            best=(winners[0]["policy"] if winners else None),
            cases=len(validation_refs),
            out=args.out,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
