"""J-PLANT: planted-target construction and recovery, PC-R-T, PC-R-D, detection at kappa 1.15.
TASK-20261009-bfdc5b. Inputs: design.json, the scratch counts and recount (recount_cc1.py),
j_cal.json (t_dec), bank A (j_cal.py). Seeds: fixed-excess power SeedSequence([0xBFDC5B, 11]).
"""
import json
import random
import sys
import numpy as np
sys.path.insert(0, sys.argv[1])
import common as C
import bounds as B

OUT = sys.argv[2]
cal = json.load(open(sys.argv[3]))
t_dec = cal["t_dec"]
ROOT = "experiments/EXP-PFDR-0b3699/runs"
design = json.load(open(f"{ROOT}/RUN-PFDR-0b3699-p0-design/design.json"))
curves = design["curves"]
d = C.load()
rc = np.load(f"{C.SCR}/recount.npz")
present = rc["planted_present"]
n_b = design["final_n_b"]

# S and K_plant from the declared rule
mu_b = {30: 521.3333333333334 / 2000, 32: 513.6666666666666 / 2000}
S_re, K_re = {}, {}
for b in C.RUNGS:
    cb = [c["curve"] for c in curves if c["bits"] == b]
    K_re[b] = round(0.15 * n_b * mu_b[b])
    S_re[b] = random.Random(f"plant-target|EXP-PFDR-0b3699|{b}").sample(cb, n_b)[:K_re[b]]
S_eq = {b: sorted(S_re[b]) == design["S"][str(b)] for b in C.RUNGS}  # design.json stores S sorted
K_eq = {b: K_re[b] == design["K_plant_b"][str(b)] for b in C.RUNGS}
inS = np.array([c["curve"] in set(design["S"][str(c["bits"])]) for c in curves])

ps = d["cnt_planted_sub"]
pt = ps - ((~inS) & present).astype(np.int64)
nonplant = ps - present.astype(np.int64)
r0, r1, r2 = d["cnt_random_sub_r0"], d["cnt_random_sub_r1"], d["cnt_random_sub_r2"]
K_total = sum(design["K_plant_b"][str(b)] for b in C.RUNGS)


def cell(x, sel=None):
    if sel is None:
        sel = np.ones(len(x), bool)
    return C.cc8(x[sel], r0[sel], r1[sel], r2[sel])


res_pt = cell(pt)
res_ps = cell(ps)
res_np = cell(nonplant)
pcrt_ii = abs((res_pt["C_A"] - res_pt["C_R"]) - K_total) <= 4 * res_pt["SD_null"]
per_rung = {}
for b in C.RUNGS:
    s = d["bits"] == b
    a = cell(pt, s)
    per_rung[b] = {"planted_target": a, "planted_sub": cell(ps, s), "planted_sub_nonplanted": cell(nonplant, s),
                   "K_plant": design["K_plant_b"][str(b)],
                   "excess_minus_K_in_SD": (a["C_A"] - a["C_R"] - design["K_plant_b"][str(b)]) / a["SD_null"]}
# per-curve: planted_target minus planted_sub on S is 0; outside S exactly -1
diff = ps - pt
chk = {"S_curves_diff_zero": int((diff[inS] == 0).sum()), "S_curves": int(inS.sum()),
       "nonS_curves_diff_one": int((diff[~inS] == 1).sum()), "nonS_curves": int((~inS).sum())}
# non-planted counts vs randoms, per-curve histogram
hist_np = np.bincount(nonplant, minlength=6).tolist()
hist_R = (np.bincount(r0, minlength=6) + np.bincount(r1, minlength=6) + np.bincount(r2, minlength=6)).tolist()
# non-planted count on S vs off S (does the excess sit on S?)
onS = {"nonplanted_on_S": int(nonplant[inS].sum()), "C_R_on_S": float((r0[inS].sum() + r1[inS].sum() + r2[inS].sum()) / 3),
       "nonplanted_off_S": int(nonplant[~inS].sum()), "C_R_off_S": float((r0[~inS].sum() + r1[~inS].sum() + r2[~inS].sum()) / 3)}

# detection probability of the actual construction (exactly K_total added) and of kappa 1.15
fit = C.fit_gnbr(d)
model = C.Model(d, fit)
CRa = np.load(f"{C.SCR}/bank_CR.npy")
Va = np.load(f"{C.SCR}/bank_V.npy")
rng = np.random.default_rng(np.random.SeedSequence([C.REVIEW_TOKEN, 11]))
CA = model.null_total(rng, CRa.shape).astype(float) + K_total
p_fixed = float((C.z_from(CA, CRa, Va) > t_dec).mean())
kappa_eff = 1 + K_total / model.M
res = {"task": "TASK-20261009-bfdc5b", "joint": "J-PLANT", "t_dec": t_dec,
       "S_recomputed_equal": S_eq, "K_plant_recomputed": K_re, "K_plant_equal": K_eq, "K_total": K_total,
       "planted_vector_present_all": bool(present.all()), "planted_target_construction_check": chk,
       "planted_target": res_pt, "planted_sub": res_ps, "planted_sub_nonplanted": res_np,
       "excess_planted_target": res_pt["C_A"] - res_pt["C_R"],
       "excess_minus_K_in_SD": (res_pt["C_A"] - res_pt["C_R"] - K_total) / res_pt["SD_null"],
       "PC-R-T": {"i_z_gt_t_dec": bool(res_pt["z"] > t_dec), "ii_within_4SD": bool(pcrt_ii)},
       "PC-R-D": {"z_gt_t_dec": bool(res_ps["z"] > t_dec)},
       "per_rung": {str(b): v for b, v in per_rung.items()},
       "hist_nonplanted": hist_np, "hist_randoms_sum_of_3": hist_R, "S_split": onS,
       "detection_fixed_K_total": {"p": p_fixed, "mc_se": float(np.sqrt(p_fixed * (1 - p_fixed) / len(CRa))),
                                   "replicates": len(CRa), "kappa_equivalent": kappa_eff}}
C.jdump(res, OUT)
print(json.dumps(res, indent=1, default=str)[:6000])
