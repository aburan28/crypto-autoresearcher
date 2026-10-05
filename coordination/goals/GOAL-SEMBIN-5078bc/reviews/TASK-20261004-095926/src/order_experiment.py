#!/usr/bin/env python3
"""W1(4): order dependence of the leading-monomial data and of the verdict.
For every small random system: closure W under (a) degrevlex (the stated order), (b) deglex, (c) graded + random generic
weights (an ADMISSIBLE order: graded, then weight sum, then degrevlex tie-break), (d) a random graded total order of the
monomials of each size (NOT multiplicative = not an admissible monomial order).  The subspace W is order independent
(its degree budget is the monomial size, not the order); LM(W), N_std and the verdict are not.
usage: order_experiment.py NMIN NMAX NSEEDS"""
import sys, os, random, json, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ref_closure import *
from gen_systems import system

def key_weight(N, seed, sign):
    rng = random.Random(seed); w = [rng.random() + 0.5 for _ in range(N)]
    def key(m):
        s = sum(w[j] for j in range(N) if (m >> j) & 1)
        return (popcount(m), sign * s, -m)
    return key

def span_equal(C1, C2, N):
    # both closures as sets of polys; compare spans by rank of union
    S1 = C1.polys(); S2 = C2.polys()
    S = Space(N, 4, key_degrevlex)
    rows = [S.from_poly(p) for p in S1]
    piv = {}
    def add(x):
        while x:
            h = x.bit_length() - 1
            if h in piv: x ^= piv[h]
            else: piv[h] = x; return True
        return False
    for r in rows: add(r)
    r1 = len(piv)
    for p in S2: add(S.from_poly(p))
    return len(piv) == r1 and len(S1) == len(S2) == r1

def main():
    nmin, nmax, nseeds = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    tot = 0; flips = 0; imposs = {'degrevlex': 0, 'deglex': 0, 'wdeg': 0, 'wdeg_rev': 0, 'randgraded': 0}
    flips_admissible = 0; rank_differs = 0; examples = []; nstd_differs_adm = 0; verdict_counts = {}
    for fam in ['quad', 'sparsequad', 'cubic', 'bilinear', 'planted']:
        for N in range(nmin, nmax + 1):
            for seed in range(nseeds):
                rng = random.Random(N * 1000 + seed * 7 + len(fam))
                M = max(2, N + rng.choice([-3, -2, -1, 0, 0, 1])) if fam != 'planted' else max(2, N - rng.choice([2, 3, 4, 5]))
                gens = system(fam, N, M, seed)
                if not gens: continue
                pts = points_of_system(N, gens); nV = len(pts)
                orders = {'degrevlex': key_degrevlex, 'deglex': make_key_deglex(N), 'wdeg': key_weight(N, seed + 1, +1),
                          'wdeg_rev': key_weight(N, seed + 2, -1), 'randgraded': make_key_random_graded(N, seed + 3)}
                res = {}; closures = {}
                for name, key in orders.items():
                    C = Closure(gens, N, 4, key=key).run(); closures[name] = C
                    lms = C.lm_set(); ns = count_std(N, lms)
                    res[name] = (len(C.basis), ns, verdict(ns, nV))
                    if ns < nV: imposs[name] += 1
                tot += 1
                ranks = {v[0] for v in res.values()}
                if len(ranks) > 1: rank_differs += 1
                if not all(span_equal(closures['degrevlex'], closures[n], N) for n in orders if n != 'degrevlex'):
                    print('SUBSPACE DIFFERS across orders', fam, N, M, seed)
                adm = {res[n][2] for n in ['degrevlex', 'deglex', 'wdeg', 'wdeg_rev']}
                if len({res[n][1] for n in ['degrevlex', 'deglex', 'wdeg', 'wdeg_rev']}) > 1: nstd_differs_adm += 1
                vc = verdict_counts.setdefault(res['degrevlex'][2], 0); verdict_counts[res['degrevlex'][2]] = vc + 1
                allv = {v[2] for v in res.values()}
                if len(adm) > 1: flips_admissible += 1
                if len(allv) > 1: flips += 1
                if (len(allv) > 1 or len({res[n][1] for n in ['degrevlex', 'deglex', 'wdeg', 'wdeg_rev']}) > 1) and len(examples) < 12:
                    examples.append(dict(family=fam, N=N, M=M, seed=seed, V=nV, results=res))
    print('degrevlex verdict counts', verdict_counts, '| systems where N_std differs among the 4 admissible orders:', nstd_differs_adm)
    print('systems', tot, '| rank differs across orders:', rank_differs, '| verdict flips among the 4 admissible orders:', flips_admissible,
          '| verdict differs among all 5 orders:', flips, '| N_std < |V| (impossible) per order:', imposs)
    for e in examples: print(json.dumps(e))

if __name__ == "__main__":
    main()
