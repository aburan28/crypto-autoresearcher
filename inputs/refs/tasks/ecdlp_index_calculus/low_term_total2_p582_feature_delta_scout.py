#!/usr/bin/env python3
"""Feature-delta scout for P581 below-rho versus rank-3 direct material.

This script compares P581 training cohorts, then tests source-public rules on
the next validation block. Verifier labels are used only for evaluation.
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
DEFAULT_TRAIN_SOURCE = STATE_DIR / "low_term_total2_order9887_p581_drift_anchor9_source_20773_20784_probe.json"
DEFAULT_TRAIN_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p581_order9887_drift_anchor9_20773_20784_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p582_feature_delta_source_20785_20796_probe.json"
DEFAULT_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p582_order9887_feature_delta_20785_20796_density_gate_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_p582_feature_delta_scout_20785_20796_probe.json"


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


def p581_below_shape_no_mod7(row: Feature) -> bool:
    return (
        phase(row) == 3
        and row.get("salt_right") == 208
        and row.get("right_anchor") == 9
        and row.get("row_pair") == "salt206_salt208"
    )


def p581_below_exact_mod7_control(row: Feature) -> bool:
    return p581_below_shape_no_mod7(row) and mod7(row) == 6


def p581_anchor9_salt206_salt208_all_phases(row: Feature) -> bool:
    return (
        row.get("salt_right") == 208
        and row.get("right_anchor") == 9
        and row.get("row_pair") == "salt206_salt208"
    )


def p581_above_rank3_shape_no_mod7(row: Feature) -> bool:
    return phase(row) == 1 and row.get("salt_right") == 208 and row.get("right_anchor") == 3


def p581_above_rank3_exact_mod7_control(row: Feature) -> bool:
    return p581_above_rank3_shape_no_mod7(row) and mod7(row) == 4


def p581_anchor3_right208_all_phases(row: Feature) -> bool:
    return row.get("salt_right") == 208 and row.get("right_anchor") == 3


def p581_below_or_rank3_shape_no_mod7(row: Feature) -> bool:
    return p581_below_shape_no_mod7(row) or p581_above_rank3_shape_no_mod7(row)


def p581_selected_miss_replay_control(row: Feature) -> bool:
    return row.get("right_anchor") == 9 and row.get("salt_right") in {207, 208} and phase(row) in {0, 2, 11}


def rule_specs() -> list[tuple[str, str, Predicate]]:
    return [
        (
            "p581_below_shape_no_mod7",
            "P581 below-rho public pocket without overfit mod7: phase3/right208/anchor9/salt206+salt208",
            p581_below_shape_no_mod7,
        ),
        (
            "p581_below_exact_mod7_control",
            "P581 below-rho exact one-window pocket including mod7=6",
            p581_below_exact_mod7_control,
        ),
        (
            "p581_anchor9_salt206_salt208_all_phases",
            "P581 below-rho row pair and anchor across all phases",
            p581_anchor9_salt206_salt208_all_phases,
        ),
        (
            "p581_above_rank3_shape_no_mod7",
            "P581 direct-verified rank-3 material without overfit mod7: phase1/right208/anchor3",
            p581_above_rank3_shape_no_mod7,
        ),
        (
            "p581_above_rank3_exact_mod7_control",
            "P581 direct-verified rank-3 exact one-window pocket including mod7=4",
            p581_above_rank3_exact_mod7_control,
        ),
        (
            "p581_anchor3_right208_all_phases",
            "P581 rank-3 anchor/right-salt shape across all phases",
            p581_anchor3_right208_all_phases,
        ),
        (
            "p581_below_or_rank3_shape_no_mod7",
            "Union of P581 below-rho pocket and P581 rank-3 diagnostic pocket",
            p581_below_or_rank3_shape_no_mod7,
        ),
        (
            "p581_selected_miss_replay_control",
            "P581 broad anchor9 phase-pool miss rule replayed as a negative control",
            p581_selected_miss_replay_control,
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
    return {
        "description": description,
        "direct_below_rho_verified_count": len(selected_positive),
        "direct_below_rho_verified_precision": ratio(len(selected_positive), len(selected)),
        "direct_below_rho_verified_recall": ratio(len(selected_positive), len(positives)),
        "direct_verified_count": len(selected_verified),
        "direct_verified_precision": ratio(len(selected_verified), len(selected)),
        "direct_verified_recall": ratio(len(selected_verified), len(verified)),
        "direct_verified_rank3_count": len(selected_rank3),
        "examples": [compact_row(row) for row in selected[:12]],
        "positive_examples": [compact_row(row) for row in selected_positive[:12]],
        "rank3_examples": [compact_row(row) for row in selected_rank3[:12]],
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
    selected_misses = [
        row for row in train_rows if p581_selected_miss_replay_control(row) and not row["direct_verified"]
    ]
    train_summary = {
        "above_rho_rank3_direct_verified": cohort_summary(
            [row for row in train_rows if row["direct_verified"] and not row["direct_below_rho_verified"]],
            "above_rho_rank3_direct_verified",
        ),
        "below_rho_direct_verified": cohort_summary(
            [row for row in train_rows if row["direct_below_rho_verified"]],
            "below_rho_direct_verified",
        ),
        "selected_misses": cohort_summary(selected_misses, "selected_misses"),
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
            "HEURISTIC: P581 feature deltas are empirical relation-supply hypotheses, not algebraic theorems.",
            "NO SPEEDUP CLAIM: public product-gate selection, sparse linear algebra, and target descent remain separate gates.",
        ],
        "method": "p582_feature_delta_scout",
        "rule_reports": reports,
        "schema": "ecdlp.low_term_total2_p582_feature_delta_scout.v1",
        "summary": {
            "best_below_rho_rule": best_below,
            "best_direct_verified_rule": best_verified,
            "claim_status": (
                "P582_FEATURE_DELTA_MAIN_RULE_VALIDATION_POSITIVE"
                if main_report["direct_below_rho_verified_count"]
                else "P582_FEATURE_DELTA_CONTROL_RULE_VALIDATION_POSITIVE"
                if best_below["direct_below_rho_verified_count"]
                else "P582_FEATURE_DELTA_DIRECT_VERIFIED_DIAGNOSTIC"
                if best_verified["direct_verified_count"]
                else "NEGATIVE_RESULT_P582_FEATURE_DELTA_NO_VALIDATION_SIGNAL"
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
