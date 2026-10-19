#!/usr/bin/env python3
"""After constraint 4: compare my classification (out/j5_classification.json, from recorded
orders; and out/recensus_compare.json, from my own counts) with census/summary.json list by list,
and determine the index base that makes each single-curve run's published seed the last accepted."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
summ = json.load(open(os.path.join(BUNDLE, "census", "summary.json")))
mine = json.load(open(os.path.join(ROOT, "out", "j5_classification.json")))
rc = json.load(open(os.path.join(ROOT, "out", "recensus_compare.json")))
q1 = json.load(open(os.path.join(ROOT, "out", "q1_seeds.json")))
res = {"runs": {}, "all_equal": True}
for s in summ:
    t = int(s["run"].split("(")[1].rstrip(")"))
    m, r = mine["runs"][str(t)], rc["runs"][str(t)]
    cmp = {"p_bits_equal": s["p_bits"] == P_bits if (P_bits := {863711343: 239, 863966734: 192, 871002724: 521, 871696354: 256, 872952608: 384, 891607927: 224}[t]) else False,
           "candidates_equal": s["candidates"] == m["b_exists"],
           "accepted_equal_j5": s["accepted"] == m["accepted_idx"], "accepted_equal_recensus": s["accepted"] == r["accepted_idx"],
           "bitlen_equal_j5": s["n_longer_than_p"] == m["bitlen_idx"], "bitlen_equal_recensus": s["n_longer_than_p"] == r["bitlen_idx"],
           "twist_equal_j5": s["only_twist_prime"] == m["twist_only_idx"], "twist_equal_recensus": s["only_twist_prime"] == r["twist_only_idx"]}
    pubs = [rec["hits"][0] for rec in q1["seeds"].values() if rec["hits"][0]["t"] == t]
    if len(pubs) == 1:
        h = pubs[0]
        cmp["single_curve_last_accepted_is_block1"] = s["accepted"][-1] == h["block1"]
        cmp["single_curve_last_accepted_is_block0"] = s["accepted"][-1] == h["block0"]
    else:
        cmp["multi_curve_published_block1_subset_of_accepted"] = all(h["block1"] in s["accepted"] for h in pubs)
        cmp["multi_curve_last_accepted_is_last_published_block1"] = s["accepted"][-1] == max(h["block1"] for h in pubs)
    res["runs"][str(t)] = cmp
    # the 0-based reading is the alternative convention and must FAIL
    if not all((not v) if k.endswith("_is_block0") else v for k, v in cmp.items()):
        res["all_equal"] = False
json.dump(res, open(os.path.join(ROOT, "out", "summary_comparison.json"), "w"), indent=1, sort_keys=True)
for t, c in res["runs"].items():
    print(t, c)
print("all_equal", res["all_equal"])
