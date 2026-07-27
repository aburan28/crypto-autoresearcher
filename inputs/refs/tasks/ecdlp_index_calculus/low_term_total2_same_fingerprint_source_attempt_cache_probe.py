#!/usr/bin/env python3
"""Audit same-fingerprint source-attempt cache gaps.

P228 left a precise fresh gap on 1144_1151: direct public QR total derives a
scalar below rho, but conservative source-attempt accounting is above rho by 13
operations.  This probe checks whether the charged rows share a full selected
factor fingerprint and selected leaf/root event, then models the narrow cache
that charges selector work per row but charges the source root scan once.

This is a cost-model audit.  It does not execute a new cached replay kernel.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = DEFAULT_STATE_DIR / "low_term_total2_same_fingerprint_source_attempt_cache_probe.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def int_value(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def float_value(value: Any, default: float = 10**12) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def public_rows_by_surface(data: dict[str, Any], policy: str) -> dict[str, dict[str, Any]]:
    rows = {}
    policy_rows = data.get("policy_rows") if isinstance(data.get("policy_rows"), dict) else {}
    for row in policy_rows.get(policy) or []:
        if isinstance(row, dict) and row.get("surface_id"):
            rows[str(row["surface_id"])] = row
    return rows


def stop_surface_ids(stop: dict[str, Any]) -> list[str]:
    surface_ids: list[str] = []
    materialized = stop.get("materialized_stop_summary") or {}
    for surface_id in materialized.get("surface_ids") or []:
        surface_ids.append(str(surface_id))
    if not surface_ids:
        for attempt in stop.get("charged_attempts") or []:
            if isinstance(attempt, dict) and attempt.get("surface_id"):
                surface_ids.append(str(attempt.get("surface_id")))
    return surface_ids


def all_summary_scalar_stops(data: dict[str, Any]) -> list[dict[str, Any]]:
    summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
    stops = []
    for kind in ("best_below_rho_stops", "best_scalar_stops"):
        for stop in summary.get(kind) or []:
            if isinstance(stop, dict):
                stops.append({"summary_stop_kind": kind, **stop})
    seen = set()
    unique = []
    for stop in stops:
        key = (
            str(stop.get("policy")),
            str(stop.get("order")),
            str(stop.get("target")),
            int_value(stop.get("transfer_index")),
            tuple(stop_surface_ids(stop)),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(stop)
    return unique


def compact_public_row(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(row, dict):
        return None
    candidate = row.get("chosen_candidate") if isinstance(row.get("chosen_candidate"), dict) else {}
    return {
        "surface_id": row.get("surface_id"),
        "row_key": row.get("row_key"),
        "target": row.get("target"),
        "transfer_index": row.get("transfer_index"),
        "selected_factor_hash": row.get("selected_factor_hash"),
        "selected_factor_fingerprint": row.get("selected_factor_fingerprint"),
        "selected_factor_coefficients": row.get("selected_factor_coefficients"),
        "candidate_name": candidate.get("candidate_name"),
        "factor_index": candidate.get("factor_index"),
        "factor_monomials": candidate.get("factor_monomials"),
        "selected_leaf_count": row.get("selected_leaf_count"),
        "factor_zero_leaf_indices": row.get("factor_zero_leaf_indices"),
        "selected_missed_leaf_count": row.get("selected_missed_leaf_count"),
        "selected_root_pair_count": row.get("selected_root_pair_count"),
        "recovered_root_count": row.get("recovered_root_count"),
        "quadratic_preserves_selected_root_pairs": row.get("quadratic_preserves_selected_root_pairs"),
        "chosen_false_positive_source": row.get("chosen_false_positive_source"),
        "public_factor_quadratic_root_ops": row.get("public_factor_quadratic_root_ops"),
        "public_factor_quadratic_root_ops_over_rho": row.get("public_factor_quadratic_root_ops_over_rho"),
        "source_charged_root_scan_ops": row.get("source_charged_root_scan_ops"),
        "source_charged_root_scan_ops_over_rho": row.get("source_charged_root_scan_ops_over_rho"),
    }


def event_signature(row: dict[str, Any] | None) -> tuple[Any, ...]:
    if not isinstance(row, dict):
        return ()
    return (
        tuple(row.get("selected_factor_fingerprint") or []),
        tuple(int_value(leaf) for leaf in row.get("factor_zero_leaf_indices") or []),
        int_value(row.get("selected_leaf_count")),
        int_value(row.get("selected_missed_leaf_count")),
        int_value(row.get("selected_root_pair_count")),
        int_value(row.get("recovered_root_count")),
    )


def audit_stop(
    stop: dict[str, Any],
    public_rows: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    attempts = [row for row in stop.get("charged_attempts") or [] if isinstance(row, dict)]
    surface_ids = stop_surface_ids(stop)
    matched_public_rows = [public_rows.get(surface_id) for surface_id in surface_ids]
    rho = int_value(stop.get("rho"))
    selector_ops = [int_value(row.get("selector_eval_ops")) for row in attempts]
    source_scan_ops = [int_value(row.get("source_factor_root_scan_ops")) for row in attempts]
    source_attempt_ops = [int_value(row.get("source_attempt_ops")) for row in attempts]
    public_qr_ops = [int_value(row.get("public_factor_quadratic_root_ops")) for row in attempts]
    current_ops = int_value(stop.get("charged_source_attempt_ops")) or sum(source_attempt_ops)
    selector_total = sum(selector_ops)
    source_scan_total = sum(source_scan_ops)
    source_scan_once_ops = max(source_scan_ops) if source_scan_ops else 0
    cached_ops = selector_total + source_scan_once_ops
    public_qr_total = int_value((stop.get("materialized_stop_summary") or {}).get("public_factor_quadratic_root_total_ops")) or sum(public_qr_ops)

    factor_hashes = {str((row or {}).get("selected_factor_hash")) for row in matched_public_rows if row}
    fingerprints = {
        json.dumps((row or {}).get("selected_factor_fingerprint") or [], sort_keys=True)
        for row in matched_public_rows
        if row
    }
    event_signatures = {
        json.dumps(event_signature(row), sort_keys=True)
        for row in matched_public_rows
        if row
    }
    same_full_fingerprint = len(fingerprints) == 1 and len(matched_public_rows) == len(surface_ids)
    same_factor_hash = len(factor_hashes) == 1 and len(matched_public_rows) == len(surface_ids)
    same_event = len(event_signatures) == 1 and len(matched_public_rows) == len(surface_ids)
    public_clean = all(
        bool(row)
        and bool(row.get("fingerprint_complete"))
        and bool(row.get("quadratic_preserves_selected_root_pairs"))
        and not bool(row.get("chosen_false_positive_source"))
        and int_value(row.get("selected_missed_leaf_count")) == 0
        for row in matched_public_rows
    )
    cache_applicable = bool(
        len(attempts) >= 2
        and bool(stop.get("stop_public_key_verified"))
        and same_factor_hash
        and same_full_fingerprint
        and same_event
        and public_clean
    )
    cached_beats = bool(cache_applicable and rho > 0 and cached_ops < rho)
    status = "SAME_FINGERPRINT_SOURCE_ATTEMPT_CACHE_NOT_APPLICABLE"
    if cache_applicable and cached_beats:
        status = "SAME_FINGERPRINT_SOURCE_ATTEMPT_CACHE_CLOSES_RHO_GAP"
    elif cache_applicable:
        status = "SAME_FINGERPRINT_SOURCE_ATTEMPT_CACHE_STILL_ABOVE_RHO"
    return {
        "status": status,
        "policy": stop.get("policy"),
        "order": stop.get("order"),
        "target": stop.get("target"),
        "transfer_index": int_value(stop.get("transfer_index")),
        "rho": rho,
        "row_count": len(attempts),
        "row_keys": [row.get("row_key") for row in attempts],
        "surface_ids": surface_ids,
        "stop_public_key_verified": bool(stop.get("stop_public_key_verified")),
        "stop_derived_secret": stop.get("stop_derived_secret"),
        "stop_union_rank": int_value(stop.get("stop_union_rank")),
        "stop_union_relation_count": int_value(stop.get("stop_union_relation_count")),
        "same_factor_hash": same_factor_hash,
        "same_full_fingerprint": same_full_fingerprint,
        "same_public_event_signature": same_event,
        "public_rows_clean": public_clean,
        "cache_applicable": cache_applicable,
        "current_source_attempt_ops": current_ops,
        "current_source_attempt_ops_over_rho": ratio(current_ops, rho),
        "public_qr_total_ops": public_qr_total,
        "public_qr_total_ops_over_rho": ratio(public_qr_total, rho),
        "selector_eval_total_ops": selector_total,
        "source_root_scan_total_ops": source_scan_total,
        "source_root_scan_once_ops": source_scan_once_ops,
        "cached_source_attempt_ops": cached_ops,
        "cached_source_attempt_ops_over_rho": ratio(cached_ops, rho),
        "cached_source_attempt_beats_rho": cached_beats,
        "savings_vs_current_source_attempt": current_ops - cached_ops,
        "extra_savings_needed_current": max(0, current_ops - max(0, rho - 1)) if rho else None,
        "extra_savings_needed_cached": max(0, cached_ops - max(0, rho - 1)) if rho else None,
        "attempt_rows": [
            {
                "row_key": row.get("row_key"),
                "surface_id": row.get("surface_id"),
                "selector_eval_ops": row.get("selector_eval_ops"),
                "source_factor_root_scan_ops": row.get("source_factor_root_scan_ops"),
                "source_attempt_ops": row.get("source_attempt_ops"),
                "public_factor_quadratic_root_ops": row.get("public_factor_quadratic_root_ops"),
            }
            for row in attempts
        ],
        "matched_public_rows": [compact_public_row(row) for row in matched_public_rows],
        "honesty_boundary": [
            "This is a cost-model audit over existing verified scalar stops.",
            "It charges selector work per row and charges only the source root scan once when full selected factor fingerprint and public event signature match.",
            "It does not execute a fresh cached replay kernel; a replay probe must reproduce the materialized rows before promotion.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--online-source", type=Path, required=True)
    parser.add_argument("--public-qr-source", type=Path, required=True)
    parser.add_argument("--policy", required=True)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    online = load_json(args.online_source)
    public = load_json(args.public_qr_source)
    public_rows = public_rows_by_surface(public, args.policy)
    stops = [stop for stop in all_summary_scalar_stops(online) if stop.get("policy") == args.policy]
    audits = [audit_stop(stop, public_rows) for stop in stops]
    audits.sort(
        key=lambda row: (
            not bool(row.get("cached_source_attempt_beats_rho")),
            int_value(row.get("cached_source_attempt_ops"), 10**12),
            int_value(row.get("current_source_attempt_ops"), 10**12),
        )
    )
    closed = [row for row in audits if row.get("cached_source_attempt_beats_rho")]
    output = {
        "schema": "ecdlp.low_term_total2_same_fingerprint_source_attempt_cache.v1",
        "method": "same_full_fingerprint_source_root_scan_once_cost_model",
        "parameters": {
            "online_source": str(args.online_source),
            "public_qr_source": str(args.public_qr_source),
            "policy": args.policy,
            "out": str(args.out),
        },
        "audits": audits,
        "summary": {
            "policy": args.policy,
            "audited_scalar_stop_count": len(audits),
            "cache_applicable_count": sum(1 for row in audits if row.get("cache_applicable")),
            "cached_below_rho_count": len(closed),
            "best_cached_stop": closed[0] if closed else (audits[0] if audits else None),
            "claim_status": (
                "SAME_FINGERPRINT_SOURCE_ATTEMPT_CACHE_COST_MODEL_CLOSES_GAP"
                if closed
                else "SAME_FINGERPRINT_SOURCE_ATTEMPT_CACHE_COST_MODEL_NO_CLOSE"
            ),
            "honesty_boundary": [
                "Cost-model only; no new cached verifier replay was executed.",
                "A promotion requires running a replay kernel that emits the same rows and secret.",
            ],
        },
    }
    write_json(args.out, output)
    print(json.dumps(output["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
