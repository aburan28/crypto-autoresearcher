#!/usr/bin/env python3
"""Audit replay of the log-GAP builder GEOMETRY (labels, duplicate and infinity skips) for recorded jobs.

What it does, on recorded seeds only (no new curve, set or count):
  * the 4 degenerate jobs of b20-r3-n4096: regenerate the curve (vendored generator, seed 8,100,000 + c) and the
    three base points (seeded stream sha256("EXP-PFDR-bb0d26|gap|main|<cell>|<c>"), as the specification's
    log_gap_builder states), scan the frozen half-box, reproduce gap_meta, and name every integer relation
    v with v.(P_1, P_2, P_3) = O exposed by a duplicate label, verified by scalar multiplication;
  * every ok job at bits 20 with r in {2, 3}: reproduce enumerated / duplicate_skips / infinity_skips / first / last.
No discrete logarithm is computed and no pair-sum count is made (that is J3).  Reviewer-written scan; the
vendored curve.py supplies only the curve generator and the group law.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
EXPD = os.path.join(ROOT, "experiments", "EXP-PFDR-bb0d26")
sys.path.insert(0, os.path.join(EXPD, "implementation", "vendor"))
import curve as ec  # noqa: E402  vendored generator and group law only

JOBS = os.path.join(EXPD, "runs", "RUN-PFDR-4d8c71", "toy-main-jobs.jsonl")
EXP = "EXP-PFDR-bb0d26"


def rng_of(*labels):
    d = hashlib.sha256("|".join(map(str, (EXP,) + labels)).encode()).digest()
    return random.Random(int.from_bytes(d, "big"))


def labels_needed(n):
    return -(-(102 * n) // 100) + 8


def half_box_T(r, n):
    T = 1
    while ((2 * T + 1) ** r - 1) // 2 < labels_needed(n):
        T += 1
    return T


def half_box(r, T):
    for v in itertools.product(range(-T, T + 1), repeat=r):
        nz = next((e for e in v if e != 0), 0)
        if nz > 0:
            yield v


def scan(E, pts, r, n):
    T = half_box_T(r, n)
    tabs = []
    for P in pts:
        tab = {0: None, 1: P}
        for k in range(2, T + 1):
            tab[k] = E.add(tab[k - 1], P)
        for k in range(1, T + 1):
            tab[-k] = E.neg(tab[k])
        tabs.append(tab)
    seen = {}
    got = enum = dup = inf = 0
    first = last = None
    rels = set()
    for v in half_box(r, T):
        enum += 1
        Q = None
        for tab, ci in zip(tabs, v):
            Q = E.add(Q, tab[ci])
        if Q is None:
            inf += 1
            rels.add(tuple(v))
            continue
        x = Q[0]
        if x in seen:
            dup += 1
            w, Qw = seen[x]
            rel = tuple(a - b for a, b in zip(v, w)) if Qw == Q else tuple(a + b for a, b in zip(v, w))
            if next(e for e in rel if e != 0) < 0:
                rel = tuple(-e for e in rel)
            rels.add(rel)
            continue
        seen[x] = (v, Q)
        got += 1
        if first is None:
            first = list(v)
        last = list(v)
        if got == n:
            break
    return {"T": T, "enumerated": enum, "duplicate_skips": dup, "infinity_skips": inf,
            "first": first, "last": last, "labels": got}, rels


def lincomb(E, v, pts):
    Q = None
    for c, P in zip(v, pts):
        Q = E.add(Q, E.mul(c, P))
    return Q


recs = [json.loads(l) for l in open(JOBS)]
out = {"interpreter": sys.version, "degenerate": [], "ok_replay_b20_r23": {}}
for rec in recs:
    run_it = rec["status"] == "degenerate" or (rec["bits"] == 20 and rec["r"] in (2, 3))
    if not run_it:
        continue
    E, _ = ec.generate_prime_order_curve(rec["bits"], seed=8_100_000 + rec["c"])
    assert (E.p, E.a, E.b, E.order) == (rec["p"], rec["a"], rec["b_coef"], rec["N"]), rec["cell"]
    rng = rng_of("gap", rec["block"], rec["cell"], rec["c"])
    pts = [E.random_point(rng) for _ in range(rec["r"])]
    meta, rels = scan(E, pts, rec["r"], rec["n"])
    recorded = {k: rec["gap_meta"][k] for k in ("T", "enumerated", "duplicate_skips", "infinity_skips", "first", "last")}
    mine = {k: meta[k] for k in recorded}
    match = mine == recorded
    if rec["status"] == "degenerate":
        # reduce the exposed relations to a basis of short ones and verify each by scalar multiplication
        rl = sorted(rels, key=lambda v: (max(map(abs, v)), sum(map(abs, v))))
        verified = [{"v": list(v), "sup_norm": max(map(abs, v)), "vP_is_O": lincomb(E, v, pts) is None} for v in rl[:6]]
        out["degenerate"].append({"cell": rec["cell"], "c": rec["c"], "N": rec["N"], "gap_meta_reproduced": match,
                                  "labels_collected": meta["labels"], "needed": rec["n"],
                                  "distinct_relation_vectors_exposed": len(rels),
                                  "shortest_relations": verified})
    else:
        d = out["ok_replay_b20_r23"].setdefault(rec["cell"], {"jobs": 0, "gap_meta_reproduced": 0, "duplicates": 0, "mismatch": []})
        d["jobs"] += 1
        d["gap_meta_reproduced"] += int(match)
        d["duplicates"] += meta["duplicate_skips"]
        if not match:
            d["mismatch"].append({"c": rec["c"], "mine": mine, "recorded": recorded})
json.dump(out, open(os.path.join(HERE, "rt_degenerate_replay.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
