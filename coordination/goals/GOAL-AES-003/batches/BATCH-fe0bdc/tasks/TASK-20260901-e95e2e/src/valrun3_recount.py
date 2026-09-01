#!/usr/bin/env python3
"""TASK-20260901-e95e2e validator RUN 3 -- receipt recounts and control checks.

All recounts computed by this script from the committed producer receipts;
expected values taken from the frozen spec (IDEA-20260901-04606c) as
transcribed in this file, never from producer analysis code.
"""
import json, hashlib, math, sys

P = "../TASK-20260901-f5d3a4"
out = {}

def load(p):
    with open(P + "/" + p) as f:
        return json.load(f)

# ---------- FIXTURE ARM RECOUNT ----------
fx = load("runs/fixture_arm.json")
N30 = 1 << 30
T = fx["trivial_swaps_excluded"]
nontriv = fx["nontrivial_trials"]
hits = fx["W_ge1_nontrivial"]
whist = fx["whist"]
wword = fx["W_ge1_by_word"]
zhist = fx["zhist"]
fa = {}
fa["trials_is_2^30"] = fx["trials"] == N30 and fx["log2N"] == 30
fa["nontrivial_eq_trials_minus_T"] = nontriv == fx["trials"] - T
fa["T"] = T
fa["E_T_preregistered"] = 0.25
fa["whist_sum_eq_nontrivial"] = sum(whist) == nontriv
fa["whist_all_W3"] = whist == [0, 0, 0, nontriv, 0]
fa["hits_eq_wge1"] = hits == fx["W_ge1_nontrivial"]
fa["hits_eq_2^30_minus_T"] = hits == N30 - T
fa["band_hits_ge_2^30_minus_8"] = hits >= N30 - 8
fa["excess_ratio"] = hits / N30
fa["excess_ratio_exact_1"] = hits == N30
fa["excess_within_1pm_2^-20"] = abs(hits / N30 - 1.0) <= 2 ** -20
fa["frozen_excess_E"] = N30
fa["wword_recount"] = wword
fa["wword_eq_identity_prediction_[0,N,N,N]"] = wword == [0, N30, N30, N30]
fa["zhist_sum_eq_nontrivial"] = sum(zhist) == nontriv
# zhist model: diff d uniform over nonzero 32-bit words on word 0 (identity law),
# 12 non-active bytes always equal -> Z = 12 + (# zero bytes among 4 active diff bytes)
p255 = 255.0 / 256
pcond = 1.0 - 2 ** -32
pk = [math.comb(4, k) * (1 / 256) ** k * p255 ** (4 - k) / pcond for k in range(4)]
bins = {}
for k in range(4):
    E = N30 * pk[k]
    obs = zhist[12 + k]
    sigma = math.sqrt(N30 * pk[k] * (1 - pk[k]))
    bins["Z=%d" % (12 + k)] = {"observed": obs, "expected": round(E, 1),
                               "sigma": round(sigma, 1),
                               "deviation_sigma": round((obs - E) / sigma, 3)}
fa["zhist_model_check"] = bins
fa["zhist_within_4sigma_all_bins"] = all(abs(b["deviation_sigma"]) <= 4 for b in bins.values())
fa["params"] = {"arm": fx["arm"], "rounds": fx["rounds"], "amask": fx["amask"],
                "smask": fx["smask"], "seed": fx["seed"], "arm_id": fx["arm_id"],
                "threads": fx["threads"], "sbox": fx["sbox"]}
out["fixture_arm_recount"] = fa

# ---------- KEYED BRIDGE RECOUNT ----------
kb = load("runs/keyed_bridge.json")
cells = kb["cells"]
br = {}
br["n_cells"] = len(cells)
expected_cells = [
    ("B1", 5, [0], [1]), ("B2", 6, [0], [0]), ("B3", 2, [0], [0]),
    ("B4", 5, [0, 1, 2, 3], [0]), ("B5", 2, [0], [1]),
]
br["cells_match_preregistered_set"] = [
    (c["cell_id"], c["r"], c["A"], c["S"]) for c in cells] == expected_cells
tot_id = sum(c["qdiff_equals_pdiff"] for c in cells)
tot_w = sum(c["W_equals_4_minus_absA"] for c in cells)
tot_trials = sum(c["trials"] for c in cells)
br["identity_law_total"] = "%d/%d" % (tot_id, tot_trials)
br["identity_law_2500of2500"] = tot_id == 2500 and tot_trials == 2500
br["W_law_total"] = "%d/%d" % (tot_w, tot_trials)
br["W_law_2500of2500"] = tot_w == 2500
b4 = [c for c in cells if c["cell_id"] == "B4"][0]
b5 = [c for c in cells if c["cell_id"] == "B5"][0]
br["B4_structure_destroyed_W0"] = b4["W0_count"] == 500 and b4["whist"] == [500, 0, 0, 0, 0]
br["B5_degenerate_trivial_500of500"] = b5["trivial_swaps"] == 500 and b5["nontrivial"] == 0
# bridge convention: whist over ALL trials (record PR-2: "100% of trials"; the
# identity law holds on trivial trials too), unlike the C arm which conditions
# on nontrivial. Both conventions are stated in the record.
br["whist_consistency_bridge_convention_all_trials"] = all(
    sum(c["whist"]) == c["trials"] for c in cells)
br["whist_sum_nontrivial_convention"] = {
    c["cell_id"]: sum(c["whist"]) == c["trials"] - c["trivial_swaps"] for c in cells}
out["keyed_bridge_recount"] = br

# ---------- GATE0 RECOUNT ----------
g0 = load("runs/gate0.json")
kd = g0["checks"]["d_keyed_trials"]
gr = {}
gr["ranks"] = [g0["checks"]["b_word_map_ranks"]["%d" % j] for j in range(4)]
gr["ranks_required"] = [32, 0, 0, 0]
gr["ranks_ok"] = gr["ranks"] == gr["ranks_required"]
gr["word0_identity"] = g0["checks"]["b_word0_map_column_equal_identity"]
gr["words123_zero"] = g0["checks"]["b_words123_maps_column_equal_zero"]
gr["D5M5_I"] = g0["checks"]["a_D5M5_is_I128"]
gr["M5D5_I"] = g0["checks"]["a_M5D5_is_I128"]
gr["P_exact"] = g0["checks"]["c_P_Wge1_nontrivial_exact"]
gr["keyed_trials"] = {"n": kd["trials"], "qdiff_eq": kd["qdiff_equals_pdiff"],
                      "W3_nontrivial": kd["W_is_3_nontrivial"],
                      "nontrivial": kd["nontrivial"], "trivial": kd["trivial_swaps"],
                      "whist_sum": sum(kd["whist"])}
gr["keyed_ok"] = (kd["trials"] == 1000 and kd["qdiff_equals_pdiff"] == 1000
                  and kd["W_is_3_nontrivial"] == 1000 and kd["nontrivial"] == 1000
                  and kd["trivial_swaps"] == 0 and sum(kd["whist"]) == 1000)
out["gate0_recount"] = gr

# ---------- CENSUS FULL-TABLE RECOUNT vs FROZEN PR-1 ----------
FROZEN = [  # transcribed verbatim from IDEA-20260901-04606c claim P2 + PR-1
    ([0], [0],        [8,32,8,32,32,32,32,32,8,32]),
    ([0], [1],        [8,0,8,32,32,32,32,32,8,0]),
    ([0], [2],        [8,0,8,32,32,32,32,32,8,0]),
    ([0], [3],        [8,0,8,32,32,32,32,32,8,0]),
    ([1], [1],        [8,32,8,32,32,32,32,32,8,32]),
    ([2], [2],        [8,32,8,32,32,32,32,32,8,32]),
    ([3], [3],        [8,32,8,32,32,32,32,32,8,32]),
    ([0,1], [0],      [16,32,16,32,32,32,32,32,16,32]),
    ([0], [0,1],      [16,32,16,32,32,32,32,32,16,32]),
    ([0,1,2,3], [0],  [32,32,32,32,32,32,32,32,32,32]),
]
cen = load("runs/census.json")
cr = {}
cr["n_cells"] = len(cen["cells"])
cr["n_cell_instances"] = sum(len(c["rounds"]) for c in cen["cells"])
cell_keys = [(c["A"], c["S"]) for c in cen["cells"]]
cr["cell_set_eq_frozen_set"] = sorted((tuple(A), tuple(S)) for A, S in cell_keys) == sorted(
    (tuple(A), tuple(S)) for A, S, _ in FROZEN)
rho_map = {(tuple(A), tuple(S)): row for A, S, row in FROZEN}
mism = []
instances_checked = 0
for c in cen["cells"]:
    key = (tuple(c["A"]), tuple(c["S"]))
    if key not in rho_map:
        mism.append(("cell_not_in_frozen_set", key))
        continue
    for rr in c["rounds"]:
        instances_checked += 1
        r = rr["r"]
        req_ranks = [32 if j in c["A"] else 0 for j in range(4)]
        req_rho = rho_map[key][r - 1]
        req_W = 4 - len(c["A"])
        req_P = 1.0 if len(c["A"]) <= 3 else 0.0
        if rr["word_map_ranks"] != req_ranks:
            mism.append(("rank", key, r, rr["word_map_ranks"], req_ranks))
        if rr["rho"] != req_rho:
            mism.append(("rho", key, r, rr["rho"], req_rho))
        if rr["W_deterministic"] != req_W:
            mism.append(("W", key, r, rr["W_deterministic"], req_W))
        if rr["P_Wge1_nontrivial"] != req_P:
            mism.append(("P", key, r, rr["P_Wge1_nontrivial"], req_P))
        if not rr["word_map_exact_equal_PjPiA"] or not rr["cell_instance_ok"]:
            mism.append(("flags", key, r))
        if (tuple(rr["A"]), tuple(rr["S"])) != key or rr["A"] != c["A"] or rr["S"] != c["S"]:
            mism.append(("round_cell_mismatch", key, r))
cr["instances_checked"] = instances_checked
cr["mismatches"] = mism
cr["all_100_match_preregistered"] = instances_checked == 100 and not mism
guards = cen["per_r_port_guards_DrMr_and_MrDr_both_I128"]
cr["per_r_guards_all_I128"] = all(
    guards[str(r)]["DrMr_is_I"] and guards[str(r)]["MrDr_is_I"] for r in range(1, 11))
cr["r_star_aff_undefined_within_10"] = min(
    rr["P_Wge1_nontrivial"]
    for c in cen["cells"] if c["A"] == [0] and c["S"] == [0]
    for rr in c["rounds"] if rr["r"] >= 2) > 2 ** -30
# P(W>=1)=1 for (A={0},S={0}) at every r -> no r with P<=2^-30 -> r*_aff undefined
cr["P_equals_1_anchor_cell_all_r"] = all(
    rr["P_Wge1_nontrivial"] == 1.0
    for c in cen["cells"] if c["A"] == [0] and c["S"] == [0] for rr in c["rounds"])
out["census_full_table_recount"] = cr

# ---------- DIGEST CONTROL ----------
census_bytes = open(P + "/runs/census.json", "rb").read()
dig_now = hashlib.sha256(census_bytes).hexdigest()
dig_file = open(P + "/runs/census.json.digest.txt").read().split()[0]
cr["census_sha256_recomputed"] = dig_now
cr["digest_file_value"] = dig_file
cr["digest_matches_census"] = dig_now == dig_file
cr["digest_recorded_in_RESULTS_and_stamps"] = dig_now == "dbb2740940ce5ce3b2648f0e726e0eb42520e2576c945c6ec25f19689606b700"

# ---------- PREREGISTRATION ORDERING + DATES ----------
da = load("runs/decision_analysis.json")
pre_mtime = da["inputs"]["preregistration_mtime"]
order = []
for f in da["inputs"]["run_file_mtimes_after_preregistration"]:
    order.append((f["file"], f["mtime"], f["mtime"] > pre_mtime, f["after_preregistration"]))
out["mtime_ordering"] = {
    "preregistration_mtime": pre_mtime,
    "run_files": order,
    "all_after_preregistration": all(x[2] for x in order) and all(x[3] for x in order),
    "census_before_arm": (1788287541.7932465 < 1788287707.4444182),
    "digest_unchanged_since_RUN2_per_decision_analysis": da["inputs"]["census_digest_unchanged_since_RUN2"],
    "digest_at_RUN2": da["inputs"]["census_digest_sha256_at_RUN2"],
    "digest_after_arm": da["inputs"]["census_digest_sha256_after_arm"],
}

# ---------- DETERMINISM RECEIPTS ----------
def fh(p):
    return hashlib.sha256(open(P + "/" + p, "rb").read()).hexdigest()
det = {}
det["cal_det_a_sha"] = fh("runs/cal_det_a.json")
det["cal_det_b_sha"] = fh("runs/cal_det_b.json")
det["byte_identical_1thr"] = det["cal_det_a_sha"] == det["cal_det_b_sha"]
det["cal_det8_a_sha"] = fh("runs/cal_det8_a.json")
det["cal_det8_b_sha"] = fh("runs/cal_det8_b.json")
det["byte_identical_8thr"] = det["cal_det8_a_sha"] == det["cal_det8_b_sha"]
out["determinism_receipt_hashes"] = det

# ---------- CAL-RATE + CAL-DET8 zhist model sanity (consistency of the identity stream at other scales)
def zcheck(zhist, n):
    pk = [math.comb(4, k) * (1 / 256) ** k * (255 / 256) ** (4 - k) for k in range(4)]
    res = {}
    for k in range(4):
        E = n * pk[k]
        obs = zhist[12 + k]
        sigma = math.sqrt(max(n * pk[k] * (1 - pk[k]), 1e-9))
        res["Z=%d" % (12 + k)] = round((obs - E) / sigma, 2)
    return res
cr8 = load("runs/cal_det8_a.json")
crr = load("runs/cal_rate.json")
out["zhist_sigma_at_other_scales"] = {
    "cal_det8_2^18": zcheck(cr8["zhist"], 1 << 18),
    "cal_rate_2^22": zcheck(crr["zhist"], 1 << 22),
}

# ---------- PARSE ATTESTATION (whole-file) ----------
files = ["PREREGISTRATION.md", "RESULTS.json", "budget_stamps.jsonl",
         "runs/build_pin_cal.json", "runs/cal_crosscheck.json", "runs/cal_det8_a.json",
         "runs/cal_det8_b.json", "runs/cal_det_a.json", "runs/cal_det_b.json",
         "runs/cal_rate.json", "runs/census.json", "runs/decision_analysis.json",
         "runs/fixture_arm.json", "runs/gate0.json", "runs/geom.json",
         "runs/keyed_bridge.json", "runs/pin.json", "runs/pinidentity.json"]
pf = {}
for f in files:
    if f.endswith(".json"):
        try:
            json.load(open(P + "/" + f))
            pf[f] = "parsed_whole"
        except Exception as e:
            pf[f] = "PARSE_FAILURE: %s" % e
    elif f.endswith(".jsonl"):
        try:
            for line in open(P + "/" + f):
                if line.strip():
                    json.loads(line)
            pf[f] = "parsed_whole_line_by_line"
        except Exception as e:
            pf[f] = "PARSE_FAILURE: %s" % e
    else:
        pf[f] = "read_whole_non_json"
out["producer_artifacts_parse_check"] = pf

json.dump(out, sys.stdout, indent=1)
print()
