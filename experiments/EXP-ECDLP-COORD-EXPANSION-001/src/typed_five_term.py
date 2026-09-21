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
        "cyclic_pareto_typed_five", PARETO_SOURCE
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


def choose_sizes(q: int, occupancy_lambda: float) -> tuple[int, int]:
    candidates = []
    for progression_size in range(2, 128):
        for transverse_size in range(2, 128):
            formal_d4 = math.comb(transverse_size + 3, 4)
            occupancy = progression_size * formal_d4 / q
            if occupancy < occupancy_lambda:
                continue
            relation_collection_proxy = progression_size * transverse_size
            linear_algebra_proxy = transverse_size**2
            candidates.append(
                (
                    max(relation_collection_proxy, linear_algebra_proxy),
                    relation_collection_proxy + linear_algebra_proxy,
                    progression_size + transverse_size,
                    progression_size,
                    transverse_size,
                )
            )
    if not candidates:
        raise RuntimeError("typed size search exhausted")
    _, _, _, progression_size, transverse_size = min(candidates)
    return progression_size, transverse_size


def build_layers(
    q: int, progression_size: int, transverse_size: int, seed: int
) -> tuple[set[int], set[int], dict[str, Any]]:
    rng = random.Random(seed)
    for attempt in range(1, q + 1):
        start = rng.randrange(q)
        progression = {
            (start + index) % q for index in range(progression_size)
        }
        if 0 in progression:
            continue
        available = [
            value
            for value in range(1, q)
            if value not in progression
        ]
        transverse = set(rng.sample(available, transverse_size))
        return progression, transverse, {
            "progression_start": start,
            "placement_attempts": attempt,
        }
    raise RuntimeError("typed layer construction exhausted")


def geometry(
    progression: set[int], transverse: set[int], q: int
) -> dict[str, Any]:
    r2 = sumset(transverse, transverse, q)
    r3 = sumset(r2, transverse, q)
    r4 = sumset(r3, transverse, q)
    d5 = sumset(progression, r4, q)
    hits = Counter(
        (left + right) % q
        for left in progression
        for right in r4
    )
    assert set(hits) == d5
    t_perm = statistics.fmean(
        (len(progression) + 1) / (hits[target] + 1)
        if target in hits
        else float(len(progression))
        for target in range(1, q)
    )
    return {
        "progression_points": len(progression),
        "transverse_points": len(transverse),
        "log_unknowns": len(transverse) + 2,
        "d2r": len(r2),
        "d3r": len(r3),
        "d4r": len(r4),
        "d5_nonidentity": len(d5 - {0}),
        "success_probability": len(d5 - {0}) / (q - 1),
        "t_perm_scan_a": t_perm,
        "materialized_advice_entries": len(r4),
        "split_pairs": len(progression) * len(r4),
        "split_redundancy": len(progression) * len(r4) / len(d5),
        "relation_collection_proxy": (
            (len(transverse) + 2) * t_perm
        ),
        "linear_algebra_proxy": (len(transverse) + 2) ** 2,
        "compiler_transition_attempts": (
            len(transverse) ** 2
            + len(r2) * len(transverse)
            + len(r3) * len(transverse)
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
        progression_size, transverse_size = choose_sizes(
            q, occupancy_lambda
        )
        rows = []
        for draw in range(draws):
            progression, transverse, construction = build_layers(
                q,
                progression_size,
                transverse_size,
                seed ^ (q << 16) ^ draw,
            )
            rows.append(
                {
                    "draw": draw,
                    "construction": construction,
                    "geometry": geometry(progression, transverse, q),
                }
            )
        medians = {
            metric: statistics.median(
                row["geometry"][metric] for row in rows
            )
            for metric in rows[0]["geometry"]
        }
        cells.append(
            {
                "q": q,
                "progression_size": progression_size,
                "transverse_size": transverse_size,
                "formal_d4_classes": math.comb(
                    transverse_size + 3, 4
                ),
                "formal_occupancy": (
                    progression_size
                    * math.comb(transverse_size + 3, 4)
                    / q
                ),
                "draws": rows,
                "medians": medians,
            }
        )
    scaling = {
        metric: fit_exponent(
            [(cell["q"], cell["medians"][metric]) for cell in cells]
        )
        for metric in (
            "progression_points",
            "transverse_points",
            "log_unknowns",
            "d4r",
            "d5_nonidentity",
            "t_perm_scan_a",
            "relation_collection_proxy",
            "linear_algebra_proxy",
            "compiler_transition_attempts",
        )
    }
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-five-term-v1",
        "claim_status": [
            "HYPOTHESIS",
            "TOY-EVIDENCE",
            "MODEL-BOUND",
            "NOVELTY-UNVERIFIED",
        ],
        "source": {
            "typed_five_term_sha256": sha256_file(SCRIPT_PATH),
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
            "Typed cyclic support geometry only. A real attack needs "
            "hash-to-curve progression generators, coordinate-defined R, "
            "compressed exact D4 membership, rank, and descent."
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
    parser.add_argument("--seed", type=int, default=173205)
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
