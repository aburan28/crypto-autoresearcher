#!/usr/bin/env python3
"""Phase-aware motif scheduler for order-9887 leaf-16 routing."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p570_pre_hit_source_feature_scout as p570


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p578_leaf16_phase_aware_motif_source_20737_20748_probe.json"
DEFAULT_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p578_order9887_phase_aware_motif_20737_20748_density_gate_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p578_phase_aware_motif_scheduler_20737_20748_probe.json"


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


def salt_anchor_phase(salt_right: int, right_anchor: int, phase: int) -> Predicate:
    return (
        lambda row: row.get("salt_right") == salt_right
        and row.get("right_anchor") == right_anchor
        and int(row.get("transfer_mod12") or -1) == phase
    )


def right_motif(salt_right: int, right_anchor: int) -> Predicate:
    return lambda row: row.get("salt_right") == salt_right and row.get("right_anchor") == right_anchor


def row_pair_anchor(row_pair: str, right_anchor: int) -> Predicate:
    return lambda row: row.get("row_pair") == row_pair and row.get("right_anchor") == right_anchor


def any_of(*parts: Predicate) -> Predicate:
    return lambda row: any(part(row) for part in parts)


def rule_specs() -> list[tuple[str, str, Predicate]]:
    p577_phase2_r208_a11 = salt_anchor_phase(208, 11, 2)
    p577_phase11_r207_a9 = salt_anchor_phase(207, 9, 11)
    p577_phase_union = any_of(p577_phase2_r208_a11, p577_phase11_r207_a9)
    p577_broad_union = any_of(right_motif(208, 11), right_motif(207, 9))
    p576_row_pair_union = any_of(row_pair_anchor("salt206_salt207", 9), row_pair_anchor("salt204_salt206", 7))
    return [
        (
            "p577_phase_aware_union",
            "P577 phase-aware motifs: phase2/right208/anchor11 and phase11/right207/anchor9",
            p577_phase_union,
        ),
        (
            "p577_phase2_right208_anchor11",
            "P577 transfer-20726 phase-2 motif",
            p577_phase2_r208_a11,
        ),
        (
            "p577_phase11_right207_anchor9",
            "P577 transfer-20735 phase-11 motif",
            p577_phase11_r207_a9,
        ),
        (
            "p577_broad_right208_anchor11_or_right207_anchor9",
            "same salt/anchor motifs without phase restriction",
            p577_broad_union,
        ),
        (
            "p576_row_pair_motif_control",
            "P576 row-pair motif control: salt206+salt207/anchor9 or salt204+salt206/anchor7",
            p576_row_pair_union,
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
    verified = [row for row in rows if row["direct_verified"]]
    selected_positive = [row for row in selected if row["direct_below_rho_verified"]]
    selected_verified = [row for row in selected if row["direct_verified"]]
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
        "positive_motif_counts": dict(
            Counter(f"{row.get('row_pair')}_anchor{row.get('right_anchor')}" for row in positives).most_common()
        ),
        "positive_phase_salt_anchor_counts": dict(
            Counter(
                f"phase{row.get('transfer_mod12')}_right{row.get('salt_right')}_anchor{row.get('right_anchor')}"
                for row in positives
            ).most_common()
        ),
        "positive_transfer_counts": dict(
            sorted(Counter(str(row["transfer_index"]) for row in positives).items(), key=lambda item: int(item[0]))
        ),
        "verified_motif_counts": dict(
            Counter(f"{row.get('row_pair')}_anchor{row.get('right_anchor')}" for row in verified).most_common()
        ),
        "verified_transfer_counts": dict(
            sorted(Counter(str(row["transfer_index"]) for row in verified).items(), key=lambda item: int(item[0]))
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
            "SOURCE-ONLY SELECTION: rules use public transfer phase, right salt, and right anchor only.",
            "LABEL BOUNDARY: direct verifier outcomes are joined only for evaluation.",
            "HEURISTIC: phase-aware recurrence is an empirical scheduler hypothesis, not a theorem.",
            "NO SPEEDUP CLAIM: public product-gate selection, sparse linear algebra, and target descent remain separate gates.",
        ],
        "method": "p578_phase_aware_motif_scheduler",
        "rule_reports": reports,
        "schema": "ecdlp.low_term_total2_p578_phase_aware_motif_scheduler.v1",
        "summary": {
            "claim_status": (
                "P577_PHASE_AWARE_MOTIF_SCHEDULER_VALIDATION_POSITIVE"
                if main_report["direct_below_rho_verified_count"]
                else "P577_PHASE_AWARE_MOTIF_DIRECT_VERIFIED_DIAGNOSTIC"
                if main_report["direct_verified_count"]
                else "NEGATIVE_RESULT_P577_PHASE_AWARE_MOTIF_NO_VALIDATION_SIGNAL"
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
