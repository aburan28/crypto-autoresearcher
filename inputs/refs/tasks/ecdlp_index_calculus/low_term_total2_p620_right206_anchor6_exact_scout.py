#!/usr/bin/env python3
"""P620 scout for the P619 right206/anchor6 exact recurrence."""

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
    / "low_term_total2_fixed_leaf_shared_product_gate_p620_order9887_right206_anchor6_exact_21661_21673_density_gate_probe.json"
)
DEFAULT_SOURCE = (
    STATE_DIR
    / "low_term_total2_order9887_p620_right206_anchor6_exact_source_21661_21673_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_p620_right206_anchor6_exact_scout_21661_21673_probe.json"

SELECTOR_RE = re.compile(
    r"_t(?P<transfer>\d+)_salt(?P<salt_left>\d+)_salt(?P<salt_right>\d+)"
    r"_ra(?P<right_anchor>\d+)_L(?P<left_leaf>\d+)_R(?P<right_leaf>\d+)-(?P<top_k>\d+)"
)


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


def p620_exact(f: dict[str, Any]) -> bool:
    return (
        f.get("parse_ok")
        and f.get("transfer_index") == 21665
        and f.get("transfer_mod12") == 5
        and f.get("transfer_mod7") == 0
        and f.get("salt_left") == 204
        and f.get("salt_right") == 206
        and f.get("right_anchor") == 6
        and f.get("left_leaf") == 9
        and f.get("right_leaf") == 6
        and f.get("top_k") == 16
    )


def p620_right206_anchor6_all_phases(f: dict[str, Any]) -> bool:
    return (
        f.get("parse_ok")
        and f.get("salt_left") == 204
        and f.get("salt_right") == 206
        and f.get("right_anchor") == 6
        and f.get("top_k") == 16
    )


def p620_right206_all_anchors_all_phases(f: dict[str, Any]) -> bool:
    return (
        f.get("parse_ok")
        and f.get("salt_left") == 204
        and f.get("salt_right") == 206
        and f.get("top_k") == 16
    )


RULES: list[tuple[str, str, Callable[[dict[str, Any]], bool]]] = [
    (
        "p620_phase5_mod7_0_right206_anchor6_exact",
        "Exact +84 recurrence of P619 phase5/right206/anchor6 branch at 21665",
        p620_exact,
    ),
    (
        "p620_right206_anchor6_all_phases",
        "Broader right206/anchor6 control across all phases in the validation block",
        p620_right206_anchor6_all_phases,
    ),
    (
        "p620_right206_salt204_salt206_all_anchors_all_phases",
        "Broad right206 salt204/salt206 all-anchor control across all phases in the validation block",
        p620_right206_all_anchors_all_phases,
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


def determine_claim(main: dict[str, Any], raw: dict[str, Any]) -> str:
    if main["direct_below_rho_verified_count"]:
        return "P620_EXACT_RIGHT206_ANCHOR6_BELOW_RHO_POSITIVE"
    if main["direct_verified_count"]:
        return "P620_EXACT_RIGHT206_ANCHOR6_VERIFIED_POSITIVE"
    if raw["direct_verified_count"]:
        return "NEGATIVE_RESULT_P620_PRIMARY_MISSED_NONQUIET_BLOCK"
    return "NEGATIVE_RESULT_P620_VALIDATION_QUIET_BLOCK"


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
    main_report = reports[0]
    claim_status = determine_claim(main_report, raw_summary)

    payload = {
        "schema": "ecdlp.low_term_total2_p620_right206_anchor6_exact_scout.v1",
        "created_at": utc_now(),
        "method": "p620_right206_anchor6_exact_scout",
        "claim_status": claim_status,
        "artifacts": {"source": str(args.source), "gate": str(args.gate)},
        "summary": {
            "claim_status": claim_status,
            "validation_dataset": raw_summary,
            "main_rule": main_report,
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
            "The exact P620 selector is source-public: transfer, phase, mod7, salts, anchor, leaves, and top-k.",
            "A below-rho direct replay is a relation-event metric, not a complete faster-than-rho ECDLP algorithm.",
            "Promotion still requires source-generation charge, sparse linear algebra, target descent, and individual-log accounting.",
        ],
    }
    out_path = Path(args.out)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claim_status": claim_status, **raw_summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
