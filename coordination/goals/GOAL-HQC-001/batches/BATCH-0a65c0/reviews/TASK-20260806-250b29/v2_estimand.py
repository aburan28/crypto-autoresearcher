#!/usr/bin/env python3
"""RED TEAM: does V2 -- the accepted blind spot -- actually change the estimand?
TASK-20260806-250b29.

amendment_v3.yaml accepts the shift-equivariant class as a blind spot and calls
V2 (interleaved block partition) "the serious one" because it is
"consequential AND exactly invisible": "a decimated window and a contiguous
window do not have the same weight law, so V2 DOES change the estimand."

The invisibility half is a theorem and is not disputed here.  The
CONSEQUENTIALITY half is asserted with no derivation and no measurement, and
the only number attached to it is a q-hat shift of +0.03%, which is a null.
This measures the other half.

WHAT IS REPORTED, AND THE BOUNDARY IT HOLDS: only the PAIRED CONTRAST
  Delta_k = log2 Ahat_k(V2) - log2 Ahat_k(V0)
on shared draws.  A difference of two unknowns discloses neither, so no value
of log2 A_k for the correct (T) arm is computed, reported, or recoverable from
this file.  The S histograms are aggregated in-process and only the contrast is
written out.

Claim tier TOY.  Nothing here is a statement about HQC, A17, A5 or any
standardised parameter set.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", "..", ".."))
STAGE_A = os.path.join(
    REPO, "coordination", "goals", "GOAL-HQC-001", "batches", "BATCH-6fddee",
    "tasks", "TASK-20260806-64b506", "stage_a.py")

RT_SEED = 0x250B29        # same seed as reinject.py: the SAME draws
VARIANTS = ["V0_correct", "V1_offbyone_trunc", "V2_interleaved_blocks",
            "V3_lastblock_window"]


def load_stage_a():
    spec = importlib.util.spec_from_file_location("stage_a_rt3b", STAGE_A)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _shard(args):
    (ps, shard, n_trials, batch, n_boot) = args
    sa = load_stage_a()
    t_cpu0 = time.process_time()
    n, N, n_e, n_2, dup = ps["n"], ps["N"], ps["n_e"], ps["n_2"], ps["dup"]
    om, omr, ome = ps["omega"], ps["omega_r"], ps["omega_e"]
    key = sa.sha_key(ps["id"], "RT3-REINJECT-T", shard, RT_SEED)
    mask_n, mask_N = (1 << n) - 1, (1 << N) - 1
    nbytes_n, nbytes_N = (n + 7) // 8, N // 8

    hist = {v: np.zeros(n_e + 1, dtype=np.int64) for v in VARIANTS}
    # bootstrap: fixed resample index blocks, SHARED across variants (paired)
    rng = np.random.Generator(np.random.PCG64(RT_SEED + 977 * shard))
    boot = {v: np.zeros((n_boot, n_e + 1), dtype=np.int64) for v in VARIANTS}

    buf0 = np.zeros((batch, nbytes_N), dtype=np.uint8)
    buf1 = np.zeros((batch, nbytes_N), dtype=np.uint8)
    t = 0
    while t < n_trials:
        b = min(batch, n_trials - t)
        for i in range(b):
            ti = t + i
            sx = sa.fixed_weight_support(sa.CTRStream(key, b"v0" + ti.to_bytes(8, "little")), n, om)
            sy = sa.fixed_weight_support(sa.CTRStream(key, b"v1" + ti.to_bytes(8, "little")), n, om)
            s1 = sa.fixed_weight_support(sa.CTRStream(key, b"v2" + ti.to_bytes(8, "little")), n, omr)
            s2 = sa.fixed_weight_support(sa.CTRStream(key, b"v3" + ti.to_bytes(8, "little")), n, omr)
            se = sa.fixed_weight_support(sa.CTRStream(key, b"v4" + ti.to_bytes(8, "little")), n, ome)
            xi = sa.support_to_int(sx, nbytes_n)
            yi = sa.support_to_int(sy, nbytes_n)
            r1 = sa.support_to_int(s1, nbytes_n)
            ei = sa.support_to_int(se, nbytes_n)
            epp = (sa.ring_mul_sparse(xi, s2, n, mask_n)
                   ^ sa.ring_mul_sparse(r1, sy, n, mask_n) ^ ei)
            buf0[i] = np.frombuffer((epp & mask_N).to_bytes(nbytes_N, "little"), dtype=np.uint8)
            buf1[i] = np.frombuffer(((epp >> 1) & mask_N).to_bytes(nbytes_N, "little"), dtype=np.uint8)

        bits0 = np.unpackbits(buf0[:b], axis=1, bitorder="little")[:, :N]
        bits1 = np.unpackbits(buf1[:b], axis=1, bitorder="little")[:, :N]
        inter = bits0.reshape(b, n_2, n_e).transpose(0, 2, 1).reshape(b, N)
        shifted = bits0.copy()
        lo = (n_e - 1) * n_2
        shifted[:, lo:lo + n_2] = bits0[:, lo - 1:lo + n_2 - 1]

        S = {}
        S["V0_correct"] = sa.decode_blocks(bits0, n_e, n_2, dup)[0].sum(axis=1)
        S["V1_offbyone_trunc"] = sa.decode_blocks(bits1, n_e, n_2, dup)[0].sum(axis=1)
        S["V2_interleaved_blocks"] = sa.decode_blocks(inter, n_e, n_2, dup)[0].sum(axis=1)
        S["V3_lastblock_window"] = sa.decode_blocks(shifted, n_e, n_2, dup)[0].sum(axis=1)
        idx = rng.integers(0, b, size=(n_boot, b))      # SHARED resample indices
        for v in VARIANTS:
            s = np.asarray(S[v], dtype=np.int64)
            hist[v] += np.bincount(s, minlength=n_e + 1)[:n_e + 1]
            bs = s[idx]
            for r in range(n_boot):
                boot[v][r] += np.bincount(bs[r], minlength=n_e + 1)[:n_e + 1]
        t += b

    return dict(shard=shard, trials=n_trials,
                hist={v: hist[v].tolist() for v in VARIANTS},
                boot={v: boot[v].tolist() for v in VARIANTS},
                cpu_seconds=time.process_time() - t_cpu0)


def log2_A(hist, n_e, k):
    H = np.asarray(hist, dtype=np.float64)
    T = H.sum()
    q = (H @ np.arange(n_e + 1)) / (T * n_e)
    mu = (H @ np.array([float(math.comb(s, k)) for s in range(n_e + 1)])) / (T * math.comb(n_e, k))
    if mu <= 0 or q <= 0:
        return None
    return math.log2(mu) - k * math.log2(q)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="PS-R1")
    ap.add_argument("--trials", type=int, default=400000)
    ap.add_argument("--shards", type=int, default=4)
    ap.add_argument("--batch", type=int, default=2000)
    ap.add_argument("--boot", type=int, default=200)
    ap.add_argument("--out", default="v2_estimand.json")
    a = ap.parse_args(argv)

    sa = load_stage_a()
    ps = [p for p in sa.PARAM_SETS if p["id"] == a.set][0]
    n_e = ps["n_e"]
    per = a.trials // a.shards
    t0 = time.time()
    with Pool(a.shards) as pool:
        res = pool.map(_shard, [(ps, s, per, a.batch, a.boot) for s in range(a.shards)])
    T = per * a.shards

    H = {v: np.zeros(n_e + 1, dtype=np.int64) for v in VARIANTS}
    B = {v: np.zeros((a.boot, n_e + 1), dtype=np.int64) for v in VARIANTS}
    for r in res:
        for v in VARIANTS:
            H[v] += np.array(r["hist"][v], dtype=np.int64)
            B[v] += np.array(r["boot"][v], dtype=np.int64)

    ks = [2, 3, 4, 5]
    out = {"task": "TASK-20260806-250b29", "param_set": ps["id"], "trials": T,
           "seed": RT_SEED, "boot_replicates": a.boot,
           "boundary": ("Only PAIRED CONTRASTS against V0 are reported. No log2 A_k, "
                        "mubar_k or S histogram of the correct (T) arm appears in this "
                        "file, and none is recoverable from it."),
           "q_shift_pct_vs_V0": {}, "delta_log2_A_vs_V0": {}}
    q0 = float(H["V0_correct"] @ np.arange(n_e + 1)) / (T * n_e)
    for v in VARIANTS:
        if v == "V0_correct":
            continue
        q = float(H[v] @ np.arange(n_e + 1)) / (T * n_e)
        out["q_shift_pct_vs_V0"][v] = 100.0 * (q - q0) / q0
        d = {}
        for k in ks:
            a0, av = log2_A(H["V0_correct"], n_e, k), log2_A(H[v], n_e, k)
            if a0 is None or av is None:
                continue
            db = np.array([log2_A(B[v][r], n_e, k) - log2_A(B["V0_correct"][r], n_e, k)
                           for r in range(a.boot)])
            d[k] = dict(delta=av - a0, boot_sd=float(db.std(ddof=1)),
                        boot_ci=[float(np.percentile(db, 2.5)), float(np.percentile(db, 97.5))],
                        z=(av - a0) / float(db.std(ddof=1)) if db.std(ddof=1) > 0 else None)
        out["delta_log2_A_vs_V0"][v] = d
    out["wall_seconds"] = time.time() - t0
    out["cpu_seconds"] = sum(r["cpu_seconds"] for r in res)
    json.dump(out, open(a.out, "w"), indent=1)

    print("PS-R1, T=%d shared draws, %d paired bootstrap replicates" % (T, a.boot))
    print("%-24s %10s  %s" % ("variant", "q shift %", "Delta log2 A_k vs V0 (bits) [paired boot z]"))
    for v in VARIANTS[1:]:
        cells = "  ".join("k=%d: %+.3e (z=%+.1f)" % (k, out["delta_log2_A_vs_V0"][v][k]["delta"],
                                                     out["delta_log2_A_vs_V0"][v][k]["z"])
                          for k in ks if k in out["delta_log2_A_vs_V0"][v])
        print("%-24s %10.4f  %s" % (v, out["q_shift_pct_vs_V0"][v], cells))
    print("wall %.0fs cpu %.0fs" % (out["wall_seconds"], out["cpu_seconds"]))


if __name__ == "__main__":
    main()
