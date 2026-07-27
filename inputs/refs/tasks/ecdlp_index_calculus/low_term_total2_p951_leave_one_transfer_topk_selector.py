#!/usr/bin/env python3
"""P951 leave-one-transfer public top-k selector audit."""

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
    compact_form,
    compact_selected,
    find_source_policy_row,
    source_leaf_indices,
    strip_private,
)
from tasks.ecdlp_index_calculus.low_term_total2_p950_public_ranked_prefix_replay import (  # noqa: E402
    DEFAULT_MODES,
    build_context,
    compact_feature,
    parse_modes,
    unique_event_forms,
)

import frontier_signed_eval_cover_association_probe as association_probe  # noqa: E402
import frontier_signed_eval_cover_preassociation_filter_probe as preassociation_filter_probe  # noqa: E402
import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_direct_witness_probe as direct_witness_probe  # noqa: E402
import public_factor_forward_safe_multiblock_zero_extra_relation_rank_probe as zero_extra_probe  # noqa: E402
import relation_probe  # noqa: E402


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p951_leave_one_transfer_topk_selector.md"
DEFAULT_P950_SOURCE = STATE_DIR / "low_term_total2_p950_public_ranked_prefix_replay_probe.json"
DEFAULT_CONFIG_SOURCE = STATE_DIR / "frontier_signed_eval_cover_row_schedule_filter_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p951_leave_one_transfer_topk_selector_probe.json"
SCHEMA = "ecdlp.low_term_total2_p951_leave_one_transfer_topk_selector.v1"

POLICY_NAMES = (
    "rho_first",
    "recall_first",
    "balanced",
    "primary_hybrid_rho_first",
)
PRIMARY_HYBRID_MODES = ("hybrid_double_monic_b", "hybrid_support_monic_b")
DEFAULT_BUDGETS = (1, 2, 3, 4, 5, 8, 12, 16, 24, 27, 32, 48, 64, 96, 128)


def selected_sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        window_start(str(row.get("window"))),
        int_value(row.get("transfer_index")),
        str(row.get("row_key")),
        str(row.get("hash")),
    )


def transfer_from_group(group: dict[str, Any]) -> int | None:
    transfers = group.get("transfer_indices") or []
    if len(transfers) != 1:
        return None
    return int_value(transfers[0], -1)


def build_p950_index(p950: dict[str, Any]) -> dict[str, Any]:
    rows_by_transfer_mode: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    groups_by_transfer_mode: dict[tuple[int, str], dict[str, Any]] = {}
    transfers: set[int] = set()
    modes: set[str] = set()
    for row in p950.get("rows") or []:
        transfer = int_value(row.get("transfer_index"), -1)
        mode = str(row.get("mode"))
        if transfer >= 0 and mode:
            rows_by_transfer_mode[(transfer, mode)].append(row)
            transfers.add(transfer)
            modes.add(mode)
    for group in p950.get("challenge_mode_groups") or []:
        transfer = transfer_from_group(group)
        mode = str(group.get("mode"))
        if transfer is not None and transfer >= 0 and mode:
            groups_by_transfer_mode[(transfer, mode)] = group
            transfers.add(transfer)
            modes.add(mode)
    return {
        "groups_by_transfer_mode": groups_by_transfer_mode,
        "modes": sorted(modes),
        "rows_by_transfer_mode": rows_by_transfer_mode,
        "transfers": sorted(transfers),
    }


def candidate_budgets(
    rows_by_transfer_mode: dict[tuple[int, str], list[dict[str, Any]]],
    modes: list[str],
    max_top_k: int,
) -> list[int]:
    budgets = set(DEFAULT_BUDGETS)
    for (_transfer, mode), rows in rows_by_transfer_mode.items():
        if mode not in modes:
            continue
        for row in rows:
            top_k = int_value(row.get("prefix_top_k"))
            if top_k:
                budgets.add(top_k)
    return sorted(budget for budget in budgets if 0 < budget <= max_top_k)


def candidate_score(
    rows_by_transfer_mode: dict[tuple[int, str], list[dict[str, Any]]],
    groups_by_transfer_mode: dict[tuple[int, str], dict[str, Any]],
    transfers: list[int],
    holdout: int,
    mode: str,
    budget: int,
) -> dict[str, Any]:
    train_transfers = [transfer for transfer in transfers if transfer != holdout]
    covered = 0
    verified = 0
    below = 0
    ranks: list[int] = []
    ratios: list[float] = []
    uncovered_transfers = []
    for transfer in train_transfers:
        rows = rows_by_transfer_mode.get((transfer, mode), [])
        group = groups_by_transfer_mode.get((transfer, mode))
        if not rows or group is None:
            uncovered_transfers.append(transfer)
            continue
        if not all(int_value(row.get("prefix_top_k"), 10**9) <= budget for row in rows):
            uncovered_transfers.append(transfer)
            continue
        covered += 1
        ranks.append(int_value(group.get("union_rank")))
        if group.get("prefix_ops_over_rho") is not None:
            ratios.append(float(group["prefix_ops_over_rho"]))
        if group.get("union_public_key_verified"):
            verified += 1
            if group.get("prefix_ops_beats_rho"):
                below += 1
    mean_ratio = round(mean(ratios), 8) if ratios else None
    return {
        "below_rho_verified_group_count": below,
        "budget_top_k": budget,
        "covered_group_count": covered,
        "holdout_transfer": holdout,
        "max_train_rank": max(ranks, default=0),
        "mean_training_ops_over_rho": mean_ratio,
        "mode": mode,
        "training_group_count": len(train_transfers),
        "uncovered_transfer_count": len(uncovered_transfers),
        "uncovered_transfers_sample": uncovered_transfers[:10],
        "verified_group_count": verified,
    }


def policy_sort_key(policy: str, score: dict[str, Any]) -> tuple[Any, ...]:
    below = int_value(score.get("below_rho_verified_group_count"))
    verified = int_value(score.get("verified_group_count"))
    covered = int_value(score.get("covered_group_count"))
    rank = int_value(score.get("max_train_rank"))
    ratio = score.get("mean_training_ops_over_rho")
    ratio_key = -float(ratio) if ratio is not None else -10**9
    budget = int_value(score.get("budget_top_k"))
    if policy in {"rho_first", "primary_hybrid_rho_first"}:
        return (below, verified, covered, rank, ratio_key, -budget, str(score.get("mode")))
    if policy == "recall_first":
        return (verified, below, covered, rank, -budget, ratio_key, str(score.get("mode")))
    if policy == "balanced":
        return (verified + below, below, verified, covered, rank, ratio_key, -budget, str(score.get("mode")))
    raise KeyError(policy)


def select_policy_candidate(
    policy: str,
    scores: list[dict[str, Any]],
) -> dict[str, Any]:
    if policy == "primary_hybrid_rho_first":
        scores = [score for score in scores if score.get("mode") in PRIMARY_HYBRID_MODES]
    if not scores:
        raise ValueError(f"no candidates for policy {policy}")
    return max(scores, key=lambda score: policy_sort_key(policy, score))


def make_scan_args(args: argparse.Namespace, mode: str, budget: int) -> argparse.Namespace:
    local = argparse.Namespace(**vars(args))
    local.mode = mode
    local.budget_top_k = budget
    return local


def scan_fixed_prefix(
    verifier: Any,
    selected: dict[str, Any],
    source: dict[str, Any],
    built: dict[str, Any],
    local_args: Any,
    mode: str,
    budget_top_k: int,
) -> dict[str, Any]:
    p = int(built["p"])
    scouts_by_pos = {int(scout["scout_pos"]): scout for scout in built["scouts"]}
    components = association_probe.build_components(built["scouts"], built["rows"], p)
    feature_rows = preassociation_filter_probe.leaf_public_features(components, scouts_by_pos, p)
    filter_seed = f"{local_args.filter_seed_prefix}:{built['target']}:{mode}"
    ranked = sorted(feature_rows, key=lambda row: preassociation_filter_probe.score_key(row, mode, filter_seed))
    prefix_count = min(max(1, int(budget_top_k)), len(ranked))
    prefix_selected = {int(row["leaf_index"]) for row in ranked[:prefix_count]}
    exact_leaves = set(source_leaf_indices(source))
    rank_by_leaf = {int(row["leaf_index"]): index for index, row in enumerate(ranked, start=1)}
    scan = direct_witness_probe.scan_selected(
        verifier,
        built,
        components,
        prefix_selected,
        local_args,
    )
    events = scan.get("relation_events") or []
    linear_forms = [compact_form(index, event) for index, event in enumerate(events)]
    exact_leaf = next(iter(sorted(exact_leaves))) if exact_leaves else None
    feature_by_leaf = {int(row["leaf_index"]): row for row in feature_rows}
    return {
        **compact_selected(selected),
        "base_order": int(built.get("order") or 0),
        "budget_top_k": int(budget_top_k),
        "candidate_verifications": int(scan.get("candidate_verifications") or 0),
        "challenge_seed_matches_p947": built.get("challenge_seed") == parse_challenge_seed(selected.get("surface_id")),
        "curve_prime": p,
        "derived_secret": scan.get("derived_secret"),
        "exact_leaf_features_posthoc": compact_feature(feature_by_leaf.get(int(exact_leaf))) if exact_leaf is not None else None,
        "exact_leaf_rank_posthoc": {
            str(leaf): rank_by_leaf.get(int(leaf))
            for leaf in sorted(exact_leaves)
        },
        "filter_seed": filter_seed,
        "generic_rho_steps": int(built.get("generic_rho_steps") or 0),
        "linear_form_count": len(linear_forms),
        "linear_forms": linear_forms,
        "materialized": True,
        "mode": mode,
        "prefix_contains_exact_leaf_posthoc": exact_leaves.issubset(prefix_selected),
        "prefix_leaf_count": len(prefix_selected),
        "prefix_ops": int(scan.get("preassociation_filter_ops") or 0),
        "prefix_ops_over_rho": scan.get("preassociation_filter_ops_over_rho"),
        "prefix_top_k": prefix_count,
        "rank": int(scan.get("rank") or 0),
        "relation_count": int(scan.get("relation_count") or 0),
        "row_public_key_verified": bool(scan.get("row_public_key_verified")),
        "selected_hit_events": int(scan.get("selected_hit_events") or 0),
        "selected_hit_roots": int(scan.get("selected_hit_roots") or 0),
        "source_factor_zero_leaf_indices_posthoc": sorted(exact_leaves),
        "verifier_challenge_seed": built.get("challenge_seed"),
        "_events": events,
    }


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
    training_selection: dict[str, Any],
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
    exact_covered = all(row.get("prefix_contains_exact_leaf_posthoc") for row in rows)
    return {
        "base_order": order,
        "budget_top_k": parsed.get("budget_top_k"),
        "challenge_seed": parsed.get("challenge_seed"),
        "exact_leaf_covered_posthoc": exact_covered,
        "mode": parsed.get("mode"),
        "modular_form_rank": matrix_rank,
        "policy": parsed.get("policy"),
        "prefix_ops": ops,
        "prefix_ops_beats_rho": bool(rho and ops < rho),
        "prefix_ops_over_rho": round(ops / max(1, rho), 8) if rho else None,
        "rho": rho,
        "row_count": len(rows),
        "row_keys": sorted({str(row.get("row_key")) for row in rows}),
        "target": parsed.get("target"),
        "training_selection": training_selection,
        "transfer_indices": sorted({int_value(row.get("transfer_index")) for row in rows}),
        "unique_form_count": len(forms),
        **union,
    }


def summarize(results: list[dict[str, Any]], row_results: list[dict[str, Any]], errors: list[dict[str, Any]]) -> dict[str, Any]:
    verified = [result for result in results if result.get("union_public_key_verified")]
    below_verified = [result for result in verified if result.get("prefix_ops_beats_rho")]
    transfer806 = [
        result
        for result in results
        if 806 in {int_value(value) for value in result.get("transfer_indices") or []}
    ]
    policy_counts: dict[str, dict[str, Any]] = {}
    for policy in sorted({str(result.get("policy")) for result in results}):
        policy_results = [result for result in results if str(result.get("policy")) == policy]
        policy_verified = [result for result in policy_results if result.get("union_public_key_verified")]
        policy_below = [result for result in policy_verified if result.get("prefix_ops_beats_rho")]
        policy_counts[policy] = {
            "below_rho_verified_count": len(policy_below),
            "result_count": len(policy_results),
            "transfer806_public_key_verified": any(
                806 in {int_value(value) for value in result.get("transfer_indices") or []}
                and result.get("union_public_key_verified")
                for result in policy_results
            ),
            "verified_count": len(policy_verified),
        }
    selected_modes = Counter(str(result.get("mode")) for result in results)
    selected_budgets = Counter(str(result.get("budget_top_k")) for result in results)
    summary = {
        "below_rho_verified_count": len(below_verified),
        "error_count": len(errors),
        "heldout_policy_result_count": len(results),
        "max_union_rank": max((int_value(result.get("union_rank")) for result in results), default=0),
        "policy_summary": policy_counts,
        "row_scan_count": len(row_results),
        "rows_with_forms": sum(1 for row in row_results if int_value(row.get("linear_form_count")) > 0),
        "selected_budget_counts": dict(selected_budgets.most_common()),
        "selected_mode_counts": dict(selected_modes.most_common()),
        "transfer806_best_ops_over_rho": min(
            (
                float(result.get("prefix_ops_over_rho"))
                for result in transfer806
                if result.get("prefix_ops_over_rho") is not None
            ),
            default=None,
        ),
        "transfer806_best_verified_ops_over_rho": min(
            (
                float(result.get("prefix_ops_over_rho"))
                for result in transfer806
                if result.get("union_public_key_verified") and result.get("prefix_ops_over_rho") is not None
            ),
            default=None,
        ),
        "transfer806_best_rank": max((int_value(result.get("union_rank")) for result in transfer806), default=0),
        "transfer806_below_rho_verified_count": sum(
            1 for result in transfer806 if result.get("union_public_key_verified") and result.get("prefix_ops_beats_rho")
        ),
        "transfer806_result_count": len(transfer806),
        "transfer806_verified_count": sum(1 for result in transfer806 if result.get("union_public_key_verified")),
        "unique_verifier_form_count": len(
            {
                (tuple(form.get("coeffs") or []), int_value(form.get("rhs")))
                for row in row_results
                for form in row.get("linear_forms") or []
            }
        ),
        "verified_count": len(verified),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: rows come from P947/P950 archive-selected surfaces.",
            "HELDOUT-TRANSFER: mode/top-k is trained without heldout transfer outcomes or heldout exact leaf rank.",
            "TRAINED-ON-P950: training uses P950 exact-prefix outcomes on non-heldout transfers; a broader fresh-window audit is still required.",
            "POLLARD-RHO BOUNDARY: this is a component selector audit, not an end-to-end faster-than-rho algorithm.",
        ],
    }
    summary["claim_status"] = determine_claim(summary)
    return summary


def determine_claim(summary: dict[str, Any]) -> str:
    if int_value(summary.get("transfer806_below_rho_verified_count")):
        return "P951_HELDOUT_TOPK_SELECTOR_CLOSES_806_BELOW_RHO"
    if int_value(summary.get("transfer806_verified_count")):
        return "P951_HELDOUT_TOPK_SELECTOR_CLOSES_806_ABOVE_RHO"
    if int_value(summary.get("below_rho_verified_count")):
        return "P951_HELDOUT_TOPK_SELECTOR_VERIFIES_BELOW_RHO_806_OPEN"
    if int_value(summary.get("verified_count")):
        return "P951_HELDOUT_TOPK_SELECTOR_VERIFIES_ABOVE_RHO"
    return "NEGATIVE_RESULT_P951_HELDOUT_TOPK_SELECTOR_NO_DERIVATION"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p950 = load_json(args.p950_source)
    index = build_p950_index(p950)
    all_modes = parse_modes(args.modes)
    selected_rows = sorted(selected_p947_rows(), key=selected_sort_key)
    rows_by_transfer: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for selected in selected_rows:
        rows_by_transfer[int_value(selected.get("transfer_index"), -1)].append(selected)

    budgets = candidate_budgets(index["rows_by_transfer_mode"], all_modes, args.max_top_k)
    verifier = relation_probe.load_verifier_module()
    records = verifier.load_records()
    config_source = load_json(args.config_source)
    context_cache: dict[str, tuple[dict[str, Any], dict[str, Any], Any, dict[str, Any]]] = {}

    row_results: list[dict[str, Any]] = []
    group_results: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    selections: list[dict[str, Any]] = []

    def context_for(selected: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], Any, dict[str, Any]] | None:
        surface_id = str(selected.get("surface_id"))
        if surface_id in context_cache:
            return context_cache[surface_id]
        source, source_error = find_source_policy_row(selected)
        challenge_seed = parse_challenge_seed(selected.get("surface_id"))
        if source is None or source_error or not challenge_seed:
            errors.append({**compact_selected(selected), "error": source_error or "missing challenge seed"})
            return None
        try:
            row_fields, built, local_args = build_context(
                verifier,
                records,
                config_source,
                args,
                selected,
                challenge_seed,
            )
        except Exception as exc:  # noqa: BLE001 - keep audit row-level.
            errors.append({**compact_selected(selected), "error": f"{type(exc).__name__}: {exc}"})
            return None
        if built.get("error"):
            errors.append({**compact_selected(selected), "error": built["error"]})
            return None
        context_cache[surface_id] = (row_fields, built, local_args, source)
        return context_cache[surface_id]

    for holdout in index["transfers"]:
        scores = [
            candidate_score(
                index["rows_by_transfer_mode"],
                index["groups_by_transfer_mode"],
                index["transfers"],
                holdout,
                mode,
                budget,
            )
            for mode in all_modes
            for budget in budgets
        ]
        for policy in POLICY_NAMES:
            selection = select_policy_candidate(policy, scores)
            selection = {**selection, "policy": policy}
            selections.append(selection)
            grouped_rows: list[dict[str, Any]] = []
            built_for_group = None
            for selected in rows_by_transfer.get(holdout, []):
                context = context_for(selected)
                if context is None:
                    continue
                _row_fields, built, local_args, source = context
                try:
                    row = scan_fixed_prefix(
                        verifier,
                        selected,
                        source,
                        built,
                        local_args,
                        str(selection["mode"]),
                        int(selection["budget_top_k"]),
                    )
                except Exception as exc:  # noqa: BLE001 - keep audit policy-level.
                    errors.append(
                        {
                            **compact_selected(selected),
                            "budget_top_k": selection["budget_top_k"],
                            "error": f"{type(exc).__name__}: {exc}",
                            "mode": selection["mode"],
                            "policy": policy,
                        }
                    )
                    continue
                row["policy"] = policy
                row["training_selection"] = selection
                row_results.append(strip_private(row))
                grouped_rows.append(row)
                built_for_group = built
            if grouped_rows and built_for_group is not None:
                key = group_key(verifier, grouped_rows[0], built_for_group)
                group_results.append(group_union_report(verifier, key, grouped_rows, built_for_group, selection))

    summary = summarize(group_results, row_results, errors)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p950_source": str(args.p950_source),
            "script": str(Path(__file__)),
        },
        "claim_status": summary["claim_status"],
        "created_at": now_iso(),
        "errors": errors,
        "heldout_results": group_results,
        "method": "p951_leave_one_transfer_topk_selector",
        "parameters": {
            "budgets": budgets,
            "config_source": str(args.config_source),
            "filter_mode": args.filter_mode,
            "max_top_k": args.max_top_k,
            "modes": all_modes,
            "p950_source": str(args.p950_source),
            "policies": list(POLICY_NAMES),
            "row_pool": args.row_pool,
            "scout_limit": args.scout_limit,
            "scout_mode": args.scout_mode,
            "scout_order": args.scout_order,
            "seed": args.seed,
            "selected_limit": args.selected_limit,
        },
        "row_results": row_results,
        "schema": SCHEMA,
        "selector_selections": selections,
        "summary": summary,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--p950-source", type=Path, default=DEFAULT_P950_SOURCE)
    parser.add_argument("--config-source", type=Path, default=DEFAULT_CONFIG_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--modes", default=",".join(DEFAULT_MODES))
    parser.add_argument("--max-top-k", type=int, default=128)
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
        f"heldout_results={summary['heldout_policy_result_count']} "
        f"verified={summary['verified_count']} "
        f"below_rho={summary['below_rho_verified_count']} "
        f"transfer806_verified={summary['transfer806_verified_count']} "
        f"transfer806_below_rho={summary['transfer806_below_rho_verified_count']} "
        f"transfer806_best_rank={summary['transfer806_best_rank']} "
        f"errors={summary['error_count']} "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
