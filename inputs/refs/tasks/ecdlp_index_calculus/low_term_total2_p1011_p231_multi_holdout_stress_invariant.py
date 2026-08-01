#!/usr/bin/env python3
"""P1011 multi-holdout stress-invariant audit for expanded p231 sources."""

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
import low_term_total2_p1010_p231_stress_row_completion_11992 as p1010


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1011_p231_multi_holdout_stress_invariant.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1011_p231_multi_holdout_stress_invariant_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1011_p231_multi_holdout_stress_invariant.v1"
DEFAULT_TARGET = p1010.DEFAULT_TARGET
TRAIN_WINDOWS = p1010.TRAIN_WINDOWS
CALIBRATION_WINDOWS = p1010.CALIBRATION_WINDOWS
VALIDATION_WINDOWS = ["11992_11999", "12000_12007", "12008_12015"]
MAX_REPRESENTATIVES = 10
MAX_UNION_SIZE = 3
MAX_PRIOR_SELECTED = 150
MAX_CALIBRATION_SELECTED = 32
MAX_VALIDATION_RECONSTRUCT = 48


RulePredicate = Callable[[dict[str, Any]], bool]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p1010.int_value(value, default)


def source_summary(window: str) -> dict[str, Any]:
    return p1007.source_summary(window)


def has_source_signal(summary: dict[str, Any]) -> bool:
    return int_value(summary.get("stress_row_below_rho")) > 0 or int_value(summary.get("stress_leaf_below_rho")) > 0


def selected_case_summary(row: dict[str, Any]) -> dict[str, Any]:
    return p1010.selected_case_summary(row)


def source_stress_positive(row: dict[str, Any]) -> bool:
    return p1010.source_stress_positive(row)


def stress_score(rows: list[dict[str, Any]], predicate: RulePredicate) -> dict[str, Any]:
    return p1010.stress_score(rows, predicate)


def build_window_rows(windows: list[str], targets: str, min_source_rank: int) -> tuple[dict[str, list[dict[str, Any]]], dict[str, bool]]:
    return p1010.build_window_rows(windows, targets, min_source_rank)


def flatten(by_window: dict[str, list[dict[str, Any]]], windows: list[str]) -> list[dict[str, Any]]:
    return p1010.flatten(by_window, windows)


def primitive_rules(train_rows: list[dict[str, Any]], prior_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return p1010.primitive_rules(train_rows, prior_rows)


def selected_signature(rows: list[dict[str, Any]], predicate: RulePredicate) -> tuple[str, ...]:
    return p1010.selected_signature(rows, predicate)


def useful_score(value: Any) -> float:
    return p1010.useful_score(value)


def rank_primitives(
    rules: list[dict[str, Any]],
    train_rows: list[dict[str, Any]],
    calibration_rows_by_window: dict[str, list[dict[str, Any]]],
    prior_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    seen: set[tuple[str, ...]] = set()
    for rule in rules:
        signature = selected_signature(prior_rows, rule["predicate"])
        if not signature or signature in seen:
            continue
        seen.add(signature)
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
        hit_lanes = sum(1 for row in calibrations.values() if int_value(row.get("selected_stress_positive_count")) > 0)
        if hit_lanes < 2:
            continue
        precision_values = [
            float(row.get("precision") or 0.0)
            for row in [train, *calibrations.values()]
            if row.get("precision") is not None
        ]
        useful_values = [useful_score(train.get("useful_amortized_ops_over_rho"))] + [
            useful_score(row.get("useful_amortized_ops_over_rho")) for row in calibrations.values()
        ]
        scored.append(
            {
                "calibration_hit_lanes": hit_lanes,
                "calibrations": calibrations,
                "description": rule["description"],
                "mean_precision": round(sum(precision_values) / len(precision_values), 8) if precision_values else None,
                "name": rule["name"],
                "predicate": rule["predicate"],
                "selected_prior_count": selected_prior_count,
                "train": train,
                "useful_mean": round(sum(useful_values) / len(useful_values), 8),
            }
        )
    scored.sort(
        key=lambda row: (
            -int_value(row.get("calibration_hit_lanes")),
            -float(row.get("mean_precision") or 0.0),
            useful_score(row.get("useful_mean")),
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
    for parts in itertools.combinations(representatives[:6], 2):
        candidates.append(union_candidate(list(parts)))
    unique: dict[tuple[str, ...], dict[str, Any]] = {}
    for candidate in candidates:
        unique.setdefault(tuple(candidate["members"]), candidate)
    return list(unique.values())


def source_only_score(
    candidate: dict[str, Any],
    train_rows: list[dict[str, Any]],
    calibration_rows_by_window: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    train = stress_score(train_rows, candidate["predicate"])
    calibrations = {window: stress_score(rows, candidate["predicate"]) for window, rows in calibration_rows_by_window.items()}
    selected_prior_count = int_value(train.get("selected_count")) + sum(
        int_value(row.get("selected_count")) for row in calibrations.values()
    )
    hit_lanes = sum(1 for row in calibrations.values() if int_value(row.get("selected_stress_positive_count")) > 0)
    latest = calibrations.get(p1008.VALIDATION_WINDOW) or {}
    precision_values = [
        float(row.get("precision") or 0.0)
        for row in [train, *calibrations.values()]
        if row.get("precision") is not None
    ]
    useful_values = [useful_score(train.get("useful_amortized_ops_over_rho"))] + [
        useful_score(row.get("useful_amortized_ops_over_rho")) for row in calibrations.values()
    ]
    return {
        "candidate": {
            "description": candidate["description"],
            "member_count": len(candidate["members"]),
            "members": candidate["members"],
            "name": candidate["name"],
        },
        "calibration_hit_lanes": hit_lanes,
        "calibrations": calibrations,
        "latest_calibration_stress_hits": int_value(latest.get("selected_stress_positive_count")),
        "mean_precision": round(sum(precision_values) / len(precision_values), 8) if precision_values else None,
        "selected_prior_count": selected_prior_count,
        "train": train,
        "useful_mean": round(sum(useful_values) / len(useful_values), 8),
    }


def choose_family(scores: list[dict[str, Any]]) -> dict[str, Any]:
    viable = [
        row
        for row in scores
        if int_value(row.get("calibration_hit_lanes")) >= 3
        and int_value(row.get("latest_calibration_stress_hits")) > 0
        and int_value(row.get("selected_prior_count")) <= MAX_PRIOR_SELECTED
        and all(int_value(score.get("selected_count")) <= MAX_CALIBRATION_SELECTED for score in row["calibrations"].values())
    ]
    pool = viable or scores
    pool.sort(
        key=lambda row: (
            -int_value(row.get("calibration_hit_lanes")),
            -int_value(row.get("latest_calibration_stress_hits")),
            -float(row.get("mean_precision") or 0.0),
            useful_score(row.get("useful_mean")),
            int_value(row.get("selected_prior_count")),
            int_value(row["candidate"].get("member_count")),
            str(row["candidate"].get("name")),
        )
    )
    return pool[0]


def lane_record(
    name: str,
    rows: list[dict[str, Any]],
    candidate: dict[str, Any],
    baseline_rank: int,
    allow_reconstruction: bool = True,
) -> dict[str, Any]:
    selected = [row for row in rows if candidate["predicate"](row)]
    if allow_reconstruction and len(selected) <= MAX_VALIDATION_RECONSTRUCT:
        analysis, groups = p1005.scalar_valid_groups(
            selected,
            {"lane": name, "rule_family": candidate["name"], "rule_members": candidate["members"]},
            baseline_rank,
        )
    else:
        analysis = {
            "summary": {
                "context_safe_scalar_valid_group_count": None,
                "reconstruction_skipped": True,
                "selected_count": len(selected),
                "selected_direct_sum_ops_over_rho": round(sum(p1010.source_ops(row) for row in selected), 8),
            }
        }
        groups = []
    return {
        "analysis_summary": analysis.get("summary"),
        "groups": groups,
        "metadata": {"lane": name, "rule_family": candidate["name"], "rule_members": candidate["members"]},
        "scalar_valid_groups": [p1005.compact_group(group) for group in groups[:12]],
        "selected": selected,
        "selected_cases": [selected_case_summary(row) for row in selected[:48]],
        "stress_selection": stress_score(rows, candidate["predicate"]),
    }


def first_hit(selected: list[dict[str, Any]], groups: list[dict[str, Any]], order: dict[str, Any]) -> dict[str, Any]:
    return p1008.first_hit_summary(selected, groups, order)


def choose_order(lanes: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    return p1009.choose_order(lanes)


def trim_lane(lane: dict[str, Any], order: dict[str, Any] | None = None) -> dict[str, Any]:
    out = {key: value for key, value in lane.items() if key not in {"groups", "selected"}}
    if order is not None and lane.get("groups") is not None:
        out["first_hit_chosen_order"] = first_hit(lane["selected"], lane["groups"], order)
    return out


def determine_claim(
    calibration_first_hits: list[dict[str, Any]],
    validation_lanes: list[dict[str, Any]],
    validation_first_hits: list[dict[str, Any]],
    validation_source_signals: dict[str, bool],
) -> str:
    if not any(hit.get("first_scalar_valid_group_below_rho") for hit in calibration_first_hits):
        return "NEGATIVE_RESULT_P1011_SCALAR_VALID_POSITIVE_CONTROL_FAILURE"
    signal_lanes = [
        lane
        for lane in validation_lanes
        if validation_source_signals.get(str(lane["metadata"]["lane"]).replace("validation_", ""), False)
    ]
    if not signal_lanes:
        return "NEGATIVE_RESULT_P1011_NO_VALIDATION_SOURCE_SIGNAL"
    selected_signal_lanes = [
        lane
        for lane in signal_lanes
        if int_value((lane.get("stress_selection") or {}).get("selected_count")) > 0
    ]
    stress_hit_lanes = [
        lane
        for lane in signal_lanes
        if int_value((lane.get("stress_selection") or {}).get("selected_stress_positive_count")) > 0
    ]
    below_rho_hits = [
        hit
        for lane, hit in zip(validation_lanes, validation_first_hits)
        if validation_source_signals.get(str(lane["metadata"]["lane"]).replace("validation_", ""), False)
        and hit.get("first_scalar_valid_group_below_rho")
    ]
    if len(selected_signal_lanes) == 0:
        return "NEGATIVE_RESULT_P1011_INVARIANT_ABSENT_ON_SOURCE_SIGNAL_HOLDOUTS"
    if len(stress_hit_lanes) == 0:
        return "NEGATIVE_RESULT_P1011_INVARIANT_NO_SOURCE_STRESS_HITS"
    if len(stress_hit_lanes) < 2:
        return "NEGATIVE_RESULT_P1011_INVARIANT_NOT_MULTI_HOLDOUT_STABLE"
    if below_rho_hits:
        return "P1011_MULTI_HOLDOUT_STRESS_INVARIANT_BELOW_RHO"
    return "NEGATIVE_RESULT_P1011_SOURCE_STABLE_BUT_NO_BELOW_RHO_SCALAR_VALID"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    windows = [*TRAIN_WINDOWS, *CALIBRATION_WINDOWS, *VALIDATION_WINDOWS]
    by_window, exists = build_window_rows(windows, args.targets, args.min_source_rank)
    train_rows = flatten(by_window, TRAIN_WINDOWS)
    calibration_rows_by_window = {window: by_window[window] for window in CALIBRATION_WINDOWS}
    prior_rows = [*train_rows, *flatten(by_window, CALIBRATION_WINDOWS)]
    primitives = primitive_rules(train_rows, prior_rows)
    scored_primitives = rank_primitives(primitives, train_rows, calibration_rows_by_window, prior_rows)
    candidates = family_candidates(scored_primitives)
    source_scores = [source_only_score(candidate, train_rows, calibration_rows_by_window) for candidate in candidates]
    chosen_score = choose_family(source_scores)
    candidate_by_name = {candidate["name"]: candidate for candidate in candidates}
    chosen_candidate = candidate_by_name[chosen_score["candidate"]["name"]]
    calibration_lanes = [
        lane_record(f"calibration_{window}", calibration_rows_by_window[window], chosen_candidate, args.baseline_rank)
        for window in CALIBRATION_WINDOWS
    ]
    chosen_order, order_scores = choose_order(calibration_lanes)
    calibration_first_hits = [first_hit(lane["selected"], lane["groups"], chosen_order) for lane in calibration_lanes]
    validation_summaries = {window: source_summary(window) for window in VALIDATION_WINDOWS}
    validation_source_signals = {window: has_source_signal(validation_summaries[window]) for window in VALIDATION_WINDOWS}
    validation_lanes = [
        lane_record(
            f"validation_{window}",
            by_window[window],
            chosen_candidate,
            args.baseline_rank,
            allow_reconstruction=validation_source_signals[window],
        )
        for window in VALIDATION_WINDOWS
    ]
    validation_first_hits = [first_hit(lane["selected"], lane["groups"], chosen_order) for lane in validation_lanes]
    claim = determine_claim(calibration_first_hits, validation_lanes, validation_first_hits, validation_source_signals)
    signal_windows = [window for window in VALIDATION_WINDOWS if validation_source_signals[window]]
    selected_signal_windows = [
        lane["metadata"]["lane"].replace("validation_", "")
        for lane in validation_lanes
        if validation_source_signals.get(lane["metadata"]["lane"].replace("validation_", ""), False)
        and int_value((lane.get("stress_selection") or {}).get("selected_count")) > 0
    ]
    stress_hit_signal_windows = [
        lane["metadata"]["lane"].replace("validation_", "")
        for lane in validation_lanes
        if validation_source_signals.get(lane["metadata"]["lane"].replace("validation_", ""), False)
        and int_value((lane.get("stress_selection") or {}).get("selected_stress_positive_count")) > 0
    ]
    below_rho_validation_windows = [
        lane["metadata"]["lane"].replace("validation_", "")
        for lane, hit in zip(validation_lanes, validation_first_hits)
        if hit.get("first_scalar_valid_group_below_rho")
    ]
    top_source_families = sorted(
        source_scores,
        key=lambda row: (
            -int_value(row.get("calibration_hit_lanes")),
            -int_value(row.get("latest_calibration_stress_hits")),
            -float(row.get("mean_precision") or 0.0),
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
            "validation_source_sha256": {
                window: p1005.sha256_file(p1007.expanded_source_path(window)) for window in VALIDATION_WINDOWS
            },
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1011_") else "NEGATIVE RESULT",
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "SOURCE-SIGNAL BOUNDARY: validation windows without below-rho source signal are separated from assembly failures.",
            "VALIDATION BOUNDARY: validation stress labels and scalar-valid groups are not used for choosing the rule or order.",
            "CONTEXT-SAFE-GATE: groups spanning multiple public fingerprints are rejected.",
            "FULL-ALGORITHM BOUNDARY: this is not relation collection, sparse linear algebra, target descent, or cryptographic-size evidence.",
        ],
        "method": "p1011_p231_multi_holdout_stress_invariant",
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
            "validation_windows": VALIDATION_WINDOWS,
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
                    "mean_precision": row["mean_precision"],
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
            "calibration": {window: source_summary(window) for window in CALIBRATION_WINDOWS},
            "exists": exists,
            "validation": validation_summaries,
            "validation_source_signals": validation_source_signals,
        },
        "summary": {
            "below_rho_validation_windows": below_rho_validation_windows,
            "calibration_below_rho_first_hit_count": sum(1 for hit in calibration_first_hits if hit.get("first_scalar_valid_group_below_rho")),
            "calibration_context_safe_scalar_valid_group_count": sum(
                int_value((lane.get("analysis_summary") or {}).get("context_safe_scalar_valid_group_count"))
                for lane in calibration_lanes
            ),
            "chosen_family_member_count": chosen_score["candidate"]["member_count"],
            "chosen_family_name": chosen_score["candidate"]["name"],
            "chosen_order_name": chosen_order["name"],
            "claim_status": claim,
            "selected_signal_windows": selected_signal_windows,
            "signal_window_count": len(signal_windows),
            "signal_windows": signal_windows,
            "stress_hit_signal_windows": stress_hit_signal_windows,
            "validation_window_count": len(VALIDATION_WINDOWS),
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
            "validation": [trim_lane(lane, chosen_order) for lane in validation_lanes],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-rank", type=int, default=8, help="Rank baseline for group summaries")
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P1011 contract path")
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
        "claim={claim} family_members={members} order={order} signal_windows={signal_windows} "
        "selected_signal_windows={selected_signal_windows} stress_hit_signal_windows={stress_hit_signal_windows} "
        "below_rho_validation_windows={below_rho_validation_windows} out={out}".format(
            claim=payload["claim_status"],
            members=summary["chosen_family_member_count"],
            order=summary["chosen_order_name"],
            signal_windows=",".join(summary["signal_windows"]),
            selected_signal_windows=",".join(summary["selected_signal_windows"]),
            stress_hit_signal_windows=",".join(summary["stress_hit_signal_windows"]),
            below_rho_validation_windows=",".join(summary["below_rho_validation_windows"]),
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
