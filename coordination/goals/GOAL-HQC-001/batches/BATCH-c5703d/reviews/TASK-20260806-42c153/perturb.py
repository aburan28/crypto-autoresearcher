#!/usr/bin/env python3
"""RED TEAM probe: inject explicit defects into the REAL Stage-A (T) instrument
and ask whether CTRL-POSHOM (clause a and clause b) actually fires.

TASK-20260806-42c153 / BATCH-c5703d / GOAL-HQC-001.

Claim tier TOY.  Nothing here is a statement about HQC, A17, A5 or any
standardised parameter set.  Every number is about an instrument, and most of
them are about a DELIBERATELY BROKEN instrument.

BOUNDARY I HOLD: I do not report log2 A_k, mubar_k or Var(S) for the CORRECT
(T) arm.  Clause-(b) work uses only WITHIN-LAG CONTRASTS of the pairwise
co-occurrence matrix, whose null mean is zero under the hypothesis being tested
and which therefore need no unknown constant.  Where a statistic is invertible
to log2 A_2 I say so and withhold the invertible quantity.

VARIANTS (all share the same sampled (x,y,r1,r2,e) per trial, so a difference
between variants is the defect and not the draw):

  V0  correct                 e'' = x*r2 ^ r1*y ^ e ; et = e'' & mask_N ;
                              blocks = contiguous windows of n_2 coordinates.
  V1  off-by-one truncation   et = (e'' >> 1) & mask_N.
  V2  interleaved partition   block j = coordinates {j, j+n_e, j+2n_e, ...}.
  V3  last-block window off   block n_e-1 read one coordinate early.
  V4  no cyclic wrap          ring_mul drops `^ (acc >> n)`.
  V5  block-0 tie rule        block 0 breaks WHT argmax ties to the HIGHEST
                              index, every other block to the lowest.
  V6  last-block bit masked   coordinate 0 of block n_e-1 forced to 0.
  V7  shared sign misread     success declared on argmax index 0 regardless of
                              the sign of the transform coefficient, at EVERY
                              block (a position-equivariant decoder defect).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
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

RT_SEED = 42153            # this task's token; fixed before any draw
VARIANTS = ["V0_correct", "V1_offbyone_trunc", "V2_interleaved_blocks",
            "V3_lastblock_window", "V4_no_cyclic_wrap", "V5_block0_tie_rule",
            "V6_lastblock_bit_masked", "V7_shared_sign_misread"]


def load_stage_a():
    spec = importlib.util.spec_from_file_location("stage_a_rt", STAGE_A)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ring_mul_nowrap(a_int: int, supp_b, n: int, mask: int) -> int:
    """stage_a.ring_mul_sparse with the cyclic fold `^ (acc >> n)` DELETED."""
    acc = 0
    for s in supp_b:
        acc ^= a_int << s
    return acc & mask


def decode_variants(sa, bits, n_e, n_2, dup):
    """Re-implementation of stage_a.decode_blocks exposing the intermediate
    quantities, so position-dependent decoder defects can be injected.
    Verified against sa.decode_blocks by the caller."""
    B = bits.shape[0]
    blk = bits.reshape(B, n_e, n_2)
    folded = blk.reshape(B, n_e, dup, 128).sum(axis=2, dtype=np.int32)
    v = (dup - 2 * folded).astype(np.int32)
    t = sa.wht128(v.reshape(-1, 128)).reshape(B, n_e, 128)
    av = np.abs(t)
    idx_first = av.argmax(axis=2)
    idx_last = 127 - av[:, :, ::-1].argmax(axis=2)
    val_first = np.take_along_axis(t, idx_first[:, :, None], axis=2)[:, :, 0]
    F = ~((idx_first == 0) & (val_first > 0))
    F_lastidx = ~((idx_last == 0)
                  & (np.take_along_axis(t, idx_last[:, :, None], axis=2)[:, :, 0] > 0))
    F_signblind = ~(idx_first == 0)
    return F.astype(np.uint8), F_lastidx.astype(np.uint8), F_signblind.astype(np.uint8)


def _shard(args):
    (ps, shard, n_trials, batch, dump_F) = args
    sa = load_stage_a()
    t_cpu0 = time.process_time()
    n, N, n_e, n_2, dup = ps["n"], ps["N"], ps["n_e"], ps["n_2"], ps["dup"]
    om, omr, ome = ps["omega"], ps["omega_r"], ps["omega_e"]
    key = sa.sha_key(ps["id"], "RT-PERTURB-T", shard, RT_SEED)
    mask_n, mask_N = (1 << n) - 1, (1 << N) - 1
    nbytes_n, nbytes_N = (n + 7) // 8, N // 8

    F = {v: np.zeros((n_trials, n_e), dtype=np.uint8) for v in VARIANTS}
    buf0 = np.zeros((batch, nbytes_N), dtype=np.uint8)
    buf1 = np.zeros((batch, nbytes_N), dtype=np.uint8)
    buf4 = np.zeros((batch, nbytes_N), dtype=np.uint8)
    selftest_max = 0

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
            r2 = sa.support_to_int(s2, nbytes_n)
            ei = sa.support_to_int(se, nbytes_n)

            epp = (sa.ring_mul_sparse(xi, s2, n, mask_n)
                   ^ sa.ring_mul_sparse(r1, sy, n, mask_n) ^ ei)
            epp_nw = (ring_mul_nowrap(xi, s2, n, mask_n)
                      ^ ring_mul_nowrap(r1, sy, n, mask_n) ^ ei)

            buf0[i] = np.frombuffer((epp & mask_N).to_bytes(nbytes_N, "little"), dtype=np.uint8)
            buf1[i] = np.frombuffer(((epp >> 1) & mask_N).to_bytes(nbytes_N, "little"), dtype=np.uint8)
            buf4[i] = np.frombuffer((epp_nw & mask_N).to_bytes(nbytes_N, "little"), dtype=np.uint8)

        bits0 = np.unpackbits(buf0[:b], axis=1, bitorder="little")[:, :N]
        bits1 = np.unpackbits(buf1[:b], axis=1, bitorder="little")[:, :N]
        bits4 = np.unpackbits(buf4[:b], axis=1, bitorder="little")[:, :N]

        F0, F0_lastidx, F0_signblind = decode_variants(sa, bits0, n_e, n_2, dup)
        ref = sa.decode_blocks(bits0, n_e, n_2, dup)[0].astype(np.uint8)
        selftest_max = max(selftest_max, int(np.abs(F0.astype(int) - ref.astype(int)).max()))

        F["V0_correct"][t:t + b] = F0
        F["V1_offbyone_trunc"][t:t + b] = sa.decode_blocks(bits1, n_e, n_2, dup)[0]
        F["V4_no_cyclic_wrap"][t:t + b] = sa.decode_blocks(bits4, n_e, n_2, dup)[0]

        inter = bits0.reshape(b, n_2, n_e).transpose(0, 2, 1).reshape(b, N)
        F["V2_interleaved_blocks"][t:t + b] = sa.decode_blocks(inter, n_e, n_2, dup)[0]

        shifted = bits0.copy()
        lo = (n_e - 1) * n_2
        shifted[:, lo:lo + n_2] = bits0[:, lo - 1:lo + n_2 - 1]
        F["V3_lastblock_window"][t:t + b] = sa.decode_blocks(shifted, n_e, n_2, dup)[0]

        F5 = F0.copy()
        F5[:, 0] = F0_lastidx[:, 0]
        F["V5_block0_tie_rule"][t:t + b] = F5

        masked = bits0.copy()
        masked[:, lo] = 0
        F["V6_lastblock_bit_masked"][t:t + b] = sa.decode_blocks(masked, n_e, n_2, dup)[0]

        F["V7_shared_sign_misread"][t:t + b] = F0_signblind

        t += b

    out = {}
    for v in VARIANTS:
        Fv = F[v].astype(np.int64)
        S = Fv.sum(axis=1)
        out[v] = dict(
            block_counts=Fv.sum(axis=0).tolist(),
            pair_matrix=(Fv.T @ Fv).tolist(),
            S_hist=np.bincount(S, minlength=n_e + 1)[:n_e + 1].tolist(),
        )
    ret = dict(shard=shard, trials=n_trials, per_variant=out,
               decode_selftest_max_abs_diff_vs_stage_a=selftest_max,
               cpu_seconds=time.process_time() - t_cpu0)
    if dump_F:
        np.savez_compressed(dump_F % shard, **{v: F[v] for v in VARIANTS})
    return ret


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="PS-R1")
    ap.add_argument("--trials", type=int, default=300000)
    ap.add_argument("--shards", type=int, default=4)
    ap.add_argument("--batch", type=int, default=2000)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dump-F", default=None)
    a = ap.parse_args(argv)

    sa = load_stage_a()
    ps = [p for p in sa.PARAM_SETS if p["id"] == a.set][0]
    per = a.trials // a.shards
    jobs = [(ps, s, per, a.batch, a.dump_F) for s in range(a.shards)]
    t0 = time.time()
    with Pool(a.shards) as pool:
        res = pool.map(_shard, jobs)
    n_e = ps["n_e"]
    agg = {}
    for v in VARIANTS:
        bc = np.zeros(n_e, dtype=np.int64)
        pm = np.zeros((n_e, n_e), dtype=np.int64)
        sh = np.zeros(n_e + 1, dtype=np.int64)
        for r in res:
            bc += np.array(r["per_variant"][v]["block_counts"], dtype=np.int64)
            pm += np.array(r["per_variant"][v]["pair_matrix"], dtype=np.int64)
            sh += np.array(r["per_variant"][v]["S_hist"], dtype=np.int64)
        agg[v] = dict(block_counts=bc.tolist(), pair_matrix=pm.tolist(),
                      S_hist=sh.tolist())
    json.dump(dict(param_set=ps, trials=per * a.shards, shards=a.shards,
                   seed=RT_SEED, wall_seconds=time.time() - t0,
                   cpu_seconds=sum(r["cpu_seconds"] for r in res),
                   decode_selftest_max_abs_diff_vs_stage_a=max(
                       r["decode_selftest_max_abs_diff_vs_stage_a"] for r in res),
                   variants=agg),
              open(a.out, "w"))
    print("wall", round(time.time() - t0, 1), "cpu",
          round(sum(r["cpu_seconds"] for r in res), 1),
          "selftest", max(r["decode_selftest_max_abs_diff_vs_stage_a"] for r in res))


if __name__ == "__main__":
    main()
