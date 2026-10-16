#!/usr/bin/env python3
"""Stage-0 instrument for EXP-ECDLP-903c48.

One preregistered rank-1 net cell over F_11. Writes observations only.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

P = 11
A_COEFF = 0
B_COEFF = 2
POINT = (1, 5)
WINDOW_END = 24


def inv(value: int) -> int:
    return pow(value % P, P - 2, P)


def add(point, other):
    if point is None:
        return other
    if other is None:
        return point
    x1, y1 = point
    x2, y2 = other
    if x1 == x2 and (y1 + y2) % P == 0:
        return None
    if point == other:
        slope = (3 * x1 * x1 + A_COEFF) * inv(2 * y1) % P
    else:
        slope = (y2 - y1) * inv(x2 - x1) % P
    x3 = (slope * slope - x1 - x2) % P
    y3 = (slope * (x1 - x3) - y1) % P
    return (x3, y3)


def on_curve(point) -> bool:
    x_coord, y_coord = point
    return (y_coord * y_coord) % P == (x_coord ** 3 + A_COEFF * x_coord + B_COEFF) % P


def group_law_order(point) -> int:
    current = point
    step = 1
    while current is not None:
        current = add(current, point)
        step += 1
        if step > WINDOW_END + 2:
            raise RuntimeError("order search exceeded the preregistered window")
    return step


def net_values(point) -> dict[int, int]:
    x_coord, y_coord = point
    values = {
        0: 0,
        1: 1,
        2: (2 * y_coord) % P,
        3: (3 * x_coord ** 4 + 6 * A_COEFF * x_coord * x_coord + 12 * B_COEFF * x_coord - A_COEFF * A_COEFF) % P,
    }
    values[4] = (
        4
        * y_coord
        * (
            x_coord ** 6
            + 5 * A_COEFF * x_coord ** 4
            + 20 * B_COEFF * x_coord ** 3
            - 5 * A_COEFF * A_COEFF * x_coord * x_coord
            - 4 * A_COEFF * B_COEFF * x_coord
            - 8 * B_COEFF * B_COEFF
            - A_COEFF ** 3
        )
    ) % P
    if values[2] == 0:
        raise RuntimeError("W(2) = 0; this cell excludes 2-torsion")
    inv_w2 = inv(values[2])
    index = 2
    while 2 * index <= WINDOW_END or 2 * index + 1 <= WINDOW_END:
        if 2 * index + 1 <= WINDOW_END:
            values[2 * index + 1] = (
                values[index + 2] * pow(values[index], 3, P)
                - values[index - 1] * pow(values[index + 1], 3, P)
            ) % P
        if 2 * index <= WINDOW_END:
            bracket = (
                values[index + 2] * pow(values[index - 1], 2, P)
                - values[index - 2] * pow(values[index + 1], 2, P)
            ) % P
            values[2 * index] = (values[index] * inv_w2 * bracket) % P
        index += 1
    return values


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=int, required=True)
    parser.add_argument("--trial-plan", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    if args.stage != 0:
        raise SystemExit("this runner implements stage 0 only")
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    curve_ok = on_curve(POINT)
    order = group_law_order(POINT)
    values = net_values(POINT)
    zeros = [n for n in range(1, WINDOW_END + 1) if values[n] == 0]
    expected = [n for n in range(1, WINDOW_END + 1) if order != 0 and n % order == 0]
    first = zeros[0] if zeros else None
    elapsed = time.perf_counter() - started
    payload = {
        "schema": "crypto.autoresearch.exp-ecdlp-903c48.stage0.v1",
        "experiment_id": "EXP-ECDLP-903c48",
        "hypothesis_id": "H-ECDLP-753879",
        "stage": 0,
        "p": P,
        "a": A_COEFF,
        "b": B_COEFF,
        "point": list(POINT),
        "window_end": WINDOW_END,
        "on_curve": curve_ok,
        "group_law_order": order,
        "first_positive_zero": first,
        "zeros": zeros,
        "zeros_match_order_multiples": zeros == expected,
        "w1": values[1],
        "w2": values[2],
        "w3": values[3],
        "w4": values[4],
        "w6": values[6],
        "w12": values[12],
        "elapsed_seconds": elapsed,
        "claim_boundary": (
            "observation of one rank-1 toy cell; not a mutual-information "
            "estimate and not a statement about any deployed curve"
        ),
    }
    (run_dir / "raw-result.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    manifest = "\n".join(
        [
            "run:",
            "  id: RUN-ECDLP-4616a2",
            "  experiment_id: EXP-ECDLP-903c48",
            "  status: observation",
            "  stage: 0",
            f"  on_curve: {str(payload['on_curve']).lower()}",
            f"  group_law_order: {payload['group_law_order']}",
            f"  first_positive_zero: {payload['first_positive_zero']}",
            f"  zeros_match_order_multiples: {str(payload['zeros_match_order_multiples']).lower()}",
            "",
        ]
    )
    (run_dir / "manifest.yaml").write_text(manifest, encoding="utf-8")
    results = "\n".join(
        [
            "# EXP-ECDLP-903c48 stage 0 observations",
            "",
            "This file records the cell. It does not decide the mutual-information claim.",
            "",
            f"- p = {P}, curve y^2 = x^3 + {B_COEFF}, point = {list(POINT)}",
            f"- on_curve: {payload['on_curve']}",
            f"- group_law_order: {payload['group_law_order']}",
            f"- first_positive_zero: {payload['first_positive_zero']}",
            f"- zeros: {payload['zeros']}",
            f"- zeros_match_order_multiples: {payload['zeros_match_order_multiples']}",
            f"- w1, w2, w12: {payload['w1']}, {payload['w2']}, {payload['w12']}",
            f"- elapsed_seconds: {payload['elapsed_seconds']}",
            "",
        ]
    )
    (run_dir / "RESULTS.md").write_text(results, encoding="utf-8")


if __name__ == "__main__":
    main()
