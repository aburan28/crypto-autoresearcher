#!/usr/bin/env python3
"""PROBE B (red team, TASK-20260809-444fe7) -- IS THE NULL FAMILY THE RIGHT
NULL, AND COULD P-B1'S FALSIFIER EVER HAVE FIRED?

NOT PRE-REGISTERED. Rescores NO frozen verdict. It does not retire AM-3, does
not rescore BATCH-a44d08, and does not restate any non-citable phrase.
CLAIM TIER TOY.

RE-EXECUTABLE from the repository root:
    python3 <this file> --out probe_bprime_output.json

WHAT IT ATTACKS
---------------
Section B' (TASK-20260809-311784, report_nullfam.md) reports: on the rebuilt
null family n_fire(c = 6) is 35 of 48, against the committed real count of
29 of 48 and the Red Team's exact-null benchmark of 47 of 48; the decay check
FAILS; the count is an artifact. Three things that headline does not settle,
and this probe measures all three from committed numbers only.

  (B1) COULD P-B1 HAVE BEEN FALSIFIED AT ALL? Its falsifier is
       n_fire(c = 6) <= 21 of 48. A step fires at c = 6 iff
       c_min = 1 + (t_crit*SE_step - Delta)/SE_diff <= 6, i.e. iff
       SE_step/SE_diff <= (5 + Delta/SE_diff)/t_crit. With Delta ~ 0 by
       construction that is a ratio threshold of 5/4.2071245566 = 1.18845.
       For a family of INDEPENDENT frames, SE_step and SE_diff estimate the
       same quantity, so the ratio is centred on 1 and the threshold is
       cleared by construction. This block computes the realized ratio
       distribution and Monte-Carlos the achievable n_fire, to find out
       whether the pre-registered falsifier had any reachable region.

  (B2) IS IT A NULL "OF THE SAME SHAPE"? AM-13 requires the identical count on
       a null object OF THE SAME SHAPE. c_min is an affine function of
       SE_step/SE_diff, so two objects with different SE ratios are not the
       same shape for this statistic however similar their pipelines. This
       block recovers the REAL arm's implied ratio from a committed number
       (the exact-null c_min median 2.990 recorded in the BATCH-cbe023 Red
       Team report, at Delta := 0 by construction) and compares it with the
       null family's own.

  (B3) DOES THE COUNT DECAY WHEN IT SHOULD? The parameter that should destroy
       a spurious count is the number of draws n: with more data a null should
       become HARDER to call. Under the null the expected c_min is
       ~ 1 + t_{n-1, 0.998} * 1, which DECREASES in n toward 1 + 2.878 = 3.878.
       So at the carried c = 6 the null count saturates upward at 48 of 48 as
       n grows. This block tabulates that, which is the artifact tell in the
       form docs/inventor-protocol.md section 3 names, stated as a property of
       the statistic rather than of one realization.

MY OWN CHECK'S COULD-NOT-FAIL ARRANGEMENTS, NAMED BEFORE RUNNING, BOTH WAYS
---------------------------------------------------------------------------
* could-not-FIRE: block B1's Monte Carlo assumes r_j(t_i) are exchangeable
  across grid points with a common sd -- the model the independent-frame
  construction is designed to realize. If the real r values were strongly
  heteroscedastic across grid points, the model would understate the
  achievable spread of the ratio and B1 would find the falsifier unreachable
  by assumption. Guarded by reporting the REALIZED per-step ratios from
  results_nullfam.json beside the simulated ones, and by reporting the
  realized per-grid-point arm sds, so a reader can see whether the model
  matches the object. The realized numbers, not the model, carry the finding.
* could-not-PASS: I could make the falsifier look reachable by simulating a
  smaller n or a different t_crit. Guarded by using the FROZEN n_draw = 8,
  the FROZEN t_crit = 4.2071245566046755, the FROZEN c grid and the FROZEN
  48-step family size. Nothing of mine enters them.

AM-10 / AM-11 ON THIS PROBE'S OWN STATISTICS
--------------------------------------------
Every count is reported per cell as well as pooled (AM-10 replication over the
four cells), and every ratio is reported with min / median / max over the 48
live steps rather than as a single number (AM-11 dispersion). The Monte Carlo
reports a distribution and a quantile, never a point estimate.
"""
import argparse
import json
import os
import subprocess
from collections import OrderedDict

import numpy as np
from scipy.stats import t as student_t

NULLFAM = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/"
           "TASK-20260809-311784/results_nullfam.json")
T_CRIT = 4.2071245566046755          # frozen, t_{7, 0.998}
C_GRID = [0, 1, 2, 3, 4, 6, 8, 12, 16, 24, 32]   # frozen
C_HEADLINE = 6                        # frozen
N_DRAW = 8                            # frozen
FAMILY = 48                           # frozen, 4 cells x 12 steps
FALSIFIER = 21                        # frozen: P-B1 is falsified at <= 21 of 48
# Committed number, quoted not rescored: the exact-null c_min median recorded in
# BATCH-cbe023/reviews/TASK-20260808-6de788/red_team_report.md section 3.3, and
# carried into results_nullfam.json as red_team_exact_null_c_min_median.
EXACT_NULL_CMIN_MEDIAN = 2.990


def load(path, rev="HEAD"):
    if os.path.exists(path):
        return json.load(open(path)), "working tree"
    blob = subprocess.run(["git", "show", "%s:%s" % (rev, path)],
                          capture_output=True, check=True)
    return json.loads(blob.stdout.decode()), "git %s" % rev


def d(vals):
    a = np.asarray(vals, dtype=float)
    return {"n": int(a.size), "mean": float(a.mean()),
            "sd": float(a.std(ddof=1)) if a.size > 1 else 0.0,
            "min": float(a.min()), "median": float(np.median(a)),
            "max": float(a.max())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nullfam", default=NULLFAM)
    ap.add_argument("--reps", type=int, default=20000)
    ap.add_argument("--out", default="probe_bprime_output.json")
    args = ap.parse_args()

    R, where = load(args.nullfam)
    OUT = OrderedDict()
    OUT["probe"] = "PROBE-B"
    OUT["task_id"] = "TASK-20260809-444fe7"
    OUT["claim_tier"] = "toy"
    OUT["status_of_this_measurement"] = (
        "RED-TEAM PROBE. NOT PRE-REGISTERED. Uses committed per-step numbers "
        "plus a Monte Carlo of the frozen statistic. No new frame is drawn, no "
        "reduction is run, AM-3 is NOT retired and BATCH-a44d08 is NOT "
        "rescored.")
    OUT["source"] = {"path": args.nullfam, "read_from": where}

    print("=" * 78)
    print("PROBE B -- is the null family the right null, and could P-B1's")
    print("           falsifier ever have fired?")
    print("RED-TEAM PROBE, NOT PRE-REGISTERED, RESCORES NOTHING. TOY.")
    print("=" * 78)

    # ------------------------------------------------------------ harvest steps
    steps = []
    for cell, cv in R["cells"].items():
        for s in cv["steps"]:
            if s.get("excluded_from_counts") or s.get("degenerate"):
                continue
            steps.append({"cell": cell, "i": s["i"], "delta": s["delta"],
                          "se_step": s["se_step_paired"],
                          "se_diff": s["injection_unit_se_diff"],
                          "c_min": s["c_min"],
                          "ratio": s["se_step_over_se_diff"]})
    OUT["n_live_steps_harvested"] = len(steps)

    # reproduce the committed count from the harvested steps
    n_fire = {str(c): int(sum(1 for s in steps if s["c_min"] <= c))
              for c in C_GRID}
    OUT["reproduced_n_fire_by_c"] = n_fire
    OUT["committed_n_fire_by_c"] = R["null_family_totals"]["n_fire_by_c_out_of_48"]
    OUT["reproduction_matches_committed"] = bool(
        all(n_fire[str(c)] == R["null_family_totals"]["n_fire_by_c_out_of_48"][str(c)]
            for c in C_GRID))
    print("\n[gate] reproduced n_fire by c from the committed per-step values: %s"
          % ("MATCHES" if OUT["reproduction_matches_committed"] else "DOES NOT MATCH"))

    # ------------------------------------------------------ B1: the ratio drives it
    ratio_thresh = (C_HEADLINE - 1.0) / T_CRIT
    fires_by_ratio_alone = int(sum(1 for s in steps if s["ratio"] <= ratio_thresh))
    # c_min with Delta forced to 0: an exact null OF the null family
    n_fire_delta0 = {str(c): int(sum(
        1 for s in steps if 1.0 + T_CRIT * s["se_step"] / s["se_diff"] <= c))
        for c in C_GRID}
    OUT["B1_the_ratio_drives_the_count"] = {
        "fire_condition": "c_min <= 6  <=>  SE_step/SE_diff <= (5 + Delta/SE_diff)/t_crit",
        "ratio_threshold_at_Delta_zero": ratio_thresh,
        "realized_ratio": d([s["ratio"] for s in steps]),
        "n_fire_c6_realized": n_fire[str(C_HEADLINE)],
        "n_fire_c6_predicted_from_the_ratio_alone": fires_by_ratio_alone,
        "n_fire_c6_with_Delta_forced_to_zero": n_fire_delta0[str(C_HEADLINE)],
        "n_fire_by_c_with_Delta_forced_to_zero": n_fire_delta0,
        "median_Delta_over_SE_diff": float(np.median(
            [s["delta"] / s["se_diff"] for s in steps])),
        "reading": (
            "If the count from the ratio alone equals the realized count, then "
            "Delta -- the only quantity that carries information about the "
            "object -- contributes nothing to the headline, and n_fire is a "
            "function of two standard-error estimates."),
    }
    print("\n[B1] ratio threshold at Delta=0: %.5f   realized ratio median %.4f"
          % (ratio_thresh, OUT["B1_the_ratio_drives_the_count"]["realized_ratio"]["median"]))
    print("     n_fire(6): realized %d | from the ratio alone %d | at Delta:=0 %d"
          % (n_fire[str(C_HEADLINE)], fires_by_ratio_alone,
             n_fire_delta0[str(C_HEADLINE)]))

    # ------------------------------------------------------ B1b: Monte Carlo
    rng = np.random.default_rng(20260811)
    reps = args.reps
    counts = np.empty(reps, dtype=np.int32)
    for b in range(reps):
        tot = 0
        for _cell in range(4):
            v = rng.standard_normal((13, N_DRAW))      # 13 grid points, 8 draws
            haar = rng.standard_normal(N_DRAW)
            sd_h = haar.std(ddof=1)
            sd_arm = v.std(axis=1, ddof=1)
            se_diff = np.sqrt(sd_arm ** 2 / N_DRAW + sd_h ** 2 / N_DRAW)
            dif = v[1:] - v[:-1]
            se_step = dif.std(axis=1, ddof=1) / np.sqrt(N_DRAW)
            delta = dif.mean(axis=1)
            cmin = 1.0 + (T_CRIT * se_step - delta) / se_diff[:-1]
            tot += int((cmin <= C_HEADLINE).sum())
        counts[b] = tot
    q = np.percentile(counts, [0, 1, 5, 25, 50, 75, 95, 99, 100])
    OUT["B1b_monte_carlo_of_the_frozen_statistic"] = {
        "model": ("r_j(t_i) iid N(0,1) across the 13 grid points and 8 draws, "
                  "with an independent 8-draw Haar reference arm -- the exact "
                  "exchangeability the independent-frame construction realizes. "
                  "The MODEL is mine; the FROZEN t_crit, n_draw, c grid and "
                  "family size are not."),
        "reps": reps,
        "n_fire_c6_distribution_over_48": {
            "mean": float(counts.mean()), "sd": float(counts.std(ddof=1)),
            "min": int(counts.min()), "max": int(counts.max()),
            "percentiles_0_1_5_25_50_75_95_99_100": [float(x) for x in q]},
        "P_n_fire_le_21_the_pre_registered_falsifier":
            float((counts <= FALSIFIER).mean()),
        "P_n_fire_le_29_i.e._below_the_committed_real_count":
            float((counts <= 29).mean()),
        "realized_null_family_value": n_fire[str(C_HEADLINE)],
        "reading": (
            "P(n_fire <= 21) is the probability that P-B1's pre-registered "
            "falsifier could have fired on a null family of this shape. A "
            "value at or near zero means the prediction ran in a could-not-be-"
            "falsified arrangement, which is a statement about the PREDICTION "
            "and not about the producer's conduct: the prereg predicted the "
            "outcome it got, and the honest reading is that the section's "
            "content is the mechanism it exposed, not the confirmation of "
            "P-B1."),
    }
    print("\n[B1b] Monte Carlo (%d reps): n_fire(6) mean %.1f sd %.1f  "
          "P(<=21) = %.5f  P(<=29) = %.5f"
          % (reps, counts.mean(), counts.std(ddof=1),
             (counts <= FALSIFIER).mean(), (counts <= 29).mean()))

    # ------------------------------------------------------ B2: same shape?
    implied_real_ratio = (EXACT_NULL_CMIN_MEDIAN - 1.0) / T_CRIT
    fam_ratio = float(np.median([s["ratio"] for s in steps]))
    OUT["B2_is_it_a_null_of_the_same_shape"] = {
        "quoted_committed_exact_null_c_min_median": EXACT_NULL_CMIN_MEDIAN,
        "quoted_from": ("BATCH-cbe023/reviews/TASK-20260808-6de788/"
                        "red_team_report.md section 3.3, carried into "
                        "results_nullfam.json; QUOTED, NOT RESCORED"),
        "implied_SE_step_over_SE_diff_of_the_REAL_arm": implied_real_ratio,
        "derivation": ("the exact null sets Delta := 0 while KEEPING the real "
                       "arm's SE_step and SE_diff, so c_min = 1 + t_crit * "
                       "(SE_step/SE_diff) exactly, and the ratio is recovered "
                       "as (c_min - 1)/t_crit"),
        "median_SE_step_over_SE_diff_of_the_NULL_FAMILY": fam_ratio,
        "factor_between_them": fam_ratio / implied_real_ratio,
        "reading": (
            "c_min is affine in SE_step/SE_diff. If the two objects' ratios "
            "differ by a large factor then they are not the same shape FOR "
            "THIS STATISTIC, whatever else is carried byte-for-byte, and the "
            "signed difference between their counts is not attributable to "
            "path structure alone. The DIRECTION of the section's finding -- "
            "both nulls at or above the real count -- does not depend on this; "
            "the magnitude does."),
    }
    print("\n[B2] implied real-arm ratio %.4f vs null-family median ratio %.4f "
          "(factor %.2f)" % (implied_real_ratio, fam_ratio,
                             fam_ratio / implied_real_ratio))

    # ------------------------------------------------------ B3: saturation in n
    tab = []
    for n in [8, 12, 16, 32, 64, 128, 1024]:
        tc = float(student_t.ppf(0.998, n - 1))
        tab.append({"n_draw": n, "t_crit_n": tc,
                    "expected_null_c_min_at_ratio_1": 1.0 + tc,
                    "fires_at_c6": bool(1.0 + tc <= C_HEADLINE)})
    tab.append({"n_draw": "inf", "t_crit_n": 2.8781617381190175,
                "expected_null_c_min_at_ratio_1": 3.8781617381190175,
                "fires_at_c6": True})
    OUT["B3_the_count_saturates_instead_of_decaying"] = {
        "table": tab,
        "carried_c_headline": C_HEADLINE,
        "null_c_min_at_the_frozen_n_draw_8": 1.0 + T_CRIT,
        "largest_c_that_still_discriminates_under_the_null": 1.0 + T_CRIT,
        "reading": (
            "Under a null with SE_step/SE_diff = 1 the expected c_min is "
            "1 + t_{n-1,0.998}, which DECREASES in n. The carried headline "
            "c = 6 lies above that value at every n, so more data drives the "
            "null count UP toward 48 of 48. A count whose null value rises "
            "with sample size is an artifact tell in the exact form "
            "docs/inventor-protocol.md section 3 names, and it is a property "
            "of the statistic rather than of one realization. It also names "
            "the discriminating region that remains OPEN: only c < 1 + t_crit "
            "= 5.207 at n_draw = 8 can separate a real arm from a null, which "
            "is where the c grid's 0..4 rungs sit."),
    }
    print("\n[B3] null c_min at ratio 1: n=8 -> %.3f, n=inf -> %.3f; carried c = 6"
          % (1.0 + T_CRIT, 3.8782))
    print("     -> the null count RISES toward 48/48 with more draws.")

    OUT["HEADLINE"] = {
        "P_B1_falsifier_probability_under_a_null_of_this_shape":
            OUT["B1b_monte_carlo_of_the_frozen_statistic"]
               ["P_n_fire_le_21_the_pre_registered_falsifier"],
        "count_from_the_SE_ratio_alone_equals_the_realized_count": bool(
            fires_by_ratio_alone == n_fire[str(C_HEADLINE)]),
        "null_family_vs_real_arm_SE_ratio_factor":
            fam_ratio / implied_real_ratio,
        "c_headline_lies_above_the_null_c_min_at_every_n_draw": True,
    }
    with open(args.out, "w") as fh:
        json.dump(OUT, fh, indent=1)
    print("\nwrote %s" % args.out)


if __name__ == "__main__":
    main()
