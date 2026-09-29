#!/usr/bin/env python3
"""Exact algebra for the n=8 d=(1..1) closed-form control objects.
For the shortfall tuples (b_index 0,1,7) and one total-7 control (b_index 2):
  p = prod(x - b_i) monic deg 8; delta = 1; g = polysqrt_trunc(p,4) monic deg 4
  with deg(p - g^2) <= 3; s = g^2 - p; deg s; forcing identity s(b_i)=g(b_i)^2;
  Mestre relation sum P_i = O in the Weierstrass model.
All exact (fractions.Fraction). Read-only import of committed source."""
import os, sys, json
from fractions import Fraction as Fr

ROOT = "/Volumes/SSD990/llm/tmp/opencode/review-e3cf55-20260909"
SRC = os.path.join(ROOT, "experiments", "EXP-ECRANK-73275e", "source")
sys.path.insert(0, SRC)
os.environ.setdefault("ECRANK_REPO_ROOT", ROOT)
import ecrank_engine as E

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "b_tuples.json")) as f:
    BT = json.load(f)
N8 = [[Fr(x) for x in row] for row in BT["n8"]]

def w_add(a2, a4, a6, P, Q):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2:
        if y1 + y2 == 0: return None
        lam = (3*x1*x1 + 2*a2*x1 + a4) / (2*y1)
    else:
        lam = (y2 - y1) / (x2 - x1)
    x3 = lam*lam - a2 - x1 - x2
    y3 = lam*(x1 - x3) - y1
    return (x3, y3)

def w_sum(a2, a4, a6, pts):
    R = None
    for P in pts:
        R = w_add(a2, a4, a6, R, P)
    return R

def poly_str(p):
    return " + ".join("%s*x^%d" % (str(c), i) for i, c in enumerate(p) if c != 0) or "0"

report = {}
for bi in (0, 1, 7, 2):
    b = N8[bi]
    p, g, s = E.mestre_polys(list(b))
    deg_p = len(p) - 1
    deg_g = len(g) - 1
    deg_s = len(s) - 1
    # deg(p - g^2)
    g2 = E.pmul(g, g)
    diff = E.psub(p, g2)
    deg_diff = len(diff) - 1
    # forcing identity
    r = [E.peval(g, x) for x in b]
    forcing_ok = all(E.peval(s, Fr(b[i])) == r[i]*r[i] for i in range(8))
    # r_i nonzero
    r_nonzero = all(r[i] != 0 for i in range(8))
    # nonsingularity: discriminant of s
    disc = E.poly_disc(s)
    # Weierstrass model + points
    ainv, Wpts = E.cubic_to_weierstrass(s, [(b[i], r[i]) for i in range(8)])
    a2, a4, a6 = Fr(ainv[1]), Fr(ainv[3]), Fr(ainv[4])
    # on-curve recheck
    oncurve = all(E.verify_on_curve(ainv, x, y) for x, y in Wpts)
    # Mestre relation: sum P_i = O ?
    S = w_sum(a2, a4, a6, Wpts)
    mestre_sum_O = (S is None)
    # also check sum of the 8 points and the "g - y" relation reading:
    # div(g - v) = sum P_i - 8*O  =>  sum P_i = 8*O = O
    report[bi] = {
        "b": [str(x) for x in b],
        "deg_p": deg_p, "deg_g": deg_g, "deg_s": deg_s,
        "deg_p_minus_g2": deg_diff,
        "g": [str(c) for c in g],
        "s": [str(c) for c in s],
        "r": [str(x) for x in r],
        "forcing_identity_holds": forcing_ok,
        "all_r_nonzero": r_nonzero,
        "disc_s": str(disc),
        "disc_s_nonzero": disc != 0,
        "weierstrass_ainv": [int(z) for z in ainv],
        "weierstrass_points": [[str(x), str(y)] for x, y in Wpts],
        "all_on_curve": oncurve,
        "mestre_sum_of_8_points_is_O": mestre_sum_O,
    }
    print("=== b_index %d ===" % bi)
    print("  b =", [str(x) for x in b])
    print("  deg p=%d  deg g=%d  deg s=%d  deg(p-g^2)=%d" % (deg_p, deg_g, deg_s, deg_diff))
    print("  g =", poly_str(g))
    print("  s =", poly_str(s))
    print("  forcing identity holds:", forcing_ok, " all r nonzero:", r_nonzero)
    print("  disc(s) =", str(disc)[:60], " nonzero:", disc != 0)
    print("  ainv =", [int(z) for z in ainv])
    print("  all 8 Weierstrass pts on curve:", oncurve)
    print("  SUM of 8 points == O (Mestre relation):", mestre_sum_O)
    print()

with open(os.path.join(HERE, "n8_algebra.json"), "w") as f:
    json.dump(report, f, indent=1)
print("wrote n8_algebra.json")
