#!/usr/bin/env python3
"""R3 attack-plan step (4): deletion-derived inputs, one clause per prediction made
unevaluable; plus one injection case for P2/P5 so `compose` is exercised on a MIXED
set (some clauses evaluated, some not). Runs the REPAIRED summary.py (copied to /tmp)
and, as a control, the FROZEN summary.py on the same derived inputs."""
import json, shutil, subprocess, sys
from pathlib import Path

R3 = Path("/tmp/val3f4b52/r3")
SRC = R3 / "repaired/results.jsonl"
REP = "/workspace/experiments/EXP-ICPERF-e21835/code/summary.py"
FRO = "/workspace/experiments/EXP-ICPERF-66fd51/code/summary.py"
rows = [json.loads(l) for l in open(SRC) if l.strip()]

def run(name, keep, inject=()):
    res = {}
    for tag, script in (("repaired", REP), ("frozen", FRO)):
        d = R3 / "del" / name / tag
        d.mkdir(parents=True, exist_ok=True)
        kept = [r for r in rows if keep(r)] + list(inject)
        (d / "results.jsonl").write_text("\n".join(json.dumps(r) for r in kept) + "\n")
        p = subprocess.run([sys.executable, script, str(d)], capture_output=True, text=True)
        s = json.load(open(d / "summary.json"))
        res[tag] = {"rc": p.returncode, "stderr_tail": p.stderr[-300:], "n_rows": len(kept),
                    "predictions": {k: {"holds": v.get("holds"), "unevaluable": v.get("unevaluable", "FIELD_ABSENT"),
                                        "n_clauses": v.get("n_clauses"), "n_evaluated": v.get("n_evaluated")}
                                    for k, v in s["predictions"].items()}}
        res[tag]["full"] = s["predictions"]
    return res

cases = {}
# P3: remove every noncore_first row of n17l6/S -> P3 clause n17l6/S/noncore... unevaluable
cases["P3_del_noncore_n17l6S"] = run("P3_del_noncore_n17l6S",
    lambda r: not (r.get("engine") == "wdsat" and r.get("config") == "noncore_first" and r.get("cell") == "n17l6" and r.get("label") == "S"))
# P3 variant: remove every core_order row -> core_order_identity unevaluable (the FIRST clause, the one compose sees first)
cases["P3_del_all_core_order"] = run("P3_del_all_core_order",
    lambda r: not (r.get("engine") == "wdsat" and r.get("config") == "core_order"))
# P4: remove every gauss_elim row of n15l5/S -> P4 clause n15l5/S unevaluable
cases["P4_del_gauss_n15l5S"] = run("P4_del_gauss_n15l5S",
    lambda r: not (r.get("engine") == "wdsat" and r.get("config") == "gauss_elim" and r.get("cell") == "n15l5" and r.get("label") == "S"))
# P5: remove every cryptominisat5 cnf_xor row of n15l5 -> P5 clause n15l5/cms_xor_U_over_S_conflicts unevaluable
cases["P5_del_cmsxor_n15l5"] = run("P5_del_cmsxor_n15l5",
    lambda r: not (r.get("engine") == "cryptominisat5" and r.get("config") == "cnf_xor" and r.get("cell") == "n15l5"))
# P6: remove every null-object row of n15l5 -> P6 cell n15l5 unevaluable (n19l6 already is)
cases["P6_del_null_n15l5"] = run("P6_del_null_n15l5",
    lambda r: not (r.get("engine") == "wdsat" and r.get("config") == "default_on_null_object" and r.get("cell") == "n15l5"))
# P6 variant: make n19l6 EVALUABLE by deleting the censored null rows and injecting one finished null row,
# so that P6 becomes a fully-evaluated prediction -> holds must become a boolean.
inj = [{"phase": "A", "instance": "n19l6-1-S", "cell": "n19l6", "label": "S", "engine": "wdsat",
        "config": "default_on_null_object", "status": "SAT", "conflicts": 10**9, "wall_s": 100.0}]
cases["P6_inject_finished_null_n19l6"] = run("P6_inject_finished_null_n19l6",
    lambda r: not (r.get("engine") == "wdsat" and r.get("config") == "default_on_null_object" and r.get("cell") == "n19l6"), inj)
# P2 + P5 mixed: inject finished Macaulay2 rows for n15l5 S and U (2 rows each) with engine_cpu_s,
# so P2 has 2 evaluated + 10 unevaluable clauses, and P5's Groebner clause is evaluated on n15l5 only.
m2 = []
for lab, ids in (("S", (1, 2)), ("U", (11, 12))):
    for i in ids:
        m2.append({"phase": "C", "instance": f"n15l5-{i}-{lab}", "cell": "n15l5", "label": lab,
                   "engine": "macaulay2_F4_ZZ2_fieldeqs", "config": "grevlex", "status": "consistent_proper_ideal",
                   "wall_s": 49.0, "cpu_s": 165.0, "engine_cpu_s": 46.5, "gb_size": 43, "maxdeg_gb": 2, "unit_ideal": False})
cases["P2P5_inject_m2_n15l5"] = run("P2P5_inject_m2_n15l5", lambda r: True, m2)

out = {}
for name, res in cases.items():
    out[name] = {tag: res[tag]["predictions"] for tag in ("repaired", "frozen")}
    out[name]["rc"] = {tag: res[tag]["rc"] for tag in ("repaired", "frozen")}
    out[name]["stderr"] = {tag: res[tag]["stderr_tail"] for tag in ("repaired", "frozen")}
json.dump({k: {t: v[t] for t in ("repaired", "frozen")} | {"full_repaired": cases[k]["repaired"]["full"]} for k, v in out.items()},
          open(R3 / "deletions_out.json", "w"), indent=1, default=str)
for name, res in out.items():
    print("=" * 100); print(name, "rc", res["rc"], "stderr", res["stderr"])
    for tag in ("repaired", "frozen"):
        print(f"  [{tag}]")
        for k, v in res[tag].items():
            print(f"     {k}: holds={v['holds']} unevaluable={v['unevaluable']} n_clauses={v['n_clauses']} n_eval={v['n_evaluated']}")
# show the specific clause records of interest
def show(name, pred, key):
    full = cases[name]["repaired"]["full"][pred]
    print(f"--- {name} {pred} {key}:", json.dumps(full["cells"].get(key), default=str))
show("P3_del_noncore_n17l6S", "P3", "n17l6/S/noncore_first_over_default_wall_censored")
show("P3_del_all_core_order", "P3", "core_order_identity")
show("P4_del_gauss_n15l5S", "P4", "n15l5/S")
show("P5_del_cmsxor_n15l5", "P5", "n15l5/cms_xor_U_over_S_conflicts")
show("P6_del_null_n15l5", "P6", "n15l5")
show("P6_inject_finished_null_n19l6", "P6", "n19l6")
show("P2P5_inject_m2_n15l5", "P2", "n15l5/S/wdsat_default_over_m2_f4")
show("P2P5_inject_m2_n15l5", "P5", "n15l5/m2_S_over_U_cpu")
