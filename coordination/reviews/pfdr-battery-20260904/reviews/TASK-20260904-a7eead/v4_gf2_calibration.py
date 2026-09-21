#!/usr/bin/env python3
"""V4: independent recomputation of the binary n = 12 calibration integers.

Own GF(2) code (Python-int bitsets); no import of harness/macaulay_fp.
Input: the meter's COMMITTED fixture json only (generator monomial lists).

Boolean ring on nb = 24 squarefree variables (x^2 = x).
rows(D)    = cumulative { m f_i : deg m <= D - deg f_i }, zero products dropped+counted
columns(D) = all squarefree monomials of degree <= D
koszul(D)  = cumulative count of the CLASSICAL trivial syzygies:
             Koszul pairs (f_i, f_j), i<j, of degree deg f_i + deg f_j, and the
             Frobenius relations f_i^2 = f_i (p = 2, squarefree) of degree
             2 deg f_i, each counted with its own multiplier monomials of
             degree <= D - d0.
deficit_cumulative(D) = rows(D) - rank(D) - koszul(D)
deficit_graded(D)     = deficit_cumulative(D) - deficit_cumulative(D-1)
"""
import hashlib, json, sys, time
from itertools import combinations
from math import comb

FIX = "/home/user/crypto-autoresearcher/harness/macaulay_fp/fixtures/chained_gf2_n12_t3_seed2026.json"
DECLARED_SHA = "62d89109f94ef658885ddb5289504df159de01ee4341852b34349d01724bf8e5"
DMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 4

raw = open(FIX, "rb").read()
got = hashlib.sha256(raw).hexdigest()
print("fixture sha256:", got, "MATCHES DECLARED" if got == DECLARED_SHA else "MISMATCH")
assert got == DECLARED_SHA
fx = json.loads(raw)
NB = fx["nb"]
print("n =", fx["n"], "k =", fx["k"], "t =", fx["t"], "nb =", NB,
      "| generators:", len(fx["generators"]),
      "| eq_degs:", {d: fx["eq_degs"].count(d) for d in sorted(set(fx["eq_degs"]))})
print("fixture system_hash:", fx["system_hash"])
print("fixture archived_system_hash:", fx["archived_system_hash"],
      "| matches_archived_system_hash:", fx["matches_archived_system_hash"])

# --- generators as GF(2) sets of squarefree masks -----------------------------
gens = []
for g, dd in zip(fx["generators"], fx["eq_degs"]):
    s = set()
    for mon in g:
        mask = 0
        for v in mon:
            mask |= 1 << v
        s ^= {mask}                     # GF(2): repeated monomial cancels
    d = max((bin(m).count("1") for m in s), default=0)
    assert d == dd, (d, dd)
    gens.append((s, dd))
print("generator degrees recomputed from the monomial lists:",
      {d: [x[1] for x in gens].count(d) for d in sorted({x[1] for x in gens})})
print("generator term counts:", [len(s) for s, _ in gens])

# --- monomial bases -----------------------------------------------------------
def monos_upto(t):
    out = []
    for j in range(0, t + 1):
        for c in combinations(range(NB), j):
            m = 0
            for v in c:
                m |= 1 << v
            out.append(m)
    return out

def ncols(D):
    return sum(comb(NB, j) for j in range(0, D + 1))

# --- koszul (classical trivial syzygy) count ---------------------------------
def koszul_count(D):
    tot = 0
    for i in range(len(gens)):
        d0 = 2 * gens[i][1]                      # Frobenius f^2 = f
        if d0 <= D:
            tot += sum(comb(NB, j) for j in range(0, D - d0 + 1))
        for j in range(i + 1, len(gens)):        # Koszul pair
            d0 = gens[i][1] + gens[j][1]
            if d0 <= D:
                tot += sum(comb(NB, k) for k in range(0, D - d0 + 1))
    return tot

# --- build + rank -------------------------------------------------------------
def rank_at(D, verbose=True):
    cols = monos_upto(D)
    cidx = {m: i for i, m in enumerate(cols)}
    assert len(cols) == ncols(D)
    t0 = time.time()
    rows = 0
    zero = 0
    pivots = {}
    rank = 0
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
                if b in pivots:
                    v ^= pivots[b]
                else:
                    pivots[b] = v
                    rank += 1
                    break
    if verbose:
        print("   [%.1f s]" % (time.time() - t0), end=" ")
    return rows, len(cols), rank, zero

print("\n%-4s %-8s %-8s %-8s %-8s %-9s %-9s %s" %
      ("D", "rows", "cols", "rank", "koszul", "cum.def", "graded", "zero_rows"))
cum = {}
for D in range(2, DMAX + 1):
    r, c, rk, z = rank_at(D)
    k = koszul_count(D)
    cum[D] = r - rk - k
    gr = cum[D] - cum.get(D - 1, 0)
    print("%-4d %-8d %-8d %-8d %-8d %-9d %-9d %d" % (D, r, c, rk, k, cum[D], gr, z))
    sys.stdout.flush()

print("\nn_q (quadrics) =", sum(1 for _, d in gens if d == 2),
      "| Frobenius count at D=4 =", sum(1 for _, d in gens if d == 2),
      "| binom(n_q,2) =", comb(sum(1 for _, d in gens if d == 2), 2),
      "| sum =", comb(sum(1 for _, d in gens if d == 2), 2) + sum(1 for _, d in gens if d == 2))
print("deficit_cumulative D2..D%d:" % DMAX, [cum[D] for D in range(2, DMAX + 1)])
gradl = [cum[D] - cum.get(D - 1, 0) for D in range(2, DMAX + 1)]
print("deficit_graded     D2..D%d:" % DMAX, gradl)
print("KN-FIND-006 integers: deficit(3) = 1, deficit(4) = 8k - 1 = 31 (k = 4);"
      " cumulative at D=4 = 8k = 32")
