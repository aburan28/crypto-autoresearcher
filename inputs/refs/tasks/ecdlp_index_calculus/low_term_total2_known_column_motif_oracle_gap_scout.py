#!/usr/bin/env python3
"""Measure the gap between public pressure order and motif-targeted source generation.

The structural feature scout showed that scalar public predicates such as salt
thresholds overfit.  This probe moves the question one level closer to the
actual mathematical object: relation-form support motifs.

It learns known-column support motifs from calibration windows, treats motifs
seen only in unknown-factor attempts as avoid motifs, and evaluates later
windows under two models:

* current pressure order: the actual direct-source order already measured;
* motif oracle: an idealized source generator that can select the first case in
  a validation window whose relation scan contains a learned known motif.

The motif oracle is not a public algorithm.  It is a proof target and gap
measurement: if it is below rho while public predicates are not, the next
positive task is to construct a public generator for those motifs.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


WINDOW_RE = re.compile(r"_(\d+)_(\d+)_probe\.json$")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_paths(raw: str) -> list[Path]:
    return [Path(item.strip()) for item in raw.split(",") if item.strip()]


def parse_motif(raw: str) -> tuple[int, ...]:
    return tuple(int(item.strip()) for item in raw.split(":") if item.strip())


def parse_motifs(raw: str) -> set[tuple[int, ...]]:
    return {parse_motif(item) for item in raw.split(",") if item.strip()}


def window_from_path(path: Path) -> tuple[int, int]:
    match = WINDOW_RE.search(path.name)
    if not match:
        return (0, 0)
    return (int(match.group(1)), int(match.group(2)))


def support_key(values: list[Any] | tuple[Any, ...]) -> tuple[int, ...]:
    return tuple(sorted(int_value(value) for value in values))


def case_supports(case: dict[str, Any]) -> dict[str, Any]:
    known_structural: set[tuple[int, ...]] = set()
    verified: set[tuple[int, ...]] = set()
    unknown: set[tuple[int, ...]] = set()
    zero_target = 0
    empty = 0
    for attempt in case.get("attempts") or []:
        if not isinstance(attempt, dict):
            continue
        reason = str(attempt.get("reason") or "")
        support = support_key(attempt.get("support") or [])
        if attempt.get("recoverable"):
            known_structural.add(support)
            if attempt.get("public_key_verified"):
                verified.add(support)
        elif reason == "unknown_factor_support" and support:
            unknown.add(support)
        elif reason == "zero_target_coefficient":
            zero_target += 1
        elif reason in {"empty_factor_support", "empty_coefficients"}:
            empty += 1
    for attempt in case.get("verified_attempts") or []:
        if isinstance(attempt, dict):
            support = support_key(attempt.get("support") or [])
            if support:
                known_structural.add(support)
                verified.add(support)
    return {
        "known_structural_motifs": sorted(known_structural),
        "unknown_motifs": sorted(unknown),
        "verified_motifs": sorted(verified),
        "zero_target_attempt_count": zero_target,
        "empty_attempt_count": empty,
    }


def load_window(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    start, end = window_from_path(path)
    cases = []
    for index, case in enumerate(payload.get("case_results") or []):
        if not isinstance(case, dict):
            continue
        selected = case.get("selected") if isinstance(case.get("selected"), dict) else {}
        motifs = case_supports(case)
        cases.append(
            {
                "artifact": str(path),
                "case_index": index,
                "direct_ops_over_rho": case.get("direct_ops_over_rho"),
                "hit": bool(case.get("public_known_factor_verified")),
                "known_support_form_count": int_value(case.get("known_support_form_count")),
                **motifs,
                "row_keys": selected.get("row_keys") or [],
                "top_k": int_value(selected.get("top_k")),
                "transfer_index": int_value(selected.get("transfer_index")),
            }
        )
    return {
        "artifact": str(path),
        "end": end,
        "start": start,
        "summary": payload.get("summary") or {},
        "cases": cases,
    }


def motif_counts(windows: list[dict[str, Any]]) -> dict[str, Any]:
    known = Counter()
    verified = Counter()
    unknown = Counter()
    for window in windows:
        for case in window["cases"]:
            known.update(tuple(motif) for motif in case.get("known_structural_motifs") or [])
            verified.update(tuple(motif) for motif in case.get("verified_motifs") or [])
            unknown.update(tuple(motif) for motif in case.get("unknown_motifs") or [])
    return {
        "known_structural": motif_counter_rows(known),
        "unknown": motif_counter_rows(unknown),
        "verified": motif_counter_rows(verified),
    }


def motif_counter_rows(counter: Counter[tuple[int, ...]]) -> list[dict[str, Any]]:
    return [
        {"count": count, "motif": list(motif)}
        for motif, count in counter.most_common()
    ]


def compact_case(case: dict[str, Any] | None) -> dict[str, Any] | None:
    if case is None:
        return None
    return {
        "case_index": case.get("case_index"),
        "direct_ops_over_rho": case.get("direct_ops_over_rho"),
        "hit": case.get("hit"),
        "known_structural_motifs": [list(motif) for motif in case.get("known_structural_motifs") or []],
        "row_keys": case.get("row_keys"),
        "top_k": case.get("top_k"),
        "transfer_index": case.get("transfer_index"),
        "unknown_motifs": [list(motif) for motif in case.get("unknown_motifs") or []],
        "verified_motifs": [list(motif) for motif in case.get("verified_motifs") or []],
    }


def stat(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "min": None, "sum": 0.0}
    return {
        "count": len(values),
        "max": round(max(values), 8),
        "mean": round(mean(values), 8),
        "min": round(min(values), 8),
        "sum": round(sum(values), 8),
    }


def learned_motifs(
    calibration: list[dict[str, Any]],
    min_count: int,
    seed_motifs: set[tuple[int, ...]],
) -> tuple[set[tuple[int, ...]], set[tuple[int, ...]]]:
    known = Counter()
    verified = Counter()
    unknown = Counter()
    for window in calibration:
        for case in window["cases"]:
            known.update(tuple(motif) for motif in case.get("known_structural_motifs") or [])
            verified.update(tuple(motif) for motif in case.get("verified_motifs") or [])
            unknown.update(tuple(motif) for motif in case.get("unknown_motifs") or [])
    target = {
        motif
        for motif, count in known.items()
        if count >= min_count or verified.get(motif, 0) >= 1
    }
    target.update(seed_motifs)
    avoid = {motif for motif, count in unknown.items() if count >= min_count and motif not in target}
    return target, avoid


def case_has_any(case: dict[str, Any], field: str, motifs: set[tuple[int, ...]]) -> bool:
    if not motifs:
        return False
    return any(tuple(motif) in motifs for motif in case.get(field) or [])


def evaluate_current_pressure(windows: list[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    for window in windows:
        cost = 0.0
        scanned = 0
        hit_case = None
        for case in window["cases"]:
            scanned += 1
            cost += float_value(case.get("direct_ops_over_rho"))
            if case.get("hit"):
                hit_case = case
                break
        rows.append(
            {
                "cost_over_rho": round(cost, 8),
                "hit": hit_case is not None,
                "hit_case": compact_case(hit_case),
                "scanned_case_count": scanned,
                "window": f"{window['start']}_{window['end']}",
            }
        )
    return summarize_rows(rows)


def evaluate_motif_oracle(
    windows: list[dict[str, Any]],
    target_motifs: set[tuple[int, ...]],
    avoid_motifs: set[tuple[int, ...]],
) -> dict[str, Any]:
    rows = []
    for window in windows:
        selected_case = None
        rejected_avoid_only = 0
        for case in window["cases"]:
            has_target = (
                case_has_any(case, "known_structural_motifs", target_motifs)
                or case_has_any(case, "verified_motifs", target_motifs)
            )
            has_avoid = case_has_any(case, "unknown_motifs", avoid_motifs)
            has_known = bool(case.get("known_structural_motifs") or case.get("verified_motifs"))
            if has_target:
                selected_case = case
                break
            if has_avoid and not has_known:
                rejected_avoid_only += 1
        cost = float_value(selected_case.get("direct_ops_over_rho")) if selected_case else 0.0
        rows.append(
            {
                "cost_over_rho": round(cost, 8),
                "hit": bool(selected_case and selected_case.get("hit")),
                "rejected_avoid_only_count": rejected_avoid_only,
                "selected_case": compact_case(selected_case),
                "selected_structural": selected_case is not None,
                "window": f"{window['start']}_{window['end']}",
            }
        )
    return summarize_rows(rows)


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    hits = [row for row in rows if row.get("hit")]
    structural = [row for row in rows if row.get("selected_structural") or row.get("hit")]
    costs = [float_value(row.get("cost_over_rho")) for row in rows]
    total = sum(costs)
    return {
        "cost_over_rho": stat(costs),
        "cost_per_hit_window_over_rho": round(total / len(hits), 8) if hits else None,
        "cost_per_structural_window_over_rho": round(total / len(structural), 8) if structural else None,
        "hit_window_count": len(hits),
        "rows": rows,
        "structural_window_count": len(structural),
        "window_count": len(rows),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", required=True)
    parser.add_argument("--calibration-end-max", type=int, default=3055)
    parser.add_argument("--min-motif-count", type=int, default=2)
    parser.add_argument(
        "--seed-known-motifs",
        default="8:11,9:11,10:13,10:14,11:13",
        help="comma-separated motifs, each encoded with colon-separated columns",
    )
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = parse_paths(args.artifacts)
    windows = [load_window(path) for path in paths]
    calibration = [window for window in windows if int_value(window.get("end")) <= args.calibration_end_max]
    validation = [window for window in windows if int_value(window.get("end")) > args.calibration_end_max]
    target_motifs, avoid_motifs = learned_motifs(
        calibration,
        args.min_motif_count,
        parse_motifs(args.seed_known_motifs),
    )
    current = evaluate_current_pressure(validation)
    oracle = evaluate_motif_oracle(validation, target_motifs, avoid_motifs)
    oracle_cost = oracle.get("cost_per_hit_window_over_rho")
    current_cost = current.get("cost_per_hit_window_over_rho")
    if isinstance(oracle_cost, (int, float)) and oracle_cost < 1.0:
        claim_status = "MOTIF_ORACLE_BELOW_RHO_SOURCE_GENERATOR_TARGET"
    elif int_value(oracle.get("hit_window_count")) > 0:
        claim_status = "MOTIF_ORACLE_RECOVERS_NEEDS_DENSITY_GAIN"
    else:
        claim_status = "MOTIF_ORACLE_NO_FORWARD_HIT"
    payload = {
        "artifacts": [str(path) for path in paths],
        "calibration_end_max": args.calibration_end_max,
        "claim_status": claim_status,
        "created_at": now_iso(),
        "honesty_boundary": {
            "assumptions": [
                "Motif labels are derived from relation scans and are not public pre-scan features.",
                "The motif oracle is an idealized source-generator target, not an implemented algorithm.",
                "Operation costs use the current direct-source rho proxy.",
            ],
            "evidence": "TOY-EVIDENCE / MODEL-BOUND / ORACLE-GAP / HEURISTIC-COST",
            "not_claimed": [
                "complete faster-than-rho prime-field ECDLP algorithm",
                "public relation-support predictor",
                "shared-product/source-charged implementation",
            ],
        },
        "learned_motifs": {
            "avoid_motifs": [list(motif) for motif in sorted(avoid_motifs)],
            "min_motif_count": args.min_motif_count,
            "seed_known_motifs": [list(motif) for motif in sorted(parse_motifs(args.seed_known_motifs))],
            "target_motifs": [list(motif) for motif in sorted(target_motifs)],
        },
        "motif_counts": {
            "calibration": motif_counts(calibration),
            "validation": motif_counts(validation),
        },
        "schema": "ecdlp.low_term_total2_known_column_motif_oracle_gap_scout.v1",
        "selection_results": {
            "current_pressure_order": current,
            "motif_oracle": oracle,
        },
        "summary": {
            "current_cost_per_hit_window_over_rho": current_cost,
            "motif_oracle_cost_per_hit_window_over_rho": oracle_cost,
            "motif_oracle_gain_over_current": (
                round(float(current_cost) / float(oracle_cost), 8)
                if isinstance(current_cost, (int, float))
                and isinstance(oracle_cost, (int, float))
                and oracle_cost
                else None
            ),
        },
        "window_split": {
            "calibration": [f"{window['start']}_{window['end']}" for window in calibration],
            "validation": [f"{window['start']}_{window['end']}" for window in validation],
        },
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": claim_status}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
