#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RED TEAM PROBE B2  --  TASK-20260809-444fe7 / BATCH-9e3584 / GOAL-MLKEM-005

IS THE SECTION C INSTRUMENT'S "DEGENERATE REGIME" A PROPERTY OF THE DATA OR OF
THE 8 x 4 DESIGN?

PROVENANCE.  Written AFTER probe_c1_seratio_null.py was run and read, which
reported that 14.4% of EFFECT-FREE 8 x 4 tables trip the
NEGATIVE_VARIANCE_COMPONENT branch.  That raised the obvious next question,
which this probe answers.  Disclosed as post-hoc.  CLAIM TIER: TOY.

WHAT IT ASKS.  Section C2 records that four of the ten targets cannot fire even
at an injection of 12 SE, because their |t|crit lies between 18.9 and 70.0,
driven by nu_eff between 1.00 and 1.50.  The producer calls this "the
degenerate regime" and says the control correctly does not fire there.  Nobody
has asked what an EFFECT-FREE table of the same shape does.  If nu_eff <= 1.5
arises routinely in a null 8 x 4 table, the degenerate regime is a property of
the DESIGN (S = 8, E = 4, Satterthwaite on three mean squares) and not of the
measurements -- which changes the forward recommendation from "interpret those
targets cautiously" to "the design cannot resolve those targets at any effect
size".

NULL MODELS, both of the identical shape:
  N1  iid standard normal 8 x 4              (no support effect, no pool effect)
  N3  support-and-pool structured normal:    entry = a_s + b_e + eps, with
      variance shares (0.4, 0.2, 0.4).  A table WITH real structure, so the
      probe is not confined to the unstructured case.

WHAT COULD NOT FAIL, BOTH DIRECTIONS:
  * could-not-FIRE: if nu_eff were bounded below by (S-1)(E-1) = 21 the probe
    could never see a degenerate draw.  It is not: the Satterthwaite branch can
    return values near 1, and the realized minimum is reported.
  * could-not-PASS: if nu_eff were degenerate in essentially every null draw,
    the probe could not distinguish design from data.  The full distribution is
    reported so both readings are visible.

WRITES exactly one file: probe_c1_nueff_null.json, beside this script.
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
S, E = 8, 4
ALPHA_PAIR = 0.10 / 11
N_NULL = 100000
SEED = 20260812


def se_decomposition(Delta):
    """CARRIED VERBATIM from TASK-20260809-3eb72c/posctl_c2.py."""
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
    return max(1.0, nu), negflag


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--n-null", type=int, default=N_NULL)
    args = ap.parse_args()

    R = OrderedDict()
    R["probe_id"] = "PROBE-B2 / probe_c1_nueff_null"
    R["task_id"] = "TASK-20260809-444fe7"
    R["role"] = "red-team"
    R["batch_id"] = "BATCH-9e3584"
    R["goal_id"] = "GOAL-MLKEM-005"
    R["claim_tier"] = "toy"
    R["provenance"] = ("Written AFTER probe_c1_seratio_null.py was run and "
                       "read. Disclosed as post-hoc. Rescored nothing.")
    R["environment"] = {"python": sys.version.split()[0],
                        "numpy": np.__version__,
                        "platform": platform.platform()}
    R["could_not_fail_named_before_the_run"] = {
        "could_not_FIRE": "if nu_eff were bounded below by (S-1)(E-1)=21 no "
                          "degenerate draw could appear. It is not; the "
                          "realized minimum is reported.",
        "could_not_PASS": "if nearly every null draw were degenerate the probe "
                          "could not separate design from data. The full "
                          "distribution is reported."}

    rng = np.random.default_rng(SEED)
    out = {}
    for label, gen in (
            ("N1_iid_normal", lambda: rng.standard_normal((S, E))),
            ("N3_support_and_pool_structured",
             lambda: (np.sqrt(0.4) * rng.standard_normal((S, 1))
                      + np.sqrt(0.2) * rng.standard_normal((1, E))
                      + np.sqrt(0.4) * rng.standard_normal((S, E))))):
        nus = np.empty(args.n_null)
        negs = 0
        for j in range(args.n_null):
            nu, neg = se_decomposition(gen())
            nus[j] = nu
            negs += int(neg)
        tcrit = student_t.ppf(1.0 - ALPHA_PAIR / 2.0, nus)
        out[label] = {
            "n_draws": args.n_null,
            "P_nu_eff_le_1.5": float(np.mean(nus <= 1.5)),
            "P_nu_eff_le_2": float(np.mean(nus <= 2.0)),
            "P_nu_eff_le_7": float(np.mean(nus <= 7.0)),
            "P_t_crit_ge_8": float(np.mean(tcrit >= 8.0)),
            "P_t_crit_ge_18": float(np.mean(tcrit >= 18.0)),
            "nu_eff_quantiles": {q: float(np.quantile(nus, v)) for q, v in
                                 [("p01", 0.01), ("p05", 0.05), ("p25", 0.25),
                                  ("p50", 0.50), ("p75", 0.75),
                                  ("p95", 0.95)]},
            "nu_eff_min": float(nus.min()), "nu_eff_max": float(nus.max()),
            "fraction_NEGATIVE_VARIANCE_COMPONENT": negs / args.n_null,
            "expected_count_t_crit_ge_8_out_of_10":
                10.0 * float(np.mean(tcrit >= 8.0))}
    R["nulls"] = out

    src = json.load(open(COMMITTED_AM7))
    obs = []
    for t in src["targets"]:
        D = np.asarray(t["Delta_table_S_by_E"], dtype=float)
        nu, neg = se_decomposition(D)
        obs.append({"cell": t["cell"], "target": t["target"],
                    "nu_eff": nu,
                    "t_crit": float(student_t.ppf(1.0 - ALPHA_PAIR / 2.0, nu)),
                    "NEGATIVE_VARIANCE_COMPONENT": neg})
    R["committed_targets"] = obs
    R["headline"] = {
        "committed_n_targets_with_t_crit_ge_8":
            sum(1 for o in obs if o["t_crit"] >= 8.0),
        "N1_expected_n_of_10_with_t_crit_ge_8":
            out["N1_iid_normal"]["expected_count_t_crit_ge_8_out_of_10"],
        "N3_expected_n_of_10_with_t_crit_ge_8":
            out["N3_support_and_pool_structured"]
               ["expected_count_t_crit_ge_8_out_of_10"],
        "committed_n_NEGATIVE_VARIANCE_COMPONENT":
            sum(1 for o in obs if o["NEGATIVE_VARIANCE_COMPONENT"]),
        "N1_expected_n_of_10_NEGATIVE_VARIANCE_COMPONENT":
            10.0 * out["N1_iid_normal"]["fraction_NEGATIVE_VARIANCE_COMPONENT"],
        "reading": "If the null rate matches the committed rate, the "
                   "degenerate regime is a property of the S=8, E=4 design "
                   "under Satterthwaite, not of the measurements."}
    R["what_this_probe_does_NOT_establish"] = [
        "It does NOT rescore Section C1 or C2 and moves no verdict.",
        "It does NOT show any committed number is wrong; the committed nu_eff "
        "values are reproduced here and reported beside the null.",
        "A design-level explanation of degeneracy is not a claim that the "
        "targets have no effect; it is a claim about resolving power.",
        "CLAIM TIER TOY.",
    ]
    R["wall_clock_seconds"] = round(time.time() - T0, 2)

    with open(args.out, "w") as fh:
        json.dump(R, fh, indent=2)
        fh.write("\n")

    print("PROBE B2 -- is the degenerate regime a design property?")
    for k, v in out.items():
        print("  %s: P(nu<=1.5)=%.4f P(nu<=2)=%.4f P(tcrit>=8)=%.4f "
              "P(neg var)=%.4f  nu median %.2f"
              % (k, v["P_nu_eff_le_1.5"], v["P_nu_eff_le_2"],
                 v["P_t_crit_ge_8"], v["fraction_NEGATIVE_VARIANCE_COMPONENT"],
                 v["nu_eff_quantiles"]["p50"]))
    h = R["headline"]
    print("  committed: %d of 10 targets have t_crit >= 8; null expectation "
          "N1 %.2f, N3 %.2f"
          % (h["committed_n_targets_with_t_crit_ge_8"],
             h["N1_expected_n_of_10_with_t_crit_ge_8"],
             h["N3_expected_n_of_10_with_t_crit_ge_8"]))
    print("  committed: %d of 10 NEGATIVE_VARIANCE_COMPONENT; null expectation "
          "N1 %.2f" % (h["committed_n_NEGATIVE_VARIANCE_COMPONENT"],
                       h["N1_expected_n_of_10_NEGATIVE_VARIANCE_COMPONENT"]))
    for o in obs:
        print("   %-9s %-16s nu_eff %8.3f  t_crit %8.3f  negvar=%s"
              % (o["cell"], o["target"], o["nu_eff"], o["t_crit"],
                 o["NEGATIVE_VARIANCE_COMPONENT"]))
    print("  wall clock %.2f s" % R["wall_clock_seconds"])


if __name__ == "__main__":
    main()
