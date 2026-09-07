"""Independent re-derivation, from scratch, of the EXACT expected collision
rates for the four curves under review.  No repo code imported."""
import json, math
from itertools import combinations

def qr(a,p):
    a%=p
    if a==0: return 0
    return 1 if pow(a,(p-1)//2,p)==1 else -1

def neg(P,p):
    return None if P is None else (P[0],(-P[1])%p)

def add(P,Q,A,p):
    if P is None: return Q
    if Q is None: return P
    x1,y1=P; x2,y2=Q
    if x1==x2:
        if (y1+y2)%p==0: return None
        lam=((3*x1*x1+A)*pow((2*y1)%p,p-2,p))%p
    else:
        lam=((y2-y1)*pow((x2-x1)%p,p-2,p))%p
    x3=(lam*lam-x1-x2)%p
    y3=(lam*(x1-x3)-y1)%p
    return (x3%p,y3%p)

def mul(k,P,A,p):
    R=None; Q=P
    while k>0:
        if k&1: R=add(R,Q,A,p)
        Q=add(Q,Q,A,p); k>>=1
    return R

def points(A,B,p):
    pts=[None]
    for x in range(p):
        f=(x*x*x+A*x+B)%p
        c=qr(f,p)
        if c==0: pts.append((x,0))
        elif c==1:
            for y in range(1,(p//2)+1):
                if (y*y)%p==f:
                    pts.append((x,y)); pts.append((x,(p-y)%p)); break
    return pts

def divisors(n):
    d=[]
    i=1
    while i*i<=n:
        if n%i==0:
            d.append(i)
            if i!=n//i: d.append(n//i)
        i+=1
    return sorted(d)

def order(P,A,p,N,divs):
    for d in divs:
        if mul(d,P,A,p) is None: return d
    return None

CURVES = [
    dict(tag="cell1_ord", p=617,  A=340, B=362, kind="ordinary"),
    dict(tag="cell1_cm",  p=617,  A=69,  B=0,   kind="CM j=1728"),
    dict(tag="cell2_ord", p=3541, A=577, B=1628,kind="ordinary"),
    dict(tag="cell2_cm",  p=3541, A=0,   B=2728,kind="CM j=0"),
]

out={}
for c in CURVES:
    p,A,B=c["p"],c["A"],c["B"]
    P=points(A,B,p); N=len(P)
    divs=divisors(N)
    T2=[Q for Q in P if mul(2,Q,A,p) is None]      # includes O
    tau=len(T2)
    FB=sorted({Q[0] for Q in P if Q is not None and (Q[0]**3+A*Q[0]+B)%p!=0})
    n=len(FB)
    # group structure
    maxord=max(order(Q,A,p,N,divs) for Q in P)
    d2=maxord; d1=N//d2
    # F = sum over nonzero T of #fixed x
    T2s=[Q for Q in T2 if Q is not None]
    # lift each FB x to a point (canonical small root)
    lift={}
    for Q in P:
        if Q is None: continue
        if Q[0] in FB and (Q[0] not in lift or Q[1]<lift[Q[0]][1]):
            lift[Q[0]]=Q
    F=0; fixdetail=[]
    for T in T2s:
        f=0
        for x in FB:
            if add(lift[x],T,A,p)[0]==x: f+=1
        F+=f; fixdetail.append(f)
    # exact transversal expectation, two independent ways
    E_tr_formula = 3*((tau-1)*n - F)/(n*(n-1))
    # brute force over unordered FB pairs
    xt = {}   # x -> multiset of partner x's
    for T in T2s:
        for x in FB:
            xt.setdefault(x,[]).append(add(lift[x],T,A,p)[0])
    tot=0
    for x in FB:
        tot += sum(1 for y in xt[x] if y!=x)
    E_tr_brute = 3*(tot/2)/ (n*(n-1)/2)
    out[c["tag"]]=dict(p=p,A=A,B=B,kind=c["kind"],N=N,tau=tau,n_FB=n,
        group=f"Z/{d1} x Z/{d2}", d1=d1, d2=d2, F=F, fix_per_T=fixdetail,
        E_tr_exact=E_tr_formula, E_tr_brute=E_tr_brute,
        partB_closed_form=6*(tau-1)/N)
    print(json.dumps(out[c["tag"]],indent=1))
json.dump(out,open("/tmp/claude/exact_out.json","w"),indent=1)
