"""J-DISP part 3 (rerun after j_disp.py stopped in its per-rung variant on a single-rung Model;
common.Model now accepts single-rung masks, unchanged for two-rung models).
Leave-top-10-curves-out and per-rung splits: z_A, kappa, the rung/subset t_A, the signed and
|dev| bounds (bank of 20000 = 5 families x 4000), power at kappa 1.15.
Seeds SeedSequence([0xBFDC5B, 15, v, f]) exactly as j_disp.py. TASK-20261009-bfdc5b.
"""
import json
import sys
import numpy as np
sys.path.insert(0, sys.argv[1])
import common as C
import bounds as B

OUT = sys.argv[2]
cal = json.load(open(sys.argv[3]))
t_perm = cal["t_perm"]["mean"]
d = C.load()
bits = d["bits"]
A = d["cnt_small_x"].astype(float)
R = np.vstack([d[f"cnt_random_sub_r{i}"] for i in range(3)]).astype(float)
nbar = R.mean(axis=0)
contrib = A - nbar
order = np.lexsort((d["curve"], bits, -contrib))
keep = np.ones(len(A), bool)
keep[order[:10]] = False
order2 = np.lexsort((d["curve"], bits, -nbar))
keep2 = np.ones(len(A), bool)
keep2[order2[:10]] = False
var = {}
for vi, (name, mask) in enumerate((("leave_top10_small_x_contrib_out", keep), ("leave_top10_null_mean_out", keep2),
                                   ("rung_30", bits == 30), ("rung_32", bits == 32))):
    c = C.cc8(A[mask], *(R[i][mask] for i in range(3)))
    fit_m = C.fit_gnbr(d, mask=mask) if name.startswith("leave") else C.fit_gnbr(d)
    mdl = C.Model(d, fit_m, mask=mask)
    rngs = [np.random.default_rng(np.random.SeedSequence([C.REVIEW_TOKEN, 15, vi, f])) for f in range(5)]
    CRv, Vv = C.random_bank(mdl, rngs[0], 20000)
    zz = C.z_from(mdl.null_total(rngs[1], 20000).astype(float), CRv, Vv)
    tA_v = float(np.quantile(zz, 0.99))
    bnd = B.Bounds(mdl, CRv, Vv, 5, seed_tag=15)
    qlo, qab, _, _ = bnd.quantiles_at(c["kappa_rel"], rngs)
    pw115 = B.power_at(mdl, CRv, Vv, max(tA_v, t_perm), rngs[2], 1.15, "poisson")
    var[name] = {"curves": int(mask.sum()),
                 "dropped": [(int(bits[i]), int(d["curve"][i])) for i in np.nonzero(~mask)[0]] if name.startswith("leave") else "other rung",
                 "C_A": c["C_A"], "C_R": c["C_R"], "z_A": c["z"], "kappa_hat": c["kappa_rel"], "SE": c["SE"],
                 "t_A_variant": tA_v, "t_dec_variant": max(tA_v, t_perm),
                 "U_signed": c["kappa_rel"] - qlo * c["SE"], "U_absdev": c["kappa_rel"] + qab * c["SE"],
                 "power_1.15": pw115, "replicates": "bank 20000 (5 families x 4000 for the bound); t_A 20000; power 20000"}
    print(name, json.dumps(var[name], default=float), flush=True)
C.jdump(var, OUT)
