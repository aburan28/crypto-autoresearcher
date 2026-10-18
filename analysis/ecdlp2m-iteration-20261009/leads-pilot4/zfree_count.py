#!/usr/bin/env python3
"""Exact solution count of the target-independent (z-free) part of each chained system, by
enumeration of the x-assignments and the u-chain (brute force over u in F_2^n). Also counts the
full-system solutions as a check against the instance labels."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE / "vendor"))
import boolsys

def gf(n, mod):
    def mul(a, b):
        r = 0
        while b:
            if b & 1: r ^= a
            b >>= 1; a <<= 1
            if a >> n & 1: a ^= mod
        return r
    return mul

def run(cellname):
    cell = json.load(open(HERE / "instances" / f"{cellname}.json"))
    m = cell.get("m", 3); n, k = cell["n"], cell["k"]; mod = cell["modulus"]; b = cell["b"]
    mul = gf(n, mod); basis = cell["basis"]
    V = []
    for c in range(1 << k):
        v = 0
        for i in range(k):
            if c >> i & 1: v ^= basis[i]
        V.append(v)
    def s3(a, bb, c):  # (ab+ac+bc)^2 + abc + b  (binary curve y^2+xy=x^3+a2 x^2+b)
        t = mul(a, bb) ^ mul(a, c) ^ mul(bb, c)
        return mul(t, t) ^ mul(mul(a, bb), c) ^ b
    # verify s3 matches boolsys on a random point would need boolsys internals; check via labels below
    F = range(1 << n)
    # roots table: R[(x,y)] = list of u with s3(u,x,y)=0
    from functools import lru_cache
    @lru_cache(None)
    def roots(x, y):
        return tuple(u for u in F if s3(u, x, y) == 0)
    # z-free: chain over x0..x_{m-2} producing u_{m-3}; x_{m-1} free (k bits)
    # states: dict u -> count after processing x0..x_{i+1}
    st = {}
    for x0 in V:
        for x1 in V:
            for u in roots(x0, x1): st[u] = st.get(u, 0) + 1
    for i in range(1, m - 2):
        nst = {}
        for u, c in st.items():
            for x in V:
                for u2 in roots(u, x): nst[u2] = nst.get(u2, 0) + c
        st = nst
    zfree = sum(st.values()) * len(V)
    # full system for a few targets: count = sum_u st[u] * #{x in V: s3(u,x,z)=0}
    chk = []
    for inst in cell["instances"][:12]:
        z = inst["z"]; tot = 0
        for u, c in st.items():
            tot += c * sum(1 for x in V if s3(u, x, z) == 0)
        chk.append(tot == inst["nsol"])
    return {"cell": cellname, "m": m, "n": n, "k": k, "zfree_solutions": zfree, "distinct_u_end": len(st), "label_check": all(chk), "checked": len(chk)}

if __name__ == "__main__":
    for c in sys.argv[1:]:
        print(json.dumps(run(c)), flush=True)
