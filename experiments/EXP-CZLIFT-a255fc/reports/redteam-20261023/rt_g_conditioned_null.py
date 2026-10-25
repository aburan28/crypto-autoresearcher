"""Red-team check G (TASK-20261023-326d39, joint R1): does the kernel-height floor explain the excess?

Same data and homomorphism representation as rt_f (cyclic primes, cells with H <= 30000, PARI
height normalization). Three nulls on the frozen cells, 100 replicates each, rng 20261023:
  R0  random homomorphism with the same image index k_p (as rt_f);
  R1  R0 conditioned on lambda1^2(ker) >= 2 log p           (the floor without its constant);
  R2  R0 conditioned on lambda1^2(ker) >= 2 log p + gap_min (gap_min = smallest observed
      lambda1^2 - 2 log p over this curve's cyclic primes; uses the observed constant).
Rejection sampling, at most 20000 draws per (curve, p) and replicate; failures are counted.
If R1/R2 reproduce the observed median while R0 does not, the arithmetic floor
h^(K) >= 2 log p - c_E for K in ker(red_p) is the mechanism of the residual excess.
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rt_b_lattice_null as B  # noqa: E402
import rt_c_points_kernel_index as C  # noqa: E402
import rt_f_kernel_minimum as F  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
OUT = os.path.join(HERE, "rt_g_conditioned_null_output.json")


def main():
    rng = np.random.default_rng(20261023)
    e = json.load(open(F.E_OUT))
    f = json.load(open(F.OUT))
    raw = json.load(open(os.path.join(ROOT, "experiments", "EXP-CZLIFT-a255fc", "runs", "RUN-CZLIFT-490b33", "raw-result.json")))
    curves = {cv["label"]: cv for cv in raw["raw"]["curves"]}
    REPS = 100
    meds = {k: [[] for _ in range(REPS)] for k in ("R0", "R1", "R2")}
    actual = []
    failures = {"R1": 0, "R2": 0}
    per_curve = {}
    for lab, info in e["curves"].items():
        cv = curves[lab]
        r = cv["rank_recalled"]
        G = np.array(info["gram"])
        Vc = np.vstack([np.zeros((1, r), dtype=np.int64), np.array(info["coords"], dtype=np.int64)])
        A, Bc, b2 = C.short_model(cv["ainvs"])
        basis = [tuple(b) for b in info["basis_naive"]]
        frows = {x["p"]: x for x in f["curves"][lab]["rows"]}
        if not frows:
            continue
        gap_min = min(x["lambda1sq_minus_2logp"] for x in frows.values())
        pc = {k: [[] for _ in range(REPS)] for k in ("R0", "R1", "R2")}
        pc_act = []
        for p in cv["primes"]:
            if p not in frows:
                continue
            cells = [c for c in cv["coverage"] if c["p"] == p and c["H"] <= 30000 and F.frozen(c)]
            if not cells:
                continue
            Np = frows[p]["N_p"]
            k_p = frows[p]["k_p"]
            m = Np // k_p
            gen = F.find_generator(A, Bc, p, Np, rng)
            table = {}
            P = None
            for k in range(Np):
                table[P] = k
                P = C.ec_add(P, gen, A, p)
            a = np.array([table[C.reduce_pt(b, p, b2)] for b in basis], dtype=np.int64)
            img = (Vc @ a) % Np
            for c in cells:
                rr = len(np.unique(img[: c["n_points"]])) / c["model_distinct"]
                actual.append(rr)
                pc_act.append(rr)
            floor1 = 2 * math.log(p)
            floor2 = floor1 + gap_min
            Q = max(floor2 * 1.01, 1e-9)
            W = B._enumerate(G, Q)
            qW = np.einsum("ij,jk,ik->i", W, G, W)
            nz = qW > 1e-12
            W, qW = W[nz], qW[nz]

            def draw():
                while True:
                    g = rng.integers(0, m, size=r)
                    if math.gcd(*[int(x) for x in g], m) == 1:
                        return g * k_p

            def lam_ok(g, floor):
                sel = qW < floor
                if not sel.any():
                    return True
                return not np.any(((W[sel] @ g) % Np) == 0)

            for t in range(REPS):
                for key, floor in (("R0", None), ("R1", floor1), ("R2", floor2)):
                    tries = 0
                    while True:
                        g = draw()
                        tries += 1
                        if floor is None or lam_ok(g, floor):
                            break
                        if tries >= 20000:
                            failures[key] += 1
                            break
                    imgr = (Vc @ g) % Np
                    for c in cells:
                        rr = len(np.unique(imgr[: c["n_points"]])) / c["model_distinct"]
                        meds[key][t].append(rr)
                        pc[key][t].append(rr)
        if pc_act:
            per_curve[lab] = {"observed": F.upper_median(pc_act), "gap_min": gap_min}
            for key in pc:
                ms = [F.upper_median(x) for x in pc[key] if x]
                per_curve[lab][key] = [round(float(np.median(ms)), 4), round(float(np.percentile(ms, 2.5)), 4),
                                       round(float(np.percentile(ms, 97.5)), 4)]
        print(lab, per_curve.get(lab), flush=True)
    out = {"cells": len(actual), "observed_median": F.upper_median(actual), "rejection_failures": failures,
           "per_curve": per_curve}
    for key in meds:
        ms = [F.upper_median(x) for x in meds[key]]
        out[key] = {"median": float(np.median(ms)), "band_2p5_97p5": [float(np.percentile(ms, 2.5)), float(np.percentile(ms, 97.5))],
                    "reps_ge_observed": int(sum(x >= out["observed_median"] for x in ms))}
    json.dump(out, open(OUT, "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "per_curve"}, indent=1))


if __name__ == "__main__":
    main()
