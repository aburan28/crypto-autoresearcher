#!/usr/bin/env python3
"""
TASK-20260808-cece0c / BATCH-cbe023 / GOAL-MLKEM-005
AM-6 -- SECTION B: the AM-3 positive control rebuilt, with `c_min` reported in
CLOSED FORM at ALL 12 STEPS of ALL 4 CELLS and the post-injection Delta printed
at every step.

Governed by, and NOT modified by, this file:
  coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/tasks/
      TASK-20260808-35efa3/prereg.md
  sha256 2da554914e5d78146c1e6cafcdbd109aacbc1a1624ed1f8e94ae769f757fc4f8
  notarized by TASK-20260808-e725b4 in commit
  4f7c63703d50445c758fc6216ca8d4436e04ae2a.

This script loads that file READ-ONLY, re-hashes it, compares against the
task-card constant hard-coded below, the producer sidecar, the notarized
receipt AND the blob inside the notarizing commit itself, asserts
`git merge-base --is-ancestor <notarizing commit> HEAD` against the NOTARIZING
COMMIT ITSELF (carried correction V-7, prereg 0.3), and ABORTS on any mismatch.

DEFECT D-2, recorded against the sibling task AM-7 and NOT repeated here: that
script's REPO_ROOT resolved five directory levels up, landing in the enclosing
checkout, so its ancestry assertion was made against the WRONG HEAD.  This file
resolves REPO_ROOT to four levels above `batches/` AND THEN VERIFIES IT: it
requires `git -C REPO_ROOT rev-parse --show-toplevel` to equal REPO_ROOT
exactly, and aborts otherwise.  The assertion is therefore made IN THIS
WORKTREE, and the resolved toplevel is printed and recorded in the JSON so a
reviewer can check which repository was asked.

CARRIED VERBATIM from BATCH-a44d08 / TASK-20260806-e17677 `measure_g3.py`
(which carried it from BATCH-f19c37 / BATCH-436ddd): the four cells, q = 3329,
CBD_{eta=2}, R = ||Q^T e||^2/||e||^2, the frozen empirical quantile estimator
q_emp(p) = sort(R)[round(p*N)-1] at N = 2^20, 8 draws per arm, GATE_K = 4.0,
SE_diff(A,t) = sqrt(sd_A^2/8 + sd_haar^2/8), every seed formula, the Haar null
arm, the 13-point AM-1 t grid (RETAINED, not re-litigated), the graded path
construction with (S_j, G_j) drawn ONCE per (d,beta,j) BEFORE and independently
of the t list, the chunked projection with chunk = 2^15 (the chunking IS part
of the RNG consumption order and must be reproduced to regenerate the committed
draws bitwise), and the AM-3 criterion of BATCH-a44d08 prereg 3.2.

CHANGED, and only as prereg.md Section B (3.2 - 3.8) freezes it:
  * THERE IS NO STEP SELECTION (prereg 3.3).  BATCH-a44d08's argmax-SE_diff
    rule is REMOVED, not replaced.  All 12 steps of all 4 cells are reported.
  * c_min(i) and c_pos(i) are reported IN CLOSED FORM at every step, with the
    post-injection Delta printed at every c of the frozen grid.
  * PRED-B1 is scored at a FIXED c = 6 as a COUNT of steps out of 12.
  * NC-B1 (c = 0), NC-B2 (c = -6) and NC-B3 (Delta_i > 0 flagging) are run.
  * the bootstrap of prereg 3.7 quantifies uncertainty on c_min and takes NO
    verdict.

NOT RUN, declared: NO NEW BKZ and NO LLL.  The graded and Haar arms are pure
numpy and THE SEEDS ARE THE CACHE.  The seed-cache reproduction is re-verified
BEFORE anything is scored and its max deviation is reported without rounding.

Observations only.  No status change, no evidence record, no interpretation
beyond the frozen outcomes of prereg 3.5.  Claim tier TOY: nothing here bears
on ML-KEM security, on any FIPS 203 parameter set, or on any attack cost.  This
script performs no git write, makes no commit, and writes exactly one file:
results_g3.json inside its own task directory.
"""

import argparse
import hashlib
import json
import os
import platform
import resource
import signal
import subprocess
import sys
import time

import numpy as np
from scipy.special import betaincinv
from scipy.stats import t as student_t

TASK_DIR = os.path.dirname(os.path.abspath(__file__))
TASKS_DIR = os.path.normpath(os.path.join(TASK_DIR, ".."))
BATCH_DIR = os.path.normpath(os.path.join(TASKS_DIR, ".."))
BATCHES_DIR = os.path.normpath(os.path.join(BATCH_DIR, ".."))
# batches -> GOAL-MLKEM-005 -> goals -> coordination -> <repo root>.  FOUR
# levels.  Five lands in the enclosing checkout: that is defect D-2.
REPO_ROOT = os.path.normpath(os.path.join(BATCHES_DIR, "..", "..", "..", ".."))

PREREG_REL = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/tasks/"
              "TASK-20260808-35efa3/prereg.md")
PREREG_PATH = os.path.join(TASKS_DIR, "TASK-20260808-35efa3", "prereg.md")
SIDECAR_PATH = os.path.join(TASKS_DIR, "TASK-20260808-35efa3",
                            "prereg_sha256.txt")
RECEIPT_PATH = os.path.join(BATCH_DIR, "archives", "TASK-20260808-e725b4",
                            "snapshot-receipt.json")

# The two constants the task card asserts.  Hard-coded so that a tampered
# sidecar or receipt cannot make the check pass.
EXPECTED_PREREG_SHA256 = \
    "2da554914e5d78146c1e6cafcdbd109aacbc1a1624ed1f8e94ae769f757fc4f8"
NOTARIZING_COMMIT = "4f7c63703d50445c758fc6216ca8d4436e04ae2a"

# The committed BATCH-a44d08 Section B record, against which the seed-cache
# reproduction of prereg 3.5 is scored (448 per-draw r values).
PRIOR_A44 = os.path.join(BATCHES_DIR, "BATCH-a44d08", "tasks",
                         "TASK-20260806-e17677", "results_g3.json")
# The BATCH-f19c37 record, which is where the declared 2.220446049250313e-16
# one-ULP d = 140 deviation was measured.  Reported additionally, as a second
# reproduction leg, so the declared expectation is checkable at its own source.
PRIOR_F19 = os.path.join(BATCHES_DIR, "BATCH-f19c37", "tasks",
                         "TASK-20260806-ca4377", "results.json")

# ------------------------------------------------- carried constants [carried]
Q_MOD = 3329
P_TAIL_10 = 2.0 ** -10
CELLS = [(100, 30), (100, 40), (140, 30), (140, 40)]
GATE_K = 4.0
N_DRAW = 8
N_ERR = 1 << 20
CHUNK = 1 << 15

# ------------------------------- the AM-1 grid, RETAINED, prereg 1 / 3, VERBATIM
GRADED_T = [0.0, 0.0025, 0.005, 0.0075, 0.01, 0.015, 0.02, 0.03,
            0.05, 0.1, 0.25, 0.5, 1.0]

# ------------------------ the AM-3 gate, CARRIED UNCHANGED (prereg 3.1, 6 / B)
AM3_EPSILON_K = 1.0                       # epsilon_i = 1.0 * SE_diff(A, t_i)
AM3_T_CRIT = 4.2071245566046755           # t_{7,0.998}   [closed form]
AM3_ALPHA_PER_STEP = 0.002                # P(t_7 > t_crit)
AM3_FAMILY_STEPS = 12
AM3_FAMILY_CELLS = 4
AM3_FAMILY_SIZE = AM3_FAMILY_STEPS * AM3_FAMILY_CELLS          # = 48
AM3_DECLARED_FWER = 0.096                 # union bound 48 x 0.002
AM3_SIDAK_REFERENCE = 0.0916233087376801  # reported for comparison ONLY

# ------------------------------------------- Section B's own frozen constants
C_GRID = [0, 1, 2, 3, 4, 6, 8, 12, 16, 24, 32]      # prereg 3.4 / 6
C_NEG_CONTROL = -6                                  # NC-B2, prereg 3.6
PRED_B1_C = 6                                       # prereg 3.5, fixed c
PRED_B1_THRESHOLD = 4                               # n_fire >= 4 of 12, EVERY cell
BOOTSTRAP_B = 20000                                 # prereg 3.7
BOOTSTRAP_TAG = 9                                   # seed TAG table, prereg 6
REPRO_R_TOL = 1e-9                                  # prereg 3.5 admissibility
REPRO_CMIN_TOL = 0.01                               # prereg 3.5 admissibility
S1_STEPS = list(range(5, 12))                       # prereg 3.3 S1: t_i >= 0.015
S2_FLATNESS_K = 1.0                                 # prereg 3.3 S2

# Quoted priors.  REVIEW MEASUREMENTS.  Cited only as the ground for AM-6 and
# as the prior that set PRED-B1's threshold; NEVER as a rescoring of
# BATCH-a44d08 (prereg 3.1 item 3, AM-6 prohibition).
QUOTED_REVIEW_PRIORS = {
    "red_team_report.md section 2.2 -- identical injection fires at c <= 6 at":
        [6, 7, 9, 7],
    "red_team_report.md section 2.2 -- plateau medians":
        [3.98, 2.72, 3.76, 4.17],
    "red_team_report.md section 2.2 -- bootstrap P(INADMISSIBLE) under the "
    "argmax rule": 0.997,
    "validation_report.yaml item d -- post-injection Delta at c = 6 was still "
    "NEGATIVE in three of four cells under the argmax rule": True,
    "validation_report.yaml MR-B1 -- committed max AM-3 statistic":
        -0.19342160540508713,
    "validation_report.yaml MR-B1 -- committed n steps with Delta_i > 0": 9,
    "status": ("REVIEW MEASUREMENTS. Quoted as the ground for AM-6 and as the "
               "prior for PRED-B1 only. Not rescored, not reproduced as a "
               "baseline, and not evidence of this run."),
}

NC_B1_COMMITTED_MAX_STAT = -0.19342160540508713   # prereg 3.6 NC-B1 [quoted]
NC_B3_COMMITTED_N_INCREASING = 9                  # prereg 3.6 NC-B3 [quoted]

GATE_NOMINAL_DISCLOSURE = (
    "4.0 is a NOMINAL FACTOR, NOT a p-value. Its realized one-sided "
    "false-positive rate was measured at 0.0015-0.0025 against a nominal 3e-5 "
    "[quoted: BATCH-f19c37 validation_report.yaml item 4 / V-5]. prereg 1 "
    "requires every report citing the gate to state this.")


def tkey(t):
    return f"{t:.4f}"


def arm_t(t):
    return f"graded_t{tkey(t)}"


# ====================================================================== seeds
def seed_error(d):
    return 20260805 + d


def seed_haar(d, beta, j):
    return 900000 + d * 1000 + beta * 10 + j


def seed_graded(d, beta, j):
    return 500000 + d * 1000 + beta * 10 + j


# ================================================================= error law
_POPCNT4 = np.array([bin(v).count("1") for v in range(16)], dtype=np.int8)


def cbd_eta2(rng, n, d):
    r = rng.integers(0, 16, size=(n, d), dtype=np.uint8)
    return (_POPCNT4[r & 3] - _POPCNT4[r >> 2]).astype(np.int8)


def make_errors(d, n_err=N_ERR, chunk=CHUNK):
    """Carried byte-for-byte, INCLUDING the chunk size: the chunking IS part of
    the RNG consumption order, so reproducing the committed draws requires the
    same chunk."""
    rng = np.random.default_rng(seed_error(d))
    Ef = np.empty((n_err, d), dtype=np.float32)
    n2 = np.empty(n_err, dtype=np.float64)
    hist = np.zeros(5, dtype=np.int64)
    for s0 in range(0, n_err, chunk):
        s1 = min(n_err, s0 + chunk)
        Ei = cbd_eta2(rng, s1 - s0, d)
        hist += np.bincount((Ei.astype(np.int32) + 2).ravel(), minlength=5)
        n2[s0:s1] = (Ei.astype(np.int32) ** 2).sum(1)
        Ef[s0:s1] = Ei
    pm = hist / hist.sum()
    check = {
        "measured_pmf": pm.tolist(),
        "exact_fips203_cbd_eta2": [1 / 16, 4 / 16, 6 / 16, 4 / 16, 1 / 16],
        "measured_per_coordinate_variance":
            float(sum(pm[i] * (i - 2) ** 2 for i in range(5))),
        "measured_per_coordinate_fourth_moment":
            float(sum(pm[i] * (i - 2) ** 4 for i in range(5))),
        "exact_per_coordinate_variance": 1.0,
        "exact_per_coordinate_fourth_moment": 2.5,
    }
    return Ef, n2, check


# ================================================================ frames
def haar_frames(d, beta, n_draw=N_DRAW):
    cols = []
    for j in range(n_draw):
        g = np.random.default_rng(seed_haar(d, beta, j))
        cols.append(np.linalg.qr(g.standard_normal((d, beta)))[0]
                    .astype(np.float32))
    return np.concatenate(cols, axis=1)


def graded_paths(d, beta, n_draw=N_DRAW):
    """(S_j, G_j) drawn ONCE from seed_graded(d,beta,j), BEFORE and
    INDEPENDENTLY of the t list, and reused across every t, so the family is a
    path (prereg 1). Carried verbatim."""
    paths = []
    for j in range(n_draw):
        g = np.random.default_rng(seed_graded(d, beta, j))
        S = g.choice(d, size=beta, replace=False)
        G = g.standard_normal((d, beta))
        E = np.zeros((d, beta))
        E[S, np.arange(beta)] = 1.0
        paths.append((E, G))
    return paths


def graded_frames_from_paths(paths, t):
    cols = []
    for (E, G) in paths:
        Mx = np.sqrt(1.0 - t) * E + np.sqrt(t) * G
        cols.append(np.linalg.qr(Mx)[0].astype(np.float32))
    return np.concatenate(cols, axis=1)


def frame_V(Qstack, d, beta, n_draw=N_DRAW):
    """V = sum_a P_aa^2 - beta^2/d, deterministic, ZERO error draws. Carried."""
    per = []
    for j in range(n_draw):
        Q = Qstack[:, j * beta:(j + 1) * beta].astype(np.float64)
        pdiag = np.einsum("ij,ij->i", Q, Q)
        per.append(float((pdiag ** 2).sum() - beta * beta / d))
    arr = np.array(per)
    return {"per_draw": per, "mean": float(arr.mean()),
            "sd": float(arr.std(ddof=1)),
            "E_V_haar_exact": 2.0 * beta * (d - beta) / (d * (d + 2.0)),
            "n_error_draws_used": 0}


# ================================================================ projection
def project(Ef, n2, Q, beta, n_draw=N_DRAW, chunk=CHUNK):
    N = Ef.shape[0]
    R = np.empty((N, n_draw), dtype=np.float32)
    for s0 in range(0, N, chunk):
        s1 = min(N, s0 + chunk)
        S = Ef[s0:s1] @ Q
        S *= S
        R[s0:s1] = S.reshape(s1 - s0, n_draw, beta).sum(axis=2) / n2[s0:s1, None]
        del S
    return R


def emp_quantile(sorted_R, p):
    n = sorted_R.shape[0]
    k = max(1, min(n, int(round(p * n))))
    return float(sorted_R[k - 1]), k


def arm_r_values(R, qb10):
    """The ONLY arm statistic Section B needs: the per-draw
    r = q_emp(2^-10) / q_Beta(2^-10). Carried estimator, verbatim."""
    vals, ks = [], []
    for j in range(R.shape[1]):
        col = np.sort(R[:, j].astype(np.float64))
        q, k = emp_quantile(col, P_TAIL_10)
        vals.append(q / qb10)
        ks.append(k)
    a = np.array(vals, dtype=np.float64)
    return {"values": a.tolist(), "mean": float(a.mean()),
            "sd": float(a.std(ddof=1)), "order_stat_k": ks[0]}


def se_of_difference(arm_sd, haar_sd, n=N_DRAW):
    """SE_diff(A,t) = sqrt(sd_A^2/n + sd_haar^2/n). Carried verbatim."""
    return float(np.sqrt(arm_sd * arm_sd / n + haar_sd * haar_sd / n))


# ================================ SECTION B: the closed forms of prereg 3.2
def closed_form_step(i, t_values, means, values, se_diff):
    """prereg 3.2, implemented exactly as written and not otherwise.

      Delta_i    = m(t_{i+1}) - m(t_i)
      SE_step(i) = sd_j( r_j(t_{i+1}) - r_j(t_i) ) / sqrt(8)   [ddof=1, paired]
      epsilon_i  = 1.0 * SE_diff(A, t_i)

      Injecting + c * SE_diff(A, t_i) into every draw at grid point t_{i+1}
      shifts the paired difference at step i by a CONSTANT, hence shifts
      Delta_i by + c*SE_diff(t_i) and leaves SE_step(i), SE_diff(t_i) and
      epsilon_i unchanged.  Therefore

        stat_i(c) = ( Delta_i + (c - 1) * SE_diff(t_i) ) / SE_step(i)
        c_min(i)  = 1 + ( t_crit * SE_step(i) - Delta_i ) / SE_diff(t_i)
        c_pos(i)  = max( 0 , - Delta_i / SE_diff(t_i) )

      Frozen degenerate handling (prereg 3.2): if SE_diff(t_i) == 0 use
      SE_diff(t_{i+1}); if both are 0, or if SE_step(i) == 0, the step is
      flagged DEGENERATE, c_min and c_pos are `undefined` with the reason, and
      the step is excluded from the counts with the exclusion printed.  NO
      DIVISION BY ZERO IS PERFORMED.
    """
    delta = float(means[i + 1] - means[i])
    v0 = np.array(values[i], dtype=np.float64)
    v1 = np.array(values[i + 1], dtype=np.float64)
    se_step = float((v1 - v0).std(ddof=1) / np.sqrt(N_DRAW))

    eps_src = "SE_diff(A, t_i)"
    eps_base = se_diff[i]
    if eps_base == 0.0:
        eps_base = se_diff[i + 1]
        eps_src = "SE_diff(A, t_{i+1})  [t_i endpoint degenerate]"
    epsilon = AM3_EPSILON_K * eps_base

    degenerate = bool(eps_base == 0.0 or se_step == 0.0)

    row = {
        "i": i,
        "t_lo": t_values[i], "t_hi": t_values[i + 1],
        "m_t_lo": float(means[i]), "m_t_hi": float(means[i + 1]),
        "delta": delta,
        "se_step_paired": se_step,
        "se_diff_at_t_lo": se_diff[i],
        "se_diff_at_t_hi": se_diff[i + 1],
        "injection_unit_se_diff": eps_base,
        "epsilon": epsilon,
        "epsilon_source": eps_src,
        "t_crit": AM3_T_CRIT,
        "degenerate": degenerate,
        "degenerate_reason": None,
        "flag_delta_gt_0_in_raw_data": bool(delta > 0.0),
        "flag_near_flat_S2": None,
    }

    if degenerate:
        row["degenerate_reason"] = (
            "SE_diff(t_i) and SE_diff(t_{i+1}) both 0" if eps_base == 0.0
            else "SE_step(i) == 0")
        row["c_pos"] = None
        row["c_min"] = None
        row["c_min_over_4"] = None
        row["c_min_gt_c_pos"] = None
        row["post_injection_delta"] = {str(c): None for c in C_GRID}
        row["fires"] = {str(c): None for c in C_GRID}
        row["am3_statistic"] = {str(c): None for c in C_GRID}
        row["excluded_from_counts"] = True
        return row

    c_min = 1.0 + (AM3_T_CRIT * se_step - delta) / eps_base
    c_pos = max(0.0, -delta / eps_base)

    row["c_pos"] = c_pos
    row["c_min"] = c_min
    # c_min in units of the design's OWN 4.0 * SE_diff gate width (prereg 3.4)
    row["c_min_over_4"] = c_min / GATE_K
    row["c_min_gt_c_pos"] = bool(c_min > c_pos)
    row["c_min_minus_c_pos"] = c_min - c_pos
    row["post_injection_delta_at_c_min"] = delta + c_min * eps_base
    row["post_injection_delta_at_c_min_identity_check"] = \
        epsilon + AM3_T_CRIT * se_step
    row["flag_near_flat_S2"] = bool(abs(delta) <= S2_FLATNESS_K * eps_base)
    row["excluded_from_counts"] = False

    pid, fires, stats = {}, {}, {}
    for c in C_GRID:
        d_c = delta + c * eps_base
        s_c = (delta + (c - 1.0) * eps_base) / se_step
        pid[str(c)] = d_c
        stats[str(c)] = s_c
        fires[str(c)] = bool(s_c > AM3_T_CRIT)
    row["post_injection_delta"] = pid
    row["am3_statistic"] = stats
    row["fires"] = fires
    # NC-B2: the negative injection, at c = -6
    row["post_injection_delta_at_c_neg6"] = delta + C_NEG_CONTROL * eps_base
    row["am3_statistic_at_c_neg6"] = \
        (delta + (C_NEG_CONTROL - 1.0) * eps_base) / se_step
    row["fires_at_c_neg6"] = bool(row["am3_statistic_at_c_neg6"] > AM3_T_CRIT)
    return row


def score_cell(t_values, means, values, se_diff):
    steps = [closed_form_step(i, t_values, means, values, se_diff)
             for i in range(len(means) - 1)]
    live = [s for s in steps if not s["degenerate"]]
    inc = [s for s in live if s["flag_delta_gt_0_in_raw_data"]]
    not_inc = [s for s in live if not s["flag_delta_gt_0_in_raw_data"]]

    n_fire, n_fire_excl_inc = {}, {}
    for c in C_GRID:
        n_fire[str(c)] = int(sum(1 for s in live if s["c_min"] <= c))
        n_fire_excl_inc[str(c)] = int(sum(1 for s in not_inc if s["c_min"] <= c))

    # cross-check: the count from the frozen definition #{i : c_min(i) <= c}
    # against the count from the statistic itself, stat_i(c) > t_crit.
    n_fire_by_stat = {str(c): int(sum(1 for s in live if s["fires"][str(c)]))
                      for c in C_GRID}

    cmins = [s["c_min"] for s in live]
    s1 = [s["c_min"] for s in live if s["i"] in S1_STEPS]
    s2 = [s["c_min"] for s in live if s["flag_near_flat_S2"]]

    return {
        "steps": steps,
        "n_steps": len(steps),
        "n_degenerate": len(steps) - len(live),
        "degenerate_step_indices": [s["i"] for s in steps if s["degenerate"]],
        "n_steps_with_delta_gt_0": len(inc),
        "increasing_step_indices": [s["i"] for s in inc],
        "n_fire": n_fire,
        "n_fire_excluding_already_increasing_steps": n_fire_excl_inc,
        "n_fire_recomputed_from_statistic": n_fire_by_stat,
        "n_fire_definitions_agree": bool(n_fire == n_fire_by_stat),
        "c_min_min": min(cmins) if cmins else None,
        "c_min_median": float(np.median(cmins)) if cmins else None,
        "c_min_max": max(cmins) if cmins else None,
        "c_min_gt_c_pos_all_steps": bool(all(s["c_min_gt_c_pos"] for s in live)),
        "S1_grid_position_summary_DATA_INDEPENDENT": {
            "definition": ("median and range of c_min(i) over steps i in "
                           "{5,...,11}, i.e. lower endpoint t_i >= 0.015. The "
                           "selection uses ONLY the position in the frozen t "
                           "grid and no measured quantity whatsoever."),
            "step_indices": S1_STEPS,
            "n": len(s1),
            "median": float(np.median(s1)) if s1 else None,
            "min": min(s1) if s1 else None,
            "max": max(s1) if s1 else None,
        },
        "S2_near_flat_summary_DATA_DEPENDENT": {
            "definition": ("median and range of c_min(i) over steps with "
                           "|Delta_i| <= 1.0 * SE_diff(t_i). USES THE DATA. "
                           "Reported as DESCRIPTIVE, never as the frozen "
                           "headline."),
            "step_indices": [s["i"] for s in live if s["flag_near_flat_S2"]],
            "n": len(s2),
            "median": float(np.median(s2)) if s2 else None,
            "min": min(s2) if s2 else None,
            "max": max(s2) if s2 else None,
        },
    }


# ================================================== bootstrap (prereg 3.7, UQ)
def bootstrap_cmin(d, beta, values, haar_values, B=BOOTSTRAP_B):
    """prereg 3.7. Resample the 8 DRAW INDICES JOINTLY across every t and the
    Haar null, B = 20000, default_rng([9, d, beta, 0]); report per step the
    fraction of replicates with c_min(i) <= 6 and the 2.5/50/97.5 percentiles
    of c_min(i).

    THIS IS UNCERTAINTY QUANTIFICATION ON A REPORTED QUANTITY. It is NOT a
    selection rule and NO verdict is taken from it. The frozen headline
    (PRED-B1) is scored on the point estimates of the full 48-step table."""
    rng = np.random.default_rng([BOOTSTRAP_TAG, d, beta, 0])
    V = np.asarray(values, dtype=np.float64)          # (13, 8)
    h = np.asarray(haar_values, dtype=np.float64)     # (8,)
    idx = rng.integers(0, N_DRAW, size=(B, N_DRAW))   # joint across every arm

    vb = V[:, idx]                                    # (13, B, 8)
    hb = h[idx]                                       # (B, 8)
    means_b = vb.mean(axis=2)                         # (13, B)
    sds_b = vb.std(axis=2, ddof=1)                    # (13, B)
    hs_b = hb.std(axis=1, ddof=1)                     # (B,)
    se_diff_b = np.sqrt(sds_b ** 2 / N_DRAW + hs_b[None, :] ** 2 / N_DRAW)

    delta_b = means_b[1:] - means_b[:-1]              # (12, B)
    dif = vb[1:] - vb[:-1]                            # (12, B, 8)
    se_step_b = dif.std(axis=2, ddof=1) / np.sqrt(N_DRAW)
    base_b = se_diff_b[:-1]                           # SE_diff at t_i, (12, B)

    ok = (base_b > 0) & (se_step_b > 0)
    with np.errstate(divide="ignore", invalid="ignore"):
        c_min_b = 1.0 + (AM3_T_CRIT * se_step_b - delta_b) / base_b
    c_min_b = np.where(ok, c_min_b, np.nan)

    out = []
    for i in range(c_min_b.shape[0]):
        col = c_min_b[i]
        good = col[np.isfinite(col)]
        n_good = int(good.size)
        out.append({
            "i": i,
            "B": int(B),
            "n_finite_replicates": n_good,
            "n_degenerate_replicates": int(B - n_good),
            "fraction_c_min_le_6": (float(np.mean(good <= PRED_B1_C))
                                    if n_good else None),
            "p2.5": float(np.percentile(good, 2.5)) if n_good else None,
            "p50": float(np.percentile(good, 50.0)) if n_good else None,
            "p97.5": float(np.percentile(good, 97.5)) if n_good else None,
        })
    return {
        "status": ("UNCERTAINTY QUANTIFICATION ONLY (prereg 3.7). NOT a "
                   "selection rule. NO verdict is taken from it. PRED-B1 is "
                   "scored on the point estimates of the full 48-step table. "
                   "Repeating the bootstrap while keeping a selection would "
                   "repeat exactly the defect BATCH-a44d08's argmax lottery "
                   "carried."),
        "rng": f"numpy.random.default_rng([{BOOTSTRAP_TAG}, {d}, {beta}, 0])",
        "resample": "the 8 DRAW INDICES, JOINTLY across every t and the Haar null",
        "per_step": out,
    }


# ====================================================== reproduction (prereg 3.5)
def _committed_cell_arm_values(cell_obj, name):
    if name == "haar_null":
        return cell_obj["haar_null"]["r_values"]
    return cell_obj["per_t"][name.replace("graded_t", "")]["r_values"]


def repro_vs_committed_g3(measured):
    """prereg 3.5: report max |r_regenerated - r_committed| against the
    committed results_g3.json over all 448 values (4 cells x 14 arms x 8
    draws). Pure comparison of recorded numbers: NO lattice, NO reduction,
    NO BKZ, NO LLL."""
    if not os.path.exists(PRIOR_A44):
        return {"status": f"NOT EVALUATED -- {PRIOR_A44} not found",
                "classification": ("infrastructure signal, never negative "
                                   "mathematical evidence (AGENTS.md rule 3)")}
    pj = json.load(open(PRIOR_A44))
    rows, devs, devs_by_d = [], [], {}
    for (d, beta) in CELLS:
        key = f"d{d}_b{beta}"
        if key not in pj.get("cells", {}):
            continue
        cell = pj["cells"][key]
        arms = ["haar_null"] + [arm_t(t) for t in GRADED_T]
        for nm in arms:
            ov = _committed_cell_arm_values(cell, nm)
            nv = measured[key][nm]["values"]
            dd = [abs(a - b) for a, b in zip(nv, ov)]
            devs.extend(dd)
            devs_by_d.setdefault(d, []).extend(dd)
            rows.append({"cell": key, "arm": nm, "n_values": len(dd),
                         "max_abs_dev": max(dd),
                         "bitwise_identical": max(dd) == 0.0})
    return {
        "source": ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-a44d08/"
                   "tasks/TASK-20260806-e17677/results_g3.json"),
        "what": ("every per-draw r = q_emp(2^-10)/q_Beta(2^-10) value of the "
                 "13 graded arms and the Haar null arm, in all four cells "
                 "(4 x 14 x 8 = 448 values), regenerated from the carried "
                 "seeds with NO NEW BKZ and NO LLL"),
        "n_values_compared": len(devs),
        "max_abs_deviation": max(devs) if devs else None,
        "max_abs_deviation_by_d": {str(k): max(v) for k, v in devs_by_d.items()},
        "all_bitwise_identical": bool(devs and max(devs) == 0.0),
        "per_arm": rows,
    }


def repro_vs_f19c37(measured):
    """The SECOND reproduction leg, at the source where the declared non-zero
    deviation was measured. prereg 3.5 declares in advance: BATCH-a44d08
    measured 2.220446049250313e-16, confined to d = 140, uniform at one ULP,
    traced to a one-ULP difference in the deterministic reference divisor
    betaincinv(beta/2,(d-beta)/2,2^-10) under scipy 1.15.3. IT MUST NOT BE
    ROUNDED TO 0.0."""
    if not os.path.exists(PRIOR_F19):
        return {"status": f"NOT EVALUATED -- {PRIOR_F19} not found",
                "classification": ("infrastructure signal, never negative "
                                   "mathematical evidence (AGENTS.md rule 3)")}
    pj = json.load(open(PRIOR_F19))
    rows, devs, devs_by_d = [], [], {}
    for (d, beta) in CELLS:
        key = f"d{d}_b{beta}"
        if key not in pj.get("cells", {}):
            continue
        old_cell = pj["cells"][key]
        old_haar = old_cell["arms_cbd"]["haar_null"][
            "ratio_p2em10_over_draws"]["values"]
        new_haar = measured[key]["haar_null"]["values"]
        dh = [abs(a - b) for a, b in zip(new_haar, old_haar)]
        devs.extend(dh)
        devs_by_d.setdefault(d, []).extend(dh)
        rows.append({"cell": key, "arm": "haar_null", "n_values": len(dh),
                     "max_abs_dev": max(dh), "bitwise_identical": max(dh) == 0.0})
        old_pt = old_cell["sensitivity_demonstration"]["per_t"]
        for t in GRADED_T:
            ov = old_pt[tkey(t)]["ratio_2em10_values"]
            nv = measured[key][arm_t(t)]["values"]
            dd = [abs(a - b) for a, b in zip(nv, ov)]
            devs.extend(dd)
            devs_by_d.setdefault(d, []).extend(dd)
            rows.append({"cell": key, "arm": arm_t(t), "n_values": len(dd),
                         "max_abs_dev": max(dd),
                         "bitwise_identical": max(dd) == 0.0})
    return {
        "source": ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-f19c37/"
                   "tasks/TASK-20260806-ca4377/results.json"),
        "what": "the same 448 per-draw r values against the earlier record",
        "n_values_compared": len(devs),
        "max_abs_deviation": max(devs) if devs else None,
        "max_abs_deviation_by_d": {str(k): max(v) for k, v in devs_by_d.items()},
        "all_bitwise_identical": bool(devs and max(devs) == 0.0),
        "declared_in_advance_by_prereg_3_5": {
            "value": 2.220446049250313e-16,
            "confined_to": "d = 140",
            "cause": ("a one-ULP difference in the deterministic reference "
                      "divisor betaincinv(beta/2,(d-beta)/2,2^-10) under "
                      "scipy 1.15.3"),
            "must_not_be_rounded_to_zero": True,
        },
        "per_arm": rows,
    }


def repro_cmin_vs_committed(cells_scored):
    """prereg 3.5's second admissibility clause:
    max |c_min(regenerated) - c_min(committed)| <= 0.01 in c units.

    c_min was NOT computed by BATCH-a44d08 (Section B introduces it), so
    c_min(committed) is evaluated HERE from the committed record's own frozen
    per-step quantities via the identical closed form. Two independent legs:
      (a) from the committed AM3.steps fields delta / se_step_paired /
          se_diff_at_t_lo -- the actual committed numbers;
      (b) recomputed from the committed per-draw r_values, which re-derives
          delta / SE_step / SE_diff from the raw committed draws.
    """
    out = {
        "definition": ("c_min(committed) is evaluated from the COMMITTED "
                       "record via the identical closed form of prereg 3.2. "
                       "BATCH-a44d08 did not compute c_min; this is not a "
                       "rescoring of its verdict, which stands untouched."),
        "tolerance_c_units": REPRO_CMIN_TOL,
    }
    if not os.path.exists(PRIOR_A44):
        out["status"] = f"NOT EVALUATED -- {PRIOR_A44} not found"
        return out
    pj = json.load(open(PRIOR_A44))
    leg_a, leg_b = [], []
    for (d, beta) in CELLS:
        key = f"d{d}_b{beta}"
        if key not in pj.get("cells", {}):
            continue
        old_steps = pj["cells"][key]["AM3"]["steps"]
        new_steps = cells_scored[key]["steps"]

        # leg (a): from the committed AM3 step fields
        for os_, ns in zip(old_steps, new_steps):
            base = os_["se_diff_at_t_lo"]
            if base == 0.0:
                base = os_["se_diff_at_t_hi"]
            if base == 0.0 or os_["se_step_paired"] == 0.0:
                continue
            cm_old = 1.0 + (AM3_T_CRIT * os_["se_step_paired"]
                            - os_["delta"]) / base
            if ns["c_min"] is None:
                continue
            leg_a.append({"cell": key, "i": os_["i"],
                          "c_min_committed": cm_old,
                          "c_min_this_run": ns["c_min"],
                          "abs_dev": abs(cm_old - ns["c_min"])})

        # leg (b): recomputed from the committed per-draw r values
        cell = pj["cells"][key]
        hv = np.array(cell["haar_null"]["r_values"], dtype=np.float64)
        hs = float(hv.std(ddof=1))
        vals = [np.array(cell["per_t"][tkey(t)]["r_values"], dtype=np.float64)
                for t in GRADED_T]
        means = [float(v.mean()) for v in vals]
        sedf = [se_of_difference(float(v.std(ddof=1)), hs) for v in vals]
        for i in range(len(GRADED_T) - 1):
            base = sedf[i] if sedf[i] != 0.0 else sedf[i + 1]
            ss = float((vals[i + 1] - vals[i]).std(ddof=1) / np.sqrt(N_DRAW))
            if base == 0.0 or ss == 0.0:
                continue
            cm_old = 1.0 + (AM3_T_CRIT * ss - (means[i + 1] - means[i])) / base
            ns = new_steps[i]
            if ns["c_min"] is None:
                continue
            leg_b.append({"cell": key, "i": i,
                          "c_min_committed_recomputed": cm_old,
                          "c_min_this_run": ns["c_min"],
                          "abs_dev": abs(cm_old - ns["c_min"])})

    out["leg_a_from_committed_AM3_step_fields"] = {
        "n_compared": len(leg_a),
        "max_abs_dev_c_units": max((r["abs_dev"] for r in leg_a), default=None),
        "rows": leg_a,
    }
    out["leg_b_recomputed_from_committed_per_draw_r_values"] = {
        "n_compared": len(leg_b),
        "max_abs_dev_c_units": max((r["abs_dev"] for r in leg_b), default=None),
        "rows": leg_b,
    }
    devs = [out["leg_a_from_committed_AM3_step_fields"]["max_abs_dev_c_units"],
            out["leg_b_recomputed_from_committed_per_draw_r_values"]
            ["max_abs_dev_c_units"]]
    devs = [x for x in devs if x is not None]
    out["max_abs_dev_c_units"] = max(devs) if devs else None
    return out


# ================= implementation check of the closed forms (NOT a result)
def closed_form_implementation_check():
    """A unit test of the CLOSED FORMS against the direct re-scoring they
    replace: inject + c * SE_diff(t_i) into every draw at t_{i+1} ARITHMETICALLY
    and confirm the resulting AM-3 statistic equals stat_i(c) of prereg 3.2 to
    float tolerance, and that the step first fires exactly at c_min.

    This is an IMPLEMENTATION CHECK of the code. It is NOT a control, NOT a
    result, and NOT an alternative rule: it computes the same frozen quantities
    two ways. It exists so that 'c_min(i) = x' is a statement about the frozen
    formula rather than about a transcription error."""
    rng = np.random.default_rng(20260808)
    t = GRADED_T
    base = np.linspace(1.10, 1.00, len(t))
    vals = [[float(base[i] + 0.01 * rng.standard_normal()) for _ in range(N_DRAW)]
            for i in range(len(t))]
    haar = [1.0 + 0.01 * float(rng.standard_normal()) for _ in range(N_DRAW)]
    hs = float(np.std(haar, ddof=1))
    means = [float(np.mean(v)) for v in vals]
    sedf = [se_of_difference(float(np.std(v, ddof=1)), hs) for v in vals]

    worst_stat, worst_delta, first_fire_ok = 0.0, 0.0, True
    for i in range(len(t) - 1):
        row = closed_form_step(i, t, means, vals, sedf)
        unit = row["injection_unit_se_diff"]
        for c in C_GRID:
            inj = [list(v) for v in vals]
            inj[i + 1] = [v + c * unit for v in inj[i + 1]]
            im = [float(np.mean(v)) for v in inj]
            isd = [se_of_difference(float(np.std(v, ddof=1)), hs) for v in inj]
            dl = im[i + 1] - im[i]
            ss = float((np.array(inj[i + 1]) - np.array(inj[i]))
                       .std(ddof=1) / np.sqrt(N_DRAW))
            eb = isd[i] if isd[i] != 0.0 else isd[i + 1]
            direct = (dl - AM3_EPSILON_K * eb) / ss
            worst_stat = max(worst_stat,
                             abs(direct - row["am3_statistic"][str(c)]))
            worst_delta = max(worst_delta,
                              abs(dl - row["post_injection_delta"][str(c)]))
        # the step fires exactly at c_min: check just below and just above
        lo = (row["delta"] + (row["c_min"] - 1e-6 - 1.0) * unit) / row["se_step_paired"]
        hi = (row["delta"] + (row["c_min"] + 1e-6 - 1.0) * unit) / row["se_step_paired"]
        first_fire_ok &= bool(lo <= AM3_T_CRIT < hi)

    return {
        "status": ("IMPLEMENTATION CHECK of the frozen closed forms. NOT a "
                   "result, NOT a control, NOT an alternative rule."),
        "max_abs_dev_statistic_closed_form_vs_direct_injection": worst_stat,
        "max_abs_dev_post_injection_delta_closed_form_vs_direct": worst_delta,
        "step_first_fires_exactly_at_c_min_at_every_step": first_fire_ok,
        "t_crit_literal": AM3_T_CRIT,
        "t_crit_recomputed_scipy_t_ppf_0p998_df7": float(student_t.ppf(0.998, 7)),
        "t_crit_agrees": bool(abs(float(student_t.ppf(0.998, 7)) - AM3_T_CRIT)
                              <= 1e-12),
        "alpha_per_step_recomputed_sf": float(student_t.sf(AM3_T_CRIT, 7)),
        "alpha_per_step_declared": AM3_ALPHA_PER_STEP,
        "union_bound_recomputed": AM3_FAMILY_SIZE * AM3_ALPHA_PER_STEP,
        "union_bound_declared": AM3_DECLARED_FWER,
        "sidak_reference_recomputed": float(1.0 - (1.0 - AM3_ALPHA_PER_STEP)
                                            ** AM3_FAMILY_SIZE),
        "sidak_reference_declared": AM3_SIDAK_REFERENCE,
    }


# ============================================================ prereg gate
def sh(cmd):
    return subprocess.run(cmd, shell=True, cwd=REPO_ROOT, capture_output=True,
                          text=True)


def verify_prereg():
    with open(PREREG_PATH, "rb") as f:
        raw = f.read()
    got = hashlib.sha256(raw).hexdigest()
    sidecar = open(SIDECAR_PATH).read().split()[0].strip() \
        if os.path.exists(SIDECAR_PATH) else None
    receipt_path_sha = receipt_field = receipt_task = None
    if os.path.exists(RECEIPT_PATH):
        rec = json.load(open(RECEIPT_PATH))
        receipt_path_sha = rec["archive"]["path_sha256"].get(PREREG_REL)
        receipt_field = rec.get("prereg_sha256")
        receipt_task = rec.get("task_id")

    # ---- DEFECT D-2 GUARD: verify REPO_ROOT really is THIS worktree ----
    top = subprocess.run(["git", "-C", REPO_ROOT, "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True)
    toplevel = top.stdout.strip() if top.returncode == 0 else None
    root_ok = bool(toplevel
                   and os.path.realpath(toplevel) == os.path.realpath(REPO_ROOT))
    common = subprocess.run(["git", "-C", REPO_ROOT, "rev-parse",
                             "--git-common-dir"], capture_output=True, text=True)

    blob_raw = subprocess.run(["git", "show", f"{NOTARIZING_COMMIT}:{PREREG_REL}"],
                              cwd=REPO_ROOT, capture_output=True)
    blob_sha = hashlib.sha256(blob_raw.stdout).hexdigest() \
        if blob_raw.returncode == 0 else None

    anc = sh(f"git merge-base --is-ancestor {NOTARIZING_COMMIT} HEAD")
    head = sh("git rev-parse HEAD").stdout.strip()
    branch = sh("git rev-parse --abbrev-ref HEAD").stdout.strip()
    dirty = sh("git status --porcelain").stdout.strip()
    follow = sh(f"git log --follow --format=%H -- {PREREG_REL}").stdout.split()
    notar_meta = sh(f"git show -s --format=%H|%ci|%s {NOTARIZING_COMMIT}").stdout.strip()

    ok = (got == EXPECTED_PREREG_SHA256
          and (sidecar is None or sidecar == got)
          and (receipt_path_sha is None or receipt_path_sha == got)
          and (receipt_field is None or receipt_field == got)
          and blob_sha == got
          and root_ok
          and anc.returncode == 0)
    return {
        "prereg_path": PREREG_REL,
        "prereg_bytes": len(raw),
        "recomputed_sha256": got,
        "expected_sha256_from_task_card": EXPECTED_PREREG_SHA256,
        "producer_prereg_sha256_txt": sidecar,
        "notarized_receipt_path_sha256": receipt_path_sha,
        "notarized_receipt_prereg_sha256_field": receipt_field,
        "notarized_receipt_task_id": receipt_task,
        "sha256_of_blob_inside_notarizing_commit": blob_sha,
        "notarizing_commit": NOTARIZING_COMMIT,
        "notarizing_commit_metadata": notar_meta,
        "repo_root_resolved": REPO_ROOT,
        "git_show_toplevel_from_repo_root": toplevel,
        "git_common_dir": common.stdout.strip() if common.returncode == 0 else None,
        "repo_root_is_this_worktree": root_ok,
        "defect_D2_guard": ("REPO_ROOT is four levels above batches/ AND is "
                            "verified to equal `git rev-parse --show-toplevel` "
                            "run from it. The sibling task AM-7 recorded defect "
                            "D-2 where a five-level REPO_ROOT resolved to the "
                            "enclosing checkout and asserted against the wrong "
                            "HEAD. The assertion below is made IN THIS "
                            "WORKTREE."),
        "ancestry_check":
            f"git merge-base --is-ancestor {NOTARIZING_COMMIT} HEAD",
        "ancestry_check_asserts": ("the NOTARIZING COMMIT ITSELF, not its "
                                   "parent -- carried correction V-7, prereg 0.3"),
        "ancestry_is_ancestor_of_HEAD": bool(anc.returncode == 0),
        "head_commit": head,
        "branch": branch,
        "worktree_dirty": bool(dirty),
        "worktree_dirty_paths": dirty.splitlines(),
        "git_log_follow_commits_touching_prereg": follow,
        "git_log_follow_count": len(follow),
        "match": bool(ok),
    }


# ====================================================================== main
def cpu_seconds():
    a = resource.getrusage(resource.RUSAGE_SELF)
    b = resource.getrusage(resource.RUSAGE_CHILDREN)
    return a.ru_utime + a.ru_stime + b.ru_utime + b.ru_stime


def peak_rss_gb():
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return r / (1024.0 ** 3) if sys.platform == "darwin" else r / (1024.0 ** 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TASK_DIR, "results_g3.json"))
    ap.add_argument("--wall-budget-seconds", type=float, default=5400.0)
    ap.add_argument("--memory-budget-gb", type=float, default=4.0)
    args = ap.parse_args()

    def on_alarm(signum, frame):
        raise TimeoutError(
            f"wall-clock budget {args.wall_budget_seconds}s exhausted -- "
            "RESOURCE EXHAUSTION, an infrastructure outcome, never negative "
            "mathematical evidence (AGENTS.md rule 3)")
    signal.signal(signal.SIGALRM, on_alarm)
    signal.alarm(int(args.wall_budget_seconds))

    t_start = time.time()

    # -------------------------------------------- GATE: the notarized prereg
    ver = verify_prereg()
    print("=" * 78)
    print("NOTARIZED PRE-REGISTRATION VERIFICATION (prereg 0.3 / 7; task card)")
    for k, v in ver.items():
        s = str(v)
        print(f"  {k:46s}: {s if len(s) < 220 else s[:220] + ' ...'}")
    if not ver["match"]:
        print("ABORT: prereg.md sha256 / REPO_ROOT / ancestry verification FAILED.")
        print("This is a HARNESS FAILURE, not a result. The run does not proceed.")
        return 2
    print("  VERIFIED. The frozen specification is loaded read-only and unmodified.")
    print(f"  AM-1 grid (13 pts, RETAINED, verbatim): {GRADED_T}")
    print(f"  AM-3 gate CARRIED UNCHANGED: (Delta_i - {AM3_EPSILON_K}"
          f"*SE_diff(A,t_i))/SE_step_paired(i) > {AM3_T_CRIT}")
    print(f"  declared family-wise false-failure rate: {AM3_DECLARED_FWER} "
          f"= {AM3_FAMILY_SIZE} x {AM3_ALPHA_PER_STEP}")
    print("  STEP SELECTION: THERE IS NONE (prereg 3.3). All 12 steps of all "
          "4 cells are reported.")
    print(f"  PRED-B1 (frozen): n_fire(cell, c={PRED_B1_C}) >= "
          f"{PRED_B1_THRESHOLD} in EVERY one of the four cells.")
    print("  NO NEW BKZ. NO LLL. Graded and Haar arms are pure numpy; the "
          "seeds are the cache.")
    print("  " + GATE_NOMINAL_DISCLOSURE)
    print("=" * 78)
    sys.stdout.flush()

    res = {
        "task_id": "TASK-20260808-cece0c",
        "batch_id": "BATCH-cbe023",
        "goal_id": "GOAL-MLKEM-005",
        "section": "B",
        "amendment": "AM-6",
        "role": "executor",
        "claim_tier": "toy",
        "claim_boundary": ("Nothing measured here bears on ML-KEM security, on "
                           "any FIPS 203 parameter set, on any attack cost, or "
                           "on any cost model. d <= 140, beta <= 40."),
        "certificate": {
            "kind": "none",
            "reason": ("No discrete-log solve and no factor-base relation is "
                       "claimed or produced, so docs/claims-and-verification.md "
                       "requires no solution certificate. The independent "
                       "re-verifications this run carries are INSTRUMENT CHECKS "
                       "and are labelled as such, never as certificates."),
        },
        "governed_by": ("prereg.md of TASK-20260808-35efa3, Section B (3.1-3.9), "
                        "notarized by TASK-20260808-e725b4 in commit "
                        + NOTARIZING_COMMIT),
        "prereg_verification": ver,
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "read_order": [
            "0. prereg.md loaded read-only, re-hashed against the task-card "
            "constant, the sidecar, the notarized receipt AND the blob inside "
            "the notarizing commit; REPO_ROOT verified to be THIS worktree; "
            "ancestry asserted against the notarizing commit itself",
            "1. graded + Haar arms regenerated FROM SEEDS (pure numpy, no BKZ, "
            "no LLL)",
            "2. seed-cache reproduction re-verified BEFORE any scoring, max "
            "deviation reported unrounded",
            "3. closed forms c_min / c_pos evaluated at ALL 12 steps of ALL 4 "
            "cells, with the post-injection Delta at every c",
            "4. the closed-form guarantee c_min(i) > c_pos(i) verified at all 48",
            "5. NC-B1 (c=0), NC-B2 (c=-6), NC-B3 (Delta_i > 0 flags)",
            "6. PRED-B1 scored at the FIXED c = 6",
            "7. realized false-failure behaviour against the declared 0.096",
            "8. bootstrap UQ on c_min (no verdict)",
            "9. the could-not-fail demonstration, in BOTH directions",
        ],
        "binding_carries": {
            "AM3_is_not_retired": (
                "AM-3 IS NOT RETIRED and is NOT on trial for its life here. Its "
                "0.096 family-wise false-failure bound is correctly derived, was "
                "declared before any datum existed, and is mechanically free of "
                "every run-supplied quantity. Its POWER is UNDEMONSTRATED, not "
                "disproved [carried: prereg 1.3 item 1 / 3.1 item 1]."),
            "a_firing_finding_does_not_reinstate_BATCH_a44d08": (
                "A FINDING THAT THE GATE CAN FIRE DOES NOT REINSTATE "
                "BATCH-a44d08'S READINGS. Its frozen INADMISSIBLE verdict stands "
                "as the output of its frozen rule on its frozen data and is NOT "
                "rescored here. Its four PARTIAL cell readings stay WITHHELD and "
                "are not lifted out [carried: prereg 3.1 item 2]."),
            "section_C_proposition_open_both_directions": (
                "Section C's proposition -- whether D depends on the frame only "
                "through V at the 2^-10 quantile -- stays OPEN IN BOTH "
                "DIRECTIONS. Nothing from BATCH-a44d08's Section C is cited "
                "here, as a baseline, as a prior, or at all [carried: prereg 1.3 "
                "item 2]."),
            "claim_tier": ("TOY, unconditionally. No number here is transported "
                           "to beta = 606, d = 1420, to any FIPS 203 parameter "
                           "set, to any attack cost, or to any other parameter "
                           "set, by extrapolation or by analogy."),
            "infrastructure_rule": ("Budget exhaustion, timeout, crash or a "
                                    "missing dependency is INFRASTRUCTURE SIGNAL "
                                    "and is NEVER negative mathematical evidence "
                                    "(AGENTS.md rule 3). gmpy2 is ABSENT in this "
                                    "environment and nothing here depends on it."),
        },
        "step_selection_rule": {
            "rule": "THERE IS NONE (prereg 3.3).",
            "statement": ("Every one of the 12 steps of every one of the 4 cells "
                          "is reported. No step is selected, so no selection "
                          "rule can maximise the quantity the injection is "
                          "denominated in. AM-6 clause (b) is satisfied by "
                          "REMOVING the object that carried the defect rather "
                          "than by replacing it."),
            "does_not_maximise_the_injections_own_denominator": (
                "The injection is denominated in SE_diff(A, t_i). "
                "BATCH-a44d08's rule selected i = argmax_i SE_diff(A, t_i) over "
                "the 12 lower endpoints -- i.e. it maximised exactly that "
                "denominator, which is largest at the head of the descent where "
                "|Delta_i| is 11x to 26x the injection unit. This run applies NO "
                "argmax, NO argmin and NO data-dependent or grid-dependent "
                "selection to the frozen headline: all 48 steps are scored and "
                "reported. The two SUMMARIES S1 and S2 are labelled and are not "
                "the headline; S1 uses only the frozen grid position and no "
                "measured quantity, and S2 is explicitly data-dependent and "
                "descriptive."),
            "verification": ("A reader can check this mechanically: the frozen "
                             "headline PRED-B1 is a count over ALL 12 steps of "
                             "each cell, and this file contains no argmax over "
                             "any SE quantity."),
        },
        "frozen_closed_forms": {
            "source": "prereg.md Section 3.2, quoted",
            "stat": "stat_i(c) = ( Delta_i + (c-1)*SE_diff(t_i) ) / SE_step(i)",
            "c_min": "c_min(i) = 1 + ( t_crit*SE_step(i) - Delta_i )/SE_diff(t_i)",
            "c_pos": "c_pos(i) = max( 0 , -Delta_i / SE_diff(t_i) )",
            "guarantee": ("c_min(i) > c_pos(i) STRICTLY at every step: at "
                          "c = c_min(i) the post-injection Delta equals "
                          "epsilon_i + t_crit*SE_step(i), which is strictly "
                          "positive whenever SE_diff(t_i) > 0 and SE_step(i) > 0. "
                          "Hence every firing the AM-3 gate can produce sits on a "
                          "GENUINELY POSITIVE post-injection Delta."),
            "t_crit": AM3_T_CRIT,
            "t_crit_label": "t_{7,0.998}  [closed form, scipy.stats.t]",
            "epsilon": f"epsilon_i = {AM3_EPSILON_K} * SE_diff(A, t_i)",
            "degenerate_policy": ("if SE_diff(t_i)=0 use SE_diff(t_{i+1}); if "
                                  "both are 0, or SE_step(i)=0, the step is "
                                  "flagged DEGENERATE, c_min/c_pos are undefined "
                                  "with the reason, and the step is EXCLUDED "
                                  "from the counts with the exclusion printed. "
                                  "No division by zero is performed."),
            "gate_nominal_factor_disclosure": GATE_NOMINAL_DISCLOSURE,
        },
        "quoted_review_priors": QUOTED_REVIEW_PRIORS,
        "config": {"q": Q_MOD, "cells": CELLS, "graded_t": GRADED_T,
                   "errors_per_cell": N_ERR, "draws_per_arm": N_DRAW,
                   "chunk": CHUNK, "tail_level": "2^-10",
                   "estimator": "q_emp(p) = sort(R)[round(p*N)-1]; index 1023",
                   "gate_k": GATE_K, "c_grid": C_GRID,
                   "c_negative_control": C_NEG_CONTROL,
                   "pred_b1_c": PRED_B1_C,
                   "pred_b1_threshold_steps_of_12": PRED_B1_THRESHOLD,
                   "bootstrap_B": BOOTSTRAP_B},
        "seed_scheme": {
            "numpy_cbd_error_seed": "20260805 + d",
            "numpy_haar_seed": "900000 + d*1000 + beta*10 + j",
            "numpy_graded_seed": "500000 + d*1000 + beta*10 + j",
            "bootstrap_seed": "default_rng([9, d, beta, 0])  [TAG 9, prereg 6]",
            "note": "THE SEEDS ARE THE CACHE. No frame cache exists on disk.",
        },
        "instrument_checks": {},
        "seed_cache_reproduction": {},
        "cells": {},
        "pred_b1": {},
        "negative_controls": {},
        "false_failure_behaviour": {},
        "bootstrap_uncertainty": {},
        "timings": {},
    }

    # ------------------------------------- stage 1: regenerate the arms
    t1 = time.time()
    measured, frame_V_by_cell, errs = {}, {}, {}
    for d in sorted({dd for dd, _ in CELLS}):
        te = time.time()
        Ef, n2, chk = make_errors(d)
        errs[d] = (Ef, n2)
        res["instrument_checks"][f"cbd_pmf_d{d}"] = chk
        print(f"[errors] d={d}: 2^20 CBD_eta2 draws in {time.time() - te:.1f}s")
        sys.stdout.flush()

    qb10_by_cell = {}
    for (d, beta) in CELLS:
        key = f"d{d}_b{beta}"
        tc = time.time()
        a, b = beta / 2.0, (d - beta) / 2.0
        qb10 = float(betaincinv(a, b, P_TAIL_10))
        qb10_by_cell[key] = qb10
        Ef, n2 = errs[d]
        Qs = {"haar_null": haar_frames(d, beta)}
        paths = graded_paths(d, beta)
        for t in GRADED_T:
            Qs[arm_t(t)] = graded_frames_from_paths(paths, t)
        del paths
        frame_V_by_cell[key] = {nm: frame_V(QQ, d, beta) for nm, QQ in Qs.items()}
        measured[key] = {}
        for nm, QQ in Qs.items():
            R = project(Ef, n2, QQ, beta)
            measured[key][nm] = arm_r_values(R, qb10)
            del R
        del Qs
        res["timings"][f"arms_{key}_wall_seconds"] = round(time.time() - tc, 2)
        print(f"[arms] {key}: 14 arms x 8 draws in {time.time() - tc:.1f}s "
              f"(q_Beta(2^-10) = {qb10:.17g})")
        sys.stdout.flush()
        rss = peak_rss_gb()
        if rss > args.memory_budget_gb:
            raise MemoryError(
                f"peak RSS {rss:.2f} GB exceeds the {args.memory_budget_gb} GB "
                "budget -- RESOURCE EXHAUSTION, never a result")
    for d in list(errs):
        del errs[d]
    res["config"]["q_Beta_2em10_per_cell"] = qb10_by_cell
    res["timings"]["stage1_arms_wall_seconds"] = round(time.time() - t1, 2)

    # ------------------- stage 2: seed-cache reproduction, BEFORE any scoring
    t2 = time.time()
    print("[repro] re-verifying the seed-cache reproduction BEFORE scoring "
          "anything (task card; prereg 3.5)")
    rep = {
        "why": ("prereg 3.5 / task card: NO NEW BKZ -- the graded arms are pure "
                "numpy and the seeds are the cache. Re-verify the reproduction "
                "BEFORE scoring anything and report the max deviation. The "
                "declared expected non-zero deviation "
                "(2.220446049250313e-16 at d = 140, one ULP, from a "
                "betaincinv difference under scipy 1.15.3) MUST NOT be rounded "
                "to 0.0."),
        "no_reduction_run": ("NO LLL and NO BKZ is executed by this run. No "
                             "lattice is generated and no basis is reduced."),
        "r_values_vs_committed_results_g3_json": repro_vs_committed_g3(measured),
        "r_values_vs_BATCH_f19c37": repro_vs_f19c37(measured),
    }
    res["seed_cache_reproduction"] = rep
    g = rep["r_values_vs_committed_results_g3_json"]
    f = rep["r_values_vs_BATCH_f19c37"]
    print(f"[repro] vs committed results_g3.json: n={g.get('n_values_compared')} "
          f"max abs dev = {g.get('max_abs_deviation')!r}  by d = "
          f"{g.get('max_abs_deviation_by_d')}")
    print(f"[repro] vs BATCH-f19c37 results.json : n={f.get('n_values_compared')} "
          f"max abs dev = {f.get('max_abs_deviation')!r}  by d = "
          f"{f.get('max_abs_deviation_by_d')}")
    sys.stdout.flush()
    res["timings"]["stage2_reproduction_wall_seconds"] = round(time.time() - t2, 2)

    # -------------- stage 3: implementation check of the closed forms
    res["instrument_checks"]["closed_form_implementation_check"] = \
        closed_form_implementation_check()
    ic = res["instrument_checks"]["closed_form_implementation_check"]
    print("[impl-check] closed form vs direct injection: max |dstat| = "
          f"{ic['max_abs_dev_statistic_closed_form_vs_direct_injection']:.3e}, "
          "max |dDelta| = "
          f"{ic['max_abs_dev_post_injection_delta_closed_form_vs_direct']:.3e}, "
          "first-fire at c_min = "
          f"{ic['step_first_fires_exactly_at_c_min_at_every_step']}, "
          f"t_crit agrees = {ic['t_crit_agrees']}")
    sys.stdout.flush()

    # ------------- stage 4: the closed forms at ALL 12 steps of ALL 4 CELLS
    t4 = time.time()
    print()
    print("=" * 78)
    print("SECTION B -- c_min IN CLOSED FORM AT ALL 12 STEPS OF ALL 4 CELLS")
    print("NO STEP SELECTION (prereg 3.3).  Post-injection Delta printed at "
          "every step.")
    print("=" * 78)
    for (d, beta) in CELLS:
        key = f"d{d}_b{beta}"
        hm = measured[key]["haar_null"]["mean"]
        hs = measured[key]["haar_null"]["sd"]
        per_t, means, values, se_diff = {}, [], [], []
        for t in GRADED_T:
            arm = measured[key][arm_t(t)]
            sd_diff = se_of_difference(arm["sd"], hs)
            per_t[tkey(t)] = {
                "t": t, "r_mean": arm["mean"], "r_sd": arm["sd"],
                "r_values": arm["values"],
                "order_stat_index_used": arm["order_stat_k"] - 1,
                "se_diff_vs_haar_null": sd_diff,
                "V": frame_V_by_cell[key][arm_t(t)],
            }
            means.append(arm["mean"])
            values.append(arm["values"])
            se_diff.append(sd_diff)

        sc = score_cell(GRADED_T, means, values, se_diff)
        sc["d"], sc["beta"], sc["q"] = d, beta, Q_MOD
        sc["haar_null"] = {"r_mean": hm, "r_sd": hs,
                           "r_values": measured[key]["haar_null"]["values"],
                           "V": frame_V_by_cell[key]["haar_null"]}
        sc["per_t"] = per_t
        res["cells"][key] = sc

        print()
        print(f"CELL {key}  (d={d}, beta={beta}, q={Q_MOD}, n_draws={N_DRAW}, "
              f"N=2^20)   haar_null r_mean={hm:.9f} r_sd={hs:.3e}")
        print("  i  t_lo    t_hi     Delta_i      SE_step     SE_diff(t_i)"
              "   eps_i      c_pos      c_min    c_min/4  inc flat")
        for s in sc["steps"]:
            if s["degenerate"]:
                print(f"  {s['i']:2d} {s['t_lo']:.4f} {s['t_hi']:.4f}  "
                      f"DEGENERATE: {s['degenerate_reason']} -- c_min, c_pos "
                      f"undefined; EXCLUDED from counts")
                continue
            print(f"  {s['i']:2d} {s['t_lo']:.4f} {s['t_hi']:.4f} "
                  f"{s['delta']:+.6e} {s['se_step_paired']:.4e} "
                  f"{s['se_diff_at_t_lo']:.4e} {s['epsilon']:.4e} "
                  f"{s['c_pos']:9.4f} {s['c_min']:10.4f} {s['c_min_over_4']:8.4f}"
                  f"  {'Y' if s['flag_delta_gt_0_in_raw_data'] else '.'} "
                  f"{'Y' if s['flag_near_flat_S2'] else '.'}")
        print("  post-injection Delta_i(c) = Delta_i + c*SE_diff(t_i), "
              "printed at every c of the frozen grid:")
        print("  i  " + "".join(f"{('c=' + str(c)):>13s}" for c in C_GRID))
        for s in sc["steps"]:
            if s["degenerate"]:
                continue
            print(f"  {s['i']:2d} " + "".join(
                f"{s['post_injection_delta'][str(c)]:+13.5e}" for c in C_GRID))
        print("  fires(c) = stat_i(c) > t_crit   (equivalently c_min(i) <= c):")
        print("  i  " + "".join(f"{('c=' + str(c)):>7s}" for c in C_GRID))
        for s in sc["steps"]:
            if s["degenerate"]:
                continue
            print(f"  {s['i']:2d} " + "".join(
                f"{('FIRE' if s['fires'][str(c)] else '.'):>7s}"
                for c in C_GRID))
        print(f"  n_fire(c)                          : "
              f"{ {c: sc['n_fire'][str(c)] for c in C_GRID} }")
        print(f"  n_fire(c) EXCLUDING already-increasing steps: "
              f"{ {c: sc['n_fire_excluding_already_increasing_steps'][str(c)] for c in C_GRID} }")
        print(f"  steps with Delta_i > 0 in the raw data (NC-B3): "
              f"{sc['n_steps_with_delta_gt_0']} of {sc['n_steps']} "
              f"at indices {sc['increasing_step_indices']}")
        print(f"  c_min(i) > c_pos(i) at every step of this cell: "
              f"{sc['c_min_gt_c_pos_all_steps']}")
        print(f"  S1 (grid-position, data-INDEPENDENT) median c_min over "
              f"i in {S1_STEPS}: {sc['S1_grid_position_summary_DATA_INDEPENDENT']['median']}"
              f"  range [{sc['S1_grid_position_summary_DATA_INDEPENDENT']['min']}, "
              f"{sc['S1_grid_position_summary_DATA_INDEPENDENT']['max']}]")
        print(f"  S2 (near-flat, DATA-DEPENDENT, descriptive) median c_min: "
              f"{sc['S2_near_flat_summary_DATA_DEPENDENT']['median']}  n="
              f"{sc['S2_near_flat_summary_DATA_DEPENDENT']['n']}")
        sys.stdout.flush()
    res["timings"]["stage4_closed_forms_wall_seconds"] = round(time.time() - t4, 2)

    # --------------- stage 5: the closed-form guarantee over all 48 steps
    all_live = [s for k in res["cells"] for s in res["cells"][k]["steps"]
                if not s["degenerate"]]
    all_steps = [s for k in res["cells"] for s in res["cells"][k]["steps"]]
    n_gt = sum(1 for s in all_live if s["c_min_gt_c_pos"])
    viol = [{"cell": k, "i": s["i"], "c_min": s["c_min"], "c_pos": s["c_pos"]}
            for k in res["cells"] for s in res["cells"][k]["steps"]
            if (not s["degenerate"]) and not s["c_min_gt_c_pos"]]
    res["closed_form_guarantee"] = {
        "statement": "c_min(i) > c_pos(i) STRICTLY at every step (prereg 3.2)",
        "n_steps_total": len(all_steps),
        "n_steps_degenerate_excluded": len(all_steps) - len(all_live),
        "n_steps_checked": len(all_live),
        "n_steps_satisfying_c_min_gt_c_pos": n_gt,
        "holds_at_all_checked_steps": bool(n_gt == len(all_live)),
        "violations": viol,
        "min_margin_c_min_minus_c_pos": min((s["c_min_minus_c_pos"]
                                             for s in all_live), default=None),
        "identity_max_abs_dev": max(
            (abs(s["post_injection_delta_at_c_min"]
                 - s["post_injection_delta_at_c_min_identity_check"])
             for s in all_live), default=None),
        "identity": ("post-injection Delta at c = c_min(i) equals "
                     "epsilon_i + t_crit*SE_step(i), verified numerically"),
        "consequence": ("EVERY firing this gate can produce sits on a GENUINELY "
                        "POSITIVE post-injection Delta. The gate cannot be made "
                        "to fire on a step that is still decreasing. A violation "
                        "here would be an IMPLEMENTATION ERROR, not a finding "
                        "(prereg 3.2)."),
        "min_post_injection_delta_at_c_min_over_48": min(
            (s["post_injection_delta_at_c_min"] for s in all_live), default=None),
        "all_post_injection_deltas_at_c_min_strictly_positive": bool(all(
            s["post_injection_delta_at_c_min"] > 0.0 for s in all_live)),
    }
    print()
    print("CLOSED-FORM GUARANTEE over all 48 steps: c_min(i) > c_pos(i) at "
          f"{n_gt}/{len(all_live)} checked steps "
          f"(degenerate excluded: {len(all_steps) - len(all_live)}); "
          f"min margin = {res['closed_form_guarantee']['min_margin_c_min_minus_c_pos']!r}")

    # ------------------------------- stage 6: PRED-B1, scored at a FIXED c = 6
    per_cell_n_fire = {k: res["cells"][k]["n_fire"][str(PRED_B1_C)]
                       for k in res["cells"]}
    per_cell_n_fire_excl = {
        k: res["cells"][k]["n_fire_excluding_already_increasing_steps"]
        [str(PRED_B1_C)] for k in res["cells"]}
    pooled = {str(c): sum(res["cells"][k]["n_fire"][str(c)]
                          for k in res["cells"]) for c in C_GRID}
    pooled_excl = {str(c): sum(
        res["cells"][k]["n_fire_excluding_already_increasing_steps"][str(c)]
        for k in res["cells"]) for c in C_GRID}
    failing = [k for k, v in per_cell_n_fire.items() if v <= PRED_B1_THRESHOLD - 1]
    res["pred_b1"] = {
        "frozen_statement": (f"PRED-B1: n_fire(cell, c={PRED_B1_C}) >= "
                             f"{PRED_B1_THRESHOLD} in EVERY one of the four "
                             "cells."),
        "threshold_unit": "a COUNT OF STEPS out of 12",
        "falsifier": f"any cell with n_fire(c={PRED_B1_C}) <= "
                     f"{PRED_B1_THRESHOLD - 1}",
        "provenance_of_the_number": (
            "The Red Team's REVIEW MEASUREMENT reports the identical injection "
            "firing at c <= 6 at 6, 7, 9, 7 of the 12 steps in the four cells "
            "[quoted: red_team_report.md section 2.2]. AM-6 forbids citing that "
            "as a rescoring; it is used here ONLY to set a prior, and 4 is "
            "chosen strictly below all four quoted values so PRED-B1 is a "
            "genuine two-sided claim about THIS run's own recomputation."),
        "scored_at_fixed_c": PRED_B1_C,
        "per_cell_n_fire_at_c6": per_cell_n_fire,
        "per_cell_n_fire_at_c6_excluding_already_increasing_steps":
            per_cell_n_fire_excl,
        "cells_failing_the_threshold": failing,
        "outcome": "PRED-B1 MET" if not failing else "PRED-B1 FALSIFIED",
        "outcome_note": ("This is the scoring of a frozen prediction against "
                         "this run's own recomputation. It is an OBSERVATION. "
                         "It is not a conclusion that AM-3 is adequate, "
                         "validated, or refuted, and it does not retire AM-3."),
        "power_curve_pooled_over_48": pooled,
        "power_curve_pooled_excluding_already_increasing_steps": pooled_excl,
        "per_cell_power_curve": {k: res["cells"][k]["n_fire"]
                                 for k in res["cells"]},
        "per_cell_power_curve_excluding_already_increasing_steps": {
            k: res["cells"][k]["n_fire_excluding_already_increasing_steps"]
            for k in res["cells"]},
    }

    # --------------------- the plain statement required by prereg 3.5 secondary
    can_fire = bool(pooled[str(PRED_B1_C)] > 0)
    res["can_the_am3_gate_fire"] = {
        "answered_by": f"n_fire(pooled, c={PRED_B1_C}) > 0  (prereg 3.5)",
        "n_fire_pooled_at_c6": pooled[str(PRED_B1_C)],
        "n_steps_pooled": len(all_live),
        "PLAIN_STATEMENT_CAN_IT_FIRE": (
            "The AM-3 gate CAN fire: at the fixed injection c = 6 it fires at "
            f"{pooled[str(PRED_B1_C)]} of the {len(all_live)} non-degenerate "
            "steps pooled over the four cells, and every one of those firings "
            "sits on a strictly positive post-injection Delta by the verified "
            "closed-form guarantee c_min(i) > c_pos(i)."
            if can_fire else
            "At the fixed injection c = 6 the AM-3 gate fired at 0 of the "
            f"{len(all_live)} non-degenerate steps pooled over the four cells "
            "on this run's recomputation."),
        "PLAIN_STATEMENT_DID_IT_FIRE_IN_BATCH_a44d08": (
            "SEPARATELY, and this is a different statement: in BATCH-a44d08 the "
            "gate DID NOT fire. Its positive control selected steps by "
            "argmax SE_diff(A, t_i) -- the injection's own denominator -- and "
            "at c = 6 the post-injection Delta was still NEGATIVE, so no "
            "monotonicity violation of any size was ever presented to it. Its "
            "frozen INADMISSIBLE verdict stands as the output of its frozen "
            "rule on its frozen data and is NOT rescored here."),
        "these_are_two_different_statements": (
            "Whether the gate CAN fire is a property of the gate. Whether it "
            "DID fire in BATCH-a44d08 is a property of that run's step "
            "selection. The first does not reinstate the second's readings, and "
            "BATCH-a44d08's four PARTIAL cell readings stay WITHHELD."),
    }

    # ------------------------------------------ stage 7: negative controls
    ncb1_fires = sum(1 for s in all_live if s["fires"]["0"])
    ncb1_stats = [s["am3_statistic"]["0"] for s in all_live]
    ncb2_fires = sum(1 for s in all_live if s["fires_at_c_neg6"])
    ncb2_stats = [s["am3_statistic_at_c_neg6"] for s in all_live]
    n_inc_pooled = sum(1 for s in all_live if s["flag_delta_gt_0_in_raw_data"])
    max_stat0 = max(ncb1_stats) if ncb1_stats else None
    res["negative_controls"] = {
        "NC_B1_c_equals_0": {
            "requirement": ("the UN-INJECTED family must return 0 violations of "
                            "48, reproducing the committed AM3-TIE in all four "
                            "cells with max statistic "
                            f"{NC_B1_COMMITTED_MAX_STAT} [quoted: "
                            "validation_report.yaml MR-B1]. A gate that fires "
                            "without an injection is broken."),
            "n_violations_of_48": ncb1_fires,
            "max_am3_statistic_over_family": max_stat0,
            "committed_max_am3_statistic_quoted": NC_B1_COMMITTED_MAX_STAT,
            "abs_dev_from_committed_max_statistic":
                (abs(max_stat0 - NC_B1_COMMITTED_MAX_STAT)
                 if max_stat0 is not None else None),
            "per_cell_max_statistic": {
                k: max(s["am3_statistic"]["0"] for s in res["cells"][k]["steps"]
                       if not s["degenerate"]) for k in res["cells"]},
            "passes": bool(ncb1_fires == 0),
        },
        "NC_B2_c_equals_minus_6": {
            "requirement": ("a NEGATIVE injection (making every step more "
                            "strongly decreasing) must return 0 violations of "
                            "48. A gate that fires on a reinforced decrease is "
                            "broken."),
            "n_violations_of_48": ncb2_fires,
            "max_am3_statistic_over_family": max(ncb2_stats) if ncb2_stats else None,
            "passes": bool(ncb2_fires == 0),
        },
        "NC_B3_already_increasing_steps_flagged": {
            "requirement": ("BATCH-a44d08 recorded 9 of 48 steps with Delta_i > "
                            "0 in the raw data [quoted: validation_report.yaml "
                            "MR-B1]. At such a step a small c fires partly on a "
                            "PRE-EXISTING INCREASE rather than on the "
                            "injection. Every such step is FLAGGED and n_fire "
                            "is additionally reported with those steps "
                            "excluded, both numbers printed."),
            "n_steps_with_delta_gt_0_this_run": n_inc_pooled,
            "committed_quoted": NC_B3_COMMITTED_N_INCREASING,
            "agrees_with_committed": bool(n_inc_pooled
                                          == NC_B3_COMMITTED_N_INCREASING),
            "per_cell": {k: res["cells"][k]["increasing_step_indices"]
                         for k in res["cells"]},
            "n_fire_at_c6_with_them": pooled[str(PRED_B1_C)],
            "n_fire_at_c6_without_them": pooled_excl[str(PRED_B1_C)],
        },
        "consequence_if_either_fails": ("Any of NC-B1 or NC-B2 failing makes "
                                        "the run INSTRUMENT-LIMITED and NO "
                                        "power statement is made from it "
                                        "(prereg 3.6)."),
        "instrument_limited": bool(ncb1_fires != 0 or ncb2_fires != 0),
    }
    print(f"[NC-B1 c=0 ] violations of 48 = {ncb1_fires}   max stat = "
          f"{max_stat0!r}  (committed {NC_B1_COMMITTED_MAX_STAT})")
    print(f"[NC-B2 c=-6] violations of 48 = {ncb2_fires}")
    print(f"[NC-B3     ] steps with Delta_i > 0: {n_inc_pooled} of "
          f"{len(all_live)}  (committed quoted: {NC_B3_COMMITTED_N_INCREASING})")

    # -------- stage 8: realized false-failure behaviour vs the declared rate
    res["false_failure_behaviour"] = {
        "declared_before_any_data": {
            "per_step_alpha": AM3_ALPHA_PER_STEP,
            "family": f"{AM3_FAMILY_STEPS} steps x {AM3_FAMILY_CELLS} cells "
                      f"= {AM3_FAMILY_SIZE} comparisons",
            "family_wise_false_failure_rate_on_a_flawless_instrument":
                AM3_DECLARED_FWER,
            "basis": ("union bound 48 x 0.002 = 0.096, valid under ANY "
                      "dependence; steps sharing an endpoint are dependent"),
            "sidak_reference_only": AM3_SIDAK_REFERENCE,
            "flawless_instrument_definition": (
                "the true mean curve m(t) is non-increasing in t (true Delta_i "
                "<= 0 at every step) and the paired per-draw differences are "
                "exchangeable across the 8 draws [carried: BATCH-a44d08 prereg "
                "3.3]"),
        },
        "realized_on_this_run": {
            "n_comparisons_scored": len(all_live),
            "n_degenerate_excluded": len(all_steps) - len(all_live),
            "n_step_violations_un_injected_c0": ncb1_fires,
            "n_steps_with_delta_gt_0": n_inc_pooled,
            "max_am3_statistic_over_family_un_injected": max_stat0,
            "expected_violation_count_under_flawless_instrument_upper_bound":
                AM3_DECLARED_FWER,
        },
        "reading_discipline": (
            "The declared 0.096 is an UPPER BOUND on P(at least one VIOLATION | "
            "flawless instrument). The realized count above is what the 48 "
            "frozen comparisons returned on this run's un-injected data. A "
            "REALIZED COUNT IS NOT AN ESTIMATE OF A RATE: one run yields one "
            "Bernoulli draw of the family-wise event, and the observed count "
            "bounds nothing about the instrument unless the instrument is "
            "flawless in the sense above. Reported, not interpreted. Whether "
            "the instrument is flawless is not something this run can establish "
            "and is not claimed."),
        "gate_nominal_factor_disclosure": GATE_NOMINAL_DISCLOSURE,
        "separately_the_4_0_gate": (
            "The 4.0 * SE_diff gate that defines SE_diff is a DIFFERENT object "
            "from the AM-3 t_crit criterion. Its realized one-sided "
            "false-positive rate was measured at 0.0015-0.0025 against a "
            "nominal 3e-5 [quoted: BATCH-f19c37 validation_report.yaml item 4 / "
            "V-5]. That is a quoted review measurement, not a result of this "
            "run."),
    }

    # ------------------------------- stage 9: c_min reproduction admissibility
    t9 = time.time()
    rep["c_min_vs_committed"] = repro_cmin_vs_committed(res["cells"])
    r_dev_primary = rep["r_values_vs_committed_results_g3_json"].get(
        "max_abs_deviation")
    r_dev_f19 = rep["r_values_vs_BATCH_f19c37"].get("max_abs_deviation")
    c_dev = rep["c_min_vs_committed"].get("max_abs_dev_c_units")
    r_devs = [x for x in (r_dev_primary, r_dev_f19) if x is not None]
    rep["max_deviation_observed_over_all_re_run_checks"] = \
        max(r_devs) if r_devs else None
    rep["admissibility"] = {
        "threshold_r": REPRO_R_TOL,
        "threshold_c_min_c_units": REPRO_CMIN_TOL,
        "max_abs_dev_r_vs_committed_results_g3_json": r_dev_primary,
        "max_abs_dev_r_vs_BATCH_f19c37": r_dev_f19,
        "max_abs_dev_r_over_both_legs": max(r_devs) if r_devs else None,
        "max_abs_dev_c_min_c_units": c_dev,
        "r_within_threshold": (None if not r_devs
                               else bool(max(r_devs) <= REPRO_R_TOL)),
        "c_min_within_threshold": (None if c_dev is None
                                   else bool(c_dev <= REPRO_CMIN_TOL)),
        "admissible": bool(r_devs and max(r_devs) <= REPRO_R_TOL
                           and c_dev is not None and c_dev <= REPRO_CMIN_TOL),
        "consequence_if_exceeded": ("If either is exceeded the arm is "
                                    "INSTRUMENT-LIMITED, that is reported as "
                                    "the result, and NO power statement is made "
                                    "(prereg 3.5)."),
        "no_rounding": ("Deviations are reported at full float64 repr. The "
                        "declared expected 2.220446049250313e-16 at d = 140 is "
                        "NOT rounded to 0.0."),
    }
    res["timings"]["stage9_cmin_repro_wall_seconds"] = round(time.time() - t9, 2)
    print(f"[repro] c_min committed-vs-this-run max |dev| = {c_dev!r} c units "
          f"(threshold {REPRO_CMIN_TOL})")
    print(f"[repro] ADMISSIBLE = {rep['admissibility']['admissible']}")
    sys.stdout.flush()

    # --------------------------------------- stage 10: bootstrap UQ (no verdict)
    t10 = time.time()
    for (d, beta) in CELLS:
        key = f"d{d}_b{beta}"
        vals = [res["cells"][key]["per_t"][tkey(t)]["r_values"] for t in GRADED_T]
        res["bootstrap_uncertainty"][key] = bootstrap_cmin(
            d, beta, vals, res["cells"][key]["haar_null"]["r_values"])
        fr = [p["fraction_c_min_le_6"]
              for p in res["bootstrap_uncertainty"][key]["per_step"]]
        print(f"[bootstrap] {key}: fraction of B={BOOTSTRAP_B} replicates with "
              f"c_min(i) <= 6, per step: "
              + " ".join(f"{x:.3f}" if x is not None else "n/a" for x in fr))
        sys.stdout.flush()
    res["timings"]["stage10_bootstrap_wall_seconds"] = round(time.time() - t10, 2)

    # ------------------ stage 11: the could-not-fail demonstration, BOTH ways
    res["could_not_fail_demonstration"] = {
        "why_both_directions": (
            "BATCH-a44d08's pre-registration named two could-not-fail forms, "
            "BOTH of the shape 'a gate too lenient to fire', and did NOT name "
            "the mirror, 'a positive control that cannot pass' -- which is the "
            "one it ran in. Both directions are named here. THE SECOND IS THE "
            "ONE THAT ACTUALLY HAPPENED."),
        "direction_1_a_gate_too_lenient_to_fire": {
            "the_arrangement": (
                "A gate so lenient, or a headline so loose, that it fires "
                "regardless. Reporting c_min with an unbounded c axis makes "
                "'the gate fires at SOME c' TRUE AT EVERY NON-DEGENERATE STEP "
                "BY CONSTRUCTION, since c_min(i) is finite whenever "
                "SE_diff(t_i) > 0. A headline of that shape is VACUOUS."),
            "guards_declared_in_advance_and_their_realized_values": {
                "frozen_headline_is_a_count_at_a_FIXED_c": {
                    "statement": f"PRED-B1: n_fire(cell, c={PRED_B1_C}) >= "
                                 f"{PRED_B1_THRESHOLD} of 12 in EVERY cell",
                    "realized_per_cell": per_cell_n_fire,
                    "a_cell_where_every_c_min_exceeds_6_falsifies_it": True,
                },
                "c_min_over_4_in_gate_width_units": {
                    "why": ("c_min is always finite, so 'fires at some c' is "
                            "vacuous. c_min(i)/4 states the firing amplitude in "
                            "units of the design's OWN 4.0*SE_diff gate width, "
                            "so a reader can see directly whether it is inside "
                            "or outside the range the design calls detectable."),
                    "per_cell_median_c_min_over_4": {
                        k: (res["cells"][k]["c_min_median"] / GATE_K
                            if res["cells"][k]["c_min_median"] is not None
                            else None) for k in res["cells"]},
                    "per_cell_min_c_min_over_4": {
                        k: (res["cells"][k]["c_min_min"] / GATE_K
                            if res["cells"][k]["c_min_min"] is not None
                            else None) for k in res["cells"]},
                    "per_cell_max_c_min_over_4": {
                        k: (res["cells"][k]["c_min_max"] / GATE_K
                            if res["cells"][k]["c_min_max"] is not None
                            else None) for k in res["cells"]},
                },
                "NC_B1_and_NC_B2": {
                    "why": ("a gate that fires with NO injection, or on a "
                            "REINFORCED DECREASE, is broken and its firings "
                            "would mean nothing"),
                    "NC_B1_violations_of_48": ncb1_fires,
                    "NC_B2_violations_of_48": ncb2_fires,
                },
            },
        },
        "direction_2_a_control_that_cannot_pass": {
            "the_arrangement": (
                "A positive control whose step selection places the injection "
                "where the injection cannot create the condition the gate "
                "tests. Then 'the gate is INADMISSIBLE' is a property of the "
                "selection rule, not a finding about the gate."),
            "THIS_IS_THE_ONE_THAT_ACTUALLY_HAPPENED": (
                "BATCH-a44d08 ran in exactly this arrangement. Its rule chose "
                "i = argmax_i SE_diff(A, t_i) over the 12 lower endpoints -- "
                "the injection's OWN denominator -- which is largest at the "
                "head of the descent where |Delta_i| is 11x to 26x the "
                "injection unit. At c = 6 the post-injection Delta was still "
                "NEGATIVE in three of four cells, so NO monotonicity violation "
                "of any size was ever presented to the gate, and a monotonicity "
                "gate declining to flag a net DECREASE is behaving CORRECTLY "
                "[quoted: validation_report.yaml item d; red_team_report.md "
                "section 2.3]. The INADMISSIBLE verdict was procedurally "
                "correct and says NOTHING about whether the gate CAN fire."),
            "guards_declared_in_advance_and_their_realized_values": {
                "guard_a_c_pos_printed_at_every_step": {
                    "why": ("the step's own REALITY threshold is on the page "
                            "beside its firing threshold"),
                    "realized": "printed at all 48 steps; see cells[*].steps[*].c_pos",
                    "per_cell_max_c_pos": {
                        k: max((s["c_pos"] for s in res["cells"][k]["steps"]
                                if not s["degenerate"]), default=None)
                        for k in res["cells"]},
                },
                "guard_b_closed_form_relation_verified_at_all_48": {
                    "why": ("every firing PROVABLY sits on a positive "
                            "post-injection Delta"),
                    "n_checked": res["closed_form_guarantee"]["n_steps_checked"],
                    "holds": res["closed_form_guarantee"]["holds_at_all_checked_steps"],
                    "min_margin": res["closed_form_guarantee"]
                                     ["min_margin_c_min_minus_c_pos"],
                    "min_post_injection_delta_at_c_min": res
                        ["closed_form_guarantee"]
                        ["min_post_injection_delta_at_c_min_over_48"],
                },
                "guard_c_there_is_no_step_selection_at_all": {
                    "why": ("no rule can place the control where the injection "
                            "cannot create the condition"),
                    "realized": ("all 12 steps of all 4 cells scored and "
                                 "reported; the frozen headline is a count over "
                                 "all 12; this file applies no argmax over any "
                                 "SE quantity"),
                },
            },
        },
        "direction_3_the_control_could_pass_trivially": {
            "the_arrangement": ("At a step with Delta_i > 0 the gate can fire "
                                "on the PRE-EXISTING INCREASE rather than on "
                                "the injection."),
            "guard": ("NC-B3 flags every such step and n_fire is reported BOTH "
                      "with and without them; PRED-B1 is scored on the full "
                      "table with the flagged count printed beside it."),
            "n_already_increasing_steps": n_inc_pooled,
            "n_fire_pooled_at_c6_with_them": pooled[str(PRED_B1_C)],
            "n_fire_pooled_at_c6_without_them": pooled_excl[str(PRED_B1_C)],
            "per_cell_with": per_cell_n_fire,
            "per_cell_without": per_cell_n_fire_excl,
        },
        "direction_4_the_reproduction_could_hide_a_defect": {
            "the_arrangement": ("If the regenerated family silently differs "
                                "from the committed one, c_min is computed on a "
                                "DIFFERENT OBJECT than the one BATCH-a44d08 "
                                "scored."),
            "guard": ("prereg 3.5's reproduction floor, re-verified BEFORE any "
                      "scoring, with the expected one-ULP d = 140 deviation "
                      "declared in advance and explicitly forbidden from being "
                      "rounded to 0.0."),
            "max_abs_dev_r_vs_committed_results_g3_json": r_dev_primary,
            "max_abs_dev_r_vs_BATCH_f19c37": r_dev_f19,
            "max_abs_dev_c_min_c_units": c_dev,
            "admissible": rep["admissibility"]["admissible"],
        },
        "residue_I_cannot_close": (
            "This run measures the POWER of one positive control on one "
            "recorded graded family at four cells, n = 8 draws, N = 2^20. A "
            "demonstration that a gate CAN fire at an INJECTED violation is NOT "
            "a demonstration that it fires at a REAL one. Nothing here "
            "establishes that AM-3 is adequate."),
    }

    res["what_this_does_not_reach"] = {
        "scope": ("the POWER of one positive control on one recorded graded "
                  "family at four cells (d in {100,140}, beta in {30,40}), "
                  "n = 8 draws, N = 2^20, q = 3329, CBD_{eta=2}"),
        "does_not": [
            "license anything about lattices in either direction",
            "rescore BATCH-a44d08, whose frozen INADMISSIBLE verdict stands",
            "reinstate any withheld BATCH-a44d08 reading; the four PARTIAL cell "
            "readings stay WITHHELD",
            "retire AM-3, which is NOT retired and NOT on trial for its life here",
            "establish that the AM-3 gate is adequate -- a demonstration that a "
            "gate CAN fire at an injected violation is not a demonstration that "
            "it fires at a real one",
            "offer any verdict as an AM-4 adjudication of a claim about a lattice",
            "cite anything from BATCH-a44d08's Section C, whose proposition "
            "stays OPEN IN BOTH DIRECTIONS",
            "bear on ML-KEM security, any FIPS 203 parameter set, any attack "
            "cost, or any cost model",
        ],
        "instrument_outcomes": ("INADMISSIBLE, INVALID and PARTIAL are "
                                "INSTRUMENT outcomes [carried]. Every "
                                "'0 violations' remains an UPPER BOUND at the "
                                "declared floor, never an absence."),
    }

    res["inference"] = {
        "requested_policy": "executor-implementation",
        "degraded_allowed": False,
        "fallback_allowed": False,
        "fallback_used": False,
        "degraded_requirements": [],
        "resolved": ("under the Claude Code runtime, per CLAUDE.md, per-role "
                     "model selection is process-level and subagents keep "
                     "model: inherit, so the resolved model is the session "
                     "model"),
        "resolved_model_id": None,
        "backend": None,
        "reasoning_effort": None,
        "model_verified": False,
        "model_verified_reason": ("no `python3 -m orchestration.adapter doctor "
                                  "--probe` receipt exists for this session"),
        "independent_session": ("procedural only -- separate session, no shared "
                                "scratch. NEVER model-level. AGENTS.md rule 12 "
                                "remains UNMET and UNWAIVED in this goal and is "
                                "recorded, not smoothed (prereg 5.10)."),
    }

    res["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    res["timings"]["total_wall_seconds"] = round(time.time() - t_start, 2)
    res["timings"]["total_cpu_core_seconds"] = round(cpu_seconds(), 2)
    res["timings"]["wall_budget_seconds"] = args.wall_budget_seconds
    res["peak_rss_gb"] = round(peak_rss_gb(), 3)
    res["memory_budget_gb"] = args.memory_budget_gb
    res["environment"] = {
        "python": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "numpy": np.__version__,
        "scipy": __import__("scipy").__version__,
        "gmpy2": "ABSENT (declared; nothing here depends on it)",
        "fpylll": "PRESENT but NOT USED by this run (no BKZ, no LLL)",
        "blas_threads_pinned_to_1": {
            v: os.environ.get(v) for v in
            ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS",
             "ACCELERATE_MAX_THREADS")},
    }

    signal.alarm(0)
    with open(args.out, "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=False)
        fh.write("\n")

    print()
    print("=" * 78)
    print("SUMMARY (observations only; no interpretation beyond prereg 3.5)")
    print(f"  prereg sha256 VERIFIED               : {ver['recomputed_sha256']}")
    print(f"  notarizing commit ancestor of HEAD   : "
          f"{ver['ancestry_is_ancestor_of_HEAD']} (asserted in "
          f"{ver['git_show_toplevel_from_repo_root']})")
    print(f"  seed-cache max |dev| vs results_g3   : {r_dev_primary!r}")
    print(f"  seed-cache max |dev| vs f19c37       : {r_dev_f19!r}")
    print(f"  c_min max |dev| (c units)            : {c_dev!r}")
    print(f"  reproduction ADMISSIBLE              : "
          f"{rep['admissibility']['admissible']}")
    print(f"  c_min(i) > c_pos(i) at all checked   : "
          f"{res['closed_form_guarantee']['holds_at_all_checked_steps']} "
          f"({n_gt}/{len(all_live)})")
    print(f"  n_fire(c=6) per cell                 : {per_cell_n_fire}")
    print(f"  n_fire(c=6) per cell, excl. already-increasing: "
          f"{per_cell_n_fire_excl}")
    print(f"  PRED-B1 (>= {PRED_B1_THRESHOLD} of 12 in EVERY cell)      : "
          f"{res['pred_b1']['outcome']}")
    print(f"  NC-B1 (c=0) violations of 48         : {ncb1_fires}")
    print(f"  NC-B2 (c=-6) violations of 48        : {ncb2_fires}")
    print(f"  steps with Delta_i > 0 (NC-B3)       : {n_inc_pooled} of "
          f"{len(all_live)}")
    print()
    print("  CAN THE AM-3 GATE FIRE:")
    print("    " + res["can_the_am3_gate_fire"]["PLAIN_STATEMENT_CAN_IT_FIRE"])
    print("  DID IT FIRE IN BATCH-a44d08 (a SEPARATE statement):")
    print("    " + res["can_the_am3_gate_fire"]
          ["PLAIN_STATEMENT_DID_IT_FIRE_IN_BATCH_a44d08"])
    print()
    print(f"  wall {res['timings']['total_wall_seconds']}s of "
          f"{args.wall_budget_seconds}s ; peak RSS {res['peak_rss_gb']} GB of "
          f"{args.memory_budget_gb} GB")
    print(f"  wrote {args.out}")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
