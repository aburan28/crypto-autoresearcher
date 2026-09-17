"""Tie (4) and (5) together independently: multiply out prod_{x in orbit} (X - x)
over K using sympy arithmetic and check it equals the reported minimal polynomial
(and in particular has coefficients in F_2).  Uses only sympy for the K-arithmetic.
"""
import json
from sympy.polys.galoistools import gf_mul, gf_rem, gf_add, gf_strip
from sympy.polys.domains import ZZ

N = 131
F_EXPS = [131, 13, 2, 1, 0]
fa = [0] * (N + 1)
for e in F_EXPS:
    fa[N - e] = 1                 # highest-degree-first

def kmul(a, b):
    return gf_rem(gf_mul(a, b, 2, ZZ), fa, 2, ZZ)

def fromvec(v):
    return gf_strip([int(c) for c in reversed(v)])

d = json.load(open('../out/rederivation_results.json'))
for e in d['attaining']:
    for o in e['orbits']:
        if o['orbit_size'] != 131:
            continue
        roots = [fromvec(v) for v in o['roots_bits_lsb_first']]
        # poly[i] = coefficient of X^i, each coefficient an element of K
        poly = [[1]]
        for r in roots:
            new = [[] for _ in range(len(poly) + 1)]
            for i, c in enumerate(poly):
                new[i + 1] = gf_add(new[i + 1], c, 2, ZZ)      # * X
                new[i] = gf_add(new[i], kmul(c, r), 2, ZZ)     # + (-r)*c  (char 2)
            poly = new
        inF2 = all(gf_strip(c) in ([], [1]) for c in poly)
        packed = 0
        for i, c in enumerate(poly):
            if gf_strip(c) == [1]:
                packed |= 1 << i
        print(f"  lambda={e['lambda_packed']:4d}: prod over the 131-orbit of (X - x) has all "
              f"coefficients in F_2: {inF2};  equals reported minpoly: "
              f"{packed == o['minpoly_packed']}  (0x{packed:x})")
