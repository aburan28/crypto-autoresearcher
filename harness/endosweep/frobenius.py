"""Frobenius-adic scalar expansions on ordinary subfield curves over F_q, q in {2, 3, 4}.

``binary.py`` covers the Koblitz curves over F_2 (Solinas' width-w tau-adic
NAF).  This module asks the same question one step up: an ordinary curve E
defined over a small field F_q, used over F_{q^m} with m prime, has the
q-power Frobenius phi(x, y) = (x^q, y^q) as an endomorphism with
phi^2 - t phi + q = 0 (t = q + 1 - #E(F_q)).  A scalar k is replaced by
rho = k mod delta, delta = (phi^m - 1)/(phi - 1) in Z[phi], and rho is
written in base phi.  The m doublings of a binary method become about m
Frobenius maps (linear maps of the coordinates), and the work left is the
additions.

What is here, and what each piece proves:

* ``Zphi``: exact arithmetic in Z[phi] (norm, conjugate, rounding, division
  by phi, reduction modulo delta).
* ``families``: every ordinary curve over F_3 and F_4 enumerated by brute
  force, giving the traces t that occur (and an example curve for each).
* ``search``: for each (q, t) and every prime m in a range, the group order
  from the Lucas sequence of the trace, #E(F_{q^m}) = q^m + 1 - V_m, and
  n = #E(F_{q^m}) / #E(F_q) tested with sympy's ``isprime`` -- a BPSW
  probable-prime test above 2^64, *not* a primality proof.  N(delta) = n is
  checked exactly.  Small embedding degrees (q^{mk} = 1 mod n, k <= 50) are
  checked and reported.
* ``digit_set`` / ``expand``: the width-w Frobenius expansion.  Digits are 0
  or the minimal-norm representative alpha_u of a residue class u modulo
  phi^w that phi does not divide; Z[phi]/(phi^w) = Z/q^w because phi and its
  conjugate are coprime on an ordinary curve.  w = 1 is the minimal digit
  set (q residues modulo phi, |D| = q); for q = 2 the width w is Solinas'.
* ``termination_certificate``: a proof that the expansion terminates for
  every input with a given digit set -- every rho with |rho| > B = D/(sqrt q
  - 1) (D the largest digit modulus) strictly shrinks, the disc |rho| <= B is
  invariant, and every lattice point of that disc is run to 0.
* ``Char3Field`` / ``Char3Curve``: F_{3^m} in a trinomial polynomial basis
  with counted multiplications, squarings, cubings (linear) and Itoh-Tsujii
  inversions; y^2 = x^3 + a2 x^2 + a6 (the ordinary char-3 form) in affine
  coordinates (reference) and projective coordinates (counted mixed
  addition 10M + 2S, derived in ``madd``).  For q = 4 the curves live in
  ``binary.Field`` of degree 2m and ``binary.BinaryCurve`` (Lopez-Dahab).
* ``mul_counted``: one scalar multiplication algorithm (table of alpha_u P,
  one batched inversion, Horner with Frobenius and mixed additions), run
  either on real arithmetic (``Char2Ops``, ``Char3Ops``) or on a counting
  stub (``StubOps``) that charges each operation its formula count.  On the
  verification instances the real counts and the stub counts are compared
  per scalar; on the 160-300-bit instances only the stub runs, so those
  costs are *modelled* (formula counts x measured digit statistics).

    python -m harness.endosweep.frobenius --out-dir research/endosweep_frob_blinding_20261008
"""
from __future__ import annotations

import argparse
import json
import os
import random
import time
from array import array
from dataclasses import dataclass
from fractions import Fraction
from math import floor, log2, sqrt

from . import binary as BI
from . import costmodel as CM

# ---------------------------------------------------------------------------
# Z[phi], phi^2 = t phi - q
# ---------------------------------------------------------------------------


class Zphi:
    """Elements a + b phi as pairs (a, b); N(a + b phi) = a^2 + t a b + q b^2 = |a + b phi|^2."""

    def __init__(self, q: int, t: int):
        if t * t >= 4 * q:
            raise ValueError("phi must be imaginary quadratic (|t| < 2 sqrt q)")
        if t % _char(q) == 0:
            raise ValueError("supersingular trace (p | t): excluded")
        self.q, self.t = q, t

    def mul(self, x, y):
        a, b = x
        c, d = y
        return (a * c - self.q * b * d, a * d + b * c + self.t * b * d)

    def conj(self, x):
        a, b = x
        return (a + self.t * b, -b)

    def norm(self, x) -> int:
        a, b = x
        return a * a + self.t * a * b + self.q * b * b

    def power(self, x, e: int):
        r = (1, 0)
        for bit in bin(e)[2:]:
            r = self.mul(r, r)
            if bit == "1":
                r = self.mul(r, x)
        return r

    def _qnorm(self, x0: Fraction, x1: Fraction) -> Fraction:
        return x0 * x0 + self.t * x0 * x1 + self.q * x1 * x1

    def round(self, l0: Fraction, l1: Fraction):
        """The element nearest to l0 + l1 phi: the 9 neighbours first (binary.Ztau's order), then a 5x5 box."""
        f0, f1 = floor(l0 + Fraction(1, 2)), floor(l1 + Fraction(1, 2))
        offs = [(i, j) for i in (-1, 0, 1) for j in (-1, 0, 1)]
        offs += [(i, j) for i in range(-2, 3) for j in range(-2, 3) if max(abs(i), abs(j)) == 2]
        best = None
        for i, j in offs:
            c = (f0 + i, f1 + j)
            d = self._qnorm(l0 - c[0], l1 - c[1])
            if best is None or d < best[0]:
                best = (d, c)
        return best[1]

    def reduce_mod(self, x, delta):
        """x - round(x / delta) delta: a small representative of x modulo delta."""
        num = self.mul(x, self.conj(delta))
        N = self.norm(delta)
        k = self.round(Fraction(num[0], N), Fraction(num[1], N))
        kd = self.mul(k, delta)
        return (x[0] - kd[0], x[1] - kd[1])

    def div_phi(self, x):
        """x / phi for phi | x (q | a): (a + b phi) conj(phi) / q = (a t / q + b) - (a / q) phi."""
        a, b = x
        if a % self.q:
            raise ArithmeticError("phi does not divide x")
        a //= self.q
        return (a * self.t + b, -a)

    def delta(self, m: int):
        """(phi^m - 1) / (phi - 1), exactly."""
        pm = self.power((0, 1), m)
        num = self.mul((pm[0] - 1, pm[1]), self.conj((-1, 1)))
        N1 = self.norm((-1, 1))
        if num[0] % N1 or num[1] % N1:
            raise ArithmeticError("phi - 1 does not divide phi^m - 1")
        return (num[0] // N1, num[1] // N1)


def _char(q: int) -> int:
    for p in (2, 3, 5, 7):
        if q % p == 0:
            return p
    raise ValueError("q must be a small prime power")


# ---------------------------------------------------------------------------
# digit sets and expansions
# ---------------------------------------------------------------------------

@dataclass
class DigitSet:
    q: int
    t: int
    w: int
    s_w: int                                 # phi = s_w (mod phi^w), an integer mod q^w
    alpha: dict                              # u > 0 -> alpha_u = (a, b), alpha_u = u (mod phi^w), minimal norm

    @property
    def table_size(self) -> int:
        """Points alpha_u P stored (u > 0; -u is the negative)."""
        return len(self.alpha)

    @property
    def max_digit_norm(self) -> int:
        Z = Zphi(self.q, self.t)
        return max(Z.norm(a) for a in self.alpha.values())


def lucas_U(q: int, t: int, k: int) -> int:
    """U_0 = 0, U_1 = 1, U_j = t U_(j-1) - q U_(j-2): phi^j = U_j phi - q U_(j-1)."""
    u0, u1 = 0, 1
    if k == 0:
        return 0
    for _ in range(k - 1):
        u0, u1 = u1, t * u1 - q * u0
    return u1


def lucas_V(q: int, t: int, m: int) -> int:
    """V_m = phi^m + conj(phi)^m: V_0 = 2, V_1 = t, V_j = t V_(j-1) - q V_(j-2)."""
    v0, v1 = 2, t
    if m == 0:
        return 2
    for _ in range(m - 1):
        v0, v1 = v1, t * v1 - q * v0
    return v1


def digit_set(q: int, t: int, w: int) -> DigitSet:
    Z = Zphi(q, t)
    mod = q ** w
    Uw, Uw1 = lucas_U(q, t, w), lucas_U(q, t, w - 1)
    s_w = q * Uw1 * pow(Uw, -1, mod) % mod
    phiw = Z.power((0, 1), w)
    # check: phi - s_w is divisible by phi^w
    num = Z.mul((-s_w, 1), Z.conj(phiw))
    if num[0] % mod or num[1] % mod:
        raise ArithmeticError("s_w is not phi mod phi^w")
    alpha = {}
    for u in range(1, mod // 2 + 1):
        if u % q:
            alpha[u] = Z.reduce_mod((u, 0), phiw)
    return DigitSet(q, t, w, s_w, alpha)


def expand(ds: DigitSet, rho) -> list[int]:
    """Width-w Frobenius expansion of rho, least significant first: 0 or a signed class u (digit sign * alpha_|u|)."""
    q, t = ds.q, ds.t
    mod = q ** ds.w
    half = mod // 2
    a, b = rho
    out = []
    while a or b:
        if a % q:
            u = (a + b * ds.s_w) % mod
            if u > half:
                u -= mod
            al = ds.alpha[abs(u)]
            if u > 0:
                a, b = a - al[0], b - al[1]
            else:
                a, b = a + al[0], b + al[1]
            out.append(u)
        else:
            out.append(0)
        a //= q                                  # exact: q | a here
        a, b = a * t + b, -a
    return out


def evaluate(ds: DigitSet, digits: list[int]):
    """sum d_i phi^i in Z[phi] (Horner): the inverse of ``expand``."""
    Z = Zphi(ds.q, ds.t)
    r = (0, 0)
    for u in reversed(digits):
        r = Z.mul(r, (0, 1))
        if u:
            al = ds.alpha[abs(u)]
            r = (r[0] + al[0], r[1] + al[1]) if u > 0 else (r[0] - al[0], r[1] - al[1])
    return r


def termination_certificate(ds: DigitSet) -> dict:
    """Prove that ``expand`` terminates on every input (see the module docstring)."""
    q, t = ds.q, ds.t
    D = sqrt(ds.max_digit_norm)
    B2 = (D / (sqrt(q) - 1)) ** 2 * 1.0001 + 1.0
    c = q - t * t / 4.0                        # N = (a + t b / 2)^2 + c b^2
    bmax = int(sqrt(B2 / c)) + 1
    pts = []
    for b in range(-bmax, bmax + 1):
        rem = B2 - c * b * b
        if rem < 0:
            continue
        r = sqrt(rem)
        lo, hi = int(floor(-t * b / 2 - r)) - 1, int(floor(-t * b / 2 + r)) + 1
        for a in range(lo, hi + 1):
            if a * a + t * a * b + q * b * b <= B2:
                pts.append((a, b))
    mod = q ** ds.w
    half = mod // 2
    length: dict = {(0, 0): 0}

    def step(x):
        a, b = x
        if a % q:
            u = (a + b * ds.s_w) % mod
            if u > half:
                u -= mod
            al = ds.alpha[abs(u)]
            a, b = (a - al[0], b - al[1]) if u > 0 else (a + al[0], b + al[1])
        a //= q
        return (a * t + b, -a)

    ok = True
    for p in pts:
        path = []
        on_path = set()
        x = p
        while x not in length:
            if x in on_path:
                ok = False
                break
            on_path.add(x)
            path.append(x)
            x = step(x)
        if not ok:
            break
        L = length[x]
        for y in reversed(path):
            L += 1
            length[y] = L
    return {"disc_radius_sq": round(B2, 3), "lattice_points": len(pts), "all_terminate": ok,
            "max_length_in_disc": max(length.values()) if ok else None}


# ---------------------------------------------------------------------------
# curves over F_q: which traces occur
# ---------------------------------------------------------------------------

def _count_char3(a2: int, a4: int, a6: int) -> int:
    n = 1
    for x in range(3):
        for y in range(3):
            if (y * y - (x ** 3 + a2 * x * x + a4 * x + a6)) % 3 == 0:
                n += 1
    return n


def _f4():
    return BI.Field(2, (1, 0))                     # F_2[w]/(w^2 + w + 1): 0, 1, w = 2, w^2 = 3


def _count_char2_f4(a: int, b: int) -> int:
    F = _f4()
    n = 1
    for x in range(4):
        for y in range(4):
            lhs = F.sqr(y) ^ F.mul(x, y)
            x2 = F.sqr(x)
            rhs = F.mul(x2, x) ^ F.mul(a, x2) ^ b
            if lhs == rhs:
                n += 1
    return n


def families() -> dict:
    """Every ordinary curve over F_2 (Koblitz form), F_3 and F_4, by brute force: trace -> example curves."""
    out: dict = {2: {}, 3: {}, 4: {}}
    for a in (0, 1):
        t = 2 + 1 - (4 if a == 0 else 2)            # #E(F_2) = 4 (a = 0), 2 (a = 1); mu = (-1)^(1-a)
        out[2].setdefault(t, []).append({"form": "y^2 + xy = x^3 + a x^2 + 1", "a": a})
    # char 3: y^2 = x^3 + a2 x^2 + a4 x + a6, nonsingular; ordinary iff 3 does not divide t
    for a2 in range(3):
        for a4 in range(3):
            for a6 in range(3):
                # discriminant of x^3 + a2 x^2 + a4 x + a6 nonzero (char 3: b2 = 4a2, etc.)
                b2, b4, b6 = (4 * a2) % 3, (2 * a4) % 3, (4 * a6) % 3
                b8 = (a2 * 4 * a6 - a4 * a4) % 3            # b8 = a1^2 a6 + 4 a2 a6 - a1 a3 a4 + a2 a3^2 - a4^2
                disc = (-b2 * b2 * b8 - 8 * b4 ** 3 - 27 * b6 * b6 + 9 * b2 * b4 * b6) % 3
                if disc == 0:
                    continue
                t = 3 + 1 - _count_char3(a2, a4, a6)
                if t % 3 == 0:
                    continue
                out[3].setdefault(t, []).append({"form": "y^2 = x^3 + a2 x^2 + a4 x + a6", "a2": a2, "a4": a4, "a6": a6})
    # char 2 over F_4: y^2 + xy = x^3 + a x^2 + b, b != 0 (every such curve is ordinary)
    for a in range(4):
        for b in range(1, 4):
            t = 4 + 1 - _count_char2_f4(a, b)
            out[4].setdefault(t, []).append({"form": "y^2 + xy = x^3 + a x^2 + b over F_4 = F_2[w]/(w^2+w+1)",
                                             "a": a, "b": b})
    return out


# ---------------------------------------------------------------------------
# the search for prime-order instances
# ---------------------------------------------------------------------------

def _primes(lo: int, hi: int) -> list[int]:
    from sympy import primerange
    return list(primerange(lo, hi + 1))


@dataclass
class Instance:
    q: int
    t: int
    m: int
    h: int                       # #E(F_q)
    n: int                       # #E(F_{q^m}) / #E(F_q), probable prime
    delta: tuple                 # (phi^m - 1)/(phi - 1), N(delta) = n

    @property
    def bits(self) -> float:
        return log2(self.n)

    @property
    def field_bits(self) -> float:
        return self.m * log2(self.q)


def instance(q: int, t: int, m: int) -> Instance | None:
    """The instance (q, t, m) if n = #E(F_{q^m})/#E(F_q) is a probable prime, else None."""
    from sympy import isprime
    h = q + 1 - t
    N = q ** m + 1 - lucas_V(q, t, m)
    if N % h:
        raise ArithmeticError("#E(F_q) does not divide #E(F_{q^m})")
    n = N // h
    if not isprime(n):
        return None
    Z = Zphi(q, t)
    d = Z.delta(m)
    if Z.norm(d) != n:
        raise ArithmeticError("N(delta) != n")
    return Instance(q, t, m, h, n, d)


def small_embedding_degree(inst: Instance, kmax: int = 50) -> int | None:
    Q = pow(inst.q, inst.m, inst.n)
    x = 1
    for k in range(1, kmax + 1):
        x = x * Q % inst.n
        if x == 1:
            return k
    return None


def search(q: int, t: int, m_lo: int, m_hi: int) -> list[Instance]:
    return [I for m in _primes(m_lo, m_hi) if (I := instance(q, t, m)) is not None]


# ---------------------------------------------------------------------------
# F_{3^m} and y^2 = x^3 + a2 x^2 + a6, counted
# ---------------------------------------------------------------------------

def find_trinomial_f3(m: int) -> tuple[int, int, int]:
    """(k, c1, c0) with x^m + c1 x^k + c0 irreducible over F_3 (smallest k)."""
    from sympy import Poly, symbols
    x = symbols("x")
    for k in range(1, m):
        for c1 in (1, 2):
            for c0 in (1, 2):
                if Poly(x ** m + c1 * x ** k + c0, x, modulus=3).is_irreducible:
                    return k, c1, c0
    raise ValueError(f"no irreducible trinomial of degree {m} over F_3")


class Char3Field:
    """F_3[x]/(x^m + c1 x^k + c0); elements are tuples of m coefficients in {0, 1, 2}.

    Multiplication is Kronecker substitution (16-bit slots, exact for m < 16384)
    followed by reduction; a cube is the linear map sum a_i x^(3i); an inverse
    is Itoh-Tsujii, a^(-1) = a^(r-1) / a^r with r = (3^m - 1)/2 and a^r in F_3,
    counted as the cubes and multiplications it performs.
    """

    def __init__(self, m: int, k: int, c1: int, c0: int):
        self.m, self.k, self.c1, self.c0 = m, k, c1 % 3, c0 % 3
        self.zero = (0,) * m
        self.one = (1,) + (0,) * (m - 1)
        self.reset()

    def reset(self):
        self.M = self.S = self.C = self.I = 0

    def counts(self) -> dict:
        return {"M": self.M, "S": self.S, "C": self.C, "I": self.I}

    def const(self, c: int):
        return ((c % 3),) + (0,) * (self.m - 1)

    def _reduce(self, r: list):
        m, k, c1, c0 = self.m, self.k, self.c1, self.c0
        for i in range(len(r) - 1, m - 1, -1):
            c = r[i] % 3
            if c:
                r[i - m + k] = (r[i - m + k] - c * c1) % 3
                r[i - m] = (r[i - m] - c * c0) % 3
        return tuple(x % 3 for x in r[:m])

    @staticmethod
    def _pack(a) -> int:
        return int.from_bytes(array("H", a).tobytes(), "little")

    def _mul(self, a, b):
        P = self._pack(a) * self._pack(b)
        slots = array("H")
        slots.frombytes(P.to_bytes(4 * self.m, "little"))
        return self._reduce(list(slots))

    def add(self, a, b):
        return tuple((x + y) % 3 for x, y in zip(a, b))

    def sub(self, a, b):
        return tuple((x - y) % 3 for x, y in zip(a, b))

    def neg(self, a):
        return tuple((-x) % 3 for x in a)

    def scale(self, c: int, a):
        """Multiplication by a constant of F_3: free (a negation at most)."""
        c %= 3
        return a if c == 1 else (self.zero if c == 0 else self.neg(a))

    def mul(self, a, b):
        self.M += 1
        return self._mul(a, b)

    def sqr(self, a):
        self.S += 1
        return self._mul(a, a)

    def cube(self, a):
        self.C += 1
        r = [0] * (3 * self.m - 2)
        for i, x in enumerate(a):
            if x:
                r[3 * i] = x
        return self._reduce(r)

    def inv(self, a):
        if a == self.zero:
            raise ZeroDivisionError("0 has no inverse")
        self.I += 1
        bits = bin(self.m - 1)[2:]
        b, k = a, 1                                  # b = a^((3^k - 1)/2)
        for bit in bits[1:]:
            tt = b
            for _ in range(k):
                tt = self.cube(tt)
            b, k = self.mul(tt, b), 2 * k
            if bit == "1":
                b, k = self.mul(self.cube(b), a), k + 1
        c = self.cube(b)                             # a^(r - 1)
        ar = self.mul(a, c)                          # a^r, in F_3
        if any(ar[1:]) or ar[0] == 0:
            raise ArithmeticError("a^r is not in F_3^*")
        return self.scale(ar[0], c)                  # 1/1 = 1, 1/2 = 2 in F_3

    def pow(self, a, e: int):
        """Uncounted exponentiation (used only to find points)."""
        r = self.one
        for bit in bin(e)[2:]:
            r = self._mul(r, r)
            if bit == "1":
                r = self._mul(r, a)
        return r

    def sqrt(self, a):
        """For odd m: a^((3^m + 1)/4), or None when a is not a square."""
        if self.m % 2 == 0:
            raise ValueError("sqrt needs odd m")
        s = self.pow(a, (3 ** self.m + 1) // 4)
        return s if self._mul(s, s) == a else None

    def random(self, rng: random.Random):
        return tuple(rng.randrange(3) for _ in range(self.m))


INF = None


class Char3Curve:
    """y^2 = x^3 + a2 x^2 + a6 over F_{3^m}, a2, a6 in F_3^* (ordinary: a2 != 0)."""

    def __init__(self, F: Char3Field, a2: int, a6: int):
        if a2 % 3 == 0 or a6 % 3 == 0:
            raise ValueError("a2 = 0 is supersingular, a6 = 0 singular")
        self.F, self.a2, self.a6 = F, a2 % 3, a6 % 3

    def rhs(self, x):
        F = self.F
        x2 = F._mul(x, x)
        return F.add(F.add(F._mul(x2, x), F.scale(self.a2, x2)), F.const(self.a6))

    def on_curve(self, P) -> bool:
        if P is INF:
            return True
        return self.F._mul(P[1], P[1]) == self.rhs(P[0])

    def neg(self, P):
        return INF if P is INF else (P[0], self.F.neg(P[1]))

    # affine reference (uncounted intent: callers reset the counters)
    def add(self, P, Q):
        F = self.F
        if P is INF:
            return Q
        if Q is INF:
            return P
        if P[0] == Q[0]:
            return self.dbl(P) if P[1] == Q[1] else INF
        lam = F.mul(F.sub(Q[1], P[1]), F.inv(F.sub(Q[0], P[0])))
        x3 = F.sub(F.sub(F.sub(F.sqr(lam), F.const(self.a2)), P[0]), Q[0])
        return (x3, F.sub(F.mul(lam, F.sub(P[0], x3)), P[1]))

    def dbl(self, P):
        """lambda = (3x^2 + 2 a2 x)/(2y) = a2 x / y in characteristic 3."""
        F = self.F
        if P is INF or P[1] == F.zero:
            return INF
        lam = F.mul(F.scale(self.a2, P[0]), F.inv(P[1]))
        x3 = F.add(F.sub(F.sqr(lam), F.const(self.a2)), P[0])         # lam^2 - a2 - 2x, -2 = 1
        return (x3, F.sub(F.mul(lam, F.sub(P[0], x3)), P[1]))

    def mul_affine(self, k: int, P):
        if k < 0:
            return self.mul_affine(-k, self.neg(P))
        R = INF
        for bit in bin(k)[2:]:
            R = self.dbl(R)
            if bit == "1":
                R = self.add(R, P)
        return R

    def frobenius(self, P):
        return INF if P is INF else (self.F.cube(P[0]), self.F.cube(P[1]))

    def random_point(self, rng: random.Random):
        while True:
            x = self.F.random(rng)
            y = self.F.sqrt(self.rhs(x))
            if y is not None:
                return (x, y)

    # projective (X : Y : Z), x = X/Z, y = Y/Z
    def proj(self, P):
        return INF if P is INF else (P[0], P[1], self.F.one)

    def madd(self, P, Q):
        """(X1:Y1:Z1) + (x2, y2): 10M + 2S.

        u = y2 Z1 - Y1, v = x2 Z1 - X1, lambda = u/v;
        x3 v^2 Z1 = u^2 Z1 - a2 v^2 Z1 - 2 v^2 X1 - v^3 =: A;
        X3 = v A, Z3 = v^3 Z1, Y3 = u (v^2 X1 - A) - v^3 Y1.
        """
        F = self.F
        if P is INF:
            return self.proj(Q)
        if Q is INF:
            return P
        X1, Y1, Z1 = P
        x2, y2 = Q
        u = F.sub(F.mul(y2, Z1), Y1)
        v = F.sub(F.mul(x2, Z1), X1)
        if v == F.zero:
            A = self.to_affine(P)
            return self.proj(self.add(A, Q))
        uu, vv = F.sqr(u), F.sqr(v)
        vvv = F.mul(v, vv)
        R = F.mul(vv, X1)
        vvZ = F.mul(vv, Z1)
        A = F.sub(F.add(F.sub(F.mul(uu, Z1), vvv), R), F.scale(self.a2, vvZ))   # -2R = R in char 3
        X3 = F.mul(v, A)
        Z3 = F.mul(v, vvZ)
        Y3 = F.sub(F.mul(u, F.sub(R, A)), F.mul(vvv, Y1))
        return (X3, Y3, Z3)

    def frobenius_proj(self, P):
        return INF if P is INF else (self.F.cube(P[0]), self.F.cube(P[1]), self.F.cube(P[2]))

    def to_affine(self, P):
        if P is INF:
            return INF
        F = self.F
        zi = F.inv(P[2])
        return (F.mul(P[0], zi), F.mul(P[1], zi))

    def batch_to_affine(self, Ps: list):
        """Montgomery's simultaneous inversion: 3(k-1) M + 1 I, then 2M per point."""
        F = self.F
        pts = [P for P in Ps if P is not INF]
        if not pts:
            return list(Ps)
        prods = [pts[0][2]]
        for P in pts[1:]:
            prods.append(F.mul(prods[-1], P[2]))
        inv = F.inv(prods[-1])
        zinv = [None] * len(pts)
        for i in range(len(pts) - 1, 0, -1):
            zinv[i] = F.mul(inv, prods[i - 1])
            inv = F.mul(inv, pts[i][2])
        zinv[0] = inv
        out = iter([(F.mul(P[0], zi), F.mul(P[1], zi)) for P, zi in zip(pts, zinv)])
        return [INF if P is INF else next(out) for P in Ps]


# ---------------------------------------------------------------------------
# F_4 inside F_{2^(2m)}: points on y^2 + xy = x^3 + a x^2 + b with b in F_4
# ---------------------------------------------------------------------------

def find_irreducible_f2(N: int) -> tuple[int, ...]:
    """Low-weight irreducible polynomial over F_2 of degree N: the lower exponents (trinomial, else pentanomial)."""
    from sympy import Poly, symbols
    x = symbols("x")
    for k in range(1, N):
        if Poly(x ** N + x ** k + 1, x, modulus=2).is_irreducible:
            return (k, 0)
    for k3 in range(3, N):
        for k2 in range(2, k3):
            for k1 in range(1, k2):
                if Poly(x ** N + x ** k3 + x ** k2 + x ** k1 + 1, x, modulus=2).is_irreducible:
                    return (k3, k2, k1, 0)
    raise ValueError("no irreducible polynomial found")


def solve_artin_schreier(F: BI.Field, c: int, theta: int) -> int | None:
    """z with z^2 + z = c in F_{2^N} (any N), given theta of trace 1; None if Tr(c) = 1."""
    if F.trace(c):
        return None
    N = F.m
    # z = sum_{i=0}^{N-2} c^(2^i) * sum_{j=i+1}^{N-1} theta^(2^j)
    thp = [theta]
    for _ in range(N - 1):
        thp.append(F.reduce(BI._spread(thp[-1])))
    suffix = [0] * (N + 1)
    for j in range(N - 1, -1, -1):
        suffix[j] = suffix[j + 1] ^ thp[j]
    z, ci = 0, c
    for i in range(N - 1):
        z ^= F.reduce(BI._clmul(ci, suffix[i + 1]))
        ci = F.reduce(BI._spread(ci))
    if F.reduce(BI._spread(z)) ^ z != c:
        raise ArithmeticError("Artin-Schreier solution check failed")
    return z


class BinaryCurveA(BI.BinaryCurve):
    """binary.BinaryCurve with any a in F_{2^N} (the F_4 twist class needs a = w).

    Only the three places where binary.py uses a in {0, 1} change: the curve
    equation, and the a-terms of the Lopez-Dahab doubling and mixed addition,
    which become one multiplication by the constant a each (+1M).
    """

    def __init__(self, F: BI.Field, a: int, b: int):
        if b == 0:
            raise ValueError("b = 0 is singular")
        self.F, self.a, self.b = F, a, b

    def _a_times(self, x: int) -> int:
        if self.a in (0, 1):
            return x if self.a else 0
        return self.F.mul(self.a, x)

    def on_curve(self, P) -> bool:
        if P is INF:
            return True
        F = self.F
        x, y = P
        x2 = F.sqr(x)
        return F.sqr(y) ^ F.mul(x, y) == F.mul(x2, x) ^ self._a_times(x2) ^ self.b

    def ld_dbl(self, P):
        F = self.F
        if P is INF or P[0] == 0:
            return INF
        X, Y, Z = P
        X2, Z2 = F.sqr(X), F.sqr(Z)
        Z3 = F.mul(X2, Z2)
        Z4 = F.sqr(Z2)
        bZ4 = Z4 if self.b == 1 else F.mul(self.b, Z4)
        X3 = F.sqr(X2) ^ bZ4
        inner = self._a_times(Z3) ^ F.sqr(Y) ^ bZ4
        return (X3, F.mul(bZ4, Z3) ^ F.mul(X3, inner), Z3)

    def ld_madd(self, P, Q):
        F = self.F
        if P is INF:
            return self.ld(Q)
        if Q is INF:
            return P
        X1, Y1, Z1 = P
        x2, y2 = Q
        Z1s = F.sqr(Z1)
        A = F.mul(y2, Z1s) ^ Y1
        B = F.mul(x2, Z1) ^ X1
        if B == 0:
            return self.ld_dbl(self.ld(Q)) if A == 0 else INF
        C = F.mul(Z1, B)
        D = F.mul(F.sqr(B), C ^ self._a_times(Z1s))
        Z3 = F.sqr(C)
        E = F.mul(A, C)
        X3 = F.sqr(A) ^ D ^ E
        Fv = X3 ^ F.mul(x2, Z3)
        G = F.mul(x2 ^ y2, F.sqr(Z3))
        return (X3, F.mul(E ^ Z3, Fv) ^ G, Z3)


class F4Embedding:
    """F_4 = {0, 1, w, w^2} inside F_{2^(2m)}, and points on y^2 + xy = x^3 + a x^2 + b there."""

    def __init__(self, m: int, seed: int = 1):
        N = 2 * m
        self.F = BI.Field(N, find_irreducible_f2(N))
        rng = random.Random(seed)
        while True:
            th = rng.getrandbits(N)
            if self.F.trace(th):
                self.theta = th
                break
        self.omega = solve_artin_schreier(self.F, 1, self.theta)        # w^2 + w + 1 = 0
        self.F.reset()

    def embed(self, e: int) -> int:
        """F_4 element (bit 0 = 1, bit 1 = w) into F_{2^(2m)}."""
        return (e & 1) ^ (self.omega if e & 2 else 0)

    def random_point(self, E: BI.BinaryCurve, rng: random.Random):
        F = self.F
        while True:
            x = rng.getrandbits(F.m)
            if x == 0:
                continue
            x2 = F.sqr(x)
            c = x ^ E.a ^ F.mul(E.b, F.inv(x2))
            z = solve_artin_schreier(F, c, self.theta)
            if z is not None:
                return (x, F.mul(x, z))


# ---------------------------------------------------------------------------
# one scalar multiplication, on real arithmetic or on a counting stub
# ---------------------------------------------------------------------------

class Char2Ops:
    """Lopez-Dahab on binary.BinaryCurve; phi = the q-power map, log2(q) squarings per coordinate."""

    def __init__(self, E: BI.BinaryCurve, q: int):
        self.E, self.F, self.r = E, E.F, {2: 1, 4: 2}[q]

    def reset(self):
        self.F.reset()

    def counts(self) -> dict:
        c = self.F.counts()
        return {"M": c["M"], "S": c["S"], "C": 0, "I": c["I"]}

    def neg(self, P):
        return self.E.neg(P)

    def proj(self, P):
        return self.E.ld(P)

    def madd(self, Q, T):
        return self.E.ld_madd(Q, T)

    def dbl(self, Q):
        return self.E.ld_dbl(Q)

    def frob(self, Q):
        for _ in range(self.r):
            Q = self.E.ld_frobenius(Q)
        return Q

    def frob_affine(self, P):
        for _ in range(self.r):
            P = self.E.frobenius(P)
        return P

    def to_affine(self, Q):
        return self.E.ld_to_affine(Q)

    def batch(self, Qs):
        return self.E.batch_to_affine(Qs)


class Char3Ops:
    def __init__(self, E: Char3Curve):
        self.E, self.F = E, E.F

    def reset(self):
        self.F.reset()

    def counts(self) -> dict:
        return self.F.counts()

    def neg(self, P):
        return self.E.neg(P)

    def proj(self, P):
        return self.E.proj(P)

    def madd(self, Q, T):
        return self.E.madd(Q, T)

    def dbl(self, Q):
        raise NotImplementedError("no doubling is needed for q = 3")

    def frob(self, Q):
        return self.E.frobenius_proj(Q)

    def frob_affine(self, P):
        return self.E.frobenius(P)

    def to_affine(self, Q):
        return self.E.to_affine(Q)

    def batch(self, Qs):
        return self.E.batch_to_affine(Qs)


def it_inversion_counts(q: int, field_degree: int) -> dict:
    """Itoh-Tsujii operation counts exactly as binary.Field.inv (char 2) / Char3Field.inv (char 3) perform them."""
    N = field_degree
    c = {"M": 0, "S": 0, "C": 0, "I": 1}
    pw = "S" if q in (2, 4) else "C"
    k = 1
    for bit in bin(N - 1)[2:][1:]:
        c[pw] += k
        c["M"] += 1
        k *= 2
        if bit == "1":
            c[pw] += 1
            c["M"] += 1
            k += 1
    c[pw] += 1
    if pw == "C":
        c["M"] += 1                                   # a * a^(r-1) = a^r in F_3
    return c


@dataclass
class CostTable:
    """Formula counts per operation (M, S, C) for one (q, coordinate system); the stub charges these."""
    name: str
    madd: dict
    frob: dict
    dbl: dict
    frob_affine: dict
    to_affine_extra: dict            # besides the inversion
    batch_per_point: dict            # besides 3(k-1) M + I
    inversion: dict
    note: str = ""


def cost_table(q: int, m: int, a_in_f2: bool = True, b_is_one: bool = False) -> CostTable:
    if q in (2, 4):
        r = 1 if q == 2 else 2
        madd = {"M": 8 + (0 if a_in_f2 else 1), "S": 5, "C": 0}
        return CostTable(
            f"q={q}: Lopez-Dahab over F_2^{r * m}",
            madd=madd, frob={"M": 0, "S": 3 * r, "C": 0},
            dbl={"M": (3 if b_is_one else 4) + (0 if a_in_f2 else 1), "S": 5, "C": 0},
            frob_affine={"M": 0, "S": 2 * r, "C": 0}, to_affine_extra={"M": 2, "S": 1, "C": 0},
            batch_per_point={"M": 2, "S": 1, "C": 0}, inversion=it_inversion_counts(q, r * m),
            note=("binary.BinaryCurve.ld_madd 8M+5S (a in {0,1}; +1M for a = w, the twist class, charged as a "
                  "full multiplication by the constant w), Frobenius = log2(q) squarings of X, Y, Z"))
    if q == 3:
        return CostTable(
            f"q=3: projective (X:Y:Z) over F_3^{m}",
            madd={"M": 10, "S": 2, "C": 0}, frob={"M": 0, "S": 0, "C": 3}, dbl={"M": 0, "S": 0, "C": 0},
            frob_affine={"M": 0, "S": 0, "C": 2}, to_affine_extra={"M": 2, "S": 0, "C": 0},
            batch_per_point={"M": 2, "S": 0, "C": 0}, inversion=it_inversion_counts(3, m),
            note="Char3Curve.madd 10M+2S (derived and implemented here), Frobenius = 3 cubings (linear)")
    raise ValueError(q)


class StubOps:
    """Counts what Char2Ops / Char3Ops would execute, without doing it (points are tokens)."""

    def __init__(self, ct: CostTable):
        self.ct = ct
        self.reset()

    def reset(self):
        self.c = {"M": 0, "S": 0, "C": 0, "I": 0}

    def counts(self) -> dict:
        return dict(self.c)

    def _charge(self, d: dict, times: int = 1):
        for k, v in d.items():
            self.c[k] = self.c.get(k, 0) + v * times

    def neg(self, P):
        return P

    def proj(self, P):
        return P

    def madd(self, Q, T):
        if Q is INF:
            return T
        self._charge(self.ct.madd)
        return Q

    def dbl(self, Q):
        if Q is INF:
            return INF
        self._charge(self.ct.dbl)
        return Q

    def frob(self, Q):
        if Q is INF:
            return INF
        self._charge(self.ct.frob)
        return Q

    def frob_affine(self, P):
        self._charge(self.ct.frob_affine)
        return P

    def to_affine(self, Q):
        if Q is INF:
            return INF
        self._charge(self.ct.inversion)
        self._charge(self.ct.to_affine_extra)
        return Q

    def batch(self, Qs):
        k = len([Q for Q in Qs if Q is not INF])
        if k:
            self.c["M"] += 3 * (k - 1)
            self._charge(self.ct.inversion)
            self._charge(self.ct.batch_per_point, k)
        return list(Qs)


def base_width(q: int) -> int:
    """The digit set used to build the table: Solinas' w = 2 (+-1) for q = 2; w = 1 for q = 3, 4."""
    return 2 if q == 2 else 1


def precompute(ops, Z: Zphi, ds: DigitSet, P) -> dict:
    """Table u -> alpha_u P (affine): base points first, then each alpha_u by its base-digit expansion, one batch."""
    q = Z.q
    bds = digit_set(q, Z.t, base_width(q))
    base = {1: P}
    for u, al in bds.alpha.items():
        if u == 1 or al == (1, 0):
            continue
        a, b = al
        if b == 0 and a in (2, -2):
            A = ops.to_affine(ops.dbl(ops.proj(P)))
            base[u] = A if a > 0 else ops.neg(A)
        elif a in (2, -2) and b in (1, -1):
            Pa = P if a > 0 else ops.neg(P)
            fp = ops.frob_affine(P)
            Q = ops.proj(fp if b == 1 else ops.neg(fp))
            Q = ops.madd(ops.madd(Q, Pa), Pa)
            base[u] = ops.to_affine(Q)
        else:
            raise NotImplementedError(f"base digit {al}")
    # table keys are classes of the width-w digit set; reuse a base point only when it is the same element
    table = {}
    for u, al in ds.alpha.items():
        for v, bal in bds.alpha.items():
            if v in base and al == bal:
                table[u] = base[v]
            elif v in base and al == (-bal[0], -bal[1]):
                table[u] = ops.neg(base[v])
    us = [u for u in ds.alpha if u not in table]
    if us:
        lds = []
        for u in us:
            Q = INF
            for d in reversed(expand(bds, ds.alpha[u])):
                if Q is not INF:
                    Q = ops.frob(Q)
                if d:
                    T = base[abs(d)]
                    Q = ops.madd(Q, T if d > 0 else ops.neg(T))
            lds.append(Q)
        for u, A in zip(us, ops.batch(lds)):
            table[u] = A
    return table


def mul_counted(ops, Z: Zphi, ds: DigitSet, delta, k: int, P, table: dict | None = None):
    """k P = rho P, rho = k mod delta, by the width-w Frobenius expansion; counts per phase."""
    ops.reset()
    if table is None:
        table = precompute(ops, Z, ds, P)
    pre = ops.counts()
    rho = Z.reduce_mod((k, 0), delta)
    digits = expand(ds, rho)
    Q = INF
    for d in reversed(digits):
        if Q is not INF:
            Q = ops.frob(Q)
        if d:
            T = table[abs(d)]
            Q = ops.madd(Q, T if d > 0 else ops.neg(T))
    mid = ops.counts()
    R = ops.to_affine(Q)
    end = ops.counts()
    sub = lambda x, y: {key: x[key] - y.get(key, 0) for key in x}  # noqa: E731
    return R, {"precompute": pre, "main": sub(mid, pre), "final": sub(end, mid), "total": end,
               "length": len(digits), "nonzero": sum(1 for d in digits if d)}


def weighted(c: dict, s: float, cube: float) -> float:
    return c.get("M", 0) + s * c.get("S", 0) + cube * c.get("C", 0)


# weights (S, C) per field characteristic under the two scenarios
SCENARIOS = {
    "linear_free": {2: (0.0, 0.0), 3: (CM.S_PER_M, 0.0)},
    "all_M": {2: (1.0, 1.0), 3: (1.0, 1.0)},
}
SCENARIO_NOTE = {
    "linear_free": ("maps that are linear over the prime field are free: squarings in characteristic 2, cubings "
                    "in characteristic 3; a characteristic-3 squaring is a real product, charged "
                    f"{CM.S_PER_M} M (costmodel.S_PER_M, an assumption)"),
    "all_M": "every squaring and cubing costs one multiplication",
}


# ---------------------------------------------------------------------------
# the study
# ---------------------------------------------------------------------------

WIDTHS = {2: (1, 2, 3, 4, 5, 6), 3: (1, 2, 3, 4), 4: (1, 2, 3)}
RANGES = {2: (131, 401), 3: (83, 257), 4: (67, 201)}          # m giving ~130-400-bit n
TARGET_BITS = (160, 300)                                        # the range the comparison is about
NIST_K = {163: 1, 233: -1, 283: -1, 409: -1, 571: -1}           # K-curves: m -> t = mu


def expansion_stats(Z: Zphi, ds: DigitSet, delta, ks: list[int], unreduced: bool = False) -> dict:
    Ls, NZs = [], []
    for k in ks:
        rho = (k, 0) if unreduced else Z.reduce_mod((k, 0), delta)
        dg = expand(ds, rho)
        Ls.append(len(dg))
        NZs.append(sum(1 for d in dg if d))
    n = len(ks)
    mean = lambda v: sum(v) / n  # noqa: E731
    return {"mean_length": round(mean(Ls), 3), "max_length": max(Ls), "min_length": min(Ls),
            "mean_nonzero": round(mean(NZs), 3), "density": round(sum(NZs) / sum(Ls), 4),
            "Ls": Ls, "NZs": NZs}


def model_costs(inst: Instance, ds: DigitSet, stats: dict, a_in_f2: bool) -> dict:
    """Mean modelled cost: the stub's precompute + per-scalar (L-1) Frobenius, (NZ-1) mixed additions, final inversion."""
    Z = Zphi(inst.q, inst.t)
    ct = cost_table(inst.q, inst.m, a_in_f2=a_in_f2, b_is_one=False)
    st = StubOps(ct)
    precompute(st, Z, ds, "P")
    pre = st.counts()
    n_sc = len(stats["Ls"])
    mean_f = sum(L - 1 for L in stats["Ls"]) / n_sc
    mean_a = sum(N - 1 for N in stats["NZs"]) / n_sc
    main = {key: mean_f * ct.frob.get(key, 0) + mean_a * ct.madd.get(key, 0) for key in ("M", "S", "C")}
    fin = {key: ct.inversion.get(key, 0) + ct.to_affine_extra.get(key, 0) for key in ("M", "S", "C")}
    tot = {key: pre.get(key, 0) + main[key] + fin[key] for key in ("M", "S", "C")}
    p = 3 if inst.q == 3 else 2
    out = {"table_points": ds.table_size, "precompute": pre, "main_mean": {k: round(v, 2) for k, v in main.items()},
           "final": fin, "total_mean": {k: round(v, 2) for k, v in tot.items()},
           "frobenius_per_scalar": round(mean_f, 2), "additions_per_scalar": round(mean_a, 2)}
    for sc, wt in SCENARIOS.items():
        s, c = wt[p]
        M_eq = weighted(tot, s, c)
        out[sc] = {"M_eq": round(M_eq, 1), "M_eq_per_bit": round(M_eq / inst.bits, 3),
                   "additions_per_bit": round(mean_a / inst.bits, 4)}
    return out


def study_instance(inst: Instance, scalars: int, seed: int, widths) -> dict:
    Z = Zphi(inst.q, inst.t)
    rng = random.Random(seed * 1000003 + inst.m * 7 + inst.t)
    ks = [rng.randrange(1, inst.n) for _ in range(scalars)]
    a_in_f2 = True
    if inst.q == 4:
        # the trace sign realised by y^2 + xy = x^3 + a x^2 + w with a in {0, 1}; the other sign needs a = w
        fam = families()[4]
        a_in_f2 = any(c["a"] in (0, 1) and c["b"] in (2, 3) for c in fam.get(inst.t, []))
    rows = {}
    for w in widths:
        ds = digit_set(inst.q, inst.t, w)
        cert = termination_certificate(ds)
        st = expansion_stats(Z, ds, inst.delta, ks)
        row = {k: v for k, v in st.items() if k not in ("Ls", "NZs")}
        row["termination"] = cert
        row["length_minus_m"] = round(st["mean_length"] - inst.m, 3)
        row["model"] = model_costs(inst, ds, st, a_in_f2)
        rows[f"w{w}"] = row
    ds1 = digit_set(inst.q, inst.t, 1 if inst.q != 2 else 2)
    unr = expansion_stats(Z, ds1, inst.delta, ks[:200], unreduced=True)
    return {"q": inst.q, "t": inst.t, "m": inst.m, "h": inst.h, "n": str(inst.n), "n_bits": round(inst.bits, 2),
            "field_bits": round(inst.field_bits, 1), "discriminant": inst.t ** 2 - 4 * inst.q,
            "probable_prime": "sympy.isprime (BPSW for n > 2^64): probable prime, not proven",
            "small_embedding_degree_le_50": small_embedding_degree(inst),
            "anomalous": inst.n == _char(inst.q),
            "a_in_F2_model": a_in_f2,
            "delta": [str(inst.delta[0]), str(inst.delta[1])], "scalars": scalars, "widths": rows,
            "unreduced_length_mean": unr["mean_length"],
            "unreduced_note": "expansion of k itself (no reduction mod delta), minimal signed digit set, 200 scalars"}


# ---------------------------------------------------------------------------
# verification on points
# ---------------------------------------------------------------------------

def _eigenvalue(inst: Instance, frob, mul, G) -> int | None:
    from sympy.ntheory import sqrt_mod
    n = inst.n
    disc = (inst.t * inst.t - 4 * inst.q) % n
    roots = sqrt_mod(disc, n, all_roots=True) or []
    inv2 = pow(2, -1, n)
    fG = frob(G)
    for s in roots:
        lam = (inst.t + int(s)) * inv2 % n
        if mul(lam, G) == fG:
            return lam
    return None


def verify_char3(inst: Instance, curve: dict, scalars: int = 6, counted: int = 12, seed: int = 5,
                 widths=(1, 2, 3)) -> dict:
    """Build E over F_{3^m}, check #E and phi on points, and k P by every width against double-and-add."""
    k_, c1, c0 = find_trinomial_f3(inst.m)
    F = Char3Field(inst.m, k_, c1, c0)
    E = Char3Curve(F, curve["a2"], curve["a6"])
    rng = random.Random(seed)
    Z = Zphi(3, inst.t)
    checks: dict = {}
    # phi^2 - t phi + q = 0 on random points
    ok = True
    for _ in range(3):
        P = E.random_point(rng)
        lhs = E.add(E.frobenius(E.frobenius(P)), E.mul_affine(3, P))
        rhs = E.mul_affine(inst.t, E.frobenius(P))
        ok &= lhs == rhs
    checks["phi^2 - t phi + q = 0 on points"] = ok
    # a point of order n: h * random point, killed by n
    while True:
        G = E.mul_affine(inst.h, E.random_point(rng))
        if G is not INF:
            break
    checks["n G = O (G = h R)"] = E.mul_affine(inst.n, G) is INF
    lam = _eigenvalue(inst, E.frobenius, E.mul_affine, G)
    checks["phi(G) = [lambda] G"] = lam is not None
    checks["delta(lambda) = 0 mod n"] = lam is not None and (inst.delta[0] + inst.delta[1] * lam) % inst.n == 0
    ops = Char3Ops(E)
    agree, model_exact = True, True
    counts = {}
    ks = [rng.randrange(1, inst.n) for _ in range(max(scalars, counted))]
    refs = {k: E.mul_affine(k, G) for k in ks[:scalars]}
    for w in widths:
        ds = digit_set(3, inst.t, w)
        tot = {"M": 0, "S": 0, "C": 0, "I": 0}
        for i, k in enumerate(ks):
            R, c = mul_counted(ops, Z, ds, inst.delta, k, G)
            if k in refs:
                agree &= R == refs[k]
            stub = StubOps(cost_table(3, inst.m))
            _, cs = mul_counted(stub, Z, ds, inst.delta, k, "P")
            model_exact &= cs["total"] == c["total"]
            for key in tot:
                tot[key] += c["total"][key]
        counts[f"w{w}"] = {key: round(v / len(ks), 2) for key, v in tot.items()}
    checks["k G by expansion = double-and-add (every width)"] = agree
    checks["stub model counts = executed counts (every scalar, every width)"] = model_exact
    return {"q": 3, "t": inst.t, "m": inst.m, "n_bits": round(inst.bits, 2), "curve": curve,
            "field": f"F_3[x]/(x^{inst.m} + {c1} x^{k_} + {c0})", "lambda": str(lam), "checks": checks,
            "all_checks_pass": all(checks.values()), "scalars_vs_reference": scalars,
            "scalars_counted": len(ks), "measured_counts_mean": counts}


def verify_char2_f4(inst: Instance, curve: dict, scalars: int = 6, counted: int = 12, seed: int = 6,
                    widths=(1, 2, 3)) -> dict:
    """The same over F_4: E: y^2 + xy = x^3 + a x^2 + b (a, b in F_4) inside F_{2^(2m)}."""
    emb = F4Embedding(inst.m)
    F = emb.F
    E = BinaryCurveA(F, emb.embed(curve["a"]), emb.embed(curve["b"]))
    a_in_f2 = curve["a"] in (0, 1)
    rng = random.Random(seed)
    Z = Zphi(4, inst.t)
    ops = Char2Ops(E, 4)
    frob = ops.frob_affine
    checks: dict = {}
    ok = True
    for _ in range(3):
        P = emb.random_point(E, rng)
        ok &= E.on_curve(P)
        lhs = E.add(frob(frob(P)), E.mul_ld(4, P))
        rhs = E.mul_ld(inst.t, frob(P))
        ok &= lhs == rhs
    checks["phi^2 - t phi + q = 0 on points"] = ok
    while True:
        G = E.mul_ld(inst.h, emb.random_point(E, rng))
        if G is not INF:
            break
    checks["n G = O (G = h R)"] = E.mul_ld(inst.n, G) is INF
    lam = _eigenvalue(inst, frob, E.mul_ld, G)
    checks["phi(G) = [lambda] G"] = lam is not None
    checks["delta(lambda) = 0 mod n"] = lam is not None and (inst.delta[0] + inst.delta[1] * lam) % inst.n == 0
    agree, model_exact = True, True
    counts = {}
    ks = [rng.randrange(1, inst.n) for _ in range(max(scalars, counted))]
    refs = {k: E.mul_affine(k, G) for k in ks[:scalars]}
    for w in widths:
        ds = digit_set(4, inst.t, w)
        tot = {"M": 0, "S": 0, "C": 0, "I": 0}
        for k in ks:
            R, c = mul_counted(ops, Z, ds, inst.delta, k, G)
            if k in refs:
                agree &= R == refs[k]
            stub = StubOps(cost_table(4, inst.m, a_in_f2=a_in_f2, b_is_one=curve["b"] == 1))
            _, cs = mul_counted(stub, Z, ds, inst.delta, k, "P")
            model_exact &= cs["total"] == c["total"]
            for key in tot:
                tot[key] += c["total"][key]
        counts[f"w{w}"] = {key: round(v / len(ks), 2) for key, v in tot.items()}
    checks["k G by expansion = double-and-add (every width)"] = agree
    checks["stub model counts = executed counts (every scalar, every width)"] = model_exact
    return {"q": 4, "t": inst.t, "m": inst.m, "n_bits": round(inst.bits, 2), "curve": curve,
            "field": f"F_2^{2 * inst.m}, lower exponents {list(F.low)}; F_4 = <w>, w^2 + w + 1 = 0",
            "lambda": str(lam), "checks": checks, "all_checks_pass": all(checks.values()),
            "scalars_vs_reference": scalars, "scalars_counted": len(ks), "measured_counts_mean": counts}


def koblitz_crosscheck(m: int, a: int, ks: int = 4, widths=(2, 4, 5)) -> dict:
    """On a NIST K-curve: this module's stub model against binary.mul_tnaf_counted's executed counts, per scalar."""
    from sympy import isprime
    lows = {163: (7, 6, 3, 0), 233: (74, 0), 283: (12, 7, 5, 0), 409: (87, 0), 571: (10, 5, 2, 0)}
    F = BI.Field(m, lows[m])
    E = BI.BinaryCurve(F, a, 1)
    mu = 1 if a == 1 else -1
    h = 2 if a == 1 else 4
    N = (1 << m) + 1 - BI.lucas_trace(mu, m)
    n = N // h
    assert isprime(n)
    rng = random.Random(m)
    while True:
        G = E.mul_ld(h, E.random_point(rng))
        if G is not INF:
            break
    kob, kchecks = BI.koblitz(E, n, h, G)
    Z = Zphi(2, mu)
    inst_delta = Z.delta(m)
    same_delta = tuple(inst_delta) == tuple(kob.delta)
    exact = True
    digits_same = True
    for w in widths:
        ds = digit_set(2, mu, w)
        tw, alpha = BI.tnaf_constants(kob, w)
        for _ in range(ks):
            k = rng.randrange(1, n)
            R, c = BI.mul_tnaf_counted(E, kob, k, G, w, (tw, alpha))
            st = StubOps(cost_table(2, m, b_is_one=True))
            _, cs = mul_counted(st, Z, ds, inst_delta, k, "P")
            exact &= cs["total"] == {"M": c["total"]["M"], "S": c["total"]["S"], "C": 0, "I": c["total"]["I"]}
            rho = Z.reduce_mod((k, 0), inst_delta)
            sol = BI.tnaf(rho, kob, w, tw, alpha)
            mine = expand(ds, rho)
            digits_same &= [0 if d == 0 else d[0] * d[1] for d in sol] == mine
    return {"curve": f"K-{m}", "delta_equals_binary_py": same_delta, "koblitz_checks": kchecks,
            "digits_equal_solinas_tnaf": digits_same, "stub_counts_equal_binary_py_counts": exact,
            "widths": list(widths), "scalars_per_width": ks}


def q4_koblitz_split(m_range) -> dict:
    """Why q = 4, t = -3 never gives a prime n.

    Those curves are the F_2-Koblitz curves (b = 1, Tr(a) = 0) with phi_4 = tau^2, so #E(F_{4^m}) = #E(F_{2^m}) #E'(F_{2^m}) (E' the quadratic twist over F_{2^m}) and, for odd m,
    n = [#E(F_{2^m})/#E(F_2)] [#E'(F_{2^m})/#E'(F_2)], a product of two integers > 1.  Checked for every prime m.
    """
    ok = True
    ms = _primes(*m_range)
    for m in ms:
        N4 = 4 ** m + 1 - lucas_V(4, -3, m)
        n4 = N4 // 8                                   # #E(F_4) = 4 + 1 + 3 = 8 = 2 * 4
        n_a = (2 ** m + 1 - lucas_V(2, 1, m)) // 2
        n_b = (2 ** m + 1 - lucas_V(2, -1, m)) // 4
        ok &= n4 == n_a * n_b and n_a > 1 and n_b > 1
    return {"m_checked": [ms[0], ms[-1]], "count": len(ms),
            "n_equals_product_of_two_Koblitz_cofactor_quotients": ok}


def nist_tnaf_reference(path: str) -> list[dict]:
    """K-curve TNAF counts measured in research/endosweep_nist_20261006/nist.json, per bit of n."""
    d = json.load(open(path))
    out = []
    for name in ("K-163", "K-233", "K-283", "K-409", "K-571"):
        e = d["curves"][f"nist/{name}"]
        q, t = int(e["q"]), int(e["t"])
        h = 2 if e["a"] == 1 else 4
        nb = log2((q + 1 - t) // h)
        s = e["summary"]
        cfg = e["scalar_multiplication"]["configs"]
        out.append({"curve": name, "n_bits": round(nb, 2),
                    "linear_free": {"best": s["S_free"]["best_tnaf"], "M_eq": s["S_free"]["tnaf_M_eq"],
                                    "M_eq_per_bit": round(s["S_free"]["tnaf_M_eq"] / nb, 3)},
                    "all_M": {"best": s["S_equals_M"]["best_tnaf"], "M_eq": s["S_equals_M"]["tnaf_M_eq"],
                              "M_eq_per_bit": round(s["S_equals_M"]["tnaf_M_eq"] / nb, 3)},
                    "wnaf_all_M_per_bit": round(s["S_equals_M"]["wnaf_M_eq"] / nb, 3),
                    "configs_measured": sorted(k for k in cfg if k.startswith("tnaf"))})
    return out


def prime_field_reference() -> dict:
    """costmodel's modelled 2-GLV and plain wNAF on a 256-bit a = 0 curve (secp256k1-like), per bit of n."""
    model = "weierstrass_jacobian_a=0"
    gid = CM.Generator("identity", 1, 0.0, "identity")
    gu = CM.Generator("zeta3", 2, CM.ENDOMORPHISM_COSTS["unit"]["M"], "unit")
    glv = CM.multiscalar_cost(128, [gid, gu], model)
    plain = CM.multiscalar_cost(256, [gid], model)
    return {"model": model, "note": (f"costmodel.multiscalar_cost, S = {CM.S_PER_M} M, I = {CM.I_PER_M} M "
                                     "(assumptions); M of a 256-bit prime field"),
            "glv2": {"M": round(glv.total_M, 1), "M_per_bit": round(glv.total_M / 256, 3), "window": glv.window},
            "wnaf": {"M": round(plain.total_M, 1), "M_per_bit": round(plain.total_M / 256, 3),
                     "window": plain.window}}


def standardized_census(std_curves: str | None) -> dict:
    """Field types in std-curves, and every binary curve whose coefficients lie in a proper subfield."""
    if not std_curves:
        return {"note": "std-curves not given"}
    import glob
    import subprocess
    out = {"field_types": {}, "subfield_curves": [], "char3_or_F4m": []}
    try:
        out["commit"] = subprocess.run(["git", "-C", std_curves, "rev-parse", "HEAD"], capture_output=True,
                                       text=True).stdout.strip()
    except OSError:
        out["commit"] = None
    for f in sorted(glob.glob(os.path.join(std_curves, "*", "curves.json"))):
        cat = os.path.basename(os.path.dirname(f))
        for c in json.load(open(f))["curves"]:
            fl = c["field"]
            ty = fl["type"]
            out["field_types"][ty] = out["field_types"].get(ty, 0) + 1
            if ty == "Extension" and int(str(fl["base"]), 16 if str(fl["base"]).startswith("0x") else 10) == 3:
                out["char3_or_F4m"].append(f"{cat}/{c['name']}")
            if ty != "Binary":
                continue
            N = int(fl["bits"])
            a, b = int(c["params"]["a"]["raw"], 16), int(c["params"]["b"]["raw"], 16)
            if fl.get("basis") == "normal":
                rot = lambda x, s: ((x << s) | (x >> (N - s))) & ((1 << N) - 1)  # noqa: E731
                sub = min(d for d in range(1, N + 1) if N % d == 0 and rot(a, d) == a and rot(b, d) == b)
            else:
                F = BI.field_from_entry(fl)

                def fixed(x, d):
                    y = x
                    for _ in range(d):
                        y = F.reduce(BI._spread(y))
                    return y == x
                sub = min(d for d in range(1, N + 1) if N % d == 0 and fixed(a, d) and fixed(b, d))
            if sub < N:
                row = {"curve": f"{cat}/{c['name']}", "field_degree": N, "coefficient_field": f"F_2^{sub}",
                       "m": N // sub}
                if sub == 2:
                    out["char3_or_F4m"].append(row["curve"])
                if sub > 1:
                    row["order_check"] = _subfield_order_check(c, sub, N // sub)
                out["subfield_curves"].append(row)
    return out


def _subfield_order_check(c: dict, s: int, m: int) -> dict:
    """For a curve defined over F_{2^s}: the trace t_s with #E(F_{2^(sm)}) = h n from V_m, and h = #E(F_{2^s})?"""
    n = int(c["order"], 16)
    h = int(c["cofactor"], 16)
    q = 1 << s
    lim = 2 * int(sqrt(q)) + 2
    for t in range(-lim, lim + 1):
        if t % 2 == 0:
            continue
        if q ** m + 1 - lucas_V(q, t, m) == h * n:
            return {"t_over_F_2^s": t, "E(F_2^s)": q + 1 - t, "cofactor": h,
                    "cofactor_equals_E(F_2^s)": h == q + 1 - t}
    return {"t_over_F_2^s": None}


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------

def run(out_dir: str, scalars: int, std_curves: str | None, nist_json: str, seed: int = 20261008) -> dict:
    t0 = time.time()
    fams = families()
    doc: dict = {"scalars": scalars, "seed": seed, "families": {}, "instances": [], "verification": [],
                 "koblitz_crosscheck": [], "scenarios": SCENARIO_NOTE}
    for q in (2, 3, 4):
        doc["families"][str(q)] = {str(t): v for t, v in sorted(fams[q].items())}
    # search
    found = {}
    for q in (2, 3, 4):
        for t in sorted(fams[q]):
            lo, hi = RANGES[q]
            found[(q, t)] = search(q, t, lo, hi)
    doc["search"] = {f"q={q},t={t}": {"m_range": list(RANGES[q]), "m_with_prime_n": [I.m for I in v],
                                      "n_bits": [round(I.bits, 1) for I in v],
                                      "in_160_300": [I.m for I in v if TARGET_BITS[0] <= I.bits <= TARGET_BITS[1]]}
                     for (q, t), v in found.items()}
    doc["q4_t-3_composite"] = q4_koblitz_split(RANGES[4])
    # every found instance plus the NIST K-curve parameters
    insts = [I for v in found.values() for I in v]
    for m, t in NIST_K.items():
        if not any(I.q == 2 and I.m == m and I.t == t for I in insts):
            insts.append(instance(2, t, m))
    for I in sorted(insts, key=lambda I: (I.q, I.t, I.m)):
        doc["instances"].append(study_instance(I, scalars, seed, WIDTHS[I.q]))
    # verification on points
    v3 = {}
    for t in sorted(fams[3]):
        for m in _primes(50, 100):
            I = instance(3, t, m)
            if I:
                v3[t] = I
                break
    for t, I in sorted(v3.items()):
        curve = next(c for c in fams[3][t] if c["a4"] == 0)
        doc["verification"].append(verify_char3(I, curve))
    for t in sorted(fams[4]):
        for m in _primes(25, 61):
            I = instance(4, t, m)
            if I:
                doc["verification"].append(verify_char2_f4(I, fams[4][t][0]))
                break
    for m, a in ((163, 1), (233, 0)):
        doc["koblitz_crosscheck"].append(koblitz_crosscheck(m, a))
    doc["summary"] = summary(doc)
    doc["binary_koblitz_measured"] = nist_tnaf_reference(nist_json)
    doc["prime_field_glv_modelled"] = prime_field_reference()
    doc["standardized"] = standardized_census(std_curves)
    doc["elapsed_s"] = round(time.time() - t0, 1)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "frobenius.json"), "w") as f:
        json.dump(doc, f, indent=1)
    with open(os.path.join(out_dir, "frobenius.md"), "w") as f:
        f.write(markdown(doc))
    return doc


def _best(rows: dict, sc: str):
    k = min(rows, key=lambda w: rows[w]["model"][sc]["M_eq_per_bit"])
    return k, rows[k]["model"][sc]


def bits_per_nonzero_predicted(q: int, w: int) -> float:
    """log2(q) * (w - 1 + q/(q - 1)): after a nonzero digit w - 1 zeros are forced, then phi divides with prob. 1/q."""
    return log2(q) * (w - 1 + q / (q - 1))


def summary(doc: dict) -> list[dict]:
    """Per instance: the best width in each scenario, and bits of n consumed per nonzero digit, measured vs predicted."""
    out = []
    for I in doc["instances"]:
        rows = I["widths"]
        r = {"q": I["q"], "t": I["t"], "m": I["m"], "n_bits": I["n_bits"],
             "in_160_300": TARGET_BITS[0] <= I["n_bits"] <= TARGET_BITS[1]}
        for sc in SCENARIOS:
            w, md = _best(rows, sc)
            r[sc] = {"best_width": int(w[1:]), "M_eq_per_bit": md["M_eq_per_bit"],
                     "table_points": rows[w]["model"]["table_points"]}
        r["bits_per_nonzero"] = {w: {"measured": round(log2(I["q"]) / row["density"], 3),
                                     "predicted": round(bits_per_nonzero_predicted(I["q"], int(w[1:])), 3),
                                     "table_points": row["model"]["table_points"]}
                                 for w, row in rows.items()}
        out.append(r)
    return out


def markdown(doc: dict) -> str:
    L = ["# Frobenius expansions over F_2, F_3, F_4", "",
         f"{doc['scalars']} random scalars per instance and width; costs are **modelled** (formula counts from "
         "`frobenius.cost_table` times measured digit statistics), except the verification section, which is "
         "**measured** on points.", "",
         "## Ordinary traces over F_q (exhaustive)", "",
         "| q | t | t^2 - 4q | curves |", "|--:|--:|--:|--:|"]
    for q, fam in doc["families"].items():
        for t, cs in fam.items():
            L.append(f"| {q} | {t} | {int(t) ** 2 - 4 * int(q)} | {len(cs)} |")
    L += ["", "## Prime-order instances (n = #E(F_{q^m}) / #E(F_q), BPSW probable prime)", "",
          "| q | t | m range | m with n prime |", "|--:|--:|:--|:--|"]
    for key, v in doc["search"].items():
        q, t = key.split(",")
        L.append(f"| {q[2:]} | {t[2:]} | {v['m_range'][0]}-{v['m_range'][1]} | "
                 f"{', '.join(f'{m} ({b})' for m, b in zip(v['m_with_prime_n'], v['n_bits'])) or 'none'} |")
    L += ["", "## Expansion statistics and modelled cost per instance", "",
          "Length = digits of the expansion of k mod delta; density = nonzero / length; adds/bit = mean "
          "additions per bit of n; M/bit = modelled M-equivalents per bit of n (whole scalar multiplication: "
          "table, main loop, final inversion).", "",
          "| q | t | m | n bits | w | table | mean length | max | density | adds/bit | M/bit (linear free) | "
          "M/bit (all M) | terminates (proof) |",
          "|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|:--|"]
    for I in doc["instances"]:
        for w, r in I["widths"].items():
            md = r["model"]
            L.append(f"| {I['q']} | {I['t']} | {I['m']} | {I['n_bits']} | {w[1:]} | {md['table_points']} | "
                     f"{r['mean_length']} | {r['max_length']} | {r['density']} | "
                     f"{md['linear_free']['additions_per_bit']} | {md['linear_free']['M_eq_per_bit']} | "
                     f"{md['all_M']['M_eq_per_bit']} | {'yes' if r['termination']['all_terminate'] else 'NO'} "
                     f"({r['termination']['lattice_points']} pts) |")
    L += ["", "## Best width per instance (modelled M-equivalents per bit of n)", "",
          "| q | t | m | n bits | linear free: w, table, M/bit | all M: w, table, M/bit |", "|--:|--:|--:|--:|:--|:--|"]
    for r in doc["summary"]:
        a, b = r["linear_free"], r["all_M"]
        L.append(f"| {r['q']} | {r['t']} | {r['m']} | {r['n_bits']} | w{a['best_width']}, {a['table_points']}, "
                 f"**{a['M_eq_per_bit']}** | w{b['best_width']}, {b['table_points']}, **{b['M_eq_per_bit']}** |")
    L += ["", "Bits of n consumed per nonzero digit, measured (log2 q / density) against "
          "log2(q) (w - 1 + q/(q-1)), on the largest instance of each q:", "",
          "| q | t | m | w | table | measured | predicted |", "|--:|--:|--:|--:|--:|--:|--:|"]
    for q in (2, 3, 4):
        rs = [r for r in doc["summary"] if r["q"] == q]
        if not rs:
            continue
        r = max(rs, key=lambda r: r["n_bits"])
        for w, v in r["bits_per_nonzero"].items():
            L.append(f"| {q} | {r['t']} | {r['m']} | {w[1:]} | {v['table_points']} | {v['measured']} | {v['predicted']} |")
    L += ["", "## Verification on points (measured)", ""]
    for v in doc["verification"]:
        L.append(f"* q = {v['q']}, t = {v['t']}, m = {v['m']} ({v['n_bits']}-bit n), {v['field']}, curve "
                 f"{v['curve']}: all checks pass = **{v['all_checks_pass']}**; mean executed counts "
                 + "; ".join(f"{w}: {c}" for w, c in v["measured_counts_mean"].items()))
        for c, ok in v["checks"].items():
            L.append(f"  * {c}: {ok}")
    L += ["", "## Cross-check against binary.py on NIST K-curves", ""]
    for c in doc["koblitz_crosscheck"]:
        L.append(f"* {c['curve']}: delta equal = {c['delta_equals_binary_py']}, digits equal Solinas TNAF = "
                 f"{c['digits_equal_solinas_tnaf']}, stub counts equal binary.py executed counts = "
                 f"{c['stub_counts_equal_binary_py_counts']} (widths {c['widths']}, {c['scalars_per_width']} "
                 "scalars each)")
    L += ["", "## Reference points", "", "Binary Koblitz TNAF, measured in `research/endosweep_nist_20261006` "
          "(32 scalars, best width):", "",
          "| curve | n bits | M/bit (S free) | M/bit (S = M) | wNAF M/bit (S = M) |", "|:--|--:|--:|--:|--:|"]
    for r in doc["binary_koblitz_measured"]:
        L.append(f"| {r['curve']} | {r['n_bits']} | {r['linear_free']['M_eq_per_bit']} | "
                 f"{r['all_M']['M_eq_per_bit']} | {r['wnaf_all_M_per_bit']} |")
    p = doc["prime_field_glv_modelled"]
    L += ["", f"Prime field (modelled, {p['note']}): 2-GLV {p['glv2']['M_per_bit']} M/bit, plain wNAF "
          f"{p['wnaf']['M_per_bit']} M/bit.", ""]
    s = doc["standardized"]
    if "field_types" in s:
        L += ["## Standardized curves", "", f"std-curves commit `{s.get('commit')}`: field types {s['field_types']}; "
              f"curves over F_3^m or F_4^m: {s['char3_or_F4m'] or 'none'}.", "",
              "Binary curves whose coefficients lie in a proper subfield:", ""]
        for r in s["subfield_curves"]:
            L.append(f"* {r['curve']}: F_2^{r['field_degree']}, coefficients in {r['coefficient_field']} "
                     f"(m = {r['m']}){'; ' + json.dumps(r['order_check']) if 'order_check' in r else ''}")
    L.append("")
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Frobenius-adic expansions on subfield curves over F_2, F_3, F_4")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--scalars", type=int, default=1000)
    ap.add_argument("--std-curves", default=None, help="a J08nY/std-curves checkout (for the census)")
    ap.add_argument("--nist-json", default="research/endosweep_nist_20261006/nist.json")
    args = ap.parse_args(argv)
    doc = run(args.out_dir, args.scalars, args.std_curves, args.nist_json)
    ok = all(v["all_checks_pass"] for v in doc["verification"]) and all(
        c["stub_counts_equal_binary_py_counts"] and c["digits_equal_solinas_tnaf"] for c in doc["koblitz_crosscheck"])
    print(f"{len(doc['instances'])} instances, {len(doc['verification'])} verified on points, "
          f"all checks pass: {ok}, {doc['elapsed_s']} s")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
