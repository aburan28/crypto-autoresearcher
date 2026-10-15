#!/usr/bin/env python3
"""Stage-0 decomposition-fraction count for EXP-ECDLP-422afc.

Enumeration only. The script records observations and does not fit an exponent.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

A = 1
B = 1
PRIMES = (101, 211, 307)
EXPERIMENT_ID = "EXP-ECDLP-422afc"
RUN_ID = "RUN-ECDLP-06bb83"
FORMULA = 0.5


def legendre(value: int, prime: int) -> int:
    return pow(value % prime, (prime - 1) // 2, prime)


def summation_s3(x1: int, x2: int, x3: int, prime: int) -> int:
    difference = (x1 - x2) % prime
    first = difference * difference % prime * (x3 * x3 % prime) % prime
    middle = ((x1 + x2) * ((x1 * x2 + A) % prime) + 2 * B) % prime
    second = 2 * middle % prime * x3 % prime
    third = pow((x1 * x2 - A) % prime, 2, prime)
    fourth = 4 * B % prime * ((x1 + x2) % prime) % prime
    return (first - second + third - fourth) % prime


def square_root(value: int, prime: int) -> int | None:
    residue = value % prime
    if legendre(residue, prime) == prime - 1:
        return None
    for candidate in range(prime):
        if candidate * candidate % prime == residue:
            return candidate
    return None


def add_points(prime: int, left, right):
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % prime == 0:
        return None
    if left == right:
        if y1 == 0:
            return None
        slope = ((3 * x1 * x1 + A) * pow(2 * y1, prime - 2, prime)) % prime
    else:
        slope = ((y2 - y1) * pow((x2 - x1) % prime, prime - 2, prime)) % prime
    x3 = (slope * slope - x1 - x2) % prime
    y3 = (slope * (x1 - x3) - y1) % prime
    return x3, y3


def factor_base(prime: int) -> list[tuple[int, int]]:
    bound = math.isqrt(prime)
    points = []
    for x in range(bound):
        y = square_root((x * x * x + A * x + B) % prime, prime)
        if y is not None:
            points.append((x, y))
    return points


def cell(prime: int) -> dict:
    points = factor_base(prime)
    xs = [point[0] for point in points]
    planted = None
    if len(points) >= 2:
        total = add_points(prime, points[0], points[1])
        if total is not None:
            planted = {
                "x1": points[0][0],
                "x2": points[1][0],
                "x_sum": total[0],
                "s3": summation_s3(points[0][0], points[1][0], total[0], prime),
            }
    decomposing = 0
    for target in range(prime):
        if any(
            summation_s3(x1, x2, target, prime) == 0
            for index, x1 in enumerate(xs)
            for x2 in xs[index + 1 :]
        ):
            decomposing += 1
    pair_checks = len(xs) * (len(xs) - 1) // 2
    fraction = decomposing / prime
    return {
        "prime": prime,
        "factor_base_bound": math.isqrt(prime),
        "factor_base_size": len(xs),
        "pair_checks_per_target": pair_checks,
        "decomposing_count": decomposing,
        "fraction": fraction,
        "formula": FORMULA,
        "abs_error": abs(fraction - FORMULA),
        "planted_s3_zero": planted is not None and planted["s3"] == 0,
        "planted": planted,
        "attack_claimed": False,
    }


def census() -> dict:
    return {
        "experiment_id": EXPERIMENT_ID,
        "run_id": RUN_ID,
        "curve": "y^2 = x^3 + x + 1",
        "m": 2,
        "beta": 0.5,
        "primes": list(PRIMES),
        "cells": [cell(prime) for prime in PRIMES],
        "attack_claimed": False,
    }


def write_outputs(run_dir: Path, result: dict) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "raw-result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    failures = sum(1 for item in result["cells"] if not item["planted_s3_zero"])
    (run_dir / "manifest.yaml").write_text(
        "run:\n"
        f"  experiment_id: {EXPERIMENT_ID}\n"
        f"  run_id: {RUN_ID}\n"
        "  attack_claimed: false\n"
        "  metrics:\n"
        f"    cells: {len(result['cells'])}\n"
        f"    planted_failures: {failures}\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trial-plan", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    write_outputs(Path(args.run_dir), census())


if __name__ == "__main__":
    main()
