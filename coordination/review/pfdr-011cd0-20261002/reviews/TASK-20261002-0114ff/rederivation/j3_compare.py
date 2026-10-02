#!/usr/bin/env python3
"""J3 after the seal: the sealed values against R16 (cells.jsonl, analysis.json).

TASK-20261002-0114ff. Reads the validator's own rederivation/outputs/cells.json
(whose sha256 is listed in the sealed section) and the producer's
runs/RUN-PFDR-011cd0-analysis/{cells.jsonl, analysis.json}.
Exactness: C_A, 3*C_R and 6*sum_s2 are integers and must be equal exactly;
curves_used exactly; kappa_rel, V, SD_null and z (floats derived from those
integers) must agree to 1e-9 relative (summation order only).
Applies the frozen outcome rule (FAM-1 z > t*, CARRY-1 z > t_carry) to the
validator's own z values with R16's t* and t_carry (RV-4).
Standard library only.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-pfdr011cd0-5753edf2e"
AN = WT + "/experiments/EXP-PFDR-011cd0/runs/RUN-PFDR-011cd0-analysis/"


def close(a, b, rel=1e-9):
    if a is None or b is None:
        return a is b
    return abs(a - b) <= rel * max(1.0, abs(a), abs(b))


def main():
    mine = json.load(open(os.path.join(HERE, "outputs", "cells.json")))
    prod = [json.loads(l) for l in open(AN + "cells.jsonl")]
    an = json.load(open(AN + "analysis.json"))
    pmap = {}
    for r in prod:
        pmap[(r["kind"], r["id"])] = r
    rows = []

    def cmp(kind, pid, m):
        p = pmap.get((kind, pid))
        if p is None:
            rows.append({"kind": kind, "id": pid, "status": "MISSING in cells.jsonl"})
            return
        d = {"kind": kind, "id": pid,
             "C_A": [m["C_A"], p["C_A"], m["C_A"] == p["C_A"]],
             "3C_R": [round(3 * m["C_R"]), round(3 * p["C_R"]), round(3 * m["C_R"]) == round(3 * p["C_R"])
                      and abs(3 * p["C_R"] - round(3 * p["C_R"])) < 1e-6],
             "V": [m["V"], p["V"], close(m["V"], p["V"])],
             "SD_null": [m["SD_null"], p["SD_null"], close(m["SD_null"], p["SD_null"])],
             "kappa_rel": [m["kappa_rel"], p["kappa_rel"], close(m["kappa_rel"], p["kappa_rel"])],
             "z": [m["z"], p["z"], close(m["z"], p["z"])],
             "curves_used": [m["curves_used"], p.get("curves_used"), m["curves_used"] == p.get("curves_used")]}
        if "sum_s2" in p:
            d["6sum_s2"] = [round(6 * m["sum_s2"]), round(6 * p["sum_s2"]), round(6 * m["sum_s2"]) == round(6 * p["sum_s2"])]
        d["all_equal"] = all(v[2] for k, v in d.items() if isinstance(v, list))
        extra = {k: v for k, v in p.items() if k not in ("kind", "id", "arm", "class", "m", "rungs", "C_A", "C_R", "V",
                                                          "SD_null", "kappa_rel", "z", "curves_used", "curves_design")}
        if extra:
            d["producer_extra_fields"] = extra
        rows.append(d)

    for pid, m in mine["Q2_FAM1_band"].items():
        cmp("fam1_band", pid, m)
    for pid, m in mine["Q2_known_null_band"].items():
        cmp("kn_band", pid, m)
    for pid, m in mine["Q2_per_rung_secondary"].items():
        kind = "kn_rung" if pid.startswith("known_null") else "fam1_rung"
        cmp(kind, pid, m)
    pl_ids = [k for (kd, k) in pmap if kd == "planted"]
    for cls in ("TT", "TB"):
        m = mine["Q3_planted"][f"planted_sub|{cls}3|band"]
        cands = [k for k in pl_ids if f"{cls}3" in k and "band" in k]
        for k in cands:
            cmp("planted", k, m)
    carry = [k for (kd, k) in pmap if kd == "carry"]
    for k in carry:
        cmp("carry", k, mine["Q4_CARRY1"])
    tstar, tcarry = an["t_star"], an["t_carry"]
    fam_exceed = sorted(k for k, v in mine["Q2_FAM1_band"].items() if v["z"] > tstar)
    fam_deficit = sorted(k for k, v in mine["Q2_FAM1_band"].items() if v["z"] < -tstar)
    carry_exceed = mine["Q4_CARRY1"]["z"] > tcarry
    famax = max(v["z"] for v in mine["Q2_FAM1_band"].values())
    out = {"t_star_R16": tstar, "t_carry_R16": tcarry,
           "own_FAM1_cells_z_gt_tstar": fam_exceed, "own_FAM1_cells_z_lt_minus_tstar": fam_deficit,
           "own_CARRY1_z": mine["Q4_CARRY1"]["z"], "own_CARRY1_z_gt_t_carry": carry_exceed,
           "own_family_max_z": famax, "R16_family_max_z": an["family_max_z"],
           "frozen_rule_on_own_values": ("O-CANDIDATE" if (fam_exceed or carry_exceed) else
                                         "no FAM-1 cell z > t* and CARRY-1 z <= t_carry (the O-NULL-BOUNDED structural condition, given the gates and controls owned by other joints)"),
           "R16_outcome_ids": an["outcome_ids"],
           "R16_fam1_cells_z_gt_tstar": an["fam1_cells_z_gt_tstar"],
           "R16_CC6": an["CC6"], "own_CC6_drops": mine["CC6_drops_listed"],
           "R16_PC_R_iii": an["PC_R"]["iii"],
           "own_PC_R_iii": {k: {x: mine["Q3_planted"][k][x] for x in ("planted_relations", "recovered_in_own_class_set")}
                            for k in mine["Q3_planted"]},
           "own_PC_R_iii_all_rungs": {k: (v if not isinstance(v, list) else len(v)) for k, v in mine["Q3_planted_all_rungs"].items()},
           "rows_compared": len(rows), "rows_all_equal": sum(1 for r in rows if r.get("all_equal")),
           "rows_not_equal": [r for r in rows if not r.get("all_equal")],
           "producer_cells_not_compared": sorted(f"{k[0]}|{k[1]}" for k in pmap if not any(
               r.get("kind") == k[0] and r.get("id") == k[1] for r in rows)),
           "comparisons": rows}
    json.dump(out, open(sys.argv[1], "w"), indent=1, sort_keys=True)
    print(json.dumps({k: v for k, v in out.items() if k not in ("comparisons", "rows_not_equal", "R16_CC6",
                                                                  "own_CC6_drops")}, indent=1)[:4000])
    print("not equal:", json.dumps(out["rows_not_equal"])[:3000])


if __name__ == "__main__":
    main()
