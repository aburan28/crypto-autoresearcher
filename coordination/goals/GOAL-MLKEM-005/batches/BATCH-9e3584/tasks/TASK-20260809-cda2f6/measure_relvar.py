#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TASK-20260809-cda2f6 / BATCH-9e3584 / GOAL-MLKEM-005
SECTION R -- THE LEAD of the notarized pre-registration

  coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/
      TASK-20260809-4011dd/prereg.md
  sha256 190cf4740b0ecefdbe7d1da0868a6258352b044ae5e99da470060f94049c70ea
  notarized by TASK-20260809-91cf76 in commit 1aa7db5313f6d3da1f366443d4d6066597393402

WHAT THIS DECIDES
  (a) whether BATCH-cbe023's R3/R1 boundary is a fact about observables or a
      property of G-REL's normalization at ONE basis index, by recomputing
      G-REL1 and G-REL2 for X8 = rdet, X9 = lam1n and X10 = hkz over ALL 8
      FROZEN BASES at every mirrored pair;
  (b) whether the AM-4/AM-8 admissibility gate -- which AM-8 makes binding over
      EVERY candidate observable in this goal -- admits an observable carrying no
      information at all, by scoring the parameter-determined null
      X_null(B,beta) = (beta/d)*(1/d)*log|det B| through the IDENTICAL gate and
      the IDENTICAL code path with G-VAR (AM-11) as a REFUSAL criterion.

CLAIM TIER: TOY. Nothing this script computes bears on ML-KEM security, on any
FIPS 203 parameter set, on any attack cost, or on any cost model. No number
produced here may be transported to beta = 606, d = 1420, or any other
parameter set.

certificate.kind: none -- no discrete-log solve and no factor-base relation is
claimed or produced, so docs/claims-and-verification.md requires no solution
certificate. The HKZ-violation verification and the bit-identity dispersion test
carried here are INSTRUMENT CHECKS and are labelled as such, never certificates.

BOUNDED: d <= 40 for any reduction. NO NEW REDUCTION beyond the frozen HKZ
pipeline. The frozen basis construction is reused EXACTLY. No new BKZ is run
outside that pipeline.

BINDING CARRY (AM-9): k = |K_I| = the size of the IDENTITY block throughout.
fpylll's k would be k_fpylll = d - k. Every basis is built EXPLICITLY as
B = [[I_k, A],[0, q I_{d-k}]]; no fpylll basis generator is called anywhere.
The convention is fixed STRUCTURALLY, not by a label.

This script writes exactly one file: results_relvar.json, inside its own task
directory. It performs no git write and makes no commit.
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
import scipy
from scipy.stats import t as student_t

T_START = time.time()

# ---------------------------------------------------------------- paths
TASK_DIR = os.path.dirname(os.path.abspath(__file__))
TASKS_DIR = os.path.normpath(os.path.join(TASK_DIR, ".."))
BATCH_DIR = os.path.normpath(os.path.join(TASKS_DIR, ".."))
BATCHES_DIR = os.path.normpath(os.path.join(BATCH_DIR, ".."))
# batches -> GOAL-MLKEM-005 -> goals -> coordination -> <repo root>.  FOUR
# levels.  Five lands in the enclosing checkout: that was defect D-2, recorded
# in BATCH-cbe023 and NOT repeated here.  The resolution is VERIFIED below.
REPO_ROOT = os.path.normpath(os.path.join(BATCHES_DIR, "..", "..", "..", ".."))

PREREG_REL = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/"
              "TASK-20260809-4011dd/prereg.md")
PREREG_PATH = os.path.join(TASKS_DIR, "TASK-20260809-4011dd", "prereg.md")
SIDECAR_PATH = os.path.join(TASKS_DIR, "TASK-20260809-4011dd",
                            "prereg_sha256.txt")
PREREG_SHA256_EXPECTED = \
    "190cf4740b0ecefdbe7d1da0868a6258352b044ae5e99da470060f94049c70ea"
NOTARIZING_COMMIT = "1aa7db5313f6d3da1f366443d4d6066597393402"

# ------------------------------------------- frozen constants, from the prereg
TAU_REL = 0.10                      # prereg 1.5 / 6   [carried]
TAU_VAR = 0.0                       # prereg 2.5 / 6   exactly zero, bit-decided
T_CRIT_7_05 = 2.364624251592784     # prereg 2.2 / 6   [closed form]
T_CRIT_7_01 = 3.4994832973504924    # prereg 2.2 / 6   [closed form]
N_BASES = 8                         # prereg 1.1 / 6
Q_MAIN = 3329
LOG_Q_MAIN = 8.110427237575024      # prereg 6         [closed form]

LATTICES = OrderedDict([
    ("L1", (100, 30)), ("L2", (100, 70)),
    ("L4", (140, 40)), ("L5", (140, 100)),
    ("L7", (20, 6)), ("L8", (20, 14)),
    ("L9", (30, 9)), ("L10", (30, 21)),
    ("L11", (40, 12)), ("L12", (40, 28)),
])
MIRROR_PAIRS = [("L1", "L2"), ("L4", "L5"), ("L7", "L8"),
                ("L9", "L10"), ("L11", "L12")]
BETA_GRID = {100: [15, 30, 35, 50, 65], 140: [20, 40, 45, 70, 95],
             20: [5, 10, 15], 30: [7, 15, 22], 40: [10, 20, 30]}
REL1_PAIR = {100: (15, 65), 140: (20, 95),
             20: (5, 15), 30: (7, 22), 40: (10, 30)}

CANDIDATES = ["rdet", "lam1n", "hkz", "null", "rawtail"]
CAND_XID = {"rdet": "X8", "lam1n": "X9", "hkz": "X10",
            "null": "X_null", "rawtail": "X_mp"}
S_X = {c: 1.0 for c in CANDIDATES}          # prereg 1.4: s_X = 1.0 for all five
REDUCTION_CANDIDATES = {"lam1n", "hkz"}     # require the frozen HKZ pipeline
MAX_D_FOR_REDUCTION = 40                    # prereg 2.13

# Budget ladder.  A cap that binds is INFRASTRUCTURE SIGNAL (prereg R-OUT-11),
# never a refusal, never an obstruction, never a negative result.
CAP_TOTAL = 5400.0
CAP_REDUCTION_TOTAL = 3600.0
CAP_PER_REDUCTION = 420.0

HKZ_MAX_SWEEP = 30


# ============================================================ prereg gate
def sha256_file(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def git(*args, cwd=REPO_ROOT):
    try:
        return subprocess.check_output(("git",) + args, cwd=cwd,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception as ex:
        return "GIT ERROR: %s" % ex


def verify_prereg():
    """VERIFY THE NOTARIZED PREREG SHA256 FIRST AND ABORT ON MISMATCH.

    Verified in BOTH directions:
      forward  -- the working-tree file hashes to the task-card constant, the
                  sidecar agrees, and the BLOB INSIDE THE NOTARIZING COMMIT
                  hashes to the same value;
      negative -- the frozen text is ABSENT at the notarizing commit's PARENT.
    The repository root is resolved and then CHECKED, so the ancestry assertion
    is made in THIS worktree (carried repair of defect D-2).
    """
    out = OrderedDict()
    top = git("rev-parse", "--show-toplevel")
    out["repo_root_resolved"] = REPO_ROOT
    out["repo_root_from_git"] = top
    if os.path.realpath(top) != os.path.realpath(REPO_ROOT):
        raise SystemExit("ABORT: repo root mismatch %r vs %r" % (top, REPO_ROOT))

    live = sha256_file(PREREG_PATH)
    out["sha256_working_tree"] = live
    out["sha256_task_card_constant"] = PREREG_SHA256_EXPECTED
    with open(SIDECAR_PATH) as fh:
        sidecar = fh.read().split()[0]
    out["sha256_sidecar"] = sidecar

    blob = git("show", "%s:%s" % (NOTARIZING_COMMIT, PREREG_REL))
    if blob.startswith("GIT ERROR"):
        raise SystemExit("ABORT: cannot read notarized blob: %s" % blob)
    # git show strips no bytes for a text blob, but hash the raw object to be
    # exact rather than the decoded string.
    raw = subprocess.check_output(
        ("git", "cat-file", "blob",
         git("rev-parse", "%s:%s" % (NOTARIZING_COMMIT, PREREG_REL))),
        cwd=REPO_ROOT)
    out["sha256_notarized_blob"] = hashlib.sha256(raw).hexdigest()

    parent = git("rev-parse", "%s^" % NOTARIZING_COMMIT)
    parent_has = git("cat-file", "-e", "%s:%s" % (parent, PREREG_REL))
    out["notarizing_commit"] = NOTARIZING_COMMIT
    out["notarizing_commit_parent"] = parent
    out["negative_test_absent_at_parent"] = parent_has.startswith("GIT ERROR")
    out["log_all_follow_commit_count"] = len(
        [x for x in git("log", "--all", "--follow", "--format=%H", "--",
                        PREREG_REL).splitlines() if x])
    out["is_ancestor_of_HEAD"] = (
        subprocess.call(("git", "merge-base", "--is-ancestor",
                         NOTARIZING_COMMIT, "HEAD"), cwd=REPO_ROOT,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL) == 0)

    agree = (live == PREREG_SHA256_EXPECTED == sidecar
             == out["sha256_notarized_blob"])
    out["ALL_FOUR_AGREE"] = bool(agree)
    if not agree:
        raise SystemExit("ABORT: prereg sha256 mismatch: %s" % json.dumps(out))
    if not out["negative_test_absent_at_parent"]:
        raise SystemExit("ABORT: frozen text is present at the notarizing "
                         "commit's parent -- it was not frozen by that commit")
    if not out["is_ancestor_of_HEAD"]:
        raise SystemExit("ABORT: notarizing commit is not an ancestor of HEAD")
    return out


# ============================================================ frozen basis
def make_A(d, k, q, i):
    """CARRIED VERBATIM from BATCH-cbe023 measure_am4.py."""
    m = d - k
    rng = np.random.default_rng([1, d, k, i])
    return rng.integers(0, q, size=(k, m), dtype=np.int64)


def build_basis(d, k, q, i):
    """B = [[I_k, A], [0, q*I_{d-k}]] in exact integer arithmetic, never by a
    generator.  CARRIED VERBATIM.  AM-9: k = |K_I|."""
    B = np.zeros((d, d), dtype=np.int64)
    B[:k, :k] = np.eye(k, dtype=np.int64)
    B[:k, k:] = make_A(d, k, q, i)
    B[k:, k:] = q * np.eye(d - k, dtype=np.int64)
    return B


def haar_orthogonal(d, rng):
    Z = rng.standard_normal((d, d))
    Q, R = np.linalg.qr(Z)
    ph = np.sign(np.diag(R))
    ph[ph == 0] = 1.0
    return Q * ph


def perm_matrix(d, rng):
    p = rng.permutation(d)
    P = np.zeros((d, d), dtype=np.int64)
    P[np.arange(d), p] = 1
    return P


def unimodular(d, rng):
    U = np.eye(d, dtype=np.int64)
    U = U[rng.permutation(d)]
    signs = rng.integers(0, 2, size=d) * 2 - 1
    U = U * signs[:, None]
    for _ in range(d // 2):
        i, j = rng.choice(d, size=2, replace=False)
        s = int(rng.integers(0, 2)) * 2 - 1
        U[i] = U[i] + s * U[j]
    return U


# ============================================================ observables
def raw_gso_logs(B):
    """log ||b*_i|| of the ROWS of B, and log|det B|, from one QR.  NO
    reduction of any kind: B.T = Q R, so |R[i,i]| = ||b*_i|| for the rows of B
    in their given order."""
    _, R = np.linalg.qr(B.astype(np.float64).T)
    dg = np.abs(np.diag(R))
    return np.log(dg), float(np.sum(np.log(dg)))


def rdet_of(M, d):
    _, logabs = np.linalg.slogdet(M.astype(np.float64))
    return float(np.exp(logabs / d)), float(logabs)


def x_null_of(d, k, beta, q):
    """X_null(B,beta) = (beta/d)*(1/d)*log|det B|.  For
    B = [[I_k,A],[0,q I_{d-k}]], |det B| = q^(d-k) EXACTLY, independent of A.
    Computed here FROM THE MATRIX-FREE CLOSED FORM, exactly as prereg 2.6
    states it, so that its zero dispersion is a property of the observable and
    not of a float path."""
    return (beta / d) * (1.0 / d) * ((d - k) * math.log(q)) if q > 1 else 0.0


def x_rawtail_of(loggs, logdet, d, beta):
    """X_mp = mean_{i >= d-beta} log||b*_i||  -  logdet/d, from the UNREDUCED
    GSO.  The declared MUST-PASS candidate (AM-10 c)."""
    return float(np.mean(loggs[d - beta:]) - logdet / d)


# --- the frozen HKZ pipeline, CARRIED VERBATIM ------------------------------
try:
    from fpylll import IntegerMatrix, GSO, LLL, BKZ, Enumeration, EnumerationError
    from fpylll.fplll.bkz_param import Strategy
    from fpylll.algorithms.bkz import BKZReduction
    import fpylll as _fp
    HAVE_FPYLLL = True
    FPYLLL_VERSION = _fp.__version__
except Exception as _e:                                   # pragma: no cover
    HAVE_FPYLLL = False
    FPYLLL_VERSION = "IMPORT FAILED: %s" % _e


def gram_int(M):
    G = M @ M.T
    Gr = np.rint(G)
    devmax = float(np.max(np.abs(G - Gr))) if G.size else 0.0
    return Gr, devmax, float(np.max(np.abs(Gr)))


def hkz_profile(M, d, verify=True):
    """CARRIED VERBATIM from BATCH-cbe023 measure_am4.py.  One BKZ pass at
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
            "sweeps": int(sweeps), "secs": time.time() - t0}


# ============================================================ the criterion
def rho_both(x_b, x_a, s):
    """prereg 1.5 / 2.1(c): the criterion at BOTH normalizations, with the
    ratio s_X/|X| printed BESIDE the entry (AM-10 b)."""
    num = abs(x_b - x_a)
    den_floor = max(abs(x_a), s)
    den_raw = abs(x_a)
    return {
        "value_maxfloor": num / den_floor,
        "value_absX": (num / den_raw) if den_raw > 0 else None,
        "s_over_absX": (s / den_raw) if den_raw > 0 else None,
        "scale_floor_is_binding": bool(den_raw < s),
        "X_a": x_a, "X_b": x_b, "s_X": s,
    }


def summarize(vals):
    a = np.asarray([v for v in vals if v is not None], dtype=float)
    if a.size == 0:
        return None
    return {"n": int(a.size), "mean": float(a.mean()),
            "sd": float(a.std(ddof=1)) if a.size > 1 else 0.0,
            "min": float(a.min()), "median": float(np.median(a)),
            "max": float(a.max())}


def bit_identical(vals):
    """G-VAR is decided STRUCTURALLY, not by tolerance (prereg 2.5)."""
    hx = set()
    for v in vals:
        if v is None:
            return None
        hx.add(float(v).hex())
    return len(hx) == 1


# ============================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    RES = OrderedDict()
    RES["task_id"] = "TASK-20260809-cda2f6"
    RES["batch_id"] = "BATCH-9e3584"
    RES["goal_id"] = "GOAL-MLKEM-005"
    RES["role"] = "executor"
    RES["section"] = "R (LEAD)"
    RES["claim_tier"] = "toy"
    RES["certificate"] = {
        "kind": "none",
        "reason": ("no discrete-log solve and no factor-base relation is claimed "
                   "or produced, so docs/claims-and-verification.md requires no "
                   "solution certificate; the HKZ-violation verification and the "
                   "bit-identity dispersion test are INSTRUMENT CHECKS")}
    RES["governed_by"] = {"prereg": PREREG_REL,
                          "sha256": PREREG_SHA256_EXPECTED,
                          "notarizing_commit": NOTARIZING_COMMIT}

    print("=" * 78)
    print("SECTION R (LEAD) -- G-REL replication over 8 bases + G-VAR")
    print("BATCH-9e3584 / TASK-20260809-cda2f6 / GOAL-MLKEM-005")
    print("CLAIM TIER: TOY.  Nothing here bears on ML-KEM security, on any")
    print("FIPS 203 parameter set, on any attack cost, or on any cost model.")
    print("=" * 78)

    print("\n[0] prereg notarization gate -- ABORT ON MISMATCH")
    pv = verify_prereg()
    RES["prereg_verification"] = pv
    for kk in ("sha256_working_tree", "sha256_sidecar", "sha256_notarized_blob",
               "negative_test_absent_at_parent", "log_all_follow_commit_count",
               "is_ancestor_of_HEAD", "ALL_FOUR_AGREE"):
        print("    %-34s %s" % (kk, pv[kk]))

    RES["git"] = {
        "revision": git("rev-parse", "HEAD"),
        "dirty": bool(git("status", "--porcelain")),
        "dirty_paths": [l for l in git("status", "--porcelain").splitlines()],
        "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
    }
    RES["environment"] = {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "host": socket.gethostname(),
        "python_version": platform.python_version(),
        "dependencies": {"numpy": np.__version__, "scipy": scipy.__version__,
                         "fpylll": FPYLLL_VERSION},
        "blas_threads": {k: os.environ.get(k) for k in
                         ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                          "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
                          "NUMEXPR_NUM_THREADS")},
        "environment_delta_vs_BATCH_cbe023": (
            "BATCH-cbe023's Section A ran on macOS-26.6-arm64 / Python 3.13.1 / "
            "numpy 2.4.0 / scipy 1.15.3 / fpylll 0.6.4. This run is Linux "
            "x86_64 / Python 3.11 / a later numpy and scipy / fpylll 0.6.4. "
            "fpylll matches exactly; the platform, the Python and the BLAS do "
            "NOT. Every number here is measured in THIS environment and is "
            "reported as such; nothing is inherited from the earlier run and "
            "no cross-environment bitwise agreement is claimed."),
    }
    RES["frozen_constants"] = {
        "tau_rel": TAU_REL, "tau_var": TAU_VAR, "s_X": S_X,
        "t_crit_df7_two_sided_0.05": T_CRIT_7_05,
        "t_crit_df7_two_sided_0.01": T_CRIT_7_01,
        "n_bases": N_BASES, "q": Q_MAIN, "log_q": LOG_Q_MAIN,
        "beta_grid": {str(k): v for k, v in BETA_GRID.items()},
        "rel1_endpoints": {str(k): list(v) for k, v in REL1_PAIR.items()},
        "mirror_pairs": ["%s/%s" % p for p in MIRROR_PAIRS],
        "k_convention_AM9": (
            "k = |K_I| = size of the IDENTITY block throughout; fpylll's k "
            "would be k_fpylll = d - k. Every basis is BUILT EXPLICITLY as "
            "[[I_k, A],[0, q I_{d-k}]]; no fpylll basis generator is called "
            "anywhere in this run, so the convention is fixed STRUCTURALLY."),
    }
    RES["binding_carries_in_force"] = [
        "AM-10 .. AM-14 of DEC-20260808-05b684 and their binding carries.",
        "AM-3 IS NOT RETIRED; its 0.096 family-wise false-failure bound stands.",
        "BATCH-a44d08 IS NOT RESCORED IN ANY RESPECT.",
        "NOT CITABLE FROM BATCH-cbe023: 'the obstruction is relocated'; "
        "'29 of 48' without its 47-of-48 exact-null benchmark in the same "
        "sentence; 'CONSISTENT', in either direction.",
        "The 3.91% detection floor is not citable without the "
        "NEGATIVE-VARIANCE-COMPONENT qualifier; the non-degenerate figure is "
        "10.83%.",
        "AM4-OBS-1 is cited ONLY through knowledge/findings/KN-FIND-f38a89.md.",
        "AM-9: fpylll's k counts the q-scaled rows.",
        "CLAIM TIER STAYS TOY.",
    ]

    # ------------------------------------------------------------------
    # 1.  Build every frozen basis once and take every non-reduction observable
    # ------------------------------------------------------------------
    print("\n[1] frozen bases and the non-reduction observables "
          "(rdet, rawtail, null)")
    t1 = time.time()
    base = {}          # (lat, beta, i) -> {cand: value}
    per_basis_meta = {}
    for lat, (d, k) in LATTICES.items():
        for i in range(N_BASES):
            B = build_basis(d, k, Q_MAIN, i)
            rd, logabs = rdet_of(B, d)
            loggs, logdet_raw = raw_gso_logs(B)
            per_basis_meta[(lat, i)] = {
                "logdet_slogdet": logabs, "logdet_from_raw_QR": logdet_raw,
                "logdet_closed_form": (d - k) * math.log(Q_MAIN),
                "max_abs_entry": int(np.max(np.abs(B)))}
            for beta in BETA_GRID[d]:
                base[(lat, beta, i)] = {
                    "rdet": rd,
                    "rawtail": x_rawtail_of(loggs, logdet_raw, d, beta),
                    "null": x_null_of(d, k, beta, Q_MAIN),
                    "lam1n": None, "hkz": None,
                }
        print("    %-4s d=%-4d k=%-4d  8 bases built" % (lat, d, k))
    t_nonred = time.time() - t1

    # Pre-registered check: the closed-form X_null table of prereg 2.6 must be
    # reproduced by the code path.  A departure is a DEFECT (R-OUT-3).
    null_table_check = OrderedDict()
    for lat, (d, k) in LATTICES.items():
        for beta in BETA_GRID[d]:
            vals = [base[(lat, beta, i)]["null"] for i in range(N_BASES)]
            null_table_check["%s_b%d" % (lat, beta)] = {
                "value": vals[0], "bit_identical_over_8_bases": bit_identical(vals),
                "float_sd": float(np.std(vals, ddof=1))}
    RES["x_null_closed_form_reproduction"] = {
        "prereg_reference": "prereg 2.6",
        "all_bit_identical": all(v["bit_identical_over_8_bases"]
                                 for v in null_table_check.values()),
        "per_cell": null_table_check}
    print("    X_null closed-form table reproduced; bit-identical over 8 bases "
          "at every cell: %s"
          % RES["x_null_closed_form_reproduction"]["all_bit_identical"])

    # ------------------------------------------------------------------
    # 2.  The frozen HKZ pipeline for X9 / X10 on the small-d family
    # ------------------------------------------------------------------
    print("\n[2] frozen HKZ pipeline for X9 = lam1n and X10 = hkz "
          "(d <= %d only)" % MAX_D_FOR_REDUCTION)
    red_meta = OrderedDict()
    not_computed = OrderedDict()
    t_red_total = 0.0
    cap_bound = []
    for lat, (d, k) in LATTICES.items():
        if d > MAX_D_FOR_REDUCTION:
            for c in sorted(REDUCTION_CANDIDATES):
                not_computed["%s/%s" % (c, lat)] = (
                    "NOT COMPUTED -- structural: d = %d exceeds the frozen "
                    "d <= %d reduction bound of prereg 2.13, and NO NEW "
                    "REDUCTION beyond the frozen HKZ pipeline is permitted. "
                    "Declared in advance in prereg 2.13. This is neither a "
                    "zero, nor a pass, nor a fail, and it enters no count."
                    % (d, MAX_D_FOR_REDUCTION))
            print("    %-4s d=%-4d  NOT COMPUTED for lam1n/hkz (structural, "
                  "declared in advance)" % (lat, d))
            continue
        for i in range(N_BASES):
            if t_red_total > CAP_REDUCTION_TOTAL:
                cap_bound.append((lat, i, "CAP_REDUCTION_TOTAL"))
                continue
            B = build_basis(d, k, Q_MAIN, i)
            prof = hkz_profile(B.astype(np.float64), d)
            red_meta[(lat, i)] = {kk: prof.get(kk) for kk in
                                  ("status", "hkz_violation", "sweeps",
                                   "gram_int_dev", "secs")}
            if prof.get("status") != "ok":
                continue
            t_red_total += prof["secs"]
            r = prof["r"]
            logdet = prof["logdet"]
            logb = 0.5 * np.log(r)
            lam1n = math.exp(0.5 * math.log(prof["lam1sq"]) - logdet / d)
            for beta in BETA_GRID[d]:
                base[(lat, beta, i)]["lam1n"] = lam1n
                base[(lat, beta, i)]["hkz"] = float(
                    np.mean(logb[d - beta:]) - logdet / d)
        viols = [v["hkz_violation"] for v in
                 (red_meta.get((lat, j)) or {} for j in range(N_BASES))
                 if v and v.get("hkz_violation") is not None]
        print("    %-4s d=%-4d  8 reductions, max hkz_violation %s, "
              "%.2f s cumulative"
              % (lat, d, ("%.3e" % max(viols)) if viols else "n/a", t_red_total))
    RES["reduction"] = {
        "pipeline": ("one BKZ pass at block_size = d, then explicit HKZ sweeps, "
                     "then an INDEPENDENT per-index enumeration reporting "
                     "hkz_violation. CARRIED VERBATIM from BATCH-cbe023 "
                     "measure_am4.py. No new BKZ outside this pipeline."),
        "per_cell": {"%s/i%d" % k_: v for k_, v in red_meta.items()},
        "max_hkz_violation_overall": max(
            [v["hkz_violation"] for v in red_meta.values()
             if v.get("hkz_violation") is not None] or [None]),
        "total_seconds": t_red_total,
        "cap_bound_cells": ["%s/i%d (%s)" % c for c in cap_bound],
        "cap_note": ("A cap that binds is INFRASTRUCTURE SIGNAL (prereg "
                     "R-OUT-11), never a refusal, never an obstruction, and "
                     "never a negative result."),
    }
    RES["not_computed"] = not_computed

    # ------------------------------------------------------------------
    # 3.  G-VAR -- the refusal criterion, decided by BIT IDENTITY
    # ------------------------------------------------------------------
    print("\n[3] G-VAR (AM-11): between-basis dispersion at fixed (d,k,beta,q)")
    gvar = OrderedDict()
    for c in CANDIDATES:
        cells = OrderedDict()
        for lat, (d, k) in LATTICES.items():
            for beta in BETA_GRID[d]:
                vals = [base[(lat, beta, i)][c] for i in range(N_BASES)]
                if any(v is None for v in vals):
                    continue
                cells["%s_b%d" % (lat, beta)] = {
                    "n": N_BASES,
                    "bit_identical": bit_identical(vals),
                    "float_sd": float(np.std(vals, ddof=1)),
                    "mean": float(np.mean(vals)),
                    "min": float(np.min(vals)), "max": float(np.max(vals)),
                }
        n_zero = sum(1 for v in cells.values() if v["bit_identical"])
        gvar[c] = {
            "xid": CAND_XID[c],
            "n_cells": len(cells),
            "n_cells_zero_dispersion_bit_identical": n_zero,
            "ZERO_DISPERSION_EVERYWHERE": bool(cells) and n_zero == len(cells),
            "G_VAR_REFUSES": bool(cells) and n_zero == len(cells),
            "per_cell": cells,
        }
        print("    %-8s %-7s cells %-3d  bit-identical over 8 bases in %d  "
              "-> G-VAR %s"
              % (CAND_XID[c], c, len(cells), n_zero,
                 "REFUSES" if gvar[c]["G_VAR_REFUSES"] else "admits"))
    RES["G_VAR"] = {
        "definition": ("an admissible observable MUST have NON-ZERO between-basis "
                       "dispersion at fixed (d,k,beta,q); a gate that admits a "
                       "zero-dispersion closed form is declared INADMISSIBLE and "
                       "NO admissibility claim may be reported from it (AM-11)"),
        "threshold": "tau_var = 0 EXACTLY, decided by bit-identity of the 8 "
                     "IEEE-754 doubles, not by a tolerance (prereg 2.5)",
        "X7_note": ("X7 = tr(P^2) CANNOT serve as this control: it is "
                    "q-independent and k-independent, so it tests only whether "
                    "the gate refuses a CONSTANT, not whether it refuses "
                    "PARAMETER ARITHMETIC. It is not used as one here."),
        "per_candidate": gvar,
    }

    # ------------------------------------------------------------------
    # 4.  G-REL1 -- beta dependence, over all 8 bases
    # ------------------------------------------------------------------
    print("\n[4] G-REL1 (beta-dependence) over ALL 8 FROZEN BASES")
    rel1 = OrderedDict()
    for c in CANDIDATES:
        per_lat = OrderedDict()
        for lat, (d, k) in LATTICES.items():
            lo, hi = REL1_PAIR[d]
            vals_lo = [base[(lat, lo, i)][c] for i in range(N_BASES)]
            vals_hi = [base[(lat, hi, i)][c] for i in range(N_BASES)]
            if any(v is None for v in vals_lo + vals_hi):
                per_lat[lat] = {"status": not_computed.get(
                    "%s/%s" % (c, lat),
                    "NOT COMPUTED -- candidate unavailable at this lattice")}
                continue
            ent = [rho_both(vals_hi[i], vals_lo[i], S_X[c])
                   for i in range(N_BASES)]
            diffs = [vals_hi[i] - vals_lo[i] for i in range(N_BASES)]
            forced_zero = bit_identical(diffs) and abs(diffs[0]) == 0.0
            sm_max = summarize([e["value_maxfloor"] for e in ent])
            sm_abs = summarize([e["value_absX"] for e in ent])
            per_lat[lat] = {
                "beta_lo": lo, "beta_hi": hi,
                "per_basis": ent,
                "maxfloor": sm_max, "absX": sm_abs,
                "s_over_absX_mean": float(np.mean(
                    [e["s_over_absX"] for e in ent if e["s_over_absX"]
                     is not None])) if any(e["s_over_absX"] is not None
                                           for e in ent) else None,
                "scale_floor_binding_in_n_of_8": int(sum(
                    e["scale_floor_is_binding"] for e in ent)),
                "n_pass_maxfloor_of_8": int(sum(
                    e["value_maxfloor"] >= TAU_REL for e in ent)),
                "n_pass_absX_of_8": int(sum(
                    (e["value_absX"] or 0.0) >= TAU_REL for e in ent)),
                "pass_at_i0_LEGACY_READING": bool(
                    ent[0]["value_maxfloor"] >= TAU_REL),
                "pass_at_mean_over_8": bool(sm_max["mean"] >= TAU_REL),
                "FORCED_ZERO_BY_ALGEBRA": bool(forced_zero),
                "forced_zero_note": (
                    "X(beta_hi) - X(beta_lo) = 0 bit-for-bit at every basis: "
                    "this candidate takes no beta argument, so REL-1 is "
                    "identically 0 BY ALGEBRA. Reported as UNTESTED, NOT as a "
                    "failure. This is not a test that could have failed."
                    if forced_zero else None),
            }
        rel1[c] = per_lat
        shown = [(l, v) for l, v in per_lat.items() if "maxfloor" in v]
        if shown:
            print("    %-8s %-7s  mean(maxfloor) over lattices: %s"
                  % (CAND_XID[c], c,
                     "  ".join("%s=%.4f" % (l, v["maxfloor"]["mean"])
                               for l, v in shown)))
    RES["G_REL1"] = rel1

    # ------------------------------------------------------------------
    # 5.  G-REL2 -- block attribution on the mirrored pairs, over all 8 bases
    # ------------------------------------------------------------------
    print("\n[5] G-REL2 (block attribution) over ALL 8 FROZEN BASES, "
          "5 mirrored pairs")
    rel2 = OrderedDict()
    for c in CANDIDATES:
        pairs = OrderedDict()
        for (la, lb) in MIRROR_PAIRS:
            d, ka = LATTICES[la]
            key = "%s/%s" % (la, lb)
            per_beta = OrderedDict()
            for beta in BETA_GRID[d]:
                va = [base[(la, beta, i)][c] for i in range(N_BASES)]
                vb = [base[(lb, beta, i)][c] for i in range(N_BASES)]
                if any(v is None for v in va + vb):
                    per_beta[str(beta)] = {"status": not_computed.get(
                        "%s/%s" % (c, la),
                        "NOT COMPUTED -- candidate unavailable at this pair")}
                    continue
                ent = [rho_both(vb[i], va[i], S_X[c]) for i in range(N_BASES)]
                g = np.array([vb[i] - va[i] for i in range(N_BASES)],
                             dtype=float)
                sd_g = float(g.std(ddof=1))
                mean_g = float(g.mean())
                tp = (mean_g / (sd_g / math.sqrt(N_BASES))) if sd_g > 0 else None
                floor = T_CRIT_7_05 * sd_g / math.sqrt(N_BASES)
                sm_max = summarize([e["value_maxfloor"] for e in ent])
                sm_abs = summarize([e["value_absX"] for e in ent])
                per_beta[str(beta)] = {
                    "per_basis": ent,
                    "mean_gap": mean_g,
                    "sd_between_bases_k_side": float(np.std(va, ddof=1)),
                    "sd_between_bases_mirror_side": float(np.std(vb, ddof=1)),
                    "sd_paired_gap": sd_g,
                    "paired_t": tp, "df": N_BASES - 1,
                    "t_crit_0.05": T_CRIT_7_05, "t_crit_0.01": T_CRIT_7_01,
                    "significant_at_0.05": (bool(abs(tp) >= T_CRIT_7_05)
                                            if tp is not None else None),
                    "detection_floor_on_mean_gap": floor,
                    "mean_gap_below_detection_floor": bool(abs(mean_g) < floor)
                    if sd_g > 0 else None,
                    "gap_as_fraction_of_its_own_spread": (
                        abs(mean_g) / sd_g if sd_g > 0 else None),
                    "maxfloor": sm_max, "absX": sm_abs,
                    "s_over_absX_mean": float(np.mean(
                        [e["s_over_absX"] for e in ent
                         if e["s_over_absX"] is not None]))
                    if any(e["s_over_absX"] is not None for e in ent) else None,
                    "scale_floor_binding_in_n_of_8": int(sum(
                        e["scale_floor_is_binding"] for e in ent)),
                    "n_pass_maxfloor_of_8": int(sum(
                        e["value_maxfloor"] >= TAU_REL for e in ent)),
                    "n_pass_absX_of_8": int(sum(
                        (e["value_absX"] or 0.0) >= TAU_REL for e in ent)),
                    "pass_at_i0_LEGACY_READING": bool(
                        ent[0]["value_maxfloor"] >= TAU_REL),
                    "pass_at_mean_over_8": bool(sm_max["mean"] >= TAU_REL),
                    "NORMALIZATIONS_DISAGREE": bool(
                        (sm_max["mean"] >= TAU_REL)
                        != ((sm_abs["mean"] >= TAU_REL)
                            if sm_abs is not None else False)),
                }
            pairs[key] = per_beta
        rel2[c] = pairs
    RES["G_REL2"] = rel2
    for c in CANDIDATES:
        for key, per_beta in rel2[c].items():
            row = []
            for b, v in per_beta.items():
                if "mean_gap" not in v:
                    row.append("b%s=NC" % b)
                else:
                    row.append("b%s: gap %.5f sd %.5f t %s"
                               % (b, v["mean_gap"], v["sd_paired_gap"],
                                  ("%+.3f" % v["paired_t"])
                                  if v["paired_t"] is not None else "n/a"))
            print("    %-8s %-8s %s" % (CAND_XID[c], key, " | ".join(row)))

    # ------------------------------------------------------------------
    # 6.  G-REL = both clauses.  Three readings, reported side by side.
    # ------------------------------------------------------------------
    grel = OrderedDict()
    for c in CANDIDATES:
        r1 = [v for v in rel1[c].values() if "maxfloor" in v]
        r1_forced = [v for v in r1 if v["FORCED_ZERO_BY_ALGEBRA"]]
        r2cells = [v for pb in rel2[c].values() for v in pb.values()
                   if "maxfloor" in v]
        grel[c] = {
            "xid": CAND_XID[c],
            "REL1": {
                "n_lattices_scored": len(r1),
                "n_forced_zero_by_algebra": len(r1_forced),
                "UNTESTED_BY_ALGEBRA": bool(r1) and len(r1_forced) == len(r1),
                "n_pass_at_mean_over_8": sum(v["pass_at_mean_over_8"] for v in r1),
                "n_pass_at_i0_legacy": sum(v["pass_at_i0_LEGACY_READING"]
                                           for v in r1),
                "best_mean_maxfloor": max([v["maxfloor"]["mean"] for v in r1],
                                          default=None),
                "best_mean_absX": max([v["absX"]["mean"] for v in r1
                                       if v["absX"] is not None], default=None),
            },
            "REL2": {
                "n_cells_scored": len(r2cells),
                "n_pass_at_mean_over_8": sum(v["pass_at_mean_over_8"]
                                             for v in r2cells),
                "n_pass_at_i0_legacy": sum(v["pass_at_i0_LEGACY_READING"]
                                           for v in r2cells),
                "n_cells_normalizations_disagree": sum(
                    v["NORMALIZATIONS_DISAGREE"] for v in r2cells),
                "n_cells_gap_below_detection_floor": sum(
                    1 for v in r2cells if v["mean_gap_below_detection_floor"]),
                "n_cells_significant_at_0.05": sum(
                    1 for v in r2cells if v["significant_at_0.05"]),
                "best_mean_maxfloor": max([v["maxfloor"]["mean"]
                                           for v in r2cells], default=None),
                "best_mean_absX": max([v["absX"]["mean"] for v in r2cells
                                       if v["absX"] is not None], default=None),
            },
        }
        rel1_ok = (grel[c]["REL1"]["n_pass_at_mean_over_8"] > 0
                   and not grel[c]["REL1"]["UNTESTED_BY_ALGEBRA"])
        rel2_ok = grel[c]["REL2"]["n_pass_at_mean_over_8"] > 0
        grel[c]["G_REL_PASS_at_mean_over_8"] = bool(rel1_ok and rel2_ok)
        grel[c]["aggregation_rule_disclosure"] = (
            "THE PRE-REGISTRATION DID NOT FREEZE A SINGLE AGGREGATION RULE for "
            "turning 8 per-basis criterion values into one pass/fail. This run "
            "reports THREE readings side by side -- the legacy i = 0 draw, the "
            "count of passing bases out of 8, and the mean over the 8 -- and "
            "uses the MEAN over the 8 bases as the headline reading. That "
            "choice is an IMPLEMENTATION COMPLETION, declared here, not a "
            "frozen clause; every underlying per-basis value is in this file so "
            "a reviewer can rescore under any other rule.")
    RES["G_REL"] = grel

    # ------------------------------------------------------------------
    # 7.  The FORCED arithmetic, reported as forced
    # ------------------------------------------------------------------
    print("\n[6] what is FORCED by algebra, reported as UNTESTED not as passed")
    d0, k0 = LATTICES["L7"]
    B0 = build_basis(d0, k0, Q_MAIN, 0)
    rng_h = np.random.default_rng([2, d0, k0, 5, 0])
    H = haar_orthogonal(d0, rng_h)
    U = unimodular(d0, np.random.default_rng([4, d0, k0, 5, 0]))
    Pi = perm_matrix(d0, np.random.default_rng([3, d0, k0, 5, 0]))
    rd_id, _ = rdet_of(B0, d0)
    forced = OrderedDict()
    forced["rdet_T1_ambient_isometry_residual"] = {
        "value": abs(rdet_of(B0.astype(np.float64) @ H, d0)[0] - rd_id),
        "status": "UNTESTED -- |det BH| = |det B| BY ALGEBRA. Not a test that "
                  "could have failed."}
    forced["rdet_T3_unimodular_residual"] = {
        "value": abs(rdet_of(U @ B0, d0)[0] - rd_id),
        "status": "UNTESTED -- |det UB| = |det B| BY ALGEBRA (|det U| = 1)."}
    forced["rdet_T2_permutation_residual"] = {
        "value": abs(rdet_of(Pi @ B0, d0)[0] - rd_id),
        "status": "UNTESTED -- a row permutation changes |det| by a sign only."}
    lg0, ld0 = raw_gso_logs(B0)
    lgH, ldH = raw_gso_logs((B0.astype(np.float64) @ H))
    forced["rawtail_T1_ambient_isometry_residual_beta5"] = {
        "value": abs(x_rawtail_of(lgH, ldH, d0, 5)
                     - x_rawtail_of(lg0, ld0, d0, 5)),
        "status": "UNTESTED -- Gram-Schmidt is equivariant under an ambient "
                  "isometry, so every ||b*_i|| is preserved EXACTLY. Residual "
                  "measures float64 QR noise and nothing else."}
    forced["X_null_all_transforms"] = {
        "value": 0.0,
        "status": "UNTESTED -- X_null is a closed form in (d,k,beta,q) and "
                  "consumes no matrix at all, so every transform residual is 0 "
                  "identically. It is not invariant; it is BLIND."}
    forced["X_null_G_Q_at_q_equals_1"] = {
        "value_at_q3329_L1_b15": x_null_of(100, 30, 15, Q_MAIN),
        "value_at_q1_L1_b15": x_null_of(100, 30, 15, 1),
        "criterion": abs(x_null_of(100, 30, 15, Q_MAIN)
                         - x_null_of(100, 30, 15, 1))
        / max(abs(x_null_of(100, 30, 15, Q_MAIN)), 1.0),
        "status": "PASSES G-Q BY ALGEBRA at tau_q = 0.10 -- and the binding "
                  "carry applies: at q = 1, A = 0 and B = I_d, so this rung "
                  "compares a q-ary lattice against Z^d. It does not "
                  "demonstrate that the criterion separates informative from "
                  "uninformative observables."}
    forced["X9_X10_T1_via_integer_Gram"] = {
        "status": "UNTESTED -- computed through the integer Gram matrix, where "
                  "G(BH) = B B^T identically (binding carry 8). A 0.0 T1 "
                  "residual there is not a test that could have failed."}
    RES["forced_arithmetic"] = forced
    for kk, vv in forced.items():
        print("    %-46s %s" % (kk, vv["status"].split(" -- ")[0]))

    # ------------------------------------------------------------------
    # 8.  The three questions the task exists to answer
    # ------------------------------------------------------------------
    hkz_l7 = rel2["hkz"].get("L7/L8", {})
    hkz_b5 = hkz_l7.get("5", {})
    ans = OrderedDict()
    ans["i_is_R3_for_hkz_a_finding_or_a_normalization_artifact"] = {
        "n_cells_normalizations_disagree_for_hkz":
            grel["hkz"]["REL2"]["n_cells_normalizations_disagree"],
        "hkz_REL2_best_mean_maxfloor": grel["hkz"]["REL2"]["best_mean_maxfloor"],
        "hkz_REL2_best_mean_absX": grel["hkz"]["REL2"]["best_mean_absX"],
        "L7_L8_beta5_mean_gap": hkz_b5.get("mean_gap"),
        "L7_L8_beta5_sd_paired_gap": hkz_b5.get("sd_paired_gap"),
        "L7_L8_beta5_paired_t": hkz_b5.get("paired_t"),
        "L7_L8_beta5_below_detection_floor":
            hkz_b5.get("mean_gap_below_detection_floor"),
    }
    ans["ii_is_R1_is_empty_more_than_a_fact_about_the_candidate_list"] = {
        "candidates_scored_here": [CAND_XID[c] for c in CANDIDATES],
        "n_passing_G_REL_at_mean_over_8":
            sum(grel[c]["G_REL_PASS_at_mean_over_8"] for c in CANDIDATES),
        "which_pass": [CAND_XID[c] for c in CANDIDATES
                       if grel[c]["G_REL_PASS_at_mean_over_8"]],
    }
    ans["iii_does_the_gate_need_a_dispersion_criterion"] = {
        "X_null_passes_G_REL": grel["null"]["G_REL_PASS_at_mean_over_8"],
        "X_null_zero_dispersion_everywhere":
            gvar["null"]["ZERO_DISPERSION_EVERYWHERE"],
        "G_VAR_FIRES": bool(grel["null"]["G_REL_PASS_at_mean_over_8"]
                            and gvar["null"]["ZERO_DISPERSION_EVERYWHERE"]),
    }
    RES["THE_THREE_QUESTIONS"] = ans

    # outcome map rows realized
    outcomes = []
    if ans["iii_does_the_gate_need_a_dispersion_criterion"]["G_VAR_FIRES"]:
        outcomes.append("R-OUT-1")
    elif not grel["null"]["G_REL_PASS_at_mean_over_8"]:
        outcomes.append("R-OUT-2")
    if (grel["null"]["G_REL_PASS_at_mean_over_8"]
            and not gvar["null"]["ZERO_DISPERSION_EVERYWHERE"]):
        outcomes.append("R-OUT-3")
    outcomes.append("R-OUT-4" if grel["rawtail"]["G_REL_PASS_at_mean_over_8"]
                    else "R-OUT-5")
    if hkz_b5:
        sig = hkz_b5.get("significant_at_0.05")
        outcomes.append("R-OUT-7" if sig else "R-OUT-6")
    n_dis = sum(grel[c]["REL2"]["n_cells_normalizations_disagree"]
                for c in CANDIDATES)
    outcomes.append("R-OUT-8" if n_dis > 0 else "R-OUT-9")
    if not_computed:
        outcomes.append("R-OUT-10")
    if cap_bound:
        outcomes.append("R-OUT-11")
    RES["outcome_rows_realized"] = outcomes
    RES["outcome_map_reference"] = "prereg 2.10"

    RES["predictions"] = {
        "P-R1_rawtail_MUST_PASS": {
            "realized": grel["rawtail"]["G_REL_PASS_at_mean_over_8"],
            "falsifier": "X_mp fails G-REL1 or G-REL2 at a majority of "
                         "computable pairs"},
        "P-R2_X_null_walks_the_gate": {
            "realized_G_REL": grel["null"]["G_REL_PASS_at_mean_over_8"],
            "G_NUM_G_INV_G_Q": "PASSES BY ALGEBRA -- UNTESTED, see "
                               "forced_arithmetic"},
        "P-R3_X_null_zero_dispersion": {
            "realized": gvar["null"]["ZERO_DISPERSION_EVERYWHERE"]},
        "P-R4_G_VAR_fires": {
            "realized": ans["iii_does_the_gate_need_a_dispersion_criterion"]
            ["G_VAR_FIRES"]},
        "P-R5_rdet_lam1n_REL1_forced_zero": {
            "rdet": grel["rdet"]["REL1"]["UNTESTED_BY_ALGEBRA"],
            "lam1n": grel["lam1n"]["REL1"]["UNTESTED_BY_ALGEBRA"]},
        "P-R6_hkz_L7L8_beta5_not_significant": {
            "realized": (not hkz_b5.get("significant_at_0.05"))
            if hkz_b5 else None,
            "our_mean_gap": hkz_b5.get("mean_gap"),
            "our_paired_t": hkz_b5.get("paired_t"),
            "quoted_review_measurement_NOT_A_BASELINE": {
                "mean_gap": 0.00103, "paired_t": -0.064,
                "sd_k6": 0.02389, "sd_k14": 0.03924,
                "source": "BATCH-cbe023/reviews/TASK-20260808-6de788/"
                          "red_team_report.md RT-A2 / section 2.2"}},
        "P-R7_normalizations_disagree_somewhere": {
            "realized": n_dis > 0, "n_cells": n_dis},
    }

    RES["timings"] = {
        "non_reduction_seconds": t_nonred,
        "reduction_seconds": t_red_total,
        "total_seconds": time.time() - T_START,
        "budget_wall_clock_seconds": CAP_TOTAL,
        "budget_note": "the wall-clock budget is a STOP, never a target",
    }
    RES["resources"] = {
        "max_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (
            1024 if platform.system() == "Linux" else 1),
        "max_rss_units": "bytes (ru_maxrss is KiB on Linux, scaled here)",
    }
    RES["validity"] = {
        "status": "VALID",
        "expected_runs": 1, "used_runs": 1,
        "caps_bound": bool(cap_bound),
        "note": "A cap that binds is INFRASTRUCTURE SIGNAL, never a refusal, "
                "never an obstruction, never a negative result.",
    }
    RES["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    with open(args.out, "w") as fh:
        json.dump(RES, fh, indent=1, default=float)
    print("\n[7] wrote %s" % args.out)
    print("    outcome rows realized: %s" % ", ".join(outcomes))
    print("    total %.2f s" % (time.time() - T_START))
    return 0


if __name__ == "__main__":
    sys.exit(main())
