#!/usr/bin/env python3
"""W1(4): for the systems of order_flip_search.json whose ideal-level 'GB degree <= 4' differs between orders, run the CLOSURE itself under
each order and compare the verdicts (N_std vs |V|)."""
import sys, os, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ref_closure import *
from order_experiment import key_weight
d = json.load(open(sys.argv[1])); out = []
nflip = 0
for f in d['flips']:
    N = f['N']; gens = [frozenset(g) for g in f['gens']]; t = f['trial']
    orders = {'degrevlex': key_degrevlex, 'deglex': make_key_deglex(N), 'wdeg': key_weight(N, t + 1, +1), 'wdeg_rev': key_weight(N, t + 2, -1)}
    pts = points_of_system(N, gens); nV = len(pts)
    res = {}
    for name, key in orders.items():
        C = Closure(gens, N, 4, key=key).run()
        ns = count_std(N, C.lm_set())
        lmI, stdI = eval_kernel_lm(N, 4, pts, key)
        res[name] = dict(rank=len(C.basis), N_std=ns, verdict=verdict(ns, nV), gb_degree=f['gb_degree_by_order'][name], W_equals_I_leq4=(set(C.lm_set()) == lmI))
    vs = {r['verdict'] for r in res.values()}
    if len(vs) > 1: nflip += 1
    out.append(dict(trial=t, N=N, V=nV, gens=f['gens'], results=res, closure_verdict_flips=len(vs) > 1))
print('systems with ideal-level GB-degree flip:', len(out), '| of those, closure-level verdict flips among the 4 admissible orders:', nflip)
for o in out:
    if o['closure_verdict_flips']: print(json.dumps(o)); break
json.dump(out, open(sys.argv[2], 'w'), indent=1)
