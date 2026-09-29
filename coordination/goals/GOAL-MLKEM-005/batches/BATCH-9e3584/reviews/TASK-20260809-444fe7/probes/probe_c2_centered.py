#!/usr/bin/env python3
"""PROBE C (red team, TASK-20260809-444fe7) -- THE CENTERED CONTROL THE
PRODUCER PROPOSED AND DECLINED, PLUS THE EQUIVARIANCE THE LADDER CANNOT ESCAPE.

NOT PRE-REGISTERED. Rescores NO frozen verdict. It neither reinstates nor
negates the frozen Section C label, and it says nothing about tail sufficiency
in either direction. CLAIM TIER TOY.

RE-EXECUTABLE from the repository root:
    python3 <this file> --out probe_c2_centered_output.json

WHAT IT ATTACKS
---------------
report_c2.md (TASK-20260809-3eb72c) records P-C2c FALSIFIED, diagnoses the
falsification as a defect in prereg 5.2's own SHOULD-NOT-catch clause rather
than in the instrument, proposes a CENTERED variant as the repair, and
declines to run it ("it is not in the notarized text, and adding an
unregistered analysis to rescue a falsified prediction is the failure mode
this batch exists to close"). The refusal to self-rescue is correct
discipline; it also leaves the diagnosis untested. A red-team probe is exactly
where an unregistered check belongs, so I build it.

report_c2.md also reports P-C2e HOLDS -- "the recovered SE matches the
committed SE to floating-point rounding at every target and every rung ...
which is what AM-14(b) asked to be shown rather than assumed", max deviation
8.53e-16 -- and prereg 5.4 claims the could-not-FIRE arrangement is averted
because the offset goes into the raw S x E table rather than into Delta_bar.

BLOCK 1 -- EQUIVARIANCE. se_decomposition computes MS_S, MS_P and MS_res from
(row - gm), (col - gm) and (D - row - col + gm). Adding a constant c to every
entry of D adds c to gm, to every row mean and to every column mean, so every
one of those three quantities is ALGEBRAICALLY UNCHANGED. SE, nu_eff and the
NEGATIVE_VARIANCE_COMPONENT flag are therefore invariant under a constant
offset EXACTLY, and the only residual is float cancellation. This block tests
whether P-C2e could have failed, by pushing the offset far past the
pre-registered ladder (up to 1e6 SE) and watching the deviation.

BLOCK 2 -- THE CENTERED CONTROL. D_centered = D - mean(D), then the same
ladder. On the centered table the rung value is the ONLY signal, so the first
firing rung measures the instrument's own sensitivity rather than the sum of a
pre-existing near-critical Delta_bar and a small offset.

BLOCK 3 -- A STRUCTURED INJECTION. Constant offsets are an exact symmetry of
the estimator, so no constant ladder of any length can detect SE inflation.
This block injects into ONE pool column only, which does move the variance
components, and reports how the recovered SE responds. It is the injection
class under which the AM-14(b) failure mode is observable at all.

MY OWN CHECK'S COULD-NOT-FAIL ARRANGEMENTS, NAMED BEFORE RUNNING, BOTH WAYS
---------------------------------------------------------------------------
* could-not-FIRE: if my re-implementation of se_decomposition/full_score
  differed from the producer's, block 2 and 3 would measure my code and not
  theirs. Guarded by a reproduction gate: at delta = 0 my path must reproduce
  the COMMITTED scoring (Delta_bar, SE, nu_eff, |t|, verdict) at all ten
  targets to 1e-12 relative, and the probe reports the realized deviation. If
  it does not reproduce, the probe reports INFRASTRUCTURE SIGNAL and claims
  nothing.
* could-not-PASS: block 2 could be arranged to fire on everything by
  centering AND lowering |t|crit, or by starting the ladder above the critical
  values. Guarded by using the FROZEN ladder {0, 0.5, 1, 2, 3, 4, 6, 8, 12},
  the FROZEN alpha_pair = 0.10/11 and the FROZEN tau_rel values 0.15 and
  0.025. Nothing of mine enters the thresholds. My stated expectation before
  running block 2 is that NO target fires at delta/SE <= 1.0 on the centered
  table -- i.e. that the producer's own diagnosis is CORRECT and my suspicion
  of it is wrong. That expectation is recorded here so that confirming it
  counts against my thesis and is reported at the same weight.

AM-10 / AM-11 ON THIS PROBE'S OWN STATISTICS
--------------------------------------------
Every statistic is reported per target across all ten targets, with its range
over the ten (min / median / max) rather than as a single pooled number, and
every ladder is reported in full rather than at its headline rung. The
replication unit here is the target, and the underlying 8 x 4 tables are the
committed ones: this probe adds NO new draw and therefore makes no claim that
requires one.
"""
import argparse
import json
import os
import subprocess
from collections import OrderedDict

import numpy as np
from scipy.stats import t as student_t

AM7 = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/tasks/"
       "TASK-20260808-3a5f18/results_am7.json")
LADDER = [0.0, 0.5, 1.0, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0]      # prereg 5.2, frozen
EXTREME = [1e2, 1e4, 1e6]                                     # mine, block 1 only
ALPHA_PAIR = 0.10 / 11.0                                      # frozen
TAU_FROZEN, TAU_REBUILT = 0.15, 0.025                         # frozen / C1
REPRO_TOL = 1e-12                                             # frozen


def se_decomposition(Delta):
    """Transcribed from posctl_c2.py, itself CARRIED VERBATIM from
    BATCH-cbe023 measure_am7.py, degenerate branch included."""
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
    return {"MS_S": MS_S, "MS_P": MS_P, "MS_res": MS_res,
            "var_Delta_bar": float(var), "SE_Delta_bar": float(np.sqrt(var)),
            "nu_eff": nu, "NEGATIVE_VARIANCE_COMPONENT": negflag,
            "Delta_bar": gm}


def full_score(Delta, M, tau_rel):
    dec = se_decomposition(np.asarray(Delta, dtype=float))
    dbar, se, nu = dec["Delta_bar"], dec["SE_Delta_bar"], dec["nu_eff"]
    tcrit = float(student_t.ppf(1.0 - ALPHA_PAIR / 2.0, nu))
    at = (abs(dbar) / se) if se > 0 else None
    rel = (abs(dbar) / M) if M > 0 else None
    return {"Delta_bar": dbar, "SE": se, "nu_eff": nu, "t_crit": tcrit,
            "abs_t": at, "relative_difference": rel,
            "FALSIFYING_PAIR": bool(at is not None and at > tcrit
                                    and rel is not None and rel > tau_rel),
            "NEGATIVE_VARIANCE_COMPONENT": dec["NEGATIVE_VARIANCE_COMPONENT"]}


def load_am7(path):
    if os.path.exists(path):
        return json.load(open(path)), "working tree"
    blob = subprocess.run(["git", "show", "HEAD:%s" % path],
                          capture_output=True, check=True)
    return json.loads(blob.stdout.decode()), "git HEAD"


def rng_stats(vals):
    a = np.asarray([v for v in vals if v is not None], dtype=float)
    if a.size == 0:
        return None
    return {"n": int(a.size), "min": float(a.min()),
            "median": float(np.median(a)), "max": float(a.max())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--am7", default=AM7)
    ap.add_argument("--out", default="probe_c2_centered_output.json")
    args = ap.parse_args()

    src, where = load_am7(args.am7)
    OUT = OrderedDict()
    OUT["probe"] = "PROBE-C"
    OUT["task_id"] = "TASK-20260809-444fe7"
    OUT["claim_tier"] = "toy"
    OUT["status_of_this_measurement"] = (
        "RED-TEAM PROBE. NOT PRE-REGISTERED. No new draw; the 8 x 4 tables are "
        "the committed ones. Rescores no verdict and adjudicates no label.")
    OUT["source"] = {"path": args.am7, "read_from": where}
    OUT["my_expectation_recorded_before_running_block_2"] = (
        "NO target fires at delta/SE <= 1.0 on the centered table, i.e. the "
        "producer's own diagnosis of P-C2c is CORRECT and my suspicion of it "
        "is wrong. Recorded here so that confirming it counts against my "
        "thesis.")

    print("=" * 78)
    print("PROBE C -- centered control, equivariance, structured injection")
    print("RED-TEAM PROBE, NOT PRE-REGISTERED, RESCORES NOTHING. TOY.")
    print("source: %s (%s)" % (args.am7, where))
    print("=" * 78)

    # ---------------------------------------------------------- gate: reproduce
    gate = []
    for t in src["targets"]:
        D0 = np.asarray(t["Delta_table_S_by_E"], dtype=float)
        M = max(abs(t["D_GR_mean"]), abs(t["D_TL_mean"]))
        c = t["scoring"]
        mine = full_score(D0, M, TAU_FROZEN)
        dev = max(
            abs(mine["Delta_bar"] - c["Delta_bar"]) / max(abs(c["Delta_bar"]), 1e-300),
            abs(mine["SE"] - c["SE_Delta_bar"]) / max(abs(c["SE_Delta_bar"]), 1e-300),
            abs(mine["nu_eff"] - c["nu_eff"]) / max(abs(c["nu_eff"]), 1e-300),
            abs(mine["abs_t"] - c["abs_t"]) / max(abs(c["abs_t"]), 1e-300))
        gate.append({"cell": t.get("cell"), "target": t.get("target"),
                     "max_relative_deviation": dev,
                     "verdict_matches": bool(mine["FALSIFYING_PAIR"]
                                             == c["FALSIFYING_PAIR"])})
    worst = max(g["max_relative_deviation"] for g in gate)
    OUT["reproduction_gate"] = {
        "n_targets": len(gate), "max_relative_deviation": worst,
        "tolerance": REPRO_TOL,
        "PASSES": bool(worst <= REPRO_TOL and all(g["verdict_matches"] for g in gate)),
        "per_target": gate}
    print("\n[gate] my path reproduces the COMMITTED scoring at %d targets, "
          "max rel dev %.3e -> %s"
          % (len(gate), worst, "PASS" if OUT["reproduction_gate"]["PASSES"] else "FAIL"))
    if not OUT["reproduction_gate"]["PASSES"]:
        OUT["INFRASTRUCTURE_SIGNAL"] = (
            "My re-implementation does not reproduce the committed scoring. "
            "This is an infrastructure signal about THIS PROBE and is never "
            "negative evidence about the producer's instrument. Blocks 2 and 3 "
            "are reported but carry no weight.")
        print("      -> INFRASTRUCTURE SIGNAL; blocks 2/3 carry no weight.")

    # ---------------------------------------------------------- block 1
    print("\n[1] EQUIVARIANCE: could P-C2e have failed?")
    b1 = []
    for t in src["targets"]:
        D0 = np.asarray(t["Delta_table_S_by_E"], dtype=float)
        se0 = float(t["scoring"]["SE_Delta_bar"])
        dec0 = se_decomposition(D0)
        row = {"cell": t.get("cell"), "target": t.get("target"),
               "committed_SE": se0, "rungs": OrderedDict()}
        for r in LADDER + EXTREME:
            dec = se_decomposition(D0 + r * se0)
            row["rungs"]["%g" % r] = {
                "SE_relative_deviation":
                    abs(dec["SE_Delta_bar"] - dec0["SE_Delta_bar"])
                    / max(abs(dec0["SE_Delta_bar"]), 1e-300),
                "nu_eff_relative_deviation":
                    abs(dec["nu_eff"] - dec0["nu_eff"])
                    / max(abs(dec0["nu_eff"]), 1e-300),
                "negflag_same": bool(dec["NEGATIVE_VARIANCE_COMPONENT"]
                                     == dec0["NEGATIVE_VARIANCE_COMPONENT"]),
            }
        b1.append(row)
    max_frozen = max(v["SE_relative_deviation"]
                     for r in b1 for k, v in r["rungs"].items()
                     if float(k) <= 12.0)
    max_extreme = max(v["SE_relative_deviation"]
                      for r in b1 for k, v in r["rungs"].items()
                      if float(k) > 12.0)
    OUT["block1_equivariance"] = {
        "argument": (
            "MS_S, MS_P and MS_res are functions of (row - gm), (col - gm) and "
            "(D - row - col + gm) only. A constant offset c adds c to D, to gm, "
            "to every row mean and to every column mean, so all three are "
            "unchanged EXACTLY. SE, nu_eff and the NEGATIVE_VARIANCE_COMPONENT "
            "flag are invariants of the constant-offset group action."),
        "max_SE_relative_deviation_over_the_FROZEN_ladder": max_frozen,
        "max_SE_relative_deviation_at_offsets_up_to_1e6_SE": max_extreme,
        "n_targets_whose_negflag_ever_changed": sum(
            1 for r in b1 if not all(v["negflag_same"] for v in r["rungs"].values())),
        "reading": (
            "If the deviation stays at machine epsilon when the offset is "
            "raised by five orders of magnitude beyond the pre-registered "
            "ladder, then P-C2e's 8.53e-16 is the signature of an exact "
            "identity, not the outcome of a test that could have failed. What "
            "it does verify -- and this is real -- is that the IMPLEMENTED "
            "se_decomposition contains no bug breaking that identity, e.g. an "
            "uncentred sum of squares."),
        "per_target": b1}
    print("    max SE rel dev over the FROZEN ladder      : %.3e" % max_frozen)
    print("    max SE rel dev at offsets up to 1e6 * SE   : %.3e" % max_extreme)

    # ---------------------------------------------------------- block 2
    print("\n[2] THE CENTERED CONTROL (proposed by report_c2.md section 4, not run there)")
    b2 = []
    for t in src["targets"]:
        D0 = np.asarray(t["Delta_table_S_by_E"], dtype=float)
        M = max(abs(t["D_GR_mean"]), abs(t["D_TL_mean"]))
        se0 = float(t["scoring"]["SE_Delta_bar"])
        Dc = D0 - D0.mean()                       # THE CENTERING
        rungs = OrderedDict()
        first15 = first025 = None
        for r in LADDER:
            s15 = full_score(Dc + r * se0, M, TAU_FROZEN)
            s025 = full_score(Dc + r * se0, M, TAU_REBUILT)
            rungs["%g" % r] = {
                "abs_t": s15["abs_t"], "t_crit": s15["t_crit"],
                "relative_difference": s15["relative_difference"],
                "SE": s15["SE"], "nu_eff": s15["nu_eff"],
                "FALSIFYING_at_0.15": s15["FALSIFYING_PAIR"],
                "FALSIFYING_at_0.025": s025["FALSIFYING_PAIR"]}
            if first15 is None and s15["FALSIFYING_PAIR"]:
                first15 = r
            if first025 is None and s025["FALSIFYING_PAIR"]:
                first025 = r
        b2.append({
            "cell": t.get("cell"), "target": t.get("target"),
            "committed_abs_t_over_t_crit":
                float(t["scoring"]["abs_t"]) / float(t["scoring"]["t_crit"]),
            "t_crit": float(t["scoring"]["t_crit"]),
            "first_firing_rung_at_0.15": first15,
            "first_firing_rung_at_0.025": first025,
            "fires_at_or_below_1SE_at_0.15": bool(first15 is not None and first15 <= 1.0),
            "rungs": rungs})
    n_over = sum(1 for r in b2 if r["fires_at_or_below_1SE_at_0.15"])
    OUT["block2_centered_control"] = {
        "construction": "D_centered = D - mean(D); then the FROZEN ladder.",
        "n_targets_firing_at_delta_over_SE_le_1_at_tau_0.15": n_over,
        "first_firing_rung_range_at_0.15": rng_stats(
            [r["first_firing_rung_at_0.15"] for r in b2]),
        "first_firing_rung_range_at_0.025": rng_stats(
            [r["first_firing_rung_at_0.025"] for r in b2]),
        "n_targets_never_firing_on_the_frozen_ladder_at_0.15": sum(
            1 for r in b2 if r["first_firing_rung_at_0.15"] is None),
        "per_target": b2}
    print("    targets firing at delta/SE <= 1.0 on the CENTERED table: %d of %d"
          % (n_over, len(b2)))
    print("    %-10s %-18s %8s %10s %10s" % (
        "cell", "target", "t_crit", "first@.15", "first@.025"))
    for r in b2:
        print("    %-10s %-18s %8.3f %10s %10s" % (
            r["cell"], r["target"], r["t_crit"],
            r["first_firing_rung_at_0.15"], r["first_firing_rung_at_0.025"]))

    # ---------------------------------------------------------- block 3
    print("\n[3] A STRUCTURED (non-constant) INJECTION -- one pool column only")
    b3 = []
    for t in src["targets"]:
        D0 = np.asarray(t["Delta_table_S_by_E"], dtype=float)
        M = max(abs(t["D_GR_mean"]), abs(t["D_TL_mean"]))
        se0 = float(t["scoring"]["SE_Delta_bar"])
        rungs = OrderedDict()
        for r in LADDER:
            D = D0.copy()
            D[:, 0] += r * se0 * D0.shape[1]     # same Delta_bar shift as constant r*se0
            s = full_score(D, M, TAU_FROZEN)
            rungs["%g" % r] = {
                "SE": s["SE"],
                "SE_relative_change_vs_committed": (s["SE"] - se0) / se0,
                "nu_eff": s["nu_eff"], "abs_t": s["abs_t"],
                "t_crit": s["t_crit"],
                "FALSIFYING_at_0.15": s["FALSIFYING_PAIR"]}
        b3.append({"cell": t.get("cell"), "target": t.get("target"),
                   "committed_SE": se0, "rungs": rungs})
    infl = [v["SE_relative_change_vs_committed"]
            for r in b3 for v in r["rungs"].values()]
    OUT["block3_structured_injection"] = {
        "construction": (
            "delta is added to ONE pool column (E index 0), scaled by E so the "
            "shift in Delta_bar equals the constant ladder's. Delta_bar moves "
            "identically; the variance components do not."),
        "SE_relative_change_range": rng_stats(infl),
        "max_abs_SE_relative_change": float(np.max(np.abs(infl))),
        "reading": (
            "Under a constant offset the SE cannot move (block 1). Under this "
            "structured offset it does. Whatever the sign, the point is the "
            "same: the pre-registered ladder is confined to the one injection "
            "class under which the quantity AM-14(b) asks about is an "
            "invariant, so its 'no SE inflation detected' is a statement about "
            "the injection, not about the estimator."),
        "per_target": b3}
    print("    |SE relative change| under the structured injection: max %.3e"
          % OUT["block3_structured_injection"]["max_abs_SE_relative_change"])
    print("    (constant-offset counterpart, block 1: max %.3e)" % max_frozen)

    OUT["HEADLINE"] = {
        "P_C2e_could_not_have_failed_under_a_CONSTANT_ladder":
            bool(max_extreme < 1e-10),
        "producer_diagnosis_of_P_C2c_confirmed_by_the_centered_control":
            bool(n_over == 0),
        "the_control_did_run_in_its_could_not_FIRE_arrangement_for_SE_inflation":
            bool(max_frozen < 1e-10),
    }
    with open(args.out, "w") as fh:
        json.dump(OUT, fh, indent=1)
    print("\nHEADLINE: %s" % json.dumps(OUT["HEADLINE"]))
    print("wrote %s" % args.out)


if __name__ == "__main__":
    main()
