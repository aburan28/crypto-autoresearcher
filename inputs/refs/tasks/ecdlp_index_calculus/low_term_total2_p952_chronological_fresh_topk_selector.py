#!/usr/bin/env python3
"""P952 chronological fresh-window top-k selector audit."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
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
    split_target,
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
from tasks.ecdlp_index_calculus.low_term_total2_p951_leave_one_transfer_topk_selector import (  # noqa: E402
    scan_fixed_prefix,
)

import public_factor_forward_safe_multiblock_zero_extra_relation_rank_probe as zero_extra_probe  # noqa: E402
import relation_probe  # noqa: E402


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p952_chronological_fresh_topk_selector.md"
DEFAULT_CONFIG_SOURCE = STATE_DIR / "frontier_signed_eval_cover_row_schedule_filter_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p952_chronological_fresh_topk_selector_probe.json"
SCHEMA = "ecdlp.low_term_total2_p952_chronological_fresh_topk_selector.v1"

DEFAULT_WINDOWS = ("1128_1135", "1136_1143", "1144_1151")
FROZEN_POLICIES = (
    ("low_term_span_k5", "low_term_span", 5),
    ("hybrid_support_monic_b_k27", "hybrid_support_monic_b", 27),
)


def parse_windows(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def artifact_for_window(window: str) -> Path:
    return STATE_DIR / f"low_term_total2_ffe_public_factor_quadratic_root_fresh_{window}_expanded_probe.json"


def source_clean(row: dict[str, Any]) -> bool:
    return bool(
        row.get("public_factor_quadratic_root_beats_rho")
        and row.get("quadratic_preserves_selected_root_pairs")
        and not row.get("chosen_false_positive_source")
    )


def compact_source_row(row: dict[str, Any], path: Path, window: str, best_policy: str) -> dict[str, Any]:
    target_label, target_prime = split_target(row.get("target"))
    return {
        "artifact": str(path),
        "b_coeff": (row.get("selected_factor_coefficients") or {}).get("b_coeff"),
        "c_coeff": (row.get("selected_factor_coefficients") or {}).get("c_coeff"),
        "clean": source_clean(row),
        "constant": (row.get("selected_factor_coefficients") or {}).get("constant"),
        "hash": row.get("selected_factor_hash"),
        "policy": best_policy,
        "ratio": row.get("public_factor_quadratic_root_ops_over_rho"),
        "row_key": row.get("row_key"),
        "source_factor_zero_leaf_indices": source_leaf_indices(row),
        "source_has_exact_leaf": bool(source_leaf_indices(row)),
        "source_selected_factor_hash": row.get("selected_factor_hash"),
        "surface_id": row.get("surface_id"),
        "target": row.get("target"),
        "target_label": target_label,
        "target_prime": target_prime,
        "transfer_index": row.get("transfer_index"),
        "window": window,
    }


def load_fresh_rows(windows: list[str], include_unhashed: bool) -> tuple[list[tuple[dict[str, Any], dict[str, Any]]], list[dict[str, Any]]]:
    rows: list[tuple[dict[str, Any], dict[str, Any]]] = []
    summaries: list[dict[str, Any]] = []
    for window in windows:
        path = artifact_for_window(window)
        payload = load_json(path)
        best_policy = str((payload.get("summary") or {}).get("best_policy") or "")
        policy_rows = (payload.get("policy_rows") or {}).get(best_policy) or []
        accepted = []
        for row in policy_rows:
            if not isinstance(row, dict) or not row.get("surface_id") or not row.get("row_key"):
                continue
            if not include_unhashed and not row.get("selected_factor_hash"):
                continue
            selected = compact_source_row(row, path, window, best_policy)
            accepted.append(selected)
            rows.append((selected, row))
        summaries.append(
            {
                "accepted_row_count": len(accepted),
                "artifact": str(path),
                "best_policy": best_policy,
                "clean_accepted_row_count": sum(1 for row in accepted if row.get("clean")),
                "hash_visible_accepted_row_count": sum(1 for row in accepted if row.get("source_selected_factor_hash")),
                "policy_row_count": len(policy_rows),
                "window": window,
            }
        )
    return rows, summaries


def group_key(verifier: Any, row: dict[str, Any], built: dict[str, Any]) -> str:
    payload = {
        "budget_top_k": row.get("budget_top_k"),
        "challenge_seed": row.get("verifier_challenge_seed"),
        "mode": row.get("mode"),
        "policy": row.get("policy"),
        "public": verifier.point_to_json(built["public"]),
        "target": row.get("target"),
    }
    return json.dumps(payload, sort_keys=True)


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
        "budget_top_k": parsed.get("budget_top_k"),
        "challenge_seed": parsed.get("challenge_seed"),
        "exact_leaf_covered_posthoc": all(row.get("prefix_contains_exact_leaf_posthoc") for row in rows),
        "mode": parsed.get("mode"),
        "modular_form_rank": matrix_rank,
        "policy": parsed.get("policy"),
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
        if int_value(summary.get("verified_target_count")) >= 2:
            return "P952_FRESH_FIXED_TOPK_VERIFIES_BOTH_TARGETS_WITH_SOME_BELOW_RHO_GROUPS"
        return "P952_FRESH_FIXED_TOPK_VERIFIES_BELOW_RHO_ONE_TARGET"
    if int_value(summary.get("verified_group_count")):
        return "P952_FRESH_FIXED_TOPK_VERIFIES_ABOVE_RHO"
    return "NEGATIVE_RESULT_P952_FRESH_FIXED_TOPK_NO_DERIVATION"


def summarize(
    rows: list[dict[str, Any]],
    groups: list[dict[str, Any]],
    errors: list[dict[str, Any]],
    window_summaries: list[dict[str, Any]],
) -> dict[str, Any]:
    verified = [group for group in groups if group.get("union_public_key_verified")]
    below = [group for group in verified if group.get("prefix_ops_beats_rho")]
    policy_summary: dict[str, dict[str, Any]] = {}
    for policy in sorted({str(group.get("policy")) for group in groups}):
        policy_groups = [group for group in groups if str(group.get("policy")) == policy]
        policy_verified = [group for group in policy_groups if group.get("union_public_key_verified")]
        policy_below = [group for group in policy_verified if group.get("prefix_ops_beats_rho")]
        policy_summary[policy] = {
            "below_rho_verified_count": len(policy_below),
            "group_count": len(policy_groups),
            "max_union_rank": max((int_value(group.get("union_rank")) for group in policy_groups), default=0),
            "verified_count": len(policy_verified),
        }
    target_summary: dict[str, dict[str, Any]] = {}
    for target in sorted({str(group.get("target")) for group in groups}):
        target_groups = [group for group in groups if str(group.get("target")) == target]
        target_verified = [group for group in target_groups if group.get("union_public_key_verified")]
        target_below = [group for group in target_verified if group.get("prefix_ops_beats_rho")]
        target_summary[target] = {
            "below_rho_verified_count": len(target_below),
            "group_count": len(target_groups),
            "verified_count": len(target_verified),
        }
    summary = {
        "below_rho_verified_group_count": len(below),
        "error_count": len(errors),
        "fresh_group_count": len(groups),
        "fresh_row_count": len({str(row.get("surface_id")) for row in rows}),
        "max_union_rank": max((int_value(group.get("union_rank")) for group in groups), default=0),
        "policy_summary": policy_summary,
        "row_scan_count": len(rows),
        "rows_with_forms": sum(1 for row in rows if int_value(row.get("linear_form_count")) > 0),
        "source_clean_row_count": len({str(row.get("surface_id")) for row in rows if row.get("clean")}),
        "source_hash_visible_row_count": len({str(row.get("surface_id")) for row in rows if row.get("source_selected_factor_hash")}),
        "target_summary": target_summary,
        "unique_verifier_form_count": len(
            {
                (tuple(form.get("coeffs") or []), int_value(form.get("rhs")))
                for row in rows
                for form in row.get("linear_forms") or []
            }
        ),
        "verified_group_count": len(verified),
        "verified_target_count": len({str(group.get("target")) for group in verified}),
        "window_summaries": window_summaries,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "CHRONOLOGICAL-FRESH-WINDOW: test windows are after the P947-P951 transfer set but still drawn from archived local artifacts.",
            "FIXED-TOPK: selectors are frozen public prefix rules; exact leaves are used only for posthoc coverage checks.",
            "COMPONENT-SIGNAL-NOT-END-TO-END: this is not yet full index calculus with independent row selection, linear algebra, and target descent.",
            "POLLARD-RHO BOUNDARY: below-rho claims are charged prefix component comparisons against toy rho.",
        ],
    }
    summary["claim_status"] = determine_claim(summary)
    return summary


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    windows = parse_windows(args.windows)
    fresh_rows, window_summaries = load_fresh_rows(windows, args.include_unhashed)
    verifier = relation_probe.load_verifier_module()
    records = verifier.load_records()
    config_source = load_json(args.config_source)
    context_cache: dict[str, tuple[dict[str, Any], dict[str, Any], Any]] = {}
    row_results: list[dict[str, Any]] = []
    raw_rows_by_group: dict[str, list[dict[str, Any]]] = defaultdict(list)
    built_by_group: dict[str, dict[str, Any]] = {}
    errors: list[dict[str, Any]] = []

    for selected, source in fresh_rows:
        challenge_seed = parse_challenge_seed(selected.get("surface_id"))
        if not challenge_seed:
            errors.append({**selected, "error": "missing challenge seed"})
            continue
        if str(selected["surface_id"]) not in context_cache:
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
                errors.append({**selected, "error": f"{type(exc).__name__}: {exc}"})
                continue
            if built.get("error"):
                errors.append({**selected, "error": built["error"]})
                continue
            context_cache[str(selected["surface_id"])] = (row_fields, built, local_args)
        _row_fields, built, local_args = context_cache[str(selected["surface_id"])]
        for policy, mode, budget in FROZEN_POLICIES:
            try:
                row = scan_fixed_prefix(verifier, selected, source, built, local_args, mode, budget)
            except Exception as exc:  # noqa: BLE001
                errors.append({**selected, "policy": policy, "mode": mode, "error": f"{type(exc).__name__}: {exc}"})
                continue
            row.update(
                {
                    "clean": selected.get("clean"),
                    "policy": policy,
                    "source_has_exact_leaf": selected.get("source_has_exact_leaf"),
                    "source_selected_factor_hash": selected.get("source_selected_factor_hash"),
                    "window": selected.get("window"),
                }
            )
            key = group_key(verifier, row, built)
            raw_rows_by_group[key].append(row)
            built_by_group.setdefault(key, built)
            row_results.append(strip_private(row))

    groups = [
        group_union_report(verifier, key, rows, built_by_group[key])
        for key, rows in sorted(raw_rows_by_group.items())
    ]
    summary = summarize(row_results, groups, errors, window_summaries)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
        },
        "claim_status": summary["claim_status"],
        "created_at": now_iso(),
        "errors": errors,
        "fresh_groups": groups,
        "method": "p952_chronological_fresh_topk_selector",
        "parameters": {
            "config_source": str(args.config_source),
            "include_unhashed": args.include_unhashed,
            "policies": [
                {"policy": policy, "mode": mode, "budget_top_k": budget}
                for policy, mode, budget in FROZEN_POLICIES
            ],
            "row_pool": args.row_pool,
            "scout_limit": args.scout_limit,
            "scout_mode": args.scout_mode,
            "scout_order": args.scout_order,
            "seed": args.seed,
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
    print(
        f"claim={payload['claim_status']} "
        f"fresh_rows={summary['fresh_row_count']} "
        f"groups={summary['fresh_group_count']} "
        f"verified={summary['verified_group_count']} "
        f"below_rho={summary['below_rho_verified_group_count']} "
        f"targets={summary['verified_target_count']} "
        f"errors={summary['error_count']} "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
