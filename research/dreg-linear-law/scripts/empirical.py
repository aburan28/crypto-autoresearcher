#!/usr/bin/env python3
"""Exact-integer d_reg ladder to large n, marginal slope, and c* + a n^{1/3} fit."""
from math import comb
import time, json

CSTAR = 0.23747907091468   # analytic saddle constant

def dreg(n):
    # tight upper bound: c* n + ~1.5 n^{1/3} + margin
    N = int(0.245*n) + 20
    a = [comb(2*n, j) if j <= 2*n else 0 for j in range(N)]
    for d in ([2]*n + [3]*n):        # divide by (1+z^2)^n then (1+z^3)^n
        for j in range(d, N):
            a[j] -= a[j-d]
    for D in range(N):
        if a[D] <= 0:
            return D
    raise RuntimeError(f"N={N} too small for n={n}")

ladder = [1000,2000,3000,4000,6000,8000,10000,12000,16000,20000]
res={}
for n in ladder:
    t=time.time()
    d=dreg(n)
    res[n]=d
    print(f"n={n:6d}  d_reg={d:6d}  d/n={d/n:.6f}  excess/n^(1/3)={(d-CSTAR*n)/n**(1/3):.5f}  [{time.time()-t:.1f}s]",flush=True)

print("\n--- marginal slopes (d_reg(n2)-d_reg(n1))/(n2-n1) ---")
ks=sorted(res)
for i in range(1,len(ks)):
    n1,n2=ks[i-1],ks[i]
    print(f"[{n1:6d},{n2:6d}] slope={ (res[n2]-res[n1])/(n2-n1):.6f}")

# least-squares fit d = c*n + a n^{1/3} + b  (test if c recovered ~ CSTAR)
import numpy as np
ns=np.array(ks,float); ds=np.array([res[k] for k in ks],float)
Amat=np.vstack([ns, ns**(1/3), np.ones_like(ns)]).T
coef,*_=np.linalg.lstsq(Amat,ds,rcond=None)
print(f"\n3-param fit d_reg ~ c*n + a n^(1/3) + b:")
print(f"  c (slope)  = {coef[0]:.6f}   [analytic c* = {CSTAR:.6f}, diff {coef[0]-CSTAR:+.2e}]")
print(f"  a (n^1/3)  = {coef[1]:.5f}")
print(f"  b          = {coef[2]:.4f}")
# residuals
pred=Amat@coef
print("  max resid  =", float(np.max(np.abs(ds-pred))))

json.dump({"cstar_analytic":CSTAR,"dreg":res,"fit_c":float(coef[0]),
           "fit_a":float(coef[1]),"fit_b":float(coef[2])}, open("empirical_out.json","w"), indent=2)
