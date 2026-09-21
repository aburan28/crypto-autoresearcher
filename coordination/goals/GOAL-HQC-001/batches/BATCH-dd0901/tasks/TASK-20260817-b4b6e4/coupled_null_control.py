#!/usr/bin/env python3
"""PART B -- the COUPLED-ARM null band on the 2-point local-exponent diagnostic.

TASK-20260817-b4b6e4 (executor) / BATCH-dd0901 / GOAL-HQC-001 /
EXP-HQC-982268 / H-HQC-18d1b4 (stays PROPOSED).
Authorized by DEC-20260817-2b638b.  Pre-registered design: design.md section 3,
CLOSED BEFORE THIS RUN; its sha256 is measured here at launch.

EXACTLY ONE STRUCTURAL CHANGE from BATCH-91929e's Part B
(null_object_control.py:256-257, which drew the two arms from INDEPENDENT
streams):

    base   ~ Binomial(n_e - 1 = 55, p)      per trial, SHARED by both arms
    arm_i  =  base + Bernoulli_i(p)         independent Bernoulli per arm

Each arm's marginal law is Binomial(56, p) EXACTLY, so any change in the band
is attributable to the coupling alone.  p is FROZEN at 0.31923392857142857 and
is NOT re-calibrated here.

ZERO DECODER CALLS, ENFORCED FAIL-CLOSED.  stage_a.py is imported (matched_pair
imports it) but nothing in it is called: call-counting wrappers that ABORT on
invocation are installed on the LOADED module objects' `_t_shard` and
`decode_blocks`, both counters are asserted 0 at exit, and all three module
sha256 pins are re-verified ON DISK at exit.  No file on disk is edited.

Claim tier: TOY, hard ceiling.  OBSERVATIONS ONLY -- the two blindness tests are
reported as PASS/FAIL and the control is declared BLIND in no verdict sense; no
branch of batch.yaml's frozen reading rule is applied or named.

Re-run:
    PYTHONDONTWRITEBYTECODE=1 python3 coupled_null_control.py --out-dir .
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import inspect
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

PART_A_RESULTS = os.path.join(HERE, "low_k_recompute_results.json")

SET_ID = "PS-R3"
M = 17
K_RANGE_AUTHORIZED = list(range(2, 27))
K_REPORTED = [5, 10, 17]

P_FROZEN = 0.31923392857142857
RUNGS = [5000, 10000, 20000, 40000]
R_PREREGISTERED = 200
BASE_SEED = 20260817
PROJECTION_PROBE_REPLICATES = 20
CORE_SECOND_BUDGET = 150.0
PROJECTION_FRACTION = 0.60
R_FLOOR = 100
FORCED_ALPHA = 0.5

# five independent null cell streams (design.md section 3.4)
CELL_STREAMS = {0: "cell_5000_P", 1: "cell_5000_N",
                2: "cell_8002_P", 3: "cell_8002_N",
                4: "replication_partner_of_cell_5000_P"}
ANALYTIC_SD_FACTORS = {"single_cell_alpha": 1.000,
                       "regime_main_effect": 1.000,
                       "shard_main_effect": 1.000,
                       "interaction": 2.000,
                       "replication_delta": 1.414}
POWER_MDE_THRESHOLD = 3.702

DECODER_CALL_COUNTERS = {"stage_a._t_shard": 0, "stage_a.decode_blocks": 0}


# ---- locally re-defined bootstrap utilities ------------------------------
# DISCLOSED IN THE SAME BULLET AS THE REUSE CLAIM (design.md section 3.2):
# arm_hists, matched_pair_stats, evaluable_k, comb_matrix, log2_A_from_hists
# and both fail-closed selftests ARE imported from the pinned modules and are
# never re-derived.  Only the bootstrap utilities below must be re-defined,
# because matched_pair.py's own loader cannot be used to load matched_pair.py
# (the chicken-and-egg exception EV-HQC-469c08 O10 recorded).  They are
# verified byte-identical to the pinned originals at run time, and measure.py
# and stage_a.py are then loaded with mp.load_module itself, not with the copy.

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
                dirty=bool(porcelain), dirty_paths=porcelain.splitlines()[:40])


def load_module_bootstrap(path, expected_sha256, name, module_name):
    """Bootstrap-only copy of matched_pair.load_module, used ONCE to load
    matched_pair.py itself.  Everything else uses mp.load_module."""
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


def pct(a, q):
    return float(np.percentile(np.asarray(a, dtype=np.float64), q))


def install_decoder_tripwires(sa):
    """Call-counting wrappers on the LOADED module object only.  No file on
    disk is touched.  A call ABORTS -- it never delegates."""
    installed = {}
    for attr in ("_t_shard", "decode_blocks"):
        key = f"stage_a.{attr}"
        if not hasattr(sa, attr):
            installed[key] = "ATTRIBUTE_ABSENT"
            continue
        original = getattr(sa, attr)

        def make(k, orig):
            def tripwire(*a, **kw):
                DECODER_CALL_COUNTERS[k] += 1
                raise SystemExit(
                    f"INFRASTRUCTURE ABORT: {k} was CALLED. This task is "
                    f"authorized for ZERO decoder calls (AGENTS.md rule 5). "
                    f"Counter={DECODER_CALL_COUNTERS[k]}. No result is "
                    f"reported from this run.")
            tripwire.__wrapped_decoder_entry_point__ = k
            tripwire.__original_id__ = id(orig)
            return tripwire
        setattr(sa, attr, make(key, original))
        installed[key] = "TRIPWIRE_INSTALLED"
    return installed


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=HERE)
    args = ap.parse_args(argv)
    t0, c0 = time.time(), core_seconds()

    design_sha = sha256_file(os.path.join(HERE, "design.md"))
    log(f"[preregistration] design.md sha256 measured at launch = {design_sha}")
    log("[preregistration] NOT independently anchored (this session does not "
        "commit); content corroboration only.")

    # ---- fail-closed load + tripwires --------------------------------------
    mp, mp_sha = load_module_bootstrap(
        MATCHED_PAIR_PY, MATCHED_PAIR_PY_EXPECTED_SHA256, "matched_pair.py",
        "matched_pair_frozen_b4b6e4")
    sa, sa_sha = mp.load_module(
        STAGE_A_PY, STAGE_A_PY_EXPECTED_SHA256, "stage_a.py",
        "stage_a_frozen_b4b6e4")
    measure, me_sha = mp.load_module(
        MEASURE_PY, MEASURE_PY_EXPECTED_SHA256, "measure.py",
        "measure_frozen_b4b6e4")
    tripwires = install_decoder_tripwires(sa)
    log(f"[tripwire] {tripwires}")

    # byte-identical check of the locally re-defined bootstrap utilities
    local_copy_check = {}
    for fn_name, local_fn in (("sha256_file", sha256_file),
                              ("core_seconds", core_seconds),
                              ("git_state", git_state)):
        try:
            same = (inspect.getsource(local_fn)
                    == inspect.getsource(getattr(mp, fn_name)))
        except Exception as exc:                                  # noqa: BLE001
            same = f"<unavailable: {exc}>"
        local_copy_check[fn_name] = same
    local_copy_check["load_module"] = (
        "NOT byte-identical by necessity: load_module_bootstrap is a reduced "
        "bootstrap copy used ONCE to load matched_pair.py itself. stage_a.py "
        "and measure.py are loaded with mp.load_module, the pinned original.")
    log(f"[reuse] locally re-defined bootstrap utilities byte-identical: "
        f"{ {k: v for k, v in local_copy_check.items() if k != 'load_module'} }")

    selftests = {"sha256_pin_mismatch": mp.selftest_fail_closed_sha_mismatch()}
    ps = [p for p in sa.PARAM_SETS if p["id"] == SET_ID][0]
    n_e, n_2 = ps["n_e"], ps["n_2"]
    selftests["injection_invariant_mismatch"] = (
        mp.selftest_injection_invariant_fail(n_e, n_2))
    for name, v in selftests.items():
        log(f"[selftest] {name}: {v['verdict']}")
        if v["verdict"] != "PASS":
            raise SystemExit(f"FAILED_IMPLEMENTATION: selftest {name} not PASS.")
    NB = sa.N_JACK_BATCHES

    partA = json.load(open(PART_A_RESULTS))
    real_uop = partA["eight_real_cells_unpaired_over_paired_by_k"]

    B = {
        "task_id": "TASK-20260817-b4b6e4", "role": "executor", "part": "B",
        "experiment_id": "EXP-HQC-982268", "hypothesis_id": "H-HQC-18d1b4",
        "goal": "GOAL-HQC-001", "batch": "BATCH-dd0901",
        "authorized_by": "DEC-20260817-2b638b", "claim_tier": "toy",
        "what_this_is": (
            "The COUPLED-ARM null band. BATCH-91929e's null drew both arms "
            "from independent streams; both of its independent reviewers "
            "showed that was the wrong shape. This is the correction, with "
            "EXACTLY ONE structural change and nothing else touched."),
        "scope_statement": (
            "TOY, hard ceiling. No decoder call is made and no cryptographic "
            "object is touched. Nothing here is a statement about HQC's "
            "IND-CCA security, its DFR, assumption A17 or A5, or any "
            "standardized parameter set."),
        "observations_only_note": (
            "The two blindness tests are reported as PASS/FAIL. The executor "
            "declares the control BLIND in NO verdict sense, applies no branch "
            "of batch.yaml's frozen reading rule, and concludes nothing."),
        "preregistration": dict(
            design_md_sha256_at_launch=design_sha,
            independently_anchored=False,
            anchoring_claim="content corroboration only"),
        "design_reference": "design.md section 3, closed before this run",
        "started_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "command": " ".join([sys.executable] + sys.argv),
        "git": git_state(),
        "environment": dict(python=sys.version, python_executable=sys.executable,
                            platform=platform.platform(),
                            machine=platform.machine(), numpy=np.__version__,
                            cpu_count=os.cpu_count()),
        "provenance": dict(
            stage_a_path=os.path.relpath(STAGE_A_PY, REPO), stage_a_sha256_at_load=sa_sha,
            measure_path=os.path.relpath(MEASURE_PY, REPO), measure_sha256_at_load=me_sha,
            matched_pair_py_path=os.path.relpath(MATCHED_PAIR_PY, REPO),
            matched_pair_py_sha256_at_load=mp_sha,
            all_pins_match_at_load=bool(
                sa_sha == STAGE_A_PY_EXPECTED_SHA256
                and me_sha == MEASURE_PY_EXPECTED_SHA256
                and mp_sha == MATCHED_PAIR_PY_EXPECTED_SHA256),
            part_a_results_sha256=sha256_file(PART_A_RESULTS),
            reused_not_rebuilt=[
                "mp.arm_hists", "mp.matched_pair_stats", "mp.load_module",
                "mp.selftest_fail_closed_sha_mismatch",
                "mp.selftest_injection_invariant_fail",
                "sa.evaluable_k", "sa.hist_of", "sa.batch_hists",
                "sa.N_JACK_BATCHES", "sa.PARAM_SETS",
                "measure.comb_matrix", "measure.log2_A_from_hists"],
            locally_redefined_bootstrap_utilities=local_copy_check,
            no_reused_function_was_rewritten=True),
        "fail_closed_selftests": selftests,
        "zero_decoder_call_enforcement": dict(
            tripwires_installed=tripwires,
            mechanism=("call-counting wrappers on the LOADED module objects' "
                       "attributes, in this process only; a call increments "
                       "the counter and raises SystemExit -- it never "
                       "delegates. No file on disk is edited."),
            counters_at_start=dict(DECODER_CALL_COUNTERS)),
        "parameter_set": {k: ps[k] for k in ("id", "n", "n_e", "n_2", "dup", "N")},
        "the_single_structural_change": dict(
            changed=("the draw: base ~ Binomial(n_e-1=55, p) shared by both "
                     "arms; arm_i = base + Bernoulli_i(p) with an INDEPENDENT "
                     "Bernoulli per arm"),
            replaces="null_object_control.py:256-257 (two independent streams)",
            unchanged=dict(p_frozen=P_FROZEN, p_recalibrated=False,
                           rungs=RUNGS, R=R_PREREGISTERED,
                           estimator_path=("mp.arm_hists -> sa.evaluable_k -> "
                                           "measure.comb_matrix -> "
                                           "mp.matched_pair_stats -> 2-point "
                                           "OLS in log-log")),
            marginal_law_of_each_arm="Binomial(56, p) EXACTLY"),
        "k_values": dict(reported=K_REPORTED,
                         k17_is_a_strict_addition_not_a_substitution=True,
                         why=("without k=17 the coupled band cannot be "
                              "compared against BATCH-91929e's uncoupled "
                              "widths 2.788 / 3.188 or the reviewer-built "
                              "coupled widths 3.398 / 3.508 / 4.326")),
        "no_planted_departure_leg": dict(
            dispatched=False, deliberate=True,
            reason=("BATCH-91929e's plant class was shown incapable of firing "
                    "at ANY magnitude (rho peaks near 1.3462 at g=2 and "
                    "REVERSES to 0.8688 by g=50 against a required 2.5256) and "
                    "its forced-identity check was an algebraic tautology "
                    "whose residual measures float64 rounding "
                    "(EV-HQC-e458ef O10, O11). Neither is re-run and no "
                    "substitute leg is invented. Declared as a substitution."),
            substituted_by=["SHAPE test", "POWER test"]),
        "persist_per_trial_S_requirement": dict(
            binds_on_this_task=False,
            reason=("DEC-20260817-2b638b next_actions item (3) is effective "
                    "from the NEXT SAMPLING TASK; this task makes zero decoder "
                    "calls and samples nothing"),
            carried_forward_to="the next sampling task in this family"),
    }

    # ---- the coupled draw --------------------------------------------------
    marg = {"count": 0, "sum": 0.0, "sumsq": 0.0,
            "per_arm": {0: {"count": 0, "sum": 0.0, "sumsq": 0.0},
                        1: {"count": 0, "sum": 0.0, "sumsq": 0.0}},
            "shared_base_count": 0, "arms_equal_count": 0}

    def coupled_pair(T, r, stream):
        """base ~ Binomial(55, p) shared; arm_i = base + Bernoulli_i(p)."""
        g_base = np.random.Generator(np.random.PCG64(
            np.random.SeedSequence([BASE_SEED, T, r, stream, 0])))
        base = g_base.binomial(n_e - 1, P_FROZEN, size=T).astype(np.int64)
        arms = []
        for i in (0, 1):
            g_i = np.random.Generator(np.random.PCG64(
                np.random.SeedSequence([BASE_SEED, T, r, stream, 1 + i])))
            arms.append(base + g_i.binomial(1, P_FROZEN, size=T).astype(np.int64))
        for i in (0, 1):
            a = arms[i]
            marg["per_arm"][i]["count"] += a.size
            marg["per_arm"][i]["sum"] += float(a.sum())
            marg["per_arm"][i]["sumsq"] += float((a.astype(np.float64) ** 2).sum())
        marg["count"] += arms[0].size + arms[1].size
        marg["sum"] += float(arms[0].sum()) + float(arms[1].sum())
        marg["sumsq"] += float((arms[0].astype(np.float64) ** 2).sum()) + \
            float((arms[1].astype(np.float64) ** 2).sum())
        marg["shared_base_count"] += base.size
        marg["arms_equal_count"] += int(np.count_nonzero(arms[0] == arms[1]))
        return arms[0], arms[1]

    def replicate(T, r, stream):
        S0, S1 = coupled_pair(T, r, stream)
        H0, B0 = mp.arm_hists(sa, S0, n_e, NB)
        H1, B1 = mp.arm_hists(sa, S1, n_e, NB)
        ks = sorted(set(sa.evaluable_k(H0, n_e)) & set(sa.evaluable_k(H1, n_e))
                    & set(K_RANGE_AUTHORIZED))
        st = mp.matched_pair_stats(measure, n_e, ks,
                                   measure.comb_matrix(n_e, ks), H0, B0, H1, B1)
        return st, ks

    # ---- PHASE 1: cost projection probe on the T=40000 rung ----------------
    probe_c0, probe_w0 = core_seconds(), time.time()
    probe_store = {}
    for r in range(PROJECTION_PROBE_REPLICATES):
        for stream in CELL_STREAMS:
            probe_store[(40000, r, stream)] = replicate(40000, r, stream)
    probe_core = core_seconds() - probe_c0
    probe_wall = time.time() - probe_w0
    n_probe_units = PROJECTION_PROBE_REPLICATES * len(CELL_STREAMS) * 40000
    unit_core_per_trial = probe_core / n_probe_units
    units_per_replicate = len(CELL_STREAMS) * sum(RUNGS)
    projected_total_core = R_PREREGISTERED * unit_core_per_trial * units_per_replicate
    threshold = PROJECTION_FRACTION * CORE_SECOND_BUDGET

    reduction = dict(no_reduction_fired=True, step_1_fired=False,
                     step_2_fired=False, step_3_fired=False)
    R_used, rungs_used = R_PREREGISTERED, list(RUNGS)
    if projected_total_core > threshold:
        reduction.update(step_1_fired=True, no_reduction_fired=False)
        per_rep_all = unit_core_per_trial * units_per_replicate
        R_fit = int(math.floor((threshold / per_rep_all) / 50.0) * 50)
        reduction["step_1_R_fit"] = R_fit
        R_used = max(R_FLOOR, R_fit)
        if R_fit < R_FLOOR:
            reduction["step_2_fired"] = True
            R_used = R_PREREGISTERED
            rungs_used = [t for t in RUNGS if t != 40000]
            units2 = len(CELL_STREAMS) * sum(rungs_used)
            reproj = R_used * unit_core_per_trial * units2
            reduction["step_2_reprojected_core_seconds"] = reproj
            if reproj > threshold:
                reduction["step_3_fired"] = True
                reduction["underpowered"] = True
    reduction["achieved_R"] = R_used
    reduction["achieved_rungs"] = rungs_used

    cost_projection = dict(
        task_id="TASK-20260817-b4b6e4", part="B",
        protocol="design.md section 3.7, applied in order, never improvised",
        written_unconditionally=True,
        trigger=("after the first 20 replicates of the T=40000 rung, project "
                 "total Part B cost from measured per-replicate cost"),
        probe=dict(rung_T=40000, replicates=PROJECTION_PROBE_REPLICATES,
                   streams=len(CELL_STREAMS),
                   measured_core_seconds=probe_core,
                   measured_wall_seconds=probe_wall,
                   trial_units=n_probe_units),
        arithmetic=dict(
            unit_core_seconds_per_trial=unit_core_per_trial,
            trial_units_per_replicate=units_per_replicate,
            formula=("projected = R * unit_core_seconds_per_trial * "
                     "(n_streams=5) * (5000 + 10000 + 20000 + 40000)"),
            R_preregistered=R_PREREGISTERED,
            projected_total_core_seconds=projected_total_core,
            core_second_authorization=CORE_SECOND_BUDGET,
            threshold_60_percent=threshold,
            projection_exceeds_threshold=bool(projected_total_core > threshold)),
        decision=reduction,
        achieved_R=R_used, achieved_rungs=rungs_used,
        underpowered=bool(reduction.get("underpowered", False)),
        underpowered_note=("If underpowered were true, Part B's bands would "
                           "NOT be presented as a calibration."))
    with open(os.path.join(args.out_dir, "cost_projection.json"), "w") as fh:
        json.dump(cost_projection, fh, indent=1)
    log(f"[cost_projection] projected_core={projected_total_core:.3f}s "
        f"threshold={threshold}s no_reduction_fired="
        f"{reduction['no_reduction_fired']} R={R_used} rungs={rungs_used}")

    # ---- PHASE 2: the ladder, five independent streams ---------------------
    # se[k][stream][T] = list over replicates
    se = {k: {s: {T: [] for T in rungs_used} for s in CELL_STREAMS}
          for k in K_REPORTED}
    uop_null = {k: {T: [] for T in rungs_used} for k in K_REPORTED}
    ks_variants = []
    for T in rungs_used:
        for r in range(R_used):
            for stream in CELL_STREAMS:
                key = (T, r, stream)
                st, ks = (probe_store[key] if key in probe_store
                          else replicate(T, r, stream))
                if ks not in ks_variants:
                    ks_variants.append(ks)
                for k in K_REPORTED:
                    j = st["ks"].index(k)
                    se[k][stream][T].append(st["se_paired"][j])
                    uop_null[k][T].append(st["unpaired_over_paired_ratio"][j])
        log(f"[rung] T={T} done R={R_used} streams={len(CELL_STREAMS)}")

    B["ladder"] = dict(
        rungs=rungs_used, replicates=R_used, streams=CELL_STREAMS,
        n_jack_batches=NB,
        jack_batch_sizes={str(T): T // NB for T in rungs_used},
        evaluable_k_distinct_variants_across_all_draws=len(ks_variants),
        evaluable_k_identical_across_all_draws=(len(ks_variants) == 1),
        evaluable_k_attained=ks_variants[0],
        evaluable_k_covers_2_to_26=(ks_variants[0] == K_RANGE_AUTHORIZED))

    # ---- realized Binomial(56, p) marginal check ---------------------------
    def moments(d):
        n = d["count"]
        mean = d["sum"] / n
        var = d["sumsq"] / n - mean ** 2
        return n, mean, var
    exp_mean, exp_var = n_e * P_FROZEN, n_e * P_FROZEN * (1 - P_FROZEN)
    marg_report = {"expected_mean_Binomial_56_p": exp_mean,
                   "expected_variance_Binomial_56_p": exp_var,
                   "p_frozen": P_FROZEN, "n_e": n_e}
    for label, d in [("both_arms_pooled", marg), ("arm_0", marg["per_arm"][0]),
                     ("arm_1", marg["per_arm"][1])]:
        n, mean, var = moments(d)
        mc_se_mean = math.sqrt(exp_var / n)
        mc_se_var = var * math.sqrt(2.0 / (n - 1))
        marg_report[label] = dict(
            n_draws=n, realized_mean=mean, realized_variance=var,
            mean_minus_expected=mean - exp_mean,
            variance_minus_expected=var - exp_var,
            monte_carlo_se_of_mean=mc_se_mean,
            approx_monte_carlo_se_of_variance=mc_se_var,
            mean_within_3_mc_se=bool(abs(mean - exp_mean) <= 3 * mc_se_mean),
            variance_within_3_mc_se=bool(abs(var - exp_var) <= 3 * mc_se_var))
    n_base = marg["shared_base_count"]
    marg_report["coupling_realized_check"] = dict(
        shared_base_draws=n_base,
        fraction_of_trials_with_arm0_equal_arm1=marg["arms_equal_count"] / n_base,
        analytic_expected_fraction=P_FROZEN ** 2 + (1 - P_FROZEN) ** 2,
        note=("arm_0 == arm_1 exactly when the two private Bernoullis agree, "
              "i.e. with probability p^2 + (1-p)^2. This is a direct, "
              "assumption-free confirmation that the arms are COUPLED and "
              "that the coupling has the pre-registered form."))
    B["realized_marginal_check"] = marg_report
    log(f"[marginal] pooled mean={marg_report['both_arms_pooled']['realized_mean']:.6f} "
        f"(expected {exp_mean:.6f}) var="
        f"{marg_report['both_arms_pooled']['realized_variance']:.6f} "
        f"(expected {exp_var:.6f})")

    # ---- the five banded contrasts, each DIRECTLY simulated -----------------
    def alpha_series(k, stream, tlo, thi):
        lo = se[k][stream][tlo]
        hi = se[k][stream][thi]
        d = math.log(thi) - math.log(tlo)
        return np.array([-(math.log(hi[r]) - math.log(lo[r])) / d
                         for r in range(R_used)], dtype=np.float64)

    PAIR_P, PAIR_N = (5000, 10000), (10000, 20000)
    have_P = PAIR_P[0] in rungs_used and PAIR_P[1] in rungs_used
    have_N = PAIR_N[0] in rungs_used and PAIR_N[1] in rungs_used

    csv_rows = []
    contrasts = {}
    for k in K_REPORTED:
        if not (have_P and have_N):
            contrasts[str(k)] = dict(unavailable="required rung pairs not in achieved rungs")
            continue
        a5P = alpha_series(k, 0, *PAIR_P)
        a5N = alpha_series(k, 1, *PAIR_N)
        a8P = alpha_series(k, 2, *PAIR_P)
        a8N = alpha_series(k, 3, *PAIR_N)
        a5Pb = alpha_series(k, 4, *PAIR_P)
        series = {
            "single_cell_alpha": (a5P, "5000->10000"),
            "regime_main_effect": ((a5P + a8P) / 2.0 - (a5N + a8N) / 2.0, "mixed"),
            "shard_main_effect": ((a5P + a5N) / 2.0 - (a8P + a8N) / 2.0, "mixed"),
            "interaction": ((a5P - a5N) - (a8P - a8N), "mixed"),
            "replication_delta": (a5P - a5Pb, "5000->10000"),
        }
        base_sd = float(np.std(series["single_cell_alpha"][0], ddof=1))
        blk = {}
        for name, (v, rp) in series.items():
            sd = float(np.std(v, ddof=1))
            p25, p50, p975 = pct(v, 2.5), pct(v, 50), pct(v, 97.5)
            mde = max(abs(p25), abs(p975))
            an = ANALYTIC_SD_FACTORS[name]
            measured_ratio = sd / base_sd
            rel = abs(measured_ratio - an) / an
            blk[name] = dict(
                replicates=R_used, rung_pair=rp,
                mean=float(np.mean(v)), sd=sd,
                p2_5=p25, p50=p50, p97_5=p975,
                null_95_interval=[p25, p975], interval_width=p975 - p25,
                measured_sd_ratio_against_single_cell_alpha=measured_ratio,
                analytic_sd_factor_under_cell_independence=an,
                relative_discrepancy=rel,
                discrepancy_exceeds_10_percent=bool(rel > 0.10),
                discrepancy_finding=("REPORTED AS A FINDING: measured SD ratio "
                                     "differs from the analytic factor by more "
                                     "than 10%" if rel > 0.10 else None),
                POWER_minimum_detectable_effect=mde,
                POWER_threshold_alpha_units=POWER_MDE_THRESHOLD,
                POWER_test=("PASS" if mde <= POWER_MDE_THRESHOLD else "FAIL"),
                directly_simulated=True,
                algebraically_rescaled_from_a_single_alpha=False)
            for r in range(R_used):
                csv_rows.append(dict(contrast=name, rung_pair=rp, k=k,
                                     replicate=r, value=float(v[r])))
        for lbl, v, rp in (("cell_5000_P", a5P, "5000->10000"),
                           ("cell_5000_N", a5N, "10000->20000"),
                           ("cell_8002_P", a8P, "5000->10000"),
                           ("cell_8002_N", a8N, "10000->20000"),
                           ("cell_5000_P_replication_partner", a5Pb, "5000->10000")):
            for r in range(R_used):
                csv_rows.append(dict(contrast=f"raw_{lbl}", rung_pair=rp, k=k,
                                     replicate=r, value=float(v[r])))
        contrasts[str(k)] = blk
    B["banded_contrasts"] = dict(
        note=("Each of the five quantities is formed DIRECTLY from four "
              "independent null cells (plus a fifth for the replication "
              "delta) per replicate. NO single alpha is banded and "
              "algebraically rescaled -- the defect DEC-20260817-2b638b "
              "rationale item (j) named."),
        analytic_factors_under_cell_independence=ANALYTIC_SD_FACTORS,
        shard_labels_carry_no_distinct_law_note=(
            "The null object is shard-free by construction, so the four cells "
            "are four independent draws from one law and the analytic factors "
            "follow from cell independence alone."),
        by_k=contrasts)

    # ---- SHAPE test --------------------------------------------------------
    shape = {}
    for k in K_REPORTED:
        pooled = [x for T in rungs_used for x in uop_null[k][T]]
        lo = real_uop[str(k)]["eight_real_cells_min"]
        hi = real_uop[str(k)]["eight_real_cells_max"]
        med = float(np.median(pooled))
        per_rung = {}
        for T in rungs_used:
            m = float(np.median(uop_null[k][T]))
            per_rung[str(T)] = dict(median=m,
                                    SHAPE_test=("PASS" if lo <= m <= hi else "FAIL"))
        shape[str(k)] = dict(
            coupled_null_median_se_unpaired_over_se_paired_pooled=med,
            coupled_null_median_per_rung=per_rung,
            eight_real_cells_range=[lo, hi],
            SHAPE_test_pooled=("PASS" if lo <= med <= hi else "FAIL"),
            SHAPE_test_agrees_across_rungs=(
                len({v["SHAPE_test"] for v in per_rung.values()}) == 1),
            pooled_is_primary_note=(
                "design.md section 3.5 did not disambiguate pooling, so BOTH "
                "the pooled median and every per-rung median are reported with "
                "their own verdicts, and any disagreement is visible rather "
                "than resolved by the executor."),
            comparator_BATCH_91929e_uncoupled_null=[0.9965, 0.9984],
            n=len(pooled))
        log(f"[SHAPE] k={k} pooled median={med:.6f} real range=[{lo:.4f},{hi:.4f}] "
            f"-> {shape[str(k)]['SHAPE_test_pooled']}")
    B["blindness_test_SHAPE"] = dict(
        definition=("the coupled null is SHAPE-BLIND at order k if its median "
                    "se_unpaired/se_paired at that k falls OUTSIDE the closed "
                    "range spanned by the eight real cells' measured values at "
                    "that same k"),
        executor_declares_no_verdict_note=(
            "PASS/FAIL is reported mechanically. The executor does NOT declare "
            "the control BLIND in a verdict sense; batch.yaml's frozen rule "
            "reads this test."),
        by_k=shape)
    B["blindness_test_POWER"] = dict(
        definition=("the coupled null is POWER-BLIND for a contrast at order k "
                    "if that contrast's minimum detectable effect "
                    "max(|p2.5|, |p97.5|) exceeds 3.702 alpha units"),
        threshold_alpha_units=POWER_MDE_THRESHOLD,
        by_k={k: {name: dict(
            minimum_detectable_effect=v["POWER_minimum_detectable_effect"],
            POWER_test=v["POWER_test"])
            for name, v in blk.items()} if "unavailable" not in blk else blk
            for k, blk in contrasts.items()},
        executor_declares_no_verdict_note=(
            "PASS/FAIL only. No verdict of blindness is issued here."))

    # ---- k=17 band widths beside the committed comparators -----------------
    if "17" in contrasts and "unavailable" not in contrasts["17"]:
        B["k17_band_width_comparison"] = dict(
            coupled_this_batch=dict(
                single_cell_alpha_width=contrasts["17"]["single_cell_alpha"]["interval_width"],
                per_contrast_widths={n: v["interval_width"]
                                     for n, v in contrasts["17"].items()}),
            committed_uncoupled_BATCH_91929e_widths=[2.788, 3.188],
            reviewer_built_coupled_widths=[3.398, 3.508, 4.326],
            note=("Reported side by side as measured. No conclusion is drawn "
                  "about what the comparison implies."))

    # ---- 2-point versus 4-rung OLS on THIS batch's coupled replicates ------
    dom = dict(
        dominated_by_verbatim=("4-rung OLS in log-log on identical data, SD "
                               "0.234334 against 0.700666, a 2.99x noise "
                               "reduction at zero cost"),
        committed_uncoupled_sd_2point=0.700666,
        committed_uncoupled_sd_4rung_ols=0.234334,
        committed_noise_reduction_factor=2.99)
    if len(rungs_used) >= 3:
        logT = np.log(np.array(rungs_used, dtype=np.float64))
        for k in K_REPORTED:
            full = []
            for r in range(R_used):
                y = np.log(np.array([se[k][0][T][r] for T in rungs_used]))
                slope, _ = np.polyfit(logT, y, 1)
                full.append(-float(slope))
            two = alpha_series(k, 0, *PAIR_P) if have_P else None
            sd4 = float(np.std(full, ddof=1))
            sd2 = float(np.std(two, ddof=1)) if two is not None else None
            dom[f"k_{k}"] = dict(
                measured_sd_2point_this_batch=sd2,
                measured_sd_4rung_ols_this_batch=sd4,
                measured_noise_reduction_factor=(None if not sd4 else
                                                 (sd2 / sd4 if sd2 else None)),
                stream="cell_5000_P (stream 0)", rungs=rungs_used,
                replicates=R_used, coupled=True)
    B["two_point_versus_four_rung_ols"] = dom

    # ---- CSV ---------------------------------------------------------------
    csv_path = os.path.join(args.out_dir, "coupled_null_replicate_summary.csv")
    with open(csv_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["contrast", "rung_pair", "k",
                                           "replicate", "value"])
        w.writeheader()
        for row in csv_rows:
            w.writerow(row)
    B["replicate_summary_csv"] = dict(
        path="coupled_null_replicate_summary.csv", rows=len(csv_rows),
        columns=["contrast", "rung_pair", "k", "replicate", "value"],
        sufficient_to_recompute_every_band_without_rerunning_the_ladder=True,
        includes_raw_cell_alphas=True)

    # ---- EXIT GATE: counters zero, pins re-verified ON DISK -----------------
    exit_pins = dict(stage_a_sha256_at_exit=sha256_file(STAGE_A_PY),
                     measure_sha256_at_exit=sha256_file(MEASURE_PY),
                     matched_pair_py_sha256_at_exit=sha256_file(MATCHED_PAIR_PY))
    pins_ok = (exit_pins["stage_a_sha256_at_exit"] == STAGE_A_PY_EXPECTED_SHA256
               and exit_pins["measure_sha256_at_exit"] == MEASURE_PY_EXPECTED_SHA256
               and exit_pins["matched_pair_py_sha256_at_exit"] == MATCHED_PAIR_PY_EXPECTED_SHA256)
    counters_ok = all(v == 0 for v in DECODER_CALL_COUNTERS.values())
    B["zero_decoder_call_enforcement"].update(
        counters_at_exit=dict(DECODER_CALL_COUNTERS),
        counters_all_zero_at_exit=counters_ok,
        module_sha256_re_verified_on_disk_at_exit=exit_pins,
        all_pins_unchanged_on_disk_at_exit=pins_ok,
        decoder_calls_made=sum(DECODER_CALL_COUNTERS.values()))
    log(f"[exit-gate] counters={DECODER_CALL_COUNTERS} all_zero={counters_ok} "
        f"pins_unchanged={pins_ok}")
    if not counters_ok or not pins_ok:
        raise SystemExit(
            "INFRASTRUCTURE ABORT at exit gate: decoder counter non-zero or a "
            "pinned module changed on disk. AGENTS.md rule 5 -- this is an "
            "infrastructure outcome, never a result.")

    wall, core = time.time() - t0, core_seconds() - c0
    B["timing"] = dict(part="B", wall_clock_seconds=wall, core_seconds=core,
                       probe_core_seconds=probe_core, probe_wall_seconds=probe_wall,
                       wall_clock_authorization_shared=300,
                       core_second_authorization_shared=150, measured=True)
    B["achieved"] = dict(R=R_used, rungs=rungs_used,
                         underpowered=bool(reduction.get("underpowered", False)))
    B["finished_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    B["validity"] = dict(
        status="completed_valid",
        certificate=dict(kind="none",
                         reason=("Pure measurement / simulation run. No "
                                 "discrete-log solve and no factor-base "
                                 "relation is claimed, so no solution "
                                 "certificate applies.")),
        reading_rule_applied=False, branch_named=False, conclusion_drawn=False,
        blindness_declared_in_a_verdict_sense=False)
    with open(os.path.join(args.out_dir, "coupled_null_control_results.json"), "w") as fh:
        json.dump(B, fh, indent=1)
    log(f"[partB] done wall={wall:.4f}s core={core:.4f}s R={R_used} rungs={rungs_used}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
