#!/usr/bin/env python3
"""P655 adjacent validation for P654 salt206 post-quiet burst surfaces."""

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
    / "low_term_total2_fixed_leaf_shared_product_gate_p655_order9887_salt206_postquiet_burst_22304_22316_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p655_salt206_postquiet_burst_source_22304_22316_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p655_salt206_postquiet_burst_scout_22304_22316_probe.json"


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


def salt206_salt207_all_anchor(f: dict[str, Any]) -> bool:
    return standard_row_pair(f, 206, 207)


def salt206_salt208_all_anchor(f: dict[str, Any]) -> bool:
    return standard_row_pair(f, 206, 208)


def salt206_right207_right208_union(f: dict[str, Any]) -> bool:
    return salt206_salt207_all_anchor(f) or salt206_salt208_all_anchor(f)


def right208_anchor13_salt206_salt208(f: dict[str, Any]) -> bool:
    return salt206_salt208_all_anchor(f) and f.get("right_anchor") == 13


def phase1_right208_anchor13_salt206_salt208(f: dict[str, Any]) -> bool:
    return right208_anchor13_salt206_salt208(f) and f.get("transfer_mod12") == 1


def mod7_2_right208_anchor13_salt206_salt208(f: dict[str, Any]) -> bool:
    return right208_anchor13_salt206_salt208(f) and f.get("transfer_mod7") == 2


def phase1_mod7_2_right208_anchor13_salt206_salt208(f: dict[str, Any]) -> bool:
    return (
        right208_anchor13_salt206_salt208(f)
        and f.get("transfer_mod12") == 1
        and f.get("transfer_mod7") == 2
    )


def phase1_salt206_salt208_all_anchor(f: dict[str, Any]) -> bool:
    return salt206_salt208_all_anchor(f) and f.get("transfer_mod12") == 1


def mod7_2_salt206_salt208_all_anchor(f: dict[str, Any]) -> bool:
    return salt206_salt208_all_anchor(f) and f.get("transfer_mod7") == 2


def phase1_salt206_right207_right208_union(f: dict[str, Any]) -> bool:
    return salt206_right207_right208_union(f) and f.get("transfer_mod12") == 1


def mod7_2_salt206_right207_right208_union(f: dict[str, Any]) -> bool:
    return salt206_right207_right208_union(f) and f.get("transfer_mod7") == 2


def phase6_salt206_salt207_all_anchor(f: dict[str, Any]) -> bool:
    return salt206_salt207_all_anchor(f) and f.get("transfer_mod12") == 6


def phase6_salt206_salt208_all_anchor(f: dict[str, Any]) -> bool:
    return salt206_salt208_all_anchor(f) and f.get("transfer_mod12") == 6


def phase6_salt206_right207_right208_union(f: dict[str, Any]) -> bool:
    return salt206_right207_right208_union(f) and f.get("transfer_mod12") == 6


def mod7_0_salt206_right207_right208_union(f: dict[str, Any]) -> bool:
    return salt206_right207_right208_union(f) and f.get("transfer_mod7") == 0


def phase6_mod7_0_salt206_right207_right208_union(f: dict[str, Any]) -> bool:
    return (
        salt206_right207_right208_union(f)
        and f.get("transfer_mod12") == 6
        and f.get("transfer_mod7") == 0
    )


def right206_anchor9_salt204_salt206(f: dict[str, Any]) -> bool:
    return standard_row_pair(f, 204, 206) and f.get("right_anchor") == 9


def phase1_right206_anchor9_salt204_salt206(f: dict[str, Any]) -> bool:
    return right206_anchor9_salt204_salt206(f) and f.get("transfer_mod12") == 1


def phase6_right206_anchor9_salt204_salt206(f: dict[str, Any]) -> bool:
    return right206_anchor9_salt204_salt206(f) and f.get("transfer_mod12") == 6


def mod7_2_right206_anchor9_salt204_salt206(f: dict[str, Any]) -> bool:
    return right206_anchor9_salt204_salt206(f) and f.get("transfer_mod7") == 2


def mod7_0_right206_anchor9_salt204_salt206(f: dict[str, Any]) -> bool:
    return right206_anchor9_salt204_salt206(f) and f.get("transfer_mod7") == 0


def phase1_mod7_2_right206_anchor9_salt204_salt206(f: dict[str, Any]) -> bool:
    return (
        right206_anchor9_salt204_salt206(f)
        and f.get("transfer_mod12") == 1
        and f.get("transfer_mod7") == 2
    )


def phase6_mod7_0_right206_anchor9_salt204_salt206(f: dict[str, Any]) -> bool:
    return (
        right206_anchor9_salt204_salt206(f)
        and f.get("transfer_mod12") == 6
        and f.get("transfer_mod7") == 0
    )


RULES: list[tuple[str, str, Callable[[dict[str, Any]], bool]]] = [
    (
        "p655_phase1_mod7_2_right208_anchor13_salt206_salt208",
        "P654 rank-3/unique-gain slice: phase1/mod7=2 right208 anchor13 salt206_salt208",
        phase1_mod7_2_right208_anchor13_salt206_salt208,
    ),
    (
        "p655_phase1_right208_anchor13_salt206_salt208",
        "P654 phase1 right208 anchor13 salt206_salt208 rank-slice control",
        phase1_right208_anchor13_salt206_salt208,
    ),
    (
        "p655_mod7_2_right208_anchor13_salt206_salt208",
        "P654 same-mod7=2 right208 anchor13 salt206_salt208 control",
        mod7_2_right208_anchor13_salt206_salt208,
    ),
    (
        "p655_all_phase_right208_anchor13_salt206_salt208",
        "P654 all-phase right208 anchor13 salt206_salt208 control",
        right208_anchor13_salt206_salt208,
    ),
    (
        "p655_phase1_salt206_salt208_all_anchor",
        "P654 phase1 salt206_salt208 all-anchor control",
        phase1_salt206_salt208_all_anchor,
    ),
    (
        "p655_mod7_2_salt206_salt208_all_anchor",
        "P654 same-mod7=2 salt206_salt208 all-anchor control",
        mod7_2_salt206_salt208_all_anchor,
    ),
    (
        "p655_phase1_salt206_right207_right208_union",
        "P654 phase1 salt206 union across right207 and right208",
        phase1_salt206_right207_right208_union,
    ),
    (
        "p655_mod7_2_salt206_right207_right208_union",
        "P654 same-mod7=2 salt206 union across right207 and right208",
        mod7_2_salt206_right207_right208_union,
    ),
    (
        "p655_phase6_mod7_0_salt206_right207_right208_union",
        "P654 phase6/mod7=0 salt206 union across right207 and right208",
        phase6_mod7_0_salt206_right207_right208_union,
    ),
    (
        "p655_phase6_salt206_salt207_all_anchor",
        "P654 phase6 salt206_salt207 all-anchor control",
        phase6_salt206_salt207_all_anchor,
    ),
    (
        "p655_phase6_salt206_salt208_all_anchor",
        "P654 phase6 salt206_salt208 all-anchor control",
        phase6_salt206_salt208_all_anchor,
    ),
    (
        "p655_phase6_salt206_right207_right208_union",
        "P654 phase6 salt206 union across right207 and right208",
        phase6_salt206_right207_right208_union,
    ),
    (
        "p655_mod7_0_salt206_right207_right208_union",
        "P654 same-mod7=0 salt206 union across right207 and right208",
        mod7_0_salt206_right207_right208_union,
    ),
    (
        "p655_broad_salt206_salt207_all_anchor",
        "P654 broad salt206_salt207 all-anchor control",
        salt206_salt207_all_anchor,
    ),
    (
        "p655_broad_salt206_salt208_all_anchor",
        "P654 broad salt206_salt208 all-anchor control",
        salt206_salt208_all_anchor,
    ),
    (
        "p655_broad_salt206_right207_right208_union",
        "P654 broad salt206 union across right207 and right208",
        salt206_right207_right208_union,
    ),
    (
        "p655_phase1_mod7_2_right206_anchor9_salt204_salt206",
        "P654 small right206 anchor9 salt204_salt206 phase1/mod7=2 recurrence control",
        phase1_mod7_2_right206_anchor9_salt204_salt206,
    ),
    (
        "p655_phase6_mod7_0_right206_anchor9_salt204_salt206",
        "P654 small right206 anchor9 salt204_salt206 phase6/mod7=0 recurrence control",
        phase6_mod7_0_right206_anchor9_salt204_salt206,
    ),
    (
        "p655_phase1_right206_anchor9_salt204_salt206",
        "P654 small right206 anchor9 salt204_salt206 phase1 recurrence control",
        phase1_right206_anchor9_salt204_salt206,
    ),
    (
        "p655_phase6_right206_anchor9_salt204_salt206",
        "P654 small right206 anchor9 salt204_salt206 phase6 recurrence control",
        phase6_right206_anchor9_salt204_salt206,
    ),
    (
        "p655_mod7_2_right206_anchor9_salt204_salt206",
        "P654 small right206 anchor9 salt204_salt206 same-mod7=2 recurrence control",
        mod7_2_right206_anchor9_salt204_salt206,
    ),
    (
        "p655_mod7_0_right206_anchor9_salt204_salt206",
        "P654 small right206 anchor9 salt204_salt206 same-mod7=0 recurrence control",
        mod7_0_right206_anchor9_salt204_salt206,
    ),
    (
        "p655_broad_right206_anchor9_salt204_salt206",
        "P654 small right206 anchor9 salt204_salt206 broad recurrence control",
        right206_anchor9_salt204_salt206,
    ),
]


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
        "rank3_mode_counts": dict(Counter(selector_mode(f) for f in rank3)),
        "rank3_mod7_counts": dict(Counter(str(f.get("transfer_mod7")) for f in rank3)),
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


def has_rank3_below(report: dict[str, Any] | None) -> bool:
    if not report:
        return False
    return bool(report["direct_below_rho_verified_count"] and report["rank3_direct_verified_count"])


def has_below(report: dict[str, Any] | None) -> bool:
    return bool(report and report["direct_below_rho_verified_count"])


def determine_claim(reports: list[dict[str, Any]], raw: dict[str, Any]) -> str:
    exact_anchor13 = report_named(reports, "p655_phase1_mod7_2_right208_anchor13_salt206_salt208")
    phase_anchor13 = report_named(reports, "p655_phase1_right208_anchor13_salt206_salt208")
    mod7_anchor13 = report_named(reports, "p655_mod7_2_right208_anchor13_salt206_salt208")
    phase1_salt208 = report_named(reports, "p655_phase1_salt206_salt208_all_anchor")
    mod7_2_salt208 = report_named(reports, "p655_mod7_2_salt206_salt208_all_anchor")
    phase6_union = report_named(reports, "p655_phase6_salt206_right207_right208_union")
    phase6_mod7_union = report_named(reports, "p655_phase6_mod7_0_salt206_right207_right208_union")
    broad_union = report_named(reports, "p655_broad_salt206_right207_right208_union")
    small_recurrence = report_named(reports, "p655_broad_right206_anchor9_salt204_salt206")

    if has_rank3_below(exact_anchor13):
        return "P655_PHASE1_MOD7_2_RIGHT208_ANCHOR13_SALT206_SALT208_RANK3_BELOW_RHO_PERSISTENCE"
    if has_below(exact_anchor13):
        return "P655_PHASE1_MOD7_2_RIGHT208_ANCHOR13_SALT206_SALT208_BELOW_RHO_PERSISTENCE"
    if has_rank3_below(phase_anchor13) or has_rank3_below(mod7_anchor13):
        return "P655_RIGHT208_ANCHOR13_SALT206_SALT208_RANK3_DRIFT"
    if has_below(phase_anchor13):
        return "P655_PHASE1_RIGHT208_ANCHOR13_SALT206_SALT208_BELOW_RHO_DRIFT"
    if has_below(mod7_anchor13):
        return "P655_MOD7_2_RIGHT208_ANCHOR13_SALT206_SALT208_BELOW_RHO_DRIFT"
    if has_below(phase1_salt208):
        return "P655_PHASE1_SALT206_SALT208_BELOW_RHO_DRIFT"
    if has_below(mod7_2_salt208):
        return "P655_MOD7_2_SALT206_SALT208_BELOW_RHO_DRIFT"
    if has_below(phase6_mod7_union):
        return "P655_PHASE6_MOD7_0_SALT206_UNION_BELOW_RHO_PERSISTENCE"
    if has_below(phase6_union):
        return "P655_PHASE6_SALT206_UNION_BELOW_RHO_DRIFT"
    if has_below(broad_union):
        return "P655_BROAD_SALT206_UNION_BELOW_RHO_DRIFT"
    if has_below(small_recurrence):
        return "P655_RIGHT206_ANCHOR9_SALT204_SALT206_RECURRENCE"
    if any(r["direct_below_rho_verified_count"] for r in reports):
        return "P655_REGISTERED_BELOW_RHO_POSITIVE"
    if any(r["rank3_direct_verified_count"] for r in reports):
        return "P655_REGISTERED_RANK_SURFACE_POSITIVE"
    if any(r["direct_verified_count"] for r in reports):
        return "P655_REGISTERED_ABOVE_RHO_POSITIVE"
    if raw["direct_verified_count"]:
        return "NEGATIVE_RESULT_P655_REGISTERED_CONTROLS_MISSED_NONQUIET_BLOCK"
    return "NEGATIVE_RESULT_P655_SALT206_POSTQUIET_ADJACENT_QUIET_BLOCK"


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
        "schema": "ecdlp.low_term_total2_p655_salt206_postquiet_burst_scout.v1",
        "created_at": utc_now(),
        "method": "p655_salt206_postquiet_burst_scout",
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
            "P655 tests adjacent persistence and public-feature separation for P654's salt206 burst.",
            "A below-rho direct replay is a relation-event metric, not a complete faster-than-rho ECDLP algorithm.",
            "Above-rho substitution recovery is bounded relation-bank evidence, not arbitrary target descent.",
            "Promotion still requires source-generation charge, sparse linear algebra, target descent, and individual-log accounting.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claim_status": claim_status, **raw_summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
