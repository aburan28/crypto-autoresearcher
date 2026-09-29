"""PROVES-TOO-MUCH FAMILY 1, broad sweep: EVERY lambda of degree 1..8 at every
r = 0 cell with n <= 14.  Two questions:
  (Q1) does (A) in its FULL strength (N <= deg D, not just N <= max(...)) hold?
  (Q2) which objects at r = 0 SPLIT COMPLETELY, and is the derivation vacuous
       on exactly those?"""
import sys, random
sys.path.insert(0,"/home/user/crypto-autoresearcher/experiments/EXP-QSP-33b442/implementation")
import qspcore as Q
from qspcore import (KField, deg, poly_str, difference_poly_f2, deg_D_and_degenerate,
                     i1_brute_f2, i2_gcd_f2, is_irreducible)
EXTRA={2:0b111,3:0b1011,5:0b100101,6:0b1000011,8:0b100011011,9:0b1000010001,
       10:0b10000001001,14:0b100000000101011}
for n,f in EXTRA.items():
    assert deg(f)==n and is_irreducible(f); Q.FIELD_POLY.setdefault(n,f)
rng=random.Random(20260917)

tested=0; viol_degD=[]; viol_max=[]; complete=[]; nonvac=[]
for n in range(3,15):
    for npr in range(1,n+1):
        if n%npr: continue
        q,r=divmod(n,npr); assert r==0
        if npr>10: continue                       # deg L = 2^{n'} must be buildable
        K=KField(n)
        for d in range(1,9):
            if d>=(1<<npr): continue
            if d**(q+1) > 3_000_000: continue     # deg D buildable
            for low in range(1<<d):
                lam=(1<<d)|low
                degD,isdeg = deg_D_and_degenerate(lam,n,npr)
                N = i1_brute_f2(K,lam,npr)[0]
                N2 = i2_gcd_f2(n,npr,lam)
                assert N==N2,(n,npr,lam,N,N2)
                tested+=1
                mx = max(d**(q+1), 1<<npr)        # p^{n'-r} = p^{n'} at r=0
                if not isdeg and N > degD: viol_degD.append((n,npr,d,poly_str(lam),N,degD))
                if N > mx: viol_max.append((n,npr,d,poly_str(lam),N,mx))
                if N == (1<<npr):
                    complete.append((n,npr,q,d,poly_str(lam),N,degD if not isdeg else "D=0",mx))
                if (not isdeg) and degD < (1<<npr): nonvac.append((n,npr,d,N,degD))
print("r = 0 lambda tested (exhaustive, degree 1..8, n <= 14, n' <= 10):", tested)
print()
print("(Q1) violations of the FULL form  N <= deg D :", len(viol_degD), viol_degD[:10])
print("     violations of the MAX form   N <= max(d^{q+1}, p^{n'}) :", len(viol_max), viol_max[:10])
print()
print("(Q2) objects at r = 0 that SPLIT COMPLETELY (N = 2^{n'}):", len(complete))
for c in complete: print("     n=%d n'=%d q=%d d=%d lam=%-30s N=%d degD=%s maxbound=%d  BOUND VACUOUS: %s"
                         %(c[0],c[1],c[2],c[3],c[4],c[5],c[6],c[7], c[7]>=c[5]))
print()
print("     candidates where deg D < 2^{n'} (derivation NON-vacuous at r=0):", len(nonvac))
print("     of those, any that split completely:",
      [x for x in nonvac if x[3]==(1<<x[1])])
print()
print("CONCLUSION TEST: is every completely splitting r=0 object one on which the")
print("derivation is VACUOUS (deg D >= 2^{n'} and max >= 2^{n'})? ->",
      all(c[6]=="D=0" or c[6]>= (1<<c[1]) for c in complete) and all(c[7]>=c[5] for c in complete))
