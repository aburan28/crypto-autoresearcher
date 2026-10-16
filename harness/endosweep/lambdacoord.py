"""Lambda coordinates on binary curves, counted, and the NIST curves re-priced with them.

Oliveira, Lopez, Aranha and Rodriguez-Henriquez, "Lambda coordinates for
binary elliptic curves" (CHES 2013; JCEN 2014) represent a point P = (x, y)
of y^2 + xy = x^3 + a x^2 + b with x != 0 as (x, lambda = x + y/x), and
projectively as (X, L, Z) with x = X/Z, lambda = L/Z.  The curve becomes

    (L^2 + L Z + a Z^2) X^2 = X^4 + b Z^4,

negation is lambda -> lambda + 1, and the q-power Frobenius is (X^2, L^2, Z^2).
This module implements the paper's Theorems 1-3 (doubling, its alternative
doubling, full addition, and the doubling-and-addition 2Q + P), the mixed
addition that Theorem 2 gives with Z_P = 1, the conversions, and Montgomery's
batched conversion to lambda-affine, all with counted field operations.

What is *proven* here: nothing beyond the paper's algebra.  What is *checked*:
every formula against the affine group law (binary.BinaryCurve) on random
points with random projective scalings, including P = Q, P = -Q and
2Q = +-P.  What is *measured*: the operations each formula executes
(``op_counts``) and those of whole scalar multiplications (``scalar_counts``),
next to the Lopez-Dahab (LD) counts of ``binary.py`` on the same scalars.

Counting conventions.  A field is a ``CountedField`` (or ``gls.Fq2``) that
counts general multiplications ``M``, squarings ``S``, inversions ``I`` (whose
Itoh-Tsujii multiplications and squarings are also in ``M`` and ``S``) and,
separately, multiplications by a curve constant ``Mc``.  A multiplication by
0 or 1 is not executed and not counted.  On the NIST curves a in {0, 1}, so
m_a is always free; b is a random field element on the B-curves, so a
multiplication by b is a full multiplication and is priced as one (``M + Mc``),
exactly as binary.py's LD doubling counts it.

    python -m harness.endosweep.lambdacoord --std-curves STD_CURVES --out-dir OUT
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import time

from . import binary as BI
from .binary import INF, _clmul, _spread

# ---------------------------------------------------------------------------
# the paper's own operation counts (Table 3, CHES 2013 archive PDF)
# ---------------------------------------------------------------------------

PAPER_SOURCE = ("T. Oliveira, J. Lopez, D. F. Aranha, F. Rodriguez-Henriquez, 'Lambda coordinates for binary "
                "elliptic curves', CHES 2013, Table 3, read from "
                "https://www.iacr.org/archive/ches2013/80860113/80860113.pdf "
                "(sha256 6fc2c8e9128b362136b391a4fbfe17bf823bb75fd67db5e110fd58dd850a16ac)")

# Table 3 of the paper: counts over F_{q^2}; m_a, m_b are multiplications by the curve constants a, b.
PAPER_TABLE3 = {
    "LD": {"full_addition": "13M + 4S", "mixed_addition": "8M + m_a + 5S", "doubling": "3M + m_a + m_b + 5S",
           "doubling_and_addition": "n/a"},
    "lambda": {"full_addition": "11M + 2S", "mixed_addition": "8M + 2S",
               "doubling": "4M + m_a + 4S  /  3M + m_a + m_b + 4S", "doubling_and_addition": "10M + m_a + 6S"},
}


# ---------------------------------------------------------------------------
# a counted F_{2^m} with constant multiplications kept apart
# ---------------------------------------------------------------------------

class CountedField(BI.Field):
    """binary.Field plus ``Mc`` (multiplications by a curve constant) and a quadratic solver."""

    def reset(self) -> None:
        super().reset()
        self.Mc = 0

    def counts(self) -> dict:
        return {"M": self.M, "S": self.S, "I": self.I, "Mc": self.Mc}

    @property
    def bits(self) -> int:
        return self.m

    def mul_const(self, c: int, z: int) -> int:
        self.Mc += 1
        return self.reduce(_clmul(c, z))

    def const_cost(self, c: int) -> float:
        """Field multiplications a multiplication by the constant c costs."""
        return 0.0 if c in (0, 1) else 1.0

    def sqr_raw(self, a: int) -> int:
        return self.reduce(_spread(a))

    def mul_raw(self, a: int, b: int) -> int:
        return self.reduce(_clmul(a, b))

    def solve_quadratic(self, c: int):
        """z with z^2 + z = c, or None (odd m only: the half-trace)."""
        if self.trace(c):
            return None
        return self.half_trace(c)

    def random(self, rng: random.Random) -> int:
        return rng.getrandbits(self.m)


def counted_field_from_entry(entry: dict) -> CountedField:
    F = BI.field_from_entry(entry)
    return CountedField(F.m, F.low)


# ---------------------------------------------------------------------------
# the affine reference for any a (binary.BinaryCurve insists on a in {0, 1})
# ---------------------------------------------------------------------------

class GeneralCurve(BI.BinaryCurve):
    """y^2 + xy = x^3 + a x^2 + b over a CountedField or an Fq2, any a; affine reference and LD.

    The affine ``add``/``dbl``/``mul_affine`` of binary.BinaryCurve already
    work for any a; ``on_curve``, the point sampler and the two LD formulas
    are generalised (a and b through ``mul_const``).
    """

    def __init__(self, F, a: int, b: int):
        if b == 0:
            raise ValueError("b = 0 is singular")
        self.F, self.a, self.b = F, a, b

    def _cmul(self, c: int, z: int) -> int:
        if c == 0:
            return 0
        if c == 1:
            return z
        return self.F.mul_const(c, z)

    def on_curve(self, P) -> bool:
        if P is INF:
            return True
        F = self.F
        x, y = P
        x2 = F.sqr_raw(x)
        return F.sqr_raw(y) ^ F.mul_raw(x, y) == F.mul_raw(x2, x) ^ F.mul_raw(self.a, x2) ^ self.b

    def lift_x(self, x: int):
        F = self.F
        if x == 0:
            return (0, F.sqrt(self.b))
        x2 = F.sqr(x)
        c = x ^ self.a ^ F.mul(self.b, F.inv(x2))
        z = F.solve_quadratic(c)
        return None if z is None else (x, F.mul(x, z))

    def random_point(self, rng: random.Random):
        while True:
            P = self.lift_x(self.F.random(rng))
            if P is not None:
                return P

    def ld_dbl(self, P):
        """Lopez-Dahab doubling with general a, b: 2M + 5S + m_a + 2 m_b (binary.py's formula)."""
        F = self.F
        if P is INF or P[0] == 0:
            return INF
        X, Y, Z = P
        X2, Z2 = F.sqr(X), F.sqr(Z)
        Z3 = F.mul(X2, Z2)
        Z4 = F.sqr(Z2)
        bZ4 = self._cmul(self.b, Z4)
        X3 = F.sqr(X2) ^ bZ4
        inner = self._cmul(self.a, Z3) ^ F.sqr(Y) ^ bZ4
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
        D = F.mul(F.sqr(B), C ^ self._cmul(self.a, Z1s))
        Z3 = F.sqr(C)
        E = F.mul(A, C)
        X3 = F.sqr(A) ^ D ^ E
        Fv = X3 ^ F.mul(x2, Z3)
        G = F.mul(x2 ^ y2, F.sqr(Z3))
        return (X3, F.mul(E ^ Z3, Fv) ^ G, Z3)


# ---------------------------------------------------------------------------
# lambda coordinates
# ---------------------------------------------------------------------------

class LambdaCurve:
    """Counted lambda-projective arithmetic on y^2 + xy = x^3 + a x^2 + b.

    Points: ``INF``, lambda-affine ``(x, l)`` and lambda-projective ``(X, L, Z)``.
    ``dbl_formula`` is "main" (Theorem 1: 4M + 4S + m_a) or "alt" (the
    alternative L_2P: 3M + 4S + m_a + m_{a^2+b} with T = L(L + Z) + a Z^2);
    the default picks the cheaper one for this curve's constants.
    """

    def __init__(self, F, a: int, b: int, dbl_formula: str | None = None):
        self.F, self.a, self.b = F, a, b
        a2b = F.sqr_raw(a) ^ b
        self.const = {"a": a, "a+1": a ^ 1, "a^2+b": a2b}
        self.cm = {k: 0 for k in self.const}
        if dbl_formula is None:
            dbl_formula = "alt" if F.const_cost(a2b) < F.const_cost(-1) else "main"
        if dbl_formula not in ("main", "alt"):
            raise ValueError("dbl_formula is 'main' or 'alt'")
        self.dbl_formula = dbl_formula

    # --- helpers ----------------------------------------------------------
    def cmul(self, which: str, z: int) -> int:
        c = self.const[which]
        if c == 0:
            return 0
        if c == 1:
            return z
        self.cm[which] += 1
        return self.F.mul_const(c, z)

    def reset(self) -> None:
        self.F.reset()
        self.cm = {k: 0 for k in self.const}

    @staticmethod
    def lift(P):
        return INF if P is INF else (P[0], P[1], 1)

    @staticmethod
    def neg_aff(P):
        return INF if P is INF else (P[0], P[1] ^ 1)

    @staticmethod
    def neg(P):
        return INF if P is INF else (P[0], P[1] ^ P[2], P[2])

    def to_lambda_affine(self, P):
        """(x, y) -> (x, x + y/x): 1I + 1M."""
        if P is INF:
            return INF
        x, y = P
        if x == 0:
            raise ValueError("the point of order 2 (x = 0) has no lambda representation")
        return (x, x ^ self.F.mul(y, self.F.inv(x)))

    def from_lambda_affine(self, P):
        """(x, l) -> (x, y = x(l + x)): 1M."""
        return INF if P is INF else (P[0], self.F.mul(P[0], P[1] ^ P[0]))

    def to_affine(self, P):
        """(X, L, Z) -> (x, y): 1I + 3M."""
        if P is INF:
            return INF
        F = self.F
        zi = F.inv(P[2])
        x = F.mul(P[0], zi)
        return (x, F.mul(x, F.mul(P[1], zi) ^ x))

    def batch_to_lambda_affine(self, Ps: list):
        """Montgomery's simultaneous inversion: 3(k-1)M + 1I, then 2M per point."""
        F = self.F
        pts = [P for P in Ps if P is not INF]
        if not pts:
            return list(Ps)
        prods = [pts[0][2]]
        for P in pts[1:]:
            prods.append(F.mul(prods[-1], P[2]))
        inv = F.inv(prods[-1])
        zinv = [0] * len(pts)
        for i in range(len(pts) - 1, 0, -1):
            zinv[i] = F.mul(inv, prods[i - 1])
            inv = F.mul(inv, pts[i][2])
        zinv[0] = inv
        out = iter([(F.mul(P[0], zi), F.mul(P[1], zi)) for P, zi in zip(pts, zinv)])
        return [INF if P is INF else next(out) for P in Ps]

    # --- Theorem 1 ----------------------------------------------------------
    def dbl(self, P, formula: str | None = None):
        if P is INF:
            return INF
        F = self.F
        X, L, Z = P
        if (formula or self.dbl_formula) == "main":
            LZ = F.mul(L, Z)
            Z2 = F.sqr(Z)
            T = F.sqr(L) ^ LZ ^ self.cmul("a", Z2)
            if T == 0:
                raise ValueError("2P has x = 0 (P has order 4)")
            X2 = F.sqr(T)
            Z2P = F.mul(T, Z2)
            L2P = F.sqr(F.mul(X, Z)) ^ X2 ^ F.mul(T, LZ) ^ Z2P
            return (X2, L2P, Z2P)
        Z2 = F.sqr(Z)
        T = F.mul(L, L ^ Z) ^ self.cmul("a", Z2)
        if T == 0:
            raise ValueError("2P has x = 0 (P has order 4)")
        X2 = F.sqr(T)
        Z2P = F.mul(T, Z2)
        LX2 = F.sqr(L ^ X)
        L2P = F.mul(LX2, LX2 ^ T ^ Z2) ^ X2 ^ self.cmul("a+1", Z2P)
        if self.const["a^2+b"]:
            L2P ^= self.cmul("a^2+b", F.sqr(Z2))
        return (X2, L2P, Z2P)

    # --- Theorem 2 ----------------------------------------------------------
    def add(self, P, Q):
        """Full addition: 11M + 2S."""
        if P is INF:
            return Q
        if Q is INF:
            return P
        F = self.F
        XP, LP, ZP = P
        XQ, LQ, ZQ = Q
        XPZQ = F.mul(XP, ZQ)
        XQZP = F.mul(XQ, ZP)
        A = F.mul(LP, ZQ) ^ F.mul(LQ, ZP)
        Bs = XPZQ ^ XQZP
        if Bs == 0:
            return self.dbl(P) if A == 0 else INF
        B = F.sqr(Bs)
        AXQZP = F.mul(A, XQZP)
        X3 = F.mul(AXQZP, F.mul(A, XPZQ))
        if X3 == 0:
            raise ValueError("P + Q has x = 0")
        ABZQ = F.mul(F.mul(A, B), ZQ)
        L3 = F.sqr(AXQZP ^ B) ^ F.mul(ABZQ, LP ^ ZP)
        return (X3, L3, F.mul(ABZQ, ZP))

    def madd(self, Q, P):
        """Q (lambda-projective) + P (lambda-affine): Theorem 2 with Z_P = 1, 8M + 2S."""
        if P is INF:
            return Q
        if Q is INF:
            return self.lift(P)
        F = self.F
        XQ, LQ, ZQ = Q
        xP, lP = P
        XPZQ = F.mul(xP, ZQ)
        A = F.mul(lP, ZQ) ^ LQ
        Bs = XPZQ ^ XQ
        if Bs == 0:
            return self.dbl(Q) if A == 0 else INF
        B = F.sqr(Bs)
        AXQ = F.mul(A, XQ)
        X3 = F.mul(AXQ, F.mul(A, XPZQ))
        if X3 == 0:
            raise ValueError("P + Q has x = 0")
        ABZQ = F.mul(F.mul(A, B), ZQ)
        L3 = F.sqr(AXQ ^ B) ^ F.mul(ABZQ, lP ^ 1)
        return (X3, L3, ABZQ)

    # --- Theorem 3 ----------------------------------------------------------
    def dbl_add(self, Q, P):
        """2Q + P, Q lambda-projective and P lambda-affine: 10M + 6S + m_a.

        When 2Q = +-P (B = 0) the formula does not apply and the result is
        computed (and counted) as a doubling followed by a mixed addition.
        """
        if Q is INF:
            return self.lift(P)
        if P is INF:
            return self.dbl(Q)
        F = self.F
        XQ, LQ, ZQ = Q
        xP, lP = P
        LQ2 = F.sqr(LQ)
        ZQ2 = F.sqr(ZQ)
        T = LQ2 ^ F.mul(LQ, ZQ) ^ self.cmul("a", ZQ2)
        if T == 0:
            raise ValueError("2Q has x = 0 (Q has order 4)")
        A = F.mul(F.sqr(XQ), ZQ2) ^ F.mul(T, LQ2 ^ F.mul(self.a ^ 1 ^ lP, ZQ2))
        xZ = F.mul(xP, ZQ2)
        Bs = xZ ^ T
        if Bs == 0:
            return self.madd(self.dbl(Q), P)
        if A == 0:
            raise ValueError("2Q + P has x = 0")
        B = F.sqr(Bs)
        X = F.mul(xZ, F.sqr(A))
        Z = F.mul(F.mul(A, B), ZQ2)
        L = F.mul(T, F.sqr(A ^ B)) ^ F.mul(lP ^ 1, Z)
        return (X, L, Z)

    def frobenius(self, P):
        """(X^2, L^2, Z^2): 3S (lambda^2 = x^2 + y^2/x^2 is the lambda of the image)."""
        return INF if P is INF else (self.F.sqr(P[0]), self.F.sqr(P[1]), self.F.sqr(P[2]))


# ---------------------------------------------------------------------------
# formula checks against the affine group law
# ---------------------------------------------------------------------------

def _rand_proj(F, rng, P):
    """A random lambda-projective representative of the lambda-affine point P (uncounted)."""
    z = 0
    while z == 0:
        z = F.random(rng)
    return (F.mul_raw(P[0], z), F.mul_raw(P[1], z), z)


def _eq(C: LambdaCurve, E, R, Paff) -> bool:
    if R is INF or Paff is INF:
        return R is INF and Paff is INF
    return C.to_affine(R) == Paff


def verify_formulas(E, C: LambdaCurve, trials: int = 8, seed: int = 1) -> dict:
    """Every lambda formula against E's affine arithmetic, with random projective scalings and edge cases."""
    F = C.F
    rng = random.Random(seed)
    ok = {k: True for k in ("curve_equation", "conversions", "negation", "dbl_main", "dbl_alt", "full_add",
                            "mixed_add", "dbl_add", "frobenius", "edge_P_plus_minus_P", "edge_P_plus_P",
                            "edge_2Q_plus_minus_2Q", "edge_dbl_add_2Q_eq_P", "edge_infinity")}
    for _ in range(trials):
        P, Q = E.random_point(rng), E.random_point(rng)
        if P[0] == 0 or Q[0] == 0:
            continue
        Pl, Ql = C.to_lambda_affine(P), C.to_lambda_affine(Q)
        Pp, Qp = _rand_proj(F, rng, Pl), _rand_proj(F, rng, Ql)
        # the lambda-projective curve equation (L^2 + LZ + aZ^2) X^2 = X^4 + b Z^4
        X, L, Z = Pp
        Z2 = F.sqr_raw(Z)
        lhs = F.mul_raw(F.sqr_raw(L) ^ F.mul_raw(L, Z) ^ F.mul_raw(C.a, Z2), F.sqr_raw(X))
        ok["curve_equation"] &= lhs == F.sqr_raw(F.sqr_raw(X)) ^ F.mul_raw(C.b, F.sqr_raw(Z2))
        ok["conversions"] &= C.from_lambda_affine(Pl) == P and C.to_affine(Pp) == P
        ok["conversions"] &= C.batch_to_lambda_affine([Pp, INF, Qp]) == [Pl, INF, Ql]
        ok["negation"] &= _eq(C, E, C.neg(Pp), E.neg(P)) and C.from_lambda_affine(C.neg_aff(Pl)) == E.neg(P)
        P2 = E.dbl(P)
        ok["dbl_main"] &= _eq(C, E, C.dbl(Pp, "main"), P2)
        ok["dbl_alt"] &= _eq(C, E, C.dbl(Pp, "alt"), P2)
        PQ = E.add(P, Q)
        ok["full_add"] &= _eq(C, E, C.add(Pp, Qp), PQ) and _eq(C, E, C.add(Qp, Pp), PQ)
        ok["mixed_add"] &= _eq(C, E, C.madd(Qp, Pl), PQ)
        ok["dbl_add"] &= _eq(C, E, C.dbl_add(Qp, Pl), E.add(E.dbl(Q), P))
        ok["frobenius"] &= _eq(C, E, C.frobenius(Pp), E.frobenius(P))
        # edge cases
        mP = _rand_proj(F, rng, C.neg_aff(Pl))
        ok["edge_P_plus_minus_P"] &= C.add(Pp, mP) is INF and C.madd(Pp, C.neg_aff(Pl)) is INF
        ok["edge_P_plus_P"] &= _eq(C, E, C.add(Pp, _rand_proj(F, rng, Pl)), P2) and _eq(C, E, C.madd(Pp, Pl), P2)
        Q2l = C.to_lambda_affine(E.dbl(Q))
        if Q2l is not INF:
            ok["edge_2Q_plus_minus_2Q"] &= C.dbl_add(Qp, C.neg_aff(Q2l)) is INF
            ok["edge_dbl_add_2Q_eq_P"] &= _eq(C, E, C.dbl_add(Qp, Q2l), E.dbl(E.dbl(Q)))
        ok["edge_infinity"] &= (C.add(INF, Pp) == Pp and C.madd(INF, Pl) == C.lift(Pl) and C.dbl(INF) is INF
                                and _eq(C, E, C.dbl_add(INF, Pl), P) and C.madd(Pp, INF) == Pp)
    return ok


# ---------------------------------------------------------------------------
# per-operation counts
# ---------------------------------------------------------------------------

def _measure(C: LambdaCurve, fn, inv_cost: dict | None = None) -> dict:
    """Counts of one call; an inversion's own Itoh-Tsujii M and S are taken out (and reported once, apart)."""
    C.reset()
    fn()
    c = dict(C.F.counts())
    if inv_cost and c["I"]:
        for k in ("M", "S"):
            c[k] -= c["I"] * inv_cost[k]
    c["by_constant"] = {k: v for k, v in C.cm.items() if v}
    return c


def op_counts(E, C: LambdaCurve, seed: int = 2) -> dict:
    """The operations each lambda and LD formula executes on one generic input (constants as this curve has them)."""
    F = C.F
    rng = random.Random(seed)
    P, Q = E.random_point(rng), E.random_point(rng)
    Pl, Ql = C.to_lambda_affine(P), C.to_lambda_affine(Q)
    Pp, Qp = _rand_proj(F, rng, Pl), _rand_proj(F, rng, Ql)
    Pd = (F.mul_raw(P[0], Pp[2]), F.mul_raw(P[1], F.sqr_raw(Pp[2])), Pp[2])       # an LD representative of P
    C.reset()
    F.inv(Pp[2])
    inv = {k: F.counts()[k] for k in ("M", "S")}
    out = {
        "inversion": dict(inv, note="Itoh-Tsujii; conversions below are net of it"),
        "lambda": {
            "doubling_main": _measure(C, lambda: C.dbl(Pp, "main")),
            "doubling_alt": _measure(C, lambda: C.dbl(Pp, "alt")),
            "full_addition": _measure(C, lambda: C.add(Pp, Qp)),
            "mixed_addition": _measure(C, lambda: C.madd(Pp, Ql)),
            "doubling_and_addition": _measure(C, lambda: C.dbl_add(Pp, Ql)),
            "frobenius": _measure(C, lambda: C.frobenius(Pp)),
            "affine_to_lambda_affine": _measure(C, lambda: C.to_lambda_affine(P), inv),
            "lambda_projective_to_affine": _measure(C, lambda: C.to_affine(Pp), inv),
        },
        "LD": {
            "doubling": _measure(C, lambda: E.ld_dbl(Pd)),
            "mixed_addition": _measure(C, lambda: E.ld_madd(Pd, Q)),
            "frobenius": _measure(C, lambda: E.ld_frobenius(Pd)),
        },
        "dbl_formula_used": C.dbl_formula,
    }
    C.reset()
    return out


def fmt_counts(c: dict) -> str:
    parts = []
    if c.get("I"):
        parts.append(f"{c['I']}I")
    parts.append(f"{c['M']}M")
    for k, v in sorted(c.get("by_constant", {}).items()):
        parts.append(f"{v}m_({k})")
    if c.get("Mc") and not c.get("by_constant"):
        parts.append(f"{c['Mc']}m_c")
    parts.append(f"{c['S']}S")
    return " + ".join(parts)


# ---------------------------------------------------------------------------
# counted scalar multiplications with lambda coordinates (mirroring binary.py)
# ---------------------------------------------------------------------------

def _phase(F, before: dict) -> dict:
    now = F.counts()
    return {k: now[k] - before[k] for k in before}


def _odd_multiples(C: LambdaCurve, Pl, w: int) -> dict:
    """Odd multiples 1..2^(w-1)-1 of P in lambda-affine, computed as binary.mul_wnaf_counted does."""
    table = {1: Pl}
    if w > 2:
        mult = {1: C.lift(Pl)}
        for j in range(2, 1 << (w - 1)):
            mult[j] = C.dbl(mult[j // 2]) if j % 2 == 0 else C.madd(mult[j - 1], Pl)
        us = list(range(3, 1 << (w - 1), 2))
        for u, A in zip(us, C.batch_to_lambda_affine([mult[u] for u in us])):
            table[u] = A
    return table


def mul_wnaf_lambda(C: LambdaCurve, k: int, P, w: int, da: bool = False):
    """Width-w NAF with a lambda-projective accumulator; da=True fuses each doubling and its addition (Theorem 3)."""
    F = C.F
    C.reset()
    Pl = C.to_lambda_affine(P)
    conv = F.counts()
    table = _odd_multiples(C, Pl, w)
    pre = _phase(F, conv)
    before = F.counts()
    Q = INF
    for d in reversed(BI.wnaf(k, w)):
        T = (table[d] if d > 0 else C.neg_aff(table[-d])) if d else None
        if Q is INF:
            Q = C.lift(T) if d else INF
        elif d and da:
            Q = C.dbl_add(Q, T)
        else:
            Q = C.dbl(Q)
            if d:
                Q = C.madd(Q, T)
    main = _phase(F, before)
    before = F.counts()
    R = C.to_affine(Q)
    return R, {"convert": conv, "precompute": pre, "main": main, "final": _phase(F, before), "total": F.counts()}


def mul_tnaf_lambda(C: LambdaCurve, kob: BI.Koblitz, k: int, P, w: int, consts=None):
    """Solinas' width-w TNAF with a lambda-projective accumulator (Frobenius = 3S), alpha_u P in lambda-affine."""
    F = C.F
    tw, alpha = consts or BI.tnaf_constants(kob, w)
    C.reset()
    Pl = C.to_lambda_affine(P)
    conv = F.counts()
    table = {1: Pl}
    us = [u for u in alpha if u != 1]
    if us:
        projs = []
        for u in us:
            Q = INF
            for d in reversed(BI.tnaf(alpha[u], kob, 2, 2, {1: (1, 0)})):
                if Q is not INF:
                    Q = C.frobenius(Q)
                if d:
                    Q = C.madd(Q, Pl if d[0] > 0 else C.neg_aff(Pl))
            projs.append(Q)
        for u, A in zip(us, C.batch_to_lambda_affine(projs)):
            table[u] = A
    pre = _phase(F, conv)
    before = F.counts()
    rho = kob.Z.reduce_mod((k, 0), kob.delta)
    Q = INF
    for d in reversed(BI.tnaf(rho, kob, w, tw, alpha)):
        if Q is not INF:
            Q = C.frobenius(Q)
        if d:
            Q = C.madd(Q, table[d[1]] if d[0] > 0 else C.neg_aff(table[d[1]]))
    main = _phase(F, before)
    before = F.counts()
    R = C.to_affine(Q)
    return R, {"convert": conv, "precompute": pre, "main": main, "final": _phase(F, before), "total": F.counts()}


def m_eq(c: dict, s_weight: float) -> float:
    """M + Mc + s_weight * S (a constant multiplication priced as a full one: b is random on the B-curves)."""
    return c["M"] + c.get("Mc", 0) + s_weight * c["S"]


def scalar_counts(E: BI.BinaryCurve, C: LambdaCurve, G, n: int, *, kob=None, widths=(2, 3, 4, 5, 6, 7),
                  scalars: int = 32, references: int = 2, seed: int = 20261006) -> dict:
    """LD (binary.py, unchanged) and lambda counts of k*G on the same scalars; every result cross-checked.

    The scalars are drawn exactly as ``binary.scalar_counts`` draws them, so
    the LD means reproduce research/endosweep_nist_20261006 to the digit.
    """
    rng = random.Random(seed)
    ks = [rng.randrange(1, n) for _ in range(scalars)]
    algos = [("ld", "wnaf", w) for w in widths] + [("lambda", "wnaf", w) for w in widths] \
        + [("lambda", "wnaf-da", w) for w in widths]
    if kob:
        algos += [("ld", "tnaf", w) for w in widths] + [("lambda", "tnaf", w) for w in widths]
    consts = {w: BI.tnaf_constants(kob, w) for w in widths} if kob else {}
    keys = ("M", "S", "I", "Mc")
    sums = {a: {**{k: 0 for k in keys}, "pre_M": 0, "pre_S": 0, "main_M": 0, "main_S": 0, "conv_M": 0, "conv_S": 0}
            for a in algos}
    agree = ref_ok = True
    for i, k in enumerate(ks):
        results = set()
        for a in algos:
            coord, alg, w = a
            if coord == "ld":
                R, c = (BI.mul_wnaf_counted(E, k, G, w) if alg == "wnaf"
                        else BI.mul_tnaf_counted(E, kob, k, G, w, consts[w]))
            elif alg == "tnaf":
                R, c = mul_tnaf_lambda(C, kob, k, G, w, consts[w])
            else:
                R, c = mul_wnaf_lambda(C, k, G, w, da=alg == "wnaf-da")
            results.add(R)
            s = sums[a]
            for key in keys:
                s[key] += c["total"].get(key, 0)
            for ph, tag in (("precompute", "pre"), ("main", "main"), ("convert", "conv")):
                if ph in c:
                    s[f"{tag}_M"] += c[ph]["M"] + c[ph].get("Mc", 0)
                    s[f"{tag}_S"] += c[ph]["S"]
        agree &= len(results) == 1
        if i < references:
            ref_ok &= results == {E.mul_affine(k, G)}
    out = {}
    for (coord, alg, w), s in sums.items():
        mean = {key: round(v / scalars, 2) for key, v in s.items()}
        conv = {"M": mean["conv_M"], "S": mean["conv_S"]}
        # primary columns: the input point already in the representation the method uses (lambda-affine for
        # lambda, as in the paper's accounting; affine for LD, which needs no conversion); "_conv" columns add
        # the one inversion that turns an (x, y) input into (x, x + y/x)
        mean["S_free_conv"] = round(m_eq(mean, 0.0), 1)
        mean["S_eq_M_conv"] = round(m_eq(mean, 1.0), 1)
        mean["S_free"] = round(mean["S_free_conv"] - m_eq(conv, 0.0), 1)
        mean["S_eq_M"] = round(mean["S_eq_M_conv"] - m_eq(conv, 1.0), 1)
        out[f"{coord}/{alg}/w{w}"] = mean
    return {"scalars": scalars, "references_checked": min(references, scalars), "all_algorithms_agree": agree,
            "reference_agrees": ref_ok, "configs": out}


def best(configs: dict, prefix: str, col: str) -> tuple[str, float]:
    cands = [(v[col], k) for k, v in configs.items() if k.startswith(prefix + "/")]
    cost, k = min(cands)
    return k.split("/")[-1], cost


# ---------------------------------------------------------------------------
# driver: every NIST binary curve
# ---------------------------------------------------------------------------

NIST_BINARY = ("K-163", "B-163", "K-233", "B-233", "K-283", "B-283", "K-409", "B-409", "K-571", "B-571")
HYPOTHESIS = ("lambda coordinates mainly save squarings in additions, so the best-TNAF/best-wNAF ratio with S = M "
              "rises from 1.61-1.64 to >= 1.70 on every K-curve, while the S-free ratio moves by < 3%")


def nist_binary_curve(c: dict, scalars: int, widths, seed: int) -> dict:
    from .corpus import _int
    F = counted_field_from_entry(c["field"])
    a, b = _int(c["params"]["a"]), _int(c["params"]["b"])
    E = GeneralCurve(F, a, b)
    n, h = _int(c["order"]), _int(c["cofactor"])
    G = (_int(c["generator"]["x"]), _int(c["generator"]["y"]))
    v = BI.verify(BI.BinaryCurve(F, a, b), n, h, G)
    res = {"m": F.m, "a": a, "koblitz": b == 1, "log2_n": round(math.log2(n), 3),
           "verified": v.ok, "verification": v.note}
    if not v.ok:
        return res
    C = LambdaCurve(F, a, b)
    res["formula_checks"] = verify_formulas(E, C, trials=6, seed=11)
    res["op_counts"] = op_counts(E, C)
    kob = None
    if b == 1:
        kob, checks = BI.koblitz(BI.BinaryCurve(F, a, b), n, h, G)
        res["koblitz_checks_pass"] = all(checks.values())
    t0 = time.time()
    sm = scalar_counts(BI.BinaryCurve(F, a, b), C, G, n, kob=kob, widths=widths, scalars=scalars, seed=seed)
    sm["seconds"] = round(time.time() - t0, 1)
    res["scalar_multiplication"] = sm
    cf = sm["configs"]
    summ = {}
    for col in ("S_free", "S_eq_M", "S_free_conv", "S_eq_M_conv"):
        row = {}
        for pre in ("ld/wnaf", "lambda/wnaf", "lambda/wnaf-da") + (("ld/tnaf", "lambda/tnaf") if kob else ()):
            w, cost = best(cf, pre, col)
            row[pre] = {"w": w, "cost": cost}
        if kob:
            row["ratio_ld"] = round(row["ld/wnaf"]["cost"] / row["ld/tnaf"]["cost"], 3)
            row["ratio_lambda"] = round(row["lambda/wnaf"]["cost"] / row["lambda/tnaf"]["cost"], 3)
            row["ratio_lambda_da"] = round(row["lambda/wnaf-da"]["cost"] / row["lambda/tnaf"]["cost"], 3)
        row["saving_wnaf"] = round(1 - row["lambda/wnaf"]["cost"] / row["ld/wnaf"]["cost"], 4)
        row["saving_wnaf_da"] = round(1 - row["lambda/wnaf-da"]["cost"] / row["ld/wnaf"]["cost"], 4)
        if kob:
            row["saving_tnaf"] = round(1 - row["lambda/tnaf"]["cost"] / row["ld/tnaf"]["cost"], 4)
        summ[col] = row
    res["summary"] = summ
    return res


def hypothesis_verdict(curves: dict) -> dict:
    """The handed-in hypothesis, judged on the primary columns and again with the input conversion included."""
    out = {"hypothesis": HYPOTHESIS}
    for basis, (sm_col, sf_col) in (("input_lambda_affine", ("S_eq_M", "S_free")),
                                    ("input_affine_with_conversion", ("S_eq_M_conv", "S_free_conv"))):
        rows = {}
        held_sm = held_sf = True
        for k, r in curves.items():
            if not r.get("koblitz") or "summary" not in r:
                continue
            s = r["summary"]
            sm_ld, sm_l = s[sm_col]["ratio_ld"], s[sm_col]["ratio_lambda"]
            sf_ld, sf_l = s[sf_col]["ratio_ld"], s[sf_col]["ratio_lambda"]
            move = round(sf_l / sf_ld - 1, 4)
            rows[k] = {"S_eq_M_ratio_ld": sm_ld, "S_eq_M_ratio_lambda": sm_l,
                       "S_eq_M_ratio_lambda_da": s[sm_col]["ratio_lambda_da"], "S_free_ratio_ld": sf_ld,
                       "S_free_ratio_lambda": sf_l, "S_free_ratio_lambda_da": s[sf_col]["ratio_lambda_da"],
                       "S_free_relative_move": move}
            held_sm &= sm_l >= 1.70
            held_sf &= abs(move) < 0.03
        out[basis] = {"per_curve": rows, "S_eq_M_part_held": held_sm, "S_free_part_held": held_sf,
                      "held": held_sm and held_sf}
    return out


def markdown(doc: dict) -> str:
    L = ["# Lambda coordinates on the NIST binary curves (counted)", ""]
    L.append(f"Paper counts: {PAPER_SOURCE}.")
    L.append("")
    L.append("## Per-operation counts, measured (this harness) vs the paper's Table 3")
    L.append("")
    L.append("| curve | formula | measured | paper (Table 3, over F_q2) |")
    L.append("|:--|:--|:--|:--|")
    pmap = {"doubling_main": "4M + m_a + 4S", "doubling_alt": "3M + m_a + m_b + 4S",
            "full_addition": "11M + 2S", "mixed_addition": "8M + 2S", "doubling_and_addition": "10M + m_a + 6S",
            "frobenius": "-", "affine_to_lambda_affine": "-", "lambda_projective_to_affine": "-"}
    for name in ("nist/K-163", "nist/B-163"):
        r = doc["curves"].get(name)
        if not r:
            continue
        for op, c in r["op_counts"]["lambda"].items():
            L.append(f"| {name[5:]} | lambda {op} | {fmt_counts(c)} | {pmap[op]} |")
        lmap = {"doubling": "3M + m_a + m_b + 5S", "mixed_addition": "8M + m_a + 5S", "frobenius": "-"}
        for op, c in r["op_counts"]["LD"].items():
            L.append(f"| {name[5:]} | LD {op} | {fmt_counts(c)} | {lmap[op]} |")
    L.append("")
    L.append("On the NIST curves a is 0 or 1, so every m_a is free; b = 1 on the K-curves (m_b free, and the")
    L.append("alternative doubling's (a^2+b) Z^4 term vanishes on K-163, a = 1); on the B-curves a multiplication")
    L.append("by b is a full multiplication, counted as M (LD) or m_c (lambda) and priced as M.")
    L.append("")
    L.append("## Scalar multiplication k*G: best width, mean field operations (32 scalars)")
    L.append("")
    for col, title in (("S_free", "squarings free (M + m_c), input lambda-affine"),
                       ("S_eq_M", "S = M (M + m_c + S), input lambda-affine"),
                       ("S_free_conv", "squarings free, input affine (conversion included)"),
                       ("S_eq_M_conv", "S = M, input affine (conversion included)")):
        L.append(f"### {title}")
        L.append("")
        L.append("| curve | LD wNAF | lambda wNAF | lambda wNAF+DA | LD TNAF | lambda TNAF | ratio LD | ratio lambda "
                 "| ratio lambda (DA) | lambda saving wNAF / wNAF+DA / TNAF |")
        L.append("|:--|--:|--:|--:|--:|--:|--:|--:|--:|:--|")
        for name, r in doc["curves"].items():
            if "summary" not in r:
                continue
            s = r["summary"][col]

            def cell(p):
                return f"{s[p]['cost']:.0f} ({s[p]['w']})" if p in s else "-"
            sv = f"{100 * s['saving_wnaf']:.1f}% / {100 * s['saving_wnaf_da']:.1f}%"
            sv += f" / {100 * s['saving_tnaf']:.1f}%" if "saving_tnaf" in s else ""
            L.append(f"| {name[5:]} | {cell('ld/wnaf')} | {cell('lambda/wnaf')} | {cell('lambda/wnaf-da')} | "
                     f"{cell('ld/tnaf')} | {cell('lambda/tnaf')} | {s.get('ratio_ld', '-')} | "
                     f"{s.get('ratio_lambda', '-')} | {s.get('ratio_lambda_da', '-')} | {sv} |")
        L.append("")
    hv = doc["hypothesis"]
    L.append("## Hypothesis")
    L.append("")
    L.append(f"> {hv['hypothesis']}")
    L.append("")
    for basis, title in (("input_lambda_affine", "input point already lambda-affine (primary)"),
                         ("input_affine_with_conversion", "input point affine, conversion (1I + 1M) included")):
        h = hv[basis]
        L.append(f"**{title}**: S = M part held: **{h['S_eq_M_part_held']}**; "
                 f"S-free part held: **{h['S_free_part_held']}**.")
        L.append("")
        L.append("| curve | S=M ratio LD | S=M ratio lambda | S=M ratio lambda (wNAF+DA) | S-free ratio LD | "
                 "S-free ratio lambda | S-free ratio lambda (wNAF+DA) | S-free move |")
        L.append("|:--|--:|--:|--:|--:|--:|--:|--:|")
        for k, r in h["per_curve"].items():
            L.append(f"| {k[5:]} | {r['S_eq_M_ratio_ld']} | {r['S_eq_M_ratio_lambda']} | "
                     f"{r['S_eq_M_ratio_lambda_da']} | {r['S_free_ratio_ld']} | {r['S_free_ratio_lambda']} | "
                     f"{r['S_free_ratio_lambda_da']} | {100 * r['S_free_relative_move']:+.1f}% |")
        L.append("")
    L.append("## Every configuration")
    L.append("")
    L.append("Means over the scalars; M, m_c, S, I include the input conversion (lambda only: 1I + 1M), the last")
    L.append("two columns exclude it.")
    L.append("")
    L.append("| curve | config | M | m_c | S | I | precompute M / S | main loop M / S | S free | S = M |")
    L.append("|:--|:--|--:|--:|--:|--:|--:|--:|--:|--:|")
    for name, r in doc["curves"].items():
        for cfg, v in r.get("scalar_multiplication", {}).get("configs", {}).items():
            L.append(f"| {name[5:]} | {cfg} | {v['M']} | {v['Mc']} | {v['S']} | {v['I']} | {v['pre_M']} / {v['pre_S']} "
                     f"| {v['main_M']} / {v['main_S']} | {v['S_free']} | {v['S_eq_M']} |")
    L.append("")
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="lambda coordinates on the NIST binary curves, counted")
    ap.add_argument("--std-curves", required=True, help="a J08nY/std-curves checkout")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--scalars", type=int, default=32)
    ap.add_argument("--widths", default="2,3,4,5,6,7")
    ap.add_argument("--curves", default=",".join(NIST_BINARY))
    ap.add_argument("--seed", type=int, default=20261006)
    args = ap.parse_args(argv)
    widths = tuple(int(w) for w in args.widths.split(","))
    raw = {c["name"]: c for c in json.load(open(os.path.join(args.std_curves, "nist", "curves.json")))["curves"]}
    from .nist import _git_head
    doc = {"std_curves_commit": _git_head(args.std_curves), "paper": PAPER_SOURCE, "paper_table3": PAPER_TABLE3,
           "scalars": args.scalars, "widths": list(widths), "seed": args.seed, "curves": {}}
    for name in args.curves.split(","):
        t0 = time.time()
        r = nist_binary_curve(raw[name], args.scalars, widths, args.seed)
        r["elapsed_s"] = round(time.time() - t0, 1)
        doc["curves"][f"nist/{name}"] = r
        print(f"[{r['elapsed_s']:7.1f}s] {name} verified={r['verified']} checks={all(r['formula_checks'].values())} "
              f"{r.get('summary', {}).get('S_eq_M', '')}", flush=True)
    doc["hypothesis"] = hypothesis_verdict(doc["curves"])
    os.makedirs(args.out_dir, exist_ok=True)
    with open(os.path.join(args.out_dir, "lambda.json"), "w") as f:
        json.dump(doc, f, indent=1, default=str)
        f.write("\n")
    with open(os.path.join(args.out_dir, "lambda.md"), "w") as f:
        f.write(markdown(doc))
    bad = [n for n, r in doc["curves"].items() if not r.get("verified") or not all(r["formula_checks"].values())
           or not (r["scalar_multiplication"]["all_algorithms_agree"] and r["scalar_multiplication"]["reference_agrees"])
           or (r.get("koblitz") and not r.get("koblitz_checks_pass"))]
    print("failed:", bad)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
