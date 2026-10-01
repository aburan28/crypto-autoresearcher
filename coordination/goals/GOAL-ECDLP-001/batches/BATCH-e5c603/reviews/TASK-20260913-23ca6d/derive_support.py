#!/usr/bin/env python3
"""Independent dictionary-algebra expansion for review joint J5.

This routine is written only from the mathematical statement in the frozen
review plan.  It has no file-reading code and imports no experiment module.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable


# Exponent order in a polynomial key.
VARS = ("u", "v", "x_3", "a", "b")
Exponent = tuple[int, int, int, int, int]
Polynomial = dict[Exponent, int]


def clean(poly: dict[Exponent, int]) -> Polynomial:
    return {exponents: coefficient for exponents, coefficient in poly.items() if coefficient}


def add(*polys: Polynomial) -> Polynomial:
    result: defaultdict[Exponent, int] = defaultdict(int)
    for poly in polys:
        for exponents, coefficient in poly.items():
            result[exponents] += coefficient
    return clean(dict(result))


def scale(poly: Polynomial, scalar: int) -> Polynomial:
    return clean({exponents: scalar * coefficient for exponents, coefficient in poly.items()})


def multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    result: defaultdict[Exponent, int] = defaultdict(int)
    for left_exponents, left_coefficient in left.items():
        for right_exponents, right_coefficient in right.items():
            exponents = tuple(
                left_exponent + right_exponent
                for left_exponent, right_exponent in zip(left_exponents, right_exponents)
            )
            result[exponents] += left_coefficient * right_coefficient
    return clean(dict(result))


def symbol(index: int) -> Polynomial:
    exponents = [0] * len(VARS)
    exponents[index] = 1
    return {tuple(exponents): 1}


def constant(value: int) -> Polynomial:
    return {(0, 0, 0, 0, 0): value} if value else {}


def monomial_text(exponents: Iterable[int], names: Iterable[str]) -> str:
    factors: list[str] = []
    for exponent, name in zip(exponents, names):
        if exponent == 1:
            factors.append(name)
        elif exponent > 1:
            factors.append(f"{name}^{exponent}")
    return "*".join(factors) if factors else "1"


def term_text(coefficient: int, exponents: Exponent) -> str:
    monomial = monomial_text(exponents, VARS)
    if monomial == "1":
        return str(coefficient)
    if coefficient == 1:
        return monomial
    if coefficient == -1:
        return f"-{monomial}"
    return f"{coefficient}*{monomial}"


def polynomial_terms(poly: Polynomial) -> list[str]:
    return [
        term_text(poly[exponents], exponents)
        for exponents in sorted(poly, reverse=True)
    ]


def coefficient_polynomial_text(poly: Polynomial) -> str:
    """Render a polynomial known to involve only a, b, and x_3."""
    coefficient_terms: list[tuple[tuple[int, int, int], int]] = []
    for (u_exp, v_exp, x3_exp, a_exp, b_exp), coefficient in poly.items():
        assert u_exp == 0 and v_exp == 0
        coefficient_terms.append(((a_exp, b_exp, x3_exp), coefficient))
    coefficient_terms.sort(key=lambda item: item[0], reverse=True)

    pieces: list[str] = []
    for exponents, integer in coefficient_terms:
        monomial = monomial_text(exponents, ("a", "b", "x_3"))
        magnitude = abs(integer)
        unsigned = monomial if magnitude == 1 and monomial != "1" else (
            str(magnitude) if monomial == "1" else f"{magnitude}*{monomial}"
        )
        if not pieces:
            pieces.append(unsigned if integer > 0 else f"-{unsigned}")
        else:
            pieces.append(("+ " if integer > 0 else "- ") + unsigned)
    return " ".join(pieces) if pieces else "0"


def collect_by_uv(poly: Polynomial) -> dict[tuple[int, int], Polynomial]:
    collected: defaultdict[tuple[int, int], defaultdict[Exponent, int]] = defaultdict(
        lambda: defaultdict(int)
    )
    for (u_exp, v_exp, x3_exp, a_exp, b_exp), coefficient in poly.items():
        coefficient_exponents = (0, 0, x3_exp, a_exp, b_exp)
        collected[(u_exp, v_exp)][coefficient_exponents] += coefficient
    return {
        uv_exponents: clean(dict(coefficient_poly))
        for uv_exponents, coefficient_poly in collected.items()
    }


def homogenized_monomial(i: int, j: int) -> str:
    exponents = (i, 2 - i, j, 2 - j)
    return monomial_text(exponents, ("alpha_1", "beta_1", "alpha_2", "beta_2"))


def main() -> None:
    u, v, x3, a, b = (symbol(index) for index in range(len(VARS)))

    e1 = add(u, v, x3)
    e2 = add(multiply(u, v), multiply(u, x3), multiply(v, x3))
    e3 = multiply(multiply(u, v), x3)
    square_part = multiply(add(e2, scale(a, -1)), add(e2, scale(a, -1)))
    product_part = scale(multiply(e1, add(e3, b)), -4)
    relation = add(square_part, product_part)
    collected = collect_by_uv(relation)

    print("J5 independent symbolic derivation transcript")
    print("phase: PRE-COMPARISON; no frozen coefficient list has been consulted")
    print("coefficient ring: Z[a,b,x_3]")
    print("affine variables: u=x_1=alpha_1/beta_1; v=x_2=alpha_2/beta_2")
    print()
    print("1. Elementary symmetric functions")
    print("e_1 = u + v + x_3")
    print("e_2 = u*v + u*x_3 + v*x_3")
    print("e_3 = u*v*x_3")
    print("f_3 = (e_2-a)^2 - 4*e_1*(e_3+b)")
    print()
    print("2. Raw dictionary expansion of (e_2-a)^2")
    for term in polynomial_terms(square_part):
        print(f"  {term}")
    print()
    print("3. Raw dictionary expansion of -4*e_1*(e_3+b)")
    for term in polynomial_terms(product_part):
        print(f"  {term}")
    print()
    print("4. Collection by affine exponent pair (i,j) in u^i*v^j")
    for i, j in sorted(collected, reverse=True):
        coefficient = coefficient_polynomial_text(collected[(i, j)])
        print(f"  (i,j)=({i},{j}): coefficient = {coefficient}")
    print()
    print("5. Homogenisation rule")
    print("  beta_1^2*beta_2^2*u^i*v^j")
    print("    = alpha_1^i*beta_1^(2-i)*alpha_2^j*beta_2^(2-j)")
    print()
    print("6. Fully collected homogenised support")
    for i, j in sorted(collected, reverse=True):
        coefficient = coefficient_polynomial_text(collected[(i, j)])
        print(
            f"  numerator bidegree ({i},{j}): "
            f"{coefficient} ; monomial {homogenized_monomial(i, j)}"
        )
    print()
    support = set(collected)
    expected_grid = {(i, j) for i in range(3) for j in range(3)}
    variable_degrees = {
        i + (2 - i) + j + (2 - j)
        for i, j in support
    }
    pair_degrees = {
        (i + (2 - i), j + (2 - j))
        for i, j in support
    }
    assert support == expected_grid
    assert all(collected[pair] for pair in support)
    assert variable_degrees == {4}
    assert pair_degrees == {(2, 2)}

    print("7. Independently derived invariants")
    print(f"  monomial count: {len(support)}")
    print("  total degree in alpha_1,beta_1,alpha_2,beta_2: 4")
    print("  bihomogeneous pair-degree in (alpha_1,beta_1)|(alpha_2,beta_2): (2,2)")
    print("  numerator exponent bidegrees present:")
    print("    " + ", ".join(f"({i},{j})" for i, j in sorted(support)))
    print("  every displayed coefficient is nonzero in Z[a,b,x_3]")
    print()
    print("END PRE-COMPARISON DERIVATION")


if __name__ == "__main__":
    main()
