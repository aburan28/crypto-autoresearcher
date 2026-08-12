#!/usr/bin/env python3
"""P665 adjacent validation for the P663 phase0 salt204 drift."""

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
    / "low_term_total2_fixed_leaf_shared_product_gate_p665_order9887_phase0_salt204_drift_22382_22394_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p665_phase0_salt204_drift_source_22382_22394_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p665_phase0_salt204_drift_scout_22382_22394_probe.json"
PHASE0_ANCHORS = {3, 6, 7, 8, 9, 11, 12, 13}


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


def right206_salt204_salt206(f: dict[str, Any]) -> bool:
    return standard_row_pair(f, 204, 206)


def right208_salt204_salt208(f: dict[str, Any]) -> bool:
    return standard_row_pair(f, 204, 208)


def salt204_union(f: dict[str, Any]) -> bool:
    return right206_salt204_salt206(f) or right208_salt204_salt208(f)


def phase0_mod7_1_right206_salt204_salt206(f: dict[str, Any]) -> bool:
    return right206_salt204_salt206(f) and f.get("transfer_mod12") == 0 and f.get("transfer_mod7") == 1


def phase0_right206_salt204_salt206(f: dict[str, Any]) -> bool:
    return right206_salt204_salt206(f) and f.get("transfer_mod12") == 0


def mod7_1_right206_salt204_salt206(f: dict[str, Any]) -> bool:
    return right206_salt204_salt206(f) and f.get("transfer_mod7") == 1


def phase0_mod7_1_right208_salt204_salt208(f: dict[str, Any]) -> bool:
    return right208_salt204_salt208(f) and f.get("transfer_mod12") == 0 and f.get("transfer_mod7") == 1


def phase0_right208_salt204_salt208(f: dict[str, Any]) -> bool:
    return right208_salt204_salt208(f) and f.get("transfer_mod12") == 0


def mod7_1_right208_salt204_salt208(f: dict[str, Any]) -> bool:
    return right208_salt204_salt208(f) and f.get("transfer_mod7") == 1


def phase0_mod7_1_salt204_union(f: dict[str, Any]) -> bool:
    return salt204_union(f) and f.get("transfer_mod12") == 0 and f.get("transfer_mod7") == 1


def phase0_salt204_union(f: dict[str, Any]) -> bool:
    return salt204_union(f) and f.get("transfer_mod12") == 0


def mod7_1_salt204_union(f: dict[str, Any]) -> bool:
    return salt204_union(f) and f.get("transfer_mod7") == 1


def phase0_anchor_pred(anchor: int, salt_right: int) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        if salt_right == 206:
            base = right206_salt204_salt206(f)
        elif salt_right == 208:
            base = right208_salt204_salt208(f)
        else:
            base = False
        return base and f.get("right_anchor") == anchor and f.get("transfer_mod12") == 0

    return pred


def phase0_mod7_1_anchor_pred(anchor: int, salt_right: int) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return phase0_anchor_pred(anchor, salt_right)(f) and f.get("transfer_mod7") == 1

    return pred


RULES: list[tuple[str, str, Callable[[dict[str, Any]], bool]]] = [
    (
        "p665_phase0_mod7_1_right206_salt204_salt206",
        "P663 phase0/mod7=1 right206 salt204_salt206 below-rho surface",
        phase0_mod7_1_right206_salt204_salt206,
    ),
    (
        "p665_phase0_right206_salt204_salt206",
        "P663 phase0 right206 salt204_salt206 surface",
        phase0_right206_salt204_salt206,
    ),
    (
        "p665_mod7_1_right206_salt204_salt206",
        "P663 same-mod7=1 right206 salt204_salt206 surface",
        mod7_1_right206_salt204_salt206,
    ),
    (
        "p665_broad_right206_salt204_salt206",
        "P663 broad right206 salt204_salt206 control",
        right206_salt204_salt206,
    ),
    (
        "p665_phase0_mod7_1_right208_salt204_salt208",
        "P663 phase0/mod7=1 right208 salt204_salt208 below-rho surface",
        phase0_mod7_1_right208_salt204_salt208,
    ),
    (
        "p665_phase0_right208_salt204_salt208",
        "P663 phase0 right208 salt204_salt208 surface",
        phase0_right208_salt204_salt208,
    ),
    (
        "p665_mod7_1_right208_salt204_salt208",
        "P663 same-mod7=1 right208 salt204_salt208 surface",
        mod7_1_right208_salt204_salt208,
    ),
    (
        "p665_broad_right208_salt204_salt208",
        "P663 broad right208 salt204_salt208 control",
        right208_salt204_salt208,
    ),
    (
        "p665_phase0_mod7_1_salt204_union",
        "P663 phase0/mod7=1 salt204 union across right206 and right208",
        phase0_mod7_1_salt204_union,
    ),
    (
        "p665_phase0_salt204_union",
        "P663 phase0 salt204 union across right206 and right208",
        phase0_salt204_union,
    ),
    (
        "p665_mod7_1_salt204_union",
        "P663 same-mod7=1 salt204 union across right206 and right208",
        mod7_1_salt204_union,
    ),
    (
        "p665_broad_salt204_union",
        "P663 broad salt204 union across right206 and right208",
        salt204_union,
    ),
]

for anchor in sorted(PHASE0_ANCHORS):
    RULES.extend(
        [
            (
                f"p665_phase0_mod7_1_right206_anchor{anchor}_salt204_salt206",
                f"P663 phase0/mod7=1 right206 salt204_salt206 anchor {anchor} split",
                phase0_mod7_1_anchor_pred(anchor, 206),
            ),
            (
                f"p665_phase0_right206_anchor{anchor}_salt204_salt206",
                f"P663 phase0 right206 salt204_salt206 anchor {anchor} split",
                phase0_anchor_pred(anchor, 206),
            ),
            (
                f"p665_phase0_mod7_1_right208_anchor{anchor}_salt204_salt208",
                f"P663 phase0/mod7=1 right208 salt204_salt208 anchor {anchor} split",
                phase0_mod7_1_anchor_pred(anchor, 208),
            ),
            (
                f"p665_phase0_right208_anchor{anchor}_salt204_salt208",
                f"P663 phase0 right208 salt204_salt208 anchor {anchor} split",
                phase0_anchor_pred(anchor, 208),
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
    r206_exact = report_named(reports, "p665_phase0_mod7_1_right206_salt204_salt206")
    r208_exact = report_named(reports, "p665_phase0_mod7_1_right208_salt204_salt208")
    union_exact = report_named(reports, "p665_phase0_mod7_1_salt204_union")
    r206_phase = report_named(reports, "p665_phase0_right206_salt204_salt206")
    r208_phase = report_named(reports, "p665_phase0_right208_salt204_salt208")
    union_phase = report_named(reports, "p665_phase0_salt204_union")
    r206_broad = report_named(reports, "p665_broad_right206_salt204_salt206")
    r208_broad = report_named(reports, "p665_broad_right208_salt204_salt208")
    union_broad = report_named(reports, "p665_broad_salt204_union")

    if has_below(union_exact) and has_rank3(union_exact):
        return f"{claim_prefix}_PHASE0_MOD7_1_SALT204_UNION_BELOW_RHO_RANK3_PERSISTENCE"
    if has_below(union_exact):
        return f"{claim_prefix}_PHASE0_MOD7_1_SALT204_UNION_BELOW_RHO_PERSISTENCE"
    if has_below(r206_exact):
        return f"{claim_prefix}_PHASE0_MOD7_1_RIGHT206_SALT204_SALT206_BELOW_RHO_PERSISTENCE"
    if has_below(r208_exact):
        return f"{claim_prefix}_PHASE0_MOD7_1_RIGHT208_SALT204_SALT208_BELOW_RHO_PERSISTENCE"
    if has_rank3(union_exact):
        return f"{claim_prefix}_PHASE0_MOD7_1_SALT204_UNION_RANK_SURFACE_PERSISTENCE"
    if has_below(union_phase):
        return f"{claim_prefix}_PHASE0_SALT204_UNION_BELOW_RHO_DRIFT"
    if has_below(r206_phase):
        return f"{claim_prefix}_PHASE0_RIGHT206_SALT204_SALT206_BELOW_RHO_DRIFT"
    if has_below(r208_phase):
        return f"{claim_prefix}_PHASE0_RIGHT208_SALT204_SALT208_BELOW_RHO_DRIFT"
    if has_rank3(union_phase):
        return f"{claim_prefix}_PHASE0_SALT204_UNION_RANK_SURFACE_DRIFT"
    if has_below(union_broad):
        return f"{claim_prefix}_BROAD_SALT204_UNION_BELOW_RHO_DRIFT"
    if has_below(r206_broad):
        return f"{claim_prefix}_BROAD_RIGHT206_SALT204_SALT206_BELOW_RHO_DRIFT"
    if has_below(r208_broad):
        return f"{claim_prefix}_BROAD_RIGHT208_SALT204_SALT208_BELOW_RHO_DRIFT"
    if has_rank3(union_broad):
        return f"{claim_prefix}_BROAD_SALT204_UNION_RANK_SURFACE_DRIFT"
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
    parser.add_argument("--claim-prefix", default="P665")
    parser.add_argument("--quiet-claim", default="NEGATIVE_RESULT_P665_PHASE0_SALT204_ADJACENT_QUIET_BLOCK")
    args = parser.parse_args()

    gate = json.loads(Path(args.gate).read_text())
    features = [p643.feature(case) for case in gate.get("cases", [])]
    raw_summary = summarize_cases(features)
    reports = [rule_report(name, desc, pred, features, raw_summary) for name, desc, pred in RULES]
    claim_status = determine_claim(reports, raw_summary, args.claim_prefix, args.quiet_claim)

    payload = {
        "schema": "ecdlp.low_term_total2_p665_phase0_salt204_drift_scout.v1",
        "created_at": utc_now(),
        "method": "p665_phase0_salt204_drift_scout",
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
            "P665 tests adjacent persistence and public-feature drift for P663's phase0 salt204 surfaces.",
            "A below-rho direct replay is a relation-event metric, not a complete faster-than-rho ECDLP algorithm.",
            "Above-rho substitution recovery is bounded relation-bank evidence, not arbitrary target descent.",
            "Promotion still requires source-generation charge, sparse linear algebra, target descent, and individual-log accounting.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claim_status": claim_status, **raw_summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
