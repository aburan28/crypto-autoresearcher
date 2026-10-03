#!/usr/bin/env python3
"""Check the hypotheses (G1), (G2) of Proposition 2.6 for instances in a JSON list
(fields: n, modulus_hex|f, z_hex|xR, V_basis_hex|basis).
(G1): z^{-1}K_0 cap (V.V)^perp = 0   (no mu != 0 with Tr(z mu) = 0 and Tr(mu v_i v_j) = 0 for all i, j)
(G2): no mu with Tr(z mu) = 0 and Tr(mu v_i v_j) = Tr(v_i) Tr(v_j) for all i, j.
Also reports whether V is inside ker Tr. usage: g1g2_check.py instances.json"""
import json, sys

def check(n, f, z, basis):
    def mul(a, b):
        r = 0
        while b:
            if b & 1: r ^= a
            a <<= 1; b >>= 1
        for d in range(r.bit_length() - 1, n - 1, -1):
            if (r >> d) & 1: r ^= f << (d - n)
        return r
    def tr(a):
        t = a; s = a
        for _ in range(n - 1):
            s = mul(s, s); t ^= s
        return t & 1
    k = len(basis)
    # linear functionals of mu: mu -> Tr(c mu) is represented by the row vector (Tr(c * t^i))_i
    def row(c):
        return sum(tr(mul(c, 1 << i)) << i for i in range(n))
    eqs = [(row(z), 0)]
    tv = [tr(v) for v in basis]
    for i in range(k):
        for j in range(i, k):
            eqs.append((row(mul(basis[i], basis[j])), tv[i] & tv[j]))
    # Gaussian elimination on augmented rows (bit n = rhs)
    piv = {}
    inconsistent = False
    for r, b in eqs:
        x = r | (b << n)
        while x & ((1 << n) - 1):
            hb = (x & ((1 << n) - 1)).bit_length() - 1
            if hb in piv: x ^= piv[hb]
            else: piv[hb] = x; break
        else:
            if x >> n: inconsistent = True
    rank = len(piv)
    g1 = (rank == n)            # homogeneous system has only the zero solution
    g2 = inconsistent or not g1 and False
    # (G2) holds iff the inhomogeneous system has no solution
    g2 = inconsistent
    return g1, g2, all(t == 0 for t in tv)

data = json.load(open(sys.argv[1]))
ok = True
for d in data:
    n = d["n"]; f = int(d.get("modulus_hex", format(d.get("f", 0), "x")), 16)
    z = int(d.get("z_hex", format(d.get("xR", 0), "x")), 16)
    basis = [int(b, 16) for b in d["V_basis_hex"]] if "V_basis_hex" in d else d["basis"]
    g1, g2, inK0 = check(n, f, z, basis)
    applies = g1 and (inK0 or g2)        # (G2) is only required when V is not inside ker Tr
    d["prop26_hypotheses"] = applies
    ok &= applies
    print(f"{d.get('name', d.get('file'))}: G1={g1} G2={'n/a' if inK0 else g2} V_in_kerTr={inK0} Prop2.6_applies={applies}")
print("Prop 2.6 hypotheses hold on every instance" if ok else "Prop 2.6 hypotheses fail on some instances (see list)")
