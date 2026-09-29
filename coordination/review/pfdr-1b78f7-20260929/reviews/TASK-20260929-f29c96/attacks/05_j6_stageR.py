"""J6(b): Stage R -- null replication probability per excursion cell (same sign, |z| > 3,
five fresh curves 5..9 with their own random means), the family-wise probability over the
four cells, power against (i) the discovery kappa and (ii) Stage R's own kappa, the kappa
detectable with probability 0.5 and 0.8, and a one-sided 95% upper bound on kappa from the
observed Stage R z (test inversion under each generator).
Seeds: numpy default_rng(20261001 + k); null R = 200000, power/grid R = 20000.
Output: attacks/out/05_j6_stageR.json
"""
import json
import os
import statistics
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rtlib import EXCURSIONS, OUT, RANDOMS, usable  # noqa: E402
from j6design import Design, frozen_count, gen_counts, zstat  # noqa: E402

GENS = ["G-POIS", "G-NB", "G-CP", "G-RES"]
DISC = {("subgroup", "TT", 3, 28): (1.1971, 3.6601), ("small_x", "SS", 4, 20): (1.2502, 3.3898),
        ("dickson", "SS", 4, 26): (1.1003, 3.9451), ("subgroup", "TT", 5, 16): (4.4118, 4.7515)}
SROBS = {("subgroup", "TT", 3, 28): (1.021, 0.2985), ("small_x", "SS", 4, 20): (0.7493, -1.9888),
         ("dickson", "SS", 4, 26): (0.8843, -2.9591), ("subgroup", "TT", 5, 16): (0.7714, -0.4312)}


def sr_means(des, A, cl, m, b):
    mu = []
    for j in range(5, 10):
        rs = [des.sr.get(("main", m, b, j, a, "census")) for a in RANDOMS[A]]
        assert all(usable(r) for r in rs)
        mu.append(statistics.mean(frozen_count(r, cl) for r in rs))
    return mu


def zdist(des, gen, rng, mu, cl, m, b, kappa, R):
    X = gen_counts(gen, rng, mu, (R, 4), cl, m, b, des, kappa=[kappa, 1, 1, 1])
    z, C_R, _ = zstat(X[:, 0, :], X[:, 1:4, :])
    return np.where(C_R >= 10, z, np.nan)


def main():
    des = Design()
    out = {}
    for gi, gen in enumerate(GENS):
        rng = np.random.default_rng(20261001 + gi)
        g = {}
        pnull = []
        for (A, cl, m, b) in EXCURSIONS:
            mu = sr_means(des, A, cl, m, b)
            z0 = zdist(des, gen, rng, mu, cl, m, b, 1.0, 200000)
            p_rep = float(np.nanmean(np.where(np.isnan(z0), 0, z0 > 3)))
            p_res = float(np.mean(~np.isnan(z0)))
            pnull.append(p_rep)
            kd, _ = DISC[(A, cl, m, b)]
            ks, zs = SROBS[(A, cl, m, b)]
            pw = {}
            for lab, kap in (("kappa_discovery", kd), ("kappa_stageR", ks)):
                zz = zdist(des, gen, rng, mu, cl, m, b, kap, 20000)
                pw[lab] = {"kappa": kap, "P_z_gt3": round(float(np.mean(np.nan_to_num(zz, nan=-99) > 3)), 5)}
            grid = [round(1.0 + 0.02 * i, 2) for i in range(0, 201)]  # 1.00 .. 5.00
            p50 = p80 = None
            ub = None
            for kap in grid:
                zz = zdist(des, gen, rng, mu, cl, m, b, kap, 4000)
                zz2 = np.nan_to_num(zz, nan=-99)
                pp = float(np.mean(zz2 > 3))
                if p50 is None and pp >= 0.5:
                    p50 = kap
                if p80 is None and pp >= 0.8:
                    p80 = kap
                # one-sided upper bound: largest kappa with P(z <= z_obs | kappa) >= 0.05
                if float(np.mean(zz2 <= zs)) >= 0.05:
                    ub = kap
                if p80 is not None and float(np.mean(zz2 <= zs)) < 0.01:
                    break
            g["|".join(map(str, (A, cl, m, b)))] = {
                "stageR_random_means": [round(x, 2) for x in mu],
                "P_null_replication_same_sign": round(p_rep, 6),
                "P_null_resolved": round(p_res, 5),
                "power": pw, "kappa_detectable_P50": p50, "kappa_detectable_P80": p80,
                "kappa_upper95_from_stageR_z": ub, "stageR_observed": {"kappa": ks, "z": zs}}
        fw = 1.0
        for p in pnull:
            fw *= (1 - p)
        g["familywise_P_any_null_replication_4_cells"] = round(1 - fw, 6)
        out[gen] = g
        print(gen, json.dumps(g, indent=None)[:1500], file=sys.stderr)
    with open(os.path.join(OUT, "out", "05_j6_stageR.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
