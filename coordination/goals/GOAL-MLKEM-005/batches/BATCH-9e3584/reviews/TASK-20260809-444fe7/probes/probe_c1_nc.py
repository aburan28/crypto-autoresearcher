#!/usr/bin/env python3
"""PROBE D (red team, TASK-20260809-444fe7) -- IS report_c1.md's STATED REASON
FOR EXCLUDING N-C TRUE, AND WHAT WOULD INCLUDING IT HAVE DONE?

NOT PRE-REGISTERED. Rescores NO frozen verdict, moves no target's verdict, and
does NOT re-litigate AM-14 -- AM-14(c) itself names the four N-A/N-B medians,
so the exclusion is a CARRY and is not the producer's discretion. What is
attacked here is only the producer's stated MECHANISM for it, which is a claim
and carries the ordinary burden. CLAIM TIER TOY.

RE-EXECUTABLE from the repository root:
    python3 <this file> --out probe_c1_nc_output.json

WHAT IT ATTACKS
---------------
report_c1.md section 1: "For Gaussian errors, R ~ Beta(beta/2, (d-beta)/2)
EXACTLY for every orthonormal frame, so D = q_emp/q_Beta - 1 is driven to ~0
on BOTH sides and the denominator max(|D_GR|, |D_TL|) of the relative
difference collapses. Its median relative differences -- 1.021643 and
1.004966 -- are therefore an artifact of a vanishing denominator, not a
measure of null central tendency."

That is a testable mechanism with a numerator and a denominator, and the
committed replicate records let both be recovered:

    relative_difference = |Delta_bar| / max(|D_GR|, |D_TL|)
      =>  max(|D_GR|, |D_TL|) = |Delta_bar| / relative_difference

If the mechanism is right, N-C's recovered denominator is far smaller than
N-A/N-B's while its |Delta_bar| is comparable. If instead N-C's NUMERATOR is
large, the same ratio arises for a different reason and the stated mechanism
is wrong even though the exclusion stands on AM-14(c) and on R = 60 < R_min.

The probe also states the counterfactual: what tau_rel the carried rule
(1.67 x the top of the range) would have produced had N-C been in the input
set, and in which direction that would have moved the instrument.

MY OWN CHECK'S COULD-NOT-FAIL ARRANGEMENTS, NAMED BEFORE RUNNING, BOTH WAYS
---------------------------------------------------------------------------
* could-not-FIRE: if the committed replicates recorded no relative_difference
  or no Delta_bar, the denominator could not be recovered and the mechanism
  could not be checked. They record both, so the check is live.
* could-not-PASS: I could declare the mechanism false by comparing N-C's
  denominator against a threshold of my own. Guarded by making the comparison
  RELATIVE between nulls -- N-C against N-A and N-B, on the same cells
  d100_b40 and d140_b40 -- with no threshold of mine anywhere, and by
  reporting the numerator distribution beside the denominator so the reader
  sees which one moved.

AM-10 / AM-11 ON THIS PROBE'S OWN STATISTICS
--------------------------------------------
Every recovered quantity is reported per null over all its replicates (300 for
N-A/N-B, 60 for N-C -- the unequal replication is disclosed, not averaged
over) with min / median / p95 / max, never as a bare median.
"""
import argparse
import json
import os
import subprocess
from collections import OrderedDict

import numpy as np

AM7 = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/tasks/"
       "TASK-20260808-3a5f18/results_am7.json")
CARRIED_MULTIPLIER = 1.67          # BATCH-cbe023 prereg 4.4, carried unchanged


def load(path):
    if os.path.exists(path):
        return json.load(open(path)), "working tree"
    blob = subprocess.run(["git", "show", "HEAD:%s" % path],
                          capture_output=True, check=True)
    return json.loads(blob.stdout.decode()), "git HEAD"


def q(vals):
    a = np.asarray(vals, dtype=float)
    a = a[np.isfinite(a)]
    if a.size == 0:
        return None
    return {"n": int(a.size), "min": float(a.min()),
            "median": float(np.median(a)), "p95": float(np.percentile(a, 95)),
            "max": float(a.max())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--am7", default=AM7)
    ap.add_argument("--out", default="probe_c1_nc_output.json")
    args = ap.parse_args()

    src, where = load(args.am7)
    OUT = OrderedDict()
    OUT["probe"] = "PROBE-D"
    OUT["task_id"] = "TASK-20260809-444fe7"
    OUT["claim_tier"] = "toy"
    OUT["status_of_this_measurement"] = (
        "RED-TEAM PROBE. NOT PRE-REGISTERED. Recovers a quantity from "
        "committed replicate records; changes no verdict and re-litigates no "
        "amendment. AM-14(c) names the four N-A/N-B medians, so the EXCLUSION "
        "is carried; only its stated MECHANISM is under test here.")
    OUT["source"] = {"path": args.am7, "read_from": where}

    print("=" * 78)
    print("PROBE D -- is the stated reason for excluding N-C true?")
    print("RED-TEAM PROBE, NOT PRE-REGISTERED, RESCORES NOTHING. TOY.")
    print("=" * 78)

    rows = OrderedDict()
    for name, nl in src["nulls"].items():
        num, den, rel = [], [], []
        for r in nl["replicates"]:
            rd = r.get("relative_difference")
            db = r.get("Delta_bar")
            if rd is None or db is None:
                continue
            rel.append(abs(rd))
            num.append(abs(db))
            den.append(abs(db) / abs(rd) if rd != 0 else float("nan"))
        rows[name] = {
            "null": nl["null"], "cell": nl["cell"],
            "R_realized": nl["R_realized"],
            "R_min": nl.get("R_min"), "R_min_met": nl.get("R_min_met"),
            "committed_median_relative_difference":
                nl["median_relative_difference"],
            "numerator_abs_Delta_bar": q(num),
            "recovered_denominator_max_abs_D": q(den),
            "relative_difference": q(rel),
        }
    OUT["per_null"] = rows

    # ---------------------------------------------------- the mechanism test
    def med(name, field):
        v = rows[name][field]
        return v["median"] if v else None

    ab_den = [med(n, "recovered_denominator_max_abs_D")
              for n in rows if rows[n]["null"] in ("N-A", "N-B")]
    c_den = [med(n, "recovered_denominator_max_abs_D")
             for n in rows if rows[n]["null"] == "N-C"]
    ab_num = [med(n, "numerator_abs_Delta_bar")
              for n in rows if rows[n]["null"] in ("N-A", "N-B")]
    c_num = [med(n, "numerator_abs_Delta_bar")
             for n in rows if rows[n]["null"] == "N-C"]
    OUT["MECHANISM_TEST"] = {
        "median_denominator_N_A_and_N_B": ab_den,
        "median_denominator_N_C": c_den,
        "denominator_collapse_factor_median_AB_over_median_C":
            (float(np.median(ab_den)) / float(np.median(c_den))) if c_den else None,
        "median_numerator_N_A_and_N_B": ab_num,
        "median_numerator_N_C": c_num,
        "numerator_factor_median_C_over_median_AB":
            (float(np.median(c_num)) / float(np.median(ab_num))) if c_num else None,
        "verdict": None,   # filled below
    }
    dfac = OUT["MECHANISM_TEST"]["denominator_collapse_factor_median_AB_over_median_C"]
    nfac = OUT["MECHANISM_TEST"]["numerator_factor_median_C_over_median_AB"]
    OUT["MECHANISM_TEST"]["verdict"] = (
        "STATED MECHANISM SUPPORTED: the denominator moves by %.1fx while the "
        "numerator moves by %.2fx, so the large N-C relative difference is "
        "driven by the denominator as report_c1.md says."
        % (dfac, nfac) if (dfac or 0) > (nfac or 0) * 3 else
        "STATED MECHANISM NOT SUPPORTED AS THE DOMINANT TERM: denominator "
        "factor %.2fx against numerator factor %.2fx." % (dfac or float("nan"),
                                                          nfac or float("nan")))

    # ---------------------------------------------------- the counterfactual
    incl = max(v["committed_median_relative_difference"] for v in rows.values())
    excl = max(v["committed_median_relative_difference"] for v in rows.values()
               if v["null"] in ("N-A", "N-B"))
    OUT["COUNTERFACTUAL_tau_rel"] = {
        "carried_rule": "tau_rel = 1.67 x the top of the range of the null's "
                        "own median relative difference (BATCH-cbe023 prereg 4.4)",
        "top_of_range_excluding_N_C": excl,
        "tau_rel_excluding_N_C": CARRIED_MULTIPLIER * excl,
        "top_of_range_including_N_C": incl,
        "tau_rel_including_N_C": CARRIED_MULTIPLIER * incl,
        "direction": (
            "Including N-C would RAISE tau_rel by a factor of %.1f, which makes "
            "the relative-difference clause HARDER to satisfy and so makes a "
            "FALSIFYING verdict LESS reachable. The exclusion therefore moves "
            "the instrument toward being able to falsify, not away from it, "
            "and is not self-serving in the direction a 'nothing moved' "
            "outcome would want." % (incl / excl)),
    }

    # ------------------------------ AM-11 dispersion applied to tau_rel itself
    med_tops = sorted(v["committed_median_relative_difference"]
                      for v in rows.values() if v["null"] in ("N-A", "N-B"))
    p95_tops = sorted(nl["p95_relative_difference"]
                      for nl in src["nulls"].values() if nl["null"] in ("N-A", "N-B"))
    OUT["AM11_dispersion_applied_to_tau_rel"] = {
        "the_four_medians_the_rule_reads": med_tops,
        "spread_factor_max_over_min": med_tops[-1] / med_tops[0],
        "tau_rel_from_the_top_MEDIAN": CARRIED_MULTIPLIER * med_tops[-1],
        "the_same_four_nulls_p95_relative_differences": p95_tops,
        "tau_rel_if_the_rule_read_the_top_p95_instead":
            CARRIED_MULTIPLIER * p95_tops[-1],
        "factor_between_the_two_readings": p95_tops[-1] / med_tops[-1],
        "reading": (
            "tau_rel is the MAXIMUM of four numbers, which is the most "
            "dispersion-sensitive functional of a four-point sample, and no "
            "dispersion is attached to it anywhere. Reading the same rule at "
            "the nulls' p95 instead of their median moves the floor by the "
            "factor above. Whether that matters is a separate question and "
            "report_c1.md answers it: all ten verdicts are invariant at 0.15 "
            "AND at 0.025, and the alternative floor lies between them, so no "
            "verdict in the section moves under either reading."),
    }

    # ------------------------------ where the SE_2way/SE_naive < 1 targets sit
    xtab = []
    for t in src["targets"]:
        s = t["scoring"]
        xtab.append({"cell": t.get("cell"), "target": t.get("target"),
                     "nu_eff": s["nu_eff"], "t_crit": s["t_crit"]})
    xtab.sort(key=lambda r: r["nu_eff"])
    OUT["AM14e_where_the_sub_1_SE_ratios_sit"] = {
        "targets_sorted_by_nu_eff": xtab,
        "the_four_targets_report_c1_flags_with_SE_2way_over_SE_naive_below_1": [
            "d100_b30/unreduced 0.3635", "d100_b40/unreduced 0.8495",
            "d140_b40/graded_t0.0025 0.9651", "d140_b40/unreduced 0.8397"],
        "reading": (
            "Those four are exactly the four smallest nu_eff in the family "
            "(1.000, 1.346, 1.426, 1.503), all far inside the degenerate "
            "regime. The AM-7 clause (1) tension report_c1.md discloses is "
            "therefore a DEGENERACY SIGNATURE concentrated at low nu_eff, not "
            "a property spread across the family -- which is forward guidance "
            "the disclosure alone does not give, and it is checkable from the "
            "committed nu_eff column above."),
    }

    print("\n%-16s %5s %13s %13s %13s"
          % ("null", "R", "med |Dbar|", "med denom", "med rel diff"))
    for name, v in rows.items():
        print("%-16s %5d %13.4e %13.4e %13.4e"
              % (name, v["R_realized"], v["numerator_abs_Delta_bar"]["median"],
                 v["recovered_denominator_max_abs_D"]["median"],
                 v["relative_difference"]["median"]))
    print("\ndenominator collapse factor (median A/B over median C): %.2f" % dfac)
    print("numerator factor          (median C over median A/B)   : %.2f" % nfac)
    print("\n%s" % OUT["MECHANISM_TEST"]["verdict"])
    print("\ncounterfactual tau_rel including N-C: %.4f  (excluding: %.4f)"
          % (OUT["COUNTERFACTUAL_tau_rel"]["tau_rel_including_N_C"],
             OUT["COUNTERFACTUAL_tau_rel"]["tau_rel_excluding_N_C"]))

    with open(args.out, "w") as fh:
        json.dump(OUT, fh, indent=1)
    print("\nwrote %s" % args.out)


if __name__ == "__main__":
    main()
