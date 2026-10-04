#!/usr/bin/env python3
"""Find the second Q-relation among the 8 forced points (J3 A.2 rigor step),
via a bounded search over small coefficients constrained by reduction mod p.

The 8 points P_1..P_8 satisfy sum P_i = O (Mestre). A second Q-relation is a
vector (n_1..n_7) with sum n_i P_i = O over Q and the n_i not all equal (which
gives the 8-point relation (n_1..n_7, 0), independent of (1,..,1)).

Method (exact, stdlib):
  * For a good prime p, precompute the cyclic table of <P_7 mod p>:
        T[t] = t*(P_7 mod p)  for t in a range.
  * For (n_1..n_6) in a box, compute R = -sum_{i<7} n_i (P_i mod p) in E(F_p),
    look up n_7 with n_7 (P_7 mod p) = R, and record the relation.
  * Each candidate relation is verified OVER Q by exact point arithmetic.
  * A verified Q-relation with the n_i not all equal proves Q-rank <= 6;
    combined with the certifier's lower bound 6, Q-rank = 6.
"""
import os, sys, json, itertools
from fractions import Fraction as Fr
from math import gcd

ROOT = "/Volumes/SSD990/llm/tmp/opencode/review-e3cf55-20260909"
SRC = os.path.join(ROOT, "experiments", "EXP-ECRANK-73275e", "source")
sys.path.insert(0, SRC)
os.environ.setdefault("ECRANK_REPO_ROOT", ROOT)
import ecrank_engine as E

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "b_tuples.json")) as f:
    BT = json.load(f)
N8 = [[Fr(x) for x in row] for row in BT["n8"]]

def fp_add(ai, p, P, Q):
    if P is None: return Q
    if Q is None: return P
    a2, a4, a6 = ai[1] % p, ai[3] % p, ai[4] % p
    x1, y1 = P; x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0: return None
        lam = (3 * x1 * x1 + 2 * a2 * x1 + a4) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - a2 - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)

def fp_neg(p, P):
    if P is None: return None
    return (P[0], (-P[1]) % p)

def fp_mul(ai, p, n, P):
    if n < 0:
        n = -n; P = fp_neg(p, P)
    R = None; Q = P
    while n:
        if n & 1: R = fp_add(ai, p, R, Q)
        Q = fp_add(ai, p, Q, Q)
        n >>= 1
    return R

def factorize(n):
    out = []; d = 2
    while d * d <= n:
        if n % d == 0:
            e = 0
            while n % d == 0: n //= d; e += 1
            out.append((d, e))
        d += 1 if d == 2 else 2
    if n > 1: out.append((n, 1))
    return out

def point_order_fp(ai, p, P, N, fac):
    if P is None: return 1
    order = N
    for q, e in fac:
        while order % q == 0:
            cand = order // q
            if fp_mul(ai, p, cand, P) is None: order = cand
            else: break
    return order

def _is_prime(n):
    if n < 2: return False
    if n % 2 == 0: return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0: return False
        d += 2
    return True

def fr_add(a2, a4, a6, P, Q):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2:
        if y1 + y2 == 0: return None
        lam = (3 * x1 * x1 + 2 * a2 * x1 + a4) / (2 * y1)
    else:
        lam = (y2 - y1) / (x2 - x1)
    x3 = lam * lam - a2 - x1 - x2
    y3 = lam * (x1 - x3) - y1
    return (x3, y3)

def fr_mul(a2, a4, a6, n, P):
    if n < 0:
        n = -n; P = (P[0], -P[1])
    R = None; Q = P
    while n:
        if n & 1: R = fr_add(a2, a4, a6, R, Q)
        Q = fr_add(a2, a4, a6, Q, Q)
        n >>= 1
    return R

def is_q_relation(ainv, Wpts, v7):
    """v7: 7 ints. Check sum_{i<7} v7[i] P_i == O over Q."""
    a2, a4, a6 = Fr(ainv[1]), Fr(ainv[3]), Fr(ainv[4])
    S = None
    for i in range(7):
        if v7[i]:
            P = (Fr(Wpts[i][0]), Fr(Wpts[i][1]))
            if v7[i] != 1:
                P = fr_mul(a2, a4, a6, v7[i], P)
            S = fr_add(a2, a4, a6, S, P)
    return S is None

def main():
    B = 8           # box for n_1..n_6
    N7RANGE = 300   # range for n_7
    report = {}
    for bi in (0, 1, 7, 2):
        b = N8[bi]
        p_, g, s = E.mestre_polys(list(b))
        r = [E.peval(g, x) for x in b]
        ainv, Wpts = E.cubic_to_weierstrass(s, [(b[i], r[i]) for i in range(8)])
        ainv = [int(z) for z in ainv]
        disc = E.disc_from_ainv(ainv)
        dens = set()
        for (x, y) in Wpts:
            dens.add(Fr(x).denominator); dens.add(Fr(y).denominator)
        bad = set()
        for d in dens:
            for q, e in factorize(d): bad.add(q)
        p = None; cand = 3
        while p is None:
            if cand > 2 and disc % cand != 0 and cand not in bad and _is_prime(cand):
                p = cand
            cand += 1
        def mf(fr, pp): return (fr.numerator * pow(fr.denominator, -1, pp)) % pp
        red = [(mf(Fr(x), p), mf(Fr(y), p)) for (x, y) in Wpts]
        # count points / order of P_7
        # N_p
        a2m, a4m, a6m = ainv[1] % p, ainv[3] % p, ainv[4] % p
        Np = 1
        e = (p - 1) // 2
        for x in range(p):
            f = (x * x * x + a2m * x * x + a4m * x + a6m) % p
            if f == 0: Np += 1
            else: Np += 2 if pow(f, e, p) == 1 else 0
        fac = factorize(Np)
        P7 = red[6]
        ord7 = point_order_fp(ainv, p, P7, Np, fac)
        # table for n_7: t -> t*P7 for t in [-N7RANGE, N7RANGE]
        tbl = {}
        for t in range(-N7RANGE, N7RANGE + 1):
            tbl[fp_mul(ainv, p, t, P7)] = t
        # search
        found = []
        vals = list(range(-B, B + 1))
        for n1 in vals:
            for n2 in vals:
                for n3 in vals:
                    for n4 in vals:
                        for n5 in vals:
                            for n6 in vals:
                                # R = -sum_{i<7} n_i P_i  (i=1..6, 0-indexed 0..5)
                                R = None
                                for i in range(6):
                                    ni = (n1, n2, n3, n4, n5, n6)[i]
                                    if ni:
                                        Q = fp_mul(ainv, p, ni, red[i])
                                        R = fp_add(ai=ainv, p=p, P=R, Q=Q) if False else fp_add(ainv, p, R, Q)
                                R = fp_neg(p, R)
                                n7 = tbl.get(R)
                                if n7 is None: continue
                                v7 = (n1, n2, n3, n4, n5, n6, n7)
                                # skip the trivial all-equal (Mestre) direction
                                if len(set(v7)) == 1: continue
                                # verify over Q
                                if is_q_relation(ainv, Wpts, list(v7)):
                                    found.append(list(v7))
        report[str(bi)] = {"p": p, "N_p": Np, "ord7": ord7,
                           "B": B, "N7RANGE": N7RANGE,
                           "n_q_relations_found": len(found),
                           "q_relations": found[:10]}
        print("=== b_index %d ===" % bi)
        print("  p=%d N_p=%d ord7=%d  B=%d N7RANGE=%d" % (p, Np, ord7, B, N7RANGE))
        print("  Q-relations found (n_1..n_7, not all equal):", len(found))
        for v in found[:6]:
            print("    ", v)
        print()
    with open(os.path.join(HERE, "second_relation2.json"), "w") as f:
        json.dump(report, f, indent=1)
    print("wrote second_relation2.json")

if __name__ == "__main__":
    main()
