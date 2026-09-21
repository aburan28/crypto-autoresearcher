#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
import resource
import time
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
Point = tuple[int, int] | None


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if platform.system() == "Darwin" else value * 1024)


class Curve:
    def __init__(self, p: int, a: int) -> None:
        self.p = p
        self.a = a % p

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
        ops["field_inversions"] += 1
        ops["field_multiplications"] += 4
        return (slope * slope - x1 - x2) % self.p, (slope * (x1 - (slope * slope - x1 - x2)) - y1) % self.p


def point(value: list[int] | None) -> Point:
    return None if value is None else (value[0], value[1])


def nonsquare(p: int) -> int:
    for value in range(2, p):
        if pow(value, (p - 1) // 2, p) == p - 1:
            return value
    raise ValueError("no nonsquare")


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


def inverse_matrix(matrix: list[list[int]], p: int, ops: dict[str, int]) -> list[list[int]]:
    size = len(matrix)
    work = [[value % p for value in row] + [int(i == j) for j in range(size)] for i, row in enumerate(matrix)]
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        if pivot is None:
            raise ValueError("singular cross matrix")
        work[column], work[pivot] = work[pivot], work[column]
        inverse = pow(work[column][column], -1, p)
        ops["field_inversions"] += 1
        work[column] = [(value * inverse) % p for value in work[column]]
        ops["field_multiplications"] += 2 * size
        for row in range(size):
            if row == column or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [(left - factor * right) % p for left, right in zip(work[row], work[column])]
            ops["field_multiplications"] += 2 * size
            ops["field_subtractions"] += 2 * size
    return [row[size:] for row in work]


def independent_rows(rows: list[list[int]], p: int) -> tuple[list[int], int]:
    if not rows:
        return [], 0
    work = [[value % p for value in row] for row in rows]
    ids = list(range(len(rows)))
    rank = 0
    pivots = []
    for column in range(len(work[0])):
        pivot = next((row for row in range(rank, len(work)) if work[row][column]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        ids[rank], ids[pivot] = ids[pivot], ids[rank]
        inverse = pow(work[rank][column], -1, p)
        work[rank] = [(value * inverse) % p for value in work[rank]]
        for row in range(rank + 1, len(work)):
            factor = work[row][column]
            if factor:
                work[row] = [(left - factor * right) % p for left, right in zip(work[row], work[rank])]
        pivots.append(ids[rank])
        rank += 1
        if rank == len(work):
            break
    return pivots, rank


class Oracle:
    def __init__(self, curve: dict[str, Any], family: dict[str, Any]) -> None:
        self.p = curve["p"]
        self.curve = Curve(curve["p"], curve["a"])
        self.nu = nonsquare(self.p)
        self.a_points = [point(value) for value in family["progression"]["points"]]
        self.r_points = [point(value) for value in family["factor_base"]["points"]]
        self.target = point(family["relations"]["target_transcript"][0]["target"])
        if self.target is None:
            raise ValueError("finite target required")
        self.cache: dict[tuple[int, ...], int] = {}
        self.ops = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0, "field_subtractions": 0, "cache_hits": 0, "unique_queries": 0}

    def value(self, indices: tuple[int, ...]) -> int:
        if indices in self.cache:
            self.ops["cache_hits"] += 1
            return self.cache[indices]
        total: Point = None
        sources = [self.a_points[indices[0]], *(self.r_points[indices[index]] for index in range(1, 5))]
        for source in sources:
            total = self.curve.add(total, source, self.ops)
        if total is None:
            result = 1
        else:
            x, y = total
            tx, ty = self.target
            dx = (x - tx) % self.p
            dy = (y - ty) % self.p
            result = (dx * dx - self.nu * dy * dy) % self.p
        self.cache[indices] = result
        self.ops["unique_queries"] += 1
        return result


def matrix_entry(oracle: Oracle, dimensions: list[int], cut: int, row: int, column: int) -> int:
    left = unrank(row, dimensions[:cut])
    right = unrank(column, dimensions[cut:])
    return oracle.value(left + right)


def cross_cut(oracle: Oracle, dimensions: list[int], cut: int, target_rank: int, seed: int, holdouts: int = 64) -> dict[str, Any]:
    row_count = product(dimensions[:cut])
    column_count = product(dimensions[cut:])
    if target_rank > min(row_count, column_count):
        return {"cut": cut, "target_rank": target_rank, "status": "REJECTED_ABOVE_AMBIENT", "holdout_mismatches": holdouts}
    rng = random.Random(seed)
    chosen = None
    candidate_trials = 0
    row_samples = None
    selected_columns = None
    selected_rows = None
    while candidate_trials < 16:
        candidate_trials += 1
        selected_columns = sorted(rng.sample(range(column_count), target_rank))
        row_samples = [[matrix_entry(oracle, dimensions, cut, row, column) for column in selected_columns] for row in range(row_count)]
        selected_rows, rank = independent_rows(row_samples, oracle.p)
        if rank == target_rank:
            chosen = True
            break
    if not chosen or selected_rows is None or selected_columns is None or row_samples is None:
        return {"cut": cut, "target_rank": target_rank, "status": "CROSS_RANK_FAILURE", "candidate_trials": candidate_trials, "holdout_count": holdouts, "holdout_mismatches": holdouts}
    cross = [[row_samples[row][index] for index in range(target_rank)] for row in selected_rows]
    inverse = inverse_matrix(cross, oracle.p, oracle.ops)
    right = [[matrix_entry(oracle, dimensions, cut, row, column) for column in range(column_count)] for row in selected_rows]
    rng_holdout = random.Random(seed ^ 0x9E3779B97F4A7C15)
    mismatches = 0
    checked = 0
    for _ in range(holdouts):
        row = rng_holdout.randrange(row_count)
        column = rng_holdout.randrange(column_count)
        left = row_samples[row]
        coefficients = [sum(left[i] * inverse[i][j] for i in range(target_rank)) % oracle.p for j in range(target_rank)]
        predicted = sum(coefficients[i] * right[i][column] for i in range(target_rank)) % oracle.p
        mismatches += int(predicted != matrix_entry(oracle, dimensions, cut, row, column))
        checked += 1
    skeleton_entries = row_count * target_rank + target_rank * column_count + target_rank * target_rank
    return {
        "cut": cut,
        "target_rank": target_rank,
        "row_count": row_count,
        "column_count": column_count,
        "selected_rows": selected_rows,
        "selected_columns": selected_columns,
        "candidate_trials": candidate_trials,
        "holdout_count": checked,
        "holdout_mismatches": mismatches,
        "skeleton_entries": skeleton_entries,
        "full_entries": row_count * column_count,
        "skeleton_over_full": skeleton_entries / max(1, row_count * column_count),
        "status": "PASS" if mismatches == 0 else "HOLDOUT_FAILURE",
    }


def run_row(curve: dict[str, Any], family: dict[str, Any], rank_row: dict[str, Any]) -> dict[str, Any]:
    oracle = Oracle(curve, family)
    dimensions = [len(oracle.a_points), len(oracle.r_points), len(oracle.r_points), len(oracle.r_points), len(oracle.r_points)]
    ranks = rank_row["exact_tt_ranks"]
    cuts = [cross_cut(oracle, dimensions, cut, ranks[cut], 1000003 + cut * 7919 + len(family["family"])) for cut in range(1, 5)]
    full_entries = product(dimensions)
    return {
        "curve_id": curve["id"],
        "family": family["family"],
        "dimensions": dimensions,
        "pilot_ranks": ranks,
        "cuts": cuts,
        "all_holdouts_exact": all(cut.get("holdout_mismatches", 1) == 0 and cut.get("status") == "PASS" for cut in cuts),
        "full_tensor_entries": full_entries,
        "unique_queries": oracle.ops["unique_queries"],
        "query_ratio_unique_over_full": oracle.ops["unique_queries"] / max(1, full_entries),
        "oracle_ops": oracle.ops,
        "oracle_cache_entries": len(oracle.cache),
        "result_digest": digest({"cuts": cuts, "dimensions": dimensions}),
        "non_enumerative": True,
    }


def run(input_path: Path, rank_path: Path, families: list[str]) -> dict[str, Any]:
    started = time.perf_counter()
    source = json.loads(input_path.read_text(encoding="utf-8"))
    ranks = json.loads(rank_path.read_text(encoding="utf-8"))
    rank_by_key = {(row["curve_id"], row["family"]): row for row in ranks["rows"]}
    rows = []
    for instance in source["instances"]:
        by_family = {item["family"]: item for item in instance["families"]}
        for family_name in families:
            key = (instance["curve"]["id"], family_name)
            rows.append(run_row(instance["curve"], by_family[family_name], rank_by_key[key]))
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-tt-cross-preflight-v1",
        "claim_status": ["NEGATIVE RESULT", "OBSERVATION", "TOY-EVIDENCE", "MODEL-BOUND"] if not all(row["all_holdouts_exact"] for row in rows) else ["OBSERVATION", "TOY-EVIDENCE", "MODEL-BOUND"],
        "source": {"producer_sha256": sha256_file(SCRIPT_PATH), "input_sha256": sha256_file(input_path), "rank_oracle_sha256": sha256_file(rank_path)},
        "config": {"families": families, "source_tuple_enumeration": False, "rank_budget": "sealed exact TT factorization oracle", "holdouts_per_cut": 64},
        "rows": rows,
        "summary": {
            "rows": len(rows),
            "all_non_enumerative": all(row["non_enumerative"] for row in rows),
            "all_holdouts_exact": all(row["all_holdouts_exact"] for row in rows),
            "all_rows_have_cross_failure": all(any(cut.get("status") == "CROSS_RANK_FAILURE" for cut in row["cuts"]) for row in rows),
            "query_work_below_full_tensor": all(row["query_ratio_unique_over_full"] < 1.0 for row in rows),
            "max_query_ratio": max(row["query_ratio_unique_over_full"] for row in rows),
            "min_query_ratio": min(row["query_ratio_unique_over_full"] for row in rows),
            "algorithm_promotion_gate": False,
            "breakthrough_claim": False,
            "boundary": "Pilot-guided sampled cross-unfolding only; no shared common basis, relation attack, or generic ECDLP claim.",
        },
        "peak_rss_bytes": rss_bytes(),
        "total_wall_seconds": time.perf_counter() - started,
        "result_digest": digest(rows),
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
