#!/usr/bin/env python3
"""R0 (TASK-20260904-0d66e3): independent regeneration of every EXP-PFDR-20ee58
summary table FROM THE RAW RECORDS ONLY.

Reads only  experiments/EXP-PFDR-20ee58/runs/*/raw-result.json  and
             experiments/EXP-PFDR-20ee58/runs/*/manifest.yaml (status field only),
recomputes every deficit as  row_count - full_rank - koszul_pairwise  out of the
raw per-degree `cumulative` layer records, rebuilds the derived tables
(per-arm deficit tables, residuals, affine fit, p-ladder, curve spread, null
generator-degree histograms, calibration table, s = 1 fixture ranks) with its
own code, and DIFFS them against analysis.json / analysis.md / execution-report.yaml.

It ALSO re-derives rows(D), ncols(D) and koszul(D) from first-principles
combinatorics (not from any producer artifact) for the mixed ring with 3s
squarefree digit variables and one free u, and checks them against the raw
counts.

No producer script is imported.  Writes nothing outside the task directory.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
from fractions import Fraction
from math import comb

ROOT = "/home/user/crypto-autoresearcher"
EXP = os.path.join(ROOT, "experiments/EXP-PFDR-20ee58")
RUNS = os.path.join(EXP, "runs")


# ---------------------------------------------------------------- combinatorics
def n_monomials_upto(n_sq: int, t: int) -> int:
    """# monomials  (squarefree subset S of n_sq digits) * u^e  with |S| + e <= t."""
    return sum(comb(n_sq, j) * (t - j + 1) for j in range(0, min(n_sq, t) + 1))


def rows_upto(n_sq: int, D: int, gen_degrees) -> int:
    return sum(n_monomials_upto(n_sq, D - d) for d in gen_degrees if D - d >= 0)


def koszul_cumulative(n_sq: int, D: int, gen_degrees) -> int:
    tot = 0
    g = [d for d in gen_degrees if d > 0]
    for i in range(len(g)):
        for j in range(i + 1, len(g)):
            md = D - g[i] - g[j]
            if md >= 0:
                tot += n_monomials_upto(n_sq, md)
    return tot


# ---------------------------------------------------------------- load
def load():
    out = {}
    for d in sorted(glob.glob(os.path.join(RUNS, "RUN-*"))):
        rid = os.path.basename(d)
        raw = json.load(open(os.path.join(d, "raw-result.json")))
        txt = open(os.path.join(d, "manifest.yaml")).read()
        m = re.search(r"^\s*status:\s*(\S+)\s*$", txt, re.M)
        out[rid] = {"raw": raw, "status": m.group(1) if m else None, "manifest_text": txt}
    return out


def deficit_from_layer(layer: dict) -> int:
    return layer["row_count"] - layer["full_rank"] - layer["koszul_pairwise"]


def main() -> int:
    runs = load()
    report = {"n_runs": len(runs), "statuses": {k: v["status"] for k, v in runs.items()}}
    problems = []

    # ---------------- stage 3/4 cells -------------------------------------
    cells = {}
    for rid, r in runs.items():
        raw = r["raw"]
        if "draws" not in raw["raw"]:
            continue
        m = raw["metrics"]
        s, p = m["s"], m["p"]
        degrees = m["degrees"]
        n_sq = 3 * s
        arms = {}
        for d in raw["raw"]["draws"]:
            cum = d["cumulative"]
            vec, rowchk, colchk, koschk = [], [], [], []
            for D in degrees:
                L = cum[str(D)]
                vec.append(deficit_from_layer(L))
                # raw internal consistency
                if L["row_count"] != d["rows"][degrees.index(D)]:
                    problems.append(f"{rid} {d['arm']} D{D}: rows mismatch inside raw")
                if L["full_rank"] != d["rank"][degrees.index(D)]:
                    problems.append(f"{rid} {d['arm']} D{D}: rank mismatch inside raw")
                if L["ncols_full"] != d["ncols"][degrees.index(D)]:
                    problems.append(f"{rid} {d['arm']} D{D}: ncols mismatch inside raw")
                if L["koszul_pairwise"] != d["koszul"][degrees.index(D)]:
                    problems.append(f"{rid} {d['arm']} D{D}: koszul mismatch inside raw")
                # first-principles counts
                gd = d["generator_degrees"]
                rowchk.append(rows_upto(n_sq, D, gd) == L["row_count"] + L["zero_product_rows"])
                colchk.append(n_monomials_upto(n_sq, D) == L["ncols_full"])
                koschk.append(koszul_cumulative(n_sq, D, gd) == L["koszul_pairwise"])
            if vec != d["deficit_vector"]:
                problems.append(f"{rid} {d['arm']}: recomputed deficit {vec} != recorded {d['deficit_vector']}")
            if vec != [d["deficit"][str(D)] for D in degrees]:
                problems.append(f"{rid} {d['arm']}: deficit dict disagrees with vector")
            if not all(rowchk):
                problems.append(f"{rid} {d['arm']}: first-principles row count mismatch {rowchk}")
            if not all(colchk):
                problems.append(f"{rid} {d['arm']}: first-principles column count mismatch {colchk}")
            if not all(koschk):
                problems.append(f"{rid} {d['arm']}: first-principles koszul count mismatch {koschk}")
            rec = {"deficit": vec, "rows": d["rows"], "ncols": d["ncols"], "rank": d["rank"],
                   "koszul": d["koszul"], "valid": d.get("valid"),
                   "generator_degrees": d["generator_degrees"],
                   "zero_product_rows": [cum[str(D)]["zero_product_rows"] for D in degrees],
                   "quotient_dim": d["quotient"]["dimension"],
                   "sol": d.get("sol"),
                   "deficit_series": d.get("deficit_series"),
                   "certificate_verified": d.get("certificate_verified")}
            for k in ("curve_seed", "target_seed", "null_seed", "cubic_seed"):
                if k in d:
                    rec[k] = d[k]
            arms.setdefault(d["arm"], []).append(rec)
        cells[f"s{s}-p{p}"] = {"run": rid, "s": s, "p": p, "degrees": degrees,
                               "status": r["status"], "arms": arms,
                               "certificates": {"total": m["planted_certificates_total"],
                                                "failed": m["planted_certificates_failed"]}}

    # per-arm deficit table
    table = {}
    all_vals = []
    for key, c in cells.items():
        for arm, recs in c["arms"].items():
            for i, D in enumerate(c["degrees"]):
                vals = [r["deficit"][i] for r in recs if r.get("valid", True)]
                all_vals.extend(vals)
                table.setdefault(arm, {}).setdefault(key, {})[str(D)] = {
                    "values": vals, "min": min(vals), "max": max(vals), "n": len(vals)}
    report["deficit_tables"] = table
    report["all_deficit_values_distinct"] = sorted(set(all_vals))
    report["total_deficit_entries"] = len(all_vals)

    # draw counts
    report["draw_counts"] = {k: {a: len(v) for a, v in c["arms"].items()} for k, c in cells.items()}
    report["twin_draw_total"] = sum(len(v) for c in cells.values() for v in c["arms"].values())

    # residuals / affine fit / p-ladder / curve spread (my own code)
    S_MAIN = (3, 4, 5)
    pts, per_sp, per_s, topo_band = [], {}, {}, {}
    for key, c in cells.items():
        if c["s"] not in S_MAIN or 8 not in c["degrees"]:
            continue
        i8 = c["degrees"].index(8)
        topo = [r["deficit"][i8] for r in c["arms"].get("null_topology", [])]
        if not topo:
            continue
        ref = sorted(topo)[len(topo) // 2]
        topo_band[key] = {"values": topo, "median": ref, "min": min(topo), "max": max(topo)}
        sem = [r for r in c["arms"].get("semaev", []) if r.get("valid", True)]
        res = [r["deficit"][i8] - ref for r in sem]
        per_sp[key] = {"s": c["s"], "p": c["p"], "sem_D8": [r["deficit"][i8] for r in sem],
                       "residuals": res, "curve_spread": max(res) - min(res) if res else None,
                       "null_band_width": max(topo) - min(topo)}
        per_s.setdefault(c["s"], []).extend(res)
        pts.extend((c["s"], x) for x in res)
    n = len(pts)
    xs = [Fraction(x) for x, _ in pts]
    ys = [Fraction(y) for _, y in pts]
    xb, yb = sum(xs) / n, sum(ys) / n
    sxx = sum((x - xb) ** 2 for x in xs)
    sxy = sum((x - xb) * (y - yb) for x, y in zip(xs, ys))
    alpha = sxy / sxx
    beta = yb - alpha * xb
    rss = sum((y - (alpha * x + beta)) ** 2 for x, y in zip(xs, ys))
    report["affine_fit_D8"] = {"n": n, "alpha": str(alpha), "beta": str(beta), "rss": str(rss),
                               "degenerate_zero_variance": rss == 0}
    report["residuals"] = {"per_cell": per_sp, "topology_band": topo_band,
                           "per_s": {str(k): {"values": v, "min": min(v), "max": max(v)} for k, v in per_s.items()}}
    report["p_ladder"] = {str(s): {str(v["p"]): v["residuals"] for k, v in per_sp.items() if v["s"] == s}
                          for s in S_MAIN}

    # null generator degrees + zero-product rows
    report["null_generator_degrees"] = {
        k: {a: sorted({str(r["generator_degrees"]) for r in recs}) for a, recs in c["arms"].items() if a.startswith("null")}
        for k, c in cells.items()}
    report["zero_product_rows_max"] = max(max(max(r["zero_product_rows"]) for r in recs)
                                          for c in cells.values() for recs in c["arms"].values())
    report["certificates"] = {k: c["certificates"] for k, c in cells.items()}
    report["certificate_verified_all"] = all(r.get("certificate_verified") in (True, None)
                                             for c in cells.values() for recs in c["arms"].values() for r in recs)
    report["deficit_series_equals_pairwise_everywhere"] = all(
        r["deficit_series"] == r["deficit"] for c in cells.values() for recs in c["arms"].values() for r in recs)

    # ---------------- calibration ------------------------------------------
    cal = runs["RUN-PFDR-20ee58-calib-gf2-n12"]["raw"]
    sem = cal["raw"]["result"]["semaev_arm"]["cumulative"]
    cum = {D: deficit_from_layer(sem[str(D)]) for D in (2, 3, 4, 5)}
    graded = [cum[2], cum[3] - cum[2], cum[4] - cum[3], cum[5] - cum[4]]
    report["calibration"] = {
        "rows": [sem[str(D)]["row_count"] for D in (2, 3, 4, 5)],
        "rank": [sem[str(D)]["full_rank"] for D in (2, 3, 4, 5)],
        "koszul_pairwise": [sem[str(D)]["koszul_pairwise"] for D in (2, 3, 4, 5)],
        "deficit_cumulative_recomputed": [cum[D] for D in (2, 3, 4, 5)],
        "deficit_graded_recomputed": graded,
        "deficit_graded_recorded": cal["metrics"]["deficit_graded_D2_D3_D4_D5"],
        "mixed_mode_deficit_pairwise": cal["metrics"]["mixed_mode_deficit_pairwise_D2_D3_D4"],
        "null_dreg": cal["raw"]["result"]["null_dreg_boolean"]["profile"]["deficit_cumulative"],
        "null_hist": {k: v["profile"]["deficit_cumulative"] for k, v in cal["raw"]["result"]["null_histogram_matched"].items()},
        "fixture_sha256_matches": cal["metrics"]["fixture_sha256_matches"],
    }
    if graded != cal["metrics"]["deficit_graded_D2_D3_D4_D5"]:
        problems.append("calibration: recomputed graded deficits differ from recorded metrics")

    # ---------------- s = 1 slice ------------------------------------------
    s1cells = runs["RUN-PFDR-20ee58-s1-slice"]["raw"]["raw"]["cells"]
    report["s1_slice"] = {f"p{c['p']}-B{c['B']}": {
        "identity": c["symbolic_identity"], "gen_degrees": c["generator_degrees"],
        "cumulative_rank": c["cumulative_rank"],
        "cumulative_deficit_recomputed": [deficit_from_layer(c["cumulative"][str(D)]) for D in range(4, 11)],
        "per_layer_rank": c["per_layer_rank"]} for c in s1cells}

    # ---------------- diff against the producer's own artifacts -------------
    aj = json.load(open(os.path.join(EXP, "analysis.json")))
    diffs = []
    for arm, cd in table.items():
        for key, byD in cd.items():
            for D, v in byD.items():
                got = aj["deficit_tables"][arm][key][D]
                if [got["values"], got["min"], got["max"], got["n"]] != [v["values"], v["min"], v["max"], v["n"]]:
                    diffs.append(f"deficit_tables[{arm}][{key}][{D}] mine={v} theirs={got}")
    for key, v in per_sp.items():
        got = aj["residuals_D8"]["per_cell"][key]
        if got["residuals"] != v["residuals"] or got["sem_D8"] != v["sem_D8"]:
            diffs.append(f"residuals[{key}] mine={v} theirs={got}")
    if float(alpha) != aj["affine_fit_D8"]["alpha"] or float(beta) != aj["affine_fit_D8"]["beta"]:
        diffs.append(f"affine fit mine alpha={alpha} beta={beta} theirs={aj['affine_fit_D8']}")
    if report["calibration"]["deficit_graded_recomputed"] != aj["calibration"]["deficit_graded_recomputed_D2_D5"]:
        diffs.append("calibration graded table differs from analysis.json")
    for k, v in report["s1_slice"].items():
        got = aj["s1_slice"]["per_cell"][k]
        if got["cumulative_rank_D4_D10"] != v["cumulative_rank"] or \
           got["cumulative_deficit_recomputed_D4_D10"] != v["cumulative_deficit_recomputed"]:
            diffs.append(f"s1 slice {k} differs")
    # execution-report headline strings
    er = open(os.path.join(EXP, "execution-report.yaml")).read()
    md = open(os.path.join(EXP, "analysis.md")).read()
    checks = {
        "exec_886x2304": "886 rows x 2304 columns per arm (contract: 886 x 2304); rank 885; koszul 1" in er,
        "exec_SEM_D8_zeros": "SEM_deficit_D8: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]" in er,
        "exec_calib_cum": "deficit_cumulative_D2_D5: [0, 1, 32, 1322]" in er,
        "exec_calib_graded": "deficit_graded_D2_D5: [0, 1, 31, 1290]" in er,
        "md_branch_M1": "**M1**" in md,
        "md_affine_alpha0": "'alpha': 0.0, 'beta': 0.0, 'n': 72, 'rss': 0" in md,
    }
    report["headline_string_checks"] = checks
    report["diffs_vs_producer"] = diffs
    report["internal_problems"] = problems

    # ---------------- branch-rule fidelity ---------------------------------
    src = open(os.path.join(EXP, "analyze.py")).read()
    report["branch_rule_source"] = {
        "all_zero_uses_residuals_not_raw_sem_D8": 'all_zero = (all(r == 0 for _, r in residual_points)' in src,
        "p3_covers_D5_D6_D7_only": 'for D in (5, 6, 7):' in src,
        "S_MAIN_excludes_s6": "S_MAIN = (3, 4, 5)" in src,
        "asserts_raw_equals_summary": 'assert vec == d["deficit_vector"]' in src,
    }
    print(json.dumps(report, indent=1, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
