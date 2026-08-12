#!/usr/bin/env python3
"""P869 public pre-scan predictor for the P867/P868 p231 motif."""

from __future__ import annotations

import argparse
import itertools
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_low_term_total2_ffe_hit_stream_probe as hit_stream_probe
import low_term_total2_p868_p231_fresh_skeleton_generator_audit as p868
import low_term_total2_public_prefix_shared_leaf_repair_probe as repair_probe


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p869_p231_public_motif_predictor.md"
DEFAULT_TRAIN_WINDOWS = ("1192_1199", "1200_1207", "1208_1215", "1216_1223")
DEFAULT_HELDOUT_WINDOWS = ("1224_1231", "1232_1239")
DEFAULT_TARGET = "22050.cf1@11731"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p869_p231_public_motif_predictor_probe.json"
SCHEMA = "ecdlp.low_term_total2_p869_p231_public_motif_predictor.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def parse_salt(row_key: str) -> int | None:
    match = re.search(r"salt(\d+)", str(row_key))
    if not match:
        return None
    return int(match.group(1))


def public_case_id(case: dict[str, Any]) -> str:
    return f"{case.get('window')}:{case.get('transfer_index')}:{case.get('target')}:{case.get('leaf_selector')}:{case.get('top_k')}:{p868.json_key(case.get('row_leaf_keys'))}"


def compact_leaf_feature(feature: dict[str, Any]) -> dict[str, Any]:
    return {
        "double_pair_scout_count": int_value(feature.get("double_pair_scout_count")),
        "has_double_pair": bool(feature.get("has_double_pair")),
        "has_repeated_terms": bool(feature.get("has_repeated_terms")),
        "leaf_index": int_value(feature.get("leaf_index")),
        "max_shape_count": int_value(feature.get("max_shape_count")),
        "min_scout_pos": int_value(feature.get("min_scout_pos")),
        "min_term_span": int_value(feature.get("min_term_span")),
        "min_term_support_size": int_value(feature.get("min_term_support_size")),
        "repeated_scout_count": int_value(feature.get("repeated_scout_count")),
        "scout_position_count": int_value(feature.get("scout_position_count")),
        "shape_2p2_count": int_value((feature.get("shape_counts") or {}).get("2+2")),
        "sum_repeat_excess": int_value(feature.get("sum_repeat_excess")),
        "term_support_size": int_value(feature.get("term_support_size")),
    }


def selected_public_features(case: dict[str, Any], context: dict[str, Any]) -> list[dict[str, Any]]:
    selected = []
    for item in hit_stream_probe.unique_row_leaf_keys(case):
        row_key = str(item.get("row_key"))
        feature_by_leaf = {
            int_value(feature.get("leaf_index")): feature
            for feature in context.get("feature_rows_by_row", {}).get(row_key, [])
            if isinstance(feature, dict)
        }
        for leaf in item.get("leaf_indices") or []:
            raw = feature_by_leaf.get(int_value(leaf))
            if raw is None:
                continue
            selected.append({"row_key": row_key, **compact_leaf_feature(raw)})
    return selected


def public_features(case: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    row_leaf_keys = hit_stream_probe.unique_row_leaf_keys(case)
    salts = [parse_salt(str(item.get("row_key"))) for item in row_leaf_keys]
    salt_values = sorted(salt for salt in salts if salt is not None)
    leaf_sets = [tuple(int_value(leaf) for leaf in item.get("leaf_indices") or []) for item in row_leaf_keys]
    unique_leaf_indices = sorted({leaf for leaves in leaf_sets for leaf in leaves})
    leaf_gap_tuple = tuple(leaf - unique_leaf_indices[0] for leaf in unique_leaf_indices) if unique_leaf_indices else tuple()
    features = selected_public_features(case, context)
    span_counts = Counter(int_value(feature.get("min_term_span")) for feature in features)
    support_counts = Counter(int_value(feature.get("min_term_support_size")) for feature in features)
    selector = str(case.get("leaf_selector") or "")
    selector_family = selector.split("_total", 1)[0]
    return {
        "all_has_double_pair": bool(features) and all(feature.get("has_double_pair") for feature in features),
        "all_has_repeated_terms": bool(features) and all(feature.get("has_repeated_terms") for feature in features),
        "case_id": public_case_id(case),
        "count_double_pair": sum(1 for feature in features if feature.get("has_double_pair")),
        "count_repeated_terms": sum(1 for feature in features if feature.get("has_repeated_terms")),
        "count_shape_2p2": sum(1 for feature in features if int_value(feature.get("shape_2p2_count")) > 0),
        "count_span1": span_counts.get(1, 0),
        "count_span2": span_counts.get(2, 0),
        "count_support2": support_counts.get(2, 0),
        "leaf_gap_tuple": leaf_gap_tuple,
        "leaf_selector": selector,
        "leaf_selector_family": selector_family,
        "max_leaf_index": max(unique_leaf_indices) if unique_leaf_indices else None,
        "max_min_term_span": max((int_value(feature.get("min_term_span")) for feature in features), default=0),
        "max_shape_count": max((int_value(feature.get("max_shape_count")) for feature in features), default=0),
        "min_leaf_index": min(unique_leaf_indices) if unique_leaf_indices else None,
        "min_min_scout_pos": min((int_value(feature.get("min_scout_pos")) for feature in features), default=0),
        "row_count": len(row_leaf_keys),
        "same_leaf_indices": bool(leaf_sets) and len(set(leaf_sets)) == 1,
        "salt_gap": (max(salt_values) - min(salt_values)) if len(salt_values) >= 2 else None,
        "salt_values": salt_values,
        "selected_leaf_occurrence_count": sum(len(leaves) for leaves in leaf_sets),
        "selected_leaf_sets": leaf_sets,
        "sum_repeat_excess": sum(int_value(feature.get("sum_repeat_excess")) for feature in features),
        "top_k": int_value(case.get("top_k")),
        "transfer_index": int_value(case.get("transfer_index")),
        "unique_leaf_count": len(unique_leaf_indices),
        "unique_leaf_indices": tuple(unique_leaf_indices),
        "window": str(case.get("window")),
    }


Predicate = tuple[str, Callable[[dict[str, Any]], bool], int]


def build_predicates(train_features: list[dict[str, Any]]) -> list[Predicate]:
    predicates: list[Predicate] = []

    def add(name: str, fn: Callable[[dict[str, Any]], bool], complexity: int = 1) -> None:
        predicates.append((name, fn, complexity))

    for selector in sorted({str(row.get("leaf_selector")) for row in train_features}):
        add(f"leaf_selector == {selector}", lambda row, selector=selector: row.get("leaf_selector") == selector, 2)
    for family in sorted({str(row.get("leaf_selector_family")) for row in train_features}):
        add(
            f"leaf_selector_family == {family}",
            lambda row, family=family: row.get("leaf_selector_family") == family,
            1,
        )
    for top_k in sorted({int_value(row.get("top_k")) for row in train_features}):
        add(f"top_k == {top_k}", lambda row, top_k=top_k: int_value(row.get("top_k")) == top_k, 1)
        add(f"top_k <= {top_k}", lambda row, top_k=top_k: int_value(row.get("top_k")) <= top_k, 1)

    for count in range(1, 7):
        add(f"unique_leaf_count <= {count}", lambda row, count=count: int_value(row.get("unique_leaf_count")) <= count, 1)
        add(f"unique_leaf_count >= {count}", lambda row, count=count: int_value(row.get("unique_leaf_count")) >= count, 1)
        add(
            f"count_span2 >= {count}",
            lambda row, count=count: int_value(row.get("count_span2")) >= count,
            1,
        )
        add(
            f"count_shape_2p2 >= {count}",
            lambda row, count=count: int_value(row.get("count_shape_2p2")) >= count,
            1,
        )
        add(
            f"count_double_pair >= {count}",
            lambda row, count=count: int_value(row.get("count_double_pair")) >= count,
            1,
        )
    for gap in (1, 2, 3, 8, 12):
        add(f"salt_gap <= {gap}", lambda row, gap=gap: row.get("salt_gap") is not None and int_value(row.get("salt_gap")) <= gap, 1)
    add("same_leaf_indices", lambda row: bool(row.get("same_leaf_indices")), 1)
    add("all_has_double_pair", lambda row: bool(row.get("all_has_double_pair")), 1)
    add("all_has_repeated_terms", lambda row: bool(row.get("all_has_repeated_terms")), 1)
    add("max_min_term_span <= 2", lambda row: int_value(row.get("max_min_term_span")) <= 2, 1)
    add("min_min_scout_pos <= 80", lambda row: int_value(row.get("min_min_scout_pos")) <= 80, 1)

    leaves = sorted({leaf for row in train_features for leaf in row.get("unique_leaf_indices", tuple())})
    for leaf in leaves:
        add(f"contains_leaf {leaf}", lambda row, leaf=leaf: leaf in set(row.get("unique_leaf_indices") or tuple()), 2)
    for left, right in itertools.combinations(leaves, 2):
        # Pair predicates are public but more specific; give them higher complexity.
        add(
            f"contains_leaf_pair {left},{right}",
            lambda row, left=left, right=right: {left, right}.issubset(set(row.get("unique_leaf_indices") or tuple())),
            3,
        )
    return predicates


def evaluate_rule(
    name: str,
    fn: Callable[[dict[str, Any]], bool],
    examples: list[dict[str, Any]],
) -> dict[str, Any]:
    selected = [row for row in examples if fn(row["features"])]
    positives = [row for row in examples if row["label_positive"]]
    true_pos = [row for row in selected if row["label_positive"]]
    false_pos = [row for row in selected if not row["label_positive"]]
    false_neg = [row for row in examples if row["label_positive"] and not fn(row["features"])]
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
    train_prevalence = safe_ratio(sum(1 for row in train_examples if row["label_positive"]), len(train_examples)) or 0.0
    candidates: list[tuple[dict[str, Any], Callable[[dict[str, Any]], bool], int]] = []
    for width in (1, 2):
        for combo in itertools.combinations(predicates, width):
            name, fn, complexity = make_rule(combo)
            metrics = evaluate_rule(name, fn, train_examples)
            if metrics["selected_count"] == 0 or metrics["true_positive_count"] == 0:
                continue
            if (metrics.get("precision") or 0.0) <= train_prevalence:
                continue
            metrics["complexity"] = complexity
            metrics["train_precision_lift"] = safe_ratio(metrics["precision"] or 0.0, train_prevalence) if train_prevalence else None
            candidates.append((metrics, fn, complexity))
    if not candidates:
        metrics = evaluate_rule("select_all", lambda _row: True, train_examples)
        metrics["complexity"] = 0
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
    top_metrics = [item[0] for item in candidates[:12]]
    return candidates[0][0], candidates[0][1], top_metrics


def build_examples(args: argparse.Namespace) -> list[dict[str, Any]]:
    targets = {target.strip() for target in args.targets.split(",") if target.strip()}
    windows = list(args.train_windows) + list(args.heldout_windows)
    source_payloads = [(window, p868.source_path(window), p868.load_json(p868.source_path(window))) for window in windows]
    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]] = {}
    build_cache: dict[str, tuple[Any, list[dict[str, Any]], dict[str, Any], dict[str, dict[str, dict[str, Any]]], argparse.Namespace]] = {}
    examples: list[dict[str, Any]] = []
    for window, _path, source in source_payloads:
        params = repair_probe.source_parameters(source)
        probe_args = repair_probe.probe_args_from_source(source)
        cache_key = p868.json_key(
            {
                "bank_source": params.get("bank_source"),
                "config_source": params.get("config_source"),
                "direct_source": params.get("direct_source"),
                "radius": params.get("radius"),
                "transfer_source": params.get("transfer_source"),
            }
        )
        if cache_key not in build_cache:
            build_cache[cache_key] = (*repair_probe.build_specs(params), probe_args)
        verifier, records, config_source, specs_by_target, probe_args = build_cache[cache_key]
        for case in p868.iter_source_cases(source, window, targets):
            context = hit_stream_probe.scan_case_context(
                verifier,
                records,
                config_source,
                specs_by_target,
                case,
                probe_args,
                context_cache,
            )
            features = public_features(case, context)
            labeled = p868.analyze_case(
                verifier,
                records,
                config_source,
                specs_by_target,
                probe_args,
                context_cache,
                case,
            )
            examples.append(
                {
                    "case": p868.compact_case(labeled),
                    "features": features,
                    "label_emits_motif": int_value(labeled.get("p867_motif_form_count")) > 0,
                    "label_positive": bool(labeled.get("p867_motif_verified_below_rho")),
                    "split": "train" if window in set(args.train_windows) else "heldout",
                    "window": window,
                }
            )
    return examples


def compact_example(row: dict[str, Any]) -> dict[str, Any]:
    case = row["case"]
    features = row["features"]
    return {
        "case_id": features.get("case_id"),
        "direct_ops_over_rho": case.get("direct_ops_over_rho"),
        "features": {
            key: features.get(key)
            for key in (
                "leaf_selector",
                "leaf_selector_family",
                "top_k",
                "unique_leaf_indices",
                "leaf_gap_tuple",
                "salt_gap",
                "count_span2",
                "count_shape_2p2",
                "count_double_pair",
                "same_leaf_indices",
            )
        },
        "label_positive": row.get("label_positive"),
        "split": row.get("split"),
        "transfer_index": case.get("transfer_index"),
        "union_derived_secret": case.get("union_derived_secret"),
        "window": row.get("window"),
    }


def summarize_split(examples: list[dict[str, Any]], selected: list[dict[str, Any]]) -> dict[str, Any]:
    positives = [row for row in examples if row["label_positive"]]
    selected_positive = [row for row in selected if row["label_positive"]]
    precision = safe_ratio(len(selected_positive), len(selected))
    prevalence = safe_ratio(len(positives), len(examples))
    recall = safe_ratio(len(selected_positive), len(positives))
    return {
        "case_count": len(examples),
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
        return "P869_PUBLIC_PRE_SCAN_RULE_PREDICTS_HELDOUT_P867_MOTIF"
    if int_value(heldout_summary.get("selected_positive_count")) > 0:
        return "P869_PUBLIC_RULE_FINDS_HELDOUT_MOTIF_WITHOUT_PRECISION_LIFT"
    return "NEGATIVE_RESULT_P869_PUBLIC_RULE_MISSES_HELDOUT_P867_MOTIF"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    examples = build_examples(args)
    train = [row for row in examples if row["split"] == "train"]
    heldout = [row for row in examples if row["split"] == "heldout"]
    chosen_metrics, chosen_fn, top_train_rules = choose_rule(train)
    train_selected = [row for row in train if chosen_fn(row["features"])]
    heldout_selected = [row for row in heldout if chosen_fn(row["features"])]
    train_summary = summarize_split(train, train_selected)
    heldout_summary = summarize_split(heldout, heldout_selected)
    claim = determine_claim(heldout_summary)
    all_heldout_summary = summarize_split(heldout, heldout)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
            "source_windows": {
                window: str(p868.source_path(window))
                for window in list(args.train_windows) + list(args.heldout_windows)
            },
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P869_") else "NEGATIVE RESULT",
        "created_at": now_iso(),
        "heldout_selected_cases": [compact_example(row) for row in heldout_selected],
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP verifier harness.",
            "PREDICTOR BOUNDARY: selected rule uses only public pre-scan features; relation labels are used for training and evaluation.",
            "HELD-OUT BOUNDARY: held-out windows are chronological but still in the same p231 fixed-row family.",
            "TARGET-DESCENT BOUNDARY: local motif prediction does not solve cross-public-key target descent.",
            "POLLARD-RHO BOUNDARY: this is relation-lane selector evidence, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p869_p231_public_motif_predictor",
        "parameters": {
            "heldout_windows": list(args.heldout_windows),
            "motif": p868.P867_MOTIF,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
            "train_windows": list(args.train_windows),
        },
        "red_team_handoff": {
            "artifact_paths": [str(args.out), str(args.contract), str(Path(__file__))],
            "assumptions": [
                "Public feature rows are available before relation-event reconstruction.",
                "Rule selection uses only train-window labels.",
                "Held-out labels are revealed only after the public rule is fixed.",
            ],
            "claim_or_task": "Test whether public pre-scan features predict held-out P867 motif below-rho derivations.",
            "evidence_so_far": [
                f"Chosen rule: {chosen_metrics.get('name')}.",
                f"Held-out selected positives: {heldout_summary.get('selected_positive_count')}/{heldout_summary.get('selected_count')}.",
                f"Held-out precision lift: {heldout_summary.get('precision_lift_over_prevalence')}.",
            ],
            "failure_modes": [
                "The chosen public rule may be exploiting fixed-row-family regularities rather than a stable algebraic predictor.",
                "The held-out set is small and still adjacent in the same p231 family.",
                "A successful predictor still needs materialization on later unseen windows before promotion.",
            ],
            "next_concrete_action": (
                "Build P870 to materialize the selected public rule on later unseen p231 windows, charging only predicted cases before relation reconstruction."
            ),
            "status": "OBSERVATION" if claim.startswith("P869_") else "NEGATIVE RESULT",
        },
        "schema": SCHEMA,
        "summary": {
            "all_heldout_prevalence": all_heldout_summary.get("prevalence"),
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
    parser.add_argument("--train-windows", nargs="+", default=list(DEFAULT_TRAIN_WINDOWS))
    parser.add_argument("--heldout-windows", nargs="+", default=list(DEFAULT_HELDOUT_WINDOWS))
    parser.add_argument("--targets", default=DEFAULT_TARGET)
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
