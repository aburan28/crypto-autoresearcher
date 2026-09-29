#!/usr/bin/env python3
"""
Tail check 1 (contract tail_checks[0]): "The single cheapest member
observed on the group-operation axis is checked against the seed
dispersion band explicitly: if it sits outside, it is re-run under 16
FRESH seeds before any statement is made about it."

This is applied identically, as a post-processing addendum, to every run
in this census (not selectively to inconvenient results): it locates the
single cheapest generic (non-special-j) class member by group_ops, and if
it lies outside the frozen base-curve seed band, re-solves that SAME
member under all 16 declared replication seeds (run_census.SEEDS), which
are "fresh" relative to that member's original single-seed measurement
(PRIMARY_SEED only). The addendum is appended to raw-result.json under
"tail_check_1_rerun" -- the original per-seed record that triggered this
is left untouched (immutability of the raw per-seed observation), and
nothing already reported is overwritten.
"""
import json
import sys
import time

sys.path.insert(0, "/home/user/crypto-autoresearcher/experiments/EXP-ISOU-2ac81f/implementation")

import run_census as rc


def apply(run_dir):
    path = f"{run_dir}/raw-result.json"
    with open(path) as f:
        raw = json.load(f)

    members = [r for r in raw["member_records"] if r["role"] == "class_member"
               and r.get("contributes_cost_datum") and not r.get("special_j")]
    if not members or not raw.get("seed_dispersion_band"):
        raw["tail_check_1_rerun"] = {"applicable": False, "reason": "no generic members or no seed band"}
    else:
        cheapest = min(members, key=lambda r: r["group_ops"])
        sb = raw["seed_dispersion_band"]
        lo, hi = sb["mean"] - 3 * sb["stdev"], sb["mean"] + 3 * sb["stdev"]
        outside = not (lo <= cheapest["group_ops"] <= hi)
        entry = {
            "applicable": True,
            "cheapest_member_vertex_id": cheapest["vertex_id"],
            "original_group_ops": cheapest["group_ops"],
            "original_seed": cheapest["seed"],
            "seed_band_lo": lo, "seed_band_hi": hi,
            "outside_band_triggered_rerun": outside,
        }
        if outside:
            p, a, b, N = cheapest["p"], cheapest["a"], cheapest["b"], cheapest["N"]
            k = raw["dlp_instance"]["k"]
            rerun_ops = []
            mult_cache = {}
            for sd in rc.SEEDS:
                P, Q, res, cert = rc.solve_member(p, a, b, N, k, sd, time.time)
                rerun_ops.append({
                    "seed": sd, "status": res.status, "group_ops": res.group_ops,
                    "certificate_verified": cert["verified"] if cert else None,
                })
            solved_ops = [r["group_ops"] for r in rerun_ops if r["status"] == "solved" and r["certificate_verified"]]
            entry["rerun_16_seeds"] = rerun_ops
            if solved_ops:
                import statistics
                entry["rerun_mean"] = statistics.mean(solved_ops)
                entry["rerun_still_outside_original_band"] = not (lo <= entry["rerun_mean"] <= hi)
        raw["tail_check_1_rerun"] = entry

    with open(path, "w") as f:
        json.dump(raw, f, indent=2, default=str)
    print(f"{run_dir}: tail_check_1_rerun = {raw['tail_check_1_rerun'].get('applicable')}, "
          f"triggered={raw['tail_check_1_rerun'].get('outside_band_triggered_rerun')}")


if __name__ == "__main__":
    for d in sys.argv[1:]:
        apply(d)
