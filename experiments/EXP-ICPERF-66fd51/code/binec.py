#!/usr/bin/env python3
"""Independent GF(2^n) and binary-curve arithmetic for certificate checking.

Written from the field and curve definitions alone (no code from the benchmark
generator or WDSat is reused). Conventions follow the generator's INFO files:
coefficient strings are LOW-DEGREE-FIRST ('1101' = 1 + x + x^3).

Curve: y^2 + x*y = x^3 + a2*x^2 + a6 over GF(2^n) (Trimoska's fixed curve has a2 = a6 = 1).
Certificate: x-coordinates x1, x2, x3 of factor-base points and x_R of the target;
valid iff some choice of y-roots gives x(P1 + P2 + P3) == x_R (equivalently, the
fourth summation polynomial vanishes at (x1, x2, x3, x_R)).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple


def bits_to_int(s: str) -> int:
    """Low-degree-first bit string -> integer with bit i = coefficient of x^i."""
    v = 0
    for i, c in enumerate(s.strip()):
        if c == "1":
            v |= 1 << i
        elif c != "0":
            raise ValueError(f"bad coefficient character {c!r}")
    return v


def int_to_bits(v: int, width: int) -> str:
    return "".join("1" if (v >> i) & 1 else "0" for i in range(width))


@dataclass(frozen=True)
class GF2n:
    n: int
    modulus: int  # integer with bit i = coefficient of x^i, degree exactly n

    def __post_init__(self):
        if self.modulus.bit_length() - 1 != self.n:
            raise ValueError("modulus degree must equal n")

    def mul(self, a: int, b: int) -> int:
        r = 0
        m = self.modulus
        top = 1 << self.n
        while b:
            if b & 1:
                r ^= a
            b >>= 1
            a <<= 1
            if a & top:
                a ^= m
        return r

    def sqr(self, a: int) -> int:
        return self.mul(a, a)

    def pow(self, a: int, e: int) -> int:
        r = 1
        while e:
            if e & 1:
                r = self.mul(r, a)
            a = self.mul(a, a)
            e >>= 1
        return r

    def inv(self, a: int) -> int:
        if a == 0:
            raise ZeroDivisionError
        return self.pow(a, (1 << self.n) - 2)

    def trace(self, a: int) -> int:
        t = a
        for _ in range(self.n - 1):
            t = self.sqr(t) ^ a
        return t  # 0 or 1

    def half_trace(self, a: int) -> int:
        """For odd n: H(a) with H(a)^2 + H(a) = a + Tr(a)."""
        if self.n % 2 == 0:
            raise NotImplementedError("half-trace needs odd n")
        h = a
        for _ in range((self.n - 1) // 2):
            h = self.sqr(self.sqr(h)) ^ a
        return h

    def solve_quadratic(self, b: int, c: int) -> Optional[int]:
        """Return a root z of z^2 + b*z + c = 0, or None if no root in GF(2^n)."""
        if b == 0:
            # z^2 = c: squaring is a bijection; z = c^(2^(n-1))
            return self.pow(c, 1 << (self.n - 1))
        # substitute z = b*w: w^2 + w = c / b^2
        d = self.mul(c, self.inv(self.sqr(b)))
        if self.trace(d) != 0:
            return None
        w = self.half_trace(d)
        assert self.sqr(w) ^ w == d
        return self.mul(b, w)


Point = Optional[Tuple[int, int]]  # None is the point at infinity


@dataclass(frozen=True)
class BinaryCurve:
    F: GF2n
    a2: int = 1
    a6: int = 1

    def on_curve(self, P: Point) -> bool:
        if P is None:
            return True
        x, y = P
        F = self.F
        lhs = F.sqr(y) ^ F.mul(x, y)
        rhs = F.mul(F.sqr(x), x) ^ F.mul(self.a2, F.sqr(x)) ^ self.a6
        return lhs == rhs

    def lift_x(self, x: int) -> Optional[Tuple[int, int]]:
        """One point with the given x, or None if x is not an x-coordinate."""
        F = self.F
        c = F.mul(F.sqr(x), x) ^ F.mul(self.a2, F.sqr(x)) ^ self.a6
        y = F.solve_quadratic(x, c)
        if y is None:
            return None
        P = (x, y)
        assert self.on_curve(P)
        return P

    def neg(self, P: Point) -> Point:
        if P is None:
            return None
        x, y = P
        return (x, x ^ y)

    def add(self, P: Point, Q: Point) -> Point:
        F = self.F
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if y1 ^ y2 == x1 or x1 == 0:  # Q == -P (or the 2-torsion point x = 0)
                return None
            # doubling: lambda = x1 + y1/x1
            lam = x1 ^ F.mul(y1, F.inv(x1))
            x3 = F.sqr(lam) ^ lam ^ self.a2
            y3 = F.sqr(x1) ^ F.mul(lam ^ 1, x3)
        else:
            lam = F.mul(y1 ^ y2, F.inv(x1 ^ x2))
            x3 = F.sqr(lam) ^ lam ^ x1 ^ x2 ^ self.a2
            y3 = F.mul(lam, x1 ^ x3) ^ x3 ^ y1
        R = (x3, y3)
        assert self.on_curve(R), "addition left the curve"
        return R


def certificate_holds(curve: BinaryCurve, xs: Tuple[int, int, int], x_target: int) -> Tuple[bool, str]:
    """Decide whether some P1 +/- P2 +/- P3 with x(Pi) = xs[i] has x-coordinate x_target."""
    pts = []
    for x in xs:
        P = curve.lift_x(x)
        if P is None:
            return False, f"x = {x:#x} is not an x-coordinate on the curve"
        pts.append(P)
    P1, P2, P3 = pts
    for s2 in (1, -1):
        Q2 = P2 if s2 == 1 else curve.neg(P2)
        for s3 in (1, -1):
            Q3 = P3 if s3 == 1 else curve.neg(P3)
            S = curve.add(curve.add(P1, Q2), Q3)
            if S is not None and S[0] == x_target:
                return True, f"P1 {'+' if s2 == 1 else '-'} P2 {'+' if s3 == 1 else '-'} P3 has x = x_R"
    return False, "no sign choice sums to a point with x = x_R"


@dataclass(frozen=True)
class InfoFile:
    n: int
    l: int
    modulus_bits: str
    x_r_bits: str
    label: str  # 'S' or 'U'
    cert_bits: Optional[Tuple[str, str, str]]

    @classmethod
    def parse(cls, path: str) -> "InfoFile":
        lines = [ln.strip() for ln in open(path).read().splitlines() if ln.strip()]
        n, l = (int(t) for t in lines[0].split())
        modulus, x_r, label = lines[1], lines[2], lines[3]
        cert = None
        if label == "S":
            parts = lines[4].split("-")
            if len(parts) != 3:
                raise ValueError(f"{path}: certificate does not have three parts")
            cert = (parts[0], parts[1], parts[2])
        return cls(n, l, modulus, x_r, label, cert)

    def field(self) -> GF2n:
        return GF2n(self.n, bits_to_int(self.modulus_bits))

    def curve(self) -> BinaryCurve:
        return BinaryCurve(self.field(), 1, 1)

    def check_certificate(self, cert_bits: Optional[Tuple[str, str, str]] = None) -> Tuple[bool, str]:
        cert = cert_bits if cert_bits is not None else self.cert_bits
        if cert is None:
            return False, "no certificate"
        for c in cert:
            if len(c) > self.l or (len(c) == self.l and False):
                return False, f"certificate component {c} longer than l = {self.l}"
            if any(ch == "1" for ch in c[self.l:]):
                return False, "certificate component has degree >= l"
        xs = tuple(bits_to_int(c) for c in cert)
        return certificate_holds(self.curve(), xs, bits_to_int(self.x_r_bits))


if __name__ == "__main__":
    import sys

    for p in sys.argv[1:]:
        info = InfoFile.parse(p)
        ok, why = info.check_certificate()
        print(f"{p}: n={info.n} l={info.l} label={info.label} certificate={'VALID' if ok else 'INVALID'} ({why})")
