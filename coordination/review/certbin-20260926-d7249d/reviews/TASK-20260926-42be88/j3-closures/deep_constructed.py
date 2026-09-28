"""J3 (2) support: the engine's semi-naive _w_closure against the validator's literal W_4 at nv = 20,
neq = 19, D = 4 on CONSTRUCTED systems chosen to reach fixpoint index >= 2 (no archived system does).
These are verification constructions, not archived systems and not trials.
Generator: random.Random(20260926 + 42) (own seed, recorded); sparse quadratic equations, a share of
them planted with linear-factor structure l1 * l2 + l3 so that falls cascade over several iterations.
usage: python3 deep_constructed.py <snapshot_root>
"""
import json
import os
import random
import sys
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from literal_w4 import Lit  # noqa: E402

ROOT = sys.argv[1]
sys.path.insert(0, os.path.join(ROOT, "src"))
from crypto_autoresearcher.gf2 import closure as gclosure  # noqa: E402
from crypto_autoresearcher.gf2 import kernels  # noqa: E402

rng = random.Random(20260926 + 42)
NV, NEQ = 20, 19


def linform(k):
    vs = rng.sample(range(NV), k)
    return [1 << v for v in vs] + ([0] if rng.random() < 0.5 else [])


def mul(p, q):
    acc = {}
    for a in p:
        for b in q:
            y = a | b
            acc[y] = acc.get(y, 0) ^ 1
    return [m for m, c in acc.items() if c]


def add(p, q):
    acc = {}
    for a in p + q:
        acc[a] = acc.get(a, 0) ^ 1
    return [m for m, c in acc.items() if c]


def make(style):
    eqs = []
    for k in range(NEQ):
        if style == "planted" and rng.random() < 0.7:
            f = add(mul(linform(rng.randint(1, 3)), linform(rng.randint(1, 3))), linform(rng.randint(0, 2)))
        else:
            monos = [sum(1 << i for i in c) for d in range(3) for c in combinations(range(NV), d)]
            f = rng.sample(monos, rng.randint(2, 6))
        eqs.append(sorted(set(f)))
    return eqs


cl = gclosure.Closure(NV, 4, NEQ)
L = Lit(NV, 4)
F = ("dims", "iterations_to_fixpoint", "one", "one_first_iteration", "final_dim", "dims_by_deg")
cases = []
for t in range(24):
    style = "planted" if t % 2 == 0 else "sparse"
    eqs = make(style)
    erec, _ = cl.w_closure(eqs, want_cert=False)
    _, lrec, per_iter, _ = L.w_closure(eqs)
    diff = [f for f in F if erec[f] != lrec[f]]
    cases.append({"t": t, "style": style, "engine": {f: erec[f] for f in F}, "literal": {f: lrec[f] for f in F},
                  "engine_new_fallen_per_iteration": erec["new_fallen_per_iteration"],
                  "engine_stack_rows_per_iteration": erec["stack_rows_per_iteration"],
                  "literal_stack_rows_per_iteration": [p["stack_rows"] for p in per_iter],
                  "differences": diff})
    print(t, style, erec["dims"], erec["one_first_iteration"], "diff", diff, flush=True)
res = {"backend": kernels.backend(), "cases": cases, "n": len(cases),
       "fixpoint_index_ge_2": sum(1 for c in cases if c["engine"]["iterations_to_fixpoint"] >= 2),
       "fixpoint_index_ge_3": sum(1 for c in cases if c["engine"]["iterations_to_fixpoint"] >= 3),
       "refuted_at_iteration_ge_2": sum(1 for c in cases if (c["engine"]["one_first_iteration"] or 0) >= 2),
       "all_equal": all(not c["differences"] for c in cases)}
json.dump(res, open(os.path.join(HERE, "deep-constructed.json"), "w"), indent=1)
print({k: v for k, v in res.items() if k != "cases"})
