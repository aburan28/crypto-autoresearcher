#!/usr/bin/env python3
"""Scout pre-relation source precursors for the auxiliary ``[11, 15]`` form.

The previous auxiliary-direction diagnostic found that exported known-factor
certificates with an additional relation-form support ``[11, 15]`` are exactly
the marginal rank-gain rows on the held-out split.  This scout asks the next
question: can public source metadata or selected-leaf term visibility predict
that auxiliary direction before relation-form construction?

This is intentionally a precursor scout.  Labels come from exported relation
forms, while features are restricted to source/support metadata and selected
leaf term supports that are visible before accepted relation equations.
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


def label_sets(sets: list[list[int]]) -> str:
    if not sets:
        return "none"
    return ";".join(label(sorted(item)) for item in sorted([sorted(item) for item in sets]))


def window_start(window: str) -> int:
    try:
        return int(str(window).split("_", 1)[0])
    except (TypeError, ValueError):
        return 0


def canonical_rows(row_keys: Any) -> tuple[str, ...]:
    if not isinstance(row_keys, list):
        return tuple()
    return tuple(sorted(str(row) for row in row_keys))


def salts(row_keys: Any) -> list[int]:
    values: list[int] = []
    for row_key in canonical_rows(row_keys):
        if "salt" not in row_key:
            continue
        try:
            values.append(int(row_key.rsplit("salt", 1)[1]))
        except ValueError:
            continue
    return sorted(values)


def bucket_features(name: str, value: int, thresholds: tuple[int, ...]) -> set[str]:
    features = {f"{name}={value}"}
    for threshold in thresholds:
        if value <= threshold:
            features.add(f"{name}<={threshold}")
        if value >= threshold:
            features.add(f"{name}>={threshold}")
    return features


def support_from_form(form: dict[str, Any]) -> list[int]:
    coeffs = form.get("coeffs")
    if not isinstance(coeffs, list):
        return []
    return [index for index, value in enumerate(coeffs[1:]) if int_value(value) != 0]


def relation_support_labels(certificate: dict[str, Any]) -> list[str]:
    return [label(support_from_form(form)) for form in certificate.get("forms") or [] if isinstance(form, dict)]


def recovery_support_labels(certificate: dict[str, Any]) -> list[str]:
    supports = certificate.get("known_factor_supports") or []
    return [label(list(support)) for support in supports if isinstance(support, list)]


def auxiliary_support_labels(certificate: dict[str, Any]) -> list[str]:
    known = set(recovery_support_labels(certificate))
    return [support for support in relation_support_labels(certificate) if support not in known]


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


def support_report_index(payload: dict[str, Any]) -> dict[tuple[str, int, str, int, tuple[str, ...]], dict[str, Any]]:
    rows: dict[tuple[str, int, str, int, tuple[str, ...]], dict[str, Any]] = {}
    for report in payload.get("case_reports") or []:
        if isinstance(report, dict):
            rows.setdefault(report_key(report), report)
    return rows


def source_case_index(payload: dict[str, Any]) -> dict[tuple[str, int, str, int, tuple[str, ...]], dict[str, Any]]:
    rows: dict[tuple[str, int, str, int, tuple[str, ...]], dict[str, Any]] = {}
    for case in source_cases(payload):
        rows.setdefault(source_case_key(case), case)
    return rows


def selected_leaf_term_profile(source_payload: dict[str, Any], source_case: dict[str, Any]) -> dict[str, Any]:
    _verifier, contexts, _product_factor, _max_relations = timing_probe.selected_contexts_from_source_case(
        source_payload,
        source_case,
    )
    leaf_terms: dict[str, set[int]] = {}
    leaf_scout_terms: dict[str, list[list[int]]] = {}
    selected_union: set[int] = set()
    for context in contexts:
        selected = {int_value(leaf) for leaf in context.get("selected_leaf_indices") or []}
        row_suffix = str(context.get("row_key", "")).rsplit(":", 1)[-1]
        for scout in context["built"].get("scouts") or []:
            pos = scout.get("scout_pos")
            matched: list[int] = []
            if pos in selected:
                matched.append(int_value(pos))
            if isinstance(pos, int) and pos - 1 in selected:
                matched.append(pos - 1)
            if not matched:
                continue
            terms = sorted({int_value(index) for index, _sign in scout.get("signed_terms") or []})
            selected_union.update(terms)
            for leaf in matched:
                key = f"{row_suffix}:{leaf}"
                leaf_terms.setdefault(key, set()).update(terms)
                leaf_scout_terms.setdefault(key, []).append(terms)
    term_labels = {key: label(sorted(values)) for key, values in sorted(leaf_terms.items())}
    scout_labels = {
        key: ";".join(label(item) for item in sorted(value))
        for key, value in sorted(leaf_scout_terms.items())
    }
    return {
        "leaf_scout_terms": scout_labels,
        "leaf_terms": term_labels,
        "selected_leaf_term_support": sorted(selected_union),
    }


def leaf_sets(source_case: dict[str, Any]) -> list[list[int]]:
    out: list[list[int]] = []
    for item in source_case.get("row_leaf_keys") or []:
        if not isinstance(item, dict):
            continue
        out.append(sorted(int_value(value) for value in item.get("leaf_indices") or []))
    return out


def public_features(
    certificate: dict[str, Any],
    support_report: dict[str, Any],
    source_case: dict[str, Any],
    term_profile: dict[str, Any],
    include_schedule_metadata: bool,
    include_residue: bool,
) -> set[str]:
    selected = certificate.get("selected") if isinstance(certificate.get("selected"), dict) else {}
    selected_support = support_report.get("selected_term_support") or certificate.get("selected_term_support") or []
    leaves = leaf_sets(source_case)
    leaf_union = sorted({leaf for item in leaves for leaf in item})
    leaf_intersection = sorted(set(leaves[0]).intersection(*[set(item) for item in leaves[1:]])) if leaves else []
    features: set[str] = {
        f"selector={selected.get('selector')}",
        f"topk={int_value(selected.get('top_k'))}",
        f"selected_support={label(selected_support)}",
        f"selected_leaf_term_support={label(term_profile.get('selected_leaf_term_support') or [])}",
        f"priority_hits={label(support_report.get('priority_hits') or [])}",
        f"priority_hit_count={len(support_report.get('priority_hits') or [])}",
        f"public_product_gate_selected={bool(support_report.get('public_product_gate_selected'))}",
        f"source_policy={source_case.get('source_policy')}",
        f"source_row_selector={source_case.get('row_selector')}",
        f"leaf_count_shape={label(sorted(len(item) for item in leaves))}",
        f"leaf_row_multiset={label_sets(leaves)}",
        f"leaf_union={label(leaf_union)}",
        f"leaf_intersection={label(leaf_intersection)}",
    }
    features.update(bucket_features("selected_support_size", len(selected_support), (8, 10, 12, 15)))
    features.update(bucket_features("selected_leaf_count", int_value(source_case.get("selected_leaf_count")), (1, 2, 3, 4, 5)))
    features.update(bucket_features("selected_row_count", int_value(source_case.get("selected_row_count")), (1, 2, 3)))
    for leaf in leaf_union:
        features.add(f"leaf_union_has={leaf}")
    for leaf in leaf_intersection:
        features.add(f"leaf_intersection_has={leaf}")
    for item in leaves:
        features.add(f"leaf_row={label(item)}")
    for key, value in (term_profile.get("leaf_terms") or {}).items():
        _row_suffix, leaf = key.split(":", 1)
        features.add(f"leaf_terms[{leaf}]={value}")
        for term in value.split(","):
            if term:
                features.add(f"leaf_terms[{leaf}]_has={term}")
    for value in (term_profile.get("leaf_scout_terms") or {}).values():
        for scout_label in value.split(";"):
            if scout_label:
                features.add(f"leaf_scout_terms={scout_label}")
    if include_schedule_metadata:
        row_offset = int_value(selected.get("source_family_row_offset"), -1)
        scanned_count = int_value(selected.get("source_family_scanned_candidate_count"), -1)
        features.update(bucket_features("source_family_row_offset", row_offset, (0, 1, 2, 4, 8, 16, 20)))
        features.update(bucket_features("source_family_scanned_candidate_count", scanned_count, (1, 2, 4, 8)))
    if include_residue:
        row_salts = salts(selected.get("row_keys"))
        if row_salts:
            gap = max(row_salts) - min(row_salts)
            features.add(f"salt_gap={gap}")
            features.add(f"salt_gap_mod_4={gap % 4}")
            features.add(f"salt_sum_mod_8={sum(row_salts) % 8}")
            features.add(f"transfer_mod_8={int_value(selected.get('transfer_index')) % 8}")
            for salt in row_salts:
                features.add(f"salt_mod_8={salt % 8}")
    return features


def conjunctions(features: set[str], max_size: int) -> set[str]:
    ordered = sorted(features)
    result = set(ordered)
    for size in range(2, max_size + 1):
        for combo in combinations(ordered, size):
            result.add("|".join(combo))
    return result


def is_positive(row: dict[str, Any], label_name: str) -> bool:
    if label_name == "aux_11_15":
        return bool(row.get("has_aux_11_15"))
    if label_name == "rank_gain":
        return int_value(row.get("rank_gain")) > 0
    raise ValueError(f"unknown label {label_name!r}")


def load_rows(
    export_payload: dict[str, Any],
    scorer_payload: dict[str, Any],
    include_schedule_metadata: bool,
    include_residue: bool,
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
        term_profile = selected_leaf_term_profile(source_cache[source_path], source_case)
        aux_labels = auxiliary_support_labels(certificate)
        label_info = labels.get(offset, {"rank_gain": 0, "unique_factor_relation_gain": 0})
        features = public_features(
            certificate,
            support_report,
            source_case,
            term_profile,
            include_schedule_metadata,
            include_residue,
        )
        window = str(certificate.get("window") or "")
        rows.append(
            {
                "artifact_offset": offset,
                "cost_over_rho": float_value(selected.get("source_family_cost_over_rho")),
                "features": conjunctions(features, max_conjunction_size),
                "has_aux_11_15": "11,15" in aux_labels,
                "rank_gain": int_value(label_info.get("rank_gain")),
                "row": {
                    "artifact_offset": offset,
                    "auxiliary_supports": aux_labels,
                    "forms_count": int_value(certificate.get("forms_count")),
                    "has_aux_11_15": "11,15" in aux_labels,
                    "leaf_count_shape": sorted(len(item) for item in leaf_sets(source_case)),
                    "leaf_row_multiset": label_sets(leaf_sets(source_case)),
                    "priority_hits": support_report.get("priority_hits") or [],
                    "rank_gain": int_value(label_info.get("rank_gain")),
                    "selected_leaf_term_support": term_profile.get("selected_leaf_term_support") or [],
                    "selected_support": support_report.get("selected_term_support") or certificate.get("selected_term_support") or [],
                    "selector": selected.get("selector"),
                    "source_family_cost_over_rho": selected.get("source_family_cost_over_rho"),
                    "source_family_row_offset": selected.get("source_family_row_offset"),
                    "top_k": int_value(selected.get("top_k")),
                    "transfer_index": int_value(selected.get("transfer_index")),
                    "unique_factor_relation_gain": int_value(label_info.get("unique_factor_relation_gain")),
                    "window": window,
                },
                "window": window,
                "window_start": window_start(window),
            }
        )
    return sorted(rows, key=lambda item: (item["window_start"], item["artifact_offset"])), errors


def split_rows(rows: list[dict[str, Any]], calibration_end: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return (
        [row for row in rows if int_value(row.get("window_start")) <= calibration_end],
        [row for row in rows if int_value(row.get("window_start")) > calibration_end],
    )


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


def contrast_rules(rows: list[dict[str, Any]], label_name: str) -> list[dict[str, Any]]:
    interesting = sorted(
        rule
        for rule in {feature for row in rows for feature in row["features"]}
        if rule.startswith("leaf_row_multiset=")
        or rule.startswith("selected_leaf_term_support=")
        or rule.startswith("leaf_terms[90]=")
        or rule.startswith("source_family_row_offset")
    )
    return [{"rule": rule, "evaluation": evaluate_rule(rule, rows, label_name)} for rule in interesting]


def claim_status(selected: dict[str, Any] | None) -> str:
    if selected is None:
        return "AUX_SOURCE_PRECURSOR_NO_VIABLE_CALIBRATION"
    validation = selected.get("validation") if isinstance(selected.get("validation"), dict) else {}
    positives = int_value(validation.get("positive_count"))
    cost = validation.get("cost_per_positive_over_rho")
    if positives <= 0:
        return "AUX_SOURCE_PRECURSOR_RULE_MISSES_VALIDATION"
    if cost is not None and float_value(cost) < 1.0:
        return "AUX_SOURCE_PRECURSOR_RULE_VALIDATES_BELOW_RHO"
    return "AUX_SOURCE_PRECURSOR_RULE_VALIDATES_ABOVE_RHO_OR_BROAD"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exported-certificates", required=True)
    parser.add_argument("--rank-scorer", required=True)
    parser.add_argument("--label", choices=["aux_11_15", "rank_gain"], default="aux_11_15")
    parser.add_argument("--calibration-end", type=int, default=3375)
    parser.add_argument("--max-conjunction-size", type=int, default=2)
    parser.add_argument("--min-calibration-hits", type=int, default=2)
    parser.add_argument("--min-calibration-precision", type=float, default=0.5)
    parser.add_argument("--include-schedule-metadata", action="store_true")
    parser.add_argument("--include-residue", action="store_true")
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    export_path = Path(args.exported_certificates)
    scorer_path = Path(args.rank_scorer)
    rows, errors = load_rows(
        load_json(export_path),
        load_json(scorer_path),
        args.include_schedule_metadata,
        args.include_residue,
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
        "claim_status": claim_status(selected),
        "contrast_rules": {
            "all_rows": contrast_rules(rows, args.label),
            "calibration": contrast_rules(calibration, args.label),
            "validation": contrast_rules(validation, args.label),
        },
        "created_at": now_iso(),
        "errors": errors,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: auxiliary-direction labels come from exported known-factor relation forms.",
            "Features are public source/support metadata and selected-leaf term support visible before accepted relation equations.",
            "include_schedule_metadata uses public source-family enumeration position; include_residue is a red-team diagnostic and must not be promoted without fresh validation.",
            "A validating rule is a source-construction work order until rerun as a real source-charged/shared-product collector.",
        ],
        "parameters": {
            "calibration_end": args.calibration_end,
            "include_residue": args.include_residue,
            "include_schedule_metadata": args.include_schedule_metadata,
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
        "schema": "ecdlp.low_term_total2_auxiliary_direction_source_precursor_scout.v1",
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
