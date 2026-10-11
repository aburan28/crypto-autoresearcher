#!/usr/bin/env python3
"""W1(4), closure-free: for random sparse systems, the exact LM(I) over ALL monomials (sizes 0..N) from the evaluation kernel under
degrevlex (the stated order), deglex and two weighted graded orders; the 'Groebner degree' = max size of a minimal element of LM(I).
A system with deg <= 4 under one order and > 4 under another is a system whose 'sufficient at D=4' status is order dependent at the
ideal level.  usage: order_flip_search.py TRIALS OUT.json"""
import sys, os, random, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ref_closure import *
from order_experiment import key_weight

def gb_degree(N, pts, key):
    mons = sorted(all_monomials(N, N), key=key)
    basis = {}; lm = set()
    for m in mons:
        v = eval_vec(m, pts)
        while v:
            h = v.bit_length() - 1
            if h in basis: v ^= basis[h]
            else: basis[h] = v; break
        if not v: lm.add(m)
    mins = [m for m in lm if not any(((m ^ (1 << j)) in lm) for j in range(N) if (m >> j) & 1)]
    return max((popcount(m) for m in mins), default=0), len(lm)

def main():
    trials = int(sys.argv[1]); out = sys.argv[2]
    rng = random.Random(2026)
    flips = []; tested = 0; hist = {}
    for t in range(trials):
        N = rng.choice([8, 9, 10, 11]); M = rng.randint(2, 5)
        gens = []
        for _ in range(M):
            p = set()
            for _ in range(rng.randint(2, 7)):
                d = rng.randint(1, 4); m = 0
                for jj in rng.sample(range(N), d): m |= 1 << jj
                p ^= {m}
            gens.append(frozenset(p))
        gens = [g for g in gens if g]
        if not gens: continue
        pts = points_of_system(N, gens)
        orders = {'degrevlex': key_degrevlex, 'deglex': make_key_deglex(N), 'wdeg': key_weight(N, t + 1, +1), 'wdeg_rev': key_weight(N, t + 2, -1)}
        degs = {}
        for name, key in orders.items():
            d, nl = gb_degree(N, pts, key); degs[name] = d
        tested += 1
        sig = tuple(sorted(set(degs.values())))
        hist[sig] = hist.get(sig, 0) + 1
        le = {d <= 4 for d in degs.values()}
        if len(le) > 1:
            flips.append(dict(trial=t, N=N, gens=[sorted(g) for g in gens], V=len(pts), gb_degree_by_order=degs))
    print('systems', tested, 'distinct-GB-degree signatures', {str(k): v for k, v in hist.items()})
    print('systems whose "GB degree <= 4" differs between orders:', len(flips))
    for f in flips[:5]: print(json.dumps(f))
    json.dump(dict(tested=tested, flips=flips, hist={str(k): v for k, v in hist.items()}), open(out, 'w'), indent=1)
main()
