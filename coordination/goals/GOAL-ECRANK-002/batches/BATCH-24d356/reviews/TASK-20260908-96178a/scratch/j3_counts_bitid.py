#!/usr/bin/env python3
"""J3.2: counts_per_H monotonicity, feasibility fraction, near-miss ledger
semantics. J3.3: R3/R4 instance-list bit-identity by independent hashing."""
import json, os, hashlib

ROOT = "/Volumes/SSD990/crypto-autoresearcher/.worktrees/ecrank-73275e-review-20260908"
R3 = os.path.join(ROOT, "experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R3-construct-n6/raw-result.json")
R4 = os.path.join(ROOT, "experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R4-construct-n6-replay/raw-result.json")

with open(R3) as f: r3 = json.load(f)
with open(R4) as f: r4 = json.load(f)

print("=== J3.2a r_height convention: r_height == max |numerator| of r (g(b) vector) ===")
from fractions import Fraction as Fr
bad = []
for i, rec in enumerate(r3["found"]):
    inst = rec["instance"]
    r = [Fr(x) for x in inst["r"]]
    maxnum = max(abs(x.numerator) for x in r)
    top_rh = rec["r_height"]
    inst_rh = inst["r_height"]
    if not (maxnum == top_rh == inst_rh):
        bad.append((i, inst["b_index"], maxnum, top_rh, inst_rh))
print("instances where r_height != max|num(r)|:", bad if bad else "NONE (all 28 consistent)")
print("n found:", len(r3["found"]))

print("\n=== J3.2b counts_per_H cumulative monotonicity from r_height ===")
H_levels = [100, 1000, 10000]
rh = [rec["r_height"] for rec in r3["found"]]
recomputed = {}
for H in H_levels:
    recomputed[H] = sum(1 for x in rh if x <= H)
print("recomputed counts_per_H:", recomputed)
print("recorded counts_per_H:  ", r3["counts_per_H"])
match = {int(k): v for k, v in r3["counts_per_H"].items()} == recomputed
print("match:", match)
mono = recomputed[100] <= recomputed[1000] <= recomputed[10000]
print("cumulative monotonic (100<=1000<=10000):", mono,
      "(%d <= %d <= %d)" % (recomputed[100], recomputed[1000], recomputed[10000]))

print("\n=== J3.2c feasibility fraction ===")
distinct_bi = set(rec["b_index"] for rec in r3["found"])
print("distinct b_index with >=1 instance:", len(distinct_bi), "(recorded feasible_tuples", r3["feasible_tuples"], ")")
print("feasibility_fraction recomputed = %d/10000 = %s (recorded %s)" % (
    len(distinct_bi), len(distinct_bi)/10000, r3["feasibility_fraction"]))
print("match:", len(distinct_bi) == r3["feasible_tuples"] == 20 and abs(r3["feasibility_fraction"] - 0.002) < 1e-12)

print("\n=== J3.2d near-miss ledger semantics ===")
print("near_miss_ledger (recorded):", r3["near_miss_ledger"])
print("near_miss_total (recorded):", r3["near_miss_total"])
zero_sol = 10000 - len(distinct_bi)
print("zero-solution b-tuples (10000 - feasible):", zero_sol)
print("=> ledger is EMPTY (0) while %d tuples have 0 solutions." % zero_sol)
print("   construct.py: near_miss only appended when a b-tuple has NO kept instance")
print("   BUT has a rejected rational-root candidate (r_zero / r_height / build fail).")
print("   A b-tuple whose quadratic has NO rational root contributes nothing to near_miss.")
print("   So near_miss_total=0 means: every zero-solution tuple had no rational root")
print("   (no near-miss candidate to record). Consistent with impl semantics;")
print("   NARROWER than a literal 'all tuples with 0 solutions' reading of the spec metric.")

print("\n=== J3.3 R3/R4 instance-list bit-identity (independent canonical hashing) ===")
def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))
r3_found = r3["found"]
r4_found = r4["found"]
h3 = hashlib.sha256(canon(r3_found).encode()).hexdigest()
h4 = hashlib.sha256(canon(r4_found).encode()).hexdigest()
print("sha256(canonical R3 found[]):", h3)
print("sha256(canonical R4 found[]):", h4)
print("bit-identical (canonical):", h3 == h4)
# also raw (unsorted) to catch ordering differences
h3r = hashlib.sha256(json.dumps(r3_found).encode()).hexdigest()
h4r = hashlib.sha256(json.dumps(r4_found).encode()).hexdigest()
print("bit-identical (as-serialized, order-sensitive):", h3r == h4r)
# counts_per_H after JSON (str keys)
print("R3 counts_per_H (json):", r3["counts_per_H"], " R4 counts_per_H (json):", r4["counts_per_H"],
      " equal:", r3["counts_per_H"] == r4["counts_per_H"])
# the in-memory iv2 flags recorded in R4
print("R4 recorded iv2_instance_list_identical:", r4.get("iv2_instance_list_identical"))
print("R4 recorded iv2_counts_identical:", r4.get("iv2_counts_identical"))
print("R4 recorded iv2_ops_r3:", r4.get("iv2_ops_r3"), " iv2_ops_r4:", r4.get("iv2_ops_r4"))
print("R3 ops:", r3["ops"], " R4 ops:", r4["ops"])
