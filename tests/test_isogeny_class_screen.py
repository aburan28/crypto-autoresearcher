"""Regression tests for rational degree-3 kernels in the prime-field screen."""

from __future__ import annotations

import re

import pytest

from tools.isogeny_class_screen import (
    CURVES,
    Curve,
    DivisionPolys,
    Poly,
    neighbours,
    phi3,
    rational_3_kernel_polynomials,
    sqrt_mod,
    three_kernel_eigenvalue,
    valuation,
    velu,
)


P224_ROOT_TO_J = {
    0x10B321F632430C8ADC27F39EF29714947427C734DD0B5345087AB9E0:
        0x54DB34B022C936701A51346437E1EF0C450767C12DC0E5A0B27F8148,
    0x17E593D097A17B91DC66911D798276726C0FDC60AC69BDE4E04C75B4:
        0xC00E881582682DAAEE334D8D13765A3C9D5A6D9F64E032997B230913,
    0x61E523018891B5BBB2E8327A924476A5AC1E25D4115F3E152F8297EB:
        0xC6F4DF43763882390062B5E7DC7629184F76E7A881E48BDB953751B8,
    0x75822737AD89C227948948C901A1FE5273AA3696652BB0C0E7B63882:
        0x43048C83BB7D2335649775F3D8C5063D93072300292B080C1EF201CD,
}


def p224() -> tuple[Curve, dict[str, int]]:
    params = CURVES["p224"]
    return Curve(params["p"], params["a"], params["b"]), params


def brute_order(curve: Curve) -> int:
    return 1 + sum(
        1
        for x in range(curve.p)
        for y in range(curve.p)
        if curve.on_curve((x, y))
    )


@pytest.mark.parametrize("prime", [5, 11, 13, 17, 41])
def test_sqrt_mod_exhaustive(prime: int) -> None:
    for value in range(prime):
        roots = [x for x in range(prime) if x * x % prime == value]
        root = sqrt_mod(value, prime)
        if roots:
            assert root == min(roots)
            assert root * root % prime == value
        else:
            assert root is None


def test_sqrt_mod_rejects_even_modulus_and_finds_p224_points() -> None:
    with pytest.raises(ValueError, match="odd prime"):
        sqrt_mod(1, 2)

    curve, _ = p224()
    points = curve.some_points(3)
    assert len(points) == 3
    assert all(curve.on_curve(point) for point in points)


def test_divexact_is_exact_and_does_not_mutate_inputs() -> None:
    poly = Poly(101)
    left = [99, 1]
    right = [96, 1]
    product = poly.mul(left, right)
    product_before = product[:]
    left_before = left[:]

    assert poly.divexact(product, left) == right
    assert product == product_before
    assert left == left_before

    with pytest.raises(ValueError, match="not exact"):
        poly.divexact([1, 0, 1], [1, 1])
    with pytest.raises(ZeroDivisionError):
        poly.divexact([1], [0])


def test_linear_factorization_success_rejection_and_budget() -> None:
    poly = Poly(101)
    split = [1]
    expected = [2, 5, 17, 42]
    for root in expected:
        split = poly.mul(split, [(-root) % poly.p, 1])

    factors = poly.linear_factors(split)
    assert [(-factor[0]) % poly.p for factor in factors] == expected

    with pytest.raises(ValueError, match="squarefree and split"):
        poly.linear_factors([2, 0, 1])
    repeated = poly.mul([100, 1], [100, 1])
    with pytest.raises(ValueError, match="squarefree and split"):
        poly.linear_factors(repeated)

    curve, _ = p224()
    division = DivisionPolys(curve, 6)
    monic_psi3 = division.P.scal(
        division.f[3],
        pow(division.f[3][-1], -1, curve.p),
    )
    with pytest.raises(RuntimeError, match="factorization incomplete"):
        division.P.linear_factors(monic_psi3, max_shifts=1)


@pytest.mark.parametrize(
    ("prime", "a", "b", "expected"),
    [
        (5, 1, 0, []),
        (7, 0, 1, [0]),
        (5, 0, 1, [0, 1]),
        (7, 0, 2, [0, 3, 5, 6]),
    ],
)
def test_rational_3_kernel_counts_and_toy_velu_orders(
    prime: int, a: int, b: int, expected: list[int]
) -> None:
    curve = Curve(prime, a, b)
    division = DivisionPolys(curve, 6)
    factors = rational_3_kernel_polynomials(division)
    roots = [(-factor[0]) % prime for factor in factors]
    assert roots == expected

    source_order = brute_order(curve)
    for factor in factors:
        a2, b2 = velu(curve, factor)
        target = Curve(prime, a2, b2)
        assert brute_order(target) == source_order
        assert phi3(curve.j(), target.j(), prime) == 0


def test_p224_exact_rational_3_neighbours() -> None:
    curve, params = p224()
    generator = (params["Gx"], params["Gy"])
    assert curve.on_curve(generator)
    assert curve.mul(params["n"], generator) is None

    trace = curve.p + 1 - params["n"]
    discriminant = trace * trace - 4 * curve.p
    assert valuation(discriminant, 3) == 3

    division = DivisionPolys(curve, 6)
    factors = rational_3_kernel_polynomials(division)
    roots = [(-factor[0]) % curve.p for factor in factors]
    assert roots == sorted(P224_ROOT_TO_J)

    product = [1]
    for factor in factors:
        product = division.P.mul(product, factor)
    monic_psi3 = division.P.scal(
        division.f[3],
        pow(division.f[3][-1], -1, curve.p),
    )
    assert product == monic_psi3

    observed = {}
    for factor, root in zip(factors, roots):
        assert three_kernel_eigenvalue(curve, factor) == 2
        a2, b2 = velu(curve, factor)
        target = Curve(curve.p, a2, b2)
        observed[root] = target.j()
        assert phi3(curve.j(), target.j(), curve.p) == 0
    assert observed == P224_ROOT_TO_J


def test_p224_neighbour_cli_reports_each_kernel_once(capsys) -> None:
    curve, params = p224()
    trace = curve.p + 1 - params["n"]
    neighbours(curve, trace, params["n"], [3])

    output = capsys.readouterr().out
    labels = [int(value) for value in re.findall(r"kernel x=(\d+)", output)]
    assert labels == sorted(P224_ROOT_TO_J)
    assert output.count("Phi_3(j,j')=0 OK") == 4
