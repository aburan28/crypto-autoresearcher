#!/usr/bin/env python3
"""Vectorised F_{2^n} and binary-curve arithmetic for EXP-SEMBIN-354a75.

WHY THIS EXISTS. `binary_field.py` is the readable reference implementation and
every result here is checked against it (`selftest_fastfield.py`), but it costs
tens of microseconds per field inversion, and the contract's largest cell needs
roughly 8.4 million point additions per enumeration. This module is the same
arithmetic expressed over numpy arrays, with one structural change: a
log/antilog (Zech) table per field, which turns multiplication and inversion
into gathers. The tables are 2^n entries, so they exist only because the
contract caps n at 24; nothing here would survive at cryptographic size, and
nothing here needs to.

WHAT IS NOT HERE. No Groebner engine, no Macaulay matrix, no summation
polynomial is ever constructed. The experiment COUNTS decompositions by adding
points, so the only algebra in this file is the group law.

TWO CURVES, ONE FIELD. For x in F_q the two curve y-values are either both in
F_q or both in F_{q^2} \\ F_q (Lemma 2's dichotomy). The second kind are exactly
the F_q-points of the QUADRATIC TWIST y^2 + xy = x^3 + (a+delta) x^2 + b with
Tr(delta) = 1, carried into E(F_{q^2}) by the isomorphism
(x, y) -> (x, y + x u) where u^2 + u = delta. That lets the whole experiment run
in F_q arithmetic on two curves instead of in F_{q^2}, and it makes the Lemma-2
bookkeeping explicit: a sum of twist points lands back in E(F_q) exactly when it
is the 2-torsion point or infinity, which is Lemma 2 part 1 as an arithmetic
condition rather than as a quoted result.
"""
from __future__ import annotations

import numpy as np

from binary_field import GF2m, modulus_for

U32 = np.uint32
U64 = np.uint64

INF_KEY = np.uint64(1) << np.uint64(60)


# --------------------------------------------------------------------------
# Field
# --------------------------------------------------------------------------
def _clmul_reduce_vec(arr: np.ndarray, s: int, n: int, modulus: int) -> np.ndarray:
    """Carry-less multiply a uint64 array by the scalar s, then reduce mod f."""
    acc = np.zeros(arr.shape, dtype=U64)
    bits = s
    while bits:
        low = bits & -bits
        acc ^= arr << U64(low.bit_length() - 1)
        bits ^= low
    for i in range(2 * n - 2, n - 1, -1):
        bit = (acc >> U64(i)) & U64(1)
        acc ^= U64(modulus << (i - n)) * bit
    return acc


class FastField:
    """F_{2^n} with log/antilog tables; elements are uint32, zero is 0.

    The modulus and the element encoding are identical to `binary_field.GF2m`,
    so the two implementations are directly comparable element by element, and
    `selftest_fastfield.py` compares them.
    """

    _CACHE: dict[int, "FastField"] = {}

    @classmethod
    def get(cls, n: int) -> "FastField":
        if n not in cls._CACHE:
            cls._CACHE[n] = cls(n)
        return cls._CACHE[n]

    def __init__(self, n: int) -> None:
        self.n = n
        self.slow = GF2m(n)
        self.modulus = self.slow.modulus
        self.q = 1 << n
        self.order = self.q - 1                      # order of F_q^*
        self.generator = self._find_primitive()
        self.antilog, self.logt = self._build_tables()
        self.trace_mask = sum((1 << i) for i in range(n)
                              if self.slow.trace(1 << i) == 1)
        self._quad_pivots = self._build_quadratic_solver()

    # -- construction ------------------------------------------------------
    def _factor(self, m: int) -> list[int]:
        out, d = [], 2
        while d * d <= m:
            if m % d == 0:
                out.append(d)
                while m % d == 0:
                    m //= d
            d += 1
        if m > 1:
            out.append(m)
        return out

    def _find_primitive(self) -> int:
        primes = self._factor(self.order)
        for g in range(2, self.q):
            if all(self.slow.pow(g, self.order // p) != 1 for p in primes):
                return g
        raise ArithmeticError("no primitive element found; field is malformed")

    def _build_tables(self) -> tuple[np.ndarray, np.ndarray]:
        """antilog[i] = g^i for i < q-1, and its inverse table.

        Built in blocks: the first block sequentially in Python, then
        antilog[jB + i] = g^{jB} * antilog[i] as one vectorised scalar
        multiplication per block. A purely sequential build costs 2^n Python
        iterations, which is seconds of wall clock at n = 24 for no reason.
        """
        size = self.order
        block = min(size, 1 << 16)
        antilog = np.zeros(size, dtype=U32)
        v = 1
        for i in range(block):
            antilog[i] = v
            v = self.slow.mul(v, self.generator)
        step = v                                      # g^block
        base = step
        j = block
        head = antilog[:block].astype(U64)
        while j < size:
            take = min(block, size - j)
            prod = _clmul_reduce_vec(head[:take], base, self.n, self.modulus)
            antilog[j:j + take] = prod.astype(U32)
            base = self.slow.mul(base, step)
            j += take
        logt = np.zeros(self.q, dtype=U32)
        logt[antilog] = np.arange(size, dtype=U32)
        return antilog, logt

    def _build_quadratic_solver(self):
        """Echelon form of the F_2-linear map z -> z^2 + z, computed once.

        `binary_field.GF2m.solve_quadratic` redoes this elimination on every
        call, which is fine for a reader and not fine for 2^12 factor-base
        x-values per cell times 36 cell configurations.
        """
        cols = [(self.slow.sqr(1 << i) ^ (1 << i), 1 << i) for i in range(self.n)]
        pivots = []
        for bit in reversed(range(self.n)):
            pick = next((i for i, (v, _s) in enumerate(cols) if v >> bit & 1), None)
            if pick is None:
                continue
            pv, ps = cols.pop(pick)
            cols = [(v ^ pv, s ^ ps) if v >> bit & 1 else (v, s) for v, s in cols]
            pivots.append((bit, pv, ps))
        return pivots

    # -- scalar helpers ----------------------------------------------------
    def solve_quadratic(self, c: int) -> int | None:
        """z in F_q with z^2 + z = c, or None. Verified before returning."""
        if c == 0:
            return 0
        target, combo = c, 0
        for bit, pv, ps in self._quad_pivots:
            if target >> bit & 1:
                target ^= pv
                combo ^= ps
        if target != 0:
            return None
        if self.slow.sqr(combo) ^ combo != c:
            raise ArithmeticError("quadratic solve returned a non-root")
        return combo

    def trace_scalar(self, v: int) -> int:
        return bin(v & self.trace_mask).count("1") & 1

    # -- vectorised field --------------------------------------------------
    def mul(self, a, b):
        a = np.asarray(a, dtype=U32)
        b = np.asarray(b, dtype=U32)
        s = self.logt[a].astype(np.int64) + self.logt[b].astype(np.int64)
        s = np.where(s >= self.order, s - self.order, s)
        r = self.antilog[s]
        return np.where((a == 0) | (b == 0), U32(0), r).astype(U32)

    def sqr(self, a):
        return self.mul(a, a)

    def inv(self, a):
        a = np.asarray(a, dtype=U32)
        l = self.logt[a].astype(np.int64)
        idx = np.where(l == 0, 0, self.order - l)
        return np.where(a == 0, U32(0), self.antilog[idx]).astype(U32)

    def div(self, a, b):
        b = np.asarray(b, dtype=U32)
        safe = np.where(b == 0, U32(1), b)
        return self.mul(a, self.inv(safe))

    def sqrt(self, a):
        a = np.asarray(a, dtype=U32)
        l = self.logt[a].astype(np.int64)
        idx = (l * (1 << (self.n - 1))) % self.order
        return np.where(a == 0, U32(0), self.antilog[idx]).astype(U32)

    def trace(self, a):
        a = np.asarray(a, dtype=U32)
        return (np.bitwise_count(a & U32(self.trace_mask)) & 1).astype(np.uint8)


# --------------------------------------------------------------------------
# Curve
# --------------------------------------------------------------------------
class FastCurve:
    """y^2 + xy = x^3 + a x^2 + b over a FastField, vectorised.

    Points are parallel uint32 arrays (X, Y) plus a boolean infinity mask, so a
    partial sum that collapses to the identity stays in the array instead of
    branching out of it. That matters for the chain condition: a prefix sum of
    infinity is exactly the degeneracy Lemma 2's proof has to exclude.
    """

    def __init__(self, field: FastField, a: int, b: int) -> None:
        if b == 0:
            raise ValueError("b = 0 is singular for this curve form")
        self.f = field
        self.a = U32(a)
        self.b = U32(b)
        self.t2 = (0, int(field.sqrt(np.array([b], dtype=U32))[0]))

    # -- membership --------------------------------------------------------
    def ys_for_x_scalar(self, x: int) -> list[int]:
        f = self.f
        if x == 0:
            return [self.t2[1]]
        c = x ^ int(self.a) ^ int(f.div(np.array([self.b]), f.sqr(np.array([x], dtype=U32)))[0])
        z = f.solve_quadratic(c)
        if z is None:
            return []
        y0 = int(f.mul(np.array([x], dtype=U32), np.array([z], dtype=U32))[0])
        return [y0, y0 ^ x]

    def on_curve(self, X, Y) -> np.ndarray:
        f = self.f
        lhs = f.sqr(Y) ^ f.mul(X, Y)
        rhs = f.mul(f.sqr(X), X) ^ f.mul(self.a, f.sqr(X)) ^ self.b
        return lhs == rhs

    # -- group law ---------------------------------------------------------
    def add(self, X1, Y1, I1, X2, Y2, I2):
        f = self.f
        X1 = np.asarray(X1, dtype=U32); Y1 = np.asarray(Y1, dtype=U32)
        X2 = np.asarray(X2, dtype=U32); Y2 = np.asarray(Y2, dtype=U32)
        I1 = np.asarray(I1, dtype=bool); I2 = np.asarray(I2, dtype=bool)
        same_x = X1 == X2
        # The two y-values over one x are y and y + x, so equal x with
        # Y1 ^ Y2 == X1 is precisely "negatives"; that also catches the
        # 2-torsion point doubling to infinity, where X1 = 0 and Y1 = Y2.
        neg = same_x & ((Y1 ^ Y2) == X1)
        dbl = same_x & ~neg

        den_gen = np.where(same_x, U32(1), X1 ^ X2)
        lam_gen = f.div(Y1 ^ Y2, den_gen)
        x3_gen = f.sqr(lam_gen) ^ lam_gen ^ X1 ^ X2 ^ self.a
        y3_gen = f.mul(lam_gen, X1 ^ x3_gen) ^ x3_gen ^ Y1

        xd = np.where(dbl, X1, U32(1))
        lam_dbl = xd ^ f.div(np.where(dbl, Y1, U32(0)), xd)
        x3_dbl = f.sqr(lam_dbl) ^ lam_dbl ^ self.a
        y3_dbl = f.sqr(xd) ^ f.mul(lam_dbl ^ U32(1), x3_dbl)

        X3 = np.where(dbl, x3_dbl, x3_gen).astype(U32)
        Y3 = np.where(dbl, y3_dbl, y3_gen).astype(U32)
        I3 = neg.copy()
        X3 = np.where(I3, U32(0), X3).astype(U32)
        Y3 = np.where(I3, U32(0), Y3).astype(U32)
        # Identity cases last, so they override the arithmetic above.
        X3 = np.where(I1, X2, np.where(I2, X1, X3)).astype(U32)
        Y3 = np.where(I1, Y2, np.where(I2, Y1, Y3)).astype(U32)
        I3 = np.where(I1, I2, np.where(I2, I1, I3))
        return X3, Y3, I3

    def negate(self, X, Y, I):
        return np.asarray(X, dtype=U32), (np.asarray(X, dtype=U32)
                                          ^ np.asarray(Y, dtype=U32)), np.asarray(I, dtype=bool)

    def key(self, X, Y, I) -> np.ndarray:
        k = (np.asarray(X, dtype=U64) << U64(self.f.n)) | np.asarray(Y, dtype=U64)
        return np.where(np.asarray(I, dtype=bool), INF_KEY, k)

    # -- counting ----------------------------------------------------------
    def group_order(self, chunk: int = 1 << 20) -> int:
        """#E(F_q) by direct count of the trace condition over every x.

        #E = 1 (infinity) + 1 (the x = 0 point) + 2 * #{x != 0 : Tr(x + a +
        b/x^2) = 0}. Exact, and independently cross-checked against the twist
        by #E + #E' = 2q + 2.
        """
        f = self.f
        total = 0
        for lo in range(1, f.q, chunk):
            hi = min(lo + chunk, f.q)
            xs = np.arange(lo, hi, dtype=U32)
            c = xs ^ self.a ^ f.div(np.full(xs.shape, self.b, dtype=U32), f.sqr(xs))
            total += int(np.count_nonzero(f.trace(c) == 0))
        return 2 + 2 * total


def twist_a(field: FastField, a: int) -> int:
    """a + delta for the smallest delta of absolute trace 1.

    Tr(a + delta) != Tr(a), so exactly the x with no F_q-rational y on E have
    one on this curve. delta is the same constant `binary_field` uses to build
    F_{q^2}, so the two constructions describe the same extension.
    """
    delta = next(d for d in range(1, field.q) if field.trace_scalar(d) == 1)
    return a ^ delta


def factor_base(curve: FastCurve, V: list[int]) -> dict:
    """Points of `curve` with x in V, as arrays, plus the Lemma-2 split.

    Returns the x-values that carry F_q-rational points ('rational'), the
    point arrays, and the x-values that do not ('irrational' for this curve).
    x = 0 always carries exactly one point, the 2-torsion point, and it is
    shared with the twist -- it is listed here and NOT in the twist's list,
    because its y lies in F_q and it is therefore a usable relation.
    """
    xs, ys, rational, missing = [], [], [], []
    for x in V:
        roots = curve.ys_for_x_scalar(x)
        if not roots:
            missing.append(x)
            continue
        rational.append(x)
        for y in roots:
            xs.append(x)
            ys.append(y)
    X = np.array(xs, dtype=U32)
    Y = np.array(ys, dtype=U32)
    assert bool(np.all(curve.on_curve(X, Y))), "factor base holds an off-curve point"
    return {
        "X": X, "Y": Y,
        "I": np.zeros(X.shape, dtype=bool),
        "keys": curve.key(X, Y, np.zeros(X.shape, dtype=bool)),
        "rational_xs": rational,
        "missing_xs": missing,
    }
