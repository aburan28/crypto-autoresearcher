#!/usr/bin/env python3
"""P586 block-level relation-supply yield predictor.

The scout trains only on source-public metadata joined to past verifier labels,
then evaluates a fresh block with labels used only after selection.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import low_term_total2_p570_pre_hit_source_feature_scout as p570


STATE_DIR = Path("ecdlp_index_calculus_state")
TRAIN_PAIRS = [
    (
        STATE_DIR / "low_term_total2_order9887_p566_leaf16_frozen_root_saved_source_20605_20616_probe.json",
        STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p566_order9887_leaf16_frozen_root_saved_20605_20616_density_gate_probe.json",
    ),
    (
        STATE_DIR / "low_term_total2_order9887_p567_leaf16_phase_route_source_20617_20628_probe.json",
        STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p567_order9887_phase_route_20617_20628_density_gate_probe.json",
    ),
    (
        STATE_DIR / "low_term_total2_order9887_p568_leaf16_right207_volume_source_20629_20640_probe.json",
        STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p568_order9887_right207_volume_20629_20640_density_gate_probe.json",
    ),
    (
        STATE_DIR / "low_term_total2_order9887_p570_leaf16_pre_hit_source_20641_20652_probe.json",
        STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p570_order9887_pre_hit_source_20641_20652_density_gate_probe.json",
    ),
    (
        STATE_DIR / "low_term_total2_order9887_p571_leaf16_pre_hit_source_20653_20664_probe.json",
        STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p571_order9887_pre_hit_source_20653_20664_density_gate_probe.json",
    ),
    (
        STATE_DIR / "low_term_total2_order9887_p572_leaf16_drift_scheduler_source_20665_20676_probe.json",
        STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p572_order9887_drift_scheduler_20665_20676_density_gate_probe.json",
    ),
    (
        STATE_DIR / "low_term_total2_order9887_p573_leaf16_latest_family_source_20677_20688_probe.json",
        STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p573_order9887_latest_family_20677_20688_density_gate_probe.json",
    ),
    (
        STATE_DIR / "low_term_total2_order9887_p574_leaf16_phase_transition_source_20689_20700_probe.json",
        STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p574_order9887_phase_transition_20689_20700_density_gate_probe.json",
    ),
    (
        STATE_DIR / "low_term_total2_order9887_p575_leaf16_source_family_motif_source_20701_20712_probe.json",
        STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p575_order9887_source_family_motif_20701_20712_density_gate_probe.json",
    ),
    (
        STATE_DIR / "low_term_total2_order9887_p576_leaf16_near_rho_family_bank_source_20713_20724_probe.json",
        STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p576_order9887_near_rho_family_bank_20713_20724_density_gate_probe.json",
    ),
    (
        STATE_DIR / "low_term_total2_order9887_p577_leaf16_motif_extension_source_20725_20736_probe.json",
        STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p577_order9887_motif_extension_20725_20736_density_gate_probe.json",
    ),
    (
        STATE_DIR / "low_term_total2_order9887_p578_leaf16_phase_aware_motif_source_20737_20748_probe.json",
        STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p578_order9887_phase_aware_motif_20737_20748_density_gate_probe.json",
    ),
    (
        STATE_DIR / "low_term_total2_order9887_p579_relation_supply_source_20749_20760_probe.json",
        STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p579_order9887_relation_supply_20749_20760_density_gate_probe.json",
    ),
    (
        STATE_DIR / "low_term_total2_order9887_p580_phase8_relation_supply_source_20761_20772_probe.json",
        STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p580_order9887_phase8_relation_supply_20761_20772_density_gate_probe.json",
    ),
    (
        STATE_DIR / "low_term_total2_order9887_p581_drift_anchor9_source_20773_20784_probe.json",
        STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p581_order9887_drift_anchor9_20773_20784_density_gate_probe.json",
    ),
    (
        STATE_DIR / "low_term_total2_order9887_p582_feature_delta_source_20785_20796_probe.json",
        STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p582_order9887_feature_delta_20785_20796_density_gate_probe.json",
    ),
    (
        STATE_DIR / "low_term_total2_order9887_p583_salt205_rank_split_source_20797_20808_probe.json",
        STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p583_order9887_salt205_rank_split_20797_20808_density_gate_probe.json",
    ),
    (
        STATE_DIR / "low_term_total2_order9887_p584_phase8_right208_anchor9_source_20809_20820_probe.json",
        STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p584_order9887_phase8_right208_anchor9_20809_20820_density_gate_probe.json",
    ),
    (
        STATE_DIR / "low_term_total2_order9887_p585_phase11_right207_rank_growth_source_20821_20832_probe.json",
        STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p585_order9887_phase11_right207_rank_growth_20821_20832_density_gate_probe.json",
    ),
]
DEFAULT_VALIDATION_SOURCE = STATE_DIR / "low_term_total2_order9887_p586_block_yield_source_20833_20844_probe.json"
DEFAULT_VALIDATION_GATE = (
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p586_order9887_block_yield_20833_20844_density_gate_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_p586_block_yield_predictor_20833_20844_probe.json"

TOP_NS = [1, 2, 3, 5, 8, 13, 21]
OBJECTIVES = ["below", "verified", "rank3"]
MIN_BACKTEST_TRAIN_BLOCKS = 4
MAX_NONTRIVIAL_SELECTED_FRACTION = 0.25


Feature = dict[str, Any]
FeatureKey = tuple[str, str]
Config = tuple[str, str, int]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def ratio(numerator: int | float, denominator: int | float) -> float | None:
    if not denominator:
        return None
    return round(float(numerator) / float(denominator), 8)


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


def parse_path_list(raw: str | None) -> list[Path] | None:
    if not raw:
        return None
    return [Path(item.strip()) for item in raw.split(",") if item.strip()]


def block_name(path: Path) -> str:
    match = re.search(r"_p(\d+)_", path.name)
    if match:
        return f"p{match.group(1)}"
    return path.stem


def load_block(source_path: Path, gate_path: Path) -> list[Feature]:
    rows = p570.source_rows([source_path], p570.gate_labels([gate_path]), block_name(source_path))
    for row in rows:
        row["block"] = block_name(source_path)
    return rows


def load_blocks(source_paths: list[Path], gate_paths: list[Path]) -> list[list[Feature]]:
    if len(source_paths) != len(gate_paths):
        raise ValueError(f"source/gate count mismatch: {len(source_paths)} sources, {len(gate_paths)} gates")
    return [load_block(source, gate) for source, gate in zip(source_paths, gate_paths)]


def feature_values(row: Feature) -> list[FeatureKey]:
    cached = row.get("_feature_values")
    if cached is not None:
        return cached
    phase = str(row["transfer_mod12"])
    mod7 = str(row["transfer_mod7"])
    salt_right = str(row["salt_right"])
    anchor = str(row["right_anchor"])
    row_pair = str(row["row_pair"])
    leaf = str(row["leaf_signature"])
    selector = str(row["base_selector"])
    role = str(row["policy_role"])
    values = [
        ("phase", phase),
        ("mod7", mod7),
        ("phase_mod7", f"{phase}|{mod7}"),
        ("salt_right", salt_right),
        ("right_anchor", anchor),
        ("row_pair", row_pair),
        ("leaf_signature", leaf),
        ("base_selector", selector),
        ("policy_role", role),
        ("phase_salt", f"{phase}|{salt_right}"),
        ("phase_anchor", f"{phase}|{anchor}"),
        ("salt_anchor", f"{salt_right}|{anchor}"),
        ("phase_salt_anchor", f"{phase}|{salt_right}|{anchor}"),
        ("phase_mod7_salt_anchor", f"{phase}|{mod7}|{salt_right}|{anchor}"),
        ("phase_row_pair_anchor", f"{phase}|{row_pair}|{anchor}"),
        ("phase_mod7_row_pair_anchor", f"{phase}|{mod7}|{row_pair}|{anchor}"),
        ("phase_leaf", f"{phase}|{leaf}"),
        ("phase_mod7_leaf", f"{phase}|{mod7}|{leaf}"),
        ("salt_anchor_leaf", f"{salt_right}|{anchor}|{leaf}"),
        ("phase_salt_anchor_leaf", f"{phase}|{salt_right}|{anchor}|{leaf}"),
        ("phase_mod7_salt_anchor_leaf", f"{phase}|{mod7}|{salt_right}|{anchor}|{leaf}"),
    ]
    row["_feature_values"] = values
    return values


def has_key(row: Feature, key: FeatureKey) -> bool:
    return key in feature_values(row)


def selected_by_keyset(row: Feature, keyset: set[FeatureKey]) -> bool:
    return any(key in keyset for key in feature_values(row))


def row_status(row: Feature) -> dict[str, bool]:
    return {
        "below": bool(row["direct_below_rho_verified"]),
        "rank3": bool(row["direct_verified"] and int_value(row.get("rank")) >= 3),
        "verified": bool(row["direct_verified"]),
    }


def compact_row(row: Feature) -> dict[str, Any]:
    return {
        "base_selector": row["base_selector"],
        "block": row["block"],
        "case_entry": row["case_entry"],
        "direct_below_rho_verified": row["direct_below_rho_verified"],
        "direct_ops_over_rho": row["direct_ops_over_rho"],
        "direct_verified": row["direct_verified"],
        "leaf_signature": row["leaf_signature"],
        "policy_role": row["policy_role"],
        "rank": row["rank"],
        "right_anchor": row["right_anchor"],
        "row_pair": row["row_pair"],
        "salt_right": row["salt_right"],
        "selector": row["selector"],
        "transfer_index": row["transfer_index"],
        "transfer_mod12": row["transfer_mod12"],
        "transfer_mod7": row["transfer_mod7"],
    }


def dataset_summary(rows: list[Feature]) -> dict[str, Any]:
    positives = [row for row in rows if row["direct_below_rho_verified"]]
    verified = [row for row in rows if row["direct_verified"]]
    rank3 = [row for row in verified if int_value(row.get("rank")) >= 3]
    best_ops = sorted(float_value(row["direct_ops_over_rho"], 10**18) for row in positives)
    return {
        "below_rho_direct_verified_count": len(positives),
        "best_below_rho_ops_over_rho": best_ops[0] if best_ops else None,
        "case_count": len(rows),
        "direct_verified_count": len(verified),
        "positive_feature_counts": dict(Counter(key for row in positives for key in [feature_token(row)]).most_common(16)),
        "rank3_direct_verified_count": len(rank3),
        "transfer_counts": dict(sorted(Counter(str(row["transfer_index"]) for row in rows).items(), key=lambda item: int(item[0]))),
        "verified_rank_counts": dict(Counter(str(row["rank"]) for row in verified).most_common()),
    }


def feature_token(row: Feature) -> str:
    return (
        f"phase{row['transfer_mod12']}_mod7{row['transfer_mod7']}_"
        f"right{row['salt_right']}_anchor{row['right_anchor']}_{row['row_pair']}_{row['leaf_signature']}"
    )


def evaluate_rows(rows: list[Feature], selected: list[Feature]) -> dict[str, Any]:
    positives = [row for row in rows if row["direct_below_rho_verified"]]
    verified = [row for row in rows if row["direct_verified"]]
    rank3 = [row for row in verified if int_value(row.get("rank")) >= 3]
    selected_positive = [row for row in selected if row["direct_below_rho_verified"]]
    selected_verified = [row for row in selected if row["direct_verified"]]
    selected_rank3 = [row for row in selected_verified if int_value(row.get("rank")) >= 3]
    best_selected_ops = sorted(
        float_value(row["direct_ops_over_rho"], 10**18) for row in selected_positive
    )
    return {
        "below_rho_direct_verified_count": len(selected_positive),
        "below_rho_precision": ratio(len(selected_positive), len(selected)),
        "below_rho_recall": ratio(len(selected_positive), len(positives)),
        "best_selected_below_rho_ops_over_rho": best_selected_ops[0] if best_selected_ops else None,
        "direct_verified_count": len(selected_verified),
        "direct_verified_precision": ratio(len(selected_verified), len(selected)),
        "direct_verified_recall": ratio(len(selected_verified), len(verified)),
        "examples": [compact_row(row) for row in selected[:12]],
        "positive_examples": [compact_row(row) for row in selected_positive[:12]],
        "rank3_direct_verified_count": len(selected_rank3),
        "rank3_precision": ratio(len(selected_rank3), len(selected)),
        "rank3_recall": ratio(len(selected_rank3), len(rank3)),
        "raw_below_rho_direct_verified_count": len(positives),
        "raw_direct_verified_count": len(verified),
        "raw_rank3_direct_verified_count": len(rank3),
        "selected_count": len(selected),
        "selected_fraction": ratio(len(selected), len(rows)),
        "selected_transfer_counts": dict(
            sorted(Counter(str(row["transfer_index"]) for row in selected).items(), key=lambda item: int(item[0]))
        ),
    }


def feature_stats(rows: list[Feature], family: str, objective: str) -> list[dict[str, Any]]:
    buckets: dict[str, list[Feature]] = defaultdict(list)
    for row in rows:
        for row_family, value in feature_values(row):
            if row_family == family:
                buckets[value].append(row)
    stats = []
    for value, bucket in buckets.items():
        objective_count = sum(1 for row in bucket if row_status(row)[objective])
        if objective_count == 0:
            continue
        positive_blocks = sorted({row["block"] for row in bucket if row_status(row)[objective]})
        stats.append(
            {
                "below_count": sum(1 for row in bucket if row["direct_below_rho_verified"]),
                "direct_verified_count": sum(1 for row in bucket if row["direct_verified"]),
                "family": family,
                "key": value,
                "objective": objective,
                "objective_count": objective_count,
                "positive_block_count": len(positive_blocks),
                "positive_blocks": positive_blocks,
                "precision": ratio(objective_count, len(bucket)),
                "rank3_count": sum(1 for row in bucket if row["direct_verified"] and int_value(row.get("rank")) >= 3),
                "selected_count": len(bucket),
            }
        )
    stats.sort(
        key=lambda item: (
            item["objective_count"],
            item["positive_block_count"],
            float_value(item["precision"]),
            -item["selected_count"],
            item["key"],
        ),
        reverse=True,
    )
    return stats


def train_policy(
    rows: list[Feature],
    family: str,
    objective: str,
    top_n: int,
    ranked: list[dict[str, Any]] | None = None,
    include_training_report: bool = True,
) -> dict[str, Any]:
    ranked = ranked if ranked is not None else feature_stats(rows, family, objective)
    keys = [(family, item["key"]) for item in ranked[:top_n]]
    policy = {
        "config": {"family": family, "objective": objective, "top_n": top_n},
        "key_stats": ranked[:top_n],
        "keys": [{"family": family, "key": key} for _, key in keys],
    }
    if include_training_report:
        selected = [row for row in rows if selected_by_keyset(row, set(keys))]
        policy["training_report"] = evaluate_rows(rows, selected)
    return policy


def all_configs(rows: list[Feature]) -> list[Config]:
    families = sorted({family for row in rows for family, _ in feature_values(row)})
    return [(family, objective, top_n) for family in families for objective in OBJECTIVES for top_n in TOP_NS]


def evaluate_policy(policy: dict[str, Any], rows: list[Feature]) -> dict[str, Any]:
    keyset = {(item["family"], item["key"]) for item in policy["keys"]}
    selected = [row for row in rows if selected_by_keyset(row, keyset)]
    report = evaluate_rows(rows, selected)
    report["keys"] = policy["keys"]
    report["config"] = policy["config"]
    return report


def add_reports(left: dict[str, Any], report: dict[str, Any], block_name_value: str) -> None:
    for key in [
        "below_rho_direct_verified_count",
        "direct_verified_count",
        "rank3_direct_verified_count",
        "raw_below_rho_direct_verified_count",
        "raw_direct_verified_count",
        "raw_rank3_direct_verified_count",
        "selected_count",
    ]:
        left[key] += int_value(report.get(key))
    left["case_count"] += int_value(report.get("raw_case_count", 0))
    if report["selected_count"] and not report["raw_direct_verified_count"]:
        left["quiet_selected_block_count"] += 1
        left["quiet_selected_case_count"] += int_value(report["selected_count"])
    if report["raw_direct_verified_count"] and report["direct_verified_count"] == 0:
        left["missed_nonquiet_block_count"] += 1
    if report["direct_verified_count"]:
        left["hit_block_count"] += 1
    left["evaluated_blocks"].append(
        {
            "block": block_name_value,
            "below_rho_direct_verified_count": report["below_rho_direct_verified_count"],
            "direct_verified_count": report["direct_verified_count"],
            "rank3_direct_verified_count": report["rank3_direct_verified_count"],
            "raw_direct_verified_count": report["raw_direct_verified_count"],
            "selected_count": report["selected_count"],
        }
    )


def backtest(blocks: list[list[Feature]]) -> list[dict[str, Any]]:
    configs = all_configs([row for block in blocks[:MIN_BACKTEST_TRAIN_BLOCKS] for row in block])
    aggregates: dict[Config, dict[str, Any]] = {}
    for config in configs:
        aggregates[config] = {
            "below_rho_direct_verified_count": 0,
            "case_count": 0,
            "config": {"family": config[0], "objective": config[1], "top_n": config[2]},
            "direct_verified_count": 0,
            "evaluated_blocks": [],
            "hit_block_count": 0,
            "missed_nonquiet_block_count": 0,
            "quiet_selected_block_count": 0,
            "quiet_selected_case_count": 0,
            "rank3_direct_verified_count": 0,
            "raw_below_rho_direct_verified_count": 0,
            "raw_direct_verified_count": 0,
            "raw_rank3_direct_verified_count": 0,
            "selected_count": 0,
        }
    for index in range(MIN_BACKTEST_TRAIN_BLOCKS, len(blocks)):
        train_rows = [row for block in blocks[:index] for row in block]
        holdout_rows = blocks[index]
        holdout_block = holdout_rows[0]["block"] if holdout_rows else f"block_{index}"
        rankings = {
            (family, objective): feature_stats(train_rows, family, objective)
            for family in sorted({config[0] for config in configs})
            for objective in OBJECTIVES
        }
        for config in configs:
            policy = train_policy(
                train_rows,
                *config,
                ranked=rankings[(config[0], config[1])],
                include_training_report=False,
            )
            report = evaluate_policy(policy, holdout_rows)
            report["raw_case_count"] = len(holdout_rows)
            add_reports(aggregates[config], report, holdout_block)
    results = []
    for aggregate in aggregates.values():
        aggregate["below_rho_precision"] = ratio(aggregate["below_rho_direct_verified_count"], aggregate["selected_count"])
        aggregate["direct_verified_precision"] = ratio(aggregate["direct_verified_count"], aggregate["selected_count"])
        aggregate["rank3_precision"] = ratio(aggregate["rank3_direct_verified_count"], aggregate["selected_count"])
        aggregate["selected_fraction"] = ratio(aggregate["selected_count"], aggregate["case_count"])
        aggregate["direct_verified_recall"] = ratio(
            aggregate["direct_verified_count"], aggregate["raw_direct_verified_count"]
        )
        results.append(aggregate)
    results.sort(
        key=lambda item: (
            item["below_rho_direct_verified_count"],
            item["rank3_direct_verified_count"],
            item["direct_verified_count"],
            -item["missed_nonquiet_block_count"],
            -item["quiet_selected_case_count"],
            float_value(item["direct_verified_precision"]),
            -item["selected_count"],
        ),
        reverse=True,
    )
    return results


def nontrivial_backtest_configs(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    eligible = [
        item
        for item in results
        if float_value(item.get("selected_fraction"), 1.0) <= MAX_NONTRIVIAL_SELECTED_FRACTION
        and int_value(item.get("direct_verified_count")) > 0
    ]
    eligible.sort(
        key=lambda item: (
            int_value(item.get("missed_nonquiet_block_count")) == 0,
            int_value(item.get("hit_block_count")),
            float_value(item.get("direct_verified_precision")),
            int_value(item.get("below_rho_direct_verified_count")),
            int_value(item.get("rank3_direct_verified_count")),
            int_value(item.get("direct_verified_count")),
            -int_value(item.get("quiet_selected_case_count")),
            -int_value(item.get("selected_count")),
        ),
        reverse=True,
    )
    return eligible


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-sources", default=None, help="Comma-separated train source JSON paths.")
    parser.add_argument("--train-gates", default=None, help="Comma-separated train gate JSON paths.")
    parser.add_argument("--validation-source", type=Path, default=DEFAULT_VALIDATION_SOURCE)
    parser.add_argument("--validation-gate", type=Path, default=DEFAULT_VALIDATION_GATE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    train_sources = parse_path_list(args.train_sources) or [source for source, _ in TRAIN_PAIRS]
    train_gates = parse_path_list(args.train_gates) or [gate for _, gate in TRAIN_PAIRS]
    train_blocks = load_blocks(train_sources, train_gates)
    validation_rows = load_block(args.validation_source, args.validation_gate)
    train_rows = [row for block in train_blocks for row in block]
    backtest_results = backtest(train_blocks)
    nontrivial_results = nontrivial_backtest_configs(backtest_results)
    best = nontrivial_results[0] if nontrivial_results else backtest_results[0]
    best_config = best["config"]
    policy = train_policy(train_rows, best_config["family"], best_config["objective"], int(best_config["top_n"]))
    validation_report = evaluate_policy(policy, validation_rows)
    validation_summary = dataset_summary(validation_rows)
    if validation_summary["direct_verified_count"] == 0:
        claim_status = "NEGATIVE_RESULT_P586_VALIDATION_QUIET_BLOCK_NO_DIRECT_VERIFIED_ROWS"
    elif validation_report["direct_verified_count"] and float_value(validation_report["selected_fraction"], 1.0) <= MAX_NONTRIVIAL_SELECTED_FRACTION:
        claim_status = "P586_PUBLIC_BLOCK_YIELD_SELECTOR_VALIDATION_POSITIVE_NONTRIVIAL"
    elif validation_report["direct_verified_count"]:
        claim_status = "P586_PUBLIC_BLOCK_YIELD_SELECTOR_FULL_GRID_CONTROL_POSITIVE"
    else:
        claim_status = "NEGATIVE_RESULT_P586_SELECTOR_MISSED_NONQUIET_BLOCK"
    payload = {
        "artifacts": {
            "train_gates": [str(path) for path in train_gates],
            "train_sources": [str(path) for path in train_sources],
            "validation_gate": str(args.validation_gate),
            "validation_source": str(args.validation_source),
        },
        "backtest_top_configs": backtest_results[:12],
        "backtest_top_nontrivial_configs": nontrivial_results[:12],
        "claim_status": claim_status,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: order-9887 local verifier harness only.",
            "SOURCE-ONLY SELECTION: policies use public phase, mod7, salt, anchor, row-pair, leaf signature, selector, and policy-role metadata.",
            "LABEL BOUNDARY: direct verifier outcomes are joined only for training labels and validation scoring.",
            "MODEL-BOUND: block-yield prediction is a scheduler component, not target descent or a faster-than-rho ECDLP algorithm.",
        ],
        "method": "p586_block_yield_predictor",
        "schema": "ecdlp.low_term_total2_p586_block_yield_predictor.v1",
        "summary": {
            "best_backtest_config": best,
            "max_nontrivial_selected_fraction": MAX_NONTRIVIAL_SELECTED_FRACTION,
            "train_block_count": len(train_blocks),
            "train_dataset": dataset_summary(train_rows),
            "trained_policy": policy,
            "validation_dataset": validation_summary,
            "validation_report": validation_report,
        },
    }
    write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": claim_status}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
