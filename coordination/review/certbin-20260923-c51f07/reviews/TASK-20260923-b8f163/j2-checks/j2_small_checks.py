#!/usr/bin/env python3
"""TASK-20260923-b8f163 J2: small consistency checks of implementation.md statements
against per-target records and references.json. Zero trials; no producer code."""
import gzip, json, os
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, *[".."] * 6, "experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05"))
def recs(f): return [json.loads(l) for l in gzip.open(os.path.join(RUN, f"targets-{f}.jsonl.gz"), "rt")]
refs = json.load(open(os.path.join(RUN, "references.json")))
s3 = recs("F-S3")
out = {}
u4 = [r for r in s3 if r["D"] == 4 and not r["degenerate"] and r["s"] == 0]
out["F-S3_D4_nondeg_unsat"] = len(u4)
out["F-S3_D4_nondeg_unsat_one_in_R4"] = sum(r["one_in_R"] for r in u4)
out["F-S3_D4_nondeg_unsat_one_in_R4_rate"] = sum(r["one_in_R"] for r in u4) / len(u4)
out["F-S3_Dstar_unsat_nondeg"] = dict(Counter(str(r.get("D_star")) for r in u4))
s3x = {r["x_R"] for r in s3}
out["F-AFF_ref_xR_equal_to_F-S3_test_xR"] = {f: sum(1 for l, v in refs[f]["references"].items() if l != "modal" and v["x_R"] in s3x) for f in ("F-AFF-1", "F-AFF-2", "F-AFF-3")}
out["F-AFF_refs_sharing_F-S3_ref_xR"] = {f: sorted(l for l, v in refs[f]["references"].items() if l != "modal" and v["x_R"] in {refs["F-S3"]["references"][k]["x_R"] for k in ("U1","U2","U3","S1","S2")}) for f in ("F-AFF-1","F-AFF-2","F-AFF-3")}
json.dump(out, open(os.path.join(HERE, "j2_small_checks.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
