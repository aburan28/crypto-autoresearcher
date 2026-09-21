#!/usr/bin/env python3
"""P661 adjacent validation for the P659 right207/salt207 branch."""

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
    / "low_term_total2_fixed_leaf_shared_product_gate_p661_order9887_right207_salt207_p659_branch_22356_22368_density_gate_probe.json"
)
DEFAULT_SOURCE = (
    STATE_DIR / "low_term_total2_order9887_p661_right207_salt207_p659_branch_source_22356_22368_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_p661_right207_salt207_p659_branch_scout_22356_22368_probe.json"

SALT207_LEFTS = {203, 205, 206}
PHASE8_ANCHORS = {3, 6, 7, 8, 9, 11, 12, 13}


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


def right207_salt207_family(f: dict[str, Any]) -> bool:
    return (
        p643.standard_leaf(f)
        and f.get("salt_left") in SALT207_LEFTS
        and f.get("salt_right") == 207
        and f.get("right_anchor") in p643.ANCHORS
    )


def right207_anchor13_salt207_family(f: dict[str, Any]) -> bool:
    return right207_salt207_family(f) and f.get("right_anchor") == 13


def phase8_mod7_1_right207_salt207(f: dict[str, Any]) -> bool:
    return right207_salt207_family(f) and f.get("transfer_mod12") == 8 and f.get("transfer_mod7") == 1


def phase8_right207_salt207(f: dict[str, Any]) -> bool:
    return right207_salt207_family(f) and f.get("transfer_mod12") == 8


def mod7_1_right207_salt207(f: dict[str, Any]) -> bool:
    return right207_salt207_family(f) and f.get("transfer_mod7") == 1


def phase8_anchor_set_right207_salt207(f: dict[str, Any]) -> bool:
    return phase8_right207_salt207(f) and f.get("right_anchor") in PHASE8_ANCHORS


def phase3_mod7_3_right207_anchor13_salt207(f: dict[str, Any]) -> bool:
    return right207_anchor13_salt207_family(f) and f.get("transfer_mod12") == 3 and f.get("transfer_mod7") == 3


def phase3_right207_anchor13_salt207(f: dict[str, Any]) -> bool:
    return right207_anchor13_salt207_family(f) and f.get("transfer_mod12") == 3


def mod7_3_right207_anchor13_salt207(f: dict[str, Any]) -> bool:
    return right207_anchor13_salt207_family(f) and f.get("transfer_mod7") == 3


def row_pair_pred(salt_left: int) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return standard_row_pair(f, salt_left, 207)

    return pred


def phase8_row_pair_pred(salt_left: int) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return standard_row_pair(f, salt_left, 207) and f.get("transfer_mod12") == 8

    return pred


def phase8_mod7_1_row_pair_pred(salt_left: int) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return (
            standard_row_pair(f, salt_left, 207)
            and f.get("transfer_mod12") == 8
            and f.get("transfer_mod7") == 1
        )

    return pred


def phase3_anchor13_row_pair_pred(salt_left: int) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return (
            standard_row_pair(f, salt_left, 207)
            and f.get("right_anchor") == 13
            and f.get("transfer_mod12") == 3
        )

    return pred


def phase3_mod7_3_anchor13_row_pair_pred(salt_left: int) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return (
            standard_row_pair(f, salt_left, 207)
            and f.get("right_anchor") == 13
            and f.get("transfer_mod12") == 3
            and f.get("transfer_mod7") == 3
        )

    return pred


def phase8_anchor_pred(anchor: int) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return phase8_right207_salt207(f) and f.get("right_anchor") == anchor

    return pred


RULES: list[tuple[str, str, Callable[[dict[str, Any]], bool]]] = [
    (
        "p661_phase8_mod7_1_right207_salt207",
        "P659 phase8/mod7=1 right207 salt207 branch",
        phase8_mod7_1_right207_salt207,
    ),
    (
        "p661_phase8_right207_salt207",
        "P659 phase8 right207 salt207 branch",
        phase8_right207_salt207,
    ),
    (
        "p661_mod7_1_right207_salt207",
        "P659 same-mod7=1 right207 salt207 branch",
        mod7_1_right207_salt207,
    ),
    (
        "p661_phase8_anchor_set_right207_salt207",
        "P659 phase8 right207 salt207 below-rho anchor set",
        phase8_anchor_set_right207_salt207,
    ),
    (
        "p661_phase3_mod7_3_right207_anchor13_salt207",
        "P659 phase3/mod7=3 right207 anchor13 salt207 branch",
        phase3_mod7_3_right207_anchor13_salt207,
    ),
    (
        "p661_phase3_right207_anchor13_salt207",
        "P659 phase3 right207 anchor13 salt207 branch",
        phase3_right207_anchor13_salt207,
    ),
    (
        "p661_mod7_3_right207_anchor13_salt207",
        "P659 same-mod7=3 right207 anchor13 salt207 branch",
        mod7_3_right207_anchor13_salt207,
    ),
    (
        "p661_broad_right207_salt207",
        "P659 broad right207 salt207 branch",
        right207_salt207_family,
    ),
    (
        "p661_broad_right207_anchor13_salt207",
        "P659 broad right207 anchor13 salt207 branch",
        right207_anchor13_salt207_family,
    ),
]

for salt_left in sorted(SALT207_LEFTS):
    RULES.extend(
        [
            (
                f"p661_phase8_mod7_1_right207_salt{salt_left}_salt207",
                f"P659 phase8/mod7=1 right207 salt{salt_left}_salt207 row-pair split",
                phase8_mod7_1_row_pair_pred(salt_left),
            ),
            (
                f"p661_phase8_right207_salt{salt_left}_salt207",
                f"P659 phase8 right207 salt{salt_left}_salt207 row-pair split",
                phase8_row_pair_pred(salt_left),
            ),
            (
                f"p661_phase3_mod7_3_right207_anchor13_salt{salt_left}_salt207",
                f"P659 phase3/mod7=3 right207 anchor13 salt{salt_left}_salt207 row-pair split",
                phase3_mod7_3_anchor13_row_pair_pred(salt_left),
            ),
            (
                f"p661_phase3_right207_anchor13_salt{salt_left}_salt207",
                f"P659 phase3 right207 anchor13 salt{salt_left}_salt207 row-pair split",
                phase3_anchor13_row_pair_pred(salt_left),
            ),
            (
                f"p661_broad_right207_salt{salt_left}_salt207",
                f"P659 broad right207 salt{salt_left}_salt207 row-pair split",
                row_pair_pred(salt_left),
            ),
        ]
    )

for anchor in sorted(PHASE8_ANCHORS):
    RULES.append(
        (
            f"p661_phase8_right207_anchor{anchor}_salt207",
            f"P659 phase8 right207 salt207 anchor {anchor} split",
            phase8_anchor_pred(anchor),
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
    phase8_exact = report_named(reports, "p661_phase8_mod7_1_right207_salt207")
    phase8 = report_named(reports, "p661_phase8_right207_salt207")
    mod7_1 = report_named(reports, "p661_mod7_1_right207_salt207")
    phase3_exact = report_named(reports, "p661_phase3_mod7_3_right207_anchor13_salt207")
    phase3 = report_named(reports, "p661_phase3_right207_anchor13_salt207")
    mod7_3 = report_named(reports, "p661_mod7_3_right207_anchor13_salt207")
    broad = report_named(reports, "p661_broad_right207_salt207")
    anchor13 = report_named(reports, "p661_broad_right207_anchor13_salt207")

    if has_below(phase8_exact) and has_rank3(phase8_exact):
        return f"{claim_prefix}_PHASE8_MOD7_1_RIGHT207_SALT207_BELOW_RHO_RANK3_PERSISTENCE"
    if has_below(phase8_exact):
        return f"{claim_prefix}_PHASE8_MOD7_1_RIGHT207_SALT207_BELOW_RHO_PERSISTENCE"
    if has_below(phase3_exact) and has_rank3(phase3_exact):
        return f"{claim_prefix}_PHASE3_MOD7_3_RIGHT207_ANCHOR13_SALT207_BELOW_RHO_RANK3_PERSISTENCE"
    if has_below(phase3_exact):
        return f"{claim_prefix}_PHASE3_MOD7_3_RIGHT207_ANCHOR13_SALT207_BELOW_RHO_PERSISTENCE"
    if has_below(phase8):
        return f"{claim_prefix}_PHASE8_RIGHT207_SALT207_BELOW_RHO_DRIFT"
    if has_below(mod7_1):
        return f"{claim_prefix}_MOD7_1_RIGHT207_SALT207_BELOW_RHO_DRIFT"
    if has_below(phase3):
        return f"{claim_prefix}_PHASE3_RIGHT207_ANCHOR13_SALT207_BELOW_RHO_DRIFT"
    if has_below(mod7_3):
        return f"{claim_prefix}_MOD7_3_RIGHT207_ANCHOR13_SALT207_BELOW_RHO_DRIFT"
    if has_rank3(phase8_exact) or has_rank3(phase3_exact):
        return f"{claim_prefix}_REGISTERED_EXACT_RANK_SURFACE_PERSISTENCE"
    if has_below(broad):
        return f"{claim_prefix}_BROAD_RIGHT207_SALT207_BELOW_RHO_DRIFT"
    if has_below(anchor13):
        return f"{claim_prefix}_BROAD_RIGHT207_ANCHOR13_SALT207_BELOW_RHO_DRIFT"
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
    parser.add_argument("--claim-prefix", default="P661")
    parser.add_argument(
        "--quiet-claim",
        default="NEGATIVE_RESULT_P661_RIGHT207_SALT207_P659_BRANCH_ADJACENT_QUIET_BLOCK",
    )
    args = parser.parse_args()

    gate = json.loads(Path(args.gate).read_text())
    features = [p643.feature(case) for case in gate.get("cases", [])]
    raw_summary = summarize_cases(features)
    reports = [rule_report(name, desc, pred, features, raw_summary) for name, desc, pred in RULES]
    claim_status = determine_claim(reports, raw_summary, args.claim_prefix, args.quiet_claim)

    payload = {
        "schema": "ecdlp.low_term_total2_p661_right207_salt207_p659_branch_scout.v1",
        "created_at": utc_now(),
        "method": "p661_right207_salt207_p659_branch_scout",
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
            "P661 tests adjacent persistence and public-feature drift for P659's right207/salt207 branch.",
            "A below-rho direct replay is a relation-event metric, not a complete faster-than-rho ECDLP algorithm.",
            "Above-rho substitution recovery is bounded relation-bank evidence, not arbitrary target descent.",
            "Promotion still requires source-generation charge, sparse linear algebra, target descent, and individual-log accounting.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claim_status": claim_status, **raw_summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
