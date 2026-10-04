#!/usr/bin/env python3
"""V3 step (1) diff, corrected shape.

Compares my independent per-cell reduction (v3_reduce.json per_cell_table)
against summary.json's `cells` block, matching the two different nestings.

summary.json: cells[cell][label]["<engine>_<config>_wall_s" | "..._conflicts" | "..._n"]
mine:         per_cell_table["<cell>/<label>"]["<engine>/<config>"] = {median_wall_s, median_conflicts, n_finished}
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
RUN = pathlib.Path("/workspace/experiments/EXP-ICPERF-66fd51/runs/RUN-ICPERF-305ca3")

mine = json.load(open(HERE / "v3_reduce.json"))["per_cell_table"]
theirs = json.load(open(RUN / "summary.json"))["cells"]


# summary.json abbreviates some engine/config pairs; map its prefix to mine.
ALIAS = {
    "cms_xor": "cryptominisat5/cnf_xor",
    "cms_pure_cnf": "cryptominisat5/pure_cnf",
    "m2_f4": "macaulay2/f4",
    "singular": "singular/std",
    "cadical_pure_cnf": "cadical/pure_cnf",
    "minisat_pure_cnf": "minisat/pure_cnf",
}


def close(a, b):
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    if a == b:
        return True
    return abs(a - b) <= 1e-9 * max(1.0, abs(a), abs(b))


rows = []
n_checked = n_match = 0
for cell, labels in theirs.items():
    for label, flat in labels.items():
        mykey = f"{cell}/{label}"
        myrow = mine.get(mykey, {})
        # reconstruct their flat keys
        for k, v in flat.items():
            if k.endswith("_wall_s"):
                base, field = k[: -len("_wall_s")], "median_wall_s"
            elif k.endswith("_conflicts"):
                base, field = k[: -len("_conflicts")], "median_conflicts"
            elif k.endswith("_n"):
                base, field = k[: -len("_n")], "n_finished"
            else:
                rows.append((cell, label, k, "UNPARSED_KEY", v, None, False))
                continue
            if base in ALIAS:
                mykey_ec = ALIAS[base]
            else:
                eng, _, cfg = base.partition("_")
                mykey_ec = f"{eng}/{cfg}"
            mysub = myrow.get(mykey_ec)
            if mysub is None:
                rows.append((cell, label, k, base, v, "MISSING_IN_MINE", False))
                continue
            mv = mysub.get(field)
            ok = close(mv, v)
            n_checked += 1
            n_match += int(ok)
            if not ok:
                rows.append((cell, label, k, base, v, mv, False))

# anything in mine that summary.json omits entirely
missing_in_theirs = []
for mykey, sub in mine.items():
    cell, _, label = mykey.partition("/")
    flat = theirs.get(cell, {}).get(label, {})
    rev = {v: k for k, v in ALIAS.items()}
    for ec, vals in sub.items():
        eng, _, cfg = ec.partition("/")
        base = rev.get(ec, f"{eng}_{cfg}")
        if f"{base}_wall_s" not in flat:
            missing_in_theirs.append(
                {
                    "cell": cell,
                    "label": label,
                    "engine_config": ec,
                    "my_median_wall_s": vals.get("median_wall_s"),
                    "my_n_finished": vals.get("n_finished"),
                    "my_n_planned": vals.get("n_planned"),
                }
            )

out = {
    "n_values_checked": n_checked,
    "n_values_matching": n_match,
    "mismatches": [
        {
            "cell": r[0],
            "label": r[1],
            "summary_key": r[2],
            "summary_value": r[4],
            "my_value": r[5],
        }
        for r in rows
    ],
    "engine_configs_present_in_my_reduction_but_absent_from_summary_cells": missing_in_theirs,
}
print(json.dumps(out, indent=1))
json.dump(out, open(HERE / "v3_celldiff.json", "w"), indent=1, sort_keys=True)
