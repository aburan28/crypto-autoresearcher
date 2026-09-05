#!/usr/bin/env python3
"""Self-checks of the V1 blind implementation (no producer artifact involved).

C1  Boolean-evaluation identity: for all 64 digit assignments, S~ evaluated at
    the assignment equals S_3(x1, x2, x_R) computed in plain F_p arithmetic with
    x_k = sum_i 2^i a_{k,i}.  This pins the ring convention a^2 = a and every
    step of the B arithmetic against a completely independent evaluation.
C2  Top form: the degree-4 part of S~ equals top(ell_1^2)*top(ell_2^2)
    = (4 a10a11 + 8 a10a12 + 16 a11a12)(4 a20a21 + 8 a20a22 + 16 a21a22).
C3  rank_mod_p agrees with sympy's DomainMatrix rank over GF(p) on the actual
    row matrices and on random matrices.
"""
import sys, random, itertools
sys.path.insert(0, "/home/user/crypto-autoresearcher/coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-642cf5")
from v1_blind_rederive import (zero, mul, add, sub, smul, const, ell, S3_in_B,
                               rank_mod_p, mul_by_mono, POP, NMASK, INSTANCES, mono_name)
from sympy import Matrix, GF
from sympy.polys.matrices import DomainMatrix

def S3_scalar(x1, x2, x3, a, b, p):
    return ((x1 - x2) ** 2 * x3 ** 2
            - 2 * ((x1 + x2) * (x1 * x2 + a) + 2 * b) * x3
            + (x1 * x2 - a) ** 2 - 4 * b * (x1 + x2)) % p

def evaluate(g, bits, p):
    """bits: tuple of 6 values in {0,1}; monomial mask -> product of its bits."""
    tot = 0
    for m, c in enumerate(g):
        if not c:
            continue
        v = 1
        for i in range(6):
            if m >> i & 1:
                v *= bits[i]
        tot += c * v
    return tot % p

ok1 = ok2 = ok3 = True
for (p, cseed, a, b, tseed, xR) in INSTANCES:
    St = S3_in_B(ell(0, p), ell(1, p), xR, a, b, p)
    # C1
    for bits in itertools.product((0, 1), repeat=6):
        x1 = bits[0] + 2 * bits[1] + 4 * bits[2]
        x2 = bits[3] + 2 * bits[4] + 4 * bits[5]
        if evaluate(St, bits, p) != S3_scalar(x1, x2, xR, a, b, p):
            ok1 = False
            print("C1 FAIL", p, cseed, tseed, bits)
    # C2
    e1sq_top = {(1 << 0) | (1 << 1): 4, (1 << 0) | (1 << 2): 8, (1 << 1) | (1 << 2): 16}
    e2sq_top = {(1 << 3) | (1 << 4): 4, (1 << 3) | (1 << 5): 8, (1 << 4) | (1 << 5): 16}
    expect = {}
    for m1, c1 in e1sq_top.items():
        for m2, c2 in e2sq_top.items():
            expect[m1 | m2] = (c1 * c2) % p
    got = {m: St[m] for m in range(NMASK) if POP[m] == 4 and St[m]}
    if got != {m: c for m, c in expect.items() if c}:
        ok2 = False
        print("C2 FAIL", p, cseed, tseed, got, expect)

# C3: sympy cross-check of rank on the real row matrices and random matrices
rng = random.Random(7)
for (p, cseed, a, b, tseed, xR) in INSTANCES[:4]:
    St = S3_in_B(ell(0, p), ell(1, p), xR, a, b, p)
    for D in (4, 5, 6, 7):
        mus = [m for m in range(NMASK) if POP[m] == D - 4]
        rows = [mul_by_mono(St, m, p) for m in mus]
        cols_top = [m for m in range(NMASK) if POP[m] == D]
        for M in (rows, [[r[c] for c in cols_top] for r in rows]):
            if not M or not M[0]:
                continue
            mine = rank_mod_p(M, p)
            theirs = DomainMatrix([[GF(p)(x) for x in r] for r in M],
                                  (len(M), len(M[0])), GF(p)).rank()
            if mine != theirs:
                ok3 = False
                print("C3 FAIL", p, D, mine, theirs)
for _ in range(20):
    p = rng.choice([4099, 65537])
    n, k = rng.randint(1, 9), rng.randint(1, 9)
    M = [[rng.randrange(p) for _ in range(k)] for _ in range(n)]
    if rng.random() < 0.5 and n > 1:           # force a dependency
        M[-1] = [(2 * x) % p for x in M[0]]
    mine = rank_mod_p(M, p)
    theirs = DomainMatrix([[GF(p)(x) for x in r] for r in M], (n, k), GF(p)).rank()
    if mine != theirs:
        ok3 = False
        print("C3 FAIL random", p, mine, theirs)

print("C1 Boolean-evaluation identity (12 instances x 64 assignments):", "PASS" if ok1 else "FAIL")
print("C2 degree-4 top form = top(ell_1^2)*top(ell_2^2), 9 monomials:", "PASS" if ok2 else "FAIL")
print("C3 rank_mod_p vs sympy DomainMatrix over GF(p):", "PASS" if ok3 else "FAIL")
# show the top form once
p, cseed, a, b, tseed, xR = INSTANCES[0]
St = S3_in_B(ell(0, p), ell(1, p), xR, a, b, p)
print("top form of S~ at p=4099 seed1101 t1:",
      {mono_name(m): St[m] for m in range(NMASK) if POP[m] == 4 and St[m]})
print("degree-3 part nonzero?", any(St[m] for m in range(NMASK) if POP[m] == 3))
