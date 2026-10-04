"""Structural consistency of the permitted row inputs, still computing NO ratio:
(1) base sizes per job and the C-4 unmatched_size candidates; (2) on-mode
rows_fed vs rows_emitted per class; (3) row rank vs the sum of
solver_rank_increments; (4) relations vs decomp increments; (5) census
saturation markers above 24 bits. TASK-20260929-fd1a9f."""
import gzip, json, sys, collections
WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-twfloor-66d6eab71"
RUNS = WT + "/experiments/EXP-PFDR-1b78f7/runs"
FILES = {
    "R10": RUNS + "/RUN-PFDR-1b78f7-census-m3/rows.jsonl.gz",
    "R11": RUNS + "/RUN-PFDR-1b78f7-census-m4/merged/rows.jsonl.gz",
    "R12": RUNS + "/RUN-PFDR-1b78f7-census-m5/rows.jsonl.gz",
    "R14": RUNS + "/RUN-PFDR-1b78f7-j0/rows.jsonl.gz",
    "R16": RUNS + "/RUN-PFDR-1b78f7-stage-r/rows.jsonl.gz",
}
res = {"unmatched_size": [], "fed_vs_emitted": collections.Counter(), "rank_vs_incr": collections.Counter(),
       "rel_vs_decomp_incr": collections.Counter(), "saturation_above_24": collections.Counter(),
       "k_determined_by": collections.Counter(), "examples": []}
for tag, p in FILES.items():
    rows = [json.loads(l) for l in gzip.open(p, "rt")]
    rows = [r for r in rows if str(r.get("method", "")).startswith("ic_m")]
    jobs = collections.defaultdict(dict)
    for r in rows:
        m = int(r["method"][4:])
        jobs[(r["panel"], r["bits"], r["curve"], m)][(r["arm"], r["mode"])] = r
    for jk, d in jobs.items():
        if jk[0] == "main":
            ssub = {d[(a, md)]["fb_size"] for (a, md) in d if a.startswith("random_sub")}
            sdick = {d[(a, md)]["fb_size"] for (a, md) in d if a.startswith("random_dick")}
            for (a, md), r in d.items():
                ref = ssub if a in ("subgroup", "small_x") else sdick if a == "dickson" else None
                if ref is not None and len(ref) == 1 and r["fb_size"] not in ref:
                    res["unmatched_size"].append([tag, list(jk), a, md, r["fb_size"], sorted(ref)])
                if ref is not None and len(ref) != 1:
                    res["unmatched_size"].append([tag, list(jk), a, md, "random sizes disagree", sorted(ref)])
    for r in rows:
        h = r["harvest"]
        m = int(r["method"][4:])
        if r["mode"] == "on":
            on = h["on"]
            for c in ("TT", "TB", "SS"):
                fed = on["rows_fed"][c]; em = h[c]["at_stop"]["rows_emitted"]
                res["fed_vs_emitted"][(tag, c, "fed==emitted" if fed == em else ("fed<emitted" if fed < em else "fed>emitted"))] += 1
            inc = on["solver_rank_increments"]
            s = inc["decomp"] + inc["TT"] + inc["TB"] + inc["SS"]
            res["rank_vs_incr"][(tag, "on", "equal" if s == r["rank"] else "differ")] += 1
            res["rel_vs_decomp_incr"][(tag, "on", "rel==decomp_incr" if r["relations"] == inc["decomp"] else ("rel>decomp_incr" if r["relations"] > inc["decomp"] else "rel<decomp_incr"))] += 1
            res["k_determined_by"][(tag, r["arm"] if r["arm"] in ("known_log", "j0_coset") else "other", str(on.get("k_determined_by")))] += 1
            if len(res["examples"]) < 3 and s != r["rank"]:
                res["examples"].append([tag, r["bits"], r["curve"], m, r["arm"], s, r["rank"]])
        else:
            res["rank_vs_incr"][(tag, "census", "rank<=relations" if r["rank"] <= r["relations"] else "rank>relations")] += 1
        if r["bits"] > 24:
            for c in ("TT", "TB", "SS"):
                res["saturation_above_24"][(tag, r["mode"], c, "saturated" if h[c].get("census_saturated_at_row") is not None else "not_saturated")] += 1
out = {k: ([[list(map(str, kk)), v] for kk, v in sorted(val.items(), key=lambda kv: str(kv[0]))] if isinstance(val, collections.Counter) else val) for k, val in res.items()}
json.dump(out, open(sys.argv[1], "w"), indent=1)
for k, v in out.items():
    print("==", k)
    for e in v: print("  ", e)
