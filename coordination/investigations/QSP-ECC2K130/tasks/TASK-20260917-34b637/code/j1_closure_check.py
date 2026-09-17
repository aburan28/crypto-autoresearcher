"""J1(a): is the injection into the RIGHT set?

(A) claims every K-root of L is a root of D.  It does NOT claim that every
root of L in the algebraic closure is a root of D -- and it must not, because
if D vanished on all p^{n'} closure-roots of L then deg D >= deg L = p^{n'}
and the bound would be vacuous.  This script measures, per candidate:

    N        = deg gcd(X^{p^n} - X, L)   (the K-roots of L)
    gDL      = deg gcd(D, L)             (the closure-roots of L that D kills,
                                          counted with multiplicity in L)
    deg L    = p^{n'}

and checks (1) G | D  (the injection, again, by an independent route) and
(2) gDL < deg L strictly somewhere, i.e. the restriction to K is load-bearing.

Pure Python, small degrees only.  Independent of everything else in this task
directory and of the producer's implementation.
"""
def trim(a):
    while a and a[-1] == 0: a.pop()
    return a
def padd(a,b,p):
    m=max(len(a),len(b)); o=[0]*m
    for i,c in enumerate(a): o[i]=(o[i]+c)%p
    for i,c in enumerate(b): o[i]=(o[i]+c)%p
    return trim(o)
def psub(a,b,p):
    m=max(len(a),len(b)); o=[0]*m
    for i,c in enumerate(a): o[i]=(o[i]+c)%p
    for i,c in enumerate(b): o[i]=(o[i]-c)%p
    return trim(o)
def pmul(a,b,p):
    if not a or not b: return []
    o=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        if x:
            for j,y in enumerate(b): o[i+j]=(o[i+j]+x*y)%p
    return trim(o)
def pmod(a,b,p):
    a=a[:]; db=len(b)-1; inv=pow(b[db],p-2,p)
    for i in range(len(a)-1,db-1,-1):
        if a[i]:
            f=a[i]*inv%p
            for j in range(db+1): a[i-db+j]=(a[i-db+j]-f*b[j])%p
    return trim(a)
def pgcd(a,b,p):
    a=trim(a[:]); b=trim(b[:])
    while b: a,b=b,pmod(a,b,p)
    if a:
        inv=pow(a[-1],p-2,p); a=[c*inv%p for c in a]
    return a
def pcompose(f,g,p):
    o=[]
    for c in reversed(f): o=padd(pmul(o,g,p),[c%p],p)
    return trim(o)
def xpn_mod(M,n,p):                      # X^{p^n} mod M, generic p-th powering
    cur=[0,1]
    for _ in range(n):
        h=[0]*((len(cur)-1)*p+1)
        for i,c in enumerate(cur): h[i*p]=c
        cur=pmod(trim(h),M,p)
    return cur

CASES=[(2,7,3),(2,4,3),(2,11,4),(3,5,3),(3,7,3),(3,4,3),(5,4,3),(5,5,3)]
print(f"{'p':>2} {'n':>3} {'np':>3} {'d':>2} {'lam':>18} {'degL':>5} {'N':>4} {'degD':>5} "
      f"{'gcd(D,L)':>9} {'G|D':>4} {'gDL<degL':>9}")
anystrict=False; anyfail=False; rows=0
for (p,n,npr) in CASES:
    q,r=divmod(n,npr); D_=p**npr
    for d in range(2,5):
        for code in range((p-1)*p**d):
            t=code; lead=t%(p-1)+1; t//=(p-1)
            lam=[0]*(d+1)
            for i in range(d): lam[i]=t%p; t//=p
            lam[d]=lead
            L=[(-c)%p for c in lam]+[0]*(D_-d-1)+[1]
            L=trim(L)
            Lq1=lam[:]
            for _ in range(q): Lq1=pcompose(Lq1,lam,p)
            mono=[0]*(p**(npr-r))+[1]
            Dp=psub(Lq1,mono,p)
            if not Dp: continue                       # degenerate, excluded from (A)
            G=pgcd(psub(xpn_mod(L,n,p),[0,1],p),L,p)
            N=len(G)-1 if G else 0
            gDL=len(pgcd(Dp,L,p))-1
            GdivD = (not pmod(Dp,G,p)) if N>0 else True
            strict = gDL < D_
            anystrict |= strict
            if not GdivD: anyfail=True
            rows+=1
            if code < 2 and d == 2:
                s="+".join(f"{c}X^{i}" for i,c in enumerate(lam) if c)
                print(f"{p:>2} {n:>3} {npr:>3} {d:>2} {s:>18} {D_:>5} {N:>4} {len(Dp)-1:>5} "
                      f"{gDL:>9} {str(GdivD):>4} {str(strict):>9}")
print()
print("candidates checked                                   :", rows)
print("any candidate where the K-root set G does NOT divide D:", anyfail)
print("at least one candidate with deg gcd(D,L) < deg L      :", anystrict)
print("  -> D does NOT vanish on every closure-root of L, so the restriction")
print("     of (A)'s injection to x in K is doing real work and the bound is")
print("     not vacuous by construction.")
