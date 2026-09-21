#!/usr/bin/env python3
"""P585 phase11/right207 rank-growth validation scout.

Rules use source-public metadata only. Direct verifier outcomes are joined only
as labels after selection.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p570_pre_hit_source_feature_scout as p570


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_TRAIN_SOURCE = STATE_DIR / "low_term_total2_order9887_p584_phase8_right208_anchor9_source_20809_20820_probe.json"
DEFAULT_TRAIN_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p584_order9887_phase8_right208_anchor9_20809_20820_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p585_phase11_right207_rank_growth_source_20821_20832_probe.json"
DEFAULT_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p585_order9887_phase11_right207_rank_growth_20821_20832_density_gate_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_p585_phase11_right207_rank_growth_scout_20821_20832_probe.json"

RIGHT207_ROW_PAIRS = {
    "salt203_salt207",
    "salt204_salt207",
    "salt205_salt207",
    "salt206_salt207",
}
RIGHT208_ROW_PAIRS = {
    "salt203_salt208",
    "salt204_salt208",
    "salt205_salt208",
    "salt206_salt208",
}
PHASE11_RIGHT207_ANCHORS = {3, 6, 7, 8, 9, 11, 12, 13}
PHASE11_P584_BELOW_ANCHORS = {6, 7, 9, 11, 12, 13}


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


def phase(row: Feature) -> int:
    return int(row.get("transfer_mod12") or -1)


def phase11_right207_anchor_band(row: Feature) -> bool:
    return (
        phase(row) == 11
        and row.get("salt_right") == 207
        and row.get("right_anchor") in PHASE11_RIGHT207_ANCHORS
        and row.get("row_pair") in RIGHT207_ROW_PAIRS
    )


def phase11_right207_p584_below_rows(row: Feature) -> bool:
    return (
        phase(row) == 11
        and row.get("salt_right") == 207
        and row.get("right_anchor") in PHASE11_P584_BELOW_ANCHORS
        and row.get("row_pair") in {"salt205_salt207", "salt206_salt207"}
    )


def phase11_right207_rank_anchor8_salt203(row: Feature) -> bool:
    return (
        phase(row) == 11
        and row.get("salt_right") == 207
        and row.get("right_anchor") == 8
        and row.get("row_pair") == "salt203_salt207"
    )


def phase11_right207_verified_training_rows(row: Feature) -> bool:
    return (
        phase(row) == 11
        and row.get("salt_right") == 207
        and row.get("right_anchor") in {3, 6, 7, 8, 9, 11, 13}
        and row.get("row_pair") in {"salt203_salt207", "salt205_salt207"}
    )


def phase7_right206_anchor13_salt204_control(row: Feature) -> bool:
    return (
        phase(row) == 7
        and row.get("salt_right") == 206
        and row.get("right_anchor") == 13
        and row.get("row_pair") == "salt204_salt206"
    )


def phase4_right208_anchor9_salt205_control(row: Feature) -> bool:
    return (
        phase(row) == 4
        and row.get("salt_right") == 208
        and row.get("right_anchor") == 9
        and row.get("row_pair") == "salt205_salt208"
    )


def right207_anchor_band_all_phases(row: Feature) -> bool:
    return (
        row.get("salt_right") == 207
        and row.get("right_anchor") in PHASE11_RIGHT207_ANCHORS
        and row.get("row_pair") in RIGHT207_ROW_PAIRS
    )


def right207_anchor8_salt203_all_phases(row: Feature) -> bool:
    return (
        row.get("salt_right") == 207
        and row.get("right_anchor") == 8
        and row.get("row_pair") == "salt203_salt207"
    )


def rule_specs() -> list[tuple[str, str, Predicate]]:
    return [
        (
            "p585_phase11_right207_anchor_band",
            "P584 drift family: phase11/right207 over anchors 3,6,7,8,9,11,12,13 and all right207 row pairs",
            phase11_right207_anchor_band,
        ),
        (
            "p585_phase11_right207_p584_below_rows",
            "P584 below-rho phase11/right207 subset: salt205/salt206 plus anchors 6,7,9,11,12,13",
            phase11_right207_p584_below_rows,
        ),
        (
            "p585_phase11_right207_rank_anchor8_salt203",
            "P584 rank-gain replay: phase11/right207/anchor8/salt203+salt207",
            phase11_right207_rank_anchor8_salt203,
        ),
        (
            "p585_phase11_right207_verified_training_rows",
            "P584 verified phase11/right207 rows: salt203/salt205 plus anchors 3,6,7,8,9,11,13",
            phase11_right207_verified_training_rows,
        ),
        (
            "p585_phase7_right206_anchor13_salt204_control",
            "P584 below-rho and rank-gain control: phase7/right206/anchor13/salt204+salt206",
            phase7_right206_anchor13_salt204_control,
        ),
        (
            "p585_phase4_right208_anchor9_salt205_control",
            "P584 below-rho control: phase4/right208/anchor9/salt205+salt208",
            phase4_right208_anchor9_salt205_control,
        ),
        (
            "p585_right207_anchor_band_all_phases",
            "Broad right207 anchor-band control across all phases",
            right207_anchor_band_all_phases,
        ),
        (
            "p585_right207_anchor8_salt203_all_phases",
            "Broad right207/anchor8/salt203+salt207 rank-gain control across all phases",
            right207_anchor8_salt203_all_phases,
        ),
    ]


def compact_row(row: Feature) -> dict[str, Any]:
    return {
        "base_selector": row["base_selector"],
        "case_entry": row["case_entry"],
        "direct_below_rho_verified": row["direct_below_rho_verified"],
        "direct_ops_over_rho": row["direct_ops_over_rho"],
        "direct_verified": row["direct_verified"],
        "leaf_signature": row["leaf_signature"],
        "policy_role": row["policy_role"],
        "rank": row["rank"],
        "right_anchor": row["right_anchor"],
        "row_pair": row["row_pair"],
        "salt_left": row["salt_left"],
        "salt_right": row["salt_right"],
        "selector": row["selector"],
        "top_k": row["top_k"],
        "transfer_index": row["transfer_index"],
        "transfer_mod12": row["transfer_mod12"],
        "transfer_mod7": row["transfer_mod7"],
    }


def feature_key(row: Feature) -> str:
    return (
        f"phase{row.get('transfer_mod12')}_mod7{row.get('transfer_mod7')}_"
        f"right{row.get('salt_right')}_anchor{row.get('right_anchor')}_{row.get('row_pair')}"
    )


def cohort_summary(rows: list[Feature], name: str) -> dict[str, Any]:
    return {
        "cohort": name,
        "count": len(rows),
        "direct_below_rho_verified_count": sum(1 for row in rows if row["direct_below_rho_verified"]),
        "direct_verified_count": sum(1 for row in rows if row["direct_verified"]),
        "examples": [compact_row(row) for row in rows[:12]],
        "feature_counts": dict(Counter(feature_key(row) for row in rows).most_common(16)),
        "leaf_signature_counts": dict(Counter(str(row["leaf_signature"]) for row in rows).most_common(16)),
        "rank_counts": dict(Counter(str(row["rank"]) for row in rows).most_common()),
        "selector_base_counts": dict(Counter(str(row["base_selector"]) for row in rows).most_common()),
        "transfer_counts": dict(
            sorted(Counter(str(row["transfer_index"]) for row in rows).items(), key=lambda item: int(item[0]))
        ),
    }


def report(rows: list[Feature], selected: list[Feature], name: str, description: str) -> dict[str, Any]:
    positives = [row for row in rows if row["direct_below_rho_verified"]]
    verified = [row for row in rows if row["direct_verified"]]
    selected_positive = [row for row in selected if row["direct_below_rho_verified"]]
    selected_verified = [row for row in selected if row["direct_verified"]]
    selected_rank3 = [row for row in selected_verified if int(row.get("rank") or 0) >= 3]
    selected_rank4 = [row for row in selected_verified if int(row.get("rank") or 0) >= 4]
    return {
        "description": description,
        "direct_below_rho_verified_count": len(selected_positive),
        "direct_below_rho_verified_precision": ratio(len(selected_positive), len(selected)),
        "direct_below_rho_verified_recall": ratio(len(selected_positive), len(positives)),
        "direct_verified_count": len(selected_verified),
        "direct_verified_precision": ratio(len(selected_verified), len(selected)),
        "direct_verified_rank3_count": len(selected_rank3),
        "direct_verified_rank4_count": len(selected_rank4),
        "direct_verified_recall": ratio(len(selected_verified), len(verified)),
        "examples": [compact_row(row) for row in selected[:12]],
        "positive_examples": [compact_row(row) for row in selected_positive[:12]],
        "rank3_examples": [compact_row(row) for row in selected_rank3[:12]],
        "rank4_examples": [compact_row(row) for row in selected_rank4[:12]],
        "raw_positive_count": len(positives),
        "raw_verified_count": len(verified),
        "right_anchor_counts": dict(Counter(str(row["right_anchor"]) for row in selected).most_common()),
        "row_pair_counts": dict(Counter(str(row["row_pair"]) for row in selected).most_common(16)),
        "rule": name,
        "salt_right_counts": dict(Counter(str(row["salt_right"]) for row in selected).most_common()),
        "selected_case_entries": [row["case_entry"] for row in selected],
        "selected_count": len(selected),
        "selected_direct_below_rho_verified_case_entries": [row["case_entry"] for row in selected_positive],
        "selected_direct_verified_case_entries": [row["case_entry"] for row in selected_verified],
        "selected_fraction": ratio(len(selected), len(rows)),
        "transfer_counts": dict(
            sorted(Counter(str(row["transfer_index"]) for row in selected).items(), key=lambda item: int(item[0]))
        ),
    }


def dataset_summary(rows: list[Feature]) -> dict[str, Any]:
    positives = [row for row in rows if row["direct_below_rho_verified"]]
    verified = [row for row in rows if row["direct_verified"]]
    return {
        "case_count": len(rows),
        "direct_below_rho_verified_count": len(positives),
        "direct_verified_count": len(verified),
        "positive_feature_counts": dict(Counter(feature_key(row) for row in positives).most_common()),
        "positive_transfer_counts": dict(
            sorted(Counter(str(row["transfer_index"]) for row in positives).items(), key=lambda item: int(item[0]))
        ),
        "verified_feature_counts": dict(Counter(feature_key(row) for row in verified).most_common(16)),
        "verified_rank_counts": dict(Counter(str(row["rank"]) for row in verified).most_common()),
        "verified_transfer_counts": dict(
            sorted(Counter(str(row["transfer_index"]) for row in verified).items(), key=lambda item: int(item[0]))
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-source", type=Path, default=DEFAULT_TRAIN_SOURCE)
    parser.add_argument("--train-gate", type=Path, default=DEFAULT_TRAIN_GATE)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--gate", type=Path, default=DEFAULT_GATE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    train_rows = p570.source_rows([args.train_source], p570.gate_labels([args.train_gate]), "training")
    validation_rows = p570.source_rows([args.source], p570.gate_labels([args.gate]), "validation")
    train_summary = {
        "below_rho_direct_verified": cohort_summary(
            [row for row in train_rows if row["direct_below_rho_verified"]],
            "below_rho_direct_verified",
        ),
        "phase11_right207_anchor_band_training": cohort_summary(
            [row for row in train_rows if phase11_right207_anchor_band(row)],
            "phase11_right207_anchor_band_training",
        ),
        "phase11_right207_rank_anchor8_training": cohort_summary(
            [row for row in train_rows if phase11_right207_rank_anchor8_salt203(row)],
            "phase11_right207_rank_anchor8_training",
        ),
        "phase7_right206_anchor13_training": cohort_summary(
            [row for row in train_rows if phase7_right206_anchor13_salt204_control(row)],
            "phase7_right206_anchor13_training",
        ),
        "phase4_right208_anchor9_training": cohort_summary(
            [row for row in train_rows if phase4_right208_anchor9_salt205_control(row)],
            "phase4_right208_anchor9_training",
        ),
    }
    reports = [
        report(validation_rows, [row for row in validation_rows if predicate(row)], name, description)
        for name, description, predicate in rule_specs()
    ]
    main_report = reports[0]
    best_below = max(
        reports,
        key=lambda item: (
            int(item["direct_below_rho_verified_count"]),
            float(item["direct_below_rho_verified_precision"] or 0.0),
            int(item["selected_count"] > 0),
            -int(item["selected_count"]),
        ),
    )
    best_verified = max(
        reports,
        key=lambda item: (
            int(item["direct_verified_count"]),
            int(item["direct_verified_rank3_count"]),
            float(item["direct_verified_precision"] or 0.0),
            -int(item["selected_count"]),
        ),
    )
    payload = {
        "artifacts": {
            "gate": str(args.gate),
            "source": str(args.source),
            "train_gate": str(args.train_gate),
            "train_source": str(args.train_source),
        },
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: order-9887 local verifier harness only.",
            "SOURCE-ONLY SELECTION: validation rules use public phase, salt, anchor, row-pair, leaf signature, and selector metadata only.",
            "LABEL BOUNDARY: direct verifier outcomes are joined only for evaluation.",
            "HEURISTIC: phase11/right207 persistence is an empirical relation-supply hypothesis, not an algebraic theorem.",
            "NO SPEEDUP CLAIM: sparse linear algebra, target descent, and source-generation cost remain separate gates.",
        ],
        "method": "p585_phase11_right207_rank_growth_scout",
        "rule_reports": reports,
        "schema": "ecdlp.low_term_total2_p585_phase11_right207_rank_growth_scout.v1",
        "summary": {
            "best_below_rho_rule": best_below,
            "best_direct_verified_rule": best_verified,
            "claim_status": (
                "P585_PHASE11_RIGHT207_MAIN_RULE_VALIDATION_POSITIVE"
                if main_report["direct_below_rho_verified_count"] or main_report["direct_verified_rank3_count"]
                else "P585_PHASE11_RIGHT207_CONTROL_RULE_VALIDATION_POSITIVE"
                if best_below["direct_below_rho_verified_count"] or best_verified["direct_verified_rank3_count"]
                else "P585_DIRECT_VERIFIED_DIAGNOSTIC"
                if best_verified["direct_verified_count"]
                else "NEGATIVE_RESULT_P585_NO_VALIDATION_SIGNAL"
            ),
            "main_rule": main_report,
            "training_cohorts": train_summary,
            "validation_dataset": dataset_summary(validation_rows),
        },
    }
    write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
