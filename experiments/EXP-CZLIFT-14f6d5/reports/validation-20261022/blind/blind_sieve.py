#!/usr/bin/env python3
"""Blind extension of the J3 re-derivation to H = 10^5 and 3 x 10^5 (TASK-20261022-a846f4).

Written before any path in the review plan's blind_from was read, from the
specification's a-invariants and general mathematics only.  This is NOT the
slow scalar search (that is blind_count.py, H <= 1000, every denominator); it
is an independent fast enumeration added because N_E(300) = 0 on both record
curves makes the H = 300 comparison nearly vacuous.

Reading (same primary reading as blind_count.py):
    N_E(H) = #{ P in E(Q) \\ {O} : max(|num x(P)|, den x(P)) <= H },
P and -P counted separately.

Method: on an integral Weierstrass model x(P) = a/d^2 with gcd(a, d) = 1
(standard).  For each d <= sqrt(H) and every a in [-H, H], x = a/d^2 is an
x-coordinate iff G(a) = 4a^3 + b2 a^2 d^2 + 2 b4 a d^4 + b6 d^6 is an integer
square (the right side of (2y + a1 x + a3)^2 = 4x^3 + b2 x^2 + 2 b4 x + b6
times d^6).  Candidates are filtered by quadratic-residue tests modulo small
moduli (sound: a true square passes every test), then every survivor is
tested exactly with math.isqrt and every hit is re-verified on the original
equation with exact Fractions.  Single process.
"""
from __future__ import annotations

import json
import math
import sys
import time
from fractions import Fraction

import numpy as np

CURVES = {
    "grunewald_zimmert_1977_rank_ge_8": [1, -1, 1, -6494556985832, 6351402068900282539],
    "brumer_kramer_1977_rank_ge_9": [1, -1, 1, -1608154463, 25555312501831],
    "control_11a1_rank0": [0, -1, 1, -10, -20],
    "control_37a1_rank1": [0, 0, 1, -1, 0],
}
MODULI = [64, 63, 65, 11, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]
SQ_TABLES = {}
for m in MODULI:
    t = np.zeros(m, dtype=bool)
    t[[(i * i) % m for i in range(m)]] = True
    SQ_TABLES[m] = t


def b_inv(ai):
    a1, a2, a3, a4, a6 = ai
    return a1 * a1 + 4 * a2, 2 * a4 + a1 * a3, a3 * a3 + 4 * a6


def on_curve(ai, x, y):
    a1, a2, a3, a4, a6 = ai
    return y * y + a1 * x * y + a3 * y == x ** 3 + a2 * x * x + a4 * x + a6


def scan(ai, hmax):
    b2, b4, b6 = b_inv(ai)
    a1, _, a3, _, _ = ai
    A = np.arange(-hmax, hmax + 1, dtype=np.int64)
    pts = []
    survivors_total = 0
    for d in range(1, math.isqrt(hmax) + 1):
        b = d * d
        mask = np.ones(A.shape, dtype=bool)
        for m in MODULI:
            am = A % m
            c3, c2, c1, c0 = 4 % m, (b2 * b) % m, (2 * b4 * b * b) % m, (b6 * b ** 3) % m
            g = (c3 * am + c2) % m
            g = (g * am + c1) % m
            g = (g * am + c0) % m
            mask &= SQ_TABLES[m][g]
        cand = A[mask]
        survivors_total += int(cand.size)
        for a in cand.tolist():
            if math.gcd(a, d) != 1:
                continue
            G = 4 * a ** 3 + b2 * a * a * b + 2 * b4 * a * b * b + b6 * b ** 3
            if G < 0:
                continue
            s = math.isqrt(G)
            if s * s != G:
                continue
            x = Fraction(a, b)
            # (2y + a1 x + a3)^2 = G / d^6  ->  2y + a1 x + a3 = +- s / d^3
            for sgn in ((1, -1) if s else (1,)):
                y = (Fraction(sgn * s, d ** 3) - a1 * x - a3) / 2
                if not on_curve(ai, x, y):
                    raise AssertionError((ai, x, y))
                pts.append((x, y))
    return pts, survivors_total


def xh(x):
    return max(abs(x.numerator), x.denominator)


def main():
    hmax = int(sys.argv[1])
    out_path = sys.argv[2]
    grid = [h for h in (300, 1000, 3000, 10000, 30000, 100000, 300000) if h <= hmax]
    res = {"schema": "validator.blind_rederivation_sieve.v1", "task_id": "TASK-20261022-a846f4",
           "reading": "N_E(H) = #{P != O : max(|num x|, den x) <= H}, P and -P separate",
           "scan_hmax": hmax, "moduli": MODULI, "curves": {}}
    for name, ai in CURVES.items():
        t0 = time.time()
        pts, surv = scan(ai, hmax)
        dt = time.time() - t0
        counts = {str(h): sum(1 for p in pts if xh(p[0]) <= h) for h in grid}
        xcounts = {str(h): len({p[0] for p in pts if xh(p[0]) <= h}) for h in grid}
        pts.sort(key=lambda p: (xh(p[0]), p[0], p[1]))
        res["curves"][name] = {
            "a_invariants": ai, "counts_by_H": counts, "x_only_counts_by_H": xcounts,
            "qr_filter_survivors": surv, "seconds": round(dt, 2),
            "points": [{"x": str(x), "y": str(y), "H_x": xh(x)} for x, y in pts],
        }
        print(f"{name}: counts={counts} survivors={surv} t={dt:.1f}s", flush=True)
    with open(out_path, "w") as fh:
        json.dump(res, fh, indent=1)


if __name__ == "__main__":
    main()
