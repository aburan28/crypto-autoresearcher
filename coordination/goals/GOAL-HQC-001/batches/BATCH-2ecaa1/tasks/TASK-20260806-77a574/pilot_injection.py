#!/usr/bin/env python3
"""Pilot real-sampler defect injection for EXP-HQC-982268 / OPEN-6.

TASK-20260806-77a574 (executor) / BATCH-2ecaa1 / GOAL-HQC-001.
Authorized by DEC-20260806-1ac8fa's next_action. Pre-registered design in
design.md (WRITTEN AND FROZEN BEFORE THIS SCRIPT WAS RUN ON REAL DATA).

WHAT THIS IS
------------
The first genuinely real-sampler defect-injection PILOT in this campaign.
Defect class: V3 (last-block-window-read-early). Injection point:
decode_blocks's block window, LAST BLOCK ONLY (index n_e - 1), shifted left
by exactly one bit position. See design.md Sections 2-3 for the full
rationale and mechanism, fixed in advance of this run.

stage_a.py and measure.py are imported READ-ONLY, sha256-pinned, exactly as
V1/V2/V3 and the cost-model task did (identical load_module() pattern to
planted_arm_v3.py). Neither file is modified on disk. The ONLY new code is
(a) a thin bit-array preprocessing wrapper that injects the defect and then
calls the real, unmodified decode_blocks, and (b) this pilot's own
driver/reporting logic.

Claim tier: TOY, hard ceiling. PS-R3 only (n_e=56 order). One defect class,
one injection point, one small trial count (5,000 defect-injected + 5,000
paired undefected control). NOT the full T_req=3.09e5 run. Nothing here is a
statement about HQC, A17, its decoding-failure rate, or any standardized
parameter set.

A timeout, crash, missing dependency or budget exhaustion is an
INFRASTRUCTURE outcome and is never evidence about the mathematics
(AGENTS.md rule 5).

Re-run:
    PYTHONDONTWRITEBYTECODE=1 python3 pilot_injection.py --out-dir .
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

# sha256 pins -- identical values to V1/V2/V3 and the cost-model task
# (independently re-verified by this task at run time via load_module()).
STAGE_A_PY_EXPECTED_SHA256 = (
    "06a0a618432c00fe26c72ecf05a8d89489db61c5183931fdb76a378717681405")
MEASURE_PY_EXPECTED_SHA256 = (
    "a4fd1ecb63f0ddc83c02ef45f2c65ab31cf13d13e7ae94f500e67465b24f5dc8")

SET_ID = "PS-R3"
N_TRIALS_DEFECTED = 5_000
N_TRIALS_UNDEFECTED = 5_000
N_TRIALS_WARMUP = 300
SHARD_WARMUP_DEFECTED = 4900
SHARD_WARMUP_UNDEFECTED = 4901
SHARD_DEFECTED = 5000            # disjoint from every prior committed T-arm
SHARD_UNDEFECTED = 6000          # shard usage at PS-R3 found in read scope
BATCH = 64
WALL_CAP_PER_CALL = 600.0
CORE_SECOND_BUDGET = 400.0
WALL_SECOND_BUDGET = 2700.0

COST_MODEL_OPTIMISTIC_LOW = 2168.0
COST_MODEL_OPTIMISTIC_HIGH = 2227.0
COST_MODEL_PESSIMISTIC = 788.0


# --------------------------------------------------------------------------
# provenance / fail-closed loading (identical pattern to planted_arm_v3.py)
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
    """Demonstrates load_module() genuinely aborts on a deliberate sha256
    mismatch. Chosen over the V1-V3 convention of editing-then-reverting the
    pinned constant in the committed script: this calls the SAME load_module()
    function used for the real load, with a deliberately wrong expected hash
    passed as an argument, so the committed pinned constants above are never
    touched (not even transiently) -- equally demonstrative, strictly safer."""
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
    """Demonstrates the injection-invariant fail-closed check (Section 3 of
    design.md) genuinely aborts when the actually-applied shift does not
    match the shift the invariant asserts. Builds a wrapper whose
    CONSTRUCTION shift is 2 bit-positions but whose INVARIANT CHECK always
    asserts shift-by-1 semantics (the real, intended defect) -- a
    deliberate mismatch between what was built and what was checked, run on
    a small synthetic bit array (no real pipeline draws consumed)."""
    rng = np.random.default_rng(12345)
    bits = rng.integers(0, 2, size=(4, n_e * n_2), dtype=np.uint8)

    def broken_wrapper(bits_in, n_e_arg, n_2_arg, dup_arg,
                       original=None, shift=2):
        b = bits_in.copy()
        lo, hi = (n_e_arg - 1) * n_2_arg, n_e_arg * n_2_arg
        b[:, lo:hi] = bits_in[:, lo - shift:hi - shift]
        # invariant check ALWAYS asserts the intended shift-by-1 semantics,
        # regardless of what `shift` the construction above actually used.
        ok = (np.array_equal(b[:, lo + 1:hi], bits_in[:, lo:hi - 1])
              and np.array_equal(b[:, lo], bits_in[:, lo - 1]))
        if not ok:
            raise SystemExit(
                "FAIL-CLOSED: injection invariant violated -- the perturbed "
                "last-block window does not match the pre-registered "
                "shift-by-1 construction (design.md Section 3).")
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
# --------------------------------------------------------------------------

def make_defected_decode_blocks(original_decode_blocks, n_2_expected: int):
    """Returns a wrapper reusing `original_decode_blocks` (the real,
    unmodified stage_a.decode_blocks, sha256-pinned) UNCHANGED internally.
    The ONLY new logic is the bit-array preprocessing step: the LAST block's
    window is shifted left by exactly one bit position before the real
    decoder ever sees it. Checked, every call, by a fail-closed invariant
    (design.md Section 3)."""
    orig_id = id(original_decode_blocks)

    def defected(bits, n_e, n_2, dup):
        assert n_2 == n_2_expected, "unexpected n_2 at call time"
        b = bits.copy()
        lo, hi = (n_e - 1) * n_2, n_e * n_2
        b[:, lo:hi] = bits[:, lo - 1:hi - 1]
        # FAIL-CLOSED INJECTION INVARIANT, checked on every call (i.e. every
        # trial in the batch), before a single trial is decoded.
        ok = (np.array_equal(b[:, lo + 1:hi], bits[:, lo:hi - 1])
              and np.array_equal(b[:, lo], bits[:, lo - 1])
              and np.array_equal(b[:, :lo], bits[:, :lo]))
        if not ok:
            raise SystemExit(
                "FAIL-CLOSED: injection invariant violated in the real "
                "pipeline call -- the perturbed last-block window does not "
                "match the pre-registered shift-by-1 construction "
                "(design.md Section 3). Aborting before any trial in this "
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
# estimator: reused via direct call to sha256-pinned measure.py / stage_a.py
# --------------------------------------------------------------------------

def arm_estimate(sa, measure, F: np.ndarray, n_e: int, ks):
    """log2 Ahat_k point estimate + leave-one-batch-out jackknife SE, for
    every k in `ks`, computed EXACTLY the way measure.py's own main()
    computes it: sa.hist_of / sa.batch_hists (reused directly) feed
    measure.comb_matrix / measure.log2_A_from_hists (reused directly)."""
    S = F.sum(axis=1).astype(np.int64)
    T = S.shape[0]
    hist = sa.hist_of(S, n_e)
    C = measure.comb_matrix(n_e, ks)
    point = measure.log2_A_from_hists(hist[None, :], n_e, ks, C)[0]
    nb = min(sa.N_JACK_BATCHES, T)
    bh = sa.batch_hists(S, n_e, nb)
    loo = np.array([measure.log2_A_from_hists((hist - bh[i])[None, :], n_e, ks, C)[0]
                    for i in range(bh.shape[0])])
    jmean = loo.mean(axis=0)
    b = bh.shape[0]
    jse = np.sqrt((b - 1) / b * ((loo - jmean) ** 2).sum(axis=0))
    return dict(T=T, q_hat=float(S.mean() / n_e), S_histogram=[int(x) for x in hist],
                jackknife_batches=b,
                per_k=[dict(k=int(k), log2_A_k=(None if not np.isfinite(point[j])
                                                 else float(point[j])),
                            jackknife_se=(None if not np.isfinite(jse[j])
                                          else float(jse[j])),
                            z_vs_zero=(None if not (np.isfinite(point[j])
                                                     and np.isfinite(jse[j])
                                                     and jse[j] > 0)
                                       else float(point[j] / jse[j])))
                       for j, k in enumerate(ks)])


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=HERE)
    args = ap.parse_args(argv)

    t_wall0, c_wall0 = time.time(), core_seconds()
    R = {
        "task_id": "TASK-20260806-77a574",
        "role": "executor",
        "experiment_id": "EXP-HQC-982268",
        "hypothesis_id": "H-HQC-18d1b4",
        "goal": "GOAL-HQC-001",
        "batch": "BATCH-2ecaa1",
        "claim_tier": "toy",
        "scope_statement": (
            "PILOT ONLY. ONE parameter set (PS-R3), ONE defect class (V3, "
            "last-block-window-read-early), ONE injection point "
            "(decode_blocks's block window, last block only), "
            f"{N_TRIALS_DEFECTED} defect-injected trials + "
            f"{N_TRIALS_UNDEFECTED} paired undefected control trials. NOT "
            "the full T_req=3.09e5 run. NOTHING here is a statement about "
            "HQC, A17, A5, any decoding-failure rate, or any standardized "
            "parameter set."),
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
        # injection-invariant selftest needs n_e/n_2, run again after load
    }
    print("[selftest] sha256 pin mismatch: "
          f"{R['fail_closed_selftests']['sha256_pin_mismatch']['verdict']}", flush=True)
    if R["fail_closed_selftests"]["sha256_pin_mismatch"]["verdict"] != "PASS":
        raise SystemExit("FAILED_IMPLEMENTATION: sha256 pin fail-closed "
                         "selftest did not pass; refusing to proceed")

    # ---- phase 1: real, sha256-pinned, read-only module load -------------
    sa, sa_sha = load_module(STAGE_A_PY, STAGE_A_PY_EXPECTED_SHA256,
                             "stage_a.py", "stage_a_frozen_pilot")
    measure, measure_sha = load_module(MEASURE_PY, MEASURE_PY_EXPECTED_SHA256,
                                       "measure.py", "measure_frozen_pilot")
    R["provenance"] = dict(
        stage_a_path=os.path.relpath(STAGE_A_PY, REPO), stage_a_sha256=sa_sha,
        stage_a_sha256_expected=STAGE_A_PY_EXPECTED_SHA256,
        stage_a_sha256_match=(sa_sha == STAGE_A_PY_EXPECTED_SHA256),
        measure_path=os.path.relpath(MEASURE_PY, REPO), measure_sha256=measure_sha,
        measure_sha256_expected=MEASURE_PY_EXPECTED_SHA256,
        measure_sha256_match=(measure_sha == MEASURE_PY_EXPECTED_SHA256),
        stage_a_modified=False, measure_modified=False,
        note="Both imported unmodified via importlib.util, read-only. "
             "Neither file was opened for writing by this task.")

    ps = [p for p in sa.PARAM_SETS if p["id"] == SET_ID][0]
    n_e, n_2, dup, N = ps["n_e"], ps["n_2"], ps["dup"], ps["N"]
    m = 17
    R["parameter_set"] = {k: ps[k] for k in
                          ("id", "role", "n", "n_e", "n_2", "dup", "omega",
                           "omega_r", "omega_e", "N")}
    R["parameter_set"]["m_load_bearing_order"] = m

    # injection-invariant selftest, now that n_e/n_2 are known
    R["fail_closed_selftests"]["injection_invariant_mismatch"] = (
        selftest_injection_invariant_fail(n_e, n_2))
    print("[selftest] injection invariant deliberate break: "
          f"{R['fail_closed_selftests']['injection_invariant_mismatch']['verdict']}",
          flush=True)
    if R["fail_closed_selftests"]["injection_invariant_mismatch"]["verdict"] != "PASS":
        raise SystemExit("FAILED_IMPLEMENTATION: injection-invariant "
                         "fail-closed selftest did not pass; refusing to proceed")

    # ---- phase 2: build the defect wrapper, confirm identity -------------
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
        mechanism="design.md Section 3, fixed before this run",
        stage_a_py_edited_on_disk=False,
        new_code_scope=("bit-array preprocessing wrapper (defected()) plus "
                        "this pilot's own driver/reporting logic only; "
                        "decode_blocks's fold/WHT/argmax/tie logic is the "
                        "real, unmodified function"))

    # ---- phase 3: warm-up (both variants), THEN timed real calls ---------
    with_warmup = {}
    sa.decode_blocks = defected_decode_blocks
    _ = sa._t_shard((ps, SHARD_WARMUP_DEFECTED, N_TRIALS_WARMUP, WALL_CAP_PER_CALL,
                     BATCH, 0))
    sa.decode_blocks = original_decode_blocks
    _ = sa._t_shard((ps, SHARD_WARMUP_UNDEFECTED, N_TRIALS_WARMUP, WALL_CAP_PER_CALL,
                     BATCH, 0))
    del _
    R["warmup"] = dict(
        trials_each=N_TRIALS_WARMUP,
        note="Both the defected and undefected code paths are warmed with a "
             "throwaway call BEFORE either arm's timed measurement, per the "
             "warm-up/cold-start discipline the Validator established in "
             "TASK-20260806-069687 (EV-HQC-bfb257) -- applied here because "
             "this pilot's own throughput figure is compared against that "
             "same cost model.")

    # ---- phase 4: THE MEASUREMENT -----------------------------------------
    sa.decode_blocks = defected_decode_blocks
    r_def = sa._t_shard((ps, SHARD_DEFECTED, N_TRIALS_DEFECTED, WALL_CAP_PER_CALL,
                        BATCH, 0))
    sa.decode_blocks = original_decode_blocks     # restore immediately
    r_undef = sa._t_shard((ps, SHARD_UNDEFECTED, N_TRIALS_UNDEFECTED, WALL_CAP_PER_CALL,
                          BATCH, 0))
    assert sa.decode_blocks is original_decode_blocks, "module left patched"

    for tag, r in (("defected", r_def), ("undefected", r_undef)):
        print(f"[{tag}] trials_done={r['trials_done']} "
              f"cpu_seconds={r['cpu_seconds']:.4f} "
              f"throughput={r['trials_done']/max(1e-9, r['cpu_seconds']):.1f} t/cs "
              f"D2_fail={r['d2_fail']} D3_fail={r['d3_fail']} "
              f"truncated={r['truncated']}", flush=True)

    R["hard_invariants"] = dict(
        defected=dict(D2_violations=r_def["d2_fail"], D3_violations=r_def["d3_fail"],
                     D3_cap=r_def["d3_cap"], D3_max_w_observed=r_def["d3_max_w"],
                     note="D2/D3 run upstream of decode_blocks and should be "
                          "entirely unaffected by a decode-only defect"),
        undefected=dict(D2_violations=r_undef["d2_fail"], D3_violations=r_undef["d3_fail"],
                        D3_cap=r_undef["d3_cap"], D3_max_w_observed=r_undef["d3_max_w"]))

    R["throughput"] = dict(
        defected=dict(trials_done=r_def["trials_done"],
                     cpu_seconds=r_def["cpu_seconds"],
                     wall_seconds=r_def["wall_seconds"],
                     trials_per_core_second=r_def["trials_done"] / max(1e-9, r_def["cpu_seconds"]),
                     truncated=r_def["truncated"]),
        undefected=dict(trials_done=r_undef["trials_done"],
                        cpu_seconds=r_undef["cpu_seconds"],
                        wall_seconds=r_undef["wall_seconds"],
                        trials_per_core_second=r_undef["trials_done"] / max(1e-9, r_undef["cpu_seconds"]),
                        truncated=r_undef["truncated"]),
        cost_model_comparison=dict(
            optimistic_band_t_per_cs=[COST_MODEL_OPTIMISTIC_LOW, COST_MODEL_OPTIMISTIC_HIGH],
            pessimistic_t_per_cs=COST_MODEL_PESSIMISTIC,
            defected_vs_optimistic_low_ratio=(
                (r_def["trials_done"] / max(1e-9, r_def["cpu_seconds"])) / COST_MODEL_OPTIMISTIC_LOW),
            defected_vs_pessimistic_ratio=(
                (r_def["trials_done"] / max(1e-9, r_def["cpu_seconds"])) / COST_MODEL_PESSIMISTIC),
            undefected_vs_optimistic_low_ratio=(
                (r_undef["trials_done"] / max(1e-9, r_undef["cpu_seconds"])) / COST_MODEL_OPTIMISTIC_LOW),
            undefected_vs_pessimistic_ratio=(
                (r_undef["trials_done"] / max(1e-9, r_undef["cpu_seconds"])) / COST_MODEL_PESSIMISTIC)))

    # ---- phase 5: estimator, reused via measure.py / stage_a.py ----------
    ks_def = sa.evaluable_k(sa.hist_of(r_def["F"].sum(axis=1).astype(np.int64), n_e), n_e,
                            floor=sa.T_STAB_THRESHOLD)
    ks_undef = sa.evaluable_k(sa.hist_of(r_undef["F"].sum(axis=1).astype(np.int64), n_e), n_e,
                              floor=sa.T_STAB_THRESHOLD)
    k_max_common = min(max(ks_def, default=1), max(ks_undef, default=1))
    ks = list(range(2, k_max_common + 1)) if k_max_common >= 2 else []
    R["reachability"] = dict(
        evaluable_k_defected=ks_def, evaluable_k_undefected=ks_undef,
        ks_reported=ks, load_bearing_order_m=m,
        m_reachable=(m in ks),
        note="sa.evaluable_k (T_STAB_THRESHOLD=30, reused directly, "
             "unmodified) applied to each arm's own histogram; ks_reported "
             "is the intersection range so both arms report the same cells.")

    est_def = arm_estimate(sa, measure, r_def["F"], n_e, ks) if ks else None
    est_undef = arm_estimate(sa, measure, r_undef["F"], n_e, ks) if ks else None
    R["MEASUREMENT"] = dict(defected=est_def, undefected=est_undef)

    if ks and est_def is not None and est_undef is not None:
        diff_rows = []
        for j, k in enumerate(ks):
            pd, pu = est_def["per_k"][j], est_undef["per_k"][j]
            if pd["log2_A_k"] is None or pu["log2_A_k"] is None:
                diff_rows.append(dict(k=k, diff=None, se=None, z=None))
                continue
            diff = pd["log2_A_k"] - pu["log2_A_k"]
            se_d = pd["jackknife_se"] or float("nan")
            se_u = pu["jackknife_se"] or float("nan")
            se = math.sqrt(se_d ** 2 + se_u ** 2) if (se_d and se_u) else None
            z = (diff / se) if (se and se > 0) else None
            diff_rows.append(dict(k=k, is_prespecified_cell=(k == m),
                                  log2_A_k_defected=pd["log2_A_k"],
                                  log2_A_k_undefected=pu["log2_A_k"],
                                  diff_defected_minus_undefected=diff,
                                  combined_jackknife_se=se, z_vs_zero_diff=z))
        R["MEASUREMENT"]["defected_minus_undefected"] = diff_rows
    else:
        R["MEASUREMENT"]["defected_minus_undefected"] = []

    # ---- close out ----------------------------------------------------
    spent_core = core_seconds() - c_wall0
    spent_wall = time.time() - t_wall0
    R["budget"] = dict(
        core_seconds_authorized=CORE_SECOND_BUDGET,
        core_seconds_spent=round(spent_core, 3),
        wall_seconds_authorized=WALL_SECOND_BUDGET,
        wall_seconds_spent=round(spent_wall, 3),
        within_core_second_budget=spent_core <= CORE_SECOND_BUDGET,
        within_wall_budget=spent_wall <= WALL_SECOND_BUDGET,
        runs_authorized=1, runs_used=1)

    ok = (R["fail_closed_selftests"]["sha256_pin_mismatch"]["verdict"] == "PASS"
          and R["fail_closed_selftests"]["injection_invariant_mismatch"]["verdict"] == "PASS"
          and R["injection"]["wrapper_calls_unmodified_function"]
          and r_def["d2_fail"] == 0 and r_def["d3_fail"] == 0
          and r_undef["d2_fail"] == 0 and r_undef["d3_fail"] == 0
          and est_def is not None and est_undef is not None
          and (m in ks)
          and est_def["per_k"][ks.index(m)]["log2_A_k"] is not None
          and est_undef["per_k"][ks.index(m)]["log2_A_k"] is not None
          and not r_def["truncated"] and not r_undef["truncated"])
    R["validity"] = dict(
        status="valid_measurement" if ok else "invalid_measurement",
        reason=("All pre-registered mechanically-sound criteria met (see "
                "design.md Section 5): both fail-closed selftests passed, "
                "the wrapper genuinely calls the unmodified decode_blocks, "
                "D2/D3 are clean on both arms, the estimator returns finite "
                "values at k=m on both arms, and neither arm was truncated."
                if ok else
                "One or more pre-registered mechanically-sound criteria "
                "(design.md Section 5) were not met -- see the individual "
                "gate fields above for which one."),
        pre_registered_criteria_source="design.md Section 5, written before this run")
    R["finished_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # F arrays are large; drop before serializing full histories already summarized
    out = os.path.join(args.out_dir, "pilot_results.json")
    with open(out, "w") as fh:
        json.dump(R, fh, indent=1)
    print(f"[done] {out}  core-s={spent_core:.2f}/{CORE_SECOND_BUDGET} "
          f"wall={spent_wall:.1f}s/{WALL_SECOND_BUDGET}s  "
          f"validity={R['validity']['status']}", flush=True)
    return R


if __name__ == "__main__":
    main()
