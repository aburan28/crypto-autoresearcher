"""POST-SEAL comparison of the sealed F2 values with the producer's A7_floor block
(RUN-PFDR-1b78f7-analysis/analysis.json). Reads the sealed outputs (never edits
them) and the producer file. Writes rederivation/out-post/compare-producer.json.
TASK-20260929-fd1a9f."""
import json, os, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-twfloor-66d6eab71"
A = WT + "/experiments/EXP-PFDR-1b78f7/runs/RUN-PFDR-1b78f7-analysis/analysis.json"
FZ = "frozen|S3|c2"


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    prod = json.load(open(A))["A7_floor"]
    recs = {tuple(json.loads(l)["key"]): json.loads(l) for l in open(os.path.join(HERE, "out", "instances.jsonl"))}
    s15 = {k: r for k, r in recs.items() if r["set"] == "S15"}

    def pk(e):
        return (e["panel"], int(e["bits"]), int(e["curve"]), int(e["m"]), e["arm"], e["mode"])

    res = {"producer_scalars": {k: prod[k] for k in ("instances", "excluded_no_verified_k_or_r0", "excluded_unmatched_size", "min")}}
    for lst in ("below_0_9", "below_1_0"):
        pset = {pk(e): e for e in prod[lst]}
        thr = "lt09" if lst == "below_0_9" else "lt10"
        mine = {k for k, r in s15.items() if r["eval"][FZ]["state"] == "ok" and r["eval"][FZ][thr]}
        exact, rounding, differ, r_diff = 0, 0, [], []
        for k in sorted(set(pset) & mine):
            e, r = pset[k], s15[k]
            if e["r"] != r["r_frozen"]:
                r_diff.append([list(k), e["r"], r["r_frozen"]])
            a, b = e["ratio"], r["eval"][FZ]["ratio"]
            if a == b:
                exact += 1
            elif abs(a - b) <= 1e-12 * abs(b):
                rounding += 1
            else:
                differ.append([list(k), a, b])
        res[lst] = {"producer_count": len(pset), "mine_count": len(mine), "key_sets_equal": set(pset) == mine,
                    "only_producer": [list(x) for x in sorted(set(pset) - mine)], "only_mine": [list(x) for x in sorted(mine - set(pset))],
                    "ratio_bit_identical": exact, "ratio_equal_to_1e-12_relative": rounding, "ratio_differ": differ,
                    "r_differ": r_diff}
    # producer universe reading: instances 3283 = S15 evaluable minus capped (CV-3b); +70 excluded (no verified k or r0) +2 unmatched
    ev_primary = [r for r in s15.values() if r["eval"][FZ]["state"] == "ok"]
    ev_cv3b = [r for r in ev_primary if r["terminated_by"] == "k_found"]
    capped_eval = [r["key"] for r in ev_primary if r["terminated_by"] != "k_found"]
    res["universe"] = {"mine_evaluable_primary_CV3": len(ev_primary), "mine_evaluable_CV3b": len(ev_cv3b),
                       "capped_but_evaluable_under_CV3": capped_eval,
                       "producer_instances": prod["instances"],
                       "reading": "producer instances = my CV-3b set iff the counts are equal; the producer's 70 = 35 capped known_log census + 35 R14 j0 rho rows (my CV-1 excludes rho rows), checked below"}
    j0rho = 35
    res["universe"]["check_70"] = {"capped_known_log_census": sum(1 for r in s15.values() if r["terminated_by"] != "k_found"),
                                   "j0_rho_rows_in_R14": j0rho, "sum": sum(1 for r in s15.values() if r["terminated_by"] != "k_found") + j0rho,
                                   "producer": prod["excluded_no_verified_k_or_r0"]}
    # min
    mn = min(ev_cv3b, key=lambda r: r["eval"][FZ]["ratio"])
    res["min"] = {"mine": [mn["key"], mn["eval"][FZ]["ratio"], mn["r_frozen"]], "producer": prod["min"],
                  "equal": tuple(mn["key"]) == pk(prod["min"]) and mn["eval"][FZ]["ratio"] == prod["min"]["ratio"] and mn["r_frozen"] == prod["min"]["r"]}
    # medians per mode|m
    med = {}
    for setname, pool in (("CV3b", ev_cv3b), ("CV3_primary", ev_primary)):
        g = {}
        for r in pool:
            g.setdefault(f"{r['key'][5]}|{r['key'][3]}", []).append(r["eval"][FZ]["ratio"])
        med[setname] = {k: statistics.median(v) for k, v in sorted(g.items())}
    res["per_mode_m_median"] = {"producer": prod["per_mode_m_median"], "mine": med,
                                "equal_CV3b": {k: med["CV3b"].get(k) == v for k, v in prod["per_mode_m_median"].items()},
                                "rel_diff_CV3b": {k: (med["CV3b"].get(k) - v) / v for k, v in prod["per_mode_m_median"].items()}}
    json.dump(res, open(os.path.join(outdir, "compare-producer.json"), "w"), indent=1, sort_keys=True, default=str)
    print(json.dumps({k: (v if k not in ("below_0_9", "below_1_0") else {kk: vv for kk, vv in v.items() if kk not in ()}) for k, v in res.items()}, indent=1, default=str)[:6000])


if __name__ == "__main__":
    main(sys.argv[1])
