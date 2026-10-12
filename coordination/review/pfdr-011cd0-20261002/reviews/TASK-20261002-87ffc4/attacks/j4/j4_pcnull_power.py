"""J4 (b)/(c): does PC-NULL measure anything? Power of the frozen PC-NULL rule against a
known-null arm that is NOT distributed as the calibrated null: (a) more dispersed than the
randoms (arm dispersion rho x D, rho in {1, 1.5, 2, 3}); (b) a mean excess kappa_kn in
{1.03, 1.05, 1.10}. Each alternative: 400 synthetic experiments from this reviewer's generator at
the realised design (98 per-rung groups; the 14 band cells pool the 30 and 32 rungs), PC-NULL
(i) with the producer's t* and P(K_null >= K) taken from the null K law of attacks/j4 (computed
here from the alternative rho = 1, kappa = 1 run), (ii) KS of the 98 per-rung z against the pooled
generator null with the asymptotic (Stephens) p at 1%.
Seed: SeedSequence([0x87ffc4, 60, alternative_index]).
Command: nice -n 19 $PY attacks/j4/j4_pcnull_power.py --npz <scratch>/null-z.npz --out attacks/j4/out/pcnull_power.json
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import j4lib as L  # noqa: E402

T_PROD = 2.848862284470068


def sim_alt(rng, groups, rho, kap, B):
    zb = []
    zr = []
    band_parts = {}
    for (cls, m) in L.FAM1_CM:
        for fam in ("SUB", "DICK"):
            for b in L.RUNGS:
                g = groups[(fam, cls, m, b)]
                n = len(g.curves)
                X = L.draw(rng, g.mj, g.D, (B, 3, n))
                CR = X.mean(axis=1).sum(axis=1)
                Q = X.var(axis=1, ddof=1).sum(axis=1)
                DA = max(g.D * rho, 1.0)
                A = L.draw(rng, kap * g.M, DA, (B,)) if g.M > 0 else np.zeros(B)
                zr.append(L.zvec(A, CR, Q))
                if b in L.BAND:
                    band_parts.setdefault((fam, cls, m), []).append((A, CR, Q))
    for k, parts in band_parts.items():
        A = sum(p[0] for p in parts)
        CR = sum(p[1] for p in parts)
        Q = sum(p[2] for p in parts)
        zb.append(L.zvec(A, CR, Q))
    return np.vstack(zb), np.vstack(zr)  # (14, B), (98, B)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--npz", required=True)
    ap.add_argument("--B", type=int, default=400)
    a = ap.parse_args()
    design = L.load_design()
    rows = L.load_extract()
    groups, _, _ = L.build_groups(rows, design)
    nz = np.load(a.npz)
    ref = np.sort(np.concatenate([nz[k] for k in nz.files if k.startswith("rung|")]))
    alts = [(1.0, 1.0), (1.5, 1.0), (2.0, 1.0), (3.0, 1.0), (1.0, 1.03), (1.0, 1.05), (1.0, 1.10)]
    out = {"B": a.B, "t_star": T_PROD, "alternatives": []}
    Knull = None
    for ai, (rho, kap) in enumerate(alts):
        rng = np.random.default_rng(np.random.SeedSequence([0x87FFC4, 60, ai]))
        zb, zr = sim_alt(rng, groups, rho, kap, a.B)
        K = np.sum(zb > T_PROD, axis=0)
        if ai == 0:
            Knull = K
        pK = np.array([np.mean(Knull >= k) for k in K])
        fail_i = pK < 0.01
        ks_p = np.array([L.kolmogorov_sf(L.ks_D_against(zr[:, j], ref), zr.shape[0]) for j in range(a.B)])
        fail_ii = ks_p < 0.01
        rec = {"rho_arm_dispersion": rho, "kappa_known_null": kap,
               "P_fail_i": float(np.mean(fail_i)), "P_fail_ii": float(np.mean(fail_ii)),
               "P_PC_NULL_fails": float(np.mean(fail_i | fail_ii)), "mean_K": float(K.mean()),
               "band_z_sd": float(zb.std()), "band_z_mean": float(zb.mean())}
        out["alternatives"].append(rec)
        print(rec, flush=True)
    out["note"] = ("the rho = 1, kappa = 1 row is the null (its P_PC_NULL_fails is the size); K_null for (i) is "
                   "that row's own K sample (400 draws), so (i) is coarse at this B")
    L.jdump(a.out, out)


if __name__ == "__main__":
    main()
