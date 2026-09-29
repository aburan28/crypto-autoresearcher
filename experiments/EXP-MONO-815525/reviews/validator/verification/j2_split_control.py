"""Direct point-arithmetic control on the split-g locus of C1/C5, where BOTH
phenomena occur, to show the point-arithmetic method separates them:
  #(sign classes summing to O)   <-> degree drop of Q_e
  #(collisions among x(eps.P))   <-> repeated root of Q_e
Everything here is over F_p (rational y-lifts only), independent code."""
import sys, itertools
from collections import Counter
sys.path.insert(0, ".")
from ffield import norm, deg, gcdp, derivp, factor_shape
from qe_indep import s3_of_e
from sweep_indep import CK

def qe_sym(p, A, B, e1, e2, e3):
    vals = []
    for k in range(5):
        s = 0
        for (i, j, d, l, m), co in CK[k].items():
            s += co * pow(e1, i, p) * pow(e2, j, p) * pow(e3, d, p) * pow(A, l, p) * pow(B, m, p)
        vals.append(s % p)
    return norm(vals, p)

def pts(p, A, B):
    sq = {}
    for y in range(p):
        sq.setdefault(y * y % p, []).append(y)
    out = []
    for x in range(p):
        v = (x * x * x + A * x + B) % p
        for y in sq.get(v, []):
            out.append((x, y))
    return out

def padd(p, A, P, Q):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0: return None
        lam = (3 * x1 * x1 + A) * pow(2 * y1, p - 2, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, p - 2, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)

for cid, p, A, B in (("C1", 101, 2, 3), ("C5", 101, 37, 29)):
    P = pts(p, A, B)
    print("=== %s p=%d  #E(F_p) affine points = %d ===" % (cid, p, len(P)))
    tally = Counter(); mism = 0; n = 0; ex = {}
    xs_by = {}
    for P1, P2, P3 in itertools.islice(itertools.combinations(P, 3), 0, 200000):
        x = (P1[0], P2[0], P3[0])
        if len(set(x)) != 3: continue
        n += 1
        e1 = sum(x) % p
        e2 = (x[0]*x[1] + x[0]*x[2] + x[1]*x[2]) % p
        e3 = (x[0]*x[1]*x[2]) % p
        sums = []
        for eps in ((1,1,1),(1,1,-1),(1,-1,1),(1,-1,-1)):
            S = None
            for s, Q in zip(eps, (P1,P2,P3)):
                S = padd(p, A, S, Q if s == 1 else (Q[0], (-Q[1]) % p))
            sums.append(S)
        n_inf = sum(1 for S in sums if S is None)
        xv = [S[0] for S in sums if S is not None]
        n_coll = len(xv) - len(set(xv))
        q = qe_sym(p, A, B, e1, e2, e3)
        d = deg(q)
        sqfree = deg(gcdp(q, derivp(q, p), p)) == 0 if q else None
        ok_deg = (4 - d == n_inf)
        ok_rep = (sqfree == (n_coll == 0))
        # and Q_e monic == prod (T - x_eps) over the finite classes
        mp = [1]
        for v in xv:
            mp = [(mp[i-1] if i > 0 else 0) - (mp[i]*v if i < len(mp) else 0)
                  for i in range(len(mp)+1)]
            mp = [c % p for c in mp]
        inv = pow(q[-1], p-2, p)
        ok_prod = [c*inv % p for c in q] == mp
        if not (ok_deg and ok_rep and ok_prod):
            mism += 1
            if mism <= 3: print("   MISMATCH", x, n_inf, n_coll, d, sqfree, ok_prod)
        key = (n_inf, n_coll, d, "sqfree" if sqfree else "REPEATED")
        tally[key] += 1
        ex.setdefault(key, (x, q, factor_shape(q, p) if q else None))
    print("  triples tested:", n, " mismatches:", mism)
    print("  (n_classes_at_infinity, n_x_collisions, deg Q_e, squarefree?) -> count")
    for k in sorted(tally, key=str):
        print("     %-38s %7d   e.g. x=%s Qe=%s shape=%s"
              % (str(k), tally[k], ex[k][0], ex[k][1], ex[k][2]))
