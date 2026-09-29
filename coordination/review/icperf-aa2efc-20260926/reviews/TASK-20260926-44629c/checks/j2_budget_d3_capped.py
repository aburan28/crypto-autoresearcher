#!/usr/bin/env python3
"""J2 addendum: the re-optimised per-target oracle budget D3 with the producer's own one-attempt-per-relation cap
(targets per relation = max(1, N/C(2^l, m)), as in the producer's 5.1 table where the m=3 column reads 2^0 at dim V = 52),
and the negation-folded floor variant (relations |F|/2, LA m(|F|/2)^2)."""
import mpmath as mp
from math import log2, factorial
mp.mp.dps = 40
r = 680564733841876926932320129493409985129; N4 = 4 * r
RHO = mp.sqrt(mp.pi * r / (4 * 131)); RHO_BITS = mp.log(RHO, 2)
def binom_real(x, m):
    x = mp.mpf(x); p = mp.mpf(1)
    for i in range(m): p *= (x - i)
    return p / mp.factorial(m)
def cost(l, m, N, w=0, div=1):
    F = mp.power(2, l); R = F / div
    tpr = N / binom_real(F, m)
    if tpr < 1: tpr = mp.mpf(1)
    return R * tpr * mp.power(2, w) + m * R * R
def argmin(m, N, w=0, div=1):
    lo, hi = mp.mpf(log2(m) + 0.01), mp.mpf(131)
    gr = (mp.sqrt(5) - 1) / 2; a, b = lo, hi
    for _ in range(250):
        c = b - gr * (b - a); d = a + gr * (b - a)
        if cost(c, m, N, w, div) < cost(d, m, N, w, div): b = d
        else: a = c
    l = (a + b) / 2
    return l, cost(l, m, N, w, div)
print("D3 (capped): per-target oracle cost 2^w at which min over l of [2^l max(1, N/C(2^l,m)) 2^w + m 2^(2l)] = rho, N = 4r")
print(f"{'m':>2} | {'w bits':>7} {'l at w':>7} | yield-cap l_cap=(131+log2 m!)/m | IDEA-20260926-4b65e3 quotes | D1 gap | D2 rho/T(l*)")
gapref = {2: -28.443, 3: -7.776, 4: 4.404, 5: 12.374, 6: 17.959, 8: 25.200}
d2ref = {2: -27.858, 3: -6.776, 4: 5.726, 5: 13.959, 6: 19.766, 8: 27.370}
q = {4: 11, 5: 33, 6: 37, 8: 42}
for m in (2, 3, 4, 5, 6, 8):
    lo, hi = mp.mpf(-150), mp.mpf(150)
    for _ in range(200):
        wm = (lo + hi) / 2
        if argmin(m, N4, wm)[1] < RHO: lo = wm
        else: hi = wm
    w = (lo + hi) / 2; lw = argmin(m, N4, w)[0]
    lcap = (131 + log2(factorial(m))) / m
    print(f"{m:>2} | {mp.nstr(w,5):>7} {mp.nstr(lw,5):>7} | {lcap:>8.2f} | {q.get(m,'-'):>6} | {gapref[m]:>7} | {d2ref[m]:>7}")
print("  (at m >= 5 the cap binds: l sits at l_cap, targets = relations = 2^l_cap, budget = rho/2^l_cap; at m = 4 the linear algebra binds first)")
print()
print("Negation-folded floor variant (relations |F|/2, LA m (|F|/2)^2) -- the finding charges |F| relations for |F| points although log(-P) = -log(P):")
print(f"{'m':>2} | {'finding (N=4r, |F|)':>20} | {'N=4r, |F|/2':>12} | {'N=r, |F|/2':>11} | shift vs finding (bits) | m<=3 vs rho")
for m in (2, 3, 4, 5, 6, 8):
    f0 = argmin(m, N4, 0, 1)[1]; f1 = argmin(m, N4, 0, 2)[1]; f2 = argmin(m, r, 0, 2)[1]
    print(f"{m:>2} | {mp.nstr(mp.log(f0,2),6):>20} | {mp.nstr(mp.log(f1,2),6):>12} | {mp.nstr(mp.log(f2,2),6):>11} | {mp.nstr(mp.log(f0,2)-mp.log(f2,2),4):>23} | {('above rho by ' + mp.nstr(mp.log(f2,2)-RHO_BITS,4) + ' bits') if m <= 3 else ''}")
print("  closed form: the negation fold (relations |F|/2 at the same C(|F|,m) sums) is the finding's formula with N -> N/2^m, so it shifts the floor by 2m/(m+1) bits; with the cofactor (N -> N/4, 4/(m+1) bits) the combined shift is (4+2m)/(m+1) bits: 2.67, 2.5, 2.4, 2.33, 2.29, 2.22 at m = 2,3,4,5,6,8. The product-law identity itself moves by the cofactor only (2 bits); the negation fold is a relation-count correction the identity does not see.")
print()
print("D3 (capped) under the corrected model (N = r, relations |F|/2): per-target budget that ties rho with l re-optimised")
for m in (4, 5, 6, 8):
    lo, hi = mp.mpf(-150), mp.mpf(150)
    for _ in range(200):
        wm = (lo + hi) / 2
        if argmin(m, r, wm, 2)[1] < RHO: lo = wm
        else: hi = wm
    w = (lo + hi) / 2; lw = argmin(m, r, w, 2)[0]
    print(f"  m={m}: w = {mp.nstr(w,5)} bits at l = {mp.nstr(lw,5)}   (finding-model D3: {q[m]} ; gap D1 corrected = {mp.nstr(RHO_BITS - mp.log(argmin(m, r, 0, 2)[1],2),4)} bits)")
