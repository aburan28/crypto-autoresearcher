#!/usr/bin/env python3
"""
Lab 02 — Finite fields F_p and F_{p^2}.

Companion to course module 05. Run directly:

    python3 lab02_finite_fields.py

Builds the two fields the whole isogeny world lives in:

  * Fp   — the prime field Z/pZ,
  * Fp2  — the quadratic extension F_p(u) with u^2 = ns, ns a fixed
           quadratic non-residue mod p (ns = -1 whenever p = 3 mod 4,
           so elements print as a + b*i).

Both element classes implement the same interface (+ - * / ** == hash,
zero/one/random/sqrt/is_zero), so the elliptic-curve code in lab 03 works
over either field unchanged — the point of writing algebra generically.
"""

from __future__ import annotations

import random

from lab01_arithmetic import legendre, sqrt_mod_p, is_probable_prime


# ----------------------------------------------------------------------
# F_p
# ----------------------------------------------------------------------

class Fp:
    """An element of the prime field F_p = Z/pZ."""

    __slots__ = ("p", "v")

    def __init__(self, p: int, v: int):
        self.p = p
        self.v = v % p

    # -- constructors for "the same field as self" ------------------------
    def zero(self) -> "Fp":
        return Fp(self.p, 0)

    def one(self) -> "Fp":
        return Fp(self.p, 1)

    def random(self, rng: random.Random) -> "Fp":
        return Fp(self.p, rng.randrange(self.p))

    # -- predicates -------------------------------------------------------
    def is_zero(self) -> bool:
        return self.v == 0

    # -- arithmetic -------------------------------------------------------
    def _coerce(self, other):
        if isinstance(other, Fp):
            if other.p != self.p:
                raise ValueError("mixed fields")
            return other
        if isinstance(other, int):
            return Fp(self.p, other)
        return NotImplemented

    def __add__(self, other):
        o = self._coerce(other)
        return NotImplemented if o is NotImplemented else Fp(self.p, self.v + o.v)

    __radd__ = __add__

    def __sub__(self, other):
        o = self._coerce(other)
        return NotImplemented if o is NotImplemented else Fp(self.p, self.v - o.v)

    def __rsub__(self, other):
        o = self._coerce(other)
        return NotImplemented if o is NotImplemented else Fp(self.p, o.v - self.v)

    def __mul__(self, other):
        o = self._coerce(other)
        return NotImplemented if o is NotImplemented else Fp(self.p, self.v * o.v)

    __rmul__ = __mul__

    def __neg__(self):
        return Fp(self.p, -self.v)

    def inverse(self) -> "Fp":
        return Fp(self.p, pow(self.v, self.p - 2, self.p))  # Fermat

    def __truediv__(self, other):
        o = self._coerce(other)
        return NotImplemented if o is NotImplemented else self * o.inverse()

    def __rtruediv__(self, other):
        o = self._coerce(other)
        return NotImplemented if o is NotImplemented else o * self.inverse()

    def __pow__(self, e: int) -> "Fp":
        if e < 0:
            return self.inverse() ** (-e)
        return Fp(self.p, pow(self.v, e, self.p))

    # -- structure --------------------------------------------------------
    def frobenius(self) -> "Fp":
        """x -> x^p is the identity on F_p (Fermat's little theorem)."""
        return self

    def is_square(self) -> bool:
        return self.v == 0 or legendre(self.v, self.p) == 1

    def sqrt(self) -> "Fp | None":
        r = sqrt_mod_p(self.v, self.p)
        return None if r is None else Fp(self.p, r)

    # -- plumbing ---------------------------------------------------------
    def __eq__(self, other):
        o = self._coerce(other)
        return NotImplemented if o is NotImplemented else self.v == o.v

    def __hash__(self):
        return hash(("Fp", self.p, self.v))

    def __repr__(self):
        return f"{self.v}"


# ----------------------------------------------------------------------
# F_{p^2}
# ----------------------------------------------------------------------

_NONRESIDUE_CACHE: dict[int, int] = {}


def quadratic_nonresidue(p: int) -> int:
    """A fixed quadratic non-residue mod p, used as u^2 when building
    F_{p^2} = F_p[u]/(u^2 - ns). We prefer -1 (i.e. p-1) when p = 3 mod 4
    so that F_{p^2} looks like the familiar 'complex numbers mod p'."""
    if p not in _NONRESIDUE_CACHE:
        if p % 4 == 3:
            _NONRESIDUE_CACHE[p] = p - 1
        else:
            n = 2
            while legendre(n, p) != -1:
                n += 1
            _NONRESIDUE_CACHE[p] = n
    return _NONRESIDUE_CACHE[p]


class Fp2:
    """An element a + b*u of F_{p^2} = F_p[u]/(u^2 - ns)."""

    __slots__ = ("p", "ns", "a", "b")

    def __init__(self, p: int, a: int, b: int = 0, ns: int | None = None):
        self.p = p
        self.ns = quadratic_nonresidue(p) if ns is None else ns
        self.a = a % p
        self.b = b % p

    # -- constructors -----------------------------------------------------
    def zero(self) -> "Fp2":
        return Fp2(self.p, 0, 0, self.ns)

    def one(self) -> "Fp2":
        return Fp2(self.p, 1, 0, self.ns)

    def random(self, rng: random.Random) -> "Fp2":
        return Fp2(self.p, rng.randrange(self.p), rng.randrange(self.p), self.ns)

    # -- predicates -------------------------------------------------------
    def is_zero(self) -> bool:
        return self.a == 0 and self.b == 0

    def in_prime_field(self) -> bool:
        return self.b == 0

    # -- arithmetic -------------------------------------------------------
    def _coerce(self, other):
        if isinstance(other, Fp2):
            if other.p != self.p or other.ns != self.ns:
                raise ValueError("mixed fields")
            return other
        if isinstance(other, int):
            return Fp2(self.p, other, 0, self.ns)
        return NotImplemented

    def __add__(self, other):
        o = self._coerce(other)
        if o is NotImplemented:
            return NotImplemented
        return Fp2(self.p, self.a + o.a, self.b + o.b, self.ns)

    __radd__ = __add__

    def __sub__(self, other):
        o = self._coerce(other)
        if o is NotImplemented:
            return NotImplemented
        return Fp2(self.p, self.a - o.a, self.b - o.b, self.ns)

    def __rsub__(self, other):
        o = self._coerce(other)
        return NotImplemented if o is NotImplemented else o - self

    def __mul__(self, other):
        o = self._coerce(other)
        if o is NotImplemented:
            return NotImplemented
        # (a + b u)(c + d u) = (ac + bd*ns) + (ad + bc) u
        p = self.p
        return Fp2(p,
                   self.a * o.a + self.b * o.b % p * self.ns,
                   self.a * o.b + self.b * o.a,
                   self.ns)

    __rmul__ = __mul__

    def __neg__(self):
        return Fp2(self.p, -self.a, -self.b, self.ns)

    def conjugate(self) -> "Fp2":
        """a - b*u. This IS the Frobenius x -> x^p (see frobenius())."""
        return Fp2(self.p, self.a, -self.b, self.ns)

    def norm(self) -> int:
        """N(a + b u) = (a + b u)(a - b u) = a^2 - ns*b^2 in F_p."""
        return (self.a * self.a - self.ns * self.b * self.b) % self.p

    def inverse(self) -> "Fp2":
        n = self.norm()
        if n == 0:
            raise ZeroDivisionError("inverse of 0 in Fp2")
        n_inv = pow(n, self.p - 2, self.p)
        return Fp2(self.p, self.a * n_inv, -self.b * n_inv, self.ns)

    def __truediv__(self, other):
        o = self._coerce(other)
        return NotImplemented if o is NotImplemented else self * o.inverse()

    def __rtruediv__(self, other):
        o = self._coerce(other)
        return NotImplemented if o is NotImplemented else o * self.inverse()

    def __pow__(self, e: int) -> "Fp2":
        if e < 0:
            return self.inverse() ** (-e)
        result, base = self.one(), self
        while e:
            if e & 1:
                result = result * base
            base = base * base
            e >>= 1
        return result

    # -- structure --------------------------------------------------------
    def frobenius(self) -> "Fp2":
        """x -> x^p, the nontrivial automorphism of F_{p^2}/F_p.
        u^p = u * (u^2)^((p-1)/2) = u * ns^((p-1)/2) = -u since ns is a
        non-residue, so (a + b u)^p = a - b u: conjugation."""
        return self.conjugate()

    def is_square(self) -> bool:
        """Euler's criterion in F_{p^2}: x is a square iff
        x^((p^2-1)/2) = 1 (or x = 0)."""
        if self.is_zero():
            return True
        return self ** ((self.p * self.p - 1) // 2) == self.one()

    def sqrt(self, rng: random.Random | None = None) -> "Fp2 | None":
        """Square root by generic Tonelli-Shanks in the cyclic group
        F_{p^2}^* of order p^2 - 1. Needs a non-square of F_{p^2}, found
        by (seeded) random search — note every element of F_p is a square
        in F_{p^2}, so we must search genuinely quadratic elements."""
        if self.is_zero():
            return self
        if not self.is_square():
            return None
        rng = rng or random.Random(0xC0FFEE)
        q = self.p * self.p
        z = self.random(rng)
        while z.is_zero() or z.is_square():
            z = self.random(rng)
        # Tonelli-Shanks with group order q - 1 = Q * 2^S.
        Q, S = q - 1, 0
        while Q % 2 == 0:
            Q //= 2
            S += 1
        one = self.one()
        m = S
        c = z ** Q
        t = self ** Q
        r = self ** ((Q + 1) // 2)
        while t != one:
            i, t2 = 0, t
            while t2 != one:
                t2 = t2 * t2
                i += 1
            b = c ** (1 << (m - i - 1))
            m = i
            c = b * b
            t = t * c
            r = r * b
        return r

    # -- plumbing ---------------------------------------------------------
    def __eq__(self, other):
        o = self._coerce(other)
        if o is NotImplemented:
            return NotImplemented
        return self.a == o.a and self.b == o.b

    def __hash__(self):
        return hash(("Fp2", self.p, self.ns, self.a, self.b))

    def __repr__(self):
        sym = "i" if self.ns == self.p - 1 else "u"
        if self.b == 0:
            return f"{self.a}"
        if self.a == 0:
            return f"{self.b}*{sym}"
        return f"{self.a}+{self.b}*{sym}"


# ----------------------------------------------------------------------
# Self-checks and demo
# ----------------------------------------------------------------------

def _selfcheck() -> None:
    rng = random.Random(2)

    for p in (11, 431, 1013):
        assert is_probable_prime(p)
        one = Fp(p, 1)
        for _ in range(100):
            x, y, z = (one.random(rng) for _ in range(3))
            assert (x + y) * z == x * z + y * z          # distributivity
            if not x.is_zero():
                assert (x * x.inverse()).v == 1
            assert x ** (p - 1) == one or x.is_zero()    # Fermat
        # sqrt round-trip in F_p
        for _ in range(50):
            x = one.random(rng)
            s = (x * x).sqrt()
            assert s is not None and s * s == x * x

    for p in (431, 1013):  # 431 = 3 mod 4, 1013 = 1 mod 4: both u^2 branches
        one2 = Fp2(p, 1)
        q = p * p
        for _ in range(100):
            x, y, z = (one2.random(rng) for _ in range(3))
            assert (x + y) * z == x * z + y * z
            assert x * y == y * x
            if not x.is_zero():
                assert x * x.inverse() == one2
                assert x ** (q - 1) == one2              # Lagrange in F_{p^2}^*
            # Frobenius is a field automorphism of order 2 fixing F_p.
            assert (x * y).frobenius() == x.frobenius() * y.frobenius()
            assert (x + y).frobenius() == x.frobenius() + y.frobenius()
            assert x.frobenius().frobenius() == x
        # Every element of F_p becomes a square in F_{p^2}.
        for a in range(1, 30):
            assert Fp2(p, a).is_square()
        # sqrt round-trip in F_{p^2}
        for _ in range(25):
            x = one2.random(rng)
            s = (x * x).sqrt(rng)
            assert s is not None and s * s == x * x
        # Exactly half of F_{p^2}^* are squares: spot-check the criterion
        # against explicit squaring on a small sample.
        sample = [one2.random(rng) for _ in range(20)]
        sq_set = {x * x for x in sample}
        assert all(s.is_square() for s in sq_set)
    print("lab02: all self-checks passed")


def _demo() -> None:
    p = 431
    print(f"\n-- demo: F_{{{p}^2}} = F_{p}(i), i^2 = -1 --")
    x = Fp2(p, 3, 5)
    y = Fp2(p, 7, 2)
    print(f"x = {x}, y = {y}")
    print(f"x + y = {x + y}")
    print(f"x * y = {x * y}")
    print(f"x^-1  = {x.inverse()}   (check x * x^-1 = {x * x.inverse()})")
    print(f"x^p   = {x.frobenius()}   (Frobenius = conjugation)")
    print(f"N(x)  = {x.norm()}   (an element of F_{p})")
    s = (x * x).sqrt()
    print(f"sqrt(x^2) = {s}  (+/- x = {x} / {-x})")
    print(f"is 2 a square in F_{p}?   {Fp(p, 2).is_square()}")
    print(f"is 2 a square in F_{p}^2? {Fp2(p, 2).is_square()}  "
          "(every F_p element is)")
    # EXERCISE 2.1: for p = 1013 (p = 1 mod 4), what is u^2? Print
    #   quadratic_nonresidue(1013) and verify it is a non-square with
    #   legendre().
    # EXERCISE 2.2: verify that the map x -> x^(p+1) sends F_{p^2}^* onto
    #   F_p^* (it is the norm map). Sample random x and check x^(p+1)
    #   equals x.norm().


if __name__ == "__main__":
    _selfcheck()
    _demo()
