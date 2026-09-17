"""PROVES-TOO-MUCH, FAMILY 1: n' | n  (r = 0), where the conclusion of (B) is
KNOWN FALSE (Diem's subfield family splits completely with beta arbitrarily
small).  Required failure signature:
 (i)  the bound must be VACUOUS at r = 0, and
 (ii) the vacuity must be a CONSEQUENCE of the derivation, not an accident.

The sharp test for (ii): (A) bounds N by deg D, and at r = 0 the two terms of
the max are d^{q+1} and p^{n'} = deg L.  When d^{q+1} = p^{n'} the LEADING
TERMS OF D CAN CANCEL, so deg D < p^{n'} and the derivation would then yield a
bound STRICTLY BELOW p^{n'} at r = 0 -- exactly the failure signature.  We run
every such (n, n', d) we can enumerate and count the roots exhaustively."""
import sys, random, json, math
sys.path.insert(0,"/home/user/crypto-autoresearcher/experiments/EXP-QSP-33b442/implementation")
import qspcore as Q
from qspcore import (KField, deg, poly_str, difference_poly_f2, deg_D_and_degenerate,
                     i1_brute_f2, i2_gcd_f2, i3_injection_f2, is_irreducible, polymod, square)
EXTRA={2:0b111,3:0b1011,5:0b100101,6:0b1000011,8:0b100011011,9:0b1000010001,10:0b10000001001,
       14:0b100000000101011,15:0b1000000000000011,16:0b10001000000001011}
for n,f in EXTRA.items():
    assert deg(f)==n and is_irreducible(f); Q.FIELD_POLY.setdefault(n,f)
rng=random.Random(20260917)

print("=== (i) is the bound vacuous at r = 0, for EVERY d? ===")
vac=[]
for n in range(2,33):
    for npr in range(1,n+1):
        if n % npr: continue
        q,r=divmod(n,npr); assert r==0
        for d in range(1,30):
            bnd = max(d**(q+1), 1<<npr)
            vac.append(bnd >= (1<<npr))
print("  max(d^{q+1}, p^{n'-r}) >= p^{n'} = deg L on all %d (n,n',d) with n'|n: %s"%(len(vac),all(vac)))
print("  reason: at r = 0 the second term of the max IS p^{n'} = deg L, structurally.")
print()
print("=== (ii) where CAN the derivation give a bound strictly below p^{n'} at r=0? ===")
eq=[]
for n in range(2,40):
    for npr in range(1,n+1):
        if n % npr: continue
        q,r=divmod(n,npr)
        target=1<<npr
        d=round(target**(1.0/(q+1)))
        for dd in (d-1,d,d+1):
            if dd>=1 and dd**(q+1)==target: eq.append((n,npr,q,dd))
eq=sorted(set(eq))
print("  (n,n',q,d) with n'|n and d^{q+1} = 2^{n'} EXACTLY (leading terms may cancel):")
for e in eq: print("    ",e)
print()
print("=== the test: exhaustive over every lambda of that degree, all three instruments ===")
hdr=("n","n'","q","d","lam","degD","N","2^n'","deg D < 2^n'?","N<=degD","N=2^n' (complete)?","VERDICT")
print("%-3s %-3s %-2s %-3s %-22s %-7s %-5s %-6s %-14s %-8s %-19s %s"%hdr)
bad=[]
tested=0
for (n,npr,q,d) in eq:
    if n>16 or n<3: continue
    if (1<<d) > 70000: continue
    K=KField(n)
    for low in range(1<<d):
        lam=(1<<d)|low
        degD,isdeg = deg_D_and_degenerate(lam,n,npr)
        D = difference_poly_f2(lam,n,npr)
        N = i1_brute_f2(K,lam,npr)[0]
        N2 = i2_gcd_f2(n,npr,lam)
        assert N==N2,(n,npr,lam,N,N2)
        tested+=1
        strictly_below = (not isdeg) and degD < (1<<npr)
        complete = (N == (1<<npr))
        ok = isdeg or (N <= degD)
        broke = strictly_below and complete
        if broke: bad.append((n,npr,d,lam,poly_str(lam),degD,N))
        if low < 4 or strictly_below or complete:
            print("%-3d %-3d %-2d %-3d %-22s %-7s %-5d %-6d %-14s %-8s %-19s %s"%(
                n,npr,q,d,poly_str(lam), "D=0" if isdeg else degD, N, 1<<npr,
                strictly_below, ok, complete, "BREAKS (A)" if broke else "ok"))
print()
print("lambda tested at the equal-degree r=0 boundary:",tested)
print("objects where the derivation gave a bound < 2^{n'} AND the object splits completely:",len(bad),bad)
