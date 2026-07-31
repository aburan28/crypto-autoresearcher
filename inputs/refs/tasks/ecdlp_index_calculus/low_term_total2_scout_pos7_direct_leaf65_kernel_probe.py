#!/usr/bin/env python3
"""Direct source-charged scout for the leaf-65 scout-7 point-match kernel.

The passive point-match token scout made the construction target stable:
double scout-7 ``11,11,15,15`` point matches, leaf ``65``, branch-local
candidate positions ``1,1``.  This probe asks whether that target becomes cheap
when every attempted source case tests only the leaf-65 branch instead of
replaying the full ordered preform stream.

The result is still model-bound.  Some ledgers omit signed-pair and/or row-pool
setup to represent a future constructive source policy; those ledgers are work
orders, not completed speedups.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import json
from datetime import datetime, timezone
from math import ceil
from pathlib import Path
from typing import Any

import frontier_signed_eval_cover_critical_leaf_probe as critical_leaf_probe
import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_direct_witness_probe as direct_witness_probe
import low_term_total2_fixed_leaf_shared_product_timing_probe as timing_probe
from low_term_total2_auxiliary_relation_event_assembly_scout import label, salt_from_row_key, term_shape
from low_term_total2_scout_pos7_candidate_form_pretest_scout import support_label
from low_term_total2_scout_pos7_preform_source_charged_collector import (
    artifact_window,
    baseline_comparison,
    case_key,
    int_value,
    load_json,
    parse_paths,
    rank_labels_by_source_case,
    ratio,
    source_cases,
    write_json,
)


COST_MODELS = (
    "targeted_full_setup",
    "single_branch_with_rowpool",
    "rowpool_charged_leaf65_kernel",
    "constructive_leaf65_kernel",
    "leaf_event_point_lower_bound",
    "affine_event_point_only_lower_bound",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def scout7_leaf65_terms(scout: dict[str, Any]) -> bool:
    terms = [int_value(index) for index in scout.get("unsigned_indices") or []]
    return int_value(scout.get("scout_pos")) == 7 and label(terms) == "11,11,15,15"


def point_match_summary(point_matches: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "point_match_candidate_pos_multiset": ",".join(str(int_value(item.get("candidate_pos"))) for item in point_matches),
        "point_match_count": len(point_matches),
        "point_match_leaf_multiset": ",".join(str(int_value(item.get("leaf_index"))) for item in point_matches),
        "point_match_scout_pos_multiset": ",".join(str(int_value(item.get("scout_pos"))) for item in point_matches),
        "point_match_support_multiset": ";".join(sorted(str(item.get("factor_support_label")) for item in point_matches)),
        "point_match_terms_multiset": ";".join(sorted(str(item.get("terms_label")) for item in point_matches)),
        "pos7_11111515_distinct_form_count": len(
            {
                (int_value(item.get("q_coeff")), int_value(item.get("rhs")), str(item.get("terms_label")))
                for item in point_matches
            }
        ),
        "pos7_11111515_distinct_row_count": len({str(item.get("row_key")) for item in point_matches}),
        "pos7_11111515_point_match_count": len(point_matches),
    }


def cost_ratios(model_ops: dict[str, int], rho: int) -> dict[str, float | None]:
    return {model: ratio(ops, rho) for model, ops in model_ops.items()}


def scan_direct_leaf65_case(
    source: dict[str, Any],
    row: dict[str, Any],
    target_leaf: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    point_matches: list[dict[str, Any]] = []
    model_ops = {model: 0 for model in COST_MODELS}
    context_rows: list[dict[str, Any]] = []
    rho = 0
    try:
        verifier, contexts, _product_factor, _max_relations = timing_probe.selected_contexts_from_source_case(source, row)
        form_keys: set[tuple[tuple[int, ...], int]] = set()
        for context_index, context in enumerate(contexts):
            built = context["built"]
            components = context["components"]
            p = int_value(built.get("p"))
            order = int_value(built.get("order"))
            rho = max(rho, int_value(built.get("generic_rho_steps")))
            scout_to_leaf = critical_leaf_probe.scout_leaf_map(components)
            scout7_leaf = int_value(scout_to_leaf.get(7), -1)
            selected = {target_leaf} if scout7_leaf == target_leaf else set()
            cover = direct_witness_probe.preassociation_filter_probe.filtered_leaf_gcd_association(
                built["scouts"],
                components,
                p,
                selected,
            )
            scheduled_rows = direct_witness_probe.eval_cover_probe.schedule_rows(
                built["rows"],
                cover["row_hit_count"],
                int_value(built.get("scheduled_row_count")),
            )
            scheduled_by_original = {int_value(item.get("original_trial")): item for item in scheduled_rows}
            branch_scouts = [
                scout
                for scout in built["scouts"]
                if scout7_leaf65_terms(scout) and int_value(scout_to_leaf.get(int_value(scout.get("scout_pos"))), -1) == target_leaf
            ]
            branch_scout = branch_scouts[0] if branch_scouts else None
            hit_rows: list[dict[str, Any]] = []
            if branch_scout is not None:
                hit_rows = [
                    scheduled_by_original[trial]
                    for trial in cover["hits_by_scout"].get(int_value(branch_scout.get("scout_pos")), [])
                    if trial in scheduled_by_original
                ]

            event_ops = len(hit_rows)
            point_ops = 1 if hit_rows and branch_scout is not None else 0
            affine_match_count = 0
            if branch_scout is not None and hit_rows:
                candidate_point = verifier.add_points(branch_scout["left"]["point"], branch_scout["right"]["point"], built["ainvs"], p)
                terms = [int_value(index) for index in branch_scout.get("unsigned_indices") or []]
                terms_lbl = label(terms)
                support_lbl = support_label(terms)
                row_key = str(context.get("row_key") or "")
                for hit_row in hit_rows:
                    if candidate_point != hit_row["point"]:
                        continue
                    affine_match_count += 1
                    relation = {"a": int_value(hit_row.get("a")), "b": int_value(hit_row.get("b")), "indices": terms}
                    relation_terms = verifier.relation_terms(relation, built["challenge"], built["ainvs"], p)
                    if relation_terms is None:
                        continue
                    coeffs, rhs = verifier.relation_linear_form(relation, relation_terms, built["challenge"], order)
                    form_key = (tuple(int_value(coeff) % order for coeff in coeffs), int_value(rhs) % order)
                    form_duplicate = form_key in form_keys
                    form_keys.add(form_key)
                    point_matches.append(
                        {
                            "candidate_pos": 1,
                            "factor_support_label": support_lbl,
                            "form_duplicate": form_duplicate,
                            "leaf_index": target_leaf,
                            "original_trial": int_value(hit_row.get("original_trial")),
                            "q_coeff": int_value(coeffs[0]) % order,
                            "rhs": int_value(rhs) % order,
                            "row_key": row_key,
                            "row_salt": salt_from_row_key(row_key),
                            "scheduled_trial": int_value(hit_row.get("trial")),
                            "scout_pos": int_value(branch_scout.get("scout_pos")),
                            "term_shape": term_shape(terms),
                            "terms": terms,
                            "terms_label": terms_lbl,
                        }
                    )

            row_factor = max(1, int_value(getattr(context["local_args"], "row_factor", 1), 1))
            product_factor = max(1, int_value(getattr(context["local_args"], "product_factor", 1), 1))
            selected_signed_pair_count = int_value(built.get("selected_signed_pair_count"))
            row_pool_ops = ceil(int_value(built.get("row_pool")) / row_factor)
            product_ops = ceil(len(selected) / product_factor)
            selected_hit_roots = int_value(cover.get("selected_hit_root_values"))
            leaf_ops = len(selected)
            branch_setup_ops = 1 if branch_scout is not None else 0
            context_model_ops = {
                "targeted_full_setup": selected_signed_pair_count
                + row_pool_ops
                + product_ops
                + selected_hit_roots
                + leaf_ops
                + event_ops
                + point_ops,
                "single_branch_with_rowpool": branch_setup_ops
                + row_pool_ops
                + product_ops
                + selected_hit_roots
                + leaf_ops
                + event_ops
                + point_ops,
                "rowpool_charged_leaf65_kernel": row_pool_ops + product_ops + selected_hit_roots + leaf_ops + event_ops + point_ops,
                "constructive_leaf65_kernel": product_ops + selected_hit_roots + leaf_ops + event_ops + point_ops,
                "leaf_event_point_lower_bound": selected_hit_roots + leaf_ops + event_ops + point_ops,
                "affine_event_point_only_lower_bound": event_ops + point_ops,
            }
            for model, ops in context_model_ops.items():
                model_ops[model] += int(ops)
            context_rows.append(
                {
                    "affine_match_count": affine_match_count,
                    "branch_scout_count": len(branch_scouts),
                    "context_index": context_index,
                    "event_ops": event_ops,
                    "model_ops": context_model_ops,
                    "point_ops": point_ops,
                    "row_key": str(context.get("row_key") or ""),
                    "row_pool_ops": row_pool_ops,
                    "scout7_leaf": scout7_leaf,
                    "selected_hit_roots": selected_hit_roots,
                    "selected_leaf_count": len(selected),
                    "selected_signed_pair_count": selected_signed_pair_count,
                }
            )
    except Exception as exc:  # noqa: BLE001 - preserve research replay failures.
        errors.append({"error": "direct_leaf65_scan_failed", "message": str(exc)})

    return (
        {
            **point_match_summary(point_matches),
            "accepted": len(point_matches) >= 2,
            "context_rows": context_rows,
            "model_ops": model_ops,
            "model_ops_over_rho": cost_ratios(model_ops, rho),
            "point_matches": point_matches,
            "rho": rho,
            "target_leaf": target_leaf,
        },
        errors,
    )


def collect_group(
    source_path: Path,
    source: dict[str, Any],
    rows: list[dict[str, Any]],
    rank_labels: dict[tuple[str, str, int, str, int, tuple[str, ...]], dict[str, Any]],
    target_leaf: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    attempts: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for row in rows:
        scan, scan_errors = scan_direct_leaf65_case(source, row, target_leaf)
        score = rank_labels.get(case_key(source_path, row), {})
        attempt = {
            **scan,
            "public_key_verified": bool(row.get("public_key_verified")),
            "rank": int_value(row.get("rank")),
            "rank_gain": int_value(score.get("rank_gain")) if score else None,
            "row_keys": row.get("row_keys") or [],
            "row_selector": row.get("row_selector"),
            "selected_leaf_count": int_value(row.get("selected_leaf_count")),
            "selected_row_count": int_value(row.get("selected_row_count")),
            "selector": row.get("selector"),
            "source_path": str(source_path),
            "source_policy": row.get("source_policy"),
            "source_verified": bool(row.get("source_verified")),
            "top_k": int_value(row.get("top_k")),
            "transfer_index": int_value(row.get("transfer_index")),
            "unique_factor_relation_gain": int_value(score.get("unique_factor_relation_gain")) if score else None,
        }
        attempts.append(attempt)
        errors.extend({**item, "source_path": str(source_path), "transfer_index": int_value(row.get("transfer_index"))} for item in scan_errors)
        if bool(scan.get("accepted")):
            break

    window = artifact_window(source_path)
    model_ops = {model: sum(int_value(attempt.get("model_ops", {}).get(model)) for attempt in attempts) for model in COST_MODELS}
    rho_values = [int_value(attempt.get("rho")) for attempt in attempts if int_value(attempt.get("rho")) > 0]
    rho = max(rho_values) if rho_values else 0
    stop = attempts[-1] if attempts and attempts[-1].get("accepted") else None
    return (
        {
            "attempt_count": len(attempts),
            "attempts": attempts,
            "has_accepted_stop": stop is not None,
            "has_rank_gain_stop": bool(stop and int_value(stop.get("rank_gain")) > 0),
            "model_ops": model_ops,
            "model_ops_over_rho": cost_ratios(model_ops, rho),
            "rho": rho,
            "source_path": str(source_path),
            "stop": stop,
            "target_leaf": target_leaf,
            "window": f"{window[0]}_{window[1]}" if window else "",
            "window_start": window[0] if window else int_value(attempts[0].get("transfer_index")) if attempts else 0,
        },
        errors,
    )


def split_groups(groups: list[dict[str, Any]], calibration_end: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return (
        [group for group in groups if int_value(group.get("window_start")) <= calibration_end],
        [group for group in groups if int_value(group.get("window_start")) > calibration_end],
    )


def summarize(groups: list[dict[str, Any]]) -> dict[str, Any]:
    accepted_groups = [group for group in groups if group.get("has_accepted_stop")]
    rank_groups = [group for group in groups if group.get("has_rank_gain_stop")]
    false_groups = [group for group in accepted_groups if not group.get("has_rank_gain_stop")]
    rho = max([int_value(group.get("rho")) for group in groups if int_value(group.get("rho")) > 0] or [0])
    model_summaries: dict[str, Any] = {}
    for model in COST_MODELS:
        ops = sum(int_value(group.get("model_ops", {}).get(model)) for group in groups)
        model_summaries[model] = {
            "cost_per_accepted_stop_over_rho": ratio(ops, rho * len(accepted_groups)) if accepted_groups and rho else None,
            "cost_per_rank_gain_stop_over_rho": ratio(ops, rho * len(rank_groups)) if rank_groups and rho else None,
            "ops": ops,
            "ops_over_rho": ratio(ops, rho),
        }
    return {
        "accepted_stop_count": len(accepted_groups),
        "attempt_count": sum(int_value(group.get("attempt_count")) for group in groups),
        "false_accept_count": len(false_groups),
        "group_count": len(groups),
        "model_summaries": model_summaries,
        "precision": ratio(len(rank_groups), len(accepted_groups)) if accepted_groups else None,
        "rank_gain_stop_count": len(rank_groups),
    }


def current_baseline_summary(summary: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for split_name in ("calibration", "validation"):
        split = summary.get(split_name) if isinstance(summary.get(split_name), dict) else {}
        models = split.get("model_summaries") if isinstance(split.get("model_summaries"), dict) else {}
        out[split_name] = {
            "rank_gain_stop_count": split.get("rank_gain_stop_count"),
            "cost_per_rank_gain_stop_over_rho": (models.get("constructive_leaf65_kernel") or {}).get("cost_per_rank_gain_stop_over_rho"),
        }
    return out


def compare_baseline_collector(baseline: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    return baseline_comparison(baseline, current_baseline_summary(current)) if baseline else {}


def claim_status(validation_summary: dict[str, Any]) -> str:
    rank_hits = int_value(validation_summary.get("rank_gain_stop_count"))
    if rank_hits <= 0:
        return "SCOUT_POS7_DIRECT_LEAF65_KERNEL_MISSES_VALIDATION"
    models = validation_summary.get("model_summaries") if isinstance(validation_summary.get("model_summaries"), dict) else {}

    def model_cost(name: str) -> float | None:
        value = (models.get(name) or {}).get("cost_per_rank_gain_stop_over_rho")
        return float(value) if value is not None else None

    if (cost := model_cost("targeted_full_setup")) is not None and cost < 1.0:
        return "SCOUT_POS7_DIRECT_LEAF65_KERNEL_TARGETED_FULL_SETUP_BELOW_RHO"
    for name in ("single_branch_with_rowpool", "rowpool_charged_leaf65_kernel"):
        if (cost := model_cost(name)) is not None and cost < 1.0:
            return "SCOUT_POS7_DIRECT_LEAF65_KERNEL_ROWPOOL_CHARGED_MODEL_BELOW_RHO"
    for name in ("constructive_leaf65_kernel", "leaf_event_point_lower_bound"):
        if (cost := model_cost(name)) is not None and cost < 1.0:
            return "SCOUT_POS7_DIRECT_LEAF65_KERNEL_CONSTRUCTIVE_MODEL_BELOW_RHO_WORK_ORDER"
    if (cost := model_cost("affine_event_point_only_lower_bound")) is not None and cost < 1.0:
        return "SCOUT_POS7_DIRECT_LEAF65_KERNEL_ONLY_AFFINE_LOWER_BOUND_BELOW_RHO"
    return "SCOUT_POS7_DIRECT_LEAF65_KERNEL_ALL_MODELS_ABOVE_RHO"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-glob",
        default="ecdlp_index_calculus_state/frontier_public_leaf_policy_p231_frozen_prefix_fixed_row_*_col15_selector_expanded_probe.json",
    )
    parser.add_argument("--source-list-from-baseline", action="store_true")
    parser.add_argument("--baseline-collector")
    parser.add_argument(
        "--direct-cert-glob",
        default="ecdlp_index_calculus_state/low_term_total2_direct_relation_equation_certificate_22050_col15_lowterm_support5_*_probe.json",
    )
    parser.add_argument(
        "--rank-scorer-glob",
        default="ecdlp_index_calculus_state/low_term_total2_factor_rank_candidate_scorer_target67_22050_multibranch_plus_priority_hash6_plus_direct_col15_lowterm_support5_*_probe.json",
    )
    parser.add_argument("--target", default="22050.cf1@11731")
    parser.add_argument("--selector", default="mode_low_term_support_total5")
    parser.add_argument("--top-k", type=int, default=16)
    parser.add_argument("--min-transfer", type=int, default=3560)
    parser.add_argument("--calibration-end", type=int, default=4064)
    parser.add_argument("--target-leaf", type=int, default=65)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def source_paths_from_args(args: argparse.Namespace, baseline: dict[str, Any]) -> list[Path]:
    if args.source_list_from_baseline:
        artifacts = baseline.get("artifacts") if isinstance(baseline.get("artifacts"), dict) else {}
        return [Path(str(path)) for path in artifacts.get("source_paths") or []]
    return [
        path
        for path in parse_paths(args.source_glob)
        if (window := artifact_window(path)) is not None and window[0] >= args.min_transfer
    ]


def main() -> None:
    args = parse_args()
    baseline = load_json(Path(args.baseline_collector)) if args.baseline_collector else {}
    source_paths = source_paths_from_args(args, baseline)
    certificate_paths = [
        path
        for path in parse_paths(args.direct_cert_glob)
        if (window := artifact_window(path)) is not None and window[0] >= args.min_transfer
    ]
    scorer_paths = [
        path
        for path in parse_paths(args.rank_scorer_glob)
        if (window := artifact_window(path)) is not None and window[0] >= args.min_transfer
    ]
    rank_labels = rank_labels_by_source_case(certificate_paths, scorer_paths)
    groups: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    rows_by_source_count: dict[str, int] = {}
    for source_path in source_paths:
        source = load_json(source_path)
        rows = source_cases(source_path, source, args.target, args.selector, args.top_k, args.min_transfer)
        rows_by_source_count[str(source_path)] = len(rows)
        if not rows:
            continue
        group, group_errors = collect_group(source_path, source, rows, rank_labels, args.target_leaf)
        groups.append(group)
        errors.extend(group_errors)
    groups.sort(key=lambda group: (int_value(group.get("window_start")), str(group.get("source_path"))))
    calibration, validation = split_groups(groups, args.calibration_end)
    current_summary = {
        "calibration": summarize(calibration),
        "validation": summarize(validation),
    }
    payload = {
        "artifacts": {
            "baseline_collector": args.baseline_collector,
            "direct_certificates": [str(path) for path in certificate_paths],
            "rank_scorers": [str(path) for path in scorer_paths],
            "source_paths": [str(path) for path in source_paths],
        },
        "baseline_comparison": compare_baseline_collector(baseline, current_summary),
        "claim_status": claim_status(current_summary["validation"]),
        "cost_model_definitions": {
            "affine_event_point_only_lower_bound": "raw branch row-hit equality checks plus one candidate-point addition when a hit row exists; omits root/product/leaf/row-pool/signed-pair setup.",
            "constructive_leaf65_kernel": "one selected leaf/product plus selected hit roots, event checks, and candidate-point additions; omits signed-pair and row-pool setup as a source-policy work order.",
            "leaf_event_point_lower_bound": "selected hit roots plus selected leaf plus event checks plus candidate-point additions; omits product, signed-pair, and row-pool setup.",
            "rowpool_charged_leaf65_kernel": "constructive leaf-65 kernel plus row-pool setup.",
            "single_branch_with_rowpool": "rowpool charged kernel plus one explicit scout-7 branch setup op.",
            "targeted_full_setup": "existing selected signed-pair setup plus row-pool/product/leaf/root/event/point work restricted to leaf 65.",
        },
        "created_at": now_iso(),
        "errors": errors,
        "groups": groups,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: every attempted source case is replayed through the existing context builder, but operation ledgers only charge the declared leaf-65 branch work.",
            "The constructive and lower-bound ledgers omit setup that a future source generator would need to remove, amortize, or avoid.",
            "Rank/public-key verification labels are used only for evaluation and are not features.",
            "A below-rho constructive ledger is an index-calculus precursor work order, not a deployed-curve ECDLP break.",
        ],
        "parameters": {
            "calibration_end": args.calibration_end,
            "min_transfer": args.min_transfer,
            "selector": args.selector,
            "source_list_from_baseline": bool(args.source_list_from_baseline),
            "target": args.target,
            "target_leaf": args.target_leaf,
            "top_k": args.top_k,
        },
        "rows_by_source_count": rows_by_source_count,
        "schema": "ecdlp.low_term_total2_scout_pos7_direct_leaf65_kernel_probe.v1",
        "summary": current_summary,
    }
    write_json(Path(args.out), payload)
    print(
        json.dumps(
            {
                "baseline_comparison": payload["baseline_comparison"],
                "claim_status": payload["claim_status"],
                "error_count": len(errors),
                "summary": payload["summary"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
