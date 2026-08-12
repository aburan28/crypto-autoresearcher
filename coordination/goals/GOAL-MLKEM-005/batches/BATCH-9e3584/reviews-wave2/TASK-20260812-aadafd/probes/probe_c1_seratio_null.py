#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RED TEAM PROBE B  --  TASK-20260809-444fe7 / BATCH-9e3584 / GOAL-MLKEM-005

THE NULL-OBJECT CONTROL ON SECTION C1's ONLY LIVE STATISTIC.

WHAT THIS IS AND IS NOT.  A RED TEAM PROBE.  NOT pre-registered.  NOT a
rescoring of Section C1, of BATCH-cbe023, or of BATCH-a44d08 (which is not
rescored in any respect).  It changes no verdict and asserts no label.
CLAIM TIER: TOY.

THE ATTACK.  TASK-20260809-97d6cf reports, under AM-14(e):

    "FOUR of ten targets have SE_2way/SE_naive < 1 ... A ratio below 1 is IN
     TENSION WITH AM-7 clause (1), which expects the two-way construction to be
     the more conservative one."

Its three other results are declared-in-advance non-events: 0 FALSIFYING at
both floors, all ten verdicts invariant to the repair (prereg 4.5 said it could
not be otherwise), and P-C1a falsified by arithmetic available before the run.
So AM-14(e) carries that section's entire live content -- and it is reported
WITHOUT the control that `docs/inventor-protocol.md` section 3 requires:

    WHAT SHOULD THE REPORTED QUANTITY HAVE DONE?  If SE_2way/SE_naive < 1 is a
    finding about the instrument, then a table with NO support effect and NO
    pool effect -- a null object of the identical 8 x 4 shape -- should NOT
    produce ratios below 1 at a comparable rate.

This probe runs the IDENTICAL se_decomposition() on null tables of the
identical shape and reports the null distribution of the ratio, P(ratio < 1),
and where each of the ten committed ratios falls in it.

WHAT COULD NOT FAIL, IN BOTH DIRECTIONS -- named BEFORE the run:
  * could-not-FIRE (the null can never look like the real tables): if the null
    were drawn with a different S, E, or a different decomposition, any
    difference would be a pipeline difference.  AVERTED: S = 8, E = 4 and
    se_decomposition() are carried VERBATIM from the producer's own
    posctl_c2.py, degenerate branch included.
  * could-not-PASS (the null can never differ from the real tables, so the
    probe can only ever say "controlled null"): if the ratio were an algebraic
    constant the probe would be vacuous.  AVERTED: the ratio's null
    distribution is REPORTED with its spread and its lower tail, so a committed
    ratio outside that tail is detectable.  The probe has a live outcome in
    which the committed ratios ARE anomalous -- and the extreme target is
    scored against the null tail separately from the count.

Two null models, both of the same shape, so the reading does not depend on one:
  N1  iid standard normal 8 x 4                (no support effect, no pool effect)
  N2  PERMUTATION null: the committed table's own 32 entries, shuffled, which
      destroys the support x pool structure while KEEPING the marginal
      distribution of that target's own entries exactly.

WRITES exactly one file: probe_c1_seratio_null.json, beside this script.
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

T0 = time.time()

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "..",
                                          "..", "..", ".."))
COMMITTED_AM7 = os.path.join(
    REPO_ROOT, "coordination", "goals", "GOAL-MLKEM-005", "batches",
    "BATCH-cbe023", "tasks", "TASK-20260808-3a5f18", "results_am7.json")

S, E = 8, 4
N_NULL = 200000
SEED = 20260812


# ---- CARRIED VERBATIM from TASK-20260809-3eb72c/posctl_c2.py ---------------
def se_decomposition(Delta):
    S_, E_ = Delta.shape
    gm = float(Delta.mean())
    row = Delta.mean(axis=1)
    col = Delta.mean(axis=0)
    MS_S = float(E_ * ((row - gm) ** 2).sum() / (S_ - 1))
    MS_P = float(S_ * ((col - gm) ** 2).sum() / (E_ - 1))
    resid = Delta - row[:, None] - col[None, :] + gm
    MS_res = float((resid ** 2).sum() / ((S_ - 1) * (E_ - 1)))
    num = MS_S + MS_P - MS_res
    negflag = bool(num <= 0.0)
    if negflag:
        var = MS_res / (S_ * E_)
        nu = float((S_ - 1) * (E_ - 1))
    else:
        var = num / (S_ * E_)
        den = (MS_S ** 2 / (S_ - 1) + MS_P ** 2 / (E_ - 1)
               + MS_res ** 2 / ((S_ - 1) * (E_ - 1)))
        nu = float(num ** 2 / den) if den > 0 else float((S_ - 1) * (E_ - 1))
    nu = max(1.0, nu)
    return {"var_Delta_bar": float(var), "SE_Delta_bar": float(np.sqrt(var)),
            "nu_eff": nu, "NEGATIVE_VARIANCE_COMPONENT": negflag,
            "Delta_bar": gm}
# ---------------------------------------------------------------------------


def se_naive(D):
    """prereg 4.3: sd(flattened, ddof=1)/sqrt(S*E)."""
    return float(np.std(np.asarray(D, dtype=float).ravel(), ddof=1)
                 / np.sqrt(S * E))


def ratio_of(D):
    D = np.asarray(D, dtype=float)
    dec = se_decomposition(D)
    sn = se_naive(D)
    return (dec["SE_Delta_bar"] / sn if sn > 0 else None), dec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--n-null", type=int, default=N_NULL)
    args = ap.parse_args()

    R = OrderedDict()
    R["probe_id"] = "PROBE-B / probe_c1_seratio_null"
    R["task_id"] = "TASK-20260809-444fe7"
    R["role"] = "red-team"
    R["batch_id"] = "BATCH-9e3584"
    R["goal_id"] = "GOAL-MLKEM-005"
    R["claim_tier"] = "toy"
    R["status_of_this_artifact"] = (
        "RED TEAM PROBE. NOT pre-registered. NOT a rescoring of Section C1 or "
        "of any committed verdict. BATCH-a44d08 is not rescored in any "
        "respect. No label is asserted or negated.")
    R["certificate"] = {"kind": "none", "reason": "no discrete-log solve and "
                        "no factor-base relation is claimed or produced"}
    R["environment"] = {"python": sys.version.split()[0],
                        "numpy": np.__version__,
                        "platform": platform.platform()}
    R["could_not_fail_named_before_the_run"] = {
        "could_not_FIRE": "a null of a different shape or a different "
                          "decomposition would make any difference a pipeline "
                          "difference. AVERTED: S=8, E=4 and "
                          "se_decomposition() carried VERBATIM from the "
                          "producer's posctl_c2.py.",
        "could_not_PASS": "if the ratio were an algebraic constant the probe "
                          "could only ever return 'controlled null'. AVERTED: "
                          "the full null distribution and its lower tail are "
                          "reported, and each committed ratio is placed in it."}

    src = json.load(open(COMMITTED_AM7))
    R["source"] = {"path": ("coordination/goals/GOAL-MLKEM-005/batches/"
                            "BATCH-cbe023/tasks/TASK-20260808-3a5f18/"
                            "results_am7.json"),
                   "status": "COMMITTED INPUT, READ ONLY"}

    rng = np.random.default_rng(SEED)

    # ---- N1: iid standard normal, no support effect, no pool effect
    n = args.n_null
    ratios = np.empty(n, dtype=float)
    negs = 0
    for j in range(n):
        D = rng.standard_normal((S, E))
        r, dec = ratio_of(D)
        ratios[j] = r
        negs += int(dec["NEGATIVE_VARIANCE_COMPONENT"])
    R["null_N1_iid_normal"] = {
        "n_draws": n, "seed": SEED,
        "model": "iid N(0,1) 8x4: NO support effect, NO pool effect",
        "P_ratio_below_1": float(np.mean(ratios < 1.0)),
        "mean": float(ratios.mean()), "sd": float(ratios.std(ddof=1)),
        "quantiles": {q: float(np.quantile(ratios, v)) for q, v in
                      [("p001", 0.001), ("p01", 0.01), ("p05", 0.05),
                       ("p10", 0.10), ("p25", 0.25), ("p50", 0.50),
                       ("p75", 0.75), ("p95", 0.95), ("p99", 0.99)]},
        "fraction_NEGATIVE_VARIANCE_COMPONENT": negs / n,
        "expected_count_below_1_in_10_targets": 10.0 * float(np.mean(ratios < 1.0))}

    # ---- the ten committed targets, recomputed here
    rows = []
    for t in src["targets"]:
        D = np.asarray(t["Delta_table_S_by_E"], dtype=float)
        r, dec = ratio_of(D)
        # N2: permutation null on THIS target's own 32 entries
        flat = D.ravel().copy()
        pr = np.empty(2000, dtype=float)
        for j in range(pr.size):
            rng.shuffle(flat)
            pr[j], _ = ratio_of(flat.reshape(S, E))
        rows.append(OrderedDict([
            ("cell", t["cell"]), ("target", t["target"]),
            ("SE_2way_over_SE_naive_recomputed", r),
            ("committed_SE_Delta_bar", float(t["scoring"]["SE_Delta_bar"])),
            ("recomputed_SE_Delta_bar", dec["SE_Delta_bar"]),
            ("SE_reproduction_relative_deviation",
             abs(dec["SE_Delta_bar"] - float(t["scoring"]["SE_Delta_bar"]))
             / max(abs(float(t["scoring"]["SE_Delta_bar"])), 1e-300)),
            ("NEGATIVE_VARIANCE_COMPONENT",
             dec["NEGATIVE_VARIANCE_COMPONENT"]),
            ("below_1", bool(r < 1.0)),
            ("percentile_in_N1_iid_null", float(np.mean(ratios <= r))),
            ("N2_permutation_null_P_below_1", float(np.mean(pr < 1.0))),
            ("N2_permutation_null_percentile_of_observed",
             float(np.mean(pr <= r))),
            ("N2_permutation_null_median", float(np.median(pr))),
        ]))
    R["targets"] = rows
    R["null_N2_permutation"] = {
        "n_shuffles_per_target": 2000,
        "model": "the target's own 32 entries shuffled: destroys the "
                 "support x pool structure, keeps the marginal exactly"}

    below = [x for x in rows if x["below_1"]]
    R["headline"] = OrderedDict([
        ("committed_count_below_1", len(below)),
        ("committed_targets_below_1",
         ["%s/%s" % (x["cell"], x["target"]) for x in below]),
        ("N1_expected_count_below_1_out_of_10",
         R["null_N1_iid_normal"]["expected_count_below_1_in_10_targets"]),
        ("N1_P_ratio_below_1", R["null_N1_iid_normal"]["P_ratio_below_1"]),
        ("reading", "The COUNT below 1 is compared with what an effect-free "
                    "table of the same shape produces. The EXTREME value is "
                    "scored separately against the null's lower tail, because "
                    "a count and a tail are different questions.")])

    R["what_this_probe_does_NOT_establish"] = [
        "It does NOT rescore Section C1 and does NOT move any verdict. All ten "
        "committed FALSIFYING verdicts are and remain False at both floors.",
        "It does NOT show the producer's arithmetic is wrong: the SE "
        "reproduction deviation is reported per target and is the check.",
        "A ratio inside the null distribution is NOT evidence that the "
        "instrument is sound; it is evidence that the ratio does not "
        "discriminate. Absence of a signal in a null control is not a result "
        "about AM-7 clause (1) in either direction.",
        "CLAIM TIER TOY.",
    ]
    R["wall_clock_seconds"] = round(time.time() - T0, 3)

    with open(args.out, "w") as fh:
        json.dump(R, fh, indent=2)
        fh.write("\n")

    h = R["headline"]
    print("PROBE B -- null-object control on SE_2way/SE_naive")
    print("  committed: %d of 10 targets below 1  %s"
          % (h["committed_count_below_1"], h["committed_targets_below_1"]))
    print("  N1 iid-normal null: P(ratio<1) = %.4f  -> expected %.2f of 10"
          % (h["N1_P_ratio_below_1"], h["N1_expected_count_below_1_out_of_10"]))
    print("  N1 null quantiles:",
          json.dumps(R["null_N1_iid_normal"]["quantiles"]))
    for x in rows:
        print("   %-9s %-16s ratio %.4f  N1 pct %.4f  N2 pct %.4f  neg=%s"
              % (x["cell"], x["target"], x["SE_2way_over_SE_naive_recomputed"],
                 x["percentile_in_N1_iid_null"],
                 x["N2_permutation_null_percentile_of_observed"],
                 x["NEGATIVE_VARIANCE_COMPONENT"]))
    print("  wall clock %.2f s" % R["wall_clock_seconds"])


if __name__ == "__main__":
    main()
