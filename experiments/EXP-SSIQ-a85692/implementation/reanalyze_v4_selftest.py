#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXP-SSIQ-a85692 v4 (specification_v4.yaml) -- STAND-ALONE SYNTHETIC
SELF-TEST of c_null_label_comparison_v3 (GD-9's fix, UNCHANGED, imported
below from reanalyze_v3.py, never reimplemented). Fixes GD-10
(RT-BATCH-006.md Front 1, Objection 1): v3's own run_synthetic_self_test_v3
never called c_null_label_comparison_v3 at all -- it called
dht.ols_loglog_fit/dht.bootstrap_gap_ci directly and duplicated the
comparison rule by hand, bypassing c_null_label_comparison_v3's own
cross-dict indexing, min-primes gate, and sorted() ordering step entirely.

THIS FILE IS A NEW, STAND-ALONE ENTRY POINT (PF-3's fix, per
specification_v4.yaml required_artifacts_note). Its argparse interface has
NO --run-b flag, and NO other flag naming a file to read as a real-data
source -- it STRUCTURALLY CANNOT accept or open
RUN-SSIQ-a85692-b/raw-result.json. reanalyze_v3.py's own main() (which DOES
require --run-b and unconditionally json.load's it) is never called from
here; only c_null_label_comparison_v3 itself, NULL_ARM_MIN_PRIMES, SEEDS,
and git_state are imported from that module, BY REFERENCE, unchanged.
Importing reanalyze_v3 as a module executes only its own module-level
imports (compute_delta_e, descent_hitting_time) and constant/function
definitions -- no file read occurs at import time (confirmed identically by
RUN-SSIQ-a85692-c's own source_access_log.yaml, which found the same import
chain performs no file I/O). reanalyze_v3.main() is DEFINED by that import
but is never CALLED anywhere in this file.

PERFORMS NO delta_E SEARCH, NO Phi_ell VERIFICATION, NO GRAPH CONSTRUCTION,
NO PHASE -1 EXECUTION, AND READS NO RUN'S raw-result.json OF ANY KIND. Every
number below is a hand-constructed synthetic dict literal, never sourced
from RUN-SSIQ-a85692-a, -b, or -c.

REQUIRED_ARTIFACTS_NOTE DIFF LIST, AS IMPLEMENTED HERE (cross-checked
against specification_v4.yaml's own required_artifacts_note in this run's
execution_report.yaml -- report any discrepancy there, per the spec's own
instruction, rather than silently reconciling it):
  CHANGED: run_synthetic_self_test_v3 (reanalyze_v3.py) is REPLACED, for
    this run's purposes, by run_synthetic_self_test_v4 (THIS file) -- the
    old function's body is not reused; the new one calls
    c_null_label_comparison_v3 directly, through three checks (CHECK 1:
    null_survivors length 2, NOT-EVALUABLE branch; CHECK 2: length 4,
    UNSORTED, fit-and-bootstrap branch; CHECK 3: length exactly
    NULL_ARM_MIN_PRIMES=3, the boundary, fit-and-bootstrap branch, PF-1's
    fix).
  NEW (this file): the entry-point mechanism itself (PF-3's fix) -- a
    separate script, reanalyze_v4_selftest.py, whose main()/argparse
    interface has no --run-b flag or any other real-data file path flag.
  UNCHANGED, IMPORTED BY REFERENCE, NOT MODIFIED:
    c_null_label_comparison_v3, NULL_ARM_MIN_PRIMES, SEEDS, git_state (all
    from reanalyze_v3.py, defined at v3/GD-9, untouched by this amendment).
  UNCHANGED, NOT INVOKED AT ALL: reanalyze_v3.main() (requires --run-b,
    reads RUN-SSIQ-a85692-b's raw-result.json -- never called here);
    trapped_exclusion_filter_v3 (imported transitively via `import
    reanalyze_v3 as rv3` but never called by this file -- the synthetic
    null_survivors lists below are hand-constructed literals, never
    derived by running the filter); compute_delta_e_v2.py's
    search/admission/Phase -1 machinery (not imported, not invoked,
    identical to reanalyze_v3.py's own diff list).
"""

import argparse
import json
import platform
import sys
import time
import os

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS_DIR)

# Imports c_null_label_comparison_v3 UNCHANGED, BY REFERENCE -- the function
# under test, not reimplemented anywhere in this file. reanalyze_v3.main()
# (the function that reads --run-b) is DEFINED by this import but never
# CALLED anywhere below.
import reanalyze_v3 as rv3   # noqa: E402

EXPERIMENT_ID = "EXP-SSIQ-a85692"
RUN_ID = "RUN-SSIQ-a85692-d"
SPEC_VERSION = 4
SEEDS = rv3.SEEDS                              # [20260805, 11, 977] -- FROZEN, reused by reference
NULL_ARM_MIN_PRIMES = rv3.NULL_ARM_MIN_PRIMES  # 3, reused by reference, not redefined
TOL = 1e-9


# ==========================================================================
# Shared synthetic construction for CHECK 2 and CHECK 3, per the frozen
# spec's own text ("CHECK 3 ... construct synthetic real_per_prime/
# null_per_prime as in CHECK 2"). Two exact power laws in N, zero noise, so
# ols_loglog_fit/bootstrap_gap_ci's outputs are hand-checkable to
# floating-point precision. real_per_prime carries an "N" key per prime
# (matching descent_metrics.per_prime's real schema); null_per_prime does
# NOT carry an "N" key (matching c_null_label.per_prime's real schema
# EXACTLY -- confirmed directly against
# RUN-SSIQ-a85692-b/raw-result.json's c_null_label.per_prime block, see
# source_access_log.yaml -- this is what forces a swapped-dict-source bug,
# e.g. reading N from null_per_prime instead of real_per_prime, to raise
# KeyError rather than silently succeed).
# ==========================================================================

_CHECK23_PRIMES = [2000, 3000, 5000, 7000]
_CHECK23_N_MAP = {2000: 200, 3000: 300, 5000: 500, 7000: 700}
_CHECK23_GAMMA_GREEDY_SYNTH = 0.3
_CHECK23_GAMMA_RANDOM_SYNTH = 0.8


def _build_check23_dicts():
    real_per_prime = {p: {"N": _CHECK23_N_MAP[p]} for p in _CHECK23_PRIMES}
    null_per_prime = {
        p: {
            "greedy_median": float(_CHECK23_N_MAP[p]) ** _CHECK23_GAMMA_GREEDY_SYNTH,
            "random_median": float(_CHECK23_N_MAP[p]) ** _CHECK23_GAMMA_RANDOM_SYNTH,
        }
        for p in _CHECK23_PRIMES
    }
    return real_per_prime, null_per_prime


def _run_check1(rng_seed, n_boot):
    """CHECK 1 (NOT-EVALUABLE branch): null_survivors length 2, below
    NULL_ARM_MIN_PRIMES=3. Assert the function's OWN return value shows
    evaluable=False and c_null_label_control_failure=="NOT-EVALUABLE" -- via
    the function's own return value, not a hand-computed prediction."""
    real_per_prime = {2000: {"N": 200}, 3000: {"N": 300},
                       5000: {"N": 500}, 7000: {"N": 700}}
    null_per_prime = {
        2000: {"greedy_median": 10.0, "random_median": 17.0},
        3000: {"greedy_median": 11.0, "random_median": 19.0},
        5000: {"greedy_median": 12.0, "random_median": 21.0},
        7000: {"greedy_median": 13.0, "random_median": 23.0},
    }
    null_survivors = [2000, 3000]   # length 2, < NULL_ARM_MIN_PRIMES=3

    ret = rv3.c_null_label_comparison_v3(
        real_per_prime, null_per_prime, null_survivors, rng_seed,
        min_primes=NULL_ARM_MIN_PRIMES, n_boot=n_boot)

    assertions = {
        "evaluable_is_False": ret["evaluable"] is False,
        "c_null_label_control_failure_is_NOT_EVALUABLE":
            ret["c_null_label_control_failure"] == "NOT-EVALUABLE",
    }
    check_pass = all(assertions.values())

    return {
        "description": (
            "CHECK 1: null_survivors length 2 (< NULL_ARM_MIN_PRIMES=3). "
            "Calls c_null_label_comparison_v3 directly and asserts on the "
            "function's own returned evaluable/c_null_label_control_failure "
            "fields."
        ),
        "inputs": {
            "real_per_prime": real_per_prime,
            "null_per_prime": null_per_prime,
            "null_survivors": null_survivors,
            "rng_seed": rng_seed,
            "min_primes": NULL_ARM_MIN_PRIMES,
            "n_boot": n_boot,
        },
        "function_return": ret,
        "assertions": assertions,
        "pass": check_pass,
    }


def _run_check2(rng_seed, n_boot):
    """CHECK 2 (fit-and-bootstrap branch): null_survivors length 4, UNSORTED
    order, two exact power laws in N with known
    gamma_greedy_synth/gamma_random_synth. Assert (i) the function's own
    internal sort produces the correct ascending N_list/primes_used -- the
    ONLY assertion that catches a missing/wrong sort (PF-2, non-redundant
    with (ii)-(iv) for this deliberately noiseless construction, per the
    frozen spec's own text) -- and (ii)-(iv) gamma_null_greedy/
    gamma_null_random/m_gap_null_ci_lo/m_gap_null_ci_hi/
    c_null_label_control_failure all match the known analytic values to
    <1e-9 tolerance."""
    real_per_prime, null_per_prime = _build_check23_dicts()
    null_survivors = [7000, 2000, 5000, 3000]   # length 4, deliberately UNSORTED

    ret = rv3.c_null_label_comparison_v3(
        real_per_prime, null_per_prime, null_survivors, rng_seed,
        min_primes=NULL_ARM_MIN_PRIMES, n_boot=n_boot)

    expected_primes_used = sorted(null_survivors)
    expected_N_list = [_CHECK23_N_MAP[p] for p in expected_primes_used]
    expected_m_gap = _CHECK23_GAMMA_RANDOM_SYNTH - _CHECK23_GAMMA_GREEDY_SYNTH

    assertions = {
        "evaluable_is_True": ret["evaluable"] is True,
        # (i) LOAD-BEARING for a missing/wrong sorted() defect specifically
        # (PF-2): this is the ONLY assertion below that is sensitive to
        # sort order for this exact-power-law construction, per the frozen
        # spec's own text -- (ii)-(iv) are analytically invariant to point
        # order for a noiseless power law, and must not be treated as
        # redundant with this one.
        "primes_used_ascending_i": ret["primes_used"] == expected_primes_used,
        "N_list_ascending_i": ret["N_list"] == expected_N_list,
        "gamma_null_greedy_matches_tol_1e-9_ii":
            abs(ret["gamma_null_greedy"] - _CHECK23_GAMMA_GREEDY_SYNTH) < TOL,
        "gamma_null_random_matches_tol_1e-9_ii":
            abs(ret["gamma_null_random"] - _CHECK23_GAMMA_RANDOM_SYNTH) < TOL,
        "m_gap_null_ci_lo_matches_tol_1e-9_iii":
            abs(ret["m_gap_null_ci_lo"] - expected_m_gap) < TOL,
        "m_gap_null_ci_hi_matches_tol_1e-9_iii":
            abs(ret["m_gap_null_ci_hi"] - expected_m_gap) < TOL,
        "c_null_label_control_failure_is_True_iv":
            ret["c_null_label_control_failure"] is True,
    }
    check_pass = all(assertions.values())

    return {
        "description": (
            "CHECK 2: null_survivors length 4, UNSORTED order "
            "[7000, 2000, 5000, 3000], two exact power laws in N with "
            "gamma_greedy_synth=%s / gamma_random_synth=%s. Assertion (i) "
            "(ascending primes_used/N_list) is the sole discriminator for a "
            "missing/wrong sorted() step (PF-2); (ii)-(iv) check the "
            "numeric fit/CI/control-failure fields against the known "
            "analytic values."
            % (_CHECK23_GAMMA_GREEDY_SYNTH, _CHECK23_GAMMA_RANDOM_SYNTH)
        ),
        "inputs": {
            "real_per_prime": real_per_prime,
            "null_per_prime": null_per_prime,
            "null_survivors": null_survivors,
            "rng_seed": rng_seed,
            "min_primes": NULL_ARM_MIN_PRIMES,
            "n_boot": n_boot,
            "gamma_greedy_synth": _CHECK23_GAMMA_GREEDY_SYNTH,
            "gamma_random_synth": _CHECK23_GAMMA_RANDOM_SYNTH,
        },
        "expected_analytic": {
            "primes_used": expected_primes_used,
            "N_list": expected_N_list,
            "gamma_null_greedy": _CHECK23_GAMMA_GREEDY_SYNTH,
            "gamma_null_random": _CHECK23_GAMMA_RANDOM_SYNTH,
            "m_gap_null_ci_lo": expected_m_gap,
            "m_gap_null_ci_hi": expected_m_gap,
            "c_null_label_control_failure": True,
        },
        "function_return": ret,
        "assertions": assertions,
        "pass": check_pass,
    }


def _run_check3(rng_seed, n_boot):
    """CHECK 3 (NEW, PF-1's fix, BLOCKING): null_survivors length EXACTLY
    NULL_ARM_MIN_PRIMES=3 (the boundary itself, not one above or below).
    Distinguishes a correct `len(null_survivors) < min_primes` gate from an
    off-by-one mutant (`<= min_primes`) -- neither CHECK 1 (length 2) nor
    CHECK 2 (length 4) constructs this boundary length, so this check exists
    specifically to close that gap. Assert evaluable=True and the same
    numeric checks as CHECK 2."""
    real_per_prime, null_per_prime = _build_check23_dicts()
    # length EXACTLY 3, unsorted subset of the 4 CHECK-2 primes, EXCLUDING
    # prime 5000 (N=500) specifically: a floating-point precision artifact
    # in the frozen, unchanged dht.ols_loglog_fit (sxx computed as sum((x -
    # xbar)**2 ...) with xbar = sum(xs)/n does not round-trip to bit-exact
    # 0.0 for the specific triple log(500.0)*3/3 at n=3, though it does for
    # every other (N, n) pair used anywhere in this self-test -- confirmed
    # directly by brute-force enumeration of all 27 length-3 index-resample
    # patterns over {200,300,500,700} before freeze of this run's own
    # construction) so ols_loglog_fit's own `sxx == 0.0` degeneracy guard
    # silently fails to fire for the all-N=500 resample, producing a
    # spurious non-degenerate fit instead of the correctly-raised
    # ValueError bootstrap_gap_ci expects to catch and skip. This is a
    # pre-existing numerical property of the UNCHANGED, imported-by-reference
    # dht.ols_loglog_fit -- not a defect in c_null_label_comparison_v3 (the
    # function under test) or in this self-test's construction of it -- and
    # is avoided here by choosing the length-3 subset {2000, 3000, 7000}
    # (N in {200, 300, 700}), verified by the same brute-force enumeration
    # to have zero anomalous resamples across all 27 index patterns.
    null_survivors = [7000, 2000, 3000]

    ret = rv3.c_null_label_comparison_v3(
        real_per_prime, null_per_prime, null_survivors, rng_seed,
        min_primes=NULL_ARM_MIN_PRIMES, n_boot=n_boot)

    expected_primes_used = sorted(null_survivors)
    expected_N_list = [_CHECK23_N_MAP[p] for p in expected_primes_used]
    expected_m_gap = _CHECK23_GAMMA_RANDOM_SYNTH - _CHECK23_GAMMA_GREEDY_SYNTH

    assertions = {
        # REQUIRED per specification_v4.yaml synthetic_self_test_v4 CHECK 3
        # text ("Assert evaluable is True and (ii)-(iv)'s same checks as
        # CHECK 2, at this boundary length specifically"):
        "evaluable_is_True": ret["evaluable"] is True,
        "gamma_null_greedy_matches_tol_1e-9_ii":
            abs(ret["gamma_null_greedy"] - _CHECK23_GAMMA_GREEDY_SYNTH) < TOL,
        "gamma_null_random_matches_tol_1e-9_ii":
            abs(ret["gamma_null_random"] - _CHECK23_GAMMA_RANDOM_SYNTH) < TOL,
        "m_gap_null_ci_lo_matches_tol_1e-9_iii":
            abs(ret["m_gap_null_ci_lo"] - expected_m_gap) < TOL,
        "m_gap_null_ci_hi_matches_tol_1e-9_iii":
            abs(ret["m_gap_null_ci_hi"] - expected_m_gap) < TOL,
        "c_null_label_control_failure_is_True_iv":
            ret["c_null_label_control_failure"] is True,
        # NOT required by the frozen spec's CHECK 3 text (only "(ii)-(iv)"
        # is named for CHECK 3, unlike CHECK 2 where (i) is explicitly
        # required) -- recorded as EXTRA, INFORMATIONAL, non-gating context
        # only, per the spec's own instruction to implement precisely what
        # is specified, not approximate or silently expand it.
        "EXTRA_INFORMATIONAL_primes_used_ascending":
            ret["primes_used"] == expected_primes_used,
        "EXTRA_INFORMATIONAL_N_list_ascending":
            ret["N_list"] == expected_N_list,
    }
    required_keys = [k for k in assertions if not k.startswith("EXTRA_INFORMATIONAL")]
    check_pass = all(assertions[k] for k in required_keys)

    return {
        "description": (
            "CHECK 3 (PF-1 fix, BLOCKING): null_survivors length EXACTLY "
            "NULL_ARM_MIN_PRIMES=3, the boundary itself -- distinguishes a "
            "correct `len(null_survivors) < min_primes` gate from an "
            "off-by-one mutant (`<= min_primes`), which CHECK 1 (length 2) "
            "and CHECK 2 (length 4) both fail to distinguish. Required "
            "assertions per specification_v4.yaml: evaluable is True, and "
            "(ii)-(iv) as in CHECK 2. The ascending-order assertions are "
            "recorded as extra/informational only -- not required by the "
            "frozen spec's CHECK 3 text and not part of check_pass's gate."
        ),
        "inputs": {
            "real_per_prime": real_per_prime,
            "null_per_prime": null_per_prime,
            "null_survivors": null_survivors,
            "rng_seed": rng_seed,
            "min_primes": NULL_ARM_MIN_PRIMES,
            "n_boot": n_boot,
            "gamma_greedy_synth": _CHECK23_GAMMA_GREEDY_SYNTH,
            "gamma_random_synth": _CHECK23_GAMMA_RANDOM_SYNTH,
        },
        "expected_analytic": {
            "primes_used": expected_primes_used,
            "N_list": expected_N_list,
            "gamma_null_greedy": _CHECK23_GAMMA_GREEDY_SYNTH,
            "gamma_null_random": _CHECK23_GAMMA_RANDOM_SYNTH,
            "m_gap_null_ci_lo": expected_m_gap,
            "m_gap_null_ci_hi": expected_m_gap,
            "c_null_label_control_failure": True,
        },
        "function_return": ret,
        "assertions": assertions,
        "required_assertion_keys": required_keys,
        "pass": check_pass,
        "boundary_note": (
            "Symmetric with how CHECK 1 already tests the boundary from "
            "below (length 2, one below NULL_ARM_MIN_PRIMES=3). Under the "
            "correct gate (`len(null_survivors) < min_primes`), 3 < 3 is "
            "False, so this proceeds to the fit-and-bootstrap branch "
            "(evaluable=True). Under the off-by-one mutant "
            "(`len(null_survivors) <= min_primes`), 3 <= 3 is True, so the "
            "mutant would instead return NOT-EVALUABLE here -- the one "
            "length at which the two rules disagree, per "
            "mutation_precondition_v4 and RT-PREFREEZE-EXP-SSIQ-a85692-v4.md "
            "PF-1."
        ),
    }


def run_synthetic_self_test_v4(rng_seed=None, n_boot=2000):
    """spec_v4 inputs.synthetic_self_test_v4. REPLACES
    run_synthetic_self_test_v3. Calls c_null_label_comparison_v3 (imported
    UNCHANGED from reanalyze_v3, never reimplemented anywhere in this file)
    directly, through THREE required checks. Every assertion below reads
    the FUNCTION'S OWN RETURN VALUE, never a hand-computed duplicate of its
    internal cross-dict indexing, min-primes gate, or sorted() step."""
    if rng_seed is None:
        rng_seed = SEEDS[0]

    check1 = _run_check1(rng_seed, n_boot)
    check2 = _run_check2(rng_seed, n_boot)
    check3 = _run_check3(rng_seed, n_boot)

    all_checks_pass = bool(check1["pass"] and check2["pass"] and check3["pass"])

    return {
        "purpose": (
            "GD-10's standing repair, applied to synthetic_self_test_v3's "
            "own defect: this self-test calls c_null_label_comparison_v3 "
            "ITSELF (imported unchanged from reanalyze_v3.py, never "
            "reimplemented), through its NOT-EVALUABLE branch (CHECK 1), "
            "its fit-and-bootstrap branch with unsorted input (CHECK 2), "
            "and the exact NULL_ARM_MIN_PRIMES boundary (CHECK 3, PF-1's "
            "fix) -- exercising the function's own cross-dict indexing, "
            "min-primes gate, and sorted() ordering step, none of which "
            "v3's self-test ever touched."
        ),
        "function_under_test": (
            "c_null_label_comparison_v3, defined in "
            "experiments/EXP-SSIQ-a85692/implementation/reanalyze_v3.py "
            "lines 141-216 (UNCHANGED by this amendment), imported here as "
            "`rv3.c_null_label_comparison_v3` and called directly in all "
            "three checks below -- no duplicate, hand-written "
            "re-implementation of its internal logic anywhere in this file."
        ),
        "independent_of_real_data": True,
        "data_source": (
            "hand-constructed synthetic dict literals, NOT sourced from "
            "RUN-SSIQ-a85692-a, RUN-SSIQ-a85692-b, or RUN-SSIQ-a85692-c, or "
            "any prior run's raw-result.json."
        ),
        "check1": check1,
        "check2": check2,
        "check3": check3,
        "all_checks_pass": all_checks_pass,
        "self_test_verdict": (
            "PASS -- all three required checks confirm c_null_label_comparison_v3's "
            "own return value matches the frozen spec's stated expectations "
            "(NOT-EVALUABLE branch, unsorted-input fit-and-bootstrap branch "
            "with correct ascending re-sort, and the exact min-primes "
            "boundary), reading the function's own output throughout."
            if all_checks_pass else
            "FAIL -- see check1/check2/check3.assertions above for the "
            "specific mismatch(es); this would indicate a defect in "
            "c_null_label_comparison_v3 or in how this self-test invokes "
            "it, and would need investigation before any future run relying "
            "on that function could be trusted."
        ),
    }


# ==========================================================================
# main() -- STAND-ALONE entry point. NO --run-b FLAG. NO OTHER FLAG NAMES A
# FILE TO READ AS A REAL-DATA SOURCE. STRUCTURALLY CANNOT read
# RUN-SSIQ-a85692-b's raw-result.json (PF-3's fix).
# ==========================================================================

def main():
    ap = argparse.ArgumentParser(
        description=(
            "EXP-SSIQ-a85692 v4 stand-alone synthetic self-test of "
            "c_null_label_comparison_v3. This parser has NO --run-b flag "
            "and NO other flag naming a file to read as a real-data "
            "source -- it structurally cannot open "
            "RUN-SSIQ-a85692-b/raw-result.json or any other prior run's "
            "raw-result.json."
        ))
    ap.add_argument("--out", required=True,
                     help="output path for RUN-SSIQ-a85692-d/raw-result.json")
    ap.add_argument("--self-test-out", required=True,
                     help="output path for RUN-SSIQ-a85692-d/self_test_v4.json")
    args = ap.parse_args()

    t_start = time.time()

    self_test = run_synthetic_self_test_v4(rng_seed=SEEDS[0])

    with open(args.self_test_out, "w") as f:
        json.dump(self_test, f, indent=2, sort_keys=True)

    wall_seconds = time.time() - t_start

    payload = {
        "experiment_id": EXPERIMENT_ID,
        "run_id": RUN_ID,
        "spec_version": SPEC_VERSION,
        "amends": (
            "specification_v3.yaml (frozen 7f40426b041044b9074f8bf208971786bde83801), "
            "ONE POINT (GD-10's fix): replaces run_synthetic_self_test_v3 "
            "(reanalyze_v3.py) with run_synthetic_self_test_v4 (this file), "
            "which calls c_null_label_comparison_v3 itself instead of "
            "duplicating its logic by hand."
        ),
        "real_data_source": (
            "NONE. This run reads no prior run's raw-result.json of any "
            "kind: this script's argparse interface has no --run-b flag or "
            "any other file-path flag naming a real-data source (see "
            "source_access_log.yaml, routes_tried_and_their_outcomes)."
        ),
        "self_test_v4_source": (
            "hand-constructed synthetic dict literals, computed entirely "
            "in this process; see runs/RUN-SSIQ-a85692-d/self_test_v4.json "
            "for the full per-check record (inputs, the function's own "
            "return values, expected analytic values, and assertion-level "
            "pass/fail), written as a DISTINCT artifact, never conflated "
            "with this file."
        ),
        "self_test_v4_summary": {
            "check1_not_evaluable_pass": self_test["check1"]["pass"],
            "check2_fit_and_bootstrap_unsorted_length4_pass": self_test["check2"]["pass"],
            "check3_boundary_length3_pass": self_test["check3"]["pass"],
            "all_checks_pass": self_test["all_checks_pass"],
        },
        "wall_clock_seconds": wall_seconds,
        "git": rv3.git_state(),
        "python": sys.version,
        "platform": platform.platform(),
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t_start)),
        "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "certificate": {
            "kind": "none",
            "verified": None,
            "verifier": None,
            "reason": (
                "Pure synthetic self-test of an existing comparison "
                "function's cross-dict indexing, gate, and sort logic. No "
                "discrete log is claimed, no factor-base relation is "
                "claimed, no isogeny problem instance is solved. "
                "docs/claims-and-verification.md requires kind: none to be "
                "stated explicitly for such runs."
            ),
        },
    }

    with open(args.out, "w") as f:
        json.dump(payload, f, indent=2, sort_keys=True)

    print("synthetic_self_test_v4: check1(NOT-EVALUABLE)=%s check2(unsorted,len4)=%s "
          "check3(boundary,len3)=%s all_checks_pass=%s"
          % (self_test["check1"]["pass"], self_test["check2"]["pass"],
             self_test["check3"]["pass"], self_test["all_checks_pass"]))
    print("wall_clock_seconds=%.6f" % wall_seconds)


if __name__ == "__main__":
    main()
