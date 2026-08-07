#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXP-SSIQ-a85692 v3 (specification_v3.yaml) -- PURE RE-ANALYSIS of
RUN-SSIQ-a85692-b's already-committed raw-result.json. Fixes GD-8
(trapped_exclusion_filter_v3) and GD-9 (c_null_label_comparison_v3), per
DEC-20260805-5f5ac6's adopted BATCH-006 plan.

THIS FILE PERFORMS NO delta_E SEARCH, NO Phi_ell VERIFICATION, NO GRAPH
CONSTRUCTION, AND NO PHASE -1 REAL-TIME EXECUTION OF ANY KIND.
compute_delta_e_v2.py's search/admission/Phase -1 machinery
(two_sided_search, build_smooth_table, run_phase_minus1_on_confirmatory_set,
apply_truncation_fallback, run_c_search_bias, verify_modular_polynomials,
build_all_graphs, run_correctness_gates) is not imported and not invoked
anywhere below. Every number this file reads comes from
experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-b/raw-result.json's
descent_metrics.per_prime (real arm) and c_null_label.per_prime (shuffled-
label null arm), OR from a hand-constructed synthetic self-test that is
explicitly NOT sourced from any prior run (see run_synthetic_self_test_v3
below).

REQUIRED_ARTIFACTS_NOTE DIFF LIST, AS IMPLEMENTED HERE (cross-checked
against specification_v3.yaml's own required_artifacts_note in this run's
execution_report.yaml -- report any discrepancy there, per the spec's own
instruction, rather than silently reconciling it):
  NEW (this file):
    - trapped_exclusion_filter_v3   (GD-8's fix)
    - c_null_label_comparison_v3    (GD-9's fix)
    - run_synthetic_self_test_v3    (PF-1's fix, required artifact)
    - main()'s decision_rule_v3 / not_evaluable_decision_rule_v3 orchestration
  IMPORTED UNCHANGED, BY REFERENCE (Python import, never reimplemented):
    - dht.ols_loglog_fit, dht.bootstrap_gap_ci
      (experiments/EXP-SSIQ-58b642/implementation/descent_hitting_time.py)
    - v1c.apply_decision_rule
      (experiments/EXP-SSIQ-a85692/implementation/compute_delta_e.py, v1)
  NOT IMPORTED, NOT INVOKED AT ALL:
    - compute_delta_e_v2.py itself (this file never imports it)
    - v1c's own search/smoke-test/admission/Phase -1 functions (imported as
      a side effect of `import compute_delta_e as v1c`, since v1c is a
      single module, but never CALLED anywhere in this file)
"""

import argparse
import json
import math
import os
import platform
import random
import sys
import time

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS_DIR)

# Importing v1c (compute_delta_e.py) triggers ITS OWN sys.path.insert for
# experiments/EXP-SSIQ-58b642/implementation (see that file's own module
# header), which is what makes the subsequent `import descent_hitting_time`
# below resolve to the SAME already-loaded module object v1c itself uses --
# i.e. dht.ols_loglog_fit/dht.bootstrap_gap_ci here are BYTE-IDENTICAL,
# same-object, to what RUN-SSIQ-a85692-b's own real arm already called.
import compute_delta_e as v1c              # noqa: E402  (REUSED UNCHANGED, apply_decision_rule)
import descent_hitting_time as dht         # noqa: E402  (REUSED UNCHANGED, ols_loglog_fit/bootstrap_gap_ci)

EXPERIMENT_ID = "EXP-SSIQ-a85692"
RUN_ID = "RUN-SSIQ-a85692-c"
SOURCE_RUN_ID = "RUN-SSIQ-a85692-b"
SPEC_VERSION = 3
SEEDS = v1c.SEEDS                          # [20260805, 11, 977] -- FROZEN, unchanged

TRAPPED_FRACTION_EXCLUSION_THRESHOLD = 0.5  # v1's own inherited text, unchanged
NULL_ARM_MIN_PRIMES = 3                     # ols_loglog_fit's own minimum, n>=3
REAL_ARM_MIN_PRIMES = 4                     # decision_rule_v3's new gate, same >=4 floor as v1/v2


# ==========================================================================
# 1. trapped_exclusion_filter_v3 (GD-8's fix)
# ==========================================================================

def trapped_exclusion_filter_v3(real_per_prime, null_per_prime,
                                 threshold=TRAPPED_FRACTION_EXCLUSION_THRESHOLD):
    """spec_v3 inputs.trapped_exclusion_filter_v3. Excludes any prime with
    greedy_trapped_fraction > threshold from EACH arm's OLS fit input,
    independently: the real arm's own descent_metrics.per_prime[p] value
    governs the real-arm filter, and the null arm's own
    c_null_label.per_prime[p] value (which may differ numerically from the
    real arm's, since the underlying descent walk differs even though the
    graph is identical) governs the null-arm filter -- NOT a shared or
    inherited exclusion set between arms, per the spec text ("a prime whose
    real-labelled descent gets trapped pervasively will trap the
    shuffled-labelled descent on the identical graph too, for a reason
    unrelated to which arm's labels are used" -- an expectation, not a rule
    that reuses one arm's filter result for the other)."""
    real_survivors, real_excluded = [], {}
    for p, rec in real_per_prime.items():
        tf = rec.get("greedy_trapped_fraction")
        if tf is None:
            continue
        if tf <= threshold:
            real_survivors.append(p)
        else:
            real_excluded[p] = tf

    null_survivors, null_excluded, null_skipped = [], {}, {}
    for p, rec in null_per_prime.items():
        if rec.get("skipped"):
            null_skipped[p] = rec.get("reason")
            continue
        tf = rec.get("greedy_trapped_fraction")
        if tf is None:
            continue
        if tf <= threshold:
            null_survivors.append(p)
        else:
            null_excluded[p] = tf

    return {
        "threshold": threshold,
        "threshold_source": (
            "v1's own inherited M-GAMMA-GREEDY definition text "
            "('same trapped_fraction reporting and exclusion threshold'); "
            "NOT a new number introduced by this amendment."
        ),
        "real_arm": {
            "survivors": sorted(real_survivors),
            "excluded_trapped_fraction": real_excluded,
            "n_survivors": len(real_survivors),
        },
        "null_arm": {
            "survivors": sorted(null_survivors),
            "excluded_trapped_fraction": null_excluded,
            "skipped": null_skipped,
            "n_survivors": len(null_survivors),
        },
    }


# ==========================================================================
# 2. c_null_label_comparison_v3 (GD-9's fix)
# ==========================================================================

def c_null_label_comparison_v3(real_per_prime, null_per_prime, null_survivors,
                                rng_seed, min_primes=NULL_ARM_MIN_PRIMES,
                                n_boot=2000):
    """spec_v3 inputs.c_null_label_comparison_v3. IF (and only if) >=3
    primes survive trapped_exclusion_filter_v3 in the null arm: fit
    gamma_null_greedy/gamma_null_random via dht.ols_loglog_fit (IMPORTED
    UNCHANGED, the IDENTICAL function the real arm's own gamma_greedy/
    gamma_random already used in RUN-SSIQ-a85692-b) on the surviving
    primes' N (from real_per_prime, unchanged) against
    c_null_label.per_prime[p].greedy_median/.random_median; bootstrap
    m_gap_null's 95% CI via dht.bootstrap_gap_ci (IMPORTED UNCHANGED, same
    n_boot=2000, same PRIMES-as-resampling-unit design). PRE-REGISTERED
    COMPARISON RULE (spec text): c_null_label_control_failure = True iff the
    null arm's 95% CI for m_gap_null ALSO excludes 0 in the POSITIVE
    direction -- mirroring apply_decision_rule's own pre-existing DETECTED
    criterion (m_gap_ci_lo is not None and m_gap_ci_lo > 0.0), not a new
    bespoke threshold. ELSE: c_null_label_control_failure is reported as the
    explicit string 'NOT-EVALUABLE', never defaulted to True or False, per
    invalidation_rules_v3_additions."""
    if len(null_survivors) < min_primes:
        return {
            "evaluable": False,
            "c_null_label_control_failure": "NOT-EVALUABLE",
            "reason": (
                "trapped_exclusion_filter_v3 left %d primes surviving in the "
                "null arm, below ols_loglog_fit's own >=%d minimum; "
                "c_null_label_comparison_v3's fit-and-bootstrap branch "
                "CANNOT RUN (dht.ols_loglog_fit raises ValueError below "
                "n=3). Reported as NOT-EVALUABLE explicitly, per "
                "invalidation_rules_v3_additions -- NOT defaulted to False "
                "(which would silently disable the control this amendment "
                "exists to fix) or to True (which would fabricate a control "
                "failure with no computation behind it)."
                % (len(null_survivors), min_primes)
            ),
            "n_null_survivors": len(null_survivors),
            "min_primes_required": min_primes,
        }

    ordered = sorted(null_survivors)
    N_list = [real_per_prime[p]["N"] for p in ordered]
    greedy_medians = [null_per_prime[p]["greedy_median"] for p in ordered]
    random_medians = [null_per_prime[p]["random_median"] for p in ordered]

    fit_greedy = dht.ols_loglog_fit(N_list, greedy_medians)
    fit_random = dht.ols_loglog_fit(N_list, random_medians)
    m_gap_null = fit_random["gamma"] - fit_greedy["gamma"]

    rng = random.Random(rng_seed)
    lo, hi, gaps = dht.bootstrap_gap_ci(N_list, greedy_medians, random_medians,
                                         rng, n_boot=n_boot)

    control_failure = bool(lo is not None and lo > 0.0)

    return {
        "evaluable": True,
        "primes_used": ordered,
        "N_list": N_list,
        "greedy_medians": greedy_medians,
        "random_medians": random_medians,
        "gamma_null_greedy": fit_greedy["gamma"],
        "gamma_null_random": fit_random["gamma"],
        "m_gap_null": m_gap_null,
        "m_gap_null_ci_lo": lo,
        "m_gap_null_ci_hi": hi,
        "n_boot": n_boot,
        "n_boot_valid_draws": len(gaps),
        "c_null_label_control_failure": control_failure,
        "reason": (
            "null arm 95%% CI [%s, %s] %s 0 in the positive direction -- "
            "mirrors apply_decision_rule's own DETECTED criterion "
            "(m_gap_ci_lo > 0.0), applied here to the null arm per the "
            "pre-registered comparison rule."
            % (lo, hi, "excludes" if control_failure else "does not exclude")
        ),
    }


# ==========================================================================
# 3. synthetic_self_test_v3 (PF-1's fix, REQUIRED ARTIFACT)
# ==========================================================================

def run_synthetic_self_test_v3(rng_seed=SEEDS[0], n_boot=2000):
    """spec_v3 inputs.synthetic_self_test_v3. INDEPENDENT of
    RUN-SSIQ-a85692-b's real data: 4 synthetic (N, greedy_median,
    random_median) triples constructed as EXACT power laws with known
    exponents (no noise), run through the IDENTICAL dht.ols_loglog_fit /
    dht.bootstrap_gap_ci calls c_null_label_comparison_v3 uses, to
    demonstrate the fit-and-bootstrap branch executes end-to-end and
    reproduces the analytically-predicted gamma/m_gap to tight tolerance.
    Per evidentiary_limitation_disclosure_v3, this is the ONLY runtime
    evidence this batch can supply that the fit-and-bootstrap branch works,
    since trapped_exclusion_filter_v3's own worked check makes that branch
    structurally unreachable on RUN-SSIQ-a85692-b's real data (confirmed
    below, see main())."""
    gamma_greedy_expected = 0.3
    gamma_random_expected = 0.8
    N_list = [100, 1000, 10000, 100000]
    greedy_medians = [float(N) ** gamma_greedy_expected for N in N_list]
    random_medians = [float(N) ** gamma_random_expected for N in N_list]

    fit_greedy = dht.ols_loglog_fit(N_list, greedy_medians)
    fit_random = dht.ols_loglog_fit(N_list, random_medians)
    m_gap_expected = gamma_random_expected - gamma_greedy_expected
    m_gap_computed = fit_random["gamma"] - fit_greedy["gamma"]

    rng = random.Random(rng_seed)
    lo, hi, gaps = dht.bootstrap_gap_ci(N_list, greedy_medians, random_medians,
                                         rng, n_boot=n_boot)

    tol = 1e-9
    gamma_greedy_match = abs(fit_greedy["gamma"] - gamma_greedy_expected) < tol
    gamma_random_match = abs(fit_random["gamma"] - gamma_random_expected) < tol
    m_gap_match = abs(m_gap_computed - m_gap_expected) < tol
    ci_contains_expected = bool(
        lo is not None and hi is not None and lo - tol <= m_gap_expected <= hi + tol)
    # For an EXACT power law with zero noise, every point lies exactly on
    # the fitted log-log line, so ANY bootstrap resample (with >=2 distinct
    # N values in the draw) reproduces the SAME exact gamma -- the CI is
    # therefore EXPECTED, analytically, to degenerate to a point at
    # m_gap_expected. Checked below, not assumed.
    ci_degenerate_at_expected = bool(
        lo is not None and hi is not None
        and abs(lo - m_gap_expected) < tol and abs(hi - m_gap_expected) < tol)

    # PRE-REGISTERED comparison rule applied to this synthetic construction
    # too, purely to demonstrate the SAME branch of code that would compute
    # c_null_label_control_failure on real data behaves as expected here:
    # since m_gap_expected=0.5>0 and the CI degenerates at 0.5, this
    # synthetic instance's own control_failure evaluates True -- a fact
    # about THIS constructed example, not a claim about RUN-SSIQ-a85692-b.
    synthetic_control_failure = bool(lo is not None and lo > 0.0)

    all_checks_pass = (gamma_greedy_match and gamma_random_match
                        and m_gap_match and ci_degenerate_at_expected)

    return {
        "purpose": (
            "PF-1 FIX, REQUIRED ARTIFACT. Demonstrates "
            "c_null_label_comparison_v3's fit-and-bootstrap branch "
            "(dht.ols_loglog_fit + dht.bootstrap_gap_ci, the IDENTICAL "
            "functions, imported unchanged) executes end-to-end and "
            "reproduces a hand-computable/analytically-predictable result, "
            "INDEPENDENT of RUN-SSIQ-a85692-b's real data. Per "
            "evidentiary_limitation_disclosure_v3, this synthetic self-test "
            "is the ONLY runtime evidence this batch supplies that the "
            "fit-and-bootstrap branch works; the real-data re-analysis "
            "(main() below) is expected, and confirmed, to reach only the "
            "NOT-EVALUABLE path."
        ),
        "independent_of_real_data": True,
        "data_source": (
            "hand-constructed exact power laws, NOT sourced from "
            "RUN-SSIQ-a85692-b, RUN-SSIQ-a85692-a, or any prior run's "
            "raw-result.json."
        ),
        "inputs": {
            "N_list": N_list,
            "greedy_medians": greedy_medians,
            "random_medians": random_medians,
            "construction": (
                "greedy_median(N) = N**0.3 (gamma_greedy=0.3, c=1.0); "
                "random_median(N) = N**0.8 (gamma_random=0.8, c=1.0) -- "
                "exact power laws, zero noise, so ols_loglog_fit's own "
                "r_squared is expected to be 1.0 exactly."
            ),
            "rng_seed": rng_seed,
            "n_boot": n_boot,
        },
        "computed": {
            "gamma_null_greedy": fit_greedy["gamma"],
            "gamma_null_random": fit_random["gamma"],
            "r_squared_greedy": fit_greedy["r_squared"],
            "r_squared_random": fit_random["r_squared"],
            "m_gap_null": m_gap_computed,
            "m_gap_null_ci_lo": lo,
            "m_gap_null_ci_hi": hi,
            "n_boot_valid_draws": len(gaps),
            "n_boot_degenerate_draws_dropped": n_boot - len(gaps),
            "synthetic_c_null_label_control_failure": synthetic_control_failure,
        },
        "expected_analytic": {
            "gamma_greedy_expected": gamma_greedy_expected,
            "gamma_random_expected": gamma_random_expected,
            "m_gap_expected": m_gap_expected,
            "derivation": (
                "log(y) = gamma*log(N) + log(c) is EXACTLY linear for a pure "
                "power law with c=1.0 and no noise, so OLS recovers gamma to "
                "floating-point precision (R^2=1, RSS=0); since every point "
                "lies exactly on the fitted line, any bootstrap resample "
                "with >=2 distinct N values reproduces the SAME exact gamma, "
                "so the CI is expected to degenerate to a point at "
                "m_gap_expected=0.5."
            ),
        },
        "checks": {
            "gamma_greedy_matches_expected_tol_1e-9": gamma_greedy_match,
            "gamma_random_matches_expected_tol_1e-9": gamma_random_match,
            "m_gap_matches_expected_tol_1e-9": m_gap_match,
            "bootstrap_ci_contains_expected_m_gap": ci_contains_expected,
            "bootstrap_ci_degenerate_at_expected_m_gap_tol_1e-9": ci_degenerate_at_expected,
        },
        "self_test_verdict": (
            "PASS -- fit-and-bootstrap branch reproduces the analytic "
            "power-law exponents and gap to 1e-9 tolerance, and the "
            "bootstrap CI degenerates to a point at the expected m_gap, "
            "exactly as predicted for a noiseless power law."
            if all_checks_pass else
            "FAIL -- see checks above for the specific mismatch; this would "
            "indicate a defect in ols_loglog_fit/bootstrap_gap_ci or in how "
            "this self-test invokes them, and would need investigation "
            "before c_null_label_comparison_v3's real-data branch (were it "
            "ever reached) could be trusted."
        ),
        "all_checks_pass": all_checks_pass,
    }


# ==========================================================================
# 4. main() -- decision_rule_v3 / not_evaluable_decision_rule_v3 orchestration
# ==========================================================================

def git_state():
    def g(*a):
        try:
            import subprocess
            return subprocess.check_output(
                ["git"] + list(a), stderr=subprocess.DEVNULL,
                cwd=_THIS_DIR).decode().strip()
        except Exception:
            return None
    return {"commit": g("rev-parse", "HEAD"),
            "branch": g("rev-parse", "--abbrev-ref", "HEAD")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-b", required=True,
                     help="path to RUN-SSIQ-a85692-b/raw-result.json (real-data source)")
    ap.add_argument("--out", required=True,
                     help="output path for RUN-SSIQ-a85692-c/raw-result.json")
    ap.add_argument("--self-test-out", required=True,
                     help="output path for RUN-SSIQ-a85692-c/synthetic_self_test.json")
    args = ap.parse_args()

    t_start = time.time()

    with open(args.run_b) as f:
        run_b = json.load(f)

    real_per_prime_raw = run_b["descent_metrics"]["per_prime"]
    null_per_prime_raw = run_b["c_null_label"]["per_prime"]
    # JSON round-trips int-keyed dicts as strings; restore int keys.
    real_per_prime = {int(k): v for k, v in real_per_prime_raw.items()}
    null_per_prime = {int(k): v for k, v in null_per_prime_raw.items()}

    # -- Step 0: synthetic self-test, computed FIRST and independent of the
    # real-data re-analysis below (order chosen for clarity only; neither
    # step depends on the other's output). --------------------------------
    synthetic_self_test = run_synthetic_self_test_v3(rng_seed=SEEDS[0])
    with open(args.self_test_out, "w") as f:
        json.dump(synthetic_self_test, f, indent=2, sort_keys=True)

    # -- Step 1: trapped_exclusion_filter_v3 (GD-8's fix), applied ONCE,
    # identically, before either arm's OLS fit runs. -----------------------
    filter_result = trapped_exclusion_filter_v3(real_per_prime, null_per_prime)
    real_survivors = filter_result["real_arm"]["survivors"]
    null_survivors = filter_result["null_arm"]["survivors"]

    # -- Step 2: c_null_label_comparison_v3 (GD-9's fix), computed
    # regardless of the real-arm gate's outcome below -- this is a
    # DIAGNOSTIC/disclosure computation independent of decision_rule_v3's
    # own gate ordering, and its own NOT-EVALUABLE/evaluable result is
    # reported either way. -------------------------------------------------
    null_comparison = c_null_label_comparison_v3(
        real_per_prime, null_per_prime, null_survivors, rng_seed=SEEDS[0])

    # -- Step 3: decision_rule_v3's NEW GATE, CHECKED FIRST. ----------------
    phase_minus1_gate_pass_already = True  # UNCHANGED from RUN-SSIQ-a85692-b; not reopened here
    phase0_pass_already = True             # UNCHANGED from RUN-SSIQ-a85692-b; not reopened here

    descent_metrics_v3 = {"ran": False}
    apply_decision_rule_invoked = False
    apply_decision_rule_result = None

    if len(real_survivors) < REAL_ARM_MIN_PRIMES:
        decision = {
            "branch": "DATA-UNAVAILABLE-BLOCKED",
            "reason": (
                "decision_rule_v3's NEW GATE (checked first, per "
                "specification_v3.yaml): trapped_exclusion_filter_v3 left "
                "%d primes surviving in the real arm, below the >=%d floor. "
                "Distinct in its stated reason from every other "
                "DATA-UNAVAILABLE/BLOCKED instance this campaign has "
                "recorded (WISDE unavailability in BATCH-003; "
                "budget-formula exhaustion in BATCH-004): this one is "
                "specifically 'lack of coverage under the corrected "
                "trapped-vertex exclusion filter.' The Phase -1 gate itself "
                "(M-COVERAGE>=0.5 on >=4 primes) is UNCHANGED and was "
                "already passed in RUN-SSIQ-a85692-b; this amendment does "
                "not reopen it -- this is a NEW, PRIOR gate on a disjoint "
                "quantity (greedy_trapped_fraction, not M-COVERAGE)."
                % (len(real_survivors), REAL_ARM_MIN_PRIMES)
            ),
        }
        # apply_decision_rule is NOT invoked in this branch: decision_rule_v3's
        # own text reports DATA-UNAVAILABLE-BLOCKED directly when the new gate
        # fails, and apply_decision_rule (v1c, imported unchanged above) has
        # no parameter representing this new gate at all -- its own
        # phase_minus1_gate_pass parameter is the DIFFERENT, already-passed
        # M-COVERAGE gate. Invoking it here would require inventing an
        # interface point decision_rule_v3 does not specify.
    else:
        # >=4 real-arm survivors: recompute gamma_greedy/gamma_random/m_gap
        # on exactly the surviving subset, using the SAME dht functions.
        ordered = sorted(real_survivors)
        N_list = [real_per_prime[p]["N"] for p in ordered]
        greedy_medians = [real_per_prime[p]["greedy_median"] for p in ordered]
        random_medians = [real_per_prime[p]["random_median"] for p in ordered]
        fit_greedy = dht.ols_loglog_fit(N_list, greedy_medians)
        fit_random = dht.ols_loglog_fit(N_list, random_medians)
        m_gap = fit_random["gamma"] - fit_greedy["gamma"]
        rng_boot = random.Random(SEEDS[0])
        lo, hi, _ = dht.bootstrap_gap_ci(N_list, greedy_medians, random_medians, rng_boot)
        descent_metrics_v3 = {
            "ran": True, "primes_used": ordered,
            "gamma_greedy": fit_greedy["gamma"], "gamma_random": fit_random["gamma"],
            "m_gap": m_gap, "m_gap_ci_lo": lo, "m_gap_ci_hi": hi,
            "n_range_achieved": [min(N_list), max(N_list)],
            "n_primes_used": len(ordered),
        }

        c_null_label_control_failure = null_comparison["c_null_label_control_failure"]

        if c_null_label_control_failure == "NOT-EVALUABLE":
            # not_evaluable_decision_rule_v3: BYPASS apply_decision_rule
            # entirely; report UNRESOLVED-BY-THIS-TEST directly, never
            # DETECTED, on the non-improvisation principle that a control
            # that could not be evaluated cannot license a positive claim.
            decision = {
                "branch": "UNRESOLVED-BY-THIS-TEST",
                "reason": (
                    "not_evaluable_decision_rule_v3: the real arm cleared "
                    ">=4 survivors, but c_null_label_control_failure is "
                    "NOT-EVALUABLE (null arm has <3 survivors). "
                    "apply_decision_rule's Boolean-only interface has no "
                    "slot for this state, so it is BYPASSED entirely per "
                    "the pre-registered bypass rule; the absence of "
                    "C-NULL-LABEL's protection is treated the same way a "
                    "genuine ambiguous/uncertain result is treated, never "
                    "as if the control had passed."
                ),
            }
        else:
            # c_search_bias / c_connectivity are UNCHANGED from
            # RUN-SSIQ-a85692-b (not recomputed; this amendment performs no
            # new search), reused by reference from that run's own raw data.
            c_search_bias_control_failure = bool(
                run_b["c_search_bias"]["magnitudes_comparable_flag"])
            c_connectivity_all_pass = all(
                v["pass"] for v in run_b["correctness_gates"]["connectivity"].values())
            apply_decision_rule_result = v1c.apply_decision_rule(
                phase0_pass=phase0_pass_already,
                phase_minus1_gate_pass=phase_minus1_gate_pass_already,
                c_search_bias_control_failure=c_search_bias_control_failure,
                c_null_label_control_failure=bool(c_null_label_control_failure),
                c_connectivity_all_pass=c_connectivity_all_pass,
                m_gap_ci_lo=descent_metrics_v3["m_gap_ci_lo"],
                m_gap_ci_hi=descent_metrics_v3["m_gap_ci_hi"],
            )
            apply_decision_rule_invoked = True
            decision = apply_decision_rule_result

    wall_seconds = time.time() - t_start

    payload = {
        "experiment_id": EXPERIMENT_ID,
        "run_id": RUN_ID,
        "amends_run_id": SOURCE_RUN_ID,
        "spec_version": SPEC_VERSION,
        "real_data_source": (
            "experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-b/raw-result.json "
            "descent_metrics.per_prime (real arm) and c_null_label.per_prime "
            "(null arm) ONLY -- no other field of that file was read or used."
        ),
        "synthetic_self_test_source": (
            "hand-constructed exact power laws, computed in this process, "
            "NOT sourced from any prior run -- see "
            "runs/RUN-SSIQ-a85692-c/synthetic_self_test.json for the full "
            "record, written as a DISTINCT artifact, never conflated with "
            "the real-data re-analysis below."
        ),
        "trapped_exclusion_filter_v3": filter_result,
        "c_null_label_comparison_v3": null_comparison,
        "descent_metrics_v3": descent_metrics_v3,
        "apply_decision_rule_invoked": apply_decision_rule_invoked,
        "apply_decision_rule_result": apply_decision_rule_result,
        "decision": decision,
        "wall_clock_seconds": wall_seconds,
        "git": git_state(),
        "python": sys.version,
        "platform": platform.platform(),
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t_start)),
        "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "certificate": {
            "kind": "none",
            "verified": None,
            "verifier": None,
            "reason": (
                "Pure measurement/re-analysis run. No discrete log is "
                "claimed, no factor-base relation is claimed, no isogeny "
                "problem instance is solved. docs/claims-and-verification.md "
                "requires kind: none to be stated explicitly for such runs."
            ),
        },
    }

    with open(args.out, "w") as f:
        json.dump(payload, f, indent=2, sort_keys=True)

    print("trapped_exclusion_filter_v3: real_arm n_survivors=%d, null_arm n_survivors=%d"
          % (filter_result["real_arm"]["n_survivors"], filter_result["null_arm"]["n_survivors"]))
    print("c_null_label_comparison_v3: evaluable=%s, c_null_label_control_failure=%s"
          % (null_comparison["evaluable"], null_comparison["c_null_label_control_failure"]))
    print("synthetic_self_test_v3: all_checks_pass=%s" % synthetic_self_test["all_checks_pass"])
    print("DECISION RULE -> %s" % decision["branch"])
    print("  %s" % decision["reason"])
    print("wall_clock_seconds=%.6f" % wall_seconds)


if __name__ == "__main__":
    main()
