#!/usr/bin/env python3
"""TASK-20260923-5f9b82 (J7): NEGATIVE CONTROL on the comparator itself.

Agreement from a comparator that cannot disagree is not evidence. This script
re-runs the per-instance comparison logic of compare_j7.py (same item
definitions, same sources) under deliberately WRONG inputs, and requires it to
report disagreements:

  N1  reference labels permuted within each arm (REF-a->U3, REF-b->U1,
      REF-c->U2, REF-d->S2, REF-e->S1)
  N2  target map off by one draw (position p -> run idx p+1; 1000 -> 1), the classic
      0/1-based error
  N3  target map off by ten (position p -> run idx p-10; position 10 -> idx 1000)
  N4  one run match flag flipped in memory (position 500, U2, T_rank)
  N5  one run target hash altered in memory (position 10, h_strict)
  N6  one re-derived first-64 rank-increment flag flipped in memory (REF-a, step 5)

Expected: N1-N3 produce many disagreements; N4-N6 produce EXACTLY one each.
Positive control P0: the true mapping produces zero.

Run from the repository root with python3 -B. Reads the same archived files as
compare_j7.py (it relies on compare_j7.py's CP-1 verification having passed).
Writes checks/comparator_negative_control.json only.
"""
import sys
sys.dont_write_bytecode = True
import copy
import gzip
import json

REV = "coordination/review/certbin-20260923-c51f07"
J6 = f"{REV}/reviews/TASK-20260923-7a2cd4"
ME = f"{REV}/reviews/TASK-20260923-5f9b82"
RUN = "experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05"
GRAN_RUN = {"T_rank": "rank", "T_set": "set", "T_strict": "strict", "T_ops": "ops"}
HASH_RUN = {"T_rank": "h_rank", "T_set": "h_set", "T_strict": "h_strict", "T_ops": "h_ops"}

rd = json.load(open(f"{J6}/rederivation.json"))
key = json.load(open(f"{REV}/blind-inputs-key.json"))
refs_run = json.load(open(f"{RUN}/references.json"))["F-S3"]["references"]
tgt_run = {}
for line in gzip.open(f"{RUN}/targets-F-S3.jsonl.gz", "rt"):
    r = json.loads(line)
    if r["D"] == 4:
        tgt_run[r["idx"]] = r
cmp_prev = json.load(open(f"{ME}/comparison.json"))
run64_true = {lab: [s["k"][1] for s in v["items"]["first-64 nonzero-a_k list (k, a_k0, a_k, increases_rank)"]["per_step"]]
              for lab, v in cmp_prev["unsat_reference_affine_replay"].items()}
run64_flags = {lab: [s["increases_rank"][1] for s in v["items"]["first-64 nonzero-a_k list (k, a_k0, a_k, increases_rank)"]["per_step"]]
               for lab, v in cmp_prev["unsat_reference_affine_replay"].items()}


def core(REFMAP, TGTMAP, tgt_run, refs_run, rd):
    dis = {}

    def chk(name, a, b):
        if a != b:
            dis[name] = dis.get(name, 0) + 1

    for lab, U in REFMAP.items():
        q1 = rd["Q1"]["references"][lab]
        q2 = rd["Q2"]["references"][lab]
        r4 = refs_run[U]["D4"]
        chk("ref.x_R", q1["x_R"], refs_run[U]["x_R"])
        chk("ref.s", q1["s_route_A_rootfinding"], refs_run[U]["s"])
        chk("ref.arm", q1["arm"], refs_run[U]["arm"])
        chk("ref.rank_4", q2["rank_4"], r4["rank"])
        chk("ref.Z_4", q2["Z_4_size"], r4["Z_size"])
        chk("ref.one_in_R4", q2["one_in_R4"], r4["one_in_R"])
        chk("ref.T_strict_content", rd["Q3"]["reference_content"][lab]["T_strict"], r4["T_strict"])
        for g in HASH_RUN:
            chk(f"ref.hash_{g}", rd["Q3"]["hashes"]["references"][lab][g], r4[HASH_RUN[g]])
    for pos, idx in TGTMAP.items():
        t = tgt_run[idx]
        q1 = rd["Q1"]["targets"][pos]
        q2 = rd["Q2"]["targets"][pos]
        chk("tgt.x_R", q1["x_R"], t["x_R"])
        chk("tgt.s", q1["s_route_A_rootfinding"], t["s"])
        chk("tgt.arm", q1["arm"], t["stratum"])
        chk("tgt.rank_4", q2["rank_4"], t["rank"])
        chk("tgt.one_in_R4", q2["one_in_R4"], t["one_in_R"])
        chk("tgt.Z_4", q2["Z_4_size"], t["Z_size"])
        for g in HASH_RUN:
            chk(f"tgt.hash_{g}", rd["Q3"]["hashes"]["targets"][pos][g], t[HASH_RUN[g]])
        for lab, U in REFMAP.items():
            for g in GRAN_RUN:
                chk(f"tgt.match_{g}", rd["Q3"]["match_flags_target_vs_reference"][pos][lab][g],
                    t["refs"][U]["match"][GRAN_RUN[g]])
    for lab in rd["Q5"]["unsat_references"]:
        rd64 = [s["increases_rank"] for s in rd["Q6"]["per_reference"][lab]["first_64_nonzero"]]
        for a, b in zip(rd64, run64_flags[lab]):
            chk("q6.first64_increases_rank", a, b)
    return {"total": sum(dis.values()), "by_item": dis}


TRUE_REF = key["references"]
TRUE_TGT = {p: int(i) for p, i in key["targets"].items()}
out = {"schema": "certbin.j7_comparator_negative_control.v1", "task_id": "TASK-20260923-5f9b82", "cases": {}}

out["cases"]["P0_true_mapping"] = {"expected": "0", **core(TRUE_REF, TRUE_TGT, tgt_run, refs_run, rd)}

perm = {"REF-a": "U3", "REF-b": "U1", "REF-c": "U2", "REF-d": "S2", "REF-e": "S1"}
out["cases"]["N1_reference_labels_permuted_within_arm"] = {"expected": "many", **core(perm, TRUE_TGT, tgt_run, refs_run, rd)}

off1 = {p: (i + 1 if i < 1000 else 1) for p, i in TRUE_TGT.items()}
out["cases"]["N2_target_map_off_by_one"] = {"expected": "many", **core(TRUE_REF, off1, tgt_run, refs_run, rd)}

off10 = {p: (i - 10 if i > 10 else 1000) for p, i in TRUE_TGT.items()}
out["cases"]["N3_target_map_off_by_ten"] = {"expected": "many", **core(TRUE_REF, off10, tgt_run, refs_run, rd)}

t4 = copy.deepcopy(tgt_run)
t4[500]["refs"]["U2"]["match"]["rank"] = not t4[500]["refs"]["U2"]["match"]["rank"]
out["cases"]["N4_one_match_flag_flipped"] = {"expected": "exactly 1", **core(TRUE_REF, TRUE_TGT, t4, refs_run, rd)}

t5 = copy.deepcopy(tgt_run)
h = t5[10]["h_strict"]
t5[10]["h_strict"] = h[:-1] + ("0" if h[-1] != "0" else "1")
out["cases"]["N5_one_target_hash_altered"] = {"expected": "exactly 1", **core(TRUE_REF, TRUE_TGT, t5, refs_run, rd)}

rd6 = copy.deepcopy(rd)
s = rd6["Q6"]["per_reference"]["REF-a"]["first_64_nonzero"][5]
s["increases_rank"] = not s["increases_rank"]
out["cases"]["N6_one_rank_increment_flag_flipped"] = {"expected": "exactly 1", **core(TRUE_REF, TRUE_TGT, tgt_run, refs_run, rd6)}

ok = (out["cases"]["P0_true_mapping"]["total"] == 0
      and all(out["cases"][k]["total"] > 100 for k in ("N1_reference_labels_permuted_within_arm",
                                                       "N2_target_map_off_by_one", "N3_target_map_off_by_ten"))
      and all(out["cases"][k]["total"] == 1 for k in ("N4_one_match_flag_flipped", "N5_one_target_hash_altered",
                                                      "N6_one_rank_increment_flag_flipped")))
out["control_passed"] = ok
with open(f"{ME}/checks/comparator_negative_control.json", "w") as f:
    json.dump(out, f, indent=1)
    f.write("\n")
for k, v in out["cases"].items():
    print(k, "expected", v["expected"], "got", v["total"], v["by_item"] if v["total"] < 40 else sorted(v["by_item"].items())[:12])
print("control_passed:", ok)
