#!/usr/bin/env python3
"""Map accepted relation-event assembly for the auxiliary ``[11, 15]`` form.

The selected-leaf precursor scout showed that public leaf-term visibility is
too broad: the held-out ``[11, 15]`` auxiliary row and its controls expose the
same full selected term support.  This scout moves one step later in the
pipeline, but still records the exact event provenance that builds each
accepted relation form:

* selected source case and row key;
* accepted relation event leaf/scout/candidate/trial metadata;
* candidate term set before the compact relation support is read; and
* compact factor support label after relation-form construction.

Features that include compact factor support are post-relation diagnostics.
Features that use only event position, leaf index, candidate terms, and row
metadata are source-construction clues that still need source-charged
validation.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any

import low_term_total2_fixed_leaf_shared_product_timing_probe as timing_probe
from low_term_total2_known_column_pressure_direct_screen import (
    report_key,
    source_case_key,
    source_cases,
)
from low_term_total2_source_relation_equation_certificate import compact_form


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


def window_start(window: str) -> int:
    try:
        return int(str(window).split("_", 1)[0])
    except (TypeError, ValueError):
        return 0


def canonical_rows(row_keys: Any) -> tuple[str, ...]:
    if not isinstance(row_keys, list):
        return tuple()
    return tuple(sorted(str(row) for row in row_keys))


def salt_from_row_key(row_key: str) -> int:
    if "salt" not in row_key:
        return -1
    try:
        return int(row_key.rsplit("salt", 1)[1])
    except ValueError:
        return -1


def bucket_features(name: str, value: int, thresholds: tuple[int, ...]) -> set[str]:
    features = {f"{name}={value}"}
    for threshold in thresholds:
        if value <= threshold:
            features.add(f"{name}<={threshold}")
        if value >= threshold:
            features.add(f"{name}>={threshold}")
    return features


def term_shape(terms: list[int]) -> str:
    counts = sorted(Counter(terms).values(), reverse=True)
    return "+".join(str(count) for count in counts) if counts else "empty"


def support_from_compact(form: dict[str, Any]) -> list[int]:
    coeffs = form.get("coeffs")
    if not isinstance(coeffs, list):
        return []
    return [index for index, value in enumerate(coeffs[1:]) if int_value(value) != 0]


def scorer_labels(payload: dict[str, Any]) -> dict[int, dict[str, Any]]:
    labels_by_offset: dict[int, dict[str, Any]] = {}
    for score in payload.get("scores") or []:
        if not isinstance(score, dict):
            continue
        candidate = score.get("candidate") if isinstance(score.get("candidate"), dict) else {}
        offset = int_value(candidate.get("artifact_offset"), -1)
        if offset < 0:
            continue
        labels_by_offset[offset] = {
            "rank_gain": int_value(score.get("rank_gain")),
            "unique_factor_relation_gain": int_value(score.get("unique_factor_relation_gain")),
        }
    return labels_by_offset


def source_case_index(payload: dict[str, Any]) -> dict[tuple[str, int, str, int, tuple[str, ...]], dict[str, Any]]:
    rows: dict[tuple[str, int, str, int, tuple[str, ...]], dict[str, Any]] = {}
    for case in source_cases(payload):
        rows.setdefault(source_case_key(case), case)
    return rows


def support_report_index(payload: dict[str, Any]) -> dict[tuple[str, int, str, int, tuple[str, ...]], dict[str, Any]]:
    rows: dict[tuple[str, int, str, int, tuple[str, ...]], dict[str, Any]] = {}
    for report in payload.get("case_reports") or []:
        if isinstance(report, dict):
            rows.setdefault(report_key(report), report)
    return rows


def direct_unique_events_with_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    seen: set[tuple[tuple[int, ...], int]] = set()
    for row in rows:
        scan = row.get("_scan") if isinstance(row.get("_scan"), dict) else {}
        for event in scan.get("relation_events") or []:
            coeffs, rhs, _terms = event["form"]
            key = (tuple(int(coeff) for coeff in coeffs), int(rhs))
            if key in seen:
                continue
            seen.add(key)
            events.append({**event, "row_key": row.get("row_key")})
    return events


def event_summary(event: dict[str, Any], form_index: int, order: int) -> dict[str, Any]:
    compact = compact_form(event, order)
    terms = [int_value(term) for term in compact.get("terms") or []]
    support = support_from_compact(compact)
    row_key = str(event.get("row_key") or "")
    salt = salt_from_row_key(row_key)
    return {
        "candidate_pos": int_value(event.get("candidate_pos")),
        "factor_support": support,
        "factor_support_label": label(support),
        "form_index": form_index,
        "leaf_index": int_value(event.get("leaf_index")),
        "original_trial": int_value(event.get("original_trial")),
        "q_coeff": int_value((compact.get("coeffs") or [0])[0]) % order,
        "rhs": int_value(compact.get("rhs")) % order,
        "row_key": row_key,
        "row_salt": salt,
        "scheduled_trial": int_value(event.get("scheduled_trial")),
        "scout_pos": int_value(event.get("scout_pos")),
        "term_shape": term_shape(terms),
        "terms": terms,
        "terms_label": label(terms),
    }


def event_features(event: dict[str, Any], include_relation_support: bool) -> set[str]:
    features: set[str] = {
        f"candidate_pos={int_value(event.get('candidate_pos'))}",
        f"leaf_index={int_value(event.get('leaf_index'))}",
        f"scout_pos={int_value(event.get('scout_pos'))}",
        f"terms={label(event.get('terms') or [])}",
        f"term_shape={event.get('term_shape')}",
    }
    features.update(bucket_features("candidate_pos", int_value(event.get("candidate_pos")), (1, 2, 3, 4, 5, 8, 13, 21)))
    features.update(bucket_features("scout_pos", int_value(event.get("scout_pos")), (8, 16, 32, 64, 79, 90)))
    salt = int_value(event.get("row_salt"), -1)
    if salt >= 0:
        features.add(f"row_salt_mod_4={salt % 4}")
        features.add(f"row_salt_mod_8={salt % 8}")
    if include_relation_support:
        features.add(f"factor_support={event.get('factor_support_label')}")
        features.add(f"rhs_mod_8={int_value(event.get('rhs')) % 8}")
        features.add(f"q_coeff_mod_8={int_value(event.get('q_coeff')) % 8}")
    return features


def conjunctions(features: set[str], max_size: int) -> set[str]:
    ordered = sorted(features)
    result = set(ordered)
    for size in range(2, max_size + 1):
        for combo in combinations(ordered, size):
            result.add("|".join(combo))
    return result


def load_rows(
    export_payload: dict[str, Any],
    scorer_payload: dict[str, Any],
    include_relation_support: bool,
    max_conjunction_size: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    labels = scorer_labels(scorer_payload)
    source_cache: dict[Path, dict[str, Any]] = {}
    source_index_cache: dict[Path, dict[tuple[str, int, str, int, tuple[str, ...]], dict[str, Any]]] = {}
    support_cache: dict[Path, dict[tuple[str, int, str, int, tuple[str, ...]], dict[str, Any]]] = {}
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for offset, certificate in enumerate(export_payload.get("certificates") or []):
        if not isinstance(certificate, dict):
            continue
        selected = certificate.get("selected") if isinstance(certificate.get("selected"), dict) else {}
        source_path = Path(str(certificate.get("source") or ""))
        support_path = Path(str(certificate.get("support") or ""))
        if not source_path.exists() or not support_path.exists():
            errors.append({"artifact_offset": offset, "error": "missing_source_or_support_path"})
            continue
        if source_path not in source_cache:
            source_cache[source_path] = load_json(source_path)
            source_index_cache[source_path] = source_case_index(source_cache[source_path])
        if support_path not in support_cache:
            support_cache[support_path] = support_report_index(load_json(support_path))
        key = (
            str(selected.get("target")),
            int_value(selected.get("transfer_index")),
            str(selected.get("selector")),
            int_value(selected.get("top_k")),
            canonical_rows(selected.get("row_keys")),
        )
        source_case = source_index_cache[source_path].get(key)
        support_report = support_cache[support_path].get(key)
        if source_case is None or support_report is None:
            errors.append({"artifact_offset": offset, "error": "missing_exact_source_or_support_case", "key": list(key)})
            continue
        verifier, contexts, _product_factor, _max_relations = timing_probe.selected_contexts_from_source_case(
            source_cache[source_path],
            source_case,
        )
        direct_rows, direct_ops, rho, _profiles = timing_probe.direct_witness_rows(verifier, contexts)
        events = direct_unique_events_with_rows(direct_rows)
        order = int_value((contexts[0]["built"] if contexts else {}).get("order"))
        event_rows = [event_summary(event, form_index, order) for form_index, event in enumerate(events)]
        label_info = labels.get(offset, {"rank_gain": 0, "unique_factor_relation_gain": 0})
        cert_window = str(certificate.get("window") or "")
        row = {
            "artifact_offset": offset,
            "cost_over_rho": float_value(selected.get("source_family_cost_over_rho")),
            "direct_ops_over_rho": round(direct_ops / max(1, rho), 8),
            "events": event_rows,
            "features": conjunctions(
                {feature for event in event_rows for feature in event_features(event, include_relation_support)},
                max_conjunction_size,
            ),
            "has_aux_11_15": any(event["factor_support_label"] == "11,15" for event in event_rows),
            "rank_gain": int_value(label_info.get("rank_gain")),
            "row": {
                "artifact_offset": offset,
                "aux_supports": sorted({event["factor_support_label"] for event in event_rows if event["factor_support_label"] not in {label(support) for support in certificate.get("known_factor_supports") or []}}),
                "direct_ops_over_rho": round(direct_ops / max(1, rho), 8),
                "event_count": len(event_rows),
                "events": event_rows,
                "has_aux_11_15": any(event["factor_support_label"] == "11,15" for event in event_rows),
                "known_factor_supports": certificate.get("known_factor_supports") or [],
                "rank_gain": int_value(label_info.get("rank_gain")),
                "selector": selected.get("selector"),
                "source_family_cost_over_rho": selected.get("source_family_cost_over_rho"),
                "top_k": int_value(selected.get("top_k")),
                "transfer_index": int_value(selected.get("transfer_index")),
                "unique_factor_relation_gain": int_value(label_info.get("unique_factor_relation_gain")),
                "window": cert_window,
            },
            "window": cert_window,
            "window_start": window_start(cert_window),
        }
        rows.append(row)
    return sorted(rows, key=lambda item: (item["window_start"], item["artifact_offset"])), errors


def split_rows(rows: list[dict[str, Any]], calibration_end: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return (
        [row for row in rows if int_value(row.get("window_start")) <= calibration_end],
        [row for row in rows if int_value(row.get("window_start")) > calibration_end],
    )


def is_positive(row: dict[str, Any], label_name: str) -> bool:
    if label_name == "aux_11_15":
        return bool(row.get("has_aux_11_15"))
    if label_name == "rank_gain":
        return int_value(row.get("rank_gain")) > 0
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


def support_contrast(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    supports = sorted({event["factor_support_label"] for row in rows for event in row["events"]})
    return [
        {
            "rule": f"factor_support={support}",
            "evaluation": evaluate_rule(f"factor_support={support}", rows, "aux_11_15"),
        }
        for support in supports
    ]


def claim_status(selected: dict[str, Any] | None, include_relation_support: bool) -> str:
    prefix = "RELATION_EVENT_SUPPORT" if include_relation_support else "RELATION_EVENT_PUBLIC"
    if selected is None:
        return f"{prefix}_RULE_NO_VIABLE_CALIBRATION"
    validation = selected.get("validation") if isinstance(selected.get("validation"), dict) else {}
    positives = int_value(validation.get("positive_count"))
    cost = validation.get("cost_per_positive_over_rho")
    if positives <= 0:
        return f"{prefix}_RULE_MISSES_VALIDATION"
    if cost is not None and float_value(cost) < 1.0:
        return f"{prefix}_RULE_VALIDATES_BELOW_RHO"
    return f"{prefix}_RULE_VALIDATES_ABOVE_RHO_OR_BROAD"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exported-certificates", required=True)
    parser.add_argument("--rank-scorer", required=True)
    parser.add_argument("--label", choices=["aux_11_15", "rank_gain"], default="aux_11_15")
    parser.add_argument("--calibration-end", type=int, default=3375)
    parser.add_argument("--max-conjunction-size", type=int, default=2)
    parser.add_argument("--min-calibration-hits", type=int, default=2)
    parser.add_argument("--min-calibration-precision", type=float, default=0.5)
    parser.add_argument("--include-relation-support", action="store_true")
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    export_path = Path(args.exported_certificates)
    scorer_path = Path(args.rank_scorer)
    rows, errors = load_rows(
        load_json(export_path),
        load_json(scorer_path),
        args.include_relation_support,
        args.max_conjunction_size,
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
    payload = {
        "artifacts": {
            "exported_certificates": str(export_path),
            "rank_scorer": str(scorer_path),
        },
        "claim_status": claim_status(selected, args.include_relation_support),
        "created_at": now_iso(),
        "errors": errors,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: rows are replayed from exported known-factor certificates and current direct witness scanner.",
            "Public mode uses accepted event position/term metadata but not compact relation support.",
            "include_relation_support is a post-relation diagnostic and cannot be counted as a pre-scan schedule.",
            "A validating public event rule is still a source-construction work order until rerun under source-charged/shared-product accounting.",
        ],
        "parameters": {
            "calibration_end": args.calibration_end,
            "include_relation_support": args.include_relation_support,
            "label": args.label,
            "max_conjunction_size": args.max_conjunction_size,
            "min_calibration_hits": args.min_calibration_hits,
            "min_calibration_precision": args.min_calibration_precision,
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
        "support_contrast": {
            "all_rows": support_contrast(rows),
            "calibration": support_contrast(calibration),
            "validation": support_contrast(validation),
        },
        "schema": "ecdlp.low_term_total2_auxiliary_relation_event_assembly_scout.v1",
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
