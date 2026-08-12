#!/usr/bin/env python3
"""Scan certificate artifacts for leave-one-artifact-out factor substitution.

This is the aggregate follow-up to the held-out `[11,15]` descent signal.  For
each candidate artifact, the scout derives factor values from the bank with
that artifact removed, then checks whether the candidate's public forms recover
their toy target secrets by substituting only derived factor columns.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_factor_substitution_descent_audit as sub


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_factor_substitution_leaveout_scout_probe.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def int_value(value: Any, default: int = 0) -> int:
    return sub.int_value(value, default)


def parse_paths(raw: str | None) -> list[Path]:
    if not raw:
        return []
    return [Path(item.strip()) for item in raw.split(",") if item.strip()]


def artifact_key(path: Path) -> str:
    return str(path)


def compact_recovered(order_report: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    recovered = []
    for candidate in order_report.get("candidate_reports") or []:
        if int_value(candidate.get("verified_recoverable_form_count")) <= 0:
            continue
        forms = [
            {
                "derived_secret": form.get("derived_secret"),
                "expected_secret": form.get("expected_secret"),
                "factor_support": form.get("factor_support"),
                "form_index": form.get("form_index"),
                "q_coeff": form.get("q_coeff"),
                "rhs": form.get("rhs"),
            }
            for form in candidate.get("form_reports") or []
            if form.get("verified_matches_expected")
        ]
        recovered.append(
            {
                "candidate": candidate.get("candidate"),
                "recoverable_form_count": int_value(candidate.get("recoverable_form_count")),
                "verified_recoverable_form_count": int_value(
                    candidate.get("verified_recoverable_form_count")
                ),
                "verified_forms": forms[:8],
            }
        )
        if len(recovered) >= limit:
            break
    return recovered


def summarize_order(order: str, report: dict[str, Any], sample_limit: int) -> dict[str, Any]:
    return {
        "candidate_certificate_count": report.get("candidate_certificate_count"),
        "candidate_with_verified_recovery_count": report.get(
            "candidate_with_verified_recovery_count"
        ),
        "claim_status": report.get("claim_status"),
        "derived_factor_columns": report.get("derived_factor_columns"),
        "false_recoverable_form_count": report.get("false_recoverable_form_count"),
        "missing_factor_column_counts": report.get("missing_factor_column_counts"),
        "order": int_value(order),
        "rank": report.get("rank"),
        "recovered_samples": compact_recovered(report, sample_limit),
        "status_counts": report.get("status_counts"),
        "training_certificate_count": report.get("training_certificate_count"),
        "verified_recoverable_form_count": report.get("verified_recoverable_form_count"),
    }


def scan_artifact(
    candidate_path: Path,
    bank_certs: list[dict[str, Any]],
    candidate_certs: list[dict[str, Any]],
    sample_limit: int,
) -> dict[str, Any]:
    candidate_artifact = artifact_key(candidate_path)
    training_certs = [
        cert for cert in bank_certs if str(cert.get("_artifact")) != candidate_artifact
    ]
    orders = sorted({
        int_value(cert.get("order"))
        for cert in training_certs + candidate_certs
        if int_value(cert.get("order"))
    })
    order_audits = {
        str(order): sub.audit_order(order, training_certs, candidate_certs)
        for order in orders
    }
    verified = sum(
        int_value(report.get("verified_recoverable_form_count"))
        for report in order_audits.values()
    )
    false = sum(
        int_value(report.get("false_recoverable_form_count"))
        for report in order_audits.values()
    )
    candidate_with_recovery = sum(
        int_value(report.get("candidate_with_verified_recovery_count"))
        for report in order_audits.values()
    )
    status_counts: Counter[str] = Counter()
    for report in order_audits.values():
        for status, count in (report.get("status_counts") or {}).items():
            status_counts[str(status)] += int_value(count)
    claim_status = (
        "LEAVEOUT_FACTOR_SUBSTITUTION_SIGNAL_FOUND"
        if verified and not false
        else "LEAVEOUT_SUBSTITUTION_INCONSISTENCY_NEEDS_REVIEW"
        if false
        else "NEGATIVE_RESULT_NO_LEAVEOUT_FACTOR_SUBSTITUTION_RECOVERY"
    )
    return {
        "artifact": candidate_artifact,
        "candidate_certificate_count": len(candidate_certs),
        "candidate_with_verified_recovery_count": candidate_with_recovery,
        "claim_status": claim_status,
        "false_recoverable_form_count": false,
        "order_reports": {
            order: summarize_order(order, report, sample_limit)
            for order, report in order_audits.items()
        },
        "status_counts": dict(sorted(status_counts.items())),
        "training_certificate_count": len(training_certs),
        "verified_recoverable_form_count": verified,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bank-certificates", required=True)
    parser.add_argument("--candidate-certificates", required=True)
    parser.add_argument("--sample-limit", type=int, default=8)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    bank_paths = parse_paths(args.bank_certificates)
    candidate_paths = parse_paths(args.candidate_certificates)
    if not bank_paths:
        raise ValueError("no bank certificates supplied")
    if not candidate_paths:
        raise ValueError("no candidate certificates supplied")
    bank_certs = sub.factor_bank.load_certificates(bank_paths)
    reports = []
    for path in candidate_paths:
        candidate_certs = sub.factor_bank.load_certificates([path])
        if not candidate_certs:
            reports.append(
                {
                    "artifact": str(path),
                    "candidate_certificate_count": 0,
                    "claim_status": "NO_USABLE_CANDIDATES",
                }
            )
            continue
        reports.append(scan_artifact(path, bank_certs, candidate_certs, args.sample_limit))
    positive_reports = [
        report
        for report in reports
        if int_value(report.get("verified_recoverable_form_count")) > 0
    ]
    false_count = sum(int_value(report.get("false_recoverable_form_count")) for report in reports)
    payload = {
        "artifacts": {
            "bank_certificates": [str(path) for path in bank_paths],
            "candidate_certificates": [str(path) for path in candidate_paths],
        },
        "claim_status": (
            "LEAVEOUT_FACTOR_SUBSTITUTION_SIGNALS_FOUND"
            if positive_reports and not false_count
            else "LEAVEOUT_SUBSTITUTION_INCONSISTENCY_NEEDS_REVIEW"
            if false_count
            else "NEGATIVE_RESULT_NO_LEAVEOUT_FACTOR_SUBSTITUTION_RECOVERIES"
        ),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: factor values live in the current order-specific low-term factor-column namespace.",
            "HEURISTIC: leave-one-artifact-out recovery is a source-generation signal, not arbitrary-target descent.",
            "NO SPEEDUP CLAIM: Pollard rho remains the baseline until complete relation collection, factor derivation, target descent, and costs are accounted.",
        ],
        "reports": reports,
        "schema": "ecdlp.low_term_total2_factor_substitution_leaveout_scout.v1",
        "summary": {
            "candidate_artifact_count": len(candidate_paths),
            "candidate_certificate_count": sum(
                int_value(report.get("candidate_certificate_count")) for report in reports
            ),
            "false_recoverable_form_count": false_count,
            "positive_artifact_count": len(positive_reports),
            "target_descent_implemented": False,
            "verified_recoverable_form_count": sum(
                int_value(report.get("verified_recoverable_form_count"))
                for report in reports
            ),
        },
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
