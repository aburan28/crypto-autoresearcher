"""Koblitz E_0: y^2 + x y = x^3 + 1 over F_{2^n} for EXP-CERTBIN-0f4599.

Points are (x, y) int pairs; O is None. Twin add paths: add_a (lambda form)
and add_b (same formula, independently expanded). Every add increments the
shared counter. No Magma/Sage/AUXIN/Bedrock.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from gf2n import Field

Point = Optional[tuple[int, int]]


@dataclass
class Curve:
    F: Field
    a2: int = 0
    a6: int = 1
    additions: int = 0
    additions_b: int = 0

    def on_curve(self, P: Point) -> bool:
        if P is None:
            return True
        x, y = P
        left = self.F.mul(y, y) ^ self.F.mul(x, y)
        right = self.F.mul(x, self.F.mul(x, x)) ^ self.F.mul(self.a2, self.F.mul(x, x)) ^ self.a6
        return left == right

    def neg(self, P: Point) -> Point:
        if P is None:
            return None
        x, y = P
        return (x, x ^ y)

    def _lambda_add(self, P: Point, Q: Point) -> Point:
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        F = self.F
        if x1 == x2:
            if y2 == (x1 ^ y1):
                return None
            if x1 == 0:
                return None
            lam = x1 ^ F.mul(y1, F.inv(x1))
            x3 = F.mul(lam, lam) ^ lam ^ self.a2
            y3 = F.mul(x1, x1) ^ F.mul(lam ^ 1, x3)
            return (x3, y3)
        lam = F.mul(y1 ^ y2, F.inv(x1 ^ x2))
        x3 = F.mul(lam, lam) ^ lam ^ x1 ^ x2 ^ self.a2
        y3 = F.mul(lam, x1 ^ x3) ^ x3 ^ y1
        return (x3, y3)

    def add_a(self, P: Point, Q: Point) -> Point:
        self.additions += 1
        return self._lambda_add(P, Q)

    def add_b(self, P: Point, Q: Point) -> Point:
        self.additions_b += 1
        if P is None:
            return Q
        if Q is None:
            return P
        if P == self.neg(Q):
            return None
        return self._lambda_add(P, Q)

    def add(self, P: Point, Q: Point) -> Point:
        return self.add_a(P, Q)

    def double(self, P: Point) -> Point:
        return self.add(P, P)

    def smul(self, k: int, P: Point) -> Point:
        R: Point = None
        Q = P
        while k:
            if k & 1:
                R = self.add(R, Q)
            Q = self.add(Q, Q)
            k >>= 1
        return R

    def solve_ys(self, x: int) -> list[int]:
        F = self.F
        if x == 0:
            return [1]
        invx = F.inv(x)
        rhs = x ^ F.mul(invx, invx)
        if self.a2:
            rhs ^= self.a2
        if F.trace(rhs) != 0:
            return []
        z = F.half_trace(rhs)
        y1 = F.mul(z, x)
        y2 = y1 ^ x
        return [y1, y2]

    def affine_points_with_x_in(self, xs: list[int]) -> list[tuple[int, int]]:
        pts: list[tuple[int, int]] = []
        for x in xs:
            for y in self.solve_ys(x):
                P = (x, y)
                if self.on_curve(P):
                    pts.append(P)
        return pts


def encode_point(P: Point) -> str:
    if P is None:
        return "O"
    return f"{P[0]:x},{P[1]:x}"
