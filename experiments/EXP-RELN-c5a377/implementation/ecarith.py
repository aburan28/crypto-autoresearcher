"""Instrumented F_p and affine short-Weierstrass arithmetic for every charged path.

Charged units (``OpCounter``):
  group_ops  one point addition, subtraction or doubling (including the trivial
             cases that return O); negation is free
  mul        one modular multiplication or squaring
  inv        one inversion, plus ``gcd_steps`` extended-Euclid division steps
W_field = mul + inv + gcd_steps. The protocol's "charged work" is group_ops.
"""

from __future__ import annotations

from dataclasses import dataclass

O = None  # point at infinity


@dataclass
class OpCounter:
    group_ops: int = 0
    mul: int = 0
    inv: int = 0
    gcd_steps: int = 0

    def W_field(self) -> int:
        return self.mul + self.inv + self.gcd_steps

    def snapshot(self) -> tuple:
        return (self.group_ops, self.mul, self.inv, self.gcd_steps)

    def delta(self, snap: tuple) -> dict:
        g, m, i, s = snap
        d = dict(group_ops=self.group_ops - g, mul=self.mul - m, inv=self.inv - i,
                 gcd_steps=self.gcd_steps - s)
        d["W_field"] = d["mul"] + d["inv"] + d["gcd_steps"]
        return d

    def as_dict(self) -> dict:
        return dict(group_ops=self.group_ops, mul=self.mul, inv=self.inv,
                    gcd_steps=self.gcd_steps, W_field=self.W_field())


class Fp:
    def __init__(self, p: int, counter: OpCounter):
        self.p = p
        self.c = counter

    def mul(self, x, y):
        self.c.mul += 1
        return x * y % self.p

    def inv(self, x):
        p = self.p
        x %= p
        if x == 0:
            raise ZeroDivisionError("inverse of 0")
        r0, r1, t0, t1, steps = p, x, 0, 1, 0
        while r1:
            qq = r0 // r1
            r0, r1 = r1, r0 - qq * r1
            t0, t1 = t1, t0 - qq * t1
            steps += 1
        self.c.inv += 1
        self.c.gcd_steps += steps
        return t0 % p

    def pow(self, x, e):
        """Square-and-multiply, every squaring and multiplication charged."""
        p = self.p
        r, base = 1, x % p
        while e:
            if e & 1:
                r = r * base % p
                self.c.mul += 1
            e >>= 1
            if e:
                base = base * base % p
                self.c.mul += 1
        return r

    def is_square(self, x) -> bool:
        x %= self.p
        return x == 0 or self.pow(x, (self.p - 1) // 2) == 1

    def sqrt(self, x):
        """Tonelli-Shanks (charged); x must be a nonzero square."""
        p = self.p
        x %= p
        if x == 0:
            return 0
        if p % 4 == 3:
            return self.pow(x, (p + 1) // 4)
        s, qq = 0, p - 1
        while qq % 2 == 0:
            qq //= 2
            s += 1
        z = 2
        while self.pow(z, (p - 1) // 2) != p - 1:
            z += 1
        m, c, t, r = s, self.pow(z, qq), self.pow(x, qq), self.pow(x, (qq + 1) // 2)
        while t != 1:
            i, t2 = 0, t
            while t2 != 1:
                t2 = self.mul(t2, t2)
                i += 1
            b = self.pow(c, 1 << (m - i - 1))
            m, c = i, self.mul(b, b)
            t, r = self.mul(t, c), self.mul(r, b)
        return r


class Curve:
    """y^2 = x^3 + a x + b over an instrumented Fp."""

    def __init__(self, F: Fp, a: int, b: int):
        self.F, self.p, self.a, self.b = F, F.p, a % F.p, b % F.p

    def rhs(self, x):
        F = self.F
        return (F.mul(F.mul(x, x), x) + F.mul(self.a, x) + self.b) % self.p

    def neg(self, P):
        return O if P is O else (P[0], (-P[1]) % self.p)

    def add(self, P, Q):
        F, p = self.F, self.p
        F.c.group_ops += 1
        if P is O:
            return Q
        if Q is O:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if (y1 + y2) % p == 0:
                return O
            lam = F.mul((3 * F.mul(x1, x1) + self.a) % p, F.inv(2 * y1))
        else:
            lam = F.mul((y2 - y1) % p, F.inv(x2 - x1))
        x3 = (F.mul(lam, lam) - x1 - x2) % p
        return (x3, (F.mul(lam, (x1 - x3) % p) - y1) % p)

    def sub(self, P, Q):
        return self.add(P, self.neg(Q))

    def mul(self, k: int, P):
        """Left-to-right double-and-add; charged as (bitlen-1) doublings plus
        (popcount-1) additions (the audit recomputes this formula)."""
        if k == 0 or P is O:
            return O
        R = P
        for bit in bin(k)[3:]:
            R = self.add(R, R)
            if bit == "1":
                R = self.add(R, P)
        return R


def scalar_mul_charge(k: int) -> int:
    """Group operations charged by Curve.mul(k, P) for P != O and k > 0."""
    if k <= 0:
        return 0
    return (k.bit_length() - 1) + (bin(k).count("1") - 1)
