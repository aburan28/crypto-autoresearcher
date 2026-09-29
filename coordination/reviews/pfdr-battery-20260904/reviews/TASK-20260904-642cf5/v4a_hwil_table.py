#!/usr/bin/env python3
"""V4(a): independent recomputation of the H-WIL rank table.

For s = 2..8, every j with j + 2 <= s, p in {4099, 65537}, and both linear forms
ell = sum 2^i a_i ('digit') and ell = sum a_i ('unit'): the rank over F_p of
multiplication by ell^2 from degree j to degree j + 2 on F_p[a_1..a_s]/(a_i^2).
Compared with min(binom(s, j), binom(s, j+2)).  My own elimination; a sympy
DomainMatrix cross-check on every cell.
"""
import itertools, json
from math import comb
from sympy import GF
from sympy.polys.matrices import DomainMatrix

def rank_mod_p(rows, p):
    M = [list(r) for r in rows]
    if not M or not M[0]: return 0
    r = 0
    for c in range(len(M[0])):
        piv = next((i for i in range(r, len(M)) if M[i][c] % p), None)
        if piv is None: continue
        M[r], M[piv] = M[piv], M[r]
        inv = pow(M[r][c], p - 2, p)
        M[r] = [x * inv % p for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] % p:
                f = M[i][c] % p
                M[i] = [(x - f * y) % p for x, y in zip(M[i], M[r])]
        r += 1
        if r == len(M): break
    return r

rows_out, below, sq = [], [], []
for p in (4099, 65537):
    for s in range(2, 9):
        for name, coeffs in (("digit", [pow(2, i, p) for i in range(s)]),
                             ("unit", [1] * s)):
            # ell^2 in F_p[a]/(a_i^2): only cross terms survive, 2 c_i c_k a_i a_k
            ell2 = {}
            for i, k in itertools.combinations(range(s), 2):
                ell2[frozenset((i, k))] = 2 * coeffs[i] * coeffs[k] % p
            for j in range(0, s - 1):
                src = [frozenset(c) for c in itertools.combinations(range(s), j)]
                dst = [frozenset(c) for c in itertools.combinations(range(s), j + 2)]
                idx = {m: n for n, m in enumerate(dst)}
                M = []
                for mono in src:
                    row = [0] * len(dst)
                    for pair, c in ell2.items():
                        if pair & mono:          # a_i^2 = 0 kills overlapping products
                            continue
                        row[idx[mono | pair]] = (row[idx[mono | pair]] + c) % p
                    M.append(row)
                mine = rank_mod_p(M, p)
                theirs = DomainMatrix([[GF(p)(x) for x in r] for r in M],
                                      (len(M), len(dst)), GF(p)).rank()
                exp = min(comb(s, j), comb(s, j + 2))
                cell = dict(p=p, s=s, j=j, ell=name, rank=mine, sympy_rank=theirs,
                            expected=exp, full_rank=(mine == exp),
                            square_map=(j + 2 == s - j))
                rows_out.append(cell)
                if mine != exp: below.append(cell)
                if cell["square_map"]: sq.append(cell)

print("cells computed:", len(rows_out))
print("my rank == sympy rank on every cell:", all(c["rank"] == c["sympy_rank"] for c in rows_out))
print("cells at rank min(C(s,j), C(s,j+2)):", sum(c["full_rank"] for c in rows_out), "of", len(rows_out))
print("cells below the maximum:", below)
print("square maps (j + 2 = s - j):", len(sq), "-- all full rank:", all(c["full_rank"] for c in sq))
for c in sq:
    print(f"   p={c['p']:5d} s={c['s']} j={c['j']} ell={c['ell']:5s} rank={c['rank']} expected={c['expected']}")
print()
print("table (p=4099, digit): " + ", ".join(f"s{c['s']}j{c['j']}={c['rank']}/{c['expected']}"
      for c in rows_out if c['p'] == 4099 and c['ell'] == 'digit'))
print("table (p=4099, unit ): " + ", ".join(f"s{c['s']}j{c['j']}={c['rank']}/{c['expected']}"
      for c in rows_out if c['p'] == 4099 and c['ell'] == 'unit'))
print("table (p=65537,digit): " + ", ".join(f"s{c['s']}j{c['j']}={c['rank']}/{c['expected']}"
      for c in rows_out if c['p'] == 65537 and c['ell'] == 'digit'))
print("table (p=65537,unit ): " + ", ".join(f"s{c['s']}j{c['j']}={c['rank']}/{c['expected']}"
      for c in rows_out if c['p'] == 65537 and c['ell'] == 'unit'))
json.dump(rows_out, open("/home/user/crypto-autoresearcher/coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-642cf5/v4a_hwil_table.json", "w"), indent=1)
