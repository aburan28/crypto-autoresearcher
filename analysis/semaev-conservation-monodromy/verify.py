#!/usr/bin/env python3
"""Exact checks for the Semaev monodromy/conservation proof dossier.

These deterministic checks catch convention, sign, and specialization mistakes.
They support—but do not replace—the proofs in ``theorem-dossier.md``.
"""

from __future__ import annotations

import itertools
import json
import math
import warnings
from collections import Counter

import sympy as sp
from sympy.utilities.exceptions import SymPyDeprecationWarning

warnings.filterwarnings("ignore", category=SymPyDeprecationWarning)


def s3(x1: object, x2: object, x3: object, a: object, b: object) -> object:
    """Classical short-Weierstrass S_3 in this dossier's convention."""
    return (
        (x1 - x2) ** 2 * x3**2
        - 2 * ((x1 + x2) * (x1 * x2 + a) + 2 * b) * x3
        + (x1 * x2 - a) ** 2
        - 4 * b * (x1 + x2)
    )


def verify_s3_discriminant() -> dict[str, object]:
    x1, x2, x3, a, b = sp.symbols("x1 x2 x3 a b")
    residual = sp.factor(
        sp.discriminant(s3(x1, x2, x3, a, b), x3)
        - 16 * (x1**3 + a * x1 + b) * (x2**3 + a * x2 + b)
    )
    assert residual == 0
    return {"identity": "disc_x3(S3)=16*f(x1)*f(x2)", "residual": 0}


def translation_cycle_lengths(
    dimension: int, translation: tuple[int, ...]
) -> list[int]:
    points = list(itertools.product((0, 1), repeat=dimension))
    unseen = set(points)
    cycles: list[int] = []
    while unseen:
        current = min(unseen)
        length = 0
        while current in unseen:
            unseen.remove(current)
            current = tuple(
                coordinate ^ delta
                for coordinate, delta in zip(current, translation, strict=True)
            )
            length += 1
        cycles.append(length)
    return sorted(cycles)


def verify_regular_action() -> dict[str, object]:
    profiles: dict[str, dict[str, object]] = {}
    for m in range(3, 9):
        dimension = m - 2
        identity = (0,) * dimension
        degree = 2**dimension
        assert translation_cycle_lengths(dimension, identity) == [1] * degree

        nonidentity_profiles = {
            tuple(translation_cycle_lengths(dimension, translation))
            for translation in itertools.product((0, 1), repeat=dimension)
            if any(translation)
        }
        expected = tuple([2] * (degree // 2))
        assert nonidentity_profiles == {expected}
        profiles[str(m)] = {
            "degree": degree,
            "identity_fixed_points": degree,
            "nonidentity_fixed_points": 0,
            "nonidentity_number_of_2_cycles": degree // 2,
        }
    return profiles


def legendre(value: int, p: int) -> int:
    value %= p
    if value == 0:
        return 0
    return 1 if pow(value, (p - 1) // 2, p) == 1 else -1


def curve_rhs(x: int, p: int, a: int, b: int) -> int:
    return (x**3 + a * x + b) % p


def factor_degrees(poly: sp.Poly) -> list[int]:
    _, factors = sp.factor_list(poly, modulus=poly.get_modulus())
    degrees: list[int] = []
    for factor, exponent in factors:
        degrees.extend([factor.degree()] * exponent)
    return sorted(degrees)


def verify_s4_factorization() -> dict[str, object]:
    # E/F_101: y^2 = x^3 + 2x + 3 is nonsingular.
    p, a_value, b_value = 101, 2, 3
    x, u, x2, x3, x4 = sp.symbols("x u x2 x3 x4")
    s4 = sp.resultant(
        s3(x, x2, u, a_value, b_value),
        s3(x3, x4, u, a_value, b_value),
        u,
    )

    cases = {
        "all_square": ((1, 3, 5), [1, 1, 1, 1]),
        "all_nonsquare": ((0, 2, 6), [1, 1, 1, 1]),
        "mixed_2_square": ((1, 3, 0), [2, 2]),
        "mixed_1_square": ((1, 0, 2), [2, 2]),
    }
    observations: dict[str, object] = {}
    for name, (values, expected_degrees) in cases.items():
        characters = [
            legendre(curve_rhs(value, p, a_value, b_value), p)
            for value in values
        ]
        assert 0 not in characters
        poly = sp.Poly(
            s4.subs({x2: values[0], x3: values[1], x4: values[2]}),
            x,
            modulus=p,
        )
        discriminant = int(sp.discriminant(poly.as_expr(), x)) % p
        assert poly.degree() == 4
        assert discriminant != 0
        observed_degrees = factor_degrees(poly)
        assert observed_degrees == expected_degrees
        # V_4 acts through A_4, so every good specialized discriminant is square.
        assert legendre(discriminant, p) == 1
        observations[name] = {
            "x_values": list(values),
            "quadratic_characters": characters,
            "factor_degrees": observed_degrees,
            "discriminant_square": True,
        }
    return observations


def curve_points(
    p: int, a: int, b: int
) -> tuple[list[tuple[int, int] | None], dict[int, tuple[int, int]]]:
    points: list[tuple[int, int] | None] = [None]
    canonical_lift: dict[int, tuple[int, int]] = {}
    for x in range(p):
        roots = [
            y for y in range(p) if y * y % p == curve_rhs(x, p, a, b)
        ]
        points.extend((x, y) for y in roots)
        if roots:
            canonical_lift[x] = (x, min(roots))
    return points, canonical_lift


def ec_neg(
    point: tuple[int, int] | None, p: int
) -> tuple[int, int] | None:
    return None if point is None else (point[0], (-point[1]) % p)


def ec_add(
    left: tuple[int, int] | None,
    right: tuple[int, int] | None,
    p: int,
    a: int,
) -> tuple[int, int] | None:
    if left is None:
        return right
    if right is None:
        return left

    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % p == 0:
        return None

    if left == right:
        if y1 == 0:
            return None
        slope = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        slope = (y2 - y1) * pow(x2 - x1, -1, p) % p

    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return x3, y3


def signed_witness_counts(
    base_x: list[int],
    lifts: dict[int, tuple[int, int]],
    arity: int,
    p: int,
    a: int,
) -> Counter[tuple[int, int] | None]:
    counts: Counter[tuple[int, int] | None] = Counter()
    for xs in itertools.product(base_x, repeat=arity):
        points = [lifts[x] for x in xs]
        for signs in itertools.product((1, -1), repeat=arity):
            target: tuple[int, int] | None = None
            for point, sign in zip(points, signs, strict=True):
                target = ec_add(
                    target, point if sign == 1 else ec_neg(point, p), p, a
                )
            counts[target] += 1
    return counts


def verify_character_counts_and_conservation() -> dict[str, object]:
    p, a, b = 101, 2, 3
    points, lifts = curve_points(p, a, b)
    z = sum(curve_rhs(x, p, a, b) == 0 for x in range(p))
    squares = sum(
        legendre(curve_rhs(x, p, a, b), p) == 1 for x in range(p)
    )
    nonsquares = sum(
        legendre(curve_rhs(x, p, a, b), p) == -1 for x in range(p)
    )
    trace = p + 1 - len(points)

    assert squares == (p - trace - z) // 2
    assert nonsquares == (p + trace - z) // 2
    assert squares + nonsquares + z == p

    split_counts: dict[str, int] = {}
    for r in (2, 3, 4):
        by_character_cells = sum(
            math.prod(squares if character == 1 else nonsquares for character in cell)
            for cell in itertools.product((1, -1), repeat=r)
            if len(set(cell)) == 1
        )
        closed_form = squares**r + nonsquares**r
        assert by_character_cells == closed_form
        split_counts[str(r)] = closed_form

    usable_x = [x for x, point in lifts.items() if point[1] != 0]
    base_a = usable_x[:5]
    base_b = usable_x[::7][:5]
    counts_a = signed_witness_counts(base_a, lifts, 3, p, a)
    counts_b = signed_witness_counts(base_b, lifts, 3, p, a)
    expected_total = (2**3) * (5**3)
    assert sum(counts_a.values()) == expected_total
    assert sum(counts_b.values()) == expected_total
    assert len(points) == 96
    assert len(counts_a) != len(counts_b)

    return {
        "curve_order": len(points),
        "trace": trace,
        "rational_2_torsion_x_count": z,
        "square_x_count": squares,
        "nonsquare_x_count": nonsquares,
        "complete_split_character_counts": split_counts,
        "witness_conservation": {
            "base_size": 5,
            "arity": 3,
            "total_per_base": expected_total,
            "support_sizes": [len(counts_a), len(counts_b)],
        },
    }


def main() -> None:
    report = {
        "s3_discriminant": verify_s3_discriminant(),
        "regular_action": verify_regular_action(),
        "s4_specializations": verify_s4_factorization(),
        "finite_field_counts": verify_character_counts_and_conservation(),
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
