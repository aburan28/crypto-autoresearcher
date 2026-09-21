#!/usr/bin/env python3
"""P868 fresh-window generator audit for the P867 p231 tail skeleton."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_direct_witness_probe as direct_witness_probe
import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_low_term_total2_ffe_hit_stream_probe as hit_stream_probe
import low_term_total2_public_prefix_shared_leaf_repair_probe as repair_probe


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p868_p231_fresh_skeleton_generator_audit.md"
DEFAULT_WINDOWS = (
    "1192_1199",
    "1200_1207",
    "1208_1215",
    "1216_1223",
    "1224_1231",
    "1232_1239",
)
DEFAULT_TARGET = "22050.cf1@11731"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p868_p231_fresh_skeleton_generator_audit_probe.json"
SCHEMA = "ecdlp.low_term_total2_p868_p231_fresh_skeleton_generator_audit.v1"
P867_MOTIF = {
    "normalized_tail_coeffs": [1, 1],
    "tail_support_gaps": [0, 2],
    "term_gaps": [0, 0, 2, 2],
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def json_key(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def source_path(window: str) -> Path:
    return STATE_DIR / f"frontier_public_leaf_policy_p231_frozen_prefix_fixed_row_{window}_probe.json"


def normalize_offsets(values: list[int]) -> list[int]:
    if not values:
        return []
    base = min(values)
    return [int(value) - base for value in values]


def invertible(value: int, modulus: int) -> bool:
    return modulus > 1 and math.gcd(value % modulus, modulus) == 1


def normalized_tail_coeffs(tail_items: list[tuple[int, int]], modulus: int) -> list[int] | None:
    if not tail_items:
        return []
    first = tail_items[0][1] % modulus
    if not invertible(first, modulus):
        return None
    inv = pow(first, -1, modulus)
    return [(coeff * inv) % modulus for _index, coeff in tail_items]


def motif_from_form(coeffs: list[int], terms: list[int], order: int) -> dict[str, Any]:
    tail_items = [(idx, coeff % order) for idx, coeff in enumerate(coeffs) if idx != 0 and coeff % order != 0]
    tail_support = [idx for idx, _coeff in tail_items]
    return {
        "normalized_tail_coeffs": normalized_tail_coeffs(tail_items, order),
        "tail_support_gaps": normalize_offsets(tail_support),
        "term_gaps": normalize_offsets([int(term) for term in terms]),
    }


def exact_tail_expression(coeffs: list[int], terms: list[int], order: int) -> dict[str, Any]:
    tail_items = [(idx, coeff % order) for idx, coeff in enumerate(coeffs) if idx != 0 and coeff % order != 0]
    return {
        "tail_coeffs": [coeff for _idx, coeff in tail_items],
        "tail_support": [idx for idx, _coeff in tail_items],
        "terms": [int(term) for term in terms],
    }


def iter_source_cases(source: dict[str, Any], window: str, targets: set[str]) -> list[dict[str, Any]]:
    cases: dict[tuple[Any, ...], dict[str, Any]] = {}
    for policy_name, result in (source.get("policies") or {}).items():
        if not isinstance(result, dict):
            continue
        row_selector = (result.get("row_selector") or {}).get("selector")
        for row in result.get("stress_leaf_results") or []:
            if not isinstance(row, dict):
                continue
            target = str(row.get("target"))
            if targets and target not in targets:
                continue
            row_leaf_keys = hit_stream_probe.unique_row_leaf_keys(row)
            if not row_leaf_keys:
                continue
            key = (
                target,
                int_value(row.get("transfer_index")),
                int_value(row.get("top_k")),
                str(row.get("selector")),
                tuple(
                    (str(item.get("row_key")), tuple(int_value(leaf) for leaf in item.get("leaf_indices") or []))
                    for item in row_leaf_keys
                ),
            )
            old = cases.get(key)
            if old is not None and (
                bool(old.get("source_public_key_verified")),
                bool(old.get("source_below_rho")),
                -float(old.get("source_ops_over_rho") or 10**18),
            ) >= (
                bool(row.get("public_key_verified")),
                bool(row.get("below_rho")),
                -float(row.get("ops_over_rho") or 10**18),
            ):
                continue
            cases[key] = {
                "leaf_selector": row.get("selector"),
                "row_leaf_keys": row_leaf_keys,
                "row_selector": row.get("row_selector") or row_selector,
                "source_below_rho": bool(row.get("below_rho")),
                "source_ops_over_rho": row.get("ops_over_rho"),
                "source_policy": policy_name,
                "source_public_key_verified": bool(row.get("public_key_verified")),
                "source_rank": row.get("rank"),
                "source_relation_count": row.get("relation_count"),
                "source_selected_leaf_count": row.get("selected_leaf_count"),
                "source_selected_row_count": row.get("selected_row_count"),
                "source_verified": bool(row.get("source_verified")),
                "target": target,
                "top_k": int_value(row.get("top_k")),
                "transfer_index": int_value(row.get("transfer_index")),
                "window": window,
            }
    return sorted(
        cases.values(),
        key=lambda row: (
            int_value(row.get("transfer_index")),
            str(row.get("target")),
            str(row.get("leaf_selector")),
            int_value(row.get("top_k")),
            json_key(row.get("row_leaf_keys")),
        ),
    )


def compact_form(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "anchor_coeff": record.get("anchor_coeff"),
        "exact_tail_expression_key": record.get("exact_tail_expression_key"),
        "motif": record.get("motif"),
        "rhs": record.get("rhs"),
        "row_key": record.get("row_key"),
        "support": record.get("support"),
        "tail_support": record.get("tail_support"),
        "terms": record.get("terms"),
    }


def form_records_from_scan(case_id: str, row_key: str, scan: dict[str, Any], order: int) -> list[dict[str, Any]]:
    records = []
    for event_index, event in enumerate(scan.get("relation_events") or []):
        coeffs, rhs, terms = event["form"]
        coeff_list = [int_value(coeff) % order for coeff in coeffs]
        term_list = [int_value(term) for term in terms]
        motif = motif_from_form(coeff_list, term_list, order)
        exact = exact_tail_expression(coeff_list, term_list, order)
        support = [idx for idx, coeff in enumerate(coeff_list) if coeff % order != 0]
        records.append(
            {
                "anchor_coeff": coeff_list[0] if coeff_list else 0,
                "case_id": case_id,
                "coeffs": coeff_list,
                "event_index": event_index,
                "exact_tail_expression_key": json_key(exact),
                "is_p867_motif": motif == P867_MOTIF,
                "motif": motif,
                "motif_key": json_key(motif),
                "order": order,
                "rhs": int_value(rhs) % order,
                "row_key": row_key,
                "support": support,
                "tail_support": exact["tail_support"],
                "terms": term_list,
            }
        )
    return records


def local_derivations(forms: list[dict[str, Any]], expected_secret: Any, order: int) -> list[dict[str, Any]]:
    by_tail: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for form in forms:
        by_tail[str(form.get("exact_tail_expression_key"))].append(form)
    derivations = []
    for exact_key, items in sorted(by_tail.items()):
        if len(items) < 2:
            continue
        sorted_items = sorted(items, key=lambda item: (str(item.get("row_key")), int_value(item.get("anchor_coeff")), int_value(item.get("rhs"))))
        for left_index, left in enumerate(sorted_items):
            for right in sorted_items[left_index + 1 :]:
                anchor_delta = (int_value(left.get("anchor_coeff")) - int_value(right.get("anchor_coeff"))) % order
                rhs_delta = (int_value(left.get("rhs")) - int_value(right.get("rhs"))) % order
                if not invertible(anchor_delta, order):
                    candidate = None
                    matches = False
                else:
                    candidate = (rhs_delta * pow(anchor_delta, -1, order)) % order
                    matches = expected_secret is not None and candidate == int_value(expected_secret) % order
                derivations.append(
                    {
                        "anchor_delta": anchor_delta,
                        "anchors": [left.get("anchor_coeff"), right.get("anchor_coeff")],
                        "candidate_secret": candidate,
                        "exact_tail_expression_key": exact_key,
                        "forms": [compact_form(left), compact_form(right)],
                        "invertible_anchor_delta": candidate is not None,
                        "is_p867_motif": bool(left.get("is_p867_motif") and right.get("is_p867_motif")),
                        "matches_expected_secret": matches,
                        "motif": left.get("motif"),
                        "order": order,
                        "rhs_delta": rhs_delta,
                        "rhs_values": [left.get("rhs"), right.get("rhs")],
                        "row_keys": [left.get("row_key"), right.get("row_key")],
                    }
                )
    return derivations


def analyze_case(
    verifier: Any,
    records: list[dict[str, Any]],
    config_source: dict[str, Any],
    specs_by_target: dict[str, dict[str, dict[str, Any]]],
    probe_args: argparse.Namespace,
    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]],
    case: dict[str, Any],
) -> dict[str, Any]:
    context = hit_stream_probe.scan_case_context(
        verifier,
        records,
        config_source,
        specs_by_target,
        case,
        probe_args,
        context_cache,
    )
    rows_for_union = []
    built_for_union = {}
    form_records = []
    row_scans = []
    direct_ops = 0
    generic_rho = 0
    orders = set()
    case_id = f"{case.get('window')}:{case.get('transfer_index')}:{case.get('target')}:{case.get('leaf_selector')}:{case.get('top_k')}"
    for item in hit_stream_probe.unique_row_leaf_keys(case):
        row_key = str(item["row_key"])
        if row_key not in context["built_by_row"]:
            row_scans.append({"row_key": row_key, "error": "row context not reconstructed"})
            continue
        built = context["built_by_row"][row_key]
        order = int_value(built.get("order"))
        orders.add(order)
        scan = direct_witness_probe.scan_selected(
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
        form_records.extend(form_records_from_scan(case_id, row_key, scan, order))
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
    union = direct_witness_probe.union_derive(verifier, rows_for_union, built_for_union, "_scan")
    order = next(iter(orders)) if len(orders) == 1 else 0
    derivations = local_derivations(form_records, union.get("union_derived_secret"), order) if order else []
    p867_derivations = [row for row in derivations if row.get("is_p867_motif")]
    matched = [row for row in derivations if row.get("matches_expected_secret")]
    matched_p867 = [row for row in p867_derivations if row.get("matches_expected_secret")]
    return {
        **case,
        "case_id": case_id,
        "direct_ops": direct_ops,
        "direct_ops_over_rho": ratio(direct_ops, generic_rho),
        "generic_rho_steps": generic_rho,
        "p867_motif_derivations": p867_derivations,
        "p867_motif_form_count": sum(1 for form in form_records if form.get("is_p867_motif")),
        "p867_motif_forms": [compact_form(form) for form in form_records if form.get("is_p867_motif")][:16],
        "p867_motif_matched_derivation_count": len(matched_p867),
        "p867_motif_verified_below_rho": bool(matched_p867 and direct_ops < generic_rho),
        "reconstructed_error_count": len(context.get("errors") or []) + sum(1 for row in row_scans if row.get("error")),
        "reconstructed_errors": context.get("errors") or [],
        "relation_form_count": len(form_records),
        "row_scans": row_scans,
        "same_tail_derivation_count": len(derivations),
        "same_tail_derivations": derivations[:16],
        "same_tail_matched_derivation_count": len(matched),
        "union_derived_secret": union.get("union_derived_secret"),
        "union_public_key_verified": bool(union.get("union_public_key_verified")),
        "union_rank": union.get("union_rank"),
        "union_relation_count": union.get("union_relation_count"),
    }


def compact_case(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": row.get("case_id"),
        "direct_ops_over_rho": row.get("direct_ops_over_rho"),
        "leaf_selector": row.get("leaf_selector"),
        "p867_motif_form_count": row.get("p867_motif_form_count"),
        "p867_motif_matched_derivation_count": row.get("p867_motif_matched_derivation_count"),
        "relation_form_count": row.get("relation_form_count"),
        "row_leaf_keys": row.get("row_leaf_keys"),
        "same_tail_matched_derivation_count": row.get("same_tail_matched_derivation_count"),
        "target": row.get("target"),
        "top_k": row.get("top_k"),
        "transfer_index": row.get("transfer_index"),
        "union_derived_secret": row.get("union_derived_secret"),
        "union_public_key_verified": row.get("union_public_key_verified"),
        "union_rank": row.get("union_rank"),
        "union_relation_count": row.get("union_relation_count"),
        "window": row.get("window"),
    }


def determine_claim(summary: dict[str, Any]) -> str:
    if int_value(summary.get("reconstruction_error_count")) and not int_value(summary.get("p867_motif_verified_below_rho_case_count")):
        return "NEGATIVE_RESULT_P868_RECONSTRUCTION_ERRORS_BLOCK_FRESH_MOTIF_AUDIT"
    if int_value(summary.get("p867_motif_verified_below_rho_case_count")) >= 2 and int_value(summary.get("p867_motif_verified_window_count")) >= 2:
        return "P868_FRESH_P231_GENERATOR_REEMITS_P867_SKELETON_MULTIWINDOW"
    if int_value(summary.get("p867_motif_verified_below_rho_case_count")) >= 1:
        return "P868_FRESH_P231_GENERATOR_REEMITS_P867_SKELETON"
    if int_value(summary.get("p867_motif_form_count")) > 0:
        return "P868_FRESH_P231_GENERATOR_EMITS_P867_FORMS_WITHOUT_VERIFIED_BELOW_RHO_PAIR"
    return "NEGATIVE_RESULT_P868_NO_FRESH_P867_SKELETON_EMISSION"


def summarize(cases: list[dict[str, Any]], source_cases: list[dict[str, Any]], windows: list[str]) -> dict[str, Any]:
    verified = [row for row in cases if row.get("union_public_key_verified")]
    p867_cases = [row for row in cases if int_value(row.get("p867_motif_form_count")) > 0]
    p867_verified = [row for row in cases if int_value(row.get("p867_motif_matched_derivation_count")) > 0]
    p867_below = [row for row in p867_verified if row.get("direct_ops_over_rho") is not None and float(row["direct_ops_over_rho"]) < 1.0]
    p867_unique_groups = {
        (
            str(row.get("target")),
            int_value(row.get("transfer_index")),
            int_value(row.get("union_derived_secret")),
            tuple(
                (str(item.get("row_key")), tuple(int_value(leaf) for leaf in item.get("leaf_indices") or []))
                for item in row.get("row_leaf_keys") or []
            ),
        )
        for row in p867_below
    }
    source_pk = [row for row in source_cases if row.get("source_public_key_verified")]
    source_pk_below = [row for row in source_pk if row.get("source_below_rho")]
    return {
        "fresh_window_count": len(windows),
        "reconstructed_case_count": len(cases),
        "reconstruction_error_count": sum(int_value(row.get("reconstructed_error_count")) for row in cases),
        "source_below_rho_public_key_verified_case_count": len(source_pk_below),
        "source_case_count": len(source_cases),
        "source_public_key_verified_case_count": len(source_pk),
        "source_target_counts": dict(Counter(str(row.get("target")) for row in source_cases).most_common()),
        "union_public_key_verified_case_count": len(verified),
        "verified_below_rho_case_count": sum(
            1 for row in verified if row.get("direct_ops_over_rho") is not None and float(row["direct_ops_over_rho"]) < 1.0
        ),
        "relation_form_count": sum(int_value(row.get("relation_form_count")) for row in cases),
        "p867_motif_form_count": sum(int_value(row.get("p867_motif_form_count")) for row in cases),
        "p867_motif_emitting_case_count": len(p867_cases),
        "p867_motif_emitting_window_count": len({str(row.get("window")) for row in p867_cases}),
        "p867_motif_verified_derivation_case_count": len(p867_verified),
        "p867_motif_verified_below_rho_case_count": len(p867_below),
        "p867_motif_verified_unique_scalar_group_count": len(p867_unique_groups),
        "p867_motif_verified_transfer_count": len({int_value(row.get("transfer_index")) for row in p867_below}),
        "p867_motif_verified_window_count": len({str(row.get("window")) for row in p867_below}),
        "same_tail_derivation_count": sum(int_value(row.get("same_tail_derivation_count")) for row in cases),
        "same_tail_matched_derivation_count": sum(int_value(row.get("same_tail_matched_derivation_count")) for row in cases),
        "windows": windows,
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    targets = {target.strip() for target in args.targets.split(",") if target.strip()}
    windows = list(args.windows)
    source_payloads = [(window, source_path(window), load_json(source_path(window))) for window in windows]
    source_cases = [
        case
        for window, _path, source in source_payloads
        for case in iter_source_cases(source, window, targets)
    ]
    verifier = None
    records = None
    config_source = None
    specs_by_target = None
    cases = []
    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]] = {}
    build_cache: dict[str, tuple[Any, list[dict[str, Any]], dict[str, Any], dict[str, dict[str, dict[str, Any]]], argparse.Namespace]] = {}
    for window, path, source in source_payloads:
        params = repair_probe.source_parameters(source)
        probe_args = repair_probe.probe_args_from_source(source)
        cache_key = json_key(
            {
                "bank_source": params.get("bank_source"),
                "config_source": params.get("config_source"),
                "direct_source": params.get("direct_source"),
                "transfer_source": params.get("transfer_source"),
                "radius": params.get("radius"),
            }
        )
        if cache_key not in build_cache:
            verifier, records, config_source, specs_by_target = repair_probe.build_specs(params)
            build_cache[cache_key] = (verifier, records, config_source, specs_by_target, probe_args)
        else:
            verifier, records, config_source, specs_by_target, probe_args = build_cache[cache_key]
        for case in [row for row in source_cases if row.get("window") == window]:
            cases.append(
                analyze_case(
                    verifier,
                    records,
                    config_source,
                    specs_by_target,
                    probe_args,
                    context_cache,
                    case,
                )
            )
    summary = summarize(cases, source_cases, windows)
    claim = determine_claim(summary)
    summary["claim_status"] = claim
    p867_below = [
        row
        for row in cases
        if row.get("p867_motif_verified_below_rho")
    ]
    best = sorted(
        [row for row in cases if row.get("union_public_key_verified")],
        key=lambda row: (
            float(row.get("direct_ops_over_rho") or 10**18),
            -int_value(row.get("p867_motif_matched_derivation_count")),
            str(row.get("case_id")),
        ),
    )[:16]
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
            "source_windows": {window: str(path) for window, path, _source in source_payloads},
        },
        "best_verified_cases": [compact_case(row) for row in best],
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P868_") else "NEGATIVE RESULT",
        "created_at": now_iso(),
        "fresh_p867_verified_below_rho_cases": [
            {
                **compact_case(row),
                "p867_motif_derivations": row.get("p867_motif_derivations"),
                "p867_motif_forms": row.get("p867_motif_forms"),
            }
            for row in p867_below[:24]
        ],
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP verifier harness.",
            "FRESH-WINDOW BOUNDARY: source windows are later than the P866/P867 windows but remain in the p231 fixed-row family.",
            "GENERATOR-OUTPUT BOUNDARY: public fixed-row artifacts choose rows/leaves; motif detection is still post-scan.",
            "SAME-CONTEXT BOUNDARY: local derivations subtract only forms from the same reconstructed challenge/public-key context.",
            "POLLARD-RHO BOUNDARY: this is relation-lane bridge evidence, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p868_p231_fresh_skeleton_generator_audit",
        "parameters": {
            "p867_motif": P867_MOTIF,
            "targets": sorted(targets),
            "windows": windows,
        },
        "red_team_handoff": {
            "artifact_paths": [str(args.out), str(args.contract), str(Path(__file__))],
            "assumptions": [
                "The selected fixed-row source artifacts are fresh relative to P866/P867.",
                "The P867 motif alone is used as calibration; no P867 form rows are read by P868.",
                "A motif emission is only a generator-output signal until public pre-scan features predict it.",
            ],
            "claim_or_task": "Test whether fresh p231 fixed-row generator outputs reemit the P867 normalized tail skeleton.",
            "evidence_so_far": [
                f"Fresh P867 motif below-rho cases: {summary.get('p867_motif_verified_below_rho_case_count')}.",
                f"Fresh P867 motif windows: {summary.get('p867_motif_verified_window_count')}.",
                f"Reconstructed cases: {summary.get('reconstructed_case_count')}; forms: {summary.get('relation_form_count')}.",
            ],
            "failure_modes": [
                "Motif emission may be specific to adjacent p231 fixed-row family windows.",
                "Post-scan motif detection is not yet a public selector.",
                "Local same-context derivations still do not create a legal cross-public-key target descent.",
            ],
            "next_concrete_action": (
                "Build P869 to train/evaluate public pre-scan predictors for the emitted P867 motif using row keys, leaf indices, and leaf public features, then require held-out prediction before relation-event reconstruction."
            ),
            "status": "OBSERVATION" if claim.startswith("P868_") else "NEGATIVE RESULT",
        },
        "schema": SCHEMA,
        "summary": summary,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--windows", nargs="+", default=list(DEFAULT_WINDOWS))
    parser.add_argument("--targets", default=DEFAULT_TARGET)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
