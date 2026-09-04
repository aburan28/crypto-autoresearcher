#!/usr/bin/env python3
"""V4 addendum: MY OWN negative control for MY OWN GF(2) instrument.

Replaces the fixture's 24 generators by random squarefree GF(2) polynomials
with the SAME degree profile (12 quadrics, 12 cubics on 24 variables) and the
SAME per-generator term counts, and re-runs the identical rank/koszul code.
A structural deficit must vanish here; if it did not, the 32 / 1322 would be
predictor bias rather than Semaev structure.  This is NOT the producer's null
arm (whose construction lives in the meter and whose adequacy is joint R4).
"""
import json, random, sys, hashlib
from itertools import combinations
from math import comb
sys.path.insert(0, "/home/user/crypto-autoresearcher/coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-a7eead")

FIX = "/home/user/crypto-autoresearcher/harness/macaulay_fp/fixtures/chained_gf2_n12_t3_seed2026.json"
fx = json.load(open(FIX))
NB = fx["nb"]
DMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 4

profile = []
for g, dd in zip(fx["generators"], fx["eq_degs"]):
    profile.append((dd, len(g)))

def monos_upto(t):
    out = []
    for j in range(0, t + 1):
        for c in combinations(range(NB), j):
            m = 0
            for v in c:
                m |= 1 << v
            out.append(m)
    return out

def all_monos_deg(d):
    out = []
    for c in combinations(range(NB), d):
        m = 0
        for v in c:
            m |= 1 << v
        out.append(m)
    return out

POOL = {d: all_monos_deg(d) for d in range(0, 4)}

def random_system(seed):
    rng = random.Random(seed)
    gens = []
    for (d, nterms) in profile:
        # nterms monomials of degree <= d with at least one of degree exactly d
        pool = []
        for dd in range(0, d + 1):
            pool.extend(POOL[dd])
        s = set(rng.sample(pool, min(nterms, len(pool))))
        top = rng.choice(POOL[d])
        s.add(top)
        gens.append((s, d))
    return gens

def koszul_count(gens, D):
    tot = 0
    for i in range(len(gens)):
        d0 = 2 * gens[i][1]
        if d0 <= D:
            tot += sum(comb(NB, j) for j in range(0, D - d0 + 1))
        for j in range(i + 1, len(gens)):
            d0 = gens[i][1] + gens[j][1]
            if d0 <= D:
                tot += sum(comb(NB, k) for k in range(0, D - d0 + 1))
    return tot

def measure(gens, D):
    cols = monos_upto(D)
    cidx = {m: i for i, m in enumerate(cols)}
    rows = zero = rank = 0
    piv = {}
    for s, dg in gens:
        for m in monos_upto(D - dg):
            acc = set()
            for mo in s:
                acc ^= {m | mo}
            if not acc:
                zero += 1
                continue
            rows += 1
            v = 0
            for mo in acc:
                v |= 1 << cidx[mo]
            while v:
                b = v.bit_length() - 1
                if b in piv:
                    v ^= piv[b]
                else:
                    piv[b] = v
                    rank += 1
                    break
    return rows, len(cols), rank, zero

print("degree profile (deg, terms):", profile)
print("\n%-6s %-4s %-8s %-8s %-8s %-9s %s" % ("seed", "D", "rows", "rank", "koszul", "cum.def", "graded"))
for seed in (7, 11, 13, 17, 19):
    gens = random_system(seed)
    cum = {}
    for D in range(2, DMAX + 1):
        r, c, rk, z = measure(gens, D)
        k = koszul_count(gens, D)
        cum[D] = r - rk - k
        print("%-6d %-4d %-8d %-8d %-8d %-9d %d" % (seed, D, r, rk, k, cum[D], cum[D] - cum.get(D - 1, 0)))
        sys.stdout.flush()
