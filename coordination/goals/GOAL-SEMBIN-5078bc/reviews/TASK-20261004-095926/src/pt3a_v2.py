#!/usr/bin/env python3
"""PT-3(a), ground-truth-anchored.  KNOWN-SUFFICIENT controls: planted point a, generators = a random invertible recombination of the spanning set
{ m + m(a) : m monomial of size 1..2 } of I_{<=2} (all quadrics and linear forms vanishing at a).  Independent ground truth: |V| = 1 by brute force, and
the evaluation kernel gives LM(I_{<=2}) with N_std(LM(I_{<=2})) = 1.  A degree-2 closure must then return 'sufficient'.
Second table: the 30 random planted systems of pt3.json compared against G1 (LM(W_2) == LM(I_{<=2}) by the evaluation kernel) and G3."""
import sys, os, json, random, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ref_closure import *
from msparse import eval_B
rng = random.Random(1234)
rows = []
for N in [7, 8, 9, 10]:
    for t in range(8):
        a = rng.getrandbits(N)
        basis = []
        for s in (1, 2):
            for c in itertools.combinations(range(N), s):
                m = sum(1 << j for j in c)
                p = {m}
                if (m & a) == m: p ^= {0}
                basis.append(frozenset(p))
        # random recombination: sparse random sums, keep generating set size = len(basis)
        gens = []
        for i in range(len(basis)):
            p = set(basis[i])
            for j in rng.sample(range(len(basis)), 3):
                p ^= set(basis[j])
            gens.append(frozenset(p))
        assert all(eval_B(g, a) == 0 for g in gens)
        pts = points_of_system(N, gens)
        C = Closure(gens, N, 2).run()
        lmI, stdI = eval_kernel_lm(N, 2, pts)
        ns = count_std(N, C.lm_set())
        rows.append(dict(N=N, trial=t, V=len(pts), rank=len(C.basis), c=len(C.S.mons), N_std=ns, verdict=verdict(ns, len(pts)),
                         W_equals_I_leq2=(set(C.lm_set()) == lmI), N_std_of_ideal_LM=count_std(N, lmI)))
ok = sum(r['verdict'] == 'sufficient' for r in rows)
print('PT-3(a) known-sufficient controls:', len(rows), 'systems; rule returns sufficient on', ok, '; W_2 == I_{<=2}:', sum(r['W_equals_I_leq2'] for r in rows))
res = json.load(open('results/pt/pt3.json'))['PT-3a_planted_degree2_closure']
agree = 0; tab = {}
for r in res:
    N = r['N']; a = r['planted']
    a_rng = random.Random(100 + r['seed']); a_chk = a_rng.getrandbits(N); assert a_chk == a
    gens = []
    for _ in range(4 * N):
        p = set()
        for i in range(N):
            if a_rng.random() < .5: p ^= {1 << i}
        for i in range(N):
            for j in range(i + 1, N):
                if a_rng.random() < .3: p ^= {(1 << i) | (1 << j)}
        if eval_B(frozenset(p), a): p ^= {0}
        gens.append(frozenset(p))
    pts = points_of_system(N, gens)
    C = Closure(gens, N, 2).run(); lmI, stdI = eval_kernel_lm(N, 2, pts)
    ns = count_std(N, C.lm_set()); v = verdict(ns, len(pts))
    G1 = set(C.lm_set()) == lmI; G3 = count_std(N, lmI) == len(pts)
    truth = 'sufficient' if (G1 and G3) else 'insufficient'
    tab[(v, truth)] = tab.get((v, truth), 0) + 1
    agree += (v == truth)
print('PT-3(a) random planted degree-2 systems: rule vs ground truth (G1 and G3) :', {str(k): n for k, n in tab.items()}, 'agree', agree, 'of', len(res))
json.dump(dict(known_sufficient=rows, random_planted_vs_truth={str(k): n for k, n in tab.items()}), open('results/pt/pt3a_v2.json', 'w'), indent=1)
