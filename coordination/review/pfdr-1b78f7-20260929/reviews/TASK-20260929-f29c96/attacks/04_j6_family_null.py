"""J6(a) family-wise calibration of the excursion rule (MC-4), and the per-cell null tails.

For each null generator (G-POIS, G-NB, G-CP, G-RES; attacks/choices.yaml) and every
(A in {subgroup, small_x, dickson}, class in {TT, SS}, m, rung) cell on its actual design
(kept curves, three matched randoms, subgroup and small_x sharing one simulated random_sub
triple, V floor, C_R >= 10 resolution), simulate R = 20000 families under kappa = 1 and
record: per-cell P(resolved), P(|z| > 3 | resolved), P(z > 3), P(z < -3); the family
distribution of the number of excursions; P(>= 4); P(>= 4 and all positive); P(max |z| >=
4.75).  Seeds: numpy default_rng(20260929 + k), k = 0..3 in generator order.
Output: attacks/out/04_j6_family_null.json
"""
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rtlib import OUT, RUNGS  # noqa: E402
from j6design import Design, gen_counts, zstat  # noqa: E402
import statistics  # noqa: E402

GENS = ["G-POIS", "G-NB", "G-CP", "G-RES"]
R = int(os.environ.get("RT_R", "20000"))


def simulate(des, gen, rng, R):
    cols = []   # per cell: (key, z, resolved)
    for m in (3, 4, 5):
        for b in RUNGS:
            for cl in ("TT", "SS"):
                d = des.cells[(cl, m, b)]
                # random_sub family: subgroup, small_x, r0, r1, r2
                sc = [j for j in range(5) if d["rand"]["sub"].get(j) is not None]
                if sc:
                    mu = [statistics.mean(d["rand"]["sub"][j]) for j in sc]
                    X = gen_counts(gen, rng, mu, (R, 5), cl, m, b, des)
                    for ai, A in ((0, "subgroup"), (1, "small_x")):
                        kc = [sc.index(j) for j in d["kept"][A]]
                        if not kc:
                            cols.append(((A, cl, m, b), None, None))
                            continue
                        z, C_R, _ = zstat(X[:, ai, kc], X[:, 2:5, :][:, :, kc])
                        cols.append(((A, cl, m, b), z, C_R >= 10))
                dc = [j for j in range(5) if d["rand"]["dik"].get(j) is not None]
                if dc:
                    mu = [statistics.mean(d["rand"]["dik"][j]) for j in dc]
                    X = gen_counts(gen, rng, mu, (R, 4), cl, m, b, des)
                    kc = [dc.index(j) for j in d["kept"]["dickson"]]
                    if kc:
                        z, C_R, _ = zstat(X[:, 0, kc], X[:, 1:4, :][:, :, kc])
                        cols.append((("dickson", cl, m, b), z, C_R >= 10))
                    else:
                        cols.append((("dickson", cl, m, b), None, None))
    return cols


def main():
    des = Design()
    out = {"R": R, "generators": {}, "design_notes": {
        "mult_source": {f"{k[0]}|{k[1]}|{k[2]}": {"source_rung": v["source_rung"], "scale": round(v["scale"], 4),
                                                   "n_inst": v["n_inst"],
                                                   "E_B": round(sum(int(a) * c for a, c in v["hist"].items()) / sum(v["hist"].values()), 4),
                                                   "D_B": round(sum(int(a) ** 2 * c for a, c in v["hist"].items()) / sum(int(a) * c for a, c in v["hist"].items()), 4),
                                                   "max_B": max(int(a) for a in v["hist"])}
                        for k, v in sorted(des.mult.items())},
        "phi_relation_frailty": {f"{k[0]}|{k[1]}|{k[2]}": round(v, 5) for k, v in sorted(des.phi.items())},
        "D_pair_dispersion": {f"{k[0]}|{k[1]}|{k[2]}": round(v, 4) for k, v in sorted(des.D.items())}}}
    for gi, gen in enumerate(GENS):
        t0 = time.time()
        rng = np.random.default_rng(20260929 + gi)
        cols = simulate(des, gen, rng, R)
        exc = np.zeros(R, dtype=int)
        pos = np.zeros(R, dtype=int)
        maxz = np.zeros(R)
        per = {}
        for key, z, res in cols:
            k = "|".join(map(str, key))
            if z is None:
                per[k] = {"kept_curves": 0}
                continue
            res = res & ~np.isnan(z)
            za = np.where(res, z, 0.0)
            e = res & (np.abs(za) > 3)
            exc += e
            pos += res & (za > 3)
            maxz = np.maximum(maxz, np.abs(za))
            pr = float(res.mean())
            per[k] = {"P_resolved": round(pr, 5),
                      "P_absz_gt3_given_resolved": round(float(e.sum() / max(1, res.sum())), 6),
                      "P_z_gt3": round(float((res & (za > 3)).mean()), 6),
                      "P_z_lt_m3": round(float((res & (za < -3)).mean()), 6)}
        hist = np.bincount(exc, minlength=12)
        g = {"per_cell": per,
             "excursion_count_hist": hist.tolist(),
             "E_excursions": round(float(exc.mean()), 4),
             "P_ge_4": round(float((exc >= 4).mean()), 5),
             "P_ge_4_all_positive": round(float(((exc >= 4) & (pos == exc)).mean()), 5),
             "P_ge_1": round(float((exc >= 1).mean()), 5),
             "P_max_absz_ge_4p75": round(float((maxz >= 4.7515).mean()), 5),
             "P_count_ge4_MCse": round(float(np.sqrt((exc >= 4).mean() * (1 - (exc >= 4).mean()) / R)), 5),
             "mean_P_absz_gt3_given_resolved": round(float(np.mean([v["P_absz_gt3_given_resolved"] for v in per.values() if "P_absz_gt3_given_resolved" in v])), 6),
             "seconds": round(time.time() - t0, 1)}
        out["generators"][gen] = g
        print(gen, "E=", g["E_excursions"], "P>=4", g["P_ge_4"], "P>=4 allpos", g["P_ge_4_all_positive"],
              "P max>=4.75", g["P_max_absz_ge_4p75"], "mean per-cell tail", g["mean_P_absz_gt3_given_resolved"],
              "sec", g["seconds"], file=sys.stderr)
    with open(os.path.join(OUT, "out", "04_j6_family_null.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
