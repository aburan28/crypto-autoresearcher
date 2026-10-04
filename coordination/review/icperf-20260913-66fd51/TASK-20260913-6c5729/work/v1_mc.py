"""Independent check of v1_density.py: draw uniform random targets per cell and
decide satisfiability by the SAME exhaustive f3 scan that certified the 60
shipped instances.  This measures the decomposable fraction without using the
F1/F2/V construction at all, so the two routes cross-check each other."""
from __future__ import annotations

import json
import os
import random

from valgf import GF2n, BinaryCurve, parse_info
from v1_exhaust import LogField, f3_fast

BENCH = "/workspace/inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks"
OUT = os.path.dirname(os.path.abspath(__file__))
SEED = 20260915
N_SAMPLES = 300


def has_root(L, xr, l):
    xr2 = L.mul(xr, xr)
    xr3 = L.mul(xr2, xr)
    xr4 = L.mul(xr2, xr2)
    pw = (xr, xr2, xr3, xr4)
    V = 1 << l
    for a in range(V):
        for b in range(a, V):
            for c in range(b, V):
                if f3_fast(L, pw, a, b, c) == 0:
                    return True
    return False


def main():
    import v1_density
    out = {"seed": SEED, "n_samples_per_cell": N_SAMPLES, "cells": {}}
    for n, l in ((15, 5), (17, 6), (19, 6)):
        info = parse_info(os.path.join(BENCH, f"INFOn{n}l{l}-1-S.dimacs"))
        F = GF2n(n, info["modulus_bits"])
        L = LogField(F)
        E = BinaryCurve(F, 1, 1)
        TW = BinaryCurve(F, 0, 1)
        D = (v1_density.sums_over_subspace(E, l)
             | v1_density.sums_over_subspace(TW, l)
             | set(range(1 << l)))
        rng = random.Random(SEED + n)
        hits = 0
        agree = 0
        disagree = []
        for _ in range(N_SAMPLES):
            xr = rng.randrange(1 << n)
            sat = has_root(L, xr, l)
            hits += sat
            inD = xr in D
            if sat == inD:
                agree += 1
            else:
                disagree.append({"xr": hex(xr), "exhaustive_sat": sat, "in_D_lower": inD})
        out["cells"][f"n{n}l{l}"] = {
            "monte_carlo_decomposable": hits,
            "monte_carlo_fraction": hits / N_SAMPLES,
            "D_lower_fraction": len(D) / (1 << n),
            "agreement_with_D_lower": agree,
            "disagreements": disagree[:20],
            "n_disagreements": len(disagree),
        }
        print(f"n{n}l{l}: exhaustive-scan decomposable {hits}/{N_SAMPLES} "
              f"= {hits/N_SAMPLES:.4f}; D_lower fraction {len(D)/(1<<n):.4f}; "
              f"agreement {agree}/{N_SAMPLES} (disagreements {len(disagree)})", flush=True)
    with open(os.path.join(OUT, "v1_mc.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
