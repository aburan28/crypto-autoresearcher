#!/usr/bin/env python3
"""Expected numbers of log-GAP jobs with label duplicates, from the spec's half-box rule alone.

Model (stated, approximate): for uniform independent P_1..P_r in a group of prime order N, the relation
lattice {v in Z^r : sum v_i P_i = O} contains a given v != 0 (mod N) with probability 1/N. Two coefficient
vectors c, c' of the half-box give the same x-label iff c - c' or c + c' is a relation. A single relation v
(up to sign) in the full box B = [-T, T]^r produces about prod(2T+1-|v_i|)/2 duplicate labels among H.
A job is degenerate when the duplicates exceed the slack |H| - n; otherwise duplicates are skipped and the
job stays ok with duplicate_skips > 0. Multiple relations and the stop-at-n truncation are ignored
(first-order approximation; both only matter when relations are already present). Only primitive v are
enumerated: for N an odd prime, kv is a relation iff v is, so v and its multiples are one event, and the
chain count prod(2T+1-|v_i|) already includes the links through multiples of v.

Usage: python3 -I dup_expectation.py <repo_root>
"""
import itertools
import json
import math
import os
import sys
from collections import defaultdict

repo = sys.argv[1]
jobs = os.path.join(repo, "experiments/EXP-PFDR-bb0d26/runs/RUN-PFDR-4d8c71/toy-main-jobs.jsonl")
invN = defaultdict(float)
cnt = defaultdict(int)
obs = defaultdict(lambda: [0, 0])  # [ok jobs with dups>0, degenerate jobs]
for line in open(jobs):
    d = json.loads(line)
    invN[d["cell"]] += 1.0 / d["N"]
    cnt[d["cell"]] += 1
    if d["status"] != "ok":
        obs[d["cell"]][1] += 1
    elif d["gap_meta"]["duplicate_skips"] > 0:
        obs[d["cell"]][0] += 1

tot_small = tot_big = 0.0
print("cell            T   |H|  slack  E[ok-with-dups]  E[degenerate]  obs(ok-dups,degenerate)")
for cell in sorted(cnt, key=lambda s: (int(s.split('-')[0][1:]), int(s.split('-')[1][1:]), int(s.split('-')[2][1:]))):
    b, r, n = cell.split("-")
    r = int(r[1:]); n = int(n[1:])
    if r == 1:
        continue  # N prime > 2T: no relation of rank 1 inside the box
    need = math.ceil(1.02 * n) + 8
    T = 0
    while ((2 * T + 1) ** r - 1) // 2 < need:
        T += 1
    H = ((2 * T + 1) ** r - 1) // 2
    slack = H - n
    w = 2 * T + 1
    n_small = n_big = 0
    # v ranges over D = [-2T, 2T]^r minus 0, counted up to sign
    for v in itertools.product(range(-2 * T, 2 * T + 1), repeat=r):
        if v <= tuple([0] * r):
            continue  # keep one of +-v (lexicographically positive)
        if math.gcd(*v) != 1:
            continue  # kv in the lattice iff v is (N odd prime): count each event once, at its primitive vector
        prod = 1
        for x in v:
            prod *= max(0, w - abs(x))
        dups = prod / 2.0
        if dups <= 0:
            continue
        if dups > slack:
            n_big += 1
        else:
            n_small += 1
    e_small = n_small * invN[cell]
    e_big = n_big * invN[cell]
    tot_small += e_small; tot_big += e_big
    print(f"{cell:14s} {T:3d} {H:5d} {slack:5d}  {e_small:14.4f}  {e_big:13.4f}  {tuple(obs[cell])}")
print(f"TOTAL expected ok-with-dups {tot_small:.3f}, expected degenerate {tot_big:.3f}; "
      f"observed ok-with-dups {sum(o[0] for o in obs.values())}, degenerate {sum(o[1] for o in obs.values())}")
