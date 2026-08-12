#!/usr/bin/env python3
"""P653 shifted scan for P651 phase5 right206 salt204_salt206 burst."""

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
    / "low_term_total2_fixed_leaf_shared_product_gate_p653_order9887_phase5_right206_salt204_salt206_22278_22290_density_gate_probe.json"
)
DEFAULT_SOURCE = (
    STATE_DIR / "low_term_total2_order9887_p653_phase5_right206_salt204_salt206_source_22278_22290_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_p653_phase5_right206_salt204_salt206_scout_22278_22290_probe.json"

RANK2_BELOW_ANCHORS = {3, 6, 7, 8, 11}
RANK3_ANCHORS = {9, 12, 13}
RANK3_BELOW_ANCHORS = {12}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def selector_mode(f: dict[str, Any]) -> str:
    selector = str(f.get("selector") or "")
    return selector.split("__", 1)[0]


def right206_salt204_salt206_all_anchor(f: dict[str, Any]) -> bool:
    return (
        p643.standard_leaf(f)
        and f.get("salt_left") == 204
        and f.get("salt_right") == 206
        and f.get("right_anchor") in p643.ANCHORS
    )


def phase5_right206_salt204_salt206_all_anchor(f: dict[str, Any]) -> bool:
    return right206_salt204_salt206_all_anchor(f) and f.get("transfer_mod12") == 5


def mod7_5_right206_salt204_salt206_all_anchor(f: dict[str, Any]) -> bool:
    return right206_salt204_salt206_all_anchor(f) and f.get("transfer_mod7") == 5


def phase5_mod7_5_right206_salt204_salt206_all_anchor(f: dict[str, Any]) -> bool:
    return (
        right206_salt204_salt206_all_anchor(f)
        and f.get("transfer_mod12") == 5
        and f.get("transfer_mod7") == 5
    )


def anchor_split(anchor: int) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return right206_salt204_salt206_all_anchor(f) and f.get("right_anchor") == anchor

    return pred


def phase5_anchor_split(anchor: int) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return phase5_right206_salt204_salt206_all_anchor(f) and f.get("right_anchor") == anchor

    return pred


def anchor_set_pred(anchors: set[int]) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return right206_salt204_salt206_all_anchor(f) and f.get("right_anchor") in anchors

    return pred


def phase5_anchor_set_pred(anchors: set[int]) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return phase5_right206_salt204_salt206_all_anchor(f) and f.get("right_anchor") in anchors

    return pred


RULES: list[tuple[str, str, Callable[[dict[str, Any]], bool]]] = [
    (
        "p653_phase5_mod7_5_right206_salt204_salt206_all_anchor",
        "P651 exact phase/mod7 right206 salt204_salt206 all-anchor shifted control",
        phase5_mod7_5_right206_salt204_salt206_all_anchor,
    ),
    (
        "p653_phase5_right206_salt204_salt206_all_anchor",
        "P651 phase5 right206 salt204_salt206 all-anchor shifted control",
        phase5_right206_salt204_salt206_all_anchor,
    ),
    (
        "p653_mod7_5_right206_salt204_salt206_all_anchor",
        "P651 same-mod7=5 right206 salt204_salt206 all-anchor shifted control",
        mod7_5_right206_salt204_salt206_all_anchor,
    ),
    (
        "p653_broad_right206_salt204_salt206_all_anchor",
        "P651 broad right206 salt204_salt206 all-anchor control",
        right206_salt204_salt206_all_anchor,
    ),
    (
        "p653_phase5_rank2_below_anchor_set",
        "P651 phase5 public anchor set that was rank-2 below-rho: 3,6,7,8,11",
        phase5_anchor_set_pred(RANK2_BELOW_ANCHORS),
    ),
    (
        "p653_phase5_rank3_anchor_set",
        "P651 phase5 public rank-3 anchor set: 9,12,13",
        phase5_anchor_set_pred(RANK3_ANCHORS),
    ),
    (
        "p653_phase5_rank3_below_anchor12",
        "P651 phase5 public anchor 12 was rank-3 below-rho",
        phase5_anchor_set_pred(RANK3_BELOW_ANCHORS),
    ),
    (
        "p653_all_phase_rank3_anchor_set",
        "P651 all-phase public rank-3 anchor set: 9,12,13",
        anchor_set_pred(RANK3_ANCHORS),
    ),
]

for anchor in (3, 6, 7, 8, 9, 11, 12, 13):
    RULES.append(
        (
            f"p653_phase5_anchor{anchor}_right206_salt204_salt206",
            f"P651 phase5 right206 salt204_salt206 anchor {anchor} split",
            phase5_anchor_split(anchor),
        )
    )
    RULES.append(
        (
            f"p653_all_phase_anchor{anchor}_right206_salt204_salt206",
            f"P651 all-phase right206 salt204_salt206 anchor {anchor} split",
            anchor_split(anchor),
        )
    )


def summarize_cases(features: list[dict[str, Any]]) -> dict[str, Any]:
    return p643.summarize_cases(features)


def public_feature_counts(features: list[dict[str, Any]]) -> dict[str, Any]:
    verified = [f for f in features if f.get("direct_verified")]
    below = [f for f in features if f.get("direct_below_rho_verified")]
    rank3 = [f for f in verified if int(f.get("rank") or 0) >= 3]
    return {
        "below_anchor_counts": dict(Counter(str(f.get("right_anchor")) for f in below)),
        "below_mode_counts": dict(Counter(selector_mode(f) for f in below)),
        "below_phase_counts": dict(Counter(str(f.get("transfer_mod12")) for f in below)),
        "rank3_anchor_counts": dict(Counter(str(f.get("right_anchor")) for f in rank3)),
        "rank3_mode_counts": dict(Counter(selector_mode(f) for f in rank3)),
        "rank3_phase_counts": dict(Counter(str(f.get("transfer_mod12")) for f in rank3)),
        "verified_anchor_counts": dict(Counter(str(f.get("right_anchor")) for f in verified)),
        "verified_mode_counts": dict(Counter(selector_mode(f) for f in verified)),
    }


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
        "mode_counts": dict(Counter(selector_mode(f) for f in selected)),
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
    exact = report_named(reports, "p653_phase5_mod7_5_right206_salt204_salt206_all_anchor")
    phase = report_named(reports, "p653_phase5_right206_salt204_salt206_all_anchor")
    mod7 = report_named(reports, "p653_mod7_5_right206_salt204_salt206_all_anchor")
    rank3_phase = report_named(reports, "p653_phase5_rank3_anchor_set")
    broad = report_named(reports, "p653_broad_right206_salt204_salt206_all_anchor")
    if exact and exact["direct_below_rho_verified_count"]:
        return "P653_PHASE5_MOD7_5_RIGHT206_SALT204_SALT206_BELOW_RHO_PERSISTENCE"
    if phase and phase["direct_below_rho_verified_count"]:
        return "P653_PHASE5_RIGHT206_SALT204_SALT206_BELOW_RHO_DRIFT"
    if mod7 and mod7["direct_below_rho_verified_count"]:
        return "P653_MOD7_5_RIGHT206_SALT204_SALT206_BELOW_RHO_DRIFT"
    if rank3_phase and rank3_phase["rank3_direct_verified_count"]:
        return "P653_PHASE5_RANK3_ANCHOR_SURFACE_POSITIVE"
    if broad and broad["direct_below_rho_verified_count"]:
        return "P653_BROAD_RIGHT206_SALT204_SALT206_BELOW_RHO_DRIFT"
    if any(r["direct_below_rho_verified_count"] for r in reports):
        return "P653_REGISTERED_BELOW_RHO_POSITIVE"
    if any(r["rank3_direct_verified_count"] for r in reports):
        return "P653_REGISTERED_RANK_SURFACE_POSITIVE"
    if any(r["direct_verified_count"] for r in reports):
        return "P653_REGISTERED_ABOVE_RHO_POSITIVE"
    if raw["direct_verified_count"]:
        return "NEGATIVE_RESULT_P653_REGISTERED_CONTROLS_MISSED_NONQUIET_BLOCK"
    return "NEGATIVE_RESULT_P653_PHASE5_RIGHT206_SHIFTED_QUIET_BLOCK"


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
        "schema": "ecdlp.low_term_total2_p653_phase5_right206_salt204_salt206_scout.v1",
        "created_at": utc_now(),
        "method": "p653_phase5_right206_salt204_salt206_scout",
        "claim_status": claim_status,
        "artifacts": {"source": str(args.source), "gate": str(args.gate)},
        "summary": {
            "claim_status": claim_status,
            "validation_dataset": raw_summary,
            "public_feature_counts": public_feature_counts(features),
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
            "P653 tests shifted persistence and public-feature separation for P651's phase5 right206 burst.",
            "A below-rho direct replay is a relation-event metric, not a complete faster-than-rho ECDLP algorithm.",
            "Above-rho substitution recovery is bounded relation-bank evidence, not arbitrary target descent.",
            "Promotion still requires source-generation charge, sparse linear algebra, target descent, and individual-log accounting.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claim_status": claim_status, **raw_summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
