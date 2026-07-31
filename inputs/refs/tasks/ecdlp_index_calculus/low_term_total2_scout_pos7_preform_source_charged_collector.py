#!/usr/bin/env python3
"""Charge an early-stop collector for the scout-7 preform signal.

The candidate/form pretest found a structural rule below full verification:
``point_match_scout_pos_multiset=7,7``.  This collector tests whether that rule
actually helps the source-charged cost model.  It scans public source cases and
stops per source artifact once two point-matched scout-7 / ``11,11,15,15``
preforms appear, before calling full public-key relation verification.

This is still a model-bound collector: it reaches the candidate-hit boundary and
charges no-hit groups, but does not yet implement a lower-level shared-product
kernel.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import frontier_signed_eval_cover_critical_leaf_probe as critical_leaf_probe
import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_direct_witness_probe as direct_witness_probe
import low_term_total2_fixed_leaf_shared_product_timing_probe as timing_probe
from low_term_total2_auxiliary_relation_event_assembly_scout import label, salt_from_row_key, term_shape
from low_term_total2_scout_pos7_candidate_form_pretest_scout import support_label
from low_term_total2_scout_pos7_source_charged_collector import (
    artifact_window,
    case_key,
    int_value,
    load_json,
    parse_paths,
    rank_labels_by_source_case,
    ratio,
    source_cases,
    write_json,
)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def preform_accepts(point_matches: list[dict[str, Any]], accept_rule: str) -> bool:
    pos7 = [
        item
        for item in point_matches
        if int_value(item.get("scout_pos")) == 7 and str(item.get("terms_label")) == "11,11,15,15"
    ]
    if accept_rule == "point_match_scout7_double_11111515":
        return len(pos7) >= 2
    if accept_rule == "point_match_scout_pos_multiset_7_7":
        return (
            len(point_matches) == 2
            and all(int_value(item.get("scout_pos")) == 7 for item in point_matches)
            and all(str(item.get("terms_label")) == "11,11,15,15" for item in point_matches)
        )
    raise ValueError(f"unknown accept rule {accept_rule!r}")


def point_match_summary(point_matches: list[dict[str, Any]]) -> dict[str, Any]:
    pos7 = [
        item
        for item in point_matches
        if int_value(item.get("scout_pos")) == 7 and str(item.get("terms_label")) == "11,11,15,15"
    ]
    return {
        "point_match_candidate_pos_multiset": ",".join(str(int_value(item.get("candidate_pos"))) for item in point_matches),
        "point_match_count": len(point_matches),
        "point_match_scout_pos_multiset": ",".join(str(int_value(item.get("scout_pos"))) for item in point_matches),
        "point_match_support_multiset": ";".join(sorted(str(item.get("factor_support_label")) for item in point_matches)),
        "point_match_terms_multiset": ";".join(sorted(str(item.get("terms_label")) for item in point_matches)),
        "pos7_11111515_candidate_pos_multiset": ",".join(str(int_value(item.get("candidate_pos"))) for item in pos7),
        "pos7_11111515_distinct_form_count": len(
            {
                (int_value(item.get("q_coeff")), int_value(item.get("rhs")), str(item.get("terms_label")))
                for item in pos7
            }
        ),
        "pos7_11111515_distinct_row_count": len({str(item.get("row_key")) for item in pos7}),
        "pos7_11111515_point_match_count": len(pos7),
    }


def scan_preform_case(
    source: dict[str, Any],
    row: dict[str, Any],
    accept_rule: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    point_matches: list[dict[str, Any]] = []
    total_ops = 0
    rho = 0
    total_candidate_point_additions = 0
    total_x_matches = 0
    stopped = False
    try:
        verifier, contexts, _product_factor, max_relations = timing_probe.selected_contexts_from_source_case(source, row)
        form_keys: set[tuple[tuple[int, ...], int]] = set()
        for context in contexts:
            built = context["built"]
            components = context["components"]
            p = int_value(built.get("p"))
            order = int_value(built.get("order"))
            rho = max(rho, int_value(built.get("generic_rho_steps")))
            selected = {int_value(leaf) for leaf in context.get("selected_leaf_indices") or []}
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
            ordered_scouts = direct_witness_probe.eval_cover_probe.order_scouts(
                built["scouts"],
                cover["hits_by_scout"],
                scheduled_rows,
                str(built["scout_order"]),
            )
            scheduled_by_original = {int_value(item.get("original_trial")): item for item in scheduled_rows}
            scout_to_leaf = critical_leaf_probe.scout_leaf_map(components)
            context_x_matches = 0
            context_candidate_point_additions = 0
            for candidate_pos, scout in enumerate(ordered_scouts[:max_relations], start=1):
                scout_pos = int_value(scout.get("scout_pos"))
                hit_rows = [
                    scheduled_by_original[trial]
                    for trial in cover["hits_by_scout"].get(scout_pos, [])
                    if trial in scheduled_by_original
                ]
                if not hit_rows:
                    continue
                candidate_point = verifier.add_points(scout["left"]["point"], scout["right"]["point"], built["ainvs"], p)
                context_candidate_point_additions += 1
                terms = [int_value(index) for index in scout.get("unsigned_indices") or []]
                terms_lbl = label(terms)
                support_lbl = support_label(terms)
                for hit_row in hit_rows:
                    context_x_matches += 1
                    if candidate_point != hit_row["point"]:
                        continue
                    relation = {"a": int_value(hit_row.get("a")), "b": int_value(hit_row.get("b")), "indices": terms}
                    relation_terms = verifier.relation_terms(relation, built["challenge"], built["ainvs"], p)
                    if relation_terms is None:
                        continue
                    coeffs, rhs = verifier.relation_linear_form(relation, relation_terms, built["challenge"], order)
                    form_key = (tuple(int_value(coeff) % order for coeff in coeffs), int_value(rhs) % order)
                    is_duplicate = form_key in form_keys
                    form_keys.add(form_key)
                    row_key = str(context.get("row_key") or "")
                    point_matches.append(
                        {
                            "candidate_pos": candidate_pos,
                            "factor_support_label": support_lbl,
                            "form_duplicate": is_duplicate,
                            "leaf_index": int_value(scout_to_leaf.get(scout_pos)),
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
                    if preform_accepts(point_matches, accept_rule):
                        stopped = True
                        break
                if stopped:
                    break
            total_x_matches += context_x_matches
            total_candidate_point_additions += context_candidate_point_additions
            costs = direct_witness_probe.preassociation_filter_probe.prefilter_costs(
                built,
                len(selected),
                int_value(cover.get("selected_hit_root_values")),
                context_x_matches,
                int_value(getattr(context["local_args"], "row_factor", 1), 1),
                int_value(getattr(context["local_args"], "product_factor", 1), 1),
            )
            total_ops += int_value(costs.get("preassociation_filter_ops"))
            # Candidate point additions are a cheap extra operation not included
            # in the existing preassociation ledger proxy.
            total_ops += context_candidate_point_additions
            if stopped:
                break
    except Exception as exc:  # noqa: BLE001 - preserve research replay failures.
        errors.append({"error": "preform_scan_failed", "message": str(exc)})
    summary = point_match_summary(point_matches)
    return (
        {
            **summary,
            "accepted": stopped,
            "accept_rule": accept_rule,
            "candidate_point_additions": total_candidate_point_additions,
            "point_matches": point_matches,
            "preform_ops": total_ops,
            "preform_ops_over_rho": ratio(total_ops, rho),
            "rho": rho,
            "x_match_count": total_x_matches,
        },
        errors,
    )


def collect_group(
    source_path: Path,
    source: dict[str, Any],
    rows: list[dict[str, Any]],
    rank_labels: dict[tuple[str, str, int, str, int, tuple[str, ...]], dict[str, Any]],
    source_case_charge_ops: int,
    accept_rule: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    attempts: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for row in rows:
        scan, scan_errors = scan_preform_case(source, row, accept_rule)
        key = case_key(source_path, row)
        score = rank_labels.get(key, {})
        charged_ops = source_case_charge_ops + int_value(scan.get("preform_ops"))
        rho = int_value(scan.get("rho"))
        attempt = {
            **scan,
            "charged_ops": charged_ops,
            "charged_ops_over_rho": ratio(charged_ops, rho),
            "public_key_verified": bool(row.get("public_key_verified")),
            "rank": int_value(row.get("rank")),
            "rank_gain": int_value(score.get("rank_gain")) if score else None,
            "row_keys": row.get("row_keys") or [],
            "row_selector": row.get("row_selector"),
            "selected_leaf_count": int_value(row.get("selected_leaf_count")),
            "selected_row_count": int_value(row.get("selected_row_count")),
            "selector": row.get("selector"),
            "source_case_charge_ops": source_case_charge_ops,
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
    total_charged = sum(int_value(attempt.get("charged_ops")) for attempt in attempts)
    rho_values = [int_value(attempt.get("rho")) for attempt in attempts if int_value(attempt.get("rho")) > 0]
    rho = max(rho_values) if rho_values else 0
    stop = attempts[-1] if attempts and attempts[-1].get("accepted") else None
    return (
        {
            "accept_rule": accept_rule,
            "attempt_count": len(attempts),
            "attempts": attempts,
            "charged_ops": total_charged,
            "charged_ops_over_rho": ratio(total_charged, rho),
            "has_accepted_stop": stop is not None,
            "has_rank_gain_stop": bool(stop and int_value(stop.get("rank_gain")) > 0),
            "rho": rho,
            "source_path": str(source_path),
            "stop": stop,
            "window": f"{window[0]}_{window[1]}" if window else "",
            "window_start": window[0] if window else int_value(attempts[0].get("transfer_index")) if attempts else 0,
        },
        errors,
    )


def summarize(groups: list[dict[str, Any]]) -> dict[str, Any]:
    accepted_groups = [group for group in groups if group.get("has_accepted_stop")]
    rank_groups = [group for group in groups if group.get("has_rank_gain_stop")]
    charged = sum(int_value(group.get("charged_ops")) for group in groups)
    rho = max([int_value(group.get("rho")) for group in groups if int_value(group.get("rho")) > 0] or [0])
    return {
        "accepted_stop_count": len(accepted_groups),
        "attempt_count": sum(int_value(group.get("attempt_count")) for group in groups),
        "charged_ops": charged,
        "charged_ops_over_rho": ratio(charged, rho),
        "cost_per_accepted_stop_over_rho": ratio(charged, rho * len(accepted_groups)) if accepted_groups and rho else None,
        "cost_per_rank_gain_stop_over_rho": ratio(charged, rho * len(rank_groups)) if rank_groups and rho else None,
        "group_count": len(groups),
        "rank_gain_stop_count": len(rank_groups),
    }


def split_groups(groups: list[dict[str, Any]], calibration_end: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return (
        [group for group in groups if int_value(group.get("window_start")) <= calibration_end],
        [group for group in groups if int_value(group.get("window_start")) > calibration_end],
    )


def baseline_comparison(baseline: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    baseline_summary = baseline.get("summary") if isinstance(baseline.get("summary"), dict) else {}
    for split_name in ("calibration", "validation"):
        old = baseline_summary.get(split_name) if isinstance(baseline_summary.get(split_name), dict) else {}
        new = current.get(split_name) if isinstance(current.get(split_name), dict) else {}
        old_cost = old.get("cost_per_rank_gain_stop_over_rho")
        new_cost = new.get("cost_per_rank_gain_stop_over_rho")
        out[split_name] = {
            "baseline_cost_per_rank_gain_stop_over_rho": old_cost,
            "baseline_rank_gain_stop_count": old.get("rank_gain_stop_count"),
            "current_cost_per_rank_gain_stop_over_rho": new_cost,
            "current_rank_gain_stop_count": new.get("rank_gain_stop_count"),
            "cost_ratio_current_over_baseline": ratio(new_cost, old_cost) if new_cost is not None and old_cost not in (None, 0) else None,
        }
    return out


def claim_status(validation_summary: dict[str, Any]) -> str:
    rank_hits = int_value(validation_summary.get("rank_gain_stop_count"))
    cost = validation_summary.get("cost_per_rank_gain_stop_over_rho")
    if rank_hits <= 0:
        return "SCOUT_POS7_PREFORM_SOURCE_CHARGED_MISSES_VALIDATION_RANK_GAIN"
    if cost is not None and float(cost) < 1.0:
        return "SCOUT_POS7_PREFORM_SOURCE_CHARGED_BELOW_RHO"
    return "SCOUT_POS7_PREFORM_SOURCE_CHARGED_ABOVE_RHO"


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
    parser.add_argument("--calibration-end", type=int, default=3831)
    parser.add_argument("--source-case-charge-ops", type=int, default=1)
    parser.add_argument(
        "--accept-rule",
        choices=["point_match_scout7_double_11111515", "point_match_scout_pos_multiset_7_7"],
        default="point_match_scout_pos_multiset_7_7",
    )
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
        group, group_errors = collect_group(
            source_path,
            source,
            rows,
            rank_labels,
            args.source_case_charge_ops,
            args.accept_rule,
        )
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
        "baseline_comparison": baseline_comparison(baseline, current_summary) if baseline else {},
        "claim_status": claim_status(current_summary["validation"]),
        "created_at": now_iso(),
        "errors": errors,
        "groups": groups,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: preform detection uses candidate-point equality and unsigned terms before full public-key verification.",
            "SOURCE-CHARGED PREFORM SCAN: no-hit source cases are charged; this is not yet a lower-level shared-product kernel.",
            "A below-rho result here is a work order for a true event-targeting collector, not a deployed-curve ECDLP break.",
        ],
        "parameters": {
            "accept_rule": args.accept_rule,
            "calibration_end": args.calibration_end,
            "min_transfer": args.min_transfer,
            "selector": args.selector,
            "source_case_charge_ops": args.source_case_charge_ops,
            "source_list_from_baseline": bool(args.source_list_from_baseline),
            "target": args.target,
            "top_k": args.top_k,
        },
        "rows_by_source_count": rows_by_source_count,
        "schema": "ecdlp.low_term_total2_scout_pos7_preform_source_charged_collector.v1",
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
