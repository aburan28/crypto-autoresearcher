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
TYPED_FIVE_SOURCE = SCRIPT_PATH.with_name("typed_five_ec.py")


def load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


STREAMING = load("typed_tt_streaming_for_fresh_witness_audit", STREAMING_SOURCE)
TF = load("typed_five_ec_for_fresh_witness_audit", TYPED_FIVE_SOURCE)
ADAPTIVE = STREAMING.ADAPTIVE
ORACLE = STREAMING.ORACLE


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def zero_ops() -> dict[str, int]:
    return {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0, "field_subtractions": 0, "unique_queries": 0, "zero_hits": 0, "source_advice_reads": 0, "logical_source_read_bytes": 0}


def add_ops(total: dict[str, int], value: dict[str, int]) -> None:
    for key, item in value.items():
        total[key] = total.get(key, 0) + int(item)


class WitnessOracle:
    def __init__(self, target: tuple[int, int], advice: Any) -> None:
        self.target = target
        self.advice = advice
        self.p = advice.p
        self.nu = ORACLE.nonsquare(self.p)
        self.ops = zero_ops()

    def value(self, indices: tuple[int, ...]) -> int:
        prefix = self.advice.prefix_for(indices[:3], self.ops)
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
            self.ops["field_multiplications"] += 2
            self.ops["field_subtractions"] += 1
        self.ops["unique_queries"] += 1
        self.ops["zero_hits"] += int(result == 0)
        return result


def direct_witness_valid(curve: Any, a_points: list[Any], r_points: list[Any], indices: tuple[int, ...], target: Any) -> bool:
    total = a_points[indices[0]]
    for index in indices[1:]:
        total = curve.add(total, r_points[index])
    return total == target


def scan_target(
    typed_curve: Any,
    family: dict[str, Any],
    advice: Any,
    target: tuple[int, int],
    prefix_order: list[tuple[int, int, int]],
    suffixes: list[tuple[int, int]],
    prefix_limit: int | None,
) -> dict[str, Any]:
    oracle = WitnessOracle(target, advice)
    a_points = [ORACLE.point(value) for value in family["progression"]["points"]]
    r_points = [ORACLE.point(value) for value in family["factor_base"]["points"]]
    target_point = ORACLE.point(list(target))
    hits: dict[int, tuple[int, ...]] = {}
    prefixes = prefix_order if prefix_limit is None else prefix_order[:prefix_limit]
    for prefix in prefixes:
        for suffix in suffixes:
            indices = prefix + suffix
            if oracle.value(indices) != 0:
                continue
            a_index = indices[0]
            if a_index not in hits:
                hits[a_index] = indices
    typed_a = [TF.point_from_json(value) for value in family["progression"]["points"]]
    typed_r = [TF.point_from_json(value) for value in family["factor_base"]["points"]]
    typed_target = TF.point_from_json(list(target))
    valid = all(direct_witness_valid(typed_curve, typed_a, typed_r, witness, typed_target) for witness in hits.values())
    return {"hits": [{"a_index": index, "indices": list(witness)} for index, witness in sorted(hits.items())], "valid_witnesses": valid, "prefixes_scanned": len(prefixes), "oracle_ops": oracle.ops}


def run_row(curve_record: dict[str, Any], family: dict[str, Any], mode: str, target_budget_factor: int) -> dict[str, Any]:
    started = time.perf_counter()
    p = curve_record["p"]
    q = curve_record["q"]
    curve_oracle = ORACLE.Curve(p, curve_record["a"])
    curve_typed = TF.Curve(p, curve_record["a"], curve_record["b"])
    generator = TF.point_from_json(curve_record["generator"])
    a_points_typed = [TF.point_from_json(value) for value in family["progression"]["points"]]
    r_points_typed = [TF.point_from_json(value) for value in family["factor_base"]["points"]]
    a_size = len(a_points_typed)
    b_size = len(r_points_typed)
    width = b_size + 1
    prefix_order = ADAPTIVE.SOURCE_AWARE.prefix_order(a_size, b_size)
    suffixes = ADAPTIVE.SOURCE_AWARE.suffix_indices(b_size)
    prefix_limit = None if mode == "full" else 1
    advice = STREAMING.StreamingSourceAdvice(curve_record, family)
    materialized = TF.compile_r_support(curve_typed, r_points_typed)
    materialized_build_ops = zero_ops()
    for profile in materialized["summary"]["profiles"]:
        add_ops(materialized_build_ops, profile["build_ops"])
    candidate_basis = TF.IncrementalBasis(width, q)
    baseline_basis = TF.IncrementalBasis(width, q)
    candidate_independent: list[dict[str, Any]] = []
    baseline_independent: list[dict[str, Any]] = []
    candidate_target_ops = TF.Ops()
    baseline_target_ops = TF.Ops()
    candidate_query_ops = zero_ops()
    baseline_query_ops = TF.Ops()
    transcripts = []
    target_budget = min(q - 1, target_budget_factor * width)
    relation_seed = family["run_seed"] ^ 0x13198A2E
    for scalar_index, scalar in enumerate(TF.nonzero_scalar_stream(q, relation_seed)):
        if scalar_index == target_budget or candidate_basis.rank == width:
            break
        target = curve_typed.mul(scalar, generator, candidate_target_ops)
        target_json = TF.point_json(target)
        target_oracle_point = ORACLE.point(target_json)
        scan = scan_target(curve_typed, family, advice, target_oracle_point, prefix_order, suffixes, prefix_limit)
        add_ops(candidate_query_ops, scan["oracle_ops"])
        baseline = TF.query_d4_all(curve_typed, a_points_typed, r_points_typed, materialized["d4_internal"], target)
        for key, value in baseline["ops"].items():
            setattr(baseline_query_ops, key, getattr(baseline_query_ops, key) + value)
        candidate_a = {item["a_index"] for item in scan["hits"]}
        baseline_a = {item["a_index"] for item in baseline["hits"]}
        support_match = candidate_a == baseline_a
        candidate_equations = []
        for hit in scan["hits"]:
            coefficients = TF.quotient_relation_coefficients(hit["a_index"], hit["indices"][1:], b_size)
            equation = {"coefficients": coefficients, "rhs": scalar, "a_index": hit["a_index"], "r_witness": hit["indices"][1:]}
            candidate_equations.append(equation)
            if candidate_basis.insert(coefficients, scalar):
                candidate_independent.append(equation)
        for hit in baseline["hits"]:
            coefficients = TF.quotient_relation_coefficients(hit["a_index"], hit["r_witness"], b_size)
            equation = {"coefficients": coefficients, "rhs": scalar, "a_index": hit["a_index"], "r_witness": list(hit["r_witness"])}
            if baseline_basis.insert(coefficients, scalar):
                baseline_independent.append(equation)
        transcripts.append({"scalar": scalar, "target": target_json, "candidate_hits": scan["hits"], "baseline_hits": baseline["hits"], "candidate_witnesses_valid": scan["valid_witnesses"], "support_match": support_match, "candidate_query_ops": scan["oracle_ops"], "baseline_query_ops": baseline["ops"]})
        baseline_target_ops = candidate_target_ops
    candidate_solve_ops = TF.LinearOps()
    baseline_solve_ops = TF.LinearOps()
    candidate_solution = None
    baseline_solution = None
    if candidate_basis.rank == width:
        candidate_solution, candidate_solve_ops = TF.solve_full_rank(candidate_independent, width, q)
    if baseline_basis.rank == width:
        baseline_solution, baseline_solve_ops = TF.solve_full_rank(baseline_independent, width, q)
    candidate_ops = {"advice_precompute": advice.ops, "target_build": TF.asdict(candidate_target_ops), "query": candidate_query_ops, "incremental_matrix": TF.asdict(candidate_basis.ops), "solve": TF.asdict(candidate_solve_ops)}
    baseline_ops = {"advice_build": materialized_build_ops, "target_build": TF.asdict(baseline_target_ops), "query": TF.asdict(baseline_query_ops), "incremental_matrix": TF.asdict(baseline_basis.ops), "solve": TF.asdict(baseline_solve_ops)}
    return {
        "curve_id": curve_record["id"],
        "family": family["family"],
        "mode": mode,
        "dimensions": [a_size, b_size, b_size, b_size, b_size],
        "prefix_limit": prefix_limit,
        "total_prefixes": len(prefix_order),
        "suffixes_per_prefix": len(suffixes),
        "target_budget": target_budget,
        "targets_attempted": len(transcripts),
        "candidate_rank": candidate_basis.rank,
        "baseline_rank": baseline_basis.rank,
        "candidate_full_rank": candidate_basis.rank == width,
        "baseline_full_rank": baseline_basis.rank == width,
        "candidate_solution": candidate_solution,
        "baseline_solution": baseline_solution,
        "candidate_ops": candidate_ops,
        "baseline_ops": baseline_ops,
        "candidate_advice": {"suffix_entries": len(advice.suffix), "retained_bytes": advice.retained_bytes(), "logical_payload_bytes": advice.logical_payload_bytes, "source_input_points": len(advice.a_points) + len(advice.r_points)},
        "materialized_advice": {"d4_entries": materialized["summary"]["d4_entries"], "builder_deep_bytes": materialized["summary"]["builder_deep_bytes"]},
        "transcripts": transcripts,
        "all_witnesses_valid": all(item["candidate_witnesses_valid"] for item in transcripts),
        "all_supports_match": all(item["support_match"] for item in transcripts),
        "total_candidate_unique_queries": sum(item["candidate_query_ops"]["unique_queries"] for item in transcripts),
        "total_full_tensor_queries_if_unbounded": len(transcripts) * a_size * b_size**4,
        "candidate_query_fraction_of_full_tensor": sum(item["candidate_query_ops"]["unique_queries"] for item in transcripts) / max(1, len(transcripts) * a_size * b_size**4),
        "row_digest": digest({"curve_id": curve_record["id"], "family": family["family"], "mode": mode, "candidate_rank": candidate_basis.rank, "baseline_rank": baseline_basis.rank, "transcripts": transcripts}),
        "wall_seconds": time.perf_counter() - started,
    }


def run(input_path: Path, families: list[str], mode: str, target_budget_factor: int) -> dict[str, Any]:
    started = time.perf_counter()
    source = json.loads(input_path.read_text(encoding="utf-8"))
    rows = []
    for instance in source["instances"]:
        by_family = {item["family"]: item for item in instance["families"]}
        for family_name in families:
            rows.append(run_row(instance["curve"], by_family[family_name], mode, target_budget_factor))
    normalized = [{key: value for key, value in row.items() if key != "wall_seconds"} for row in rows]
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-fresh-witness-relation-audit-v1",
        "claim_status": ["OBSERVATION", "TOY-EVIDENCE", "MODEL-BOUND"],
        "source": {"producer_sha256": sha256_file(SCRIPT_PATH), "streaming_sha256": sha256_file(STREAMING_SOURCE), "typed_five_ec_sha256": sha256_file(TYPED_FIVE_SOURCE), "input_sha256": sha256_file(input_path)},
        "config": {"families": families, "mode": mode, "expected_full": mode == "full", "target_budget_factor": target_budget_factor, "relation_seed_rule": "family.run_seed xor 0x13198A2E", "witness_policy": "first exact zero per A after scanning the declared prefix/suffix order", "candidate_direct_predicate": "exact norm equality over source-advice sums", "source_tuple_enumeration": mode == "full"},
        "rows": rows,
        "summary": {
            "rows": len(rows),
            "all_witnesses_valid": all(row["all_witnesses_valid"] for row in rows),
            "all_supports_match": all(row["all_supports_match"] for row in rows),
            "all_candidate_full_rank": all(row["candidate_full_rank"] for row in rows),
            "all_baseline_full_rank": all(row["baseline_full_rank"] for row in rows),
            "all_candidate_full_tensor_mode": all(row["candidate_query_fraction_of_full_tensor"] == 1.0 for row in rows) if mode == "full" else False,
            "mean_candidate_query_fraction_of_full_tensor": sum(row["candidate_query_fraction_of_full_tensor"] for row in rows) / max(1, len(rows)),
            "min_candidate_rank": min(row["candidate_rank"] for row in rows),
            "max_candidate_rank": max(row["candidate_rank"] for row in rows),
            "breakthrough_claim": False,
            "algorithm_promotion_gate": False,
            "boundary": "Fresh witness-bearing relation audit; full mode is an explicit B^5 scan control and truncated mode is an expected negative. No generic ECDLP claim.",
        },
        "result_digest": digest(normalized),
        "total_wall_seconds": time.perf_counter() - started,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--families", nargs="+", required=True)
    parser.add_argument("--mode", choices=("full", "truncated"), default="full")
    parser.add_argument("--target-budget-factor", type=int, default=4)
    args = parser.parse_args()
    if args.target_budget_factor < 1:
        raise SystemExit("target-budget-factor must be positive")
    print(json.dumps(run(args.input, args.families, args.mode, args.target_budget_factor), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
