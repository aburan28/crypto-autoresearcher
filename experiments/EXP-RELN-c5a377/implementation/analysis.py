"""C-5 verdict rule (AMD-20260926-a7d25d), applied verbatim with the literal
readings accepted by AMD-20260929-988139 (OQ-2..OQ-5) and the fail-closed
rulings of AMD-20260929-cc7226 (protocol v4):

  Under delta_proof: supercritical-enriched iff delta_proof lower 95% CI > 1/4
  at both budgets and all three sizes with a flat or rising trend, AND the
  Erdos-Renyi null with identical |V|, |E| does not also exceed 1/4.
  Certified subcritical iff the giant component fraction < 0.05 and
  cycle_rank <= 2 * (number of components with a cycle) at all sizes.
  Otherwise inconclusive.

Literal readings (not protocol changes):
  * lower 95% CI (per size x budget): Student-t over the three seed fixtures,
    mean - t_{0.975,2} sd / sqrt(3); undefined (fails) if any delta_proof is null.
  * flat or rising trend (per budget): the upper end of the two-sided 95%
    t-interval of the OLS slope of delta_proof on bits over the nine fixtures
    is >= 0 (the slope is not significantly negative).
  * ER "also exceeds 1/4" in a size x budget cell when the mean ER delta_proof
    over its 3 x 32 replicates (null replicates excluded) is > 1/4; the
    enrichment clause requires that this happens in NO cell.
  * certified subcritical: both inequalities at every fixture and both budgets.
  * if both the supercritical and the subcritical rules fire, the verdict is
    inconclusive with reason 'both_rules_fired'.

Protocol v4 rulings (AMD-20260929-cc7226):
  * F-3: a size x budget cell with no feasible ER replicate has the ER clause
    'undetermined'. An undetermined cell cannot satisfy supercritical-enriched:
    if every other supercritical clause holds and no determined cell has ER
    exceeding 1/4, the supercritical rule is 'undetermined' and the verdict is
    inconclusive. Feasible ER replicates are counted per cell.
  * F-4: known_positive = not_exercised is neither a pass nor a defect and does
    not change the verdict. Cells where any fixture's known positive was not
    exercised (or did not pass) are listed as lacking known-positive power
    confirmation; negative conclusions are scoped to the other cells.
  * FX-4 (F-6): where known_false = not_exercised the LP log recovery fraction
    is reported as 'undetermined'.

  python3 analysis.py <raw-result.json> [--out analysis.json]
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

SIZES = (16, 20, 24)
BUDGETS = ("A1", "A2")
GATE = 0.25
T975 = {2: 4.302652729911275, 7: 2.364624251592785}


def t975(df: int) -> float:
    if df in T975:
        return T975[df]
    from scipy.stats import t  # only for non-frozen shapes (tests)
    return float(t.ppf(0.975, df))


def lower_ci(vals):
    if len(vals) < 2 or any(v is None for v in vals):
        return None
    n = len(vals)
    return statistics.fmean(vals) - t975(n - 1) * statistics.stdev(vals) / math.sqrt(n)


def slope_upper_ci(xs, ys):
    if len(ys) < 3 or any(y is None for y in ys):
        return None, None
    n = len(xs)
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - b * mx
    sse = sum((y - a - b * x) ** 2 for x, y in zip(xs, ys))
    se = math.sqrt(sse / (n - 2) / sxx)
    return b, b + t975(n - 2) * se


def table(cells: list[dict]) -> dict:
    """{(bits, budget): [per-fixture rows]}"""
    out = {}
    for c in cells:
        bits = c["fixture"]["bits"]
        for blk in c["budgets"]:
            g = blk["graph"]
            er_reps = blk["null_er"]["replicates"]
            er = [r["delta_proof"] for r in er_reps if r is not None]
            rw = [r["delta_proof"] for r in blk["null_rewire"]["replicates"]]
            kp = (blk.get("known_positive") or {}).get("status")
            kf = (blk.get("known_false") or {}).get("status")
            out.setdefault((bits, blk["budget"]), []).append({
                "fixture_id": c["fixture_id"], "seed": c["fixture"]["seed"],
                "delta_proof": g["delta_proof"], "delta_ratio": g["delta_ratio"],
                "cycle_rank": g["cycle_rank"], "E": g["E"], "V": g["V"],
                "giant_component_fraction": g["giant_component_fraction"],
                "components_with_cycle": g["components_with_cycle"],
                "er_delta_proof": er, "er_feasible_replicates": sum(1 for r in er_reps if r is not None),
                "er_replicates": len(er_reps), "rewire_delta_proof": rw,
                "known_positive_status": kp, "known_false_status": kf,
                "lp_recovery_fraction": "undetermined" if kf == "not_exercised"
                else blk["recovery"]["lp_recovery_fraction"],
                "charged_work_over_sqrt_q": blk["charged"]["charged_work_over_sqrt_q"]})
    return out


def verdict(cells: list[dict]) -> dict:
    tab = table(cells)
    missing = [(b, bu) for b in SIZES for bu in BUDGETS if len(tab.get((b, bu), [])) != 3]
    per_cell = {}
    ci_ok, er_exceeds_any = True, False
    er_undetermined_cells, no_power_cells = [], []
    for b in SIZES:
        for bu in BUDGETS:
            rows = sorted(tab.get((b, bu), []), key=lambda r: r["seed"])
            dp = [r["delta_proof"] for r in rows]
            lci = lower_ci(dp) if len(rows) == 3 else None
            n_feasible = sum(r["er_feasible_replicates"] for r in rows)
            er_all = [v for r in rows for v in r["er_delta_proof"] if v is not None]
            er_mean = statistics.fmean(er_all) if er_all else None
            if n_feasible == 0:
                er_exc = "undetermined"
                er_undetermined_cells.append(f"{b}-{bu}")
            else:
                er_exc = er_mean is not None and er_mean > GATE
                er_exceeds_any |= er_exc
            kp_ok = len(rows) == 3 and all(r["known_positive_status"] == "pass" for r in rows)
            if not kp_ok:
                no_power_cells.append(f"{b}-{bu}")
            ok = lci is not None and lci > GATE
            ci_ok &= ok
            per_cell[f"{b}-{bu}"] = {"delta_proof": dp, "lower_95_ci": lci, "ci_gt_quarter": ok,
                                     "er_mean_delta_proof": er_mean, "er_exceeds_quarter": er_exc,
                                     "er_feasible_replicates": n_feasible,
                                     "er_replicates": sum(r["er_replicates"] for r in rows),
                                     "known_positive_statuses": [r["known_positive_status"] for r in rows],
                                     "known_positive_power_confirmed": kp_ok,
                                     "rows": rows}
    trend = {}
    trend_ok = True
    for bu in BUDGETS:
        xs, ys = [], []
        for b in SIZES:
            for r in tab.get((b, bu), []):
                xs.append(b)
                ys.append(r["delta_proof"])
        slope, up = slope_upper_ci(xs, ys)
        ok = up is not None and up >= 0
        trend[bu] = {"slope_per_bit": slope, "slope_upper_95_ci": up, "flat_or_rising": ok}
        trend_ok &= ok
    supercritical = (not missing) and ci_ok and trend_ok and not er_exceeds_any
    if supercritical and er_undetermined_cells:
        supercritical = "undetermined"
    sub_rows = [r for rows in tab.values() for r in rows]
    subcritical = (not missing) and bool(sub_rows) and all(
        r["giant_component_fraction"] < 0.05 and r["cycle_rank"] <= 2 * r["components_with_cycle"]
        for r in sub_rows)
    if missing:
        v, why = "inconclusive", f"missing cells {missing}"
    elif supercritical == "undetermined":
        v, why = "inconclusive", (f"AMD-20260929-cc7226 F-3: ER null infeasible (no feasible replicate) in "
                                  f"{er_undetermined_cells}; supercritical-enriched cannot be supported"
                                  + ("; subcritical rule also fired" if subcritical else ""))
    elif supercritical and subcritical:
        v, why = "inconclusive", "both_rules_fired"
    elif supercritical is True:
        v, why = "supercritical-enriched", "C-5 supercritical clauses all hold"
    elif subcritical:
        v, why = "certified-subcritical", "C-5 subcritical clauses hold at every fixture and budget"
    else:
        v, why = "inconclusive", "neither C-5 rule holds"
    res = {"verdict": v, "reason": why, "clauses": {
        "ci_gt_quarter_all_cells": ci_ok, "trend_flat_or_rising_both_budgets": trend_ok,
        "er_null_exceeds_quarter_in_any_cell": er_exceeds_any,
        "er_null_undetermined_cells": er_undetermined_cells,
        "supercritical_rule": supercritical, "subcritical_rule": subcritical},
        "known_positive": {
            "cells_lacking_power_confirmation": no_power_cells,
            "negative_conclusion_scope_cells": [k for k in per_cell if k not in no_power_cells],
            "note": "AMD-20260929-cc7226 F-4: a negative or ER-matched reading in a listed cell lacks "
                    "known-positive power confirmation; negative conclusions are scoped to the other cells. "
                    "The verdict is unchanged by this list."},
        "per_cell": per_cell, "trend": trend}
    if v == "supercritical-enriched":
        res["definitional_impediment"] = (
            "C-5: may not be read as crossing RT-1472's gate until the RT-1472 source is acquired "
            "and a later protocol amendment maps delta_proof onto it (no amendment through v4 does).")
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("raw_result")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    raw = json.loads(Path(a.raw_result).read_text())
    if any("smoke" in c.get("ns", "") for c in raw["cells"]):
        print("REFUSED: smoke-namespace cells never receive a verdict", file=sys.stderr)
        return 2
    res = verdict(raw["cells"])
    txt = json.dumps(res, indent=1, sort_keys=True)
    if a.out:
        with open(a.out, "x") as fh:
            fh.write(txt)
    print(json.dumps({"verdict": res["verdict"], "reason": res["reason"], "clauses": res["clauses"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
