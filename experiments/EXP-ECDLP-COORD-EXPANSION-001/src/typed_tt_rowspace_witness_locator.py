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
ADAPTIVE_SOURCE = SCRIPT_PATH.with_name("typed_tt_adaptive_skeleton_preflight.py")
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


ADAPTIVE = load("typed_tt_adaptive_for_rowspace_locator", ADAPTIVE_SOURCE)
STREAMING = load("typed_tt_streaming_for_rowspace_locator", STREAMING_SOURCE)
TF = load("typed_five_ec_for_rowspace_locator", TYPED_FIVE_SOURCE)
ORACLE = STREAMING.ORACLE


def digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def zero_ops() -> dict[str, int]:
    return {
        "point_add_calls": 0,
        "field_inversions": 0,
        "field_multiplications": 0,
        "field_subtractions": 0,
        "field_additions": 0,
        "cache_hits": 0,
        "unique_queries": 0,
        "source_advice_reads": 0,
        "logical_source_read_bytes": 0,
        "zero_hits": 0,
    }


def add_ops(total: dict[str, int], extra: dict[str, int]) -> None:
    for key, value in extra.items():
        total[key] = total.get(key, 0) + int(value)


class SourceOracle:
    """Target-specialized source-advice predicate with cached source queries."""

    def __init__(self, advice: Any, target: tuple[int, int]) -> None:
        self.advice = advice
        self.p = advice.p
        self.nu = ORACLE.nonsquare(self.p)
        self.target = target
        self.cache: dict[tuple[int, ...], int] = {}
        self.ops = zero_ops()

    def value(self, indices: tuple[int, ...]) -> int:
        cached = self.cache.get(indices)
        if cached is not None:
            self.ops["cache_hits"] += 1
            return cached
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
        self.cache[indices] = result
        self.ops["unique_queries"] += 1
        self.ops["zero_hits"] += int(result == 0)
        return result


def target_family(family: dict[str, Any], target: list[int]) -> dict[str, Any]:
    return ADAPTIVE.SOURCE_AWARE.target_family(family, target)


def suffixes(b_size: int) -> list[tuple[int, int]]:
    return ADAPTIVE.SOURCE_AWARE.suffix_indices(b_size)


def reconstruct_and_locate(
    oracle: SourceOracle,
    skeleton: dict[str, Any],
    a_size: int,
    b_size: int,
) -> dict[str, Any]:
    prefixes = ADAPTIVE.SOURCE_AWARE.prefix_order(a_size, b_size)
    suffix_list = suffixes(b_size)
    rank = skeleton["rank"]
    pivot_columns = skeleton["pivot_columns"]
    inverse = skeleton["inverse"]
    basis = skeleton["basis_rows"]
    reconstruction_ops = zero_ops()
    hits: list[dict[str, Any]] = []
    for prefix in prefixes:
        sampled = [oracle.value(prefix + suffix_list[column]) for column in pivot_columns]
        coefficients = ADAPTIVE.SOURCE_AWARE.row_times_matrix(sampled, inverse, oracle.p)
        reconstruction_ops["field_multiplications"] += rank * rank
        reconstruction_ops["field_additions"] += rank * max(0, rank - 1)
        for column, suffix in enumerate(suffix_list):
            predicted = 0
            for index in range(rank):
                predicted += coefficients[index] * basis[index][column]
            predicted %= oracle.p
            reconstruction_ops["field_multiplications"] += rank
            reconstruction_ops["field_additions"] += max(0, rank - 1)
            if predicted == 0:
                indices = prefix + suffix
                hits.append({"indices": list(indices), "a_index": indices[0], "suffix_column": column})
    return {
        "hits": hits,
        "reconstruction_ops": reconstruction_ops,
        "predicted_entries": len(prefixes) * len(suffix_list),
        "specialization_queries": len(prefixes) * rank,
    }


def direct_witness_valid(
    curve: Any,
    a_points: list[Any],
    r_points: list[Any],
    indices: tuple[int, ...],
    target: Any,
    ops: Any,
) -> bool:
    total = a_points[indices[0]]
    for index in indices[1:]:
        total = curve.add(total, r_points[index], ops)
    return total == target


def first_per_a(hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    chosen: dict[int, dict[str, Any]] = {}
    for hit in hits:
        chosen.setdefault(hit["a_index"], hit)
    return [chosen[index] for index in sorted(chosen)]


def run_row(
    curve_record: dict[str, Any],
    family: dict[str, Any],
    mode: str,
    target_budget_factor: int,
) -> dict[str, Any]:
    started = time.perf_counter()
    p = curve_record["p"]
    q = curve_record["q"]
    curve_typed = TF.Curve(p, curve_record["a"], curve_record["b"])
    generator = TF.point_from_json(curve_record["generator"])
    a_points_typed = [TF.point_from_json(value) for value in family["progression"]["points"]]
    r_points_typed = [TF.point_from_json(value) for value in family["factor_base"]["points"]]
    a_size = len(a_points_typed)
    b_size = len(r_points_typed)
    width = b_size + 1
    full_entries_per_target = a_size * b_size**4
    advice = STREAMING.StreamingSourceAdvice(curve_record, family)
    materialized = TF.compile_r_support(curve_typed, r_points_typed)
    materialized_build_ops = zero_ops()
    for profile in materialized["summary"]["profiles"]:
        add_ops(materialized_build_ops, profile["build_ops"])
    candidate_source_ops = zero_ops()
    candidate_reconstruction_ops = zero_ops()
    candidate_rank_ops = zero_ops()
    candidate_witness_ops = TF.Ops()
    target_ops = TF.Ops()
    baseline_query_ops = TF.Ops()
    candidate_basis = TF.IncrementalBasis(width, q)
    baseline_basis = TF.IncrementalBasis(width, q)
    transcripts: list[dict[str, Any]] = []
    skeleton_ranks: list[int] = []
    reusable_skeleton: dict[str, Any] | None = None
    reusable_target: list[int] | None = None
    target_budget = min(q - 1, target_budget_factor * width)
    relation_seed = family["run_seed"] ^ 0x13198A2E
    for scalar_index, scalar in enumerate(TF.nonzero_scalar_stream(q, relation_seed)):
        if scalar_index == target_budget:
            break
        target = curve_typed.mul(scalar, generator, target_ops)
        target_json = TF.point_json(target)
        target_oracle = ORACLE.point(target_json)
        if mode == "per_target" or reusable_skeleton is None:
            oracle_for_build = SourceOracle(advice, target_oracle)
            skeleton = ADAPTIVE.adaptive_build(oracle_for_build, a_size, b_size)
            add_ops(candidate_source_ops, oracle_for_build.ops)
            add_ops(candidate_rank_ops, skeleton["rank_counters"])
            if reusable_skeleton is None:
                reusable_skeleton = skeleton
                reusable_target = target_json
        else:
            skeleton = reusable_skeleton
        skeleton_ranks.append(skeleton["rank"])
        oracle = SourceOracle(advice, target_oracle)
        located = reconstruct_and_locate(oracle, skeleton, a_size, b_size)
        add_ops(candidate_source_ops, oracle.ops)
        add_ops(candidate_reconstruction_ops, located["reconstruction_ops"])
        baseline = TF.query_d4_all(curve_typed, a_points_typed, r_points_typed, materialized["d4_internal"], target)
        for key, value in baseline["ops"].items():
            setattr(baseline_query_ops, key, getattr(baseline_query_ops, key) + value)
        candidate_hits = located["hits"]
        candidate_a = {item["a_index"] for item in candidate_hits}
        baseline_a = {item["a_index"] for item in baseline["hits"]}
        all_candidate_witnesses_valid = all(
            direct_witness_valid(
                curve_typed,
                a_points_typed,
                r_points_typed,
                tuple(item["indices"]),
                target,
                candidate_witness_ops,
            )
            for item in candidate_hits
        )
        support_match = candidate_a == baseline_a
        candidate_equations = []
        for hit in first_per_a(candidate_hits):
            coefficients = TF.quotient_relation_coefficients(hit["a_index"], tuple(hit["indices"][1:]), b_size)
            equation = {"coefficients": coefficients, "rhs": scalar, "a_index": hit["a_index"], "r_witness": hit["indices"][1:]}
            candidate_equations.append(equation)
            candidate_basis.insert(coefficients, scalar)
        for hit in baseline["hits"]:
            coefficients = TF.quotient_relation_coefficients(hit["a_index"], hit["r_witness"], b_size)
            baseline_basis.insert(coefficients, scalar)
        transcripts.append({
            "scalar": scalar,
            "target": target_json,
            "candidate_hits": candidate_hits,
            "candidate_equations": candidate_equations,
            "baseline_hits": baseline["hits"],
            "candidate_rank": skeleton["rank"],
            "rowspace_rank": skeleton["rank"],
            "candidate_prefixes_examined": skeleton["candidate_prefixes_examined"],
            "candidate_witnesses_valid": all_candidate_witnesses_valid,
            "support_match": support_match,
            "candidate_source_queries": oracle.ops["unique_queries"],
            "predicted_entries": located["predicted_entries"],
        })
    candidate_solve_ops = TF.LinearOps()
    baseline_solve_ops = TF.LinearOps()
    candidate_independent = []
    baseline_independent = []
    for transcript in transcripts:
        candidate_independent.extend(transcript["candidate_equations"])
        for hit in transcript["baseline_hits"]:
            coefficients = TF.quotient_relation_coefficients(hit["a_index"], hit["r_witness"], b_size)
            baseline_independent.append({"coefficients": coefficients, "rhs": transcript["scalar"]})
    candidate_solution = None
    baseline_solution = None
    if candidate_basis.rank == width:
        candidate_solution, candidate_solve_ops = TF.solve_full_rank(candidate_independent, width, q)
    if baseline_basis.rank == width:
        baseline_solution, baseline_solve_ops = TF.solve_full_rank(baseline_independent, width, q)
    return {
        "curve_id": curve_record["id"],
        "family": family["family"],
        "mode": mode,
        "dimensions": [a_size, b_size, b_size, b_size, b_size],
        "target_budget": target_budget,
        "targets_attempted": len(transcripts),
        "reusable_skeleton_target": reusable_target,
        "rowspace_ranks": sorted(set(skeleton_ranks)),
        "candidate_rank": candidate_basis.rank,
        "baseline_rank": baseline_basis.rank,
        "candidate_full_rank": candidate_basis.rank == width,
        "baseline_full_rank": baseline_basis.rank == width,
        "candidate_solution": candidate_solution,
        "baseline_solution": baseline_solution,
        "candidate_source_ops": candidate_source_ops,
        "candidate_reconstruction_ops": candidate_reconstruction_ops,
        "candidate_rank_ops": candidate_rank_ops,
        "candidate_relation_matrix_ops": TF.asdict(candidate_basis.ops),
        "candidate_witness_ops": TF.asdict(candidate_witness_ops),
        "candidate_advice_build_ops": advice.ops,
        "candidate_target_build_ops": TF.asdict(target_ops),
        "candidate_solve_ops": TF.asdict(candidate_solve_ops),
        "baseline_advice_build_ops": materialized_build_ops,
        "baseline_target_build_ops": TF.asdict(target_ops),
        "baseline_query_ops": TF.asdict(baseline_query_ops),
        "baseline_matrix_ops": TF.asdict(baseline_basis.ops),
        "baseline_solve_ops": TF.asdict(baseline_solve_ops),
        "candidate_advice": {
            "retained_bytes": advice.retained_bytes(),
            "logical_payload_bytes": advice.logical_payload_bytes,
            "suffix_entries": len(advice.suffix),
        },
        "materialized_advice": {
            "d4_entries": materialized["summary"]["d4_entries"],
            "builder_deep_bytes": materialized["summary"]["builder_deep_bytes"],
        },
        "transcripts": transcripts,
        "all_candidate_witnesses_valid": all(item["candidate_witnesses_valid"] for item in transcripts),
        "all_supports_match": all(item["support_match"] for item in transcripts),
        "candidate_source_query_fraction": sum(item["candidate_source_queries"] for item in transcripts) / max(1, len(transcripts) * full_entries_per_target),
        "candidate_predicted_entries_fraction": sum(item["predicted_entries"] for item in transcripts) / max(1, len(transcripts) * full_entries_per_target),
        "row_digest": digest({"curve_id": curve_record["id"], "family": family["family"], "mode": mode, "transcripts": transcripts}),
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
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-rowspace-witness-locator-v1",
        "claim_status": ["HYPOTHESIS", "OBSERVATION", "TOY-EVIDENCE", "MODEL-BOUND"],
        "source": {
            "producer_sha256": sha256_file(SCRIPT_PATH),
            "adaptive_sha256": sha256_file(ADAPTIVE_SOURCE),
            "streaming_sha256": sha256_file(STREAMING_SOURCE),
            "typed_five_ec_sha256": sha256_file(TYPED_FIVE_SOURCE),
            "input_sha256": sha256_file(input_path),
        },
        "config": {
            "families": families,
            "mode": mode,
            "target_budget_factor": target_budget_factor,
            "rank_discovery": "adaptive dependent-prefix plateau",
            "candidate_locator": "target-conditioned row-space reconstruction over all suffix columns",
            "source_tuple_enumeration": False,
            "suffix_reconstruction_enumeration": True,
            "target_stream": "family.run_seed xor 0x13198A2E",
        },
        "rows": rows,
        "summary": {
            "rows": len(rows),
            "all_candidate_witnesses_valid": all(row["all_candidate_witnesses_valid"] for row in rows),
            "all_supports_match": all(row["all_supports_match"] for row in rows),
            "all_candidate_full_rank": all(row["candidate_full_rank"] for row in rows),
            "all_baseline_full_rank": all(row["baseline_full_rank"] for row in rows),
            "mean_candidate_source_query_fraction": sum(row["candidate_source_query_fraction"] for row in rows) / max(1, len(rows)),
            "max_candidate_source_query_fraction": max(row["candidate_source_query_fraction"] for row in rows),
            "mean_candidate_predicted_entries_fraction": sum(row["candidate_predicted_entries_fraction"] for row in rows) / max(1, len(rows)),
            "all_per_target_exact": mode == "per_target" and all(row["all_supports_match"] and row["all_candidate_witnesses_valid"] for row in rows),
            "reuse_control": mode == "reuse",
            "breakthrough_claim": False,
            "algorithm_promotion_gate": False,
            "boundary": "Target-conditioned TT row-space witness locator; source queries are sub-enumerative but suffix reconstruction remains exhaustive and no generic ECDLP claim is made.",
        },
        "result_digest": digest(normalized),
        "total_wall_seconds": time.perf_counter() - started,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--families", nargs="+", required=True)
    parser.add_argument("--mode", choices=("per_target", "reuse"), default="per_target")
    parser.add_argument("--target-budget-factor", type=int, default=1)
    args = parser.parse_args()
    if args.target_budget_factor < 1:
        raise SystemExit("target-budget-factor must be positive")
    print(json.dumps(run(args.input, args.families, args.mode, args.target_budget_factor), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
