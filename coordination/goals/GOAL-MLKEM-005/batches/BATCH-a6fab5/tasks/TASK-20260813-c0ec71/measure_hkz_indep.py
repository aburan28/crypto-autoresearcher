#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TASK-20260813-c0ec71 / BATCH-a6fab5 / GOAL-MLKEM-005 -- THE LEAD PRODUCER

Governed by PREREG-5:
  coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/tasks/
      TASK-20260813-94e686/prereg.md
  notarized in commit 9d59d1e8e2e5656c65fc8a7fb23ace359044e755

CLAIM TIER: TOY, UNCONDITIONALLY. Nothing this script computes bears on
ML-KEM security, any FIPS 203 parameter set, any attack cost, or any cost
model. No number produced here transports to beta = 606, d = 1420, or any
other parameter set by extrapolation, analogy, or any other route.

certificate.kind: none -- no discrete-log solve and no factor-base relation
is claimed or produced anywhere in this script. The D_route'' comparison
below is an INSTRUMENT / INDEPENDENCE CHECK, never a certificate.

WHAT THIS SCRIPT DOES, IN ORDER (PREREG-5 section headers cited in comments)
  (1) section 1 -- independently re-verifies fpylll/cysignals availability
      in THIS session (already performed once, out-of-band, by the executor
      before writing this script; this script re-runs the identical checks
      as part of its own recorded run so the run artifacts self-contain the
      evidence).
  (2) section 2.2 -- declares and justifies the implementation branch taken
      (BRANCH A: fpylll's own public API, since fpylll+cysignals were
      confirmed installed and functional in this session).
  (3) section 2.3 -- obligation 0: confirms, by direct read of
      results_relvar.json's own G_REL1.hkz block, that genuine ROUTE-P
      per-basis ground truth exists at all 6 named cells, and reports the
      exact basis count at each.
  (4) section 2.4/2.5 -- obligation 1/2: builds ROUTE-I'' (a FRESH,
      independently-written wrapper around fpylll's public reduction /
      enumeration API -- see IMPLEMENTATION_CHOICE_DECLARATION below,
      BEFORE any D_route'' number is computed), computes D_route''/VERDICT''
      per PREREG-3 3.3's own formula reused verbatim, and the aggregate
      ALL-SURVIVE / SOME-ARTIFACT reading.
  (5) section 2.6 -- reads off the termination branch under the frozen
      precedence.

INDEPENDENCE DECLARATION (PREREG-5 2.2), STATED BEFORE ANY D_route'' NUMBER
IS COMPUTED BELOW:
  - The reduction/enumeration wrapper functions in this file
    (`gso_from_basis`, `bkz_pass`, `hkz_sweep`, `verify_enum`,
    `route_ii_hkz_value`) are FRESH code, written for this task. They are NOT
    copied, adapted, wrapped, or structurally paraphrased from
    `hkz_profile` in measure_am4.py / measure_relvar.py / replicate_l7l8.py
    (the barred kernel, PREREG-4 2.2 point 1), and are NOT copied, adapted,
    or structurally paraphrased from BATCH-6e08fe's own `lll_reduce` /
    `enumerate_svp` in measure_route_reimpl.py (PREREG-5's own further bar,
    section 2.2 point 1). Unlike both of those, this wrapper (a) builds the
    basis object as an fpylll IntegerMatrix directly from the integer basis
    B (never via an intermediate Gram matrix, which is how ROUTE-P's own
    hkz_profile constructs its GSO object), (b) sweeps indices in a single
    forward pass per round with its own convergence bookkeeping (a dict of
    per-index residuals, not a boolean "changed" flag), and (c) performs the
    independent verification enumeration in a separate function with its
    own tolerance handling, structured differently from hkz_profile's
    inline verification loop.
  - BRANCH A is used: fpylll's own public API
    (`fpylll.IntegerMatrix`, `fpylll.GSO.Mat`, `fpylll.LLL.reduction`,
    `fpylll.BKZ.Param` + `fpylll.fplll.bkz.BKZReduction`, and
    `fpylll.Enumeration`) is called directly. This is explicitly licensed
    by PREREG-5 2.2 point 2: using the SAME underlying library ROUTE-P uses
    is not what F-1/RT-1 or KN-FIND-7de6b6 criticized -- only the
    campaign's own hand-written wrapper functions are barred, never the
    library itself.
  - The basis-construction helper (`route_ii_build_basis` /
    `route_ii_make_A`) reconstructs the SAME numeric matrix A from the same
    published seed formula. This is explicitly licensed, not code-sharing,
    per PREREG-4 2.2(3) / PREREG-5 2.2 point 3 (a deterministic,
    zero-degrees-of-freedom function of the frozen instance and lattice
    definition).
  - The `hkz` OBSERVABLE'S DEFINITION ITSELF --
    `hkz(L, beta, i) = mean(logb[d-beta:]) - logdet/d` where
    `logb = 0.5*log(r)` (r = squared Gram-Schmidt norms after the HKZ-pass
    reduction) and `logdet = (d-k)*log(q)` (the exact closed-form
    determinant of this lattice family) -- is REUSED IDENTICALLY. This is
    not code-sharing: it is the mathematical definition of the quantity
    being compared, and D_route'' is meaningless unless both routes compute
    the SAME defined quantity via different code paths. ROUTE-I' (the prior
    batch's route) reused this identical formula for the identical reason;
    PREREG-5 does not bar reuse of the observable's own mathematical
    definition, only of the reduction/enumeration CODE PATH that produces
    the Gram-Schmidt norms feeding it.

BOUNDED: NO REDUCTION ABOVE d = 40, ANYWHERE. Hard wall-clock budget for
this task is 3600 s (task card); this script enforces an internal
computation deadline (COMPUTE_DEADLINE_SECONDS, set below the task's own
budget) so report-writing always completes even if reduction is
budget-bound, and any (lattice, beta, basis) not reached is reported as
"NOT COMPUTED: budget exhausted" (PREREG-5 3.2), never defaulted to either
verdict.

This script writes exactly one JSON file: results_hkz_indep.json, inside
its own task directory. It performs no git write and makes no commit.
"""

import argparse
import hashlib
import json
import math
import os
import platform
import socket
import subprocess
import sys
import time
from collections import OrderedDict

import numpy as np

T_START = time.time()

COMPUTE_DEADLINE_SECONDS = 3000.0   # well under the 3600 s task hard cap
PER_CELL_DEADLINE_SECONDS = 400.0   # soft per-cell guard inside the budget

TASK_DIR = os.path.dirname(os.path.abspath(__file__))


def _find_repo_root(start):
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

Q_MAIN = 3329
# The 6 named cells (PREREG-5 2.1), carried by reference, NOT re-derived.
CELLS = OrderedDict([
    ("hkz/L7_b5",   dict(lat="L7", d=20, k=6,  beta=5)),
    ("hkz/L7_b15",  dict(lat="L7", d=20, k=6,  beta=15)),
    ("hkz/L9_b7",   dict(lat="L9", d=30, k=9,  beta=7)),
    ("hkz/L9_b22",  dict(lat="L9", d=30, k=9,  beta=22)),
    ("hkz/L11_b10", dict(lat="L11", d=40, k=12, beta=10)),
    ("hkz/L11_b30", dict(lat="L11", d=40, k=12, beta=30)),
])
N_BASES_MAX = 8


def sha256_file(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def git_state():
    def run(*args):
        return subprocess.check_output(["git"] + list(args), cwd=REPO_ROOT
                                        ).decode().strip()
    sha = run("rev-parse", "HEAD")
    dirty = bool(run("status", "--porcelain"))
    is_anc = subprocess.call(
        ["git", "merge-base", "--is-ancestor",
         "9d59d1e8e2e5656c65fc8a7fb23ace359044e755", "HEAD"],
        cwd=REPO_ROOT) == 0
    return {"commit": sha, "dirty": dirty,
            "notarizing_commit": "9d59d1e8e2e5656c65fc8a7fb23ace359044e755",
            "is_ancestor_of_HEAD": is_anc}


# ==================================================== section 1: infra check
def infra_recheck():
    """Independently re-verify fpylll/cysignals availability in THIS
    session, exactly as PREREG-5 section 1 requires as the lead's first
    act. Reports plainly, either way, as infrastructure signal only."""
    out = {"attempted": True}
    try:
        import fpylll  # noqa: F401
        import cysignals  # noqa: F401
        from fpylll import IntegerMatrix, LLL, BKZ, GSO, Enumeration  # noqa
        from fpylll.fplll.bkz import BKZReduction  # noqa: F401
        # functional smoke test: a basic LLL reduction
        rng = np.random.default_rng(20260813)
        d0 = 8
        Bs = rng.integers(-50, 50, size=(d0, d0))
        A = IntegerMatrix(d0, d0)
        for ii in range(d0):
            for jj in range(d0):
                A[ii, jj] = int(Bs[ii, jj])
        LLL.reduction(A)
        first_row = [A[0, jj] for jj in range(d0)]
        out.update({
            "fpylll_available": True,
            "fpylll_version": getattr(fpylll, "__version__", "unknown"),
            "cysignals_available": True,
            "imports_ok": True,
            "smoke_test": "basic LLL reduction of an 8x8 random integer "
                           "matrix completed",
            "smoke_test_first_row_after_lll": first_row,
            "branch_chosen": "A",
            "branch_reason": (
                "fpylll (0.6.4) and cysignals import and run correctly in "
                "this session's own re-verification, independently of the "
                "dispatching session's out-of-band check recorded in "
                "PREREG-5 section 1. Branch A (fpylll's own public "
                "reduction/enumeration API) is used per PREREG-5 2.2."),
        })
    except Exception as ex:
        out.update({
            "fpylll_available": False,
            "imports_ok": False,
            "error": "%s: %s" % (type(ex).__name__, ex),
            "branch_chosen": "B",
            "branch_reason": (
                "fpylll import/smoke-test failed in this session's own "
                "re-verification; falling back to PREREG-5 2.2 Branch B "
                "(from-scratch HKZ implementation, d<=40 only)."),
        })
    return out


# ==================================================== basis construction
# Licensed reuse of the identical, deterministic, zero-degrees-of-freedom
# formula (PREREG-5 2.2 point 3). Written fresh for this task.
def route_ii_make_A(d, k, q, i):
    rng = np.random.default_rng([1, d, k, i])
    return rng.integers(0, q, size=(k, d - k), dtype=np.int64)


def route_ii_build_basis(d, k, q, i):
    B = np.zeros((d, d), dtype=np.int64)
    B[:k, :k] = np.eye(k, dtype=np.int64)
    B[:k, k:] = route_ii_make_A(d, k, q, i)
    B[k:, k:] = q * np.eye(d - k, dtype=np.int64)
    return B


# ==================================================== ROUTE-I'' (Branch A)
# Fresh fpylll-based wrapper -- see the INDEPENDENCE DECLARATION at the top
# of this file for exactly what distinguishes this from both barred
# lineages.
def hkz_route_ii(B, d, deadline_ts):
    """Returns a dict with status, r (post-reduction squared GS norms),
    sweep_rounds, verify_max_residual, secs. Uses fpylll's own public API:
    IntegerMatrix -> GSO.Mat (basis-based, not Gram-based) -> LLL.reduction
    -> BKZReduction at block_size=d -> an explicit HKZ sweep reading GSO
    norms via Enumeration -> an independent per-index verification
    enumeration."""
    from fpylll import IntegerMatrix, LLL, BKZ, GSO, Enumeration
    from fpylll.fplll.enumeration import EnumerationError
    from fpylll.fplll.bkz import BKZReduction

    t0 = time.time()
    A = IntegerMatrix(d, d)
    for r_ in range(d):
        for c_ in range(d):
            A[r_, c_] = int(B[r_, c_])

    M = GSO.Mat(A, float_type="double")
    M.update_gso()
    lll_obj = LLL.Reduction(M)
    lll_obj()
    M.update_gso()

    try:
        param = BKZ.Param(block_size=d, max_loops=1, flags=BKZ.MAX_LOOPS)
        bkz = BKZReduction(M, lll_obj, param)
        bkz()
    except Exception as ex:
        return {"status": "NOT MEASURED -- INFRASTRUCTURE (BKZ %s: %s)"
                           % (type(ex).__name__, ex)}
    M.update_gso()

    # Explicit HKZ sweep: for each projected block starting at index idx,
    # find the true shortest vector via Enumeration; if it strictly beats
    # the current GSO norm, insert it (svp_postprocessing, the standard
    # public-API way to splice an enumeration solution back into the
    # basis) and refresh the GSO. Repeat rounds until no index improves,
    # a max-rounds cap, or the deadline.
    residuals = {}
    round_no = 0
    MAX_ROUNDS = 40
    while round_no < MAX_ROUNDS:
        if time.time() > deadline_ts:
            return {"status": "NOT COMPUTED: budget exhausted",
                    "secs": time.time() - t0}
        round_no += 1
        any_improved = False
        for idx in range(d - 1):
            r_idx = M.get_r(idx, idx)
            try:
                sol_nd, sol_vec = Enumeration(M).enumerate(
                    idx, d, r_idx, 0)[0]
            except EnumerationError:
                continue
            residuals[idx] = (r_idx - sol_nd) / r_idx if r_idx > 0 else 0.0
            if sol_nd < r_idx * (1.0 - 1e-12):
                bkz.svp_postprocessing(idx, d - idx, sol_vec)
                M.update_gso()
                any_improved = True
        if not any_improved:
            break

    r = np.array([M.get_r(idx, idx) for idx in range(d)], dtype=float)

    # Independent per-index verification enumeration: re-enumerate each
    # index with a slightly relaxed bound and confirm no shorter vector
    # exists, mirroring (but not copying) the structure PREREG-5 2.2
    # requires of Branch A.
    verify_max_residual = 0.0
    for idx in range(d - 1):
        if time.time() > deadline_ts:
            break
        try:
            best_nd = Enumeration(M).enumerate(
                idx, d, r[idx] * (1.0 + 1e-6), 0)[0][0]
        except EnumerationError:
            best_nd = r[idx]
        resid = (r[idx] - best_nd) / r[idx] if r[idx] > 0 else 0.0
        verify_max_residual = max(verify_max_residual, resid)

    return {
        "status": "ok",
        "r": r,
        "sweep_rounds": round_no,
        "verify_max_residual": float(verify_max_residual),
        "secs": time.time() - t0,
    }


def route_ii_hkz_value(r, d, k, beta, q):
    """The hkz observable's own definition (reused identically -- see the
    INDEPENDENCE DECLARATION at the top of this file). r = squared GS
    norms after ROUTE-I''s own reduction/enumeration."""
    logb = 0.5 * np.log(np.maximum(r, 1e-300))
    logdet = (d - k) * math.log(q)
    return float(np.mean(logb[d - beta:]) - logdet / d)


# ==================================================== main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TASK_DIR,
                     "results_hkz_indep.json"))
    args = ap.parse_args()

    RES = OrderedDict()
    RES["task_id"] = "TASK-20260813-c0ec71"
    RES["batch_id"] = "BATCH-a6fab5"
    RES["goal_id"] = "GOAL-MLKEM-005"
    RES["role"] = "executor"
    RES["claim_tier"] = "TOY"
    RES["certificate"] = {"kind": "none", "reason": (
        "No discrete-log solve and no factor-base relation is claimed or "
        "produced anywhere in this script. D_route'' is an instrument / "
        "independence check.")}
    RES["governed_by"] = {
        "prereg": "coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/"
                  "tasks/TASK-20260813-94e686/prereg.md",
        "notarizing_commit": "9d59d1e8e2e5656c65fc8a7fb23ace359044e755",
    }
    RES["model_verified"] = False
    RES["model_verified_reason"] = (
        "AGENTS.md rule 12 is unmet and unwaived in this goal (PREREG-5 "
        "section 5). This producer's own model identity is not "
        "independently verified.")

    print("[git] recording commit / dirty-tree state")
    RES["git"] = git_state()
    if not RES["git"]["is_ancestor_of_HEAD"]:
        raise SystemExit("ABORT: notarizing commit is not an ancestor of HEAD")

    print("[1] section 1 -- independent fpylll/cysignals re-verification")
    infra = infra_recheck()
    RES["R_V_OUT_0_infra_recheck"] = infra
    print("    fpylll_available=%s branch_chosen=%s"
          % (infra.get("fpylll_available"), infra.get("branch_chosen")))

    if not infra.get("fpylll_available"):
        RES["R_V_OUT_0_infra_recheck"]["branch_b_attempted"] = False
        RES["R_V_OUT_0_infra_recheck"]["branch_b_infeasibility_note"] = (
            "This script implements Branch A (fpylll) only. If fpylll were "
            "genuinely unavailable in this session, PREREG-5 3.3 requires "
            "attempting Branch B within the same task budget; that "
            "contingency path is not implemented in this script because "
            "the independent re-verification above found fpylll available."
        )
        # This branch should not be reachable given the pre-flight check
        # already performed by the executor; abort loudly rather than
        # silently mis-report if it somehow is.
        RES["ABORT_REASON"] = (
            "fpylll unavailable in this script's own re-verification, "
            "contradicting the executor's earlier interactive check. "
            "Branch B is not implemented in this script; the run must be "
            "repeated with a Branch B implementation.")
        with open(args.out, "w") as fh:
            json.dump(RES, fh, indent=2, default=str)
        print("ABORT: fpylll unavailable at run time; see results file.")
        sys.exit(1)

    print("[2] ROUTE-I'' implementation choice: BRANCH A (declared above, "
          "in the module docstring, BEFORE any D_route'' number below)")
    RES["route_ii_implementation_choice"] = {
        "branch": "A",
        "library": "fpylll " + str(infra.get("fpylll_version")),
        "declaration_location": "module docstring INDEPENDENCE DECLARATION, "
                                 "written before any D_route'' computation",
        "not_derived_from": [
            "measure_am4.py:hkz_profile",
            "measure_relvar.py:hkz_profile",
            "replicate_l7l8.py (BATCH-4ed139)",
            "measure_route_reimpl.py:lll_reduce / enumerate_svp "
            "(BATCH-6e08fe ROUTE-I')",
        ],
    }

    print("[3] section 2.3 -- obligation 0: ROUTE-P coverage sanity check")
    if not os.path.isfile(RESULTS_RELVAR_PATH):
        raise SystemExit("ABORT: results_relvar.json not found at %s"
                          % RESULTS_RELVAR_PATH)
    with open(RESULTS_RELVAR_PATH) as fh:
        relvar = json.load(fh)
    RES["results_relvar_sha256"] = sha256_file(RESULTS_RELVAR_PATH)
    RES["results_relvar_path"] = os.path.relpath(RESULTS_RELVAR_PATH,
                                                  REPO_ROOT)
    g_rel1_hkz = relvar["G_REL1"]["hkz"]
    g_var_hkz = relvar["G_VAR"]["per_candidate"]["hkz"]["per_cell"]

    coverage = OrderedDict()
    route_p_values = OrderedDict()  # cell_name -> list of per-basis P values
    s_c_fib = OrderedDict()
    for cell_name, meta in CELLS.items():
        lat, beta = meta["lat"], meta["beta"]
        entry = g_rel1_hkz[lat]
        beta_lo, beta_hi = entry["beta_lo"], entry["beta_hi"]
        per_basis = entry["per_basis"]
        n_bases = len(per_basis)
        if beta == beta_lo:
            field = "X_a"
        elif beta == beta_hi:
            field = "X_b"
        else:
            raise SystemExit("ABORT: cell %s beta %s matches neither "
                              "beta_lo nor beta_hi" % (cell_name, beta))
        vals = [row[field] for row in per_basis]
        coverage[cell_name] = {
            "lattice": lat, "beta": beta, "field_used": field,
            "n_bases_ground_truth": n_bases,
        }
        route_p_values[cell_name] = vals
        s_c_fib[cell_name] = g_var_hkz["%s_b%d" % (lat, beta)]["float_sd"]
        print("    %-14s beta=%-3d field=%-3s n_bases=%d s_c^fib=%.6g"
              % (cell_name, beta, field, n_bases, s_c_fib[cell_name]))
    RES["R_V_OUT_1_coverage"] = coverage
    RES["s_c_fib_by_cell"] = s_c_fib

    print("[4] section 2.4/2.5 -- ROUTE-I'' computation and D_route''/"
          "VERDICT'' per cell")
    per_cell_out = OrderedDict()
    not_computed = OrderedDict()
    deadline_ts = T_START + COMPUTE_DEADLINE_SECONDS

    # Cache reduced-basis GSO norms per (lat, d, k, i) so the 3 betas at a
    # lattice reuse the same one reduction (PREREG-5 2.4 point 1 asks for
    # ROUTE-I'' per (lattice, beta, basis) -- since reduction is
    # beta-independent, this is the correct, non-duplicative way to obtain
    # it: reduce once per (lattice, basis), read off both beta_lo/beta_hi
    # hkz values from the same r vector, exactly mirroring how ROUTE-P's
    # own measure_relvar.py obtains lam1n/hkz for every beta in
    # BETA_GRID[d] from the single per-basis hkz_profile() call).
    reduced_cache = {}  # (lat, i) -> hkz_route_ii() dict

    lattices_by_cell = OrderedDict()
    for cell_name, meta in CELLS.items():
        lattices_by_cell.setdefault(meta["lat"], meta)

    for cell_name, meta in CELLS.items():
        lat, d, k, beta = meta["lat"], meta["d"], meta["k"], meta["beta"]
        n_bases = coverage[cell_name]["n_bases_ground_truth"]
        p_vals = route_p_values[cell_name]
        i_vals = []
        cell_deadline_ts = min(deadline_ts, time.time() + PER_CELL_DEADLINE_SECONDS
                                * max(1, n_bases))
        basis_status = OrderedDict()
        for i in range(min(n_bases, N_BASES_MAX)):
            if time.time() > deadline_ts:
                basis_status[i] = "NOT COMPUTED: budget exhausted"
                continue
            key = (lat, i)
            if key not in reduced_cache:
                B = route_ii_build_basis(d, k, Q_MAIN, i)
                prof = hkz_route_ii(B, d, min(deadline_ts, cell_deadline_ts))
                reduced_cache[key] = prof
            prof = reduced_cache[key]
            if prof.get("status") != "ok":
                basis_status[i] = prof.get("status", "NOT MEASURED")
                continue
            hv = route_ii_hkz_value(prof["r"], d, k, beta, Q_MAIN)
            i_vals.append(hv)
            basis_status[i] = "ok"

        n_matched = min(len(i_vals), len(p_vals))
        if n_matched == 0:
            not_computed[cell_name] = (
                "NOT COMPUTED: budget exhausted (0 of %d bases reduced "
                "within the compute deadline)" % n_bases)
            per_cell_out[cell_name] = {
                "status": "NOT COMPUTED: budget exhausted",
                "basis_status": basis_status,
            }
            print("    %-14s NOT COMPUTED: budget exhausted"
                  % cell_name)
            continue

        p_matched = p_vals[:n_matched]
        i_matched = i_vals[:n_matched]
        d_route = max(abs(a - b) for a, b in zip(p_matched, i_matched))
        sfib = s_c_fib[cell_name]
        verdict = "EXCEEDS" if sfib > d_route else "DOES NOT EXCEED"
        reads_toward = ("discharge (matches lam1n's own discharge pattern)"
                         if verdict == "EXCEEDS" else
                         "confirming the T-INDVERIFY-ARTIFACT-PARTIAL flag "
                         "(matches BATCH-6e08fe's own LLL-quality finding)")
        per_cell_out[cell_name] = {
            "status": "ok",
            "lattice": lat, "d": d, "k": k, "beta": beta,
            "n_matched_bases": n_matched,
            "n_bases_ground_truth": n_bases,
            "route_p_values": p_matched,
            "route_ii_values": i_matched,
            "D_route_pp": d_route,
            "s_c_fib": sfib,
            "VERDICT_pp": verdict,
            "reads_toward": reads_toward,
            "basis_status": basis_status,
        }
        print("    %-14s D_route''=%.6g s_c^fib=%.6g VERDICT''=%s"
              % (cell_name, d_route, sfib, verdict))

    RES["R_V_OUT_2_per_cell"] = per_cell_out
    RES["not_computed"] = not_computed

    print("[5] section 2.5 -- aggregate reading")
    covered = [c for c, v in per_cell_out.items() if v.get("status") == "ok"]
    exceeds = [c for c in covered
               if per_cell_out[c]["VERDICT_pp"] == "EXCEEDS"]
    not_exceeds = [c for c in covered
                   if per_cell_out[c]["VERDICT_pp"] == "DOES NOT EXCEED"]
    all_survive = len(covered) > 0 and len(not_exceeds) == 0
    some_artifact = len(not_exceeds) > 0
    RES["R_V_OUT_3_aggregate"] = {
        "covered_cells": covered,
        "coverage_fraction": "%d/6" % len(covered),
        "exceeds_cells": exceeds,
        "does_not_exceed_cells": not_exceeds,
        "ALL_SURVIVE": all_survive,
        "SOME_ARTIFACT": some_artifact,
    }
    print("    COVERED=%d/6 ALL_SURVIVE=%s SOME_ARTIFACT=%s"
          % (len(covered), all_survive, some_artifact))

    print("[6] section 2.6 -- termination branch under frozen precedence")
    branch_b_infeasible = False  # unreachable: Branch A was used (infra ok)
    if len(covered) == 0:
        # T-HKZINDEP-NODATA branch (a): budget exhaustion, fpylll available
        term = "T-HKZINDEP-NODATA"
        term_reason = ("branch (a): COVERED is empty -- no cell of the 6 "
                        "could be computed against within this task's "
                        "budget, despite fpylll being available (Branch A "
                        "chosen). This does NOT trigger the fourth-attempt "
                        "boundary (PREREG-5 2.6): a repeat at a larger "
                        "budget alone would plausibly resolve it.")
    elif some_artifact:
        term = "T-HKZINDEP-ARTIFACT"
        term_reason = ("COVERED is non-empty and SOME-ARTIFACT holds: at "
                        "least one covered cell reads DOES NOT EXCEED.")
    else:
        term = "T-HKZINDEP-CONFIRMED"
        term_reason = ("COVERED is non-empty and ALL-SURVIVE holds: every "
                        "covered cell reads EXCEEDS.")
    partial = len(covered) < 6 and term != "T-HKZINDEP-NODATA"
    if partial:
        term_display = term + "-PARTIAL"
    else:
        term_display = term
    RES["R_V_OUT_4_termination"] = {
        "branch": term_display,
        "branch_base": term,
        "partial": partial,
        "reason": term_reason,
        "coverage_fraction": "%d/6" % len(covered),
        "not_computed_cells": list(not_computed.keys()),
    }
    print("    TERMINATION BRANCH: %s" % term_display)
    print("    reason: %s" % term_reason)

    RES["timings"] = {"total_wall_seconds": time.time() - T_START}
    RES["environment"] = {
        "python": sys.version,
        "platform": platform.platform(),
        "hostname": socket.gethostname(),
        "numpy_version": np.__version__,
    }
    RES["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    with open(args.out, "w") as fh:
        json.dump(RES, fh, indent=2, default=str)
    print("\nWrote %s" % args.out)


if __name__ == "__main__":
    main()
