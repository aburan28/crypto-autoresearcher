"""R0 part 2: regenerate the band table, NULL-3 table, F5 flags, iteration-count table,
count-1 audit, censoring audit, equal-d^s and m=3 sections from raw records and diff
against analysis.json.  Red Team TASK-20260904-3a2ff5."""
import json, os, collections
ROOT = "/home/user/crypto-autoresearcher"
RUNS = os.path.join(ROOT, "experiments/EXP-PFDR-cbdefb/runs")
OUT = os.path.join(ROOT, "coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-3a2ff5")
AJ = json.load(open(os.path.join(ROOT, "experiments/EXP-PFDR-cbdefb/analysis.json")))
LADDER = [(s, p) for s in (1,2,3,4,5) for p in (4099,16411,65537)]

def load(run):
    return json.load(open(os.path.join(RUNS, run, "raw-result.json")))

def systems(raw, arm):
    if arm == "semaev":
        return [d["semaev"] for d in raw["raw"]["draws"]]
    if arm == "noncurve":
        return [d["result"] for d in raw["raw"]["noncurve"]]
    if arm == "null1":
        return [o["result"] for d in raw["raw"]["draws"] for o in d.get("null1", [])]
    if arm == "null2":
        return [o["result"] for o in raw["raw"].get("null2_objects", [])]
    if arm == "null3":
        return [o["result"] for o in raw["raw"].get("null3_objects", [])]

def rule3(r):
    falls = [h["D"] for h in r.get("history", []) if h.get("fall") and h.get("iteration_count") != 1]
    return (falls[0] if falls else None, falls[-1] if falls else None)

report = {}

# ---- 1. count-1 audit: where does the artifact tell fire, and is it only at s = 1?
count1 = collections.Counter(); count1_sat = collections.Counter()
for s, p in LADDER:
    raw = load(f"RUN-PFDR-cbdefb-m2-s{s}-p{p}")
    for arm in ("semaev", "null1", "null2", "null3", "noncurve"):
        for r in systems(raw, arm):
            if r.get("degenerate"): continue
            for h in r.get("history", []):
                if h.get("fall") and h.get("iteration_count") == 1:
                    count1[f"{s},{p},{arm}"] += 1
                    if h.get("W0_saturated") is True:
                        count1_sat[f"{s},{p},{arm}"] += 1
report["count1_by_cell_arm"] = dict(count1)
report["count1_saturated_by_cell_arm"] = dict(count1_sat)
report["count1_only_at_s1"] = all(k.startswith("1,") for k in count1)
report["analysis_falls_with_iteration_count_1"] = AJ["controls"]["falls_with_iteration_count_1"]
report["count1_matches_analysis"] = dict(count1) == AJ["controls"]["falls_with_iteration_count_1"]

# ---- 2. band table (HEUR-001)
band = {}
for s, p in LADDER:
    raw = load(f"RUN-PFDR-cbdefb-m2-s{s}-p{p}")
    for arm in ("null1", "null2"):
        offs, cens, nofall, unc = set(), 0, 0, 0
        for r in systems(raw, arm):
            if r.get("degenerate"): continue
            _, dlf = rule3(r)
            if r.get("right_censored"):
                cens += 1
            elif dlf is None:
                nofall += 1
            else:
                unc += 1; offs.add(dlf - (s + 2))
        band[f"{s},{p},{arm}"] = {"s_plus_2": s + 2, "uncensored_with_fall": unc,
                                  "offsets": sorted(offs), "all_in_012": all(0 <= c <= 2 for c in offs) if offs else None,
                                  "censored": cens, "no_fall": nofall}
report["band"] = band
report["band_matches_analysis"] = {}
for k, v in AJ["controls"]["null_band"].items():
    mine = band.get(k)
    report["band_matches_analysis"][k] = (mine is not None and sorted(v.get("offsets", [])) == mine["offsets"]
                                          and v.get("uncensored") == mine["uncensored_with_fall"])

# ---- 3. F5 flags and pairs
pairs = {}
for s, p in LADDER:
    raw = load(f"RUN-PFDR-cbdefb-m2-s{s}-p{p}")
    for arm in ("semaev", "null1", "null2", "null3", "noncurve"):
        st = set()
        for r in systems(raw, arm):
            if r.get("degenerate"): continue
            dff, dlf = rule3(r)
            st.add((dff, dlf, "censored" if r.get("right_censored") else "certified"))
        pairs[f"{s},{p},{arm}"] = sorted(st, key=str)
f5 = {}
for arm in ("null1", "null2", "noncurve"):
    f5[arm] = all(pairs[f"{s},{p},{arm}"] == pairs[f"{s},{p},semaev"] for s, p in LADDER)
report["F5"] = f5
report["F5_analysis"] = AJ["controls"]["F5_same_pair_at_every_cell"]
report["F5_matches"] = f5 == {k: v for k, v in AJ["controls"]["F5_same_pair_at_every_cell"].items()}

# ---- 4. NULL-3 vs Semaev
n3 = {}
for s, p in LADDER:
    raw = load(f"RUN-PFDR-cbdefb-m2-s{s}-p{p}")
    sem = {rule3(r)[0] for r in systems(raw, "semaev") if not r.get("degenerate")}
    n3v = {rule3(r)[0] for r in systems(raw, "null3") if not r.get("degenerate")}
    n3l = {rule3(r)[1] for r in systems(raw, "null3") if not r.get("degenerate")}
    seml = {rule3(r)[1] for r in systems(raw, "semaev") if not r.get("degenerate")}
    diff = sorted({(a - b) if (a is not None and b is not None) else None for a in n3v for b in sem})
    diffl = sorted({(a - b) if (a is not None and b is not None) else None for a in n3l for b in seml}, key=str)
    n3[f"{s},{p}"] = {"semaev_dff": sorted(sem, key=str), "null3_dff": sorted(n3v, key=str),
                      "dff_diff": [d for d in diff], "dlf_diff": [d for d in diffl],
                      "null3_degenerate": sum(1 for r in systems(raw, "null3") if r.get("degenerate"))}
report["null3"] = n3

# ---- 5. censoring audit: did any censored draw enter a d_lf fit?
cens_in_fit = 0
for s, p in LADDER:
    raw = load(f"RUN-PFDR-cbdefb-m2-s{s}-p{p}")
    for r in systems(raw, "semaev"):
        if r.get("right_censored"):
            cens_in_fit += 1
report["semaev_censored_draws_total"] = cens_in_fit

# ---- 6. certificate routes and Z sizes on the Semaev arm (for R2/R3)
routes = collections.Counter(); zsz = collections.Counter(); vcomp = collections.Counter()
c2_holds = collections.Counter(); c2_degrees = collections.Counter()
for s, p in LADDER:
    raw = load(f"RUN-PFDR-cbdefb-m2-s{s}-p{p}")
    for r in systems(raw, "semaev"):
        if r.get("degenerate"): continue
        c = r.get("certificate", {})
        routes[f"s{s}:{c.get('route')}"] += 1
        zsz[f"s{s}:Z={c.get('Z_size')}"] += 1
        for c2 in c.get("C2", []) or []:
            c2_degrees[f"s{s}:D={c2['D']}"] += 1
            c2_holds[f"s{s}:D={c2['D']}:{c2['holds']}"] += 1
        for h in r.get("history", []):
            if h.get("fall"):
                vcomp[f"s{s}:V_complete_at_fall={h.get('V_complete_at_D')}"] += 1
report["semaev_certificate_routes"] = dict(routes)
report["semaev_Z_sizes"] = dict(zsz)
report["semaev_C2_degrees_checked"] = dict(c2_degrees)
report["semaev_C2_holds"] = dict(c2_holds)
report["semaev_V_complete_at_fall_degree"] = dict(vcomp)

# ---- 7. equal-d^s and m3
for run in ("equalds-d2-s6", "equalds-d4-s3", "equalds-d8-s2", "m3-s2", "m3-s3"):
    raw = load(f"RUN-PFDR-cbdefb-{run}")
    m = raw["metrics"]
    report[f"run_{run}_metric_keys"] = sorted(m.keys())
    report[f"run_{run}_cell"] = m.get("cell")

json.dump(report, open(os.path.join(OUT, "r0_controls.json"), "w"), indent=1, default=str)
for k in ("count1_only_at_s1", "count1_matches_analysis", "F5", "F5_analysis", "F5_matches",
          "semaev_censored_draws_total", "semaev_certificate_routes", "semaev_Z_sizes",
          "semaev_C2_degrees_checked", "semaev_C2_holds", "semaev_V_complete_at_fall_degree"):
    print(k, "=", report[k])
print("band mismatches:", [k for k, v in report["band_matches_analysis"].items() if not v])
