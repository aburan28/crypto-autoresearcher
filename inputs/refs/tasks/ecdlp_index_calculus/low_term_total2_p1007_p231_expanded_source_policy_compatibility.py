#!/usr/bin/env python3
"""P1007 source-policy compatibility audit for expanded p231 sources."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Callable
from pathlib import Path
from typing import Any

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1007_p231_expanded_source_policy_compatibility.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1007_p231_expanded_source_policy_compatibility_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1007_p231_expanded_source_policy_compatibility.v1"
DEFAULT_TARGET = "22050.cf1@11731"
TRAIN_WINDOWS = [
    "11800_11807",
    "11808_11815",
    "11816_11823",
    "11824_11831",
    "11832_11839",
    "11840_11847",
    "11848_11855",
    "11856_11863",
    "11864_11871",
    "11872_11879",
    "11880_11887",
    "11888_11895",
    "11896_11903",
    "11904_11911",
    "11912_11919",
]
CONTROL_WINDOW = "11968_11975"
VALIDATION_WINDOW = "11976_11983"


RulePredicate = Callable[[dict[str, Any]], bool]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def expanded_source_path(window: str) -> Path:
    return STATE_DIR / f"frontier_public_leaf_policy_p231_frozen_prefix_fixed_row_{window}_col15_selector_expanded_probe.json"


def install_expanded_source_paths() -> None:
    def source_path(window: str) -> Path:
        return expanded_source_path(window)

    p1005.p998.p868.source_path = source_path
    p1005.p998.p993.p868.source_path = source_path
    p1005.p1003.p868.source_path = source_path
    p1005.p1003.p993.p868.source_path = source_path


def features(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("features") or {}


def source_case(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("source_case") or {}


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def selected_ops(rows: list[dict[str, Any]]) -> float:
    return sum(float(source_case(row).get("source_ops_over_rho") or 0.0) for row in rows)


def safe_ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def leaf_tuple(row: dict[str, Any]) -> tuple[int, ...]:
    return tuple(int_value(value) for value in features(row).get("unique_leaf_indices") or [])


def leaf_set(row: dict[str, Any]) -> set[int]:
    return set(leaf_tuple(row))


def build_examples(window: str, targets: str, min_source_rank: int) -> list[dict[str, Any]]:
    return p1005.p998.build_window_examples(window, targets, min_source_rank)


def build_window_set(windows: list[str], targets: str, min_source_rank: int) -> tuple[list[dict[str, Any]], dict[str, bool]]:
    rows: list[dict[str, Any]] = []
    exists: dict[str, bool] = {}
    for window in windows:
        path = expanded_source_path(window)
        exists[window] = path.exists()
        if path.exists():
            rows.extend(build_examples(window, targets, min_source_rank))
    return rows, exists


def source_summary(window: str) -> dict[str, Any]:
    path = expanded_source_path(window)
    if not path.exists():
        return {"source_exists": False}
    payload = load_json(path)
    summaries = ((payload.get("summary") or {}).get("policy_summaries") or [])
    fixed = next((row for row in summaries if row.get("policy") == "fixed_target_cap2_ow0_hw3_lw0_sw0_cw0_aw1"), summaries[0] if summaries else {})
    return {
        "path": str(path),
        "sha256": p1005.sha256_file(path),
        "source_exists": True,
        "stress_leaf_below_rho": fixed.get("stress_leaf_below_rho"),
        "stress_leaf_best_ops_over_rho": fixed.get("stress_leaf_best_ops_over_rho"),
        "stress_leaf_verified": fixed.get("stress_leaf_verified"),
        "stress_row_below_rho": fixed.get("stress_row_below_rho"),
        "stress_row_verified": fixed.get("stress_row_verified"),
    }


def add_rule(rules: list[dict[str, Any]], name: str, description: str, predicate: RulePredicate) -> None:
    rules.append({"description": description, "name": name, "predicate": predicate})


def candidate_rules(training_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selectors = sorted({str(features(row).get("leaf_selector")) for row in training_rows})
    top_ks = sorted({int_value(features(row).get("top_k")) for row in training_rows})
    leaves = sorted({leaf for row in training_rows for leaf in leaf_tuple(row)})
    tuple_counts = Counter(leaf_tuple(row) for row in training_rows)
    common_tuples = [item for item, _count in tuple_counts.most_common(12)]
    rules: list[dict[str, Any]] = []
    for selector in selectors:
        add_rule(
            rules,
            f"selector={selector}",
            f"leaf_selector == {selector}",
            lambda row, selector=selector: str(features(row).get("leaf_selector")) == selector,
        )
    for prefix in (
        "mode_cost_",
        "mode_cost_hybrid",
        "mode_cost_low",
        "mode_double_pair",
        "mode_hybrid",
        "mode_low_leaf_index",
        "mode_low_term_support",
    ):
        add_rule(
            rules,
            f"selector_prefix={prefix}",
            f"leaf_selector starts with {prefix}",
            lambda row, prefix=prefix: str(features(row).get("leaf_selector")).startswith(prefix),
        )
    for top_k in top_ks:
        add_rule(
            rules,
            f"topk={top_k}",
            f"top_k == {top_k}",
            lambda row, top_k=top_k: int_value(features(row).get("top_k")) == top_k,
        )
    for top_k in (4, 7, 12, 16):
        add_rule(
            rules,
            f"topk_le={top_k}",
            f"top_k <= {top_k}",
            lambda row, top_k=top_k: int_value(features(row).get("top_k")) <= top_k,
        )
    for leaf in leaves:
        add_rule(
            rules,
            f"contains_leaf={leaf}",
            f"unique_leaf_indices contains {leaf}",
            lambda row, leaf=leaf: leaf in leaf_set(row),
        )
    for item in common_tuples:
        add_rule(
            rules,
            f"leaf_tuple={list(item)}",
            f"unique_leaf_indices == {list(item)}",
            lambda row, item=item: leaf_tuple(row) == item,
        )
    for count in (1, 2, 3):
        add_rule(
            rules,
            f"leaf_count_le={count}",
            f"unique leaf count <= {count}",
            lambda row, count=count: len(leaf_tuple(row)) <= count,
        )
        add_rule(
            rules,
            f"leaf_count_eq={count}",
            f"unique leaf count == {count}",
            lambda row, count=count: len(leaf_tuple(row)) == count,
        )
    for selector in selectors:
        for top_k in top_ks:
            add_rule(
                rules,
                f"selector={selector} AND topk={top_k}",
                f"leaf_selector == {selector} and top_k == {top_k}",
                lambda row, selector=selector, top_k=top_k: str(features(row).get("leaf_selector")) == selector
                and int_value(features(row).get("top_k")) == top_k,
            )
        for item in common_tuples:
            add_rule(
                rules,
                f"selector={selector} AND leaf_tuple={list(item)}",
                f"leaf_selector == {selector} and unique_leaf_indices == {list(item)}",
                lambda row, selector=selector, item=item: str(features(row).get("leaf_selector")) == selector
                and leaf_tuple(row) == item,
            )
    for top_k in top_ks:
        for item in common_tuples:
            add_rule(
                rules,
                f"topk={top_k} AND leaf_tuple={list(item)}",
                f"top_k == {top_k} and unique_leaf_indices == {list(item)}",
                lambda row, top_k=top_k, item=item: int_value(features(row).get("top_k")) == top_k
                and leaf_tuple(row) == item,
            )
    return rules


def score_selection(rows: list[dict[str, Any]], predicate: RulePredicate) -> dict[str, Any]:
    positives = [row for row in rows if row.get("label_positive")]
    selected = [row for row in rows if predicate(row)]
    selected_positive = [row for row in selected if row.get("label_positive")]
    selected_direct = selected_ops(selected)
    return {
        "case_count": len(rows),
        "positive_count": len(positives),
        "precision": safe_ratio(len(selected_positive), len(selected)),
        "recall": safe_ratio(len(selected_positive), len(positives)),
        "selected_count": len(selected),
        "selected_direct_sum_ops_over_rho": round(selected_direct, 8),
        "selected_positive_count": len(selected_positive),
        "useful_amortized_ops_over_rho": safe_ratio(selected_direct, len(selected_positive)),
    }


def choose_rule(
    rules: list[dict[str, Any]],
    train_rows: list[dict[str, Any]],
    control_rows: list[dict[str, Any]],
    validation_rows: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    scored: list[dict[str, Any]] = []
    for rule in rules:
        row = {
            "description": rule["description"],
            "name": rule["name"],
            "train": score_selection(train_rows, rule["predicate"]),
            "control_diagnostic": score_selection(control_rows, rule["predicate"]),
            "validation_diagnostic": score_selection(validation_rows, rule["predicate"]),
        }
        if int_value(row["train"].get("selected_positive_count")) > 0:
            scored.append(row)
    scored.sort(
        key=lambda row: (
            -float(row["train"].get("precision") or 0.0),
            float(row["train"].get("useful_amortized_ops_over_rho") or 10**9),
            -int_value(row["train"].get("selected_positive_count")),
            int_value(row["train"].get("selected_count"), 10**9),
            str(row.get("name")),
        )
    )
    by_name = {rule["name"]: rule for rule in rules}
    chosen = scored[0]
    return by_name[str(chosen["name"])], scored


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


def lane_record(name: str, rows: list[dict[str, Any]], predicate: RulePredicate, rule_name: str, baseline_rank: int) -> dict[str, Any]:
    selected = [row for row in rows if predicate(row)]
    analysis, groups = p1005.scalar_valid_groups(selected, {"lane": name, "rule": rule_name}, baseline_rank)
    return {
        "analysis_summary": analysis.get("summary"),
        "scalar_valid_groups": [p1005.compact_group(group) for group in groups[:12]],
        "selected_cases": [selected_case_summary(row) for row in selected[:24]],
        "selected_count": len(selected),
        "source_selection": score_selection(rows, predicate),
    }


def determine_claim(control: dict[str, Any], validation: dict[str, Any]) -> str:
    control_best = (control.get("analysis_summary") or {}).get("scalar_valid_best_amortized_ops_over_rho")
    validation_summary = validation.get("analysis_summary") or {}
    validation_best = validation_summary.get("scalar_valid_best_amortized_ops_over_rho")
    if int_value(validation.get("selected_count")) == 0:
        return "NEGATIVE_RESULT_P1007_EXPANDED_RULE_SELECTS_NO_HOLDOUT_ROWS"
    if int_value(validation_summary.get("context_safe_scalar_valid_group_count")) == 0:
        return "NEGATIVE_RESULT_P1007_EXPANDED_RULE_NO_HOLDOUT_SCALAR_VALID_GROUP"
    if control_best is None or float(control_best) >= 1.0:
        return "P1007_EXPANDED_RULE_HOLDOUT_BELOW_RHO_CONTROL_WEAK"
    if validation_best is not None and float(validation_best) < 1.0:
        return "P1007_EXPANDED_SOURCE_POLICY_CONTEXT_SAFE_BELOW_RHO"
    return "P1007_EXPANDED_SOURCE_POLICY_CONTEXT_SAFE_ABOVE_RHO"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    install_expanded_source_paths()
    train_rows, train_exists = build_window_set(TRAIN_WINDOWS, args.targets, args.min_source_rank)
    control_rows, control_exists = build_window_set([CONTROL_WINDOW], args.targets, args.min_source_rank)
    validation_rows, validation_exists = build_window_set([VALIDATION_WINDOW], args.targets, args.min_source_rank)
    rules = candidate_rules(train_rows)
    chosen_rule, scored_rules = choose_rule(rules, train_rows, control_rows, validation_rows)
    train_record = lane_record("train_expanded_prior", train_rows, chosen_rule["predicate"], chosen_rule["name"], args.baseline_rank)
    control_record = lane_record("control_11968_11975", control_rows, chosen_rule["predicate"], chosen_rule["name"], args.baseline_rank)
    validation_record = lane_record(
        "validation_11976_11983",
        validation_rows,
        chosen_rule["predicate"],
        chosen_rule["name"],
        args.baseline_rank,
    )
    claim = determine_claim(control_record, validation_record)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": p1005.sha256_file(Path(args.contract)),
            "script_sha256": p1005.sha256_file(Path(__file__)),
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1007_") else "NEGATIVE RESULT",
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "SOURCE-POLICY BOUNDARY: this uses col15_selector_expanded artifacts, not the older P998 source family.",
            "TRAINING BOUNDARY: the rule is selected from training source labels only; control and validation labels are diagnostics.",
            "CONTEXT-SAFE-GATE: groups spanning multiple public fingerprints are rejected.",
            "FULL-ALGORITHM BOUNDARY: scalar-valid relation groups are not full relation collection, sparse linear algebra, or target descent.",
        ],
        "method": "p1007_p231_expanded_source_policy_compatibility",
        "parameters": {
            "baseline_rank": args.baseline_rank,
            "control_window": CONTROL_WINDOW,
            "min_source_rank": args.min_source_rank,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
            "train_windows": TRAIN_WINDOWS,
            "validation_window": VALIDATION_WINDOW,
        },
        "rule_search": {
            "candidate_rule_count": len(rules),
            "chosen_rule": {
                "description": chosen_rule["description"],
                "name": chosen_rule["name"],
            },
            "top_rules_by_training_score": scored_rules[:24],
        },
        "schema": SCHEMA,
        "source": {
            "control": source_summary(CONTROL_WINDOW),
            "train_exists": train_exists,
            "validation": source_summary(VALIDATION_WINDOW),
            "validation_exists": validation_exists,
        },
        "summary": {
            "chosen_rule_name": chosen_rule["name"],
            "claim_status": claim,
            "control_best_scalar_valid_amortized_ops_over_rho": (
                (control_record.get("analysis_summary") or {}).get("scalar_valid_best_amortized_ops_over_rho")
            ),
            "control_context_safe_scalar_valid_group_count": (
                (control_record.get("analysis_summary") or {}).get("context_safe_scalar_valid_group_count")
            ),
            "control_selected_count": control_record.get("selected_count"),
            "train_selected_count": train_record.get("selected_count"),
            "train_source_positive_count": train_record["source_selection"].get("selected_positive_count"),
            "validation_best_scalar_valid_amortized_ops_over_rho": (
                (validation_record.get("analysis_summary") or {}).get("scalar_valid_best_amortized_ops_over_rho")
            ),
            "validation_context_safe_scalar_valid_group_count": (
                (validation_record.get("analysis_summary") or {}).get("context_safe_scalar_valid_group_count")
            ),
            "validation_selected_count": validation_record.get("selected_count"),
            "validation_source_positive_count": validation_record["source_selection"].get("selected_positive_count"),
            "validation_total_selected_ops_over_rho": validation_record["source_selection"].get(
                "selected_direct_sum_ops_over_rho"
            ),
        },
        "lanes": {
            "control": control_record,
            "train": train_record,
            "validation": validation_record,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-rank", type=int, default=8, help="Rank baseline for group summaries")
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P1007 contract path")
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
        "claim={claim} rule={rule} train_selected={train_sel} control_selected={ctrl_sel} "
        "control_groups={ctrl_groups} control_best={ctrl_best} validation_selected={val_sel} "
        "validation_groups={val_groups} validation_best={val_best} validation_total={val_total} out={out}".format(
            claim=payload["claim_status"],
            rule=summary["chosen_rule_name"],
            train_sel=summary["train_selected_count"],
            ctrl_sel=summary["control_selected_count"],
            ctrl_groups=summary["control_context_safe_scalar_valid_group_count"],
            ctrl_best=summary["control_best_scalar_valid_amortized_ops_over_rho"],
            val_sel=summary["validation_selected_count"],
            val_groups=summary["validation_context_safe_scalar_valid_group_count"],
            val_best=summary["validation_best_scalar_valid_amortized_ops_over_rho"],
            val_total=summary["validation_total_selected_ops_over_rho"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
