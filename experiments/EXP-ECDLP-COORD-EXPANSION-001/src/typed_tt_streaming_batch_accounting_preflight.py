#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import time
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
STREAMING_SOURCE = SCRIPT_PATH.with_name("typed_tt_streaming_prefix_tradeoff_preflight.py")


def load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


STREAMING = load("typed_tt_streaming_for_batch_accounting", STREAMING_SOURCE)
ADAPTIVE = STREAMING.ADAPTIVE
ORACLE = STREAMING.ORACLE
TYPED_FIVE = STREAMING.TYPED_FIVE


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reset_prefix(advice: Any) -> None:
    advice.current_prefix_key = None
    advice.current_prefix = None


def target_pool(family: dict[str, Any]) -> tuple[list[tuple[str, list[int]]], list[tuple[str, list[int]]]]:
    relations = [(f"relation_{index}", item["target"]) for index, item in enumerate(family["relations"]["target_transcript"][:8])]
    held_out = [
        (f"held_out_supported_{index}", item["target"])
        for index, item in enumerate(family["held_out_descent"]["transcript"])
        if item["materialized_d4"]["success"] and item["r_scan_plus_d3"]["success"]
    ]
    return relations, held_out


def batch_specs(relations: list[tuple[str, list[int]]], held_out: list[tuple[str, list[int]]]) -> list[tuple[str, list[tuple[str, list[int]]]]]:
    specs = []
    for width in (1, 2, 4, 8):
        specs.append((f"balanced_{width}", relations[:width] + held_out[:width]))
    specs.append(("full", relations + held_out))
    return specs


def run_batch(
    curve: dict[str, Any],
    family: dict[str, Any],
    advice: Any,
    skeleton: dict[str, Any],
    targets: list[tuple[str, list[int]]],
    a_size: int,
    b_size: int,
) -> dict[str, Any]:
    columns = skeleton["pivot_columns"]
    suffixes = ADAPTIVE.SOURCE_AWARE.suffix_indices(b_size)
    oracles = [STREAMING.StreamingOracle(curve, family, target, advice) for _, target in targets]
    prefixes = ADAPTIVE.SOURCE_AWARE.prefix_order(a_size, b_size)
    mismatches_by_target = {label: 0 for label, _ in targets}
    validation_queries_by_target = {label: 0 for label, _ in targets}
    specialization_queries_by_target = {label: 0 for label, _ in targets}
    for prefix in prefixes:
        for (label, _), oracle in zip(targets, oracles):
            sampled = [oracle.value(prefix + suffixes[column]) for column in columns]
            specialization_queries_by_target[label] += len(columns)
            coefficients = ADAPTIVE.SOURCE_AWARE.row_times_matrix(sampled, skeleton["inverse"], oracle.p)
            for column, suffix in enumerate(suffixes):
                actual = oracle.value(prefix + suffix)
                predicted = sum(coefficients[index] * skeleton["basis_rows"][index][column] for index in range(skeleton["rank"])) % oracle.p
                mismatches_by_target[label] += int(actual != predicted)
                validation_queries_by_target[label] += 1
    target_results = []
    for (label, target), oracle in zip(targets, oracles):
        target_results.append({
            "label": label,
            "target": target,
            "mismatches": mismatches_by_target[label],
            "specialization_queries": specialization_queries_by_target[label],
            "validation_queries": validation_queries_by_target[label],
            "oracle_ops": oracle.ops,
            "direct_reference_ops": oracle.reference.ops,
            "direct_reference_mismatches": oracle.reference_mismatches,
        })
    source_online = STREAMING.CN.empty_ops()
    for oracle in oracles:
        STREAMING.CN.add_ops(source_online, oracle.ops)
    direct_reference_total = STREAMING.CN.empty_ops()
    for oracle in oracles:
        STREAMING.CN.add_ops(direct_reference_total, oracle.reference.ops)
    return {
        "target_count": len(targets),
        "total_prefixes": len(prefixes),
        "targets": target_results,
        "source_online_ops": source_online,
        "direct_reference_ops": direct_reference_total,
        "all_exact": all(item["mismatches"] == 0 for item in target_results),
        "all_direct_reference_exact": all(item["direct_reference_mismatches"] == 0 for item in target_results),
        "all_relation_targets_exact": all(item["mismatches"] == 0 for item in target_results if item["label"].startswith("relation_")),
        "all_supported_descent_targets_exact": all(item["mismatches"] == 0 for item in target_results if item["label"].startswith("held_out_supported_")),
        "prefix_recompute_calls": source_online.get("prefix_recompute_calls", 0),
        "charged_point_add_ratio_over_direct": source_online["point_add_calls"] / max(1, direct_reference_total["point_add_calls"]),
        "point_adds_per_target": source_online["point_add_calls"] / max(1, len(targets)),
        "direct_point_adds_per_target": direct_reference_total["point_add_calls"] / max(1, len(targets)),
    }


def run_row(curve: dict[str, Any], family: dict[str, Any], materialized_row: dict[str, Any]) -> dict[str, Any]:
    started = time.perf_counter()
    a_size = len(family["progression"]["points"])
    b_size = len(family["factor_base"]["points"])
    advice = STREAMING.StreamingSourceAdvice(curve, family)
    base_target = family["relations"]["target_transcript"][0]["target"]
    base_oracle = STREAMING.StreamingOracle(curve, family, base_target, advice)
    skeleton = ADAPTIVE.adaptive_build(base_oracle, a_size, b_size)
    relations, held_out = target_pool(family)
    results = []
    for label, targets in batch_specs(relations, held_out):
        reset_prefix(advice)
        result = run_batch(curve, family, advice, skeleton, targets, a_size, b_size)
        result["label"] = label
        result["targets_expected_relation_count"] = sum(item[0].startswith("relation_") for item in targets)
        result["targets_expected_descent_count"] = sum(item[0].startswith("held_out_supported_") for item in targets)
        result["charged_source_ops"] = STREAMING.CN.empty_ops()
        STREAMING.CN.add_ops(result["charged_source_ops"], advice.ops)
        STREAMING.CN.add_ops(result["charged_source_ops"], base_oracle.ops)
        STREAMING.CN.add_ops(result["charged_source_ops"], result["source_online_ops"])
        result["charged_point_add_ratio_including_advice"] = result["charged_source_ops"]["point_add_calls"] / max(1, result["direct_reference_ops"]["point_add_calls"] + base_oracle.reference.ops["point_add_calls"])
        results.append(result)
    full = next(item for item in results if item["label"] == "full")
    rho = STREAMING.rho_reference(curve, family, curve["p"] ^ len(family["family"]))
    retained_ratio = advice.retained_bytes() / max(1, materialized_row["source_advice"]["python_retained_bytes"])
    return {
        "curve_id": curve["id"],
        "family": family["family"],
        "dimensions": [a_size, b_size, b_size, b_size, b_size],
        "discovered_rank": skeleton["rank"],
        "candidate_prefixes_examined": skeleton["candidate_prefixes_examined"],
        "full_tensor_entries": a_size * b_size**4,
        "source_advice": {
            "prefix_entries_retained": 1,
            "suffix_entries": len(advice.suffix),
            "python_retained_bytes": advice.retained_bytes(),
            "logical_payload_bytes": advice.logical_payload_bytes,
            "source_input_points": len(advice.a_points) + len(advice.r_points),
            "source_input_point_bytes_uncharged": (len(advice.a_points) + len(advice.r_points)) * advice.point_payload_bytes,
            "precompute_ops": advice.ops,
        },
        "materialized_advice": {"python_retained_bytes": materialized_row["source_advice"]["python_retained_bytes"]},
        "streaming_vs_materialized_retained_ratio": retained_ratio,
        "construction_oracle_ops": base_oracle.ops,
        "batches": results,
        "full_batch": full,
        "base_reference_mismatches": base_oracle.reference_mismatches,
        "rho_reference": rho,
        "relation_target_binding": full["targets_expected_relation_count"] == 8 and all(item["label"] == f"relation_{index}" for index, item in enumerate(item for item in full["targets"] if item["label"].startswith("relation_"))),
        "independent_relation_witnesses_present": bool(family["relations"]["independent_equations"]) and all(item.get("r_witness") for item in family["relations"]["independent_equations"]),
        "all_full_relation_targets_exact": full["all_relation_targets_exact"],
        "all_full_supported_descent_targets_exact": full["all_supported_descent_targets_exact"],
        "all_full_direct_reference_exact": full["all_direct_reference_exact"],
        "fixed_curve_advice_target_independent": True,
        "streaming_prefix_state": True,
        "wall_seconds": time.perf_counter() - started,
        "row_digest": digest({"curve_id": curve["id"], "family": family["family"], "rank": skeleton["rank"], "batches": [{key: value for key, value in batch.items() if key not in {"targets", "source_online_ops", "direct_reference_ops", "charged_source_ops"}} for batch in results], "source_advice": advice.ops}),
    }


def run(input_path: Path, materialized_path: Path, families: list[str], order: str = "diagonal") -> dict[str, Any]:
    started = time.perf_counter()
    source = json.loads(input_path.read_text(encoding="utf-8"))
    materialized = json.loads(materialized_path.read_text(encoding="utf-8"))
    materialized_by_key = {(row["curve_id"], row["family"]): row for row in materialized["rows"]}
    original_prefix_order = ADAPTIVE.SOURCE_AWARE.prefix_order
    if order != "diagonal":
        ADAPTIVE.SOURCE_AWARE.prefix_order = lambda a_size, b_size: STREAMING.CN.alternate_prefix_order(a_size, b_size, order)
    rows = []
    try:
        for instance in source["instances"]:
            by_family = {item["family"]: item for item in instance["families"]}
            for family_name in families:
                key = (instance["curve"]["id"], family_name)
                rows.append(run_row(instance["curve"], by_family[family_name], materialized_by_key[key]))
    finally:
        ADAPTIVE.SOURCE_AWARE.prefix_order = original_prefix_order
    normalized = [{key: value for key, value in row.items() if key != "wall_seconds"} for row in rows]
    full_batches = [row["full_batch"] for row in rows]
    balanced_batches = [batch for row in rows for batch in row["batches"] if batch["label"] != "full"]
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-streaming-batch-accounting-preflight-v1",
        "claim_status": ["OBSERVATION", "TOY-EVIDENCE", "MODEL-BOUND"],
        "source": {"producer_sha256": sha256_file(SCRIPT_PATH), "streaming_sha256": sha256_file(STREAMING_SOURCE), "input_sha256": sha256_file(input_path), "materialized_sha256": sha256_file(materialized_path), "typed_five_ec_sha256": sha256_file(TYPED_FIVE.SCRIPT_PATH)},
        "config": {"families": families, "prefix_order": order, "expected_exact": order == "diagonal", "batch_specs": ["balanced_1", "balanced_2", "balanced_4", "balanced_8", "full"], "full_relation_targets": 8, "full_descent_targets": "all supported", "batch_loop_order": "prefix_then_target_then_suffix", "full_tensor_validation": True, "source_inputs_separate": True},
        "rows": rows,
        "summary": {
            "rows": len(rows),
            "all_full_exact": all(batch["all_exact"] for batch in full_batches),
            "all_balanced_exact": all(batch["all_exact"] for batch in balanced_batches),
            "all_full_direct_reference_exact": all(row["all_full_direct_reference_exact"] and row["base_reference_mismatches"] == 0 for row in rows),
            "all_full_relation_targets_exact": all(row["all_full_relation_targets_exact"] for row in rows),
            "all_full_supported_descent_targets_exact": all(row["all_full_supported_descent_targets_exact"] for row in rows),
            "all_relation_bindings": all(row["relation_target_binding"] and row["independent_relation_witnesses_present"] for row in rows),
            "all_memory_reductions": all(row["streaming_vs_materialized_retained_ratio"] < 1.0 for row in rows),
            "min_retained_ratio": min(row["streaming_vs_materialized_retained_ratio"] for row in rows),
            "max_retained_ratio": max(row["streaming_vs_materialized_retained_ratio"] for row in rows),
            "balanced_batch_point_add_ratios": {label: {"min": min(batch["charged_point_add_ratio_including_advice"] for row in rows for batch in row["batches"] if batch["label"] == label), "max": max(batch["charged_point_add_ratio_including_advice"] for row in rows for batch in row["batches"] if batch["label"] == label)} for label in ("balanced_1", "balanced_2", "balanced_4", "balanced_8")},
            "all_batch_prefix_reuse": all(batch["prefix_recompute_calls"] == batch["total_prefixes"] for batch in balanced_batches),
            "breakthrough_claim": False,
            "algorithm_promotion_gate": False,
            "boundary": "Target-batched streaming source advice with full relation/descent replay; no generic ECDLP claim.",
        },
        "total_wall_seconds": time.perf_counter() - started,
        "result_digest": digest(normalized),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("materialized", type=Path)
    parser.add_argument("--families", nargs="+", required=True)
    parser.add_argument("--order", choices=("diagonal", "lexicographic", "reverse_lexicographic"), default="diagonal")
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.materialized, args.families, args.order), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
