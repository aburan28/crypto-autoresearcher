#!/usr/bin/env python3
"""P647 fresh validation for P646 quotient proxy buckets."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p643_phase0_salt203_burst_scout as p643
import low_term_total2_p646_xonly_quotient_diagnostic as p646


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p647_order9887_quotient_bucket_validation_22226_22238_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p647_quotient_bucket_validation_source_22226_22238_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p647_quotient_bucket_validation_scout_22226_22238_probe.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def feature(case: dict[str, Any]) -> dict[str, Any]:
    item = p643.feature(case)
    item["_case"] = case
    item["row_key_salts"] = list(p646.row_key_salts(case))
    return item


def is_row_salts_203_207(f: dict[str, Any]) -> bool:
    return p646.row_salt_multiset(f) == "row_salts:203,207"


def is_selector_salts_203_207(f: dict[str, Any]) -> bool:
    return p646.unordered_selector_salts(f) == "selector_salts:203,207"


def is_row_salts_203_207_anchor_mirror7(f: dict[str, Any]) -> bool:
    return is_row_salts_203_207(f) and p646.anchor_mirror(f) == "anchor_mirror:7"


def is_selector_salts_203_207_anchor_mirror7(f: dict[str, Any]) -> bool:
    return is_selector_salts_203_207(f) and p646.anchor_mirror(f) == "anchor_mirror:7"


def is_row_salts_203_208(f: dict[str, Any]) -> bool:
    return p646.row_salt_multiset(f) == "row_salts:203,208"


def is_selector_salts_203_208(f: dict[str, Any]) -> bool:
    return p646.unordered_selector_salts(f) == "selector_salts:203,208"


def is_row_salts_203_208_anchor_mirror7(f: dict[str, Any]) -> bool:
    return is_row_salts_203_208(f) and p646.anchor_mirror(f) == "anchor_mirror:7"


def is_right_salt_207(f: dict[str, Any]) -> bool:
    return p646.right_salt(f) == "right_salt:207"


RULES: list[tuple[str, str, Callable[[dict[str, Any]], bool]]] = [
    (
        "p647_row_salts_203_207",
        "P646 row-key salt multiset 203,207 proxy bucket",
        is_row_salts_203_207,
    ),
    (
        "p647_selector_salts_203_207",
        "P646 selector salt multiset 203,207 proxy bucket",
        is_selector_salts_203_207,
    ),
    (
        "p647_row_salts_203_207_anchor_mirror7",
        "P646 row-key salt multiset 203,207 with anchor mirror 7 refinement",
        is_row_salts_203_207_anchor_mirror7,
    ),
    (
        "p647_selector_salts_203_207_anchor_mirror7",
        "P646 selector salt multiset 203,207 with anchor mirror 7 refinement",
        is_selector_salts_203_207_anchor_mirror7,
    ),
    (
        "p647_row_salts_203_208",
        "P646 companion row-key salt multiset 203,208 control",
        is_row_salts_203_208,
    ),
    (
        "p647_selector_salts_203_208",
        "P646 companion selector salt multiset 203,208 control",
        is_selector_salts_203_208,
    ),
    (
        "p647_row_salts_203_208_anchor_mirror7",
        "P646 companion row-key salt multiset 203,208 with anchor mirror 7 control",
        is_row_salts_203_208_anchor_mirror7,
    ),
    (
        "p647_right_salt_207",
        "P646 broad right-salt 207 control",
        is_right_salt_207,
    ),
]


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
        "row_pair_counts": dict(Counter(str(f["row_pair"]) for f in selected)),
        "right_anchor_counts": dict(Counter(str(f["right_anchor"]) for f in selected)),
        "row_key_salt_counts": dict(Counter(",".join(str(s) for s in f.get("row_key_salts") or []) for f in selected)),
        "positive_feature_counts": dict(Counter(p643.feature_id(f) for f in below)),
        "rank3_feature_counts": dict(Counter(p643.feature_id(f) for f in rank3)),
        "selected_direct_verified_case_entries": [p643.case_entry(f) for f in verified],
        "selected_direct_below_rho_verified_case_entries": [p643.case_entry(f) for f in below],
        "selected_rank3_direct_verified_case_entries": [p643.case_entry(f) for f in rank3],
        "positive_examples": below[:24],
        "rank3_examples": rank3[:24],
    }


def report_named(reports: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    return next((r for r in reports if r["rule"] == name), None)


def determine_claim(reports: list[dict[str, Any]], raw: dict[str, Any]) -> str:
    anchor7 = report_named(reports, "p647_row_salts_203_207_anchor_mirror7")
    row203207 = report_named(reports, "p647_row_salts_203_207")
    sel203207 = report_named(reports, "p647_selector_salts_203_207")
    row203208 = report_named(reports, "p647_row_salts_203_208")
    if anchor7 and anchor7["direct_below_rho_verified_count"] and anchor7["rank3_direct_verified_count"]:
        return "P647_QUOTIENT_BUCKET_ANCHOR_MIRROR7_RANK3_BELOW_RHO_VALIDATED"
    if row203207 and row203207["direct_below_rho_verified_count"]:
        return "P647_ROW_SALTS_203_207_BELOW_RHO_VALIDATED"
    if sel203207 and sel203207["direct_below_rho_verified_count"]:
        return "P647_SELECTOR_SALTS_203_207_BELOW_RHO_VALIDATED"
    if row203208 and row203208["direct_below_rho_verified_count"]:
        return "P647_COMPANION_203_208_BELOW_RHO_POSITIVE"
    if any(r["direct_below_rho_verified_count"] for r in reports):
        return "P647_REGISTERED_PROXY_BELOW_RHO_POSITIVE"
    if any(r["rank3_direct_verified_count"] for r in reports):
        return "P647_REGISTERED_PROXY_RANK_SURFACE_POSITIVE"
    if any(r["direct_verified_count"] for r in reports):
        return "P647_REGISTERED_PROXY_ABOVE_RHO_POSITIVE"
    if raw["direct_verified_count"]:
        return "NEGATIVE_RESULT_P647_PROXY_BUCKETS_MISSED_NONQUIET_BLOCK"
    return "NEGATIVE_RESULT_P647_QUOTIENT_BUCKET_VALIDATION_QUIET_BLOCK"


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
        "schema": "ecdlp.low_term_total2_p647_quotient_bucket_validation_scout.v1",
        "created_at": utc_now(),
        "method": "p647_quotient_bucket_validation_scout",
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
            "P647 validates sign-insensitive proxy buckets, not true Kummer arithmetic.",
            "Verifier labels are used only after public proxy bucket selection.",
            "A below-rho direct replay is a relation-event metric, not a complete faster-than-rho ECDLP algorithm.",
            "Rank-3 rows are relation-bank signals, not solved sparse linear algebra.",
            "Promotion still requires source-generation charge, sparse linear algebra, target descent, and individual-log accounting.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claim_status": claim_status, **raw_summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
