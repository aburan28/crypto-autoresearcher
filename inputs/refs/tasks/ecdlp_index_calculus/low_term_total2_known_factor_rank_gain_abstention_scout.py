#!/usr/bin/env python3
"""Scout simple rank-gain gates over exported known-factor certificates.

This diagnostic asks whether any compact feature of the exported
known-factor-substitution surface distinguishes certificates that add marginal
target-eliminated factor rank.  Some features are post-relation evidence, so a
positive rule is a work order for a future source generator, not yet a pre-scan
algorithm.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import json
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any


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


def support_labels(certificate: dict[str, Any]) -> list[str]:
    supports = certificate.get("known_factor_supports") or []
    return [label(list(support)) for support in supports if isinstance(support, list)]


def bucket_features(name: str, value: int, thresholds: tuple[int, ...]) -> set[str]:
    features = {f"{name}={value}"}
    for threshold in thresholds:
        if value <= threshold:
            features.add(f"{name}<=%d" % threshold)
        if value >= threshold:
            features.add(f"{name}>=%d" % threshold)
    return features


def selected_support_label(certificate: dict[str, Any]) -> str:
    return label(certificate.get("selected_term_support") or [])


def certificate_features(certificate: dict[str, Any], mode: str) -> set[str]:
    selected = certificate.get("selected") if isinstance(certificate.get("selected"), dict) else {}
    features: set[str] = {
        f"selector={selected.get('selector')}",
        f"topk={int_value(selected.get('top_k'))}",
        f"selected_support={selected_support_label(certificate)}",
        f"window_mod_16={window_start(str(certificate.get('window'))) % 16}",
    }
    if mode == "post_relation":
        for support in support_labels(certificate):
            features.add(f"known_support={support}")
        features.update(bucket_features("forms_count", int_value(certificate.get("forms_count")), (1, 2, 3, 4, 5)))
        features.update(bucket_features("relation_rank", int_value(certificate.get("rank")), (1, 2, 3, 4, 5)))
        features.update(
            bucket_features("known_factor_recovery_count", int_value(certificate.get("known_factor_recovery_count")), (1, 2, 3))
        )
        features.update(
            bucket_features("known_support_form_count", int_value(certificate.get("known_support_form_count")), (1, 2, 3, 4, 5))
        )
    return features


def conjunctions(features: set[str], max_size: int) -> set[str]:
    ordered = sorted(features)
    result = set(ordered)
    for size in range(2, max_size + 1):
        for combo in combinations(ordered, size):
            result.add("|".join(combo))
    return result


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
            "rank_gain": int_value(score.get("rank_gain")),
            "unique_factor_relation_gain": int_value(score.get("unique_factor_relation_gain")),
            "score": score,
        }
    return labels


def load_rows(export_payload: dict[str, Any], scorer_payload: dict[str, Any], feature_mode: str, max_conjunction_size: int) -> list[dict[str, Any]]:
    labels = scorer_labels(scorer_payload)
    rows: list[dict[str, Any]] = []
    for offset, certificate in enumerate(export_payload.get("certificates") or []):
        if not isinstance(certificate, dict):
            continue
        selected = certificate.get("selected") if isinstance(certificate.get("selected"), dict) else {}
        label_info = labels.get(offset, {"rank_gain": 0, "unique_factor_relation_gain": 0})
        base_features = certificate_features(certificate, feature_mode)
        rows.append(
            {
                "artifact_offset": offset,
                "cost_over_rho": float_value(selected.get("source_family_cost_over_rho")),
                "features": conjunctions(base_features, max_conjunction_size),
                "rank_gain": int_value(label_info.get("rank_gain")),
                "row": {
                    "artifact_offset": offset,
                    "direct_ops_over_rho": selected.get("direct_ops_over_rho"),
                    "forms_count": int_value(certificate.get("forms_count")),
                    "known_factor_supports": certificate.get("known_factor_supports") or [],
                    "rank": int_value(certificate.get("rank")),
                    "rank_gain": int_value(label_info.get("rank_gain")),
                    "selector": selected.get("selector"),
                    "source_family_cost_over_rho": selected.get("source_family_cost_over_rho"),
                    "top_k": int_value(selected.get("top_k")),
                    "transfer_index": int_value(selected.get("transfer_index")),
                    "unique_factor_relation_gain": int_value(label_info.get("unique_factor_relation_gain")),
                    "window": certificate.get("window"),
                },
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
        "rank_gain_total": sum(int_value(row.get("rank_gain")) for row in selected),
        "selected_count": len(selected),
        "selected_rows": [row["row"] for row in selected],
        "unique_factor_relation_gain_total": sum(int_value(row.get("unique_factor_relation_gain")) for row in selected),
        "rank_gain_hit_count": len(positives),
    }


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
            float(item["calibration"].get("cost_per_rank_gain_hit_over_rho") or 999999.0),
            str(item.get("rule")),
        )
    )
    return candidates


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exported-certificates", required=True)
    parser.add_argument("--rank-scorer", required=True)
    parser.add_argument("--calibration-end", type=int, default=3375)
    parser.add_argument("--feature-mode", choices=["public_pre_scan", "post_relation"], default="post_relation")
    parser.add_argument("--max-conjunction-size", type=int, default=2)
    parser.add_argument("--min-calibration-hits", type=int, default=2)
    parser.add_argument("--min-calibration-precision", type=float, default=0.5)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    export_path = Path(args.exported_certificates)
    scorer_path = Path(args.rank_scorer)
    rows = load_rows(
        load_json(export_path),
        load_json(scorer_path),
        args.feature_mode,
        args.max_conjunction_size,
    )
    calibration, validation = split_rows(rows, args.calibration_end)
    candidates = choose_rules(
        calibration,
        validation,
        args.min_calibration_hits,
        args.min_calibration_precision,
    )
    selected = candidates[0] if candidates else None
    payload = {
        "artifacts": {
            "exported_certificates": str(export_path),
            "rank_scorer": str(scorer_path),
        },
        "claim_status": (
            "RANK_GAIN_RULE_VALIDATES"
            if selected and int_value(selected["validation"].get("rank_gain_hit_count")) > 0
            else "RANK_GAIN_RULE_ABSTAINS_OR_MISSES_VALIDATION"
            if selected
            else "RANK_GAIN_RULE_NO_VIABLE_CALIBRATION"
        ),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: rank gain is measured against the current target-eliminated factor-bank namespace.",
            "If feature_mode=post_relation, selected features are diagnostic post-relation evidence and not a pre-scan source schedule.",
        ],
        "parameters": {
            "calibration_end": args.calibration_end,
            "feature_mode": args.feature_mode,
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
        "schema": "ecdlp.low_term_total2_known_factor_rank_gain_abstention_scout.v1",
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["split_summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"], "selected_rule": selected["rule"] if selected else None}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
