#!/usr/bin/env python3
"""P594 phase10/right207/anchor9/salt206 adjacent-holdout scout.

Rules use source-public metadata only. Direct verifier outcomes are joined only
as labels after selection. The adjacent 20989..21000 block can test phase10
persistence, but the exact phase10/mod7=0 repeat is transfer 21070.
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
DEFAULT_TRAIN_SOURCE = STATE_DIR / "low_term_total2_order9887_p593_phase3_right207_anchor9_exact_crt_source_20977_20988_probe.json"
DEFAULT_TRAIN_GATE = (
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p593_order9887_phase3_right207_anchor9_exact_crt_20977_20988_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p594_phase10_right207_anchor9_salt206_source_20989_21000_probe.json"
DEFAULT_GATE = (
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p594_order9887_phase10_right207_anchor9_salt206_20989_21000_density_gate_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_p594_phase10_right207_anchor9_salt206_scout_20989_21000_probe.json"

SALT207_ROW_PAIRS = {
    "salt203_salt207",
    "salt205_salt207",
    "salt206_salt207",
}
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


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def phase(row: Feature) -> int:
    return int_value(row.get("transfer_mod12"), -1)


def mod7(row: Feature) -> int:
    return int_value(row.get("transfer_mod7"), -1)


def primary_phase10_right207_anchor9_salt206(row: Feature) -> bool:
    return phase(row) == 10 and row.get("row_pair") == "salt206_salt207" and row.get("right_anchor") == 9


def phase10_mod7_5_right207_anchor9_salt206(row: Feature) -> bool:
    return primary_phase10_right207_anchor9_salt206(row) and mod7(row) == 5


def phase10_mod7_0_right207_anchor9_salt206(row: Feature) -> bool:
    return primary_phase10_right207_anchor9_salt206(row) and mod7(row) == 0


def phase10_right207_anchor9_all_pairs(row: Feature) -> bool:
    return phase(row) == 10 and row.get("row_pair") in SALT207_ROW_PAIRS and row.get("right_anchor") == 9


def phase10_right207_anchor_band(row: Feature) -> bool:
    return phase(row) == 10 and row.get("row_pair") in SALT207_ROW_PAIRS and row.get("right_anchor") in {3, 6, 9, 13}


def right207_anchor9_all_phases(row: Feature) -> bool:
    return row.get("row_pair") in SALT207_ROW_PAIRS and row.get("right_anchor") == 9


def right207_anchor_band_all_phases(row: Feature) -> bool:
    return row.get("row_pair") in SALT207_ROW_PAIRS and row.get("right_anchor") in {3, 6, 9, 13}


def broad_salt206_replay(row: Feature) -> bool:
    return row.get("row_pair") in {"salt206_salt207", "salt206_salt208"}


def phase10_anchor9_all_rowpairs(row: Feature) -> bool:
    return phase(row) == 10 and row.get("right_anchor") == 9


def stale_phase3_mod7_0_right207_anchor9(row: Feature) -> bool:
    return phase(row) == 3 and mod7(row) == 0 and row.get("row_pair") in SALT207_ROW_PAIRS and row.get("right_anchor") == 9


def failed_phase9_right208_anchor7(row: Feature) -> bool:
    return phase(row) == 9 and row.get("row_pair") in RIGHT208_ROW_PAIRS and row.get("right_anchor") == 7


def rule_specs() -> list[tuple[str, str, Predicate]]:
    return [
        (
            "p594_phase10_right207_anchor9_salt206",
            "Primary P593 control-positive pocket: phase10/right207/anchor9/salt206_salt207",
            primary_phase10_right207_anchor9_salt206,
        ),
        (
            "p594_phase10_mod7_5_right207_anchor9_salt206_adjacent",
            "Adjacent-block shifted-mod7 control: phase10/mod7=5/right207/anchor9/salt206_salt207",
            phase10_mod7_5_right207_anchor9_salt206,
        ),
        (
            "p594_phase10_mod7_0_right207_anchor9_salt206_exact_control",
            "Exact P593 mod7=0 control; expected zero selections until transfer 21070",
            phase10_mod7_0_right207_anchor9_salt206,
        ),
        (
            "p594_phase10_right207_anchor9_all_pairs",
            "phase10/right207/anchor9 across emitted salt207 row pairs",
            phase10_right207_anchor9_all_pairs,
        ),
        (
            "p594_phase10_right207_anchor_band",
            "phase10/right207 anchor band {3,6,9,13}",
            phase10_right207_anchor_band,
        ),
        (
            "p594_right207_anchor9_all_phases",
            "right207/anchor9 across all phases",
            right207_anchor9_all_phases,
        ),
        (
            "p594_right207_anchor_band_all_phases",
            "right207 anchor band {3,6,9,13} across all phases",
            right207_anchor_band_all_phases,
        ),
        (
            "p594_broad_salt206_replay",
            "Broad salt206 row-pair replay control",
            broad_salt206_replay,
        ),
        (
            "p594_phase10_anchor9_all_rowpairs",
            "phase10/anchor9 across all emitted row pairs",
            phase10_anchor9_all_rowpairs,
        ),
        (
            "p594_stale_phase3_mod7_0_right207_anchor9",
            "Failed P593 primary family as stale-family control",
            stale_phase3_mod7_0_right207_anchor9,
        ),
        (
            "p594_failed_phase9_right208_anchor7",
            "Failed right208 phase9 anchor7 control",
            failed_phase9_right208_anchor7,
        ),
    ]


def feature_key(row: Feature) -> str:
    return (
        f"phase{row.get('transfer_mod12')}_mod7{row.get('transfer_mod7')}_"
        f"right{row.get('salt_right')}_anchor{row.get('right_anchor')}_{row.get('row_pair')}"
    )


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
        "top_k": row["top_k"],
        "transfer_index": row["transfer_index"],
        "transfer_mod12": row["transfer_mod12"],
        "transfer_mod7": row["transfer_mod7"],
    }


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
    rank3 = [row for row in verified if int_value(row.get("rank")) >= 3]
    selected_positive = [row for row in selected if row["direct_below_rho_verified"]]
    selected_verified = [row for row in selected if row["direct_verified"]]
    selected_rank3 = [row for row in selected_verified if int_value(row.get("rank")) >= 3]
    return {
        "case_entry_sample": [row["case_entry"] for row in selected[:64]],
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
        "raw_below_rho_count": len(positives),
        "raw_direct_verified_count": len(verified),
        "raw_rank3_count": len(rank3),
        "right_anchor_counts": dict(Counter(str(row["right_anchor"]) for row in selected).most_common()),
        "row_pair_counts": dict(Counter(str(row["row_pair"]) for row in selected).most_common(16)),
        "rule": name,
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-source", type=Path, default=DEFAULT_TRAIN_SOURCE)
    parser.add_argument("--train-gate", type=Path, default=DEFAULT_TRAIN_GATE)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--gate", type=Path, default=DEFAULT_GATE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def best_report(reports: list[dict[str, Any]], primary: dict[str, Any], field: str) -> dict[str, Any]:
    return max(
        reports,
        key=lambda item: (
            int(item[field]),
            int(item["direct_verified_rank3_count"]),
            float(item["direct_below_rho_verified_precision"] or item["direct_verified_precision"] or 0.0),
            int(item["selected_count"] > 0),
            int(item is primary),
            -int(item["selected_count"]),
        ),
    )


def main() -> int:
    args = parse_args()
    train_rows = p570.source_rows([args.train_source], p570.gate_labels([args.train_gate]), "p593_training")
    validation_rows = p570.source_rows([args.source], p570.gate_labels([args.gate]), "p594_validation")
    reports = [
        report(validation_rows, [row for row in validation_rows if predicate(row)], name, description)
        for name, description, predicate in rule_specs()
    ]
    main_report = reports[0]
    best_below = best_report(reports, main_report, "direct_below_rho_verified_count")
    best_verified = best_report(reports, main_report, "direct_verified_count")
    validation_summary = dataset_summary(validation_rows)
    if main_report["direct_below_rho_verified_count"]:
        claim_status = "P594_PRIMARY_PHASE10_RIGHT207_ANCHOR9_SALT206_BELOW_RHO_VALIDATION_POSITIVE"
    elif main_report["direct_verified_count"]:
        claim_status = "P594_PRIMARY_PHASE10_RIGHT207_ANCHOR9_SALT206_DIRECT_VALIDATION_POSITIVE_ABOVE_RHO"
    elif best_below["direct_below_rho_verified_count"] or best_verified["direct_verified_count"]:
        claim_status = "P594_CONTROL_RULE_VALIDATION_POSITIVE_PRIMARY_MISSED"
    elif validation_summary["direct_verified_count"] == 0:
        claim_status = "NEGATIVE_RESULT_P594_VALIDATION_QUIET_BLOCK"
    else:
        claim_status = "NEGATIVE_RESULT_P594_PRIMARY_MISSED_NONQUIET_BLOCK"
    payload = {
        "artifacts": {
            "gate": str(args.gate),
            "source": str(args.source),
            "train_gate": str(args.train_gate),
            "train_source": str(args.train_source),
        },
        "claim_status": claim_status,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: order-9887 local verifier harness only.",
            "SOURCE-ONLY SELECTION: validation rules use public phase, mod7, salt, anchor, row-pair, selector, and policy-role metadata only.",
            "LABEL BOUNDARY: direct verifier outcomes are joined only for evaluation.",
            "CRT BOUNDARY: adjacent block tests phase10 persistence, not exact mod7=0 recurrence; exact repeat is transfer 21070.",
            "NO SPEEDUP CLAIM: relation collection, sparse linear algebra, and target descent remain separate gates.",
        ],
        "method": "p594_phase10_right207_anchor9_salt206_scout",
        "rule_reports": reports,
        "schema": "ecdlp.low_term_total2_p594_phase10_right207_anchor9_salt206_scout.v1",
        "summary": {
            "best_below_rho_rule": best_below,
            "best_direct_verified_rule": best_verified,
            "claim_status": claim_status,
            "main_rule": main_report,
            "training_cohorts": {
                "p593_direct_verified": cohort_summary(
                    [row for row in train_rows if row["direct_verified"]],
                    "p593_direct_verified",
                ),
                "p593_primary_pocket": cohort_summary(
                    [row for row in train_rows if primary_phase10_right207_anchor9_salt206(row)],
                    "p593_primary_pocket",
                ),
                "p593_right207_anchor9_all_phases": cohort_summary(
                    [row for row in train_rows if right207_anchor9_all_phases(row)],
                    "p593_right207_anchor9_all_phases",
                ),
                "p593_broad_salt206": cohort_summary(
                    [row for row in train_rows if broad_salt206_replay(row)],
                    "p593_broad_salt206",
                ),
            },
            "validation_dataset": validation_summary,
        },
    }
    write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
