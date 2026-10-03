#!/usr/bin/env python3
"""Execute EXP-BINSTD-a3cfee Stages 0-2 (TASK-20261001-3d2adf).

Observations only. No hypothesis status change. No n=131 / exponent / break claim.
"""
from __future__ import annotations

import json
import math
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from runpack import (
    EXP_ID,
    TASK_ID,
    EXP_ROOT,
    dump_text,
    dump_yaml,
    peak_rss_bytes,
    utc_now,
    write_run_package,
)
from toy import (
    MODULI,
    bailey_step,
    binomial_hw_density,
    build_dp_pool,
    build_hw_filter_only_pool,
    build_uniform_pool,
    choose_N,
    choose_cutoff,
    find_generator,
    find_normal_element,
    group_order_estimate,
    hw_normal,
    is_distinguished,
    make_field,
    make_koblitz,
    pairwise_permutation_pvalue,
    replay_walk,
    seed_start_point,
    semaev_m2_yield,
    walk_until_dp,
)

PRIMARY_N = 17
SECONDARY_N = 23
ATTEMPTS = 250
BAND = [0.7, 1.4]

# Pre-minted run IDs (allocate_id --check OK)
RUN_STAGE0_REPLAY = "RUN-BINSTD-09f640"
RUN_STAGE0_FREEZE = "RUN-BINSTD-f17ead"
RUN_S1_DP = "RUN-BINSTD-6a2a20"
RUN_S1_UNI = "RUN-BINSTD-811f0f"
RUN_S1_HW = "RUN-BINSTD-14d961"
RUN_S2_DP = "RUN-BINSTD-ba45f7"
RUN_S2_UNI = "RUN-BINSTD-dcf12a"
RUN_S2_HW = "RUN-BINSTD-9c2e6c"
RUN_S2_CUTOFF = "RUN-BINSTD-b34e25"

SEEDS_S1 = [2026100101, 2026100102, 2026100103, 2026100104, 2026100105]
SEEDS_S2 = [2026100111, 2026100112, 2026100113, 2026100114, 2026100115]


def ratio(a, b):
    if b == 0:
        return float("inf") if a else float("nan")
    return a / b


def in_band(r):
    return BAND[0] <= r <= BAND[1]


def stage0():
    t0 = time.time()
    started = utc_now()
    n = PRIMARY_N
    F = make_field(n)
    curve = make_koblitz(F)
    beta = find_normal_element(F)
    c = choose_cutoff(n)
    N = choose_N(n)
    G = find_generator(curve, random.Random(20261001))
    order = group_order_estimate(curve)

    # Replay vectors: scan seeds until 8 successful DP+replay pairs (toy cycles
    # make some seeds fail before DP; failures are not math evidence).
    replay_rows = []
    scan_seed = 0xA3CFEE01
    tried = 0
    while len(replay_rows) < 8 and tried < 200:
        tried += 1
        seed = scan_seed
        scan_seed += 1
        start = seed_start_point(curve, G, seed)
        if start is None:
            continue
        dp, steps, ok = walk_until_dp(curve, beta, start, c, 1 << 16)
        if not ok or dp is None:
            continue
        dp2, rok = replay_walk(curve, beta, start, c, steps)
        byte_ok = bool(rok and dp2 is not None and dp2[0] == dp[0] and dp2[1] == dp[1])
        if not byte_ok:
            replay_rows.append(
                {
                    "seed": seed,
                    "steps": steps,
                    "pass": False,
                    "reason": "replay_mismatch",
                }
            )
            continue
        replay_rows.append(
            {
                "seed": seed,
                "steps": steps,
                "dp_x": dp[0],
                "dp_y": dp[1],
                "pass": True,
            }
        )
    all_pass = len(replay_rows) >= 8 and all(r.get("pass") for r in replay_rows)
    dens_poly_proxy = binomial_hw_density(n, c)
    expected_uniform = ATTEMPTS * (N * N) / (2.0 * order)

    freeze = {
        "experiment_id": EXP_ID,
        "task_id": TASK_ID,
        "stage": 0,
        "primary_cell": {
            "n": n,
            "modulus": MODULI[n],
            "curve": "Y^2+XY=X^3+1",
            "cutoff_c": c,
            "pool_size_N": N,
            "attempts_per_arm": ATTEMPTS,
            "group_order_sharp": order,
            "normal_element_beta": beta,
            "hw_density_binomial_proxy": dens_poly_proxy,
            "target_density_1_over_sqrt_2n": 1.0 / math.sqrt(2**n),
            "density_match_note": (
                "Toy Bailey walks enter short cycles; cutoff c raised vs pure "
                "1/sqrt matching so DP hits occur before cycle abort. Relative "
                "density is approximate; disclosed confounder (not hidden)."
            ),
            "generator_x": G[0],
            "generator_y": G[1],
        },
        "secondary_cell_plan": {
            "n": SECONDARY_N,
            "cutoff_c": choose_cutoff(SECONDARY_N),
            "pool_size_N": choose_N(SECONDARY_N),
            "attempts_per_arm": ATTEMPTS,
        },
        "frozen_before_stage1": True,
        "no_break_claim": True,
    }
    dump_yaml(EXP_ROOT / "stage0" / "cutoff-and-N-freeze.yaml", freeze)

    preds = {
        "experiment_id": EXP_ID,
        "heuristic": "HEUR-BINSTD-d1f9a5-H1",
        "written_before_stage1": True,
        "band": BAND,
        "predictions": {
            "A_pairwise_ratios_in_band": (
                "yield_DP/uniform, DP/HW_filter_only, HW_filter_only/uniform "
                f"all in {BAND} at m=2 on every tested toy cell"
            ),
            "B_uniform_matches_modeled": (
                f"uniform-arm count ≈ |F|^2/(2*|G|)*attempts = {expected_uniform:.4f} "
                "within sampling error"
            ),
            "C_certificate_pass_rate": 1.0,
            "D_replay_iterations": "reported distribution; no numeric prediction",
        },
        "modeled_baseline_formula": "|F|^m/(m!*N_group) with m=2 => N^2/(2*|G|) per target",
        "claim_tier": "observational",
        "no_n131_transfer": True,
    }
    dump_yaml(EXP_ROOT / "stage0" / "preregistered-predictions.yaml", preds)

    baseline_plan = {
        "experiment_id": EXP_ID,
        "formula": "E[relations] ≈ |F|^m / (m! * N_group) * n_attempts",
        "m": 2,
        "F_is": "pool (size N) used as m=2 factor-base for random targets R",
        "N_group": order,
        "N_pool": N,
        "n_attempts": ATTEMPTS,
        "expected_count_primary": expected_uniform,
        "target_expected_ge_5": expected_uniform >= 5,
        "IMP_sample_power": None if expected_uniform >= 5 else "expected_count < 5",
        "note": "Modeled column; not a theorem. Measured counts reported separately.",
    }
    dump_yaml(EXP_ROOT / "stage0" / "uniform-baseline-plan.yaml", baseline_plan)

    replay_doc = {
        "experiment_id": EXP_ID,
        "task_id": TASK_ID,
        "pass": all_pass,
        "n_vectors": len(replay_rows),
        "cutoff_c": c,
        "n": n,
        "rows": replay_rows,
        "certificate": {
            "kind": "none",
            "verified": False,
            "note": "Stage-0 walk-replay instrument check; no relation/DL claimed.",
        },
    }
    dump_yaml(EXP_ROOT / "stage0" / "replay-check.yaml", replay_doc)

    method = f"""# Methodological note — EXP-BINSTD-a3cfee Stage 0

Task `{TASK_ID}`. Written BEFORE any Stage-1 yield comparison.

## Instrument

- Field: F_2^{n} with irreducible trinomial modulus (n={n} primary).
- Curve: Y^2 + XY = X^3 + 1 (ordinary binary Koblitz analog).
- Normal basis: powers of β={beta} under Frobenius; HW measured in that basis
  (Bailey-style type-2 analog at toy scale — not the ECC2K-130 constants).
- Walk: P ← σ^j(P) ⊕ P with j = ((HW(x)/2) mod 8) + 3.
- DP predicate: HW_normal(x) ≤ c={c}.
- Pool size N={N}; attempts/arm={ATTEMPTS}.
- Group order |E| = {order} (exact trace count).

## Arms

1. **DP_walk**: Bailey walk until DP; byte-identical seed replay required.
2. **uniform**: size-matched random curve points.
3. **HW_filter_only**: rejection sample HW≤c without walk (isolates filter).

## Semaev m=2 yield

For each attempt, sample random R on E; search P,Q in pool with P+Q=R;
certificate.kind=`decomposition` re-verified on a fresh schoolbook Field/Curve.

## Modeled baseline

E[count] ≈ N²/(2·|G|)·attempts = {expected_uniform:.4f} (H1 band {BAND}).

## Claim boundary

No deployed-curve break, no exponent move, no n=131 transfer of toy ratios.
KN-LIT-661e97 n=131 figures are context only.
"""
    dump_text(EXP_ROOT / "stage0" / "methodological-note.md", method)

    finished = utc_now()
    write_run_package(
        RUN_STAGE0_REPLAY,
        stage=0,
        arm="replay_check",
        seed=20261001,
        command="python3 experiments/EXP-BINSTD-a3cfee/implementation/run_stages.py --stage0",
        parameters={"n": n, "cutoff_c": c, "N": N, "beta": beta},
        metrics={"replay_pass": all_pass, "n_vectors": len(replay_rows)},
        valid=all_pass,
        invalid_reason=None if all_pass else "replay_byte_mismatch",
        termination_reason="completed",
        stdout_text=json.dumps(replay_doc, indent=2),
        started_at=started,
        finished_at=finished,
        wall_seconds=time.time() - t0,
        certificate={
            "kind": "none",
            "verified": False,
            "note": "Stage-0 replay instrument; certificate.kind none.",
        },
    )
    write_run_package(
        RUN_STAGE0_FREEZE,
        stage=0,
        arm="cutoff_N_freeze",
        seed=20261001,
        command="python3 experiments/EXP-BINSTD-a3cfee/implementation/run_stages.py --stage0",
        parameters=freeze["primary_cell"],
        metrics={
            "expected_uniform_count": expected_uniform,
            "hw_density_proxy": dens_poly_proxy,
            "group_order": order,
        },
        valid=True,
        invalid_reason=None,
        termination_reason="completed",
        stdout_text=json.dumps(freeze, indent=2),
        started_at=started,
        finished_at=finished,
        wall_seconds=time.time() - t0,
        certificate={
            "kind": "none",
            "verified": False,
            "note": "Stage-0 freeze metrics; certificate.kind none.",
        },
    )
    assert all_pass, "Stage 0 replay failed — abort before Stage 1"
    return freeze


def run_three_arm_cell(n: int, seeds: list[int], run_ids: dict, stage: int, cutoff_override=None):
    F = make_field(n)
    curve = make_koblitz(F)
    beta = find_normal_element(F)
    c = cutoff_override if cutoff_override is not None else choose_cutoff(n)
    N = choose_N(n)
    order = group_order_estimate(curve)
    G = find_generator(curve, random.Random(seeds[0] ^ n))

    # Aggregate across seeds: build one pooled measurement per arm using seed[0]
    # for pool construction and seed[1] for yield attempts (spec seeds as quintile).
    pool_seed = seeds[0]
    yield_seed = seeds[1]
    max_steps = 1 << 18 if n == 17 else 1 << 20

    results = {}
    replay_costs = []

    # DP arm
    t0 = time.time()
    started = utc_now()
    dp_pool, collisions, dp_attempts = build_dp_pool(
        curve, beta, G, c, N, pool_seed, max_steps
    )
    if len(dp_pool) < N:
        raise RuntimeError(f"DP pool incomplete: got {len(dp_pool)}/{N}")
    replay_costs = [e["steps"] for e in dp_pool if e.get("steps")]
    y_dp = semaev_m2_yield(curve, dp_pool, ATTEMPTS, yield_seed, order)
    finished = utc_now()
    write_run_package(
        run_ids["DP_walk"],
        stage=stage,
        arm="DP_walk",
        seed=pool_seed,
        command="python3 experiments/EXP-BINSTD-a3cfee/implementation/run_stages.py",
        parameters={
            "n": n,
            "cutoff_c": c,
            "N": N,
            "attempts": ATTEMPTS,
            "curve_id": f"toy-koblitz-n{n}",
            "group_order": order,
            "pool_collisions": collisions,
            "pool_build_attempts": dp_attempts,
        },
        metrics={
            "relation_count": y_dp["relation_count"],
            "yield_rate": y_dp["yield_rate"],
            "expected_count_modeled": y_dp["expected_count_modeled"],
            "certificate_pass_rate": y_dp["certificate_pass_rate"],
            "replay_iterations_mean": sum(replay_costs) / len(replay_costs),
            "replay_iterations_max": max(replay_costs),
            "walk_collision_rate": collisions / max(dp_attempts, 1),
            "peak_rss_bytes": peak_rss_bytes(),
        },
        valid=y_dp["certificate_fail_count"] == 0 and len(dp_pool) == N,
        invalid_reason=None,
        termination_reason="completed",
        stdout_text=json.dumps({k: v for k, v in y_dp.items() if k != "hit_flags"}, indent=2),
        started_at=started,
        finished_at=finished,
        wall_seconds=time.time() - t0,
        certificate={
            "kind": "decomposition" if y_dp["relation_count"] else "none",
            "verified": y_dp["certificate_pass_rate"] == 1.0,
            "pass_count": y_dp["certificate_pass_count"],
            "fail_count": y_dp["certificate_fail_count"],
            "note": (
                "Each counted Semaev m=2 hit re-checked on fresh schoolbook Curve; "
                "kind=decomposition when relations found else none."
            ),
            "sample": y_dp["hits_sample"],
        },
    )
    results["DP_walk"] = y_dp

    # uniform
    t0 = time.time()
    started = utc_now()
    uni_pool = build_uniform_pool(curve, N, pool_seed + 17)
    y_uni = semaev_m2_yield(curve, uni_pool, ATTEMPTS, yield_seed + 17, order)
    finished = utc_now()
    write_run_package(
        run_ids["uniform"],
        stage=stage,
        arm="uniform",
        seed=pool_seed + 17,
        command="python3 experiments/EXP-BINSTD-a3cfee/implementation/run_stages.py",
        parameters={
            "n": n,
            "N": N,
            "attempts": ATTEMPTS,
            "curve_id": f"toy-koblitz-n{n}",
            "group_order": order,
        },
        metrics={
            "relation_count": y_uni["relation_count"],
            "yield_rate": y_uni["yield_rate"],
            "expected_count_modeled": y_uni["expected_count_modeled"],
            "certificate_pass_rate": y_uni["certificate_pass_rate"],
            "uniform_baseline_relative_error_vs_heuristic": (
                (y_uni["relation_count"] - y_uni["expected_count_modeled"])
                / y_uni["expected_count_modeled"]
                if y_uni["expected_count_modeled"]
                else None
            ),
            "peak_rss_bytes": peak_rss_bytes(),
        },
        valid=y_uni["certificate_fail_count"] == 0,
        invalid_reason=None,
        termination_reason="completed",
        stdout_text=json.dumps({k: v for k, v in y_uni.items() if k != "hit_flags"}, indent=2),
        started_at=started,
        finished_at=finished,
        wall_seconds=time.time() - t0,
        certificate={
            "kind": "decomposition" if y_uni["relation_count"] else "none",
            "verified": y_uni["certificate_pass_rate"] == 1.0,
            "pass_count": y_uni["certificate_pass_count"],
            "fail_count": y_uni["certificate_fail_count"],
            "note": "Uniform-arm m=2 decompositions; independent re-verify.",
            "sample": y_uni["hits_sample"],
        },
    )
    results["uniform"] = y_uni

    # HW filter only
    t0 = time.time()
    started = utc_now()
    hw_pool, hw_att = build_hw_filter_only_pool(curve, beta, c, N, pool_seed + 33)
    if len(hw_pool) < N:
        raise RuntimeError(f"HW pool incomplete: got {len(hw_pool)}/{N} after {hw_att}")
    y_hw = semaev_m2_yield(curve, hw_pool, ATTEMPTS, yield_seed + 33, order)
    finished = utc_now()
    write_run_package(
        run_ids["HW_filter_only"],
        stage=stage,
        arm="HW_filter_only",
        seed=pool_seed + 33,
        command="python3 experiments/EXP-BINSTD-a3cfee/implementation/run_stages.py",
        parameters={
            "n": n,
            "cutoff_c": c,
            "N": N,
            "attempts": ATTEMPTS,
            "curve_id": f"toy-koblitz-n{n}",
            "group_order": order,
            "rejection_attempts": hw_att,
        },
        metrics={
            "relation_count": y_hw["relation_count"],
            "yield_rate": y_hw["yield_rate"],
            "expected_count_modeled": y_hw["expected_count_modeled"],
            "certificate_pass_rate": y_hw["certificate_pass_rate"],
            "peak_rss_bytes": peak_rss_bytes(),
        },
        valid=y_hw["certificate_fail_count"] == 0,
        invalid_reason=None,
        termination_reason="completed",
        stdout_text=json.dumps({k: v for k, v in y_hw.items() if k != "hit_flags"}, indent=2),
        started_at=started,
        finished_at=finished,
        wall_seconds=time.time() - t0,
        certificate={
            "kind": "decomposition" if y_hw["relation_count"] else "none",
            "verified": y_hw["certificate_pass_rate"] == 1.0,
            "pass_count": y_hw["certificate_pass_count"],
            "fail_count": y_hw["certificate_fail_count"],
            "note": "HW-filter-only arm m=2 decompositions; independent re-verify.",
            "sample": y_hw["hits_sample"],
        },
    )
    results["HW_filter_only"] = y_hw

    rng = random.Random(99)
    p_dp_uni, _ = pairwise_permutation_pvalue(
        results["DP_walk"]["hit_flags"], results["uniform"]["hit_flags"], rng
    )
    p_dp_hw, _ = pairwise_permutation_pvalue(
        results["DP_walk"]["hit_flags"], results["HW_filter_only"]["hit_flags"], random.Random(100)
    )
    p_hw_uni, _ = pairwise_permutation_pvalue(
        results["HW_filter_only"]["hit_flags"], results["uniform"]["hit_flags"], random.Random(101)
    )

    counts = {k: results[k]["relation_count"] for k in results}
    rates = {k: results[k]["yield_rate"] for k in results}
    ratios = {
        "DP_over_uniform": ratio(rates["DP_walk"], rates["uniform"]),
        "DP_over_HW_filter_only": ratio(rates["DP_walk"], rates["HW_filter_only"]),
        "HW_filter_only_over_uniform": ratio(rates["HW_filter_only"], rates["uniform"]),
    }
    return {
        "n": n,
        "cutoff_c": c,
        "N": N,
        "group_order": order,
        "attempts": ATTEMPTS,
        "counts": counts,
        "rates": rates,
        "ratios": ratios,
        "ratios_in_band": {k: in_band(v) for k, v in ratios.items()},
        "p_values": {
            "DP_vs_uniform": p_dp_uni,
            "DP_vs_HW_filter_only": p_dp_hw,
            "HW_filter_only_vs_uniform": p_hw_uni,
        },
        "certificate_pass_rate": {
            k: results[k]["certificate_pass_rate"] for k in results
        },
        "uniform_expected": results["uniform"]["expected_count_modeled"],
        "uniform_relative_error": (
            (counts["uniform"] - results["uniform"]["expected_count_modeled"])
            / results["uniform"]["expected_count_modeled"]
            if results["uniform"]["expected_count_modeled"]
            else None
        ),
        "replay_cost": {
            "mean": sum(replay_costs) / len(replay_costs) if replay_costs else None,
            "max": max(replay_costs) if replay_costs else None,
            "min": min(replay_costs) if replay_costs else None,
            "n": len(replay_costs),
            "histogram_deciles_raw_sample": sorted(replay_costs)[:: max(len(replay_costs) // 10, 1)],
        },
        "run_ids": run_ids,
    }


def stage1(freeze):
    cell = run_three_arm_cell(
        PRIMARY_N,
        SEEDS_S1,
        {"DP_walk": RUN_S1_DP, "uniform": RUN_S1_UNI, "HW_filter_only": RUN_S1_HW},
        stage=1,
    )
    dump_yaml(
        EXP_ROOT / "stage1" / "three-arm-yield-summary.yaml",
        {
            "experiment_id": EXP_ID,
            "task_id": TASK_ID,
            "stage": 1,
            "cell": cell,
            "no_break_claim": True,
            "no_n131_transfer": True,
        },
    )
    dump_yaml(
        EXP_ROOT / "stage1" / "pairwise-ratios.yaml",
        {
            "experiment_id": EXP_ID,
            "band": BAND,
            "ratios": cell["ratios"],
            "in_band": cell["ratios_in_band"],
            "p_values": cell["p_values"],
            "decision_hint_DO": (
                "DO-1"
                if all(cell["ratios_in_band"].values())
                else "single_cell_out_of_band_await_stage2"
            ),
        },
    )
    dump_yaml(
        EXP_ROOT / "stage1" / "replay-cost-summary.yaml",
        {
            "experiment_id": EXP_ID,
            "arm": "DP_walk",
            "replay_cost": cell["replay_cost"],
            "note": "Measured toy-scale iterations-to-DP; not the n=131 2^25.27 figure.",
        },
    )
    return cell


def stage2(stage1_cell):
    # Second cell at n=23
    cell2 = run_three_arm_cell(
        SECONDARY_N,
        SEEDS_S2,
        {"DP_walk": RUN_S2_DP, "uniform": RUN_S2_UNI, "HW_filter_only": RUN_S2_HW},
        stage=2,
    )
    # Optional second cutoff at primary n (density sweep control)
    t0 = time.time()
    started = utc_now()
    n = PRIMARY_N
    F = make_field(n)
    curve = make_koblitz(F)
    beta = find_normal_element(F)
    c2 = choose_cutoff(n) + 1  # one step higher density
    N = choose_N(n)
    order = group_order_estimate(curve)
    G = find_generator(curve, random.Random(SEEDS_S1[0] ^ 0xC0FF))
    dp_pool, coll, att = build_dp_pool(curve, beta, G, c2, N, SEEDS_S1[2], 1 << 18)
    y = semaev_m2_yield(curve, dp_pool, ATTEMPTS, SEEDS_S1[3], order)
    finished = utc_now()
    write_run_package(
        RUN_S2_CUTOFF,
        stage=2,
        arm="DP_walk_second_cutoff",
        seed=SEEDS_S1[2],
        command="python3 experiments/EXP-BINSTD-a3cfee/implementation/run_stages.py",
        parameters={"n": n, "cutoff_c": c2, "N": N, "attempts": ATTEMPTS, "group_order": order},
        metrics={
            "relation_count": y["relation_count"],
            "yield_rate": y["yield_rate"],
            "certificate_pass_rate": y["certificate_pass_rate"],
        },
        valid=y["certificate_fail_count"] == 0 and len(dp_pool) == N,
        invalid_reason=None,
        termination_reason="completed",
        stdout_text=json.dumps({k: v for k, v in y.items() if k != "hit_flags"}, indent=2),
        started_at=started,
        finished_at=finished,
        wall_seconds=time.time() - t0,
        certificate={
            "kind": "decomposition" if y["relation_count"] else "none",
            "verified": y["certificate_pass_rate"] == 1.0,
            "note": "Stage-2 second-cutoff DP arm; density-scaling control.",
            "sample": y["hits_sample"],
        },
    )
    both_in_band = all(stage1_cell["ratios_in_band"].values()) and all(
        cell2["ratios_in_band"].values()
    )
    dump_yaml(
        EXP_ROOT / "stage2" / "replication-summary.yaml",
        {
            "experiment_id": EXP_ID,
            "task_id": TASK_ID,
            "stage": 2,
            "primary_cell_n17": {
                "ratios": stage1_cell["ratios"],
                "in_band": stage1_cell["ratios_in_band"],
            },
            "secondary_cell_n23": {
                "ratios": cell2["ratios"],
                "in_band": cell2["ratios_in_band"],
                "counts": cell2["counts"],
            },
            "second_cutoff": {
                "n": n,
                "cutoff_c": c2,
                "relation_count_DP": y["relation_count"],
                "yield_rate": y["yield_rate"],
                "run_id": RUN_S2_CUTOFF,
            },
            "m3_status": "skipped_budget_after_stage2_replication_cell",
            "decision_orientation": "DO-1" if both_in_band else "DO-2_or_noise_see_ratios",
            "H_alt_requires_two_cell_agreement": True,
            "no_break_claim": True,
            "no_n131_transfer": True,
        },
    )
    return cell2


def main():
    print("=== Stage 0 ===", flush=True)
    freeze = stage0()
    print("Stage 0 complete; replay pass; N/c frozen.", flush=True)
    print("=== Stage 1 ===", flush=True)
    s1 = stage1(freeze)
    print("Stage 1 ratios:", s1["ratios"], flush=True)
    print("=== Stage 2 ===", flush=True)
    s2 = stage2(s1)
    print("Stage 2 ratios:", s2["ratios"], flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
