#!/usr/bin/env python3
"""Audit cacheability of the scout-7 branch micro-kernel inputs.

The branch micro-kernel cost scout showed below-rho headroom only after removing
both signed-pair setup and row-pool setup.  This audit asks whether those setup
costs are actually reusable across the current source groups.  It fingerprints
the first source-case contexts for:

* row pools;
* the scout-7 leaf polynomial;
* the scout-7 branch candidate point/input pair; and
* the row-side hit polynomial.

If these fingerprints are mostly unique, cache accounting is a lower bound
rather than an implementation path; the next positive move is a source policy
that directly constructs the scout-7 branch without generating the full
signed-pair/row-pool context.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from math import ceil
from pathlib import Path
from typing import Any

import frontier_signed_eval_cover_critical_leaf_probe as critical_leaf_probe
import low_term_total2_fixed_leaf_shared_product_timing_probe as timing_probe
from low_term_total2_auxiliary_relation_event_assembly_scout import label
from low_term_total2_scout_pos7_source_charged_collector import (
    int_value,
    load_json,
    source_cases,
    write_json,
)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stable_hash(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def row_pool_fingerprint(rows: list[dict[str, Any]]) -> str:
    return stable_hash(
        [
            {
                "trial": int_value(row.get("trial")),
                "x": int_value(row.get("x")),
                "y": int_value((row.get("point") or [0, 0])[1]) if isinstance(row.get("point"), (list, tuple)) else 0,
            }
            for row in rows
        ]
    )


def point_payload(point: Any) -> list[int] | None:
    if point is None:
        return None
    return [int(point[0]), int(point[1])]


def scout7_terms(scout: dict[str, Any]) -> bool:
    terms = [int_value(index) for index in scout.get("unsigned_indices") or []]
    return int_value(scout.get("scout_pos")) == 7 and label(terms) == "11,11,15,15"


def branch_scout_fingerprint(scout: dict[str, Any] | None) -> str:
    if not scout:
        return stable_hash({"missing": True})
    return stable_hash(
        {
            "left": point_payload((scout.get("left") or {}).get("point")),
            "right": point_payload((scout.get("right") or {}).get("point")),
            "scout_pos": int_value(scout.get("scout_pos")),
            "signed_terms": scout.get("signed_terms") or [],
            "unsigned_indices": [int_value(index) for index in scout.get("unsigned_indices") or []],
        }
    )


def context_profile(source_path: Path, window: str, window_start: int, source: dict[str, Any], row: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    profiles: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    try:
        _verifier, contexts, _product_factor, _max_relations = timing_probe.selected_contexts_from_source_case(source, row)
        for context_index, context in enumerate(contexts):
            built = context["built"]
            components = context["components"]
            scout_to_leaf = critical_leaf_probe.scout_leaf_map(components)
            scout7_leaf = int_value(scout_to_leaf.get(7), -1)
            scout7_leaf_poly = (components.get("leaves") or [{}])[scout7_leaf].get("poly") if scout7_leaf >= 0 else []
            branch_scouts = [scout for scout in built.get("scouts") or [] if scout7_terms(scout)]
            row_factor = max(1, int_value(getattr(context["local_args"], "row_factor", 1), 1))
            profiles.append(
                {
                    "branch_scout_count": len(branch_scouts),
                    "branch_scout_fingerprint": branch_scout_fingerprint(branch_scouts[0] if branch_scouts else None),
                    "context_index": context_index,
                    "generic_rho_steps": int_value(built.get("generic_rho_steps")),
                    "hit_poly_fingerprint": stable_hash(components.get("hit_poly") or []),
                    "row_key": str(context.get("row_key") or ""),
                    "row_pool": int_value(built.get("row_pool")),
                    "row_pool_fingerprint": row_pool_fingerprint(built.get("rows") or []),
                    "row_pool_ops": ceil(int_value(built.get("row_pool")) / row_factor),
                    "scout7_leaf": scout7_leaf,
                    "scout7_leaf_poly_fingerprint": stable_hash(scout7_leaf_poly or []),
                    "scout_seed_prefix": built.get("scout_seed_prefix"),
                    "selected_signed_pair_count": int_value(built.get("selected_signed_pair_count")),
                    "source_path": str(source_path),
                    "transfer_index": int_value(row.get("transfer_index")),
                    "window": window,
                    "window_start": window_start,
                }
            )
    except Exception as exc:  # noqa: BLE001 - preserve research replay failures.
        errors.append({"error": "cacheability_context_failed", "message": str(exc), "source_path": str(source_path)})
    return profiles, errors


def duplicate_summary(profiles: list[dict[str, Any]], key: str) -> dict[str, Any]:
    counts = Counter(str(profile.get(key)) for profile in profiles)
    duplicate_context_count = sum(count for count in counts.values() if count > 1)
    return {
        "duplicate_context_count": duplicate_context_count,
        "duplicate_fraction": round(duplicate_context_count / len(profiles), 8) if profiles else None,
        "max_multiplicity": max(counts.values()) if counts else 0,
        "unique_count": len(counts),
    }


def within_group_reuse(rows: list[dict[str, Any]], key: str) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(str(row.get("source_path")), []).append(row)
    reusable = 0
    total = 0
    for contexts in groups.values():
        if len(contexts) < 2:
            continue
        total += 1
        if len({str(context.get(key)) for context in contexts}) < len(contexts):
            reusable += 1
    return {
        "group_count_with_multiple_contexts": total,
        "reusable_group_count": reusable,
        "reusable_group_fraction": round(reusable / total, 8) if total else None,
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    keys = [
        "row_pool_fingerprint",
        "branch_scout_fingerprint",
        "scout7_leaf_poly_fingerprint",
        "hit_poly_fingerprint",
    ]
    row_pool_ops_sum = sum(int_value(row.get("row_pool_ops")) for row in rows)
    signed_pair_ops_sum = sum(int_value(row.get("selected_signed_pair_count")) for row in rows)
    return {
        "branch_scout_count_distribution": dict(sorted(Counter(int_value(row.get("branch_scout_count")) for row in rows).items())),
        "context_count": len(rows),
        "duplicate_summaries": {key: duplicate_summary(rows, key) for key in keys},
        "row_pool_ops_sum": row_pool_ops_sum,
        "scout7_leaf_distribution": dict(sorted(Counter(int_value(row.get("scout7_leaf")) for row in rows).items())),
        "selected_signed_pair_ops_sum": signed_pair_ops_sum,
        "within_group_reuse": {key: within_group_reuse(rows, key) for key in keys},
    }


def claim_status(summary: dict[str, Any]) -> str:
    duplicates = summary.get("duplicate_summaries") if isinstance(summary.get("duplicate_summaries"), dict) else {}
    row_pool = duplicates.get("row_pool_fingerprint") if isinstance(duplicates.get("row_pool_fingerprint"), dict) else {}
    branch = duplicates.get("branch_scout_fingerprint") if isinstance(duplicates.get("branch_scout_fingerprint"), dict) else {}
    if int_value(row_pool.get("duplicate_context_count")) == 0 and int_value(branch.get("duplicate_context_count")) == 0:
        return "SCOUT_POS7_BRANCH_NO_EXACT_CROSS_CONTEXT_CACHEABILITY"
    if int_value(row_pool.get("duplicate_context_count")) > 0 and int_value(branch.get("duplicate_context_count")) > 0:
        return "SCOUT_POS7_BRANCH_HAS_ROW_AND_BRANCH_CACHEABILITY_SIGNAL"
    return "SCOUT_POS7_BRANCH_HAS_PARTIAL_CACHEABILITY_SIGNAL"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collector", required=True)
    parser.add_argument("--calibration-end", type=int, default=3831)
    parser.add_argument("--target", default="22050.cf1@11731")
    parser.add_argument("--selector", default="mode_low_term_support_total5")
    parser.add_argument("--top-k", type=int, default=16)
    parser.add_argument("--min-transfer", type=int, default=3560)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    collector_path = Path(args.collector)
    collector = load_json(collector_path)
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for group in collector.get("groups") or []:
        if not isinstance(group, dict) or not group.get("source_path"):
            continue
        source_path = Path(str(group.get("source_path")))
        source = load_json(source_path)
        source_rows = source_cases(source_path, source, args.target, args.selector, args.top_k, args.min_transfer)
        if not source_rows:
            errors.append({"error": "missing_source_rows", "source_path": str(source_path)})
            continue
        profiles, profile_errors = context_profile(
            source_path,
            str(group.get("window") or ""),
            int_value(group.get("window_start")),
            source,
            source_rows[0],
        )
        for profile in profiles:
            profile.update(
                {
                    "accepted": bool(group.get("has_accepted_stop")),
                    "rank_gain": bool(group.get("has_rank_gain_stop")),
                }
            )
        rows.extend(profiles)
        errors.extend(profile_errors)

    calibration = [row for row in rows if int_value(row.get("window_start")) <= args.calibration_end]
    validation = [row for row in rows if int_value(row.get("window_start")) > args.calibration_end]
    full_summary = summarize(rows)
    payload = {
        "artifacts": {
            "collector": str(collector_path),
        },
        "claim_status": claim_status(full_summary),
        "created_at": now_iso(),
        "errors": errors,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: cacheability is exact fingerprint reuse in replayed first source-case contexts.",
            "No cache hit here does not rule out a new source policy that constructs the scout-7 branch directly.",
            "A cacheability signal would still need a measured implementation before being counted as a speedup.",
        ],
        "parameters": {
            "calibration_end": args.calibration_end,
            "min_transfer": args.min_transfer,
            "selector": args.selector,
            "target": args.target,
            "top_k": args.top_k,
        },
        "rows": rows,
        "schema": "ecdlp.low_term_total2_scout_pos7_branch_cacheability_audit.v1",
        "summary": {
            "all": full_summary,
            "calibration": summarize(calibration),
            "validation": summarize(validation),
        },
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
