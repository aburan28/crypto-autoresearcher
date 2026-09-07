from itertools import combinations, product

def ops(p,A,B):
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

def reps(p,A,B):
    out={}
    for x in range(p):
        r=(x**3+A*x+B)%p
        if r==0: continue
        if pow(r,(p-1)//2,p)==1:
            for y in range(1,p):
                if y*y%p==r: out[x]=(x,y); break
    return list(out.values())

def has_witness(p,A,B):
    add,neg,O=ops(p,A,B)
    R=reps(p,A,B)
    for trip in combinations(R,3):
        seen=set(); ok=True
        for signs in product([1,-1],repeat=2):
            eps=(1,)+signs; S=O
            for e,P in zip(eps,trip): S=add(S,P if e==1 else neg(P))
            k='INF' if S is O else S[0]
            if k in seen: ok=False; break
            seen.add(k)
        if ok: return True
    return False

for p in (19,23,31,37):
    fam={'j=0 (A=0)':[0,0],'j=1728 (B=0)':[0,0],'generic':[0,0]}
    for A in range(p):
        for B in range(p):
            if (4*A**3+27*B**2)%p==0: continue
            key='j=0 (A=0)' if A==0 else ('j=1728 (B=0)' if B==0 else 'generic')
            fam[key][0]+=1
            if not has_witness(p,A,B): fam[key][1]+=1
    print(f"p={p}:", {k:f"{v[1]}/{v[0]} no-witness ({100*v[1]/v[0]:.1f}%)" for k,v in fam.items()})
