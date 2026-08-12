#!/usr/bin/env python3
"""Scout auxiliary relation-form directions in exported known-factor certs.

Known-factor export certificates can recover a target scalar through an
already-known factor support, such as ``[10, 14]``.  Marginal rank gain needs
more: an additional relation direction that is not just another copy of the
recovery support.  This diagnostic contrasts compact relation-form supports
against scorer labels for marginal target-eliminated factor-rank gain.

Features here are post-relation evidence.  A validating rule is therefore a
source-construction work order, not yet a public pre-scan schedule.
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


PREFERRED_RULES = {
    "aux_support=11,15": 0,
    "has_aux_support_11_15": 1,
    "aux_support_set=11,15": 2,
    "has_aux_col15": 3,
}


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


def window_start(window: str) -> int:
    try:
        return int(str(window).split("_", 1)[0])
    except (TypeError, ValueError):
        return 0


def label(values: Any) -> str:
    if not isinstance(values, list):
        return "none"
    return ",".join(str(int_value(value)) for value in values)


def support_from_form(form: dict[str, Any]) -> list[int]:
    coeffs = form.get("coeffs")
    if not isinstance(coeffs, list):
        return []
    # coeffs[0] is the target coefficient; coeffs[1:] are factor columns.
    return [index for index, value in enumerate(coeffs[1:]) if int_value(value) != 0]


def support_set_label(labels: list[str]) -> str:
    if not labels:
        return "none"
    return ";".join(sorted(set(labels)))


def bucket_features(name: str, value: int, thresholds: tuple[int, ...]) -> set[str]:
    features = {f"{name}={value}"}
    for threshold in thresholds:
        if value <= threshold:
            features.add(f"{name}<=%d" % threshold)
        if value >= threshold:
            features.add(f"{name}>=%d" % threshold)
    return features


def scorer_labels(payload: dict[str, Any]) -> dict[int, dict[str, Any]]:
    labels: dict[int, dict[str, Any]] = {}
    for score in payload.get("scores") or []:
        if not isinstance(score, dict):
            continue
        candidate = score.get("candidate") if isinstance(score.get("candidate"), dict) else {}
        offset = int_value(candidate.get("artifact_offset"), -1)
        if offset < 0:
            continue
        labels[offset] = {
            "rank_after": int_value(score.get("rank_after")),
            "rank_before": int_value(score.get("rank_before")),
            "rank_gain": int_value(score.get("rank_gain")),
            "score": score,
            "unique_factor_relation_gain": int_value(score.get("unique_factor_relation_gain")),
        }
    return labels


def relation_supports(certificate: dict[str, Any]) -> list[str]:
    supports: list[str] = []
    for form in certificate.get("forms") or []:
        if not isinstance(form, dict):
            continue
        supports.append(label(support_from_form(form)))
    return supports


def recovery_supports(certificate: dict[str, Any]) -> list[str]:
    supports = certificate.get("known_factor_supports") or []
    return [label(list(support)) for support in supports if isinstance(support, list)]


def auxiliary_supports(certificate: dict[str, Any]) -> list[str]:
    known = set(recovery_supports(certificate))
    return [support for support in relation_supports(certificate) if support not in known]


def certificate_features(certificate: dict[str, Any]) -> set[str]:
    form_labels = relation_supports(certificate)
    known_labels = recovery_supports(certificate)
    aux_labels = auxiliary_supports(certificate)
    form_counts = Counter(form_labels)
    aux_counts = Counter(aux_labels)
    selected = certificate.get("selected") if isinstance(certificate.get("selected"), dict) else {}
    features: set[str] = {
        f"selector={selected.get('selector')}",
        f"topk={int_value(selected.get('top_k'))}",
        f"window_mod_16={window_start(str(certificate.get('window'))) % 16}",
        f"form_support_set={support_set_label(form_labels)}",
        f"known_recovery_support_set={support_set_label(known_labels)}",
        f"aux_support_set={support_set_label(aux_labels)}",
    }
    for support in form_labels:
        features.add(f"form_support={support}")
    for support in known_labels:
        features.add(f"known_recovery_support={support}")
    for support in aux_labels:
        features.add(f"aux_support={support}")
    for support, count in sorted(form_counts.items()):
        features.add(f"form_support_count[{support}]={count}")
        if count >= 2:
            features.add(f"form_support_count[{support}]>=2")
    for support, count in sorted(aux_counts.items()):
        features.add(f"aux_support_count[{support}]={count}")
        if count >= 2:
            features.add(f"aux_support_count[{support}]>=2")
    if "11,15" in aux_counts:
        features.add("has_aux_support_11_15")
    if "10,14" in known_labels:
        features.add("has_known_recovery_10_14")
    if any("15" in support.split(",") for support in aux_labels if support != "none"):
        features.add("has_aux_col15")
    if aux_labels:
        features.add("has_any_aux_support")
    features.update(bucket_features("forms_count", int_value(certificate.get("forms_count")), (1, 2, 3, 4, 5)))
    features.update(bucket_features("distinct_form_support_count", len(set(form_labels)), (1, 2, 3, 4, 5)))
    features.update(bucket_features("distinct_aux_support_count", len(set(aux_labels)), (0, 1, 2, 3, 4)))
    features.update(bucket_features("aux_form_count", len(aux_labels), (0, 1, 2, 3, 4)))
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
    max_conjunction_size: int,
) -> list[dict[str, Any]]:
    labels = scorer_labels(scorer_payload)
    rows: list[dict[str, Any]] = []
    for offset, certificate in enumerate(export_payload.get("certificates") or []):
        if not isinstance(certificate, dict):
            continue
        selected = certificate.get("selected") if isinstance(certificate.get("selected"), dict) else {}
        label_info = labels.get(offset, {"rank_gain": 0, "unique_factor_relation_gain": 0})
        form_labels = relation_supports(certificate)
        known_labels = recovery_supports(certificate)
        aux_labels = auxiliary_supports(certificate)
        row = {
            "artifact_offset": offset,
            "auxiliary_supports": aux_labels,
            "direct_ops_over_rho": selected.get("direct_ops_over_rho"),
            "distinct_auxiliary_supports": sorted(set(aux_labels)),
            "distinct_form_supports": sorted(set(form_labels)),
            "form_supports": form_labels,
            "forms_count": int_value(certificate.get("forms_count")),
            "known_factor_supports": certificate.get("known_factor_supports") or [],
            "known_recovery_supports": known_labels,
            "rank": int_value(certificate.get("rank")),
            "rank_after": int_value(label_info.get("rank_after")),
            "rank_before": int_value(label_info.get("rank_before")),
            "rank_gain": int_value(label_info.get("rank_gain")),
            "selector": selected.get("selector"),
            "source_family_cost_over_rho": selected.get("source_family_cost_over_rho"),
            "top_k": int_value(selected.get("top_k")),
            "transfer_index": int_value(selected.get("transfer_index")),
            "unique_factor_relation_gain": int_value(label_info.get("unique_factor_relation_gain")),
            "window": certificate.get("window"),
        }
        rows.append(
            {
                "artifact_offset": offset,
                "cost_over_rho": float_value(selected.get("source_family_cost_over_rho")),
                "features": conjunctions(certificate_features(certificate), max_conjunction_size),
                "rank_gain": int_value(label_info.get("rank_gain")),
                "row": row,
                "unique_factor_relation_gain": int_value(label_info.get("unique_factor_relation_gain")),
                "window": str(certificate.get("window")),
                "window_start": window_start(str(certificate.get("window"))),
            }
        )
    return sorted(rows, key=lambda item: (item["window_start"], item["artifact_offset"]))


def split_rows(rows: list[dict[str, Any]], calibration_end: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    calibration = [row for row in rows if int_value(row.get("window_start")) <= calibration_end]
    validation = [row for row in rows if int_value(row.get("window_start")) > calibration_end]
    return calibration, validation


def evaluate_rule(rule: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    selected = [row for row in rows if rule in row["features"]]
    positives = [row for row in selected if int_value(row.get("rank_gain")) > 0]
    cost = sum(float_value(row.get("cost_over_rho")) for row in selected)
    return {
        "cost_over_rho": round(cost, 8),
        "cost_per_rank_gain_hit_over_rho": round(cost / len(positives), 8) if positives else None,
        "precision": round(len(positives) / len(selected), 8) if selected else None,
        "rank_gain_hit_count": len(positives),
        "rank_gain_total": sum(int_value(row.get("rank_gain")) for row in selected),
        "selected_count": len(selected),
        "selected_rows": [row["row"] for row in selected],
        "unique_factor_relation_gain_total": sum(int_value(row.get("unique_factor_relation_gain")) for row in selected),
    }


def preferred_rank(rule: str) -> int:
    return PREFERRED_RULES.get(rule, 50)


def choose_rules(
    calibration: list[dict[str, Any]],
    validation: list[dict[str, Any]],
    min_calibration_hits: int,
    min_calibration_precision: float,
) -> list[dict[str, Any]]:
    rules = sorted({feature for row in calibration for feature in row["features"]})
    candidates: list[dict[str, Any]] = []
    for rule in rules:
        calibration_eval = evaluate_rule(rule, calibration)
        if int_value(calibration_eval.get("rank_gain_hit_count")) < min_calibration_hits:
            continue
        precision = calibration_eval.get("precision")
        if precision is None or float(precision) < min_calibration_precision:
            continue
        validation_eval = evaluate_rule(rule, validation)
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
            -int_value(item["calibration"].get("rank_gain_hit_count")),
            int_value(item.get("feature_count")),
            preferred_rank(str(item.get("rule"))),
            float(item["calibration"].get("cost_per_rank_gain_hit_over_rho") or 999999.0),
            str(item.get("rule")),
        )
    )
    return candidates


def support_contrast(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    labels = sorted({support for row in rows for support in row["row"]["distinct_auxiliary_supports"]})
    return [
        {
            "rule": f"aux_support={support}",
            "evaluation": evaluate_rule(f"aux_support={support}", rows),
        }
        for support in labels
    ]


def claim_status(selected: dict[str, Any] | None) -> str:
    if selected is None:
        return "AUXILIARY_DIRECTION_RULE_NO_VIABLE_CALIBRATION"
    validation = selected.get("validation") if isinstance(selected.get("validation"), dict) else {}
    hit_count = int_value(validation.get("rank_gain_hit_count"))
    cost_per_hit = validation.get("cost_per_rank_gain_hit_over_rho")
    if hit_count <= 0:
        return "AUXILIARY_DIRECTION_RULE_MISSES_VALIDATION"
    if cost_per_hit is not None and float_value(cost_per_hit) < 1.0:
        return "AUXILIARY_DIRECTION_RULE_VALIDATES_BELOW_RHO_POST_RELATION"
    return "AUXILIARY_DIRECTION_RULE_VALIDATES_ABOVE_RHO_POST_RELATION"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exported-certificates", required=True)
    parser.add_argument("--rank-scorer", required=True)
    parser.add_argument("--calibration-end", type=int, default=3375)
    parser.add_argument("--max-conjunction-size", type=int, default=1)
    parser.add_argument("--min-calibration-hits", type=int, default=2)
    parser.add_argument("--min-calibration-precision", type=float, default=0.5)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    export_path = Path(args.exported_certificates)
    scorer_path = Path(args.rank_scorer)
    rows = load_rows(load_json(export_path), load_json(scorer_path), args.max_conjunction_size)
    calibration, validation = split_rows(rows, args.calibration_end)
    candidates = choose_rules(
        calibration,
        validation,
        args.min_calibration_hits,
        args.min_calibration_precision,
    )
    selected = candidates[0] if candidates else None
    target_rule = "aux_support=11,15"
    payload = {
        "artifacts": {
            "exported_certificates": str(export_path),
            "rank_scorer": str(scorer_path),
        },
        "claim_status": claim_status(selected),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: rank gain is measured against the current target-eliminated factor-bank namespace.",
            "POST-RELATION DIAGNOSTIC: auxiliary supports are observed after relation-form construction and are not yet a public pre-scan source schedule.",
            "This artifact identifies a source-construction target; it does not claim a complete faster-than-rho ECDLP algorithm.",
        ],
        "parameters": {
            "calibration_end": args.calibration_end,
            "max_conjunction_size": args.max_conjunction_size,
            "min_calibration_hits": args.min_calibration_hits,
            "min_calibration_precision": args.min_calibration_precision,
        },
        "rows": [row["row"] for row in rows],
        "rules": candidates[:20],
        "selected_rule": selected,
        "split_summary": {
            "calibration_rank_gain_hit_count": sum(1 for row in calibration if int_value(row.get("rank_gain")) > 0),
            "calibration_row_count": len(calibration),
            "validation_rank_gain_hit_count": sum(1 for row in validation if int_value(row.get("rank_gain")) > 0),
            "validation_row_count": len(validation),
        },
        "support_contrast": {
            "all_rows": support_contrast(rows),
            "calibration": support_contrast(calibration),
            "validation": support_contrast(validation),
        },
        "target_rule": {
            "calibration": evaluate_rule(target_rule, calibration),
            "rule": target_rule,
            "validation": evaluate_rule(target_rule, validation),
        },
        "schema": "ecdlp.low_term_total2_relation_form_auxiliary_direction_scout.v1",
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["split_summary"], indent=2, sort_keys=True))
    print(
        json.dumps(
            {
                "claim_status": payload["claim_status"],
                "selected_rule": selected["rule"] if selected else None,
                "target_rule_validation": payload["target_rule"]["validation"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
