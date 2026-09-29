"""J4 proves-too-much / nearby-object control for PA-ECDLP-869870-v1-to-v2.

Known-false object (DEC-20260907-f394f5 review_plan.proves_too_much):
    f(x) = (x + 1) mod N, same DP predicate form
    mix(x XOR K2) < floor(2^64 / W) with murmur3 fmix64 as written in the
    amendment (NOT imported from source_v2/).

Failure signature: fixture_gate_v2 PASSES (raw |mean scaled_cost - 1.79| <= 0.10
and |mean scaled_P - 1.24|/1.24 <= 0.12). This script must MISS 1.79.

Independent of the 16 v2 fixture cells. Not an EXP run. Reviewer control only.
"""
from __future__ import annotations

import hashlib
import json
import math
import time
from pathlib import Path

import numpy as np

N = 1 << 24
T = 256
A = 0.25
W = math.sqrt(A * N / T)
CAP = int(round(8 * W))
THRESHOLD = int(math.floor(2.0**64 / W))
SQRT_N_OVER_T = math.sqrt(N / T)
SQRT_NT = math.sqrt(N * T)
M_ONLINE = 40000
PUBLISHED_COST = 1.79
PUBLISHED_P = 1.24
BAND_COST = 0.10
BAND_P = 0.12
R_POOL = 2
SEEDS = (1, 2, 3)

FMIX_C1 = np.uint64(0xFF51AFD7ED558CCD)
FMIX_C2 = np.uint64(0xC4CEB9FE1A85EC53)


def fmix64(h: np.ndarray) -> np.ndarray:
    """MurmurHash3 64-bit fmix64 from the amendment text, independently typed."""
    h = h.astype(np.uint64, copy=True)
    h ^= h >> np.uint64(33)
    h *= FMIX_C1
    h ^= h >> np.uint64(33)
    h *= FMIX_C2
    h ^= h >> np.uint64(33)
    return h


def sha256_u64(s: str) -> int:
    return int.from_bytes(hashlib.sha256(s.encode()).digest()[:8], "big")


def next_dp_and_length(starts: np.ndarray, dps: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    nDP = int(dps.size)
    j = np.searchsorted(dps, starts)
    wrapped = j == nDP
    j = np.where(wrapped, 0, j)
    nxts = dps[j]
    lengths = np.where(wrapped, N - starts + int(dps[0]), nxts - starts)
    return nxts.astype(np.int64), lengths.astype(np.int64)


def run_one(seed: int, dp_mode: str) -> dict:
    t0 = time.perf_counter()
    if dp_mode == "hash_fmix64":
        k2 = sha256_u64(f"rt-9f3c12|identity|dp|{seed}")
        x = np.arange(N, dtype=np.uint64)
        isdp = fmix64(x ^ np.uint64(k2)) < np.uint64(THRESHOLD)
    elif dp_mode == "periodic":
        k2 = None
        isdp = (np.arange(N, dtype=np.int64) % int(W)) == 0
    else:
        raise ValueError(dp_mode)

    dps = np.flatnonzero(isdp).astype(np.int64)
    nDP = int(dps.size)
    if nDP == 0:
        raise RuntimeError("no DPs")

    gaps = np.empty(nDP, dtype=np.int64)
    gaps[0] = int(dps[0] + N - dps[-1])
    gaps[1:] = dps[1:] - dps[:-1]
    bs = np.zeros(N, dtype=np.int64)
    bs[dps] = gaps
    top_t_share = float(np.sort(gaps)[-T:].sum()) / N
    mean_gap = float(gaps.mean())
    max_gap = int(gaps.max())

    # Generation: uniform starts until R_POOL * T distinct DPs. Charge cap on miss.
    rng = np.random.RandomState(201 + seed)
    hits_h: dict[int, int] = {}
    hits_s: dict[int, int] = {}
    p_ops = 0
    walks = 0
    target = R_POOL * T
    # Bound the loop; identity walk reaches a DP in expected W steps.
    while len(hits_h) < target and walks < 200000:
        start = int(rng.randint(0, N))
        nxts, lengths = next_dp_and_length(np.array([start], dtype=np.int64), dps)
        length = int(lengths[0])
        nxt = int(nxts[0])
        walks += 1
        if length > CAP:
            p_ops += CAP
            continue
        p_ops += length
        hits_h[nxt] = hits_h.get(nxt, 0) + 1
        hits_s[nxt] = hits_s.get(nxt, 0) + length

    pool = np.fromiter(hits_h.keys(), dtype=np.int64)
    h = np.array([hits_h[int(d)] for d in pool], dtype=np.float64)
    s = np.array([hits_s[int(d)] for d in pool], dtype=np.float64)
    weight = s + 4.0 * W * h
    # Deterministic tie-break: higher weight, then lower id.
    order = np.lexsort((pool, -weight))
    table = pool[order[:T]]
    coverage = float(bs[table].sum()) / N
    scaled_p = p_ops / SQRT_NT

    rng_o = np.random.RandomState(101 + seed)
    starts = rng_o.randint(0, N, size=M_ONLINE).astype(np.int64)
    nxts, lengths = next_dp_and_length(starts, dps)
    charged = np.minimum(lengths, CAP)
    term_ok = lengths <= CAP
    in_table = np.zeros(N, dtype=bool)
    in_table[table] = True
    hit = term_ok & in_table[nxts]
    n_hits = int(hit.sum())
    total_steps = int(charged.sum())
    scaled = (total_steps / n_hits / SQRT_N_OVER_T) if n_hits else float("inf")

    # Exact-expectation on the whole [0, N): same formula as the instrument.
    all_x = np.arange(N, dtype=np.int64)
    all_nxt, all_len = next_dp_and_length(all_x, dps)
    all_ok = all_len <= CAP
    all_hit = all_ok & in_table[all_nxt]
    exact_p_hit = float(all_hit.mean())
    exact_mean_len = float(np.minimum(all_len, CAP).mean())
    scaled_exact = (
        (exact_mean_len / exact_p_hit / SQRT_N_OVER_T) if exact_p_hit else float("inf")
    )

    residual_raw = scaled - PUBLISHED_COST
    residual_p_rel = (scaled_p - PUBLISHED_P) / PUBLISHED_P
    raw_cost_in_band = abs(residual_raw) <= BAND_COST
    raw_p_in_band = abs(residual_p_rel) <= BAND_P

    return {
        "seed": seed,
        "dp_mode": dp_mode,
        "walk": "f(x) = (x + 1) mod N",
        "K2": None if k2 is None else int(k2),
        "nDP": nDP,
        "mean_gap": mean_gap,
        "max_gap": max_gap,
        "top_T_share": top_t_share,
        "C_max_contract_a_1_4": 0.39,
        "generation_walks": walks,
        "pool_size": int(pool.size),
        "P_group_ops": p_ops,
        "scaled_P": scaled_p,
        "published_weight_coverage": coverage,
        "M": M_ONLINE,
        "hits": n_hits,
        "c_hat": n_hits / M_ONLINE,
        "total_steps": total_steps,
        "scaled_cost_sampled": scaled,
        "scaled_cost_exact_expectation": scaled_exact,
        "published_scaled_cost": PUBLISHED_COST,
        "residual_cost_raw": residual_raw,
        "residual_P_rel_raw": residual_p_rel,
        "raw_abs_residual_cost_le_0.10": raw_cost_in_band,
        "raw_abs_rel_residual_P_le_0.12": raw_p_in_band,
        "fixture_gate_v2_raw_would_pass": bool(raw_cost_in_band and raw_p_in_band),
        "wall_seconds": time.perf_counter() - t0,
    }


def main() -> None:
    out_dir = Path(__file__).resolve().parent.parent / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for mode in ("hash_fmix64", "periodic"):
        for seed in SEEDS:
            row = run_one(seed, mode)
            rows.append(row)
            print(
                f"{mode} s{seed}: cost={row['scaled_cost_sampled']:.4f} "
                f"P={row['scaled_P']:.4f} topT={row['top_T_share']:.6f} "
                f"C={row['published_weight_coverage']:.6f} "
                f"pass={row['fixture_gate_v2_raw_would_pass']}",
                flush=True,
            )

    def _agg(mode: str) -> dict:
        sel = [r for r in rows if r["dp_mode"] == mode]
        costs = [r["scaled_cost_sampled"] for r in sel]
        ps = [r["scaled_P"] for r in sel]
        mean_c = float(np.mean(costs))
        mean_p = float(np.mean(ps))
        res_c = mean_c - PUBLISHED_COST
        res_p = (mean_p - PUBLISHED_P) / PUBLISHED_P
        raw_pass = abs(res_c) <= BAND_COST and abs(res_p) <= BAND_P
        return {
            "dp_mode": mode,
            "n_seeds": len(sel),
            "MEASURED_mean_scaled_cost": mean_c,
            "MEASURED_mean_scaled_P": mean_p,
            "residual_cost_raw_mean": res_c,
            "residual_P_rel_raw_mean": res_p,
            "raw_abs_residual_cost_le_0.10": abs(res_c) <= BAND_COST,
            "raw_abs_rel_residual_P_le_0.12": abs(res_p) <= BAND_P,
            "fixture_gate_v2_raw_would_pass": bool(raw_pass),
            "failure_signature_triggered": bool(raw_pass),
            "top_T_share_mean": float(np.mean([r["top_T_share"] for r in sel])),
            "published_weight_coverage_mean": float(
                np.mean([r["published_weight_coverage"] for r in sel])
            ),
            "per_seed": sel,
        }

    payload = {
        "control": "j4_identity_walk",
        "task_id": "TASK-20260907-9f3c12",
        "review_plan": "ledger/decisions/DEC-20260907-f394f5.yaml",
        "known_false_object": "f(x) = x + 1 (mod N), same DP predicate",
        "failure_signature": "fixture_gate_v2 PASSES for an identity or permutation walk",
        "N": N,
        "T": T,
        "a": A,
        "W": W,
        "cap": CAP,
        "note": (
            "Independent reviewer control. Does not re-run the 16 v2 fixture "
            "cells. Does not import source_v2/. fmix64 constants taken from "
            "PA-ECDLP-869870-v1-to-v2 murmur3 definition."
        ),
        "hash_fmix64": _agg("hash_fmix64"),
        "periodic": _agg("periodic"),
        "prior_internal_permutation_fixture": {
            "source": (
                "coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-289698/"
                "tasks/TASK-20260906-90e7cf/results/j4_perm_pipeline_verdicts.json"
            ),
            "object": "affine-xorshift keyed bijection (prior J4 known-false object)",
            "G2_fixture_cost_pooled": 50.21051733193277,
            "G2_cost_within_tolerance": False,
            "provenance": "internal",
        },
    }
    out = out_dir / "j4_identity_walk.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    main()
