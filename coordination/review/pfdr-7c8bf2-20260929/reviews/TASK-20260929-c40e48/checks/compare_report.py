#!/usr/bin/env python3
"""TASK-20260929-c40e48 J3: every number quoted in
experiments/EXP-PFDR-7c8bf2/execution-report.yaml against raw-result.json,
fits.json and execution.json, at the precision the report quotes.

Usage: python compare_report.py <execution-report.yaml> <run dir> <out.json>
"""
import json
import sys

import yaml


def r(x, nd):
    return round(x, nd)


def main(rep_path, run, out_path):
    rep = yaml.safe_load(open(rep_path))["execution_report"]
    raw = json.load(open(f"{run}/raw-result.json"))
    fits = json.load(open(f"{run}/fits.json"))
    ex = json.load(open(f"{run}/execution.json"))
    rows = []

    def chk(what, quoted, source_value, ok):
        rows.append({"quoted_in_report": what, "report_value": quoted, "raw_value": source_value, "agree": bool(ok)})

    chk("runs.completed[0].wall_seconds", rep["runs"]["completed"][0]["wall_seconds"], ex["wall_seconds"],
        r(ex["wall_seconds"], 1) == rep["runs"]["completed"][0]["wall_seconds"])
    chk("outcome_id", rep["outcome_id"], raw["outcome_id"], rep["outcome_id"] == raw["outcome_id"])
    chk("outcome_conditions_met", rep["outcome_conditions_met"], raw["outcome_conditions_met"],
        rep["outcome_conditions_met"] == raw["outcome_conditions_met"])
    obs = rep["observations"]
    for name, v in obs["primary_slopes_log2_ratio_vs_log2N_12_32"].items():
        for lab, key in (("primary", "primary_12_32"), ("sensitivity", "sensitivity_20_32")):
            f = raw["P3_P4_fits"][name][key]
            src = [f["slope"], f["lo"], f["hi"]]
            chk(f"{name} {lab}", v[lab], src, [r(x, 4) for x in src] == v[lab]
                and fits["series"][name][key] == f)
        if "window" in v:
            m = raw["P3_P4_fits"][name]["m"]
            chk(f"{name} window", v["window"], raw["windows"][str(m)], v["window"] == raw["windows"][str(m)])
            chk(f"{name} model", v["model"], 1 / (2 * m), r(1 / (2 * m), 4) == v["model"] or r(1 / (2 * m), 3) == v["model"])
    ex6 = [e for e in raw["condition_details"]["slope_interval_exclusions"]]
    chk("condition_detail: only S6-smallx excludes; [0.0841, 0.1242] excludes 0.0833",
        "S6-smallx alone, [0.0841, 0.1242], 0.0833", ex6,
        len(ex6) == 1 and ex6[0]["series"] == "S6-smallx" and [r(x, 4) for x in ex6[0]["ci"]] == [0.0841, 0.1242]
        and r(ex6[0]["excluded"], 4) == 0.0833)
    s6s = raw["P3_P4_fits"]["S6-smallx"]["sensitivity_20_32"]
    chk("condition_detail: S6 20..32 [0.0651, 0.1029]", [0.0651, 0.1029], [s6s["lo"], s6s["hi"]],
        [r(s6s["lo"], 4), r(s6s["hi"], 4)] == [0.0651, 0.1029])
    chk("condition_detail: every point estimate in its window", "no point estimate outside window",
        raw["condition_details"]["point_estimates_outside_window"], raw["condition_details"]["point_estimates_outside_window"] == [])
    mr = raw["P5_min"]
    chk("min_ratio value", obs["min_ratio"]["value"], mr["min_ratio"], r(mr["min_ratio"], 4) == obs["min_ratio"]["value"])
    row = mr["min_row"]
    chk("min_ratio row", obs["min_ratio"]["row"], row,
        obs["min_ratio"]["row"] == f"{row['file'].replace('.jsonl.gz', '')} bits {row['bits']} curve {row['curve']} {row['method']} {row['fb']} {row['engine']}")
    chk("rows_below_1_0 / rows_below_0_9", [obs["rows_below_1_0"], obs["rows_below_0_9"]],
        [mr["rows_below_1"], mr["rows_below_0_9"]], obs["rows_below_1_0"] == mr["rows_below_1"] == [] and obs["rows_below_0_9"] == mr["rows_below_0_9"] == [])
    for fb, v in obs["m3_base_geometric_mean_ratio_20_32"].items():
        if fb == "pairwise_overlap":
            src = raw["P6_bases"]["pairwise_overlap"]
            chk("P6 pairwise_overlap", v, src, all(v.values()) and all(src.values()) and len(v) == len(src) == 3)
            continue
        p = raw["P6_bases"]["per_base"][fb]
        chk(f"P6 {fb}", v, {"gm": p["geometric_mean_ratio"], "ci95": p["ci95"]},
            r(p["geometric_mean_ratio"], 3) == v["gm"] and [r(x, 3) for x in p["ci95"]] == v["ci95"])
    ctl = obs["controls"]
    a = raw["P7_controls"]["a_rho"]
    for lab, key in (("filtered_set", "subgroup(m=[2, 3],sizes=[],tol=0.15)"), ("unfiltered_set", "none")):
        w = a[key]["walk_exponent"]
        q = ctl["rho_walk_exponent"][lab]
        chk(f"rho walk exponent {lab}", q, [w["slope"], w["lo"], w["hi"], a[key]["n"]],
            [r(w["slope"], 3), r(w["lo"], 3), r(w["hi"], 3)] == q[:3] and q[3].startswith(f"n={a[key]['n']}"))
    h2 = raw["P7_controls"]["b_H2_relations_per_fb_slope_20_32"]
    sl = sorted(v["slope"] for v in h2.values())
    chk("H2: all eight series between -0.007 and -0.001", ctl["H2_relations_per_fb_slope_20_32"], {"min": sl[0], "max": sl[-1]},
        r(sl[0], 3) >= -0.007 and r(sl[-1], 3) <= -0.001)
    h1 = raw["P7_controls"]["c_H1_descriptive"]["per_m"]
    for m in ("3", "4", "5", "6", "7"):
        chk(f"H1 c_{m}", ctl["H1_descriptive_only"][f"c_{m}"], h1[m]["c_m"], r(h1[m]["c_m"], 3) == ctl["H1_descriptive_only"][f"c_{m}"])
        chk(f"H1 ks_reject_1pct m{m}", ctl["H1_descriptive_only"]["ks_reject_1pct"][f"m{m}"],
            h1[m]["ks_randomized_pit_vs_poisson"]["reject_1pct"],
            ctl["H1_descriptive_only"]["ks_reject_1pct"][f"m{m}"] == h1[m]["ks_randomized_pit_vs_poisson"]["reject_1pct"])
    d = raw["P7_controls"]["d_table_share_at_32_bits"]
    for name, q in ctl["table_share_at_32_bits_median"].items():
        v = d[name]["median"]
        nd = 3 if q >= 0.01 else 4
        chk(f"table share 32 bits {name}", q, v, r(v, nd) == q)
    # anomalies and gates
    chk("anomaly P7(a) n = 92 not 110; 18 curves", "n = 92; 18", {"none_n": a["none"]["n"], "110-92": 110 - a["none"]["n"]},
        a["none"]["n"] == 92)
    chk("anomaly P7(c) m = 7 p = 0.0098", 0.0098, h1["7"]["ks_randomized_pit_vs_poisson"]["p"],
        r(h1["7"]["ks_randomized_pit_vs_poisson"]["p"], 4) == 0.0098)
    p1 = raw["P1_consistency"]
    chk("I-2 counts 165 + 165, 0 missing, 0 unequal", rep["gates_and_invalidation_checks"]["I-2_twin_consistency"],
        {k: (v["mitm_rows_checked"], len(v["missing_twin"]), len(v["unequal"])) for k, v in p1.items()},
        all(v["mitm_rows_checked"] == 165 and not v["missing_twin"] and not v["unequal"] for v in p1.values()))
    rc = raw["readme_row_count_crosscheck"]
    chk("readme_row_count_crosscheck all equal", rep["gates_and_invalidation_checks"]["readme_row_count_crosscheck"], rc,
        all(v["readme"] == v["file"] for v in rc.values()))
    chk("I-1 5/5 digests equal archive", rep["gates_and_invalidation_checks"]["I-1_inputs_readable_and_digest_equal_to_archive"],
        {k: v["sha256"] == v["archive_sha256"] for k, v in raw["inputs"].items()},
        all(v["sha256"] == v["archive_sha256"] for v in raw["inputs"].values()) and len(raw["inputs"]) == 5)
    chk("I-3 solver_modules_loaded empty", rep["gates_and_invalidation_checks"]["I-3_no_solver_module_and_no_results_file_written"],
        raw["solver_modules_loaded"], raw["solver_modules_loaded"] == [])
    chk("TW-FLOOR not fired", rep["tripwires"]["TW-FLOOR"], mr["rows_below_0_9"], mr["rows_below_0_9"] == [])
    n_ok = sum(x["agree"] for x in rows)
    json.dump({"n": len(rows), "n_agree": n_ok, "rows": rows}, open(out_path, "w"), indent=1, default=str)
    print(f"{n_ok}/{len(rows)} agree")
    for x in rows:
        if not x["agree"]:
            print("DISAGREE:", json.dumps(x, default=str))


if __name__ == "__main__":
    main(*sys.argv[1:4])
