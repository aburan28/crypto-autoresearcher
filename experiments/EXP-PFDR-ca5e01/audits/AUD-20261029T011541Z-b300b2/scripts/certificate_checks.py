#!/usr/bin/env python3
"""Independent certificate checks for EXP-PFDR-ca5e01 (certificate kind: none; exact counts).

Shares no code with the producer (no import of run.py, check.py, vendor/curve.py, paircount.c).
Uses only: Python ints for the group law, sympy.isprime/sqrt_mod, numpy, and PARI/GP ellcard
(run as a subprocess) for #E(F_p).

Checks, over main-block job records (RUN-PFDR-eb4733/main-jobs.jsonl):
  A. curve: p prime, nonsingular, N = #E(F_p) by PARI ellcard, N prime, Hasse   [sample, 400 curves]
     and curve parameters consistent across all cells at the same (bits, c)       [all records]
  B. structured base: rebuilt from (p,a,b_coef,b,struct_meta) by the specification's rule,
     C(F) recounted by brute force with my own group law, compared with record.struct   [sample]
     (window d=1, GAP d=2,3; b <= BMAX)
  C. plant_internal(L) = C({+-k : 1<=k<=L}) as integer arithmetic (no wrap, N prime >> 4L),
     and L = smallest in [1, b//4] with plant_internal >= 0.30 * mean(null)         [all records]
  D. struct_pairs == pairs == b(b-2)/2                                              [all records]
Usage: certificate_checks.py <experiment_dir> <nsample> <bmax> [bmin]
"""
import json, math, random, subprocess, sys
from collections import Counter
import numpy as np
from sympy import isprime
from sympy.ntheory import sqrt_mod

exp, NS, BMAX = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
BMIN = int(sys.argv[4]) if len(sys.argv) > 4 else 0
main = [json.loads(l) for l in open(exp + "/runs/RUN-PFDR-eb4733/main-jobs.jsonl")]
print("records", len(main))

# ---------- D ---------------------------------------------------------------------
badD = [r for r in main if not (r["pairs"] == r["struct_pairs"] == r["b"] * (r["b"] - 2) // 2)]
print("D pair-count identity violations:", len(badD))

# ---------- A (consistency over all records) ----------------------------------------
cur = {}
inc = 0
for r in main:
    bits = int(r["cell"].split("-")[0][1:])
    k = (bits, r["c"])
    v = (r["p"], r["a"], r["b_coef"], r["N"])
    if cur.setdefault(k, v) != v:
        inc += 1
print("A distinct (bits,c) curves:", len(cur), "inconsistent records:", inc)
for (bits, c), (p, a, bc, N) in cur.items():
    assert p.bit_length() == bits, ((bits, c), p)
rng = random.Random(1234)
sample = rng.sample(sorted(cur), min(NS, len(cur)))
gp_in = "\n".join(
    "E=ellinit([%d,%d],%d);print(isprime(%d),\" \",ellcard(E),\" \",(4*%d^3+27*%d^2)%%%d!=0);" % (cur[k][1], cur[k][2], cur[k][0], cur[k][0], cur[k][1], cur[k][2], cur[k][0])
    for k in sample
)
# note: gp ellinit([a4,a6],p) is short Weierstrass y^2=x^3+a4 x+a6 over F_p
out = subprocess.run(["gp", "-q", "--default", "parisizemax=2G"], input=gp_in + "\nquit\n", capture_output=True, text=True).stdout.split("\n")
out = [l for l in out if l.strip()]
badA = 0
for k, line in zip(sample, out):
    pr, card, nonsing = line.split()
    p, a, bc, N = cur[k]
    ok = (pr == "1" and int(card) == N and nonsing == "1" and isprime(N) and abs(p + 1 - N) <= 2 * math.isqrt(p) + 1)
    if not ok:
        badA += 1
        print("  curve FAIL", k, line, cur[k])
print("A curves checked with PARI ellcard:", len(out), "of", len(sample), "failures:", badA)

# ---------- own elliptic-curve arithmetic ---------------------------------------------
def make_curve(p, a, bc):
    def f(x): return (x * x * x + a * x + bc) % p
    def add(P, Q):
        if P is None: return Q
        if Q is None: return P
        x1, y1 = P; x2, y2 = Q
        if x1 == x2:
            if (y1 + y2) % p == 0: return None
            lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
        else:
            lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
        x3 = (lam * lam - x1 - x2) % p
        return (x3, (lam * (x1 - x3) - y1) % p)
    return f, add

def lifts(f, p, x):
    v = f(x % p)
    if v == 0: return []
    if pow(v, (p - 1) // 2, p) != 1: return []
    y = int(sqrt_mod(v, p))
    return [(x % p, y), (x % p, (p - y) % p)]

def count_pairs(F, add, p):
    """C(F) = sum_{s != O} binom(m_s,2), m_s = #{unordered {P,Q}: P!=Q, Q!=-P, P+Q=s}."""
    assert len(set(F)) == len(F)
    m = Counter()
    n = len(F)
    for i in range(n):
        for j in range(i + 1, n):
            P, Q = F[i], F[j]
            if P[0] == Q[0]:  # Q = -P (same x, distinct points): excluded
                continue
            m[add(P, Q)] += 1
    assert None not in m
    return sum(v * (v - 1) // 2 for v in m.values())

def window_base(p, f, x0, b):
    F, x, used = [], x0, 0
    while len(F) < b:
        F += lifts(f, p, x); x += 1; used += 1
    assert len(F) == b
    return F, used

def gap_base(p, f, x0, w, b, d):
    side = max(2, math.ceil(round(b ** (1.0 / d), 9)))
    F, seen, enum = [], set(), 0
    if d == 2:
        c = 0
        while len(F) < b:
            for a in range(side):
                x = (x0 + a + c * w[0]) % p
                enum += 1
                if x not in seen:
                    seen.add(x); F += lifts(f, p, x)
                if len(F) >= b: break
            c += 1
    else:
        e = 0
        while len(F) < b:
            for c in range(side):
                for a in range(side):
                    x = (x0 + a + c * w[0] + e * w[1]) % p
                    enum += 1
                    if x not in seen:
                        seen.add(x); F += lifts(f, p, x)
                    if len(F) >= b: break
                if len(F) >= b: break
            e += 1
    assert len(F) == b, (len(F), b)
    return F, side, enum

# ---------- B -------------------------------------------------------------------------
cand = [r for r in main if BMIN <= r["b"] <= BMAX]
rng2 = random.Random(99)
bysd = {1: [], 2: [], 3: []}
for r in cand:
    bysd[int(r["cell"][-1])].append(r)
chosen = []
for d in (1, 2, 3):
    chosen += rng2.sample(bysd[d], min(NS // 8, len(bysd[d])))
res = Counter()
mism = []
for r in chosen:
    p, a, bc, b = r["p"], r["a"], r["b_coef"], r["b"]
    f, add = make_curve(p, a, bc)
    d = int(r["cell"][-1]); m = r["struct_meta"]
    if d == 1:
        F, used = window_base(p, f, m["x0"], b)
        meta_ok = used == m["span"]
    else:
        F, side, enum = gap_base(p, f, m["x0"], m["w"], b, d)
        meta_ok = (side == m["side"] and enum == m["enumerated"])
    # on-curve and symmetric
    assert all((y * y - f(x)) % p == 0 for x, y in F)
    assert set(F) == {(x, (p - y) % p) for x, y in F}
    cnt = count_pairs(F, add, p)
    ok = cnt == r["struct"]
    res[(d, "count_match" if ok else "COUNT_MISMATCH")] += 1
    res[(d, "meta_match" if meta_ok else "META_MISMATCH")] += 1
    if not ok or not meta_ok:
        mism.append((r["cell"], r["c"], cnt, r["struct"], meta_ok))
print("B structured-base recounts (own group law, brute force):", sorted(res.items()))
print("B units:", [(r["cell"], r["c"], r["b"]) for r in chosen][:60])
print("B mismatches:", mism)

# ---------- C -------------------------------------------------------------------------
def plant_internal(L):
    # points +-k, k=1..L, as integers (the group is Z/N, 2L+... << N so no wrap)
    pts = [k for k in range(-L, L + 1) if k != 0]
    m = Counter()
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            u, v = pts[i], pts[j]
            if u + v == 0: continue
            m[u + v] += 1
    return sum(v * (v - 1) // 2 for v in m.values())

def plant_internal_fast(L):
    # numpy convolution: s -> number of ordered pairs (u,v), u,v in S, u+v=s ; remove u=v ; unordered = /2
    S = np.zeros(2 * L + 1, dtype=np.int64)
    for k in range(-L, L + 1):
        if k: S[k + L] = 1
    conv = np.convolve(S, S)  # index s + 2L
    # remove diagonal u=v: contributes at s=2u
    for k in range(-L, L + 1):
        if k: conv[2 * k + 2 * L] -= 1
    conv[2 * L] = 0  # s = 0 excluded (u=-v)
    assert (conv % 2 == 0).all()
    mm = conv // 2
    return int((mm * (mm - 1) // 2).sum())

for L in (1, 2, 3, 5, 9, 14, 30):
    assert plant_internal(L) == plant_internal_fast(L), L
print("C plant_internal slow==fast on L in {1,2,3,5,9,14,30}")
memo = {}
def PI(L):
    if L not in memo: memo[L] = plant_internal_fast(L)
    return memo[L]
badC = 0
Nmax = 0
for r in main:
    L, b = r["plant_L"], r["b"]
    assert 4 * L < r["N"]
    ok = PI(L) == r["plant_internal"]
    target = 0.30 * (sum(r["null"]) / 20)
    cap = b // 4
    if r["plant_feasible"]:
        ok = ok and PI(L) >= target and (L == 1 or PI(L - 1) < target) and 1 <= L <= cap
    else:
        ok = ok and L == cap and PI(L) < target
    if not ok:
        badC += 1
        if badC < 5: print("  C FAIL", r["cell"], r["c"], L, r["plant_internal"], PI(L), target, r["plant_feasible"])
print("C plant_internal / minimal-L / feasibility violations over all records:", badC)
