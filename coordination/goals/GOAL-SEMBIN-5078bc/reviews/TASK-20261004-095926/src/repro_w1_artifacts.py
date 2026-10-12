#!/usr/bin/env python3
"""Standalone reproducers of the two W1 breaking artifacts.
ARTIFACT 1 (order flip, admissible orders): N=10, three generators given as lists of monomial bitmasks (bit j-1 <-> x_j).  Order-experiment trial 1449 of
   order_flip_search.py (python rng seed 2026); weights of 'wdeg' = random.Random(1450).random()+0.5 per variable; 'wdeg_rev' uses seed 1451 and the reversed sign.
   Under degrevlex and deglex the closure verdict is 'sufficient'; under both weighted graded orders it is 'insufficient'; W is the same 245-dimensional subspace
   and equals I_{<=4} in all four.
ARTIFACT 2 (non-admissible order): family sparsequad N=9 M=6 seed 0 of gen_systems.system, random per-monomial graded order make_key_random_graded(9, seed 3):
   N_std = 7 < |V| = 8 although every row of W lies in the ideal ('impossible' branch of the verdict rule)."""
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ref_closure import *
from order_experiment import key_weight
from gen_systems import system
from msparse import eval_B
N = 10
gens = [frozenset(g) for g in [[8, 769], [1, 530, 546], [58, 64, 160, 320, 323]]]
pts = points_of_system(N, gens); nV = len(pts)
print('ARTIFACT 1: N=%d |V|=%d' % (N, nV))
t = 1449
orders = {'degrevlex': key_degrevlex, 'deglex': make_key_deglex(N), 'wdeg': key_weight(N, t + 1, +1), 'wdeg_rev': key_weight(N, t + 2, -1)}
spans = []
for name, key in orders.items():
    C = Closure(gens, N, 4, key=key).run()
    ns = count_std(N, C.lm_set()); lmI, _ = eval_kernel_lm(N, 4, pts, key)
    print('  %-10s rank %d  N_std %d  verdict %-12s  LM(W)==LM(I<=4): %s' % (name, len(C.basis), ns, verdict(ns, nV), set(C.lm_set()) == lmI))
    spans.append(C)
# same subspace
S = Space(N, 4); rows = []
def span_of(C): return {S.from_poly(p) for p in C.polys()}
piv = {}
def add(x):
    while x:
        h = x.bit_length() - 1
        if h in piv: x ^= piv[h]
        else: piv[h] = x; return
for C in spans[:1]:
    for p in C.polys(): add(S.from_poly(p))
r0 = len(piv)
for C in spans[1:]:
    for p in C.polys(): add(S.from_poly(p))
print('  the four closures span the same subspace:', len(piv) == r0)
print('ARTIFACT 2:')
N2 = 9; M2 = 6
gens2 = system('sparsequad', N2, M2, 0); pts2 = points_of_system(N2, gens2)
C = Closure(gens2, N2, 4, key=make_key_random_graded(N2, 3)).run()
ns = count_std(N2, C.lm_set())
Cd = Closure(gens2, N2, 4).run(); nsd = count_std(N2, Cd.lm_set())
rowsvanish = all(eval_B(p, a) == 0 for p in C.polys() for a in pts2)
print('  |V| = %d ; random graded order: N_std = %d -> %s ; degrevlex: N_std = %d -> %s ; every row of W vanishes on V: %s' % (len(pts2), ns, verdict(ns, len(pts2)), nsd, verdict(nsd, len(pts2)), rowsvanish))
