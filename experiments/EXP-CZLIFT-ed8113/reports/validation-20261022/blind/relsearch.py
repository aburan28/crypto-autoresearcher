"""Blind exact relation search for EXP-CZLIFT-ed8113 (validator TASK-20261022-67902e, phase 1).

Written from experiments/EXP-CZLIFT-ed8113/specification.yaml, trial-plan.json and
ledger/hypotheses/H-CZLIFT-cb95b8.yaml plus general mathematics only. No producer
implementation, raw result or decision was read before this file was sealed.

Arithmetic: general Weierstrass model y^2 + a1 xy + a3 y = x^3 + a2 x^2 + a4 x + a6
over Q with exact Fractions (Silverman, AEC III.2.3). The point at infinity is None.

Relation search: all m in [-B, B]^r, m != 0, with sum m_i P_i = O, found exactly by a
meet-in-the-middle over the multiples tables, and optionally re-checked by brute force.
"""
from __future__ import annotations

import itertools
import math
from fractions import Fraction as Fr

O = None  # point at infinity


class Curve:
    def __init__(self, a1=0, a2=0, a3=0, a4=0, a6=0):
        self.a1, self.a2, self.a3, self.a4, self.a6 = (Fr(v) for v in (a1, a2, a3, a4, a6))

    def ainvs(self):
        return (self.a1, self.a2, self.a3, self.a4, self.a6)

    def disc(self) -> Fr:
        a1, a2, a3, a4, a6 = self.ainvs()
        b2 = a1 * a1 + 4 * a2
        b4 = 2 * a4 + a1 * a3
        b6 = a3 * a3 + 4 * a6
        b8 = a1 * a1 * a6 + 4 * a2 * a6 - a1 * a3 * a4 + a2 * a3 * a3 - a4 * a4
        return -b2 * b2 * b8 - 8 * b4 ** 3 - 27 * b6 * b6 + 9 * b2 * b4 * b6

    def on_curve(self, P) -> bool:
        if P is O:
            return True
        x, y = P
        a1, a2, a3, a4, a6 = self.ainvs()
        return y * y + a1 * x * y + a3 * y == x ** 3 + a2 * x * x + a4 * x + a6

    def neg(self, P):
        if P is O:
            return O
        x, y = P
        return (x, -y - self.a1 * x - self.a3)

    def add(self, P, Q):
        if P is O:
            return Q
        if Q is O:
            return P
        a1, a2, a3, a4, a6 = self.ainvs()
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if y1 + y2 + a1 * x2 + a3 == 0:
                return O
            den = 2 * y1 + a1 * x1 + a3
            lam = (3 * x1 * x1 + 2 * a2 * x1 + a4 - a1 * y1) / den
            nu = (-x1 ** 3 + a4 * x1 + 2 * a6 - a3 * y1) / den
        else:
            lam = (y2 - y1) / (x2 - x1)
            nu = (y1 * x2 - y2 * x1) / (x2 - x1)
        x3 = lam * lam + a1 * lam - a2 - x1 - x2
        y3 = -(lam + a1) * x3 - nu - a3
        return (x3, y3)

    def mul(self, k: int, P):
        if k < 0:
            return self.mul(-k, self.neg(P))
        R, Q = O, P
        while k:
            if k & 1:
                R = self.add(R, Q)
            Q = self.add(Q, Q)
            k >>= 1
        return R


def multiples(E: Curve, P, B: int) -> dict:
    """{k: [k]P for k in -B..B}, built by repeated addition (independent of mul())."""
    tab = {0: O}
    cur = O
    for k in range(1, B + 1):
        cur = E.add(cur, P)
        tab[k] = cur
        tab[-k] = E.neg(cur)
    return tab


def canon(m):
    """Sign-normalise a coefficient vector: first nonzero entry positive."""
    for v in m:
        if v != 0:
            return tuple(m) if v > 0 else tuple(-u for u in m)
    return tuple(m)


def relation_search(E: Curve, pts, B: int = 6):
    """Exact search. Returns the sorted list of canonical relations m (first nonzero > 0)."""
    r = len(pts)
    for P in pts:
        if not E.on_curve(P):
            raise ValueError("point not on curve")
    tabs = [multiples(E, P, B) for P in pts]
    rng = range(-B, B + 1)
    if r == 1:
        found = {canon((m,)) for m in rng if m != 0 and tabs[0][m] is O}
        return sorted(found)
    # left: partial sums over the first r-1 points; right: [-m_r] P_r
    left = {}
    for ms in itertools.product(rng, repeat=r - 1):
        S = O
        for i, m in enumerate(ms):
            S = E.add(S, tabs[i][m])
        left.setdefault(S, []).append(ms)
    found = set()
    for mr in rng:
        target = tabs[r - 1][-mr]
        for ms in left.get(target, []):
            m = tuple(ms) + (mr,)
            if any(m):
                found.add(canon(m))
    return sorted(found)


def relation_search_bruteforce(E: Curve, pts, B: int = 6):
    """Brute-force cross-check: evaluate every sign-canonical m directly with mul()."""
    r = len(pts)
    found = set()
    for m in itertools.product(range(-B, B + 1), repeat=r):
        if not any(m) or canon(m) != m:
            continue
        S = O
        for mi, P in zip(m, pts):
            S = E.add(S, E.mul(mi, P))
        if S is O:
            found.add(m)
    return sorted(found)


def naive_height(P) -> float:
    if P is O:
        return 0.0
    x = P[0]
    return math.log(max(abs(x.numerator), abs(x.denominator), 1))


def sym(v: int, p: int) -> int:
    v %= p
    return v if v <= p // 2 else v - p


def fit_short(lifts):
    """r = 2: y^2 = x^3 + A x + B through two integer points with distinct x."""
    (x1, y1), (x2, y2) = lifts
    Y1, Y2 = Fr(y1 * y1 - x1 ** 3), Fr(y2 * y2 - x2 ** 3)
    A = (Y1 - Y2) / (x1 - x2)
    Bc = Y1 - A * x1
    return Curve(0, 0, 0, A, Bc)


def fit_x2(lifts):
    """r = 3: y^2 = x^3 + a2 x^2 + a4 x + a6 through three points with distinct x
    (Lagrange interpolation of the quadratic through (x_i, y_i^2 - x_i^3))."""
    xs = [Fr(x) for x, _ in lifts]
    Ys = [Fr(y * y - x ** 3) for x, y in lifts]
    c2 = c1 = c0 = Fr(0)
    for i in range(3):
        j, k = [t for t in range(3) if t != i]
        den = (xs[i] - xs[j]) * (xs[i] - xs[k])
        w = Ys[i] / den
        c2 += w
        c1 += -w * (xs[j] + xs[k])
        c0 += w * xs[j] * xs[k]
    return Curve(0, c2, 0, c1, c0)


def fit(lifts):
    return fit_short(lifts) if len(lifts) == 2 else fit_x2(lifts)


def frac_mod_p(q: Fr, p: int):
    """Reduce a rational with denominator prime to p; None if p divides the denominator."""
    if q.denominator % p == 0:
        return None
    return (q.numerator * pow(q.denominator, -1, p)) % p


def affine_points(a: int, b: int, p: int):
    sq = {}
    for t in range(p):
        sq.setdefault(t * t % p, []).append(t)
    pts = []
    for x in range(p):
        rhs = (x ** 3 + a * x + b) % p
        for y in sq.get(rhs, []):
            pts.append((x, y))
    return pts


def classify(rels, r):
    """Coarse type of the shortest relation found."""
    if not rels:
        return None
    best = min(rels, key=lambda m: (max(abs(v) for v in m), sum(abs(v) for v in m)))
    nz = [v for v in best if v != 0]
    if len(nz) == 1:
        return "torsion"
    if max(abs(v) for v in nz) == 1 and len(nz) == 2:
        return "coincident_or_opposite"
    if max(abs(v) for v in nz) == 1 and len(nz) == 3:
        return "collinear"
    return "other"


def fstr(q: Fr) -> str:
    return str(q)
