#!/usr/bin/env python3
"""Scout selected-leaf signatures for the double ``[11,15]`` compatibility.

Coarse source metadata does not predict the clean double ``[11,15]`` event
pattern.  This scout moves one layer deeper without running direct witness
replay: for each source-charged collector attempt, it rebuilds the public
selected-leaf contexts and extracts selected leaf indices, leaf signatures, and
row-pair sharing features.

The result is a diagnostic for a cheaper pretest.  It does not charge a full
shared-product implementation and it does not claim a faster-than-rho algorithm.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any

import low_term_total2_fixed_leaf_shared_context_audit_probe as context_probe
import low_term_total2_fixed_leaf_shared_product_timing_probe as timing_probe
from low_term_total2_auxiliary_relation_event_assembly_scout import canonical_rows


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


def short_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()[:16]


def bucket_features(name: str, value: int, thresholds: tuple[int, ...]) -> set[str]:
    features = {f"{name}={value}"}
    for threshold in thresholds:
        if value <= threshold:
            features.add(f"{name}<={threshold}")
        if value >= threshold:
            features.add(f"{name}>={threshold}")
    return features


def source_case_index(source: dict[str, Any]) -> dict[tuple[str, int, str, int, tuple[str, ...]], dict[str, Any]]:
    index: dict[tuple[str, int, str, int, tuple[str, ...]], dict[str, Any]] = {}
    for policy_name, result in (source.get("policies") or {}).items():
        if not isinstance(result, dict):
            continue
        row_selector = (result.get("row_selector") or {}).get("selector")
        for row in result.get("stress_leaf_results") or []:
            if not isinstance(row, dict):
                continue
            key = (
                str(row.get("target")),
                int_value(row.get("transfer_index")),
                str(row.get("selector")),
                int_value(row.get("top_k")),
                canonical_rows(row.get("row_keys")),
            )
            index.setdefault(key, {**row, "source_policy": policy_name, "row_selector": row.get("row_selector") or row_selector})
    return index


def attempt_key(attempt: dict[str, Any]) -> tuple[str, int, str, int, tuple[str, ...]]:
    return (
        "22050.cf1@11731",
        int_value(attempt.get("transfer_index")),
        str(attempt.get("selector")),
        int_value(attempt.get("top_k")),
        canonical_rows(attempt.get("row_keys")),
    )


def signature_profile(source: dict[str, Any], source_case: dict[str, Any]) -> dict[str, Any]:
    _verifier, contexts, product_factor, _max_relations = timing_probe.selected_contexts_from_source_case(source, source_case)
    row_profiles = []
    signature_counter: Counter[str] = Counter()
    index_counter: Counter[int] = Counter()
    signature_by_index: dict[int, set[str]] = {}
    for context in contexts:
        row_sigs = []
        leaf_indices = sorted(int_value(leaf) for leaf in context.get("selected_leaf_indices") or [])
        for leaf_index in leaf_indices:
            leaf = context["components"]["leaves"][int(leaf_index)]
            signature = context_probe.leaf_signature(leaf)
            sig_key = context_probe.signature_key(signature)
            signature_counter[sig_key] += 1
            index_counter[int(leaf_index)] += 1
            signature_by_index.setdefault(int(leaf_index), set()).add(sig_key)
            row_sigs.append(
                {
                    "leaf_index": int(leaf_index),
                    "signature_hash": short_hash(signature),
                    "signature_key": sig_key,
                    "scout_positions": signature.get("scout_positions") or [],
                }
            )
        row_profiles.append(
            {
                "leaf_indices": leaf_indices,
                "row_key": context.get("row_key"),
                "signature_hashes": [row["signature_hash"] for row in row_sigs],
                "signature_keys": [row["signature_key"] for row in row_sigs],
                "signatures": row_sigs,
            }
        )
    leaf_index_shape = ";".join(",".join(str(leaf) for leaf in row["leaf_indices"]) for row in row_profiles)
    leaf_count_shape = ",".join(str(len(row["leaf_indices"])) for row in row_profiles)
    all_indices = sorted(index_counter)
    shared_indices = sorted(index for index, count in index_counter.items() if count >= 2)
    duplicate_signature_count = sum(count - 1 for count in signature_counter.values() if count > 1)
    shared_signature_count = sum(1 for count in signature_counter.values() if count >= 2)
    unique_signature_count = len(signature_counter)
    signature_multiset_hash = short_hash(sorted(signature_counter.items()))
    signature_set_hash = short_hash(sorted(signature_counter))
    row_signature_hashes = [short_hash(row["signature_keys"]) for row in row_profiles]
    return {
        "all_leaf_indices": all_indices,
        "duplicate_signature_count": duplicate_signature_count,
        "leaf_count_shape": leaf_count_shape,
        "leaf_index_shape": leaf_index_shape,
        "product_factor": product_factor,
        "row_count": len(row_profiles),
        "row_profiles": row_profiles,
        "row_signature_hashes": row_signature_hashes,
        "selected_leaf_occurrence_count": sum(index_counter.values()),
        "shared_leaf_indices": shared_indices,
        "shared_signature_count": shared_signature_count,
        "signature_multiset_hash": signature_multiset_hash,
        "signature_set_hash": signature_set_hash,
        "unique_leaf_index_count": len(all_indices),
        "unique_signature_count": unique_signature_count,
    }


def profile_features(profile: dict[str, Any], include_exact_signature: bool) -> set[str]:
    features: set[str] = {
        f"leaf_count_shape={profile.get('leaf_count_shape')}",
        f"leaf_index_shape={profile.get('leaf_index_shape')}",
        f"row_count={int_value(profile.get('row_count'))}",
        f"selected_leaf_occurrence_count={int_value(profile.get('selected_leaf_occurrence_count'))}",
        f"unique_leaf_index_count={int_value(profile.get('unique_leaf_index_count'))}",
        f"shared_leaf_index_count={len(profile.get('shared_leaf_indices') or [])}",
        f"shared_leaf_indices={','.join(str(index) for index in profile.get('shared_leaf_indices') or [])}",
        f"unique_signature_count={int_value(profile.get('unique_signature_count'))}",
        f"shared_signature_count={int_value(profile.get('shared_signature_count'))}",
        f"duplicate_signature_count={int_value(profile.get('duplicate_signature_count'))}",
    }
    for leaf_index in profile.get("all_leaf_indices") or []:
        features.add(f"has_leaf_index={int(leaf_index)}")
    for leaf_index in profile.get("shared_leaf_indices") or []:
        features.add(f"shared_leaf_index={int(leaf_index)}")
    features.update(bucket_features("unique_signature_count", int_value(profile.get("unique_signature_count")), (1, 2, 3, 4, 5)))
    features.update(bucket_features("shared_signature_count", int_value(profile.get("shared_signature_count")), (0, 1, 2, 3)))
    features.update(bucket_features("duplicate_signature_count", int_value(profile.get("duplicate_signature_count")), (0, 1, 2)))
    if include_exact_signature:
        features.add(f"signature_set_hash={profile.get('signature_set_hash')}")
        features.add(f"signature_multiset_hash={profile.get('signature_multiset_hash')}")
        for row_hash in profile.get("row_signature_hashes") or []:
            features.add(f"has_row_signature_hash={row_hash}")
    return features


def conjunctions(features: set[str], max_size: int) -> set[str]:
    ordered = sorted(features)
    result = set(ordered)
    for size in range(2, max_size + 1):
        for combo in combinations(ordered, size):
            result.add("|".join(combo))
    return result


def load_rows(
    collector: dict[str, Any],
    include_exact_signature: bool,
    max_conjunction_size: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    source_cache: dict[Path, dict[str, Any]] = {}
    source_index_cache: dict[Path, dict[tuple[str, int, str, int, tuple[str, ...]], dict[str, Any]]] = {}
    signature_cache: dict[tuple[str, int, str, int, tuple[str, ...]], dict[str, Any]] = {}
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for group in collector.get("groups") or []:
        if not isinstance(group, dict):
            continue
        window_start = int_value(group.get("window_start"))
        for attempt_index, attempt in enumerate(group.get("attempts") or []):
            if not isinstance(attempt, dict):
                continue
            source_path = Path(str(attempt.get("source_path") or ""))
            if not source_path.exists():
                errors.append({"attempt_index": attempt_index, "error": "missing_source", "source_path": str(source_path)})
                continue
            if source_path not in source_cache:
                source_cache[source_path] = load_json(source_path)
                source_index_cache[source_path] = source_case_index(source_cache[source_path])
            key = attempt_key(attempt)
            source_case = source_index_cache[source_path].get(key)
            if source_case is None:
                errors.append({"attempt_index": attempt_index, "error": "missing_source_case", "key": list(key), "source_path": str(source_path)})
                continue
            cache_key = (str(source_path), *key)
            if cache_key not in signature_cache:
                try:
                    signature_cache[cache_key] = signature_profile(source_cache[source_path], source_case)
                except Exception as exc:  # noqa: BLE001 - preserve research replay failures.
                    errors.append(
                        {
                            "attempt_index": attempt_index,
                            "error": "signature_profile_failed",
                            "message": str(exc),
                            "key": list(key),
                            "source_path": str(source_path),
                        }
                    )
                    continue
            profile = signature_cache[cache_key]
            support = str(attempt.get("support_multiset") or "")
            is_double = support == "11,15;11,15" and int_value(attempt.get("pos7_11111515_count")) >= 2
            rank_gain = int_value(attempt.get("rank_gain")) > 0
            features = conjunctions(profile_features(profile, include_exact_signature), max_conjunction_size)
            rows.append(
                {
                    "cost_over_rho": float_value(attempt.get("charged_ops_over_rho")),
                    "features": features,
                    "is_double_pos7_11_15": is_double,
                    "is_double_rank_gain": is_double and rank_gain,
                    "rank_gain": rank_gain,
                    "row": {
                        "attempt_index": attempt_index,
                        "cost_over_rho": attempt.get("charged_ops_over_rho"),
                        "is_double_pos7_11_15": is_double,
                        "is_double_rank_gain": is_double and rank_gain,
                        "leaf_count_shape": profile.get("leaf_count_shape"),
                        "leaf_index_shape": profile.get("leaf_index_shape"),
                        "public_key_verified": attempt.get("public_key_verified"),
                        "rank": attempt.get("rank"),
                        "rank_gain": attempt.get("rank_gain"),
                        "row_keys": attempt.get("row_keys") or [],
                        "selected_leaf_occurrence_count": profile.get("selected_leaf_occurrence_count"),
                        "shared_leaf_indices": profile.get("shared_leaf_indices"),
                        "shared_signature_count": profile.get("shared_signature_count"),
                        "signature_multiset_hash": profile.get("signature_multiset_hash"),
                        "signature_set_hash": profile.get("signature_set_hash"),
                        "source_path": str(source_path),
                        "support_multiset": support,
                        "transfer_index": attempt.get("transfer_index"),
                        "unique_leaf_index_count": profile.get("unique_leaf_index_count"),
                        "unique_signature_count": profile.get("unique_signature_count"),
                        "window": group.get("window"),
                    },
                    "transfer_index": int_value(attempt.get("transfer_index")),
                    "window_start": window_start,
                }
            )
    return sorted(rows, key=lambda item: (item["window_start"], item["transfer_index"], str(item["row"].get("source_path")))), errors


def split_rows(rows: list[dict[str, Any]], calibration_end: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return (
        [row for row in rows if int_value(row.get("window_start")) <= calibration_end],
        [row for row in rows if int_value(row.get("window_start")) > calibration_end],
    )


def is_positive(row: dict[str, Any], label_name: str) -> bool:
    if label_name == "double_pos7_11_15":
        return bool(row.get("is_double_pos7_11_15"))
    if label_name == "double_rank_gain":
        return bool(row.get("is_double_rank_gain"))
    if label_name == "rank_gain":
        return bool(row.get("rank_gain"))
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
        return "SCOUT_POS7_LEAF_SIGNATURE_NO_VIABLE_CALIBRATION_RULE"
    validation = selected.get("validation") if isinstance(selected.get("validation"), dict) else {}
    positives = int_value(validation.get("positive_count"))
    cost = validation.get("cost_per_positive_over_rho")
    if positives <= 0:
        return "SCOUT_POS7_LEAF_SIGNATURE_RULE_MISSES_VALIDATION"
    if cost is not None and float_value(cost) < 1.0:
        return "SCOUT_POS7_LEAF_SIGNATURE_RULE_BELOW_RHO"
    return "SCOUT_POS7_LEAF_SIGNATURE_RULE_VALIDATES_ABOVE_RHO"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collector", required=True)
    parser.add_argument("--calibration-end", type=int, default=3831)
    parser.add_argument("--label", choices=["double_pos7_11_15", "double_rank_gain", "rank_gain"], default="double_rank_gain")
    parser.add_argument("--max-conjunction-size", type=int, default=2)
    parser.add_argument("--min-calibration-hits", type=int, default=2)
    parser.add_argument("--min-calibration-precision", type=float, default=0.5)
    parser.add_argument("--include-exact-signature", action="store_true")
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    collector_path = Path(args.collector)
    collector = load_json(collector_path)
    rows, errors = load_rows(collector, args.include_exact_signature, args.max_conjunction_size)
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
            "collector": str(collector_path),
        },
        "claim_status": claim_status(selected),
        "created_at": now_iso(),
        "errors": errors,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: selected-leaf contexts are rebuilt from public source rows but not charged as a full collector.",
            "Default rules exclude exact full leaf-signature hashes; enable them only as a diagnostic overfit check.",
            "A validating rule is a pretest work order, not a completed faster-than-rho ECDLP algorithm.",
        ],
        "parameters": {
            "calibration_end": args.calibration_end,
            "include_exact_signature": args.include_exact_signature,
            "label": args.label,
            "max_conjunction_size": args.max_conjunction_size,
            "min_calibration_hits": args.min_calibration_hits,
            "min_calibration_precision": args.min_calibration_precision,
        },
        "rows": [row["row"] for row in rows],
        "rules": rules[:20],
        "schema": "ecdlp.low_term_total2_scout_pos7_leaf_signature_pretest_scout.v1",
        "selected_rule": selected,
        "split_summary": {
            "calibration_positive_count": sum(1 for row in calibration if is_positive(row, args.label)),
            "calibration_row_count": len(calibration),
            "validation_positive_count": sum(1 for row in validation if is_positive(row, args.label)),
            "validation_row_count": len(validation),
        },
    }
    write_json(Path(args.out), payload)
    print(
        json.dumps(
            {
                "claim_status": payload["claim_status"],
                "error_count": len(errors),
                "selected_rule": selected["rule"] if selected else None,
                "split_summary": payload["split_summary"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
