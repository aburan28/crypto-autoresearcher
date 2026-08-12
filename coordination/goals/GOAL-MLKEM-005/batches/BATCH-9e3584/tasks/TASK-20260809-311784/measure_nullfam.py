#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TASK-20260809-311784 / BATCH-9e3584 / GOAL-MLKEM-005
SECTION B' of the notarized pre-registration -- AM-13's NULL FAMILY.

  prereg  coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/
          TASK-20260809-4011dd/prereg.md
  sha256  190cf4740b0ecefdbe7d1da0868a6258352b044ae5e99da470060f94049c70ea
  notarized by TASK-20260809-91cf76 in commit
  1aa7db5313f6d3da1f366443d4d6066597393402

WHAT THIS BUILDS.  The 13 grid points of the AM-1 t grid are regenerated as 13
INDEPENDENT HAAR FRAMES from the carried seeds, so that E[Delta_i] = 0 at EVERY
step.  Everything downstream -- errors, projection, chunking, quantile
estimator, n_draw, SE construction, t_crit, GATE_K and the c grid -- is CARRIED
BYTE-FOR-BYTE from BATCH-cbe023 measure_g3.py.  The null family therefore
differs from the graded family in EXACTLY ONE respect: the frames at
consecutive grid points are drawn independently instead of from a shared
(S_j, G_j) path.

PURE NUMPY.  NO BKZ.  NO LLL.  NO REDUCTION OF ANY KIND.

CLAIM TIER: TOY.  Nothing here bears on ML-KEM security, on any FIPS 203
parameter set, on any attack cost, or on any cost model.

certificate.kind: none -- no discrete-log solve and no factor-base relation is
claimed or produced.

This script writes exactly one file: results_nullfam.json, in its own task
directory.  It performs no git write and makes no commit.
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

# --------------------------------------------------- carried constants [carried]
Q_MOD = 3329
P_TAIL_10 = 2.0 ** -10
CELLS = [(100, 30), (100, 40), (140, 30), (140, 40)]
GATE_K = 4.0
N_DRAW = 8
N_ERR = 1 << 20
CHUNK = 1 << 15
GRADED_T = [0.0, 0.0025, 0.005, 0.0075, 0.01, 0.015, 0.02, 0.03,
            0.05, 0.1, 0.25, 0.5, 1.0]
AM3_EPSILON_K = 1.0
AM3_T_CRIT = 4.2071245566046755          # t_{7,0.998}   [carried, closed form]
C_GRID = [0, 1, 2, 3, 4, 6, 8, 12, 16, 24, 32]
C_NEG_CONTROL = -6
PRED_B1_C = 6
S1_STEPS = list(range(5, 12))
S2_FLATNESS_K = 1.0

# --------------------------------------------- Section B' own frozen constants
# prereg 3.1: the seed formula for the 13-frame family, declared BEFORE any draw
# and disclosed as a COMPLETION -- the carried seed table has no such entry
# because no such family was ever built.
def seed_nullfam(d, beta, j, m):
    return 700000 + d * 1000 + beta * 10 + j + 100000 * (m + 1)


MATERIALLY_BELOW = 8            # prereg 3.3 / 6, set before any datum
FAMILY_SIZE = 48                # 4 cells x 12 steps  [carried]

# Quoted counts.  BOTH must appear in the same sentence as the headline
# (binding carry 4 / prereg 3.2).
COMMITTED_REAL_N_FIRE_C6 = 29           # [quoted: BATCH-cbe023 results_g3.json]
RED_TEAM_EXACT_NULL_N_FIRE_C6 = 47      # [quoted: red_team_report.md RT-B2]
RED_TEAM_EXACT_NULL_PER_CELL = [12, 11, 12, 12]
RED_TEAM_EXACT_NULL_C4 = 42
RED_TEAM_EXACT_NULL_CMIN_MEDIAN = 2.99


# ============================================================ prereg gate
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
        raise SystemExit("ABORT: repo root mismatch %r vs %r" % (top, REPO_ROOT))
    out["repo_root_verified"] = True
    live = sha256_file(PREREG_PATH)
    sidecar = open(SIDECAR_PATH).read().split()[0]
    blob_oid = git("rev-parse", "%s:%s" % (NOTARIZING_COMMIT, PREREG_REL))
    raw = subprocess.check_output(("git", "cat-file", "blob", blob_oid),
                                  cwd=REPO_ROOT)
    blob_sha = hashlib.sha256(raw).hexdigest()
    parent = git("rev-parse", "%s^" % NOTARIZING_COMMIT)
    absent = git("cat-file", "-e", "%s:%s" % (parent, PREREG_REL)).startswith(
        "GIT ERROR")
    out.update({"sha256_working_tree": live, "sha256_sidecar": sidecar,
                "sha256_task_card_constant": PREREG_SHA256_EXPECTED,
                "sha256_notarized_blob": blob_sha,
                "notarizing_commit": NOTARIZING_COMMIT,
                "notarizing_commit_parent": parent,
                "negative_test_absent_at_parent": absent,
                "is_ancestor_of_HEAD": subprocess.call(
                    ("git", "merge-base", "--is-ancestor", NOTARIZING_COMMIT,
                     "HEAD"), cwd=REPO_ROOT, stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL) == 0})
    out["ALL_FOUR_AGREE"] = (live == sidecar == PREREG_SHA256_EXPECTED
                             == blob_sha)
    if not out["ALL_FOUR_AGREE"]:
        raise SystemExit("ABORT: prereg sha256 mismatch %s" % json.dumps(out))
    if not absent:
        raise SystemExit("ABORT: frozen text present at the notarizing parent")
    if not out["is_ancestor_of_HEAD"]:
        raise SystemExit("ABORT: notarizing commit is not an ancestor of HEAD")
    return out


# ============================================ carried pipeline, byte-for-byte
def seed_error(d):
    return 20260805 + d


def seed_haar(d, beta, j):
    return 900000 + d * 1000 + beta * 10 + j


_POPCNT4 = np.array([bin(v).count("1") for v in range(16)], dtype=np.int8)


def cbd_eta2(rng, n, d):
    r = rng.integers(0, 16, size=(n, d), dtype=np.uint8)
    return (_POPCNT4[r & 3] - _POPCNT4[r >> 2]).astype(np.int8)


def make_errors(d, n_err=N_ERR, chunk=CHUNK):
    """CARRIED BYTE-FOR-BYTE INCLUDING THE CHUNK SIZE: the chunking IS part of
    the RNG consumption order."""
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
    return Ef, n2, {
        "measured_pmf": pm.tolist(),
        "exact_fips203_cbd_eta2": [1 / 16, 4 / 16, 6 / 16, 4 / 16, 1 / 16],
        "measured_per_coordinate_variance":
            float(sum(pm[i] * (i - 2) ** 2 for i in range(5))),
        "exact_per_coordinate_variance": 1.0}


def haar_frames(d, beta, n_draw=N_DRAW):
    """The carried Haar NULL ARM, seed_haar(d,beta,j).  Unchanged."""
    cols = []
    for j in range(n_draw):
        g = np.random.default_rng(seed_haar(d, beta, j))
        cols.append(np.linalg.qr(g.standard_normal((d, beta)))[0]
                    .astype(np.float32))
    return np.concatenate(cols, axis=1)


def nullfam_frames(d, beta, m, n_draw=N_DRAW):
    """THE ONE THING THAT CHANGES.  Grid point m is an INDEPENDENT Haar frame
    stack, drawn from seed_nullfam(d,beta,j,m).  Consecutive grid points share
    NOTHING, so E[Delta_i] = 0 at every step by construction.  Pure numpy; no
    reduction of any kind."""
    cols = []
    for j in range(n_draw):
        g = np.random.default_rng(seed_nullfam(d, beta, j, m))
        cols.append(np.linalg.qr(g.standard_normal((d, beta)))[0]
                    .astype(np.float32))
    return np.concatenate(cols, axis=1)


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
    return float(np.sqrt(arm_sd * arm_sd / n + haar_sd * haar_sd / n))


def closed_form_step(i, t_values, means, values, se_diff):
    """CARRIED VERBATIM from BATCH-cbe023 measure_g3.py, including the frozen
    degenerate handling.  NO DIVISION BY ZERO IS PERFORMED."""
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
    row = {"i": i, "t_lo": t_values[i], "t_hi": t_values[i + 1],
           "m_t_lo": float(means[i]), "m_t_hi": float(means[i + 1]),
           "delta": delta, "se_step_paired": se_step,
           "se_diff_at_t_lo": se_diff[i], "se_diff_at_t_hi": se_diff[i + 1],
           "injection_unit_se_diff": eps_base, "epsilon": epsilon,
           "epsilon_source": eps_src, "t_crit": AM3_T_CRIT,
           "degenerate": degenerate, "degenerate_reason": None,
           "flag_delta_gt_0_in_raw_data": bool(delta > 0.0)}
    if degenerate:
        row["degenerate_reason"] = (
            "SE_diff(t_i) and SE_diff(t_{i+1}) both 0" if eps_base == 0.0
            else "SE_step(i) == 0")
        row["c_min"] = row["c_pos"] = None
        row["fires"] = {str(c): None for c in C_GRID}
        row["excluded_from_counts"] = True
        return row
    c_min = 1.0 + (AM3_T_CRIT * se_step - delta) / eps_base
    c_pos = max(0.0, -delta / eps_base)
    row["c_pos"] = c_pos
    row["c_min"] = c_min
    row["c_min_over_4"] = c_min / GATE_K
    row["se_step_over_se_diff"] = se_step / eps_base
    row["flag_near_flat_S2"] = bool(abs(delta) <= S2_FLATNESS_K * eps_base)
    row["excluded_from_counts"] = False
    pid, fires, stats = {}, {}, {}
    for c in C_GRID:
        pid[str(c)] = delta + c * eps_base
        s_c = (delta + (c - 1.0) * eps_base) / se_step
        stats[str(c)] = s_c
        fires[str(c)] = bool(s_c > AM3_T_CRIT)
    row["post_injection_delta"] = pid
    row["am3_statistic"] = stats
    row["fires"] = fires
    row["am3_statistic_at_c_neg6"] = \
        (delta + (C_NEG_CONTROL - 1.0) * eps_base) / se_step
    row["fires_at_c_neg6"] = bool(row["am3_statistic_at_c_neg6"] > AM3_T_CRIT)
    return row


def score_cell(t_values, means, values, se_diff):
    steps = [closed_form_step(i, t_values, means, values, se_diff)
             for i in range(len(means) - 1)]
    live = [s for s in steps if not s["degenerate"]]
    n_fire = {str(c): int(sum(1 for s in live if s["c_min"] <= c))
              for c in C_GRID}
    n_fire_by_stat = {str(c): int(sum(1 for s in live if s["fires"][str(c)]))
                      for c in C_GRID}
    cmins = [s["c_min"] for s in live]
    s1 = [s["c_min"] for s in live if s["i"] in S1_STEPS]
    return {"steps": steps, "n_steps": len(steps),
            "n_degenerate": len(steps) - len(live),
            "n_steps_with_delta_gt_0":
                int(sum(s["flag_delta_gt_0_in_raw_data"] for s in live)),
            "n_fire": n_fire,
            "n_fire_recomputed_from_statistic": n_fire_by_stat,
            "n_fire_definitions_agree": bool(n_fire == n_fire_by_stat),
            "n_fire_at_c_neg6": int(sum(s["fires_at_c_neg6"] for s in live)),
            "c_min_min": min(cmins) if cmins else None,
            "c_min_median": float(np.median(cmins)) if cmins else None,
            "c_min_max": max(cmins) if cmins else None,
            "c_min_over_4_median":
                float(np.median([c / GATE_K for c in cmins])) if cmins else None,
            "se_step_over_se_diff_median": float(np.median(
                [s["se_step_over_se_diff"] for s in live])) if live else None,
            "mean_delta": float(np.mean([s["delta"] for s in live]))
            if live else None,
            "sd_delta": float(np.std([s["delta"] for s in live], ddof=1))
            if len(live) > 1 else None,
            "S1_median_c_min_DATA_INDEPENDENT":
                float(np.median(s1)) if s1 else None}


# ============================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    from scipy.special import betaincinv

    RES = OrderedDict()
    RES.update({"task_id": "TASK-20260809-311784", "batch_id": "BATCH-9e3584",
                "goal_id": "GOAL-MLKEM-005", "role": "executor",
                "section": "B' -- AM-13 NULL FAMILY", "claim_tier": "toy"})
    RES["certificate"] = {"kind": "none",
                          "reason": "no discrete-log solve and no factor-base "
                                    "relation is claimed or produced"}
    RES["governed_by"] = {"prereg": PREREG_REL,
                          "sha256": PREREG_SHA256_EXPECTED,
                          "notarizing_commit": NOTARIZING_COMMIT}

    print("=" * 78)
    print("SECTION B' -- AM-13 NULL FAMILY   BATCH-9e3584 / TASK-20260809-311784")
    print("13 INDEPENDENT Haar frames per cell.  PURE NUMPY, NO BKZ, NO LLL,")
    print("NO REDUCTION OF ANY KIND.  CLAIM TIER: TOY.")
    print("=" * 78)

    print("\n[0] prereg notarization gate -- ABORT ON MISMATCH")
    RES["prereg_verification"] = verify_prereg()
    print("    ALL FOUR AGREE: %s   absent at parent: %s   ancestor of HEAD: %s"
          % (RES["prereg_verification"]["ALL_FOUR_AGREE"],
             RES["prereg_verification"]["negative_test_absent_at_parent"],
             RES["prereg_verification"]["is_ancestor_of_HEAD"]))

    RES["git"] = {"revision": git("rev-parse", "HEAD"),
                  "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
                  "dirty": bool(git("status", "--porcelain")),
                  "dirty_paths": git("status", "--porcelain").splitlines()}
    RES["environment"] = {
        "operating_system": platform.platform(),
        "architecture": platform.machine(), "host": socket.gethostname(),
        "python_version": platform.python_version(),
        "dependencies": {"numpy": np.__version__, "scipy": scipy.__version__},
        "blas_threads": {k: os.environ.get(k) for k in
                         ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                          "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
                          "NUMEXPR_NUM_THREADS")}}
    RES["frozen_constants"] = {
        "cells": ["d%d_b%d" % c for c in CELLS], "q": Q_MOD,
        "graded_t_grid_13_points": GRADED_T, "n_draw": N_DRAW,
        "n_err": N_ERR, "chunk": CHUNK, "gate_k": GATE_K,
        "t_crit": AM3_T_CRIT, "c_grid": C_GRID, "c_neg_control": C_NEG_CONTROL,
        "pred_b1_c": PRED_B1_C, "family_size": FAMILY_SIZE,
        "materially_below_threshold_set_in_advance": MATERIALLY_BELOW,
        "seed_nullfam": "700000 + d*1000 + beta*10 + j + 100000*(m+1)",
        "seed_nullfam_status": (
            "IMPLEMENTATION COMPLETION, declared in prereg 3.1 BEFORE any draw. "
            "The carried seed table has no 13-frame-family entry because no "
            "such family was ever built."),
    }
    RES["quoted_counts_NOT_RESCORED"] = {
        "committed_real_n_fire_c6_out_of_48": COMMITTED_REAL_N_FIRE_C6,
        "red_team_exact_null_n_fire_c6_out_of_48": RED_TEAM_EXACT_NULL_N_FIRE_C6,
        "red_team_exact_null_per_cell": RED_TEAM_EXACT_NULL_PER_CELL,
        "red_team_exact_null_n_fire_c4_out_of_48": RED_TEAM_EXACT_NULL_C4,
        "red_team_exact_null_c_min_median": RED_TEAM_EXACT_NULL_CMIN_MEDIAN,
        "status": ("QUOTED. The real count is read from BATCH-cbe023 "
                   "results_g3.json and the exact-null benchmark from the Red "
                   "Team's REVIEW MEASUREMENT (red_team_report.md RT-B2). "
                   "Neither is rescored, reproduced as a baseline, or offered "
                   "as evidence of this run. Binding carry: the real count may "
                   "not be reported without the exact-null benchmark in the "
                   "same sentence."),
        "the_two_nulls_are_different_objects": (
            "The Red Team's exact null is SYNTHETIC: it keeps the committed "
            "SE_step(i) and SE_diff(t_i) and sets Delta_i := 0 by hand. THIS "
            "null is an OBJECT: 13 independently drawn Haar frame stacks whose "
            "Delta_i, SE_step(i) and SE_diff(t_i) are all its own measured "
            "quantities. Agreement between them is therefore informative and "
            "is not built in."),
    }

    cells_out = OrderedDict()
    err_cache = {}
    for (d, beta) in CELLS:
        key = "d%d_b%d" % (d, beta)
        print("\n[cell %s]  d = %d  beta = %d" % (key, d, beta))
        t0 = time.time()
        if d not in err_cache:
            err_cache[d] = make_errors(d)
        Ef, n2, echk = err_cache[d]
        qb10 = float(betaincinv(beta / 2.0, (d - beta) / 2.0, P_TAIL_10))

        # the carried Haar NULL ARM -- unchanged, and it sets SE_diff
        Qh = haar_frames(d, beta)
        haar = arm_r_values(project(Ef, n2, Qh, beta), qb10)
        print("    Haar null arm  r_mean %.9f  r_sd %.4e"
              % (haar["mean"], haar["sd"]))

        means, values, se_diff, arms = [], [], [], OrderedDict()
        for m, t in enumerate(GRADED_T):
            Qm = nullfam_frames(d, beta, m)
            a = arm_r_values(project(Ef, n2, Qm, beta), qb10)
            arms["m%02d_t%.4f" % (m, t)] = a
            means.append(a["mean"])
            values.append(a["values"])
            se_diff.append(se_of_difference(a["sd"], haar["sd"]))
            print("    m=%2d  t=%.4f  r_mean %.9f  r_sd %.4e  SE_diff %.4e"
                  % (m, t, a["mean"], a["sd"], se_diff[-1]))

        sc = score_cell(GRADED_T, means, values, se_diff)
        sc["haar_null_arm"] = haar
        sc["arms"] = arms
        sc["error_law_check"] = echk
        sc["q_beta_tail_2^-10"] = qb10
        sc["seconds"] = time.time() - t0
        cells_out[key] = sc
        print("    n_fire  %s" % sc["n_fire"])
        print("    mean Delta over 12 steps  %+.6e   (sd %.6e)"
              % (sc["mean_delta"], sc["sd_delta"]))
        print("    c_min median %.4f   se_step/se_diff median %.4f   %.1f s"
              % (sc["c_min_median"], sc["se_step_over_se_diff_median"],
                 sc["seconds"]))
    RES["cells"] = cells_out

    # ------------------------------------------------------- family totals
    tot = {str(c): sum(cells_out[k]["n_fire"][str(c)] for k in cells_out)
           for c in C_GRID}
    per_cell_c6 = [cells_out[k]["n_fire"][str(PRED_B1_C)] for k in cells_out]
    n_null_c6 = tot[str(PRED_B1_C)]
    n_degen = sum(cells_out[k]["n_degenerate"] for k in cells_out)
    RES["null_family_totals"] = {
        "n_fire_by_c_out_of_%d" % FAMILY_SIZE: tot,
        "n_fire_c6_out_of_48": n_null_c6,
        "n_fire_c6_per_cell": per_cell_c6,
        "n_fire_at_c_neg6": sum(cells_out[k]["n_fire_at_c_neg6"]
                                for k in cells_out),
        "n_degenerate_steps": n_degen,
        "n_live_steps": FAMILY_SIZE - n_degen,
        "n_fire_definitions_agree_in_every_cell":
            all(cells_out[k]["n_fire_definitions_agree"] for k in cells_out),
        "mean_Delta_over_all_live_steps": float(np.mean(
            [s["delta"] for k in cells_out for s in cells_out[k]["steps"]
             if not s["degenerate"]])),
    }

    # -------------------------------------------------------- the decay check
    seq = [tot[str(c)] for c in C_GRID]
    monotone = all(seq[i] <= seq[i + 1] for i in range(len(seq) - 1))
    RES["decay_check"] = {
        "criterion": ("PASS (the count is an effect): n_fire on the null family "
                      "is MATERIALLY BELOW the real count at c = 6, where "
                      "MATERIALLY BELOW was fixed in advance at a difference of "
                      "at least %d of %d, AND n_fire decays as c decreases "
                      "toward the negative control. FAIL (the count is an "
                      "artifact): n_fire on the null family is AT OR ABOVE the "
                      "real count at c = 6."
                      % (MATERIALLY_BELOW, FAMILY_SIZE)),
        "reference": "prereg 3.3, AM-13, docs/inventor-protocol.md section 3",
        "null_n_fire_c6": n_null_c6,
        "real_n_fire_c6_QUOTED": COMMITTED_REAL_N_FIRE_C6,
        "difference_real_minus_null": COMMITTED_REAL_N_FIRE_C6 - n_null_c6,
        "materially_below_threshold": MATERIALLY_BELOW,
        "null_is_materially_below_real":
            bool(COMMITTED_REAL_N_FIRE_C6 - n_null_c6 >= MATERIALLY_BELOW),
        "n_fire_monotone_nondecreasing_in_c": bool(monotone),
        "n_fire_at_c_0": tot["0"],
        "n_fire_at_c_neg6": RES["null_family_totals"]["n_fire_at_c_neg6"],
        "VERDICT": ("PASS -- the committed count is materially above its own "
                    "null family"
                    if COMMITTED_REAL_N_FIRE_C6 - n_null_c6 >= MATERIALLY_BELOW
                    else "FAIL -- the count does not decay when the parameter "
                         "meant to destroy the effect is applied, so it is an "
                         "ARTIFACT (docs/inventor-protocol.md section 3)"),
    }

    RES["THE_REQUIRED_SENTENCE"] = (
        "On the rebuilt null family, n_fire(c = 6) is %d of 48, against the "
        "committed real count of %d of 48 and the Red Team's exact-null "
        "benchmark of %d of 48."
        % (n_null_c6, COMMITTED_REAL_N_FIRE_C6, RED_TEAM_EXACT_NULL_N_FIRE_C6))

    RES["predictions"] = {
        "P-B1": {
            "statement": "the null family gives n_fire(c = 6) AT OR ABOVE 29 of "
                         "48, so the criterion of prereg 3.3 FAILS -- i.e. the "
                         "committed count is not evidence of an effect",
            "falsifier": "the null family gives n_fire(c = 6) <= 21 of 48",
            "realized_null_n_fire_c6": n_null_c6,
            "HOLDS": bool(n_null_c6 >= COMMITTED_REAL_N_FIRE_C6),
            "FALSIFIED": bool(n_null_c6 <= COMMITTED_REAL_N_FIRE_C6
                              - MATERIALLY_BELOW)},
        "detection_floor": {
            "value": 1, "units": "steps out of 48",
            "as_percentage_points": 100.0 / FAMILY_SIZE,
            "note": "the count is an integer out of 48; no difference smaller "
                    "than one step is resolvable and none is claimed"},
        "E_Delta_is_zero_by_construction_check": {
            "mean_Delta_over_all_live_steps":
                RES["null_family_totals"]["mean_Delta_over_all_live_steps"],
            "note": "consecutive grid points share NOTHING, so E[Delta_i] = 0 "
                    "at every step by construction. The realized mean is a "
                    "check that the construction did what it says; it is not a "
                    "test that could have failed in expectation."},
    }

    RES["could_not_fail_demonstration"] = {
        "could_not_FIRE": (
            "The null could never look like the real arm because it is built by "
            "a different pipeline. AVERTED: the null family differs from the "
            "graded family in EXACTLY ONE respect -- the 13 frames are drawn "
            "independently instead of from a shared (S_j, G_j) path. Errors, "
            "projection, chunking, quantile estimator, n_draw, SE construction, "
            "t_crit and the c grid are identical and carried byte-for-byte."),
        "could_not_PASS": (
            "The null could never differ from the real arm because c_min is "
            "dominated by t_crit*SE_step/SE_diff. That arrangement is exactly "
            "what P-B1 predicts, and prereg 3.3 declares IN ADVANCE that it is "
            "a FAIL -- an artifact -- rather than a null result. The "
            "coincidence is a reportable finding about the statistic, not a "
            "silent pass. The realized se_step/se_diff medians are reported per "
            "cell so a reader can see the domination directly."),
    }

    RES["timings"] = {"total_seconds": time.time() - T_START,
                      "per_cell_seconds": {k: cells_out[k]["seconds"]
                                           for k in cells_out}}
    RES["resources"] = {
        "max_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        * (1024 if platform.system() == "Linux" else 1)}
    RES["validity"] = {"status": "VALID", "expected_runs": 1, "used_runs": 1,
                       "no_selection_applied": True,
                       "n_degenerate_steps": n_degen}
    RES["what_this_does_not_reach"] = [
        "No reduction of any kind was run, so nothing here bears on any "
        "reduced basis, on any block size, or on any lattice-reduction cost.",
        "This is a NULL OBJECT. It carries no information about whether AM-3 "
        "has power against a real violation, in either direction. AM-3 IS NOT "
        "RETIRED; its power remains undemonstrated rather than disproved, and "
        "its 0.096 family-wise false-failure bound stands.",
        "BATCH-a44d08 is not rescored in any respect.",
        "Claim tier TOY: nothing here bears on ML-KEM security, on any FIPS 203 "
        "parameter set, on any attack cost or on any cost model.",
    ]
    RES["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    with open(args.out, "w") as fh:
        json.dump(RES, fh, indent=1, default=float)

    print("\n" + "=" * 78)
    print(RES["THE_REQUIRED_SENTENCE"])
    print("DECAY CHECK: %s" % RES["decay_check"]["VERDICT"])
    print("n_fire by c on the null family: %s" % tot)
    print("=" * 78)
    print("wrote %s   total %.1f s" % (args.out, time.time() - T_START))
    return 0


if __name__ == "__main__":
    sys.exit(main())
