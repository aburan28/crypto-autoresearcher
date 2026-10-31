# FEASIBILITY PROBE ONLY (not a result). Legendre fibre L_t0: y^2=x(x+1)(x+t0), p odd prime.
# F_{p^2}=F_p[s]/(s^2-n), n a non-residue. elements are (a,b)=a+b s.
import sys, itertools
from collections import Counter
def run(p):
    n=next(c for c in range(2,p) if pow(c,(p-1)//2,p)==p-1)
    def mul(x,y): return ((x[0]*y[0]+n*x[1]*y[1])%p,(x[0]*y[1]+x[1]*y[0])%p)
    def add(x,y): return ((x[0]+y[0])%p,(x[1]+y[1])%p)
    def sub(x,y): return ((x[0]-y[0])%p,(x[1]-y[1])%p)
    def pw(x,e):
        r=(1,0)
        while e:
            if e&1:r=mul(r,x)
            x=mul(x,x);e>>=1
        return r
    def inv(x): return pw(x,p*p-2)
    def frob(x): return pw(x,p)
    O=None
    # curve over F_p, short-ish: y^2 = x^3 + (1+t)x^2 + t x
    def ecadd(P,Q,t,F):
        # generic over field ops tuple F=(add,sub,mul,inv,zero,one,eq)
        ad,sb,ml,iv,z,o,eq=F
        if P is None:return Q
        if Q is None:return P
        x1,y1=P;x2,y2=Q
        a2=ad(t,o)
        if eq(x1,x2):
            if not eq(y1,y2) or eq(y1,z):return None
            three=ad(ad(o,o),o);two=ad(o,o)
            lam=ml(ad(ad(ml(three,ml(x1,x1)),ml(ml(two,a2),x1)),t),iv(ml(two,y1)))
        else: lam=ml(sb(y2,y1),iv(sb(x2,x1)))
        x3=sb(sb(sb(ml(lam,lam),a2),x1),x2)
        y3=sb(ml(lam,sb(x1,x3)),y1)
        return (x3,y3)
    Fp2=(add,sub,mul,inv,(0,0),(1,0),lambda a,b:a==b)
    out=[]
    for t0 in range(2,p):
        t=(t0,0)
        # E(F_p) points
        pts=[None]
        for x in range(p):
            r=x*(x+1)*(x+t0)%p
            for y in range(p):
                if y*y%p==r: pts.append(((x,0),(y,0)))
        N=len(pts)
        idx={P:i for i,P in enumerate(pts)}
        tr=[]
        for a in range(p):
            for b in range(p):
                u=(a,b)
                if pw(u,p+1)!=(t0,0):continue
                u1=add(u,(1,0))
                y=mul(u,pw(u1,(p+1)//2))
                lhs=mul(y,y);rhs=mul(mul(u,u1),add(u,t))
                assert lhs==rhs,"not on curve"
                P=(u,y);Pc=(frob(u),frob(y))
                assert Pc[0]==(t0*1,0) or True
                T=ecadd(P,Pc,t,Fp2)
                assert T is None or (T[0][1]==0 and T[1][1]==0)
                T=None if T is None else ((T[0][0],0),(T[1][0],0))
                tr.append(idx[T])
        assert len(tr)==p+1
        M=len(tr)
        dist=len(set(tr))
        # 2E-coset structure: group by Z/2 classes via x-qr test  (E/2E classes: chi(x-e_i))
        def cls(P):
            if P is None:return 'O'
            x=P[0][0]
            ch=lambda v:(0 if v%p==0 else (1 if pow(v%p,(p-1)//2,p)==1 else -1))
            return (ch(x),ch(x+1),ch(x+t0))
        cc=Counter(cls(pts[i]) for i in tr); cg=Counter(cls(P) for P in pts)
        out.append((t0,N,M,dist,len(cc),len(cg)))
    return out
for p in map(int,sys.argv[1:]):
    r=run(p)
    print("p",p,"fibres",len(r))
    for t0,N,M,dist,kc,kg in r[:8]: print("  t0",t0,"|E|",N,"traces",M,"distinct",dist,"classes hit",kc,"of",kg)
    import statistics
    print("  mean distinct/|E|",statistics.mean(d/N for _,N,_,d,_,_ in r),"coupon pred (M=p+1 draws)",statistics.mean(1-(1-1/N)**(p+1) for _,N,_,_,_,_ in r))
    print("  mean classes hit",statistics.mean(k for *_,k,_ in r),"of mean",statistics.mean(g for *_,g in r))

# ---- second probe: odd-part projection (also PROBE ONLY)
def run2(p):
    import statistics,math
    n=next(c for c in range(2,p) if pow(c,(p-1)//2,p)==p-1)
    mulF=lambda x,y:(x*y)%p
    # work in F_p only for the trace points: recompute traces by reusing run's logic is heavy; reimplement minimal
    res=[]
    def mul(x,y): return ((x[0]*y[0]+n*x[1]*y[1])%p,(x[0]*y[1]+x[1]*y[0])%p)
    def pw(x,e):
        r=(1,0)
        while e:
            if e&1:r=mul(r,x)
            x=mul(x,x);e>>=1
        return r
    def add2(x,y): return ((x[0]+y[0])%p,(x[1]+y[1])%p)
    for t0 in range(2,p):
        def ec(P,Q):
            if P is None:return Q
            if Q is None:return P
            x1,y1=P;x2,y2=Q
            if x1==x2:
                if (y1+y2)%p==0:return None
                lam=(3*x1*x1+2*(1+t0)*x1+t0)*pow(2*y1,-1,p)%p
            else: lam=(y2-y1)*pow(x2-x1,-1,p)%p
            x3=(lam*lam-(1+t0)-x1-x2)%p
            return (x3,(lam*(x1-x3)-y1)%p)
        def sm(k,P):
            R=None
            while k:
                if k&1:R=ec(R,P)
                P=ec(P,P);k>>=1
            return R
        pts=[None]+[(x,y) for x in range(p) for y in range(p) if y*y%p==x*(x+1)*(x+t0)%p]
        N=len(pts); h=1
        while N%(2*h)==0 and (N//h)%2==0: h*=2
        m=N//h
        # traces: Tr(P)=P+Frob(P) computed in F_p^2 then to F_p via x,y coords; reuse: x1=(u),(y); do via formula in Fp2 with generic lambda
        def inv2(x): return pw(x,p*p-2)
        def ec2(P,Q):
            if P is None:return Q
            if Q is None:return P
            x1,y1=P;x2,y2=Q
            if x1==x2:
                if add2(y1,y2)==(0,0):return None
                num=add2(add2(mul((3,0),mul(x1,x1)),mul((2*(1+t0)%p,0),x1)),(t0,0))
                lam=mul(num,inv2(mul((2,0),y1)))
            else: lam=mul(((y2[0]-y1[0])%p,(y2[1]-y1[1])%p),inv2(((x2[0]-x1[0])%p,(x2[1]-x1[1])%p)))
            x3=mul(lam,lam);x3=((x3[0]-(1+t0)-x1[0]-x2[0])%p,(x3[1]-x1[1]-x2[1])%p)
            d=((x1[0]-x3[0])%p,(x1[1]-x3[1])%p);y3=mul(lam,d);y3=((y3[0]-y1[0])%p,(y3[1]-y1[1])%p)
            return (x3,y3)
        trs=set()
        for a in range(p):
            for b in range(p):
                u=(a,b)
                if pw(u,p+1)!=(t0,0):continue
                u1=((a+1)%p,b)
                y=mul(u,pw(u1,(p+1)//2))
                T=ec2((u,y),(pw(u,p),pw(y,p)))
                if T is None: trs.add(None)
                else:
                    assert T[0][1]==0 and T[1][1]==0
                    trs.add((T[0][0],T[1][0]))
        proj=set(sm(h,P) for P in trs)
        Mp=(p+1)//2
        res.append((len(proj),m,1-(1-1/m)**Mp, len(proj)/m))
    return res
for p in [11,13,17,19,23,29,31]:
    r=run2(p)
    import statistics
    print("odd-part p",p,"mean distinct/m",round(statistics.mean(x[3] for x in r),3),"coupon(M=(p+1)/2)",round(statistics.mean(x[2] for x in r),3))
