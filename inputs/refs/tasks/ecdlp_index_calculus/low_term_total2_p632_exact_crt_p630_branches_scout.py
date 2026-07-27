#!/usr/bin/env python3
"""P632 exact CRT recurrence scan for P630 phase/mod7 branches."""

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
    / "low_term_total2_fixed_leaf_shared_product_gate_p632_order9887_exact_crt_p630_branches_21990_22002_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p632_exact_crt_p630_branches_source_21990_22002_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p632_exact_crt_p630_branches_scout_21990_22002_probe.json"

SELECTOR_RE = re.compile(
    r"_t(?P<transfer>\d+)_salt(?P<salt_left>\d+)_salt(?P<salt_right>\d+)"
    r"_ra(?P<right_anchor>\d+)_L(?P<left_leaf>\d+)_R(?P<right_leaf>\d+)-(?P<top_k>\d+)"
)

ANCHORS = {3, 6, 7, 8, 9, 11, 12, 13}
SALT207_LEFTS = {203, 205, 206}
RIGHT206_LEFTS = {203, 204, 205, 206}
EXACT_RIGHT206_TRANSFER = 21993
EXACT_RIGHT207_TRANSFER = 21998


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


def right206_anchor9_salt204_salt206(f: dict[str, Any]) -> bool:
    return (
        standard_leaf(f)
        and f.get("salt_left") == 204
        and f.get("salt_right") == 206
        and f.get("right_anchor") == 9
    )


def right207_anchor13_salt207(f: dict[str, Any]) -> bool:
    return (
        standard_leaf(f)
        and f.get("salt_left") in SALT207_LEFTS
        and f.get("salt_right") == 207
        and f.get("right_anchor") == 13
    )


def broad_right206_all_anchor(f: dict[str, Any]) -> bool:
    return (
        standard_leaf(f)
        and f.get("salt_left") in RIGHT206_LEFTS
        and f.get("salt_right") == 206
        and f.get("right_anchor") in ANCHORS
    )


def broad_right207_salt207_all_anchor(f: dict[str, Any]) -> bool:
    return (
        standard_leaf(f)
        and f.get("salt_left") in SALT207_LEFTS
        and f.get("salt_right") == 207
        and f.get("right_anchor") in ANCHORS
    )


def exact_right206_recurrence(f: dict[str, Any]) -> bool:
    return right206_anchor9_salt204_salt206(f) and f.get("transfer_index") == EXACT_RIGHT206_TRANSFER


def exact_right207_salt203(f: dict[str, Any]) -> bool:
    return (
        right207_anchor13_salt207(f)
        and f.get("salt_left") == 203
        and f.get("transfer_index") == EXACT_RIGHT207_TRANSFER
    )


def exact_right207_salt205(f: dict[str, Any]) -> bool:
    return (
        right207_anchor13_salt207(f)
        and f.get("salt_left") == 205
        and f.get("transfer_index") == EXACT_RIGHT207_TRANSFER
    )


def exact_right207_salt206(f: dict[str, Any]) -> bool:
    return (
        right207_anchor13_salt207(f)
        and f.get("salt_left") == 206
        and f.get("transfer_index") == EXACT_RIGHT207_TRANSFER
    )


def exact_right207_recurrence_union(f: dict[str, Any]) -> bool:
    return right207_anchor13_salt207(f) and f.get("transfer_index") == EXACT_RIGHT207_TRANSFER


def phase9_right206_anchor9(f: dict[str, Any]) -> bool:
    return right206_anchor9_salt204_salt206(f) and f.get("transfer_mod12") == 9


def mod7_6_right206_anchor9(f: dict[str, Any]) -> bool:
    return right206_anchor9_salt204_salt206(f) and f.get("transfer_mod7") == 6


def all_phase_right206_anchor9(f: dict[str, Any]) -> bool:
    return right206_anchor9_salt204_salt206(f)


def phase2_right207_anchor13(f: dict[str, Any]) -> bool:
    return right207_anchor13_salt207(f) and f.get("transfer_mod12") == 2


def mod7_4_right207_anchor13(f: dict[str, Any]) -> bool:
    return right207_anchor13_salt207(f) and f.get("transfer_mod7") == 4


def all_phase_right207_anchor13(f: dict[str, Any]) -> bool:
    return right207_anchor13_salt207(f)


def split_union(f: dict[str, Any]) -> bool:
    return all_phase_right206_anchor9(f) or all_phase_right207_anchor13(f)


RULES: list[tuple[str, str, Callable[[dict[str, Any]], bool]]] = [
    (
        "p632_exact_21993_phase9_mod7_6_right206_anchor9_salt204_salt206",
        "Exact P630 phase9/mod7=6 right206/anchor9 salt204_salt206 recurrence at transfer 21993",
        exact_right206_recurrence,
    ),
    (
        "p632_exact_21998_phase2_mod7_4_right207_anchor13_salt203_salt207",
        "Exact P630 phase2/mod7=4 right207/anchor13 salt203_salt207 sibling recurrence at transfer 21998",
        exact_right207_salt203,
    ),
    (
        "p632_exact_21998_phase2_mod7_4_right207_anchor13_salt205_salt207",
        "Exact P630 phase2/mod7=4 right207/anchor13 salt205_salt207 sibling recurrence at transfer 21998",
        exact_right207_salt205,
    ),
    (
        "p632_exact_21998_phase2_mod7_4_right207_anchor13_salt206_salt207",
        "Exact P630 phase2/mod7=4 right207/anchor13 salt206_salt207 below-rho recurrence at transfer 21998",
        exact_right207_salt206,
    ),
    (
        "p632_exact_21998_phase2_mod7_4_right207_anchor13_salt207_union",
        "Exact P630 phase2/mod7=4 right207/anchor13 salt207 row-pair union at transfer 21998",
        exact_right207_recurrence_union,
    ),
    (
        "p632_phase9_right206_anchor9_salt204_salt206",
        "P630 phase9 right206/anchor9 salt204_salt206 diagnostic",
        phase9_right206_anchor9,
    ),
    (
        "p632_mod7_6_right206_anchor9_salt204_salt206",
        "P630 same-mod7=6 right206/anchor9 salt204_salt206 diagnostic",
        mod7_6_right206_anchor9,
    ),
    (
        "p632_all_phase_right206_anchor9_salt204_salt206",
        "P630 all-phase right206/anchor9 salt204_salt206 diagnostic",
        all_phase_right206_anchor9,
    ),
    (
        "p632_phase2_right207_anchor13_salt207_union",
        "P630 phase2 right207/anchor13 salt207 row-pair diagnostic",
        phase2_right207_anchor13,
    ),
    (
        "p632_mod7_4_right207_anchor13_salt207_union",
        "P630 same-mod7=4 right207/anchor13 salt207 row-pair diagnostic",
        mod7_4_right207_anchor13,
    ),
    (
        "p632_all_phase_right207_anchor13_salt207_union",
        "P630 all-phase right207/anchor13 salt207 row-pair diagnostic",
        all_phase_right207_anchor13,
    ),
    (
        "p632_broad_right206_all_anchor_any_left",
        "Broad right206 all-anchor row-pair diagnostic",
        broad_right206_all_anchor,
    ),
    (
        "p632_broad_right207_salt207_all_anchor",
        "Broad right207 salt207 all-anchor diagnostic",
        broad_right207_salt207_all_anchor,
    ),
    (
        "p632_split_union",
        "Union of all-phase right206/anchor9 salt204_salt206 and all-phase right207/anchor13 salt207",
        split_union,
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
        "selected_direct_verified_case_entries": [case_entry(f) for f in verified],
        "selected_direct_below_rho_verified_case_entries": [case_entry(f) for f in below],
        "examples": selected[:24],
        "positive_examples": below[:24],
        "rank3_examples": [f for f in verified if int(f.get("rank") or 0) >= 3][:24],
    }


def report_named(reports: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    return next((r for r in reports if r["rule"] == name), None)


def determine_claim(reports: list[dict[str, Any]], raw: dict[str, Any]) -> str:
    exact_right206 = report_named(reports, "p632_exact_21993_phase9_mod7_6_right206_anchor9_salt204_salt206")
    exact_right207 = report_named(reports, "p632_exact_21998_phase2_mod7_4_right207_anchor13_salt207_union")
    phase9 = report_named(reports, "p632_phase9_right206_anchor9_salt204_salt206")
    phase2 = report_named(reports, "p632_phase2_right207_anchor13_salt207_union")
    right206 = report_named(reports, "p632_all_phase_right206_anchor9_salt204_salt206")
    right207 = report_named(reports, "p632_all_phase_right207_anchor13_salt207_union")
    if exact_right206 and exact_right206["direct_below_rho_verified_count"]:
        return "P632_EXACT_RIGHT206_PHASE9_MOD7_6_BELOW_RHO_RECURRENCE"
    if exact_right207 and exact_right207["direct_below_rho_verified_count"]:
        return "P632_EXACT_RIGHT207_PHASE2_MOD7_4_BELOW_RHO_RECURRENCE"
    if phase9 and phase9["direct_below_rho_verified_count"]:
        return "P632_PHASE9_RIGHT206_BELOW_RHO_DRIFT"
    if phase2 and phase2["direct_below_rho_verified_count"]:
        return "P632_PHASE2_RIGHT207_BELOW_RHO_DRIFT"
    if right206 and right206["direct_below_rho_verified_count"]:
        return "P632_RIGHT206_ANCHOR9_BELOW_RHO_DRIFT"
    if right207 and right207["direct_below_rho_verified_count"]:
        return "P632_RIGHT207_ANCHOR13_BELOW_RHO_DRIFT"
    if any(r["direct_below_rho_verified_count"] for r in reports):
        return "P632_REGISTERED_SPLIT_BELOW_RHO_POSITIVE"
    if exact_right206 and exact_right206["rank3_direct_verified_count"]:
        return "P632_EXACT_RIGHT206_RANK_SURFACE_RECURRENCE"
    if exact_right207 and exact_right207["rank3_direct_verified_count"]:
        return "P632_EXACT_RIGHT207_RANK_SURFACE_RECURRENCE"
    if any(r["rank3_direct_verified_count"] for r in reports):
        return "P632_REGISTERED_SPLIT_RANK_SURFACE_POSITIVE"
    if raw["direct_verified_count"]:
        return "NEGATIVE_RESULT_P632_REGISTERED_CONTROLS_MISSED_NONQUIET_BLOCK"
    return "NEGATIVE_RESULT_P632_EXACT_CRT_RECURRENCE_QUIET_BLOCK"


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
        "schema": "ecdlp.low_term_total2_p632_exact_crt_p630_branches_scout.v1",
        "created_at": utc_now(),
        "method": "p632_exact_crt_p630_branches_scout",
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
        },
        "rule_reports": reports,
        "honesty_boundary": [
            "Verifier labels are used only for post-run evaluation, not for rule definition.",
            "P632 tests exact phase/mod7 CRT recurrence of P630's two raw relation-supply branches.",
            "A below-rho direct replay is a relation-event metric, not a complete faster-than-rho ECDLP algorithm.",
            "Rank-3 or rank-4 rows and unique factor-relation gain are relation-bank signals, not solved sparse linear algebra.",
            "Promotion still requires source-generation charge, sparse linear algebra, target descent, and individual-log accounting.",
        ],
    }
    out_path = Path(args.out)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claim_status": claim_status, **raw_summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
