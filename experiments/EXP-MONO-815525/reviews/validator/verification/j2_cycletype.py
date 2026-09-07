"""Compute the Frobenius cycle type DIRECTLY on the four sign classes
(the object IDEA-20260904-ad63fe's (C3) mechanism is actually about),
with the point at infinity counted as a genuine class.  No factorization."""
import json, random, sys
from collections import Counter
sys.path.insert(0, ".")
from ffield import has_root_Fp
from qe_indep import s3_of_e
from j2_pointarith import K3, L6, ec_add, ec_neg, on_curve

CLASSES = [(1,1,1),(1,1,-1),(1,-1,1),(1,-1,-1)]
def lbl(c): return "".join("+" if s>0 else "-" for s in c)

def cycle_type(p, A, B, e1, e2, e3):
    K = K3(p, e1, e2, e3); Av, Bv = [A%p,0,0], [B%p,0,0]
    rng = random.Random(555 + p + e1 + 3*e2 + 5*e3)
    while True:
        n = [rng.randrange(p) for _ in range(3)]
        if not K.is_zero(n) and not K.is_square(n): break
    L = L6(K, n)
    x1 = [0,1,0]
    fx1 = K.add(K.add(K.mul(x1, K.mul(x1,x1)), K.mul(Av,x1)), Bv)
    if K.is_square(fx1):
        Y1 = L.emb(K.sqrt(fx1))
    else:
        Y1 = (K.zero[:], K.sqrt(K.mul(fx1, K.inv(n))))
    X1 = L.emb(x1); P1 = (X1, Y1)
    P2 = (L.pw(X1, p), L.pw(Y1, p)); P3 = (L.pw(X1, p*p), L.pw(Y1, p*p))
    assert on_curve(L, Av, Bv, P1) and on_curve(L, Av, Bv, P2) and on_curve(L, Av, Bv, P3)
    xv = {}
    for eps in CLASSES:
        S = None
        for s, Q in zip(eps, (P1,P2,P3)):
            S = ec_add(L, Av, Bv, S, Q if s == 1 else ec_neg(L, Q))
        xv[eps] = None if S is None else S[0]       # None == the point at infinity
    # Frobenius on P^1: x -> x^p, with infinity fixed
    def frob(u): return None if u is None else L.pw(u, p)
    # build the permutation on the four fibre points (as a multiset of values)
    vals = [xv[c] for c in CLASSES]
    def key(u):
        return "INF" if u is None else tuple(tuple(z % p for z in w) for w in u)
    ks = [key(v) for v in vals]
    distinct = len(set(ks)) == 4
    perm = []
    for v in vals:
        fk = key(frob(v))
        perm.append(ks.index(fk) if fk in ks else -1)
    # cycle type
    if -1 in perm or sorted(perm) != [0,1,2,3]:
        return None, distinct, ks
    seen = [False]*4; ct = []
    for i in range(4):
        if not seen[i]:
            j, L_ = i, 0
            while not seen[j]:
                seen[j] = True; j = perm[j]; L_ += 1
            ct.append(L_)
    return tuple(sorted(ct)), distinct, ks

RAW="/Volumes/SSD990/crypto-autoresearcher/experiments/EXP-MONO-815525/runs/RUN-MONO-815525-1/raw-result.json"
d=json.load(open(RAW))
devs=[(r["p"],r["A"],r["B"],r["e"],r["curve"]) for sw in d["stage_1"]["exhaustive_sweep"]
      for r in sw["deviations_all"]]
devs+=[(r["p"],r["A"],r["B"],[r["e1"],r["e2"],r["e3"]],r["curve"])
       for r in d["stage_2"]["deviations_sampled"]]
rng=random.Random(77)
samp=rng.sample(devs,300)
c=Counter(); dist=0
for p,A,B,e,cid in samp:
    ct,ok,_=cycle_type(p,A,B,*e); c[ct]+=1; dist+=ok
print("DEGREE-DROP instances (300 sampled from the 6,762):")
print("  Frobenius cycle type on the 4 sign classes (infinity included):", dict(c))
print("  four fibre points distinct (infinity counted as one):", dist, "/", len(samp))

# non-drop g-irreducible controls
CURVES=[("C1",101,2,3),("C2",1009,5,7),("C3",211,3,11),("C4",1999,7,13),("C5",101,37,29)]
rng=random.Random(99); c2=Counter(); n=0; dist2=0
for cid,p,A,B in CURVES:
    got=0
    while got<40:
        e1,e2,e3=(rng.randrange(p) for _ in range(3))
        if has_root_Fp([(-e3)%p,e2%p,(-e1)%p,1],p): continue
        if s3_of_e(p,A,B,e1,e2,e3)==0: continue
        ct,ok,_=cycle_type(p,A,B,e1,e2,e3); c2[ct]+=1; n+=1; dist2+=ok; got+=1
print("\nNON-DROP g-irreducible controls (200, 40 per curve):")
print("  Frobenius cycle type on the 4 sign classes:", dict(c2))
print("  four fibre points distinct:", dist2, "/", n)
