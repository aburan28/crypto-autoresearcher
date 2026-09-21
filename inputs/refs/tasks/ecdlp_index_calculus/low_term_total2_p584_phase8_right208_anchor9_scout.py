#!/usr/bin/env python3
"""P584 phase8/right208/anchor9 family validation scout.

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
DEFAULT_TRAIN_SOURCE = STATE_DIR / "low_term_total2_order9887_p583_salt205_rank_split_source_20797_20808_probe.json"
DEFAULT_TRAIN_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p583_order9887_salt205_rank_split_20797_20808_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p584_phase8_right208_anchor9_source_20809_20820_probe.json"
DEFAULT_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p584_order9887_phase8_right208_anchor9_20809_20820_density_gate_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_p584_phase8_right208_anchor9_scout_20809_20820_probe.json"

RIGHT208_ROW_PAIRS = {
    "salt203_salt208",
    "salt204_salt208",
    "salt205_salt208",
    "salt206_salt208",
}


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


def mod7(row: Feature) -> int:
    return int(row.get("transfer_mod7") or -1)


def p583_phase8_right208_anchor9_all_rowpairs(row: Feature) -> bool:
    return (
        phase(row) == 8
        and row.get("salt_right") == 208
        and row.get("right_anchor") == 9
        and row.get("row_pair") in RIGHT208_ROW_PAIRS
    )


def p583_phase8_right208_anchor9_exact_mod7_control(row: Feature) -> bool:
    return p583_phase8_right208_anchor9_all_rowpairs(row) and mod7(row) == 0


def p583_phase8_right208_anchor9_salt205_control(row: Feature) -> bool:
    return (
        phase(row) == 8
        and row.get("salt_right") == 208
        and row.get("right_anchor") == 9
        and row.get("row_pair") == "salt205_salt208"
    )


def p583_phase8_anchor9_all_right_salts(row: Feature) -> bool:
    return phase(row) == 8 and row.get("right_anchor") == 9


def p583_right208_anchor9_all_phases(row: Feature) -> bool:
    return row.get("salt_right") == 208 and row.get("right_anchor") == 9 and row.get("row_pair") in RIGHT208_ROW_PAIRS


def p583_right208_anchor9_salt205_all_phases(row: Feature) -> bool:
    return row.get("salt_right") == 208 and row.get("right_anchor") == 9 and row.get("row_pair") == "salt205_salt208"


def p582_salt205_anchor9_split_no_mod7(row: Feature) -> bool:
    return (
        phase(row) == 5
        and row.get("salt_right") == 208
        and row.get("right_anchor") == 9
        and row.get("row_pair") == "salt205_salt208"
    ) or (
        phase(row) == 10
        and row.get("salt_right") == 207
        and row.get("right_anchor") == 9
        and row.get("row_pair") == "salt205_salt207"
    )


def p581_failed_below_replay_control(row: Feature) -> bool:
    return (
        phase(row) == 3
        and row.get("salt_right") == 208
        and row.get("right_anchor") == 9
        and row.get("row_pair") == "salt206_salt208"
    )


def rule_specs() -> list[tuple[str, str, Predicate]]:
    return [
        (
            "p583_phase8_right208_anchor9_all_rowpairs",
            "P583 raw-positive family: phase8/right208/anchor9 across all right208 row pairs",
            p583_phase8_right208_anchor9_all_rowpairs,
        ),
        (
            "p583_phase8_right208_anchor9_exact_mod7_control",
            "P583 exact one-window family including mod7=0",
            p583_phase8_right208_anchor9_exact_mod7_control,
        ),
        (
            "p583_phase8_right208_anchor9_salt205_control",
            "P583 salt205 subset of phase8/right208/anchor9",
            p583_phase8_right208_anchor9_salt205_control,
        ),
        (
            "p583_phase8_anchor9_all_right_salts",
            "phase8/anchor9 across right salts and row pairs",
            p583_phase8_anchor9_all_right_salts,
        ),
        (
            "p583_right208_anchor9_all_phases",
            "right208/anchor9 all right208 row pairs across all phases",
            p583_right208_anchor9_all_phases,
        ),
        (
            "p583_right208_anchor9_salt205_all_phases",
            "right208/anchor9/salt205+salt208 across all phases",
            p583_right208_anchor9_salt205_all_phases,
        ),
        (
            "p582_salt205_anchor9_split_no_mod7",
            "P582 salt205 phase split replayed as a negative-control branch",
            p582_salt205_anchor9_split_no_mod7,
        ),
        (
            "p581_failed_below_replay_control",
            "P581 failed below-rho pocket replayed as a negative control",
            p581_failed_below_replay_control,
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
        "phase8_right208_anchor9_training": cohort_summary(
            [row for row in train_rows if p583_phase8_right208_anchor9_all_rowpairs(row)],
            "phase8_right208_anchor9_training",
        ),
        "salt205_subset_training": cohort_summary(
            [row for row in train_rows if p583_phase8_right208_anchor9_salt205_control(row)],
            "salt205_subset_training",
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
            int(item["direct_verified_rank4_count"]),
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
            "HEURISTIC: phase8/right208/anchor9 persistence is an empirical relation-supply hypothesis, not an algebraic theorem.",
            "NO SPEEDUP CLAIM: public product-gate selection, sparse linear algebra, and target descent remain separate gates.",
        ],
        "method": "p584_phase8_right208_anchor9_scout",
        "rule_reports": reports,
        "schema": "ecdlp.low_term_total2_p584_phase8_right208_anchor9_scout.v1",
        "summary": {
            "best_below_rho_rule": best_below,
            "best_direct_verified_rule": best_verified,
            "claim_status": (
                "P584_PHASE8_RIGHT208_ANCHOR9_MAIN_RULE_VALIDATION_POSITIVE"
                if main_report["direct_below_rho_verified_count"]
                else "P584_PHASE8_RIGHT208_ANCHOR9_CONTROL_RULE_VALIDATION_POSITIVE"
                if best_below["direct_below_rho_verified_count"]
                else "P584_DIRECT_VERIFIED_DIAGNOSTIC"
                if best_verified["direct_verified_count"]
                else "NEGATIVE_RESULT_P584_NO_VALIDATION_SIGNAL"
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
