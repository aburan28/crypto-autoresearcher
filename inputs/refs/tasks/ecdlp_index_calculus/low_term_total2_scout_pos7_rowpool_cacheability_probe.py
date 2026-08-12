#!/usr/bin/env python3
"""Audit exact row-pool cacheability for the direct leaf-65 scout-7 kernel.

The selected-root gate model showed that avoiding row-pool work on zero-root
contexts would cross rho, but selected-root status is currently replay-derived.
This probe checks a more concrete route: exact row-pool reuse.  It reconstructs
the direct leaf-65 attempt stream, fingerprints each deterministic row pool and
the fixed leaf-65 branch inputs, and recharges row-pool setup once per exact
fingerprint in each split.

This is still a model-bound cache ledger, not a deployed implementation, but it
does not use rank or selected-root labels to decide which row pools to cache.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import frontier_signed_eval_cover_critical_leaf_probe as critical_leaf_probe
import low_term_total2_fixed_leaf_shared_product_timing_probe as timing_probe
from low_term_total2_scout_pos7_branch_cacheability_audit import branch_scout_fingerprint, row_pool_fingerprint
from low_term_total2_scout_pos7_direct_leaf65_kernel_probe import COST_MODELS as DIRECT_COST_MODELS
from low_term_total2_scout_pos7_direct_leaf65_kernel_probe import int_value, load_json, ratio, write_json
from low_term_total2_scout_pos7_source_charged_collector import canonical_rows, source_cases


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stable_hash(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def row_case_key(row: dict[str, Any]) -> tuple[int, tuple[str, ...]]:
    return int_value(row.get("transfer_index")), canonical_rows(row.get("row_keys"))


def attempt_key(attempt: dict[str, Any]) -> tuple[int, tuple[str, ...]]:
    return int_value(attempt.get("transfer_index")), canonical_rows(attempt.get("row_keys"))


def source_row_lookup(source_path: Path, source: dict[str, Any], target: str, selector: str, top_k: int, min_transfer: int) -> dict[tuple[int, tuple[str, ...]], dict[str, Any]]:
    return {
        row_case_key(row): row
        for row in source_cases(source_path, source, target, selector, top_k, min_transfer)
    }


def context_profiles_for_attempt(source: dict[str, Any], source_path: Path, row: dict[str, Any], attempt: dict[str, Any], target_leaf: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    profiles: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    try:
        _verifier, contexts, _product_factor, _max_relations = timing_probe.selected_contexts_from_source_case(source, row)
        for context_index, context in enumerate(contexts):
            built = context["built"]
            components = context["components"]
            scout_to_leaf = critical_leaf_probe.scout_leaf_map(components)
            scout7_leaf = int_value(scout_to_leaf.get(7), -1)
            leaf_poly = (components.get("leaves") or [{}])[target_leaf].get("poly") if 0 <= target_leaf < len(components.get("leaves") or []) else []
            branch_scouts = [
                scout
                for scout in built.get("scouts") or []
                if int_value(scout.get("scout_pos")) == 7
                and [int_value(index) for index in scout.get("unsigned_indices") or []] == [11, 11, 15, 15]
            ]
            direct_context = next(
                (
                    item
                    for item in attempt.get("context_rows") or []
                    if str(item.get("row_key")) == str(context.get("row_key"))
                ),
                {},
            )
            row_pool_hash = row_pool_fingerprint(built.get("rows") or [])
            profiles.append(
                {
                    "attempt_accepted": bool(attempt.get("accepted")),
                    "attempt_rank_gain": attempt.get("rank_gain"),
                    "branch_scout_fingerprint": branch_scout_fingerprint(branch_scouts[0] if branch_scouts else None),
                    "context_index": context_index,
                    "hit_poly_fingerprint": stable_hash(components.get("hit_poly") or []),
                    "leaf65_poly_fingerprint": stable_hash(leaf_poly or []),
                    "row_key": str(context.get("row_key") or ""),
                    "row_pool_fingerprint": row_pool_hash,
                    "row_pool_ops": int_value(direct_context.get("row_pool_ops"), 1),
                    "row_seed_prefix": str(getattr(context.get("local_args"), "row_seed_prefix", "")),
                    "scout7_leaf": scout7_leaf,
                    "selected_hit_roots": int_value(direct_context.get("selected_hit_roots")),
                    "source_path": str(source_path),
                    "transfer_index": int_value(row.get("transfer_index")),
                    "window_start": int_value(attempt.get("window_start")),
                }
            )
    except Exception as exc:  # noqa: BLE001 - audit should preserve replay failures.
        errors.append({"error": "context_profile_failed", "message": str(exc), "source_path": str(source_path), "transfer_index": int_value(row.get("transfer_index"))})
    return profiles, errors


def duplicate_summary(rows: list[dict[str, Any]], key: str) -> dict[str, Any]:
    counts = Counter(str(row.get(key)) for row in rows)
    duplicate_context_count = sum(count for count in counts.values() if count > 1)
    return {
        "duplicate_context_count": duplicate_context_count,
        "duplicate_fraction": ratio(duplicate_context_count, len(rows)),
        "max_multiplicity": max(counts.values()) if counts else 0,
        "unique_count": len(counts),
    }


def row_key_stability(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row.get("row_key"))].append(row)
    out = []
    for row_key, items in sorted(groups.items()):
        out.append(
            {
                "any_selected_root": any(int_value(item.get("selected_hit_roots")) > 0 for item in items),
                "context_count": len(items),
                "leaf65_poly_unique_count": len({str(item.get("leaf65_poly_fingerprint")) for item in items}),
                "row_key": row_key,
                "row_pool_unique_count": len({str(item.get("row_pool_fingerprint")) for item in items}),
                "row_seed_prefix_unique_count": len({str(item.get("row_seed_prefix")) for item in items}),
                "selected_hit_root_values": sorted({int_value(item.get("selected_hit_roots")) for item in items}),
            }
        )
    out.sort(key=lambda item: (-int_value(item.get("context_count")), str(item.get("row_key"))))
    return out


def split_profiles(rows: list[dict[str, Any]], calibration_end: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return (
        [row for row in rows if int_value(row.get("window_start")) <= calibration_end],
        [row for row in rows if int_value(row.get("window_start")) > calibration_end],
    )


def split_groups(groups: list[dict[str, Any]], calibration_end: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return (
        [group for group in groups if int_value(group.get("window_start")) <= calibration_end],
        [group for group in groups if int_value(group.get("window_start")) > calibration_end],
    )


def cached_rowpool_ops(rows: list[dict[str, Any]], key: str) -> int:
    charges: dict[str, int] = {}
    for row in rows:
        cache_key = str(row.get(key))
        charges.setdefault(cache_key, int_value(row.get("row_pool_ops"), 1))
    return sum(charges.values())


def summarize_profiles(rows: list[dict[str, Any]]) -> dict[str, Any]:
    keys = [
        "row_key",
        "row_seed_prefix",
        "row_pool_fingerprint",
        "leaf65_poly_fingerprint",
        "branch_scout_fingerprint",
        "hit_poly_fingerprint",
    ]
    return {
        "context_count": len(rows),
        "duplicate_summaries": {key: duplicate_summary(rows, key) for key in keys},
        "row_key_stability_top": row_key_stability(rows)[:20],
        "row_pool_ops_once_by_row_key": cached_rowpool_ops(rows, "row_key"),
        "row_pool_ops_once_by_row_pool_fingerprint": cached_rowpool_ops(rows, "row_pool_fingerprint"),
        "row_pool_ops_sum": sum(int_value(row.get("row_pool_ops")) for row in rows),
        "selected_root_context_count": sum(1 for row in rows if int_value(row.get("selected_hit_roots")) > 0),
    }


def summarize_costs(groups: list[dict[str, Any]], profiles: list[dict[str, Any]]) -> dict[str, Any]:
    rho = max([int_value(group.get("rho")) for group in groups if int_value(group.get("rho")) > 0] or [0])
    rank_hits = [group for group in groups if group.get("has_rank_gain_stop")]
    constructive_ops = sum(int_value(group.get("model_ops", {}).get("constructive_leaf65_kernel")) for group in groups)
    all_rowpool_ops = sum(int_value(row.get("row_pool_ops")) for row in profiles)
    cached_by_fingerprint = cached_rowpool_ops(profiles, "row_pool_fingerprint")
    cached_by_row_key = cached_rowpool_ops(profiles, "row_key")
    selected_root_rowpool = sum(int_value(row.get("row_pool_ops")) for row in profiles if int_value(row.get("selected_hit_roots")) > 0)
    models = {
        "constructive_leaf65_kernel": constructive_ops,
        "current_all_context_rowpool": constructive_ops + all_rowpool_ops,
        "exact_row_pool_fingerprint_cached": constructive_ops + cached_by_fingerprint,
        "row_key_cached_diagnostic": constructive_ops + cached_by_row_key,
        "selected_root_context_rowpool": constructive_ops + selected_root_rowpool,
    }
    return {
        "model_summaries": {
            name: {
                "cost_per_rank_gain_stop_over_rho": ratio(ops, rho * len(rank_hits)) if rank_hits and rho else None,
                "ops": ops,
                "ops_over_rho": ratio(ops, rho),
            }
            for name, ops in models.items()
        },
        "rank_gain_stop_count": len(rank_hits),
        "rho": rho,
    }


def claim_status(validation_costs: dict[str, Any]) -> str:
    models = validation_costs.get("model_summaries") if isinstance(validation_costs.get("model_summaries"), dict) else {}
    cached = (models.get("exact_row_pool_fingerprint_cached") or {}).get("cost_per_rank_gain_stop_over_rho")
    current = (models.get("current_all_context_rowpool") or {}).get("cost_per_rank_gain_stop_over_rho")
    if cached is not None and float(cached) < 1.0:
        return "SCOUT_POS7_ROWPOOL_EXACT_CACHE_BELOW_RHO_WORK_ORDER"
    if current is not None and float(current) < 1.0:
        return "SCOUT_POS7_ROWPOOL_CURRENT_BELOW_RHO"
    return "SCOUT_POS7_ROWPOOL_EXACT_CACHE_STILL_ABOVE_RHO"


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
    profiles: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for group in direct.get("groups") or []:
        source_path = Path(str(group.get("source_path")))
        source_key = str(source_path)
        source = source_cache.setdefault(source_key, load_json(source_path))
        lookup = row_lookup_cache.get(source_key)
        if lookup is None:
            lookup = source_row_lookup(source_path, source, args.target, args.selector, args.top_k, args.min_transfer)
            row_lookup_cache[source_key] = lookup
        for attempt in group.get("attempts") or []:
            row = lookup.get(attempt_key(attempt))
            if row is None:
                errors.append({"error": "missing_source_case_for_attempt", "source_path": source_key, "transfer_index": int_value(attempt.get("transfer_index"))})
                continue
            attempt_with_window = {**attempt, "window_start": int_value(group.get("window_start"))}
            attempt_profiles, attempt_errors = context_profiles_for_attempt(source, source_path, row, attempt_with_window, args.target_leaf)
            profiles.extend(attempt_profiles)
            errors.extend(attempt_errors)

    calibration_profiles, validation_profiles = split_profiles(profiles, args.calibration_end)
    calibration_groups, validation_groups = split_groups(direct.get("groups") or [], args.calibration_end)
    summary = {
        "calibration": {
            "cacheability": summarize_profiles(calibration_profiles),
            "costs": summarize_costs(calibration_groups, calibration_profiles),
        },
        "validation": {
            "cacheability": summarize_profiles(validation_profiles),
            "costs": summarize_costs(validation_groups, validation_profiles),
        },
    }
    payload = {
        "artifacts": {
            "direct_kernel": str(direct_path),
        },
        "claim_status": claim_status(summary["validation"]["costs"]),
        "created_at": now_iso(),
        "errors": errors,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: exact row-pool cache charge assumes row pools can be generated/stored once per deterministic fingerprint across the attempt stream.",
            "This does not avoid the first construction of each unique row pool and does not yet include an implemented cache in the collector.",
            "Rank and selected-root labels are used only for evaluation summaries, not to choose cache keys.",
        ],
        "parameters": {
            "calibration_end": args.calibration_end,
            "min_transfer": args.min_transfer,
            "selector": args.selector,
            "target": args.target,
            "target_leaf": args.target_leaf,
            "top_k": args.top_k,
        },
        "profiles": profiles,
        "schema": "ecdlp.low_term_total2_scout_pos7_rowpool_cacheability_probe.v1",
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
