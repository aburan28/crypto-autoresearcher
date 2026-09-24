#!/usr/bin/env python3
"""J8 (1), (3) -- TASK-20260924-d95e70. From archived records: per set, the
M_3 / M_4 / W_4 / M_5 records against the semi-regular reference (series.json)
and the bilinear-support ceiling; C-NULLS code-path hashes per set; and the
number of independent random draws behind each null set (F-AFF-1 instances are
A0 + sum_j r_j Aj for ONE archived (A0, Aj) draw)."""
import collections
import glob
import gzip
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = "/home/user/crypto-autoresearcher/experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0"
SRC = "/home/user/crypto-autoresearcher/experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05"
IMPL = "/home/user/crypto-autoresearcher/experiments/EXP-CERTBIN-e94b27/impl/closure.py"
C = collections.Counter
ser = json.load(open(os.path.join(HERE, "series.json")))
SR_RANK4 = ser["cases"][0]["D4"]["semi_regular_rank"]
CEIL5 = ser["bilinear_support_ceiling_M5"]["rank_M5_ceiling"]
recs = [json.loads(l) for l in gzip.open(os.path.join(RUN, "closures.jsonl.gz"), "rt")]
by = collections.defaultdict(list)
for r in recs:
    by[(r["set"], r["closure"])].append(r)
table = {}
for s in ("U62", "C20", "S62", "N-AFF62", "N-F262"):
    t = {}
    t["M3_rank"] = dict(C(r["rank"] for r in by[(s, "M_3")]))
    m4 = by[(s, "M_4")]
    t["M4_rank"] = dict(C(r["rank"] for r in m4))
    t["M4_rank_eq_semi_regular_2771"] = sum(r["rank"] == SR_RANK4 for r in m4)
    t["M4_nontrivial_syzygies_2771_minus_rank"] = dict(C(SR_RANK4 - r["rank"] for r in m4))
    t["M4_one"] = dict(C(str(r["one"]) for r in m4))
    w = by[(s, "W_4")]
    t["W4_iterations_to_fixpoint"] = dict(C(r["iterations_to_fixpoint"] for r in w))
    t["W4_dims_by_deg"] = {str(k): v for k, v in C(tuple(r["dims_by_deg"]) for r in w).items()}
    t["W4_one"] = dict(C(str(r["one"]) for r in w))
    t["W4_fallen_at_iteration0"] = dict(C(r["new_fallen_per_iteration"][0] for r in w))
    if (s, "M_5") in by:
        m5 = by[(s, "M_5")]
        t["M5_rank"] = dict(C(r["rank"] for r in m5))
        t["M5_rank_eq_bilinear_ceiling_12364"] = sum(r["rank"] == CEIL5 for r in m5)
        t["M5_one"] = dict(C(str(r["one"]) for r in m5))
        t["M5_cap_B4"] = dict(C(r["dims_by_deg"][4] for r in m5))
    table[s] = t
hashes = {}
for f in sorted(glob.glob(os.path.join(RUN, "checkpoint", "p-*.json.gz"))):
    d = json.load(gzip.open(f, "rt"))
    hashes[os.path.basename(f)] = d.get("closure_module_sha256")
impl_sha = hashlib.sha256(open(IMPL, "rb").read()).hexdigest()
p1 = json.load(gzip.open(os.path.join(SRC, "checkpoint", "p1-instances.json.gz"), "rt"))
aff = p1["F-AFF-1"]
draws = {"N-AFF62": {"family": "F-AFF-1", "A0_hex_is_single": isinstance(aff.get("A0_hex"), list) and isinstance(aff["A0_hex"][0], str),
                     "Aj_hex_count": len(aff.get("Aj_hex", [])),
                     "independent_random_draws_behind_62_instances": 1,
                     "note": "every N-AFF62 instance is A0 + sum_j r_j Aj for the ONE archived (A0, Aj) of F-AFF-1"},
         "N-F262": {"family": "F-NULLF2", "independent_random_draws_behind_62_instances": 62,
                    "note": "each F-NULLF2 instance is its own draw on the union support"}}
out = {"task": "TASK-20260924-d95e70", "joint": "J8", "semi_regular_rank_M4": SR_RANK4,
       "bilinear_ceiling_rank_M5": CEIL5, "table": table,
       "c_nulls_closure_module_sha256_per_checkpoint": hashes, "impl_closure_py_sha256": impl_sha,
       "all_checkpoints_same_hash_as_impl": all(h == impl_sha for h in hashes.values()),
       "null_draw_structure": draws}
json.dump(out, open(os.path.join(HERE, "null-comparison.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
