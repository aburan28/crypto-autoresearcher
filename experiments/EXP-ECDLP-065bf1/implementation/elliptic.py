"""Toy short-Weierstrass arithmetic over a prime field. Dual addition routes.

Path A uses the affine slope formula. Path B uses the chord cubic restriction
(same third-intersection identity). No Magma/Sage. No scalar recovery.
"""
from __future__ import annotations


def modinv(a: int, p: int) -> int:
    a %= p
    if a == 0:
        raise ZeroDivisionError("inverse of 0")
    return pow(a, -1, p)


def on_curve(x: int, y: int, a: int, b: int, p: int) -> bool:
    return (y * y - (x * x * x + a * x + b)) % p == 0


def add_affine_a(
    p1: tuple[int, int], p2: tuple[int, int], curve_a: int, p: int
) -> tuple[int, int]:
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2 and (y1 + y2) % p == 0:
        raise ValueError("point at infinity not used in this instrument")
    if x1 == x2 and y1 == y2:
        lam = ((3 * x1 * x1 + curve_a) * modinv(2 * y1, p)) % p
    else:
        lam = ((y2 - y1) * modinv((x2 - x1) % p, p)) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return x3, y3


def add_affine_b(
    p1: tuple[int, int], p2: tuple[int, int], curve_a: int, p: int
) -> tuple[int, int]:
    """Chord cubic: the third root of (x-x1)(x-x2)(x-x3) = lambda^2 - (x1+x2+x3) identity."""
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2 and (y1 + y2) % p == 0:
        raise ValueError("point at infinity not used in this instrument")
    if x1 == x2 and y1 == y2:
        num = (3 * x1 * x1 + curve_a) % p
        den = (2 * y1) % p
    else:
        num = (y2 - y1) % p
        den = (x2 - x1) % p
    lam = (num * modinv(den, p)) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return x3, y3


def scalar_mul(k: int, g: tuple[int, int], curve_a: int, p: int, route: str) -> tuple[int, int]:
    if k < 1:
        raise ValueError("k>=1 required (public known-scalar forward)")
    add = add_affine_a if route == "A" else add_affine_b
    acc = g
    # naive repeated addition, public k only
    for _ in range(k - 1):
        acc = add(acc, g, curve_a, p)
    return acc


def double_add_chain(k: int, g: tuple[int, int], curve_a: int, p: int, route: str) -> list[tuple[int, int]]:
    """Return [G, 2G, ..., kG] via successive +G (public forward)."""
    add = add_affine_a if route == "A" else add_affine_b
    pts = [g]
    acc = g
    for _ in range(k - 1):
        acc = add(acc, g, curve_a, p)
        pts.append(acc)
    return pts
