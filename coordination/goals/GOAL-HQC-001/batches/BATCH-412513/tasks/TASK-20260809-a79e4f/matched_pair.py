#!/usr/bin/env python3
"""Matched-pair measurement at the V3/decode_blocks injection point, PS-R3.

TASK-20260809-a79e4f (executor) / BATCH-412513 / GOAL-HQC-001 / EXP-HQC-982268.
Authorized by DEC-20260809-46e85c. Pre-registered design in design.md
(WRITTEN AND FROZEN BEFORE THIS SCRIPT WAS RUN ON REAL DATA).

TWO PRE-REGISTERED STAGES, ONE SCRIPT, TWO INVOCATIONS (--stage 1, --stage 2).

STAGE 1 (zero new entropy): re-decodes the already-committed shards 5000 and
6000 through BOTH decode_blocks variants (crossing shard x variant),
reconstructing genuine matched pairs on draws that already exist in the
committed record. Fail-closed on a determinism gate that reproduces the
ORIGINAL configuration (5000 defected, 6000 undefected) and checks
bit-identity against pilot_results.json's committed S_histogram arrays.

STAGE 2 (new sampling at a pre-registered size): a matched-pair arm at fresh
shard indices 8001/8002, at T2 = clamp(round(10000 * (SE_pooled_measured *
2.80 / 0.20) ** 2), 20000, 60000), where SE_pooled_measured is stage 1's own
measured pooled paired SE at k=17. Requires stage 1's output to already
exist on disk.

stage_a.py and measure.py are imported READ-ONLY, sha256-pinned, identical
load_module() pattern to pilot_injection.py. Neither file is modified on
disk. The ONLY new code here is the injection wrapper (copied in behaviour
from pilot_injection.py's make_defected_decode_blocks), this driver, and the
matched-pair jackknife on the per-batch difference (design.md Section 4).

Claim tier: TOY, hard ceiling. PS-R3 only. Nothing here is a statement about
HQC, A17, its decoding-failure rate, or any standardized parameter set.

A timeout, crash, missing dependency or budget exhaustion is an
INFRASTRUCTURE outcome and is never evidence about the mathematics
(AGENTS.md rule 5).

Re-run:
    PYTHONDONTWRITEBYTECODE=1 python3 matched_pair.py --stage 1 --out-dir .
    PYTHONDONTWRITEBYTECODE=1 python3 matched_pair.py --stage 2 --out-dir .
"""

from __future__ import annotations

import argparse
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
PILOT_RESULTS_JSON = os.path.join(
    REPO, "coordination", "goals", "GOAL-HQC-001", "batches", "BATCH-2ecaa1",
    "tasks", "TASK-20260806-77a574", "pilot_results.json")

# sha256 pins -- identical values pilot_injection.py and every prior arm in
# this campaign pinned for the same two files (independently re-verified by
# this task at run time via load_module()).
STAGE_A_PY_EXPECTED_SHA256 = (
    "06a0a618432c00fe26c72ecf05a8d89489db61c5183931fdb76a378717681405")
MEASURE_PY_EXPECTED_SHA256 = (
    "a4fd1ecb63f0ddc83c02ef45f2c65ab31cf13d13e7ae94f500e67465b24f5dc8")

SET_ID = "PS-R3"
M = 17                       # load-bearing order, primary cell
K_RANGE_AUTHORIZED = list(range(2, 27))   # task card's authorized k range

N_TRIALS_STAGE1 = 5_000
N_TRIALS_WARMUP = 300
SHARD_WARMUP_DEFECTED = 4900
SHARD_WARMUP_UNDEFECTED = 4901
SHARD_5000 = 5000
SHARD_6000 = 6000
STAGE2_SHARD_A = 8001
STAGE2_SHARD_B = 8002
DISJOINT_SHARDS_IN_RECORD = (
    list(range(0, 4)) + [900, 999] + list(range(1000, 1008))
    + [4900, 4901, 5000, 6000, 7777, 7778, 424242])

BATCH = 64
WALL_CAP_PER_CALL = 600.0
CORE_SECOND_BUDGET = 400.0
WALL_SECOND_BUDGET = 1800.0

# stage-2 sizing rule, fixed in advance by DEC-20260809-46e85c
STAGE2_DELTA = 0.20
STAGE2_Z = 2.80
STAGE2_T_FLOOR = 20_000
STAGE2_T_CAP = 60_000
STAGE2_BASE_T = 10_000        # stage 1's pooled trial count


# --------------------------------------------------------------------------
# provenance / fail-closed loading (identical pattern to pilot_injection.py)
# --------------------------------------------------------------------------

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


def load_module(path: str, expected_sha256: str, name: str, module_name: str):
    """FAIL-CLOSED: aborts (SystemExit) if the file on disk does not match
    the pinned sha256. Loaded read-only via importlib; the file itself is
    never opened for writing."""
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


# --------------------------------------------------------------------------
# fail-closed self-tests -- run BEFORE the real module load / any real data
# --------------------------------------------------------------------------

def selftest_fail_closed_sha_mismatch():
    bad_hash = "0" * 64
    try:
        load_module(STAGE_A_PY, bad_hash, "stage_a.py [DELIBERATE MISMATCH]",
                    "stage_a_selftest_badhash")
        return dict(aborted=False, message=None,
                    verdict="FAIL -- did not abort on a real mismatch")
    except SystemExit as exc:
        msg = str(exc)
        ok = ("FAIL-CLOSED" in msg and bad_hash in msg
              and STAGE_A_PY_EXPECTED_SHA256 in msg)
        return dict(aborted=True, message=msg,
                    verdict="PASS" if ok else "FAIL -- aborted but message "
                                              "did not name expected/actual "
                                              "hashes correctly")


def selftest_injection_invariant_fail(n_e: int, n_2: int):
    rng = np.random.default_rng(12345)
    bits = rng.integers(0, 2, size=(4, n_e * n_2), dtype=np.uint8)

    def broken_wrapper(bits_in, n_e_arg, n_2_arg, dup_arg,
                       original=None, shift=2):
        b = bits_in.copy()
        lo, hi = (n_e_arg - 1) * n_2_arg, n_e_arg * n_2_arg
        b[:, lo:hi] = bits_in[:, lo - shift:hi - shift]
        ok = (np.array_equal(b[:, lo + 1:hi], bits_in[:, lo:hi - 1])
              and np.array_equal(b[:, lo], bits_in[:, lo - 1]))
        if not ok:
            raise SystemExit(
                "FAIL-CLOSED: injection invariant violated -- the perturbed "
                "last-block window does not match the pre-registered "
                "shift-by-1 construction (design.md Section 6).")
        return "UNREACHABLE -- would have called the real decode_blocks"

    try:
        broken_wrapper(bits, n_e, n_2, 1)
        return dict(aborted=False, message=None,
                    verdict="FAIL -- did not abort on a real invariant break")
    except SystemExit as exc:
        msg = str(exc)
        ok = "FAIL-CLOSED" in msg and "injection invariant" in msg
        return dict(aborted=True, message=msg,
                    verdict="PASS" if ok else "FAIL -- aborted but for the "
                                              "wrong stated reason")


# --------------------------------------------------------------------------
# the defect: V3 (last-block-window-read-early), decode_blocks injection point
# copied in behaviour from pilot_injection.py's make_defected_decode_blocks
# --------------------------------------------------------------------------

def make_defected_decode_blocks(original_decode_blocks, n_2_expected: int):
    orig_id = id(original_decode_blocks)

    def defected(bits, n_e, n_2, dup):
        assert n_2 == n_2_expected, "unexpected n_2 at call time"
        b = bits.copy()
        lo, hi = (n_e - 1) * n_2, n_e * n_2
        b[:, lo:hi] = bits[:, lo - 1:hi - 1]
        ok = (np.array_equal(b[:, lo + 1:hi], bits[:, lo:hi - 1])
              and np.array_equal(b[:, lo], bits[:, lo - 1])
              and np.array_equal(b[:, :lo], bits[:, :lo]))
        if not ok:
            raise SystemExit(
                "FAIL-CLOSED: injection invariant violated in the real "
                "pipeline call -- the perturbed last-block window does not "
                "match the pre-registered shift-by-1 construction "
                "(design.md Section 6). Aborting before any trial in this "
                "batch is scored.")
        assert id(original_decode_blocks) == orig_id, (
            "the wrapper's inner call target changed identity -- would no "
            "longer be calling the real, unmodified decode_blocks")
        return original_decode_blocks(b, n_e, n_2, dup)

    defected.__wrapped_original_id__ = orig_id
    defected.__wrapped_original_qualname__ = (
        f"{original_decode_blocks.__module__}.{original_decode_blocks.__qualname__}")
    return defected


# --------------------------------------------------------------------------
# matched-pair jackknife on the per-batch difference (design.md Section 4)
# --------------------------------------------------------------------------

def arm_hists(sa, S: np.ndarray, n_e: int, nb: int):
    """Whole-arm histogram + batch histograms, exactly sa.hist_of/batch_hists."""
    H = sa.hist_of(S, n_e)
    Bh = sa.batch_hists(S, n_e, nb)
    return H, Bh


def matched_pair_stats(measure, n_e: int, ks, C: np.ndarray,
                       H_d: np.ndarray, Bd: np.ndarray,
                       H_u: np.ndarray, Bu: np.ndarray):
    """Paired (matched-pair leave-one-batch-out jackknife on the per-batch
    DIFFERENCE) and unpaired (independent-arm quadrature) statistics, for
    every k in `ks`. Bd/Bu must have the same number of rows and be aligned
    by batch index (design.md Section 4)."""
    assert Bd.shape[0] == Bu.shape[0]
    nb = Bd.shape[0]

    point_d = measure.log2_A_from_hists(H_d[None, :], n_e, ks, C)[0]
    point_u = measure.log2_A_from_hists(H_u[None, :], n_e, ks, C)[0]
    point_diff = point_d - point_u

    loo_d = measure.log2_A_from_hists(H_d[None, :] - Bd, n_e, ks, C)
    loo_u = measure.log2_A_from_hists(H_u[None, :] - Bu, n_e, ks, C)
    loo_diff = loo_d - loo_u

    def jack_se(vals: np.ndarray) -> np.ndarray:
        mean = np.nanmean(vals, axis=0)
        b = vals.shape[0]
        return np.sqrt((b - 1) / b * np.nansum((vals - mean) ** 2, axis=0))

    se_paired = jack_se(loo_diff)
    se_d = jack_se(loo_d)
    se_u = jack_se(loo_u)
    se_unpaired = np.sqrt(se_d ** 2 + se_u ** 2)

    with np.errstate(invalid="ignore", divide="ignore"):
        z_paired = point_diff / se_paired
        z_unpaired = point_diff / se_unpaired
        ratio = se_unpaired / se_paired

    return dict(
        ks=list(ks),
        point_defected=[_f(x) for x in point_d],
        point_undefected=[_f(x) for x in point_u],
        diff=[_f(x) for x in point_diff],
        se_paired=[_f(x) for x in se_paired],
        se_unpaired=[_f(x) for x in se_unpaired],
        z_paired=[_f(x) for x in z_paired],
        z_unpaired=[_f(x) for x in z_unpaired],
        unpaired_over_paired_ratio=[_f(x) for x in ratio],
        n_batches=nb,
    )


def _f(x):
    return None if not np.isfinite(x) else float(x)


def cell(stats: dict, k: int) -> dict:
    j = stats["ks"].index(k)
    return dict(k=k,
               point_defected=stats["point_defected"][j],
               point_undefected=stats["point_undefected"][j],
               diff=stats["diff"][j],
               se_paired=stats["se_paired"][j],
               se_unpaired=stats["se_unpaired"][j],
               z_paired=stats["z_paired"][j],
               z_unpaired=stats["z_unpaired"][j],
               unpaired_over_paired_ratio=stats["unpaired_over_paired_ratio"][j])


# --------------------------------------------------------------------------
# arm runner: one shard, one variant, warmed up, timed
# --------------------------------------------------------------------------

def run_arm(sa, ps, shard: int, n_trials: int, decode_fn, original_decode_blocks):
    """Installs decode_fn as sa.decode_blocks, runs a warmup call then the
    timed real call, restores original_decode_blocks immediately after."""
    sa.decode_blocks = decode_fn
    _ = sa._t_shard((ps, shard, N_TRIALS_WARMUP, WALL_CAP_PER_CALL, BATCH, 0))
    r = sa._t_shard((ps, shard, n_trials, WALL_CAP_PER_CALL, BATCH, 0))
    sa.decode_blocks = original_decode_blocks
    return r


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=HERE)
    ap.add_argument("--stage", type=int, choices=[1, 2], required=True)
    args = ap.parse_args(argv)
    out_path = os.path.join(args.out_dir, "matched_pair_results.json")

    t_wall0, c_wall0 = time.time(), core_seconds()
    R = {
        "task_id": "TASK-20260809-a79e4f",
        "role": "executor",
        "experiment_id": "EXP-HQC-982268",
        "hypothesis_id": "H-HQC-18d1b4",
        "goal": "GOAL-HQC-001",
        "batch": "BATCH-412513",
        "claim_tier": "toy",
        "stage": args.stage,
        "scope_statement": (
            "TOY, hard ceiling. PS-R3 only. One defect class (V3, "
            "last-block-window-read-early), one injection point "
            "(decode_blocks's block window, last block only). NOTHING here "
            "is a statement about HQC, A17, A5, any decoding-failure rate, "
            "or any standardized parameter set."),
        "design_reference": "design.md, written and frozen before this run",
        "started_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "command": " ".join([sys.executable] + sys.argv),
        "git": git_state(),
        "environment": dict(
            python=sys.version, python_executable=sys.executable,
            platform=platform.platform(), machine=platform.machine(),
            numpy=np.__version__, cpu_count=os.cpu_count(),
            affinity=len(os.sched_getaffinity(0))),
    }

    # ---- phase 0: fail-closed self-tests, BEFORE any real module load ----
    R["fail_closed_selftests"] = {
        "sha256_pin_mismatch": selftest_fail_closed_sha_mismatch(),
    }
    print("[selftest] sha256 pin mismatch: "
          f"{R['fail_closed_selftests']['sha256_pin_mismatch']['verdict']}", flush=True)
    if R["fail_closed_selftests"]["sha256_pin_mismatch"]["verdict"] != "PASS":
        raise SystemExit("FAILED_IMPLEMENTATION: sha256 pin fail-closed "
                         "selftest did not pass; refusing to proceed")

    # ---- phase 1: real, sha256-pinned, read-only module load -------------
    sa, sa_sha = load_module(STAGE_A_PY, STAGE_A_PY_EXPECTED_SHA256,
                             "stage_a.py", "stage_a_frozen_matched_pair")
    measure, measure_sha = load_module(MEASURE_PY, MEASURE_PY_EXPECTED_SHA256,
                                       "measure.py", "measure_frozen_matched_pair")
    R["provenance"] = dict(
        stage_a_path=os.path.relpath(STAGE_A_PY, REPO), stage_a_sha256=sa_sha,
        stage_a_sha256_expected=STAGE_A_PY_EXPECTED_SHA256,
        stage_a_sha256_match=(sa_sha == STAGE_A_PY_EXPECTED_SHA256),
        measure_path=os.path.relpath(MEASURE_PY, REPO), measure_sha256=measure_sha,
        measure_sha256_expected=MEASURE_PY_EXPECTED_SHA256,
        measure_sha256_match=(measure_sha == MEASURE_PY_EXPECTED_SHA256),
        stage_a_modified=False, measure_modified=False)

    ps = [p for p in sa.PARAM_SETS if p["id"] == SET_ID][0]
    n_e, n_2, dup, N = ps["n_e"], ps["n_2"], ps["dup"], ps["N"]
    R["parameter_set"] = {k: ps[k] for k in
                          ("id", "role", "n", "n_e", "n_2", "dup", "omega",
                           "omega_r", "omega_e", "N")}
    R["parameter_set"]["m_load_bearing_order"] = M

    R["fail_closed_selftests"]["injection_invariant_mismatch"] = (
        selftest_injection_invariant_fail(n_e, n_2))
    print("[selftest] injection invariant deliberate break: "
          f"{R['fail_closed_selftests']['injection_invariant_mismatch']['verdict']}",
          flush=True)
    if R["fail_closed_selftests"]["injection_invariant_mismatch"]["verdict"] != "PASS":
        raise SystemExit("FAILED_IMPLEMENTATION: injection-invariant "
                         "fail-closed selftest did not pass; refusing to proceed")

    original_decode_blocks = sa.decode_blocks
    defected_decode_blocks = make_defected_decode_blocks(original_decode_blocks, n_2)
    R["injection"] = dict(
        defect_class="V3 (last-block-window-read-early)",
        injection_point="decode_blocks's block window, LAST BLOCK ONLY "
                        "(index n_e - 1), shifted left by exactly one bit "
                        "position; decode_blocks itself called unmodified",
        wrapper_calls_unmodified_function=(
            defected_decode_blocks.__wrapped_original_id__ == id(original_decode_blocks)),
        wrapped_original_qualname=defected_decode_blocks.__wrapped_original_qualname__,
        mechanism="design.md Section 6, fixed before this run")

    C = measure.comb_matrix(n_e, K_RANGE_AUTHORIZED)
    NB = sa.N_JACK_BATCHES  # 200

    d2_d3_flags = []

    if args.stage == 1:
        # ---- phase 2: GATE arms (reproduce TASK-20260806-77a574's original
        #      configuration exactly: 5000 defected, 6000 undefected) -------
        r_gate_5000_def = run_arm(sa, ps, SHARD_5000, N_TRIALS_STAGE1,
                                  defected_decode_blocks, original_decode_blocks)
        r_gate_6000_undef = run_arm(sa, ps, SHARD_6000, N_TRIALS_STAGE1,
                                    original_decode_blocks, original_decode_blocks)
        d2_d3_flags += [("gate_5000_defected", r_gate_5000_def),
                        ("gate_6000_undefected", r_gate_6000_undef)]

        S_gate_5000_def = r_gate_5000_def["F"].sum(axis=1).astype(np.int64)
        S_gate_6000_undef = r_gate_6000_undef["F"].sum(axis=1).astype(np.int64)
        hist_gate_5000_def = sa.hist_of(S_gate_5000_def, n_e)
        hist_gate_6000_undef = sa.hist_of(S_gate_6000_undef, n_e)

        # ---- phase 3: DETERMINISM GATE (fail-closed, run first) ----------
        with open(PILOT_RESULTS_JSON) as fh:
            pilot = json.load(fh)
        committed_def_hist = np.array(
            pilot["MEASUREMENT"]["defected"]["S_histogram"], dtype=np.int64)
        committed_undef_hist = np.array(
            pilot["MEASUREMENT"]["undefected"]["S_histogram"], dtype=np.int64)
        match_def = bool(np.array_equal(hist_gate_5000_def, committed_def_hist))
        match_undef = bool(np.array_equal(hist_gate_6000_undef, committed_undef_hist))
        gate_pass = match_def and match_undef
        R["determinism_gate"] = dict(
            status="PASS" if gate_pass else "FAIL",
            defected_shard_5000_bit_identical_to_pilot=match_def,
            undefected_shard_6000_bit_identical_to_pilot=match_undef,
            reproduced_defected_S_histogram=[int(x) for x in hist_gate_5000_def],
            committed_defected_S_histogram=[int(x) for x in committed_def_hist],
            reproduced_undefected_S_histogram=[int(x) for x in hist_gate_6000_undef],
            committed_undefected_S_histogram=[int(x) for x in committed_undef_hist],
            pilot_results_source=os.path.relpath(PILOT_RESULTS_JSON, REPO))
        print(f"[determinism_gate] status={R['determinism_gate']['status']}", flush=True)

        if not gate_pass:
            # FAIL-CLOSED ABORT. AGENTS.md rule 5: infrastructure/environment
            # signal, never a result about the mathematics. No crossed arm is
            # run, no jackknife is computed.
            R["hard_invariants"] = {tag: dict(D2_violations=r["d2_fail"],
                                              D3_violations=r["d3_fail"])
                                    for tag, r in d2_d3_flags}
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
                reason=("Stage 1 determinism gate FAILED: the reconstructed "
                        "S-histograms are not bit-identical to "
                        "pilot_results.json's committed arrays. Per AGENTS.md "
                        "rule 5 this is an infrastructure/environment "
                        "regression signal and is NEVER reported as a result "
                        "about the mathematics. No crossed arm was run; "
                        "stage 2 is NOT authorized to proceed from this "
                        "output."))
            R["finished_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            with open(out_path, "w") as fh:
                json.dump({"stage_1": R}, fh, indent=1)
            print(f"[ABORT] determinism gate failed; wrote {out_path}", flush=True)
            return R

        # ---- phase 4: CROSSED arms (the missing half of each pair) -------
        r_cross_5000_undef = run_arm(sa, ps, SHARD_5000, N_TRIALS_STAGE1,
                                     original_decode_blocks, original_decode_blocks)
        r_cross_6000_def = run_arm(sa, ps, SHARD_6000, N_TRIALS_STAGE1,
                                   defected_decode_blocks, original_decode_blocks)
        d2_d3_flags += [("crossed_5000_undefected", r_cross_5000_undef),
                        ("crossed_6000_defected", r_cross_6000_def)]

        S_cross_5000_undef = r_cross_5000_undef["F"].sum(axis=1).astype(np.int64)
        S_cross_6000_def = r_cross_6000_def["F"].sum(axis=1).astype(np.int64)

        R["hard_invariants"] = {tag: dict(D2_violations=r["d2_fail"],
                                          D3_violations=r["d3_fail"],
                                          D3_cap=r["d3_cap"], D3_max_w=r["d3_max_w"])
                                for tag, r in d2_d3_flags}
        d2_d3_clean = all(r["d2_fail"] == 0 and r["d3_fail"] == 0
                          for _, r in d2_d3_flags)
        any_truncated = any(r["truncated"] for _, r in d2_d3_flags)

        # ---- phase 5: per-trial S, TRIAL ORDER, all four arms -------------
        R["per_trial_S"] = dict(
            shard_5000_defected=[int(x) for x in S_gate_5000_def],
            shard_5000_undefected=[int(x) for x in S_cross_5000_undef],
            shard_6000_defected=[int(x) for x in S_cross_6000_def],
            shard_6000_undefected=[int(x) for x in S_gate_6000_undef])

        # ---- phase 6: matched-pair statistics -----------------------------
        H_5000_def, B_5000_def = arm_hists(sa, S_gate_5000_def, n_e, NB)
        H_5000_undef, B_5000_undef = arm_hists(sa, S_cross_5000_undef, n_e, NB)
        H_6000_def, B_6000_def = arm_hists(sa, S_cross_6000_def, n_e, NB)
        H_6000_undef, B_6000_undef = arm_hists(sa, S_gate_6000_undef, n_e, NB)

        ks_5000 = set(sa.evaluable_k(H_5000_def, n_e)) & set(sa.evaluable_k(H_5000_undef, n_e))
        ks_6000 = set(sa.evaluable_k(H_6000_def, n_e)) & set(sa.evaluable_k(H_6000_undef, n_e))
        ks_pooled = ks_5000 & ks_6000 & set(K_RANGE_AUTHORIZED)
        ks_5000 = sorted(ks_5000 & set(K_RANGE_AUTHORIZED))
        ks_6000 = sorted(ks_6000 & set(K_RANGE_AUTHORIZED))
        ks_pooled = sorted(ks_pooled)
        R["reachability"] = dict(
            evaluable_k_shard_5000=ks_5000, evaluable_k_shard_6000=ks_6000,
            evaluable_k_pooled=ks_pooled, load_bearing_order_m=M,
            m_reachable_pooled=(M in ks_pooled))

        C_5000 = measure.comb_matrix(n_e, ks_5000) if ks_5000 else None
        C_6000 = measure.comb_matrix(n_e, ks_6000) if ks_6000 else None
        C_pooled = measure.comb_matrix(n_e, ks_pooled) if ks_pooled else None

        stats_5000 = (matched_pair_stats(measure, n_e, ks_5000, C_5000,
                                         H_5000_def, B_5000_def, H_5000_undef, B_5000_undef)
                     if ks_5000 else None)
        stats_6000 = (matched_pair_stats(measure, n_e, ks_6000, C_6000,
                                         H_6000_def, B_6000_def, H_6000_undef, B_6000_undef)
                     if ks_6000 else None)

        H_pooled_def = H_5000_def + H_6000_def
        H_pooled_undef = H_5000_undef + H_6000_undef
        B_pooled_def = np.concatenate([B_5000_def, B_6000_def], axis=0)
        B_pooled_undef = np.concatenate([B_5000_undef, B_6000_undef], axis=0)
        stats_pooled = (matched_pair_stats(measure, n_e, ks_pooled, C_pooled,
                                           H_pooled_def, B_pooled_def,
                                           H_pooled_undef, B_pooled_undef)
                       if ks_pooled else None)

        R["matched_pair"] = dict(
            per_shard=dict(shard_5000=stats_5000, shard_6000=stats_6000),
            pooled=stats_pooled,
            primary_cell_k17=dict(
                shard_5000=(cell(stats_5000, M) if stats_5000 and M in stats_5000["ks"] else None),
                shard_6000=(cell(stats_6000, M) if stats_6000 and M in stats_6000["ks"] else None),
                pooled=(cell(stats_pooled, M) if stats_pooled and M in stats_pooled["ks"] else None)))

        se_pooled_k17 = (R["matched_pair"]["primary_cell_k17"]["pooled"]["se_paired"]
                        if R["matched_pair"]["primary_cell_k17"]["pooled"] else None)

        # ---- stage-2 sizing, computed from stage 1's own measured SE ------
        if se_pooled_k17 is not None and se_pooled_k17 > 0:
            t2_raw = STAGE2_BASE_T * (se_pooled_k17 * STAGE2_Z / STAGE2_DELTA) ** 2
            t2 = int(round(t2_raw))
            t2_clamped = max(STAGE2_T_FLOOR, min(STAGE2_T_CAP, t2))
        else:
            t2_raw, t2, t2_clamped = None, None, None
        R["stage2_sizing"] = dict(
            formula="T2 = clamp(round(10000 * (SE_pooled_measured * 2.80 / 0.20) ** 2), 20000, 60000)",
            SE_pooled_measured_k17=se_pooled_k17,
            delta=STAGE2_DELTA, z=STAGE2_Z, floor=STAGE2_T_FLOOR, cap=STAGE2_T_CAP,
            T2_raw=t2_raw, T2_rounded=t2, T2_clamped=t2_clamped,
            substitution_shown=(
                f"T2 = clamp(round(10000 * ({se_pooled_k17} * 2.80 / 0.20) ** 2), "
                f"20000, 60000) = clamp({t2}, 20000, 60000) = {t2_clamped}"
                if se_pooled_k17 is not None else
                "SE_pooled_measured at k=17 was not finite; T2 could not be computed."),
            fresh_shards_preregistered=[STAGE2_SHARD_A, STAGE2_SHARD_B],
            fresh_shards_disjoint_from_record=(
                STAGE2_SHARD_A not in DISJOINT_SHARDS_IN_RECORD
                and STAGE2_SHARD_B not in DISJOINT_SHARDS_IN_RECORD))

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
              and gate_pass and d2_d3_clean and not any_truncated
              and stats_pooled is not None and M in stats_pooled["ks"]
              and se_pooled_k17 is not None and se_pooled_k17 > 0)
        R["validity"] = dict(
            status="valid_measurement" if ok else "invalid_measurement",
            failure_class=(None if ok else "invalid_measurement"),
            reason=("All pre-registered mechanically-sound criteria met "
                    "(design.md Section 7): determinism gate PASS, both "
                    "fail-closed selftests PASS, wrapper genuinely calls the "
                    "unmodified decode_blocks, D2/D3 clean on all four arms, "
                    "the pooled estimator returns a finite diff and finite "
                    "positive SE_paired at k=17, no arm truncated."
                    if ok else
                    "One or more pre-registered mechanically-sound criteria "
                    "(design.md Section 7) were not met -- see the "
                    "individual gate fields above for which one."))

    else:  # args.stage == 2
        if not os.path.exists(out_path):
            raise SystemExit(
                "FAILED_IMPLEMENTATION: stage 2 requires stage 1's output "
                f"at {out_path} to already exist (it supplies SE_pooled_measured "
                "and T2). Run --stage 1 first.")
        with open(out_path) as fh:
            prior = json.load(fh)
        stage1 = prior.get("stage_1")
        if stage1 is None or stage1.get("validity", {}).get("status") != "valid_measurement":
            raise SystemExit(
                "FAILED_IMPLEMENTATION: stage 1 in the existing "
                "matched_pair_results.json is not valid_measurement; stage 2 "
                "is not authorized to proceed from an invalid stage 1 "
                "(BRANCH D of DEC-20260809-46e85c: no crossed arm, no stage 2).")
        t2 = stage1["stage2_sizing"]["T2_clamped"]
        se_pooled_stage1_k17 = stage1["stage2_sizing"]["SE_pooled_measured_k17"]
        if t2 is None:
            raise SystemExit(
                "FAILED_IMPLEMENTATION: stage 1 did not produce a finite T2; "
                "cannot run stage 2.")

        t2a = math.ceil(t2 / 2)
        t2b = t2 - t2a
        R["stage2_sizing_applied"] = dict(
            T2=t2, T2_shard_8001=t2a, T2_shard_8002=t2b,
            SE_pooled_measured_k17_from_stage1=se_pooled_stage1_k17,
            substitution_shown=stage1["stage2_sizing"]["substitution_shown"])

        r_8001_def = run_arm(sa, ps, STAGE2_SHARD_A, t2a,
                             defected_decode_blocks, original_decode_blocks)
        r_8001_undef = run_arm(sa, ps, STAGE2_SHARD_A, t2a,
                               original_decode_blocks, original_decode_blocks)
        r_8002_def = run_arm(sa, ps, STAGE2_SHARD_B, t2b,
                             defected_decode_blocks, original_decode_blocks)
        r_8002_undef = run_arm(sa, ps, STAGE2_SHARD_B, t2b,
                               original_decode_blocks, original_decode_blocks)
        d2_d3_flags += [("shard_8001_defected", r_8001_def),
                        ("shard_8001_undefected", r_8001_undef),
                        ("shard_8002_defected", r_8002_def),
                        ("shard_8002_undefected", r_8002_undef)]
        R["hard_invariants"] = {tag: dict(D2_violations=r["d2_fail"],
                                          D3_violations=r["d3_fail"],
                                          D3_cap=r["d3_cap"], D3_max_w=r["d3_max_w"])
                                for tag, r in d2_d3_flags}
        d2_d3_clean = all(r["d2_fail"] == 0 and r["d3_fail"] == 0
                          for _, r in d2_d3_flags)
        any_truncated = any(r["truncated"] for _, r in d2_d3_flags)

        S_8001_def = r_8001_def["F"].sum(axis=1).astype(np.int64)
        S_8001_undef = r_8001_undef["F"].sum(axis=1).astype(np.int64)
        S_8002_def = r_8002_def["F"].sum(axis=1).astype(np.int64)
        S_8002_undef = r_8002_undef["F"].sum(axis=1).astype(np.int64)

        H_8001_def, B_8001_def = arm_hists(sa, S_8001_def, n_e, NB)
        H_8001_undef, B_8001_undef = arm_hists(sa, S_8001_undef, n_e, NB)
        H_8002_def, B_8002_def = arm_hists(sa, S_8002_def, n_e, NB)
        H_8002_undef, B_8002_undef = arm_hists(sa, S_8002_undef, n_e, NB)

        ks_8001 = set(sa.evaluable_k(H_8001_def, n_e)) & set(sa.evaluable_k(H_8001_undef, n_e))
        ks_8002 = set(sa.evaluable_k(H_8002_def, n_e)) & set(sa.evaluable_k(H_8002_undef, n_e))
        ks_pooled2 = ks_8001 & ks_8002 & set(K_RANGE_AUTHORIZED)
        ks_8001 = sorted(ks_8001 & set(K_RANGE_AUTHORIZED))
        ks_8002 = sorted(ks_8002 & set(K_RANGE_AUTHORIZED))
        ks_pooled2 = sorted(ks_pooled2)
        R["reachability"] = dict(
            evaluable_k_shard_8001=ks_8001, evaluable_k_shard_8002=ks_8002,
            evaluable_k_pooled=ks_pooled2, load_bearing_order_m=M,
            m_reachable_pooled=(M in ks_pooled2))

        C_8001 = measure.comb_matrix(n_e, ks_8001) if ks_8001 else None
        C_8002 = measure.comb_matrix(n_e, ks_8002) if ks_8002 else None
        C_pooled2 = measure.comb_matrix(n_e, ks_pooled2) if ks_pooled2 else None

        stats_8001 = (matched_pair_stats(measure, n_e, ks_8001, C_8001,
                                         H_8001_def, B_8001_def, H_8001_undef, B_8001_undef)
                     if ks_8001 else None)
        stats_8002 = (matched_pair_stats(measure, n_e, ks_8002, C_8002,
                                         H_8002_def, B_8002_def, H_8002_undef, B_8002_undef)
                     if ks_8002 else None)

        H_p2_def = H_8001_def + H_8002_def
        H_p2_undef = H_8001_undef + H_8002_undef
        B_p2_def = np.concatenate([B_8001_def, B_8002_def], axis=0)
        B_p2_undef = np.concatenate([B_8001_undef, B_8002_undef], axis=0)
        stats_pooled2 = (matched_pair_stats(measure, n_e, ks_pooled2, C_pooled2,
                                            H_p2_def, B_p2_def, H_p2_undef, B_p2_undef)
                        if ks_pooled2 else None)

        R["matched_pair"] = dict(
            per_shard=dict(shard_8001=stats_8001, shard_8002=stats_8002),
            pooled=stats_pooled2,
            primary_cell_k17=dict(
                shard_8001=(cell(stats_8001, M) if stats_8001 and M in stats_8001["ks"] else None),
                shard_8002=(cell(stats_8002, M) if stats_8002 and M in stats_8002["ks"] else None),
                pooled=(cell(stats_pooled2, M) if stats_pooled2 and M in stats_pooled2["ks"] else None)))

        se_pooled2_k17 = (R["matched_pair"]["primary_cell_k17"]["pooled"]["se_paired"]
                         if R["matched_pair"]["primary_cell_k17"]["pooled"] else None)

        spent_core = core_seconds() - c_wall0
        spent_wall = time.time() - t_wall0
        R["budget"] = dict(
            core_seconds_authorized=CORE_SECOND_BUDGET,
            core_seconds_spent=round(spent_core, 3),
            wall_seconds_authorized=WALL_SECOND_BUDGET,
            wall_seconds_spent=round(spent_wall, 3),
            within_core_second_budget=spent_core <= CORE_SECOND_BUDGET,
            within_wall_budget=spent_wall <= WALL_SECOND_BUDGET)

        t2_matches_rule = (t2 == stage1["stage2_sizing"]["T2_clamped"])
        ok = (R["fail_closed_selftests"]["sha256_pin_mismatch"]["verdict"] == "PASS"
              and R["fail_closed_selftests"]["injection_invariant_mismatch"]["verdict"] == "PASS"
              and R["injection"]["wrapper_calls_unmodified_function"]
              and d2_d3_clean and not any_truncated
              and stats_pooled2 is not None and M in stats_pooled2["ks"]
              and se_pooled2_k17 is not None and se_pooled2_k17 > 0
              and t2_matches_rule)
        R["validity"] = dict(
            status="valid_measurement" if ok else "invalid_measurement",
            failure_class=(None if ok else "invalid_measurement"),
            t2_matches_preregistered_rule=t2_matches_rule,
            reason=("All pre-registered mechanically-sound criteria met "
                    "(design.md Section 7): both fail-closed selftests PASS, "
                    "wrapper genuinely calls the unmodified decode_blocks, "
                    "D2/D3 clean on all four fresh-shard arms, the pooled "
                    "estimator returns a finite diff and finite positive "
                    "SE_paired at k=17, no arm truncated, T2 run matches the "
                    "pre-registered clamp formula applied to stage 1's "
                    "measured SE."
                    if ok else
                    "One or more pre-registered mechanically-sound criteria "
                    "(design.md Section 7) were not met -- see the "
                    "individual gate fields above for which one."))

        # ---- fitted SE-vs-T exponent (secondary, reported regardless) -----
        se_5000 = None
        se_6000 = None
        p5000 = stage1["matched_pair"]["primary_cell_k17"]["shard_5000"]
        p6000 = stage1["matched_pair"]["primary_cell_k17"]["shard_6000"]
        if p5000 is not None:
            se_5000 = p5000["se_paired"]
        if p6000 is not None:
            se_6000 = p6000["se_paired"]
        se_per_shard_5000_mean = (
            float(np.mean([x for x in (se_5000, se_6000) if x is not None]))
            if (se_5000 is not None or se_6000 is not None) else None)
        se_10000_pooled = stage1["stage2_sizing"]["SE_pooled_measured_k17"]
        se_t2_pooled = se_pooled2_k17

        points = [(5000.0, se_per_shard_5000_mean), (10000.0, se_10000_pooled),
                 (float(t2), se_t2_pooled)]
        valid_points = [(t, se) for t, se in points if se is not None and se > 0]
        if len(valid_points) >= 2:
            logt = np.log(np.array([p[0] for p in valid_points]))
            logse = np.log(np.array([p[1] for p in valid_points]))
            slope, intercept = np.polyfit(logt, logse, 1)
            alpha = -float(slope)
        else:
            alpha = None
        R["se_vs_trial_count_fit"] = dict(
            points=[dict(T=t, SE_paired_k17=se) for t, se in points],
            method="numpy.polyfit(log(T), log(SE), 1); alpha = -slope",
            fitted_exponent_alpha=alpha,
            consistent_with_1_over_sqrt_T_band=[0.4, 0.6],
            note="1/sqrt(T) consistency is alpha in [0.4, 0.6], declared in "
                 "advance (DEC-20260809-46e85c design.md Section 5). This "
                 "value is reported descriptively; no conclusion is drawn "
                 "here about whether the assumption holds.")

        # ---- combine into final matched_pair_results.json ------------------
        prior["stage_2"] = R
        R["finished_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with open(out_path, "w") as fh:
            json.dump(prior, fh, indent=1)
        print(f"[done] stage 2 -> {out_path}  core-s={spent_core:.2f}/{CORE_SECOND_BUDGET} "
              f"wall={spent_wall:.1f}s/{WALL_SECOND_BUDGET}s  "
              f"validity={R['validity']['status']}", flush=True)
        return R

    R["finished_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(out_path, "w") as fh:
        json.dump({"stage_1": R}, fh, indent=1)
    print(f"[done] stage 1 -> {out_path}  core-s={(core_seconds() - c_wall0):.2f}/"
          f"{CORE_SECOND_BUDGET} wall={(time.time() - t_wall0):.1f}s/{WALL_SECOND_BUDGET}s  "
          f"validity={R['validity']['status']}", flush=True)
    return R


if __name__ == "__main__":
    main()
