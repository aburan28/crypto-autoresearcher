#!/usr/bin/env python3
"""Binary field and binary-curve arithmetic for EXP-SEMBIN-354a75.

Standard library only, integers as bit-vectors over F_2, one irreducible
polynomial per degree found by search rather than transcribed. The experiment
COUNTS decompositions and never solves a polynomial system, so nothing here has
to be fast at cryptographic size; it has to be right at n <= 24 and checkable by
a reader who does not trust it.

TWO FIELDS PER CELL, AND WHY. F_q = F_{2^n} is where the curve and the target
point live. F_{q^2} is where the other y-root lives when the trace condition
fails, and Semaev's Lemma 2 is about exactly those solutions: the algebraic
system counts them and they are not usable relations. The contract makes
reporting them separately an invalidation rule, because a count that silently
includes or silently excludes them differs from the correct one by precisely the
quantity under measurement.

F_{q^2} IS BUILT AS A QUADRATIC EXTENSION OF F_q, NOT AS F_{2^{2n}} WITH ITS OWN
MODULUS. The first draft did the latter and had to locate the embedding of F_q by
searching F_{q^2} for a root of F_q's modulus -- 64 seconds at n = 13, and
O(2^{2n}) work, so 2^48 at the contract's largest cell. Representing F_{q^2} as
F_q[u]/(u^2 + u + delta) with Tr_{F_q}(delta) = 1 makes the embedding the
inclusion b = 0, makes arithmetic a pair of F_q operations, and makes the
Lemma-2 root explicit: for c in F_q with Tr(c) = 1, the solutions of z^2 + z = c
are z = z0 + u where z0^2 + z0 = c + delta. That is derived in
`QuadraticExtension.solve_quadratic_over_base` and checked there.
"""
from __future__ import annotations

# Moduli are SEARCHED, never tabulated. The first draft carried a hand-typed
# table and the import-time irreducibility check rejected its degree-18 entry
# immediately -- which is the argument against the table. Every entry is a
# 20-to-50-bit constant no reader verifies by eye, a wrong one silently redefines
# the field every count takes place in, and the property is cheap to test.
_MODULUS_CACHE: dict[int, int] = {}


def clmul(a: int, b: int) -> int:
    """Carry-less product of two F_2 polynomials packed into ints."""
    out = 0
    while b:
        low = b & -b
        out ^= a * low
        b ^= low
    return out


def _reduce(v: int, modulus: int, m: int) -> int:
    while v.bit_length() > m:
        v ^= modulus << (v.bit_length() - m - 1)
    return v


def _pow_in(v: int, e: int, modulus: int, m: int) -> int:
    r, base = 1, v
    while e:
        if e & 1:
            r = _reduce(clmul(r, base), modulus, m)
        base = _reduce(clmul(base, base), modulus, m)
        e >>= 1
    return r


def _is_irreducible(m: int, modulus: int) -> bool:
    """x^(2^m) == x mod f, and x^(2^d) != x for every proper divisor d of m.

    This is the property actually required: the modulus must generate a field of
    exactly 2^m elements rather than of a subfield. Cheaper and far less
    error-prone than trial division, and applied to every modulus this module
    uses, searched or caller-supplied.
    """
    if modulus.bit_length() != m + 1:
        return False
    if _pow_in(2, 1 << m, modulus, m) != 2:
        return False
    for d in range(1, m):
        if m % d == 0 and _pow_in(2, 1 << d, modulus, m) == 2:
            return False
    return True


def _find_modulus(m: int) -> int:
    """Smallest irreducible x^m + ... in a fixed enumeration order.

    Trinomials x^m + x^k + 1 by increasing k, then pentanomials
    lexicographically. Deterministic, so every machine and every worktree gets
    the same field and two runs are comparable.
    """
    if m < 2:
        raise ValueError("field degree must be at least 2")
    head = 1 << m
    for k in range(1, m):
        cand = head | (1 << k) | 1
        if _is_irreducible(m, cand):
            return cand
    for k3 in range(3, m):
        for k2 in range(2, k3):
            for k1 in range(1, k2):
                cand = head | (1 << k3) | (1 << k2) | (1 << k1) | 1
                if _is_irreducible(m, cand):
                    return cand
    raise ArithmeticError(f"no irreducible tri- or pentanomial of degree {m}")


def modulus_for(m: int) -> int:
    if m not in _MODULUS_CACHE:
        _MODULUS_CACHE[m] = _find_modulus(m)
    return _MODULUS_CACHE[m]


class GF2m:
    """F_{2^m} as ints, reduced modulo a fixed irreducible polynomial.

    Zero is 0 and one is 1, so `add` is xor and elements are hashable ints. That
    matters: the enumeration buckets tens of millions of curve points by value,
    and an int key is the difference between a feasible run and an infeasible
    one.
    """

    is_extension = False

    def __init__(self, m: int, modulus: int | None = None) -> None:
        self.m = m
        if modulus is None:
            modulus = modulus_for(m)
        elif not _is_irreducible(m, modulus):
            raise ValueError(f"supplied modulus for degree {m} is not "
                             f"irreducible")
        self.modulus = modulus
        self.size = 1 << m
        self.mask = self.size - 1
        self.zero = 0
        self.one = 1

    def add(self, a: int, b: int) -> int:
        return a ^ b

    def reduce(self, v: int) -> int:
        return _reduce(v, self.modulus, self.m)

    def mul(self, a: int, b: int) -> int:
        return _reduce(clmul(a, b), self.modulus, self.m)

    def sqr(self, a: int) -> int:
        return _reduce(clmul(a, a), self.modulus, self.m)

    def pow(self, a: int, e: int) -> int:
        return _pow_in(a, e, self.modulus, self.m)

    def inv(self, a: int) -> int:
        if a == 0:
            raise ZeroDivisionError("inverse of zero in F_{2^m}")
        return self.pow(a, self.size - 2)

    def div(self, a: int, b: int) -> int:
        return self.mul(a, self.inv(b))

    def sqrt(self, a: int) -> int:
        """The unique square root; squaring is a bijection in characteristic 2."""
        return self.pow(a, self.size // 2)

    def trace(self, a: int) -> int:
        """Absolute trace to F_2: sum of a^(2^i) for i in [0, m)."""
        t, x = 0, a
        for _ in range(self.m):
            t ^= x
            x = self.sqr(x)
        if t not in (0, 1):
            raise ArithmeticError(f"trace left the prime field: {t}")
        return t

    def solve_quadratic(self, c: int) -> int | None:
        """z with z^2 + z = c, or None when no F_{2^m} solution exists.

        Solvable exactly when Tr(c) = 0. The map z -> z^2 + z is F_2-linear with
        kernel {0, 1}, so this is an ordinary linear system; solving it that way
        is valid for every m, where the half-trace shortcut needs m odd. Every
        returned root is verified before it leaves this function, which is the
        one place a wrong y could enter every count in the experiment.
        """
        if c == 0:
            return 0
        if self.trace(c) != 0:
            return None
        cols = [(self.sqr(1 << i) ^ (1 << i), 1 << i) for i in range(self.m)]
        target, combo = c, 0
        for bit in reversed(range(self.m)):
            pick = next((i for i, (v, _s) in enumerate(cols) if v >> bit & 1),
                        None)
            if pick is None:
                continue
            pvec, psrc = cols.pop(pick)
            cols = [(v ^ pvec, s ^ psrc) if v >> bit & 1 else (v, s)
                    for v, s in cols]
            if target >> bit & 1:
                target ^= pvec
                combo ^= psrc
        if target != 0:
            raise ArithmeticError("trace said solvable but the linear solve "
                                  "found no root")
        if self.sqr(combo) ^ combo != c:
            raise ArithmeticError("quadratic solve returned a non-root")
        return combo


class QuadraticExtension:
    """F_{q^2} = F_q[u]/(u^2 + u + delta) with Tr_{F_q}(delta) = 1.

    Elements are pairs (a, b) meaning a + b*u with a, b in F_q. F_q embeds as
    b = 0, so `in_base` is a comparison rather than a table lookup and the
    embedding is the inclusion rather than something that must be found.

    delta is chosen as the smallest element of F_q with absolute trace 1, which
    is exactly the condition making u^2 + u + delta irreducible over F_q.
    """

    is_extension = True

    def __init__(self, base: GF2m) -> None:
        self.base = base
        self.delta = next((d for d in range(1, base.size)
                           if base.trace(d) == 1), None)
        if self.delta is None:
            raise ArithmeticError("no element of trace 1; F_2-trace is onto, so "
                                  "this cannot happen for a valid field")
        self.zero = (0, 0)
        self.one = (1, 0)
        self.size = base.size * base.size

    def embed(self, v: int) -> tuple[int, int]:
        return (v, 0)

    def in_base(self, v: tuple[int, int]) -> bool:
        return v[1] == 0

    def pull_back(self, v: tuple[int, int]) -> int:
        if v[1] != 0:
            raise ValueError("element is not in the base field")
        return v[0]

    def add(self, x, y):
        return (x[0] ^ y[0], x[1] ^ y[1])

    def mul(self, x, y):
        f = self.base
        a, b = x
        c, d = y
        ac = f.mul(a, c)
        bd = f.mul(b, d)
        # (a + bu)(c + du) = ac + (ad + bc)u + bd u^2, and u^2 = u + delta.
        return (ac ^ f.mul(bd, self.delta), f.mul(a, d) ^ f.mul(b, c) ^ bd)

    def sqr(self, x):
        f = self.base
        a, b = x
        b2 = f.sqr(b)
        return (f.sqr(a) ^ f.mul(b2, self.delta), b2)

    def inv(self, x):
        f = self.base
        a, b = x
        if a == 0 and b == 0:
            raise ZeroDivisionError("inverse of zero in F_{q^2}")
        # Norm N(a + bu) = (a + bu)(a + b(u+1)) = a^2 + ab + b^2 delta, in F_q.
        norm = f.sqr(a) ^ f.mul(a, b) ^ f.mul(f.sqr(b), self.delta)
        if norm == 0:
            raise ArithmeticError("nonzero element of zero norm; the extension "
                                  "modulus is reducible")
        ninv = f.inv(norm)
        # Conjugate of a + bu is (a + b) + bu, since u -> u + 1.
        return (f.mul(a ^ b, ninv), f.mul(b, ninv))

    def div(self, x, y):
        return self.mul(x, self.inv(y))

    def solve_quadratic_over_base(self, c: int):
        """All z in F_{q^2} with z^2 + z = c, for c in the BASE field.

        Write z = z0 + z1 u. Then z^2 = z0^2 + z1^2 u^2 = z0^2 + z1^2(u + delta),
        so z^2 + z = (z0^2 + z1^2 delta + z0) + (z1^2 + z1) u. For the result to
        lie in F_q the u-part must vanish, so z1^2 = z1 and z1 is 0 or 1.

          z1 = 0 gives z0^2 + z0 = c,          solvable iff Tr(c) = 0
          z1 = 1 gives z0^2 + z0 = c + delta,  solvable iff Tr(c) = 1,
                                               since Tr(delta) = 1

        Exactly one branch fires, so every x on the curve contributes two
        y-values -- both in F_q, or both in F_{q^2} \\ F_q as a conjugate pair.
        That dichotomy is what the Lemma-2 accounting counts.
        """
        f = self.base
        tr = f.trace(c)
        if tr == 0:
            z0 = f.solve_quadratic(c)
            roots = [(z0, 0), (z0 ^ 1, 0)]
        else:
            z0 = f.solve_quadratic(c ^ self.delta)
            if z0 is None:
                raise ArithmeticError("Tr(c) = 1 but c + delta is not solvable; "
                                      "delta does not have trace 1")
            roots = [(z0, 1), (z0 ^ 1, 1)]
        for r in roots:
            if self.add(self.sqr(r), r) != self.embed(c):
                raise ArithmeticError("extension quadratic solve returned a "
                                      "non-root")
        return roots


INFINITY = None


class BinaryCurve:
    """E: y^2 + x y = x^3 + a x^2 + b, b != 0, over a supplied binary field.

    The affine equation Semaev works with (Section 2 of the frozen source). The
    field is injected rather than assumed, so the same class serves E(F_q) and
    E(F_{q^2}); `field.is_extension` is the only thing that differs. The point at
    infinity is the identity and is represented as None, which the contract's
    invalid_input control requires be REJECTED as a target R rather than counted.
    """

    def __init__(self, field, a, b) -> None:
        self.f = field
        self.a = a
        self.b = b
        if b == field.zero:
            raise ValueError("b = 0 is singular for this curve form")

    def is_on_curve(self, p) -> bool:
        if p is INFINITY:
            return True
        f = self.f
        x, y = p
        lhs = f.add(f.sqr(y), f.mul(x, y))
        rhs = f.add(f.add(f.mul(f.sqr(x), x), f.mul(self.a, f.sqr(x))), self.b)
        return lhs == rhs

    def negate(self, p):
        if p is INFINITY:
            return INFINITY
        x, y = p
        return (x, self.f.add(y, x))

    def add(self, p, q):
        if p is INFINITY:
            return q
        if q is INFINITY:
            return p
        f = self.f
        x1, y1 = p
        x2, y2 = q
        if x1 == x2:
            if f.add(y1, y2) == x1:
                return INFINITY                 # q == -p
            if y1 != y2:
                raise ArithmeticError("points share x but are neither equal "
                                      "nor negatives")
            if x1 == f.zero:
                return INFINITY                 # the unique 2-torsion point
            lam = f.add(x1, f.div(y1, x1))
            x3 = f.add(f.add(f.sqr(lam), lam), self.a)
            y3 = f.add(f.sqr(x1), f.mul(f.add(lam, f.one), x3))
            return (x3, y3)
        lam = f.div(f.add(y1, y2), f.add(x1, x2))
        x3 = f.add(f.add(f.add(f.add(f.sqr(lam), lam), x1), x2), self.a)
        y3 = f.add(f.add(f.mul(lam, f.add(x1, x3)), x3), y1)
        return (x3, y3)

    def mul_scalar(self, p, k: int):
        r, base = INFINITY, p
        while k:
            if k & 1:
                r = self.add(r, base)
            base = self.add(base, base)
            k >>= 1
        return r

    def rhs_quadratic_constant(self, x):
        """c with z^2 + z = c under y = x z; defined for x != 0.

        c = x + a + b/x^2. The trace of c decides whether the two y-values for
        this x lie in F_q or in F_{q^2} \\ F_q, which is the Lemma-2 dichotomy.
        """
        f = self.f
        if x == f.zero:
            raise ValueError("x = 0 has no y = xz substitution; handle it "
                             "separately (y^2 = b, one root)")
        return f.add(f.add(x, self.a), f.div(self.b, f.sqr(x)))

    def ys_for_x(self, x):
        """y-values in THIS field with (x, y) on the curve; [] if none."""
        f = self.f
        if x == f.zero:
            return [f.sqrt(self.b)] if not f.is_extension else \
                [self._ext_sqrt(self.b)]
        c = self.rhs_quadratic_constant(x)
        if f.is_extension:
            raise NotImplementedError("use ys_for_base_x on an extension curve")
        z = f.solve_quadratic(c)
        if z is None:
            return []
        y0 = f.mul(x, z)
        return [y0, f.add(y0, x)]

    def _ext_sqrt(self, v):
        f = self.f
        return f.pow(v, f.size // 2) if hasattr(f, "pow") else None

    def affine_points(self):
        out = []
        for x in range(self.f.size):
            out.extend((x, y) for y in self.ys_for_x(x))
        return out

    def order(self) -> int:
        return len(self.affine_points()) + 1
