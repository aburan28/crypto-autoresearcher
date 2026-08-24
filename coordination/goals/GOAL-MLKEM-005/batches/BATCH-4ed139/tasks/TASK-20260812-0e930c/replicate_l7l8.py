#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TASK-20260812-0e930c / BATCH-4ed139 / GOAL-MLKEM-005
RIDER (iii) -- the fpylll-equipped replication of the L7/L8 arm.

WHAT THIS IS, AND WHAT IT IS NOT.
  This RESTORES THE COVERAGE WAVE 2 LOST and is NEVER to be presented as
  resolving a doubt, THERE BEING NONE TO RESOLVE.  fpylll was absent in both
  wave-2 review sessions and in this batch's lead producer.  That absence is
  INFRASTRUCTURE SIGNAL (AGENTS.md rule 5) and was NEVER evidence against
  lam1n, hkz, the 48 reductions, or their reported max hkz_violation of 0.0.
  If the values reproduce, that is a replication of a quantity nobody doubted.
  If they do not, that is a FINDING and it is reported plainly and immediately.

GOVERNED BY
  PREREG-1, frozen and notarized:
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/
        TASK-20260812-34b86c/prereg.md
  section 8.3 (rider iii), section 2.5 route RD, section 11 binding carries.
  P-L1: the re-measurement reproduces the committed L7/L8 hkz and lam1n values
  to 6 decimals.  FALSIFIER: max absolute deviation above 1e-6.

CLAIM TIER: TOY, UNCONDITIONALLY.  Nothing computed here bears on ML-KEM
security, on any FIPS 203 parameter set, on any attack cost, or on any cost
model.  No number here transports to beta = 606, d = 1420, or anywhere else.

certificate.kind: none -- no discrete-log solve and no factor-base relation is
claimed or produced, so docs/claims-and-verification.md requires no solution
certificate.  The hkz_violation enumeration is an INSTRUMENT CHECK and is
labelled as such, never a certificate.

AM-9, APPLIED AND STATED: fpylll's k counts the q-SCALED ROWS, NOT the identity
block.  Throughout this file k = |K_I| = the size of the IDENTITY block
(L7: k = 6, L8: k = 14); fpylll's k would be k_fpylll = d - k (L7: 14, L8: 6).
No fpylll basis generator is called anywhere: every basis is built EXPLICITLY
as B = [[I_k, A], [0, q I_{d-k}]], and what is handed to fpylll is the full
d x d integer GRAM matrix -- d = 20 ROWS, all of them, never k rows and never
d - k rows.  The convention is therefore fixed STRUCTURALLY, not by a label.

SCOPE.  q = 3329; L7 (d=20, k=6) and L8 (d=20, k=14) only; the frozen beta grid
{5, 10, 15}; the 8 frozen bases; the frozen HKZ pipeline carried verbatim.
d <= 40 throughout.  No new reduction.  L1/L2 and L4/L5 are OUT OF SCOPE.

This script writes exactly one file: the --out path inside its own task
directory.  It performs no git write and makes no commit.
"""

import argparse
import hashlib
import json
import math
import os
import platform
import resource
import socket
import subprocess
import sys
import time
from collections import OrderedDict

import numpy as np

try:
    import scipy
    SCIPY_VERSION = scipy.__version__
except Exception as _se:                                   # pragma: no cover
    SCIPY_VERSION = "IMPORT FAILED: %s" % _se

T_START = time.time()

# ---------------------------------------------------------------- paths
TASK_DIR = os.path.dirname(os.path.abspath(__file__))
TASKS_DIR = os.path.normpath(os.path.join(TASK_DIR, ".."))
BATCH_DIR = os.path.normpath(os.path.join(TASKS_DIR, ".."))
BATCHES_DIR = os.path.normpath(os.path.join(BATCH_DIR, ".."))
# batches -> GOAL-MLKEM-005 -> goals -> coordination -> <repo root>.  FOUR
# levels; five lands in the enclosing checkout (defect D-2, not repeated).
REPO_ROOT = os.path.normpath(os.path.join(BATCHES_DIR, "..", "..", "..", ".."))

PREREG_REL = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/"
              "TASK-20260812-34b86c/prereg.md")
PREREG_PATH = os.path.join(REPO_ROOT, PREREG_REL)
PREREG_SIDECAR_REL = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/"
                      "tasks/TASK-20260812-34b86c/prereg_sha256.txt")
PREREG_SIDECAR_PATH = os.path.join(REPO_ROOT, PREREG_SIDECAR_REL)
NOTARIZING_COMMIT = "8d72f2c03"

COMMITTED_REL = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/"
                 "TASK-20260809-cda2f6/results_relvar.json")
COMMITTED_PATH = os.path.join(REPO_ROOT, COMMITTED_REL)
PRODUCER_SCRIPT_REL = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/"
                       "tasks/TASK-20260809-cda2f6/measure_relvar.py")
PRODUCER_SCRIPT_PATH = os.path.join(REPO_ROOT, PRODUCER_SCRIPT_REL)

# ------------------------------------------- frozen constants (PREREG-1 2.1/2.2)
Q_MAIN = 3329
N_BASES = 8
LATTICES = OrderedDict([("L7", (20, 6)), ("L8", (20, 14))])
BETA_GRID = [5, 10, 15]           # PREREG-1 2.2, d = 20
MAX_D_FOR_REDUCTION = 40
HKZ_MAX_SWEEP = 30                # carried verbatim
P_L1_TOL = 1e-6                   # PREREG-1 8.3 / 9: falsifier is ABOVE this

CAP_TOTAL = 1200.0                # task-card cap INCLUDING the install


def sha256_file(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def git(*args, cwd=REPO_ROOT):
    try:
        return subprocess.check_output(("git",) + args, cwd=cwd,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception as ex:
        return "GIT ERROR: %s" % ex


# ============================================================ prereg gate
def verify_prereg():
    """Verify PREREG-1 in BOTH directions before any measurement:
      forward  -- the working-tree file, the committed sidecar, and the BLOB
                  INSIDE the notarizing commit all hash to the same value;
      negative -- the frozen text is ABSENT at the notarizing commit's PARENT.
    The repository root is resolved and then CHECKED in this worktree.
    """
    out = OrderedDict()
    top = git("rev-parse", "--show-toplevel")
    out["repo_root_resolved"] = REPO_ROOT
    out["repo_root_from_git"] = top
    if os.path.realpath(top) != os.path.realpath(REPO_ROOT):
        raise SystemExit("ABORT: repo root mismatch %r vs %r" % (top, REPO_ROOT))

    live = sha256_file(PREREG_PATH)
    out["sha256_working_tree"] = live
    sidecar = None
    if os.path.exists(PREREG_SIDECAR_PATH):
        with open(PREREG_SIDECAR_PATH) as fh:
            sidecar = fh.read().split()[0]
    out["sha256_sidecar"] = sidecar
    out["sidecar_path"] = PREREG_SIDECAR_REL

    full = git("rev-parse", NOTARIZING_COMMIT)
    out["notarizing_commit_arg"] = NOTARIZING_COMMIT
    out["notarizing_commit_full"] = full
    blob_id = git("rev-parse", "%s:%s" % (full, PREREG_REL))
    if blob_id.startswith("GIT ERROR"):
        raise SystemExit("ABORT: cannot read notarized blob: %s" % blob_id)
    raw = subprocess.check_output(("git", "cat-file", "blob", blob_id),
                                  cwd=REPO_ROOT)
    out["sha256_notarized_blob"] = hashlib.sha256(raw).hexdigest()

    parent = git("rev-parse", "%s^" % full)
    parent_has = git("cat-file", "-e", "%s:%s" % (parent, PREREG_REL))
    out["notarizing_commit_parent"] = parent
    out["negative_test_absent_at_parent"] = parent_has.startswith("GIT ERROR")
    out["is_ancestor_of_HEAD"] = (
        subprocess.call(("git", "merge-base", "--is-ancestor", full, "HEAD"),
                        cwd=REPO_ROOT, stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL) == 0)

    agree = (live == out["sha256_notarized_blob"]
             and (sidecar is None or sidecar == live))
    out["WORKING_TREE_MATCHES_NOTARIZED_BLOB"] = bool(
        live == out["sha256_notarized_blob"])
    out["SIDECAR_AGREES"] = bool(sidecar is not None and sidecar == live)
    out["ALL_AGREE"] = bool(agree)
    if not agree:
        raise SystemExit("ABORT: PREREG-1 sha256 mismatch: %s" % json.dumps(out))
    if not out["negative_test_absent_at_parent"]:
        raise SystemExit("ABORT: frozen text present at the notarizing commit's "
                         "parent -- it was not frozen by that commit")
    if not out["is_ancestor_of_HEAD"]:
        raise SystemExit("ABORT: notarizing commit is not an ancestor of HEAD")
    return out


# ============================================================ frozen basis
def make_A(d, k, q, i):
    """CARRIED VERBATIM from BATCH-9e3584 measure_relvar.py (itself carried
    verbatim from BATCH-cbe023 measure_am4.py)."""
    m = d - k
    rng = np.random.default_rng([1, d, k, i])
    return rng.integers(0, q, size=(k, m), dtype=np.int64)


def build_basis(d, k, q, i):
    """B = [[I_k, A], [0, q*I_{d-k}]] in exact integer arithmetic, never by a
    generator.  CARRIED VERBATIM.  AM-9: k = |K_I| = the IDENTITY block."""
    B = np.zeros((d, d), dtype=np.int64)
    B[:k, :k] = np.eye(k, dtype=np.int64)
    B[:k, k:] = make_A(d, k, q, i)
    B[k:, k:] = q * np.eye(d - k, dtype=np.int64)
    return B


def verify_construction(B, d, k, q, i):
    """The 8 frozen bases are verified against the NOTARIZED TEXT of PREREG-1
    section 2.3 (family F0) BEFORE any reduction is run.  Structural, block by
    block, plus the exact determinant; not a spot check."""
    A = make_A(d, k, q, i)
    chk = OrderedDict()
    chk["shape_is_d_by_d"] = bool(B.shape == (d, d))
    chk["dtype_is_int64"] = bool(B.dtype == np.int64)
    chk["top_left_is_I_k"] = bool(np.array_equal(B[:k, :k], np.eye(k, dtype=np.int64)))
    chk["top_right_is_A_i"] = bool(np.array_equal(B[:k, k:], A))
    chk["bottom_left_is_zero"] = bool(np.array_equal(
        B[k:, :k], np.zeros((d - k, k), dtype=np.int64)))
    chk["bottom_right_is_qI"] = bool(np.array_equal(
        B[k:, k:], q * np.eye(d - k, dtype=np.int64)))
    chk["A_entries_in_range_0_to_q_minus_1"] = bool(
        A.min() >= 0 and A.max() <= q - 1)
    chk["A_seed_recipe"] = "np.random.default_rng([1, d, k, i]).integers(0, q, (k, d-k))"
    # |det B| = q^(d-k) EXACTLY, constant in i BY CONSTRUCTION (PREREG-1 2.3 F0).
    _, logabs = np.linalg.slogdet(B.astype(np.float64))
    chk["logabsdet_slogdet"] = float(logabs)
    chk["logabsdet_closed_form_q_pow_d_minus_k"] = float((d - k) * math.log(q))
    chk["logabsdet_abs_deviation"] = float(abs(logabs - (d - k) * math.log(q)))
    chk["det_matches_closed_form_to_1e_9_relative"] = bool(
        chk["logabsdet_abs_deviation"] <= 1e-9 * max(1.0, abs(logabs)))
    chk["ALL_STRUCTURAL_CHECKS_PASS"] = bool(
        chk["shape_is_d_by_d"] and chk["dtype_is_int64"]
        and chk["top_left_is_I_k"] and chk["top_right_is_A_i"]
        and chk["bottom_left_is_zero"] and chk["bottom_right_is_qI"]
        and chk["A_entries_in_range_0_to_q_minus_1"]
        and chk["det_matches_closed_form_to_1e_9_relative"])
    return chk


# --- the frozen HKZ pipeline, CARRIED VERBATIM ------------------------------
try:
    from fpylll import IntegerMatrix, GSO, LLL, BKZ, Enumeration, EnumerationError
    from fpylll.fplll.bkz_param import Strategy
    from fpylll.algorithms.bkz import BKZReduction
    import fpylll as _fp
    HAVE_FPYLLL = True
    FPYLLL_VERSION = _fp.__version__
    FPYLLL_IMPORT_ERROR = None
except Exception as _e:                                   # pragma: no cover
    HAVE_FPYLLL = False
    FPYLLL_VERSION = "IMPORT FAILED: %s" % _e
    FPYLLL_IMPORT_ERROR = "%s: %s" % (type(_e).__name__, _e)


def gram_int(M):
    G = M @ M.T
    Gr = np.rint(G)
    devmax = float(np.max(np.abs(G - Gr))) if G.size else 0.0
    return Gr, devmax, float(np.max(np.abs(Gr)))


def hkz_profile(M, d, verify=True):
    """CARRIED VERBATIM from BATCH-9e3584 measure_relvar.py.  One BKZ pass at
    block_size = d, then explicit HKZ sweeps (fpylll's svp_call discards
    improvements below lll_delta*r_i and therefore does NOT reach HKZ), then an
    INDEPENDENT per-index enumeration reporting
    hkz_violation = max_i (r_i - lambda_1(pi_i(L))^2)/r_i.  INSTRUMENT CHECK,
    not a certificate."""
    if not HAVE_FPYLLL:
        return {"status": "NOT MEASURED -- INFRASTRUCTURE (fpylll unavailable)"}
    t0 = time.time()
    Gr, devmax, gmax = gram_int(M)
    if devmax >= 0.5:
        return {"status": "NOT ADJUDICATED -- Gram integrality deviation "
                          "%.3e >= 0.5" % devmax, "gram_int_dev": devmax}
    try:
        A = IntegerMatrix(d, d)
        for i in range(d):
            for j in range(d):
                A[i, j] = int(Gr[i, j])
        Mg = GSO.Mat(A, gram=True)
        Mg.update_gso()
        LLL.Reduction(Mg)()
        strat = [Strategy(b) for b in range(d + 1)]
        bk = BKZReduction(Mg)
        bk(BKZ.Param(block_size=d, strategies=strat, max_loops=1,
                     flags=BKZ.MAX_LOOPS))
        sweeps = 0
        for sweeps in range(HKZ_MAX_SWEEP):
            changed = False
            for i in range(d - 1):
                ri = Mg.get_r(i, i)
                try:
                    nd, sol = Enumeration(Mg).enumerate(i, d, ri, 0)[0]
                except EnumerationError:
                    continue
                if nd < ri * (1 - 1e-12):
                    bk.svp_postprocessing(i, d - i, sol)
                    Mg.update_gso()
                    changed = True
            if not changed:
                break
        r = np.array([Mg.get_r(i, i) for i in range(d)], dtype=float)
        viol = None
        if verify:
            viol = 0.0
            for i in range(d - 1):
                try:
                    mn = Enumeration(Mg).enumerate(i, d, r[i] * 1.0000001, 0)[0][0]
                except EnumerationError:
                    mn = r[i]
                viol = max(viol, (r[i] - mn) / r[i])
    except Exception as ex:
        return {"status": "NOT MEASURED -- INFRASTRUCTURE (%s: %s)"
                          % (type(ex).__name__, ex)}
    logdet = 0.5 * float(np.sum(np.log(r)))
    return {"status": "ok", "r": r, "lam1sq": float(r[0]), "logdet": logdet,
            "gram_int_dev": devmax, "gram_max": gmax, "hkz_violation": viol,
            "sweeps": int(sweeps), "secs": time.time() - t0,
            "rows_passed_to_fpylll": int(d)}


# ============================================================ committed values
def committed_per_basis(doc):
    """Read the COMMITTED per-basis hkz and lam1n values for L7 and L8 out of
    results_relvar.json, route RC of PREREG-1 2.5.  The file is IMMUTABLE and is
    read only -- never edited.  In its G_REL2 block the mirrored pair 'L7/L8'
    stores, per beta and per basis, X_a = the L7 value and X_b = the L8 value."""
    out = {}
    for cand in ("hkz", "lam1n"):
        pair = doc["G_REL2"][cand]["L7/L8"]
        for beta in BETA_GRID:
            cell = pair[str(beta)]
            for i, ent in enumerate(cell["per_basis"]):
                out[(cand, "L7", beta, i)] = float(ent["X_a"])
                out[(cand, "L8", beta, i)] = float(ent["X_b"])
    return out


# ============================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    RES = OrderedDict()
    RES["task_id"] = "TASK-20260812-0e930c"
    RES["batch_id"] = "BATCH-4ed139"
    RES["goal_id"] = "GOAL-MLKEM-005"
    RES["role"] = "executor"
    RES["rider"] = "(iii) fpylll-equipped replication of the L7/L8 arm"
    RES["claim_tier"] = "toy"
    RES["FRAMING_FROZEN"] = (
        "THIS RESTORES THE COVERAGE WAVE 2 LOST AND RESOLVES NO DOUBT, THERE "
        "BEING NONE TO RESOLVE. fpylll's absence in both wave-2 sessions and in "
        "this batch's lead producer is INFRASTRUCTURE SIGNAL (AGENTS.md rule 5) "
        "and was NEVER evidence against lam1n, hkz, the 48 reductions, or their "
        "reported max hkz_violation of 0.0. A reproduction here vindicates "
        "nothing and impugns nothing; it fills a hole in coverage, and if the "
        "numbers reproduce that is exactly what was already expected.")
    RES["certificate"] = {
        "kind": "none",
        "reason": ("no discrete-log solve and no factor-base relation is claimed "
                   "or produced, so docs/claims-and-verification.md requires no "
                   "solution certificate; the hkz_violation enumeration is an "
                   "INSTRUMENT CHECK and is never a certificate")}
    RES["governed_by"] = {"prereg": PREREG_REL,
                          "prereg_section": "8.3 (rider iii); routes RC/RD of 2.5",
                          "notarizing_commit_arg": NOTARIZING_COMMIT}

    print("=" * 78)
    print("RIDER (iii) -- fpylll-equipped replication of the L7/L8 arm")
    print("BATCH-4ed139 / TASK-20260812-0e930c / GOAL-MLKEM-005")
    print("CLAIM TIER: TOY. Nothing here bears on ML-KEM security, on any FIPS")
    print("203 parameter set, on any attack cost, or on any cost model.")
    print("THIS RESTORES COVERAGE AND RESOLVES NO DOUBT, THERE BEING NONE TO")
    print("RESOLVE. fpylll's absence in wave 2 was INFRASTRUCTURE SIGNAL.")
    print("=" * 78)

    print("\n[0] PREREG-1 notarization gate -- ABORT ON MISMATCH")
    pv = verify_prereg()
    RES["prereg_verification"] = pv
    for kk in ("sha256_working_tree", "sha256_notarized_blob", "sha256_sidecar",
               "notarizing_commit_full", "negative_test_absent_at_parent",
               "is_ancestor_of_HEAD", "ALL_AGREE"):
        print("    %-38s %s" % (kk, pv[kk]))

    RES["inputs_pinned_by_sha256"] = OrderedDict([
        (PREREG_REL, sha256_file(PREREG_PATH)),
        (COMMITTED_REL, sha256_file(COMMITTED_PATH)),
        (PRODUCER_SCRIPT_REL, sha256_file(PRODUCER_SCRIPT_PATH)),
        (os.path.relpath(os.path.abspath(__file__), REPO_ROOT),
         sha256_file(os.path.abspath(__file__))),
    ])
    print("\n[0b] inputs pinned by sha256")
    for p, h in RES["inputs_pinned_by_sha256"].items():
        print("    %s  %s" % (h, p))

    RES["git"] = {
        "revision": git("rev-parse", "HEAD"),
        "dirty": bool(git("status", "--porcelain")),
        "dirty_paths": [l for l in git("status", "--porcelain").splitlines()],
        "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
    }

    # ------------------------------------------------------------------
    # environment -- RECORDED IN FULL, and compared to the producer's stack
    # ------------------------------------------------------------------
    doc = json.load(open(COMMITTED_PATH))
    prod_env = doc["environment"]
    env = OrderedDict([
        ("operating_system", platform.platform()),
        ("architecture", platform.machine()),
        ("host", socket.gethostname()),
        ("python_version", platform.python_version()),
        ("python_executable", sys.executable),
        ("dependencies", {"numpy": np.__version__, "scipy": SCIPY_VERSION,
                          "fpylll": FPYLLL_VERSION}),
        ("fpylll_import_error", FPYLLL_IMPORT_ERROR),
        ("blas_threads", {k: os.environ.get(k) for k in
                          ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                           "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
                           "NUMEXPR_NUM_THREADS")}),
        ("concurrency_note", "4-core host with one other executor running "
                             "concurrently; timings are wall clock under that "
                             "load and are reported as measured"),
    ])
    prod_dep = prod_env.get("dependencies", {})
    same = OrderedDict([
        ("operating_system", prod_env.get("operating_system") == env["operating_system"]),
        ("architecture", prod_env.get("architecture") == env["architecture"]),
        ("python_version", prod_env.get("python_version") == env["python_version"]),
        ("numpy", prod_dep.get("numpy") == np.__version__),
        ("scipy", prod_dep.get("scipy") == SCIPY_VERSION),
        ("fpylll", prod_dep.get("fpylll") == FPYLLL_VERSION),
    ])
    env["producer_environment_as_committed"] = prod_env
    env["matches_producer_field_by_field"] = same
    env["ENVIRONMENTS_DIFFER"] = bool(not all(same.values()))
    env["cross_platform_claim"] = (
        "NO CROSS-PLATFORM CLAIM IS MADE. Whether this run differs from the "
        "producer's stack is REPORTED AS MEASURED in "
        "matches_producer_field_by_field above, and a cross-platform claim "
        "would require the environments actually to differ with both recorded. "
        "PREREG-1 11.1: the 'genuinely cross-platform' reading of the L7/L8 "
        "agreement is NOT CITABLE; the citable form is a PORTABILITY result "
        "across three textually distinct implementations with fpylll pinned at "
        "0.6.4.")
    RES["environment"] = env
    print("\n[1] environment")
    print("    this run   %s | py %s | numpy %s | scipy %s | fpylll %s"
          % (env["operating_system"], env["python_version"],
             np.__version__, SCIPY_VERSION, FPYLLL_VERSION))
    print("    producer   %s | py %s | numpy %s | scipy %s | fpylll %s"
          % (prod_env.get("operating_system"), prod_env.get("python_version"),
             prod_dep.get("numpy"), prod_dep.get("scipy"), prod_dep.get("fpylll")))
    print("    ENVIRONMENTS_DIFFER = %s  (field by field: %s)"
          % (env["ENVIRONMENTS_DIFFER"],
             ", ".join("%s=%s" % kv for kv in same.items())))

    RES["AM_9_applied"] = {
        "statement": ("fpylll's k counts the q-SCALED ROWS, NOT the identity "
                      "block. k = |K_I| = the identity block throughout: "
                      "L7 k = 6, L8 k = 14; k_fpylll = d - k would be 14 and 6."),
        "rows_passed_to_fpylll_per_basis": 20,
        "why": ("what is handed to fpylll is the FULL d x d integer Gram matrix "
                "G = B B^T with d = 20 rows -- all of them, never k rows and "
                "never d - k rows. No fpylll basis generator is called anywhere; "
                "every basis is built explicitly as [[I_k, A],[0, q I_{d-k}]], "
                "so the convention is fixed STRUCTURALLY rather than by a label "
                "and fpylll is never asked to interpret a k at all."),
    }

    if not HAVE_FPYLLL:
        RES["INFRASTRUCTURE_OUTCOME"] = {
            "status": "INFRASTRUCTURE_SIGNAL -- fpylll unavailable",
            "error": FPYLLL_IMPORT_ERROR,
            "uncovered": ("hkz and lam1n at L7 and L8, beta in {5,10,15}, 8 "
                          "bases, and the max hkz_violation: ALL UNCOVERED"),
            "claims": "NONE. This is not a negative result about anything.",
        }
        RES["P_L1"] = {"verdict": "NOT EVALUATED -- INFRASTRUCTURE",
                       "reason": "fpylll unavailable; no deviation was measured "
                                 "and none is reported"}
        with open(args.out, "w") as fh:
            json.dump(RES, fh, indent=1, default=float)
        print("\n[!] fpylll unavailable -- INFRASTRUCTURE SIGNAL, nothing claimed")
        return 0

    # ------------------------------------------------------------------
    # 2.  Rebuild the 8 frozen bases and VERIFY them before any reduction
    # ------------------------------------------------------------------
    print("\n[2] rebuild the 8 frozen bases at L7 and L8 and VERIFY the "
          "construction against the notarized text BEFORE any reduction")
    bases = {}
    constr = OrderedDict()
    for lat, (d, k) in LATTICES.items():
        for i in range(N_BASES):
            B = build_basis(d, k, Q_MAIN, i)
            bases[(lat, i)] = B
            constr["%s/i%d" % (lat, i)] = verify_construction(B, d, k, Q_MAIN, i)
        ok = all(constr["%s/i%d" % (lat, j)]["ALL_STRUCTURAL_CHECKS_PASS"]
                 for j in range(N_BASES))
        print("    %-3s d=%-3d k=%-3d (k_fpylll = d-k = %d)  8 bases built, "
              "all structural checks pass: %s" % (lat, d, k, d - k, ok))
    RES["basis_construction_verification"] = {
        "reference": "PREREG-1 section 2.3, family F0, carried verbatim from "
                     "BATCH-9e3584 measure_relvar.py build_basis/make_A",
        "ALL_BASES_VERIFIED": bool(all(
            v["ALL_STRUCTURAL_CHECKS_PASS"] for v in constr.values())),
        "per_basis": constr,
    }
    if not RES["basis_construction_verification"]["ALL_BASES_VERIFIED"]:
        raise SystemExit("ABORT: a frozen basis failed its structural "
                         "verification; no reduction is run")

    # ------------------------------------------------------------------
    # 3.  The frozen HKZ pipeline -- route RD, d = 20 only
    # ------------------------------------------------------------------
    print("\n[3] frozen HKZ pipeline (route RD), d = %d <= %d"
          % (20, MAX_D_FOR_REDUCTION))
    measured = {}
    red_meta = OrderedDict()
    t_red = 0.0
    for lat, (d, k) in LATTICES.items():
        for i in range(N_BASES):
            prof = hkz_profile(bases[(lat, i)].astype(np.float64), d)
            red_meta["%s/i%d" % (lat, i)] = {
                kk: prof.get(kk) for kk in
                ("status", "hkz_violation", "sweeps", "gram_int_dev",
                 "gram_max", "secs", "rows_passed_to_fpylll")}
            if prof.get("status") != "ok":
                continue
            t_red += prof["secs"]
            r = prof["r"]
            logdet = prof["logdet"]
            logb = 0.5 * np.log(r)
            lam1n = math.exp(0.5 * math.log(prof["lam1sq"]) - logdet / d)
            for beta in BETA_GRID:
                measured[("lam1n", lat, beta, i)] = lam1n
                measured[("hkz", lat, beta, i)] = float(
                    np.mean(logb[d - beta:]) - logdet / d)
        viols = [red_meta["%s/i%d" % (lat, j)]["hkz_violation"]
                 for j in range(N_BASES)
                 if red_meta["%s/i%d" % (lat, j)].get("hkz_violation") is not None]
        print("    %-3s 8 reductions, max hkz_violation %s, %.2f s cumulative"
              % (lat, ("%.6e" % max(viols)) if viols else "n/a", t_red))
    all_viols = [v["hkz_violation"] for v in red_meta.values()
                 if v.get("hkz_violation") is not None]
    RES["reduction"] = {
        "pipeline": ("one BKZ pass at block_size = d, then explicit HKZ sweeps, "
                     "then an INDEPENDENT per-index enumeration reporting "
                     "hkz_violation. CARRIED VERBATIM from BATCH-9e3584 "
                     "measure_relvar.py. No new reduction beyond it."),
        "n_reductions": len(red_meta),
        "n_status_ok": sum(1 for v in red_meta.values() if v["status"] == "ok"),
        "max_hkz_violation_measured_here": (max(all_viols) if all_viols else None),
        "max_hkz_violation_committed_BATCH_9e3584_all_lattices":
            doc["reduction"]["max_hkz_violation_overall"],
        "committed_value_scope_note": (
            "the committed figure is the maximum over ALL of that run's "
            "reductions (L7, L8, L9, L10, L11, L12); the figure measured here "
            "is over the L7/L8 arm only. They are reported side by side and "
            "are NOT the same quantity."),
        "total_reduction_seconds": t_red,
        "per_basis": red_meta,
    }
    print("    max hkz_violation measured here (L7/L8 arm): %s"
          % RES["reduction"]["max_hkz_violation_measured_here"])

    # ------------------------------------------------------------------
    # 4.  Comparison against the COMMITTED per-basis values -- P-L1
    # ------------------------------------------------------------------
    print("\n[4] per-basis, per-cell comparison against the committed values "
          "(route RC), P-L1 tolerance %g" % P_L1_TOL)
    comm = committed_per_basis(doc)
    per_cell = OrderedDict()
    devs_all = []
    for cand in ("hkz", "lam1n"):
        for lat in LATTICES:
            for beta in BETA_GRID:
                rows = []
                cell_devs = []
                for i in range(N_BASES):
                    c = comm.get((cand, lat, beta, i))
                    m = measured.get((cand, lat, beta, i))
                    dev = None if (c is None or m is None) else abs(m - c)
                    if dev is not None:
                        cell_devs.append(dev)
                        devs_all.append(((cand, lat, beta, i), dev))
                    rows.append({"basis_i": i, "committed": c, "remeasured": m,
                                 "abs_deviation": dev,
                                 "bit_identical": (None if (c is None or m is None)
                                                   else bool(float(c).hex()
                                                             == float(m).hex()))})
                per_cell["%s/%s_b%d" % (cand, lat, beta)] = {
                    "candidate": cand, "lattice": lat, "beta": beta,
                    "n_bases": N_BASES,
                    "max_abs_deviation_in_cell": (max(cell_devs)
                                                  if cell_devs else None),
                    "n_bit_identical_of_8": sum(
                        1 for r_ in rows if r_["bit_identical"]),
                    "per_basis": rows,
                }
                print("      %-6s %-3s beta %-3d  max|dev| %s   "
                      "bit-identical %d/8"
                      % (cand, lat, beta,
                         ("%.3e" % max(cell_devs)) if cell_devs else "n/a",
                         per_cell["%s/%s_b%d" % (cand, lat, beta)]
                         ["n_bit_identical_of_8"]))
    max_dev = max((d_ for _, d_ in devs_all), default=None)
    where = max(devs_all, key=lambda t: t[1])[0] if devs_all else None
    per_cand = {}
    for cand in ("hkz", "lam1n"):
        ds = [d_ for kk, d_ in devs_all if kk[0] == cand]
        per_cand[cand] = {"n_comparisons": len(ds),
                          "max_abs_deviation": (max(ds) if ds else None),
                          "n_bit_identical": sum(
                              1 for v in per_cell.values()
                              if v["candidate"] == cand
                              for r_ in v["per_basis"] if r_["bit_identical"])}
    RES["comparison"] = {
        "committed_source": COMMITTED_REL,
        "committed_source_sha256": RES["inputs_pinned_by_sha256"][COMMITTED_REL],
        "committed_source_note": ("IMMUTABLE and read only; never edited. The "
                                  "per-basis values are read from its G_REL2 "
                                  "block for the mirrored pair L7/L8, where "
                                  "X_a is the L7 value and X_b the L8 value."),
        "n_comparisons_total": len(devs_all),
        "n_cells": len(per_cell),
        "MAX_ABS_DEVIATION": max_dev,
        "max_abs_deviation_at": ("%s/%s beta %d basis %d" % where) if where else None,
        "per_candidate": per_cand,
        "per_cell": per_cell,
    }
    print("    MAX ABSOLUTE DEVIATION over %d comparisons: %s   at %s"
          % (len(devs_all), ("%.6e" % max_dev) if max_dev is not None else "n/a",
             RES["comparison"]["max_abs_deviation_at"]))

    RES["P_L1"] = {
        "statement": "the fpylll re-measurement reproduces the committed L7/L8 "
                     "hkz and lam1n values to 6 decimals",
        "falsifier": "max absolute deviation above %g" % P_L1_TOL,
        "frozen_at": "PREREG-1 sections 8.3 and 9, notarized before this run",
        "max_abs_deviation": max_dev,
        "verdict": ("HOLDS" if (max_dev is not None and max_dev <= P_L1_TOL)
                    else ("FALSIFIED" if max_dev is not None
                          else "NOT EVALUATED -- no comparison available")),
        "coverage": "L7 and L8 only, beta in {5, 10, 15}, 8 bases, "
                    "hkz and lam1n; L1/L2, L4/L5, L9..L12 out of scope",
    }
    print("\n[5] P-L1: %s   (max abs deviation %s, falsifier > %g)"
          % (RES["P_L1"]["verdict"],
             ("%.6e" % max_dev) if max_dev is not None else "n/a", P_L1_TOL))

    RES["what_this_does_not_show"] = [
        "It resolves no doubt: there was none to resolve. It restores coverage.",
        "It vindicates no earlier number and impugns none.",
        "It is not a cross-platform result; see environment.cross_platform_claim.",
        "It says nothing about ML-KEM, any FIPS 203 parameter set, any attack "
        "cost or any cost model. CLAIM TIER TOY.",
        "It does not rescore BATCH-a44d08, does not retire AM-3, and makes no "
        "admissibility claim about any observable.",
        "The citable range is 4.87x to 31.03x; 'a factor of 6 to 31' is FALSE.",
    ]
    RES["binding_carries_in_force"] = [
        "AM-10 .. AM-14 of DEC-20260808-05b684; AM-15, AM-16 of "
        "DEC-20260809-afe29b; AM-17 of DEC-20260812-7c4a1e.",
        "AM-3 IS NOT RETIRED. BATCH-a44d08 IS NOT RESCORED IN ANY RESPECT.",
        "AM-9: fpylll's k counts the q-scaled rows, NOT the identity block.",
        "The L7/L8 agreement is a PORTABILITY result across three textually "
        "distinct implementations; 'genuinely cross-platform' is NOT CITABLE.",
        "knowledge/INDEX.md is NOT written, regenerated or staged.",
        "CLAIM TIER STAYS TOY.",
    ]
    RES["timings"] = {
        "reduction_seconds": t_red,
        "script_total_seconds": time.time() - T_START,
        "budget_wall_clock_seconds_task": 3600.0,
        "cap_including_install_seconds": CAP_TOTAL,
        "budget_note": "the wall-clock budget is a STOP, never a target; "
                       "install seconds are recorded in run_manifest.yaml",
    }
    RES["resources"] = {
        "max_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (
            1024 if platform.system() == "Linux" else 1),
        "max_rss_units": "bytes (ru_maxrss is KiB on Linux, scaled here)",
        "memory_budget_gb": 4,
    }
    RES["validity"] = {
        "status": "VALID",
        "expected_runs": 1, "used_runs": 1,
        "note": "one measurement invocation; every invocation made by this task "
                "is enumerated in run_manifest.yaml",
    }
    RES["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    with open(args.out, "w") as fh:
        json.dump(RES, fh, indent=1, default=float)
    print("\n[6] wrote %s" % args.out)
    print("    outcome row realized: R2-OUT-8 (rider iii)")
    print("    total %.2f s" % (time.time() - T_START))
    return 0


if __name__ == "__main__":
    sys.exit(main())
