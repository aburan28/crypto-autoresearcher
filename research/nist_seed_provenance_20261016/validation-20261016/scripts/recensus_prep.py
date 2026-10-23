#!/usr/bin/env python3
"""Prepare inputs for the independent early-abort re-census (and the J3 full counts).

For each run and each candidate block of MY Q4 set (out/q4_candidates_<t>.txt), compute
c = X9.62(seed) and bsq = -27/c mod p. The GP driver derives b0 itself
(bsq^((p+1)/4) when p = 3 mod 4, else a square root) and builds the twist as
y^2 = x^3 - 3 d^2 x + d^3 b0 with d the smallest positive non-residue mod p
(a model different from y^2 = x^3 - 3x - b0, isomorphic to it when p = 3 mod 4).
Usage: recensus_prep.py <W> -> tmp/shard_<j>.gp, j = 0..W-1, rows interleaved by cost.
       recensus_prep.py resume <W> <tag> -> tmp/shard<tag>_<j>.gp with only rows not yet
       present (as a complete "t i N0 Nt" line) in out/recensus_raw_*.txt.
       recensus_prep.py rows <listfile> <outfile> -> one GP input for given "t i" rows.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

P = load_params()
TMP = os.path.join(ROOT, "tmp")
os.makedirs(TMP, exist_ok=True)


def smallest_nonresidue(p):
    d = 2
    while pow(d, (p - 1) // 2, p) != p - 1:
        d += 1
    return d


def bsq_for(t, field, i1):
    p = P[FIELD_CURVE[field]]["p"]
    s = drand48_byte_stream(t, 20 * i1)[-20:]
    c = x962_c(s, p.bit_length())
    return (-27 * pow(c, -1, p)) % p


def runs_info():
    info = {}
    for t, field, count in RUNS:
        p = P[FIELD_CURVE[field]]["p"]
        cand = [int(x) for x in open(os.path.join(ROOT, "out", f"q4_candidates_{t}.txt"))]
        info[t] = (field, p, smallest_nonresidue(p), cand)
    return info


def write_gp(path, items):
    """items: list of (t, p, d, i, bsq). GP vector of [t, p, d, i, bsq]."""
    with open(path, "w") as f:
        f.write("[\\\n")
        f.write(",\\\n".join(f"[{t},{p},{d},{i},{b}]" for t, p, d, i, b in items))
        f.write("]\n")


if __name__ == "__main__":
    info = runs_info()
    if sys.argv[1] == "rows":
        items = []
        for line in open(sys.argv[2]):
            t, i = map(int, line.split())
            field, p, d, cand = info[t]
            items.append((t, p, d, i, bsq_for(t, field, i)))
        write_gp(sys.argv[3], items)
    else:
        resume = sys.argv[1] == "resume"
        if resume:
            import glob
            done = set()
            for fn in glob.glob(os.path.join(ROOT, "out", "recensus_raw_*.txt")):
                for line in open(fn):
                    f = line.split()
                    if len(f) == 4 and f[2] != "ERR":
                        done.add((int(f[0]), int(f[1])))
            W, tag = int(sys.argv[2]), sys.argv[3]
        else:
            done, W, tag = set(), int(sys.argv[1]), ""
        allrows = []
        for t, (field, p, d, cand) in info.items():
            stream = drand48_byte_stream(t, 20 * max(cand))
            for i in cand:
                if (t, i) in done:
                    continue
                c = x962_c(stream[20 * (i - 1):20 * i], p.bit_length())
                allrows.append((p.bit_length(), t, p, d, i, (-27 * pow(c, -1, p)) % p))
        allrows.sort(key=lambda r: (-r[0], r[1], r[4]))   # big fields first, interleaved
        shards = [[] for _ in range(W)]
        for k, r in enumerate(allrows):
            shards[k % W].append(r[1:])
        for j in range(W):
            write_gp(os.path.join(TMP, f"shard{tag}_{j}.gp"), shards[j])
        print("rows", len(allrows), "shards", [len(s) for s in shards],
              "nonresidues", {t: v[2] for t, v in info.items()})
