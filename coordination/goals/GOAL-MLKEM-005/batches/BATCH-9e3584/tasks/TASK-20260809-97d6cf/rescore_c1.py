#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TASK-20260809-97d6cf / BATCH-9e3584 / GOAL-MLKEM-005
SECTION C1 of the notarized pre-registration -- AM-14 (c), (d), (e).

  prereg  coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/
          TASK-20260809-4011dd/prereg.md
  sha256  190cf4740b0ecefdbe7d1da0868a6258352b044ae5e99da470060f94049c70ea
  notarized by TASK-20260809-91cf76 in commit
  1aa7db5313f6d3da1f366443d4d6066597393402

>>> THIS IS A RE-SCORE OF COMMITTED BATCH-cbe023 DATA UNDER A POST-BATCH
>>> THRESHOLD, AND IT IS LABELLED AS SUCH THROUGHOUT.  It is NOT a fresh
>>> measurement.  It does NOT reinstate the frozen Section C label, and it does
>>> NOT establish that label's negation.  No new draw is taken, no frame is
>>> built, and no projection is run.

What it does, exactly:
  (c) re-derives tau_rel from the REBUILT null's OWN measured distribution by
      the carried design rule of BATCH-cbe023 prereg 4.4, and re-scores at it;
  (d) widens the SUGGESTIVE band to record ANY pair with |t| >= 0.8*|t|crit
      REGARDLESS of the relative floor;
  (e) reports SE_2way / SE_naive at EVERY target, disclosing any ratio below 1.

BATCH-a44d08 IS NOT RESCORED IN ANY RESPECT.
CLAIM TIER: TOY.  certificate.kind: none.

This script writes exactly one file: results_c1.json, in its own task directory.
"""

import argparse
import hashlib
import json
import os
import platform
import resource
import socket
import subprocess
import sys
import time
from collections import OrderedDict

import numpy as np
import scipy
from scipy.stats import t as student_t

T_START = time.time()

TASK_DIR = os.path.dirname(os.path.abspath(__file__))
TASKS_DIR = os.path.normpath(os.path.join(TASK_DIR, ".."))
BATCH_DIR = os.path.normpath(os.path.join(TASKS_DIR, ".."))
BATCHES_DIR = os.path.normpath(os.path.join(BATCH_DIR, ".."))
REPO_ROOT = os.path.normpath(os.path.join(BATCHES_DIR, "..", "..", "..", ".."))

PREREG_REL = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/"
              "TASK-20260809-4011dd/prereg.md")
PREREG_PATH = os.path.join(TASKS_DIR, "TASK-20260809-4011dd", "prereg.md")
SIDECAR_PATH = os.path.join(TASKS_DIR, "TASK-20260809-4011dd",
                            "prereg_sha256.txt")
PREREG_SHA256_EXPECTED = \
    "190cf4740b0ecefdbe7d1da0868a6258352b044ae5e99da470060f94049c70ea"
NOTARIZING_COMMIT = "1aa7db5313f6d3da1f366443d4d6066597393402"

COMMITTED_AM7 = os.path.join(BATCHES_DIR, "BATCH-cbe023", "tasks",
                             "TASK-20260808-3a5f18", "results_am7.json")

# ---------------------------------------------------------- carried constants
TAU_REL_FROZEN = 0.15                      # [carried] BATCH-cbe023 prereg 4.4
ALPHA_PAIR = 0.10 / 11                     # [carried] 0.0090909090909...
SUGGESTIVE_FRAC = 0.8                      # [carried] 4.4
S_SUPPORTS, E_POOLS = 8, 4                 # [carried]

# ---------------------------------------------------- derived here, in advance
# prereg 4.1: tau_rel = 1.67 x the top of the measured range of the null's OWN
# median relative difference. The rule is CARRIED unchanged; only its INPUT
# moves, from the superseded instrument's nulls to this batch's REBUILT nulls.
DESIGN_MULTIPLIER = 1.67
NULLS_FOR_DERIVATION = ["N-A__d100_b40", "N-A__d140_b40",
                        "N-B__d100_b40", "N-B__d140_b40"]
NULLS_EXCLUDED = ["N-C__d100_b40", "N-C__d140_b40"]
TAU_REL_REBUILT_ROUNDED = 0.025            # prereg 4.1, stated BEFORE any rescore

# The detection floor, CARRIED WITH ITS QUALIFIER and used only in that form.
FLOOR_NONDEGENERATE_PCT = 10.83
FLOOR_FAMILY_PCT = 10.8
FLOOR_DEGENERATE_QUALIFIER = (
    "the 3.91% figure belongs to a target flagged NEGATIVE-VARIANCE-COMPONENT "
    "and may not be cited without that qualifier in the same sentence; the "
    "tightest NON-degenerate floor is 10.83% relative and the family-level "
    "bound over targets with a well-defined two-way SE is ~10.8% relative")


def sha256_file(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def git(*a, cwd=REPO_ROOT):
    try:
        return subprocess.check_output(("git",) + a, cwd=cwd,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception as ex:
        return "GIT ERROR: %s" % ex


def verify_prereg():
    out = OrderedDict()
    top = git("rev-parse", "--show-toplevel")
    if os.path.realpath(top) != os.path.realpath(REPO_ROOT):
        raise SystemExit("ABORT: repo root mismatch")
    live = sha256_file(PREREG_PATH)
    sidecar = open(SIDECAR_PATH).read().split()[0]
    oid = git("rev-parse", "%s:%s" % (NOTARIZING_COMMIT, PREREG_REL))
    blob = hashlib.sha256(subprocess.check_output(
        ("git", "cat-file", "blob", oid), cwd=REPO_ROOT)).hexdigest()
    parent = git("rev-parse", "%s^" % NOTARIZING_COMMIT)
    absent = git("cat-file", "-e",
                 "%s:%s" % (parent, PREREG_REL)).startswith("GIT ERROR")
    out.update({"sha256_working_tree": live, "sha256_sidecar": sidecar,
                "sha256_task_card_constant": PREREG_SHA256_EXPECTED,
                "sha256_notarized_blob": blob,
                "notarizing_commit": NOTARIZING_COMMIT,
                "notarizing_commit_parent": parent,
                "negative_test_absent_at_parent": absent,
                "is_ancestor_of_HEAD": subprocess.call(
                    ("git", "merge-base", "--is-ancestor", NOTARIZING_COMMIT,
                     "HEAD"), cwd=REPO_ROOT, stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL) == 0})
    out["ALL_FOUR_AGREE"] = (live == sidecar == PREREG_SHA256_EXPECTED == blob)
    if not out["ALL_FOUR_AGREE"]:
        raise SystemExit("ABORT: prereg sha256 mismatch %s" % json.dumps(out))
    if not absent:
        raise SystemExit("ABORT: frozen text present at the notarizing parent")
    return out


# ================================== the SE decomposition, CARRIED VERBATIM
def se_decomposition(Delta):
    """Two-way random-effects decomposition on the S x E table, BATCH-cbe023
    prereg 4.3, carried verbatim including the degenerate branch."""
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


def se_naive(Delta):
    """SE_naive = sd(flattened table, ddof=1) / sqrt(S*E)  (prereg 4.3)."""
    a = np.asarray(Delta, dtype=float).ravel()
    return float(a.std(ddof=1) / np.sqrt(a.size))


def score_at(Delta, M, tau_rel):
    """The carried pair criterion, evaluated at a supplied tau_rel, PLUS the
    WIDENED SUGGESTIVE band of AM-14(d) which carries NO floor condition."""
    dec = se_decomposition(np.asarray(Delta, dtype=float))
    dbar, se, nu = dec["Delta_bar"], dec["SE_Delta_bar"], dec["nu_eff"]
    tcrit = float(student_t.ppf(1.0 - ALPHA_PAIR / 2.0, nu))
    at = (abs(dbar) / se) if se > 0 else None
    rel = (abs(dbar) / M) if M > 0 else None
    cond_i = bool(at is not None and at > tcrit)
    cond_ii = bool(rel is not None and rel > tau_rel)
    floor = (tcrit * se / M) if M > 0 else None
    return {
        "tau_rel_used": tau_rel,
        "Delta_bar": dbar, "SE_Delta_bar": se, "nu_eff": nu,
        "t_crit": tcrit, "abs_t": at,
        "abs_t_over_t_crit": (at / tcrit) if (at is not None and tcrit) else None,
        "relative_difference": rel,
        "condition_i_t": cond_i, "condition_ii_relative": cond_ii,
        "FALSIFYING_PAIR": bool(cond_i and cond_ii),
        "detection_floor_relative": floor,
        "floor_below_tau_rel": (bool(floor < tau_rel)
                                if floor is not None else None),
        "SUGGESTIVE_carried_band": bool(
            at is not None and cond_ii and SUGGESTIVE_FRAC * tcrit <= at < tcrit),
        "SUGGESTIVE_WIDENED_band_AM14d": bool(
            at is not None and SUGGESTIVE_FRAC * tcrit <= at < tcrit),
        "NEGATIVE_VARIANCE_COMPONENT": dec["NEGATIVE_VARIANCE_COMPONENT"],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    RES = OrderedDict()
    RES.update({"task_id": "TASK-20260809-97d6cf", "batch_id": "BATCH-9e3584",
                "goal_id": "GOAL-MLKEM-005", "role": "executor",
                "section": "C1 -- AM-14 (c),(d),(e)", "claim_tier": "toy"})
    RES["THIS_IS_A_RE_SCORE_NOT_A_MEASUREMENT"] = (
        "Every number below is computed from COMMITTED BATCH-cbe023 data under "
        "a POST-BATCH threshold. No new draw was taken, no frame was built and "
        "no projection was run. This re-score does NOT reinstate the frozen "
        "Section C label and does NOT establish its negation.")
    RES["certificate"] = {"kind": "none",
                          "reason": "no discrete-log solve and no factor-base "
                                    "relation is claimed or produced"}
    RES["governed_by"] = {"prereg": PREREG_REL,
                          "sha256": PREREG_SHA256_EXPECTED,
                          "notarizing_commit": NOTARIZING_COMMIT}

    print("=" * 78)
    print("SECTION C1 -- AM-14 (c),(d),(e)   BATCH-9e3584 / TASK-20260809-97d6cf")
    print("A RE-SCORE OF COMMITTED DATA UNDER A POST-BATCH THRESHOLD.")
    print("NOT a fresh measurement.  CLAIM TIER: TOY.")
    print("=" * 78)

    print("\n[0] prereg notarization gate -- ABORT ON MISMATCH")
    RES["prereg_verification"] = verify_prereg()
    print("    ALL FOUR AGREE: %s" % RES["prereg_verification"]["ALL_FOUR_AGREE"])

    src = json.load(open(COMMITTED_AM7))
    RES["source"] = {
        "path": ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/tasks/"
                 "TASK-20260808-3a5f18/results_am7.json"),
        "sha256": sha256_file(COMMITTED_AM7),
        "status": "COMMITTED INPUT, read only. Not modified, not rescored "
                  "beyond what AM-14 (c),(d),(e) direct.",
    }

    # ---------------------------------------------- (c) the floor, re-derived
    print("\n[1] AM-14(c): re-derive tau_rel from the REBUILT null's own "
          "distribution")
    meds = OrderedDict()
    for k in NULLS_FOR_DERIVATION:
        meds[k] = float(src["nulls"][k]["median_relative_difference"])
        print("    %-16s median relative difference  %.8f" % (k, meds[k]))
    top = max(meds.values())
    tau_exact = DESIGN_MULTIPLIER * top
    excl = OrderedDict((k, float(src["nulls"][k]["median_relative_difference"]))
                       for k in NULLS_EXCLUDED)
    RES["tau_rel_rederivation"] = {
        "carried_design_rule": (
            "tau_rel = 1.67 x the top of the measured range of the NULL's OWN "
            "median relative difference -- 'the smallest round multiple that "
            "puts the floor clearly above the null's central tendency rather "
            "than at its edge'. CARRIED UNCHANGED from BATCH-cbe023 prereg 4.4; "
            "only its INPUT moves, from the superseded instrument's nulls to "
            "this batch's REBUILT nulls, which is what AM-14(c) requires."),
        "inputs_rebuilt_null_medians": meds,
        "top_of_range": top,
        "multiplier": DESIGN_MULTIPLIER,
        "tau_rel_exact": tau_exact,
        "tau_rel_rounded_USED": TAU_REL_REBUILT_ROUNDED,
        "tau_rel_frozen_for_comparison": TAU_REL_FROZEN,
        "stated_in_the_prereg_before_any_rescore": True,
        "N_C_excluded_and_why": {
            "excluded_nulls": excl,
            "reason": (
                "N-C is the SECONDARY Gaussian instrument check. For Gaussian "
                "errors R ~ Beta(beta/2,(d-beta)/2) EXACTLY for every "
                "orthonormal frame, so D = q_emp/q_Beta - 1 is driven to ~0 on "
                "BOTH sides and the DENOMINATOR max(|D_GR|,|D_TL|) of the "
                "relative difference collapses. Its median relative differences "
                "are therefore an artifact of a vanishing denominator, not a "
                "measure of null central tendency. N-C also ran at R = 60, "
                "below the frozen R_min = 200. AM-14(c) names exactly the four "
                "N-A/N-B medians. Both the exclusion and the excluded numbers "
                "are reported here."),
        },
    }
    print("    top of range %.8f   x %.2f  ->  tau_rel = %.8f  (used: %.3f)"
          % (top, DESIGN_MULTIPLIER, tau_exact, TAU_REL_REBUILT_ROUNDED))
    print("    N-C EXCLUDED (vanishing denominator, R = 60 < R_min = 200): %s"
          % {k: round(v, 6) for k, v in excl.items()})

    # ------------------------------------------------------ re-score at both
    print("\n[2] re-score every target at BOTH tau_rel = %.2f (frozen) and "
          "%.3f (re-derived)" % (TAU_REL_FROZEN, TAU_REL_REBUILT_ROUNDED))
    rows = []
    for t in src["targets"]:
        D = np.asarray(t["Delta_table_S_by_E"], dtype=float)
        M = max(abs(t["D_GR_mean"]), abs(t["D_TL_mean"]))
        s_frozen = score_at(D, M, TAU_REL_FROZEN)
        s_new = score_at(D, M, TAU_REL_REBUILT_ROUNDED)
        se2 = s_frozen["SE_Delta_bar"]
        sen = se_naive(D)
        committed = t["scoring"]
        repro = {
            "committed_Delta_bar": committed["Delta_bar"],
            "recomputed_Delta_bar": s_frozen["Delta_bar"],
            "committed_SE": committed["SE_Delta_bar"],
            "recomputed_SE": se2,
            "committed_abs_t": committed["abs_t"],
            "recomputed_abs_t": s_frozen["abs_t"],
            "committed_FALSIFYING": committed["FALSIFYING_PAIR"],
            "recomputed_FALSIFYING": s_frozen["FALSIFYING_PAIR"],
            "max_rel_dev": max(
                abs(s_frozen["Delta_bar"] - committed["Delta_bar"])
                / max(abs(committed["Delta_bar"]), 1e-300),
                abs(se2 - committed["SE_Delta_bar"])
                / max(abs(committed["SE_Delta_bar"]), 1e-300)),
        }
        rows.append(OrderedDict([
            ("cell", t["cell"]), ("target", t["target"]),
            ("INFORMATIVE", t["INFORMATIVE"]),
            ("reproduction_of_committed_scoring", repro),
            ("at_tau_rel_frozen_0.15", s_frozen),
            ("at_tau_rel_rederived_0.025", s_new),
            ("SE_2way", se2), ("SE_naive", sen),
            ("SE_2way_over_SE_naive", (se2 / sen) if sen > 0 else None),
            ("SE_RATIO_BELOW_1_DISCLOSED",
             bool(sen > 0 and se2 / sen < 1.0)),
            ("SE_ratio_note",
             "AM-14(e): a ratio below 1 is in tension with AM-7 clause (1) and "
             "is disclosed here explicitly, per target."
             if (sen > 0 and se2 / sen < 1.0) else None),
            ("VERDICT_INVARIANT_TO_THE_REPAIR",
             bool(s_frozen["FALSIFYING_PAIR"] == s_new["FALSIFYING_PAIR"])),
        ]))
        print("    %-9s %-16s |t|/tcrit %.4f  rel %.5f  floor %.5f  "
              "FALSIF@0.15 %s  FALSIF@0.025 %s  SE2/SEn %.4f"
              % (t["cell"], t["target"], s_frozen["abs_t_over_t_crit"],
                 s_frozen["relative_difference"],
                 s_frozen["detection_floor_relative"],
                 s_frozen["FALSIFYING_PAIR"], s_new["FALSIFYING_PAIR"],
                 se2 / sen))
    RES["targets"] = rows

    # ------------------------------------------------------------- summaries
    n = len(rows)
    n_below_1 = sum(r["SE_RATIO_BELOW_1_DISCLOSED"] for r in rows)
    sugg_carried = [(r["cell"], r["target"]) for r in rows
                    if r["at_tau_rel_frozen_0.15"]["SUGGESTIVE_carried_band"]]
    sugg_widened = [(r["cell"], r["target"]) for r in rows
                    if r["at_tau_rel_frozen_0.15"]["SUGGESTIVE_WIDENED_band_AM14d"]]
    floors = [r["at_tau_rel_frozen_0.15"]["detection_floor_relative"]
              for r in rows]
    n_floor_below_015 = sum(1 for f in floors if f < TAU_REL_FROZEN)
    n_floor_below_0025 = sum(1 for f in floors if f < TAU_REL_REBUILT_ROUNDED)
    max_repro_dev = max(r["reproduction_of_committed_scoring"]["max_rel_dev"]
                        for r in rows)

    RES["summary"] = {
        "n_targets": n,
        "reproduction_of_committed_scoring_max_relative_deviation": max_repro_dev,
        "reproduction_within_1e-12": bool(max_repro_dev < 1e-12),
        "n_FALSIFYING_at_tau_rel_0.15": sum(
            r["at_tau_rel_frozen_0.15"]["FALSIFYING_PAIR"] for r in rows),
        "n_FALSIFYING_at_tau_rel_0.025": sum(
            r["at_tau_rel_rederived_0.025"]["FALSIFYING_PAIR"] for r in rows),
        "n_verdicts_invariant_to_the_repair": sum(
            r["VERDICT_INVARIANT_TO_THE_REPAIR"] for r in rows),
        "n_SUGGESTIVE_carried_band": len(sugg_carried),
        "SUGGESTIVE_carried_band": sugg_carried,
        "n_SUGGESTIVE_WIDENED_band": len(sugg_widened),
        "SUGGESTIVE_WIDENED_band": sugg_widened,
        "n_admitted_ONLY_by_the_widened_band": len(
            [x for x in sugg_widened if x not in sugg_carried]),
        "admitted_ONLY_by_the_widened_band": [
            x for x in sugg_widened if x not in sugg_carried],
        "n_targets_with_floor_below_tau_rel_0.15": n_floor_below_015,
        "n_targets_with_floor_below_tau_rel_0.025": n_floor_below_0025,
        "n_SE_ratio_below_1": n_below_1,
        "SE_2way_over_SE_naive_range": [min(r["SE_2way_over_SE_naive"]
                                            for r in rows),
                                        max(r["SE_2way_over_SE_naive"]
                                            for r in rows)],
        "detection_floor_carried_with_its_qualifier": {
            "non_degenerate_tightest_pct": FLOOR_NONDEGENERATE_PCT,
            "family_level_bound_pct": FLOOR_FAMILY_PCT,
            "qualifier": FLOOR_DEGENERATE_QUALIFIER},
    }

    RES["predictions"] = {
        "P-C1a": {
            "statement": "lowering the floor from 0.15 to 0.025 moves at least "
                         "one target OUT of 'floor >= tau_rel' and into a "
                         "decidable state",
            "falsifier": "no target changes state",
            "n_with_floor_below_tau_rel_at_0.15": n_floor_below_015,
            "n_with_floor_below_tau_rel_at_0.025": n_floor_below_0025,
            "HOLDS": bool(n_floor_below_0025 > n_floor_below_015),
            "DIRECTION_NOTE": (
                "The prediction as written points the WRONG WAY and the "
                "arithmetic says so: LOWERING tau_rel can only make "
                "'floor >= tau_rel' MORE common, never less, since the floors "
                "are unchanged. The realized direction is reported above and "
                "the prediction is recorded as FALSIFIED rather than quietly "
                "reinterpreted."),
        },
        "P-C1b": {
            "statement": "at least one pair enters the WIDENED SUGGESTIVE band "
                         "that the carried band excluded",
            "falsifier": "the widened band admits nothing the carried band "
                         "did not",
            "n_admitted_only_by_widened": len(
                [x for x in sugg_widened if x not in sugg_carried]),
            "HOLDS": bool([x for x in sugg_widened if x not in sugg_carried]),
        },
        "P-C1c": {
            "statement": "at least one target has SE_2way/SE_naive < 1",
            "falsifier": "every target has ratio >= 1",
            "n_below_1": n_below_1,
            "HOLDS": bool(n_below_1 > 0),
        },
        "pre_registered_consequence_note": (
            "prereg 4.5 declared BEFORE this re-score that with a "
            "non-degenerate detection floor of ~10.8% relative and a "
            "re-derived floor of 2.5%, the floor is NO LONGER THE BINDING TERM "
            "-- the |t| clause is -- so this section CANNOT produce a "
            "falsification the carried scoring did not already produce, and "
            "can only change labels and expose near misses. That limit was "
            "declared in advance so it would not be discovered afterwards and "
            "reported as a result."),
    }

    RES["what_this_does_not_establish"] = [
        "It does NOT reinstate the frozen Section C label and does NOT "
        "establish its negation. Every statement here is about a CONDITION "
        "(floor versus tau_rel, |t| versus |t|crit) and never about that label.",
        "BATCH-a44d08 is not rescored in any respect; its Section C verdict and "
        "detection floors remain VOID IN BOTH DIRECTIONS.",
        "No new measurement was performed, so nothing here can strengthen or "
        "weaken any proposition about tail sufficiency in either direction.",
        "Claim tier TOY.",
    ]

    RES["git"] = {"revision": git("rev-parse", "HEAD"),
                  "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
                  "dirty": bool(git("status", "--porcelain"))}
    RES["environment"] = {
        "operating_system": platform.platform(),
        "architecture": platform.machine(), "host": socket.gethostname(),
        "python_version": platform.python_version(),
        "dependencies": {"numpy": np.__version__, "scipy": scipy.__version__}}
    RES["timings"] = {"total_seconds": time.time() - T_START}
    RES["resources"] = {
        "max_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        * (1024 if platform.system() == "Linux" else 1)}
    RES["validity"] = {"status": "VALID", "expected_runs": 1, "used_runs": 1}
    RES["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    with open(args.out, "w") as fh:
        json.dump(RES, fh, indent=1, default=float)
    print("\n[3] summary")
    for k in ("n_FALSIFYING_at_tau_rel_0.15", "n_FALSIFYING_at_tau_rel_0.025",
              "n_verdicts_invariant_to_the_repair", "n_SUGGESTIVE_carried_band",
              "n_SUGGESTIVE_WIDENED_band", "n_admitted_ONLY_by_the_widened_band",
              "n_targets_with_floor_below_tau_rel_0.15",
              "n_targets_with_floor_below_tau_rel_0.025", "n_SE_ratio_below_1",
              "reproduction_within_1e-12"):
        print("    %-46s %s" % (k, RES["summary"][k]))
    print("\nwrote %s   %.2f s" % (args.out, time.time() - T_START))
    return 0


if __name__ == "__main__":
    sys.exit(main())
