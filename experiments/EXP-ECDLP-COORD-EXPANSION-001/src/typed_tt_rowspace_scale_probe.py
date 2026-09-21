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
ROWSPACE_SOURCE = SCRIPT_PATH.with_name("typed_tt_rowspace_witness_locator.py")


def load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ROWSPACE = load("typed_tt_rowspace_for_scale_probe", ROWSPACE_SOURCE)
ADAPTIVE = ROWSPACE.ADAPTIVE
STREAMING = ROWSPACE.STREAMING
TF = ROWSPACE.TF
ORACLE = ROWSPACE.ORACLE
SourceOracle = ROWSPACE.SourceOracle


def digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sample_columns(b_size: int, limit: int, seed: int) -> list[int]:
    count = b_size * b_size
    if limit >= count:
        return list(range(count))
    ranked = sorted(
        range(count),
        key=lambda index: hashlib.sha256(f"ROWSPACE-SCALE|{seed}|{index}".encode("ascii")).digest(),
    )
    return sorted(ranked[:limit])


def sample_reconstruction(
    oracle: Any,
    skeleton: dict[str, Any],
    a_size: int,
    b_size: int,
    columns: list[int],
) -> dict[str, Any]:
    prefixes = ADAPTIVE.SOURCE_AWARE.prefix_order(a_size, b_size)
    suffixes = ADAPTIVE.SOURCE_AWARE.suffix_indices(b_size)
    rank = skeleton["rank"]
    pivot_columns = skeleton["pivot_columns"]
    inverse = skeleton["inverse"]
    basis = skeleton["basis_rows"]
    sampled_entries = 0
    mismatches = 0
    field_multiplications = 0
    field_additions = 0
    for prefix in prefixes:
        sampled = [oracle.value(prefix + suffixes[column]) for column in pivot_columns]
        coefficients = ADAPTIVE.SOURCE_AWARE.row_times_matrix(sampled, inverse, oracle.p)
        field_multiplications += rank * rank
        field_additions += rank * max(0, rank - 1)
        for column in columns:
            predicted = sum(coefficients[index] * basis[index][column] for index in range(rank)) % oracle.p
            actual = oracle.value(prefix + suffixes[column])
            mismatches += int(predicted != actual)
            sampled_entries += 1
            field_multiplications += rank
            field_additions += max(0, rank - 1)
    return {
        "sampled_entries": sampled_entries,
        "mismatches": mismatches,
        "field_multiplications": field_multiplications,
        "field_additions": field_additions,
    }


def bounded_adaptive_build(oracle: Any, a_size: int, b_size: int, max_prefixes: int) -> dict[str, Any]:
    suffix_list = ADAPTIVE.SOURCE_AWARE.suffix_indices(b_size)
    window = max(4, b_size // 2)
    basis_rows = []
    basis_prefixes = []
    echelon: dict[int, list[int]] = {}
    counters = {"field_inversions": 0, "field_multiplications": 0, "field_subtractions": 0}
    examined = 0
    plateau = 0
    rank = 0
    for prefix in ADAPTIVE.SOURCE_AWARE.prefix_order(a_size, b_size):
        if examined == max_prefixes:
            break
        examined += 1
        row = [oracle.value(prefix + suffix) for suffix in suffix_list]
        if ADAPTIVE.SOURCE_AWARE.row_reduce_add(row, echelon, oracle.p, counters):
            basis_rows.append(row)
            basis_prefixes.append(prefix)
            rank += 1
            plateau = 0
        else:
            plateau += 1
        if rank > 0 and plateau >= window:
            break
    if not basis_rows:
        raise ValueError("bounded scale probe found no nonzero row")
    pivot_columns, column_rank = ADAPTIVE.SOURCE_AWARE.column_pivots(basis_rows, oracle.p, counters)
    if column_rank != rank:
        raise ValueError("bounded scale probe column rank mismatch")
    cross = [[basis_rows[row][column] for column in pivot_columns] for row in range(rank)]
    inverse = ADAPTIVE.SOURCE_AWARE.inverse_matrix(cross, oracle.p, counters)
    return {
        "rank": rank,
        "basis_rows": basis_rows,
        "basis_prefixes": basis_prefixes,
        "pivot_columns": pivot_columns,
        "inverse": inverse,
        "candidate_prefixes_examined": examined,
        "total_prefixes": a_size * b_size * b_size,
        "stability_window": window,
        "terminal_plateau": plateau,
        "stopping_reason": "dependent_prefix_plateau" if plateau >= window else "prefix_budget",
        "rank_counters": counters,
    }


def run_row(curve_record: dict[str, Any], family: dict[str, Any], sample_limit: int, target_budget_factor: int, max_prefixes: int) -> dict[str, Any]:
    started = time.perf_counter()
    p = curve_record["p"]
    q = curve_record["q"]
    curve_typed = TF.Curve(p, curve_record["a"], curve_record["b"])
    generator = TF.point_from_json(curve_record["generator"])
    a_size = len(family["progression"]["points"])
    b_size = len(family["factor_base"]["points"])
    full_entries_per_target = a_size * b_size**4
    advice = STREAMING.StreamingSourceAdvice(curve_record, family)
    source_ops = ROWSPACE.zero_ops()
    rank_ops = ROWSPACE.zero_ops()
    reconstruction_ops = ROWSPACE.zero_ops()
    target_ops = TF.Ops()
    sample_columns_list = sample_columns(b_size, sample_limit, family["run_seed"] ^ 0xA5A5A5A5)
    skeleton = None
    target_budget = min(q - 1, target_budget_factor * (b_size + 1))
    transcripts = []
    relation_seed = family["run_seed"] ^ 0x13198A2E
    for target_index, scalar in enumerate(TF.nonzero_scalar_stream(q, relation_seed)):
        if target_index == target_budget:
            break
        target = curve_typed.mul(scalar, generator, target_ops)
        target_json = TF.point_json(target)
        target_oracle = ORACLE.point(target_json)
        if skeleton is None:
            build_oracle = SourceOracle(advice, target_oracle)
            skeleton = bounded_adaptive_build(build_oracle, a_size, b_size, max_prefixes)
            ROWSPACE.add_ops(source_ops, build_oracle.ops)
            ROWSPACE.add_ops(rank_ops, skeleton["rank_counters"])
        oracle = SourceOracle(advice, target_oracle)
        sampled = sample_reconstruction(oracle, skeleton, a_size, b_size, sample_columns_list)
        ROWSPACE.add_ops(source_ops, oracle.ops)
        ROWSPACE.add_ops(reconstruction_ops, sampled)
        transcripts.append({
            "scalar": scalar,
            "target": target_json,
            "rowspace_rank": skeleton["rank"],
            "prefixes_examined": skeleton["candidate_prefixes_examined"],
            "sample_columns": len(sample_columns_list),
            "sampled_entries": sampled["sampled_entries"],
            "mismatches": sampled["mismatches"],
            "source_unique_queries": oracle.ops["unique_queries"],
        })
    return {
        "curve_id": curve_record["id"],
        "family": family["family"],
        "mode": "reuse_scale_probe",
        "dimensions": [a_size, b_size, b_size, b_size, b_size],
        "target_budget": target_budget,
        "targets_attempted": len(transcripts),
        "rowspace_rank": skeleton["rank"],
        "rowspace_stopping_reason": skeleton["stopping_reason"],
        "rowspace_prefixes_examined": skeleton["candidate_prefixes_examined"],
        "rowspace_rank_set": sorted({item["rowspace_rank"] for item in transcripts}),
        "sample_columns": len(sample_columns_list),
        "sample_column_fraction": len(sample_columns_list) / max(1, b_size * b_size),
        "sampled_entries_fraction": sum(item["sampled_entries"] for item in transcripts) / max(1, len(transcripts) * full_entries_per_target),
        "all_sample_matches": all(item["mismatches"] == 0 for item in transcripts),
        "total_sample_mismatches": sum(item["mismatches"] for item in transcripts),
        "candidate_source_ops": source_ops,
        "candidate_rank_ops": rank_ops,
        "candidate_reconstruction_ops": reconstruction_ops,
        "candidate_target_build_ops": TF.asdict(target_ops),
        "candidate_advice": {"retained_bytes": advice.retained_bytes(), "logical_payload_bytes": advice.logical_payload_bytes, "suffix_entries": len(advice.suffix)},
        "transcripts": transcripts,
        "full_tensor_entries": len(transcripts) * full_entries_per_target,
        "row_digest": digest({"curve_id": curve_record["id"], "family": family["family"], "transcripts": transcripts}),
        "wall_seconds": time.perf_counter() - started,
    }


def run(input_path: Path, families: list[str], sample_limit: int, target_budget_factor: int, max_prefixes: int) -> dict[str, Any]:
    started = time.perf_counter()
    source = json.loads(input_path.read_text(encoding="utf-8"))
    rows = []
    for instance in source["instances"]:
        by_family = {item["family"]: item for item in instance["families"]}
        for family_name in families:
            rows.append(run_row(instance["curve"], by_family[family_name], sample_limit, target_budget_factor, max_prefixes))
    normalized = [{key: value for key, value in row.items() if key != "wall_seconds"} for row in rows]
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-rowspace-scale-probe-v1",
        "claim_status": ["OBSERVATION", "TOY-EVIDENCE", "MODEL-BOUND"],
        "source": {"producer_sha256": sha256_file(SCRIPT_PATH), "rowspace_sha256": sha256_file(ROWSPACE_SOURCE), "input_sha256": sha256_file(input_path)},
        "config": {"families": families, "sample_limit": sample_limit, "target_budget_factor": target_budget_factor, "max_prefixes": max_prefixes, "mode": "reuse_scale_probe", "source_tuple_enumeration": False, "suffix_reconstruction_enumeration": False, "validation": "sampled direct source values only"},
        "rows": rows,
        "summary": {
            "rows": len(rows),
            "all_sample_matches": all(row["all_sample_matches"] for row in rows),
            "max_sample_mismatches": max(row["total_sample_mismatches"] for row in rows),
            "rowspace_ranks": sorted({rank for row in rows for rank in row["rowspace_rank_set"]}),
            "all_prefix_bounded": all(row["rowspace_stopping_reason"] == "prefix_budget" for row in rows),
            "max_sampled_entries_fraction": max(row["sampled_entries_fraction"] for row in rows),
            "breakthrough_claim": False,
            "algorithm_promotion_gate": False,
            "boundary": "Larger-dimension sampled validation of reused TT row spaces; no full support, relation, descent, or ECDLP claim.",
        },
        "result_digest": digest(normalized),
        "total_wall_seconds": time.perf_counter() - started,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--families", nargs="+", required=True)
    parser.add_argument("--sample-limit", type=int, default=64)
    parser.add_argument("--target-budget-factor", type=int, default=1)
    parser.add_argument("--max-prefixes", type=int, default=128)
    args = parser.parse_args()
    if args.sample_limit < 1 or args.target_budget_factor < 1 or args.max_prefixes < 1:
        raise SystemExit("sample-limit, target-budget-factor, and max-prefixes must be positive")
    print(json.dumps(run(args.input, args.families, args.sample_limit, args.target_budget_factor, args.max_prefixes), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
