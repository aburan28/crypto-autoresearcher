"""Exact target-quadratic coefficients for first-norm TT specialization."""

from __future__ import annotations

from collections.abc import Sequence


def _projective(target: Sequence[int], p: int) -> tuple[int, int, int]:
    if p <= 2:
        raise ValueError("p must be an odd prime")
    if len(target) != 3:
        raise ValueError("target must contain exactly X, Y, Z")
    x, y, z = (int(value) for value in target)
    canonical = tuple(value >= 0 and value < p for value in (x, y, z))
    if not all(canonical):
        raise ValueError("target coordinates must be canonical residues")
    zero_coordinates = (x == 0, y == 0, z == 0)
    if all(zero_coordinates):
        raise ValueError("the all-zero projective tuple is invalid")
    return x, y, z


def trace_zero_coefficients(
    target: Sequence[int],
    p: int,
    norm_n: int,
) -> tuple[int, int, int, int, int, int]:
    """Return coefficients in basis order X2, XZ, Z2, XY, YZ, Y2."""

    x, y, z = _projective(target, p)
    n = int(norm_n) % p
    x2 = x * x % p
    y2 = y * y % p
    z2 = z * z % p
    return (
        z2,
        -2 * x * z % p,
        (x2 + n * y2) % p,
        0,
        -2 * n * y * z % p,
        n * z2 % p,
    )


def general_basis_coefficients(
    target: Sequence[int],
    p: int,
    trace_t: int,
    norm_n: int,
) -> tuple[int, int, int, int, int, int]:
    """Return six-source coefficients for a general quadratic basis."""

    x, y, z = _projective(target, p)
    t = int(trace_t) % p
    n = int(norm_n) % p
    x2 = x * x % p
    y2 = y * y % p
    z2 = z * z % p
    return (
        z2,
        -z * (2 * x + t * y) % p,
        (x2 + t * x * y + n * y2) % p,
        t * z2 % p,
        -z * (t * x + 2 * n * y) % p,
        n * z2 % p,
    )
