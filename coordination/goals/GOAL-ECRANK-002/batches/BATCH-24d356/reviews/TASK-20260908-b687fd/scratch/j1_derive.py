#!/usr/bin/env python3
"""J1 control-family derivation, exact (fractions.Fraction, integer poly algebra).

Reconstructs the R7 known-false d=(1..1) b-tuples from seed 760812 EXACTLY as
run_r7() does, then derives, from the M2 mechanism statement alone:
  delta (Lagrange interpolant of d_i), g (Mestre trunc-sqrt = polysqrt_trunc),
  s = delta*g^2 mod p, deg s, at n=6 and n=8.
No floating point. No ops counting.
"""
import os, sys, json, random
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "../../../../../../../.."))
SRC = os.path.join(REPO, "experiments/EXP-ECRANK-73275e/source")
sys.path.insert(0, SRC)
os.environ.setdefault("ECRANK_REPO_ROOT", REPO)

import ecrank_engine as E
import construct as CT

B_INTS = CT.B_INTS
print("B_INTS =", B_INTS)
print("len(B_INTS) =", len(B_INTS))

def reconstruct_r7_tuples():
    """Exactly as run_r7(): one RNG stream, n=6 first (8 tuples x 4), then n=8 (8 x 6)."""
    rng = random.Random(760812)
    out = {}
    for n in (6, 8):
        per = []
        for bi in range(8):
            rest = rng.sample(B_INTS, n - 2)
            b = [Fr(0), Fr(1)] + [Fr(x) for x in rest]
            per.append(b)
        out[n] = per
    return out

tuples = reconstruct_r7_tuples()

def poly_str(p):
    # p is a list of Fr, low-to-high
    terms = []
    for i, c in enumerate(p):
        if c == 0:
            continue
        terms.append("%s*x^%d" % (c, i))
    return " + ".join(reversed(terms)) if terms else "0"

print("\n" + "="*80)
print("N = 6  (k = 3, g monic degree 3, s = g^2 - p, deg s <= 2 by construction)")
print("="*80)
for bi, b in enumerate(tuples[6]):
    p, g, s = E.mestre_polys(list(b))
    deg_s = len(s) - 1
    # delta at d=(1..1) is the constant 1
    delta = E.lagrange_interp([Fr(x) for x in b], [Fr(1)]*6)
    print("\n--- b_index %d ---" % bi)
    print("b =", [str(x) for x in b])
    print("p =", poly_str(p))
    print("g =", poly_str(g))
    print("delta =", poly_str(delta))
    print("s = g^2 - p =", poly_str(s))
    print("deg s =", deg_s)
    # check s(b_i) == g(b_i)^2
    ok = all(E.peval(s, Fr(x)) == E.peval(g, Fr(x))**2 for x in b)
    print("s(b_i)==g(b_i)^2 for all i:", ok)
    # run the actual build_instance to confirm the rejection reason
    r = [E.peval(g, x) for x in b]
    inst, why = E.build_instance(list(b), [1]*6, r, 6)
    print("build_instance -> built=%s reason=%s" % (inst is not None, why))

print("\n" + "="*80)
print("N = 8  (k = 4, g monic degree 4, s = g^2 - p, deg s <= 3 by construction)")
print("="*80)
for bi, b in enumerate(tuples[8]):
    p, g, s = E.mestre_polys(list(b))
    deg_s = len(s) - 1
    delta = E.lagrange_interp([Fr(x) for x in b], [Fr(1)]*8)
    print("\n--- b_index %d ---" % bi)
    print("b =", [str(x) for x in b])
    print("p =", poly_str(p))
    print("g =", poly_str(g))
    print("delta =", poly_str(delta))
    print("s = g^2 - p =", poly_str(s))
    print("deg s =", deg_s)
    ok = all(E.peval(s, Fr(x)) == E.peval(g, Fr(x))**2 for x in b)
    print("s(b_i)==g(b_i)^2 for all i:", ok)
    r = [E.peval(g, x) for x in b]
    inst, why = E.build_instance(list(b), [1]*8, r, 8)
    print("build_instance -> built=%s reason=%s" % (inst is not None, why))
