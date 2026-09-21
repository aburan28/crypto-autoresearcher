#!/usr/bin/env python3
"""P704 fresh-surface transfer audit for P701-derived factor values.

P703 shows that P701 factor values explain same-surface held-out P659 forms.
This audit freezes those factor values and substitutes endpoint forms from
other available P699 surfaces without adding those forms' factor-eliminated rows
to the training bank.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any

import low_term_total2_p693_endpoint_column_source_support_scout as p693
import low_term_total2_p697_endpoint_event_factor_rank_audit as p697
import low_term_total2_p699_public_minimal_endpoint_selector_persistence_audit as p699
import low_term_total2_p701_completion_form_reuse_audit as p701
import low_term_total2_p702_factor_substitution_target_verification as p702


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_p704_fresh_surface_factor_value_transfer_probe.json"
TRAINING_SURFACE = "P659_adjacent"
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


def parse_surface(raw: str) -> tuple[str, Path, Path]:
    parts = raw.split("|")
    if len(parts) != 3:
        raise ValueError("--surface must look like NAME|SOURCE|PRODUCT")
    return parts[0], Path(parts[1]), Path(parts[2])


def candidate_surfaces(args: argparse.Namespace) -> list[tuple[str, Path, Path]]:
    surfaces = [parse_surface(raw) for raw in args.surface] if args.surface else list(p699.DEFAULT_SURFACES)
    return [
        (name, source, product)
        for name, source, product in surfaces
        if name != TRAINING_SURFACE and source.exists() and product.exists()
    ]


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


def surface_report(
    args: argparse.Namespace,
    surface_name: str,
    source: Path,
    product: Path,
    factor_count: int,
    factor_values: dict[int, dict[str, Any]],
    priority_columns: set[int],
) -> dict[str, Any]:
    verifier, surface_meta, records = p699.collect_surface_records(args, source, product, priority_columns)
    candidate_records = [
        record for record in records if int_value(record.get("q_coeff")) % ORDER
    ]
    substitution_reports = [
        p702.substitute_record(verifier, record, index, factor_count, factor_values)
        for index, record in enumerate(candidate_records)
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
    hidden_secret_counts: Counter[str] = Counter(
        str(report["hidden_secret"])
        for report in substitution_reports
        if report.get("hidden_secret") is not None
    )
    return {
        "candidate_direct_cost_stats_over_rho": cost_stats(candidate_records),
        "candidate_form_count": len(candidate_records),
        "claim_status": (
            "FRESH_SURFACE_SUBSTITUTION_VERIFIES"
            if verified_secret_counts and not false_public_secret_count
            else "FRESH_SURFACE_SUBSTITUTION_MIXED"
            if verified_secret_counts and false_public_secret_count
            else "NEGATIVE_RESULT_FRESH_SURFACE_SUBSTITUTION_NO_PUBLIC_VERIFY"
            if status_counts["TARGET_RECOVERED_BY_FACTOR_SUBSTITUTION"]
            else "NEGATIVE_RESULT_FRESH_SURFACE_NO_RECOVERABLE_FORMS"
        ),
        "false_public_secret_count": false_public_secret_count,
        "hidden_secret_counts": dict(sorted(hidden_secret_counts.items(), key=lambda item: int(item[0]))),
        "recoverable_form_count": status_counts["TARGET_RECOVERED_BY_FACTOR_SUBSTITUTION"],
        "schema": "ecdlp.low_term_total2_p704.surface_report.v1",
        "secret_counts": {
            "derived": dict(sorted(derived_secret_counts.items(), key=lambda item: int(item[0]))),
            "public_key_verified": dict(sorted(verified_secret_counts.items(), key=lambda item: int(item[0]))),
        },
        "source": str(source),
        "status_counts": dict(sorted(status_counts.items())),
        "substitution_report_samples": substitution_reports[: args.sample_limit],
        "surface_meta": surface_meta,
        "surface_name": surface_name,
        "verified_form_count": sum(1 for report in substitution_reports if report.get("public_key_verified")),
    }


def determine_claim(summary: dict[str, Any]) -> str:
    if summary["verified_surface_count"] and not summary["false_public_secret_count"]:
        return "P704_FRESH_SURFACE_FACTOR_VALUE_TRANSFER_POSITIVE"
    if summary["verified_surface_count"] and summary["false_public_secret_count"]:
        return "P704_FRESH_SURFACE_FACTOR_VALUE_TRANSFER_MIXED"
    if summary["recoverable_form_count"]:
        return "NEGATIVE_RESULT_P704_P701_FACTOR_VALUES_DO_NOT_TRANSFER_TO_TESTED_SURFACES"
    return "NEGATIVE_RESULT_P704_NO_FRESH_SURFACE_RECOVERABLE_FORMS"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    priority_columns = p693.parse_columns(args.priority_columns)
    reconstructed = p702.reconstruct_p701_row_union(args)
    verifier = reconstructed["verifier"]
    replay_records = reconstructed["replay"]["replayed_records"]
    base, excluded_candidates, bank_meta = p697.base_bank(
        [Path(path) for path in (args.certificate or [str(path) for path in p697.p690.DEFAULT_CERTIFICATE_PATHS])]
    )
    base_state = p697.bank_state(base)
    union = p697.union_derive(verifier, replay_records)
    endpoint_cert = p697.pseudo_certificate(
        "p704_p701_row_union_training_endpoint",
        replay_records,
        args.target,
        union,
    )
    augmented_state = p697.bank_state(base + [endpoint_cert])
    factor_values = p702.factor_values_from_state(augmented_state)
    reports = [
        surface_report(
            args,
            surface_name,
            source,
            product,
            int_value(augmented_state.get("factor_count")),
            factor_values,
            priority_columns,
        )
        for surface_name, source, product in candidate_surfaces(args)
    ]
    recoverable = sum(int_value(report.get("recoverable_form_count")) for report in reports)
    verified = sum(int_value(report.get("verified_form_count")) for report in reports)
    false_public = sum(int_value(report.get("false_public_secret_count")) for report in reports)
    summary = {
        "augmented_missing_columns": augmented_state["missing_columns"],
        "augmented_rank": int_value(augmented_state["rank"]),
        "base_missing_columns": base_state["missing_columns"],
        "base_rank": int_value(base_state["rank"]),
        "candidate_form_count": sum(int_value(report.get("candidate_form_count")) for report in reports),
        "derived_factor_column_count": len(factor_values),
        "excluded_p690_candidate_count": len(excluded_candidates),
        "factor_count": int_value(augmented_state.get("factor_count")),
        "false_public_secret_count": false_public,
        "p701_training_charge_over_rho": float_value(reconstructed["replay"].get("row_replay_charge_over_rho")),
        "recoverable_form_count": recoverable,
        "surface_count": len(reports),
        "verified_form_count": verified,
        "verified_surface_count": sum(1 for report in reports if int_value(report.get("verified_form_count"))),
    }
    claim_status = determine_claim(summary)
    return {
        "artifacts": {
            "base_certificates": bank_meta["paths"],
            "p701": str(Path(args.p701)),
            "training_product": str(Path(args.product)),
            "training_source": str(Path(args.source)),
        },
        "claim_status": claim_status,
        "created_at": p697.p696.now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: transfer is tested only across existing P699 order-9887 endpoint surfaces.",
            "HEURISTIC: a negative result here scopes the current factor-value namespace; it does not rule out retraining or a different representation.",
            "NO IMPOSSIBILITY CLAIM: this is a surface-transfer test, not a theorem about prime-field ECDLP.",
        ],
        "method": "p704_fresh_surface_factor_value_transfer",
        "parameters": {
            "candidate_surfaces": [report["surface_name"] for report in reports],
            "priority_columns": sorted(priority_columns),
            "target": args.target,
            "training_surface": TRAINING_SURFACE,
        },
        "schema": "ecdlp.low_term_total2_p704_fresh_surface_factor_value_transfer.v1",
        "summary": summary,
        "surface_reports": reports,
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
    parser.add_argument("--surface", action="append", default=[], help="Candidate surface NAME|SOURCE|PRODUCT.")
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
    print(json.dumps({"surface_claims": {
        report["surface_name"]: report["claim_status"] for report in payload["surface_reports"]
    }}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
