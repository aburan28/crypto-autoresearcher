"""POST HOC (labelled; written after f7.json was read): sensitivity of the m = 4
on-mode ratio slope to r_distinct (raw) and r_census, every m = 4 base, 20000
replicates seed 0; ratio levels per rung (median, min) under r_rank and
r_frozen for m = 4 small_x on; and the minimum r_rank ratio over every m = 4
on-mode instance. Not decision-bearing; reported beside the declared F7 result."""
import json, math, os, statistics, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f7  # noqa: E402
S = f7.S
recs = [json.loads(l) for l in open(os.path.join(HERE, "..", "rederivation", "out", "instances.jsonl"))]
out = {"label": "POST HOC sensitivity, not decision-bearing", "slopes_20000": {}, "levels_small_x_m4_on": {}}
for base in f7.BASES:
    for key in ("r_distinct_raw", "r_census"):
        xs, ys, gs = [], [], []
        for r in recs:
            k = r["key"]
            if r["set"] != "S15" or k[0] != "main" or k[3] != 4 or k[5] != "on" or k[4] not in f7.BASES[base] or r["excluded"]:
                continue
            rr = r[key]
            if not rr:
                continue
            xs.append(r["log2N"]); ys.append(math.log2(r["S3"] / (0.5 * math.sqrt(rr * r["N"])))); gs.append(k[1])
        f = S.bootstrap_slope(xs, ys, gs, reps=20000, level=0.95, seed=0)
        out["slopes_20000"][f"m4|{base}|on|ratio_{key}"] = {k2: f[k2] for k2 in ("slope", "lo", "hi", "n")}
for key in ("r_rank", "r_frozen", "r_distinct_raw"):
    lv = {}
    for r in recs:
        k = r["key"]
        if r["set"] == "S15" and k[0] == "main" and k[3] == 4 and k[4] == "small_x" and k[5] == "on":
            lv.setdefault(k[1], []).append(r["S3"] / (0.5 * math.sqrt(r[key] * r["N"])))
    out["levels_small_x_m4_on"][key] = {b: {"median": statistics.median(v), "min": min(v)} for b, v in sorted(lv.items())}
mins = {}
for key in ("r_rank", "r_rank1", "r_distinct_raw"):
    vals = [(r["S3"] / (0.5 * math.sqrt(r[key] * r["N"])), r["key"]) for r in recs
            if r["set"] in ("S15", "S16") and r["key"][0] == "main" and r["key"][3] == 4 and r["key"][5] == "on" and not r["excluded"] and r[key]]
    mins[key] = min(vals)
out["min_ratio_m4_on_all_arms"] = {k: [v[0], v[1]] for k, v in mins.items()}
json.dump(out, open(os.path.join(sys.argv[1], "f7-posthoc.json"), "w"), indent=1, sort_keys=True)
print(json.dumps(out, indent=1)[:6000])
