#!/usr/bin/env python3
"""Stage-0 labelled fall certificate for EXP-SEMBIN-22a1a2.

One summation polynomial over F_8, unshifted and shifted by 1.
The bound 4 is the idea's bound. No Groebner basis is computed.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

EXPERIMENT_ID = "EXP-SEMBIN-22a1a2"
RUN_ID = "RUN-SEMBIN-a818df"
N_FIELD = 3
N_VARS = 9
DEGREE_CAP = 4
BOUND = 4
MODULUS = 0b1011  # z^3 + z + 1

ZERO = tuple(0 for _ in range(N_VARS))


def poly_add(left: dict, right: dict) -> dict:
    out = dict(left)
    for monomial, coeff in right.items():
        value = out.get(monomial, 0) ^ coeff
        if value:
            out[monomial] = value
        elif monomial in out:
            del out[monomial]
    return out


def poly_mul(left: dict, right: dict) -> dict:
    out: dict = {}
    for left_monomial in left:
        for right_monomial in right:
            monomial = tuple(a + b for a, b in zip(left_monomial, right_monomial))
            out[monomial] = out.get(monomial, 0) ^ 1
    return {monomial: coeff for monomial, coeff in out.items() if coeff}


def const_one() -> dict:
    return {ZERO: 1}


def var_poly(index: int) -> dict:
    exponents = [0] * N_VARS
    exponents[index] = 1
    return {tuple(exponents): 1}


def poly_degree(poly: dict) -> int:
    if not poly:
        return -1
    return max(sum(monomial) for monomial in poly)


def bool_reduce(poly: dict) -> dict:
    out: dict = {}
    for monomial, coeff in poly.items():
        reduced = tuple(1 if exponent else 0 for exponent in monomial)
        out[reduced] = out.get(reduced, 0) ^ coeff
    return {monomial: coeff for monomial, coeff in out.items() if coeff}


def field_zero():
    return [{}, {}, {}]


def field_const(value: int):
    return [const_one() if (value >> bit) & 1 else {} for bit in range(3)]


def field_add(left, right):
    return [poly_add(left[i], right[i]) for i in range(3)]


def field_mul(left, right):
    parts = [dict() for _ in range(5)]
    for i in range(3):
        for j in range(3):
            parts[i + j] = poly_add(parts[i + j], poly_mul(left[i], right[j]))
    # z^3 = 1 + z and z^4 = z + z^2 for z^3 + z + 1.
    coord0 = poly_add(parts[0], parts[3])
    coord1 = poly_add(poly_add(parts[1], parts[3]), parts[4])
    coord2 = poly_add(parts[2], parts[4])
    return [coord0, coord1, coord2]


def point(index: int, shift: bool):
    coords = [var_poly(index * 3 + bit) for bit in range(3)]
    if shift and index == 0:
        coords[0] = poly_add(coords[0], const_one())
    return coords


def summation(shift: bool):
    """S_3(x1, x2, x3) = (x1 x2 + x1 x3 + x2 x3)^2 + x1 x2 x3 + 1."""
    x1 = point(0, shift)
    x2 = point(1, False)
    x3 = point(2, False)
    pair12 = field_mul(x1, x2)
    pair13 = field_mul(x1, x3)
    pair23 = field_mul(x2, x3)
    quad = field_add(field_add(pair12, pair13), pair23)
    squared = field_mul(quad, quad)
    cubic = field_mul(pair12, x3)
    total = field_add(field_add(squared, cubic), field_const(1))
    return total


def monomials_up_to(max_degree: int) -> list:
    found = []

    def walk(position: int, remaining: int, prefix: list) -> None:
        if position == N_VARS:
            if remaining == 0:
                found.append(tuple(prefix))
            return
        for exponent in range(remaining + 1):
            prefix.append(exponent)
            walk(position + 1, remaining - exponent, prefix)
            prefix.pop()

    for degree in range(max_degree + 1):
        walk(0, degree, [])
    return found


def binomial(n: int, k: int) -> int:
    value = 1
    for i in range(k):
        value = value * (n - i) // (i + 1)
    return value


def multiply_by(poly: dict, monomial: tuple) -> dict:
    out = {}
    for source, coeff in poly.items():
        shifted = tuple(a + b for a, b in zip(source, monomial))
        out[shifted] = out.get(shifted, 0) ^ coeff
    return {item: coeff for item, coeff in out.items() if coeff}


def to_bits(poly: dict, index: dict) -> int:
    row = 0
    for monomial, coeff in poly.items():
        if coeff:
            row |= 1 << index[monomial]
    return row


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


def rank_and_low(rows: list, degrees: list, degree: int) -> tuple[int, int]:
    allowed = {i for i, item in enumerate(degrees) if item <= degree}
    low_columns = {i for i, item in enumerate(degrees) if item < degree}
    pivots: dict = {}
    for row in rows:
        insert_row(pivots, row, allowed)
    low = sum(1 for column in pivots if column in low_columns)
    return len(pivots), low


def products(polys: list, monomials: list, degree: int, reduced: bool) -> list:
    rows = []
    for poly in polys:
        generator_degree = poly_degree(poly)
        if generator_degree < 0:
            continue
        for monomial in monomials:
            # Definition 5 keeps the formal bound. Definition 6 admits a row
            # once the product has degree at most D after X_i^2 -> X_i.
            if not reduced and sum(monomial) + generator_degree > degree:
                continue
            product = multiply_by(poly, monomial)
            if reduced:
                product = bool_reduce(product)
                if product and poly_degree(product) > degree:
                    continue
            if product:
                rows.append(product)
    return rows


def first_fall(polys: list, monomials: list, index: dict, degrees: list, reduced: bool) -> int:
    previous = 0
    for degree in range(1, DEGREE_CAP + 1):
        rows = []
        for product in products(polys, monomials, degree, reduced):
            if any(sum(monomial) > degree for monomial in product):
                raise RuntimeError("product escaped the degree cap")
            rows.append(to_bits(product, index))
        count, low = rank_and_low(rows, degrees, degree)
        if low - previous < 0:
            return -1
        if low - previous > 0:
            return degree
        previous = count
    return BOUND + 1


def macaulay_degree(polys: list, monomials: list, index: dict) -> int | None:
    for degree in range(1, DEGREE_CAP + 1):
        rows = []
        for product in products(polys, monomials, degree, False):
            rows.append(to_bits(product, index))
        if rows and rank_and_low(rows, [sum(item) for item in monomials], degree)[0] < len(rows):
            return degree
    return None


def reading(polys: list, monomials: list, index: dict, degrees: list) -> dict:
    mac = macaulay_degree(polys, monomials, index)
    return {
        "def5_true": first_fall(polys, monomials, index, degrees, False),
        "def6_fake": first_fall(polys, monomials, index, degrees, True),
        "macaulay_degree": mac,
        "macaulay_present": mac is not None,
    }


def same_polys(left, right) -> bool:
    return all(left[i] == right[i] for i in range(3))


def field_arithmetic_ok() -> bool:
    generator = field_const(0b010)
    squared = field_mul(generator, generator)
    cubed = field_mul(squared, generator)
    return cubed == field_const(0b011)


def constant_term_is_one(polys) -> bool:
    return (
        polys[0].get(ZERO, 0) == 1
        and polys[1].get(ZERO, 0) == 0
        and polys[2].get(ZERO, 0) == 0
    )


def square_cancels() -> bool:
    square = var_poly(0)
    doubled = multiply_by(square, tuple(1 if i == 0 else 0 for i in range(N_VARS)))
    total = poly_add(doubled, square)
    return poly_degree(total) == 2 and bool_reduce(total) == {}


def macaulay_diverges(unshifted: dict, shifted: dict) -> bool:
    if unshifted["macaulay_present"] != shifted["macaulay_present"]:
        return True
    if unshifted["macaulay_present"] and shifted["macaulay_present"]:
        return abs(unshifted["macaulay_degree"] - shifted["macaulay_degree"]) >= 1
    return False


def census() -> dict:
    monomials = monomials_up_to(DEGREE_CAP)
    index = {monomial: i for i, monomial in enumerate(monomials)}
    degrees = [sum(monomial) for monomial in monomials]
    unshifted_polys = summation(False)
    shifted_polys = summation(True)
    unshifted = reading(unshifted_polys, monomials, index, degrees)
    shifted = reading(shifted_polys, monomials, index, degrees)
    columns_ok = len(monomials) == binomial(N_VARS + DEGREE_CAP, DEGREE_CAP) == 715
    falls_ok = min(unshifted["def5_true"], unshifted["def6_fake"], shifted["def5_true"], shifted["def6_fake"]) >= 1
    planted_ok = bool(
        columns_ok
        and MODULUS == 0b1011
        and field_arithmetic_ok()
        and square_cancels()
        and constant_term_is_one(unshifted_polys)
        and constant_term_is_one(shifted_polys)
        and not same_polys(unshifted_polys, shifted_polys)
        and not macaulay_diverges(unshifted, unshifted)
        and falls_ok
    )
    fake_kept = shifted["def6_fake"] <= BOUND
    true_exceeds = shifted["def5_true"] > BOUND
    matrix_holds = planted_ok and fake_kept and (true_exceeds or macaulay_diverges(unshifted, shifted))
    return {
        "attack_claimed": False,
        "beyond_matrix": planted_ok and not matrix_holds,
        "bound": BOUND,
        "column_count": len(monomials),
        "degree_cap": DEGREE_CAP,
        "experiment_id": EXPERIMENT_ID,
        "matrix_holds": matrix_holds,
        "modulus": MODULUS,
        "n_field": N_FIELD,
        "n_variables": N_VARS,
        "planted_ok": planted_ok,
        "run_id": RUN_ID,
        "shifted": shifted,
        "unshifted": unshifted,
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
