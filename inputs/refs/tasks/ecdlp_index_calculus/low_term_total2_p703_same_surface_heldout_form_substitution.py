#!/usr/bin/env python3
"""P703 same-surface held-out endpoint-form substitution audit.

P702 verifies the P701 closure forms by factor substitution.  This stricter
same-surface audit excludes every non-training endpoint form from factor-value
derivation, then checks whether those held-out forms substitute to the same
public-key-verified target secret under the P701-derived factor values.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any

import low_term_total2_p697_endpoint_event_factor_rank_audit as p697
import low_term_total2_p701_completion_form_reuse_audit as p701
import low_term_total2_p702_factor_substitution_target_verification as p702
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_p703_same_surface_heldout_form_substitution_probe.json"
ORDER = p697.ORDER


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def support_key(values: list[int]) -> str:
    return ",".join(str(value) for value in values)


def cost_stats(records: list[dict[str, Any]]) -> dict[str, Any]:
    costs = [
        float_value(record.get("direct_ops_over_rho"))
        for record in records
        if record.get("direct_ops_over_rho") is not None
    ]
    if not costs:
        return {"count": 0, "max": None, "mean": None, "min": None}
    return {
        "count": len(costs),
        "max": round(max(costs), 8),
        "mean": round(mean(costs), 8),
        "min": round(min(costs), 8),
    }


def determine_claim(summary: dict[str, Any]) -> str:
    if (
        summary["verified_heldout_form_count"] == summary["heldout_form_count"]
        and summary["heldout_form_count"]
        and not summary["false_public_secret_count"]
        and summary["unique_verified_secret_count"] == 1
    ):
        return "P703_SAME_SURFACE_HELDOUT_FORMS_ALL_VERIFY_WITH_P701_FACTOR_VALUES"
    if summary["verified_heldout_form_count"] and not summary["false_public_secret_count"]:
        return "P703_SAME_SURFACE_HELDOUT_FORMS_PARTIALLY_VERIFY_WITH_P701_FACTOR_VALUES"
    if summary["false_public_secret_count"]:
        return "NEGATIVE_RESULT_P703_HELDOUT_FORM_SUBSTITUTION_INCONSISTENT"
    return "NEGATIVE_RESULT_P703_NO_HELDOUT_FORM_SUBSTITUTION_RECOVERY"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    reconstructed = p702.reconstruct_p701_row_union(args)
    verifier = reconstructed["verifier"]
    replay = reconstructed["replay"]
    replay_records = replay["replayed_records"]
    base, excluded_candidates, bank_meta = p697.base_bank(
        [Path(path) for path in (args.certificate or [str(path) for path in p697.p690.DEFAULT_CERTIFICATE_PATHS])]
    )
    base_state = p697.bank_state(base)
    union = p697.union_derive(verifier, replay_records)
    endpoint_cert = p697.pseudo_certificate(
        "p703_p701_row_union_training_endpoint",
        replay_records,
        args.target,
        union,
    )
    augmented_state = p697.bank_state(base + [endpoint_cert])
    factor_values = p702.factor_values_from_state(augmented_state)
    training_keys = {p701.form_key(record) for record in replay_records}
    heldout_records = [
        record
        for record in reconstructed["surface_records"]
        if p701.form_key(record) not in training_keys and int_value(record.get("q_coeff")) % ORDER
    ]
    substitution_reports = [
        p702.substitute_record(
            verifier,
            record,
            index,
            int_value(augmented_state.get("factor_count")),
            factor_values,
        )
        for index, record in enumerate(heldout_records)
    ]
    status_counts: Counter[str] = Counter(report["status"] for report in substitution_reports)
    derived_secret_counts: Counter[str] = Counter(
        str(report["derived_secret"])
        for report in substitution_reports
        if report.get("derived_secret") is not None
    )
    verified_secret_counts: Counter[str] = Counter(
        str(report["derived_secret"])
        for report in substitution_reports
        if report.get("derived_secret") is not None and report.get("public_key_verified")
    )
    false_public_secret_count = sum(
        1
        for report in substitution_reports
        if report.get("derived_secret") is not None and not report.get("public_key_verified")
    )
    verified_support_counts: Counter[str] = Counter(
        support_key(report["factor_support"])
        for report in substitution_reports
        if report.get("public_key_verified")
    )
    all_support_counts: Counter[str] = Counter(
        support_key(report["factor_support"]) for report in substitution_reports
    )
    summary = {
        "augmented_missing_columns": augmented_state["missing_columns"],
        "augmented_rank": int_value(augmented_state["rank"]),
        "base_missing_columns": base_state["missing_columns"],
        "base_rank": int_value(base_state["rank"]),
        "derived_factor_column_count": len(factor_values),
        "excluded_p690_candidate_count": len(excluded_candidates),
        "factor_count": int_value(augmented_state.get("factor_count")),
        "false_public_secret_count": false_public_secret_count,
        "heldout_direct_cost_stats_over_rho": cost_stats(heldout_records),
        "heldout_form_count": len(heldout_records),
        "p701_training_charge_over_rho": float_value(replay.get("row_replay_charge_over_rho")),
        "p701_training_form_count": len(replay_records),
        "recoverable_heldout_form_count": status_counts["TARGET_RECOVERED_BY_FACTOR_SUBSTITUTION"],
        "surface_endpoint_form_count": int_value(reconstructed["surface_record_count"]),
        "unique_derived_secret_count": len(derived_secret_counts),
        "unique_verified_secret_count": len(verified_secret_counts),
        "verified_heldout_form_count": sum(
            1 for report in substitution_reports if report.get("public_key_verified")
        ),
    }
    claim_status = determine_claim(summary)
    return {
        "artifacts": {
            "base_certificates": bank_meta["paths"],
            "p701": str(Path(args.p701)),
            "product": str(Path(args.product)),
            "source": str(Path(args.source)),
        },
        "claim_status": claim_status,
        "created_at": p697.p696.now_iso(),
        "heldout_reports": substitution_reports,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: held-out forms are from the same reconstructed P659 endpoint surface.",
            "HEURISTIC: this reduces same-form leakage concern but is not a fresh-target or arbitrary-target descent test.",
            "NO END-TO-END SPEEDUP CLAIM: candidate target-relation generation cost and scaling remain open.",
        ],
        "method": "p703_same_surface_heldout_form_substitution",
        "parameters": {
            "completion_form_index": reconstructed["completion_form_index"],
            "priority_columns": sorted(reconstructed["priority_columns"]),
            "target": args.target,
            "training_stage_form_indices": [
                int_value(record.get("_endpoint_form_index"))
                for record in reconstructed["stage_records"]
            ],
        },
        "schema": "ecdlp.low_term_total2_p703_same_surface_heldout_form_substitution.v1",
        "secret_counts": {
            "derived": dict(sorted(derived_secret_counts.items(), key=lambda item: int(item[0]))),
            "public_key_verified": dict(sorted(verified_secret_counts.items(), key=lambda item: int(item[0]))),
        },
        "status_counts": dict(sorted(status_counts.items())),
        "summary": summary,
        "support_counts": {
            "all": dict(sorted(all_support_counts.items())),
            "public_key_verified": dict(sorted(verified_support_counts.items())),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=str(p701.DEFAULT_SOURCE))
    parser.add_argument("--product", default=str(p701.DEFAULT_PRODUCT))
    parser.add_argument("--target", default="67.a1@9803")
    parser.add_argument("--priority-columns", default="0,15")
    parser.add_argument("--p698", default=str(p701.DEFAULT_P698))
    parser.add_argument("--p701", default=str(p702.DEFAULT_P701))
    parser.add_argument("--completion-form-index", type=int, default=None)
    parser.add_argument("--certificate", action="append", default=None, help="Base certificate artifact to include.")
    parser.add_argument("--max-cases", type=int, default=0)
    parser.add_argument("--max-endpoint-leaves", type=int, default=0)
    parser.add_argument("--sample-limit", type=int, default=12)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    print(json.dumps({"claim_status": payload["claim_status"], "summary": payload["summary"]}, indent=2, sort_keys=True))
    print(json.dumps({"secret_counts": payload["secret_counts"], "status_counts": payload["status_counts"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
