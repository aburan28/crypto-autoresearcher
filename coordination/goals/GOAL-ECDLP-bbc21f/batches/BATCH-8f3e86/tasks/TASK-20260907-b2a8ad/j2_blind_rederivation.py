#!/usr/bin/env python3
"""J2 blind re-derivation of the G3-feasibility verdict -- TASK-20260907-b2a8ad.

Written from experiments/EXP-ECDLP-612fb1/amendments/v2_to_v3.yaml Section 3
(`g3_predicate`) and its `exact_parameter_table_for_this_item` ALONE, under
reading P2 (`reading_P2_instrument_family`), which invites an independent
uniformly random function on Z_N with an independent Bernoulli(theta) DP
marking rather than a reproduction of the frozen mix64 instrument.

Nothing under experiments/EXP-ECDLP-612fb1/source_v2/, source_v3/, any
RUN-ECDLP-612fb1-v3-* directory, the executor's task directory, the sibling
reviewer's task directory, or the EXP-ECDLP-6ac801 lane was read, opened,
imported, ported or consulted before this file was written and its output
sealed. See j2_seal_manifest.yaml for the sealed read-list and timestamps.

Clause map (amendment Section 3 clause -> code):
  parameters / exact_parameter_table  -> cell_parameters()
  reading_P2_instrument_family        -> draw_instrument()
  basins                              -> exact_basins()
  top_share                           -> top_share()
  pool                                -> build_pool()
  selection                           -> select_static()
  static_coverage                     -> static_coverage()
  predicate_per_seed / _per_cell      -> run_cell() / main()
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
import sys
import time

import numpy as np

# --- amendment Section 3 `parameters`, for this item's N = 2^24 row ----------
N_BITS = 24
N = 1 << N_BITS          # 16777216
T = 256                  # FROZEN by v2 at n = 24; not recomputed from N^(1/3)
T_SEL = T // 2           # 128, "T_sel = floor(T/2) EXACTLY"
R_PRIMARY = 2
SEEDS = (1, 2, 3, 4, 5)  # declared, five exactly
A_VALUES = (("1/16", 1.0 / 16.0), ("1/8", 1.0 / 8.0))

# Disclosed choice for the two items Section 3's
# `what_a_reviewer_needs_and_this_section_does_not_give` deliberately leaves
# open. Both are declared here, before the run, and recorded in the seal.
STREAM_ROOT = 0xB2A8AD           # this task's own id token, nothing borrowed
STREAM_INSTRUMENT = 1            # f and D  (P2's own random-function family)
STREAM_POOL_STARTS = 2           # (i) the uniform pool-start draw
STREAM_TIEBREAK = 3              # (ii) the tie-break key stream
POOL_START_BATCH = 4096          # batching of the start draw, disclosed


def cell_parameters(a: float) -> dict:
    """Amendment Section 3 `parameters`: W = sqrt(a*N/T) real-valued and NOT
    rounded, theta = 1/W, cap = ceil(8*W)."""
    w = math.sqrt(a * N / T)
    theta = 1.0 / w
    cap = math.ceil(8.0 * w)
    return {"a": a, "W": w, "theta": theta, "cap": cap}


def rng_for(a_index: int, seed: int, purpose: int) -> np.random.Generator:
    return np.random.default_rng(
        np.random.SeedSequence([STREAM_ROOT, a_index, seed, purpose])
    )


def draw_instrument(a_index: int, seed: int, theta: float):
    """Reading P2: our own uniformly random function f on Z_N, and our own
    INDEPENDENT Bernoulli(theta) DP marking. Deliberately not mix64."""
    rng = rng_for(a_index, seed, STREAM_INSTRUMENT)
    f = rng.integers(0, N, size=N, dtype=np.int64).astype(np.int32)
    dp = rng.random(N) < theta
    return f, dp


def exact_basins(f: np.ndarray, dp: np.ndarray, cap: int):
    """Amendment Section 3 `basins`, computed exactly by pointer doubling.

    dist(x) = least m >= 0 with D(f^m(x)) = 1; first_dp(x) = f^m(x) for that m.
    basin(d) = #{x : first_dp(x) = d AND dist(x) <= cap}.  Points with
    dist(x) > cap are CAPPED and belong to no basin; points whose trajectory
    enters a DP-free cycle are UNREACHABLE and belong to no basin.  dist(d) = 0
    for a DP d, so every DP is in its own basin.

    Invariant maintained: after k rounds, jump[x] = f^m(x) and length[x] = m
    with m = min(2^k, dist(x)); a DP is a fixed point of the jump with
    length 0, so absorbed entries stop moving.  Choosing 2^K > cap makes
    `length[x] <= cap` exactly the "not capped, not unreachable" test, since
    then length[x] = min(2^K, dist(x)) > cap whenever dist(x) > cap.
    """
    jump = np.where(dp, np.arange(N, dtype=np.int32), f)
    length = np.where(dp, 0, 1).astype(np.int32)

    rounds = 0
    reach = 1
    while reach <= cap:            # stop only once 2^rounds > cap
        length = length + length[jump]
        jump = jump[jump]
        rounds += 1
        reach <<= 1

    valid = length <= cap
    counts = np.bincount(jump[valid], minlength=N)
    dp_ids = np.flatnonzero(dp)
    basin = counts[dp_ids].astype(np.int64)
    del counts

    stats = {
        "doubling_rounds": rounds,
        "n_dps": int(dp_ids.size),
        "basin_mass": int(basin.sum()),
        "capped_or_unreachable_mass": int(N - int(valid.sum())),
        "capped_or_unreachable_fraction": float((N - int(valid.sum())) / N),
    }
    return dp_ids, basin, jump, length, valid, stats


def top_share(basin: np.ndarray, t: int) -> float:
    """Amendment Section 3 `top_share`: the t LARGEST basin(d) summed, over N.
    Ties among equal basin sizes do not change the sum, so no tie-break."""
    if t >= basin.size:
        return float(basin.sum()) / N
    part = np.partition(basin, basin.size - t)[basin.size - t:]
    return float(part.sum()) / N


def build_pool(a_index: int, seed: int, jump, length, cap: int, r: int):
    """Amendment Section 3 `pool`.

    Independent uniform starts from Z_N on a deterministic stream seeded by s.
    Each start is walked to its first DP or to the cap.  A capped walk is a
    MISS: charged `cap` group operations to P, contributing NOTHING.  A walk
    terminating at DP d after L steps credits S_d += L, h_d += 1 (L = 0 when
    the start is itself a DP).  GENERATION STOPS AT THE FIRST MOMENT the pool
    holds exactly r*T DISTINCT DPs.  Every generating walk, hit or miss, is
    charged to P.
    """
    target = r * T
    rng = rng_for(a_index, seed, STREAM_POOL_STARTS)
    s_sum: dict[int, int] = {}
    h_cnt: dict[int, int] = {}
    walks = misses = hits = 0
    p_ops = 0
    done = False
    while not done:
        starts = rng.integers(0, N, size=POOL_START_BATCH, dtype=np.int64)
        for x in starts:
            walks += 1
            if not bool(length[x] <= cap):
                misses += 1
                p_ops += cap                       # a MISS is charged `cap`
                continue
            hits += 1
            d = int(jump[x])
            steps = int(length[x])
            p_ops += steps
            if d in s_sum:
                s_sum[d] += steps
                h_cnt[d] += 1
            else:
                s_sum[d] = steps
                h_cnt[d] = 1
                if len(s_sum) == target:           # first moment we hit r*T
                    done = True
                    break
    assert len(s_sum) == target, (len(s_sum), target)
    ids = np.fromiter(s_sum.keys(), dtype=np.int64, count=target)
    s_arr = np.array([s_sum[int(i)] for i in ids], dtype=np.float64)
    h_arr = np.array([h_cnt[int(i)] for i in ids], dtype=np.float64)
    stats = {
        "generating_walks": walks,
        "hits": hits,
        "misses": misses,
        "capped_walk_fraction": float(misses / walks),
        "P_group_operations": int(p_ops),
        "P_over_sqrt_NT": float(p_ops / math.sqrt(N * T)),
        "distinct_dps": target,
    }
    return ids, s_arr, h_arr, stats


def select_static(a_index, seed, ids, s_arr, h_arr, w_len: float):
    """Amendment Section 3 `selection`: the T entries of LARGEST
        w(d) = S_d + 4 * W * h_d
    ties broken by an independent, seeded, deterministic key ASCENDING.

    w IS COMPUTED FROM POOL EVIDENCE ONLY.  No basin array is a parameter of
    this function or is in scope inside it -- exact basin sizes SCORE the
    selection (see static_coverage) and never MAKE it.  Selection by true basin
    size is a different and strictly stronger rule this predicate forbids.
    """
    weight = s_arr + 4.0 * w_len * h_arr
    tiekey = rng_for(a_index, seed, STREAM_TIEBREAK).random(ids.size)
    order = np.lexsort((tiekey, -weight))   # primary: w descending
    chosen = order[:T]
    return ids[chosen], weight, int(np.unique(weight).size)


def static_coverage(selected_ids, dp_ids, basin) -> float:
    """Amendment Section 3 `static_coverage`: the EXACT coverage of the table
    the realistic rule already chose.  This is the SCORING step."""
    pos = np.searchsorted(dp_ids, selected_ids)
    assert np.all(dp_ids[pos] == selected_ids), "selected entry is not a DP"
    return float(basin[pos].sum()) / N


def run_cell(a_label: str, a_index: int, a: float, seed: int, r: int) -> dict:
    par = cell_parameters(a)
    t0 = time.time()
    f, dp = draw_instrument(a_index, seed, par["theta"])
    dp_ids, basin, jump, length, valid, bstats = exact_basins(f, dp, par["cap"])
    del f, dp, valid

    ts_sel = top_share(basin, T_SEL)
    ts_full = top_share(basin, T)

    ids, s_arr, h_arr, pstats = build_pool(
        a_index, seed, jump, length, par["cap"], r
    )
    selected, weight, distinct_w = select_static(
        a_index, seed, ids, s_arr, h_arr, par["W"]
    )
    cov = static_coverage(selected, dp_ids, basin)

    margin = ts_sel - cov
    return {
        "a_label": a_label,
        "a": a,
        "seed": seed,
        "r": r,
        "N": N,
        "T": T,
        "T_sel": T_SEL,
        "W": par["W"],
        "theta": par["theta"],
        "cap": par["cap"],
        "TopShare_T_sel": ts_sel,
        "TopShare_T": ts_full,
        "StaticCov": cov,
        "margin": margin,
        "sign": "+" if margin >= 0 else "-",
        "g3_s": bool(margin >= 0),
        "exact_coverage_non_exceedance_ok": bool(cov <= ts_full),
        "weight_ties_present": bool(distinct_w < ids.size),
        "distinct_weight_values": distinct_w,
        "basin_stats": bstats,
        "pool_stats": pstats,
        "wall_seconds": time.time() - t0,
    }


def main() -> int:
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    cells = []
    rows = []
    for a_index, (a_label, a) in enumerate(A_VALUES):
        per_seed = []
        for seed in SEEDS:
            row = run_cell(a_label, a_index, a, seed, R_PRIMARY)
            rows.append(row)
            per_seed.append(row)
            print(
                "a=%-5s s=%d  TopShare(T_sel)=%.9f  StaticCov=%.9f  "
                "margin=%+.9f  %s  (%.1fs)"
                % (
                    a_label, seed, row["TopShare_T_sel"], row["StaticCov"],
                    row["margin"], "PASS" if row["g3_s"] else "fail",
                    row["wall_seconds"],
                ),
                file=sys.stderr, flush=True,
            )
        pc = sum(1 for x in per_seed if x["g3_s"])
        cells.append({
            "a_label": a_label,
            "a": a,
            "N": N, "T": T, "T_sel": T_SEL, "r": R_PRIMARY,
            "seeds": list(SEEDS),
            "pass_count": pc,
            "verdict": "G3 PASS" if pc >= 4 else "G3 FAIL",
            "signs": "".join(x["sign"] for x in per_seed),
            "margins": [x["margin"] for x in per_seed],
            "min_abs_margin": min(abs(x["margin"]) for x in per_seed),
        })
        print(
            "a=%-5s r=%d  pass_count=%d/5  %s  signs=%s"
            % (a_label, R_PRIMARY, pc, cells[-1]["verdict"], cells[-1]["signs"]),
            file=sys.stderr, flush=True,
        )

    out = {
        "task_id": "TASK-20260907-b2a8ad",
        "joint": "J2",
        "what_this_is": (
            "Independent (BLIND) re-derivation of the G3-feasibility verdict "
            "from experiments/EXP-ECDLP-612fb1/amendments/v2_to_v3.yaml "
            "Section 3 under reading P2. NOT a replication: no producer code "
            "was read, imported or consulted."
        ),
        "reading": "P2 (own uniformly random function on Z_N + own independent Bernoulli(theta) DP marking)",
        "agreement_criterion_this_is_judged_under": (
            "verdict and per-seed margin SIGN only; magnitudes differ between "
            "random-function families by construction and are NOT a break"
        ),
        "disclosed_open_choices": {
            "pool_start_prng": (
                "numpy PCG64 via default_rng(SeedSequence([0xB2A8AD, a_index, "
                "seed, 2])), drawn in batches of 4096 uniform int64 in [0, N)"
            ),
            "tiebreak_key_stream": (
                "numpy PCG64 via default_rng(SeedSequence([0xB2A8AD, a_index, "
                "seed, 3])); one float64 key per pool entry; selection is "
                "np.lexsort((tiekey, -weight)), i.e. w descending with the key "
                "ASCENDING as the amendment specifies"
            ),
            "instrument_stream": (
                "numpy PCG64 via default_rng(SeedSequence([0xB2A8AD, a_index, "
                "seed, 1])); f = uniform on [0, N) per point, D = "
                "(uniform(0,1) < theta) per point, independent of f"
            ),
        },
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "platform": platform.platform(),
        },
        "started_utc": started,
        "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "cells": cells,
        "per_seed": rows,
    }
    text = json.dumps(out, indent=2, sort_keys=False)
    with open("j2_output.json", "w") as fh:
        fh.write(text + "\n")
    print(
        "sha256(j2_output.json) = %s"
        % hashlib.sha256((text + "\n").encode()).hexdigest(),
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
