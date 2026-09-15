"""V3 step (1) continued: diff the validator's own reduction against
summary.json, value by value."""
from __future__ import annotations

import json
import os

RUN = "/workspace/experiments/EXP-ICPERF-66fd51/runs/RUN-ICPERF-305ca3"
OUT = os.path.dirname(os.path.abspath(__file__))


def close(a, b, tol=5e-5):
    if a is None or b is None:
        return a is None and b is None
    if b == 0:
        return abs(a - b) < tol
    return abs(a - b) <= tol * max(1.0, abs(b))


def walk(prefix, mine, theirs, diffs, same):
    if isinstance(theirs, dict) and isinstance(mine, dict):
        for k in sorted(set(theirs) | set(mine)):
            walk(f"{prefix}.{k}", mine.get(k), theirs.get(k), diffs, same)
        return
    if isinstance(theirs, (int, float)) and isinstance(mine, (int, float)) \
            and not isinstance(theirs, bool) and not isinstance(mine, bool):
        if close(mine, theirs):
            same.append(prefix)
        else:
            diffs.append({"path": prefix, "mine": mine, "summary_json": theirs,
                          "rel": (mine - theirs) / theirs if theirs else None})
        return
    if mine != theirs:
        diffs.append({"path": prefix, "mine": mine, "summary_json": theirs})
    else:
        same.append(prefix)


def main():
    sj = json.load(open(os.path.join(RUN, "summary.json")))
    mine = json.load(open(os.path.join(OUT, "v3_reduce.json")))

    report = {"summary_json_top_keys": sorted(sj.keys())}

    # ---- per-cell medians -------------------------------------------------
    diffs, same = [], []
    their_cells = sj.get("cells", {})
    for key, mycell in mine["per_cell_table"].items():
        tc = their_cells.get(key)
        if tc is None:
            diffs.append({"path": f"cells.{key}", "mine": "present",
                          "summary_json": "absent"})
            continue
        for k, v in tc.items():
            if not isinstance(v, (int, float)) or isinstance(v, bool):
                continue
            # map summary.json's names onto mine
            mapped = MAP.get(k)
            if mapped is None:
                continue
            eng_cfg, field = mapped
            m = mycell.get(eng_cfg, {}).get(field)
            if close(m, v):
                same.append(f"cells.{key}.{k}")
            else:
                diffs.append({"path": f"cells.{key}.{k}", "mine": m,
                              "summary_json": v,
                              "rel": ((m - v) / v) if (m is not None and v) else None})
    report["per_cell_median_diffs"] = diffs
    report["per_cell_medians_matching"] = len(same)
    report["per_cell_medians_checked"] = len(same) + len(diffs)

    # ---- predictions ------------------------------------------------------
    report["summary_json_predictions"] = sj.get("predictions")
    report["my_headline"] = mine["headline"]

    with open(os.path.join(OUT, "v3_diff.json"), "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)

    print(f"per-cell medians checked {report['per_cell_medians_checked']}, "
          f"matching {report['per_cell_medians_matching']}, "
          f"differing {len(diffs)}")
    for d in diffs:
        print("  DIFF", d)
    print()
    print("summary.json top-level keys:", sorted(sj.keys()))
    print()
    print("cells keys of one cell:", sorted(their_cells.get("n15l5/S", {}).keys()))


MAP = {
    "wdsat_default_wall_s": ("wdsat/default", "median_wall_s"),
    "wdsat_default_conflicts": ("wdsat/default", "median_conflicts"),
    "wdsat_core_order_wall_s": ("wdsat/core_order", "median_wall_s"),
    "wdsat_core_order_conflicts": ("wdsat/core_order", "median_conflicts"),
    "wdsat_symmetry_wall_s": ("wdsat/symmetry", "median_wall_s"),
    "wdsat_symmetry_conflicts": ("wdsat/symmetry", "median_conflicts"),
    "wdsat_gauss_elim_wall_s": ("wdsat/gauss_elim", "median_wall_s"),
    "wdsat_gauss_elim_conflicts": ("wdsat/gauss_elim", "median_conflicts"),
    "wdsat_noncore_first_wall_s": ("wdsat/noncore_first", "median_wall_s"),
    "wdsat_noncore_first_conflicts": ("wdsat/noncore_first", "median_conflicts"),
    "wdsat_null_wall_s": ("wdsat/default_on_null_object", "median_wall_s"),
    "wdsat_null_conflicts": ("wdsat/default_on_null_object", "median_conflicts"),
    "cms_cnf_xor_wall_s": ("cryptominisat5/cnf_xor", "median_wall_s"),
    "cms_cnf_xor_conflicts": ("cryptominisat5/cnf_xor", "median_conflicts"),
    "cms_pure_cnf_wall_s": ("cryptominisat5/pure_cnf", "median_wall_s"),
    "cadical_pure_cnf_wall_s": ("cadical/pure_cnf", "median_wall_s"),
    "minisat_pure_cnf_wall_s": ("minisat/pure_cnf", "median_wall_s"),
    "m2_f4_wall_s": ("macaulay2_F4_ZZ2_fieldeqs/grevlex", "median_wall_s"),
    "singular_std_wall_s": ("singular_std_GF2_fieldeqs/dp", "median_wall_s"),
}

if __name__ == "__main__":
    main()
