#!/usr/bin/env python3
"""
TASK-20260806-c973e6 / BATCH-a44d08 / GOAL-MLKEM-005
SECTION C of the notarized pre-registration: the matched-`V` cross-family
comparison, AM-5's replacement for the withdrawn F-A1 observable.

Governed by, and NOT modified by, this file:
  coordination/goals/GOAL-MLKEM-005/batches/BATCH-a44d08/tasks/
      TASK-20260806-843c40/prereg.md
  sha256 8d00ca3f0977e7367cfd10f4eb01cc0d4d24dfdc1ecf9739ba3cc299ee2a6c80
  notarized by TASK-20260806-0a1072 in commit
  9cb2d3e28ae7a474edbb116d694969470829e112, asserted here to be an ancestor of
  HEAD -- the NOTARIZING COMMIT ITSELF, not its parent (prereg.md §0.2 / V-7).

This script loads that file READ-ONLY, re-hashes it, compares against the
notarized receipt AND the producer sidecar, and ABORTS on mismatch.  It
re-derives none of its thresholds.

WHAT IS NEW HERE, and the whole point of the task: the red team's probe
(BATCH-f19c37 reviews/TASK-20260806-ca8dc7/l2_vmatch.py) ran on ITS OWN frames
and ITS OWN seeds -- seed_graded = 500000 + j, error seed 20260806 + d, D
measured as a shift against its own Haar arm -- so its D values are not
absolutely comparable to the committed instrument's.  This run reproduces the
matched-V control ON THE COMMITTED BASES: the committed seed scheme
(seed_graded(d,beta,j) = 500000 + d*1000 + beta*10 + j, seed_error(d) =
20260805 + d, seed_basis(d,beta,i) = 700000 + d*1000 + beta*10 + i), the
committed CBD_{eta=2} error stream in the committed chunk order, the committed
frozen estimator D = sort(R)[1023]/q_Beta(2^-10) - 1 at N = 2^20, and the
committed float32 frame / float64 statistic dtypes.  A bit-exactness check
against BATCH-f19c37's committed results.json is run and reported for every
graded and unreduced arm this script regenerates.

CARRIED VERBATIM from BATCH-f19c37 / TASK-20260806-ca4377 `measure.py`
(itself carried from BATCH-436ddd `b2a.py`): the four cells, q = 3329,
CBD_{eta=2} sampler, R = ||Q^T e||^2/||e||^2 on the orthonormal tail-beta GSO
frame, the frozen empirical quantile estimator at N = 2^20, 8 draws per arm,
every seed formula, the AM-1 13-point t grid, the graded-path construction
with (S_j, G_j) hoisted before the t list, the chunked projection with
chunk = 2^15, the BETA_MAX = 60 tail slice, and the unreduced-basis frame
(fpylll `IntegerMatrix.random(d,"qary",k=d//2,q=3329)` at `seed_basis`,
QR(B^T), last beta columns).  NO LLL AND NO BKZ IS RUN by this script: the
unreduced arm is read before any reduction, exactly as `reduce_one` reads it.

Observations only.  No status change, no hypothesis movement, no evidence
record, no interpretation beyond the declared verdicts of prereg.md §4.4.
Claim tier TOY: nothing here bears on ML-KEM security, on any FIPS 203
parameter set, on any attack cost, or on any cost model.  V, m3 and D are
properties of a basis PRESENTATION, not of a lattice (prereg.md §1.1), and no
verdict here is offered as an AM-4 adjudicator.

This script performs no git write, makes no commit, and writes exactly one
file, inside its own task directory: vmatch.json.
"""

import os

# Budget discipline: the host is shared and heavily loaded.  Pin every BLAS
# backend to a single thread BEFORE numpy is imported.
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS",
           "ACCELERATE_MAX_THREADS"):
    os.environ[_v] = "1"

import argparse
import hashlib
import json
import platform
import resource
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

PREREG_PATH = os.path.join(TASKS_DIR, "TASK-20260806-843c40", "prereg.md")
PREREG_SIDECAR = os.path.join(TASKS_DIR, "TASK-20260806-843c40",
                              "prereg_sha256.txt")
RECEIPT_PATH = os.path.join(BATCH_DIR, "archives", "TASK-20260806-0a1072",
                            "snapshot-receipt.json")
PREREG_REL = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-a44d08/tasks/"
              "TASK-20260806-843c40/prereg.md")
NOTARIZING_COMMIT = "9cb2d3e28ae7a474edbb116d694969470829e112"
EXPECTED_PREREG_SHA256 = (
    "8d00ca3f0977e7367cfd10f4eb01cc0d4d24dfdc1ecf9739ba3cc299ee2a6c80")

COMMITTED_F19 = os.path.join(
    BATCHES_DIR, "BATCH-f19c37", "tasks", "TASK-20260806-ca4377",
    "results.json")
RED_TEAM_PROBE = os.path.join(
    BATCHES_DIR, "BATCH-f19c37", "reviews", "TASK-20260806-ca8dc7",
    "l2_vmatch.py")

# ------------------------------------------------------- carried constants
Q_MOD = 3329                                     # [carried]
CELLS = [(100, 30), (100, 40), (140, 30), (140, 40)]   # [carried]
N_DRAW = 8                                       # [carried] draws_per_arm
N_ERR = 1 << 20                                  # [carried] N = 2^20
CHUNK = 1 << 15                                  # [carried] committed chunking
P_TAIL = 2.0 ** -10                              # [carried]
BETA_MAX = 60                                    # [carried] tail slice width
GRADED_T = [0.0, 0.0025, 0.005, 0.0075, 0.01, 0.015, 0.02, 0.03,
            0.05, 0.1, 0.25, 0.5, 1.0]           # [carried] AM-1 13-point grid

# ------------------------------------- Section C constants, prereg.md §4, FROZEN
V_MATCH_TOL = 1e-9                               # §4.2
DEGEN_TOL = 1e-9                                 # §4.3 step 3 / §4.6 Form 2
REL_EFFECT_FLOOR = 0.05                          # §4.4 condition (ii)
M3_SEPARATION = 0.10                             # §4.5 informativeness
SUGGESTIVE_T = 3.0                               # §4.4
TCRIT_NC12 = 3.6358074219539622                  # §4.4, fpylll available
TCRIT_NC8 = 3.3352949398170852                   # §4.4, fpylll unavailable
FAMILY_ALPHA = 0.10                              # §4.4 family-wise level
P_ABS_T7_GT_3 = 0.019942126131992522             # §4.4 [closed form]
# §4.6 item 3: the red team's independently constructed m3_TL cross-check.
RT_M3_CHECK = [(8.6334, 0.980040), (6.0526, -0.568440)]   # at (d,beta)=(100,30)

FORBIDDEN_WORDS = ["absent", "no departure", "vanishes",
                   "consistent with zero", "negligible difference"]


# ================================================================== seeds
def seed_basis(d, beta, i):
    return 700000 + d * 1000 + beta * 10 + i


def seed_error(d):
    return 20260805 + d


def seed_graded(d, beta, j):
    return 500000 + d * 1000 + beta * 10 + j


# ============================================================== error law
_POPCNT4 = np.array([bin(v).count("1") for v in range(16)], dtype=np.int8)


def cbd_eta2(rng, n, d):
    r = rng.integers(0, 16, size=(n, d), dtype=np.uint8)
    return (_POPCNT4[r & 3] - _POPCNT4[r >> 2]).astype(np.int8)


# ================================================================ frames
def graded_paths(d, beta, n_draw=N_DRAW):
    """[carried] prereg.md §1: (S_j, G_j) drawn ONCE per (d,beta,j) from
    seed_graded, BEFORE and INDEPENDENTLY of the t list, reused across every t.
    Draw order fresh-rng -> choice -> standard_normal, bit-identical to the
    committed instrument."""
    out = []
    for j in range(n_draw):
        g = np.random.default_rng(seed_graded(d, beta, j))
        S = g.choice(d, size=beta, replace=False)
        G = g.standard_normal((d, beta))
        E = np.zeros((d, beta))
        E[S, np.arange(beta)] = 1.0
        out.append((E, G))
    return out


def graded_frames(paths, t):
    return [np.linalg.qr(np.sqrt(1.0 - t) * E + np.sqrt(t) * G)[0]
            .astype(np.float32) for (E, G) in paths]


def unreduced_frames(d, beta, n_draw=N_DRAW):
    """[carried] The committed unreduced arm.  fpylll builds the q-ary basis at
    seed_basis; the frame is the last beta columns of Q from QR(B^T), read
    BEFORE any reduction, exactly as BATCH-436ddd `reduce_one` reads it.
    NO LLL AND NO BKZ IS RUN."""
    from fpylll import IntegerMatrix, FPLLL
    out = []
    for i in range(n_draw):
        FPLLL.set_random_seed(seed_basis(d, beta, i))
        A = IntegerMatrix.random(d, "qary", k=d // 2, q=Q_MOD)
        M = np.array([[A[r, c] for c in range(d)] for r in range(d)],
                     dtype=np.float64)
        Qf, _ = np.linalg.qr(M.T)
        Q60 = np.ascontiguousarray(Qf[:, d - BETA_MAX:], dtype=np.float32)
        out.append(np.ascontiguousarray(Q60[:, BETA_MAX - beta:]))
    return out


# ============================================ TL, the two-level family, §4.2
def v_tl(u, d, beta):
    m = beta / d
    return (beta * ((u - m) ** 2 + (1.0 - u - m) ** 2)
            + (d - 2 * beta) * m * m)


def m3_tl(u, d, beta):
    m = beta / d
    return (beta * ((u - m) ** 3 + (1.0 - u - m) ** 3)
            + (d - 2 * beta) * (-m) ** 3)


def u_from_v(V, d, beta):
    """§4.2 closed-form inverse, float64.  Returns None if V is outside the
    reachable interval [V_TL(1/2), V_TL(1)] (declared UNREACHABLE)."""
    m = beta / d
    S = (V - (d - 2 * beta) * m * m) / beta
    x = S / 2.0 - (0.5 - m) ** 2
    if x < 0.0:
        return None
    u = 0.5 + np.sqrt(x)
    if u > 1.0:
        return None
    return float(u)


def tl_frame(u, d, beta):
    """§4.2: beta mutually orthogonal rank-1 projectors on the coordinate pairs
    (a, a+beta), each with diagonal (u, 1-u).  Deterministic; no seed.  The
    error law is i.i.d. across coordinates, so the placement of the support is
    irrelevant in distribution."""
    Q = np.zeros((d, beta), dtype=np.float64)
    a = np.arange(beta)
    Q[a, a] = np.sqrt(u)
    Q[a + beta, a] = np.sqrt(1.0 - u)
    return np.ascontiguousarray(Q.astype(np.float32))


# ============================================================ frame scalars
def diag_moments(Q, d, beta):
    """V = sum_a (P_aa - beta/d)^2 and m3 = sum_a (P_aa - beta/d)^3 for
    P = Q Q^T.  Deterministic: ZERO error draws.  float64 arithmetic on the
    exact float32 frame the projection consumes (committed convention)."""
    Qd = np.asarray(Q, dtype=np.float64)
    pd = np.einsum("ij,ij->i", Qd, Qd)
    c = pd - beta / d
    return float(np.sum(c * c)), float(np.sum(c ** 3))


# ============================================================== projection
def project_D(Ef, n2, frames, d, beta, qb):
    """[carried] The committed projection and estimator, byte for byte in
    structure: stack the 8 frames into a d x (8*beta) float32 array, chunk the
    error matrix at 2^15, accumulate R in float32, then
    D_j = sort(R_j)[1023] / q_Beta(2^-10) - 1 in float64."""
    Q = np.ascontiguousarray(np.concatenate(frames, axis=1))
    R = np.empty((N_ERR, N_DRAW), dtype=np.float32)
    for s0 in range(0, N_ERR, CHUNK):
        s1 = min(N_ERR, s0 + CHUNK)
        S = Ef[s0:s1] @ Q
        S *= S
        R[s0:s1] = S.reshape(s1 - s0, N_DRAW, beta).sum(axis=2) / n2[s0:s1, None]
        del S
    idx = max(1, min(N_ERR, int(round(P_TAIL * N_ERR)))) - 1
    D, qe = [], []
    for j in range(N_DRAW):
        col = np.sort(R[:, j].astype(np.float64))
        qe.append(float(col[idx]))
        D.append(float(col[idx] / qb - 1.0))
    del R
    return D, qe, idx


def arm_record(name, family, frames, d, beta, Ef, n2, qb):
    V, M3 = [], []
    for Q in frames:
        v, m3 = diag_moments(Q, d, beta)
        V.append(v)
        M3.append(m3)
    D, qe, idx = project_D(Ef, n2, frames, d, beta, qb)
    return {
        "arm": name, "family": family,
        "V_per_draw": V, "V_mean": float(np.mean(V)),
        "V_sd": float(np.std(V, ddof=1)),
        "m3_per_draw": M3, "m3_mean": float(np.mean(M3)),
        "m3_sd": float(np.std(M3, ddof=1)),
        "q_emp_per_draw": qe, "order_stat_index": idx,
        "D_per_draw": D, "D_mean": float(np.mean(D)),
        "D_sd": float(np.std(D, ddof=1)),
    }


# ============================================================ verification
def verify_prereg():
    with open(PREREG_PATH, "rb") as f:
        raw = f.read()
    got = hashlib.sha256(raw).hexdigest()
    rec = json.load(open(RECEIPT_PATH))
    want_receipt = rec["archive"]["path_sha256"][PREREG_REL]
    want_field = rec["prereg_sha256"]
    want_sidecar = open(PREREG_SIDECAR).read().split()[0].strip()
    ok = (got == want_receipt == want_field == want_sidecar
          == EXPECTED_PREREG_SHA256)
    return {
        "prereg_path": PREREG_REL,
        "prereg_bytes": len(raw),
        "recomputed_sha256": got,
        "expected_sha256_from_dispatch": EXPECTED_PREREG_SHA256,
        "notarized_receipt_path_sha256": want_receipt,
        "notarized_receipt_prereg_sha256_field": want_field,
        "producer_prereg_sha256_txt": want_sidecar,
        "receipt_task_id": rec["task_id"],
        "all_four_sources_agree": bool(ok),
        "match": bool(ok),
    }


def git_state():
    def g(*a):
        return subprocess.run(["git", "-C", REPO_ROOT] + list(a),
                              capture_output=True, text=True)
    head = g("rev-parse", "HEAD").stdout.strip()
    anc = g("merge-base", "--is-ancestor", NOTARIZING_COMMIT, "HEAD")
    dirty = g("status", "--porcelain").stdout.strip()
    return {
        "head_commit": head,
        "notarizing_commit_asserted": NOTARIZING_COMMIT,
        "assertion": ("git merge-base --is-ancestor <NOTARIZING COMMIT ITSELF> "
                      "HEAD -- prereg.md §0.2 correction V-7: the notarizing "
                      "commit, NOT its parent"),
        "notarizing_commit_is_ancestor_of_head": bool(anc.returncode == 0),
        "worktree_dirty": bool(dirty),
        "worktree_dirty_paths": dirty.splitlines(),
        "branch": g("rev-parse", "--abbrev-ref", "HEAD").stdout.strip(),
    }


def env_record():
    try:
        import fpylll
        fp = fpylll.__version__
    except Exception as e:          # pragma: no cover
        fp = f"UNAVAILABLE: {e}"
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
        "numpy": np.__version__,
        "scipy": __import__("scipy").__version__,
        "fpylll": fp,
        "blas_threads_pinned_to": 1,
        "thread_env": {v: os.environ.get(v) for v in
                       ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                        "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
                        "NUMEXPR_NUM_THREADS", "ACCELERATE_MAX_THREADS")},
        "loadavg_at_start": list(os.getloadavg()),
    }


# ====================================================================== main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TASK_DIR, "vmatch.json"))
    ap.add_argument("--wall-budget-seconds", type=float, default=5400.0)
    args = ap.parse_args()

    t_start = time.time()

    # ------------------------------------------- GATE 1: notarized prereg
    ver = verify_prereg()
    print("=" * 78)
    print("NOTARIZED PRE-REGISTRATION VERIFICATION (prereg.md §7)")
    for k, v in ver.items():
        print(f"  {k:40s}: {v}")
    if not ver["match"]:
        print("ABORT: prereg.md sha256 does NOT match the notarized receipt.")
        print("Harness failure, not a result. The run does not proceed.")
        return 2
    git = git_state()
    print("GIT STATE")
    for k, v in git.items():
        print(f"  {k:40s}: {v}")
    if not git["notarizing_commit_is_ancestor_of_head"]:
        print("ABORT: the notarizing commit is NOT an ancestor of HEAD.")
        return 2
    print("  VERIFIED. Section C is loaded read-only and unmodified.")
    print("=" * 78)
    sys.stdout.flush()

    committed = json.load(open(COMMITTED_F19))

    res = {
        "task_id": "TASK-20260806-c973e6",
        "batch_id": "BATCH-a44d08",
        "goal_id": "GOAL-MLKEM-005",
        "role": "executor",
        "claim_tier": "toy",
        "section": "C -- matched-V cross-family comparison (AM-5)",
        "governed_by": ("prereg.md §4 of TASK-20260806-843c40, notarized by "
                        "TASK-20260806-0a1072 in commit "
                        + NOTARIZING_COMMIT),
        "prereg_verification": ver,
        "git": git,
        "environment": env_record(),
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "what_this_run_is": (
            "A REPRODUCTION of the red team's matched-V control ON THE "
            "COMMITTED BASES, so that its D values become absolutely "
            "comparable to the committed instrument's. The red team probe used "
            "its own seeds (seed_graded = 500000 + j; error seed 20260806 + d) "
            "and measured D as a shift against its own Haar arm; this run uses "
            "the committed seed scheme, the committed CBD error stream and the "
            "frozen estimator D = sort(R)[1023]/q_Beta(2^-10) - 1."),
        "scope_limit": (
            "V, m3 and D are properties of a basis PRESENTATION, not of a "
            "lattice (prereg.md §1.1). No verdict here is an AM-4 adjudicator. "
            "Claim tier TOY: nothing here bears on ML-KEM security, on any "
            "FIPS 203 parameter set, on any attack cost or on any cost model."),
        "frozen_constants": {
            "cells": CELLS, "q": Q_MOD, "draws_per_arm": N_DRAW,
            "errors_per_cell": N_ERR, "chunk": CHUNK,
            "tail_level": P_TAIL, "graded_t_grid": GRADED_T,
            "V_match_tolerance_abs": V_MATCH_TOL,
            "degeneracy_exclusion_tolerance_abs": DEGEN_TOL,
            "relative_effect_floor": REL_EFFECT_FLOOR,
            "m3_separation_requirement": M3_SEPARATION,
            "suggestive_band_lower_t": SUGGESTIVE_T,
            "P_abs_t7_gt_3": P_ABS_T7_GT_3,
            "tcrit_nC12_declared": TCRIT_NC12,
            "tcrit_nC8_declared": TCRIT_NC8,
            "family_wise_alpha": FAMILY_ALPHA,
            "seed_scheme": {
                "seed_basis": "700000 + d*1000 + beta*10 + i",
                "seed_error": "20260805 + d",
                "seed_graded": "500000 + d*1000 + beta*10 + j",
                "TL_family": "deterministic, no seed (pairs (a, a+beta))"},
        },
        "cells": {},
        "protocol_deviations": [],
        "objections_recorded_and_run_anyway": [],
        "timings": {},
    }

    # ------------------------------- fpylll availability fixes the n_C branch
    try:
        import fpylll  # noqa: F401
        fpylll_ok = True
    except Exception as e:
        fpylll_ok = False
        res["protocol_deviations"].append({
            "kind": "infrastructure",
            "what": f"fpylll unavailable: {e}",
            "effect": ("the unreduced real-lattice target of §4.3 step 5 is "
                       "NOT MEASURED in any cell; the declared n_C = 8 branch "
                       "applies. Infrastructure, never a result "
                       "(AGENTS.md rule 3, prereg.md §5.7).")})
    res["fpylll_available"] = fpylll_ok
    res["declared_nC"] = 12 if fpylll_ok else 8
    res["declared_tcrit"] = TCRIT_NC12 if fpylll_ok else TCRIT_NC8

    all_pairs = []

    for (d, beta) in CELLS:
        if time.time() - t_start > args.wall_budget_seconds:
            res["aborted_reason"] = (
                f"wall-clock budget exhausted before cell d{d}_b{beta} -- "
                "INFRASTRUCTURE OUTCOME, never a result (AGENTS.md rule 3)")
            break
        ckey = f"d{d}_b{beta}"
        tc0 = time.time()
        a, b = beta / 2.0, (d - beta) / 2.0
        qb = float(betaincinv(a, b, P_TAIL))
        m = beta / d
        V_lo, V_hi = v_tl(0.5, d, beta), v_tl(1.0, d, beta)
        V_degen = beta * (1.0 - beta / d)

        cell = {
            "d": d, "beta": beta, "m_beta_over_d": m,
            "q_Beta_2em10": qb,
            "V_reachable_interval_TL": [V_lo, V_hi],
            "V_degenerate_coordinate_projector": V_degen,
            "V_TL_at_u1_equals_degenerate": bool(abs(V_hi - V_degen) < 1e-12),
            "E_V_haar_exact": 2.0 * beta * (d - beta) / (d * (d + 2.0)),
        }
        print(f"\n[cell {ckey}] q_Beta(2^-10) = {qb:.17g}  TL reachable V in "
              f"[{V_lo:.6f}, {V_hi:.6f}]  degenerate V = {V_degen:.6f}")

        # ---- graded frames on the full 13-point grid; V is deterministic
        paths = graded_paths(d, beta)
        gframes = {t: graded_frames(paths, t) for t in GRADED_T}
        del paths

        grid = []
        for t in GRADED_T:
            Vs = [diag_moments(Q, d, beta)[0] for Q in gframes[t]]
            M3s = [diag_moments(Q, d, beta)[1] for Q in gframes[t]]
            Vm = float(np.mean(Vs))
            per_draw_reach = [bool(V_lo <= v <= V_hi) for v in Vs]
            grid.append({
                "t": t, "V_mean": Vm, "V_per_draw": Vs,
                "V_min": float(min(Vs)), "V_max": float(max(Vs)),
                "m3_mean": float(np.mean(M3s)),
                "degenerate": bool(abs(Vm - V_degen) <= DEGEN_TOL),
                "reachable_by_mean_V": bool(V_lo <= Vm <= V_hi),
                "reachable_all_8_draws": bool(all(per_draw_reach)),
                "n_draws_reachable": int(sum(per_draw_reach)),
            })
        cell["graded_grid_V"] = grid

        # ---- §4.3 selection rule, uses no measurement
        survivors = [g for g in grid
                     if g["reachable_by_mean_V"] and not g["degenerate"]]
        keep = {id(g) for g in survivors}
        excl = [{"t": g["t"], "reason":
                 ("DEGENERATE (|V - beta(1-beta/d)| <= 1e-9)" if g["degenerate"]
                  else "UNREACHABLE for TL"),
                 "V_mean": g["V_mean"],
                 "reachable_all_8_draws": g["reachable_all_8_draws"],
                 "n_draws_reachable": g["n_draws_reachable"]}
                for g in grid if id(g) not in keep]
        survivors.sort(key=lambda g: g["t"])
        if len(survivors) >= 3:
            chosen = [survivors[0], survivors[2]]
            rule = "first and third survivor by t ascending"
        elif len(survivors) == 2:
            chosen = survivors
            rule = "exactly two survive -> take both"
        elif len(survivors) == 1:
            chosen = survivors
            rule = "exactly one survives -> take it"
        else:
            chosen = []
            rule = "none survives -> this cell contributes no graded target"
        cell["target_selection"] = {
            "rule_applied": rule,
            "n_survivors": len(survivors),
            "survivor_t": [g["t"] for g in survivors],
            "chosen_t": [g["t"] for g in chosen],
            "exclusions": excl,
        }
        print(f"  survivors t = {[g['t'] for g in survivors]}  -> chosen "
              f"{[g['t'] for g in chosen]}  ({rule})")

        # ---- error draws: the committed stream, committed chunk order
        te = time.time()
        rng = np.random.default_rng(seed_error(d))
        Ef = np.empty((N_ERR, d), dtype=np.float32)
        n2 = np.empty(N_ERR, dtype=np.float64)
        hist = np.zeros(5, dtype=np.int64)
        for s0 in range(0, N_ERR, CHUNK):
            s1 = min(N_ERR, s0 + CHUNK)
            Ei = cbd_eta2(rng, s1 - s0, d)
            hist += np.bincount((Ei.astype(np.int32) + 2).ravel(), minlength=5)
            n2[s0:s1] = (Ei.astype(np.int32) ** 2).sum(1)
            Ef[s0:s1] = Ei
        pm = hist / hist.sum()
        cell["cbd_pmf_check"] = {
            "measured": pm.tolist(),
            "exact_fips203_cbd_eta2": [1 / 16, 4 / 16, 6 / 16, 4 / 16, 1 / 16],
            "measured_mu4": float(sum(pm[i] * (i - 2) ** 4 for i in range(5))),
            "exact_mu4": 2.5}
        cell["timing_error_generation_seconds"] = round(time.time() - te, 2)

        # ---- assemble the targets
        targets = []
        for g in chosen:
            targets.append({"kind": "graded", "t": g["t"],
                            "label": f"graded_t{g['t']:.4f}",
                            "frames": gframes[g["t"]]})
        unred_note = None
        if fpylll_ok:
            uf = unreduced_frames(d, beta)
            uV = [diag_moments(Q, d, beta)[0] for Q in uf]
            uVm = float(np.mean(uV))
            reach = all(V_lo <= v <= V_hi for v in uV)
            cell["unreduced_arm"] = {
                "V_mean": uVm, "V_per_draw": uV,
                "reachable_all_8_draws": bool(reach),
                "reachable_by_mean_V": bool(V_lo <= uVm <= V_hi)}
            if reach:
                targets.append({"kind": "unreduced", "t": None,
                                "label": "unreduced", "frames": uf})
            else:
                unred_note = (
                    f"UNREACHABLE: the committed unreduced arm has V = {uVm:.6f}"
                    f", outside the TL-reachable interval "
                    f"[{V_lo:.6f}, {V_hi:.6f}]. prereg.md §4.2 requires it to be "
                    "declared UNREACHABLE and excluded, and §4.3 step 5's "
                    "parenthetical claim that all four unreduced V lie inside "
                    "the reachable intervals is therefore NOT correct in this "
                    "cell. The frozen rule is applied and the objection is "
                    "recorded (prereg.md §5.5).")
                cell["unreduced_arm"]["exclusion"] = unred_note
                res["objections_recorded_and_run_anyway"].append({
                    "cell": ckey, "objection": unred_note})
                print("  " + unred_note)

        # ---- measure every target pair
        pairs = []
        for tg in targets:
            gr = arm_record(tg["label"], "GR" if tg["kind"] == "graded"
                            else "UNREDUCED", tg["frames"], d, beta, Ef, n2, qb)
            us, tlf, resid = [], [], []
            unreachable_draw = False
            for v in gr["V_per_draw"]:
                u = u_from_v(v, d, beta)
                if u is None:
                    unreachable_draw = True
                    break
                us.append(u)
                Qtl = tl_frame(u, d, beta)
                tlf.append(Qtl)
                resid.append(abs(diag_moments(Qtl, d, beta)[0] - v))
            if unreachable_draw:
                pairs.append({"target": tg["label"],
                              "status": "EXCLUDED -- UNREACHABLE at some draw"})
                continue
            tl = arm_record("TL_matched_" + tg["label"], "TL", tlf,
                            d, beta, Ef, n2, qb)
            tl["u_per_draw"] = us
            tl["m3_closed_form_per_draw"] = [m3_tl(u, d, beta) for u in us]
            tl["V_closed_form_per_draw"] = [v_tl(u, d, beta) for u in us]

            diffs = np.array(gr["D_per_draw"]) - np.array(tl["D_per_draw"])
            dbar = float(diffs.mean())
            se = float(diffs.std(ddof=1) / np.sqrt(N_DRAW))
            denom = max(abs(gr["D_mean"]), abs(tl["D_mean"]))
            tstat = (abs(dbar) / se) if se > 0 else None
            rel = (abs(dbar) / denom) if denom > 0 else None
            m3sep_den = max(abs(gr["m3_mean"]), abs(tl["m3_mean"]))
            m3sep = (abs(gr["m3_mean"] - tl["m3_mean"]) / m3sep_den
                     if m3sep_den > 0 else None)
            informative = bool(m3sep is not None and m3sep > M3_SEPARATION)

            pr = {
                "cell": ckey, "target": tg["label"], "target_kind": tg["kind"],
                "t": tg["t"],
                "GR": gr, "TL": tl,
                "V_match_residual_per_draw": resid,
                "V_match_residual_max": float(max(resid)),
                "V_match_residual_mean": float(np.mean(resid)),
                "V_match_within_frozen_tolerance":
                    bool(max(resid) <= V_MATCH_TOL),
                "V_match_mean_level_abs_diff":
                    abs(gr["V_mean"] - tl["V_mean"]),
                "D_GR_mean": gr["D_mean"], "D_TL_mean": tl["D_mean"],
                "m3_GR_mean": gr["m3_mean"], "m3_TL_mean": tl["m3_mean"],
                "paired_diff_per_draw": diffs.tolist(),
                "paired_diff_mean": dbar,
                "SE_paired_diff": se,
                "abs_t": tstat,
                "relative_difference": rel,
                "m3_separation": m3sep,
                "INFORMATIVE": informative,
                "detection_floor_relative_nC12":
                    (TCRIT_NC12 * se / denom) if denom > 0 else None,
            }
            pairs.append(pr)
            all_pairs.append(pr)
            print(f"  [{tg['label']:<18s}] V={gr['V_mean']:9.6f}  "
                  f"|dV|max={max(resid):.3e}  m3_GR={gr['m3_mean']:+9.6f}  "
                  f"m3_TL={tl['m3_mean']:+9.6f}  D_GR={gr['D_mean']:+.8f}  "
                  f"D_TL={tl['D_mean']:+.8f}  diff={dbar:+.8f}  "
                  f"|t|={tstat if tstat is None else round(tstat, 3)}  "
                  f"rel={rel if rel is None else round(rel, 5)}  "
                  f"INFORMATIVE={informative}")
            sys.stdout.flush()
        cell["pairs"] = pairs

        # ---- §4.6 Form 2: the degenerate point, as a LABELLED INSTRUMENT CHECK
        gr0 = arm_record("graded_t0.0000", "GR", gframes[0.0], d, beta,
                         Ef, n2, qb)
        tl1 = arm_record("TL_u1_coordinate_projector", "TL",
                         [tl_frame(1.0, d, beta)] * N_DRAW, d, beta, Ef, n2, qb)
        dg = np.array(gr0["D_per_draw"]) - np.array(tl1["D_per_draw"])
        cell["degenerate_instrument_check"] = {
            "status": ("INSTRUMENT CHECK, NEVER SUPPORT FOR ANYTHING. At "
                       "V = beta(1-beta/d) both families ARE the same object "
                       "-- a coordinate projector on beta axes -- so agreement "
                       "is forced by identity, not by mechanism. Excluded from "
                       "the scored family by prereg.md §4.3 step 3 and "
                       "reported by §4.6 Form 2."),
            "V_GR": gr0["V_mean"], "V_TL": tl1["V_mean"],
            "V_abs_diff": abs(gr0["V_mean"] - tl1["V_mean"]),
            "m3_GR": gr0["m3_mean"], "m3_TL": tl1["m3_mean"],
            "D_GR_mean": gr0["D_mean"], "D_TL_mean": tl1["D_mean"],
            "D_GR_per_draw": gr0["D_per_draw"],
            "D_TL_per_draw": tl1["D_per_draw"],
            "paired_diff_mean": float(dg.mean()),
            "SE_paired_diff": float(dg.std(ddof=1) / np.sqrt(N_DRAW)),
            "abs_t": (float(abs(dg.mean()) / (dg.std(ddof=1) / np.sqrt(N_DRAW)))
                      if dg.std(ddof=1) > 0 else None),
            "relative_difference": float(abs(dg.mean())
                                         / max(abs(gr0["D_mean"]),
                                               abs(tl1["D_mean"]))),
            "note": ("GR at t=0 is the coordinate projector on the random "
                     "subset S_j; TL at u=1 is the coordinate projector on "
                     "axes 0..beta-1. They are equal in DISTRIBUTION under the "
                     "i.i.d. error law but not on the same realized draws, so a "
                     "small realized difference is expected and is reported."),
        }

        # ---- bit-exactness of the regenerated committed arms
        rep = []
        cm = committed["cells"][ckey]
        for pr in pairs:
            if pr.get("status"):
                continue
            nm = pr["target"]
            if nm not in cm["arms_cbd"]:
                continue
            old_D = [x - 1.0 for x in
                     cm["arms_cbd"][nm]["ratio_p2em10_over_draws"]["values"]]
            old_V = cm["frame_V"][nm]["per_draw"]
            rep.append({
                "arm": nm,
                "max_abs_D_dev_vs_committed":
                    float(max(abs(x - y) for x, y in
                              zip(pr["GR"]["D_per_draw"], old_D))),
                "max_abs_V_dev_vs_committed":
                    float(max(abs(x - y) for x, y in
                              zip(pr["GR"]["V_per_draw"], old_V))),
                "bitwise_identical_D":
                    bool(all(x == y for x, y in
                             zip(pr["GR"]["D_per_draw"], old_D))),
            })
        old_D0 = [x - 1.0 for x in
                  cm["arms_cbd"]["graded_t0.0000"]
                  ["ratio_p2em10_over_draws"]["values"]]
        rep.append({
            "arm": "graded_t0.0000",
            "max_abs_D_dev_vs_committed":
                float(max(abs(x - y) for x, y in
                          zip(gr0["D_per_draw"], old_D0))),
            "max_abs_V_dev_vs_committed":
                float(max(abs(x - y) for x, y in
                          zip(gr0["V_per_draw"],
                              cm["frame_V"]["graded_t0.0000"]["per_draw"]))),
            "bitwise_identical_D":
                bool(all(x == y for x, y in zip(gr0["D_per_draw"], old_D0))),
        })
        cell["reproduction_vs_committed_BATCH_f19c37"] = {
            "source": ("BATCH-f19c37/tasks/TASK-20260806-ca4377/results.json "
                       "-- the committed measurement of the same frames"),
            "rows": rep,
            "all_bitwise_identical":
                bool(all(r["bitwise_identical_D"] for r in rep)),
            "meaning": ("This is what makes 'the committed bases' verified "
                        "rather than asserted: the GR and unreduced arms this "
                        "run regenerates from the committed seeds reproduce "
                        "the committed D and V values. It is an instrument "
                        "check, not evidence about any mechanism."),
        }

        del Ef, n2, gframes
        cell["timing_cell_wall_seconds"] = round(time.time() - tc0, 2)
        res["cells"][ckey] = cell

    # =========================================================== §4.4 scoring
    scored = [p for p in all_pairs if p["INFORMATIVE"]]
    noninf = [p for p in all_pairs if not p["INFORMATIVE"]]
    nC_realized = len(scored)
    tcrit_realized = (float(student_t.ppf(1.0 - FAMILY_ALPHA / (2 * nC_realized),
                                          N_DRAW - 1))
                      if nC_realized > 0 else None)
    tcrit_primary = res["declared_tcrit"]

    def score(pr, tcrit):
        cond_i = bool(pr["abs_t"] is not None and pr["abs_t"] > tcrit)
        cond_ii = bool(pr["relative_difference"] is not None
                       and pr["relative_difference"] > REL_EFFECT_FLOOR)
        sugg = bool(pr["abs_t"] is not None
                    and SUGGESTIVE_T <= pr["abs_t"] < tcrit and cond_ii)
        floor = (tcrit * pr["SE_paired_diff"]
                 / max(abs(pr["D_GR_mean"]), abs(pr["D_TL_mean"])))
        return {"condition_i_t": cond_i, "condition_ii_relative": cond_ii,
                "FALSIFYING_PAIR": bool(cond_i and cond_ii),
                "SUGGESTIVE_NOT_FALSIFYING": sugg,
                "detection_floor_relative": floor,
                "floor_below_5pct": bool(floor < REL_EFFECT_FLOOR)}

    def verdict(tcrit):
        rows = [{"cell": p["cell"], "target": p["target"],
                 **score(p, tcrit)} for p in scored]
        falsifying = [r for r in rows if r["FALSIFYING_PAIR"]]
        if falsifying:
            v = "L2 TAIL-SUFFICIENCY FALSIFIED"
        elif any(r["floor_below_5pct"] for r in rows) and rows:
            v = "CONSISTENT"
        elif rows:
            v = "UNDERPOWERED -- UPPER BOUND"
        else:
            v = "NOT EVALUABLE -- no informative pair"
        best_floor = min((r["detection_floor_relative"] for r in rows),
                         default=None)
        return {"t_crit": tcrit, "rows": rows,
                "n_falsifying": len(falsifying),
                "n_suggestive": sum(r["SUGGESTIVE_NOT_FALSIFYING"]
                                    for r in rows),
                "verdict": v,
                "tightest_detection_floor_relative": best_floor,
                "upper_bound_statement":
                    (None if v == "L2 TAIL-SUFFICIENCY FALSIFIED" or
                     best_floor is None else
                     f"any matched-V cross-family difference not detected here "
                     f"is bounded above by {100 * best_floor:.2f} percent "
                     f"relative at n = 8 draws, N = 2^20")}

    res["scoring"] = {
        "multiplicity_note": (
            "prereg.md §4.3 step 4 and §4.5 require n_C to be recomputed from "
            "the realized count and the Bonferroni level taken there. The "
            "dispatch contract additionally freezes the DECLARED critical "
            "values 3.6358074219539622 (n_C = 12) / 3.3352949398170852 "
            "(n_C = 8) and forbids re-deriving them. Both readings are "
            "reported. The declared value is the larger, hence the more "
            "conservative against falsification, and is the PRIMARY score."),
        "declared_nC": res["declared_nC"],
        "declared_tcrit": tcrit_primary,
        "realized_nC_after_reachability_and_informativeness": nC_realized,
        "realized_tcrit_recomputed": tcrit_realized,
        "n_targets_measured": len(all_pairs),
        "n_noninformative_excluded": len(noninf),
        "noninformative_pairs": [
            {"cell": p["cell"], "target": p["target"],
             "m3_GR": p["m3_GR_mean"], "m3_TL": p["m3_TL_mean"],
             "m3_separation": p["m3_separation"],
             "D_GR": p["D_GR_mean"], "D_TL": p["D_TL_mean"],
             "abs_t": p["abs_t"], "relative_difference":
                 p["relative_difference"]} for p in noninf],
        "primary_declared_nC": verdict(tcrit_primary),
        "secondary_realized_nC": (verdict(tcrit_realized)
                                  if tcrit_realized else None),
    }

    # ================================== §4.6 could-not-fail demonstrations
    # Form 1: within-path co-monotonicity, on the COMMITTED 13-point graded
    # path. Pure post-processing of already-recorded values; no measurement.
    f1 = {}
    for ckey, cm in committed["cells"].items():
        pts = []
        for t in GRADED_T:
            nm = f"graded_t{t:.4f}"
            pts.append((t, cm["frame_V"][nm]["mean"],
                        cm["arms_cbd"][nm]["ratio_p2em10_over_draws"]["mean"]
                        - 1.0))
        inv = sum(1 for i in range(len(pts)) for j in range(len(pts))
                  if pts[i][1] > pts[j][1] and pts[i][2] < pts[j][2])
        f1[ckey] = {
            "V_strictly_decreasing_in_t":
                bool(all(pts[i][1] > pts[i + 1][1] for i in range(len(pts) - 1))),
            "D_strictly_decreasing_in_t":
                bool(all(pts[i][2] > pts[i + 1][2] for i in range(len(pts) - 1))),
            "n_ordered_pairs_with_V_high_but_D_low": inv,
            "n_ordered_pairs_considered": len(pts) * (len(pts) - 1),
            "points": [{"t": t, "V": v, "D": D} for (t, v, D) in pts]}

    res["could_not_fail_demonstration"] = {
        "form_1_within_path_co_monotonicity": {
            "arrangement": ("Scoring co-monotonicity within a single monotone "
                            "path, where the verdict is forced by the "
                            "construction. This is the F-A1 defect itself."),
            "why_this_run_is_not_in_it": (
                "EVERY scored pair is cross-family by construction: GR (or the "
                "unreduced real-lattice arm) against TL at equal V. There is "
                "no within-path pair in the scored family; the count is "
                "reported below and is 0."),
            "n_within_path_pairs_in_scored_family": 0,
            "n_cross_family_pairs_in_scored_family": nC_realized,
            "committed_path_evidence": f1,
            "committed_path_evidence_note": (
                "Post-processing of BATCH-f19c37's COMMITTED values; no "
                "measurement was made for this block. It shows the F-A1 "
                "arrangement concretely: on the committed graded path V(t) and "
                "D(t) are both strictly decreasing in t, so the number of "
                "ordered pairs with higher V and lower D is 0 IDENTICALLY, "
                "whatever the mechanism. That test could not have failed."),
        },
        "form_2_matching_at_the_degenerate_V": {
            "arrangement": ("Matching at V = beta(1-beta/d), the global maximum "
                            "of V, where both families ARE the same object -- a "
                            "coordinate projector on beta axes. Agreement there "
                            "is forced by identity, not by mechanism."),
            "why_this_run_is_not_in_it": (
                "The degenerate point is excluded from the scored family BY "
                "RULE (prereg.md §4.3 step 3, tolerance 1e-9), before any data, "
                "and is retained only as a LABELLED INSTRUMENT CHECK. Every "
                "cell's exclusion is recorded in target_selection.exclusions "
                "and its instrument check in degenerate_instrument_check. No "
                "scored pair sits at the degenerate V; the minimum distance "
                "from a scored pair's V to the degenerate V is reported."),
            "per_cell": {},
        },
        "form_3_decoy_TL_family_tracking_GR_m3": {
            "arrangement": ("Choosing a second family whose m3 tracks GR's, so "
                            "that equal V implies equal everything and "
                            "agreement is forced again."),
            "why_this_run_is_not_in_it": (
                "prereg.md §4.5 requires a DECLARED m3 separation "
                "(> 10 percent of the larger |m3|) for a pair to enter the "
                "family at all, and m3 is reported for every frame. The "
                "realized separations are listed per pair. m3 is a "
                "deterministic function of the frames and uses no D value, so "
                "this exclusion cannot be tuned to an outcome."),
            "m3_separation_requirement": M3_SEPARATION,
            "per_pair": [{"cell": p["cell"], "target": p["target"],
                          "m3_GR": p["m3_GR_mean"], "m3_TL": p["m3_TL_mean"],
                          "m3_separation": p["m3_separation"],
                          "INFORMATIVE": p["INFORMATIVE"]}
                         for p in all_pairs],
            "m3_TL_closed_form_cross_check_vs_red_team": [
                {"V_target": V, "red_team_reported_m3": M,
                 "closed_form_m3_TL_here": m3_tl(u_from_v(V, 100, 30), 100, 30),
                 "abs_diff": abs(m3_tl(u_from_v(V, 100, 30), 100, 30) - M)}
                for (V, M) in RT_M3_CHECK],
            "cross_check_note": (
                "prereg.md §4.6 item 3: agreement of the closed-form m3_TL with "
                "the red team's independently constructed frames at (d,beta) = "
                "(100,30) checks that this TL construction is the SAME OBJECT "
                "as theirs. It is not evidence about D."),
        },
        "form_4_a_falsifier_that_cannot_fire": {
            "arrangement": ("The mirror defect: a criterion whose rejection "
                            "region is unreachable, so that CONSISTENT is a "
                            "property of the gate rather than of the object."),
            "why_this_run_is_not_in_it": (
                "prereg.md §4.4 declares the detection floor and FORCES an "
                "UNDERPOWERED -- UPPER BOUND verdict, never CONSISTENT, when "
                "the floor sits above the 5 percent effect size. The realized "
                "floors are reported per pair and the verdict is taken from "
                "them mechanically."),
        },
    }
    for ckey, cell in res["cells"].items():
        Vd = cell["V_degenerate_coordinate_projector"]
        dists = [abs(p["GR"]["V_mean"] - Vd) for p in cell["pairs"]
                 if not p.get("status")]
        res["could_not_fail_demonstration"][
            "form_2_matching_at_the_degenerate_V"]["per_cell"][ckey] = {
            "V_degenerate": Vd,
            "min_distance_from_a_scored_pair_V": (min(dists) if dists else None),
            "degenerate_excluded_by_rule": True,
            "instrument_check": cell["degenerate_instrument_check"],
        }

    # ---------------------------------------------------- wording scan (§5.4)
    blob = json.dumps(res).lower()
    res["forbidden_wording_scan"] = {
        "words": FORBIDDEN_WORDS,
        "hits_in_this_json": [w for w in FORBIDDEN_WORDS if w in blob],
        "rule": ("prereg.md §5.4: no 'absent', 'no departure', 'vanishes', "
                 "'consistent with zero' or synonym applied to a measured arm "
                 "without its floor."),
    }

    ru = resource.getrusage(resource.RUSAGE_SELF)
    res["timings"]["total_wall_seconds"] = round(time.time() - t_start, 2)
    res["timings"]["cpu_seconds"] = round(ru.ru_utime + ru.ru_stime, 2)
    res["resources"] = {
        "max_rss_bytes": ru.ru_maxrss,
        "max_rss_gib": round(ru.ru_maxrss / (1 << 30), 3),
        "wall_budget_seconds": args.wall_budget_seconds,
        "memory_budget_gib": 4.0,
        "loadavg_at_end": list(os.getloadavg()),
    }
    res["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    with open(args.out, "w") as f:
        json.dump(res, f, indent=1)

    # ------------------------------------------------------------ summary
    print("\n" + "=" * 78)
    print("SECTION C SUMMARY -- observations only, no interpretation")
    print("=" * 78)
    print(f"declared n_C = {res['declared_nC']}  t_crit = {tcrit_primary}")
    print(f"realized n_C = {nC_realized}  t_crit(recomputed) = {tcrit_realized}")
    print(f"targets measured = {len(all_pairs)}  "
          f"non-informative excluded = {len(noninf)}")
    print("\n%-10s %-20s %10s %11s %11s %12s %12s %10s %8s %8s" %
          ("cell", "target", "V", "m3_GR", "m3_TL", "D_GR", "D_TL",
           "|dV|max", "|t|", "rel%"))
    for p in all_pairs:
        print("%-10s %-20s %10.6f %+11.6f %+11.6f %+12.8f %+12.8f %10.2e "
              "%8.3f %8.3f" %
              (p["cell"], p["target"], p["GR"]["V_mean"], p["m3_GR_mean"],
               p["m3_TL_mean"], p["D_GR_mean"], p["D_TL_mean"],
               p["V_match_residual_max"], p["abs_t"] or 0.0,
               100 * (p["relative_difference"] or 0.0)))
    print("\nPRIMARY (declared n_C): " +
          res["scoring"]["primary_declared_nC"]["verdict"])
    if res["scoring"]["secondary_realized_nC"]:
        print("SECONDARY (realized n_C): " +
              res["scoring"]["secondary_realized_nC"]["verdict"])
    print("tightest detection floor (relative): " +
          str(res["scoring"]["primary_declared_nC"]
              ["tightest_detection_floor_relative"]))
    print(f"\nwall {res['timings']['total_wall_seconds']} s   "
          f"cpu {res['timings']['cpu_seconds']} s   "
          f"max RSS {res['resources']['max_rss_gib']} GiB")
    print(f"written: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
