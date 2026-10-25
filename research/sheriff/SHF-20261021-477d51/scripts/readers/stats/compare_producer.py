#!/usr/bin/env python3
"""Step 3: diff the blind re-derivation against the producer's ecbench outputs.

Reads (after the blind seal) sessions/<s>/comparisons/*.json,
analysis/table-<s>.txt, analysis/band-<s>.{json,txt}. Prints every value
with |mine - producer| beyond tolerance.

Usage: python3 -I compare_producer.py <campaign_dir> <rederive_out.json>
"""
import json
import re
import sys

camp, mine_p = sys.argv[1], sys.argv[2]
mine = json.load(open(mine_p))
TOL_EXACT = 1e-9  # comparisons JSON carries full floats
mism, checked = [], 0


def close(a, b, tol):
    if a is None or b is None:
        return a is None and b is None
    return abs(a - b) <= tol * max(1.0, abs(b))


for s, d in mine.items():
    # comparisons/*.json
    for key, c in d["compare"].items():
        p = json.load(open(f"{camp}/sessions/{s}/comparisons/{key}.json"))
        o = p["ops"]
        pairs = [("ratio", c["ratio"], o["ratio_b_over_a"]),
                 ("ci_lo", c["ci95"][0], o["ci95"][0]), ("ci_hi", c["ci95"][1], o["ci95"][1])]
        for nm, a, b in pairs:
            checked += 1
            if not close(a, b, TOL_EXACT):
                mism.append((s, f"comparisons/{key}.json ops.{nm}", a, b))
        for nm, a, b in (("pairs", c["pairs"], o["pairs"]), ("unpaired", c["unpaired"], o["unpaired_runs"]),
                         ("same_seeds", c["same_seeds"], o["same_seeds"]), ("ci_method", c["ci_method"], o["ci_method"]),
                         ("status", "ok", o["status"]), ("resamples", 4000, o["resamples"]),
                         ("seed", 20261002, p.get("resample_seed"))):
            checked += 1
            if a != b:
                mism.append((s, f"comparisons/{key}.json {nm}", a, b))
        # arm summaries
        a_arm, b_arm = key.split("__")
        for side, arm in (("a", a_arm), ("b", b_arm)):
            checked += 1
            if not close(d["table"][arm]["mean_s"], p[side]["mean_s"], TOL_EXACT):
                mism.append((s, f"comparisons/{key}.json {side}.mean_s", d["table"][arm]["mean_s"], p[side]["mean_s"]))
            if p[side]["verified"] != 24 or p[side]["measured"] != 24:
                mism.append((s, f"comparisons/{key}.json {side}.verified/measured", 24, (p[side]["verified"], p[side]["measured"])))
        # per-workload ratios
        for w in p["workloads"]:
            checked += 1
            if not close(c["per_workload"][w["workload_id"]], w["ratio_b_over_a"], TOL_EXACT):
                mism.append((s, f"comparisons/{key}.json workload {w['workload_id']}", c["per_workload"][w["workload_id"]], w["ratio_b_over_a"]))
    # table-<s>.txt (3 decimals)
    rows = {}
    for line in open(f"{camp}/analysis/table-{s}.txt"):
        if not line.startswith("| ECBS"):
            continue
        cells = [x.strip() for x in line.strip().strip("|").split("|")]
        rows[cells[1]] = cells
    for arm, t in d["table"].items():
        cells = rows.get(arm)
        if cells is None:
            mism.append((s, f"table-{s}.txt missing arm", arm, None))
            continue
        ver = cells[5]
        mean_s = float(cells[6])
        lo, hi = [float(x) for x in re.findall(r"[-0-9.]+", cells[7])]
        sref = float(cells[11])
        levels = cells[14]
        for nm, a, b, tol in (("mean_s", round(t["mean_s"], 3), mean_s, 0.0011),
                              ("ci_lo", round(t["ci95"][0], 3), lo, 0.0011),
                              ("ci_hi", round(t["ci95"][1], 3), hi, 0.0011),
                              ("s_over_ref", round(t["s_over_ref"], 3), sref, 0.0011)):
            checked += 1
            if abs(a - b) > tol:
                mism.append((s, f"table-{s}.txt {arm} {nm}", a, b))
        checked += 1
        if ver != f"{t['verified']}/{t['runs']}":
            mism.append((s, f"table-{s}.txt {arm} verified", f"{t['verified']}/{t['runs']}", ver))
        mylev = " ".join(f"{k}×{v}" for k, v in sorted(t["levels"].items()))
        checked += 1
        if mylev != levels:
            mism.append((s, f"table-{s}.txt {arm} levels", mylev, levels))
    # band-<s>.json
    bj = json.load(open(f"{camp}/analysis/band-{s}.json"))
    if bj["weights"] != [0.0, 0.1, 1.0]:
        mism.append((s, f"band-{s}.json weights", [0.0, 0.1, 1.0], bj["weights"]))
    prow = {r["arm"]: r for r in bj["rows"]}
    for arm, b in d["band"].items():
        for i, w in enumerate([0.0, 0.1, 1.0]):
            checked += 1
            if not close(b["mean_s"][i], prow[arm]["mean_s"][i], TOL_EXACT):
                mism.append((s, f"band-{s}.json {arm} w={w}", b["mean_s"][i], prow[arm]["mean_s"][i]))
        checked += 1
        if prow[arm]["uncounted"] != b["uncounted"]:
            mism.append((s, f"band-{s}.json {arm} uncounted", b["uncounted"], prow[arm]["uncounted"]))
    # ranks: my order verdict from band means
    for rk in bj["ranks"]:
        a, b = rk["a"], rk["b"]
        ma, mb = d["band"][a]["mean_s"], d["band"][b]["mean_s"]
        if all(x < y for x, y in zip(ma, mb)):
            v = f"{a} < {b}"
        elif all(x > y for x, y in zip(ma, mb)):
            v = f"{b} < {a}"
        else:
            v = "unresolved inside the band"
        checked += 1
        if v != rk["verdict"]:
            mism.append((s, f"band-{s}.json rank {a} vs {b}", v, rk["verdict"]))
    # band txt: 3-decimal rendering of the json
    txt = open(f"{camp}/analysis/band-{s}.txt").read()
    for arm, b in d["band"].items():
        m = re.search(r"\| [^|]+ \| [0-9.]+ \| " + re.escape(arm) + r" \| (\d+/\d+) \| ([0-9.]+) \| ([0-9.]+) \| ([0-9.]+) \|", txt)
        checked += 1
        if not m:
            mism.append((s, f"band-{s}.txt row {arm}", "present", "absent"))
            continue
        for i in range(3):
            if abs(float(m.group(2 + i)) - round(b["mean_s"][i], 3)) > 0.0011:
                mism.append((s, f"band-{s}.txt {arm} w#{i}", round(b["mean_s"][i], 3), float(m.group(2 + i))))

print(f"checked {checked} values; mismatches {len(mism)}")
for m in mism:
    print("MISMATCH", m)
