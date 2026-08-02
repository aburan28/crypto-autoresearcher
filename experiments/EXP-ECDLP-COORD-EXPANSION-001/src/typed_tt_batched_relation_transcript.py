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
BATCH_SOURCE = SCRIPT_PATH.with_name("typed_tt_batched_source_sum.py")


def load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BATCH = load("typed_tt_batching_for_relation_transcript", BATCH_SOURCE)
ROWSPACE = BATCH.ROWSPACE
ADAPTIVE = BATCH.ADAPTIVE
STREAMING = BATCH.STREAMING
TF = BATCH.TF
ORACLE = BATCH.ORACLE


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add_ops(total: dict[str, int], extra: dict[str, int]) -> None:
    for key, value in extra.items():
        total[key] = total.get(key, 0) + int(value)


def locate_target(
    predicates: Any,
    target_index: int,
    skeleton: dict[str, Any],
    a_size: int,
    b_size: int,
) -> dict[str, Any]:
    prefixes = ADAPTIVE.SOURCE_AWARE.prefix_order(a_size, b_size)
    suffixes = ADAPTIVE.SOURCE_AWARE.suffix_indices(b_size)
    rank = skeleton["rank"]
    pivot_columns = skeleton["pivot_columns"]
    inverse = skeleton["inverse"]
    basis = skeleton["basis_rows"]
    reconstruction_ops = BATCH.zero_ops()
    hits = []
    for prefix in prefixes:
        sampled = [predicates.value(target_index, prefix + suffixes[column]) for column in pivot_columns]
        coefficients = ADAPTIVE.SOURCE_AWARE.row_times_matrix(sampled, inverse, predicates.p)
        reconstruction_ops["field_multiplications"] += rank * rank
        reconstruction_ops["field_additions"] += rank * max(0, rank - 1)
        for column, suffix in enumerate(suffixes):
            predicted = sum(coefficients[index] * basis[index][column] for index in range(rank)) % predicates.p
            reconstruction_ops["field_multiplications"] += rank
            reconstruction_ops["field_additions"] += max(0, rank - 1)
            if predicted == 0:
                indices = prefix + suffix
                hits.append({"indices": list(indices), "a_index": indices[0], "suffix_column": column})
    return {
        "hits": hits,
        "predicted_entries": len(prefixes) * len(suffixes),
        "specialization_queries": len(prefixes) * rank,
        "reconstruction_ops": reconstruction_ops,
    }


def witness_valid(curve: Any, a_points: list[Any], r_points: list[Any], indices: tuple[int, ...], target: Any, ops: Any) -> bool:
    total = a_points[indices[0]]
    for index in indices[1:]:
        total = curve.add(total, r_points[index], ops)
    return total == target


def reference_mismatches(
    curve_record: dict[str, Any],
    family: dict[str, Any],
    target: tuple[int, int],
    predicate_cache: dict[tuple[int, ...], int],
) -> tuple[int, int]:
    reference = ORACLE.Oracle(curve_record, ROWSPACE.target_family(family, list(target)))
    mismatches = 0
    for indices, value in predicate_cache.items():
        mismatches += int(value != reference.value(indices))
    return mismatches, len(predicate_cache)


def run_mode(
    curve_record: dict[str, Any],
    family: dict[str, Any],
    targets: list[tuple[int, int]],
    baseline_targets: list[dict[str, Any]],
    materialized: dict[str, Any],
    mode: str,
) -> dict[str, Any]:
    p = curve_record["p"]
    q = curve_record["q"]
    curve = TF.Curve(p, curve_record["a"], curve_record["b"])
    a_points = [TF.point_from_json(value) for value in family["progression"]["points"]]
    r_points = [TF.point_from_json(value) for value in family["factor_base"]["points"]]
    a_size = len(a_points)
    b_size = len(r_points)
    width = b_size + 1
    advice = STREAMING.StreamingSourceAdvice(curve_record, family)
    source = BATCH.SourceSumCache(advice, mode == "shared_source_sums")
    predicates = BATCH.BatchedPredicates(source, targets, p)
    skeleton = ADAPTIVE.adaptive_build(predicates.target_view(0), a_size, b_size)
    source.update_peak()
    rank_ops = dict(skeleton["rank_counters"])
    matrix = TF.IncrementalBasis(width, q)
    witness_ops = TF.Ops()
    relation_equations: list[dict[str, Any]] = []
    transcripts = []
    reconstruction_ops = BATCH.zero_ops()
    reference_mismatch_total = 0
    reference_query_total = 0
    source_snapshots = []
    for target_index, target in enumerate(targets):
        located = locate_target(predicates, target_index, skeleton, a_size, b_size)
        target_point = TF.point_from_json([int(target[0]), int(target[1])])
        valid = all(
            witness_valid(curve, a_points, r_points, tuple(item["indices"]), target_point, witness_ops)
            for item in located["hits"]
        )
        expected = baseline_targets[target_index].get("expected_witness")
        expected_witness_valid = True
        candidate_contains_expected_witness = True
        if expected is not None:
            expected_indices = (int(expected["a_index"]), *[int(value) for value in expected["r_witness"]])
            expected_witness_valid = witness_valid(curve, a_points, r_points, expected_indices, target_point, witness_ops)
            candidate_contains_expected_witness = any(tuple(item["indices"]) == expected_indices for item in located["hits"])
        direct_mismatches, reference_queries = reference_mismatches(
            curve_record, family, target, predicates.caches[target_index]
        )
        baseline_hits = baseline_targets[target_index]["hits"]
        candidate_a = {item["a_index"] for item in located["hits"]}
        baseline_a = {item["a_index"] for item in baseline_hits}
        candidate_equations = []
        for item in located["hits"]:
            coefficients = TF.quotient_relation_coefficients(item["a_index"], tuple(item["indices"][1:]), b_size)
            equation = {
                "coefficients": coefficients,
                "rhs": baseline_targets[target_index]["scalar"],
                "a_index": item["a_index"],
                "r_witness": item["indices"][1:],
            }
            candidate_equations.append(equation)
            if matrix.insert(coefficients, equation["rhs"]):
                relation_equations.append(equation)
        add_ops(reconstruction_ops, located["reconstruction_ops"])
        reference_mismatch_total += direct_mismatches
        reference_query_total += reference_queries
        source.update_peak()
        source_snapshots.append(dict(source.ops))
        transcripts.append({
            "target_index": target_index,
            "scalar": baseline_targets[target_index]["scalar"],
            "target": list(target),
            "label": baseline_targets[target_index].get("label", f"relation_{target_index}"),
            "held_out_supported": baseline_targets[target_index].get("held_out_supported", False),
            "expected_witness": baseline_targets[target_index].get("expected_witness"),
            "expected_witness_valid": expected_witness_valid,
            "candidate_contains_expected_witness": candidate_contains_expected_witness,
            "candidate_hits": located["hits"],
            "baseline_hits": baseline_hits,
            "candidate_witnesses_valid": valid,
            "support_match": candidate_a == baseline_a,
            "direct_reference_mismatches": direct_mismatches,
            "reference_queries": reference_queries,
            "candidate_rank_after_target": matrix.rank,
            "candidate_equation_count": len(candidate_equations),
            "predicted_entries": located["predicted_entries"],
        })
        if mode == "target_separated_control":
            source.discard_target(target_index)
            predicates.discard_target(target_index)
    solve_ops = TF.LinearOps()
    solution = None
    if matrix.rank == width:
        solution, solve_ops = TF.solve_full_rank(relation_equations, width, q)
    return {
        "mode": mode,
        "dimensions": [a_size, b_size, b_size, b_size, b_size],
        "target_count": len(targets),
        "rowspace_rank": skeleton["rank"],
        "rowspace_prefixes_examined": skeleton["candidate_prefixes_examined"],
        "rowspace_stopping_reason": skeleton["stopping_reason"],
        "candidate_rank": matrix.rank,
        "candidate_full_rank": matrix.rank == width,
        "candidate_solution": solution,
        "diagnostic_solution_digest": digest(solution) if solution is not None else None,
        "candidate_source_ops": dict(source.ops),
        "candidate_source_snapshots": source_snapshots,
        "candidate_predicate_ops": [dict(item) for item in predicates.ops],
        "candidate_reconstruction_ops": reconstruction_ops,
        "candidate_rank_ops": rank_ops,
        "candidate_relation_matrix_ops": TF.asdict(matrix.ops),
        "candidate_witness_ops": TF.asdict(witness_ops),
        "candidate_solve_ops": TF.asdict(solve_ops),
        "candidate_advice_build_ops": dict(advice.ops),
        "candidate_advice": {
            "retained_bytes": advice.retained_bytes(),
            "logical_payload_bytes": advice.logical_payload_bytes,
            "source_cache_peak_bytes": source.peak_cache_bytes,
            "source_cache_peak_entries": source.peak_cache_entries,
            "source_cache_logical_payload_bytes": source.peak_cache_entries * advice.point_payload_bytes,
        },
        "transcripts": transcripts,
        "all_candidate_witnesses_valid": all(item["candidate_witnesses_valid"] for item in transcripts),
        "all_supports_match": all(item["support_match"] for item in transcripts),
        "all_held_out_supported_coverage": all(
            not item["held_out_supported"] or (item["support_match"] and item["candidate_witnesses_valid"] and item["expected_witness_valid"] and item["candidate_contains_expected_witness"])
            for item in transcripts
        ),
        "all_direct_reference_exact": reference_mismatch_total == 0,
        "direct_reference_mismatches": reference_mismatch_total,
        "direct_reference_queries": reference_query_total,
        "candidate_predicted_entries": sum(item["predicted_entries"] for item in transcripts),
        "candidate_source_queries": source.ops["unique_queries"],
        "row_digest": digest({"mode": mode, "rank": skeleton["rank"], "candidate_rank": matrix.rank, "transcripts": transcripts}),
    }


def run_row(curve_record: dict[str, Any], family: dict[str, Any]) -> dict[str, Any]:
    p = curve_record["p"]
    q = curve_record["q"]
    curve = TF.Curve(p, curve_record["a"], curve_record["b"])
    generator = TF.point_from_json(curve_record["generator"])
    a_points = [TF.point_from_json(value) for value in family["progression"]["points"]]
    r_points = [TF.point_from_json(value) for value in family["factor_base"]["points"]]
    b_size = len(r_points)
    materialized = TF.compile_r_support(curve, r_points)
    baseline_targets = []
    target_ops = TF.Ops()
    target_limit = b_size + 1
    seed = family["run_seed"] ^ 0x13198A2E
    targets = []
    for index, scalar in enumerate(TF.nonzero_scalar_stream(q, seed)):
        if index == target_limit:
            break
        target = curve.mul(scalar, generator, target_ops)
        target_json = TF.point_json(target)
        baseline = TF.query_d4_all(curve, a_points, r_points, materialized["d4_internal"], target)
        baseline_targets.append({"label": f"relation_{index}", "scalar": scalar, "target": target_json, "hits": baseline["hits"], "ops": baseline["ops"], "held_out_supported": False, "expected_witness": None})
        targets.append((int(target_json[0]), int(target_json[1])))
    seen_targets = set(targets)
    held_out_added = 0
    for item in family["held_out_descent"]["transcript"]:
        if held_out_added == 4 or not (item["materialized_d4"]["success"] and item["r_scan_plus_d3"]["success"]):
            continue
        target_json = item["target"]
        target_tuple = (int(target_json[0]), int(target_json[1]))
        if target_tuple in seen_targets:
            continue
        target = TF.point_from_json(target_json)
        baseline = TF.query_d4_all(curve, a_points, r_points, materialized["d4_internal"], target)
        baseline_targets.append({
            "label": f"held_out_supported_{held_out_added}",
            "scalar": int(item["scalar"]),
            "target": target_json,
            "hits": baseline["hits"],
            "ops": baseline["ops"],
            "held_out_supported": True,
            "expected_witness": {"a_index": item["r_scan_plus_d3"]["a_index"], "r_witness": item["r_scan_plus_d3"]["r_witness"]},
        })
        targets.append(target_tuple)
        seen_targets.add(target_tuple)
        held_out_added += 1
    separated = run_mode(curve_record, family, targets, baseline_targets, materialized, "target_separated_control")
    shared = run_mode(curve_record, family, targets, baseline_targets, materialized, "shared_source_sums")
    baseline_query_ops = TF.Ops()
    for item in baseline_targets:
        for key, value in item["ops"].items():
            setattr(baseline_query_ops, key, getattr(baseline_query_ops, key) + value)
    materialized_build_ops = BATCH.zero_ops()
    for profile in materialized["summary"]["profiles"]:
        add_ops(materialized_build_ops, profile["build_ops"])
    return {
        "curve_id": curve_record["id"],
        "family": family["family"],
        "dimensions": shared["dimensions"],
        "target_count": len(targets),
        "target_build_ops": TF.asdict(target_ops),
        "baseline_advice_build_ops": materialized_build_ops,
        "baseline_query_ops": TF.asdict(baseline_query_ops),
        "baseline_advice": {
            "d4_entries": materialized["summary"]["d4_entries"],
            "builder_deep_bytes": materialized["summary"]["builder_deep_bytes"],
        },
        "target_separated_control": separated,
        "shared_candidate": shared,
        "same_rowspace_rank": separated["rowspace_rank"] == shared["rowspace_rank"],
        "same_relation_rank": separated["candidate_rank"] == shared["candidate_rank"],
        "same_support": separated["all_supports_match"] and shared["all_supports_match"],
        "diagnostic_solution_digest": family["diagnostic"]["expected_solution_digest"],
        "shared_diagnostic_solution_match": shared["diagnostic_solution_digest"] == family["diagnostic"]["expected_solution_digest"],
        "control_diagnostic_solution_match": separated["diagnostic_solution_digest"] == family["diagnostic"]["expected_solution_digest"],
        "strict_source_add_saving": shared["candidate_source_ops"]["point_add_calls"] < separated["candidate_source_ops"]["point_add_calls"],
        "row_digest": digest({"curve_id": curve_record["id"], "family": family["family"], "separated": separated["row_digest"], "shared": shared["row_digest"]}),
    }


def run(input_path: Path, families: list[str], curve_id: str | None = None) -> dict[str, Any]:
    started = time.perf_counter()
    source = json.loads(input_path.read_text(encoding="utf-8"))
    rows = []
    for instance in source["instances"]:
        if curve_id is not None and instance["curve"]["id"] != curve_id:
            continue
        by_family = {item["family"]: item for item in instance["families"]}
        for family_name in families:
            rows.append(run_row(instance["curve"], by_family[family_name]))
    normalized = [{key: value for key, value in row.items() if key != "wall_seconds"} for row in rows]
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-batched-relation-transcript-v1",
        "claim_status": ["OBSERVATION", "TOY-EVIDENCE", "MODEL-BOUND"],
        "source": {
            "producer_sha256": sha256_file(SCRIPT_PATH),
            "batch_source_sha256": sha256_file(BATCH_SOURCE),
            "input_sha256": sha256_file(input_path),
        },
        "config": {
            "families": families,
            "curve_id": curve_id or "all",
            "targets_per_row": "B+1",
            "rowspace": "adaptive dependent-prefix plateau",
            "locator": "full predicted suffix scan with pivot-only source queries",
            "shared_mode": "source sums keyed by indices",
            "control_mode": "source sums keyed by target and indices, discarded per target",
            "baseline": "independently rebuilt materialized typed D4",
            "source_tuple_enumeration": False,
            "full_predicted_suffix_scan": True,
        },
        "rows": rows,
        "summary": {
            "rows": len(rows),
            "all_witnesses_valid": all(row["shared_candidate"]["all_candidate_witnesses_valid"] and row["target_separated_control"]["all_candidate_witnesses_valid"] for row in rows),
            "all_supports_match": all(row["same_support"] for row in rows),
            "all_held_out_supported_coverage": all(row["shared_candidate"]["all_held_out_supported_coverage"] and row["target_separated_control"]["all_held_out_supported_coverage"] for row in rows),
            "all_direct_reference_exact": all(row["shared_candidate"]["all_direct_reference_exact"] and row["target_separated_control"]["all_direct_reference_exact"] for row in rows),
            "all_same_rowspace_rank": all(row["same_rowspace_rank"] for row in rows),
            "all_same_relation_rank": all(row["same_relation_rank"] for row in rows),
            "all_diagnostic_solution_matches": all(row["shared_diagnostic_solution_match"] and row["control_diagnostic_solution_match"] for row in rows),
            "all_candidate_full_rank": all(row["shared_candidate"]["candidate_full_rank"] for row in rows),
            "all_strict_source_add_saving": all(row["strict_source_add_saving"] for row in rows),
            "breakthrough_claim": False,
            "algorithm_promotion_gate": False,
            "boundary": "Fixed-curve shared-source-sum row-space relation transcript on small generated curves; no generic ECDLP or exponent claim.",
        },
        "total_wall_seconds": time.perf_counter() - started,
        "result_digest": digest(normalized),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--families", nargs="+", required=True)
    parser.add_argument("--curve-id")
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.families, args.curve_id), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
