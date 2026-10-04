from itertools import product

def mk(p,A,B):
    assert (4*A**3+27*B**2) % p != 0, "singular"
    O=None
    def add(P,Q):
        if P is O: return Q
        if Q is O: return P
        x1,y1=P; x2,y2=Q
        if x1==x2 and (y1+y2)%p==0: return O
        if P==Q:
            lam=(3*x1*x1+A)*pow(2*y1,p-2,p)%p
        else:
            lam=(y2-y1)*pow(x2-x1,p-2,p)%p
        x3=(lam*lam-x1-x2)%p; y3=(lam*(x1-x3)-y1)%p
        return (x3,y3)
    def neg(P): return O if P is O else (P[0],(-P[1])%p)
    return add,neg,O

def onc(p,A,B,x):
    r=(x**3+A*x+B)%p
    if r==0: return 0
    if pow(r,(p-1)//2,p)!=1: return None
    y=pow(r,(p+1)//4,p) if p%4==3 else tonelli(r,p)
    assert y*y%p==r
    return y

def tonelli(n,p):
    q=p-1;s=0
    while q%2==0: q//=2;s+=1
    if s==1: return pow(n,(p+1)//4,p)
    z=2
    while pow(z,(p-1)//2,p)!=p-1: z+=1
    m,c,t,r=s,pow(z,q,p),pow(n,q,p),pow(n,(q+1)//2,p)
    while t!=1:
        i,t2=0,t
        while t2!=1: t2=t2*t2%p;i+=1
        b=pow(c,1<<(m-i-1),p);m=i;c=b*b%p;t=t*c%p;r=r*b%p
    return r

def roots(p,A,B,pts):
    add,neg,O=mk(p,A,B)
    n=len(pts); out={}
    for signs in product([1,-1],repeat=n-1):
        eps=(1,)+signs
        S=O
        for e,P in zip(eps,pts):
            S=add(S, P if e==1 else neg(P))
        out[eps]= 'INF' if S is O else S[0]
    return out

def check(label,p,A,B,pts,expect=None):
    for (x,y) in pts:
        assert (y*y-(x**3+A*x+B))%p==0, ("not on curve",x,y)
        assert y%p!=0, ("2-torsion point used!",x,y)
    r=roots(p,A,B,pts)
    vals=list(r.values())
    print(f"{label}: p={p} A={A} B={B} pts={pts}")
    for k,v in r.items(): print("   ",k,"->",v)
    print("   distinct:",len(set(vals)),"of",len(vals),"  all_distinct:",len(set(vals))==len(vals))
    if expect is not None:
        print("   matches recorded root multiset:", sorted(vals)==sorted(expect))
    # diagnose collisions
    ks=list(r.keys())
    for i in range(len(ks)):
        for j in range(i+1,len(ks)):
            if r[ks[i]]==r[ks[j]]:
                w=[a!=b for a,b in zip(ks[i],ks[j])]
                Ssup=[t+1 for t,b in enumerate(w) if b]
                comp=[t+1 for t,b in enumerate(w) if not b]
                print(f"   COLLISION {ks[i]} vs {ks[j]} at x={r[ks[i]]}; flipped set S={Ssup} (|S|={len(Ssup)}), complement S'={comp} (|S'|={len(comp)})")
                add,neg,O=mk(p,A,B)
                for name,idx in (("Q_S",Ssup),("Q_S'",comp)):
                    T=O
                    for t in idx:
                        e=ks[i][t-1]; P=pts[t-1]
                        T=add(T,P if e==1 else neg(P))
                    print(f"      {name} (signs from first vector) = {T} ;  in E[2]? {T is None or T[1]%p==0}")
    print()

check("m=4 witness_1",101,2,3,[(3,6),(5,21),(9,12)],[11,47,1,66])
check("m=4 witness_2",211,5,7,[(2,5),(3,7),(8,83)],[175,127,120,183])
check("m=5 attempt_1",101,2,3,[(3,6),(5,21),(9,12),(10,35)],[3,67,96,21,69,99,5,3])
check("m=5 attempt_2",101,2,3,[(17,1),(18,35),(20,8),(21,32)],[62,17,61,56,52,73,25,47])
