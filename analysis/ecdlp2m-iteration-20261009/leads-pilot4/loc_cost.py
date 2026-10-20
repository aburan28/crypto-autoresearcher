"""Locality-restricted closure cost at n=131 (derivation, not a measurement)."""
import sys, math
from math import comb, log2
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "wwit-ecc2k130"))
import wwit_model as W

def block_vars(n, k, m):
    # segments: ('u',i) n bits in blocks i,i+1 ; ('x',j) k bits in one block
    segs = {}
    for i in range(m - 2): segs[('u', i)] = (n, {i, i + 1})
    for j in range(m):
        b = 0 if j <= 1 else j - 1
        segs[('x', j)] = (k, {b})
    return segs

def nvars_window(segs, blocks):
    return sum(sz for sz, bl in segs.values() if bl <= blocks)  # segment fully inside? no: variable inside window if its block set meets? 

def vars_in(segs, a, b):
    # variables whose whole block interval lies inside [a,b]  (a monomial lies in window [a,b]
    # iff every variable's interval meets... ) -- locality def: L = max lo - min hi + 1
    # a monomial has locality <= L iff exists window [a,a+L-1] with every variable having
    # some block in it, i.e. interval [lo,hi] meets [a,b].
    return sum(sz for sz, bl in segs.values() if max(bl) >= a and min(bl) <= b)

def cnt(N, D): return sum(comb(N, i) for i in range(D + 1))

def count_L(n, k, m, L, D=4):
    segs = block_vars(n, k, m); nb = m - 1
    if L >= nb: return cnt(sum(s for s, _ in segs.values()), D)
    tot = 0
    for a in range(nb - L + 1):
        tot += cnt(vars_in(segs, a, a + L - 1), D)
    for a in range(nb - L):
        tot -= cnt(vars_in(segs, a + 1, a + L - 1), D)   # intersection of windows a and a+1 = [a+1, a+L-1]
    return tot

def windows(n, k, m, L=2, D=4):
    segs = block_vars(n, k, m); nb = m - 1
    return [cnt(vars_in(segs, a, a + L - 1), D) for a in range(nb - L + 1)]

# validate vs pilot #3 exact counts
for (m, n, k, full, l1, l2) in [(3,9,3,4048,2479,4048),(3,11,4,10903,6415,10903),(4,7,2,9109,3137,7727),(4,9,3,31931,9770,26258),(4,11,3,52956,18837,45339),(5,9,3,124314,17061,65649)]:
    print(m,n,k, count_L(n,k,m,99)==full, count_L(n,k,m,1), l1, count_L(n,k,m,2), l2)
