# Independent checks for crypto:papers/rootfinding-decomposition/lean/S3Roots.lean
# 1) exact Z[a,b,xR,yR,xF,yF,X] check of the linear_combination certificate (S3Roots.lean:72-86)
# 2) differential test of S3 (lines 35-38) vs an independent group law: S3(x(P),x(Q),x(P+Q))=0
# 3) witness for hypotheses hx,hR,hF (lines 62-63) + numeric factorization/root check over F_p
# 4) proves-too-much control: perturb one S3 coefficient -> identity must fail
import random
V = ["a","b","xR","yR","xF","yF","X"]
class P:
    def __init__(s, d=None): s.d = {k:v for k,v in (d or {}).items() if v}
    @staticmethod
    def var(n): e=[0]*7; e[V.index(n)]=1; return P({tuple(e):1})
    @staticmethod
    def c(k): return P({(0,)*7:k})
    def __add__(s,o):
        o=o if isinstance(o,P) else P.c(o); d=dict(s.d)
        for k,v in o.d.items(): d[k]=d.get(k,0)+v
        return P(d)
    __radd__=__add__
    def __neg__(s): return P({k:-v for k,v in s.d.items()})
    def __sub__(s,o): return s+(-(o if isinstance(o,P) else P.c(o)))
    def __rsub__(s,o): return P.c(o)-s
    def __mul__(s,o):
        o=o if isinstance(o,P) else P.c(o); d={}
        for k1,v1 in s.d.items():
            for k2,v2 in o.d.items():
                k=tuple(x+y for x,y in zip(k1,k2)); d[k]=d.get(k,0)+v1*v2
        return P(d)
    __rmul__=__mul__
    def __pow__(s,n):
        r=P.c(1)
        for _ in range(n): r=r*s
        return r
a,b,xR,yR,xF,yF,X=[P.var(v) for v in V]
def S3p(a,b,x1,x2,x3,k2b=2):
    return (x1-x2)**2*x3**2 - 2*((x1+x2)*(x1*x2+a)+k2b*b)*x3 + ((x1*x2-a)**2 - 4*b*(x1+x2))
d=xF-xR
Np=(yF-yR)**2 - d**2*(xR+xF)
Nm=(-yF-yR)**2 - d**2*(xR+xF)
e1=(2*X*xF**2 - 4*X*xF*xR + 2*X*xR**2 - a*xR - b + 2*xF**3 - 2*xF**2*xR - 2*xF*xR**2 + xR**3 + 2*yF**2 - yR**2)
e2=(2*X*xF**2 - 4*X*xF*xR + 2*X*xR**2 - a*xF + 2*a*xR + b + xF**3 - 2*xF**2*xR - 2*xF*xR**2 + 4*xR**3 - yF**2)
hR=yR**2-(xR**3+a*xR+b); hF=yF**2-(xF**3+a*xF+b)
res = d**2*S3p(a,b,xR,xF,X) - (d**2*X-Np)*(d**2*X-Nm) - e1*hR - e2*hF
print("1) certificate residual over Z is identically zero:", res.d == {}, "(terms:", len(res.d), ")")
res2 = d**2*S3p(a,b,xR,xF,X,k2b=3) - (d**2*X-Np)*(d**2*X-Nm) - e1*hR - e2*hF
print("4) control (2b->3b in S3): residual nonzero:", res2.d != {})
# group law over F_p
def mkcurve(p,A,B):
    def add(P1,P2):
        if P1 is None: return P2
        if P2 is None: return P1
        if P1[0]==P2[0] and (P1[1]+P2[1])%p==0: return None
        l=((3*P1[0]**2+A)*pow(2*P1[1],-1,p) if P1==P2 else (P2[1]-P1[1])*pow(P2[0]-P1[0],-1,p))%p
        x3=(l*l-P1[0]-P2[0])%p; return (x3,(l*(P1[0]-x3)-P1[1])%p)
    pts=[(x,y) for x in range(p) for y in range(p) if (y*y-x**3-A*x-B)%p==0]
    return add,pts
def S3n(p,A,B,x1,x2,x3): return ((x1-x2)**2*x3**2 - 2*((x1+x2)*(x1*x2+A)+2*B)*x3 + (x1*x2-A)**2 - 4*B*(x1+x2))%p
random.seed(7); fails=0; n=0; facfail=0; rootfail=0
for p in [101, 1009, 7919]:
    for _ in range(3):
        A,B=random.randrange(p),random.randrange(p)
        if (4*A**3+27*B**2)%p==0: continue
        add,pts=mkcurve(p,A,B) if p<2000 else (None,None)
        if pts is None:
            # sample points by trial for big p
            def add(P1,P2,A=A,p=p):
                if P1[0]==P2[0] and (P1[1]+P2[1])%p==0: return None
                l=((3*P1[0]**2+A)*pow(2*P1[1],-1,p) if P1==P2 else (P2[1]-P1[1])*pow(P2[0]-P1[0],-1,p))%p
                x3=(l*l-P1[0]-P2[0])%p; return (x3,(l*(P1[0]-x3)-P1[1])%p)
            pts=[]
            while len(pts)<60:
                x=random.randrange(p); r=(x**3+A*x+B)%p
                y=next((y for y in range(p) if y*y%p==r),None) if pow(r,(p-1)//2,p) in (0,1) else None
                if y is not None: pts.append((x,y))
        for _ in range(200):
            R=random.choice(pts); F=random.choice(pts)
            if R[0]==F[0]: continue
            n+=1
            S=add(R,F); D=add(R,(F[0],(-F[1])%p))
            if S3n(p,A,B,R[0],F[0],S[0])!=0 or S3n(p,A,B,R[0],F[0],D[0])!=0: fails+=1
            inv=pow(F[0]-R[0],-1,p)
            xp=(((F[1]-R[1])*inv)**2-R[0]-F[0])%p; xm=(((-F[1]-R[1])*inv)**2-R[0]-F[0])%p
            assert xp==S[0] and xm==D[0]
            for Xv in random.sample(range(p),20):
                if S3n(p,A,B,R[0],F[0],Xv)!=((R[0]-F[0])**2*(Xv-xp)*(Xv-xm))%p: facfail+=1
            roots={Xv for Xv in range(p) if S3n(p,A,B,R[0],F[0],Xv)==0} if p<2000 else None
            if roots is not None and roots!={xp,xm}: rootfail+=1
print("2) S3(x_R,x_F,x(R+-F))=0 via independent group law: pairs",n,"failures",fails)
print("3) witnesses with hx,hR,hF true:",n,"; factorization mismatches",facfail,"; root-set mismatches (p<2000)",rootfail)
print("   example witness: p=101 curve y^2=x^3+2x+3, R=(3,6)? on-curve:",(6*6-(27+6+3))%101==0)
