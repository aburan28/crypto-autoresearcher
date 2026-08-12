#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
import resource
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
ADAPTIVE_SOURCE = SCRIPT_PATH.with_name("typed_tt_adaptive_skeleton_preflight.py")
ORACLE_SOURCE = SCRIPT_PATH.with_name("typed_tt_cross_preflight.py")


def load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ADAPTIVE = load("typed_tt_adaptive_for_circuit_native", ADAPTIVE_SOURCE)
ORACLE = load("typed_tt_oracle_for_circuit_native", ORACLE_SOURCE)
TYPED_FIVE = load("typed_five_ec_for_circuit_native", SCRIPT_PATH.with_name("typed_five_ec.py"))
Point = tuple[int, int] | None


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def deep_size(value: Any, seen: set[int] | None = None) -> int:
    seen = seen or set()
    identity = id(value)
    if identity in seen:
        return 0
    seen.add(identity)
    size = sys.getsizeof(value)
    if isinstance(value, dict):
        size += sum(deep_size(key, seen) + deep_size(item, seen) for key, item in value.items())
    elif isinstance(value, (list, tuple, set, frozenset, Counter)):
        size += sum(deep_size(item, seen) for item in value)
    return size


def rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if platform.system() == "Darwin" else value * 1024)


def unrank(value: int, dimensions: list[int]) -> tuple[int, ...]:
    result = [0] * len(dimensions)
    for index in range(len(dimensions) - 1, -1, -1):
        result[index] = value % dimensions[index]
        value //= dimensions[index]
    return tuple(result)


def alternate_prefix_order(a_size: int, b_size: int, mode: str) -> list[tuple[int, int, int]]:
    values = [unrank(value, [a_size, b_size, b_size]) for value in range(a_size * b_size * b_size)]
    if mode == "lexicographic":
        return values
    if mode == "reverse_lexicographic":
        return list(reversed(values))
    raise ValueError(f"unknown prefix order: {mode}")


def empty_ops() -> dict[str, int]:
    return {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0, "field_subtractions": 0}


def add_ops(left: dict[str, int], right: dict[str, int]) -> None:
    for key, value in right.items():
        left[key] = left.get(key, 0) + value


class SourceAdvice:
    def __init__(self, curve: dict[str, Any], family: dict[str, Any]) -> None:
        self.p = curve["p"]
        self.curve = ORACLE.Curve(curve["p"], curve["a"])
        self.a_points = [ORACLE.point(value) for value in family["progression"]["points"]]
        self.r_points = [ORACLE.point(value) for value in family["factor_base"]["points"]]
        self.prefix: dict[tuple[int, int, int], Point] = {}
        self.suffix: dict[tuple[int, int], Point] = {}
        self.ops = empty_ops()
        for a_index, a_point in enumerate(self.a_points):
            for r0_index, r0_point in enumerate(self.r_points):
                first = self.curve.add(a_point, r0_point, self.ops)
                for r1_index, r1_point in enumerate(self.r_points):
                    self.prefix[(a_index, r0_index, r1_index)] = self.curve.add(first, r1_point, self.ops)
        for r2_index, r2_point in enumerate(self.r_points):
            for r3_index, r3_point in enumerate(self.r_points):
                self.suffix[(r2_index, r3_index)] = self.curve.add(r2_point, r3_point, self.ops)
        self.field_bytes = max(1, (self.p.bit_length() + 7) // 8)
        self.point_payload_bytes = 2 * self.field_bytes
        self.advice_bytes = deep_size({"prefix": self.prefix, "suffix": self.suffix})
        self.logical_payload_bytes = (len(self.prefix) + len(self.suffix)) * self.point_payload_bytes


class CircuitNativeOracle:
    def __init__(self, curve: dict[str, Any], family: dict[str, Any], target: list[int], advice: SourceAdvice) -> None:
        self.p = curve["p"]
        self.nu = ORACLE.nonsquare(self.p)
        self.target = ORACLE.point(target)
        if self.target is None:
            raise ValueError("finite target required")
        self.advice = advice
        self.reference = ORACLE.Oracle(curve, ADAPTIVE.target_family(family, target))
        self.reference_mismatches = 0
        self.cache: dict[tuple[int, ...], int] = {}
        self.ops = {**empty_ops(), "cache_hits": 0, "unique_queries": 0, "source_advice_reads": 0, "logical_source_read_bytes": 0, "predicate_field_multiplications": 0, "predicate_field_subtractions": 0}

    def value(self, indices: tuple[int, ...]) -> int:
        if indices in self.cache:
            self.ops["cache_hits"] += 1
            reference_result = self.reference.value(indices)
            self.reference_mismatches += int(reference_result != self.cache[indices])
            return self.cache[indices]
        prefix = self.advice.prefix[indices[:3]]
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


def baseline_ops(baseline_row: dict[str, Any]) -> dict[str, int]:
    total = empty_ops()
    add_ops(total, baseline_row["construction_oracle_ops"])
    for target in baseline_row["targets"]:
        add_ops(total, target["oracle_ops"])
    return total


def op_subset(value: dict[str, int]) -> dict[str, int]:
    return {key: value.get(key, 0) for key in ("point_add_calls", "field_inversions", "field_multiplications", "field_subtractions", "cache_hits", "unique_queries")}


def rho_reference(curve: dict[str, Any], family: dict[str, Any], seed: int) -> dict[str, Any]:
    supported = next((item for item in family["held_out_descent"]["transcript"] if item["materialized_d4"]["success"] and item["r_scan_plus_d3"]["success"]), None)
    if supported is None:
        return {"status": "NO_SUPPORTED_TARGET"}
    curve_object = TYPED_FIVE.Curve(curve["p"], curve["a"], curve["b"])
    generator = TYPED_FIVE.point_from_json(curve["generator"])
    target = TYPED_FIVE.point_from_json(supported["target"])
    result = TYPED_FIVE.COORDINATE.ENERGY.pollard_rho(curve_object, curve["q"], generator, target, seed)
    if not result["verified"] or result["recovered_scalar"] != supported["scalar"]:
        raise AssertionError("rho reference recovered the wrong scalar")
    return {"status": "PASS", "known_scalar": supported["scalar"], "target": supported["target"], "ops": result["ops"], "cycle_steps": result["cycle_steps"]}


def run_row(curve: dict[str, Any], family: dict[str, Any], baseline_row: dict[str, Any]) -> dict[str, Any]:
    started = time.perf_counter()
    a_size = len(family["progression"]["points"])
    b_size = len(family["factor_base"]["points"])
    full_entries = a_size * b_size**4
    advice = SourceAdvice(curve, family)
    base_target = family["relations"]["target_transcript"][0]["target"]
    base_oracle = CircuitNativeOracle(curve, family, base_target, advice)
    skeleton = ADAPTIVE.adaptive_build(base_oracle, a_size, b_size)
    relation_targets = [item["target"] for item in family["relations"]["target_transcript"][:8]]
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
        oracle = CircuitNativeOracle(curve, family, target, advice)
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
    source_online = empty_ops()
    add_ops(source_online, base_oracle.ops)
    for target in target_results:
        add_ops(source_online, target["oracle_ops"])
    direct_reference_total = empty_ops()
    add_ops(direct_reference_total, base_oracle.reference.ops)
    for target in target_results:
        add_ops(direct_reference_total, target["direct_reference_ops"])
    sealed_baseline_match = op_subset(base_oracle.reference.ops) == op_subset(baseline_row["construction_oracle_ops"])
    baseline_targets = {item["label"]: item for item in baseline_row["targets"]}
    for target in target_results:
        if target["label"] in baseline_targets:
            sealed_baseline_match = sealed_baseline_match and op_subset(target["direct_reference_ops"]) == op_subset(baseline_targets[target["label"]]["oracle_ops"])
    charged_source = empty_ops()
    add_ops(charged_source, advice.ops)
    add_ops(charged_source, source_online)
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
        "construction_query_ratio_full_tensor": (skeleton["candidate_prefixes_examined"] * b_size**2) / max(1, full_entries),
        "specialization_query_ratio_full_tensor": (a_size * b_size**2 * skeleton["rank"]) / max(1, full_entries),
        "source_advice": {"prefix_entries": len(advice.prefix), "suffix_entries": len(advice.suffix), "python_retained_bytes": advice.advice_bytes, "logical_payload_bytes": advice.logical_payload_bytes, "field_bytes": advice.field_bytes, "point_payload_bytes": advice.point_payload_bytes, "precompute_ops": advice.ops},
        "construction_oracle_ops": base_oracle.ops,
        "targets": target_results,
        "source_online_ops": source_online,
        "charged_source_ops": charged_source,
        "direct_baseline_ops": direct_reference_total,
        "rho_reference": rho,
        "charged_point_adds_over_rho_group_operations": (charged_source["point_add_calls"] / max(1, rho["ops"]["group_operations"])) if rho["status"] == "PASS" else None,
        "sealed_baseline_match": sealed_baseline_match,
        "relation_target_binding": all({f"relation_{index}": target for index, target in enumerate(relation_targets)}.get(item["label"]) == item["target"] for item in target_results if item["label"].startswith("relation_")),
        "held_out_target_binding": any(item["label"] == "held_out_first" and item["target"] == family["held_out_descent"]["transcript"][0]["target"] for item in target_results),
        "independent_relation_witnesses_present": bool(family["relations"]["independent_equations"]) and all(item.get("r_witness") for item in family["relations"]["independent_equations"]),
        "relation_target_count": len(relation_targets),
        "supported_descent_target_count": len(supported_descent),
        "all_relation_targets_exact": all(item["mismatches"] == 0 for item in target_results if item["label"].startswith("relation_")),
        "all_supported_descent_targets_exact": all(item["mismatches"] == 0 for item in target_results if item["label"].startswith("held_out_supported_") or (item["label"] == "held_out_first" and tuple(item["target"]) in {tuple(entry["target"]) for entry in supported_descent})),
        "direct_reference_mismatches": sum(item["direct_reference_mismatches"] for item in target_results) + base_oracle.reference_mismatches,
        "charged_point_add_ratio_over_direct": charged_source["point_add_calls"] / max(1, direct_reference_total["point_add_calls"]),
        "all_exact": all(item["mismatches"] == 0 for item in target_results),
        "source_construction_non_enumerative": True,
        "fixed_curve_advice_target_independent": True,
        "wall_seconds": time.perf_counter() - started,
        "row_digest": digest({"curve_id": curve["id"], "family": family["family"], "rank": skeleton["rank"], "examined": skeleton["candidate_prefixes_examined"], "basis_prefixes": skeleton["basis_prefixes"], "pivot_columns": skeleton["pivot_columns"], "targets": [{key: value for key, value in item.items() if key not in {"oracle_ops", "direct_reference_ops"}} for item in target_results], "source_advice": advice.ops}),
    }


def run(input_path: Path, baseline_path: Path, families: list[str], order: str = "diagonal") -> dict[str, Any]:
    started = time.perf_counter()
    source = json.loads(input_path.read_text(encoding="utf-8"))
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    baseline_by_key = {(row["curve_id"], row["family"]): row for row in baseline["rows"]}
    rows = []
    original_prefix_order = ADAPTIVE.SOURCE_AWARE.prefix_order
    if order != "diagonal":
        ADAPTIVE.SOURCE_AWARE.prefix_order = lambda a_size, b_size: alternate_prefix_order(a_size, b_size, order)
    try:
        for instance in source["instances"]:
            by_family = {item["family"]: item for item in instance["families"]}
            for family_name in families:
                key = (instance["curve"]["id"], family_name)
                rows.append(run_row(instance["curve"], by_family[family_name], baseline_by_key[key]))
    finally:
        ADAPTIVE.SOURCE_AWARE.prefix_order = original_prefix_order
    normalized = [{key: value for key, value in row.items() if key != "wall_seconds"} for row in rows]
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-circuit-native-accounting-preflight-v1",
        "claim_status": ["OBSERVATION", "TOY-EVIDENCE", "MODEL-BOUND"],
        "source": {"producer_sha256": sha256_file(SCRIPT_PATH), "adaptive_baseline_sha256": sha256_file(baseline_path), "input_sha256": sha256_file(input_path), "typed_five_ec_sha256": sha256_file(TYPED_FIVE.SCRIPT_PATH)},
        "config": {"families": families, "cut": 3, "prefix_order": order, "expected_exact": order == "diagonal", "source_sums": ["A+R0+R1", "R2+R3"], "rank_budget_input": False, "source_tuple_enumeration": False, "validation_full_tensor": True, "logical_bandwidth_accounted": True},
        "rows": rows,
        "summary": {
            "rows": len(rows),
            "all_adaptive": all(row["source_construction_non_enumerative"] for row in rows),
            "all_exact_validation": all(row["all_exact"] for row in rows),
            "all_fixed_curve_advice_target_independent": all(row["fixed_curve_advice_target_independent"] for row in rows),
            "all_counter_paths_present": all(row["charged_source_ops"]["point_add_calls"] >= row["source_advice"]["precompute_ops"]["point_add_calls"] for row in rows),
            "all_direct_reference_exact": all(row["direct_reference_mismatches"] == 0 for row in rows),
            "all_relation_bindings": all(row["relation_target_binding"] and row["independent_relation_witnesses_present"] for row in rows),
            "all_supported_descent_exact": all(row["all_supported_descent_targets_exact"] for row in rows),
            "all_sealed_baseline_matches": all(row["sealed_baseline_match"] for row in rows),
            "min_charged_point_add_ratio": min(row["charged_point_add_ratio_over_direct"] for row in rows),
            "max_charged_point_add_ratio": max(row["charged_point_add_ratio_over_direct"] for row in rows),
            "rows_with_charged_point_add_win": sum(row["charged_point_add_ratio_over_direct"] < 1.0 for row in rows),
            "algorithm_promotion_gate": False,
            "breakthrough_claim": False,
            "boundary": "Shared source-sum evaluator with fixed-curve advice and logical bandwidth accounting; no generic ECDLP claim.",
        },
        "peak_rss_bytes": rss_bytes(),
        "total_wall_seconds": time.perf_counter() - started,
        "result_digest": digest(normalized),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("--families", nargs="+", required=True)
    parser.add_argument("--order", choices=("diagonal", "lexicographic", "reverse_lexicographic"), default="diagonal")
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.baseline, args.families, args.order), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
