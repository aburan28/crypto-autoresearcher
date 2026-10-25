#!/usr/bin/env python3
"""Multiplicity check: 6 curves x 5 alternatives x 3 band weights = 90
interval decisions. Vectorised two-stage (cluster, then pairs) bootstrap of
the ratio of sums, as ecbench forms it, with B resamples; reports the 95%
interval and the Bonferroni (alpha = 0.05/90) interval and the label each
gives. Own RNG (numpy), so values differ from ecbench's in the 3rd digit.

Usage: python3 -I multiplicity.py <campaign_dir> <out_json>
"""
import json
import sys

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import rederive as rd  # noqa: E402

camp, outp = sys.argv[1], sys.argv[2]
B = 200000
K = 90
out = {}
rng = np.random.default_rng(90)
for s in rd.SESSIONS:
    R = rd.load(f"{camp}/sessions/{s}/records.jsonl")
    out[s] = {}
    for arm in rd.ALTS:
        cells = []
        for w in rd.WEIGHTS:
            byw, _, _ = rd.pairs_by_workload(R, "plan", arm, lambda r, w=w: rd.priced_s(r, w))
            A = np.array([[a for a, _ in v] for v in byw.values()])  # (8,3)
            Bm = np.array([[b for _, b in v] for v in byw.values()])
            nc, npair = A.shape
            ic = rng.integers(0, nc, size=(B, nc))
            ip = rng.integers(0, npair, size=(B, nc, npair))
            sa = A[ic[:, :, None], ip].sum(axis=(1, 2))
            sb = Bm[ic[:, :, None], ip].sum(axis=(1, 2))
            rat = sb / sa
            q = np.quantile(rat, [0.025, 0.975, 0.05 / K / 2, 1 - 0.05 / K / 2])
            cells.append({"w": w, "ratio": float(Bm.sum() / A.sum()),
                          "ci95": [float(q[0]), float(q[1])], "class95": rd.classify(q[:2]),
                          "ci_bonf90": [float(q[2]), float(q[3])], "class_bonf": rd.classify(q[2:])})
        out[s][arm] = {"cells": cells,
                       "label95": rd.protocol_label([c["class95"] for c in cells]),
                       "label_bonf": rd.protocol_label([c["class_bonf"] for c in cells])}
json.dump(out, open(outp, "w"), indent=1)
for s, d in out.items():
    for arm, v in d.items():
        print(s, f"{arm:15s}", v["label95"], "|", v["label_bonf"], "|",
              " ".join(f"w={c['w']}:{c['ratio']:.3f} bonf[{c['ci_bonf90'][0]:.3f},{c['ci_bonf90'][1]:.3f}]" for c in v["cells"]))
