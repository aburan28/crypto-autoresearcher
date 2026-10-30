"""Curves for EXP-MONO-1a1be2 (TASK-20261029-a97206): seeded generation, group law, point counting,
factor base, lifts, 2-torsion.

Short Weierstrass y^2 = x^3 + a x + b over F_Q = F_q[t]/(g). Points are (x, y) tuples of field
elements; the point at infinity is None. The group law is generic over the field object, so the
same code runs over FQ and over the quadratic extension FQ2 (group-law cross-check).

Seed rule (specification seeds.curve_seed_rule): SHA-256 of the UTF-8 seed string, first 16 bytes
big-endian as an integer s, numpy.random.Generator(PCG64(s)).

IMPLEMENTATION CHOICES where the specification is silent (recorded in implementation/kat-report.md):
  * a curve attempt draws rng.integers(0, q, size=2n); the first n integers are the coefficients
    of a (constant term first), the next n those of b. A rejected attempt redraws from the same
    generator; the number of rejected attempts is recorded.
  * for n = 1 every j lies in F_q, so the j-in-F_q rejection is vacuous and only the singular
    rejection applies (the anchor cells would otherwise have no curve).
"""
from __future__ import annotations

import hashlib
import math
import random

import numpy as np

import fqn
from fqn import FQ, FQ2


# ----------------------------------------------------------------------------- seeds
def seed_int(seed_string: str) -> int:
    """First 16 bytes (big-endian) of SHA-256 of the UTF-8 seed string, as an integer."""
    return int.from_bytes(hashlib.sha256(seed_string.encode("utf-8")).digest()[:16], "big")


def make_rng(seed_string: str) -> np.random.Generator:
    return np.random.Generator(np.random.PCG64(seed_int(seed_string)))


# ----------------------------------------------------------------------------- the curve
class WCurve:
    """y^2 = x^3 + a x + b over the field object F (FQ or FQ2); a, b already in F."""

    def __init__(self, F, a, b):
        self.F, self.a, self.b = F, a, b

    def f(self, x):
        F = self.F
        return F.add(F.add(F.mul(F.mul(x, x), x), F.mul(self.a, x)), self.b)

    def on_curve(self, P) -> bool:
        if P is None:
            return True
        F = self.F
        x, y = P
        return F.mul(y, y) == self.f(x)

    def neg(self, P):
        if P is None:
            return None
        return (P[0], self.F.neg(P[1]))

    def add(self, P, R):
        F = self.F
        if P is None:
            return R
        if R is None:
            return P
        x1, y1 = P
        x2, y2 = R
        if x1 == x2:
            if F.is_zero(F.add(y1, y2)):
                return None
            three = F.from_int(3)
            lam = F.mul(F.add(F.mul(three, F.mul(x1, x1)), self.a), F.inv(F.add(y1, y1)))
        else:
            lam = F.mul(F.sub(y2, y1), F.inv(F.sub(x2, x1)))
        x3 = F.sub(F.sub(F.mul(lam, lam), x1), x2)
        y3 = F.sub(F.mul(lam, F.sub(x1, x3)), y1)
        return (x3, y3)

    def mul(self, k: int, P):
        if k < 0:
            return self.mul(-k, self.neg(P))
        R, Pk = None, P
        while k:
            if k & 1:
                R = self.add(R, Pk)
            k >>= 1
            if k:
                Pk = self.add(Pk, Pk)
        return R

    def lift(self, x, F2: FQ2 | None = None):
        """For x in F_Q, a point with that x-coordinate over F_Q (if f(x) is a square) or, with F2,
        over F_{Q^2}. Returns None when f(x) is a nonsquare and F2 is not given."""
        y2 = self.f(x)
        if F2 is None:
            y = self.F.sqrt(y2)
            return None if y is None else (x, y)
        return (F2.embed(x), F2.lift_y(y2))


class Curve(WCurve):
    """A curve over F_Q = FQ with the experiment's bookkeeping."""

    def __init__(self, F: FQ, a, b):
        super().__init__(F, a, b)
        self._roots = None

    # --- selection rules
    def discriminant_term(self):
        """4a^3 + 27b^2 (zero iff singular)."""
        F = self.F
        a3 = F.mul(F.mul(self.a, self.a), self.a)
        b2 = F.mul(self.b, self.b)
        return F.add(F.smul(a3, 4), F.smul(b2, 27))

    def is_singular(self) -> bool:
        return self.F.is_zero(self.discriminant_term())

    def j_invariant(self):
        """1728 * 4a^3 / (4a^3 + 27b^2); requires nonsingular."""
        F = self.F
        a3 = F.mul(F.mul(self.a, self.a), self.a)
        return F.mul(F.smul(a3, 4 * 1728), F.inv(self.discriminant_term()))

    def j_in_Fq(self) -> bool:
        """j lies in the subfield F_q = the constants, i.e. every coefficient above t^0 is zero."""
        return self.F.is_scalar(self.j_invariant())

    # --- 2-torsion
    def f_poly(self):
        F = self.F
        return fqn.ptrim(F, [self.b, self.a, F.zero, F.one])

    def two_torsion_roots(self):
        """x-coordinates (sorted by code) of the nonzero 2-torsion points of E(F_Q)."""
        if self._roots is None:
            self._roots = fqn.roots(self.F, self.f_poly())
        return self._roots

    def two_torsion_points(self):
        return [(r, self.F.zero) for r in self.two_torsion_roots()]

    # --- factor base D = {P != O : x(P) in F_q}
    def factor_base(self):
        """Returns (D, X, t2): D the list of points with x in F_q sorted by (code(x), code(y)) with both
        signs of every non-2-torsion x, X the sorted list of those x (as constants), t2 the number of
        2-torsion points in D. The lift used for T_S/T_X is the point of each x with the smaller y code."""
        F = self.F
        D, X, t2 = [], [], 0
        for xv in range(F.q):
            x = F.from_int(xv)
            y2 = self.f(x)
            if F.is_zero(y2):
                D.append((x, F.zero))
                X.append(x)
                t2 += 1
                continue
            y = F.sqrt(y2)
            if y is None:
                continue
            ny = F.neg(y)
            first, second = (y, ny) if F.to_code(y) <= F.to_code(ny) else (ny, y)
            D.append((x, first))
            D.append((x, second))
            X.append(x)
        return D, X, t2

    # --- point counting
    def count_points_naive(self) -> int:
        """From the definition: number of (x, y) with y^2 = f(x), plus the point at infinity.
        Squares are tabulated by direct squaring of every element (no chi, no sqrt, no kernel)."""
        F = self.F
        squares: dict = {}
        for y in F.elements():
            s = F.mul(y, y)
            squares[s] = squares.get(s, 0) + 1
        total = 1
        for x in F.elements():
            total += squares.get(self.f(x), 0)
        return total

    def count_points_chi(self) -> int:
        """N = Q + 1 + sum_x chi(f(x)), by the quadratic character (independent of the naive table)."""
        F = self.F
        return F.Q + 1 + sum(F.chi(self.f(x)) for x in F.elements())

    def twist(self):
        """The quadratic twist y^2 = x^3 + a d^2 x + b d^3 (d the least nonsquare); N + N' = 2Q + 2."""
        F = self.F
        d = F.nonsquare()
        d2 = F.mul(d, d)
        return Curve(F, F.mul(self.a, d2), F.mul(self.b, F.mul(d2, d)))

    def count_points_bsgs(self, max_points: int = 64, seed: int = 20261029):
        """Baby-step giant-step on the Hasse interval. For a random point P of E the candidates are the
        integers M in the interval with M*P = O; for a random point P' of the quadratic twist E' they
        are the M with (2Q+2-M)*P' = O. Candidate sets of several random points on both curves are
        intersected until one value remains (the twist removes the ambiguity of groups of small
        exponent). Returns (N, number_of_point_pairs_used). Raises ValueError if still ambiguous after
        max_points pairs. Randomness: random.Random(seed) chooses the points; N does not depend on it
        (the true N lies in every candidate set, and the intersection is accepted only when it is a
        single value)."""
        F = self.F
        Q = F.Q
        w = math.isqrt(4 * Q) + 1
        lo, hi = Q + 1 - w, Q + 1 + w
        rnd = random.Random(seed)
        Et = self.twist()
        cand = None
        for used in range(1, max_points + 1):
            sets = []
            for curve, flip in ((self, False), (Et, True)):
                P = None
                while P is None:
                    x = F.from_code(rnd.randrange(Q))
                    P = curve.lift(x)
                    if P is not None and F.is_zero(P[1]):
                        P = None
                mult = curve._order_multiples(P, lo, hi)      # interval is symmetric about Q+1
                sets.append({2 * Q + 2 - M for M in mult} if flip else mult)
            mine = sets[0] & sets[1]
            cand = mine if cand is None else (cand & mine)
            if len(cand) == 1:
                return next(iter(cand)), used
            if not cand:
                raise ValueError("empty candidate set (internal error)")
        raise ValueError(f"ambiguous after {max_points} points: {sorted(cand)[:5]}")

    def _order_multiples(self, P, lo: int, hi: int) -> set[int]:
        """All M in [lo, hi] with M*P = O (BSGS)."""
        span = hi - lo + 1
        m = math.isqrt(span) + 1
        baby: dict = {}
        Pj = None
        for j in range(m):
            baby.setdefault(Pj, []).append(j)       # key None = O for j = 0
            Pj = self.add(Pj, P)
        mP = Pj                                      # m*P
        # R0 = lo*P ; M = lo + i*m + j with R0 + i*mP = -j P  <=>  -(R0 + i mP) = jP
        G = self.mul(lo, P)
        out = set()
        i = 0
        while lo + i * m <= hi:
            key = self.neg(G)
            for j in baby.get(key, ()):
                M = lo + i * m + j
                if lo <= M <= hi:
                    out.add(M)
            G = self.add(G, mP)
            i += 1
        return out


# ----------------------------------------------------------------------------- generation
def generate_curve(F: FQ, seed_string: str):
    """Seeded curve per the module docstring. Returns (Curve, info) with info recording the seed
    integer, the attempts used and the rejection counts."""
    rng = make_rng(seed_string)
    n, q = F.n, F.q
    attempts = rej_singular = rej_j = 0
    while True:
        attempts += 1
        vals = [int(v) for v in rng.integers(0, q, size=2 * n)]
        a, b = tuple(vals[:n]), tuple(vals[n:])
        E = Curve(F, a, b)
        if E.is_singular():
            rej_singular += 1
            continue
        if n > 1 and E.j_in_Fq():
            rej_j += 1
            continue
        info = {"seed_string": seed_string, "seed_int": seed_int(seed_string), "generator": "numpy PCG64",
                "attempts": attempts, "rejected_singular": rej_singular, "rejected_j_in_Fq": rej_j}
        return E, info


def count_points(E: Curve, kernel=None):
    """N by the specification's rule: exhaustive when Q < 2^27 (compiled kernel if given, else the
    chi sum in Python), otherwise BSGS. Returns (N, method)."""
    Q = E.F.Q
    if Q < 2 ** 27:
        if kernel is not None:
            return kernel.count_points(E), "exhaustive_kernel"
        return E.count_points_chi(), "exhaustive_python_chi"
    N, _ = E.count_points_bsgs()
    return N, "bsgs"
