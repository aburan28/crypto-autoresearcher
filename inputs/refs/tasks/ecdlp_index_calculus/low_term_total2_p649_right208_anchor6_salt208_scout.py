#!/usr/bin/env python3
"""P649 adjacent scan for P648 right208 anchor6 salt208 branch."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p643_phase0_salt203_burst_scout as p643


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p649_order9887_right208_anchor6_salt208_22252_22264_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p649_right208_anchor6_salt208_source_22252_22264_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p649_right208_anchor6_salt208_scout_22252_22264_probe.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def right208_salt208_all_anchor(f: dict[str, Any]) -> bool:
    return (
        p643.standard_leaf(f)
        and f.get("salt_left") in p643.SALT208_LEFTS
        and f.get("salt_right") == 208
        and f.get("right_anchor") in p643.ANCHORS
    )


def right208_anchor6_salt208_family(f: dict[str, Any]) -> bool:
    return right208_salt208_all_anchor(f) and f.get("right_anchor") == 6


def phase10_right208_anchor6_salt208_family(f: dict[str, Any]) -> bool:
    return right208_anchor6_salt208_family(f) and f.get("transfer_mod12") == 10


def mod7_0_right208_anchor6_salt208_family(f: dict[str, Any]) -> bool:
    return right208_anchor6_salt208_family(f) and f.get("transfer_mod7") == 0


def phase10_mod7_0_right208_anchor6_salt208_family(f: dict[str, Any]) -> bool:
    return (
        right208_anchor6_salt208_family(f)
        and f.get("transfer_mod12") == 10
        and f.get("transfer_mod7") == 0
    )


def phase10_right208_salt208_all_anchor(f: dict[str, Any]) -> bool:
    return right208_salt208_all_anchor(f) and f.get("transfer_mod12") == 10


def mod7_0_right208_salt208_all_anchor(f: dict[str, Any]) -> bool:
    return right208_salt208_all_anchor(f) and f.get("transfer_mod7") == 0


def row_pair_anchor6(row_pair: str) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return right208_anchor6_salt208_family(f) and f.get("row_pair") == row_pair

    return pred


def phase10_row_pair_anchor6(row_pair: str) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return phase10_right208_anchor6_salt208_family(f) and f.get("row_pair") == row_pair

    return pred


RULES: list[tuple[str, str, Callable[[dict[str, Any]], bool]]] = [
    (
        "p649_phase10_mod7_0_right208_anchor6_salt208_family",
        "P648 exact phase/mod7 right208 anchor6 salt208 control; adjacent block is expected to select zero until CRT repeat",
        phase10_mod7_0_right208_anchor6_salt208_family,
    ),
    (
        "p649_phase10_right208_anchor6_salt208_family",
        "P648 phase10 right208 anchor6 salt208 family",
        phase10_right208_anchor6_salt208_family,
    ),
    (
        "p649_mod7_0_right208_anchor6_salt208_family",
        "P648 same-mod7=0 right208 anchor6 salt208 family",
        mod7_0_right208_anchor6_salt208_family,
    ),
    (
        "p649_all_phase_right208_anchor6_salt208_family",
        "P648 all-phase right208 anchor6 salt208 family",
        right208_anchor6_salt208_family,
    ),
    (
        "p649_phase10_right208_salt208_all_anchor",
        "P648 phase10 broad right208 salt208 all-anchor control",
        phase10_right208_salt208_all_anchor,
    ),
    (
        "p649_mod7_0_right208_salt208_all_anchor",
        "P648 same-mod7=0 broad right208 salt208 all-anchor control",
        mod7_0_right208_salt208_all_anchor,
    ),
    (
        "p649_broad_right208_salt208_all_anchor",
        "P648 broad right208 salt208 all-anchor control",
        right208_salt208_all_anchor,
    ),
]

for row_pair_name in ("salt203_salt208", "salt204_salt208", "salt205_salt208", "salt206_salt208"):
    RULES.append(
        (
            f"p649_phase10_anchor6_{row_pair_name}",
            f"P648 phase10 right208 anchor6 {row_pair_name} row-pair split",
            phase10_row_pair_anchor6(row_pair_name),
        )
    )
    RULES.append(
        (
            f"p649_all_phase_anchor6_{row_pair_name}",
            f"P648 all-phase right208 anchor6 {row_pair_name} row-pair split",
            row_pair_anchor6(row_pair_name),
        )
    )


def summarize_cases(features: list[dict[str, Any]]) -> dict[str, Any]:
    return p643.summarize_cases(features)


def rule_report(
    name: str,
    description: str,
    pred: Callable[[dict[str, Any]], bool],
    features: list[dict[str, Any]],
    raw_summary: dict[str, Any],
) -> dict[str, Any]:
    selected = [f for f in features if pred(f)]
    verified = [f for f in selected if f.get("direct_verified")]
    below = [f for f in selected if f.get("direct_below_rho_verified")]
    rank3 = [f for f in verified if int(f.get("rank") or 0) >= 3]
    selected_count = len(selected)
    return {
        "rule": name,
        "description": description,
        "selected_count": selected_count,
        "selected_fraction": selected_count / max(1, raw_summary["case_count"]),
        "direct_verified_count": len(verified),
        "direct_below_rho_verified_count": len(below),
        "rank3_direct_verified_count": len(rank3),
        "direct_verified_precision": len(verified) / selected_count if selected_count else 0.0,
        "direct_below_rho_verified_precision": len(below) / selected_count if selected_count else 0.0,
        "direct_verified_recall": len(verified) / max(1, raw_summary["direct_verified_count"]),
        "direct_below_rho_verified_recall": len(below)
        / max(1, raw_summary["direct_below_rho_verified_count"]),
        "rank3_direct_verified_recall": len(rank3) / max(1, raw_summary["rank3_direct_verified_count"]),
        "transfer_counts": dict(Counter(str(f["transfer_index"]) for f in selected)),
        "phase_counts": dict(Counter(str(f["transfer_mod12"]) for f in selected)),
        "mod7_counts": dict(Counter(str(f["transfer_mod7"]) for f in selected)),
        "right_anchor_counts": dict(Counter(str(f["right_anchor"]) for f in selected)),
        "row_pair_counts": dict(Counter(str(f["row_pair"]) for f in selected)),
        "verified_feature_counts": dict(Counter(p643.feature_id(f) for f in verified)),
        "positive_feature_counts": dict(Counter(p643.feature_id(f) for f in below)),
        "rank3_feature_counts": dict(Counter(p643.feature_id(f) for f in rank3)),
        "verified_rank_counts": dict(Counter(str(f.get("rank")) for f in verified)),
        "selected_direct_verified_case_entries": [p643.case_entry(f) for f in verified],
        "selected_direct_below_rho_verified_case_entries": [p643.case_entry(f) for f in below],
        "selected_rank3_direct_verified_case_entries": [p643.case_entry(f) for f in rank3],
        "positive_examples": below[:24],
        "rank3_examples": rank3[:24],
    }


def report_named(reports: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    return next((r for r in reports if r["rule"] == name), None)


def determine_claim(reports: list[dict[str, Any]], raw: dict[str, Any]) -> str:
    phase10 = report_named(reports, "p649_phase10_right208_anchor6_salt208_family")
    mod7 = report_named(reports, "p649_mod7_0_right208_anchor6_salt208_family")
    anchor6 = report_named(reports, "p649_all_phase_right208_anchor6_salt208_family")
    broad = report_named(reports, "p649_broad_right208_salt208_all_anchor")
    if phase10 and phase10["direct_below_rho_verified_count"]:
        return "P649_PHASE10_RIGHT208_ANCHOR6_SALT208_BELOW_RHO_PERSISTENCE"
    if mod7 and mod7["direct_below_rho_verified_count"]:
        return "P649_MOD7_0_RIGHT208_ANCHOR6_SALT208_BELOW_RHO_DRIFT"
    if anchor6 and anchor6["direct_below_rho_verified_count"]:
        return "P649_RIGHT208_ANCHOR6_SALT208_BELOW_RHO_DRIFT"
    if broad and broad["direct_below_rho_verified_count"]:
        return "P649_BROAD_RIGHT208_SALT208_BELOW_RHO_DRIFT"
    if any(r["direct_below_rho_verified_count"] for r in reports):
        return "P649_REGISTERED_BELOW_RHO_POSITIVE"
    if any(r["rank3_direct_verified_count"] for r in reports):
        return "P649_REGISTERED_RANK_SURFACE_POSITIVE"
    if any(r["direct_verified_count"] for r in reports):
        return "P649_REGISTERED_ABOVE_RHO_POSITIVE"
    if raw["direct_verified_count"]:
        return "NEGATIVE_RESULT_P649_REGISTERED_CONTROLS_MISSED_NONQUIET_BLOCK"
    return "NEGATIVE_RESULT_P649_RIGHT208_ANCHOR6_SALT208_QUIET_BLOCK"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", default=str(DEFAULT_GATE))
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    gate = json.loads(Path(args.gate).read_text())
    features = [p643.feature(case) for case in gate.get("cases", [])]
    raw_summary = summarize_cases(features)
    reports = [rule_report(name, desc, pred, features, raw_summary) for name, desc, pred in RULES]
    claim_status = determine_claim(reports, raw_summary)

    payload = {
        "schema": "ecdlp.low_term_total2_p649_right208_anchor6_salt208_scout.v1",
        "created_at": utc_now(),
        "method": "p649_right208_anchor6_salt208_scout",
        "claim_status": claim_status,
        "artifacts": {"source": str(args.source), "gate": str(args.gate)},
        "summary": {
            "claim_status": claim_status,
            "validation_dataset": raw_summary,
            "best_below_rho_rule": max(
                reports,
                key=lambda r: (
                    r["direct_below_rho_verified_count"],
                    r["direct_below_rho_verified_precision"],
                    -r["selected_count"],
                ),
            ),
            "best_direct_verified_rule": max(
                reports,
                key=lambda r: (
                    r["direct_verified_count"],
                    r["direct_verified_precision"],
                    -r["selected_count"],
                ),
            ),
            "best_rank3_rule": max(
                reports,
                key=lambda r: (
                    r["rank3_direct_verified_count"],
                    r["direct_verified_precision"],
                    -r["selected_count"],
                ),
            ),
        },
        "rule_reports": reports,
        "honesty_boundary": [
            "Verifier labels are used only after public selector evaluation.",
            "P649 tests adjacent persistence of P648's right208 anchor6 salt208 branch.",
            "A below-rho direct replay is a relation-event metric, not a complete faster-than-rho ECDLP algorithm.",
            "Above-rho substitution recovery is bounded relation-bank evidence, not arbitrary target descent.",
            "Promotion still requires source-generation charge, sparse linear algebra, target descent, and individual-log accounting.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claim_status": claim_status, **raw_summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
