#!/usr/bin/env python3
"""z-free solution counts with closed-form roots of S_3(u, x, y) = 0 as a quadratic in u (odd n).
S_3(u,x,y) = (x+y)^2 u^2 + (xy) u + (xy)^2 + b   [(ab+ac+bc)^2 + abc + b with a=u]"""
import json, sys
from pathlib import Path
def make(n, mod):
    def mul(a, b):
        r = 0
        while b:
            if b & 1: r ^= a
            b >>= 1; a <<= 1
            if a >> n & 1: a ^= mod
        return r
    def pw(a, e):
        r = 1
        while e:
            if e & 1: r = mul(r, a)
            a = mul(a, a); e >>= 1
        return r
    inv = lambda a: pw(a, (1 << n) - 2)
    def tr(a):
        t, s = 0, a
        for _ in range(n): t ^= s; s = mul(s, s)
        return t
    def ht(a):  # half-trace, n odd: sum_{i=0}^{(n-1)/2} a^(2^(2i))
        t, s = 0, a
        for _ in range((n + 1) // 2): t ^= s; s = mul(mul(s, s), mul(s, s)) if False else pw(s, 4)
        return t
    sqrt = lambda a: pw(a, 1 << (n - 1))
    def roots(A, C, Dd):
        if A == 0:
            if C == 0: return None if Dd == 0 else ()
            return (mul(Dd, inv(C)),)
        if C == 0: return (sqrt(mul(Dd, inv(A))),)
        t = mul(mul(Dd, A), inv(mul(C, C)))
        if tr(t): return ()
        w = ht(t); k = mul(C, inv(A))
        return (mul(k, w), mul(k, w ^ 1))
    return mul, roots
def run(path):
    cell = json.load(open(path)); m = cell.get("m", 3); n, k = cell["n"], cell["k"]
    mul, roots = make(n, cell["modulus"]); b = cell["b"]; basis = cell["basis"]
    V = []
    for c in range(1 << k):
        v = 0
        for i in range(k):
            if c >> i & 1: v ^= basis[i]
        V.append(v)
    def R(x, y):
        s = x ^ y; p = mul(x, y)
        r = roots(mul(s, s), p, mul(p, p) ^ b)
        if r is None: raise SystemExit("degenerate: every u")
        return r
    st = {}
    for x0 in V:
        for x1 in V:
            for u in R(x0, x1): st[u] = st.get(u, 0) + 1
    for i in range(1, m - 2):
        nst = {}
        for u, c in st.items():
            for x in V:
                for u2 in R(u, x): nst[u2] = nst.get(u2, 0) + c
        st = nst
    zf = sum(st.values()) * len(V)
    ok = []
    for inst in cell["instances"][:20]:
        z = inst["z"]; tot = 0
        for u, c in st.items():
            tot += c * sum(len(R(u, x)) for x in V if False) if False else c * sum(len(R(x, z)) and (u in R(x, z)) for x in V)
        ok.append(tot == inst["nsol"])
    from math import comb
    N = (m - 2) * n + m * k
    c4 = sum(comb(N, i) for i in range(5)); c3 = sum(comb(N, i) for i in range(4))
    return {"cell": Path(path).stem, "m": m, "n": n, "k": k, "N": N, "zfree": zf, "cols3": c3, "cols4": c4,
            "log2_cols4_over_zfree": round(__import__("math").log2(c4 / zf), 2), "label_check": all(ok), "checked": len(ok)}
if __name__ == "__main__":
  for p in sys.argv[1:]:
    print(json.dumps(run(p)), flush=True)
