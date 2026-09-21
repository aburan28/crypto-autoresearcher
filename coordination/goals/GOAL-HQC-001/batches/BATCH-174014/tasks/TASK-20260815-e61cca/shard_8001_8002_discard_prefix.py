#!/usr/bin/env python3
"""Single-shard-only (unpooled) local exponent for shards 8001 and 8002,
via a discard-prefix repeat of a T=20,000 matched-pair extension on EACH
shard individually, plus an adapted two-step disjointness proof (no raw
per-trial array exists for these shards to check directly against).

TASK-20260815-e61cca (executor) / BATCH-174014 / GOAL-HQC-001 / EXP-HQC-982268.
Authorized by DEC-20260814-3f429d's next_actions (adopting the Red Team's own
named next_concrete_action and required_controls items 1 and 3,
TASK-20260814-a49f1c). Pre-registered design in design.md (WRITTEN AND FROZEN
BEFORE THIS SCRIPT WAS RUN ON REAL DATA).

stage_a.py's _t_shard has no trial-offset parameter: every call begins trial
indexing at 0 internally. To get a disjoint trial range on shards already
used by TASK-20260809-a79e4f stage 2 (trials 0..9999 on shards 8001/8002),
this script calls _t_shard ONCE per (shard, variant) with
n_trials = 10000 + 20000 = 30000, and retains only the trailing slice
[10000:30000) for every statistic. The discarded prefix [0:10000) is STILL
COMPUTED (never skipped).

UNLIKE TASK-20260814-8bbdd2 (shards 5000/6000), stage 2 never persisted a raw
per-trial S array for shards 8001/8002 (matched_pair.py's stage-2 branch
never writes an R['per_trial_S'] key). The direct bit-identical-array-vs-
committed-record disjointness check is therefore NOT AVAILABLE here. This
script instead runs a DEDICATED, SEPARATE verification call at n_trials=10000
per (shard, variant) BEFORE the real n_trials=30000 analysis call, checks
that verification call's own D2/D3/D3_cap/D3_max_w and recomputed
matched_pair_stats match TASK-20260809-a79e4f's COMMITTED stage_2 values
exactly, and THEN checks that the real analysis call's own discarded prefix
is bit-identical to that SAME verification call's own raw per-trial S
(within-task, cross-call determinism check). This is explicitly WEAKER than
TASK-20260814-8bbdd2's direct check -- see design.md Section 3 for the full
argument -- and is named as such in this script's own output, never silently
treated as equivalent.

stage_a.py, measure.py, and TASK-20260809-a79e4f's matched_pair.py are
imported READ-ONLY via matched_pair.py's own load_module() pattern. None of
the three files is modified on disk.

Claim tier: TOY, hard ceiling. PS-R3 only. Nothing here is a statement about
HQC, A17, its decoding-failure rate, or any standardized parameter set.

A timeout, crash, missing dependency or budget exhaustion is an
INFRASTRUCTURE outcome and is never evidence about the mathematics
(AGENTS.md rule 5).

Re-run:
    PYTHONDONTWRITEBYTECODE=1 python3 shard_8001_8002_discard_prefix.py --out-dir .
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

# sha256 pins -- identical values matched_pair.py, matched_pair_repeat.py and
# every prior arm in this campaign pinned for these two files (independently
# re-verified by this task at run time via load_module()).
STAGE_A_PY_EXPECTED_SHA256 = (
    "06a0a618432c00fe26c72ecf05a8d89489db61c5183931fdb76a378717681405")
MEASURE_PY_EXPECTED_SHA256 = (
    "a4fd1ecb63f0ddc83c02ef45f2c65ab31cf13d13e7ae94f500e67465b24f5dc8")
# matched_pair.py's expected pin, cited from TASK-20260814-8bbdd2's own
# measured/self-consistency-pinned value (that task's own recommendation:
# "the measured value is what future tasks in this family should cite").
MATCHED_PAIR_PY_EXPECTED_SHA256 = (
    "66266a6178eb46e0b37ec0afdb2620064db56bff82318498e2dd83af1bd1c821")

SET_ID = "PS-R3"
M = 17                       # load-bearing order, primary cell
K_RANGE_AUTHORIZED = list(range(2, 27))

SHARD_8001 = 8001
SHARD_8002 = 8002
N_DISCARD_PREFIX = 10000
N_NEW = 20000
N_TOTAL_PER_CALL = N_DISCARD_PREFIX + N_NEW   # 30000
N_VERIFICATION = 10000

BATCH = 64
WALL_CAP_PER_CALL = 600.0
CORE_SECOND_BUDGET = 500.0
WALL_SECOND_BUDGET = 1800.0

# Prior task's committed T=10,000 single-shard se_paired at k=17, read here
# for report convenience (also re-read from PRIOR_RESULTS_JSON at run time,
# not fabricated).
PRIOR_SE_10000 = {
    SHARD_8001: None,  # filled from committed JSON at run time
    SHARD_8002: None,
}


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
    never opened for writing. Locally re-defined (not imported via
    matched_pair.py's own load_module) because that function cannot be used
    to sha256-verify-and-load matched_pair.py itself before it has been
    loaded -- the same bootstrap chicken-and-egg problem
    TASK-20260814-8bbdd2 hit and disclosed (design.md Section 1;
    EV-HQC-469c08 O10)."""
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


def _stats_to_arrays(stats):
    """matched_pair_stats' returned dict, as float64 numpy arrays keyed by k,
    for exact comparison against committed JSON values (which are plain
    Python floats/None)."""
    return {k: dict(
        point_defected=stats["point_defected"][i],
        point_undefected=stats["point_undefected"][i],
        diff=stats["diff"][i],
        se_paired=stats["se_paired"][i],
        se_unpaired=stats["se_unpaired"][i],
        z_paired=stats["z_paired"][i],
        z_unpaired=stats["z_unpaired"][i],
        unpaired_over_paired_ratio=stats["unpaired_over_paired_ratio"][i],
    ) for i, k in enumerate(stats["ks"])}


def _exact_or_none_equal(a, b):
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    return a == b


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=HERE)
    args = ap.parse_args(argv)
    out_path = os.path.join(args.out_dir, "shard_8001_8002_discard_prefix_results.json")

    t_wall0, c_wall0 = time.time(), core_seconds()
    R = {
        "task_id": "TASK-20260815-e61cca",
        "role": "executor",
        "experiment_id": "EXP-HQC-982268",
        "hypothesis_id": "H-HQC-18d1b4",
        "goal": "GOAL-HQC-001",
        "batch": "BATCH-174014",
        "claim_tier": "toy",
        "part": "A",
        "scope_statement": (
            "TOY, hard ceiling. PS-R3 only. One defect class (V3, "
            "last-block-window-read-early), one injection point "
            "(decode_blocks's block window, last block only). Shards 8001 "
            "and 8002 INDIVIDUALLY, NO cross-shard pooling anywhere in this "
            "script. Trial indices [10000, 30000) retained per shard "
            "(discarded prefix [0, 10000) computed but excluded from every "
            "statistic). NOTHING here is a statement about HQC, A17, A5, "
            "any decoding-failure rate, or any standardized parameter set."),
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
        "n_verification": N_VERIFICATION,
        "shards": [SHARD_8001, SHARD_8002],
        "retained_slice": "[10000:30000)",
        "discarded_slice": "[0:10000)",
        "disjointness_proof_strength_note": (
            "WEAKER than TASK-20260814-8bbdd2's direct bit-identical-array-"
            "vs-committed-record check, because TASK-20260809-a79e4f stage 2 "
            "never persisted a raw per-trial S array for shards 8001/8002. "
            "See design.md Section 3 for the full argument; not silently "
            "treated as equivalent anywhere in this script's output."),
    }

    # ---- phase 1: real, sha256-pinned, read-only module loads ------------
    sa, sa_sha = load_module_fail_closed(
        STAGE_A_PY, STAGE_A_PY_EXPECTED_SHA256, "stage_a.py",
        "stage_a_frozen_shard_8001_8002")
    measure, measure_sha = load_module_fail_closed(
        MEASURE_PY, MEASURE_PY_EXPECTED_SHA256, "measure.py",
        "measure_frozen_shard_8001_8002")
    mp_mod, mp_sha = load_module_fail_closed(
        MATCHED_PAIR_PY, MATCHED_PAIR_PY_EXPECTED_SHA256, "matched_pair.py",
        "matched_pair_frozen_shard_8001_8002")

    R["provenance"] = dict(
        stage_a_path=os.path.relpath(STAGE_A_PY, REPO), stage_a_sha256=sa_sha,
        stage_a_sha256_expected=STAGE_A_PY_EXPECTED_SHA256,
        stage_a_sha256_match=(sa_sha == STAGE_A_PY_EXPECTED_SHA256),
        measure_path=os.path.relpath(MEASURE_PY, REPO), measure_sha256=measure_sha,
        measure_sha256_expected=MEASURE_PY_EXPECTED_SHA256,
        measure_sha256_match=(measure_sha == MEASURE_PY_EXPECTED_SHA256),
        matched_pair_py_path=os.path.relpath(MATCHED_PAIR_PY, REPO),
        matched_pair_py_sha256_measured=mp_sha,
        matched_pair_py_sha256_expected=MATCHED_PAIR_PY_EXPECTED_SHA256,
        matched_pair_py_sha256_match=(mp_sha == MATCHED_PAIR_PY_EXPECTED_SHA256),
        prior_results_json_path=os.path.relpath(PRIOR_RESULTS_JSON, REPO),
        prior_results_json_sha256=sha256_file(PRIOR_RESULTS_JSON),
        stage_a_modified=False, measure_modified=False, matched_pair_py_modified=False,
        bootstrap_utility_functions_note=(
            "sha256_file, core_seconds, git_state and load_module_fail_closed "
            "are LOCALLY RE-DEFINED in this script, not imported via mp_mod.*, "
            "for the same bootstrap chicken-and-egg reason "
            "TASK-20260814-8bbdd2 disclosed (EV-HQC-469c08 O10). "
            "make_defected_decode_blocks, matched_pair_stats, arm_hists, cell "
            "and run_arm ARE genuinely imported via mp_mod.*, never "
            "re-derived."))

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
        mechanism="design.md Section 3/4, fixed before this run")

    NB = sa.N_JACK_BATCHES  # 200
    with open(PRIOR_RESULTS_JSON) as fh:
        prior = json.load(fh)
    committed_stage2_hard_inv = prior["stage_2"]["hard_invariants"]
    committed_stage2_matched_pair = prior["stage_2"]["matched_pair"]["per_shard"]

    shards = (SHARD_8001, SHARD_8002)
    variants = (("defected", defected_decode_blocks),
                ("undefected", original_decode_blocks))

    # ---- phase 3: FOUR DEDICATED VERIFICATION CALLS at n_trials=10000,
    #      one per (shard, variant), BEFORE any analysis call ---------------
    verification_calls = {}
    verification_d2_d3 = []
    for shard in shards:
        for variant, decode_fn in variants:
            r = mp_mod.run_arm(sa, ps, shard, N_VERIFICATION, decode_fn,
                               original_decode_blocks)
            verification_calls[(shard, variant)] = r
            verification_d2_d3.append((f"shard_{shard}_{variant}", r))
            print(f"[verify-call] shard={shard} variant={variant} "
                  f"trials_done={r['trials_done']} truncated={r['truncated']}",
                  flush=True)

    R["verification_hard_invariants"] = {
        tag: dict(D2_violations=r["d2_fail"], D3_violations=r["d3_fail"],
                  D3_cap=r["d3_cap"], D3_max_w=r["d3_max_w"])
        for tag, r in verification_d2_d3}
    verification_d2_d3_clean = all(
        r["d2_fail"] == 0 and r["d3_fail"] == 0 for _, r in verification_d2_d3)
    verification_any_truncated = any(r["truncated"] for _, r in verification_d2_d3)
    verification_all_full_length = all(
        r["trials_done"] == N_VERIFICATION for _, r in verification_d2_d3)

    # Step 1: verification call D2/D3/D3_cap/D3_max_w vs committed stage_2 --
    step1_hard_invariant_checks = []
    step1_hard_invariant_all_pass = True
    for tag, r in verification_d2_d3:
        committed = committed_stage2_hard_inv[tag]
        measured = dict(D2_violations=r["d2_fail"], D3_violations=r["d3_fail"],
                        D3_cap=r["d3_cap"], D3_max_w=r["d3_max_w"])
        ok = (measured["D2_violations"] == committed["D2_violations"]
              and measured["D3_violations"] == committed["D3_violations"]
              and measured["D3_cap"] == committed["D3_cap"]
              and measured["D3_max_w"] == committed["D3_max_w"])
        step1_hard_invariant_all_pass &= ok
        step1_hard_invariant_checks.append(dict(
            key=tag, measured=measured, committed=committed,
            verdict="PASS" if ok else "FAIL"))

    # Compute per-shard matched_pair_stats from the verification calls (per
    # shard, defected vs undefected on the SAME shard, exactly as stage 2
    # itself did) and compare to committed stage_2 per-shard values.
    step1_stats_checks = []
    step1_stats_all_pass = True
    verification_S = {}
    for shard in shards:
        S_def = verification_calls[(shard, "defected")]["F"].sum(axis=1).astype(np.int64)
        S_undef = verification_calls[(shard, "undefected")]["F"].sum(axis=1).astype(np.int64)
        verification_S[(shard, "defected")] = S_def
        verification_S[(shard, "undefected")] = S_undef
        H_def, B_def = mp_mod.arm_hists(sa, S_def, n_e, NB)
        H_undef, B_undef = mp_mod.arm_hists(sa, S_undef, n_e, NB)
        ks = sorted((set(sa.evaluable_k(H_def, n_e))
                    & set(sa.evaluable_k(H_undef, n_e))
                    & set(K_RANGE_AUTHORIZED)))
        C = measure.comb_matrix(n_e, ks) if ks else None
        stats = (mp_mod.matched_pair_stats(measure, n_e, ks, C, H_def, B_def, H_undef, B_undef)
                 if ks else None)
        measured_by_k = _stats_to_arrays(stats) if stats else {}
        committed_shard = committed_stage2_matched_pair[f"shard_{shard}"]
        committed_by_k = dict(zip(committed_shard["ks"], [
            dict(point_defected=committed_shard["point_defected"][i],
                 point_undefected=committed_shard["point_undefected"][i],
                 diff=committed_shard["diff"][i],
                 se_paired=committed_shard["se_paired"][i],
                 se_unpaired=committed_shard["se_unpaired"][i],
                 z_paired=committed_shard["z_paired"][i],
                 z_unpaired=committed_shard["z_unpaired"][i],
                 unpaired_over_paired_ratio=committed_shard["unpaired_over_paired_ratio"][i])
            for i in range(len(committed_shard["ks"]))]))
        per_k_pass = True
        mismatches = []
        all_ks = sorted(set(measured_by_k) | set(committed_by_k))
        for k in all_ks:
            m_ = measured_by_k.get(k)
            c_ = committed_by_k.get(k)
            if m_ is None or c_ is None:
                per_k_pass = False
                mismatches.append(dict(k=k, reason="k missing in one side",
                                        measured_present=m_ is not None,
                                        committed_present=c_ is not None))
                continue
            for field in ("point_defected", "point_undefected", "diff",
                          "se_paired", "se_unpaired", "z_paired", "z_unpaired",
                          "unpaired_over_paired_ratio"):
                if not _exact_or_none_equal(m_[field], c_[field]):
                    per_k_pass = False
                    mismatches.append(dict(k=k, field=field,
                                            measured=m_[field], committed=c_[field]))
        step1_stats_all_pass &= per_k_pass
        step1_stats_checks.append(dict(
            shard=shard, ks_measured=ks, ks_committed=committed_shard["ks"],
            bit_identical_all_k_all_fields=per_k_pass,
            mismatches=mismatches,
            verdict="PASS" if per_k_pass else "FAIL"))

    step1_overall_pass = (step1_hard_invariant_all_pass and step1_stats_all_pass
                          and verification_d2_d3_clean
                          and not verification_any_truncated
                          and verification_all_full_length)
    R["disjointness_proof"] = dict(
        step1_verification_vs_committed_statistics=dict(
            hard_invariant_checks=step1_hard_invariant_checks,
            hard_invariant_all_pass=step1_hard_invariant_all_pass,
            matched_pair_stats_checks=step1_stats_checks,
            matched_pair_stats_all_pass=step1_stats_all_pass,
            tolerance_used="EXACT (Python == on float64 values); no tolerance "
                            "was needed -- see note below for whether this held.",
            overall_status="PASS" if step1_overall_pass else "FAIL"))
    print(f"[disjointness_proof.step1] status={R['disjointness_proof']['step1_verification_vs_committed_statistics']['overall_status']}",
          flush=True)

    if not step1_overall_pass:
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
            reason=("Step 1 of the adapted disjointness proof FAILED: the "
                    "dedicated n_trials=10000 verification call's own "
                    "D2/D3/D3_cap/D3_max_w or recomputed matched_pair_stats "
                    "did not match TASK-20260809-a79e4f's committed stage_2 "
                    "values exactly. Per AGENTS.md rule 5 this is an "
                    "infrastructure/environment/determinism regression "
                    "signal and is NEVER reported as a result about the "
                    "mathematics. No analysis call was made; no matched-pair "
                    "statistic was computed from any retained tail."))
        R["finished_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with open(out_path, "w") as fh:
            json.dump(R, fh, indent=1)
        print(f"[ABORT] disjointness proof step 1 failed; wrote {out_path}", flush=True)
        return R

    # ---- phase 4: THE FOUR REAL (shard, variant) ANALYSIS CALLS, ONE
    #      _t_shard call each, n_trials = 30000 ------------------------------
    d2_d3_flags = []
    calls = {}
    for shard in shards:
        for variant, decode_fn in variants:
            r = mp_mod.run_arm(sa, ps, shard, N_TOTAL_PER_CALL, decode_fn,
                               original_decode_blocks)
            calls[(shard, variant)] = r
            d2_d3_flags.append((f"shard_{shard}_{variant}", r))
            print(f"[analysis-call] shard={shard} variant={variant} "
                  f"trials_done={r['trials_done']} truncated={r['truncated']}",
                  flush=True)

    R["analysis_hard_invariants"] = {tag: dict(D2_violations=r["d2_fail"],
                                      D3_violations=r["d3_fail"],
                                      D3_cap=r["d3_cap"], D3_max_w=r["d3_max_w"])
                            for tag, r in d2_d3_flags}
    d2_d3_clean = all(r["d2_fail"] == 0 and r["d3_fail"] == 0
                      for _, r in d2_d3_flags)
    any_truncated = any(r["truncated"] for _, r in d2_d3_flags)
    all_full_length = all(r["trials_done"] == N_TOTAL_PER_CALL for _, r in d2_d3_flags)

    # ---- phase 5: Step 2 -- within-task cross-call raw bit-identity ------
    S_full = {}
    F_full = {}
    for (shard, variant), r in calls.items():
        F_full[(shard, variant)] = r["F"]                    # (30000, n_e)
        S_full[(shard, variant)] = r["F"].sum(axis=1).astype(np.int64)

    step2_checks = []
    step2_all_pass = True
    for shard in shards:
        for variant, _ in variants:
            key = f"shard_{shard}_{variant}"
            S_prefix = S_full[(shard, variant)][:N_DISCARD_PREFIX]
            S_verification = verification_S[(shard, variant)]
            elementwise_match = bool(np.array_equal(S_prefix, S_verification))
            hist_prefix = sa.hist_of(S_prefix, n_e)
            hist_verification = sa.hist_of(S_verification, n_e)
            hist_match = bool(np.array_equal(hist_prefix, hist_verification))
            length_match = (len(S_prefix) == len(S_verification) == N_DISCARD_PREFIX
                            == N_VERIFICATION)
            ok = elementwise_match and hist_match and length_match
            step2_all_pass &= ok
            step2_checks.append(dict(
                key=key, length_match=length_match,
                elementwise_per_trial_S_bit_identical=elementwise_match,
                S_histogram_bit_identical=hist_match,
                prefix_length=int(len(S_prefix)),
                verification_length=int(len(S_verification)),
                verdict="PASS" if ok else "FAIL"))

    R["disjointness_proof"]["step2_analysis_prefix_vs_verification_raw"] = dict(
        rule=("For each of the 4 (shard, variant) pairs, the analysis call's "
              "own discarded prefix [0:10000) must be bit-identical, "
              "elementwise, to the SEPARATE, prior verification call's own "
              "raw per-trial S for the SAME (shard, variant), within this "
              "SAME task's own execution. This is a within-task determinism "
              "check, NOT a check against any externally committed raw "
              "array (none exists for these shards)."),
        checks=step2_checks,
        overall_status="PASS" if step2_all_pass else "FAIL")
    print(f"[disjointness_proof.step2] status={R['disjointness_proof']['step2_analysis_prefix_vs_verification_raw']['overall_status']}",
          flush=True)

    disjointness_all_pass = step1_overall_pass and step2_all_pass
    R["disjointness_proof"]["overall_status"] = "PASS" if disjointness_all_pass else "FAIL"
    R["disjointness_proof"]["limitation_note"] = (
        "This two-step check is WEAKER than TASK-20260814-8bbdd2's direct "
        "bit-identical-array-vs-committed-record check, which compared a "
        "freshly generated prefix directly against a raw array PERSISTED BY "
        "A DIFFERENT, EARLIER TASK'S RUN. Step 1 here only confirms a "
        "verification call made INSIDE THIS SAME task's own execution "
        "reproduces the committed DERIVED statistics (no raw array exists "
        "to compare against directly); Step 2 only confirms internal, "
        "within-task self-consistency between two calls in the SAME "
        "process, not agreement with any independently-generated or "
        "previously-committed raw data. See design.md Section 3 for the "
        "full argument. Not silently treated as equivalent to "
        "TASK-20260814-8bbdd2's check anywhere in this record.")

    if not disjointness_all_pass:
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
            reason=("Step 2 of the adapted disjointness proof FAILED: the "
                    "real n_trials=30000 analysis call's own discarded "
                    "prefix [0:10000) is not bit-identical to the separate, "
                    "prior verification call's own raw per-trial S for the "
                    "same (shard, variant), within this task's own "
                    "execution. Per AGENTS.md rule 5 this is an "
                    "infrastructure/environment/determinism regression "
                    "signal and is NEVER reported as a result about the "
                    "mathematics. No matched-pair statistic was computed "
                    "from any retained tail."))
        R["finished_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with open(out_path, "w") as fh:
            json.dump(R, fh, indent=1)
        print(f"[ABORT] disjointness proof step 2 failed; wrote {out_path}", flush=True)
        return R

    # ---- phase 6: THE STANDING F[:, 0:n_e-1] INVARIANT, on the RETAINED
    #      tail only (design.md Section 4) -------------------------------
    invariant_checks = []
    invariant_all_pass = True
    for shard in shards:
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
              "20,000-trial tail slice of each shard (EV-HQC-3a0372 O11)."),
        checks=invariant_checks,
        overall_status="PASS" if invariant_all_pass else "FAIL")
    print(f"[f_invariant_check] status={R['f_invariant_check']['overall_status']}", flush=True)

    # release the full F arrays now that both checks are done (memory)
    for k in list(F_full.keys()):
        F_full[k] = None

    # ---- phase 7: matched-pair statistics on the RETAINED tail, PER SHARD
    #      ONLY, NO POOLING ANYWHERE -----------------------------------------
    S_tail = {k: v[N_DISCARD_PREFIX:N_TOTAL_PER_CALL] for k, v in S_full.items()}
    R["per_trial_S_retained_tail_length"] = {
        f"shard_{s}_{v}": int(len(S_tail[(s, v)]))
        for s in shards for v in ("defected", "undefected")}

    H = {}
    B = {}
    for shard in shards:
        for variant in ("defected", "undefected"):
            H[(shard, variant)], B[(shard, variant)] = mp_mod.arm_hists(
                sa, S_tail[(shard, variant)], n_e, NB)

    stats_by_shard = {}
    ks_by_shard = {}
    for shard in shards:
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

    R["reachability"] = dict(
        evaluable_k_shard_8001=ks_by_shard[SHARD_8001],
        evaluable_k_shard_8002=ks_by_shard[SHARD_8002],
        load_bearing_order_m=M,
        m_reachable_shard_8001=(M in ks_by_shard[SHARD_8001]),
        m_reachable_shard_8002=(M in ks_by_shard[SHARD_8002]),
        note="NO POOLED evaluable_k reported anywhere in this file -- "
             "Part A never pools across shards.")

    R["matched_pair"] = dict(
        per_shard=dict(
            shard_8001=stats_by_shard[SHARD_8001],
            shard_8002=stats_by_shard[SHARD_8002]),
        pooled=None,
        pooled_note="DELIBERATELY NOT COMPUTED. design.md constraint: no "
                     "cross-shard pooling anywhere in Part A. The IVW "
                     "pooling alternative for 8001/8002 is computed "
                     "separately in Part B (ivw_pooling_check.py) from "
                     "already-committed data, not from this task's new "
                     "sampling.",
        primary_cell_k17=dict(
            shard_8001=(mp_mod.cell(stats_by_shard[SHARD_8001], M)
                       if stats_by_shard[SHARD_8001] and M in stats_by_shard[SHARD_8001]["ks"]
                       else None),
            shard_8002=(mp_mod.cell(stats_by_shard[SHARD_8002], M)
                       if stats_by_shard[SHARD_8002] and M in stats_by_shard[SHARD_8002]["ks"]
                       else None)))

    se_8001_new_k17 = (R["matched_pair"]["primary_cell_k17"]["shard_8001"]["se_paired"]
                       if R["matched_pair"]["primary_cell_k17"]["shard_8001"] else None)
    se_8002_new_k17 = (R["matched_pair"]["primary_cell_k17"]["shard_8002"]["se_paired"]
                       if R["matched_pair"]["primary_cell_k17"]["shard_8002"] else None)

    # ---- phase 8: single-shard-only (unpooled) local exponent, per shard,
    #      T=10000 (committed) -> T=20000-tail-based-T=? no: T=10000 -> new
    #      T=20000 is a DISJOINT sample, not a growing dataset (same
    #      convention as TASK-20260814-8bbdd2 O6) ---------------------------
    committed_se_10000 = {
        SHARD_8001: (committed_stage2_matched_pair["shard_8001"]["se_paired"][
            committed_stage2_matched_pair["shard_8001"]["ks"].index(M)]
            if M in committed_stage2_matched_pair["shard_8001"]["ks"] else None),
        SHARD_8002: (committed_stage2_matched_pair["shard_8002"]["se_paired"][
            committed_stage2_matched_pair["shard_8002"]["ks"].index(M)]
            if M in committed_stage2_matched_pair["shard_8002"]["ks"] else None),
    }
    committed_diff_10000 = {
        SHARD_8001: (committed_stage2_matched_pair["shard_8001"]["diff"][
            committed_stage2_matched_pair["shard_8001"]["ks"].index(M)]
            if M in committed_stage2_matched_pair["shard_8001"]["ks"] else None),
        SHARD_8002: (committed_stage2_matched_pair["shard_8002"]["diff"][
            committed_stage2_matched_pair["shard_8002"]["ks"].index(M)]
            if M in committed_stage2_matched_pair["shard_8002"]["ks"] else None),
    }

    def local_exponent(se_t1, t1, se_t2, t2):
        if se_t1 is None or se_t2 is None or se_t1 <= 0 or se_t2 <= 0:
            return None
        return -float(np.log(se_t2 / se_t1) / np.log(t2 / t1))

    single_shard_exponents = {}
    for shard, se_new in ((SHARD_8001, se_8001_new_k17), (SHARD_8002, se_8002_new_k17)):
        se_10k = committed_se_10000[shard]
        alpha = local_exponent(se_10k, 10000.0, se_new, 20000.0)
        single_shard_exponents[f"shard_{shard}"] = dict(
            T_committed=10000, se_paired_committed_k17=se_10k,
            diff_committed_k17=committed_diff_10000[shard],
            T_new=20000, se_paired_new_k17=se_new,
            diff_new_k17=(R["matched_pair"]["primary_cell_k17"][f"shard_{shard}"]["diff"]
                         if R["matched_pair"]["primary_cell_k17"][f"shard_{shard}"] else None),
            local_exponent_alpha=alpha,
            method="alpha = -[log(SE_20000) - log(SE_10000)] / [log(20000) - "
                   "log(10000)], exact 2-point OLS slope, same method "
                   "TASK-20260814-8bbdd2 used for shards 5000/6000 "
                   "(EV-HQC-469c08 O6). No cross-shard pooling anywhere in "
                   "this computation.",
            consistent_with_1_over_sqrt_T_band=[0.4, 0.6],
            note="Reported descriptively. No conclusion is drawn here about "
                 "which of DEC-20260809-186c86's two named outcomes obtains, "
                 "or whether this reflects shard-specific or general "
                 "estimator behaviour -- that is Coordinator/Validator/Red "
                 "Team judgment.")
    R["single_shard_only_local_exponent"] = single_shard_exponents

    # ---- phase 9: budget + validity ---------------------------------------
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
          and verification_d2_d3_clean and not verification_any_truncated
          and verification_all_full_length
          and se_8001_new_k17 is not None and se_8001_new_k17 > 0
          and se_8002_new_k17 is not None and se_8002_new_k17 > 0)
    R["validity"] = dict(
        status="valid_measurement" if ok else "invalid_measurement",
        failure_class=(None if ok else "invalid_measurement"),
        reason=("All pre-registered mechanically-sound criteria met "
                "(design.md Section 8): both fail-closed selftests PASS, "
                "wrapper genuinely calls the unmodified decode_blocks, the "
                "two-step adapted disjointness proof PASSES on all 4 "
                "(shard, variant) pairs, the F[:, 0:n_e-1] structural "
                "invariant PASSES on both shards, D2/D3 clean on all 8 "
                "calls (4 verification + 4 analysis), no call truncated, "
                "every call delivered its full requested trial count, each "
                "shard's own estimator returns a finite diff and finite "
                "positive SE_paired at k=17 on its retained tail."
                if ok else
                "One or more pre-registered mechanically-sound criteria "
                "(design.md Section 8) were not met -- see the individual "
                "gate fields above (disjointness_proof, f_invariant_check, "
                "hard_invariants, fail_closed_selftests) for which one."))

    R["finished_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(out_path, "w") as fh:
        json.dump(R, fh, indent=1)
    print(f"[done] -> {out_path}  core-s={spent_core:.2f}/{CORE_SECOND_BUDGET} "
          f"wall={spent_wall:.1f}s/{WALL_SECOND_BUDGET}s  "
          f"validity={R['validity']['status']}", flush=True)
    return R


if __name__ == "__main__":
    main()
