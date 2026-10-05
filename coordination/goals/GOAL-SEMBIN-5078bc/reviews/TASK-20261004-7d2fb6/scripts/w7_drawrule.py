#!/usr/bin/env python3
"""w7_drawrule.py -- joint W7 (2): from RUN-SEMBIN-9bb990/counts (the exact count of every draw of every n), recompute per n (low_degree_polynomial,
B_random: the paper's Table 2 convention) the FIRST solution-free draw and the FIRST solution-bearing draw in draw order 0..9, and compare with the
draws that ran in RUN-SEMBIN-5ed13e (instance ids in its lane records) and with the counts those lane records carry. Read-only."""
import json, glob, os, collections, sys
REPO = "/home/user/crypto-autoresearcher"; WS = os.environ["WS"]
C = f"{REPO}/experiments/EXP-SEMBIN-7e1371/runs/RUN-SEMBIN-9bb990/counts/cells/results.jsonl"
R = f"{REPO}/experiments/EXP-SEMBIN-7e1371/runs/RUN-SEMBIN-5ed13e"
recs = [json.loads(l) for l in open(C) if l.strip()]
cnt = collections.defaultdict(dict); dup = collections.defaultdict(list)
for r in recs:
    if r.get("instrument") == "exhaustive_solution_count" and r.get("m") == 2 and r.get("t") == 2 and r.get("family") == "chained_S3_eq5":
        key = (r["n"], r["subspace"], r["B_mode"])
        dup[(key, r["draw"])].append(r["solutions"])
        cnt[key][r["draw"]] = r["solutions"]
out = {}
for n in range(40, 46):
    key = (n, "low_degree_polynomial", "B_random")
    c = cnt[key]
    draws = sorted(c)
    zero = [d for d in draws if c[d] == 0]; nz = [d for d in draws if c[d] > 0]
    ran = []
    for lane in glob.glob(f"{R}/closure_m2_n{n}/cells/results.jsonl"):
        for l in open(lane):
            r = json.loads(l)
            if r["instrument"] == "exhaustive_solution_count": ran.append((r["draw"], r["solutions"]))
    ran = sorted(ran)
    rule = sorted({zero[0], nz[0]})
    out[n] = {"counts_by_draw_0_to_9": [c.get(d) for d in range(10)], "draws_present": draws, "first_solution_free": zero[:1], "first_solution_bearing": nz[:1], "rule_draws": rule,
              "draws_that_ran": [d for d, _ in ran], "counts_in_5ed13e_records": [s for _, s in ran], "rule_equals_ran": rule == [d for d, _ in ran],
              "counts_agree_with_9bb990_counts": all(c[d] == s for d, s in ran), "duplicate_count_records_disagree": any(len(set(v)) > 1 for k, v in dup.items() if k[0] == key)}
    print(n, out[n])
json.dump(out, open(f"{WS}/outputs/w7_drawrule.json", "w"), indent=1)
