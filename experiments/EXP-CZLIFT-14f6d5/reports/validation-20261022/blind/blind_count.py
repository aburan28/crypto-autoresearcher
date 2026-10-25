#!/usr/bin/env python3
"""Blind re-derivation of N_E(H) by slow scalar search (TASK-20261022-a846f4, joint J3).

Written from the specification of EXP-CZLIFT-14f6d5, the trial plan, the
hypothesis record H-CZLIFT-27a184 and general mathematics only.  No path in the
review plan's blind_from list was read before this file and its output were
sealed with sha256sum.

Quantity (review_plan.blind_rederivation): N_E(300) on each record curve.

The specification does not define N_E(H) in words.  The primary reading here is
the standard naive-height count (Silverman, AEC VIII.6; Neron's
N_E(H) ~ c_E (log H)^{r/2} is stated for it):

    N_E(H) = #{ P in E(Q) \\ {O} : H(x(P)) <= H },
    H(a/b) = max(|a|, b) for x = a/b in lowest terms, b >= 1,

counting P and -P separately.  Alternative readings are sealed alongside:
    x_only    : number of distinct x-coordinates (P and -P identified)
    with_O    : primary + 1 for the point at infinity
    d_height  : x = a/d^2, height max(|a|, d) <= H (denominator-root height)

Method ("slow scalar search", no sieve, no assumption on the denominator):
for every coprime pair (a, b) with |a| <= H, 1 <= b <= H, test whether
x = a/b is the x-coordinate of a rational point of
    y^2 + a1 x y + a3 y = x^3 + a2 x^2 + a4 x + a6
via (2y + a1 x + a3)^2 = 4x^3 + b2 x^2 + 2 b4 x + b6,
b2 = a1^2 + 4 a2, b4 = 2 a4 + a1 a3, b6 = a3^2 + 4 a6.
With F(a,b) = 4a^3 + b2 a^2 b + 2 b4 a b^2 + b6 b^3, the right side equals
F/b^3 = (F b)/b^4, a rational square iff F*b is an integer square s^2.
Every point found is re-verified on the original equation with exact
Fractions.  The d_height reading needs denominators up to H^2; for it only
square denominators d^2 are scanned (standard: on an integral Weierstrass model
x(P) = m/e^2), which the full scan up to b <= H independently confirms (any
non-square b hit is reported).
"""
from __future__ import annotations

import json
import math
import sys
import time
from fractions import Fraction

CURVES = {
    # From experiments/EXP-CZLIFT-14f6d5/specification.yaml, inputs.curves (verbatim).
    "grunewald_zimmert_1977_rank_ge_8": [1, -1, 1, -6494556985832, 6351402068900282539],
    "brumer_kramer_1977_rank_ge_9": [1, -1, 1, -1608154463, 25555312501831],
    # Own-counter controls (general mathematics, Cremona's tables):
    # 11a1: y^2 + y = x^3 - x^2 - 10x - 20, E(Q) = Z/5, affine torsion (5,5),(5,-6),(16,60),(16,-61).
    "control_11a1_rank0": [0, -1, 1, -10, -20],
    # 37a1: y^2 + y = x^3 - x, rank 1, E(Q) = Z, generator (0,0).
    "control_37a1_rank1": [0, 0, 1, -1, 0],
}


def b_invariants(ai):
    a1, a2, a3, a4, a6 = ai
    return a1 * a1 + 4 * a2, 2 * a4 + a1 * a3, a3 * a3 + 4 * a6


def on_curve(ai, x: Fraction, y: Fraction) -> bool:
    a1, a2, a3, a4, a6 = ai
    return y * y + a1 * x * y + a3 * y == x ** 3 + a2 * x * x + a4 * x + a6


def points_with_x(ai, a: int, b: int):
    """Rational points with x = a/b (gcd(a,b)=1, b>=1); [] if none."""
    b2, b4, b6 = b_invariants(ai)
    F = 4 * a ** 3 + b2 * a * a * b + 2 * b4 * a * b * b + b6 * b ** 3
    T = F * b
    if T < 0:
        return []
    s = math.isqrt(T)
    if s * s != T:
        return []
    a1, _, a3, _, _ = ai
    x = Fraction(a, b)
    out = []
    for sgn in ((1, -1) if s else (1,)):
        y = (Fraction(sgn * s, b * b) - a1 * x - a3) / 2
        if not on_curve(ai, x, y):
            raise AssertionError(f"point fails curve equation: {ai} x={x} y={y}")
        out.append((x, y))
    return out


def scan_full(ai, hmax: int):
    """All affine points with max(|a|, b) <= hmax, every denominator b scanned."""
    pts = []
    nonsquare_den_hits = 0
    for b in range(1, hmax + 1):
        for a in range(-hmax, hmax + 1):
            if math.gcd(a, b) != 1:
                continue
            found = points_with_x(ai, a, b)
            if found and math.isqrt(b) ** 2 != b:
                nonsquare_den_hits += 1
            for x, y in found:
                pts.append((x, y))
    return pts, nonsquare_den_hits


def scan_d_height(ai, dmax: int):
    """Affine points with x = a/d^2, max(|a|, d) <= dmax (square denominators only)."""
    pts = []
    for d in range(1, dmax + 1):
        b = d * d
        for a in range(-dmax, dmax + 1):
            if math.gcd(a, b) != 1:
                continue
            pts.extend(points_with_x(ai, a, b))
    return pts


def xheight(x: Fraction) -> int:
    return max(abs(x.numerator), x.denominator)


def main():
    hmax = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    grid = [h for h in (10, 30, 100, 300, 1000, 3000) if h <= hmax]
    result = {
        "schema": "validator.blind_rederivation.v1",
        "task_id": "TASK-20261022-a846f4",
        "experiment_id": "EXP-CZLIFT-14f6d5",
        "quantity": "N_E(300) on each record curve by slow scalar search",
        "primary_reading": "N_E(H) = #{P in E(Q)\\{O}: max(|num x|, den x) <= H}, P and -P counted separately",
        "scan_hmax": hmax,
        "curves": {},
    }
    for name, ai in CURVES.items():
        t0 = time.time()
        pts, nonsq = scan_full(ai, hmax)
        t1 = time.time()
        dpts = scan_d_height(ai, 300)
        t2 = time.time()
        b2, b4, b6 = b_invariants(ai)
        a1, a2, a3, a4, a6 = ai
        b8 = a1 * a1 * a6 + 4 * a2 * a6 - a1 * a3 * a4 + a2 * a3 * a3 - a4 * a4
        disc = -b2 * b2 * b8 - 8 * b4 ** 3 - 27 * b6 * b6 + 9 * b2 * b4 * b6
        counts = {}
        for h in grid:
            sel = [p for p in pts if xheight(p[0]) <= h]
            xs = {p[0] for p in sel}
            counts[str(h)] = {
                "primary_points_excl_O": len(sel),
                "x_only": len(xs),
                "with_O": len(sel) + 1,
            }
        pts_sorted = sorted(pts, key=lambda p: (xheight(p[0]), p[0], p[1]))
        result["curves"][name] = {
            "a_invariants": ai,
            "discriminant": str(disc),
            "nonsingular": disc != 0,
            "counts_by_H": counts,
            "N_E_300_primary": counts.get("300", {}).get("primary_points_excl_O"),
            "d_height_reading_N_300": len(dpts),
            "d_height_reading_x_only_300": len({p[0] for p in dpts}),
            "nonsquare_denominator_hits": nonsq,
            "points_up_to_scan_hmax": [
                {"x": str(x), "y": str(y), "H_x": xheight(x)} for x, y in pts_sorted
            ],
            "seconds_full_scan": round(t1 - t0, 3),
            "seconds_d_scan": round(t2 - t1, 3),
        }
        print(f"{name}: N(300) primary={counts.get('300', {}).get('primary_points_excl_O')} "
              f"x_only={counts.get('300', {}).get('x_only')} d_height={len(dpts)} "
              f"counts={ {h: c['primary_points_excl_O'] for h, c in counts.items()} } "
              f"nonsq_hits={nonsq} t={t1 - t0:.1f}s", flush=True)
    with open(sys.argv[2], "w") as fh:
        json.dump(result, fh, indent=1)


if __name__ == "__main__":
    main()
