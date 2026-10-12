#!/usr/bin/env python3
"""Stage-0 subfield four-sum census for EXP-OAKLEY-4276c4.

Counts distinct ordered sums of four factor-base points. The factor-2 and
factor-4 bands are the idea's H2 readings and are not fitted to a census.
"""

from __future__ import annotations

import argparse
import array
import json
import math
from pathlib import Path

EXPERIMENT_ID = "EXP-OAKLEY-4276c4"
RUN_ID = "RUN-OAKLEY-524738"
DEGREE = 25
ORDER = (1 << DEGREE) - 1
MASK = (1 << DEGREE) - 1
REDUCTION = (1 << 3) | 1
FIELD_SIZE = 1 << DEGREE
PREDICTED_COUNT = 376992
B_COEFFICIENT = 2  # the basis element z


def _require_prediction() -> None:
    if math.comb(36, 5) != PREDICTED_COUNT:
        raise RuntimeError("C(36, 5) is not the frozen predicted count")


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


def on_curve(
    exponential: array.array, logarithm: array.array, x_coord: int, y_coord: int
) -> bool:
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
    points: list[tuple[int, int]] = []
    y_at_zero = exponential[(logarithm[B_COEFFICIENT] * (1 << 24)) % ORDER]
    points.append((0, y_at_zero))
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


def point_add(
    exponential: array.array,
    logarithm: array.array,
    left: tuple[int, int] | None,
    right: tuple[int, int] | None,
) -> tuple[int, int] | None:
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
    slope = multiply(
        exponential, logarithm, y1 ^ y2, inverse(exponential, logarithm, x1 ^ x2)
    )
    x3 = multiply(exponential, logarithm, slope, slope) ^ slope ^ x1 ^ x2
    y3 = multiply(exponential, logarithm, slope, x1 ^ x3) ^ x3 ^ y1
    return x3, y3


def planted_report(
    exponential: array.array,
    logarithm: array.array,
    domain: list[int],
    points: list[tuple[int, int]],
) -> dict:
    closed = all(
        (left ^ right) in domain
        and multiply(exponential, logarithm, left, right) in domain
        for left in domain
        for right in domain
    )
    fixed = all(
        element == 0
        or exponential[(32 * logarithm[element]) % ORDER] == element
        for element in domain
    )
    b_outside = exponential[(32 * logarithm[B_COEFFICIENT]) % ORDER] != B_COEFFICIENT
    nonzero = [point for point in points if point[0] != 0]
    identities = False
    planted_point = None
    if len(nonzero) >= 3 and all(
        on_curve(exponential, logarithm, point[0], point[1]) for point in points
    ):
        first, second, third = nonzero[0], nonzero[1], nonzero[2]
        doubled = point_add(exponential, logarithm, first, first)
        associated = point_add(
            exponential,
            logarithm,
            point_add(exponential, logarithm, first, second),
            third,
        ) == point_add(
            exponential,
            logarithm,
            first,
            point_add(exponential, logarithm, second, third),
        )
        identities = (
            point_add(exponential, logarithm, first, (first[0], first[0] ^ first[1])) is None
            and doubled is not None
            and on_curve(exponential, logarithm, doubled[0], doubled[1])
            and associated
        )
        if doubled is not None:
            planted_point = {
                "x": first[0],
                "y": first[1],
                "double_x": doubled[0],
                "double_y": doubled[1],
            }
    ok = (
        len(domain) == 32
        and closed
        and fixed
        and b_outside
        and len(points) >= 2
        and identities
    )
    return {
        "subfield_size": len(domain),
        "subfield_closed": closed and fixed,
        "b_outside_subfield": b_outside,
        "factor_base_size": len(points),
        "addition_identities": identities,
        "planted_ok": ok,
        "planted_point": planted_point,
    }


def distinct_sums(
    exponential: array.array, logarithm: array.array, points: list[tuple[int, int]]
) -> int:
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
                    if total is None:
                        continue
                    found.add((total[0] << DEGREE) | total[1])
    return len(found)


def census() -> dict:
    _require_prediction()
    exponential, logarithm = build_tables()
    domain = subfield(exponential, logarithm)
    points = factor_base(exponential, logarithm, domain)
    planted = planted_report(exponential, logarithm, domain, points)
    measured = None
    if planted["planted_ok"]:
        measured = distinct_sums(exponential, logarithm, points)
    within = (
        measured is not None
        and measured * 2 >= PREDICTED_COUNT
        and measured <= PREDICTED_COUNT * 2
    )
    beyond = measured is not None and (
        measured * 4 < PREDICTED_COUNT or measured > PREDICTED_COUNT * 4
    )
    return {
        "attack_claimed": False,
        "b": "z",
        "beyond_factor_4": beyond,
        "curve": "y^2 + x*y = x^3 + z",
        "denominator": FIELD_SIZE,
        "experiment_id": EXPERIMENT_ID,
        "measured_count": measured,
        "modulus": "z^25 + z^3 + 1",
        "p": 5,
        "planted": planted,
        "predicted_count": PREDICTED_COUNT,
        "run_id": RUN_ID,
        "within_factor_2": within,
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
        f"    factor_base_size: {planted['factor_base_size']}\n"
        f"    measured_count: {result['measured_count']}\n"
        f"    predicted_count: {result['predicted_count']}\n"
        f"    within_factor_2: {str(result['within_factor_2']).lower()}\n"
        f"    beyond_factor_4: {str(result['beyond_factor_4']).lower()}\n",
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
