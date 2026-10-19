# Independent recount of a2 (T^2 coeff of Frobenius char poly) for C: y^2 = x^6 + (g+g^2) x^3 + g^3 over F_p,
# g = smallest primitive root mod p (PARI znprimroot), via point counts over F_p and F_{p^2}.
import numpy as np, sys
def isp(n):
    i=2
    while i*i<=n:
        if n%i==0: return False
        i+=1
    return n>1
def factor(n):
    f=set(); d=2
    while d*d<=n:
        while n%d==0: f.add(d); n//=d
        d+=1
    if n>1: f.add(n)
    return f
def primroot(p):
    fs=factor(p-1)
    for g in range(2,p):
        if all(pow(g,(p-1)//q,p)!=1 for q in fs): return g
def legendre_table(p):
    t=np.full(p,-1,dtype=np.int64); t[0]=0
    sq=(np.arange(1,p,dtype=np.int64)**2)%p; t[sq]=1
    return t
def a2(p):
    g=primroot(p); c3=(g+g*g)%p; c0=pow(g,3,p)
    L=legendre_table(p)
    x=np.arange(p,dtype=np.int64)
    x3=(x*x%p)*x%p
    f=((x3*x3)%p + c3*x3 + c0)%p
    N1=p+int(L[f].sum())+2
    # F_{p^2} = F_p[s]/(s^2-n), n smallest non-residue
    n=next(a for a in range(2,p) if L[a]==-1)
    a=np.repeat(np.arange(p,dtype=np.int64),p); b=np.tile(np.arange(p,dtype=np.int64),p)
    def mul(u1,v1,u2,v2): return ((u1*u2 + n*(v1*v2%p))%p, (u1*v2+v1*u2)%p)
    u2,v2=mul(a,b,a,b); u3,v3=mul(u2,v2,a,b); u6,v6=mul(u3,v3,u3,v3)
    fu=(u6 + c3*u3 + c0)%p; fv=(v6 + c3*v3)%p
    del a,b,u2,v2,u6,v6
    norm=(fu*fu - n*(fv*fv%p))%p
    N2=p*p+int(L[norm].sum())+2
    t1=p+1-N1; t2=p*p+1-N2
    e2=(t1*t1-t2)//2
    return g,t1,e2,e2-2*p
for k,p in [(1,19),(5,37),(9,79),(11,109),(21,349),(25,487),(31,739),(35,937),(41,1279),(55,2287),(65,3187)]:
    g,t1,e2,d=a2(p); print(f"k={k} p={p} g={g} a1={-t1} a2={e2} a2-2p={d}", flush=True)
