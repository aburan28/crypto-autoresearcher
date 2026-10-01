"""Instrumented F_p and affine short-Weierstrass arithmetic (AMD-20260926-3479cf C-4).

Every charged backend (B0, B1) performs all field arithmetic through an ``Fp``
instance bound to an ``OpCounter``. Charged units:

* ``mul``        one modular multiplication or squaring
* ``inv``        one inversion, charged as 1 mult (C-4) ...
* ``gcd_steps``  ... plus the number of extended-Euclid division steps it took
* ``probes``     one hash-table probe (lookup or insert)

W = mul + inv + gcd_steps + probes (see ``OpCounter.W``). Additions and
subtractions are counted in ``add`` for information but are not charged.

Bulk helpers (``count_mul``) exist for vectorised polynomial kernels: they add
exactly the number of elementwise products the kernel performs, and
``tests/test_fparith.py`` checks bulk counts against per-operation counting.
"""

from __future__ import annotations

from dataclasses import dataclass, field

INF = None  # the point at infinity in affine coordinates


@dataclass
class OpCounter:
    mul: int = 0
    inv: int = 0
    gcd_steps: int = 0
    probes: int = 0
    add: int = 0

    def W(self) -> int:
        return self.mul + self.inv + self.gcd_steps + self.probes

    def snapshot(self) -> tuple:
        return (self.mul, self.inv, self.gcd_steps, self.probes, self.add)

    def delta(self, snap: tuple) -> dict:
        m, i, g, p, a = snap
        d = dict(mul=self.mul - m, inv=self.inv - i, gcd_steps=self.gcd_steps - g,
                 probes=self.probes - p, add=self.add - a)
        d["W"] = d["mul"] + d["inv"] + d["gcd_steps"] + d["probes"]
        return d

    def as_dict(self) -> dict:
        return dict(mul=self.mul, inv=self.inv, gcd_steps=self.gcd_steps,
                    probes=self.probes, add=self.add, W=self.W())


class Fp:
    """Prime field with counted operations. Elements are ints in [0, p)."""

    def __init__(self, p: int, counter: OpCounter | None = None):
        self.p = p
        self.c = counter if counter is not None else OpCounter()

    # -- charged -------------------------------------------------------
    def mul(self, x: int, y: int) -> int:
        self.c.mul += 1
        return x * y % self.p

    def sqr(self, x: int) -> int:
        self.c.mul += 1
        return x * x % self.p

    def count_mul(self, n: int) -> None:
        self.c.mul += n

    def inv(self, x: int) -> int:
        """Extended Euclid; charged as 1 mult plus its division-step count."""
        p = self.p
        x %= p
        if x == 0:
            raise ZeroDivisionError("inverse of 0 in F_p")
        r0, r1 = p, x
        t0, t1 = 0, 1
        steps = 0
        while r1:
            qq = r0 // r1
            r0, r1 = r1, r0 - qq * r1
            t0, t1 = t1, t0 - qq * t1
            steps += 1
        self.c.inv += 1
        self.c.gcd_steps += steps
        return t0 % p

    def pow(self, x: int, e: int) -> int:
        """Left-to-right square-and-multiply; every product counted."""
        if e < 0:
            return self.pow(self.inv(x), -e)
        result = 1
        started = False
        for bit in bin(e)[2:] if e else "":
            if started:
                result = self.sqr(result)
            if bit == "1":
                result = self.mul(result, x) if started else x % self.p
                started = True
        return result % self.p if started else 1

    def probe(self, n: int = 1) -> None:
        self.c.probes += n

    # -- uncharged (counted in ``add``) ----------------------------------
    def add(self, x: int, y: int) -> int:
        self.c.add += 1
        return (x + y) % self.p

    def sub(self, x: int, y: int) -> int:
        self.c.add += 1
        return (x - y) % self.p

    def neg(self, x: int) -> int:
        return (-x) % self.p

    # -- derived -------------------------------------------------------
    def is_square(self, x: int) -> bool:
        x %= self.p
        if x == 0:
            return True
        return self.pow(x, (self.p - 1) // 2) == 1

    def sqrt(self, x: int) -> int:
        """Tonelli-Shanks; raises ValueError on a non-residue. Fully counted."""
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
        m = s
        c = self.pow(z, qq)
        t = self.pow(x, qq)
        r = self.pow(x, (qq + 1) // 2)
        while t != 1:
            i, t2 = 0, t
            while t2 != 1:
                t2 = self.sqr(t2)
                i += 1
            bexp = self.pow(c, 1 << (m - i - 1))
            m = i
            c = self.sqr(bexp)
            t = self.mul(t, c)
            r = self.mul(r, bexp)
        return r


class Curve:
    """y^2 = x^3 + a x + b over an instrumented Fp; affine, INF = None."""

    def __init__(self, F: Fp, a: int, b: int):
        self.F = F
        self.p = F.p
        self.a = a % F.p
        self.b = b % F.p

    def rhs(self, x: int) -> int:
        F = self.F
        return F.add(F.mul(F.add(F.sqr(x), self.a), x), self.b)

    def is_liftable(self, x: int) -> bool:
        """x lifts to an F_p-point with y != 0 (prime-order curves have no 2-torsion)."""
        r = self.rhs(x)
        return r != 0 and self.F.is_square(r)

    def lift(self, x: int):
        """Canonical lift (x, min(y, p - y)), matching the fixture generator's G."""
        y = self.F.sqrt(self.rhs(x))
        return (x, min(y, self.p - y))

    def on_curve(self, P) -> bool:
        if P is INF:
            return True
        x, y = P
        return (y * y - (x * x * x + self.a * x + self.b)) % self.p == 0

    def neg(self, P):
        if P is INF:
            return INF
        return (P[0], (-P[1]) % self.p)

    def add(self, P, Q):
        if P is INF:
            return Q
        if Q is INF:
            return P
        F = self.F
        p = self.p
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if (y1 + y2) % p == 0:
                return INF
            # doubling: lambda = (3x^2 + a) / 2y
            num = (3 * F.sqr(x1) + self.a) % p
            lam = F.mul(num, F.inv(2 * y1))
        else:
            lam = F.mul((y2 - y1) % p, F.inv((x2 - x1) % p))
        F.c.add += 6
        x3 = (F.sqr(lam) - x1 - x2) % p
        y3 = (F.mul(lam, (x1 - x3) % p) - y1) % p
        return (x3, y3)

    def sub(self, P, Q):
        return self.add(P, self.neg(Q))

    def mul(self, k: int, P):
        """Double-and-add, counted through add()."""
        if k < 0:
            return self.mul(-k, self.neg(P))
        R = INF
        Q = P
        while k:
            if k & 1:
                R = self.add(R, Q)
            k >>= 1
            if k:
                Q = self.add(Q, Q)
        return R
