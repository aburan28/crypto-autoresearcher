import sys
sys.path.insert(0,'../../experiments/EXP-SEMBIN-d9767f/implementation/vendor')
from boolsys import modulus_for
class GF:
    def __init__(s,n):
        s.n=n; mod,_=modulus_for(n); s.mod=mod; q=(1<<n)-1; s.q=q
        # find a primitive element by trial (x is primitive for Conway)
        def mulraw(a,b):
            r=0
            while b:
                if b&1: r^=a
                b>>=1; a<<=1
                if a>>n: a^=mod
            return r
        for g in range(2,1<<n):
            e=[1]*(q); x=1; ok=True
            for i in range(q):
                e[i]=x; x=mulraw(x,g)
                if x==1 and i<q-1: ok=False;break
            if ok and x==1: break
        s.exp=e+e; s.log=[0]*(1<<n)
        for i in range(q): s.log[e[i]]=i
        s.g=g
    def mul(s,a,b):
        if a==0 or b==0: return 0
        return s.exp[s.log[a]+s.log[b]]
    def inv(s,a): return s.exp[s.q-s.log[a]]
    def sq(s,a): return 0 if a==0 else s.exp[(2*s.log[a])%s.q]
    def tr(s,a):
        t=0;x=a
        for _ in range(s.n): t^=x; x=s.sq(x)
        return t
    def halftrace(s,c):  # n odd: h with h^2+h=c if Tr(c)=0
        h=c;x=c
        for _ in range((s.n-1)//2):
            x=s.sq(s.sq(x)); h^=x
        return h
    def quad(s,a,b,c):
        """roots of a y^2 + b y + c = 0 in F; returns list"""
        if a==0:
            if b==0: return None if c!=0 else 'all'
            return [s.mul(c,s.inv(b))]
        if b==0:
            return [s.sqrt(s.mul(c,s.inv(a)))]
        ac=s.mul(a,c); b2=s.sq(b)
        t=s.mul(ac,s.inv(b2))
        if s.tr(t)!=0: return []
        w=s.halftrace(t)
        r1=s.mul(s.mul(b,w),s.inv(a)); r2=r1^s.mul(b,s.inv(a))
        return [r1,r2]
    def sqrt(s,a): return 0 if a==0 else s.exp[(s.log[a]*((s.q+1)//2))%s.q] if False else s.pw(a,1<<(s.n-1))
    def pw(s,a,e):
        if a==0: return 0 if e else 1
        return s.exp[(s.log[a]*e)%s.q]
def s3(F,a,b,c,B):
    ab=F.mul(a,b);ac=F.mul(a,c);bc=F.mul(b,c)
    return F.sq(ab^ac^bc)^F.mul(ab,c)^B
def span(basis):
    out=[0]
    for v in basis: out+= [x^v for x in out]
    return out
def sat_set(F,shape,Vs,B):
    n=F.n
    def roots_u(x1,x2):  # S3(u,x1,x2)=0 as quadratic in u
        a=F.sq(x1^x2); b=F.mul(x1,x2); c=F.sq(b)^B
        r=F.quad(a,b,c)
        return [] if r is None else (list(range(1<<n)) if r=='all' else r)
    sat=set()
    if shape=='chain3':
        us=set()
        for x1 in Vs:
            for x2 in Vs:
                us.update(roots_u(x1,x2))
        for u in us:
            for x3 in Vs:
                a=F.sq(u^x3); b=F.mul(u,x3); c=F.sq(b)^B
                r=F.quad(a,b,c)
                if r is None: continue
                if r=='all': sat.update(range(1<<n))
                else: sat.update(r)
    else:
        us=set()
        for x1 in Vs:
            for x2 in Vs:
                us.update(roots_u(x1,x2))
        us=list(us)
        for u1 in us:
            for u2 in us:
                a=F.sq(u1^u2); b=F.mul(u1,u2); c=F.sq(b)^B
                r=F.quad(a,b,c)
                if r is None: continue
                if r=='all': sat.update(range(1<<n))
                else: sat.update(r)
    return sat
