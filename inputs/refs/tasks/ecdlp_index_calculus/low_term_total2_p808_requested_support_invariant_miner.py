#!/usr/bin/env python3
"""P808 requested-support invariant miner after the P807 public-feature failure."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P806_SCRIPT = TASK_DIR / "low_term_total2_p806_public_feature_classifier.py"
P807_SCRIPT = TASK_DIR / "low_term_total2_p807_richer_public_feature_classifier.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p808_requested_support_invariant_miner_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p808_requested_support_invariant_miner.md"
SCHEMA = "ecdlp.low_term_total2_p808_requested_support_invariant_miner.v1"

PUBLIC_STATIC = "public_static_rich_p807"
CALIBRATION_TRACE = "calibration_trace_density_nonpublic"
COMBINED = "combined_static_plus_trace_diagnostic"
TRACE_RANK = "calibration_trace_rank_projection_nonpublic"
FAMILIES = (PUBLIC_STATIC, CALIBRATION_TRACE, COMBINED)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def csv_ints(text: str) -> list[int]:
    return [int(item.strip()) for item in text.split(",") if item.strip()]


def csv_strings(text: str) -> list[str]:
    return [item.strip() for item in text.split(",") if item.strip()]


def stat(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "min": None}
    return {"count": len(values), "max": max(values), "mean": round(mean(values), 8), "min": min(values)}


def slug(value: str) -> str:
    text = "".join(ch if ch.isalnum() else "_" for ch in str(value))
    return "_".join(part for part in text.split("_") if part)


def bounded_bin(value: int, modulus: int, bins: int) -> int:
    if modulus <= 0:
        return 0
    return max(0, min(int(bins) - 1, int(value) * int(bins) // int(modulus)))


def count_bin(value: int) -> str:
    value = int(value)
    if value <= 0:
        return "0"
    if value <= 8:
        return str(value)
    power = 1 << (value.bit_length() - 1)
    return f"{power}+"


def canonical_support(support: tuple[int, int]) -> tuple[int, int]:
    left, right = int(support[0]), int(support[1])
    return (left, right) if left <= right else (right, left)


def line_key_tuple(record: dict[str, Any]) -> tuple[int, int, int, int] | None:
    raw = record.get("line_key")
    if raw is None:
        return None
    if len(raw) != 4:
        return None
    return tuple(int(part) for part in raw)


def support_from_line_key(record: dict[str, Any]) -> tuple[int, int] | None:
    key = line_key_tuple(record)
    if key is None:
        return None
    return canonical_support((key[0], key[1]))


def form_seed_index(record: dict[str, Any]) -> int | None:
    form = record.get("calibration_form") or {}
    label = str(form.get("seed_label") or "")
    if label.startswith("t") and label[1:].isdigit():
        return int(label[1:])
    return None


def trace_sort_tuple(item: tuple[tuple[int, int, int, int], dict[str, Any]]) -> tuple[int, int, int, tuple[int, int, int, int]]:
    key, value = item
    return (
        int(value.get("candidate_row_count") or 0),
        int(value.get("candidate_form_count") or 0),
        -int(sum(int(part) for part in key)),
        tuple(-int(part) for part in key),
    )


def group_calibrations_by_support(
    all_calibrated: dict[tuple[int, int, int, int], dict[str, Any]]
) -> dict[tuple[int, int], list[tuple[tuple[int, int, int, int], dict[str, Any]]]]:
    grouped: dict[tuple[int, int], list[tuple[tuple[int, int, int, int], dict[str, Any]]]] = defaultdict(list)
    for raw_key, value in all_calibrated.items():
        key = tuple(int(part) for part in raw_key)
        grouped[canonical_support((key[0], key[1]))].append((key, value))
    for items in grouped.values():
        items.sort(key=trace_sort_tuple, reverse=True)
    return grouped


def trace_features_for_support(
    support: tuple[int, int],
    grouped: dict[tuple[int, int], list[tuple[tuple[int, int, int, int], dict[str, Any]]]],
    order: int,
    bins: int,
) -> tuple[str, ...]:
    items = grouped.get(canonical_support(support)) or []
    if not items:
        return ("trace_present=0",)
    best_key, best = items[0]
    rows = [int(item.get("candidate_row_count") or 0) for _key, item in items]
    forms = [int(item.get("candidate_form_count") or 0) for _key, item in items]
    field_ops = [
        int(((item.get("field_ops") or {}).get("total_field_ops")) or 0)
        for _key, item in items
    ]
    line_values = [int(item.get("line_value") or 0) % int(order) for _key, item in items]
    suffixes = Counter((int(key[2]), int(key[3])) for key, _item in items)
    best_form = best.get("calibration_form") or {}
    seed_index = form_seed_index(best)
    rhs_known = int(best_form.get("rhs_known") or 0) % int(order)
    scale = int(best_form.get("scale") or 0) % int(order)
    replica = int(best_form.get("replica") or 0)
    row_index = int(best_form.get("row_index") or 0)
    suffix, suffix_count = suffixes.most_common(1)[0]
    return (
        "trace_present=1",
        f"trace_record_count_bin={count_bin(len(items))}",
        f"trace_best_candidate_rows_bin={count_bin(max(rows))}",
        f"trace_best_candidate_forms_bin={count_bin(max(forms))}",
        f"trace_min_candidate_rows_bin={count_bin(min(rows))}",
        f"trace_min_field_ops_bin={count_bin(min(field_ops))}",
        f"trace_best_line_suffix={int(best_key[2])}:{int(best_key[3])}",
        f"trace_common_line_suffix={suffix[0]}:{suffix[1]}",
        f"trace_common_line_suffix_count_bin={count_bin(suffix_count)}",
        f"trace_best_line_value_bin={bounded_bin(int(best.get('line_value') or 0), order, bins)}",
        f"trace_best_line_value_mod16={int(best.get('line_value') or 0) % 16}",
        f"trace_min_line_value_mod16={min(line_values) % 16}",
        f"trace_rhs_bin={bounded_bin(rhs_known, order, bins)}",
        f"trace_rhs_mod16={rhs_known % 16}",
        f"trace_scale_bin={bounded_bin(scale, order, bins)}",
        f"trace_scale_mod16={scale % 16}",
        f"trace_best_replica_mod8={replica % 8}",
        f"trace_best_row_index_mod16={row_index % 16}",
        f"trace_best_seed_mod8={0 if seed_index is None else seed_index % 8}",
        f"trace_has_rows_ge_2={int(max(rows) >= 2)}",
        f"trace_has_rows_ge_4={int(max(rows) >= 4)}",
        f"trace_has_forms_ge_4={int(max(forms) >= 4)}",
    )


def build_trace_features(
    all_pairs: list[tuple[int, int]],
    all_calibrated: dict[tuple[int, int, int, int], dict[str, Any]],
    order: int,
    bins: int,
) -> tuple[dict[tuple[int, int], tuple[str, ...]], dict[tuple[int, int], list[tuple[tuple[int, int, int, int], dict[str, Any]]]]]:
    grouped = group_calibrations_by_support(all_calibrated)
    features = {
        canonical_support(support): trace_features_for_support(canonical_support(support), grouped, order, bins)
        for support in all_pairs
    }
    return features, grouped


def trace_rank_projection_supports(
    all_calibrated: dict[tuple[int, int, int, int], dict[str, Any]],
    budget: int,
) -> set[tuple[int, int]]:
    ranked = sorted(all_calibrated.items(), key=trace_sort_tuple, reverse=True)
    return {
        canonical_support((int(key[0]), int(key[1])))
        for key, _value in ranked[: min(int(budget), len(ranked))]
    }


def trace_support_rank_supports(
    grouped: dict[tuple[int, int], list[tuple[tuple[int, int, int, int], dict[str, Any]]]],
    count: int,
) -> set[tuple[int, int]]:
    ranked = sorted(
        grouped.items(),
        key=lambda item: (trace_sort_tuple(item[1][0]), tuple(-part for part in item[0])),
        reverse=True,
    )
    return {support for support, _items in ranked[: max(0, min(int(count), len(ranked)))]}


def train_logodds_model(examples: list[dict[str, Any]], smoothing: float) -> dict[str, Any]:
    counts: dict[str, Counter] = defaultdict(Counter)
    totals = Counter()
    for example in examples:
        requested = example["requested"]
        features_by_support = example["features_by_support"]
        for support in example["all_pairs"]:
            label = "positive" if support in requested else "negative"
            totals[label] += 1
            for feature in features_by_support[support]:
                counts[feature][label] += 1
    positive = int(totals["positive"])
    negative = int(totals["negative"])
    base = math.log((positive + smoothing) / (negative + smoothing))
    weights = {
        feature: math.log((counter["positive"] + smoothing) / (counter["negative"] + smoothing))
        for feature, counter in counts.items()
    }
    ranked = sorted(weights.items(), key=lambda item: item[1])
    return {
        "base_log_odds": base,
        "feature_count": len(weights),
        "negative_examples": negative,
        "positive_examples": positive,
        "smoothing": float(smoothing),
        "top_negative_features": [{"feature": key, "weight": round(value, 8)} for key, value in ranked[:8]],
        "top_positive_features": [{"feature": key, "weight": round(value, 8)} for key, value in reversed(ranked[-8:])],
        "weights": weights,
    }


def score_support(features: tuple[str, ...], model: dict[str, Any]) -> float:
    score = float(model["base_log_odds"])
    weights = model["weights"]
    for feature in features:
        score += float(weights.get(feature, 0.0))
    return score


def select_model_supports(example: dict[str, Any], model: dict[str, Any], count: int) -> set[tuple[int, int]]:
    ranked = sorted(
        example["all_pairs"],
        key=lambda support: (-score_support(example["features_by_support"][support], model), support[0], support[1]),
    )
    return set(ranked[: max(0, min(int(count), len(ranked)))])


def overlap_row(
    selected: set[tuple[int, int]],
    requested: set[tuple[int, int]],
    all_pairs: list[tuple[int, int]],
) -> dict[str, Any]:
    overlap = len(selected & requested)
    union = len(selected | requested)
    return {
        "jaccard_with_requested": ratio(overlap, union),
        "overlap_count": overlap,
        "overlap_over_requested": ratio(overlap, len(requested)),
        "requested_count": len(requested),
        "selected_count": len(selected),
        "universe_count": len(all_pairs),
    }


def compact_model(model: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in model.items() if key != "weights"}


def feature_scope(family: str) -> str:
    if family == PUBLIC_STATIC:
        return "PUBLIC-STATIC"
    if family == CALIBRATION_TRACE:
        return "CALIBRATION-DERIVED-NONPUBLIC"
    if family == COMBINED:
        return "DIAGNOSTIC-MIXED"
    if family == TRACE_RANK:
        return "CALIBRATION-DERIVED-NONPUBLIC"
    return "UNKNOWN"


def aggregate_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["family"], row["protocol"], int(row["support_budget"]))].append(row)
    out = []
    for (family, protocol, budget), items in sorted(grouped.items()):
        out.append(
            {
                "family": family,
                "protocol": protocol,
                "scope": feature_scope(family),
                "support_budget": int(budget),
                "jaccard_with_requested": stat([float(item["jaccard_with_requested"] or 0.0) for item in items]),
                "overlap_over_requested": stat([float(item["overlap_over_requested"] or 0.0) for item in items]),
                "overlap_count": stat([float(item["overlap_count"]) for item in items]),
            }
        )
    return out


def best_row(rows: list[dict[str, Any]], family: str, protocol: str) -> dict[str, Any] | None:
    candidates = [row for row in rows if row["family"] == family and row["protocol"] == protocol]
    if not candidates:
        return None
    return max(
        candidates,
        key=lambda row: (
            float(row["overlap_over_requested"] or 0.0),
            float(row["jaccard_with_requested"] or 0.0),
            int(row["overlap_count"]),
        ),
    )


def min_row(rows: list[dict[str, Any]], family: str, protocol: str) -> dict[str, Any] | None:
    candidates = [row for row in rows if row["family"] == family and row["protocol"] == protocol]
    if not candidates:
        return None
    return min(
        candidates,
        key=lambda row: (
            float(row["overlap_over_requested"] or 0.0),
            float(row["jaccard_with_requested"] or 0.0),
            int(row["overlap_count"]),
        ),
    )


def determine_claim(rows: list[dict[str, Any]]) -> str:
    public_cross = best_row(rows, PUBLIC_STATIC, "cross_target_logodds")
    trace_projection_min = min_row(rows, TRACE_RANK, "exact_line_rank_projection")
    trace_support_best = best_row(rows, TRACE_RANK, "support_aggregate_rank")
    public_overlap = 0.0 if public_cross is None else float(public_cross["overlap_over_requested"] or 0.0)
    if public_overlap >= 0.80:
        return "P808_PUBLIC_STATIC_INVARIANT_CANDIDATE_READY_FOR_CHARGED_SCAN"
    if trace_projection_min is not None and float(trace_projection_min["overlap_over_requested"] or 0.0) >= 0.999:
        if trace_support_best is not None and float(trace_support_best["overlap_over_requested"] or 0.0) >= 0.80:
            return "P808_CALIBRATION_TRACE_RANK_EXPLAINS_REQUESTED_SUPPORT_SIGNAL"
        return "P808_LINE_RANK_PROJECTION_EXPLAINS_REQUESTED_LINES_NOT_SUPPORTS"
    return "P808_NO_COMPACT_INVARIANT_FOUND"


def load_research_stack(p806: Any) -> dict[str, Any]:
    p801 = p806.load_module("ecdlp_p801_for_p808", p806.P801_SCRIPT)
    p800 = p801.load_module("ecdlp_p800_for_p808", p801.P800_SCRIPT)
    p799 = p800.load_module("ecdlp_p799_for_p808", p800.P799_SCRIPT)
    p798 = p799.load_module("ecdlp_p798_for_p808", p799.P798_SCRIPT)
    p797 = p798.load_module("ecdlp_p797_for_p808", p798.P797_SCRIPT)
    p796 = p797.load_module("ecdlp_p796_for_p808", p797.P796_SCRIPT)
    p795 = p796.load_module("ecdlp_p795_for_p808", p796.P795_SCRIPT)
    p794 = p795.load_module("ecdlp_p794_for_p808", p795.P794_SCRIPT)
    p793 = p794.load_module("ecdlp_p793_for_p808", p794.P793_SCRIPT)
    p792 = p793.load_module("ecdlp_p792_for_p808", p793.P792_SCRIPT)
    p789 = p792.load_module("ecdlp_p789_for_p808", p792.P789_SCRIPT)
    p788 = p789.load_module("ecdlp_p788_for_p808", p789.P788_SCRIPT)
    p787 = p788.load_module("ecdlp_p787_for_p808", p788.P787_SCRIPT)
    p786 = p787.load_module("ecdlp_p786_for_p808", p787.P786_SCRIPT)
    p784 = p786.load_module("ecdlp_p784_for_p808", p786.P784_SCRIPT)
    p782 = p784.load_module("ecdlp_p782_for_p808", p784.P782_SCRIPT)
    p780 = p782.load_module("ecdlp_p780_for_p808", p782.P780_SCRIPT)
    stack = p780.load_stack()
    return {
        "p801": p801,
        "p784": p784,
        "p787": p787,
        "p788": p788,
        "p794": p794,
        "p795": p795,
        "p793": p793,
        "p792": p792,
        "p789": p789,
        "stack": stack,
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    if int(args.width) != 2:
        raise ValueError("P808 mines width-2 support-pair invariants; use --width 2")
    p806 = load_module("ecdlp_p806_for_p808", P806_SCRIPT)
    p807 = load_module("ecdlp_p807_for_p808", P807_SCRIPT)
    p807.configure_p807(p806)
    modules = load_research_stack(p806)
    p801 = modules["p801"]
    p784 = modules["p784"]
    p787 = modules["p787"]
    p788 = modules["p788"]
    p794 = modules["p794"]
    p795 = modules["p795"]
    p793 = modules["p793"]
    p792 = modules["p792"]
    p789 = modules["p789"]
    stack = modules["stack"]
    p746 = stack["p746"]
    relprobe = stack["relprobe"]

    frozen_pairs = p788.selected_frozen_pairs(p787, args.p786_summary)
    required = sorted({item["dest_group_key"] for item in frozen_pairs})
    base_groups = p784.normalized_groups(args.p777_summary, required)
    support_budgets = csv_ints(args.support_budgets)
    namespaces = csv_strings(args.constructor_namespaces)

    train_args = p795.namespace_args(args, args.train_seed_namespace, int(args.train_replicas))
    train_prepared = {}
    for group_key in required:
        print(f"preparing train namespace {args.train_seed_namespace} group={group_key}", flush=True)
        train_prepared[group_key] = p794.prepare_target(
            p793,
            p792,
            p789,
            p787,
            p784,
            stack,
            base_groups[group_key],
            train_args,
        )
    trained_by_group_support = {
        group_key: {
            int(budget): p794.selected_calibrations(train_prepared[group_key]["all_calibrated"], int(budget))
            for budget in support_budgets
        }
        for group_key in required
    }

    contexts = {}
    for namespace in namespaces:
        for group_key in required:
            print(f"building public context namespace={namespace} group={group_key}", flush=True)
            contexts[(namespace, group_key)] = p806.build_public_context(
                p801,
                p746,
                relprobe,
                base_groups[group_key],
                trained_by_group_support[group_key],
                support_budgets,
                namespace,
                args,
            )

    trace_features_by_group = {}
    trace_grouped_by_group = {}
    for group_key in required:
        reference_context = contexts[(namespaces[0], group_key)]
        features, grouped = build_trace_features(
            reference_context["all_pairs"],
            train_prepared[group_key]["all_calibrated"],
            int(reference_context["order"]),
            int(args.feature_bins),
        )
        trace_features_by_group[group_key] = features
        trace_grouped_by_group[group_key] = grouped

    examples_by_family = {}
    for namespace in namespaces:
        for group_key in required:
            context = contexts[(namespace, group_key)]
            all_pairs = [canonical_support(support) for support in context["all_pairs"]]
            public_features = {canonical_support(key): tuple(value) for key, value in context["features_by_support"].items()}
            trace_features = trace_features_by_group[group_key]
            combined_features = {
                support: tuple(public_features[support]) + tuple(trace_features[support])
                for support in all_pairs
            }
            for budget in support_budgets:
                requested = p806.requested_supports(p801, trained_by_group_support[group_key], int(budget))
                examples_by_family[(namespace, group_key, int(budget), PUBLIC_STATIC)] = {
                    "all_pairs": all_pairs,
                    "features_by_support": public_features,
                    "requested": requested,
                }
                examples_by_family[(namespace, group_key, int(budget), CALIBRATION_TRACE)] = {
                    "all_pairs": all_pairs,
                    "features_by_support": trace_features,
                    "requested": requested,
                }
                examples_by_family[(namespace, group_key, int(budget), COMBINED)] = {
                    "all_pairs": all_pairs,
                    "features_by_support": combined_features,
                    "requested": requested,
                }

    overlap_rows = []
    model_rows = []
    for namespace in namespaces:
        for group_key in required:
            for budget in support_budgets:
                current_requested = examples_by_family[(namespace, group_key, int(budget), PUBLIC_STATIC)]["requested"]
                all_pairs = examples_by_family[(namespace, group_key, int(budget), PUBLIC_STATIC)]["all_pairs"]
                exact_projection = trace_rank_projection_supports(train_prepared[group_key]["all_calibrated"], int(budget))
                support_rank = trace_support_rank_supports(trace_grouped_by_group[group_key], len(current_requested))
                for protocol, selected in (
                    ("exact_line_rank_projection", exact_projection),
                    ("support_aggregate_rank", support_rank),
                ):
                    row = {
                        **overlap_row(selected, current_requested, all_pairs),
                        "family": TRACE_RANK,
                        "group_key": group_key,
                        "namespace": namespace,
                        "protocol": protocol,
                        "scope": feature_scope(TRACE_RANK),
                        "support_budget": int(budget),
                    }
                    overlap_rows.append(row)

                for family in FAMILIES:
                    current = examples_by_family[(namespace, group_key, int(budget), family)]
                    same_model = train_logodds_model([current], float(args.logodds_smoothing))
                    same_selected = select_model_supports(current, same_model, len(current_requested))
                    same_row = {
                        **overlap_row(same_selected, current_requested, all_pairs),
                        "family": family,
                        "group_key": group_key,
                        "namespace": namespace,
                        "protocol": "same_target_logodds_upper",
                        "scope": feature_scope(family),
                        "support_budget": int(budget),
                    }
                    overlap_rows.append(same_row)
                    model_rows.append(
                        {
                            "family": family,
                            "group_key": group_key,
                            "model": "same_target_logodds_upper",
                            "namespace": namespace,
                            "scope": feature_scope(family),
                            "support_budget": int(budget),
                            **compact_model(same_model),
                        }
                    )

                    cross_examples = [
                        examples_by_family[(namespace, other_group, int(budget), family)]
                        for other_group in required
                        if other_group != group_key
                    ]
                    cross_model = train_logodds_model(cross_examples, float(args.logodds_smoothing))
                    cross_selected = select_model_supports(current, cross_model, len(current_requested))
                    cross_row = {
                        **overlap_row(cross_selected, current_requested, all_pairs),
                        "family": family,
                        "group_key": group_key,
                        "namespace": namespace,
                        "protocol": "cross_target_logodds",
                        "scope": feature_scope(family),
                        "support_budget": int(budget),
                    }
                    overlap_rows.append(cross_row)
                    model_rows.append(
                        {
                            "family": family,
                            "group_key": group_key,
                            "model": "cross_target_logodds",
                            "namespace": namespace,
                            "scope": feature_scope(family),
                            "support_budget": int(budget),
                            **compact_model(cross_model),
                        }
                    )

    summary = {
        "aggregate_overlap": aggregate_rows(overlap_rows),
        "best_calibration_trace_cross_target": best_row(overlap_rows, CALIBRATION_TRACE, "cross_target_logodds"),
        "best_calibration_trace_same_target": best_row(overlap_rows, CALIBRATION_TRACE, "same_target_logodds_upper"),
        "best_public_static_cross_target": best_row(overlap_rows, PUBLIC_STATIC, "cross_target_logodds"),
        "best_public_static_same_target": best_row(overlap_rows, PUBLIC_STATIC, "same_target_logodds_upper"),
        "best_trace_support_rank": best_row(overlap_rows, TRACE_RANK, "support_aggregate_rank"),
        "constructor_namespaces": namespaces,
        "feature_bins": int(args.feature_bins),
        "model_rows": model_rows,
        "overlap_rows": overlap_rows,
        "support_budgets": support_budgets,
        "target_groups": required,
        "trace_projection_min": min_row(overlap_rows, TRACE_RANK, "exact_line_rank_projection"),
        "train_seed_namespace": args.train_seed_namespace,
    }
    claim_status = determine_claim(overlap_rows)
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p777_summary": str(args.p777_summary),
            "p786_summary": str(args.p786_summary),
            "p806_script": str(P806_SCRIPT),
            "p807_script": str(P807_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": claim_status,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "PUBLIC-STATIC TRACK: P807 rich factor-base geometry features are public but previously failed row-recovery charging.",
            "CALIBRATION-TRACE TRACK: candidate row counts, line keys, line values, rhs, scale, replica, and row indices come from training calibration traces and are not a standalone public derivation method.",
            "SUPPORT-SET ONLY: P808 measures support-set reconstruction and invariant separability; it does not claim recovered rows or a faster-than-rho ECDLP solver.",
            "CHARGING RULE: only a public-static or public target-conditioned candidate reaching high cross-target support overlap should be promoted to a charged P801/P804/P807 row scan.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p808_requested_support_invariant_miner",
        "parameters": {
            "constructor_namespaces": namespaces,
            "feature_bins": int(args.feature_bins),
            "logodds_smoothing": float(args.logodds_smoothing),
            "min_line_rows": int(args.min_line_rows),
            "row_policy": args.row_policy,
            "sparse_policies": args.sparse_policies,
            "support_budgets": support_budgets,
            "train_replicas": int(args.train_replicas),
            "train_seed_namespace": args.train_seed_namespace,
            "walk_mode": args.walk_mode,
            "width": int(args.width),
        },
        "schema": SCHEMA,
        "summary": summary,
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        **payload,
        "schema": f"{SCHEMA}.summary",
        "summary": {
            **payload["summary"],
            "model_rows": [
                {
                    key: value
                    for key, value in row.items()
                    if key not in {"top_negative_features", "top_positive_features"}
                }
                for row in payload["summary"]["model_rows"]
            ],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p777-summary", type=Path, default=DEFAULT_P777_SUMMARY)
    parser.add_argument("--p786-summary", type=Path, default=DEFAULT_P786_SUMMARY)
    parser.add_argument("--train-seed-namespace", default="supportline20-v1")
    parser.add_argument("--constructor-namespaces", default="prehitpair-p807-rich-v14,prehitpair-p807-rich-v15,prehitpair-p807-rich-v16")
    parser.add_argument("--support-budgets", default="128,256,512")
    parser.add_argument("--train-replicas", type=int, default=20)
    parser.add_argument("--feature-bins", type=int, default=8)
    parser.add_argument("--logodds-smoothing", type=float, default=1.0)
    parser.add_argument("--min-line-rows", type=int, default=2)
    parser.add_argument("--row-policy", default="sequential_min_forms_ge_1")
    parser.add_argument("--sparse-policies", default="natural,support_asc,support_span_asc,pivot_low,pivot_high,coefficient_weight_asc")
    parser.add_argument("--width", type=int, default=2)
    parser.add_argument("--walk-mode", default="hash6")
    parser.add_argument("--max-relations", type=int, default=96)
    parser.add_argument("--max-subsets", type=int, default=25000)
    parser.add_argument("--control-count", type=int, default=8)
    parser.add_argument("--field-weight", type=int, default=2)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--summary-out", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary_out = args.summary_out or args.out.with_name(args.out.stem.replace("_probe", "_summary") + args.out.suffix)
    summary = summary_from_payload(payload)
    write_json(summary_out, summary)
    print(f"wrote {args.out}")
    print(f"wrote {summary_out}")
    print(
        json.dumps(
            {
                "best_calibration_trace_cross_target": summary["summary"]["best_calibration_trace_cross_target"],
                "best_public_static_cross_target": summary["summary"]["best_public_static_cross_target"],
                "best_trace_support_rank": summary["summary"]["best_trace_support_rank"],
                "claim_status": summary["claim_status"],
                "trace_projection_min": summary["summary"]["trace_projection_min"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
