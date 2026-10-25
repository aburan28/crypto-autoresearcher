#!/usr/bin/env python3
"""Diff analysis/summary.json against the blind re-derivation."""
import json, sys
camp, mine_p = sys.argv[1], sys.argv[2]
mine = json.load(open(mine_p))
summ = json.load(open(f"{camp}/analysis/summary.json"))
mism, n = [], 0
def chk(tag, a, b, tol=1e-9):
    global n
    n += 1
    if a is None or b is None or abs(a - b) > tol * max(1, abs(b)):
        mism.append((tag, a, b))
for e in summ:
    s = e["curve_tag"]; d = mine[s]
    chk(f"{s} log2_r", d["curve"]["log2_r"], e["log2_r"])
    chk(f"{s} plan_over_rho", d["compare"]["rho-neg__plan"]["ratio"], e["plan_over_rho"]["ratio"])
    for i in (0, 1):
        chk(f"{s} plan_over_rho ci{i}", d["compare"]["rho-neg__plan"]["ci95"][i], e["plan_over_rho"]["ci95"][i])
        chk(f"{s} aa ci{i}", d["compare"]["plan__plan-aa"]["ci95"][i], e["aa"]["ci95"][i])
    chk(f"{s} aa", d["compare"]["plan__plan-aa"]["ratio"], e["aa"]["ratio"])
    for arm, v in e["mean_s"].items():
        for i in range(3):
            chk(f"{s} mean_s {arm} w#{i}", d["band"][arm]["mean_s"][i], v[i])
    for a in e["alternatives"]:
        c = d["compare"][f"plan__{a['arm']}"]
        chk(f"{s} {a['arm']} ops_ratio", c["ratio"], a["ops_ratio"])
        for i in (0, 1):
            chk(f"{s} {a['arm']} ci{i}", c["ci95"][i], a["ci95"][i])
        for i, p in enumerate(d["band_ratios"][a["arm"]]["per_weight"]):
            chk(f"{s} {a['arm']} band_ratio w={p['w']}", p["ratio_of_band_means"], a["band_ratio"][i])
        mylab = d["band_ratios"][a["arm"]]["protocol_label"]
        n += 1
        print(f"{s} {a['arm']:15s} producer verdict: {a['verdict']!r:35s} my protocol label (interval at every weight): {mylab}")
print(f"summary.json: checked {n}; mismatches {len(mism)}")
for m in mism: print("MISMATCH", m)
