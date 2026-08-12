#!/usr/bin/env python3
"""Near-rho family-bank scheduler for order-9887 leaf-16 routing."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p570_pre_hit_source_feature_scout as p570


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p576_leaf16_near_rho_family_bank_source_20713_20724_probe.json"
DEFAULT_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p576_order9887_near_rho_family_bank_20713_20724_density_gate_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p576_near_rho_family_bank_scheduler_20713_20724_probe.json"


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


def right_motif(salt_right: int, right_anchor: int) -> Predicate:
    return lambda row: row.get("salt_right") == salt_right and row.get("right_anchor") == right_anchor


def row_pair_anchor(row_pair: str, right_anchor: int) -> Predicate:
    return lambda row: row.get("row_pair") == row_pair and row.get("right_anchor") == right_anchor


def any_of(*parts: Predicate) -> Predicate:
    return lambda row: any(part(row) for part in parts)


def rule_specs() -> list[tuple[str, str, Predicate]]:
    p575_near = row_pair_anchor("salt204_salt206", 3)
    p574_raw = right_motif(207, 11)
    p572_raw = right_motif(208, 3)
    return [
        (
            "near_rho_family_bank_union",
            "union of P575 salt204+salt206/anchor3, P574 right207/anchor11, and P572 right208/anchor3",
            any_of(p575_near, p574_raw, p572_raw),
        ),
        (
            "p575_salt204_salt206_anchor3",
            "P575 near-rho above-rho diagnostic shape",
            p575_near,
        ),
        (
            "p574_right207_anchor11",
            "P574 below-rho raw motif",
            p574_raw,
        ),
        (
            "p572_right208_anchor3",
            "P572 below-rho raw motif",
            p572_raw,
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


def report(rows: list[Feature], selected: list[Feature], name: str, description: str) -> dict[str, Any]:
    positives = [row for row in rows if row["direct_below_rho_verified"]]
    selected_positive = [row for row in selected if row["direct_below_rho_verified"]]
    selected_verified = [row for row in selected if row["direct_verified"]]
    return {
        "description": description,
        "direct_below_rho_verified_count": len(selected_positive),
        "direct_below_rho_verified_precision": ratio(len(selected_positive), len(selected)),
        "direct_below_rho_verified_recall": ratio(len(selected_positive), len(positives)),
        "direct_verified_count": len(selected_verified),
        "direct_verified_precision": ratio(len(selected_verified), len(selected)),
        "examples": [compact_row(row) for row in selected[:12]],
        "positive_examples": [compact_row(row) for row in selected_positive[:12]],
        "raw_positive_count": len(positives),
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
        "verified_motif_counts": dict(
            Counter(f"{row.get('row_pair')}_anchor{row.get('right_anchor')}" for row in verified).most_common()
        ),
        "verified_transfer_counts": dict(
            sorted(Counter(str(row["transfer_index"]) for row in verified).items(), key=lambda item: int(item[0]))
        ),
        "positive_motif_counts": dict(
            Counter(f"{row.get('row_pair')}_anchor{row.get('right_anchor')}" for row in positives).most_common()
        ),
        "positive_transfer_counts": dict(
            sorted(Counter(str(row["transfer_index"]) for row in positives).items(), key=lambda item: int(item[0]))
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--gate", type=Path, default=DEFAULT_GATE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = p570.source_rows([args.source], p570.gate_labels([args.gate]), "validation")
    reports = [
        report(rows, [row for row in rows if predicate(row)], name, description)
        for name, description, predicate in rule_specs()
    ]
    main_report = reports[0]
    payload = {
        "artifacts": {"gate": str(args.gate), "source": str(args.source)},
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: order-9887 local verifier harness only.",
            "SOURCE-ONLY SELECTION: rules use row pair, right salt, and right anchor only.",
            "LABEL BOUNDARY: direct verifier outcomes are joined only for evaluation.",
            "HEURISTIC: near-rho bank growth is a source-generation diagnostic, not an end-to-end algorithm.",
            "NO SPEEDUP CLAIM: below-rho promotion is separate from above-rho relation-bank material.",
        ],
        "method": "p576_near_rho_family_bank_scheduler",
        "rule_reports": reports,
        "schema": "ecdlp.low_term_total2_p576_near_rho_family_bank_scheduler.v1",
        "summary": {
            "claim_status": (
                "NEAR_RHO_FAMILY_BANK_SCHEDULER_VALIDATION_POSITIVE"
                if main_report["direct_below_rho_verified_count"]
                else "NEAR_RHO_FAMILY_BANK_DIRECT_VERIFIED_DIAGNOSTIC"
                if main_report["direct_verified_count"]
                else "NEGATIVE_RESULT_NEAR_RHO_FAMILY_BANK_NO_VALIDATION_SIGNAL"
            ),
            "dataset": dataset_summary(rows),
            "main_rule": main_report,
        },
    }
    write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
