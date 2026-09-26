#!/usr/bin/env python3
"""CP-6 caveat support for TASK-20260926-f50294: for every compared item of
cp2_compare.json, the number of distinct values it takes over the pool and
within each arm. An item that takes ONE value on every system (or one value
within every arm) sits at a floor or ceiling and is weak evidence about either
implementation: two implementations that both always output that value agree
without exercising the code path. Also: the D-2 space-dimension identity on
the re-deriver's independent numbers, and the kernel-dimension distribution of
the whole N-ELL19 arm (record-level; bears on re-deriver AMB-7).

Usage: python3 cp2_floor_ceiling.py <worktree_root> <cp2_json> <out_json>
"""
import gzip
import json
import os
import sys
from collections import Counter, defaultdict


def main():
    root, cp2p, outp = sys.argv[1:4]
    os.chdir(root)
    d = json.load(open(cp2p))
    red = json.load(open("coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-f0736e/rederivation.json"))["systems"]
    vals = defaultdict(list)
    per_arm = defaultdict(lambda: defaultdict(set))
    for lab, s in d["per_system"].items():
        for it, row in s["items"].items():
            v = row["run"] if row["run"] is not None else row["rederiver"]
            if v is None:
                continue
            j = json.dumps(v, sort_keys=True)
            vals[it].append(j)
            per_arm[it][s["arm"]].add(j)
    table = {}
    for it, vs in sorted(vals.items()):
        c = Counter(vs)
        arms = {a: len(x) for a, x in per_arm[it].items()}
        const_all = len(c) == 1
        const_within_arms = all(n == 1 for n in arms.values())
        table[it] = {
            "systems": len(vs),
            "distinct_values": len(c),
            "top_values": [[json.loads(k) if len(k) < 80 else k[:80] + "...", n] for k, n in c.most_common(4)],
            "distinct_per_arm": arms,
            "floor_or_ceiling": "SAME VALUE ON EVERY SYSTEM" if const_all else (
                "SAME VALUE WITHIN EVERY ARM (saturated per arm)" if const_within_arms else "varies"),
        }
    # D-2 space identity: dim(rowspace(M_4) + ell*B_<=3) (direct, 20 vars) == rank R'_4 (19 vars) + 1160
    d2 = Counter()
    for lab, r in red.items():
        q4 = r["Q4"]
        if q4.get("applicable") and q4.get("ell_route_space_dim") is not None:
            d2[q4["ell_route_space_dim"] == q4["rank_R4"] + 1160] += 1
    kd = Counter()
    with gzip.open("experiments/EXP-CERTBIN-060020/runs/RUN-CERTBIN-a3fc60/closures.jsonl.gz", "rt") as fh:
        for line in fh:
            x = json.loads(line)
            if x["arm"] == "N-ELL19":
                kd[(x["role"], x["rc_b"].get("kernel_dim"), x["rc_b"].get("c_rule"))] += 1
    out = {"per_item": table,
           "D-2_space_identity_rederiver (dim(M_4 + ell*B_<=3) == rank R'_4 + 1160)": {str(k): v for k, v in d2.items()},
           "N-ELL19_whole_arm_kernel_dim (run records)": {str(k): v for k, v in kd.items()}}
    json.dump(out, open(outp, "w"), indent=1)
    for it, t in table.items():
        print(f"{t['floor_or_ceiling'][:28]:28s} {t['distinct_values']:3d}  {it}")
    print(out["D-2_space_identity_rederiver (dim(M_4 + ell*B_<=3) == rank R'_4 + 1160)"])
    print(out["N-ELL19_whole_arm_kernel_dim (run records)"])


if __name__ == "__main__":
    main()
