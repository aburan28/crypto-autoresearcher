#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RED TEAM PROBE C  --  TASK-20260809-444fe7 / BATCH-9e3584 / GOAL-MLKEM-005

THE CENTERED POSITIVE CONTROL THAT SECTION C2 PRE-REGISTERED FOR A SUCCESSOR
AND DELIBERATELY DID NOT RUN.

WHAT THIS IS AND IS NOT.  A RED TEAM PROBE.  NOT pre-registered.  NOT a
rescoring of Section C2 and NOT a re-verdict of P-C2c, which stands FALSIFIED
in the producer's own record and is not reinstated here.  BATCH-a44d08 is not
rescored in any respect.  CLAIM TIER: TOY.

THE ATTACK, AND THE PRODUCER'S OWN CONDUCT.  TASK-20260809-3eb72c recorded
P-C2c as FALSIFIED -- one target fired at delta/SE = 1.0 -- and then REFUSED
the consequence its own pre-registration declared ("the instrument is
over-sensitive"), diagnosing instead that the target's committed |Delta_bar|
was already 4.5295 SE, 88.5% of its own |t|crit, so a CONSTANT ADDITIVE
injection cannot separate instrument sensitivity from a pre-existing
near-critical effect.  It pre-registered the repair -- a CENTERED variant --
for a successor and did not run it, on the stated ground that adding an
unregistered analysis to rescue a falsified prediction is the failure mode the
batch exists to close.

That refusal is correct conduct AND it leaves the diagnosis UNTESTED.  Testing
someone else's deferred repair is the Red Team's job, not the producer's, so
this probe runs it: subtract each target's own Delta_bar from its committed
raw 8 x 4 table so that Delta_bar = 0 EXACTLY, then run the identical ladder
through the identical full_score() path.

WHAT COULD NOT FAIL, IN BOTH DIRECTIONS -- named BEFORE the run, and one of
them IS partially met, which is stated rather than hidden:
  * could-not-FIRE: after centering, |t| = delta/SE exactly (a constant offset
    leaves every variance component unchanged), so at rung r the t-clause fires
    iff r > |t|crit, and min |t|crit over the ten targets is 2.78 > 1.0.  THE
    BOTTOM TWO RUNGS THEREFORE CANNOT FIRE ON THE t-CLAUSE BY ARITHMETIC.  This
    probe IS in that arrangement on the t-clause and says so: its value is (a)
    verifying that the IMPLEMENTED path actually behaves that way, which is the
    same thing AM-14(b) asked of C2 itself, and (b) the relative-difference
    clause, which is NOT forced -- rel = delta/M after centering and can land
    either side of tau_rel.
  * could-not-PASS: if centering also changed SE, the comparison would be
    between two different instruments.  AVERTED: the recovered SE at every rung
    is compared against the committed SE and the deviation is reported.

WRITES exactly one file: probe_c2_centered.json, beside this script.
NO git write, NO commit.
"""

import argparse
import json
import os
import platform
import sys
import time
from collections import OrderedDict

import numpy as np
from scipy.stats import t as student_t

T0 = time.time()

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "..",
                                          "..", "..", ".."))
COMMITTED_AM7 = os.path.join(
    REPO_ROOT, "coordination", "goals", "GOAL-MLKEM-005", "batches",
    "BATCH-cbe023", "tasks", "TASK-20260808-3a5f18", "results_am7.json")

ALPHA_PAIR = 0.10 / 11          # carried
TAU_REL_FROZEN = 0.15           # carried
TAU_REL_REBUILT = 0.025         # Section C1, prereg 4.1
LADDER = [0, 0.5, 1.0, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0]   # carried, prereg 5.2


# ---- CARRIED VERBATIM from TASK-20260809-3eb72c/posctl_c2.py ---------------
def se_decomposition(Delta):
    S, E = Delta.shape
    gm = float(Delta.mean())
    row = Delta.mean(axis=1)
    col = Delta.mean(axis=0)
    MS_S = float(E * ((row - gm) ** 2).sum() / (S - 1))
    MS_P = float(S * ((col - gm) ** 2).sum() / (E - 1))
    resid = Delta - row[:, None] - col[None, :] + gm
    MS_res = float((resid ** 2).sum() / ((S - 1) * (E - 1)))
    num = MS_S + MS_P - MS_res
    negflag = bool(num <= 0.0)
    if negflag:
        var = MS_res / (S * E)
        nu = float((S - 1) * (E - 1))
    else:
        var = num / (S * E)
        den = (MS_S ** 2 / (S - 1) + MS_P ** 2 / (E - 1)
               + MS_res ** 2 / ((S - 1) * (E - 1)))
        nu = float(num ** 2 / den) if den > 0 else float((S - 1) * (E - 1))
    nu = max(1.0, nu)
    return {"var_Delta_bar": float(var), "SE_Delta_bar": float(np.sqrt(var)),
            "nu_eff": nu, "NEGATIVE_VARIANCE_COMPONENT": negflag,
            "Delta_bar": gm}


def full_score(Delta, M, tau_rel):
    dec = se_decomposition(np.asarray(Delta, dtype=float))
    dbar, se, nu = dec["Delta_bar"], dec["SE_Delta_bar"], dec["nu_eff"]
    tcrit = float(student_t.ppf(1.0 - ALPHA_PAIR / 2.0, nu))
    at = (abs(dbar) / se) if se > 0 else None
    rel = (abs(dbar) / M) if M > 0 else None
    return {"Delta_bar": dbar, "SE_Delta_bar": se, "nu_eff": nu,
            "t_crit": tcrit, "abs_t": at, "relative_difference": rel,
            "condition_i_t": bool(at is not None and at > tcrit),
            "condition_ii_relative": bool(rel is not None and rel > tau_rel),
            "FALSIFYING_PAIR": bool(at is not None and at > tcrit
                                    and rel is not None and rel > tau_rel),
            "NEGATIVE_VARIANCE_COMPONENT": dec["NEGATIVE_VARIANCE_COMPONENT"]}
# ---------------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    R = OrderedDict()
    R["probe_id"] = "PROBE-C / probe_c2_centered"
    R["task_id"] = "TASK-20260809-444fe7"
    R["role"] = "red-team"
    R["batch_id"] = "BATCH-9e3584"
    R["goal_id"] = "GOAL-MLKEM-005"
    R["claim_tier"] = "toy"
    R["status_of_this_artifact"] = (
        "RED TEAM PROBE. NOT pre-registered. NOT a rescoring of Section C2. "
        "P-C2c stands FALSIFIED in the producer's record and is not "
        "reinstated. BATCH-a44d08 is not rescored in any respect.")
    R["certificate"] = {"kind": "none", "reason": "no discrete-log solve and "
                        "no factor-base relation is claimed or produced"}
    R["environment"] = {"python": sys.version.split()[0],
                        "numpy": np.__version__,
                        "platform": platform.platform()}
    R["could_not_fail_named_before_the_run"] = {
        "could_not_FIRE": "PARTIALLY MET AND DISCLOSED. After centering, "
                          "|t| = delta/SE exactly, so the t-clause cannot fire "
                          "at rungs 0.5 and 1.0 given min |t|crit = 2.78. The "
                          "probe's live content is (a) whether the IMPLEMENTED "
                          "path behaves that way and (b) the relative-"
                          "difference clause, which is not forced.",
        "could_not_PASS": "if centering changed SE the comparison would be "
                          "between two instruments. AVERTED: recovered SE vs "
                          "committed SE is reported at every rung."}

    src = json.load(open(COMMITTED_AM7))
    R["source"] = {"path": ("coordination/goals/GOAL-MLKEM-005/batches/"
                            "BATCH-cbe023/tasks/TASK-20260808-3a5f18/"
                            "results_am7.json"),
                   "status": "COMMITTED INPUT, READ ONLY"}

    rows = []
    max_se_dev = 0.0
    fired_le1_uncentered = []
    fired_le1_centered = []
    for t in src["targets"]:
        D0 = np.asarray(t["Delta_table_S_by_E"], dtype=float)
        M = max(abs(t["D_GR_mean"]), abs(t["D_TL_mean"]))
        se_c = float(t["scoring"]["SE_Delta_bar"])
        base = full_score(D0, M, TAU_REL_FROZEN)
        Dc = D0 - D0.mean()                      # THE CENTERING
        ladder = []
        for r in LADDER:
            dabs = r * se_c
            unc = full_score(D0 + dabs, M, TAU_REL_FROZEN)
            cen = full_score(Dc + dabs, M, TAU_REL_FROZEN)
            cen25 = full_score(Dc + dabs, M, TAU_REL_REBUILT)
            dev = abs(cen["SE_Delta_bar"] - se_c) / max(abs(se_c), 1e-300)
            max_se_dev = max(max_se_dev, dev)
            ladder.append(OrderedDict([
                ("delta_over_SE", r),
                ("UNCENTERED_abs_t", unc["abs_t"]),
                ("UNCENTERED_FALSIFYING_0.15", unc["FALSIFYING_PAIR"]),
                ("CENTERED_abs_t", cen["abs_t"]),
                ("CENTERED_relative_difference", cen["relative_difference"]),
                ("CENTERED_condition_i_t", cen["condition_i_t"]),
                ("CENTERED_condition_ii_relative_0.15",
                 cen["condition_ii_relative"]),
                ("CENTERED_FALSIFYING_0.15", cen["FALSIFYING_PAIR"]),
                ("CENTERED_FALSIFYING_0.025", cen25["FALSIFYING_PAIR"]),
                ("CENTERED_SE_recovery_relative_deviation", dev),
            ]))
            if r <= 1.0 and r > 0:
                if unc["FALSIFYING_PAIR"]:
                    fired_le1_uncentered.append(
                        "%s/%s @%s" % (t["cell"], t["target"], r))
                if cen["FALSIFYING_PAIR"]:
                    fired_le1_centered.append(
                        "%s/%s @%s" % (t["cell"], t["target"], r))
        rows.append(OrderedDict([
            ("cell", t["cell"]), ("target", t["target"]),
            ("committed_Delta_bar", base["Delta_bar"]),
            ("committed_SE", se_c), ("committed_abs_t", base["abs_t"]),
            ("committed_t_crit", base["t_crit"]),
            ("committed_abs_t_over_t_crit",
             base["abs_t"] / base["t_crit"] if base["abs_t"] else None),
            ("centered_Delta_bar_at_rung_0", float(Dc.mean())),
            ("ladder", ladder),
        ]))
    R["targets"] = rows
    R["headline"] = OrderedDict([
        ("targets_firing_at_delta_over_SE_le_1_UNCENTERED",
         fired_le1_uncentered),
        ("targets_firing_at_delta_over_SE_le_1_CENTERED", fired_le1_centered),
        ("max_CENTERED_SE_recovery_relative_deviation", max_se_dev),
        ("targets_firing_at_12SE_CENTERED_with_tcrit_below_8",
         [("%s/%s" % (x["cell"], x["target"]))
          for x in rows if x["committed_t_crit"] < 8.0
          and x["ladder"][-1]["CENTERED_FALSIFYING_0.15"]]),
        ("targets_with_tcrit_below_8",
         [("%s/%s" % (x["cell"], x["target"]))
          for x in rows if x["committed_t_crit"] < 8.0]),
        ("reading", "If the CENTERED bottom rungs do not fire while the "
                    "UNCENTERED one did, the producer's diagnosis of P-C2c is "
                    "corroborated BY MEASUREMENT and the 'over-sensitive' "
                    "reading its own pre-registration declared is NOT "
                    "supported. That finding runs AGAINST the Red Team's "
                    "adversarial prior and is reported at equal weight."),
    ])
    R["what_this_probe_does_NOT_establish"] = [
        "It does NOT reinstate P-C2c and does NOT overturn its FALSIFIED "
        "status; the producer's record stands.",
        "The t-clause outcome at rungs 0.5 and 1.0 is FORCED BY ARITHMETIC "
        "after centering and is reported as an IMPLEMENTATION check, never as "
        "a test that could have failed mathematically.",
        "It says nothing about tail sufficiency in either direction and "
        "neither reinstates nor negates the frozen Section C label.",
        "CLAIM TIER TOY.",
    ]
    R["wall_clock_seconds"] = round(time.time() - T0, 3)

    with open(args.out, "w") as fh:
        json.dump(R, fh, indent=2)
        fh.write("\n")

    h = R["headline"]
    print("PROBE C -- the CENTERED positive control C2 deferred")
    print("  fired at delta/SE <= 1, UNCENTERED :",
          h["targets_firing_at_delta_over_SE_le_1_UNCENTERED"])
    print("  fired at delta/SE <= 1, CENTERED   :",
          h["targets_firing_at_delta_over_SE_le_1_CENTERED"])
    print("  max centered SE recovery deviation : %.3e" % max_se_dev)
    print("  |t|crit < 8 targets                :",
          len(h["targets_with_tcrit_below_8"]))
    print("  of those, CENTERED FALSIFYING @12SE:",
          len(h["targets_firing_at_12SE_CENTERED_with_tcrit_below_8"]))
    print("  wall clock %.2f s" % R["wall_clock_seconds"])


if __name__ == "__main__":
    main()
