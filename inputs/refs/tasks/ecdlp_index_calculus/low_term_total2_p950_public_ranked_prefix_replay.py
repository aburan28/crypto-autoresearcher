#!/usr/bin/env python3
"""P950 public ranked-prefix replay for P949 exact surfaces."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_DIR = Path(__file__).resolve().parent
for candidate in (REPO_ROOT, TASK_DIR):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tasks.ecdlp_index_calculus.low_term_total2_p942_hash_context_discriminator import (  # noqa: E402
    int_value,
    load_json,
    now_iso,
    write_json,
    window_start,
)
from tasks.ecdlp_index_calculus.low_term_total2_p947_chronology_rank_descent_audit import (  # noqa: E402
    modular_rank,
)
from tasks.ecdlp_index_calculus.low_term_total2_p948_verifier_equation_attachment_audit import (  # noqa: E402
    parse_challenge_seed,
    selected_p947_rows,
)
from tasks.ecdlp_index_calculus.low_term_total2_p949_exact_surface_relation_envelope_regeneration import (  # noqa: E402
    coefficient_payload,
    compact_form,
    compact_selected,
    find_source_policy_row,
    source_leaf_indices,
    strip_private,
)

import frontier_signed_eval_cover_association_probe as association_probe  # noqa: E402
import frontier_signed_eval_cover_preassociation_filter_probe as preassociation_filter_probe  # noqa: E402
import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_materialization_probe as materialization_probe  # noqa: E402
import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_direct_witness_probe as direct_witness_probe  # noqa: E402
import public_factor_forward_safe_multiblock_zero_extra_relation_rank_probe as zero_extra_probe  # noqa: E402
import relation_probe  # noqa: E402


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p950_public_ranked_prefix_replay.md"
DEFAULT_CONFIG_SOURCE = STATE_DIR / "frontier_signed_eval_cover_row_schedule_filter_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p950_public_ranked_prefix_replay_probe.json"
SCHEMA = "ecdlp.low_term_total2_p950_public_ranked_prefix_replay.v1"

DEFAULT_MODES = (
    "pool_order",
    "low_leaf_index",
    "double_pair_first",
    "no_double_pair_first",
    "high_double_pair_count",
    "low_double_pair_count",
    "low_term_support",
    "low_term_span",
    "low_monic_b",
    "low_monic_c",
    "hybrid_double_monic_b",
    "hybrid_support_monic_b",
    "zero_double_pair_low_monic_b",
    "high_shape_concentration",
    "hash_leaf",
)


def parse_modes(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def selected_sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        window_start(str(row.get("window"))),
        int_value(row.get("transfer_index")),
        str(row.get("row_key")),
        str(row.get("hash")),
    )


def compact_feature(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    keep = [
        "leaf_index",
        "scout_position_count",
        "min_scout_pos",
        "double_pair_scout_count",
        "has_double_pair",
        "repeated_scout_count",
        "has_repeated_terms",
        "sum_repeat_excess",
        "min_term_support_size",
        "min_term_span",
        "term_support_size",
        "max_shape_count",
        "monic_b",
        "monic_c",
    ]
    return {key: row.get(key) for key in keep}


def unique_event_forms(rows: list[dict[str, Any]]) -> list[tuple[list[int], int, list[int]]]:
    forms: list[tuple[list[int], int, list[int]]] = []
    seen: set[tuple[tuple[int, ...], int]] = set()
    for row in rows:
        for event in row.get("_events") or []:
            coeffs, rhs, terms = event["form"]
            coeff_list = [int(coeff) for coeff in coeffs]
            key = (tuple(coeff_list), int(rhs))
            if key in seen:
                continue
            seen.add(key)
            forms.append((coeff_list, int(rhs), [int(term) for term in terms]))
    return forms


def build_context(
    verifier: Any,
    records: list[dict[str, Any]],
    config_source: dict[str, Any],
    args: argparse.Namespace,
    selected: dict[str, Any],
    challenge_seed: str,
) -> tuple[dict[str, Any], dict[str, Any], Any]:
    row = zero_extra_probe.row_fields(
        str(selected.get("target")),
        str(selected.get("row_key")),
        args.filter_mode,
    )
    cfg = materialization_probe.cfg_for_row(config_source, row, args.row_pool)
    local_args = direct_witness_probe.shared_target_args(zero_extra_probe.base_args(args), row)
    local_args.challenge_seed = challenge_seed
    local_args.scout_seed_prefix = challenge_seed
    local_args.filter_seed_prefix = challenge_seed
    local_args.seed = challenge_seed
    built = materialization_probe.build_eval_context_with_seed_control(
        verifier,
        records,
        cfg,
        local_args,
    )
    return row, built, local_args


def challenge_mode_key(verifier: Any, row: dict[str, Any], built: dict[str, Any]) -> str:
    payload = {
        "challenge_seed": row.get("verifier_challenge_seed"),
        "mode": row.get("mode"),
        "public": verifier.point_to_json(built["public"]),
        "target": row.get("target"),
    }
    return json.dumps(payload, sort_keys=True)


def scan_public_prefix(
    verifier: Any,
    selected: dict[str, Any],
    source: dict[str, Any],
    built: dict[str, Any],
    local_args: Any,
    mode: str,
    exact_leaves: set[int],
) -> dict[str, Any]:
    p = int(built["p"])
    scouts_by_pos = {int(scout["scout_pos"]): scout for scout in built["scouts"]}
    components = association_probe.build_components(built["scouts"], built["rows"], p)
    feature_rows = preassociation_filter_probe.leaf_public_features(components, scouts_by_pos, p)
    filter_seed = f"{local_args.filter_seed_prefix}:{built['target']}:{mode}"
    ranking = direct_witness_probe.selected_rankings(feature_rows, mode, filter_seed, exact_leaves)
    prefix_count = int(ranking.get("max_kept_leaf_rank") or 0)
    ranked = ranking.get("ranked") or []
    exact_leaf = next(iter(sorted(exact_leaves))) if exact_leaves else None
    feature_by_leaf = {int(row["leaf_index"]): row for row in feature_rows}
    if prefix_count <= 0:
        return {
            **compact_selected(selected),
            "error": "exact leaf missing from public feature ranking",
            "mode": mode,
            "materialized": False,
            "source_factor_zero_leaf_indices": sorted(exact_leaves),
            "source_selected_factor_coefficients": coefficient_payload(source),
            "source_selected_factor_hash": source.get("selected_factor_hash"),
        }
    prefix_selected = {int(row["leaf_index"]) for row in ranked[:prefix_count]}
    scan = direct_witness_probe.scan_selected(
        verifier,
        built,
        components,
        prefix_selected,
        local_args,
    )
    events = scan.get("relation_events") or []
    linear_forms = [compact_form(index, event) for index, event in enumerate(events)]
    return {
        **compact_selected(selected),
        "base_order": int(built.get("order") or 0),
        "challenge_seed_matches_p947": built.get("challenge_seed") == parse_challenge_seed(selected.get("surface_id")),
        "candidate_verifications": int(scan.get("candidate_verifications") or 0),
        "curve_prime": p,
        "derived_secret": scan.get("derived_secret"),
        "exact_leaf_features": compact_feature(feature_by_leaf.get(int(exact_leaf))) if exact_leaf is not None else None,
        "filter_seed": filter_seed,
        "generic_rho_steps": int(built.get("generic_rho_steps") or 0),
        "linear_form_count": len(linear_forms),
        "linear_forms": linear_forms,
        "materialized": True,
        "mode": mode,
        "prefix_contains_exact_leaf": exact_leaves.issubset(prefix_selected),
        "prefix_leaf_count": len(prefix_selected),
        "prefix_ops": int(scan.get("preassociation_filter_ops") or 0),
        "prefix_ops_over_rho": scan.get("preassociation_filter_ops_over_rho"),
        "prefix_top_k": prefix_count,
        "rank": int(scan.get("rank") or 0),
        "relation_count": int(scan.get("relation_count") or 0),
        "row_public_key_verified": bool(scan.get("row_public_key_verified")),
        "selected_hit_events": int(scan.get("selected_hit_events") or 0),
        "selected_hit_roots": int(scan.get("selected_hit_roots") or 0),
        "source_challenge_seed": source.get("challenge_seed"),
        "source_factor_zero_leaf_indices": sorted(exact_leaves),
        "source_selected_factor_coefficients": coefficient_payload(source),
        "source_selected_factor_hash": source.get("selected_factor_hash"),
        "verifier_challenge_seed": built.get("challenge_seed"),
        "_events": events,
    }


def group_union_report(
    verifier: Any,
    key: str,
    rows: list[dict[str, Any]],
    built: dict[str, Any],
) -> dict[str, Any]:
    forms = unique_event_forms(rows)
    order = int(built.get("order") or 0)
    union = {
        "union_relation_count": len(forms),
        "union_rank": 0,
        "union_derived": False,
        "union_public_key_verified": False,
        "union_derived_secret": None,
    }
    if forms:
        union = zero_extra_probe.union_derive(verifier, rows, built)
    matrix_rank = (
        modular_rank([form[0] for form in forms], order)
        if forms and order
        else {
            "rank": 0,
            "row_count": len(forms),
            "column_count": 0,
            "nonunit_pivot_obstruction_count": 0,
        }
    )
    parsed_key = json.loads(key)
    rho = int(built.get("generic_rho_steps") or 0)
    ops = sum(int(row.get("prefix_ops") or 0) for row in rows)
    return {
        "base_order": order,
        "challenge_seed": parsed_key.get("challenge_seed"),
        "mode": parsed_key.get("mode"),
        "modular_form_rank": matrix_rank,
        "prefix_ops": ops,
        "prefix_ops_beats_rho": bool(rho and ops < rho),
        "prefix_ops_over_rho": round(ops / max(1, rho), 8) if rho else None,
        "rho": rho,
        "row_count": len(rows),
        "row_keys": sorted({str(row.get("row_key")) for row in rows}),
        "target": parsed_key.get("target"),
        "transfer_indices": sorted({int_value(row.get("transfer_index")) for row in rows}),
        "unique_form_count": len(forms),
        **union,
    }


def mode_summary(groups: list[dict[str, Any]], rows: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    rows_by_mode: dict[str, list[dict[str, Any]]] = defaultdict(list)
    groups_by_mode: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        rows_by_mode[str(row.get("mode"))].append(row)
    for group in groups:
        groups_by_mode[str(group.get("mode"))].append(group)
    for mode in sorted(set(rows_by_mode) | set(groups_by_mode)):
        mode_rows = rows_by_mode.get(mode, [])
        mode_groups = groups_by_mode.get(mode, [])
        verified = [group for group in mode_groups if group.get("union_public_key_verified")]
        below_rho_verified = [
            group
            for group in verified
            if group.get("prefix_ops_beats_rho")
        ]
        top_ks = [int(row.get("prefix_top_k") or 0) for row in mode_rows if row.get("prefix_top_k") is not None]
        ratios = [
            float(row.get("prefix_ops_over_rho"))
            for row in mode_rows
            if row.get("prefix_ops_over_rho") is not None
        ]
        group_ratios = [
            float(group.get("prefix_ops_over_rho"))
            for group in verified
            if group.get("prefix_ops_over_rho") is not None
        ]
        transfer806 = [
            group
            for group in mode_groups
            if 806 in {int_value(value) for value in group.get("transfer_indices") or []}
        ]
        out[mode] = {
            "below_rho_verified_group_count": len(below_rho_verified),
            "group_count": len(mode_groups),
            "max_prefix_top_k": max(top_ks, default=0),
            "max_union_rank": max((int_value(group.get("union_rank")) for group in mode_groups), default=0),
            "mean_prefix_ops_over_rho": round(mean(ratios), 8) if ratios else None,
            "mean_prefix_top_k": round(mean(top_ks), 8) if top_ks else None,
            "min_verified_group_ops_over_rho": min(group_ratios) if group_ratios else None,
            "row_count": len(mode_rows),
            "rows_with_forms": sum(1 for row in mode_rows if int_value(row.get("linear_form_count")) > 0),
            "transfer806_public_key_verified": any(group.get("union_public_key_verified") for group in transfer806),
            "transfer806_best_rank": max((int_value(group.get("union_rank")) for group in transfer806), default=0),
            "verified_group_count": len(verified),
        }
    return out


def determine_claim(summary: dict[str, Any]) -> str:
    if int_value(summary.get("source_error_count")):
        return "NEGATIVE_RESULT_P950_SOURCE_RECOVERY_INCOMPLETE"
    if int_value(summary.get("context_error_count")):
        return "NEGATIVE_RESULT_P950_CONTEXT_BUILD_ERRORS"
    if int_value(summary.get("transfer806_verified_mode_count")):
        if int_value(summary.get("below_rho_verified_group_count")):
            return "P950_PUBLIC_PREFIX_CLOSES_806_AND_HAS_BELOW_RHO_VERIFIED_GROUP"
        return "P950_PUBLIC_PREFIX_CLOSES_806_TRANSFER_GAP"
    if int_value(summary.get("verified_group_count")):
        if int_value(summary.get("below_rho_verified_group_count")):
            return "P950_PUBLIC_PREFIX_VERIFIES_GROUPS_WITH_BELOW_RHO_DIAGNOSTIC"
        return "P950_PUBLIC_PREFIX_REPLAYS_VERIFIED_GROUPS_806_OPEN"
    if int_value(summary.get("rows_with_forms")):
        return "P950_PUBLIC_PREFIX_FORMS_WITHOUT_GROUP_DERIVATION"
    return "NEGATIVE_RESULT_P950_PUBLIC_PREFIX_NO_VERIFIER_FORMS"


def summarize(rows: list[dict[str, Any]], groups: list[dict[str, Any]], context_errors: list[dict[str, Any]]) -> dict[str, Any]:
    materialized = [row for row in rows if row.get("materialized")]
    verified_groups = [group for group in groups if group.get("union_public_key_verified")]
    below_rho_verified = [group for group in verified_groups if group.get("prefix_ops_beats_rho")]
    transfer806_groups = [
        group
        for group in groups
        if 806 in {int_value(value) for value in group.get("transfer_indices") or []}
    ]
    mode_report = mode_summary(groups, rows)
    summary = {
        "below_rho_verified_group_count": len(below_rho_verified),
        "challenge_mode_group_count": len(groups),
        "context_error_count": len(context_errors),
        "max_modular_form_rank": max(
            (int_value((group.get("modular_form_rank") or {}).get("rank")) for group in groups),
            default=0,
        ),
        "max_union_rank": max((int_value(group.get("union_rank")) for group in groups), default=0),
        "mode_count": len(mode_report),
        "mode_summary": mode_report,
        "mode_row_count": len(rows),
        "rows_with_forms": sum(1 for row in materialized if int_value(row.get("linear_form_count")) > 0),
        "source_error_count": sum(1 for row in context_errors if row.get("error_class") == "source"),
        "surface_count": len({str(row.get("surface_id")) for row in rows} | {str(row.get("surface_id")) for row in context_errors}),
        "transfer806_best_ops_over_rho": min(
            (
                float(group.get("prefix_ops_over_rho"))
                for group in transfer806_groups
                if group.get("prefix_ops_over_rho") is not None
            ),
            default=None,
        ),
        "transfer806_best_rank": max((int_value(group.get("union_rank")) for group in transfer806_groups), default=0),
        "transfer806_group_count": len(transfer806_groups),
        "transfer806_verified_mode_count": sum(1 for group in transfer806_groups if group.get("union_public_key_verified")),
        "unique_verifier_form_count": len(
            {
                (tuple(form.get("coeffs") or []), int_value(form.get("rhs")))
                for row in rows
                for form in row.get("linear_forms") or []
            }
        ),
        "verified_group_count": len(verified_groups),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: surfaces are P947/P949 archive-selected rows.",
            "PUBLIC-RANKED-PREFIX: leaf ordering is public, but top-k is chosen by exact-leaf rank, so this is still an oracle-prefix diagnostic.",
            "POLLARD-RHO BOUNDARY: below-rho prefix counters are component counters, not an end-to-end index-calculus algorithm.",
        ],
    }
    summary["claim_status"] = determine_claim(summary)
    return summary


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    modes = parse_modes(args.modes)
    selected_rows = sorted(selected_p947_rows(), key=selected_sort_key)
    if args.limit is not None:
        selected_rows = selected_rows[: args.limit]
    config_source = load_json(args.config_source)
    verifier = relation_probe.load_verifier_module()
    records = verifier.load_records()

    raw_rows_by_group: dict[str, list[dict[str, Any]]] = defaultdict(list)
    built_by_group: dict[str, dict[str, Any]] = {}
    output_rows: list[dict[str, Any]] = []
    context_errors: list[dict[str, Any]] = []

    for selected in selected_rows:
        source, source_error = find_source_policy_row(selected)
        challenge_seed = parse_challenge_seed(selected.get("surface_id"))
        if source_error or source is None:
            context_errors.append(
                {
                    **compact_selected(selected),
                    "error": source_error,
                    "error_class": "source",
                }
            )
            continue
        exact_leaves = set(source_leaf_indices(source))
        if not challenge_seed or not exact_leaves:
            context_errors.append(
                {
                    **compact_selected(selected),
                    "error": "missing challenge seed or exact leaves",
                    "error_class": "source",
                    "source_factor_zero_leaf_indices": sorted(exact_leaves),
                }
            )
            continue
        try:
            _row_fields, built, local_args = build_context(
                verifier,
                records,
                config_source,
                args,
                selected,
                challenge_seed,
            )
        except Exception as exc:  # noqa: BLE001 - row-level audit should continue.
            context_errors.append(
                {
                    **compact_selected(selected),
                    "error": f"{type(exc).__name__}: {exc}",
                    "error_class": "context",
                    "source_factor_zero_leaf_indices": sorted(exact_leaves),
                }
            )
            continue
        if built.get("error"):
            context_errors.append(
                {
                    **compact_selected(selected),
                    "error": built["error"],
                    "error_class": "context",
                    "source_factor_zero_leaf_indices": sorted(exact_leaves),
                }
            )
            continue
        for mode in modes:
            try:
                row = scan_public_prefix(verifier, selected, source, built, local_args, mode, exact_leaves)
            except Exception as exc:  # noqa: BLE001 - mode-level audit should continue.
                row = {
                    **compact_selected(selected),
                    "error": f"{type(exc).__name__}: {exc}",
                    "materialized": False,
                    "mode": mode,
                    "source_factor_zero_leaf_indices": sorted(exact_leaves),
                    "source_selected_factor_coefficients": coefficient_payload(source),
                    "source_selected_factor_hash": source.get("selected_factor_hash"),
                }
            if row.get("materialized"):
                key = challenge_mode_key(verifier, row, built)
                raw_rows_by_group[key].append(row)
                built_by_group.setdefault(key, built)
            output_rows.append(strip_private(row))

    groups = [
        group_union_report(verifier, key, rows, built_by_group[key])
        for key, rows in sorted(raw_rows_by_group.items())
    ]
    summary = summarize(output_rows, groups, context_errors)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
        },
        "challenge_mode_groups": groups,
        "claim_status": summary["claim_status"],
        "context_errors": context_errors,
        "created_at": now_iso(),
        "method": "p950_public_ranked_prefix_replay",
        "parameters": {
            "config_source": str(args.config_source),
            "filter_mode": args.filter_mode,
            "limit": args.limit,
            "max_relations": args.max_relations,
            "modes": modes,
            "row_pool": args.row_pool,
            "scout_limit": args.scout_limit,
            "scout_mode": args.scout_mode,
            "scout_order": args.scout_order,
            "seed": args.seed,
            "selected_limit": args.selected_limit,
        },
        "rows": output_rows,
        "schema": SCHEMA,
        "summary": summary,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--config-source", type=Path, default=DEFAULT_CONFIG_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--modes", default=",".join(DEFAULT_MODES))
    parser.add_argument("--filter-mode", default="low_term_span")
    parser.add_argument("--row-pool", type=int, default=512)
    parser.add_argument("--row-count", type=int, default=128)
    parser.add_argument("--scout-limit", type=int, default=192)
    parser.add_argument("--scout-mode", default="s3_coeff_spread")
    parser.add_argument("--scout-order", default="eval_cover_hits_high")
    parser.add_argument("--selected-limit", type=int, default=64)
    parser.add_argument("--factor-base-size", type=int, default=16)
    parser.add_argument("--max-relations", type=int, default=96)
    parser.add_argument("--min-distinct-indices", type=int, default=4)
    parser.add_argument("--min-unsigned-distinct-indices", type=int, default=2)
    parser.add_argument("--allow-combined-coefficients", dest="require_unit_coefficients", action="store_false")
    parser.set_defaults(require_unit_coefficients=True)
    parser.add_argument("--row-factor", type=int, default=512)
    parser.add_argument("--product-factor", type=int, default=4096)
    parser.add_argument("--seed", default="ecdlp-frontier-signed-dual-sieve-v1")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary = payload["summary"]
    print(
        f"claim={payload['claim_status']} "
        f"surfaces={summary['surface_count']} "
        f"modes={summary['mode_count']} "
        f"mode_rows={summary['mode_row_count']} "
        f"groups={summary['challenge_mode_group_count']} "
        f"verified_groups={summary['verified_group_count']} "
        f"below_rho_verified={summary['below_rho_verified_group_count']} "
        f"transfer806_verified_modes={summary['transfer806_verified_mode_count']} "
        f"transfer806_best_rank={summary['transfer806_best_rank']} "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
