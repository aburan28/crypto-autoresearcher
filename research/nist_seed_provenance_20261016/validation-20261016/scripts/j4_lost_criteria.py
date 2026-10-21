#!/usr/bin/env python3
"""J4 refinement: would each twist-only row's twist (reachable by -b when p = 3 mod 4) have
passed the full stated criteria (prime, bitlen(nt) <= bitlen(p), nt != p, MOV k < 2^10)?
Uses the recorded Nt (verified against full counts in j3_analysis for all 47 rows)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import gmpy2
P = load_params()
cls = json.load(open(os.path.join(ROOT, "out", "j5_classification.json")))
res = {}
for t, field, count in RUNS:
    p = P[FIELD_CURVE[field]]["p"]
    rec = {int(l.split()[0]): tuple(map(int, l.split()[1:])) for l in open(os.path.join(BUNDLE, "census", f"orders_{t}.txt"))}
    rows = []
    for i in cls["runs"][str(t)]["twist_only_idx"]:
        nt = rec[i][1]
        ok_bit = nt.bit_length() <= p.bit_length()
        ok_mov = nt != p and all(pow(p, k, nt) != 1 for k in range(1, 1024))
        rows.append({"i": i, "nt_bits": nt.bit_length(), "passes_bitlen": ok_bit, "passes_n_ne_p_and_mov": ok_mov,
                     "would_be_accepted": bool(gmpy2.is_prime(nt, 25)) and ok_bit and ok_mov})
    res[str(t)] = {"p_mod_4": p % 4, "twist_only": len(rows), "would_be_accepted": sum(r["would_be_accepted"] for r in rows),
                   "fail_bitlen": [r["i"] for r in rows if not r["passes_bitlen"]], "rows": rows}
s3 = sum(v["would_be_accepted"] for v in res.values() if v["p_mod_4"] == 3)
t3 = sum(v["twist_only"] for v in res.values() if v["p_mod_4"] == 3)
res["summary"] = {"twist_only_p3mod4": t3, "would_be_accepted_p3mod4": s3}
json.dump(res, open(os.path.join(ROOT, "out", "j4_lost_criteria.json"), "w"), indent=1, sort_keys=True)
for t, v in res.items():
    if t != "summary":
        print(t, "p%4", v["p_mod_4"], "twist-only", v["twist_only"], "would be accepted on twist", v["would_be_accepted"], "fail bitlen", v["fail_bitlen"])
print(res["summary"])
