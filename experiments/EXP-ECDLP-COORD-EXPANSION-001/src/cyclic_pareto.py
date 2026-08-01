#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import statistics
import time
from pathlib import Path
from typing import Any, Iterable


SCRIPT_PATH = Path(__file__).resolve()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def signed_formal_class_count(fiber_count: int, depth: int) -> int:
    total = 1 if depth % 2 == 0 else 0
    for l1_norm in range(depth % 2 or 2, depth + 1, 2):
        for support_size in range(
            1, min(fiber_count, l1_norm) + 1
        ):
            total += (
                2**support_size
                * math.comb(fiber_count, support_size)
                * math.comb(l1_norm - 1, support_size - 1)
            )
    return total


def formal_class_count(size: int, depth: int, symmetry: str) -> int:
    if symmetry == "sign_canonical":
        return math.comb(size + depth - 1, depth)
    if symmetry == "sign_complete":
        if size % 2:
            raise ValueError("sign-complete size must be even")
        return signed_formal_class_count(size // 2, depth)
    raise ValueError(f"unknown symmetry: {symmetry}")


def choose_size(q: int, occupancy_lambda: float, symmetry: str) -> int:
    size = 2
    while formal_class_count(size, 5, symmetry) / q < occupancy_lambda:
        size += 2 if symmetry == "sign_complete" else 1
    return size


def support_levels(base: tuple[int, ...], q: int) -> list[set[int]]:
    levels = [{0}]
    for _ in range(5):
        levels.append(
            {
                (partial + scalar) % q
                for partial in levels[-1]
                for scalar in base
            }
        )
    return levels


def metrics(base: tuple[int, ...], q: int) -> tuple[int, int, int, int]:
    levels = support_levels(base, q)
    d5_new = levels[5] - levels[1] - levels[3]
    return (
        len(levels[2]),
        len(levels[3]),
        len(levels[5] - {0}),
        len(d5_new),
    )


def bases(q: int, size: int, symmetry: str) -> Iterable[tuple[int, ...]]:
    if symmetry == "sign_canonical":
        yield from itertools.combinations(range(1, q), size)
        return
    if symmetry == "sign_complete":
        for fibers in itertools.combinations(
            range(1, (q + 1) // 2), size // 2
        ):
            yield tuple(
                scalar
                for representative in fibers
                for scalar in (representative, (-representative) % q)
            )
        return
    raise ValueError(f"unknown symmetry: {symmetry}")


def dominates(
    left: tuple[int, int, int],
    right: tuple[int, int, int],
) -> bool:
    return (
        left[0] <= right[0]
        and left[1] <= right[1]
        and left[2] >= right[2]
        and left != right
    )


def pareto_frontier(
    triples: set[tuple[int, int, int]]
) -> list[tuple[int, int, int]]:
    frontier = []
    for candidate in sorted(triples):
        if any(dominates(other, candidate) for other in triples):
            continue
        frontier.append(candidate)
    return frontier


def weighted_median(
    metric_counts: dict[tuple[int, int, int, int], int], index: int
) -> float:
    counts: dict[int, int] = {}
    for value, multiplicity in metric_counts.items():
        counts[value[index]] = counts.get(value[index], 0) + multiplicity
    total = sum(counts.values())

    def order_statistic(position: int) -> int:
        cumulative = 0
        for value, multiplicity in sorted(counts.items()):
            cumulative += multiplicity
            if cumulative > position:
                return value
        raise AssertionError("weighted median position was not reached")

    lower = order_statistic((total - 1) // 2)
    upper = order_statistic(total // 2)
    return (lower + upper) / 2


def scaling_normal_form(base: tuple[int, ...], q: int) -> tuple[int, ...]:
    return min(
        tuple(sorted((multiplier * value) % q for value in base))
        for multiplier in range(1, q)
    )


def analyze_cell(
    q: int, occupancy_lambda: float, symmetry: str
) -> dict[str, Any]:
    size = choose_size(q, occupancy_lambda, symmetry)
    started = time.perf_counter()
    metric_counts: dict[tuple[int, int, int, int], int] = {}
    examples: dict[tuple[int, int, int, int], tuple[int, ...]] = {}
    sets_enumerated = 0
    for base in bases(q, size, symmetry):
        value = metrics(base, q)
        sets_enumerated += 1
        metric_counts[value] = metric_counts.get(value, 0) + 1
        examples.setdefault(value, base)
    d2_median = weighted_median(metric_counts, 0)
    d3_median = weighted_median(metric_counts, 1)
    d5_new_median = weighted_median(metric_counts, 3)
    d2_limit = 0.8 * d2_median
    d3_limit = 0.8 * d3_median
    d5_new_floor = 0.9 * d5_new_median
    qualifying_metrics = [
        value
        for value in metric_counts
        if value[0] <= d2_limit
        and value[1] <= d3_limit
        and value[3] >= d5_new_floor
    ]
    qualifying_count = sum(
        metric_counts[value] for value in qualifying_metrics
    )
    qualifying_metric_set = set(qualifying_metrics)
    scaling_orbits: dict[tuple[int, ...], int] = {}
    if qualifying_count:
        for base in bases(q, size, symmetry):
            if metrics(base, q) not in qualifying_metric_set:
                continue
            normal_form = scaling_normal_form(base, q)
            scaling_orbits[normal_form] = (
                scaling_orbits.get(normal_form, 0) + 1
            )
    frontier = pareto_frontier(
        {(value[0], value[1], value[3]) for value in metric_counts}
    )
    best_examples = sorted(
        qualifying_metrics,
        key=lambda value: (
            -value[3],
            value[0] + value[1],
            value[0],
            value[1],
        ),
    )[:10]
    minimum_d2_at_coverage = min(
        (
            value[0]
            for value in metric_counts
            if value[3] >= d5_new_floor
        ),
        default=None,
    )
    minimum_d3_at_coverage = min(
        (
            value[1]
            for value in metric_counts
            if value[3] >= d5_new_floor
        ),
        default=None,
    )
    maximum_d5_new_at_joint_compression = max(
        (
            value[3]
            for value in metric_counts
            if value[0] <= d2_limit and value[1] <= d3_limit
        ),
        default=None,
    )
    return {
        "q": q,
        "symmetry": symmetry,
        "occupancy_lambda_target": occupancy_lambda,
        "factor_base_size": size,
        "formal_depth_5_classes": formal_class_count(size, 5, symmetry),
        "formal_occupancy": formal_class_count(size, 5, symmetry) / q,
        "sets_enumerated": sets_enumerated,
        "unique_metric_tuples": len(metric_counts),
        "medians": {
            "d2": d2_median,
            "d3": d3_median,
            "d5_nonidentity": weighted_median(metric_counts, 2),
            "d5_new": d5_new_median,
        },
        "joint_thresholds": {
            "d2_maximum": d2_limit,
            "d3_maximum": d3_limit,
            "d5_new_minimum": d5_new_floor,
        },
        "qualifying_sets": qualifying_count,
        "qualifying_fraction": qualifying_count / sets_enumerated,
        "qualifying_scaling_orbits": [
            {
                "normal_form": list(normal_form),
                "enumerated_members": multiplicity,
            }
            for normal_form, multiplicity in sorted(
                scaling_orbits.items()
            )
        ],
        "minimum_d2_at_required_coverage": minimum_d2_at_coverage,
        "minimum_d3_at_required_coverage": minimum_d3_at_coverage,
        "maximum_d5_new_at_joint_compression": (
            maximum_d5_new_at_joint_compression
        ),
        "pareto_frontier": [
            {"d2": value[0], "d3": value[1], "d5_new": value[2]}
            for value in sorted(frontier)
        ],
        "qualifying_examples": [
            {
                "base": list(examples[value]),
                "d2": value[0],
                "d3": value[1],
                "d5_nonidentity": value[2],
                "d5_new": value[3],
                "multiplicity": metric_counts[value],
            }
            for value in best_examples
        ],
        "wall_seconds": time.perf_counter() - started,
    }


def run(primes: list[int], occupancy_lambdas: list[float]) -> dict[str, Any]:
    started = time.perf_counter()
    cells = [
        analyze_cell(q, occupancy_lambda, symmetry)
        for q in primes
        for occupancy_lambda in occupancy_lambdas
        for symmetry in ("sign_canonical", "sign_complete")
    ]
    unique_populations: dict[tuple[int, str, int], int] = {}
    for cell in cells:
        key = (
            cell["q"],
            cell["symmetry"],
            cell["factor_base_size"],
        )
        unique_populations.setdefault(key, cell["sets_enumerated"])
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-cyclic-pareto-v1",
        "claim_status": [
            "TOY-EVIDENCE",
            "MODEL-BOUND",
            "NOVELTY-UNVERIFIED",
        ],
        "source_sha256": sha256_file(SCRIPT_PATH),
        "config": {
            "primes": primes,
            "occupancy_lambdas": occupancy_lambdas,
            "thresholds": {
                "d2_ratio_maximum": 0.8,
                "d3_ratio_maximum": 0.8,
                "d5_new_retention_minimum": 0.9,
            },
        },
        "cells": cells,
        "cells_with_qualifying_sets": [
            (
                f"{cell['q']}|lambda={cell['occupancy_lambda_target']}|"
                f"{cell['symmetry']}"
            )
            for cell in cells
            if cell["qualifying_sets"]
        ],
        "total_cell_enumerations": sum(
            cell["sets_enumerated"] for cell in cells
        ),
        "total_unique_population_sets": sum(unique_populations.values()),
        "unique_populations": len(unique_populations),
        "breakthrough_claim": False,
        "total_wall_seconds": time.perf_counter() - started,
        "boundary": (
            "Exhaustive small cyclic-group feasibility census only. "
            "No coordinate predicate, relation matrix, descent, or ECDLP "
            "algorithm is constructed."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--primes", nargs="+", type=int, default=[19, 31, 43, 59]
    )
    parser.add_argument(
        "--occupancy-lambdas",
        nargs="+",
        type=float,
        default=[0.2, 0.5, 1.5],
    )
    args = parser.parse_args()
    print(
        json.dumps(
            run(args.primes, args.occupancy_lambdas),
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
