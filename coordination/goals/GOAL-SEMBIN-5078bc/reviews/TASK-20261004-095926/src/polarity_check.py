#!/usr/bin/env python3
"""W1(3): numerical test of  N_std(W') >= N_std(W) >= |V|  for W' inside W inside I, over random systems and four missing-product mutants (W' = mutant closure),
under the stated order.  usage: polarity_check.py NSYS"""
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ref_closure import *
from gen_systems import system
n = int(sys.argv[1]); rng = random.Random(55); viol = 0; tot = 0; strict = 0; ge = 0
for t in range(n):
    fam = rng.choice(['quad', 'sparsequad', 'cubic', 'bilinear', 'planted', 'toeplitz']); N = rng.randint(8, 14)
    M = max(2, N + rng.choice([-3, -2, -1, 0])) if fam != 'planted' else max(2, N - 3)
    gens = system(fam, N, M, t)
    if not gens: continue
    nV = len(points_of_system(N, gens))
    U = Closure(gens, N, 4).run(); nu = count_std(N, U.lm_set())
    for mut in [dict(budget_shift=1), dict(gens_only=True), dict(drop_last_chunk=16), dict(drop_last_batch=True), dict(only_new_lm=True)]:
        Cm = Closure(gens, N, 4, **mut).run(); nm = count_std(N, Cm.lm_set()); tot += 1
        if not (nm >= nu >= nV): viol += 1; print('POLARITY VIOLATION', fam, N, M, t, mut, nm, nu, nV)
        strict += (nm > nu); ge += (nm == nu)
print('mutant closures tested', tot, '| violations of N_std(W\') >= N_std(W) >= |V|:', viol, '| strictly larger:', strict, '| equal:', ge)
