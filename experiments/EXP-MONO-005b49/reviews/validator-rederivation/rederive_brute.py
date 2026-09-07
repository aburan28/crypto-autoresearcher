#!/usr/bin/env python3
"""Validator's OWN from-scratch brute force. No repo code imported."""
from fractions import Fraction
from itertools import product

# ---------- my own EC arithmetic over F_p (affine, None = O) ----------
def inv(a, p): return pow(a % p, p - 2, p)

def ec_add(P, Q, A, p):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0: return None
        lam = (3*x1*x1 + A) * inv(2*y1, p) % p
    else:
        lam = (y2 - y1) * inv(x2 - x1, p) % p
    x3 = (lam*lam - x1 - x2) % p
    y3 = (lam*(x1 - x3) - y1) % p
    return (x3, y3)

def ec_neg(P, p):
    return None if P is None else (P[0], (-P[1]) % p)

def ec_mul(k, P, A, p):
    R = None; Q = P
    while k:
        if k & 1: R = ec_add(R, Q, A, p)
        Q = ec_add(Q, Q, A, p); k >>= 1
    return R

def is_singular(A, B, p): return (4*pow(A,3,p) + 27*pow(B,2,p)) % p == 0

def points(A, B, p):
    """Enumerate E(F_p) by brute force over x and y (fully naive)."""
    sq = {}
    for y in range(p):
        sq.setdefault((y*y) % p, []).append(y)
    pts = [None]
    for x in range(p):
        f = (x*x*x + A*x + B) % p
        for y in sq.get(f, []):
            pts.append((x, y))
    return pts

def j_inv(A, B, p):
    den = (4*pow(A,3,p) + 27*pow(B,2,p)) % p
    if den == 0: return None
    return (1728 * 4 * pow(A,3,p) % p) * inv(den, p) % p

def invariants(A, B, p):
    pts = points(A, B, p)
    N = len(pts)
    tau = sum(1 for P in pts if ec_mul(2, P, A, p) is None)
    nu4 = sum(1 for P in pts if ec_mul(4, P, A, p) is None)
    nu8 = sum(1 for P in pts if ec_mul(8, P, A, p) is None)
    return dict(p=p, A=A, B=B, N=N, tau=tau, nu4=nu4, nu8=nu8,
                j=j_inv(A,B,p), pts=pts)

def group_structure(A, B, p, N, pts):
    """n1 | n2, n1*n2 = N, from #E[m] for m | N. n1 = gcd over exponents."""
    # n1 = largest n such that E[n] has n^2 points
    n1 = 1
    for n in range(1, N + 1):
        if N % n: continue
        if n*n > N: break
        cnt = sum(1 for P in pts if ec_mul(n, P, A, p) is None)
        if cnt == n*n: n1 = n
    return (n1, N // n1)

# ---------- the measured statistic, computed with ZERO theory ----------
SIGN_CLASSES = [(1,1,1),(1,1,-1),(1,-1,1),(1,-1,-1)]

def key(P): return "O" if P is None else P[0]

def f_collisions(P1, P2, P3, A, p):
    xs = []
    for eps in SIGN_CLASSES:
        acc = None
        for Pk, e in zip((P1,P2,P3), eps):
            acc = ec_add(acc, Pk if e == 1 else ec_neg(Pk, p), A, p)
        xs.append("INF" if acc is None else acc[0])
    return sum(1 for i in range(4) for j in range(i+1,4) if xs[i] == xs[j])

def exact_expectations_bruteforce(A, B, p, pts):
    """Exhaustive over ALL ordered triples with distinct keys. No theory used:
       f is computed by literally forming the 4 signed sums on the curve."""
    N = len(pts)
    T = set(i for i, P in enumerate(pts) if ec_mul(2, P, A, p) is None)
    gen = [i for i in range(N) if i not in T]
    ck = [1 if i in T else 2 for i in range(N)]
    kk = [key(pts[i]) for i in range(N)]

    num = 0; cnt = 0                      # transversal accumulators
    S = {}                                # group-uniform: sum of f by (c1,c2)
    for i in range(N):
        for j in range(N):
            if kk[j] == kk[i]: continue
            for k in range(N):
                if kk[k] == kk[i] or kk[k] == kk[j]: continue
                v = f_collisions(pts[i], pts[j], pts[k], A, p)
                key2 = (ck[i], ck[j])
                S[key2] = S.get(key2, 0) + v
                if ck[i] == 2 and ck[j] == 2 and ck[k] == 2:
                    num += v; cnt += 1
    E_trans = Fraction(num, cnt) if cnt else None
    E_gu = sum(Fraction(v, N*(N-c1)*(N-c1-c2)) for (c1, c2), v in S.items())
    # normalisation check
    Cn = {}
    for i in range(N):
        for j in range(N):
            if kk[j] == kk[i]: continue
            for k in range(N):
                if kk[k] == kk[i] or kk[k] == kk[j]: continue
                Cn[(ck[i], ck[j])] = Cn.get((ck[i], ck[j]), 0) + 1
    wsum = sum(Fraction(c, N*(N-c1)*(N-c1-c2)) for (c1, c2), c in Cn.items())
    return E_trans, E_gu, wsum

# ---------- my LOCKED closed forms ----------
def cf_trans(N, tau, nu4):
    G = N - tau
    D00 = G*(tau-1) - (nu4 - tau)
    return Fraction(6 * D00, G * (G - 2))

def cf_gu(N, tau, nu4):
    G = N - tau
    C = [G*(G-2)*(G-4), tau*G*(G-2), tau*(tau-1)*G, tau*(tau-1)*(tau-2)]
    W = [Fraction(1, N*(N-2)*(N-4)),
         Fraction(1, N*(N-1)*(N-3)) + Fraction(1, N*(N-2)*(N-3)) + Fraction(1, N*(N-2)*(N-4)),
         Fraction(1, N*(N-1)*(N-2)) + Fraction(1, N*(N-1)*(N-3)) + Fraction(1, N*(N-2)*(N-3)),
         Fraction(1, N*(N-1)*(N-2))]
    pi = [C[j]*W[j] for j in range(4)]
    return pi, sum(pi), pi[0]*cf_trans(N, tau, nu4) + 2*pi[1] + 6*pi[2] + 6*pi[3]
