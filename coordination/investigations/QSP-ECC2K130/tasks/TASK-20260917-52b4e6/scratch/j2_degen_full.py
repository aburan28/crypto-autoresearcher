"""J2: the FULL degenerate family (c != 1, b != 0) -- does ANY degenerate L
split completely?  Exhaustive over all K-coefficient lambda at two cells."""
import sys, random, itertools
sys.path.insert(0,"/home/user/crypto-autoresearcher/experiments/EXP-QSP-33b442/implementation")
import qspcore as Q
from qspcore import (KField, deg, difference_poly_k, kp_eval, is_irreducible, i1_brute_k, i3_injection_k)
EXTRA={5:0b100101,6:0b1000011}
for n,f in EXTRA.items():
    assert is_irreducible(f); Q.FIELD_POLY.setdefault(n,f)
rng=random.Random(20260917)
for (n,npr) in [(4,3),(6,4),(6,5)]:
    K=KField(n); qn=1<<n; q,r=divmod(n,npr); j=(npr-r)//(q+1); e=1<<j
    found=[]
    for c in range(1,qn):
        for b in range(qn):
            co=[b]+[0]*(e-1)+[c]
            if difference_poly_k(K,co,n,npr): continue    # not degenerate
            # exhaustive distinct-root count of L over K
            cnt=0
            for x in range(qn):
                if K.pow2k(x,npr) == kp_eval(K,co,x): cnt+=1
            i1 = i1_brute_k(K,co,npr)
            i3 = i3_injection_k(K,co,npr,rng)
            found.append((c,b,cnt,i1,i3.get("degenerate"),i3.get("N")))
    Ns=sorted(set(f[2] for f in found))
    print("(n,n')=(%d,%d) q=%d r=%d j=%d d=2^%d: %d degenerate lambda (c X^{2^j}+b over K)"%(n,npr,q,r,j,j,len(found)))
    print("   distinct N values: %s   bound 2^{n'-j} = %d   2^{n'} = %d"%(Ns, 1<<(npr-j), 1<<npr))
    print("   all N <= 2^{n'-j}: %s ;  any N = 2^{n'} (complete split): %s"
          %(all(f[2]<=(1<<(npr-j)) for f in found), any(f[2]==(1<<npr) for f in found)))
    print("   I1 agrees with brute count on all: %s ; i3 flags degenerate on all: %s"
          %(all(f[2]==f[3] for f in found), all(f[4] for f in found)))
    mx=max(found,key=lambda t:t[2]); print("   max N = %d at (c=%d,b=%d)"%(mx[2],mx[0],mx[1]))
