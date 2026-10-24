#!/usr/bin/env python3
"""J2 definition probe (TASK-20261022-a846f4), written after reading the driver.

Re-implements (without importing producer code) the summary definitions found in
experiments/EXP-CZLIFT-a255fc/implementation/run.py::summarize and
measure_curve, and compares them with the definition stated in H-CZLIFT-27a184
("every coverage cell with N >= 30 ... median in [0.8, 1.2]").  Lists the raw
rows that make the two disagree.  Cells are taken from raw-result.json; they
were verified cell by cell against the validator's independent recomputation
(j2_recompute.json, zero mismatches).
Usage: j2_definitions.py RAW_1E5 RAW_3E5 OUT_JSON
"""
import json
import math
import statistics
import sys


def stats(ratios):
    s = sorted(ratios)
    n = len(s)
    return {"cells": n,
            "median_upper_element_s[n//2]": s[n // 2] if s else None,
            "median_conventional": statistics.median(s) if s else None,
            "frac_above_1p5": sum(r > 1.5 for r in s) / n if n else None,
            "frac_below_0p5": sum(r < 0.5 for r in s) / n if n else None,
            "min": s[0] if s else None, "max": s[-1] if s else None}


def slope(xs, ys):
    if len(xs) < 2:
        return None
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    return None if sxx == 0 else sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx


def main():
    out = {}
    for rid, path in (("RUN-CZLIFT-ca7450", sys.argv[1]), ("RUN-CZLIFT-b1dce4", sys.argv[2])):
        raw = json.load(open(path))
        m = raw["metrics"]
        cells = [dict(c, label=cv["label"]) for cv in raw["raw"]["curves"] for c in cv["coverage"]]
        code = [c for c in cells if c["n_points"] >= 30 and c["model_distinct"] <= 0.9 * c["N_p"]]
        hyp = [c for c in cells if c["n_points"] >= 30]
        excluded = [c for c in hyp if not (c["model_distinct"] <= 0.9 * c["N_p"])]
        sc, sh = stats([c["ratio_to_model"] for c in code]), stats([c["ratio_to_model"] for c in hyp])
        border = sorted(hyp, key=lambda c: abs(c["model_distinct"] / c["N_p"] - 0.9))[:4]
        # growth slope per code: H >= 100 and N >= 3; h_half scaling: >= 3 resolved primes, loglog H_half vs log p
        gs, hh = {}, {}
        for cv in raw["raw"]["curves"]:
            hs = sorted(int(h) for h in cv["counts"])
            sel = [h for h in hs if h >= 100 and cv["counts"][str(h)] >= 3]
            gs[cv["label"]] = {"validator": slope([math.log(math.log(h)) for h in sel],
                                                 [math.log(cv["counts"][str(h)]) for h in sel]),
                               "recorded": m["growth_slopes"][cv["label"]]["measured"], "fit_points": len(sel),
                               "fit_H": sel}
            pts = [(math.log(int(p)), math.log(math.log(h))) for p, h in cv["h_half"].items() if h >= 10]
            if len(pts) >= 3:
                hh[cv["label"]] = {"validator": slope([a for a, _ in pts], [b for _, b in pts]),
                                   "recorded": m["h_half_scaling"].get(cv["label"], {}).get("slope"),
                                   "resolved": len(pts),
                                   "recorded_resolved": m["h_half_scaling"].get(cv["label"], {}).get("resolved_primes")}
            elif cv["label"] in m["h_half_scaling"]:
                hh[cv["label"]] = {"validator": None, "recorded": m["h_half_scaling"][cv["label"]]}
        out[rid] = {
            "manifest": {k: m[k] for k in ("coverage_cells", "coverage_ratio_median",
                                           "coverage_ratio_frac_above_1p5", "coverage_ratio_frac_below_0p5")},
            "code_definition": sc,
            "code_definition_reproduces_manifest_exactly": (
                sc["cells"] == m["coverage_cells"] and sc["median_upper_element_s[n//2]"] == m["coverage_ratio_median"]
                and sc["frac_above_1p5"] == m["coverage_ratio_frac_above_1p5"]
                and sc["frac_below_0p5"] == m["coverage_ratio_frac_below_0p5"]),
            "hypothesis_definition": sh,
            "rows_excluded_by_saturation_filter": [
                {k: c[k] for k in ("label", "p", "H", "N_p", "n_points", "distinct", "model_distinct", "ratio_to_model")}
                for c in excluded],
            "cells_nearest_saturation_threshold": [
                {"label": c["label"], "p": c["p"], "H": c["H"], "model_over_N_p": c["model_distinct"] / c["N_p"]} for c in border],
            "growth_slopes": gs,
            "h_half_scaling": hh,
        }
    json.dump(out, open(sys.argv[3], "w"), indent=1)
    for rid, r in out.items():
        print("=====", rid)
        print(" manifest:", r["manifest"])
        print(" code def:", r["code_definition"], "reproduces:", r["code_definition_reproduces_manifest_exactly"])
        print(" hyp  def:", r["hypothesis_definition"])
        print(" excluded rows:", len(r["rows_excluded_by_saturation_filter"]),
              [(c["label"][:6], c["p"], c["H"], c["n_points"], c["N_p"], round(c["ratio_to_model"], 4)) for c in r["rows_excluded_by_saturation_filter"]])
        print(" nearest threshold:", r["cells_nearest_saturation_threshold"])
        print(" growth:", {k: (v["validator"], v["recorded"], v["validator"] == v["recorded"], v["fit_H"]) for k, v in r["growth_slopes"].items()})
        print(" h_half_scaling:", r["h_half_scaling"])


if __name__ == "__main__":
    main()
