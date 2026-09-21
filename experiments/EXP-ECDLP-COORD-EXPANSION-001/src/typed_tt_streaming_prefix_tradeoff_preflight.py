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
CIRCUIT_NATIVE_SOURCE = SCRIPT_PATH.with_name("typed_tt_circuit_native_accounting_preflight.py")


def load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


CN = load("typed_tt_circuit_native_for_streaming", CIRCUIT_NATIVE_SOURCE)
ADAPTIVE = CN.ADAPTIVE
ORACLE = CN.ORACLE
TYPED_FIVE = CN.TYPED_FIVE
Point = tuple[int, int] | None


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class StreamingSourceAdvice:
    """Retain the suffix table and only the most recently used prefix state."""

    def __init__(self, curve: dict[str, Any], family: dict[str, Any]) -> None:
        self.p = curve["p"]
        self.curve = ORACLE.Curve(curve["p"], curve["a"])
        self.a_points = [ORACLE.point(value) for value in family["progression"]["points"]]
        self.r_points = [ORACLE.point(value) for value in family["factor_base"]["points"]]
        self.suffix: dict[tuple[int, int], Point] = {}
        self.ops = CN.empty_ops()
        for r2_index, r2_point in enumerate(self.r_points):
            for r3_index, r3_point in enumerate(self.r_points):
                self.suffix[(r2_index, r3_index)] = self.curve.add(r2_point, r3_point, self.ops)
        self.current_prefix_key: tuple[int, int, int] | None = None
        self.current_prefix: Point = None
        self.field_bytes = max(1, (self.p.bit_length() + 7) // 8)
        self.point_payload_bytes = 2 * self.field_bytes
        self.suffix_bytes = CN.deep_size(self.suffix)
        self.logical_payload_bytes = len(self.suffix) * self.point_payload_bytes + self.point_payload_bytes

    def prefix_for(self, key: tuple[int, int, int], online_ops: dict[str, int]) -> Point:
        if key != self.current_prefix_key:
            a_index, r0_index, r1_index = key
            first = self.curve.add(self.a_points[a_index], self.r_points[r0_index], online_ops)
            self.current_prefix = self.curve.add(first, self.r_points[r1_index], online_ops)
            self.current_prefix_key = key
        return self.current_prefix

    def retained_bytes(self) -> int:
        return self.suffix_bytes + CN.deep_size({"key": self.current_prefix_key, "point": self.current_prefix})


class StreamingOracle:
    def __init__(self, curve: dict[str, Any], family: dict[str, Any], target: list[int], advice: StreamingSourceAdvice) -> None:
        self.p = curve["p"]
        self.nu = ORACLE.nonsquare(self.p)
        self.target = ORACLE.point(target)
        if self.target is None:
            raise ValueError("finite target required")
        self.advice = advice
        self.reference = ORACLE.Oracle(curve, ADAPTIVE.target_family(family, target))
        self.reference_mismatches = 0
        self.cache: dict[tuple[int, ...], int] = {}
        self.ops = {
            **CN.empty_ops(),
            "cache_hits": 0,
            "unique_queries": 0,
            "source_advice_reads": 0,
            "logical_source_read_bytes": 0,
            "predicate_field_multiplications": 0,
            "predicate_field_subtractions": 0,
            "prefix_recompute_calls": 0,
        }

    def value(self, indices: tuple[int, ...]) -> int:
        if indices in self.cache:
            self.ops["cache_hits"] += 1
            reference_result = self.reference.value(indices)
            self.reference_mismatches += int(reference_result != self.cache[indices])
            return self.cache[indices]
        new_prefix = indices[:3] != self.advice.current_prefix_key
        prefix = self.advice.prefix_for(indices[:3], self.ops)
        self.ops["prefix_recompute_calls"] += int(new_prefix)
        suffix = self.advice.suffix[indices[3:]]
        total = self.advice.curve.add(prefix, suffix, self.ops)
        self.ops["source_advice_reads"] += 2
        self.ops["logical_source_read_bytes"] += 2 * self.advice.point_payload_bytes
        if total is None:
            result = 1
        else:
            x, y = total
            tx, ty = self.target
            dx = (x - tx) % self.p
            dy = (y - ty) % self.p
            result = (dx * dx - self.nu * dy * dy) % self.p
            self.ops["predicate_field_multiplications"] += 2
            self.ops["predicate_field_subtractions"] += 1
        self.cache[indices] = result
        self.ops["unique_queries"] += 1
        reference_result = self.reference.value(indices)
        self.reference_mismatches += int(reference_result != result)
        return result


def rho_reference(curve: dict[str, Any], family: dict[str, Any], seed: int) -> dict[str, Any]:
    return CN.rho_reference(curve, family, seed)


def run_row(curve: dict[str, Any], family: dict[str, Any], baseline_row: dict[str, Any], materialized_row: dict[str, Any]) -> dict[str, Any]:
    started = time.perf_counter()
    a_size = len(family["progression"]["points"])
    b_size = len(family["factor_base"]["points"])
    full_entries = a_size * b_size**4
    advice = StreamingSourceAdvice(curve, family)
    base_target = family["relations"]["target_transcript"][0]["target"]
    base_oracle = StreamingOracle(curve, family, base_target, advice)
    skeleton = ADAPTIVE.adaptive_build(base_oracle, a_size, b_size)
    supported_descent = [item for item in family["held_out_descent"]["transcript"] if item["materialized_d4"]["success"] and item["r_scan_plus_d3"]["success"]]
    binding_targets = list(ADAPTIVE.SOURCE_AWARE.target_list(family))
    seen_targets = {tuple(target) for _, target in binding_targets}
    for index, item in enumerate(supported_descent):
        target_key = tuple(item["target"])
        if target_key not in seen_targets:
            binding_targets.append((f"held_out_supported_{index}", item["target"]))
            seen_targets.add(target_key)
    target_results = []
    for label, target in binding_targets:
        oracle = StreamingOracle(curve, family, target, advice)
        result = ADAPTIVE.SOURCE_AWARE.reconstruct_target(oracle, skeleton, a_size, b_size, True)
        target_results.append({
            "label": label,
            "target": target,
            "mismatches": result["mismatches"],
            "specialization_queries": result["specialization_queries"],
            "validation_queries": result["validation_queries"],
            "oracle_ops": oracle.ops,
            "direct_reference_ops": oracle.reference.ops,
            "direct_reference_mismatches": oracle.reference_mismatches,
        })
    source_online = CN.empty_ops()
    CN.add_ops(source_online, base_oracle.ops)
    for target in target_results:
        CN.add_ops(source_online, target["oracle_ops"])
    direct_reference_total = CN.empty_ops()
    CN.add_ops(direct_reference_total, base_oracle.reference.ops)
    for target in target_results:
        CN.add_ops(direct_reference_total, target["direct_reference_ops"])
    baseline_targets = {item["label"]: item for item in baseline_row["targets"]}
    sealed_baseline_match = CN.op_subset(base_oracle.reference.ops) == CN.op_subset(baseline_row["construction_oracle_ops"])
    for target in target_results:
        if target["label"] in baseline_targets:
            sealed_baseline_match = sealed_baseline_match and CN.op_subset(target["direct_reference_ops"]) == CN.op_subset(baseline_targets[target["label"]]["oracle_ops"])
    charged_source = CN.empty_ops()
    CN.add_ops(charged_source, advice.ops)
    CN.add_ops(charged_source, source_online)
    rho = rho_reference(curve, family, curve["p"] ^ len(family["family"]))
    return {
        "curve_id": curve["id"],
        "family": family["family"],
        "dimensions": [a_size, b_size, b_size, b_size, b_size],
        "discovered_rank": skeleton["rank"],
        "candidate_prefixes_examined": skeleton["candidate_prefixes_examined"],
        "stability_window": skeleton["stability_window"],
        "basis_prefixes": skeleton["basis_prefixes"],
        "pivot_columns": skeleton["pivot_columns"],
        "construction_queries": skeleton["candidate_prefixes_examined"] * b_size**2,
        "specialization_queries_per_target": a_size * b_size**2 * skeleton["rank"],
        "full_tensor_entries": full_entries,
        "source_advice": {
            "prefix_entries_retained": int(advice.current_prefix_key is not None),
            "suffix_entries": len(advice.suffix),
            "python_retained_bytes": advice.retained_bytes(),
            "suffix_python_bytes": advice.suffix_bytes,
            "current_prefix_python_bytes": CN.deep_size({"key": advice.current_prefix_key, "point": advice.current_prefix}),
            "logical_payload_bytes": advice.logical_payload_bytes,
            "source_input_points": len(advice.a_points) + len(advice.r_points),
            "source_input_point_bytes_uncharged": (len(advice.a_points) + len(advice.r_points)) * advice.point_payload_bytes,
            "field_bytes": advice.field_bytes,
            "point_payload_bytes": advice.point_payload_bytes,
            "precompute_ops": advice.ops,
        },
        "materialized_advice": {
            "python_retained_bytes": materialized_row["source_advice"]["python_retained_bytes"],
            "prefix_entries": materialized_row["source_advice"]["prefix_entries"],
            "suffix_entries": materialized_row["source_advice"]["suffix_entries"],
        },
        "construction_oracle_ops": base_oracle.ops,
        "targets": target_results,
        "source_online_ops": source_online,
        "charged_source_ops": charged_source,
        "direct_baseline_ops": direct_reference_total,
        "rho_reference": rho,
        "sealed_baseline_match": sealed_baseline_match,
        "relation_target_binding": all(item["label"] == f"relation_{index}" and item["target"] == family["relations"]["target_transcript"][index]["target"] for index, item in enumerate(target_results) if item["label"].startswith("relation_")),
        "independent_relation_witnesses_present": bool(family["relations"]["independent_equations"]) and all(item.get("r_witness") for item in family["relations"]["independent_equations"]),
        "all_relation_targets_exact": all(item["mismatches"] == 0 for item in target_results if item["label"].startswith("relation_")),
        "all_supported_descent_targets_exact": all(item["mismatches"] == 0 for item in target_results if item["label"].startswith("held_out_supported_") or (item["label"] == "held_out_first" and tuple(item["target"]) in {tuple(entry["target"]) for entry in supported_descent})),
        "direct_reference_mismatches": sum(item["direct_reference_mismatches"] for item in target_results) + base_oracle.reference_mismatches,
        "charged_point_add_ratio_over_direct": charged_source["point_add_calls"] / max(1, direct_reference_total["point_add_calls"]),
        "streaming_vs_materialized_retained_ratio": advice.retained_bytes() / max(1, materialized_row["source_advice"]["python_retained_bytes"]),
        "all_exact": all(item["mismatches"] == 0 for item in target_results),
        "streaming_prefix_state": True,
        "fixed_curve_advice_target_independent": True,
        "wall_seconds": time.perf_counter() - started,
        "row_digest": digest({"curve_id": curve["id"], "family": family["family"], "rank": skeleton["rank"], "examined": skeleton["candidate_prefixes_examined"], "basis_prefixes": skeleton["basis_prefixes"], "pivot_columns": skeleton["pivot_columns"], "targets": [{key: value for key, value in item.items() if key not in {"oracle_ops", "direct_reference_ops"}} for item in target_results], "source_advice": advice.ops}),
    }


def run(input_path: Path, baseline_path: Path, materialized_path: Path, families: list[str], order: str = "diagonal") -> dict[str, Any]:
    started = time.perf_counter()
    source = json.loads(input_path.read_text(encoding="utf-8"))
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    materialized = json.loads(materialized_path.read_text(encoding="utf-8"))
    baseline_by_key = {(row["curve_id"], row["family"]): row for row in baseline["rows"]}
    materialized_by_key = {(row["curve_id"], row["family"]): row for row in materialized["rows"]}
    rows = []
    original_prefix_order = ADAPTIVE.SOURCE_AWARE.prefix_order
    if order != "diagonal":
        ADAPTIVE.SOURCE_AWARE.prefix_order = lambda a_size, b_size: CN.alternate_prefix_order(a_size, b_size, order)
    try:
        for instance in source["instances"]:
            by_family = {item["family"]: item for item in instance["families"]}
            for family_name in families:
                key = (instance["curve"]["id"], family_name)
                rows.append(run_row(instance["curve"], by_family[family_name], baseline_by_key[key], materialized_by_key[key]))
    finally:
        ADAPTIVE.SOURCE_AWARE.prefix_order = original_prefix_order
    normalized = [{key: value for key, value in row.items() if key != "wall_seconds"} for row in rows]
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-streaming-prefix-tradeoff-preflight-v1",
        "claim_status": ["OBSERVATION", "TOY-EVIDENCE", "MODEL-BOUND"],
        "source": {
            "producer_sha256": sha256_file(SCRIPT_PATH),
            "circuit_native_sha256": sha256_file(CIRCUIT_NATIVE_SOURCE),
            "baseline_sha256": sha256_file(baseline_path),
            "materialized_sha256": sha256_file(materialized_path),
            "input_sha256": sha256_file(input_path),
            "typed_five_ec_sha256": sha256_file(TYPED_FIVE.SCRIPT_PATH),
        },
        "config": {"families": families, "cut": 3, "prefix_order": order, "expected_exact": order == "diagonal", "source_sums": ["A+R0+R1", "R2+R3"], "streaming_prefix_state": True, "full_tensor_validation": True, "source_input_points_separate": True},
        "rows": rows,
        "summary": {
            "rows": len(rows),
            "all_exact_validation": all(row["all_exact"] for row in rows),
            "all_direct_reference_exact": all(row["direct_reference_mismatches"] == 0 for row in rows),
            "all_relation_bindings": all(row["relation_target_binding"] and row["independent_relation_witnesses_present"] for row in rows),
            "all_supported_descent_exact": all(row["all_supported_descent_targets_exact"] for row in rows),
            "all_sealed_baseline_matches": all(row["sealed_baseline_match"] for row in rows),
            "all_memory_reductions": all(row["streaming_vs_materialized_retained_ratio"] < 1.0 for row in rows),
            "min_streaming_vs_materialized_retained_ratio": min(row["streaming_vs_materialized_retained_ratio"] for row in rows),
            "max_streaming_vs_materialized_retained_ratio": max(row["streaming_vs_materialized_retained_ratio"] for row in rows),
            "min_charged_point_add_ratio_over_direct": min(row["charged_point_add_ratio_over_direct"] for row in rows),
            "max_charged_point_add_ratio_over_direct": max(row["charged_point_add_ratio_over_direct"] for row in rows),
            "breakthrough_claim": False,
            "algorithm_promotion_gate": False,
            "boundary": "Fixed-curve streaming advice tradeoff with source inputs reported separately; no generic ECDLP claim.",
        },
        "total_wall_seconds": time.perf_counter() - started,
        "result_digest": digest(normalized),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("materialized", type=Path)
    parser.add_argument("--families", nargs="+", required=True)
    parser.add_argument("--order", choices=("diagonal", "lexicographic", "reverse_lexicographic"), default="diagonal")
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.baseline, args.materialized, args.families, args.order), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
