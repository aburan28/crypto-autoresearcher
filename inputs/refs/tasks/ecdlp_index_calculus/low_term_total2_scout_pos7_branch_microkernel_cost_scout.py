#!/usr/bin/env python3
"""Cost scout for cheaper scout-7 branch micro-kernels.

The first-case preform gate validated the double scout-7 ``11,11,15,15``
shape, but remained far above rho because every source group paid a first-case
preform scan.  This scout replays the first source case and charges only the
leaf containing ``scout_pos=7`` under several explicit cost models:

* targeted full setup: the existing preassociation ledger restricted to the
  scout-7 leaf;
* single-scout setup: replace the full signed-pair setup by one branch setup;
* pair-setup cached: assume signed-pair setup is cached or forced externally;
* pair-and-row cached: also assume row-pool setup is cached per source family;
* leaf-event lower bound: charge only leaf/root/event work.

The last models are optimistic lower bounds and should be read only as work
orders for a measured micro-kernel, not as completed speedups.
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
from low_term_total2_scout_pos7_source_charged_collector import (
    int_value,
    load_json,
    ratio,
    source_cases,
    write_json,
)


COST_MODELS = (
    "targeted_full_setup",
    "single_scout_setup",
    "pair_setup_cached",
    "pair_and_row_cached",
    "leaf_event_only_lower_bound",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def scout7_terms(scout: dict[str, Any]) -> bool:
    return int_value(scout.get("scout_pos")) == 7 and label([int_value(index) for index in scout.get("unsigned_indices") or []]) == "11,11,15,15"


def point_match_summary(point_matches: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "point_match_count": len(point_matches),
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


def scan_first_case_branch(
    source: dict[str, Any],
    row: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    point_matches: list[dict[str, Any]] = []
    rho = 0
    model_ops = {name: 0 for name in COST_MODELS}
    context_rows: list[dict[str, Any]] = []
    try:
        verifier, contexts, _product_factor, _max_relations = timing_probe.selected_contexts_from_source_case(source, row)
        for context_index, context in enumerate(contexts):
            built = context["built"]
            components = context["components"]
            p = int_value(built.get("p"))
            order = int_value(built.get("order"))
            rho = max(rho, int_value(built.get("generic_rho_steps")))
            scout_to_leaf = critical_leaf_probe.scout_leaf_map(components)
            scout7_leaf = scout_to_leaf.get(7)
            selected = {int_value(scout7_leaf)} if scout7_leaf is not None else set()
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
            branch_scouts = [scout for scout in built["scouts"] if scout7_terms(scout)]
            raw_root_hit_candidate_count = 0
            affine_match_count = 0
            candidate_point_additions = 0
            for scout in branch_scouts[:1]:
                scout_pos = int_value(scout.get("scout_pos"))
                hit_rows = [
                    scheduled_by_original[trial]
                    for trial in cover["hits_by_scout"].get(scout_pos, [])
                    if trial in scheduled_by_original
                ]
                if not hit_rows:
                    continue
                candidate_point_additions += 1
                candidate_point = verifier.add_points(scout["left"]["point"], scout["right"]["point"], built["ainvs"], p)
                terms = [int_value(index) for index in scout.get("unsigned_indices") or []]
                terms_lbl = label(terms)
                support_lbl = support_label(terms)
                for hit_row in hit_rows:
                    raw_root_hit_candidate_count += 1
                    if candidate_point != hit_row["point"]:
                        continue
                    affine_match_count += 1
                    relation = {"a": int_value(hit_row.get("a")), "b": int_value(hit_row.get("b")), "indices": terms}
                    relation_terms = verifier.relation_terms(relation, built["challenge"], built["ainvs"], p)
                    if relation_terms is None:
                        continue
                    coeffs, rhs = verifier.relation_linear_form(relation, relation_terms, built["challenge"], order)
                    row_key = str(context.get("row_key") or "")
                    point_matches.append(
                        {
                            "candidate_point_addition_index": candidate_point_additions,
                            "factor_support_label": support_lbl,
                            "leaf_index": int_value(scout7_leaf),
                            "original_trial": int_value(hit_row.get("original_trial")),
                            "q_coeff": int_value(coeffs[0]) % order,
                            "rhs": int_value(rhs) % order,
                            "row_key": row_key,
                            "row_salt": salt_from_row_key(row_key),
                            "scheduled_trial": int_value(hit_row.get("trial")),
                            "scout_pos": scout_pos,
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
            event_ops = raw_root_hit_candidate_count
            point_ops = candidate_point_additions
            context_model_ops = {
                "targeted_full_setup": selected_signed_pair_count
                + row_pool_ops
                + product_ops
                + selected_hit_roots
                + leaf_ops
                + event_ops
                + point_ops,
                "single_scout_setup": 1 + row_pool_ops + product_ops + selected_hit_roots + leaf_ops + event_ops + point_ops,
                "pair_setup_cached": row_pool_ops + product_ops + selected_hit_roots + leaf_ops + event_ops + point_ops,
                "pair_and_row_cached": product_ops + selected_hit_roots + leaf_ops + event_ops + point_ops,
                "leaf_event_only_lower_bound": selected_hit_roots + leaf_ops + event_ops + point_ops,
            }
            for name, ops in context_model_ops.items():
                model_ops[name] += int(ops)
            context_rows.append(
                {
                    "affine_match_count": affine_match_count,
                    "branch_scout_count": len(branch_scouts),
                    "context_index": context_index,
                    "model_ops": context_model_ops,
                    "raw_root_hit_candidate_count": raw_root_hit_candidate_count,
                    "row_pool_ops": row_pool_ops,
                    "scout7_leaf": int_value(scout7_leaf),
                    "selected_hit_roots": selected_hit_roots,
                    "selected_leaf_count": len(selected),
                    "selected_signed_pair_count": selected_signed_pair_count,
                }
            )
    except Exception as exc:  # noqa: BLE001 - preserve research replay failures.
        errors.append({"error": "scout7_branch_scan_failed", "message": str(exc)})
    return (
        {
            **point_match_summary(point_matches),
            "accepted": len(point_matches) >= 2,
            "context_rows": context_rows,
            "model_ops": model_ops,
            "model_ops_over_rho": {name: ratio(ops, rho) for name, ops in model_ops.items()},
            "point_matches": point_matches,
            "rho": rho,
        },
        errors,
    )


def split_rows(rows: list[dict[str, Any]], calibration_end: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return (
        [row for row in rows if int_value(row.get("window_start")) <= calibration_end],
        [row for row in rows if int_value(row.get("window_start")) > calibration_end],
    )


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    accepted = [row for row in rows if row.get("accepted")]
    rank_hits = [row for row in accepted if row.get("has_rank_gain_stop")]
    false_accepts = [row for row in accepted if not row.get("has_rank_gain_stop")]
    model_summaries: dict[str, Any] = {}
    for model in COST_MODELS:
        cost = sum(float(row["scan"]["model_ops_over_rho"].get(model) or 0.0) for row in rows)
        model_summaries[model] = {
            "cost_per_rank_gain_stop_over_rho": round(cost / len(rank_hits), 8) if rank_hits else None,
            "total_cost_over_rho": round(cost, 8),
        }
    return {
        "accepted_count": len(accepted),
        "false_accept_count": len(false_accepts),
        "group_count": len(rows),
        "model_summaries": model_summaries,
        "precision": round(len(rank_hits) / len(accepted), 8) if accepted else None,
        "rank_gain_stop_count": len(rank_hits),
        "recall": round(len(rank_hits) / max(1, sum(1 for row in rows if row.get("has_rank_gain_stop"))), 8),
    }


def claim_status(validation_summary: dict[str, Any]) -> str:
    models = validation_summary.get("model_summaries") if isinstance(validation_summary.get("model_summaries"), dict) else {}
    rank_hits = int_value(validation_summary.get("rank_gain_stop_count"))
    if rank_hits <= 0:
        return "SCOUT_POS7_BRANCH_MICROKERNEL_MISSES_VALIDATION"
    non_lower_models = ["targeted_full_setup", "single_scout_setup", "pair_setup_cached", "pair_and_row_cached"]
    if any(float((models.get(name) or {}).get("cost_per_rank_gain_stop_over_rho") or 999999.0) < 1.0 for name in non_lower_models):
        return "SCOUT_POS7_BRANCH_MICROKERNEL_NONLOWER_MODEL_BELOW_RHO"
    lower = (models.get("leaf_event_only_lower_bound") or {}).get("cost_per_rank_gain_stop_over_rho")
    if lower is not None and float(lower) < 1.0:
        return "SCOUT_POS7_BRANCH_MICROKERNEL_ONLY_LEAF_EVENT_LOWER_BOUND_BELOW_RHO"
    return "SCOUT_POS7_BRANCH_MICROKERNEL_ALL_MODELS_ABOVE_RHO"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collector", required=True)
    parser.add_argument("--calibration-end", type=int, default=3831)
    parser.add_argument("--target", default="22050.cf1@11731")
    parser.add_argument("--selector", default="mode_low_term_support_total5")
    parser.add_argument("--top-k", type=int, default=16)
    parser.add_argument("--min-transfer", type=int, default=3560)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    collector_path = Path(args.collector)
    collector = load_json(collector_path)
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for group in collector.get("groups") or []:
        if not isinstance(group, dict) or not group.get("source_path"):
            continue
        source_path = Path(str(group.get("source_path")))
        source = load_json(source_path)
        source_rows = source_cases(source_path, source, args.target, args.selector, args.top_k, args.min_transfer)
        if not source_rows:
            errors.append({"error": "missing_source_rows", "source_path": str(source_path)})
            continue
        scan, scan_errors = scan_first_case_branch(source, source_rows[0])
        rows.append(
            {
                "accepted": bool(scan.get("accepted")),
                "first_transfer_index": int_value(source_rows[0].get("transfer_index")),
                "has_accepted_stop": bool(group.get("has_accepted_stop")),
                "has_rank_gain_stop": bool(group.get("has_rank_gain_stop")),
                "scan": {key: value for key, value in scan.items() if key != "point_matches"},
                "source_path": str(source_path),
                "window": group.get("window"),
                "window_start": int_value(group.get("window_start")),
            }
        )
        errors.extend({**error, "source_path": str(source_path)} for error in scan_errors)
    rows.sort(key=lambda row: (int_value(row.get("window_start")), str(row.get("source_path"))))
    calibration, validation = split_rows(rows, args.calibration_end)
    calibration_summary = summarize(calibration)
    validation_summary = summarize(validation)
    payload = {
        "artifacts": {
            "collector": str(collector_path),
        },
        "claim_status": claim_status(validation_summary),
        "cost_model_definitions": {
            "leaf_event_only_lower_bound": "selected hit roots + selected leaf + raw scout-7 root-hit events + candidate-point additions; omits signed-pair and row-pool setup.",
            "pair_and_row_cached": "single scout-7 selected leaf plus roots/events/point additions; assumes signed-pair and row-pool setup are cached.",
            "pair_setup_cached": "pair_and_row_cached plus row-pool setup.",
            "single_scout_setup": "pair_setup_cached plus one branch setup op instead of full signed-pair setup.",
            "targeted_full_setup": "existing preassociation ledger restricted to the scout-7 leaf, including full signed-pair setup.",
        },
        "created_at": now_iso(),
        "errors": errors,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: replay targets only the first source case and only the leaf containing scout_pos=7.",
            "The non-full cost models are optimistic work-order ledgers, not measured implementations.",
            "The leaf_event_only_lower_bound omits signed-pair and row-pool setup and cannot be counted as an algorithmic speedup by itself.",
            "A below-rho lower bound only identifies headroom for a future measured micro-kernel/source policy.",
        ],
        "parameters": {
            "calibration_end": args.calibration_end,
            "min_transfer": args.min_transfer,
            "selector": args.selector,
            "target": args.target,
            "top_k": args.top_k,
        },
        "rows": rows,
        "schema": "ecdlp.low_term_total2_scout_pos7_branch_microkernel_cost_scout.v1",
        "summary": {
            "calibration": calibration_summary,
            "validation": validation_summary,
        },
    }
    write_json(Path(args.out), payload)
    print(
        json.dumps(
            {
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
