#!/usr/bin/env python3
"""Bind the 42 comparisons/*.json to the sealed records: recompute measured counts, mean S per arm,
per-workload means and ops ratio (mean_b/mean_a) from records.jsonl. (SHF-20261021-477d51 receipts reader)"""
import glob, json, sys
from collections import OrderedDict, defaultdict
B = sys.argv[1]
out = OrderedDict(); bad = 0; n = 0
for s in ["c24", "c28", "c30", "r24", "r26", "r28"]:
    sess = json.load(open(f"{B}/sessions/{s}/session.json"))
    S = defaultdict(list); SW = defaultdict(list)
    for l in open(f"{B}/sessions/{s}/records.jsonl"):
        r = json.loads(l)
        if r["warmup"] or r["outcome"]["status"] != "verified":
            continue
        S[r["arm"]].append(r["cost"]["s"]); SW[(r["arm"], r["workload"]["workload_id"])].append(r["cost"]["s"])
    for f in sorted(glob.glob(f"{B}/sessions/{s}/comparisons/*.json")):
        c = json.load(open(f)); n += 1
        a, b = c["a"], c["b"]
        ma = sum(S[a["arm"]]) / len(S[a["arm"]]); mb = sum(S[b["arm"]]) / len(S[b["arm"]])
        ok = (a["session_id"] == b["session_id"] == sess["session_id"] and a["measured"] == len(S[a["arm"]]) and b["measured"] == len(S[b["arm"]])
              and abs(a["mean_s"] - ma) <= 1e-9 * ma and abs(b["mean_s"] - mb) <= 1e-9 * mb
              and abs(c["ops"]["ratio_b_over_a"] - mb / ma) <= 1e-9 * (mb / ma))
        for w in c["workloads"]:
            wa = SW[(a["arm"], w["workload_id"])]; wb = SW[(b["arm"], w["workload_id"])]
            ok = ok and abs(w["a_mean_s"] - sum(wa) / len(wa)) <= 1e-9 * w["a_mean_s"] and abs(w["b_mean_s"] - sum(wb) / len(wb)) <= 1e-9 * w["b_mean_s"]
        bad += not ok
        out[f.split("/sessions/")[1]] = OrderedDict(ok=ok, a=a["arm"], b=b["arm"], mean_a=ma, mean_b=mb, ratio=mb / ma, reported_ratio=c["ops"]["ratio_b_over_a"])
json.dump(OrderedDict(n=n, mismatches=bad, files=out), open(sys.argv[2], "w"), indent=1)
print("comparisons", n, "mismatches", bad)
