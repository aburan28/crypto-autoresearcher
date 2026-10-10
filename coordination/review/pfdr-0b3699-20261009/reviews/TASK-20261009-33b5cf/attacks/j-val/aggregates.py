"""J-VAL (4) continued: recompute from the recount every count-derived record of
analysis.json and cells.jsonl (RUN-PFDR-0b3699-analysis), TASK-20261009-33b5cf.

Input: the per-curve recount table written by recount.py (scratch), design.json (S,
K_plant), analysis.json, cells.jsonl. Formulas from specification.yaml
analysis.statistic (CC-8 pooled per CC-10), analysis.dispersion_robustness (point
estimate only), controls (planted_target, PC-R-T (ii)), tail_checks (histograms,
count >= 3 lists, top-10 share). Standard library only; no producer code.
Integer quantities are compared exactly; floats derived deterministically from the
counts are compared to 1e-9 relative. Simulated quantities (calibrated_p, t_A, U_A,
bootstrap intervals) are not recomputed here.
The PRIMARY set is the sampling rule's (sampled curves, every arm; null arms, all
curves); every other comparison is labelled supplementary.
TB recount under the PDI-3 reading (star pairs only) is checked for the one instance
where the plain-CC-1 reading differs.
No seeds. Usage: python aggregates.py <repo> <percurve.jsonl.gz> <out.json>
"""
import gzip
import json
import math
import os
import sys
from collections import Counter

AN = "experiments/EXP-PFDR-0b3699/runs/RUN-PFDR-0b3699-analysis"
DESIGN = "experiments/EXP-PFDR-0b3699/runs/RUN-PFDR-0b3699-p0-design/design.json"
R = ["random_sub_r0", "random_sub_r1", "random_sub_r2"]


def cell(rows, x_of, triple):
    CX = sum(x_of(r) for r in rows)
    tot = 0
    s2 = 0.0
    s2_6 = 0  # 6 x sum_s2 as an integer
    for r in rows:
        a = [r[t] for t in triple]
        tot += sum(a)
        s2_6 += 3 * sum(v * v for v in a) - sum(a) ** 2
    CR = tot / 3
    s2 = s2_6 / 6
    V = max(s2, CR)
    SD = math.sqrt(4 * V / 3)
    return {"C_X": CX, "C_R": CR, "3C_R": tot, "sum_s2": s2, "6sum_s2": s2_6, "V": V, "SD_null": SD,
            "kappa_rel": CX / CR, "z": (CX - CR) / SD, "SE": SD / CR, "curves": len(rows)}


def close(a, b, tol=1e-9):
    if a is None or b is None:
        return a == b
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def main():
    repo, pc, outp = sys.argv[1:4]
    rows = [json.loads(l) for l in gzip.open(pc, "rt")]
    design = json.load(open(os.path.join(repo, DESIGN)))
    an = json.load(open(os.path.join(repo, AN, "analysis.json")))
    cells = [json.loads(l) for l in open(os.path.join(repo, AN, "cells.jsonl"))]
    res = {"cells_jsonl": [], "analysis_json": [], "mismatches": []}

    def chk(where, name, mine, theirs, integer=False, primary=False):
        ok = (mine == theirs) if integer else close(mine, theirs)
        rec = {"where": where, "name": name, "recomputed": mine, "recorded": theirs, "equal": ok,
               "set": "primary" if primary else "supplementary"}
        res["analysis_json" if where.startswith("analysis") else "cells_jsonl"].append(rec)
        if not ok:
            res["mismatches"].append(rec)

    scopes = {"band": rows, "rung30": [r for r in rows if r["bits"] == 30],
              "rung32": [r for r in rows if r["bits"] == 32]}
    # cells.jsonl
    for c in cells:
        arm, scope = c["arm"], c["scope"]
        rr = scopes[scope]
        if arm.startswith("null:"):
            nm = arm[5:]
            if nm == "known_null_sub":
                x, tri = "known_null_sub", R
            else:
                x = "random_sub_" + nm.split("_")[0]
                tri = [t for t in R if t != x] + ["known_null_sub"]
            prim = True
        else:
            x, tri = arm, R
            prim = arm == "known_null_sub"
        mine = cell(rr, lambda r: r[x], tri)
        tag = f"cells.jsonl[{arm}|{scope}]"
        chk(tag, "C_X", mine["C_X"], int(round(c["C_X"])) if float(c["C_X"]).is_integer() else c["C_X"], integer=True, primary=prim)
        chk(tag, "3C_R(integer)", mine["3C_R"], int(round(3 * c["C_R"])), integer=True, primary=True)
        chk(tag, "6sum_s2(integer)", mine["6sum_s2"], int(round(6 * c["sum_s2"])), integer=True, primary=True)
        for k in ("V", "SD_null", "kappa_rel", "z", "SE"):
            chk(tag, k, mine[k], c[k], primary=prim)
        chk(tag, "curves", mine["curves"], c["curves"], integer=True, primary=True)

    # analysis.json primary / mutation / contrast / cells
    a_cell = cell(rows, lambda r: r["small_x"], R)
    m_cell = cell(rows, lambda r: r["small_x_offset"], R)
    for k in ("C_X", "C_R", "V", "SD_null", "kappa_rel", "z", "SE", "curves"):
        chk("analysis.primary", k, a_cell[k], an["primary"][k], integer=(k in ("C_X", "curves")))
        chk("analysis.mutation", k, m_cell[k], an["mutation"][k], integer=(k in ("C_X", "curves")))
    chk("analysis.primary", "C_A", a_cell["C_X"], an["primary"]["C_A"], integer=True)
    zD = (a_cell["C_X"] - m_cell["C_X"]) / math.sqrt(2 * a_cell["V"])
    chk("analysis.contrast", "z_Delta", zD, an["contrast"]["z_Delta"])
    chk("analysis.contrast", "C_A_admitted", a_cell["C_X"], an["contrast"]["C_A_admitted"], integer=True)
    chk("analysis.contrast", "C_M_admitted", m_cell["C_X"], an["contrast"]["C_M_admitted"], integer=True)
    chk("analysis.contrast", "V_admitted", a_cell["V"], an["contrast"]["V_admitted"])
    for arm, rec in an["cells"].items():
        mine = cell(rows, lambda r, a=arm: r[a], R)
        for k in ("C_X", "C_R", "sum_s2", "V", "SD_null", "kappa_rel", "z", "SE", "curves"):
            chk(f"analysis.cells[{arm}]", k, mine[k], rec[k], integer=(k in ("C_X", "curves")),
                primary=(arm == "known_null_sub" or k in ("C_R", "sum_s2", "curves")))
        for b in ("30", "32"):
            mb = cell(scopes["rung" + b], lambda r, a=arm: r[a], R)
            for k in ("C_X", "C_R", "V", "z", "kappa_rel"):
                if k in rec["per_rung"][b]:
                    chk(f"analysis.cells[{arm}].per_rung[{b}]", k, mb[k], rec["per_rung"][b][k],
                        integer=(k == "C_X"), primary=(arm == "known_null_sub" or k in ("C_R",)))
    # per-rung small_x sign
    for b in ("30", "32"):
        mb = cell(scopes["rung" + b], lambda r: r["small_x"], R)
        chk("analysis.per_rung_small_x_sign", b, mb["kappa_rel"] - 1, an["per_rung_small_x_sign"][b])
    # PC-R-T
    S = {int(b): set(v) for b, v in design["S"].items()}
    Kp = sum(len(v) for v in S.values())
    pt = cell(rows, lambda r: r["planted_target"], R)
    chk("analysis.controls.PC-R-T", "K_plant_realised", Kp, an["controls"]["PC-R-T"]["K_plant_realised"], integer=True)
    chk("analysis.controls.PC-R-T", "C_planted_target_minus_C_R", pt["C_X"] - pt["C_R"],
        an["controls"]["PC-R-T"]["C_planted_target_minus_C_R"])
    chk("analysis.controls.PC-R-T", "ii_within_4SD", abs(pt["C_X"] - pt["C_R"] - Kp) <= 4 * pt["SD_null"],
        an["controls"]["PC-R-T"]["ii_within_4SD_of_K_plant"], integer=True)
    pd = cell(rows, lambda r: r["planted_sub"], R)
    chk("analysis.controls.PC-R-D", "z", pd["z"], an["controls"]["PC-R-D"]["z"])
    chk("design.json", "K_plant_b == |S_b|", {b: len(S[b]) for b in (30, 32)},
        {int(b): v for b, v in design["K_plant_b"].items()}, integer=True, primary=True)
    # tail checks: histograms and >= 3 lists
    for arm in ("small_x", "small_x_offset"):
        h = Counter(r[arm] for r in rows)
        chk(f"analysis.tail_checks[{arm}]", "per_curve_histogram", {str(k): v for k, v in sorted(h.items())},
            {k: v for k, v in sorted(an["tail_checks"][arm]["per_curve_histogram"].items(), key=lambda kv: int(kv[0]))},
            integer=True)
        chk(f"analysis.tail_checks[{arm}]", "zero_count_curves", h[0], an["tail_checks"][arm]["zero_count_curves"], integer=True)
        ge3 = sorted([r["bits"], r["curve"], r[arm]] for r in rows if r[arm] >= 3)
        chk(f"analysis.tail_checks[{arm}]", "curves_with_count_ge_3 (all curves)", ge3,
            sorted(an["tail_checks"][arm]["curves_with_count_ge_3"]), integer=True)
        ge3s = sorted([r["bits"], r["curve"], r[arm]] for r in rows if r[arm] >= 3 and r["in_sample"])
        rec_s = sorted(x for x in an["tail_checks"][arm]["curves_with_count_ge_3"]
                       if any(r["bits"] == x[0] and r["curve"] == x[1] and r["in_sample"] for r in rows))
        chk(f"analysis.tail_checks[{arm}]", "curves_with_count_ge_3 restricted to the sample", ge3s, rec_s,
            integer=True, primary=True)
    for arm in R:
        h = Counter(r[arm] for r in rows)
        chk("analysis.tail_checks.randoms_histogram", arm, {str(k): v for k, v in sorted(h.items())},
            {k: v for k, v in sorted(an["tail_checks"]["randoms_histogram"][arm].items(), key=lambda kv: int(kv[0]))},
            integer=True, primary=True)
    # top-10 share of the excess (as smallx-tt4-localise.json): d_j = n_X,j - mean of the triple
    def top10(x, tri):
        d = [r[x] - sum(r[t] for t in tri) / 3 for r in rows]
        tot = sum(d)
        if tot <= 0:
            return None
        return sum(sorted(d, reverse=True)[:10]) / tot
    for nm, x, tri in [("r0", "random_sub_r0", ["random_sub_r1", "random_sub_r2", "known_null_sub"]),
                       ("r1", "random_sub_r1", ["random_sub_r0", "random_sub_r2", "known_null_sub"]),
                       ("r2", "random_sub_r2", ["random_sub_r0", "random_sub_r1", "known_null_sub"]),
                       ("known_null_sub", "known_null_sub", R)]:
        chk("analysis.tail_checks.null_pseudo_cells_top10_share", nm, top10(x, tri),
            an["tail_checks"]["null_pseudo_cells_top10_share"][nm], primary=True)
    for arm in ("small_x", "small_x_offset"):
        chk(f"analysis.tail_checks[{arm}]", "top10_share_of_excess", top10(arm, R),
            an["tail_checks"][arm]["top10_share_of_excess"])
    # secondary totals
    arms8 = ["subgroup", "small_x", "random_sub_r0", "random_sub_r1", "random_sub_r2", "known_null_sub",
             "planted_sub", "small_x_offset"]
    for arm in arms8:
        prim = arm in R or arm == "known_null_sub"
        chk("analysis.secondary.TB_counts", arm, sum(r[arm + "|TB"] for r in rows), an["secondary"]["TB_counts"][arm],
            integer=True, primary=prim)
        chk("analysis.secondary.TT_sign_only_counts_CC-1b", arm, sum(r[arm + "|sign"] for r in rows),
            an["secondary"]["TT_sign_only_counts_CC-1b"][arm], integer=True, primary=prim)
        chk("analysis.secondary.TT_R_star_sum (vs TT count)", arm, sum(r[arm] for r in rows),
            an["secondary"]["TT_R_star_sum"][arm], integer=True, primary=prim)
    # H1c point estimate and dispersion robustness point estimates
    nb = [sum(r[t] for t in R) / 3 for r in rows]
    s2 = sum((3 * sum(r[t] ** 2 for t in R) - sum(r[t] for t in R) ** 2) / 6 for r in rows)
    D_R = s2 / sum(nb)
    chk("analysis.secondary.H1c_TT4_dispersion", "D_pooled", D_R, an["secondary"]["H1c_TT4_dispersion"]["D_pooled"], primary=True)
    for arm, key in (("small_x", "rho_A"), ("small_x_offset", "rho_M")):
        CX = sum(r[arm] for r in rows)
        kh = CX / sum(nb)
        DA = (sum((r[arm] - nbj - (kh - 1) * nbj) ** 2 for r, nbj in zip(rows, nb)) - s2 / 3) / sum(nb)
        chk("analysis.dispersion_robustness", key + " (point)", DA / D_R, an["dispersion_robustness"][key]["rho"])
    Vs = a_cell["V"] * max(1.0, an["dispersion_robustness"]["rho_A"]["interval_95"][1])
    chk("analysis.dispersion_robustness", "z_A_with_V_scaled", (a_cell["C_X"] - a_cell["C_R"]) / math.sqrt(4 * Vs / 3),
        an["dispersion_robustness"]["z_A_with_V_scaled"])
    # declared_metrics consistency with the recomputed values
    dm = an["declared_metrics"]
    chk("analysis.declared_metrics", "C_A", a_cell["C_X"], dm["C_A"], integer=True)
    chk("analysis.declared_metrics", "C_R", a_cell["C_R"], dm["C_R"])
    chk("analysis.declared_metrics", "V", a_cell["V"], dm["V"])
    chk("analysis.declared_metrics", "z_A", a_cell["z"], dm["z_A"])
    chk("analysis.declared_metrics", "z_M", m_cell["z"], dm["z_M"])
    chk("analysis.declared_metrics", "z_Delta", zD, dm["z_Delta"])
    chk("analysis.declared_metrics", "kappa_M", m_cell["kappa_rel"], dm["kappa_M"])
    res["n_compared"] = len(res["analysis_json"]) + len(res["cells_jsonl"])
    res["n_primary"] = sum(1 for x in res["analysis_json"] + res["cells_jsonl"] if x["set"] == "primary")
    res["n_mismatch"] = len(res["mismatches"])
    res["n_mismatch_primary"] = sum(1 for x in res["mismatches"] if x["set"] == "primary")
    json.dump(res, open(outp, "w"), indent=1, default=str)
    print("compared", res["n_compared"], "primary", res["n_primary"], "mismatches", res["n_mismatch"],
          "primary mismatches", res["n_mismatch_primary"])
    for m in res["mismatches"]:
        print("MISMATCH", json.dumps(m, default=str)[:400])


if __name__ == "__main__":
    main()
