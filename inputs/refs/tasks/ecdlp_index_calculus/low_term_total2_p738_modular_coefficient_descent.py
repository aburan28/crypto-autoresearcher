#!/usr/bin/env python3
"""P738 modular coefficient and target-descent audit for P737 hit rows."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_direct_source_relation_equation_certificate as direct_cert
import low_term_total2_factor_substitution_descent_audit as substitution
import low_term_total2_fixed_leaf_shared_product_timing_probe as timing_probe
import low_term_total2_p719_shared_signed_pair_core_scanner_audit as p719
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P737 = STATE_DIR / "low_term_total2_p737_selector_to_matrix_bridge_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p738_modular_coefficient_descent_probe.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


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


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def row_leaf_variables(case: dict[str, Any]) -> list[str]:
    variables: list[str] = []
    for item in case.get("row_leaf_keys") or []:
        row_key = str(item.get("row_key"))
        leaf_indices = item.get("leaf_indices") or []
        if not leaf_indices:
            variables.append(row_key)
            continue
        for leaf in leaf_indices:
            variables.append(f"{row_key}:leaf{int_value(leaf)}")
    return variables or [str(item) for item in case.get("row_keys") or []]


def source_case_key(case: dict[str, Any]) -> tuple[Any, ...]:
    return (
        str(case.get("target")),
        int_value(case.get("transfer_index")),
        str(case.get("selector")),
        int_value(case.get("top_k")),
        tuple(str(item) for item in case.get("row_keys") or []),
        tuple(row_leaf_variables(case)),
        str(case.get("source_policy") or ""),
    )


def hit_row_key(hit_row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        str(hit_row.get("target")),
        int_value(hit_row.get("transfer_index")),
        str(hit_row.get("selector")),
        int_value(hit_row.get("top_k")),
        tuple(str(item) for item in hit_row.get("row_key_variables") or []),
        tuple(str(item) for item in hit_row.get("row_leaf_variables") or []),
        str(hit_row.get("source_policy") or ""),
    )


def iter_source_cases(source: dict[str, Any]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for policy_name, result in (source.get("policies") or {}).items():
        if not isinstance(result, dict):
            continue
        row_selector = (result.get("row_selector") or {}).get("selector")
        for row in result.get("stress_leaf_results") or []:
            if not isinstance(row, dict):
                continue
            cases.append(
                {
                    **row,
                    "source_policy": policy_name,
                    "row_selector": row.get("row_selector") or row_selector,
                }
            )
    return cases


def find_exact_source_case(source: dict[str, Any], hit_row: dict[str, Any]) -> dict[str, Any]:
    target_key = hit_row_key(hit_row)
    matches = [case for case in iter_source_cases(source) if source_case_key(case) == target_key]
    if not matches:
        raise ValueError(f"no exact source case for {json.dumps(target_key, sort_keys=True)}")
    matches.sort(
        key=lambda row: (
            not bool(row.get("public_key_verified")),
            not bool(row.get("source_verified")),
            float_value(row.get("ops_over_rho"), 10**18),
            str(row.get("source_policy")),
        )
    )
    return matches[0]


def unique_events(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    seen: set[tuple[tuple[int, ...], int]] = set()
    for row in rows:
        scan = row.get("_scan") if isinstance(row.get("_scan"), dict) else {}
        for event in scan.get("relation_events") or scan.get("_events") or []:
            coeffs, rhs, _terms = event["form"]
            key = (tuple(int(coeff) for coeff in coeffs), int(rhs))
            if key in seen:
                continue
            seen.add(key)
            events.append(event)
    return events


def shared_scan_rows(
    verifier: Any,
    contexts: list[dict[str, Any]],
    row_profiles: list[dict[str, Any]],
    max_relations: int,
) -> dict[str, Any]:
    records = [
        {
            "context": context,
            "context_index": index,
            "core_fingerprint": p719.p718.signed_pair_core_fingerprint(context["built"]),
            "profile": profile,
        }
        for index, (context, profile) in enumerate(zip(contexts, row_profiles))
    ]
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        groups[str(record["core_fingerprint"])].append(record)
    direct_rows: list[dict[str, Any]] = []
    shared_rows: list[dict[str, Any]] = []
    group_reports: list[dict[str, Any]] = []
    cover_mismatch_count = 0
    event_mismatch_count = 0
    for core_key, members in sorted(groups.items(), key=lambda item: item[0]):
        shared_scouts = members[0]["context"]["built"]["scouts"]
        member_reports = []
        for record in members:
            context = record["context"]
            direct_cover = p719.direct_cover(context)
            shared_cover = p719.shared_cover(context, shared_scouts)
            direct_normalized = p719.shared_timing.normalized_cover(direct_cover)
            shared_normalized = p719.shared_timing.normalized_cover(shared_cover)
            direct_scan = p719.scan_with_cover(verifier, context, direct_cover, max_relations)
            shared_context = p719.context_with_shared_scouts(context, shared_scouts)
            shared_scan = p719.scan_with_cover(verifier, shared_context, shared_cover, max_relations)
            direct_events = p719.normalized_event_forms(direct_scan)
            shared_events = p719.normalized_event_forms(shared_scan)
            cover_match = direct_normalized == shared_normalized
            event_match = direct_events == shared_events
            if not cover_match:
                cover_mismatch_count += 1
            if not event_match:
                event_mismatch_count += 1
            direct_rows.append({"row_key": context["row_key"], "_scan": direct_scan})
            shared_rows.append({"row_key": context["row_key"], "_scan": shared_scan})
            member_reports.append(
                {
                    "context_index": int_value(record.get("context_index")),
                    "cover_match": cover_match,
                    "direct_event_count": len(direct_events),
                    "event_match": event_match,
                    "row_key": context["row_key"],
                    "shared_event_count": len(shared_events),
                }
            )
        group_reports.append(
            {
                "core_fingerprint": core_key,
                "member_count": len(members),
                "members": member_reports,
            }
        )
    return {
        "cover_mismatch_count": cover_mismatch_count,
        "direct_rows": direct_rows,
        "event_mismatch_count": event_mismatch_count,
        "group_reports": group_reports,
        "shared_rows": shared_rows,
    }


def certificate_for_hit(
    hit_row: dict[str, Any],
    stream_name: str,
    hit_index: int,
    source_cache: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    source_path = Path(str(hit_row.get("source")))
    source = source_cache.setdefault(str(source_path), load_json(source_path))
    source_case = find_exact_source_case(source, hit_row)
    verifier, contexts, product_factor, max_relations = timing_probe.selected_contexts_from_source_case(
        source,
        source_case,
    )
    if not contexts:
        raise ValueError(f"no verifier contexts for {source_path} {hit_index}")
    _direct_rows, direct_ops, rho, row_profiles = timing_probe.direct_witness_rows(verifier, contexts)
    built_by_row = {str(context["row_key"]): context["built"] for context in contexts}
    scans = shared_scan_rows(verifier, contexts, row_profiles, max_relations)
    direct_union = p719.p709.direct_source.direct_witness_probe.union_derive(
        verifier,
        scans["direct_rows"],
        built_by_row,
        "_scan",
    )
    shared_union = p719.p709.direct_source.direct_witness_probe.union_derive(
        verifier,
        scans["shared_rows"],
        built_by_row,
        "_scan",
    )
    order = int_value(contexts[0]["built"].get("order"))
    shared_events = unique_events(scans["shared_rows"])
    direct_events = unique_events(scans["direct_rows"])
    shared_ops_over_rho = hit_row.get("shared_ops_over_rho")
    public_key_verified = bool(shared_union.get("union_public_key_verified"))
    derived_secret = shared_union.get("union_derived_secret")
    event_equivalent = int_value(scans.get("cover_mismatch_count")) == 0 and int_value(scans.get("event_mismatch_count")) == 0
    status = (
        "P738_MODULAR_COEFFICIENT_CERTIFICATE_PASS"
        if public_key_verified and event_equivalent
        else "P738_MODULAR_COEFFICIENT_CERTIFICATE_NEEDS_REVIEW"
    )
    return {
        "certificate_status": status,
        "clause": "p737_shared_core_hit_row",
        "derived_secret": derived_secret,
        "direct_form_count": len(direct_events),
        "direct_ops": direct_ops,
        "direct_ops_over_rho": ratio(direct_ops, rho),
        "direct_union": {
            "derived_secret": direct_union.get("union_derived_secret"),
            "public_key_verified": bool(direct_union.get("union_public_key_verified")),
            "rank": int_value(direct_union.get("union_rank")),
            "relation_count": int_value(direct_union.get("union_relation_count")),
        },
        "event_equivalence": {
            "cover_mismatch_count": int_value(scans.get("cover_mismatch_count")),
            "event_mismatch_count": int_value(scans.get("event_mismatch_count")),
            "group_count": len(scans.get("group_reports") or []),
        },
        "expected_secret": derived_secret if public_key_verified else None,
        "forms": [direct_cert.compact_form(event, order) for event in shared_events],
        "forms_count": len(shared_events),
        "hit_index": hit_index,
        "order": order,
        "product_factor": product_factor,
        "public_key_verified": public_key_verified,
        "rank": int_value(shared_union.get("union_rank")),
        "rowspace_derives_expected_secret": public_key_verified,
        "scan_row_count": len(scans["shared_rows"]),
        "selected": {
            "charged_ops_over_rho": hit_row.get("charged_ops_over_rho"),
            "clause": "p737_shared_core_hit_row",
            "direct_ops": direct_ops,
            "direct_ops_over_rho": ratio(direct_ops, rho),
            "expected_rank": hit_row.get("rank"),
            "rho": rho,
            "row_keys": hit_row.get("row_key_variables") or [],
            "row_leaf_keys": hit_row.get("row_leaf_variables") or [],
            "secret": derived_secret if public_key_verified else None,
            "selector": hit_row.get("selector"),
            "shared_ops": None,
            "shared_ops_over_rho": shared_ops_over_rho,
            "source_policy": hit_row.get("source_policy"),
            "stream": stream_name,
            "target": hit_row.get("target"),
            "top_k": int_value(hit_row.get("top_k")),
            "transfer_index": int_value(hit_row.get("transfer_index")),
            "window": hit_row.get("window"),
        },
        "shared_union": {
            "derived_secret": shared_union.get("union_derived_secret"),
            "public_key_verified": public_key_verified,
            "rank": int_value(shared_union.get("union_rank")),
            "relation_count": int_value(shared_union.get("union_relation_count")),
        },
        "source": str(source_path),
        "source_case_selector": {
            "selector": source_case.get("selector"),
            "source_policy": source_case.get("source_policy"),
            "target": source_case.get("target"),
            "top_k": source_case.get("top_k"),
            "transfer_index": source_case.get("transfer_index"),
        },
        "source_match": {
            "exact": source_case_key(source_case) == hit_row_key(hit_row),
            "row_key_variables": hit_row.get("row_key_variables") or [],
            "row_leaf_variables": hit_row.get("row_leaf_variables") or [],
        },
        "stream": stream_name,
        "timing": None,
        "window": "_".join(str(part) for part in hit_row.get("window") or []),
    }


def annotate_certificates(certificates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    annotated = []
    for index, cert in enumerate(certificates):
        item = dict(cert)
        item["_artifact"] = "p738_in_memory_p737_hit_certificate"
        item["_artifact_offset"] = index
        item["_global_index"] = index
        annotated.append(item)
    return annotated


def order_factor_audits(certificates: list[dict[str, Any]]) -> dict[str, Any]:
    orders = sorted({int_value(cert.get("order")) for cert in certificates if int_value(cert.get("order"))})
    return {str(order): factor_bank.audit_order(certificates, order) for order in orders}


def leave_one_out_descent(certificates: list[dict[str, Any]], order: int) -> dict[str, Any]:
    order_certs = [cert for cert in certificates if int_value(cert.get("order")) == order]
    factor_count = substitution.factor_count_for(order_certs, order)
    status_counts: Counter[str] = Counter()
    false_recoveries = 0
    verified_recoveries = 0
    candidate_with_verified = 0
    samples = []
    for cert in order_certs:
        cert_index = int_value(cert.get("_global_index"))
        training = [item for item in order_certs if int_value(item.get("_global_index")) != cert_index]
        derivation = substitution.derive_factor_values(training, order, factor_count)
        factor_values = derivation["factor_values"]
        form_reports = []
        cert_verified = 0
        cert_false = 0
        for form_index, form in enumerate(cert.get("forms") or []):
            if not isinstance(form, dict):
                continue
            report = substitution.audit_candidate_form(cert, form, form_index, order, factor_count, factor_values)
            status_counts[report["status"]] += 1
            if report["verified_matches_expected"]:
                verified_recoveries += 1
                cert_verified += 1
            elif report["status"] == "TARGET_RECOVERED_BY_FACTOR_SUBSTITUTION":
                false_recoveries += 1
                cert_false += 1
            form_reports.append(report)
        if cert_verified:
            candidate_with_verified += 1
        if cert_verified or cert_false or len(samples) < 12:
            samples.append(
                {
                    "certificate_index": cert_index,
                    "derived_factor_column_count": len(factor_values),
                    "factor_rank": derivation["rank"],
                    "false_recoverable_form_count": cert_false,
                    "form_reports": form_reports[:8],
                    "matrix_consistent": derivation["matrix_consistent"],
                    "target": (cert.get("selected") or {}).get("target"),
                    "transfer_index": int_value((cert.get("selected") or {}).get("transfer_index")),
                    "verified_recoverable_form_count": cert_verified,
                }
            )
    return {
        "candidate_certificate_count": len(order_certs),
        "candidate_with_verified_recovery_count": candidate_with_verified,
        "claim_status": (
            "LEAVE_ONE_OUT_TARGET_DESCENT_SIGNAL_FOUND"
            if verified_recoveries and not false_recoveries
            else "LEAVE_ONE_OUT_TARGET_DESCENT_FALSE_RECOVERY_NEEDS_REVIEW"
            if false_recoveries
            else "NEGATIVE_RESULT_NO_LEAVE_ONE_OUT_TARGET_RECOVERY"
        ),
        "factor_column_count": factor_count,
        "false_recoverable_form_count": false_recoveries,
        "order": order,
        "sample_reports": samples[:20],
        "status_counts": dict(sorted(status_counts.items())),
        "verified_recoverable_form_count": verified_recoveries,
    }


def circular_upper_bound_descent(certificates: list[dict[str, Any]], order: int) -> dict[str, Any]:
    order_certs = [cert for cert in certificates if int_value(cert.get("order")) == order]
    factor_count = substitution.factor_count_for(order_certs, order)
    derivation = substitution.derive_factor_values(order_certs, order, factor_count)
    factor_values = derivation["factor_values"]
    status_counts: Counter[str] = Counter()
    verified = 0
    false = 0
    samples = []
    for cert in order_certs:
        cert_verified = 0
        for form_index, form in enumerate(cert.get("forms") or []):
            if not isinstance(form, dict):
                continue
            report = substitution.audit_candidate_form(cert, form, form_index, order, factor_count, factor_values)
            status_counts[report["status"]] += 1
            if report["verified_matches_expected"]:
                verified += 1
                cert_verified += 1
            elif report["status"] == "TARGET_RECOVERED_BY_FACTOR_SUBSTITUTION":
                false += 1
            if cert_verified and len(samples) < 12:
                samples.append(
                    {
                        "certificate_index": int_value(cert.get("_global_index")),
                        "form_index": form_index,
                        "target": (cert.get("selected") or {}).get("target"),
                        "transfer_index": int_value((cert.get("selected") or {}).get("transfer_index")),
                    }
                )
    return {
        "claim_status": (
            "CIRCULAR_UPPER_BOUND_TARGET_SUBSTITUTION_RECOVERS"
            if verified and not false
            else "CIRCULAR_UPPER_BOUND_FALSE_RECOVERY_NEEDS_REVIEW"
            if false
            else "CIRCULAR_UPPER_BOUND_NO_TARGET_RECOVERY"
        ),
        "derived_factor_column_count": len(factor_values),
        "factor_column_count": factor_count,
        "false_recoverable_form_count": false,
        "matrix_consistent": derivation["matrix_consistent"],
        "order": order,
        "rank": derivation["rank"],
        "sample_recoveries": samples,
        "status_counts": dict(sorted(status_counts.items())),
        "unique_relation_count": derivation["unique_relation_count"],
        "verified_recoverable_form_count": verified,
    }


def stream_summary(stream: dict[str, Any], certs: list[dict[str, Any]]) -> dict[str, Any]:
    passing = [cert for cert in certs if cert.get("certificate_status") == "P738_MODULAR_COEFFICIENT_CERTIFICATE_PASS"]
    return {
        "certificate_count": len(certs),
        "detector_total": (stream.get("detector_eval") or {}).get("source_replay_total_with_fallback_over_rho"),
        "event_mismatch_count": sum(int_value((cert.get("event_equivalence") or {}).get("event_mismatch_count")) for cert in certs),
        "exact_source_match_count": sum(1 for cert in certs if (cert.get("source_match") or {}).get("exact")),
        "exported_form_count": sum(int_value(cert.get("forms_count")) for cert in certs),
        "passing_certificate_count": len(passing),
        "rho_baseline": (stream.get("detector_eval") or {}).get("vs_independent_rho_with_fallback_over_rho"),
        "stream": stream.get("stream"),
        "target": stream.get("target"),
    }


def determine_claim(
    certificate_summary: dict[str, Any],
    factor_audits: dict[str, Any],
    leave_one_out: dict[str, Any],
) -> str:
    export_ok = (
        int_value(certificate_summary.get("certificate_count")) > 0
        and certificate_summary.get("certificate_count") == certificate_summary.get("passing_certificate_count")
        and int_value(certificate_summary.get("event_mismatch_count")) == 0
    )
    total_rank = sum(int_value(audit.get("rank")) for audit in factor_audits.values())
    matrices_consistent = all(bool(audit.get("matrix_consistent")) for audit in factor_audits.values())
    loo_verified = sum(int_value(audit.get("verified_recoverable_form_count")) for audit in leave_one_out.values())
    loo_false = sum(int_value(audit.get("false_recoverable_form_count")) for audit in leave_one_out.values())
    if export_ok and total_rank > 0 and matrices_consistent and loo_verified and not loo_false:
        return "P738_NONCIRCULAR_TARGET_DESCENT_SIGNAL_FOUND"
    if export_ok and total_rank > 0 and matrices_consistent:
        return "P738_MODULAR_FACTOR_RANK_POSITIVE_TARGET_DESCENT_OPEN"
    if export_ok:
        return "NEGATIVE_RESULT_P738_MODULAR_FACTOR_RANK_TRIVIAL"
    return "NEGATIVE_RESULT_P738_COEFFICIENT_EXPORT_FAILED"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p737 = load_json(Path(args.p737))
    source_cache: dict[str, dict[str, Any]] = {}
    stream_certs: dict[str, list[dict[str, Any]]] = {}
    errors = []
    for stream in p737.get("streams") or []:
        certs = []
        for index, hit_row in enumerate(stream.get("hit_rows") or []):
            try:
                certs.append(certificate_for_hit(hit_row, str(stream.get("stream")), index, source_cache))
            except Exception as exc:  # noqa: BLE001 - replay failure is experiment evidence.
                errors.append(
                    {
                        "error": f"{type(exc).__name__}: {exc}",
                        "hit_index": index,
                        "stream": stream.get("stream"),
                        "target": hit_row.get("target"),
                        "transfer_index": hit_row.get("transfer_index"),
                    }
                )
        stream_certs[str(stream.get("stream"))] = certs
    certificates = annotate_certificates([cert for certs in stream_certs.values() for cert in certs])
    orders = sorted({int_value(cert.get("order")) for cert in certificates if int_value(cert.get("order"))})
    factor_audits = order_factor_audits(certificates)
    leave_one_out = {str(order): leave_one_out_descent(certificates, order) for order in orders}
    circular_upper = {str(order): circular_upper_bound_descent(certificates, order) for order in orders}
    stream_summaries = [
        stream_summary(stream, stream_certs.get(str(stream.get("stream")), []))
        for stream in p737.get("streams") or []
    ]
    certificate_summary = {
        "certificate_count": len(certificates),
        "event_mismatch_count": sum(
            int_value((cert.get("event_equivalence") or {}).get("event_mismatch_count"))
            for cert in certificates
        ),
        "exact_source_match_count": sum(1 for cert in certificates if (cert.get("source_match") or {}).get("exact")),
        "export_error_count": len(errors),
        "exported_form_count": sum(int_value(cert.get("forms_count")) for cert in certificates),
        "passing_certificate_count": sum(
            1 for cert in certificates
            if cert.get("certificate_status") == "P738_MODULAR_COEFFICIENT_CERTIFICATE_PASS"
        ),
        "source_file_count": len(source_cache),
    }
    payload = {
        "artifacts": {
            "contract": str(STATE_DIR / "experiment_contract_order9887_p738_modular_coefficient_descent.md"),
            "p737": str(Path(args.p737)),
        },
        "certificate_errors": errors,
        "certificate_samples": certificates[:8],
        "certificate_summary": certificate_summary,
        "certificates": certificates if args.include_certificates else [],
        "claim_status": "",
        "created_at": now_iso(),
        "factor_rank_audits": factor_audits,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: modular coefficients are verifier relation-event forms from the local low-term total-2 model.",
            "REPLAY-BACKED: certificate forms must verify the public key through the verifier.",
            "NON-CIRCULAR DESCENT REQUIRED: leave-one-out recovery is the target-descent success gate.",
            "NO DEPLOYED-CURVE CLAIM: large-prime scaling, sparse linear algebra, and arbitrary target descent remain open.",
        ],
        "leave_one_out_descent": leave_one_out,
        "method": "p738_modular_coefficient_descent",
        "parameters": {
            "include_certificates": bool(args.include_certificates),
            "p737_claim_status": p737.get("claim_status"),
            "rank_modulus_source": "certificate order",
            "source_case_match": "target+transfer+selector+top_k+source_policy+row_keys+row_leaf_keys",
        },
        "schema": "ecdlp.low_term_total2_p738_modular_coefficient_descent.v1",
        "self_including_upper_bound_descent": circular_upper,
        "stream_summaries": stream_summaries,
        "target_descent_status": {},
    }
    payload["claim_status"] = determine_claim(certificate_summary, factor_audits, leave_one_out)
    loo_verified = sum(int_value(audit.get("verified_recoverable_form_count")) for audit in leave_one_out.values())
    loo_false = sum(int_value(audit.get("false_recoverable_form_count")) for audit in leave_one_out.values())
    total_rank = sum(int_value(audit.get("rank")) for audit in factor_audits.values())
    payload["target_descent_status"] = {
        "non_circular_leave_one_out_false_recoveries": loo_false,
        "non_circular_leave_one_out_verified_recoveries": loo_verified,
        "reason": (
            "Leave-one-out factor substitution recovered at least one target with no false recovery."
            if loo_verified and not loo_false
            else "Modular factor rank is positive, but leave-one-out factor substitution did not recover a target."
            if total_rank > 0
            else "No modular factor rank was obtained from target-eliminated rows."
        ),
        "status": (
            "BOUNDED_SIGNAL_FOUND"
            if loo_verified and not loo_false
            else "OPEN"
        ),
    }
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p737", default=str(DEFAULT_P737))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument(
        "--include-certificates",
        action="store_true",
        help="Include full exported certificates in the probe instead of compact samples only.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    compact = {
        "certificate_summary": payload["certificate_summary"],
        "claim_status": payload["claim_status"],
        "factor_rank_summary": {
            order: {
                "deficiency": audit.get("deficiency"),
                "factor_variable_count": audit.get("factor_variable_count"),
                "matrix_consistent": audit.get("matrix_consistent"),
                "rank": audit.get("rank"),
                "unique_factor_relation_count": audit.get("unique_factor_relation_count"),
            }
            for order, audit in payload["factor_rank_audits"].items()
        },
        "leave_one_out_summary": {
            order: {
                "claim_status": audit.get("claim_status"),
                "false_recoverable_form_count": audit.get("false_recoverable_form_count"),
                "verified_recoverable_form_count": audit.get("verified_recoverable_form_count"),
            }
            for order, audit in payload["leave_one_out_descent"].items()
        },
        "stream_summaries": payload["stream_summaries"],
        "target_descent_status": payload["target_descent_status"],
    }
    print(json.dumps(compact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
