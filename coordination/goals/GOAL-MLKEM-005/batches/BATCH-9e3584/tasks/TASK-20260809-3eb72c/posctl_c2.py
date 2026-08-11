#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TASK-20260809-3eb72c / BATCH-9e3584 / GOAL-MLKEM-005
SECTION C2 of the notarized pre-registration -- AM-14 (b):
A POSITIVE CONTROL THAT ACTUALLY INJECTS.

  prereg  coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/
          TASK-20260809-4011dd/prereg.md
  sha256  190cf4740b0ecefdbe7d1da0868a6258352b044ae5e99da470060f94049c70ea
  notarized by TASK-20260809-91cf76 in commit
  1aa7db5313f6d3da1f366443d4d6066597393402

AM-14(b) exists because closed-form arithmetic IN THE SE THE CONTROL IS MEANT
TO VALIDATE cannot detect SE inflation and is therefore not a control.  So:

  * the declared offset is added to EVERY ENTRY of the committed raw S x E
    Delta table;
  * the ENTIRE scoring path is re-run FROM THAT TABLE -- two-way variance
    decomposition, SE(Delta_bar), Satterthwaite nu_eff, |t|, |t|crit, relative
    difference, and the FALSIFYING-PAIR verdict under both clauses;
  * NO CLOSED-FORM SHORTCUT IS USED ANYWHERE.

BATCH-a44d08 IS NOT RESCORED IN ANY RESPECT.
CLAIM TIER: TOY.  certificate.kind: none.

This script writes exactly one file: results_c2.json, in its own task directory.
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

ALPHA_PAIR = 0.10 / 11                     # [carried]
TAU_REL_FROZEN = 0.15                      # [carried]
TAU_REL_REBUILT = 0.025                    # prereg 4.1, derived by Section C1

# prereg 5.2, declared in advance, in units of the target's committed SE
DELTA_OVER_SE_LADDER = [0.0, 0.5, 1.0, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0]
SHOULD_NOT_CATCH = [0.5, 1.0]              # prereg 5.2
SHOULD_CATCH = [8.0, 12.0]                 # prereg 5.2, where |t|crit < 8
REPRO_TOL = 1e-12                          # prereg 5.3 / 6


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
                "negative_test_absent_at_parent": absent})
    out["ALL_FOUR_AGREE"] = (live == sidecar == PREREG_SHA256_EXPECTED == blob)
    if not out["ALL_FOUR_AGREE"]:
        raise SystemExit("ABORT: prereg sha256 mismatch %s" % json.dumps(out))
    if not absent:
        raise SystemExit("ABORT: frozen text present at the notarizing parent")
    return out


# ============ the FULL scoring path, re-run from the raw table every time
def se_decomposition(Delta):
    """CARRIED VERBATIM from BATCH-cbe023 measure_am7.py, degenerate branch
    included.  RE-RUN FROM THE TABLE on every call -- no shortcut."""
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
            "sigma2_support": (MS_S - MS_res) / E,
            "sigma2_pool": (MS_P - MS_res) / S,
            "sigma2_resid": MS_res,
            "var_Delta_bar": float(var), "SE_Delta_bar": float(np.sqrt(var)),
            "nu_eff": nu, "NEGATIVE_VARIANCE_COMPONENT": negflag,
            "Delta_bar": gm}


def full_score(Delta, M, tau_rel):
    """The ENTIRE path, from the raw S x E table to the verdict."""
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
            "NEGATIVE_VARIANCE_COMPONENT": dec["NEGATIVE_VARIANCE_COMPONENT"],
            "decomposition": dec}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    RES = OrderedDict()
    RES.update({"task_id": "TASK-20260809-3eb72c", "batch_id": "BATCH-9e3584",
                "goal_id": "GOAL-MLKEM-005", "role": "executor",
                "section": "C2 -- AM-14 (b)", "claim_tier": "toy"})
    RES["certificate"] = {"kind": "none",
                          "reason": "no discrete-log solve and no factor-base "
                                    "relation is claimed or produced"}
    RES["governed_by"] = {"prereg": PREREG_REL,
                          "sha256": PREREG_SHA256_EXPECTED,
                          "notarizing_commit": NOTARIZING_COMMIT}
    RES["what_this_is"] = (
        "A POSITIVE CONTROL ON THE SECTION C INSTRUMENT. The offset is added to "
        "the RAW S x E table and the whole scoring path is re-run from that "
        "table. It measures the instrument, not the proposition: nothing here "
        "bears on tail sufficiency in either direction.")

    print("=" * 78)
    print("SECTION C2 -- AM-14(b) INJECTING POSITIVE CONTROL")
    print("BATCH-9e3584 / TASK-20260809-3eb72c   CLAIM TIER: TOY")
    print("The offset goes into the RAW S x E table and the FULL path is re-run.")
    print("=" * 78)

    print("\n[0] prereg notarization gate -- ABORT ON MISMATCH")
    RES["prereg_verification"] = verify_prereg()
    print("    ALL FOUR AGREE: %s" % RES["prereg_verification"]["ALL_FOUR_AGREE"])

    src = json.load(open(COMMITTED_AM7))
    RES["source"] = {
        "path": ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/tasks/"
                 "TASK-20260808-3a5f18/results_am7.json"),
        "sha256": sha256_file(COMMITTED_AM7),
        "status": "COMMITTED INPUT, read only."}
    RES["frozen_constants"] = {
        "delta_over_SE_ladder": DELTA_OVER_SE_LADDER,
        "should_NOT_catch": SHOULD_NOT_CATCH,
        "should_catch_where_tcrit_below_8": SHOULD_CATCH,
        "alpha_pair": ALPHA_PAIR,
        "tau_rel_frozen": TAU_REL_FROZEN,
        "tau_rel_rebuilt": TAU_REL_REBUILT,
        "reproduction_tolerance_relative": REPRO_TOL,
        "S": 8, "E": 4}

    print("\n[1] inject and re-run, every target, every rung, both tau_rel")
    rows = []
    for t in src["targets"]:
        D0 = np.asarray(t["Delta_table_S_by_E"], dtype=float)
        M = max(abs(t["D_GR_mean"]), abs(t["D_TL_mean"]))
        committed = t["scoring"]
        se_committed = float(committed["SE_Delta_bar"])
        base = full_score(D0, M, TAU_REL_FROZEN)

        ladder = []
        for r in DELTA_OVER_SE_LADDER:
            delta_abs = r * se_committed
            Dinj = D0 + delta_abs                     # THE ACTUAL INJECTION
            s015 = full_score(Dinj, M, TAU_REL_FROZEN)
            s0025 = full_score(Dinj, M, TAU_REL_REBUILT)
            ladder.append(OrderedDict([
                ("delta_over_SE", r),
                ("delta_absolute_in_D_units", delta_abs),
                ("Delta_bar", s015["Delta_bar"]),
                ("SE_Delta_bar_RECOVERED", s015["SE_Delta_bar"]),
                ("SE_recovery_relative_deviation",
                 abs(s015["SE_Delta_bar"] - se_committed)
                 / max(abs(se_committed), 1e-300)),
                ("nu_eff", s015["nu_eff"]),
                ("t_crit", s015["t_crit"]),
                ("abs_t", s015["abs_t"]),
                ("relative_difference", s015["relative_difference"]),
                ("FALSIFYING_at_tau_rel_0.15", s015["FALSIFYING_PAIR"]),
                ("FALSIFYING_at_tau_rel_0.025", s0025["FALSIFYING_PAIR"]),
                ("condition_i_t", s015["condition_i_t"]),
                ("condition_ii_at_0.15", s015["condition_ii_relative"]),
                ("condition_ii_at_0.025", s0025["condition_ii_relative"]),
            ]))

        zero = ladder[0]
        repro = {
            "committed_Delta_bar": committed["Delta_bar"],
            "recovered_Delta_bar": zero["Delta_bar"],
            "committed_SE": se_committed,
            "recovered_SE": zero["SE_Delta_bar_RECOVERED"],
            "committed_nu_eff": committed["nu_eff"],
            "recovered_nu_eff": zero["nu_eff"],
            "committed_abs_t": committed["abs_t"],
            "recovered_abs_t": zero["abs_t"],
            "committed_FALSIFYING": committed["FALSIFYING_PAIR"],
            "recovered_FALSIFYING": zero["FALSIFYING_at_tau_rel_0.15"],
            "max_relative_deviation": max(
                abs(zero["Delta_bar"] - committed["Delta_bar"])
                / max(abs(committed["Delta_bar"]), 1e-300),
                abs(zero["SE_Delta_bar_RECOVERED"] - se_committed)
                / max(abs(se_committed), 1e-300),
                abs(zero["nu_eff"] - committed["nu_eff"])
                / max(abs(committed["nu_eff"]), 1e-300)),
        }
        repro["within_tolerance"] = bool(
            repro["max_relative_deviation"] < REPRO_TOL)

        ats = [x["abs_t"] for x in ladder if x["abs_t"] is not None]
        above = [x for x in ladder
                 if x["delta_over_SE"] * se_committed > abs(base["Delta_bar"])]
        mono = all(above[i]["abs_t"] <= above[i + 1]["abs_t"] + 1e-12
                   for i in range(len(above) - 1))
        max_se_dev = max(x["SE_recovery_relative_deviation"] for x in ladder)

        rows.append(OrderedDict([
            ("cell", t["cell"]), ("target", t["target"]),
            ("committed_SE_used_as_the_injection_unit", se_committed),
            ("M_denominator_max_abs_D", M),
            ("reproduction_at_delta_0", repro),
            ("ladder", ladder),
            ("abs_t_monotone_above_the_committed_Delta_bar", bool(mono)),
            ("max_SE_recovery_relative_deviation", max_se_dev),
            ("SE_INFLATION_DETECTED", bool(max_se_dev >= REPRO_TOL)),
            ("fires_at_delta_over_SE_le_1_at_0.15", bool(any(
                x["FALSIFYING_at_tau_rel_0.15"] for x in ladder
                if 0 < x["delta_over_SE"] <= 1.0))),
            ("fires_at_delta_over_SE_le_1_at_0.025", bool(any(
                x["FALSIFYING_at_tau_rel_0.025"] for x in ladder
                if 0 < x["delta_over_SE"] <= 1.0))),
            ("fires_at_delta_over_SE_12_at_0.15", bool(
                ladder[-1]["FALSIFYING_at_tau_rel_0.15"])),
            ("fires_at_delta_over_SE_12_at_0.025", bool(
                ladder[-1]["FALSIFYING_at_tau_rel_0.025"])),
            ("t_crit_below_8", bool(base["t_crit"] < 8.0)),
            ("t_crit", base["t_crit"]),
            ("NEGATIVE_VARIANCE_COMPONENT", base["NEGATIVE_VARIANCE_COMPONENT"]),
        ]))
        print("    %-9s %-16s tcrit %8.4f  SEdev %.2e  mono %s  "
              "fire@<=1SE %s  fire@12SE(0.15/0.025) %s/%s"
              % (t["cell"], t["target"], base["t_crit"], max_se_dev,
                 mono, rows[-1]["fires_at_delta_over_SE_le_1_at_0.15"],
                 rows[-1]["fires_at_delta_over_SE_12_at_0.15"],
                 rows[-1]["fires_at_delta_over_SE_12_at_0.025"]))
    RES["targets"] = rows

    n = len(rows)
    tcrit_lt8 = [r for r in rows if r["t_crit_below_8"]]
    RES["summary"] = {
        "n_targets": n,
        "n_reproducing_at_delta_0_within_1e-12": sum(
            r["reproduction_at_delta_0"]["within_tolerance"] for r in rows),
        "max_reproduction_relative_deviation": max(
            r["reproduction_at_delta_0"]["max_relative_deviation"]
            for r in rows),
        "n_abs_t_monotone": sum(
            r["abs_t_monotone_above_the_committed_Delta_bar"] for r in rows),
        "max_SE_recovery_relative_deviation_over_all_targets": max(
            r["max_SE_recovery_relative_deviation"] for r in rows),
        "n_targets_with_SE_INFLATION_DETECTED": sum(
            r["SE_INFLATION_DETECTED"] for r in rows),
        "n_firing_at_delta_over_SE_le_1_at_0.15": sum(
            r["fires_at_delta_over_SE_le_1_at_0.15"] for r in rows),
        "n_firing_at_delta_over_SE_le_1_at_0.025": sum(
            r["fires_at_delta_over_SE_le_1_at_0.025"] for r in rows),
        "n_targets_with_t_crit_below_8": len(tcrit_lt8),
        "n_of_those_firing_at_delta_over_SE_12_at_0.15": sum(
            r["fires_at_delta_over_SE_12_at_0.15"] for r in tcrit_lt8),
        "n_of_those_firing_at_delta_over_SE_12_at_0.025": sum(
            r["fires_at_delta_over_SE_12_at_0.025"] for r in tcrit_lt8),
        "targets_with_t_crit_at_or_above_8": [
            (r["cell"], r["target"], r["t_crit"]) for r in rows
            if not r["t_crit_below_8"]],
    }

    RES["predictions"] = {
        "P-C2a": {
            "statement": "at delta/SE = 0 every target reproduces its committed "
                         "Delta_bar, SE, nu_eff, |t| and verdict to 1e-12 "
                         "relative",
            "n_reproducing": RES["summary"]["n_reproducing_at_delta_0_within_1e-12"],
            "of": n,
            "HOLDS": bool(RES["summary"]["n_reproducing_at_delta_0_within_1e-12"]
                          == n)},
        "P-C2b": {
            "statement": "|t| is monotone non-decreasing in delta once delta "
                         "exceeds |Delta_bar_committed|",
            "n_monotone": RES["summary"]["n_abs_t_monotone"], "of": n,
            "HOLDS": bool(RES["summary"]["n_abs_t_monotone"] == n)},
        "P-C2c": {
            "statement": "NO target returns FALSIFYING at delta/SE <= 1.0",
            "n_firing_at_0.15":
                RES["summary"]["n_firing_at_delta_over_SE_le_1_at_0.15"],
            "n_firing_at_0.025":
                RES["summary"]["n_firing_at_delta_over_SE_le_1_at_0.025"],
            "HOLDS": bool(
                RES["summary"]["n_firing_at_delta_over_SE_le_1_at_0.15"] == 0
                and RES["summary"]["n_firing_at_delta_over_SE_le_1_at_0.025"]
                == 0),
            "consequence_if_falsified": "the instrument fires on nothing and is "
                                        "OVER-SENSITIVE; reported as a finding "
                                        "about the instrument"},
        "P-C2d": {
            "statement": "every target with |t|crit < 8 returns FALSIFYING at "
                         "delta/SE = 12 under the floor in use",
            "n_with_t_crit_below_8": RES["summary"]["n_targets_with_t_crit_below_8"],
            "n_firing_at_0.15":
                RES["summary"]["n_of_those_firing_at_delta_over_SE_12_at_0.15"],
            "n_firing_at_0.025":
                RES["summary"]["n_of_those_firing_at_delta_over_SE_12_at_0.025"],
            "HOLDS_at_0.15": bool(
                RES["summary"]["n_of_those_firing_at_delta_over_SE_12_at_0.15"]
                == RES["summary"]["n_targets_with_t_crit_below_8"]),
            "HOLDS_at_0.025": bool(
                RES["summary"]["n_of_those_firing_at_delta_over_SE_12_at_0.025"]
                == RES["summary"]["n_targets_with_t_crit_below_8"])},
        "P-C2e": {
            "statement": "the recovered SE at delta > 0 equals the committed SE "
                         "to 1e-12 relative at every target; a departure IS the "
                         "SE inflation AM-14(b) was written to detect",
            "max_SE_recovery_relative_deviation":
                RES["summary"]["max_SE_recovery_relative_deviation_over_all_targets"],
            "n_targets_with_inflation":
                RES["summary"]["n_targets_with_SE_INFLATION_DETECTED"],
            "HOLDS": bool(
                RES["summary"]["n_targets_with_SE_INFLATION_DETECTED"] == 0)},
        "detection_floor": {
            "value": 0.5, "units": "multiples of the target's committed SE",
            "note": "the ladder's bottom rung. Nothing below 0.5 SE is tested "
                    "and nothing below it is claimed."},
    }

    RES["could_not_fail_demonstration"] = {
        "could_not_FIRE": (
            "The injection is applied to Delta_bar AFTER the variance "
            "decomposition, so SE is unchanged by construction and inflation "
            "can never be detected. THIS IS THE EXACT DEFECT AM-14(b) NAMES. "
            "AVERTED: the offset is added to the RAW S x E table and "
            "se_decomposition() is re-run FROM THAT TABLE at every rung; the "
            "recovered SE is compared against the committed SE at every rung "
            "and the maximum deviation is reported (P-C2e)."),
        "could_not_PASS": (
            "The ladder starts so high that every rung fires, making 'detects "
            "the injection' vacuous. AVERTED: the ladder starts at 0.5 SE, "
            "BELOW every target's |t|crit, and P-C2c declares in advance that "
            "the bottom two rungs MUST NOT fire. The control has a live failure "
            "mode at both ends."),
    }
    RES["what_this_does_not_establish"] = [
        "This is a control ON THE INSTRUMENT. It says nothing about tail "
        "sufficiency in either direction, and it neither reinstates nor negates "
        "the frozen Section C label.",
        "BATCH-a44d08 is not rescored in any respect.",
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
    print("\n[2] predictions")
    for k, v in RES["predictions"].items():
        if k == "detection_floor":
            continue
        print("    %-7s %s" % (k, {kk: vv for kk, vv in v.items()
                                   if kk.startswith("HOLDS") or kk.startswith("n_")}))
    print("\nwrote %s   %.2f s" % (args.out, time.time() - T_START))
    return 0


if __name__ == "__main__":
    sys.exit(main())
