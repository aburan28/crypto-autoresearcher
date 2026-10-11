"""J-PTM: the proves-too-much control. The full decision argument (z against t_dec, the
governing bound by AR-3 with its coverage, X_rel, the frozen outcome table) run with each
of the five known-answer objects in the structured arm's place, plus planted_sub (dynamic
range) and small_x (reference). TASK-20261009-bfdc5b.
Bounds at each object's kappa_hat: bank A (j_cal.py) with struct draws
SeedSequence([0xBFDC5B, 5, 1000 + object_index, f]).
Failure signature (c) joint law: pc_z_bank.npy (5 x 20000).
"""
import json
import sys
import numpy as np
sys.path.insert(0, sys.argv[1])
import common as C
import bounds as B

OUT = sys.argv[2]
cal = json.load(open(sys.argv[3]))
cov = json.load(open(sys.argv[4]))
plant = json.load(open(sys.argv[5]))
t_dec = cal["t_dec"]
t_Delta = cal["t_Delta"]["mean"]
d = C.load()
fit = C.fit_gnbr(d)
model = C.Model(d, fit)
CRa = np.load(f"{C.SCR}/bank_CR.npy")
Va = np.load(f"{C.SCR}/bank_V.npy")
bA = B.Bounds(model, CRa, Va, 5, seed_tag=5)
bA._q_lo = np.load(f"{C.SCR}/grid_qlo_A.npy")
bA._q_abs = np.load(f"{C.SCR}/grid_qabs_A.npy")
gov = cov["AR3"]["bank_A"]["pooled_12000"]["governing"]
cov_signed = cov["AR3"]["bank_A"]["pooled_12000"]["signed_coverages"]
xr = cov["X_rel"]["reported"]
xr_num = xr if isinstance(xr, float) else 99.0

rc = np.load(f"{C.SCR}/recount.npz")
design = json.load(open("experiments/EXP-PFDR-0b3699/runs/RUN-PFDR-0b3699-p0-design/design.json"))
inS = np.array([c["curve"] in set(design["S"][str(c["bits"])]) for c in design["curves"]])
pt = d["cnt_planted_sub"] - ((~inS) & rc["planted_present"]).astype(np.int64)
r = {a: d[f"cnt_{a}"] for a in C.NULLS}
M = d["cnt_small_x_offset"]
objects = [
    ("random_sub_r0", r["random_sub_r0"], (r["random_sub_r1"], r["random_sub_r2"], r["known_null_sub"])),
    ("random_sub_r1", r["random_sub_r1"], (r["random_sub_r0"], r["random_sub_r2"], r["known_null_sub"])),
    ("random_sub_r2", r["random_sub_r2"], (r["random_sub_r0"], r["random_sub_r1"], r["known_null_sub"])),
    ("known_null_sub", r["known_null_sub"], (r["random_sub_r0"], r["random_sub_r1"], r["random_sub_r2"])),
    ("planted_target", pt, (r["random_sub_r0"], r["random_sub_r1"], r["random_sub_r2"])),
    ("planted_sub (dynamic range)", d["cnt_planted_sub"], (r["random_sub_r0"], r["random_sub_r1"], r["random_sub_r2"])),
    ("small_x (reference)", d["cnt_small_x"], (r["random_sub_r0"], r["random_sub_r1"], r["random_sub_r2"])),
]
rows = []
for oi, (name, X, trip) in enumerate(objects):
    c = C.cc8(X, *trip)
    if c["kappa_rel"] < 1.40:
        bd = bA.observed(c["kappa_rel"], c["SE"], oi)
    else:  # far outside the grid: direct simulation is still exact (no interpolation used)
        bd = bA.observed(c["kappa_rel"], c["SE"], oi)
    U_gov = bd["U_signed"] if gov == "signed" else bd["U_absdev"]
    kb = {}
    for b in C.RUNGS:
        s = d["bits"] == b
        kb[b] = C.cc8(X[s], *(t[s] for t in trip))["kappa_rel"]
    # mutation and contrast as the frozen table reads them (M vs the object's own triple)
    cM = C.cc8(M, *trip)
    zD = (c["C_A"] - M.sum()) / np.sqrt(2 * c["V"])
    if c["z"] > t_dec:
        if cM["z"] > t_dec:
            outcome = "O-A2"
        elif kb[30] > 1 and kb[32] > 1 and zD > t_Delta:
            outcome = "O-A1"
        else:
            outcome = "O-A1b"
    else:
        outcome = "O-A3" if (U_gov <= 1.15 and xr_num <= 1.15) else "O-A4"
    rows.append({"object": name, "C_X": c["C_A"], "C_R": c["C_R"], "three_C_R": c["three_C_R"], "V": c["V"],
                 "SD_null": c["SD_null"], "z": c["z"], "z_gt_t_dec": bool(c["z"] > t_dec), "kappa_hat": c["kappa_rel"],
                 "SE": c["SE"], "U_signed": bd["U_signed"], "U_signed_mc_se": bd["U_signed_mc_se"],
                 "U_absdev": bd["U_absdev"], "U_absdev_mc_se": bd["U_absdev_mc_se"], "governing": gov,
                 "U_governing": U_gov, "signed_coverages_1.00_1.10_1.15": cov_signed, "X_rel": xr,
                 "kappa_30": kb[30], "kappa_32": kb[32], "z_M_vs_same_triple": cM["z"], "z_Delta_vs_M": zD,
                 "outcome_by_frozen_table": outcome})
    print(rows[-1]["object"], rows[-1]["z"], rows[-1]["U_governing"], outcome, flush=True)

nulls = rows[:4]
K = sum(1 for x in nulls if x["z_gt_t_dec"])
bank = np.load(f"{C.SCR}/pc_z_bank.npy")
Kb = (bank > t_dec).sum(axis=1)
pK = float((Kb >= K).mean())
# (c) joint law of "governing bound below 1.00" over the four null cells, from the z bank:
# U < 1  <=>  z < q_lo(kappa_hat) (signed)  or  z < -q_abs(kappa_hat) (|dev|), kappa_hat = 1 + z SE
SEt = np.mean([x["SE"] for x in nulls])
kh_b = 1 + bank * SEt
if gov == "signed":
    below_b = bank < bA.q_lo(kh_b)
else:
    below_b = bank < -bA.q_abs(kh_b)
nb_b = below_b.sum(axis=1)
nb_obs = sum(1 for x in nulls if x["U_governing"] < 1.0)
p_c = float((nb_b >= nb_obs).mean())
pt_row = rows[4]
sig = {"a_planted_target_no_excess_bounded": bool((not pt_row["z_gt_t_dec"]) and pt_row["U_governing"] <= 1.15),
       "b_null_K": K, "b_P_Knull_ge_K": pK, "b_met": bool(pK < 0.01),
       "c_null_bounds_below_1": nb_obs, "c_P_ge_observed_joint": p_c,
       "c_expected_below_1_per_cell": float(below_b.mean()),
       "c_met": bool(p_c < 0.01), "replicates_joint_law": len(Kb)}
sig["failure_signature_met_any"] = bool(sig["a_planted_target_no_excess_bounded"] or sig["b_met"] or sig["c_met"])
res = {"task": "TASK-20261009-bfdc5b", "joint": "J-PTM", "t_dec": t_dec, "t_Delta": t_Delta,
       "governing_rule": gov, "table": rows, "failure_signature": sig}
C.jdump(res, OUT)
print(json.dumps(sig, indent=1))
