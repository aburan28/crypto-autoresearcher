#!/usr/bin/env python3
"""Score public leaves by residual-nullspace asymmetry and replay candidates.

The current order-11779 frontier is rank 15/16: column 6 is free, but the
recent source/direct certificates keep producing target-eliminated rows whose
projection onto the remaining nullspace cancels.  This scout moves one step
earlier than certificate export.  It ranks public selected-leaf candidates by
their signed scout contribution against the residual null vector, then replays
bounded row-pair prefixes through the normal direct verifier and the existing
target-eliminated nullspace classifier.

This is a scheduling experiment.  A nonzero leaf charge is not a relation by
itself; it is only a public selector signal that must survive verifier export,
target elimination, and the rank/frontier gate.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_direct_witness_probe as direct_witness_probe
import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_low_term_total2_ffe_hit_stream_probe as hit_stream_probe
import low_term_total2_deficiency_direction_scorer as deficiency
import low_term_total2_nullspace_projection_obstruction_scout as obstruction
import low_term_total2_public_prefix_shared_leaf_repair_probe as repair_probe
import low_term_total2_source_relation_equation_certificate as certificate_probe
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_SOURCE = (
    STATE_DIR
    / "frontier_public_leaf_policy_p231_frozen_prefix_fixed_row_16272_16279_col15_selector_expanded_probe.json"
)
DEFAULT_FRONTIER_LIST_SOURCE = (
    STATE_DIR
    / "low_term_total2_nullspace_source_candidate_scout_16264_16279_direct_verified_order11779_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_nullspace_asymmetric_leaf_scout_16272_16279_order11779_probe.json"
DEFAULT_MODES = "free_nonzero,null_abs,free_one_sided,positive_free,negative_free"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def int_value(value: Any, default: int = 0) -> int:
    return factor_bank.int_value(value, default)


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def parse_csv(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def parse_int_csv(raw: str | None) -> set[int]:
    return {int(item) for item in parse_csv(raw)}


def parse_null_vector(raw: str) -> list[int]:
    return [int(item.strip()) for item in raw.split(",") if item.strip()]


def resolve_frontier_paths(raw: str, list_source: Path) -> list[Path]:
    paths = [Path(item) for item in parse_csv(raw)]
    if paths:
        return paths
    source = load_json(list_source)
    artifacts = (source.get("artifacts") or {}).get("frontier_certificates") or []
    return [Path(item) for item in artifacts]


def frontier_nullspace(frontier_paths: list[Path], order: int) -> tuple[list[dict[str, Any]], int]:
    frontier_certificates = factor_bank.load_certificates(frontier_paths)
    frontier_rows, _rhs, _rows_by_key, factor_count = deficiency.row_vectors(
        frontier_certificates,
        order,
    )
    rref_rows, pivot_columns = deficiency.rref_mod(frontier_rows, order)
    _free_columns, null_basis = deficiency.nullspace_basis(
        rref_rows,
        pivot_columns,
        factor_count,
        order,
    )
    return null_basis, factor_count


def signed_null_coeff(null_vector: list[int], index: int, order: int) -> int:
    if index < 0 or index >= len(null_vector):
        return 0
    return obstruction.signed(int(null_vector[index]) % order, order)


def scout_by_pos(built: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {
        int_value(scout.get("scout_pos")): scout
        for scout in built.get("scouts") or []
        if isinstance(scout, dict) and scout.get("scout_pos") is not None
    }


def leaf_scouts(context: dict[str, Any], leaf_index: int) -> list[dict[str, Any]]:
    leaves = context["components"].get("leaves") or []
    if leaf_index < 0 or leaf_index >= len(leaves):
        return []
    by_pos = scout_by_pos(context["built"])
    out = []
    seen: set[int] = set()
    for pos in leaves[leaf_index].get("scout_positions") or []:
        scout = by_pos.get(int_value(pos))
        if scout is None:
            continue
        key = int_value(scout.get("scout_pos"))
        if key in seen:
            continue
        seen.add(key)
        out.append(scout)
    return out


def leaf_null_profile(
    context: dict[str, Any],
    leaf_index: int,
    null_vector: list[int],
    order: int,
    free_column: int,
) -> dict[str, Any]:
    contributions = []
    support: Counter[int] = Counter()
    null_support: Counter[int] = Counter()
    projection = 0
    signed_charge = 0
    free_term_count = 0
    opposite_term_count = 0
    for scout in leaf_scouts(context, leaf_index):
        scout_projection = 0
        scout_signed_charge = 0
        scout_terms = []
        for index_raw, sign_raw in scout.get("signed_terms") or []:
            index = int_value(index_raw)
            sign = int_value(sign_raw)
            support[index] += 1
            coeff_signed = signed_null_coeff(null_vector, index, order)
            if coeff_signed:
                null_support[index] += 1
            if index == free_column:
                free_term_count += 1
            if index < len(null_vector) and coeff_signed == -signed_null_coeff(null_vector, free_column, order):
                opposite_term_count += 1
            contribution_signed = sign * coeff_signed
            contribution_mod = ((sign % order) * (int(null_vector[index]) % order)) % order if index < len(null_vector) else 0
            projection = (projection + contribution_mod) % order
            scout_projection = (scout_projection + contribution_mod) % order
            signed_charge += contribution_signed
            scout_signed_charge += contribution_signed
            scout_terms.append(
                {
                    "contribution_signed": contribution_signed,
                    "factor_index": index,
                    "null_coefficient_signed": coeff_signed,
                    "sign": sign,
                }
            )
        contributions.append(
            {
                "projection_signed": obstruction.signed(scout_projection, order),
                "scout_pos": int_value(scout.get("scout_pos")),
                "signed_charge": scout_signed_charge,
                "terms": scout_terms,
            }
        )
    projection_signed = obstruction.signed(projection, order)
    return {
        "abs_projection_signed": abs(projection_signed),
        "free_minus_opposite_term_count": free_term_count - opposite_term_count,
        "free_term_count": free_term_count,
        "has_nonzero_projection": projection_signed != 0,
        "leaf_index": int(leaf_index),
        "null_support": sorted(null_support),
        "null_support_size": len(null_support),
        "opposite_term_count": opposite_term_count,
        "projection_signed": projection_signed,
        "scout_contributions": contributions,
        "scout_count": len(contributions),
        "signed_charge": signed_charge,
        "support": sorted(support),
        "support_size": len(support),
        "touches_free_column": bool(free_term_count),
    }


def candidate_leaf_indices(context: dict[str, Any], row_key: str) -> list[int]:
    feature_rows = context.get("feature_rows_by_row", {}).get(row_key, [])
    feature_indices = [
        int_value(row.get("leaf_index"))
        for row in feature_rows
        if isinstance(row, dict) and row.get("leaf_index") is not None
    ]
    if feature_indices:
        return sorted(set(feature_indices))
    leaves = context["components_by_row"].get(row_key, {}).get("leaves") or []
    return list(range(len(leaves)))


def score_profile(profile: dict[str, Any], mode: str) -> tuple[Any, ...]:
    leaf = int_value(profile.get("leaf_index"))
    abs_projection = int_value(profile.get("abs_projection_signed"))
    free_terms = int_value(profile.get("free_term_count"))
    signed_charge = int_value(profile.get("signed_charge"))
    support_size = int_value(profile.get("support_size"), 10**9)
    nonzero = bool(profile.get("has_nonzero_projection"))
    free_one_sided = int_value(profile.get("free_minus_opposite_term_count"))
    if mode == "free_nonzero":
        return (not (free_terms and nonzero), -abs_projection, -free_terms, support_size, leaf)
    if mode == "null_abs":
        return (-abs_projection, not nonzero, -free_terms, support_size, leaf)
    if mode == "free_one_sided":
        return (-abs(free_one_sided), not (free_terms and nonzero), -abs_projection, support_size, leaf)
    if mode == "positive_free":
        return (not (free_terms and signed_charge > 0), -signed_charge, support_size, leaf)
    if mode == "negative_free":
        return (not (free_terms and signed_charge < 0), signed_charge, support_size, leaf)
    raise ValueError(f"unknown nullspace leaf mode: {mode}")


def ranked_leaf_profiles(
    context: dict[str, Any],
    row_key: str,
    mode: str,
    null_vector: list[int],
    order: int,
    free_column: int,
) -> list[dict[str, Any]]:
    row_context = {
        "built": context["built_by_row"][row_key],
        "components": context["components_by_row"][row_key],
    }
    profiles = [
        leaf_null_profile(row_context, leaf, null_vector, order, free_column)
        for leaf in candidate_leaf_indices(context, row_key)
    ]
    return sorted(profiles, key=lambda profile: score_profile(profile, mode))


def direct_unique_events(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    seen: set[tuple[tuple[int, ...], int]] = set()
    for row in rows:
        scan = row.get("_scan") if isinstance(row.get("_scan"), dict) else {}
        for event in scan.get("relation_events") or []:
            coeffs, rhs, _terms = event["form"]
            key = (tuple(int(coeff) for coeff in coeffs), int(rhs))
            if key in seen:
                continue
            seen.add(key)
            events.append(event)
    return events


def projection_status_report(
    cert: dict[str, Any],
    null_basis: list[dict[str, Any]],
    factor_count: int,
    order: int,
) -> tuple[Counter[str], list[dict[str, Any]]]:
    status_counts: Counter[str] = Counter()
    samples = []
    for relation in factor_bank.target_eliminated_rows(cert):
        if relation.get("relation_status") != "TARGET_ELIMINATED_FACTOR_RELATION":
            continue
        report = obstruction.relation_report(cert, relation, null_basis, factor_count, order)
        status = str(report.get("status"))
        status_counts[status] += 1
        if len(samples) < 6 or status == "NONZERO_NULLSPACE_PROJECTION":
            samples.append(
                {
                    "factor_support": report.get("factor_support"),
                    "left_form": report.get("left_form"),
                    "pair": report.get("pair"),
                    "projections": report.get("projections"),
                    "q_coeffs": report.get("q_coeffs"),
                    "right_form": report.get("right_form"),
                    "status": status,
                }
            )
    return status_counts, samples


def evaluate_selection(
    verifier: Any,
    context: dict[str, Any],
    pair: dict[str, Any],
    label: str,
    row_leaf_map: dict[str, set[int]],
    selected_profiles: dict[str, list[dict[str, Any]]],
    null_basis: list[dict[str, Any]],
    factor_count: int,
    order: int,
) -> dict[str, Any] | None:
    rows_for_union = []
    built_for_union = {}
    row_results = []
    direct_ops = 0
    generic_rho = 0
    case_order = 0
    for row_key, leaves in sorted(row_leaf_map.items()):
        if row_key not in context["built_by_row"]:
            return None
        built = context["built_by_row"][row_key]
        components = context["components_by_row"][row_key]
        local_args = context["local_args_by_row"][row_key]
        scan = direct_witness_probe.scan_selected(
            verifier,
            built,
            components,
            {int(leaf) for leaf in leaves},
            local_args,
        )
        rows_for_union.append({"row_key": row_key, "_scan": scan})
        built_for_union[row_key] = built
        direct_ops += int_value(scan.get("preassociation_filter_ops"))
        generic_rho = max(generic_rho, int_value(built.get("generic_rho_steps")))
        case_order = case_order or int_value(built.get("order"))
        row_results.append(
            {
                "preassociation_filter_ops": int_value(scan.get("preassociation_filter_ops")),
                "rank": int_value(scan.get("rank")),
                "relation_count": int_value(scan.get("relation_count")),
                "row_key": row_key,
                "row_public_key_verified": bool(scan.get("row_public_key_verified")),
                "selected_hit_events": int_value(scan.get("selected_hit_events")),
                "selected_hit_roots": int_value(scan.get("selected_hit_roots")),
                "selected_leaf_count": int_value(scan.get("selected_leaf_count")),
                "selected_leaf_indices": sorted(int(leaf) for leaf in leaves),
            }
        )
    union = direct_witness_probe.union_derive(verifier, rows_for_union, built_for_union, "_scan")
    events = direct_unique_events(rows_for_union)
    forms = [certificate_probe.compact_form(event, case_order) for event in events]
    cert = {
        "_artifact": "in_memory_nullspace_asymmetric_leaf_scout",
        "_artifact_offset": 0,
        "certificate_status": (
            "PUBLIC_DIRECT_RELATION_EQUATIONS_VERIFY_PUBLIC_KEY"
            if bool(union.get("union_public_key_verified"))
                else "PUBLIC_DIRECT_RELATION_EQUATIONS_NEED_REVIEW"
        ),
        "derived_secret": union.get("union_derived_secret"),
        "direct_ops_over_rho": ratio(direct_ops, generic_rho),
        "expected_secret": union.get("union_derived_secret"),
        "forms": forms,
        "forms_count": len(forms),
        "order": case_order,
        "public_key_verified": bool(union.get("union_public_key_verified")),
        "rank": int_value(union.get("union_rank")),
        "rowspace_derives_expected_secret": bool(union.get("union_public_key_verified")),
        "selected": {
            "direct_ops": direct_ops,
            "direct_ops_over_rho": ratio(direct_ops, generic_rho),
            "rho": generic_rho,
            "row_keys": sorted(row_leaf_map),
            "selected_leaf_indices_by_row": {
                row_key: sorted(leaves) for row_key, leaves in sorted(row_leaf_map.items())
            },
            "selector": label,
            "target": pair.get("target"),
            "top_k": int_value(pair.get("top_k")),
            "transfer_index": int_value(pair.get("transfer_index")),
        },
    }
    status_counts, samples = projection_status_report(cert, null_basis, factor_count, order)
    profile_values = [
        profile
        for profiles in selected_profiles.values()
        for profile in profiles
    ]
    leaf_nonzero_count = sum(1 for profile in profile_values if profile.get("has_nonzero_projection"))
    leaf_free_nonzero_count = sum(
        1
        for profile in profile_values
        if profile.get("touches_free_column") and profile.get("has_nonzero_projection")
    )
    return {
        "direct_below_rho": bool(generic_rho and direct_ops < generic_rho),
        "direct_ops": direct_ops,
        "direct_ops_over_rho": ratio(direct_ops, generic_rho),
        "_candidate_certificate": cert,
        "forms": [
            {
                "coeff_support": [
                    idx
                    for idx, coeff in enumerate((form.get("coeffs") or [])[1:])
                    if int_value(coeff) % max(1, case_order)
                ],
                "terms": form.get("terms") or [],
            }
            for form in forms[:12]
        ],
        "forms_count": len(forms),
        "generic_rho_steps": generic_rho,
        "label": label,
        "leaf_free_nonzero_count": leaf_free_nonzero_count,
        "leaf_nonzero_count": leaf_nonzero_count,
        "projection_samples": samples,
        "projection_status_counts": dict(sorted(status_counts.items())),
        "row_keys": sorted(row_leaf_map),
        "row_results": row_results,
        "selected_leaf_indices_by_row": {
            row_key: sorted(leaves) for row_key, leaves in sorted(row_leaf_map.items())
        },
        "selected_leaf_profiles": {
            row_key: profiles for row_key, profiles in sorted(selected_profiles.items())
        },
        "target": pair.get("target"),
        "target_eliminated_row_count": sum(status_counts.values()),
        "top_k": int_value(pair.get("top_k")),
        "transfer_index": int_value(pair.get("transfer_index")),
        "union_derived_secret": union.get("union_derived_secret"),
        "union_public_key_verified": bool(union.get("union_public_key_verified")),
        "union_rank": int_value(union.get("union_rank")),
        "union_relation_count": int_value(union.get("union_relation_count")),
    }


def compact_pair(pair: dict[str, Any]) -> dict[str, Any]:
    return {
        "row_keys": pair.get("row_keys") or [],
        "row_selector": pair.get("row_selector"),
        "source_policy": pair.get("source_policy"),
        "source_row_count": len(pair.get("source_rows") or []),
        "target": pair.get("target"),
        "top_k": int_value(pair.get("top_k")),
        "transfer_index": int_value(pair.get("transfer_index")),
    }


def summarize(results: list[dict[str, Any]], pairs: list[dict[str, Any]]) -> dict[str, Any]:
    aggregate = Counter()
    for result in results:
        aggregate.update(result.get("projection_status_counts") or {})
    verified = [row for row in results if row.get("union_public_key_verified")]
    direct_below = [row for row in verified if row.get("direct_below_rho")]
    leaf_signal = [row for row in results if int_value(row.get("leaf_free_nonzero_count")) > 0]
    nonzero_projection = [
        row
        for row in results
        if int_value((row.get("projection_status_counts") or {}).get("NONZERO_NULLSPACE_PROJECTION")) > 0
    ]
    verified_nonzero_projection = [
        row for row in nonzero_projection if row.get("union_public_key_verified")
    ]
    best_leaf_signal = sorted(
        leaf_signal,
        key=lambda row: (
            not bool(row.get("union_public_key_verified")),
            float(row.get("direct_ops_over_rho") or 10**9),
            -int_value(row.get("leaf_free_nonzero_count")),
            str(row.get("label")),
        ),
    )[:8]
    best_verified = sorted(
        verified,
        key=lambda row: (
            float(row.get("direct_ops_over_rho") or 10**9),
            -int_value(row.get("leaf_free_nonzero_count")),
            str(row.get("label")),
        ),
    )[:8]
    if verified_nonzero_projection:
        claim_status = "NONZERO_NULLSPACE_PROJECTION_ASYMMETRIC_LEAF_FOUND"
    elif nonzero_projection:
        claim_status = "UNVERIFIED_NONZERO_NULLSPACE_PROJECTION_TRACE_FOUND"
    elif verified and leaf_signal:
        claim_status = "NEGATIVE_RESULT_ASYMMETRIC_LEAF_SIGNAL_DID_NOT_SURVIVE_EXPORT"
    elif leaf_signal:
        claim_status = "NEGATIVE_RESULT_ASYMMETRIC_LEAF_SIGNAL_DID_NOT_VERIFY"
    elif results:
        claim_status = "NEGATIVE_RESULT_NO_ASYMMETRIC_LEAF_PROJECTION_FOUND"
    else:
        claim_status = "NO_SELECTIONS_TESTED"
    keep = (
        "label",
        "target",
        "transfer_index",
        "top_k",
        "row_keys",
        "direct_ops_over_rho",
        "leaf_free_nonzero_count",
        "union_public_key_verified",
        "union_rank",
        "union_relation_count",
        "projection_status_counts",
    )
    return {
        "claim_status": claim_status,
        "direct_below_rho_verified_count": len(direct_below),
        "leaf_free_nonzero_signal_count": len(leaf_signal),
        "nonzero_projection_selection_count": len(nonzero_projection),
        "verified_nonzero_projection_selection_count": len(verified_nonzero_projection),
        "pair_count": len(pairs),
        "projection_status_counts": dict(sorted(aggregate.items())),
        "tested_selection_count": len(results),
        "verified_selection_count": len(verified),
        "best_leaf_signal": [
            {key: row.get(key) for key in keep}
            for row in best_leaf_signal
        ],
        "best_verified": [
            {key: row.get(key) for key in keep}
            for row in best_verified
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--frontier-certificates", default="")
    parser.add_argument("--frontier-list-source", type=Path, default=DEFAULT_FRONTIER_LIST_SOURCE)
    parser.add_argument("--targets", default="22050.cf1@11731")
    parser.add_argument("--transfers", default="")
    parser.add_argument("--modes", default=DEFAULT_MODES)
    parser.add_argument("--max-pairs", type=int, default=8)
    parser.add_argument("--max-prefix", type=int, default=5)
    parser.add_argument("--order", type=int, default=11779)
    parser.add_argument("--free-column", type=int, default=6)
    parser.add_argument("--null-vector", default="1,1,11778,1,1,11778,1,0,0,0,0,0,0,0,0,0")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = load_json(args.source)
    params = repair_probe.source_parameters(source)
    probe_args = repair_probe.probe_args_from_source(source)
    targets = set(parse_csv(args.targets))
    transfers = parse_int_csv(args.transfers)
    modes = parse_csv(args.modes) or parse_csv(DEFAULT_MODES)
    null_vector = parse_null_vector(args.null_vector)
    frontier_paths = resolve_frontier_paths(args.frontier_certificates, args.frontier_list_source)
    null_basis, factor_count = frontier_nullspace(frontier_paths, int_value(args.order, 11779))
    verifier, records, config_source, specs_by_target = repair_probe.build_specs(params)
    pairs = repair_probe.iter_source_pairs(source, targets, transfers)[: max(0, int_value(args.max_pairs, 8))]
    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]] = {}
    results = []
    errors = []

    for pair in pairs:
        seed_case = {
            "target": pair["target"],
            "transfer_index": pair["transfer_index"],
            "top_k": pair["top_k"],
            "row_leaf_keys": [{"row_key": row_key, "leaf_indices": [0]} for row_key in pair["row_keys"]],
        }
        try:
            context = hit_stream_probe.scan_case_context(
                verifier,
                records,
                config_source,
                specs_by_target,
                seed_case,
                probe_args,
                context_cache,
            )
            rankings_by_mode: dict[str, dict[str, list[dict[str, Any]]]] = {}
            for mode in modes:
                rankings_by_mode[mode] = {
                    row_key: ranked_leaf_profiles(
                        context,
                        row_key,
                        mode,
                        null_vector,
                        int_value(args.order, 11779),
                        int_value(args.free_column, 6),
                    )
                    for row_key in pair["row_keys"]
                }
                for prefix in range(1, max(1, int_value(args.max_prefix, 5)) + 1):
                    row_leaf_map = {
                        row_key: {
                            int(profile["leaf_index"])
                            for profile in rankings_by_mode[mode][row_key][:prefix]
                        }
                        for row_key in pair["row_keys"]
                    }
                    selected_profiles = {
                        row_key: rankings_by_mode[mode][row_key][:prefix]
                        for row_key in pair["row_keys"]
                    }
                    result = evaluate_selection(
                        verifier,
                        context,
                        pair,
                        f"{mode}:prefix{prefix}",
                        row_leaf_map,
                        selected_profiles,
                        null_basis,
                        factor_count,
                        int_value(args.order, 11779),
                    )
                    if result:
                        results.append(result)
        except Exception as error:  # Preserve replay failures for red-team inspection.
            errors.append({**compact_pair(pair), "error": str(error)})

    results.sort(
        key=lambda row: (
            -int_value((row.get("projection_status_counts") or {}).get("NONZERO_NULLSPACE_PROJECTION")),
            not bool(row.get("union_public_key_verified")),
            float(row.get("direct_ops_over_rho") or 10**9),
            -int_value(row.get("leaf_free_nonzero_count")),
            str(row.get("label")),
        )
    )
    summary = summarize(results, pairs)
    certificates = []
    seen_certificates: set[str] = set()
    for result in results:
        cert = result.pop("_candidate_certificate", None)
        if not isinstance(cert, dict):
            continue
        if not result.get("union_public_key_verified"):
            continue
        if not int_value((result.get("projection_status_counts") or {}).get("NONZERO_NULLSPACE_PROJECTION")):
            continue
        key = json.dumps(cert.get("forms") or [], sort_keys=True, separators=(",", ":"))
        if key in seen_certificates:
            continue
        seen_certificates.add(key)
        cert["_artifact_offset"] = len(certificates)
        certificates.append(cert)
    summary["candidate_certificate_count"] = len(certificates)
    payload = {
        "artifacts": {
            "frontier_certificates": [str(path) for path in frontier_paths],
            "frontier_list_source": str(args.frontier_list_source),
            "source": str(args.source),
        },
        "certificates": certificates,
        "claim_status": summary["claim_status"],
        "created_at": now_iso(),
        "errors": errors[:40],
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: signed leaf nullspace charge is a public selector signal before relation export.",
            "NO SPEEDUP CLAIM: any positive must still pass direct certificate, rank, frontier, and rho-normalized cost gates.",
            "OPEN: if nullspace charge repeatedly cancels at export, the next candidate needs a relation-generation mechanism that preserves asymmetric coefficients, not just asymmetric leaf support.",
        ],
        "parameters": {
            "free_column": int_value(args.free_column, 6),
            "max_pairs": max(0, int_value(args.max_pairs, 8)),
            "max_prefix": max(1, int_value(args.max_prefix, 5)),
            "modes": modes,
            "null_vector": null_vector,
            "order": int_value(args.order, 11779),
            "targets": sorted(targets),
            "transfers": sorted(transfers),
        },
        "source_pairs": [compact_pair(pair) for pair in pairs],
        "results": results[:120],
        "schema": "ecdlp.low_term_total2_nullspace_asymmetric_leaf_scout.v1",
        "summary": summary,
    }
    write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
