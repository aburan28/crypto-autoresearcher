"""J2 (c): is the characterisation of D = 0 EXHAUSTIVE?  Search ALL lambda
(F_2 coefficients at several cells; ALL K-coefficients at two cells) for
D = 0, and check every hit is of the claimed form c X^{2^j} + b."""
import sys, random, math
sys.path.insert(0,"/home/user/crypto-autoresearcher/experiments/EXP-QSP-33b442/implementation")
import qspcore as Q
from qspcore import (KField, deg, poly_str, difference_poly_f2, deg_D_and_degenerate,
                     difference_poly_k, kp_deg, kp_from_f2, is_irreducible, polymod, square)
EXTRA={5:0b100101,6:0b1000011,8:0b100011011,9:0b1000010001,10:0b10000001001}
for n,f in EXTRA.items():
    assert is_irreducible(f); Q.FIELD_POLY.setdefault(n,f)

print("=== A. F_2 coefficients: ALL lambda of ALL degrees 1..7 at each cell ===")
tot=0; hits=[]
for (n,npr) in [(4,3),(6,4),(6,5),(8,5),(8,6),(8,7),(9,4),(12,5),(12,6),(12,4),(6,3),
                (7,3),(11,6),(13,7),(11,4),(13,5)]:
    q,r=divmod(n,npr)
    for d in range(1,8):
        if d >= (1<<npr): continue
        for low in range(1<<d):
            lam=(1<<d)|low
            tot+=1
            _,isdeg = deg_D_and_degenerate(lam,n,npr)
            if isdeg: hits.append((n,npr,q,r,d,lam,poly_str(lam)))
print("lambda tested:",tot," D==0 hits:",len(hits))
for h in hits: print("   n=%d n'=%d q=%d r=%d d=%d lam=%s"%(h[0],h[1],h[2],h[3],h[4],h[6]))
# claimed form over F_2: c=1 so lambda = X^{2^j} or X^{2^j}+1
def claimed(lam,n,npr):
    q,r=divmod(n,npr)
    if (npr-r)%(q+1): return False
    j=(npr-r)//(q+1)
    return j>=1 and lam in ((1<<(1<<j)), (1<<(1<<j))|1)
print("every hit has the claimed form c X^{2^j}+b:", all(claimed(h[5],h[0],h[1]) for h in hits))
print("hits with b=1 (lambda = X^{2^j}+1):", [h[6] for h in hits if h[5]&1])

print()
print("=== B. FULL K-coefficient sweep, every lambda of every degree 1..3 ===")
for (n,npr,dmax) in [(4,3,3),(6,4,2)]:
    K=KField(n); qn=1<<n
    q,r=divmod(n,npr)
    found=[]; cnt=0
    for d in range(1,dmax+1):
        # lambda = sum_{i<=d} a_i Y^i, a_d != 0
        import itertools
        for lead in range(1,qn):
            for rest in itertools.product(range(qn), repeat=d):
                coeffs=list(rest)+[lead]
                cnt+=1
                D=difference_poly_k(K,coeffs,n,npr)
                if not D: found.append((d,coeffs))
    print(" (n,n')=(%d,%d) q=%d r=%d : %d lambda tested, %d with D=0"%(n,npr,q,r,cnt,len(found)))
    j=(npr-r)//(q+1) if (npr-r)%(q+1)==0 else None
    okform=True; forms=[]
    for (d,co) in found:
        # claimed: lambda = c X^{2^j} + b  <=> coeffs[2^j]!=0, coeffs[0] free, all else 0
        e=1<<j
        good = (d==e) and all(co[i]==0 for i in range(1,len(co)) if i!=e)
        okform &= good
        forms.append((d,co[e],co[0],good))
    print("   every D=0 lambda has form c X^{2^%s} + b : %s"%(j,okform))
    cs=sorted(set(f[1] for f in forms)); bs=sorted(set(f[2] for f in forms))
    print("   distinct c values realised: %d of %d nonzero K elements; b values: %s"%(len(cs),qn-1,bs))
    # does EVERY (c,b) of that shape give D=0?  (the converse)
    e=1<<j; allshape=0; degshape=0
    for c in range(1,qn):
        for b in range(qn):
            co=[b]+[0]*(e-1)+[c]
            allshape+=1
            if not difference_poly_k(K,co,n,npr): degshape+=1
    print("   converse: of %d lambda of shape cX^{2^j}+b, %d are degenerate (D=0)"%(allshape,degshape))
