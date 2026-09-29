#!/usr/bin/env python3
"""
Independent, exact verifier for a high-rank elliptic curve certificate.

Pure Python (fractions only). Does NOT use PARI, so it is an independent check
of the search output rather than a restatement of it.

Certificate claim
-----------------
Base curve  E : y^2 = x^3 + A x + B          over Q
Field       K = Q(sqrt(d) : d in V),  V a subgroup of Q*/(Q*)^2 of order 2^k
Then        rank E(K) >= (number of verified distinct twist classes)

Mathematical basis
------------------
For squarefree d, the twist  E^(d) : v^2 = u^3 + A d^2 u + B d^3  admits
    phi_d : E^(d)(Q) -> E(K),   (u,v) |-> (u/d, (v/d^2) sqrt(d)),
an injective group homomorphism.  For sigma in G = Gal(K/Q), sigma(sqrt d) =
chi_d(sigma) sqrt(d), hence sigma(phi_d(P)) = chi_d(sigma) phi_d(P): the image
is a chi_d-eigenvector.  G is elementary abelian 2-group, so E(K) (x) Q is a
Q[G]-module splitting into character eigenspaces; the projector
e_chi = |G|^-1 sum_sigma chi(sigma) sigma kills every eigenvector of a
different character.  Therefore non-torsion points attached to pairwise
distinct classes d lie in pairwise distinct eigenspaces and are Z-independent.
No height / regulator computation is involved.

Non-torsion is certified by Mazur's theorem: a torsion point of an elliptic
curve over Q has order in {1,...,10,12}, so exhibiting m*P != O for
m = 1..12 proves P has infinite order.
"""
import json, sys
from fractions import Fraction as F

# ---------- exact arithmetic on y^2 = x^3 + a4 x + a6 over Q ----------
O = None  # point at infinity

def on_curve(P, a4, a6):
    if P is O: return True
    x, y = P
    return y*y == x*x*x + a4*x + a6

def add(P, Q, a4):
    if P is O: return Q
    if Q is O: return P
    x1,y1 = P; x2,y2 = Q
    if x1 == x2:
        if y1 != y2 or y1 == 0: return O
        lam = (3*x1*x1 + a4) / (2*y1)
    else:
        lam = (y2-y1)/(x2-x1)
    x3 = lam*lam - x1 - x2
    return (x3, lam*(x1-x3) - y1)

def mul(n, P, a4):
    R = O; Q = P
    if n < 0: n = -n; Q = (P[0], -P[1])
    while n:
        if n & 1: R = add(R, Q, a4)
        Q = add(Q, Q, a4); n >>= 1
    return R

# ---------- squarefree part ----------
def squarefree_part(n):
    if n == 0: raise ValueError('d=0')
    s = -1 if n < 0 else 1
    n = abs(n); out = 1; d = 2
    while d*d <= n:
        e = 0
        while n % d == 0: n//=d; e+=1
        if e & 1: out *= d
        d += 1 if d == 2 else 2
    out *= n
    return s*out

MAZUR_ORDERS = [1,2,3,4,5,6,7,8,9,10,12]   # possible finite orders over Q

def verify(cert, verbose=True):
    A = int(cert['base_curve']['A']); B = int(cert['base_curve']['B'])
    V = [int(x) for x in cert['field']['V_classes']]
    errs = []; ok_classes = []

    # --- (0) V must be a subgroup of Q*/(Q*)^2 of order 2^k, squarefree reps
    Vs = [squarefree_part(v) for v in V]
    if len(set(Vs)) != len(Vs): errs.append('V has repeated classes mod squares')
    k = cert['field']['k']
    if len(Vs) != 2**k: errs.append('|V| != 2^k')
    Vset = set(Vs)
    for a in Vs:
        for b in Vs:
            if squarefree_part(a*b) not in Vset:
                errs.append('V not closed: %d*%d'%(a,b)); break
    if 1 not in Vset: errs.append('V lacks the trivial class')

    # --- (1),(2) each twist point: on curve, and non-torsion by Mazur
    for e in cert['twists']:
        d = int(e['d']); ds = squarefree_part(d)
        if ds not in Vset:
            errs.append('d=%d not in V'%d); continue
        a4 = A*d*d; a6 = B*d*d*d
        good = 0
        for (xs, ys) in e['points']:
            P = (F(xs), F(ys))
            if not on_curve(P, F(a4), F(a6)):
                errs.append('point %s not on twist d=%d'%((xs,ys), d)); continue
            tors = False
            for m in MAZUR_ORDERS:
                if mul(m, P, F(a4)) is O:
                    tors = True; break
            if tors:
                errs.append('point %s on twist d=%d is TORSION'%((xs,ys), d)); continue
            good += 1
        if good >= 1: ok_classes.append(ds)

    ok_classes = sorted(set(ok_classes))
    rank_bound = len(ok_classes)
    if verbose:
        print('base curve   E : y^2 = x^3 + (%d) x + (%d)' % (A,B))
        print('field        K = Q(sqrt d : d in V),  |V| = 2^%d, [K:Q] = %d' % (k, 2**k))
        print('twist classes with a verified non-torsion rational point: %d' % rank_bound)
        print('CERTIFIED    rank E(K) >= %d' % rank_bound)
        print('errors: %d' % len(errs))
        for m in errs[:20]: print('   !', m)
    return rank_bound, errs

if __name__ == '__main__':
    cert = json.load(open(sys.argv[1]))
    r, errs = verify(cert)
    sys.exit(0 if not errs else 1)
