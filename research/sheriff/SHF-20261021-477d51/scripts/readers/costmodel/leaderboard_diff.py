#!/usr/bin/env python3
"""Reader costmodel (SHF-20261021-477d51): compare docs/ic/leaderboard.json before
(b4f056101^1) and after (b4f056101): which top-level keys changed, and whether the
new planner_component rows equal the frozen analysis/summary.json values.
argv: before.json after.json summary.json specs_dir"""
import json, sys, pathlib, math


def close(x, y):
    """Equal up to the builder's 12-significant-figure rounding."""
    if isinstance(x, dict) and isinstance(y, dict):
        return x.keys() == y.keys() and all(close(x[k], y[k]) for k in x)
    if isinstance(x, list) and isinstance(y, list):
        return len(x) == len(y) and all(close(a, b) for a, b in zip(x, y))
    if isinstance(x, (int, float)) and isinstance(y, (int, float)):
        return math.isclose(x, y, rel_tol=1e-10, abs_tol=1e-12)
    return x == y
before = json.load(open(sys.argv[1])); after = json.load(open(sys.argv[2]))
summary = json.load(open(sys.argv[3])); specs = pathlib.Path(sys.argv[4])
changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
print("top-level keys changed:", changed)
for k in ("board", "leaders", "families", "exponents"):
    print(f"  {k} identical: {before.get(k) == after.get(k)}")
src_changed = {k: (before["sources"].get(k), after["sources"].get(k)) for k in set(before["sources"]) | set(after["sources"]) if before["sources"].get(k) != after["sources"].get(k)}
print("sources changed:", list(src_changed))
pc = after["planner_component"]
print("planner_component class:", pc.get("class"))
by = {r["curve_tag"]: r for r in summary}
bad = 0
for row in pc["rows"]:
    s = by[row["tag"]]
    spec = json.load(open(specs / f"{row['tag']}.json"))
    plan = next(a for a in spec["arms"] if a["name"] == "plan")["method"]["params"]
    alts = {a["arm"]: a for a in s["alternatives"]}
    ok = (row["plan"] == plan and close(row["plan_over_rho"], s["plan_over_rho"])
          and close(row["predicted_plan_over_rho"], s["predicted_plan_over_rho"])
          and all(close(a, {k: alts[a["arm"]][k] for k in ("arm", "ops_ratio", "ci95", "band_ratio", "verdict")}) for a in row["alternatives"]))
    bad += not ok
    print(f"  {row['tag']}: equals summary.json/spec (to 1e-10 rel): {ok}; plan/rho {s['plan_over_rho']['ratio']:.4f} ci {[round(x,4) for x in s['plan_over_rho']['ci95']]}; predicted {s['predicted_plan_over_rho']:.4f}; verdicts {[(a['arm'], a['verdict']) for a in row['alternatives']]}")
print("rows not matching:", bad)
