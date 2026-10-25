#!/usr/bin/env python3
"""Blind re-derivation (joint J3) for TASK-20261022-3aca4b / EXP-CZLIFT-a255fc.

Written from the statement only: experiments/EXP-CZLIFT-a255fc/specification.yaml,
trial-plan.json, ledger/hypotheses/H-CZLIFT-9a32e9.yaml and general mathematics.
No path listed in review_plan.blind_rederivation.blind_from was opened before this
file and its output were sealed (see SEAL.sha256).

Quantity (review_plan.blind_rederivation.quantity):
  * N_E(H) for 11a1 and 37a1 at H = 300 and H = 1000 by a slow scalar search;
  * the uniform model N_p (1 - (1 - 1/N_p)^N) for 37a1 at p = 101 and p = 1009
    with an independently computed N_p.

Definitions taken from the statement:
  * naive height H(x) = max(|a|, d^2) for x = a/d^2 in lowest terms;
  * N_E(H) counts rational points (both y-values for an x), the point at
    infinity once;
  * model value M(N, N_p) = N_p (1 - (1 - 1/N_p)^N), N = N_E(H) the same count
    the observed residue count uses.

Assumption (the specification defers ainvs to implementation/run.py, which is
blind-from): the Cremona minimal models
  11a1 = [0,-1,1,-10,-20]   y^2 + y = x^3 - x^2 - 10x - 20  (rank 0, torsion Z/5)
  37a1 = [0, 0,1, -1,  0]   y^2 + y = x^3 - x               (rank 1, gen (0,0))
The rank / generator / torsion facts are recalled and are used only for the
independent group-law cross-check, never for the slow search itself.
"""
import json
import math
import platform
import sys
from fractions import Fraction

CURVES = {
    "11a1": (0, -1, 1, -10, -20),
    "37a1": (0, 0, 1, -1, 0),
}
GRID = [10, 30, 100, 300, 1000, 3000, 10000]          # slow search grid
GRID_GROUPLAW = [10, 30, 100, 300, 1000, 3000, 10000, 30000, 100000, 300000]
PRIMES = [101, 1009]


def binv(a1, a2, a3, a4, a6):
    return a1 * a1 + 4 * a2, 2 * a4 + a1 * a3, a3 * a3 + 4 * a6


def on_curve(ainv, P):
    if P is None:
        return True
    a1, a2, a3, a4, a6 = ainv
    x, y = P
    return y * y + a1 * x * y + a3 * y == x ** 3 + a2 * x * x + a4 * x + a6


def height(P):
    if P is None:
        return 1
    x = P[0]
    return max(abs(x.numerator), x.denominator)


def slow_search(ainv, H):
    """Every rational point with max(|a|, d^2) <= H, scalar loops, exact isqrt."""
    a1, a2, a3, a4, a6 = ainv
    b2, b4, b6 = binv(*ainv)
    pts = [None]
    for d in range(1, math.isqrt(H) + 1):
        d2 = d * d
        d3 = d2 * d
        d4 = d2 * d2
        d6 = d4 * d2
        for a in range(-H, H + 1):
            if math.gcd(a, d) != 1:
                continue
            # (d^3 (2y + a1 x + a3))^2 = 4a^3 + b2 a^2 d^2 + 2 b4 a d^4 + b6 d^6
            R = 4 * a ** 3 + b2 * a * a * d2 + 2 * b4 * a * d4 + b6 * d6
            if R < 0:
                continue
            s = math.isqrt(R)
            if s * s != R:
                continue
            x = Fraction(a, d2)
            for t in sorted({s, -s}):
                y = (Fraction(t, d3) - a1 * x - a3) / 2
                P = (x, y)
                assert on_curve(ainv, P), (ainv, P)
                assert height(P) <= H
                pts.append(P)
    return pts


# ---- independent group law (Fractions) for the cross-check -----------------
def neg(ainv, P):
    if P is None:
        return None
    a1, a2, a3, a4, a6 = ainv
    x, y = P
    return (x, -y - a1 * x - a3)


def add(ainv, P, Q):
    a1, a2, a3, a4, a6 = ainv
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and y1 + y2 + a1 * x2 + a3 == 0:
        return None
    if x1 == x2:
        lam = (3 * x1 * x1 + 2 * a2 * x1 + a4 - a1 * y1) / (2 * y1 + a1 * x1 + a3)
    else:
        lam = (y2 - y1) / (x2 - x1)
    nu = y1 - lam * x1
    x3 = lam * lam + a1 * lam - a2 - x1 - x2
    y3 = -(lam + a1) * x3 - nu - a3
    R = (x3, y3)
    assert on_curve(ainv, R)
    return R


def grouplaw_points(ainv, gen, nmax):
    pts = {}
    P = None
    for n in range(1, nmax + 1):
        P = add(ainv, P, gen)
        if P is None:
            break
        pts[n] = P
    return pts


# ---- reduction mod p ----------------------------------------------------------
def reduce_pt(P, p):
    if P is None:
        return "O"
    x, y = P
    if x.denominator % p == 0:
        return "O"
    return (x.numerator * pow(x.denominator, -1, p) % p,
            y.numerator * pow(y.denominator, -1, p) % p)


def count_Fp_brute(ainv, p):
    a1, a2, a3, a4, a6 = ainv
    n = 1
    for x in range(p):
        r = (x ** 3 + a2 * x * x + a4 * x + a6) % p
        for y in range(p):
            if (y * y + a1 * x * y + a3 * y - r) % p == 0:
                n += 1
    return n


def count_Fp_legendre(ainv, p):
    b2, b4, b6 = binv(*ainv)
    n = 1
    for x in range(p):
        f = (4 * x ** 3 + b2 * x * x + 2 * b4 * x + b6) % p
        if f == 0:
            n += 1
        else:
            n += 1 + (1 if pow(f, (p - 1) // 2, p) == 1 else -1)
    return n


def model(N, Np):
    return Np * (1 - (1 - Fraction(1, Np)) ** N)


def main():
    out = {
        "task_id": "TASK-20261022-3aca4b",
        "experiment_id": "EXP-CZLIFT-a255fc",
        "joint": "J3",
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "assumed_ainvs": {k: list(v) for k, v in CURVES.items()},
        "height": "max(|a|, d^2), x = a/d^2 lowest terms; O counted once",
        "slow_search": {},
        "grouplaw_crosscheck": {},
        "uniform_model_37a1": {},
    }
    slow = {}
    for name, ainv in CURVES.items():
        slow[name] = {}
        for H in GRID:
            pts = slow_search(ainv, H)
            slow[name][H] = pts
        Hbig = GRID[-1]
        out["slow_search"][name] = {
            "N_E": {str(H): len(slow[name][H]) for H in GRID},
            "points_at_H_%d" % Hbig: [
                "O" if P is None else "(%s, %s) h=%d" % (P[0], P[1], height(P))
                for P in slow[name][Hbig]
            ],
        }
    # nested consistency: the H-search at smaller H equals the filtered larger one
    for name in CURVES:
        big = slow[name][GRID[-1]]
        for H in GRID:
            assert len([P for P in big if height(P) <= H]) == len(slow[name][H])

    # group-law cross-checks
    tors = grouplaw_points(CURVES["11a1"], (Fraction(5), Fraction(5)), 10)
    tpts = [None] + list(tors.values())
    out["grouplaw_crosscheck"]["11a1"] = {
        "generator": "(5,5)", "order": len(tpts),
        "points": ["(%s, %s) h=%d" % (P[0], P[1], height(P)) for P in tpts[1:]],
        "N_E": {str(H): sum(1 for P in tpts if height(P) <= H) for H in GRID_GROUPLAW},
    }
    ainv = CURVES["37a1"]
    gen = (Fraction(0), Fraction(0))
    mult = grouplaw_points(ainv, gen, 24)
    gl = [None]
    heights = {}
    for n, P in mult.items():
        gl.append(P)
        gl.append(neg(ainv, P))
        heights[n] = height(P)
    out["grouplaw_crosscheck"]["37a1"] = {
        "generator": "(0,0)",
        "height_of_nP": {str(n): heights[n] for n in range(1, 13)},
        "N_E": {str(H): sum(1 for P in gl if height(P) <= H) for H in GRID_GROUPLAW},
    }
    for H in GRID:
        a = sorted(map(str, [P for P in slow["37a1"][H] if P is not None]))
        b = sorted(map(str, [P for P in gl if P is not None and height(P) <= H]))
        assert a == b, ("37a1 slow vs group law", H)
        a = sorted(map(str, [P for P in slow["11a1"][H] if P is not None]))
        b = sorted(map(str, [P for P in tpts if P is not None and height(P) <= H]))
        assert a == b, ("11a1 slow vs torsion", H)

    # uniform model for 37a1
    for p in PRIMES:
        Np_leg = count_Fp_legendre(ainv, p)
        Np_brute = count_Fp_brute(ainv, p)
        assert Np_leg == Np_brute
        Np = Np_leg
        rows = []
        for H in GRID_GROUPLAW:
            pts = [P for P in gl if height(P) <= H]
            N = len(pts)
            m = model(N, Np)
            obs = len({reduce_pt(P, p) for P in pts})
            rows.append({
                "H": H, "N": N,
                "model": float(m),
                "model_exact": "%s/%s" % (m.numerator, m.denominator) if N <= 12 else None,
                "observed_distinct_residues": obs,
                "ratio": obs / float(m),
                "model_over_Np": float(m) / Np,
                "passes_tail_filter_N_ge_30_and_cov_le_0p9": (N >= 30 and float(m) / Np <= 0.9),
            })
        out["uniform_model_37a1"][str(p)] = {
            "N_p": Np, "a_p": p + 1 - Np, "N_p_method": "Legendre count == brute force count",
            "rows": rows,
        }
    # headline values the task asks for
    out["headline"] = {
        "N_E_11a1_H300": out["slow_search"]["11a1"]["N_E"]["300"],
        "N_E_11a1_H1000": out["slow_search"]["11a1"]["N_E"]["1000"],
        "N_E_37a1_H300": out["slow_search"]["37a1"]["N_E"]["300"],
        "N_E_37a1_H1000": out["slow_search"]["37a1"]["N_E"]["1000"],
        "N_p_37a1": {str(p): out["uniform_model_37a1"][str(p)]["N_p"] for p in PRIMES},
        "model_37a1_at_N_E(300)": {
            str(p): float(model(out["slow_search"]["37a1"]["N_E"]["300"],
                                out["uniform_model_37a1"][str(p)]["N_p"])) for p in PRIMES},
        "model_37a1_at_N_E(1000)": {
            str(p): float(model(out["slow_search"]["37a1"]["N_E"]["1000"],
                                out["uniform_model_37a1"][str(p)]["N_p"])) for p in PRIMES},
    }
    json.dump(out, sys.stdout, indent=1, sort_keys=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
