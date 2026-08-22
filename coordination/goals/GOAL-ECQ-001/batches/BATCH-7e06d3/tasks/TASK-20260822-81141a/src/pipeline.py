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


def _is_pol(g):
    return str(pari.type(g)) == "t_POL"


def c4c6(a2, a4, a6):
    b2, b4, b6 = 4 * a2, 2 * a4, 4 * a6
    c4 = b2 * b2 - 24 * b4
    c6 = -b2 ** 3 + 36 * b2 * b4 - 216 * b6
    return b2, c4, c6


def reduce_family(a2, a4, a6):
    """Reduce the family y^2=x^3+a2 x^2+a4 x+a6 over Q(t) to the c4/c6 model
    y^2 = x^3 - 27 c4' x - 54 c6', removing the largest Lam(t) in Q(t) with
    Lam^4 | c4 and Lam^6 | c6.  Returns (c4', c6', b2, Lam).
    The accompanying isomorphism is  X = (36 x + 3 b2)/Lam^2,  Y = 108 y/Lam^3.
    """
    b2, c4, c6 = c4c6(a2, a4, a6)
    lam = pari("1")
    if c4 != 0 and c6 != 0:
        g = pari.gcd(c4, c6)
        if _is_pol(g) and int(g.poldegree(T)) > 0:
            fa = pari.factor(g)
            for i in range(fa.nrows()):
                f = fa[0][i]
                if not _is_pol(f):
                    continue
                k = min(_pol_val(c4, f) // 4, _pol_val(c6, f) // 6)
                if k >= 1:
                    lam = lam * f ** k
                    c4 = c4 / f ** (4 * k)
                    c6 = c6 / f ** (6 * k)
    # rational content
    def cont(a):
        if a == 0:
            return None
        return Fraction(str(pari.content(a)))
    mu = Fraction(1)
    while True:
        cs = [cont(c4), cont(c6)]
        moved = False
        for p in SMALL_PRIMES:
            ks = []
            for c, e in zip(cs, (4, 6)):
                if c is None:
                    ks.append(10 ** 9)
                else:
                    ks.append((_vp_int(c.numerator, p) - _vp_int(c.denominator, p)) // e)
            k = min(ks)
            if k >= 1:
                mu *= p ** k
                c4 = c4 / pari(str(p ** (4 * k)))
                c6 = c6 / pari(str(p ** (6 * k)))
                moved = True
                break
            ks2 = []
            for c, e in zip(cs, (4, 6)):
                if c is None:
                    ks2.append(10 ** 9)
                else:
                    ks2.append(_vp_int(c.denominator, p) // e)
            k2 = min(ks2)
            if k2 >= 1:
                mu /= p ** k2
                c4 = c4 * pari(str(p ** (4 * k2)))
                c6 = c6 * pari(str(p ** (6 * k2)))
                moved = True
                break
        if not moved:
            break
    lam = lam * pari("%d/%d" % (mu.numerator, mu.denominator))
    return c4, c6, b2, lam


def _vp_int(n, p):
    n = int(n)
    if n == 0:
        return 10 ** 9
    k = 0
    while n % p == 0:
        n //= p
        k += 1
    return k


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
    if str(pari.type(g)) == "t_RFRAC":
        n, d = g.numerator(), g.denominator()
    else:
        n, d = g, pari("1")
    return _poly_coeffs(n), _poly_coeffs(d)


def _poly_coeffs(p):
    if not _is_pol(p):
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


# --------------------------------------------------------------------------
# STAGE 3: certification harness over Q
#   (1) exact on-curve check in our own rational arithmetic,
#   (2) Neron-Tate height matrix at two precisions,
#   (3) greedy maximal independent subset via Gram determinants.
# --------------------------------------------------------------------------

def on_curve_exact(ainv, P):
    """a1,a2,a3,a4,a6 and P=(x,y) as Fractions.  Exact, our own arithmetic."""
    a1, a2, a3, a4, a6 = [Fraction(a) for a in ainv]
    x, y = Fraction(P[0]), Fraction(P[1])
    return y * y + a1 * x * y + a3 * y - (x ** 3 + a2 * x * x + a4 * x + a6) == 0


def _pt_str(P):
    return "[%s,%s]" % (frac_str(P[0]), frac_str(P[1]))


def height_matrix_pari(ainv, pts, precision_digits):
    pari.set_real_precision(precision_digits)
    E = pari.ellinit("[%s]" % ",".join(frac_str(a) for a in ainv))
    V = pari("[%s]" % ",".join(_pt_str(P) for P in pts))
    return E.ellheightmatrix(V)


def _to_float_matrix(H, n):
    return [[float(H[i][j]) for j in range(n)] for i in range(n)]


def _det(M):
    import numpy as np
    if not M:
        return 1.0
    return float(np.linalg.det(np.array(M, dtype=float)))


def independent_subset(G, tol=1e-6):
    """Greedy maximal independent subset of a Gram matrix.

    A candidate is accepted only if it increases the Gram determinant by a
    factor > tol.  det(G_new)/det(G_old) is the squared distance from the new
    vector to the span of the accepted ones, so the criterion is
    dimension-independent: it does NOT get harder to pass as the subset grows.
    (A raw relative-determinant test does, and silently under-counts the
    rank-30 fixture -- that failure mode is why this form is used.)
    """
    n = len(G)
    chosen = []
    prev = 1.0
    for i in range(n):
        cand = chosen + [i]
        sub = [[G[a][b] for b in cand] for a in cand]
        d = _det(sub)
        if d > 0 and d / prev > tol:
            chosen = cand
            prev = d
    return chosen


def certify_rank(ainv, pts, precisions=(38, 77), tol=1e-6, eig_tol=1e-6):
    """Certified rank LOWER BOUND from the exhibited points only.

    Every point is first re-verified on the curve in exact rational
    arithmetic by our own code (on_curve_exact); a single failure voids the
    whole certificate.  Independence is then decided from the Neron-Tate
    height pairing at two working precisions, and the two must agree.
    """
    exact_ok = [on_curve_exact(ainv, P) for P in pts]
    if not all(exact_ok):
        return {"error": "point not on curve in exact arithmetic",
                "n_points": len(pts), "on_curve_all": False,
                "bad_indices": [i for i, v in enumerate(exact_ok) if not v],
                "rank": None}
    res = {"n_points": len(pts), "on_curve_all": True, "by_precision": {},
           "tol": tol, "eig_tol": eig_tol}
    ranks = []
    for prec in precisions:
        H = height_matrix_pari(ainv, pts, prec)
        G = _to_float_matrix(H, len(pts))
        chosen = independent_subset(G, tol)
        if chosen:
            body = ";".join(",".join(str(H[a][b]) for b in chosen) for a in chosen)
            sub = pari("Mat(%s)" % body) if len(chosen) == 1 else pari("[%s]" % body)
            det = str(pari.matdet(sub))
            ev = pari.qfjacobi(sub)[0]
            eigs = sorted(float(ev[i]) for i in range(len(chosen)))
            least = eigs[0]
        else:
            det, least = "1", None
        res["by_precision"][prec] = {
            "rank": len(chosen), "indices": chosen,
            "regulator_det": det, "least_eigenvalue": least,
            "diag_heights": [G[i][i] for i in range(len(pts))],
        }
        ranks.append(len(chosen) if (least is None or least > eig_tol) else -1)
    res["ranks_by_precision"] = ranks
    res["precision_agreement"] = len(set(ranks)) == 1 and ranks[0] >= 0
    res["rank"] = ranks[0] if res["precision_agreement"] else None
    return res


# --------------------------------------------------------------------------
# family assembly
# --------------------------------------------------------------------------

class Family(object):
    pass


def build_family(points, origin=None):
    """points: 8 rational points in P^2 (lists of 3 ints/Fractions, z != 0).
    Returns a Family with the pencil, the 9th base point and the reduced
    Weierstrass family over Q(t) together with the 8 sections."""
    basis = cubics_through(points)
    if len(basis) != 2:
        raise ValueError("cubics through the 8 points do not form a pencil (dim=%d)" % len(basis))
    C1 = primitive_form(vec_to_form(basis[0]))
    C2 = primitive_form(vec_to_form(basis[1]))
    P9 = primitive_point(ninth_base_point(C1, C2, points))
    base9 = [[Fraction(c) for c in p] for p in points] + [P9]
    mons = set(C1) | set(C2)
    Ct = {e: pari(frac_str(C1.get(e, 0))) + T * pari(frac_str(C2.get(e, 0))) for e in mons}

    best = None
    idxs = range(9) if origin is None else [origin]
    for oi in idxs:
        try:
            P0 = [pari(frac_str(c)) for c in base9[oi]]
            wd = weierstrass_data(Ct, P0)
            A0, A1, A2, A3 = wd["A"]
            a2, a4, a6 = A2, A1 * A3, A0 * A3 * A3
            c4, c6, b2, lam = reduce_family(a2, a4, a6)
            size = max(len(str(x.numerator)) + len(str(x.denominator))
                       for x in _poly_coeffs(c4) + _poly_coeffs(c6))
            if best is None or size < best[0]:
                best = (size, oi, wd, c4, c6, b2, lam)
        except Exception:
            continue
    if best is None:
        raise ValueError("no usable origin among the 9 base points")
    size, oi, wd, c4, c6, b2, lam = best

    secs = []
    for j in range(9):
        if j == oi:
            continue
        Q = [pari(frac_str(c)) for c in base9[j]]
        m = map_point(wd, Q)
        if m is None:
            raise ValueError("base point %d falls on the frame's line at infinity" % j)
        x, y = m
        X = (36 * x + 3 * b2) / lam ** 2
        Y = 216 * y / lam ** 3
        if (Y * Y - (X ** 3 - 27 * c4 * X - 54 * c6)) != 0:
            raise ValueError("section %d fails the exact Q(t) curve equation" % j)
        secs.append((X, Y))

    F = Family()
    F.points = [[Fraction(c) for c in p] for p in points]
    F.C1, F.C2, F.P9 = C1, C2, P9
    F.base9 = base9
    F.origin_index = oi
    F.c4, F.c6 = c4, c6
    F.lam, F.b2 = lam, b2
    F.disc = (c4 ** 3 - c6 ** 2) / 1728
    F.sections = secs
    F.c4_co = _poly_coeffs(c4)
    F.c6_co = _poly_coeffs(c6)
    F.sec_rf = [(gen_to_ratfunc(X), gen_to_ratfunc(Y)) for X, Y in secs]
    F.model_size = size
    F.deg = (int(c4.poldegree(T)), int(c6.poldegree(T)), int(F.disc.poldegree(T)))
    return F


def reduce_short(A, B):
    """[0,0,0,A,B] with A,B rational -> integral, small-prime-reduced model.
    Returns (A',B',mu) with A'=A mu^4, B'=B mu^6 and (x,y)->(mu^2 x, mu^3 y)."""
    A, B = Fraction(A), Fraction(B)
    d = _lcm(A.denominator, B.denominator)
    mu = Fraction(d)
    Ai = int(A * d ** 4)
    Bi = int(B * d ** 6)
    for p in SMALL_PRIMES:
        while True:
            k = min(_vp(Ai, p) // 4, _vp(Bi, p) // 6)
            if k < 1:
                break
            Ai //= p ** 4
            Bi //= p ** 6
            mu = mu / p
    return Ai, Bi, mu


def specialise(F, t0):
    """Specialise the family at t=t0 (Fraction).  Returns (ainv, points) with
    ainv=[0,0,0,A,B] integral and the 8 sections as exact rational points, or
    None if the fibre is singular."""
    c4v = eval_coeffs(F.c4_co, t0)
    c6v = eval_coeffs(F.c6_co, t0)
    if c4v ** 3 - c6v ** 2 == 0:
        return None
    A, B, mu = reduce_short(-27 * c4v, -54 * c6v)
    pts = []
    for rx, ry in F.sec_rf:
        X = eval_ratfunc(rx, t0)
        Y = eval_ratfunc(ry, t0)
        if X is None or Y is None:
            return None
        pts.append((X * mu ** 2, Y * mu ** 3))
    return [0, 0, 0, A, B], pts


# --------------------------------------------------------------------------
# STAGE 2: Mestre-Nagao statistic (ORDERING ONLY -- never a certified rank)
# --------------------------------------------------------------------------

def primes_upto(N):
    sieve = [True] * (N + 1)
    sieve[0:2] = [False, False]
    for i in range(2, int(N ** 0.5) + 1):
        if sieve[i]:
            for j in range(i * i, N + 1, i):
                sieve[j] = False
    return [i for i, v in enumerate(sieve) if v]


def mn_score(ainv, plist, logs):
    """S(N) = sum_{p<=N} ((p+1-a_p)/p) log p, via PARI ellap."""
    E = pari.ellinit("[0,0,0,%d,%d]" % (ainv[3], ainv[4]))
    s = 0.0
    for p, lg in zip(plist, logs):
        ap = int(E.ellap(p))
        s += ((p + 1 - ap) / p) * lg
    return s


def extra_points(ainv, alarm_seconds=25):
    """Search for points beyond the sections.  ellrank's r_low/r_high are NOT
    used as a rank claim -- only the POINTS it exhibits are kept, and they are
    re-verified in exact arithmetic downstream."""
    s = "[0,0,0,%d,%d]" % (ainv[3], ainv[4])
    try:
        r = pari("iferr(alarm(%d,ellrank(ellinit(%s))),E,[-1,-1,0,[]])" % (alarm_seconds, s))
    except BaseException:
        # PARI alarm/interrupt surfaces as a Python exception under cypari;
        # this is an infrastructure outcome (budget guard), never a rank claim.
        try:
            pari("alarm(0)")
        except BaseException:
            pass
        return [], "timeout"
    try:
        rl, rh = int(r[0]), int(r[1])
    except Exception:
        return [], None
    pts = []
    V = r[3]
    for i in range(len(V)):
        P = V[i]
        pts.append((Fraction(str(P[0])), Fraction(str(P[1]))))
    return pts, (rl, rh)


# --------------------------------------------------------------------------
# drivers
# --------------------------------------------------------------------------

def search_configuration(seed, tries):
    """Deterministic seeded search for an 8-point configuration in general
    position whose reduced Q(t) model has the smallest coefficients.
    The objective is model height only -- NOT rank, and not any property of
    the specialisations, so it cannot tune the answer toward a target rank."""
    rng = random.Random(seed)
    cands = []
    audit = {"tried": 0, "general_position": 0, "built": 0}
    for _ in range(tries):
        audit["tried"] += 1
        R = rng.choice([2, 3, 4])
        if 2 * R + 1 < 8:
            continue
        xs = rng.sample(range(-R, R + 1), 8)
        pts = [[x, rng.randint(-R, R), 1] for x in xs]
        if len(set(map(tuple, pts))) < 8:
            continue
        rep = general_position_report(pts)
        if not rep["general_position"]:
            continue
        audit["general_position"] += 1
        try:
            fam = build_family(pts)
        except Exception:
            continue
        audit["built"] += 1
        cands.append((fam.model_size, pts))
    if not cands:
        raise RuntimeError("no usable configuration found")
    cands.sort(key=lambda z: (z[0], z[1]))
    return cands[0][1], audit, sorted(c[0] for c in cands)


def json_default(o):
    if isinstance(o, Fraction):
        return frac_str(o)
    raise TypeError(repr(o))


def cmd_selftest(args):
    out = {"harness_self_tests": {}}
    d = json.load(open(args.record_curve))
    ai = d["a_invariants"]
    pts = [(Fraction(a), Fraction(b)) for a, b in d["points"]]
    t0 = time.time()
    r = certify_rank(ai, pts)
    out["harness_self_tests"]["a_record_rank30"] = {
        "source": args.record_curve, "n_points_supplied": len(pts),
        "expected_rank": 30, "returned_rank": r["rank"],
        "pass": r["rank"] == 30,
        "regulator_det": {str(k): v["regulator_det"] for k, v in r["by_precision"].items()},
        "least_eigenvalue": {str(k): v["least_eigenvalue"] for k, v in r["by_precision"].items()},
        "precision_agreement": r["precision_agreement"],
        "seconds": time.time() - t0,
    }
    t0 = time.time()
    E = pari.ellinit("[0,0,1,-1,0]")
    V = E.ellratpoints(50)
    p37 = []
    for i in range(len(V)):
        p37.append((Fraction(str(V[i][0])), Fraction(str(V[i][1]))))
    r2 = certify_rank([0, 0, 1, -1, 0], p37)
    out["harness_self_tests"]["b_conductor37_rank1"] = {
        "a_invariants": [0, 0, 1, -1, 0], "n_points_supplied": len(p37),
        "expected_rank": 1, "returned_rank": r2["rank"], "pass": r2["rank"] == 1,
        "regulator_det": {str(k): v["regulator_det"] for k, v in r2["by_precision"].items()},
        "precision_agreement": r2["precision_agreement"],
        "seconds": time.time() - t0,
    }
    json.dump(out, open(args.out, "w"), indent=2, default=json_default)
    print(json.dumps(out, indent=2, default=json_default))
    return out


def cmd_family(args):
    t_start = time.time()
    if args.points:
        pts = json.loads(args.points)
        audit, sizes = {"tried": 0, "supplied": True}, []
    else:
        pts, audit, sizes = search_configuration(args.seed, args.tries)
    F = build_family(pts)
    gp = general_position_report(pts)
    tlist = [Fraction(s) for s in args.tvals.split(",")]
    regs = []
    for t0 in tlist:
        sp = specialise(F, t0)
        if sp is None:
            regs.append({"t": frac_str(t0), "status": "singular_fibre"})
            continue
        ai, pp = sp
        c = certify_rank(ai, pp)
        regs.append({
            "t": frac_str(t0),
            "a_invariants": [str(a) for a in ai],
            "section_points": [[frac_str(x), frac_str(y)] for x, y in pp],
            "rank_of_the_8_sections": c["rank"],
            "regulator_det_8x8": {str(k): v["regulator_det"] for k, v in c["by_precision"].items()},
            "least_eigenvalue": {str(k): v["least_eigenvalue"] for k, v in c["by_precision"].items()},
            "nonsingular": c["rank"] == 8,
            "independent_indices": c["by_precision"][38]["indices"],
        })
    out = {
        "construction": "pencil of plane cubics through 8 rational points in general position",
        "configuration_search": {"seed": args.seed, "tries": args.tries,
                                 "audit": audit, "model_size_distribution_head": sizes[:20]},
        "eight_points_P2Q": [[frac_str(c) for c in p] for p in F.points],
        "general_position_audit": gp,
        "pencil_basis_C1": {str(list(k)): frac_str(v) for k, v in sorted(F.C1.items())},
        "pencil_basis_C2": {str(list(k)): frac_str(v) for k, v in sorted(F.C2.items())},
        "pencil": "C_t = C1 + t*C2",
        "ninth_base_point": [frac_str(c) for c in F.P9],
        "ninth_base_point_method": "resultant elimination of y from C1,C2 with the eight known x-coordinates divided out; verified by exact substitution into both C1 and C2",
        "zero_section_index_in_base9": F.origin_index,
        "weierstrass_family_over_Qt": {
            "model": "y^2 = x^3 - 27*c4(t)*x - 54*c6(t)",
            "c4": str(F.c4), "c6": str(F.c6),
            "discriminant": str(F.disc),
            "degrees": {"c4": F.deg[0], "c6": F.deg[1], "discriminant": F.deg[2]},
            "rational_elliptic_surface_check": {
                "deg_c4_le_4": F.deg[0] <= 4, "deg_c6_le_6": F.deg[1] <= 6,
                "deg_disc_eq_12": F.deg[2] == 12},
        },
        "eight_sections_over_Qt": [{"X": str(X), "Y": str(Y)} for X, Y in F.sections],
        "sections_verified_symbolically_over_Qt": True,
        "regulators_at_specialisations": regs,
        "wall_clock_seconds": time.time() - t_start,
    }
    json.dump(out, open(args.out, "w"), indent=2, default=json_default)
    print(json.dumps({k: out[k] for k in ("eight_points_P2Q", "ninth_base_point",
                                          "weierstrass_family_over_Qt")}, indent=2))
    for r in regs:
        print("t=%s rank_of_8_sections=%s det=%s" % (r["t"], r.get("rank_of_the_8_sections"),
                                                     str(r.get("regulator_det_8x8", {}).get("38"))[:16]))
    return out


def enumerate_domain(pmax, qmax):
    out = []
    for q in range(1, qmax + 1):
        for p in range(-pmax, pmax + 1):
            if p == 0:
                continue
            if math.gcd(abs(p), q) != 1:
                continue
            out.append(Fraction(p, q))
    return out


def cmd_sieve(args):
    t_start = time.time()
    fam_json = json.load(open(args.family))
    pts = [[Fraction(c) for c in p] for p in fam_json["eight_points_P2Q"]]
    F = build_family([[int(Fraction(c)) for c in p] for p in pts])
    plist = primes_upto(args.mn_N)
    logs = [math.log(p) for p in plist]
    D1 = enumerate_domain(args.pmax, args.qmax)
    scored = []
    singular = 0
    for t0 in D1:
        sp = specialise(F, t0)
        if sp is None:
            singular += 1
            continue
        s = mn_score(sp[0], plist, logs)
        scored.append((s, t0))
    scored.sort(key=lambda z: -z[0])
    D2 = [t for t in enumerate_domain(args.pmax2, args.qmax2)]
    D2set = set(D2)
    scored2 = [(s, t) for s, t in scored if t in D2set]
    rng = random.Random(args.seed)
    rand2 = rng.sample([t for _, t in scored2], min(args.K, len(scored2)))
    out = {
        "statistic": "Mestre-Nagao S(N) = sum_{p<=N} ((p+1-a_p)/p) log p, ellap",
        "statistic_role": "ORDERING ONLY; never contributes to a certified rank",
        "mn_N": args.mn_N, "n_primes": len(plist),
        "tier1_domain": {"t = p/q": "gcd(p,q)=1", "pmax": args.pmax, "qmax": args.qmax,
                         "enumerated": len(D1), "singular_fibres_skipped": singular,
                         "scored_volume": len(scored)},
        "tier2_domain": {"pmax": args.pmax2, "qmax": args.qmax2, "scored_volume": len(scored2)},
        "seconds_per_specialisation": (time.time() - t_start) / max(1, len(scored)),
        "tier1_top": [[frac_str(t), s] for s, t in scored[:args.K_global]],
        "tier2_mn_arm": [[frac_str(t), s] for s, t in scored2[:args.K]],
        "tier2_random_control_arm": [[frac_str(t), None] for t in rand2],
        "control_seed": args.seed,
        "overlap_mn_vs_random": len(set(t for _, t in scored2[:args.K]) & set(rand2)),
        "score_summary": {
            "max": scored[0][0] if scored else None,
            "median": scored[len(scored) // 2][0] if scored else None,
            "min": scored[-1][0] if scored else None,
        },
        "wall_clock_seconds": time.time() - t_start,
    }
    json.dump(out, open(args.out, "w"), indent=2, default=json_default)
    print(json.dumps({k: out[k] for k in ("tier1_domain", "tier2_domain",
                                          "seconds_per_specialisation", "score_summary")},
                     indent=2))
    return out


def certify_one(F, t0, alarm_seconds):
    sp = specialise(F, t0)
    if sp is None:
        return {"t": frac_str(t0), "status": "singular_fibre"}
    ai, sec = sp
    t1 = time.time()
    ex, rr = extra_points(ai, alarm_seconds)
    descent_seconds = time.time() - t1
    allpts = list(sec) + list(ex)
    c = certify_rank(ai, allpts)
    rec = {
        "t": frac_str(t0),
        "a_invariants": [str(a) for a in ai],
        "n_sections": len(sec), "n_descent_points": len(ex),
        "descent_status": ("timeout" if rr == "timeout" else
                           ("ok" if rr else "error")),
        "ellrank_bounds_NOT_A_CLAIM": (list(rr) if isinstance(rr, tuple) else rr),
        "descent_seconds": descent_seconds,
        "certified_rank": c.get("rank"),
        "on_curve_all_exact": c.get("on_curve_all"),
        "precision_agreement": c.get("precision_agreement"),
        "regulator_det": {str(k): v["regulator_det"] for k, v in c.get("by_precision", {}).items()},
        "least_eigenvalue": {str(k): v["least_eigenvalue"] for k, v in c.get("by_precision", {}).items()},
        "independent_point_indices": (c["by_precision"][38]["indices"]
                                      if "by_precision" in c else None),
        "exhibited_points": [[frac_str(x), frac_str(y)] for x, y in allpts],
    }
    if "error" in c:
        rec["certificate_error"] = c["error"]
    return rec


def cmd_certify(args):
    t_start = time.time()
    fam_json = json.load(open(args.family))
    F = build_family([[int(Fraction(c)) for c in p] for p in fam_json["eight_points_P2Q"]])
    sv = json.load(open(args.sieve))
    arms = {
        "tier2_mn_arm": [Fraction(x[0]) for x in sv["tier2_mn_arm"]],
        "tier2_random_control_arm": [Fraction(x[0]) for x in sv["tier2_random_control_arm"]],
        "tier1_global_top": [Fraction(x[0]) for x in sv["tier1_top"][:args.K_global]],
    }
    alarms = {"tier2_mn_arm": args.alarm, "tier2_random_control_arm": args.alarm,
              "tier1_global_top": args.alarm_global}
    results = {}
    for name, ts in arms.items():
        recs = []
        for t0 in ts:
            if time.time() - t_start > args.budget:
                recs.append({"t": frac_str(t0), "status": "not_run_budget_exhausted"})
                continue
            recs.append(certify_one(F, t0, alarms[name]))
            print("[%s] t=%s rank=%s (%s) %.1fs" % (
                name, frac_str(t0), recs[-1].get("certified_rank"),
                recs[-1].get("descent_status"), time.time() - t_start), flush=True)
        results[name] = recs

    def hit(recs):
        done = [r for r in recs if r.get("certified_rank") is not None]
        h = {"attempted": len(recs), "certified": len(done),
             "descent_timeouts": sum(1 for r in recs if r.get("descent_status") == "timeout"),
             "not_run": sum(1 for r in recs if r.get("status") == "not_run_budget_exhausted")}
        for thr in (9, 10, 11, 12):
            h["rank_ge_%d" % thr] = sum(1 for r in done if r["certified_rank"] >= thr)
        h["max_certified_rank"] = max([r["certified_rank"] for r in done], default=None)
        h["rank_histogram"] = {}
        for r in done:
            k = str(r["certified_rank"])
            h["rank_histogram"][k] = h["rank_histogram"].get(k, 0) + 1
        return h

    allrecs = [r for recs in results.values() for r in recs
               if r.get("certified_rank") is not None]
    allrecs.sort(key=lambda r: (-r["certified_rank"], len(r["a_invariants"][4])))
    out = {
        "certification_rule": "every reported rank is a LOWER BOUND from exhibited points, each re-verified on that exact curve in exact rational arithmetic by our own code, with the r x r Neron-Tate regulator reported at two precisions",
        "silverman_note": "Silverman specialisation motivated the search only; every curve below is recertified with its own points and its own regulator",
        "arms": {k: hit(v) for k, v in results.items()},
        "curves_best_first": allrecs,
        "per_arm_records": results,
        "wall_clock_seconds": time.time() - t_start,
    }
    json.dump(out, open(args.out, "w"), indent=2, default=json_default)
    print(json.dumps(out["arms"], indent=2))
    return out


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("selftest")
    s.add_argument("--record-curve", required=True)
    s.add_argument("--out", required=True)
    s.set_defaults(func=cmd_selftest)

    s = sub.add_parser("family")
    s.add_argument("--seed", type=int, default=81141)
    s.add_argument("--tries", type=int, default=4000)
    s.add_argument("--points", default=None)
    s.add_argument("--tvals", default="1,2,-1,1/2,5,-7,7/5,11/3")
    s.add_argument("--out", required=True)
    s.set_defaults(func=cmd_family)

    s = sub.add_parser("sieve")
    s.add_argument("--family", required=True)
    s.add_argument("--mn-N", type=int, default=1000)
    s.add_argument("--pmax", type=int, default=2000)
    s.add_argument("--qmax", type=int, default=40)
    s.add_argument("--pmax2", type=int, default=150)
    s.add_argument("--qmax2", type=int, default=8)
    s.add_argument("--K", type=int, default=60)
    s.add_argument("--K-global", type=int, default=20)
    s.add_argument("--seed", type=int, default=81141)
    s.add_argument("--out", required=True)
    s.set_defaults(func=cmd_sieve)

    s = sub.add_parser("certify")
    s.add_argument("--family", required=True)
    s.add_argument("--sieve", required=True)
    s.add_argument("--alarm", type=int, default=8)
    s.add_argument("--alarm-global", type=int, default=20)
    s.add_argument("--K-global", type=int, default=20)
    s.add_argument("--budget", type=float, default=1500.0)
    s.add_argument("--out", required=True)
    s.set_defaults(func=cmd_certify)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
