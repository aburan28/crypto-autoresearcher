# FEASIBILITY PROBE ONLY (not a result): K1 / K2-telescoped on one tiny toy curve.
import random, sys
from math import gcd
def isprime(n):
    return n>1 and all(n%d for d in range(2,int(n**.5)+1))
def order(p,a,b):
    s=p+1
    for x in range(p):
        r=(x**3+a*x+b)%p
        if r: s+= 1 if pow(r,(p-1)//2,p)==1 and False else 0
    # Legendre
    t=0
    for x in range(p):
        r=(x**3+a*x+b)%p
        t+= 0 if r==0 else (1 if pow(r,(p-1)//2,p)==1 else -1)
    return p+1+t
def find(p0):
    for p in range(p0,p0+400):
        if not isprime(p): continue
        for a in range(1,30):
            for b in range(1,30):
                if (4*a**3+27*b*b)%p==0: continue
                N=order(p,a,b)
                if isprime(N) and N>1000 and N!=p and gcd(N,p-1)==1: return p,a,b,N
p,a,b,N=find(1009)
print("p,a,b,N",p,a,b,N)
def add(P,Q):
    if P is None: return Q
    if Q is None: return P
    x1,y1=P;x2,y2=Q
    if x1==x2 and (y1+y2)%p==0: return None
    l=((3*x1*x1+a)*pow(2*y1,-1,p) if P==Q else (y2-y1)*pow(x2-x1,-1,p))%p
    x3=(l*l-x1-x2)%p; return (x3,(l*(x1-x3)-y1)%p)
def mul(k,P):
    R=None
    while k:
        if k&1:R=add(R,P)
        P=add(P,P);k>>=1
    return R
def lineval(T,S,R):  # line through T,S (tangent if equal) / vertical at T+S, at R. returns None on zero-division
    x1,y1=T;x2,y2=S;xr,yr=R
    if x1==x2 and (y1+y2)%p==0:
        num=(xr-x1)%p; den=1  # line is vertical, T+S=O, v=1
        return num,den
    l=((3*x1*x1+a)*pow(2*y1,-1,p) if T==S else (y2-y1)*pow(x2-x1,-1,p))%p
    x3=(l*l-x1-x2)%p
    num=(yr-y1-l*(xr-x1))%p; den=(xr-x3)%p
    return num,den
def miller(P,R,chain):
    # chain: list of ('d') / ('a') bits MSB first of N ; returns f_N,P(R) or None on collision
    T=P;f=1;n=N
    bits=bin(n)[3:]
    for bt in bits:
        num,den=lineval(T,T,R)
        if den==0 or num==0 and False: return None
        f=f*f%p*num%p*pow(den,-1,p)%p; T=add(T,T)
        if bt=='1':
            if T is None: return None
            num,den=lineval(T,P,R)
            if den==0: return None
            f=f*num%p*pow(den,-1,p)%p; T=add(T,P)
    return f
# find P
random.seed(1)
while True:
    x=random.randrange(p);r=(x**3+a*x+b)%p
    if r and pow(r,(p-1)//2,p)==1:
        y=next(y for y in range(p) if y*y%p==r);P=(x,y);break
assert mul(N,P) is None
Np=pow(N,-1,p-1)
pts=[None,P]
for k in range(2,N): pts.append(add(pts[-1],P))
U={}
miss=0
for k in range(2,N-1):
    f=miller(P,pts[k],None)
    if f is None or f==0: miss+=1;continue
    U[k]=pow(f,Np,p)
print("computed",len(U),"collision/zero skipped",miss)
# K1
ratios=set();bad=0;n=0
for _ in range(3000):
    i=random.randrange(2,N-1);j=random.randrange(2,N-1);s=(i+j)%N
    if i not in U or j not in U or s not in U or s in (0,1,N-1): continue
    R,S=pts[i],pts[j]
    if R[0]==S[0]: continue
    l=(S[1]-R[1])*pow(S[0]-R[0],-1,p)%p
    g=(P[1]-R[1]-l*(P[0]-R[0]))*pow(P[0]-pts[s][0],-1,p)%p
    q=U[i]*U[j]*pow(U[s],-1,p)*pow(g,-1,p)%p
    ratios.add(q);n+=1
print("K1 pairs",n,"distinct ratio values",sorted(ratios)[:5],"p-1=",p-1)
# K2 telescoped
cs=set()
for k in range(2,N-2):
    if k in U and k+1 in U:
        d=(P[0]-pts[k][0])%p
        cs.add(U[k+1]*d%p*pow(U[k],-1,p)%p)
print("K2 telescoped distinct constants",len(cs),sorted(cs)[:5])
