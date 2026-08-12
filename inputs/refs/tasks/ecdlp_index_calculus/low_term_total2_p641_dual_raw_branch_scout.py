#!/usr/bin/env python3
"""P641 adjacent scan for P640 dual raw below-rho branches."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p641_order9887_dual_raw_branch_22107_22119_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p641_dual_raw_branch_source_22107_22119_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p641_dual_raw_branch_scout_22107_22119_probe.json"

SELECTOR_RE = re.compile(
    r"_t(?P<transfer>\d+)_salt(?P<salt_left>\d+)_salt(?P<salt_right>\d+)"
    r"_ra(?P<right_anchor>\d+)_L(?P<left_leaf>\d+)_R(?P<right_leaf>\d+)-(?P<top_k>\d+)"
)

ANCHORS = {3, 6, 7, 8, 9, 11, 12, 13}
SALT208_LEFTS = {203, 204, 205, 206}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def feature(case: dict[str, Any]) -> dict[str, Any]:
    selector = str(case.get("selector", ""))
    match = SELECTOR_RE.search(selector)
    if not match:
        return {
            "selector": selector,
            "parse_ok": False,
            "target": case.get("target"),
            "transfer_index": case.get("transfer_index"),
            "top_k": case.get("top_k"),
        }
    transfer = int(match.group("transfer"))
    salt_left = int(match.group("salt_left"))
    salt_right = int(match.group("salt_right"))
    right_anchor = int(match.group("right_anchor"))
    left_leaf = int(match.group("left_leaf"))
    right_leaf = int(match.group("right_leaf"))
    top_k = int(match.group("top_k"))
    return {
        "selector": selector,
        "parse_ok": True,
        "target": case.get("target"),
        "transfer_index": transfer,
        "transfer_mod12": transfer % 12,
        "transfer_mod7": transfer % 7,
        "salt_left": salt_left,
        "salt_right": salt_right,
        "row_pair": f"salt{salt_left}_salt{salt_right}",
        "right_anchor": right_anchor,
        "left_leaf": left_leaf,
        "right_leaf": right_leaf,
        "leaf_signature": f"L{left_leaf:02d}_R{right_leaf:02d}-{top_k}",
        "top_k": top_k,
        "base_selector": selector.split("__", 1)[0],
        "direct_verified": bool(case.get("direct_union_public_key_verified")),
        "direct_below_rho_verified": bool(
            case.get("direct_union_public_key_verified") and case.get("direct_below_rho")
        ),
        "direct_ops_over_rho": case.get("direct_verifier_replay_ops_over_rho"),
        "rank": int(case.get("direct_union_rank") or 0),
        "relation_count": int(case.get("direct_union_relation_count") or 0),
    }


def feature_id(f: dict[str, Any]) -> str:
    return (
        f"phase{f.get('transfer_mod12')}_mod7{f.get('transfer_mod7')}"
        f"_right{f.get('salt_right')}_anchor{f.get('right_anchor')}"
        f"_salt{f.get('salt_left')}_salt{f.get('salt_right')}"
    )


def case_entry(f: dict[str, Any]) -> str:
    return f"{f.get('target')}|{f.get('transfer_index')}|{f.get('selector')}|{f.get('top_k')}"


def standard_leaf(f: dict[str, Any]) -> bool:
    return (
        f.get("parse_ok")
        and f.get("left_leaf") == 9
        and f.get("right_leaf") == f.get("right_anchor")
        and f.get("top_k") == 16
    )


def right208_salt208_family(f: dict[str, Any]) -> bool:
    return (
        standard_leaf(f)
        and f.get("salt_left") in SALT208_LEFTS
        and f.get("salt_right") == 208
        and f.get("right_anchor") in ANCHORS
    )


def right208_anchor9_salt208_family(f: dict[str, Any]) -> bool:
    return right208_salt208_family(f) and f.get("right_anchor") == 9


def right208_anchor9_salt206_salt208(f: dict[str, Any]) -> bool:
    return right208_anchor9_salt208_family(f) and f.get("salt_left") == 206


def phase4_right208_anchor9_salt206_salt208(f: dict[str, Any]) -> bool:
    return right208_anchor9_salt206_salt208(f) and f.get("transfer_mod12") == 4


def mod7_4_right208_anchor9_salt206_salt208(f: dict[str, Any]) -> bool:
    return right208_anchor9_salt206_salt208(f) and f.get("transfer_mod7") == 4


def all_phase_right208_anchor9_salt206_salt208(f: dict[str, Any]) -> bool:
    return right208_anchor9_salt206_salt208(f)


def phase4_right208_anchor9_salt208_family(f: dict[str, Any]) -> bool:
    return right208_anchor9_salt208_family(f) and f.get("transfer_mod12") == 4


def mod7_4_right208_anchor9_salt208_family(f: dict[str, Any]) -> bool:
    return right208_anchor9_salt208_family(f) and f.get("transfer_mod7") == 4


def all_phase_right208_anchor9_salt208_family(f: dict[str, Any]) -> bool:
    return right208_anchor9_salt208_family(f)


def broad_right208_salt208_all_anchor(f: dict[str, Any]) -> bool:
    return right208_salt208_family(f)


def right206_salt204_salt206_all_anchor(f: dict[str, Any]) -> bool:
    return (
        standard_leaf(f)
        and f.get("salt_left") == 204
        and f.get("salt_right") == 206
        and f.get("right_anchor") in ANCHORS
    )


def right206_anchor6_salt204_salt206(f: dict[str, Any]) -> bool:
    return right206_salt204_salt206_all_anchor(f) and f.get("right_anchor") == 6


def phase0_right206_anchor6_salt204_salt206(f: dict[str, Any]) -> bool:
    return right206_anchor6_salt204_salt206(f) and f.get("transfer_mod12") == 0


def mod7_5_right206_anchor6_salt204_salt206(f: dict[str, Any]) -> bool:
    return right206_anchor6_salt204_salt206(f) and f.get("transfer_mod7") == 5


def all_phase_right206_anchor6_salt204_salt206(f: dict[str, Any]) -> bool:
    return right206_anchor6_salt204_salt206(f)


RULES: list[tuple[str, str, Callable[[dict[str, Any]], bool]]] = [
    (
        "p641_phase4_right208_anchor9_salt206_salt208",
        "P640 phase4/right208/anchor9 salt206_salt208 adjacent persistence",
        phase4_right208_anchor9_salt206_salt208,
    ),
    (
        "p641_mod7_4_right208_anchor9_salt206_salt208",
        "P640 same-mod7=4 right208/anchor9 salt206_salt208 diagnostic",
        mod7_4_right208_anchor9_salt206_salt208,
    ),
    (
        "p641_all_phase_right208_anchor9_salt206_salt208",
        "P640 all-phase right208/anchor9 salt206_salt208 diagnostic",
        all_phase_right208_anchor9_salt206_salt208,
    ),
    (
        "p641_phase4_right208_anchor9_salt208_family",
        "P640 phase4/right208/anchor9 salt208 row-pair family",
        phase4_right208_anchor9_salt208_family,
    ),
    (
        "p641_mod7_4_right208_anchor9_salt208_family",
        "P640 same-mod7=4 right208/anchor9 salt208 row-pair family",
        mod7_4_right208_anchor9_salt208_family,
    ),
    (
        "p641_all_phase_right208_anchor9_salt208_family",
        "P640 all-phase right208/anchor9 salt208 row-pair family",
        all_phase_right208_anchor9_salt208_family,
    ),
    (
        "p641_broad_right208_salt208_all_anchor",
        "P640 broad right208/salt208 all-anchor diagnostic",
        broad_right208_salt208_all_anchor,
    ),
    (
        "p641_phase0_right206_anchor6_salt204_salt206",
        "P640 phase0/right206/anchor6 salt204_salt206 adjacent persistence",
        phase0_right206_anchor6_salt204_salt206,
    ),
    (
        "p641_mod7_5_right206_anchor6_salt204_salt206",
        "P640 same-mod7=5 right206/anchor6 salt204_salt206 diagnostic",
        mod7_5_right206_anchor6_salt204_salt206,
    ),
    (
        "p641_all_phase_right206_anchor6_salt204_salt206",
        "P640 all-phase right206/anchor6 salt204_salt206 diagnostic",
        all_phase_right206_anchor6_salt204_salt206,
    ),
    (
        "p641_broad_right206_salt204_salt206_all_anchor",
        "P640 broad right206 salt204_salt206 all-anchor diagnostic",
        right206_salt204_salt206_all_anchor,
    ),
]


def summarize_cases(features: list[dict[str, Any]]) -> dict[str, Any]:
    verified = [f for f in features if f.get("direct_verified")]
    below = [f for f in features if f.get("direct_below_rho_verified")]
    return {
        "case_count": len(features),
        "direct_verified_count": len(verified),
        "direct_below_rho_verified_count": len(below),
        "rank3_direct_verified_count": sum(1 for f in verified if int(f.get("rank") or 0) >= 3),
        "verified_transfer_counts": dict(Counter(str(f["transfer_index"]) for f in verified)),
        "positive_transfer_counts": dict(Counter(str(f["transfer_index"]) for f in below)),
        "verified_feature_counts": dict(Counter(feature_id(f) for f in verified)),
        "positive_feature_counts": dict(Counter(feature_id(f) for f in below)),
        "verified_rank_counts": dict(Counter(str(f.get("rank")) for f in verified)),
        "direct_verified_case_entries": [case_entry(f) for f in verified],
        "direct_below_rho_verified_case_entries": [case_entry(f) for f in below],
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
    selected_count = len(selected)
    return {
        "rule": name,
        "description": description,
        "selected_count": selected_count,
        "selected_fraction": selected_count / max(1, raw_summary["case_count"]),
        "direct_verified_count": len(verified),
        "direct_below_rho_verified_count": len(below),
        "rank3_direct_verified_count": sum(1 for f in verified if int(f.get("rank") or 0) >= 3),
        "direct_verified_precision": len(verified) / selected_count if selected_count else 0.0,
        "direct_below_rho_verified_precision": len(below) / selected_count if selected_count else 0.0,
        "direct_verified_recall": len(verified) / max(1, raw_summary["direct_verified_count"]),
        "direct_below_rho_verified_recall": len(below)
        / max(1, raw_summary["direct_below_rho_verified_count"]),
        "transfer_counts": dict(Counter(str(f["transfer_index"]) for f in selected)),
        "right_anchor_counts": dict(Counter(str(f["right_anchor"]) for f in selected)),
        "row_pair_counts": dict(Counter(str(f["row_pair"]) for f in selected)),
        "verified_feature_counts": dict(Counter(feature_id(f) for f in verified)),
        "positive_feature_counts": dict(Counter(feature_id(f) for f in below)),
        "verified_rank_counts": dict(Counter(str(f.get("rank")) for f in verified)),
        "selected_direct_verified_case_entries": [case_entry(f) for f in verified],
        "selected_direct_below_rho_verified_case_entries": [case_entry(f) for f in below],
        "examples": selected[:24],
        "positive_examples": below[:24],
        "rank3_examples": [f for f in verified if int(f.get("rank") or 0) >= 3][:24],
    }


def report_named(reports: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    return next((r for r in reports if r["rule"] == name), None)


def determine_claim(reports: list[dict[str, Any]], raw: dict[str, Any]) -> str:
    phase4_208 = report_named(reports, "p641_phase4_right208_anchor9_salt206_salt208")
    mod7_208 = report_named(reports, "p641_mod7_4_right208_anchor9_salt206_salt208")
    all_208 = report_named(reports, "p641_all_phase_right208_anchor9_salt206_salt208")
    family_208 = report_named(reports, "p641_all_phase_right208_anchor9_salt208_family")
    broad_208 = report_named(reports, "p641_broad_right208_salt208_all_anchor")
    phase0_206 = report_named(reports, "p641_phase0_right206_anchor6_salt204_salt206")
    mod7_206 = report_named(reports, "p641_mod7_5_right206_anchor6_salt204_salt206")
    all_206 = report_named(reports, "p641_all_phase_right206_anchor6_salt204_salt206")
    broad_206 = report_named(reports, "p641_broad_right206_salt204_salt206_all_anchor")
    if phase4_208 and phase4_208["direct_below_rho_verified_count"]:
        return "P641_PHASE4_RIGHT208_ANCHOR9_SALT206_SALT208_BELOW_RHO_PERSISTENCE"
    if mod7_208 and mod7_208["direct_below_rho_verified_count"]:
        return "P641_MOD7_4_RIGHT208_ANCHOR9_SALT206_SALT208_BELOW_RHO_PERSISTENCE"
    if all_208 and all_208["direct_below_rho_verified_count"]:
        return "P641_RIGHT208_ANCHOR9_SALT206_SALT208_BELOW_RHO_DRIFT"
    if family_208 and family_208["direct_below_rho_verified_count"]:
        return "P641_RIGHT208_ANCHOR9_SALT208_FAMILY_BELOW_RHO_DRIFT"
    if broad_208 and broad_208["direct_below_rho_verified_count"]:
        return "P641_BROAD_RIGHT208_SALT208_BELOW_RHO_DRIFT"
    if phase0_206 and phase0_206["direct_below_rho_verified_count"]:
        return "P641_PHASE0_RIGHT206_ANCHOR6_SALT204_SALT206_BELOW_RHO_PERSISTENCE"
    if mod7_206 and mod7_206["direct_below_rho_verified_count"]:
        return "P641_MOD7_5_RIGHT206_ANCHOR6_SALT204_SALT206_BELOW_RHO_PERSISTENCE"
    if all_206 and all_206["direct_below_rho_verified_count"]:
        return "P641_RIGHT206_ANCHOR6_SALT204_SALT206_BELOW_RHO_DRIFT"
    if broad_206 and broad_206["direct_below_rho_verified_count"]:
        return "P641_BROAD_RIGHT206_SALT204_SALT206_BELOW_RHO_DRIFT"
    if any(r["direct_below_rho_verified_count"] for r in reports):
        return "P641_REGISTERED_BELOW_RHO_POSITIVE"
    if any(r["rank3_direct_verified_count"] for r in reports):
        return "P641_REGISTERED_RANK_SURFACE_POSITIVE"
    if any(r["direct_verified_count"] for r in reports):
        return "P641_REGISTERED_ABOVE_RHO_POSITIVE"
    if raw["direct_verified_count"]:
        return "NEGATIVE_RESULT_P641_REGISTERED_CONTROLS_MISSED_NONQUIET_BLOCK"
    return "NEGATIVE_RESULT_P641_DUAL_RAW_BRANCH_QUIET_BLOCK"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", default=str(DEFAULT_GATE))
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    gate = json.loads(Path(args.gate).read_text())
    features = [feature(case) for case in gate.get("cases", [])]
    raw_summary = summarize_cases(features)
    reports = [rule_report(name, desc, pred, features, raw_summary) for name, desc, pred in RULES]
    claim_status = determine_claim(reports, raw_summary)

    payload = {
        "schema": "ecdlp.low_term_total2_p641_dual_raw_branch_scout.v1",
        "created_at": utc_now(),
        "method": "p641_dual_raw_branch_scout",
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
            "Verifier labels are used only for post-run evaluation, not for rule definition.",
            "P641 tests adjacent drift of P640's dual raw relation-supply branches.",
            "A below-rho direct replay is a relation-event metric, not a complete faster-than-rho ECDLP algorithm.",
            "Substitution recovery is a bounded relation-bank signal, not solved target descent.",
            "Promotion still requires source-generation charge, sparse linear algebra, target descent, and individual-log accounting.",
        ],
    }
    out_path = Path(args.out)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claim_status": claim_status, **raw_summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
