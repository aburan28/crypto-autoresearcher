#!/usr/bin/env python3
"""Write the descended chained system (t = 3) of a named instance of results/instances_t3.json to a .sys file
(the format read by lfdclose2), with the descent of gen3.py but without searching for a new instance.
usage: mksys3.py instances_t3.json NAME out.sys"""
import json, sys
from gf2n import Field
from s3sys import write_system
recs = {r["name"]: r for r in json.load(open(sys.argv[1]))}
r = recs[sys.argv[2]]
n, k = r["n"], r["k"]
F = Field(n, int(r["modulus_hex"], 16))
Vb = [int(x, 16) for x in r["V_basis_hex"]]; z = int(r["z_hex"], 16); a6 = int(r["a6_hex"], 16)
U = [(1 << i, 1 << i) for i in range(n)]            # (variable bit, field element t^i)
def X(rr): return [(1 << (n + rr * k + j), Vb[j]) for j in range(k)]
def descent():
    def sqv(L): return [(m, F.sq(c)) for m, c in L]
    def bil(A, B, coef, scale=1):
        for ma, ca in A:
            for mb, cb in B:
                c = F.mul(scale, F.mul(ca, cb))
                if c: coef[ma | mb] = coef.get(ma | mb, 0) ^ c
    X1, X2, X3 = X(0), X(1), X(2)
    e1 = {}
    bil(sqv(U), sqv(X1), e1); bil(sqv(U), sqv(X2), e1); bil(sqv(X1), sqv(X2), e1)
    for mu, cu in U:
        for m1, c1 in X1:
            for m2, c2 in X2:
                c = F.mul(cu, F.mul(c1, c2))
                if c: e1[mu | m1 | m2] = e1.get(mu | m1 | m2, 0) ^ c
    e1[0] = e1.get(0, 0) ^ a6
    e2 = {}
    bil(sqv(U), sqv(X3), e2)
    for mu, cu in sqv(U):
        c = F.mul(cu, F.sq(z))
        if c: e2[mu] = e2.get(mu, 0) ^ c
    for mx, cx in sqv(X3):
        c = F.mul(cx, F.sq(z))
        if c: e2[mx] = e2.get(mx, 0) ^ c
    bil(U, X3, e2, z)
    e2[0] = e2.get(0, 0) ^ a6
    return [sorted(m for m, c in e.items() if (c >> b) & 1) for e in (e1, e2) for b in range(n)]
with open(sys.argv[3], "w") as fh:
    write_system(descent(), n + 3 * k, fh)
print("wrote", sys.argv[3], "N =", n + 3 * k, "equations", 2 * n)
