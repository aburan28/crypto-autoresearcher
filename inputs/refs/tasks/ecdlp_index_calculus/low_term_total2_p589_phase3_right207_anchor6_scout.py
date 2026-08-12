#!/usr/bin/env python3
"""P589 phase3/right207/anchor6 recurrence scout.

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
DEFAULT_TRAIN_SOURCE = STATE_DIR / "low_term_total2_order9887_p588_right208_phase_drift_source_20857_20868_probe.json"
DEFAULT_TRAIN_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p588_order9887_right208_phase_drift_20857_20868_density_gate_probe.json"
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p589_phase3_right207_anchor6_source_20869_20880_probe.json"
DEFAULT_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p589_order9887_phase3_right207_anchor6_20869_20880_density_gate_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p589_phase3_right207_anchor6_scout_20869_20880_probe.json"

SALT207_ROW_PAIRS = {
    "salt203_salt207",
    "salt204_salt207",
    "salt205_salt207",
    "salt206_salt207",
}
P588_BELOW_ROW_PAIRS = {"salt205_salt207", "salt206_salt207"}
P588_RANK3_ROW_PAIR = "salt203_salt207"
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


def phase3_right207_anchor6_all_salt207(row: Feature) -> bool:
    return phase(row) == 3 and row.get("row_pair") in SALT207_ROW_PAIRS and row.get("right_anchor") == 6


def phase3_right207_anchor6_below_pairs(row: Feature) -> bool:
    return phase(row) == 3 and row.get("row_pair") in P588_BELOW_ROW_PAIRS and row.get("right_anchor") == 6


def phase3_right207_anchor6_rank3_pair(row: Feature) -> bool:
    return phase(row) == 3 and row.get("row_pair") == P588_RANK3_ROW_PAIR and row.get("right_anchor") == 6


def phase3_right207_anchor6_exact_mod7_6(row: Feature) -> bool:
    return phase3_right207_anchor6_all_salt207(row) and mod7(row) == 6


def right207_anchor6_all_phases(row: Feature) -> bool:
    return row.get("row_pair") in SALT207_ROW_PAIRS and row.get("right_anchor") == 6


def phase3_right207_anchor_band(row: Feature) -> bool:
    return phase(row) == 3 and row.get("row_pair") in SALT207_ROW_PAIRS and row.get("right_anchor") in {3, 6, 9, 13}


def failed_p588_phase9_right208_anchor13(row: Feature) -> bool:
    return phase(row) == 9 and row.get("row_pair") in RIGHT208_ROW_PAIRS and row.get("right_anchor") == 13


def failed_p588_phase6_right208_anchor9(row: Feature) -> bool:
    return phase(row) == 6 and row.get("row_pair") in RIGHT208_ROW_PAIRS and row.get("right_anchor") == 9


def p586_p587_failed_salt206_replay(row: Feature) -> bool:
    return row.get("row_pair") in {"salt206_salt207", "salt206_salt208"}


def rule_specs() -> list[tuple[str, str, Predicate]]:
    return [
        (
            "p589_phase3_right207_anchor6_all_salt207",
            "P588 raw-positive pocket: phase3/right207/anchor6 across all salt*_salt207 row pairs",
            phase3_right207_anchor6_all_salt207,
        ),
        (
            "p589_phase3_right207_anchor6_below_pairs",
            "P588 below-rho subfamilies: phase3/right207/anchor6 with salt205+salt207 or salt206+salt207",
            phase3_right207_anchor6_below_pairs,
        ),
        (
            "p589_phase3_right207_anchor6_rank3_pair",
            "P588 rank-3 subfamily: phase3/right207/anchor6 with salt203+salt207",
            phase3_right207_anchor6_rank3_pair,
        ),
        (
            "p589_phase3_right207_anchor6_exact_mod7_6",
            "Exact P588 transfer-mod7 replay control for phase3/right207/anchor6",
            phase3_right207_anchor6_exact_mod7_6,
        ),
        (
            "p589_right207_anchor6_all_phases",
            "right207/anchor6 across all phases",
            right207_anchor6_all_phases,
        ),
        (
            "p589_phase3_right207_anchor_band",
            "phase3/right207 over anchor band {3,6,9,13}",
            phase3_right207_anchor_band,
        ),
        (
            "p589_failed_p588_phase9_right208_anchor13",
            "Failed P588 control: phase9/right208/anchor13",
            failed_p588_phase9_right208_anchor13,
        ),
        (
            "p589_failed_p588_phase6_right208_anchor9",
            "Failed P588 control: phase6/right208/anchor9",
            failed_p588_phase6_right208_anchor9,
        ),
        (
            "p589_p586_p587_failed_salt206_replay",
            "Older failed broad row-pair replay: row pairs starting with salt206",
            p586_p587_failed_salt206_replay,
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
        "salt_right": row["salt_right"],
        "selector": row["selector"],
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
        "rank_counts": dict(Counter(str(row["rank"]) for row in rows).most_common()),
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
        "direct_verified_rank3_count": len(selected_rank3),
        "direct_verified_recall": ratio(len(selected_verified), len(verified)),
        "examples": [compact_row(row) for row in selected[:12]],
        "positive_examples": [compact_row(row) for row in selected_positive[:12]],
        "rank3_examples": [compact_row(row) for row in selected_rank3[:12]],
        "raw_positive_count": len(positives),
        "raw_verified_count": len(verified),
        "right_anchor_counts": dict(Counter(str(row["right_anchor"]) for row in selected).most_common()),
        "row_pair_counts": dict(Counter(str(row["row_pair"]) for row in selected).most_common(16)),
        "rule": name,
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
        "positive_feature_counts": dict(Counter(feature_key(row) for row in positives).most_common(16)),
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
            "SOURCE-ONLY SELECTION: validation rules use public phase, mod7, salt, anchor, row-pair, and selector metadata only.",
            "LABEL BOUNDARY: direct verifier outcomes are joined only for evaluation.",
            "NO SPEEDUP CLAIM: relation collection, sparse linear algebra, and target descent remain separate gates.",
        ],
        "method": "p589_phase3_right207_anchor6_scout",
        "rule_reports": reports,
        "schema": "ecdlp.low_term_total2_p589_phase3_right207_anchor6_scout.v1",
        "summary": {
            "best_below_rho_rule": best_below,
            "best_direct_verified_rule": best_verified,
            "claim_status": (
                "P589_PHASE3_RIGHT207_ANCHOR6_MAIN_RULE_VALIDATION_POSITIVE"
                if main_report["direct_below_rho_verified_count"] or main_report["direct_verified_count"]
                else "P589_PHASE3_RIGHT207_ANCHOR6_CONTROL_RULE_VALIDATION_POSITIVE"
                if best_below["direct_below_rho_verified_count"] or best_verified["direct_verified_count"]
                else "NEGATIVE_RESULT_P589_NO_VALIDATION_SIGNAL"
            ),
            "main_rule": main_report,
            "training_cohorts": {
                "p588_below_rho": cohort_summary(
                    [row for row in train_rows if row["direct_below_rho_verified"]],
                    "p588_below_rho",
                ),
                "p588_phase3_right207_anchor6": cohort_summary(
                    [row for row in train_rows if phase3_right207_anchor6_all_salt207(row)],
                    "p588_phase3_right207_anchor6",
                ),
                "p588_right208_phase_drift_controls": cohort_summary(
                    [
                        row
                        for row in train_rows
                        if failed_p588_phase9_right208_anchor13(row) or failed_p588_phase6_right208_anchor9(row)
                    ],
                    "p588_right208_phase_drift_controls",
                ),
            },
            "validation_dataset": dataset_summary(validation_rows),
        },
    }
    write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
