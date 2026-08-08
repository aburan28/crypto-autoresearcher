#!/usr/bin/env python3
"""
TASK-20260806-e17677 / BATCH-a44d08 / GOAL-MLKEM-005
AM-3 -- the AM-1 graded family re-run and scored under the NOTARIZED
replacement gate of Section B.

Governed by, and NOT modified by, this file:
  coordination/goals/GOAL-MLKEM-005/batches/BATCH-a44d08/tasks/
      TASK-20260806-843c40/prereg.md
  sha256 8d00ca3f0977e7367cfd10f4eb01cc0d4d24dfdc1ecf9739ba3cc299ee2a6c80
  notarized by TASK-20260806-0a1072 in commit
  9cb2d3e28ae7a474edbb116d694969470829e112, which is an ancestor of HEAD.

This script loads that file READ-ONLY, re-hashes it, compares against the
notarized receipt, the producer sidecar AND the blob inside the notarizing
commit itself, asserts `git merge-base --is-ancestor <notarizing commit> HEAD`
against the NOTARIZING COMMIT ITSELF (carried correction V-7, prereg 0.2),
and ABORTS on any mismatch.  It re-derives none of its thresholds and adds,
removes or re-spaces no grid point.

CARRIED VERBATIM from BATCH-f19c37 / TASK-20260806-ca4377 `measure.py` (which
carried it from BATCH-436ddd `b2a.py`): the four cells, q = 3329, CBD_{eta=2},
R = ||Q^T e||^2/||e||^2, the frozen empirical quantile estimator
q_emp(p) = sort(R)[round(p*N)-1] at N = 2^20, 8 draws per arm, GATE_K = 4.0,
SE_diff(A) = sqrt(sd_A^2/8 + sd_haar^2/8), every seed formula, the Haar null
arm, the 13-point AM-1 t grid, the graded path construction with (S_j, G_j)
drawn ONCE per (d,beta,j) BEFORE and independently of the t list, and the
chunked projection with chunk = 2^15 (the chunking is part of the RNG stream
and must be reproduced to regenerate the committed draws bitwise).

CHANGED, and only as prereg.md Section B freezes it:
  * G3 (withdrawn by DEC-20260806-14ac13) is REPLACED by the AM-3 gate of
    prereg 3.2.  The withdrawn 1.0 * SE_step_paired tolerance is NOT computed
    anywhere in this file, by design (task constraint 6; prereg 5.5).
  * the mandatory injected positive control of prereg 3.5 is run and reported
    for every c in {1,2,3,4,6}, with the frozen INADMISSIBLE branch.

NOT RUN, declared: NO NEW BKZ and no LLL.  The graded and Haar arms are pure
numpy.  The seed-cache reproduction is therefore re-verified in the two halves
that need no reduction (basis generation from seed_basis, and the whole graded
/ Haar arm), and the LLL/BKZ half is QUOTED from the committed record and
labelled as quoted, not re-run.

Observations only.  No status change, no evidence record, no interpretation
beyond the frozen verdicts of prereg 3.2.  Claim tier TOY: nothing here bears
on ML-KEM security, on any FIPS 203 parameter set, or on any attack cost.
This script performs no git write, makes no commit, and writes exactly one
file: results_g3.json inside its own task directory.
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
REPO_ROOT = os.path.normpath(os.path.join(BATCHES_DIR, "..", "..", "..", ".."))

PREREG_REL = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-a44d08/tasks/"
              "TASK-20260806-843c40/prereg.md")
PREREG_PATH = os.path.join(TASKS_DIR, "TASK-20260806-843c40", "prereg.md")
SIDECAR_PATH = os.path.join(TASKS_DIR, "TASK-20260806-843c40", "prereg_sha256.txt")
RECEIPT_PATH = os.path.join(BATCH_DIR, "archives", "TASK-20260806-0a1072",
                            "snapshot-receipt.json")

# The two constants the task card and the receipt both assert.  Hard-coded so
# that a tampered receipt cannot make the check pass.
EXPECTED_PREREG_SHA256 = \
    "8d00ca3f0977e7367cfd10f4eb01cc0d4d24dfdc1ecf9739ba3cc299ee2a6c80"
NOTARIZING_COMMIT = "9cb2d3e28ae7a474edbb116d694969470829e112"

PRIOR_F19 = os.path.join(BATCHES_DIR, "BATCH-f19c37", "tasks",
                         "TASK-20260806-ca4377", "results.json")
PRIOR_436 = os.path.join(BATCHES_DIR, "BATCH-436ddd", "tasks",
                         "TASK-20260806-09ec68", "b2a_results.json")

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

# ------------------------------------------- the FROZEN AM-3 gate, prereg 3.2/3.3
AM3_EPSILON_K = 1.0                       # epsilon_i = 1.0 * SE_diff(A, t_i)
AM3_T_CRIT = 4.2071245566046755           # t_{7,0.998}   [closed form]
AM3_ALPHA_PER_STEP = 0.002                # P(t_7 > t_crit)
AM3_FAMILY_STEPS = 12                     # 12 consecutive pairs of the 13-pt grid
AM3_FAMILY_CELLS = 4
AM3_FAMILY_SIZE = AM3_FAMILY_STEPS * AM3_FAMILY_CELLS          # = 48
AM3_DECLARED_FWER = 0.096                 # union bound 48 x 0.002
AM3_SIDAK_REFERENCE = 0.0916233087376801  # reported for comparison ONLY
POSITIVE_CONTROL_C = [1, 2, 3, 4, 6]      # prereg 3.5, frozen
POSITIVE_CONTROL_INADMISSIBLE_AT = 6      # frozen admissibility clause

# The withdrawn rule (DEC-20260806-14ac13, AM-1 G3 tie tolerance denominated in
# SE_step_paired) is NOT implemented in this file.  It is not computed, not
# reported, and not available to be reached for.  Recorded here as a statement
# a reader can verify by grepping this file.
WITHDRAWN_RULE_NOT_IMPLEMENTED = (
    "The withdrawn AM-1 G3 rule (|Delta| > 1.0 * SE_step_paired, no absolute "
    "floor, no multiplicity policy) is not implemented anywhere in this file. "
    "SE_step_paired appears ONLY as the denominator the frozen AM-3 statistic "
    "of prereg 3.2 specifies, which is the correct scale for a paired design "
    "and is a different object from the withdrawn RULE (prereg 3.6 item 3).")


def tkey(t):
    return f"{t:.4f}"


def arm_t(t):
    return f"graded_t{tkey(t)}"


# ====================================================================== seeds
def seed_basis(d, beta, i):
    return 700000 + d * 1000 + beta * 10 + i


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
    """Carried byte-for-byte, including the chunk size: the chunking IS part of
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
        cols.append(np.linalg.qr(g.standard_normal((d, beta)))[0].astype(np.float32))
    return np.concatenate(cols, axis=1)


def graded_paths(d, beta, n_draw=N_DRAW):
    """(S_j, G_j) drawn ONCE from seed_graded(d,beta,j), BEFORE and
    INDEPENDENTLY of the t list, and reused across every t, so the family is a
    path (prereg 1)."""
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
    """V = sum_a P_aa^2 - beta^2/d, deterministic, ZERO error draws.  Carried."""
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
    r = q_emp(2^-10) / q_Beta(2^-10).  Carried estimator, verbatim."""
    vals, ks = [], []
    for j in range(R.shape[1]):
        col = np.sort(R[:, j].astype(np.float64))
        q, k = emp_quantile(col, P_TAIL_10)
        vals.append(q / qb10)
        ks.append(k)
    a = np.array(vals, dtype=np.float64)
    return {"values": a.tolist(), "mean": float(a.mean()),
            "sd": float(a.std(ddof=1)), "order_stat_k": ks[0]}


def gate(arm_mean, arm_sd, haar_mean, haar_sd, k=GATE_K, n=N_DRAW):
    """prereg 1, carried verbatim.  NOTE, and every report in this batch states
    it: `4.0` is a NOMINAL FACTOR, NOT A P-VALUE.  The validator measured the
    realized one-sided false-positive rate of this gate at 0.0015-0.0025
    against a nominal 3e-5, a factor of about 60
    [quoted: BATCH-f19c37 validation_report.yaml item 4 / V-5]."""
    se = float(np.sqrt(arm_sd * arm_sd / n + haar_sd * haar_sd / n))
    shift = float(arm_mean - haar_mean)
    return {"arm_mean": arm_mean, "arm_sd": arm_sd,
            "haar_mean": haar_mean, "haar_sd": haar_sd,
            "n_draws_each": n, "se_of_difference": se,
            "shift_arm_minus_haar": shift,
            "shift_in_units_of_se_of_difference": (shift / se) if se > 0 else None,
            "threshold_k": k, "threshold_abs": k * se,
            "upper_bound_statement_if_not_cleared":
                f"|D| < {k:.1f} x SE_diff = {k * se:.6f} "
                f"(upper bound at {n} draws, N = 2^20)",
            "cleared": bool(se > 0 and abs(shift) >= k * se),
            "nominal_factor_disclosure":
                "4.0 is a nominal factor, not a p-value; realized one-sided "
                "false-positive rate measured at 0.0015-0.0025 against a "
                "nominal 3e-5 [quoted: BATCH-f19c37 validation_report item 4]"}


# ============================================ THE FROZEN AM-3 GATE (prereg 3.2)
def am3_score(t_values, means, values, se_diff):
    """prereg 3.2, implemented exactly as written and not otherwise.

      Delta_i    = m(t_{i+1}) - m(t_i)
      SE_step(i) = sd_j( r_j(t_{i+1}) - r_j(t_i) ) / sqrt(8)     [ddof=1, paired]
      epsilon_i  = 1.0 * SE_diff(A, t_i)
      STEP VIOLATION iff (Delta_i - epsilon_i)/SE_step(i) > t_crit,
                         t_crit = t_{7,0.998} = 4.2071245566046755

    Frozen degenerate handling: if SE_diff(A,t_i) == 0 use SE_diff(A,t_{i+1});
    if both are 0, or if SE_step(i) == 0, the step is flagged DEGENERATE and
    scored as a violation iff Delta_i > epsilon_i directly, with no division.
    """
    steps = []
    for i in range(len(means) - 1):
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
        if degenerate:
            stat = None
            violation = bool(delta > epsilon)
        else:
            stat = (delta - epsilon) / se_step
            violation = bool(stat > AM3_T_CRIT)

        steps.append({
            "i": i, "t_lo": t_values[i], "t_hi": t_values[i + 1],
            "m_t_lo": float(means[i]), "m_t_hi": float(means[i + 1]),
            "delta": delta,
            "is_increase": bool(delta > 0),
            "se_step_paired": se_step,
            "se_diff_at_t_lo": se_diff[i],
            "se_diff_at_t_hi": se_diff[i + 1],
            "epsilon": epsilon,
            "epsilon_source": eps_src,
            "am3_statistic": stat,
            "t_crit": AM3_T_CRIT,
            "degenerate": degenerate,
            "violation": violation,
            "se_step_over_se_diff": (se_step / se_diff[i]) if se_diff[i] > 0 else None,
            "delta_50pct_power_point":
                (epsilon + AM3_T_CRIT * se_step) if not degenerate else None,
        })

    viol = [s for s in steps if s["violation"]]
    incs = [s for s in steps if s["is_increase"]]
    if viol:
        outcome = "AM3-FAIL"
    elif incs:
        outcome = "AM3-TIE"
    else:
        outcome = "AM3-PASS"
    stats = [s["am3_statistic"] for s in steps if s["am3_statistic"] is not None]
    return {
        "rule": ("prereg 3.2 FROZEN: STEP VIOLATION iff "
                 "(Delta_i - 1.0*SE_diff(A,t_i))/SE_step_paired(i) > "
                 f"{AM3_T_CRIT}"),
        "t_crit": AM3_T_CRIT,
        "epsilon_k": AM3_EPSILON_K,
        "steps": steps,
        "n_steps": len(steps),
        "n_increases": len(incs),
        "n_violations": len(viol),
        "violating_step_indices": [s["i"] for s in viol],
        "max_am3_statistic": max(stats) if stats else None,
        "outcome": outcome,
    }


def cell_verdict(g1_clears, g2_fires, am3_outcome):
    """Validity table [carried, BATCH-f19c37 4.2] with AM3 in G3's place
    (prereg 3.2):
      G1 clears + G2 does not fire + AM3-PASS = VALID
      ...                          + AM3-TIE  = PARTIAL
      ...                          + AM3-FAIL = INVALID
      G1 fails, or G2 fires                   = INVALID
    INVALID is an INSTRUMENT OUTCOME and is never evidence about lattices in
    either direction."""
    if (not g1_clears) or g2_fires:
        return "INVALID"
    return {"AM3-PASS": "VALID", "AM3-TIE": "PARTIAL",
            "AM3-FAIL": "INVALID"}[am3_outcome]


# ============================ THE MANDATORY POSITIVE CONTROL (prereg 3.5, frozen)
def positive_control(t_values, values, haar_mean, haar_sd):
    """prereg 3.5, frozen:

      For each cell, take the recorded per-draw graded paths, add a constant
      c * SE_diff(A, t_i) to every draw at one grid point t_{i+1}, and re-score
      the AM-3 criterion, for c in {1,2,3,4,6} and for i = the step whose lower
      endpoint has the LARGEST SE_diff in that cell (the hardest step to flag,
      fixed by a data-independent rule).  Report the smallest c at which the
      cell returns AM3-FAIL.

      Frozen admissibility clause: if any cell fails to return AM3-FAIL at
      c = 6, the AM-3 gate is declared INADMISSIBLE for this goal and the
      demonstration reports that as its result, with no verdict on the real
      arms.

    The injection is arithmetic on already-recorded values.  It reduces no
    lattice, draws no error, and is not an additional measurement of any
    object."""
    n_steps = len(t_values) - 1
    se_diff_all = [gate(float(np.mean(values[i])), float(np.std(values[i], ddof=1)),
                        haar_mean, haar_sd)["se_of_difference"]
                   for i in range(len(t_values))]
    # data-independent rule: argmax over the 12 LOWER endpoints t_0..t_11
    lower_se = se_diff_all[:n_steps]
    i_hard = int(np.argmax(lower_se))
    inject_unit = se_diff_all[i_hard]

    runs = []
    smallest_fail_c = None
    for c in POSITIVE_CONTROL_C:
        inj_vals = [list(v) for v in values]
        inj_vals[i_hard + 1] = [v + c * inject_unit for v in inj_vals[i_hard + 1]]
        inj_means = [float(np.mean(v)) for v in inj_vals]
        inj_sds = [float(np.std(v, ddof=1)) for v in inj_vals]
        inj_se_diff = [gate(inj_means[i], inj_sds[i], haar_mean, haar_sd)
                       ["se_of_difference"] for i in range(len(t_values))]
        sc = am3_score(t_values, inj_means, inj_vals, inj_se_diff)
        tgt = sc["steps"][i_hard]
        runs.append({
            "c": c,
            "injected_at_grid_point_t": t_values[i_hard + 1],
            "injection_absolute": c * inject_unit,
            "target_step_i": i_hard,
            "target_step_delta": tgt["delta"],
            "target_step_epsilon": tgt["epsilon"],
            "target_step_se_step_paired": tgt["se_step_paired"],
            "target_step_am3_statistic": tgt["am3_statistic"],
            "target_step_violation": tgt["violation"],
            "cell_outcome": sc["outcome"],
            "n_violations_all_12_steps": sc["n_violations"],
            "violating_step_indices": sc["violating_step_indices"],
        })
        if sc["outcome"] == "AM3-FAIL" and smallest_fail_c is None:
            smallest_fail_c = c

    fails_at_6 = any(r["c"] == POSITIVE_CONTROL_INADMISSIBLE_AT
                     and r["cell_outcome"] == "AM3-FAIL" for r in runs)
    return {
        "rule": "prereg 3.5, frozen",
        "se_diff_per_grid_point": {tkey(t_values[i]): se_diff_all[i]
                                   for i in range(len(t_values))},
        "hardest_step_selection_rule":
            "argmax over the 12 LOWER endpoints t_0..t_11 of SE_diff(A, t_i); "
            "data-independent rule fixed by prereg 3.5 before any datum",
        "hardest_step_i": i_hard,
        "hardest_step_t_lo": t_values[i_hard],
        "hardest_step_t_hi": t_values[i_hard + 1],
        "hardest_step_se_diff_at_t_lo": inject_unit,
        "runs": runs,
        "smallest_c_returning_AM3_FAIL": smallest_fail_c,
        "returns_AM3_FAIL_at_c6": bool(fails_at_6),
    }


# ======================================================== reproduction checks
def repro_graded_and_haar(measured):
    """THE SEEDS ARE THE CACHE.  Compare every per-draw r value regenerated
    here against the committed BATCH-f19c37 record, bitwise.  Pure comparison
    of recorded numbers: no lattice, no reduction."""
    if not os.path.exists(PRIOR_F19):
        return {"status": f"NOT EVALUATED -- {PRIOR_F19} not found",
                "classification": "infrastructure, never a result"}
    pj = json.load(open(PRIOR_F19))
    rows, devs = [], []
    for (d, beta) in CELLS:
        key = f"d{d}_b{beta}"
        if key not in pj.get("cells", {}):
            continue
        old_cell = pj["cells"][key]
        old_haar = old_cell["arms_cbd"]["haar_null"]["ratio_p2em10_over_draws"]["values"]
        new_haar = measured[key]["haar_null"]["values"]
        dh = [abs(a - b) for a, b in zip(new_haar, old_haar)]
        devs.extend(dh)
        rows.append({"cell": key, "arm": "haar_null", "n_values": len(dh),
                     "max_abs_dev": max(dh), "bitwise_identical": max(dh) == 0.0})
        old_pt = old_cell["sensitivity_demonstration"]["per_t"]
        for t in GRADED_T:
            ov = old_pt[tkey(t)]["ratio_2em10_values"]
            nv = measured[key][arm_t(t)]["values"]
            dd = [abs(a - b) for a, b in zip(nv, ov)]
            devs.extend(dd)
            rows.append({"cell": key, "arm": arm_t(t), "n_values": len(dd),
                         "max_abs_dev": max(dd),
                         "bitwise_identical": max(dd) == 0.0})
    return {
        "source": ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-f19c37/"
                   "tasks/TASK-20260806-ca4377/results.json"),
        "what": ("every per-draw r = q_emp(2^-10)/q_Beta(2^-10) value of the "
                 "13 graded arms and the Haar null arm, in all four cells"),
        "n_values_compared": len(devs),
        "max_abs_deviation": max(devs) if devs else None,
        "all_bitwise_identical": bool(devs and max(devs) == 0.0),
        "per_arm": rows,
    }


def repro_shared_points_436(measured, haar_by_cell):
    """The six t shared with BATCH-436ddd.  That record stores means only, so
    the comparison is on means."""
    if not os.path.exists(PRIOR_436):
        return {"status": f"NOT EVALUATED -- {PRIOR_436} not found",
                "classification": "infrastructure, never a result"}
    pj = json.load(open(PRIOR_436))
    shared = [0.0, 0.05, 0.1, 0.25, 0.5, 1.0]
    rows, devs = [], []
    for (d, beta) in CELLS:
        key = f"d{d}_b{beta}"
        if key not in pj.get("cells", {}):
            continue
        old = pj["cells"][key]["sensitivity_demonstration"]["per_t"]
        for t in shared:
            ok = f"{t:.2f}"
            if ok not in old:
                continue
            dm = abs(measured[key][arm_t(t)]["mean"] - old[ok]["ratio_2em10_mean"])
            devs.append(dm)
            rows.append({"cell": key, "t": t,
                         "mean_this_run": measured[key][arm_t(t)]["mean"],
                         "mean_BATCH_436ddd": old[ok]["ratio_2em10_mean"],
                         "abs_dev": dm, "bitwise_identical": dm == 0.0})
    return {
        "source": ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-436ddd/"
                   "tasks/TASK-20260806-09ec68/b2a_results.json"),
        "what": "mean r at the six t shared with BATCH-436ddd, four cells",
        "n_values_compared": len(devs),
        "max_abs_deviation": max(devs) if devs else None,
        "all_bitwise_identical": bool(devs and max(devs) == 0.0),
        "rows": rows,
    }


def repro_basis_generation():
    """The half of the 32/32 seed-cache reproduction that needs NO reduction:
    regenerate the 32 UNREDUCED q-ary bases from seed_basis(d,beta,i) and
    compare ||b0||_raw and the raw GSO log2 slope against the committed
    metadata.  NO LLL and NO BKZ is run.  If fpylll is unavailable this is
    recorded as infrastructure, never as a result (AGENTS.md rule 3)."""
    out = {
        "what": ("32 unreduced q-ary bases regenerated from "
                 "seed_basis(d,beta,i) = 700000 + d*1000 + beta*10 + i via "
                 "FPLLL.set_random_seed + IntegerMatrix.random(d,'qary',"
                 "k=d//2,q=3329); compared on b0_norm_raw and "
                 "gso_log2_slope_raw against BATCH-f19c37's committed "
                 "reduction metadata."),
        "no_reduction_run": "NO LLL and NO BKZ is executed by this check.",
    }
    if not os.path.exists(PRIOR_F19):
        out["status"] = f"NOT EVALUATED -- {PRIOR_F19} not found"
        return out
    try:
        from fpylll import IntegerMatrix, FPLLL
        import fpylll as _f
        out["fpylll_version"] = _f.__version__
    except Exception as e:                                    # pragma: no cover
        out["status"] = f"NOT EVALUATED -- fpylll unavailable: {e!r}"
        out["classification"] = ("infrastructure signal, never negative "
                                 "mathematical evidence (AGENTS.md rule 3)")
        return out
    pj = {m["tag"]: m for m in json.load(open(PRIOR_F19))["reductions"]}
    rows, devs = [], []
    for (d, beta) in CELLS:
        for i in range(N_DRAW):
            tag = f"d{d}_b{beta}_i{i}"
            if tag not in pj:
                continue
            s = seed_basis(d, beta, i)
            FPLLL.set_random_seed(s)
            A = IntegerMatrix.random(d, "qary", k=d // 2, q=Q_MOD)
            M = np.array([[A[r, c] for c in range(d)] for r in range(d)],
                         dtype=np.float64)
            Rm = np.linalg.qr(M.T)[1]
            gs = np.abs(np.diag(Rm))
            b0 = float(gs[0])
            slope = float(np.polyfit(np.arange(d), np.log2(gs), 1)[0])
            p = pj[tag]
            rel = abs(b0 - p["b0_norm_raw"]) / p["b0_norm_raw"]
            sl = abs(slope - p["gso_log2_slope_raw"])
            devs.append(max(rel, sl))
            rows.append({"tag": tag, "fplll_seed": s,
                         "b0_norm_raw_rel_dev": rel,
                         "gso_log2_slope_raw_abs_dev": sl})
    out["n_compared"] = len(rows)
    out["max_b0_norm_raw_rel_dev"] = max((r["b0_norm_raw_rel_dev"] for r in rows),
                                         default=None)
    out["max_gso_log2_slope_raw_abs_dev"] = max(
        (r["gso_log2_slope_raw_abs_dev"] for r in rows), default=None)
    out["max_abs_deviation"] = max(devs) if devs else None
    out["per_tag"] = rows
    return out


def repro_reductions_quoted():
    """The LLL/BKZ half of the 32/32 figure.  NOT RE-RUN: task constraint 3
    forbids new BKZ.  QUOTED from the committed record and labelled quoted."""
    out = {"status": "NOT RE-RUN -- NO NEW BKZ (task constraint 3, batch thesis)",
           "classification": "quoted, not measured by this run"}
    if os.path.exists(PRIOR_F19):
        pj = json.load(open(PRIOR_F19))["instrument_checks"]
        for lab in ("reduction_reproduction_vs_BATCH_436ddd",
                    "reduction_reproduction_vs_BATCH_a51f91"):
            b = pj.get(lab)
            if isinstance(b, dict) and "n_compared" in b:
                out[lab] = {"n_compared": b["n_compared"],
                            "max_b0_norm_rel_dev": b["max_b0_norm_rel_dev"],
                            "max_gso_slope_abs_dev": b["max_gso_slope_abs_dev"]}
    out["quoted_figure"] = ("32 of 32 reductions at max deviation 0.0 against "
                            "both prior batches [quoted: EV-MLKEM-94c773; "
                            "BATCH-f19c37 results.json instrument_checks]")
    return out


# ======================== implementation check of the scorer (NOT a result)
def scorer_implementation_check():
    """A unit test of the FROZEN scorer against inputs whose correct AM-3
    outcome is known by construction.  This is an IMPLEMENTATION CHECK of the
    code, not a control, not a result, and NOT an alternative rule: it computes
    the same frozen statistic of prereg 3.2 on synthetic inputs.  It exists so
    that 'the gate returned X' is a statement about the gate rather than about
    a transcription error."""
    t = GRADED_T
    rng = np.random.default_rng(20260806)
    # (a) strictly decreasing, tiny noise -> must be AM3-PASS (no Delta > 0)
    base = np.linspace(1.10, 1.00, len(t))
    vals_a = [[float(base[i] - 1e-6 * j) for j in range(N_DRAW)]
              for i in range(len(t))]
    means_a = [float(np.mean(v)) for v in vals_a]
    se_a = [0.002] * len(t)
    ra = am3_score(t, means_a, vals_a, se_a)
    # (b) same, but with one huge injected increase -> must be AM3-FAIL
    vals_b = [list(v) for v in vals_a]
    vals_b[5] = [v + 1.0 for v in vals_b[5]]
    means_b = [float(np.mean(v)) for v in vals_b]
    rb = am3_score(t, means_b, vals_b, se_a)
    # (c) an increase far too small to clear t_crit -> must be AM3-TIE
    vals_c = [list(v) for v in vals_a]
    vals_c[5] = [v + (means_a[4] - means_a[5]) + 1e-9 + 1e-7 * rng.standard_normal()
                 for v in vals_c[5]]
    means_c = [float(np.mean(v)) for v in vals_c]
    rc = am3_score(t, means_c, vals_c, se_a)
    return {
        "status": "IMPLEMENTATION CHECK of the frozen scorer. NOT a result, "
                  "NOT a control, NOT an alternative rule.",
        "case_a_strictly_decreasing": {"expected": "AM3-PASS",
                                       "got": ra["outcome"],
                                       "ok": ra["outcome"] == "AM3-PASS"},
        "case_b_large_injected_increase": {"expected": "AM3-FAIL",
                                           "got": rb["outcome"],
                                           "ok": rb["outcome"] == "AM3-FAIL"},
        "case_c_negligible_increase": {"expected": "AM3-TIE",
                                       "got": rc["outcome"],
                                       "ok": rc["outcome"] == "AM3-TIE"},
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

    blob = sh(f"git show {NOTARIZING_COMMIT}:{PREREG_REL}")
    blob_sha = hashlib.sha256(blob.stdout.encode()).hexdigest() \
        if blob.returncode == 0 else None
    # exact bytes, not the text-decoded form
    blob_raw = subprocess.run(["git", "show", f"{NOTARIZING_COMMIT}:{PREREG_REL}"],
                              cwd=REPO_ROOT, capture_output=True)
    blob_sha = hashlib.sha256(blob_raw.stdout).hexdigest() \
        if blob_raw.returncode == 0 else None

    anc = sh(f"git merge-base --is-ancestor {NOTARIZING_COMMIT} HEAD")
    head = sh("git rev-parse HEAD").stdout.strip()
    dirty = sh("git status --porcelain").stdout.strip()
    follow = sh(f"git log --follow --format=%H -- {PREREG_REL}").stdout.split()

    ok = (got == EXPECTED_PREREG_SHA256
          and (sidecar is None or sidecar == got)
          and (receipt_path_sha is None or receipt_path_sha == got)
          and (receipt_field is None or receipt_field == got)
          and blob_sha == got
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
        "ancestry_check":
            f"git merge-base --is-ancestor {NOTARIZING_COMMIT} HEAD",
        "ancestry_check_asserts": ("the NOTARIZING COMMIT ITSELF, not its "
                                   "parent -- carried correction V-7, prereg 0.2"),
        "ancestry_is_ancestor_of_HEAD": bool(anc.returncode == 0),
        "head_commit": head,
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
    print("NOTARIZED PRE-REGISTRATION VERIFICATION (prereg 7; task constraint 1)")
    for k, v in ver.items():
        if k in ("git_log_follow_commits_touching_prereg", "worktree_dirty_paths"):
            print(f"  {k:44s}: {v if len(str(v)) < 200 else str(v)[:200] + ' ...'}")
        else:
            print(f"  {k:44s}: {v}")
    if not ver["match"]:
        print("ABORT: prereg.md sha256 / ancestry verification FAILED.")
        print("This is a harness failure, not a result. The run does not proceed.")
        return 2
    print("  VERIFIED. The frozen specification is loaded read-only and unmodified.")
    print(f"  AM-1 grid (13 pts, RETAINED, verbatim): {GRADED_T}")
    print(f"  AM-3 gate: (Delta_i - {AM3_EPSILON_K}*SE_diff(A,t_i))/SE_step_paired(i)"
          f" > {AM3_T_CRIT}")
    print(f"  declared family-wise false-failure rate: {AM3_DECLARED_FWER} "
          f"= {AM3_FAMILY_SIZE} x {AM3_ALPHA_PER_STEP} "
          f"({AM3_FAMILY_STEPS} steps x {AM3_FAMILY_CELLS} cells)")
    print(f"  positive control c in {POSITIVE_CONTROL_C}; INADMISSIBLE if any "
          f"cell does not FAIL at c = {POSITIVE_CONTROL_INADMISSIBLE_AT}")
    print("  NO NEW BKZ. NO LLL. Graded and Haar arms are pure numpy.")
    print("  " + WITHDRAWN_RULE_NOT_IMPLEMENTED)
    print("=" * 78)
    sys.stdout.flush()

    res = {
        "task_id": "TASK-20260806-e17677",
        "batch_id": "BATCH-a44d08",
        "goal_id": "GOAL-MLKEM-005",
        "section": "B",
        "role": "executor",
        "claim_tier": "toy",
        "claim_boundary": ("Nothing measured here bears on ML-KEM security, on "
                           "any FIPS 203 parameter set, on any attack cost, or "
                           "on any cost model. d <= 140, beta <= 40."),
        "governed_by": ("prereg.md of TASK-20260806-843c40, Section B, "
                        "notarized by TASK-20260806-0a1072 in commit "
                        + NOTARIZING_COMMIT),
        "prereg_verification": ver,
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "read_order": [
            "0. prereg.md loaded read-only, re-hashed against the task card "
            "constant, the sidecar, the notarized receipt AND the blob inside "
            "the notarizing commit; ancestry asserted against the notarizing "
            "commit itself",
            "1. graded + Haar arms regenerated FROM SEEDS (pure numpy, no BKZ, "
            "no LLL)",
            "2. seed-cache reproduction re-verified BEFORE any scoring",
            "3. G1 and G2 scored per cell, carried verbatim, reported SEPARATELY",
            "4. the frozen AM-3 gate scored per cell over 12 steps",
            "5. realized false-failure behaviour reported against the declared "
            "0.096",
            "6. the mandatory injected positive control, every c in {1,2,3,4,6}",
            "7. admissibility branch, then the could-not-fail demonstration",
        ],
        "frozen_am3_gate": {
            "source": "prereg.md Section 3.2 / 3.3, quoted",
            "delta": "Delta_i = m(t_{i+1}) - m(t_i), m(t) = mean_j r_A(2^-10)",
            "se_step": "SE_step(i) = sd_j( r_j(t_{i+1}) - r_j(t_i) )/sqrt(8), ddof=1, paired",
            "epsilon": f"epsilon_i = {AM3_EPSILON_K} * SE_diff(A, t_i)",
            "violation": "(Delta_i - epsilon_i)/SE_step(i) > t_crit",
            "t_crit": AM3_T_CRIT,
            "t_crit_label": "t_{7,0.998}  [closed form, scipy.stats.t]",
            "alpha_per_step": AM3_ALPHA_PER_STEP,
            "multiplicity_family": f"{AM3_FAMILY_STEPS} steps x "
                                   f"{AM3_FAMILY_CELLS} cells = {AM3_FAMILY_SIZE}",
            "declared_family_wise_false_failure_rate": AM3_DECLARED_FWER,
            "declared_rate_basis": "union bound, valid under ANY dependence "
                                   "among the 48 steps",
            "sidak_reference_not_the_declared_rate": AM3_SIDAK_REFERENCE,
            "G1_G2_not_in_family": ("G1 and G2 are carried per-cell gates, "
                                    "reported SEPARATELY, and are NOT in the "
                                    "AM-3 multiplicity family. No p-value or "
                                    "significance level is claimed for them."),
            "withdrawn_rule": WITHDRAWN_RULE_NOT_IMPLEMENTED,
        },
        "config": {"q": Q_MOD, "cells": CELLS, "graded_t": GRADED_T,
                   "errors_per_cell": N_ERR, "draws_per_arm": N_DRAW,
                   "chunk": CHUNK, "tail_level": "2^-10",
                   "estimator": "q_emp(p) = sort(R)[round(p*N)-1]; index 1023",
                   "gate_k": GATE_K},
        "seed_scheme": {
            "numpy_cbd_error_seed": "20260805 + d",
            "numpy_haar_seed": "900000 + d*1000 + beta*10 + j",
            "numpy_graded_seed": "500000 + d*1000 + beta*10 + j",
            "fplll_basis_seed_used_only_by_the_reproduction_check":
                "700000 + d*1000 + beta*10 + i",
            "note": "THE SEEDS ARE THE CACHE. No frame cache exists on disk.",
        },
        "instrument_checks": {},
        "seed_cache_reproduction": {},
        "cells": {},
        "am3_family": {},
        "positive_control": {},
        "timings": {},
    }

    # ------------------------------------- stage 1: regenerate the arms
    t1 = time.time()
    measured = {}
    frame_V_by_cell = {}
    errs = {}
    for d in sorted({dd for dd, _ in CELLS}):
        te = time.time()
        Ef, n2, chk = make_errors(d)
        errs[d] = (Ef, n2)
        res["instrument_checks"][f"cbd_pmf_d{d}"] = chk
        print(f"[errors] d={d}: 2^20 CBD_eta2 draws in {time.time() - te:.1f}s")
        sys.stdout.flush()

    for (d, beta) in CELLS:
        key = f"d{d}_b{beta}"
        tc = time.time()
        a, b = beta / 2.0, (d - beta) / 2.0
        qb10 = float(betaincinv(a, b, P_TAIL_10))
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
              f"(q_Beta(2^-10) = {qb10:.8f})")
        sys.stdout.flush()
        rss = peak_rss_gb()
        if rss > args.memory_budget_gb:
            raise MemoryError(
                f"peak RSS {rss:.2f} GB exceeds the {args.memory_budget_gb} GB "
                "budget -- RESOURCE EXHAUSTION, never a result")
    for d in list(errs):
        del errs[d]
    res["timings"]["stage1_arms_wall_seconds"] = round(time.time() - t1, 2)

    # ------------------- stage 2: seed-cache reproduction, BEFORE any scoring
    t2 = time.time()
    print("[repro] re-verifying the seed-cache reproduction BEFORE scoring "
          "anything (task constraint 3)")
    rep = {
        "why": ("Task constraint 3: the seeds are the cache; re-verify the "
                "reproduction before scoring anything and report the max "
                "deviation observed."),
        "graded_and_haar_arms_vs_BATCH_f19c37": repro_graded_and_haar(measured),
        "shared_points_vs_BATCH_436ddd": repro_shared_points_436(measured, None),
        "basis_generation_vs_BATCH_f19c37": repro_basis_generation(),
        "lll_bkz_half": repro_reductions_quoted(),
    }
    devs = [rep["graded_and_haar_arms_vs_BATCH_f19c37"].get("max_abs_deviation"),
            rep["shared_points_vs_BATCH_436ddd"].get("max_abs_deviation"),
            rep["basis_generation_vs_BATCH_f19c37"].get("max_abs_deviation")]
    devs = [x for x in devs if x is not None]
    rep["max_deviation_observed_over_all_re_run_checks"] = max(devs) if devs else None
    rep["scope_statement"] = (
        "The '32/32 reductions at max deviation 0.0' figure is a REDUCTION "
        "reproduction. Task constraint 3 forbids new BKZ, so its LLL/BKZ half "
        "is QUOTED, not re-run. What this run RE-VERIFIED is (i) the entire "
        "Section B measurement path -- every per-draw r value of all 13 graded "
        "arms and the Haar null arm in all four cells, regenerated from the "
        "seeds -- and (ii) the basis-generation half of the 32 reductions, "
        "which needs no reduction at all.")
    res["seed_cache_reproduction"] = rep
    res["timings"]["stage2_reproduction_wall_seconds"] = round(time.time() - t2, 2)
    g = rep["graded_and_haar_arms_vs_BATCH_f19c37"]
    print(f"[repro] graded+Haar per-draw r values: n={g.get('n_values_compared')} "
          f"max abs dev = {g.get('max_abs_deviation')}")
    s4 = rep["shared_points_vs_BATCH_436ddd"]
    print(f"[repro] BATCH-436ddd shared-point means: n={s4.get('n_values_compared')} "
          f"max abs dev = {s4.get('max_abs_deviation')}")
    bg = rep["basis_generation_vs_BATCH_f19c37"]
    print(f"[repro] basis generation (no reduction): n={bg.get('n_compared')} "
          f"max dev = {bg.get('max_abs_deviation')}  "
          f"{bg.get('status', 'OK')}")
    sys.stdout.flush()

    # ---------------------- stage 3: implementation check of the frozen scorer
    res["instrument_checks"]["scorer_implementation_check"] = \
        scorer_implementation_check()
    ic = res["instrument_checks"]["scorer_implementation_check"]
    print(f"[impl-check] scorer: a={ic['case_a_strictly_decreasing']['got']} "
          f"b={ic['case_b_large_injected_increase']['got']} "
          f"c={ic['case_c_negligible_increase']['got']}  "
          f"t_crit agrees={ic['t_crit_agrees']}")

    # ------------------------------------ stage 4: G1, G2, AM-3, per cell
    t4 = time.time()
    all_steps = []
    for (d, beta) in CELLS:
        key = f"d{d}_b{beta}"
        hm = measured[key]["haar_null"]["mean"]
        hs = measured[key]["haar_null"]["sd"]
        per_t, means, values, se_diff = {}, [], [], []
        for t in GRADED_T:
            arm = measured[key][arm_t(t)]
            gt = gate(arm["mean"], arm["sd"], hm, hs)
            per_t[tkey(t)] = {
                "t": t,
                "r_mean": arm["mean"], "r_sd": arm["sd"],
                "r_values": arm["values"],
                "order_stat_index_used": arm["order_stat_k"] - 1,
                "V": frame_V_by_cell[key][arm_t(t)],
                "gate": gt,
            }
            means.append(arm["mean"])
            values.append(arm["values"])
            se_diff.append(gt["se_of_difference"])

        G1_clears = bool(per_t[tkey(0.0)]["gate"]["cleared"])
        G2_fires = bool(per_t[tkey(1.0)]["gate"]["cleared"])
        am3 = am3_score(GRADED_T, means, values, se_diff)
        verdict = cell_verdict(G1_clears, G2_fires, am3["outcome"])
        for s in am3["steps"]:
            all_steps.append(dict(s, cell=key))

        pc = positive_control(GRADED_T, values, hm, hs)
        res["positive_control"][key] = pc

        res["cells"][key] = {
            "d": d, "beta": beta, "q": Q_MOD,
            "haar_null": {"r_mean": hm, "r_sd": hs,
                          "r_values": measured[key]["haar_null"]["values"],
                          "V": frame_V_by_cell[key]["haar_null"]},
            "per_t": per_t,
            "G1": {"definition": "the t = 0 arm CLEARS the 4.0 x SE_diff gate "
                                 "vs the Haar null [carried, BATCH-f19c37 4.2]",
                   "clears": G1_clears,
                   "shift_in_se": per_t[tkey(0.0)]["gate"]
                                       ["shift_in_units_of_se_of_difference"],
                   "in_am3_multiplicity_family": False},
            "G2": {"definition": "G2 FIRES iff the t = 1 arm CLEARS the gate; "
                                 "the design requires it NOT to fire "
                                 "[carried, BATCH-f19c37 4.2]",
                   "fires": G2_fires,
                   "does_not_fire": bool(not G2_fires),
                   "shift_in_se": per_t[tkey(1.0)]["gate"]
                                       ["shift_in_units_of_se_of_difference"],
                   "in_am3_multiplicity_family": False},
            "AM3": am3,
            "cell_verdict": verdict,
            "cell_verdict_rule": ("G1 clears + G2 does not fire + AM3-PASS = "
                                  "VALID; + AM3-TIE = PARTIAL; + AM3-FAIL = "
                                  "INVALID; G1 fails or G2 fires = INVALID. "
                                  "INVALID is an INSTRUMENT OUTCOME and is "
                                  "never evidence about lattices in either "
                                  "direction."),
            "dynamic_range_abs": float(means[0] - means[-1]),
            "dynamic_range_in_se_diff_at_t0":
                float((means[0] - means[-1]) / se_diff[0]) if se_diff[0] > 0 else None,
        }
        print(f"  [cell] {key}: G1_clears={G1_clears}  G2_fires={G2_fires}  "
              f"AM3={am3['outcome']} (incr {am3['n_increases']}/12, viol "
              f"{am3['n_violations']}/12, max stat "
              f"{am3['max_am3_statistic']:.4f}) -> {verdict}")
        print(f"         positive control: hardest step i={pc['hardest_step_i']} "
              f"(t {pc['hardest_step_t_lo']} -> {pc['hardest_step_t_hi']}, "
              f"SE_diff {pc['hardest_step_se_diff_at_t_lo']:.6g}); "
              f"outcomes " + ", ".join(f"c={r['c']}:{r['cell_outcome']}"
                                       for r in pc["runs"]))
        sys.stdout.flush()
    res["timings"]["stage4_scoring_wall_seconds"] = round(time.time() - t4, 2)

    # ------------------------ stage 5: the AM-3 family, realized vs declared
    n_viol = sum(1 for s in all_steps if s["violation"])
    n_inc = sum(1 for s in all_steps if s["is_increase"])
    stats = [s["am3_statistic"] for s in all_steps
             if s["am3_statistic"] is not None]
    eps_all = [s["epsilon"] for s in all_steps]
    ratios = [s["se_step_over_se_diff"] for s in all_steps
              if s["se_step_over_se_diff"] is not None]
    res["am3_family"] = {
        "declared_before_any_data": {
            "per_step_alpha": AM3_ALPHA_PER_STEP,
            "family": f"{AM3_FAMILY_STEPS} steps x {AM3_FAMILY_CELLS} cells "
                      f"= {AM3_FAMILY_SIZE} comparisons",
            "family_wise_false_failure_rate_on_a_flawless_instrument":
                AM3_DECLARED_FWER,
            "basis": "union bound 48 x 0.002 = 0.096, valid under ANY "
                     "dependence; steps sharing an endpoint are dependent",
            "sidak_reference_only": AM3_SIDAK_REFERENCE,
            "flawless_instrument_definition":
                "the true mean curve m(t) is non-increasing in t (true "
                "Delta_i <= 0 at every step) and the paired per-draw "
                "differences are exchangeable across the 8 draws (prereg 3.3)",
        },
        "realized": {
            "n_comparisons_scored": len(all_steps),
            "n_steps_with_delta_gt_0": n_inc,
            "n_step_violations": n_viol,
            "violations": [{"cell": s["cell"], "i": s["i"], "t_lo": s["t_lo"],
                            "t_hi": s["t_hi"], "delta": s["delta"],
                            "epsilon": s["epsilon"],
                            "se_step_paired": s["se_step_paired"],
                            "am3_statistic": s["am3_statistic"]}
                           for s in all_steps if s["violation"]],
            "max_am3_statistic_over_family": max(stats) if stats else None,
            "max_am3_statistic_cell_and_step": max(
                ((s["am3_statistic"], s["cell"], s["i"]) for s in all_steps
                 if s["am3_statistic"] is not None), default=None),
            "n_degenerate_steps": sum(1 for s in all_steps if s["degenerate"]),
            "min_epsilon_over_family": min(eps_all) if eps_all else None,
            "all_epsilon_nonnegative": bool(all(e >= 0.0 for e in eps_all)),
            "se_step_over_se_diff_min": min(ratios) if ratios else None,
            "se_step_over_se_diff_median":
                float(np.median(ratios)) if ratios else None,
            "se_step_over_se_diff_max": max(ratios) if ratios else None,
            "expected_violation_count_under_flawless_instrument_upper_bound":
                AM3_FAMILY_SIZE * AM3_ALPHA_PER_STEP,
        },
        "reading_discipline": (
            "The declared 0.096 is an UPPER BOUND on P(at least one VIOLATION "
            "| flawless instrument). The realized counts below are what the "
            "48 frozen comparisons returned on this run's data. A realized "
            "count is not an estimate of a rate: one run yields one Bernoulli "
            "draw of the family-wise event, and the observed count bounds "
            "nothing about the instrument unless the instrument is flawless in "
            "prereg 3.3's sense. Reported, not interpreted. Whether the "
            "instrument is flawless is not something this run can establish "
            "and is not claimed."),
        "power_operating_point_conditional": (
            "prereg 3.4 states Delta_50% = epsilon_i + t_crit * SE_step(i), "
            "and its numeric form 2.52-2.77 x SE_diff is CONDITIONAL on the "
            "measured SE_step/SE_diff ratio 0.3599-0.4228 recurring. The "
            "realized ratios of this run are reported above so the condition "
            "is checkable. The false-failure rate of prereg 3.3 is NOT "
            "conditional on it."),
    }

    # --------------------------------- stage 6: admissibility, then verdicts
    per_cell_c6 = {k: v["returns_AM3_FAIL_at_c6"]
                   for k, v in res["positive_control"].items()}
    admissible = all(per_cell_c6.values())
    res["positive_control_summary"] = {
        "rule": "prereg 3.5, frozen",
        "c_grid": POSITIVE_CONTROL_C,
        "returns_AM3_FAIL_at_c6_per_cell": per_cell_c6,
        "smallest_c_returning_AM3_FAIL_per_cell":
            {k: v["smallest_c_returning_AM3_FAIL"]
             for k, v in res["positive_control"].items()},
        "gate_admissible": bool(admissible),
        "admissibility_clause": (
            "If any cell fails to return AM3-FAIL at c = 6, the AM-3 gate is "
            "declared INADMISSIBLE for this goal and the demonstration reports "
            "that as its result, with no verdict on the real arms."),
        "caveat_if_real_data_already_fails": (
            "Where a cell's UNINJECTED AM-3 outcome is already AM3-FAIL, the "
            "injected control cannot separate 'the gate fires because of the "
            "injection' from 'the gate was already firing'. The uninjected "
            "outcome per cell is recorded beside the control for exactly this "
            "reason, and the control is additionally reported at the level of "
            "the TARGET STEP -- target_step_violation and its statistic -- "
            "which does isolate the injected step."),
    }
    for key in res["cells"]:
        res["positive_control"][key]["uninjected_cell_outcome"] = \
            res["cells"][key]["AM3"]["outcome"]
        res["positive_control"][key]["uninjected_target_step"] = next(
            (s for s in res["cells"][key]["AM3"]["steps"]
             if s["i"] == res["positive_control"][key]["hardest_step_i"]), None)

    severity = {"VALID": 0, "PARTIAL": 1, "INVALID": 2}
    cell_verdicts = {k: v["cell_verdict"] for k, v in res["cells"].items()}
    overall = max(cell_verdicts.values(), key=lambda v: severity[v])
    res["overall"] = {
        "per_cell_verdict": cell_verdicts,
        "overall_verdict": overall,
        "rule": "the overall verdict is the MOST SEVERE cell verdict (prereg 3.2)",
        "gate_admissible": bool(admissible),
        "if_inadmissible": ("If gate_admissible is false, prereg 3.5 makes THE "
                            "INADMISSIBILITY the run's result and no verdict on "
                            "the real arms stands."),
        "instrument_outcome_statement": (
            "VALID / PARTIAL / INVALID is a statement about the INSTRUMENT. "
            "INVALID is never evidence about lattices in either direction, and "
            "a VALID or PARTIAL verdict licenses only what G1, G2 and "
            "monotonicity license about the instrument. It adjudicates no law. "
            "EV-MLKEM-94c773 records that this instrument at 8 draws is 9-13x "
            "too coarse to resolve the residual that survives reduction "
            "[quoted: BATCH-f19c37 validation_report item 5]; a new gate does "
            "not change that."),
    }

    # ------------------------------------- stage 7: could-not-fail disclosure
    res["could_not_fail_demonstration"] = {
        "named_by_the_prereg": {
            "section": "prereg 3.6",
            "form_1": ("The mirror of AM-1: setting alpha and epsilon so loose "
                       "that no real path can ever violate, so that 'the "
                       "instrument is VALID' becomes a property of the gate "
                       "exactly as 'INVALID' was a property of the withdrawn "
                       "gate."),
            "form_2": ("The AM-3 loophole: declaring a rate that is secretly "
                       "conditional on a nuisance quantity the run supplies, so "
                       "the declaration is not a pre-registration at all."),
        },
        "against_form_1_mechanical": {
            "test": "the mandatory injected positive control of prereg 3.5, on "
                    "this batch's own recorded data, at the HARDEST step per "
                    "cell chosen by the data-independent argmax-SE_diff rule",
            "smallest_c_returning_AM3_FAIL_per_cell":
                {k: v["smallest_c_returning_AM3_FAIL"]
                 for k, v in res["positive_control"].items()},
            "target_step_violation_per_cell_per_c":
                {k: {r["c"]: r["target_step_violation"] for r in v["runs"]}
                 for k, v in res["positive_control"].items()},
            "gate_admissible": bool(admissible),
        },
        "against_form_2_mechanical": {
            "claim": ("The declared 0.096 is a function of t_crit and the "
                      "family size alone: 48 x P(t_7 > 4.2071245566046755) = "
                      "48 x 0.002. No measured quantity enters it."),
            "recomputed_alpha_from_t_crit_only":
                float(student_t.sf(AM3_T_CRIT, 7)),
            "recomputed_union_bound": AM3_FAMILY_SIZE * float(
                student_t.sf(AM3_T_CRIT, 7)),
            "declared": AM3_DECLARED_FWER,
            "bound_step_requires_only": "epsilon_i >= 0 pointwise",
            "min_epsilon_observed_over_the_48": min(eps_all) if eps_all else None,
            "all_epsilon_nonnegative_observed":
                bool(all(e >= 0.0 for e in eps_all)),
            "conditional_statement_kept_separate": (
                "prereg 3.4's power figure IS conditional on the measured "
                "SE_step/SE_diff ratio and is labelled conditional; the "
                "realized ratios are reported so the condition is checkable."),
        },
        "the_arrangement_in_which_THIS_RUN_could_not_fail": {
            "named": (
                "A re-run that (i) re-derived the gate from the data it then "
                "scores, or (ii) scored only the injected positive control and "
                "not the real arms, or (iii) chose the 'hardest' step after "
                "seeing where the gate fires most easily, or (iv) quietly "
                "computed the withdrawn SE_step_paired tolerance and reported "
                "whichever verdict read better. Any of these makes the reported "
                "verdict a property of the run rather than of the frozen gate."),
            "why_this_run_is_not_in_it": [
                "(i) Every threshold is a module-level literal in measure_g3.py "
                "-- AM3_T_CRIT, AM3_EPSILON_K, GRADED_T, GATE_K, "
                "POSITIVE_CONTROL_C -- transcribed from a prereg.md whose "
                "sha256 is checked against the task card constant, the producer "
                "sidecar, the notarized receipt and the blob inside the "
                "notarizing commit, with the run aborting on mismatch. The "
                "ordering is a property of the git record.",
                "(ii) The real arms and the injected control are both scored "
                "and both reported, and the uninjected cell outcome is recorded "
                "beside every control run.",
                "(iii) The hardest step is argmax over the 12 LOWER endpoints "
                "of SE_diff(A,t_i) -- a rule frozen in prereg 3.5 before any "
                "datum of this batch existed. The full SE_diff table for all 13 "
                "grid points is recorded so the argmax is checkable by a "
                "reader.",
                "(iv) The withdrawn rule is not implemented in this file. "
                "SE_step_paired appears only as the denominator the frozen AM-3 "
                "statistic specifies. No post-hoc alternative rule is computed "
                "and none is presented beside the verdict.",
            ],
            "residue_this_run_cannot_close": (
                "This run cannot close off-repository pre-computation, and it "
                "cannot make its own reading of the prereg independent of the "
                "prereg's author's intent. It also inherits every limit of the "
                "instrument: presentation-dependence of V (prereg 1.1), the "
                "8-draw coarseness, and the fact that a criterion with a "
                "correct false-failure rate is still only a criterion about "
                "this instrument."),
        },
    }

    res["what_this_does_not_reach"] = [
        "Claim tier TOY, unconditionally. No number here transports to "
        "beta = 606, d = 1420, any FIPS 203 parameter set, any attack cost, or "
        "any other parameter set, by extrapolation or by analogy.",
        "No status change, no hypothesis movement, no evidence record. This is "
        "an executor artifact of observations.",
        "No interpretation beyond the frozen verdicts of prereg 3.2 and the "
        "frozen admissibility branch of prereg 3.5.",
        "No AM-4 adjudicator claim. V is presentation-dependent (prereg 1.1) "
        "and no verdict here adjudicates a claim about a lattice.",
        "Independence in this batch is PROCEDURAL -- separate sessions, no "
        "shared scratch, snapshot before review -- and never model-level.",
        "Every non-clearing arm is reported as an upper bound |D| < 4.0 x "
        "SE_diff = <number> at 8 draws, N = 2^20. No arm is described as "
        "'absent', 'no departure', 'vanishing' or 'consistent with zero'.",
    ]

    res["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    res["timings"]["total_wall_seconds"] = round(time.time() - t_start, 2)
    res["timings"]["total_cpu_core_seconds"] = round(cpu_seconds(), 2)
    res["timings"]["wall_budget_seconds"] = args.wall_budget_seconds
    res["peak_rss_gb"] = round(peak_rss_gb(), 3)
    res["memory_budget_gb"] = args.memory_budget_gb
    res["environment"] = {
        "python": sys.version, "platform": platform.platform(),
        "machine": platform.machine(), "numpy": np.__version__,
        "scipy": __import__("scipy").__version__,
        "blas_threads_pinned_to_1": {
            k: os.environ.get(k) for k in
            ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS",
             "ACCELERATE_MAX_THREADS")},
    }

    signal.alarm(0)
    with open(args.out, "w") as f:
        json.dump(res, f, indent=1, sort_keys=False)
    print("=" * 78)
    print(f"per-cell verdicts : {cell_verdicts}")
    print(f"overall verdict   : {overall}  (most severe cell verdict)")
    print(f"gate admissible   : {admissible}")
    print(f"AM-3 family       : {n_viol} violations / {len(all_steps)} "
          f"comparisons; {n_inc} steps with Delta > 0")
    print(f"declared FWER     : {AM3_DECLARED_FWER} (union bound 48 x 0.002)")
    print(f"wrote {args.out}  wall {res['timings']['total_wall_seconds']}s  "
          f"peak RSS {res['peak_rss_gb']} GB")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
