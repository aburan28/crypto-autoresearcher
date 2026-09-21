#!/usr/bin/env python3
"""Scout pre-replay source metadata for the double ``[11,15]`` event rows.

The source-charged collector found a clean compatibility signature:
``scout_pos=7`` with support multiset ``11,15;11,15``.  That signature is still
too expensive because the current collector discovers it by direct replay.

This scout consumes a collector artifact and asks whether metadata already
present before direct replay can select the double-event rows.  Replay-derived
fields such as public-key verification are excluded unless explicitly enabled.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import json
import re
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any


SALT_RE = re.compile(r":salt(\d+)$")


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


def salt_values(row_keys: Any) -> list[int]:
    salts: list[int] = []
    for row_key in row_keys or []:
        match = SALT_RE.search(str(row_key))
        if match:
            salts.append(int(match.group(1)))
    return sorted(salts)


def bucket_features(name: str, value: int, thresholds: tuple[int, ...]) -> set[str]:
    features = {f"{name}={value}"}
    for threshold in thresholds:
        if value <= threshold:
            features.add(f"{name}<={threshold}")
        if value >= threshold:
            features.add(f"{name}>={threshold}")
    return features


def row_features(row: dict[str, Any], include_residue: bool, include_replay_derived: bool) -> set[str]:
    attempt_index = int_value(row.get("attempt_index"))
    transfer = int_value(row.get("transfer_index"))
    selected_leaf_count = int_value(row.get("selected_leaf_count"))
    selected_row_count = int_value(row.get("selected_row_count"))
    salts = salt_values(row.get("row_keys"))
    salt_gap = salts[-1] - salts[0] if len(salts) >= 2 else 0
    features: set[str] = {
        f"attempt_index={attempt_index}",
        f"row_selector={row.get('row_selector')}",
        f"selector={row.get('selector')}",
        f"source_policy={row.get('source_policy')}",
        f"top_k={int_value(row.get('top_k'))}",
        f"selected_leaf_count={selected_leaf_count}",
        f"selected_row_count={selected_row_count}",
        f"salt_count={len(salts)}",
        f"salt_gap={salt_gap}",
    }
    features.update(bucket_features("attempt_index", attempt_index, (0, 1, 2, 3)))
    features.update(bucket_features("selected_leaf_count", selected_leaf_count, (1, 2, 3, 4, 5)))
    features.update(bucket_features("selected_row_count", selected_row_count, (1, 2, 3)))
    features.update(bucket_features("salt_gap", salt_gap, (0, 1, 2, 4, 8, 12)))
    if include_residue:
        features.update(
            {
                f"transfer_mod_8={transfer % 8}",
                f"transfer_mod_16={transfer % 16}",
                f"salt_sum_mod_8={sum(salts) % 8 if salts else 0}",
                f"salt_min_mod_8={salts[0] % 8 if salts else 0}",
                f"salt_max_mod_8={salts[-1] % 8 if salts else 0}",
            }
        )
    if include_replay_derived:
        features.update(
            {
                f"public_key_verified={bool(row.get('public_key_verified'))}",
                f"source_verified={bool(row.get('source_verified'))}",
                f"rank={int_value(row.get('rank'))}",
            }
        )
        features.update(bucket_features("rank", int_value(row.get("rank")), (0, 1, 2, 3)))
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
    include_residue: bool,
    include_replay_derived: bool,
    max_conjunction_size: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for group in collector.get("groups") or []:
        if not isinstance(group, dict):
            continue
        window_start = int_value(group.get("window_start"))
        for attempt_index, attempt in enumerate(group.get("attempts") or []):
            if not isinstance(attempt, dict):
                continue
            attempt_with_index = {**attempt, "attempt_index": attempt_index}
            support = str(attempt.get("support_multiset") or attempt.get("point_match_support_multiset") or "")
            pos7_count = int_value(
                attempt.get("pos7_11111515_count"),
                int_value(attempt.get("pos7_11111515_point_match_count")),
            )
            is_double = support == "11,15;11,15" and pos7_count >= 2
            rank_gain = int_value(attempt.get("rank_gain")) > 0
            features = conjunctions(
                row_features(attempt_with_index, include_residue, include_replay_derived),
                max_conjunction_size,
            )
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
                        "public_key_verified": attempt.get("public_key_verified"),
                        "rank": attempt.get("rank"),
                        "rank_gain": attempt.get("rank_gain"),
                        "row_keys": attempt.get("row_keys") or [],
                        "row_selector": attempt.get("row_selector"),
                        "selected_leaf_count": attempt.get("selected_leaf_count"),
                        "selected_row_count": attempt.get("selected_row_count"),
                        "source_path": attempt.get("source_path"),
                        "source_policy": attempt.get("source_policy"),
                        "support_multiset": attempt.get("support_multiset"),
                        "top_k": attempt.get("top_k"),
                        "transfer_index": attempt.get("transfer_index"),
                        "window": group.get("window"),
                    },
                    "transfer_index": int_value(attempt.get("transfer_index")),
                    "window_start": window_start,
                }
            )
    return sorted(rows, key=lambda item: (item["window_start"], item["transfer_index"], str(item["row"].get("source_path"))))


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
        return "SCOUT_POS7_SOURCE_METADATA_NO_VIABLE_CALIBRATION_RULE"
    validation = selected.get("validation") if isinstance(selected.get("validation"), dict) else {}
    positives = int_value(validation.get("positive_count"))
    cost = validation.get("cost_per_positive_over_rho")
    if positives <= 0:
        return "SCOUT_POS7_SOURCE_METADATA_RULE_MISSES_VALIDATION"
    if cost is not None and float_value(cost) < 1.0:
        return "SCOUT_POS7_SOURCE_METADATA_RULE_BELOW_RHO"
    return "SCOUT_POS7_SOURCE_METADATA_RULE_VALIDATES_ABOVE_RHO"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collector", required=True)
    parser.add_argument("--calibration-end", type=int, default=3831)
    parser.add_argument("--label", choices=["double_pos7_11_15", "double_rank_gain", "rank_gain"], default="double_rank_gain")
    parser.add_argument("--max-conjunction-size", type=int, default=2)
    parser.add_argument("--min-calibration-hits", type=int, default=2)
    parser.add_argument("--min-calibration-precision", type=float, default=0.5)
    parser.add_argument("--include-residue", action="store_true")
    parser.add_argument("--include-replay-derived", action="store_true")
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    collector_path = Path(args.collector)
    collector = load_json(collector_path)
    rows = load_rows(
        collector,
        args.include_residue,
        args.include_replay_derived,
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
            "collector": str(collector_path),
        },
        "claim_status": claim_status(selected),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: rows come from the source-charged collector attempt stream.",
            "Default features exclude replay-derived public-key/rank data and exact salt/transfer residues.",
            "A validating metadata rule is a source-order work order, not a completed ECDLP speedup.",
        ],
        "parameters": {
            "calibration_end": args.calibration_end,
            "include_replay_derived": args.include_replay_derived,
            "include_residue": args.include_residue,
            "label": args.label,
            "max_conjunction_size": args.max_conjunction_size,
            "min_calibration_hits": args.min_calibration_hits,
            "min_calibration_precision": args.min_calibration_precision,
        },
        "rows": [row["row"] for row in rows],
        "rules": rules[:20],
        "schema": "ecdlp.low_term_total2_scout_pos7_source_metadata_pretest_scout.v1",
        "selected_rule": selected,
        "split_summary": {
            "calibration_positive_count": sum(1 for row in calibration if is_positive(row, args.label)),
            "calibration_row_count": len(calibration),
            "validation_positive_count": sum(1 for row in validation if is_positive(row, args.label)),
            "validation_row_count": len(validation),
        },
    }
    write_json(Path(args.out), payload)
    print(json.dumps({"claim_status": payload["claim_status"], "split_summary": payload["split_summary"], "selected_rule": selected["rule"] if selected else None}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
