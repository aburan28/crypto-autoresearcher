#!/usr/bin/env python3
"""PART B -- null-object control on the 2-point local-exponent diagnostic ITSELF.

TASK-20260817-c603c0 (executor) / BATCH-91929e / GOAL-HQC-001 /
EXP-HQC-982268.  Authorized by DEC-20260815-176614.  Pre-registered design in
design.md Section 3, FROZEN BEFORE ANY DATUM WAS GENERATED (the single
exception -- the calibrated constant p, which is by construction a Part A
measurement -- is disclosed in design.md Section 3.2 and anchored by the
design.md sha256 recorded in stdout.log before Part A ran).

NO DECODER CALLS.  Decoder-free, shard-free, defect-free i.i.d. parametric
null object: per-trial S ~ Binomial(n_e=56, p).  Both arms of every synthetic
matched pair are drawn from the IDENTICAL law and differ only in RNG stream.

THE PIPELINE IS THE OBJECT UNDER TEST.  Synthetic arrays are fed through the
SAME mp.arm_hists / sa.evaluable_k / measure.log2_A_from_hists (via
mp.matched_pair_stats) / 2-point-OLS path Part A uses, imported from the same
pinned modules.  No stage is bypassed, shortcut, approximated or
reimplemented; no pinned module is edited.

Claim tier: TOY, hard ceiling.  OBSERVATIONS ONLY.

Re-run:
    PYTHONDONTWRITEBYTECODE=1 python3 null_object_control.py --out-dir .
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import os
import platform
import resource
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *([".."] * 7)))

STAGE_A_PY = os.path.join(
    REPO, "coordination", "goals", "GOAL-HQC-001", "batches", "BATCH-6fddee",
    "tasks", "TASK-20260806-64b506", "stage_a.py")
MEASURE_PY = os.path.join(
    REPO, "coordination", "goals", "GOAL-HQC-001", "batches", "BATCH-0a65c0",
    "tasks", "TASK-20260806-cde749", "measure.py")
MATCHED_PAIR_PY = os.path.join(
    REPO, "coordination", "goals", "GOAL-HQC-001", "batches", "BATCH-412513",
    "tasks", "TASK-20260809-a79e4f", "matched_pair.py")

STAGE_A_PY_EXPECTED_SHA256 = (
    "06a0a618432c00fe26c72ecf05a8d89489db61c5183931fdb76a378717681405")
MEASURE_PY_EXPECTED_SHA256 = (
    "a4fd1ecb63f0ddc83c02ef45f2c65ab31cf13d13e7ae94f500e67465b24f5dc8")
MATCHED_PAIR_PY_EXPECTED_SHA256 = (
    "66266a6178eb46e0b37ec0afdb2620064db56bff82318498e2dd83af1bd1c821")

SET_ID = "PS-R3"
M = 17
K_RANGE_AUTHORIZED = list(range(2, 27))

RUNGS = [5000, 10000, 20000, 40000]
R_PREREGISTERED = 200
G_VALUES = [1.25, 1.5, 2.0]
BASE_SEED = 20260817
PROJECTION_PROBE_REPLICATES = 20
CORE_SECOND_BUDGET = 900.0
PROJECTION_FRACTION = 0.60          # step 1 trigger: > 60% of 900 core-seconds
R_FLOOR = 50
FORCED_ALPHA = 0.5

PART_A_RESULTS = os.path.join(HERE, "cross_regime_arms_results.json")


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def core_seconds() -> float:
    a = resource.getrusage(resource.RUSAGE_SELF)
    b = resource.getrusage(resource.RUSAGE_CHILDREN)
    return a.ru_utime + a.ru_stime + b.ru_utime + b.ru_stime


def git_state():
    def run(*a):
        try:
            return subprocess.run(a, cwd=REPO, capture_output=True, text=True,
                                  timeout=60).stdout.strip()
        except Exception as exc:                                  # noqa: BLE001
            return f"<unavailable: {exc}>"
    porcelain = run("git", "status", "--porcelain")
    return dict(commit=run("git", "rev-parse", "HEAD"),
                branch=run("git", "rev-parse", "--abbrev-ref", "HEAD"),
                dirty=bool(porcelain), dirty_paths=porcelain.splitlines()[:60])


def load_module_fail_closed(path, expected_sha256, name, module_name):
    actual = sha256_file(path)
    if actual != expected_sha256:
        raise SystemExit(
            f"FAIL-CLOSED: {name} sha256 mismatch. expected={expected_sha256} "
            f"actual={actual}.")
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, actual


def log(m):
    print(m, flush=True)


def rng_for(T, r, arm, leg_code):
    return np.random.Generator(np.random.PCG64(
        np.random.SeedSequence([BASE_SEED, T, r, arm, leg_code])))


def round_half_away(x):
    return np.floor(np.abs(x) + 0.5) * np.sign(x)


def plant(S, mu, g, n_e):
    return np.clip(round_half_away(mu + g * (S.astype(np.float64) - mu)),
                   0, n_e).astype(np.int64)


def pct(a, q):
    return float(np.percentile(np.asarray(a, dtype=np.float64), q))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=HERE)
    args = ap.parse_args(argv)
    t0, c0 = time.time(), core_seconds()

    mp, mp_sha = load_module_fail_closed(
        MATCHED_PAIR_PY, MATCHED_PAIR_PY_EXPECTED_SHA256, "matched_pair.py",
        "matched_pair_frozen_c603c0_B")
    sa, sa_sha = load_module_fail_closed(
        STAGE_A_PY, STAGE_A_PY_EXPECTED_SHA256, "stage_a.py",
        "stage_a_frozen_c603c0_B")
    measure, me_sha = load_module_fail_closed(
        MEASURE_PY, MEASURE_PY_EXPECTED_SHA256, "measure.py",
        "measure_frozen_c603c0_B")

    selftests = {
        "sha256_pin_mismatch": mp.selftest_fail_closed_sha_mismatch()}
    ps = [p for p in sa.PARAM_SETS if p["id"] == SET_ID][0]
    n_e, n_2 = ps["n_e"], ps["n_2"]
    selftests["injection_invariant_mismatch"] = (
        mp.selftest_injection_invariant_fail(n_e, n_2))
    for name, v in selftests.items():
        log(f"[selftest] {name}: {v['verdict']}")
        if v["verdict"] != "PASS":
            raise SystemExit(f"FAILED_IMPLEMENTATION: selftest {name} not PASS.")

    NB = sa.N_JACK_BATCHES

    with open(PART_A_RESULTS) as fh:
        partA = json.load(fh)
    calib = partA["part_b_p_calibration_input"]
    p = calib["p"]
    mean_S_real = calib["mean_per_trial_S_real_undefected_5000_P2"]
    mu = n_e * p
    log(f"[calibration] p={p!r} (frozen) from mean S={mean_S_real} at "
        f"shard 5000 window P2 [35000:45000)")

    B = {
        "task_id": "TASK-20260817-c603c0", "role": "executor", "part": "B",
        "experiment_id": "EXP-HQC-982268", "hypothesis_id": "H-HQC-18d1b4",
        "goal": "GOAL-HQC-001", "batch": "BATCH-91929e",
        "authorized_by": "DEC-20260815-176614", "claim_tier": "toy",
        "what_this_is": (
            "A null-object control ON THE 2-POINT LOCAL-EXPONENT DIAGNOSTIC "
            "ITSELF. Decoder-free, shard-free, defect-free. The pipeline is the "
            "object under test; no stage is bypassed or reimplemented. "
            "OBSERVATIONS ONLY -- no reading rule is applied here."),
        "scope_statement": (
            "TOY, hard ceiling. No decoder call is made in this script and no "
            "cryptographic object is touched. Nothing here is a statement about "
            "HQC, A17, A5, any decoding-failure rate, or any standardized "
            "parameter set."),
        "design_reference": "design.md Section 3, frozen before this run",
        "started_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "command": " ".join([sys.executable] + sys.argv),
        "git": git_state(),
        "environment": dict(python=sys.version, platform=platform.platform(),
                            machine=platform.machine(), numpy=np.__version__,
                            cpu_count=os.cpu_count()),
        "provenance": dict(
            stage_a_sha256=sa_sha, measure_sha256=me_sha,
            matched_pair_py_sha256=mp_sha,
            stage_a_sha256_match=(sa_sha == STAGE_A_PY_EXPECTED_SHA256),
            measure_sha256_match=(me_sha == MEASURE_PY_EXPECTED_SHA256),
            matched_pair_py_sha256_match=(mp_sha == MATCHED_PAIR_PY_EXPECTED_SHA256),
            part_a_results_sha256=sha256_file(PART_A_RESULTS),
            design_md_sha256_at_part_b_launch=sha256_file(
                os.path.join(HERE, "design.md")),
            bootstrap_utility_functions_note=(
                "sha256_file, core_seconds, git_state and "
                "load_module_fail_closed are LOCALLY RE-DEFINED (the disclosed "
                "chicken-and-egg exception, EV-HQC-469c08 O10); arm_hists, "
                "matched_pair_stats, cell and both selftests ARE imported via "
                "mp.*, and evaluable_k / hist_of / batch_hists via sa.*, "
                "comb_matrix / log2_A_from_hists via measure.*.")),
        "fail_closed_selftests": selftests,
        "parameter_set": {k: ps[k] for k in ("id", "n", "n_e", "n_2", "dup", "N")},
        "null_object": dict(
            law="S ~ Binomial(n_e=56, p), i.e. the sum of 56 i.i.d. Bernoulli(p) block indicators",
            p_frozen=p, mean_S_real_undefected_shard5000_P2=mean_S_real,
            mu=mu, n_e=n_e,
            calibration_rule=calib["rule"],
            both_arms_identical_law=True,
            arms_differ_only_in_rng_stream=True,
            rng=("numpy.random.Generator(PCG64(SeedSequence([20260817, T, r, "
                 "arm, leg_code]))); arm in {0,1}; leg_code 0 = unmodified "
                 "ladder, 1+i = sensitivity leg for G_VALUES[i]"),
            n_jack_batches=NB),
        "forced_values": {
            "forced_value_1_log2_A_k": "0 EXACTLY at every k, per arm (A_k = 1 is a theorem on the independent-block null)",
            "forced_value_2_paired_diff": "0 EXACTLY at every k",
            "forced_value_3_local_exponent_alpha": 0.5,
            "honest_caveat": (
                "The T^(-1/2) law is exact only asymptotically, with an "
                "O(T^(-1)) finite-T correction. That is why the ladder is run AT "
                "the same T values and batch sizes as the real arms rather than "
                "asserting 0.5 from theory: the measured centre of the replicate "
                "distribution quantifies the finite-T bias and its spread is the "
                "noise floor.")},
        "pipeline_acceptance": dict(
            stages_used=["mp.arm_hists (-> sa.hist_of, sa.batch_hists)",
                         "sa.evaluable_k", "measure.comb_matrix",
                         "mp.matched_pair_stats (-> measure.log2_A_from_hists)",
                         "2-point OLS-in-log-log slope, identical to Part A"],
            any_stage_bypassed_shortcut_or_reimplemented=False,
            any_pinned_module_edited=False,
            note=("Every stage accepted synthetic int64 per-trial S arrays "
                  "without modification. Had any stage refused, this run would "
                  "have STOPPED and reported that as a finding.")),
    }

    def replicate(T, r, leg_code=0, g=None):
        """ONE synthetic matched pair through the REAL pipeline."""
        S0 = rng_for(T, r, 0, 0).binomial(n_e, p, size=T).astype(np.int64)
        S1 = rng_for(T, r, 1, 0).binomial(n_e, p, size=T).astype(np.int64)
        if g is not None:
            S1 = plant(S1, mu, g, n_e)
        H0, B0 = mp.arm_hists(sa, S0, n_e, NB)
        H1, B1 = mp.arm_hists(sa, S1, n_e, NB)
        ks = sorted(set(sa.evaluable_k(H0, n_e)) & set(sa.evaluable_k(H1, n_e))
                    & set(K_RANGE_AUTHORIZED))
        st = mp.matched_pair_stats(measure, n_e, ks,
                                   measure.comb_matrix(n_e, ks),
                                   H0, B0, H1, B1)
        return st, ks

    # ---- PHASE 1: cost projection probe on the T=40000 rung --------------
    probe_c0 = core_seconds()
    probe_w0 = time.time()
    probe_store = []
    for r in range(PROJECTION_PROBE_REPLICATES):
        probe_store.append(replicate(40000, r))
    probe_core = core_seconds() - probe_c0
    probe_wall = time.time() - probe_w0
    per_rep_40000_core = probe_core / PROJECTION_PROBE_REPLICATES
    unit_core_per_trial = per_rep_40000_core / 40000.0
    ladder_trial_units = sum(RUNGS)
    sens_trial_units = len(G_VALUES) * 20000
    total_units = ladder_trial_units + sens_trial_units
    projected_total_core = R_PREREGISTERED * unit_core_per_trial * total_units
    threshold = PROJECTION_FRACTION * CORE_SECOND_BUDGET

    reduction = dict(no_reduction_fired=True, step_1_fired=False,
                     step_2_fired=False, step_3_fired=False)
    R_used = R_PREREGISTERED
    rungs_used = list(RUNGS)
    if projected_total_core > threshold:
        reduction["step_1_fired"] = True
        reduction["no_reduction_fired"] = False
        per_rep_all = unit_core_per_trial * total_units
        R_fit = int(math.floor((threshold / per_rep_all) / 50.0) * 50)
        R_used = max(R_FLOOR, R_fit)
        reduction["step_1_R_fit"] = R_fit
        if R_fit < R_FLOOR:
            reduction["step_2_fired"] = True
            R_used = R_PREREGISTERED
            rungs_used = [t for t in RUNGS if t != 40000]
            units2 = sum(rungs_used) + sens_trial_units
            reproj = R_used * unit_core_per_trial * units2
            reduction["step_2_reprojected_core_seconds"] = reproj
            if reproj > threshold:
                reduction["step_3_fired"] = True
                reduction["underpowered"] = True
    reduction["achieved_R"] = R_used
    reduction["achieved_rungs"] = rungs_used

    cost_projection = dict(
        task_id="TASK-20260817-c603c0", part="B",
        protocol="design.md Section 3.7, applied in order, never improvised",
        written_unconditionally=True,
        trigger=("after the first 20 replicates of the T=40000 rung, project "
                 "total Part B cost from measured per-replicate cost"),
        probe=dict(rung_T=40000, replicates=PROJECTION_PROBE_REPLICATES,
                   measured_core_seconds=round(probe_core, 6),
                   measured_wall_seconds=round(probe_wall, 6),
                   core_seconds_per_replicate=per_rep_40000_core),
        arithmetic=dict(
            unit_core_seconds_per_trial=unit_core_per_trial,
            ladder_trial_units_per_replicate=ladder_trial_units,
            sensitivity_trial_units_per_replicate=sens_trial_units,
            total_trial_units_per_replicate=total_units,
            R_preregistered=R_PREREGISTERED,
            projected_total_core_seconds=projected_total_core,
            core_second_authorization=CORE_SECOND_BUDGET,
            threshold_60_percent=threshold,
            projection_exceeds_threshold=bool(projected_total_core > threshold),
            formula=("projected = R * (core_seconds_per_replicate_at_40000 / "
                     "40000) * (5000 + 10000 + 20000 + 40000 + 3*20000)")),
        decision=reduction,
        underpowered=bool(reduction.get("underpowered", False)),
        underpowered_note=(
            "If underpowered were true, Part B's band would NOT be presented as "
            "a calibration."))
    with open(os.path.join(args.out_dir, "cost_projection.json"), "w") as fh:
        json.dump(cost_projection, fh, indent=1)
    log(f"[cost_projection] projected_core={projected_total_core:.3f}s "
        f"threshold={threshold}s no_reduction_fired={reduction['no_reduction_fired']} "
        f"R={R_used} rungs={rungs_used}")

    # ---- PHASE 2: the ladder ---------------------------------------------
    per_rung = {}
    se17 = {}
    csv_rows = []
    for T in rungs_used:
        se_list, diff17, logA0, logA1, diffs = [], [], [], [], []
        ks_variants = []
        for r in range(R_used):
            if T == 40000 and r < len(probe_store):
                st, ks = probe_store[r]
            else:
                st, ks = replicate(T, r)
            if ks not in ks_variants:
                ks_variants.append(ks)
            j = st["ks"].index(M)
            se_list.append(st["se_paired"][j])
            diff17.append(st["diff"][j])
            logA0.append(st["point_defected"])
            logA1.append(st["point_undefected"])
            diffs.append(st["diff"])
        se17[T] = se_list
        # evaluable_k is by construction a contiguous run starting at k=2, so
        # the common evaluable range across replicates is the shortest one.
        # If replicates differ, that is REPORTED, not repaired.
        ncommon = min(len(x) for x in logA0)
        ks_common = sorted(ks_variants, key=len)[0]
        def _arr(rows):
            return np.array([[np.nan if v is None else v for v in x[:ncommon]]
                             for x in rows], dtype=np.float64)
        A0, A1, DF = _arr(logA0), _arr(logA1), _arr(diffs)
        per_rung[str(T)] = dict(
            T=T, jack_batch_size=T // NB, n_batches=NB, replicates=R_used,
            evaluable_k_attained_common=ks_common,
            evaluable_k_distinct_variants_across_replicates=ks_variants,
            evaluable_k_identical_across_all_replicates=(len(ks_variants) == 1),
            evaluable_k_covers_2_to_26=(ks_common == K_RANGE_AUTHORIZED),
            by_k_summaries_are_over=ks_common,
            forced_value_1_log2_A_k_vs_zero=dict(
                forced=0.0,
                arm0_mean_by_k=[float(x) for x in np.nanmean(A0,axis=0)],
                arm1_mean_by_k=[float(x) for x in np.nanmean(A1,axis=0)],
                arm0_sd_by_k=[float(x) for x in np.nanstd(A0,axis=0,ddof=1)],
                arm1_sd_by_k=[float(x) for x in np.nanstd(A1,axis=0,ddof=1)],
                arm0_max_abs_deviation_from_zero=float(np.nanmax(np.abs(A0))),
                arm1_max_abs_deviation_from_zero=float(np.nanmax(np.abs(A1))),
                arm0_mean_abs_deviation_by_k=[float(x) for x in np.nanmean(np.abs(A0),axis=0)],
                arm1_mean_abs_deviation_by_k=[float(x) for x in np.nanmean(np.abs(A1),axis=0)],
                note=("The measured deviation from 0 at every k IS the direct, "
                      "decoder-free test of whether log2_A_from_hists carries a "
                      "batch-size-dependent bias.")),
            forced_value_2_paired_diff_vs_zero=dict(
                forced=0.0,
                mean_by_k=[float(x) for x in np.nanmean(DF,axis=0)],
                sd_by_k=[float(x) for x in np.nanstd(DF,axis=0,ddof=1)],
                max_abs_deviation_from_zero=float(np.nanmax(np.abs(DF))),
                mean_abs_deviation_by_k=[float(x) for x in np.nanmean(np.abs(DF),axis=0)],
                at_k17=dict(mean=float(np.mean(diff17)),
                            sd=float(np.std(diff17, ddof=1)),
                            max_abs=float(np.max(np.abs(diff17))))),
            se_paired_k17=dict(mean=float(np.mean(se_list)),
                               sd=float(np.std(se_list, ddof=1)),
                               p2_5=pct(se_list, 2.5), p50=pct(se_list, 50),
                               p97_5=pct(se_list, 97.5)))
        log(f"[rung] T={T} done R={R_used} se17_mean={np.mean(se_list):.6g}")

    # ---- adjacent rung-pair 2-point exponents ----------------------------
    pairs = [(rungs_used[i], rungs_used[i + 1]) for i in range(len(rungs_used) - 1)]
    pair_stats = {}
    alpha_by_pair = {}
    for (tlo, thi) in pairs:
        a = []
        for r in range(R_used):
            lo, hi = se17[tlo][r], se17[thi][r]
            al = -(math.log(hi) - math.log(lo)) / (math.log(thi) - math.log(tlo))
            a.append(al)
            csv_rows.append(dict(leg="unmodified_null", g="",
                                 rung_pair=f"{tlo}->{thi}", replicate=r,
                                 T_lo=tlo, T_hi=thi, se_paired_k17_lo=lo,
                                 se_paired_k17_hi=hi, alpha=al))
        alpha_by_pair[(tlo, thi)] = a
        pair_stats[f"{tlo}->{thi}"] = dict(
            T_lo=tlo, T_hi=thi,
            jack_batch_size_lo=tlo // NB, jack_batch_size_hi=thi // NB,
            batch_size_transition=f"{tlo // NB}->{thi // NB}",
            is_regime_P=(tlo // NB == 25 and thi // NB == 50),
            is_regime_N=(tlo // NB == 50 and thi // NB == 100),
            replicates=R_used, forced_alpha=FORCED_ALPHA,
            mean=float(np.mean(a)), sd=float(np.std(a, ddof=1)),
            p2_5=pct(a, 2.5), p50=pct(a, 50), p97_5=pct(a, 97.5),
            null_95_band=[pct(a, 2.5), pct(a, 97.5)],
            mean_minus_forced=float(np.mean(a) - FORCED_ALPHA),
            median_minus_forced=float(pct(a, 50) - FORCED_ALPHA),
            forced_value_inside_null_95_band=bool(
                pct(a, 2.5) <= FORCED_ALPHA <= pct(a, 97.5)))
    B["ladder_rungs"] = per_rung
    B["adjacent_rung_pair_alpha_distributions"] = pair_stats

    # ---- the two contested regimes compared, decoder-free ----------------
    key_P, key_N = "5000->10000", "10000->20000"
    if key_P in pair_stats and key_N in pair_stats:
        aP = alpha_by_pair[(5000, 10000)]
        aN = alpha_by_pair[(10000, 20000)]
        B["contested_regime_comparison_on_the_null_object"] = dict(
            what=("REQUIRED DELIVERABLE. A decoder-free, shard-free, "
                  "defect-free comparison of the null object's own alpha "
                  "distribution at rung pair 5000->10000 (batch 25->50, "
                  "regime P exactly) against 10000->20000 (batch 50->100, "
                  "regime N exactly)."),
            regime_P_5000_to_10000=pair_stats[key_P],
            regime_N_10000_to_20000=pair_stats[key_N],
            difference_of_means=float(np.mean(aP) - np.mean(aN)),
            difference_of_medians=float(pct(aP, 50) - pct(aN, 50)),
            paired_by_replicate_mean_difference=float(
                np.mean(np.array(aP) - np.array(aN))),
            paired_by_replicate_sd=float(np.std(np.array(aP) - np.array(aN), ddof=1)),
            regime_N_median_inside_regime_P_null_band=bool(
                pair_stats[key_P]["p2_5"] <= pct(aN, 50) <= pair_stats[key_P]["p97_5"]),
            regime_P_median_inside_regime_N_null_band=bool(
                pair_stats[key_N]["p2_5"] <= pct(aP, 50) <= pair_stats[key_N]["p97_5"]),
            observation_only_note=(
                "Reported as measured. No conclusion is drawn here about "
                "whether the confound is a property of the instrument."))

    # ---- four-rung full-ladder OLS ---------------------------------------
    if len(rungs_used) >= 3:
        logT = np.log(np.array(rungs_used, dtype=np.float64))
        full_alpha, resid_rms = [], []
        for r in range(R_used):
            y = np.log(np.array([se17[T][r] for T in rungs_used]))
            slope, intercept = np.polyfit(logT, y, 1)
            full_alpha.append(-float(slope))
            resid_rms.append(float(np.sqrt(np.mean((y - (slope * logT + intercept)) ** 2))))
        scatter = {}
        for (tlo, thi) in pairs:
            d = np.array(alpha_by_pair[(tlo, thi)]) - np.array(full_alpha)
            scatter[f"{tlo}->{thi}"] = dict(
                mean_2point_minus_fullladder=float(np.mean(d)),
                sd=float(np.std(d, ddof=1)),
                rms=float(np.sqrt(np.mean(d ** 2))))
        B["full_ladder_fit"] = dict(
            rungs=rungs_used, points_per_fit=len(rungs_used),
            residual_degrees_of_freedom=len(rungs_used) - 2,
            method="numpy.polyfit(log(T), log(se_paired_k17), 1); alpha = -slope",
            forced_alpha=FORCED_ALPHA, replicates=R_used,
            alpha_mean=float(np.mean(full_alpha)),
            alpha_sd=float(np.std(full_alpha, ddof=1)),
            alpha_p2_5=pct(full_alpha, 2.5), alpha_p50=pct(full_alpha, 50),
            alpha_p97_5=pct(full_alpha, 97.5),
            alpha_mean_minus_forced=float(np.mean(full_alpha) - FORCED_ALPHA),
            fit_residual_rms_mean=float(np.mean(resid_rms)),
            scatter_of_2point_estimates_about_the_full_ladder_line=scatter,
            note=("The scatter of the 2-point estimates about this "
                  "well-determined line IS the calibration of the diagnostic in "
                  "question."))

    # ---- PHASE 3: sensitivity / anti-blindness leg -----------------------
    sens = {}
    null_band_N = pair_stats[key_N]["null_95_band"] if key_N in pair_stats else None
    any_out_of_band = False
    if 20000 in rungs_used and 10000 in rungs_used:
        for gi, g in enumerate(G_VALUES):
            rho, a_planted, resid = [], [], []
            for r in range(R_used):
                st, _ks = replicate(20000, r, leg_code=1 + gi, g=g)
                j = st["ks"].index(M)
                se_pl = st["se_paired"][j]
                se_un = se17[20000][r]
                rg = se_pl / se_un
                al_pl = -(math.log(se_pl) - math.log(se17[10000][r])) / math.log(2.0)
                al_un = alpha_by_pair[(10000, 20000)][r]
                rho.append(rg)
                a_planted.append(al_pl)
                resid.append(al_pl - (al_un - math.log2(rg)))
                csv_rows.append(dict(leg="planted", g=g,
                                     rung_pair="10000->20000", replicate=r,
                                     T_lo=10000, T_hi=20000,
                                     se_paired_k17_lo=se17[10000][r],
                                     se_paired_k17_hi=se_pl, alpha=al_pl))
            med = pct(a_planted, 50)
            out = not (null_band_N[0] <= med <= null_band_N[1])
            frac_out = float(np.mean([(x < null_band_N[0]) or (x > null_band_N[1])
                                      for x in a_planted]))
            any_out_of_band |= out
            sens[str(g)] = dict(
                g=g, rung="T=20000, arm B dispersion-scaled",
                construction=("S_planted = clip(round_half_away_from_zero(mu + "
                              "g*(S_base - mu)), 0, n_e), mu = n_e*p; arm A "
                              "unchanged; same replicate seeds"),
                replicates=R_used,
                rho_g_measured=dict(mean=float(np.mean(rho)),
                                    sd=float(np.std(rho, ddof=1)),
                                    p50=pct(rho, 50), p2_5=pct(rho, 2.5),
                                    p97_5=pct(rho, 97.5),
                                    note="MEASURED, never predicted"),
                alpha_planted=dict(mean=float(np.mean(a_planted)),
                                   sd=float(np.std(a_planted, ddof=1)),
                                   p2_5=pct(a_planted, 2.5),
                                   p50=med, p97_5=pct(a_planted, 97.5)),
                forced_identity=dict(
                    statement=("alpha_planted(10000 unmodified -> 20000 planted) "
                               "= alpha_unmodified(10000->20000) - log2(rho_g), "
                               "exactly, since log2(20000/10000) = 1"),
                    checked="per replicate, with MEASURED rho_g",
                    residual_mean_abs=float(np.mean(np.abs(resid))),
                    residual_max_abs=float(np.max(np.abs(resid)))),
                unmodified_null_95_band=null_band_N,
                planted_median=med,
                verdict="OUT_OF_BAND" if out else "IN_BAND",
                fraction_of_planted_replicates_outside_null_band=frac_out)
            log(f"[sensitivity] g={g} rho={np.mean(rho):.6g} "
                f"median_alpha={med:.6g} verdict={'OUT_OF_BAND' if out else 'IN_BAND'}")
    B["sensitivity_leg"] = dict(
        g_values=G_VALUES, per_g=sens,
        preregistered_verdict_rule=(
            "OUT_OF_BAND iff the planted alpha distribution's MEDIAN lies "
            "outside the unmodified null 95% band ([2.5, 97.5] percentiles) at "
            "rung pair 10000->20000."),
        any_g_out_of_band=bool(any_out_of_band),
        blindness_verdict=("NOT_BLIND" if any_out_of_band else "BLIND"),
        fail_closed_blindness_rule=(
            "If NO g produces a planted alpha distribution lying outside the "
            "unmodified null 95% band, the null-object control is reported "
            "BLIND and its null band carries NO interpretive weight at the "
            "ledger archive. That is a finding, not a failure to route around."),
        scope=("ONE planted departure class only: dispersion scaling of one arm "
               "at one rung. A control shown non-blind to that class is not "
               "thereby shown non-blind to any other."))

    # ---- CSV -------------------------------------------------------------
    csv_path = os.path.join(args.out_dir, "noc_replicate_summary.csv")
    with open(csv_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["leg", "g", "rung_pair", "replicate",
                                           "T_lo", "T_hi", "se_paired_k17_lo",
                                           "se_paired_k17_hi", "alpha"])
        w.writeheader()
        for row in csv_rows:
            w.writerow(row)

    spent_core, spent_wall = core_seconds() - c0, time.time() - t0
    B["achieved"] = dict(R_preregistered=R_PREREGISTERED, R_achieved=R_used,
                         rungs_preregistered=RUNGS, rungs_achieved=rungs_used,
                         reduction_protocol_fired=not reduction["no_reduction_fired"],
                         underpowered=bool(reduction.get("underpowered", False)))
    B["budget"] = dict(core_seconds_authorized=CORE_SECOND_BUDGET,
                       core_seconds_spent_part_B=round(spent_core, 3),
                       wall_seconds_spent_part_B=round(spent_wall, 3),
                       measured_not_estimated=True)
    all_finite = all(np.isfinite(se17[T]).all() and (np.array(se17[T]) > 0).all()
                     for T in rungs_used)
    B["validity"] = dict(
        status="valid_measurement" if all_finite else "invalid_measurement",
        failure_class=(None if all_finite else "invalid_measurement"),
        every_replicate_finite_positive_se_paired_k17=bool(all_finite),
        pipeline_accepted_synthetic_input_unmodified=True,
        note=("A BLIND verdict on the sensitivity leg does NOT make Part B "
              "invalid -- it is a recorded finding that bounds how the band may "
              "be used."))
    B["finished_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    out = os.path.join(args.out_dir, "null_object_control_results.json")
    with open(out, "w") as fh:
        json.dump(B, fh, indent=1)
    log(f"[done] PART B -> {out}  core-s={spent_core:.2f} wall={spent_wall:.1f}s "
        f"validity={B['validity']['status']} "
        f"blindness={B['sensitivity_leg']['blindness_verdict']}")
    return B


if __name__ == "__main__":
    main()
