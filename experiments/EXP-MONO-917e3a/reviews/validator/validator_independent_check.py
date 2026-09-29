#!/usr/bin/env python3
"""Validator's OWN independent witness verification for TASK-20260904-cb0cb2 / J2.

Written from scratch WITHOUT reading
experiments/EXP-MONO-917e3a/implementation/witness_search.py.
Only stdlib. Affine Weierstrass arithmetic y^2 = x^3 + A x + B over F_p.
Point at infinity is None.
"""
from itertools import product, combinations


# ---------- (a) elliptic curve arithmetic over F_p, written from scratch ----------

class Curve:
    def __init__(self, p, A, B):
        self.p, self.A, self.B = p, A % p, B % p
        self.disc = (-16 * (4 * self.A ** 3 + 27 * self.B ** 2)) % p
        assert self.disc != 0, "singular curve"

    def on_curve(self, P):
        if P is None:
            return True
        x, y = P
        return (y * y - (x * x * x + self.A * x + self.B)) % self.p == 0

    def neg(self, P):
        if P is None:
            return None
        x, y = P
        return (x % self.p, (-y) % self.p)

    def add(self, P, Q):
        p = self.p
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 % p == x2 % p and (y1 + y2) % p == 0:
            return None                      # P = -Q  ->  O
        if x1 % p == x2 % p and y1 % p == y2 % p:
            if y1 % p == 0:                  # 2-torsion, doubling gives O
                return None
            lam = (3 * x1 * x1 + self.A) * pow(2 * y1, p - 2, p) % p
        else:
            lam = (y2 - y1) * pow((x2 - x1) % p, p - 2, p) % p
        x3 = (lam * lam - x1 - x2) % p
        y3 = (lam * (x1 - x3) - y1) % p
        return (x3, y3)

    def dbl(self, P):
        return self.add(P, P)

    def mul(self, k, P):
        if k < 0:
            return self.mul(-k, self.neg(P))
        R, Q = None, P
        while k:
            if k & 1:
                R = self.add(R, Q)
            Q = self.dbl(Q)
            k >>= 1
        return R

    def is_two_torsion(self, P):
        """P in E[2], i.e. 2P = O.  Includes P = O."""
        return self.dbl(P) is None

    def two_torsion_points(self):
        """All F_p-rational points of E[2] (O plus points with y=0)."""
        pts = [None]
        for x in range(self.p):
            if (x * x * x + self.A * x + self.B) % self.p == 0:
                pts.append((x, 0))
        return pts

    def points(self):
        pts = [None]
        sq = {}
        for y in range(self.p):
            sq.setdefault(y * y % self.p, []).append(y)
        for x in range(self.p):
            rhs = (x * x * x + self.A * x + self.B) % self.p
            for y in sq.get(rhs, []):
                pts.append((x, y))
        return pts

    def order_of(self, P):
        if P is None:
            return 1
        n, Q = 1, P
        while Q is not None:
            Q = self.add(Q, P)
            n += 1
        return n


# ---------- (b) the 2^{m-2} sign-class x-coordinates and pairwise distinctness ----------

def sign_class_sums(E, pts):
    """pts = [P_1,...,P_{m-1}].  Return list of (eps, sum) over the 2^{m-2}
    sign vectors with eps_1 fixed to +1 (a section of {+-1}^{m-1}/<diag>)."""
    n = len(pts)
    out = []
    for tail in product([1, -1], repeat=n - 1):
        eps = (1,) + tail
        S = None
        for e, P in zip(eps, pts):
            S = E.add(S, P if e == 1 else E.neg(P))
        out.append((eps, S))
    return out


def x_coords_distinct(E, pts):
    """Compute the sign-class x-coordinates and check pairwise distinctness.
    Returns (ok, records, collisions, infinities)."""
    recs = sign_class_sums(E, pts)
    infinities = [eps for eps, S in recs if S is None]
    xs = [(eps, (None if S is None else S[0])) for eps, S in recs]
    collisions = []
    for (e1, x1), (e2, x2) in combinations(xs, 2):
        if x1 == x2:
            collisions.append((e1, e2, x1))
    ok = (not collisions) and (not infinities)
    return ok, xs, collisions, infinities


# ---------- (c) INDEPENDENT cross-check via my own J1 torsion criterion ----------

def torsion_criterion_violations(E, pts):
    """My J1 criterion: the V-action is free iff for every nonempty PROPER
    subset S of {1..m-1} and every sign pattern on S, sum_{i in S} eps_i P_i
    is NOT in E[2].  Return the list of violations."""
    n = len(pts)
    bad = []
    for r in range(1, n):                       # nonempty proper subsets
        for S in combinations(range(n), r):
            for signs in product([1, -1], repeat=r):
                if signs[0] == -1:              # global sign on S is irrelevant
                    continue
                Q = None
                for i, e in zip(S, signs):
                    Q = E.add(Q, pts[i] if e == 1 else E.neg(pts[i]))
                if E.is_two_torsion(Q):
                    bad.append((S, signs, Q))
    return bad


def report(name, p, A, B, pts):
    E = Curve(p, A, B)
    print("=" * 78)
    print(f"{name}:  p={p}  A={A}  B={B}  m-1={len(pts)}  m={len(pts)+1}")
    for i, P in enumerate(pts, 1):
        assert E.on_curve(P), f"P_{i}={P} NOT on curve"
        print(f"  P_{i} = {P}   on_curve=True   ord={E.order_of(P)}   in E[2]={E.is_two_torsion(P)}")
    N = len(E.points())
    print(f"  #E(F_p) = {N};  E[2](F_p) = {E.two_torsion_points()}")
    ok, xs, coll, inf = x_coords_distinct(E, pts)
    print(f"  2^(m-2) = {len(xs)} sign classes (eps_1 = +1):")
    for eps, x in xs:
        s = "".join("+" if e == 1 else "-" for e in eps)
        print(f"    eps={s}  ->  x = {x if x is not None else 'INFINITY'}")
    print(f"  sorted distinct x-values: {sorted(x for _, x in xs if x is not None)}")
    print(f"  any signed sum = O ? {inf if inf else 'no'}")
    print(f"  collisions: {coll if coll else 'NONE'}")
    print(f"  >>> PAIRWISE DISTINCT: {ok}")
    bad = torsion_criterion_violations(E, pts)
    print(f"  cross-check via J1 torsion criterion -> violations: {bad if bad else 'NONE'}")
    print(f"  >>> two independent routes agree: {ok == (not bad and not inf)}")
    return ok, xs, coll


if __name__ == "__main__":
    report("m=4 witness #1", 101, 2, 3, [(3, 6), (5, 21), (9, 12)])
    report("m=4 witness #2", 211, 5, 7, [(2, 5), (3, 7), (8, 83)])
    report("m=5 witness", 101, 2, 3, [(17, 1), (18, 35), (20, 8), (21, 32)])
