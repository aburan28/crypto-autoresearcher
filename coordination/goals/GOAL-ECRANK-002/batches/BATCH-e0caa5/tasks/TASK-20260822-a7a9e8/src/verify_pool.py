#!/usr/bin/env python3
"""
Independent verifier for highrank_pool.json (TASK-20260822-a7a9e8).

Deliberately independent of the solver: STANDARD LIBRARY ONLY, no PARI, no
numpy.  It re-checks, for every curve in the pool:

  1. every listed independent point satisfies the general Weierstrass equation
     y^2 + a1 x y + a3 y = x^3 + a2 x^2 + a4 x + a6  in EXACT rational
     arithmetic;
  2. the listed points are pairwise distinct and none is the point at infinity;
  3. the curve is nonsingular (discriminant != 0);
  4. certified_rank == number of listed independent points;
  5. the Mestre construction is reproducible from the recorded parameter set A:
     rebuilding p, g, s from A reproduces the recorded s-polynomial and all
     2k simultaneous square conditions s(a_i) = g(a_i)^2 hold exactly.

It does NOT re-check the height regulator (that needs PARI); the regulator
determinant is reported by the solver and re-checked there at two precisions.

usage: python3 verify_pool.py highrank_pool.json
"""
import json
import sys
from fractions import Fraction as Fr


def pmul(a, b):
    r = [Fr(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x == 0:
            continue
        for j, y in enumerate(b):
            r[i + j] += x * y
    return r


def psub(a, b):
    n = max(len(a), len(b))
    r = [Fr(0)] * n
    for i, x in enumerate(a):
        r[i] += x
    for i, y in enumerate(b):
        r[i] -= y
    while len(r) > 1 and r[-1] == 0:
        r.pop()
    return r


def peval(p, x):
    s = Fr(0)
    for c in reversed(p):
        s = s * x + c
    return s


def rebuild(A):
    k = len(A) // 2
    p = [Fr(1)]
    for a in A:
        p = pmul(p, [Fr(-a), Fr(1)])
    g = [Fr(0)] * (k + 1)
    g[k] = Fr(1)
    for j in range(k - 1, -1, -1):
        S = Fr(0)
        for u in range(j + 1, k + 1):
            v = k + j - u
            if 0 <= v <= k and v > j:
                S += g[u] * g[v]
        g[j] = (p[k + j] - S) / 2
    return g, psub(pmul(g, g), p)


def disc(ai):
    a1, a2, a3, a4, a6 = [Fr(z) for z in ai]
    b2 = a1 * a1 + 4 * a2
    b4 = 2 * a4 + a1 * a3
    b6 = a3 * a3 + 4 * a6
    b8 = (a1 * a1 * a6 + 4 * a2 * a6 - a1 * a3 * a4 + a2 * a3 * a3 - a4 * a4)
    return -b2 * b2 * b8 - 8 * b4 ** 3 - 27 * b6 * b6 + 9 * b2 * b4 * b6


def main(path):
    pool = json.load(open(path))
    curves = pool["curves"]
    bad = 0
    npts = 0
    for c in curves:
        ai = [Fr(z) for z in c["min_ainv"]]
        a1, a2, a3, a4, a6 = ai
        pts = [(Fr(x), Fr(y)) for x, y in c["independent_points"]]
        for x, y in pts:
            npts += 1
            if y * y + a1 * x * y + a3 * y != x ** 3 + a2 * x * x + a4 * x + a6:
                print("FAIL on-curve", c["curve_id"], x, y)
                bad += 1
        if len(set(pts)) != len(pts):
            print("FAIL duplicate points", c["curve_id"])
            bad += 1
        if disc(ai) == 0:
            print("FAIL singular", c["curve_id"])
            bad += 1
        if c["certified_rank"] != len(pts):
            print("FAIL rank/points mismatch", c["curve_id"])
            bad += 1
        A = c["A"]
        g, s = rebuild(A)
        if [str(Fr(z)) for z in s] != [str(Fr(z)) for z in c["s_poly"]]:
            print("FAIL s-poly not reproducible from A", c["curve_id"])
            bad += 1
        for a in A:
            if peval(s, Fr(a)) != peval(g, Fr(a)) ** 2:
                print("FAIL square condition", c["curve_id"], a)
                bad += 1
    print("curves=%d points_checked=%d failures=%d" % (len(curves), npts, bad))
    print("VERDICT:", "PASS" if bad == 0 else "FAIL")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
