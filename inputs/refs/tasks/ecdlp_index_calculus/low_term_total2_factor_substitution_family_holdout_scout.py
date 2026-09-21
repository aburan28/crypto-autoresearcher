#!/usr/bin/env python3
"""Run leave-family-out factor-substitution target-descent audits.

P313 showed leave-one-artifact factor-substitution recoveries.  This stricter
scout withholds every artifact whose candidate forms expose a support family,
derives factor values from the remaining certificate bank, and then tests only
the held-out forms in that family.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_factor_substitution_descent_audit as sub


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_factor_substitution_family_holdout_scout_probe.json"


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


def parse_families(raw: str | None) -> list[tuple[int, ...]]:
    if not raw:
        return []
    families: list[tuple[int, ...]] = []
    for chunk in raw.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        family = tuple(int(part.strip()) for part in chunk.split(",") if part.strip())
        if family:
            families.append(family)
    return families


def form_support(cert: dict[str, Any], form: dict[str, Any]) -> tuple[int, ...]:
    order = int_value(cert.get("order"))
    coeffs = [int_value(value) % order for value in form.get("coeffs") or []]
    return tuple(index for index, value in enumerate(coeffs[1:]) if value % order)


def candidate_families(candidate_certs: list[dict[str, Any]]) -> list[tuple[int, ...]]:
    counts: Counter[tuple[int, ...]] = Counter()
    for cert in candidate_certs:
        for form in cert.get("forms") or []:
            if isinstance(form, dict):
                support = form_support(cert, form)
                if support:
                    counts[support] += 1
    return [family for family, _ in counts.most_common()]


def filter_cert_to_family(cert: dict[str, Any], family: tuple[int, ...]) -> dict[str, Any] | None:
    forms = [
        form
        for form in cert.get("forms") or []
        if isinstance(form, dict) and form_support(cert, form) == family
    ]
    if not forms:
        return None
    filtered = dict(cert)
    filtered["forms"] = forms
    filtered["forms_count"] = len(forms)
    return filtered


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
        "training_unique_relation_count": report.get("training_unique_relation_count"),
        "verified_recoverable_form_count": report.get("verified_recoverable_form_count"),
    }


def audit_family(
    family: tuple[int, ...],
    bank_certs: list[dict[str, Any]],
    candidate_certs: list[dict[str, Any]],
    sample_limit: int,
) -> dict[str, Any]:
    family_candidates: list[dict[str, Any]] = []
    excluded_artifacts: set[str] = set()
    candidate_form_count = 0
    for cert in candidate_certs:
        filtered = filter_cert_to_family(cert, family)
        if filtered is None:
            continue
        family_candidates.append(filtered)
        excluded_artifacts.add(str(cert.get("_artifact")))
        candidate_form_count += len(filtered.get("forms") or [])
    training_certs = [
        cert for cert in bank_certs if str(cert.get("_artifact")) not in excluded_artifacts
    ]
    orders = sorted({
        int_value(cert.get("order"))
        for cert in training_certs + family_candidates
        if int_value(cert.get("order"))
    })
    order_audits = {
        str(order): sub.audit_order(order, training_certs, family_candidates)
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
    derived_columns_by_order: dict[str, list[int]] = {}
    for order, report in order_audits.items():
        for status, count in (report.get("status_counts") or {}).items():
            status_counts[str(status)] += int_value(count)
        derived_columns_by_order[order] = report.get("derived_factor_columns") or []
    if not family_candidates:
        claim_status = "NO_CANDIDATE_FORMS_FOR_FAMILY"
    elif false:
        claim_status = "FAMILY_HOLDOUT_SUBSTITUTION_INCONSISTENCY_NEEDS_REVIEW"
    elif verified:
        claim_status = "FAMILY_HOLDOUT_FACTOR_SUBSTITUTION_SIGNAL_FOUND"
    else:
        claim_status = "NEGATIVE_RESULT_NO_FAMILY_HOLDOUT_RECOVERY"
    return {
        "candidate_certificate_count": len(family_candidates),
        "candidate_form_count": candidate_form_count,
        "candidate_with_verified_recovery_count": candidate_with_recovery,
        "claim_status": claim_status,
        "derived_columns_by_order": derived_columns_by_order,
        "excluded_artifact_count": len(excluded_artifacts),
        "excluded_artifacts": sorted(excluded_artifacts),
        "false_recoverable_form_count": false,
        "family": list(family),
        "family_key": ",".join(str(item) for item in family),
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
    parser.add_argument("--families")
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
    candidate_certs = sub.factor_bank.load_certificates(candidate_paths)
    families = parse_families(args.families) or candidate_families(candidate_certs)
    reports = [
        audit_family(family, bank_certs, candidate_certs, args.sample_limit)
        for family in families
    ]
    false_count = sum(int_value(report.get("false_recoverable_form_count")) for report in reports)
    positive_reports = [
        report
        for report in reports
        if int_value(report.get("verified_recoverable_form_count")) > 0
    ]
    payload = {
        "artifacts": {
            "bank_certificates": [str(path) for path in bank_paths],
            "candidate_certificates": [str(path) for path in candidate_paths],
        },
        "claim_status": (
            "FAMILY_HOLDOUT_FACTOR_SUBSTITUTION_SIGNALS_FOUND"
            if positive_reports and not false_count
            else "FAMILY_HOLDOUT_SUBSTITUTION_INCONSISTENCY_NEEDS_REVIEW"
            if false_count
            else "NEGATIVE_RESULT_NO_FAMILY_HOLDOUT_SUBSTITUTION_RECOVERIES"
        ),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: factor values live in the current order-specific low-term factor-column namespace.",
            "HEURISTIC: family-held-out recovery is a stricter source-generation signal, not arbitrary-target descent.",
            "NO SPEEDUP CLAIM: Pollard rho remains the baseline until relation generation, factor derivation, target descent, and costs are accounted end to end.",
        ],
        "reports": reports,
        "schema": "ecdlp.low_term_total2_factor_substitution_family_holdout_scout.v1",
        "summary": {
            "candidate_certificate_count": sum(
                int_value(report.get("candidate_certificate_count")) for report in reports
            ),
            "candidate_form_count": sum(
                int_value(report.get("candidate_form_count")) for report in reports
            ),
            "family_count": len(reports),
            "false_recoverable_form_count": false_count,
            "positive_family_count": len(positive_reports),
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
