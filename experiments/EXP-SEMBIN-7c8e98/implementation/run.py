#!/usr/bin/env python3
"""Stage-0 refutation-degree certificate for EXP-SEMBIN-7c8e98.

One chained summation system over F_32. The degree 4 is the idea's
reading. No batch and no Groebner basis are run.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

EXPERIMENT_ID = "EXP-SEMBIN-7c8e98"
RUN_ID = "RUN-SEMBIN-9ecb77"
N_FIELD = 5
K_DIM = 2
N_VARS = N_FIELD + 3 * K_DIM
DEGREE_CAP = 4
BOUND = 4
MODULUS = (1 << 5) | (1 << 2) | 1  # z^5 + z^2 + 1
COLUMN_COUNT = 562


def popcount(value: int) -> int:
    return bin(value).count("1")


def binomial(n: int, k: int) -> int:
    value = 1
    for i in range(k):
        value = value * (n - i) // (i + 1)
    return value


def field_mul(left: int, right: int) -> int:
    result = 0
    while right:
        if right & 1:
            result ^= left
        right >>= 1
        left <<= 1
        if left & (1 << N_FIELD):
            left ^= MODULUS
    return result


def field_ok() -> bool:
    value = 2
    for _ in range(4):
        value = field_mul(value, 2)
    # z^5 = z^2 + 1, and the polynomial has no root in F_2.
    return value == 5 and (1 ^ 1 ^ 1) != 0


def sym_add(left: dict, right: dict) -> dict:
    out = dict(left)
    for mask, coef in right.items():
        value = out.get(mask, 0) ^ coef
        if value:
            out[mask] = value
        elif mask in out:
            del out[mask]
    return out


def sym_mul(left: dict, right: dict) -> dict:
    out: dict = {}
    for left_mask, left_coef in left.items():
        for right_mask, right_coef in right.items():
            mask = left_mask | right_mask
            value = out.get(mask, 0) ^ field_mul(left_coef, right_coef)
            if value:
                out[mask] = value
            elif mask in out:
                del out[mask]
    return out


def sym_const(coef: int) -> dict:
    return {0: coef} if coef else {}


def element(start: int, width: int) -> dict:
    out = {}
    coef = 1
    for offset in range(width):
        out[1 << (start + offset)] = coef
        coef = field_mul(coef, 2)
    return out


def summation(x_var, y_var, z_var) -> dict:
    pair_xy = sym_mul(x_var, y_var)
    pair_xz = sym_mul(x_var, z_var)
    pair_yz = sym_mul(y_var, z_var)
    quad = sym_add(sym_add(pair_xy, pair_xz), pair_yz)
    # In the Boolean ring each squarefree monomial squares to itself.
    squared = sym_mul(quad, quad)
    cubic = sym_mul(pair_xy, z_var)
    return sym_add(sym_add(squared, cubic), sym_const(1))


def coordinates(symbolic: dict) -> list:
    equations = [set() for _ in range(N_FIELD)]
    for mask, coef in symbolic.items():
        for bit in range(N_FIELD):
            if (coef >> bit) & 1:
                if mask in equations[bit]:
                    equations[bit].remove(mask)
                else:
                    equations[bit].add(mask)
    return [equation for equation in equations if equation]


def build_system(target: int) -> list:
    auxiliary = element(0, N_FIELD)
    x1 = element(N_FIELD, K_DIM)
    x2 = element(N_FIELD + K_DIM, K_DIM)
    x3 = element(N_FIELD + 2 * K_DIM, K_DIM)
    first = summation(auxiliary, x1, x2)
    second = summation(auxiliary, x3, sym_const(target))
    return coordinates(first) + coordinates(second)


def satisfies(equations: list, assignment: int) -> bool:
    for equation in equations:
        total = 0
        for mask in equation:
            if mask & ~assignment == 0:
                total ^= 1
        if total:
            return False
    return True


def solution_count(equations: list) -> int:
    return sum(1 for assignment in range(1 << N_VARS) if satisfies(equations, assignment))


def monomials(degree: int) -> list:
    return [mask for mask in range(1 << N_VARS) if popcount(mask) <= degree]


def highest_allowed(row: int, allowed: set) -> int | None:
    current = row
    while current:
        column = current.bit_length() - 1
        if column in allowed:
            return column
        current ^= 1 << column
    return None


def insert_row(pivots: dict, row: int, allowed: set) -> None:
    current = row
    while True:
        column = highest_allowed(current, allowed)
        if column is None:
            return
        pivot = pivots.get(column)
        if pivot is None:
            for other, pivot_row in list(pivots.items()):
                if (pivot_row >> column) & 1:
                    pivots[other] = pivot_row ^ current
            pivots[column] = current
            return
        current ^= pivot


def in_span(target: int, pivots: dict, allowed: set) -> bool:
    current = target
    while True:
        column = highest_allowed(current, allowed)
        if column is None:
            return True
        pivot = pivots.get(column)
        if pivot is None:
            return False
        current ^= pivot


def mul_var(masks: set, variable: int) -> set:
    bit = 1 << variable
    out: set = set()
    for mask in masks:
        product = mask | bit
        if product in out:
            out.remove(product)
        else:
            out.add(product)
    return out


def contains_one(equations: list, degree: int) -> bool:
    space = monomials(degree)
    index = {mask: position for position, mask in enumerate(space)}
    allowed = set(range(len(space)))
    pivots: dict = {}
    queue: list = []

    def add_masks(masks: set) -> None:
        truncated = {mask for mask in masks if popcount(mask) <= degree}
        if not truncated:
            return
        row = 0
        for mask in truncated:
            row |= 1 << index[mask]
        if in_span(row, pivots, allowed):
            return
        insert_row(pivots, row, allowed)
        queue.append(truncated)

    for equation in equations:
        add_masks(set(equation))
    while queue:
        masks = queue.pop()
        generator_degree = max(popcount(mask) for mask in masks)
        if generator_degree + 1 > degree:
            continue
        for variable in range(N_VARS):
            add_masks(mul_var(masks, variable))
    return in_span(1 << index[0], pivots, allowed)


def refutation_degree(equations: list) -> int:
    for degree in range(1, DEGREE_CAP + 1):
        if contains_one(equations, degree):
            return degree
    return BOUND + 1


def first_unsat():
    for target in range(1, 1 << N_FIELD):
        equations = build_system(target)
        if solution_count(equations) == 0:
            return target, equations
    return None, None


def census() -> dict:
    columns = sum(binomial(N_VARS, degree) for degree in range(DEGREE_CAP + 1))
    target, equations = first_unsat()
    counted = None if equations is None else solution_count(equations)
    degree = None if equations is None else refutation_degree(equations)
    unit_ok = contains_one([{0}], 1)
    linear_ok = not contains_one([{1}], DEGREE_CAP)
    null_ok = not contains_one([], DEGREE_CAP)
    sound_ok = degree is None or degree > DEGREE_CAP or counted == 0
    planted_ok = bool(
        field_ok()
        and columns == COLUMN_COUNT
        and N_VARS == 11
        and target is not None
        and counted == 0
        and unit_ok
        and linear_ok
        and null_ok
        and sound_ok
    )
    matrix_holds = planted_ok and degree == BOUND
    return {
        "attack_claimed": False,
        "beyond_matrix": planted_ok and not matrix_holds,
        "bound": BOUND,
        "column_count": columns,
        "degree_cap": DEGREE_CAP,
        "experiment_id": EXPERIMENT_ID,
        "k_dim": K_DIM,
        "matrix_holds": matrix_holds,
        "modulus": MODULUS,
        "n_field": N_FIELD,
        "n_variables": N_VARS,
        "planted_ok": planted_ok,
        "refutation_degree": degree,
        "run_id": RUN_ID,
        "selected_target": target,
        "solution_count": counted,
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
