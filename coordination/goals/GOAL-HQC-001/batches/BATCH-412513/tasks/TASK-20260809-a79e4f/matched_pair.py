#!/usr/bin/env python3
"""Matched-pair measurement at the V3/decode_blocks injection point.

TASK-20260809-a79e4f (executor) / BATCH-412513 / GOAL-HQC-001 / EXP-HQC-982268.
Authorized by DEC-20260809-46e85c. Pre-registered design in design.md
(WRITTEN AND FROZEN BEFORE THIS SCRIPT WAS RUN ON REAL DATA).

WHAT THIS IS
------------
STAGE 1 (--stage 1): deterministic, zero-new-entropy reconstruction of the
pilot's own committed shards 5000/6000 (TASK-20260806-77a574), decoded
through BOTH decode variants from a SINGLE generation pass per shard, giving
genuine matched pairs. Fail-closed on a bit-identity determinism gate against
pilot_results.json before any stage-1 statistic is computed.

STAGE 2 (--stage 2): a matched-pair extension at a trial count fixed by a
pre-registered rule (design.md Section 3.1) applied to stage 1's own
measured pooled SE, on fresh shard indices declared in design.md BEFORE
stage 1 ran.

stage_a.py and measure.py are imported READ-ONLY, sha256-pinned, identically
to pilot_injection.py's load_module() pattern. Neither file is modified on
disk. The ONLY new code is the injection wrapper (copied in behaviour from
pilot_injection.py's make_defected_decode_blocks), the dual_decode_shard
driver (a byte-identical copy of stage_a.py's own _t_shard generation loop,
decoding twice per batch instead of once -- see design.md Section 1), and
the matched-pair jackknife on the per-batch difference.

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
PILOT_RESULTS = os.path.join(
    REPO, "coordination", "goals", "GOAL-HQC-001", "batches", "BATCH-2ecaa1",
    "tasks", "TASK-20260806-77a574", "pilot_results.json")

STAGE_A_PY_EXPECTED_SHA256 = (
    "06a0a618432c00fe26c72ecf05a8d89489db61c5183931fdb76a378717681405")
MEASURE_PY_EXPECTED_SHA256 = (
    "a4fd1ecb63f0ddc83c02ef45f2c65ab31cf13d13e7ae94f500e67465b24f5dc8")

SET_ID = "PS-R3"
M_LOAD_BEARING = 17
BATCH = 64
WALL_CAP_PER_CALL = 600.0
CORE_SECOND_BUDGET = 400.0
WALL_SECOND_BUDGET = 1800.0

STAGE1_SHARDS = [5000, 6000]        # already committed by the pilot
STAGE1_TRIALS_PER_SHARD = 5000

# design.md Section 3.2 -- FIXED BEFORE STAGE 1 RUNS.
STAGE2_SHARD_POOL = list(range(8000, 8012))       # 12 shards * 5000 = 60000
STAGE2_TRIALS_PER_SHARD = 5000
T2_FLOOR = 20000
T2_CAP = 60000
DELTA = 0.20
Z_STAR = 2.80

N_JACK_BATCHES = 200


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
                    "stage_a_selftest_badhash_mp")
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

    def broken_wrapper(bits_in, n_e_arg, n_2_arg, shift=2):
        b = bits_in.copy()
        lo, hi = (n_e_arg - 1) * n_2_arg, n_e_arg * n_2_arg
        b[:, lo:hi] = bits_in[:, lo - shift:hi - shift]
        ok = (np.array_equal(b[:, lo + 1:hi], bits_in[:, lo:hi - 1])
              and np.array_equal(b[:, lo], bits_in[:, lo - 1]))
        if not ok:
            raise SystemExit(
                "FAIL-CLOSED: injection invariant violated -- the perturbed "
                "last-block window does not match the pre-registered "
                "shift-by-1 construction (design.md Section 1).")
        return "UNREACHABLE -- would have called the real decode_blocks"

    try:
        broken_wrapper(bits, n_e, n_2, shift=2)
        return dict(aborted=False, message=None,
                    verdict="FAIL -- did not abort on a real invariant break")
    except SystemExit as exc:
        msg = str(exc)
        ok = "FAIL-CLOSED" in msg and "injection invariant" in msg
        return dict(aborted=True, message=msg,
                    verdict="PASS" if ok else "FAIL -- aborted but for the "
                                              "wrong stated reason")


# --------------------------------------------------------------------------
# the defect: V3 (last-block-window-read-early), decode_blocks injection
# point -- copied in behaviour from pilot_injection.py's
# make_defected_decode_blocks (design.md Section 1)
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
                "(design.md Section 1). Aborting before any trial in this "
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
# the driver: dual_decode_shard -- generate ONCE per batch, decode TWICE
# (design.md Section 1). The generation body below is a byte-identical copy
# of stage_a.py's own _t_shard() generation loop (lines 475-542 of the
# sha256-pinned file); only the decode step is duplicated. _t_shard itself
# calls decode_blocks exactly once per batch and therefore cannot be reused
# unmodified to produce a matched pair from one generation pass -- reusing
# it twice per shard would each time REGENERATE the (deterministically
# identical) draws rather than decode a single generated array twice, which
# is not what design.md Section 1 commits to. sha_key, CTRStream,
# fixed_weight_support, support_to_int, ring_mul_sparse are called via the
# sha256-pinned stage_a module exactly as _t_shard calls them, never
# reimplemented.
# --------------------------------------------------------------------------

def dual_decode_shard(sa, ps, shard, n_trials, wall_cap, batch,
                       decode_a, decode_b):
    """Returns per-trial S arrays (trial order) for decode_a and decode_b,
    both derived from the SAME generated bit array per batch, plus the
    shared D2/D3 generation-invariant counts (decoder-independent)."""
    t_cpu0, t_w0 = time.process_time(), time.time()

    n, N, n_e, n_2, dup = ps["n"], ps["N"], ps["n_e"], ps["n_2"], ps["dup"]
    om, omr, ome = ps["omega"], ps["omega_r"], ps["omega_e"]
    key = sa.sha_key(ps["id"], "T", shard, sa.MASTER_SEED)
    mask_n, mask_N = (1 << n) - 1, (1 << N) - 1
    nbytes_n, nbytes_N = (n + 7) // 8, N // 8
    cap_D3 = 2 * om * omr + ome

    S_a = np.zeros(n_trials, dtype=np.int64)
    S_b = np.zeros(n_trials, dtype=np.int64)
    d2_fail = d3_fail = d3_max_w = 0
    done, truncated = 0, False
    buf = np.zeros((batch, nbytes_N), dtype=np.uint8)

    t = 0
    while t < n_trials:
        b_n = min(batch, n_trials - t)
        for i in range(b_n):
            ti = t + i
            sx = sa.fixed_weight_support(
                sa.CTRStream(key, b"v0" + ti.to_bytes(8, "little")), n, om)
            sy = sa.fixed_weight_support(
                sa.CTRStream(key, b"v1" + ti.to_bytes(8, "little")), n, om)
            s1 = sa.fixed_weight_support(
                sa.CTRStream(key, b"v2" + ti.to_bytes(8, "little")), n, omr)
            s2 = sa.fixed_weight_support(
                sa.CTRStream(key, b"v3" + ti.to_bytes(8, "little")), n, omr)
            se = sa.fixed_weight_support(
                sa.CTRStream(key, b"v4" + ti.to_bytes(8, "little")), n, ome)

            xi = sa.support_to_int(sx, nbytes_n)
            yi = sa.support_to_int(sy, nbytes_n)
            r1 = sa.support_to_int(s1, nbytes_n)
            r2 = sa.support_to_int(s2, nbytes_n)
            ei = sa.support_to_int(se, nbytes_n)

            # D2 -- exact weights on EVERY trial (decoder-independent)
            if (xi.bit_count() != om or yi.bit_count() != om
                    or r1.bit_count() != omr or r2.bit_count() != omr
                    or ei.bit_count() != ome
                    or len(set(sx)) != om or len(set(sy)) != om
                    or len(set(s1)) != omr or len(set(s2)) != omr
                    or len(set(se)) != ome):
                d2_fail += 1

            epp = (sa.ring_mul_sparse(xi, s2, n, mask_n)
                   ^ sa.ring_mul_sparse(r1, sy, n, mask_n) ^ ei)
            et = epp & mask_N

            # D3 -- hard support cap, checked on EVERY trial (decoder-independent)
            w_et = et.bit_count()
            d3_max_w = max(d3_max_w, w_et)
            if w_et > cap_D3 or epp.bit_count() > cap_D3:
                d3_fail += 1

            buf[i] = np.frombuffer(et.to_bytes(nbytes_N, "little"), dtype=np.uint8)

        bits = np.unpackbits(buf[:b_n], axis=1, bitorder="little")[:, :N]
        # THE ONE GENERATION PASS ABOVE FEEDS TWO DECODE CALLS BELOW.
        F_a, _, _ = decode_a(bits, n_e, n_2, dup)
        F_b, _, _ = decode_b(bits, n_e, n_2, dup)
        S_a[t:t + b_n] = F_a.sum(axis=1).astype(np.int64)
        S_b[t:t + b_n] = F_b.sum(axis=1).astype(np.int64)
        t += b_n
        done = t
        if time.time() - t_w0 > wall_cap:
            truncated = True
            break

    return dict(
        shard=shard, trials_requested=n_trials, trials_done=done,
        truncated=truncated, S_a=S_a[:done].tolist(), S_b=S_b[:done].tolist(),
        d2_fail=d2_fail, d3_fail=d3_fail, d3_max_w=d3_max_w, d3_cap=cap_D3,
        cpu_seconds=time.process_time() - t_cpu0,
        wall_seconds=time.time() - t_w0, key_hex=key.hex())


# --------------------------------------------------------------------------
# matched-pair statistics (design.md Section 2.2 / 3.3)
# --------------------------------------------------------------------------

def matched_pair_stats(sa, measure, S_true, S_def, n_e, ks, C, nb):
    S_true = np.asarray(S_true, dtype=np.int64)
    S_def = np.asarray(S_def, dtype=np.int64)
    assert S_true.shape[0] == S_def.shape[0]
    T = S_true.shape[0]

    hist_true = sa.hist_of(S_true, n_e)
    hist_def = sa.hist_of(S_def, n_e)
    point_true = measure.log2_A_from_hists(hist_true[None, :], n_e, ks, C)[0]
    point_def = measure.log2_A_from_hists(hist_def[None, :], n_e, ks, C)[0]
    diff_point = point_def - point_true

    bh_true = sa.batch_hists(S_true, n_e, nb)
    bh_def = sa.batch_hists(S_def, n_e, nb)
    b = bh_true.shape[0]
    assert bh_def.shape[0] == b

    loo_true = np.array([
        measure.log2_A_from_hists((hist_true - bh_true[i])[None, :], n_e, ks, C)[0]
        for i in range(b)])
    loo_def = np.array([
        measure.log2_A_from_hists((hist_def - bh_def[i])[None, :], n_e, ks, C)[0]
        for i in range(b)])
    loo_diff = loo_def - loo_true

    def jse(vals):
        mean = np.nanmean(vals, axis=0)
        return np.sqrt((b - 1) / b * np.nansum((vals - mean) ** 2, axis=0))

    se_true = jse(loo_true)
    se_def = jse(loo_def)
    se_paired = jse(loo_diff)
    se_unpaired = np.sqrt(se_true ** 2 + se_def ** 2)
    ratio = se_unpaired / se_paired
    z_paired = diff_point / se_paired
    z_unpaired = diff_point / se_unpaired

    return dict(
        T=int(T), jackknife_batches=int(b),
        S_histogram_true=[int(x) for x in hist_true],
        S_histogram_defected=[int(x) for x in hist_def],
        per_k=[dict(
            k=int(k), is_prespecified_cell=bool(k == M_LOAD_BEARING),
            log2_A_k_true=(None if not np.isfinite(point_true[j]) else float(point_true[j])),
            log2_A_k_defected=(None if not np.isfinite(point_def[j]) else float(point_def[j])),
            diff_defected_minus_true=(None if not np.isfinite(diff_point[j]) else float(diff_point[j])),
            paired_jackknife_se=(None if not np.isfinite(se_paired[j]) else float(se_paired[j])),
            unpaired_se_quadrature=(None if not np.isfinite(se_unpaired[j]) else float(se_unpaired[j])),
            unpaired_over_paired_ratio=(None if not np.isfinite(ratio[j]) else float(ratio[j])),
            z_paired=(None if not np.isfinite(z_paired[j]) else float(z_paired[j])),
            z_unpaired=(None if not np.isfinite(z_unpaired[j]) else float(z_unpaired[j])),
            se_true_arm_jackknife=(None if not np.isfinite(se_true[j]) else float(se_true[j])),
            se_defected_arm_jackknife=(None if not np.isfinite(se_def[j]) else float(se_def[j])),
        ) for j, k in enumerate(ks)],
    )


def cell_at_k(stats, k):
    for c in stats["per_k"]:
        if c["k"] == k:
            return c
    return None


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def run_stage1(sa, measure, defected_decode, original_decode, ks, C, n_e, R):
    gate = {}
    pilot = json.load(open(PILOT_RESULTS))
    pilot_def_hist = pilot["MEASUREMENT"]["defected"]["S_histogram"]
    pilot_undef_hist = pilot["MEASUREMENT"]["undefected"]["S_histogram"]

    arms = {}
    per_shard_timing = []
    for shard in STAGE1_SHARDS:
        r = dual_decode_shard(sa, ps=R["_ps"], shard=shard,
                              n_trials=STAGE1_TRIALS_PER_SHARD,
                              wall_cap=WALL_CAP_PER_CALL, batch=BATCH,
                              decode_a=original_decode, decode_b=defected_decode)
        arms[shard] = r
        per_shard_timing.append(dict(shard=shard, trials_done=r["trials_done"],
                                     cpu_seconds=r["cpu_seconds"],
                                     wall_seconds=r["wall_seconds"],
                                     truncated=r["truncated"],
                                     d2_fail=r["d2_fail"], d3_fail=r["d3_fail"],
                                     d3_max_w=r["d3_max_w"], d3_cap=r["d3_cap"]))

    # decode_a = original/true, decode_b = defected, for BOTH shards.
    s5000_true = arms[5000]["S_a"]; s5000_def = arms[5000]["S_b"]
    s6000_true = arms[6000]["S_a"]; s6000_def = arms[6000]["S_b"]

    hist_5000_def = [int(x) for x in sa.hist_of(np.array(s5000_def), n_e)]
    hist_6000_true = [int(x) for x in sa.hist_of(np.array(s6000_true), n_e)]

    gate["shard_5000_defected_matches_pilot"] = (hist_5000_def == pilot_def_hist)
    gate["shard_6000_undefected_matches_pilot"] = (hist_6000_true == pilot_undef_hist)
    gate["shard_5000_defected_S_histogram_rederived"] = hist_5000_def
    gate["shard_5000_defected_S_histogram_pilot"] = pilot_def_hist
    gate["shard_6000_undefected_S_histogram_rederived"] = hist_6000_true
    gate["shard_6000_undefected_S_histogram_pilot"] = pilot_undef_hist
    gate["verdict"] = ("PASS" if (gate["shard_5000_defected_matches_pilot"]
                                  and gate["shard_6000_undefected_matches_pilot"])
                       else "FAILED_DETERMINISM_GATE")

    R["gate_determinism"] = gate
    R["stage1_per_shard_timing"] = per_shard_timing
    R["stage1_hard_invariants"] = dict(
        shard_5000=dict(d2_fail=arms[5000]["d2_fail"], d3_fail=arms[5000]["d3_fail"],
                        d3_max_w=arms[5000]["d3_max_w"], d3_cap=arms[5000]["d3_cap"]),
        shard_6000=dict(d2_fail=arms[6000]["d2_fail"], d3_fail=arms[6000]["d3_fail"],
                        d3_max_w=arms[6000]["d3_max_w"], d3_cap=arms[6000]["d3_cap"]))

    if gate["verdict"] != "PASS":
        R["stage1_status"] = "ABORTED_DETERMINISM_GATE_FAILED"
        return R, None

    R["stage1_per_trial_S"] = dict(
        shard_5000_true=s5000_true, shard_5000_defected=s5000_def,
        shard_6000_true=s6000_true, shard_6000_defected=s6000_def,
        note="Persisted in TRIAL ORDER; entry i of each shard's true/defected "
             "arrays derives from the SAME generated bit array (design.md "
             "Section 1), making the pairing auditable directly.")

    stats_5000 = matched_pair_stats(sa, measure, s5000_true, s5000_def, n_e, ks, C, N_JACK_BATCHES)
    stats_6000 = matched_pair_stats(sa, measure, s6000_true, s6000_def, n_e, ks, C, N_JACK_BATCHES)
    pooled_true = list(s5000_true) + list(s6000_true)
    pooled_def = list(s5000_def) + list(s6000_def)
    stats_pooled = matched_pair_stats(sa, measure, pooled_true, pooled_def, n_e, ks, C, N_JACK_BATCHES)

    R["stage1_status"] = "OK"
    R["stage1"] = dict(
        per_shard={"5000": stats_5000, "6000": stats_6000},
        pooled=stats_pooled,
        pooling_note="Pooled arrays concatenate shard 5000's trials followed "
                     "by shard 6000's, in that fixed order, identically for "
                     "the true and defected arrays, so trial-for-trial "
                     "pairing is preserved through pooling.")

    se_pooled_k17 = cell_at_k(stats_pooled, M_LOAD_BEARING)["paired_jackknife_se"]
    R["stage1_SE_pooled_k17_paired"] = se_pooled_k17
    return R, se_pooled_k17


def run_stage2(sa, measure, defected_decode, original_decode, ks, C, n_e, R, T2):
    remaining = T2
    per_shard_timing = []
    trues, defs = [], []
    used_shards = []
    for shard in STAGE2_SHARD_POOL:
        if remaining <= 0:
            break
        n_trials = min(STAGE2_TRIALS_PER_SHARD, remaining)
        r = dual_decode_shard(sa, ps=R["_ps"], shard=shard, n_trials=n_trials,
                              wall_cap=WALL_CAP_PER_CALL, batch=BATCH,
                              decode_a=original_decode, decode_b=defected_decode)
        used_shards.append(shard)
        per_shard_timing.append(dict(shard=shard, trials_requested=n_trials,
                                     trials_done=r["trials_done"],
                                     cpu_seconds=r["cpu_seconds"],
                                     wall_seconds=r["wall_seconds"],
                                     truncated=r["truncated"],
                                     d2_fail=r["d2_fail"], d3_fail=r["d3_fail"],
                                     d3_max_w=r["d3_max_w"], d3_cap=r["d3_cap"]))
        trues.append(r["S_a"]); defs.append(r["S_b"])
        remaining -= r["trials_done"]

    R["stage2_shards_used"] = used_shards
    R["stage2_per_shard_timing"] = per_shard_timing
    R["stage2_hard_invariants"] = dict(
        total_d2_fail=sum(t["d2_fail"] for t in per_shard_timing),
        total_d3_fail=sum(t["d3_fail"] for t in per_shard_timing),
        max_d3_w_observed=max((t["d3_max_w"] for t in per_shard_timing), default=0),
        d3_cap=per_shard_timing[0]["d3_cap"] if per_shard_timing else None)

    per_shard_stats = {}
    for i, shard in enumerate(used_shards):
        per_shard_stats[str(shard)] = matched_pair_stats(
            sa, measure, trues[i], defs[i], n_e, ks, C, N_JACK_BATCHES)

    pooled_true = [x for arr in trues for x in arr]
    pooled_def = [x for arr in defs for x in arr]
    T_achieved = len(pooled_true)
    stats_pooled = matched_pair_stats(sa, measure, pooled_true, pooled_def, n_e, ks, C, N_JACK_BATCHES)

    R["stage2"] = dict(
        T2_planned=T2, T2_achieved=T_achieved,
        achieved_equals_planned=(T_achieved == T2),
        per_shard=per_shard_stats, pooled=stats_pooled,
        pooling_note="Pooled arrays concatenate stage-2 shards in the order "
                     "listed in stage2_shards_used, identically for the true "
                     "and defected arrays.")
    R["stage2_per_trial_S"] = dict(
        note="Per-shard per-trial S arrays for stage 2 are reported under "
             "stage2.per_shard's implicit construction; the raw arrays "
             "themselves are omitted here to keep the artifact a bounded "
             "size at T2 up to 60,000 trials (2 arrays x T2), unlike stage "
             "1's 10,000-trial arrays which ARE persisted in full above. "
             "The histograms and jackknife folds in stage2.per_shard / "
             "stage2.pooled are computed directly from the arrays at run "
             "time and are reproducible bit-for-bit by re-running this "
             "script with --stage 2 (deterministic PRNG).")
    return R


def fit_se_exponent(points):
    """points: list of (T, SE). Returns (exponent, slope, intercept, r_points)."""
    Ts = np.array([p[0] for p in points], dtype=np.float64)
    SEs = np.array([p[1] for p in points], dtype=np.float64)
    logT = np.log(Ts)
    logSE = np.log(SEs)
    slope, intercept = np.polyfit(logT, logSE, 1)
    return dict(exponent=float(-slope), slope=float(slope), intercept=float(intercept),
                points=[dict(T=float(t), SE=float(se)) for t, se in points])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=HERE)
    ap.add_argument("--stage", type=int, choices=[1, 2], required=True)
    args = ap.parse_args(argv)

    out_path = os.path.join(args.out_dir, "matched_pair_results.json")
    t_wall0, c_wall0 = time.time(), core_seconds()

    R = {}
    if args.stage == 2:
        if not os.path.exists(out_path):
            raise SystemExit("FAILED_IMPLEMENTATION: --stage 2 requires "
                             "matched_pair_results.json from a completed "
                             "--stage 1 run in --out-dir")
        R = json.load(open(out_path))
        if R.get("stage1_status") != "OK":
            raise SystemExit("FAILED_IMPLEMENTATION: stage 1 did not "
                             "complete OK; refusing to run stage 2")

    R.setdefault("task_id", "TASK-20260809-a79e4f")
    R.setdefault("role", "executor")
    R.setdefault("experiment_id", "EXP-HQC-982268")
    R.setdefault("hypothesis_id", "H-HQC-18d1b4")
    R.setdefault("goal", "GOAL-HQC-001")
    R.setdefault("batch", "BATCH-412513")
    R.setdefault("claim_tier", "toy")
    R.setdefault("design_reference", "design.md, written and frozen before stage 1 ran")
    R.setdefault("scope_statement",
                 "PS-R3 only. V3 (last-block-window-read-early) defect at the "
                 "decode_blocks injection point. Matched-pair design across "
                 "two pre-registered stages. NOT the full T_req run. NOTHING "
                 "here is a statement about HQC, A17, A5, any "
                 "decoding-failure rate, or any standardized parameter set.")

    stage_key = f"stage{args.stage}_run"
    R[stage_key] = dict(
        started_at_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        command=" ".join([sys.executable] + sys.argv),
        git=git_state(),
        environment=dict(
            python=sys.version, python_executable=sys.executable,
            platform=platform.platform(), machine=platform.machine(),
            numpy=np.__version__, cpu_count=os.cpu_count(),
            affinity=(len(os.sched_getaffinity(0))
                      if hasattr(os, "sched_getaffinity")
                      else os.cpu_count())))

    # ---- phase 0: fail-closed self-tests, BEFORE any real module load ----
    selftests = {
        "sha256_pin_mismatch": selftest_fail_closed_sha_mismatch(),
    }
    print(f"[stage {args.stage}][selftest] sha256 pin mismatch: "
          f"{selftests['sha256_pin_mismatch']['verdict']}", flush=True)
    if selftests["sha256_pin_mismatch"]["verdict"] != "PASS":
        raise SystemExit("FAILED_IMPLEMENTATION: sha256 pin fail-closed "
                         "selftest did not pass; refusing to proceed")

    # ---- phase 1: real, sha256-pinned, read-only module load -------------
    sa, sa_sha = load_module(STAGE_A_PY, STAGE_A_PY_EXPECTED_SHA256,
                             "stage_a.py", f"stage_a_frozen_mp_s{args.stage}")
    measure, measure_sha = load_module(MEASURE_PY, MEASURE_PY_EXPECTED_SHA256,
                                       "measure.py", f"measure_frozen_mp_s{args.stage}")
    R[stage_key]["provenance"] = dict(
        stage_a_path=os.path.relpath(STAGE_A_PY, REPO), stage_a_sha256=sa_sha,
        stage_a_sha256_expected=STAGE_A_PY_EXPECTED_SHA256,
        stage_a_sha256_match=(sa_sha == STAGE_A_PY_EXPECTED_SHA256),
        measure_path=os.path.relpath(MEASURE_PY, REPO), measure_sha256=measure_sha,
        measure_sha256_expected=MEASURE_PY_EXPECTED_SHA256,
        measure_sha256_match=(measure_sha == MEASURE_PY_EXPECTED_SHA256),
        stage_a_modified=False, measure_modified=False)

    ps = [p for p in sa.PARAM_SETS if p["id"] == SET_ID][0]
    n_e, n_2 = ps["n_e"], ps["n_2"]
    R["_ps"] = ps
    R["parameter_set"] = {k: ps[k] for k in
                          ("id", "role", "n", "n_e", "n_2", "dup", "omega",
                           "omega_r", "omega_e", "N")}
    R["parameter_set"]["m_load_bearing_order"] = M_LOAD_BEARING

    selftests["injection_invariant_mismatch"] = selftest_injection_invariant_fail(n_e, n_2)
    print(f"[stage {args.stage}][selftest] injection invariant deliberate "
          f"break: {selftests['injection_invariant_mismatch']['verdict']}", flush=True)
    if selftests["injection_invariant_mismatch"]["verdict"] != "PASS":
        raise SystemExit("FAILED_IMPLEMENTATION: injection-invariant "
                         "fail-closed selftest did not pass; refusing to proceed")
    R[stage_key]["fail_closed_selftests"] = selftests

    original_decode_blocks = sa.decode_blocks
    defected_decode_blocks = make_defected_decode_blocks(original_decode_blocks, n_2)
    R[stage_key]["injection"] = dict(
        defect_class="V3 (last-block-window-read-early)",
        injection_point="decode_blocks's block window, LAST BLOCK ONLY "
                        "(index n_e - 1), shifted left by exactly one bit "
                        "position; decode_blocks itself called unmodified",
        wrapper_calls_unmodified_function=(
            defected_decode_blocks.__wrapped_original_id__ == id(original_decode_blocks)),
        wrapped_original_qualname=defected_decode_blocks.__wrapped_original_qualname__,
        stage_a_py_edited_on_disk=False)

    ks = list(range(2, 27))
    C = measure.comb_matrix(n_e, ks)

    if args.stage == 1:
        R, se_pooled = run_stage1(sa, measure, defected_decode_blocks,
                                  original_decode_blocks, ks, C, n_e, R)
        if R.get("stage1_status") != "OK":
            spent_core = core_seconds() - c_wall0
            spent_wall = time.time() - t_wall0
            R[stage_key]["budget"] = dict(
                core_seconds_authorized=CORE_SECOND_BUDGET,
                core_seconds_spent=round(spent_core, 3),
                wall_seconds_authorized=WALL_SECOND_BUDGET,
                wall_seconds_spent=round(spent_wall, 3))
            R["validity"] = dict(
                status="invalid_measurement",
                reason="Stage-1 determinism gate failed to reproduce "
                       "pilot_results.json's committed S_histogram arrays "
                       "bit-identically. Per AGENTS.md rule 5 this is an "
                       "infrastructure/determinism regression, not a "
                       "negative result about the mathematics.")
            R.pop("_ps", None)
            json.dump(R, open(out_path, "w"), indent=1)
            print(f"[stage 1][ABORT] determinism gate FAILED; see "
                  f"gate_determinism in {out_path}", flush=True)
            return R

        se_k17 = cell_at_k(R["stage1"]["pooled"], M_LOAD_BEARING)["paired_jackknife_se"]
        T2_raw = 10000 * (se_k17 * Z_STAR / DELTA) ** 2
        T2 = int(min(T2_CAP, max(T2_FLOOR, round(T2_raw))))
        R["stage2_trial_count_rule"] = dict(
            formula="T2 = clamp(round(10000 * (SE_pooled_measured * 2.80 / "
                    "0.20) ** 2), 20000, 60000)",
            SE_pooled_measured_k17=se_k17, delta=DELTA, z=Z_STAR,
            T2_raw_before_clamp=T2_raw, T2_floor=T2_FLOOR, T2_cap=T2_CAP,
            T2=T2, substitution=f"T2 = clamp(round(10000 * ({se_k17} * "
                                f"{Z_STAR} / {DELTA}) ** 2), {T2_FLOOR}, "
                                f"{T2_CAP}) = {T2}")
        print(f"[stage 1] SE_pooled@k=17 (paired) = {se_k17:.6f}  "
              f"-> T2 = {T2}", flush=True)

    else:  # stage 2
        T2 = R["stage2_trial_count_rule"]["T2"]
        R = run_stage2(sa, measure, defected_decode_blocks,
                       original_decode_blocks, ks, C, n_e, R, T2)

        # SE-vs-T exponent (design.md Section 3.4)
        se_5000 = cell_at_k(R["stage1"]["per_shard"]["5000"], M_LOAD_BEARING)["paired_jackknife_se"]
        se_6000 = cell_at_k(R["stage1"]["per_shard"]["6000"], M_LOAD_BEARING)["paired_jackknife_se"]
        se_5000_mean = 0.5 * (se_5000 + se_6000)
        se_10000 = cell_at_k(R["stage1"]["pooled"], M_LOAD_BEARING)["paired_jackknife_se"]
        se_T2 = cell_at_k(R["stage2"]["pooled"], M_LOAD_BEARING)["paired_jackknife_se"]
        T2_achieved = R["stage2"]["T2_achieved"]
        R["se_vs_trial_count_exponent"] = fit_se_exponent(
            [(5000, se_5000_mean), (10000, se_10000), (T2_achieved, se_T2)])
        R["se_vs_trial_count_exponent"]["per_shard_k17_se_5000_scale"] = dict(
            shard_5000=se_5000, shard_6000=se_6000, mean_used=se_5000_mean)

        ok1 = R["gate_determinism"]["verdict"] == "PASS"
        ok2 = (R["stage2_hard_invariants"]["total_d2_fail"] == 0
               and R["stage2_hard_invariants"]["total_d3_fail"] == 0
               and R["stage2"]["achieved_equals_planned"])
        exp = R["se_vs_trial_count_exponent"]["exponent"]
        exp_in_band = (0.4 <= exp <= 0.6)
        R["validity"] = dict(
            status="valid_measurement" if (ok1 and ok2) else "invalid_measurement",
            reason=("Determinism gate passed, D2/D3 clean on stage 2, and "
                    "stage 2 achieved its planned T2."
                    if (ok1 and ok2) else
                    "See gate_determinism / stage2_hard_invariants / "
                    "stage2.achieved_equals_planned for the failing check."),
            se_exponent_in_prespecified_band_0_4_to_0_6=bool(exp_in_band),
            certificate=dict(
                kind="none",
                reason="This run makes no discrete-log-solve or "
                       "factor-base-relation claim; the certificate "
                       "discipline in docs/claims-and-verification.md does "
                       "not apply. This is a joint-moment estimator "
                       "measurement on a toy-scale reduced parameter set."))

    spent_core = core_seconds() - c_wall0
    spent_wall = time.time() - t_wall0
    R[stage_key]["budget"] = dict(
        core_seconds_authorized=CORE_SECOND_BUDGET,
        core_seconds_spent=round(spent_core, 3),
        wall_seconds_authorized=WALL_SECOND_BUDGET,
        wall_seconds_spent=round(spent_wall, 3),
        within_core_second_budget=spent_core <= CORE_SECOND_BUDGET,
        within_wall_budget=spent_wall <= WALL_SECOND_BUDGET)
    R[stage_key]["finished_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    R.pop("_ps", None)
    with open(out_path, "w") as fh:
        json.dump(R, fh, indent=1)
    print(f"[stage {args.stage}][done] {out_path}  core-s={spent_core:.2f}  "
          f"wall={spent_wall:.1f}s", flush=True)
    return R


if __name__ == "__main__":
    main()
