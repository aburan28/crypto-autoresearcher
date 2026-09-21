#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TASK-20260813-630414 / BATCH-8d09f5 / GOAL-MLKEM-005 -- THE LEAD PRODUCER

Governed by PREREG-6:
  coordination/goals/GOAL-MLKEM-005/batches/BATCH-8d09f5/tasks/
      TASK-20260813-4aec9a/prereg.md
  notarized in commit dcaac725f65da93c0ab27eeed970d6d10b2bcde1

CLAIM TIER: TOY, UNCONDITIONALLY. Nothing this script computes bears on
ML-KEM security, any FIPS 203 parameter set, any attack cost, or any cost
model.

certificate.kind: none -- no discrete-log solve and no factor-base relation
is claimed or produced anywhere in this script. This is a mutation-testing
(positive) control on the D_route/D_route'' comparison MECHANISM itself,
never a certificate.

THIS IS NOT A FOURTH ROUTE-COMPARISON ATTEMPT (PREREG-6 section 0). It is a
mutation test with a known, injected ground truth: a byte-for-byte copy of
measure_hkz_indep.py's four ROUTE-I''-building functions
(route_ii_make_A, route_ii_build_basis, hkz_route_ii, route_ii_hkz_value),
renamed with a `_mut` suffix, with EXACTLY ONE functional line changed in
the copy of route_ii_make_A (PREREG-6 section 2.2): the seed-formula index
argument `i` changed to `(i + 1) % n_bases`.

measure_hkz_indep.py itself is FROZEN, READ ONLY, and is never imported from
by this script -- only read as text (for the mechanical diff in step 3) via
a plain file read, never `import`.

WHAT THIS SCRIPT DOES, IN ORDER (PREREG-6 section headers cited in comments)
  (1) section 1 -- independently re-verifies fpylll/cysignals availability
      in THIS session (infrastructure re-verification, fresh).
  (2) section 2.4 point 1 -- obligation 1 point 1: independently recomputes
      section 2.3's frozen prediction directly from results_relvar.json's
      own per-basis arrays, and reports whether it matches PREREG-6's
      stated numbers.
  (3) section 2.2 / 2.4 point 2 -- builds ROUTE-MUT (this script's own
      `_mut`-suffixed functions) and emits a literal, machine-generated
      unified diff between measure_hkz_indep.py's four source functions
      (extracted from the frozen file's own text via the `ast` module, a
      read-only operation) and this script's own `_mut` functions'
      source (obtained via `inspect.getsource`), so a reviewer can confirm
      mechanically that exactly one functional line differs (plus the
      cosmetic `_mut` renames, named as such).
  (4) section 2.4 points 3-6 -- obligation 1: computes ROUTE-MUT's hkz
      value at every matched basis (up to 8) for the 2 named cells only
      (hkz/L7_b5, hkz/L11_b30), computes D_route_mut/VERDICT_mut per
      PREREG-3 3.3's own formula verbatim, and states the detected /
      not-detected reading per section 2.4 point 5.
  (5) section 2.5 -- obligation 2: the aggregate DETECTED_SET /
      NOT_DETECTED_SET reading and coverage fraction.
  (6) section 2.6 -- reads off the termination branch (fresh 4-branch
      clause: T-MUTCTRL-NODATA / -DETECTED / -NOT-DETECTED / -MIXED, with
      -PARTIAL suffix as required) under the frozen precedence.

BOUNDED: NO REDUCTION ABOVE d = 40, ANYWHERE, FOR ANY REASON. Only the two
named cells (hkz/L7_b5 d=20, hkz/L11_b30 d=40) are attempted. Hard
wall-clock budget for this task is 3600 s (task card); this script enforces
an internal compute deadline (COMPUTE_DEADLINE_SECONDS, set below the
task's own budget) so report-writing always completes even if reduction is
budget-bound; any basis not reached within budget is reported as
"NOT COMPUTED: budget exhausted" (PREREG-5 3.2, carried), never defaulted
to either verdict.

This script writes exactly one JSON file: results_hkz_mutation6.json,
inside its own task directory. It performs no git write and makes no
commit.
"""

import argparse
import ast
import difflib
import hashlib
import inspect
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

COMPUTE_DEADLINE_SECONDS = 2600.0   # well under the 3600 s task hard cap
PER_CELL_DEADLINE_SECONDS = 500.0   # soft per-cell guard inside the budget

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

# FROZEN, READ-ONLY reference file. Never imported from, never edited.
FROZEN_REFERENCE_PATH = os.path.join(
    REPO_ROOT, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/"
    "tasks/TASK-20260813-c0ec71/measure_hkz_indep.py")
FROZEN_REFERENCE_COMMIT = "3d3f5fde552f1a4783616a624f602917719701e8"

PREREG6_PATH = os.path.join(
    REPO_ROOT, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-8d09f5/"
    "tasks/TASK-20260813-4aec9a/prereg.md")
PREREG6_NOTARIZING_COMMIT = "dcaac725f65da93c0ab27eeed970d6d10b2bcde1"

Q_MAIN = 3329
N_BASES = 8
# The 2 named cells this document covers (PREREG-6 2.1), ONLY these two.
CELLS = OrderedDict([
    ("hkz/L7_b5",   dict(lat="L7", d=20, k=6,  beta=5)),
    ("hkz/L11_b30", dict(lat="L11", d=40, k=12, beta=30)),
])


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
         PREREG6_NOTARIZING_COMMIT, "HEAD"],
        cwd=REPO_ROOT) == 0
    return {"commit": sha, "dirty": dirty,
            "notarizing_commit": PREREG6_NOTARIZING_COMMIT,
            "is_ancestor_of_HEAD": is_anc}


# ==================================================== section 1: infra check
def infra_recheck():
    """Independently re-verify fpylll/cysignals availability in THIS
    session, exactly as PREREG-6 section 1 (restating PREREG-5 section 1)
    requires as the lead's first act. Reports plainly, either way, as
    infrastructure signal only. If fpylll is unavailable, this fires
    T-MUTCTRL-NODATA branch (b) directly -- no Branch-B contingency is
    commissioned by PREREG-6."""
    out = {"attempted": True}
    try:
        import fpylll  # noqa: F401
        import cysignals  # noqa: F401
        from fpylll import IntegerMatrix, LLL, BKZ, GSO, Enumeration  # noqa
        from fpylll.fplll.bkz import BKZReduction  # noqa: F401
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
            "cysignals_version": getattr(cysignals, "__version__", "unknown"),
            "imports_ok": True,
            "smoke_test": "basic LLL reduction of an 8x8 random integer "
                           "matrix completed",
            "smoke_test_first_row_after_lll": first_row,
            "branch_chosen": "A",
            "branch_reason": (
                "fpylll and cysignals import and run correctly in this "
                "task's own re-verification, independently performed fresh "
                "in this session as PREREG-6 section 1 requires. Branch A "
                "(fpylll's own public API) is used per PREREG-6 section 1, "
                "reusing the licensed, already-reviewed reduction/"
                "enumeration shape of measure_hkz_indep.py unmodified "
                "except for the one mutated line in the copied "
                "basis-construction helper (section 2.2)."),
        })
    except Exception as ex:
        out.update({
            "fpylll_available": False,
            "imports_ok": False,
            "error": "%s: %s" % (type(ex).__name__, ex),
            "branch_chosen": None,
            "branch_reason": (
                "fpylll/cysignals import or smoke-test failed in this "
                "task's own re-verification. PREREG-6 section 1 commissions "
                "NO Branch-B contingency for this document; this fires "
                "T-MUTCTRL-NODATA branch (b) directly."),
        })
    return out


# ============================================== step 2: independent recompute
def recompute_frozen_prediction(relvar):
    """PREREG-6 section 2.4 point 1 / obligation 1 point 1: independently
    recompute section 2.3's frozen prediction directly from
    results_relvar.json's own G_REL1.hkz.L7/L11 per-basis arrays (cyclic
    adjacent-basis max-abs-difference at hkz/L7_b5's X_a field and
    hkz/L11_b30's X_b field). Report whether this recomputation matches
    PREREG-6's stated numbers. A mismatch is reported as a finding about
    PREREG-6, never silently corrected or substituted."""
    g = relvar["G_REL1"]["hkz"]

    def cyclic_maxdiff(vals):
        n = len(vals)
        diffs = [abs(vals[i] - vals[(i + 1) % n]) for i in range(n)]
        mx = max(diffs)
        idx = diffs.index(mx)
        return diffs, mx, idx

    Xa = [row["X_a"] for row in g["L7"]["per_basis"]]
    Xb = [row["X_b"] for row in g["L11"]["per_basis"]]
    diffs_a, max_a, idx_a = cyclic_maxdiff(Xa)
    diffs_b, max_b, idx_b = cyclic_maxdiff(Xb)

    prereg6_stated = {
        "hkz/L7_b5": 0.0665893489077094,
        "hkz/L11_b30": 0.00948000985335451,
    }
    own = {
        "hkz/L7_b5": max_a,
        "hkz/L11_b30": max_b,
    }
    match = {
        "hkz/L7_b5": own["hkz/L7_b5"] == prereg6_stated["hkz/L7_b5"],
        "hkz/L11_b30": own["hkz/L11_b30"] == prereg6_stated["hkz/L11_b30"],
    }
    return {
        "hkz/L7_b5": {
            "X_a_values": Xa,
            "cyclic_adjacent_diffs": diffs_a,
            "own_recomputed_max": max_a,
            "own_recomputed_argmax_i": idx_a,
            "prereg6_stated": prereg6_stated["hkz/L7_b5"],
            "matches_prereg6": match["hkz/L7_b5"],
        },
        "hkz/L11_b30": {
            "X_b_values": Xb,
            "cyclic_adjacent_diffs": diffs_b,
            "own_recomputed_max": max_b,
            "own_recomputed_argmax_i": idx_b,
            "prereg6_stated": prereg6_stated["hkz/L11_b30"],
            "matches_prereg6": match["hkz/L11_b30"],
        },
        "all_match": all(match.values()),
    }


# ============================== step 3: mutant functions (ROUTE-MUT)
# Byte-for-byte copy of measure_hkz_indep.py's route_ii_make_A,
# route_ii_build_basis, hkz_route_ii and route_ii_hkz_value, renamed with a
# `_mut` suffix (cosmetic; shown in the diff below), with EXACTLY ONE
# functional line changed, in the copy of route_ii_make_A only
# (PREREG-6 section 2.2): the seed-formula index argument changed from `i`
# to `(i + 1) % n_bases`.

def route_ii_make_A_mut(d, k, q, i, n_bases=N_BASES):
    rng = np.random.default_rng([1, d, k, (i + 1) % n_bases])   # MUTATED
    return rng.integers(0, q, size=(k, d - k), dtype=np.int64)


def route_ii_build_basis_mut(d, k, q, i):
    B = np.zeros((d, d), dtype=np.int64)
    B[:k, :k] = np.eye(k, dtype=np.int64)
    B[:k, k:] = route_ii_make_A_mut(d, k, q, i)
    B[k:, k:] = q * np.eye(d - k, dtype=np.int64)
    return B


def hkz_route_ii_mut(B, d, deadline_ts):
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


def route_ii_hkz_value_mut(r, d, k, beta, q):
    """The hkz observable's own definition (reused identically -- see the
    INDEPENDENCE DECLARATION at the top of this file). r = squared GS
    norms after ROUTE-I''s own reduction/enumeration."""
    logb = 0.5 * np.log(np.maximum(r, 1e-300))
    logdet = (d - k) * math.log(q)
    return float(np.mean(logb[d - beta:]) - logdet / d)


# ================================== step 3b: mechanical diff verification
FROZEN_FUNC_NAMES = ["route_ii_make_A", "route_ii_build_basis",
                      "hkz_route_ii", "route_ii_hkz_value"]
MUT_FUNC_NAMES = ["route_ii_make_A_mut", "route_ii_build_basis_mut",
                  "hkz_route_ii_mut", "route_ii_hkz_value_mut"]


def extract_function_sources(path, names):
    """Read-only extraction (never import) of named top-level function
    definitions' exact source text from a .py file, via the ast module."""
    with open(path, "r") as fh:
        src = fh.read()
    tree = ast.parse(src, filename=path)
    lines = src.splitlines(keepends=True)
    out = OrderedDict()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in names:
            start = node.lineno - 1
            end = node.end_lineno
            out[node.name] = "".join(lines[start:end])
    missing = [n for n in names if n not in out]
    if missing:
        raise SystemExit("ABORT: could not locate functions %s in %s"
                          % (missing, path))
    return out, sha256_file(path)


def build_mechanical_diff():
    frozen_src, frozen_sha256 = extract_function_sources(
        FROZEN_REFERENCE_PATH, FROZEN_FUNC_NAMES)
    mut_funcs = {
        "route_ii_make_A_mut": route_ii_make_A_mut,
        "route_ii_build_basis_mut": route_ii_build_basis_mut,
        "hkz_route_ii_mut": hkz_route_ii_mut,
        "route_ii_hkz_value_mut": route_ii_hkz_value_mut,
    }
    mut_src = OrderedDict(
        (name, inspect.getsource(mut_funcs[name])) for name in MUT_FUNC_NAMES
    )
    frozen_block = "".join(frozen_src[n] + "\n" for n in FROZEN_FUNC_NAMES)
    mut_block = "".join(mut_src[n] + "\n" for n in MUT_FUNC_NAMES)
    diff_lines = list(difflib.unified_diff(
        frozen_block.splitlines(keepends=True),
        mut_block.splitlines(keepends=True),
        fromfile="measure_hkz_indep.py (4 named functions, frozen)",
        tofile="measure_hkz_mutation6.py (4 _mut functions)",
    ))
    # Mechanical count: lines that are genuinely a body-content change
    # (the mutated seed-index line), vs lines that are only a def-line /
    # call-site rename (`_mut` suffix / recursive-call rename), classified
    # by substring content, not by trusting prose.
    added = [ln for ln in diff_lines if ln.startswith("+") and not ln.startswith("+++")]
    removed = [ln for ln in diff_lines if ln.startswith("-") and not ln.startswith("---")]
    functional_changed = [
        (r, a) for r, a in zip(removed, added)
        if "(i + 1) % n_bases" in a or "(i + 1) % n_bases" in r
    ]
    return {
        "frozen_reference_path": os.path.relpath(FROZEN_REFERENCE_PATH, REPO_ROOT),
        "frozen_reference_sha256": frozen_sha256,
        "frozen_reference_commit": FROZEN_REFERENCE_COMMIT,
        "unified_diff": "".join(diff_lines),
        "n_removed_lines": len(removed),
        "n_added_lines": len(added),
        "functional_change_lines": functional_changed,
        "n_functional_change_pairs": len(functional_changed),
    }


# ==================================================== main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TASK_DIR,
                     "results_hkz_mutation6.json"))
    args = ap.parse_args()

    RES = OrderedDict()
    RES["task_id"] = "TASK-20260813-630414"
    RES["batch_id"] = "BATCH-8d09f5"
    RES["goal_id"] = "GOAL-MLKEM-005"
    RES["role"] = "executor"
    RES["claim_tier"] = "TOY"
    RES["certificate"] = {"kind": "none", "reason": (
        "No discrete-log solve and no factor-base relation is claimed or "
        "produced anywhere in this script. This is a mutation-testing "
        "(positive) control on the D_route/D_route'' comparison mechanism "
        "itself, never a certificate.")}
    RES["governed_by"] = {
        "prereg": os.path.relpath(PREREG6_PATH, REPO_ROOT),
        "notarizing_commit": PREREG6_NOTARIZING_COMMIT,
    }
    RES["model_verified"] = False
    RES["model_verified_reason"] = (
        "AGENTS.md rule 12 is unmet and unwaived in this goal (PREREG-6 "
        "section 5, carried from PREREG-5 section 5). This producer's own "
        "model identity is not independently verified.")

    print("[git] recording commit / dirty-tree state")
    RES["git"] = git_state()
    if not RES["git"]["is_ancestor_of_HEAD"]:
        raise SystemExit("ABORT: PREREG-6 notarizing commit is not an "
                          "ancestor of HEAD")

    print("[1] section 1 -- independent fpylll/cysignals re-verification")
    infra = infra_recheck()
    RES["R_MC_OUT_0_infra_recheck"] = infra
    print("    fpylll_available=%s branch_chosen=%s"
          % (infra.get("fpylll_available"), infra.get("branch_chosen")))

    if not infra.get("fpylll_available"):
        RES["TERMINATION"] = {
            "branch": "T-MUTCTRL-NODATA",
            "sub_branch": "(b)",
            "reason": ("fpylll unavailable in this task's own session "
                       "re-verification. PREREG-6 section 1/3.3 commissions "
                       "no Branch-B contingency for this document; this "
                       "fires T-MUTCTRL-NODATA branch (b) directly."),
        }
        with open(args.out, "w") as fh:
            json.dump(RES, fh, indent=2, default=str)
        print("TERMINATION: T-MUTCTRL-NODATA branch (b) -- fpylll "
              "unavailable. See results file.")
        return

    print("[2] obligation 1 point 1 -- independent recomputation of "
          "PREREG-6 section 2.3's frozen prediction")
    if not os.path.isfile(RESULTS_RELVAR_PATH):
        raise SystemExit("ABORT: results_relvar.json not found at %s"
                          % RESULTS_RELVAR_PATH)
    with open(RESULTS_RELVAR_PATH) as fh:
        relvar = json.load(fh)
    RES["results_relvar_sha256"] = sha256_file(RESULTS_RELVAR_PATH)
    RES["results_relvar_path"] = os.path.relpath(RESULTS_RELVAR_PATH,
                                                  REPO_ROOT)
    recomp = recompute_frozen_prediction(relvar)
    RES["R_MC_OUT_0b_prediction_recomputation"] = recomp
    print("    L7_b5   own=%.16g prereg6=%.16g match=%s"
          % (recomp["hkz/L7_b5"]["own_recomputed_max"],
             recomp["hkz/L7_b5"]["prereg6_stated"],
             recomp["hkz/L7_b5"]["matches_prereg6"]))
    print("    L11_b30 own=%.16g prereg6=%.16g match=%s"
          % (recomp["hkz/L11_b30"]["own_recomputed_max"],
             recomp["hkz/L11_b30"]["prereg6_stated"],
             recomp["hkz/L11_b30"]["matches_prereg6"]))

    print("[3] section 2.2/2.4 point 2 -- mechanical diff, mutant vs frozen "
          "source")
    diff_info = build_mechanical_diff()
    RES["R_MC_OUT_1_mechanical_diff"] = diff_info
    print("    frozen reference sha256=%s" % diff_info["frozen_reference_sha256"])
    print("    n_functional_change_pairs=%d (expected: 1)"
          % diff_info["n_functional_change_pairs"])

    g_rel1_hkz = relvar["G_REL1"]["hkz"]
    g_var_hkz = relvar["G_VAR"]["per_candidate"]["hkz"]["per_cell"]

    print("[4] obligation 1 points 3-6 -- ROUTE-MUT computation and "
          "D_route_mut/VERDICT_mut per cell")
    per_cell_out = OrderedDict()
    not_computed = OrderedDict()
    deadline_ts = T_START + COMPUTE_DEADLINE_SECONDS
    reduced_cache = {}  # (lat, i) -> hkz_route_ii_mut() dict

    for cell_name, meta in CELLS.items():
        lat, d, k, beta = meta["lat"], meta["d"], meta["k"], meta["beta"]
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
        p_vals = [row[field] for row in per_basis]
        s_c_fib = g_var_hkz["%s_b%d" % (lat, beta)]["float_sd"]

        i_vals = []
        cell_deadline_ts = min(deadline_ts, time.time() + PER_CELL_DEADLINE_SECONDS
                                * max(1, n_bases))
        basis_status = OrderedDict()
        for i in range(min(n_bases, N_BASES)):
            if time.time() > deadline_ts:
                basis_status[i] = "NOT COMPUTED: budget exhausted"
                continue
            key = (lat, i)
            if key not in reduced_cache:
                B = route_ii_build_basis_mut(d, k, Q_MAIN, i)
                prof = hkz_route_ii_mut(B, d, min(deadline_ts, cell_deadline_ts))
                reduced_cache[key] = prof
            prof = reduced_cache[key]
            if prof.get("status") != "ok":
                basis_status[i] = prof.get("status", "NOT MEASURED")
                continue
            hv = route_ii_hkz_value_mut(prof["r"], d, k, beta, Q_MAIN)
            i_vals.append(hv)
            basis_status[i] = "ok"

        n_matched = min(len(i_vals), len(p_vals))
        if n_matched == 0:
            not_computed[cell_name] = (
                "NOT COMPUTED: budget exhausted (0 of %d bases reduced "
                "within the compute deadline)" % n_bases)
            per_cell_out[cell_name] = {
                "status": "NOT COMPUTED: budget exhausted",
                "field_used": field,
                "s_c_fib": s_c_fib,
                "basis_status": basis_status,
            }
            print("    %-14s NOT COMPUTED: budget exhausted" % cell_name)
            continue

        p_matched = p_vals[:n_matched]
        i_matched = i_vals[:n_matched]
        d_route_mut = max(abs(a - b) for a, b in zip(p_matched, i_matched))
        verdict_mut = ("EXCEEDS" if s_c_fib > d_route_mut
                        else "DOES NOT EXCEED")
        detection = ("DETECTED" if verdict_mut == "DOES NOT EXCEED"
                     else "NOT DETECTED")
        matches_prediction = None
        pred_key = cell_name
        if pred_key in recomp:
            pred_val = recomp[pred_key]["prereg6_stated"]
            matches_prediction = abs(d_route_mut - pred_val) < 1e-6

        per_cell_out[cell_name] = {
            "status": "ok",
            "lattice": lat, "d": d, "k": k, "beta": beta,
            "field_used": field,
            "n_matched_bases": n_matched,
            "n_bases_ground_truth": n_bases,
            "route_p_values": p_matched,
            "route_mut_values": i_matched,
            "D_route_mut": d_route_mut,
            "s_c_fib": s_c_fib,
            "VERDICT_mut": verdict_mut,
            "detection_reading": detection,
            "close_to_frozen_prediction": matches_prediction,
            "basis_status": basis_status,
        }
        print("    %-14s D_route_mut=%.6g s_c^fib=%.6g VERDICT_mut=%s (%s)"
              % (cell_name, d_route_mut, s_c_fib, verdict_mut, detection))

    RES["R_MC_OUT_2_per_cell"] = per_cell_out
    RES["not_computed"] = not_computed

    print("[5] section 2.5 -- obligation 2: aggregate reading")
    covered = [c for c, v in per_cell_out.items() if v.get("status") == "ok"]
    detected_set = [c for c in covered
                    if per_cell_out[c]["VERDICT_mut"] == "DOES NOT EXCEED"]
    not_detected_set = [c for c in covered
                         if per_cell_out[c]["VERDICT_mut"] == "EXCEEDS"]
    RES["R_MC_OUT_3_aggregate"] = {
        "covered_cells": covered,
        "coverage_fraction": "%d/2" % len(covered),
        "DETECTED_SET": detected_set,
        "NOT_DETECTED_SET": not_detected_set,
    }
    print("    COVERED=%d/2 DETECTED_SET=%s NOT_DETECTED_SET=%s"
          % (len(covered), detected_set, not_detected_set))

    print("[6] section 2.6 -- termination branch, fresh 4-branch precedence")
    if len(covered) == 0:
        branch = "T-MUTCTRL-NODATA"
        sub_branch = "(a)"
        reason = ("COVERED is empty -- neither of the 2 named cells could "
                   "be computed against within this task's budget.")
        partial = False
    elif len(covered) == 2 and len(detected_set) == 1 and len(not_detected_set) == 1:
        branch = "T-MUTCTRL-MIXED"
        sub_branch = None
        reason = ("|COVERED| = 2 and the two cells' VERDICT_mut disagree: "
                   "%s detected, %s not detected." % (detected_set, not_detected_set))
        partial = False
    elif len(covered) == 2 and len(detected_set) == 2:
        branch = "T-MUTCTRL-DETECTED"
        sub_branch = None
        reason = "|COVERED| = 2 and both cells' VERDICT_mut = DOES NOT EXCEED."
        partial = False
    elif len(covered) == 2 and len(not_detected_set) == 2:
        branch = "T-MUTCTRL-NOT-DETECTED"
        sub_branch = None
        reason = "|COVERED| = 2 and both cells' VERDICT_mut = EXCEEDS."
        partial = False
    elif len(covered) == 1 and detected_set:
        branch = "T-MUTCTRL-DETECTED"
        sub_branch = None
        reason = ("|COVERED| = 1 (%s); its VERDICT_mut = DOES NOT EXCEED."
                   % covered[0])
        partial = True
    elif len(covered) == 1 and not_detected_set:
        branch = "T-MUTCTRL-NOT-DETECTED"
        sub_branch = None
        reason = ("|COVERED| = 1 (%s); its VERDICT_mut = EXCEEDS."
                   % covered[0])
        partial = True
    else:
        raise SystemExit("ABORT: unreachable termination-branch state; "
                          "covered=%r detected=%r not_detected=%r"
                          % (covered, detected_set, not_detected_set))

    branch_display = branch + ("-PARTIAL" if partial else "")
    RES["R_MC_OUT_4_termination"] = {
        "branch": branch_display,
        "branch_base": branch,
        "sub_branch": sub_branch,
        "partial": partial,
        "reason": reason,
        "coverage_fraction": "%d/2" % len(covered),
        "not_computed_cells": list(not_computed.keys()),
    }
    print("    TERMINATION BRANCH: %s" % branch_display)
    print("    reason: %s" % reason)

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
