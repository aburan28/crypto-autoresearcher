"""Independent (sympy) confirmation of two structural facts used in the report:
   (i)  z^131+z^13+z^2+z+1 is irreducible over F_2
   (ii) each G factors over F_2 as (degree-1) * (irreducible of degree 131),
        and that degree-131 factor is exactly the minimal polynomial reported.
Uses sympy's own irreducibility test and factorizer; no code from gf2poly/gfk.
"""
import json
from sympy.polys.galoistools import gf_irreducible_p, gf_factor_sqf, gf_factor, gf_degree, gf_mul, gf_strip
from sympy.polys.domains import ZZ

def packed_to_list(a):
    return [(a >> i) & 1 for i in range(a.bit_length() - 1, -1, -1)]

def list_to_packed(l):
    v = 0
    for i, c in enumerate(reversed(l)):
        if c: v |= 1 << i
    return v

f = (1 << 131) | (1 << 13) | (1 << 2) | (1 << 1) | 1
print('sympy gf_irreducible_p(z^131+z^13+z^2+z+1 over GF(2)) =',
      gf_irreducible_p(packed_to_list(f), 2, ZZ))

d = json.load(open('../out/rederivation_results.json'))
for e in d['attaining']:
    G = int(e['G_packed_hex'], 16)
    lead, facs = gf_factor(packed_to_list(G), 2, ZZ)
    degs = sorted(gf_degree(q) * m for q, m in facs)
    mults = sorted(m for q, m in facs)
    packed = {list_to_packed(q) for q, m in facs}
    reported = {o['minpoly_packed'] for o in e['orbits']}
    # product check
    prod = [1]
    for q, m in facs:
        for _ in range(m):
            prod = gf_mul(prod, q, 2, ZZ)
    ok_prod = gf_strip(prod) == gf_strip(packed_to_list(G))
    irr = all(gf_irreducible_p(q, 2, ZZ) for q, m in facs)
    print(f"  lambda={e['lambda_packed']:4d}: sympy factor degrees={degs} multiplicities={mults} "
          f"all irreducible={irr} product==G:{ok_prod} "
          f"factors match my reported minpolys: {packed == reported}")
