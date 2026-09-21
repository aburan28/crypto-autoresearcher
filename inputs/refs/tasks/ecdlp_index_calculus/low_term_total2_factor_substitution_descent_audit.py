#!/usr/bin/env python3
"""Audit bounded target descent by substituting derived factor logs.

The relation-bank audit can derive some shared factor-base variables from
target-eliminated rows, but full rank is not necessary for a bounded individual
log if a fresh target relation only touches the derived factor columns.  This
script derives factor values from a training certificate set, then checks
whether held-out candidate certificate forms solve their target secret after
substitution.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_factor_substitution_descent_audit_probe.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def parse_paths(raw: str | None) -> list[Path]:
    if not raw:
        return []
    return [Path(item.strip()) for item in raw.split(",") if item.strip()]


def int_value(value: Any, default: int = 0) -> int:
    return factor_bank.int_value(value, default)


def selected_info(cert: dict[str, Any]) -> dict[str, Any]:
    selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
    return {
        "artifact": cert.get("_artifact"),
        "artifact_offset": int_value(cert.get("_artifact_offset")),
        "certificate_index": int_value(cert.get("_global_index")),
        "clause": cert.get("clause") or selected.get("clause"),
        "direct_ops_over_rho": cert.get("direct_ops_over_rho"),
        "expected_secret": int_value(cert.get("expected_secret")),
        "forms_count": int_value(cert.get("forms_count")),
        "order": int_value(cert.get("order")),
        "public_key_verified": cert.get("public_key_verified"),
        "rowspace_derives_expected_secret": cert.get("rowspace_derives_expected_secret"),
        "target": selected.get("target"),
        "top_k": int_value(selected.get("top_k")),
        "transfer_index": int_value(selected.get("transfer_index")),
        "window": cert.get("window"),
    }


def factor_count_for(certs: list[dict[str, Any]], order: int) -> int:
    factor_count = 0
    for cert in certs:
        if int_value(cert.get("order")) != order:
            continue
        for form in cert.get("forms") or []:
            if not isinstance(form, dict):
                continue
            factor_count = max(factor_count, max(0, len(form.get("coeffs") or []) - 1))
    return factor_count


def derive_factor_values(
    training_certs: list[dict[str, Any]],
    order: int,
    factor_count: int,
) -> dict[str, Any]:
    rows_by_key: dict[tuple[tuple[int, ...], int], dict[str, Any]] = {}
    relation_count = 0
    for cert in training_certs:
        if int_value(cert.get("order")) != order:
            continue
        for relation in factor_bank.target_eliminated_rows(cert):
            if relation.get("relation_status") != "TARGET_ELIMINATED_FACTOR_RELATION":
                continue
            relation_count += 1
            coeffs = factor_bank.pad(
                [int_value(value) % order for value in relation.get("canonical_coeffs") or []],
                factor_count,
            )
            rhs = int_value(relation.get("canonical_rhs")) % order
            rows_by_key.setdefault(
                (tuple(coeffs), rhs),
                {
                    "canonical_coeffs": coeffs,
                    "canonical_rhs": rhs,
                    "multiplicity": 0,
                },
            )
            rows_by_key[(tuple(coeffs), rhs)]["multiplicity"] += 1
    unique_rows = list(rows_by_key.values())
    matrix = [row["canonical_coeffs"] for row in unique_rows]
    rhs_values = [int_value(row["canonical_rhs"]) % order for row in unique_rows]
    factor_values: dict[int, dict[str, Any]] = {}
    for index in range(factor_count):
        derived = factor_bank.derive_variable(matrix, rhs_values, index, order)
        if derived.get("derivable"):
            factor_values[index] = {
                "combination_row_count": int_value(derived.get("combination_row_count")),
                "factor_variable": f"F:{order}:column={index}",
                "value": int_value(derived.get("value")) % order,
            }
    rank = factor_bank.rank_mod(matrix, order)
    augmented_rank = factor_bank.rank_mod(
        [row + [rhs_values[index]] for index, row in enumerate(matrix)],
        order,
    )
    return {
        "augmented_rank": augmented_rank,
        "factor_values": factor_values,
        "matrix_consistent": augmented_rank == rank,
        "rank": rank,
        "relation_count": relation_count,
        "unique_relation_count": len(unique_rows),
    }


def support(coeffs: list[int], order: int) -> list[int]:
    return [idx for idx, value in enumerate(coeffs) if value % order]


def audit_candidate_form(
    cert: dict[str, Any],
    form: dict[str, Any],
    form_index: int,
    order: int,
    factor_count: int,
    factor_values: dict[int, dict[str, Any]],
) -> dict[str, Any]:
    q_coeff, factor_coeffs, rhs = factor_bank.form_parts(form, order, factor_count)
    form_support = support(factor_coeffs, order)
    missing = [idx for idx in form_support if idx not in factor_values]
    if q_coeff % order == 0:
        status = "Q_COEFF_ZERO"
        recovered = None
    elif missing:
        status = "MISSING_FACTOR_VALUES"
        recovered = None
    else:
        known_sum = sum(
            factor_coeffs[idx] * int_value(factor_values[idx].get("value"))
            for idx in form_support
        ) % order
        recovered = ((rhs - known_sum) * pow(q_coeff % order, -1, order)) % order
        status = "TARGET_RECOVERED_BY_FACTOR_SUBSTITUTION"
    expected = int_value(cert.get("expected_secret"))
    return {
        "derived_secret": recovered,
        "expected_secret": expected,
        "factor_support": form_support,
        "form_index": form_index,
        "missing_factor_columns": missing,
        "q_coeff": q_coeff % order,
        "rhs": rhs % order,
        "status": status,
        "verified_matches_expected": bool(recovered is not None and recovered == expected),
    }


def audit_order(
    order: int,
    training_certs: list[dict[str, Any]],
    candidate_certs: list[dict[str, Any]],
) -> dict[str, Any]:
    order_training = [cert for cert in training_certs if int_value(cert.get("order")) == order]
    order_candidates = [cert for cert in candidate_certs if int_value(cert.get("order")) == order]
    factor_count = factor_count_for(order_training + order_candidates, order)
    derivation = derive_factor_values(order_training, order, factor_count)
    factor_values = derivation["factor_values"]
    status_counts: Counter[str] = Counter()
    missing_counts: Counter[str] = Counter()
    recovered_candidates: dict[int, dict[str, Any]] = {}
    candidate_reports = []
    for cert in order_candidates:
        cert_info = selected_info(cert)
        form_reports = []
        for form_index, form in enumerate(cert.get("forms") or []):
            if not isinstance(form, dict):
                continue
            report = audit_candidate_form(
                cert,
                form,
                form_index,
                order,
                factor_count,
                factor_values,
            )
            status_counts[report["status"]] += 1
            for column in report.get("missing_factor_columns") or []:
                missing_counts[str(column)] += 1
            if report["verified_matches_expected"]:
                recovered_candidates[int_value(cert.get("_global_index"))] = cert_info
            form_reports.append(report)
        candidate_reports.append(
            {
                "candidate": cert_info,
                "form_reports": form_reports,
                "recoverable_form_count": sum(
                    1 for item in form_reports if item["status"] == "TARGET_RECOVERED_BY_FACTOR_SUBSTITUTION"
                ),
                "verified_recoverable_form_count": sum(
                    1 for item in form_reports if item["verified_matches_expected"]
                ),
            }
        )
    verified_recoveries = sum(
        item["verified_recoverable_form_count"] for item in candidate_reports
    )
    false_recoveries = sum(
        1
        for item in candidate_reports
        for form in item["form_reports"]
        if form["status"] == "TARGET_RECOVERED_BY_FACTOR_SUBSTITUTION"
        and not form["verified_matches_expected"]
    )
    return {
        "candidate_certificate_count": len(order_candidates),
        "candidate_reports": candidate_reports[:50],
        "candidate_with_verified_recovery_count": len(recovered_candidates),
        "claim_status": (
            "FACTOR_SUBSTITUTION_TARGET_DESCENT_SIGNAL_FOUND"
            if verified_recoveries and not false_recoveries
            else "TARGET_SUBSTITUTION_INCONSISTENCY_NEEDS_REVIEW"
            if false_recoveries
            else "NEGATIVE_RESULT_NO_FACTOR_SUBSTITUTION_TARGET_RECOVERY"
        ),
        "derived_factor_columns": sorted(factor_values),
        "derived_factor_values": [factor_values[idx] for idx in sorted(factor_values)],
        "factor_column_count": factor_count,
        "false_recoverable_form_count": false_recoveries,
        "matrix_consistent": derivation["matrix_consistent"],
        "missing_factor_column_counts": dict(sorted(missing_counts.items(), key=lambda item: int(item[0]))),
        "order": order,
        "rank": derivation["rank"],
        "status_counts": dict(sorted(status_counts.items())),
        "training_certificate_count": len(order_training),
        "training_relation_count": derivation["relation_count"],
        "training_unique_relation_count": derivation["unique_relation_count"],
        "verified_recoverable_form_count": verified_recoveries,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-certificates", required=True)
    parser.add_argument("--candidate-certificates", required=True)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    training_paths = parse_paths(args.training_certificates)
    candidate_paths = parse_paths(args.candidate_certificates)
    if not training_paths:
        raise ValueError("no training certificates supplied")
    if not candidate_paths:
        raise ValueError("no candidate certificates supplied")
    training_certs = factor_bank.load_certificates(training_paths)
    candidate_certs = factor_bank.load_certificates(candidate_paths)
    orders = sorted({
        int_value(cert.get("order"))
        for cert in training_certs + candidate_certs
        if int_value(cert.get("order"))
    })
    order_audits = {
        str(order): audit_order(order, training_certs, candidate_certs)
        for order in orders
    }
    total_verified = sum(
        int_value(audit.get("verified_recoverable_form_count"))
        for audit in order_audits.values()
    )
    total_false = sum(
        int_value(audit.get("false_recoverable_form_count"))
        for audit in order_audits.values()
    )
    payload = {
        "artifacts": {
            "candidate_certificates": [str(path) for path in candidate_paths],
            "training_certificates": [str(path) for path in training_paths],
        },
        "claim_status": (
            "FACTOR_SUBSTITUTION_TARGET_DESCENT_SIGNAL_FOUND"
            if total_verified and not total_false
            else "TARGET_SUBSTITUTION_INCONSISTENCY_NEEDS_REVIEW"
            if total_false
            else "NEGATIVE_RESULT_NO_FACTOR_SUBSTITUTION_TARGET_RECOVERY"
        ),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: factor values live in the current order-specific low-term factor-column namespace.",
            "HEURISTIC: a held-out factor-substitution recovery is a bounded target-descent signal, not a complete arbitrary-target descent algorithm.",
            "NO SPEEDUP CLAIM: Pollard rho remains the baseline until relation generation, linear algebra, target descent, and costs are accounted end to end.",
        ],
        "order_audits": order_audits,
        "schema": "ecdlp.low_term_total2_factor_substitution_descent_audit.v1",
        "summary": {
            "candidate_certificate_count": len(candidate_certs),
            "false_recoverable_form_count": total_false,
            "order_count": len(order_audits),
            "target_descent_implemented": False,
            "training_certificate_count": len(training_certs),
            "verified_recoverable_form_count": total_verified,
        },
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
