#!/usr/bin/env python3
"""Blind re-derivation for TASK-20261022-38e8d2 (EXP-CZLIFT-8c50ea), joint J3.

Written from experiments/EXP-CZLIFT-8c50ea/specification.yaml,
experiments/EXP-CZLIFT-8c50ea/trial-plan.json and
ledger/hypotheses/H-CZLIFT-89e169.yaml only. No harness or implementation
file and no raw result was read before this file and its output were sealed.

Quantity: all points of E(K), K = Q(theta), theta^3 = 2, on 11a1 and 37a1 with
x = alpha/d^2, alpha in Z[theta] with |coords(alpha)| <= hmax in the integral
basis (1, theta, theta^2), 1 <= d <= dmax, and the rational sub-count
(alpha with zero theta-coordinates).

Square test.  For y^2 + a1 xy + a3 y = x^3 + a2 x^2 + a4 x + a6,
(2y + a1 x + a3)^2 = f(x) = 4x^3 + b2 x^2 + 2 b4 x + b6, so x in K is the
x-coordinate of a K-point iff f(x) is a square in K.  With x = alpha/d^2,
G = d^6 f(x) = 4 alpha^3 + b2 d^2 alpha^2 + 2 b4 d^4 alpha + b6 d^6 is in
Z[theta]; Z[theta] is the maximal order (disc -108 = field disc), hence
integrally closed, so G is a square in K iff it is a square in Z[theta].

Two independent square tests, both exact in what they accept:
  A  numpy: candidate sqrt from the three embeddings (both relative signs on
     the complex embedding), rounded to Z[theta], accepted only if the exact
     int64 square equals G.  No tolerance is used to reject.
  B  pure Python big ints: norm filter (N(G) must be a non-negative perfect
     square), then the characteristic-polynomial method: if G = beta^2 with
     charpoly(beta) = X^3 - t1 X^2 + t2 X - t3, then t3^2 = N(G),
     (t1^2 - s1)^2 - 8 t1 t3 - 4 s2 = 0 (s_i from charpoly(G)),
     t2 = (t1^2 - s1)/2 and beta (G + t2) = t1 G + t3.  Integer roots t1 are
     found exactly with sympy; beta is then checked exactly.
Every accepted point is finally re-verified on the original Weierstrass
equation in exact rational arithmetic over K.

Usage: python3 blind_points.py OUT.json
"""
import json
import math
import sys
import time
from fractions import Fraction

import numpy as np
import sympy

CURVES = {
    # Cremona labels, [a1, a2, a3, a4, a6] (general knowledge, not from the producer)
    "11a1": [0, -1, 1, -10, -20],
    "37a1": [0, 0, 1, -1, 0],
}
BOXES = {
    # specification.yaml inputs.box
    "replication_h24_d6": (24, 6),
    "main_h32_d4": (32, 4),
}


# ---------- exact Z[theta] / K arithmetic (theta^3 = 2) ----------
def mul(a, b):
    a0, a1, a2 = a
    b0, b1, b2 = b
    return (a0 * b0 + 2 * (a1 * b2 + a2 * b1),
            a0 * b1 + a1 * b0 + 2 * a2 * b2,
            a0 * b2 + a1 * b1 + a2 * b0)


def add(*xs):
    return tuple(sum(c) for c in zip(*xs))


def scal(k, a):
    return tuple(k * c for c in a)


def norm(a):
    a0, a1, a2 = a
    return a0 ** 3 + 2 * a1 ** 3 + 4 * a2 ** 3 - 6 * a0 * a1 * a2


def inverse(a):
    """Exact inverse in K via the adjugate: a * adj(a) = N(a)."""
    a0, a1, a2 = a
    adj = (a0 * a0 - 2 * a1 * a2, 2 * a2 * a2 - a0 * a1, a1 * a1 - a0 * a2)
    n = norm(a)
    assert mul(a, adj) == (n, 0, 0)
    return tuple(Fraction(c, n) for c in adj)


def bcoef(ai):
    a1, a2, a3, a4, a6 = ai
    return a1 * a1 + 4 * a2, 2 * a4 + a1 * a3, a3 * a3 + 4 * a6


def G_exact(alpha, d, b2, b4, b6):
    a2_ = mul(alpha, alpha)
    a3_ = mul(a2_, alpha)
    return add(scal(4, a3_), scal(b2 * d ** 2, a2_), scal(2 * b4 * d ** 4, alpha),
               (b6 * d ** 6, 0, 0))


# ---------- Method B: exact characteristic-polynomial square test ----------
_t = sympy.Symbol("t")


def sqrt_exact_B(G):
    """Return beta in Z[theta] with beta^2 = G, or None.  Exact."""
    if G == (0, 0, 0):
        return (0, 0, 0)
    n = norm(G)
    if n < 0:
        return None
    r = math.isqrt(n)
    if r * r != n:
        return None
    if G[1] == 0 and G[2] == 0:
        # rational G: square in K (odd degree) iff square in Q
        g = G[0]
        if g < 0:
            return None
        s = math.isqrt(g)
        return (s, 0, 0) if s * s == g else None
    s1 = 3 * G[0]
    G2 = mul(G, G)
    s2 = (s1 * s1 - 3 * G2[0]) // 2
    assert s1 * s1 - 3 * G2[0] == 2 * s2
    for t3 in {r, -r}:
        poly = sympy.Poly((_t ** 2 - s1) ** 2 - 8 * t3 * _t - 4 * s2, _t, domain="ZZ")
        for root in poly.ground_roots():
            t1 = int(root)
            if (t1 * t1 - s1) % 2:
                continue
            t2 = (t1 * t1 - s1) // 2
            den = add(G, (t2, 0, 0))
            num = add(scal(t1, G), (t3, 0, 0))
            beta = mul(num, inverse(den))
            if all(c.denominator == 1 for c in beta):
                beta = tuple(int(c) for c in beta)
                if mul(beta, beta) == G:
                    return beta
    return None


def run_B(ai, hmax, dmax):
    b2, b4, b6 = bcoef(ai)
    hits = {}
    norm_survivors = 0
    for d in range(1, dmax + 1):
        for a0 in range(-hmax, hmax + 1):
            for a1 in range(-hmax, hmax + 1):
                for a2 in range(-hmax, hmax + 1):
                    G = G_exact((a0, a1, a2), d, b2, b4, b6)
                    n = norm(G)
                    if G != (0, 0, 0):
                        if n < 0:
                            continue
                        r = math.isqrt(n)
                        if r * r != n:
                            continue
                    norm_survivors += 1
                    beta = sqrt_exact_B(G)
                    if beta is not None:
                        hits[(a0, a1, a2, d)] = beta
    return hits, norm_survivors


# ---------- Method A: numpy embedding candidates + exact int64 check ----------
C = 2.0 ** (1.0 / 3.0)
W = complex(-0.5, math.sqrt(3) / 2)


def run_A(ai, hmax, dmax):
    b2, b4, b6 = bcoef(ai)
    rng = np.arange(-hmax, hmax + 1, dtype=np.int64)
    A0, A1, A2 = [x.ravel() for x in np.meshgrid(rng, rng, rng, indexing="ij")]

    def m(a, b):
        return (a[0] * b[0] + 2 * (a[1] * b[2] + a[2] * b[1]),
                a[0] * b[1] + a[1] * b[0] + 2 * a[2] * b[2],
                a[0] * b[2] + a[1] * b[1] + a[2] * b[0])

    al = (A0, A1, A2)
    sq = m(al, al)
    cu = m(sq, al)
    hits = {}
    for d in range(1, dmax + 1):
        g = [4 * cu[i] + b2 * d ** 2 * sq[i] + 2 * b4 * d ** 4 * al[i] for i in range(3)]
        g[0] = g[0] + b6 * d ** 6
        assert max(int(np.abs(x).max()) for x in g) < 2 ** 40
        gf = [x.astype(np.float64) for x in g]
        v1 = np.sqrt(np.maximum(gf[0] + gf[1] * C + gf[2] * C * C, 0.0))
        v2c = gf[0] + gf[1] * (C * W) + gf[2] * (C * C * W * W)
        r2 = np.sqrt(v2c.astype(np.complex128))
        for s in (1.0, -1.0):
            v2 = s * r2
            b0 = (v1 + 2 * v2.real) / 3
            b1 = (v1 + 2 * (v2 * np.conj(W)).real) / (3 * C)
            bb2 = (v1 + 2 * (v2 * np.conj(W) ** 2).real) / (3 * C * C)
            B = [np.rint(x).astype(np.int64) for x in (b0, b1, bb2)]
            sqb = m(B, B)
            ok = (sqb[0] == g[0]) & (sqb[1] == g[1]) & (sqb[2] == g[2])
            for i in np.nonzero(ok)[0]:
                key = (int(A0[i]), int(A1[i]), int(A2[i]), d)
                hits[key] = (int(B[0][i]), int(B[1][i]), int(B[2][i]))
    return hits


# ---------- points ----------
def on_curve(ai, x, y):
    a1, a2, a3, a4, a6 = ai
    lhs = add(mul(y, y), scal(a1, mul(x, y)), scal(a3, y))
    x2 = mul(x, x)
    rhs = add(mul(x2, x), scal(a2, x2), scal(a4, x), (a6, 0, 0))
    return lhs == rhs


def min_rep(x):
    """Minimal d with d^2 x in Z[theta], and h = max|coords(d^2 x)|."""
    den = 1
    for c in x:
        den = den * c.denominator // math.gcd(den, c.denominator)
    d = 1
    while (d * d) % den:
        d += 1
    al = tuple(int(c * d * d) for c in x)
    return d, max(abs(c) for c in al), al


def fmt(x):
    return [str(c) for c in x]


def points_from_hits(ai, hits):
    a1, a2, a3, a4, a6 = ai
    by_x = {}
    for (q0, q1, q2, d), beta in hits.items():
        x = tuple(Fraction(c, d * d) for c in (q0, q1, q2))
        w = tuple(Fraction(c, d ** 3) for c in beta)  # 2y + a1 x + a3 = +-w
        ys = set()
        for sgn in (1, -1):
            y = tuple((sgn * w[i] - a1 * x[i] - (a3 if i == 0 else 0)) / 2 for i in range(3))
            assert on_curve(ai, x, y), (x, y)
            ys.add(y)
        by_x.setdefault(x, {"ys": ys, "reps": []})["reps"].append([q0, q1, q2, d])
    out = []
    for x, rec in sorted(by_x.items(), key=lambda kv: (min_rep(kv[0])[1], min_rep(kv[0])[0], [float(c) for c in kv[0]])):
        d0, h0, al0 = min_rep(x)
        out.append({
            "x": fmt(x),
            "ys": sorted([fmt(y) for y in rec["ys"]]),
            "n_affine_points": len(rec["ys"]),
            "rational": x[1] == 0 and x[2] == 0,
            "min_alpha": list(al0),
            "min_d": d0,
            "min_h": h0,
            "box_representations": sorted(rec["reps"]),
        })
    return out


def bound_torsion_11a1():
    """#E(F_p) at degree-one primes of K for 11a1: torsion of E(K) injects
    into E~(F_p) at a good unramified degree-one prime with p > 2."""
    ai = CURVES["11a1"]
    out = {}
    for p in (5, 7, 13, 17, 23, 29, 31, 43, 47):
        roots = [r for r in range(p) if (r ** 3 - 2) % p == 0]
        if not roots or p in (2, 3, 11):
            continue
        a1, a2, a3, a4, a6 = ai
        cnt = 1
        for X in range(p):
            for Y in range(p):
                if (Y * Y + a1 * X * Y + a3 * Y - (X ** 3 + a2 * X * X + a4 * X + a6)) % p == 0:
                    cnt += 1
        out[p] = cnt
    g = 0
    for v in out.values():
        g = math.gcd(g, v)
    return {"E_Fp_orders_at_degree1_primes": out, "gcd": g}


def main():
    outpath = sys.argv[1]
    result = {"field": "Q(theta), theta^3 = 2, basis (1, theta, theta^2)",
              "curves": {k: v for k, v in CURVES.items()},
              "boxes": {k: {"hmax": v[0], "dmax": v[1]} for k, v in BOXES.items()},
              "results": {}}
    for cname, ai in CURVES.items():
        for bname, (hmax, dmax) in BOXES.items():
            t0 = time.time()
            hA = run_A(ai, hmax, dmax)
            tA = time.time() - t0
            t0 = time.time()
            hB, nsurv = run_B(ai, hmax, dmax)
            tB = time.time() - t0
            agree = (set(hA) == set(hB)) and all(
                mul(hA[k], hA[k]) == mul(hB[k], hB[k]) for k in hA)
            pts = points_from_hits(ai, hB)
            nx = len(pts)
            nxq = sum(1 for p in pts if p["rational"])
            naff = sum(p["n_affine_points"] for p in pts)
            naffq = sum(p["n_affine_points"] for p in pts if p["rational"])
            npairs = len(hB)
            npairsq = sum(1 for k in hB if k[1] == 0 and k[2] == 0)
            cum = []
            for h in range(0, hmax + 1):
                inbox = [p for p in pts if p["min_h"] <= h and p["min_d"] <= dmax]
                cum.append({
                    "h": h,
                    "NK_x": len(inbox),
                    "NQ_x": sum(1 for p in inbox if p["rational"]),
                    "NK_pts": sum(p["n_affine_points"] for p in inbox),
                    "NQ_pts": sum(p["n_affine_points"] for p in inbox if p["rational"]),
                    "NK_pairs": sum(1 for k in hB if max(abs(k[0]), abs(k[1]), abs(k[2])) <= h),
                    "NQ_pairs": sum(1 for k in hB if k[1] == 0 and k[2] == 0 and abs(k[0]) <= h),
                })
            result["results"][f"{cname}/{bname}"] = {
                "curve": cname, "hmax": hmax, "dmax": dmax,
                "methodA_hits": len(hA), "methodB_hits": len(hB),
                "methodB_norm_square_survivors": nsurv,
                "methods_agree": agree,
                "seconds": {"A": round(tA, 2), "B": round(tB, 2)},
                "counts": {
                    "distinct_x_K": nx, "distinct_x_Q": nxq,
                    "affine_points_K": naff, "affine_points_Q": naffq,
                    "points_with_O_K": naff + 1, "points_with_O_Q": naffq + 1,
                    "alpha_d_pairs_K": npairs, "alpha_d_pairs_Q": npairsq,
                    "ratio_x": (nx / nxq) if nxq else None,
                    "ratio_affine_points": (naff / naffq) if naffq else None,
                    "ratio_points_with_O": (naff + 1) / (naffq + 1),
                    "ratio_pairs": (npairs / npairsq) if npairsq else None,
                },
                "cumulative_in_h_at_fixed_dmax": cum,
                "points": pts,
            }
            print(cname, bname, result["results"][f"{cname}/{bname}"]["counts"],
                  "agree", agree, "secs", round(tA, 1), round(tB, 1), flush=True)
    result["torsion_bound_11a1"] = bound_torsion_11a1()
    print("torsion bound 11a1", result["torsion_bound_11a1"], flush=True)
    with open(outpath, "w") as fh:
        json.dump(result, fh, indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
