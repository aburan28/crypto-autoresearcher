#!/usr/bin/env python3
"""Blind re-derivation of J2 for TASK-20260907-b8f8a9.

Quantity (DEC-20260907-f394f5 review_plan.blind_rederivation.what):
  murmur3_fmix64 8-key mean scaled cost at N = 2^24, a = 1/4, T = 256.

Written from PA-ECDLP-869870-v1-to-v2's statement of the quantity and mixer
definition, plus the mixer primitives fmix64 / key() as specified in
coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-289698/tasks/TASK-20260906-7ec3ea/src/j2_rederive.py
(that path is not in blind_from). This file does not import executor code and
does not read source_v2/, execution-report-v2.yaml, or TASK-20260907-fe3512
report bodies.

Mixer (amendment murmur3_fmix64 definition):
  h ^= h>>33; h *= 0xff51afd7ed558ccd; h ^= h>>33;
  h *= 0xc4ceb9fe1a85ec53; h ^= h>>33.
  Walk f(x) = mix(x XOR K) mod N  (LOW log2 N bits).
  DP predicate mix(x XOR K2) < floor(2^64 / W).

Keys: sha256 as in j2_rederive.py key(), under THIS task's namespace so the
sealed cell is a fresh computation, not a copy of the prior 7ec3ea seal.

Fixture (v1 specification definitions + amendment cell):
  W = sqrt(a N / T) = 128; cap = 8W = 1024; r = 2 (2T distinct DPs);
  every walk charged to P (capped walks at the cap); weight S_d + 4 W h_d;
  table = top-T (ties by seeded permutation); M = 40000 single-walk trials;
  scaled_cost = (total trial steps) / hits / sqrt(N/T).

RNG (own, declared): pool/trial streams and tie seeds derived from this
task's key() namespace. Different from the 7ec3ea streams.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import resource
import time
from datetime import datetime, timezone

import numpy as np

U64 = np.uint64


def key(s: str) -> np.uint64:
    """sha256-derived 64-bit key, exactly as j2_rederive.py key()."""
    return U64(int.from_bytes(hashlib.sha256(s.encode()).digest()[:8], "big"))


def fmix64(h):
    """MurmurHash3 64-bit fmix64 finalizer (amendment + j2_rederive.py)."""
    h = h.astype(U64, copy=True)
    h ^= h >> U64(33)
    h *= U64(0xFF51AFD7ED558CCD)
    h ^= h >> U64(33)
    h *= U64(0xC4CEB9FE1A85EC53)
    h ^= h >> U64(33)
    return h


def build(N: int, W: int, kwalk, kdp):
    x = np.arange(N, dtype=U64)
    f = (fmix64(x ^ kwalk) & U64(N - 1)).astype(np.int64)
    thr = U64((1 << 64) // W)
    isdp = fmix64(x ^ kdp) < thr
    return f, isdp


def walk_batch(starts, f, isdp, cap):
    x = starts.astype(np.int64).copy()
    n = x.size
    length = np.zeros(n, np.int64)
    term = np.full(n, -1, np.int64)
    active = np.ones(n, bool)
    dp0 = isdp[x]
    term[dp0] = x[dp0]
    active[dp0] = False
    for step in range(1, cap + 1):
        ia = np.nonzero(active)[0]
        if ia.size == 0:
            break
        xi = f[x[ia]]
        x[ia] = xi
        dp = isdp[xi]
        hit = ia[dp]
        term[hit] = xi[dp]
        length[hit] = step
        active[hit] = False
    ia = np.nonzero(active)[0]
    length[ia] = cap
    term[ia] = -1
    return length, term


def fixture(N, T, W, f, isdp, cap, M, rng_pool, rng_trial, tie_seed):
    rT = 2 * T
    S = {}
    H = {}
    P = 0
    nwalks = 0
    ncapped = 0
    ndup = 0
    done = False
    while not done:
        starts = rng_pool.integers(0, N, size=64)
        L, D = walk_batch(starts, f, isdp, cap)
        for l, dd in zip(L.tolist(), D.tolist()):
            nwalks += 1
            if dd < 0:
                ncapped += 1
                P += cap
                continue
            if dd in S:
                ndup += 1
                P += l
                S[dd] += l
                H[dd] += 1
            else:
                P += l
                S[dd] = l
                H[dd] = 1
            if len(S) >= rT:
                done = True
                break
    dps = np.array(sorted(S), dtype=np.int64)
    w = np.array([S[d] + 4 * W * H[d] for d in dps.tolist()], dtype=np.int64)
    perm = np.random.default_rng(tie_seed).permutation(dps.size)
    order = np.lexsort((perm, -w))
    table = dps[order[:T]]
    tset = np.zeros(N, bool)
    tset[table] = True
    starts = rng_trial.integers(0, N, size=M)
    L, D = walk_batch(starts, f, isdp, cap)
    hits = int(((D >= 0) & tset[np.maximum(D, 0)]).sum())
    tot = int(L.sum())
    scaled_cost = (tot / hits / math.sqrt(N / T)) if hits else None
    return {
        "pool_walks": nwalks,
        "pool_distinct_dps": int(len(S)),
        "pool_capped_walks": ncapped,
        "pool_duplicate_walks": ndup,
        "P": int(P),
        "scaled_P": P / math.sqrt(N * T),
        "M": M,
        "hits": hits,
        "trial_total_steps": tot,
        "trial_capped_walks": int((D < 0).sum()),
        "mean_trial_length": tot / M,
        "hit_rate": hits / M,
        "scaled_cost": scaled_cost,
        "table_size": int(table.size),
        "table_id_hash": hashlib.sha256(np.sort(table).tobytes()).hexdigest()[:16],
    }


def main():
    N = 1 << 24
    T = 256
    a = 0.25
    W = int(round(math.sqrt(a * N / T)))
    assert W == 128, W
    cap = 8 * W
    M = 40000
    nkeys = 8
    mixname = "murmur3_fmix64"
    published = 1.79

    out = {
        "task_id": "TASK-20260907-b8f8a9",
        "joint": "J2",
        "quantity": "murmur3_fmix64 8-key mean scaled cost at N=2^24, a=1/4, T=256",
        "sealed_before_any_blind_from_read": True,
        "parameters": {
            "N": N,
            "T": T,
            "a": a,
            "W": W,
            "cap": cap,
            "M": M,
            "n_keys": nkeys,
            "mixer": mixname,
            "walk_projection": "low log2N bits / mix(x XOR K) mod N",
            "dp_predicate": "mix(x XOR K2) < floor(2^64/W)",
            "pool": "continue until 2T distinct DPs; every walk charged; capped at cap",
            "weight": "S_d + 4 W h_d",
            "key_namespace": "validator-b8f8a9|...",
            "not_copied_from": "TASK-20260906-7ec3ea sealed 1.6814 / -0.109",
        },
        "keys": [],
    }
    t0 = time.time()
    costs = []
    scaled_Ps = []
    for i in range(1, nkeys + 1):
        tk = time.time()
        kw = key(f"validator-b8f8a9|{mixname}|walk|N{N}|{i}")
        kd = key(f"validator-b8f8a9|{mixname}|dp|N{N}|{i}")
        f, isdp = build(N, W, kw, kd)
        pool_seed = int(key(f"validator-b8f8a9|pool|{mixname}|{N}|{i}|p")) % (1 << 63)
        trial_seed = int(key(f"validator-b8f8a9|trial|{mixname}|{N}|{i}|p")) % (1 << 63)
        rp = np.random.default_rng(pool_seed)
        rt = np.random.default_rng(trial_seed)
        fx = fixture(N, T, W, f, isdp, cap, M, rp, rt, tie_seed=88000 + i)
        rec = {
            "mixer": mixname,
            "key_index": i,
            "walk_key_hex": f"{int(kw):016x}",
            "dp_key_hex": f"{int(kd):016x}",
            "n_dp": int(isdp.sum()),
            "fixture": fx,
            "seconds": round(time.time() - tk, 2),
        }
        out["keys"].append(rec)
        costs.append(fx["scaled_cost"])
        scaled_Ps.append(fx["scaled_P"])
        print(
            f"key{i}: cost={fx['scaled_cost']:.6f} scaledP={fx['scaled_P']:.6f} "
            f"hits={fx['hits']} P={fx['P']} walks={fx['pool_walks']} "
            f"n_dp={rec['n_dp']} ({rec['seconds']}s)",
            flush=True,
        )

    arr = np.array(costs, dtype=float)
    parr = np.array(scaled_Ps, dtype=float)
    mean_cost = float(arr.mean())
    mean_P = float(parr.mean())
    raw_residual = mean_cost - published
    out["aggregates"] = {
        "n": int(arr.size),
        "scaled_cost_values": [float(x) for x in arr],
        "scaled_cost_mean": mean_cost,
        "scaled_cost_std": float(arr.std(ddof=1)),
        "scaled_cost_min": float(arr.min()),
        "scaled_cost_max": float(arr.max()),
        "scaled_P_values": [float(x) for x in parr],
        "scaled_P_mean": mean_P,
        "scaled_P_std": float(parr.std(ddof=1)),
        "published_scaled_cost": published,
        "raw_residual_mean_minus_1.79": raw_residual,
        "raw_band_0.10_pass": abs(raw_residual) <= 0.10,
    }
    out["elapsed_seconds"] = round(time.time() - t0, 2)
    out["peak_rss_kb_ru_maxrss"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    out["sealed_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    here = os.path.dirname(os.path.abspath(__file__))
    dest = os.path.join(here, "..", "j2_sealed.json")
    blob = json.dumps(out, indent=2, sort_keys=False)
    digest = hashlib.sha256(blob.encode()).hexdigest()
    out["seal_sha256_of_this_json_without_this_field"] = digest
    # Re-dump including the digest field; record the content hash of the
    # pre-digest blob so the mean cannot be edited without breaking the seal.
    with open(dest, "w") as fh:
        json.dump(out, fh, indent=2)
        fh.write("\n")
    print(f"SEALED mean_scaled_cost={mean_cost:.6f} raw_residual={raw_residual:.6f}")
    print(f"wrote {dest}")
    print(f"pre_digest_sha256={digest}")
    print(f"elapsed={out['elapsed_seconds']}s rss_kb={out['peak_rss_kb_ru_maxrss']}")


if __name__ == "__main__":
    main()
