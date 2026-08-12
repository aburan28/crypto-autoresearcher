#!/usr/bin/env python3
"""P1078 remaining-column source-family pivot after the P1073 [14,15] packet."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import low_term_total2_p1055_p231_source_charged_rank_audit as p1055
import low_term_total2_p1063_p231_free_column_source_construction as p1063
import low_term_total2_p1069_p231_forward_transfer_descent_accounting as p1069
import low_term_total2_p1071_p231_remaining_column_source_expansion as p1071


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1078_p231_remaining_column_source_family_pivot.md"
DEFAULT_P1059 = STATE_DIR / "low_term_total2_p1059_p231_rowkey_prefix_shared_source_probe.json"
DEFAULT_P1067 = STATE_DIR / "low_term_total2_p1067_p231_post_carrier_source_refresh_probe.json"
DEFAULT_P1069 = STATE_DIR / "low_term_total2_p1069_p231_forward_transfer_descent_accounting_probe.json"
DEFAULT_P1073 = STATE_DIR / "low_term_total2_p1073_p231_topk7_order_compression_probe.json"
DEFAULT_P1074 = STATE_DIR / "low_term_total2_p1074_p231_disjoint_source_packet_validation_probe.json"
DEFAULT_P1077 = STATE_DIR / "low_term_total2_p1077_p231_frozen_filter_holdout_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1078_p231_remaining_column_source_family_pivot_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1078_p231_remaining_column_source_family_pivot.v1"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_columns(text: str) -> list[int]:
    return [int(item) for item in text.split(",") if item.strip()]


def direct_ops(ref: dict[str, Any]) -> float:
    return p1055.float_value(ref.get("direct_ops_over_rho")) or float("inf")


def ref_sort_key(ref: dict[str, Any]) -> tuple[Any, ...]:
    return (ref["window_start"], ref["transfer_index"], ref["selector"], ref["top_k"], ref["case_id"])


def ref_summary(ref: dict[str, Any] | None) -> dict[str, Any] | None:
    if ref is None:
        return None
    keys = [
        "case_id",
        "direct_ops_over_rho",
        "direct_public_key_verified",
        "priority_hits",
        "row_keys",
        "salt_max",
        "salt_min",
        "salt_sum",
        "selected_term_support",
        "selector",
        "source",
        "target",
        "top_k",
        "transfer_index",
        "window",
        "window_start",
    ]
    return {key: ref.get(key) for key in keys if key in ref}


def packet_summary(packet: dict[str, Any]) -> dict[str, Any]:
    return {
        "base_plus_source_free_columns": packet.get("base_plus_source_free_columns") or [],
        "base_plus_source_rank": packet.get("base_plus_source_rank"),
        "base_rank": packet.get("base_rank"),
        "charge_per_rank_gain": packet.get("charge_per_rank_gain"),
        "selected_case_count": packet.get("selected_case_count"),
        "selected_window_count": packet.get("selected_window_count"),
        "source_rank_gain_over_base": packet.get("source_rank_gain_over_base"),
        "source_support_columns": packet.get("source_support_columns") or [],
        "strict_source_charge_over_rho": packet.get("strict_source_charge_over_rho"),
        "usable_source_certificate_count": packet.get("usable_source_certificate_count"),
    }


def find_ref(refs: list[dict[str, Any]], case_id: str | None, label: str) -> dict[str, Any]:
    if not case_id:
        raise ValueError(f"{label} case id is missing")
    for ref in refs:
        if ref["case_id"] == case_id:
            return ref
    raise ValueError(f"{label} case id not found in expanded refs: {case_id}")


def compact_item(item: dict[str, Any]) -> dict[str, Any]:
    payload = ref_summary(item.get("ref")) or {}
    payload.update(
        {
            "classes": item.get("classes") or [],
            "stats": item.get("stats"),
        }
    )
    return payload


def progress_sort_key(item: dict[str, Any], remaining_columns: set[int]) -> tuple[Any, ...]:
    stats = item["stats"]
    removed = set(stats.get("removed_free_columns") or [])
    remaining_hit = bool(removed & remaining_columns)
    charge = p1055.float_value(stats.get("marginal_charge_over_rho")) or float("inf")
    return (
        not (remaining_hit and charge < 1.0),
        not remaining_hit,
        charge,
        -p1055.int_value(stats.get("marginal_rank_gain")),
        item.get("selector") or "",
        item.get("top_k") or -1,
        (item.get("ref") or {}).get("case_id") or item.get("family_key") or "",
    )


def classify_stats(stats: dict[str, Any], remaining_columns: set[int], replay_columns: set[int]) -> list[str]:
    removed = set(stats.get("removed_free_columns") or [])
    charge = p1055.float_value(stats.get("marginal_charge_over_rho")) or float("inf")
    classes: list[str] = []
    if removed & remaining_columns:
        classes.append("remaining_column_hit_below_rho" if charge < 1.0 else "remaining_column_hit_above_rho")
    if removed and removed <= replay_columns:
        classes.append("replay_column_only")
    if stats.get("marginal_rank_gain", 0) > 0 and not removed:
        classes.append("rank_gain_no_free_column")
    if not classes and (stats.get("marginal_rank_gain", 0) > 0 or removed):
        classes.append("other_progress")
    return classes


def build_context(args: argparse.Namespace) -> dict[str, Any]:
    p1067_payload = load_json(args.p1067)
    p1069_payload = load_json(args.p1069)
    p1073_payload = load_json(args.p1073)
    p1074_payload = load_json(args.p1074) if args.p1074.exists() else {}

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
    family_refs.sort(key=ref_sort_key)
    cache: dict[Path, list[dict[str, Any]]] = {}
    promoted_packet = p1071.evaluate_refs(promoted_refs, factor_rows, cache, args)
    priority_columns = parse_columns(args.priority_columns)

    stage1_ref = None
    stage1_stats = None
    for ref in family_refs:
        result = p1071.evaluate_refs(promoted_refs + [ref], factor_rows, cache, args)
        stats = p1063.marginal_stats(promoted_packet, result, priority_columns)
        if (stats["marginal_rank_gain"] > 0 or stats["removed_free_columns"]) and stats["marginal_charge_over_rho"] < 1.0:
            stage1_ref = ref
            stage1_stats = stats
            break
    if stage1_ref is None:
        raise ValueError("no below-rho stage1 carrier found for frozen family")

    stage1_refs = promoted_refs + [stage1_ref]
    stage1_packet = p1071.evaluate_refs(stage1_refs, factor_rows, cache, args)

    p1073_case_id = ((p1073_payload.get("summary") or {}).get("best_policy") or {}).get("first_target_column_prefix", {}).get(
        "last_case_id"
    )
    p1073_winner_ref = find_ref(expanded_refs, p1073_case_id, "P1073 strict winner")
    strict_refs = stage1_refs + [p1073_winner_ref]
    strict_packet = p1071.evaluate_refs(strict_refs, factor_rows, cache, args)

    p1074_case_id = None
    disjoint = (p1074_payload.get("summary") or {}).get("disjoint_single_windows") or []
    if disjoint:
        p1074_case_id = ((disjoint[0].get("first_target_column_prefix") or {}).get("last_case_id"))
    p1074_carrier_ref = find_ref(expanded_refs, p1074_case_id, "P1074 diagnostic carrier") if p1074_case_id else None
    diagnostic_refs = stage1_refs + ([p1074_carrier_ref] if p1074_carrier_ref else [])
    diagnostic_packet = p1071.evaluate_refs(diagnostic_refs, factor_rows, cache, args) if p1074_carrier_ref else None

    return {
        "cache": cache,
        "diagnostic_packet": diagnostic_packet,
        "diagnostic_refs": diagnostic_refs if p1074_carrier_ref else [],
        "expanded_refs": expanded_refs,
        "factor_paths": factor_paths,
        "factor_rows": factor_rows,
        "inventory": inventory,
        "p1073_payload": p1073_payload,
        "p1073_winner_ref": p1073_winner_ref,
        "p1074_carrier_ref": p1074_carrier_ref,
        "p1074_payload": p1074_payload,
        "promoted_packet": promoted_packet,
        "promoted_refs": promoted_refs,
        "promotion_window_end": promotion_window_end,
        "selected_paths": selected_paths,
        "stage1_packet": stage1_packet,
        "stage1_ref": stage1_ref,
        "stage1_refs": stage1_refs,
        "stage1_stats": stage1_stats,
        "strict_packet": strict_packet,
        "strict_refs": strict_refs,
    }


def scan_packet(
    name: str,
    baseline_refs: list[dict[str, Any]],
    baseline_packet: dict[str, Any],
    candidate_refs: list[dict[str, Any]],
    factor_rows: dict[str, dict[str, Any]],
    cache: dict[Path, list[dict[str, Any]]],
    args: argparse.Namespace,
    remaining_columns: set[int],
    replay_columns: set[int],
) -> dict[str, Any]:
    analysis_columns = sorted(remaining_columns | replay_columns)
    baseline_ids = {ref["case_id"] for ref in baseline_refs}
    candidates = [ref for ref in candidate_refs if ref["case_id"] not in baseline_ids]
    single_progress: list[dict[str, Any]] = []
    single_remaining: list[dict[str, Any]] = []
    single_remaining_below: list[dict[str, Any]] = []
    single_replay_only = 0
    single_rank_only = 0

    for ref in candidates:
        result = p1071.evaluate_refs(baseline_refs + [ref], factor_rows, cache, args)
        stats = p1063.marginal_stats(baseline_packet, result, analysis_columns)
        classes = classify_stats(stats, remaining_columns, replay_columns)
        if not classes:
            continue
        item = {"classes": classes, "ref": ref, "stats": stats}
        single_progress.append(item)
        if "replay_column_only" in classes:
            single_replay_only += 1
        if "rank_gain_no_free_column" in classes:
            single_rank_only += 1
        if "remaining_column_hit_below_rho" in classes or "remaining_column_hit_above_rho" in classes:
            single_remaining.append(item)
            if "remaining_column_hit_below_rho" in classes:
                single_remaining_below.append(item)

    refs_by_combo: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for ref in candidates:
        refs_by_combo[(ref["selector"], p1055.int_value(ref.get("top_k"), -1))].append(ref)

    family_progress: list[dict[str, Any]] = []
    family_remaining: list[dict[str, Any]] = []
    family_remaining_below: list[dict[str, Any]] = []
    for (selector, top_k), refs in sorted(refs_by_combo.items()):
        refs.sort(key=ref_sort_key)
        result = p1071.evaluate_refs(baseline_refs + refs, factor_rows, cache, args)
        stats = p1063.marginal_stats(baseline_packet, result, analysis_columns)
        classes = classify_stats(stats, remaining_columns, replay_columns)
        item = {
            "case_count": len(refs),
            "classes": classes,
            "family_key": f"{selector}:{top_k}",
            "first_case_id": refs[0]["case_id"] if refs else None,
            "selector": selector,
            "stats": stats,
            "top_k": top_k,
            "window_count": len({ref["window"] for ref in refs}),
        }
        if classes:
            family_progress.append(item)
        if "remaining_column_hit_below_rho" in classes or "remaining_column_hit_above_rho" in classes:
            family_remaining.append(item)
            if "remaining_column_hit_below_rho" in classes:
                family_remaining_below.append(item)

    full_result = p1071.evaluate_refs(baseline_refs + candidates, factor_rows, cache, args)
    full_stats = p1063.marginal_stats(baseline_packet, full_result, analysis_columns)
    full_classes = classify_stats(full_stats, remaining_columns, replay_columns)

    single_progress.sort(key=lambda item: progress_sort_key(item, remaining_columns))
    single_remaining.sort(key=lambda item: progress_sort_key(item, remaining_columns))
    single_remaining_below.sort(key=lambda item: progress_sort_key(item, remaining_columns))
    family_progress.sort(key=lambda item: progress_sort_key(item, remaining_columns))
    family_remaining.sort(key=lambda item: progress_sort_key(item, remaining_columns))
    family_remaining_below.sort(key=lambda item: progress_sort_key(item, remaining_columns))

    strict_success = bool(
        single_remaining_below
        or family_remaining_below
        or ("remaining_column_hit_below_rho" in full_classes)
    )
    any_remaining = bool(single_remaining or family_remaining or any(col in full_stats["removed_free_columns"] for col in remaining_columns))
    return {
        "baseline_free_columns": baseline_packet.get("base_plus_source_free_columns") or [],
        "baseline_name": name,
        "full_pool": {
            "classes": full_classes,
            "result": p1071.compact_result(full_result, max_cases=8),
            "stats": full_stats,
        },
        "record_counts": {
            "candidate_case_count": len(candidates),
            "candidate_family_count": len(refs_by_combo),
            "family_progress_count": len(family_progress),
            "family_remaining_below_rho_count": len(family_remaining_below),
            "family_remaining_count": len(family_remaining),
            "single_progress_count": len(single_progress),
            "single_rank_only_count": single_rank_only,
            "single_remaining_below_rho_count": len(single_remaining_below),
            "single_remaining_count": len(single_remaining),
            "single_replay_only_count": single_replay_only,
        },
        "strict_success": strict_success,
        "summary": {
            "any_remaining_column_signal": any_remaining,
            "best_family_progress": family_progress[0] if family_progress else None,
            "best_family_remaining": family_remaining[0] if family_remaining else None,
            "best_family_remaining_below_rho": family_remaining_below[0] if family_remaining_below else None,
            "best_single_progress": compact_item(single_progress[0]) if single_progress else None,
            "best_single_remaining": compact_item(single_remaining[0]) if single_remaining else None,
            "best_single_remaining_below_rho": compact_item(single_remaining_below[0]) if single_remaining_below else None,
            "full_pool_classes": full_classes,
            "full_pool_removed_free_columns": full_stats["removed_free_columns"],
            "full_pool_marginal_charge_over_rho": full_stats["marginal_charge_over_rho"],
            "full_pool_marginal_rank_gain": full_stats["marginal_rank_gain"],
            "strict_success": strict_success,
        },
        "top_family_progress": family_progress[:12],
        "top_family_remaining": family_remaining[:12],
        "top_single_progress": [compact_item(item) for item in single_progress[:20]],
        "top_single_remaining": [compact_item(item) for item in single_remaining[:20]],
    }


def stage1_replay_controls(
    stage1_refs: list[dict[str, Any]],
    stage1_packet: dict[str, Any],
    candidates: list[dict[str, Any]],
    context: dict[str, Any],
    args: argparse.Namespace,
    remaining_columns: set[int],
    replay_columns: set[int],
) -> dict[str, Any]:
    baseline_ids = {ref["case_id"] for ref in stage1_refs}
    analysis_columns = sorted(remaining_columns | replay_columns)
    replay_items: list[dict[str, Any]] = []
    remaining_items: list[dict[str, Any]] = []
    for ref in candidates:
        if ref["case_id"] in baseline_ids:
            continue
        result = p1071.evaluate_refs(stage1_refs + [ref], context["factor_rows"], context["cache"], args)
        stats = p1063.marginal_stats(stage1_packet, result, analysis_columns)
        classes = classify_stats(stats, remaining_columns, replay_columns)
        item = {"classes": classes, "ref": ref, "stats": stats}
        if "replay_column_only" in classes:
            replay_items.append(item)
        if "remaining_column_hit_below_rho" in classes or "remaining_column_hit_above_rho" in classes:
            remaining_items.append(item)
    replay_items.sort(key=lambda item: progress_sort_key(item, remaining_columns))
    remaining_items.sort(key=lambda item: progress_sort_key(item, remaining_columns))

    p1073_control = p1063.marginal_stats(
        stage1_packet,
        p1071.evaluate_refs(stage1_refs + [context["p1073_winner_ref"]], context["factor_rows"], context["cache"], args),
        analysis_columns,
    )
    p1074_control = None
    if context.get("p1074_carrier_ref"):
        p1074_control = p1063.marginal_stats(
            stage1_packet,
            p1071.evaluate_refs(stage1_refs + [context["p1074_carrier_ref"]], context["factor_rows"], context["cache"], args),
            analysis_columns,
        )
    return {
        "best_remaining_against_stage1": compact_item(remaining_items[0]) if remaining_items else None,
        "best_replay_against_stage1": compact_item(replay_items[0]) if replay_items else None,
        "p1073_winner_stage1_stats": p1073_control,
        "p1074_carrier_stage1_stats": p1074_control,
        "remaining_count_against_stage1": len(remaining_items),
        "replay_only_count_against_stage1": len(replay_items),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--p1059", type=Path, default=DEFAULT_P1059)
    parser.add_argument("--p1067", type=Path, default=DEFAULT_P1067)
    parser.add_argument("--p1069", type=Path, default=DEFAULT_P1069)
    parser.add_argument("--p1073", type=Path, default=DEFAULT_P1073)
    parser.add_argument("--p1074", type=Path, default=DEFAULT_P1074)
    parser.add_argument("--p1077", type=Path, default=DEFAULT_P1077)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--factor-glob", default=p1055.DEFAULT_FACTOR_GLOB)
    parser.add_argument("--selected-glob", default=p1055.DEFAULT_SELECTED_GLOB)
    parser.add_argument("--order", type=int, default=11779)
    parser.add_argument("--column", type=int, default=15)
    parser.add_argument("--priority-columns", default="6,7,10,14,15")
    parser.add_argument("--remaining-columns", default="6,7")
    parser.add_argument("--replay-columns", default="15")
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

    remaining_columns = set(parse_columns(args.remaining_columns))
    replay_columns = set(parse_columns(args.replay_columns))
    context = build_context(args)
    expanded_refs = context["expanded_refs"]

    strict_scan = scan_packet(
        "strict_p1073_packet",
        context["strict_refs"],
        context["strict_packet"],
        expanded_refs,
        context["factor_rows"],
        context["cache"],
        args,
        remaining_columns,
        replay_columns,
    )
    diagnostic_scan = None
    if context.get("diagnostic_packet"):
        diagnostic_scan = scan_packet(
            "diagnostic_p1074_packet",
            context["diagnostic_refs"],
            context["diagnostic_packet"],
            expanded_refs,
            context["factor_rows"],
            context["cache"],
            args,
            remaining_columns,
            replay_columns,
        )
    replay_controls = stage1_replay_controls(
        context["stage1_refs"],
        context["stage1_packet"],
        expanded_refs,
        context,
        args,
        remaining_columns,
        replay_columns,
    )

    strict_success = bool(strict_scan["strict_success"])
    strict_any_remaining = bool(strict_scan["summary"]["any_remaining_column_signal"])
    if strict_success:
        claim_status = "POSITIVE_SIGNAL_P1078_REMAINING_COLUMN_67_BELOW_RHO_SOURCE_PIVOT"
    elif strict_any_remaining:
        claim_status = "OBSERVATION_P1078_REMAINING_COLUMN_67_EXISTS_ABOVE_RHO_IN_EXPANDED_POOL"
    else:
        claim_status = "NEGATIVE_RESULT_P1078_EXPANDED_FAMILIES_NO_67_DIRECTION_AFTER_1415_PACKET"

    p1077_payload = load_json(args.p1077) if args.p1077.exists() else {}
    payload = {
        "artifact_hashes": {
            "contract": p1069.sha256_file(args.contract) if args.contract.exists() else None,
            "factor_artifact_count": len(context["factor_paths"]),
            "factor_artifact_digest": p1069.digest_paths(context["factor_paths"]),
            "p1059": p1069.sha256_file(args.p1059) if args.p1059.exists() else None,
            "p1067": p1069.sha256_file(args.p1067) if args.p1067.exists() else None,
            "p1069": p1069.sha256_file(args.p1069) if args.p1069.exists() else None,
            "p1073": p1069.sha256_file(args.p1073) if args.p1073.exists() else None,
            "p1074": p1069.sha256_file(args.p1074) if args.p1074.exists() else None,
            "p1077": p1069.sha256_file(args.p1077) if args.p1077.exists() else None,
            "script": p1069.sha256_file(Path(__file__)),
            "selected_artifact_count": len(context["selected_paths"]),
            "selected_artifact_digest": p1069.digest_paths(context["selected_paths"]),
        },
        "artifacts": {
            "contract": str(args.contract),
            "p1059": str(args.p1059),
            "p1067": str(args.p1067),
            "p1069": str(args.p1069),
            "p1073": str(args.p1073),
            "p1074": str(args.p1074),
            "p1077": str(args.p1077),
            "script": str(Path(__file__)),
        },
        "claim_status": claim_status,
        "claim_taxonomy": [
            "TOY-EVIDENCE",
            "MODEL-BOUND",
            "SOURCE-FAMILY-PIVOT",
            "SINGLE-TARGET",
            "POLLARD-RHO-BOUNDARY",
            "DIRECT-OPS-CAVEAT",
        ],
        "controls": {
            "diagnostic_p1074_packet": packet_summary(context["diagnostic_packet"]) if context.get("diagnostic_packet") else None,
            "p1077_summary": p1077_payload.get("summary"),
            "promoted_packet": packet_summary(context["promoted_packet"]),
            "replay_controls": replay_controls,
            "stage1_packet": packet_summary(context["stage1_packet"]),
            "strict_p1073_packet": packet_summary(context["strict_packet"]),
        },
        "expanded_source_inventory": context["inventory"],
        "honesty_boundary": {
            "cryptographic_scale_unproved": True,
            "fresh_target_artifacts_available": bool(context["inventory"]["fresh_target_available_in_selected_source_family"]),
            "not_a_complete_index_calculus_algorithm": True,
            "not_a_deployed_curve_break": True,
            "pre_materialized_source_pool": True,
            "target_descent_not_closed_unless_6_and_7_removed": True,
        },
        "parameters": {
            "baseline_model": "strict [14,15] packet from P1072/P1073; P1074 packet retained as diagnostic control",
            "column": args.column,
            "order": args.order,
            "priority_columns": parse_columns(args.priority_columns),
            "remaining_columns": sorted(remaining_columns),
            "replay_columns": sorted(replay_columns),
            "source": args.source,
            "target": args.target,
            "target_selector": args.selector,
            "target_top_k": args.top_k,
            "promotion_window_end": context["promotion_window_end"],
            "stage1_ref": ref_summary(context["stage1_ref"]),
            "stage1_stats": context["stage1_stats"],
            "p1073_winner_ref": ref_summary(context["p1073_winner_ref"]),
            "p1074_carrier_ref": ref_summary(context.get("p1074_carrier_ref")),
            "strict_ref_case_ids": [ref["case_id"] for ref in context["strict_refs"]],
        },
        "record_counts": {
            "expanded_case_count": len(expanded_refs),
            "expanded_window_count": len({ref["window"] for ref in expanded_refs}),
            "strict_candidate_case_count": strict_scan["record_counts"]["candidate_case_count"],
            "strict_candidate_family_count": strict_scan["record_counts"]["candidate_family_count"],
        },
        "schema": SCHEMA,
        "strict_scan": strict_scan,
        "diagnostic_scan": diagnostic_scan,
        "strict_success": strict_success,
        "summary": {
            "claim_status": claim_status,
            "diagnostic_strict_success": bool(diagnostic_scan and diagnostic_scan["strict_success"]),
            "expanded_case_count": len(expanded_refs),
            "fresh_target_artifacts_available": context["inventory"]["fresh_target_available_in_selected_source_family"],
            "p1077_claim_status": (p1077_payload.get("summary") or {}).get("claim_status"),
            "remaining_columns": sorted(remaining_columns),
            "replay_only_count_against_stage1": replay_controls["replay_only_count_against_stage1"],
            "stage1_free_columns": context["stage1_packet"].get("base_plus_source_free_columns") or [],
            "strict_any_remaining_column_signal": strict_any_remaining,
            "strict_best_family_remaining": strict_scan["summary"]["best_family_remaining"],
            "strict_best_single_remaining": strict_scan["summary"]["best_single_remaining"],
            "strict_full_pool_classes": strict_scan["summary"]["full_pool_classes"],
            "strict_full_pool_removed_free_columns": strict_scan["summary"]["full_pool_removed_free_columns"],
            "strict_packet_free_columns": context["strict_packet"].get("base_plus_source_free_columns") or [],
            "strict_success": strict_success,
        },
        "timestamp_utc": p1071.now_iso(),
    }
    write_json(args.out, payload)
    print(
        "claim={claim} strict_success={success} expanded_cases={cases} "
        "single_remaining={single_remaining} family_remaining={family_remaining} full_removed={full_removed} out={out}".format(
            claim=claim_status,
            success=strict_success,
            cases=len(expanded_refs),
            single_remaining=strict_scan["record_counts"]["single_remaining_count"],
            family_remaining=strict_scan["record_counts"]["family_remaining_count"],
            full_removed=strict_scan["summary"]["full_pool_removed_free_columns"],
            out=args.out,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
