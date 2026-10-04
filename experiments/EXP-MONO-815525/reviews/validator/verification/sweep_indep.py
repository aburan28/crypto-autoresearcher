"""Independent replication of the two exhaustive F_101^3 sweeps, using MY
symmetric coefficients and MY factorization.  Also records disc(Q_e) so that
'repeated root' is checked as a SEPARATE event from 'root at infinity'."""
import json, sys, time
from collections import Counter
sys.path.insert(0, ".")
from ffield import norm, deg, gcdp, derivp, powmodp, sub as psub, mulp, divmodp

CK = {int(k): {tuple(map(int, kk.split(","))): v for kk, v in tab.items()}
      for k, tab in json.load(open("my_sym_coeffs.json")).items()}

def build(p, A, B):
    """c_k(e) = sum_d C[k][d](e1,e2) * e3^d ; return C[k][d] as term lists."""
    out = []
    for k in range(5):
        byd = {}
        for (i, j, d, l, m), co in CK[k].items():
            v = co * pow(A, l, p) * pow(B, m, p) % p
            if v:
                byd.setdefault(d, []).append((i, j, v))
        out.append([byd.get(d, []) for d in range(max(byd) + 1)])
    return out

def quartic_shape(q, p):
    """q monic (list low->high), deg 3 or 4 -> (factor-degree multiset, disc0)."""
    d = deg(q)
    sq = deg(gcdp(q, derivp(q, p), p)) == 0
    h = powmodp([0, 1], p, q, p)
    g1 = gcdp(psub(h, [0, 1], p), q, p)       # product of distinct linear factors
    nroots = deg(g1)
    return d, sq, nroots

def sweep(p, A, B, label, limit=None):
    C = build(p, A, B)
    t0 = time.time()
    n_irr = n_drop = 0
    pats = Counter(); nonsqfree = []; odd = []
    Ap = A % p
    for e1 in range(p):
        for e2 in range(p):
            # reducible-g set: e3 = a^3 - e1 a^2 + e2 a
            red = set()
            for a in range(p):
                red.add((a * a * a - e1 * a * a + e2 * a) % p)
            # precompute C[k][d](e1,e2)
            cc = []
            for k in range(5):
                row = []
                for terms in C[k]:
                    s = 0
                    for (i, j, v) in terms:
                        s += v * pow(e1, i, p) * pow(e2, j, p)
                    row.append(s % p)
                cc.append(row)
            for e3 in range(p):
                if e3 in red:
                    continue
                n_irr += 1
                q = []
                for k in range(5):
                    row = cc[k]
                    s = 0
                    for v in reversed(row):
                        s = (s * e3 + v) % p
                    q.append(s)
                qq = norm(q, p)
                d = deg(qq)
                if d < 4:
                    n_drop += 1
                inv = pow(qq[-1], p - 2, p)
                mq = [c * inv % p for c in qq]
                dd, sq, nroots = quartic_shape(mq, p)
                if not sq:
                    nonsqfree.append((e1, e2, e3, mq))
                if dd == 4 and sq and nroots == 1:
                    pats["deg4:1+3"] += 1
                elif dd == 3 and sq and nroots == 0:
                    pats["deg3:3"] += 1
                else:
                    pats["OTHER d=%d sq=%s roots=%d" % (dd, sq, nroots)] += 1
                    odd.append((e1, e2, e3, dd, sq, nroots))
            if limit and n_irr > limit:
                print("  [partial stop]"); return
        if e1 % 20 == 0:
            print("  %s e1=%d  n_irr=%d  %.1fs" % (label, e1, n_irr, time.time() - t0), flush=True)
    print("\n=== %s p=%d A=%d B=%d ===" % (label, p, A, B))
    print("  g-irreducible instances:", n_irr, " (expected (p^3-p)/3 =", (p**3 - p)//3, ")")
    print("  degree drops (deg Q_e < 4):", n_drop)
    print("  patterns:", dict(pats))
    print("  NON-SQUAREFREE Q_e instances:", len(nonsqfree), nonsqfree[:3])
    print("  other/unexpected:", len(odd), odd[:5])
    print("  elapsed %.1fs" % (time.time() - t0))

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    if which in ("C1", "both"): sweep(101, 2, 3, "C1")
    if which in ("C5", "both"): sweep(101, 37, 29, "C5")
