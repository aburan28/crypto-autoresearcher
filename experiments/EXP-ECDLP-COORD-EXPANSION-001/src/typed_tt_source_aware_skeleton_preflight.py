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
ORACLE_SOURCE = SCRIPT_PATH.with_name("typed_tt_cross_preflight.py")


def load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


EXACT = load("typed_exact_for_source_aware", EXACT_SOURCE)
ORACLE_MODULE = load("typed_oracle_for_source_aware", ORACLE_SOURCE)


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


def unrank(value: int, dimensions: list[int]) -> tuple[int, ...]:
    result = [0] * len(dimensions)
    for index in range(len(dimensions) - 1, -1, -1):
        result[index] = value % dimensions[index]
        value //= dimensions[index]
    return tuple(result)


def prefix_order(a_size: int, b_size: int) -> list[tuple[int, int, int]]:
    result = []
    seen = set()
    for a_index in range(a_size):
        for diagonal in range(b_size):
            prefix = (a_index, diagonal, diagonal)
            result.append(prefix)
            seen.add(prefix)
    for value in range(a_size * b_size * b_size):
        prefix = unrank(value, [a_size, b_size, b_size])
        if prefix not in seen:
            result.append(prefix)
            seen.add(prefix)
    return result


def suffix_indices(b_size: int) -> list[tuple[int, int]]:
    return [unrank(value, [b_size, b_size]) for value in range(b_size * b_size)]


def row_reduce_add(row: list[int], basis: dict[int, list[int]], p: int, counters: dict[str, int]) -> bool:
    work = [value % p for value in row]
    for pivot in sorted(basis):
        factor = work[pivot]
        if not factor:
            continue
        prior = basis[pivot]
        for index in range(pivot, len(work)):
            work[index] = (work[index] - factor * prior[index]) % p
            counters["field_multiplications"] += 1
            counters["field_subtractions"] += 1
    pivot = next((index for index, value in enumerate(work) if value), None)
    if pivot is None:
        return False
    inverse = pow(work[pivot], -1, p)
    counters["field_inversions"] += 1
    for index in range(pivot, len(work)):
        work[index] = work[index] * inverse % p
        counters["field_multiplications"] += 1
    basis[pivot] = work
    return True


def row_pivots(matrix: list[list[int]], p: int, counters: dict[str, int]) -> tuple[list[int], int]:
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
    return row_pivots([list(column) for column in zip(*matrix)], p, counters)


def inverse_matrix(matrix: list[list[int]], p: int, counters: dict[str, int]) -> list[list[int]]:
    size = len(matrix)
    work = [[value % p for value in row] + [int(i == j) for j in range(size)] for i, row in enumerate(matrix)]
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        if pivot is None:
            raise ValueError("singular skeleton cross")
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


def target_list(family: dict[str, Any]) -> list[tuple[str, list[int]]]:
    relation = [(f"relation_{index}", item["target"]) for index, item in enumerate(family["relations"]["target_transcript"][:8])]
    held = ("held_out_first", family["held_out_descent"]["transcript"][0]["target"])
    return relation + [held]


def build_skeleton(oracle: Any, a_size: int, b_size: int, rank_target: int, counters: dict[str, int]) -> dict[str, Any]:
    suffixes = suffix_indices(b_size)
    basis_rows = []
    basis_prefixes = []
    echelon: dict[int, list[int]] = {}
    examined = 0
    for prefix in prefix_order(a_size, b_size):
        examined += 1
        row = [oracle.value(prefix + suffix) for suffix in suffixes]
        if row_reduce_add(row, echelon, oracle.p, counters):
            basis_rows.append(row)
            basis_prefixes.append(prefix)
            if len(basis_rows) == rank_target:
                break
    if len(basis_rows) != rank_target:
        raise ValueError("source-aware prefix order did not reach target rank")
    pivot_columns, column_rank = column_pivots(basis_rows, oracle.p, counters)
    if column_rank != rank_target:
        raise ValueError("basis column rank mismatch")
    cross = [[basis_rows[row][column] for column in pivot_columns] for row in range(rank_target)]
    inverse = inverse_matrix(cross, oracle.p, counters)
    return {"rank": rank_target, "basis_rows": basis_rows, "basis_prefixes": basis_prefixes, "pivot_columns": pivot_columns, "inverse": inverse, "candidate_prefixes_examined": examined}


def reconstruct_target(oracle: Any, skeleton: dict[str, Any], a_size: int, b_size: int, validate_full: bool) -> dict[str, Any]:
    prefixes = prefix_order(a_size, b_size)
    suffixes = suffix_indices(b_size)
    rank = skeleton["rank"]
    columns = skeleton["pivot_columns"]
    inverse = skeleton["inverse"]
    basis = skeleton["basis_rows"]
    mismatches = 0
    validation_queries = 0
    specialization_queries = 0
    for prefix in prefixes:
        sampled = [oracle.value(prefix + suffixes[column]) for column in columns]
        specialization_queries += len(columns)
        coefficients = row_times_matrix(sampled, inverse, oracle.p)
        if validate_full:
            for column, suffix in enumerate(suffixes):
                actual = oracle.value(prefix + suffix)
                predicted = sum(coefficients[index] * basis[index][column] for index in range(rank)) % oracle.p
                mismatches += int(actual != predicted)
                validation_queries += 1
    return {"mismatches": mismatches, "specialization_queries": specialization_queries, "validation_queries": validation_queries}


def run_row(curve: dict[str, Any], family: dict[str, Any], rank_row: dict[str, Any]) -> dict[str, Any]:
    started = time.perf_counter()
    a_size = len(family["progression"]["points"])
    b_size = len(family["factor_base"]["points"])
    dimensions = [a_size, b_size, b_size, b_size, b_size]
    full_entries = product(dimensions)
    rank_target = rank_row["exact_tt_ranks"][3]
    base_target = family["relations"]["target_transcript"][0]["target"]
    base_oracle = ORACLE_MODULE.Oracle(curve, target_family(family, base_target))
    construction_ops = {"field_inversions": 0, "field_multiplications": 0, "field_subtractions": 0}
    skeleton = build_skeleton(base_oracle, a_size, b_size, rank_target, construction_ops)
    target_results = []
    for label, target in target_list(family):
        oracle = ORACLE_MODULE.Oracle(curve, target_family(family, target))
        result = reconstruct_target(oracle, skeleton, a_size, b_size, True)
        target_results.append({
            "label": label,
            "target": target,
            "mismatches": result["mismatches"],
            "specialization_queries": result["specialization_queries"],
            "validation_queries": result["validation_queries"],
            "oracle_ops": oracle.ops,
        })
    construction_queries = skeleton["candidate_prefixes_examined"] * (b_size * b_size)
    specialization_queries = a_size * b_size * b_size * rank_target
    return {
        "curve_id": curve["id"],
        "family": family["family"],
        "dimensions": dimensions,
        "rank_target": rank_target,
        "skeleton_rank": skeleton["rank"],
        "candidate_prefixes_examined": skeleton["candidate_prefixes_examined"],
        "total_prefixes": a_size * b_size * b_size,
        "basis_prefixes": skeleton["basis_prefixes"],
        "pivot_columns": skeleton["pivot_columns"],
        "basis_entries": rank_target * (b_size * b_size),
        "full_tensor_entries": full_entries,
        "construction_queries": construction_queries,
        "construction_oracle_ops": base_oracle.ops,
        "construction_query_count_matches": base_oracle.ops["unique_queries"] == construction_queries,
        "construction_query_ratio_full_tensor": construction_queries / max(1, full_entries),
        "specialization_queries_per_target": specialization_queries,
        "specialization_query_ratio_full_tensor": specialization_queries / max(1, full_entries),
        "targets": target_results,
        "all_exact": all(item["mismatches"] == 0 for item in target_results),
        "construction_ops": construction_ops,
        "source_construction_non_enumerative": True,
        "enumerative_validation": True,
        "wall_seconds": time.perf_counter() - started,
        "row_digest": digest({"curve_id": curve["id"], "family": family["family"], "rank": rank_target, "candidate_prefixes_examined": skeleton["candidate_prefixes_examined"], "basis_prefixes": skeleton["basis_prefixes"], "pivot_columns": skeleton["pivot_columns"], "targets": [{key: value for key, value in item.items() if key != "oracle_ops"} for item in target_results]}),
    }


def run(input_path: Path, rank_path: Path, families: list[str]) -> dict[str, Any]:
    started = time.perf_counter()
    source = json.loads(input_path.read_text(encoding="utf-8"))
    rank_source = json.loads(rank_path.read_text(encoding="utf-8"))
    rank_by_key = {(row["curve_id"], row["family"]): row for row in rank_source["rows"]}
    rows = []
    for instance in source["instances"]:
        by_family = {item["family"]: item for item in instance["families"]}
        for family_name in families:
            key = (instance["curve"]["id"], family_name)
            rows.append(run_row(instance["curve"], by_family[family_name], rank_by_key[key]))
    normalized_rows = [{key: value for key, value in row.items() if key != "wall_seconds"} for row in rows]
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-source-aware-skeleton-preflight-v1",
        "claim_status": ["OBSERVATION", "TOY-EVIDENCE", "MODEL-BOUND"],
        "source": {"producer_sha256": sha256_file(SCRIPT_PATH), "exact_tensor_source_sha256": sha256_file(EXACT_SOURCE), "oracle_source_sha256": sha256_file(ORACLE_SOURCE), "input_sha256": sha256_file(input_path), "rank_oracle_sha256": sha256_file(rank_path)},
        "config": {"families": families, "cut": 3, "rank_budget": "sealed exact TT oracle", "targets": "first eight relation plus held-out first", "source_tuple_enumeration": False, "validation_full_tensor": True},
        "rows": rows,
        "summary": {
            "rows": len(rows),
            "all_source_paths_non_enumerative": all(row["source_construction_non_enumerative"] for row in rows),
            "all_exact_validation": all(row["all_exact"] for row in rows),
            "all_construction_query_counts_match": all(row["construction_query_count_matches"] for row in rows),
            "min_construction_query_ratio": min(row["construction_query_ratio_full_tensor"] for row in rows),
            "max_construction_query_ratio": max(row["construction_query_ratio_full_tensor"] for row in rows),
            "min_specialization_query_ratio": min(row["specialization_query_ratio_full_tensor"] for row in rows),
            "max_specialization_query_ratio": max(row["specialization_query_ratio_full_tensor"] for row in rows),
            "algorithm_promotion_gate": False,
            "breakthrough_claim": False,
            "boundary": "Source-aware prefix-fiber skeleton construction with separately charged full validation; no generic ECDLP claim.",
        },
        "peak_rss_bytes": rss_bytes(),
        "total_wall_seconds": time.perf_counter() - started,
        "result_digest": digest(normalized_rows),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("rank_oracle", type=Path)
    parser.add_argument("--families", nargs="+", required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.rank_oracle, args.families), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
