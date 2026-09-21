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
TYPED_FIVE_SOURCE = SCRIPT_PATH.with_name("typed_five_ec.py")


def load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


TF = load("typed_five_ec_for_downstream_accounting", TYPED_FIVE_SOURCE)


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def zero_ops() -> dict[str, int]:
    return {
        "field_inversions": 0,
        "field_multiplications": 0,
        "field_additions": 0,
        "group_operations": 0,
        "point_additions": 0,
        "point_doublings": 0,
        "row_additions": 0,
    }


def add_ops(total: dict[str, int], value: dict[str, int]) -> None:
    for key, item in value.items():
        total[key] = total.get(key, 0) + int(item)


def profile_ops(summary: dict[str, Any]) -> dict[str, int]:
    total = zero_ops()
    for profile in summary["profiles"]:
        add_ops(total, profile["build_ops"])
    return total


def typed_ops(value: dict[str, Any]) -> dict[str, int]:
    result = zero_ops()
    add_ops(result, value)
    return result


def recovery_ops(width: int, verified_targets: int, paths: int = 2) -> dict[str, int]:
    total = zero_ops()
    evaluations = verified_targets * paths
    total["field_multiplications"] = evaluations * width
    total["field_additions"] = evaluations * max(0, width - 1)
    return total


def reconstruct_row(
    curve_record: dict[str, Any],
    family: dict[str, Any],
    batch_row: dict[str, Any],
    negative_batch_row: dict[str, Any],
) -> dict[str, Any]:
    started = time.perf_counter()
    curve = TF.Curve(curve_record["p"], curve_record["a"], curve_record["b"])
    generator = TF.point_from_json(curve_record["generator"])
    a_points = [TF.point_from_json(value) for value in family["progression"]["points"]]
    r_points = [TF.point_from_json(value) for value in family["factor_base"]["points"]]
    compiler = TF.compile_r_support(curve, r_points)
    relation_seed = family["run_seed"] ^ 0x13198A2E
    relation = TF.collect_relations(curve, curve_record["q"], generator, a_points, r_points, compiler["d4_internal"], relation_seed)
    descent_seed = family["run_seed"] ^ 0x03707344
    descent = TF.held_out_descent(
        curve,
        curve_record["q"],
        generator,
        a_points,
        r_points,
        compiler["d3_internal"],
        compiler["d4_internal"],
        relation["solution_internal"],
        relation["attempted_scalars_internal"],
        descent_seed,
        family["held_out_descent"]["target_count"],
    )
    relation_expected = family["relations"]
    descent_expected = family["held_out_descent"]
    relation_collection_ops = zero_ops()
    add_ops(relation_collection_ops, profile_ops(compiler["summary"]))
    add_ops(relation_collection_ops, typed_ops(relation["summary"]["target_build_ops"]))
    add_ops(relation_collection_ops, typed_ops(relation["summary"]["query_ops"]))
    matrix_ops = zero_ops()
    add_ops(matrix_ops, typed_ops(relation["summary"]["incremental_linear_ops"]))
    add_ops(matrix_ops, typed_ops(relation["summary"]["solve_linear_ops"]))
    materialized_descent_ops = typed_ops(descent["materialized_d4"]["query_ops"])
    alternate_descent_ops = typed_ops(descent["r_scan_plus_d3"]["query_ops"])
    descent_build_ops = typed_ops(descent["target_build_ops"])
    coefficient_recovery_ops = recovery_ops(len(r_points) + 1, descent["verified_targets"], 2)
    downstream_ops = zero_ops()
    add_ops(downstream_ops, relation_collection_ops)
    add_ops(downstream_ops, matrix_ops)
    add_ops(downstream_ops, descent_build_ops)
    add_ops(downstream_ops, materialized_descent_ops)
    add_ops(downstream_ops, alternate_descent_ops)
    add_ops(downstream_ops, coefficient_recovery_ops)
    full_batch = next(batch for batch in batch_row["batches"] if batch["label"] == "full")
    negative_full_batch = next(batch for batch in negative_batch_row["batches"] if batch["label"] == "full")
    public_digest = TF.canonical_digest({"factor_base_digest": family["factor_base"]["digest"], "progression_digest": family["progression"]["digest"]})
    return {
        "curve_id": curve_record["id"],
        "family": family["family"],
        "q": curve_record["q"],
        "a_size": len(a_points),
        "b_size": len(r_points),
        "public_construction_digest": public_digest,
        "compiler": {
            "d3_entries": compiler["summary"]["d3_entries"],
            "d4_entries": compiler["summary"]["d4_entries"],
            "digest": compiler["summary"]["digest"],
            "persistent_json_bytes": compiler["summary"]["persistent_json_bytes"],
            "builder_deep_bytes": compiler["summary"]["builder_deep_bytes"],
            "build_ops": profile_ops(compiler["summary"]),
        },
        "relation": {
            "seed": relation_seed,
            "transcript_digest": relation["summary"]["target_transcript_digest"],
            "expected_transcript_digest": relation_expected["target_transcript_digest"],
            "independent_equations_digest": digest(relation["summary"]["independent_equations"]),
            "expected_independent_equations_digest": digest(relation_expected["independent_equations"]),
            "attack_solution": relation["summary"]["attack_solution"],
            "expected_attack_solution": relation_expected["attack_solution"],
            "quotient_rank": relation["summary"]["quotient_rank"],
            "expected_quotient_rank": relation_expected["quotient_rank"],
            "targets_attempted": relation["summary"]["targets_attempted"],
            "candidate_relation_rows": relation["summary"]["candidate_relation_rows"],
            "independent_rows": relation["summary"]["independent_rows"],
            "relation_collection_ops": relation_collection_ops,
            "matrix_ops": matrix_ops,
        },
        "descent": {
            "seed": descent_seed,
            "transcript_digest": descent["transcript_digest"],
            "expected_transcript_digest": descent_expected["transcript_digest"],
            "target_count": descent["target_count"],
            "supported_targets": descent["supported_targets"],
            "verified_targets": descent["verified_targets"],
            "success_probability": descent["success_probability"],
            "materialized_d4_ops": materialized_descent_ops,
            "r_scan_plus_d3_ops": alternate_descent_ops,
            "target_build_ops": descent_build_ops,
            "coefficient_recovery_ops": coefficient_recovery_ops,
        },
        "downstream_ops": downstream_ops,
        "candidate_batch": {
            "full_target_count": full_batch["target_count"],
            "all_exact": full_batch["all_exact"],
            "all_direct_reference_exact": full_batch["all_direct_reference_exact"],
            "charged_source_ops": full_batch["charged_source_ops"],
            "charged_point_add_ratio_including_advice": full_batch["charged_point_add_ratio_including_advice"],
        },
        "negative_batch": {
            "full_target_count": negative_full_batch["target_count"],
            "all_exact": negative_full_batch["all_exact"],
            "all_direct_reference_exact": negative_full_batch["all_direct_reference_exact"],
        },
        "checks": {
            "public_construction_matches": public_digest == family["frozen_public_construction_digest"],
            "compiler_matches": compiler["summary"]["digest"] == family["compiler"]["digest"] and compiler["summary"]["d3_entries"] == family["compiler"]["d3_entries"] and compiler["summary"]["d4_entries"] == family["compiler"]["d4_entries"],
            "relation_transcript_matches": relation["summary"]["target_transcript_digest"] == relation_expected["target_transcript_digest"],
            "relation_equations_match": digest(relation["summary"]["independent_equations"]) == digest(relation_expected["independent_equations"]),
            "relation_solution_matches": relation["summary"]["attack_solution"] == relation_expected["attack_solution"],
            "relation_rank_matches": relation["summary"]["quotient_rank"] == relation_expected["quotient_rank"],
            "descent_transcript_matches": descent["transcript_digest"] == descent_expected["transcript_digest"],
            "descent_verified": descent["all_supported_verified"] and descent["verified_targets"] == descent["supported_targets"],
            "candidate_full_exact": full_batch["all_exact"],
            "candidate_full_direct_reference_exact": full_batch["all_direct_reference_exact"],
            "negative_preserves_direct_arithmetic": negative_full_batch["all_direct_reference_exact"],
            "negative_reproduces_failure": not negative_full_batch["all_exact"],
        },
        "wall_seconds": time.perf_counter() - started,
        "row_digest": digest({"curve_id": curve_record["id"], "family": family["family"], "compiler": compiler["summary"]["digest"], "relation": relation["summary"]["target_transcript_digest"], "descent": descent["transcript_digest"], "downstream_ops": downstream_ops}),
    }


def run(input_path: Path, materialized_path: Path, batch_path: Path, negative_batch_path: Path, families: list[str]) -> dict[str, Any]:
    started = time.perf_counter()
    source = json.loads(input_path.read_text(encoding="utf-8"))
    materialized = json.loads(materialized_path.read_text(encoding="utf-8"))
    batch = json.loads(batch_path.read_text(encoding="utf-8"))
    negative_batch = json.loads(negative_batch_path.read_text(encoding="utf-8"))
    materialized_by_key = {(row["curve_id"], row["family"]): row for row in materialized["rows"]}
    batch_by_key = {(row["curve_id"], row["family"]): row for row in batch["rows"]}
    negative_by_key = {(row["curve_id"], row["family"]): row for row in negative_batch["rows"]}
    rows = []
    for instance in source["instances"]:
        by_family = {item["family"]: item for item in instance["families"]}
        for family_name in families:
            key = (instance["curve"]["id"], family_name)
            rows.append(reconstruct_row(instance["curve"], by_family[family_name], batch_by_key[key], negative_by_key[key]))
    normalized = [{key: value for key, value in row.items() if key != "wall_seconds"} for row in rows]
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-downstream-cost-accounting-preflight-v1",
        "claim_status": ["OBSERVATION", "TOY-EVIDENCE", "MODEL-BOUND"],
        "source": {"producer_sha256": sha256_file(SCRIPT_PATH), "typed_five_ec_sha256": sha256_file(TYPED_FIVE_SOURCE), "input_sha256": sha256_file(input_path), "materialized_sha256": sha256_file(materialized_path), "batch_sha256": sha256_file(batch_path), "negative_batch_sha256": sha256_file(negative_batch_path)},
        "config": {"families": families, "relation_seed_rule": "family.run_seed xor 0x13198A2E", "descent_seed_rule": "family.run_seed xor 0x03707344", "independent_public_support_rebuild": True, "relation_matrix_rebuilt": True, "target_coefficient_recovery_charged": True, "mixed_cost_comparison": False},
        "rows": rows,
        "summary": {
            "rows": len(rows),
            "all_public_construction_matches": all(row["checks"]["public_construction_matches"] for row in rows),
            "all_compiler_matches": all(row["checks"]["compiler_matches"] for row in rows),
            "all_relation_transcripts_match": all(row["checks"]["relation_transcript_matches"] for row in rows),
            "all_relation_equations_match": all(row["checks"]["relation_equations_match"] for row in rows),
            "all_relation_solutions_match": all(row["checks"]["relation_solution_matches"] for row in rows),
            "all_relation_ranks_match": all(row["checks"]["relation_rank_matches"] for row in rows),
            "all_descent_transcripts_match": all(row["checks"]["descent_transcript_matches"] for row in rows),
            "all_descents_verified": all(row["checks"]["descent_verified"] for row in rows),
            "all_candidate_full_exact": all(row["checks"]["candidate_full_exact"] for row in rows),
            "all_candidate_direct_reference_exact": all(row["checks"]["candidate_full_direct_reference_exact"] for row in rows),
            "all_negative_direct_arithmetic_exact": all(row["checks"]["negative_preserves_direct_arithmetic"] for row in rows),
            "all_negative_exactness_failures": all(row["checks"]["negative_reproduces_failure"] for row in rows),
            "total_relation_matrix_field_multiplications": sum(row["relation"]["matrix_ops"]["field_multiplications"] for row in rows),
            "total_relation_matrix_field_inversions": sum(row["relation"]["matrix_ops"]["field_inversions"] for row in rows),
            "total_verified_descent_targets": sum(row["descent"]["verified_targets"] for row in rows),
            "breakthrough_claim": False,
            "algorithm_promotion_gate": False,
            "boundary": "Independent public D3/D4, relation, quotient-solve, and descent ledger attached to the batched evaluator; source and downstream counters are explicitly separate and not a generic ECDLP claim.",
        },
        "result_digest": digest(normalized),
        "total_wall_seconds": time.perf_counter() - started,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("materialized", type=Path)
    parser.add_argument("batch", type=Path)
    parser.add_argument("negative_batch", type=Path)
    parser.add_argument("--families", nargs="+", required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.materialized, args.batch, args.negative_batch, args.families), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
