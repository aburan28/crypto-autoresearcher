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
from collections import Counter
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
        "cyclic_pareto_asymmetric", PARETO_SOURCE
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


def sumset(left: set[int], right: set[int], q: int) -> set[int]:
    return {(a + b) % q for a in left for b in right}


def choose_layer_sizes(
    q: int, occupancy_lambda: float
) -> tuple[int, int]:
    candidates = []
    for progression_size in range(2, 128):
        pair_classes = 2 * progression_size - 1
        for random_size in range(2, 128):
            triple_classes = math.comb(random_size + 2, 3)
            occupancy = pair_classes * triple_classes / q
            if occupancy < occupancy_lambda:
                continue
            candidates.append(
                (
                    progression_size + random_size,
                    triple_classes,
                    progression_size,
                    random_size,
                )
            )
    if not candidates:
        raise RuntimeError("layer-size search exhausted")
    _, _, progression_size, random_size = min(candidates)
    return progression_size, random_size


def build_layers(
    q: int, progression_size: int, random_size: int, seed: int
) -> tuple[set[int], set[int], dict[str, Any]]:
    rng = random.Random(seed)
    for attempts in range(1, q + 1):
        start = rng.randrange(q)
        progression = {
            (start + index) % q for index in range(progression_size)
        }
        if 0 in progression:
            continue
        available = [
            scalar
            for scalar in range(1, q)
            if scalar not in progression
        ]
        transverse = set(rng.sample(available, random_size))
        return progression, transverse, {
            "progression_start": start,
            "placement_attempts": attempts,
        }
    raise RuntimeError("layer construction exhausted")


def layer_geometry(
    progression: set[int], transverse: set[int], q: int
) -> dict[str, Any]:
    d2 = sumset(progression, progression, q)
    r2 = sumset(transverse, transverse, q)
    d3 = sumset(r2, transverse, q)
    d5 = sumset(d2, d3, q)
    hits = Counter(
        (left + right) % q for left in d2 for right in d3
    )
    assert set(hits) == d5
    t_perm = statistics.fmean(
        (len(d2) + 1) / (hits[target] + 1)
        if target in hits
        else float(len(d2))
        for target in range(1, q)
    )
    return {
        "progression_size": len(progression),
        "transverse_size": len(transverse),
        "columns": len(progression) + len(transverse),
        "d2": len(d2),
        "d3": len(d3),
        "d5": len(d5),
        "d5_nonidentity": len(d5 - {0}),
        "success_probability": len(d5 - {0}) / (q - 1),
        "split_pairs": len(d2) * len(d3),
        "split_redundancy": len(d2) * len(d3) / len(d5),
        "t_perm_scan_d2": t_perm,
        "support_mass_entries": len(d2) + len(d3),
        "compiler_transition_attempts": (
            len(progression) ** 2
            + len(transverse) ** 2
            + len(r2) * len(transverse)
        ),
    }


def homogeneous_geometry(
    q: int, size: int, seed: int
) -> dict[str, Any]:
    base = set(random.Random(seed).sample(range(1, q), size))
    levels = PARETO.support_levels(tuple(sorted(base)), q)
    return {
        "columns": size,
        "d2": len(levels[2]),
        "d3": len(levels[3]),
        "d5_nonidentity": len(levels[5] - {0}),
        "success_probability": len(levels[5] - {0}) / (q - 1),
        "compiler_transition_attempts": (
            size**2 + len(levels[2]) * size
        ),
    }


def fit_exponent(points: list[tuple[int, float]]) -> float:
    xs = [math.log2(q) for q, _ in points]
    ys = [math.log2(value) for _, value in points]
    x_mean = statistics.fmean(xs)
    y_mean = statistics.fmean(ys)
    return sum(
        (x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)
    ) / sum((x - x_mean) ** 2 for x in xs)


def run(
    primes: list[int],
    occupancy_lambda: float,
    draws: int,
    seed: int,
) -> dict[str, Any]:
    if any(not is_prime(q) for q in primes):
        raise ValueError("all group orders must be prime")
    started = time.perf_counter()
    cells = []
    for q in primes:
        progression_size, random_size = choose_layer_sizes(
            q, occupancy_lambda
        )
        homogeneous_size = PARETO.choose_size(
            q, occupancy_lambda, "sign_canonical"
        )
        rows = []
        homogeneous_rows = []
        for draw in range(draws):
            progression, transverse, construction = build_layers(
                q,
                progression_size,
                random_size,
                seed ^ (q << 16) ^ draw,
            )
            rows.append(
                {
                    "draw": draw,
                    "construction": construction,
                    "geometry": layer_geometry(
                        progression, transverse, q
                    ),
                }
            )
            homogeneous_rows.append(
                homogeneous_geometry(
                    q,
                    homogeneous_size,
                    seed ^ (q << 20) ^ draw ^ 0x9E3779B1,
                )
            )
        layer_medians = {
            metric: statistics.median(
                row["geometry"][metric] for row in rows
            )
            for metric in rows[0]["geometry"]
            if isinstance(rows[0]["geometry"][metric], (int, float))
        }
        homogeneous_medians = {
            metric: statistics.median(
                row[metric] for row in homogeneous_rows
            )
            for metric in homogeneous_rows[0]
        }
        cells.append(
            {
                "q": q,
                "occupancy_lambda": occupancy_lambda,
                "progression_size": progression_size,
                "transverse_size": random_size,
                "homogeneous_size": homogeneous_size,
                "formal_layer_occupancy": (
                    (2 * progression_size - 1)
                    * math.comb(random_size + 2, 3)
                    / q
                ),
                "formal_homogeneous_occupancy": (
                    math.comb(homogeneous_size + 4, 5) / q
                ),
                "draws": rows,
                "layer_medians": layer_medians,
                "homogeneous_medians": homogeneous_medians,
                "ratios_to_homogeneous": {
                    metric: layer_medians[metric]
                    / homogeneous_medians[metric]
                    for metric in (
                        "columns",
                        "d2",
                        "d3",
                        "d5_nonidentity",
                        "success_probability",
                        "compiler_transition_attempts",
                    )
                },
            }
        )
    scaling = {
        metric: fit_exponent(
            [(cell["q"], cell["layer_medians"][metric]) for cell in cells]
        )
        for metric in (
            "columns",
            "d2",
            "d3",
            "d5_nonidentity",
            "t_perm_scan_d2",
            "support_mass_entries",
            "compiler_transition_attempts",
        )
    }
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-asymmetric-layers-v1",
        "claim_status": [
            "HYPOTHESIS",
            "TOY-EVIDENCE",
            "MODEL-BOUND",
            "NOVELTY-UNVERIFIED",
        ],
        "source": {
            "asymmetric_layers_sha256": sha256_file(SCRIPT_PATH),
            "cyclic_pareto_sha256": sha256_file(PARETO_SOURCE),
        },
        "config": {
            "primes": primes,
            "occupancy_lambda": occupancy_lambda,
            "draws": draws,
            "seed": seed,
        },
        "cells": cells,
        "median_scaling_exponents": scaling,
        "breakthrough_claim": False,
        "total_wall_seconds": time.perf_counter() - started,
        "boundary": (
            "Position-specific cyclic support geometry only. The scalar "
            "layers are not coordinate factor bases, and materialized D3 "
            "advice, relation rank, and descent are not solved."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--primes",
        nargs="+",
        type=int,
        default=[251, 503, 1009, 2003, 4001, 8009, 16001, 32003],
    )
    parser.add_argument("--occupancy-lambda", type=float, default=0.5)
    parser.add_argument("--draws", type=int, default=31)
    parser.add_argument("--seed", type=int, default=141421)
    args = parser.parse_args()
    print(
        json.dumps(
            run(
                args.primes,
                args.occupancy_lambda,
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
