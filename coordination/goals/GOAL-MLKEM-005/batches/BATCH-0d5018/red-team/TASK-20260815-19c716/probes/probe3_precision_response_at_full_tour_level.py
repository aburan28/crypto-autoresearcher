#!/usr/bin/env python3
"""RT probe 3 (TASK-20260815-19c716). The reversal: read the SAME recorded
numbers as a precision-response curve at the FULL-TOUR level, which is the
level at which this goal has never plotted one.

Pure arithmetic on committed producer JSON from two batches. Runs no fpylll.

Derived quantity: POST-OUTER-LLL RESIDUAL WALL CLOCK
    residual = subprocess_wall_clock_seconds - outer_lll_reduction_elapsed_seconds
It is the same derived quantity in every row, so rows are comparable to each
other. It is an UPPER BOUND on BKZ-tour time (it also contains interpreter
startup, imports, basis generation, GSO.Mat construction and update_gso()),
never an equality, and it is labelled as such in every row.

Provenance of every input field is emitted alongside the value. Where a field
was not recorded (the (d=512,beta=70) worker was SIGTERM-killed before writing
its JSON, so it has no outer_lll_reduction_elapsed_seconds), the substitute and
its assumption are named explicitly and the row is marked estimated=True.
"""
import json
import re
import subprocess
import sys

REPO = "/Volumes/SSD990/crypto-autoresearcher"
PRIOR = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-279acb/tasks/"
         "TASK-20260815-6e4c02/main_grid_d512_reattempt_results.json")
THIS = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-0d5018/tasks/"
        "TASK-20260815-f14d3c/main_grid_d512_beta5570_reattempt_results.json")
B55 = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-0d5018/tasks/"
       "TASK-20260815-f14d3c/bisection_d512_beta55_results.json")
B70 = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-0d5018/tasks/"
       "TASK-20260815-f14d3c/bisection_d512_beta70_results.json")


def load(p):
    return json.load(open("%s/%s" % (REPO, p)))


def deepest_frame(cell):
    tb = cell.get("traceback", "")
    frames = re.findall(r'File "([^"]+)", line (\d+), in (\w+)', tb)
    if not frames:
        return None
    entry = [f for f in frames if f[0].endswith("bkz.py") or f[0].endswith("bkz2.py")]
    return {
        "n_frames": len(frames),
        "first_fpylll_algorithms_frame": (
            "%s:%s in %s" % (entry[0][0].split("/")[-1], entry[0][1], entry[0][2])
            if entry else None),
        "deepest_fpylll_algorithms_frame": (
            "%s:%s in %s" % (entry[-1][0].split("/")[-1], entry[-1][1], entry[-1][2])
            if entry else None),
        "entered_a_tour": any(f[2] == "tour" for f in frames),
        "entered_svp_preprocessing": any(f[2] == "svp_preprocessing" for f in frames),
    }


rows = []
prior = load(PRIOR)
this = load(THIS)
b70_outer_mean = sum(t["outer_lll_reduction_elapsed_seconds"]
                     for t in load(B70)["trials"]) / 7.0

for cell in prior["main_grid"]:
    rows.append({
        "batch": "BATCH-279acb", "d": cell["d"], "beta": cell["beta"],
        "mpfr_bits": cell["mpfr_bits_used"],
        "precision_source": "beta=40-bisected 69 bits, BORROWED for beta=55/70",
        "status": cell["status"],
        "wall_clock_s": round(cell["subprocess_wall_clock_seconds"], 2),
        "outer_lll_s": round(cell["outer_lll_reduction_elapsed_seconds"], 2),
        "outer_lll_source": "recorded by the worker itself",
        "residual_post_outer_lll_s": round(
            cell["subprocess_wall_clock_seconds"]
            - cell["outer_lll_reduction_elapsed_seconds"], 2),
        "estimated": False,
        "failure_depth": deepest_frame(cell),
    })

for cell in this["main_grid"]:
    if "outer_lll_reduction_elapsed_seconds" in cell:
        outer = cell["outer_lll_reduction_elapsed_seconds"]
        src = "recorded by the worker itself"
        est = False
    else:
        outer = b70_outer_mean
        src = ("NOT RECORDED (worker SIGTERM-killed before writing JSON); "
               "substituted with the mean of the 7 outer-LLL timings this run "
               "measured on the SAME basis during its own bisection "
               "(%.2fs). ASSUMPTION: outer LLL cost is the same in the "
               "reattempt subprocess as in the bisection subprocess." % b70_outer_mean)
        est = True
    rows.append({
        "batch": "BATCH-0d5018", "d": cell["d"], "beta": cell["beta"],
        "mpfr_bits": cell["mpfr_bits_used"],
        "precision_source": "OWN-basis bisected minimum",
        "status": cell["status"],
        "wall_clock_s": round(cell["subprocess_wall_clock_seconds"], 2),
        "outer_lll_s": round(outer, 2),
        "outer_lll_source": src,
        "residual_post_outer_lll_s": round(
            cell["subprocess_wall_clock_seconds"] - outer, 2),
        "estimated": est,
        "failure_depth": deepest_frame(cell),
        "note": ("residual is a LOWER bound here: the cell was killed at the "
                 "cap, it did not fail at this time"
                 if cell["status"] == "NOT_COMPUTED" else None),
    })

# same-cell, same-seed, precision-only comparisons
def find(batch, beta):
    return [r for r in rows if r["batch"] == batch and r["beta"] == beta][0]


comparisons = []
for beta in (55, 70):
    a = find("BATCH-279acb", beta)
    b = find("BATCH-0d5018", beta)
    comparisons.append({
        "cell": "d=512, beta=%d" % beta,
        "same_seed": True,
        "same_construction": True,
        "precision_change_bits": "%d -> %d" % (a["mpfr_bits"], b["mpfr_bits"]),
        "residual_s_before": a["residual_post_outer_lll_s"],
        "residual_s_after": b["residual_post_outer_lll_s"],
        "residual_ratio": round(
            b["residual_post_outer_lll_s"] / a["residual_post_outer_lll_s"], 1),
        "ratio_is_lower_bound": b["status"] == "NOT_COMPUTED",
        "ratio_uses_estimated_outer_lll": b["estimated"],
        "failure_depth_before": a["failure_depth"]["deepest_fpylll_algorithms_frame"],
        "failure_depth_after": (b["failure_depth"] or {}).get(
            "deepest_fpylll_algorithms_frame"),
        "entered_a_tour_before": a["failure_depth"]["entered_a_tour"],
        "entered_a_tour_after": (b["failure_depth"] or {}).get("entered_a_tour"),
    })

out = {
    "probe": "probe3_precision_response_at_full_tour_level",
    "this_session_ran_no_fpylll": True,
    "derived_quantity": "post-outer-LLL residual wall clock = "
                        "subprocess_wall_clock_seconds - outer_lll_reduction_elapsed_seconds; "
                        "an UPPER bound on BKZ-tour time, identical in construction across rows",
    "rows": rows,
    "same_cell_precision_only_comparisons": comparisons,
    "n_distinct_full_tour_precision_points_ever_measured_per_cell": {
        "d=512,beta=40": ["69 bits (BATCH-279acb, ERROR)"],
        "d=512,beta=55": ["69 bits (BATCH-279acb, ERROR)", "75 bits (BATCH-0d5018, ERROR)"],
        "d=512,beta=70": ["69 bits (BATCH-279acb, ERROR)",
                          "73 bits (BATCH-0d5018, NOT_COMPUTED at cap)"],
    },
    "untested_at_full_tour_level_anywhere_in_this_goal":
        "any precision strictly above each cell's own isolated-step minimum "
        "(e.g. 100 bits, already measured ADEQUATE at the isolated step at "
        "every one of the three d=512 bases, and inside the SAME 2-limb "
        "64-bit mpfr regime as 73/75 bits per the producer's own "
        "budget_justification, which places the limb boundary at 129+ bits)",
}
json.dump(out, sys.stdout, indent=2)
print()
