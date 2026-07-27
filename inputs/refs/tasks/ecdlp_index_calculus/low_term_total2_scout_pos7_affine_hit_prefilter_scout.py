#!/usr/bin/env python3
"""Scout fixed-branch affine-hit prefilters for the scout-7 row side.

The cacheability audit showed that the scout-7 branch/leaf is fixed, while the
row pool and hit polynomial are transfer-specific.  This scout stays below
relation-form construction and asks three narrower questions:

* Does fixed-branch affine matching alone select the rank-gain positives?
* Can source/salt metadata predict those affine-hit groups before row-side work?
* Can root-hit counts predict them before candidate-point equality?

Affine matching here means only ``candidate_point == scheduled_row.point`` for
the fixed scout-7 branch.  No q coefficient, RHS, rank, derived secret, or
public-key verification is used to form the affine gate.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any

from low_term_total2_scout_pos7_source_charged_collector import int_value, ratio, write_json


SALT_RE = re.compile(r":salt(\d+)$")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def bucket_features(name: str, value: int, thresholds: tuple[int, ...]) -> set[str]:
    features = {f"{name}={value}"}
    for threshold in thresholds:
        if value <= threshold:
            features.add(f"{name}<={threshold}")
        if value >= threshold:
            features.add(f"{name}>={threshold}")
    return features


def gap_bucket(gap: int) -> str:
    if gap <= 0:
        return "0"
    if gap <= 2:
        return "1_2"
    if gap <= 4:
        return "3_4"
    if gap <= 8:
        return "5_8"
    return "9_plus"


def offset_bucket(offset: int) -> str:
    if offset <= 0:
        return "0"
    if offset <= 1:
        return "1"
    if offset <= 3:
        return "2_3"
    if offset <= 5:
        return "4_5"
    return "6_7"


def salt_from_row_key(row_key: str) -> int:
    match = SALT_RE.search(str(row_key))
    return int(match.group(1)) if match else -1


def conjunctions(features: set[str], max_size: int) -> set[str]:
    ordered = sorted(features)
    result = set(ordered)
    for size in range(2, max_size + 1):
        for combo in combinations(ordered, size):
            result.add("|".join(combo))
    return result


def context_cache_by_source(cacheability: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    for row in cacheability.get("rows") or []:
        if not isinstance(row, dict):
            continue
        out.setdefault(str(row.get("source_path") or ""), []).append(row)
    for rows in out.values():
        rows.sort(key=lambda item: int_value(item.get("context_index")))
    return out


def row_cost(row: dict[str, Any], model: str) -> float:
    scan = row.get("scan") if isinstance(row.get("scan"), dict) else {}
    costs = scan.get("model_ops_over_rho") if isinstance(scan.get("model_ops_over_rho"), dict) else {}
    return float_value(costs.get(model))


def root_gate_cost(row: dict[str, Any]) -> float:
    scan = row.get("scan") if isinstance(row.get("scan"), dict) else {}
    rho = int_value(scan.get("rho"), 1)
    total = 0
    for context in scan.get("context_rows") or []:
        if not isinstance(context, dict):
            continue
        total += (
            int_value(context.get("selected_leaf_count"))
            + int_value(context.get("selected_hit_roots"))
            + int_value(context.get("raw_root_hit_candidate_count"))
        )
    return float(total) / max(1, rho)


def affine_extra_cost(row: dict[str, Any]) -> float:
    scan = row.get("scan") if isinstance(row.get("scan"), dict) else {}
    rho = int_value(scan.get("rho"), 1)
    total = 0
    for context in scan.get("context_rows") or []:
        if not isinstance(context, dict):
            continue
        # One candidate-point addition is needed when the fixed branch has any
        # row-side root-hit candidates in that context.
        if int_value(context.get("raw_root_hit_candidate_count")) > 0:
            total += 1
    return float(total) / max(1, rho)


def is_positive(row: dict[str, Any]) -> bool:
    return bool(row.get("has_rank_gain_stop"))


def affine_accepts(row: dict[str, Any]) -> bool:
    scan = row.get("scan") if isinstance(row.get("scan"), dict) else {}
    affine_matches = sum(int_value(context.get("affine_match_count")) for context in scan.get("context_rows") or [])
    return affine_matches >= 2


def is_affine_positive(row: dict[str, Any]) -> bool:
    return is_positive(row) and affine_accepts(row)


def source_features(row: dict[str, Any], context_rows: list[dict[str, Any]], include_residue: bool) -> set[str]:
    transfer = int_value(row.get("first_transfer_index"))
    window_start = int_value(row.get("window_start"))
    salts = [salt_from_row_key(str(context.get("row_key") or "")) for context in context_rows]
    salts = sorted(salt for salt in salts if salt >= 0)
    gap = salts[-1] - salts[0] if len(salts) >= 2 else 0
    features = {
        f"context_count={len(context_rows)}",
        f"salt_count={len(salts)}",
        f"salt_gap_bucket={gap_bucket(gap)}",
        f"transfer_offset_bucket={offset_bucket(transfer - window_start)}",
    }
    features.update(bucket_features("salt_gap", gap, (0, 1, 2, 4, 5, 8, 12)))
    features.update(bucket_features("transfer_offset", transfer - window_start, (0, 1, 2, 3, 5, 7)))
    if salts:
        features.add(f"salt_min_bucket={gap_bucket(salts[0] - 160)}")
        features.add(f"salt_max_bucket={gap_bucket(salts[-1] - 160)}")
        features.update(bucket_features("salt_min", salts[0], (160, 164, 168, 172, 176, 180)))
        features.update(bucket_features("salt_max", salts[-1], (164, 168, 172, 176, 180)))
    if include_residue:
        features.update(
            {
                f"salt_pair={','.join(str(salt) for salt in salts)}",
                f"salt_min_mod_8={salts[0] % 8 if salts else 'none'}",
                f"salt_max_mod_8={salts[-1] % 8 if salts else 'none'}",
                f"salt_sum_mod_8={sum(salts) % 8 if salts else 'none'}",
                f"transfer_mod_8={transfer % 8}",
            }
        )
    return features


def root_features(row: dict[str, Any]) -> set[str]:
    scan = row.get("scan") if isinstance(row.get("scan"), dict) else {}
    raw_counts = [int_value(context.get("raw_root_hit_candidate_count")) for context in scan.get("context_rows") or []]
    root_counts = [int_value(context.get("selected_hit_roots")) for context in scan.get("context_rows") or []]
    total_raw = sum(raw_counts)
    total_roots = sum(root_counts)
    features = {
        f"context_raw_root_hit_candidate_count_multiset={','.join(str(value) for value in sorted(raw_counts))}",
        f"context_selected_hit_roots_multiset={','.join(str(value) for value in sorted(root_counts))}",
        f"has_context_raw_ge_2={any(value >= 2 for value in raw_counts)}",
        f"has_two_contexts_with_roots={sum(1 for value in root_counts if value > 0) >= 2}",
    }
    for name, value in (
        ("total_raw_root_hit_candidate_count", total_raw),
        ("total_selected_hit_roots", total_roots),
        ("max_context_raw_root_hit_candidate_count", max(raw_counts or [0])),
        ("max_context_selected_hit_roots", max(root_counts or [0])),
    ):
        features.add(f"{name}={value}")
        features.update(bucket_features(name, value, (0, 1, 2, 3, 4)))
    return features


def split_rows(rows: list[dict[str, Any]], calibration_end: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return (
        [row for row in rows if int_value(row.get("window_start")) <= calibration_end],
        [row for row in rows if int_value(row.get("window_start")) > calibration_end],
    )


def evaluate_rule(rule: str, rows: list[dict[str, Any]], feature_key: str, scan_cost_model: str) -> dict[str, Any]:
    selected = [row for row in rows if rule in row[feature_key]]
    positives = [row for row in selected if is_affine_positive(row)]
    rejected_positives = [row for row in rows if rule not in row[feature_key] and is_affine_positive(row)]
    scan_cost = sum(row_cost(row, scan_cost_model) for row in selected)
    return {
        "affine_positive_label": "rank_gain_stop && affine_accepts_fixed_scout7_branch",
        "cost_per_positive_over_rho": round(scan_cost / len(positives), 8) if positives else None,
        "positive_count": len(positives),
        "precision": round(len(positives) / len(selected), 8) if selected else None,
        "rank_gain_selected_count": sum(1 for row in selected if is_positive(row)),
        "recall": round(len(positives) / (len(positives) + len(rejected_positives)), 8)
        if positives or rejected_positives
        else None,
        "rejected_positive_count": len(rejected_positives),
        "scan_cost_over_rho": round(scan_cost, 8),
        "selected_count": len(selected),
        "selected_groups": [row["group"] for row in selected],
    }


def choose_rules(
    calibration: list[dict[str, Any]],
    validation: list[dict[str, Any]],
    feature_key: str,
    scan_cost_model: str,
    min_hits: int,
    min_precision: float,
) -> list[dict[str, Any]]:
    rules: list[dict[str, Any]] = []
    for rule in sorted({feature for row in calibration for feature in row[feature_key]}):
        cal = evaluate_rule(rule, calibration, feature_key, scan_cost_model)
        if int_value(cal.get("positive_count")) < min_hits:
            continue
        precision = cal.get("precision")
        if precision is None or float(precision) < min_precision:
            continue
        rules.append(
            {
                "calibration": cal,
                "feature_count": rule.count("|") + 1,
                "rule": rule,
                "validation": evaluate_rule(rule, validation, feature_key, scan_cost_model),
            }
        )
    rules.sort(
        key=lambda item: (
            -float((item.get("calibration") or {}).get("precision") or 0.0),
            -int_value((item.get("calibration") or {}).get("positive_count")),
            int_value(item.get("feature_count")),
            float((item.get("calibration") or {}).get("cost_per_positive_over_rho") or 999999.0),
            str(item.get("rule")),
        )
    )
    return rules


def validation_hit_rules(rules: list[dict[str, Any]], limit: int = 10) -> list[dict[str, Any]]:
    hits = [rule for rule in rules if int_value((rule.get("validation") or {}).get("positive_count")) > 0]
    hits.sort(
        key=lambda item: (
            float((item.get("validation") or {}).get("cost_per_positive_over_rho") or 999999.0),
            -float((item.get("validation") or {}).get("precision") or 0.0),
            int_value(item.get("feature_count")),
            str(item.get("rule")),
        )
    )
    return hits[:limit]


def affine_gate_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    selected = [row for row in rows if affine_accepts(row)]
    positives = [row for row in selected if is_positive(row)]
    rejected_positives = [row for row in rows if not affine_accepts(row) and is_positive(row)]
    models = {}
    for model in (
        "pair_and_row_cached",
        "leaf_event_only_lower_bound",
        "pair_setup_cached",
        "single_scout_setup",
        "targeted_full_setup",
    ):
        cost = sum(row_cost(row, model) for row in rows)
        models[model] = {
            "cost_per_positive_over_rho": round(cost / len(positives), 8) if positives else None,
            "total_cost_over_rho": round(cost, 8),
        }
    root_gate = sum(root_gate_cost(row) for row in rows)
    affine_extra = sum(affine_extra_cost(row) for row in rows)
    return {
        "affine_extra_cost_over_rho": round(affine_extra, 8),
        "model_costs_charged_all_groups": models,
        "positive_count": len(positives),
        "precision": round(len(positives) / len(selected), 8) if selected else None,
        "recall": round(len(positives) / (len(positives) + len(rejected_positives)), 8)
        if positives or rejected_positives
        else None,
        "rejected_positive_count": len(rejected_positives),
        "root_gate_cost_over_rho": round(root_gate, 8),
        "selected_count": len(selected),
        "selected_groups": [row["group"] for row in selected],
    }


def claim_status(validation_affine: dict[str, Any], source_hits: list[dict[str, Any]], root_hits: list[dict[str, Any]]) -> str:
    affine_cost = ((validation_affine.get("model_costs_charged_all_groups") or {}).get("leaf_event_only_lower_bound") or {}).get(
        "cost_per_positive_over_rho"
    )
    if int_value(validation_affine.get("positive_count")) <= 0:
        return "SCOUT_POS7_AFFINE_HIT_PREFILTER_MISSES_VALIDATION"
    if source_hits:
        return "SCOUT_POS7_AFFINE_HIT_PREFILTER_SOURCE_RULE_VALIDATES"
    if root_hits:
        return "SCOUT_POS7_AFFINE_HIT_PREFILTER_ROOT_RULE_VALIDATES"
    if affine_cost is not None and float(affine_cost) < 1.0:
        return "SCOUT_POS7_AFFINE_HIT_GATE_VALIDATES_ONLY_AFTER_ROW_SIDE_WORK"
    return "SCOUT_POS7_AFFINE_HIT_PREFILTER_ABOVE_RHO"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--branch-cost", required=True)
    parser.add_argument("--cacheability", required=True)
    parser.add_argument("--calibration-end", type=int, default=3831)
    parser.add_argument("--max-conjunction-size", type=int, default=2)
    parser.add_argument("--min-calibration-hits", type=int, default=2)
    parser.add_argument("--min-calibration-precision", type=float, default=0.5)
    parser.add_argument("--include-source-residue-features", action="store_true")
    parser.add_argument("--scan-cost-model", default="leaf_event_only_lower_bound")
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    branch_path = Path(args.branch_cost)
    cache_path = Path(args.cacheability)
    branch = load_json(branch_path)
    cacheability = load_json(cache_path)
    contexts_by_source = context_cache_by_source(cacheability)
    rows: list[dict[str, Any]] = []
    for row in branch.get("rows") or []:
        if not isinstance(row, dict):
            continue
        source_path = str(row.get("source_path") or "")
        contexts = contexts_by_source.get(source_path, [])
        source_feats = source_features(row, contexts, args.include_source_residue_features)
        root_feats = root_features(row)
        rows.append(
            {
                **row,
                "group": {
                    "accepted": bool(row.get("accepted")),
                    "first_transfer_index": row.get("first_transfer_index"),
                    "has_rank_gain_stop": bool(row.get("has_rank_gain_stop")),
                    "source_path": source_path,
                    "window": row.get("window"),
                    "window_start": row.get("window_start"),
                },
                "root_features": conjunctions(root_feats, args.max_conjunction_size),
                "source_features": conjunctions(source_feats, args.max_conjunction_size),
            }
        )
    calibration, validation = split_rows(rows, args.calibration_end)
    source_rules = choose_rules(
        calibration,
        validation,
        "source_features",
        args.scan_cost_model,
        args.min_calibration_hits,
        args.min_calibration_precision,
    )
    root_rules = choose_rules(
        calibration,
        validation,
        "root_features",
        args.scan_cost_model,
        args.min_calibration_hits,
        args.min_calibration_precision,
    )
    validation_source_hits = validation_hit_rules(source_rules)
    validation_root_hits = validation_hit_rules(root_rules)
    validation_affine = affine_gate_summary(validation)
    payload = {
        "artifacts": {
            "branch_cost": str(branch_path),
            "cacheability": str(cache_path),
        },
        "claim_status": claim_status(validation_affine, validation_source_hits, validation_root_hits),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: affine-hit features use fixed-branch candidate-point equality, not relation-form coefficients, rank, secret recovery, or public-key verification.",
            "Source features are available before row-side work; root features require fixed-leaf row-side association.",
            "The default scan cost model is the optimistic leaf/event lower bound and must not be counted as a completed speedup.",
        ],
        "parameters": {
            "rule_positive_label": "rank_gain_stop && affine_accepts_fixed_scout7_branch",
            "calibration_end": args.calibration_end,
            "include_source_residue_features": args.include_source_residue_features,
            "max_conjunction_size": args.max_conjunction_size,
            "min_calibration_hits": args.min_calibration_hits,
            "min_calibration_precision": args.min_calibration_precision,
            "scan_cost_model": args.scan_cost_model,
        },
        "rows": [row["group"] for row in rows],
        "schema": "ecdlp.low_term_total2_scout_pos7_affine_hit_prefilter_scout.v1",
        "source_rule_count": len(source_rules),
        "source_rules": source_rules[:20],
        "split_summary": {
            "calibration_affine_gate": affine_gate_summary(calibration),
            "validation_affine_gate": validation_affine,
        },
        "root_rule_count": len(root_rules),
        "root_rules": root_rules[:20],
        "validation_root_hit_rule_count": len(validation_root_hits),
        "validation_root_hit_rules": validation_root_hits,
        "validation_source_hit_rule_count": len(validation_source_hits),
        "validation_source_hit_rules": validation_source_hits,
    }
    write_json(Path(args.out), payload)
    print(
        json.dumps(
            {
                "claim_status": payload["claim_status"],
                "source_rule_count": len(source_rules),
                "root_rule_count": len(root_rules),
                "split_summary": payload["split_summary"],
                "validation_source_hit_rule_count": len(validation_source_hits),
                "validation_root_hit_rule_count": len(validation_root_hits),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
