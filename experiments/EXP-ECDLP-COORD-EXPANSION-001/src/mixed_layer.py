#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import random
import statistics
import sys
import time
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
PARETO_SOURCE = SCRIPT_PATH.with_name("cyclic_pareto.py")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_pareto() -> Any:
    spec = importlib.util.spec_from_file_location(
        "cyclic_pareto_mixed_layer", PARETO_SOURCE
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load cyclic Pareto source")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PARETO = load_pareto()


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            return value == divisor
        divisor = 3 if divisor == 2 else divisor + 2
    return True


def build_random_base(q: int, size: int, seed: int) -> tuple[int, ...]:
    return tuple(sorted(random.Random(seed).sample(range(1, q), size)))


def build_mixed_base(
    q: int,
    size: int,
    core_fraction: float,
    seed: int,
) -> dict[str, Any]:
    if not 0 <= core_fraction <= 1:
        raise ValueError("core fraction must lie in [0,1]")
    core_size = min(size, max(0, round(core_fraction * size)))
    layer_size = size - core_size
    rng = random.Random(seed)
    core = set(rng.sample(range(1, q), core_size))
    progression: set[int] | None = None
    progression_start = None
    attempts = 0
    if layer_size:
        for _ in range(q):
            attempts += 1
            start = rng.randrange(q)
            candidate = {(start + index) % q for index in range(layer_size)}
            if 0 in candidate or candidate & core:
                continue
            progression = candidate
            progression_start = start
            break
        if progression is None:
            raise RuntimeError("mixed progression placement exhausted")
    else:
        progression = set()
    base = tuple(sorted(core | progression))
    if len(base) != size or 0 in base:
        raise AssertionError("mixed base cardinality mismatch")
    return {
        "base": base,
        "core": sorted(core),
        "progression": sorted(progression),
        "core_size": core_size,
        "progression_size": layer_size,
        "progression_start": progression_start,
        "placement_attempts": attempts,
    }


def geometry(base: tuple[int, ...], q: int) -> dict[str, Any]:
    levels = PARETO.support_levels(base, q)
    d5_new = levels[5] - levels[1] - levels[3]
    transitions = [
        len(levels[depth - 1]) * len(base)
        for depth in range(1, 6)
    ]
    return {
        "d1": len(levels[1]),
        "d2": len(levels[2]),
        "d3": len(levels[3]),
        "d4": len(levels[4]),
        "d5": len(levels[5]),
        "d5_nonidentity": len(levels[5] - {0}),
        "d5_new": len(d5_new),
        "transition_attempts_by_depth": transitions,
        "transition_attempts_total": sum(transitions),
    }


def fit_exponent(points: list[tuple[int, float]]) -> float | None:
    if len(points) < 3:
        return None
    xs = [math.log2(q) for q, _ in points]
    ys = [math.log2(value) for _, value in points]
    x_mean = statistics.fmean(xs)
    y_mean = statistics.fmean(ys)
    denominator = sum((x - x_mean) ** 2 for x in xs)
    return sum(
        (x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)
    ) / denominator


def run_cell(
    q: int,
    occupancy_lambda: float,
    core_fractions: list[float],
    draws: int,
    seed: int,
) -> dict[str, Any]:
    size = PARETO.choose_size(
        q, occupancy_lambda, "sign_canonical"
    )
    nulls = []
    for draw in range(draws):
        base = build_random_base(
            q, size, seed ^ (q << 16) ^ draw ^ 0x9E3779B1
        )
        nulls.append(geometry(base, q))
    null_medians = {
        metric: statistics.median(record[metric] for record in nulls)
        for metric in (
            "d2",
            "d3",
            "d5_nonidentity",
            "d5_new",
            "transition_attempts_total",
        )
    }
    families = []
    for fraction_index, core_fraction in enumerate(core_fractions):
        rows = []
        for draw in range(draws):
            built = build_mixed_base(
                q,
                size,
                core_fraction,
                (
                    seed
                    ^ (q << 20)
                    ^ (fraction_index << 12)
                    ^ draw
                    ^ 0x85EBCA6B
                ),
            )
            row = {
                "draw": draw,
                "construction": {
                    key: value
                    for key, value in built.items()
                    if key != "base"
                },
                "geometry": geometry(built["base"], q),
            }
            row["ratios_to_random_median"] = {
                metric: row["geometry"][metric]
                / max(null_medians[metric], 1e-300)
                for metric in null_medians
            }
            ratios = row["ratios_to_random_median"]
            row["joint_effect_gate"] = (
                ratios["d2"] <= 0.8
                and ratios["d3"] <= 0.8
                and ratios["d5_nonidentity"] >= 0.9
                and ratios["d5_new"] >= 0.9
            )
            rows.append(row)
        median_ratios = {
            metric: statistics.median(
                row["ratios_to_random_median"][metric] for row in rows
            )
            for metric in null_medians
        }
        families.append(
            {
                "core_fraction_requested": core_fraction,
                "core_sizes_observed": sorted(
                    {
                        row["construction"]["core_size"]
                        for row in rows
                    }
                ),
                "progression_sizes_observed": sorted(
                    {
                        row["construction"]["progression_size"]
                        for row in rows
                    }
                ),
                "five_word_transverse_mass_heuristic": (
                    core_fraction**5
                    + 5
                    * core_fraction**4
                    * (1 - core_fraction)
                ),
                "draws": rows,
                "median_ratios_to_random": median_ratios,
                "joint_effect_passes": sum(
                    row["joint_effect_gate"] for row in rows
                ),
                "joint_effect_pass_fraction": (
                    sum(row["joint_effect_gate"] for row in rows) / draws
                ),
            }
        )
    return {
        "q": q,
        "factor_base_size": size,
        "formal_depth_5_classes": PARETO.formal_class_count(
            size, 5, "sign_canonical"
        ),
        "formal_occupancy": PARETO.formal_class_count(
            size, 5, "sign_canonical"
        )
        / q,
        "null_draws": draws,
        "null_medians": null_medians,
        "families": families,
    }


def run(
    primes: list[int],
    occupancy_lambda: float,
    core_fractions: list[float],
    draws: int,
    seed: int,
) -> dict[str, Any]:
    if any(not is_prime(q) for q in primes):
        raise ValueError("all group orders must be prime")
    started = time.perf_counter()
    cells = [
        run_cell(
            q, occupancy_lambda, core_fractions, draws, seed
        )
        for q in primes
    ]
    scaling = {}
    for core_fraction in core_fractions:
        key = str(core_fraction)
        scaling[key] = {}
        for metric in ("d2", "d3", "d5_new"):
            points = []
            for cell in cells:
                family = next(
                    item
                    for item in cell["families"]
                    if item["core_fraction_requested"] == core_fraction
                )
                values = [
                    row["geometry"][metric] for row in family["draws"]
                ]
                points.append((cell["q"], statistics.median(values)))
            scaling[key][metric] = fit_exponent(points)
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-mixed-layer-v1",
        "claim_status": [
            "HYPOTHESIS",
            "TOY-EVIDENCE",
            "MODEL-BOUND",
            "NOVELTY-UNVERIFIED",
        ],
        "source": {
            "mixed_layer_sha256": sha256_file(SCRIPT_PATH),
            "cyclic_pareto_sha256": sha256_file(PARETO_SOURCE),
        },
        "config": {
            "primes": primes,
            "occupancy_lambda": occupancy_lambda,
            "core_fractions": core_fractions,
            "draws": draws,
            "seed": seed,
        },
        "cells": cells,
        "joint_effect_pass_cells": [
            {
                "q": cell["q"],
                "core_fraction": family["core_fraction_requested"],
                "passes": family["joint_effect_passes"],
            }
            for cell in cells
            for family in cell["families"]
            if family["joint_effect_passes"]
        ],
        "median_scaling_exponents": scaling,
        "breakthrough_claim": False,
        "total_wall_seconds": time.perf_counter() - started,
        "boundary": (
            "Cyclic-group additive feasibility only. Scalar-defined bases "
            "are diagnostic constructions, not ECDLP factor bases with "
            "known logarithms or coordinate membership."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--primes",
        nargs="+",
        type=int,
        default=[251, 503, 1009, 2003, 4001, 8009],
    )
    parser.add_argument("--occupancy-lambda", type=float, default=0.5)
    parser.add_argument(
        "--core-fractions",
        nargs="+",
        type=float,
        default=[0.0, 0.45, 0.55, 0.65, 0.8, 1.0],
    )
    parser.add_argument("--draws", type=int, default=31)
    parser.add_argument("--seed", type=int, default=161803)
    args = parser.parse_args()
    print(
        json.dumps(
            run(
                args.primes,
                args.occupancy_lambda,
                args.core_fractions,
                args.draws,
                args.seed,
            ),
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
