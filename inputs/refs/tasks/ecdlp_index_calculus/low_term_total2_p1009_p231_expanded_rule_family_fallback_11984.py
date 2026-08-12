#!/usr/bin/env python3
"""P1009 rule-family fallback audit for expanded p231 sources."""

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


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1009_p231_expanded_rule_family_fallback_11984.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1009_p231_expanded_rule_family_fallback_11984_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1009_p231_expanded_rule_family_fallback_11984.v1"
DEFAULT_TARGET = "22050.cf1@11731"
TRAIN_WINDOWS = p1007.TRAIN_WINDOWS
CONTROL_WINDOWS = [p1007.CONTROL_WINDOW, p1007.VALIDATION_WINDOW]
VALIDATION_WINDOW = p1008.VALIDATION_WINDOW
MAX_UNION_SIZE = 3
MAX_REPRESENTATIVES = 5
MAX_PRIOR_SELECTED = 40


RulePredicate = Callable[[dict[str, Any]], bool]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def features(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("features") or {}


def source_case(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("source_case") or {}


def source_ops(row: dict[str, Any]) -> float:
    return float(source_case(row).get("source_ops_over_rho") or 0.0)


def leaf_tuple(row: dict[str, Any]) -> tuple[int, ...]:
    return tuple(int_value(value) for value in features(row).get("unique_leaf_indices") or [])


def leaf_set(row: dict[str, Any]) -> set[int]:
    return set(leaf_tuple(row))


def selector(row: dict[str, Any]) -> str:
    return str(features(row).get("leaf_selector"))


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
        "top_k": f.get("top_k"),
        "transfer_index": c.get("transfer_index"),
        "unique_leaf_indices": f.get("unique_leaf_indices"),
        "window": row.get("window"),
    }


def build_window_rows(windows: list[str], targets: str, min_source_rank: int) -> tuple[dict[str, list[dict[str, Any]]], dict[str, bool]]:
    p1007.install_expanded_source_paths()
    by_window: dict[str, list[dict[str, Any]]] = {}
    exists: dict[str, bool] = {}
    for window in windows:
        path = p1007.expanded_source_path(window)
        exists[window] = path.exists()
        by_window[window] = p1007.build_examples(window, targets, min_source_rank) if path.exists() else []
    return by_window, exists


def flatten(by_window: dict[str, list[dict[str, Any]]], windows: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for window in windows:
        rows.extend(by_window.get(window) or [])
    return rows


def add_rule(rules: list[dict[str, Any]], name: str, description: str, predicate: RulePredicate) -> None:
    if any(rule["name"] == name for rule in rules):
        return
    rules.append({"description": description, "members": [name], "name": name, "predicate": predicate})


def curated_rules(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rules: list[dict[str, Any]] = []
    selectors = sorted({selector(row) for row in rows})
    top_ks = sorted({int_value(features(row).get("top_k")) for row in rows})
    tuples = sorted({leaf_tuple(row) for row in rows})
    selected_tuples = {
        (8, 56, 90),
        (19, 34, 90),
        (34, 90),
        *[item for item in tuples if set(item) & {8, 19, 34, 56, 90}],
    }
    for prefix in (
        "mode_low_term_support",
        "mode_cost_low_leaf_index",
        "mode_cost_hybrid_support_monic_b",
        "mode_hybrid",
    ):
        add_rule(
            rules,
            f"selector_prefix={prefix}",
            f"leaf_selector starts with {prefix}",
            lambda row, prefix=prefix: selector(row).startswith(prefix),
        )
    for item in sorted(selected_tuples):
        add_rule(
            rules,
            f"leaf_tuple={list(item)}",
            f"unique_leaf_indices == {list(item)}",
            lambda row, item=item: leaf_tuple(row) == item,
        )
    for top_k in (4, 7, 12):
        if top_k in top_ks:
            add_rule(
                rules,
                f"topk={top_k}",
                f"top_k == {top_k}",
                lambda row, top_k=top_k: int_value(features(row).get("top_k")) == top_k,
            )
    for top_k in (4, 7, 12):
        add_rule(
            rules,
            f"selector_prefix=mode_low_term_support AND topk={top_k}",
            f"low-term-support selector and top_k == {top_k}",
            lambda row, top_k=top_k: selector(row).startswith("mode_low_term_support")
            and int_value(features(row).get("top_k")) == top_k,
        )
    for item in sorted(selected_tuples):
        add_rule(
            rules,
            f"selector_prefix=mode_low_term_support AND leaf_tuple={list(item)}",
            f"low-term-support selector and unique_leaf_indices == {list(item)}",
            lambda row, item=item: selector(row).startswith("mode_low_term_support") and leaf_tuple(row) == item,
        )
    for selector_name in selectors:
        if selector_name.startswith("mode_low_term_support"):
            for top_k in (4, 7, 12):
                add_rule(
                    rules,
                    f"selector={selector_name} AND topk={top_k}",
                    f"leaf_selector == {selector_name} and top_k == {top_k}",
                    lambda row, selector_name=selector_name, top_k=top_k: selector(row) == selector_name
                    and int_value(features(row).get("top_k")) == top_k,
                )
    for leaf in (8, 19, 34, 56, 90):
        add_rule(
            rules,
            f"contains_leaf={leaf}",
            f"unique_leaf_indices contains {leaf}",
            lambda row, leaf=leaf: leaf in leaf_set(row),
        )
    return rules


def primitive_rules(train_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rules = p1007.candidate_rules(train_rows) + curated_rules(train_rows)
    unique: dict[str, dict[str, Any]] = {}
    for rule in rules:
        unique.setdefault(rule["name"], rule)
    return list(unique.values())


def selected_signature(rows: list[dict[str, Any]], predicate: RulePredicate) -> tuple[str, ...]:
    return tuple(sorted(str(row.get("case_id")) for row in rows if predicate(row)))


def source_score(rows: list[dict[str, Any]], predicate: RulePredicate) -> dict[str, Any]:
    return p1007.score_selection(rows, predicate)


def useful_score(value: Any) -> float:
    return float(value) if value is not None else 10**9


def rank_primitives(
    rules: list[dict[str, Any]],
    train_rows: list[dict[str, Any]],
    control_rows_by_window: dict[str, list[dict[str, Any]]],
    prior_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    seen_signatures: set[tuple[str, ...]] = set()
    for rule in rules:
        signature = selected_signature(prior_rows, rule["predicate"])
        if not signature or signature in seen_signatures:
            continue
        seen_signatures.add(signature)
        train = source_score(train_rows, rule["predicate"])
        controls = {window: source_score(rows, rule["predicate"]) for window, rows in control_rows_by_window.items()}
        if int_value(train.get("selected_positive_count")) == 0:
            continue
        control_positive_lanes = sum(1 for row in controls.values() if int_value(row.get("selected_positive_count")) > 0)
        selected_prior_count = int_value(train.get("selected_count")) + sum(
            int_value(row.get("selected_count")) for row in controls.values()
        )
        if selected_prior_count > MAX_PRIOR_SELECTED:
            continue
        useful_values = [useful_score(train.get("useful_amortized_ops_over_rho"))] + [
            useful_score(row.get("useful_amortized_ops_over_rho")) for row in controls.values()
        ]
        scored.append(
            {
                "controls": controls,
                "control_positive_lanes": control_positive_lanes,
                "description": rule["description"],
                "name": rule["name"],
                "predicate": rule["predicate"],
                "selected_prior_count": selected_prior_count,
                "signature": signature,
                "train": train,
                "useful_mean": round(sum(useful_values) / len(useful_values), 8),
            }
        )
    scored.sort(
        key=lambda row: (
            -int_value(row.get("control_positive_lanes")),
            -float((row["train"].get("precision") or 0.0)),
            useful_score(row.get("useful_mean")),
            -int_value(row["train"].get("selected_positive_count")),
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
    candidates: list[dict[str, Any]] = []
    candidates.extend(
        {
            "description": item["description"],
            "members": [item["name"]],
            "name": item["name"],
            "predicate": item["predicate"],
        }
        for item in representatives
    )
    for size in range(2, min(MAX_UNION_SIZE, len(representatives)) + 1):
        candidates.append(union_candidate(representatives[:size]))
    if len(representatives) >= 3:
        for parts in itertools.combinations(representatives[:4], 2):
            candidates.append(union_candidate(list(parts)))
    unique: dict[tuple[str, ...], dict[str, Any]] = {}
    for candidate in candidates:
        key = tuple(candidate["members"])
        unique.setdefault(key, candidate)
    return list(unique.values())


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
        "source_selection": source_score(rows, candidate["predicate"]),
    }


def first_hit(selected: list[dict[str, Any]], groups: list[dict[str, Any]], order: dict[str, Any]) -> dict[str, Any]:
    return p1008.first_hit_summary(selected, groups, order)


def public_order_candidates() -> list[dict[str, Any]]:
    orders = p1008.order_candidates()
    return [order for order in orders if not order.get("diagnostic")]


def score_order(order: dict[str, Any], lanes: list[dict[str, Any]]) -> dict[str, Any]:
    hits = []
    misses = 0
    for lane in lanes:
        summary = first_hit(lane["selected"], lane["groups"], order)
        first = summary.get("first_scalar_valid_group")
        if first:
            hits.append(
                {
                    "charged_ops_over_rho": first.get("charged_ops_over_rho"),
                    "lane": lane["metadata"]["lane"],
                    "ordered_index": first.get("ordered_index"),
                }
            )
        else:
            misses += 1
    charges = [float(row["charged_ops_over_rho"]) for row in hits]
    return {
        "below_rho_hit_count": sum(1 for value in charges if value < 1.0),
        "hit_count": len(hits),
        "lane_hits": hits,
        "max_charge": max(charges) if charges else None,
        "mean_charge": round(sum(charges) / len(charges), 8) if charges else None,
        "miss_count": misses,
        "order_description": order["description"],
        "order_name": order["name"],
    }


def choose_order(lanes: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    orders = public_order_candidates()
    scored = [score_order(order, lanes) for order in orders]
    scored.sort(
        key=lambda row: (
            -int_value(row.get("below_rho_hit_count")),
            -int_value(row.get("hit_count")),
            useful_score(row.get("mean_charge")),
            useful_score(row.get("max_charge")),
            str(row.get("order_name")),
        )
    )
    by_name = {order["name"]: order for order in orders}
    return by_name[str(scored[0]["order_name"])], scored


def trim_lane(lane: dict[str, Any], order: dict[str, Any] | None = None) -> dict[str, Any]:
    out = {key: value for key, value in lane.items() if key not in {"groups", "selected"}}
    if order is not None:
        out["first_hit_chosen_order"] = first_hit(lane["selected"], lane["groups"], order)
    return out


def source_only_lane(name: str, rows: list[dict[str, Any]], candidate: dict[str, Any]) -> dict[str, Any]:
    selected = [row for row in rows if candidate["predicate"](row)]
    return {
        "metadata": {"lane": name, "rule_family": candidate["name"], "rule_members": candidate["members"]},
        "selected_cases": [selected_case_summary(row) for row in selected[:40]],
        "source_selection": source_score(rows, candidate["predicate"]),
    }


def evaluate_family(candidate: dict[str, Any], rows_by_lane: dict[str, list[dict[str, Any]]], baseline_rank: int) -> dict[str, Any]:
    train_lane = source_only_lane("train_expanded_prior", rows_by_lane["train"], candidate)
    controls = [
        lane_record(f"control_{window}", rows_by_lane[window], candidate, baseline_rank)
        for window in CONTROL_WINDOWS
    ]
    prior_lanes = controls
    chosen_order, order_scores = choose_order(prior_lanes)
    control_first_hits = [first_hit(lane["selected"], lane["groups"], chosen_order) for lane in controls]
    control_pass = all(
        bool((hit.get("first_scalar_valid_group") or {}).get("charged_ops_over_rho") is not None)
        and float((hit.get("first_scalar_valid_group") or {}).get("charged_ops_over_rho")) < 1.0
        for hit in control_first_hits
    )
    prior_first_hits = [first_hit(lane["selected"], lane["groups"], chosen_order) for lane in prior_lanes]
    charges = [
        float((hit.get("first_scalar_valid_group") or {}).get("charged_ops_over_rho"))
        for hit in prior_first_hits
        if (hit.get("first_scalar_valid_group") or {}).get("charged_ops_over_rho") is not None
    ]
    return {
        "candidate": {
            "description": candidate["description"],
            "member_count": len(candidate["members"]),
            "members": candidate["members"],
            "name": candidate["name"],
        },
        "control_below_rho_count": sum(1 for hit in control_first_hits if hit.get("first_scalar_valid_group_below_rho")),
        "control_pass": control_pass,
        "control_scalar_valid_group_count": sum(
            int_value((lane.get("analysis_summary") or {}).get("context_safe_scalar_valid_group_count"))
            for lane in controls
        ),
        "lanes": {
            "controls": [trim_lane(lane, chosen_order) for lane in controls],
            "train": train_lane,
        },
        "mean_prior_first_charge": round(sum(charges) / len(charges), 8) if charges else None,
        "order_search": {
            "chosen_order": {
                "description": chosen_order["description"],
                "name": chosen_order["name"],
            },
            "training_scores": order_scores,
        },
        "prior_below_rho_hit_count": sum(1 for hit in prior_first_hits if hit.get("first_scalar_valid_group_below_rho")),
        "prior_hit_count": len(charges),
        "prior_selected_count": int_value(train_lane["source_selection"].get("selected_count"))
        + sum(int_value((lane.get("analysis_summary") or {}).get("selected_count")) for lane in controls),
        "raw": {
            "chosen_order": chosen_order,
            "controls": controls,
            "train": train_lane,
        },
    }


def choose_family(evaluated: list[dict[str, Any]]) -> dict[str, Any]:
    union_pool = [row for row in evaluated if row["candidate"]["member_count"] > 1 and row.get("control_pass")]
    control_pool = [row for row in evaluated if row.get("control_pass")]
    pool = union_pool or control_pool or evaluated
    pool.sort(
        key=lambda row: (
            -int_value(row.get("control_below_rho_count")),
            -int_value(row.get("prior_below_rho_hit_count")),
            -int_value(row.get("prior_hit_count")),
            useful_score(row.get("mean_prior_first_charge")),
            int_value(row.get("prior_selected_count")),
            int_value(row["candidate"].get("member_count")),
            str(row["candidate"].get("name")),
        )
    )
    return pool[0]


def determine_claim(chosen: dict[str, Any], validation: dict[str, Any], validation_first: dict[str, Any]) -> str:
    if not chosen.get("control_pass"):
        return "NEGATIVE_RESULT_P1009_POSITIVE_CONTROL_FAILURE"
    summary = validation.get("analysis_summary") or {}
    if int_value(summary.get("selected_count")) == 0:
        return "NEGATIVE_RESULT_P1009_FAMILY_SELECTS_NO_HOLDOUT_ROWS"
    if int_value(summary.get("context_safe_scalar_valid_group_count")) == 0:
        return "NEGATIVE_RESULT_P1009_FAMILY_NO_HOLDOUT_SCALAR_VALID_GROUP"
    first = validation_first.get("first_scalar_valid_group")
    if first and float(first.get("charged_ops_over_rho") or 10**9) < 1.0:
        return "P1009_EXPANDED_RULE_FAMILY_EARLY_STOP_BELOW_RHO"
    if first:
        return "NEGATIVE_RESULT_P1009_EXPANDED_RULE_FAMILY_EARLY_STOP_ABOVE_RHO"
    return "NEGATIVE_RESULT_P1009_EXPANDED_RULE_FAMILY_NO_ORDER_HIT"


def remove_raw(evaluated: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in evaluated.items() if key != "raw"}


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    windows = [*TRAIN_WINDOWS, *CONTROL_WINDOWS, VALIDATION_WINDOW]
    by_window, exists = build_window_rows(windows, args.targets, args.min_source_rank)
    train_rows = flatten(by_window, TRAIN_WINDOWS)
    control_rows_by_window = {window: by_window[window] for window in CONTROL_WINDOWS}
    prior_rows = [*train_rows, *flatten(by_window, CONTROL_WINDOWS)]
    rules = primitive_rules(train_rows)
    scored_primitives = rank_primitives(rules, train_rows, control_rows_by_window, prior_rows)
    candidates = family_candidates(scored_primitives)
    rows_by_lane = {
        "train": train_rows,
        **control_rows_by_window,
    }
    evaluated = [evaluate_family(candidate, rows_by_lane, args.baseline_rank) for candidate in candidates]
    chosen = choose_family(evaluated)
    chosen_order = chosen["raw"]["chosen_order"]
    validation_candidate = {
        **chosen["candidate"],
        "predicate": next(candidate["predicate"] for candidate in candidates if candidate["name"] == chosen["candidate"]["name"]),
    }
    validation_lane = lane_record(
        f"validation_{VALIDATION_WINDOW}",
        by_window[VALIDATION_WINDOW],
        validation_candidate,
        args.baseline_rank,
    )
    validation_first = first_hit(validation_lane["selected"], validation_lane["groups"], chosen_order)
    all_validation_orders = [
        first_hit(validation_lane["selected"], validation_lane["groups"], order)
        for order in [*public_order_candidates(), *[order for order in p1008.order_candidates() if order.get("diagnostic")]]
    ]
    all_validation_orders.sort(
        key=lambda row: (
            not row.get("first_scalar_valid_group_below_rho"),
            (row.get("first_scalar_valid_group") or {}).get("charged_ops_over_rho", 10**9),
            row.get("order_name"),
        )
    )
    best_single = next(
        (row for row in evaluated if row["candidate"]["member_count"] == 1),
        None,
    )
    claim = determine_claim(chosen, validation_lane, validation_first)
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
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1009_") else "NEGATIVE RESULT",
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "RULE-FAMILY BOUNDARY: the primary family is selected from prior train/control windows, not validation labels.",
            "UNION-CAP BOUNDARY: fallback unions use at most three public predicates.",
            "CONTEXT-SAFE-GATE: groups spanning multiple public fingerprints are rejected.",
            "FULL-ALGORITHM BOUNDARY: this is not relation collection, sparse linear algebra, target descent, or cryptographic-size evidence.",
        ],
        "method": "p1009_p231_expanded_rule_family_fallback_11984",
        "parameters": {
            "baseline_rank": args.baseline_rank,
            "control_windows": CONTROL_WINDOWS,
            "max_representatives": MAX_REPRESENTATIVES,
            "max_union_size": MAX_UNION_SIZE,
            "min_source_rank": args.min_source_rank,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
            "train_windows": TRAIN_WINDOWS,
            "validation_window": VALIDATION_WINDOW,
        },
        "rule_search": {
            "candidate_family_count": len(candidates),
            "chosen_family": chosen["candidate"],
            "primitive_rule_count": len(rules),
            "representative_primitives": [
                {
                    "control_positive_lanes": row["control_positive_lanes"],
                    "controls": row["controls"],
                    "description": row["description"],
                    "name": row["name"],
                    "selected_prior_count": row["selected_prior_count"],
                    "train": row["train"],
                    "useful_mean": row["useful_mean"],
                }
                for row in scored_primitives[:MAX_REPRESENTATIVES]
            ],
            "top_prior_families": [remove_raw(row) for row in sorted(
                evaluated,
                key=lambda row: (
                    not row.get("control_pass"),
                    -int_value(row.get("control_below_rho_count")),
                    -int_value(row.get("prior_below_rho_hit_count")),
                    useful_score(row.get("mean_prior_first_charge")),
                    int_value(row.get("prior_selected_count")),
                    str(row["candidate"].get("name")),
                ),
            )[:12]],
            "best_single_prior_family": remove_raw(best_single) if best_single else None,
        },
        "schema": SCHEMA,
        "source": {
            "exists": exists,
            "validation": p1007.source_summary(VALIDATION_WINDOW),
        },
        "summary": {
            "chosen_family_member_count": chosen["candidate"]["member_count"],
            "chosen_family_name": chosen["candidate"]["name"],
            "chosen_order_name": chosen["order_search"]["chosen_order"]["name"],
            "claim_status": claim,
            "control_pass": chosen.get("control_pass"),
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
            "validation_selected_source_positive_count": (validation_lane.get("analysis_summary") or {}).get(
                "selected_source_positive_count"
            ),
            "validation_total_selected_ops_over_rho": (validation_lane.get("analysis_summary") or {}).get(
                "selected_direct_sum_ops_over_rho"
            ),
        },
        "lanes": {
            "prior_chosen_family": remove_raw(chosen),
            "validation": {
                **trim_lane(validation_lane, chosen_order),
                "all_order_diagnostic": all_validation_orders,
            },
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-rank", type=int, default=8, help="Rank baseline for group summaries")
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P1009 contract path")
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
        "claim={claim} family_members={members} order={order} control_pass={control_pass} "
        "validation_selected={validation_selected} validation_pos={validation_pos} "
        "validation_groups={validation_groups} validation_first={validation_first} out={out}".format(
            claim=payload["claim_status"],
            members=summary["chosen_family_member_count"],
            order=summary["chosen_order_name"],
            control_pass=summary["control_pass"],
            validation_selected=summary["validation_selected_count"],
            validation_pos=summary["validation_selected_source_positive_count"],
            validation_groups=summary["validation_context_safe_scalar_valid_group_count"],
            validation_first=summary["validation_chosen_first_charge"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
