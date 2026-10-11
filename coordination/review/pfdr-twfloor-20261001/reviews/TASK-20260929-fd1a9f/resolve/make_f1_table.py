"""Per-key F1 table (completion gate): for every RS-1 key and every control, the
re-execution outcome, terminated_by and the disjoint checks. Reads only this
task's own resolve/ outputs. Writes resolve/f1-per-key.yaml."""
import json
import os

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
cmds = yaml.safe_load(open(os.path.join(HERE, "commands.yaml")))
rs1 = {tuple(k) for j in cmds["jobs"] for k in j["rs1_keys"]}
kt = {(r["panel"], r["bits"], r["curve"], r["m"], r["arm"], r["mode"]): r for r in map(json.loads, open(os.path.join(HERE, "k-table.jsonl")))}
rc = {}
for l in open(os.path.join(HERE, "row-comparison.jsonl")):
    r = json.loads(l)
    rc[tuple(r["key"])] = r
CHECKS = ["curve_params_equal_archived_row", "P_on_curve", "Q_on_curve", "N_prime", "N_P_is_O", "k_rule_P_eq_Q",
          "k_solver_eq_k_rule_mod_N", "k_solver_P_eq_Q", "k_bsgs_eq_k_rule"]


def role(k):
    if k in rs1:
        return "RS-1"
    twin_of = k[:5] + ("on",)
    if k[5] == "census" and twin_of in rs1:
        return "C-a census twin"
    if k[1] == 32 and k[2] == 0 and k[4] == "random_sub_r0":
        return "C-b"
    if k[0] == "j0" and k[4] == "j0_random_r0":
        return "C-c"
    if k[4] == "random_sub_r0" and k[3] == 3:
        return "known_log cap supplier"
    return "other"


rows = []
for k in sorted(kt, key=lambda k: (role(k) != "RS-1", k)):
    r = kt[k]
    c = r["checks"]
    bad = [x for x in CHECKS if c.get(x) is False]
    na = [x for x in CHECKS if c.get(x) is None]
    rows.append(f"{role(k)} | {' '.join(map(str, k))} | {rc[k]['outcome']} | {r['terminated_by']} | "
                f"k_solver {r['k_solver']} k_rule {r['k_rule']} k_bsgs {r['k_bsgs']} | "
                f"checks: {'ALL PASS' if not bad else 'FAIL ' + ','.join(bad)}" + (f" (n/a: {','.join(na)})" if na else ""))
rho = [f"j0 rho row | {' '.join(map(str, r['key']))} | {r['outcome']}" for r in rc.values() if len(r["key"]) == 4]
doc = {"f1_per_key": {"columns": "role | panel bits curve m arm mode | re-execution outcome | terminated_by | k values | disjoint checks",
                      "checks": CHECKS, "n": len(rows), "rows": rows, "j0_rho_rows": sorted(rho)}}
yaml.safe_dump(doc, open(os.path.join(HERE, "f1-per-key.yaml"), "w"), sort_keys=False, width=300)
print(len(rows), "instances;", len(rho), "rho rows;", sum(1 for x in rows if x.startswith("RS-1")), "RS-1")
