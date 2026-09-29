"""J2 (b): ATTACK the composition-equals-monomial step IN CHARACTERISTIC p.
Claim under attack: over a field, f o g = Y^m  ==>  g = c Y^e + b and
f = c'(Y-b)^{m/e}.  Brute force over F_q for q = 2,3,4,5,7,8,9 with explicit
attention to additive / p-th power / inseparable maps."""
import itertools, sys

def make_field(p, k, modpoly=None):
    """returns (elements, add, mul, zero, one, name); F_p if k==1 else F_p[t]/(modpoly)"""
    if k == 1:
        els = list(range(p))
        return els, (lambda a,b:(a+b)%p), (lambda a,b:(a*b)%p), 0, 1, "F_%d"%p
    # elements are tuples of length k
    def add(a,b): return tuple((x+y)%p for x,y in zip(a,b))
    def rmul(a,b):
        r=[0]*(2*k-1)
        for i,x in enumerate(a):
            if x:
                for j,y in enumerate(b): r[i+j]=(r[i+j]+x*y)%p
        for i in range(2*k-2,k-1,-1):
            c=r[i]
            if c:
                r[i]=0
                for j in range(k): r[i-k+j]=(r[i-k+j]-c*modpoly[j])%p
        return tuple(r[:k])
    els=[tuple(e) for e in itertools.product(range(p),repeat=k)]
    zero=tuple([0]*k); one=tuple([1]+[0]*(k-1))
    return els, add, rmul, zero, one, "F_%d^%d"%(p,k)

def polycompose(f,g,add,mul,zero):
    """f, g are coefficient lists (index=power). Horner."""
    r=[zero]
    for c in reversed(f):
        # r = r*g + c
        nr=[zero]*(len(r)+len(g)-1)
        for i,a in enumerate(r):
            if a==zero: continue
            for j,b in enumerate(g):
                if b==zero: continue
                nr[i+j]=add(nr[i+j],mul(a,b))
        if not nr: nr=[zero]
        nr[0]=add(nr[0],c)
        while len(nr)>1 and nr[-1]==zero: nr.pop()
        r=nr
    return r

def polys(els,zero,dg):
    """all polynomials of EXACT degree dg"""
    for lead in els:
        if lead==zero: continue
        for rest in itertools.product(els,repeat=dg):
            yield list(rest)+[lead]

CASES=[(2,1,None),(3,1,None),(5,1,None),(7,1,None),(2,2,[1,1]),(3,2,[1,0]),(2,3,[1,1,0])]
total=0; ce=[]
for (p,k,mp) in CASES:
    els,add,mul,zero,one,name = make_field(p,k,mp)
    q=len(els)
    for e in range(1,5):
        for df in range(1,5):
            m=e*df
            if m>9: continue
            if q**(e+1)*(q-1) > 300000: continue
            for g in polys(els,zero,e):
                for f in polys(els,zero,df):
                    total+=1
                    c=polycompose(f,g,add,mul,zero)
                    if len(c)!=m+1: continue
                    if c[m]==zero: continue
                    if all(c[i]==zero for i in range(m)):
                        # f o g = c_m * Y^m ; the claim is stated for MONIC Y^m,
                        # record both, and test the structural conclusion on g
                        mono = (c[m]==one)
                        shape = all(g[i]==zero for i in range(1,e))   # g = c Y^e + b
                        if not shape:
                            ce.append((name,e,df,m,list(g),list(f),c[m],mono))
print("compositions evaluated:", total)
print("counterexamples (f o g a monomial with g NOT of the form cY^e+b):", len(ce))
for x in ce[:20]: print("   ",x)
print()
print("=== targeted: the maps the plan names ===")
for (p,k,mp) in [(2,1,None),(3,1,None),(5,1,None)]:
    els,add,mul,zero,one,name=make_field(p,k,mp)
    q=len(els)
    targets={ "Y^p":[zero]*p+[one],
              "Y^p+Y":[zero,one]+[zero]*(p-2)+[one],
              "Y^{p^2}+Y^p":[zero]*p+[one]+[zero]*(p*p-p-1)+[one] }
    for gname,g in targets.items():
        e=len(g)-1
        hit=[]
        for df in range(1,4):
            if q**(df+1) > 200000: continue
            for f in polys(els,zero,df):
                c=polycompose(f,g,add,mul,zero)
                m=len(c)-1
                if all(c[i]==zero for i in range(m)):
                    hit.append((df,list(f),m))
        shape=all(g[i]==zero for i in range(1,e))
        print("  %s g=%-14s (shape cY^e+b: %s) -> f with f o g monomial, deg f<=3: %s"
              %(name,gname,shape,hit if hit else "NONE"))
print()
print("=== inseparable f: f = h(Y^p) ===")
for (p,k,mp) in [(2,1,None),(3,1,None)]:
    els,add,mul,zero,one,name=make_field(p,k,mp); q=len(els)
    bad=[]
    for dh in range(1,4):
        for h in polys(els,zero,dh):
            f=[zero]*(dh*p+1)
            for i,c in enumerate(h): f[i*p]=c
            for e in range(1,4):
                if q**(e+1)>20000: continue
                for g in polys(els,zero,e):
                    c=polycompose(f,g,add,mul,zero); m=len(c)-1
                    if m>0 and all(c[i]==zero for i in range(m)):
                        if not all(g[i]==zero for i in range(1,e)): bad.append((name,list(f),list(g)))
    print("  %s inseparable-f counterexamples: %d %s"%(name,len(bad),bad[:5]))
