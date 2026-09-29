"""V3 step (1): the validator's own reduction of results.jsonl, written from
the contract (specification.yaml metrics, H-ICPERF-cc4847 P1-P6 wording) and
results.jsonl ONLY, before opening code/summary.py. Diffs against
summary.json. Output: v3_reduce.json, v3_diff.md."""
import json, os, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__))
RUN = "/workspace/experiments/EXP-ICPERF-66fd51/runs/RUN-ICPERF-305ca3"
rows = [json.loads(l) for l in open(os.path.join(RUN, "results.jsonl"))]
S = json.load(open(os.path.join(RUN, "summary.json")))
FIN = ("SAT", "UNSAT")
CELLS = ("n15l5", "n17l6", "n19l6")


def med(v):
    return st.median(v) if v else None


def sel(**kw):
    out = []
    for r in rows:
        if all(r.get(k) == v for k, v in kw.items()):
            out.append(r)
    return out


def conflicts(r):
    if r["engine"] == "wdsat":
        return r.get("conflicts")
    if r["engine"] == "cryptominisat5":
        return (r.get("stats") or {}).get("conflicts")
    return None


# ------------------------------------------------------------- per-cell medians
key_map = {  # summary.json key prefix -> (engine, config)
    "wdsat_default": ("wdsat", "default"), "wdsat_core_order": ("wdsat", "core_order"),
    "wdsat_noncore_first": ("wdsat", "noncore_first"), "wdsat_symmetry": ("wdsat", "symmetry"),
    "wdsat_gauss_elim": ("wdsat", "gauss_elim"), "wdsat_default_on_null_object": ("wdsat", "default_on_null_object"),
    "cms_xor": ("cryptominisat5", "cnf_xor"), "cryptominisat5_pure_cnf": ("cryptominisat5", "pure_cnf"),
    "cadical_pure_cnf": ("cadical", "pure_cnf"), "minisat_pure_cnf": ("minisat", "pure_cnf"),
    "m2_f4": ("macaulay2_F4_ZZ2_fieldeqs", "grevlex"), "singular": ("singular_std_GF2_fieldeqs", "dp")}
cells = {}
diffs = []
for cell in CELLS:
    cells[cell] = {}
    for lab in ("S", "U"):
        d = {}
        for k, (eng, cfg) in key_map.items():
            rs = sel(cell=cell, label=lab, engine=eng, config=cfg)
            fin = [r for r in rs if r["status"] in FIN]
            d[k + "_n"] = len(fin)
            d[k + "_wall_s"] = med([r["wall_s"] for r in fin])
            if eng in ("wdsat",):
                d[k + "_conflicts"] = med([conflicts(r) for r in fin])
            if eng == "cryptominisat5" and cfg == "cnf_xor":
                d[k + "_conflicts_validator"] = med([conflicts(r) for r in fin])
            d[k + "_n_rows_total"] = len(rs)
            d[k + "_excluded_statuses"] = sorted({r["status"] for r in rs if r["status"] not in FIN})
        cells[cell][lab] = d
        # diff against summary.json cells
        for k, v in S["cells"][cell][lab].items():
            mine = d.get(k, "MISSING")
            same = (mine == v) or (isinstance(v, float) and isinstance(mine, (int, float)) and abs(mine - v) <= 1e-9)
            if not same:
                diffs.append({"where": f"cells/{cell}/{lab}/{k}", "summary": v, "validator": mine})

# ----------------------------------------------------------------- predictions
P = {}
# P1
certs = sel(engine="certificate")
sat_rows = [r for r in rows if r.get("status") == "SAT" and "verification" in r]
sat_rows_all = [r for r in rows if r.get("status") == "SAT"]
P["P1"] = {"n_certificates": len(certs), "certificates_verified": sum(1 for r in certs if r["verified"]),
           "n_sat_answers_with_verification_block": len(sat_rows),
           "n_sat_rows_total_incl_null_objects": len(sat_rows_all),
           "sat_rows_without_verification_block": [(r["instance"], r["engine"], r["config"]) for r in sat_rows_all if "verification" not in r],
           "unverified_sat_answers": [(r["instance"], r["engine"], r["config"]) for r in sat_rows if not r["verification"]["verified"]],
           "sat_answers_on_U": [(r["instance"], r["engine"], r["config"]) for r in sat_rows if r["label"] == "U"]}
P["P1"]["holds"] = P["P1"]["certificates_verified"] == 30 and not P["P1"]["unverified_sat_answers"]
# P2
p2 = {}
for cell in CELLS:
    for lab in ("S", "U"):
        w = cells[cell][lab]["wdsat_default_wall_s"]
        for g in ("m2_f4", "singular"):
            gw = cells[cell][lab][g + "_wall_s"]
            p2[f"{cell}/{lab}/{g}"] = None if gw is None else {"ratio_wdsat_over_groebner": w / gw, "holds": w / gw <= 0.1}
P["P2"] = {"cells": p2, "holds": None if all(v is None for v in p2.values()) else all(v["holds"] for v in p2.values() if v)}
# P3a
mism = []
for cell in CELLS:
    for r in sel(cell=cell, engine="wdsat", config="default"):
        c = sel(instance=r["instance"], engine="wdsat", config="core_order")
        assert len(c) == 1
        if c[0]["conflicts"] != r["conflicts"] or c[0]["status"] != r["status"]:
            mism.append(r["instance"])
P["P3a"] = {"instances_compared": 60, "mismatching": mism, "holds": not mism}
# P3b: on the SAME instances, timeouts at 120
p3b = {}
for cell in CELLS:
    for lab in ("S", "U"):
        nc = sel(cell=cell, label=lab, engine="wdsat", config="noncore_first")
        insts = sorted(r["instance"] for r in nc)
        cens = [(r["wall_s"] if r["status"] in FIN else r["timeout_s"]) for r in nc]
        dflt = [sel(instance=i, engine="wdsat", config="default")[0]["wall_s"] for i in insts]
        dflt_all = cells[cell][lab]["wdsat_default_wall_s"]
        p3b[f"{cell}/{lab}"] = {"instances": insts, "noncore_censored_median": med(cens),
                                "n_timeouts": sum(1 for r in nc if r["status"] not in FIN),
                                "default_median_same_instances": med(dflt), "default_median_all_10": dflt_all,
                                "ratio_matched": med(cens) / med(dflt), "ratio_vs_all10": med(cens) / dflt_all,
                                "holds_(>=2x_matched)": med(cens) / med(dflt) >= 2}
P["P3b"] = {"cells": p3b, "holds": all(v["holds_(>=2x_matched)"] for v in p3b.values())}
# P3c: CMS pure CNF vs WDSat default on ANF, l = 6 cells
p3c = {}
for cell in ("n17l6", "n19l6"):
    for lab in ("S", "U"):
        pc = [r for r in sel(cell=cell, label=lab, engine="cryptominisat5", config="pure_cnf") if r["status"] in FIN]
        insts = sorted(r["instance"] for r in pc)
        pcm = med([r["wall_s"] for r in pc])
        wd_same = med([sel(instance=i, engine="wdsat", config="default")[0]["wall_s"] for i in insts])
        wd_all = cells[cell][lab]["wdsat_default_wall_s"]
        p3c[f"{cell}/{lab}"] = {"cms_pure_cnf_median_wall": pcm, "n": len(pc), "instances": insts,
                                "wdsat_default_median_same_instances": wd_same, "wdsat_default_median_all_10": wd_all,
                                "ratio_matched": pcm / wd_same, "ratio_vs_all10": pcm / wd_all,
                                "holds_matched_(>=10x)": pcm / wd_same >= 10, "holds_all10_(>=10x)": pcm / wd_all >= 10}
P["P3c"] = {"cells": p3c, "holds_matched": all(v["holds_matched_(>=10x)"] for v in p3c.values()),
            "holds_all10": all(v["holds_all10_(>=10x)"] for v in p3c.values())}
P["P3"] = {"holds": P["P3a"]["holds"] and P["P3b"]["holds"] and P["P3c"]["holds_matched"] and P["P3c"]["holds_all10"]}
# P4
p4 = {}
for cell in CELLS:
    for lab in ("S", "U"):
        d = cells[cell][lab]["wdsat_default_wall_s"]
        g = cells[cell][lab]["wdsat_gauss_elim_wall_s"]
        if d <= 0.05:
            p4[f"{cell}/{lab}"] = {"default": d, "gauss_elim": g, "resolvable": False, "holds": None}
        else:
            p4[f"{cell}/{lab}"] = {"default": d, "gauss_elim": g, "resolvable": True, "ratio_ge_over_default": g / d,
                                   "holds_(no_more_than_10pct_speedup)": g / d >= 0.9}
P["P4"] = {"cells": p4, "holds": all(v["holds_(no_more_than_10pct_speedup)"] for v in p4.values() if v["resolvable"]),
           "unresolvable_cells": [k for k, v in p4.items() if not v["resolvable"]]}
# P5
p5 = {}
for cell in CELLS:
    for eng, cfg, nm in (("wdsat", "default", "wdsat"), ("cryptominisat5", "cnf_xor", "cms_xor")):
        s = med([conflicts(r) for r in sel(cell=cell, label="S", engine=eng, config=cfg) if r["status"] in FIN])
        u = med([conflicts(r) for r in sel(cell=cell, label="U", engine=eng, config=cfg) if r["status"] in FIN])
        p5[f"{cell}/{nm}"] = {"S_median_conflicts": s, "U_median_conflicts": u, "ratio_U_over_S": u / s, "holds_(>=2)": u / s >= 2}
    for g in ("macaulay2_F4_ZZ2_fieldeqs", "singular_std_GF2_fieldeqs"):
        fs = [r for r in sel(cell=cell, label="S", engine=g) if r["status"] in FIN]
        fu = [r for r in sel(cell=cell, label="U", engine=g) if r["status"] in FIN]
        p5[f"{cell}/{g}"] = None if not (fs and fu) else "finished rows exist -- recompute"
P["P5"] = {"cells": p5, "holds_SAT_clause": all(v["holds_(>=2)"] for v in p5.values() if isinstance(v, dict)),
           "groebner_clause": "asserts nothing: no Groebner row finished"}
# P6
p6 = {}
for cell in CELLS:
    nul = [r for r in sel(cell=cell, engine="wdsat", config="default_on_null_object")]
    nul_fin = [r for r in nul if r["status"] in FIN]
    nm = med([r["conflicts"] for r in nul_fin])
    um = cells[cell]["U"]["wdsat_default_conflicts"]
    uwall = cells[cell]["U"]["wdsat_default_wall_s"]
    p6[cell] = {"null_rows": len(nul), "null_finished": len(nul_fin), "null_timeouts": len(nul) - len(nul_fin),
                "null_median_conflicts_finished": nm, "structured_U_median_conflicts": um,
                "ratio": None if nm is None else nm / um, "holds": None if nm is None else nm / um >= 10,
                "null_min_finished_conflicts": min([r["conflicts"] for r in nul_fin], default=None),
                "censored_wall_lower_bound_180_over_structured_U_median_wall": 180 / uwall,
                "null_S_template_finished_conflicts": sorted(r["conflicts"] for r in nul_fin if r["label"] == "S"),
                "null_U_template_finished_conflicts": sorted(r["conflicts"] for r in nul_fin if r["label"] == "U")}
P["P6"] = {"cells": p6,
           "holds_every_cell_literal": all(v["holds"] is True for v in p6.values()),
           "holds_ignoring_null_cells": all(v["holds"] for v in p6.values() if v["holds"] is not None),
           "null_cells": [c for c, v in p6.items() if v["holds"] is None]}

out = {"cells": cells, "predictions": P, "diffs_vs_summary_cells": diffs}
json.dump(out, open(os.path.join(HERE, "v3_reduce.json"), "w"), indent=1)

# ------------------------------------------------- diff of prediction values
pd = []
def cmp(where, a, b):
    same = a == b or (isinstance(a, float) and isinstance(b, (int, float)) and abs(a - b) < 1e-9)
    pd.append({"where": where, "summary": a, "validator": b, "same": same})
sp = S["predictions"]
cmp("P1.holds", sp["P1"]["holds"], P["P1"]["holds"])
cmp("P1.n_sat_answers", sp["P1"]["n_sat_answers"], P["P1"]["n_sat_answers_with_verification_block"])
cmp("P1.unverified", [tuple(x) for x in sp["P1"]["unverified_sat_answers"]], P["P1"]["unverified_sat_answers"])
cmp("P2.holds", sp["P2"]["holds"], P["P2"]["holds"])
cmp("P3.core_order_identity.holds", sp["P3"]["cells"]["core_order_identity"]["holds"], P["P3a"]["holds"])
for cell in CELLS:
    for lab in ("S", "U"):
        k = f"{cell}/{lab}/noncore_first_over_default_wall_censored"
        cmp(k + ".noncore_lb", sp["P3"]["cells"][k]["noncore_first_wall_s_lower_bound"], p3b[f"{cell}/{lab}"]["noncore_censored_median"])
        cmp(k + ".default_wall_s", sp["P3"]["cells"][k]["default_wall_s"], p3b[f"{cell}/{lab}"]["default_median_same_instances"])
        cmp(k + ".ratio", sp["P3"]["cells"][k]["ratio_lower_bound"], p3b[f"{cell}/{lab}"]["ratio_matched"])
for cell in ("n17l6", "n19l6"):
    for lab in ("S", "U"):
        k = f"{cell}/{lab}/cms_pure_cnf_over_wdsat"
        cmp(k + ".ratio(vs matched)", sp["P3"]["cells"][k]["ratio"], p3c[f"{cell}/{lab}"]["ratio_matched"])
        cmp(k + ".ratio(vs all10)", sp["P3"]["cells"][k]["ratio"], p3c[f"{cell}/{lab}"]["ratio_vs_all10"])
cmp("P3.holds", sp["P3"]["holds"], P["P3"]["holds"])
for k, v in sp["P4"]["cells"].items():
    cmp(f"P4.{k}.gauss_elim", v["gauss_elim"], p4[k]["gauss_elim"])
    cmp(f"P4.{k}.default", v["default"], p4[k]["default"])
    cmp(f"P4.{k}.holds", v["holds"], p4[k].get("holds_(no_more_than_10pct_speedup)", p4[k].get("holds")))
cmp("P4.holds", sp["P4"]["holds"], P["P4"]["holds"])
for cell in CELLS:
    cmp(f"P5.{cell}/wdsat.ratio", sp["P5"]["cells"][f"{cell}/wdsat_U_over_S_conflicts"]["ratio"], p5[f"{cell}/wdsat"]["ratio_U_over_S"])
    cmp(f"P5.{cell}/cms_xor.ratio", sp["P5"]["cells"][f"{cell}/cms_xor_U_over_S_conflicts"]["ratio"], p5[f"{cell}/cms_xor"]["ratio_U_over_S"])
    cmp(f"P5.{cell}/cms_xor.S", sp["P5"]["cells"][f"{cell}/cms_xor_U_over_S_conflicts"]["S"], p5[f"{cell}/cms_xor"]["S_median_conflicts"])
    cmp(f"P5.{cell}/cms_xor.U", sp["P5"]["cells"][f"{cell}/cms_xor_U_over_S_conflicts"]["U"], p5[f"{cell}/cms_xor"]["U_median_conflicts"])
cmp("P5.holds", sp["P5"]["holds"], P["P5"]["holds_SAT_clause"])
for cell in CELLS:
    cmp(f"P6.{cell}.null_median", sp["P6"]["cells"][cell]["null_median_conflicts"], p6[cell]["null_median_conflicts_finished"])
    cmp(f"P6.{cell}.U_median", sp["P6"]["cells"][cell]["structured_U_median_conflicts"], p6[cell]["structured_U_median_conflicts"])
    cmp(f"P6.{cell}.ratio", sp["P6"]["cells"][cell]["ratio"], p6[cell]["ratio"])
cmp("P6.holds (summary) vs validator literal every-cell", sp["P6"]["holds"], P["P6"]["holds_every_cell_literal"])
cmp("P6.holds (summary) vs validator ignoring null cells", sp["P6"]["holds"], P["P6"]["holds_ignoring_null_cells"])
out["prediction_diffs"] = pd
json.dump(out, open(os.path.join(HERE, "v3_reduce.json"), "w"), indent=1)
with open(os.path.join(HERE, "v3_diff.md"), "w") as f:
    f.write("## per-cell median diffs (summary.json cells vs validator)\n\n")
    if not diffs:
        f.write("none: every cells/* value in summary.json reproduces exactly.\n")
    for d in diffs:
        f.write(f"- {d['where']}: summary={d['summary']} validator={d['validator']}\n")
    f.write("\n## prediction-value diffs\n\n| where | summary.json | validator | same |\n|---|---|---|---|\n")
    for d in pd:
        f.write(f"| {d['where']} | {d['summary']} | {d['validator']} | {d['same']} |\n")
print("cell diffs:", len(diffs))
for d in diffs:
    print(" ", d)
print("prediction diffs (not same):")
for d in pd:
    if not d["same"]:
        print(" ", d)
print(json.dumps({"P3b": p3b, "P3c": p3c, "P6": p6, "P4_unresolvable": P["P4"]["unresolvable_cells"], "P1": P["P1"]}, indent=1))
