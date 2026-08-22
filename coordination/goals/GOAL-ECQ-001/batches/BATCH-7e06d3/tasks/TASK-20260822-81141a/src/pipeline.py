#!/usr/bin/env python3
"""
TASK-20260822-81141a  /  GOAL-ECQ-001  /  BATCH-7e06d3
Rank-over-Q pipeline: pencil of plane cubics through 8 rational points
-> rational elliptic surface over Q(t) with 8 sections
-> Mestre-Nagao sieve of specialisations (with random-sample control)
-> certification over Q by exhibited points + Neron-Tate regulator.

All exact arithmetic is done with fractions.Fraction (Python) or PARI
rational-function arithmetic in the variable t.  NO floating point is used
anywhere in the construction; floating point appears only in canonical
Neron-Tate height computations (PARI ellheightmatrix), where it is
unavoidable, and there every rank decision is taken at two precisions.

Stage numbering follows the task card.
"""

import argparse
import itertools
import json
import math
import os
import random
import sys
import time
from fractions import Fraction

from cypari import pari

pari.allocatemem(1 << 30, silent=True)

# --------------------------------------------------------------------------
# generic exact linear algebra over Q (Fractions), written here rather than
# taken from a library, per the task card.
# --------------------------------------------------------------------------

MONOMIALS = [(i, j, 3 - i - j) for i in range(4) for j in range(4 - i)]
assert len(MONOMIALS) == 10


def rref(mat):
    """Exact reduced row echelon form.  mat: list of lists of Fraction."""
    m = [row[:] for row in mat]
    rows, cols = len(m), len(m[0])
    pivots = []
    r = 0
    for c in range(cols):
        piv = None
        for rr in range(r, rows):
            if m[rr][c] != 0:
                piv = rr
                break
        if piv is None:
            continue
        m[r], m[piv] = m[piv], m[r]
        inv = Fraction(1, 1) / m[r][c]
        m[r] = [x * inv for x in m[r]]
        for rr in range(rows):
            if rr != r and m[rr][c] != 0:
                f = m[rr][c]
                m[rr] = [a - f * b for a, b in zip(m[rr], m[r])]
        pivots.append(c)
        r += 1
        if r == rows:
            break
    return m, pivots


def nullspace(mat, ncols):
    """Exact basis of the kernel of mat (list of rows)."""
    if not mat:
        return [[Fraction(int(i == j)) for j in range(ncols)] for i in range(ncols)]
    m, pivots = rref(mat)
    free = [c for c in range(ncols) if c not in pivots]
    basis = []
    for fc in free:
        v = [Fraction(0)] * ncols
        v[fc] = Fraction(1)
        for i, pc in enumerate(pivots):
            v[pc] = -m[i][fc]
        basis.append(v)
    return basis


def mat3_det(M):
    return (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1])
            - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
            + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))


def mat3_inv(M):
    d = mat3_det(M)
    if d == 0:
        raise ValueError("singular frame matrix")
    cof = [[(M[(i + 1) % 3][(j + 1) % 3] * M[(i + 2) % 3][(j + 2) % 3]
             - M[(i + 1) % 3][(j + 2) % 3] * M[(i + 2) % 3][(j + 1) % 3])
            for j in range(3)] for i in range(3)]
    # inverse = adj/det, adj = cof^T
    return [[cof[j][i] / d for j in range(3)] for i in range(3)], d


def mat3_apply(M, v):
    return [M[i][0] * v[0] + M[i][1] * v[1] + M[i][2] * v[2] for i in range(3)]


# --------------------------------------------------------------------------
# trivariate cubic forms as dict {(i,j,k): coeff}
# --------------------------------------------------------------------------

def poly_mul(p, q):
    out = {}
    for e1, c1 in p.items():
        for e2, c2 in q.items():
            e = (e1[0] + e2[0], e1[1] + e2[1], e1[2] + e2[2])
            out[e] = out.get(e, 0) + c1 * c2
    return out


def eval_form(C, P):
    """Evaluate a form (dict) at a projective point P=[x,y,z]."""
    tot = 0
    for (i, j, k), c in C.items():
        tot = tot + c * (P[0] ** i) * (P[1] ** j) * (P[2] ** k)
    return tot


def substitute_linear(C, M):
    """G(u,v,w) = C(M.(u,v,w)).  M is 3x3, entries in the coefficient ring."""
    L = []
    for i in range(3):
        L.append({(1, 0, 0): M[i][0], (0, 1, 0): M[i][1], (0, 0, 1): M[i][2]})
    out = {}
    for (a, b, c), coeff in C.items():
        term = {(0, 0, 0): coeff}
        for _ in range(a):
            term = poly_mul(term, L[0])
        for _ in range(b):
            term = poly_mul(term, L[1])
        for _ in range(c):
            term = poly_mul(term, L[2])
        for e, cc in term.items():
            out[e] = out.get(e, 0) + cc
    return out


def grad_form(C, P):
    """Gradient of the cubic form C at P, exact."""
    g = []
    for var in range(3):
        s = 0
        for e, c in C.items():
            if e[var] == 0:
                continue
            ee = list(e)
            ee[var] -= 1
            s = s + c * e[var] * (P[0] ** ee[0]) * (P[1] ** ee[1]) * (P[2] ** ee[2])
        g.append(s)
    return g


# --------------------------------------------------------------------------
# STAGE 1a: the pencil through 8 points, general-position audit, 9th point
# --------------------------------------------------------------------------

def cubics_through(points):
    rows = []
    for P in points:
        rows.append([Fraction(P[0]) ** i * Fraction(P[1]) ** j * Fraction(P[2]) ** k
                     for (i, j, k) in MONOMIALS])
    basis = nullspace(rows, 10)
    return basis


def vec_to_form(v):
    return {MONOMIALS[i]: v[i] for i in range(10) if v[i] != 0}


def general_position_report(points):
    """No 3 collinear, no 6 on a conic, all distinct.  Exact."""
    P = [[Fraction(c) for c in p] for p in points]
    n = len(P)
    collinear = []
    for a, b, c in itertools.combinations(range(n), 3):
        if mat3_det([P[a], P[b], P[c]]) == 0:
            collinear.append([a, b, c])
    on_conic = []
    conic_mons = [(2, 0, 0), (1, 1, 0), (1, 0, 1), (0, 2, 0), (0, 1, 1), (0, 0, 2)]
    for six in itertools.combinations(range(n), 6):
        rows = [[p[0] ** i * p[1] ** j * p[2] ** k for (i, j, k) in conic_mons]
                for p in (P[s] for s in six)]
        if len(nullspace(rows, 6)) > 0:
            on_conic.append(list(six))
    distinct = True
    for a, b in itertools.combinations(range(n), 2):
        cr = [P[a][1] * P[b][2] - P[a][2] * P[b][1],
              P[a][2] * P[b][0] - P[a][0] * P[b][2],
              P[a][0] * P[b][1] - P[a][1] * P[b][0]]
        if all(x == 0 for x in cr):
            distinct = False
    return {"three_collinear": collinear, "six_on_a_conic": on_conic,
            "all_distinct": distinct,
            "general_position": (not collinear) and (not on_conic) and distinct}


def form_to_pari_xy(C, xname="x", yname="y"):
    """Dehomogenised (z=1) polynomial string in x,y."""
    parts = []
    for (i, j, k), c in sorted(C.items()):
        if c == 0:
            continue
        parts.append("(%s)*%s^%d*%s^%d" % (frac_str(c), xname, i, yname, j))
    return "+".join(parts) if parts else "0"


def frac_str(c):
    c = Fraction(c)
    return str(c.numerator) if c.denominator == 1 else "%d/%d" % (c.numerator, c.denominator)


def ninth_base_point(C1, C2, known):
    """Compute the 9th base point of the pencil <C1,C2> exactly, by
    eliminating y from the two dehomogenised cubics and dividing out the
    eight known x-coordinates.  Verified by exact substitution."""
    # require the 8 known points affine (z=1) with distinct x-coordinates
    xs = []
    for P in known:
        assert Fraction(P[2]) != 0
        xs.append(Fraction(P[0]) / Fraction(P[2]))
    assert len(set(xs)) == 8, "known points must have distinct x-coordinates"
    f1 = pari(form_to_pari_xy(C1))
    f2 = pari(form_to_pari_xy(C2))
    R = pari.polresultant(f1, f2, pari("y"))
    R = R / pari.polcoeff(R, R.poldegree(pari("x")), pari("x"))  # monic
    known_prod = pari("1")
    for xv in xs:
        known_prod = known_prod * pari("x - (%s)" % frac_str(xv))
    q, r = R.divrem(known_prod)
    if r != 0:
        raise RuntimeError("resultant is not divisible by the known x-factors")
    if q.poldegree(pari("x")) != 1:
        raise RuntimeError("residual factor has degree %s, not 1" % q.poldegree(pari("x")))
    # q = x - x9  (monic)
    x9 = -pari.polcoeff(q, 0, pari("x"))
    x9 = Fraction(str(x9))
    g1 = pari(form_to_pari_xy(C1).replace("x", "(%s)" % frac_str(x9)))
    g2 = pari(form_to_pari_xy(C2).replace("x", "(%s)" % frac_str(x9)))
    g = pari.gcd(g1, g2)
    if g.poldegree(pari("y")) != 1:
        raise RuntimeError("gcd in y has degree %s, not 1" % g.poldegree(pari("y")))
    y9 = -pari.polcoeff(g, 0, pari("y")) / pari.polcoeff(g, 1, pari("y"))
    y9 = Fraction(str(y9))
    P9 = [x9, y9, Fraction(1)]
    assert eval_form(C1, P9) == 0 and eval_form(C2, P9) == 0, "9th point fails exact check"
    return P9


# --------------------------------------------------------------------------
# STAGE 1b: cubic (with a rational point) -> Weierstrass, with explicit maps
#
# Frame: P0 -> (0:1:0), tangent at P0 -> {w=0}, third intersection of that
# tangent with the cubic -> (1:0:0).  Then
#    G = a v^2 w + v(b u^2 + c u w + d w^2) + (f u^2 w + g u w^2 + h w^3)
# (the u^3, v^3 and u v^2 coefficients vanish identically -- checked).
# Solving G(u,v,1)=0 as a quadratic in u and setting
#    Z = 2(b v + f) u + (c v + g)
# gives  Z^2 = A3 v^3 + A2 v^2 + A1 v + A0  with
#    A3 = -4ab, A2 = c^2-4bd-4af, A1 = 2cg-4bh-4df, A0 = g^2-4fh,
# and finally X = A3 v, Y = A3 Z gives
#    Y^2 = X^3 + A2 X^2 + A1 A3 X + A0 A3^2 .
# --------------------------------------------------------------------------

def weierstrass_data(C, P0, e3_candidates=None):
    """Return dict with A0..A3, the frame matrix M and its inverse."""
    g = grad_form(C, P0)
    if all(x == 0 for x in g):
        raise ValueError("P0 is a singular point of the cubic")
    # Euler: g . P0 = 3*C(P0) = 0, so P0 lies on the tangent line ker(g).
    # Pick a second spanning vector R of ker(g), independent of P0.
    R = None
    for v in kernel_of_linear_form(g):
        cr = [P0[1] * v[2] - P0[2] * v[1], P0[2] * v[0] - P0[0] * v[2],
              P0[0] * v[1] - P0[1] * v[0]]
        if any(x != 0 for x in cr):
            R = v
            break
    if R is None:
        raise ValueError("could not build the tangent line frame")

    # third intersection: C(P0 + tau R) = tau^2 (c2 + c3 tau)
    c0, c1, c2, c3 = cubic_line_coeffs(C, P0, R)
    if c0 != 0 or c1 != 0:
        raise ValueError("tangent-line expansion failed: c0=%s c1=%s" % (c0, c1))
    if c3 == 0:
        raise ValueError("tangent line is a component / inflectional degeneracy (c3=0)")
    # T = c3 * P0 - c2 * R   (projective, integral in the coefficient ring)
    T = [c3 * P0[i] - c2 * R[i] for i in range(3)]

    e3s = e3_candidates or ([0, 0, 1], [0, 1, 0], [1, 0, 0], [1, 1, 1], [1, 2, 3], [3, -1, 2])
    M = None
    for E3 in e3s:
        cand = [[T[0], P0[0], E3[0]], [T[1], P0[1], E3[1]], [T[2], P0[2], E3[2]]]
        if mat3_det(cand) != 0:
            M = cand
            break
    if M is None:
        raise ValueError("could not complete the frame")

    G = substitute_linear(C, M)

    def cf(e):
        return G.get(e, 0)

    checks = {"u3": cf((3, 0, 0)), "v3": cf((0, 3, 0)), "uv2": cf((1, 2, 0))}
    a = cf((0, 2, 1))
    b = cf((2, 1, 0))
    c = cf((1, 1, 1))
    d = cf((0, 1, 2))
    f = cf((2, 0, 1))
    gg = cf((1, 0, 2))
    h = cf((0, 0, 3))
    A3 = -4 * a * b
    A2 = c * c - 4 * b * d - 4 * a * f
    A1 = 2 * c * gg - 4 * b * h - 4 * d * f
    A0 = gg * gg - 4 * f * h
    Minv, det = mat3_inv(M)
    return {"M": M, "Minv": Minv, "abcdfgh": (a, b, c, d, f, gg, h),
            "A": (A0, A1, A2, A3), "vanishing_checks": checks, "G": G}


def kernel_of_linear_form(g):
    """Two independent vectors spanning ker(g) for a nonzero linear form g."""
    idx = None
    for i in range(3):
        if g[i] != 0:
            idx = i
            break
    others = [i for i in range(3) if i != idx]
    out = []
    for o in others:
        v = [0, 0, 0]
        v[o] = g[idx]
        v[idx] = -g[o]
        out.append(v)
    return out


def cubic_line_coeffs(C, P0, R):
    """C(P0 + tau R) = c0 + c1 tau + c2 tau^2 + c3 tau^3; returns all four."""
    # expand exactly by treating tau symbolically with a tiny dense poly
    coeffs = [0, 0, 0, 0]
    for (i, j, k), cc in C.items():
        # (P0[0]+tau R[0])^i * ... : multiply small polynomials in tau
        poly = [cc, 0, 0, 0]
        for var, ex in ((0, i), (1, j), (2, k)):
            for _ in range(ex):
                new = [0, 0, 0, 0]
                for dg in range(4):
                    if poly[dg] == 0:
                        continue
                    if dg <= 3:
                        new[dg] = new[dg] + poly[dg] * P0[var]
                    if dg + 1 <= 3:
                        new[dg + 1] = new[dg + 1] + poly[dg] * R[var]
                poly = new
        for dg in range(4):
            coeffs[dg] = coeffs[dg] + poly[dg]
    return coeffs[0], coeffs[1], coeffs[2], coeffs[3]


def map_point(wd, P):
    """Map a projective point P on the cubic to (X,Y) on Y^2=X^3+A2X^2+A1A3X+A0A3^2."""
    a, b, c, d, f, gg, h = wd["abcdfgh"]
    A0, A1, A2, A3 = wd["A"]
    q = mat3_apply(wd["Minv"], P)
    u, v, w = q
    if w == 0:
        return None  # maps to the point at infinity / the frame's line at infinity
    ua = u / w
    va = v / w
    X = A3 * va
    Y = A3 * (2 * (b * va + f) * ua + (c * va + gg))
    return (X, Y)


# --------------------------------------------------------------------------
# normalisation helpers (exact)
# --------------------------------------------------------------------------

def _lcm(a, b):
    return a * b // math.gcd(a, b)


def primitive_form(C):
    """Scale a Q-form to primitive integral coefficients (content 1)."""
    vals = [Fraction(c) for c in C.values() if c != 0]
    if not vals:
        return dict(C)
    L = 1
    for v in vals:
        L = _lcm(L, v.denominator)
    nums = [int(v * L) for v in vals]
    g = 0
    for n in nums:
        g = math.gcd(g, abs(n))
    s = Fraction(L, g)
    out = {e: Fraction(c) * s for e, c in C.items() if c != 0}
    # sign convention: first nonzero coefficient positive
    first = out[sorted(out)[0]]
    if first < 0:
        out = {e: -c for e, c in out.items()}
    return out


def primitive_point(P):
    vals = [Fraction(c) for c in P]
    L = 1
    for v in vals:
        L = _lcm(L, v.denominator)
    nums = [int(v * L) for v in vals]
    g = 0
    for n in nums:
        g = math.gcd(g, abs(n))
    if g == 0:
        return [Fraction(0)] * 3
    out = [Fraction(n, g) for n in nums]
    for c in out:
        if c != 0:
            if c < 0:
                out = [-c2 for c2 in out]
            break
    return out


SMALL_PRIMES = [p for p in range(2, 3000) if all(p % q for q in range(2, int(p ** .5) + 1))]


def _vp(n, p):
    if n == 0:
        return 10 ** 9
    k = 0
    while n % p == 0:
        n //= p
        k += 1
    return k


def reduce_weierstrass(a2, a4, a6):
    """Return integral, partially minimised [0,a2,0,a4,a6] plus the scaling
    factor lam with (X,Y) -> (lam^2 X, lam^3 Y).  Exact throughout."""
    a2, a4, a6 = Fraction(a2), Fraction(a4), Fraction(a6)
    d = 1
    for v, e in ((a2, 2), (a4, 4), (a6, 6)):
        den = v.denominator
        # need d^e * v integral for the given e; d = lcm of denominators works
        d = _lcm(d, den)
    lam = Fraction(d)
    A2 = int(a2 * d ** 2)
    A4 = int(a4 * d ** 4)
    A6 = int(a6 * d ** 6)
    for p in SMALL_PRIMES:
        while True:
            k = min(_vp(A2, p) // 2, _vp(A4, p) // 4, _vp(A6, p) // 6)
            if k < 1:
                break
            k = 1
            A2 //= p ** 2
            A4 //= p ** 4
            A6 //= p ** 6
            lam = lam / p
    return A2, A4, A6, lam


# --------------------------------------------------------------------------
# Q(t) layer: reduction of the Weierstrass family and fast specialisation
# --------------------------------------------------------------------------

T = pari("t")


def _pol_val(a, f):
    """valuation of the polynomial a at the irreducible polynomial f"""
    if a == 0:
        return 10 ** 9
    k = 0
    while True:
        q, r = a.divrem(f)
        if r != 0:
            return k
        a = q
        k += 1


def reduce_family(a2, a4, a6):
    """Remove the largest lam(t) in Q[t] and rational constant with
    lam^2 | a2, lam^4 | a4, lam^6 | a6.  Returns (a2,a4,a6,lam)."""
    lam = pari("1")
    prod = a2 * a4 * a6
    if prod != 0:
        fa = pari.factor(prod)
        for i in range(fa.nrows()):
            f = fa[0][i]
            if pari.type(f) != "t_POL":
                continue
            k = min(_pol_val(a2, f) // 2, _pol_val(a4, f) // 4, _pol_val(a6, f) // 6)
            if k >= 1:
                lam = lam * f ** k
                a2 = a2 / f ** (2 * k)
                a4 = a4 / f ** (4 * k)
                a6 = a6 / f ** (6 * k)
    # rational content
    def content_frac(a):
        if a == 0:
            return None
        return Fraction(str(pari.content(a)))
    cs = [content_frac(a) for a in (a2, a4, a6)]
    # numerator side: remove m with m^2|c2, m^4|c4, m^6|c6 ; denominator side too
    num = 1
    for p in SMALL_PRIMES:
        while True:
            ks = []
            for c, e in zip(cs, (2, 4, 6)):
                if c is None:
                    ks.append(10 ** 9)
                    continue
                v = _vp(c.numerator, p) - _vp_den(c.denominator, p)
                ks.append(v // e)
            k = min(ks)
            if k < 1:
                break
            num *= p
            cs = [None if c is None else c / Fraction(p) ** e for c, e in zip(cs, (2, 4, 6))]
    den = 1
    for p in SMALL_PRIMES:
        while True:
            ks = []
            for c, e in zip(cs, (2, 4, 6)):
                if c is None:
                    ks.append(10 ** 9)
                    continue
                ks.append(_vp(c.denominator, p) // e)
            k = min(ks)
            if k < 1:
                break
            den *= p
            cs = [None if c is None else c * Fraction(p) ** e for c, e in zip(cs, (2, 4, 6))]
    mu = Fraction(num, den)
    mus = pari("%d/%d" % (mu.numerator, mu.denominator))
    a2 = a2 / mus ** 2
    a4 = a4 / mus ** 4
    a6 = a6 / mus ** 6
    lam = lam * mus
    return a2, a4, a6, lam


def _vp_den(n, p):
    if n == 0:
        return 0
    k = 0
    while n % p == 0:
        n //= p
        k += 1
    return k


def gen_to_ratfunc(g):
    """PARI element of Q(t) -> (num_coeffs, den_coeffs) as Fraction lists,
    ascending powers of t."""
    ty = pari.type(g)
    if ty == "t_RFRAC":
        n, d = g.numerator(), g.denominator()
    else:
        n, d = g, pari("1")
    return _poly_coeffs(n), _poly_coeffs(d)


def _poly_coeffs(p):
    if pari.type(p) != "t_POL":
        return [Fraction(str(p))]
    deg = int(p.poldegree(T))
    v = pari.Vec(p)  # descending
    return [Fraction(str(v[deg - i])) for i in range(deg + 1)]


def eval_coeffs(coeffs, t0):
    acc = Fraction(0)
    for c in reversed(coeffs):
        acc = acc * t0 + c
    return acc


def eval_ratfunc(rf, t0):
    n = eval_coeffs(rf[0], t0)
    d = eval_coeffs(rf[1], t0)
    if d == 0:
        return None
    return n / d
