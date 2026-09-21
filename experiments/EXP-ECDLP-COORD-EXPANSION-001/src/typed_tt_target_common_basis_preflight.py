#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import math
import platform
import resource
import sys
import time
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
EXACT_SOURCE = SCRIPT_PATH.with_name("typed_exact_tt_factor_preflight.py")


def load_exact() -> Any:
    spec = importlib.util.spec_from_file_location("typed_exact_for_common_basis", EXACT_SOURCE)
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
    right = product(dimensions[cut:])
    left = product(dimensions[:cut])
    return [values[row * right:(row + 1) * right] for row in range(left)]


def rank_mod(rows: list[list[int]], p: int, operations: dict[str, int]) -> int:
    if not rows or not rows[0]:
        return 0
    work = [[value % p for value in row] for row in rows]
    rank = 0
    for column in range(len(work[0])):
        pivot = next((row for row in range(rank, len(work)) if work[row][column]), None)
        if pivot is None:
            continue
        if pivot != rank:
            work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][column], -1, p)
        operations["field_inversions"] += 1
        for position in range(column, len(work[rank])):
            work[rank][position] = work[rank][position] * inverse % p
            operations["field_multiplications"] += 1
        for row in range(rank + 1, len(work)):
            factor = work[row][column]
            if not factor:
                continue
            for position in range(column, len(work[row])):
                work[row][position] = (work[row][position] - factor * work[rank][position]) % p
                operations["field_multiplications"] += 1
                operations["field_subtractions"] += 1
        rank += 1
        if rank == len(work):
            break
    return rank


def target_records(family: dict[str, Any]) -> list[tuple[str, list[int]]]:
    relation = family["relations"]["target_transcript"]
    held_out = family["held_out_descent"]["transcript"]
    candidates = [("relation_first", relation[0]["target"]), ("held_out_first", held_out[0]["target"])]
    result = []
    seen = set()
    for label, value in candidates:
        key = tuple(value) if value is not None else None
        if key in seen:
            continue
        seen.add(key)
        result.append((label, value))
    return result


def family_for_target(family: dict[str, Any], target: list[int]) -> dict[str, Any]:
    result = copy.deepcopy(family)
    result["relations"]["target_transcript"] = [{"target": target}]
    return result


def synthetic_controls(p: int) -> dict[str, Any]:
    duplicate = [[1, 2, 3], [2, 4, 6]]
    independent = [[1, 0, 1], [0, 1, 1]]
    operations = {"field_inversions": 0, "field_multiplications": 0, "field_subtractions": 0}
    duplicate_rank = rank_mod(duplicate, p, operations)
    independent_rank = rank_mod(independent, p, operations)
    return {"duplicate_rank": duplicate_rank, "independent_rank": independent_rank, "pass": duplicate_rank == 1 and independent_rank == 2}


def run_row(curve: dict[str, Any], family: dict[str, Any]) -> dict[str, Any]:
    started = time.perf_counter()
    targets = target_records(family)
    target_values = []
    dimensions = None
    producer_ops = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
    tensors = []
    for label, target in targets:
        target_family = family_for_target(family, target)
        values, current_dimensions, ops, _ = EXACT.build_tensor(curve, target_family)
        dimensions = current_dimensions
        tensors.append(values)
        target_values.append({"label": label, "target": target, "entries": len(values), "digest": digest(values)})
        for key, value in ops.items():
            producer_ops[key] += value
    if dimensions is None:
        raise ValueError("no target tensors")
    rank_operations = {"field_inversions": 0, "field_multiplications": 0, "field_subtractions": 0}
    cuts = []
    for cut in (2, 3):
        matrices = [unfold(values, dimensions, cut) for values in tensors]
        stacked_rows = [row for matrix in matrices for row in matrix]
        row_union = rank_mod(stacked_rows, curve["p"], rank_operations)
        row_count = len(matrices[0])
        column_count = len(matrices[0][0])
        horizontal = [
            [matrices[target_index][row][column] for target_index in range(len(matrices)) for column in range(column_count)]
            for row in range(row_count)
        ]
        column_union = rank_mod(horizontal, curve["p"], rank_operations)
        single_rank = rank_mod(matrices[0], curve["p"], rank_operations)
        cuts.append({
            "cut": cut,
            "single_rank": single_rank,
            "row_union_rank": row_union,
            "column_union_rank": column_union,
            "row_ambient": min(len(stacked_rows), column_count),
            "column_ambient": min(row_count, len(horizontal[0])),
            "target_count": len(tensors),
            "row_union_fraction": row_union / max(1, min(len(stacked_rows), column_count)),
            "column_union_fraction": column_union / max(1, min(row_count, len(horizontal[0]))),
        })
    return {
        "curve_id": curve["id"],
        "family": family["family"],
        "dimensions": dimensions,
        "target_count": len(tensors),
        "targets": target_values,
        "cuts": cuts,
        "tensor_entries_total": sum(item["entries"] for item in target_values),
        "producer_ops": producer_ops,
        "rank_operations": rank_operations,
        "synthetic_controls": synthetic_controls(curve["p"]),
        "wall_seconds": time.perf_counter() - started,
        "row_digest": digest({"targets": target_values, "cuts": cuts}),
        "enumerative_diagnostic": True,
    }


def run(input_path: Path, families: list[str]) -> dict[str, Any]:
    started = time.perf_counter()
    source = json.loads(input_path.read_text(encoding="utf-8"))
    rows = []
    for instance in source["instances"]:
        by_family = {item["family"]: item for item in instance["families"]}
        for family_name in families:
            rows.append(run_row(instance["curve"], by_family[family_name]))
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-target-common-basis-preflight-v1",
        "claim_status": ["OBSERVATION", "TOY-EVIDENCE", "MODEL-BOUND"],
        "source": {"producer_sha256": sha256_file(SCRIPT_PATH), "exact_tensor_source_sha256": sha256_file(EXACT_SOURCE), "input_sha256": sha256_file(input_path)},
        "config": {"families": families, "targets": "relation first plus held-out first, deduplicated", "cuts": [2, 3], "source_tuple_enumeration": True},
        "controls": synthetic_controls(101),
        "rows": rows,
        "summary": {
            "rows": len(rows),
            "all_enumerative": all(row["enumerative_diagnostic"] for row in rows),
            "all_controls_pass": all(row["synthetic_controls"]["pass"] for row in rows),
            "max_target_count": max(row["target_count"] for row in rows),
            "max_row_union_fraction": max(cut["row_union_fraction"] for row in rows for cut in row["cuts"]),
            "max_column_union_fraction": max(cut["column_union_fraction"] for row in rows for cut in row["cuts"]),
            "algorithm_promotion_gate": False,
            "breakthrough_claim": False,
            "boundary": "Enumerative target-stacked TT rank census only; no target-specialized compiler, relation attack, or generic ECDLP claim.",
        },
        "peak_rss_bytes": rss_bytes(),
        "total_wall_seconds": time.perf_counter() - started,
        "result_digest": digest([{key: value for key, value in row.items() if key != "wall_seconds"} for row in rows]),
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
