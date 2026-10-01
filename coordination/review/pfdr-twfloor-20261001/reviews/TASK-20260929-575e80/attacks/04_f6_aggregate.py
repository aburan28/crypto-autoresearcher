"""04 -- F6 (c): the aggregate lemma test (choices F6-1 D6, F6-4; MC-1, MC-2, MC-5).

T = sum_i w_i S_i^2 / sum_i w_i r_i N_i / 4, w_i = 1/(N_i B_i), per (m, mode, arm class),
for conventions: frozen (A7 r, X = 2S), frozen_Xtotal (S' = X_total/2), rank (r = rank),
rank1 (r = rank + 1). Under the lemma E[num] >= E[den], so T >= 1 up to sampling error.

Interval: curve bootstrap stratified by rung (resample the five curve indices within each
rung; every arm of the class on a resampled curve moves with it), 20000 replicates (MC-1),
percentile 95% and 99%; 200 bootstrap seeds (MC-2) -> mean and s.d. of each endpoint.
Coverage at five curves per rung (MC-5): 1000 synthetic designs per decision cell drawn from
NULL-P (frozen: r* ~ exact compound Poisson with the instance's own H1 means, S fixed) or
NULL-G (rank: u* ~ Gamma(rank+1, 1/kappa_hat), r fixed), 2000 replicates each, true T known.
"""
import json
import math
import os
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib575 import OUT, dump  # noqa: E402
from numlib import cp_pmf  # noqa: E402
import importlib.util  # noqa: E402

spec = importlib.util.spec_from_file_location("n3", os.path.join(os.path.dirname(os.path.abspath(__file__)), "03_f6_nulls.py"))
n3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(n3)
CLS = ("TT", "TB", "SS")
CONV = ("frozen", "frozen_Xtotal", "rank", "rank1")


def contributions(x, conv):
    w = 1.0 / (x["N"] * x["B"])
    if conv == "frozen":
        s, r = x["S"], x["r_frozen"]
    elif conv == "frozen_Xtotal":
        s, r = (2 * x["S"] + x["B"] + x["attempts"] + 2) / 2.0, x["r_frozen"]
    elif conv == "rank":
        s, r = x["S"], x["rank"]
    else:
        s, r = x["S"], x["rank"] + 1
    return w * s * s, w * r * x["N"] / 4.0


def cell_arrays(rows, conv):
    """A[rung_index, curve], Bd[rung_index, curve] summed over the class's arms on the curve."""
    rungs = sorted({x["bits"] for x in rows})
    curves = sorted({x["curve"] for x in rows})
    A = np.zeros((len(rungs), len(curves)))
    Bd = np.zeros((len(rungs), len(curves)))
    present = np.zeros((len(rungs), len(curves)), dtype=bool)
    for x in rows:
        a, b = contributions(x, conv)
        i, j = rungs.index(x["bits"]), curves.index(x["curve"])
        A[i, j] += a
        Bd[i, j] += b
        present[i, j] = True
    return A, Bd, present, rungs, curves


def boot(A, Bd, present, reps, seed):
    rng = np.random.default_rng(seed)
    nR, nC = A.shape
    Ts = np.empty(reps)
    num = np.zeros(reps)
    den = np.zeros(reps)
    for i in range(nR):
        avail = np.flatnonzero(present[i])
        if len(avail) == 0:
            continue
        idx = avail[rng.integers(0, len(avail), size=(reps, len(avail)))]
        num += A[i][idx].sum(axis=1)
        den += Bd[i][idx].sum(axis=1)
    Ts = num / den
    return Ts


def pct(Ts, level):
    lo = (1 - level) / 2
    return float(np.quantile(Ts, lo)), float(np.quantile(Ts, 1 - lo))


def main():
    xs = [json.loads(l) for l in open(os.path.join(OUT, "instances.jsonl"))]
    ev = [x for x in xs if x["evaluable"] and x["src"] != "stage-r"]
    groups = defaultdict(list)
    for x in ev:
        groups[(x["m"], x["mode"], x["cls"])].append(x)
    res = {}
    for (m, mode, cl), rows in sorted(groups.items()):
        for conv in CONV:
            A, Bd, present, rungs, curves = cell_arrays(rows, conv)
            T = float(A[present].sum() / Bd[present].sum())
            lo95, hi95, lo99, hi99 = [], [], [], []
            for seed in range(200):
                Ts = boot(A, Bd, present, 20000, seed)
                a, b = pct(Ts, 0.95)
                c, d = pct(Ts, 0.99)
                lo95.append(a); hi95.append(b); lo99.append(c); hi99.append(d)
            res[f"m{m}|{mode}|{cl}|{conv}"] = {
                "n_instances": len(rows), "rungs": rungs, "T": T,
                "ci95": [float(np.mean(lo95)), float(np.mean(hi95))],
                "ci95_endpoint_mc_sd": [float(np.std(lo95, ddof=1)), float(np.std(hi95, ddof=1))],
                "ci99": [float(np.mean(lo99)), float(np.mean(hi99))],
                "ci99_endpoint_mc_sd": [float(np.std(lo99, ddof=1)), float(np.std(hi99, ddof=1))],
                "upper95_below_1": float(np.mean(hi95)) < 1.0,
                "seeds_with_upper95_below_1": int(sum(1 for h in hi95 if h < 1.0))}
        print(m, mode, cl, {c: round(res[f"m{m}|{mode}|{cl}|{c}"]["T"], 3) for c in CONV}, flush=True)

    # ---- MC-5 coverage at five curves per rung -------------------------------------------------
    laws = n3.jump_laws()
    kap = {}
    for m in (3, 4, 5):
        for mode in ("census", "on"):
            rs = [x for x in ev if x["m"] == m and x["mode"] == mode and x["cls"] == "random"]
            u = sum(4 * x["S"] ** 2 / x["N"] for x in rs)
            kap[(m, mode)] = sum(x["rank"] + 1 for x in rs) / u
    cov = {}
    for (m, mode, cl) in [(m, "on", c) for m in (3, 4, 5) for c in ("random", "structured")] + [(3, "on", "j0_random")]:
        rows = groups[(m, mode, cl)]
        # frozen under NULL-P: per-instance exact pmf of r*
        cdfs, rels = [], []
        Er = []
        for x in rows:
            mus = {c: x[f"mu_{c}"] for c in CLS}
            parts, lam = [], 0.0
            for c in CLS:
                if mus[c] > 0:
                    L = laws[(m, c)]
                    parts.append((mus[c] / L["EJ"], L["pmf"]))
                    lam += mus[c] / L["EJ"]
            if lam > 0:
                mix = np.zeros(max(len(p) for _, p in parts))
                for lc, p in parts:
                    mix[:len(p)] += (lc / lam) * p
                f = cp_pmf(lam, mix)
            else:
                f = np.array([1.0])
            cdfs.append(np.cumsum(f))
            rels.append(x["relations"])
            Er.append(x["relations"] + sum(mus.values()))
        w = np.array([1.0 / (x["N"] * x["B"]) for x in rows])
        Sv = np.array([float(x["S"]) for x in rows])
        Nv = np.array([float(x["N"]) for x in rows])
        T_true_f = float((w * Sv ** 2).sum() / (w * np.array(Er) * Nv / 4).sum())
        rungs = sorted({x["bits"] for x in rows})
        curves = sorted({x["curve"] for x in rows})
        ri = np.array([rungs.index(x["bits"]) for x in rows])
        ci = np.array([curves.index(x["curve"]) for x in rows])
        rng = np.random.default_rng(575)
        hit95 = hit99 = 0
        hitg95 = hitg99 = 0
        kh = kap[(m, mode)]
        q = np.array([x["rank"] + 1 for x in rows], dtype=float)
        rk = np.array([x["rank"] for x in rows], dtype=float)
        T_true_g = float((w * (q / kh) * Nv / 4).sum() / (w * rk * Nv / 4).sum())
        for rep in range(1000):
            # NULL-P draw for r_frozen
            rs = np.array([rels[i] + int(np.searchsorted(cdfs[i], rng.random())) for i in range(len(rows))], dtype=float)
            A = np.zeros((len(rungs), len(curves)))
            Bd = np.zeros((len(rungs), len(curves)))
            np.add.at(A, (ri, ci), w * Sv ** 2)
            np.add.at(Bd, (ri, ci), w * rs * Nv / 4)
            present = Bd > 0
            Ts = boot(A, Bd, present, 2000, 10_000 + rep)
            a, b = pct(Ts, 0.95)
            c, d = pct(Ts, 0.99)
            hit95 += a <= T_true_f <= b
            hit99 += c <= T_true_f <= d
            # NULL-G draw for r_rank: u* ~ Gamma(q, 1/kh), S* = sqrt(u* N)/2, r = rank
            us = rng.gamma(q, 1.0 / kh)
            S2 = us * Nv / 4.0
            A2 = np.zeros((len(rungs), len(curves)))
            B2 = np.zeros((len(rungs), len(curves)))
            np.add.at(A2, (ri, ci), w * S2)
            np.add.at(B2, (ri, ci), w * rk * Nv / 4)
            Ts2 = boot(A2, B2, B2 > 0, 2000, 20_000 + rep)
            a, b = pct(Ts2, 0.95)
            c, d = pct(Ts2, 0.99)
            hitg95 += a <= T_true_g <= b
            hitg99 += c <= T_true_g <= d
        cov[f"m{m}|{mode}|{cl}"] = {"frozen_NULL_P": {"T_true": T_true_f, "coverage95": hit95 / 1000, "coverage99": hit99 / 1000},
                                    "rank_NULL_G_khat": {"T_true": T_true_g, "coverage95": hitg95 / 1000, "coverage99": hitg99 / 1000},
                                    "designs": 1000, "reps_per_design": 2000}
        print("coverage", m, mode, cl, cov[f"m{m}|{mode}|{cl}"], flush=True)
    dump("04_f6_aggregate.json", {"weights": "w_i = 1/(N_i*B_i)", "cells": res, "coverage_mc5": cov})


if __name__ == "__main__":
    main()
