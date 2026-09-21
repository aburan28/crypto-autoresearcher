#!/usr/bin/env python3
"""R4(d): re-derive (D7)'s sigma >= 1 claim from the reduced column count.

(D7): 'even under d_solve = d_ff the reduced column count sum_{j <= D}
binom(ms, j) is about B^{m H(1/(2m))}, sigma >= 1 in the sense of
IDEA-20260808-812554, so 84cdb7's conditional N^{2/(m+1)+o(1)} stake is closed
at d = 2'.

IDEA-20260808-812554 defines T_solve = B^{(m-1) sigma} and states that beating
rho requires sigma < 1 - 2/(m-1).  With d = 2 the factor base is B = 2^s, and
under d_solve = d_ff = m 2^{m-1} + floor((s - 2^{m-1})/2) + 1 the number of
columns of the Macaulay matrix in degree <= d_ff is
    C(ms, <= d_ff) ~ C(ms, s/2) = 2^{ms H(1/(2m))} = B^{m H(1/(2m))}  (s -> inf).
Charging T_solve >= columns^omega gives sigma >= omega m H(1/(2m)) / (m - 1).
Tabulated below against 1 (the literal claim) and against the admission
threshold 1 - 2/(m-1) (what the closure actually needs).
"""
import json, math, sys
from math import comb, log2

def H(x):
    if x in (0,1): return 0.0
    return -x*log2(x)-(1-x)*log2(1-x)

rows=[]
for m in range(2,13):
    h=H(1/(2*m))
    base=m*h/(m-1)
    thr=1-2/(m-1) if m>2 else float('-inf')
    rows.append({"m":m,"H(1/(2m))":round(h,4),
        "sigma_lb_omega1":round(base,4),
        "sigma_lb_omega2":round(2*base,4),
        "sigma_lb_omega2.37":round(2.37*base,4),
        "admission_threshold_1-2/(m-1)": None if m==2 else round(thr,4),
        "omega1_geq_1": base>=1,
        "omega1_excludes": (None if m==2 else base>=thr),
        "omega2_excludes": (None if m==2 else 2*base>=thr)})

# finite-s check of the asymptotic: exact column count vs B^{m H}
finite=[]
for m in (2,3):
    for s in (6,10,20,40,80):
        e=2**(m-1); n=m*s; dff=m*e+(s-e)//2+1
        cols=sum(comb(n,j) for j in range(0,min(dff,n)+1))
        finite.append({"m":m,"s":s,"n":n,"d_ff":dff,"log2_cols":round(log2(cols),3),
                       "s*m*H(1/(2m))":round(s*m*H(1/(2*m)),3),
                       "sigma_from_exact_cols_omega1":round(log2(cols)/((m-1)*s),4)})
json.dump({"asymptotic":rows,"finite_s_check":finite},sys.stdout,indent=1)
