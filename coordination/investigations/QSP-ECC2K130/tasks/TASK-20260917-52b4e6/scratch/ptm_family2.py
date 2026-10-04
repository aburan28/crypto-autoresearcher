"""PROVES-TOO-MUCH, FAMILY 2: the LINEARIZED family of KN-LIT-4fe9d2 Theorem 1,
where beta >= 3/4 is ALREADY KNOWN.  Two failure signatures to test:

 (S1) The argument must NOT derive beta >= 3/4 GENERALLY (that is Theorem 1's
      result and (B) is not restricted to linearized lambda).
 (S2) Where (B) is STRONGER than Theorem 1 (n/(n+n'-r) > 3/4), hunt for a
      LINEARIZED complete splitter with beta strictly between n/(n+n'-r) and
      3/4: such an object satisfies Theorem 1 and REFUTES (B).

The whole F_2-linearized slice is decided by PROPOSITION 2 alone -- an
F_2-coefficient linearized L_f splits completely iff f | T^n - 1 -- so this
test uses NO instrument of the experiment at all.  We enumerate every divisor
f of T^n - 1 over F_2 of degree n' with n' not dividing n, read off
l = deg(f - T^{n'}) (so d = 2^l), and test (B) directly."""
import sys, math, json
sys.path.insert(0,"/home/user/crypto-autoresearcher/experiments/EXP-QSP-33b442/implementation")
from qspcore import deg, gcd, polydivmod, ddf_factor, poly_str, is_irreducible
import random, itertools
rng=random.Random(20260917)

def sqfree_factor_xn1(n):
    """all monic irreducible factors of T^n - 1 over F_2 with multiplicities."""
    # T^n - 1 = (T^{n/2^v} - 1)^{2^v} with n = 2^v * m, m odd
    v=0; m=n
    while m%2==0: m//=2; v+=1
    g=(1<<m)^1
    # g is squarefree; factor by ddf over the splitting behaviour: all irreducible
    # factors of T^m-1 have degree = ord_d(2) for d | m.  Use ddf_factor with
    # the multiplicative order bound.
    facs=[]
    rest=g
    k=1
    while deg(rest)>0:
        # gcd(rest, T^{2^k}-T)
        x=0b10
        for _ in range(k):
            # square mod rest
            s=0; i=0; t=x
            while t:
                if t&1: s|=1<<(2*i)
                t>>=1; i+=1
            while s and deg(s)>=deg(rest): s ^= rest << (deg(s)-deg(rest))
            x=s
        h=x^0b10
        part = rest if h==0 else gcd(rest,h)
        if deg(part)>0:
            from qspcore import _edf
            facs += [(f,1<<v) for f in _edf(part,k,rng)]
            rest = polydivmod(rest,part)[0]
        k+=1
        if k>n+2: break
    assert deg(rest)<=0, deg(rest)
    return facs

def clmul(a,b):
    r=0
    while a:
        if a&1: r^=b
        a>>=1; b<<=1
    return r

def divisors_of_degree(facs, target):
    """all monic divisors of prod f^e with degree == target"""
    out=[]
    items=[(f,e) for (f,e) in facs]
    def rec(i,cur,dg):
        if dg>target: return
        if i==len(items):
            if dg==target: out.append(cur)
            return
        f,e=items[i]; df=deg(f); acc=cur
        for k in range(e+1):
            if dg+k*df<=target: rec(i+1,acc,dg+k*df)
            else: break
            acc=clmul(acc,f)
        return
    rec(0,1,0)
    return out

print("=== (S2) every F_2-linearized COMPLETE SPLITTER, decided by Proposition 2 alone ===")
print("%-4s %-4s %-3s %-3s %-4s %-10s %-10s %-9s %-10s %-8s"%(
      "n","n'","q","r","l","beta","(B) bound","beta>=(B)","Thm1 3/4","beta>=3/4"))
rows=[]; viol=[]; between=[]
for n in range(3,41):
    facs=sqfree_factor_xn1(n)
    assert sum(deg(f)*e for f,e in facs)==n, (n,[(deg(f),e) for f,e in facs])
    for npr in range(2,n):
        if n%npr==0: continue                     # Family 2 is about n' NOT dividing n
        q,r=divmod(n,npr)
        for f in divisors_of_degree(facs,npr):
            g=f^(1<<npr)
            if g==0: continue                      # lambda = 0, d = 0, excluded (d>=1)
            l=deg(g)
            if l<1: continue                       # lambda = constant
            beta=l*n/(npr*npr)
            B=n/(n+npr-r)
            rows.append((n,npr,q,r,l,beta,B))
            if beta < B - 1e-12: viol.append((n,npr,q,r,l,beta,B))
            if B > 0.75 and 0.75 <= beta < B: between.append((n,npr,q,r,l,beta,B))
            if n in (7,11,31,131) or beta<B+1e-9:
                print("%-4d %-4d %-3d %-3d %-4d %-10.6f %-10.6f %-9s %-10s %-8s"%(
                      n,npr,q,r,l,beta,B,beta>=B-1e-12,"0.75",beta>=0.75))
print()
print("F_2-linearized complete splitters found (n<=40, n' not dividing n):",len(rows))
print("VIOLATIONS of (B) beta >= n/(n+n'-r):",len(viol),viol)
print("objects with 3/4 <= beta < (B)'s bound (would satisfy Thm 1 and refute (B)):",len(between),between)
print("objects with beta < 3/4 (so (B) does NOT derive Theorem 1's bound generally):",
      sum(1 for x in rows if x[5]<0.75), [x for x in rows if x[5]<0.75][:12])
print()
print("=== n = 131 itself ===")
facs=sqfree_factor_xn1(131)
print("  T^131 - 1 factors over F_2 into degrees:", sorted(deg(f) for f,e in facs), "(multiplicities:",[e for f,e in facs],")")
for npr in range(2,131):
    if 131%npr==0: continue
    ds=divisors_of_degree(facs,npr)
    if not ds: continue
    q,r=divmod(131,npr)
    for f in ds:
        g=f^(1<<npr)
        if g==0: continue
        l=deg(g)
        if l<1: continue
        beta=l*131/(npr*npr); B=131/(131+npr-r)
        print("  n'=%d q=%d r=%d l=%d d=2^%d beta=%.6f (B) bound=%.6f  beta>=(B): %s  beta>=3/4: %s"
              %(npr,q,r,l,l,beta,B,beta>=B,beta>=0.75))
print()
print("=== (S1) does (B) derive beta >= 3/4 generally?  smallest (B) bound over n'<n, n' not | n ===")
worst=[]
for n in (7,11,31,131,257):
    m=min((131 if n==131 else n)/((131 if n==131 else n)+npr-((131 if n==131 else n)%npr))
          for npr in range(2,n) if n%npr)
    worst.append((n,m))
for n,m in worst: print("  n=%-5d min over n' of n/(n+n'-r) = %.6f   (3/4 = 0.75 -> (B) is WEAKER than Thm 1 here: %s)"%(n,m,m<0.75))
