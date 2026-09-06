#!/usr/bin/env python3
"""R0 (TASK-20260904-ed0e8f, red team): regenerate the analysis.md tables from
the RAW records only.

Rule of the joint: nothing is read from raw-result.json's `metrics` block, from
`execution-report.yaml`, or from analysis.md.  Everything is recomputed from
`raw.draws[*]` / `raw.null2_by_p_seed` / `raw.table` / `raw.mixed` /
`raw.non_monomial`, and every per-object (d_ff, fall_dim) is RE-DERIVED from the
per-layer rank profile (`layers`: full_rank, top_rank) rather than read from the
recorded `d_ff` / `fall_dim_at_d_ff` fields.  The recorded fields are then
compared against the re-derivation as a separate consistency check.

Output: JSON on stdout (also written to r0_regenerated.json by the caller).
"""
import json
import glob
import os
import sys
from collections import Counter, defaultdict

ROOT = "/home/user/crypto-autoresearcher"
RUNS = os.path.join(ROOT, "experiments/EXP-PFDR-5726af/runs")

CELL_OF_RUN = {
    "RUN-PFDR-5726af-m2-s2-gate": (2, 2),
    "RUN-PFDR-5726af-m2-s3": (2, 3),
    "RUN-PFDR-5726af-m2-s4": (2, 4),
    "RUN-PFDR-5726af-m2-s5": (2, 5),
    "RUN-PFDR-5726af-m2-s6": (2, 6),
    "RUN-PFDR-5726af-m3-s4": (3, 4),
    "RUN-PFDR-5726af-m3-s5": (3, 5),
}


def derive_dff(layers):
    """(d_ff, fall_dim) re-derived from the layer profile, using ONLY
    full_rank and top_rank.  fall_dim(D) := full_rank(D) - top_rank(D);
    d_ff := least D with fall_dim(D) > 0."""
    for L in sorted(layers, key=lambda x: x["D"]):
        fd = L["full_rank"] - L["top_rank"]
        if fd > 0:
            return L["D"], fd
    return None, None


def load(run):
    with open(os.path.join(RUNS, run, "raw-result.json")) as fh:
        return json.load(fh)


def main():
    out = {}
    mismatches = []

    # ---------- B: Semaev arm per cell, plus C/D/E/F/G ----------
    cells = {}
    for run, cell in CELL_OF_RUN.items():
        d = load(run)
        raw = d["raw"]
        rec = {
            "cell": cell,
            "run": run,
            "semaev_d_ff": [],
            "semaev_fall_dim": [],
            "semaev_d_ff_recorded": [],
            "semaev_fall_dim_recorded": [],
            "instances": [],
            "null1_d_ff": [],
            "null1_pairs": [],
            "null2_pairs_from_draws": set(),
            "n_draws": 0,
            "cert_kinds": Counter(),
            "generator_degree": set(),
            "top_form_tensor_check": Counter(),
            "s_poly_crosscheck": Counter(),
            "oracle_agrees": Counter(),
            "N_sol": [],
            "d_solve": [],
            "layer_profile_frozen_fixture": None,
            "D_max_computed": Counter(),
            "null1_censored": 0,
            "null1_no_fall": 0,
        }
        for dr in raw["draws"]:
            rec["n_draws"] += 1
            sem = dr["semaev"]
            dff, fdim = derive_dff(sem["layers"])
            rec["semaev_d_ff"].append(dff)
            rec["semaev_fall_dim"].append(fdim)
            rec["semaev_d_ff_recorded"].append(sem.get("d_ff"))
            rec["semaev_fall_dim_recorded"].append(sem.get("fall_dim_at_d_ff"))
            if (dff, fdim) != (sem.get("d_ff"), sem.get("fall_dim_at_d_ff")):
                mismatches.append(
                    ["semaev-recorded-vs-derived", run, dr["curve_seed"],
                     dr.get("target", {}), dff, fdim,
                     sem.get("d_ff"), sem.get("fall_dim_at_d_ff")])
            rec["instances"].append({
                "p": dr["p"], "curve_seed": dr["curve_seed"],
                "a": dr["curve"]["a"], "b": dr["curve"]["b"],
                "target": dr.get("target"),
                "frozen_fixture": dr.get("is_frozen_fixture", False),
            })
            rec["generator_degree"].add(dr.get("generator_degree"))
            rec["top_form_tensor_check"][json.dumps(dr.get("top_form_tensor_check"))] += 1
            rec["s_poly_crosscheck"][json.dumps(dr.get("s_poly_crosscheck_random_points"))] += 1
            if "oracle_agrees" in dr:
                rec["oracle_agrees"][str(dr["oracle_agrees"])] += 1
            rec["cert_kinds"][dr.get("certificate", {}).get("kind")] += 1
            sc = dr.get("sol_covariate") or {}
            rec["N_sol"].append(sc.get("N_sol"))
            rec["d_solve"].append(sc.get("d_solve"))
            rec["D_max_computed"][sem.get("D_max_computed")] += 1
            if rec["n_draws"] == 1:
                rec["layer_profile_first_draw"] = [
                    (L["D"], L["rows"], L["ncols_full"], L["ncols_top"],
                     L["full_rank"], L["top_rank"], L["full_rank"] - L["top_rank"])
                    for L in sorted(sem["layers"], key=lambda x: x["D"])]
                rec["first_draw_header"] = {"p": dr["p"], "curve_seed": dr["curve_seed"],
                                            "a": dr["curve"]["a"], "b": dr["curve"]["b"],
                                            "target": dr.get("target"),
                                            "generator_terms": dr.get("generator_terms")}
            if dr.get("is_frozen_fixture"):
                rec["layer_profile_frozen_fixture"] = [
                    (L["D"], L["rows"], L["ncols_full"], L["ncols_top"],
                     L["full_rank"], L["top_rank"], L["full_rank"] - L["top_rank"])
                    for L in sorted(sem["layers"], key=lambda x: x["D"])]
            for n1 in dr.get("null1", []):
                nd, nf = derive_dff(n1["layers"])
                rec["null1_d_ff"].append(nd)
                rec["null1_pairs"].append((nd, nf))
                if (nd, nf) != (n1.get("d_ff"), n1.get("fall_dim_at_d_ff")):
                    mismatches.append(["null1-recorded-vs-derived", run,
                                       n1.get("seed"), nd, nf,
                                       n1.get("d_ff"), n1.get("fall_dim_at_d_ff")])
                if n1.get("censored"):
                    rec["null1_censored"] += 1
                if nd is None:
                    rec["null1_no_fall"] += 1
            for n2 in dr.get("null2", []) or []:
                if "layers" in n2:
                    nd, nf = derive_dff(n2["layers"])
                else:
                    nd, nf = n2.get("d_ff"), n2.get("fall_dim_at_d_ff")
                rec["null2_pairs_from_draws"].add((dr["p"], n2.get("seed"), nd, nf))

        # NULL-2 at run level (D-NULL2-ONCE)
        n2tab = []
        for n2 in raw.get("null2_by_p_seed", []):
            nd, nf = derive_dff(n2["layers"]) if "layers" in n2 else (n2.get("d_ff"), n2.get("fall_dim_at_d_ff"))
            n2tab.append((n2.get("p"), n2.get("seed"), nd, nf))
            if "layers" in n2 and (nd, nf) != (n2.get("d_ff"), n2.get("fall_dim_at_d_ff")):
                mismatches.append(["null2-recorded-vs-derived", run, n2.get("p"),
                                   n2.get("seed"), nd, nf, n2.get("d_ff"),
                                   n2.get("fall_dim_at_d_ff")])
        rec["null2_by_p_seed"] = sorted(n2tab)
        rec["null2_pairs_from_draws"] = sorted(rec["null2_pairs_from_draws"])
        rec["generator_degree"] = sorted(x for x in rec["generator_degree"] if x is not None)
        rec["D_max_computed"] = dict(rec["D_max_computed"])
        rec["cert_kinds"] = dict(rec["cert_kinds"])
        rec["top_form_tensor_check"] = dict(rec["top_form_tensor_check"])
        rec["s_poly_crosscheck"] = dict(rec["s_poly_crosscheck"])
        rec["oracle_agrees"] = dict(rec["oracle_agrees"])
        rec["null1_hist"] = dict(Counter(rec["null1_d_ff"]))
        rec["null1_pairs_distinct"] = sorted(set(rec["null1_pairs"]))
        rec["null3_identical_across_all_instances"] = (
            len(set(zip(rec["semaev_d_ff"], rec["semaev_fall_dim"]))) == 1)
        rec["null3_by_prime"] = {
            str(pp): sorted({(x, y) for i, (x, y) in
                             enumerate(zip(rec["semaev_d_ff"], rec["semaev_fall_dim"]))
                             if rec["instances"][i]["p"] == pp})
            for pp in sorted({i["p"] for i in rec["instances"]})}
        cells[f"{cell[0]},2,{cell[1]}"] = rec

    # NULL-2 minus Semaev per cell (the P3 table)
    p3 = {}
    for k, rec in cells.items():
        sem_pairs = set(zip(rec["semaev_d_ff"], rec["semaev_fall_dim"]))
        diffs = []
        # pair each null2 object with the Semaev draws at the same prime
        by_p = defaultdict(list)
        for (p, seed, nd, nf) in rec["null2_by_p_seed"]:
            by_p[p].append((seed, nd, nf))
        for inst, sd, sf in zip(rec["instances"], rec["semaev_d_ff"], rec["semaev_fall_dim"]):
            for (seed, nd, nf) in by_p.get(inst["p"], []):
                diffs.append({"p": inst["p"], "curve_seed": inst["curve_seed"],
                              "target": inst["target"], "seed": seed,
                              "d_ff_diff": (nd - sd) if nd is not None else None,
                              "fall_dim_diff": (nf - sf) if nf is not None else None})
        nz = [x for x in diffs if x["d_ff_diff"] or x["fall_dim_diff"]]
        p3[k] = {"n_pairs": len(diffs), "n_nonzero": len(nz),
                 "semaev_pairs_distinct": sorted(sem_pairs),
                 "distinct_diffs": sorted({(x["d_ff_diff"], x["fall_dim_diff"]) for x in diffs}),
                 "example_nonzero": nz[0] if nz else None}
    out["cells"] = {k: {kk: vv for kk, vv in v.items() if kk != "null1_pairs"}
                    for k, v in cells.items()}
    out["p3_null2_minus_semaev"] = p3

    # ---------- I: H-WIL ----------
    d = load("RUN-PFDR-5726af-hwil")
    tab = d["raw"]["table"]
    from math import comb
    bad = []
    ells = Counter()
    es = Counter()
    for row in tab:
        ells[row.get("ell")] += 1
        e = row.get("e", 2)
        es[e] += 1
        exp = min(comb(row["s"], row["j"]), comb(row["s"], row["j"] + e))
        if row["rank_meter_top"] != exp or row["expected"] != exp:
            bad.append(row)
    out["hwil"] = {"n_cells": len(tab), "below_max": bad,
                   "ell_kinds": dict(ells), "e_values": dict(es),
                   "s_values": sorted({r["s"] for r in tab}),
                   "p_values": sorted({r["p"] for r in tab}),
                   "j_range": sorted({(r["s"], r["j"]) for r in tab}),
                   "square_maps": sum(1 for r in tab if r.get("square_map")),
                   "independent_agree": all(
                       r["rank_meter_top"] == r["rank_independent"] for r in tab),
                   "sample_row": tab[0]}

    # ---------- H: nearby objects ----------
    d = load("RUN-PFDR-5726af-nearby-s3")
    mixed = d["raw"]["mixed"]
    mx = []
    for obj in mixed:
        dd, ff = derive_dff(obj["layers"])
        mx.append((dd, ff))
        if (dd, ff) != (obj.get("d_ff"), obj.get("fall_dim_at_d_ff")):
            mismatches.append(["mixed-recorded-vs-derived", obj.get("seed"), dd, ff,
                               obj.get("d_ff"), obj.get("fall_dim_at_d_ff")])
    nm = d["raw"]["non_monomial"]
    nmv = {"A": [], "B": [], "ell1_pow4_degree4_part_terms": set()}
    for obj in nm:
        nmv["ell1_pow4_degree4_part_terms"].add(obj.get("ell1_pow4_degree4_part_terms"))
        for tag, key in (("A", "reading_A_S3_plus_ell1^4"),
                         ("B", "reading_B_homogeneous_top_only")):
            sub = obj[key]
            dd, ff = derive_dff(sub["layers"])
            nmv[tag].append((dd, ff))
            if (dd, ff) != (sub.get("d_ff"), sub.get("fall_dim_at_d_ff")):
                mismatches.append(["nonmono-recorded-vs-derived", tag, dd, ff,
                                   sub.get("d_ff"), sub.get("fall_dim_at_d_ff")])
    nmv["A"] = sorted(set(nmv["A"])) + [len(nm)]
    nmv["B"] = sorted(set(nmv["B"])) + [len(nm)]
    nmv["ell1_pow4_degree4_part_terms"] = sorted(nmv["ell1_pow4_degree4_part_terms"])
    out["nearby"] = {"mixed_n": len(mx), "mixed_hist": dict(Counter(x[0] for x in mx)),
                     "mixed_pairs_distinct": sorted(set(mx)),
                     "non_monomial": nmv}

    # ---------- H-TOP ----------
    d = load("RUN-PFDR-5726af-htop")
    top = d["raw"]["S4_top_terms"]
    out["htop_raw_top_terms"] = top

    out["recorded_vs_derived_mismatches"] = mismatches
    json.dump(out, sys.stdout, indent=1, default=str)


if __name__ == "__main__":
    main()
