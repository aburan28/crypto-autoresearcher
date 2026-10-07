"""EXP-SEMBIN-79a02d -- Sage-free core: GF(2^n) arithmetic, independent Weil
descent of Semaev eq. (5) (t = 3, chained S_3), binary-curve points, the
DREG-compatible generator hash, field-level solution enumeration (E1), the
support-matched null, and the known-false constructions.

Written for TASK-20261002-fc71d6 from the frozen S_3 formula
(inputs/SEMAEV-2015-310/paper_fulltext.md eq. (14)):
    S_3(a,b,c) = (ab + ac + bc)^2 + abc + B.
No code from src/ is imported (src/ needs Sage); src/semaev_tree.py was read as
a reference for variable ordering and the hash format only.

Field elements are Python ints: bit l = coefficient of alpha^l in the power
basis of F_2[X]/(modulus).
Boolean monomials are Python ints used as bitmasks over the N variables
(N <= 64), variable order u1_0..u1_{n-1}, x1_0..x1_{k-1}, x2_*, x3_*.
A Boolean polynomial is a Python set of monomial bitmasks (coefficient 1).
"""
from __future__ import annotations

import hashlib
import random
from itertools import combinations

# ---------------------------------------------------------------- GF(2^n)

CONWAY = {  # candidate default moduli (bit i = coeff of X^i); verified in Stage 1 by hash match
    12: (1 << 12) | (1 << 7) | (1 << 6) | (1 << 5) | (1 << 3) | (1 << 1) | 1,
    15: (1 << 15) | (1 << 5) | (1 << 4) | (1 << 2) | 1,
}


class GF2n:
    def __init__(self, n: int, modulus: int):
        assert modulus >> n == 1
        self.n, self.mod = n, modulus
        self.mask = (1 << n) - 1
        # Tr(alpha^i) table for the trace and the linear map for w -> w^2 + w
        self._tr = [self.trace_slow(1 << i) for i in range(n)]

    def mul(self, a: int, b: int) -> int:
        r = 0
        while b:
            if b & 1:
                r ^= a
            b >>= 1
            a <<= 1
            if a >> self.n:
                a ^= self.mod
        return r

    def sq(self, a: int) -> int:
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
        assert a
        return self.pow(a, (1 << self.n) - 2)

    def alpha_pow(self, e: int) -> int:
        return self.pow(2, e)

    def trace_slow(self, a: int) -> int:
        t, x = 0, a
        for _ in range(self.n):
            t ^= x
            x = self.sq(x)
        assert t in (0, 1)
        return t

    def trace(self, a: int) -> int:
        t = 0
        i = 0
        while a:
            if a & 1:
                t ^= self._tr[i]
            a >>= 1
            i += 1
        return t

    def sqrt(self, a: int) -> int:
        return self.pow(a, 1 << (self.n - 1))

    def solve_artin_schreier(self, c: int):
        """All w with w^2 + w = c (0 or 2 solutions)."""
        if self.trace(c):
            return []
        # linear system over F_2: L(w) = w^2 + w ; solve by Gaussian elimination
        n = self.n
        cols = [self.sq(1 << i) ^ (1 << i) for i in range(n)]  # L(e_i)
        # rows: augmented matrix in terms of unknown bits
        rows = []
        for r in range(n):
            v = 0
            for i in range(n):
                if (cols[i] >> r) & 1:
                    v |= 1 << i
            rows.append([v, (c >> r) & 1])
        piv_rows = []
        used = [False] * n
        for col in range(n):
            pr = None
            for ri in range(n):
                if not used[ri] and (rows[ri][0] >> col) & 1:
                    pr = ri
                    break
            if pr is None:
                continue
            used[pr] = True
            for ri in range(n):
                if ri != pr and (rows[ri][0] >> col) & 1:
                    rows[ri][0] ^= rows[pr][0]
                    rows[ri][1] ^= rows[pr][1]
            piv_rows.append((col, pr))
        for ri in range(n):
            if not used[ri] and rows[ri][0] == 0 and rows[ri][1]:
                return []
        w = 0
        for col, pr in piv_rows:
            if rows[pr][1]:
                w |= 1 << col  # free variables set to 0
        assert self.sq(w) ^ w == c
        return [w, w ^ 1]


def is_irreducible(poly: int, n: int) -> bool:
    """Rabin-style check via X^(2^n) == X mod poly and gcd conditions (small n)."""
    def pmulmod(a, b):
        r = 0
        while b:
            if b & 1:
                r ^= a
            b >>= 1
            a <<= 1
            if a >> n:
                a ^= poly
        return r

    def pgcd(a, b):
        while b:
            while a and a.bit_length() >= b.bit_length():
                a ^= b << (a.bit_length() - b.bit_length())
            a, b = b, a
        return a
    x = 2
    powers = [x]
    for _ in range(n):
        x = pmulmod(x, x)
        powers.append(x)
    if powers[n] != 2:
        return False
    for p in range(2, n + 1):
        if n % p == 0:
            h = powers[n // p] ^ 2
            if pgcd(poly, h) != 1:
                return False
    return True


# ---------------------------------------------------------------- descent

class Layout:
    def __init__(self, n: int, k: int):
        self.n, self.k = n, k
        self.N = n + 3 * k
        self.u = [j for j in range(n)]
        self.x = [[n + i * k + j for j in range(k)] for i in range(3)]

    def names(self):
        return ([f"u1_{j}" for j in range(self.n)] +
                [f"x{i+1}_{j}" for i in range(3) for j in range(self.k)])


def _add(d: dict, mono: int, c: int):
    v = d.get(mono, 0) ^ c
    if v:
        d[mono] = v
    else:
        d.pop(mono, None)


def descend_S3_vars(F: GF2n, L: Layout, B: int):
    """F_q-coefficient dict of S_3(u1, x1, x2) over Boolean monomials."""
    n, k = L.n, L.k
    d: dict = {}
    a2 = [F.alpha_pow(e) for e in range(4 * n)]
    U, X1, X2 = L.u, L.x[0], L.x[1]
    # (u x1)^2, (u x2)^2, (x1 x2)^2
    for (A, ea), (Bv, eb) in (((U, n), (X1, k)), ((U, n), (X2, k)), ((X1, k), (X2, k))):
        for a in range(ea):
            for b in range(eb):
                _add(d, (1 << A[a]) | (1 << Bv[b]), a2[2 * (a + b)])
    # u x1 x2
    for a in range(n):
        for b in range(k):
            for c in range(k):
                _add(d, (1 << U[a]) | (1 << X1[b]) | (1 << X2[c]), a2[a + b + c])
    _add(d, 0, B)
    return d


def descend_S3_const(F: GF2n, L: Layout, B: int, z: int, xi: int = 2):
    """F_q-coefficient dict of S_3(u1, x3, z) (z constant)."""
    n, k = L.n, L.k
    d: dict = {}
    U, X3 = L.u, L.x[xi]
    z2 = F.sq(z)
    for a in range(n):
        for b in range(k):
            ab = F.alpha_pow(a + b)
            _add(d, (1 << U[a]) | (1 << X3[b]), F.sq(ab) ^ F.mul(z, ab))
    for a in range(n):
        _add(d, 1 << U[a], F.mul(z2, F.alpha_pow(2 * a)))
    for b in range(k):
        _add(d, 1 << X3[b], F.mul(z2, F.alpha_pow(2 * b)))
    _add(d, 0, B)
    return d


def coordinates(coeff_dict: dict, n: int):
    """Equate coefficients of alpha^l: list of n Boolean polys (sets)."""
    out = []
    for l in range(n):
        out.append({m for m, c in coeff_dict.items() if (c >> l) & 1})
    return out


def build_system(F: GF2n, L: Layout, B: int, z: int, corrupt=None):
    """Ordered generator list (nonzero only), DREG order: S3(u1,x1,x2) l=0..n-1,
    then S3(u1,x3,z) l=0..n-1. corrupt = (eq_index, l) flips that constant."""
    polys = coordinates(descend_S3_vars(F, L, B), L.n) + \
        coordinates(descend_S3_const(F, L, B, z), L.n)
    if corrupt is not None:
        j, l = corrupt
        polys[j * L.n + l] ^= {0}
    return [p for p in polys if p]


def monosets_hash(polys, N: int) -> str:
    """Identical byte format to src/h012c_block_m4ri.py:45-55."""
    h = hashlib.sha256()
    for f in polys:
        encoded = sorted(tuple(i for i in range(N) if (m >> i) & 1) for m in f)
        h.update(len(encoded).to_bytes(8, "big"))
        for mono in encoded:
            h.update(len(mono).to_bytes(4, "big"))
            for v in mono:
                h.update(v.to_bytes(4, "big"))
    return h.hexdigest()


def deg(m: int) -> int:
    return bin(m).count("1")


def poly_deg(f) -> int:
    return max((deg(m) for m in f), default=-1)


# ---------------------------------------------------------------- curve

class Curve:
    """y^2 + xy = x^3 + A x^2 + B over F."""

    def __init__(self, F: GF2n, A: int, B: int):
        self.F, self.A, self.B = F, A, B

    def lift_x(self, x: int):
        F = self.F
        if x == 0:
            return [(0, F.sqrt(self.B))]
        # y = x w : w^2 + w = x + A + B/x^2
        c = x ^ self.A ^ F.mul(self.B, F.inv(F.sq(x)))
        return [(x, F.mul(x, w)) for w in F.solve_artin_schreier(c)]

    def on_curve(self, P):
        if P is None:
            return True
        F = self.F
        x, y = P
        return F.sq(y) ^ F.mul(x, y) == F.mul(F.sq(x), x) ^ F.mul(self.A, F.sq(x)) ^ self.B

    def neg(self, P):
        return None if P is None else (P[0], P[0] ^ P[1])

    def add(self, P, Q):
        F = self.F
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if y1 ^ y2 == x2:  # Q = -P
                return None
            if x1 == 0:
                return None
            lam = x1 ^ F.mul(y1, F.inv(x1))
            x3 = F.sq(lam) ^ lam ^ self.A
            y3 = F.sq(x1) ^ F.mul(lam ^ 1, x3)
            return (x3, y3)
        lam = F.mul(y1 ^ y2, F.inv(x1 ^ x2))
        x3 = F.sq(lam) ^ lam ^ x1 ^ x2 ^ self.A
        y3 = F.mul(lam, x1 ^ x3) ^ x3 ^ y1
        return (x3, y3)


def V_elements(k: int):
    return list(range(1 << k))  # polynomials in alpha of degree < k


def planted_z(F: GF2n, E: Curve, k: int, rng: random.Random, t: int = 3):
    cands = []
    for v in V_elements(k):
        cands.extend(E.lift_x(v))
    for _ in range(1000):
        pts = rng.sample(cands, t)
        R = None
        for P in pts:
            R = E.add(R, P)
        if R is not None and R[0] != 0:
            assert E.on_curve(R)
            return R[0], pts
    raise RuntimeError("no planted z")


# ---------------------------------------------------------------- enumeration E1

def S3_eval(F: GF2n, a: int, b: int, c: int, B: int) -> int:
    s = F.mul(a, b) ^ F.mul(a, c) ^ F.mul(b, c)
    return F.sq(s) ^ F.mul(F.mul(a, b), c) ^ B


def solve_quadratic(F: GF2n, a: int, b: int, c: int):
    """All u in F with a u^2 + b u + c = 0."""
    if a == 0 and b == 0:
        return None if c == 0 else []  # None = all of F
    if a == 0:
        return [F.mul(c, F.inv(b))]
    if b == 0:
        return [F.sqrt(F.mul(c, F.inv(a)))]
    # u = (b/a) w : w^2 + w = a c / b^2
    t = F.mul(F.mul(a, c), F.inv(F.sq(b)))
    ba = F.mul(b, F.inv(a))
    return [F.mul(ba, w) for w in F.solve_artin_schreier(t)]


def enumerate_field(F: GF2n, L: Layout, B: int, z: int, corrupt=None):
    """E1: all (u1, x1, x2, x3) with S3(u1,x1,x2) + c1 = 0, S3(u1,x3,z) + c2 = 0,
    u1 in F, x_i in V. corrupt (j, l) adds alpha^l to equation j.
    Returns sorted list of Boolean assignment bitmasks."""
    k, n = L.k, L.n
    c = [0, 0]
    if corrupt is not None:
        c[corrupt[0]] ^= 1 << corrupt[1]
    Vs = V_elements(k)
    sols = []
    for x1 in Vs:
        for x2 in Vs:
            # S3(u,x1,x2) = u^2 (x1+x2)^2 + u x1 x2 + (x1 x2)^2 + B
            s = x1 ^ x2
            p = F.mul(x1, x2)
            us = solve_quadratic(F, F.sq(s), p, F.sq(p) ^ B ^ c[0])
            if us is None:
                us = range(1 << n)
            for u in us:
                assert S3_eval(F, u, x1, x2, B) ^ c[0] == 0
                for x3 in Vs:
                    if S3_eval(F, u, x3, z, B) ^ c[1] == 0:
                        sols.append(assignment(L, u, (x1, x2, x3)))
    return sorted(sols)


def assignment(L: Layout, u: int, xs) -> int:
    m = 0
    for j in range(L.n):
        if (u >> j) & 1:
            m |= 1 << L.u[j]
    for i in range(3):
        for j in range(L.k):
            if (xs[i] >> j) & 1:
                m |= 1 << L.x[i][j]
    return m


def eval_poly(f, pt: int) -> int:
    return sum(1 for m in f if (m & pt) == m) & 1


# ---------------------------------------------------------------- null

def boolean_null(polys, N: int, rng: random.Random):
    """Support-matched null: same per-degree monomial counts per generator,
    distinct random square-free monomials (rule of src/h012_peel_rank.py:30-47)."""
    out = []
    for f in polys:
        by_deg = {}
        for m in f:
            by_deg[deg(m)] = by_deg.get(deg(m), 0) + 1
        nf = set()
        for d in sorted(by_deg):
            cnt = by_deg[d]
            got = 0
            while got < cnt:
                mm = 0
                for v in rng.sample(range(N), d):
                    mm |= 1 << v
                if mm not in nf:
                    nf.add(mm)
                    got += 1
        out.append(nf)
    return out


# ---------------------------------------------------------------- semi-regular prediction

def semireg_rank_pred(eq_degs, nb, Dmax):
    """Re-implementation of src/h012_peel_rank.py:50-67."""
    from math import comb
    # forward in-place recurrence exactly as written in h012_peel_rank.py
    a = [comb(nb, j) if j <= nb else 0 for j in range(Dmax + 2)]
    for d in eq_degs:
        for j in range(d, Dmax + 2):
            a[j] -= a[j - d]
    HF, ok = [], True
    for d in range(Dmax + 2):
        if not ok or a[d] <= 0:
            HF.append(0)
            if a[d] <= 0:
                ok = False
        else:
            HF.append(a[d])
    pred, tot = {}, 0
    for D in range(0, Dmax + 1):
        tot += comb(nb, D) - HF[D]
        pred[D] = tot
    return pred, HF
