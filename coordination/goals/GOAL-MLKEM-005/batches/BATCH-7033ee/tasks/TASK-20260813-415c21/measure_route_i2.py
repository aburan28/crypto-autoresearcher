#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TASK-20260813-415c21 / BATCH-7033ee / GOAL-MLKEM-005
THE LEAD PRODUCER: RC-3 carry + build & run ROUTE-I2

Governed by:
  coordination/goals/GOAL-MLKEM-005/batches/BATCH-7033ee/tasks/
      TASK-20260813-61dab8/prereg.md                              (PREREG-4)
  sha256 (prereg.md)  b781b8c1aef9463642a1740bac4093bf22fcae0fe75a3389b5be7a4c826d4f7e
  notarized by TASK-20260813-30cdca, commit e40098f4f9c41be88a7e1c4970e39444247a4c53

WHAT THIS SCRIPT DOES, in the order PREREG-4 requires
  (0) Carries PREREG-4 section 1's frozen RC-3 correction VERBATIM into its
      own output -- no recomputation.
  (1) Obligation 0 (PREREG-4 2.3): reads (never recomputes) results_relvar.json
      and independently confirms ROUTE-P's per-basis coverage at all 18 cells
      before writing a single line of reduction code.
  (2) Builds ROUTE-I2: a genuinely non-code-shared re-implementation of the
      F0 basis construction and of a HKZ-style reduction/enumeration
      pipeline, satisfying PREREG-4 2.2's independence requirements.
  (3) Obligation 1 (PREREG-4 2.4): computes lam1n/hkz via ROUTE-I2 at every
      basis of every cell, D_route_independent, s_c^fib, verdict, and a
      per-basis violation/optimality diagnostic.
  (4) Obligation 2 (PREREG-4 2.5): aggregates COVERED2/UNCOVERED2, compares
      against PREREG-3's own D_route, and reports summary statistics.
  (5) Reads off the termination branch under PREREG-4 2.6's frozen precedence
      and the PREREG-4 2.7 revisit list.

INDEPENDENCE (PREREG-4 2.2), STATED HERE SO IT CANNOT BE MISSED
  This script does NOT import, exec, copy-paste or transliterate make_A,
  build_basis, hkz_profile or gram_int from measure_am4.py / measure_relvar.py
  / replicate_l7l8.py, and does NOT import fpylll AT ALL -- this environment
  has no fpylll, sage or flint installed at dispatch time (declared gap G-5),
  and even if it did, using it would not discharge the independence
  requirement (a different algorithmic path is required, not merely a
  different file). The basis construction below re-derives PREREG-4 2.1's
  mathematical specification directly from numpy.random.default_rng, which
  PREREG-4 2.1 itself states is REQUIRED (reproducing the same public seed
  formula is not a code-sharing violation; it is the frozen INPUT both
  routes must consume for any comparison to be meaningful). The reduction
  pipeline is a from-scratch LLL (delta = 0.999, chosen explicitly DIFFERENT
  from measure_relvar.py's fpylll-default ~0.99) followed by a progressive,
  increasing-block-size local-enumeration sweep with a FIXED-PIVOT
  size-reduction completion (never an ordinary LLL call on the post-insertion
  block, which was verified during development to sometimes swap the very
  vector the enumeration just found back out of place) -- see
  report_route_i2.md for the full list of genuine algorithmic differences
  from hkz_profile's pipeline.

CLAIM TIER: TOY, UNCONDITIONALLY. Nothing this script computes bears on
ML-KEM security, on any FIPS 203 parameter set, on any attack cost, or on
any cost model. No reduction above d = 40, anywhere, for any reason. No
number here transports beyond the exact lattices/betas/bases measured.

certificate.kind: none -- no discrete-log solve and no factor-base relation
is claimed or produced. The logdet-invariance self-check and the per-index
enumeration diagnostic below are INSTRUMENT CHECKS on this script's OWN
reduction, never certificates of any external claim.

BOUNDED: hard wall-clock caps are enforced throughout (see BUDGET below); a
cap that binds is reported as infrastructure signal, per PREREG-4 2.6's
T-INDEP-NODATA branch and PREREG-4's own not_computed convention, never as a
route disagreement or a dispersion finding.

This script writes exactly one file: results_route_i2.json, inside its own
task directory. It performs no git write and makes no commit.
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

T_START = time.time()

# --------------------------------------------------------------- paths
TASK_DIR = os.path.dirname(os.path.abspath(__file__))
TASKS_DIR = os.path.normpath(os.path.join(TASK_DIR, ".."))
BATCH_DIR = os.path.normpath(os.path.join(TASKS_DIR, ".."))
BATCHES_DIR = os.path.normpath(os.path.join(BATCH_DIR, ".."))
# batches -> GOAL-MLKEM-005 -> goals -> coordination -> <repo root>. FOUR
# levels, exactly the resolution measure_relvar.py's own comment records
# fixing (defect D-2) -- re-derived here independently, verified below.
REPO_ROOT = os.path.normpath(os.path.join(BATCHES_DIR, "..", "..", "..", ".."))

PREREG_REL = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-7033ee/tasks/"
              "TASK-20260813-61dab8/prereg.md")
PREREG_PATH = os.path.join(REPO_ROOT, PREREG_REL)
PREREG_SHA256_EXPECTED = \
    "b781b8c1aef9463642a1740bac4093bf22fcae0fe75a3389b5be7a4c826d4f7e"
NOTARIZING_COMMIT = "e40098f4f9c41be88a7e1c4970e39444247a4c53"

RESULTS_RELVAR_REL = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/"
                       "tasks/TASK-20260809-cda2f6/results_relvar.json")
RESULTS_RELVAR_PATH = os.path.join(REPO_ROOT, RESULTS_RELVAR_REL)

RESULTS_C3LANE_REL = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/"
                       "tasks/TASK-20260813-7b3039/results_c3lane.json")
RESULTS_C3LANE_PATH = os.path.join(REPO_ROOT, RESULTS_C3LANE_REL)

# --------------------------------------------------------------- frozen scope
Q_MAIN = 3329
N_BASES = 8
LATTICES = OrderedDict([("L7", (20, 6)), ("L9", (30, 9)), ("L11", (40, 12))])
BETA_GRID = {"L7": [5, 10, 15], "L9": [7, 15, 22], "L11": [10, 20, 30]}
MIRROR_PAIR = {"L7": "L7/L8", "L9": "L9/L10", "L11": "L11/L12"}
CANDIDATES = ["lam1n", "hkz"]

# Per-lattice wall-clock caps for the ROUTE-I2 reduction of ONE basis, and for
# its independent post-hoc violation diagnostic. Chosen from empirical timing
# during development (documented in report_route_i2.md), sized so that
# N_BASES=8 * 3 lattices fits inside the 7200s hard budget with margin, while
# giving d=40 (the most expensive lattice) the largest allowance. A cap that
# binds is reported, never silently absorbed.
REDUCE_TIME_CAP = {"L7": 90.0, "L9": 220.0, "L11": 340.0}
DIAG_TIME_CAP = {"L7": 30.0, "L9": 30.0, "L11": 45.0}
# Block sizes tried during the progressive sweep. Capped below full d for L11
# (28 rather than 40) because full-width enumeration at d=40 was empirically
# the dominant cost and the dominant source of numerical-breakdown skips
# (see report_route_i2.md) -- disclosed here as a genuine, reported
# limitation, not a silent shortcut.
BLOCK_SCHEDULE_CAP = {"L7": 20, "L9": 30, "L11": 28}
DIAG_MAX_BLOCK = {"L7": None, "L9": None, "L11": 25}
ENUM_NODE_CAP = 200_000
MAX_OUTER_SWEEPS = 30
LLL_DELTA = 0.999          # PREREG-4 2.2(2): a DIFFERENT delta from fpylll's
                            # LLL.Reduction(...)() default of ~0.99.
GLOBAL_BUDGET_SECONDS = 7200.0
GLOBAL_SAFETY_MARGIN_SECONDS = 400.0   # stop issuing new reductions this
                                        # much before the hard budget so
                                        # obligation 2 / JSON write always fit


def elapsed():
    return time.time() - T_START


def budget_remaining():
    return GLOBAL_BUDGET_SECONDS - elapsed()


# --------------------------------------------------------------- git / hash
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
    out = OrderedDict()
    top = git("rev-parse", "--show-toplevel")
    out["repo_root_resolved"] = REPO_ROOT
    out["repo_root_from_git"] = top
    out["repo_root_matches"] = bool(os.path.realpath(top) == os.path.realpath(REPO_ROOT))
    live = sha256_file(PREREG_PATH)
    out["sha256_working_tree"] = live
    out["sha256_expected"] = PREREG_SHA256_EXPECTED
    out["sha256_matches"] = bool(live == PREREG_SHA256_EXPECTED)
    out["notarizing_commit"] = NOTARIZING_COMMIT
    out["is_ancestor_of_HEAD"] = (
        subprocess.call(("git", "merge-base", "--is-ancestor",
                         NOTARIZING_COMMIT, "HEAD"), cwd=REPO_ROOT,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL) == 0)
    return out


# =======================================================================
# RC-3 -- CARRIED VERBATIM FROM PREREG-4 SECTION 1. NO RECOMPUTATION.
# =======================================================================
RC3_FROZEN_TEXT_VERBATIM = r"""
BATCH-fbb639's R-C-OUT-0 coverage table is corrected at four hkz
cells, per the Red Team's probe_coverage_beta_mismatch_output.json
(TASK-20260813-6ab893), read directly and carried without recomputation:

1. hkz/L9_b15 and hkz/L11_b20 are restated as genuinely
   UNCOVERED, not COVERED. Beta 15 (L9) and beta 20 (L11) are the
   *middle* beta of each lattice's three-point grid and are not
   REL1-pair endpoints in results_am4.json -- am4_has_a_genuine_value_
   at_this_beta: false for both, confirmed against that file's own
   declared beta_lo/beta_hi fields (L9: lo=7, hi=22; L11: lo=10,
   hi=30). The value measure_c3lane.py read and reported as this cell's
   ROUTE-I comparison was in fact the beta_lo comparison of a
   different beta, silently substituted with no genuine second-route
   value existing for the cited beta.
2. hkz/L9_b22 and hkz/L11_b30 are restated with the corrected TRUE
   beta_hi-based D_route source. Both cells *are* genuine REL1-pair
   endpoints (beta_hi), but measure_c3lane.py's check reads only
   am4_row['X_lo'] unconditionally, so the reported D_route for these
   two beta_hi cells was in fact computed against the wrong endpoint
   of the pair (the beta_lo value, not the beta_hi value the cell
   itself is at). The corrected, genuinely-beta_hi-sourced comparison is:

   | cell | am4 X_hi | relvar X (basis 0) | true D_route |
   |---|---|---|---|
   | hkz/L9_b22  | -0.11249180258058367 | -0.11249180258058367 | 0.0 |
   | hkz/L11_b30 | -0.13095122117764646 | -0.13095122117764646 | 0.0 |

   D_route is numerically unchanged at exactly 0.0 for both cells
   under the corrected source -- this is a provenance-labelling
   correction (which stored value was cited as the cell's comparison), not
   a correction that changes any reported number or verdict.

Corrected coverage fraction. lam1n's 9 cells are unaffected by this
correction (all remain COVERED at 9/9, per the beta-independence
argument above). hkz's corrected coverage is 7 of 9 cells (L7 b5/b10/
b15; L9 b7, b22; L11 b10, b30), with hkz/L9_b15 and hkz/L11_b20
restated UNCOVERED. The corrected total across lam1n + hkz is 16 of
18, not 18 of 18 as BATCH-fbb639 reported (rawtail's coverage --
ROUTE-W only, never counted -- is untouched by this correction).

This supersedes BATCH-fbb639's R-C-OUT-0 coverage table at exactly
these four cells and its "18 of 27" coverage-fraction statement wherever
quoted without this correction in the same sentence. It does not change
results_c3lane.json's D_route value at any cell, and it does not
change the fired termination branch.

EFFECT ON THE FIRED TERMINATION BRANCH -- STATED, NOT RE-ARGUED. Per the
Red Team's own probe output, T-C3LANE-OPEN-PARTIAL still fires after this
correction: 16 genuinely-covered cells (all 9 lam1n cells plus hkz's 7
genuinely-covered cells) still show EXCEEDS, SOME-EXCEEDS still holds
over the corrected COVERED set, and the -PARTIAL suffix was already
applicable at 18/27 and remains applicable at the corrected, smaller
coverage count. This correction narrows and corrects the coverage table;
it does not overturn the branch, and this document does not re-litigate
that conclusion -- it is carried here as background so RC-3's scope is
clear, and restated as committed, citable text by this batch's ledger
archive exactly as PREREG-3 3.7 required for RC-1/RC-2.

NO RE-RUN IS REQUIRED, AND NONE IS PERMITTED HERE. measure_c3lane.py,
results_c3lane.json and report_c3lane.md are immutable committed
artifacts (TASK-20260813-7b3039, archived at TASK-20260813-7ac7cd) and
are not edited, not re-run, and not vendored. The lead producer of this
batch carries the frozen text above into its own report by quotation,
attributed to PREREG-4 section 1, and does not recompute anything for RC-3.
""".strip()


# =======================================================================
# ROUTE-I2 -- fresh basis construction, re-derived from PREREG-4 2.1's
# mathematical specification. NOT imported/transcribed from build_basis.
# =======================================================================
def route_i2_basis(d, k, q, i):
    """B = [[I_k, A],[0, q*I_{d-k}]], A drawn i.i.d. uniform on {0..q-1} via
    numpy.random.default_rng([1, d, k, i]).integers(...). This seed formula
    is the FROZEN INPUT SPECIFICATION (PREREG-1 2.2/2.3's F0, restated by
    PREREG-4 2.1) that BOTH routes must consume for D_route to be
    interpretable -- PREREG-4 2.1 states explicitly that reproducing it from
    the public formula, in fresh code, is REQUIRED, not a code-sharing
    violation."""
    rng = np.random.default_rng([1, d, k, i])
    A = rng.integers(0, q, size=(k, d - k), dtype=np.int64)
    B = np.zeros((d, d), dtype=np.int64)
    B[:k, :k] = np.eye(k, dtype=np.int64)
    B[:k, k:] = A
    B[k:, k:] = q * np.eye(d - k, dtype=np.int64)
    return B


# --------------------------------------------------------------- GSO (own)
def gso_full(B):
    """Classical Gram-Schmidt recurrence computed directly from inner
    products (NOT via QR, and NOT via gram_int's Gram-matrix path) --
    mu[i,j] and r[i] = ||b*_i||^2 for the rows of B in their given order."""
    n = B.shape[0]
    Bf = B.astype(np.float64)
    Bstar = np.zeros_like(Bf)
    mu = np.eye(n)
    r = np.zeros(n)
    for i in range(n):
        v = Bf[i].copy()
        for j in range(i):
            mu[i, j] = np.dot(Bf[i], Bstar[j]) / r[j]
            v -= mu[i, j] * Bstar[j]
        Bstar[i] = v
        r[i] = np.dot(v, v)
    return mu, r, Bstar


def gso_continue(B, mu, r, Bstar, start):
    """Recompute mu/r/Bstar for rows [start, n) only, reusing rows [0,start)
    which are provably unchanged (ROUTE-I2 never modifies a row below the
    insertion point it is currently working on) -- an efficiency device with
    no bearing on independence (it computes the identical numbers a full
    recompute would)."""
    n = B.shape[0]
    Bf = B.astype(np.float64)
    mu = mu.copy(); r = r.copy(); Bstar = Bstar.copy()
    for i in range(start, n):
        v = Bf[i].copy()
        for j in range(i):
            mu[i, j] = np.dot(Bf[i], Bstar[j]) / r[j]
            v -= mu[i, j] * Bstar[j]
        Bstar[i] = v
        r[i] = np.dot(v, v)
    return mu, r, Bstar


# --------------------------------------------------------------- LLL (own)
def lll_reduce_inplace(B, delta=LLL_DELTA):
    """Textbook LLL (Lenstra-Lenstra-Lovasz) via the classical Gram-Schmidt
    recurrence above -- no fpylll IntegerMatrix/GSO.Mat/LLL.Reduction call
    anywhere. delta = 0.999 (PREREG-4 2.2 requirement 2's named difference)."""
    B = B.copy().astype(np.int64)
    n = B.shape[0]
    mu, r, _ = gso_full(B)
    k = 1
    steps = 0
    while k < n:
        steps += 1
        for j in range(k - 1, -1, -1):
            q = round(mu[k, j])
            if q != 0:
                B[k] -= q * B[j]
                mu, r, _ = gso_full(B)
        if r[k] >= (delta - mu[k, k - 1] ** 2) * r[k - 1]:
            k += 1
        else:
            B[[k - 1, k]] = B[[k, k - 1]]
            mu, r, _ = gso_full(B)
            k = max(k - 1, 1)
    return B, steps


# --------------------------------------------------------------- enumeration
def zigzag(c):
    """Yields integers in strictly increasing distance from c, nearest
    first -- the standard Schnorr-Euchner search order, implemented here as
    a plain generator (no fpylll Enumeration object anywhere)."""
    x0 = round(c)
    yield x0
    delta = 1
    while True:
        a, b = x0 + delta, x0 - delta
        if abs(a - c) <= abs(b - c):
            yield a; yield b
        else:
            yield b; yield a
        delta += 1


def enum_shortest(mu, r, start, n, bound2, node_cap=ENUM_NODE_CAP):
    """Depth-first, zig-zag-ordered branch-and-bound enumeration for the
    shortest NONZERO vector of the projected block [start, start+n), given
    the GLOBAL mu/r arrays (whose [start:,start:] slice IS that block's own
    Gram-Schmidt data, by the recursive definition of Gram-Schmidt).
    Genuinely different code path from fpylll's Enumeration class: no
    Enumeration object, no svp_call, own recursion, own pruning. Returns
    (coeffs, best_norm2, node_count, node_cap_hit)."""
    v = [0] * n

    class _St:
        pass
    st = _St()
    st.norm2 = bound2
    st.coeffs = None
    st.nodes = 0
    hit_cap = [False]

    def rec(t, partial):
        if hit_cap[0]:
            return
        st.nodes += 1
        if st.nodes > node_cap:
            hit_cap[0] = True
            return
        if t < 0:
            if 1e-9 < partial < st.norm2:
                st.norm2 = partial
                st.coeffs = tuple(v)
            return
        c = 0.0
        for i in range(t + 1, n):
            if v[i] != 0:
                c -= mu[start + i, start + t] * v[i]
        rt = r[start + t]
        for x in zigzag(c):
            contrib = (x - c) ** 2 * rt
            new_partial = partial + contrib
            if new_partial >= st.norm2:
                break
            v[t] = x
            rec(t - 1, new_partial)
            if hit_cap[0]:
                return
        v[t] = 0

    rec(n - 1, 0.0)
    return st.coeffs, (st.norm2 if st.coeffs is not None else None), st.nodes, hit_cap[0]


# --------------------------------------------------------------- insertion
def ext_gcd(a, b):
    """Standard extended Euclid: returns (g, s, t) with s*a + t*b = g,
    g = gcd(|a|,|b|), g >= 0."""
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
    if old_r < 0:
        old_r, old_s, old_t = -old_r, -old_s, -old_t
    return old_r, old_s, old_t


def insert_combination(coeffs, rows):
    """Given integer coeffs (not all zero) and matching integer row vectors,
    returns (new_rows, ok) such that new_rows[0] = (sum coeffs[t]*rows[t]) /
    gcd(coeffs), and new_rows is a UNIMODULAR transform of rows (same
    lattice, verified by determinant-preservation during development).
    ok=False only if gcd(coeffs) is not +-1 (the found vector is a proper
    multiple of a primitive one) -- reported and skipped, never forced."""
    m = len(rows)
    coeffs = [int(c) for c in coeffs]
    rows = [r.copy() for r in rows]
    active = [i for i in range(m) if coeffs[i] != 0]
    if not active:
        return None, False
    while len(active) > 1:
        i, j = active[0], active[1]
        a, b = coeffs[i], coeffs[j]
        g, s, t = ext_gcd(a, b)
        ai, bj = a // g, b // g
        row_i_new = ai * rows[i] + bj * rows[j]
        row_j_new = (-t) * rows[i] + s * rows[j]
        rows[i], rows[j] = row_i_new, row_j_new
        coeffs[i], coeffs[j] = g, 0
        active = [k for k in range(m) if coeffs[k] != 0]
    lead = active[0]
    g_final = coeffs[lead]
    if abs(g_final) != 1:
        return None, False
    if g_final == -1:
        rows[lead] = -rows[lead]
    if lead != 0:
        rows[0], rows[lead] = rows[lead], rows[0]
    return rows, True


# --------------------------------------------------------------- fixed-pivot completion
class SizeReduceBreakdown(Exception):
    """Raised (never crashes the run) when a size-reduction coefficient
    explodes or fails to converge -- a numerical breakdown of THIS
    insertion attempt, caught upstream and skipped, per PREREG-4 2.4's
    'never as a comparison value' rule for anything that cannot be
    computed cleanly."""
    pass


def size_reduce_fixed_pivot(B, bs, max_coeff=2 ** 40, max_passes=80):
    """Size-reduce local rows [1, bs) against row 0 and each other, WITHOUT
    ever swapping row 0 out of position -- unlike calling ordinary LLL on
    the post-insertion block (verified during development to sometimes
    swap the just-enumerated shortest vector back out via its own delta
    condition, silently discarding the improvement). This guarantees the
    block's row 0 stays EXACTLY the vector enum_shortest found. A genuinely
    different completion step from hkz_profile's BKZReduction pass."""
    B = B.copy()
    for k in range(1, bs):
        for _pass in range(max_passes):
            mu_full, _, _ = gso_full(B[:k + 1])
            mu_k = mu_full[k]
            moved = False
            for j in range(k - 1, -1, -1):
                if not np.isfinite(mu_k[j]):
                    raise SizeReduceBreakdown(
                        "non-finite mu[%d,%d]=%r" % (k, j, mu_k[j]))
                qv = round(mu_k[j])
                if abs(qv) > max_coeff:
                    raise SizeReduceBreakdown(
                        "reduction coefficient exploded: q=%r at k=%d j=%d" % (qv, k, j))
                if qv != 0:
                    B[k] = B[k] - int(qv) * B[j]
                    moved = True
                    break
            if not moved:
                break
        else:
            raise SizeReduceBreakdown(
                "size reduction did not converge in %d passes at k=%d" % (max_passes, k))
    return B


# --------------------------------------------------------------- full pipeline
def route_i2_reduce(B0, lattice_label, time_cap, node_cap=ENUM_NODE_CAP,
                     max_outer_sweeps=MAX_OUTER_SWEEPS):
    """ROUTE-I2's own reduction pipeline: LLL(delta=0.999) once, then a
    RIGHT-TO-LEFT-within-each-block-size, INCREASING-block-size progressive
    sweep (a genuinely different order and growth strategy from
    hkz_profile's single BKZ pass at block_size=d followed by
    left-to-right per-index repair sweeps), using this script's own
    enum_shortest + insert_combination + size_reduce_fixed_pivot, never
    fpylll. Every accepted insertion is verified against the exact logdet
    invariant (an integer-lattice unimodular transform can NEVER change
    log|det B|); a violation beyond float64 tolerance is treated as a
    numerical breakdown of that specific attempt and rejected, never
    silently accepted -- this is a self-check this script adds that
    hkz_profile's own pipeline does not have."""
    d = B0.shape[0]
    t0 = time.time()
    B, lll_steps = lll_reduce_inplace(B0)
    diag = OrderedDict()
    diag["lll_steps"] = lll_steps
    diag["lll_delta"] = LLL_DELTA
    diag["lll_secs"] = time.time() - t0
    diag["insertions"] = 0
    diag["enum_calls"] = 0
    diag["node_cap_hits"] = 0
    diag["outer_sweeps_done"] = 0
    diag["time_cap_hit"] = False
    diag["gcd_skips"] = 0
    diag["reverted_no_help"] = 0
    diag["size_reduce_breakdowns"] = 0
    diag["logdet_invariant_breaks"] = 0
    diag["converged"] = False

    max_bs = min(d, BLOCK_SCHEDULE_CAP.get(lattice_label, d))
    block_sizes = list(range(2, max_bs + 1))
    diag["block_schedule_max"] = max_bs
    diag["block_schedule_capped_below_d"] = bool(max_bs < d)

    mu, r, Bstar = gso_full(B)
    logdet_ref = 0.5 * float(np.sum(np.log(r)))
    diag["logdet_after_lll"] = logdet_ref

    for sweep in range(max_outer_sweeps):
        if time.time() - t0 > time_cap:
            diag["time_cap_hit"] = True
            break
        diag["outer_sweeps_done"] += 1
        any_insert = False
        for bs in block_sizes:
            if time.time() - t0 > time_cap:
                diag["time_cap_hit"] = True
                break
            for start in range(d - bs, -1, -1):
                if time.time() - t0 > time_cap:
                    diag["time_cap_hit"] = True
                    break
                diag["enum_calls"] += 1
                coeffs, norm2, nodes, cap_hit = enum_shortest(
                    mu, r, start, bs, r[start] * (1 - 1e-9), node_cap=node_cap)
                if cap_hit:
                    diag["node_cap_hits"] += 1
                if coeffs is None or norm2 >= r[start] * (1 - 1e-9):
                    continue
                rows = [B[start + t] for t in range(bs)]
                new_rows, ok = insert_combination(list(coeffs), rows)
                if not ok:
                    diag["gcd_skips"] += 1
                    continue
                B_trial = B.copy()
                for t in range(bs):
                    B_trial[start + t] = new_rows[t]
                try:
                    B_trial_local = size_reduce_fixed_pivot(
                        B_trial[start:start + bs], bs)
                except SizeReduceBreakdown:
                    diag["size_reduce_breakdowns"] += 1
                    continue
                B_trial[start:start + bs] = B_trial_local
                mu2, r2, Bstar2 = gso_continue(B_trial, mu, r, Bstar, start)
                if r2[start] >= r[start] * (1 - 1e-9):
                    diag["reverted_no_help"] += 1
                    continue
                ld2 = 0.5 * float(np.sum(np.log(r2)))
                if abs(ld2 - logdet_ref) > 1e-6 * max(1.0, abs(logdet_ref)):
                    diag["logdet_invariant_breaks"] += 1
                    continue
                B, mu, r, Bstar = B_trial, mu2, r2, Bstar2
                diag["insertions"] += 1
                any_insert = True
            if diag["time_cap_hit"]:
                break
        if diag["time_cap_hit"]:
            # A sweep aborted by the wall-clock cap is a TRUNCATED search, not
            # a fixed point: no insertion in a partial sweep says nothing about
            # convergence, so leave converged False.
            break
        if not any_insert:
            diag["converged"] = True
            break

    mu, r, _ = gso_full(B)
    diag["logdet_final"] = 0.5 * float(np.sum(np.log(r)))
    diag["logdet_drift_from_lll"] = diag["logdet_final"] - logdet_ref
    diag["total_secs"] = time.time() - t0
    return B, r, diag


def diagnostic_violation(B, lattice_label, time_cap, node_cap=ENUM_NODE_CAP):
    """Independent post-hoc check: for every index j, search the projected
    sublattice starting at j (bounded by DIAG_MAX_BLOCK for the tested
    lattice) for a vector shorter than the CURRENT r[j]; report the relative
    violation. This is ROUTE-I2's own violation/optimality diagnostic
    (PREREG-4 2.2 requirement 4), computed by a SEPARATE enumeration call
    from the one used during reduction, differing in kind from
    hkz_profile's hkz_violation (which used fpylll's Enumeration class and a
    fixed 1.0000001 relative bound; this uses this script's own
    enum_shortest and reports both max and per-index results, plus whether
    the check itself was budget-capped in width or time -- disclosed, never
    silently narrowed)."""
    d = B.shape[0]
    mu, rr, _ = gso_full(B)
    max_block = DIAG_MAX_BLOCK.get(lattice_label)
    t0 = time.time()
    max_viol = 0.0
    per_index = []
    for j in range(d):
        if time.time() - t0 > time_cap:
            per_index.append({"index": j, "status": "SKIPPED_TIME_CAP"})
            continue
        bs = d - j if max_block is None else min(d - j, max_block)
        coeffs, norm2, nodes, cap_hit = enum_shortest(
            mu, rr, j, bs, rr[j], node_cap=node_cap)
        if coeffs is not None and norm2 < rr[j]:
            viol = (rr[j] - norm2) / rr[j]
        else:
            viol = 0.0
        max_viol = max(max_viol, viol)
        per_index.append({"index": j, "violation": viol,
                          "block_width_checked": bs,
                          "node_cap_hit": bool(cap_hit)})
    return {
        "max_violation": max_viol,
        "per_index": per_index,
        "seconds": time.time() - t0,
        "block_width_cap": max_block,
        "full_width_checked": max_block is None,
        "n_indices_time_skipped": sum(
            1 for p in per_index if p.get("status") == "SKIPPED_TIME_CAP"),
    }


# --------------------------------------------------------------- observables
def observables_from_profile(r, d, beta):
    """lam1n and hkz(beta) per PREREG-4 2.1's mathematical definitions,
    applied to ROUTE-I2's own r_j = ||b*_j||^2 profile."""
    logdet = 0.5 * float(np.sum(np.log(r)))
    lam1n = math.exp(0.5 * math.log(r[0]) - logdet / d)
    tail = [0.5 * math.log(r[j]) for j in range(d - beta, d)]
    hkz = float(np.mean(tail)) - logdet / d
    return lam1n, hkz, logdet


# =======================================================================
# main
# =======================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    RES = OrderedDict()
    RES["task_id"] = "TASK-20260813-415c21"
    RES["batch_id"] = "BATCH-7033ee"
    RES["goal_id"] = "GOAL-MLKEM-005"
    RES["role"] = "executor"
    RES["claim_tier"] = "toy"
    RES["certificate"] = {
        "kind": "none",
        "reason": ("no discrete-log solve and no factor-base relation is claimed "
                   "or produced; the logdet-invariance self-check and the "
                   "per-index enumeration diagnostic are INSTRUMENT CHECKS on "
                   "this script's own reduction, never certificates.")}
    RES["governed_by"] = {"prereg": PREREG_REL, "sha256": PREREG_SHA256_EXPECTED,
                          "notarizing_commit": NOTARIZING_COMMIT}

    print("=" * 78)
    print("TASK-20260813-415c21 -- ROUTE-I2 (lead producer)")
    print("BATCH-7033ee / GOAL-MLKEM-005 -- CLAIM TIER: TOY")
    print("=" * 78)

    print("\n[gate] prereg notarization")
    pv = verify_prereg()
    RES["prereg_verification"] = pv
    for kk in ("repo_root_matches", "sha256_matches", "is_ancestor_of_HEAD"):
        print("    %-24s %s" % (kk, pv[kk]))
    if not (pv["repo_root_matches"] and pv["sha256_matches"]):
        raise SystemExit("ABORT: prereg gate failed: %s" % json.dumps(pv))

    RES["git"] = {
        "revision": git("rev-parse", "HEAD"),
        "dirty": bool(git("status", "--porcelain")),
        "dirty_paths": [l for l in git("status", "--porcelain").splitlines()],
        "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
    }
    fpylll_present = False
    try:
        import fpylll  # noqa: F401
        fpylll_present = True
    except Exception:
        fpylll_present = False
    RES["environment"] = {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "host": socket.gethostname(),
        "python_version": platform.python_version(),
        "dependencies": {"numpy": np.__version__},
        "fpylll_present_but_NOT_imported_by_this_script": fpylll_present,
        "sage_present": False, "flint_present": False,
        "declared_gap_G5": ("this environment has no fpylll, sage or flint "
                            "installed at dispatch time (per the handoff); "
                            "this script uses a from-scratch reduction "
                            "pipeline and imports none of them"),
    }

    # -------------------------------------------------------------
    # R-B-OUT-0: RC-3, carried verbatim, no recomputation
    # -------------------------------------------------------------
    print("\n[0] R-B-OUT-0 -- RC-3 carried verbatim from PREREG-4 section 1")
    RES["R-B-OUT-0_RC3_carry"] = {
        "attribution": "PREREG-4 section 1, carried verbatim by this document",
        "recomputed": False,
        "note": ("This text is quoted, not recomputed. It supersedes "
                 "BATCH-fbb639's R-C-OUT-0 coverage table at exactly the "
                 "four named hkz cells; it does not change any D_route "
                 "value and does not change the fired termination branch."),
        "frozen_text_verbatim": RC3_FROZEN_TEXT_VERBATIM,
    }
    print("    carried, %d chars, recomputed=False" % len(RC3_FROZEN_TEXT_VERBATIM))

    # -------------------------------------------------------------
    # Obligation 0 (R-B-OUT-1): verify ROUTE-P coverage BEFORE building
    # ROUTE-I2, per PREREG-4 2.3.
    # -------------------------------------------------------------
    print("\n[1] Obligation 0 -- verify ROUTE-P coverage (results_relvar.json)")
    obl0 = OrderedDict()
    obl0["source_path"] = RESULTS_RELVAR_REL
    obl0["source_sha256"] = None
    obl0["source_readable"] = os.path.isfile(RESULTS_RELVAR_PATH)
    route_p = {}         # (cand, lat, beta) -> {"per_basis": [...], "s_c_fib": x}
    gaps = []
    if not obl0["source_readable"]:
        obl0["FATAL"] = "results_relvar.json is missing or unreadable"
        print("    FATAL: %s not readable" % RESULTS_RELVAR_PATH)
    else:
        obl0["source_sha256"] = sha256_file(RESULTS_RELVAR_PATH)
        with open(RESULTS_RELVAR_PATH) as fh:
            relvar = json.load(fh)
        # PREREG-4 2.1 states the per-basis ROUTE-P path as
        # rel2[cand][pair][beta]['per_basis'][i]['X_a'] under G_REL2, and
        # separately (2.1's s_c^fib line) as
        # "results_relvar.json.per_candidate.<X>.per_cell.<L>_<b>.float_sd".
        # THAT SECOND PATH IS NOT LITERALLY PRESENT: the actual key is
        # G_VAR.per_candidate.<X>.per_cell.<L>_<b>.float_sd (verified below
        # by reading the real file, exactly as PREREG-4 2.3 requires this
        # lead to do rather than trust the prose paragraph).
        rel2_path_used = "G_REL2.<cand>.<pair>.<beta>.per_basis[i].X_a"
        svar_path_stated_in_prereg = ("results_relvar.json.per_candidate."
                                      "<X>.per_cell.<L>_<b>.float_sd")
        svar_path_actually_found = ("G_VAR.per_candidate.<X>.per_cell."
                                    "<L>_<b>.float_sd")
        obl0["G_REL2_json_path_used"] = rel2_path_used
        obl0["s_c_fib_json_path_stated_in_PREREG_4_2_1"] = svar_path_stated_in_prereg
        obl0["s_c_fib_json_path_actually_present_and_used"] = svar_path_actually_found
        obl0["s_c_fib_path_discrepancy_note"] = (
            "PREREG-4 2.1 states the s_c^fib path without a 'G_VAR.' prefix; "
            "the actual committed results_relvar.json has no top-level "
            "'per_candidate' key at all -- the real key is nested under "
            "G_VAR.per_candidate.<X>.per_cell.<L>_<b>.float_sd, verified by "
            "direct read of the file below, per 2.3's instruction to verify "
            "rather than trust the paragraph. This is a path-label "
            "discrepancy in the pre-registration's prose, not a data gap: "
            "the values themselves are present and are used below.")

        for cand in CANDIDATES:
            for lat, (d, k) in LATTICES.items():
                pair = MIRROR_PAIR[lat]
                for beta in BETA_GRID[lat]:
                    cell = "%s/%s_b%d" % (cand, lat, beta)
                    try:
                        pb = relvar["G_REL2"][cand][pair][str(beta)]["per_basis"]
                    except (KeyError, TypeError):
                        gaps.append({"cell": cell, "reason": "G_REL2 path missing"})
                        continue
                    xa = [row.get("X_a") if isinstance(row, dict) else None
                          for row in pb]
                    n_present = sum(1 for x in xa if x is not None)
                    if len(pb) < N_BASES or n_present < N_BASES:
                        gaps.append({"cell": cell,
                                    "reason": "per_basis has %d entries, %d "
                                              "non-null X_a (need %d)"
                                              % (len(pb), n_present, N_BASES)})
                        continue
                    try:
                        sfib = (relvar["G_VAR"]["per_candidate"][cand]
                                ["per_cell"]["%s_b%d" % (lat, beta)]["float_sd"])
                    except (KeyError, TypeError):
                        gaps.append({"cell": cell,
                                    "reason": "G_VAR.per_candidate float_sd missing"})
                        continue
                    route_p[(cand, lat, beta)] = {
                        "per_basis_X_a": xa, "s_c_fib": sfib}
        obl0["cells_expected"] = 18
        obl0["cells_confirmed_full_8basis_coverage"] = len(route_p)
        obl0["gaps"] = gaps
        obl0["ALL_18_CELLS_COVERED"] = bool(len(route_p) == 18 and not gaps)
        print("    cells expected: 18, confirmed full 8-basis coverage: %d"
              % len(route_p))
        print("    gaps found: %d" % len(gaps))
        for g in gaps:
            print("      GAP: %s -- %s" % (g["cell"], g["reason"]))
    RES["R-B-OUT-1_obligation0_route_p_verification"] = obl0

    # -------------------------------------------------------------
    # Build ROUTE-I2 and compute Obligation 1 (R-B-OUT-2)
    # -------------------------------------------------------------
    print("\n[2] Building ROUTE-I2 and computing per-cell comparison "
          "(Obligation 1)")
    per_lattice_reduction = OrderedDict()
    profiles = {}   # (lat, i) -> r array (or None)
    reduction_diag = OrderedDict()
    uncovered_bases = OrderedDict()   # (lat,i) -> reason

    for lat, (d, k) in LATTICES.items():
        reduction_diag[lat] = []
        for i in range(N_BASES):
            if budget_remaining() < GLOBAL_SAFETY_MARGIN_SECONDS:
                reason = ("GLOBAL_BUDGET_EXHAUSTED: %.1fs remaining of %.0fs "
                          "hard cap before the %.0fs safety margin"
                          % (budget_remaining(), GLOBAL_BUDGET_SECONDS,
                             GLOBAL_SAFETY_MARGIN_SECONDS))
                uncovered_bases[(lat, i)] = reason
                profiles[(lat, i)] = None
                reduction_diag[lat].append({"basis": i, "status": "SKIPPED", "reason": reason})
                print("    %-4s i=%d SKIPPED -- %s" % (lat, i, reason))
                continue
            B0 = route_i2_basis(d, k, Q_MAIN, i)
            t0b = time.time()
            try:
                Bred, r, diag = route_i2_reduce(
                    B0, lat, time_cap=REDUCE_TIME_CAP[lat])
            except Exception as ex:
                reason = "EXCEPTION during reduction: %s: %s" % (type(ex).__name__, ex)
                uncovered_bases[(lat, i)] = reason
                profiles[(lat, i)] = None
                reduction_diag[lat].append({"basis": i, "status": "EXCEPTION",
                                            "reason": reason})
                print("    %-4s i=%d EXCEPTION -- %s" % (lat, i, reason))
                continue
            vdiag = diagnostic_violation(Bred, lat, time_cap=DIAG_TIME_CAP[lat])
            # PREREG-4 2.4: a basis whose reduction or whose own violation
            # diagnostic was cut short by a time cap cannot be reported as a
            # comparison value -- it is UNCOVERED2 with the reason.
            capped = []
            if diag["time_cap_hit"]:
                capped.append("reduction hit the %.0fs per-basis time cap "
                              "(converged=%s, sweeps=%d)"
                              % (REDUCE_TIME_CAP[lat], diag["converged"],
                                 diag["outer_sweeps_done"]))
            if vdiag["n_indices_time_skipped"]:
                capped.append("violation diagnostic hit the %.0fs time cap "
                              "(%d of %d indices unchecked)"
                              % (DIAG_TIME_CAP[lat],
                                 vdiag["n_indices_time_skipped"], d))
            if capped:
                reason = "TIME_CAP: " + "; ".join(capped)
                uncovered_bases[(lat, i)] = reason
                profiles[(lat, i)] = None
                reduction_diag[lat].append(
                    {"basis": i, "status": "TIME_CAPPED", "reason": reason,
                     "reduce_diag": diag,
                     "violation_diag": {k2: v2 for k2, v2 in vdiag.items()
                                        if k2 != "per_index"},
                     "violation_per_index": vdiag["per_index"]})
                print("    %-4s i=%d TIME_CAPPED -- %s" % (lat, i, reason))
                continue
            profiles[(lat, i)] = r
            entry = {"basis": i, "status": "OK", "reduce_diag": diag,
                     "violation_diag": {k2: v2 for k2, v2 in vdiag.items()
                                       if k2 != "per_index"},
                     "violation_per_index": vdiag["per_index"]}
            reduction_diag[lat].append(entry)
            print("    %-4s i=%d  %.2fs reduce (sweeps=%d conv=%s) "
                  "+ %.2fs diag  max_violation=%.4g  logdet_drift=%.2e"
                  % (lat, i, diag["total_secs"], diag["outer_sweeps_done"],
                     diag["converged"], vdiag["seconds"], vdiag["max_violation"],
                     diag["logdet_drift_from_lll"]))
        per_lattice_reduction[lat] = reduction_diag[lat]

    RES["route_i2_reduction_diagnostics"] = per_lattice_reduction
    RES["route_i2_uncovered_bases"] = {
        "%s/i%d" % k2: v2 for k2, v2 in uncovered_bases.items()}

    # per-cell computation
    per_cell = OrderedDict()
    for cand in CANDIDATES:
        for lat, (d, k) in LATTICES.items():
            for beta in BETA_GRID[lat]:
                cell_key = "%s/%s_b%d" % (cand, lat, beta)
                pkey = (cand, lat, beta)
                route_p_entry = route_p.get(pkey)
                per_basis = []
                any_missing = False
                for i in range(N_BASES):
                    r = profiles.get((lat, i))
                    if r is None:
                        any_missing = True
                        per_basis.append({"basis": i, "status": "UNCOVERED2",
                                          "reason": uncovered_bases.get((lat, i),
                                                                        "unknown")})
                        continue
                    lam1n, hkzv, logdet = observables_from_profile(r, d, beta)
                    xval = lam1n if cand == "lam1n" else hkzv
                    xp = (route_p_entry["per_basis_X_a"][i]
                          if route_p_entry is not None else None)
                    per_basis.append({"basis": i, "status": "OK",
                                      "X_route_i2": xval,
                                      "X_route_p": xp,
                                      "abs_diff": (abs(xval - xp)
                                                  if xp is not None else None)})
                if route_p_entry is None:
                    per_cell[cell_key] = {
                        "status": "UNCOVERED2",
                        "reason": "ROUTE-P itself has no full 8-basis coverage "
                                  "at this cell (see obligation 0 gaps)",
                        "per_basis": per_basis}
                    continue
                if any_missing:
                    per_cell[cell_key] = {
                        "status": "UNCOVERED2",
                        "reason": "ROUTE-I2 could not compute one or more of "
                                  "the 8 fibre bases at this lattice (see "
                                  "route_i2_uncovered_bases)",
                        "per_basis": per_basis}
                    continue
                diffs = [pb["abs_diff"] for pb in per_basis]
                d_route_indep = max(diffs)
                s_c_fib = route_p_entry["s_c_fib"]
                verdict = "EXCEEDS" if s_c_fib > d_route_indep else "DOES NOT EXCEED"
                per_cell[cell_key] = {
                    "status": "COVERED2",
                    "D_route_independent": d_route_indep,
                    "s_c_fib": s_c_fib,
                    "verdict": verdict,
                    "per_basis": per_basis,
                }
    RES["R-B-OUT-2_obligation1_per_cell"] = per_cell
    n_covered2 = sum(1 for v in per_cell.values() if v["status"] == "COVERED2")
    print("    COVERED2: %d / 18" % n_covered2)

    # -------------------------------------------------------------
    # Obligation 2 (R-B-OUT-3): aggregate + comparison to PREREG-3's D_route
    # -------------------------------------------------------------
    print("\n[3] Obligation 2 -- aggregate + comparison to PREREG-3's D_route")
    prereg3_d_route = {}
    prereg3_note = None
    if os.path.isfile(RESULTS_C3LANE_PATH):
        with open(RESULTS_C3LANE_PATH) as fh:
            c3 = json.load(fh)
        pc1 = c3.get("R-C-OUT-1_per_cell_comparison", {})
        for k2, v2 in pc1.items():
            prereg3_d_route[k2] = v2.get("D_route")
    else:
        prereg3_note = "results_c3lane.json not found -- comparison to PREREG-3 unavailable"

    RC3_UNCOVERED_FOR_PREREG3 = {"hkz/L9_b15", "hkz/L11_b20"}

    covered2_cells = [k2 for k2, v2 in per_cell.items() if v2["status"] == "COVERED2"]
    uncovered2_cells = [k2 for k2, v2 in per_cell.items() if v2["status"] != "COVERED2"]
    comparison_table = OrderedDict()
    for cell_key in per_cell:
        entry = per_cell[cell_key]
        row = {"D_route_independent": entry.get("D_route_independent"),
               "status": entry["status"]}
        if cell_key in RC3_UNCOVERED_FOR_PREREG3:
            row["prereg3_D_route"] = None
            row["prereg3_note"] = ("UNCOVERED under RC-3 (PREREG-4 section 1) "
                                   "-- no genuine PREREG-3 D_route exists at "
                                   "this cell to compare against")
        else:
            row["prereg3_D_route"] = prereg3_d_route.get(cell_key)
        if row["D_route_independent"] is not None and row["prereg3_D_route"] is not None:
            row["same_order_near_machine_epsilon"] = bool(
                row["D_route_independent"] < 1e-8)
        comparison_table[cell_key] = row

    covered_d_route_indep = [per_cell[k2]["D_route_independent"] for k2 in covered2_cells]
    covered_s_c_fib = [per_cell[k2]["s_c_fib"] for k2 in covered2_cells]
    n_exceeds = sum(1 for k2 in covered2_cells if per_cell[k2]["verdict"] == "EXCEEDS")
    n_does_not_exceed = len(covered2_cells) - n_exceeds

    smallest_s_c_fib_overall = None
    try:
        with open(RESULTS_RELVAR_PATH) as fh:
            relvar_for_min = json.load(fh)
        vals = []
        for cand in ("lam1n", "hkz"):
            for cellname, cellval in (relvar_for_min["G_VAR"]["per_candidate"]
                                      [cand]["per_cell"].items()):
                if cellname.split("_")[0] in LATTICES:
                    vals.append(cellval["float_sd"])
        if vals:
            smallest_s_c_fib_overall = min(vals)
    except Exception:
        smallest_s_c_fib_overall = None

    obl2 = OrderedDict()
    obl2["COVERED2"] = covered2_cells
    obl2["UNCOVERED2"] = [{"cell": k2, "reason": per_cell[k2].get("reason")}
                          for k2 in uncovered2_cells]
    obl2["n_covered2"] = len(covered2_cells)
    obl2["n_uncovered2"] = len(uncovered2_cells)
    obl2["n_EXCEEDS"] = n_exceeds
    obl2["n_DOES_NOT_EXCEED"] = n_does_not_exceed
    obl2["comparison_to_prereg3_D_route"] = comparison_table
    obl2["prereg3_note"] = prereg3_note
    obl2["summary_statistics"] = {
        "D_route_independent_max": (max(covered_d_route_indep)
                                    if covered_d_route_indep else None),
        "D_route_independent_median": (float(np.median(covered_d_route_indep))
                                       if covered_d_route_indep else None),
        "s_c_fib_max_over_covered_cells": (max(covered_s_c_fib)
                                           if covered_s_c_fib else None),
        "s_c_fib_median_over_covered_cells": (float(np.median(covered_s_c_fib))
                                              if covered_s_c_fib else None),
        "smallest_s_c_fib_anywhere_in_scope": smallest_s_c_fib_overall,
    }
    RES["R-B-OUT-3_obligation2_aggregate"] = obl2
    print("    COVERED2 %d/18  EXCEEDS %d  DOES-NOT-EXCEED %d  UNCOVERED2 %d"
          % (len(covered2_cells), n_exceeds, n_does_not_exceed, len(uncovered2_cells)))

    # -------------------------------------------------------------
    # Termination branch, PREREG-4 2.6, precedence exactly as frozen
    # -------------------------------------------------------------
    print("\n[4] Termination branch (PREREG-4 2.6)")
    threshold_eps = 1e-8
    threshold_frac = 0.10
    undermines_cells = []
    confirmation_regime = None
    for k2 in covered2_cells:
        entry = per_cell[k2]
        d_ri = entry["D_route_independent"]
        s_fib = entry["s_c_fib"]
        cond_scale = bool(d_ri >= threshold_frac * s_fib)
        prereg3_verdict_here = ("EXCEEDS" if k2 not in RC3_UNCOVERED_FOR_PREREG3
                                and prereg3_d_route.get(k2) is not None
                                and s_fib > prereg3_d_route.get(k2) else None)
        this_verdict = entry["verdict"]
        cond_flip = bool(prereg3_verdict_here == "EXCEEDS" and this_verdict == "DOES NOT EXCEED")
        if cond_scale or cond_flip:
            undermines_cells.append({
                "cell": k2, "D_route_independent": d_ri, "s_c_fib": s_fib,
                "fired_condition": ("scale (D_route_independent >= 10%% of "
                                    "s_c^fib)" if cond_scale else
                                    "verdict_flip (EXCEEDS -> DOES NOT EXCEED)"),
            })

    if len(covered2_cells) == 0:
        branch = "T-INDEP-NODATA"
        branch_quote = ("PREREG-4 2.6: 'FIRES WHEN COVERED2 is empty ... MEANS: "
                        "a genuinely independent second route could not be "
                        "built or run this batch, for infrastructure reasons "
                        "... FORBIDS: any claim that the EXCEEDS verdicts are "
                        "or are not artifacts; closing, pausing or completing "
                        "GOAL-MLKEM-005.'")
    elif undermines_cells:
        suffix = "-PARTIAL" if len(covered2_cells) < 18 else ""
        branch = "T-INDEP-UNDERMINES" + suffix
        branch_quote = ("PREREG-4 2.6: 'a single cell firing UNDERMINES's "
                        "condition is sufficient to fire T-INDEP-UNDERMINES "
                        "and prevents T-INDEP-CONFIRMS from being read over "
                        "the whole COVERED2 set.'")
    else:
        # PREREG-4 2.6: T-INDEP-CONFIRMS is the EXACT COMPLEMENT of
        # T-INDEP-UNDERMINES -- no outcome falls between the two. The only
        # thing the below-epsilon/above-epsilon split decides is which
        # confirmation regime is reported.
        all_near_eps = all(per_cell[k2]["D_route_independent"] <= threshold_eps
                           for k2 in covered2_cells)
        suffix = "-PARTIAL" if len(covered2_cells) < 18 else ""
        branch = "T-INDEP-CONFIRMS" + suffix
        confirmation_regime = ("at or near machine epsilon" if all_near_eps
                               else "below the dispersion threshold but above "
                                    "machine epsilon")
        branch_quote = ("PREREG-4 2.6: 'FIRES WHEN COVERED2 is non-empty and "
                        "T-INDEP-UNDERMINES's condition fires at no covered "
                        "cell -- i.e., stated operationally and as the exact "
                        "complement of that branch so that no outcome falls "
                        "between the two ... and must state which regime the "
                        "confirmation is in: at or near machine epsilon ... or "
                        "below the dispersion threshold but above machine "
                        "epsilon ... the second is a genuine and expected "
                        "outcome for a from-scratch reduction at d <= 40, it "
                        "fires this same branch, and it is reported as the "
                        "weaker of the two readings.' Regime here: %s."
                        % confirmation_regime)

    RES["R-B-OUT-4_termination_branch"] = {
        "branch": branch,
        "quoted_clause": branch_quote,
        "confirmation_regime": confirmation_regime,
        "n_covered2": len(covered2_cells),
        "n_total_cells": 18,
        "threshold_eps_used": threshold_eps,
        "threshold_frac_used": threshold_frac,
        "smallest_s_c_fib_anywhere_in_scope": smallest_s_c_fib_overall,
    }
    RES["R-B-OUT-5_revisit_list"] = undermines_cells
    print("    branch: %s" % branch)
    print("    R-B-OUT-5 revisit list: %d cell(s)" % len(undermines_cells))

    RES["timings"] = {
        "total_seconds": elapsed(),
        "global_budget_seconds": GLOBAL_BUDGET_SECONDS,
        "budget_note": "the wall-clock budget is a STOP, never a target",
    }
    RES["resources"] = {
        "max_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (
            1024 if platform.system() == "Linux" else 1),
        "max_rss_units": "bytes (ru_maxrss is KiB on Linux, scaled here)",
    }
    RES["validity"] = {
        "status": "VALID",
        "note": ("A cap that binds (per-basis reduce/diagnostic time caps, or "
                 "the global budget guard) is INFRASTRUCTURE SIGNAL, reported "
                 "in route_i2_uncovered_bases / R-B-OUT-2's UNCOVERED2 status, "
                 "never a route disagreement, never a dispersion finding."),
    }
    RES["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    with open(args.out, "w") as fh:
        json.dump(RES, fh, indent=1, default=float)
    print("\n[5] wrote %s" % args.out)
    print("    total %.2f s" % elapsed())
    return 0


if __name__ == "__main__":
    sys.exit(main())
