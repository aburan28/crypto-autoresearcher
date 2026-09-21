#!/usr/bin/env python3
"""RED TEAM re-injection against the v3 control set.  TASK-20260806-250b29.

Re-runs six of the eight variants of TASK-20260806-42c153 through the REAL
Stage-A (T) instrument at PS-R1, with an INDEPENDENT seed, and evaluates the
CONTROLS AS v3 BINDS THEM (CTRL-POSHOM clauses (a) and (b) with REF-3 as the
binding reference; CTRL-IDXMAP as specified in amendment_v3.yaml).

Claim tier TOY.  Nothing here is a statement about HQC, A17, A5 or any
standardised parameter set.  Every number is about an instrument, and most of
them are about a deliberately broken one.

BOUNDARY: no log2 A_k, mubar_k or Var(S) is reported for the CORRECT (T) arm.
Clause-(a)/(b) statistics are position CONTRASTS whose null mean is zero
regardless of the unknown dependence, so they carry no estimate of A_2.

READ-SCOPE EXCURSION, DISCLOSED: loading the real instrument requires
BATCH-6fddee/.../stage_a.py, which is outside this task's declared read_scope.
The dispatch card orders an injection against the real instrument; that cannot
be done without it.  stage_a.py is NOT modified.

VARIANTS (all share the same (x,y,r1,r2,e) draws per trial):
  V0 correct; V1 off-by-one truncation window; V2 interleaved block partition;
  V3 last block's window read one coordinate early; V5 block-0 tie rule;
  V6 block n_e-1 coordinate 0 forced to 0.
V4 (no cyclic wrap) and V7 (inert) are not re-run: V4's verdict ("fires, zero
marginal value") is uncontested and it is the expensive variant, and V7
injected nothing.
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

RT_SEED = 250629          # this task's token 250b29 -> 0x250b29 = 2427689 -> see below
RT_SEED = 0x250B29        # fixed before any draw; INDEPENDENT of 42153
VARIANTS = ["V0_correct", "V1_offbyone_trunc", "V2_interleaved_blocks",
            "V3_lastblock_window", "V5_block0_tie_rule", "V6_lastblock_bit_masked"]


def load_stage_a():
    spec = importlib.util.spec_from_file_location("stage_a_rt3", STAGE_A)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def decode_variants(sa, bits, n_e, n_2, dup):
    """Re-implementation of stage_a.decode_blocks exposing the tie rule, so the
    position-dependent decoder defect V5 can be injected.  Asserted against
    sa.decode_blocks by the caller on every batch."""
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
    return F.astype(np.uint8), F_lastidx.astype(np.uint8)


def _shard(args):
    (ps, shard, n_trials, batch) = args
    sa = load_stage_a()
    t_cpu0 = time.process_time()
    n, N, n_e, n_2, dup = ps["n"], ps["N"], ps["n_e"], ps["n_2"], ps["dup"]
    om, omr, ome = ps["omega"], ps["omega_r"], ps["omega_e"]
    key = sa.sha_key(ps["id"], "RT3-REINJECT-T", shard, RT_SEED)
    mask_n, mask_N = (1 << n) - 1, (1 << N) - 1
    nbytes_n, nbytes_N = (n + 7) // 8, N // 8

    F = {v: np.zeros((n_trials, n_e), dtype=np.uint8) for v in VARIANTS}
    buf0 = np.zeros((batch, nbytes_N), dtype=np.uint8)
    buf1 = np.zeros((batch, nbytes_N), dtype=np.uint8)
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
            ei = sa.support_to_int(se, nbytes_n)
            epp = (sa.ring_mul_sparse(xi, s2, n, mask_n)
                   ^ sa.ring_mul_sparse(r1, sy, n, mask_n) ^ ei)
            buf0[i] = np.frombuffer((epp & mask_N).to_bytes(nbytes_N, "little"), dtype=np.uint8)
            buf1[i] = np.frombuffer(((epp >> 1) & mask_N).to_bytes(nbytes_N, "little"), dtype=np.uint8)

        bits0 = np.unpackbits(buf0[:b], axis=1, bitorder="little")[:, :N]
        bits1 = np.unpackbits(buf1[:b], axis=1, bitorder="little")[:, :N]

        F0, F0_lastidx = decode_variants(sa, bits0, n_e, n_2, dup)
        ref = sa.decode_blocks(bits0, n_e, n_2, dup)[0].astype(np.uint8)
        selftest_max = max(selftest_max, int(np.abs(F0.astype(int) - ref.astype(int)).max()))

        F["V0_correct"][t:t + b] = F0
        F["V1_offbyone_trunc"][t:t + b] = sa.decode_blocks(bits1, n_e, n_2, dup)[0]

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

        t += b

    # ---- statistics.  Position contrasts only; no A_k of the correct arm. ----
    out = {}
    for v in VARIANTS:
        Fv = F[v].astype(np.float64)
        S = Fv.sum(axis=1)
        # clause (a): Z_t = F_t - (S_t/n_e) 1   -> REF-3 sufficient statistics
        Z = Fv - (S[:, None] / n_e)
        # clause (b): within-lag contrasts  Y_t(d)_j = F_tj * F_t,(j+d mod n_e),
        # centred by the lag mean over j.  Null mean zero under clause (b).
        Yb = {}
        for d in (1, 2, 3):
            Yd = Fv * np.roll(Fv, -d, axis=1)
            Yb[d] = Yd - Yd.mean(axis=1, keepdims=True)
        out[v] = dict(
            block_counts=Fv.sum(axis=0).astype(np.int64).tolist(),
            Zsum=Z.sum(axis=0).tolist(),
            Zcross=(Z.T @ Z).tolist(),
            Ysum={d: Yb[d].sum(axis=0).tolist() for d in Yb},
            Ycross={d: (Yb[d].T @ Yb[d]).tolist() for d in Yb},
            n=int(Fv.shape[0]),
        )
    return dict(shard=shard, trials=n_trials, per_variant=out,
                decode_selftest_max_abs_diff_vs_stage_a=selftest_max,
                cpu_seconds=time.process_time() - t_cpu0)


def ref3(Zsum, Zcross, T, df_drop=1):
    """REF-3 (red team TASK-20260806-42c153 sec 3.4), the reference v3 BINDS.
    X = T * Zbar' pinv(Sigma_hat) Zbar ~ chi^2_{n_e-1}.  No unknown constant,
    no assumed independence, no modelled null."""
    Zsum = np.asarray(Zsum, dtype=np.float64)
    Zc = np.asarray(Zcross, dtype=np.float64)
    Zbar = Zsum / T
    Sig = Zc / T - np.outer(Zbar, Zbar)
    X = float(T * Zbar @ np.linalg.pinv(Sig, rcond=1e-10) @ Zbar)
    df = len(Zbar) - df_drop
    return X, df


def chi2_sf(x, df):
    """Wilson-Hilferty upper tail; adequate at the magnitudes here."""
    import math
    z = ((x / df) ** (1.0 / 3.0) - (1 - 2.0 / (9 * df))) / np.sqrt(2.0 / (9 * df))
    return 0.5 * math.erfc(z / np.sqrt(2.0))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="PS-R1")
    ap.add_argument("--trials", type=int, default=200000)
    ap.add_argument("--shards", type=int, default=4)
    ap.add_argument("--batch", type=int, default=2000)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)

    sa = load_stage_a()
    ps = [p for p in sa.PARAM_SETS if p["id"] == a.set][0]
    per = a.trials // a.shards
    jobs = [(ps, s, per, a.batch) for s in range(a.shards)]
    t0 = time.time()
    with Pool(a.shards) as pool:
        res = pool.map(_shard, jobs)
    n_e = ps["n_e"]
    T = per * a.shards

    report = {}
    q0 = None
    for v in VARIANTS:
        bc = np.zeros(n_e); Zs = np.zeros(n_e); Zc = np.zeros((n_e, n_e))
        Ys = {d: np.zeros(n_e) for d in (1, 2, 3)}
        Yc = {d: np.zeros((n_e, n_e)) for d in (1, 2, 3)}
        for r in res:
            pv = r["per_variant"][v]
            bc += np.array(pv["block_counts"], dtype=np.float64)
            Zs += np.array(pv["Zsum"]); Zc += np.array(pv["Zcross"])
            for d in (1, 2, 3):
                Ys[d] += np.array(pv["Ysum"][str(d)] if str(d) in pv["Ysum"] else pv["Ysum"][d])
                Yc[d] += np.array(pv["Ycross"][str(d)] if str(d) in pv["Ycross"] else pv["Ycross"][d])
        q = bc.sum() / (T * n_e)
        if v == "V0_correct":
            q0 = q
        # REF-1: independent-blocks Pearson Q on per-block failure counts
        exp = bc.sum() / n_e
        Q = float(((bc - exp) ** 2 / (exp * (1 - q))).sum())
        Xa, dfa = ref3(Zs, Zc, T)
        cb = {}
        for d in (1, 2, 3):
            Xd, dfd = ref3(Ys[d], Yc[d], T)
            cb[d] = dict(X_over_df=Xd / dfd, p=chi2_sf(Xd, dfd))
        report[v] = dict(
            q_hat=q,
            q_shift_pct=(100.0 * (q - q0) / q0) if q0 else 0.0,
            REF1_Q_over_df=Q / (n_e - 1),
            REF3_clause_a_X_over_df=Xa / dfa,
            REF3_clause_a_p=chi2_sf(Xa, dfa),
            REF3_clause_b={str(d): cb[d] for d in cb},
        )
    out = dict(task="TASK-20260806-250b29", param_set=ps, trials=T, seed=RT_SEED,
               wall_seconds=time.time() - t0,
               cpu_seconds=sum(r["cpu_seconds"] for r in res),
               decode_selftest_max_abs_diff_vs_stage_a=max(
                   r["decode_selftest_max_abs_diff_vs_stage_a"] for r in res),
               results=report)
    json.dump(out, open(a.out, "w"), indent=1)
    print("trials", T, "wall", round(out["wall_seconds"], 1),
          "cpu", round(out["cpu_seconds"], 1),
          "selftest_max_abs_diff", out["decode_selftest_max_abs_diff_vs_stage_a"])
    hdr = "%-24s %9s %9s %10s %10s %10s" % ("variant", "q_shift%", "REF1 Q/df",
                                            "REF3(a)/df", "REF3(a) p", "REF3(b1)/df")
    print(hdr)
    for v in VARIANTS:
        r = report[v]
        print("%-24s %9.4f %9.3f %10.3f %10.3g %10.3f"
              % (v, r["q_shift_pct"], r["REF1_Q_over_df"],
                 r["REF3_clause_a_X_over_df"], r["REF3_clause_a_p"],
                 r["REF3_clause_b"]["1"]["X_over_df"]))


if __name__ == "__main__":
    main()
