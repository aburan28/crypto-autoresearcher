#!/usr/bin/env python3
"""Rank lower-bound certificates by reduction (TASK-20261022-a846f4; citation provenance and control C3).

For E/Q with E(Q)[2] = 0 (checked: 4x^3 + b2 x^2 + 2 b4 x + b6 has no rational
root), dim_F2 E(Q)/2E(Q) = rank.  For a good odd prime p at which the cubic
splits completely, the map  Q -> (chi(x - e1), chi(x - e2))  (Legendre symbols;
for x = e_i the product rule chi((e_i - e_j)(e_i - e_k)) is used; O -> (+,+))
is a homomorphism E(F_p) -> (Z/2)^2 with kernel 2E(F_p).  Composed with
reduction it kills 2E(Q).  If the images of k points have F_2-rank k, the
points are independent in E(Q)/2E(Q) and rank >= k.  Sound; not a rank
upper bound.
Usage: rank_certificate.py RANK7_POINTS_JSON SOURCE_CHECK_JSON OUT_JSON
"""
import json
import sys
from fractions import Fraction

import sympy

CURVES = {
    "382623908456a1": [0, 0, 0, -10012, 346900],
    "grunewald-zimmert-1977-rank-ge-8": [1, -1, 1, -6494556985832, 6351402068900282539],
    "brumer-kramer-1977-rank-ge-9": [1, -1, 1, -1608154463, 25555312501831],
}


def binv(ai):
    a1, a2, a3, a4, a6 = ai
    return a1 * a1 + 4 * a2, 2 * a4 + a1 * a3, a3 * a3 + 4 * a6


def on_curve(ai, x, y):
    a1, a2, a3, a4, a6 = ai
    return y * y + a1 * x * y + a3 * y == x ** 3 + a2 * x * x + a4 * x + a6


def chi(a, p):
    a %= p
    if a == 0:
        return 0
    return 1 if pow(a, (p - 1) // 2, p) == 1 else -1


def rank_f2(rows):
    rows = [int("".join(map(str, r)), 2) for r in rows]
    rank = 0
    for bit in reversed(range(max(1, max((r.bit_length() for r in rows), default=1)))):
        piv = next((i for i, r in enumerate(rows) if (r >> bit) & 1), None)
        if piv is None:
            continue
        pr = rows.pop(piv)
        rows = [r ^ pr if (r >> bit) & 1 else r for r in rows]
        rank += 1
    return rank


def certify(ai, pts, target, pmax=200000):
    b2, b4, b6 = binv(ai)
    X = sympy.symbols("X")
    f = 4 * X ** 3 + b2 * X ** 2 + 2 * b4 * X + b6
    rational_roots = [r for r in sympy.roots(sympy.Poly(f, X), filter="Q")]
    disc = sympy.discriminant(f, X)
    cols = [[] for _ in pts]
    used = []
    p = 3
    while p < pmax:
        p = int(sympy.nextprime(p))
        if disc % p == 0:
            continue
        # complete splitting of f mod p into three distinct linear factors
        fac = sympy.Poly(f, X, modulus=p).factor_list()[1]
        lin = [g for g, e in fac if g.degree() == 1]
        if len(lin) != 3 or any(e != 1 for _, e in fac):
            continue
        es = sorted({int((-g.all_coeffs()[1] * pow(int(g.all_coeffs()[0]) % p, -1, p)) % p) for g in lin})
        if len(es) != 3:
            continue
        e1, e2, e3 = es
        for i, (x, y) in enumerate(pts):
            if x.denominator % p == 0:
                bits = (0, 0)
            else:
                xr = x.numerator * pow(x.denominator, -1, p) % p
                c1 = chi(xr - e1, p) if xr != e1 else chi((e1 - e2) * (e1 - e3), p)
                c2 = chi(xr - e2, p) if xr != e2 else chi((e2 - e1) * (e2 - e3), p)
                bits = (0 if c1 == 1 else 1, 0 if c2 == 1 else 1)
            cols[i].extend(bits)
        used.append(p)
        if rank_f2(cols) >= target and len(used) >= target + 4:
            break
    r = rank_f2(cols)
    return {"rational_roots_of_2_division_cubic": [str(z) for z in rational_roots],
            "E_Q_2_torsion_trivial": len(rational_roots) == 0,
            "points_used": len(pts), "split_primes_used": used, "f2_rank_of_images": r,
            "certified_rank_lower_bound": r if len(rational_roots) == 0 else None}


def main():
    rank7 = json.load(open(sys.argv[1]))["curves"]["382623908456a1_from_raw"]["points"]
    src = json.load(open(sys.argv[2]))["pages"]
    out = {}
    # rank-7 curve: one point per x-coordinate among the 40 smallest-height points of the validator's enumeration
    seen, pts7 = set(), []
    for p in rank7:
        x = Fraction(p["x"])
        if x in seen:
            continue
        seen.add(x)
        pts7.append((x, Fraction(p["y"])))
        if len(pts7) >= 40:
            break
    out["382623908456a1"] = certify(CURVES["382623908456a1"], pts7, 8)
    for key, label in (("rk8", "grunewald-zimmert-1977-rank-ge-8"), ("rk9", "brumer-kramer-1977-rank-ge-9")):
        ai = CURVES[label]
        pts = [(Fraction(q["x"]), Fraction(q["y"])) for q in src[key]["listed_points"]]
        assert all(on_curve(ai, x, y) for x, y in pts)
        out[label] = certify(ai, pts, len(pts))
        out[label]["source_points"] = len(pts)
    json.dump(out, open(sys.argv[3], "w"), indent=1)
    for k, v in out.items():
        print(k, {kk: vv for kk, vv in v.items() if kk != "split_primes_used"}, "n_split_primes", len(v["split_primes_used"]))


if __name__ == "__main__":
    main()
