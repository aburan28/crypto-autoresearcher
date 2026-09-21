#!/usr/bin/env python3
"""P583 salt-205 anchor-9 relation-supply and rank-growth split scout.

Selection rules use source-public metadata only. Direct verifier outcomes are
joined as labels for evaluation after the rule has selected rows.
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
DEFAULT_TRAIN_SOURCE = STATE_DIR / "low_term_total2_order9887_p582_feature_delta_source_20785_20796_probe.json"
DEFAULT_TRAIN_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p582_order9887_feature_delta_20785_20796_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p583_salt205_rank_split_source_20797_20808_probe.json"
DEFAULT_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p583_order9887_salt205_rank_split_20797_20808_density_gate_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_p583_salt205_anchor9_rank_split_scout_20797_20808_probe.json"


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


def p582_salt205_anchor9_split_exact_mod7_control(row: Feature) -> bool:
    return (
        phase(row) == 5
        and mod7(row) == 6
        and row.get("salt_right") == 208
        and row.get("right_anchor") == 9
        and row.get("row_pair") == "salt205_salt208"
    ) or (
        phase(row) == 10
        and mod7(row) == 4
        and row.get("salt_right") == 207
        and row.get("right_anchor") == 9
        and row.get("row_pair") == "salt205_salt207"
    )


def p582_salt205_anchor9_all_phases(row: Feature) -> bool:
    return (
        row.get("right_anchor") == 9
        and row.get("row_pair") in {"salt205_salt207", "salt205_salt208"}
        and row.get("salt_right") in {207, 208}
    )


def p582_salt205_right208_anchor9_all_phases(row: Feature) -> bool:
    return (
        row.get("salt_right") == 208
        and row.get("right_anchor") == 9
        and row.get("row_pair") == "salt205_salt208"
    )


def p582_salt205_right207_anchor9_all_phases(row: Feature) -> bool:
    return (
        row.get("salt_right") == 207
        and row.get("right_anchor") == 9
        and row.get("row_pair") == "salt205_salt207"
    )


def p582_rank_growth_phase4_right208_anchor6_salt206_salt208(row: Feature) -> bool:
    return (
        phase(row) == 4
        and row.get("salt_right") == 208
        and row.get("right_anchor") == 6
        and row.get("row_pair") == "salt206_salt208"
    )


def p582_rank_growth_exact_mod7_control(row: Feature) -> bool:
    return p582_rank_growth_phase4_right208_anchor6_salt206_salt208(row) and mod7(row) == 5


def p582_rank_growth_anchor6_right208_salt206_salt208_all_phases(row: Feature) -> bool:
    return (
        row.get("salt_right") == 208
        and row.get("right_anchor") == 6
        and row.get("row_pair") == "salt206_salt208"
    )


def p582_phase4_right208_salt206_salt208_all_anchors(row: Feature) -> bool:
    return phase(row) == 4 and row.get("salt_right") == 208 and row.get("row_pair") == "salt206_salt208"


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
            "p582_salt205_anchor9_split_no_mod7",
            "P582 raw below-rho split without overfit mod7: phase5/right208/salt205+salt208 OR phase10/right207/salt205+salt207, anchor9",
            p582_salt205_anchor9_split_no_mod7,
        ),
        (
            "p582_salt205_anchor9_split_exact_mod7_control",
            "P582 raw below-rho exact split including mod7 residues",
            p582_salt205_anchor9_split_exact_mod7_control,
        ),
        (
            "p582_salt205_anchor9_all_phases",
            "salt205 anchor9 rows for right207/right208 across all phases",
            p582_salt205_anchor9_all_phases,
        ),
        (
            "p582_salt205_right208_anchor9_all_phases",
            "salt205+salt208 anchor9 across all phases",
            p582_salt205_right208_anchor9_all_phases,
        ),
        (
            "p582_salt205_right207_anchor9_all_phases",
            "salt205+salt207 anchor9 across all phases",
            p582_salt205_right207_anchor9_all_phases,
        ),
        (
            "p582_rank_growth_phase4_right208_anchor6_salt206_salt208",
            "P582 factor-rank greedy row shape: phase4/right208/anchor6/salt206+salt208",
            p582_rank_growth_phase4_right208_anchor6_salt206_salt208,
        ),
        (
            "p582_rank_growth_exact_mod7_control",
            "P582 factor-rank greedy row exact shape including mod7=5",
            p582_rank_growth_exact_mod7_control,
        ),
        (
            "p582_rank_growth_anchor6_right208_salt206_salt208_all_phases",
            "P582 rank-growth row pair/right-salt/anchor6 across all phases",
            p582_rank_growth_anchor6_right208_salt206_salt208_all_phases,
        ),
        (
            "p582_phase4_right208_salt206_salt208_all_anchors",
            "P582 phase4/right208/salt206+salt208 verified-burst control across anchors",
            p582_phase4_right208_salt206_salt208_all_anchors,
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
        "rank4_direct_verified": cohort_summary(
            [row for row in train_rows if row["direct_verified"] and int(row.get("rank") or 0) >= 4],
            "rank4_direct_verified",
        ),
        "rank_growth_shape_training": cohort_summary(
            [row for row in train_rows if p582_rank_growth_phase4_right208_anchor6_salt206_salt208(row)],
            "rank_growth_shape_training",
        ),
        "direct_verified_rank3plus": cohort_summary(
            [row for row in train_rows if row["direct_verified"] and int(row.get("rank") or 0) >= 3],
            "direct_verified_rank3plus",
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
    best_rank4 = max(
        reports,
        key=lambda item: (
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
            "HEURISTIC: salt205 anchor9 drift and rank-growth rules are empirical relation-supply hypotheses, not algebraic theorems.",
            "NO SPEEDUP CLAIM: public product-gate selection, sparse linear algebra, and target descent remain separate gates.",
        ],
        "method": "p583_salt205_anchor9_rank_split_scout",
        "rule_reports": reports,
        "schema": "ecdlp.low_term_total2_p583_salt205_anchor9_rank_split_scout.v1",
        "summary": {
            "best_below_rho_rule": best_below,
            "best_direct_verified_rule": best_verified,
            "best_rank4_rule": best_rank4,
            "claim_status": (
                "P583_SALT205_ANCHOR9_MAIN_RULE_VALIDATION_POSITIVE"
                if main_report["direct_below_rho_verified_count"]
                else "P583_SALT205_ANCHOR9_CONTROL_RULE_VALIDATION_POSITIVE"
                if best_below["direct_below_rho_verified_count"]
                else "P583_RANK_GROWTH_DIRECT_VERIFIED_DIAGNOSTIC"
                if best_rank4["direct_verified_rank4_count"]
                else "P583_DIRECT_VERIFIED_DIAGNOSTIC"
                if best_verified["direct_verified_count"]
                else "NEGATIVE_RESULT_P583_NO_VALIDATION_SIGNAL"
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
