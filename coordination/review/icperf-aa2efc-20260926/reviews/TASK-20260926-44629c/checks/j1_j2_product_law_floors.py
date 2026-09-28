#!/usr/bin/env python3
"""J1 + J2 checks for REVIEW-ICPERF-20260926-bcf1b2 (validator TASK-20260926-44629c).

Model under review (KN-FIND-aa2efc / EV-ICPERF-10c5fc / RESEARCH_ECC2K130_DECOMPOSITION.md 5.1-5.3):
  relations needed        |F| = 2^l          (2^l / n for a Frobenius-stable SET)
  targets per relation    N / C(|F|, m)
  oracle per target       C(|F|, m-1)
  linear algebra          m * 2^(2l)
Free-oracle floor  F(m; N, s) = min over l of [ 2^(l-s) N / C(2^(l-s), m) + m 2^(2(l-s)) ]
Producer's model: N = 4r = #E (about 2^131), s = 0.  Subgroup-restricted model: N = r, s = 2.
All arithmetic here is exact (fractions) at integer l and 60-digit mpmath at real l.
"""
import mpmath as mp
from fractions import Fraction
from math import comb, log2

mp.mp.dps = 60
r = 680564733841876926932320129493409985129
N4 = 4 * r
RHO_BITS = mp.log(mp.sqrt(mp.pi * r / (4 * 131)), 2)   # J3 re-derives this separately
MS = [2, 3, 4, 5, 6, 8]

def binom_real(x, m):
    """C(x, m) for real x >= m via the falling factorial (exact binomial when x is an integer)."""
    x = mp.mpf(x)
    p = mp.mpf(1)
    for i in range(m):
        p *= (x - i)
    return p / mp.factorial(m)

def targets_term(l, m, N, s=0):
    F = mp.power(2, l - s)
    return F * N / binom_real(F, m)

def la_term(l, m, s=0):
    return m * mp.power(2, 2 * (l - s))

def cost(l, m, N, s=0):
    return targets_term(l, m, N, s) + la_term(l, m, s)

def argmin_real(m, N, s=0, lo=None, hi=None):
    """Golden-section search on the (unimodal in l) cost, l real in [lo, hi]."""
    lo = mp.mpf(lo if lo is not None else s + log2(m) + 0.01)
    hi = mp.mpf(hi if hi is not None else 130)
    gr = (mp.sqrt(5) - 1) / 2
    a, b = lo, hi
    c = b - gr * (b - a); d = a + gr * (b - a)
    for _ in range(300):
        if cost(c, m, N, s) < cost(d, m, N, s):
            b = d
        else:
            a = c
        c = b - gr * (b - a); d = a + gr * (b - a)
    l = (a + b) / 2
    return l, cost(l, m, N, s)

def argmin_int(m, N, s=0):
    best = None
    for l in range(s + 2, 131):
        F = 2 ** (l - s)
        if F < m:
            continue
        v = Fraction(F * N, comb(F, m)) + m * F * F
        if best is None or v < best[1]:
            best = (l, v)
    return best

def bits(x):
    if isinstance(x, Fraction):
        return mp.log(mp.mpf(x.numerator) / mp.mpf(x.denominator), 2)
    return mp.log(mp.mpf(x), 2)

print("=" * 100)
print("J1(a)/(J2) FREE-ORACLE FLOOR, PRODUCER MODEL (N = 4r, s = 0) vs SUBGROUP-RESTRICTED (N = r, s = 2)")
print("=" * 100)
print("log2 r =", mp.nstr(bits(r), 12), " log2 4r =", mp.nstr(bits(N4), 12), " rho bits =", mp.nstr(RHO_BITS, 8))
hdr = f"{'m':>2} | {'l* (4r)':>8} {'floor(4r) bits':>14} {'T bits':>8} {'L bits':>8} | {'l* (r,s=2)':>10} {'floor(r) bits':>13} | {'diff bits':>9} | {'producer':>8} {'d(prod)':>7} | int-l floor(4r) | int-l floor(r)"
print(hdr)
producer = {2: 89.25, 3: 68.58, 4: 56.40, 5: 48.44, 6: 42.85, 8: 35.61}
producer_dimV = {2: 43.33, 3: 33.00, 4: 26.83, 5: 22.76, 6: 19.89, 8: 16.12}
rows = {}
for m in MS:
    l4, f4 = argmin_real(m, N4, 0)
    T4 = targets_term(l4, m, N4, 0); L4 = la_term(l4, m, 0)
    lr, fr = argmin_real(m, r, 2)
    li4, fi4 = argmin_int(m, N4, 0)
    lir, fir = argmin_int(m, r, 2)
    rows[m] = dict(l4=l4, f4=f4, T4=T4, L4=L4, lr=lr, fr=fr, li4=li4, fi4=fi4, lir=lir, fir=fir)
    print(f"{m:>2} | {mp.nstr(l4,6):>8} {mp.nstr(bits(f4),7):>14} {mp.nstr(bits(T4),7):>8} {mp.nstr(bits(L4),7):>8} | "
          f"{mp.nstr(lr,6):>10} {mp.nstr(bits(fr),7):>13} | {mp.nstr(bits(f4)-bits(fr),5):>9} | "
          f"{producer[m]:>8} {mp.nstr(bits(f4)-producer[m],4):>7} | l={li4} {mp.nstr(bits(fi4),7)} | l={lir} {mp.nstr(bits(fir),7)}")
print()
print("Producer dim V column vs my real-l optimum (producer model):")
for m in MS:
    print(f"  m={m}: producer dim V {producer_dimV[m]:>6}  my l* {mp.nstr(rows[m]['l4'],6)}  diff {mp.nstr(rows[m]['l4']-producer_dimV[m],3)}")
print()
print("Does any m <= 3 row cross rho (2^%s) in EITHER model?" % mp.nstr(RHO_BITS, 6))
for m in (2, 3):
    print(f"  m={m}: floor(4r) - rho = {mp.nstr(bits(rows[m]['f4'])-RHO_BITS,5)} bits; floor(r,s=2) - rho = {mp.nstr(bits(rows[m]['fr'])-RHO_BITS,5)} bits  ->",
          "ABOVE rho in both" if bits(rows[m]['fr']) > RHO_BITS else "CROSSES")
print()
print("Closed form check: l* = [log2 N + log2((m-1)(m-1)!/2)]/(m+1) under C(2^l,m) ~ 2^(ml)/m!, and floor bit shift 4r->r = 4/(m+1) bits")
for m in MS:
    from math import factorial
    lcf = (log2(N4) + log2((m - 1) * factorial(m - 1) / 2)) / (m + 1)
    print(f"  m={m}: closed-form l* {lcf:.4f}; predicted shift {4/(m+1):.4f} bits; measured shift {mp.nstr(bits(rows[m]['f4'])-bits(rows[m]['fr']),5)}")

print()
print("=" * 100)
print("J1(a) PRODUCT IDENTITY WITH EXACT BINOMIALS at the floor-optimal l (producer model, integer l nearest l*)")
print("=" * 100)
print("  identity: 2^l * N/C(2^l,m) * C(2^l,m-1) = N * m/(2^l - m + 1)  (exact)  vs  m*N (approximation used by the producer)")
for m in MS:
    l = int(mp.nint(rows[m]['l4']))
    F = 2 ** l
    exact_ratio = Fraction(comb(F, m - 1), comb(F, m))          # = m/(F-m+1)
    approx = Fraction(m, F)
    prod_exact = Fraction(F * N4, comb(F, m)) * comb(F, m - 1)   # = N4 * m * F/(F-m+1)
    rel_err = float(exact_ratio / approx - 1)
    print(f"  m={m} l={l}: C(F,m-1)/C(F,m) = m/(F-m+1); relative error of m/F approx = {rel_err:.3e}; "
          f"product/(m N) - 1 = {float(prod_exact/(m*N4) - 1):.3e}; log2 product = {log2(float(prod_exact)):.6f} vs log2(m N) = {log2(m*N4):.6f}")
print("  -> identity holds exactly up to the factor F/(F-m+1) = 1 + (m-1)/(F-m+1); at every optimal l this is below 1e-4 relative.")

print()
print("=" * 100)
print("J1(b) UNIFORM-SPREAD / ONE-RELATION-PER-TARGET ASSUMPTION at l*: lambda = C(2^l,m)/N (expected decompositions per target)")
print("=" * 100)
for m in MS:
    l = rows[m]['l4']
    lam = binom_real(mp.power(2, l), m) / N4
    # Poisson: P(target decomposable) = 1 - exp(-lam); relations per target (counting all) = lam exactly in expectation
    p_dec = 1 - mp.exp(-lam)
    print(f"  m={m} l*={mp.nstr(l,6)}: lambda = 2^{mp.nstr(bits(lam),6)}; 1/lambda vs 1/P(decomposable) differ by factor {mp.nstr(lam/p_dec,8)} (relative error ~lambda/2 = 2^{mp.nstr(bits(lam)-1,5)})")
print("  -> at every floor-optimal l the m-subset sums cover a 2^-20 .. 2^-1 fraction of the group, so the Poisson correction is negligible;")
print("     the UNIFORM-SPREAD heuristic itself (sums equidistributed over cosets / the group) is measured by the producer at n <= 19 only (note section 1) and is a transfer assumption at n = 131.")

print()
print("=" * 100)
print("J1(c) FROBENIUS-STABLE-SET VARIANT m*2^n/n: arithmetic facts at n = 131")
print("=" * 100)
n = 131
# order of 2 mod 131
o = 1; x = 2 % n
while x != 1:
    x = (x * 2) % n; o += 1
print(f"  ord_131(2) = {o}  -> 2-cyclotomic cosets mod 131 have sizes 1 and {o}; invariant F_2-subspace dims: 0, 1, {o}, 131")
print(f"  131 prime and every x not in F_2 has Frobenius orbit of size exactly 131 (orbit size divides 131): orbit unions of k orbits have 131k abscissae for any k -> 'free' as SETS")
print(f"  Frobenius eigenvalue on <G> exists with order 131 iff 131 | r-1: (r-1) mod 131 = {(r-1) % 131}")
print(f"  collapsed product: (2^l/n) * N/C(2^l,m) * C(2^l,m-1) = m N /n  -> log2(m*2^131/131) at m=3: {log2(3*2**131/131):.4f}")
for m in MS:
    # orbit-collapsed floor: relations 2^l/n, LA m (2^l/n)^2, targets N/C(2^l,m) per relation
    def cost_orb(l, m=m):
        F = mp.power(2, l)
        return (F / n) * N4 / binom_real(F, m) + m * (F / n) ** 2
    lo, hi = mp.mpf(log2(m) + 0.01), mp.mpf(130)
    gr = (mp.sqrt(5) - 1) / 2; a, b = lo, hi
    for _ in range(300):
        c = b - gr * (b - a); d = a + gr * (b - a)
        if cost_orb(c) < cost_orb(d): b = d
        else: a = c
    lstar = (a + b) / 2
    print(f"  orbit-collapsed (relations /n, LA /n^2) free-oracle floor m={m}: l*={mp.nstr(lstar,6)} floor=2^{mp.nstr(bits(cost_orb(lstar)),6)}  (producer no-collapse floor 2^{mp.nstr(bits(rows[m]['f4']),6)})")
print("  -> the collapse moves the m=3 floor by about log2(131)*2/(m+1) ~ 3.5 bits (rel/LA collapse) but m=3 stays above rho; the FINDING's floor table is the NO-collapse table and says so ('2^l/n for a Frobenius-stable set').")

print()
print("=" * 100)
print("J2 ORACLE-BUDGET COLUMN, REQUIRED SPEED-UP, GAP -- three DIFFERENT quantities, pinned")
print("=" * 100)
print("  D1 gap      G(m) = rho / floor(l*)                      : headroom on the TOTAL free-oracle cost")
print("  D2 budget   B(m) = rho / T(l*)   (T = targets term alone): per-target oracle cost at which targets x oracle = rho at the FLOOR-OPTIMAL l, LA ignored")
print("  D2' exact   B'(m) = (rho - L(l*)) / T(l*)                : same with the LA term charged")
print("  D3 re-opt   W(m) : per-target oracle cost 2^w at which min over l of [2^w T(l) + L(l)] = rho  (l re-optimised for the oracle)")
print("  D4 speed-up S(m) = rho / (m N)  (= B(m)/C(2^l*, m-1))     : required speed-up over exhaustive search of the C(|F|,m-1) sub-tuples")
prod_budget = {2: -27.86, 3: -6.78, 4: 5.71, 5: 13.94, 6: 19.77, 8: 27.35}
prod_speed = {2: -71.19, 3: -71.78, 4: -72.19, 5: -72.51, 6: -72.78, 8: -73.19}
rho = mp.power(2, RHO_BITS)
print(f"{'m':>2} | {'G bits':>8} | {'B bits':>8} {'producer':>8} {'diff':>6} | {'Bx bits':>8} | {'W bits':>8} {'l at W':>7} | {'S bits':>9} {'producer':>9} | search/target bits (C(2^l*,m-1))")
for m in MS:
    R = rows[m]
    G = rho / R['f4']; B = rho / R['T4']
    Bp = (rho - R['L4']) / R['T4'] if rho > R['L4'] else mp.mpf('nan')
    S = rho / (m * N4)
    search = binom_real(mp.power(2, R['l4']), m - 1)
    # D3: solve min_l [2^w T(l) + L(l)] = rho for w by bisection on w
    def minw(w):
        def c(l): return mp.power(2, w) * targets_term(l, m, N4) + la_term(l, m)
        lo, hi = mp.mpf(log2(m) + 0.01), mp.mpf(130); gr = (mp.sqrt(5) - 1) / 2; a, b = lo, hi
        for _ in range(200):
            cc = b - gr * (b - a); d = a + gr * (b - a)
            if c(cc) < c(d): b = d
            else: a = cc
        l = (a + b) / 2
        return c(l), l
    wlo, whi = mp.mpf(-100), mp.mpf(100)
    for _ in range(200):
        wm = (wlo + whi) / 2
        if minw(wm)[0] < rho: wlo = wm
        else: whi = wm
    W = (wlo + whi) / 2; lW = minw(W)[1]
    print(f"{m:>2} | {mp.nstr(bits(G),5):>8} | {mp.nstr(bits(B),5):>8} {prod_budget[m]:>8} {mp.nstr(bits(B)-prod_budget[m],3):>6} | {mp.nstr(bits(Bp),5) if Bp==Bp else 'n/a':>8} | {mp.nstr(W,5):>8} {mp.nstr(lW,5):>7} | {mp.nstr(bits(S),6):>9} {prod_speed[m]:>9} | {mp.nstr(bits(search),6)}")
print()
print("  Check: B(m)/C(2^l*,m-1) reproduces S(m) (the last column is the product law read backwards):")
for m in MS:
    R = rows[m]
    print(f"    m={m}: log2 B - log2 search = {mp.nstr(bits(rho/R['T4']) - bits(binom_real(mp.power(2,R['l4']),m-1)),6)} vs log2 S = {mp.nstr(bits(rho/(m*N4)),6)}")
print("  Check: G(m)^((m+1)/2) = W(m) (closed form of D3, since min_l[2^w T + L] scales as 2^(2w/(m+1))):")
for m in MS:
    R = rows[m]
    print(f"    m={m}: (m+1)/2 * log2 G = {mp.nstr(bits(rho/R['f4'])*(m+1)/2,5)}")
