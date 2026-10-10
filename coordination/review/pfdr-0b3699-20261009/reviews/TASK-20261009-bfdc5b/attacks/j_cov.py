"""J-COV: both U_A bounds, their simulated coverages at kappa 1.00/1.10/1.15, the AR-3 choice
and its seed stability, compound-planting coverage, and X_rel under both plantings.
TASK-20261009-bfdc5b. Written from the text before analyze_a.py was opened.

Seeds:
  bank A (q grid)   = j_cal.py bank, SeedSequence([0xBFDC5B, 1, f]) r0..r2, 5 x 20000
  grid struct draws   SeedSequence([0xBFDC5B, 5, f]); observed bound [0xBFDC5B, 5, 1000, f]
  bank B (q grid)     SeedSequence([0xBFDC5B, 9, 0]) r0..r2, 5 x 20000; struct [0xBFDC5B, 10, f]
  coverage designs    SeedSequence([0xBFDC5B, 6, set, kappa_index]) sets 0..2, 4000 designs each
  compound coverage   SeedSequence([0xBFDC5B, 7, kappa_index]), 4000 designs
  X_rel / power       SeedSequence([0xBFDC5B, 8, planting_index]) on bank A
"""
import json
import sys
import numpy as np
sys.path.insert(0, sys.argv[1])
import common as C
import bounds as B

OUT = sys.argv[2]
cal = json.load(open(sys.argv[3]))
t_dec = cal["t_dec"]

d = C.load()
fit = C.fit_gnbr(d)
model = C.Model(d, fit)
obsA = C.cc8(d["cnt_small_x"], d["cnt_random_sub_r0"], d["cnt_random_sub_r1"], d["cnt_random_sub_r2"])
kh, SE = obsA["kappa_rel"], obsA["SE"]

CRa = np.load(f"{C.SCR}/bank_CR.npy")
Va = np.load(f"{C.SCR}/bank_V.npy")
bA = B.Bounds(model, CRa, Va, 5, seed_tag=5)
bA.build_grid()
np.save(f"{C.SCR}/grid_qlo_A.npy", bA._q_lo)
np.save(f"{C.SCR}/grid_qabs_A.npy", bA._q_abs)
obs_bound_A = bA.observed(kh, SE, 0)
print("observed bound (bank A)", obs_bound_A, flush=True)

# independent bank B for seed stability of the whole procedure
rngB = np.random.default_rng(np.random.SeedSequence([C.REVIEW_TOKEN, 9, 0]))
CRb, Vb = C.random_bank(model, rngB, 100000)
np.save(f"{C.SCR}/bankB_CR.npy", CRb)
np.save(f"{C.SCR}/bankB_V.npy", Vb)
bB = B.Bounds(model, CRb, Vb, 5, seed_tag=10)
bB.build_grid()
np.save(f"{C.SCR}/grid_qlo_B.npy", bB._q_lo)
np.save(f"{C.SCR}/grid_qabs_B.npy", bB._q_abs)
obs_bound_B = bB.observed(kh, SE, 0)
print("observed bound (bank B)", obs_bound_B, flush=True)

KAPPAS = (1.00, 1.10, 1.15)
cov = {"bank_A": {}, "bank_B": {}}
designs_store = {}
for s in range(3):
    for ki, k in enumerate(KAPPAS):
        rng = np.random.default_rng(np.random.SeedSequence([C.REVIEW_TOKEN, 6, s, ki]))
        khs, SEs, CRs, Vs, CAs = B.synthetic_designs(model, rng, 4000, k)
        designs_store[(s, ki)] = (khs, SEs)
        for name, bb in (("bank_A", bA), ("bank_B", bB)):
            cov[name][f"set{s}_kappa{k:.2f}"] = B.coverage(bb, khs, SEs, k)
    print("coverage set", s, {kk: v for kk, v in cov["bank_A"].items() if kk.startswith(f"set{s}")}, flush=True)

# pooled 12000 designs per kappa, and AR-3 per set
ar3 = {}
pooled = {}
for name, bb in (("bank_A", bA), ("bank_B", bB)):
    ar3[name] = {}
    for s in range(3):
        cs = [cov[name][f"set{s}_kappa{k:.2f}"]["coverage_signed"] for k in KAPPAS]
        ar3[name][f"set{s}"] = {"signed_coverages": cs, "governing": "signed" if min(cs) >= 0.945 else "absdev"}
    pooled[name] = {}
    for ki, k in enumerate(KAPPAS):
        khs = np.concatenate([designs_store[(s, ki)][0] for s in range(3)])
        SEs = np.concatenate([designs_store[(s, ki)][1] for s in range(3)])
        pooled[name][f"kappa{k:.2f}"] = B.coverage(bb, khs, SEs, k)
    cs = [pooled[name][f"kappa{k:.2f}"]["coverage_signed"] for k in KAPPAS]
    ar3[name]["pooled_12000"] = {"signed_coverages": cs, "governing": "signed" if min(cs) >= 0.945 else "absdev"}

# compound planting coverage (bounds still by the Poisson-planted rule)
comp = {}
for ki, k in enumerate((1.10, 1.15)):
    rng = np.random.default_rng(np.random.SeedSequence([C.REVIEW_TOKEN, 7, ki]))
    khs, SEs, *_ = B.synthetic_designs(model, rng, 4000, k, planting="compound")
    comp[f"kappa{k:.2f}"] = {"bank_A": B.coverage(bA, khs, SEs, k), "bank_B": B.coverage(bB, khs, SEs, k)}
print("compound coverage", comp, flush=True)

# X_rel and power at 1.15
xr = {}
for pi, planting in enumerate(("poisson", "compound")):
    rng = np.random.default_rng(np.random.SeedSequence([C.REVIEW_TOKEN, 8, pi]))
    x, pw = B.x_rel(model, CRa, Va, t_dec, rng, planting)
    p115 = B.power_at(model, CRa, Va, t_dec, rng, 1.15, planting)
    p110 = B.power_at(model, CRa, Va, t_dec, rng, 1.10, planting)
    xr[planting] = {"X_rel": x, "power_grid": pw, "power_at_1.15": p115, "power_at_1.10": p110}
xr["reported"] = max(xr["poisson"]["X_rel"], xr["compound"]["X_rel"]) if all(
    isinstance(xr[p]["X_rel"], float) for p in ("poisson", "compound")) else "X_rel > 1.30"

res = {"task": "TASK-20261009-bfdc5b", "joint": "J-COV", "t_dec_used": t_dec, "observed_small_x": obsA,
       "observed_bound_bank_A": obs_bound_A, "observed_bound_bank_B": obs_bound_B,
       "coverage": cov, "coverage_pooled": pooled, "AR3": ar3, "compound_coverage": comp, "X_rel": xr,
       "readings": "common.py RD-1..RD-7; bounds.py",
       "replicates": {"bank": "5 x 20000 per bank (A, B)", "designs": "4000 per kappa per set, 3 sets",
                      "compound": 4000, "X_rel": "100000 (bank A)"}}
C.jdump(res, OUT)
print(json.dumps({"obsA": obs_bound_A, "ar3": ar3, "xr": {k: (v["X_rel"] if isinstance(v, dict) else v) for k, v in xr.items()}}, default=str, indent=1))
