#!/usr/bin/env python3
"""W1(4) on the twelve window systems: for an instance with rank(W) = c - eval_rank (W = I_{<=4}, a subspace that does not depend on the graded
order), the leading-monomial set under ANY graded order is LM_order(I_{<=4}), computed closure-free from the enumerated zero set V.
Reports N_std and the verdict under degrevlex (stated), deglex and several random weighted graded orders (admissible).
usage: window_order_check.py SYSTEM.ms CLOSURE.json SOLUTIONS.txt [nweights]"""
import sys, os, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from msparse import *
from ref_closure import *
from order_experiment import key_weight

ms, cj, solf = sys.argv[1:4]
nw = int(sys.argv[4]) if len(sys.argv) > 4 else 4
N, B, R, info = parse_ms(ms)
j = json.load(open(cj)); pts = [int(x) for x in open(solf).read().split()]
c = j['columns']
out = dict(instance=os.path.basename(ms), N=N, V=len(pts), rank=j['rank'], columns=c)
orders = {'degrevlex(stated)': key_degrevlex, 'deglex': make_key_deglex(N)}
for t in range(nw): orders['wdeg_seed%d' % t] = key_weight(N, 100 + t, +1)
res = {}
for name, key in orders.items():
    lmI, stdI = eval_kernel_lm(N, 4, pts, key)
    W_is_I = (j['rank'] == c - len(stdI))
    ns = count_std(N, lmI) if W_is_I else None
    res[name] = dict(eval_rank=len(stdI), W_equals_I_leq4_dimension=W_is_I, N_std_if_W_equals_I=ns,
                     verdict=(verdict(ns, len(pts)) if ns is not None else None))
out['orders'] = res
out['verdicts_all_orders_equal'] = len({r['verdict'] for r in res.values()}) == 1
print(json.dumps(out))
