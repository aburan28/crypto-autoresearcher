#!/usr/bin/env python3
"""Stage-0 instrument for EXP-ECDLP-f34097.

One preregistered cell over F_31. Writes observations only.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

P = 31
PLANTED = (2, 0, 3, 0)  # x0, x1, y0, y1
ORACLE_V_MAX = 8
A_COEFF = 1
B_COEFF = 30


def inv(value: int) -> int:
    return pow(value % P, P - 2, P)


def add(point, other, a_coeff: int = A_COEFF):
    if point is None:
        return other
    if other is None:
        return point
    x1, y1 = point
    x2, y2 = other
    if x1 == x2 and (y1 + y2) % P == 0:
        return None
    if point == other:
        if y1 % P == 0:
            return None
        slope = (3 * x1 * x1 + a_coeff) * inv(2 * y1) % P
    else:
        slope = (y2 - y1) * inv(x2 - x1) % P
    x3 = (slope * slope - x1 - x2) % P
    y3 = (slope * (x1 - x3) - y1) % P
    return (x3, y3)


def mul(scalar: int, point):
    result = None
    addend = point
    k = scalar
    while k:
        if k & 1:
            result = add(result, addend)
        addend = add(addend, addend)
        k >>= 1
    return result


def on_fibre(x_coord: int, y_coord: int) -> bool:
    return (y_coord * y_coord - x_coord ** 3 - A_COEFF * x_coord - B_COEFF) % P == 0


def section_identity(x1: int, y1: int) -> bool:
    """True when the degree-at-most-1 section lies on the constant surface.

    The residual in t has degree at most 3, so four sample points decide it.
    """
    for t_value in range(4):
        x_coord = (PLANTED[0] + x1 * t_value) % P
        y_coord = (PLANTED[2] + y1 * t_value) % P
        residual = (
            y_coord * y_coord - x_coord ** 3 - A_COEFF * x_coord - B_COEFF
        ) % P
        if residual != 0:
            return False
    return True


def oracle() -> dict:
    generator = (PLANTED[0], PLANTED[2])
    target = generator
    found = None
    for scalar in range(1, ORACLE_V_MAX + 1):
        if mul(scalar, generator) == target:
            found = scalar
            break
    return {
        "oracle_recovered": found == 1 and mul(1, generator) == target,
        "oracle_multiplier": found,
        "generator": list(generator),
        "target": list(target),
    }


def structured_search() -> dict:
    started = time.perf_counter()
    solutions = [
        [x1, y1]
        for x1 in range(P)
        for y1 in range(P)
        if section_identity(x1, y1)
    ]
    elapsed = time.perf_counter() - started
    return {
        "variable_count": 2,
        "structured_solution_count": len(solutions),
        "structured_contains_planted": [0, 0] in solutions,
        "structured_seconds": elapsed,
        "solutions_truncated": solutions[:8],
    }


def random_control() -> dict:
    """Preregistered system u + 2v = 14, u - v = -1 over F_31."""
    started = time.perf_counter()
    solutions = []
    for u_val in range(P):
        for v_val in range(P):
            if (u_val + 2 * v_val - 14) % P == 0 and (u_val - v_val + 1) % P == 0:
                solutions.append([u_val, v_val])
    elapsed = time.perf_counter() - started
    return {
        "variable_count": 2,
        "random_solution_count": len(solutions),
        "random_contains_planted": [4, 5] in solutions,
        "random_seconds": elapsed,
        "solutions": solutions,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=int, required=True)
    parser.add_argument("--trial-plan", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    if args.stage != 0:
        raise SystemExit("version 1 runs stage 0 only")
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    planted_on_curve = on_fibre(PLANTED[0], PLANTED[2])
    identity_at_planted = section_identity(0, 0)
    oracle_row = oracle()
    structured = structured_search()
    control = random_control()
    payload = {
        "schema": "crypto.autoresearch.exp-ecdlp-f34097.stage0.v1",
        "experiment_id": "EXP-ECDLP-f34097",
        "hypothesis_id": "H-ECDLP-af796a",
        "stage": 0,
        "p": P,
        "degree_bound": 1,
        "t0": 0,
        "planted_section": list(PLANTED),
        "planted_on_curve": planted_on_curve,
        "identity_at_planted": identity_at_planted,
        **oracle_row,
        **structured,
        **control,
        "claim_boundary": (
            "observation of one toy cell; not a section-cost exponent "
            "and not a statement about any deployed curve"
        ),
    }
    (run_dir / "raw-result.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    manifest = "\n".join(
        [
            "run:",
            "  id: RUN-ECDLP-62ec3d",
            "  experiment_id: EXP-ECDLP-f34097",
            "  status: observation",
            "  stage: 0",
            f"  oracle_recovered: {str(payload['oracle_recovered']).lower()}",
            f"  oracle_multiplier: {payload['oracle_multiplier']}",
            f"  structured_contains_planted: {str(payload['structured_contains_planted']).lower()}",
            f"  structured_solution_count: {payload['structured_solution_count']}",
            f"  random_contains_planted: {str(payload['random_contains_planted']).lower()}",
            f"  random_solution_count: {payload['random_solution_count']}",
            "",
        ]
    )
    (run_dir / "manifest.yaml").write_text(manifest, encoding="utf-8")
    results = "\n".join(
        [
            "# EXP-ECDLP-f34097 stage 0 observations",
            "",
            "This file records the cell. It does not decide the section-cost claim.",
            "",
            f"- p = {P}, degree bound = 1, planted section = {list(PLANTED)}",
            f"- planted point on the fibre: {planted_on_curve}",
            f"- identity at (x1, y1) = (0, 0): {identity_at_planted}",
            f"- oracle_recovered: {payload['oracle_recovered']}",
            f"- oracle_multiplier: {payload['oracle_multiplier']}",
            f"- structured_solution_count: {payload['structured_solution_count']}",
            f"- structured_contains_planted: {payload['structured_contains_planted']}",
            f"- random_solution_count: {payload['random_solution_count']}",
            f"- random_contains_planted: {payload['random_contains_planted']}",
            f"- structured_seconds: {payload['structured_seconds']}",
            f"- random_seconds: {payload['random_seconds']}",
            "",
        ]
    )
    (run_dir / "RESULTS.md").write_text(results, encoding="utf-8")


if __name__ == "__main__":
    main()
