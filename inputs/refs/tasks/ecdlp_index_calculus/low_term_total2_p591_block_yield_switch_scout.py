#!/usr/bin/env python3
"""P591 block-yield and source-family switch scout.

The scout trains on source-public family selectors from P586-P590 and may
recommend abstention after a quiet block. Direct verifier outcomes are labels
for training/evaluation only.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p570_pre_hit_source_feature_scout as p570


STATE_DIR = Path("ecdlp_index_calculus_state")
TRAIN_PAIRS = [
    (
        STATE_DIR / "low_term_total2_order9887_p586_block_yield_source_20833_20844_probe.json",
        STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p586_order9887_block_yield_20833_20844_density_gate_probe.json",
    ),
    (
        STATE_DIR / "low_term_total2_order9887_p587_p586_family_repair_source_20845_20856_probe.json",
        STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p587_order9887_p586_family_repair_20845_20856_density_gate_probe.json",
    ),
    (
        STATE_DIR / "low_term_total2_order9887_p588_right208_phase_drift_source_20857_20868_probe.json",
        STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p588_order9887_right208_phase_drift_20857_20868_density_gate_probe.json",
    ),
    (
        STATE_DIR / "low_term_total2_order9887_p589_phase3_right207_anchor6_source_20869_20880_probe.json",
        STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p589_order9887_phase3_right207_anchor6_20869_20880_density_gate_probe.json",
    ),
    (
        STATE_DIR / "low_term_total2_order9887_p590_phase9_right208_anchor7_source_20881_20892_probe.json",
        STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p590_order9887_phase9_right208_anchor7_20881_20892_density_gate_probe.json",
    ),
]
DEFAULT_VALIDATION_SOURCE = STATE_DIR / "low_term_total2_order9887_p591_block_yield_switch_source_20893_20904_probe.json"
DEFAULT_VALIDATION_GATE = (
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p591_order9887_block_yield_switch_20893_20904_density_gate_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_p591_block_yield_switch_scout_20893_20904_probe.json"

RIGHT208_ROW_PAIRS = {
    "salt203_salt208",
    "salt204_salt208",
    "salt205_salt208",
    "salt206_salt208",
}
SALT207_ROW_PAIRS = {
    "salt203_salt207",
    "salt204_salt207",
    "salt205_salt207",
    "salt206_salt207",
}
P586_PHASE7_ROW_PAIRS = {"salt203_salt207", "salt203_salt208"}
P586_PHASE7_ANCHORS = {3, 6, 7, 8, 9, 12, 13}


Feature = dict[str, Any]
Predicate = Callable[[Feature], bool]


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


def phase(row: Feature) -> int:
    return int_value(row.get("transfer_mod12"), -1)


def mod7(row: Feature) -> int:
    return int_value(row.get("transfer_mod7"), -1)


def p586_phase7_family(row: Feature) -> bool:
    return (
        phase(row) == 7
        and row.get("row_pair") in P586_PHASE7_ROW_PAIRS
        and row.get("right_anchor") in P586_PHASE7_ANCHORS
    )


def p586_phase2_right207_anchor9(row: Feature) -> bool:
    return phase(row) == 2 and row.get("row_pair") == "salt205_salt207" and row.get("right_anchor") == 9


def p587_phase6_right208_anchor9(row: Feature) -> bool:
    return phase(row) == 6 and row.get("row_pair") == "salt204_salt208" and row.get("right_anchor") == 9


def p587_phase9_right208_anchor13(row: Feature) -> bool:
    return phase(row) == 9 and row.get("row_pair") in RIGHT208_ROW_PAIRS and row.get("right_anchor") == 13


def p588_phase3_right207_anchor6(row: Feature) -> bool:
    return phase(row) == 3 and row.get("row_pair") in SALT207_ROW_PAIRS and row.get("right_anchor") == 6


def p589_phase9_right208_anchor7(row: Feature) -> bool:
    return phase(row) == 9 and row.get("row_pair") in RIGHT208_ROW_PAIRS and row.get("right_anchor") == 7


def p589_phase9_right207_anchor9_salt206(row: Feature) -> bool:
    return phase(row) == 9 and row.get("row_pair") == "salt206_salt207" and row.get("right_anchor") == 9


def p589_phase9_union(row: Feature) -> bool:
    return p589_phase9_right208_anchor7(row) or p589_phase9_right207_anchor9_salt206(row)


def right208_anchor7_all_phases(row: Feature) -> bool:
    return row.get("row_pair") in RIGHT208_ROW_PAIRS and row.get("right_anchor") == 7


def broad_salt206_replay(row: Feature) -> bool:
    return row.get("row_pair") in {"salt206_salt207", "salt206_salt208"}


def phase9_right208_anchor_band(row: Feature) -> bool:
    return phase(row) == 9 and row.get("row_pair") in RIGHT208_ROW_PAIRS and row.get("right_anchor") in {7, 9, 13}


def phase3_right207_anchor_band(row: Feature) -> bool:
    return phase(row) == 3 and row.get("row_pair") in SALT207_ROW_PAIRS and row.get("right_anchor") in {3, 6, 9, 13}


def selector_specs() -> list[tuple[str, str, Predicate]]:
    return [
        ("p586_phase7_family", "P586 phase7 salt203 right207/right208 anchor-band family", p586_phase7_family),
        ("p586_phase2_right207_anchor9", "P586 phase2 right207/anchor9/salt205_salt207 pocket", p586_phase2_right207_anchor9),
        ("p587_phase6_right208_anchor9", "P587 phase6 right208/anchor9/salt204_salt208 pocket", p587_phase6_right208_anchor9),
        ("p587_phase9_right208_anchor13", "P587 phase9 right208/anchor13 family", p587_phase9_right208_anchor13),
        ("p588_phase3_right207_anchor6", "P588 phase3 right207/anchor6 family", p588_phase3_right207_anchor6),
        ("p589_phase9_right208_anchor7", "P589 phase9 right208/anchor7 family", p589_phase9_right208_anchor7),
        (
            "p589_phase9_right207_anchor9_salt206",
            "P589 companion phase9 right207/anchor9/salt206_salt207 pocket",
            p589_phase9_right207_anchor9_salt206,
        ),
        ("p589_phase9_union", "Union of P589 phase9 right208/anchor7 and right207/anchor9 pockets", p589_phase9_union),
        ("right208_anchor7_all_phases", "right208/anchor7 across all phases", right208_anchor7_all_phases),
        ("phase9_right208_anchor_band", "phase9/right208 anchor band {7,9,13}", phase9_right208_anchor_band),
        ("phase3_right207_anchor_band", "phase3/right207 anchor band {3,6,9,13}", phase3_right207_anchor_band),
        ("broad_salt206_replay", "Broad salt206 row-pair replay control", broad_salt206_replay),
    ]


def feature_key(row: Feature) -> str:
    return (
        f"phase{row.get('transfer_mod12')}_mod7{row.get('transfer_mod7')}_"
        f"right{row.get('salt_right')}_anchor{row.get('right_anchor')}_{row.get('row_pair')}"
    )


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
    return {
        "case_count": len(rows),
        "direct_below_rho_verified_count": len(positives),
        "direct_verified_count": len(verified),
        "positive_feature_counts": dict(Counter(feature_key(row) for row in positives).most_common(16)),
        "positive_transfer_counts": dict(
            sorted(Counter(str(row["transfer_index"]) for row in positives).items(), key=lambda item: int(item[0]))
        ),
        "rank3_direct_verified_count": len(rank3),
        "verified_feature_counts": dict(Counter(feature_key(row) for row in verified).most_common(16)),
        "verified_rank_counts": dict(Counter(str(row["rank"]) for row in verified).most_common()),
        "verified_transfer_counts": dict(
            sorted(Counter(str(row["transfer_index"]) for row in verified).items(), key=lambda item: int(item[0]))
        ),
    }


def selector_report(rows: list[Feature], selected: list[Feature], name: str, description: str) -> dict[str, Any]:
    positives = [row for row in rows if row["direct_below_rho_verified"]]
    verified = [row for row in rows if row["direct_verified"]]
    rank3 = [row for row in verified if int_value(row.get("rank")) >= 3]
    selected_positive = [row for row in selected if row["direct_below_rho_verified"]]
    selected_verified = [row for row in selected if row["direct_verified"]]
    selected_rank3 = [row for row in selected_verified if int_value(row.get("rank")) >= 3]
    return {
        "description": description,
        "direct_below_rho_verified_count": len(selected_positive),
        "direct_below_rho_verified_precision": ratio(len(selected_positive), len(selected)),
        "direct_below_rho_verified_recall": ratio(len(selected_positive), len(positives)),
        "direct_verified_count": len(selected_verified),
        "direct_verified_precision": ratio(len(selected_verified), len(selected)),
        "direct_verified_recall": ratio(len(selected_verified), len(verified)),
        "examples": [compact_row(row) for row in selected[:12]],
        "positive_examples": [compact_row(row) for row in selected_positive[:12]],
        "rank3_direct_verified_count": len(selected_rank3),
        "rank3_recall": ratio(len(selected_rank3), len(rank3)),
        "raw_below_rho_count": len(positives),
        "raw_direct_verified_count": len(verified),
        "raw_rank3_count": len(rank3),
        "rule": name,
        "selected_case_entries": [row["case_entry"] for row in selected],
        "selected_count": len(selected),
        "selected_direct_verified_case_entries": [row["case_entry"] for row in selected_verified],
        "selected_fraction": ratio(len(selected), len(rows)),
        "selected_positive_case_entries": [row["case_entry"] for row in selected_positive],
        "transfer_counts": dict(
            sorted(Counter(str(row["transfer_index"]) for row in selected).items(), key=lambda item: int(item[0]))
        ),
    }


def selector_training_report(blocks: list[list[Feature]], name: str, description: str, predicate: Predicate) -> dict[str, Any]:
    all_rows = [row for block in blocks for row in block]
    selected_all = [row for row in all_rows if predicate(row)]
    base = selector_report(all_rows, selected_all, name, description)
    block_reports = []
    hit_blocks = 0
    quiet_selected_blocks = 0
    missed_nonquiet_blocks = 0
    recent_hit_blocks = 0
    for index, block in enumerate(blocks):
        selected = [row for row in block if predicate(row)]
        report = selector_report(block, selected, name, description)
        report["block"] = block[0]["block"] if block else f"block_{index}"
        block_reports.append(report)
        raw_verified = report["raw_direct_verified_count"]
        selected_verified = report["direct_verified_count"]
        if selected_verified:
            hit_blocks += 1
            if index >= len(blocks) - 3:
                recent_hit_blocks += 1
        if selected and raw_verified == 0:
            quiet_selected_blocks += 1
        if raw_verified and selected_verified == 0:
            missed_nonquiet_blocks += 1
    base.update(
        {
            "block_reports": block_reports,
            "hit_block_count": hit_blocks,
            "missed_nonquiet_block_count": missed_nonquiet_blocks,
            "quiet_selected_block_count": quiet_selected_blocks,
            "recent_hit_block_count": recent_hit_blocks,
        }
    )
    return base


def choose_recommendation(training_reports: list[dict[str, Any]], block_summaries: list[dict[str, Any]]) -> dict[str, Any]:
    latest_quiet = bool(block_summaries and block_summaries[-1]["direct_verified_count"] == 0)
    nonquiet_blocks = sum(1 for item in block_summaries if item["direct_verified_count"])
    eligible = [
        report
        for report in training_reports
        if report["direct_verified_count"]
        and (report["selected_fraction"] is None or report["selected_fraction"] <= 0.25)
    ]
    eligible.sort(
        key=lambda item: (
            item["recent_hit_block_count"],
            item["hit_block_count"],
            -item["missed_nonquiet_block_count"],
            -item["quiet_selected_block_count"],
            item["direct_verified_precision"] or 0.0,
            item["direct_below_rho_verified_count"],
            item["direct_verified_count"],
            -item["selected_count"],
        ),
        reverse=True,
    )
    best = eligible[0] if eligible else None
    reason = []
    action = "test_best_selector"
    selected_rule = best["rule"] if best else None
    if latest_quiet:
        reason.append("latest_training_block_quiet")
    if best is None:
        action = "abstain_or_source_generation_change"
        reason.append("no_nontrivial_selector_with_training_hits")
    elif latest_quiet and (best["recent_hit_block_count"] == 0 or best["hit_block_count"] < 2):
        action = "abstain_or_source_generation_change"
        reason.append("best_selector_not_recently_recurrent_after_quiet_block")
    elif nonquiet_blocks and best["missed_nonquiet_block_count"] >= nonquiet_blocks:
        action = "abstain_or_source_generation_change"
        reason.append("best_selector_missed_all_nonquiet_training_blocks")
    else:
        reason.append("best_selector_has_training_support")
    return {
        "action": action,
        "best_selector": selected_rule,
        "best_selector_training_report": best,
        "reason": reason,
    }


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
    if len(train_sources) != len(train_gates):
        raise ValueError(f"source/gate count mismatch: {len(train_sources)} sources, {len(train_gates)} gates")
    train_blocks = [load_block(source, gate) for source, gate in zip(train_sources, train_gates)]
    validation_rows = load_block(args.validation_source, args.validation_gate)
    block_summaries = [
        {"block": block[0]["block"] if block else f"block_{index}", **dataset_summary(block)}
        for index, block in enumerate(train_blocks)
    ]
    training_reports = [
        selector_training_report(train_blocks, name, description, predicate)
        for name, description, predicate in selector_specs()
    ]
    training_reports.sort(
        key=lambda item: (
            item["recent_hit_block_count"],
            item["hit_block_count"],
            item["direct_verified_count"],
            item["direct_below_rho_verified_count"],
            -(item["selected_count"]),
        ),
        reverse=True,
    )
    recommendation = choose_recommendation(training_reports, block_summaries)
    validation_reports = [
        selector_report(validation_rows, [row for row in validation_rows if predicate(row)], name, description)
        for name, description, predicate in selector_specs()
    ]
    validation_reports.sort(
        key=lambda item: (
            item["direct_below_rho_verified_count"],
            item["rank3_direct_verified_count"],
            item["direct_verified_count"],
            item["direct_verified_precision"] or 0.0,
            -item["selected_count"],
        ),
        reverse=True,
    )
    validation_summary = dataset_summary(validation_rows)
    selected_validation_report = next(
        (item for item in validation_reports if item["rule"] == recommendation.get("best_selector")),
        validation_reports[0] if validation_reports else None,
    )
    if recommendation["action"] == "abstain_or_source_generation_change" and validation_summary["direct_verified_count"] == 0:
        claim_status = "P591_ABSTENTION_VALIDATION_POSITIVE_QUIET_BLOCK"
    elif recommendation["action"] == "abstain_or_source_generation_change":
        claim_status = "NEGATIVE_RESULT_P591_ABSTENTION_MISSED_NONQUIET_BLOCK"
    elif selected_validation_report and selected_validation_report["direct_verified_count"]:
        claim_status = "P591_SOURCE_FAMILY_SWITCH_SELECTOR_VALIDATION_POSITIVE"
    elif validation_summary["direct_verified_count"] == 0:
        claim_status = "NEGATIVE_RESULT_P591_VALIDATION_QUIET_BLOCK_NO_DIRECT_VERIFIED_ROWS"
    else:
        claim_status = "NEGATIVE_RESULT_P591_SELECTOR_MISSED_NONQUIET_BLOCK"
    payload = {
        "artifacts": {
            "train_gates": [str(path) for path in train_gates],
            "train_sources": [str(path) for path in train_sources],
            "validation_gate": str(args.validation_gate),
            "validation_source": str(args.validation_source),
        },
        "claim_status": claim_status,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: order-9887 local verifier harness only.",
            "SOURCE-ONLY SELECTION: selectors use public phase, mod7, salt, anchor, row-pair, leaf signature, selector, and policy-role metadata.",
            "LABEL BOUNDARY: direct verifier outcomes are joined only for training labels and validation scoring.",
            "MODEL-BOUND: block-yield switching is a scheduler component, not target descent or a faster-than-rho ECDLP algorithm.",
        ],
        "method": "p591_block_yield_switch_scout",
        "schema": "ecdlp.low_term_total2_p591_block_yield_switch_scout.v1",
        "summary": {
            "block_summaries": block_summaries,
            "recommendation": recommendation,
            "top_training_reports": training_reports[:12],
            "validation_dataset": validation_summary,
            "validation_reports": validation_reports,
            "recommended_validation_report": selected_validation_report,
        },
    }
    write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": claim_status}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
