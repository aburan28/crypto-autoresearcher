#!/usr/bin/env python3
"""J8 search for small separating systems (own seeds 2026092609/2026092610).
Planted unsatisfiable systems: neq-1 random quadratics, then one quadratic
equal to 1 on every common solution of the others. Classified by the literal
small engine. Writes found.json (the systems used by crafted_attempts.py)."""
import json
import random
import sys
import time
from itertools import combinations

import small_engine as se


def monos_q(n):
    return [0] + [1 << i for i in range(n)] + [(1 << i) | (1 << j) for i, j in combinations(range(n), 2)]


def planted(rng, n, neq, dens):
    M = monos_q(n)
    gs = [{m for m in M if rng.random() < dens} for _ in range(neq - 1)]
    S = se.solutions(gs, n)
    if not S:
        return None
    piv = {}
    for a in S:
        r = 0
        for c, m in enumerate(M):
            if m & a == m:
                r |= 1 << c
        b = 1
        while r:
            p = r.bit_length() - 1
            if p in piv:
                pr, pb = piv[p]
                r ^= pr
                b ^= pb
            else:
                piv[p] = (r, b)
                break
        else:
            if b:
                return None
    x = [rng.randrange(2) for _ in M]
    for p in sorted(piv):
        r, b = piv[p]
        s = b
        for c in range(len(M)):
            if c != p and (r >> c) & 1:
                s ^= x[c]
        x[p] = s
    f = {M[c] for c in range(len(M)) if x[c]}
    fs = gs + [f]
    assert not se.solutions(fs, n)
    return fs


def classify(fs, n):
    out = {}
    for D in (3, 4):
        R = se.Ring(n, D)
        E, _ = se.rowspace(R, fs, D)
        W = se.literal_W(R, fs, D)
        out[D] = {"M": E.contains(R.vec({0})), "W": W["one"], "first": W["one_first_iteration"], "dims": W["dims"]}
    R5 = se.Ring(n, 5)
    E5, _ = se.rowspace(R5, fs, 5)
    out[5] = {"M": E5.contains(R5.vec({0}))}
    return out


def main():
    outp = sys.argv[1]
    rng = random.Random(2026092610)
    found = {"X3": [], "Y4": [], "X4": []}
    stats = {}
    t = time.time()
    for n, neq in [(6, 3), (7, 3), (7, 4), (8, 3), (8, 4)]:
        for _ in range(300):
            fs = planted(rng, n, neq, rng.choice([0.3, 0.5]))
            if fs is None:
                continue
            c = classify(fs, n)
            key = (n, neq, c[3]["M"], c[3]["W"], c[4]["M"], c[4]["W"], c[5]["M"])
            stats[str(key)] = stats.get(str(key), 0) + 1
            rec = {"n": n, "neq": neq, "fs": [sorted(f) for f in fs], "class": c}
            if (not c[3]["W"]) and c[4]["M"] and len(found["X3"]) < 3:
                found["X3"].append(rec)
            if c[4]["W"] and not c[4]["M"] and len(found["Y4"]) < 3:
                found["Y4"].append(rec)
            if (not c[4]["W"]) and c[5]["M"] and len(found["X4"]) < 3:
                found["X4"].append(rec)
        print(n, neq, round(time.time() - t, 1), flush=True)
    json.dump({"stats (n, neq, 1inM3, 1inW3, 1inM4, 1inW4, 1inM5)": stats, "found": found}, open(outp, "w"), indent=1)
    print(stats)
    print({k: len(v) for k, v in found.items()})


if __name__ == "__main__":
    main()
