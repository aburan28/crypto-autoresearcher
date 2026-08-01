#!/usr/bin/env python3
"""P989 relation-form independence audit for the P988 p231 high-gap stream."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p868_p231_fresh_skeleton_generator_audit as p868
import low_term_total2_p985_p231_cumulative_false_positive_discriminator as p985
import low_term_total2_p987_p231_cumulative_high_gap_relation_source as p987
import relation_probe


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p989_p231_relation_independence_readiness.md"
DEFAULT_P984 = STATE_DIR / "low_term_total2_p984_p231_cumulative_high_gap_forward_probe.json"
DEFAULT_P986 = STATE_DIR / "low_term_total2_p986_p231_adaptive_high_gap_guard_validation_probe.json"
DEFAULT_P988 = STATE_DIR / "low_term_total2_p988_p231_forward_high_gap_density_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p989_p231_relation_independence_readiness_probe.json"
SCHEMA = "ecdlp.low_term_total2_p989_p231_relation_independence_readiness.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def round8(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 8)


def ratio(numerator: int | float, denominator: int | float) -> float | None:
    if denominator == 0:
        return None
    return round8(float(numerator) / float(denominator))


def json_key(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def source_controls(p988: dict[str, Any]) -> dict[str, Any]:
    summary = p988.get("summary") or {}
    return {
        "p988_claim_expected": p988.get("claim_status") == "P988_FORWARD_HIGH_GAP_DENSITY_REMAINS_BELOW_RHO",
        "p988_control_pass": bool(summary.get("control_pass")),
        "p988_combined_selected_fourteen": int_value(summary.get("combined_selected_count")) == 14,
        "p988_combined_broad_groups_twelve": int_value(summary.get("combined_broad_relation_group_count")) == 12,
        "p988_broad_amortized_expected": summary.get("combined_broad_direct_relation_amortized_ops_over_rho")
        == 0.94890511,
        "p988_reconstruction_errors_zero": int_value(summary.get("reconstruction_error_count")) == 0,
    }


def relation_key(row: dict[str, Any]) -> str:
    return json_key(
        {
            "row_leaf_keys": row.get("row_leaf_keys") or [],
            "target": row.get("target"),
            "transfer_index": int_value(row.get("transfer_index")),
            "union_derived_secret": row.get("union_derived_secret"),
        }
    )


def broad_rows(p984: dict[str, Any], p986: dict[str, Any], p988: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    rows.extend(p987.rows_from_p984(p984))
    rows.extend(p987.rows_from_p986(p986))
    for case in p988.get("forward_cases") or []:
        if isinstance(case, dict):
            row = dict(case)
            row["audit_block"] = "p988_forward_high_gap"
            rows.append(row)
    broad = [row for row in rows if p985.is_broad(row)]
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for row in broad:
        key = relation_key(row)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped


def pad(values: list[int], width: int) -> list[int]:
    if len(values) >= width:
        return values[:]
    return values + [0] * (width - len(values))


def rank_mod(matrix: list[list[int]], modulus: int) -> dict[str, Any]:
    if not matrix:
        return {"rank": 0, "nonunit_pivot_candidate_count": 0}
    width = max(len(row) for row in matrix)
    mat = [[int_value(value) % modulus for value in pad(row, width)] for row in matrix]
    rank = 0
    nonunit = 0
    for col in range(width):
        pivot = None
        for row in range(rank, len(mat)):
            value = mat[row][col] % modulus
            if value == 0:
                continue
            if math.gcd(value, modulus) == 1:
                pivot = row
                break
            nonunit += 1
        if pivot is None:
            continue
        mat[rank], mat[pivot] = mat[pivot], mat[rank]
        inv = pow(mat[rank][col] % modulus, -1, modulus)
        mat[rank] = [(value * inv) % modulus for value in mat[rank]]
        for row in range(len(mat)):
            if row == rank:
                continue
            factor = mat[row][col] % modulus
            if factor:
                mat[row] = [(left - factor * right) % modulus for left, right in zip(mat[row], mat[rank])]
        rank += 1
        if rank == len(mat):
            break
    return {"rank": rank, "nonunit_pivot_candidate_count": nonunit}


def build_specs_for_window(
    window: str,
    build_cache: dict[str, tuple[Any, list[dict[str, Any]], dict[str, Any], dict[str, dict[str, dict[str, Any]]], argparse.Namespace]],
) -> tuple[Any, list[dict[str, Any]], dict[str, Any], dict[str, dict[str, dict[str, Any]]], argparse.Namespace]:
    source = p868.load_json(p868.source_path(window))
    params = p868.repair_probe.source_parameters(source)
    probe_args = p868.repair_probe.probe_args_from_source(source)
    cache_key = p868.json_key(
        {
            "bank_source": params.get("bank_source"),
            "config_source": params.get("config_source"),
            "direct_source": params.get("direct_source"),
            "radius": params.get("radius"),
            "transfer_source": params.get("transfer_source"),
        }
    )
    if cache_key not in build_cache:
        build_cache[cache_key] = (*p868.repair_probe.build_specs(params), probe_args)
    return build_cache[cache_key]


def reconstruct_case(
    row: dict[str, Any],
    build_cache: dict[str, tuple[Any, list[dict[str, Any]], dict[str, Any], dict[str, dict[str, dict[str, Any]]], argparse.Namespace]],
    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]],
) -> dict[str, Any]:
    verifier, records, config_source, specs_by_target, probe_args = build_specs_for_window(str(row.get("window")), build_cache)
    context = p868.hit_stream_probe.scan_case_context(
        verifier,
        records,
        config_source,
        specs_by_target,
        row,
        probe_args,
        context_cache,
    )
    rows_for_union = []
    built_for_union = {}
    form_records: list[dict[str, Any]] = []
    row_scans = []
    direct_ops = 0
    generic_rho = 0
    orders: set[int] = set()
    for item in p868.hit_stream_probe.unique_row_leaf_keys(row):
        row_key = str(item["row_key"])
        if row_key not in context["built_by_row"]:
            row_scans.append({"row_key": row_key, "error": "row context not reconstructed"})
            continue
        built = context["built_by_row"][row_key]
        order = int_value(built.get("order"))
        orders.add(order)
        scan = p868.direct_witness_probe.scan_selected(
            verifier,
            built,
            context["components_by_row"][row_key],
            {int_value(leaf) for leaf in item["leaf_indices"]},
            context["local_args_by_row"][row_key],
        )
        rows_for_union.append({"row_key": row_key, "_scan": scan})
        built_for_union[row_key] = built
        direct_ops += int_value(scan.get("preassociation_filter_ops"))
        generic_rho = max(generic_rho, int_value(built.get("generic_rho_steps")))
        form_records.extend(p868.form_records_from_scan(str(row.get("case_id")), row_key, scan, order))
        row_scans.append(
            {
                "derived_secret": scan.get("derived_secret"),
                "preassociation_filter_ops": scan.get("preassociation_filter_ops"),
                "rank": scan.get("rank"),
                "relation_count": scan.get("relation_count"),
                "row_key": row_key,
                "row_public_key_verified": bool(scan.get("row_public_key_verified")),
                "selected_leaf_indices": scan.get("selected_leaf_indices"),
            }
        )
    union = p868.direct_witness_probe.union_derive(verifier, rows_for_union, built_for_union, "_scan")
    order = next(iter(orders)) if len(orders) == 1 else 0
    derivations = p868.local_derivations(form_records, union.get("union_derived_secret"), order) if order else []
    matched = [item for item in derivations if item.get("matches_expected_secret")]
    p867_matched = [item for item in matched if item.get("is_p867_motif")]
    return {
        "case_id": row.get("case_id"),
        "direct_ops_over_rho": row.get("direct_ops_over_rho"),
        "form_records": form_records,
        "generic_rho_steps": generic_rho,
        "local_derivation_count": len(derivations),
        "local_matched_derivation_count": len(matched),
        "order": order,
        "p867_matched_derivation_count": len(p867_matched),
        "reconstructed_error_count": len(context.get("errors") or []) + sum(1 for scan in row_scans if scan.get("error")),
        "relation_form_count": len(form_records),
        "row_leaf_keys": row.get("row_leaf_keys"),
        "row_scans": row_scans,
        "target": row.get("target"),
        "transfer_index": row.get("transfer_index"),
        "union_derived_secret": union.get("union_derived_secret"),
        "union_public_key_verified": bool(union.get("union_public_key_verified")),
        "union_rank": union.get("union_rank"),
        "union_relation_count": union.get("union_relation_count"),
        "window": row.get("window"),
    }


def form_key(form: dict[str, Any]) -> str:
    return json_key({"coeffs": form.get("coeffs"), "rhs": form.get("rhs"), "terms": form.get("terms")})


def compact_form(form: dict[str, Any]) -> dict[str, Any]:
    return {
        "anchor_coeff": form.get("anchor_coeff"),
        "case_id": form.get("case_id"),
        "event_index": form.get("event_index"),
        "exact_tail_expression_key": form.get("exact_tail_expression_key"),
        "is_p867_motif": form.get("is_p867_motif"),
        "motif": form.get("motif"),
        "rhs": form.get("rhs"),
        "row_key": form.get("row_key"),
        "support": form.get("support"),
        "tail_support": form.get("tail_support"),
        "terms": form.get("terms"),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p984_path = Path(args.p984)
    p986_path = Path(args.p986)
    p988_path = Path(args.p988)
    p984 = load_json(p984_path)
    p986 = load_json(p986_path)
    p988 = load_json(p988_path)
    controls = source_controls(p988)
    control_pass = all(controls.values())
    selected = broad_rows(p984, p986, p988)

    build_cache: dict[
        str,
        tuple[Any, list[dict[str, Any]], dict[str, Any], dict[str, dict[str, dict[str, Any]]], argparse.Namespace],
    ] = {}
    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]] = {}
    reconstructed = [reconstruct_case(row, build_cache, context_cache) for row in selected]
    all_forms = [form for case in reconstructed for form in case.get("form_records") or []]
    unique_forms_by_key: dict[str, dict[str, Any]] = {}
    for form in all_forms:
        unique_forms_by_key.setdefault(form_key(form), form)
    unique_forms = list(unique_forms_by_key.values())
    orders = sorted({int_value(form.get("order")) for form in unique_forms if int_value(form.get("order"))})
    order = orders[0] if len(orders) == 1 else 0
    coeff_width = max([len(form.get("coeffs") or []) for form in unique_forms], default=0)
    coeff_matrix = [pad([int_value(value) for value in form.get("coeffs") or []], coeff_width) for form in unique_forms]
    augmented_matrix = [row + [int_value(form.get("rhs"))] for row, form in zip(coeff_matrix, unique_forms)]
    coeff_rank = rank_mod(coeff_matrix, order) if order else {"rank": 0, "nonunit_pivot_candidate_count": 0}
    augmented_rank = rank_mod(augmented_matrix, order) if order else {"rank": 0, "nonunit_pivot_candidate_count": 0}
    verifier_probe = {"mixed_wide_relation_rank": 0, "derived_secret": None, "mixed_wide_relations_derive_secret": False}
    if unique_forms and order:
        verifier = next(iter(build_cache.values()))[0]
        verifier_forms = [
            ([int_value(value) for value in form.get("coeffs") or []], int_value(form.get("rhs")), [int_value(t) for t in form.get("terms") or []])
            for form in unique_forms
        ]
        verifier_probe = relation_probe.linear_rank_probe(verifier, verifier_forms, order)

    reconstruction_error_count = sum(int_value(case.get("reconstructed_error_count")) for case in reconstructed)
    term_key_counter = Counter(json_key(form.get("terms") or []) for form in unique_forms)
    exact_tail_counter = Counter(str(form.get("exact_tail_expression_key")) for form in unique_forms)
    coeff_length_counter = Counter(str(len(form.get("coeffs") or [])) for form in unique_forms)
    row_key_counter = Counter(str(form.get("row_key")) for form in unique_forms)
    case_rank_counter = Counter(str(case.get("union_rank")) for case in reconstructed)
    full_column_rank = bool(order and coeff_width and coeff_rank["rank"] == coeff_width)
    derives_secret = bool(verifier_probe.get("mixed_wide_relations_derive_secret"))
    success = bool(
        control_pass
        and len(selected) == 12
        and reconstruction_error_count == 0
        and len(orders) == 1
        and len(unique_forms) > 0
        and derives_secret
    )
    if not control_pass:
        claim = "NEGATIVE_RESULT_P989_CONTROL_FAILURE"
    elif len(selected) != 12:
        claim = "NEGATIVE_RESULT_P989_UNEXPECTED_BROAD_GROUP_COUNT"
    elif reconstruction_error_count != 0:
        claim = "NEGATIVE_RESULT_P989_RECONSTRUCTION_ERRORS"
    elif len(orders) != 1:
        claim = "NEGATIVE_RESULT_P989_INCONSISTENT_FORM_ORDER"
    elif not unique_forms:
        claim = "NEGATIVE_RESULT_P989_NO_RECONSTRUCTED_FORMS"
    elif derives_secret:
        claim = "P989_SHARED_BASIS_RELATION_FORMS_DERIVE_SECRET"
    elif full_column_rank:
        claim = "P989_FULL_COLUMN_RANK_BUT_NO_VERIFIER_SECRET_DERIVATION"
    else:
        claim = "NEGATIVE_RESULT_P989_RELATION_FORMS_RANK_DEFICIENT"

    case_summaries = []
    for case in reconstructed:
        forms = case.get("form_records") or []
        local_order = int_value(case.get("order"))
        local_width = max([len(form.get("coeffs") or []) for form in forms], default=0)
        local_rank = rank_mod(
            [pad([int_value(value) for value in form.get("coeffs") or []], local_width) for form in forms],
            local_order,
        ) if local_order else {"rank": 0, "nonunit_pivot_candidate_count": 0}
        case_summaries.append(
            {
                "case_id": case.get("case_id"),
                "direct_ops_over_rho": case.get("direct_ops_over_rho"),
                "form_count": len(forms),
                "local_coeff_column_count": local_width,
                "local_coeff_rank": local_rank["rank"],
                "local_matched_derivation_count": case.get("local_matched_derivation_count"),
                "order": local_order,
                "p867_matched_derivation_count": case.get("p867_matched_derivation_count"),
                "row_leaf_keys": case.get("row_leaf_keys"),
                "transfer_index": case.get("transfer_index"),
                "union_derived_secret": case.get("union_derived_secret"),
                "union_public_key_verified": case.get("union_public_key_verified"),
                "union_rank": case.get("union_rank"),
                "union_relation_count": case.get("union_relation_count"),
                "window": case.get("window"),
            }
        )

    return {
        "artifacts": {
            "contract": str(args.contract),
            "p984_source": str(p984_path),
            "p986_source": str(p986_path),
            "p988_source": str(p988_path),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": sha256_file(Path(args.contract)),
            "p984_source_sha256": sha256_file(p984_path),
            "p986_source_sha256": sha256_file(p986_path),
            "p988_source_sha256": sha256_file(p988_path),
            "script_sha256": sha256_file(Path(__file__)),
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P989_") else "NEGATIVE RESULT",
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "RECONSTRUCTED-FORMS: rank is measured from source relation_events, not from matrix-form proxies.",
            "SHARED-BASIS-ASSUMPTION: verifier derivation is the promoted check for a shared linear system.",
            "NO-SOURCE-COST-CHANGE: this audits independence/readiness, not relation collection cost.",
            "NO-END-TO-END-BREAK: target descent and scaling remain open.",
        ],
        "method": "p989_p231_relation_independence_readiness",
        "schema": SCHEMA,
        "source_controls": controls,
        "summary": {
            "augmented_rank_mod_order": augmented_rank["rank"],
            "broad_case_count": len(selected),
            "case_union_rank_histogram": dict(sorted(case_rank_counter.items())),
            "coefficient_column_count": coeff_width,
            "coefficient_length_histogram": dict(sorted(coeff_length_counter.items())),
            "coefficient_rank_mod_order": coeff_rank["rank"],
            "coefficient_rank_ratio": ratio(coeff_rank["rank"], coeff_width),
            "control_pass": control_pass,
            "derived_secret": verifier_probe.get("derived_secret"),
            "exact_tail_expression_count": len(exact_tail_counter),
            "form_order": order or None,
            "form_order_count": len(orders),
            "full_column_rank": full_column_rank,
            "linear_independence_success": success,
            "mixed_wide_relation_rank": verifier_probe.get("mixed_wide_relation_rank"),
            "mixed_wide_relations_derive_secret": derives_secret,
            "nonunit_pivot_candidate_count": coeff_rank["nonunit_pivot_candidate_count"],
            "reconstructed_case_count": len(reconstructed),
            "reconstruction_error_count": reconstruction_error_count,
            "row_key_count": len(row_key_counter),
            "term_basis_count": len(term_key_counter),
            "unique_form_count": len(unique_forms),
            "raw_form_count": len(all_forms),
            "window_count": len({case.get("window") for case in reconstructed}),
        },
        "diagnostics": {
            "case_summaries": case_summaries,
            "exact_tail_expression_histogram": dict(sorted(exact_tail_counter.items())),
            "row_key_histogram": dict(sorted(row_key_counter.items())),
            "term_basis_histogram": dict(sorted(term_key_counter.items())),
            "unique_forms_sample": [compact_form(form) for form in unique_forms[:32]],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P989 contract path")
    parser.add_argument("--p984", default=str(DEFAULT_P984), help="P984 cumulative high-gap JSON")
    parser.add_argument("--p986", default=str(DEFAULT_P986), help="P986 adaptive high-gap JSON")
    parser.add_argument("--p988", default=str(DEFAULT_P988), help="P988 forward density JSON")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    print(
        "claim={claim} cases={cases} forms={forms} unique_forms={unique_forms} "
        "cols={cols} coeff_rank={coeff_rank} verifier_rank={verifier_rank} "
        "derives={derives} term_bases={term_bases} out={out}".format(
            claim=payload["claim_status"],
            cases=summary["broad_case_count"],
            forms=summary["raw_form_count"],
            unique_forms=summary["unique_form_count"],
            cols=summary["coefficient_column_count"],
            coeff_rank=summary["coefficient_rank_mod_order"],
            verifier_rank=summary["mixed_wide_relation_rank"],
            derives=summary["mixed_wide_relations_derive_secret"],
            term_bases=summary["term_basis_count"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
