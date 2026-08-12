#!/usr/bin/env python3
"""P1010 stress-row completion audit for expanded p231 sources."""

from __future__ import annotations

import argparse
import itertools
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005
import low_term_total2_p1007_p231_expanded_source_policy_compatibility as p1007
import low_term_total2_p1008_p231_expanded_rule_early_stop_11984 as p1008
import low_term_total2_p1009_p231_expanded_rule_family_fallback_11984 as p1009


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1010_p231_stress_row_completion_11992.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1010_p231_stress_row_completion_11992_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1010_p231_stress_row_completion_11992.v1"
DEFAULT_TARGET = "22050.cf1@11731"
TRAIN_WINDOWS = p1007.TRAIN_WINDOWS
CALIBRATION_WINDOWS = [p1007.CONTROL_WINDOW, p1007.VALIDATION_WINDOW, p1008.VALIDATION_WINDOW]
VALIDATION_WINDOW = "11992_11999"
MAX_REPRESENTATIVES = 8
MAX_UNION_SIZE = 3
MAX_PRIOR_SELECTED = 90
MAX_CALIBRATION_SELECTED = 24


RulePredicate = Callable[[dict[str, Any]], bool]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p1009.int_value(value, default)


def features(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("features") or {}


def source_case(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("source_case") or {}


def selector(row: dict[str, Any]) -> str:
    return str(features(row).get("leaf_selector"))


def leaf_tuple(row: dict[str, Any]) -> tuple[int, ...]:
    return tuple(int_value(value) for value in features(row).get("unique_leaf_indices") or [])


def leaf_set(row: dict[str, Any]) -> set[int]:
    return set(leaf_tuple(row))


def source_ops(row: dict[str, Any]) -> float:
    return float(source_case(row).get("source_ops_over_rho") or 0.0)


def transfer_index(row: dict[str, Any]) -> int:
    return int_value(source_case(row).get("transfer_index"))


def transfer_offset(row: dict[str, Any]) -> int:
    return transfer_index(row) % 8


def source_stress_positive(row: dict[str, Any]) -> bool:
    case = source_case(row)
    return bool(case.get("source_public_key_verified")) and source_ops(row) < 1.0


def selected_case_summary(row: dict[str, Any]) -> dict[str, Any]:
    f = features(row)
    c = source_case(row)
    return {
        "case_id": row.get("case_id"),
        "label_positive": row.get("label_positive"),
        "leaf_selector": f.get("leaf_selector"),
        "source_ops_over_rho": c.get("source_ops_over_rho"),
        "source_public_key_verified": c.get("source_public_key_verified"),
        "source_rank": c.get("source_rank"),
        "source_stress_positive": source_stress_positive(row),
        "top_k": f.get("top_k"),
        "transfer_index": c.get("transfer_index"),
        "transfer_offset": transfer_offset(row),
        "unique_leaf_indices": f.get("unique_leaf_indices"),
        "window": row.get("window"),
    }


def build_window_rows(windows: list[str], targets: str, min_source_rank: int) -> tuple[dict[str, list[dict[str, Any]]], dict[str, bool]]:
    return p1009.build_window_rows(windows, targets, min_source_rank)


def flatten(by_window: dict[str, list[dict[str, Any]]], windows: list[str]) -> list[dict[str, Any]]:
    return p1009.flatten(by_window, windows)


def safe_ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    return p1007.safe_ratio(numerator, denominator)


def add_rule(rules: list[dict[str, Any]], name: str, description: str, predicate: RulePredicate) -> None:
    if any(rule["name"] == name for rule in rules):
        return
    rules.append({"description": description, "members": [name], "name": name, "predicate": predicate})


def offset_rules(prior_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    stress_rows = [row for row in prior_rows if source_stress_positive(row)]
    offsets = sorted({transfer_offset(row) for row in stress_rows})
    selector_names = sorted({selector(row) for row in stress_rows})
    top_ks = sorted({int_value(features(row).get("top_k")) for row in stress_rows})
    tuples = sorted({leaf_tuple(row) for row in stress_rows})
    leaves = sorted({leaf for row in stress_rows for leaf in leaf_tuple(row)})
    rules: list[dict[str, Any]] = []
    for offset in offsets:
        add_rule(
            rules,
            f"transfer_offset={offset}",
            f"transfer index modulo 8 == {offset}",
            lambda row, offset=offset: transfer_offset(row) == offset,
        )
        for top_k in top_ks:
            add_rule(
                rules,
                f"transfer_offset={offset} AND topk={top_k}",
                f"transfer offset == {offset} and top_k == {top_k}",
                lambda row, offset=offset, top_k=top_k: transfer_offset(row) == offset
                and int_value(features(row).get("top_k")) == top_k,
            )
        for selector_name in selector_names:
            add_rule(
                rules,
                f"transfer_offset={offset} AND selector={selector_name}",
                f"transfer offset == {offset} and leaf_selector == {selector_name}",
                lambda row, offset=offset, selector_name=selector_name: transfer_offset(row) == offset
                and selector(row) == selector_name,
            )
        for item in tuples:
            add_rule(
                rules,
                f"transfer_offset={offset} AND leaf_tuple={list(item)}",
                f"transfer offset == {offset} and unique_leaf_indices == {list(item)}",
                lambda row, offset=offset, item=item: transfer_offset(row) == offset and leaf_tuple(row) == item,
            )
        for leaf in leaves:
            add_rule(
                rules,
                f"transfer_offset={offset} AND contains_leaf={leaf}",
                f"transfer offset == {offset} and unique_leaf_indices contains {leaf}",
                lambda row, offset=offset, leaf=leaf: transfer_offset(row) == offset and leaf in leaf_set(row),
            )
    for selector_name in selector_names:
        for top_k in top_ks:
            add_rule(
                rules,
                f"selector={selector_name} AND topk={top_k}",
                f"leaf_selector == {selector_name} and top_k == {top_k}",
                lambda row, selector_name=selector_name, top_k=top_k: selector(row) == selector_name
                and int_value(features(row).get("top_k")) == top_k,
            )
    for item in tuples:
        for top_k in top_ks:
            add_rule(
                rules,
                f"leaf_tuple={list(item)} AND topk={top_k}",
                f"unique_leaf_indices == {list(item)} and top_k == {top_k}",
                lambda row, item=item, top_k=top_k: leaf_tuple(row) == item
                and int_value(features(row).get("top_k")) == top_k,
            )
    return rules


def primitive_rules(train_rows: list[dict[str, Any]], prior_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rules = p1007.candidate_rules(train_rows) + p1009.curated_rules(train_rows) + offset_rules(prior_rows)
    unique: dict[str, dict[str, Any]] = {}
    for rule in rules:
        unique.setdefault(rule["name"], rule)
    return list(unique.values())


def stress_score(rows: list[dict[str, Any]], predicate: RulePredicate) -> dict[str, Any]:
    stress_rows = [row for row in rows if source_stress_positive(row)]
    selected = [row for row in rows if predicate(row)]
    selected_stress = [row for row in selected if source_stress_positive(row)]
    selected_ops = sum(source_ops(row) for row in selected)
    return {
        "case_count": len(rows),
        "precision": safe_ratio(len(selected_stress), len(selected)),
        "recall": safe_ratio(len(selected_stress), len(stress_rows)),
        "selected_count": len(selected),
        "selected_direct_sum_ops_over_rho": round(selected_ops, 8),
        "selected_stress_positive_count": len(selected_stress),
        "stress_positive_count": len(stress_rows),
        "useful_amortized_ops_over_rho": safe_ratio(selected_ops, len(selected_stress)),
    }


def selected_signature(rows: list[dict[str, Any]], predicate: RulePredicate) -> tuple[str, ...]:
    return tuple(sorted(str(row.get("case_id")) for row in rows if predicate(row)))


def useful_score(value: Any) -> float:
    return float(value) if value is not None else 10**9


def rank_primitives(
    rules: list[dict[str, Any]],
    train_rows: list[dict[str, Any]],
    calibration_rows_by_window: dict[str, list[dict[str, Any]]],
    prior_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    seen_signatures: set[tuple[str, ...]] = set()
    for rule in rules:
        signature = selected_signature(prior_rows, rule["predicate"])
        if not signature or signature in seen_signatures:
            continue
        seen_signatures.add(signature)
        train = stress_score(train_rows, rule["predicate"])
        calibrations = {window: stress_score(rows, rule["predicate"]) for window, rows in calibration_rows_by_window.items()}
        selected_prior_count = int_value(train.get("selected_count")) + sum(
            int_value(row.get("selected_count")) for row in calibrations.values()
        )
        if selected_prior_count > MAX_PRIOR_SELECTED:
            continue
        if any(int_value(row.get("selected_count")) > MAX_CALIBRATION_SELECTED for row in calibrations.values()):
            continue
        if int_value(train.get("selected_stress_positive_count")) == 0:
            continue
        latest_calibration = calibrations.get(p1008.VALIDATION_WINDOW) or {}
        calibration_hit_lanes = sum(1 for row in calibrations.values() if int_value(row.get("selected_stress_positive_count")) > 0)
        stress_values = [useful_score(train.get("useful_amortized_ops_over_rho"))] + [
            useful_score(row.get("useful_amortized_ops_over_rho")) for row in calibrations.values()
        ]
        scored.append(
            {
                "calibration_hit_lanes": calibration_hit_lanes,
                "calibrations": calibrations,
                "description": rule["description"],
                "latest_calibration_stress_hits": int_value(latest_calibration.get("selected_stress_positive_count")),
                "name": rule["name"],
                "predicate": rule["predicate"],
                "selected_prior_count": selected_prior_count,
                "train": train,
                "useful_mean": round(sum(stress_values) / len(stress_values), 8),
            }
        )
    scored.sort(
        key=lambda row: (
            -int_value(row.get("latest_calibration_stress_hits")),
            -int_value(row.get("calibration_hit_lanes")),
            -float(row["train"].get("precision") or 0.0),
            useful_score(row.get("useful_mean")),
            -int_value(row["train"].get("selected_stress_positive_count")),
            int_value(row.get("selected_prior_count")),
            str(row.get("name")),
        )
    )
    return scored


def union_candidate(parts: list[dict[str, Any]]) -> dict[str, Any]:
    names = [str(part["name"]) for part in parts]
    predicates = [part["predicate"] for part in parts]

    def predicate(row: dict[str, Any], predicates: list[RulePredicate] = predicates) -> bool:
        return any(item(row) for item in predicates)

    return {
        "description": " OR ".join(str(part["description"]) for part in parts),
        "members": names,
        "name": " UNION ".join(names),
        "predicate": predicate,
    }


def family_candidates(scored_primitives: list[dict[str, Any]]) -> list[dict[str, Any]]:
    representatives = scored_primitives[:MAX_REPRESENTATIVES]
    candidates: list[dict[str, Any]] = [
        {
            "description": row["description"],
            "members": [row["name"]],
            "name": row["name"],
            "predicate": row["predicate"],
        }
        for row in representatives
    ]
    for size in range(2, min(MAX_UNION_SIZE, len(representatives)) + 1):
        candidates.append(union_candidate(representatives[:size]))
    for parts in itertools.combinations(representatives[:5], 2):
        candidates.append(union_candidate(list(parts)))
    unique: dict[tuple[str, ...], dict[str, Any]] = {}
    for candidate in candidates:
        unique.setdefault(tuple(candidate["members"]), candidate)
    return list(unique.values())


def source_only_family_score(
    candidate: dict[str, Any],
    train_rows: list[dict[str, Any]],
    calibration_rows_by_window: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    train = stress_score(train_rows, candidate["predicate"])
    calibrations = {window: stress_score(rows, candidate["predicate"]) for window, rows in calibration_rows_by_window.items()}
    selected_prior_count = int_value(train.get("selected_count")) + sum(
        int_value(row.get("selected_count")) for row in calibrations.values()
    )
    calibration_hit_lanes = sum(1 for row in calibrations.values() if int_value(row.get("selected_stress_positive_count")) > 0)
    latest = calibrations.get(p1008.VALIDATION_WINDOW) or {}
    values = [useful_score(train.get("useful_amortized_ops_over_rho"))] + [
        useful_score(row.get("useful_amortized_ops_over_rho")) for row in calibrations.values()
    ]
    return {
        "candidate": {
            "description": candidate["description"],
            "member_count": len(candidate["members"]),
            "members": candidate["members"],
            "name": candidate["name"],
        },
        "calibration_hit_lanes": calibration_hit_lanes,
        "calibrations": calibrations,
        "latest_calibration_stress_hits": int_value(latest.get("selected_stress_positive_count")),
        "selected_prior_count": selected_prior_count,
        "train": train,
        "useful_mean": round(sum(values) / len(values), 8),
    }


def choose_family(scored_families: list[dict[str, Any]]) -> dict[str, Any]:
    viable = [
        row
        for row in scored_families
        if int_value(row.get("latest_calibration_stress_hits")) > 0
        and int_value(row.get("calibration_hit_lanes")) >= 2
        and int_value(row.get("selected_prior_count")) <= MAX_PRIOR_SELECTED
        and all(int_value(score.get("selected_count")) <= MAX_CALIBRATION_SELECTED for score in row["calibrations"].values())
    ]
    pool = viable or scored_families
    pool.sort(
        key=lambda row: (
            -int_value(row.get("latest_calibration_stress_hits")),
            -int_value(row.get("calibration_hit_lanes")),
            -float(row["train"].get("precision") or 0.0),
            useful_score(row.get("useful_mean")),
            int_value(row.get("selected_prior_count")),
            int_value(row["candidate"].get("member_count")),
            str(row["candidate"].get("name")),
        )
    )
    return pool[0]


def lane_record(name: str, rows: list[dict[str, Any]], candidate: dict[str, Any], baseline_rank: int) -> dict[str, Any]:
    selected = [row for row in rows if candidate["predicate"](row)]
    analysis, groups = p1005.scalar_valid_groups(
        selected,
        {"lane": name, "rule_family": candidate["name"], "rule_members": candidate["members"]},
        baseline_rank,
    )
    return {
        "analysis_summary": analysis.get("summary"),
        "groups": groups,
        "metadata": {"lane": name, "rule_family": candidate["name"], "rule_members": candidate["members"]},
        "scalar_valid_groups": [p1005.compact_group(group) for group in groups[:12]],
        "selected": selected,
        "selected_cases": [selected_case_summary(row) for row in selected[:40]],
        "stress_selection": stress_score(rows, candidate["predicate"]),
    }


def first_hit(selected: list[dict[str, Any]], groups: list[dict[str, Any]], order: dict[str, Any]) -> dict[str, Any]:
    return p1008.first_hit_summary(selected, groups, order)


def choose_order(lanes: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    return p1009.choose_order(lanes)


def trim_lane(lane: dict[str, Any], order: dict[str, Any] | None = None) -> dict[str, Any]:
    out = {key: value for key, value in lane.items() if key not in {"groups", "selected"}}
    if order is not None:
        out["first_hit_chosen_order"] = first_hit(lane["selected"], lane["groups"], order)
    return out


def determine_claim(
    latest_calibration_stress_hits: int,
    calibration_first_hits: list[dict[str, Any]],
    validation: dict[str, Any],
    validation_first: dict[str, Any],
) -> str:
    if latest_calibration_stress_hits <= 0:
        return "NEGATIVE_RESULT_P1010_LATEST_CALIBRATION_STRESS_MISS"
    if not any(hit.get("first_scalar_valid_group_below_rho") for hit in calibration_first_hits):
        return "NEGATIVE_RESULT_P1010_SCALAR_VALID_POSITIVE_CONTROL_FAILURE"
    summary = validation.get("analysis_summary") or {}
    stress = validation.get("stress_selection") or {}
    if int_value(summary.get("selected_count")) == 0:
        return "NEGATIVE_RESULT_P1010_STRESS_RULE_SELECTS_NO_HOLDOUT_ROWS"
    if int_value(stress.get("selected_stress_positive_count")) == 0:
        return "NEGATIVE_RESULT_P1010_STRESS_RULE_NO_HOLDOUT_STRESS_POSITIVE"
    if int_value(summary.get("context_safe_scalar_valid_group_count")) == 0:
        return "NEGATIVE_RESULT_P1010_STRESS_RULE_NO_HOLDOUT_SCALAR_VALID_GROUP"
    first = validation_first.get("first_scalar_valid_group")
    if first and float(first.get("charged_ops_over_rho") or 10**9) < 1.0:
        return "P1010_STRESS_ROW_COMPLETION_EARLY_STOP_BELOW_RHO"
    if first:
        return "NEGATIVE_RESULT_P1010_STRESS_ROW_COMPLETION_ABOVE_RHO"
    return "NEGATIVE_RESULT_P1010_STRESS_ROW_COMPLETION_NO_ORDER_HIT"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    windows = [*TRAIN_WINDOWS, *CALIBRATION_WINDOWS, VALIDATION_WINDOW]
    by_window, exists = build_window_rows(windows, args.targets, args.min_source_rank)
    train_rows = flatten(by_window, TRAIN_WINDOWS)
    calibration_rows_by_window = {window: by_window[window] for window in CALIBRATION_WINDOWS}
    prior_rows = [*train_rows, *flatten(by_window, CALIBRATION_WINDOWS)]
    primitives = primitive_rules(train_rows, prior_rows)
    scored_primitives = rank_primitives(primitives, train_rows, calibration_rows_by_window, prior_rows)
    candidates = family_candidates(scored_primitives)
    source_family_scores = [
        source_only_family_score(candidate, train_rows, calibration_rows_by_window)
        for candidate in candidates
    ]
    chosen_score = choose_family(source_family_scores)
    candidate_by_name = {candidate["name"]: candidate for candidate in candidates}
    chosen_candidate = candidate_by_name[chosen_score["candidate"]["name"]]
    calibration_lanes = [
        lane_record(f"calibration_{window}", calibration_rows_by_window[window], chosen_candidate, args.baseline_rank)
        for window in CALIBRATION_WINDOWS
    ]
    chosen_order, order_scores = choose_order(calibration_lanes)
    calibration_first_hits = [first_hit(lane["selected"], lane["groups"], chosen_order) for lane in calibration_lanes]
    validation_lane = lane_record(f"validation_{VALIDATION_WINDOW}", by_window[VALIDATION_WINDOW], chosen_candidate, args.baseline_rank)
    validation_first = first_hit(validation_lane["selected"], validation_lane["groups"], chosen_order)
    all_validation_orders = [
        first_hit(validation_lane["selected"], validation_lane["groups"], order)
        for order in [*p1009.public_order_candidates(), *[order for order in p1008.order_candidates() if order.get("diagnostic")]]
    ]
    all_validation_orders.sort(
        key=lambda row: (
            not row.get("first_scalar_valid_group_below_rho"),
            (row.get("first_scalar_valid_group") or {}).get("charged_ops_over_rho", 10**9),
            row.get("order_name"),
        )
    )
    claim = determine_claim(
        int_value(chosen_score.get("latest_calibration_stress_hits")),
        calibration_first_hits,
        validation_lane,
        validation_first,
    )
    top_source_families = sorted(
        source_family_scores,
        key=lambda row: (
            -int_value(row.get("latest_calibration_stress_hits")),
            -int_value(row.get("calibration_hit_lanes")),
            -float(row["train"].get("precision") or 0.0),
            useful_score(row.get("useful_mean")),
            int_value(row.get("selected_prior_count")),
            str(row["candidate"].get("name")),
        ),
    )[:12]
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": p1005.sha256_file(Path(args.contract)),
            "script_sha256": p1005.sha256_file(Path(__file__)),
            "validation_source_sha256": p1005.sha256_file(p1007.expanded_source_path(VALIDATION_WINDOW)),
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1010_") else "NEGATIVE RESULT",
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "STRESS-LABEL BOUNDARY: source stress labels are used only on train/calibration windows for rule selection.",
            "VALIDATION BOUNDARY: validation labels and scalar-valid groups are reported only after the rule and order are fixed.",
            "CONTEXT-SAFE-GATE: groups spanning multiple public fingerprints are rejected.",
            "FULL-ALGORITHM BOUNDARY: this is not relation collection, sparse linear algebra, target descent, or cryptographic-size evidence.",
        ],
        "method": "p1010_p231_stress_row_completion_11992",
        "parameters": {
            "baseline_rank": args.baseline_rank,
            "calibration_windows": CALIBRATION_WINDOWS,
            "max_calibration_selected": MAX_CALIBRATION_SELECTED,
            "max_prior_selected": MAX_PRIOR_SELECTED,
            "max_representatives": MAX_REPRESENTATIVES,
            "max_union_size": MAX_UNION_SIZE,
            "min_source_rank": args.min_source_rank,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
            "train_windows": TRAIN_WINDOWS,
            "validation_window": VALIDATION_WINDOW,
        },
        "rule_search": {
            "candidate_family_count": len(candidates),
            "chosen_family": chosen_score["candidate"],
            "chosen_source_score": chosen_score,
            "primitive_rule_count": len(primitives),
            "representative_primitives": [
                {
                    "calibration_hit_lanes": row["calibration_hit_lanes"],
                    "calibrations": row["calibrations"],
                    "description": row["description"],
                    "latest_calibration_stress_hits": row["latest_calibration_stress_hits"],
                    "name": row["name"],
                    "selected_prior_count": row["selected_prior_count"],
                    "train": row["train"],
                    "useful_mean": row["useful_mean"],
                }
                for row in scored_primitives[:MAX_REPRESENTATIVES]
            ],
            "top_source_families": top_source_families,
        },
        "schema": SCHEMA,
        "source": {
            "calibration": {window: p1007.source_summary(window) for window in CALIBRATION_WINDOWS},
            "exists": exists,
            "validation": p1007.source_summary(VALIDATION_WINDOW),
        },
        "summary": {
            "calibration_below_rho_first_hit_count": sum(1 for hit in calibration_first_hits if hit.get("first_scalar_valid_group_below_rho")),
            "calibration_context_safe_scalar_valid_group_count": sum(
                int_value((lane.get("analysis_summary") or {}).get("context_safe_scalar_valid_group_count"))
                for lane in calibration_lanes
            ),
            "chosen_family_member_count": chosen_score["candidate"]["member_count"],
            "chosen_family_name": chosen_score["candidate"]["name"],
            "chosen_order_name": chosen_order["name"],
            "claim_status": claim,
            "latest_calibration_stress_hits": chosen_score.get("latest_calibration_stress_hits"),
            "validation_best_scalar_valid_amortized_ops_over_rho": (
                (validation_lane.get("analysis_summary") or {}).get("scalar_valid_best_amortized_ops_over_rho")
            ),
            "validation_chosen_first_charge": (validation_first.get("first_scalar_valid_group") or {}).get(
                "charged_ops_over_rho"
            ),
            "validation_context_safe_scalar_valid_group_count": (
                (validation_lane.get("analysis_summary") or {}).get("context_safe_scalar_valid_group_count")
            ),
            "validation_selected_count": (validation_lane.get("analysis_summary") or {}).get("selected_count"),
            "validation_selected_stress_positive_count": validation_lane["stress_selection"].get(
                "selected_stress_positive_count"
            ),
            "validation_total_selected_ops_over_rho": (validation_lane.get("analysis_summary") or {}).get(
                "selected_direct_sum_ops_over_rho"
            ),
        },
        "order_search": {
            "chosen_order": {
                "description": chosen_order["description"],
                "name": chosen_order["name"],
            },
            "training_scores": order_scores,
        },
        "lanes": {
            "calibration": [trim_lane(lane, chosen_order) for lane in calibration_lanes],
            "validation": {
                **trim_lane(validation_lane, chosen_order),
                "all_order_diagnostic": all_validation_orders,
            },
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-rank", type=int, default=8, help="Rank baseline for group summaries")
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P1010 contract path")
    parser.add_argument("--min-source-rank", type=int, default=2, help="Minimum source rank for source-positive labels")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--targets", default=DEFAULT_TARGET, help="Comma-separated target filter")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    print(
        "claim={claim} family_members={members} order={order} latest_cal_stress={latest_cal} "
        "calibration_below_rho_hits={cal_hits} validation_selected={validation_selected} "
        "validation_stress={validation_stress} validation_groups={validation_groups} "
        "validation_first={validation_first} out={out}".format(
            claim=payload["claim_status"],
            members=summary["chosen_family_member_count"],
            order=summary["chosen_order_name"],
            latest_cal=summary["latest_calibration_stress_hits"],
            cal_hits=summary["calibration_below_rho_first_hit_count"],
            validation_selected=summary["validation_selected_count"],
            validation_stress=summary["validation_selected_stress_positive_count"],
            validation_groups=summary["validation_context_safe_scalar_valid_group_count"],
            validation_first=summary["validation_chosen_first_charge"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
