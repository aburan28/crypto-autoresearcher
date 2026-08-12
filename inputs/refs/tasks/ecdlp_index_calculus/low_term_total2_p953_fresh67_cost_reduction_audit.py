#!/usr/bin/env python3
"""P953 fresh 67 public-prefix cost-reduction audit."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
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
)
from tasks.ecdlp_index_calculus.low_term_total2_p947_chronology_rank_descent_audit import modular_rank  # noqa: E402
from tasks.ecdlp_index_calculus.low_term_total2_p948_verifier_equation_attachment_audit import parse_challenge_seed  # noqa: E402
from tasks.ecdlp_index_calculus.low_term_total2_p949_exact_surface_relation_envelope_regeneration import (  # noqa: E402
    compact_form,
    source_leaf_indices,
    strip_private,
)
from tasks.ecdlp_index_calculus.low_term_total2_p950_public_ranked_prefix_replay import (  # noqa: E402
    build_context,
    compact_feature,
    unique_event_forms,
)
from tasks.ecdlp_index_calculus.low_term_total2_p952_chronological_fresh_topk_selector import (  # noqa: E402
    DEFAULT_WINDOWS,
    load_fresh_rows,
    parse_windows,
)

import frontier_signed_eval_cover_association_probe as association_probe  # noqa: E402
import frontier_signed_eval_cover_preassociation_filter_probe as preassociation_filter_probe  # noqa: E402
import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_direct_witness_probe as direct_witness_probe  # noqa: E402
import public_factor_forward_safe_multiblock_zero_extra_relation_rank_probe as zero_extra_probe  # noqa: E402
import relation_probe  # noqa: E402


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p953_fresh67_cost_reduction_audit.md"
DEFAULT_CONFIG_SOURCE = STATE_DIR / "frontier_signed_eval_cover_row_schedule_filter_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p953_fresh67_cost_reduction_audit_probe.json"
SCHEMA = "ecdlp.low_term_total2_p953_fresh67_cost_reduction_audit.v1"
DEFAULT_TARGET = "67.a1@9803"


PolicySpec = tuple[str, tuple[tuple[str, int], ...]]


POLICY_SPECS: tuple[PolicySpec, ...] = (
    ("low_term_span_k3", (("low_term_span", 3),)),
    ("low_term_span_k4", (("low_term_span", 4),)),
    ("low_term_span_k5", (("low_term_span", 5),)),
    ("low_term_span_k6", (("low_term_span", 6),)),
    ("low_term_span_k8", (("low_term_span", 8),)),
    ("low_term_support_k5", (("low_term_support", 5),)),
    ("low_term_support_k8", (("low_term_support", 8),)),
    ("low_term_support_k12", (("low_term_support", 12),)),
    ("hybrid_support_monic_b_k4", (("hybrid_support_monic_b", 4),)),
    ("hybrid_support_monic_b_k6", (("hybrid_support_monic_b", 6),)),
    ("hybrid_support_monic_b_k8", (("hybrid_support_monic_b", 8),)),
    ("hybrid_support_monic_b_k10", (("hybrid_support_monic_b", 10),)),
    ("hybrid_support_monic_b_k12", (("hybrid_support_monic_b", 12),)),
    ("hybrid_support_monic_b_k16", (("hybrid_support_monic_b", 16),)),
    ("hybrid_support_monic_b_k20", (("hybrid_support_monic_b", 20),)),
    ("hybrid_support_monic_b_k24", (("hybrid_support_monic_b", 24),)),
    ("hybrid_support_monic_b_k27", (("hybrid_support_monic_b", 27),)),
    ("hybrid_double_monic_b_k8", (("hybrid_double_monic_b", 8),)),
    ("hybrid_double_monic_b_k12", (("hybrid_double_monic_b", 12),)),
    ("hybrid_double_monic_b_k16", (("hybrid_double_monic_b", 16),)),
    ("hybrid_double_monic_b_k20", (("hybrid_double_monic_b", 20),)),
    ("double_pair_first_k8", (("double_pair_first", 8),)),
    ("high_double_pair_count_k8", (("high_double_pair_count", 8),)),
    ("low_span5__hybrid_support_k4", (("low_term_span", 5), ("hybrid_support_monic_b", 4))),
    ("low_span5__hybrid_support_k6", (("low_term_span", 5), ("hybrid_support_monic_b", 6))),
    ("low_span5__hybrid_support_k8", (("low_term_span", 5), ("hybrid_support_monic_b", 8))),
    ("low_span5__hybrid_support_k10", (("low_term_span", 5), ("hybrid_support_monic_b", 10))),
    ("low_span5__hybrid_support_k12", (("low_term_span", 5), ("hybrid_support_monic_b", 12))),
    ("low_span4__hybrid_support_k8", (("low_term_span", 4), ("hybrid_support_monic_b", 8))),
    ("low_span4__hybrid_support_k12", (("low_term_span", 4), ("hybrid_support_monic_b", 12))),
    ("low_span5__hybrid_double_k8", (("low_term_span", 5), ("hybrid_double_monic_b", 8))),
    ("low_span5__hybrid_double_k12", (("low_term_span", 5), ("hybrid_double_monic_b", 12))),
    ("low_span5__low_support_k8", (("low_term_span", 5), ("low_term_support", 8))),
    ("low_span5__double_pair_k8", (("low_term_span", 5), ("double_pair_first", 8))),
)


def policy_specs(raw: str | None) -> list[PolicySpec]:
    specs = list(POLICY_SPECS)
    if not raw:
        return specs
    wanted = {item.strip() for item in raw.split(",") if item.strip()}
    return [spec for spec in specs if spec[0] in wanted]


def compact_source(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "b_coeff": row.get("b_coeff"),
        "c_coeff": row.get("c_coeff"),
        "clean": row.get("clean"),
        "constant": row.get("constant"),
        "hash": row.get("hash"),
        "policy": row.get("policy"),
        "ratio": row.get("ratio"),
        "row_key": row.get("row_key"),
        "source_artifact": row.get("artifact"),
        "source_has_exact_leaf": row.get("source_has_exact_leaf"),
        "source_selected_factor_hash": row.get("source_selected_factor_hash"),
        "surface_id": row.get("surface_id"),
        "target": row.get("target"),
        "target_prime": row.get("target_prime"),
        "transfer_index": row.get("transfer_index"),
        "window": row.get("window"),
    }


def group_key(verifier: Any, row: dict[str, Any], built: dict[str, Any]) -> str:
    payload = {
        "challenge_seed": row.get("verifier_challenge_seed"),
        "policy": row.get("policy"),
        "public": verifier.point_to_json(built["public"]),
        "target": row.get("target"),
    }
    return json.dumps(payload, sort_keys=True)


def component_ranked_rows(
    feature_rows: list[dict[str, Any]],
    mode: str,
    built: dict[str, Any],
    local_args: Any,
) -> tuple[str, list[dict[str, Any]]]:
    filter_seed = f"{local_args.filter_seed_prefix}:{built['target']}:{mode}"
    ranked = sorted(feature_rows, key=lambda row: preassociation_filter_probe.score_key(row, mode, filter_seed))
    return filter_seed, ranked


def scan_policy_prefix(
    verifier: Any,
    selected: dict[str, Any],
    source: dict[str, Any],
    built: dict[str, Any],
    local_args: Any,
    policy: str,
    components_spec: tuple[tuple[str, int], ...],
    feature_cache: dict[str, Any] | None = None,
) -> dict[str, Any]:
    p = int(built["p"])
    if feature_cache is None:
        scouts_by_pos = {int(scout["scout_pos"]): scout for scout in built["scouts"]}
        components = association_probe.build_components(built["scouts"], built["rows"], p)
        feature_rows = preassociation_filter_probe.leaf_public_features(components, scouts_by_pos, p)
    else:
        components = feature_cache["components"]
        feature_rows = feature_cache["feature_rows"]
    feature_by_leaf = {int(row["leaf_index"]): row for row in feature_rows}
    exact_leaves = set(source_leaf_indices(source))
    prefix_selected: set[int] = set()
    component_reports: list[dict[str, Any]] = []

    for mode, budget in components_spec:
        filter_seed, ranked = component_ranked_rows(feature_rows, mode, built, local_args)
        prefix_count = min(max(1, int(budget)), len(ranked))
        leaves = {int(row["leaf_index"]) for row in ranked[:prefix_count]}
        prefix_selected.update(leaves)
        rank_by_leaf = {int(row["leaf_index"]): index for index, row in enumerate(ranked, start=1)}
        component_reports.append(
            {
                "budget_top_k": int(budget),
                "exact_leaf_covered_posthoc": exact_leaves.issubset(leaves),
                "exact_leaf_rank_posthoc": {
                    str(leaf): rank_by_leaf.get(int(leaf))
                    for leaf in sorted(exact_leaves)
                },
                "filter_seed": filter_seed,
                "mode": mode,
                "selected_leaf_count": len(leaves),
                "top_leaf_indices_sample": [int(row["leaf_index"]) for row in ranked[: min(prefix_count, 12)]],
            }
        )

    scan = direct_witness_probe.scan_selected(
        verifier,
        built,
        components,
        prefix_selected,
        local_args,
    )
    events = scan.get("relation_events") or []
    linear_forms = [compact_form(index, event) for index, event in enumerate(events)]
    exact_leaf_features = {
        str(leaf): compact_feature(feature_by_leaf.get(int(leaf)))
        for leaf in sorted(exact_leaves)
        if int(leaf) in feature_by_leaf
    }
    return {
        **compact_source(selected),
        "base_order": int(built.get("order") or 0),
        "candidate_verifications": int(scan.get("candidate_verifications") or 0),
        "challenge_seed_matches_source": built.get("challenge_seed") == parse_challenge_seed(selected.get("surface_id")),
        "component_reports": component_reports,
        "curve_prime": p,
        "derived_secret": scan.get("derived_secret"),
        "exact_leaf_features_posthoc": exact_leaf_features,
        "generic_rho_steps": int(built.get("generic_rho_steps") or 0),
        "linear_form_count": len(linear_forms),
        "linear_forms": linear_forms,
        "materialized": True,
        "mode": "+".join(mode for mode, _budget in components_spec),
        "policy": policy,
        "policy_components": [
            {"mode": mode, "budget_top_k": int(budget)}
            for mode, budget in components_spec
        ],
        "policy_component_budget_sum": sum(int(budget) for _mode, budget in components_spec),
        "prefix_contains_exact_leaf_posthoc": exact_leaves.issubset(prefix_selected),
        "prefix_leaf_count": len(prefix_selected),
        "prefix_ops": int(scan.get("preassociation_filter_ops") or 0),
        "prefix_ops_over_rho": scan.get("preassociation_filter_ops_over_rho"),
        "prefix_top_k": len(prefix_selected),
        "rank": int(scan.get("rank") or 0),
        "relation_count": int(scan.get("relation_count") or 0),
        "row_public_key_verified": bool(scan.get("row_public_key_verified")),
        "selected_hit_events": int(scan.get("selected_hit_events") or 0),
        "selected_hit_roots": int(scan.get("selected_hit_roots") or 0),
        "source_factor_zero_leaf_indices_posthoc": sorted(exact_leaves),
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
    parsed = json.loads(key)
    rho = int(built.get("generic_rho_steps") or 0)
    ops = sum(int(row.get("prefix_ops") or 0) for row in rows)
    return {
        "base_order": order,
        "challenge_seed": parsed.get("challenge_seed"),
        "exact_leaf_covered_posthoc": all(row.get("prefix_contains_exact_leaf_posthoc") for row in rows),
        "max_row_prefix_leaf_count": max((int_value(row.get("prefix_leaf_count")) for row in rows), default=0),
        "modular_form_rank": matrix_rank,
        "policy": parsed.get("policy"),
        "policy_components": rows[0].get("policy_components") if rows else [],
        "prefix_ops": ops,
        "prefix_ops_beats_rho": bool(rho and ops < rho),
        "prefix_ops_over_rho": round(ops / max(1, rho), 8) if rho else None,
        "rho": rho,
        "row_count": len(rows),
        "row_keys": sorted({str(row.get("row_key")) for row in rows}),
        "source_clean_row_count": sum(1 for row in rows if row.get("clean")),
        "target": parsed.get("target"),
        "transfer_indices": sorted({int_value(row.get("transfer_index")) for row in rows}),
        "unique_form_count": len(forms),
        "windows": sorted({str(row.get("window")) for row in rows}),
        **union,
    }


def determine_claim(summary: dict[str, Any]) -> str:
    if int_value(summary.get("below_rho_verified_group_count")):
        return "P953_FRESH67_COST_REDUCTION_BELOW_RHO"
    if int_value(summary.get("verified_group_count")):
        return "P953_FRESH67_VERIFIES_ABOVE_RHO_ONLY"
    if int_value(summary.get("groups_with_forms_count")):
        return "NEGATIVE_RESULT_P953_FRESH67_FORMS_WITHOUT_DERIVATION"
    return "NEGATIVE_RESULT_P953_FRESH67_NO_FORMS"


def summarize(
    rows: list[dict[str, Any]],
    groups: list[dict[str, Any]],
    errors: list[dict[str, Any]],
    window_summaries: list[dict[str, Any]],
    target: str,
) -> dict[str, Any]:
    verified = [group for group in groups if group.get("union_public_key_verified")]
    below = [group for group in verified if group.get("prefix_ops_beats_rho")]
    groups_with_forms = [group for group in groups if int_value(group.get("unique_form_count")) > 0]
    policy_summary: dict[str, dict[str, Any]] = {}
    for policy in sorted({str(group.get("policy")) for group in groups}):
        policy_groups = [group for group in groups if str(group.get("policy")) == policy]
        policy_verified = [group for group in policy_groups if group.get("union_public_key_verified")]
        policy_below = [group for group in policy_verified if group.get("prefix_ops_beats_rho")]
        verified_ratios = [
            float(group.get("prefix_ops_over_rho"))
            for group in policy_verified
            if group.get("prefix_ops_over_rho") is not None
        ]
        policy_summary[policy] = {
            "below_rho_verified_count": len(policy_below),
            "group_count": len(policy_groups),
            "max_union_rank": max((int_value(group.get("union_rank")) for group in policy_groups), default=0),
            "min_verified_ops_over_rho": min(verified_ratios) if verified_ratios else None,
            "policy_components": policy_groups[0].get("policy_components") if policy_groups else [],
            "verified_count": len(policy_verified),
        }
    best_verified = min(
        verified,
        key=lambda group: float(group.get("prefix_ops_over_rho") or 10**18),
        default=None,
    )
    best_any = min(
        groups,
        key=lambda group: float(group.get("prefix_ops_over_rho") or 10**18),
        default=None,
    )
    summary = {
        "below_rho_verified_group_count": len(below),
        "best_any_group": best_any,
        "best_verified_group": best_verified,
        "error_count": len(errors),
        "fresh_group_count": len(groups),
        "fresh_row_count": len({str(row.get("surface_id")) for row in rows}),
        "groups_with_forms_count": len(groups_with_forms),
        "max_union_rank": max((int_value(group.get("union_rank")) for group in groups), default=0),
        "policy_count": len(policy_summary),
        "policy_summary": policy_summary,
        "row_scan_count": len(rows),
        "rows_with_forms": sum(1 for row in rows if int_value(row.get("linear_form_count")) > 0),
        "source_clean_row_count": len({str(row.get("surface_id")) for row in rows if row.get("clean")}),
        "target": target,
        "unique_verifier_form_count": len(
            {
                (tuple(form.get("coeffs") or []), int_value(form.get("rhs")))
                for row in rows
                for form in row.get("linear_forms") or []
            }
        ),
        "verified_group_count": len(verified),
        "window_summaries": window_summaries,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "CHRONOLOGICAL-FRESH-WINDOW: rows are later than P947-P951 but still from archived local fresh-window artifacts.",
            "FIXED-PUBLIC-PREFIX: selectors use public leaf rankings and fixed budgets; exact leaves are posthoc diagnostics only.",
            "COMPONENT-SIGNAL-NOT-END-TO-END: this is not full index calculus with independent row selection, linear algebra, and target descent.",
            "POLLARD-RHO BOUNDARY: below-rho claims are charged prefix component comparisons against toy rho.",
        ],
    }
    summary["claim_status"] = determine_claim(summary)
    return summary


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    windows = parse_windows(args.windows)
    fresh_rows, window_summaries = load_fresh_rows(windows, args.include_unhashed)
    target_rows = [(selected, source) for selected, source in fresh_rows if str(selected.get("target")) == args.target]
    verifier = relation_probe.load_verifier_module()
    records = verifier.load_records()
    config_source = load_json(args.config_source)
    specs = policy_specs(args.policies)
    context_cache: dict[str, tuple[dict[str, Any], dict[str, Any], Any, dict[str, Any]]] = {}
    row_results: list[dict[str, Any]] = []
    raw_rows_by_group: dict[str, list[dict[str, Any]]] = defaultdict(list)
    built_by_group: dict[str, dict[str, Any]] = {}
    errors: list[dict[str, Any]] = []

    for selected, source in target_rows:
        challenge_seed = parse_challenge_seed(selected.get("surface_id"))
        if not challenge_seed:
            errors.append({**compact_source(selected), "error": "missing challenge seed"})
            continue
        surface_id = str(selected["surface_id"])
        if surface_id not in context_cache:
            try:
                row_fields, built, local_args = build_context(
                    verifier,
                    records,
                    config_source,
                    args,
                    selected,
                    challenge_seed,
                )
            except Exception as exc:  # noqa: BLE001
                errors.append({**compact_source(selected), "error": f"{type(exc).__name__}: {exc}"})
                continue
            if built.get("error"):
                errors.append({**compact_source(selected), "error": built["error"]})
                continue
            scouts_by_pos = {int(scout["scout_pos"]): scout for scout in built["scouts"]}
            components = association_probe.build_components(built["scouts"], built["rows"], int(built["p"]))
            feature_rows = preassociation_filter_probe.leaf_public_features(components, scouts_by_pos, int(built["p"]))
            context_cache[surface_id] = (row_fields, built, local_args, {"components": components, "feature_rows": feature_rows})
        _row_fields, built, local_args, feature_cache = context_cache[surface_id]
        for policy, components_spec in specs:
            try:
                row = scan_policy_prefix(
                    verifier,
                    selected,
                    source,
                    built,
                    local_args,
                    policy,
                    components_spec,
                    feature_cache,
                )
            except Exception as exc:  # noqa: BLE001
                errors.append({**compact_source(selected), "policy": policy, "error": f"{type(exc).__name__}: {exc}"})
                continue
            key = group_key(verifier, row, built)
            raw_rows_by_group[key].append(row)
            built_by_group.setdefault(key, built)
            row_results.append(strip_private(row))

    groups = [
        group_union_report(verifier, key, rows, built_by_group[key])
        for key, rows in sorted(raw_rows_by_group.items())
    ]
    summary = summarize(row_results, groups, errors, window_summaries, args.target)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
        },
        "claim_status": summary["claim_status"],
        "created_at": now_iso(),
        "errors": errors,
        "fresh_groups": groups,
        "method": "p953_fresh67_cost_reduction_audit",
        "parameters": {
            "config_source": str(args.config_source),
            "include_unhashed": args.include_unhashed,
            "policies": [
                {
                    "policy": policy,
                    "components": [
                        {"mode": mode, "budget_top_k": budget}
                        for mode, budget in components_spec
                    ],
                }
                for policy, components_spec in specs
            ],
            "row_pool": args.row_pool,
            "scout_limit": args.scout_limit,
            "scout_mode": args.scout_mode,
            "scout_order": args.scout_order,
            "seed": args.seed,
            "target": args.target,
            "windows": windows,
        },
        "row_results": row_results,
        "schema": SCHEMA,
        "summary": summary,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--config-source", type=Path, default=DEFAULT_CONFIG_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--windows", default=",".join(DEFAULT_WINDOWS))
    parser.add_argument("--target", default=DEFAULT_TARGET)
    parser.add_argument("--policies", default=None, help="Comma-separated policy names to run; default runs the P953 suite.")
    parser.add_argument("--include-unhashed", action=argparse.BooleanOptionalAction, default=True)
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
    best_verified = summary.get("best_verified_group") or {}
    print(
        f"claim={payload['claim_status']} "
        f"target={summary['target']} "
        f"fresh_rows={summary['fresh_row_count']} "
        f"policies={summary['policy_count']} "
        f"groups={summary['fresh_group_count']} "
        f"verified={summary['verified_group_count']} "
        f"below_rho={summary['below_rho_verified_group_count']} "
        f"best_verified_ops_over_rho={best_verified.get('prefix_ops_over_rho')} "
        f"best_verified_policy={best_verified.get('policy')} "
        f"errors={summary['error_count']} "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
