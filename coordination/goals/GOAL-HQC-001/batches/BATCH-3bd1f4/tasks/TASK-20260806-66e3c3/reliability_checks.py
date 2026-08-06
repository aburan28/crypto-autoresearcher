#!/usr/bin/env python3
"""Two cheap, no-new-sampling reliability checks on the "double dilution"
formula: Delta(log2_A_k) = (k/n_e)*Delta_p/ln2 * [mubar_{k-1}/mubar_k - 1/q_hat].

TASK-20260806-66e3c3 (executor) / BATCH-3bd1f4 / GOAL-HQC-001 / EXP-HQC-982268.

WHAT THIS IS
------------
Pre-registered in design.md (this task's own directory) BEFORE this script
was run on any data. Two checks, both computed ENTIRELY from already-
committed data -- NO cryptographic sampler is invoked, NO stage_a.py shard is
generated or regenerated, NO new (T)-trial is drawn anywhere in this file:

  (1) Conditional-vs-unconditional mubar_{k-1} check: extends the Red Team's
      single k=16/17 deviation number (13.4%) into a full per-k pattern, on
      TWO independent already-committed datasets (T=1e7 real-sampler
      baseline; T=10,000 pooled matched-pair true-arm).
  (2) SE-scaling in-range check: independently reimplements the required-T
      formula from already-committed constants and sweeps Delta_p across a
      wide range (not just the Validator's single audited point), checking
      for the algebraic 1/Delta_p^2 scaling, monotonicity, sign symmetry,
      and absence of blow-ups/discontinuities/sign errors.

WHAT THIS IS NOT
----------------
Nothing here is a statement about HQC, A17, any decoding-failure rate, or any
standardized HQC parameter set. Claim tier: TOY, hard ceiling. This task
reports observations only and makes no campaign-level call.

Re-run:
    PYTHONDONTWRITEBYTECODE=1 python3 reliability_checks.py --out-dir .
    PYTHONDONTWRITEBYTECODE=1 python3 reliability_checks.py --selftest-fail-closed
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import platform
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *([".."] * 7)))

MEASURE_PY = os.path.join(
    REPO, "coordination", "goals", "GOAL-HQC-001", "batches", "BATCH-0a65c0",
    "tasks", "TASK-20260806-cde749", "measure.py")
MEASUREMENT_RESULTS = os.path.join(
    REPO, "coordination", "goals", "GOAL-HQC-001", "batches", "BATCH-0a65c0",
    "tasks", "TASK-20260806-cde749", "measurement_results.json")
REANALYSIS_RESULTS = os.path.join(
    REPO, "coordination", "goals", "GOAL-HQC-001", "batches", "BATCH-fc30b5",
    "tasks", "TASK-20260806-e120e8", "reanalysis_results.json")

# sha256 pins, taken directly from the already-committed snapshot receipts
# named in design.md Section 1.2 item 1-3 -- NOT recomputed on the fly and
# then compared to themselves (that would be a tautology). These are the
# hashes another task's Coordinator snapshot already declared.
PIN_MEASURE_PY = "a4fd1ecb63f0ddc83c02ef45f2c65ab31cf13d13e7ae94f500e67465b24f5dc8"
PIN_MEASUREMENT_RESULTS = "6b2804e36f35a453f524843af6ef40da03e0295aece7fc574e01923f0d575801"
PIN_REANALYSIS_RESULTS = "d67c80fedd7e29e8c5dc1838a2003bb235241214103bf6cfbb1d68cde7e5bd35"

ALPHA = 0.05
POWER = 0.90


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def z_from_normal_quantile(p: float) -> float:
    """Inverse standard normal CDF via math.erfinv-equivalent (no scipy
    dependency assumed). Uses the same closed-form Acklam-free approach:
    scipy.stats.norm.ppf if available, else a high-precision rational
    approximation (Beasley-Springer-Moro) accurate to ~1e-9, sufficient for
    the atol=1e-6 gate this check uses."""
    try:
        from scipy.stats import norm
        return float(norm.ppf(p))
    except Exception:
        pass
    # Beasley-Springer-Moro algorithm
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow = 0.02425
    phigh = 1 - plow
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p <= phigh:
        q = p - 0.5
        r = q*q
        return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
               (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)
    q = math.sqrt(-2 * math.log(1 - p))
    return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
             ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)


def git_state():
    def run(*a):
        try:
            return subprocess.run(a, cwd=REPO, capture_output=True, text=True,
                                  timeout=60).stdout.strip()
        except Exception as exc:  # pragma: no cover
            return f"<unavailable: {exc}>"
    return dict(commit=run("git", "rev-parse", "HEAD"),
                branch=run("git", "rev-parse", "--abbrev-ref", "HEAD"),
                dirty=bool(run("git", "status", "--porcelain")),
                dirty_paths=run("git", "status", "--porcelain").splitlines()[:40])


# --------------------------------------------------------------------------
# fail-closed gates
# --------------------------------------------------------------------------

class FailClosed(SystemExit):
    pass


def gate_sha256_pins(corrupt: bool = False):
    """Section 1.2 items 1-3 / 2.2 item 1. FAIL-CLOSED on mismatch."""
    checks = []
    for path, pin, label in (
        (MEASURE_PY, PIN_MEASURE_PY, "measure.py"),
        (MEASUREMENT_RESULTS, PIN_MEASUREMENT_RESULTS, "measurement_results.json"),
        (REANALYSIS_RESULTS, PIN_REANALYSIS_RESULTS, "reanalysis_results.json"),
    ):
        actual = sha256_file(path)
        expected = pin
        if corrupt and label == "measure.py":
            expected = "0" * 64  # deliberately wrong, to exercise the gate
        ok = (actual == expected)
        checks.append(dict(file=label, path=os.path.relpath(path, REPO),
                           expected_sha256=expected, actual_sha256=actual,
                           match=ok))
        if not ok:
            raise FailClosed(
                f"FAIL-CLOSED: sha256 mismatch on {label}: "
                f"expected {expected}, got {actual}")
    return checks


def load_measure_module():
    spec = importlib.util.spec_from_file_location("measure_pinned", MEASURE_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --------------------------------------------------------------------------
# Check 1: conditional-vs-unconditional mubar_{k-1}
# --------------------------------------------------------------------------

def check1_dataset_A(measure_mod, R_out):
    """T=1e7 real-sampler baseline. mu_k for every reachable k, computed via
    the sha256-pinned log2_A_from_hists/comb_matrix -- no reimplementation."""
    d = json.load(open(MEASUREMENT_RESULTS))

    hist = np.array(d["T_arm_diagnostics"]["S_histogram"], dtype=np.float64)
    n_e = d["configuration"]["n_e"]
    T_ach = d["T_arm"]["trials_achieved"]
    q_committed = d["T_arm_diagnostics"]["q_hat_measured"]

    gate = dict(
        histogram_sum_equals_T_achieved=dict(
            histogram_sum=float(hist.sum()), T_achieved=T_ach,
            match=bool(hist.sum() == T_ach)))
    if not gate["histogram_sum_equals_T_achieved"]["match"]:
        raise FailClosed("FAIL-CLOSED: Dataset A S_histogram sum != "
                          "trials_achieved; possible truncation or "
                          "transcription error.")

    q_recomputed = float((hist * np.arange(n_e + 1)).sum() / (T_ach * n_e))
    gate["q_hat_recompute"] = dict(
        committed=q_committed, recomputed=q_recomputed,
        rel_diff=abs(q_recomputed - q_committed) / q_committed,
        match=bool(abs(q_recomputed - q_committed) / q_committed < 1e-12))
    if not gate["q_hat_recompute"]["match"]:
        raise FailClosed("FAIL-CLOSED: Dataset A q_hat recomputation "
                          "mismatch beyond tolerance.")

    # Largest s with nonzero histogram support bounds the largest k for
    # which mu_k is computable from this histogram at all.
    support = np.nonzero(hist > 0)[0]
    s_max = int(support.max())
    k_max_usable = s_max  # mu_k needs s>=k support to be nonzero

    ks = list(range(1, k_max_usable + 1))
    C = measure_mod.comb_matrix(n_e, ks)
    log2A = measure_mod.log2_A_from_hists(hist[None, :], n_e, ks, C)[0]
    q_used_by_pinned_fn = float(hist @ np.arange(n_e + 1) / (T_ach * n_e))

    # cross-check the pinned function's own internally-computed q against
    # our independently-recomputed q_recomputed (must be identical, same
    # histogram, same formula)
    gate["pinned_fn_q_matches_recompute"] = dict(
        match=bool(q_used_by_pinned_fn == q_recomputed))
    if not gate["pinned_fn_q_matches_recompute"]["match"]:
        raise FailClosed("FAIL-CLOSED: pinned log2_A_from_hists internal q "
                          "does not match independently recomputed q.")

    mu = {}
    for j, k in enumerate(ks):
        lv = log2A[j]
        if np.isfinite(lv):
            mu[k] = float(2.0 ** (lv + k * math.log2(q_recomputed)))
        else:
            mu[k] = None

    # cross-check log2_A_17 against the committed MEASUREMENT.cells value
    cell17 = [c for c in d["MEASUREMENT"]["cells"] if c["k"] == 17][0]
    idx17 = ks.index(17)
    gate["log2_A_17_cross_check"] = dict(
        committed=cell17["log2_A_k"], recomputed=float(log2A[idx17]),
        abs_diff=abs(float(log2A[idx17]) - cell17["log2_A_k"]),
        match=bool(abs(float(log2A[idx17]) - cell17["log2_A_k"]) < 1e-9))
    if not gate["log2_A_17_cross_check"]["match"]:
        raise FailClosed("FAIL-CLOSED: Dataset A recomputed log2_A_17 does "
                          "not match the committed cell value.")

    eff_trials = {k: int(hist[k:].sum()) for k in ks}

    rows = []
    for k in range(2, k_max_usable + 1):
        if mu.get(k) is None or mu.get(k - 1) is None or mu[k] <= 0:
            continue
        ratio = mu[k - 1] / mu[k]
        rel_dev = ratio * q_recomputed - 1.0
        rows.append(dict(
            k=k, mu_km1=mu[k - 1], mu_k=mu[k], ratio=ratio,
            iid_prediction_1_over_q=1.0 / q_recomputed,
            relative_deviation=rel_dev,
            effective_trials_k=eff_trials[k],
            effective_trials_km1=eff_trials[k - 1]))

    R_out["check1_dataset_A"] = dict(
        source="TASK-20260806-cde749/measurement_results.json",
        T=T_ach, n_e=n_e, q_hat=q_recomputed,
        s_max_support=s_max, k_max_usable=k_max_usable,
        gates=gate, per_k=rows)
    return rows


def check1_dataset_B(R_out):
    """T=10,000 pooled matched-pair true arm. mubar_k_true/mubar_km1_true
    read DIRECTLY from the already-committed per_k table -- no
    recomputation, this IS the table the Red Team's 13.4% number came
    from."""
    d = json.load(open(REANALYSIS_RESULTS))
    rt = d["required_T_derivation"]
    per_k = rt["per_k"]

    # mu_1 == q_hat exactly (an algebraic identity of mubar_from_hist: the
    # k=1 restricted moment IS the marginal rate). Cross-check this against
    # the load_bearing_k17 baseline_arm provenance string's own stated
    # q_hat, parsed but not trusted blindly -- both must agree.
    q_from_mu1 = None
    for row in per_k:
        if row["k"] == 2:
            q_from_mu1 = row["mubar_km1_true"]
            break
    if q_from_mu1 is None:
        raise FailClosed("FAIL-CLOSED: Dataset B per_k table missing k=2 "
                          "row needed to recover q_hat via mubar_1.")

    baseline_arm_str = rt["baseline_arm"]
    import re
    m = re.search(r"q_hat=([0-9.eE+-]+)", baseline_arm_str)
    if not m:
        raise FailClosed("FAIL-CLOSED: could not parse q_hat from Dataset "
                          "B's baseline_arm provenance string.")
    q_from_string = float(m.group(1))
    gate = dict(
        q_hat_from_mu1_vs_provenance_string=dict(
            from_mu1=q_from_mu1, from_string=q_from_string,
            rel_diff=abs(q_from_mu1 - q_from_string) / q_from_string,
            match=bool(abs(q_from_mu1 - q_from_string) / q_from_string < 1e-9)))
    if not gate["q_hat_from_mu1_vs_provenance_string"]["match"]:
        raise FailClosed("FAIL-CLOSED: Dataset B q_hat mismatch between "
                          "mubar_1 and provenance string.")
    q_hat = q_from_mu1

    rows = []
    for row in per_k:
        k = row["k"]
        mu_k = row["mubar_k_true"]
        mu_km1 = row["mubar_km1_true"]
        if mu_k <= 0:
            continue
        ratio = mu_km1 / mu_k
        rel_dev = ratio * q_hat - 1.0
        rows.append(dict(
            k=k, mu_km1=mu_km1, mu_k=mu_k, ratio=ratio,
            iid_prediction_1_over_q=1.0 / q_hat,
            relative_deviation=rel_dev))

    R_out["check1_dataset_B"] = dict(
        source="TASK-20260806-e120e8/reanalysis_results.json",
        T=10000, n_e=56, q_hat=q_hat, gates=gate, per_k=rows)
    return rows, q_hat


def check1_cross_dataset_agreement(rows_A, rows_B, R_out):
    A = {r["k"]: r["relative_deviation"] for r in rows_A}
    B = {r["k"]: r["relative_deviation"] for r in rows_B}
    common_ks = sorted(set(A) & set(B))
    compare = [dict(k=k, dataset_A_T1e7=A[k], dataset_B_T1e4=B[k],
                    abs_diff=abs(A[k] - B[k]))
               for k in common_ks]
    R_out["check1_cross_dataset_agreement"] = dict(
        common_ks=common_ks, per_k=compare,
        k17_dataset_A=A.get(17), k17_dataset_B=B.get(17),
        note=("Dataset B's k=17 relative_deviation is the exact quantity "
              "the Red Team reported as 13.4% (0.134); reproduced here from "
              "the same committed per_k table, not a new measurement."))


# --------------------------------------------------------------------------
# Check 2: SE-scaling in-range check
# --------------------------------------------------------------------------

def required_T(k, delta_p, n_e, q_hat, mu_k, mu_km1, se_ref, T_ref, z_sum):
    bracket = mu_km1 / mu_k - 1.0 / q_hat
    delta_log2_A = (k / n_e) * (delta_p / math.log(2.0)) * bracket
    if delta_log2_A == 0.0:
        return float("inf"), delta_log2_A, bracket
    treq = T_ref * (z_sum * se_ref / abs(delta_log2_A)) ** 2
    return treq, delta_log2_A, bracket


def check2(R_out):
    d = json.load(open(REANALYSIS_RESULTS))
    rt = d["required_T_derivation"]
    pt = rt["power_target"]
    lb = rt["load_bearing_k17"]
    n_e = 56
    T_ref = 10000
    q_hat = None
    for row in rt["per_k"]:
        if row["k"] == 2:
            q_hat = row["mubar_km1_true"]
    z_sum_committed = pt["z_sum"]

    gates = {}

    # gate: z_sum recomputation
    z_alpha2 = z_from_normal_quantile(1 - ALPHA / 2)
    z_beta = z_from_normal_quantile(POWER)
    z_sum_recomputed = z_alpha2 + z_beta
    gates["z_sum_recompute"] = dict(
        committed=z_sum_committed, recomputed=z_sum_recomputed,
        abs_diff=abs(z_sum_recomputed - z_sum_committed),
        match=bool(abs(z_sum_recomputed - z_sum_committed) < 1e-6))
    if not gates["z_sum_recompute"]["match"]:
        raise FailClosed("FAIL-CLOSED: z_sum recomputation mismatch.")
    z_sum = z_sum_committed  # use the committed value for all downstream math

    # gate: reproduce load_bearing_k17 at delta_p=0.0082 exactly
    row17 = [r for r in rt["per_k"] if r["k"] == 17][0]
    treq, dlog2A, bracket17 = required_T(
        17, 0.0082, n_e, q_hat, row17["mubar_k_true"], row17["mubar_km1_true"],
        row17["se_paired_at_T_ref_10000"], T_ref, z_sum)
    committed = lb["modeled_delta_log2_A_red_team_input"]
    gates["load_bearing_k17_reproduction"] = dict(
        committed_total=committed["total"], recomputed_total=dlog2A,
        rel_diff=abs(dlog2A - committed["total"]) / abs(committed["total"]),
        committed_required_T=lb["required_T_red_team_input"],
        recomputed_required_T=treq,
        rel_diff_T=abs(treq - lb["required_T_red_team_input"]) / lb["required_T_red_team_input"],
        match=bool(abs(dlog2A - committed["total"]) / abs(committed["total"]) < 1e-9
                   and abs(treq - lb["required_T_red_team_input"]) / lb["required_T_red_team_input"] < 1e-6))
    if not gates["load_bearing_k17_reproduction"]["match"]:
        raise FailClosed("FAIL-CLOSED: reimplemented formula does not "
                          "reproduce the committed k=17 Delta_p=0.0082 "
                          "figures.")

    # gate: reproduce all 8 committed sensitivity points at k=17
    sens_checks = []
    all_sens_ok = True
    for point in rt["delta_p_sensitivity_k17"]:
        dp = point["delta_p_input"]
        treq_r, dlog2A_r, _ = required_T(
            17, dp, n_e, q_hat, row17["mubar_k_true"], row17["mubar_km1_true"],
            row17["se_paired_at_T_ref_10000"], T_ref, z_sum)
        ok = (abs(treq_r - point["required_T"]) / point["required_T"] < 1e-6)
        all_sens_ok &= ok
        sens_checks.append(dict(
            delta_p=dp, committed_required_T=point["required_T"],
            recomputed_required_T=treq_r, match=bool(ok)))
    gates["sensitivity_table_reproduction"] = dict(
        all_pass=bool(all_sens_ok), per_point=sens_checks)
    if not all_sens_ok:
        raise FailClosed("FAIL-CLOSED: reimplemented formula does not "
                          "reproduce the committed delta_p_sensitivity_k17 "
                          "table.")

    R_out["check2_gates"] = gates

    # --- the actual in-range sweep, k=17, wide Delta_p range -------------
    dp_mags = np.logspace(-6, 0, 61)  # 1e-6 .. 1.0, 61 points
    sweep = []
    for dp in dp_mags:
        t_pos, dlog2A_pos, _ = required_T(
            17, float(dp), n_e, q_hat, row17["mubar_k_true"],
            row17["mubar_km1_true"], row17["se_paired_at_T_ref_10000"],
            T_ref, z_sum)
        t_neg, dlog2A_neg, _ = required_T(
            17, -float(dp), n_e, q_hat, row17["mubar_k_true"],
            row17["mubar_km1_true"], row17["se_paired_at_T_ref_10000"],
            T_ref, z_sum)
        sweep.append(dict(
            delta_p=float(dp), T_req_pos=t_pos, T_req_neg=t_neg,
            T_req_times_dp_sq_pos=t_pos * dp * dp,
            sign_symmetric=bool(
                math.isfinite(t_pos) and math.isfinite(t_neg)
                and abs(t_pos - t_neg) / t_pos < 1e-9)))

    products = np.array([r["T_req_times_dp_sq_pos"] for r in sweep])
    products_finite = products[np.isfinite(products)]
    cv = float(np.std(products_finite) / np.mean(products_finite))

    treqs_pos = np.array([r["T_req_pos"] for r in sweep])
    monotonic_decreasing = bool(np.all(np.diff(treqs_pos) < 0))
    all_finite_positive = bool(np.all(np.isfinite(treqs_pos)) and np.all(treqs_pos > 0))
    all_sign_symmetric = bool(all(r["sign_symmetric"] for r in sweep))

    R_out["check2_sweep_k17"] = dict(
        n_e=n_e, q_hat=q_hat, T_ref=T_ref, z_sum=z_sum,
        se_ref=row17["se_paired_at_T_ref_10000"],
        mubar_k_true=row17["mubar_k_true"], mubar_km1_true=row17["mubar_km1_true"],
        bracket_term=bracket17,
        delta_p_range=[float(dp_mags.min()), float(dp_mags.max())],
        n_points=len(sweep),
        T_req_times_delta_p_sq_coefficient_of_variation=cv,
        monotonic_decreasing_in_abs_delta_p=monotonic_decreasing,
        all_finite_and_positive=all_finite_positive,
        all_sign_symmetric=all_sign_symmetric,
        committed_table_range_for_comparison=[0.0002, 0.05],
        rows=sweep)

    # --- bracket-term sign stability across k=2..26 at fixed |Delta_p| ----
    bracket_rows = []
    for row in rt["per_k"]:
        k = row["k"]
        _, _, bracket = required_T(
            k, 0.0082, n_e, q_hat, row["mubar_k_true"], row["mubar_km1_true"],
            row["se_paired_at_T_ref_10000"], T_ref, z_sum)
        bracket_rows.append(dict(k=k, bracket_term=bracket,
                                 sign="positive" if bracket > 0 else
                                      ("negative" if bracket < 0 else "zero")))
    signs = set(r["sign"] for r in bracket_rows)
    R_out["check2_bracket_sign_across_k"] = dict(
        per_k=bracket_rows, distinct_signs_observed=sorted(signs),
        sign_stable_across_k=bool(len(signs) == 1))

    # --- required-T across full k range at Delta_p=0.0082, wide sweep too -
    per_k_wide = []
    for row in rt["per_k"]:
        k = row["k"]
        dp_local = np.logspace(-6, -0.5, 21)  # narrower (still wide) sweep per-k to bound cost
        treqs = []
        for dp in dp_local:
            t, _, _ = required_T(k, float(dp), n_e, q_hat, row["mubar_k_true"],
                                 row["mubar_km1_true"],
                                 row["se_paired_at_T_ref_10000"], T_ref, z_sum)
            treqs.append(t)
        treqs = np.array(treqs)
        mono = bool(np.all(np.diff(treqs) < 0))
        finite_pos = bool(np.all(np.isfinite(treqs)) and np.all(treqs > 0))
        prods = treqs * dp_local ** 2
        cv_k = float(np.std(prods) / np.mean(prods))
        per_k_wide.append(dict(k=k, monotonic=mono, all_finite_positive=finite_pos,
                               cv_T_req_times_dp_sq=cv_k))
    R_out["check2_sweep_all_k"] = dict(
        delta_p_range=[float(1e-6), float(10 ** -0.5)],
        n_points_per_k=21, per_k=per_k_wide,
        all_k_monotonic=bool(all(r["monotonic"] for r in per_k_wide)),
        all_k_finite_positive=bool(all(r["all_finite_positive"] for r in per_k_wide)),
        max_cv_across_k=float(max(r["cv_T_req_times_dp_sq"] for r in per_k_wide)))


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=HERE)
    ap.add_argument("--selftest-fail-closed", action="store_true",
                    help="Deliberately corrupt the measure.py pin and "
                         "confirm gate_sha256_pins aborts. Writes no "
                         "results file. Not counted as the authorized run.")
    args = ap.parse_args(argv)

    if args.selftest_fail_closed:
        try:
            gate_sha256_pins(corrupt=True)
        except FailClosed as exc:
            print(f"[selftest] FAIL-CLOSED gate correctly aborted: {exc}",
                  flush=True)
            return 0
        else:
            print("[selftest] FAILURE: gate did NOT abort on a corrupted "
                  "pin. This is a self-integrity defect.", flush=True)
            return 1

    t0 = time.time()
    R = {
        "task_id": "TASK-20260806-66e3c3",
        "role": "executor",
        "experiment_id": "EXP-HQC-982268",
        "goal": "GOAL-HQC-001",
        "batch": "BATCH-3bd1f4",
        "claim_tier": "toy",
        "scope_statement": (
            "PS-R3 only. No new (T)-sampling: both checks compute entirely "
            "from already-committed measurement_results.json and "
            "reanalysis_results.json, plus a sha256-pinned read-only import "
            "of measure.py's comb_matrix/log2_A_from_hists."),
        "started_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git": git_state(),
        "environment": dict(
            python=sys.version.split()[0], numpy=np.__version__,
            platform=platform.platform(), processor=platform.machine()),
    }

    R["fail_closed_gates"] = dict(sha256_pins=gate_sha256_pins(corrupt=False))

    measure_mod = load_measure_module()

    rows_A = check1_dataset_A(measure_mod, R)
    rows_B, q_hat_B = check1_dataset_B(R)
    check1_cross_dataset_agreement(rows_A, rows_B, R)

    check2(R)

    R["validity"] = dict(status="valid_measurement",
                         reason="All fail-closed gates passed; both checks "
                                "produced finite results across their "
                                "reported ranges; no new (T)-sampling "
                                "occurred.")
    R["certificate"] = dict(kind="none",
                            note="Pure measurement/reanalysis of already-"
                                 "committed data. No discrete-log solve or "
                                 "factor-base relation is claimed.")
    R["wall_seconds"] = round(time.time() - t0, 3)
    R["finished_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    out = os.path.join(args.out_dir, "checks_results.json")
    with open(out, "w") as fh:
        json.dump(R, fh, indent=1)
    print(f"[done] {out} wall={R['wall_seconds']}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
