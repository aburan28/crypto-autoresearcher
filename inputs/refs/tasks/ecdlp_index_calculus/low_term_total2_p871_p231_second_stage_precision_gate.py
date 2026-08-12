#!/usr/bin/env python3
"""P871 second-stage public precision gate over P870-selected p231 cases."""

from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p871_p231_second_stage_precision_gate.md"
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_p870_p231_public_rule_materialization_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p871_p231_second_stage_precision_gate_probe.json"
DEFAULT_TRAIN_WINDOWS = ("1240_1247", "1248_1255", "1256_1263", "1264_1271")
DEFAULT_HELDOUT_WINDOWS = ("1272_1279", "1280_1287")
SCHEMA = "ecdlp.low_term_total2_p871_p231_second_stage_precision_gate.v1"


Predicate = tuple[str, Callable[[dict[str, Any]], bool], int]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


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


def safe_ratio(numerator: int | float, denominator: int | float) -> float | None:
    if denominator == 0:
        return None
    return round(float(numerator) / float(denominator), 8)


def tuple_value(value: Any) -> tuple[int, ...]:
    if value is None:
        return tuple()
    return tuple(int_value(item) for item in value)


def public_features(case: dict[str, Any]) -> dict[str, Any]:
    features = dict(case.get("public_features") or {})
    features["direct_ops_over_rho_bucket"] = None
    features["leaf_gap_tuple"] = tuple_value(features.get("leaf_gap_tuple"))
    features["unique_leaf_indices"] = tuple_value(features.get("unique_leaf_indices"))
    features["leaf_selector"] = str(features.get("leaf_selector") or case.get("leaf_selector") or "")
    features["leaf_selector_family"] = str(features.get("leaf_selector_family") or "")
    features["salt_gap"] = case.get("public_features", {}).get("salt_gap")
    features["top_k"] = int_value(features.get("top_k"))
    features["unique_leaf_count"] = int_value(features.get("unique_leaf_count"))
    features["selected_leaf_occurrence_count"] = int_value(features.get("selected_leaf_occurrence_count"))
    features["count_double_pair"] = int_value(features.get("count_double_pair"))
    features["count_shape_2p2"] = int_value(features.get("count_shape_2p2"))
    features["window"] = str(case.get("window") or features.get("window") or "")
    return features


def compact_case(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": (case.get("public_features") or {}).get("case_id"),
        "direct_ops_over_rho": case.get("direct_ops_over_rho"),
        "leaf_selector": case.get("leaf_selector"),
        "p867_motif_verified_below_rho": bool(case.get("p867_motif_verified_below_rho")),
        "row_leaf_keys": case.get("row_leaf_keys"),
        "target": case.get("target"),
        "top_k": case.get("top_k"),
        "transfer_index": case.get("transfer_index"),
        "union_derived_secret": case.get("union_derived_secret"),
        "union_rank": case.get("union_rank"),
        "union_relation_count": case.get("union_relation_count"),
        "window": case.get("window"),
        "public_features": {
            key: public_features(case).get(key)
            for key in (
                "leaf_selector",
                "leaf_selector_family",
                "top_k",
                "unique_leaf_indices",
                "leaf_gap_tuple",
                "salt_gap",
                "unique_leaf_count",
                "selected_leaf_occurrence_count",
                "count_double_pair",
                "count_shape_2p2",
            )
        },
    }


def build_examples(payload: dict[str, Any], train_windows: set[str], heldout_windows: set[str]) -> list[dict[str, Any]]:
    examples = []
    allowed_windows = train_windows | heldout_windows
    for case in payload.get("selected_cases") or []:
        window = str(case.get("window"))
        if window not in allowed_windows:
            continue
        split = "train" if window in train_windows else "heldout"
        examples.append(
            {
                "case": case,
                "features": public_features(case),
                "label_positive": bool(case.get("p867_motif_verified_below_rho")),
                "split": split,
                "window": window,
            }
        )
    return examples


def add_predicate(predicates: list[Predicate], name: str, fn: Callable[[dict[str, Any]], bool], complexity: int = 1) -> None:
    predicates.append((name, fn, complexity))


def build_predicates(train_features: list[dict[str, Any]]) -> list[Predicate]:
    predicates: list[Predicate] = []
    for selector in sorted({str(row.get("leaf_selector")) for row in train_features}):
        add_predicate(
            predicates,
            f"leaf_selector == {selector}",
            lambda row, selector=selector: row.get("leaf_selector") == selector,
            2,
        )
    for family in sorted({str(row.get("leaf_selector_family")) for row in train_features}):
        add_predicate(
            predicates,
            f"leaf_selector_family == {family}",
            lambda row, family=family: row.get("leaf_selector_family") == family,
            1,
        )
    for leaf_gap in sorted({tuple_value(row.get("leaf_gap_tuple")) for row in train_features}):
        add_predicate(
            predicates,
            f"leaf_gap_tuple == {list(leaf_gap)}",
            lambda row, leaf_gap=leaf_gap: tuple_value(row.get("leaf_gap_tuple")) == leaf_gap,
            3,
        )
    for leaf_set in sorted({tuple_value(row.get("unique_leaf_indices")) for row in train_features}):
        add_predicate(
            predicates,
            f"unique_leaf_indices == {list(leaf_set)}",
            lambda row, leaf_set=leaf_set: tuple_value(row.get("unique_leaf_indices")) == leaf_set,
            3,
        )
    for top_k in sorted({int_value(row.get("top_k")) for row in train_features}):
        add_predicate(predicates, f"top_k == {top_k}", lambda row, top_k=top_k: int_value(row.get("top_k")) == top_k, 1)
        add_predicate(predicates, f"top_k <= {top_k}", lambda row, top_k=top_k: int_value(row.get("top_k")) <= top_k, 1)
    for count in range(1, 11):
        add_predicate(
            predicates,
            f"unique_leaf_count == {count}",
            lambda row, count=count: int_value(row.get("unique_leaf_count")) == count,
            1,
        )
        add_predicate(
            predicates,
            f"unique_leaf_count <= {count}",
            lambda row, count=count: int_value(row.get("unique_leaf_count")) <= count,
            1,
        )
        add_predicate(
            predicates,
            f"unique_leaf_count >= {count}",
            lambda row, count=count: int_value(row.get("unique_leaf_count")) >= count,
            1,
        )
        add_predicate(
            predicates,
            f"selected_leaf_occurrence_count == {count}",
            lambda row, count=count: int_value(row.get("selected_leaf_occurrence_count")) == count,
            1,
        )
        add_predicate(
            predicates,
            f"count_double_pair >= {count}",
            lambda row, count=count: int_value(row.get("count_double_pair")) >= count,
            1,
        )
        add_predicate(
            predicates,
            f"count_shape_2p2 >= {count}",
            lambda row, count=count: int_value(row.get("count_shape_2p2")) >= count,
            1,
        )
    for gap in (0, 1, 2, 4, 6, 8):
        add_predicate(
            predicates,
            f"salt_gap <= {gap}",
            lambda row, gap=gap: row.get("salt_gap") is not None and int_value(row.get("salt_gap")) <= gap,
            1,
        )
    return predicates


def evaluate_rule(name: str, fn: Callable[[dict[str, Any]], bool], examples: list[dict[str, Any]]) -> dict[str, Any]:
    selected = [row for row in examples if fn(row["features"])]
    positives = [row for row in examples if row["label_positive"]]
    true_pos = [row for row in selected if row["label_positive"]]
    false_pos = [row for row in selected if not row["label_positive"]]
    false_neg = [row for row in positives if not fn(row["features"])]
    precision = safe_ratio(len(true_pos), len(selected))
    recall = safe_ratio(len(true_pos), len(positives))
    f1 = None
    if precision is not None and recall is not None and precision + recall:
        f1 = round(2 * precision * recall / (precision + recall), 8)
    return {
        "false_negative_count": len(false_neg),
        "false_positive_count": len(false_pos),
        "f1": f1,
        "name": name,
        "positive_count": len(positives),
        "precision": precision,
        "recall": recall,
        "selected_count": len(selected),
        "true_positive_count": len(true_pos),
    }


def make_rule(predicates: tuple[Predicate, ...]) -> tuple[str, Callable[[dict[str, Any]], bool], int]:
    name = " AND ".join(predicate[0] for predicate in predicates)
    complexity = sum(predicate[2] for predicate in predicates)

    def fn(row: dict[str, Any]) -> bool:
        return all(predicate[1](row) for predicate in predicates)

    return name, fn, complexity


def choose_rule(train_examples: list[dict[str, Any]]) -> tuple[dict[str, Any], Callable[[dict[str, Any]], bool], list[dict[str, Any]]]:
    train_features = [row["features"] for row in train_examples]
    predicates = build_predicates(train_features)
    train_positive_count = sum(1 for row in train_examples if row["label_positive"])
    min_true_positives = min(2, train_positive_count)
    train_prevalence = safe_ratio(train_positive_count, len(train_examples)) or 0.0
    candidates: list[tuple[dict[str, Any], Callable[[dict[str, Any]], bool], int]] = []
    for width in (1, 2):
        for combo in itertools.combinations(predicates, width):
            name, fn, complexity = make_rule(combo)
            metrics = evaluate_rule(name, fn, train_examples)
            if metrics["selected_count"] == 0 or metrics["true_positive_count"] < min_true_positives:
                continue
            if (metrics.get("precision") or 0.0) <= train_prevalence:
                continue
            metrics["complexity"] = complexity
            metrics["train_precision_lift"] = safe_ratio(metrics["precision"] or 0.0, train_prevalence) if train_prevalence else None
            candidates.append((metrics, fn, complexity))
    if not candidates:
        metrics = evaluate_rule("select_all_p870_selected", lambda _row: True, train_examples)
        metrics["complexity"] = 0
        metrics["train_precision_lift"] = 1.0
        return metrics, (lambda _row: True), [metrics]
    candidates.sort(
        key=lambda item: (
            -(item[0].get("f1") or 0.0),
            -(item[0].get("precision") or 0.0),
            -int_value(item[0].get("true_positive_count")),
            int_value(item[0].get("selected_count")),
            item[2],
            item[0]["name"],
        )
    )
    return candidates[0][0], candidates[0][1], [item[0] for item in candidates[:16]]


def summarize_split(examples: list[dict[str, Any]], selected: list[dict[str, Any]]) -> dict[str, Any]:
    positives = [row for row in examples if row["label_positive"]]
    selected_positive = [row for row in selected if row["label_positive"]]
    precision = safe_ratio(len(selected_positive), len(selected))
    prevalence = safe_ratio(len(positives), len(examples))
    recall = safe_ratio(len(selected_positive), len(positives))
    f1 = None
    if precision is not None and recall is not None and precision + recall:
        f1 = round(2 * precision * recall / (precision + recall), 8)
    return {
        "case_count": len(examples),
        "f1": f1,
        "motif_positive_count": len(positives),
        "motif_positive_window_count": len({row["window"] for row in positives}),
        "precision": precision,
        "precision_lift_over_prevalence": safe_ratio(precision or 0.0, prevalence or 0.0) if prevalence else None,
        "prevalence": prevalence,
        "recall": recall,
        "selected_count": len(selected),
        "selected_positive_count": len(selected_positive),
        "selected_positive_transfer_count": len({int_value(row["case"].get("transfer_index")) for row in selected_positive}),
        "selected_positive_window_count": len({row["window"] for row in selected_positive}),
    }


def determine_claim(heldout_summary: dict[str, Any]) -> str:
    if int_value(heldout_summary.get("selected_positive_count")) > 0 and (
        heldout_summary.get("precision_lift_over_prevalence") or 0
    ) > 1.0:
        return "P871_PUBLIC_SECOND_STAGE_GATE_IMPROVES_HELDOUT_PRECISION"
    if int_value(heldout_summary.get("selected_positive_count")) > 0:
        return "P871_PUBLIC_SECOND_STAGE_GATE_FINDS_HELDOUT_MOTIFS_WITHOUT_PRECISION_LIFT"
    return "NEGATIVE_RESULT_P871_PUBLIC_SECOND_STAGE_GATE_MISSES_HELDOUT_MOTIFS"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    source = load_json(args.source)
    train_windows = set(args.train_windows)
    heldout_windows = set(args.heldout_windows)
    examples = build_examples(source, train_windows, heldout_windows)
    train = [row for row in examples if row["split"] == "train"]
    heldout = [row for row in examples if row["split"] == "heldout"]
    chosen_metrics, chosen_fn, top_train_rules = choose_rule(train)
    train_selected = [row for row in train if chosen_fn(row["features"])]
    heldout_selected = [row for row in heldout if chosen_fn(row["features"])]
    train_summary = summarize_split(train, train_selected)
    heldout_summary = summarize_split(heldout, heldout_selected)
    all_heldout_summary = summarize_split(heldout, heldout)
    claim = determine_claim(heldout_summary)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
            "source": str(args.source),
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P871_") else "NEGATIVE RESULT",
        "created_at": now_iso(),
        "heldout_selected_cases": [compact_case(row["case"]) for row in heldout_selected],
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP verifier harness.",
            "SELECTED-ONLY BOUNDARY: only P870-selected cases are used; recall over unselected cases is not estimated.",
            "TRAIN/HELD-OUT BOUNDARY: held-out windows are chronological but still in the same p231 fixed-row family.",
            "FEATURE BOUNDARY: the second-stage gate uses public P870 feature fields, not relation-event labels.",
            "TARGET-DESCENT BOUNDARY: higher precision local derivations do not solve cross-public-key target descent.",
            "POLLARD-RHO BOUNDARY: this is relation-lane selector evidence, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p871_p231_second_stage_precision_gate",
        "parameters": {
            "base_source_claim": source.get("claim_status"),
            "heldout_windows": list(args.heldout_windows),
            "train_windows": list(args.train_windows),
        },
        "red_team_handoff": {
            "artifact_paths": [str(args.out), str(args.contract), str(Path(__file__))],
            "assumptions": [
                "P870 selected-case labels are available because P870 already paid reconstruction cost.",
                "No unselected-case labels are used.",
                "The second-stage rule is selected from train windows only.",
            ],
            "claim_or_task": "Test whether a public second-stage gate improves precision over P870-selected held-out prevalence.",
            "evidence_so_far": [
                f"Chosen rule: {chosen_metrics.get('name')}.",
                f"Held-out precision: {heldout_summary.get('precision')}.",
                f"Held-out lift: {heldout_summary.get('precision_lift_over_prevalence')}.",
            ],
            "failure_modes": [
                "The rule may overfit sparse train positives.",
                "Selected-only evaluation cannot prove recall over unselected P870 cases.",
                "The p231 family may be too narrow for broader ECDLP claims.",
            ],
            "next_concrete_action": (
                "Build P872 to materialize the P871 gate on later P870-style windows or run a paid full-label recall audit if recall is strategically necessary."
            ),
            "status": "OBSERVATION" if claim.startswith("P871_") else "NEGATIVE RESULT",
        },
        "schema": SCHEMA,
        "summary": {
            "all_heldout_prevalence": all_heldout_summary.get("prevalence"),
            "base_p870_global_precision": (source.get("summary") or {}).get("p867_motif_verified_below_rho_precision"),
            "chosen_rule": chosen_metrics,
            "claim_status": claim,
            "heldout": heldout_summary,
            "top_train_rules": top_train_rules,
            "train": train_summary,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--train-windows", nargs="+", default=list(DEFAULT_TRAIN_WINDOWS))
    parser.add_argument("--heldout-windows", nargs="+", default=list(DEFAULT_HELDOUT_WINDOWS))
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
