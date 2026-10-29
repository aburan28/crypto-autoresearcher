#!/usr/bin/env python3
"""E[C] for a uniform n-subset of a fixed label universe L (TASK-20261029-e5fe6b, joint J4, part i).

Derivation (see the YAML report): two distinct unordered pairs with the same sum are disjoint, so C(X)
counts 4-subsets of X together with one of their 3 pair-splittings having equal pair sums. By linearity,
for X a uniform n-subset of L (|L| = l):

    E[C(X)] = C(L) * (n)_4 / (l)_4          (exact, for every L)

with C(L) = sum_s binom(m_s(L), 2). For L = F_p (p odd), m_s = (p-1)/2 for every s, so
C(F_p) = p (p-1)(p-3)/8 and E[C] = (n)_4 / (8 (p-2)) = 3 binom(n,4)/(p-2) exactly. For L the label universe
of a curve (density ~1/2) the random-set approximation C(L) ~ (l)_4 / (8p) gives E[C] ~ 3 binom(n,4)/p.

This script (1) verifies the exact identity by exhaustive enumeration on small sets, (2) verifies the
F_p closed form, (3) computes C(L) exactly (FFT autocorrelation of the indicator of L) for every recorded
curve of the 20- and 24-bit curve sets, checks |L| = (N-1)/2, and compares the exact E[C] with
3 binom(n,4)/p and with the measured null means of the job records.

Usage: python3 -I ec_check.py <repo_root> <out_json> [--bits 20,24]
"""
import argparse
import itertools
import json
import math
import os
import sys
import time
from collections import defaultdict
from fractions import Fraction

import numpy as np


def ff4(x):
    return x * (x - 1) * (x - 2) * (x - 3)


def C_brute(X, p):
    m = defaultdict(int)
    X = list(X)
    for i in range(len(X)):
        for j in range(i + 1, len(X)):
            m[(X[i] + X[j]) % p] += 1
    return sum(v * (v - 1) // 2 for v in m.values())


def label_universe_small(p, a, b):
    sq = {(y * y) % p for y in range(1, p)}
    return [x for x in range(p) if ((x ** 3 + a * x + b) % p) in sq]


def exhaustive_checks():
    out = []
    # (1) exact identity on small label universes, all n-subsets enumerated
    for (p, a, b, ns) in [(43, 2, 3, (4, 5, 6)), (61, 5, 7, (4, 5)), (31, 1, 1, (4, 5, 6, 7))]:
        L = label_universe_small(p, a, b)
        l = len(L)
        CL = C_brute(L, p)
        for n in ns:
            tot = 0
            cnt = 0
            for X in itertools.combinations(L, n):
                tot += C_brute(X, p)
                cnt += 1
            mean = Fraction(tot, cnt)
            pred = Fraction(CL * ff4(n), ff4(l))
            out.append({"check": "E[C] = C(L)(n)_4/(l)_4 exhaustive", "p": p, "l": l, "n": n, "subsets": cnt,
                        "mean": str(mean), "predicted": str(pred), "equal": mean == pred})
    # (2) L = F_p closed form
    for p in (11, 13, 17, 23):
        L = list(range(p))
        CL = C_brute(L, p)
        out.append({"check": "C(F_p) = p(p-1)(p-3)/8", "p": p, "C": CL, "closed": p * (p - 1) * (p - 3) // 8,
                    "equal": CL * 8 == p * (p - 1) * (p - 3)})
        n = 5
        tot = cnt = 0
        for X in itertools.combinations(L, n):
            tot += C_brute(X, p); cnt += 1
        out.append({"check": "E[C] over F_p = (n)_4/(8(p-2))", "p": p, "n": n, "mean": str(Fraction(tot, cnt)),
                    "closed": str(Fraction(ff4(n), 8 * (p - 2))), "equal": Fraction(tot, cnt) == Fraction(ff4(n), 8 * (p - 2))})
    return out


def exact_CL(p, a, b):
    """C(L) and |L| for L = {x in F_p : x^3 + a x + b a nonzero square}, exact."""
    y = np.arange(1, (p + 1) // 2, dtype=np.int64)
    is_sq = np.zeros(p, dtype=bool)
    is_sq[(y * y) % p] = True
    x = np.arange(p, dtype=np.int64)
    f = ((x * x % p) * x % p + (a % p) * x + b) % p
    inL = is_sq[f]  # f = 0 is never marked (is_sq[0] False)
    del f, x, y, is_sq
    l = int(inL.sum())
    size = 1 << int(math.ceil(math.log2(2 * p)))
    A = np.fft.rfft(inL.astype(np.float64), size)
    conv = np.fft.irfft(A * A, size)
    del A
    rr = conv[:p].copy()
    rr[: p - 1] += conv[p: 2 * p - 1]
    del conv
    r = np.rint(rr)
    maxerr = float(np.max(np.abs(rr - r)))
    r = r.astype(np.int64)
    del rr
    h = np.zeros(p, dtype=np.int64)
    u = np.arange(p, dtype=np.int64)
    h[(2 * u) % p] = inL.astype(np.int64)  # the u = v = s/2 term of the ordered count r(s)
    diff = r - h
    if np.any(diff % 2):
        raise RuntimeError("parity failure in m_s")
    m = diff // 2
    C = 0
    S1 = 0
    chunk = 1 << 18
    for i in range(0, p, chunk):
        mm = m[i: i + chunk]
        C += int(np.sum(mm * (mm - 1) // 2))
        S1 += int(np.sum(mm))
    assert S1 == l * (l - 1) // 2, "sum of m_s must be binom(l, 2)"
    return C, l, maxerr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("out")
    ap.add_argument("--bits", default="20,24")
    args = ap.parse_args()
    bits_sel = {int(b) for b in args.bits.split(",")}
    t0 = time.time()
    ex = exhaustive_checks()
    print("exhaustive checks all equal:", all(e["equal"] for e in ex), f"({time.time() - t0:.1f}s)")

    jobs = os.path.join(args.repo, "experiments/EXP-PFDR-bb0d26/runs/RUN-PFDR-4d8c71/toy-main-jobs.jsonl")
    curves = {}
    cell_recs = defaultdict(list)
    for line in open(jobs):
        d = json.loads(line)
        if d["status"] != "ok":
            continue
        key = (d["bits"], d["c"])
        curves[key] = (d["p"], d["a"], d["b_coef"], d["N"])
        cell_recs[d["cell"]].append(d)

    per_curve = {}
    for key in sorted(curves):
        if key[0] not in bits_sel:
            continue
        p, a, b, N = curves[key]
        C, l, maxerr = exact_CL(p, a, b)
        per_curve[key] = {"p": p, "N": N, "l": l, "l_eq_(N-1)/2": l * 2 == N - 1, "C_L": C, "fft_maxerr": maxerr}
    print(f"exact C(L) for {len(per_curve)} curves ({time.time() - t0:.1f}s);",
          "all |L| == (N-1)/2:", all(v["l_eq_(N-1)/2"] for v in per_curve.values()),
          "max fft rounding err:", max(v["fft_maxerr"] for v in per_curve.values()))

    cells = []
    for cell, R in sorted(cell_recs.items()):
        bits = R[0]["bits"]; n = R[0]["n"]
        if bits not in bits_sel:
            continue
        Eex = Fraction(0); F = Fraction(0); F2 = Fraction(0); M = Fraction(0); V = Fraction(0)
        ratios_exact_over_formula = []
        for d in R:
            pc = per_curve[(bits, d["c"])]
            e = Fraction(pc["C_L"] * ff4(n), ff4(pc["l"]))
            fo = Fraction(3 * math.comb(n, 4), d["p"])
            Eex += e; F += fo; F2 += Fraction(3 * math.comb(n, 4), d["p"] - 2)
            ratios_exact_over_formula.append(float(e / fo))
            xs = d["null_C"]
            M += Fraction(sum(xs), len(xs))
            mu = Fraction(sum(xs), len(xs))
            V += sum((Fraction(x) - mu) ** 2 for x in xs) / (len(xs) - 1)
        z_mean = float((M - Eex)) / math.sqrt(float(V) / 20)   # sd of M = sqrt(sum var_c / 20)
        cells.append({"cell": cell, "curves": len(R), "M": float(M), "sum_E_exact": float(Eex), "sum_formula": float(F),
                      "M_over_E_exact": float(M / Eex), "M_over_formula": float(M / F),
                      "E_exact_over_formula": float(Eex / F),
                      "per_curve_E_exact_over_formula_min": min(ratios_exact_over_formula),
                      "per_curve_E_exact_over_formula_max": max(ratios_exact_over_formula),
                      "z_M_vs_E_exact": z_mean})
    zs = [c["z_M_vs_E_exact"] for c in cells]
    summ = {"cells": len(cells), "mean_z": float(np.mean(zs)) if zs else None,
            "sd_z_pop": float(np.std(zs)) if zs else None, "max_abs_z": max(map(abs, zs)) if zs else None}
    print(json.dumps(summ))
    curves_out = {f"b{k[0]}-c{k[1]}": {kk: vv for kk, vv in v.items() if kk in ("p", "l", "C_L", "l_eq_(N-1)/2")}
                  for k, v in per_curve.items()}
    rel = [ (v["C_L"] * 8 * v["p"]) / ff4(v["l"]) for v in per_curve.values()]
    res = {"python": sys.version.split()[0], "numpy": np.__version__, "exhaustive": ex,
           "per_curve_count": len(per_curve),
           "all_l_eq_(N-1)/2": all(v["l_eq_(N-1)/2"] for v in per_curve.values()),
           "C_L_over_randomset_(l)_4/(8p)": {"min": min(rel), "max": max(rel), "mean": float(np.mean(rel))},
           "cells": cells, "summary_z_M_vs_E_exact": summ, "seconds": round(time.time() - t0, 1)}
    with open(args.out, "w") as fh:
        json.dump(res, fh, separators=(",", ":"))
        fh.write("\n")
    with open(args.out.replace(".json", "-curves.json"), "w") as fh:
        json.dump(curves_out, fh, separators=(",", ":"))
        fh.write("\n")


if __name__ == "__main__":
    main()
