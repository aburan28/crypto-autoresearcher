#!/usr/bin/env python3
"""Stage-0 chain-versus-sum identity for EXP-OAKLEY-2c0552.

Compares a two-factor Semaev chain with a four-point sum. Zero disagreements
and any positive disagreement count are the frozen readings. They are not fitted.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

EXPERIMENT_ID = "EXP-OAKLEY-2c0552"
RUN_ID = "RUN-OAKLEY-a451a8"
PRIME = 17
A = 1
B = 1


def legendre(value: int) -> int:
    return pow(value % PRIME, (PRIME - 1) // 2, PRIME)


def summation_s3(x1: int, x2: int, x3: int) -> int:
    difference = (x1 - x2) % PRIME
    first = difference * difference % PRIME * (x3 * x3 % PRIME) % PRIME
    middle = ((x1 + x2) * ((x1 * x2 + A) % PRIME) + 2 * B) % PRIME
    second = 2 * middle % PRIME * x3 % PRIME
    third = pow((x1 * x2 - A) % PRIME, 2, PRIME)
    fourth = 4 * B % PRIME * ((x1 + x2) % PRIME) % PRIME
    return (first - second + third - fourth) % PRIME


def square_root(value: int) -> int | None:
    residue = value % PRIME
    if legendre(residue) == PRIME - 1:
        return None
    for candidate in range(PRIME):
        if candidate * candidate % PRIME == residue:
            return candidate
    return None


def curve_rhs(x_coord: int) -> int:
    return (x_coord * x_coord * x_coord + A * x_coord + B) % PRIME


def least_point(x_coord: int) -> tuple[int, int] | None:
    y_coord = square_root(curve_rhs(x_coord))
    if y_coord is None:
        return None
    return x_coord, y_coord


def add_points(left, right):
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % PRIME == 0:
        return None
    if left == right:
        if y1 == 0:
            return None
        slope = ((3 * x1 * x1 + A) * pow(2 * y1, PRIME - 2, PRIME)) % PRIME
    else:
        slope = ((y2 - y1) * pow((x2 - x1) % PRIME, PRIME - 2, PRIME)) % PRIME
    x3 = (slope * slope - x1 - x2) % PRIME
    y3 = (slope * (x1 - x3) - y1) % PRIME
    return x3, y3


def direct_sums_to_infinity(xs: tuple[int, int, int, int], points: dict[int, tuple[int, int]]) -> bool:
    chosen = []
    for x_coord in xs:
        point = points.get(x_coord)
        if point is None:
            return False
        chosen.append(point)
    for mask in range(16):
        total = None
        for index, point in enumerate(chosen):
            if (mask >> index) & 1:
                signed = point
            else:
                signed = (point[0], (-point[1]) % PRIME)
            total = signed if total is None else add_points(total, signed)
        if total is None:
            return True
    return False


def chain_sums_to_infinity(xs: tuple[int, int, int, int], points: dict[int, tuple[int, int]]) -> bool:
    if any(x_coord not in points for x_coord in xs):
        return False
    if xs[0] == xs[1] and xs[2] == xs[3]:
        return True
    x1, x2, x3, x4 = xs
    for auxiliary in range(PRIME):
        if summation_s3(x1, x2, auxiliary) == 0 and summation_s3(auxiliary, x3, x4) == 0:
            return True
    return False


def planted_pair(points: dict[int, tuple[int, int]]) -> dict | None:
    xs = sorted(points)
    for index, x1 in enumerate(xs):
        for x2 in xs[index + 1 :]:
            total = add_points(points[x1], points[x2])
            if total is None:
                continue
            value = summation_s3(x1, x2, total[0])
            return {"x1": x1, "x2": x2, "x_sum": total[0], "s3": value}
    return None


def census() -> dict:
    points = {}
    for x_coord in range(PRIME):
        point = least_point(x_coord)
        if point is not None:
            points[x_coord] = point
    planted = planted_pair(points)
    planted_ok = planted is not None and planted["s3"] == 0 and len(points) >= 2
    disagreements = None
    if planted_ok:
        disagreements = 0
        for x1 in range(PRIME):
            for x2 in range(PRIME):
                for x3 in range(PRIME):
                    for x4 in range(PRIME):
                        xs = (x1, x2, x3, x4)
                        geometric = direct_sums_to_infinity(xs, points)
                        algebraic = chain_sums_to_infinity(xs, points)
                        if geometric != algebraic:
                            disagreements += 1
    return {
        "attack_claimed": False,
        "curve": "y^2 = x^3 + x + 1",
        "disagreement_count": disagreements,
        "experiment_id": EXPERIMENT_ID,
        "ordered_quadruples": PRIME ** 4,
        "planted": planted,
        "planted_ok": planted_ok,
        "points_on_curve": len(points),
        "prime": PRIME,
        "run_id": RUN_ID,
    }


def write_outputs(run_dir: Path, result: dict) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "raw-result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (run_dir / "manifest.yaml").write_text(
        "run:\n"
        f"  experiment_id: {EXPERIMENT_ID}\n"
        f"  run_id: {RUN_ID}\n"
        "  attack_claimed: false\n"
        "  metrics:\n"
        f"    planted_ok: {str(result['planted_ok']).lower()}\n"
        f"    disagreement_count: {result['disagreement_count']}\n"
        f"    ordered_quadruples: {result['ordered_quadruples']}\n",
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
