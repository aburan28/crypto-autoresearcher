"""Proves-too-much control: PTM-1, PTM-2, PTM-3 (attacks/choices.yaml ptm1_choice, ptm3_choice).

PTM-1  random arms read as structured, on the committed rows.  Each random arm X of a triple is
       the "structured" arm against the other two of its own triple (C_R = sum_j mean of two;
       s_j^2 over the two; V = max(sum s_j^2, C_R); SD = sqrt(1.5 V); resolved iff C_R >= 10),
       over every (X, class in {TT, SS}, m, rung) with the frozen drop rule on the triple
       (396 pseudo-cells), and the Stage R rule on R16's random arms (12 pseudo-cells).  The same
       statistic is simulated under G-POIS, G-NB and G-CP (R = 4000, default_rng(20261201+k))
       on the same designs, which (a) gives its nominal rate and (b) checks each null generator
       against known-null data.  The secondary (three randoms of the other family where |F|
       matches) exists on 16 of 165 (m, bits, curve) and is not a family; not computed.
PTM-2  synthetic null counts through A1, the excursion rule, the selection of the (up to) four
       most extreme excursions and Stage R on fresh synthetic curves (discovery design means as
       the fresh-curve proxy, the actual R16 design for the four R16 cells); per generator,
       R = 20000 families, default_rng(20261101 + k).
PTM-3  planted excess on the committed structured counts: n' = n + Poisson((kappa - 1) rbar_j),
       randoms unchanged, at 30 and 32 bits and at each excursion rung; Stage R on synthetic fresh
       curves (G-CP null + the same planted Poisson excess); kappa in {1.1, 1.25, 1.5, 2, 3, 5};
       R = 4000 per (cell, kappa); default_rng(20261201 + i).  Sensitivity: the excess added as a
       compound (bundle-shaped) count with the rung's multiplicity distribution.
Output: attacks/out/09_ptm.json
"""
import json
import math
import os
import statistics
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rtlib import EXCURSIONS, OUT, RANDOMS, RUNGS, STRUCT, usable  # noqa: E402
from j6design import Design, frozen_count, gen_counts, zstat  # noqa: E402

SUB, DIK = RANDOMS["subgroup"], RANDOMS["dickson"]


def z2(A, Rr):
    """A: (R, J); Rr: (R, 2, J) -> z with a two-random reference."""
    C_A = A.sum(axis=1)
    C_R = Rr.sum(axis=(1, 2)) / 2.0
    s2 = Rr.var(axis=1, ddof=1).sum(axis=1)
    V = np.maximum(s2, C_R)
    SD = np.sqrt(1.5 * V)
    with np.errstate(divide="ignore", invalid="ignore"):
        z = np.where(SD > 0, (C_A - C_R) / SD, np.nan)
    return z, C_R


def ptm1_real(des):
    cells = []
    for (cl, m, b), d in des.cells.items():
        for fam, arms in (("sub", SUB), ("dik", DIK)):
            trip = {j: v for j, v in d["rand"][fam].items() if v is not None}
            # frozen drop rule on the triple: censored instances drop the curve
            keep = []
            for j in trip:
                rs = [des.main.get(("main", m, b, j, a, "census")) for a in arms]
                if all(usable(r) for r in rs) and not any(bool(r["harvest"]["SS"]["at_A_fix"].get("censored")) for r in rs):
                    keep.append(j)
            for xi, X in enumerate(arms):
                nA = [trip[j][xi] for j in keep]
                nR = [[trip[j][k] for k in range(3) if k != xi] for j in keep]
                if not keep:
                    continue
                C_A = float(sum(nA))
                C_R = sum(sum(v) / 2 for v in nR)
                s2 = sum(statistics.variance(v) for v in nR)
                V = max(s2, C_R)
                SD = math.sqrt(1.5 * V)
                z = (C_A - C_R) / SD if SD > 0 else None
                cells.append({"arm": X, "class": cl, "m": m, "bits": b, "curves": keep, "C_A": C_A, "C_R": C_R,
                              "z": z, "resolved": C_R >= 10})
    res = [c for c in cells if c["resolved"] and c["z"] is not None]
    exc = [c for c in res if abs(c["z"]) > 3]
    by = defaultdict(lambda: [0, 0])
    for c in res:
        by[f"{c['class']}|{c['m']}"][0] += 1
        by[f"{c['class']}|{c['m']}"][1] += abs(c["z"]) > 3
    return cells, {"pseudo_cells": len(cells), "resolved": len(res), "excursions": len(exc),
                   "rate": len(exc) / max(1, len(res)),
                   "positive": sum(1 for c in exc if c["z"] > 0),
                   "by_class_m": {k: {"resolved": v[0], "excursions": v[1]} for k, v in sorted(by.items())},
                   "excursion_list": [[c["arm"], c["class"], c["m"], c["bits"], round(c["z"], 3)] for c in exc]}


def ptm1_sim(des, cells, gen, rng, R=4000):
    tot = 0.0
    by = defaultdict(float)
    nres = 0.0
    for c in cells:
        cl, m, b = c["class"], c["m"], c["bits"]
        d = des.cells[(cl, m, b)]
        fam = "dik" if c["arm"] in DIK else "sub"
        mu = [statistics.mean(d["rand"][fam][j]) for j in c["curves"]]
        X = gen_counts(gen, rng, mu, (R, 3), cl, m, b, des)
        z, C_R = z2(X[:, 0, :], X[:, 1:3, :])
        e = (C_R >= 10) & (np.abs(np.nan_to_num(z)) > 3)
        tot += e.mean()
        nres += (C_R >= 10).mean()
        by[f"{cl}|{m}"] += e.mean()
    return {"E_excursions": tot, "E_resolved": nres, "rate": tot / max(1e-9, nres),
            "E_by_class_m": {k: round(v, 3) for k, v in sorted(by.items())}}


def ptm1_stage_r(des):
    out = []
    for (A, cl, m, b) in EXCURSIONS:
        arms = RANDOMS[A]
        rows = {j: [frozen_count(des.sr.get(("main", m, b, j, a, "census")), cl) for a in arms] for j in range(5, 10)}
        for xi, X in enumerate(arms):
            nA = [rows[j][xi] for j in rows]
            nR = [[rows[j][k] for k in range(3) if k != xi] for j in rows]
            C_A = float(sum(nA))
            C_R = sum(sum(v) / 2 for v in nR)
            s2 = sum(statistics.variance(v) for v in nR)
            SD = math.sqrt(1.5 * max(s2, C_R))
            out.append({"cell": [A, cl, m, b], "random_as_structured": X, "z": (C_A - C_R) / SD,
                        "resolved": C_R >= 10})
    return out


def q_replicate(des, gen, rng, cl, m, b, A, R=20000, sr=False):
    """P(z > 3) and P(z < -3) on fresh synthetic curves for cell (A, cl, m, b)."""
    if sr:
        mu = [statistics.mean(frozen_count(des.sr.get(("main", m, b, j, a, "census")), cl) for a in RANDOMS[A])
              for j in range(5, 10)]
    else:
        d = des.cells[(cl, m, b)]
        fam = "dik" if A == "dickson" else "sub"
        mu = [statistics.mean(d["rand"][fam][j]) for j in d["kept"][A]]
        if not mu:
            return 0.0, 0.0
    X = gen_counts(gen, rng, mu, (R, 4), cl, m, b, des)
    z, C_R = zstat(X[:, 0, :], X[:, 1:4, :])[:2]
    res = C_R >= 10
    zz = np.where(res, np.nan_to_num(z), 0.0)
    return float((zz > 3).mean()), float((zz < -3).mean())


def ptm2(des, gen, gi, R=20000):
    import importlib.util
    spec = importlib.util.spec_from_file_location("fam04", os.path.join(os.path.dirname(os.path.abspath(__file__)), "04_j6_family_null.py"))
    fam04 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fam04)
    rng = np.random.default_rng(20261101 + gi)
    cols = fam04.simulate(des, gen, rng, R)
    keys, Z = [], []
    for key, z, res in cols:
        if z is None:
            continue
        keys.append(key)
        Z.append(np.where(res & ~np.isnan(z), z, 0.0))
    Z = np.array(Z)            # (cells, R)
    rng2 = np.random.default_rng(20261111 + gi)
    q = []
    for (A, cl, m, b) in keys:
        sr = (A, cl, m, b) in EXCURSIONS
        q.append(q_replicate(des, gen, rng2, cl, m, b, A, R=20000, sr=sr))
    q = np.array(q)            # (cells, 2): P(z>3), P(z<-3)
    absz = np.abs(Z)
    exc = absz > 3
    n_exc = exc.sum(axis=0)
    p_norep = np.ones(R)
    sel_count = np.zeros(R)
    for r in range(R):
        idx = np.flatnonzero(exc[:, r])
        if len(idx) == 0:
            continue
        top = idx[np.argsort(-absz[idx, r])][:4]
        sel_count[r] = len(top)
        for i in top:
            qq = q[i, 0] if Z[i, r] > 0 else q[i, 1]
            p_norep[r] *= (1 - qq)
    p_rep = 1 - p_norep
    has = n_exc >= 1
    return {"E_excursions": float(n_exc.mean()), "P_excursion_ge_1": float(has.mean()),
            "P_ge_4": float((n_exc >= 4).mean()),
            "per_cell_rate_mean": float(exc.mean()),
            "E_selected": float(sel_count.mean()),
            "P_any_replication_given_excursions": float(p_rep[has].mean()) if has.any() else None,
            "P_any_replication_given_ge4": float(p_rep[n_exc >= 4].mean()) if (n_exc >= 4).any() else None,
            "P_replicated_anomaly_overall": float(p_rep.mean()),
            "mean_q_same_sign_over_cells": float(np.mean(np.maximum(q[:, 0], q[:, 1]))),
            "nominal_one_sided": 0.00135}


def ptm3(des):
    kappas = [1.1, 1.25, 1.5, 2.0, 3.0, 5.0]
    out = {}
    targets = set()
    for A in STRUCT:
        for cl in ("TT", "SS"):
            for m in (3, 4, 5):
                for b in (30, 32):
                    targets.add((A, cl, m, b))
    for e in EXCURSIONS:
        targets.add(e)
    i = 0
    for (A, cl, m, b) in sorted(targets):
        d = des.cells[(cl, m, b)]
        fam = "dik" if A == "dickson" else "sub"
        kept = d["kept"][A]
        key = f"{A}|{cl}|{m}|{b}"
        if not kept:
            out[key] = {"note": "no kept curves"}
            continue
        nA = np.array([d["obs"][(A, j)] for j in kept], dtype=float)
        nR = np.array([d["rand"][fam][j] for j in kept], dtype=float).T   # (3, J)
        rbar = nR.mean(axis=0)
        C_R = nR.sum() / 3
        s2 = nR.var(axis=0, ddof=1).sum()
        SD = math.sqrt(4 * max(s2, C_R) / 3)
        rec = {"C_R": C_R, "resolved": C_R >= 10, "kappa": {}}
        for kap in kappas:
            i += 1
            rng = np.random.default_rng(20261201 + i)
            R = 4000
            for shape in ("poisson", "compound"):
                if shape == "poisson":
                    add = rng.poisson((kap - 1) * rbar[None, :] * np.ones((R, len(kept))))
                else:
                    add = gen_counts("G-CP", rng, list((kap - 1) * rbar), (R, 1), cl, m, b, des)[:, 0, :]
                CA = (nA[None, :] + add).sum(axis=1)
                zd = (CA - C_R) / SD if C_R >= 10 else np.full(R, -np.inf)
                p_disc = float((zd > 3).mean())
                mu = list(rbar)
                X = gen_counts("G-CP", rng, mu, (R, 4), cl, m, b, des)
                if shape == "poisson":
                    addsr = rng.poisson((kap - 1) * np.array(mu)[None, :] * np.ones((R, len(mu))))
                else:
                    addsr = gen_counts("G-CP", rng, list((kap - 1) * np.array(mu)), (R, 1), cl, m, b, des)[:, 0, :]
                zsr, CRs = zstat(X[:, 0, :] + addsr, X[:, 1:4, :])[:2]
                p_sr = float(((CRs >= 10) & (np.nan_to_num(zsr) > 3)).mean())
                rec["kappa"].setdefault(str(kap), {})[shape] = {"P_discovery_z_gt3": p_disc, "P_stageR_z_gt3": p_sr,
                                                                 "P_not_ONULL": p_disc * p_sr}
        for shape in ("poisson", "compound"):
            X_ = None
            for kap in kappas:
                if rec["kappa"][str(kap)][shape]["P_not_ONULL"] >= 0.5:
                    X_ = kap
                    break
            rec[f"X_{shape}"] = X_ if X_ is not None else "> 5.0 (not reached)"
        out[key] = rec
        print(key, rec["X_poisson"], rec["X_compound"], file=sys.stderr)
    # per (class, m) summary: weakest arm at 30 and 32 bits (a closure covers every arm)
    summ = {}
    for cl in ("TT", "SS"):
        for m in (3, 4, 5):
            xs = []
            for A in STRUCT:
                for b in (30, 32):
                    v = out.get(f"{A}|{cl}|{m}|{b}", {})
                    xs.append((A, b, v.get("X_poisson"), v.get("X_compound")))
            summ[f"{cl}|{m}"] = xs
    return out, summ


def main():
    des = Design()
    cells, real = ptm1_real(des)
    out = {"PTM1": {"real": real, "stage_r": ptm1_stage_r(des)}}
    print("PTM1 real", {k: real[k] for k in ("resolved", "excursions", "rate", "positive")}, file=sys.stderr)
    out["PTM1"]["simulated_same_statistic"] = {}
    for gi, gen in enumerate(("G-POIS", "G-NB", "G-CP")):
        rng = np.random.default_rng(20261201 + 100 + gi)
        out["PTM1"]["simulated_same_statistic"][gen] = ptm1_sim(des, cells, gen, rng)
        print("PTM1 sim", gen, out["PTM1"]["simulated_same_statistic"][gen], file=sys.stderr)
    out["PTM2"] = {}
    for gi, gen in enumerate(("G-POIS", "G-NB", "G-CP")):
        out["PTM2"][gen] = ptm2(des, gen, gi)
        print("PTM2", gen, out["PTM2"][gen], file=sys.stderr)
    out["PTM3"], out["PTM3_summary_by_class_m"] = ptm3(des)
    with open(os.path.join(OUT, "out", "09_ptm.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)


if __name__ == "__main__":
    main()
