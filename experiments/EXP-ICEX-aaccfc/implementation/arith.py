"""Instrumented F_p, affine curve and Z/q arithmetic in the C-3 cost units of
AMD-20260926-ced670 (own copy, adapted from EXP-SDEG-85eefd fparith.py).

C-3 units: F_p multiplication (or squaring) 1; inversion 10 (declared, not
measured); affine point addition 13; hash probe 1; sparse-LA modular
multiplication over Z/q 1.

Literal reading used here (implementation.md, OQ-1): every affine group
operation with two finite operands -- addition, doubling, or an addition whose
result is O -- is charged 13 units as a whole, and the field operations it
performs internally are NOT charged again; they are tallied separately in
``pmul``/``pinv`` for the secondary field-level figure. Field operations
outside point arithmetic (liftability tests, square roots) are charged at
mul 1 / inv 10. An LA inversion over Z/q is charged 10 by analogy with the
F_p inversion (OQ-2). Additions/subtractions are free.
"""

from __future__ import annotations

from dataclasses import dataclass, fields

from common import UNIT_INV, UNIT_LA_MUL, UNIT_MUL, UNIT_POINT_ADD, UNIT_PROBE

INF = None


@dataclass
class Cost:
    mul: int = 0
    inv: int = 0
    probes: int = 0
    pt_add: int = 0
    pt_dbl: int = 0
    la_mul: int = 0
    la_inv: int = 0
    pmul: int = 0  # field mults inside point ops (not charged separately)
    pinv: int = 0  # field inversions inside point ops (not charged separately)

    def units(self) -> int:
        return (UNIT_MUL * self.mul + UNIT_INV * self.inv + UNIT_PROBE * self.probes
                + UNIT_POINT_ADD * (self.pt_add + self.pt_dbl)
                + UNIT_LA_MUL * self.la_mul + UNIT_INV * self.la_inv)

    def units_fieldlevel(self) -> int:
        """Secondary figure: point ops priced by their actual field operations."""
        return (UNIT_MUL * (self.mul + self.pmul) + UNIT_INV * (self.inv + self.pinv)
                + UNIT_PROBE * self.probes + UNIT_LA_MUL * self.la_mul + UNIT_INV * self.la_inv)

    def snapshot(self) -> tuple:
        return tuple(getattr(self, f.name) for f in fields(self))

    def delta(self, snap: tuple) -> dict:
        d = {f.name: getattr(self, f.name) - s for f, s in zip(fields(self), snap)}
        c = Cost(**d)
        d["units"] = c.units()
        d["units_fieldlevel"] = c.units_fieldlevel()
        return d

    def as_dict(self) -> dict:
        d = {f.name: getattr(self, f.name) for f in fields(self)}
        d["units"] = self.units()
        d["units_fieldlevel"] = self.units_fieldlevel()
        return d

    @staticmethod
    def from_dict(d: dict) -> "Cost":
        return Cost(**{f.name: d.get(f.name, 0) for f in fields(Cost)})


def _xgcd_inv(x: int, p: int) -> int:
    x %= p
    if x == 0:
        raise ZeroDivisionError("inverse of 0")
    r0, r1, t0, t1 = p, x, 0, 1
    while r1:
        qq = r0 // r1
        r0, r1 = r1, r0 - qq * r1
        t0, t1 = t1, t0 - qq * t1
    return t0 % p


class Fp:
    def __init__(self, p: int, cost: Cost):
        self.p, self.c = p, cost

    def mul(self, x, y):
        self.c.mul += 1
        return x * y % self.p

    def sqr(self, x):
        self.c.mul += 1
        return x * x % self.p

    def inv(self, x):
        self.c.inv += 1
        return _xgcd_inv(x, self.p)

    def pow(self, x, e):
        if e < 0:
            return self.pow(self.inv(x), -e)
        result, started = 1, False
        for bit in bin(e)[2:] if e else "":
            if started:
                result = self.sqr(result)
            if bit == "1":
                result = self.mul(result, x) if started else x % self.p
                started = True
        return result % self.p if started else 1

    def probe(self, n: int = 1):
        self.c.probes += n

    def is_square(self, x):
        x %= self.p
        return True if x == 0 else self.pow(x, (self.p - 1) // 2) == 1

    def sqrt(self, x):
        """Tonelli-Shanks, fully counted."""
        p = self.p
        x %= p
        if x == 0:
            return 0
        if not self.is_square(x):
            raise ValueError("non-residue")
        if p % 4 == 3:
            return self.pow(x, (p + 1) // 4)
        s, qq = 0, p - 1
        while qq % 2 == 0:
            qq //= 2
            s += 1
        z = 2
        while self.is_square(z):
            z += 1
        m, c, t, r = s, self.pow(z, qq), self.pow(x, qq), self.pow(x, (qq + 1) // 2)
        while t != 1:
            i, t2 = 0, t
            while t2 != 1:
                t2 = self.sqr(t2)
                i += 1
            bexp = self.pow(c, 1 << (m - i - 1))
            m, c = i, self.sqr(bexp)
            t, r = self.mul(t, c), self.mul(r, bexp)
        return r


class Curve:
    """y^2 = x^3 + a x + b, affine, INF = None. Group ops charged 13 units each."""

    def __init__(self, F: Fp, a: int, b: int):
        self.F, self.p, self.a, self.b = F, F.p, a % F.p, b % F.p

    def rhs(self, x):
        F = self.F
        return (F.mul((F.sqr(x) + self.a) % self.p, x) + self.b) % self.p

    def is_liftable(self, x):
        r = self.rhs(x)
        return r != 0 and self.F.is_square(r)

    def lift(self, x):
        y = self.F.sqrt(self.rhs(x))
        return (x, min(y, self.p - y))

    def neg(self, P):
        return INF if P is INF else (P[0], (-P[1]) % self.p)

    def add(self, P, Q):
        if P is INF:
            return Q
        if Q is INF:
            return P
        c, p = self.F.c, self.p
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if (y1 + y2) % p == 0:
                c.pt_add += 1
                return INF
            c.pt_dbl += 1
            c.pmul += 4
            c.pinv += 1
            lam = (3 * x1 * x1 + self.a) * _xgcd_inv(2 * y1, p) % p
        else:
            c.pt_add += 1
            c.pmul += 3
            c.pinv += 1
            lam = (y2 - y1) * _xgcd_inv(x2 - x1, p) % p
        x3 = (lam * lam - x1 - x2) % p
        return (x3, (lam * (x1 - x3) - y1) % p)

    def sub(self, P, Q):
        return self.add(P, self.neg(Q))

    def mul(self, k: int, P):
        """Right-to-left double-and-add through add()."""
        if k < 0:
            return self.mul(-k, self.neg(P))
        R, Qp = INF, P
        while k:
            if k & 1:
                R = self.add(R, Qp)
            k >>= 1
            if k:
                Qp = self.add(Qp, Qp)
        return R


class Zq:
    """Z/q arithmetic for sparse LA; every modular multiplication counted (C-3)."""

    def __init__(self, q: int, cost: Cost):
        self.q, self.c = q, cost

    def mul(self, x, y):
        self.c.la_mul += 1
        return x * y % self.q

    def inv(self, x):
        self.c.la_inv += 1
        return _xgcd_inv(x, self.q)

    def count(self, n: int):
        self.c.la_mul += n
