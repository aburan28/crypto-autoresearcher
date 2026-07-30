#!/usr/bin/env python3
"""Measure pre-row-pool root/point membership for the fixed scout-7 leaf.

The direct leaf-65 scout-7 kernel is below rho only after row-pool setup is
removed, and the row-pool gate model showed that an oracle selected-root gate
would be enough.  This probe measures the concrete row-side primitive behind
that work order:

* solve the invariant leaf-65 quadratic once and stream deterministic rows
  until a root x-value is found;
* stream deterministic rows until the invariant scout-7 branch point is found;
* compare those streaming ledgers to full row-pool materialization.

The implementation still replays the existing context builder to recover row
orders and branch inputs.  The reported costs are therefore a work-order ledger
for a future streaming implementation, not a claim that this script itself has
avoided row construction.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from math import ceil
from pathlib import Path
from typing import Any

import frontier_signed_eval_cover_critical_leaf_probe as critical_leaf_probe
import low_term_total2_fixed_leaf_shared_product_timing_probe as timing_probe
import semaev_root_mitm_probe
from low_term_total2_scout_pos7_direct_leaf65_kernel_probe import (
    int_value,
    load_json,
    ratio,
    scout7_leaf65_terms,
    write_json,
)
from low_term_total2_scout_pos7_rowpool_cacheability_probe import (
    attempt_key,
    source_row_lookup,
)


ROOT_MODELS = (
    "root_stream_gate_constructive_fractional",
    "root_stream_gate_positive_rowpool_fractional",
    "root_stream_gate_positive_rowpool_integer",
)

BRANCH_FIRST_MODELS = (
    "branch_point_stream_cached_fractional",
    "branch_point_stream_context_setup_fractional",
    "branch_point_stream_context_setup_integer",
)

BRANCH_FULL_MODELS = (
    "branch_point_full_scan_cached_fractional",
    "branch_point_full_scan_context_setup_fractional",
    "branch_point_full_scan_context_setup_integer",
)

MODELS = ROOT_MODELS + BRANCH_FIRST_MODELS + BRANCH_FULL_MODELS


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def point_payload(point: Any) -> tuple[int, int] | None:
    if point is None:
        return None
    return int(point[0]), int(point[1])


def point_equal(left: Any, right: Any) -> bool:
    return point_payload(left) == point_payload(right)


def field_roots_for_leaf(poly: list[Any], p: int, verifier: Any) -> list[int]:
    coeffs = [int_value(part) % p for part in poly]
    while len(coeffs) > 1 and coeffs[-1] == 0:
        coeffs.pop()
    if len(coeffs) == 3:
        return sorted(semaev_root_mitm_probe.quadratic_roots_mod(coeffs[2], coeffs[1], coeffs[0], p, verifier))
    if len(coeffs) == 2:
        return [(-coeffs[0] * pow(coeffs[1], -1, p)) % p] if coeffs[1] else []
    return [root for root in range(p) if sum(coeff * pow(root, idx, p) for idx, coeff in enumerate(coeffs)) % p == 0]


def row_scan_cost(first_trial: int | None, row_count: int, row_factor: int) -> dict[str, Any]:
    scanned = int(first_trial) if first_trial is not None else int(row_count)
    scanned = max(0, min(scanned, int(row_count)))
    row_factor = max(1, int(row_factor))
    return {
        "integer_ops": ceil(scanned / row_factor),
        "scanned_rows": scanned,
        "fractional_ops": round(scanned / row_factor, 8),
    }


def direct_context_for(attempt: dict[str, Any], row_key: str) -> dict[str, Any]:
    return next(
        (
            row
            for row in attempt.get("context_rows") or []
            if isinstance(row, dict) and str(row.get("row_key")) == row_key
        ),
        {},
    )


def scan_context(
    verifier: Any,
    context: dict[str, Any],
    direct_context: dict[str, Any],
    target_leaf: int,
    form_keys: set[tuple[tuple[int, ...], int]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    built = context["built"]
    components = context["components"]
    p = int_value(built.get("p"))
    order = int_value(built.get("order"))
    rows = sorted(built.get("rows") or [], key=lambda row: int_value(row.get("trial")))
    row_count = len(rows)
    row_factor = max(1, int_value(getattr(context.get("local_args"), "row_factor", 1), 1))
    scout_to_leaf = critical_leaf_probe.scout_leaf_map(components)
    scout7_leaf = int_value(scout_to_leaf.get(7), -1)
    leaf = (components.get("leaves") or [{}])[target_leaf] if 0 <= target_leaf < len(components.get("leaves") or []) else {}
    leaf_roots = field_roots_for_leaf([int_value(part) for part in leaf.get("poly") or []], p, verifier)
    root_set = {int(root) % p for root in leaf_roots}
    root_positions = [
        int_value(row.get("trial"))
        for row in rows
        if int_value(row.get("x")) % p in root_set
    ]
    selected_root_values = sorted({int_value(row.get("x")) % p for row in rows if int_value(row.get("x")) % p in root_set})

    branch_scouts = [
        scout
        for scout in built.get("scouts") or []
        if scout7_leaf65_terms(scout)
        and int_value(scout_to_leaf.get(int_value(scout.get("scout_pos"))), -1) == target_leaf
    ]
    branch_scout = branch_scouts[0] if branch_scouts else None
    candidate_point = (
        verifier.add_points(branch_scout["left"]["point"], branch_scout["right"]["point"], built["ainvs"], p)
        if branch_scout is not None
        else None
    )
    point_rows = [row for row in rows if candidate_point is not None and point_equal(row.get("point"), candidate_point)]
    point_positions = [int_value(row.get("trial")) for row in point_rows]

    point_match_records: list[dict[str, Any]] = []
    if branch_scout is not None:
        terms = [int_value(index) for index in branch_scout.get("unsigned_indices") or []]
        for hit_row in point_rows:
            relation = {"a": int_value(hit_row.get("a")), "b": int_value(hit_row.get("b")), "indices": terms}
            relation_terms = verifier.relation_terms(relation, built["challenge"], built["ainvs"], p)
            if relation_terms is None:
                continue
            coeffs, rhs = verifier.relation_linear_form(relation, relation_terms, built["challenge"], order)
            form_key = (tuple(int_value(coeff) % order for coeff in coeffs), int_value(rhs) % order)
            duplicate = form_key in form_keys
            form_keys.add(form_key)
            point_match_records.append(
                {
                    "form_duplicate": duplicate,
                    "original_trial": int_value(hit_row.get("trial")),
                    "q_coeff": int_value(coeffs[0]) % order,
                    "rhs": int_value(rhs) % order,
                    "row_key": str(context.get("row_key") or ""),
                    "scout_pos": int_value(branch_scout.get("scout_pos")),
                    "terms": terms,
                }
            )

    root_cost = row_scan_cost(min(root_positions) if root_positions else None, row_count, row_factor)
    point_first_cost = row_scan_cost(min(point_positions) if point_positions else None, row_count, row_factor)
    point_full_cost = row_scan_cost(row_count if rows else None, row_count, row_factor)
    constructive_ops = int_value((direct_context.get("model_ops") or {}).get("constructive_leaf65_kernel"))
    row_pool_ops = int_value(direct_context.get("row_pool_ops"), ceil(row_count / row_factor))
    direct_selected_hit_roots = int_value(direct_context.get("selected_hit_roots"))
    direct_affine_matches = int_value(direct_context.get("affine_match_count"))
    return (
        {
            "branch_scout_count": len(branch_scouts),
            "branch_setup_ops": 1 if branch_scout is not None else 0,
            "constructive_ops": constructive_ops,
            "direct_affine_match_count": direct_affine_matches,
            "direct_selected_hit_roots": direct_selected_hit_roots,
            "leaf65_roots": leaf_roots,
            "point_first_scan": point_first_cost,
            "point_full_scan": point_full_cost,
            "point_match_count": len(point_match_records),
            "point_match_first_count": 1 if point_match_records else 0,
            "point_positions": point_positions,
            "root_hit": bool(selected_root_values),
            "root_positions": root_positions,
            "root_scan": root_cost,
            "row_count": row_count,
            "row_factor": row_factor,
            "row_key": str(context.get("row_key") or ""),
            "row_pool_ops": row_pool_ops,
            "scout7_leaf": scout7_leaf,
            "selected_root_values": selected_root_values,
            "stream_affine_match_count": len(point_match_records),
            "stream_selected_hit_roots": len(selected_root_values),
        },
        point_match_records,
    )


def attempt_model_ops(contexts: list[dict[str, Any]], point_matches: list[dict[str, Any]]) -> dict[str, float]:
    root_fractional = sum(float(row["root_scan"]["fractional_ops"]) for row in contexts)
    root_integer = sum(int_value(row["root_scan"]["integer_ops"]) for row in contexts)
    point_first_fractional = sum(float(row["point_first_scan"]["fractional_ops"]) for row in contexts)
    point_first_integer = sum(int_value(row["point_first_scan"]["integer_ops"]) for row in contexts)
    point_full_fractional = sum(float(row["point_full_scan"]["fractional_ops"]) for row in contexts)
    point_full_integer = sum(int_value(row["point_full_scan"]["integer_ops"]) for row in contexts)
    branch_setup = sum(int_value(row.get("branch_setup_ops")) for row in contexts)
    positive_constructive = sum(int_value(row.get("constructive_ops")) for row in contexts if row.get("root_hit"))
    positive_rowpool = sum(int_value(row.get("row_pool_ops")) for row in contexts if row.get("root_hit"))
    first_match_ops = sum(int_value(row.get("point_match_first_count")) for row in contexts)
    full_match_ops = len(point_matches)
    return {
        "branch_point_full_scan_cached_fractional": round(point_full_fractional + full_match_ops, 8),
        "branch_point_full_scan_context_setup_fractional": round(point_full_fractional + branch_setup + full_match_ops, 8),
        "branch_point_full_scan_context_setup_integer": point_full_integer + branch_setup + full_match_ops,
        "branch_point_stream_cached_fractional": round(point_first_fractional + first_match_ops, 8),
        "branch_point_stream_context_setup_fractional": round(point_first_fractional + branch_setup + first_match_ops, 8),
        "branch_point_stream_context_setup_integer": point_first_integer + branch_setup + first_match_ops,
        "root_stream_gate_constructive_fractional": round(root_fractional + positive_constructive, 8),
        "root_stream_gate_positive_rowpool_fractional": round(root_fractional + positive_constructive + positive_rowpool, 8),
        "root_stream_gate_positive_rowpool_integer": root_integer + positive_constructive + positive_rowpool,
    }


def scan_attempt(source: dict[str, Any], row: dict[str, Any], attempt: dict[str, Any], target_leaf: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    try:
        verifier, contexts, _product_factor, _max_relations = timing_probe.selected_contexts_from_source_case(source, row)
        form_keys: set[tuple[tuple[int, ...], int]] = set()
        profiles: list[dict[str, Any]] = []
        point_matches: list[dict[str, Any]] = []
        rho = 0
        for context in contexts:
            rho = max(rho, int_value(context["built"].get("generic_rho_steps")))
            profile, context_matches = scan_context(
                verifier,
                context,
                direct_context_for(attempt, str(context.get("row_key") or "")),
                target_leaf,
                form_keys,
            )
            profiles.append(profile)
            point_matches.extend(context_matches)
        models = attempt_model_ops(profiles, point_matches)
        return (
            {
                "accepted_branch_first": sum(int_value(row.get("point_match_first_count")) for row in profiles) >= 2,
                "accepted_branch_full": len(point_matches) >= 2,
                "accepted_direct": bool(attempt.get("accepted")),
                "context_rows": profiles,
                "model_ops": models,
                "model_ops_over_rho": {name: ratio(value, rho) for name, value in models.items()},
                "point_matches": point_matches,
                "rank_gain": int_value(attempt.get("rank_gain")),
                "rho": rho,
                "row_keys": attempt.get("row_keys") or [],
                "root_context_count": sum(1 for row in profiles if row.get("root_hit")),
                "selected_root_mismatch_count": sum(
                    1
                    for row in profiles
                    if int_value(row.get("stream_selected_hit_roots")) != int_value(row.get("direct_selected_hit_roots"))
                ),
                "point_match_mismatch_count": sum(
                    1
                    for row in profiles
                    if int_value(row.get("stream_affine_match_count")) != int_value(row.get("direct_affine_match_count"))
                ),
                "transfer_index": int_value(attempt.get("transfer_index")),
            },
            errors,
        )
    except Exception as exc:  # noqa: BLE001 - preserve research replay failures.
        errors.append({"error": "pre_rowpool_attempt_failed", "message": str(exc), "transfer_index": int_value(attempt.get("transfer_index"))})
        return ({}, errors)


def zero_ops() -> dict[str, float]:
    return {name: 0.0 for name in MODELS}


def add_ops(left: dict[str, float], right: dict[str, Any]) -> None:
    for name in MODELS:
        left[name] = float(left.get(name, 0.0)) + float(right.get(name, 0.0))


def collect_group(
    source_path: Path,
    source: dict[str, Any],
    lookup: dict[tuple[int, tuple[str, ...]], dict[str, Any]],
    group: dict[str, Any],
    target_leaf: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    attempts: list[dict[str, Any]] = []
    root_ops = zero_ops()
    branch_first_ops = zero_ops()
    branch_full_ops = zero_ops()
    branch_first_stop = None
    branch_full_stop = None
    for attempt in group.get("attempts") or []:
        row = lookup.get(attempt_key(attempt))
        if row is None:
            errors.append({"error": "missing_source_case_for_attempt", "source_path": str(source_path), "transfer_index": int_value(attempt.get("transfer_index"))})
            continue
        stream_attempt, attempt_errors = scan_attempt(source, row, attempt, target_leaf)
        errors.extend({**item, "source_path": str(source_path)} for item in attempt_errors)
        if not stream_attempt:
            continue
        attempts.append(stream_attempt)
        add_ops(root_ops, {name: stream_attempt["model_ops"][name] for name in ROOT_MODELS})
        if branch_first_stop is None:
            add_ops(branch_first_ops, {name: stream_attempt["model_ops"][name] for name in BRANCH_FIRST_MODELS})
            if stream_attempt.get("accepted_branch_first"):
                branch_first_stop = stream_attempt
        if branch_full_stop is None:
            add_ops(branch_full_ops, {name: stream_attempt["model_ops"][name] for name in BRANCH_FULL_MODELS})
            if stream_attempt.get("accepted_branch_full"):
                branch_full_stop = stream_attempt

    model_ops = zero_ops()
    for name in ROOT_MODELS:
        model_ops[name] = root_ops[name]
    for name in BRANCH_FIRST_MODELS:
        model_ops[name] = branch_first_ops[name]
    for name in BRANCH_FULL_MODELS:
        model_ops[name] = branch_full_ops[name]
    rho = int_value(group.get("rho"))
    return (
        {
            "attempt_count": len(attempts),
            "attempts": attempts,
            "branch_first_stop": branch_first_stop,
            "branch_full_stop": branch_full_stop,
            "direct_has_rank_gain_stop": bool(group.get("has_rank_gain_stop")),
            "has_branch_first_rank_gain_stop": bool(branch_first_stop and int_value(branch_first_stop.get("rank_gain")) > 0),
            "has_branch_first_stop": branch_first_stop is not None,
            "has_branch_full_rank_gain_stop": bool(branch_full_stop and int_value(branch_full_stop.get("rank_gain")) > 0),
            "has_branch_full_stop": branch_full_stop is not None,
            "has_direct_stop": bool(group.get("has_accepted_stop")),
            "model_ops": model_ops,
            "model_ops_over_rho": {name: ratio(value, rho) for name, value in model_ops.items()},
            "rho": rho,
            "source_path": str(source_path),
            "stop": group.get("stop"),
            "window": group.get("window"),
            "window_start": int_value(group.get("window_start")),
        },
        errors,
    )


def split_groups(groups: list[dict[str, Any]], calibration_end: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return (
        [group for group in groups if int_value(group.get("window_start")) <= calibration_end],
        [group for group in groups if int_value(group.get("window_start")) > calibration_end],
    )


def stop_flags(group: dict[str, Any], model: str) -> tuple[bool, bool]:
    if model in ROOT_MODELS:
        return bool(group.get("has_direct_stop")), bool(group.get("direct_has_rank_gain_stop"))
    if model in BRANCH_FIRST_MODELS:
        return bool(group.get("has_branch_first_stop")), bool(group.get("has_branch_first_rank_gain_stop"))
    if model in BRANCH_FULL_MODELS:
        return bool(group.get("has_branch_full_stop")), bool(group.get("has_branch_full_rank_gain_stop"))
    return False, False


def summarize(groups: list[dict[str, Any]]) -> dict[str, Any]:
    rho = max([int_value(group.get("rho")) for group in groups if int_value(group.get("rho")) > 0] or [0])
    model_summaries = {}
    for model in MODELS:
        ops = sum(float((group.get("model_ops") or {}).get(model) or 0.0) for group in groups)
        accepted = []
        rank_hits = []
        for group in groups:
            has_stop, has_rank = stop_flags(group, model)
            if has_stop:
                accepted.append(group)
            if has_rank:
                rank_hits.append(group)
        model_summaries[model] = {
            "accepted_stop_count": len(accepted),
            "cost_per_accepted_stop_over_rho": ratio(ops, rho * len(accepted)) if accepted and rho else None,
            "cost_per_rank_gain_stop_over_rho": ratio(ops, rho * len(rank_hits)) if rank_hits and rho else None,
            "ops": round(ops, 8),
            "ops_over_rho": ratio(ops, rho),
            "precision": ratio(len(rank_hits), len(accepted)) if accepted else None,
            "rank_gain_stop_count": len(rank_hits),
        }
    context_rows = [
        context
        for group in groups
        for attempt in group.get("attempts") or []
        for context in attempt.get("context_rows") or []
    ]
    attempts = [attempt for group in groups for attempt in group.get("attempts") or []]
    return {
        "attempt_count": len(attempts),
        "branch_first_stop_count": sum(1 for group in groups if group.get("has_branch_first_stop")),
        "branch_full_stop_count": sum(1 for group in groups if group.get("has_branch_full_stop")),
        "context_count": len(context_rows),
        "context_root_count": sum(1 for row in context_rows if row.get("root_hit")),
        "direct_stop_count": sum(1 for group in groups if group.get("has_direct_stop")),
        "group_count": len(groups),
        "leaf_root_distribution": {
            ",".join(str(root) for root in roots): count
            for roots, count in sorted(
                Counter(tuple(row.get("leaf65_roots") or []) for row in context_rows).items(),
                key=lambda item: str(item[0]),
            )
        },
        "model_summaries": model_summaries,
        "point_match_mismatch_count": sum(int_value(attempt.get("point_match_mismatch_count")) for attempt in attempts),
        "rho": rho,
        "root_mismatch_count": sum(int_value(attempt.get("selected_root_mismatch_count")) for attempt in attempts),
        "root_position_summary": position_summary([pos for row in context_rows for pos in row.get("root_positions") or []]),
        "point_position_summary": position_summary([pos for row in context_rows for pos in row.get("point_positions") or []]),
    }


def position_summary(values: list[int]) -> dict[str, Any]:
    values = sorted(int(value) for value in values)
    if not values:
        return {"count": 0}
    return {
        "count": len(values),
        "min": values[0],
        "median": values[len(values) // 2],
        "max": values[-1],
    }


def claim_status(validation: dict[str, Any]) -> str:
    if int_value(validation.get("root_mismatch_count")) or int_value(validation.get("point_match_mismatch_count")):
        return "SCOUT_POS7_PRE_ROWPOOL_STREAM_NEEDS_REVIEW"
    models = validation.get("model_summaries") if isinstance(validation.get("model_summaries"), dict) else {}
    direct_stop_count = int_value(validation.get("direct_stop_count"))
    for model in (
        "branch_point_full_scan_context_setup_integer",
        "branch_point_full_scan_context_setup_fractional",
        "branch_point_full_scan_cached_fractional",
        "root_stream_gate_positive_rowpool_integer",
        "root_stream_gate_positive_rowpool_fractional",
        "root_stream_gate_constructive_fractional",
        "branch_point_stream_context_setup_fractional",
        "branch_point_stream_cached_fractional",
    ):
        cost = (models.get(model) or {}).get("cost_per_rank_gain_stop_over_rho")
        rank_hits = int_value((models.get(model) or {}).get("rank_gain_stop_count"))
        precision = (models.get(model) or {}).get("precision")
        if cost is not None and float(cost) < 1.0 and rank_hits == direct_stop_count and rank_hits > 0 and precision == 1.0:
            return f"SCOUT_POS7_PRE_ROWPOOL_{model.upper()}_BELOW_RHO_WORK_ORDER"
    return "SCOUT_POS7_PRE_ROWPOOL_STREAM_STILL_ABOVE_RHO"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--direct-kernel", required=True)
    parser.add_argument("--calibration-end", type=int, default=4064)
    parser.add_argument("--target", default="22050.cf1@11731")
    parser.add_argument("--selector", default="mode_low_term_support_total5")
    parser.add_argument("--top-k", type=int, default=16)
    parser.add_argument("--min-transfer", type=int, default=3560)
    parser.add_argument("--target-leaf", type=int, default=65)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    direct_path = Path(args.direct_kernel)
    direct = load_json(direct_path)
    source_cache: dict[str, dict[str, Any]] = {}
    row_lookup_cache: dict[str, dict[tuple[int, tuple[str, ...]], dict[str, Any]]] = {}
    groups: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for group in direct.get("groups") or []:
        if not isinstance(group, dict) or not group.get("source_path"):
            continue
        source_path = Path(str(group.get("source_path")))
        source_key = str(source_path)
        source = source_cache.setdefault(source_key, load_json(source_path))
        lookup = row_lookup_cache.get(source_key)
        if lookup is None:
            lookup = source_row_lookup(source_path, source, args.target, args.selector, args.top_k, args.min_transfer)
            row_lookup_cache[source_key] = lookup
        stream_group, group_errors = collect_group(source_path, source, lookup, group, args.target_leaf)
        groups.append(stream_group)
        errors.extend(group_errors)

    groups.sort(key=lambda row: (int_value(row.get("window_start")), str(row.get("source_path"))))
    calibration_groups, validation_groups = split_groups(groups, args.calibration_end)
    summary = {
        "calibration": summarize(calibration_groups),
        "validation": summarize(validation_groups),
    }
    payload = {
        "artifacts": {
            "direct_kernel": str(direct_path),
        },
        "claim_status": claim_status(summary["validation"]),
        "cost_model_definitions": {
            "branch_point_full_scan_cached_fractional": "Streams every deterministic row and tests equality to the cached scout-7 branch point; charges fractional row work plus one relation-form op per point match.",
            "branch_point_full_scan_context_setup_fractional": "Full branch-point scan plus one branch setup op per context.",
            "branch_point_full_scan_context_setup_integer": "Full branch-point scan with row work rounded to row-pool units plus context branch setup.",
            "branch_point_stream_cached_fractional": "Streams rows only until the first branch-point hit in each context, or to exhaustion on no-hit contexts; assumes branch point is cached.",
            "branch_point_stream_context_setup_fractional": "First-hit branch-point stream plus one branch setup op per context.",
            "branch_point_stream_context_setup_integer": "First-hit branch-point stream with row work rounded to row-pool units plus context branch setup.",
            "root_stream_gate_constructive_fractional": "Streams rows until a leaf-65 root x-value is found or exhausted, then charges constructive leaf-65 work only on root-hit contexts.",
            "root_stream_gate_positive_rowpool_fractional": "Root stream plus constructive work and full row-pool charge only on root-hit contexts.",
            "root_stream_gate_positive_rowpool_integer": "Same as positive-rowpool root stream, but row-stream work is rounded to row-pool units.",
        },
        "created_at": now_iso(),
        "errors": errors,
        "groups": groups,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: contexts are replayed with the current builder; costs model a future streaming implementation rather than this script avoiding row construction.",
            "The branch and leaf side are cached/fixed only because the cacheability audit proved invariant fingerprints on this split.",
            "Fractional row-stream costs are row-order work normalized by row_factor; integer models show the conservative row-pool-unit boundary.",
            "A below-rho streaming ledger is an index-calculus precursor work order, not a deployed-curve ECDLP break.",
        ],
        "parameters": {
            "calibration_end": args.calibration_end,
            "min_transfer": args.min_transfer,
            "selector": args.selector,
            "target": args.target,
            "target_leaf": args.target_leaf,
            "top_k": args.top_k,
        },
        "schema": "ecdlp.low_term_total2_scout_pos7_pre_rowpool_root_intersection_probe.v1",
        "summary": summary,
    }
    write_json(Path(args.out), payload)
    print(
        json.dumps(
            {
                "claim_status": payload["claim_status"],
                "error_count": len(errors),
                "summary": payload["summary"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
