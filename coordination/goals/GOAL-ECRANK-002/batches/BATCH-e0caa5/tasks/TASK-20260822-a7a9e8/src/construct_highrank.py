#!/usr/bin/env python3
"""
Mestre-style construction of high-rank elliptic curves over Q.
TASK-20260822-a7a9e8 / BATCH-e0caa5 / GOAL-ECRANK-002.

CONSTRUCTION (exactly as run; re-runnable from this file alone)
===============================================================

Let A = {a_1, ..., a_{2k}} be 2k distinct rationals (here: distinct integers).

  p(x) = prod_{i=1}^{2k} (x - a_i)              monic, degree 2k
  g(x) = the unique monic degree-k polynomial with deg(p - g^2) <= k-1
         (the polynomial part of the Laurent expansion of sqrt(p) at infinity;
          computed here by exact coefficient matching over Q)
  s(x) = g(x)^2 - p(x)                           degree <= k-1

Because p(a_i) = 0 we get, for EVERY i,

  s(a_i) = g(a_i)^2 ,

i.e. 2k simultaneous square conditions hold BY CONSTRUCTION.  So the curve
y^2 = s(x) carries the 2k rational points (a_i, g(a_i)).

Two instantiations are used:

  M8  : 2k = 8,  k = 4  ->  deg s = 3  ->  y^2 = s(x) is already a cubic
        (Weierstrass) model with 8 exhibited rational points.
        Function-theoretic ceiling: g - y has a pole of order 8 at infinity and
        vanishes at all 8 points, so their sum is O.  One relation => at most 7
        independent.

  M10 : 2k = 10, k = 5  ->  deg s = 4  ->  y^2 = s(x) is a QUARTIC model with
        10 exhibited rational points.  It is reduced to a cubic below.
        Same argument (g - v vanishes at all 10 points, pole order 5 at each of
        the two points at infinity) gives one relation => at most 9 independent.

QUARTIC -> CUBIC REDUCTION (M10), derived here rather than quoted
-----------------------------------------------------------------
Pick a base index i0, put e = g(a_{i0}) != 0, and shift u = t + a_{i0} so that

  v^2 = s~(t) = a t^4 + b t^3 + c t^2 + d t + e^2 .

Write the "osculating parabola" v = e + (d/2e) t + m t^2 with m a parameter.
Then s~(t) - (e + (d/2e)t + m t^2)^2 = t^2 * Q_m(t) with

  Q_m(t) = (a - m^2) t^2 + (b - (d/e) m) t + (c - d^2/(4e^2) - 2 e m).

A rational point with t != 0 exists iff disc Q_m is a square, i.e. iff

  w^2 = D(m) := (b - (d/e)m)^2 - 4 (a - m^2)(c - d^2/(4e^2) - 2 e m),

a CUBIC in m with leading coefficient -8e.  The birational map is

  m = (v - e - (d/2e) t) / t^2 ,     w = 2(a - m^2) t + (b - (d/e) m).

The 9 construction points with t != 0 are pushed through this map and each
image is re-checked to satisfy w^2 = D(m) in EXACT rational arithmetic.
(The point with t = 0 is the base point and maps to infinity: it contributes
nothing, which is the same relation counted above.)

Finally w^2 = A3 m^3 + A2 m^2 + A1 m + A0 is put in Weierstrass form by
X = A3 m, Y = A3 w:

  Y^2 = X^3 + A2 X^2 + A1 A3 X + A0 A3^2 ,

denominators are cleared by (X,Y) -> (u^2 X, u^3 Y), and PARI's
ellminimalmodel + ellchangepoint move curve and points to a minimal model.

AUGMENTATION (optional extra points)
------------------------------------
Beyond the prescribed a_i, extra rational points are searched on the quartic
model by scanning u = n/dd with |n| <= nmax, 1 <= dd <= dmax, gcd(n,dd)=1 and
testing whether s(n/dd) is a rational square (exact integer perfect-square
test).  Each hit is mapped through the same reduction and appended.

CERTIFICATION RULES OBEYED
--------------------------
* Every reported rank is a LOWER BOUND equal to the number of exhibited
  independent points.  No analytic rank, no ellrank r_high, no point-free
  bound is ever counted.
* Every exhibited point is verified on its reported (minimal) model in exact
  rational arithmetic by verify_on_curve() below, using fractions only --
  PARI's word is never taken for it.
* Independence is certified by the Neron-Tate height pairing matrix
  (PARI ellheightmatrix) and its determinant, computed at two different real
  precisions; a singular matrix means the points are NOT independent and a
  maximal independent subset is extracted instead, lowering the claim.
* Timeouts / PARI errors are recorded as infrastructure outcomes, never as
  rank 0 and never as mathematical evidence.

USAGE
-----
  python3 construct_highrank.py m10 --trials N --seed S --amax M --out F.json
  python3 construct_highrank.py m8  --trials N --seed S --amax M --out F.json
  python3 construct_highrank.py augment --pool F.json --top K --nmax N --dmax D
"""

import argparse
import itertools
import json
import math
import os
import random
import sys
import time
import traceback
from fractions import Fraction as Fr

import cypari

pari = cypari.pari

# ---------------------------------------------------------------- polynomials
# polynomials are python lists of Fraction, index = degree


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


def prod_linear(A):
    p = [Fr(1)]
    for a in A:
        p = pmul(p, [Fr(-a), Fr(1)])
    return p


def pshift(p, c):
    """return p(t + c)"""
    out = [Fr(0)]
    base = [Fr(1)]
    for i, co in enumerate(p):
        if i > 0:
            base = pmul(base, [c, Fr(1)])
        out = psub(out, [-co * b for b in base])
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def polysqrt_trunc(p, k):
    """p monic of degree 2k -> monic g of degree k with deg(p - g^2) <= k-1."""
    g = [Fr(0)] * (k + 1)
    g[k] = Fr(1)
    for j in range(k - 1, -1, -1):
        S = Fr(0)
        for u in range(j + 1, k + 1):
            v = k + j - u
            if 0 <= v <= k and v > j:
                S += g[u] * g[v]
        g[j] = (p[k + j] - S) / 2
    return g


def mestre_polys(A):
    """A: list of 2k distinct rationals. returns p, g, s = g^2 - p."""
    n = len(A)
    assert n % 2 == 0
    k = n // 2
    p = prod_linear([Fr(a) for a in A])
    g = polysqrt_trunc(p, k)
    s = psub(pmul(g, g), p)
    # exact check of the 2k simultaneous square conditions
    for a in A:
        if peval(s, Fr(a)) != peval(g, Fr(a)) ** 2:
            raise AssertionError("square condition failed at a=%s" % a)
    return p, g, s


# --------------------------------------------------------- quartic -> cubic


def quartic_reduction(s, a0, e):
    """s quartic with s(a0) = e^2 (e != 0).  Return (D, coef) where D is the
    cubic in m and coef = (a,b,c,d,e) of the shifted quartic."""
    st = pshift(s, Fr(a0))
    st = st + [Fr(0)] * (5 - len(st))
    c0, d, c, b, a = st[0], st[1], st[2], st[3], st[4]
    if c0 != e * e:
        raise AssertionError("shift did not produce e^2 constant term")
    cp = c - d * d / (4 * e * e)
    P1 = psub([b], [Fr(0), d / e])
    P2 = psub([a], [Fr(0), Fr(0), Fr(1)])
    P3 = psub([cp], [Fr(0), 2 * e])
    D = psub(pmul(P1, P1), [4 * x for x in pmul(P2, P3)])
    return D, (a, b, c, d, e)


def quartic_point_to_cubic(t, v, coef):
    a, b, c, d, e = coef
    m = (v - e - (d / (2 * e)) * t) / (t * t)
    w = 2 * (a - m * m) * t + (b - (d / e) * m)
    return m, w


def cubic_to_weierstrass(D, pts):
    """w^2 = D(m), deg D = 3 -> Y^2 = X^3 + a2 X^2 + a4 X + a6 (integral)."""
    if len(D) != 4 or D[3] == 0:
        raise AssertionError("D is not a genuine cubic")
    A0, A1, A2, A3 = D[0], D[1], D[2], D[3]
    a2, a4, a6 = A2, A1 * A3, A0 * A3 * A3
    P = [(A3 * m, A3 * w) for m, w in pts]
    u = math.lcm(a2.denominator, a4.denominator, a6.denominator)
    a2, a4, a6 = a2 * u * u, a4 * u ** 4, a6 * u ** 6
    P = [(x * u * u, y * u ** 3) for x, y in P]
    ainv = [Fr(0), a2, Fr(0), a4, a6]
    for x, y in P:
        if y * y != x ** 3 + a2 * x * x + a4 * x + a6:
            raise AssertionError("weierstrass image point off curve")
    return [int(z) for z in ainv], P


# ------------------------------------------------------ exact on-curve check


def verify_on_curve(ainv, x, y):
    """EXACT check of y^2 + a1 x y + a3 y = x^3 + a2 x^2 + a4 x + a6.
    Own code, fractions only, no PARI."""
    a1, a2, a3, a4, a6 = [Fr(z) for z in ainv]
    x = Fr(x)
    y = Fr(y)
    return y * y + a1 * x * y + a3 * y == x ** 3 + a2 * x * x + a4 * x + a6


def disc_from_ainv(ainv):
    a1, a2, a3, a4, a6 = [Fr(z) for z in ainv]
    b2 = a1 * a1 + 4 * a2
    b4 = 2 * a4 + a1 * a3
    b6 = a3 * a3 + 4 * a6
    b8 = a1 * a1 * a6 + 4 * a2 * a6 - a1 * a3 * a4 + a2 * a3 * a3 - a4 * a4
    return -b2 * b2 * b8 - 8 * b4 ** 3 - 27 * b6 * b6 + 9 * b2 * b4 * b6


# ------------------------------------------------------------------- PARI


def frs(x):
    x = Fr(x)
    return "%d/%d" % (x.numerator, x.denominator)


def ptlist(P):
    return "[" + ",".join("[%s,%s]" % (frs(x), frs(y)) for x, y in P) + "]"


def minimal_model_and_points(ainv, P):
    """Return (min_ainv, min_points) via PARI ellminimalmodel/ellchangepoint."""
    gp = ("E0=ellinit(%s); v=0; E=ellminimalmodel(E0,&v);"
          "PL=%s; PL=[ellchangepoint(p,v)|p<-PL];"
          "[E[1..5],PL]") % (str(list(ainv)), ptlist(P))
    res = pari(gp)
    mai = [int(res[0][i]) for i in range(5)]
    mp = []
    for i in range(len(P)):
        q = res[1][i]
        mp.append((Fr(str(q[0])), Fr(str(q[1]))))
    return mai, mp


def height_matrix_det(ainv, P, prec):
    gp = ("default(realprecision,%d); E=ellinit(%s); PL=%s;"
          "M=ellheightmatrix(E,PL); [matdet(M), vector(#PL,i,M[i,i])]") % (
        prec, str(list(ainv)), ptlist(P))
    res = pari(gp)
    det = float(res[0])
    diag = [float(res[1][i]) for i in range(len(P))]
    return det, diag


def hadamard_ratio(det, diag):
    pr = 1.0
    for d in diag:
        if d <= 0:
            return 0.0
        pr *= d
    if pr == 0:
        return 0.0
    return abs(det) / pr


IND_TOL = 1e-9   # Hadamard ratio below this => treated as dependent


def independent_subset(ainv, P, prec=60):
    """Greedy maximal subset with non-degenerate height pairing matrix.
    Returns (indices, det, diag)."""
    idx = []
    last = (0.0, [])
    for i in range(len(P)):
        cand = idx + [i]
        sub = [P[j] for j in cand]
        if len(sub) == 1:
            d, dg = height_matrix_det(ainv, sub, prec)
            if d > 1e-12:
                idx = cand
                last = (d, dg)
            continue
        d, dg = height_matrix_det(ainv, sub, prec)
        if hadamard_ratio(d, dg) > IND_TOL:
            idx = cand
            last = (d, dg)
    return idx, last[0], last[1]


# ------------------------------------------------------------- constructions


def build_from_A(A, kind):
    """Return dict with curve + exhibited points, or raise."""
    p, g, s = mestre_polys(A)
    if kind == "m8":
        if len(s) != 4 or s[3] == 0:
            raise AssertionError("s is not a cubic")
        pts_model = [(Fr(a), peval(g, Fr(a))) for a in A]
        ainv, P = cubic_to_weierstrass(s, pts_model)
        base_index = None
        quartic = None
    else:
        if len(s) != 5 or s[4] == 0:
            raise AssertionError("s is not a quartic")
        base_index = 0
        e = peval(g, Fr(A[base_index]))
        if e == 0:
            raise AssertionError("base point has e = 0")
        D, coef = quartic_reduction(s, A[base_index], e)
        cub = []
        for i, a in enumerate(A):
            if i == base_index:
                continue
            t = Fr(a) - Fr(A[base_index])
            v = peval(g, Fr(a))
            m, w = quartic_point_to_cubic(t, v, coef)
            if w * w != peval(D, m):
                raise AssertionError("cubic image point off cubic")
            cub.append((m, w))
        if len(set(m for m, _ in cub)) != len(cub):
            raise AssertionError("image points collide")
        ainv, P = cubic_to_weierstrass(D, cub)
        quartic = dict(s=[frs(c) for c in s], base_a=A[base_index],
                       e=frs(e), coef=[frs(z) for z in coef],
                       D=[frs(c) for c in D])
    if disc_from_ainv(ainv) == 0:
        raise AssertionError("singular curve")
    mai, mp = minimal_model_and_points(ainv, P)
    for x, y in mp:
        if not verify_on_curve(mai, x, y):
            raise AssertionError("minimal-model point failed exact check")
    return dict(A=list(A), kind=kind, raw_ainv=[str(z) for z in ainv],
                min_ainv=[str(z) for z in mai],
                points=[(frs(x), frs(y)) for x, y in mp],
                _mp=mp, _mai=mai, quartic=quartic, base_index=base_index,
                s_poly=[frs(c) for c in s], g_poly=[frs(c) for c in g])


# ------------------------------------------------------------------ scoring


def score_curve(rec, prec_lo=60, prec_hi=120):
    mai, mp = rec["_mai"], rec["_mp"]
    det, diag = height_matrix_det(mai, mp, prec_lo)
    hr = hadamard_ratio(det, diag)
    if hr > IND_TOL:
        idx = list(range(len(mp)))
    else:
        idx, det, diag = independent_subset(mai, mp, prec_lo)
        hr = hadamard_ratio(det, diag)
    sub = [mp[i] for i in idx]
    det_hi, diag_hi = (height_matrix_det(mai, sub, prec_hi)
                       if sub else (0.0, []))
    rec["certified_rank"] = len(idx)
    rec["independent_indices"] = idx
    rec["regulator_det"] = det
    rec["regulator_det_highprec"] = det_hi
    rec["regulator_det_agree"] = (
        abs(det - det_hi) <= 1e-6 * max(1.0, abs(det)))
    rec["hadamard_ratio"] = hr
    rec["height_diagonal"] = diag
    rec["independent_points"] = [(frs(x), frs(y)) for x, y in sub]
    rec["exact_check_all_points"] = all(verify_on_curve(mai, x, y)
                                        for x, y in mp)
    return rec


# --------------------------------------------------------------- augment


def extra_quartic_points(s, A, nmax, dmax):
    """scan u = n/dd for extra rational squares of s(u)."""
    L = 1
    for c in s:
        L = math.lcm(L, c.denominator)
    C = [int(c * L) for c in s]          # integer coeffs of L*s
    found = []
    known = set(Fr(a) for a in A)
    for dd in range(1, dmax + 1):
        dd4 = [dd ** j for j in range(5)]
        for n in range(-nmax, nmax + 1):
            if math.gcd(abs(n), dd) != 1:
                continue
            u = Fr(n, dd)
            if u in known:
                continue
            # S = L*s(n/dd)*dd^4 ; s(u) square in Q  <=>  S*L square in Z
            S = 0
            npow = 1
            for j in range(len(C)):
                S += C[j] * npow * dd4[len(C) - 1 - j]
                npow *= n
            T = S * L
            if T < 0:
                continue
            r = math.isqrt(T)
            if r * r != T:
                continue
            # s(u) = T / (L*dd^2)^2
            val = Fr(r, L * dd * dd)
            if val * val != peval(s, u):
                continue
            found.append((u, val))
    return found


# ------------------------------------------------------------------ driver


def run_search(kind, trials, seed, amax, out, budget_s, log):
    rng = random.Random(seed)
    n = 8 if kind == "m8" else 10
    pool = []
    stats = dict(trials=0, built=0, degenerate=0, pari_errors=[],
                 rank_hist={})
    t0 = time.time()
    seen = set()
    while stats["trials"] < trials and time.time() - t0 < budget_s:
        stats["trials"] += 1
        A = tuple(sorted(rng.sample(range(-amax, amax + 1), n)))
        if A in seen:
            continue
        seen.add(A)
        try:
            rec = build_from_A(list(A), kind)
        except AssertionError as ex:
            stats["degenerate"] += 1
            continue
        except Exception as ex:                    # PARI / infrastructure
            stats["pari_errors"].append(
                dict(A=list(A), error=repr(ex)[:300], stage="build"))
            continue
        try:
            score_curve(rec)
        except Exception as ex:
            stats["pari_errors"].append(
                dict(A=list(A), error=repr(ex)[:300], stage="score"))
            continue
        stats["built"] += 1
        r = rec["certified_rank"]
        stats["rank_hist"][str(r)] = stats["rank_hist"].get(str(r), 0) + 1
        rec.pop("_mp")
        rec.pop("_mai")
        pool.append(rec)
        print("[%6.1fs] trial %d A=%s rank=%d det=%.6g" % (
            time.time() - t0, stats["trials"], list(A), r,
            rec["regulator_det"]), flush=True)
    stats["wall_clock_s"] = time.time() - t0
    stats["max_certified_rank"] = max(
        [c["certified_rank"] for c in pool], default=0)
    res = dict(kind=kind, seed=seed, amax=amax, stats=stats, curves=pool)
    with open(out, "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(stats, indent=1), flush=True)
    return res


def run_augment(poolfile, out, top, nmax, dmax, budget_s):
    data = json.load(open(poolfile))
    curves = sorted(data["curves"], key=lambda c: -c["certified_rank"])[:top]
    t0 = time.time()
    results = []
    for rec in curves:
        if time.time() - t0 > budget_s:
            break
        A = rec["A"]
        kind = rec["kind"]
        p, g, s = mestre_polys(A)
        extra = extra_quartic_points(s, A, nmax, dmax)
        info = dict(A=A, kind=kind, base_rank=rec["certified_rank"],
                    n_extra_found=len(extra),
                    extra_u=[frs(u) for u, _ in extra],
                    scan_nmax=nmax, scan_dmax=dmax)
        if extra and kind == "m10":
            base_index = rec["base_index"]
            e = peval(g, Fr(A[base_index]))
            D, coef = quartic_reduction(s, A[base_index], e)
            cub = []
            for i, a in enumerate(A):
                if i == base_index:
                    continue
                t = Fr(a) - Fr(A[base_index])
                cub.append(quartic_point_to_cubic(t, peval(g, Fr(a)), coef))
            for u, val in extra:
                for sgn in (1, -1):
                    t = u - Fr(A[base_index])
                    if t == 0:
                        continue
                    m, w = quartic_point_to_cubic(t, sgn * val, coef)
                    if w * w == peval(D, m):
                        cub.append((m, w))
                        break
            try:
                ainv, P = cubic_to_weierstrass(D, cub)
                mai, mp = minimal_model_and_points(ainv, P)
                rec2 = dict(A=A, kind=kind + "+extra", raw_ainv=[str(z) for z in ainv],
                            min_ainv=[str(z) for z in mai],
                            points=[(frs(x), frs(y)) for x, y in mp],
                            _mp=mp, _mai=mai, quartic=None,
                            base_index=base_index,
                            s_poly=[frs(c) for c in s],
                            g_poly=[frs(c) for c in g])
                score_curve(rec2)
                info["augmented_rank"] = rec2["certified_rank"]
                info["augmented_det"] = rec2["regulator_det"]
                rec2.pop("_mp")
                rec2.pop("_mai")
                info["augmented_curve"] = rec2
            except Exception as ex:
                info["augment_error"] = repr(ex)[:300]
        results.append(info)
        print("A=%s base=%d extra=%d aug=%s" % (
            A, rec["certified_rank"], len(extra),
            info.get("augmented_rank")), flush=True)
    out_obj = dict(source=poolfile, nmax=nmax, dmax=dmax,
                   wall_clock_s=time.time() - t0, results=results)
    with open(out, "w") as f:
        json.dump(out_obj, f, indent=1)
    return out_obj


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["m8", "m10", "augment"])
    ap.add_argument("--trials", type=int, default=50)
    ap.add_argument("--seed", type=int, default=20260822)
    ap.add_argument("--amax", type=int, default=12)
    ap.add_argument("--out", required=True)
    ap.add_argument("--pool")
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--nmax", type=int, default=200)
    ap.add_argument("--dmax", type=int, default=8)
    ap.add_argument("--budget", type=float, default=600.0)
    a = ap.parse_args()
    if a.mode == "augment":
        run_augment(a.pool, a.out, a.top, a.nmax, a.dmax, a.budget)
    else:
        run_search(a.mode, a.trials, a.seed, a.amax, a.out, a.budget, sys.stderr)


if __name__ == "__main__":
    main()
