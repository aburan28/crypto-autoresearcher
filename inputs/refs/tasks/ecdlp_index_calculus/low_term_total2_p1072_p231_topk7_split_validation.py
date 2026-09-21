#!/usr/bin/env python3
"""P1072 chronological split validation for the P1071 top-k7 family."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import low_term_total2_p1055_p231_source_charged_rank_audit as p1055
import low_term_total2_p1063_p231_free_column_source_construction as p1063
import low_term_total2_p1069_p231_forward_transfer_descent_accounting as p1069
import low_term_total2_p1071_p231_remaining_column_source_expansion as p1071


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1072_p231_topk7_split_validation.md"
DEFAULT_P1059 = STATE_DIR / "low_term_total2_p1059_p231_rowkey_prefix_shared_source_probe.json"
DEFAULT_P1067 = STATE_DIR / "low_term_total2_p1067_p231_post_carrier_source_refresh_probe.json"
DEFAULT_P1069 = STATE_DIR / "low_term_total2_p1069_p231_forward_transfer_descent_accounting_probe.json"
DEFAULT_P1071 = STATE_DIR / "low_term_total2_p1071_p231_remaining_column_source_expansion_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1072_p231_topk7_split_validation_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1072_p231_topk7_split_validation.v1"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def compact_prefix(prefix: dict[str, Any] | None) -> dict[str, Any] | None:
    if not prefix:
        return None
    return {
        "last_case_id": prefix.get("last_case_id"),
        "length": prefix.get("length"),
        "marginal_charge_over_rho": prefix.get("marginal_charge_over_rho"),
        "marginal_rank_gain": prefix.get("marginal_rank_gain"),
        "removed_free_columns": prefix.get("removed_free_columns") or [],
        "union_free_columns": prefix.get("union_free_columns") or [],
    }


def stage_ref_summary(ref: dict[str, Any] | None, stats: dict[str, Any] | None = None) -> dict[str, Any] | None:
    if not ref:
        return None
    payload = {
        "case_id": ref.get("case_id"),
        "direct_ops_over_rho": ref.get("direct_ops_over_rho"),
        "direct_public_key_verified": ref.get("direct_public_key_verified"),
        "priority_hits": ref.get("priority_hits") or [],
        "row_keys": ref.get("row_keys") or [],
        "selector": ref.get("selector"),
        "top_k": ref.get("top_k"),
        "transfer_index": ref.get("transfer_index"),
        "window": ref.get("window"),
        "window_start": ref.get("window_start"),
    }
    if stats:
        payload.update(
            {
                "marginal_charge_over_rho": stats.get("marginal_charge_over_rho"),
                "marginal_rank_gain": stats.get("marginal_rank_gain"),
                "removed_free_columns": stats.get("removed_free_columns") or [],
                "union_free_columns": stats.get("union_free_columns") or [],
            }
        )
    return payload


def prefix_scan(
    refs: list[dict[str, Any]],
    baseline_refs: list[dict[str, Any]],
    baseline_packet: dict[str, Any],
    factor_rows: dict[str, dict[str, Any]],
    cache: dict[Path, list[dict[str, Any]]],
    args: argparse.Namespace,
    priority_columns: list[int],
    target_column: int,
) -> dict[str, Any]:
    first_rank = None
    first_target = None
    checkpoints = []
    for length in range(1, len(refs) + 1):
        prefix = refs[:length]
        result = p1071.evaluate_refs(baseline_refs + prefix, factor_rows, cache, args)
        stats = p1063.marginal_stats(baseline_packet, result, priority_columns)
        checkpoint = {
            "last_case_id": prefix[-1]["case_id"],
            "length": length,
            "marginal_charge_over_rho": stats["marginal_charge_over_rho"],
            "marginal_rank_gain": stats["marginal_rank_gain"],
            "removed_free_columns": stats["removed_free_columns"],
            "union_free_columns": stats["union_free_columns"],
        }
        if stats["marginal_rank_gain"] > 0 and first_rank is None:
            first_rank = checkpoint
        if target_column in stats["removed_free_columns"] and first_target is None:
            first_target = checkpoint
        if stats["marginal_rank_gain"] > 0 or target_column in stats["removed_free_columns"] or length in (1, len(refs)):
            checkpoints.append(checkpoint)
    final = p1071.evaluate_refs(baseline_refs + refs, factor_rows, cache, args)
    final_stats = p1063.marginal_stats(baseline_packet, final, priority_columns)
    return {
        "checkpoints": checkpoints,
        "final": p1071.compact_result(final),
        "final_stats": final_stats,
        "first_rank_gain_prefix": compact_prefix(first_rank),
        "first_target_column_prefix": compact_prefix(first_target),
        "ordered_case_ids": [ref["case_id"] for ref in refs],
        "selected_case_count": len(refs),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--p1059", type=Path, default=DEFAULT_P1059)
    parser.add_argument("--p1067", type=Path, default=DEFAULT_P1067)
    parser.add_argument("--p1069", type=Path, default=DEFAULT_P1069)
    parser.add_argument("--p1071", type=Path, default=DEFAULT_P1071)
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
    p1067_payload = load_json(args.p1067)
    p1069_payload = load_json(args.p1069)
    p1071_payload = load_json(args.p1071)
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
    family_refs.sort(key=lambda ref: (ref["window_start"], ref["transfer_index"], ref["case_id"]))
    cache: dict[Path, list[dict[str, Any]]] = {}
    promoted_packet = p1071.evaluate_refs(promoted_refs, factor_rows, cache, args)

    stage1_ref = None
    stage1_stats = None
    stage1_candidates = []
    for ref in family_refs:
        result = p1071.evaluate_refs(promoted_refs + [ref], factor_rows, cache, args)
        stats = p1063.marginal_stats(promoted_packet, result, priority_columns)
        if (
            (stats["marginal_rank_gain"] > 0 or stats["removed_free_columns"])
            and stats["marginal_charge_over_rho"] < 1.0
        ):
            stage1_candidates.append((ref, stats))
            if stage1_ref is None:
                stage1_ref = ref
                stage1_stats = stats
    stage1_refs = promoted_refs + ([stage1_ref] if stage1_ref else [])
    stage1_packet = p1071.evaluate_refs(stage1_refs, factor_rows, cache, args)
    validation_refs = []
    if stage1_ref:
        validation_refs = [ref for ref in family_refs if ref["window_start"] > p1069.window_end(stage1_ref)]
    validation = prefix_scan(
        validation_refs,
        stage1_refs,
        stage1_packet,
        factor_rows,
        cache,
        args,
        priority_columns,
        args.target_column,
    )
    first_rank = validation.get("first_rank_gain_prefix")
    first_target = validation.get("first_target_column_prefix")
    below_rho_success = bool(
        (
            first_target
            and (p1055.float_value(first_target.get("marginal_charge_over_rho")) or float("inf")) < 1.0
        )
        or (
            first_rank
            and (p1055.float_value(first_rank.get("marginal_charge_over_rho")) or float("inf")) < 1.0
        )
    )
    weak_success = bool(
        (validation.get("final_stats") or {}).get("marginal_rank_gain", 0) > 0
        or (validation.get("final_stats") or {}).get("removed_free_columns")
    )
    if below_rho_success:
        claim_status = "POSITIVE_SIGNAL_P1072_TOPK7_STAGE2_BELOW_RHO"
    elif weak_success:
        claim_status = "OBSERVATION_P1072_TOPK7_STAGE2_EXISTS_ABOVE_RHO"
    else:
        claim_status = "NEGATIVE_RESULT_P1072_TOPK7_STAGE2_NO_CHRONOLOGICAL_DIRECTION"

    payload = {
        "artifact_hashes": {
            "contract": p1069.sha256_file(args.contract) if args.contract.exists() else None,
            "factor_artifact_count": len(factor_paths),
            "factor_artifact_digest": p1069.digest_paths(factor_paths),
            "p1059": p1069.sha256_file(args.p1059) if args.p1059.exists() else None,
            "p1067": p1069.sha256_file(args.p1067) if args.p1067.exists() else None,
            "p1069": p1069.sha256_file(args.p1069) if args.p1069.exists() else None,
            "p1071": p1069.sha256_file(args.p1071) if args.p1071.exists() else None,
            "script": p1069.sha256_file(Path(__file__)),
            "selected_artifact_count": len(selected_paths),
            "selected_artifact_digest": p1069.digest_paths(selected_paths),
        },
        "artifacts": {
            "contract": str(args.contract),
            "p1059": str(args.p1059),
            "p1067": str(args.p1067),
            "p1069": str(args.p1069),
            "p1071": str(args.p1071),
            "script": str(Path(__file__)),
        },
        "claim_status": claim_status,
        "claim_taxonomy": [
            "TOY-EVIDENCE",
            "MODEL-BOUND",
            "CHRONOLOGICAL-SPLIT",
            "SINGLE-TARGET",
            "POLLARD-RHO-BOUNDARY",
            "TARGET-DESCENT-BOUNDARY",
        ],
        "controls": {
            "promoted_packet": p1071.compact_result(promoted_packet),
            "p1071_summary": p1071_payload.get("summary"),
            "stage1_packet": p1071.compact_result(stage1_packet),
            "validation": validation,
        },
        "expanded_source_inventory": inventory,
        "honesty_boundary": {
            "cryptographic_scale_unproved": True,
            "fresh_target_artifacts_available": bool(inventory["fresh_target_available_in_selected_source_family"]),
            "not_a_complete_index_calculus_algorithm": True,
            "not_a_deployed_curve_break": True,
            "single_target_artifact_family": True,
            "target_descent_closed": len((validation.get("final_stats") or {}).get("union_free_columns") or []) == 0,
        },
        "parameters": {
            "family_selector": args.selector,
            "family_top_k": args.top_k,
            "order": args.order,
            "priority_columns": priority_columns,
            "promoted_refs": promoted_refs,
            "source": args.source,
            "stage1_ref": stage_ref_summary(stage1_ref, stage1_stats),
            "target": args.target,
            "target_column": args.target_column,
        },
        "record_counts": {
            "family_case_count": len(family_refs),
            "family_window_count": len({ref["window"] for ref in family_refs}),
            "stage1_below_rho_candidate_count": len(stage1_candidates),
            "validation_case_count": len(validation_refs),
            "validation_window_count": len({ref["window"] for ref in validation_refs}),
        },
        "schema": SCHEMA,
        "strict_success": below_rho_success,
        "summary": {
            "claim_status": claim_status,
            "family_case_count": len(family_refs),
            "family_selector": args.selector,
            "family_top_k": args.top_k,
            "first_stage2_rank_prefix": first_rank,
            "first_stage2_target_column_prefix": first_target,
            "fresh_target_artifacts_available": inventory["fresh_target_available_in_selected_source_family"],
            "stage1": stage_ref_summary(stage1_ref, stage1_stats),
            "stage1_below_rho_candidate_count": len(stage1_candidates),
            "strict_success": below_rho_success,
            "validation_case_count": len(validation_refs),
            "validation_final_stats": validation.get("final_stats"),
            "weak_success": weak_success,
        },
        "timestamp_utc": p1071.now_iso(),
    }
    write_json(args.out, payload)
    print(
        "claim={claim} strict_success={success} weak_success={weak} stage1={stage1} "
        "validation_cases={cases} first_target={first_target} final_rank={rank} final_removed={removed} out={out}".format(
            claim=claim_status,
            success=below_rho_success,
            weak=weak_success,
            stage1=(stage1_ref or {}).get("case_id"),
            cases=len(validation_refs),
            first_target=first_target,
            rank=(validation.get("final_stats") or {}).get("marginal_rank_gain"),
            removed=(validation.get("final_stats") or {}).get("removed_free_columns"),
            out=args.out,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
