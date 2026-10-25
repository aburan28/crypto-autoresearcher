"""Red-team check E (TASK-20261023-326d39, joint R1): which part of the coverage excess is geometry
and which is arithmetic.

Needs cypari2 (PARI/GP 2.17.2 was used, from a scratch virtualenv; not a repository dependency).
For every ladder curve of recalled rank r >= 1:
  1. enumerate all points of naive height <= HMAX with rt_c's exact sieve (own code);
  2. compute canonical heights with PARI ellheight and pick a basis greedily (smallest canonical
     height first, independence by Gram determinant); express EVERY point in that basis by solving
     the height-pairing system and rounding, and verify each representation exactly with PARI's
     group law (ellmul / elladd over Q). A curve whose points do not all have integral coordinates
     in the chosen basis is reported and skipped;
  3. three versions of the frozen cells with H <= HMAX, nested in H per (curve, p):
       observed      the actual reductions mod p (recorded `distinct`);
       E1 actual-set the actual point set (its Mordell-Weil coordinates, ordered by naive height)
                     pushed through a uniformly random homomorphism Z^r -> Z/N_p;
       E2 MW-ball    the same number of shortest vectors of the actual Mordell-Weil Gram matrix
                     (canonical-height ball) through a random homomorphism;
     200 replicates each, numpy default_rng(20261023).
If E1 reproduces the observed median, the excess is the geometry of the point set under ANY
homomorphism (no arithmetic of reduction mod p); if E1 falls short, the remainder is arithmetic.
Usage: <venv python> rt_e_mw_coordinate_null.py [HMAX]  (default 30000)
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rt_c_points_kernel_index as C  # noqa: E402  (own red-team code)
import rt_b_lattice_null as B  # noqa: E402  (own red-team code: Fincke-Pohst)

import cypari2  # noqa: E402

pari = cypari2.Pari()
pari.allocatemem(2 * 10 ** 9, silent=True) if hasattr(pari, "allocatemem") else None
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
RUNS = ["RUN-CZLIFT-74f172", "RUN-CZLIFT-490b33"]


def to_pari_point(pt, ai):
    a, d, c = pt
    a1, a2, a3, a4, a6 = ai
    X = pari(f"{a}/{d * d}")
    Yc = pari(f"{c}/{d ** 3}")
    y = (Yc - a1 * X - a3) / 2
    return pari.vector(2, [X, y])


def mw_coordinates(ai, pts, r):
    E = pari.ellinit(ai)
    tors = int(pari.elltors(E)[0])
    P = [to_pari_point(q, ai) for q in pts]
    for Q in P[:50]:
        assert pari.ellisoncurve(E, Q)
    h = [float(pari.ellheight(E, Q)) for Q in P]
    order = sorted(range(len(P)), key=lambda i: h[i])
    basis = []
    for i in order:
        if h[i] < 1e-9:
            continue
        cand = basis + [i]
        G = np.array([[float(pari.ellheight(E, P[s], P[t])) for t in cand] for s in cand])
        if np.linalg.det(G) > 1e-6 * max(1.0, np.prod(np.diag(G))):
            basis = cand
        if len(basis) == r:
            break
    G = np.array([[float(pari.ellheight(E, P[s], P[t])) for t in basis] for s in basis])
    Ginv = np.linalg.inv(G)
    coords = []
    bad = 0
    maxres = 0.0
    for Q in P:
        rhs = np.array([float(pari.ellheight(E, Q, P[t])) for t in basis])
        x = Ginv @ rhs
        n = np.round(x).astype(int)
        maxres = max(maxres, float(np.abs(x - n).max()))
        # exact verification
        S = pari.vector(1, [0])
        for k, t in enumerate(basis):
            if n[k]:
                S = pari.elladd(E, S, pari.ellmul(E, P[t], int(n[k])))
        if S != Q:
            bad += 1
        coords.append(n.tolist())
    return {"torsion_order": tors, "basis_naive": [pts[i] for i in basis], "gram": G.tolist(),
            "regulator_det": float(np.linalg.det(G)), "coords": coords, "unverified": bad,
            "max_rounding_residual": maxres}


def frozen(c):
    return c["n_points"] >= 30 and c["model_distinct"] <= 0.9 * c["N_p"]


def upper_median(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2] if xs else None


def main():
    HMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 30000
    rng = np.random.default_rng(20261023)
    raws = {r: json.load(open(os.path.join(ROOT, "experiments", "EXP-CZLIFT-a255fc", "runs", r, "raw-result.json")))
            for r in RUNS}
    curves = raws["RUN-CZLIFT-490b33"]["raw"]["curves"]
    out = {"HMAX": HMAX, "pari_version": str(pari("version()")), "curves": {}, "summary": {}}
    per = {}
    for cv in curves:
        r = cv["rank_recalled"]
        if r < 1:
            continue
        pts = sorted(C.enumerate_points(cv["ainvs"], HMAX), key=C.height)
        mw = mw_coordinates(cv["ainvs"], pts, r)
        info = dict(mw)
        info["points_naive_sorted"] = pts
        info["n_points"] = len(pts) + 1
        out["curves"][cv["label"]] = info
        print(cv["label"], "r", r, "points", len(pts) + 1, "unverified", mw["unverified"],
              "maxres %.2e" % mw["max_rounding_residual"], "tors", mw["torsion_order"], flush=True)
        if mw["unverified"] or mw["torsion_order"] != 1:
            continue
        V = np.vstack([np.zeros((1, r), dtype=np.int64), np.array(mw["coords"], dtype=np.int64)])  # O first
        Gm = np.array(mw["gram"])
        Wball, _ = B.shortest_vectors(Gm / Gm.max(), len(V) if len(V) % 2 else len(V) + 1, rng)
        rows_by_p = {}
        for c in cv["coverage"]:
            if c["H"] <= HMAX and frozen(c):
                rows_by_p.setdefault(c["p"], []).append(c)
        if rows_by_p:
            per[cv["label"]] = (V, Wball, rows_by_p)
    # observed on the same cell subset
    obs = [c["ratio_to_model"] for lab, (V, W, rb) in per.items() for rows in rb.values() for c in rows]
    e1, e2 = [], []
    pc1 = {lab: [] for lab in per}
    pc2 = {lab: [] for lab in per}
    for _ in range(200):
        a1, a2 = [], []
        c1 = {lab: [] for lab in per}
        c2 = {lab: [] for lab in per}
        for lab, (V, W, rb) in per.items():
            for p, rows in rb.items():
                Np = rows[0]["N_p"]
                g = rng.integers(0, Np, size=V.shape[1])
                img1 = (V @ g) % Np
                img2 = (W @ g) % Np
                for c in rows:
                    n = c["n_points"]
                    r1 = len(np.unique(img1[:n])) / c["model_distinct"]
                    r2 = len(np.unique(img2[:n])) / c["model_distinct"]
                    a1.append(r1); a2.append(r2); c1[lab].append(r1); c2[lab].append(r2)
        e1.append(upper_median(a1)); e2.append(upper_median(a2))
        for lab in per:
            pc1[lab].append(upper_median(c1[lab])); pc2[lab].append(upper_median(c2[lab]))
    out["summary"] = {
        "cells_H_le_HMAX_frozen": len(obs),
        "observed_median": upper_median(obs),
        "E1_actual_set_random_hom": {"median": float(np.median(e1)), "band_2p5_97p5": [float(np.percentile(e1, 2.5)), float(np.percentile(e1, 97.5))],
                                     "reps_ge_observed": int(sum(x >= upper_median(obs) for x in e1))},
        "E2_MW_ball_random_hom": {"median": float(np.median(e2)), "band_2p5_97p5": [float(np.percentile(e2, 2.5)), float(np.percentile(e2, 97.5))],
                                  "reps_ge_observed": int(sum(x >= upper_median(obs) for x in e2))},
        "per_curve": {lab: {"observed": upper_median([c["ratio_to_model"] for rows in per[lab][2].values() for c in rows]),
                            "E1_median": float(np.median(pc1[lab])), "E1_band": [float(np.percentile(pc1[lab], 2.5)), float(np.percentile(pc1[lab], 97.5))],
                            "E2_median": float(np.median(pc2[lab])), "E2_band": [float(np.percentile(pc2[lab], 2.5)), float(np.percentile(pc2[lab], 97.5))]}
                      for lab in per},
    }
    path = os.path.join(HERE, f"rt_e_mw_coordinate_null_output_H{HMAX}.json")
    json.dump(out, open(path, "w"), indent=1, default=str)
    print(json.dumps(out["summary"], indent=1))


if __name__ == "__main__":
    main()
