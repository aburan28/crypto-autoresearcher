#!/usr/bin/env python3
"""Scout source-neighborhood predictors for rank-rich lowterm rows.

The selected-leaf shape ``2,3`` marked the broad full-support lowterm family but
did not isolate marginal rank gain.  This scout adds pre-scan neighborhood
features: how many sibling source cases share the same transfer, selector,
top-k, row keys, and leaf-union/intersection patterns.  It intentionally avoids
post-relation fields such as public verification, rank, relation count, or
direct operation cost.
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

from low_term_total2_known_column_pressure_direct_screen import source_case_key, source_cases


WINDOW_RE = re.compile(r"(?:fixed_row_|selector_expanded_|col15_)(\d+)_(\d+)")


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


def build_window_map(paths: list[Path]) -> dict[str, Path]:
    mapped: dict[str, Path] = {}
    for path in paths:
        window = window_from_path(path)
        if window:
            mapped[window] = path
    return mapped


def window_start(window: str) -> int:
    try:
        return int(str(window).split("_", 1)[0])
    except (TypeError, ValueError):
        return 0


def label(values: Any) -> str:
    if not isinstance(values, list):
        return "none"
    return ",".join(str(int_value(value)) for value in values)


def canonical_rows(row_keys: Any) -> tuple[str, ...]:
    if not isinstance(row_keys, list):
        return tuple()
    return tuple(sorted(str(row) for row in row_keys))


def bucket_features(name: str, value: int, thresholds: tuple[int, ...]) -> set[str]:
    features = {f"{name}={value}"}
    for threshold in thresholds:
        if value <= threshold:
            features.add(f"{name}<=%d" % threshold)
        if value >= threshold:
            features.add(f"{name}>=%d" % threshold)
    return features


def row_leaf_sets(case: dict[str, Any]) -> list[set[int]]:
    sets: list[set[int]] = []
    for item in case.get("row_leaf_keys") or []:
        if not isinstance(item, dict):
            continue
        sets.append({int_value(value) for value in item.get("leaf_indices") or []})
    return sets


def leaf_union(case: dict[str, Any]) -> set[int]:
    union: set[int] = set()
    for item in row_leaf_sets(case):
        union.update(item)
    return union


def leaf_intersection(case: dict[str, Any]) -> set[int]:
    sets = row_leaf_sets(case)
    if not sets:
        return set()
    intersection = set(sets[0])
    for item in sets[1:]:
        intersection &= item
    return intersection


def leaf_count_shape(case: dict[str, Any]) -> tuple[int, ...]:
    return tuple(sorted(len(item) for item in row_leaf_sets(case)))


def source_case_index(source_payload: dict[str, Any]) -> dict[tuple[str, int, str, int, tuple[str, ...]], dict[str, Any]]:
    result: dict[tuple[str, int, str, int, tuple[str, ...]], dict[str, Any]] = {}
    for case in source_cases(source_payload):
        result.setdefault(source_case_key(case), case)
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
        }
    return labels


def peer_stats(target: dict[str, Any], peers: list[dict[str, Any]]) -> dict[str, int]:
    target_rows = set(canonical_rows(target.get("row_keys")))
    target_union = leaf_union(target)
    target_intersection = leaf_intersection(target)
    target_shape = leaf_count_shape(target)
    row_degrees = Counter()
    for peer in peers:
        for row_key in canonical_rows(peer.get("row_keys")):
            row_degrees[row_key] += 1
    target_degrees = [row_degrees[row] for row in target_rows]
    return {
        "peer_count": len(peers),
        "same_leaf_union_count": sum(1 for peer in peers if leaf_union(peer) == target_union),
        "same_leaf_intersection_count": sum(1 for peer in peers if leaf_intersection(peer) == target_intersection),
        "same_leaf_shape_count": sum(1 for peer in peers if leaf_count_shape(peer) == target_shape),
        "shares_any_row_count": sum(1 for peer in peers if set(canonical_rows(peer.get("row_keys"))) & target_rows),
        "shares_all_rows_count": sum(1 for peer in peers if set(canonical_rows(peer.get("row_keys"))) == target_rows),
        "target_row_degree_max": max(target_degrees) if target_degrees else 0,
        "target_row_degree_min": min(target_degrees) if target_degrees else 0,
        "target_row_degree_sum": sum(target_degrees),
        "unique_leaf_union_count": len({tuple(sorted(leaf_union(peer))) for peer in peers}),
        "unique_leaf_shape_count": len({leaf_count_shape(peer) for peer in peers}),
        "unique_row_key_count": len({row for peer in peers for row in canonical_rows(peer.get("row_keys"))}),
    }


def neighborhood_features(target: dict[str, Any], all_cases: list[dict[str, Any]]) -> set[str]:
    transfer = int_value(target.get("transfer_index"))
    selector = str(target.get("selector"))
    top_k = int_value(target.get("top_k"))
    scopes = {
        "transfer": [case for case in all_cases if int_value(case.get("transfer_index")) == transfer],
        "transfer_selector": [
            case
            for case in all_cases
            if int_value(case.get("transfer_index")) == transfer and str(case.get("selector")) == selector
        ],
        "transfer_selector_topk": [
            case
            for case in all_cases
            if int_value(case.get("transfer_index")) == transfer
            and str(case.get("selector")) == selector
            and int_value(case.get("top_k")) == top_k
        ],
    }
    features: set[str] = set()
    for scope, peers in scopes.items():
        stats = peer_stats(target, peers)
        for name, value in stats.items():
            if name.endswith("_count") or name.startswith("unique_") or name.endswith("_max") or name.endswith("_min") or name.endswith("_sum"):
                features.update(bucket_features(f"{scope}_{name}", int_value(value), (1, 2, 3, 4, 5, 8, 11, 16, 22, 33)))
            else:
                features.add(f"{scope}_{name}={value}")
    features.add(f"leaf_count_shape={label(list(leaf_count_shape(target)))}")
    features.add(f"leaf_union={label(sorted(leaf_union(target)))}")
    features.add(f"leaf_intersection={label(sorted(leaf_intersection(target)))}")
    features.update(bucket_features("selected_leaf_count", int_value(target.get("selected_leaf_count")), (1, 2, 3, 4, 5)))
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
    source_by_window: dict[str, Path],
    max_conjunction_size: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    labels_by_offset = scorer_labels(scorer_payload)
    source_payload_cache: dict[Path, dict[str, Any]] = {}
    source_index_cache: dict[Path, dict[tuple[str, int, str, int, tuple[str, ...]], dict[str, Any]]] = {}
    source_cases_cache: dict[Path, list[dict[str, Any]]] = {}
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for offset, certificate in enumerate(export_payload.get("certificates") or []):
        if not isinstance(certificate, dict):
            continue
        selected = certificate.get("selected") if isinstance(certificate.get("selected"), dict) else {}
        window = str(certificate.get("window") or "")
        source_path = source_by_window.get(window)
        if source_path is None:
            errors.append({"artifact_offset": offset, "error": "missing_source", "window": window})
            continue
        if source_path not in source_payload_cache:
            payload = load_json(source_path)
            source_payload_cache[source_path] = payload
            cases = source_cases(payload)
            source_cases_cache[source_path] = cases
            source_index_cache[source_path] = source_case_index(payload)
        key = (
            str(selected.get("target")),
            int_value(selected.get("transfer_index")),
            str(selected.get("selector")),
            int_value(selected.get("top_k")),
            canonical_rows(selected.get("row_keys")),
        )
        source_case = source_index_cache[source_path].get(key)
        if source_case is None:
            errors.append({"artifact_offset": offset, "error": "missing_exact_source_case", "key": list(key), "window": window})
            continue
        labels = labels_by_offset.get(offset, {"rank_gain": 0, "unique_factor_relation_gain": 0})
        features = conjunctions(neighborhood_features(source_case, source_cases_cache[source_path]), max_conjunction_size)
        rows.append(
            {
                "artifact_offset": offset,
                "cost_over_rho": float_value(selected.get("source_family_cost_over_rho")),
                "features": features,
                "forms_count": int_value(certificate.get("forms_count")),
                "rank_gain": int_value(labels.get("rank_gain")),
                "row": {
                    "artifact_offset": offset,
                    "forms_count": int_value(certificate.get("forms_count")),
                    "leaf_count_shape": list(leaf_count_shape(source_case)),
                    "rank": int_value(certificate.get("rank")),
                    "rank_gain": int_value(labels.get("rank_gain")),
                    "source_family_cost_over_rho": selected.get("source_family_cost_over_rho"),
                    "top_k": int_value(selected.get("top_k")),
                    "transfer_index": int_value(selected.get("transfer_index")),
                    "unique_factor_relation_gain": int_value(labels.get("unique_factor_relation_gain")),
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


def is_positive(row: dict[str, Any], label_name: str) -> bool:
    if label_name == "rank_gain":
        return int_value(row.get("rank_gain")) > 0
    if label_name == "forms_count_ge2":
        return int_value(row.get("forms_count")) >= 2
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
    rules: list[dict[str, Any]] = []
    for rule in sorted({feature for row in calibration for feature in row["features"]}):
        calibration_eval = evaluate_rule(rule, calibration, label_name)
        if int_value(calibration_eval.get("positive_count")) < min_calibration_hits:
            continue
        precision = calibration_eval.get("precision")
        if precision is None or float(precision) < min_calibration_precision:
            continue
        validation_eval = evaluate_rule(rule, validation, label_name)
        rules.append(
            {
                "calibration": calibration_eval,
                "feature_count": rule.count("|") + 1,
                "rule": rule,
                "validation": validation_eval,
            }
        )
    rules.sort(
        key=lambda item: (
            -float(item["calibration"].get("precision") or 0.0),
            -int_value(item["calibration"].get("positive_count")),
            int_value(item.get("feature_count")),
            float(item["calibration"].get("cost_per_positive_over_rho") or 999999.0),
            str(item.get("rule")),
        )
    )
    return rules


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exported-certificates", required=True)
    parser.add_argument("--rank-scorer", required=True)
    parser.add_argument(
        "--source-glob",
        default="ecdlp_index_calculus_state/frontier_public_leaf_policy_p231_frozen_prefix_fixed_row_*_col15_selector_expanded_probe.json",
    )
    parser.add_argument("--label", choices=["forms_count_ge2", "rank_gain"], default="rank_gain")
    parser.add_argument("--calibration-end", type=int, default=3375)
    parser.add_argument("--max-conjunction-size", type=int, default=2)
    parser.add_argument("--min-calibration-hits", type=int, default=2)
    parser.add_argument("--min-calibration-precision", type=float, default=0.5)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    export_path = Path(args.exported_certificates)
    scorer_path = Path(args.rank_scorer)
    rows, errors = load_rows(
        load_json(export_path),
        load_json(scorer_path),
        build_window_map(parse_paths(args.source_glob)),
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
            "source_glob": args.source_glob,
        },
        "claim_status": (
            "SOURCE_NEIGHBORHOOD_RULE_VALIDATES"
            if selected and int_value(selected["validation"].get("positive_count")) > 0
            else "SOURCE_NEIGHBORHOOD_RULE_ABSTAINS_OR_MISSES_VALIDATION"
            if selected
            else "SOURCE_NEIGHBORHOOD_RULE_NO_VIABLE_CALIBRATION"
        ),
        "created_at": now_iso(),
        "errors": errors,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: labels come from exported known-factor certificates and the current factor-rank scorer.",
            "Features use source-neighborhood metadata before direct relation scanning and exclude public verification, relation count, rank, and operation-cost labels.",
            "A validating rule is a source-generator work order, not a deployed-curve speedup claim.",
        ],
        "parameters": {
            "calibration_end": args.calibration_end,
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
        "schema": "ecdlp.low_term_total2_source_neighborhood_rank_scout.v1",
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["split_summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"], "selected_rule": selected["rule"] if selected else None, "error_count": len(errors)}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
