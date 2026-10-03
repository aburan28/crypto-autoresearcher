#!/usr/bin/env python3
"""Koblitz Y^2 + XY = X^3 + A X^2 + B. Infinity is None. Stdlib only."""
from __future__ import annotations

from typing import Any, Optional, Tuple

Point = Optional[Tuple[int, int]]


class Curve:
    def __init__(self, F: Any, A: int, B: int):
        if B == 0:
            raise ValueError("B must be nonzero")
        self.F, self.A, self.B = F, A, B

    def on_curve(self, P: Point) -> bool:
        if P is None:
            return True
        F = self.F
        x, y = P
        lhs = F.mul(y, y) ^ F.mul(x, y)
        x2 = F.mul(x, x)
        rhs = F.mul(x2, x) ^ F.mul(self.A, x2) ^ self.B
        return lhs == rhs

    def neg(self, P: Point) -> Point:
        if P is None:
            return None
        return (P[0], P[0] ^ P[1])

    def double(self, P: Point) -> Point:
        F = self.F
        if P is None:
            return None
        x1, y1 = P
        if x1 == 0:
            return None
        lam = x1 ^ F.mul(y1, F.inv(x1))
        x3 = F.mul(lam, lam) ^ lam ^ self.A
        y3 = F.mul(x1, x1) ^ F.mul(lam ^ 1, x3)
        return (x3, y3)

    def add(self, P: Point, Q: Point) -> Point:
        F = self.F
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if y2 == (x1 ^ y1):
                return None
            return self.double(P)
        dx = x1 ^ x2
        lam = F.mul(y1 ^ y2, F.inv(dx))
        x3 = F.mul(lam, lam) ^ lam ^ x1 ^ x2 ^ self.A
        y3 = F.mul(lam, x1 ^ x3) ^ x3 ^ y1
        return (x3, y3)

    def rhs_c(self, x: int) -> int:
        F = self.F
        return x ^ self.A ^ F.mul(self.B, F.inv(F.mul(x, x)))

    def lift_x(self, x: int) -> Point:
        F = self.F
        if x == 0:
            return (0, F.sqrt(self.B))
        c = self.rhs_c(x)
        if F.trace(c) != 0:
            return None
        z = F.half_trace(c)
        return (x, F.mul(x, z))

    def frobenius(self, P: Point) -> Point:
        if P is None:
            return None
        F = self.F
        return (F.square(P[0]), F.square(P[1]))
