#!/usr/bin/env python3
"""P663 adjacent validation for P661 phase2/phase6 drift surfaces."""

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
    / "low_term_total2_fixed_leaf_shared_product_gate_p663_order9887_p661_drift_surfaces_22369_22381_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p663_p661_drift_surfaces_source_22369_22381_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p663_p661_drift_surfaces_scout_22369_22381_probe.json"
PHASE2_ANCHORS = {3, 6, 7, 8, 9, 11, 12, 13}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def selector_mode(f: dict[str, Any]) -> str:
    selector = str(f.get("selector") or "")
    return selector.split("__", 1)[0]


def ops_bucket(f: dict[str, Any]) -> str:
    value = f.get("direct_ops_over_rho")
    if value is None:
        return "none"
    return f"{float(value):.3f}"


def standard_row_pair(f: dict[str, Any], salt_left: int, salt_right: int) -> bool:
    return (
        p643.standard_leaf(f)
        and f.get("salt_left") == salt_left
        and f.get("salt_right") == salt_right
        and f.get("right_anchor") in p643.ANCHORS
    )


def right207_salt203_salt207(f: dict[str, Any]) -> bool:
    return standard_row_pair(f, 203, 207)


def right208_salt203_salt208(f: dict[str, Any]) -> bool:
    return standard_row_pair(f, 203, 208)


def salt203_union(f: dict[str, Any]) -> bool:
    return right207_salt203_salt207(f) or right208_salt203_salt208(f)


def right206_salt204_salt206(f: dict[str, Any]) -> bool:
    return standard_row_pair(f, 204, 206)


def right206_anchor11_salt204_salt206(f: dict[str, Any]) -> bool:
    return right206_salt204_salt206(f) and f.get("right_anchor") == 11


def phase2_mod7_0_right207_salt203_salt207(f: dict[str, Any]) -> bool:
    return right207_salt203_salt207(f) and f.get("transfer_mod12") == 2 and f.get("transfer_mod7") == 0


def phase2_right207_salt203_salt207(f: dict[str, Any]) -> bool:
    return right207_salt203_salt207(f) and f.get("transfer_mod12") == 2


def mod7_0_right207_salt203_salt207(f: dict[str, Any]) -> bool:
    return right207_salt203_salt207(f) and f.get("transfer_mod7") == 0


def phase2_mod7_0_right208_salt203_salt208(f: dict[str, Any]) -> bool:
    return right208_salt203_salt208(f) and f.get("transfer_mod12") == 2 and f.get("transfer_mod7") == 0


def phase2_right208_salt203_salt208(f: dict[str, Any]) -> bool:
    return right208_salt203_salt208(f) and f.get("transfer_mod12") == 2


def mod7_0_right208_salt203_salt208(f: dict[str, Any]) -> bool:
    return right208_salt203_salt208(f) and f.get("transfer_mod7") == 0


def phase2_mod7_0_salt203_union(f: dict[str, Any]) -> bool:
    return salt203_union(f) and f.get("transfer_mod12") == 2 and f.get("transfer_mod7") == 0


def phase2_salt203_union(f: dict[str, Any]) -> bool:
    return salt203_union(f) and f.get("transfer_mod12") == 2


def mod7_0_salt203_union(f: dict[str, Any]) -> bool:
    return salt203_union(f) and f.get("transfer_mod7") == 0


def phase6_mod7_4_right206_anchor11_salt204_salt206(f: dict[str, Any]) -> bool:
    return right206_anchor11_salt204_salt206(f) and f.get("transfer_mod12") == 6 and f.get("transfer_mod7") == 4


def phase6_right206_anchor11_salt204_salt206(f: dict[str, Any]) -> bool:
    return right206_anchor11_salt204_salt206(f) and f.get("transfer_mod12") == 6


def mod7_4_right206_anchor11_salt204_salt206(f: dict[str, Any]) -> bool:
    return right206_anchor11_salt204_salt206(f) and f.get("transfer_mod7") == 4


def phase6_right206_salt204_salt206(f: dict[str, Any]) -> bool:
    return right206_salt204_salt206(f) and f.get("transfer_mod12") == 6


def mod7_4_right206_salt204_salt206(f: dict[str, Any]) -> bool:
    return right206_salt204_salt206(f) and f.get("transfer_mod7") == 4


def phase2_anchor_pred(anchor: int, salt_right: int) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        if salt_right == 207:
            base = right207_salt203_salt207(f)
        elif salt_right == 208:
            base = right208_salt203_salt208(f)
        else:
            base = False
        return base and f.get("right_anchor") == anchor and f.get("transfer_mod12") == 2

    return pred


def phase2_mod7_0_anchor_pred(anchor: int, salt_right: int) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return phase2_anchor_pred(anchor, salt_right)(f) and f.get("transfer_mod7") == 0

    return pred


RULES: list[tuple[str, str, Callable[[dict[str, Any]], bool]]] = [
    (
        "p663_phase2_mod7_0_right207_salt203_salt207",
        "P661 phase2/mod7=0 right207 salt203_salt207 rank surface",
        phase2_mod7_0_right207_salt203_salt207,
    ),
    (
        "p663_phase2_right207_salt203_salt207",
        "P661 phase2 right207 salt203_salt207 rank surface",
        phase2_right207_salt203_salt207,
    ),
    (
        "p663_mod7_0_right207_salt203_salt207",
        "P661 same-mod7=0 right207 salt203_salt207 rank surface",
        mod7_0_right207_salt203_salt207,
    ),
    (
        "p663_broad_right207_salt203_salt207",
        "P661 broad right207 salt203_salt207 control",
        right207_salt203_salt207,
    ),
    (
        "p663_phase2_mod7_0_right208_salt203_salt208",
        "P661 phase2/mod7=0 right208 salt203_salt208 below-rho surface",
        phase2_mod7_0_right208_salt203_salt208,
    ),
    (
        "p663_phase2_right208_salt203_salt208",
        "P661 phase2 right208 salt203_salt208 below-rho surface",
        phase2_right208_salt203_salt208,
    ),
    (
        "p663_mod7_0_right208_salt203_salt208",
        "P661 same-mod7=0 right208 salt203_salt208 below-rho surface",
        mod7_0_right208_salt203_salt208,
    ),
    (
        "p663_broad_right208_salt203_salt208",
        "P661 broad right208 salt203_salt208 control",
        right208_salt203_salt208,
    ),
    (
        "p663_phase2_mod7_0_salt203_union",
        "P661 phase2/mod7=0 salt203 union across right207 and right208",
        phase2_mod7_0_salt203_union,
    ),
    (
        "p663_phase2_salt203_union",
        "P661 phase2 salt203 union across right207 and right208",
        phase2_salt203_union,
    ),
    (
        "p663_mod7_0_salt203_union",
        "P661 same-mod7=0 salt203 union across right207 and right208",
        mod7_0_salt203_union,
    ),
    (
        "p663_phase6_mod7_4_right206_anchor11_salt204_salt206",
        "P661 phase6/mod7=4 right206 anchor11 salt204_salt206 below-rho surface",
        phase6_mod7_4_right206_anchor11_salt204_salt206,
    ),
    (
        "p663_phase6_right206_anchor11_salt204_salt206",
        "P661 phase6 right206 anchor11 salt204_salt206 surface",
        phase6_right206_anchor11_salt204_salt206,
    ),
    (
        "p663_mod7_4_right206_anchor11_salt204_salt206",
        "P661 same-mod7=4 right206 anchor11 salt204_salt206 surface",
        mod7_4_right206_anchor11_salt204_salt206,
    ),
    (
        "p663_phase6_right206_salt204_salt206",
        "P661 phase6 right206 salt204_salt206 broad control",
        phase6_right206_salt204_salt206,
    ),
    (
        "p663_mod7_4_right206_salt204_salt206",
        "P661 same-mod7=4 right206 salt204_salt206 broad control",
        mod7_4_right206_salt204_salt206,
    ),
    (
        "p663_broad_right206_salt204_salt206",
        "P661 broad right206 salt204_salt206 control",
        right206_salt204_salt206,
    ),
]

for anchor in sorted(PHASE2_ANCHORS):
    RULES.extend(
        [
            (
                f"p663_phase2_mod7_0_right207_anchor{anchor}_salt203_salt207",
                f"P661 phase2/mod7=0 right207 salt203_salt207 anchor {anchor} split",
                phase2_mod7_0_anchor_pred(anchor, 207),
            ),
            (
                f"p663_phase2_right207_anchor{anchor}_salt203_salt207",
                f"P661 phase2 right207 salt203_salt207 anchor {anchor} split",
                phase2_anchor_pred(anchor, 207),
            ),
            (
                f"p663_phase2_mod7_0_right208_anchor{anchor}_salt203_salt208",
                f"P661 phase2/mod7=0 right208 salt203_salt208 anchor {anchor} split",
                phase2_mod7_0_anchor_pred(anchor, 208),
            ),
            (
                f"p663_phase2_right208_anchor{anchor}_salt203_salt208",
                f"P661 phase2 right208 salt203_salt208 anchor {anchor} split",
                phase2_anchor_pred(anchor, 208),
            ),
        ]
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
        "below_mod7_counts": dict(Counter(str(f.get("transfer_mod7")) for f in below)),
        "below_ops_over_rho_counts": dict(Counter(ops_bucket(f) for f in below)),
        "below_phase_counts": dict(Counter(str(f.get("transfer_mod12")) for f in below)),
        "below_row_pair_counts": dict(Counter(str(f.get("row_pair")) for f in below)),
        "rank3_anchor_counts": dict(Counter(str(f.get("right_anchor")) for f in rank3)),
        "rank3_feature_counts": dict(Counter(p643.feature_id(f) for f in rank3)),
        "rank3_mod7_counts": dict(Counter(str(f.get("transfer_mod7")) for f in rank3)),
        "rank3_mode_counts": dict(Counter(selector_mode(f) for f in rank3)),
        "rank3_ops_over_rho_counts": dict(Counter(ops_bucket(f) for f in rank3)),
        "rank3_phase_counts": dict(Counter(str(f.get("transfer_mod12")) for f in rank3)),
        "rank3_row_pair_counts": dict(Counter(str(f.get("row_pair")) for f in rank3)),
        "verified_anchor_counts": dict(Counter(str(f.get("right_anchor")) for f in verified)),
        "verified_mode_counts": dict(Counter(selector_mode(f) for f in verified)),
        "verified_mod7_counts": dict(Counter(str(f.get("transfer_mod7")) for f in verified)),
        "verified_ops_over_rho_counts": dict(Counter(ops_bucket(f) for f in verified)),
        "verified_phase_counts": dict(Counter(str(f.get("transfer_mod12")) for f in verified)),
        "verified_row_pair_counts": dict(Counter(str(f.get("row_pair")) for f in verified)),
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
        "row_pair_counts": dict(Counter(str(f["row_pair"]) for f in selected)),
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


def has_below(report: dict[str, Any] | None) -> bool:
    return bool(report and report["direct_below_rho_verified_count"])


def has_rank3(report: dict[str, Any] | None) -> bool:
    return bool(report and report["rank3_direct_verified_count"])


def determine_claim(
    reports: list[dict[str, Any]],
    raw: dict[str, Any],
    claim_prefix: str,
    quiet_claim: str,
) -> str:
    r207_exact = report_named(reports, "p663_phase2_mod7_0_right207_salt203_salt207")
    r208_exact = report_named(reports, "p663_phase2_mod7_0_right208_salt203_salt208")
    union_exact = report_named(reports, "p663_phase2_mod7_0_salt203_union")
    r206_exact = report_named(reports, "p663_phase6_mod7_4_right206_anchor11_salt204_salt206")
    r207_phase = report_named(reports, "p663_phase2_right207_salt203_salt207")
    r208_phase = report_named(reports, "p663_phase2_right208_salt203_salt208")
    r206_phase = report_named(reports, "p663_phase6_right206_anchor11_salt204_salt206")
    r207_broad = report_named(reports, "p663_broad_right207_salt203_salt207")
    r208_broad = report_named(reports, "p663_broad_right208_salt203_salt208")
    r206_broad = report_named(reports, "p663_broad_right206_salt204_salt206")

    if has_below(union_exact) and has_rank3(union_exact):
        return f"{claim_prefix}_PHASE2_MOD7_0_SALT203_UNION_BELOW_RHO_RANK3_PERSISTENCE"
    if has_below(r208_exact):
        return f"{claim_prefix}_PHASE2_MOD7_0_RIGHT208_SALT203_SALT208_BELOW_RHO_PERSISTENCE"
    if has_rank3(r207_exact):
        return f"{claim_prefix}_PHASE2_MOD7_0_RIGHT207_SALT203_SALT207_RANK_SURFACE_PERSISTENCE"
    if has_below(r207_exact):
        return f"{claim_prefix}_PHASE2_MOD7_0_RIGHT207_SALT203_SALT207_BELOW_RHO_PERSISTENCE"
    if has_below(r206_exact):
        return f"{claim_prefix}_PHASE6_MOD7_4_RIGHT206_ANCHOR11_SALT204_SALT206_BELOW_RHO_PERSISTENCE"
    if has_below(r208_phase):
        return f"{claim_prefix}_PHASE2_RIGHT208_SALT203_SALT208_BELOW_RHO_DRIFT"
    if has_rank3(r207_phase):
        return f"{claim_prefix}_PHASE2_RIGHT207_SALT203_SALT207_RANK_SURFACE_DRIFT"
    if has_below(r207_phase):
        return f"{claim_prefix}_PHASE2_RIGHT207_SALT203_SALT207_BELOW_RHO_DRIFT"
    if has_below(r206_phase):
        return f"{claim_prefix}_PHASE6_RIGHT206_ANCHOR11_SALT204_SALT206_BELOW_RHO_DRIFT"
    if has_rank3(r207_broad):
        return f"{claim_prefix}_BROAD_RIGHT207_SALT203_SALT207_RANK_SURFACE_DRIFT"
    if has_below(r207_broad):
        return f"{claim_prefix}_BROAD_RIGHT207_SALT203_SALT207_BELOW_RHO_DRIFT"
    if has_below(r208_broad):
        return f"{claim_prefix}_BROAD_RIGHT208_SALT203_SALT208_BELOW_RHO_DRIFT"
    if has_below(r206_broad):
        return f"{claim_prefix}_BROAD_RIGHT206_SALT204_SALT206_BELOW_RHO_DRIFT"
    if any(r["direct_below_rho_verified_count"] for r in reports):
        return f"{claim_prefix}_REGISTERED_BELOW_RHO_POSITIVE"
    if any(r["rank3_direct_verified_count"] for r in reports):
        return f"{claim_prefix}_REGISTERED_RANK_SURFACE_POSITIVE"
    if any(r["direct_verified_count"] for r in reports):
        return f"{claim_prefix}_REGISTERED_ABOVE_RHO_POSITIVE"
    if raw["direct_verified_count"]:
        return f"NEGATIVE_RESULT_{claim_prefix}_REGISTERED_CONTROLS_MISSED_NONQUIET_BLOCK"
    return quiet_claim


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", default=str(DEFAULT_GATE))
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--claim-prefix", default="P663")
    parser.add_argument("--quiet-claim", default="NEGATIVE_RESULT_P663_P661_DRIFT_SURFACES_ADJACENT_QUIET_BLOCK")
    args = parser.parse_args()

    gate = json.loads(Path(args.gate).read_text())
    features = [p643.feature(case) for case in gate.get("cases", [])]
    raw_summary = summarize_cases(features)
    reports = [rule_report(name, desc, pred, features, raw_summary) for name, desc, pred in RULES]
    claim_status = determine_claim(reports, raw_summary, args.claim_prefix, args.quiet_claim)

    payload = {
        "schema": "ecdlp.low_term_total2_p663_p661_drift_surfaces_scout.v1",
        "created_at": utc_now(),
        "method": "p663_p661_drift_surfaces_scout",
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
            "P663 tests adjacent persistence and public-feature drift for P661's phase2/phase6 surfaces.",
            "A below-rho direct replay is a relation-event metric, not a complete faster-than-rho ECDLP algorithm.",
            "Above-rho substitution recovery is bounded relation-bank evidence, not arbitrary target descent.",
            "Promotion still requires source-generation charge, sparse linear algebra, target descent, and individual-log accounting.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claim_status": claim_status, **raw_summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
