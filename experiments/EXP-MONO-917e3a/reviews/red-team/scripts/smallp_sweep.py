from itertools import combinations, product

def curve_ops(p,A,B):
    O=None
    def add(P,Q):
        if P is O: return Q
        if Q is O: return P
        x1,y1=P; x2,y2=Q
        if x1==x2 and (y1+y2)%p==0: return O
        if P==Q: lam=(3*x1*x1+A)*pow(2*y1,p-2,p)%p
        else:    lam=(y2-y1)*pow(x2-x1,p-2,p)%p
        x3=(lam*lam-x1-x2)%p; y3=(lam*(x1-x3)-y1)%p
        return (x3,y3)
    def neg(P): return O if P is O else (P[0],(-P[1])%p)
    return add,neg,O

def points(p,A,B):
    pts=[]
    for x in range(p):
        r=(x**3+A*x+B)%p
        for y in range(p):
            if y*y%p==r and y!=0:   # exclude 2-torsion (y=0) per the record's OI-1(b)
                pts.append((x,y))
    return pts

def clean(p,A,B,trip):
    add,neg,O=curve_ops(p,A,B)
    seen=set()
    for signs in product([1,-1],repeat=len(trip)-1):
        eps=(1,)+signs; S=O
        for e,P in zip(eps,trip):
            S=add(S,P if e==1 else neg(P))
        k='INF' if S is O else S[0]
        if k in seen: return False
        seen.add(k)
    return True

for p in (5,7,11,13,17,19,23):
    total=0; nowitness=[]
    for A in range(p):
        for B in range(p):
            if (4*A**3+27*B**2)%p==0: continue
            total+=1
            P=points(p,A,B)
            # only distinct x-coords matter for a triple; require distinct x's
            byx={}
            for (x,y) in P: byx.setdefault(x,(x,y))
            reps=list(byx.values())
            found=False
            for trip in combinations(reps,3):
                if clean(p,A,B,trip): found=True; break
            if not found: nowitness.append((A,B,len(reps)))
    print(f"p={p}: {total} non-singular curves; {len(nowitness)} with NO clean m=4 witness "
          f"(searched all triples of distinct-x non-2-torsion points)")
    for w in nowitness[:6]: print("    A,B,#distinct-x-with-point =",w)
