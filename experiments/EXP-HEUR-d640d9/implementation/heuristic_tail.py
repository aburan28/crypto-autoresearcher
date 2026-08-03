#!/usr/bin/env python3
"""
EXP-HEUR-d640d9 / RUN-HEUR-d640d9-a -- executor implementation.

Frozen contract: experiments/EXP-HEUR-d640d9/specification.yaml (status approved,
approved_by coordinator, frozen at commit dfe285d4).

WHAT THIS PROGRAM DOES.  It enumerates, exactly and in pure Python with integer /
rational arithmetic only, the complete type set of maximal orders in the
quaternion algebra B_{p,infinity} for every prime p in the contract's tier rule,
computes delta_E (the degree of the smallest isogeny E -> E^(p)) for every class
by two independent routes, and then evaluates the four pre-registered statistics
S1..S4 of section 5 of the contract together with every pre-registered null
object (NULL-A..NULL-C) and instrument-fidelity control (IF-1..IF-6).

WHAT THIS PROGRAM CANNOT DO (contract section 0, restated here so that no reader
of the code can miss it).  Heuristic 1 is a TAIL statement at u ~ 13.1.  The
primes reachable here give u <~ 4.5.  Nothing computed by this program can
confirm Heuristic 1, support P0, support any margin row, or support the attack;
and nothing computed here refutes Theorem 1.1 or the p^{1/3+o(1)} exponent
either (prohibition SP-H, binding in both directions).  This program records
observations.

No third-party package is imported.  No published table of class numbers,
delta_E values or supersingular counts is used as data: every number in the
output is computed here.
"""

import argparse
import itertools
import json
import math
import operator
import os
import random
import sys
import time
from decimal import Decimal, getcontext, localcontext
from fractions import Fraction

getcontext().prec = 60

# ===========================================================================
# 0.  Seeds -- copied verbatim from the frozen contract, section 7 replication
# ===========================================================================
SEEDS = {
    "master": 20260802,
    "walk_sampler": 20260802101,
    "monte_carlo_ks": 20260802102,
    "null_a": 20260802103,
    "null_b": 20260802104,
    "null_b2": 20260802105,
    "null_c": 20260802106,
    "pit_randomization": 20260802107,
    "tenfold_split": 20260802108,
    "route_f_sample": 20260802109,
    "bootstrap": 20260802110,
}

B_GRID = [2, 3, 5, 7, 11, 13, 17, 19]
WEIGHTINGS = ["W-CURVE", "W-TYPE", "W-MASS"]
MC_REPLICATES = 10000       # contract-fixed: S1a "10,000 resamples"
NULL_REPLICATIONS = 200     # contract-fixed: NULL-B / NULL-B2 "200 replications"
BOOTSTRAP_REPLICATES = 10000  # contract-fixed: S4 bootstrap and NULL-C

# The contract fixes replicate counts for S1a, for the S4 bootstrap and for
# NULL-C, but says only "with a Monte-Carlo null" for the S3 randomised-PIT
# goodness-of-fit test.  This count is therefore an EXECUTOR CHOICE, declared
# here and reported in raw-result.json with its resolution floor: the smallest
# attainable p-value is 1/(PIT_MC_REPLICATES + 1), which must be below the
# contract's 0.001 rejection threshold for the test to be able to fire at all.
PIT_MC_REPLICATES = 10000

TIERS = [
    ("TIER-0", 11, 199, True),
    ("TIER-1", 200, 2000, True),
    ("TIER-2", 2001, 8000, False),
    ("TIER-3", 8001, 22000, False),
]


# ===========================================================================
# 1.  Exact linear algebra over Z and Q
# ===========================================================================
def hnf(rows, ncols):
    M = [list(r) for r in rows if any(r)]
    r = 0
    for c in range(ncols):
        piv = None
        for i in range(r, len(M)):
            if M[i][c] != 0:
                piv = i
                break
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        for i in range(r + 1, len(M)):
            while M[i][c] != 0:
                q = M[r][c] // M[i][c]
                M[r] = [a - q * b for a, b in zip(M[r], M[i])]
                M[r], M[i] = M[i], M[r]
        if M[r][c] < 0:
            M[r] = [-a for a in M[r]]
        for i in range(r):
            q = M[i][c] // M[r][c]
            if q:
                M[i] = [a - q * b for a, b in zip(M[i], M[r])]
        r += 1
        if r == len(M):
            break
    return [row for row in M if any(row)]


def det_rat(M):
    n = len(M)
    A = [[Fraction(x) for x in row] for row in M]
    det = Fraction(1)
    for c in range(n):
        piv = None
        for i in range(c, n):
            if A[i][c] != 0:
                piv = i
                break
        if piv is None:
            return Fraction(0)
        if piv != c:
            A[c], A[piv] = A[piv], A[c]
            det = -det
        det *= A[c][c]
        inv = A[c][c]
        for i in range(c + 1, n):
            if A[i][c] != 0:
                f = A[i][c] / inv
                A[i] = [a - f * b for a, b in zip(A[i], A[c])]
    return det


def inverse_rat(M):
    n = len(M)
    A = [[Fraction(x) for x in row] + [Fraction(1 if i == j else 0) for j in range(n)]
         for i, row in enumerate(M)]
    for c in range(n):
        piv = next(i for i in range(c, n) if A[i][c] != 0)
        A[c], A[piv] = A[piv], A[c]
        pv = A[c][c]
        A[c] = [x / pv for x in A[c]]
        for i in range(n):
            if i != c and A[i][c] != 0:
                f = A[i][c]
                A[i] = [x - f * y for x, y in zip(A[i], A[c])]
    return [row[n:] for row in A]


def isqrt_exact(n):
    if n < 0:
        return None
    r = math.isqrt(n)
    return r if r * r == n else None


def kernel_basis(A, n):
    """Basis of {c in Z^n : A c = 0} for an integer matrix A given by rows."""
    m = len(A)
    cols = [[A[i][j] for i in range(m)] for j in range(n)]
    U = [[1 if i == j else 0 for i in range(n)] for j in range(n)]
    r = 0
    for i in range(m):
        piv = None
        for j in range(r, n):
            if cols[j][i] != 0:
                piv = j
                break
        if piv is None:
            continue
        cols[r], cols[piv] = cols[piv], cols[r]
        U[r], U[piv] = U[piv], U[r]
        for j in range(r + 1, n):
            while cols[j][i] != 0:
                q = cols[r][i] // cols[j][i]
                cols[r] = [a - q * b for a, b in zip(cols[r], cols[j])]
                U[r] = [a - q * b for a, b in zip(U[r], U[j])]
                cols[r], cols[j] = cols[j], cols[r]
                U[r], U[j] = U[j], U[r]
        r += 1
        if r == n:
            break
    return [U[j] for j in range(n) if not any(cols[j])]


# ===========================================================================
# 2.  Quaternion algebra and lattices
# ===========================================================================
class Quat:
    """B = (a,b): i^2=a, j^2=b, k=ij, ji=-k, ik=aj, ki=-aj, jk=-bi, kj=bi."""

    __slots__ = ("a", "b")

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def mul(self, x, y):
        a, b = self.a, self.b
        x0, x1, x2, x3 = x
        y0, y1, y2, y3 = y
        return (x0 * y0 + a * x1 * y1 + b * x2 * y2 - a * b * x3 * y3,
                x0 * y1 + x1 * y0 - b * x2 * y3 + b * x3 * y2,
                x0 * y2 + x2 * y0 + a * x1 * y3 - a * x3 * y1,
                x0 * y3 + x3 * y0 + x1 * y2 - x2 * y1)

    def conj(self, x):
        return (x[0], -x[1], -x[2], -x[3])

    def nrd(self, x):
        a, b = self.a, self.b
        return x[0] * x[0] - a * x[1] * x[1] - b * x[2] * x[2] + a * b * x[3] * x[3]

    def trd(self, x):
        return 2 * x[0]

    def bil(self, x, y):
        a, b = self.a, self.b
        return x[0] * y[0] - a * x[1] * y[1] - b * x[2] * y[2] + a * b * x[3] * y[3]


class Lattice:
    __slots__ = ("M", "den")

    def __init__(self, M, den):
        g = den
        for row in M:
            for x in row:
                g = math.gcd(g, x)
        if g > 1:
            M = [[x // g for x in row] for row in M]
            den //= g
        self.M = tuple(tuple(r) for r in hnf(M, 4))
        self.den = den

    def basis(self):
        d = self.den
        return [tuple(Fraction(x, d) for x in row) for row in self.M]

    def det(self):
        return det_rat([list(r) for r in self.M]) / Fraction(self.den) ** 4

    def coords(self, v):
        num = []
        for x in v:
            y = Fraction(x) * self.den
            if y.denominator != 1:
                return None
            num.append(int(y))
        n = len(self.M)
        out = [0] * n
        w = list(num)
        for i in range(n):
            c = next(cc for cc in range(4) if self.M[i][cc] != 0)
            if w[c] % self.M[i][c] != 0:
                return None
            q = w[c] // self.M[i][c]
            out[i] = q
            if q:
                for cc in range(4):
                    w[cc] -= q * self.M[i][cc]
        return None if any(w) else out

    def contains(self, v):
        return self.coords(v) is not None

    def __eq__(self, other):
        return self.den == other.den and self.M == other.M

    def __hash__(self):
        return hash((self.den, self.M))


def lattice_from_vectors(vecs):
    d = 1
    for v in vecs:
        for x in v:
            dd = Fraction(x).denominator
            d = d * dd // math.gcd(d, dd)
    rows = [[int(Fraction(x) * d) for x in v] for v in vecs]
    return Lattice(rows, d)


def lattice_sum(L1, L2):
    d = L1.den * L2.den // math.gcd(L1.den, L2.den)
    rows = [[x * (d // L1.den) for x in r] for r in L1.M]
    rows += [[x * (d // L2.den) for x in r] for r in L2.M]
    return Lattice(rows, d)


def lattice_mul(Q, L1, L2):
    b1, b2 = L1.basis(), L2.basis()
    return lattice_from_vectors([Q.mul(u, v) for u in b1 for v in b2])


def scale_lattice(L, f):
    f = Fraction(f)
    return lattice_from_vectors([tuple(x * f for x in v) for v in L.basis()])


def conj_lattice(Q, L):
    return lattice_from_vectors([Q.conj(v) for v in L.basis()])


def ring_closure(Q, L):
    cur = L
    for _ in range(32):
        nxt = lattice_sum(cur, lattice_mul(Q, cur, cur))
        if nxt == cur:
            return cur
        cur = nxt
    raise RuntimeError("ring closure did not stabilise")


def is_integral_order(Q, L):
    return all(Q.trd(v).denominator == 1 and Q.nrd(v).denominator == 1
               for v in L.basis())


def reduced_discriminant(Q, L):
    bs = L.basis()
    d2 = abs(det_rat([[Q.trd(Q.mul(u, v)) for v in bs] for u in bs]))
    if d2.denominator != 1:
        return None
    return isqrt_exact(int(d2))


def frac_gcd(vals):
    d = 1
    for v in vals:
        dd = Fraction(v).denominator
        d = d * dd // math.gcd(d, dd)
    g = 0
    for v in vals:
        g = math.gcd(g, abs(int(Fraction(v) * d)))
    return Fraction(g, d)


def nrd_ideal(Q, L):
    bs = L.basis()
    vals = [Q.nrd(b) for b in bs]
    for a in range(4):
        for b in range(a + 1, 4):
            vals.append(2 * Q.bil(bs[a], bs[b]))
    return frac_gcd(vals)


# ===========================================================================
# 3.  LLL and exhaustive short-vector enumeration (exact)
# ===========================================================================
def nearest_int(x):
    f = Fraction(x)
    q, r = divmod(f.numerator, f.denominator)
    if 2 * r > f.denominator:
        q += 1
    return q


def lll_gram(G0, delta=Fraction(99, 100)):
    n = len(G0)
    G = [[Fraction(x) for x in row] for row in G0]
    U = [[1 if i == j else 0 for j in range(n)] for i in range(n)]

    def gso():
        mu = [[Fraction(0)] * n for _ in range(n)]
        Bst = [Fraction(0)] * n
        for i in range(n):
            s = G[i][i]
            for j in range(i):
                t = G[i][j]
                for kk in range(j):
                    t -= mu[j][kk] * mu[i][kk] * Bst[kk]
                mu[i][j] = t / Bst[j] if Bst[j] != 0 else Fraction(0)
                s -= mu[i][j] ** 2 * Bst[j]
            Bst[i] = s
        return mu, Bst

    def rowop(i, j, q):
        U[i] = [a - q * b for a, b in zip(U[i], U[j])]
        for c in range(n):
            G[i][c] -= q * G[j][c]
        for r in range(n):
            G[r][i] -= q * G[r][j]

    def swap(i, j):
        U[i], U[j] = U[j], U[i]
        G[i], G[j] = G[j], G[i]
        for r in range(n):
            G[r][i], G[r][j] = G[r][j], G[r][i]

    k = 1
    guard = 0
    while k < n:
        guard += 1
        if guard > 50000:
            raise RuntimeError("LLL did not terminate")
        mu, Bst = gso()
        for j in range(k - 1, -1, -1):
            q = nearest_int(mu[k][j])
            if q:
                rowop(k, j, q)
                mu, Bst = gso()
        if Bst[k] >= (delta - mu[k][k - 1] ** 2) * Bst[k - 1]:
            k += 1
        else:
            swap(k, k - 1)
            k = max(k - 1, 1)
    return U, G


def _cholesky(G):
    n = len(G)
    Q = [[Fraction(G[i][j]) for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            Q[j][i] = Q[i][j]
            Q[i][j] = Q[i][j] / Q[i][i]
        for kk in range(i + 1, n):
            for l in range(kk, n):
                Q[kk][l] = Q[kk][l] - Q[kk][i] * Q[i][l]
    return Q


def _sqrt_upper(f):
    f = Fraction(f)
    if f <= 0:
        return Fraction(0)
    return Fraction(math.isqrt(f.numerator * f.denominator) + 1, f.denominator)


def short_vectors(G, C, reduce_first=True):
    """All x != 0 in Z^n with x^T G x <= C, one per +/- pair, in the ORIGINAL
    coordinates.  Exact rational arithmetic throughout."""
    n = len(G)
    if reduce_first:
        U, Gr = lll_gram(G)
    else:
        U = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
        Gr = [[Fraction(x) for x in row] for row in G]
    Q = _cholesky(Gr)
    C = Fraction(C)
    x = [0] * n
    out = []

    def rec(i, rem, shift):
        qii = Q[i][i]
        z = _sqrt_upper(rem / qii)
        lo = math.ceil(-shift - z)
        hi = math.floor(-shift + z)
        for xi in range(lo, hi + 1):
            t = qii * (xi + shift) ** 2
            if t > rem:
                continue
            x[i] = xi
            if i == 0:
                if any(x):
                    out.append((C - (rem - t), tuple(x)))
            else:
                sh = Fraction(0)
                for j in range(i, n):
                    if x[j]:
                        sh += Q[i - 1][j] * x[j]
                rec(i - 1, rem - t, sh)
        x[i] = 0

    rec(n - 1, C, Fraction(0))
    res = {}
    for val, v in out:
        w = v
        for c in v:
            if c != 0:
                if c < 0:
                    w = tuple(-cc for cc in v)
                break
        res[w] = val
    final = []
    for w, val in res.items():
        orig = tuple(sum(w[i] * U[i][j] for i in range(n)) for j in range(n))
        for c in orig:
            if c != 0:
                if c < 0:
                    orig = tuple(-cc for cc in orig)
                break
        final.append((val, orig))
    final.sort(key=lambda t: (t[0], t[1]))
    return final


def short_vectors_at_least_one(G, start):
    """short_vectors with the search radius doubled until at least one nonzero
    vector is found.  Purely a robustness wrapper: the radius only ever grows,
    so nothing inside the requested radius is ever missed, and the returned list
    is exhaustive for the radius actually used (which is also returned)."""
    C = Fraction(start)
    if C <= 0:
        C = Fraction(1)
    for _ in range(64):
        sv = short_vectors(G, C)
        if sv:
            return sv, C
        C *= 2
    raise RuntimeError("no short vector found within 2^64 x the initial radius")


def brute_force_min_box(G, C):
    """Fully exhaustive search over the rigorous coordinate box implied by G^-1:
    every x with x^T G x <= C satisfies |x_i| <= sqrt(C * (G^-1)_ii).
    Returns (minimum, box_dimensions, points_visited) with NO lattice reduction."""
    n = len(G)
    Ginv = inverse_rat(G)
    bounds = []
    for i in range(n):
        b = Fraction(C) * Ginv[i][i]
        bounds.append(math.isqrt(b.numerator * b.denominator) // b.denominator + 1
                      if b > 0 else 0)
    total = 1
    for b in bounds:
        total *= (2 * b + 1)
    best = None
    idx = [0] * n
    ranges = [range(-b, b + 1) for b in bounds]

    def rec(i, vec):
        nonlocal best
        if i == n:
            if any(vec):
                val = sum(vec[a] * G[a][b] * vec[b] for a in range(n) for b in range(n))
                if val > 0 and (best is None or val < best):
                    best = val
            return
        for t in ranges[i]:
            rec(i + 1, vec + [t])

    rec(0, [])
    return best, bounds, total


def gram3(Q, basis3):
    full = [(Fraction(0), v[0], v[1], v[2]) for v in basis3]
    return [[Q.bil(u, w) for w in full] for u in full]


def lattice3(vecs):
    d = 1
    for v in vecs:
        for x in v:
            dd = Fraction(x).denominator
            d = d * dd // math.gcd(d, dd)
    rows = [[int(Fraction(x) * d) for x in v] for v in vecs]
    H = hnf(rows, 3)
    if len(H) != 3:
        raise RuntimeError("rank-3 lattice expected")
    return [tuple(Fraction(x, d) for x in row) for row in H]


# ===========================================================================
# 4.  Successive minima / canonical Minkowski form for rank-3 forms
# ===========================================================================
def _rank(rows):
    A = [[Fraction(x) for x in r] for r in rows]
    m, n = len(A), len(A[0])
    r = 0
    for c in range(n):
        piv = None
        for i in range(r, m):
            if A[i][c] != 0:
                piv = i
                break
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        for i in range(r + 1, m):
            if A[i][c] != 0:
                f = A[i][c] / A[r][c]
                A[i] = [a - f * b for a, b in zip(A[i], A[r])]
        r += 1
    return r


def successive_minima(G, want=3):
    n = len(G)
    d = abs(det_rat(G))
    est = max(1, int(float(d) ** (1.0 / n)) * 2 + 2)
    bound = Fraction(est)
    while True:
        vecs = short_vectors(G, bound)
        minima, chosen = [], []
        for val, v in vecs:
            if len(chosen) == want:
                break
            if _rank(chosen + [v]) == len(chosen) + 1:
                chosen.append(v)
                minima.append(val)
        if len(minima) == want and minima[-1] <= bound:
            return minima, [(val, v) for val, v in vecs if val <= minima[-1]]
        bound *= 2


def _bilform(G, u, v):
    n = len(G)
    return sum(u[i] * G[i][j] * v[j] for i in range(n) for j in range(n))


def canonical_gram3(G):
    """Canonical conjugacy label (contract step Q3).  Minkowski-reduced Gram of a
    rank-3 form; TIE-BREAKING RULE (declared): among all bases (v1,v2,v3) whose
    norms are the three successive minima in order and whose determinant is +-1,
    take the lexicographically smallest tuple (m1,m2,m3,g23,g13,g12)."""
    minima, vecs = successive_minima(G, 3)
    m1, m2, m3 = minima
    pool = []
    for val, v in vecs:
        pool.append((val, v))
        pool.append((val, tuple(-x for x in v)))
    c1 = [v for val, v in pool if val == m1]
    c2 = [v for val, v in pool if val == m2]
    c3 = [v for val, v in pool if val == m3]
    best = None
    for v1 in c1:
        for v2 in c2:
            for v3 in c3:
                D = det_rat([list(v1), list(v2), list(v3)])
                if D != 1 and D != -1:
                    continue
                key = (m1, m2, m3, _bilform(G, v2, v3), _bilform(G, v1, v3),
                       _bilform(G, v1, v2))
                if best is None or key < best:
                    best = key
    if best is None:
        raise RuntimeError("no Minkowski basis found")
    return best


def aov_tuple(G):
    """(N1,N2,N3,x,y,z) in the AOV eq.(7) normalisation:
    Gram = [[N1, x/2, y/2],[x/2, N2, z/2],[y/2, z/2, N3]] with
    p = xyz - N3 x^2 - N2 y^2 - N1 z^2 + 4 N1 N2 N3 = 4 det.
    DECLARED normalisation: over Minkowski bases realising the successive minima,
    keep those with x >= 0 and y >= 0 and take the lexicographically smallest
    (x, y, z)."""
    minima, vecs = successive_minima(G, 3)
    m1, m2, m3 = minima
    pool = []
    for val, v in vecs:
        pool.append((val, v))
        pool.append((val, tuple(-x for x in v)))
    c1 = [v for val, v in pool if val == m1]
    c2 = [v for val, v in pool if val == m2]
    c3 = [v for val, v in pool if val == m3]
    best = None
    for v1 in c1:
        for v2 in c2:
            for v3 in c3:
                D = det_rat([list(v1), list(v2), list(v3)])
                if D != 1 and D != -1:
                    continue
                x = 2 * _bilform(G, v1, v2)
                y = 2 * _bilform(G, v1, v3)
                z = 2 * _bilform(G, v2, v3)
                if x < 0 or y < 0:
                    continue
                key = (x, y, z)
                if best is None or key < best:
                    best = key
    if best is None:
        return None
    x, y, z = best
    return (m1, m2, m3, x, y, z)


def theta_series(G, bound):
    """Number of vectors (as +/- pairs) of each norm value <= bound."""
    out = {}
    for val, _ in short_vectors(G, bound):
        out[val] = out.get(val, 0) + 1
    return tuple(sorted((str(k), v) for k, v in out.items()))


# ===========================================================================
# 5.  Maximal order construction (contract step Q1) and verification
# ===========================================================================
def legendre(a, p):
    a %= p
    if a == 0:
        return 0
    return 1 if pow(a, (p - 1) // 2, p) == 1 else -1


def is_prime(n):
    if n < 2:
        return False
    for sp in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % sp == 0:
            return n == sp
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def algebra_params(p):
    if p % 4 == 3:
        return 1, -1, -p, "p = 3 (mod 4): B = (-1,-p)"
    if p % 8 == 5:
        return 2, -2, -p, "p = 5 (mod 8): B = (-2,-p)"
    q = 3
    while not (is_prime(q) and legendre(p, q) == -1):
        q += 4
    return q, -q, -p, ("p = 1 (mod 8): B = (-q,-p), q = %d the smallest prime "
                       "= 3 (mod 4) with Legendre(p|q) = -1" % q)


def build_maximal_order(p):
    q, a, b, note = algebra_params(p)
    Q = Quat(a, b)
    log = {"algebra_a_b": [a, b], "q": q, "presentation_note": note, "steps": []}
    e = [(Fraction(1), Fraction(0), Fraction(0), Fraction(0)),
         (Fraction(0), Fraction(1), Fraction(0), Fraction(0)),
         (Fraction(0), Fraction(0), Fraction(1), Fraction(0)),
         (Fraction(0), Fraction(0), Fraction(0), Fraction(1))]
    L = lattice_from_vectors(e)
    d = reduced_discriminant(Q, L)
    log["steps"].append({"stage": "Z<1,i,j,k>", "reduced_discriminant": d})
    if d != 4 * q * p:
        raise RuntimeError("base order discriminant wrong at p=%d" % p)
    if q > 2:
        c = next(cc for cc in range(q) if (cc * cc + p) % q == 0)
        x = (Fraction(0), Fraction(c, q), Fraction(0), Fraction(1, q))
        if Q.trd(x).denominator != 1 or Q.nrd(x).denominator != 1:
            raise RuntimeError("non-integral q-adic generator at p=%d" % p)
        L = ring_closure(Q, lattice_sum(L, lattice_from_vectors([e[0], x, e[2], e[3]])))
        d = reduced_discriminant(Q, L)
        log["steps"].append({"stage": "adjoin (%d*i + k)/%d" % (c, q),
                             "reduced_discriminant": d})
    guard = 0
    while d is not None and d % 2 == 0:
        guard += 1
        if guard > 8:
            raise RuntimeError("2-adic enlargement stalled at p=%d" % p)
        bs = L.basis()
        found = None
        for mask in range(1, 16):
            cs = [(mask >> t) & 1 for t in range(4)]
            x = tuple(sum(Fraction(cs[t] * bs[t][r], 2) for t in range(4))
                      for r in range(4))
            if Q.trd(x).denominator != 1 or Q.nrd(x).denominator != 1:
                continue
            cand = ring_closure(Q, lattice_sum(L, lattice_from_vectors([x] + bs)))
            if not is_integral_order(Q, cand):
                continue
            dc = reduced_discriminant(Q, cand)
            if dc is not None and dc < d and d % dc == 0:
                found = (cs, cand, dc)
                break
        if found is None:
            break
        cs, L, d = found
        log["steps"].append({"stage": "adjoin (%s)/2 in the current basis" % (cs,),
                             "reduced_discriminant": d})
    log["final_reduced_discriminant"] = d
    return Q, L, log


def verify_order(Q, L, p):
    bs = L.basis()
    prods = [Q.mul(u, v) for u in bs for v in bs]
    closed = all(L.contains(w) for w in prods)
    integral = all(Q.trd(v).denominator == 1 and Q.nrd(v).denominator == 1 for v in bs)
    integral_prod = all(Q.trd(w).denominator == 1 and Q.nrd(w).denominator == 1
                        for w in prods)
    d = reduced_discriminant(Q, L)
    return {
        "check_a_closure_under_multiplication": bool(closed),
        "check_b_integrality_trd_nrd_basis": bool(integral),
        "check_b_integrality_trd_nrd_basis_products": bool(integral_prod),
        "check_c_reduced_discriminant": d,
        "check_c_reduced_discriminant_equals_p": bool(d == p),
        "maximality_criterion": ("an order of B_{p,infinity} whose reduced "
                                 "discriminant equals p is maximal"),
        "accepted": bool(closed and integral and integral_prod and d == p),
        "basis_over_Z": [[str(x) for x in v] for v in bs],
    }


# ===========================================================================
# 6.  Ideals, right orders, the two-sided ideal P, delta_E
# ===========================================================================
def left_ideals_of_norm(Q, O, ell):
    bs = O.basis()
    detO = O.det()
    out = {}
    for c0 in range(ell):
        for c1 in range(ell):
            for c2 in range(ell):
                for c3 in range(ell):
                    if c0 == c1 == c2 == c3 == 0:
                        continue
                    x = tuple(c0 * bs[0][r] + c1 * bs[1][r] + c2 * bs[2][r]
                              + c3 * bs[3][r] for r in range(4))
                    gens = [Q.mul(u, x) for u in bs] + [
                        tuple(ell * y for y in u) for u in bs]
                    I = lattice_from_vectors(gens)
                    if I.det() / detO == ell ** 2:
                        out[I] = True
    return sorted(out.keys(), key=lambda L: (L.den, L.M))


def right_order(Q, I, nrm):
    return scale_lattice(lattice_mul(Q, conj_lattice(Q, I), I), Fraction(1, nrm))


def gross_lattice_basis(Q, O):
    vecs = []
    for e in O.basis():
        g = (e[0] * 2 - Q.trd(e), e[1] * 2, e[2] * 2, e[3] * 2)
        vecs.append((g[1], g[2], g[3]))
    return lattice3(vecs)


def _kernel_mod_p(M, p):
    n = len(M)
    A = [row[:] for row in M]
    piv_cols, r = [], 0
    for c in range(n):
        piv = None
        for i in range(r, n):
            if A[i][c] % p:
                piv = i
                break
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        inv = pow(A[r][c], p - 2, p)
        A[r] = [(x * inv) % p for x in A[r]]
        for i in range(n):
            if i != r and A[i][c] % p:
                f = A[i][c]
                A[i] = [(x - f * y) % p for x, y in zip(A[i], A[r])]
        piv_cols.append(c)
        r += 1
    free = [c for c in range(n) if c not in piv_cols]
    ker = []
    for fc in free:
        v = [0] * n
        v[fc] = 1
        for idx, pc in enumerate(piv_cols):
            v[pc] = (-A[idx][fc]) % p
        ker.append(v)
    return ker


def two_sided_p_ideal(Q, O, p):
    """P = {x in O : p | Nrd(x)}: the unique two-sided ideal of reduced norm p."""
    bs = O.basis()
    Gm = []
    for u in bs:
        row = []
        for v in bs:
            f = Q.bil(u, v)
            row.append(f.numerator % p * pow(f.denominator % p, p - 2, p) % p)
        Gm.append(row)
    ker = _kernel_mod_p(Gm, p)
    gens = [tuple(p * y for y in u) for u in bs]
    for c in ker:
        gens.append(tuple(sum(c[t] * bs[t][r] for t in range(4)) for r in range(4)))
    return lattice_from_vectors(gens), len(ker)


def trace_zero_sublattice(P):
    bs = P.basis()
    dens = 1
    for e in bs:
        dd = e[0].denominator
        dens = dens * dd // math.gcd(dens, dd)
    ker = kernel_basis([[int(e[0] * dens) for e in bs]], 4)
    if len(ker) != 3:
        raise RuntimeError("trace-zero sublattice rank != 3")
    out = []
    for c in ker:
        v = tuple(sum(c[t] * bs[t][r] for t in range(4)) for r in range(4))
        if v[0] != 0:
            raise RuntimeError("trace-zero extraction failed")
        out.append((v[1], v[2], v[3]))
    return lattice3(out)


def unit_count(Q, O):
    """|O^x| / 2 = w, from the units (Nrd = 1) of the order."""
    bs = O.basis()
    G = [[Q.bil(u, v) for v in bs] for u in bs]
    sv = short_vectors(G, 1)
    return sum(1 for val, _ in sv if val == 1)


def inv_quat(Q, g):
    n = Q.nrd(g)
    return tuple(x / n for x in Q.conj(g))


def find_conjugator(Q, O_target, O_source, p):
    """gamma with gamma^{-1} O_target gamma = O_source, searched in the connecting
    ideal O_target*O_source and, if that fails, in its twist by the two-sided
    ideal P (connecting ideals form a torsor under the two-sided ideal group)."""
    C = lattice_mul(Q, O_target, O_source)

    def candidates():
        yield "I", C
        Pid, _ = two_sided_p_ideal(Q, O_source, p)
        yield "I*P", lattice_mul(Q, C, Pid)

    for tag, L in candidates():
        N = nrd_ideal(Q, L)
        bs = L.basis()
        G = [[Q.bil(u, v) / N for v in bs] for u in bs]
        for val, c in short_vectors(G, 1):
            if val != 1:
                continue
            g = tuple(sum(c[t] * bs[t][r] for t in range(4)) for r in range(4))
            gi = inv_quat(Q, g)
            if lattice_from_vectors([Q.mul(gi, Q.mul(v, g))
                                     for v in O_target.basis()]) == O_source:
                return g, tag
    return None, None


# ===========================================================================
# 7.  IF-1: brute-force supersingular count in F_{p^2}
# ===========================================================================
def brute_force_ss_count(p):
    r = next(rr for rr in range(2, p) if pow(rr, (p - 1) // 2, p) == p - 1)
    m = (p - 1) // 2
    fact = [1] * (m + 1)
    for i in range(1, m + 1):
        fact[i] = fact[i - 1] * i % p
    inv_fact = [1] * (m + 1)
    inv_fact[m] = pow(fact[m], p - 2, p)
    for i in range(m, 0, -1):
        inv_fact[i - 1] = inv_fact[i] * i % p
    s0, s1 = (m + 1) // 2, (2 * m) // 3
    coeffs = []
    for s in range(s0, s1 + 1):
        t, u = 2 * m - 3 * s, 2 * s - m
        coeffs.append((t, u, fact[m] * inv_fact[s] % p * inv_fact[t] % p
                       * inv_fact[u] % p))

    def mul(x, y):
        return ((x[0] * y[0] + r * x[1] * y[1]) % p, (x[0] * y[1] + x[1] * y[0]) % p)

    def powe(x, ex):
        res = (1, 0)
        while ex:
            if ex & 1:
                res = mul(res, x)
            x = mul(x, x)
            ex >>= 1
        return res

    def hasse_zero(a, b):
        a0 = a1 = 0
        if a == (0, 0):
            for (t, u, C) in coeffs:
                if t == 0:
                    bu = powe(b, u) if u else (1, 0)
                    a0 = (a0 + C * bu[0]) % p
                    a1 = (a1 + C * bu[1]) % p
            return a0 == 0 and a1 == 0
        if b == (0, 0):
            for (t, u, C) in coeffs:
                if u == 0:
                    at = powe(a, t) if t else (1, 0)
                    a0 = (a0 + C * at[0]) % p
                    a1 = (a1 + C * at[1]) % p
            return a0 == 0 and a1 == 0
        bpows, cur_b, b2 = {}, powe(b, coeffs[0][1]), mul(b, b)
        for (t, u, C) in coeffs:
            bpows[u] = cur_b
            cur_b = mul(cur_b, b2)
        cur_a, a3 = powe(a, coeffs[-1][0]), mul(a, mul(a, a))
        for (t, u, C) in reversed(coeffs):
            term = mul(cur_a, bpows[u])
            a0 = (a0 + C * term[0]) % p
            a1 = (a1 + C * term[1]) % p
            cur_a = mul(cur_a, a3)
        return a0 == 0 and a1 == 0

    c1728 = (1728 % p, 0)
    n_all = n_fp = 0
    for u in range(p):
        for v in range(p):
            j = (u, v)
            if j == (0, 0):
                a, b = (0, 0), (1, 0)
            elif j == c1728:
                a, b = (1, 0), (0, 0)
            else:
                d = ((1728 - u) % p, (-v) % p)
                a = mul((3, 0), mul(j, d))
                b = mul((2, 0), mul(j, mul(d, d)))
            if hasse_zero(a, b):
                n_all += 1
                if v == 0:
                    n_fp += 1
    return n_all, n_fp


def closed_form_ss(p):
    eps = {1: 0, 5: 1, 7: 1, 11: 2}[p % 12]
    return p // 12 + eps


# ===========================================================================
# 8.  Number-theoretic helpers (all computed here, none recalled)
# ===========================================================================
def factorize(n):
    f = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            f[d] = f.get(d, 0) + 1
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f


def largest_prime_factor(n):
    if n == 1:
        return 1
    return max(factorize(n))


def is_smooth(n, B):
    return n == 1 or largest_prime_factor(n) <= B


def x_bound(p):
    """X_p = floor((p/2)^(1/3)), computed exactly: largest n with 2 n^3 <= p."""
    n = int(round((p / 2.0) ** (1.0 / 3.0))) + 2
    while 2 * n ** 3 > p:
        n -= 1
    while 2 * (n + 1) ** 3 <= p:
        n += 1
    return n


def hurwitz_class_number(N):
    """H(N) by exact enumeration of reduced positive definite binary forms of
    discriminant -N (Hurwitz weighting: a(x^2+y^2) counts 1/2, a(x^2+xy+y^2)
    counts 1/3)."""
    if N <= 0:
        return Fraction(0)
    if N % 4 not in (0, 3):
        return Fraction(0)
    total = Fraction(0)
    amax = math.isqrt(N // 3)
    for a in range(1, amax + 1):
        for b in range(-a + 1, a + 1):
            num = b * b + N
            if num % (4 * a):
                continue
            c = num // (4 * a)
            if c < a:
                continue
            if (b < 0) and (a == c or a == -b):
                continue
            if b * b - 4 * a * c != -N:
                continue
            g = math.gcd(math.gcd(a, b), c)
            aa, bb, cc = a // g, b // g, c // g
            if (aa, bb, cc) == (1, 0, 1):
                total += Fraction(1, 2)
            elif (aa, bb, cc) == (1, 1, 1):
                total += Fraction(1, 3)
            else:
                total += 1
    return total


def smooth_counts_upto(n):
    """P+(m) for every m <= n, by sieve."""
    lp = list(range(n + 1))
    for i in range(2, n + 1):
        if lp[i] == i:
            for j in range(i, n + 1, i):
                if lp[j] == j or lp[j] < i:
                    lp[j] = i
    out = [0] * (n + 1)
    for m in range(1, n + 1):
        out[m] = 1 if m == 1 else largest_prime_factor(m)
    return out


# ===========================================================================
# 9.  Per-prime enumeration (route Q)
# ===========================================================================
def enumerate_prime(p, tier, do_brute_ss, do_route_f, do_brute_box, ell=2):
    t0 = time.time()
    rec = {"p": p, "tier": tier}
    Q, O0, olog = build_maximal_order(p)
    ver = verify_order(Q, O0, p)
    rec["O_0"] = {"construction": olog, "verification": ver}
    if not ver["accepted"]:
        rec["status"] = "order_construction_failed"
        return rec

    # ---- BFS over the ell-ideal graph (contract step Q2/Q3)
    key0 = canonical_gram3(gram3(Q, gross_lattice_basis(Q, O0)))
    reps = {key0: O0}
    order_keys = [key0]
    frontier = [O0]
    while frontier:
        nxt = []
        for Ocur in frontier:
            for I in left_ideals_of_norm(Q, Ocur, ell):
                Or = right_order(Q, I, ell)
                k = canonical_gram3(gram3(Q, gross_lattice_basis(Q, Or)))
                if k not in reps:
                    reps[k] = Or
                    order_keys.append(k)
                    nxt.append(Or)
        frontier = nxt
    order_keys.sort()
    index_of = {k: i for i, k in enumerate(order_keys)}
    h = len(order_keys)

    # ---- graph with reverse-edge map (needed for the non-backtracking walk)
    nbr = [[0] * (ell + 1) for _ in range(h)]
    rev = [[0] * (ell + 1) for _ in range(h)]
    conj_tags = {"I": 0, "I*P": 0, "none": 0}
    ideal_cache = {}
    for i, ki in enumerate(order_keys):
        Oi = reps[ki]
        ideal_cache[i] = left_ideals_of_norm(Q, Oi, ell)
    theta_checks = {"pairs_checked": 0, "violations": []}
    theta_bound = 10 * max(1, int((4 * p * p) ** (1.0 / 3.0)))
    theta_rep = {}
    for i, ki in enumerate(order_keys):
        Oi = reps[ki]
        for t, I in enumerate(ideal_cache[i]):
            Or = right_order(Q, I, ell)
            kj = canonical_gram3(gram3(Q, gross_lattice_basis(Q, Or)))
            j = index_of[kj]
            nbr[i][t] = j
            Oj = reps[kj]
            # IF-4: declared-conjugate orders must have identical theta series
            th_a = theta_series(gram3(Q, gross_lattice_basis(Q, Or)), theta_bound)
            if j not in theta_rep:
                theta_rep[j] = theta_series(gram3(Q, gross_lattice_basis(Q, Oj)),
                                            theta_bound)
            th_b = theta_rep[j]
            theta_checks["pairs_checked"] += 1
            if th_a != th_b:
                theta_checks["violations"].append(
                    {"p": p, "edge": [i, t], "class": j})
            g, tag = find_conjugator(Q, Oj, Or, p)
            if g is None:
                conj_tags["none"] += 1
                rev[i][t] = -1
                continue
            conj_tags[tag] += 1
            gi = inv_quat(Q, g)
            back = lattice_from_vectors(
                [Q.mul(g, Q.mul(v, gi)) for v in conj_lattice(Q, I).basis()])
            s = None
            for u, Ju in enumerate(ideal_cache[j]):
                if Ju == back:
                    s = u
                    break
            rev[i][t] = -1 if s is None else s

    # ---- per-class records (contract steps Q4/Q5)
    X_p = x_bound(p)
    classes = []
    if_2 = {"checked": 0, "disagreements": [], "brute_force_box": []}
    for i, k in enumerate(order_keys):
        O = reps[k]
        Pid, kerdim = two_sided_p_ideal(Q, O, p)
        idx = Pid.det() / O.det()
        b4 = Pid.basis()
        G4 = [[Q.bil(u, v) / p for v in b4] for u in b4]
        b3 = trace_zero_sublattice(Pid)
        G3 = [[x / p for x in row] for row in gram3(Q, b3)]
        sv3, radius3 = short_vectors_at_least_one(G3, X_p)
        d3 = min(v for v, _ in sv3)
        sv4 = short_vectors(G4, d3)
        d4 = min(v for v, _ in sv4)
        if_2["checked"] += 1
        if d3 != d4:
            if_2["disagreements"].append({"p": p, "class": i, "rank3": str(d3),
                                          "rank4": str(d4)})
        if do_brute_box:
            bmin, bounds, npts = brute_force_min_box(G3, d3)
            if_2["brute_force_box"].append(
                {"p": p, "class": i, "box_half_widths": bounds,
                 "points_visited": npts, "minimum": str(bmin),
                 "agrees": bool(bmin == d3)})
        delta = d3
        if delta.denominator != 1:
            raise RuntimeError("non-integral delta_E at p=%d class %d" % (p, i))
        delta = int(delta)
        nmin = sum(1 for v, _ in sv3 if v == delta)
        minvec = next(vv for v, vv in sv3 if v == delta)
        aov = aov_tuple(G3)
        rkey = canonical_gram3(G3)
        w = unit_count(Q, O)
        counts = {}
        for val, _ in sv3:
            if val.denominator == 1 and int(val) <= X_p:
                counts[int(val)] = counts.get(int(val), 0) + 1
        classes.append({
            "class_index": i,
            "delta_E": delta,
            "delta_E_factorization": {str(a): b for a, b in factorize(delta).items()},
            "P_plus": largest_prime_factor(delta),
            "delta_over_Xp": str(Fraction(delta, X_p)),
            "N1N2N3xyz": [str(t) for t in aov] if aov else None,
            "R_canonical_key": [str(t) for t in rkey],
            "galois_stable": bool(delta == 1),
            "aut_half_order_w": w,
            "n_minimal_vectors_pm_pairs": nmin,
            "minimal_vector": [str(x) for x in minvec],
            "rank3_gram_det": str(det_rat(G3)),
            "rank4_index_in_O": str(idx),
            "p_ideal_radical_dim": kerdim,
            "rank3_enumeration_radius": str(radius3),
            "representation_counts_pm_pairs": {str(kk): vv
                                               for kk, vv in sorted(counts.items())},
        })

    rec["n_types"] = h
    rec["X_p"] = X_p
    rec["classes"] = classes
    rec["graph"] = {"neighbours": nbr, "reverse": rev,
                    "start_index": index_of[key0],
                    "conjugator_source_counts": conj_tags,
                    "reverse_undetermined": sum(1 for r in rev for x in r if x < 0)}
    rec["IF_2"] = if_2
    rec["IF_4"] = {"pairs_checked": theta_checks["pairs_checked"],
                   "theta_bound": theta_bound,
                   "violations": theta_checks["violations"]}
    n_delta1 = sum(1 for c in classes if c["delta_E"] == 1)
    lhs = h
    rhs_cf = Fraction(closed_form_ss(p) + n_delta1, 2)
    rec["IF_1"] = {
        "n_types": h,
        "n_classes_delta_1": n_delta1,
        "closed_form_count": closed_form_ss(p),
        "identity_rhs_from_closed_form": str(rhs_cf),
        "identity_holds_closed_form": bool(Fraction(lhs) == rhs_cf),
    }
    if do_brute_ss:
        bf, bf_fp = brute_force_ss_count(p)
        rec["IF_1"].update({
            "brute_force_count": bf,
            "brute_force_count_in_Fp": bf_fp,
            "closed_form_matches_brute_force": bool(bf == closed_form_ss(p)),
            "identity_rhs_from_brute_force": str(Fraction(bf + n_delta1, 2)),
            "identity_holds_brute_force": bool(Fraction(lhs) == Fraction(bf + n_delta1, 2)),
            "delta1_equals_j_in_Fp": bool(n_delta1 == bf_fp),
        })
    # IF-5
    maxd = max(c["delta_E"] for c in classes)
    rec["IF_5"] = {"max_delta_E": maxd, "X_p": X_p,
                   "violations": [c["class_index"] for c in classes
                                  if c["delta_E"] > X_p]}
    # mass formula (free extra instrument check, reported not gating)
    mass = sum(Fraction(1, 2 * c["aut_half_order_w"]) for c in classes)
    # the mass formula counts CURVES: a Galois-stable class carries one
    # j-invariant, every other class carries the pair {j, j^p}
    mass_curves = sum(Fraction(1 if c["galois_stable"] else 2,
                               2 * c["aut_half_order_w"]) for c in classes)
    rec["mass_check"] = {"sum_over_types_1_over_Aut": str(mass),
                         "sum_over_curves_1_over_Aut": str(mass_curves),
                         "p_minus_1_over_24": str(Fraction(p - 1, 24)),
                         "curve_mass_matches": bool(mass_curves == Fraction(p - 1, 24))}
    # D1 first-moment identity, verified per n (contract D1 normalisation rule)
    d1 = []
    for n in range(1, X_p + 1):
        lhs_n = sum(Fraction((1 if c["galois_stable"] else 2)
                             * 2 * c["representation_counts_pm_pairs"].get(str(n), 0),
                             c["aut_half_order_w"]) for c in classes)
        Hn = hurwitz_class_number(4 * n * p)
        d1.append({"n": n, "mass_weighted_ordered_count_over_curves": str(lhs_n),
                   "H_4np": str(Hn), "agree": bool(lhs_n == Hn)})
    rec["D1_identity_per_n"] = d1
    rec["route_F"] = route_f_enumerate(p, X_p) if do_route_f else None
    rec["wall_clock_seconds"] = round(time.time() - t0, 3)
    rec["status"] = "complete"
    return rec


# ===========================================================================
# 10.  Route F -- direct enumeration of reduced ternary Gram matrices
# ===========================================================================
def route_f_enumerate(p, X_p):
    """AOV eq. (7): p = xyz - N3 x^2 - N2 y^2 - N1 z^2 + 4 N1 N2 N3 with
    0 <= x,y <= N1, |z| <= N2, p/4 <= N1 N2 N3 <= p/2, N1 <= N2 <= N3.
    Every solution is canonicalised through the SAME canonical_gram3 code path
    used by route Q and de-duplicated."""
    found = {}
    tuples = 0
    for N1 in range(1, X_p + 1):
        n2max = math.isqrt(p // (2 * N1)) + 1
        for N2 in range(N1, n2max + 1):
            for x in range(0, N1 + 1):
                D = 4 * N1 * N2 - x * x
                if D <= 0:
                    continue
                for y in range(0, N1 + 1):
                    for z in range(-N2, N2 + 1):
                        num = p - x * y * z + N2 * y * y + N1 * z * z
                        if num <= 0 or num % D:
                            continue
                        N3 = num // D
                        if N3 < N2:
                            continue
                        if not (4 * N1 * N2 * N3 >= p and 2 * N1 * N2 * N3 <= p):
                            continue
                        G = [[Fraction(N1), Fraction(x, 2), Fraction(y, 2)],
                             [Fraction(x, 2), Fraction(N2), Fraction(z, 2)],
                             [Fraction(y, 2), Fraction(z, 2), Fraction(N3)]]
                        if 4 * det_rat(G) != p:
                            continue
                        if det_rat([[G[0][0]]]) <= 0:
                            continue
                        if det_rat([r[:2] for r in G[:2]]) <= 0:
                            continue
                        tuples += 1
                        key = tuple(str(t) for t in canonical_gram3(G))
                        if key not in found:
                            found[key] = (N1, N2, N3, x, y, z)
    return {"n_tuples": tuples, "n_classes": len(found),
            "canonical_keys": sorted(list(k) for k in found)}


# ===========================================================================
# 11.  NULL-A: random integral ternary forms of the same determinant
# ===========================================================================
def null_a_forms(p, n_forms, rng, X_p):
    """DECLARED random construction.  Draw N1 ~ U[1, X_p]; N2 ~ U[N1, floor(sqrt(p /
    (2 N1)))]; x, y ~ U[0, N1]; then scan every z in [-N2, N2], keep the (z, N3)
    that satisfy the AOV determinant identity with N3 >= N2 and positive
    definiteness, and pick one of them uniformly.  Reject and redraw if none.
    The resulting form has determinant p/4, exactly as the arithmetic family, and
    its minimum is computed by the identical short_vectors code path."""
    out = []
    tries = 0
    while len(out) < n_forms:
        tries += 1
        if tries > 400000 + 4000 * n_forms:
            break
        N1 = rng.randint(1, max(1, X_p))
        hi = math.isqrt(p // (2 * N1)) if 2 * N1 <= p else 0
        if hi < N1:
            continue
        N2 = rng.randint(N1, hi)
        x = rng.randint(0, N1)
        y = rng.randint(0, N1)
        D = 4 * N1 * N2 - x * x
        if D <= 0:
            continue
        ok = []
        for z in range(-N2, N2 + 1):
            num = p - x * y * z + N2 * y * y + N1 * z * z
            if num <= 0 or num % D:
                continue
            N3 = num // D
            if N3 < N2:
                continue
            G = [[Fraction(N1), Fraction(x, 2), Fraction(y, 2)],
                 [Fraction(x, 2), Fraction(N2), Fraction(z, 2)],
                 [Fraction(y, 2), Fraction(z, 2), Fraction(N3)]]
            if 4 * det_rat(G) != p:
                continue
            if det_rat([r[:2] for r in G[:2]]) <= 0:
                continue
            ok.append((z, N3, G))
        if not ok:
            continue
        z, N3, G = ok[rng.randrange(len(ok))]
        sv, _radius = short_vectors_at_least_one(G, X_p)
        dmin = min(v for v, _ in sv)
        if dmin.denominator != 1:
            continue
        dmin = int(dmin)
        counts = {}
        for val, _ in sv:
            if val.denominator == 1 and int(val) <= X_p:
                counts[int(val)] = counts.get(int(val), 0) + 1
        out.append({"p": p, "N1N2N3xyz": [N1, N2, N3, x, y, z], "delta_null": dmin,
                    "P_plus": largest_prime_factor(dmin),
                    "galois_stable": bool(dmin == 1),
                    "aut_half_order_w": 1,
                    "representation_counts_pm_pairs": counts})
    return out, tries


# ===========================================================================
# 12.  Random sampling helpers (seeded, pure stdlib)
# ===========================================================================
def binomial_sample(rng, n, pr):
    """Exact binomial sampler.

    Two exact routes, chosen only by cost and never by outcome:

    * n <= 30, or a small standard deviation: inverse transform, enumerating
      outcomes outward from the mode in decreasing-pmf order.  O(sigma) steps.
    * otherwise: Devroye's beta-splitting recursion.  With V the k-th order
      statistic of n iid U(0,1) -- i.e. V ~ Beta(k, n+1-k), drawn by the
      standard library's exact `betavariate` -- the count of uniforms below pr
      splits exactly as k + Bin(n-k, (pr-V)/(1-V)) when V <= pr, and as
      Bin(k-1, pr/V) otherwise.  O(log n) steps.

    Both are exact in distribution; neither is a normal or Poisson
    approximation.  The switch exists because the inverse-transform route costs
    O(sigma) and sigma reaches several hundred at the pooled sample sizes of
    this run."""
    if n <= 0 or pr <= 0.0:
        return 0
    if pr >= 1.0:
        return n
    if n > 30 and n * pr * (1.0 - pr) > 900.0:
        k = (n + 1) // 2
        v = rng.betavariate(k, n + 1 - k)
        if v <= pr:
            return k + binomial_sample(rng, n - k, (pr - v) / (1.0 - v))
        return binomial_sample(rng, k - 1, pr / v)
    u = rng.random()
    mode = int((n + 1) * pr)
    if mode > n:
        mode = n
    logpmf_mode = (math.lgamma(n + 1) - math.lgamma(mode + 1) - math.lgamma(n - mode + 1)
                   + mode * math.log(pr) + (n - mode) * math.log1p(-pr))
    pm = math.exp(logpmf_mode)
    acc = pm
    if u < acc:
        return mode
    lo = hi = mode
    plo = phi = pm
    while True:
        nxt_lo = plo * lo / (n - lo + 1) * (1 - pr) / pr if lo > 0 else 0.0
        nxt_hi = phi * (n - hi) / (hi + 1) * pr / (1 - pr) if hi < n else 0.0
        if nxt_lo <= 0.0 and nxt_hi <= 0.0:
            return hi if phi >= plo else lo
        if nxt_hi >= nxt_lo:
            hi += 1
            phi = nxt_hi
            acc += phi
            if u < acc:
                return hi
        else:
            lo -= 1
            plo = nxt_lo
            acc += plo
            if u < acc:
                return lo
        if lo <= 0 and hi >= n:
            return hi


def multinomial_sample(rng, n, probs):
    out = []
    rem = n
    remp = 1.0
    for idx in range(len(probs) - 1):
        if rem == 0:
            out.append(0)
            continue
        q = probs[idx] / remp if remp > 0 else 0.0
        q = min(max(q, 0.0), 1.0)
        c = binomial_sample(rng, rem, q)
        out.append(c)
        rem -= c
        remp -= probs[idx]
    out.append(rem)
    return out


# ===========================================================================
# 13.  Statistical primitives (exact where the quantity is rational)
# ===========================================================================
def log_binom(n, k):
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def binom_two_sided_pvalue(n, k, p0):
    """Two-sided exact binomial p-value: sum of pmf over all outcomes whose pmf
    does not exceed pmf(k).  Computed in 60-digit Decimal; the exact rational
    comparison against the threshold is done separately by
    binom_two_sided_below_threshold."""
    if n == 0:
        return 1.0
    with localcontext() as ctx:
        ctx.prec = 60
        P = Decimal(p0.numerator) / Decimal(p0.denominator)
        Qd = Decimal(1) - P
        lp = [None] * (n + 1)
        logs = [log_binom(n, i) + i * math.log(float(p0)) + (n - i) * math.log1p(-float(p0))
                if 0 < float(p0) < 1 else None for i in range(n + 1)]
        ref = logs[k]
        tot = Decimal(0)
        pmf = P ** 0 * Qd ** n
        cur = pmf
        for i in range(0, n + 1):
            if i > 0:
                cur = cur * Decimal(n - i + 1) / Decimal(i) * P / Qd
            if logs[i] <= ref + 1e-12:
                tot += cur
        return float(min(Decimal(1), tot))


def betainc_reg(a, b, x):
    """Regularised incomplete beta I_x(a,b), by the standard Lentz continued
    fraction.  This is the closed form of the binomial tail
    sum_{i>=k} C(n,i) x^i (1-x)^{n-i} = I_x(k, n-k+1); using it makes the
    Clopper-Pearson interval computable at the weighted sample sizes here, where
    the naive term-by-term tail would need O(n) exponentials per bisection
    step."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    front = math.exp(a * math.log(x) + b * math.log1p(-x) - lbeta)
    if x > (a + 1.0) / (a + b + 2.0):
        return 1.0 - betainc_reg(b, a, 1.0 - x)
    tiny = 1e-300
    f, c, d = 1.0, 1.0, 0.0
    for i in range(0, 400):
        m = i // 2
        if i == 0:
            num = 1.0
        elif i % 2 == 0:
            num = (m * (b - m) * x) / ((a + 2.0 * m - 1.0) * (a + 2.0 * m))
        else:
            num = -((a + m) * (a + b + m) * x) / ((a + 2.0 * m) * (a + 2.0 * m + 1.0))
        d = 1.0 + num * d
        if abs(d) < tiny:
            d = tiny
        d = 1.0 / d
        c = 1.0 + num / c
        if abs(c) < tiny:
            c = tiny
        f *= c * d
        if abs(1.0 - c * d) < 1e-15:
            break
    return front * (f - 1.0) / a


def clopper_pearson(k, n, level=0.99):
    """Clopper-Pearson interval, in its Beta-quantile form
        low  = BetaInv(alpha;   k,   n-k+1),
        high = BetaInv(1-alpha; k+1, n-k),
    obtained by bisection on betainc_reg.  k may be a weighted count; it is used
    as given.  This is the DESCRIPTIVE naive comparison the contract names in
    NC-3(b); it is explicitly NOT the S2 rejection statistic, which is computed
    in exact rational arithmetic elsewhere."""
    alpha = (1.0 - level) / 2.0
    if n <= 0:
        return (0.0, 1.0)
    k = float(k)
    n = float(n)

    def betainv(a, b, q):
        if a <= 0:
            return 0.0
        if b <= 0:
            return 1.0
        lo, hi = 0.0, 1.0
        for _ in range(200):
            mid = (lo + hi) / 2.0
            if betainc_reg(a, b, mid) < q:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2.0

    low = 0.0 if k <= 0 else betainv(k, n - k + 1.0, alpha)
    high = 1.0 if k >= n else betainv(k + 1.0, n - k, 1.0 - alpha)
    return (low, high)


def chi2_sf(x, df):
    """Upper tail of the chi-square distribution: Q(df/2, x/2), by series /
    continued fraction (pure Python, no scipy)."""
    if x <= 0:
        return 1.0
    a, xx = df / 2.0, x / 2.0
    if xx < a + 1:
        term = 1.0 / a
        s = term
        n = 1
        while True:
            term *= xx / (a + n)
            s += term
            if abs(term) < abs(s) * 1e-16 or n > 100000:
                break
            n += 1
        return max(0.0, min(1.0, 1.0 - s * math.exp(-xx + a * math.log(xx) - math.lgamma(a))))
    tiny = 1e-300
    b = xx + 1 - a
    c = 1.0 / tiny
    d = 1.0 / b
    hh = d
    for i in range(1, 100000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        de = d * c
        hh *= de
        if abs(de - 1.0) < 1e-16:
            break
    return max(0.0, min(1.0, math.exp(-xx + a * math.log(xx) - math.lgamma(a)) * hh))


def holm(pvals):
    """Holm-Bonferroni adjusted p-values, order preserved."""
    m = len(pvals)
    idx = sorted(range(m), key=lambda i: pvals[i])
    adj = [0.0] * m
    prev = 0.0
    for rank, i in enumerate(idx):
        v = min(1.0, (m - rank) * pvals[i])
        v = max(v, prev)
        adj[i] = v
        prev = v
    return adj


def fisher_combined(pvals):
    if not pvals:
        return 1.0, 0.0
    eps = 1e-300
    stat = -2.0 * sum(math.log(max(p, eps)) for p in pvals)
    return chi2_sf(stat, 2 * len(pvals)), stat


def ks_one_sample(counts, probs):
    """KS statistic of an empirical count vector against a discrete distribution."""
    n = sum(counts)
    if n == 0:
        return 0.0
    D = 0.0
    ce = 0
    ct = 0.0
    for c, pr in zip(counts, probs):
        ce += c
        ct += pr
        D = max(D, abs(ce / n - ct))
    return D


def ks_two_sample(c1, c2):
    n1, n2 = sum(c1), sum(c2)
    if n1 == 0 or n2 == 0:
        return 0.0
    D = 0.0
    a = b = 0
    for x, y in zip(c1, c2):
        a += x
        b += y
        D = max(D, abs(a / n1 - b / n2))
    return D


# ===========================================================================
# 14.  Sample assembly and the three weightings (contract section 4)
# ===========================================================================
def build_samples(records):
    out = []
    for rec in records:
        p = rec["p"]
        for c in rec["classes"]:
            out.append({
                "p": p, "tier": rec["tier"], "X_p": rec["X_p"],
                "class_index": c["class_index"], "delta": c["delta_E"],
                "P_plus": c["P_plus"], "w": c["aut_half_order_w"],
                "galois_stable": c["galois_stable"],
                "counts": {int(k): v for k, v in
                           c["representation_counts_pm_pairs"].items()},
            })
    return out


def weight_of(s, weighting):
    """W-CURVE: uniform over supersingular j-invariants -- 1 for a Galois-stable
    class (j in F_p) and 2 otherwise.  W-TYPE: uniform over conjugacy classes.
    W-MASS: the contract's literal '1/|Aut(E)|', which for a class with
    w = |O^x|/2 is 1/(2w).  Note 1/(2w) is proportional to 1/w, so every
    normalised statistic is unchanged by the factor 2; the mass FORMULA itself
    uses the measure over curves, c_i/|Aut|, and that version is checked
    separately in mass_check."""
    if weighting == "W-TYPE":
        return Fraction(1)
    if weighting == "W-CURVE":
        return Fraction(1) if s["galois_stable"] else Fraction(2)
    return Fraction(1, 2 * s["w"])


# ===========================================================================
# 15.  S2 -- the ell = 2 parity statistic
# ===========================================================================
def s2_core(samples, weighting):
    if not samples:
        return None
    W = Fraction(0)
    W2 = Fraction(0)
    num_null = Fraction(0)
    var_null = Fraction(0)
    num_obs = Fraction(0)
    for s in samples:
        w = weight_of(s, weighting)
        n = s["delta"]
        q = Fraction(n // 2, n)
        W += w
        W2 += w * w
        num_null += w * q
        var_null += w * w * q * (1 - q)
        if n % 2 == 0:
            num_obs += w
    p_null = num_null / W
    Var_null = var_null / (W * W)
    p_obs = num_obs / W
    Var_obs = p_obs * (1 - p_obs) * W2 / (W * W)
    denom = Var_obs + Var_null
    diff = p_obs - p_null
    reject_exact = (diff * diff > 9 * denom) if denom > 0 else False
    z = float(diff) / math.sqrt(float(denom)) if denom > 0 else 0.0
    return {
        "n_samples": len(samples),
        "total_weight": str(W),
        "p_obs_exact": str(p_obs), "p_obs_float": float(p_obs),
        "p_null_exact": str(p_null), "p_null_float": float(p_null),
        "Var_obs_exact": str(Var_obs), "Var_null_exact": str(Var_null),
        "z_2_float": z,
        "abs_z_gt_3_EXACT_RATIONAL_COMPARISON": bool(reject_exact),
        "exact_comparison_form": "(p_obs - p_null)^2 > 9 (Var_obs + Var_null)",
        "sign": (1 if diff > 0 else (-1 if diff < 0 else 0)),
        "p_obs_over_p_null_exact": str(p_obs / p_null) if p_null > 0 else None,
        "log2_p_obs_over_p_null": (math.log2(float(p_obs / p_null))
                                   if p_null > 0 and p_obs > 0 else None),
    }


def s2_naive(samples, weighting):
    """The comparison NC-3(b) names: P(delta even) against 1/2, exact binomial
    Clopper-Pearson 99% interval.  Reported descriptively; NOT the rejection
    statistic (contract S2)."""
    if not samples:
        return None
    W = Fraction(0)
    even = Fraction(0)
    for s in samples:
        w = weight_of(s, weighting)
        W += w
        if s["delta"] % 2 == 0:
            even += w
    n_eff = float(W)
    k_eff = float(even)
    lo, hi = clopper_pearson(k_eff, n_eff, 0.99)
    frac = even / W
    return {"effective_n": str(W), "effective_even": str(even),
            "fraction_exact": str(frac), "fraction_float": float(frac),
            "clopper_pearson_99_low": lo, "clopper_pearson_99_high": hi,
            "one_half_inside_CI": bool(lo <= 0.5 <= hi)}


_RESID_CACHE = {}


def resid_fracs(n, ell):
    """Exact vector [ #{1<=m<=n : m = r mod ell} / n ]_{r<ell}: the size-matched
    residue distribution of a uniform random integer in [1, n]."""
    key = (n, ell)
    v = _RESID_CACHE.get(key)
    if v is None:
        cnt = [0] * ell
        for m in range(1, n + 1):
            cnt[m % ell] += 1
        v = [Fraction(c, n) for c in cnt]
        _RESID_CACHE[key] = v
    return v


def s2_secondary_mod_ell(samples, ell, weighting):
    """delta_E mod ell against the exact size-matched multinomial null."""
    if not samples:
        return None
    obs = [Fraction(0)] * ell
    exp = [Fraction(0)] * ell
    W = Fraction(0)
    for s in samples:
        w = weight_of(s, weighting)
        n = s["delta"]
        W += w
        obs[n % ell] += w
        rf = resid_fracs(n, ell)
        for r in range(ell):
            exp[r] += w * rf[r]
    chi = 0.0
    for r in range(ell):
        e = float(exp[r])
        if e > 0:
            chi += (float(obs[r]) - e) ** 2 / e
    return {"ell": ell, "observed_weighted": [str(x) for x in obs],
            "expected_weighted": [str(x) for x in exp],
            "chi_square": chi, "df": ell - 1,
            "p_value": chi2_sf(chi, ell - 1)}


# ===========================================================================
# 16.  S3 -- the size-model double fit
# ===========================================================================
def build_pplus_table(nmax):
    return [0] + [largest_prime_factor(m) for m in range(1, nmax + 1)]


def f1_table(pp, n):
    d = {}
    for m in range(1, n + 1):
        d[pp[m]] = d.get(pp[m], 0) + 1
    return {y: Fraction(c, n) for y, c in d.items()}


class SizeModels:
    """Exact tables for M1 and M2 and the derived log-likelihood ratios.

    f(y | n) = #{ m <= n : P+(m) = y } / n, by direct sieve enumeration -- NO
    Dickman asymptotics anywhere, as the contract requires.  M1 uses n = the
    sample's own delta_E; M2 uses n = X_p.  Everything is built once, exactly, in
    rational arithmetic; the log ratios are then cached in both float (used for
    the null replication arms) and 60-digit Decimal (used for the reported
    observed value, so the float comparison against the |LLR| > 10 threshold has
    an exact-arithmetic counterpart)."""

    def __init__(self, nmax):
        self.pp = build_pplus_table(nmax)
        self._t = {}
        self._cdf = {}
        self._lnf = {}
        self._lnd = {}

    def table(self, n):
        t = self._t.get(n)
        if t is None:
            t = f1_table(self.pp, n)
            self._t[n] = t
        return t

    def cdf_below(self, n):
        """{y: F(y^-)} and {y: f(y)} for the randomised PIT."""
        c = self._cdf.get(n)
        if c is None:
            tab = self.table(n)
            acc = Fraction(0)
            c = {}
            for y in sorted(tab):
                c[y] = (float(acc), float(tab[y]))
                acc += tab[y]
            self._cdf[n] = c
        return c

    def lnr(self, n, X, y):
        """(kind, float, Decimal) for ln f1(y|n) - ln f2(y|X)."""
        key = (n, X, y)
        v = self._lnf.get(key)
        if v is not None:
            return v
        f1 = self.table(n).get(y, Fraction(0))
        f2 = self.table(X).get(y, Fraction(0))
        if f1 == 0:
            v = ("zero_f1", float("-inf"), None)
        elif f2 == 0:
            v = ("zero_f2", float("inf"), None)
        else:
            r = f1 / f2
            d = (Decimal(r.numerator) / Decimal(r.denominator)).ln()
            v = ("ok", float(d), d)
        self._lnf[key] = v
        return v


def s3_llr(samples, weighting, SM, exact=False):
    """Returns (LLR_float, LLR_decimal_or_None, total weight, #f1=0, #f2=0).

    M1's support is [1, n_i] while M2's is [1, X_p] >= [1, n_i], so the real data
    (where y_i = P+(delta_i) <= delta_i = n_i by construction) never make f1 zero.
    A null arm generated from M2 CAN make f1 zero; that is recorded, not hidden,
    and turns the LLR into -infinity."""
    tot_f = 0.0
    tot_d = Decimal(0) if exact else None
    Wt = Fraction(0)
    z1 = z2 = 0
    for s in samples:
        w = weight_of(s, weighting)
        kind, lf, ld = SM.lnr(s["delta"], s["X_p"], s["P_plus"])
        Wt += w
        if kind == "zero_f1":
            z1 += 1
            continue
        if kind == "zero_f2":
            z2 += 1
            continue
        wf = float(w)
        tot_f += wf * lf
        if exact:
            tot_d += Decimal(w.numerator) / Decimal(w.denominator) * ld
    return tot_f, tot_d, Wt, z1, z2


def s3_llr_grouped(groups, SM):
    """LLR over grouped data: groups is a list of (n, X, y, weight, count)."""
    tot = 0.0
    z1 = z2 = 0
    for n, X, y, w, c in groups:
        kind, lf, _ = SM.lnr(n, X, y)
        if kind == "zero_f1":
            z1 += c
            continue
        if kind == "zero_f2":
            z2 += c
            continue
        tot += w * lf * c
    return tot, z1, z2


def llr_value(tot, z1, z2):
    if z1 > 0:
        return float("-inf")
    if z2 > 0:
        return float("inf")
    return float(tot)


def s3_pit_values(samples, SM, model, rng):
    """Randomised probability-integral transform values."""
    out = []
    rnd = rng.random
    for s in samples:
        n = s["delta"] if model == "M1" else s["X_p"]
        Fm, f = SM.cdf_below(n)[s["P_plus"]]
        out.append(Fm + rnd() * f)
    return out


def weighted_ks_uniform(uvals, weights_norm):
    """sup_x | weighted empirical CDF of {u_i} - x |, weights already normalised
    to sum 1.  Both one-sided suprema are taken, so ties and the jump at each u
    are handled exactly as in the Monte-Carlo null below."""
    pairs = sorted(zip(uvals, weights_norm))
    D = 0.0
    acc = 0.0
    for u, w in pairs:
        d = acc - u
        if d > D:
            D = d
        elif -d > D:
            D = -d
        acc += w
        d = acc - u
        if d > D:
            D = d
        elif -d > D:
            D = -d
    return D


def mc_ks_uniform_null(weights_norm, reps, rng):
    """Monte-Carlo null of the weighted one-sample KS statistic.

    Under the model the u_i are exactly Uniform(0,1) and independent of the
    weights, so a replicate is: draw n uniforms, sort them, and attach the SAME
    weight multiset in a uniformly random order.  Identical in distribution to
    drawing (u_i) alongside the fixed weights and sorting the pairs, which is
    what weighted_ks_uniform does to the observed data."""
    n = len(weights_norm)
    equal = (min(weights_norm) == max(weights_norm))
    rnd = rng.random
    out = []
    if equal:
        w0 = weights_norm[0]
        hi = [(i + 1) * w0 for i in range(n)]
        lo = [i * w0 for i in range(n)]
        for _ in range(reps):
            us = sorted([rnd() for _ in range(n)])
            dp = max(map(operator.sub, hi, us))
            dm = max(map(operator.sub, us, lo))
            out.append(dp if dp > dm else dm)
    else:
        ws = list(weights_norm)
        for _ in range(reps):
            us = sorted([rnd() for _ in range(n)])
            rng.shuffle(ws)
            acc = list(itertools.accumulate(ws))
            below = [0.0] + acc[:-1]
            dp = max(map(operator.sub, acc, us))
            dm = max(map(operator.sub, us, below))
            out.append(dp if dp > dm else dm)
    return out


# ===========================================================================
# 17.  S4 -- the disjointness ratio
# ===========================================================================
_SMOOTH_CACHE = {}


def smooth_values(X_p, B):
    key = (X_p, B)
    if key not in _SMOOTH_CACHE:
        _SMOOTH_CACHE[key] = [n for n in range(1, X_p + 1) if is_smooth(n, B)]
    return _SMOOTH_CACHE[key]


def s4_counts(samples, B):
    out = []
    for s in samples:
        c = 0
        for n in smooth_values(s["X_p"], B):
            c += s["counts"].get(n, 0)
        out.append(c)
    return out


def d2_from(counts, weights):
    W = sum(weights)
    if W == 0:
        return None
    lam = sum(w * c for w, c in zip(weights, counts)) / W
    hit = sum(w for w, c in zip(weights, counts) if c >= 1) / W
    return lam, hit


def d2ref(lam):
    lf = float(lam)
    if lf <= 0:
        return None
    return (1.0 - math.exp(-lf)) / lf


def bootstrap_d2star(counts, weights, reps, rng):
    """Non-parametric bootstrap over CLASSES.  Implemented as a multinomial over
    the distinct (count, weight) categories, which is exactly equivalent to
    resampling classes with replacement and is far cheaper."""
    cats = {}
    for c, w in zip(counts, weights):
        key = (c, w)
        cats[key] = cats.get(key, 0) + 1
    keys = sorted(cats, key=lambda k: (k[0], float(k[1])))
    n = len(counts)
    probs = [cats[k] / n for k in keys]
    out = []
    attempted = 0
    for _ in range(reps):
        attempted += 1
        m = multinomial_sample(rng, n, probs)
        W = 0.0
        S = 0.0
        H = 0.0
        for (c, w), mm in zip(keys, m):
            wf = float(w)
            W += wf * mm
            S += wf * mm * c
            H += wf * mm * (1 if c >= 1 else 0)
        if W <= 0:
            continue
        lam = S / W
        hit = H / W
        if lam <= 0:
            continue
        ref = (1.0 - math.exp(-lam)) / lam
        out.append((hit / lam) / ref)
    out.sort()
    return out, attempted


def poisson_tail_ratios(lam, tmax=4000):
    """[P(X>=t+1)/P(X>=t)]_{t>=1} for X ~ Poisson(lam), plus P(X>=1)."""
    pmf = math.exp(-lam)
    tail = 1.0
    tails = []
    for t in range(0, tmax):
        tail -= pmf
        if tail <= 0.0:
            tails.append(0.0)
            break
        tails.append(tail)          # tails[t] = P(X >= t+1)
        pmf *= lam / (t + 1)
    ratios = []
    for t in range(1, len(tails)):
        ratios.append(tails[t] / tails[t - 1] if tails[t - 1] > 0 else 0.0)
    return tails[0] if tails else 0.0, ratios


def null_c_d2star(counts, weights, lam, reps, rng):
    """NULL-C: the representation events are redistributed independently across
    classes at the measured lambda_hat -- independent Poisson(lambda_hat) counts,
    which is the perfect-disjointness reference at the same finite sample -- and
    D2* is recomputed by the IDENTICAL estimator.

    Sampled exactly by the level decomposition
        N_1 ~ Bin(m, P(X>=1)),   N_{t+1} | N_t ~ Bin(N_t, P(X>=t+1)/P(X>=t)),
    which holds because the classes are independent and each is conditioned only
    on its own count.  Then #{count >= 1} = N_1 and the total count = sum_t N_t.
    This is exact, not an approximation, and avoids drawing one Poisson variate
    per class per replicate."""
    groups = {}
    for w in weights:
        groups[w] = groups.get(w, 0) + 1
    lf = float(lam)
    p1, ratios = poisson_tail_ratios(lf)
    gitems = sorted(groups.items(), key=lambda kv: float(kv[0]))
    out = []
    attempted = 0
    for _ in range(reps):
        attempted += 1
        W = 0.0
        S = 0.0
        H = 0.0
        for w, m in gitems:
            wf = float(w)
            W += wf * m
            n_t = binomial_sample(rng, m, p1)
            H += wf * n_t
            tot = n_t
            for r in ratios:
                if n_t <= 0 or r <= 0.0:
                    break
                n_t = binomial_sample(rng, n_t, r)
                tot += n_t
            S += wf * tot
        if W <= 0 or S <= 0:
            continue
        lam_r = S / W
        hit = H / W
        ref = (1.0 - math.exp(-lam_r)) / lam_r
        out.append((hit / lam_r) / ref)
    out.sort()
    return out, attempted


def s4_pool(samples, rngBoot, rngC):
    """S4 for one prime pool, under all three weightings, with the bootstrap and
    NULL-C reference distributions and the three pre-registered rarity regimes."""
    out = {"n_classes": len(samples), "per_B": {}}
    for B in B_GRID:
        cnts = s4_counts(samples, B)
        out["per_B"][str(B)] = {}
        for wt in WEIGHTINGS:
            ws = [weight_of(s, wt) for s in samples]
            lam, hit = d2_from(cnts, ws)
            ref = d2ref(lam)
            D2 = hit / lam if lam > 0 else None
            D2s = (float(D2) / ref) if (D2 is not None and ref) else None
            boot, batt = bootstrap_d2star(cnts, ws, BOOTSTRAP_REPLICATES, rngBoot)
            nullc, catt = null_c_d2star(cnts, ws, lam, BOOTSTRAP_REPLICATES, rngC)
            Wtot = sum(float(w) for w in ws)
            smooth_hit = sum(float(w) for w, s in zip(ws, samples)
                             if is_smooth(s["delta"], B))
            out["per_B"][str(B)][wt] = {
                "lambda_hat_exact": str(lam), "lambda_hat": float(lam),
                "P_count_ge_1_exact": str(hit), "P_count_ge_1": float(hit),
                "D2_exact": str(D2) if D2 is not None else None,
                "D2": float(D2) if D2 is not None else None,
                "D2_ref": ref, "D2_star": D2s,
                "bootstrap_replicates_attempted": batt,
                "bootstrap_replicates_completed": len(boot),
                "D2_star_bootstrap_99_low": percentile(boot, 0.005),
                "D2_star_bootstrap_99_high": percentile(boot, 0.995),
                "NULL_C_replicates_attempted": catt,
                "NULL_C_replicates_completed": len(nullc),
                "NULL_C_D2_star_median": percentile(nullc, 0.5),
                "NULL_C_D2_star_99_low": percentile(nullc, 0.005),
                "NULL_C_D2_star_99_high": percentile(nullc, 0.995),
                "P_E_SMOOTH": smooth_hit / Wtot,
                "P_E_EXISTS": float(hit),
                "S4c_gap": float(hit) - smooth_hit / Wtot,
                "S4c_gap_bits": (math.log2(float(hit) / (smooth_hit / Wtot))
                                 if smooth_hit > 0 and hit > 0 else None)}
    prim = {B: out["per_B"][str(B)]["W-CURVE"]["lambda_hat"] for B in B_GRID}
    regimes = {}
    for target in (0.30, 0.10, 0.03):
        Bsel = min(B_GRID, key=lambda B: abs(prim[B] - target))
        row = out["per_B"][str(Bsel)]["W-CURVE"]
        regimes[str(target)] = {
            "B": Bsel, "achieved_lambda_hat": prim[Bsel],
            "reached": bool(target / 2.0 <= prim[Bsel] <= 2.0 * target),
            "reached_rule": ("Executor reading, declared here: a regime counts as "
                             "REACHED when the selected B's lambda_hat lies within a "
                             "factor of two of the target; the contract fixes the "
                             "selection rule but not the reachability test, and every "
                             "raw lambda_hat is reported so any other test can be "
                             "applied by a reviewer."),
            "D2_star": row["D2_star"],
            "D2_star_99_CI": [row["D2_star_bootstrap_99_low"],
                              row["D2_star_bootstrap_99_high"]],
            "NULL_C_99_CI": [row["NULL_C_D2_star_99_low"],
                             row["NULL_C_D2_star_99_high"]]}
    out["regimes"] = regimes
    out["distinct_B_selected"] = sorted({v["B"] for v in regimes.values()})
    out["all_three_regimes_distinct"] = bool(len(out["distinct_B_selected"]) == 3)
    ordered = sorted(regimes.items(), key=lambda kv: -kv[1]["achieved_lambda_hat"])
    least_rare, rarest = ordered[0][1], ordered[-1][1]
    n_ref = sum(1 for v in regimes.values()
                if v["D2_star"] is not None and v["D2_star"] <= 0.85
                and v["D2_star_99_CI"][1] is not None and v["D2_star_99_CI"][1] < 0.95)
    hi = rarest["D2_star_99_CI"][1]
    lo = rarest["D2_star_99_CI"][0]
    boot_res = abs((hi or 0.0) - (lo or 0.0))
    not_shrinking = bool(rarest["D2_star"] is not None
                         and least_rare["D2_star"] is not None
                         and rarest["D2_star"] <= least_rare["D2_star"] + boot_res)
    consistent = all(v["D2_star_99_CI"][0] is not None
                     and v["D2_star_99_CI"][0] <= 1.0 <= v["D2_star_99_CI"][1]
                     for v in regimes.values())
    reached = [v for v in regimes.values() if v["reached"]]
    consistent_reached_only = bool(reached) and all(
        v["D2_star_99_CI"][0] is not None
        and v["D2_star_99_CI"][0] <= 1.0 <= v["D2_star_99_CI"][1] for v in reached)
    out["n_regimes_reached"] = len(reached)
    out["CI_contains_1_in_all_REACHED_regimes"] = consistent_reached_only
    nullc_biased = any(
        out["per_B"][str(v["B"])]["W-CURVE"]["NULL_C_D2_star_99_high"] is not None
        and out["per_B"][str(v["B"])]["W-CURVE"]["NULL_C_D2_star_99_high"] < 1.0
        for v in regimes.values())
    if n_ref >= 2 and not_shrinking:
        verdict = ("REFUTED IN TESTED SCOPE" if not nullc_biased else
                   "VOID (NULL-C shows the estimator is biased at this sample size)")
    elif consistent:
        verdict = "CONSISTENT WITH DISJOINTNESS IN TESTED SCOPE"
    else:
        verdict = "INCONCLUSIVE"
    out["refuted_regimes_count"] = n_ref
    out["deficit_not_shrinking_as_lambda_decreases"] = not_shrinking
    out["NULL_C_indicates_estimator_bias"] = nullc_biased
    out["CI_contains_1_in_all_three_regimes"] = consistent
    out["monotonicity_tail_check"] = {
        "D2_star_by_lambda": [{"lambda_hat": v["achieved_lambda_hat"],
                               "D2_star": v["D2_star"]} for _, v in ordered],
        "moves_toward_1_as_lambda_decreases": bool(
            rarest["D2_star"] is not None and least_rare["D2_star"] is not None
            and abs(1 - rarest["D2_star"]) <= abs(1 - least_rare["D2_star"]))}
    out["VERDICT"] = verdict
    return out


def percentile(sorted_vals, q):
    if not sorted_vals:
        return None
    idx = q * (len(sorted_vals) - 1)
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return sorted_vals[lo]
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (idx - lo)


# ===========================================================================
# 18.  S1 -- the walk sampler and its tests
# ===========================================================================
def run_walks(nbr, rev, n_walk, L, rng, start):
    """Non-backtracking walk in the ell-ideal graph started at the verified O_0
    (vertex index of O_0 is passed as start).  Returns endpoint class counts."""
    h = len(nbr)
    deg = len(nbr[0])
    counts = [0] * h
    getr = rng.randrange
    for _ in range(n_walk):
        v = start
        back = -1
        for _ in range(L):
            if back < 0:
                t = getr(deg)
            else:
                t = getr(deg - 1)
                if t >= back:
                    t += 1
            nv = nbr[v][t]
            back = rev[v][t]
            v = nv
        counts[v] += 1
    return counts


S1_WORKERS = 4


def _s1_worker(rec):
    return s1_for_prime(rec, SEEDS["walk_sampler"], SEEDS["monte_carlo_ks"])


def s1_for_prime(rec, seed_walk, seed_mc):
    p = rec["p"]
    nbr = rec["graph"]["neighbours"]
    rev = rec["graph"]["reverse"]
    start_index = rec["graph"]["start_index"]
    h = rec["n_types"]
    deltas = [c["delta_E"] for c in rec["classes"]]
    atoms = sorted(set(deltas))
    exact_counts = [sum(1 for d in deltas if d == a) for a in atoms]
    exact_probs = [c / h for c in exact_counts]
    n_walk = max(20 * h, 20000)
    Lbase = max(1, math.ceil(math.log2(p)))
    rngw = random.Random(seed_walk + p)
    rngm = random.Random(seed_mc + p)

    # shared Monte-Carlo nulls (they depend only on the exact distribution and
    # on n_walk, not on L)
    d_null_1 = []
    for _ in range(MC_REPLICATES):
        m = multinomial_sample(rngm, n_walk, exact_probs)
        d_null_1.append(ks_one_sample(m, exact_probs))
    d_null_1.sort()
    d_null_2 = []
    for _ in range(MC_REPLICATES):
        a = multinomial_sample(rngm, n_walk, exact_probs)
        b = multinomial_sample(rngm, n_walk, exact_probs)
        d_null_2.append(ks_two_sample(a, b))
    d_null_2.sort()
    unif = [1.0 / h] * h
    chi_null = []
    tv_null = []
    for _ in range(MC_REPLICATES):
        m = multinomial_sample(rngm, n_walk, unif)
        e = n_walk / h
        chi_null.append(sum((c - e) ** 2 / e for c in m))
        tv_null.append(0.5 * sum(abs(c / n_walk - 1.0 / h) for c in m))
    chi_null.sort()
    tv_null.sort()

    out = {"p": p, "n_types": h, "n_walk": n_walk, "L_base": Lbase,
           "atoms": atoms, "exact_counts": exact_counts, "lengths": {}}
    for mult in (1, 3, 10):
        L = mult * Lbase
        vis = run_walks(nbr, rev, n_walk, L, rngw, start_index)
        walk_delta = [0] * len(atoms)
        for ci, cnt in enumerate(vis):
            walk_delta[atoms.index(deltas[ci])] += cnt
        # S1a
        D1 = ks_one_sample(walk_delta, exact_probs)
        k1 = sum(1 for d in d_null_1 if d >= D1)
        p1 = (k1 + 1) / (MC_REPLICATES + 1)
        # S1b -- the reference arm is an exact-uniform draw: it is its own null
        refc = multinomial_sample(rngm, n_walk, exact_probs)
        D2s = ks_two_sample(walk_delta, refc)
        k2 = sum(1 for d in d_null_2 if d >= D2s)
        p2 = (k2 + 1) / (MC_REPLICATES + 1)
        # null-object check: the exact-uniform reference arm against the exact CDF
        Dref = ks_one_sample(refc, exact_probs)
        kref = sum(1 for d in d_null_1 if d >= Dref)
        pref = (kref + 1) / (MC_REPLICATES + 1)
        # S1c
        e = n_walk / h
        chi = sum((c - e) ** 2 / e for c in vis)
        chi_p = chi2_sf(chi, h - 1)
        kchi = sum(1 for c in chi_null if c >= chi)
        chi_mc_p = (kchi + 1) / (MC_REPLICATES + 1)
        tv = 0.5 * sum(abs(c / n_walk - 1.0 / h) for c in vis)
        ktv = sum(1 for t in tv_null if t >= tv)
        tv_mc_p = (ktv + 1) / (MC_REPLICATES + 1)
        # S1d
        n1 = sum(1 for d in deltas if d == 1)
        obs1 = sum(cnt for ci, cnt in enumerate(vis) if deltas[ci] == 1)
        p0 = Fraction(n1, h)
        pv = binom_two_sided_pvalue(n_walk, obs1, p0) if 0 < n1 < h else (
            1.0 if obs1 == (n_walk if n1 == h else 0) else 0.0)
        out["lengths"][str(L)] = {
            "L": L, "multiplier": mult,
            "S1a_D": D1, "S1a_mc_exceed_count": k1, "S1a_mc_p": p1,
            "S1b_D": D2s, "S1b_mc_exceed_count": k2, "S1b_mc_p": p2,
            "S1_null_object_reference_arm_D": Dref,
            "S1_null_object_reference_arm_mc_p": pref,
            "S1c_chi_square": chi, "S1c_df": h - 1, "S1c_chi_p": chi_p,
            "S1c_chi_mc_p": chi_mc_p, "S1c_TV": tv, "S1c_TV_mc_p": tv_mc_p,
            "S1d_walk_delta1": obs1, "S1d_exact_fraction": str(p0),
            "S1d_binomial_p": pv,
            "walk_delta_counts": walk_delta,
        }
    return out


# ===========================================================================
# 19.  Driver
# ===========================================================================
def primes_in(lo, hi):
    return [n for n in range(lo, hi + 1) if is_prime(n)]


def tier_primes(tier_ids):
    out = []
    for tid, lo, hi, mand in TIERS:
        if tid in tier_ids:
            out.append((tid, primes_in(lo, hi)))
    return out


def worker(args):
    p, tier, do_brute_ss, do_route_f, do_brute_box = args
    try:
        rec = enumerate_prime(p, tier, do_brute_ss, do_route_f, do_brute_box)
    except Exception as exc:  # recorded, never silently dropped
        rec = {"p": p, "tier": tier, "status": "enumeration_error",
               "error": "%s: %s" % (type(exc).__name__, exc)}
    return rec


# --------------------------------------------------------------------------
# Durable incremental persistence.
#
# ENGINEERING ONLY -- it changes no threshold, no statistic and no protocol
# step.  Every completed prime is appended to a JSON-lines file the moment it
# is produced, so that an interruption leaves a recoverable, honestly-scoped
# partial (the set of COMPLETE primes) rather than nothing.  A resumed run
# skips primes already present.  The partial-prime rule of contract section 3
# is unaffected: a prime is written only after enumerate_prime returned, and a
# record whose status is not "complete" is never counted as enumerated.
# --------------------------------------------------------------------------
def jsonl_load(path):
    out = {}
    if not path or not os.path.exists(path):
        return out
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                # a truncated final line from an interrupted write is dropped;
                # the prime is simply re-enumerated.
                continue
            out[rec["p"]] = rec
    return out


def jsonl_append(path, rec):
    with open(path, "a") as fh:
        fh.write(json.dumps(rec, default=str))
        fh.write("\n")
        fh.flush()
        os.fsync(fh.fileno())


def run_enumeration(plan, cache_path, workers, t_start):
    done = jsonl_load(cache_path)
    if done:
        print("[cache] resumed %d prime records from %s" % (len(done), cache_path),
              flush=True)
    todo = [a for a in plan if a[0] not in done]
    n_done = len(done)
    total = len(plan)
    if todo:
        if workers > 1:
            import multiprocessing as mp
            with mp.Pool(workers) as pool:
                for rec in pool.imap_unordered(worker, todo, chunksize=1):
                    done[rec["p"]] = rec
                    jsonl_append(cache_path, rec)
                    n_done += 1
                    if n_done % 10 == 0 or n_done == total:
                        print("[enum] %d/%d last_p=%d status=%s %.1fs"
                              % (n_done, total, rec["p"], rec.get("status"),
                                 time.time() - t_start), flush=True)
        else:
            for a in todo:
                rec = worker(a)
                done[rec["p"]] = rec
                jsonl_append(cache_path, rec)
                n_done += 1
                print("[enum] %d/%d p=%d status=%s" % (n_done, total, rec["p"],
                                                       rec.get("status")), flush=True)
    return [done[a[0]] for a in plan if a[0] in done]


def run_s1(complete, cache_path, workers, t_start):
    done = jsonl_load(cache_path)
    if done:
        print("[cache] resumed %d S1 rows from %s" % (len(done), cache_path), flush=True)
    todo = [r for r in complete if r["p"] not in done]
    n_done = len(done)
    total = len(complete)
    if todo:
        if workers > 1:
            import multiprocessing as mp
            with mp.Pool(workers) as pool:
                for row in pool.imap_unordered(_s1_worker, todo, chunksize=1):
                    done[row["p"]] = row
                    jsonl_append(cache_path, row)
                    n_done += 1
                    if n_done % 10 == 0 or n_done == total:
                        print("[S1] %d/%d last_p=%d %.1fs"
                              % (n_done, total, row["p"], time.time() - t_start),
                              flush=True)
        else:
            for r in todo:
                row = _s1_worker(r)
                done[row["p"]] = row
                jsonl_append(cache_path, row)
                n_done += 1
    return [done[r["p"]] for r in complete if r["p"] in done]


def build_plan(tier_ids):
    rngF = random.Random(SEEDS["route_f_sample"])
    plan = []
    tier_lists = tier_primes(tier_ids)
    tier1_primes = [pp for tid, ps in tier_lists if tid == "TIER-1" for pp in ps]
    route_f_sample = sorted(rngF.sample(tier1_primes, min(10, len(tier1_primes)))) \
        if tier1_primes else []
    for tid, ps in tier_lists:
        for p in ps:
            plan.append((p, tid, tid == "TIER-0",
                         tid == "TIER-0" or p in route_f_sample, tid == "TIER-0"))
    return plan, route_f_sample


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tiers", default="TIER-0,TIER-1")
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--stage", default="all",
                    choices=["enumerate", "s1", "analyse", "all"])
    ap.add_argument("--cache", default=None, help="JSON-lines enumeration cache")
    ap.add_argument("--s1-cache", default=None, help="JSON-lines S1 cache")
    args = ap.parse_args()
    global S1_WORKERS
    S1_WORKERS = args.workers

    t_start = time.time()
    tier_ids = args.tiers.split(",")
    plan, route_f_sample = build_plan(tier_ids)
    print("[plan] tiers=%s primes=%d route_F_sample=%s" %
          (tier_ids, len(plan), route_f_sample), flush=True)

    records = run_enumeration(plan, args.cache, args.workers, t_start)
    if args.stage == "enumerate":
        print("[enumerate] %d records in cache" % len(records), flush=True)
        return
    complete = sorted([r for r in records if r.get("status") == "complete"],
                      key=lambda r: r["p"])
    s1rows = run_s1(complete, args.s1_cache, args.workers, t_start)
    if args.stage == "s1":
        print("[s1] %d rows in cache" % len(s1rows), flush=True)
        return

    analyse(records, plan, route_f_sample, tier_ids, args.out, t_start, s1rows)


# ===========================================================================
# 20.  Analysis: the four pre-registered statistics, their nulls, the controls
# ===========================================================================
def strata_mod(samples, m):
    out = {}
    for s in samples:
        out.setdefault(s["p"] % m, []).append(s)
    return out


def by_tier(samples):
    out = {}
    for s in samples:
        out.setdefault(s["tier"], []).append(s)
    return out


def analyse(records, plan, route_f_sample, tier_ids, outpath, t_start, s1rows_in=None):
    result = {}
    result["experiment_id"] = "EXP-HEUR-d640d9"
    result["run_id"] = "RUN-HEUR-d640d9-a"
    result["seeds_used"] = SEEDS
    result["contract_note"] = (
        "Heuristic 1 is a TAIL statement at u ~ 13.1; this run measures the BODY at "
        "toy primes with u <~ 4.5. Nothing here can confirm Heuristic 1, support P0, "
        "support any margin row or support the attack, and nothing here refutes "
        "Theorem 1.1 or the p^{1/3+o(1)} exponent (contract section 0; SP-H).")

    complete = [r for r in records if r.get("status") == "complete"]
    discarded = [{"p": r["p"], "tier": r.get("tier"), "reason": r.get("status"),
                  "error": r.get("error")} for r in records
                 if r.get("status") != "complete"]
    complete.sort(key=lambda r: r["p"])
    result["primes_attempted"] = [r["p"] for r in records]
    result["primes_completed"] = [r["p"] for r in complete]
    result["primes_attempted_but_discarded"] = discarded
    tiers_done = {}
    for tid, lo, hi, mand in TIERS:
        if tid not in tier_ids:
            continue
        want = primes_in(lo, hi)
        got = [r["p"] for r in complete if r["tier"] == tid]
        tiers_done[tid] = {"primes_in_rule": len(want), "primes_completed": len(got),
                           "tier_complete": bool(len(want) == len(got)),
                           "mandatory": mand}
    result["tiers"] = tiers_done

    samples = build_samples(complete)
    result["n_records"] = len(samples)
    result["record_floor_10000_met"] = bool(len(samples) >= 10000)

    # ---------------- controls IF-1..IF-6 ----------------
    if1_rows = []
    if1_ok = True
    cf_ok = True
    for r in complete:
        row = dict(r["IF_1"])
        row["p"] = r["p"]
        if "identity_holds_brute_force" in row:
            if not row["identity_holds_brute_force"]:
                if1_ok = False
            if not row["closed_form_matches_brute_force"]:
                cf_ok = False
        else:
            if not row["identity_holds_closed_form"]:
                if1_ok = False
        if1_rows.append(row)
    if2_dis = [d for r in complete for d in r["IF_2"]["disagreements"]]
    box_rows = [b for r in complete for b in r["IF_2"]["brute_force_box"]]
    if4_vio = [v for r in complete for v in r["IF_4"]["violations"]]
    if5_vio = [{"p": r["p"], "max_delta_E": r["IF_5"]["max_delta_E"],
                "X_p": r["IF_5"]["X_p"], "violating_classes": r["IF_5"]["violations"]}
               for r in complete if r["IF_5"]["violations"]]
    d1_fail = [{"p": r["p"], "rows": [d for d in r["D1_identity_per_n"] if not d["agree"]]}
               for r in complete
               if any(not d["agree"] for d in r["D1_identity_per_n"])]
    mass_fail = [{"p": r["p"], **r["mass_check"]} for r in complete
                 if not r["mass_check"]["curve_mass_matches"]]
    rev_bad = sum(r["graph"]["reverse_undetermined"] for r in complete)

    routef_rows = []
    for r in complete:
        rf = r.get("route_F")
        if not rf:
            continue
        keysQ = sorted(tuple(c["R_canonical_key"]) for c in r["classes"])
        keysF = sorted(tuple(k) for k in rf["canonical_keys"])
        dQ = sorted(c["delta_E"] for c in r["classes"])
        dF = sorted(int(Fraction(k[0])) for k in rf["canonical_keys"])
        routef_rows.append({
            "p": r["p"], "route_F_n_classes": rf["n_classes"],
            "route_F_n_tuples": rf["n_tuples"], "route_Q_n_types": r["n_types"],
            "counts_agree": bool(rf["n_classes"] == r["n_types"]),
            "class_multiset_agrees": bool(keysQ == keysF),
            "delta_E_multiset_agrees": bool(dQ == dF),
            "route_F_only": [list(k) for k in keysF if k not in keysQ][:20],
            "route_Q_only": [list(k) for k in keysQ if k not in keysF][:20]})

    result["controls"] = {
        "IF_1": {
            "name": "THE EXACTLY KNOWN COUNT",
            "brute_force_primes": [r["p"] for r in complete
                                   if "brute_force_count" in r["IF_1"]],
            "closed_form_verified_against_brute_force_everywhere": bool(cf_ok),
            "closed_form_used_as_reference_beyond_TIER_0": True,
            "identity": "n_types = (#SS + #{classes with delta_E = 1}) / 2",
            "identity_holds_everywhere": bool(if1_ok),
            "verdict": "PASS" if (if1_ok and cf_ok) else "FAIL",
            "rows": if1_rows},
        "IF_2": {
            "name": "Minimum computed two ways",
            "classes_checked_rank3_vs_rank4": sum(r["IF_2"]["checked"] for r in complete),
            "disagreements": if2_dis,
            "brute_force_box_checks": len(box_rows),
            "brute_force_box_disagreements": [b for b in box_rows if not b["agrees"]],
            "verdict": "PASS" if not if2_dis and all(b["agrees"] for b in box_rows)
                       else "FAIL"},
        "IF_3": {
            "name": "Route agreement",
            "route_F_run_at": [row["p"] for row in routef_rows],
            "route_F_sample_of_TIER_1": route_f_sample,
            "rows": routef_rows,
            "route_F_used_as_ground_truth": False,
            "governing_route": "Q",
            "verdict": ("PASS" if routef_rows and all(
                row["class_multiset_agrees"] and row["delta_E_multiset_agrees"]
                for row in routef_rows)
                else "ROUTE-F-DISQUALIFIED (route Q governs)")},
        "IF_4": {
            "name": "Conjugacy-test soundness (theta series of the Gross lattice)",
            "pairs_checked": sum(r["IF_4"]["pairs_checked"] for r in complete),
            "violations": if4_vio,
            "verdict": "PASS" if not if4_vio else "FAIL",
            "additional_stronger_check": (
                "for every declared-conjugate pair an explicit conjugating quaternion "
                "gamma with gamma^{-1} O_rep gamma = O_observed was produced and "
                "verified as a lattice identity; edges where none was found: %d"
                % rev_bad)},
        "IF_5": {"name": "AOV bound as a free empirical check",
                 "violations": if5_vio,
                 "verdict": "PASS (no violation)" if not if5_vio else "VIOLATIONS"},
        "IF_6": {"name": "Optional external anchor at p = 101051",
                 "reached": False,
                 "verdict": "NOT APPLICABLE: the run did not reach p = 101,051, which "
                            "is outside the contract's mandatory range. The AOV "
                            "delta_E = 36 anchor is an UNVERIFIED SECONDARY QUOTATION "
                            "and was neither used nor checked."},
        "first_moment_identity_D1": {
            "declared_identity": ("sum_i (1/w_i) * #{alpha in R_i : Trd = 0, Nrd = n p, "
                                  "ORDERED count} = H(4np), with w_i = |O_i^x|/2 and "
                                  "H the Hurwitz class number computed here by exact "
                                  "enumeration of reduced binary forms"),
            "verified_at_every_completed_prime": bool(not d1_fail),
            "failures": d1_fail,
            "calibration_verdict": "CALIBRATED" if not d1_fail else "UNCALIBRATED"},
        "mass_formula_free_check": {
            "identity": "sum over supersingular curves of 1/w = (p-1)/24",
            "holds_everywhere": bool(not mass_fail), "failures": mass_fail,
            "status": "reported, not gating"},
    }

    if not if1_ok or if2_dis or if4_vio:
        result["TERMINAL_INSTRUMENT_FAILURE"] = True
        with open(outpath, "w") as fh:
            json.dump(result, fh, indent=1)
        print("[STOP] terminal instrument failure", flush=True)
        return

    # ---------------- NULL-A ----------------
    rngA = random.Random(SEEDS["null_a"])
    null_a_samples = []
    null_a_meta = []
    for r in complete:
        forms, tries = null_a_forms(r["p"], r["n_types"], rngA, r["X_p"])
        null_a_meta.append({"p": r["p"], "requested": r["n_types"],
                            "generated": len(forms), "draws": tries})
        for f in forms:
            null_a_samples.append({"p": r["p"], "tier": r["tier"], "X_p": r["X_p"],
                                   "class_index": -1, "delta": f["delta_null"],
                                   "P_plus": f["P_plus"], "w": 1,
                                   "galois_stable": f["galois_stable"],
                                   "counts": f["representation_counts_pm_pairs"]})
    result["NULL_A"] = {
        "construction": null_a_forms.__doc__,
        "weighting_rule_for_the_null": (
            "W-TYPE = 1 for every form; W-CURVE = 1 if the form's minimum is 1 else 2 "
            "(the arithmetic rule 'Galois-stable <=> delta_E = 1' transported to the "
            "null); W-MASS = the constant 1/(2*1), i.e. uniform, because a random "
            "ternary form carries no automorphism-of-an-order structure -- every "
            "statistic here is weight-normalised, so a constant weight is the same "
            "measure as weight 1. Recorded as an Executor reading, not as a contract "
            "statement."),
        "n_forms": len(null_a_samples), "per_prime": null_a_meta,
        "delta_null_histogram": {},
    }
    hh = {}
    for s in null_a_samples:
        hh[s["delta"]] = hh.get(s["delta"], 0) + 1
    result["NULL_A"]["delta_null_histogram"] = {str(k): v for k, v in sorted(hh.items())}

    # ---------------- S2 ----------------
    s2 = {"rejection_statistic_definition": (
        "q_i = floor(n_i/2)/n_i exactly; p_null = sum w q / sum w; "
        "Var_null = sum w^2 q(1-q)/(sum w)^2; p_obs = weighted even fraction; "
        "Var_obs = p_obs(1-p_obs) sum w^2/(sum w)^2; z_2 = (p_obs-p_null)/"
        "sqrt(Var_obs+Var_null). All rational parts are exact; the threshold "
        "|z_2| > 3 is decided by the EXACT rational comparison "
        "(p_obs-p_null)^2 > 9(Var_obs+Var_null)."),
        "naive_comparison_required_by_NC_3": {}, "pooled": {}, "by_p_mod_8": {},
        "by_tier": {}, "secondary_mod_ell": {}, "null_A": {}, "null_B": {}}
    for wt in WEIGHTINGS:
        s2["pooled"][wt] = s2_core(samples, wt)
        s2["naive_comparison_required_by_NC_3"][wt] = {
            "overall": s2_naive(samples, wt),
            "by_p_mod_8": {str(k): s2_naive(v, wt)
                           for k, v in sorted(strata_mod(samples, 8).items())}}
        s2["by_p_mod_8"][wt] = {str(k): s2_core(v, wt)
                                for k, v in sorted(strata_mod(samples, 8).items())}
        s2["by_tier"][wt] = {k: s2_core(v, wt) for k, v in sorted(by_tier(samples).items())}
        s2["secondary_mod_ell"][wt] = {}
        for ell in (3, 5, 7, 11):
            s2["secondary_mod_ell"][wt][str(ell)] = {
                "overall": s2_secondary_mod_ell(samples, ell, wt),
                "by_p_mod_ell": {str(k): s2_secondary_mod_ell(v, ell, wt)
                                 for k, v in sorted(strata_mod(samples, ell).items())}}
        s2["null_A"][wt] = s2_core(null_a_samples, wt)
    # ---- NULL-B replications of the S2 statistic, under BOTH coherent readings
    #
    # UNDERSPECIFICATION, recorded rather than resolved by fiat.  NULL-B says
    # "delta_E replaced by a uniform random integer in [1, n_i]", and S2's null
    # is built from "n_i, the observed delta_E of sample i".  After the
    # replacement there are two things "the observed delta_E" can mean, and they
    # give different numbers:
    #   READING-KEEP-SIZE : q_i is still evaluated at the ORIGINAL delta_E.
    #                       The S2 statistic is then exactly calibrated by
    #                       construction, which is what a null arm is for.
    #   READING-NEW-SIZE  : q_i is evaluated at the REPLACEMENT integer.
    #                       This is the more literal reading of "the observed
    #                       delta_E of sample i" applied to the null data.
    # Both are computed; neither is chosen for the reader.
    rngB = random.Random(SEEDS["null_b"])
    grp = {}
    for s in samples:
        key = (s["delta"], weight_of(s, "W-CURVE"))
        grp[key] = grp.get(key, 0) + 1
    grp_items = sorted(grp.items(), key=lambda kv: (kv[0][0], float(kv[0][1])))

    def s2_z_from(pairs):
        """pairs: list of (n_for_q, weight, count, even_count)."""
        W = Fraction(0); W2 = Fraction(0); nn = Fraction(0)
        vv = Fraction(0); oo = Fraction(0)
        for n, w, c, ev in pairs:
            q = Fraction(n // 2, n)
            W += w * c
            W2 += w * w * c
            nn += w * q * c
            vv += w * w * q * (1 - q) * c
            oo += w * ev
        if W == 0:
            return 0.0
        p_null = nn / W
        p_obs = oo / W
        Var_null = vv / (W * W)
        Var_obs = p_obs * (1 - p_obs) * W2 / (W * W)
        den = Var_obs + Var_null
        return (float(p_obs - p_null) / math.sqrt(float(den))) if den > 0 else 0.0

    nb_keep, nb_new = [], []
    for _ in range(NULL_REPLICATIONS):
        keep_pairs, new_pairs = [], []
        for (n, w), c in grp_items:
            # m ~ U[1,n] for each of the c samples in the group: the counts per
            # value are exactly multinomial with equal cell probabilities.
            cnts = multinomial_sample(rngB, c, [1.0 / n] * n)
            ev = sum(cnts[v - 1] for v in range(1, n + 1) if v % 2 == 0)
            keep_pairs.append((n, w, c, ev))
            for v in range(1, n + 1):
                if cnts[v - 1]:
                    new_pairs.append((v, w, cnts[v - 1],
                                      cnts[v - 1] if v % 2 == 0 else 0))
        nb_keep.append(s2_z_from(keep_pairs))
        nb_new.append(s2_z_from(new_pairs))
    nb_keep.sort(); nb_new.sort()
    s2["null_B"] = {
        "replications": NULL_REPLICATIONS,
        "construction": ("delta_E replaced by a uniform random integer in [1, n_i]; "
                         "W-CURVE weighting"),
        "UNDERSPECIFICATION_NOTE": (
            "The contract does not say whether, after the replacement, q_i is "
            "evaluated at the ORIGINAL delta_E or at the REPLACEMENT integer. The two "
            "readings give different numbers, so both are reported and neither is "
            "chosen by the Executor. READING-KEEP-SIZE is calibrated by construction "
            "and is the arm that tests the estimator; READING-NEW-SIZE is the more "
            "literal one."),
        "READING_KEEP_SIZE": {
            "z_2_min": nb_keep[0], "z_2_max": nb_keep[-1],
            "z_2_mean": sum(nb_keep) / len(nb_keep),
            "z_2_abs_gt_3_count": sum(1 for z in nb_keep if abs(z) > 3)},
        "READING_NEW_SIZE": {
            "z_2_min": nb_new[0], "z_2_max": nb_new[-1],
            "z_2_mean": sum(nb_new) / len(nb_new),
            "z_2_abs_gt_3_count": sum(1 for z in nb_new if abs(z) > 3)},
        "calibration_note": ("under NULL-B READING-KEEP-SIZE the S2 statistic is "
                             "exactly calibrated by construction; this arm checks the "
                             "estimator, not the arithmetic object")}
    pooled = s2["pooled"]["W-CURVE"]
    C1 = bool(pooled["abs_z_gt_3_EXACT_RATIONAL_COMPARISON"])
    strata = s2["by_p_mod_8"]["W-CURVE"]
    sig = [(k, v) for k, v in strata.items()
           if v and v["abs_z_gt_3_EXACT_RATIONAL_COMPARISON"]]
    C2 = False
    for sgn in (1, -1):
        if sum(1 for k, v in sig if v["sign"] == sgn) >= 2:
            C2 = True
    tiers_present = sorted(by_tier(samples))
    higher = [t for t in tiers_present if t not in ("TIER-0", "TIER-1")]
    if higher:
        a = s2["by_tier"]["W-CURVE"].get("TIER-1")
        bsam = [s for s in samples if s["tier"] in higher]
        b = s2_core(bsam, "W-CURVE")
        c3_basis = "TIER-1 alone vs union of higher completed tiers alone"
    else:
        a = s2["by_tier"]["W-CURVE"].get("TIER-0")
        b = s2["by_tier"]["W-CURVE"].get("TIER-1")
        c3_basis = "TIER-0 alone vs TIER-1 alone (no tier beyond TIER-1 completed)"
    C3 = bool(a and b and a["sign"] == b["sign"] and a["sign"] != 0)
    nullA_same = bool(s2["null_A"]["W-CURVE"] and
                      s2["null_A"]["W-CURVE"]["abs_z_gt_3_EXACT_RATIONAL_COMPARISON"]
                      and s2["null_A"]["W-CURVE"]["sign"] == pooled["sign"])
    if C1 and C2 and C3:
        verdict = "REJECTED IN TESTED SCOPE" if not nullA_same else "VOID (NULL-A reproduces the signal)"
    elif not C1 and not C2 and not C3:
        verdict = "NOT REJECTED IN TESTED SCOPE"
    else:
        verdict = "INCONCLUSIVE (rejection condition only partially met)"
    s2["C1"] = {"met": C1, "pooled_W_CURVE": pooled}
    s2["C2"] = {"met": C2, "significant_strata": [k for k, v in sig],
                "signs": {k: v["sign"] for k, v in strata.items() if v}}
    s2["C3"] = {"met": C3, "basis": c3_basis, "arm_a": a, "arm_b": b}
    s2["null_A_voids_signal"] = nullA_same
    s2["VERDICT"] = verdict
    result["S2"] = s2

    # ---------------- S3 ----------------
    maxX = max(s["X_p"] for s in samples)
    maxn = max(max(s["delta"] for s in samples), maxX)
    SM = SizeModels(max(maxn, maxX) + 1)
    pp = SM.pp
    s3 = {"models": {"M1": "uniform random integer of the sample's own size n_i",
                     "M2": "uniform random integer of size X_p = floor((p/2)^(1/3))"},
          "llr": {}, "stability": {}, "null_B": {}, "null_B2": {},
          "goodness_of_fit": {}, "order_statistic": {}}
    for wt in WEIGHTINGS:
        totf, totd, Wt, z1, z2 = s3_llr(samples, wt, SM, exact=True)
        s3["llr"][wt] = {"LLR_total_exact_decimal60": str(totd),
                         "LLR_total_float": llr_value(totf, z1, z2),
                         "float_minus_exact": (float(Decimal(repr(totf)) - totd)
                                               if totd is not None else None),
                         "samples_with_zero_M1_density": z1,
                         "samples_with_zero_M2_density": z2,
                         "total_weight": str(Wt),
                         "LLR_per_sample_mean": totf / float(Wt),
                         "preferred": "M1" if totf > 0 else ("M2" if totf < 0 else "tie")}
    llr_primary = s3["llr"]["W-CURVE"]["LLR_total_float"]
    splits = {}
    splits["by_tier"] = {}
    for t, sub in sorted(by_tier(samples).items()):
        tt, _, _, za, zb = s3_llr(sub, "W-CURVE", SM)
        splits["by_tier"][t] = llr_value(tt, za, zb)
    splits["by_p_mod_8"] = {}
    for k, sub in sorted(strata_mod(samples, 8).items()):
        tt, _, _, za, zb = s3_llr(sub, "W-CURVE", SM)
        splits["by_p_mod_8"][str(k)] = llr_value(tt, za, zb)
    rngS = random.Random(SEEDS["tenfold_split"])
    fold = [rngS.randrange(10) for _ in samples]
    splits["tenfold"] = {}
    for f in range(10):
        sub = [s for s, ff in zip(samples, fold) if ff == f]
        tt, _, _, za, zb = s3_llr(sub, "W-CURVE", SM)
        splits["tenfold"][str(f)] = llr_value(tt, za, zb)
    splits["weightings"] = {wt: s3["llr"][wt]["LLR_total_float"]
                            for wt in ("W-CURVE", "W-TYPE")}
    s3["stability"] = splits
    sgn = 1 if llr_primary > 0 else (-1 if llr_primary < 0 else 0)
    stable = (all((1 if v > 0 else -1 if v < 0 else 0) == sgn
                  for v in splits["by_tier"].values())
              and all((1 if v > 0 else -1 if v < 0 else 0) == sgn
                      for v in splits["by_p_mod_8"].values())
              and all((1 if v > 0 else -1 if v < 0 else 0) == sgn
                      for v in splits["tenfold"].values())
              and all((1 if v > 0 else -1 if v < 0 else 0) == sgn
                      for v in splits["weightings"].values()))
    # ---- NULL-B / NULL-B2 LLR calibration, under BOTH coherent readings
    #
    # Same underspecification as in S2, and it bites harder here.  NULL-B/NULL-B2
    # say "delta_E replaced by a uniform random integer in [1, n_i]" / "[1, X_p]",
    # and the LLR needs BOTH the observable y = P+(delta_E) and the M1 size n_i.
    #   READING-KEEP-SIZE : y := P+(replacement), n_i := the ORIGINAL delta_E.
    #                       This is the arm that is M1-truth (resp. M2-truth) by
    #                       construction, so it calibrates the LLR.
    #   READING-NEW-SIZE  : y := P+(replacement), n_i := the replacement itself.
    # Under NULL-B2 / READING-KEEP-SIZE the M1 likelihood is exactly zero
    # whenever the replacement's largest prime factor exceeds the original
    # delta_E, so the LLR is exactly -infinity.  That is a structural property of
    # the two pre-registered models, reported rather than smoothed.
    def null_llr_arm(seed, size_of, keep_size):
        rng = random.Random(seed)
        gg = {}
        for s in samples:
            key = (size_of(s), s["delta"], s["X_p"], weight_of(s, "W-CURVE"))
            gg[key] = gg.get(key, 0) + 1
        items = sorted(gg.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2],
                                                   float(kv[0][3])))
        prepared = []
        for (sz, n0, X, w) in [k for k, _ in items]:
            tab = SM.table(sz)
            ys = sorted(tab)
            probs = [float(tab[y]) for y in ys]
            prepared.append((ys, probs))
        vals = []
        zeros = 0
        wf_cache = {}
        for _ in range(NULL_REPLICATIONS):
            groups = []
            for ((sz, n0, X, w), c), (ys, probs) in zip(items, prepared):
                cnts = multinomial_sample(rng, c, probs)
                wf = wf_cache.setdefault(w, float(w))
                for y, cc in zip(ys, cnts):
                    if cc:
                        groups.append((n0 if keep_size else sz, X, y, wf, cc))
            tt, za, zb = s3_llr_grouped(groups, SM)
            zeros += za
            vals.append(llr_value(tt, za, zb))
        vals.sort()
        return vals, zeros

    nbk, nbk_z = null_llr_arm(SEEDS["null_b"] + 1, lambda s: s["delta"], True)
    nbn, nbn_z = null_llr_arm(SEEDS["null_b"] + 2, lambda s: s["delta"], False)
    nb2k, nb2k_z = null_llr_arm(SEEDS["null_b2"], lambda s: s["X_p"], True)
    nb2n, nb2n_z = null_llr_arm(SEEDS["null_b2"] + 1, lambda s: s["X_p"], False)
    obs = llr_primary

    def rng_summary(vals, zeros):
        fin = [v for v in vals if math.isfinite(v)]
        return {"min": vals[0], "max": vals[-1],
                "mean_of_finite": (sum(fin) / len(fin)) if fin else None,
                "n_finite": len(fin), "n_replications": len(vals),
                "total_samples_with_zero_M1_density": zeros}

    s3["null_B"] = {
        "replications": NULL_REPLICATIONS,
        "construction": "delta_E replaced by a uniform random integer in [1, n_i]",
        "READING_KEEP_SIZE": rng_summary(nbk, nbk_z),
        "READING_NEW_SIZE": rng_summary(nbn, nbn_z)}
    s3["null_B2"] = {
        "replications": NULL_REPLICATIONS,
        "construction": "delta_E replaced by a uniform random integer in [1, X_p]",
        "READING_KEEP_SIZE": rng_summary(nb2k, nb2k_z),
        "READING_NEW_SIZE": rng_summary(nb2n, nb2n_z),
        "degeneracy_note": (
            "M1 has support [1, n_i] while M2 has support [1, X_p], and [1, n_i] is "
            "contained in [1, X_p]. Under READING-KEEP-SIZE, data generated from M2 "
            "therefore place positive mass outside M1's support, which makes the M1 "
            "likelihood exactly zero and the LLR exactly -infinity. This is a "
            "structural property of the two pre-registered models, reported rather "
            "than smoothed.")}
    s3["UNDERSPECIFICATION_NOTE"] = (
        "The contract does not say whether, after NULL-B/NULL-B2 replace delta_E, the "
        "M1 size n_i is the ORIGINAL delta_E or the replacement. The two readings give "
        "different null LLR ranges and can give different VOID verdicts, so both are "
        "computed and both verdicts are reported; the Executor chooses neither. The "
        "contract's own gloss on the void criterion ('if the observed value is not "
        "separated from both') is likewise read in two ways: OR-of-ranges and "
        "union-span. All four combinations are reported below.")

    def void_flags(nbv, nb2v):
        inside_B = nbv[0] <= obs <= nbv[-1]
        inside_B2 = nb2v[0] <= obs <= nb2v[-1]
        lo = min(nbv[0], nb2v[0])
        hi = max(nbv[-1], nb2v[-1])
        return {"observed_inside_null_B_range": bool(inside_B),
                "observed_inside_null_B2_range": bool(inside_B2),
                "VOID_reading_OR": bool(inside_B or inside_B2),
                "observed_inside_union_span": bool(lo <= obs <= hi),
                "VOID_reading_UNION_SPAN": bool(lo <= obs <= hi)}

    vf_keep = void_flags(nbk, nb2k)
    vf_new = void_flags(nbn, nb2n)
    s3["void_criterion"] = {"READING_KEEP_SIZE": vf_keep, "READING_NEW_SIZE": vf_new}
    decisive = bool(abs(obs) > 10 and stable)

    def verdict_for(vf, key):
        if vf[key]:
            return "VOID (observed LLR not separated from the null LLR distributions)"
        if decisive:
            return "M1 PREFERRED (decisive)" if obs > 0 else "M2 PREFERRED (decisive)"
        return "NOT-DISCRIMINATED"

    s3["VERDICT_matrix"] = {
        "KEEP_SIZE__OR": verdict_for(vf_keep, "VOID_reading_OR"),
        "KEEP_SIZE__UNION_SPAN": verdict_for(vf_keep, "VOID_reading_UNION_SPAN"),
        "NEW_SIZE__OR": verdict_for(vf_new, "VOID_reading_OR"),
        "NEW_SIZE__UNION_SPAN": verdict_for(vf_new, "VOID_reading_UNION_SPAN")}
    vset = sorted(set(s3["VERDICT_matrix"].values()))
    s3["VERDICT_all_readings_agree"] = bool(len(vset) == 1)
    s3["VERDICT"] = (vset[0] if len(vset) == 1 else
                     "READING-DEPENDENT: " + " | ".join(vset))
    s3["sign_stable_across_all_four_splits"] = stable
    s3["abs_LLR_gt_10"] = bool(abs(obs) > 10)

    # goodness of fit, randomised PIT
    gof = {"mc_replicates": PIT_MC_REPLICATES,
           "mc_replicate_count_provenance": (
               "EXECUTOR CHOICE: the contract fixes 10,000 resamples for S1a and "
               "10,000 replicates for the S4 bootstrap and NULL-C, but says only "
               "'with a Monte-Carlo null' here. The smallest attainable p-value is "
               "1/(reps+1) = %.6g, which is below the contract's 0.001 rejection "
               "threshold, so the test can fire." % (1.0 / (PIT_MC_REPLICATES + 1)))}
    for wt in WEIGHTINGS:
        ws = [float(weight_of(s, wt)) for s in samples]
        Wsum = sum(ws)
        wn = [w / Wsum for w in ws]
        rngN = random.Random(SEEDS["monte_carlo_ks"] + 7)
        null = mc_ks_uniform_null(wn, PIT_MC_REPLICATES, rngN)
        null.sort()
        gof[wt] = {}
        for model in ("M1", "M2"):
            rngP = random.Random(SEEDS["pit_randomization"] + (0 if model == "M1" else 1))
            u = s3_pit_values(samples, SM, model, rngP)
            D = weighted_ks_uniform(u, wn)
            k = sum(1 for d in null if d >= D)
            pv = (k + 1) / (len(null) + 1)
            gof[wt][model] = {"KS_D": D, "mc_exceed_count": k, "mc_p": pv,
                              "rejected_at_0_001": bool(pv < 0.001)}
        gof[wt]["null_D_median"] = percentile(null, 0.5)
        gof[wt]["null_D_99_9"] = percentile(null, 0.999)
        gof[wt]["both_models_rejected"] = bool(gof[wt]["M1"]["rejected_at_0_001"]
                                               and gof[wt]["M2"]["rejected_at_0_001"])
    s3["goodness_of_fit"] = gof

    # the SAME randomised-PIT goodness-of-fit run on NULL-A.  Falsification
    # criterion (b) requires the both-models rejection to SURVIVE NULL-A: if
    # random integral ternary forms of the same determinant are rejected by the
    # identical test with comparable magnitude, the rejection is a property of
    # "minima of ternary forms computed by this code", not of maximal orders.
    gof_a = {"mc_replicates": PIT_MC_REPLICATES}
    if null_a_samples:
        maxXa = max(s["X_p"] for s in null_a_samples)
        maxna = max(max(s["delta"] for s in null_a_samples), maxXa)
        SMa = SM if maxna <= maxn and maxXa <= maxX else SizeModels(maxna + 1)
        for wt in WEIGHTINGS:
            wsa = [float(weight_of(s, wt)) for s in null_a_samples]
            Wa = sum(wsa)
            wna = [w / Wa for w in wsa]
            rngNa = random.Random(SEEDS["monte_carlo_ks"] + 11)
            nulla = mc_ks_uniform_null(wna, PIT_MC_REPLICATES, rngNa)
            nulla.sort()
            gof_a[wt] = {}
            for model in ("M1", "M2"):
                rngPa = random.Random(SEEDS["pit_randomization"]
                                      + (100 if model == "M1" else 101))
                ua = s3_pit_values(null_a_samples, SMa, model, rngPa)
                Da = weighted_ks_uniform(ua, wna)
                ka = sum(1 for d in nulla if d >= Da)
                pva = (ka + 1) / (len(nulla) + 1)
                gof_a[wt][model] = {"KS_D": Da, "mc_exceed_count": ka, "mc_p": pva,
                                    "rejected_at_0_001": bool(pva < 0.001)}
            gof_a[wt]["both_models_rejected"] = bool(
                gof_a[wt]["M1"]["rejected_at_0_001"]
                and gof_a[wt]["M2"]["rejected_at_0_001"])
    s3["goodness_of_fit_NULL_A"] = gof_a
    arith_both = bool(gof["W-CURVE"]["both_models_rejected"])
    null_both = bool(gof_a.get("W-CURVE", {}).get("both_models_rejected", False))
    s3["both_models_rejected_arithmetic"] = arith_both
    s3["both_models_rejected_NULL_A"] = null_both
    s3["both_models_rejection_survives_NULL_A"] = bool(arith_both and not null_both)
    s3["NULL_A_KS_D_comparison"] = {
        "arithmetic_M1_D": gof["W-CURVE"]["M1"]["KS_D"],
        "arithmetic_M2_D": gof["W-CURVE"]["M2"]["KS_D"],
        "NULL_A_M1_D": gof_a.get("W-CURVE", {}).get("M1", {}).get("KS_D"),
        "NULL_A_M2_D": gof_a.get("W-CURVE", {}).get("M2", {}).get("KS_D"),
        "note": ("The void criterion is comparative: a rejection of the arithmetic "
                 "object that is reproduced at the same magnitude on NULL-A is an "
                 "artifact of the estimator or the construction, not a property of "
                 "maximal orders.")}
    # NULL-A run of the same LLR
    tota, _, _, za, zb = s3_llr(null_a_samples, "W-CURVE", SM)
    tota_v = llr_value(tota, za, zb)
    s3["null_A_LLR"] = {"LLR_total_float": tota_v,
                        "samples_with_zero_M1_density": za,
                        "preferred": "M1" if tota_v > 0 else ("M2" if tota_v < 0 else "tie"),
                        "n_samples": len(null_a_samples),
                        "same_model_as_arithmetic": bool((tota_v > 0) == (obs > 0))}
    # order statistic (descriptive only, mandatory label)
    ostat = []
    for r in complete:
        sub = [s for s in samples if s["p"] == r["p"]]
        best = min(sub, key=lambda s: s["P_plus"])
        y0 = best["P_plus"]
        N = len(sub)
        f1t = SM.table(best["delta"])
        f2t = SM.table(best["X_p"])
        F1 = sum(v for y, v in f1t.items() if y <= y0)
        F2 = sum(v for y, v in f2t.items() if y <= y0)
        ostat.append({"p": r["p"], "smoothest_delta": best["delta"], "P_plus": y0,
                      "n_samples_at_this_prime": N,
                      "P_at_least_one_under_M1": str(1 - (1 - F1) ** N),
                      "P_at_least_one_under_M2": str(1 - (1 - F2) ** N)})
    s3["order_statistic"] = {
        "MANDATORY_LABEL": ("non-discriminating (RT-H1(2)): consistent with any model "
                            "assigning this threshold a probability within a factor of "
                            "a few"),
        "rows": ostat}
    result["S3"] = s3

    # ---------------- S4 ----------------
    rngBoot = random.Random(SEEDS["bootstrap"])
    rngC = random.Random(SEEDS["null_c"])
    pools = [("ALL", samples)] + [(t, sub) for t, sub in sorted(by_tier(samples).items())]
    s4 = {"counting_convention": ("representations counted as UNORDERED +/- PAIRS "
                                  "(the ordered count is twice this and is recorded "
                                  "per class in the per-prime records)"),
          "prime_pool_reading": (
              "The contract says 'per prime-pool' without defining the pool. Both "
              "readings are computed and reported: the PRIMARY pool ALL is every "
              "completed prime pooled, and one pool per completed tier is reported "
              "beside it. No Executor choice therefore decides the verdict alone."),
          "pools": {}}
    for label, sub in pools:
        s4["pools"][label] = s4_pool(sub, rngBoot, rngC)
    s4["VERDICT"] = s4["pools"]["ALL"]["VERDICT"]
    s4["null_A"] = {}
    for B in B_GRID:
        cn = s4_counts(null_a_samples, B)
        ws = [weight_of(s, "W-CURVE") for s in null_a_samples]
        lam, hit = d2_from(cn, ws)
        ref = d2ref(lam)
        s4["null_A"][str(B)] = {
            "lambda_hat": float(lam), "P_count_ge_1": float(hit),
            "D2": float(hit / lam) if lam > 0 else None, "D2_ref": ref,
            "D2_star": float(hit / lam) / ref if (lam > 0 and ref) else None}
    result["S4"] = s4

    # ---------------- S1 ----------------
    s1 = {"sampler": ("non-backtracking random walk in the ell=2 ideal graph from the "
                      "verified O_0; the endpoint's class is identified by the route-Q "
                      "canonical form"),
          "scope_honesty": ("THE PAPER DOES NOT STATE ITS SAMPLER. A verdict here is a "
                            "verdict about THIS walk at THESE primes."),
          "class_visit_reading": ("S1c uses the ENDPOINT class of each of the N_walk "
                                  "draws; intermediate vertices are not counted. "
                                  "Recorded as an Executor reading."),
          "per_prime": {}, "per_length": {}}
    s1rows = s1rows_in if s1rows_in is not None else [_s1_worker(r) for r in complete]
    for row in s1rows:
        s1["per_prime"][str(row["p"])] = row
    Lmults = (1, 3, 10)
    for mult in Lmults:
        pa, pb, pc, pd, pref = [], [], [], [], []
        keys = []
        for row in s1rows:
            L = mult * row["L_base"]
            e = row["lengths"][str(L)]
            keys.append(row["p"])
            pa.append(e["S1a_mc_p"]); pb.append(e["S1b_mc_p"])
            pc.append(e["S1c_chi_p"]); pd.append(e["S1d_binomial_p"])
            pref.append(e["S1_null_object_reference_arm_mc_p"])
        ha, hb, hc = holm(pa), holm(pb), holm(pc)
        fa, sa = fisher_combined(pa)
        fb, sb = fisher_combined(pb)
        fr, sr = fisher_combined(pref)
        rej_a = bool(fa < 0.001)
        rej_b = bool(fb < 0.001)
        rej_c = any(v < 0.001 for v in hc)
        rej_d = any(v < 0.001 for v in pd)
        verdict = "SAMPLER-REJECTED" if (rej_a or rej_b or rej_c or rej_d) \
            else "SAMPLER-NOT-REJECTED"
        s1["per_length"][str(mult)] = {
            "L_rule": "%d * ceil(log2 p)" % mult,
            "primes": keys,
            "S1a_holm_rejections_at_0_05": sum(1 for v in ha if v < 0.05),
            "S1a_fisher_p": fa, "S1a_fisher_stat": sa, "S1a_rejects": rej_a,
            "S1b_holm_rejections_at_0_05": sum(1 for v in hb if v < 0.05),
            "S1b_fisher_p": fb, "S1b_fisher_stat": sb, "S1b_rejects": rej_b,
            "S1c_holm_rejections_at_0_001": sum(1 for v in hc if v < 0.001),
            "S1c_rejects": rej_c,
            "S1d_rejections_at_0_001": sum(1 for v in pd if v < 0.001),
            "S1d_rejects": rej_d,
            "S1_instrument_null_reference_arm_fisher_p": fr,
            "S1_instrument_voided": bool(fr < 0.001),
            "VERDICT": verdict,
            "S1a_S1b_agree": bool(rej_a == rej_b)}
    allrej = all(v["VERDICT"] == "SAMPLER-REJECTED" for v in s1["per_length"].values())
    s1["rejected_at_all_three_lengths"] = allrej
    s1["consequence"] = (
        "The optional sampled arm at p ~ 2^28 is STRICTLY CONDITIONAL on S1 and is "
        "additionally OPTIONAL under the contract. It was NOT run in this run; the "
        "reason and the resulting scope gap are stated in the execution report.")
    result["S1"] = s1

    # ---------------- secondary metrics and tail checks ----------------
    prime_rate_obs = Fraction(0); prime_rate_exp = Fraction(0); Wtot = Fraction(0)
    for s in samples:
        w = weight_of(s, "W-CURVE")
        Wtot += w
        if s["delta"] > 1 and len(factorize(s["delta"])) == 1 and \
                sum(factorize(s["delta"]).values()) == 1:
            prime_rate_obs += w
        n = s["delta"]
        npr = sum(1 for m in range(2, n + 1)
                  if len(factorize(m)) == 1 and sum(factorize(m).values()) == 1)
        prime_rate_exp += w * Fraction(npr, n)
    sizes = [Fraction(s["delta"], s["X_p"]) for s in samples]
    sizes_f = sorted(float(x) for x in sizes)
    u_vals = []
    for r in complete:
        for B in B_GRID:
            u_vals.append(math.log(r["p"] / 2.0) / (3.0 * math.log(B)))
    u_alt = []
    for r in complete:
        for B in B_GRID:
            if r["X_p"] > 1:
                u_alt.append(math.log(r["X_p"]) / math.log(B))
    result["secondary"] = {
        "prime_minimum_rate": {
            "observed_weighted_fraction": str(prime_rate_obs / Wtot),
            "size_matched_model_prediction": str(prime_rate_exp / Wtot),
            "signed_excess": float((prime_rate_obs - prime_rate_exp) / Wtot),
            "sign_note": ("a positive excess is the most attack-unfavourable "
                          "deviation available (producer's T3)")},
        "size_distribution_delta_over_Xp": {
            "mean": float(sum(sizes) / len(sizes)),
            "q05": sizes_f[int(0.05 * (len(sizes_f) - 1))],
            "median": sizes_f[int(0.5 * (len(sizes_f) - 1))],
            "q95": sizes_f[int(0.95 * (len(sizes_f) - 1))],
            "max": sizes_f[-1]},
        "u_range_reached_paper_definition": [min(u_vals), max(u_vals)],
        "u_range_reached_log_Xp_over_log_B": [min(u_alt), max(u_alt)] if u_alt else None,
        "W_CURVE_minus_W_TYPE": {
            "S2_p_obs": (s2["pooled"]["W-CURVE"]["p_obs_float"]
                         - s2["pooled"]["W-TYPE"]["p_obs_float"]),
            "S2_z2": (s2["pooled"]["W-CURVE"]["z_2_float"]
                      - s2["pooled"]["W-TYPE"]["z_2_float"]),
            "S3_LLR": (s3["llr"]["W-CURVE"]["LLR_total_float"]
                       - s3["llr"]["W-TYPE"]["LLR_total_float"])},
        "wall_clock_per_prime_seconds": {str(r["p"]): r["wall_clock_seconds"]
                                         for r in complete},
    }
    result["tail_checks"] = {
        "delta_1_spike_by_prime": [{"p": r["p"], "n_types": r["n_types"],
                                    "n_delta_1": r["IF_1"]["n_classes_delta_1"],
                                    "fraction": r["IF_1"]["n_classes_delta_1"] / r["n_types"]}
                                   for r in complete],
        "max_delta_vs_Xp": [{"p": r["p"], "max_delta_E": r["IF_5"]["max_delta_E"],
                             "X_p": r["X_p"]} for r in complete],
        "S2_stability_by_tier": {t: (v["sign"] if v else None)
                                 for t, v in s2["by_tier"]["W-CURVE"].items()},
        "S3_stability_by_tier": s3["stability"]["by_tier"],
        "S4_monotonicity": s4["pools"]["ALL"]["monotonicity_tail_check"],
    }
    # ---------------- section 7: PH1..PH5 recorded MET / NOT MET ----------------
    l10 = s1["per_length"].get("10", {})
    ph1_met = bool(l10.get("VERDICT") == "SAMPLER-NOT-REJECTED")
    ph2_met = bool(s2["VERDICT"] == "NOT REJECTED IN TESTED SCOPE")
    llr_w = s3["llr"]["W-CURVE"]["LLR_total_float"]
    ph3_met = bool(llr_w > 0)
    ph4_met = bool(s4["pools"]["ALL"]["CI_contains_1_in_all_three_regimes"])
    # PH5: the contract does not name the interval, so the comparison basis is an
    # Executor reading and is declared.  Basis used: the S2 naive Clopper-Pearson
    # 99% intervals for the even-fraction under W-CURVE and under W-TYPE.  If they
    # overlap the two measures agree "to within their own confidence intervals".
    cc = s2["naive_comparison_required_by_NC_3"]["W-CURVE"]["overall"]
    ct = s2["naive_comparison_required_by_NC_3"]["W-TYPE"]["overall"]
    ph5_overlap = bool(cc["clopper_pearson_99_low"] <= ct["clopper_pearson_99_high"]
                       and ct["clopper_pearson_99_low"] <= cc["clopper_pearson_99_high"])
    result["preregistered_predictions"] = {
        "frozen_reference": ("experiments/EXP-HEUR-d640d9/specification.yaml section 7, "
                             "frozen at commit dfe285d4 before any datum of this run "
                             "existed; not adjusted, and completed runs are not "
                             "re-scored against anything else."),
        "recording_rule": ("Each is recorded MET or NOT MET with its numbers. Success "
                           "of the experiment is a property of the protocol being "
                           "executed and reported, never of any prediction taking a "
                           "particular value (contract section 7 verdict_recording)."),
        "PH1": {"statement": "S1 returns SAMPLER-NOT-REJECTED at L = 10*ceil(log2 p).",
                "verdict": "MET" if ph1_met else "NOT MET",
                "numbers": l10},
        "PH2": {"statement": "S2 does not meet its three-part rejection condition.",
                "verdict": "MET" if ph2_met else "NOT MET",
                "numbers": {"C1": s2["C1"]["met"], "C2": s2["C2"]["met"],
                            "C3": s2["C3"]["met"], "S2_VERDICT": s2["VERDICT"],
                            "pooled_W_CURVE_z_2": pooled["z_2_float"]}},
        "PH3": {"statement": "S3 prefers M1 over M2.",
                "verdict": "MET" if ph3_met else "NOT MET",
                "numbers": {"LLR_W_CURVE": llr_w,
                            "preferred": s3["llr"]["W-CURVE"]["preferred"],
                            "S3_VERDICT": s3["VERDICT"]},
                "note": ("The sign of the LLR is recorded here even when the S3 "
                         "verdict is VOID or NOT-DISCRIMINATED; the verdict, not the "
                         "sign, is what the contract's decision rule governs.")},
        "PH4": {"statement": "S4's D2* is consistent with 1 in all reached rarity regimes.",
                "verdict": "MET" if ph4_met else "NOT MET",
                "numbers": {"CI_contains_1_all_three": ph4_met,
                            "CI_contains_1_reached_only":
                                s4["pools"]["ALL"]["CI_contains_1_in_all_REACHED_regimes"],
                            "n_regimes_reached": s4["pools"]["ALL"]["n_regimes_reached"],
                            "S4_VERDICT": s4["VERDICT"]}},
        "PH5": {"statement": ("W-CURVE and W-TYPE statistics agree to within their own "
                              "confidence intervals."),
                "verdict": "MET" if ph5_overlap else "NOT MET",
                "comparison_basis_is_an_EXECUTOR_READING": (
                    "The contract does not name which statistic or which interval. "
                    "Basis used: overlap of the S2 naive Clopper-Pearson 99% intervals "
                    "for the even-fraction under the two weightings. Every other "
                    "W-CURVE minus W-TYPE difference is reported in 'secondary' so any "
                    "other basis can be applied by a reviewer."),
                "numbers": {"W_CURVE_CI": [cc["clopper_pearson_99_low"],
                                           cc["clopper_pearson_99_high"]],
                            "W_TYPE_CI": [ct["clopper_pearson_99_low"],
                                          ct["clopper_pearson_99_high"]],
                            "intervals_overlap": ph5_overlap,
                            "S3_LLR_difference":
                                result["secondary"]["W_CURVE_minus_W_TYPE"]["S3_LLR"]}},
    }

    # ---------------- section 9: falsification criterion, evaluated ----------------
    fa = bool(s2["VERDICT"] == "REJECTED IN TESTED SCOPE")
    fb = bool(s3["both_models_rejection_survives_NULL_A"])
    s4all = s4["pools"]["ALL"]
    fc = bool(s4all["VERDICT"] == "REFUTED IN TESTED SCOPE"
              and not s4all["NULL_C_indicates_estimator_bias"])
    fs = bool(s1["rejected_at_all_three_lengths"])
    result["falsification_criterion"] = {
        "reference": "contract section 9 falsification_criterion",
        "(a)_S2_full_three_part_rejection_surviving_NULL_A": fa,
        "(b)_S3_rejects_BOTH_models_and_survives_NULL_A": fb,
        "(c)_S4_refuted_in_tested_scope_and_survives_NULL_C": fc,
        "random_integer_model_falsified_in_tested_scope": bool(fa or fb or fc),
        "walk_based_sampler_falsified_in_tested_scope": fs,
        "MANDATORY_SCOPE_STATEMENT": (
            "Any falsification recorded here is of the MODEL or of the SAMPLER, at toy "
            "primes, in the BODY of the distribution, at constant-factor level. It is "
            "never a falsification of Theorem 1.1, of the p^{1/3+o(1)} exponent, or of "
            "Heuristic 1 at its operating point. NOTHING IN THIS CONTRACT CAN CONFIRM "
            "HEURISTIC 1: a statistic that fails to reject is a statement about the "
            "body at toy primes and nothing else (SP-H, binding in both directions)."),
    }

    result["per_prime_records"] = complete
    result["null_A_samples"] = null_a_samples
    result["wall_clock_total_seconds"] = round(time.time() - t_start, 3)
    with open(outpath, "w") as fh:
        json.dump(result, fh, indent=1, default=str)
    print("[done] wrote %s in %.1fs" % (outpath, time.time() - t_start), flush=True)


if __name__ == "__main__":
    main()
