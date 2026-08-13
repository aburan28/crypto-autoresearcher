#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RED TEAM PROBE E  --  TASK-20260809-444fe7 / BATCH-9e3584 / GOAL-MLKEM-005

AM-11's DISPERSION REQUIREMENT AND AM-10's REPLICATION REQUIREMENT, APPLIED TO
SECTION B's OWN NEWLY PROPOSED STATISTIC: n_fire ON THE NULL FAMILY.

WHAT THIS IS AND IS NOT.  A RED TEAM PROBE.  NOT pre-registered.  NOT a
rescoring of Section B' and NOT a re-verdict of its decay check.  It does not
retire AM-3, which stays undemonstrated rather than disproved.  BATCH-a44d08 is
not rescored in any respect.  CLAIM TIER: TOY.

THE ATTACK.  TASK-20260809-311784 reports, as its headline:

  "On the rebuilt null family, n_fire(c = 6) is 35 of 48, against the committed
   real count of 29 of 48 and the Red Team's exact-null benchmark of 47 of 48."

and reads a FAIL of the pre-registered decay check from  35 >= 29.  The
pre-registered decision boundary is "materially below = a difference of at
least 8 of 48".  The realized difference is  real - null = -6.

n_fire is a NEWLY PROPOSED STATISTIC computed on a RANDOM OBJECT -- 13
independently drawn Haar frame stacks -- and it is reported from ONE
realization with NO dispersion attached.  AM-11 requires dispersion for every
statistic and AM-10 requires replication; the producer applied both to Section
R's G-REL and to neither here.  If the between-replicate sd of n_fire is
comparable to the 8-of-48 decision boundary, then the boundary and the realized
margin are the same size, and a single realization cannot locate the count
relative to either.

WHAT THIS PROBE VARIES, AND WHAT IT HOLDS FIXED.
  VARIED:   the 13-frame family's seeds, via a disjoint offset
            seed = seed_nullfam(d,beta,j,m) + 10_000_000*(rep+1).
  HELD FIXED, exactly as the producer had them: the CBD error sample
            (seed_error(d)), the carried Haar null arm (seed_haar) that sets
            SE_diff, q_Beta, N_ERR, CHUNK, N_DRAW, t_crit, GATE_K and the
            c grid.
  CONSEQUENCE, DISCLOSED: the dispersion measured here is over FRAME DRAWS
            ONLY.  It is a LOWER BOUND on the total sampling dispersion of
            n_fire, because the error sample and the Haar arm are frozen across
            replicates.  A wider replication would only widen it.

WHAT COULD NOT FAIL, IN BOTH DIRECTIONS -- named BEFORE the run:
  * could-not-FIRE (this probe can never show meaningful dispersion): if every
    replicate reused the producer's seeds it would reproduce 35 exactly and the
    sd would be 0 by construction.  AVERTED: the offset is disjoint and
    strictly positive, and replicate 0's seed set is asserted DIFFERENT from
    the producer's in the output.
  * could-not-PASS (this probe can never show the count is stable): if the
    statistic were an integer with a huge range, any spread would look large.
    AVERTED: n_fire is bounded in [0, 48], its detection floor is 1 step =
    2.083 percentage points (the producer's own figure), and the sd is reported
    against BOTH the 8-of-48 decision boundary and the realized -6 margin, so a
    small sd is a finding FOR the producer and is reported as such.

BUDGET.  --time-budget caps the wall clock; the probe reports HOW MANY
replicates completed and never pads.  An exhausted budget is reported as an
exhausted budget, never as a result.

WRITES exactly one file: probe_nfire_dispersion.json, beside this script.
NO git write, NO commit.
"""

import argparse
import importlib.util
import json
import os
import platform
import sys
import time
from collections import OrderedDict

import numpy as np
from scipy.special import betaincinv

T0 = time.time()

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "..",
                                          "..", "..", ".."))
PRODUCER = os.path.join(
    REPO_ROOT, "coordination", "goals", "GOAL-MLKEM-005", "batches",
    "BATCH-9e3584", "tasks", "TASK-20260809-311784", "measure_nullfam.py")

SEED_OFFSET_STEP = 10_000_000
COMMITTED_REAL_N_FIRE_C6 = 29        # quoted with its benchmark, below
RED_TEAM_EXACT_NULL_N_FIRE_C6 = 47   # the benchmark, same sentence, carry 4
PRODUCER_REALIZED_N_FIRE_C6 = 35
MATERIALLY_BELOW = 8


def load_producer_module():
    spec = importlib.util.spec_from_file_location("mnf", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--replicates", type=int, default=8)
    ap.add_argument("--time-budget", type=float, default=2400.0)
    args = ap.parse_args()

    M = load_producer_module()

    R = OrderedDict()
    R["probe_id"] = "PROBE-E / probe_nfire_dispersion"
    R["task_id"] = "TASK-20260809-444fe7"
    R["role"] = "red-team"
    R["batch_id"] = "BATCH-9e3584"
    R["goal_id"] = "GOAL-MLKEM-005"
    R["claim_tier"] = "toy"
    R["status_of_this_artifact"] = (
        "RED TEAM PROBE. NOT pre-registered. NOT a rescoring of Section B'. "
        "AM-3 IS NOT RETIRED. BATCH-a44d08 is not rescored in any respect.")
    R["certificate"] = {"kind": "none", "reason": "no discrete-log solve and "
                        "no factor-base relation is claimed or produced"}
    R["environment"] = {"python": sys.version.split()[0],
                        "numpy": np.__version__,
                        "platform": platform.platform(),
                        "note": "PURE NUMPY. NO BKZ. NO LLL. NO reduction of "
                                "any kind, exactly as the producer."}
    R["carried_verbatim_from_producer"] = {
        "module": ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/"
                   "tasks/TASK-20260809-311784/measure_nullfam.py"),
        "functions": ["make_errors", "haar_frames", "project", "arm_r_values",
                      "se_of_difference", "score_cell", "seed_nullfam",
                      "seed_error", "seed_haar"],
        "constants": {"CELLS": M.CELLS, "N_ERR": M.N_ERR, "CHUNK": M.CHUNK,
                      "N_DRAW": M.N_DRAW, "GATE_K": M.GATE_K,
                      "AM3_T_CRIT": M.AM3_T_CRIT, "C_GRID": M.C_GRID,
                      "GRADED_T": M.GRADED_T, "P_TAIL_10": M.P_TAIL_10}}
    R["what_is_varied_and_what_is_held_fixed"] = {
        "varied": "the 13-frame family seeds, offset by 10_000_000*(rep+1)",
        "held_fixed": ["CBD error sample seed_error(d)",
                       "the carried Haar null arm seed_haar(d,beta,j), which "
                       "sets SE_diff",
                       "q_Beta, N_ERR, CHUNK, N_DRAW, t_crit, GATE_K, c grid"],
        "DISCLOSED_CONSEQUENCE": "the dispersion measured here is over FRAME "
                                 "DRAWS ONLY and is a LOWER BOUND on the total "
                                 "sampling dispersion of n_fire."}
    R["could_not_fail_named_before_the_run"] = {
        "could_not_FIRE": "reusing the producer's seeds would reproduce 35 "
                          "with sd 0 by construction. AVERTED: strictly "
                          "positive disjoint offset, asserted below.",
        "could_not_PASS": "an unbounded statistic would make any spread look "
                          "large. AVERTED: n_fire is bounded in [0,48] with a "
                          "1-step detection floor, and a SMALL sd is reported "
                          "as a finding FOR the producer."}

    # guard: replicate seeds are disjoint from the producer's
    base = M.seed_nullfam(100, 30, 0, 0)
    R["guard_seed_disjointness"] = {
        "producer_seed_example_d100_b30_j0_m0": int(base),
        "replicate_offsets": [SEED_OFFSET_STEP * (r + 1)
                              for r in range(args.replicates)],
        "max_producer_seed_upper_bound":
            int(M.seed_nullfam(140, 40, M.N_DRAW - 1, len(M.GRADED_T) - 1)),
        "offsets_strictly_exceed_producer_seed_range":
            bool(SEED_OFFSET_STEP >
                 M.seed_nullfam(140, 40, M.N_DRAW - 1, len(M.GRADED_T) - 1))}

    err_cache = {}
    haar_cache = {}
    qb_cache = {}
    reps = []
    budget_exhausted = False

    for rep in range(args.replicates):
        if time.time() - T0 > args.time_budget:
            budget_exhausted = True
            break
        t_rep = time.time()
        off = SEED_OFFSET_STEP * (rep + 1)
        cells_out = OrderedDict()
        for (d, beta) in M.CELLS:
            key = "d%d_b%d" % (d, beta)
            if d not in err_cache:
                err_cache[d] = M.make_errors(d)
            Ef, n2, _ = err_cache[d]
            if key not in qb_cache:
                qb_cache[key] = float(betaincinv(beta / 2.0, (d - beta) / 2.0,
                                                 M.P_TAIL_10))
            qb10 = qb_cache[key]
            if key not in haar_cache:
                Qh = M.haar_frames(d, beta)
                haar_cache[key] = M.arm_r_values(
                    M.project(Ef, n2, Qh, beta), qb10)
            haar = haar_cache[key]
            means, values, se_diff = [], [], []
            for m, _t in enumerate(M.GRADED_T):
                cols = []
                for j in range(M.N_DRAW):
                    g = np.random.default_rng(
                        M.seed_nullfam(d, beta, j, m) + off)
                    cols.append(np.linalg.qr(
                        g.standard_normal((d, beta)))[0].astype(np.float32))
                Qm = np.concatenate(cols, axis=1)
                a = M.arm_r_values(M.project(Ef, n2, Qm, beta), qb10)
                means.append(a["mean"])
                values.append(a["values"])
                se_diff.append(M.se_of_difference(a["sd"], haar["sd"]))
            sc = M.score_cell(M.GRADED_T, means, values, se_diff)
            cells_out[key] = {
                "n_fire": sc["n_fire"],
                "n_degenerate": sc["n_degenerate"],
                "c_min_median": sc["c_min_median"],
                "se_step_over_se_diff_median":
                    sc["se_step_over_se_diff_median"],
                "mean_delta": sc["mean_delta"],
                "n_fire_definitions_agree": sc["n_fire_definitions_agree"]}
        tot = {str(c): sum(cells_out[k]["n_fire"][str(c)] for k in cells_out)
               for c in M.C_GRID}
        reps.append(OrderedDict([
            ("replicate", rep), ("seed_offset", off),
            ("n_fire_by_c", tot),
            ("n_fire_c6", tot["6"]),
            ("n_fire_c6_per_cell",
             [cells_out[k]["n_fire"]["6"] for k in cells_out]),
            ("n_degenerate_total",
             sum(cells_out[k]["n_degenerate"] for k in cells_out)),
            ("se_step_over_se_diff_median_per_cell",
             [cells_out[k]["se_step_over_se_diff_median"] for k in cells_out]),
            ("c_min_median_per_cell",
             [cells_out[k]["c_min_median"] for k in cells_out]),
            ("seconds", round(time.time() - t_rep, 2)),
        ]))
        print("  replicate %d  n_fire(c=6) = %2d of 48   (%.1f s)"
              % (rep, tot["6"], reps[-1]["seconds"]), flush=True)

    R["replicates"] = reps
    R["budget"] = {"time_budget_seconds": args.time_budget,
                   "replicates_requested": args.replicates,
                   "replicates_completed": len(reps),
                   "budget_exhausted": budget_exhausted,
                   "note": "an exhausted budget is reported as an exhausted "
                           "budget and never as a result"}

    if reps:
        v = np.array([r["n_fire_c6"] for r in reps], dtype=float)
        allc = {str(c): [r["n_fire_by_c"][str(c)] for r in reps]
                for c in M.C_GRID}
        R["headline"] = OrderedDict([
            ("producer_single_realization_n_fire_c6",
             PRODUCER_REALIZED_N_FIRE_C6),
            ("replicate_n_fire_c6_values", [int(x) for x in v]),
            ("mean", float(v.mean())),
            ("sd_ddof1", float(v.std(ddof=1)) if v.size > 1 else None),
            ("min", int(v.min())), ("max", int(v.max())),
            ("range", int(v.max() - v.min())),
            ("n_replicates", int(v.size)),
            ("committed_real_count_with_its_benchmark",
             "the committed real count of %d of 48 and the Red Team's "
             "exact-null benchmark of %d of 48"
             % (COMMITTED_REAL_N_FIRE_C6, RED_TEAM_EXACT_NULL_N_FIRE_C6)),
            ("replicates_at_or_above_the_committed_real_count",
             int((v >= COMMITTED_REAL_N_FIRE_C6).sum())),
            ("replicates_materially_below_it_by_the_frozen_8_of_48",
             int((v <= COMMITTED_REAL_N_FIRE_C6 - MATERIALLY_BELOW).sum())),
            ("sd_against_the_frozen_decision_boundary_of_8",
             (float(v.std(ddof=1)) / MATERIALLY_BELOW) if v.size > 1 else None),
            ("n_fire_by_c_across_replicates", allc),
        ])
    R["what_this_probe_does_NOT_establish"] = [
        "It does NOT overturn Section B's decay-check verdict; the direction "
        "of that verdict is reported here with its own replicate evidence and "
        "the Coordinator adjudicates it, not this probe.",
        "It does NOT retire AM-3. AM-3's power remains UNDEMONSTRATED RATHER "
        "THAN DISPROVED and its 0.096 family-wise false-failure bound stands.",
        "It measures dispersion over FRAME DRAWS ONLY; the error sample and "
        "the Haar arm are frozen, so this is a LOWER BOUND.",
        "No reduction of any kind was run, so nothing here bears on any "
        "reduced basis, block size, or lattice-reduction cost.",
        "CLAIM TIER TOY.",
    ]
    R["wall_clock_seconds"] = round(time.time() - T0, 2)

    with open(args.out, "w") as fh:
        json.dump(R, fh, indent=2)
        fh.write("\n")

    print("PROBE E -- AM-11 dispersion of n_fire(c=6) on the null family")
    if reps:
        h = R["headline"]
        print("  replicates completed: %d  (budget exhausted: %s)"
              % (len(reps), budget_exhausted))
        print("  n_fire(c=6) values:", h["replicate_n_fire_c6_values"])
        print("  mean %.2f  sd %.2f  range %d  [min %d, max %d]"
              % (h["mean"], h["sd_ddof1"] or float("nan"), h["range"],
                 h["min"], h["max"]))
        print("  producer's single realization: %d"
              % PRODUCER_REALIZED_N_FIRE_C6)
        print("  replicates >= committed real count (29): %d of %d"
              % (h["replicates_at_or_above_the_committed_real_count"],
                 len(reps)))
        print("  sd / frozen 8-of-48 boundary: %s"
              % h["sd_against_the_frozen_decision_boundary_of_8"])
    else:
        print("  NO REPLICATE COMPLETED WITHIN THE TIME BUDGET. "
              "This is INFRASTRUCTURE SIGNAL, not a result.")
    print("  wall clock %.1f s" % R["wall_clock_seconds"])


if __name__ == "__main__":
    main()
