"""J6: the narrowest true statement per FAM-1 cell, from the archived R16 analysis.json (A_INT,
calibrated p) and cells.jsonl (per-rung cells), beside this reviewer's recomputations
(attacks/j4/out/aint.json, tstar.json; attacks/ptm/out/ptm.json). No new statistic is computed
here; it is a table writer.
Command: nice -n 19 $PY attacks/j6/j6_table.py --out attacks/j6/out/cell-statements.json
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "j4"))
import j4lib as L  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    an = json.load(open(os.path.join(L.EXP, "runs", "RUN-PFDR-011cd0-analysis", "analysis.json")))
    cells = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(L.EXP, "runs", "RUN-PFDR-011cd0-analysis", "cells.jsonl"))}
    own = json.load(open(os.path.join(HERE, "..", "j4", "out", "aint.json")))
    ts = json.load(open(os.path.join(HERE, "..", "j4", "out", "tstar.json")))
    ptm = json.load(open(os.path.join(HERE, "..", "ptm", "out", "ptm.json")))
    tprod = an["t_star"]
    n_curves = {}
    rows = []
    for (cls, m) in L.FAM1_CM:
        for arm in L.FAM1_ARMS:
            cid = f"{arm}|{cls}{m}|band"
            ai = an["A_INT"][cid]
            c = cells[cid]
            o = own["A_INT_own"][cid]
            tgt = L.TARGET[(cls, m)]
            ub = ai["upper95_one_sided"]
            lo2, hi2 = ai["ci95"]
            xr = ai["X_rel_realised"]["X_rel"]
            per_rung = {b: cells[f"{arm}|{cls}{m}|{b}"] for b in (30, 32)}
            flags = []
            if xr is not None and xr <= tgt:
                flags.append("X_rel_meets_target")
            else:
                flags.append("X_rel_MISSES_target")
            if ub > tgt:
                flags.append("UPPER_BOUND_ABOVE_TARGET")
            if ub < 1.0:
                flags.append("UPPER_BOUND_BELOW_1 (deficit side; no bound reading below 1)")
            if lo2 > 1.0:
                flags.append("TWO_SIDED_95_EXCLUDES_1_FROM_BELOW (per cell, multiplicity-unadjusted)")
            if hi2 < 1.0:
                flags.append("TWO_SIDED_95_EXCLUDES_1_FROM_ABOVE (per cell, multiplicity-unadjusted)")
            if any(abs(per_rung[b]["z"]) > tprod for b in per_rung):
                flags.append("A_PER_RUNG_CELL_HAS_ABS_Z_GT_TSTAR (not decision-bearing, CC-10)")
            pc = an["calibrated_p_fam1_band"][cid]
            stmt = (f"{arm}, {cls} m {m}, 30-32 bits ({c['curves_used']} curves), this mitm engine at default arity "
                    f"and min_fill, generated prime-order curves c >= 10: relation-level kappa_rel = {ai['kappa_rel']:.4f}, "
                    f"two-sided 95% [{lo2:.4f}, {hi2:.4f}], one-sided 95% upper bound {ub:.4f}; z = {c['z']:.3f} <= t* "
                    f"= {tprod:.3f} (per-cell calibrated p {pc:.4f}; not an excursion of the family-wise rule). "
                    f"Achieved detection limit X_rel = {xr} against target {tgt}.")
            if ub > tgt:
                stmt += (f" The data do NOT exclude a relation-level excess of kappa = {tgt} (the upper bound "
                         f"{ub:.3f} exceeds it); this cell cannot carry a bound-based 'excess below target' reading.")
            if ub < 1.0:
                stmt += (" The count lies in the lower tail of the null (upper bound below 1); the defensible "
                         "reading is 'no excess detected', not 'excess bounded below 1'.")
            if (cls, m) == ("SS", 4):
                stmt += " [" + L.TA1_LABEL + "]"
            rows.append({"cell": cid, "kappa_rel": ai["kappa_rel"], "ci95": ai["ci95"], "upper95": ub,
                         "z": c["z"], "calibrated_p": pc, "X_rel_producer": xr,
                         "X_rel_own": o["X_rel_own"]["X_rel_frozen"], "upper95_own_onesided": o["upper95_onesided_reading"],
                         "target": tgt, "flags": flags,
                         "per_rung": {str(b): {"kappa_rel": per_rung[b]["kappa_rel"], "z": per_rung[b]["z"]} for b in per_rung},
                         "narrowest_statement": stmt})
    meets_xrel = [r["cell"] for r in rows if "X_rel_meets_target" in r["flags"]]
    meets_bound = [r["cell"] for r in rows if "X_rel_meets_target" in r["flags"] and "UPPER_BOUND_ABOVE_TARGET" not in r["flags"]
                   and not any(f.startswith("UPPER_BOUND_BELOW_1") for f in r["flags"])]
    carry = an["A_INT"]["CARRY-1|subgroup|TT3|28"]
    out = {"t_star_producer": tprod, "cells": rows,
           "cells_meeting_target_by_X_rel": meets_xrel,
           "cells_meeting_target_by_X_rel_AND_with_upper_bound_in_[1,target]": meets_bound,
           "CARRY_1": {"kappa_rel": carry["kappa_rel"], "ci95": carry["ci95"], "upper95": carry["upper95_one_sided"],
                       "z": an["CARRY_1"]["z"], "t_carry": an["t_carry"], "X_rel": carry["X_rel_realised"]["X_rel"],
                       "EV_PFDR_1faf10_OBS_8_bound_pair_units": "1.10-1.14 (Stage R, pair units)",
                       "EV_PFDR_1faf10_discovery_relation_kappa": 1.196},
           "per_rung_abs_z_gt_tstar": an["A_TAIL"]["per_rung_abs_z_gt_tstar"],
           "per_rung_multiplicity_check": ptm.get("per_rung_multiplicity")}
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    L.jdump(a.out, out)
    for r in rows:
        print(r["cell"], round(r["kappa_rel"], 4), round(r["upper95"], 4), r["X_rel_producer"], r["X_rel_own"], r["flags"])
    print("meets X_rel:", len(meets_xrel), "meets X_rel and bound:", len(meets_bound))


if __name__ == "__main__":
    main()
