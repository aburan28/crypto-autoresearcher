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


def unevaluated(reason: str, **fields) -> dict:
    """D3(b,c): a clause that could not be evaluated, reported instead of dropped."""
    rec = dict(fields)
    rec.update({"evaluated": False, "reason": reason, "holds": None})
    return rec


def evaluated(**fields) -> dict:
    """D3(b,c): a clause that was evaluated in full."""
    rec = dict(fields)
    rec["evaluated"] = True
    return rec


def compose(clauses: dict, **extra) -> dict:
    """D3(b,c): ONE uniform reporting rule for every prediction quantified over cells.

    Every clause says whether it was evaluated; an unevaluated clause names what was
    missing.  The prediction lists every such clause in `unevaluable`, and a NONEMPTY
    `unevaluable` list forces top-level `holds: None` -- never true and never false,
    because a prediction quantified over every cell is not settled by the cells that
    happened to be measurable.  This changes no median, ratio, threshold, inclusion rule
    or the definition of `finished`; it changes only what is reported.
    """
    unevaluable = sorted(k for k, v in clauses.items() if not v.get("evaluated", True))
    resolved = [v["holds"] for k, v in clauses.items()
                if v.get("evaluated", True) and v.get("holds") is not None]
    holds = None if (unevaluable or not resolved) else all(resolved)
    rec = {"cells": clauses, "unevaluable": unevaluable, "n_clauses": len(clauses),
           "n_evaluated": len(clauses) - len(unevaluable), "holds": holds}
    rec.update(extra)
    return rec


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
                                "evaluated": True, "unevaluable": [],  # D3(b)
                                "holds": (len(certs) == 30 and not bad_certs and not bad_answers)}

    # ---- P2: WDSat default vs every finishing Groebner engine, per cell, S and U separately
    p2 = {}
    for cell in cells:
        for label in ("S", "U"):
            L = out["cells"][cell][label]
            for gname, key in (("m2_f4", "m2_f4_wall_s"), ("singular", "singular_wall_s")):
                name = f"{cell}/{label}/wdsat_default_over_{gname}"
                if L.get(key) is not None and L.get("wdsat_default_wall_s") is not None:
                    ratio = L["wdsat_default_wall_s"] / L[key] if L[key] > 0 else None
                    p2[name] = evaluated(ratio=ratio, holds=ratio is not None and ratio <= 0.1)
                else:  # D3(b): the missing side is named instead of the clause vanishing
                    missing = [k for k in (key, "wdsat_default_wall_s") if L.get(k) is None]
                    p2[name] = unevaluated(f"no median for {', '.join(missing)}: no row of that"
                                           f" engine/config finished on {cell}/{label}", ratio=None)
    out["predictions"]["P2"] = compose(
        p2, note="an unevaluable clause means no Groebner engine finished on that cell/label;"
                 " nothing is asserted about it")

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
        p3["core_order_identity"] = evaluated(instances_compared=compared,
                                              mismatching_instances=mismatches,
                                              holds=not mismatches)
    else:  # D3(b)
        p3["core_order_identity"] = unevaluated(
            "no instance carries both a finished default row and a finished core_order row"
            " with a conflict count", instances_compared=0, mismatching_instances=[])
    # P3b compares wall time on the SAME instances, right-censored: a timeout row
    # contributes its timeout_s, a lower bound on its true wall, so the resulting
    # median is itself a lower bound and the >= 2x test stays valid (never inflated
    # in the direction of the prediction by the censoring).
    for cell in cells:
        for label in ("S", "U"):
            # D3(a): THE LOOP-VARIABLE LEAK.  The pure-CNF clause below read `L`, which
            # this loop never bound, so it silently used the last aggregate bound by the
            # earlier per-cell loop (n19l6/U) and every l = 6 cell received that one
            # cell's ratio.  Binding the per-(cell, label) aggregate here, inside the loop
            # that uses it, is the whole fix; the ratio's formula is untouched.
            L = out["cells"][cell][label]
            nc_name = f"{cell}/{label}/noncore_first_over_default_wall_censored"
            nc = [r for r in rows if r.get("engine") == "wdsat" and r.get("config") == "noncore_first"
                  and r.get("cell") == cell and r.get("label") == label
                  and (finished(r) or r.get("status") == "budget_stop_timeout")]
            stems = {r["instance"] for r in nc}
            de = [r for r in rows if r.get("engine") == "wdsat" and r.get("config") == "default"
                  and r.get("instance") in stems and finished(r)]
            if not nc:  # D3(b)
                p3[nc_name] = unevaluated(f"no noncore_first row on {cell}/{label} is either"
                                          f" finished or a recorded timeout", n_noncore_rows=0)
            elif not de:  # D3(b)
                p3[nc_name] = unevaluated(f"no finished wdsat default row on the {len(stems)}"
                                          f" instance(s) the noncore_first rows cover",
                                          n_noncore_rows=len(nc))
            else:
                nc_vals = [r["wall_s"] if finished(r) else float(r.get("timeout_s") or r["wall_s"]) for r in nc]
                de_med = med([r["wall_s"] for r in de])
                nc_med = med(nc_vals)
                r = nc_med / de_med if de_med and de_med > 0 else float("inf")
                p3[nc_name] = evaluated(
                    noncore_first_wall_s_lower_bound=nc_med, default_wall_s=de_med, ratio_lower_bound=r,
                    n_noncore_rows=len(nc), n_noncore_timeouts=sum(1 for x in nc if not finished(x)),
                    noncore_first_conflicts_finished_median=med([x["conflicts"] for x in nc if finished(x) and x.get("conflicts") is not None]),
                    holds=r >= 2)
            if cell.endswith("l6"):
                cms_name = f"{cell}/{label}/cms_pure_cnf_over_wdsat"
                if L["cryptominisat5_pure_cnf_wall_s"] is not None and L["wdsat_default_wall_s"] is not None:
                    r = L["cryptominisat5_pure_cnf_wall_s"] / L["wdsat_default_wall_s"] if L["wdsat_default_wall_s"] > 0 else float("inf")
                    p3[cms_name] = evaluated(ratio=r, holds=r >= 10,
                                             cryptominisat5_pure_cnf_wall_s=L["cryptominisat5_pure_cnf_wall_s"],
                                             wdsat_default_wall_s=L["wdsat_default_wall_s"])
                else:  # D3(b)
                    missing = [k for k in ("cryptominisat5_pure_cnf_wall_s", "wdsat_default_wall_s")
                               if L[k] is None]
                    p3[cms_name] = unevaluated(f"no median for {', '.join(missing)} on"
                                               f" {cell}/{label}", ratio=None)
    out["predictions"]["P3"] = compose(p3)

    # ---- P4: -x does not reduce median wall time
    p4 = {}
    for cell in cells:
        for label in ("S", "U"):
            L = out["cells"][cell][label]
            name = f"{cell}/{label}"
            if L["wdsat_gauss_elim_wall_s"] is not None and L["wdsat_default_wall_s"] is not None:
                d = L["wdsat_default_wall_s"]
                if d <= 0.05:
                    # D3(c): the frozen reduction reported this cell with holds None and
                    # then dropped it from the top-level `holds`, so a prediction
                    # quantified over every cell read as settled on a subset.  The
                    # threshold and the 0.05 s floor are unchanged; only the reporting is.
                    p4[name] = unevaluated("default median under the 0.05 s floor;"
                                           " unresolvable by wall clock",
                                           gauss_elim=L["wdsat_gauss_elim_wall_s"], default=d)
                else:
                    p4[name] = evaluated(gauss_elim=L["wdsat_gauss_elim_wall_s"], default=d,
                                         holds=L["wdsat_gauss_elim_wall_s"] >= 0.9 * d)
            else:  # D3(b)
                missing = [k for k in ("wdsat_gauss_elim_wall_s", "wdsat_default_wall_s") if L[k] is None]
                p4[name] = unevaluated(f"no median for {', '.join(missing)} on {name}",
                                       gauss_elim=L["wdsat_gauss_elim_wall_s"],
                                       default=L["wdsat_default_wall_s"])
    out["predictions"]["P4"] = compose(p4)

    # ---- P5: SAT solvers U/S conflicts >= 2; Groebner S/U cpu in [0.5, 2]
    p5 = {}
    for cell in cells:
        S, U = out["cells"][cell]["S"], out["cells"][cell]["U"]
        name = f"{cell}/wdsat_U_over_S_conflicts"
        if S["wdsat_default_conflicts"] and U["wdsat_default_conflicts"] is not None:
            r = U["wdsat_default_conflicts"] / S["wdsat_default_conflicts"]
            p5[name] = evaluated(ratio=r, S=S["wdsat_default_conflicts"],
                                 U=U["wdsat_default_conflicts"], holds=r >= 2)
        else:  # D3(b)
            p5[name] = unevaluated("no usable wdsat default median conflict count for both"
                                   f" labels of {cell} (S={S['wdsat_default_conflicts']},"
                                   f" U={U['wdsat_default_conflicts']})", ratio=None)
        cms = {}
        for label in ("S", "U"):
            cms[label] = med([(r.get("stats") or {}).get("conflicts") for r in rows
                              if r.get("engine") == "cryptominisat5" and r.get("config") == "cnf_xor"
                              and r.get("cell") == cell and r.get("label") == label and finished(r)])
        name = f"{cell}/cms_xor_U_over_S_conflicts"
        if cms["S"] and cms["U"] is not None:
            r = cms["U"] / cms["S"]
            p5[name] = evaluated(ratio=r, S=cms["S"], U=cms["U"], holds=r >= 2)
        else:  # D3(b)
            p5[name] = unevaluated("no usable cryptominisat5 cnf_xor median conflict count for"
                                   f" both labels of {cell} (S={cms['S']}, U={cms['U']})",
                                   ratio=None, S=cms["S"], U=cms["U"])
        # D3(b): THE UNEVALUATED GROEBNER CLAUSE.  This term is guarded on m2_f4_cpu_s,
        # which is the median of the rows' `engine_cpu_s` key.  When no Macaulay2 row
        # carries that key the term simply vanished, and the top-level `holds` was then
        # computed over the surviving terms as if P5 had been evaluated in full.  The
        # guard and the [0.5, 2] band are unchanged; the skip is now recorded.
        name = f"{cell}/m2_S_over_U_cpu"
        if S["m2_f4_cpu_s"] and U["m2_f4_cpu_s"]:
            r = S["m2_f4_cpu_s"] / U["m2_f4_cpu_s"]
            p5[name] = evaluated(ratio=r, S=S["m2_f4_cpu_s"], U=U["m2_f4_cpu_s"], holds=0.5 <= r <= 2)
        else:
            p5[name] = unevaluated(
                "no median for m2_f4_cpu_s: no macaulay2_F4_ZZ2_fieldeqs/grevlex row of"
                f" {cell} carries the engine_cpu_s key (S={S['m2_f4_cpu_s']},"
                f" U={U['m2_f4_cpu_s']}), so the Groebner clause of P5 was not evaluated",
                ratio=None)
    out["predictions"]["P5"] = compose(p5)

    # ---- P6: null objects >= 10x harder in conflicts than structured U
    p6 = {}
    for cell in cells:
        U = out["cells"][cell]["U"]
        S = out["cells"][cell]["S"]
        null_conf = med([U["wdsat_default_on_null_object_conflicts"], S["wdsat_default_on_null_object_conflicts"]])
        if null_conf is not None and U["wdsat_default_conflicts"]:
            r = null_conf / U["wdsat_default_conflicts"]
            p6[cell] = evaluated(null_median_conflicts=null_conf,
                                 structured_U_median_conflicts=U["wdsat_default_conflicts"],
                                 ratio=r, holds=r >= 10)
        else:
            # D3(c): THE SILENTLY DROPPED CELL.  The frozen reduction filtered cells whose
            # own `holds` was None out of the top-level `holds`, so a prediction quantified
            # over EVERY cell was reported true on the strength of the cells that happened
            # to finish.  The exclusion rule for null rows and the >= 10x threshold are
            # unchanged; the cell is now named in `unevaluable` and the prediction reports
            # `holds: null`.
            missing = ("no finished null-object row carries a conflict count"
                       if null_conf is None else
                       "no usable structured U median conflict count")
            p6[cell] = unevaluated(f"{missing} for {cell}", null_median_conflicts=null_conf,
                                   structured_U_median_conflicts=U["wdsat_default_conflicts"],
                                   ratio=None)
    out["predictions"]["P6"] = compose(
        p6, note="null objects with status budget_stop/infrastructure are excluded and counted"
                 " in exclusions; a cell with no finished null object is reported in"
                 " `unevaluable` and forces holds: null")

    out["n_rows"] = len(rows)
    (run_dir / "summary.json").write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps({k: v.get("holds") for k, v in out["predictions"].items()}, indent=1))


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
