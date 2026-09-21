#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
import resource
import time
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
Point = tuple[int, int] | None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if platform.system() == "Darwin" else value * 1024)


class AffineCurve:
    def __init__(self, p: int, a: int, b: int) -> None:
        self.p = p
        self.a = a % p
        self.b = b % p

    def add(self, left: Point, right: Point, ops: dict[str, int]) -> Point:
        ops["point_add_calls"] += 1
        if left is None:
            return right
        if right is None:
            return left
        x1, y1 = left
        x2, y2 = right
        if x1 == x2 and (y1 + y2) % self.p == 0:
            return None
        if left == right:
            if y1 % self.p == 0:
                return None
            numerator = (3 * x1 * x1 + self.a) % self.p
            denominator = (2 * y1) % self.p
        else:
            numerator = (y2 - y1) % self.p
            denominator = (x2 - x1) % self.p
        slope = numerator * pow(denominator, -1, self.p) % self.p
        x3 = (slope * slope - x1 - x2) % self.p
        y3 = (slope * (x1 - x3) - y1) % self.p
        ops["field_inversions"] += 1
        ops["field_multiplications"] += 4
        return x3, y3


def point(value: list[int] | None) -> Point:
    return None if value is None else (value[0], value[1])


def point_json(value: Point) -> list[int] | None:
    return None if value is None else [value[0], value[1]]


def nonsquare(p: int) -> int:
    for value in range(2, p):
        if pow(value, (p - 1) // 2, p) == p - 1:
            return value
    raise ValueError("no nonsquare found")


def inverse_matrix(matrix: list[list[int]], p: int, counters: dict[str, int]) -> list[list[int]]:
    size = len(matrix)
    work = [
        [value % p for value in row] + [int(row_index == column) for column in range(size)]
        for row_index, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        if pivot is None:
            raise ValueError("singular factorization pivot block")
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
        inverse = pow(work[column][column], -1, p)
        counters["field_inversions"] += 1
        work[column] = [(value * inverse) % p for value in work[column]]
        counters["field_multiplications"] += 2 * size
        for row in range(size):
            if row == column or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [
                (left - factor * right) % p
                for left, right in zip(work[row], work[column])
            ]
            counters["field_multiplications"] += 2 * size
            counters["field_subtractions"] += 2 * size
    return [row[size:] for row in work]


def matrix_vector(matrix: list[list[int]], vector: list[int], p: int) -> list[int]:
    return [sum(left * right for left, right in zip(row, vector)) % p for row in matrix]


def factor_matrix(
    matrix: list[list[int]], p: int, counters: dict[str, int]
) -> tuple[list[list[int]], list[list[int]], int]:
    if not matrix or not matrix[0]:
        raise ValueError("empty matrix")
    row_count = len(matrix)
    column_count = len(matrix[0])
    work = [[value % p for value in row] for row in matrix]
    row_ids = list(range(row_count))
    pivot_columns: list[int] = []
    pivot_rows: list[int] = []
    rank = 0
    for column in range(column_count):
        pivot = next((row for row in range(rank, row_count) if work[row][column]), None)
        if pivot is None:
            continue
        if pivot != rank:
            work[rank], work[pivot] = work[pivot], work[rank]
            row_ids[rank], row_ids[pivot] = row_ids[pivot], row_ids[rank]
        inverse = pow(work[rank][column], -1, p)
        counters["field_inversions"] += 1
        for position in range(column, column_count):
            work[rank][position] = work[rank][position] * inverse % p
            counters["field_multiplications"] += 1
        for row in range(rank + 1, row_count):
            factor = work[row][column]
            if not factor:
                continue
            for position in range(column, column_count):
                work[row][position] = (work[row][position] - factor * work[rank][position]) % p
                counters["field_multiplications"] += 1
                counters["field_subtractions"] += 1
        pivot_columns.append(column)
        pivot_rows.append(row_ids[rank])
        rank += 1
        if rank == min(row_count, column_count):
            break
    if rank == 0:
        raise ValueError("zero tensor unfolding is not supported by this preflight")
    basis = [[matrix[row][column] for column in pivot_columns] for row in range(row_count)]
    pivot_block = [[matrix[row][column] for column in pivot_columns] for row in pivot_rows]
    inverse = inverse_matrix(pivot_block, p, counters)
    coefficients = []
    for column in range(column_count):
        right = [matrix[row][column] % p for row in pivot_rows]
        coefficients.append(matrix_vector(inverse, right, p))
    residual = [[coefficients[column][basis_index] for column in range(column_count)] for basis_index in range(rank)]
    for row in range(row_count):
        for column in range(column_count):
            reconstructed = sum(basis[row][index] * residual[index][column] for index in range(rank)) % p
            if reconstructed != matrix[row][column] % p:
                raise AssertionError("rank factorization reconstruction failed")
    return basis, residual, rank


def raw_shape_schedule() -> list[int]:
    def add(left: list[int], right: list[int]) -> list[int]:
        return [1, *(a + b for a, b in zip(left[1:-1], right[1:-1])), 1]

    def mul(left: list[int], right: list[int]) -> list[int]:
        return [1, *(a * b for a, b in zip(left[1:-1], right[1:-1])), 1]

    def rcb(left: tuple[list[int], list[int], list[int]], right: tuple[list[int], list[int], list[int]]) -> tuple[list[int], list[int], list[int]]:
        x1, y1, z1 = left
        x2, y2, z2 = right
        t0 = mul(x1, x2)
        t1 = mul(y1, y2)
        t2 = mul(z1, z2)
        t3 = add(mul(add(x1, y1), add(x2, y2)), t0)
        t3 = add(t3, t1)
        t4 = add(mul(add(x1, z1), add(x2, z2)), t0)
        t4 = add(t4, t2)
        t5 = add(mul(add(y1, z1), add(y2, z2)), t1)
        t5 = add(t5, t2)
        z3 = add(t4, t2)
        x3 = add(t1, z3)
        z3 = add(t1, z3)
        y3 = mul(x3, z3)
        t1 = add(add(t0, t0), t0)
        t1 = add(t1, t2)
        t2 = add(t0, t2)
        t4 = add(t4, t2)
        t0 = mul(t1, t4)
        y3 = add(y3, t0)
        t0 = mul(t5, t4)
        x3 = add(mul(t3, x3), t0)
        t0 = mul(t3, t1)
        z3 = add(mul(t5, z3), t0)
        return x3, y3, z3

    shape = [1, 1, 1, 1, 1, 1]
    source = (shape, shape, shape)
    for _ in range(4):
        source = rcb(source, (shape, shape, shape))
    x, y, z = source
    ex = add(x, z)
    ey = add(y, z)
    return add(mul(ex, ex), mul(ey, ey))


def exact_tt_factor(values: list[int], dimensions: list[int], p: int) -> dict[str, Any]:
    counters = {
        "field_inversions": 0,
        "field_multiplications": 0,
        "field_subtractions": 0,
        "factorizations": 0,
    }
    residual = list(values)
    cores: list[list[list[list[int]]]] = []
    ranks = [1]
    for mode, dimension in enumerate(dimensions[:-1]):
        left_dimension = ranks[-1] * dimension
        right_dimension = 1
        for item in dimensions[mode + 1:]:
            right_dimension *= item
        matrix = [
            residual[row * right_dimension : (row + 1) * right_dimension]
            for row in range(left_dimension)
        ]
        basis, residual_matrix, rank = factor_matrix(matrix, p, counters)
        counters["factorizations"] += 1
        next_rank = rank
        cores.append([
            [basis[row][index] for index in range(next_rank)]
            for row in range(ranks[-1] * dimension)
        ])
        residual = [value for row in residual_matrix for value in row]
        ranks.append(next_rank)
    final_rank = ranks[-1]
    final_dimension = dimensions[-1]
    if len(residual) != final_rank * final_dimension:
        raise AssertionError("final residual shape mismatch")
    cores.append([
        [residual[row * final_dimension + column]]
        for row in range(final_rank)
        for column in range(final_dimension)
    ])
    ranks.append(1)
    return {
        "ranks": ranks,
        "cores": cores,
        "operations": counters,
    }


def core_value(cores: list[list[list[list[int]]]], dimensions: list[int], indices: tuple[int, ...], p: int) -> int:
    vector = cores[0][indices[0]]
    for mode in range(1, len(dimensions)):
        core = cores[mode]
        left_rank = len(vector)
        next_vector = [0] * len(core[0])
        for right_index in range(len(core[0])):
            total = 0
            for left_index in range(left_rank):
                block = core[(left_index * dimensions[mode]) + indices[mode]]
                total += vector[left_index] * block[right_index]
            next_vector[right_index] = total % p
        vector = next_vector
    return vector[0] % p


def reconstruct_tensor(cores: list[list[list[list[int]]]], dimensions: list[int], p: int) -> list[int]:
    current = [[value % p for value in row] for row in cores[0]]
    for mode in range(1, len(dimensions)):
        dimension = dimensions[mode]
        left_rank = len(current[0])
        next_rows = []
        for row in current:
            for index in range(dimension):
                next_row = []
                for right_index in range(len(cores[mode][0])):
                    value = 0
                    for left_index in range(left_rank):
                        block = cores[mode][left_index * dimension + index]
                        value += row[left_index] * block[right_index]
                    next_row.append(value % p)
                next_rows.append(next_row)
        current = next_rows
    return [row[0] % p for row in current]


def core_entries(ranks: list[int], dimensions: list[int]) -> int:
    return sum(dimensions[index] * ranks[index] * ranks[index + 1] for index in range(len(dimensions)))


def build_tensor(curve: dict[str, Any], family: dict[str, Any]) -> tuple[list[int], list[int], dict[str, int], Point]:
    p = curve["p"]
    model = AffineCurve(p, curve["a"], curve["b"])
    a_points = [point(value) for value in family["progression"]["points"]]
    r_points = [point(value) for value in family["factor_base"]["points"]]
    target = point(family["relations"]["target_transcript"][0]["target"])
    if target is None:
        raise ValueError("finite target required")
    nu = nonsquare(p)
    dimensions = [len(a_points), len(r_points), len(r_points), len(r_points), len(r_points)]
    ops = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
    values = []
    for indices in itertools.product(*(range(size) for size in dimensions)):
        total: Point = None
        for source in [a_points[indices[0]], *(r_points[indices[index]] for index in range(1, 5))]:
            total = model.add(total, source, ops)
        if total is None:
            values.append(1)
            continue
        x, y = total
        tx, ty = target
        dx = (x - tx) % p
        dy = (y - ty) % p
        values.append((dx * dx - nu * dy * dy) % p)
    return values, dimensions, ops, target


def run_row(curve: dict[str, Any], family: dict[str, Any]) -> dict[str, Any]:
    values, dimensions, group_ops, target = build_tensor(curve, family)
    factor = exact_tt_factor(values, dimensions, curve["p"])
    reconstructed = reconstruct_tensor(factor["cores"], dimensions, curve["p"])
    mismatches = sum(left != right for left, right in zip(reconstructed, values))
    raw_ranks = raw_shape_schedule()
    exact_payload = core_entries(factor["ranks"], dimensions)
    raw_payload = core_entries(raw_ranks, dimensions)
    return {
        "curve_id": curve["id"],
        "family": family["family"],
        "q": curve["q"],
        "p": curve["p"],
        "target": point_json(target),
        "dimensions": dimensions,
        "tensor_entries": len(values),
        "tensor_digest": digest(values),
        "exact_tt_ranks": factor["ranks"],
        "raw_closure_ranks": raw_ranks,
        "exact_core_entries": exact_payload,
        "raw_core_entries_actual_dimensions": raw_payload,
        "compression_ratio_raw_over_exact": raw_payload / max(1, exact_payload),
        "reconstruction_mismatches": mismatches,
        "group_ops": group_ops,
        "factorization_ops": factor["operations"],
        "core_digest": digest(factor["cores"]),
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
    exact_payloads = [row["exact_core_entries"] for row in rows]
    raw_payloads = [row["raw_core_entries_actual_dimensions"] for row in rows]
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-exact-tt-factor-preflight-v1",
        "claim_status": ["OBSERVATION", "TOY-EVIDENCE", "MODEL-BOUND"],
        "source": {"producer_sha256": sha256_file(SCRIPT_PATH), "input_sha256": sha256_file(input_path)},
        "config": {"input_result": str(input_path.resolve()), "families": families, "source_tuple_enumeration": True, "factorization": "exact modular sequential TT rank factorization over F_p"},
        "rows": rows,
        "summary": {
            "rows": len(rows),
            "all_reconstructed": all(row["reconstruction_mismatches"] == 0 for row in rows),
            "all_enumerative": all(row["enumerative_diagnostic"] for row in rows),
            "min_exact_core_entries": min(exact_payloads),
            "max_exact_core_entries": max(exact_payloads),
            "min_raw_core_entries_actual_dimensions": min(raw_payloads),
            "max_raw_core_entries_actual_dimensions": max(raw_payloads),
            "any_strict_payload_reduction": any(row["exact_core_entries"] < row["raw_core_entries_actual_dimensions"] for row in rows),
            "algorithm_promotion_gate": False,
            "breakthrough_claim": False,
            "boundary": "Enumerative toy exact-TT factorization only; no non-enumerative compiler, end-to-end relation attack, or generic ECDLP claim.",
        },
        "peak_rss_bytes": rss_bytes(),
        "total_wall_seconds": time.perf_counter() - started,
        "result_digest": digest(rows),
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
