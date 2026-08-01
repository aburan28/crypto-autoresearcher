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
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
EXACT_SOURCE = SCRIPT_PATH.with_name("typed_exact_tt_factor_preflight.py")


def load_exact() -> Any:
    spec = importlib.util.spec_from_file_location("typed_exact_for_shared_prefix", EXACT_SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load exact tensor source")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


EXACT = load_exact()


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if platform.system() == "Darwin" else value * 1024)


def product(values: list[int]) -> int:
    result = 1
    for value in values:
        result *= value
    return result


def unfold(values: list[int], dimensions: list[int], cut: int) -> list[list[int]]:
    width = product(dimensions[cut:])
    height = product(dimensions[:cut])
    return [values[row * width:(row + 1) * width] for row in range(height)]


def row_pivots(matrix: list[list[int]], p: int, counters: dict[str, int]) -> tuple[list[int], int]:
    if not matrix or not matrix[0]:
        return [], 0
    work = [[value % p for value in row] for row in matrix]
    identifiers = list(range(len(work)))
    pivots = []
    rank = 0
    for column in range(len(work[0])):
        pivot = next((row for row in range(rank, len(work)) if work[row][column]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        identifiers[rank], identifiers[pivot] = identifiers[pivot], identifiers[rank]
        inverse = pow(work[rank][column], -1, p)
        counters["field_inversions"] += 1
        for position in range(column, len(work[rank])):
            work[rank][position] = work[rank][position] * inverse % p
            counters["field_multiplications"] += 1
        for row in range(rank + 1, len(work)):
            factor = work[row][column]
            if not factor:
                continue
            for position in range(column, len(work[row])):
                work[row][position] = (work[row][position] - factor * work[rank][position]) % p
                counters["field_multiplications"] += 1
                counters["field_subtractions"] += 1
        pivots.append(identifiers[rank])
        rank += 1
        if rank == len(work):
            break
    return pivots, rank


def column_pivots(matrix: list[list[int]], p: int, counters: dict[str, int]) -> tuple[list[int], int]:
    if not matrix or not matrix[0]:
        return [], 0
    transposed = [list(column) for column in zip(*matrix)]
    return row_pivots(transposed, p, counters)


def inverse_matrix(matrix: list[list[int]], p: int, counters: dict[str, int]) -> list[list[int]]:
    size = len(matrix)
    work = [[value % p for value in row] + [int(i == j) for j in range(size)] for i, row in enumerate(matrix)]
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        if pivot is None:
            raise ValueError("singular skeleton pivot block")
        work[column], work[pivot] = work[pivot], work[column]
        inverse = pow(work[column][column], -1, p)
        counters["field_inversions"] += 1
        work[column] = [(value * inverse) % p for value in work[column]]
        counters["field_multiplications"] += 2 * size
        for row in range(size):
            if row == column or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [(left - factor * right) % p for left, right in zip(work[row], work[column])]
            counters["field_multiplications"] += 2 * size
            counters["field_subtractions"] += 2 * size
    return [row[size:] for row in work]


def row_times_matrix(row: list[int], matrix: list[list[int]], p: int) -> list[int]:
    return [sum(row[index] * matrix[index][column] for index in range(len(row))) % p for column in range(len(matrix[0]))]


def target_family(family: dict[str, Any], target: list[int]) -> dict[str, Any]:
    import copy
    result = copy.deepcopy(family)
    result["relations"]["target_transcript"] = [{"target": target}]
    return result


def targets_for(family: dict[str, Any], limit: int = 8) -> tuple[list[tuple[str, list[int]]], tuple[str, list[int]]]:
    relation = [(f"relation_{index}", item["target"]) for index, item in enumerate(family["relations"]["target_transcript"][:limit])]
    held_out = ("held_out_first", family["held_out_descent"]["transcript"][0]["target"])
    return relation, held_out


def build_skeleton(base_matrix: list[list[int]], p: int, counters: dict[str, int]) -> dict[str, Any]:
    basis_rows, rank = row_pivots(base_matrix, p, counters)
    if rank == 0:
        raise ValueError("zero base matrix")
    basis = [base_matrix[row] for row in basis_rows]
    basis_columns, column_rank = column_pivots(basis, p, counters)
    if column_rank != rank:
        raise ValueError("basis column rank mismatch")
    cross = [[basis[row][column] for column in basis_columns] for row in range(rank)]
    inverse = inverse_matrix(cross, p, counters)
    return {"basis_rows": basis_rows, "basis_columns": basis_columns, "basis": basis, "inverse": inverse, "rank": rank}


def reconstruct(matrix: list[list[int]], skeleton: dict[str, Any], p: int) -> tuple[int, list[list[int]]]:
    basis = skeleton["basis"]
    basis_columns = skeleton["basis_columns"]
    inverse = skeleton["inverse"]
    mismatches = 0
    coefficients = []
    for row in matrix:
        sampled = [row[column] for column in basis_columns]
        coefficient = row_times_matrix(sampled, inverse, p)
        coefficients.append(coefficient)
        predicted = [sum(coefficient[index] * basis[index][column] for index in range(len(coefficient))) % p for column in range(len(basis[0]))]
        mismatches += int(predicted != [value % p for value in row])
    return mismatches, coefficients


def synthetic_controls(p: int) -> dict[str, Any]:
    counters = {"field_inversions": 0, "field_multiplications": 0, "field_subtractions": 0}
    base = [[1, 2, 3], [2, 4, 6]]
    independent = [[1, 2, 3], [2, 4, 6], [0, 1, 1]]
    skeleton = build_skeleton(base, p, counters)
    pass_duplicate = reconstruct(base, skeleton, p)[0] == 0
    rejected_extra = reconstruct(independent, skeleton, p)[0] > 0
    return {"duplicate_pass": pass_duplicate, "independent_rejected": rejected_extra, "pass": pass_duplicate and rejected_extra}


def run_row(curve: dict[str, Any], family: dict[str, Any]) -> dict[str, Any]:
    started = time.perf_counter()
    relation_targets, held_out = targets_for(family)
    selected = relation_targets
    tensors = []
    target_metadata = []
    dimensions = None
    build_ops = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
    for label, target in selected + [held_out]:
        values, current_dimensions, ops, _ = EXACT.build_tensor(curve, target_family(family, target))
        tensors.append(values)
        dimensions = current_dimensions
        target_metadata.append({"label": label, "target": target, "entries": len(values), "digest": digest(values)})
        for key, value in ops.items():
            build_ops[key] += value
    if dimensions is None:
        raise ValueError("no tensors")
    matrix_list = [unfold(values, dimensions, 3) for values in tensors]
    base_matrix = matrix_list[0]
    counters = {"field_inversions": 0, "field_multiplications": 0, "field_subtractions": 0}
    skeleton = build_skeleton(base_matrix, curve["p"], counters)
    rank = skeleton["rank"]
    full_entries = len(base_matrix) * len(base_matrix[0])
    batch_rows = []
    for batch_size in (1, 2, 4, 8):
        mismatches = []
        for index in range(batch_size):
            mismatch, _ = reconstruct(matrix_list[index], skeleton, curve["p"])
            mismatches.append(mismatch)
        batch_rows.append({
            "batch_size": batch_size,
            "mismatches": mismatches,
            "all_exact": all(value == 0 for value in mismatches),
            "specialization_entries_per_target": len(base_matrix) * rank,
            "full_target_entries": full_entries,
            "specialization_ratio": (len(base_matrix) * rank) / max(1, full_entries),
            "batch_specialization_entries": batch_size * len(base_matrix) * rank,
        })
    held_out_mismatch, _ = reconstruct(matrix_list[-1], skeleton, curve["p"])
    return {
        "curve_id": curve["id"],
        "family": family["family"],
        "dimensions": dimensions,
        "cut": 3,
        "target_count": len(selected),
        "targets": target_metadata,
        "skeleton_rank": rank,
        "basis_rows": skeleton["basis_rows"],
        "basis_columns": skeleton["basis_columns"],
        "basis_entries": rank * len(base_matrix[0]),
        "base_discovery_entries": full_entries,
        "full_target_entries": full_entries,
        "batch_results": batch_rows,
        "held_out_mismatches": held_out_mismatch,
        "all_batches_exact": all(row["all_exact"] for row in batch_rows),
        "held_out_exact": held_out_mismatch == 0,
        "build_ops": build_ops,
        "skeleton_ops": counters,
        "synthetic_controls": synthetic_controls(curve["p"]),
        "enumerative_diagnostic": True,
        "wall_seconds": time.perf_counter() - started,
        "row_digest": digest({"targets": target_metadata, "rank": rank, "basis_rows": skeleton["basis_rows"], "basis_columns": skeleton["basis_columns"], "batch_results": batch_rows, "held_out_mismatches": held_out_mismatch}),
    }


def run(input_path: Path, families: list[str]) -> dict[str, Any]:
    started = time.perf_counter()
    source = json.loads(input_path.read_text(encoding="utf-8"))
    rows = []
    for instance in source["instances"]:
        by_family = {item["family"]: item for item in instance["families"]}
        for family_name in families:
            rows.append(run_row(instance["curve"], by_family[family_name]))
    normalized_rows = [{key: value for key, value in row.items() if key != "wall_seconds"} for row in rows]
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-shared-prefix-construction-preflight-v1",
        "claim_status": ["OBSERVATION", "TOY-EVIDENCE", "MODEL-BOUND"],
        "source": {"producer_sha256": sha256_file(SCRIPT_PATH), "exact_tensor_source_sha256": sha256_file(EXACT_SOURCE), "input_sha256": sha256_file(input_path)},
        "config": {"families": families, "cut": 3, "batches": [1, 2, 4, 8], "held_out": "first held-out descent target", "source_tuple_enumeration": True},
        "rows": rows,
        "summary": {
            "rows": len(rows),
            "all_enumerative": all(row["enumerative_diagnostic"] for row in rows),
            "all_batches_exact": all(row["all_batches_exact"] for row in rows),
            "all_held_out_exact": all(row["held_out_exact"] for row in rows),
            "all_controls_pass": all(row["synthetic_controls"]["pass"] for row in rows),
            "min_specialization_ratio": min(batch["specialization_ratio"] for row in rows for batch in row["batch_results"]),
            "max_specialization_ratio": max(batch["specialization_ratio"] for row in rows for batch in row["batch_results"]),
            "algorithm_promotion_gate": False,
            "breakthrough_claim": False,
            "boundary": "Enumerative exact shared cut-3 row skeleton only; no non-enumerative compiler, relation attack, or generic ECDLP claim.",
        },
        "peak_rss_bytes": rss_bytes(),
        "total_wall_seconds": time.perf_counter() - started,
        "result_digest": digest(normalized_rows),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--families", nargs="+", required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.families), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
