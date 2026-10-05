#!/usr/bin/env python3
"""Generate small window-shaped instances with the REPOSITORY generator (boolsys.generate / eq4sys.generate,
read from the code directory, unmodified) and write them as plain files for the scratch tools.
Also computes |V| by an independent truth-table method (ANF -> evaluation by Moebius transform over all 2^N points).
Usage: gen_small.py OUTDIR family n m t k draw [B_mode] [subspace]
scratch (not an experiment run)."""
import sys, json, os, hashlib
import numpy as np
sys.path.insert(0, os.environ["CODE"])
import boolsys, eq4sys
SEEDS = [20260913101, 20260913102, 20260913103, 20260913104, 20260913105]

def zeros_count(N, eqs):
    """|V| = number of x in {0,1}^N with every equation zero. Truth table of each equation by the Moebius transform."""
    ok = np.ones(1 << N, dtype=bool)
    for e in eqs:
        t = np.zeros(1 << N, dtype=np.uint8)
        for m in e:
            t[m] ^= 1
        for i in range(N):
            v = t.reshape(-1, 2, 1 << i)
            v[:, 1, :] ^= v[:, 0, :]
        ok &= (t == 0)
    return int(ok.sum()), ok

def build(family, n, m, t, k, draw, B_mode="B_random", subspace="low_degree_polynomial"):
    seed = SEEDS[draw % 5]
    if family == "chained":
        return boolsys.generate(n, m, t, k, B_mode, subspace, seed, draw)
    if family == "eq4":
        return eq4sys.generate(n, m, k, B_mode, subspace, seed, draw)
    if family == "null":
        base = boolsys.generate(n, m, t, k, B_mode, subspace, seed, draw)
        return boolsys.matched_null(base, seed)
    raise ValueError(family)

if __name__ == "__main__":
    out, family, n, m, t, k, draw = sys.argv[1], sys.argv[2], *map(int, sys.argv[3:8])
    inst = build(family, n, m, t, k, draw)
    N = inst["N"]
    s, _ = zeros_count(N, inst["equations"]) if N <= 26 else (None, None)
    name = f"{family}_n{n}_m{m}_t{t}_k{k}_d{draw}"
    sysd = {"name": name, "N": N, "equations": [sorted(e) for e in inst["equations"]], "V": s,
            "max_degree": max(max((bin(x).count("1") for x in e), default=0) for e in inst["equations"]),
            "system_sha256": boolsys.sha256_of(inst), "n": n, "m": m, "t": t, "k": k, "draw": draw}
    os.makedirs(out, exist_ok=True)
    json.dump(sysd, open(f"{out}/{name}.json", "w"))
    # plain text for the C++ reference: N, D, ngens, then per generator: count masks...
    with open(f"{out}/{name}.sys", "w") as fh:
        fh.write(f"{N} {len(sysd['equations'])}\n")
        for e in sysd["equations"]:
            fh.write(f"{len(e)} " + " ".join(map(str, e)) + "\n")
    print(name, "N", N, "eqs", len(inst["equations"]), "maxdeg", sysd["max_degree"], "|V|", s)
