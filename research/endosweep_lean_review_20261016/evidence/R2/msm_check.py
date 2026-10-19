"""R2: check msm.json rows against the Lean Pippenger definitions (windows, break-even iff)."""
import json, sys
d = json.load(open(sys.argv[1]))
def lean_windows(bits, c): return bits // c + 1          # Pippenger.windows
nrows = bad_w = bad_iff = bad_cs = bad_gain = bad_dbl = 0
for cv in d["curves"]:
    for r in cv["rows"]:
        nrows += 1
        N = r["N"]; ce = r["endo_per_point_M"]
        for k in ("plain", "glv_no_endo"):
            x = r[k]
            if x["windows"] != lean_windows(x["coeff_bits"], x["c"]): bad_w += 1
            if x["doublings"] != (x["windows"] - 1) * x["c"] or x["combine_adds"] != x["windows"] - 1: bad_dbl += 1
        P, G0 = r["plain"]["total_M"], r["glv_no_endo"]["total_M"]
        cs = (P - G0) / N
        if abs(cs - r["C_star_M"]) > 0.06: bad_cs += 1
        gt = G0 + N * ce
        if abs(gt - r["glv_total_M"]) > 0.2: print("glv_total mismatch", cv["curve"], r["mode"], N, gt, r["glv_total_M"])
        gain = 100 * (P - gt) / P
        if abs(gain - r["glv_gain_pct"]) > 0.01: bad_gain += 1
        # Lean glv_wins_iff / gain_pos_iff on the recorded numbers
        lhs = (r["glv_total_M"] < P); rhs = (ce < r["C_star_M"]); g = r["glv_gain_pct"] > 0
        if not (lhs == rhs == g): bad_iff += 1; print("iff disagreement (rounding?)", cv["curve"], r["mode"], N, r["glv_total_M"], P, ce, r["C_star_M"], r["glv_gain_pct"])
print(f"rows={nrows} windows_mismatch={bad_w} dbl/comb_mismatch={bad_dbl} cstar_mismatch={bad_cs} gain_mismatch={bad_gain} iff_disagreements={bad_iff}")
# README table: secp256k1 batched affine C*(N)
for cv in d["curves"]:
    if cv["curve"].lower().startswith("secp256k1"):
        for mode in ("batch_affine", "mixed"):
            print(cv["curve"], mode, [(r["logN"], r["C_star_M"], r["C_star_hypothesis_M"], r["plain"]["c"], r["glv_no_endo"]["c"], r["plain"]["windows"], r["glv_no_endo"]["windows"]) for r in cv["rows"] if r["mode"] == mode and r["logN"] % 2 == 0])
