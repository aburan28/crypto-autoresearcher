#!/usr/bin/env python3
"""
TASK-20260907-2db9aa -- Stage A blind re-derivation, RE-SEALED under the
v2 explicit STATIC(T)_r pool-selection weight formula, scoped ONLY to
a = 1/8 (plus a = 1/4 as a proves-too-much method control), per
ledger/handoffs/TASK-20260907-2db9aa.yaml and
experiments/EXP-ECDLP-6ac801/specification.v2.yaml `definitions` /
`blind_rederivation.v2_rerequirement_a_1_8`.

THIS IS A FROM-SCRATCH, INDEPENDENT IMPLEMENTATION. It was written having
read ONLY:
  - experiments/EXP-ECDLP-6ac801/specification.v2.yaml (the frozen v2
    contract's own `definitions`, `instrument`, `inputs`, `blind_rederivation`
    blocks)
  - ledger/handoffs/TASK-20260907-2db9aa.yaml (this task's own handoff,
    which restates the formula verbatim)
It has NOT read, and does not import or copy from, any file under
experiments/EXP-ECDLP-612fb1/source_v2/, any RUN-ECDLP-612fb1-v2-ascan-*/
or RUN-ECDLP-612fb1-v2-analysis-001/ directory, any file under
experiments/EXP-ECDLP-6ac801/runs/, or TASK-20260907-80e198's own
sealed_blind_rederivation.json / blind_rederivation.py /
postseal_diagnostic*.py files.

MODEL (from specification.v2.yaml `definitions` and `blind_rederivation.
quantity`, implemented literally rather than approximated by a hash):

  - N points, indices 0..N-1.
  - f: Z_N -> Z_N, a uniformly random function on N points (drawn as an
    explicit random lookup table -- this is the literal HEUR-BLT-1 object,
    "a uniformly random function on N points", not a hash-based stand-in
    for one; this reviewer's own independent design choice).
  - D subset Z_N: an independent Bernoulli(1/W) marking (distinguished
    points), drawn from an RNG stream independent of f's own stream, per
    `blind_rederivation.quantity` ("truncated at an independent
    Bernoulli(1/W) marking").
  - W = sqrt(a * N / T)  (definitions.W)
  - The walk from x applies f repeatedly until it first lands in D; the
    "exact basin" of a DP d is the set of x whose walk first reaches d.
    Exact (not sampled): computed by full enumeration via binary lifting
    (pointer doubling) over the N-point functional graph, with D-points
    made absorbing. K doublings with 2^K > N fully resolves every point's
    fate (absorbed at some DP, with the true walk length; or provably
    stuck forever in a DP-free cycle -- expected count ~0 at these
    parameters and checked explicitly below).
  - exact top-T_sel basin share: sum of the T_sel LARGEST true basin sizes
    (over ALL basins, oracle order) / N.
  - STATIC(T)_r exact coverage: build an r*T-distinct-DP precomputation
    pool via uniformly random restarts (every walk charged, i.e. every
    restart's landing DP is credited even if already known), stopping the
    instant r*T distinct DPs have been credited; weight_d = S_d + 4*W*h_d
    (S_d = summed generating-walk length landing at d, h_d = hit count);
    select the T pool entries with the largest weight_d; STATIC(T)_r exact
    coverage = sum of the TRUE basin sizes of those selected T DPs / N.

Each of the 2 a-values x 5 seeds = 10 cells run here uses its OWN fresh,
independent draw of f and D (this reviewer's own explicit design choice,
disclosed in the report: the frozen `definitions` text specifies the
statistical model per cell, not a code-level batching detail requiring one
f shared across a-values within a seed).

Seeding: every RNG stream is derived via numpy.random.SeedSequence from
(MASTER_SEED, a_num, a_den, seed, stream_tag), so the whole computation is
exactly reproducible from this file and the seed value alone.
"""
import hashlib
import json
import math
import platform
import subprocess
import sys
import time

import numpy as np

MASTER_SEED = 0x54415348_32444239  # "TASK 2db9" in hex-ish, arbitrary fixed constant chosen by this task
STREAM_TAG = {"f_table": 1, "dp_mark": 2, "restart": 3}

N = 1 << 24          # 16777216
T = round(N ** (1.0 / 3.0))   # 256
T_SEL = T // 2        # 128
R = 2
POOL_SIZE = R * T      # 512
SEEDS = [1, 2, 3, 4, 5]
A_VALUES = [("1/8", 1, 8), ("1/4", 1, 4)]   # (label, numerator, denominator)
DOUBLING_ROUNDS = 26   # 2^26 > N = 2^24, safely covers any finite absorption path

RESTART_CHUNK = 20000


def rng_for(a_num, a_den, seed, stream_name):
    ss = np.random.SeedSequence([MASTER_SEED, a_num, a_den, seed, STREAM_TAG[stream_name]])
    return np.random.default_rng(ss)


def compute_cell(a_label, a_num, a_den, seed):
    a = a_num / a_den
    W = math.sqrt(a * N / T)

    f_rng = rng_for(a_num, a_den, seed, "f_table")
    dp_rng = rng_for(a_num, a_den, seed, "dp_mark")
    restart_rng = rng_for(a_num, a_den, seed, "restart")

    # f: literal uniformly random self-map table on Z_N.
    f_table = f_rng.integers(0, N, size=N, dtype=np.int64)

    # D: literal i.i.d. Bernoulli(1/W) marking, independent RNG stream.
    dp_mask = dp_rng.random(N) < (1.0 / W)
    n_dp = int(dp_mask.sum())

    idx_all = np.arange(N, dtype=np.int64)
    nxt = np.where(dp_mask, idx_all, f_table)
    steps = np.where(dp_mask, 0, 1).astype(np.int64)

    # Binary lifting / pointer doubling: after k rounds, nxt[x] = state of
    # x after 2^k applications of the absorbing map, and steps[x] = the
    # TRUE number of real f-steps taken to reach that state (saturates at
    # the true absorption distance because an already-absorbed node p has
    # steps[p] == 0, so composing through it adds nothing further).
    for _ in range(DOUBLING_ROUNDS):
        old_nxt = nxt
        nxt = old_nxt[old_nxt]
        steps = steps + steps[old_nxt]

    absorbed_mask = dp_mask[nxt]
    n_absorbed = int(absorbed_mask.sum())
    n_stuck = N - n_absorbed

    # Exact basin sizes (oracle order), over all DPs.
    basin_counts_full = np.bincount(nxt[absorbed_mask], minlength=N)
    basin_sizes = basin_counts_full[dp_mask]
    assert basin_sizes.shape[0] == n_dp
    total_covered = int(basin_sizes.sum())
    # control (c): non-exceedance sanity
    assert total_covered == n_absorbed
    assert total_covered <= N

    sorted_desc = np.sort(basin_sizes)[::-1]
    exact_top_tsel_sum = int(sorted_desc[:T_SEL].sum())
    exact_top_tsel_share = exact_top_tsel_sum / N
    exact_top_T_sum = int(sorted_desc[:T].sum())
    exact_top_T_share = exact_top_T_sum / N

    # --- STATIC(T)_r pool construction: uniform random restarts, batched,
    # every walk charged, until POOL_SIZE distinct DPs are credited. ---
    S_acc = np.zeros(N, dtype=np.int64)
    h_acc = np.zeros(N, dtype=np.int64)
    credited_mask = np.zeros(N, dtype=bool)
    distinct_count = 0
    total_draws = 0
    total_skipped_stuck = 0

    # Exact, order-respecting construction: pre-generate a chunk of random
    # restarts via vectorized RNG + array lookups (fast), then walk that
    # chunk IN ORDER with a plain Python loop crediting every walk ("every
    # walk charged") and stopping the INSTANT the POOL_SIZE-th distinct DP
    # is newly credited -- so the stopping point is exact, never an
    # overshoot, and every walk actually "performed" before that point is
    # charged exactly once, matching `blind_rederivation`'s pool-
    # construction procedure.
    while distinct_count < POOL_SIZE:
        idx_batch = restart_rng.integers(0, N, size=RESTART_CHUNK)
        valid = absorbed_mask[idx_batch]
        total_skipped_stuck += int((~valid).sum())
        idx_valid = idx_batch[valid]
        term_list = nxt[idx_valid].tolist()
        length_list = steps[idx_valid].tolist()
        for t, L in zip(term_list, length_list):
            total_draws += 1
            S_acc[t] += L
            h_acc[t] += 1
            if not credited_mask[t]:
                credited_mask[t] = True
                distinct_count += 1
                if distinct_count == POOL_SIZE:
                    break

    assert distinct_count == POOL_SIZE
    pool_dp_ids = np.nonzero(credited_mask)[0]
    assert pool_dp_ids.shape[0] == POOL_SIZE

    S_pool = S_acc[pool_dp_ids].astype(np.float64)
    h_pool = h_acc[pool_dp_ids].astype(np.float64)
    weight_pool = S_pool + 4.0 * W * h_pool

    order = np.argsort(-weight_pool, kind="stable")  # descending weight; stable tie-break by original (ascending id) order
    selected_order = order[:T]
    selected_dp_ids = pool_dp_ids[selected_order]

    true_basin_of_selected = basin_counts_full[selected_dp_ids]
    static_t_r_coverage_sum = int(true_basin_of_selected.sum())
    static_t_r_coverage = static_t_r_coverage_sum / N

    margin = exact_top_tsel_share - static_t_r_coverage

    return {
        "a_label": a_label,
        "a_value": a,
        "seed": seed,
        "N": N,
        "T": T,
        "T_sel": T_SEL,
        "r": R,
        "pool_size": POOL_SIZE,
        "W": W,
        "n_distinguished_points": n_dp,
        "n_absorbed": n_absorbed,
        "n_stuck_dp_free_cycle": n_stuck,
        "exact_top_tsel_basin_share": exact_top_tsel_share,
        "exact_top_T_basin_share": exact_top_T_share,
        "static_T_r_exact_coverage": static_t_r_coverage,
        "margin": margin,
        "pass": bool(margin >= 0.0),
        "pool_construction_total_draws": total_draws,
        "pool_construction_skipped_stuck_draws": total_skipped_stuck,
    }


def git_state():
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd="/home/user/crypto-autoresearcher"
        ).decode().strip()
        dirty = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd="/home/user/crypto-autoresearcher",
            capture_output=True, text=True,
        ).stdout.strip()
        return {"commit": commit, "dirty": bool(dirty), "dirty_files": dirty.splitlines()}
    except Exception as e:
        return {"error": str(e)}


def main():
    t0 = time.time()
    results = []
    for a_label, a_num, a_den in A_VALUES:
        for seed in SEEDS:
            cell_t0 = time.time()
            r = compute_cell(a_label, a_num, a_den, seed)
            r["wall_clock_seconds"] = time.time() - cell_t0
            results.append(r)
            print(
                f"a={a_label} seed={seed} W={r['W']:.4f} "
                f"top_Tsel_share={r['exact_top_tsel_basin_share']:.6f} "
                f"static_coverage={r['static_T_r_exact_coverage']:.6f} "
                f"margin={r['margin']:+.6f} pass={r['pass']} "
                f"n_stuck={r['n_stuck_dp_free_cycle']} "
                f"({r['wall_clock_seconds']:.2f}s)",
                file=sys.stderr,
            )

    per_a_summary = {}
    for a_label, _, _ in A_VALUES:
        cells = [r for r in results if r["a_label"] == a_label]
        pass_count = sum(1 for c in cells if c["pass"])
        per_a_summary[a_label] = {
            "pass_count": pass_count,
            "total_seeds": len(cells),
            "verdict": "G3-FEASIBLE" if pass_count >= 4 else "G3-INFEASIBLE",
            "per_seed_margins": [c["margin"] for c in cells],
            "per_seed_pass": [c["pass"] for c in cells],
        }

    manifest = {
        "task_id": "TASK-20260907-2db9aa",
        "purpose": (
            "Freshly SEALED, from-scratch, independent blind re-derivation "
            "of the a=1/8 cell (plus a=1/4 proves-too-much control) under "
            "the now-explicit STATIC(T)_r weight formula "
            "weight_d = S_d + 4*W*h_d, per specification.v2.yaml "
            "definitions and blind_rederivation.v2_rerequirement_a_1_8."
        ),
        "blind_from_respected_at_computation_time": True,
        "paths_read_before_this_computation": [
            "experiments/EXP-ECDLP-6ac801/specification.v2.yaml",
            "ledger/handoffs/TASK-20260907-2db9aa.yaml",
            "agents/validator.md",
            "AGENTS.md",
            "CLAUDE.md",
        ],
        "paths_NOT_read_before_this_computation": [
            "coordination/.../TASK-20260907-80e198/sealed_blind_rederivation.json",
            "coordination/.../TASK-20260907-80e198/blind_rederivation.py",
            "coordination/.../TASK-20260907-80e198/postseal_diagnostic_weight_formula.py",
            "coordination/.../TASK-20260907-80e198/postseal_diagnostic_v2_clean.py",
            "experiments/EXP-ECDLP-612fb1/source_v2/*",
            "experiments/EXP-ECDLP-612fb1/runs/RUN-ECDLP-612fb1-v2-ascan-*/*",
            "experiments/EXP-ECDLP-612fb1/runs/RUN-ECDLP-612fb1-v2-analysis-001/*",
            "experiments/EXP-ECDLP-6ac801/runs/*",
        ],
        "parameters": {
            "N": N, "T": T, "T_sel": T_SEL, "r": R, "pool_size": POOL_SIZE,
            "a_values": [{"label": lbl, "numerator": n, "denominator": d} for lbl, n, d in A_VALUES],
            "seeds": SEEDS,
            "master_seed": MASTER_SEED,
            "doubling_rounds": DOUBLING_ROUNDS,
        },
        "environment": {
            "python": sys.version,
            "numpy": np.__version__,
            "platform": platform.platform(),
        },
        "git_state": git_state(),
        "command": "python3 blind_rederivation.py",
        "wall_clock_seconds_total": time.time() - t0,
        "results": results,
        "per_a_summary": per_a_summary,
    }
    return manifest


if __name__ == "__main__":
    manifest = main()
    out_path = "/home/user/crypto-autoresearcher/coordination/experiments/EXP-ECDLP-6ac801/batches/BATCH-3c7493/tasks/TASK-20260907-2db9aa/sealed_blind_rederivation.json"
    with open(out_path, "w") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
    print(f"Wrote {out_path}", file=sys.stderr)
