#!/usr/bin/env python3
"""W3(a) variants: which weakening of the polynomial-ring Macaulay block breaks the equivalence with the Boolean single-level span?
V1 full (field-equation multiples with every multiplier, non-square-free multipliers for generators)
V2 square-free multipliers only (for generators and for field equations)
V3 field-equation rows WITHOUT multipliers (the N rows x_i^2+x_i only)
V4 no field-equation rows at all (implicit reduction only in the comparison)
For square-free generators, compare (i) pi(row space) with the Boolean single-level span B1 and (ii) the square-free leading monomials with LM(B1)."""
import sys, os, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ref_closure import *
from gen_systems import system
import w3_experiments as w
D = 4
def rows_variant(gens_P, N, variant):
    mons = sorted(w.exps_upto(N, D), key=w.pkey); idx = {e: i for i, e in enumerate(mons)}
    out = []
    def prod(mu, g):
        s = {}
        for e in g:
            m = w.mul_exp(mu, e); s[m] = s.get(m, 0) ^ 1
        return {m for m, v in s.items() if v}
    sfonly = (variant == 'V2')
    for g in gens_P:
        dg = max(sum(e) for e in g)
        for mu in w.exps_upto(N, D - dg):
            if sfonly and any(x > 1 for x in mu): continue
            out.append(prod(mu, g))
    if variant in ('V1', 'V2'):
        for i in range(N):
            f = [tuple(2 if j == i else 0 for j in range(N)), tuple(1 if j == i else 0 for j in range(N))]
            for mu in w.exps_upto(N, D - 2):
                if sfonly and any(x > 1 for x in mu): continue
                out.append(prod(mu, f))
    elif variant == 'V3':
        for i in range(N):
            out.append({tuple(2 if j == i else 0 for j in range(N)), tuple(1 if j == i else 0 for j in range(N))})
    return mons, idx, out
rng = random.Random(8); res = {v: dict(pi_equal=0, lm_equal=0, n=0) for v in ['V1', 'V2', 'V3', 'V4']}
for trial in range(60):
    N = rng.choice([4, 5, 6]); M = rng.randint(2, N + 1); fam = rng.choice(['quad', 'sparsequad', 'planted'])
    gens = system(fam, N, M, trial)
    if not gens: continue
    gens_P = [w.poly_from_B(g, N) for g in gens]
    C1 = Closure(gens, N, D, gens_only=True).run(); S = C1.S; lmB1 = sorted(C1.lm_set())
    for v in res:
        mons, idx, rows = rows_variant(gens_P, N, v)
        U = w.echelon_P(rows, idx)
        piU = w.span_rank_and_lm_B([w.pi_reduce_vec(U[h], mons, S) for h in U])
        both = dict(piU)
        for h, b in C1.basis.items():
            x = b
            while x:
                hh = x.bit_length() - 1
                if hh in both: x ^= both[hh]
                else: both[hh] = x; break
        pi_eq = (len(both) == len(piU) == len(C1.basis))
        lm_sf = sorted(sum(1 << j for j, x in enumerate(mons[h]) if x) for h in U if all(x <= 1 for x in mons[h]))
        res[v]['n'] += 1; res[v]['pi_equal'] += pi_eq; res[v]['lm_equal'] += (lm_sf == lmB1)
print(json.dumps(res))
json.dump(res, open(sys.argv[1], 'w'), indent=1)
