#!/usr/bin/env python3
"""Probe one- and two-leaf anti-cancellation extensions of source selections.

The null-vector source-row scorer found below-rho rows with free-column contact,
but exact replay showed their target-eliminated export forms collapse to zero,
usually through equal-opposite two-column support.  This bounded probe keeps the
scored source-row leaves fixed and tries one or two additional ranked leaves to
see whether export can acquire a third non-cancelling null-supported column.

This is still a scheduling/source-generation experiment.  Any positive hit must
pass the usual rank-extension, repair-bank, family-holdout, source-cost,
sparse-LA, and fresh-target gates before promotion.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any

import low_term_total2_nullspace_asymmetric_leaf_scout as null_scout
import low_term_total2_public_prefix_shared_leaf_repair_probe as repair_probe
import low_term_total2_ruleprefix2_null_vector_source_row_scorer as source_scorer
import low_term_total2_ruleprefix2_source_row_leaf_replay as leaf_replay
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


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


def parse_int_set(raw: str | None) -> set[int]:
    values: set[int] = set()
    if not raw:
        return values
    for chunk in raw.replace(";", ",").split(","):
        chunk = chunk.strip()
        if chunk:
            values.add(int(chunk))
    return values


def null_support_union(profiles_by_row: dict[str, list[dict[str, Any]]]) -> set[int]:
    support: set[int] = set()
    for profiles in profiles_by_row.values():
        for profile in profiles:
            support.update(int_value(item) for item in profile.get("null_support") or [])
    return support


def extension_score(
    profile: dict[str, Any],
    selected_null_support: set[int],
    verifier_aware: bool = False,
    prefer_support_columns: set[int] | None = None,
    avoid_support_columns: set[int] | None = None,
) -> tuple[Any, ...]:
    leaf = int_value(profile.get("leaf_index"))
    null_support = {int_value(item) for item in profile.get("null_support") or []}
    new_support = len(null_support - selected_null_support)
    has_nonzero = bool(profile.get("has_nonzero_projection"))
    touches_free = bool(profile.get("touches_free_column"))
    abs_projection = int_value(profile.get("abs_projection_signed"))
    free_one_sided = abs(int_value(profile.get("free_minus_opposite_term_count")))
    signed_charge = abs(int_value(profile.get("signed_charge")))
    support_size = int_value(profile.get("support_size"), 10**9)
    precheck_public = bool(profile.get("precheck_row_public_key_verified"))
    precheck_relation_count = int_value(profile.get("precheck_relation_count"))
    precheck_rank = int_value(profile.get("precheck_rank"))
    precheck_hits = int_value(profile.get("precheck_selected_hit_events"))
    verifier_prefix: tuple[Any, ...] = ()
    support_prefix: tuple[Any, ...] = ()
    if verifier_aware:
        verifier_prefix = (
            not precheck_public,
            -precheck_rank,
            -precheck_relation_count,
            -precheck_hits,
        )
    if prefer_support_columns or avoid_support_columns:
        support = {int_value(item) for item in profile.get("support") or []}
        prefer = prefer_support_columns or set()
        avoid = avoid_support_columns or set()
        support_avoid_hits = len(support & avoid)
        null_avoid_hits = len(null_support & avoid)
        support_prefer_hits = len(support & prefer)
        null_prefer_hits = len(null_support & prefer)
        support_only_preferred = bool(support) and bool(prefer) and support <= prefer
        null_only_preferred = bool(null_support) and bool(prefer) and null_support <= prefer
        support_prefix = (
            support_avoid_hits,
            null_avoid_hits,
            not support_only_preferred,
            not null_only_preferred,
            -support_prefer_hits,
            -null_prefer_hits,
        )
    return (
        *verifier_prefix,
        *support_prefix,
        not has_nonzero,
        -new_support,
        not touches_free,
        -abs_projection,
        -free_one_sided,
        -signed_charge,
        support_size,
        leaf,
    )


def candidate_extensions(
    context: dict[str, Any],
    selected: dict[str, set[int]],
    selected_profiles: dict[str, list[dict[str, Any]]],
    null_vector: list[int],
    order: int,
    free_column: int,
    per_row: int,
    verifier: Any | None = None,
    verifier_aware: bool = False,
    prefer_support_columns: set[int] | None = None,
    avoid_support_columns: set[int] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    selected_support = null_support_union(selected_profiles)
    out: dict[str, list[dict[str, Any]]] = {}
    for row_key, selected_leaves in sorted(selected.items()):
        row_context = source_scorer.row_context(context, row_key)
        profiles = []
        for leaf in null_scout.candidate_leaf_indices(context, row_key):
            leaf_index = int_value(leaf)
            if leaf_index in selected_leaves:
                continue
            profile = null_scout.leaf_null_profile(
                row_context,
                leaf_index,
                null_vector,
                order,
                free_column,
            )
            if not profile.get("null_support"):
                continue
            profile["row_key"] = row_key
            profile["new_null_support"] = sorted(
                {int_value(item) for item in profile.get("null_support") or []} - selected_support
            )
            annotate_column_preferences(
                profile,
                prefer_support_columns or set(),
                avoid_support_columns or set(),
            )
            if verifier_aware and verifier is not None:
                profile.update(
                    precheck_extension_leaf(
                        verifier,
                        context,
                        row_key,
                        selected_leaves | {leaf_index},
                    )
                )
            profiles.append(profile)
        profiles.sort(
            key=lambda profile: extension_score(
                profile,
                selected_support,
                verifier_aware=verifier_aware,
                prefer_support_columns=prefer_support_columns,
                avoid_support_columns=avoid_support_columns,
            )
        )
        out[row_key] = profiles[: max(0, per_row)]
    return out


def annotate_column_preferences(
    profile: dict[str, Any],
    prefer_support_columns: set[int],
    avoid_support_columns: set[int],
) -> None:
    support = {int_value(item) for item in profile.get("support") or []}
    null_support = {int_value(item) for item in profile.get("null_support") or []}
    if prefer_support_columns:
        profile["preferred_support_column_count"] = len(support & prefer_support_columns)
        profile["preferred_null_support_column_count"] = len(null_support & prefer_support_columns)
        profile["support_all_preferred_columns"] = bool(support) and support <= prefer_support_columns
        profile["null_support_all_preferred_columns"] = (
            bool(null_support) and null_support <= prefer_support_columns
        )
    if avoid_support_columns:
        profile["avoided_support_column_count"] = len(support & avoid_support_columns)
        profile["avoided_null_support_column_count"] = len(null_support & avoid_support_columns)
        profile["support_touches_avoided_columns"] = bool(support & avoid_support_columns)
        profile["null_support_touches_avoided_columns"] = bool(null_support & avoid_support_columns)


def precheck_extension_leaf(
    verifier: Any,
    context: dict[str, Any],
    row_key: str,
    selected_leaves: set[int],
) -> dict[str, Any]:
    """Run the row-local selected-leaf verifier precheck for ranking only."""
    try:
        built = context["built_by_row"][row_key]
        components = context["components_by_row"][row_key]
        local_args = context["local_args_by_row"][row_key]
        scan = null_scout.direct_witness_probe.scan_selected(
            verifier,
            built,
            components,
            {int(leaf) for leaf in selected_leaves},
            local_args,
        )
    except Exception as error:
        return {"precheck_error": str(error)}
    return {
        "precheck_candidate_verifications": int_value(scan.get("candidate_verifications")),
        "precheck_ops_over_rho": scan.get("preassociation_filter_ops_over_rho"),
        "precheck_preassociation_filter_ops": int_value(scan.get("preassociation_filter_ops")),
        "precheck_rank": int_value(scan.get("rank")),
        "precheck_relation_count": int_value(scan.get("relation_count")),
        "precheck_row_public_key_verified": bool(scan.get("row_public_key_verified")),
        "precheck_selected_hit_events": int_value(scan.get("selected_hit_events")),
        "precheck_selected_hit_roots": int_value(scan.get("selected_hit_roots")),
    }


def precheck_variant_selection(
    verifier: Any,
    context: dict[str, Any],
    row_leaf_map: dict[str, set[int]],
) -> dict[str, Any]:
    """Run the same scan/union verifier path used for final replay, for ranking only."""
    rows_for_union = []
    built_for_union = {}
    row_results = []
    direct_ops = 0
    generic_rho = 0
    try:
        for row_key, leaves in sorted(row_leaf_map.items()):
            built = context["built_by_row"][row_key]
            components = context["components_by_row"][row_key]
            local_args = context["local_args_by_row"][row_key]
            scan = null_scout.direct_witness_probe.scan_selected(
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
            row_results.append(
                {
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
        union = null_scout.direct_witness_probe.union_derive(
            verifier,
            rows_for_union,
            built_for_union,
            "_scan",
        )
    except Exception as error:
        return {"pair_precheck_error": str(error)}
    return {
        "pair_precheck_direct_below_rho": bool(generic_rho and direct_ops < generic_rho),
        "pair_precheck_direct_ops": direct_ops,
        "pair_precheck_ops_over_rho": ratio(direct_ops, generic_rho),
        "pair_precheck_row_public_key_verified_count": sum(
            1 for row in row_results if row.get("row_public_key_verified")
        ),
        "pair_precheck_row_results": row_results,
        "pair_precheck_selected_hit_events": sum(
            int_value(row.get("selected_hit_events")) for row in row_results
        ),
        "pair_precheck_selected_hit_roots": sum(
            int_value(row.get("selected_hit_roots")) for row in row_results
        ),
        "pair_precheck_union_public_key_verified": bool(union.get("union_public_key_verified")),
        "pair_precheck_union_rank": int_value(union.get("union_rank")),
        "pair_precheck_union_relation_count": int_value(union.get("union_relation_count")),
    }


def compact_extension(profile: dict[str, Any]) -> dict[str, Any]:
    keep = (
        "row_key",
        "leaf_index",
        "projection_signed",
        "abs_projection_signed",
        "free_term_count",
        "free_minus_opposite_term_count",
        "null_support",
        "new_null_support",
        "support",
        "signed_charge",
        "precheck_candidate_verifications",
        "precheck_ops_over_rho",
        "precheck_rank",
        "precheck_relation_count",
        "precheck_row_public_key_verified",
        "precheck_selected_hit_events",
        "precheck_selected_hit_roots",
        "precheck_error",
        "preferred_support_column_count",
        "preferred_null_support_column_count",
        "support_all_preferred_columns",
        "null_support_all_preferred_columns",
        "avoided_support_column_count",
        "avoided_null_support_column_count",
        "support_touches_avoided_columns",
        "null_support_touches_avoided_columns",
    )
    return {key: profile.get(key) for key in keep}


def compact_pair_precheck(precheck: dict[str, Any]) -> dict[str, Any]:
    keep = (
        "pair_precheck_direct_below_rho",
        "pair_precheck_direct_ops",
        "pair_precheck_ops_over_rho",
        "pair_precheck_row_public_key_verified_count",
        "pair_precheck_row_results",
        "pair_precheck_selected_hit_events",
        "pair_precheck_selected_hit_roots",
        "pair_precheck_union_public_key_verified",
        "pair_precheck_union_rank",
        "pair_precheck_union_relation_count",
        "pair_precheck_error",
    )
    return {key: precheck.get(key) for key in keep if key in precheck}


def pair_support_pressure(
    first: dict[str, Any],
    second: dict[str, Any],
    avoid_columns: set[int],
    prefer_columns: set[int],
) -> dict[str, Any]:
    first_support = {int_value(item) for item in first.get("support") or []}
    second_support = {int_value(item) for item in second.get("support") or []}
    support = first_support | second_support
    first_null_support = {int_value(item) for item in first.get("null_support") or []}
    second_null_support = {int_value(item) for item in second.get("null_support") or []}
    null_support = first_null_support | second_null_support
    return {
        "pair_avoided_null_support_column_count": len(null_support & avoid_columns),
        "pair_avoided_null_support_columns": sorted(null_support & avoid_columns),
        "pair_avoided_support_column_count": len(support & avoid_columns),
        "pair_avoided_support_columns": sorted(support & avoid_columns),
        "pair_null_support": sorted(null_support),
        "pair_preferred_null_support_column_count": len(null_support & prefer_columns),
        "pair_preferred_support_column_count": len(support & prefer_columns),
        "pair_support": sorted(support),
    }


def form_supports(result: dict[str, Any]) -> list[set[int]]:
    supports: list[set[int]] = []
    for form in result.get("forms") or []:
        if not isinstance(form, dict):
            continue
        raw_support = form.get("coeff_support")
        if raw_support is None:
            raw_support = form.get("factor_support")
        if raw_support is None:
            raw_support = form.get("terms")
        support = {int_value(item) for item in raw_support or []}
        if support:
            supports.append(support)
    return supports


def export_form_pressure(
    result: dict[str, Any],
    prefer_columns: set[int],
    avoid_columns: set[int],
) -> dict[str, Any]:
    supports = form_supports(result)
    avoid_counts = [len(support & avoid_columns) for support in supports]
    prefer_counts = [len(support & prefer_columns) for support in supports]
    return {
        "export_form_avoid_column_count": len(
            sorted({column for support in supports for column in (support & avoid_columns)})
        ),
        "export_form_avoid_columns": sorted(
            {column for support in supports for column in (support & avoid_columns)}
        ),
        "export_form_avoid_form_count": sum(1 for count in avoid_counts if count),
        "export_form_clean_form_count": sum(1 for count in avoid_counts if not count),
        "export_form_count": len(supports),
        "export_form_max_avoid_columns_per_form": max(avoid_counts, default=0),
        "export_form_preferred_only_form_count": sum(
            1 for support in supports if prefer_columns and support <= prefer_columns
        ),
        "export_form_preferred_total_hits": sum(prefer_counts),
        "export_form_total_avoid_hits": sum(avoid_counts),
    }


def export_form_score(result: dict[str, Any]) -> tuple[Any, ...]:
    pressure = (
        result.get("export_form_pressure")
        if isinstance(result.get("export_form_pressure"), dict)
        else {}
    )
    nonzero_projection_count = int_value(
        (result.get("projection_status_counts") or {}).get("NONZERO_NULLSPACE_PROJECTION")
    )
    return (
        not bool(result.get("union_public_key_verified")),
        not bool(nonzero_projection_count),
        int_value(pressure.get("export_form_avoid_form_count")),
        int_value(pressure.get("export_form_total_avoid_hits")),
        int_value(pressure.get("export_form_avoid_column_count")),
        int_value(pressure.get("export_form_max_avoid_columns_per_form")),
        -int_value(pressure.get("export_form_preferred_only_form_count")),
        -int_value(pressure.get("export_form_clean_form_count")),
        -int_value(pressure.get("export_form_preferred_total_hits")),
        -nonzero_projection_count,
        float(result.get("direct_ops_over_rho") or 10**9),
        str(result.get("label")),
    )


def passes_export_form_gate(
    result: dict[str, Any],
    max_avoid_column_count: int,
    require_nonzero: bool,
    require_verified: bool,
) -> bool:
    pressure = (
        result.get("export_form_pressure")
        if isinstance(result.get("export_form_pressure"), dict)
        else {}
    )
    if require_verified and not result.get("union_public_key_verified"):
        return False
    nonzero_projection_count = int_value(
        (result.get("projection_status_counts") or {}).get("NONZERO_NULLSPACE_PROJECTION")
    )
    if require_nonzero and not nonzero_projection_count:
        return False
    if max_avoid_column_count >= 0 and int_value(
        pressure.get("export_form_max_avoid_columns_per_form")
    ) > max_avoid_column_count:
        return False
    return True


def map_key(row_leaf_map: dict[str, set[int]]) -> str:
    return json.dumps(
        {row_key: sorted(int(leaf) for leaf in leaves) for row_key, leaves in sorted(row_leaf_map.items())},
        sort_keys=True,
        separators=(",", ":"),
    )


def merge_one(selected: dict[str, set[int]], row_key: str, leaf_index: int) -> dict[str, set[int]]:
    merged = {key: set(leaves) for key, leaves in selected.items()}
    merged.setdefault(row_key, set()).add(int(leaf_index))
    return merged


def merge_many(selected: dict[str, set[int]], extensions: list[dict[str, Any]]) -> dict[str, set[int]]:
    merged = {key: set(leaves) for key, leaves in selected.items()}
    for profile in extensions:
        row_key = str(profile.get("row_key"))
        merged.setdefault(row_key, set()).add(int_value(profile.get("leaf_index")))
    return merged


def two_leaf_score(
    first: dict[str, Any],
    second: dict[str, Any],
    selected_null_support: set[int],
    prefer_support_columns: set[int] | None = None,
    avoid_support_columns: set[int] | None = None,
    target_residue_columns: set[int] | None = None,
) -> tuple[Any, ...]:
    first_support = {int_value(item) for item in first.get("support") or []}
    second_support = {int_value(item) for item in second.get("support") or []}
    support = first_support | second_support
    first_null_support = {int_value(item) for item in first.get("null_support") or []}
    second_null_support = {int_value(item) for item in second.get("null_support") or []}
    null_support = first_null_support | second_null_support
    prefer = prefer_support_columns or set()
    target = target_residue_columns or set()
    avoid = (avoid_support_columns or set()) - target
    target_support_hits = len(support & target)
    target_null_hits = len(null_support & target)
    prefer_support_hits = len(support & prefer)
    prefer_null_hits = len(null_support & prefer)
    avoid_support_hits = len(support & avoid)
    avoid_null_hits = len(null_support & avoid)
    new_support = len(null_support - selected_null_support)
    precheck_verified_count = sum(
        1 for profile in (first, second) if profile.get("precheck_row_public_key_verified")
    )
    precheck_rank = (
        int_value(first.get("precheck_rank"))
        + int_value(second.get("precheck_rank"))
    )
    precheck_relations = (
        int_value(first.get("precheck_relation_count"))
        + int_value(second.get("precheck_relation_count"))
    )
    abs_projection = (
        int_value(first.get("abs_projection_signed"))
        + int_value(second.get("abs_projection_signed"))
    )
    free_one_sided = (
        abs(int_value(first.get("free_minus_opposite_term_count")))
        + abs(int_value(second.get("free_minus_opposite_term_count")))
    )
    signed_charge = abs(
        int_value(first.get("signed_charge")) + int_value(second.get("signed_charge"))
    )
    leaf_key = (
        str(first.get("row_key")),
        int_value(first.get("leaf_index")),
        str(second.get("row_key")),
        int_value(second.get("leaf_index")),
    )
    return (
        not target_null_hits,
        -target_null_hits,
        not target_support_hits,
        -target_support_hits,
        avoid_support_hits,
        avoid_null_hits,
        -prefer_support_hits,
        -prefer_null_hits,
        -new_support,
        -precheck_verified_count,
        -precheck_rank,
        -precheck_relations,
        -abs_projection,
        -free_one_sided,
        -signed_charge,
        leaf_key,
    )


def pair_checked_two_leaf_score(item: dict[str, Any]) -> tuple[Any, ...]:
    precheck = item.get("pair_precheck") if isinstance(item.get("pair_precheck"), dict) else {}
    pressure = (
        item.get("pair_support_pressure")
        if isinstance(item.get("pair_support_pressure"), dict)
        else {}
    )
    ops_over_rho = precheck.get("pair_precheck_ops_over_rho")
    return (
        not bool(precheck.get("pair_precheck_union_public_key_verified")),
        -int_value(precheck.get("pair_precheck_union_rank")),
        -int_value(precheck.get("pair_precheck_union_relation_count")),
        not bool(precheck.get("pair_precheck_direct_below_rho")),
        float(ops_over_rho if ops_over_rho is not None else 10**9),
        int_value(pressure.get("pair_avoided_null_support_column_count")),
        int_value(pressure.get("pair_avoided_support_column_count")),
        -int_value(pressure.get("pair_preferred_support_column_count")),
        -int_value(pressure.get("pair_preferred_null_support_column_count")),
        -int_value(precheck.get("pair_precheck_row_public_key_verified_count")),
        -int_value(precheck.get("pair_precheck_selected_hit_events")),
        item.get("base_score") or (),
    )


def main() -> None:
    args = parse_args()
    scorer = leaf_replay.load_json(args.scorer)
    selected_rows = leaf_replay.select_rows(scorer, args)
    if args.require_source_public_key_verified:
        selected_rows = [row for row in selected_rows if row.get("public_key_verified")]
    if args.prefer_source_public_key_verified:
        selected_rows = sorted(
            selected_rows,
            key=lambda row: (
                not bool(row.get("public_key_verified")),
                -int_value(row.get("signal_score")),
                -int_value(row.get("rank")),
                float(row.get("ops_over_rho") if row.get("ops_over_rho") is not None else 10**9),
                str(row.get("source_label")),
                int_value(row.get("transfer_index")),
                str(row.get("selector")),
            ),
        )
    null_vector = source_scorer.parse_null_vector(args.null_vector)
    order = int_value(args.order, 11779)
    free_column = int_value(args.free_column, 6)
    prefer_extension_support_columns = parse_int_set(args.prefer_extension_support_columns)
    avoid_extension_support_columns = parse_int_set(args.avoid_extension_support_columns)
    pair_avoid_extension_support_columns = parse_int_set(args.pair_avoid_extension_support_columns)
    pair_prefer_extension_support_columns = parse_int_set(args.pair_prefer_extension_support_columns)
    target_residue_columns = parse_int_set(args.target_residue_columns)
    export_form_avoid_columns = parse_int_set(args.export_form_avoid_columns)
    export_form_prefer_columns = parse_int_set(args.export_form_prefer_columns)
    frontier_paths = null_scout.resolve_frontier_paths(args.frontier_certificates, args.frontier_list_source)
    null_basis, factor_count = null_scout.frontier_nullspace(frontier_paths, order)
    source_cache: dict[str, dict[str, Any]] = {}
    runtime_cache: dict[str, tuple[Any, list[dict[str, Any]], dict[str, Any], dict[str, dict[str, dict[str, Any]]], argparse.Namespace]] = {}
    context_caches: dict[str, dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]]] = {}
    results = []
    pairs = []
    errors = []
    seen_variants: set[str] = set()
    variant_counts: Counter[str] = Counter()
    variant_result_stats: dict[str, Counter[str]] = defaultdict(Counter)
    selected_source_count = 0

    for source_row_index, row in enumerate(selected_rows):
        if len(results) >= int_value(args.max_evaluations):
            break
        source_path = str(row.get("source_path"))
        try:
            source = source_cache.get(source_path)
            if source is None:
                source = leaf_replay.load_json(Path(source_path))
                source_cache[source_path] = source
            runtime = runtime_cache.get(source_path)
            if runtime is None:
                params = repair_probe.source_parameters(source)
                probe_args = repair_probe.probe_args_from_source(source)
                verifier, records, config_source, specs_by_target = repair_probe.build_specs(params)
                runtime = (verifier, records, config_source, specs_by_target, probe_args)
                runtime_cache[source_path] = runtime
            verifier, records, config_source, specs_by_target, probe_args = runtime
            context_cache = context_caches.setdefault(source_path, {})
            pair = {
                "row_keys": row.get("row_keys") or sorted(leaf_replay.row_leaf_map(row.get("row_leaf_keys") or [])),
                "row_selector": row.get("row_selector"),
                "source_policy": row.get("source_policy"),
                "target": row.get("target"),
                "top_k": int_value(row.get("top_k")),
                "transfer_index": int_value(row.get("transfer_index")),
            }
            context = source_scorer.build_context(
                verifier,
                records,
                config_source,
                specs_by_target,
                probe_args,
                pair,
                context_cache,
            )
            selected = leaf_replay.row_leaf_map(row.get("row_leaf_keys") or [])
            exact_profiles = leaf_replay.profiles_for_selection(
                context,
                selected,
                null_vector,
                order,
                free_column,
            )
            extensions_by_row = candidate_extensions(
                context,
                selected,
                exact_profiles,
                null_vector,
                order,
                free_column,
                int_value(args.per_row_extensions, 4),
                verifier=verifier,
                verifier_aware=bool(args.verifier_aware_extensions),
                prefer_support_columns=prefer_extension_support_columns,
                avoid_support_columns=avoid_extension_support_columns,
            )
            selected_source_count += 1
            pairs.append(pair)

            selected_null_support = null_support_union(exact_profiles)
            header_variants: list[tuple[str, dict[str, set[int]], dict[str, Any]]] = []
            one_leaf_variants: list[tuple[str, dict[str, set[int]], dict[str, Any]]] = []
            two_leaf_variants: list[tuple[str, dict[str, set[int]], dict[str, Any]]] = []
            if args.include_exact:
                header_variants.append(("exact", selected, {"kind": "exact"}))
            for row_key, profiles in sorted(extensions_by_row.items()):
                for profile in profiles:
                    one_leaf_variants.append(
                        (
                            "extend_one",
                            merge_one(selected, row_key, int_value(profile.get("leaf_index"))),
                            {
                                "extension": compact_extension(profile),
                                "kind": "extend_one",
                                "source_row_index": source_row_index,
                            },
                        )
                    )
            if args.include_two_leaf_extensions:
                flat_extensions = [
                    profile
                    for profiles in extensions_by_row.values()
                    for profile in profiles
                ]
                candidate_pairs: list[dict[str, Any]] = []
                for first, second in combinations(flat_extensions, 2):
                    if (
                        str(first.get("row_key")) == str(second.get("row_key"))
                        and int_value(first.get("leaf_index")) == int_value(second.get("leaf_index"))
                    ):
                        continue
                    base_score = two_leaf_score(
                        first,
                        second,
                        selected_null_support,
                        prefer_support_columns=prefer_extension_support_columns,
                        avoid_support_columns=avoid_extension_support_columns,
                        target_residue_columns=target_residue_columns,
                    )
                    candidate_pairs.append(
                        {
                            "base_score": base_score,
                            "extensions": (first, second),
                            "pair_support_pressure": pair_support_pressure(
                                first,
                                second,
                                pair_avoid_extension_support_columns,
                                pair_prefer_extension_support_columns,
                            ),
                            "variant_map": merge_many(selected, [first, second]),
                        }
                    )
                candidate_pairs.sort(key=lambda item: item["base_score"])
                if args.pair_verifier_aware_two_leaf_extensions:
                    precheck_cap = max(
                        0,
                        int_value(
                            args.max_two_leaf_pair_prechecks_per_source_row,
                            args.max_two_leaf_pairs_per_source_row,
                        ),
                    )
                    for item in candidate_pairs[:precheck_cap]:
                        item["pair_precheck"] = precheck_variant_selection(
                            verifier,
                            context,
                            item["variant_map"],
                        )
                    candidate_pairs.sort(
                        key=lambda item: (
                            0 if "pair_precheck" in item else 1,
                            pair_checked_two_leaf_score(item),
                        )
                    )
                for item in candidate_pairs[
                    : max(0, int_value(args.max_two_leaf_pairs_per_source_row))
                ]:
                    first, second = item["extensions"]
                    pair_precheck = item.get("pair_precheck") or {}
                    two_leaf_variants.append(
                        (
                            "extend_two",
                            item["variant_map"],
                            {
                                "extensions": [compact_extension(first), compact_extension(second)],
                                "kind": "extend_two",
                                "pair_precheck": compact_pair_precheck(pair_precheck),
                                "pair_support_pressure": item.get("pair_support_pressure") or {},
                                "source_row_index": source_row_index,
                                "target_residue_columns": sorted(target_residue_columns),
                            },
                        )
                    )
            max_variants = max(0, int_value(args.max_variants_per_source_row, 12))
            if args.include_two_leaf_extensions and two_leaf_variants:
                two_cap = min(len(two_leaf_variants), max_variants)
                one_cap = max(0, max_variants - len(header_variants) - two_cap)
                variants = header_variants + one_leaf_variants[:one_cap] + two_leaf_variants[:two_cap]
            else:
                variants = (header_variants + one_leaf_variants)[:max_variants]
            for variant_index, (kind, variant_map, variant_meta) in enumerate(variants):
                if len(results) >= int_value(args.max_evaluations):
                    break
                key = map_key(variant_map)
                if key in seen_variants:
                    continue
                seen_variants.add(key)
                profiles = leaf_replay.profiles_for_selection(
                    context,
                    variant_map,
                    null_vector,
                    order,
                    free_column,
                )
                label = (
                    f"anti_cancel:{source_row_index}:{variant_index}:"
                    f"{row.get('source_label')}:{row.get('selector')}:{kind}"
                )
                result = null_scout.evaluate_selection(
                    verifier,
                    context,
                    pair,
                    label,
                    variant_map,
                    profiles,
                    null_basis,
                    factor_count,
                    order,
                )
                if not result:
                    continue
                result["source_row_signal"] = leaf_replay.compact_source_row(row)
                result["variant"] = variant_meta
                if args.export_form_aware_ranking:
                    result["export_form_pressure"] = export_form_pressure(
                        result,
                        export_form_prefer_columns,
                        export_form_avoid_columns,
                    )
                results.append(result)
                variant_counts[kind] += 1
                nonzero_projection_count = int_value(
                    (result.get("projection_status_counts") or {}).get("NONZERO_NULLSPACE_PROJECTION")
                )
                stats = variant_result_stats[kind]
                stats["tested_selection_count"] += 1
                stats["nonzero_projection_selection_count"] += int(nonzero_projection_count > 0)
                stats["nonzero_projection_event_count"] += nonzero_projection_count
                stats["verified_selection_count"] += int(bool(result.get("union_public_key_verified")))
                stats["verified_nonzero_projection_selection_count"] += int(
                    bool(result.get("union_public_key_verified")) and nonzero_projection_count > 0
                )
                stats["direct_below_rho_verified_count"] += int(
                    bool(result.get("union_public_key_verified"))
                    and float(result.get("direct_ops_over_rho") or 10**9) <= 1.0
                )
        except Exception as error:
            errors.append({"error": str(error), "source_row": leaf_replay.compact_source_row(row)})

    raw_result_count = len(results)
    if args.export_form_aware_ranking:
        if not export_form_avoid_columns and not export_form_prefer_columns:
            raise SystemExit(
                "--export-form-aware-ranking requires --export-form-avoid-columns "
                "or --export-form-prefer-columns"
            )
        results = [
            result
            for result in results
            if passes_export_form_gate(
                result,
                int_value(args.max_export_form_avoid_columns_per_form, -1),
                bool(args.require_export_form_nonzero_projection),
                bool(args.require_export_form_verified),
            )
        ]
        results.sort(key=export_form_score)
        cap = int_value(args.export_form_result_cap)
        if cap > 0:
            results = results[:cap]
    else:
        results.sort(
            key=lambda result: (
                -int_value((result.get("projection_status_counts") or {}).get("NONZERO_NULLSPACE_PROJECTION")),
                not bool(result.get("union_public_key_verified")),
                float(result.get("direct_ops_over_rho") or 10**9),
                -int_value(result.get("leaf_free_nonzero_count")),
                str(result.get("label")),
            )
        )
    summary = null_scout.summarize(results, pairs)
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
    summary["error_count"] = len(errors)
    summary["raw_result_count_before_export_form_filter"] = raw_result_count
    summary["selected_source_row_count"] = selected_source_count
    summary["variant_kind_counts"] = dict(sorted(variant_counts.items()))
    summary["variant_kind_summary"] = {
        kind: dict(sorted(stats.items()))
        for kind, stats in sorted(variant_result_stats.items())
    }
    payload = {
        "artifacts": {
            "frontier_certificates": [str(path) for path in frontier_paths],
            "frontier_list_source": str(args.frontier_list_source),
            "scorer": str(args.scorer),
        },
        "certificates": certificates,
        "claim_status": summary["claim_status"],
        "errors": errors[:100],
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: one/two-leaf anti-cancellation extension is a source scheduling experiment, not target descent.",
            "NO SPEEDUP CLAIM: positive extension requires rank, repair-bank, family-holdout, source-cost, sparse-LA, and fresh-target gates.",
        ],
        "parameters": {
            "free_column": free_column,
            "include_exact": bool(args.include_exact),
            "max_evaluations": int_value(args.max_evaluations),
            "max_rows": int_value(args.max_rows),
            "max_two_leaf_pair_prechecks_per_source_row": int_value(
                args.max_two_leaf_pair_prechecks_per_source_row
            ),
            "max_two_leaf_pairs_per_source_row": int_value(args.max_two_leaf_pairs_per_source_row),
            "max_variants_per_source_row": int_value(args.max_variants_per_source_row),
            "min_signal_score": int_value(args.min_signal_score),
            "null_vector": null_vector,
            "order": order,
            "pair_avoid_extension_support_columns": sorted(pair_avoid_extension_support_columns),
            "pair_prefer_extension_support_columns": sorted(pair_prefer_extension_support_columns),
            "pair_verifier_aware_two_leaf_extensions": bool(
                args.pair_verifier_aware_two_leaf_extensions
            ),
            "per_row_extensions": int_value(args.per_row_extensions),
            "prefer_extension_support_columns": sorted(prefer_extension_support_columns),
            "prefer_source_public_key_verified": bool(args.prefer_source_public_key_verified),
            "avoid_extension_support_columns": sorted(avoid_extension_support_columns),
            "include_two_leaf_extensions": bool(args.include_two_leaf_extensions),
            "export_form_avoid_columns": sorted(export_form_avoid_columns),
            "export_form_aware_ranking": bool(args.export_form_aware_ranking),
            "export_form_prefer_columns": sorted(export_form_prefer_columns),
            "export_form_result_cap": int_value(args.export_form_result_cap),
            "max_export_form_avoid_columns_per_form": int_value(
                args.max_export_form_avoid_columns_per_form
            ),
            "require_export_form_nonzero_projection": bool(
                args.require_export_form_nonzero_projection
            ),
            "require_export_form_verified": bool(args.require_export_form_verified),
            "require_source_public_key_verified": bool(args.require_source_public_key_verified),
            "statuses": parse_csv(args.statuses),
            "target_residue_columns": sorted(target_residue_columns),
            "verifier_aware_extensions": bool(args.verifier_aware_extensions),
        },
        "schema": "ecdlp.low_term_total2_ruleprefix2_anti_cancellation_leaf_extension.v1",
        "selected_source_rows": [leaf_replay.compact_source_row(row) for row in selected_rows],
        "results": results[:160],
        "summary": summary,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scorer", required=True, type=Path)
    parser.add_argument("--frontier-certificates", default="")
    parser.add_argument(
        "--frontier-list-source",
        type=Path,
        default=null_scout.DEFAULT_FRONTIER_LIST_SOURCE,
    )
    parser.add_argument("--statuses", default="BELOW_RHO_NULL_FREE_SIGNAL")
    parser.add_argument("--min-signal-score", type=int, default=0)
    parser.add_argument("--max-rows", type=int, default=24)
    parser.add_argument("--max-evaluations", type=int, default=160)
    parser.add_argument("--per-row-extensions", type=int, default=4)
    parser.add_argument("--max-variants-per-source-row", type=int, default=8)
    parser.add_argument("--include-exact", action="store_true")
    parser.add_argument("--include-two-leaf-extensions", action="store_true")
    parser.add_argument("--max-two-leaf-pairs-per-source-row", type=int, default=0)
    parser.add_argument("--pair-verifier-aware-two-leaf-extensions", action="store_true")
    parser.add_argument("--max-two-leaf-pair-prechecks-per-source-row", type=int, default=0)
    parser.add_argument(
        "--pair-avoid-extension-support-columns",
        default="",
        help=(
            "Comma- or semicolon-separated columns to penalize in the combined "
            "support of two extension leaves after pair verifier precheck."
        ),
    )
    parser.add_argument(
        "--pair-prefer-extension-support-columns",
        default="",
        help=(
            "Comma- or semicolon-separated columns to prefer in the combined "
            "support of two extension leaves after pair verifier precheck."
        ),
    )
    parser.add_argument("--prefer-source-public-key-verified", action="store_true")
    parser.add_argument("--require-source-public-key-verified", action="store_true")
    parser.add_argument("--verifier-aware-extensions", action="store_true")
    parser.add_argument(
        "--prefer-extension-support-columns",
        default="",
        help="Comma- or semicolon-separated factor columns to prefer in extension leaf support.",
    )
    parser.add_argument(
        "--avoid-extension-support-columns",
        default="",
        help="Comma- or semicolon-separated factor columns to penalize in extension leaf support.",
    )
    parser.add_argument(
        "--target-residue-columns",
        default="",
        help="Comma- or semicolon-separated low columns to target as residual support.",
    )
    parser.add_argument(
        "--export-form-aware-ranking",
        action="store_true",
        help=(
            "After replay, rank/filter retained results by exported target-eliminated "
            "form supports instead of only extension-leaf supports."
        ),
    )
    parser.add_argument(
        "--export-form-avoid-columns",
        default="",
        help="Comma- or semicolon-separated exported-form support columns to penalize.",
    )
    parser.add_argument(
        "--export-form-prefer-columns",
        default="",
        help="Comma- or semicolon-separated exported-form support columns to prefer.",
    )
    parser.add_argument(
        "--max-export-form-avoid-columns-per-form",
        type=int,
        default=-1,
        help=(
            "If nonnegative, discard replayed results whose exported forms have "
            "more than this many avoided columns in any one form."
        ),
    )
    parser.add_argument(
        "--export-form-result-cap",
        type=int,
        default=0,
        help="If positive, keep only this many exported-form-ranked replay results.",
    )
    parser.add_argument("--require-export-form-nonzero-projection", action="store_true")
    parser.add_argument("--require-export-form-verified", action="store_true")
    parser.add_argument("--order", type=int, default=11779)
    parser.add_argument("--free-column", type=int, default=6)
    parser.add_argument("--null-vector", default="1,1,11778,1,1,11778,1,0,0,0,0,0,0,0,0,0")
    parser.add_argument("--out", required=True, type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    main()
