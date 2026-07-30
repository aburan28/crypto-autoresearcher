#!/usr/bin/env python3
"""Charge a source-window collector for the ``scout_pos=7`` event clue.

The fresh direct-surface scout showed that accepted event ``scout_pos=7`` with
terms ``11,11,15,15`` remains a sparse rank-gain clue beyond transfer 3559.
This collector moves one step earlier in the pipeline: it scans public source
cases from the col15 selector-expanded artifacts, pays a source-row charge plus
direct replay cost for each attempted case, and stops per source artifact when
the event clause appears.

This is still not the final shared-product collector.  It intentionally charges
no-hit cases instead of assuming a free event oracle.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import glob
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_fixed_leaf_shared_product_timing_probe as timing_probe
from low_term_total2_auxiliary_relation_event_assembly_scout import (
    canonical_rows,
    direct_unique_events_with_rows,
    event_summary,
)


WINDOW_RE = re.compile(r"_(\d+)_(\d+)(?:_[^/]*)?_probe\.json$")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def parse_paths(raw: str) -> list[Path]:
    paths: list[Path] = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        matches = sorted(Path(path) for path in glob.glob(item))
        paths.extend(matches or [Path(item)])
    seen: set[str] = set()
    unique: list[Path] = []
    for path in paths:
        key = str(path)
        if key not in seen:
            seen.add(key)
            unique.append(path)
    return unique


def artifact_window(path: Path) -> tuple[int, int] | None:
    match = WINDOW_RE.search(path.name)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def case_key(source_path: Path, row: dict[str, Any]) -> tuple[str, str, int, str, int, tuple[str, ...]]:
    return (
        str(source_path),
        str(row.get("target")),
        int_value(row.get("transfer_index")),
        str(row.get("selector")),
        int_value(row.get("top_k")),
        canonical_rows(row.get("row_keys")),
    )


def cert_key(cert: dict[str, Any]) -> tuple[str, str, int, str, int, tuple[str, ...]]:
    selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
    return (
        str(cert.get("source") or ""),
        str(selected.get("target")),
        int_value(selected.get("transfer_index")),
        str(selected.get("selector")),
        int_value(selected.get("top_k")),
        canonical_rows(selected.get("row_keys")),
    )


def scorer_by_artifact(paths: list[Path]) -> dict[tuple[str, int], dict[str, Any]]:
    labels: dict[tuple[str, int], dict[str, Any]] = {}
    for path in paths:
        payload = load_json(path)
        for score in payload.get("scores") or []:
            if not isinstance(score, dict):
                continue
            candidate = score.get("candidate") if isinstance(score.get("candidate"), dict) else {}
            artifact = str(candidate.get("artifact") or "")
            offset = int_value(candidate.get("artifact_offset"), -1)
            if artifact and offset >= 0:
                labels[(artifact, offset)] = score
    return labels


def rank_labels_by_source_case(certificate_paths: list[Path], scorer_paths: list[Path]) -> dict[tuple[str, str, int, str, int, tuple[str, ...]], dict[str, Any]]:
    scorer_labels = scorer_by_artifact(scorer_paths)
    labels: dict[tuple[str, str, int, str, int, tuple[str, ...]], dict[str, Any]] = {}
    for path in certificate_paths:
        payload = load_json(path)
        for offset, cert in enumerate(payload.get("certificates") or []):
            if not isinstance(cert, dict):
                continue
            key = cert_key(cert)
            labels[key] = scorer_labels.get((str(path), offset), {})
    return labels


def source_cases(
    source_path: Path,
    source: dict[str, Any],
    target: str,
    selector: str,
    top_k: int,
    min_transfer: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, int, str, int, tuple[str, ...]]] = set()
    for policy_name, result in (source.get("policies") or {}).items():
        if not isinstance(result, dict):
            continue
        row_selector = (result.get("row_selector") or {}).get("selector")
        for row in result.get("stress_leaf_results") or []:
            if not isinstance(row, dict):
                continue
            transfer = int_value(row.get("transfer_index"), -1)
            if transfer < min_transfer:
                continue
            if str(row.get("target")) != target:
                continue
            if str(row.get("selector")) != selector:
                continue
            if int_value(row.get("top_k")) != top_k:
                continue
            dedupe = (
                str(row.get("target")),
                transfer,
                str(row.get("selector")),
                int_value(row.get("top_k")),
                canonical_rows(row.get("row_keys")),
            )
            if dedupe in seen:
                continue
            seen.add(dedupe)
            rows.append(
                {
                    **row,
                    "source_path": str(source_path),
                    "source_policy": policy_name,
                    "row_selector": row.get("row_selector") or row_selector,
                }
            )
    rows.sort(
        key=lambda row: (
            int_value(row.get("transfer_index")),
            int_value(row.get("selected_row_count")),
            int_value(row.get("selected_leaf_count")),
            canonical_rows(row.get("row_keys")),
            str(row.get("source_policy")),
        )
    )
    return rows


def has_event(events: list[dict[str, Any]], scout_pos: int, terms_label: str) -> bool:
    return any(
        int_value(event.get("scout_pos")) == scout_pos and str(event.get("terms_label")) == terms_label
        for event in events
    )


def support_multiset(events: list[dict[str, Any]]) -> str:
    return ";".join(sorted(str(event.get("factor_support_label")) for event in events))


def pos7_11111515_count(events: list[dict[str, Any]]) -> int:
    return sum(
        1
        for event in events
        if int_value(event.get("scout_pos")) == 7 and str(event.get("terms_label")) == "11,11,15,15"
    )


def source_prefilter_accepts(row: dict[str, Any], source_prefilter: str) -> bool:
    if source_prefilter == "none":
        return True
    if source_prefilter == "public_key_verified":
        return bool(row.get("public_key_verified"))
    raise ValueError(f"unknown source prefilter {source_prefilter!r}")


def attempt_accepts(attempt: dict[str, Any], accept_rule: str) -> bool:
    if accept_rule == "pos7_terms_11_11_15_15":
        return bool(attempt.get("has_scout_pos7_terms_11_11_15_15"))
    if accept_rule == "double_11_15":
        return str(attempt.get("support_multiset")) == "11,15;11,15"
    if accept_rule == "double_pos7_11_15":
        return (
            str(attempt.get("support_multiset")) == "11,15;11,15"
            and int_value(attempt.get("pos7_11111515_count")) >= 2
        )
    if accept_rule == "public_key_verified_pos7":
        return bool(attempt.get("public_key_verified")) and bool(attempt.get("has_scout_pos7_terms_11_11_15_15"))
    raise ValueError(f"unknown accept rule {accept_rule!r}")


def replay_case(
    source: dict[str, Any],
    source_path: Path,
    row: dict[str, Any],
    rank_labels: dict[tuple[str, str, int, str, int, tuple[str, ...]], dict[str, Any]],
    source_case_charge_ops: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    try:
        verifier, contexts, _product_factor, _max_relations = timing_probe.selected_contexts_from_source_case(source, row)
        direct_rows, direct_ops, rho, _profiles = timing_probe.direct_witness_rows(verifier, contexts)
        order = int_value((contexts[0]["built"] if contexts else {}).get("order"))
        events = [event_summary(event, form_index, order) for form_index, event in enumerate(direct_unique_events_with_rows(direct_rows))]
    except Exception as exc:  # noqa: BLE001 - research artifact should preserve replay failures.
        errors.append(
            {
                "error": "replay_failed",
                "message": str(exc),
                "source_path": str(source_path),
                "transfer_index": int_value(row.get("transfer_index")),
            }
        )
        direct_ops = 0
        rho = 0
        events = []
    key = case_key(source_path, row)
    score = rank_labels.get(key, {})
    charged_ops = source_case_charge_ops + direct_ops
    has_pos7_terms = has_event(events, 7, "11,11,15,15")
    has_pos8_terms = has_event(events, 8, "10,10,14,14")
    event_support_multiset = support_multiset(events)
    pos7_count = pos7_11111515_count(events)
    return (
        {
            "charged_ops": charged_ops,
            "charged_ops_over_rho": ratio(charged_ops, rho),
            "direct_ops": direct_ops,
            "direct_ops_over_rho": ratio(direct_ops, rho),
            "event_count": len(events),
            "events": events,
            "has_scout_pos7_terms_11_11_15_15": has_pos7_terms,
            "has_scout_pos8_terms_10_10_14_14": has_pos8_terms,
            "pos7_11111515_count": pos7_count,
            "public_key_verified": bool(row.get("public_key_verified")),
            "rank": int_value(row.get("rank")),
            "rank_gain": int_value(score.get("rank_gain")) if score else None,
            "rho": rho,
            "row_keys": row.get("row_keys") or [],
            "row_selector": row.get("row_selector"),
            "selector": row.get("selector"),
            "selected_leaf_count": int_value(row.get("selected_leaf_count")),
            "selected_row_count": int_value(row.get("selected_row_count")),
            "source_case_charge_ops": source_case_charge_ops,
            "source_ops_over_rho": ratio(source_case_charge_ops, rho),
            "source_path": str(source_path),
            "source_policy": row.get("source_policy"),
            "source_verified": bool(row.get("source_verified")),
            "support_multiset": event_support_multiset,
            "top_k": int_value(row.get("top_k")),
            "transfer_index": int_value(row.get("transfer_index")),
            "unique_factor_relation_gain": int_value(score.get("unique_factor_relation_gain")) if score else None,
        },
        errors,
    )


def collect_group(
    source_path: Path,
    source: dict[str, Any],
    rows: list[dict[str, Any]],
    rank_labels: dict[tuple[str, str, int, str, int, tuple[str, ...]], dict[str, Any]],
    source_case_charge_ops: int,
    accept_rule: str,
    source_prefilter: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    attempts: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for row in rows:
        if not source_prefilter_accepts(row, source_prefilter):
            continue
        attempt, attempt_errors = replay_case(source, source_path, row, rank_labels, source_case_charge_ops)
        attempt["accept_rule"] = accept_rule
        attempt["accepted"] = attempt_accepts(attempt, accept_rule)
        attempts.append(attempt)
        errors.extend(attempt_errors)
        if attempt["accepted"]:
            break
    window = artifact_window(source_path)
    total_charged = sum(int_value(attempt.get("charged_ops")) for attempt in attempts)
    rho_values = [int_value(attempt.get("rho")) for attempt in attempts if int_value(attempt.get("rho")) > 0]
    rho = max(rho_values) if rho_values else 0
    stop = attempts[-1] if attempts and attempts[-1].get("accepted") else None
    return (
        {
            "accept_rule": accept_rule,
            "attempt_count": len(attempts),
            "attempts": attempts,
            "charged_ops": total_charged,
            "charged_ops_over_rho": ratio(total_charged, rho),
            "has_accepted_stop": stop is not None,
            "has_event_stop": stop is not None,
            "has_rank_gain_stop": bool(stop and int_value(stop.get("rank_gain")) > 0),
            "rho": rho,
            "source_path": str(source_path),
            "source_prefilter": source_prefilter,
            "stop": stop,
            "window": f"{window[0]}_{window[1]}" if window else "",
            "window_start": window[0] if window else int_value(attempts[0].get("transfer_index")) if attempts else 0,
        },
        errors,
    )


def summarize(groups: list[dict[str, Any]]) -> dict[str, Any]:
    event_groups = [group for group in groups if group.get("has_accepted_stop")]
    rank_groups = [group for group in groups if group.get("has_rank_gain_stop")]
    charged = sum(int_value(group.get("charged_ops")) for group in groups)
    rho = max([int_value(group.get("rho")) for group in groups if int_value(group.get("rho")) > 0] or [0])
    return {
        "attempt_count": sum(int_value(group.get("attempt_count")) for group in groups),
        "charged_ops": charged,
        "charged_ops_over_rho": ratio(charged, rho),
        "cost_per_event_stop_over_rho": ratio(charged, rho * len(event_groups)) if event_groups and rho else None,
        "cost_per_rank_gain_stop_over_rho": ratio(charged, rho * len(rank_groups)) if rank_groups and rho else None,
        "accepted_stop_count": len(event_groups),
        "event_stop_count": len(event_groups),
        "group_count": len(groups),
        "rank_gain_stop_count": len(rank_groups),
    }


def split_groups(groups: list[dict[str, Any]], calibration_end: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return (
        [group for group in groups if int_value(group.get("window_start")) <= calibration_end],
        [group for group in groups if int_value(group.get("window_start")) > calibration_end],
    )


def claim_status(validation_summary: dict[str, Any]) -> str:
    rank_hits = int_value(validation_summary.get("rank_gain_stop_count"))
    cost = validation_summary.get("cost_per_rank_gain_stop_over_rho")
    if rank_hits <= 0:
        return "SCOUT_POS7_SOURCE_CHARGED_COLLECTOR_MISSES_VALIDATION_RANK_GAIN"
    if cost is not None and float_value(cost) < 1.0:
        return "SCOUT_POS7_SOURCE_CHARGED_COLLECTOR_BELOW_RHO_DIRECT_REPLAY_COST"
    return "SCOUT_POS7_SOURCE_CHARGED_COLLECTOR_ABOVE_RHO_NEEDS_CHEAPER_EVENT_TEST"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-glob",
        default="ecdlp_index_calculus_state/frontier_public_leaf_policy_p231_frozen_prefix_fixed_row_*_col15_selector_expanded_probe.json",
    )
    parser.add_argument(
        "--direct-cert-glob",
        default="ecdlp_index_calculus_state/low_term_total2_direct_relation_equation_certificate_22050_col15_lowterm_support5_*_probe.json",
    )
    parser.add_argument(
        "--rank-scorer-glob",
        default="ecdlp_index_calculus_state/low_term_total2_factor_rank_candidate_scorer_target67_22050_multibranch_plus_priority_hash6_plus_direct_col15_lowterm_support5_*_probe.json",
    )
    parser.add_argument("--target", default="22050.cf1@11731")
    parser.add_argument("--selector", default="mode_low_term_support_total5")
    parser.add_argument("--top-k", type=int, default=16)
    parser.add_argument("--min-transfer", type=int, default=3560)
    parser.add_argument("--calibration-end", type=int, default=3831)
    parser.add_argument("--source-case-charge-ops", type=int, default=1)
    parser.add_argument(
        "--accept-rule",
        choices=[
            "pos7_terms_11_11_15_15",
            "double_11_15",
            "double_pos7_11_15",
            "public_key_verified_pos7",
        ],
        default="pos7_terms_11_11_15_15",
    )
    parser.add_argument(
        "--source-prefilter",
        choices=["none", "public_key_verified"],
        default="none",
        help=(
            "Diagnostic only: public_key_verified is carried by source artifacts and "
            "may already reflect relation replay, so do not treat it as a cheap pretest."
        ),
    )
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_paths = [
        path
        for path in parse_paths(args.source_glob)
        if (window := artifact_window(path)) is not None and window[0] >= args.min_transfer
    ]
    certificate_paths = [
        path
        for path in parse_paths(args.direct_cert_glob)
        if (window := artifact_window(path)) is not None and window[0] >= args.min_transfer
    ]
    scorer_paths = [
        path
        for path in parse_paths(args.rank_scorer_glob)
        if (window := artifact_window(path)) is not None and window[0] >= args.min_transfer
    ]
    rank_labels = rank_labels_by_source_case(certificate_paths, scorer_paths)
    groups: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    rows_by_source_count: dict[str, int] = {}
    for source_path in source_paths:
        source = load_json(source_path)
        rows = source_cases(source_path, source, args.target, args.selector, args.top_k, args.min_transfer)
        rows_by_source_count[str(source_path)] = len(rows)
        if not rows:
            continue
        group, group_errors = collect_group(
            source_path,
            source,
            rows,
            rank_labels,
            args.source_case_charge_ops,
            args.accept_rule,
            args.source_prefilter,
        )
        groups.append(group)
        errors.extend(group_errors)
    groups.sort(key=lambda group: (int_value(group.get("window_start")), str(group.get("source_path"))))
    calibration, validation = split_groups(groups, args.calibration_end)
    calibration_summary = summarize(calibration)
    validation_summary = summarize(validation)
    payload = {
        "artifacts": {
            "direct_certificates": [str(path) for path in certificate_paths],
            "rank_scorers": [str(path) for path in scorer_paths],
            "source_paths": [str(path) for path in source_paths],
        },
        "claim_status": claim_status(validation_summary),
        "created_at": now_iso(),
        "errors": errors,
        "groups": groups,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: event detection uses direct verifier replay over public source cases.",
            "SOURCE-CHARGED DIRECT REPLAY: no-hit cases are charged, but this is not yet a shared-product implementation.",
            "A below-rho result here is a work order for a true shared-product/event-targeting collector, not a completed deployed-curve break.",
        ],
        "parameters": {
            "calibration_end": args.calibration_end,
            "accept_rule": args.accept_rule,
            "min_transfer": args.min_transfer,
            "selector": args.selector,
            "source_case_charge_ops": args.source_case_charge_ops,
            "source_prefilter": args.source_prefilter,
            "target": args.target,
            "top_k": args.top_k,
        },
        "rows_by_source_count": rows_by_source_count,
        "schema": "ecdlp.low_term_total2_scout_pos7_source_charged_collector.v1",
        "summary": {
            "calibration": calibration_summary,
            "validation": validation_summary,
        },
    }
    write_json(Path(args.out), payload)
    print(json.dumps({"claim_status": payload["claim_status"], "summary": payload["summary"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
