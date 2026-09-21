#!/usr/bin/env python3
"""Scan broader source-family support variants for known-column motifs.

The pressure-selected known-column family became degenerate: every validation
case had selected support (0,4,5,6,7,10,11,14,15).  The support scout artifacts
contain additional selectors/top-k/source policies with different selected
supports.  This probe scans a bounded, public order over those reports and asks
whether the broader source family creates relation-form motifs in windows where
the pressure family had no structural form.

This is still direct-source replay.  It charges skipped candidate source rows
and direct scans, but it is not yet a shared-product amortized collector.
"""

from __future__ import annotations

import argparse
import glob
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

from low_term_total2_known_column_motif_oracle_gap_scout import (
    case_supports,
    int_value,
    parse_motifs,
    stat,
    support_key,
)
from low_term_total2_known_column_pressure_direct_screen import (
    report_key,
    scan_case,
    source_case_key,
    source_cases,
)
from low_term_total2_known_factor_holdout_descent_probe import known_factors


WINDOW_RE = re.compile(r"(?:fixed_row_|selector_expanded_|col15_)(\d+)_(\d+)")
TARGETED_FULL_SUPPORT = (0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
TARGETED_HYBRID_SUPPORT = (0, 4, 5, 7, 10, 11, 14, 15)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_int_tuple(raw: str) -> tuple[int, ...]:
    return tuple(int(part.strip()) for part in raw.split(",") if part.strip())


def window_from_path(path: Path) -> str:
    match = WINDOW_RE.search(path.name)
    if not match:
        return ""
    return f"{int(match.group(1))}_{int(match.group(2))}"


def pair_support_count(selected_support: tuple[int, ...], motifs: set[tuple[int, ...]]) -> int:
    support = set(selected_support)
    return sum(1 for motif in motifs if set(motif).issubset(support))


def motif_column_count(selected_support: tuple[int, ...], motifs: set[tuple[int, ...]]) -> int:
    motif_cols = {col for motif in motifs for col in motif}
    return len(set(selected_support) & motif_cols)


def compact_attempts(case: dict[str, Any]) -> dict[str, Any]:
    motifs = case_supports(case)
    return {
        "hit": bool(case.get("public_known_factor_verified")),
        "known_structural_motifs": [list(motif) for motif in motifs["known_structural_motifs"]],
        "unknown_motifs": [list(motif) for motif in motifs["unknown_motifs"]],
        "verified_motifs": [list(motif) for motif in motifs["verified_motifs"]],
    }


def report_features(
    report: dict[str, Any],
    target_motifs: set[tuple[int, ...]],
    degenerate_support: tuple[int, ...],
) -> dict[str, Any]:
    selected_support = support_key(report.get("selected_term_support") or [])
    known_cols = tuple(col for col in selected_support if 7 <= col <= 14)
    return {
        "degenerate_pressure_support": selected_support == degenerate_support,
        "known_column_count": len(known_cols),
        "known_columns": list(known_cols),
        "motif_column_count": motif_column_count(selected_support, target_motifs),
        "motif_pair_visible_count": pair_support_count(selected_support, target_motifs),
        "selected_support": list(selected_support),
        "selected_support_size": len(selected_support),
    }


def diversity_order_key(report: dict[str, Any]) -> tuple[Any, ...]:
    features = report["expansion_features"]
    return (
        features["degenerate_pressure_support"],
        -int_value(features.get("motif_pair_visible_count")),
        -int_value(features.get("motif_column_count")),
        -int_value(features.get("known_column_count")),
        int_value(features.get("selected_support_size")),
        int_value(report.get("transfer_index")),
        int_value(report.get("top_k")),
        str(report.get("selector")),
        tuple(str(row) for row in report.get("row_keys") or []),
    )


def targeted_order_key(report: dict[str, Any]) -> tuple[Any, ...]:
    features = report["expansion_features"]
    selected_support = tuple(int_value(col) for col in features.get("selected_support") or [])
    selector = str(report.get("selector"))
    top_k = int_value(report.get("top_k"))
    if (
        selector == "mode_low_term_support_total5"
        and top_k == 16
        and selected_support == TARGETED_FULL_SUPPORT
    ):
        bucket = 0
    elif (
        selector == "mode_cost_hybrid_support_monic_b_total2"
        and top_k == 16
        and selected_support == TARGETED_HYBRID_SUPPORT
    ):
        bucket = 1
    elif selector == "mode_cost_hybrid_support_monic_b_total2" and selected_support == TARGETED_HYBRID_SUPPORT:
        bucket = 2
    elif top_k == 16 and selected_support == TARGETED_FULL_SUPPORT:
        bucket = 3
    else:
        bucket = 4
    return (
        bucket,
        -int_value(features.get("motif_pair_visible_count")),
        -int_value(features.get("motif_column_count")),
        int_value(features.get("selected_support_size")),
        int_value(report.get("transfer_index")),
        str(report.get("selector")),
        top_k,
        tuple(str(row) for row in report.get("row_keys") or []),
    )


def candidate_reports(
    support_payload: dict[str, Any],
    target: str,
    target_motifs: set[tuple[int, ...]],
    degenerate_support: tuple[int, ...],
    order_policy: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, int, str, int, tuple[str, ...]]] = set()
    for report in support_payload.get("case_reports") or []:
        if not isinstance(report, dict):
            continue
        if target and str(report.get("target")) != target:
            continue
        key = report_key(report)
        if key in seen:
            continue
        seen.add(key)
        features = report_features(report, target_motifs, degenerate_support)
        rows.append({**report, "expansion_features": features})
    if order_policy == "targeted":
        rows.sort(key=targeted_order_key)
    else:
        rows.sort(key=diversity_order_key)
    return rows


def compact_scan_case(report: dict[str, Any], scanned: dict[str, Any]) -> dict[str, Any]:
    motifs = compact_attempts(scanned)
    return {
        "case": {
            "direct_ops_over_rho": scanned.get("direct_ops_over_rho"),
            "known_support_form_count": scanned.get("known_support_form_count"),
            "public_known_factor_verified": scanned.get("public_known_factor_verified"),
            "recoverable_form_count": scanned.get("recoverable_form_count"),
            "scanned_form_count": scanned.get("scanned_form_count"),
            **motifs,
        },
        "public": {
            "features": report.get("expansion_features"),
            "row_keys": report.get("row_keys") or [],
            "selector": report.get("selector"),
            "top_k": int_value(report.get("top_k")),
            "transfer_index": int_value(report.get("transfer_index")),
        },
    }


def evaluate_window(
    source_path: Path,
    support_path: Path,
    known_by_order: dict[int, dict[int, int]],
    target: str,
    target_motifs: set[tuple[int, ...]],
    degenerate_support: tuple[int, ...],
    max_candidates: int,
    source_row_cost_over_rho: float,
    order_policy: str,
) -> dict[str, Any]:
    source_payload = load_json(source_path)
    support_payload = load_json(support_path)
    index: dict[tuple[str, int, str, int, tuple[str, ...]], list[dict[str, Any]]] = {}
    for case in source_cases(source_payload):
        index.setdefault(source_case_key(case), []).append(case)
    candidates = []
    for report in candidate_reports(support_payload, target, target_motifs, degenerate_support, order_policy):
        if report_key(report) in index:
            candidates.append(report)
    cost = 0.0
    scanned_count = 0
    source_rows = 0
    first_structural = None
    first_hit = None
    scanned_rows = []
    for report in candidates[:max_candidates]:
        source_rows += 1
        cost += source_row_cost_over_rho
        scanned = scan_case(source_payload, index, report, known_by_order)
        scanned_count += 1
        cost += float_value(scanned.get("direct_ops_over_rho"))
        row = compact_scan_case(report, scanned)
        scanned_rows.append(row)
        if first_structural is None and int_value(scanned.get("known_support_form_count")) > 0:
            first_structural = row
        if scanned.get("public_known_factor_verified"):
            first_hit = row
            break
    return {
        "candidate_count": len(candidates),
        "cost_over_rho": round(cost, 8),
        "hit": first_hit is not None,
        "hit_case": first_hit,
        "scanned_candidate_count": scanned_count,
        "scanned_rows": scanned_rows[:8],
        "selected_structural": first_structural is not None,
        "source_row_count": source_rows,
        "structural_case": first_structural,
        "support_report_count": len(support_payload.get("case_reports") or []),
        "window": window_from_path(support_path),
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    costs = [float_value(row.get("cost_over_rho")) for row in rows]
    hits = [row for row in rows if row.get("hit")]
    structural = [row for row in rows if row.get("selected_structural")]
    return {
        "cost_over_rho": stat(costs),
        "cost_per_hit_window_over_rho": round(sum(costs) / len(hits), 8) if hits else None,
        "cost_per_structural_window_over_rho": round(sum(costs) / len(structural), 8) if structural else None,
        "hit_window_count": len(hits),
        "scanned_candidate_count": sum(int_value(row.get("scanned_candidate_count")) for row in rows),
        "source_row_count": sum(int_value(row.get("source_row_count")) for row in rows),
        "structural_window_count": len(structural),
        "window_count": len(rows),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-glob", required=True)
    parser.add_argument("--support-glob", required=True)
    parser.add_argument("--training-audit", required=True)
    parser.add_argument("--target", default="22050.cf1@11731")
    parser.add_argument("--validation-start-min", type=int, default=3056)
    parser.add_argument("--validation-end-max", type=int, default=3303)
    parser.add_argument("--max-candidates-per-window", type=int, default=32)
    parser.add_argument("--order-policy", choices=["diversity", "targeted"], default="diversity")
    parser.add_argument("--source-row-cost-over-rho", type=float, default=1.0 / 137.0)
    parser.add_argument("--degenerate-support", default="0,4,5,6,7,10,11,14,15")
    parser.add_argument("--seed-known-motifs", default="8:11,9:11,10:13,10:14,11:13")
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sources = {window_from_path(Path(path)): Path(path) for path in glob.glob(args.source_glob)}
    supports = {window_from_path(Path(path)): Path(path) for path in glob.glob(args.support_glob)}
    training = load_json(Path(args.training_audit))
    known_by_order = known_factors(training)
    target_motifs = parse_motifs(args.seed_known_motifs)
    degenerate_support = parse_int_tuple(args.degenerate_support)
    rows = []
    for window in sorted(set(sources) & set(supports)):
        if not window:
            continue
        start, end = (int(part) for part in window.split("_"))
        if start < args.validation_start_min or end > args.validation_end_max:
            continue
        rows.append(
            evaluate_window(
                sources[window],
                supports[window],
                known_by_order,
                args.target,
                target_motifs,
                degenerate_support,
                args.max_candidates_per_window,
                args.source_row_cost_over_rho,
                args.order_policy,
            )
        )
    summary = summarize(rows)
    claim_status = (
        "SOURCE_FAMILY_EXPANSION_BELOW_RHO_CANDIDATE"
        if isinstance(summary.get("cost_per_hit_window_over_rho"), (int, float))
        and float(summary["cost_per_hit_window_over_rho"]) < 1.0
        else (
            "SOURCE_FAMILY_EXPANSION_RECOVERS_NEEDS_DENSITY_GAIN"
            if int_value(summary.get("hit_window_count")) > 0
            else "SOURCE_FAMILY_EXPANSION_NO_FORWARD_HIT"
        )
    )
    payload = {
        "claim_status": claim_status,
        "created_at": now_iso(),
        "degenerate_support": list(degenerate_support),
        "honesty_boundary": {
            "assumptions": [
                "Candidate reports come from existing source/support artifacts and are sorted by public selected-support diversity.",
                "Skipped candidates are charged with source_row_cost_over_rho, then selected candidates are direct-scanned.",
                "This expands selector/top-k/source-policy rows but is still direct-source replay, not shared-product amortized collection.",
            ],
            "evidence": "TOY-EVIDENCE / MODEL-BOUND / HEURISTIC-COST / SOURCE-FAMILY-SCOUT",
            "not_claimed": [
                "complete faster-than-rho prime-field ECDLP algorithm",
                "deployment-relevant attack",
                "shared-product source collector",
            ],
        },
        "parameters": {
            "max_candidates_per_window": args.max_candidates_per_window,
            "order_policy": args.order_policy,
            "seed_known_motifs": [list(motif) for motif in sorted(target_motifs)],
            "source_row_cost_over_rho": round(args.source_row_cost_over_rho, 8),
            "target": args.target,
            "validation_end_max": args.validation_end_max,
            "validation_start_min": args.validation_start_min,
        },
        "rows": rows,
        "schema": "ecdlp.low_term_total2_known_column_source_family_expansion_scout.v1",
        "summary": summary,
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": claim_status}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
