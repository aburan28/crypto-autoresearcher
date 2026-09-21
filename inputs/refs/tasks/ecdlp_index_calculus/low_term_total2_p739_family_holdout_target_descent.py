#!/usr/bin/env python3
"""P739 family-holdout target-descent audit over P738 certificates."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Any, Callable

import low_term_total2_factor_substitution_descent_audit as substitution


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P738 = STATE_DIR / "low_term_total2_p738_modular_coefficient_descent_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p739_family_holdout_target_descent_probe.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def int_value(value: Any, default: int = 0) -> int:
    return substitution.int_value(value, default)


def stat(values: list[int | float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "median": None, "min": None}
    return {
        "count": len(values),
        "max": max(values),
        "mean": round(mean(values), 8),
        "median": median(values),
        "min": min(values),
    }


def selected(cert: dict[str, Any]) -> dict[str, Any]:
    return cert.get("selected") if isinstance(cert.get("selected"), dict) else {}


def cert_index(cert: dict[str, Any]) -> int:
    return int_value(cert.get("_global_index"), int_value(cert.get("_artifact_offset")))


def transfer_index(cert: dict[str, Any]) -> int:
    return int_value(selected(cert).get("transfer_index"))


def target(cert: dict[str, Any]) -> str:
    return str(selected(cert).get("target") or "")


def source_policy(cert: dict[str, Any]) -> str:
    return str(selected(cert).get("source_policy") or "")


def row_salts(cert: dict[str, Any]) -> set[str]:
    salts: set[str] = set()
    for key in selected(cert).get("row_keys") or []:
        match = re.search(r":salt([^:]+)$", str(key))
        if match:
            salts.add(match.group(1))
    return salts


def leaf_indices(cert: dict[str, Any]) -> set[int]:
    leaves: set[int] = set()
    for key in selected(cert).get("row_leaf_keys") or []:
        match = re.search(r":leaf(\d+)$", str(key))
        if match:
            leaves.add(int(match.group(1)))
    return leaves


def support_for_form(form: dict[str, Any], order: int) -> tuple[int, ...]:
    coeffs = [int_value(value) % order for value in form.get("coeffs") or []]
    return tuple(index for index, coeff in enumerate(coeffs[1:]) if coeff % order)


def factor_supports(cert: dict[str, Any], order: int) -> set[tuple[int, ...]]:
    return {
        support_for_form(form, order)
        for form in cert.get("forms") or []
        if isinstance(form, dict)
    }


def factor_support_columns(cert: dict[str, Any], order: int) -> set[int]:
    return {column for support in factor_supports(cert, order) for column in support}


def annotate_certificates(p738: dict[str, Any]) -> list[dict[str, Any]]:
    certificates = []
    for index, cert in enumerate(p738.get("certificates") or []):
        if not isinstance(cert, dict):
            continue
        item = dict(cert)
        item["_artifact"] = item.get("_artifact") or str(DEFAULT_P738)
        item["_artifact_offset"] = int_value(item.get("_artifact_offset"), index)
        item["_global_index"] = int_value(item.get("_global_index"), index)
        certificates.append(item)
    return certificates


HoldoutFn = Callable[[dict[str, Any], list[dict[str, Any]], int], tuple[list[dict[str, Any]], dict[str, Any]]]


def certificate_leave_one_out(candidate: dict[str, Any], certs: list[dict[str, Any]], order: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    idx = cert_index(candidate)
    return [cert for cert in certs if cert_index(cert) != idx], {"held_out_certificate": idx}


def source_policy_holdout(candidate: dict[str, Any], certs: list[dict[str, Any]], order: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    policy = source_policy(candidate)
    return (
        [cert for cert in certs if source_policy(cert) != policy],
        {"held_out_source_policy": policy},
    )


def row_salt_holdout(candidate: dict[str, Any], certs: list[dict[str, Any]], order: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    salts = row_salts(candidate)
    return (
        [cert for cert in certs if cert_index(cert) != cert_index(candidate) and not (row_salts(cert) & salts)],
        {"held_out_row_salts": sorted(salts)},
    )


def leaf_index_holdout(candidate: dict[str, Any], certs: list[dict[str, Any]], order: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    leaves = leaf_indices(candidate)
    return (
        [cert for cert in certs if cert_index(cert) != cert_index(candidate) and not (leaf_indices(cert) & leaves)],
        {"held_out_leaf_indices": sorted(leaves)},
    )


def factor_support_holdout(candidate: dict[str, Any], certs: list[dict[str, Any]], order: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    supports = factor_supports(candidate, order)
    return (
        [
            cert
            for cert in certs
            if cert_index(cert) != cert_index(candidate)
            and factor_supports(cert, order).isdisjoint(supports)
        ],
        {"held_out_factor_supports": [list(support) for support in sorted(supports)]},
    )


def factor_support_overlap_holdout(candidate: dict[str, Any], certs: list[dict[str, Any]], order: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    columns = factor_support_columns(candidate, order)
    return (
        [
            cert
            for cert in certs
            if cert_index(cert) != cert_index(candidate)
            and factor_support_columns(cert, order).isdisjoint(columns)
        ],
        {"held_out_factor_support_columns": sorted(columns)},
    )


def forward_only_prior_transfers(candidate: dict[str, Any], certs: list[dict[str, Any]], order: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    transfer = transfer_index(candidate)
    return (
        [cert for cert in certs if transfer_index(cert) < transfer],
        {"candidate_transfer_index": transfer},
    )


def disjoint_target_holdout(candidate: dict[str, Any], certs: list[dict[str, Any]], order: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    candidate_target = target(candidate)
    return (
        [cert for cert in certs if target(cert) != candidate_target],
        {"held_out_target": candidate_target},
    )


HOLDOUTS: dict[str, HoldoutFn] = {
    "certificate_leave_one_out": certificate_leave_one_out,
    "source_policy_holdout": source_policy_holdout,
    "row_salt_holdout": row_salt_holdout,
    "leaf_index_holdout": leaf_index_holdout,
    "factor_support_holdout": factor_support_holdout,
    "factor_support_overlap_holdout": factor_support_overlap_holdout,
    "forward_only_prior_transfers": forward_only_prior_transfers,
    "disjoint_target_holdout": disjoint_target_holdout,
}


def audit_candidate(
    candidate: dict[str, Any],
    training: list[dict[str, Any]],
    order: int,
    factor_count: int,
) -> dict[str, Any]:
    derivation = substitution.derive_factor_values(training, order, factor_count)
    factor_values = derivation["factor_values"]
    reports = []
    verified = 0
    false = 0
    for form_index, form in enumerate(candidate.get("forms") or []):
        if not isinstance(form, dict):
            continue
        report = substitution.audit_candidate_form(candidate, form, form_index, order, factor_count, factor_values)
        if report.get("verified_matches_expected"):
            verified += 1
        elif report.get("status") == "TARGET_RECOVERED_BY_FACTOR_SUBSTITUTION":
            false += 1
        reports.append(report)
    return {
        "derived_factor_column_count": len(factor_values),
        "factor_rank": derivation["rank"],
        "false_recoverable_form_count": false,
        "form_reports": reports,
        "matrix_consistent": derivation["matrix_consistent"],
        "training_certificate_count": len(training),
        "training_unique_relation_count": derivation["unique_relation_count"],
        "verified_recoverable_form_count": verified,
    }


def audit_holdout_axis(
    axis: str,
    holdout_fn: HoldoutFn,
    order: int,
    certs: list[dict[str, Any]],
) -> dict[str, Any]:
    factor_count = substitution.factor_count_for(certs, order)
    status_counts: Counter[str] = Counter()
    missing_counts: Counter[str] = Counter()
    verified_forms = 0
    false_forms = 0
    verified_candidates = 0
    false_candidates = 0
    untestable_candidates = 0
    training_counts: list[int] = []
    ranks: list[int] = []
    derived_counts: list[int] = []
    samples = []
    for candidate in certs:
        training, holdout_detail = holdout_fn(candidate, certs, order)
        if not training:
            untestable_candidates += 1
            if len(samples) < 12:
                samples.append(
                    {
                        "certificate_index": cert_index(candidate),
                        "holdout_detail": holdout_detail,
                        "status": "UNTESTABLE_NO_TRAINING_CERTIFICATES",
                        "target": target(candidate),
                        "transfer_index": transfer_index(candidate),
                    }
                )
            continue
        audited = audit_candidate(candidate, training, order, factor_count)
        training_counts.append(int_value(audited.get("training_certificate_count")))
        ranks.append(int_value(audited.get("factor_rank")))
        derived_counts.append(int_value(audited.get("derived_factor_column_count")))
        candidate_verified = int_value(audited.get("verified_recoverable_form_count"))
        candidate_false = int_value(audited.get("false_recoverable_form_count"))
        verified_forms += candidate_verified
        false_forms += candidate_false
        if candidate_verified:
            verified_candidates += 1
        if candidate_false:
            false_candidates += 1
        for report in audited.get("form_reports") or []:
            status_counts[str(report.get("status"))] += 1
            for column in report.get("missing_factor_columns") or []:
                missing_counts[str(column)] += 1
        if candidate_verified or candidate_false or len(samples) < 12:
            samples.append(
                {
                    "certificate_index": cert_index(candidate),
                    "derived_factor_column_count": audited.get("derived_factor_column_count"),
                    "factor_rank": audited.get("factor_rank"),
                    "false_recoverable_form_count": candidate_false,
                    "form_reports": [
                        report
                        for report in audited.get("form_reports") or []
                        if report.get("verified_matches_expected")
                        or report.get("status") == "TARGET_RECOVERED_BY_FACTOR_SUBSTITUTION"
                    ][:8],
                    "holdout_detail": holdout_detail,
                    "matrix_consistent": audited.get("matrix_consistent"),
                    "target": target(candidate),
                    "training_certificate_count": audited.get("training_certificate_count"),
                    "transfer_index": transfer_index(candidate),
                    "verified_recoverable_form_count": candidate_verified,
                }
            )
    if untestable_candidates == len(certs):
        claim_status = "UNTESTABLE_WITH_CURRENT_ARTIFACT"
    elif verified_forms and not false_forms:
        claim_status = "FAMILY_HOLDOUT_TARGET_DESCENT_SIGNAL_SURVIVES"
    elif false_forms:
        claim_status = "FAMILY_HOLDOUT_FALSE_RECOVERY_NEEDS_REVIEW"
    else:
        claim_status = "NEGATIVE_RESULT_FAMILY_HOLDOUT_NO_TARGET_RECOVERY"
    return {
        "axis": axis,
        "candidate_certificate_count": len(certs),
        "candidate_with_false_recovery_count": false_candidates,
        "candidate_with_verified_recovery_count": verified_candidates,
        "claim_status": claim_status,
        "derived_factor_column_count_stats": stat(derived_counts),
        "factor_column_count": factor_count,
        "false_recoverable_form_count": false_forms,
        "factor_rank_stats": stat(ranks),
        "missing_factor_column_counts": dict(sorted(missing_counts.items(), key=lambda item: int(item[0]))),
        "order": order,
        "sample_reports": samples[:20],
        "status_counts": dict(sorted(status_counts.items())),
        "training_certificate_count_stats": stat(training_counts),
        "untestable_candidate_count": untestable_candidates,
        "verified_recoverable_form_count": verified_forms,
    }


def audit_order(order: int, certs: list[dict[str, Any]]) -> dict[str, Any]:
    order_certs = [cert for cert in certs if int_value(cert.get("order")) == order]
    axes = {
        name: audit_holdout_axis(name, holdout, order, order_certs)
        for name, holdout in HOLDOUTS.items()
    }
    strict_axes = [
        name for name in axes
        if name not in {"certificate_leave_one_out", "disjoint_target_holdout"}
    ]
    surviving_strict_axes = [
        name for name in strict_axes
        if axes[name].get("claim_status") == "FAMILY_HOLDOUT_TARGET_DESCENT_SIGNAL_SURVIVES"
    ]
    false_axes = [
        name for name, audit in axes.items()
        if audit.get("claim_status") == "FAMILY_HOLDOUT_FALSE_RECOVERY_NEEDS_REVIEW"
    ]
    leave_one_out = axes["certificate_leave_one_out"]
    if false_axes:
        claim_status = "P739_FAMILY_HOLDOUT_FALSE_RECOVERY_NEEDS_REVIEW"
    elif surviving_strict_axes:
        claim_status = "P739_STRICT_FAMILY_HOLDOUT_TARGET_DESCENT_SIGNAL_SURVIVES"
    elif leave_one_out.get("verified_recoverable_form_count"):
        claim_status = "P739_LEAVE_ONE_OUT_ONLY_FAMILY_DEPENDENCE_OBSERVED"
    else:
        claim_status = "NEGATIVE_RESULT_P739_NO_TARGET_DESCENT_RECOVERY"
    return {
        "axis_audits": axes,
        "candidate_certificate_count": len(order_certs),
        "claim_status": claim_status,
        "control_leave_one_out_verified_forms": leave_one_out.get("verified_recoverable_form_count"),
        "false_recovery_axes": false_axes,
        "order": order,
        "strict_surviving_axes": surviving_strict_axes,
        "targets": sorted({target(cert) for cert in order_certs}),
    }


def determine_claim(order_audits: dict[str, Any]) -> str:
    strict = [
        (order, audit)
        for order, audit in order_audits.items()
        if audit.get("claim_status") == "P739_STRICT_FAMILY_HOLDOUT_TARGET_DESCENT_SIGNAL_SURVIVES"
    ]
    false = [
        (order, audit)
        for order, audit in order_audits.items()
        if audit.get("claim_status") == "P739_FAMILY_HOLDOUT_FALSE_RECOVERY_NEEDS_REVIEW"
    ]
    if false:
        return "P739_FAMILY_HOLDOUT_FALSE_RECOVERY_NEEDS_REVIEW"
    if strict:
        return "P739_STRICT_FAMILY_HOLDOUT_TARGET_DESCENT_SIGNAL_SURVIVES"
    if any(audit.get("control_leave_one_out_verified_forms") for audit in order_audits.values()):
        return "P739_NARROWS_P738_TO_LEAVE_ONE_OUT_FAMILY_SIGNAL"
    return "NEGATIVE_RESULT_P739_NO_TARGET_DESCENT_RECOVERY"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p738 = load_json(Path(args.p738))
    certs = annotate_certificates(p738)
    if not certs:
        raise ValueError("P738 probe does not contain full certificates; rerun P738 with --include-certificates")
    orders = sorted({int_value(cert.get("order")) for cert in certs if int_value(cert.get("order"))})
    order_audits = {str(order): audit_order(order, certs) for order in orders}
    payload = {
        "artifacts": {
            "contract": str(STATE_DIR / "experiment_contract_order11779_p739_family_holdout_target_descent.md"),
            "p738": str(Path(args.p738)),
        },
        "claim_status": "",
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: uses the P738 verifier relation-event factor-column namespace.",
            "FAMILY-HOLDOUT: each axis excludes only the public family it defines.",
            "NO DISJOINT-TARGET CLAIM: disjoint target holdout is untestable when an order has only one target.",
            "NO DEPLOYED-CURVE CLAIM: sparse linear algebra, arbitrary target descent, and large-prime scaling remain open.",
        ],
        "method": "p739_family_holdout_target_descent",
        "order_audits": order_audits,
        "parameters": {
            "holdout_axes": sorted(HOLDOUTS),
            "p738_claim_status": p738.get("claim_status"),
        },
        "schema": "ecdlp.low_term_total2_p739_family_holdout_target_descent.v1",
    }
    payload["claim_status"] = determine_claim(order_audits)
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p738", default=str(DEFAULT_P738))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    compact = {
        "claim_status": payload["claim_status"],
        "orders": {
            order: {
                "claim_status": audit.get("claim_status"),
                "control_leave_one_out_verified_forms": audit.get("control_leave_one_out_verified_forms"),
                "strict_surviving_axes": audit.get("strict_surviving_axes"),
                "targets": audit.get("targets"),
                "axis_summary": {
                    axis: {
                        "claim_status": axis_audit.get("claim_status"),
                        "false_recoverable_form_count": axis_audit.get("false_recoverable_form_count"),
                        "untestable_candidate_count": axis_audit.get("untestable_candidate_count"),
                        "verified_recoverable_form_count": axis_audit.get("verified_recoverable_form_count"),
                    }
                    for axis, axis_audit in (audit.get("axis_audits") or {}).items()
                },
            }
            for order, audit in payload["order_audits"].items()
        },
    }
    print(json.dumps(compact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
