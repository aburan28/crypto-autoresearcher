#!/usr/bin/env python3
"""W1(5): verify the identity   N_std = (c - r - K) + N_std^{>D}   on random closures, where
   c = # monomials of size <= D, r = rank = |LM(W)|, K = # non-LM monomials of size <= D that contain a PROPER LM member as a subset,
   N_std^{>D} = # standard monomials of size > D (all of whose subsets of size <= D are standard).
Also records: K = 0 for every closure under the stated (admissible) order (LM(W) is an up-set inside sizes <= D) -- tested, and the mutant
closures (missing products) where K can be > 0.  usage: identity_check.py NSYS"""
import sys, os, random, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ref_closure import *
from gen_systems import system
n = int(sys.argv[1]); rng = random.Random(4); bad = 0; K_pos = 0; tot = 0; Kpos_mut = 0; totm = 0
for t in range(n):
    fam = rng.choice(['quad', 'sparsequad', 'cubic', 'bilinear', 'planted']); N = rng.randint(8, 13)
    M = max(2, N + rng.choice([-3, -2, -1, 0])) if fam != 'planted' else max(2, N - 3)
    gens = system(fam, N, M, t)
    if not gens: continue
    for mut in [{}, dict(budget_shift=1), dict(gens_only=True), dict(drop_last_batch=True)]:
        C = Closure(gens, N, 4, **mut).run(); lms = set(C.lm_set()); r = len(lms); c = len(C.S.mons)
        K = 0
        for m in C.S.mons:
            if m in lms: continue
            bits = [j for j in range(N) if (m >> j) & 1]
            hit = False
            for k in range(len(bits)):          # proper subsets
                for sub in itertools.combinations(bits, k):
                    mm = sum(1 << j for j in sub)
                    if mm in lms: hit = True; break
                if hit: break
            K += hit
        nstd = count_std(N, list(lms))
        # standard monomials of size > D : faces of size > D
        nstd_le = nstd_gt = 0
        # recount by size via DFS faces
        lmset = lms
        def faces_by_size():
            from collections import defaultdict
            cnt = defaultdict(int)
            stack = [(0, -1, [])]
            if 0 in lmset: return cnt
            while stack:
                mask, last, el = stack.pop(); cnt[len(el)] += 1
                for v in range(last + 1, N):
                    vm = 1 << v; ok = True
                    for sz in range(0, min(len(el), 3) + 1):
                        for T in itertools.combinations(el, sz):
                            tm = vm
                            for e in T: tm |= 1 << e
                            if tm in lmset: ok = False; break
                        if not ok: break
                    if ok: stack.append((mask | vm, v, el + [v]))
            return cnt
        cnt = faces_by_size(); gt = sum(v for k, v in cnt.items() if k > 4)
        ident = (nstd == (c - r - K) + gt)
        tot += not mut; totm += bool(mut)
        if mut: Kpos_mut += (K > 0)
        else: K_pos += (K > 0)
        if not ident: bad += 1; print('IDENTITY FAILS', fam, N, M, t, mut)
print('closures (unmutated) tested', tot, 'mutant closures', totm, '| identity failures', bad, '| unmutated closures with K>0:', K_pos, '| mutant closures with K>0:', Kpos_mut)
