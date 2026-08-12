#!/usr/bin/env python3
"""Test the ``scout_pos=7`` source-clause clue on fresh direct certificates.

The auxiliary event-assembly scout found that accepted event ``scout_pos=7``
isolates the post-relation ``[11, 15]`` auxiliary direction on the
``3056..3559`` known-factor export split.  This scout asks whether the same
event-level clause is useful on the later direct lowterm-support5 bridge
certificates.

This is not yet a full source-charged collector: the input direct-certificate
artifacts already contain public-verified direct-source cases.  Treat a
positive result here as a work order for the launcher/collector to measure
no-hit windows and shared-product costs.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import glob
import json
import re
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any

import low_term_total2_fixed_leaf_shared_product_timing_probe as timing_probe
from low_term_total2_auxiliary_relation_event_assembly_scout import (
    canonical_rows,
    direct_unique_events_with_rows,
    event_summary,
    source_case_index,
)


WINDOW_RE = re.compile(r"_(\d+)_(\d+)_probe\.json$")


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


def label(values: Any) -> str:
    if not isinstance(values, list):
        return "none"
    return ",".join(str(int_value(value)) for value in values)


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


def window_from_path(path: Path) -> str:
    match = WINDOW_RE.search(path.name)
    if not match:
        return ""
    return f"{int(match.group(1))}_{int(match.group(2))}"


def window_start(window: str) -> int:
    try:
        return int(str(window).split("_", 1)[0])
    except (TypeError, ValueError):
        return 0


def cert_window_start(cert: dict[str, Any]) -> int:
    selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
    transfer = int_value(selected.get("transfer_index"), -1)
    if transfer >= 0:
        return transfer
    return window_start(str(cert.get("window") or ""))


def artifact_window_range(path: Path) -> tuple[int, int] | None:
    window = window_from_path(path)
    if not window:
        return None
    start, end = window.split("_", 1)
    return int(start), int(end)


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


def event_support_set(events: list[dict[str, Any]]) -> set[str]:
    return {str(event.get("factor_support_label")) for event in events}


def scout_positions(events: list[dict[str, Any]]) -> set[int]:
    return {int_value(event.get("scout_pos")) for event in events}


def event_terms(events: list[dict[str, Any]]) -> set[str]:
    return {str(event.get("terms_label")) for event in events}


def bucket_features(name: str, value: int, thresholds: tuple[int, ...]) -> set[str]:
    features = {f"{name}={value}"}
    for threshold in thresholds:
        if value <= threshold:
            features.add(f"{name}<={threshold}")
        if value >= threshold:
            features.add(f"{name}>={threshold}")
    return features


def row_features(cert: dict[str, Any], events: list[dict[str, Any]], include_relation_support: bool) -> set[str]:
    selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
    positions = scout_positions(events)
    terms = event_terms(events)
    features: set[str] = {
        f"selector={selected.get('selector')}",
        f"topk={int_value(selected.get('top_k'))}",
        f"scout_pos_set={label(sorted(positions))}",
        f"event_terms_set={';'.join(sorted(terms)) if terms else 'none'}",
    }
    for position in sorted(positions):
        features.add(f"has_scout_pos={position}")
    for term_label in sorted(terms):
        features.add(f"has_event_terms={term_label}")
    if 7 in positions:
        features.add("has_scout_pos7")
    if 8 in positions:
        features.add("has_scout_pos8")
    if {7, 8} <= positions:
        features.add("has_scout_pos7_and8")
    if any(int_value(event.get("scout_pos")) == 7 and str(event.get("terms_label")) == "11,11,15,15" for event in events):
        features.add("has_scout_pos7_terms_11_11_15_15")
    if any(int_value(event.get("scout_pos")) == 8 and str(event.get("terms_label")) == "10,10,14,14" for event in events):
        features.add("has_scout_pos8_terms_10_10_14_14")
    if (
        any(int_value(event.get("scout_pos")) == 7 and str(event.get("terms_label")) == "11,11,15,15" for event in events)
        and any(int_value(event.get("scout_pos")) == 8 and str(event.get("terms_label")) == "10,10,14,14" for event in events)
    ):
        features.add("has_scout7_11_15_and_scout8_10_14")
    features.update(bucket_features("event_count", len(events), (1, 2, 3, 4, 5)))
    features.update(bucket_features("forms_count", int_value(cert.get("forms_count")), (1, 2, 3, 4, 5)))
    if include_relation_support:
        support_set = event_support_set(events)
        features.add(f"factor_support_set={';'.join(sorted(support_set)) if support_set else 'none'}")
        for support in sorted(support_set):
            features.add(f"factor_support={support}")
        if "11,15" in support_set:
            features.add("has_factor_support_11_15")
    return features


def target_rule_names(include_relation_support: bool) -> list[str]:
    rules = [
        "has_scout_pos7",
        "has_scout_pos=7",
        "has_scout_pos7_terms_11_11_15_15",
        "has_event_terms=11,11,15,15",
        "has_scout_pos8",
        "has_scout_pos=8",
        "has_scout_pos8_terms_10_10_14_14",
        "has_event_terms=10,10,14,14",
        "has_scout_pos7_and8",
        "has_scout7_11_15_and_scout8_10_14",
        "topk=16",
        "event_count=2|topk=16",
    ]
    if include_relation_support:
        rules.extend(
            [
                "has_factor_support_11_15",
                "factor_support=11,15",
                "factor_support=11,15|has_scout_pos7",
                "factor_support=11,15|has_scout_pos7_terms_11_11_15_15",
            ]
        )
    return rules


def conjunctions(features: set[str], max_size: int) -> set[str]:
    ordered = sorted(features)
    result = set(ordered)
    for size in range(2, max_size + 1):
        for combo in combinations(ordered, size):
            result.add("|".join(combo))
    return result


def load_rows(
    certificate_paths: list[Path],
    scorer_labels: dict[tuple[str, int], dict[str, Any]],
    include_relation_support: bool,
    max_conjunction_size: int,
    min_transfer: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    source_cache: dict[Path, dict[str, Any]] = {}
    source_index_cache: dict[Path, dict[tuple[str, int, str, int, tuple[str, ...]], dict[str, Any]]] = {}
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for cert_path in certificate_paths:
        payload = load_json(cert_path)
        for offset, cert in enumerate(payload.get("certificates") or []):
            if not isinstance(cert, dict):
                continue
            transfer = cert_window_start(cert)
            if transfer < min_transfer:
                continue
            selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
            source_path = Path(str(cert.get("source") or ""))
            if not source_path.exists():
                errors.append({"artifact": str(cert_path), "artifact_offset": offset, "error": "missing_source"})
                continue
            if source_path not in source_cache:
                source_cache[source_path] = load_json(source_path)
                source_index_cache[source_path] = source_case_index(source_cache[source_path])
            key = (
                str(selected.get("target")),
                int_value(selected.get("transfer_index")),
                str(selected.get("selector")),
                int_value(selected.get("top_k")),
                canonical_rows(selected.get("row_keys")),
            )
            source_case = source_index_cache[source_path].get(key)
            if source_case is None:
                errors.append({"artifact": str(cert_path), "artifact_offset": offset, "error": "missing_exact_source_case", "key": list(key)})
                continue
            verifier, contexts, _product_factor, _max_relations = timing_probe.selected_contexts_from_source_case(
                source_cache[source_path],
                source_case,
            )
            direct_rows, direct_ops, rho, _profiles = timing_probe.direct_witness_rows(verifier, contexts)
            events_raw = direct_unique_events_with_rows(direct_rows)
            order = int_value((contexts[0]["built"] if contexts else {}).get("order"))
            events = [event_summary(event, form_index, order) for form_index, event in enumerate(events_raw)]
            positions = scout_positions(events)
            terms = event_terms(events)
            has_pos7_terms = any(
                int_value(event.get("scout_pos")) == 7 and str(event.get("terms_label")) == "11,11,15,15" for event in events
            )
            has_pos8_terms = any(
                int_value(event.get("scout_pos")) == 8 and str(event.get("terms_label")) == "10,10,14,14" for event in events
            )
            score = scorer_labels.get((str(cert_path), offset), {})
            rank_gain = int_value(score.get("rank_gain"))
            unique_gain = int_value(score.get("unique_factor_relation_gain"))
            cost = float_value(selected.get("direct_ops_over_rho"))
            row = {
                "artifact": str(cert_path),
                "artifact_offset": offset,
                "cost_over_rho": cost,
                "events": events,
                "features": conjunctions(row_features(cert, events, include_relation_support), max_conjunction_size),
                "has_scout_pos7": 7 in positions,
                "has_scout7_11_15_and_scout8_10_14": has_pos7_terms and has_pos8_terms,
                "rank_gain": rank_gain,
                "row": {
                    "artifact": str(cert_path),
                    "artifact_offset": offset,
                    "direct_ops_over_rho": selected.get("direct_ops_over_rho"),
                    "event_count": len(events),
                    "events": events,
                    "event_terms_set": sorted(terms),
                    "factor_supports": sorted(event_support_set(events)),
                    "forms_count": int_value(cert.get("forms_count")),
                    "has_scout_pos7": 7 in positions,
                    "has_scout_pos7_terms_11_11_15_15": has_pos7_terms,
                    "has_scout_pos8": 8 in positions,
                    "has_scout_pos8_terms_10_10_14_14": has_pos8_terms,
                    "has_scout7_11_15_and_scout8_10_14": has_pos7_terms and has_pos8_terms,
                    "rank": int_value(cert.get("rank")),
                    "rank_gain": rank_gain,
                    "scout_pos_set": sorted(positions),
                    "selector": selected.get("selector"),
                    "top_k": int_value(selected.get("top_k")),
                    "transfer_index": transfer,
                    "unique_factor_relation_gain": unique_gain,
                    "window": cert.get("window"),
                },
                "transfer_index": transfer,
            }
            rows.append(row)
    return sorted(rows, key=lambda item: (int_value(item.get("transfer_index")), str(item.get("artifact")), int_value(item.get("artifact_offset")))), errors


def split_rows(rows: list[dict[str, Any]], calibration_end: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return (
        [row for row in rows if int_value(row.get("transfer_index")) <= calibration_end],
        [row for row in rows if int_value(row.get("transfer_index")) > calibration_end],
    )


def is_positive(row: dict[str, Any], label_name: str) -> bool:
    if label_name == "rank_gain":
        return int_value(row.get("rank_gain")) > 0
    if label_name == "scout_pos7":
        return bool(row.get("has_scout_pos7"))
    if label_name == "scout7_11_15_and_scout8_10_14":
        return bool(row.get("has_scout7_11_15_and_scout8_10_14"))
    raise ValueError(f"unknown label {label_name!r}")


def evaluate_rule(rule: str, rows: list[dict[str, Any]], label_name: str) -> dict[str, Any]:
    selected = [row for row in rows if rule in row["features"]]
    positives = [row for row in selected if is_positive(row, label_name)]
    cost = sum(float_value(row.get("cost_over_rho")) for row in selected)
    return {
        "cost_over_rho": round(cost, 8),
        "cost_per_positive_over_rho": round(cost / len(positives), 8) if positives else None,
        "positive_count": len(positives),
        "precision": round(len(positives) / len(selected), 8) if selected else None,
        "selected_count": len(selected),
        "selected_rows": [row["row"] for row in selected],
    }


def choose_rules(
    calibration: list[dict[str, Any]],
    validation: list[dict[str, Any]],
    label_name: str,
    min_calibration_hits: int,
    min_calibration_precision: float,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for rule in sorted({feature for row in calibration for feature in row["features"]}):
        calibration_eval = evaluate_rule(rule, calibration, label_name)
        if int_value(calibration_eval.get("positive_count")) < min_calibration_hits:
            continue
        precision = calibration_eval.get("precision")
        if precision is None or float(precision) < min_calibration_precision:
            continue
        validation_eval = evaluate_rule(rule, validation, label_name)
        candidates.append(
            {
                "calibration": calibration_eval,
                "feature_count": rule.count("|") + 1,
                "rule": rule,
                "validation": validation_eval,
            }
        )
    candidates.sort(
        key=lambda item: (
            -float(item["calibration"].get("precision") or 0.0),
            -int_value(item["calibration"].get("positive_count")),
            int_value(item.get("feature_count")),
            float(item["calibration"].get("cost_per_positive_over_rho") or 999999.0),
            str(item.get("rule")),
        )
    )
    return candidates


def claim_status(selected: dict[str, Any] | None) -> str:
    if selected is None:
        return "SCOUT_POS7_SOURCE_CLAUSE_NO_VIABLE_CALIBRATION"
    validation = selected.get("validation") if isinstance(selected.get("validation"), dict) else {}
    positives = int_value(validation.get("positive_count"))
    cost = validation.get("cost_per_positive_over_rho")
    if positives <= 0:
        return "SCOUT_POS7_SOURCE_CLAUSE_MISSES_VALIDATION"
    if cost is not None and float_value(cost) < 1.0:
        return "SCOUT_POS7_SOURCE_CLAUSE_VALIDATES_BELOW_RHO_DIRECT_SURFACE"
    return "SCOUT_POS7_SOURCE_CLAUSE_VALIDATES_ABOVE_RHO_OR_BROAD_DIRECT_SURFACE"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--certificate-glob",
        default="ecdlp_index_calculus_state/low_term_total2_direct_relation_equation_certificate_22050_col15_lowterm_support5_*_probe.json",
    )
    parser.add_argument(
        "--scorer-glob",
        default="ecdlp_index_calculus_state/low_term_total2_factor_rank_candidate_scorer_target67_22050_multibranch_plus_priority_hash6_plus_direct_col15_lowterm_support5_*_probe.json",
    )
    parser.add_argument("--min-transfer", type=int, default=3560)
    parser.add_argument("--calibration-end", type=int, default=3831)
    parser.add_argument("--label", choices=["rank_gain", "scout_pos7", "scout7_11_15_and_scout8_10_14"], default="rank_gain")
    parser.add_argument("--max-conjunction-size", type=int, default=2)
    parser.add_argument("--min-calibration-hits", type=int, default=2)
    parser.add_argument("--min-calibration-precision", type=float, default=0.5)
    parser.add_argument("--include-relation-support", action="store_true")
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    certificate_paths = [
        path
        for path in parse_paths(args.certificate_glob)
        if (window := artifact_window_range(path)) is not None and window[0] >= args.min_transfer
    ]
    scorer_paths = [
        path
        for path in parse_paths(args.scorer_glob)
        if (window := artifact_window_range(path)) is not None and window[0] >= args.min_transfer
    ]
    labels = scorer_by_artifact(scorer_paths)
    rows, errors = load_rows(
        certificate_paths,
        labels,
        args.include_relation_support,
        args.max_conjunction_size,
        args.min_transfer,
    )
    calibration, validation = split_rows(rows, args.calibration_end)
    rules = choose_rules(
        calibration,
        validation,
        args.label,
        args.min_calibration_hits,
        args.min_calibration_precision,
    )
    selected = rules[0] if rules else None
    target_rule_evaluations = {
        rule: {
            "calibration": evaluate_rule(rule, calibration, args.label),
            "feature_count": rule.count("|") + 1,
            "rule": rule,
            "validation": evaluate_rule(rule, validation, args.label),
        }
        for rule in target_rule_names(args.include_relation_support)
    }
    payload = {
        "artifacts": {
            "certificate_glob": args.certificate_glob,
            "certificate_paths": [str(path) for path in certificate_paths],
            "scorer_glob": args.scorer_glob,
            "scorer_paths": [str(path) for path in scorer_paths],
        },
        "claim_status": claim_status(selected),
        "created_at": now_iso(),
        "errors": errors,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: rows are public-verified direct-source lowterm-support5 certificates.",
            "DIRECT-SURFACE ONLY: no-hit source windows and shared-product amortization are not fully charged here.",
            "A validating rule is a work order for a launcher-level source-clause collector, not a completed faster-than-rho algorithm.",
        ],
        "parameters": {
            "calibration_end": args.calibration_end,
            "include_relation_support": args.include_relation_support,
            "label": args.label,
            "max_conjunction_size": args.max_conjunction_size,
            "min_calibration_hits": args.min_calibration_hits,
            "min_calibration_precision": args.min_calibration_precision,
            "min_transfer": args.min_transfer,
        },
        "rows": [row["row"] for row in rows],
        "rules": rules[:20],
        "selected_rule": selected,
        "split_summary": {
            "calibration_positive_count": sum(1 for row in calibration if is_positive(row, args.label)),
            "calibration_row_count": len(calibration),
            "validation_positive_count": sum(1 for row in validation if is_positive(row, args.label)),
            "validation_row_count": len(validation),
        },
        "target_rule_evaluations": target_rule_evaluations,
        "schema": "ecdlp.low_term_total2_scout_pos7_source_clause_fresh_scout.v1",
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["split_summary"], indent=2, sort_keys=True))
    print(
        json.dumps(
            {
                "claim_status": payload["claim_status"],
                "error_count": len(errors),
                "selected_rule": selected["rule"] if selected else None,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
