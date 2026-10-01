"""V3 step (1): the validator's OWN reduction of results.jsonl to per-cell
medians and to P1-P6, written from the wording of H-ICPERF-cc4847 and the
metric definitions in EXP-ICPERF-66fd51/specification.yaml, BEFORE opening
experiments/EXP-ICPERF-66fd51/code/summary.py.

Conventions taken from the contract:
  * medians are over rows with status in {SAT, UNSAT} ("finished"); budget
    stops and infrastructure exits are excluded and counted separately
    (specification.yaml preregistered_prediction.formula, interpretation_limits);
  * P3b is the one exception: a timeout row is counted AT its timeout, giving a
    right-censored lower bound (hypothesis wording);
  * median of an even-sized sample is the mean of the two central values
    (statistics.median).
"""
from __future__ import annotations

import json
import os
import statistics
from collections import defaultdict

RUN = "/workspace/experiments/EXP-ICPERF-66fd51/runs/RUN-ICPERF-305ca3"
OUT = os.path.dirname(os.path.abspath(__file__))
CELLS = ["n15l5", "n17l6", "n19l6"]
L6 = ["n17l6", "n19l6"]
FINISHED = {"SAT", "UNSAT"}


def load():
    return [json.loads(l) for l in open(os.path.join(RUN, "results.jsonl"))]


def med(vals):
    return statistics.median(vals) if vals else None


def inst_id(name):
    return int(name.split("-")[1])


def main():
    rows = load()
    out = {}

    def sel(engine=None, config=None, cell=None, label=None, phase=None,
            finished_only=True, insts=None):
        r = rows
        if engine is not None:
            r = [x for x in r if x.get("engine") == engine]
        if config is not None:
            r = [x for x in r if x.get("config") == config]
        if cell is not None:
            r = [x for x in r if x.get("cell") == cell]
        if label is not None:
            r = [x for x in r if x.get("label") == label]
        if phase is not None:
            r = [x for x in r if x.get("phase") == phase]
        if insts is not None:
            r = [x for x in r if x.get("instance") in insts]
        if finished_only:
            r = [x for x in r if x.get("status") in FINISHED]
        return r

    # ---------------- per-cell table -------------------------------------
    table = {}
    engine_configs = [
        ("wdsat", "default"), ("wdsat", "core_order"), ("wdsat", "symmetry"),
        ("wdsat", "gauss_elim"), ("wdsat", "noncore_first"),
        ("wdsat", "default_on_null_object"),
        ("cryptominisat5", "cnf_xor"), ("cryptominisat5", "pure_cnf"),
        ("cadical", "pure_cnf"), ("minisat", "pure_cnf"),
        ("macaulay2_F4_ZZ2_fieldeqs", "grevlex"), ("singular_std_GF2_fieldeqs", "dp"),
    ]
    for cell in CELLS:
        for label in ("S", "U"):
            key = f"{cell}/{label}"
            table[key] = {}
            for eng, cfg in engine_configs:
                rs = sel(eng, cfg, cell, label)
                allr = sel(eng, cfg, cell, label, finished_only=False)
                walls = [x["wall_s"] for x in rs]
                confs = [x["conflicts"] for x in rs if x.get("conflicts") is not None]
                table[key][f"{eng}/{cfg}"] = {
                    "n_planned": len(allr),
                    "n_finished": len(rs),
                    "n_excluded": len(allr) - len(rs),
                    "excluded_statuses": sorted({x.get("status") for x in allr
                                                 if x.get("status") not in FINISHED}),
                    "median_wall_s": med(walls),
                    "median_conflicts": med(confs),
                }
    out["per_cell_table"] = table

    # ---------------- P1 --------------------------------------------------
    certs = [r for r in rows if r.get("engine") == "certificate"]
    sats = [r for r in rows if r.get("status") == "SAT" and "verification" in r]
    out["P1"] = {
        "n_certificates": len(certs),
        "n_certificates_verified": sum(1 for r in certs if r.get("verified")),
        "invalid_certificates": [r["instance"] for r in certs if not r.get("verified")],
        "n_sat_answers": len(sats),
        "n_sat_verified": sum(1 for r in sats if r["verification"]["verified"]),
        "unverified_sat_answers": [
            {"instance": r["instance"], "engine": r["engine"], "config": r["config"],
             "x_bits": r["verification"]["x_bits"]}
            for r in sats if not r["verification"]["verified"]],
        "holds": (sum(1 for r in certs if r.get("verified")) == len(certs)
                  and all(r["verification"]["verified"] for r in sats)),
    }

    # ---------------- P2 --------------------------------------------------
    p2 = {}
    for cell in CELLS:
        for label in ("S", "U"):
            wd = med([x["wall_s"] for x in sel("wdsat", "default", cell, label)])
            for eng, cfg in (("macaulay2_F4_ZZ2_fieldeqs", "grevlex"),
                             ("singular_std_GF2_fieldeqs", "dp")):
                gr = sel(eng, cfg, cell, label)
                if gr:
                    p2[f"{cell}/{label}/{eng}"] = {
                        "wdsat_median_wall_s": wd,
                        "groebner_median_wall_s": med([x["wall_s"] for x in gr]),
                        "ratio": wd / med([x["wall_s"] for x in gr]),
                    }
    out["P2"] = {"cells": p2, "holds": None if not p2 else all(v["ratio"] <= 0.1 for v in p2.values()),
                 "note": "no Groebner engine finished any row" if not p2 else ""}

    # ---------------- P3a -------------------------------------------------
    d = {(x["instance"]): x for x in sel("wdsat", "default")}
    c = {(x["instance"]): x for x in sel("wdsat", "core_order")}
    common = sorted(set(d) & set(c))
    mismatch = [i for i in common if d[i].get("conflicts") != c[i].get("conflicts")]
    status_mismatch = [i for i in common if d[i]["status"] != c[i]["status"]]
    out["P3a"] = {"n_compared": len(common), "n_conflict_mismatches": len(mismatch),
                  "mismatching": mismatch, "n_status_mismatches": len(status_mismatch),
                  "holds": len(mismatch) == 0 and len(status_mismatch) == 0}

    # ---------------- P3b -------------------------------------------------
    p3b = {}
    for cell in CELLS:
        for label in ("S", "U"):
            nc_all = sel("wdsat", "noncore_first", cell, label, finished_only=False)
            insts = sorted({x["instance"] for x in nc_all})
            if not insts:
                continue
            nc_wall = []
            for x in nc_all:
                nc_wall.append(x["wall_s"] if x["status"] in FINISHED else x["timeout_s"])
            dflt_matched = [x["wall_s"] for x in sel("wdsat", "default", cell, label,
                                                     insts=set(insts))]
            dflt_all = [x["wall_s"] for x in sel("wdsat", "default", cell, label)]
            p3b[f"{cell}/{label}"] = {
                "instances": insts,
                "n_rows": len(nc_all),
                "n_timeouts": sum(1 for x in nc_all if x["status"] not in FINISHED),
                "noncore_median_wall_censored": med(nc_wall),
                "default_median_wall_matched_subset": med(dflt_matched),
                "default_median_wall_all_10": med(dflt_all),
                "ratio_vs_matched_subset": med(nc_wall) / med(dflt_matched),
                "ratio_vs_all_10": med(nc_wall) / med(dflt_all),
            }
    out["P3b"] = {"cells": p3b,
                  "holds": all(v["ratio_vs_matched_subset"] >= 2 for v in p3b.values())}

    # ---------------- P3c -------------------------------------------------
    p3c = {}
    for cell in L6:
        for label in ("S", "U"):
            cms = sel("cryptominisat5", "pure_cnf", cell, label)
            insts = sorted({x["instance"] for x in
                            sel("cryptominisat5", "pure_cnf", cell, label,
                                finished_only=False)})
            if not cms:
                continue
            m_cms = med([x["wall_s"] for x in cms])
            m_wd_all = med([x["wall_s"] for x in sel("wdsat", "default", cell, label)])
            m_wd_sub = med([x["wall_s"] for x in sel("wdsat", "default", cell, label,
                                                     insts=set(insts))])
            p3c[f"{cell}/{label}"] = {
                "cms_pure_cnf_median_wall_s": m_cms,
                "wdsat_default_median_wall_s_all_10": m_wd_all,
                "wdsat_default_median_wall_s_matched_subset": m_wd_sub,
                "ratio_vs_all_10": m_cms / m_wd_all,
                "ratio_vs_matched_subset": m_cms / m_wd_sub,
                "phase_D_instances": insts,
            }
    out["P3c"] = {"cells": p3c,
                  "holds_vs_all_10": all(v["ratio_vs_all_10"] >= 10 for v in p3c.values()),
                  "holds_vs_matched_subset": all(v["ratio_vs_matched_subset"] >= 10
                                                 for v in p3c.values())}
    out["P3"] = {"holds": out["P3a"]["holds"] and out["P3b"]["holds"]
                 and out["P3c"]["holds_vs_all_10"]}

    # ---------------- P4 --------------------------------------------------
    p4 = {}
    for cell in CELLS:
        for label in ("S", "U"):
            dm = med([x["wall_s"] for x in sel("wdsat", "default", cell, label)])
            gm = med([x["wall_s"] for x in sel("wdsat", "gauss_elim", cell, label)])
            p4[f"{cell}/{label}"] = {
                "default_median_wall_s": dm, "gauss_median_wall_s": gm,
                "gauss_over_default": gm / dm,
                "above_0.05s_floor": dm > 0.05,
                "reduces_by_more_than_10pct": (gm < 0.9 * dm),
            }
    out["P4"] = {"cells": p4,
                 "holds": all(not v["reduces_by_more_than_10pct"]
                              for v in p4.values() if v["above_0.05s_floor"]),
                 "cells_under_floor": [k for k, v in p4.items() if not v["above_0.05s_floor"]]}

    # ---------------- P5 --------------------------------------------------
    p5 = {}
    for cell in CELLS:
        for eng, cfg in (("wdsat", "default"), ("cryptominisat5", "cnf_xor")):
            s = [x["conflicts"] for x in sel(eng, cfg, cell, "S")
                 if x.get("conflicts") is not None]
            u = [x["conflicts"] for x in sel(eng, cfg, cell, "U")
                 if x.get("conflicts") is not None]
            if not s or not u:
                # conflicts may live under stats for CMS
                s = [x["stats"]["conflicts"] for x in sel(eng, cfg, cell, "S")
                     if x.get("stats", {}).get("conflicts") is not None]
                u = [x["stats"]["conflicts"] for x in sel(eng, cfg, cell, "U")
                     if x.get("stats", {}).get("conflicts") is not None]
            if s and u:
                p5[f"{cell}/{eng}"] = {"median_S_conflicts": med(s),
                                       "median_U_conflicts": med(u),
                                       "U_over_S": med(u) / med(s),
                                       "n_S": len(s), "n_U": len(u)}
    out["P5"] = {"sat_engines": p5,
                 "groebner_engines": "none finished; the [0.5,2] clause is unevaluable",
                 "holds_sat_clause": all(v["U_over_S"] >= 2 for v in p5.values())}

    # ---------------- P6 --------------------------------------------------
    p6 = {}
    for cell in CELLS:
        nul_all = sel("wdsat", "default_on_null_object", cell, finished_only=False)
        nul = [x for x in nul_all if x["status"] in FINISHED]
        struct_u = [x["conflicts"] for x in sel("wdsat", "default", cell, "U")
                    if x.get("conflicts") is not None]
        nc = [x["conflicts"] for x in nul if x.get("conflicts") is not None]
        p6[cell] = {
            "n_null_planned": len(nul_all), "n_null_finished": len(nul),
            "n_null_timeout": len(nul_all) - len(nul),
            "null_median_conflicts": med(nc),
            "structured_U_median_conflicts": med(struct_u),
            "ratio": (med(nc) / med(struct_u)) if nc else None,
            "null_timeout_s": sorted({x["timeout_s"] for x in nul_all}),
            "structured_U_median_wall_s": med([x["wall_s"] for x in
                                               sel("wdsat", "default", cell, "U")]),
        }
        if p6[cell]["ratio"] is None:
            t = p6[cell]["null_timeout_s"][0]
            p6[cell]["censored_wall_lower_bound"] = t / p6[cell]["structured_U_median_wall_s"]
    out["P6"] = {
        "cells": p6,
        "holds_on_every_cell": all(v["ratio"] is not None and v["ratio"] >= 10
                                   for v in p6.values()),
        "holds_ignoring_null_cells": all(v["ratio"] >= 10 for v in p6.values()
                                         if v["ratio"] is not None),
        "cells_with_null_ratio": [k for k, v in p6.items() if v["ratio"] is None],
    }

    out["headline"] = {
        "P1": out["P1"]["holds"], "P2": out["P2"]["holds"], "P3": out["P3"]["holds"],
        "P4": out["P4"]["holds"], "P5": out["P5"]["holds_sat_clause"],
        "P6_every_cell": out["P6"]["holds_on_every_cell"],
        "P6_ignoring_null_cells": out["P6"]["holds_ignoring_null_cells"],
    }

    with open(os.path.join(OUT, "v3_reduce.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps(out["headline"], indent=1, sort_keys=True))
    return out


if __name__ == "__main__":
    main()
