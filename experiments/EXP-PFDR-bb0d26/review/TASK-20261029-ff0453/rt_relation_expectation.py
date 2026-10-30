#!/usr/bin/env python3
"""Expected number of curves whose seeded base points P_1..P_r carry a short integer relation that the
frozen half-box would expose as a duplicate label, against the recorded duplicate_skips.

For uniform P_i = k_i G in a group of prime order N and a fixed nonzero v, Pr[v.k = 0 mod N] = 1/N.
Two half-box vectors c, c' give the same label iff (c - c').k = 0 or (c + c').k = 0 mod N.  With H_n the
first n half-box vectors in the frozen lexicographic order, the first-order expected number of exposed
relations on a curve of order N is |D_n| / (2N), D_n = ((H_n - H_n) u (H_n + H_n)) minus {0}, counted up to
sign.  Uses only the frozen half-box rule and the recorded N of each ok job.  No point is generated.
"""
from __future__ import annotations

import itertools
import json
import math
import os
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
JOBS = os.path.join(ROOT, "experiments", "EXP-PFDR-bb0d26", "runs", "RUN-PFDR-4d8c71", "toy-main-jobs.jsonl")


def labels_needed(n):
    return -(-(102 * n) // 100) + 8


def half_box_T(r, n):
    T = 1
    while ((2 * T + 1) ** r - 1) // 2 < labels_needed(n):
        T += 1
    return T


def half_box(r, T):
    for v in itertools.product(range(-T, T + 1), repeat=r):
        for e in v:
            if e != 0:
                if e > 0:
                    yield v
                break


def D_size(r, n):
    T = half_box_T(r, n)
    H = np.array(list(itertools.islice(half_box(r, T), n)), dtype=np.int64)
    base = 4 * T + 1
    enc = lambda A: np.ravel_multi_index(tuple((A + 2 * T).T), (base,) * r)
    s = set()
    for sign in (1, -1):
        for i in range(0, len(H), 512):
            blk = H[i:i + 512]
            V = (blk[:, None, :] - sign * H[None, :, :]).reshape(-1, r)
            s.update(np.unique(enc(V)).tolist())
    zero = int(np.ravel_multi_index((2 * T,) * r, (base,) * r))
    s.discard(zero)
    return T, len(s) // 2 + (len(s) % 2)  # up to sign (D is symmetric, so len(s) is even)


recs = [json.loads(l) for l in open(JOBS)]
cells = defaultdict(list)
for r in recs:
    cells[(r["cell"], r["r"], r["n"], r["bits"])].append(r)

rows, tot_out, tot_in = [], 0.0, 0.0
for (cid, r, n, bits), rs in sorted(cells.items(), key=lambda t: (t[0][3], t[0][1], t[0][2])):
    if r == 1:
        continue
    T, D = D_size(r, n)
    lam = sum(D / x["N"] for x in rs)
    obs = sum(1 for x in rs if (x["gap_meta"] or {}).get("duplicate_skips", 0) > 0)
    rows.append({"cell": cid, "T": T, "D_up_to_sign": D, "curves": len(rs),
                 "expected_curves_with_exposed_relation": round(lam, 4), "observed_curves_with_duplicates": obs})
    if cid == "b20-r3-n4096":
        tot_in += lam
    else:
        tot_out += lam
obs_out = sum(rw["observed_curves_with_duplicates"] for rw in rows if rw["cell"] != "b20-r3-n4096")
obs_in = sum(rw["observed_curves_with_duplicates"] for rw in rows if rw["cell"] == "b20-r3-n4096")
pois_cdf0 = math.exp(-tot_out)
pois_ge = 1 - sum(math.exp(-tot_in) * tot_in ** k / math.factorial(k) for k in range(obs_in))
out = {"rows": rows,
       "expected_outside_invalid_cell": round(tot_out, 3), "observed_outside_invalid_cell": obs_out,
       "P_zero_outside_given_poisson": round(pois_cdf0, 4),
       "expected_in_invalid_cell": round(tot_in, 3), "observed_in_invalid_cell": obs_in,
       "P_ge_observed_in_invalid_cell": round(pois_ge, 4)}
json.dump(out, open(os.path.join(HERE, "rt_relation_expectation.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
for rw in rows:
    print(rw)
