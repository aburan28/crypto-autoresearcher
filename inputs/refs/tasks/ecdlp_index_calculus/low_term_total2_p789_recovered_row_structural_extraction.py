#!/usr/bin/env python3
"""P789 structural extraction for the P788 recovered rows."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P788_SCRIPT = TASK_DIR / "low_term_total2_p788_affine_false_positive_audit.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p789_recovered_row_structural_extraction_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p789_recovered_row_structural_extraction.md"
SCHEMA = "ecdlp.low_term_total2_p789_recovered_row_structural_extraction.v1"


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


def stat(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "min": None}
    return {"count": len(values), "max": max(values), "mean": round(mean(values), 8), "min": min(values)}


def csv_strings(text: str) -> list[str]:
    return [item.strip() for item in text.split(",") if item.strip()]


def csv_ints(text: str) -> list[int]:
    return [int(item.strip()) for item in text.split(",") if item.strip()]


def namespace_args(args: argparse.Namespace, seed_namespace: str) -> argparse.Namespace:
    values = vars(args).copy()
    values["seed_namespace"] = seed_namespace
    return argparse.Namespace(**values)


def tuple_key(values: list[int] | tuple[int, ...]) -> str:
    if not values:
        return "empty"
    return ",".join(str(int(value)) for value in values)


def bucket(value: int | None, width: int) -> str:
    if value is None:
        return "none"
    return str(int(value) // width)


def seed_index(seed_label: str) -> int | None:
    match = re.search(r"(\d+)$", str(seed_label))
    if not match:
        return None
    return int(match.group(1))


def point_map(factor_base: dict[str, Any]) -> dict[int, dict[str, int]]:
    return {int(point["index"]): {"x": int(point["x"]), "y": int(point["y"])} for point in factor_base["points"]}


def form_coeffs(form: dict[str, Any], order: int) -> list[int]:
    return [int(value) % order for value in form.get("coeffs") or []]


def form_support(coeffs: list[int], order: int) -> list[int]:
    return [index for index, coeff in enumerate(coeffs[1:]) if int(coeff) % order]


def supported_form(form: dict[str, Any], mapped_dest_indices: set[int], order: int) -> bool:
    coeffs = form_coeffs(form, order)
    if not coeffs or not coeffs[0]:
        return False
    return all((not coeff) or factor_index in mapped_dest_indices for factor_index, coeff in enumerate(coeffs[1:]))


def supported_forms(row: dict[str, Any], mapped_dest_indices: set[int], order: int) -> list[tuple[int, dict[str, Any]]]:
    return [
        (index, form)
        for index, form in enumerate(row.get("forms") or [])
        if supported_form(form, mapped_dest_indices, order)
    ]


def recover_from_form(
    row: dict[str, Any],
    form: dict[str, Any],
    factor_values: dict[int, int],
    order: int,
) -> dict[str, Any]:
    coeffs = form_coeffs(form, order)
    support = form_support(coeffs, order)
    acc = int(form["rhs"]) % order
    ops = {
        "field_additions": 0,
        "field_inversions": 0,
        "field_multiplications": 0,
        "relations_considered": 1,
        "total_field_ops": 0,
    }
    for factor_index in support:
        coeff = coeffs[1 + factor_index] % order
        acc = (acc - coeff * int(factor_values[factor_index])) % order
        ops["field_multiplications"] += 1
        ops["field_additions"] += 1
    secret = (acc * pow(coeffs[0] % order, -1, order)) % order
    ops["field_inversions"] += 1
    ops["field_multiplications"] += 1
    ops["total_field_ops"] = ops["field_inversions"] + ops["field_multiplications"] + ops["field_additions"]
    expected = int(row["_expected_secret"]) % order
    return {
        "expected_secret": int(expected),
        "matches_expected": secret == expected,
        "operation_counts": ops,
        "recovered_secret": int(secret),
        "secret_delta": int((secret - expected) % order),
        "support": support,
    }


def mod_features(features: dict[str, str], prefix: str, value: int | None, moduli: list[int]) -> None:
    if value is None:
        return
    for modulus in moduli:
        features[f"{prefix}_mod_{modulus}"] = str(int(value) % modulus)


def row_feature_record(
    row: dict[str, Any],
    order: int,
    pair_key: str,
    replica: int,
    row_index: int,
    form_index: int,
    form: dict[str, Any],
    recovery: dict[str, Any],
    source_by_index: dict[int, dict[str, int]],
    dest_by_index: dict[int, dict[str, int]],
    dest_to_source: dict[int, int],
    anchor_dest_indices: set[int],
) -> dict[str, Any]:
    support = [int(index) for index in recovery["support"]]
    source_support = [int(dest_to_source[index]) for index in support]
    coeffs = form_coeffs(form, order)
    factor_coeffs = [coeffs[1 + index] % order for index in support]
    dest_x = [dest_by_index[index]["x"] for index in support]
    dest_y = [dest_by_index[index]["y"] for index in support]
    source_x = [source_by_index[index]["x"] for index in source_support]
    source_y = [source_by_index[index]["y"] for index in source_support]
    seed_ord = seed_index(str(row.get("seed_label")))
    support_span = max(support) - min(support) if support else None
    source_span = max(source_support) - min(source_support) if source_support else None
    dest_x_span = max(dest_x) - min(dest_x) if dest_x else None
    source_x_span = max(source_x) - min(source_x) if source_x else None
    public_features: dict[str, str] = {
        "chosen_form_index": str(form_index),
        "dest_index_parity_pattern": tuple_key([value % 2 for value in support]),
        "dest_y_parity_pattern": tuple_key([value % 2 for value in dest_y]),
        "eligible_form_count": str(len(supported_forms(row, set(dest_to_source), order))),
        "factor_coeff_abs_bucket_8": bucket(sum(min(value, order - value) for value in factor_coeffs), 8),
        "factor_coeff_parity_pattern": tuple_key([value % 2 for value in factor_coeffs]),
        "form_count": str(len(row.get("forms") or [])),
        "map_pair": pair_key,
        "online_additions_bucket_16": bucket(
            int((row.get("cost_model") or {}).get("collection_online_group_additions") or 0),
            16,
        ),
        "q_coeff_mod_2": str(coeffs[0] % 2),
        "source_index_parity_pattern": tuple_key([value % 2 for value in source_support]),
        "source_y_parity_pattern": tuple_key([value % 2 for value in source_y]),
        "support_max_bucket_8": bucket(max(support) if support else None, 8),
        "support_min_bucket_8": bucket(min(support) if support else None, 8),
        "support_size": str(len(support)),
        "support_span_bucket_8": bucket(support_span, 8),
        "target": str(row.get("target")),
    }
    if len(support) == 2:
        public_features["dest_gap_exact"] = str(abs(support[1] - support[0]))
        public_features["dest_gap_bucket_8"] = bucket(abs(support[1] - support[0]), 8)
        public_features["source_gap_bucket_8"] = bucket(abs(source_support[1] - source_support[0]), 8)
        public_features["dest_x_gap_bucket_64"] = bucket(abs(dest_x[1] - dest_x[0]), 64)
        public_features["source_x_gap_bucket_64"] = bucket(abs(source_x[1] - source_x[0]), 64)
    if seed_ord is not None:
        mod_features(public_features, "seed_index", seed_ord, [2, 3, 5, 7, 11])
    mod_features(public_features, "support_sum", sum(support), [3, 5, 7, 11])
    mod_features(public_features, "source_support_sum", sum(source_support), [3, 5, 7, 11])
    mod_features(public_features, "dest_x_sum", sum(dest_x), [3, 5, 7, 11])
    mod_features(public_features, "source_x_sum", sum(source_x), [3, 5, 7, 11])
    if support_span is not None:
        mod_features(public_features, "support_span", support_span, [3, 5, 7])
    if source_span is not None:
        mod_features(public_features, "source_span", source_span, [3, 5, 7])
    if dest_x_span is not None:
        mod_features(public_features, "dest_x_span", dest_x_span, [3, 5, 7, 11])
    if source_x_span is not None:
        mod_features(public_features, "source_x_span", source_x_span, [3, 5, 7, 11])

    parity_pairs = [f"{left % 2}->{right % 2}" for left, right in zip(source_y, dest_y)]
    public_features["source_dest_y_parity_pairs"] = tuple_key([int(pair.replace("->", "")) for pair in parity_pairs])
    public_features["source_dest_y_parity_same_count"] = str(
        sum(1 for left, right in zip(source_y, dest_y) if left % 2 == right % 2)
    )

    anchor_overlap = sorted(set(support) & anchor_dest_indices)
    private_fit_features = {
        "anchor_overlap_count": str(len(anchor_overlap)),
        "anchor_overlap_tuple": tuple_key(anchor_overlap),
        "has_anchor_dest": str(bool(anchor_overlap)).lower(),
        "support_is_anchor_subset": str(bool(support) and set(support) <= anchor_dest_indices).lower(),
    }

    return {
        "chosen_form_index": int(form_index),
        "dest_support": support,
        "expected_secret": int(recovery["expected_secret"]),
        "matches_expected": bool(recovery["matches_expected"]),
        "operation_counts": recovery["operation_counts"],
        "order": int(order),
        "pair_key": pair_key,
        "private_fit_features": private_fit_features,
        "public_features": public_features,
        "recovered_secret": recovery["recovered_secret"],
        "replica": int(replica),
        "row_index": int(row_index),
        "secret_delta": int(recovery["secret_delta"]),
        "seed_label": str(row.get("seed_label")),
        "source_support": source_support,
        "support_pair_sample": [
            {
                "anchor_dest": index in anchor_dest_indices,
                "dest": index,
                "dest_x": dest_by_index[index]["x"],
                "dest_y_parity": dest_by_index[index]["y"] % 2,
                "source": int(dest_to_source[index]),
                "source_x": source_by_index[int(dest_to_source[index])]["x"],
                "source_y_parity": source_by_index[int(dest_to_source[index])]["y"] % 2,
            }
            for index in support[:8]
        ],
        "target": str(row.get("target")),
    }


def evaluate_rows(
    rows: list[dict[str, Any]],
    order: int,
    factor_values: dict[int, int],
    pair_key: str,
    replica: int,
    source_by_index: dict[int, dict[str, int]],
    dest_by_index: dict[int, dict[str, int]],
    dest_to_source: dict[int, int],
    anchor_dest_indices: set[int],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    mapped_dest_indices = set(factor_values)
    records = []
    ops = Counter()
    for row_index, row in enumerate(rows):
        supported = supported_forms(row, mapped_dest_indices, order)
        if not supported:
            continue
        form_index, form = supported[0]
        recovery = recover_from_form(row, form, factor_values, order)
        records.append(
            row_feature_record(
                row,
                order,
                pair_key,
                replica,
                row_index,
                form_index,
                form,
                recovery,
                source_by_index,
                dest_by_index,
                dest_to_source,
                anchor_dest_indices,
            )
        )
        ops.update(recovery["operation_counts"])
    ops["total_field_ops"] = ops["field_inversions"] + ops["field_multiplications"] + ops["field_additions"]
    return records, dict(ops)


def hypergeom_tail(population: int, successes: int, draws: int, observed: int) -> float | None:
    if population <= 0 or successes < 0 or draws < 0 or observed < 0:
        return None
    if observed > successes or observed > draws:
        return 0.0
    denominator = math.comb(population, draws)
    if denominator == 0:
        return None
    upper = min(successes, draws)
    total = 0
    for value in range(observed, upper + 1):
        if draws - value > population - successes:
            continue
        total += math.comb(successes, value) * math.comb(population - successes, draws - value)
    return round(total / denominator, 12)


def predicate_surface(
    records: list[dict[str, Any]],
    feature_key: str,
    min_support: int,
    min_hits: int,
    min_lift: float,
) -> dict[str, Any]:
    total = len(records)
    recovered_total = sum(1 for record in records if record["matches_expected"])
    global_rate = recovered_total / total if total else 0.0
    buckets: dict[tuple[str, str], dict[str, Any]] = defaultdict(
        lambda: {"examples": [], "recovered": 0, "total": 0}
    )
    for record in records:
        for name, value in (record.get(feature_key) or {}).items():
            key = (str(name), str(value))
            buckets[key]["total"] += 1
            if record["matches_expected"]:
                buckets[key]["recovered"] += 1
                if len(buckets[key]["examples"]) < 8:
                    buckets[key]["examples"].append(
                        {
                            "pair_key": record["pair_key"],
                            "recovered_secret": record["recovered_secret"],
                            "replica": record["replica"],
                            "seed_label": record["seed_label"],
                            "support": record["dest_support"],
                            "target": record["target"],
                        }
                    )
    predicates = []
    for (name, value), item in buckets.items():
        support = int(item["total"])
        recovered = int(item["recovered"])
        if support < min_support or recovered == 0:
            continue
        rate = recovered / support
        lift = (rate / global_rate) if global_rate else None
        predicate = {
            "expected_hits_at_global_rate": round(support * global_rate, 8),
            "feature": name,
            "hypergeom_tail_p": hypergeom_tail(total, recovered_total, support, recovered),
            "lift_over_global_rate": round(lift, 8) if lift is not None else None,
            "predicate": f"{name} == {value}",
            "recovered_count": recovered,
            "recovered_examples": item["examples"],
            "recovered_rate": round(rate, 8),
            "support": support,
            "value": value,
        }
        predicate["passes_threshold"] = bool(
            recovered >= min_hits and lift is not None and lift >= min_lift
        )
        predicates.append(predicate)
    predicates.sort(
        key=lambda item: (
            bool(item["passes_threshold"]),
            int(item["recovered_count"]),
            float(item.get("lift_over_global_rate") or 0.0),
            -int(item["support"]),
        ),
        reverse=True,
    )
    return {
        "global_recovered_count": recovered_total,
        "global_recovered_rate": ratio(recovered_total, total),
        "min_lift": min_lift,
        "min_predicate_hits": min_hits,
        "min_predicate_support": min_support,
        "passing_count": sum(1 for item in predicates if item["passes_threshold"]),
        "top_predicates": predicates[:40],
    }


def anchor_confound_report(records: list[dict[str, Any]]) -> dict[str, Any]:
    anchor_records = [
        record
        for record in records
        if (record.get("private_fit_features") or {}).get("has_anchor_dest") == "true"
    ]
    non_anchor_records = [
        record
        for record in records
        if (record.get("private_fit_features") or {}).get("has_anchor_dest") != "true"
    ]
    recovered_records = [record for record in records if record["matches_expected"]]
    anchor_recovered = [record for record in anchor_records if record["matches_expected"]]
    non_anchor_recovered = [record for record in non_anchor_records if record["matches_expected"]]
    return {
        "anchor_record_count": len(anchor_records),
        "anchor_recovered_count": len(anchor_recovered),
        "anchor_recovered_rate": ratio(len(anchor_recovered), len(anchor_records)),
        "all_recovered_rows_have_anchor": bool(recovered_records) and len(anchor_recovered) == len(recovered_records),
        "non_anchor_record_count": len(non_anchor_records),
        "non_anchor_recovered_count": len(non_anchor_recovered),
        "non_anchor_recovered_rate": ratio(len(non_anchor_recovered), len(non_anchor_records)),
        "recovered_row_count": len(recovered_records),
    }


def aggregate_records(records: list[dict[str, Any]], expected_random: float = 0.0) -> dict[str, Any]:
    recovered = sum(1 for record in records if record["matches_expected"])
    total_ops = Counter()
    for record in records:
        total_ops.update(record.get("operation_counts") or {})
    total_ops["total_field_ops"] = (
        total_ops["field_inversions"] + total_ops["field_multiplications"] + total_ops["field_additions"]
    )
    return {
        "eligible_target_count": len(records),
        "expected_random_recovered": round(expected_random, 8),
        "operation_counts": dict(total_ops),
        "transfer_mismatch_count": len(records) - recovered,
        "transfer_recovered_count": recovered,
        "transfer_recovered_rate": ratio(recovered, len(records)),
    }


def evaluate_pair(
    p784: Any,
    p786: Any,
    p787: Any,
    stack: dict[str, Any],
    base_groups: dict[str, dict[str, Any]],
    frozen: dict[str, Any],
    args: argparse.Namespace,
) -> dict[str, Any]:
    source_item = base_groups[frozen["source_group_key"]]
    dest_item = base_groups[frozen["dest_group_key"]]
    pair_key = f"{frozen['source_group_key']}->{frozen['dest_group_key']}"
    source_args = namespace_args(args, args.source_fit_seed_namespace)
    source_solve = p786.selected_case(p784, stack, source_item, "source", source_args)
    source_fb = p786.public_factor_base(stack, str(source_item["target"]), int(source_item["factor_base_size"]))
    dest_fb = p786.public_factor_base(stack, str(dest_item["target"]), int(dest_item["factor_base_size"]))
    dest_order = int(dest_fb["base_order"])
    source_values = p786.normalized_factor_values(source_solve["factor_values"], dest_order)
    public_map = p787.find_public_map(p786, source_fb, dest_fb, frozen["fit_map_kind"])
    factor_values = p786.mapped_factor_values(
        public_map["mapping"],
        source_values,
        dest_order,
        frozen["fit_transform"],
    )
    dest_to_source = {int(dest): int(source) for source, dest in public_map["mapping"].items()}
    source_by_index = point_map(source_fb)
    dest_by_index = point_map(dest_fb)
    anchor_dest_indices = {int(item["dest"]) for item in frozen["fit_transform"].get("anchor_pairs") or []}

    replica_results = []
    all_records = []
    expected_random = 0.0
    for replica in range(int(args.replicas)):
        dest_case = p787.destination_case(p784, dest_item, args.eval_seed_namespace, replica)
        rows, order = p784.collect_destination(stack, dest_case, args)
        records, ops = evaluate_rows(
            rows,
            order,
            factor_values,
            pair_key,
            replica,
            source_by_index,
            dest_by_index,
            dest_to_source,
            anchor_dest_indices,
        )
        all_records.extend(records)
        expected_random += len(records) / order if order else 0.0
        replica_results.append(
            {
                "aggregate": aggregate_records(records, len(records) / order if order else 0.0),
                "dest_case": dest_case,
                "dest_rows_available": len(rows),
                "operation_counts": ops,
                "recovered_rows": [record for record in records if record["matches_expected"]],
                "replica": replica,
            }
        )

    return {
        "aggregate": aggregate_records(all_records, expected_random),
        "anchor_dest_indices": sorted(anchor_dest_indices),
        "dest_group_key": frozen["dest_group_key"],
        "dest_target": frozen["dest_target"],
        "fit_map_kind": frozen["fit_map_kind"],
        "fit_recovered_count": frozen["fit_recovered_count"],
        "fit_transform": frozen["fit_transform"],
        "frozen_map": {key: value for key, value in public_map.items() if key != "mapping"},
        "pair_key": pair_key,
        "records": all_records,
        "replicas": replica_results,
        "source_control_ok": bool(source_solve["control_ok"]),
        "source_group_key": frozen["source_group_key"],
        "source_selected_strict_pass": bool(source_solve["selected_strict_pass"]),
        "source_solve": p786.summarize_solve(source_solve),
        "source_target": frozen["source_target"],
    }


def determine_claim(summary: dict[str, Any]) -> str:
    if not summary["positive_control"]["p788_primary_replay_ok"]:
        return "NEGATIVE_RESULT_P789_P788_REPLAY_CONTROL_FAILURE"
    public_pass = int(summary["public_predicate_surface"]["passing_count"])
    private_pass = int(summary["private_fit_predicate_surface"]["passing_count"])
    anchor_confound = summary["anchor_confound"]
    if public_pass and anchor_confound["all_recovered_rows_have_anchor"]:
        return "P789_PUBLIC_PREDICATES_ANCHOR_CONFOUNDED_MISMATCH_DOMINATED"
    if public_pass:
        return "P789_PUBLIC_ROW_STRUCTURE_ENRICHMENT_CANDIDATE_MISMATCH_DOMINATED"
    if private_pass:
        return "P789_PRIVATE_FIT_FEATURE_ENRICHMENT_ONLY_NO_PUBLIC_BRIDGE"
    return "NEGATIVE_RESULT_P789_NO_PUBLIC_ROW_STRUCTURE_ENRICHMENT"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p788 = load_module("ecdlp_p788_for_p789", P788_SCRIPT)
    p787 = p788.load_module("ecdlp_p787_for_p789", p788.P787_SCRIPT)
    p786 = p787.load_module("ecdlp_p786_for_p789", p787.P786_SCRIPT)
    p784 = p786.load_module("ecdlp_p784_for_p789", p786.P784_SCRIPT)
    p782 = p784.load_module("ecdlp_p782_for_p789", p784.P782_SCRIPT)
    p780 = p782.load_module("ecdlp_p780_for_p789", p782.P780_SCRIPT)
    stack = p780.load_stack()
    frozen_pairs = p788.selected_frozen_pairs(p787, args.p786_summary)
    required = sorted({key for item in frozen_pairs for key in [item["source_group_key"], item["dest_group_key"]]})
    base_groups = p784.normalized_groups(args.p777_summary, required)
    pair_results = [evaluate_pair(p784, p786, p787, stack, base_groups, frozen, args) for frozen in frozen_pairs]
    all_records = [record for pair in pair_results for record in pair["records"]]
    aggregate = aggregate_records(
        all_records,
        sum(float(pair["aggregate"].get("expected_random_recovered") or 0.0) for pair in pair_results),
    )
    public_surface = predicate_surface(
        all_records,
        "public_features",
        int(args.min_predicate_support),
        int(args.min_predicate_hits),
        float(args.min_lift),
    )
    private_surface = predicate_surface(
        all_records,
        "private_fit_features",
        int(args.min_predicate_support),
        int(args.min_predicate_hits),
        float(args.min_lift),
    )
    anchor_confound = anchor_confound_report(all_records)
    non_anchor_public_surface = predicate_surface(
        [
            record
            for record in all_records
            if (record.get("private_fit_features") or {}).get("has_anchor_dest") != "true"
        ],
        "public_features",
        int(args.min_predicate_support),
        int(args.min_predicate_hits),
        float(args.min_lift),
    )
    source_ok = (
        sum(1 for pair in pair_results if pair["source_control_ok"]) == len(pair_results)
        and sum(1 for pair in pair_results if pair["source_selected_strict_pass"]) == len(pair_results)
    )
    positive_control = {
        "expected_p788_primary_eligible": 1255,
        "expected_p788_primary_recovered": 4,
        "p788_primary_replay_ok": bool(
            int(args.replicas) == 5
            and args.eval_seed_namespace == "affineaudit-v1"
            and args.source_fit_seed_namespace == "coordbridge-v1"
            and aggregate["eligible_target_count"] == 1255
            and aggregate["transfer_recovered_count"] == 4
            and source_ok
        ),
        "source_controls_ok": source_ok,
    }
    recovered_rows = [record for record in all_records if record["matches_expected"]]
    summary = {
        "aggregate": aggregate,
        "anchor_confound": anchor_confound,
        "pair_count": len(pair_results),
        "pairs": [
            {
                "aggregate": pair["aggregate"],
                "anchor_dest_indices": pair["anchor_dest_indices"],
                "dest_group_key": pair["dest_group_key"],
                "fit_map_kind": pair["fit_map_kind"],
                "frozen_map": pair["frozen_map"],
                "pair_key": pair["pair_key"],
                "recovered_rows": [
                    record for replica in pair["replicas"] for record in replica["recovered_rows"]
                ],
                "replicas": [
                    {
                        "aggregate": replica["aggregate"],
                        "dest_rows_available": replica["dest_rows_available"],
                        "recovered_rows": replica["recovered_rows"],
                        "replica": replica["replica"],
                    }
                    for replica in pair["replicas"]
                ],
                "source_control_ok": pair["source_control_ok"],
                "source_selected_strict_pass": pair["source_selected_strict_pass"],
                "source_group_key": pair["source_group_key"],
            }
            for pair in pair_results
        ],
        "positive_control": positive_control,
        "private_fit_predicate_surface": private_surface,
        "public_predicate_surface_excluding_anchor_rows": non_anchor_public_surface,
        "public_predicate_surface": public_surface,
        "recovered_rows": recovered_rows,
        "replicas": int(args.replicas),
        "source_control_ok_count": sum(1 for pair in pair_results if pair["source_control_ok"]),
        "source_selected_strict_pass_count": sum(1 for pair in pair_results if pair["source_selected_strict_pass"]),
    }
    claim_status = determine_claim(summary)
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p777_summary": str(args.p777_summary),
            "p786_summary": str(args.p786_summary),
            "p788_script": str(P788_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": claim_status,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "REPLAY-AUDIT: P789 replays P788 deterministic row generation and does not fit new affine parameters on destination outcomes.",
            "PUBLIC-PREDICATE: public feature enrichment is separated from private-fit anchor features.",
            "MULTIPLE-TESTING: predicate enrichment is exploratory and requires fresh validation before promotion.",
            "MISMATCH-DOMINATED: exact hits are evaluated amid many false recoveries; this is not target descent.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p789_recovered_row_structural_extraction",
        "parameters": {
            "eval_seed_namespace": args.eval_seed_namespace,
            "field_weights": csv_ints(args.field_weights),
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "min_lift": args.min_lift,
            "min_predicate_hits": args.min_predicate_hits,
            "min_predicate_support": args.min_predicate_support,
            "public_substitution_ops_per_selected": args.public_substitution_ops_per_selected,
            "replicas": args.replicas,
            "row_policy": args.row_policy,
            "source_fit_seed_namespace": args.source_fit_seed_namespace,
            "sparse_policies": csv_strings(args.sparse_policies),
            "walk_mode": args.walk_mode,
            "width": args.width,
        },
        "row_records": all_records,
        "schema": SCHEMA,
        "summary": summary,
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifacts": payload["artifacts"],
        "claim_status": payload["claim_status"],
        "created_at": payload["created_at"],
        "honesty_boundary": payload["honesty_boundary"],
        "method": payload["method"],
        "parameters": payload["parameters"],
        "schema": f"{SCHEMA}.summary",
        "summary": payload["summary"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p777-summary", type=Path, default=DEFAULT_P777_SUMMARY)
    parser.add_argument("--p786-summary", type=Path, default=DEFAULT_P786_SUMMARY)
    parser.add_argument("--source-fit-seed-namespace", default="coordbridge-v1")
    parser.add_argument("--eval-seed-namespace", default="affineaudit-v1")
    parser.add_argument("--replicas", type=int, default=5)
    parser.add_argument("--row-policy", default="sequential_min_forms_ge_1")
    parser.add_argument("--sparse-policies", default="natural,support_asc,support_span_asc,pivot_low,pivot_high,coefficient_weight_asc")
    parser.add_argument("--width", type=int, default=2)
    parser.add_argument("--walk-mode", default="hash6")
    parser.add_argument("--max-relations", type=int, default=96)
    parser.add_argument("--max-subsets", type=int, default=25000)
    parser.add_argument("--field-weights", default="1,2")
    parser.add_argument("--public-substitution-ops-per-selected", type=int, default=6)
    parser.add_argument("--min-predicate-support", type=int, default=8)
    parser.add_argument("--min-predicate-hits", type=int, default=2)
    parser.add_argument("--min-lift", type=float, default=5.0)
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
                "aggregate": summary["summary"]["aggregate"],
                "anchor_confound": summary["summary"]["anchor_confound"],
                "claim_status": summary["claim_status"],
                "positive_control": summary["summary"]["positive_control"],
                "private_fit_passing_predicates": summary["summary"]["private_fit_predicate_surface"]["passing_count"],
                "public_passing_predicates_excluding_anchor_rows": summary["summary"][
                    "public_predicate_surface_excluding_anchor_rows"
                ]["passing_count"],
                "public_passing_predicates": summary["summary"]["public_predicate_surface"]["passing_count"],
                "top_public_predicates": summary["summary"]["public_predicate_surface"]["top_predicates"][:5],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
