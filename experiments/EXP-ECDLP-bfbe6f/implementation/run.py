#!/usr/bin/env python3
"""Stage-0 Semaev S_3 worksheet for EXP-ECDLP-bfbe6f.

Twelve evaluations on y^2 = x^3 + x + 2 over F_41. Not a discrete logarithm.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


P = 41
A = 1
B = 2
EXPERIMENT_ID = "EXP-ECDLP-bfbe6f"
RUN_ID = "RUN-ECDLP-8f5190"
POINTS = ((0, 17), (1, 2), (3, 14), (5, 3))
PAIRS = ((0, 1), (0, 3), (0, 5), (1, 3), (1, 5), (3, 5))
EXPECTED_AT_SEVEN = (13, 33, 35, 11, 28, 38)
THIRD = 7


def s3_reduced(x1: int, x2: int, x3: int) -> int:
    """KN-TECH-002 formula, reduced after every field operation."""
    diff = (x1 - x2) % P
    square = (diff * diff) % P
    leading = (square * ((x3 * x3) % P)) % P
    total = (x1 + x2) % P
    product = (x1 * x2) % P
    inner = (total * ((product + A) % P)) % P
    inner = (inner + (2 * B) % P) % P
    linear = ((2 * inner) % P * x3) % P
    gap = (product - A) % P
    constant = ((gap * gap) % P - ((4 * B) % P * total) % P) % P
    return (leading - linear + constant) % P


def s3_delayed(x1: int, x2: int, x3: int) -> int:
    """Same polynomial with one reduction per coefficient, then Horner."""
    leading = (x1 - x2) ** 2 % P
    linear = 2 * ((x1 + x2) * (x1 * x2 + A) + 2 * B) % P
    constant = ((x1 * x2 - A) ** 2 - 4 * B * (x1 + x2)) % P
    return (leading * x3 * x3 - linear * x3 + constant) % P


def inv(value: int) -> int:
    return pow(value % P, P - 2, P)


def ec_add(left: tuple[int, int] | None, right: tuple[int, int] | None) -> tuple[int, int] | None:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % P == 0:
        return None
    if left == right:
        slope = ((3 * x1 * x1 + A) % P * inv(2 * y1)) % P
    else:
        slope = ((y2 - y1) % P * inv((x2 - x1) % P)) % P
    x3 = (slope * slope - x1 - x2) % P
    y3 = (slope * (x1 - x3) - y1) % P
    return (x3, y3)


def on_curve_expanded(x_value: int, y_value: int) -> bool:
    rhs = (x_value * x_value * x_value + A * x_value + B) % P
    return (y_value * y_value) % P == rhs


def on_curve_horner(x_value: int, y_value: int) -> bool:
    rhs = ((x_value * x_value + A) % P * x_value + B) % P
    return (y_value * y_value) % P == rhs


def census() -> dict:
    by_x = {x_value: (x_value, y_value) for x_value, y_value in POINTS}
    points_on_curve = all(
        on_curve_expanded(x_value, y_value) and on_curve_horner(x_value, y_value)
        for x_value, y_value in POINTS
    )
    discriminant_nonzero = (4 * A * A * A + 27 * B * B) % P != 0
    sum_x: list[int] = []
    true_values: list[int] = []
    seven_values: list[int] = []
    affine = True
    agree = True
    for x1, x2 in PAIRS:
        total = ec_add(by_x[x1], by_x[x2])
        if total is None:
            affine = False
            break
        third = total[0]
        reduced_true = s3_reduced(x1, x2, third)
        delayed_true = s3_delayed(x1, x2, third)
        reduced_seven = s3_reduced(x1, x2, THIRD)
        delayed_seven = s3_delayed(x1, x2, THIRD)
        agree = agree and reduced_true == delayed_true and reduced_seven == delayed_seven
        sum_x.append(third)
        true_values.append(reduced_true)
        seven_values.append(reduced_seven)
    diagonal: list[int] = []
    for x_value, _y_value in POINTS:
        reduced = s3_reduced(x_value, x_value, THIRD)
        delayed = s3_delayed(x_value, x_value, THIRD)
        agree = agree and reduced == delayed
        diagonal.append(reduced)
    planted_ok = (
        points_on_curve
        and discriminant_nonzero
        and affine
        and agree
        and len(true_values) == 6
        and len(seven_values) == 6
        and len(diagonal) == 4
    )
    nonzero = sum(1 for value in true_values if value != 0)
    seven_match = tuple(seven_values) == EXPECTED_AT_SEVEN
    matrix_holds = planted_ok and nonzero == 0 and seven_match
    return {
        "attack_claimed": False,
        "experiment_id": EXPERIMENT_ID,
        "run_id": RUN_ID,
        "prime": P,
        "curve_a": A,
        "curve_b": B,
        "pairs": [list(pair) for pair in PAIRS],
        "sum_x": sum_x,
        "true_values": true_values,
        "seven_values": seven_values,
        "expected_at_seven": list(EXPECTED_AT_SEVEN),
        "diagonal_at_seven": diagonal,
        "success_consults_diagonal": False,
        "points_on_curve": points_on_curve,
        "discriminant_nonzero": discriminant_nonzero,
        "implementations_agree": agree,
        "sums_affine": affine,
        "true_sum_nonzero_count": nonzero,
        "planted_ok": planted_ok,
        "matrix_holds": matrix_holds,
        "beyond_matrix": planted_ok and not matrix_holds,
    }


def write_outputs(run_dir: Path, result: dict) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "raw-result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (run_dir / "manifest.yaml").write_text(
        "run:\n"
        f"  experiment_id: {EXPERIMENT_ID}\n"
        f"  run_id: {RUN_ID}\n"
        "  attack_claimed: false\n"
        "  metrics:\n"
        f"    planted_ok: {str(result['planted_ok']).lower()}\n"
        f"    matrix_holds: {str(result['matrix_holds']).lower()}\n"
        f"    beyond_matrix: {str(result['beyond_matrix']).lower()}\n",
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
