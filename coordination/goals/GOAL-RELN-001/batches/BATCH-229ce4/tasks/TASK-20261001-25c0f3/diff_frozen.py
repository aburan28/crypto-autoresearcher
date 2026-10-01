"""Diff the frozen analysis.py output against recompute_out.json, per cell and aggregate."""
import json, sys
D = sys.argv[1]
fr = json.load(open(f"{D}/frozen_analysis_out.json"))
me = json.load(open(f"{D}/recompute_out.json"))["verdict"]
def eq(a, b):
    if isinstance(a, float) or isinstance(b, float):
        return a is not None and b is not None and abs(a - b) < 1e-12
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(eq(x, y) for x, y in zip(a, b))
    return a == b
diffs = []
pairs = [("verdict", fr["verdict"], me["verdict"]),
         ("supercritical_rule", fr["clauses"]["supercritical_rule"], me["supercritical_rule"]),
         ("subcritical_rule", fr["clauses"]["subcritical_rule"], me["subcritical_rule"]),
         ("ci_all", fr["clauses"]["ci_gt_quarter_all_cells"], me["ci_gt_quarter_all"]),
         ("trend_both", fr["clauses"]["trend_flat_or_rising_both_budgets"], me["trend_ok_both"]),
         ("er_exceeds_any", fr["clauses"]["er_null_exceeds_quarter_in_any_cell"], me["er_exceeds_any"]),
         ("er_undetermined", fr["clauses"]["er_null_undetermined_cells"], me["er_undetermined_cells"])]
for bu in ("A1", "A2"):
    pairs += [(f"trend.{bu}.slope", fr["trend"][bu]["slope_per_bit"], me["trend"][bu]["slope"]),
              (f"trend.{bu}.upper", fr["trend"][bu]["slope_upper_95_ci"], me["trend"][bu]["upper"]),
              (f"trend.{bu}.ok", fr["trend"][bu]["flat_or_rising"], me["trend"][bu]["ok"])]
n = 0
for k, fc in fr["per_cell"].items():
    mc = me["per_cell"][k]
    pairs += [(f"{k}.delta_proof", fc["delta_proof"], mc["delta_proof"]),
              (f"{k}.lower_95_ci", fc["lower_95_ci"], mc["lower_95_ci"]),
              (f"{k}.ci_gt_quarter", fc["ci_gt_quarter"], mc["ci_gt_quarter"]),
              (f"{k}.er_mean", fc["er_mean_delta_proof"], mc["er_mean_delta_proof"]),
              (f"{k}.er_exceeds", fc["er_exceeds_quarter"], mc["er_exceeds_quarter"]),
              (f"{k}.er_feasible", fc["er_feasible_replicates"], mc["er_feasible"]),
              (f"{k}.kp_power", fc["known_positive_power_confirmed"], mc["kp_power_confirmed"])]
    rows = sorted(fc["rows"], key=lambda r: r["seed"])
    for i, r in enumerate(rows):
        for fk, mk in (("V", "V"), ("E", "E"), ("cycle_rank", "cycle_rank"),
                       ("components_with_cycle", "components_with_cycle"),
                       ("giant_component_fraction", "giant_fraction")):
            pairs.append((f"{k}.{r['fixture_id']}.{fk}", r[fk], mc[mk][i]))
for name, a, b in pairs:
    n += 1
    if not eq(a, b):
        diffs.append((name, a, b))
print(json.dumps({"compared": n, "differences": diffs,
                  "frozen_known_positive": fr["known_positive"]["cells_lacking_power_confirmation"]}, indent=1))
