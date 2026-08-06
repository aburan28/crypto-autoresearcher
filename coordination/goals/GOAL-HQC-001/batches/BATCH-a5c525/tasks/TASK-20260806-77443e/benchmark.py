#!/usr/bin/env python3
"""Calibration benchmark for TASK-20260806-77443e (executor) / BATCH-a5c525 /
GOAL-HQC-001.

PURPOSE
-------
This is NOT the real-sampler defect-injection experiment DEC-20260806-0995d5
named as GOAL-HQC-001's next action. It is a SMALL timing-calibration
benchmark that measures the REAL, unmodified generation path of
stage_a.py -- CTRStream, fixed_weight_support (Floyd's algorithm),
ring_mul_sparse, and decode_blocks (the real WHT/Reed-Muller decoder) -- at
small trial counts (hundreds to low thousands per parameter set), so
cost_model.md can report grounded, measured per-stage throughput instead of
an estimate. It samples genuine (T)-distributed HQC-shaped instances through
stage_a.py's real code (imported read-only, never modified), but the trial
counts here are far too small to constitute a measurement of anything about
HQC, A17, or any decoding-failure rate. Claim tier: TOY, hard ceiling.

FAIL-CLOSED SELF-INTEGRITY CHECK
---------------------------------
Before any timing is recorded, this script re-runs a subset of stage_a.py's
own SMOKE-SELF-TESTS invariants (fixed-weight exactness/distinctness,
sparse-vs-dense ring-multiplication agreement, WHT-vs-dense-Hadamard
agreement) against the imported, unmodified stage_a module. Any failure
raises SystemExit(1) and NO benchmark numbers are produced or reported --
this is a real abort on a real mismatch, not a warning.

This script imports stage_a.py READ-ONLY (sys.path insertion + import).
It does not modify stage_a.py, does not write anywhere outside its own task
directory, and does not touch measure.py.

Re-run:
    PYTHONDONTWRITEBYTECODE=1 python3 benchmark.py --out benchmark_results.json
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
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", "..", ".."))
STAGE_A_DIR = os.path.join(
    REPO, "coordination", "goals", "GOAL-HQC-001", "batches", "BATCH-6fddee",
    "tasks", "TASK-20260806-64b506")
STAGE_A_PATH = os.path.join(STAGE_A_DIR, "stage_a.py")

# --------------------------------------------------------------------------
# read-only import of the REAL, unmodified stage_a.py
# --------------------------------------------------------------------------

STAGE_A_SHA256 = hashlib.sha256(open(STAGE_A_PATH, "rb").read()).hexdigest()

spec = importlib.util.spec_from_file_location("stage_a_readonly", STAGE_A_PATH)
sa = importlib.util.module_from_spec(spec)
sys.modules["stage_a_readonly"] = sa
spec.loader.exec_module(sa)  # defines functions/constants only; no __main__ side effects

# Benchmark-only domain tags, deliberately DISTINCT from the real (T)/NULL-M/
# NULL-P/CTRL-BS arm domains stage_a.py itself uses ("T", "NULL-M", "NULL-P",
# "CTRL-BS"), and from the per-vector tags "v0".."v4" _t_shard uses, so no
# benchmark draw can ever be mistaken for, or reused as, part of any real
# measurement instance.
BENCH_ARM_DOMAIN = "BENCH-TASK-77443e"
BENCH_VEC_TAGS = (b"bv0", b"bv1", b"bv2", b"bv3", b"bv4")


# --------------------------------------------------------------------------
# fail-closed self-integrity gate
# --------------------------------------------------------------------------

def self_integrity_gate() -> dict:
    """Re-run a subset of stage_a.py's own SMOKE-SELF-TESTS invariants
    against the imported module. Aborts (SystemExit(1)) on ANY real
    mismatch -- this is not advisory."""
    checks = {}

    H = np.ones((1, 1), dtype=np.int64)
    for _ in range(7):
        H = np.block([[H, H], [H, -H]])
    v = np.random.default_rng(7).integers(-3, 4, size=(5, 128)).astype(np.int32)
    checks["wht_matches_dense_hadamard"] = bool(
        np.array_equal(sa.wht128(v.copy()), (v.astype(np.int64) @ H.T).astype(np.int32)))

    st = sa.CTRStream(b"integrity-key---", b"ring-gate")
    n = 251
    sa_supp = sa.fixed_weight_support(st, n, 7)
    sb_supp = sa.fixed_weight_support(st, n, 9)
    ai = sa.support_to_int(sa_supp, (n + 7) // 8)
    checks["ring_sparse_equals_dense"] = bool(
        sa.ring_mul_sparse(ai, sb_supp, n, (1 << n) - 1) == sa.ring_mul_dense(sa_supp, sb_supp, n))

    ok = True
    for i in range(50):
        s = sa.fixed_weight_support(sa.CTRStream(b"integrity-key---", b"fw-gate%d" % i), 1000, 66)
        ok &= (len(s) == 66 and len(set(s)) == 66 and all(0 <= a < 1000 for a in s))
    checks["fixed_weight_exact_and_distinct"] = bool(ok)

    checks["stage_a_importable_and_hashed"] = bool(len(STAGE_A_SHA256) == 64)

    all_pass = all(checks.values())
    if not all_pass:
        sys.stderr.write(
            "FAIL-CLOSED SELF-INTEGRITY GATE FAILED: %r\n"
            "Aborting. No benchmark numbers are produced.\n" % checks)
        sys.exit(1)
    return dict(checks=checks, all_pass=all_pass)


# --------------------------------------------------------------------------
# per-stage timing primitives (calling stage_a's REAL functions directly)
# --------------------------------------------------------------------------

def bench_param_set(ps: dict, n_stage: int, n_tshard: int, warmup: int) -> dict:
    n, N, n_e, n_2, dup = ps["n"], ps["N"], ps["n_e"], ps["n_2"], ps["dup"]
    om, omr, ome = ps["omega"], ps["omega_r"], ps["omega_e"]
    mask_n, mask_N = (1 << n) - 1, (1 << N) - 1
    nbytes_n, nbytes_N = (n + 7) // 8, N // 8
    key = sa.sha_key(ps["id"], BENCH_ARM_DOMAIN, 0, sa.MASTER_SEED)

    def gen_trial(ti: int):
        sx = sa.fixed_weight_support(sa.CTRStream(key, BENCH_VEC_TAGS[0] + ti.to_bytes(8, "little")), n, om)
        sy = sa.fixed_weight_support(sa.CTRStream(key, BENCH_VEC_TAGS[1] + ti.to_bytes(8, "little")), n, om)
        s1 = sa.fixed_weight_support(sa.CTRStream(key, BENCH_VEC_TAGS[2] + ti.to_bytes(8, "little")), n, omr)
        s2 = sa.fixed_weight_support(sa.CTRStream(key, BENCH_VEC_TAGS[3] + ti.to_bytes(8, "little")), n, omr)
        se = sa.fixed_weight_support(sa.CTRStream(key, BENCH_VEC_TAGS[4] + ti.to_bytes(8, "little")), n, ome)
        return sx, sy, s1, s2, se

    # ---- warm-up (discarded; avoids cold-start / first-call bias) --------
    for ti in range(warmup):
        gen_trial(ti)

    # ---- STAGE 1: fixed_weight_support (Floyd's algorithm), 5 vectors/trial
    t0 = time.process_time()
    supports = [gen_trial(warmup + ti) for ti in range(n_stage)]
    t1 = time.process_time()
    stage1_cpu = t1 - t0

    # ---- STAGE 2: ring multiplication (support_to_int packing + the two
    #      ring_mul_sparse shift-XOR accumulations stage_a.py's _t_shard
    #      itself performs per trial) --------------------------------------
    t0 = time.process_time()
    ets = []
    for sx, sy, s1, s2, se in supports:
        xi = sa.support_to_int(sx, nbytes_n)
        r1 = sa.support_to_int(s1, nbytes_n)
        ei = sa.support_to_int(se, nbytes_n)
        epp = sa.ring_mul_sparse(xi, s2, n, mask_n) ^ sa.ring_mul_sparse(r1, sy, n, mask_n) ^ ei
        et = epp & mask_N
        ets.append(et)
    t1 = time.process_time()
    stage2_cpu = t1 - t0

    # ---- bit-packing (needed to feed decode_blocks; charged separately) --
    t0 = time.process_time()
    buf = np.zeros((n_stage, nbytes_N), dtype=np.uint8)
    for i, et in enumerate(ets):
        buf[i] = np.frombuffer(et.to_bytes(nbytes_N, "little"), dtype=np.uint8)
    bits = np.unpackbits(buf, axis=1, bitorder="little")[:, :N]
    t1 = time.process_time()
    pack_cpu = t1 - t0

    # ---- STAGE 3: decode_blocks (real WHT/Reed-Muller decoder), one batch
    #      call over all n_stage trials, matching how _t_shard invokes it --
    t0 = time.process_time()
    F, W, ties = sa.decode_blocks(bits, n_e, n_2, dup)
    t1 = time.process_time()
    stage3_cpu = t1 - t0

    # ---- authoritative full-pipeline cross-check via the REAL, unmodified
    #      _t_shard worker (D2/D3 invariant checks included, batch=64,
    #      replay disabled to isolate generation+decode cost) -------------
    t0w, t0c = time.time(), time.process_time()
    tshard = sa._t_shard((ps, 999, n_tshard, 600.0, 64, 0))
    t1w, t1c = time.time(), time.process_time()

    total_stage_cpu = stage1_cpu + stage2_cpu + pack_cpu + stage3_cpu
    return dict(
        param_set=ps["id"], n=n, n_e=n_e, N=N, dup=dup,
        omega=om, omega_r=omr, omega_e=ome,
        n_stage_trials=n_stage, warmup_trials=warmup,
        stage1_fixed_weight_support=dict(
            cpu_seconds_total=stage1_cpu, cpu_seconds_per_trial=stage1_cpu / n_stage,
            trials_per_core_second=n_stage / stage1_cpu if stage1_cpu > 0 else None,
            note="5 CTRStream-keyed fixed_weight_support calls per trial "
                 "(weights: 2*omega + 2*omega_r + omega_e = %d draws total)"
                 % (2 * om + 2 * omr + ome)),
        stage2_ring_multiplication=dict(
            cpu_seconds_total=stage2_cpu, cpu_seconds_per_trial=stage2_cpu / n_stage,
            trials_per_core_second=n_stage / stage2_cpu if stage2_cpu > 0 else None,
            note="support_to_int packing (x3) + 2 ring_mul_sparse shift-XOR "
                 "accumulations per trial (omega+omega_r=%d shifts of an "
                 "%d-bit integer)" % (om + omr, n)),
        stage_bitpack=dict(
            cpu_seconds_total=pack_cpu, cpu_seconds_per_trial=pack_cpu / n_stage,
            trials_per_core_second=n_stage / pack_cpu if pack_cpu > 0 else None),
        stage3_decode_blocks=dict(
            cpu_seconds_total=stage3_cpu, cpu_seconds_per_trial=stage3_cpu / n_stage,
            trials_per_core_second=n_stage / stage3_cpu if stage3_cpu > 0 else None,
            note="one batched decode_blocks() call over all n_stage_trials, "
                 "same real WHT/Reed-Muller decoder V2/V3 benchmarked"),
        stages_summed=dict(
            cpu_seconds_total=total_stage_cpu, cpu_seconds_per_trial=total_stage_cpu / n_stage,
            trials_per_core_second=n_stage / total_stage_cpu if total_stage_cpu > 0 else None,
            note="sum of stage1+stage2+bitpack+stage3, MY OWN separately-timed "
                 "calls to the real functions -- compare against "
                 "full_pipeline_via_real_t_shard below as a cross-check"),
        full_pipeline_via_real_t_shard=dict(
            n_trials_requested=n_tshard, trials_done=tshard["trials_done"],
            truncated=tshard["truncated"],
            cpu_seconds=tshard["cpu_seconds"], wall_seconds=tshard["wall_seconds"],
            cpu_seconds_per_trial=(tshard["cpu_seconds"] / tshard["trials_done"]
                                    if tshard["trials_done"] else None),
            trials_per_core_second=(tshard["trials_done"] / tshard["cpu_seconds"]
                                     if tshard["cpu_seconds"] > 0 else None),
            d2_fail=tshard["d2_fail"], d3_fail=tshard["d3_fail"],
            note="calls stage_a.py's own unmodified _t_shard() worker "
                 "directly (batch=64, replay/D5 disabled: want_replay=0). "
                 "Includes D2 (exact-weight) and D3 (support-cap) invariant "
                 "checking, i.e. this is the REAL per-trial cost stage_a.py "
                 "itself would charge, not a reimplementation."),
    )


def git_state() -> dict:
    def run(*a):
        try:
            return subprocess.run(a, cwd=REPO, capture_output=True, text=True,
                                   timeout=60).stdout.strip()
        except Exception as exc:  # noqa: BLE001
            return "unavailable: %s" % exc
    porcelain = run("git", "status", "--porcelain")
    return dict(commit=run("git", "rev-parse", "HEAD"),
                branch=run("git", "rev-parse", "--abbrev-ref", "HEAD"),
                dirty=bool(porcelain), dirty_entries=porcelain.splitlines()[:40],
                dirty_entry_count=len(porcelain.splitlines()))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    t_start_wall, t_start_cpu = time.time(), time.process_time()

    integrity = self_integrity_gate()

    # PS-R3 is the primary target of the named next action (n_e=56 order,
    # matching V1-V3's control-arm parameter set); PS-A/PS-R1/PS-R5 get
    # smaller samples, enough for a stable per-trial estimate, purely to
    # ground the standardized-parameter half of the cost table.
    plan = {
        "PS-R3": dict(n_stage=2000, n_tshard=2000, warmup=50),
        "PS-A": dict(n_stage=500, n_tshard=500, warmup=30),
        "PS-R1": dict(n_stage=500, n_tshard=500, warmup=30),
        "PS-R5": dict(n_stage=500, n_tshard=500, warmup=30),
    }

    results = {}
    for ps in sa.PARAM_SETS:
        if ps["id"] not in plan:
            continue
        p = plan[ps["id"]]
        results[ps["id"]] = bench_param_set(ps, p["n_stage"], p["n_tshard"], p["warmup"])

    t_end_wall, t_end_cpu = time.time(), time.process_time()

    out = dict(
        task_id="TASK-20260806-77443e",
        batch_id="BATCH-a5c525",
        goal_id="GOAL-HQC-001",
        purpose=("Small timing-calibration benchmark of stage_a.py's REAL "
                 "generation path (CTRStream, fixed_weight_support, "
                 "ring_mul_sparse, decode_blocks), imported read-only and "
                 "never modified. NOT the real-sampler defect-injection "
                 "experiment itself. Claim tier: toy."),
        claim_tier="toy",
        role="executor -- observations only; no interpretation, no status change",
        stage_a_path=os.path.relpath(STAGE_A_PATH, REPO),
        stage_a_sha256=STAGE_A_SHA256,
        self_integrity_gate=integrity,
        command=" ".join([sys.executable] + sys.argv),
        git=git_state(),
        environment=dict(
            python=sys.version, python_executable=sys.executable,
            platform=platform.platform(), machine=platform.machine(),
            numpy=np.__version__, cpu_count=os.cpu_count(),
            affinity=(len(os.sched_getaffinity(0))
                      if hasattr(os, "sched_getaffinity") else None),
        ),
        bench_domain_tag=BENCH_ARM_DOMAIN,
        bench_vector_tags=[t.decode() for t in BENCH_VEC_TAGS],
        master_seed_reused_from_stage_a=sa.MASTER_SEED,
        seed_note=("Reuses stage_a.py's MASTER_SEED constant only as an "
                   "input to sha_key's domain-separated derivation; the "
                   "arm domain tag ('%s') and per-vector tags are "
                   "benchmark-exclusive and share no domain string with any "
                   "real (T)/NULL-M/NULL-P/CTRL-BS arm, so no benchmark "
                   "draw is or could be reused as part of a measurement." % BENCH_ARM_DOMAIN),
        per_param_set=results,
        total_wall_seconds=t_end_wall - t_start_wall,
        total_cpu_seconds=t_end_cpu - t_start_cpu,
        started_at_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t_start_wall)),
        finished_at_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t_end_wall)),
    )

    def enc(o):
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, np.bool_):
            return bool(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        raise TypeError(str(type(o)))

    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=1, default=enc)
    print("WROTE", args.out)
    print("total_cpu_seconds=%.3f total_wall_seconds=%.3f"
          % (out["total_cpu_seconds"], out["total_wall_seconds"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
