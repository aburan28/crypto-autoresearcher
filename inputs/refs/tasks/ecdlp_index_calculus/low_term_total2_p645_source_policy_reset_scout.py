#!/usr/bin/env python3
"""P645 broad raw-burst source-policy reset scout."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p643_phase0_salt203_burst_scout as p643


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p645_order9887_source_policy_reset_22213_22225_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p645_source_policy_reset_source_22213_22225_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p645_source_policy_reset_scout_22213_22225_probe.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def right206_anchor3_salt204_salt206(f: dict[str, Any]) -> bool:
    return (
        p643.standard_leaf(f)
        and f.get("salt_left") == 204
        and f.get("salt_right") == 206
        and f.get("right_anchor") == 3
    )


def phase9_mod7_0_right206_anchor3_salt204_salt206(f: dict[str, Any]) -> bool:
    return (
        right206_anchor3_salt204_salt206(f)
        and f.get("transfer_mod12") == 9
        and f.get("transfer_mod7") == 0
    )


def broad_right206_salt204_salt206_all_anchor(f: dict[str, Any]) -> bool:
    return (
        p643.standard_leaf(f)
        and f.get("salt_left") == 204
        and f.get("salt_right") == 206
        and f.get("right_anchor") in p643.ANCHORS
    )


CONTROL_RULES: list[tuple[str, str, Callable[[dict[str, Any]], bool]]] = [
    (
        "p645_p641_phase9_mod7_0_right206_anchor3_salt204_salt206",
        "P641/P642 right206 anchor3 salt204_salt206 branch negative control",
        phase9_mod7_0_right206_anchor3_salt204_salt206,
    ),
    (
        "p645_broad_right206_salt204_salt206_all_anchor",
        "P641/P642 broad right206 salt204_salt206 all-anchor negative control",
        broad_right206_salt204_salt206_all_anchor,
    ),
    (
        "p645_phase0_mod7_1_right207_salt203_salt207_all_anchor",
        "P642/P643 phase0/mod7=1 right207 salt203_salt207 all-anchor control",
        p643.phase0_mod7_1_right207_salt203_salt207,
    ),
    (
        "p645_phase0_mod7_1_right207_anchor9_salt203_salt207_rank3",
        "P642/P643 phase0/mod7=1 right207 anchor9 salt203_salt207 rank-3 control",
        p643.phase0_mod7_1_right207_anchor9_salt203_salt207,
    ),
    (
        "p645_phase0_mod7_1_right208_salt203_salt208_all_anchor",
        "P642/P643 phase0/mod7=1 right208 salt203_salt208 all-anchor control",
        p643.phase0_mod7_1_right208_salt203_salt208,
    ),
    (
        "p645_phase0_mod7_1_salt203_right207_right208_union",
        "P642/P643 phase0/mod7=1 salt203 right207/right208 union control",
        p643.phase0_mod7_1_salt203_union,
    ),
    (
        "p645_broad_right208_salt208_all_anchor",
        "P642/P643 broad right208/salt208 all-anchor control",
        p643.broad_right208_salt208_all_anchor,
    ),
    (
        "p645_phase9_mod7_5_right207_anchor9_salt207_family",
        "P642/P644 phase9/mod7=5 right207 anchor9 salt207 family control",
        p643.phase9_mod7_5_right207_anchor9_salt207_family,
    ),
    (
        "p645_phase11_mod7_0_right207_anchor13_salt207_family",
        "P642/P644 phase11/mod7=0 right207 anchor13 salt207 family control",
        p643.phase11_mod7_0_right207_anchor13_salt207_family,
    ),
]


def key_transfer(f: dict[str, Any]) -> str:
    return str(f.get("transfer_index"))


def key_phase_mod7(f: dict[str, Any]) -> str:
    return f"phase{f.get('transfer_mod12')}_mod7{f.get('transfer_mod7')}"


def key_row_pair(f: dict[str, Any]) -> str:
    return str(f.get("row_pair"))


def key_right_anchor(f: dict[str, Any]) -> str:
    return f"anchor{f.get('right_anchor')}"


def key_salt_right_anchor(f: dict[str, Any]) -> str:
    return f"right{f.get('salt_right')}_anchor{f.get('right_anchor')}"


def key_phase_row_pair(f: dict[str, Any]) -> str:
    return f"{key_phase_mod7(f)}_{f.get('row_pair')}"


def key_phase_right_anchor(f: dict[str, Any]) -> str:
    return f"{key_phase_mod7(f)}_anchor{f.get('right_anchor')}"


def key_phase_salt_right_anchor(f: dict[str, Any]) -> str:
    return f"{key_phase_mod7(f)}_right{f.get('salt_right')}_anchor{f.get('right_anchor')}"


def key_phase_row_anchor(f: dict[str, Any]) -> str:
    return f"{key_phase_mod7(f)}_{f.get('row_pair')}_anchor{f.get('right_anchor')}"


def key_phase_row_anchor_leaf(f: dict[str, Any]) -> str:
    return (
        f"{key_phase_mod7(f)}_{f.get('row_pair')}_anchor{f.get('right_anchor')}"
        f"_{f.get('leaf_signature')}"
    )


BUCKET_FAMILIES: list[tuple[str, str, Callable[[dict[str, Any]], str]]] = [
    ("transfer", "Single transfer index", key_transfer),
    ("phase_mod7", "Transfer phase and mod7 pair", key_phase_mod7),
    ("row_pair", "Salt row-pair", key_row_pair),
    ("right_anchor", "Right anchor", key_right_anchor),
    ("salt_right_anchor", "Right salt and anchor", key_salt_right_anchor),
    ("phase_row_pair", "Phase/mod7 plus salt row-pair", key_phase_row_pair),
    ("phase_right_anchor", "Phase/mod7 plus right anchor", key_phase_right_anchor),
    ("phase_salt_right_anchor", "Phase/mod7 plus right salt and anchor", key_phase_salt_right_anchor),
    ("phase_row_anchor", "Phase/mod7 plus row-pair and anchor", key_phase_row_anchor),
    ("phase_row_anchor_leaf", "Phase/mod7 plus row-pair, anchor, and leaf signature", key_phase_row_anchor_leaf),
]


def bucket_entry(name: str, bucket_key: str, selected: list[dict[str, Any]], raw: dict[str, Any]) -> dict[str, Any]:
    verified = [f for f in selected if f.get("direct_verified")]
    below = [f for f in selected if f.get("direct_below_rho_verified")]
    rank3 = [f for f in verified if int(f.get("rank") or 0) >= 3]
    selected_count = len(selected)
    return {
        "bucket_family": name,
        "bucket_key": bucket_key,
        "selected_count": selected_count,
        "selected_fraction": selected_count / max(1, raw["case_count"]),
        "direct_verified_count": len(verified),
        "direct_below_rho_verified_count": len(below),
        "rank3_direct_verified_count": len(rank3),
        "direct_verified_precision": len(verified) / selected_count if selected_count else 0.0,
        "direct_below_rho_verified_precision": len(below) / selected_count if selected_count else 0.0,
        "direct_verified_recall": len(verified) / max(1, raw["direct_verified_count"]),
        "direct_below_rho_verified_recall": len(below) / max(1, raw["direct_below_rho_verified_count"]),
        "rank3_direct_verified_recall": len(rank3) / max(1, raw["rank3_direct_verified_count"]),
        "transfer_counts": dict(Counter(str(f["transfer_index"]) for f in selected)),
        "row_pair_counts": dict(Counter(str(f["row_pair"]) for f in selected)),
        "right_anchor_counts": dict(Counter(str(f["right_anchor"]) for f in selected)),
        "verified_feature_counts": dict(Counter(p643.feature_id(f) for f in verified)),
        "positive_feature_counts": dict(Counter(p643.feature_id(f) for f in below)),
        "rank3_feature_counts": dict(Counter(p643.feature_id(f) for f in rank3)),
        "selected_direct_verified_case_entries": [p643.case_entry(f) for f in verified],
        "selected_direct_below_rho_verified_case_entries": [p643.case_entry(f) for f in below],
        "selected_rank3_direct_verified_case_entries": [p643.case_entry(f) for f in rank3],
        "positive_examples": below[:12],
        "rank3_examples": rank3[:12],
    }


def bucket_report(
    name: str,
    description: str,
    key_fn: Callable[[dict[str, Any]], str],
    features: list[dict[str, Any]],
    raw: dict[str, Any],
) -> dict[str, Any]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for feature in features:
        if not feature.get("parse_ok"):
            continue
        buckets[key_fn(feature)].append(feature)
    entries = [
        bucket_entry(name, bucket_key, selected, raw)
        for bucket_key, selected in sorted(buckets.items())
    ]
    by_below = sorted(
        entries,
        key=lambda item: (
            -int(item["direct_below_rho_verified_count"]),
            -float(item["direct_below_rho_verified_precision"]),
            -int(item["rank3_direct_verified_count"]),
            int(item["selected_count"]),
            str(item["bucket_key"]),
        ),
    )
    by_direct = sorted(
        entries,
        key=lambda item: (
            -int(item["direct_verified_count"]),
            -float(item["direct_verified_precision"]),
            -int(item["rank3_direct_verified_count"]),
            int(item["selected_count"]),
            str(item["bucket_key"]),
        ),
    )
    by_rank3 = sorted(
        entries,
        key=lambda item: (
            -int(item["rank3_direct_verified_count"]),
            -float(item["direct_verified_precision"]),
            -int(item["direct_below_rho_verified_count"]),
            int(item["selected_count"]),
            str(item["bucket_key"]),
        ),
    )
    return {
        "bucket_family": name,
        "description": description,
        "nonempty_bucket_count": len(entries),
        "top_below_rho_buckets": by_below[:16],
        "top_direct_verified_buckets": by_direct[:16],
        "top_rank3_buckets": by_rank3[:16],
    }


def all_bucket_candidates(reports: list[dict[str, Any]], table: str) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for report in reports:
        candidates.extend(report.get(table) or [])
    return candidates


def best_bucket(reports: list[dict[str, Any]], table: str) -> dict[str, Any] | None:
    candidates = all_bucket_candidates(reports, table)
    if not candidates:
        return None
    if table == "top_rank3_buckets":
        return max(
            candidates,
            key=lambda item: (
                int(item["rank3_direct_verified_count"]),
                int(item["direct_below_rho_verified_count"]),
                float(item["direct_verified_precision"]),
                -int(item["selected_count"]),
            ),
        )
    if table == "top_direct_verified_buckets":
        return max(
            candidates,
            key=lambda item: (
                int(item["direct_verified_count"]),
                float(item["direct_verified_precision"]),
                int(item["direct_below_rho_verified_count"]),
                -int(item["selected_count"]),
            ),
        )
    return max(
        candidates,
        key=lambda item: (
            int(item["direct_below_rho_verified_count"]),
            float(item["direct_below_rho_verified_precision"]),
            int(item["rank3_direct_verified_count"]),
            -int(item["selected_count"]),
        ),
    )


def report_named(reports: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    return next((r for r in reports if r["rule"] == name), None)


def determine_claim(
    control_reports: list[dict[str, Any]],
    bucket_reports: list[dict[str, Any]],
    raw: dict[str, Any],
) -> str:
    if any(r["direct_below_rho_verified_count"] for r in control_reports):
        return "P645_REGISTERED_CONTROL_BELOW_RHO_POSITIVE"
    best_below = best_bucket(bucket_reports, "top_below_rho_buckets")
    best_rank3 = best_bucket(bucket_reports, "top_rank3_buckets")
    if best_below and int(best_below["direct_below_rho_verified_count"]) > 0:
        return "P645_RAW_BURST_BELOW_RHO_OBSERVATION"
    if best_rank3 and int(best_rank3["rank3_direct_verified_count"]) > 0:
        return "P645_RAW_RANK_SURFACE_OBSERVATION"
    if raw["direct_verified_count"]:
        return "P645_RAW_ABOVE_RHO_DIRECT_OBSERVATION"
    return "NEGATIVE_RESULT_P645_SOURCE_POLICY_RESET_QUIET_BLOCK"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", default=str(DEFAULT_GATE))
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    gate = json.loads(Path(args.gate).read_text())
    features = [p643.feature(case) for case in gate.get("cases", [])]
    raw_summary = p643.summarize_cases(features)
    control_reports = [
        p643.rule_report(name, desc, pred, features, raw_summary)
        for name, desc, pred in CONTROL_RULES
    ]
    bucket_reports = [
        bucket_report(name, desc, key_fn, features, raw_summary)
        for name, desc, key_fn in BUCKET_FAMILIES
    ]
    claim_status = determine_claim(control_reports, bucket_reports, raw_summary)

    payload = {
        "schema": "ecdlp.low_term_total2_p645_source_policy_reset_scout.v1",
        "created_at": utc_now(),
        "method": "p645_source_policy_reset_scout",
        "claim_status": claim_status,
        "artifacts": {"source": str(args.source), "gate": str(args.gate)},
        "summary": {
            "claim_status": claim_status,
            "validation_dataset": raw_summary,
            "best_control_below_rho_rule": max(
                control_reports,
                key=lambda r: (
                    r["direct_below_rho_verified_count"],
                    r["direct_below_rho_verified_precision"],
                    -r["selected_count"],
                ),
            ),
            "best_raw_below_rho_bucket": best_bucket(bucket_reports, "top_below_rho_buckets"),
            "best_raw_direct_verified_bucket": best_bucket(bucket_reports, "top_direct_verified_buckets"),
            "best_raw_rank3_bucket": best_bucket(bucket_reports, "top_rank3_buckets"),
        },
        "control_rule_reports": control_reports,
        "bucket_reports": bucket_reports,
        "novel_theory_routes": [
            {
                "route": "conservative_source_policy_reset",
                "status": "HYPOTHESIS",
                "mechanism": "Rank public phase/mod7, salt row-pair, right-anchor, and leaf-signature buckets before promoting a selector.",
                "failure_mode": "Fresh bursts may remain isolated and nonrecurring.",
            },
            {
                "route": "x_only_kummer_quotient",
                "status": "OPEN",
                "mechanism": "Merge sign-paired relation rows into x-only public buckets and test whether positive mass concentrates.",
                "failure_mode": "Quotienting may merge positive and negative rows without improving selector precision.",
            },
            {
                "route": "trace_norm_character_projection",
                "status": "OPEN",
                "mechanism": "Compute auxiliary source-row projections and compare histograms on P642 positives versus quiet controls.",
                "failure_mode": "Projection may not compose with EC addition or may be label-leaky.",
            },
        ],
        "honesty_boundary": [
            "Verifier labels are used only for post-run bucket evaluation, not for a claimed autonomous selector.",
            "P645 resets the public source-policy search after P643/P644 narrowed P642 to a local burst.",
            "A below-rho direct replay is a relation-event metric, not a complete faster-than-rho ECDLP algorithm.",
            "Raw bucket positives are hypotheses for the next validation block, not proven recurring structure.",
            "Promotion still requires source-generation charge, sparse linear algebra, target descent, and individual-log accounting.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claim_status": claim_status, **raw_summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
