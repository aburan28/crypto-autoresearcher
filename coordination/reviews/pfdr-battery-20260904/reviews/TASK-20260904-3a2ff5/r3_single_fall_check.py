"""R3: verify the hypothesis and the conclusion of Theorem A of
derivation-r3-single-fall.md on EVERY system of EXP-PFDR-cbdefb (all arms, all cells).
TASK-20260904-3a2ff5.  Reads runs/*/raw-result.json only."""
import json, os, collections
ROOT = "/home/user/crypto-autoresearcher"
RUNS = os.path.join(ROOT, "experiments/EXP-PFDR-cbdefb/runs")
OUT = os.path.join(ROOT, "coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-3a2ff5")
LAD = [(s, p) for s in (1, 2, 3, 4, 5) for p in (4099, 16411, 65537)]

def systems(raw):
    yield from (("semaev", d["semaev"]) for d in raw["raw"]["draws"])
    yield from (("noncurve", d["result"]) for d in raw["raw"]["noncurve"])
    yield from (("null1", o["result"]) for d in raw["raw"]["draws"] for o in d.get("null1", []))
    yield from (("null2", o["result"]) for o in raw["raw"].get("null2_objects", []))
    yield from (("null3", o["result"]) for o in raw["raw"].get("null3_objects", []))

res = {"V_complete_at_first_fall": collections.Counter(),
       "SAT_fall_dim_equals_dim_I_at_dff_minus_1": collections.Counter(),
       "fall_degrees_per_system": collections.Counter(),
       "missing_diagnostic": collections.Counter(),
       "Z_size_max_by_arm": collections.defaultdict(int)}
for run in [f"RUN-PFDR-cbdefb-m2-s{s}-p{p}" for s, p in LAD] + ["RUN-PFDR-cbdefb-m3-s2",
                                                                 "RUN-PFDR-cbdefb-m3-s3"]:
    raw = json.load(open(os.path.join(RUNS, run, "raw-result.json")))
    for arm, r in systems(raw):
        if r.get("degenerate"):
            continue
        res["Z_size_max_by_arm"][arm] = max(res["Z_size_max_by_arm"][arm],
                                            r.get("certificate", {}).get("Z_size") or 0)
        falls = [h for h in r["history"] if h["fall"]]
        res["fall_degrees_per_system"][f"{arm}:{len(falls)}"] += 1
        if not falls:
            continue
        h = falls[0]
        if "V_complete_at_D" not in h:
            res["missing_diagnostic"][arm] += 1
            continue
        res["V_complete_at_first_fall"][f"{arm}:{h['V_complete_at_D']}"] += 1
        prev = [x for x in r["history"] if x["D"] == h["D"] - 1]
        ok = bool(prev) and h["fall_dim"] == prev[0].get("dim_I_at_D")
        res["SAT_fall_dim_equals_dim_I_at_dff_minus_1"][f"{arm}:{ok}"] += 1
res = {k: (dict(v) if isinstance(v, (collections.Counter, collections.defaultdict)) else v)
       for k, v in res.items()}
json.dump(res, open(os.path.join(OUT, "r3_single_fall_check.json"), "w"), indent=1)
print(json.dumps(res, indent=1))
