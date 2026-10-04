"""Literal set-based transcription of the regime-A (GF(2)) solver, copied from
EXP-CERTBIN-4e92d7/impl/selftest.py (literal_elimination)."""
import numpy as np


def literal_elimination_gf2(Md):
    rows = [set(np.flatnonzero(r).tolist()) for r in Md]
    used = set()
    ops = []
    for c in range(Md.shape[1]):
        cand = [i for i in range(len(rows)) if i not in used and c in rows[i]]
        if not cand:
            continue
        p = cand[0]
        X = cand[1:]
        for x in X:
            rows[x] ^= rows[p]
        used.add(p)
        ops.append((p, c, X))
    return ops
