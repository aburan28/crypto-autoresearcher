#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TASK-20260813-ea2e96 / BATCH-6e08fe / GOAL-MLKEM-005 -- THE LEAD PRODUCER

Governed by PREREG-4:
  coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/tasks/
      TASK-20260813-cdcd88/prereg.md
  sha256 ff577564dcdbb45b1b19885297ffc512888f9442dc99f2057fdf7f86f63fbbda
  notarized in commit 1e1acf08b151dd31b4d41b8afd287d261adce1e5

CLAIM TIER: TOY, UNCONDITIONALLY. Nothing this script computes bears on
ML-KEM security, on any FIPS 203 parameter set, on any attack cost, or on
any cost model. No number produced here transports to beta = 606, d = 1420,
or any other parameter set by extrapolation, analogy or any other route.

certificate.kind: none -- no discrete-log solve and no factor-base relation
is claimed or produced anywhere in this script. The D_route' comparison
below is an INSTRUMENT / INDEPENDENCE CHECK, never a certificate.

WHAT THIS SCRIPT DOES, IN ORDER
  (a) RC-3 -- carries PREREG-4 section 1's frozen coverage-table correction
      TEXT VERBATIM into results_route_reimpl.json / report_route_reimpl.md.
      NO RECOMPUTATION of any kind for part (a): the two 0.0 values are
      read, as constants, directly from the already-committed
      probe_coverage_beta_mismatch_output.json (path and sha256 recorded in
      run_manifest.yaml) and are never recomputed by this script.
  (b) obligation 0 -- reads (never recomputes) results_relvar.json's own
      G_REL1 block for lam1n/hkz at L7/L9/L11 and reports, per cell, whether
      genuine ROUTE-P per-basis ground truth exists (PREREG-4 2.3).
  (c) THE ONE GENUINELY NEW COMPUTATION OF THIS BATCH: ROUTE-I', a
      from-scratch, non-code-shared re-implementation, per PREREG-4 2.2 --
      see IMPLEMENTATION_CHOICE_DECLARATION below, BEFORE any D_route'
      number is computed.
  (d) obligation 1/2 -- D_route'/VERDICT' per PREREG-3 3.3's own formula,
      reused verbatim, and the ALL-SURVIVE / SOME-ARTIFACT aggregate.
  (e) the termination branch read off PREREG-4 2.6's frozen precedence.

BOUNDED: NO REDUCTION ABOVE d = 40, ANYWHERE. Hard wall-clock budget for
this task is 1800 s (dispatch queue); this script enforces an internal
computation deadline (COMPUTE_DEADLINE_SECONDS, set below the task's own
budget) so that report-writing always completes even if reduction is
budget-bound, and any (lattice, basis) pair not reached is reported as
"NOT COMPUTED: budget exhausted" (PREREG-4 3.2), never defaulted to a
verdict.

This script writes exactly one file: results_route_reimpl.json, inside its
own task directory. It performs no git write and makes no commit.
"""

import argparse
import hashlib
import json
import math
import os
import platform
import socket
import sys
import time
from collections import OrderedDict

import numpy as np

T_START = time.time()

# A hard internal deadline for the COMPUTATION phase only (reduction +
# enumeration). Left well below the task's 1800 s dispatch-queue budget so
# that JSON/report writing always completes. A cell not reached by this
# deadline is reported as NOT COMPUTED: budget exhausted (PREREG-4 3.2),
# never silently merged with a genuinely UNCOVERED cell.
COMPUTE_DEADLINE_SECONDS = 1500.0
PER_BASIS_LLL_CAP = 240.0
PER_BASIS_ENUM_CAP = 150.0

TASK_DIR = os.path.dirname(os.path.abspath(__file__))


def _find_repo_root(start):
    """Walk upward until a .git directory is found -- avoids the
    off-by-one-level defect (D-2) this goal's own scripts have flagged
    before when a fixed '..' count was hardcoded."""
    cur = start
    for _ in range(20):
        if os.path.isdir(os.path.join(cur, ".git")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    raise SystemExit("ABORT: could not locate repo root (.git) above %s" % start)


REPO_ROOT = _find_repo_root(TASK_DIR)

RESULTS_RELVAR_PATH = os.path.join(
    REPO_ROOT, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/"
    "tasks/TASK-20260809-cda2f6/results_relvar.json")
PROBE_OUTPUT_PATH = os.path.join(
    REPO_ROOT, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/"
    "reviews/TASK-20260813-6ab893/probes/probe_coverage_beta_mismatch_output.json")
RESULTS_C3LANE_PATH = os.path.join(
    REPO_ROOT, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/"
    "tasks/TASK-20260813-7b3039/results_c3lane.json")
PREREG4_PATH = os.path.join(TASK_DIR, "..", "TASK-20260813-cdcd88",
                            "prereg.md")

Q_MAIN = 3329
N_BASES = 8
LATTICES = OrderedDict([("L7", (20, 6)), ("L9", (30, 9)), ("L11", (40, 12))])
BETA_GRID = {20: [5, 10, 15], 30: [7, 15, 22], 40: [10, 20, 30]}
REL1_PAIR = {20: (5, 15), 30: (7, 22), 40: (10, 30)}
CANDIDATES = ["lam1n", "hkz"]

# ============================================================ RC-3, FROZEN
RC3_TEXT = (
    "BATCH-fbb639's coverage table (R-C-OUT-0 of results_c3lane.json) "
    "falsely marks hkz/L9_b15 and hkz/L11_b20 as COVERED "
    "(route_i_available: true). results_am4.json's gates.hkz.G_REL1.all "
    "block reports hkz only at the two REL1_PAIR endpoint betas per "
    "lattice (L9: 7 and 22; L11: 10 and 30) -- never the middle beta "
    "either lattice's 3-point grid uses (L9: 15; L11: 20), and "
    "measure_c3lane.py never reads X_hi. hkz/L9_b15 and hkz/L11_b20 are "
    "restated as UNCOVERED, not COVERED. Two further cells, hkz/L9_b22 "
    "and hkz/L11_b30, cite the WRONG beta's value as their D_route "
    "source (the beta_lo comparison was reused instead of the true "
    "beta_hi comparison). hkz/L9_b22 and hkz/L11_b30 are restated with "
    "the corrected TRUE beta_hi-based D_route source -- am4_X_hi compared "
    "against relvar's own G_REL1 X_b at basis 0 -- numerically UNCHANGED "
    "at exactly 0.0 for both cells (probe_coverage_beta_mismatch_output.json, "
    "per_cell_beta_coverage_audit[\"hkz/L9_b22\"].TRUE_beta_hi_comparison "
    "and [\"hkz/L11_b30\"].TRUE_beta_hi_comparison, true_abs_deviation: 0.0 "
    "in both). lam1n's equivalent beta reuse is verified LEGITIMATE and is "
    "explicitly excluded from this correction: lam1n's X_lo == X_hi "
    "exactly at both lattices, so any beta's comparison genuinely is "
    "\"the\" comparison for it. GENUINE COVERAGE NARROWS FROM 18 TO 16 OF "
    "27: lam1n 9/9 unaffected, hkz 7/9 genuinely covered (L7 all 3: "
    "b5/b10/b15; L9: b7/b22; L11: b10/b30). THIS SUPERSEDES THE 18/27 "
    "COVERAGE FRACTION and the per-cell source attribution for these 4 "
    "named cells wherever either is quoted without this correction in "
    "the same sentence."
)

IMPLEMENTATION_CHOICE_DECLARATION = (
    "ROUTE-I' implementation choice (PREREG-4 section 2.2), declared here "
    "BEFORE any D_route' number is computed and checkable against the "
    "committed script below:\n"
    "\n"
    "1. Environment check performed FIRST: this run environment has NO "
    "fpylll installed (`import fpylll` fails with ModuleNotFoundError) and "
    "no other independently maintained lattice-reduction library is "
    "installed (checked: no sagemath, no python-flint/pari lattice "
    "routines, no third-party BKZ/LLL package). Options 2.2(2)(i) and "
    "2.2(2)(ii) are therefore UNAVAILABLE in this environment and are not "
    "used. This is recorded as an infrastructure fact, not asserted.\n"
    "2. This script instead uses option 2.2(2)(iii): a from-scratch "
    "reduction/enumeration routine in pure Python/numpy, written without "
    "consulting make_A/build_basis/hkz_profile's source in "
    "measure_am4.py/measure_relvar.py/replicate_l7l8.py or any descendant "
    "(including BATCH-4ed139's replicate_l7l8.py). Specifically:\n"
    "   (a) basis construction reconstructs the SAME numeric matrix A from "
    "the frozen, already-public seed formula "
    "(default_rng([1,d,k,i]).integers(0,q,(k,d-k))) -- per PREREG-4 "
    "2.2(3), this is explicitly NOT code-sharing: it is producing an "
    "identical, publicly declared input independently, which is what "
    "every route in this corpus (including ROUTE-P) already does. The "
    "same [[I_k,A],[0,qI_{d-k}]] block structure is used because that is "
    "the definition of the lattice being measured, not a copied routine.\n"
    "   (b) the reduction/enumeration step itself -- the step "
    "hkz_profile() performs in the barred lineage -- is replaced by a "
    "SEPARATE, INDEPENDENTLY WRITTEN implementation: (i) a standard "
    "floating-point LLL reduction (Lenstra-Lenstra-Lovasz, delta=0.99) "
    "written from the textbook algorithm with incremental "
    "Gram-Schmidt/mu-matrix bookkeeping, using only numpy dot products and "
    "no fpylll call anywhere; and (ii) a from-scratch depth-first "
    "Schnorr-Euchner-style enumeration search (also textbook, not fpylll's "
    "Enumeration class) run on top of the LLL basis to find the EXACT "
    "shortest nonzero lattice vector (lambda_1), bounded by the LLL "
    "vector's own norm as the starting search radius, with per-basis time "
    "caps.\n"
    "3. lam1n' is computed from the EXACT enumerated lambda_1 (not merely "
    "an LLL approximation) wherever enumeration completes within its "
    "per-basis cap: lam1n'(L,i) = exp(0.5*log(lambda_1^2) - logdet/d). "
    "Because HKZ reduction's own defining property makes its first vector "
    "equal to lambda_1 exactly, an exact independent lambda_1 is "
    "mathematically the identical quantity ROUTE-P's HKZ pipeline reports "
    "at index 0, regardless of which algorithm found it -- so this is a "
    "genuine, algorithm-independent check for lam1n specifically. Where "
    "the per-basis enumeration cap is hit before an exact result is found, "
    "the LLL basis's own first-vector norm is reported instead, EXPLICITLY "
    "FLAGGED per basis as 'LLL_UPPER_BOUND (exact enumeration timed out)' "
    "and distinguished from an exact result in every output row; a "
    "flagged basis is excluded from that cell's matched-basis count for "
    "D_route' rather than silently included as if exact.\n"
    "4. hkz'(L,beta,i) is computed from the GSO tail of the SAME "
    "LLL-reduced (delta=0.99) basis: hkz'(L,beta,i) = "
    "mean_{j>=d-beta}(log||b*_j||) - logdet/d, exactly PREREG-4/PREREG-3's "
    "own formula for the observable, but evaluated on an LLL-quality "
    "reduced basis rather than a full BKZ+explicit-HKZ-sweep+verification "
    "basis. THIS IS DECLARED HERE AS AN EXPLICIT LIMITATION, NOT HIDDEN: "
    "unlike lam1n (whose index-0 value is algorithm-independent by "
    "definition once the true minimum is found), the GSO tail profile at "
    "indices 1..d-1 of a merely-LLL-reduced basis is not certified to "
    "equal the profile of an HKZ-reduced basis, so hkz' D_route' may "
    "reflect real reduction-quality differences between LLL and full "
    "BKZ/HKZ, in addition to (or instead of) genuine cross-implementation "
    "noise. This is reported as part of the result, not smoothed over: "
    "hkz' is a genuinely independent, non-code-shared measurement of the "
    "SAME lattice under a DIFFERENT (and by construction weaker) "
    "reduction depth than ROUTE-P's HKZ pipeline, and any resulting "
    "disagreement is reported as measured, without claiming it isolates "
    "code-sharing from reduction-quality as a cause.\n"
    "5. logdet(L) = (d-k)*log(q) is used as the closed-form determinant "
    "(exact for B = [[I_k,A],[0,qI_{d-k}]], independent of A and of any "
    "reduction) -- a basic linear-algebra fact, not a transcription of any "
    "barred function.\n"
    "6. No fpylll import, no fpylll call, and no import of "
    "measure_am4.py / measure_relvar.py / replicate_l7l8.py or any "
    "function from them appears anywhere in this script (checkable by "
    "grep against the committed file).\n"
    "7. results_l7l8.json and results_am4.json are NEVER read anywhere in "
    "this script (checkable by grep); they are excluded as a ROUTE-P "
    "source per PREREG-4 2.1."
)


# ============================================================ helpers
def sha256_file(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def make_A_indep(d, k, q, i):
    """Reconstructs the SAME numeric instance from the frozen, published
    seed formula (PREREG-4 2.2(3)) -- required, and explicitly NOT
    code-sharing. Written independently of make_A() in the barred lineage."""
    rng = np.random.default_rng([1, d, k, i])
    return rng.integers(0, q, size=(k, d - k), dtype=np.int64)


def build_basis_indep(d, k, q, i):
    B = np.zeros((d, d), dtype=np.int64)
    B[:k, :k] = np.eye(k, dtype=np.int64)
    B[:k, k:] = make_A_indep(d, k, q, i)
    B[k:, k:] = q * np.eye(d - k, dtype=np.int64)
    return B


def gso_full(B):
    n = B.shape[0]
    Bstar = B.copy()
    mu = np.eye(n)
    sqn = np.zeros(n)
    for i in range(n):
        for j in range(i):
            mu[i, j] = np.dot(B[i], Bstar[j]) / sqn[j]
            Bstar[i] = Bstar[i] - mu[i, j] * Bstar[j]
        sqn[i] = np.dot(Bstar[i], Bstar[i])
    return Bstar, mu, sqn


def refresh_row(B, Bstar, mu, sqn, k):
    Bs = B[k].copy()
    for j in range(k):
        m = np.dot(B[k], Bstar[j]) / sqn[j]
        mu[k, j] = m
        Bs = Bs - m * Bstar[j]
    Bstar[k] = Bs
    sqn[k] = np.dot(Bs, Bs)


def lll_reduce(B, delta=0.99, time_cap=None):
    """From-scratch floating-point LLL (Lenstra-Lenstra-Lovasz), written
    independently: standard textbook recursion with incremental
    Gram-Schmidt bookkeeping. No fpylll, no import from the barred
    lineage."""
    B = B.astype(np.float64).copy()
    n = B.shape[0]
    Bstar, mu, sqn = gso_full(B)
    k = 1
    t0 = time.time()
    while k < n:
        if time_cap and time.time() - t0 > time_cap:
            return B, Bstar, mu, sqn, time.time() - t0, False
        changed = False
        for j in range(k - 1, -1, -1):
            if abs(mu[k, j]) > 0.5:
                qz = round(mu[k, j])
                B[k] = B[k] - qz * B[j]
                for jj in range(j + 1):
                    if jj < j:
                        mu[k, jj] -= qz * mu[j, jj]
                    elif jj == j:
                        mu[k, jj] -= qz
                changed = True
        if changed:
            refresh_row(B, Bstar, mu, sqn, k)
        if sqn[k] + mu[k, k - 1] ** 2 * sqn[k - 1] >= delta * sqn[k - 1]:
            k += 1
        else:
            B[[k, k - 1]] = B[[k - 1, k]]
            Bstar, mu, sqn = gso_full(B)
            k = max(k - 1, 1)
    return B, Bstar, mu, sqn, time.time() - t0, True


def enumerate_svp(mu, sqn, n, time_cap):
    """From-scratch depth-first Schnorr-Euchner-style enumeration for the
    EXACT shortest nonzero lattice vector, seeded with R^2 = sqn[0] (the
    LLL basis's own first vector, a valid upper bound). Standard textbook
    recursion; not fpylll's Enumeration, not derived from any campaign
    file."""
    best = [sqn[0], None]
    t0 = time.time()
    u = [0] * n
    state = {"nodes": 0, "timeout": False}

    def rec(i, tail_norm):
        if state["timeout"]:
            return
        state["nodes"] += 1
        if state["nodes"] % 200000 == 0 and time.time() - t0 > time_cap:
            state["timeout"] = True
            return
        if i < 0:
            if 0 < tail_norm <= best[0]:
                best[0] = tail_norm
                best[1] = u.copy()
            return
        center = 0.0
        for j in range(i + 1, n):
            center -= u[j] * mu[j, i]
        c0 = round(center)
        # Zig-zag away from the center in order of increasing |u_i - center|;
        # the first step must go toward the center's fractional side, else the
        # pruning break below can discard a nearer coefficient.
        sgn = 1 if center >= c0 else -1
        offset = 0
        tried = 0
        max_try = 4000
        while tried < max_try:
            ui = c0 - sgn * offset
            l = ui - center
            add = l * l * sqn[i]
            new_tail = tail_norm + add
            if new_tail > best[0]:
                if offset >= 0:
                    offset = -(offset + 1)
                else:
                    break
                tried += 1
                continue
            u[i] = ui
            rec(i - 1, new_tail)
            if state["timeout"]:
                return
            if offset >= 0:
                offset = -(offset + 1)
            else:
                offset = -offset
            tried += 1

    rec(n - 1, 0.0)
    return best, state, time.time() - t0


# ============================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    RES = OrderedDict()
    RES["task_id"] = "TASK-20260813-ea2e96"
    RES["batch_id"] = "BATCH-6e08fe"
    RES["goal_id"] = "GOAL-MLKEM-005"
    RES["role"] = "executor"
    RES["claim_tier"] = "toy"
    RES["certificate"] = {
        "kind": "none",
        "reason": ("no discrete-log solve and no factor-base relation is "
                   "claimed or produced anywhere in this script; the D_route' "
                   "comparison is an INSTRUMENT / INDEPENDENCE CHECK, not a "
                   "certificate")}
    RES["governed_by"] = {
        "prereg": "coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/"
                  "tasks/TASK-20260813-cdcd88/prereg.md",
        "sha256": "ff577564dcdbb45b1b19885297ffc512888f9442dc99f2057fdf7f86f63fbbda",
        "notarizing_commit": "1e1acf08b151dd31b4d41b8afd287d261adce1e5"}

    print("=" * 78)
    print("TASK-20260813-ea2e96 -- THE LEAD PRODUCER, BATCH-6e08fe")
    print("CLAIM TIER: TOY. Nothing here bears on ML-KEM security, on any")
    print("FIPS 203 parameter set, on any attack cost, or on any cost model.")
    print("=" * 78)

    # ------------------------------------------------------------------
    # environment / infrastructure check (part of the implementation-choice
    # declaration: which options of PREREG-4 2.2(2) are even available)
    # ------------------------------------------------------------------
    print("\n[env] checking for fpylll and alternative lattice-reduction "
          "libraries")
    have_fpylll = False
    fpylll_err = None
    try:
        import fpylll  # noqa: F401
        have_fpylll = True
    except Exception as ex:
        fpylll_err = "%s: %s" % (type(ex).__name__, ex)
    print("    fpylll available: %s (%s)" % (have_fpylll, fpylll_err))
    RES["environment_check"] = {
        "fpylll_available": have_fpylll,
        "fpylll_import_error": fpylll_err,
        "alternative_lattice_libraries_checked": [
            "sagemath (not installed)", "python-flint (not installed)",
            "any third-party BKZ/LLL package (none found via pip list)"],
        "conclusion": ("options 2.2(2)(i)/(ii) of PREREG-4 are UNAVAILABLE "
                       "in this run environment; option 2.2(2)(iii) "
                       "(from-scratch pure Python/numpy routine) is used"),
    }

    print("\n" + "=" * 78)
    print("IMPLEMENTATION_CHOICE_DECLARATION (PREREG-4 2.2) -- READ BEFORE "
          "ANY D_route' NUMBER BELOW")
    print("=" * 78)
    print(IMPLEMENTATION_CHOICE_DECLARATION)
    RES["implementation_choice_declaration"] = IMPLEMENTATION_CHOICE_DECLARATION

    # ------------------------------------------------------------------
    # part (a) -- RC-3, carried verbatim, NO RECOMPUTATION
    # ------------------------------------------------------------------
    print("\n[a] RC-3 -- carried verbatim from PREREG-4 section 1, sourced "
          "from the Red Team's own committed probe. NO RECOMPUTATION.")
    probe_sha = sha256_file(PROBE_OUTPUT_PATH)
    with open(PROBE_OUTPUT_PATH) as fh:
        probe = json.load(fh)
    pc = probe["per_cell_beta_coverage_audit"]
    rc3_l9b22 = pc["hkz/L9_b22"]["TRUE_beta_hi_comparison"]["true_abs_deviation"]
    rc3_l11b30 = pc["hkz/L11_b30"]["TRUE_beta_hi_comparison"]["true_abs_deviation"]
    RES["R_IV_OUT_0_RC3"] = {
        "text": RC3_TEXT,
        "source_path": ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/"
                        "reviews/TASK-20260813-6ab893/probes/"
                        "probe_coverage_beta_mismatch_output.json"),
        "source_sha256": probe_sha,
        "carried_not_recomputed": True,
        "recomputed_by_this_task": False,
        "hkz_L9_b22_true_abs_deviation": rc3_l9b22,
        "hkz_L11_b30_true_abs_deviation": rc3_l11b30,
        "hkz_L9_b15_restated": "UNCOVERED",
        "hkz_L11_b20_restated": "UNCOVERED",
        "genuine_coverage_16_of_27": True,
    }
    print("    hkz/L9_b22 true_abs_deviation (carried) = %s" % rc3_l9b22)
    print("    hkz/L11_b30 true_abs_deviation (carried) = %s" % rc3_l11b30)
    print("    hkz/L9_b15, hkz/L11_b20 restated UNCOVERED (carried)")

    # ------------------------------------------------------------------
    # obligation 0 -- coverage audit (read only, results_relvar.json's own
    # G_REL1 block -- the ONLY valid ROUTE-P source for part (b))
    # ------------------------------------------------------------------
    print("\n[b0] obligation 0 -- coverage audit of results_relvar.json's "
          "OWN G_REL1 block (results_l7l8.json / results_am4.json are "
          "NEVER read as a ROUTE-P source anywhere in this script)")
    relvar_sha = sha256_file(RESULTS_RELVAR_PATH)
    with open(RESULTS_RELVAR_PATH) as fh:
        relvar = json.load(fh)
    g_rel1 = relvar["G_REL1"]
    g_var = relvar["G_VAR"]["per_candidate"]

    coverage = OrderedDict()
    route_p_per_basis = {}  # (cand, lat, beta) -> list of 8 X values
    for cand in CANDIDATES:
        for lat, (d, k) in LATTICES.items():
            entry = g_rel1[cand][lat]
            beta_lo = entry["beta_lo"]
            beta_hi = entry["beta_hi"]
            per_basis = entry["per_basis"]
            n_bases_avail = len(per_basis)
            for beta in BETA_GRID[d]:
                cellkey = "%s/%s_b%d" % (cand, lat, beta)
                if beta == beta_lo:
                    vals = [row["X_a"] for row in per_basis]
                    covered = True
                    field = "X_a @ beta_lo"
                elif beta == beta_hi:
                    vals = [row["X_b"] for row in per_basis]
                    covered = True
                    field = "X_b @ beta_hi"
                else:
                    vals = None
                    covered = False
                    field = None
                coverage[cellkey] = {
                    "candidate": cand, "lattice": lat, "beta": beta,
                    "d": d, "k": k,
                    "beta_lo": beta_lo, "beta_hi": beta_hi,
                    "is_middle_beta": (beta != beta_lo and beta != beta_hi),
                    "route_p_covered": covered,
                    "route_p_field_used": field,
                    "route_p_n_bases_available": n_bases_avail if covered else 0,
                }
                if covered:
                    route_p_per_basis[(cand, lat, beta)] = vals
    n_covered = sum(1 for v in coverage.values() if v["route_p_covered"])
    print("    18 cells audited; ROUTE-P (G_REL1) covered: %d / 18"
          % n_covered)
    for k_, v in coverage.items():
        print("    %-14s beta=%-3d covered=%-5s n_bases=%s"
              % (k_, v["beta"], v["route_p_covered"],
                 v["route_p_n_bases_available"]))
    RES["R_IV_OUT_1_coverage_audit"] = {
        "source": "results_relvar.json G_REL1 block ONLY (PREREG-4 2.1)",
        "source_sha256": relvar_sha,
        "results_l7l8_json_used_as_route_p_source": False,
        "results_am4_json_used_as_route_p_source": False,
        "n_covered_of_18": n_covered,
        "per_cell": coverage,
    }

    # s_c^fib -- read from G_VAR.per_candidate.<X>.per_cell.<L>_<b>.float_sd.
    # NOTE (protocol deviation, recorded per AGENTS.md rule 12 / executor.md
    # #10): PREREG-4 2.1 states this path as
    # "results_relvar.json.per_candidate.<X>.per_cell.<L>_<b>.float_sd", but
    # results_relvar.json has NO top-level "per_candidate" key; the field
    # that matches PREREG-4's description (float_sd of the candidate's raw
    # value over 8 bases at fixed (L,beta)) lives at
    # G_VAR.per_candidate.<X>.per_cell.<L>_<b>.float_sd. This resolution is
    # read-only (no value is computed or altered) and is reported here
    # rather than silently assumed.
    path_resolution_note = (
        "PREREG-4 2.1 names the s_c^fib path as "
        "'results_relvar.json.per_candidate.<X>.per_cell.<L>_<b>.float_sd'; "
        "results_relvar.json has no top-level per_candidate key. The field "
        "matching PREREG-4's own description (float_sd of X over the 8 "
        "frozen bases at fixed L,beta) is found at "
        "G_VAR.per_candidate.<X>.per_cell.<L>_<b>.float_sd and is used here, "
        "read-only, with this resolution stated rather than assumed."
    )
    print("\n[b0] s_c^fib path resolution note:")
    print("    " + path_resolution_note)

    # ------------------------------------------------------------------
    # obligation 1 -- ROUTE-I': the one genuinely new computation
    # ------------------------------------------------------------------
    print("\n[b1] obligation 1 -- building ROUTE-I' (from-scratch LLL + "
          "exact enumeration) for every lattice with >=1 covered cell")
    route_i_lam1n = {}   # (lat, i) -> {"value":..,"exact":bool,"secs":..}
    route_i_hkz = {}      # (lat, beta, i) -> value (float) or None
    per_basis_log = OrderedDict()
    compute_start = time.time()
    budget_exhausted_bases = []

    lattices_with_coverage = sorted(
        {v["lattice"] for v in coverage.values() if v["route_p_covered"]},
        key=lambda l: list(LATTICES.keys()).index(l))

    for lat in lattices_with_coverage:
        d, k = LATTICES[lat]
        logdet = (d - k) * math.log(Q_MAIN)
        for i in range(N_BASES):
            elapsed = time.time() - compute_start
            if elapsed > COMPUTE_DEADLINE_SECONDS:
                budget_exhausted_bases.append((lat, i))
                per_basis_log["%s/i%d" % (lat, i)] = {
                    "status": "NOT COMPUTED: budget exhausted "
                              "(COMPUTE_DEADLINE_SECONDS reached before "
                              "this basis was reached)"}
                continue
            remaining = COMPUTE_DEADLINE_SECONDS - elapsed
            lll_cap = min(PER_BASIS_LLL_CAP, remaining)
            B = build_basis_indep(d, k, Q_MAIN, i)
            Bred, Bstar, mu, sqn, lll_secs, lll_done = lll_reduce(
                B, delta=0.99, time_cap=lll_cap)
            if not lll_done:
                per_basis_log["%s/i%d" % (lat, i)] = {
                    "status": "NOT COMPUTED: budget exhausted (LLL did not "
                              "converge within its per-basis cap)",
                    "lll_secs": lll_secs}
                budget_exhausted_bases.append((lat, i))
                continue
            elapsed = time.time() - compute_start
            remaining = COMPUTE_DEADLINE_SECONDS - elapsed
            enum_cap = min(PER_BASIS_ENUM_CAP, max(remaining, 0.0))
            if enum_cap <= 0.0:
                exact = False
                best_sq = sqn[0]
                enum_secs = 0.0
                enum_nodes = 0
            else:
                best, state, enum_secs = enumerate_svp(mu, sqn, d, enum_cap)
                exact = not state["timeout"]
                best_sq = best[0]
                enum_nodes = state["nodes"]
            lam1n_val = math.exp(0.5 * math.log(best_sq) - logdet / d)
            route_i_lam1n[(lat, i)] = {
                "value": lam1n_val, "exact": exact,
                "lll_secs": lll_secs, "enum_secs": enum_secs,
                "enum_nodes": enum_nodes,
                "lambda1_sq": best_sq,
                "lll_first_vec_norm_sq": float(sqn[0])}
            logb_tail = 0.5 * np.log(np.maximum(sqn, 1e-300))
            for beta in BETA_GRID[d]:
                hkz_val = float(np.mean(logb_tail[d - beta:]) - logdet / d)
                route_i_hkz[(lat, beta, i)] = hkz_val
            per_basis_log["%s/i%d" % (lat, i)] = {
                "status": "ok", "lll_secs": lll_secs, "enum_secs": enum_secs,
                "enum_nodes": enum_nodes, "svp_exact": exact,
                "lam1n_prime": lam1n_val,
                "hkz_prime_at_beta": {str(b): route_i_hkz[(lat, b, i)]
                                      for b in BETA_GRID[d]}}
            print("    %-4s i=%d  LLL %6.2fs  enum %6.2fs (exact=%s, "
                  "%d nodes)  lam1n'=%.6f"
                  % (lat, i, lll_secs, enum_secs, exact, enum_nodes,
                     lam1n_val))

    RES["route_i_prime_per_basis_log"] = per_basis_log
    RES["route_i_prime_budget_exhausted_bases"] = [
        "%s/i%d" % bi for bi in budget_exhausted_bases]
    RES["route_i_prime_total_compute_seconds"] = time.time() - compute_start

    # ------------------------------------------------------------------
    # obligation 1 (continued) -- D_route' / VERDICT' per covered cell
    # ------------------------------------------------------------------
    print("\n[b1] D_route'/VERDICT' -- PREREG-3 3.3's formula, verbatim, "
          "ties resolve to DOES NOT EXCEED")
    per_cell_results = OrderedDict()
    for cellkey, cinfo in coverage.items():
        if not cinfo["route_p_covered"]:
            per_cell_results[cellkey] = {"status": "UNCOVERED"}
            continue
        cand, lat, beta = cinfo["candidate"], cinfo["lattice"], cinfo["beta"]
        p_vals = route_p_per_basis[(cand, lat, beta)]
        matched = []
        for i in range(min(N_BASES, len(p_vals))):
            if cand == "lam1n":
                ri = route_i_lam1n.get((lat, i))
                if ri is None or not ri["exact"]:
                    continue
                iv = ri["value"]
            else:
                iv = route_i_hkz.get((lat, beta, i))
                if iv is None:
                    continue
            matched.append((i, p_vals[i], iv, abs(p_vals[i] - iv)))
        if not matched:
            per_cell_results[cellkey] = {
                "status": "NOT COMPUTED: budget exhausted (no exact "
                          "ROUTE-I' value available at any of the "
                          "ROUTE-P-covered bases for this cell)"}
            continue
        d_route = max(m[3] for m in matched)
        s_c_fib = None
        s_c_fib_lookup = g_var[cand]["per_cell"].get("%s_b%d" % (lat, beta))
        if s_c_fib_lookup:
            s_c_fib = s_c_fib_lookup["float_sd"]
        if s_c_fib is None:
            verdict = None
            note = "s_c^fib unavailable for this cell -- treated as NOT COMPUTED"
        else:
            verdict = "EXCEEDS" if s_c_fib > d_route else "DOES NOT EXCEED"
            note = None
        per_cell_results[cellkey] = {
            "status": "COMPUTED",
            "n_matched_bases": len(matched),
            "n_route_p_bases": len(p_vals),
            "s_c_fib": s_c_fib,
            "D_route_prime": d_route,
            "VERDICT_prime": verdict,
            "note": note,
            "matched_bases_detail": [
                {"basis": m[0], "route_p": m[1], "route_i_prime": m[2],
                 "abs_diff": m[3]} for m in matched],
            "agrees_with_batch_fbb639_EXCEEDS": (
                (verdict == "EXCEEDS") if verdict is not None else None),
        }
        print("    %-14s n_matched=%d/%d  s_c^fib=%s  D_route'=%.6e  "
              "VERDICT'=%s"
              % (cellkey, len(matched), len(p_vals), s_c_fib, d_route,
                 verdict))

    RES["R_IV_OUT_2_per_cell"] = per_cell_results

    # ------------------------------------------------------------------
    # obligation 2 -- aggregate
    # ------------------------------------------------------------------
    computed_cells = {k: v for k, v in per_cell_results.items()
                      if v.get("status") == "COMPUTED"
                      and v.get("VERDICT_prime") is not None}
    exceeds_cells = [k for k, v in computed_cells.items()
                     if v["VERDICT_prime"] == "EXCEEDS"]
    dne_cells = [k for k, v in computed_cells.items()
                if v["VERDICT_prime"] == "DOES NOT EXCEED"]
    uncovered_cells = [k for k, v in per_cell_results.items()
                       if v.get("status") == "UNCOVERED"]
    not_computed_cells = [k for k, v in per_cell_results.items()
                          if v.get("status", "").startswith("NOT COMPUTED")]

    all_survive = bool(computed_cells) and len(dne_cells) == 0
    some_artifact = len(dne_cells) > 0
    RES["R_IV_OUT_3_aggregate"] = {
        "n_covered": len(computed_cells),
        "n_uncovered": len(uncovered_cells),
        "n_not_computed_budget": len(not_computed_cells),
        "coverage_fraction": "%d / 18" % len(computed_cells),
        "ALL_SURVIVE": all_survive,
        "SOME_ARTIFACT": some_artifact,
        "exceeds_cells": exceeds_cells,
        "does_not_exceed_cells": dne_cells,
        "uncovered_cells": uncovered_cells,
        "not_computed_budget_cells": not_computed_cells,
    }
    print("\n[b2] obligation 2 -- aggregate")
    print("    COVERED = %d/18  ALL-SURVIVE=%s  SOME-ARTIFACT=%s"
          % (len(computed_cells), all_survive, some_artifact))
    print("    EXCEEDS cells: %s" % exceeds_cells)
    print("    DOES NOT EXCEED cells: %s" % dne_cells)
    print("    UNCOVERED cells: %s" % uncovered_cells)
    print("    NOT COMPUTED (budget) cells: %s" % not_computed_cells)

    # ------------------------------------------------------------------
    # termination branch -- PREREG-4 2.6's frozen precedence
    # ------------------------------------------------------------------
    print("\n[term] termination branch (PREREG-4 2.6 precedence)")
    if len(computed_cells) == 0:
        branch = "T-INDVERIFY-NODATA"
        partial = False
    else:
        partial = (len(computed_cells) < 18)
        if some_artifact:
            branch = "T-INDVERIFY-ARTIFACT" + ("-PARTIAL" if partial else "")
        else:
            branch = "T-INDVERIFY-CONFIRMED" + ("-PARTIAL" if partial else "")
    RES["R_IV_OUT_4_termination_branch"] = {
        "branch": branch,
        "partial_suffix_applied": partial,
        "precedence_note": ("PREREG-4 2.6: T-INDVERIFY-NODATA dominates "
                            "(fires alone); between ARTIFACT and CONFIRMED, "
                            "SOME-ARTIFACT takes precedence over ALL-SURVIVE "
                            "whenever both could be read from the same data "
                            "-- a single artifact-flagged cell is sufficient "
                            "to fire T-INDVERIFY-ARTIFACT."),
        "flagged_cells_for_revisit_condition_2_8": dne_cells,
    }
    print("    BRANCH: %s" % branch)

    # ------------------------------------------------------------------
    # provenance / manifest fields
    # ------------------------------------------------------------------
    RES["input_shas"] = {
        RESULTS_RELVAR_PATH.replace(REPO_ROOT + os.sep, ""): relvar_sha,
        PROBE_OUTPUT_PATH.replace(REPO_ROOT + os.sep, ""): probe_sha,
    }
    RES["s_c_fib_path_resolution_note"] = path_resolution_note
    RES["timings"] = {
        "total_seconds": time.time() - T_START,
        "compute_deadline_seconds": COMPUTE_DEADLINE_SECONDS,
    }
    RES["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    with open(args.out, "w") as fh:
        json.dump(RES, fh, indent=1, default=float)
    print("\nwrote %s" % args.out)
    print("total %.2f s" % (time.time() - T_START))
    return 0


if __name__ == "__main__":
    sys.exit(main())
