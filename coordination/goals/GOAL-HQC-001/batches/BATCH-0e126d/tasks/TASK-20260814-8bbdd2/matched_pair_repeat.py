#!/usr/bin/env python3
"""Discard-prefix repeat of the T=20,000 matched-pair extension on shards
5000/6000 THEMSELVES, at a genuinely new disjoint trial range.

TASK-20260814-8bbdd2 (executor) / BATCH-0e126d / GOAL-HQC-001 / EXP-HQC-982268.
Authorized by DEC-20260809-186c86's next_actions (adopting the Red Team's
named counterexample, EV-HQC-3a0372 O8). Pre-registered design in design.md
(WRITTEN AND FROZEN BEFORE THIS SCRIPT WAS RUN ON REAL DATA).

stage_a.py's _t_shard has no trial-offset parameter: every call begins trial
indexing at 0 internally. To get a disjoint trial range on shards already
used by TASK-20260809-a79e4f (trials 0..4999 on shards 5000/6000), this
script calls _t_shard ONCE per (shard, variant) with n_trials = 5000+10000 =
15000, and retains only the trailing slice [5000:15000) for every statistic.
The discarded prefix [0:5000) is STILL COMPUTED (never skipped) so its
S-histogram / per-trial S can be checked bit-identical against
TASK-20260809-a79e4f's committed per_trial_S arrays -- the disjointness
proof (design.md Section 3).

stage_a.py, measure.py, and TASK-20260809-a79e4f's matched_pair.py are
imported READ-ONLY via matched_pair.py's own load_module() pattern. None of
the three files is modified on disk. The only new code here is the
discard-prefix driver, the disjointness self-check, and the new standing
F[:, 0:n_e-1] structural invariant check (design.md Section 4); the
matched-pair jackknife statistics themselves are computed by calling
matched_pair.py's own arm_hists / matched_pair_stats / cell / run_arm
functions directly.

Claim tier: TOY, hard ceiling. PS-R3 only. Nothing here is a statement about
HQC, A17, its decoding-failure rate, or any standardized parameter set.

A timeout, crash, missing dependency or budget exhaustion is an
INFRASTRUCTURE outcome and is never evidence about the mathematics
(AGENTS.md rule 5).

Re-run:
    PYTHONDONTWRITEBYTECODE=1 python3 matched_pair_repeat.py --out-dir .
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
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
PRIOR_RESULTS_JSON = os.path.join(
    REPO, "coordination", "goals", "GOAL-HQC-001", "batches", "BATCH-412513",
    "tasks", "TASK-20260809-a79e4f", "matched_pair_results.json")

# sha256 pins -- identical values matched_pair.py, pilot_injection.py and
# every prior arm in this campaign pinned for these two files (independently
# re-verified by this task at run time via load_module()).
STAGE_A_PY_EXPECTED_SHA256 = (
    "06a0a618432c00fe26c72ecf05a8d89489db61c5183931fdb76a378717681405")
MEASURE_PY_EXPECTED_SHA256 = (
    "a4fd1ecb63f0ddc83c02ef45f2c65ab31cf13d13e7ae94f500e67465b24f5dc8")

SET_ID = "PS-R3"
M = 17                       # load-bearing order, primary cell
K_RANGE_AUTHORIZED = list(range(2, 27))

SHARD_5000 = 5000
SHARD_6000 = 6000
N_DISCARD_PREFIX = 5000
N_NEW = 10000
N_TOTAL_PER_CALL = N_DISCARD_PREFIX + N_NEW   # 15000

BATCH = 64
WALL_CAP_PER_CALL = 600.0
CORE_SECOND_BUDGET = 500.0
WALL_SECOND_BUDGET = 1800.0


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


def load_module_fail_closed(path: str, expected_sha256: str, name: str, module_name: str):
    """FAIL-CLOSED: aborts (SystemExit) if the file on disk does not match
    the pinned sha256. Loaded read-only via importlib; the file itself is
    never opened for writing. Identical pattern to matched_pair.py's own
    load_module()."""
    actual = sha256_file(path)
    if actual != expected_sha256:
        raise SystemExit(
            f"FAIL-CLOSED: {name} sha256 mismatch. expected={expected_sha256} "
            f"actual={actual}. This task reuses {name} read-only and refuses "
            f"to proceed if the file on disk differs from what design.md was "
            f"written against.")
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)                          # imported UNMODIFIED
    return mod, actual


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=HERE)
    args = ap.parse_args(argv)
    out_path = os.path.join(args.out_dir, "matched_pair_repeat_results.json")

    t_wall0, c_wall0 = time.time(), core_seconds()
    R = {
        "task_id": "TASK-20260814-8bbdd2",
        "role": "executor",
        "experiment_id": "EXP-HQC-982268",
        "hypothesis_id": "H-HQC-18d1b4",
        "goal": "GOAL-HQC-001",
        "batch": "BATCH-0e126d",
        "claim_tier": "toy",
        "scope_statement": (
            "TOY, hard ceiling. PS-R3 only. One defect class (V3, "
            "last-block-window-read-early), one injection point "
            "(decode_blocks's block window, last block only). Shards 5000 "
            "and 6000 ONLY, trial indices [5000, 15000) ONLY (discarded "
            "prefix [0, 5000) computed but excluded from every statistic). "
            "NOTHING here is a statement about HQC, A17, A5, any "
            "decoding-failure rate, or any standardized parameter set."),
        "design_reference": "design.md, written and frozen before this run",
        "started_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "command": " ".join([sys.executable] + sys.argv),
        "git": git_state(),
        "environment": dict(
            python=sys.version, python_executable=sys.executable,
            platform=platform.platform(), machine=platform.machine(),
            numpy=np.__version__, cpu_count=os.cpu_count(),
            affinity=len(os.sched_getaffinity(0))),
        "n_discard_prefix": N_DISCARD_PREFIX,
        "n_new": N_NEW,
        "n_total_per_call": N_TOTAL_PER_CALL,
        "shards": [SHARD_5000, SHARD_6000],
        "retained_slice": "[5000:15000)",
        "discarded_slice": "[0:5000)",
    }

    # ---- phase 1: real, sha256-pinned, read-only module loads ------------
    sa, sa_sha = load_module_fail_closed(
        STAGE_A_PY, STAGE_A_PY_EXPECTED_SHA256, "stage_a.py",
        "stage_a_frozen_matched_pair_repeat")
    measure, measure_sha = load_module_fail_closed(
        MEASURE_PY, MEASURE_PY_EXPECTED_SHA256, "measure.py",
        "measure_frozen_matched_pair_repeat")

    # matched_pair.py: no pre-declared expected hash exists (this is the
    # first task to reuse it). Measure its sha256 now, then load it via the
    # same fail-closed loader pinned to the value just measured -- a
    # self-consistency pin that catches a race/modification between the
    # measurement and the load, and the measured value is recorded so a
    # future task in this family can cite it as an external pin.
    matched_pair_measured_sha256 = sha256_file(MATCHED_PAIR_PY)
    mp_mod, mp_sha = load_module_fail_closed(
        MATCHED_PAIR_PY, matched_pair_measured_sha256, "matched_pair.py",
        "matched_pair_frozen_repeat")

    R["provenance"] = dict(
        stage_a_path=os.path.relpath(STAGE_A_PY, REPO), stage_a_sha256=sa_sha,
        stage_a_sha256_expected=STAGE_A_PY_EXPECTED_SHA256,
        stage_a_sha256_match=(sa_sha == STAGE_A_PY_EXPECTED_SHA256),
        measure_path=os.path.relpath(MEASURE_PY, REPO), measure_sha256=measure_sha,
        measure_sha256_expected=MEASURE_PY_EXPECTED_SHA256,
        measure_sha256_match=(measure_sha == MEASURE_PY_EXPECTED_SHA256),
        matched_pair_py_path=os.path.relpath(MATCHED_PAIR_PY, REPO),
        matched_pair_py_sha256_measured=matched_pair_measured_sha256,
        matched_pair_py_sha256_note=(
            "No expected value was pre-declared for this file before this "
            "task existed (it is reused for the first time by this task "
            "family); measured, not fabricated, per the handoff. This is "
            "the value future tasks in this family should cite as the pin."),
        prior_results_json_path=os.path.relpath(PRIOR_RESULTS_JSON, REPO),
        prior_results_json_sha256=sha256_file(PRIOR_RESULTS_JSON),
        stage_a_modified=False, measure_modified=False, matched_pair_py_modified=False)

    # ---- phase 2: fail-closed selftests, reused from matched_pair.py -----
    R["fail_closed_selftests"] = {
        "sha256_pin_mismatch": mp_mod.selftest_fail_closed_sha_mismatch(),
    }
    print("[selftest] sha256 pin mismatch: "
          f"{R['fail_closed_selftests']['sha256_pin_mismatch']['verdict']}", flush=True)
    if R["fail_closed_selftests"]["sha256_pin_mismatch"]["verdict"] != "PASS":
        raise SystemExit("FAILED_IMPLEMENTATION: sha256 pin fail-closed "
                         "selftest did not pass; refusing to proceed")

    ps = [p for p in sa.PARAM_SETS if p["id"] == SET_ID][0]
    n_e, n_2, dup, N = ps["n_e"], ps["n_2"], ps["dup"], ps["N"]
    R["parameter_set"] = {k: ps[k] for k in
                          ("id", "role", "n", "n_e", "n_2", "dup", "omega",
                           "omega_r", "omega_e", "N")}
    R["parameter_set"]["m_load_bearing_order"] = M

    R["fail_closed_selftests"]["injection_invariant_mismatch"] = (
        mp_mod.selftest_injection_invariant_fail(n_e, n_2))
    print("[selftest] injection invariant deliberate break: "
          f"{R['fail_closed_selftests']['injection_invariant_mismatch']['verdict']}",
          flush=True)
    if R["fail_closed_selftests"]["injection_invariant_mismatch"]["verdict"] != "PASS":
        raise SystemExit("FAILED_IMPLEMENTATION: injection-invariant "
                         "fail-closed selftest did not pass; refusing to proceed")

    original_decode_blocks = sa.decode_blocks
    defected_decode_blocks = mp_mod.make_defected_decode_blocks(original_decode_blocks, n_2)
    R["injection"] = dict(
        defect_class="V3 (last-block-window-read-early)",
        injection_point="decode_blocks's block window, LAST BLOCK ONLY "
                        "(index n_e - 1), shifted left by exactly one bit "
                        "position; decode_blocks itself called unmodified",
        wrapper_calls_unmodified_function=(
            defected_decode_blocks.__wrapped_original_id__ == id(original_decode_blocks)),
        wrapped_original_qualname=defected_decode_blocks.__wrapped_original_qualname__,
        mechanism="design.md Section 4/7, fixed before this run")

    # ---- phase 3: THE FOUR (shard, variant) CALLS, ONE _t_shard call each,
    #      n_trials = 15000, via matched_pair.py's own run_arm() ------------
    d2_d3_flags = []
    calls = {}   # (shard, variant) -> raw r dict (with full F retained)
    for shard in (SHARD_5000, SHARD_6000):
        for variant, decode_fn in (("defected", defected_decode_blocks),
                                   ("undefected", original_decode_blocks)):
            r = mp_mod.run_arm(sa, ps, shard, N_TOTAL_PER_CALL, decode_fn,
                               original_decode_blocks)
            calls[(shard, variant)] = r
            d2_d3_flags.append((f"shard_{shard}_{variant}", r))
            print(f"[call] shard={shard} variant={variant} "
                  f"trials_done={r['trials_done']} truncated={r['truncated']}",
                  flush=True)

    R["hard_invariants"] = {tag: dict(D2_violations=r["d2_fail"],
                                      D3_violations=r["d3_fail"],
                                      D3_cap=r["d3_cap"], D3_max_w=r["d3_max_w"])
                            for tag, r in d2_d3_flags}
    d2_d3_clean = all(r["d2_fail"] == 0 and r["d3_fail"] == 0
                      for _, r in d2_d3_flags)
    any_truncated = any(r["truncated"] for _, r in d2_d3_flags)
    all_full_length = all(r["trials_done"] == N_TOTAL_PER_CALL for _, r in d2_d3_flags)

    # ---- phase 4: DISJOINTNESS SELF-CHECK (FAIL-CLOSED, before any stat) -
    with open(PRIOR_RESULTS_JSON) as fh:
        prior = json.load(fh)
    committed = prior["stage_1"]["per_trial_S"]

    S_full = {}
    F_full = {}
    for (shard, variant), r in calls.items():
        F_full[(shard, variant)] = r["F"]                    # (15000, n_e)
        S_full[(shard, variant)] = r["F"].sum(axis=1).astype(np.int64)

    disjointness_checks = []
    disjointness_all_pass = True
    for shard, variant in ((SHARD_5000, "defected"), (SHARD_5000, "undefected"),
                           (SHARD_6000, "defected"), (SHARD_6000, "undefected")):
        key = f"shard_{shard}_{variant}"
        S_prefix = S_full[(shard, variant)][:N_DISCARD_PREFIX]
        committed_arr = np.array(committed[key], dtype=np.int64)
        elementwise_match = bool(np.array_equal(S_prefix, committed_arr))
        hist_prefix = sa.hist_of(S_prefix, n_e)
        hist_committed = sa.hist_of(committed_arr, n_e)
        hist_match = bool(np.array_equal(hist_prefix, hist_committed))
        length_match = (len(S_prefix) == len(committed_arr) == N_DISCARD_PREFIX)
        ok = elementwise_match and hist_match and length_match
        disjointness_all_pass &= ok
        disjointness_checks.append(dict(
            key=key, length_match=length_match,
            elementwise_per_trial_S_bit_identical=elementwise_match,
            S_histogram_bit_identical=hist_match,
            prefix_length=int(len(S_prefix)),
            committed_length=int(len(committed_arr)),
            verdict="PASS" if ok else "FAIL"))
    R["disjointness_self_check"] = dict(
        rule=("For each of the 4 (shard, variant) calls, the discarded prefix "
              "[0:5000) of this run's own freshly generated per-trial S must "
              "be bit-identical, elementwise, to TASK-20260809-a79e4f's "
              "committed per_trial_S array for the same (shard, variant), AND "
              "the S-histograms of both must be bit-identical."),
        checks=disjointness_checks,
        overall_status="PASS" if disjointness_all_pass else "FAIL",
        source=os.path.relpath(PRIOR_RESULTS_JSON, REPO))
    print(f"[disjointness_self_check] status={R['disjointness_self_check']['overall_status']}",
          flush=True)

    if not disjointness_all_pass:
        # FAIL-CLOSED ABORT. AGENTS.md rule 5: infrastructure/environment
        # signal, never a result about the mathematics. No matched-pair
        # statistic is computed from the retained tail.
        spent_core = core_seconds() - c_wall0
        spent_wall = time.time() - t_wall0
        R["budget"] = dict(
            core_seconds_authorized=CORE_SECOND_BUDGET,
            core_seconds_spent=round(spent_core, 3),
            wall_seconds_authorized=WALL_SECOND_BUDGET,
            wall_seconds_spent=round(spent_wall, 3))
        R["validity"] = dict(
            status="invalid_measurement",
            failure_class="infrastructure_error",
            reason=("The disjointness self-check FAILED: at least one "
                    "discarded-prefix per-trial S array (or its histogram) "
                    "is not bit-identical to TASK-20260809-a79e4f's "
                    "committed per_trial_S array for the same (shard, "
                    "variant). Per AGENTS.md rule 5 this is an "
                    "infrastructure/environment/determinism regression "
                    "signal and is NEVER reported as a result about the "
                    "mathematics. No matched-pair statistic was computed "
                    "from the retained tail."))
        R["finished_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with open(out_path, "w") as fh:
            json.dump(R, fh, indent=1)
        print(f"[ABORT] disjointness self-check failed; wrote {out_path}", flush=True)
        return R

    # ---- phase 5: THE STANDING F[:, 0:n_e-1] INVARIANT, on the RETAINED
    #      tail only (design.md Section 4) -------------------------------
    invariant_checks = []
    invariant_all_pass = True
    for shard in (SHARD_5000, SHARD_6000):
        F_def_tail = F_full[(shard, "defected")][N_DISCARD_PREFIX:N_TOTAL_PER_CALL]
        F_undef_tail = F_full[(shard, "undefected")][N_DISCARD_PREFIX:N_TOTAL_PER_CALL]
        window_def = F_def_tail[:, 0:n_e - 1]
        window_undef = F_undef_tail[:, 0:n_e - 1]
        mismatch_mask = (window_def != window_undef)
        mismatch_count = int(mismatch_mask.sum())
        ok = (mismatch_count == 0
              and window_def.shape == window_undef.shape
              and window_def.shape == (N_NEW, n_e - 1))
        invariant_all_pass &= ok
        invariant_checks.append(dict(
            shard=shard,
            trials_checked=N_NEW,
            blocks_checked_per_trial=n_e - 1,
            total_elements_checked=int(window_def.size),
            mismatch_count=mismatch_count,
            shapes_match=bool(window_def.shape == window_undef.shape),
            verdict="PASS" if ok else "FAIL"))
    R["f_invariant_check"] = dict(
        rule=("F[:, 0:n_e-1] (all blocks except the last) must be bit-identical, "
              "elementwise, between the defected and undefected decode of the "
              "SAME trial on the SAME shard, checked on the retained "
              "10,000-trial tail slice of each shard (EV-HQC-3a0372 O11)."),
        checks=invariant_checks,
        overall_status="PASS" if invariant_all_pass else "FAIL")
    print(f"[f_invariant_check] status={R['f_invariant_check']['overall_status']}", flush=True)

    # release the full F arrays now that both checks are done (memory)
    for k in list(F_full.keys()):
        F_full[k] = None

    # ---- phase 6: matched-pair statistics on the RETAINED tail only ------
    S_tail = {k: v[N_DISCARD_PREFIX:N_TOTAL_PER_CALL] for k, v in S_full.items()}
    R["per_trial_S_retained_tail_length"] = {
        f"shard_{s}_{v}": int(len(S_tail[(s, v)]))
        for s in (SHARD_5000, SHARD_6000) for v in ("defected", "undefected")}

    NB = sa.N_JACK_BATCHES  # 200
    H = {}
    B = {}
    for shard in (SHARD_5000, SHARD_6000):
        for variant in ("defected", "undefected"):
            H[(shard, variant)], B[(shard, variant)] = mp_mod.arm_hists(
                sa, S_tail[(shard, variant)], n_e, NB)

    stats_by_shard = {}
    ks_by_shard = {}
    for shard in (SHARD_5000, SHARD_6000):
        H_def, B_def = H[(shard, "defected")], B[(shard, "defected")]
        H_undef, B_undef = H[(shard, "undefected")], B[(shard, "undefected")]
        ks = sorted((set(sa.evaluable_k(H_def, n_e))
                    & set(sa.evaluable_k(H_undef, n_e))
                    & set(K_RANGE_AUTHORIZED)))
        ks_by_shard[shard] = ks
        C = measure.comb_matrix(n_e, ks) if ks else None
        stats_by_shard[shard] = (
            mp_mod.matched_pair_stats(measure, n_e, ks, C, H_def, B_def, H_undef, B_undef)
            if ks else None)

    ks_pooled = sorted(set(ks_by_shard[SHARD_5000]) & set(ks_by_shard[SHARD_6000])
                       & set(K_RANGE_AUTHORIZED))
    H_pooled_def = H[(SHARD_5000, "defected")] + H[(SHARD_6000, "defected")]
    H_pooled_undef = H[(SHARD_5000, "undefected")] + H[(SHARD_6000, "undefected")]
    B_pooled_def = np.concatenate([B[(SHARD_5000, "defected")], B[(SHARD_6000, "defected")]], axis=0)
    B_pooled_undef = np.concatenate([B[(SHARD_5000, "undefected")], B[(SHARD_6000, "undefected")]], axis=0)
    C_pooled = measure.comb_matrix(n_e, ks_pooled) if ks_pooled else None
    stats_pooled = (mp_mod.matched_pair_stats(measure, n_e, ks_pooled, C_pooled,
                                              H_pooled_def, B_pooled_def,
                                              H_pooled_undef, B_pooled_undef)
                   if ks_pooled else None)

    R["reachability"] = dict(
        evaluable_k_shard_5000=ks_by_shard[SHARD_5000],
        evaluable_k_shard_6000=ks_by_shard[SHARD_6000],
        evaluable_k_pooled=ks_pooled, load_bearing_order_m=M,
        m_reachable_pooled=(M in ks_pooled))

    R["matched_pair"] = dict(
        per_shard=dict(
            shard_5000=stats_by_shard[SHARD_5000],
            shard_6000=stats_by_shard[SHARD_6000]),
        pooled=stats_pooled,
        primary_cell_k17=dict(
            shard_5000=(mp_mod.cell(stats_by_shard[SHARD_5000], M)
                       if stats_by_shard[SHARD_5000] and M in stats_by_shard[SHARD_5000]["ks"]
                       else None),
            shard_6000=(mp_mod.cell(stats_by_shard[SHARD_6000], M)
                       if stats_by_shard[SHARD_6000] and M in stats_by_shard[SHARD_6000]["ks"]
                       else None),
            pooled=(mp_mod.cell(stats_pooled, M)
                   if stats_pooled and M in stats_pooled["ks"] else None)))

    se_pooled_k17 = (R["matched_pair"]["primary_cell_k17"]["pooled"]["se_paired"]
                    if R["matched_pair"]["primary_cell_k17"]["pooled"] else None)

    # ---- phase 7: fitted SE-vs-trial-count exponent refit, 3 points on
    #      shards 5000/6000 ONLY (T=5000, T=10000 from the committed prior
    #      task; T=20000 from this task) --------------------------------
    prior_k17 = prior["stage_1"]["matched_pair"]["primary_cell_k17"]
    se_5000_prior = prior_k17["shard_5000"]["se_paired"] if prior_k17["shard_5000"] else None
    se_6000_prior = prior_k17["shard_6000"]["se_paired"] if prior_k17["shard_6000"] else None
    se_per_shard_5000_mean = (
        float(np.mean([x for x in (se_5000_prior, se_6000_prior) if x is not None]))
        if (se_5000_prior is not None or se_6000_prior is not None) else None)
    se_10000_pooled_prior = prior_k17["pooled"]["se_paired"] if prior_k17["pooled"] else None

    points = [(5000.0, se_per_shard_5000_mean), (10000.0, se_10000_pooled_prior),
             (20000.0, se_pooled_k17)]
    valid_points = [(t, se) for t, se in points if se is not None and se > 0]
    if len(valid_points) >= 2:
        logt = np.log(np.array([p[0] for p in valid_points]))
        logse = np.log(np.array([p[1] for p in valid_points]))
        slope, intercept = np.polyfit(logt, logse, 1)
        alpha = -float(slope)
    else:
        alpha = None
    R["se_vs_trial_count_fit"] = dict(
        points=[dict(T=t, SE_paired_k17=se,
                     source=("TASK-20260809-a79e4f committed stage 1" if t < 20000
                             else "this task (TASK-20260814-8bbdd2)"))
               for t, se in points],
        shards="5000 and 6000 for ALL THREE points (never 8001/8002)",
        method="numpy.polyfit(log(T), log(SE), 1); alpha = -slope",
        fitted_exponent_alpha=alpha,
        consistent_with_1_over_sqrt_T_band=[0.4, 0.6],
        reference_prior_task_points_note=(
            "TASK-20260809-a79e4f's own (T=5000, T=10000) points on these "
            "same two shards were SE=0.137502 (mean of per-shard values) and "
            "SE=0.096781 (pooled); DEC-20260809-186c86 frames landing near "
            "0.068-0.070 at T=20000 as consistent with 1/sqrt(T) continuing "
            "from those two points."),
        note="1/sqrt(T) consistency is alpha in [0.4, 0.6], declared in "
             "advance. This value is reported descriptively; no conclusion "
             "is drawn here about which of DEC-20260809-186c86's two named "
             "outcomes (shard-specific vs. general refutation) obtains.")

    # ---- phase 8: budget + validity ---------------------------------------
    spent_core = core_seconds() - c_wall0
    spent_wall = time.time() - t_wall0
    R["budget"] = dict(
        core_seconds_authorized=CORE_SECOND_BUDGET,
        core_seconds_spent=round(spent_core, 3),
        wall_seconds_authorized=WALL_SECOND_BUDGET,
        wall_seconds_spent=round(spent_wall, 3),
        within_core_second_budget=spent_core <= CORE_SECOND_BUDGET,
        within_wall_budget=spent_wall <= WALL_SECOND_BUDGET)

    ok = (R["fail_closed_selftests"]["sha256_pin_mismatch"]["verdict"] == "PASS"
          and R["fail_closed_selftests"]["injection_invariant_mismatch"]["verdict"] == "PASS"
          and R["injection"]["wrapper_calls_unmodified_function"]
          and disjointness_all_pass
          and invariant_all_pass
          and d2_d3_clean and not any_truncated and all_full_length
          and stats_pooled is not None and M in stats_pooled["ks"]
          and se_pooled_k17 is not None and se_pooled_k17 > 0)
    R["validity"] = dict(
        status="valid_measurement" if ok else "invalid_measurement",
        failure_class=(None if ok else "invalid_measurement"),
        reason=("All pre-registered mechanically-sound criteria met "
                "(design.md Section 8): both fail-closed selftests PASS, "
                "wrapper genuinely calls the unmodified decode_blocks, the "
                "disjointness self-check PASSES on all 4 calls, the "
                "F[:, 0:n_e-1] structural invariant PASSES on both shards, "
                "D2/D3 clean on all four calls, no call truncated, all four "
                "calls delivered the full 15,000 trials requested, the "
                "pooled estimator returns a finite diff and finite positive "
                "SE_paired at k=17 on the retained tail."
                if ok else
                "One or more pre-registered mechanically-sound criteria "
                "(design.md Section 8) were not met -- see the individual "
                "gate fields above (disjointness_self_check, "
                "f_invariant_check, hard_invariants, fail_closed_selftests) "
                "for which one."))

    R["finished_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(out_path, "w") as fh:
        json.dump(R, fh, indent=1)
    print(f"[done] -> {out_path}  core-s={spent_core:.2f}/{CORE_SECOND_BUDGET} "
          f"wall={spent_wall:.1f}s/{WALL_SECOND_BUDGET}s  "
          f"validity={R['validity']['status']}", flush=True)
    return R


if __name__ == "__main__":
    main()
