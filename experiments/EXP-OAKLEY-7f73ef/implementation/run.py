#!/usr/bin/env python3
"""Stage-0 subfield hit count for EXP-OAKLEY-7f73ef.

Counts how many subfield x-coordinates occur as a four-point factor-base
sum. The band is three binomial standard deviations around 1/120 and is
not fitted to the count.
"""

from __future__ import annotations

import argparse
import array
import json
from pathlib import Path

EXPERIMENT_ID = "EXP-OAKLEY-7f73ef"
RUN_ID = "RUN-OAKLEY-326307"
DEGREE = 25
ORDER = (1 << DEGREE) - 1
MASK = (1 << DEGREE) - 1
REDUCTION = (1 << 3) | 1
B_COEFFICIENT = 2
SUBFIELD_SIZE = 32
FACTORIAL = 120
# (120 * count - 32)^2 <= 9 * 32 * 119  is the closed 3-sd band.
BAND_SQUARE = 9 * 32 * 119


def multiply_by_z(value: int) -> int:
    value <<= 1
    if value & (1 << DEGREE):
        value = (value & MASK) ^ REDUCTION
    return value


def build_tables() -> tuple[array.array, array.array]:
    exponential = array.array("I", [0]) * ORDER
    logarithm = array.array("I", [0]) * (1 << DEGREE)
    value = 1
    for index in range(ORDER):
        exponential[index] = value
        logarithm[value] = index
        value = multiply_by_z(value)
    if value != 1:
        raise RuntimeError("z did not return to 1 at 2^25-1")
    return exponential, logarithm


def multiply(exponential: array.array, logarithm: array.array, left: int, right: int) -> int:
    if left == 0 or right == 0:
        return 0
    return exponential[(logarithm[left] + logarithm[right]) % ORDER]


def inverse(exponential: array.array, logarithm: array.array, value: int) -> int:
    return exponential[(ORDER - logarithm[value]) % ORDER]


def trace(exponential: array.array, logarithm: array.array, value: int) -> int:
    if value == 0:
        return 0
    total = 0
    exponent = logarithm[value]
    for index in range(DEGREE):
        total ^= exponential[(exponent * (1 << index)) % ORDER]
    return total


def half_trace(exponential: array.array, logarithm: array.array, value: int) -> int:
    if value == 0:
        return 0
    total = 0
    exponent = logarithm[value]
    for index in range(12):
        total ^= exponential[(exponent * (1 << (2 * index + 1))) % ORDER]
    return total


def subfield(exponential: array.array, logarithm: array.array) -> list[int]:
    generator = exponential[ORDER // 31]
    elements = {0}
    value = 1
    for _ in range(31):
        elements.add(value)
        value = multiply(exponential, logarithm, value, generator)
    return sorted(elements)


def on_curve(exponential: array.array, logarithm: array.array, x_coord: int, y_coord: int) -> bool:
    left = multiply(exponential, logarithm, y_coord, y_coord) ^ multiply(
        exponential, logarithm, x_coord, y_coord
    )
    right = multiply(
        exponential, logarithm, multiply(exponential, logarithm, x_coord, x_coord), x_coord
    ) ^ B_COEFFICIENT
    return left == right


def factor_base(
    exponential: array.array, logarithm: array.array, domain: list[int]
) -> list[tuple[int, int]]:
    points = [(0, exponential[(logarithm[B_COEFFICIENT] * (1 << 24)) % ORDER])]
    for x_coord in domain:
        if x_coord == 0:
            continue
        x_squared = multiply(exponential, logarithm, x_coord, x_coord)
        residue = x_coord ^ multiply(
            exponential, logarithm, B_COEFFICIENT, inverse(exponential, logarithm, x_squared)
        )
        if trace(exponential, logarithm, residue) != 0:
            continue
        slope = half_trace(exponential, logarithm, residue)
        y_coord = multiply(exponential, logarithm, x_coord, slope)
        points.append((x_coord, y_coord))
        points.append((x_coord, y_coord ^ x_coord))
    return sorted(points)


def point_add(exponential, logarithm, left, right):
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2:
        if y2 == (x1 ^ y1):
            return None
        if x1 == 0:
            return None
        slope = x1 ^ multiply(exponential, logarithm, y1, inverse(exponential, logarithm, x1))
        x3 = multiply(exponential, logarithm, slope, slope) ^ slope
        y3 = multiply(exponential, logarithm, x1, x1) ^ multiply(
            exponential, logarithm, slope ^ 1, x3
        )
        return x3, y3
    slope = multiply(exponential, logarithm, y1 ^ y2, inverse(exponential, logarithm, x1 ^ x2))
    x3 = multiply(exponential, logarithm, slope, slope) ^ slope ^ x1 ^ x2
    y3 = multiply(exponential, logarithm, slope, x1 ^ x3) ^ x3 ^ y1
    return x3, y3


def planted_report(exponential, logarithm, domain, points) -> dict:
    domain_set = set(domain)
    closed = all(
        (left ^ right) in domain_set and multiply(exponential, logarithm, left, right) in domain_set
        for left in domain
        for right in domain
    )
    fixed = all(
        element == 0 or exponential[(32 * logarithm[element]) % ORDER] == element
        for element in domain
    )
    b_outside = exponential[(32 * logarithm[B_COEFFICIENT]) % ORDER] != B_COEFFICIENT
    nonzero = [point for point in points if point[0] != 0]
    identities = False
    planted_point = None
    if len(nonzero) >= 3 and all(on_curve(exponential, logarithm, point[0], point[1]) for point in points):
        first, second, third = nonzero[0], nonzero[1], nonzero[2]
        doubled = point_add(exponential, logarithm, first, first)
        associated = point_add(
            exponential, logarithm, point_add(exponential, logarithm, first, second), third
        ) == point_add(
            exponential, logarithm, first, point_add(exponential, logarithm, second, third)
        )
        identities = (
            point_add(exponential, logarithm, first, (first[0], first[0] ^ first[1])) is None
            and doubled is not None
            and on_curve(exponential, logarithm, doubled[0], doubled[1])
            and associated
        )
        if doubled is not None:
            planted_point = {
                "double_x": doubled[0],
                "double_y": doubled[1],
                "x": first[0],
                "y": first[1],
            }
    ok = len(domain) == SUBFIELD_SIZE and closed and fixed and b_outside and len(points) >= 2 and identities
    return {
        "addition_identities": identities,
        "b_outside_subfield": b_outside,
        "factor_base_size": len(points),
        "planted_ok": ok,
        "planted_point": planted_point,
        "subfield_closed": closed and fixed,
        "subfield_size": len(domain),
    }


def subfield_hits(exponential, logarithm, domain, points) -> int:
    domain_set = set(domain)
    found: set[int] = set()
    for first in points:
        for second in points:
            partial = point_add(exponential, logarithm, first, second)
            if partial is None:
                continue
            for third in points:
                triple = point_add(exponential, logarithm, partial, third)
                if triple is None:
                    continue
                for fourth in points:
                    total = point_add(exponential, logarithm, triple, fourth)
                    if total is not None and total[0] in domain_set:
                        found.add(total[0])
    return len(found)


def within_band(count: int) -> bool:
    gap = FACTORIAL * count - SUBFIELD_SIZE
    return gap * gap <= BAND_SQUARE


def census() -> dict:
    if BAND_SQUARE != 9 * SUBFIELD_SIZE * (FACTORIAL - 1):
        raise RuntimeError("binomial band does not match 3 standard deviations")
    exponential, logarithm = build_tables()
    domain = subfield(exponential, logarithm)
    points = factor_base(exponential, logarithm, domain)
    planted = planted_report(exponential, logarithm, domain, points)
    count = subfield_hits(exponential, logarithm, domain, points) if planted["planted_ok"] else None
    return {
        "attack_claimed": False,
        "b": "z",
        "beyond_three_sd": count is not None and not within_band(count),
        "curve": "y^2 + x*y = x^3 + z",
        "experiment_id": EXPERIMENT_ID,
        "hit_count": count,
        "modulus": "z^25 + z^3 + 1",
        "p": 5,
        "planted": planted,
        "population": SUBFIELD_SIZE,
        "predicted_probability": "1/120",
        "run_id": RUN_ID,
        "within_three_sd": count is not None and within_band(count),
    }


def write_outputs(run_dir: Path, result: dict) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "raw-result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    planted = result["planted"]
    (run_dir / "manifest.yaml").write_text(
        "run:\n"
        f"  experiment_id: {EXPERIMENT_ID}\n"
        f"  run_id: {RUN_ID}\n"
        "  attack_claimed: false\n"
        "  metrics:\n"
        f"    planted_ok: {str(planted['planted_ok']).lower()}\n"
        f"    hit_count: {result['hit_count']}\n"
        f"    population: {result['population']}\n"
        f"    within_three_sd: {str(result['within_three_sd']).lower()}\n"
        f"    beyond_three_sd: {str(result['beyond_three_sd']).lower()}\n",
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
