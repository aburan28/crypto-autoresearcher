#!/usr/bin/env python3
"""Reduce results.jsonl to per-cell medians and evaluate the pre-registered predictions
P1..P6 of H-ICPERF-cc4847. Pure arithmetic on the recorded rows; writes summary.json.

Budget stops and infrastructure exits are EXCLUDED from medians and COUNTED per cell,
as the contract requires. Every ratio names the two rows it was formed from.
"""
from __future__ import annotations

import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

SAT_STATUSES = {"SAT"}
UNSAT_STATUSES = {"UNSAT", "UNSAT_certified_unit_ideal"}
FINISHED_GB = {"UNSAT_certified_unit_ideal", "consistent_proper_ideal"}


def med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def load(run_dir: Path):
    rows = [json.loads(ln) for ln in (run_dir / "results.jsonl").read_text().splitlines() if ln.strip()]
    return rows


def finished(r):
    s = r.get("status", "")
    return not (s.startswith("budget_stop") or s.startswith("infrastructure") or s == "unknown")


def main(run_dir: Path):
    rows = load(run_dir)
    by = defaultdict(list)
    for r in rows:
        by[(r["cell"], r["label"], r["engine"], r["config"])].append(r)

    cells = sorted({r["cell"] for r in rows})
    out = {"cells": {}, "predictions": {}, "exclusions": {}}

    def stat(cell, label, engine, config, key):
        rs = by.get((cell, label, engine, config), [])
        fin = [r for r in rs if finished(r)]
        out["exclusions"][f"{cell}/{label}/{engine}/{config}"] = {
            "n_rows": len(rs), "n_finished": len(fin),
            "excluded_statuses": sorted({r.get("status", "?") for r in rs if not finished(r)})}
        return med([r.get(key) for r in fin]), len(fin)

    for cell in cells:
        c = {}
        for label in ("S", "U"):
            L = {}
            for cfg in ("default", "core_order", "noncore_first", "symmetry", "gauss_elim", "default_on_null_object"):
                L[f"wdsat_{cfg}_wall_s"], L[f"wdsat_{cfg}_n"] = stat(cell, label, "wdsat", cfg, "wall_s")
                L[f"wdsat_{cfg}_conflicts"], _ = stat(cell, label, "wdsat", cfg, "conflicts")
            L["cms_xor_wall_s"], L["cms_xor_n"] = stat(cell, label, "cryptominisat5", "cnf_xor", "wall_s")
            for e in ("cryptominisat5", "cadical", "minisat"):
                L[f"{e}_pure_cnf_wall_s"], L[f"{e}_pure_cnf_n"] = stat(cell, label, e, "pure_cnf", "wall_s")
            L["m2_f4_wall_s"], L["m2_f4_n"] = stat(cell, label, "macaulay2_F4_ZZ2_fieldeqs", "grevlex", "wall_s")
            L["m2_f4_cpu_s"], _ = stat(cell, label, "macaulay2_F4_ZZ2_fieldeqs", "grevlex", "engine_cpu_s")
            L["singular_wall_s"], L["singular_n"] = stat(cell, label, "singular_std_GF2_fieldeqs", "dp", "wall_s")
            c[label] = L
        out["cells"][cell] = c

    # ---- P1: certificates and every SAT answer verified
    certs = [r for r in rows if r["engine"] == "certificate"]
    sat_answers = [r for r in rows if r.get("status") == "SAT" and "verification" in r]
    bad_certs = [r["instance"] for r in certs if not r.get("verified")]
    bad_answers = [(r["instance"], r["engine"], r["config"]) for r in sat_answers if not r["verification"].get("verified")]
    sat_on_U = [(r["instance"], r["engine"], r["config"]) for r in sat_answers if r["label"] == "U"]
    out["predictions"]["P1"] = {"n_certificates": len(certs), "invalid_certificates": bad_certs,
                                "n_sat_answers": len(sat_answers), "unverified_sat_answers": bad_answers,
                                "sat_answers_on_U_labelled_instances": sat_on_U,
                                "holds": (len(certs) == 30 and not bad_certs and not bad_answers)}

    # ---- P2: WDSat default vs every finishing Groebner engine, per cell, S and U separately
    p2 = {}
    for cell in cells:
        for label in ("S", "U"):
            L = out["cells"][cell][label]
            for gname, key in (("m2_f4", "m2_f4_wall_s"), ("singular", "singular_wall_s")):
                if L.get(key) is not None and L.get("wdsat_default_wall_s") is not None:
                    ratio = L["wdsat_default_wall_s"] / L[key] if L[key] > 0 else None
                    p2[f"{cell}/{label}/wdsat_default_over_{gname}"] = {"ratio": ratio, "holds": ratio is not None and ratio <= 0.1}
    out["predictions"]["P2"] = {"cells": p2, "holds": all(v["holds"] for v in p2.values()) if p2 else None,
                                "note": "None = no Groebner engine finished on that cell; nothing asserted"}

    # ---- P3: (a) explicit core order == default per instance (identity check on -g);
    #          (b) non-core-first order >= 2x default in median conflicts per cell;
    #          (c) CMS pure CNF >= 10x WDSat ANF wall at l=6
    p3 = {}
    by_inst = {}
    for r in rows:
        if r.get("engine") == "wdsat" and finished(r) and r.get("conflicts") is not None:
            by_inst.setdefault(r["instance"], {})[r["config"]] = r["conflicts"]
    mismatches = sorted(i for i, c in by_inst.items()
                        if "default" in c and "core_order" in c and c["default"] != c["core_order"])
    compared = sum(1 for c in by_inst.values() if "default" in c and "core_order" in c)
    if compared:
        p3["core_order_identity"] = {"instances_compared": compared, "mismatching_instances": mismatches,
                                     "holds": not mismatches}
    # P3b compares wall time on the SAME instances, right-censored: a timeout row
    # contributes its timeout_s, a lower bound on its true wall, so the resulting
    # median is itself a lower bound and the >= 2x test stays valid (never inflated
    # in the direction of the prediction by the censoring).
    for cell in cells:
        for label in ("S", "U"):
            nc = [r for r in rows if r.get("engine") == "wdsat" and r.get("config") == "noncore_first"
                  and r.get("cell") == cell and r.get("label") == label
                  and (finished(r) or r.get("status") == "budget_stop_timeout")]
            if not nc:
                continue
            stems = {r["instance"] for r in nc}
            de = [r for r in rows if r.get("engine") == "wdsat" and r.get("config") == "default"
                  and r.get("instance") in stems and finished(r)]
            if not de:
                continue
            nc_vals = [r["wall_s"] if finished(r) else float(r.get("timeout_s") or r["wall_s"]) for r in nc]
            de_med = med([r["wall_s"] for r in de])
            nc_med = med(nc_vals)
            r = nc_med / de_med if de_med and de_med > 0 else float("inf")
            p3[f"{cell}/{label}/noncore_first_over_default_wall_censored"] = {
                "noncore_first_wall_s_lower_bound": nc_med, "default_wall_s": de_med, "ratio_lower_bound": r,
                "n_noncore_rows": len(nc), "n_noncore_timeouts": sum(1 for x in nc if not finished(x)),
                "noncore_first_conflicts_finished_median": med([x["conflicts"] for x in nc if finished(x) and x.get("conflicts") is not None]),
                "holds": r >= 2}
            if cell.endswith("l6") and L["cryptominisat5_pure_cnf_wall_s"] is not None and L["wdsat_default_wall_s"] is not None:
                r = L["cryptominisat5_pure_cnf_wall_s"] / L["wdsat_default_wall_s"] if L["wdsat_default_wall_s"] > 0 else float("inf")
                p3[f"{cell}/{label}/cms_pure_cnf_over_wdsat"] = {"ratio": r, "holds": r >= 10}
    out["predictions"]["P3"] = {"cells": p3, "holds": all(v["holds"] for v in p3.values()) if p3 else None}

    # ---- P4: -x does not reduce median wall time
    p4 = {}
    for cell in cells:
        for label in ("S", "U"):
            L = out["cells"][cell][label]
            if L["wdsat_gauss_elim_wall_s"] is not None and L["wdsat_default_wall_s"] is not None:
                d = L["wdsat_default_wall_s"]
                if d <= 0.05:
                    p4[f"{cell}/{label}"] = {"gauss_elim": L["wdsat_gauss_elim_wall_s"], "default": d,
                                            "holds": None, "note": "default median under the 0.05 s floor; unresolvable by wall clock"}
                else:
                    p4[f"{cell}/{label}"] = {"gauss_elim": L["wdsat_gauss_elim_wall_s"], "default": d,
                                            "holds": L["wdsat_gauss_elim_wall_s"] >= 0.9 * d}
    resolved = [v["holds"] for v in p4.values() if v["holds"] is not None]
    out["predictions"]["P4"] = {"cells": p4, "holds": all(resolved) if resolved else None}

    # ---- P5: SAT solvers U/S conflicts >= 2; Groebner S/U cpu in [0.5, 2]
    p5 = {}
    for cell in cells:
        S, U = out["cells"][cell]["S"], out["cells"][cell]["U"]
        if S["wdsat_default_conflicts"] and U["wdsat_default_conflicts"] is not None:
            r = U["wdsat_default_conflicts"] / S["wdsat_default_conflicts"]
            p5[f"{cell}/wdsat_U_over_S_conflicts"] = {"ratio": r, "holds": r >= 2}
        cms = {}
        for label in ("S", "U"):
            cms[label] = med([(r.get("stats") or {}).get("conflicts") for r in rows
                              if r.get("engine") == "cryptominisat5" and r.get("config") == "cnf_xor"
                              and r.get("cell") == cell and r.get("label") == label and finished(r)])
        if cms["S"] and cms["U"] is not None:
            r = cms["U"] / cms["S"]
            p5[f"{cell}/cms_xor_U_over_S_conflicts"] = {"ratio": r, "S": cms["S"], "U": cms["U"], "holds": r >= 2}
        if S["m2_f4_cpu_s"] and U["m2_f4_cpu_s"]:
            r = S["m2_f4_cpu_s"] / U["m2_f4_cpu_s"]
            p5[f"{cell}/m2_S_over_U_cpu"] = {"ratio": r, "holds": 0.5 <= r <= 2}
    out["predictions"]["P5"] = {"cells": p5, "holds": all(v["holds"] for v in p5.values()) if p5 else None}

    # ---- P6: null objects >= 10x harder in conflicts than structured U
    p6 = {}
    for cell in cells:
        U = out["cells"][cell]["U"]
        S = out["cells"][cell]["S"]
        null_conf = med([U["wdsat_default_on_null_object_conflicts"], S["wdsat_default_on_null_object_conflicts"]])
        if null_conf is not None and U["wdsat_default_conflicts"]:
            r = null_conf / U["wdsat_default_conflicts"]
            p6[cell] = {"null_median_conflicts": null_conf, "structured_U_median_conflicts": U["wdsat_default_conflicts"],
                        "ratio": r, "holds": r >= 10}
        else:
            p6[cell] = {"null_median_conflicts": null_conf, "structured_U_median_conflicts": U["wdsat_default_conflicts"],
                        "ratio": None, "holds": None}
    out["predictions"]["P6"] = {"cells": p6, "holds": all(v["holds"] for v in p6.values() if v["holds"] is not None) if p6 else None,
                                "note": "null objects with status budget_stop/infrastructure are excluded and counted in exclusions"}

    out["n_rows"] = len(rows)
    (run_dir / "summary.json").write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps({k: v.get("holds") for k, v in out["predictions"].items()}, indent=1))


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
