"""Self-test of literal_w4.Lit on small random systems (nv = 6, 7; D = 3, 4):
(a) against a second, worklist-style least-fixpoint computation (one product at a time,
    membership-tested), which must reach the same space;
(b) soundness: every final basis element vanishes on every common Boolean zero;
(c) at least 3 systems with fixpoint index >= 2 (constructed by planting affine structure if needed).
Output: selftest_literal.json
"""
import json
import os
import random
import sys
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from literal_w4 import Lit  # noqa: E402


def rand_eqs(rng, nv, neq, density=0.5, planted=None):
    monos = [sum(1 << i for i in c) for d in range(3) for c in combinations(range(nv), d)]
    eqs = []
    for k in range(neq):
        f = [m for m in monos if rng.random() < density]
        eqs.append(f)
    return eqs


def worklist_closure(L, eqs):
    piv = L.span(L.macaulay_rows(eqs))

    def member(x):
        while x:
            l = x.bit_length() - 1
            p = piv.get(l)
            if p is None:
                return False, x
            x ^= p
        return True, 0

    changed = True
    while changed:
        changed = False
        for l, b in list(piv.items()):
            if l >= L.low:
                continue
            for j in range(L.nv):
                y = L.times_vj(b, j)
                ok, r = member(y)
                if not ok:
                    piv[r.bit_length() - 1] = r
                    changed = True
    return piv


def evaluate(L, x, assignment):
    s = 0
    for p in L.bits_of(x):
        m = L.mons[p]
        if m & assignment == m:
            s ^= 1
    return s


def eval_eq(f, a):
    s = 0
    for m in f:
        if m & a == m:
            s ^= 1
    return s


rng = random.Random(20260926)
out = {"cases": []}
deep = 0
for trial in range(60):
    nv = 6 if trial % 2 == 0 else 7
    D = 3 if trial % 3 == 0 else 4
    neq = rng.randint(3, 6)
    dens = rng.choice([0.15, 0.25, 0.5])
    eqs = rand_eqs(rng, nv, neq, dens)
    # plant affine richness on some trials: add products of a random linear form (deeper iterations)
    if trial % 4 == 1:
        lin = [1 << rng.randrange(nv), 1 << rng.randrange(nv)]
        eqs[0] = lin + [0]
    L = Lit(nv, D)
    mrec, rec, per_iter, piv = L.w_closure(eqs)
    piv2 = worklist_closure(L, eqs)
    same_dim = len(piv2) == rec["final_dim"]
    # same space: every element of one reduces to 0 in the other
    def reduces(pv, x):
        while x:
            l = x.bit_length() - 1
            p = pv.get(l)
            if p is None:
                return False
            x ^= p
        return True
    same_space = same_dim and all(reduces(piv, x) for x in piv2.values())
    zeros = [a for a in range(1 << nv) if all(eval_eq(f, a) == 0 for f in eqs)]
    sound = all(evaluate(L, x, a) == 0 for x in piv.values() for a in zeros)
    codim = L.C - rec["final_dim"]
    if rec["iterations_to_fixpoint"] >= 2:
        deep += 1
    out["cases"].append({"trial": trial, "nv": nv, "D": D, "neq": neq, "iters": rec["iterations_to_fixpoint"],
                         "dims": rec["dims"], "one": rec["one"], "s": len(zeros), "codim": codim,
                         "same_space_as_worklist": same_space, "sound": sound, "codim_ge_s": codim >= len(zeros)})
out["n"] = len(out["cases"])
out["fixpoint_index_ge_2"] = deep
out["all_same_space"] = all(c["same_space_as_worklist"] for c in out["cases"])
out["all_sound"] = all(c["sound"] and c["codim_ge_s"] for c in out["cases"])
out["refuted_cases"] = sum(1 for c in out["cases"] if c["one"])
with open(os.path.join(HERE, "selftest_literal.json"), "w") as fh:
    json.dump(out, fh, indent=1)
print({k: v for k, v in out.items() if k != "cases"})
print(sorted(set((c["iters"], c["one"]) for c in out["cases"])))
