#!/usr/bin/env python3
"""V5 -- TIMING INTEGRITY.

Attack plan from review-plan.yaml, joint V5:
  (1) recorded_at gaps and the wall_s vs cpu_s check across all 504 rows.
  (2) P3c and P4 medians recomputed EXCLUDING rows with loadavg1_at_start > 2;
      per-cell change in percent; whether any P3c (>=10x) or P4 (no >10%
      speedup) verdict flips.
  (3) Any row with wall_s > timeout_s + 1.

Reads results.jsonl only. No solver, no compiler. Metric definitions taken
from the contract / hypothesis wording, not from summary.py.
"""
import json
import pathlib
import statistics
from datetime import datetime

RUN = pathlib.Path("/workspace/experiments/EXP-ICPERF-66fd51/runs/RUN-ICPERF-305ca3")
HERE = pathlib.Path(__file__).resolve().parent

ROWS = [json.loads(l) for l in open(RUN / "results.jsonl")]
SOLVE = [r for r in ROWS if "status" in r]
FINISHED = {"SAT", "UNSAT"}


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


# ---------------------------------------------------------------- (1) gaps
order = sorted(ROWS, key=lambda r: ts(r["recorded_at"]))
gaps = []
for a, b in zip(order, order[1:]):
    d = ts(b["recorded_at"]) - ts(a["recorded_at"])
    # A gap is "explained" when the row that closes it ran for that long: rows
    # are stamped at completion, so a 900 s Singular timeout produces a 900 s
    # gap with nothing idle in it. What matters is the UNEXPLAINED remainder.
    unexplained = d - (b.get("wall_s") or 0.0)
    if unexplained > 300.0:
        gaps.append(
            {
                "gap_s": round(d, 1),
                "unexplained_idle_s": round(unexplained, 1),
                "after_row": {
                    "instance": a.get("instance"),
                    "engine": a.get("engine"),
                    "config": a.get("config"),
                    "phase": a.get("phase"),
                    "recorded_at": a["recorded_at"],
                    "wall_s": a.get("wall_s"),
                },
                "before_row": {
                    "instance": b.get("instance"),
                    "engine": b.get("engine"),
                    "config": b.get("config"),
                    "phase": b.get("phase"),
                    "recorded_at": b["recorded_at"],
                    "wall_s": b.get("wall_s"),
                    "timeout_s": b.get("timeout_s"),
                },
            }
        )

# Rows are stamped at completion, so the idle time sits BETWEEN two rows: the
# row closing a gap started at recorded_at - wall_s, which is after the idle
# period ended. A row could only have absorbed a suspension by having wall_s
# inflated far past its own cpu_s; that is the test below, not an interval
# overlap. Recorded here so the reasoning is auditable rather than assumed.
span = []
for g in gaps:
    b = g["before_row"]
    span.append(
        {
            "gap_s": g["gap_s"],
            "unexplained_idle_s": g["unexplained_idle_s"],
            "row_closing_the_gap": b,
            "row_wall_s": b.get("wall_s"),
            "row_started_s_after_idle_ended": round(
                g["unexplained_idle_s"], 1
            ),
            "row_absorbs_the_idle_time": False,
        }
    )

# ------------------------------------------------- (1b) wall_s vs cpu_s
wall_cpu = []
for r in SOLVE:
    w, c = r.get("wall_s"), r.get("cpu_s")
    if w is None or c is None:
        wall_cpu.append({"instance": r.get("instance"), "engine": r.get("engine"),
                         "config": r.get("config"), "wall_s": w, "cpu_s": c,
                         "note": "missing"})
        continue
    wall_cpu.append(
        {
            "instance": r.get("instance"),
            "engine": r.get("engine"),
            "config": r.get("config"),
            "status": r.get("status"),
            "wall_s": w,
            "cpu_s": c,
            "wall_minus_cpu_s": round(w - c, 4),
            "wall_over_cpu": round(w / c, 4) if c > 0 else None,
            "loadavg1_at_start": r.get("loadavg1_at_start"),
        }
    )

excess = sorted(
    [x for x in wall_cpu if x.get("wall_minus_cpu_s") is not None],
    key=lambda x: -x["wall_minus_cpu_s"],
)

# ------------------------------------------------- (3) timeout overshoot
overshoot = []
for r in SOLVE:
    w, t = r.get("wall_s"), r.get("timeout_s")
    if w is not None and t is not None and w > t + 1.0:
        overshoot.append(
            {
                "instance": r.get("instance"),
                "engine": r.get("engine"),
                "config": r.get("config"),
                "status": r.get("status"),
                "wall_s": w,
                "timeout_s": t,
                "over_by_s": round(w - t, 4),
                "timed_out": r.get("timed_out"),
            }
        )

# --------------------------------- (2) exclusion sensitivity for P3c and P4
def cell_median_wall(engine, config, cell, label, exclude_high_load):
    xs = []
    n = 0
    for r in SOLVE:
        if r.get("engine") != engine or r.get("config") != config:
            continue
        if r.get("cell") != cell or r.get("label") != label:
            continue
        if r.get("status") not in FINISHED:
            continue
        if exclude_high_load and (r.get("loadavg1_at_start") or 0.0) > 2.0:
            continue
        xs.append(r["wall_s"])
        n += 1
    return med(xs), n


def phase_d_instance_set(cell, label):
    """P3c compares CMS pure-CNF against WDSat default. The pure-CNF phase ran
    on a subset; the matched comparison is over that subset."""
    return {
        r["instance"]
        for r in SOLVE
        if r.get("engine") == "cryptominisat5"
        and r.get("config") == "pure_cnf"
        and r.get("cell") == cell
        and r.get("label") == label
    }


def matched_median_wall(engine, config, cell, label, insts, exclude_high_load):
    xs = []
    for r in SOLVE:
        if r.get("engine") != engine or r.get("config") != config:
            continue
        if r.get("cell") != cell or r.get("label") != label:
            continue
        if r.get("instance") not in insts:
            continue
        if r.get("status") not in FINISHED:
            continue
        if exclude_high_load and (r.get("loadavg1_at_start") or 0.0) > 2.0:
            continue
        xs.append(r["wall_s"])
    return med(xs), len(xs)


cells = sorted({(r["cell"], r["label"]) for r in SOLVE if r.get("label") in ("S", "U")})

p3c = []
for cell, label in cells:
    if not cell.endswith("l6"):
        continue  # P3c is worded at l = 6
    insts = phase_d_instance_set(cell, label)
    row = {"cell": cell, "label": label, "n_phase_D_instances": len(insts)}
    for tag, excl in (("all", False), ("lowload", True)):
        cms_all, n_cms = cell_median_wall("cryptominisat5", "pure_cnf", cell, label, excl)
        wd_all, n_wd = cell_median_wall("wdsat", "default", cell, label, excl)
        wd_m, n_wdm = matched_median_wall("wdsat", "default", cell, label, insts, excl)
        row[tag] = {
            "cms_pure_cnf_median_wall_s": cms_all,
            "n_cms": n_cms,
            "wdsat_default_median_wall_s_all_10": wd_all,
            "n_wdsat_all": n_wd,
            "wdsat_default_median_wall_s_matched": wd_m,
            "n_wdsat_matched": n_wdm,
            "ratio_vs_all_10": (cms_all / wd_all) if (cms_all and wd_all) else None,
            "ratio_vs_matched": (cms_all / wd_m) if (cms_all and wd_m) else None,
        }
    for key in ("ratio_vs_all_10", "ratio_vs_matched"):
        a, b = row["all"][key], row["lowload"][key]
        row[f"{key}_pct_change"] = (
            round(100.0 * (b - a) / a, 2) if (a and b) else None
        )
        row[f"{key}_holds_all"] = (a is not None and a >= 10.0)
        row[f"{key}_holds_lowload"] = (b is not None and b >= 10.0)
        row[f"{key}_verdict_flips"] = (
            row[f"{key}_holds_all"] != row[f"{key}_holds_lowload"]
        )
    p3c.append(row)

p4 = []
for cell, label in cells:
    row = {"cell": cell, "label": label}
    for tag, excl in (("all", False), ("lowload", True)):
        d, nd = cell_median_wall("wdsat", "default", cell, label, excl)
        g, ng = cell_median_wall("wdsat", "gauss_elim", cell, label, excl)
        row[tag] = {
            "default_median_wall_s": d,
            "n_default": nd,
            "gauss_median_wall_s": g,
            "n_gauss": ng,
            "gauss_over_default": (g / d) if (d and g) else None,
            "above_0.05s_floor": (d is not None and d > 0.05),
            # P4 fails if -x REDUCES median wall by more than 10%
            "reduces_by_more_than_10pct": (
                d is not None and g is not None and g < 0.9 * d
            ),
        }
    a, b = row["all"]["gauss_over_default"], row["lowload"]["gauss_over_default"]
    row["gauss_over_default_pct_change"] = (
        round(100.0 * (b - a) / a, 2) if (a and b) else None
    )
    row["verdict_flips"] = (
        row["all"]["reduces_by_more_than_10pct"]
        != row["lowload"]["reduces_by_more_than_10pct"]
    )
    p4.append(row)

# how many rows are excluded by the load filter, and where
load_counts = {}
for r in SOLVE:
    la = r.get("loadavg1_at_start")
    ph = r.get("phase")
    key = ph
    d = load_counts.setdefault(key, {"n": 0, "n_high": 0, "max_loadavg": 0.0})
    d["n"] += 1
    if la is not None:
        d["max_loadavg"] = max(d["max_loadavg"], la)
        if la > 2.0:
            d["n_high"] += 1

# wall vs cpu split by engine. The sign matters: wall > cpu is time the row
# lost (to contention, to a suspension); cpu > wall is a row using more than
# one core. Pooling the two hides both.
by_engine = {}
for r in SOLVE:
    w, c = r.get("wall_s"), r.get("cpu_s")
    if w is None or c is None:
        continue
    e = r["engine"]
    d = by_engine.setdefault(
        e, {"n": 0, "min_wall_minus_cpu": None, "max_wall_minus_cpu": None,
            "min_cpu_over_wall": None, "max_cpu_over_wall": None}
    )
    d["n"] += 1
    diff = w - c
    d["min_wall_minus_cpu"] = diff if d["min_wall_minus_cpu"] is None else min(d["min_wall_minus_cpu"], diff)
    d["max_wall_minus_cpu"] = diff if d["max_wall_minus_cpu"] is None else max(d["max_wall_minus_cpu"], diff)
    if w > 0.001:
        rat = c / w
        d["min_cpu_over_wall"] = rat if d["min_cpu_over_wall"] is None else min(d["min_cpu_over_wall"], rat)
        d["max_cpu_over_wall"] = rat if d["max_cpu_over_wall"] is None else max(d["max_cpu_over_wall"], rat)
for d in by_engine.values():
    for k in list(d):
        if k != "n" and d[k] is not None:
            d[k] = round(d[k], 4)

out = {
    "wall_vs_cpu_by_engine": by_engine,
    "n_rows_total": len(ROWS),
    "n_solve_rows": len(SOLVE),
    "n_certificate_rows": len(ROWS) - len(SOLVE),
    "gaps_over_300s": gaps,
    "rows_spanning_a_gap": span,
    "wall_vs_cpu": {
        "n_rows_with_both": len([x for x in wall_cpu if x.get("wall_minus_cpu_s") is not None]),
        "max_wall_minus_cpu_s": excess[0] if excess else None,
        "top_10_by_wall_minus_cpu": excess[:10],
        "n_wall_minus_cpu_over_2s": len([x for x in excess if x["wall_minus_cpu_s"] > 2.0]),
        "n_wall_minus_cpu_over_5s": len([x for x in excess if x["wall_minus_cpu_s"] > 5.0]),
        "n_wall_over_cpu_ratio_over_1_5": len(
            [x for x in excess if (x.get("wall_over_cpu") or 0) > 1.5 and x["wall_s"] > 1.0]
        ),
    },
    "timeout_overshoot_over_1s": overshoot,
    "loadavg_by_phase": load_counts,
    "n_high_load_solve_rows": sum(d["n_high"] for d in load_counts.values()),
    "P3c_exclusion_sensitivity": p3c,
    "P4_exclusion_sensitivity": p4,
}
json.dump(out, open(HERE / "v5_timing.json", "w"), indent=1, sort_keys=True, default=str)
print(json.dumps({k: v for k, v in out.items() if k not in ("P3c_exclusion_sensitivity", "P4_exclusion_sensitivity")}, indent=1, default=str)[:6000])
