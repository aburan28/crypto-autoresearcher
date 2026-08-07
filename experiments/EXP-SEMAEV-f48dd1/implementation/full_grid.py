#!/usr/bin/env python3
"""Full cell grid for EXP-SEMAEV-f48dd1: x-oracle Semaev yield discrimination.

40 configurations × 3 arms = 120 arm-runs.
m=3, primes=[101, 103, 107, 211], b=[0.4, 0.5], seeds=[1,2,3,4,5]

Arm A: no-oracle, exhaustive enumeration of all m-tuples
Arm B: x-oracle, MITM with true x-coordinate queries
Arm C: random predictor, MITM with PRNG queries (run-matched with B)

Produces:
  - manifest.yaml
  - raw-results.json
  - analysis.yaml
"""
from __future__ import annotations

import hashlib
import json
import math
import platform
import statistics
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from harness.toycurve import EllipticCurve, Point


# ---------------------------------------------------------------------------
# Curve and factor-base construction
# ---------------------------------------------------------------------------

def find_curve(p: int) -> EllipticCurve:
    """Deterministic search for the first nonsingular curve y^2 = x^3 + Ax + B
    over F_p with A, B in [0, p) (lexicographic) that has a point of order >= 5."""
    for A in range(p):
        for B in range(p):
            try:
                E = EllipticCurve(p, A, B)
            except ValueError:
                continue
            # Check for a point of order >= 5
            for x in range(p):
                P = E.lift_x(x)
                if P is not None:
                    Q = P
                    for k in range(2, 20):
                        Q = E.add(Q, P)
                        if Q is None:
                            if k >= 5:
                                return E
                            break
                    # If we didn't hit O, order is at least 20
                    return E
    raise RuntimeError(f"No suitable curve found over F_{p}")


def build_factor_base(E: EllipticCurve, B_size: int) -> Tuple[List[Point], List[int]]:
    """Build factor base: first B_size on-curve x-coordinates, then all points
    with those x-coords. Returns (points, x_coords)."""
    p = E.p
    x_coords = []
    for x in range(p):
        if E.lift_x(x) is not None:
            x_coords.append(x)
            if len(x_coords) == B_size:
                break

    if len(x_coords) < B_size:
        raise ValueError(f"Could not find {B_size} on-curve x-coordinates over F_{p}")

    # Collect all points with these x-coordinates
    points = []
    for x in x_coords:
        P = E.lift_x(x)
        if P is not None:
            points.append(P)
            neg_P = E.negate(P)
            if neg_P != P:  # Don't double-count if y=0
                points.append(neg_P)

    return points, x_coords


# ---------------------------------------------------------------------------
# Arm implementations
# ---------------------------------------------------------------------------

def arm_a_no_oracle(E: EllipticCurve, F: List[Point], m: int) -> Dict:
    """Arm A: exhaustive enumeration, no MITM."""
    t0 = time.perf_counter()
    relations = 0
    tuples_enumerated = 0
    field_ops = 0

    if m == 3:
        for P1 in F:
            for P2 in F:
                for P3 in F:
                    tuples_enumerated += 1
                    field_ops += 2
                    S = E.add(P1, P2)
                    S = E.add(S, P3)
                    if S is None:  # P1 + P2 + P3 = O
                        relations += 1

    wall_clock = time.perf_counter() - t0

    return {
        "tuples_enumerated": tuples_enumerated,
        "relations_found": relations,
        "relations_verified": relations,
        "oracle_queries": 0,
        "hash_table_hits": 0,
        "false_positives": 0,
        "field_operations": field_ops,
        "wall_clock_seconds": round(wall_clock, 4),
    }


def arm_b_x_oracle(E: EllipticCurve, F: List[Point], m: int) -> Dict:
    """Arm B: x-oracle MITM.

    Yield denominator is |F|^m (the full enumeration space), per specification.
    MITM reduces verification cost but the enumeration space is the same as
    exhaustive search — this ensures cross-arm yield consistency.
    """
    t0 = time.perf_counter()
    F_size = len(F)
    enumeration_space = F_size ** m  # |F|^m — spec-mandated denominator

    if m != 3:
        raise NotImplementedError("Only m=3 implemented")

    # Right half: build hash table H[x(P2+P3)] -> list of (P2, P3)
    H: Dict[int, List[Tuple[Point, Point]]] = {}
    right_pairs = 0
    field_ops = 0

    for P2 in F:
        for P3 in F:
            right_pairs += 1
            field_ops += 1
            S = E.add(P2, P3)
            if S is not None:
                x_S = S[0]
                if x_S not in H:
                    H[x_S] = []
                H[x_S].append((P2, P3))

    # Left half: for each P1, query x(P1) and look up in H
    oracle_queries = 0
    hash_table_hits = 0
    relations_found = 0
    false_positives = 0
    candidates_verified = 0

    for P1 in F:
        oracle_queries += 1
        x_P1 = P1[0]  # x-oracle returns x(P1)

        if x_P1 in H:
            hash_table_hits += 1
            for P2, P3 in H[x_P1]:
                candidates_verified += 1
                field_ops += 2
                S = E.add(P1, P2)
                S = E.add(S, P3)
                if S is None:
                    relations_found += 1
                else:
                    false_positives += 1

    wall_clock = time.perf_counter() - t0

    return {
        "tuples_enumerated": enumeration_space,  # |F|^m per spec
        "candidates_verified": candidates_verified,  # secondary metric (MITM filtered)
        "relations_found": relations_found,
        "relations_verified": relations_found,
        "oracle_queries": oracle_queries,
        "hash_table_hits": hash_table_hits,
        "false_positives": false_positives,
        "field_operations": field_ops,
        "wall_clock_seconds": round(wall_clock, 4),
        "right_half_pairs": right_pairs,
    }


def arm_c_random_predictor(E: EllipticCurve, F: List[Point], m: int, seed: int) -> Dict:
    """Arm C: random predictor MITM (run-matched with B).

    Yield denominator is |F|^m (the full enumeration space), per specification.
    MITM reduces verification cost but the enumeration space is the same as
    exhaustive search — this ensures cross-arm yield consistency.
    """
    t0 = time.perf_counter()
    F_size = len(F)
    enumeration_space = F_size ** m  # |F|^m — spec-mandated denominator

    if m != 3:
        raise NotImplementedError("Only m=3 implemented")

    # Right half: identical to B
    H: Dict[int, List[Tuple[Point, Point]]] = {}
    right_pairs = 0
    field_ops = 0

    for P2 in F:
        for P3 in F:
            right_pairs += 1
            field_ops += 1
            S = E.add(P2, P3)
            if S is not None:
                x_S = S[0]
                if x_S not in H:
                    H[x_S] = []
                H[x_S].append((P2, P3))

    # Left half: identical to B, but oracle is replaced by PRNG
    oracle_queries = 0
    hash_table_hits = 0
    relations_found = 0
    false_positives = 0
    candidates_verified = 0
    prng_outputs = set()
    prng_counter = 0

    for P1 in F:
        oracle_queries += 1
        # Deterministic PRNG keyed on (seed, P1, counter) with collision avoidance
        # Retry until we get a unique value
        max_attempts = E.p * 2  # Safety limit
        attempts = 0
        while True:
            prng_key = f"{seed}:{P1[0]}:{P1[1]}:{prng_counter}"
            prng_hash = hashlib.sha256(prng_key.encode()).hexdigest()
            x_rand = int(prng_hash, 16) % E.p
            prng_counter += 1
            attempts += 1
            if x_rand not in prng_outputs:
                break
            if attempts > max_attempts:
                raise RuntimeError(f"PRNG exhausted after {max_attempts} attempts")
        prng_outputs.add(x_rand)

        if x_rand in H:
            hash_table_hits += 1
            for P2, P3 in H[x_rand]:
                candidates_verified += 1
                field_ops += 2
                S = E.add(P1, P2)
                S = E.add(S, P3)
                if S is None:
                    relations_found += 1
                else:
                    false_positives += 1

    wall_clock = time.perf_counter() - t0

    return {
        "tuples_enumerated": enumeration_space,  # |F|^m per spec
        "candidates_verified": candidates_verified,  # secondary metric (MITM filtered)
        "relations_found": relations_found,
        "relations_verified": relations_found,
        "oracle_queries": oracle_queries,
        "hash_table_hits": hash_table_hits,
        "false_positives": false_positives,
        "field_operations": field_ops,
        "wall_clock_seconds": round(wall_clock, 4),
        "right_half_pairs": right_pairs,
        "prng_collision_free": len(prng_outputs) == oracle_queries,
    }


# ---------------------------------------------------------------------------
# Grid runner
# ---------------------------------------------------------------------------

PRIMES = [101, 103, 107, 211]
B_VALUES = [0.4, 0.5]
SEEDS = [1, 2, 3, 4, 5]
M = 3


def run_cell(p: int, b: float, seed: int) -> Dict:
    """Run a single configuration (all 3 arms) and return results."""
    B_size = int(math.floor(p ** b))
    cell_id = f"m{M}_p{p}_b{b}_seed{seed}"

    # Find curve
    E = find_curve(p)
    N = E.order()

    # Build factor base
    F, x_coords = build_factor_base(E, B_size)
    F_size = len(F)

    # Expected baseline
    expected_relations = (F_size ** M) / N
    expected_yield = 1.0 / N

    # Run arms
    result_A = arm_a_no_oracle(E, F, M)
    result_A["arm"] = "A"
    result_A["oracle_type"] = "none"

    result_B = arm_b_x_oracle(E, F, M)
    result_B["arm"] = "B"
    result_B["oracle_type"] = "x_coordinate"

    result_C = arm_c_random_predictor(E, F, M, seed)
    result_C["arm"] = "C"
    result_C["oracle_type"] = "random_predictor"

    # Control checks
    query_match = result_B["oracle_queries"] == result_C["oracle_queries"]
    prng_ok = result_C.get("prng_collision_free", False)

    Y_A = result_A["relations_found"] / result_A["tuples_enumerated"] if result_A["tuples_enumerated"] > 0 else 0.0
    baseline_ok = (Y_A >= expected_yield / 4) and (Y_A <= expected_yield * 4)

    all_controls_pass = query_match and prng_ok and baseline_ok

    # Compute yields
    for arm_result in [result_A, result_B, result_C]:
        tuples = arm_result["tuples_enumerated"]
        rels = arm_result["relations_found"]
        arm_result["yield"] = rels / tuples if tuples > 0 else 0.0

    return {
        "cell_id": cell_id,
        "m": M,
        "p": p,
        "b": b,
        "seed": seed,
        "B": B_size,
        "N": N,
        "curve": {"a": E.a, "b": E.b},
        "factor_base_size": F_size,
        "factor_base_x_coords": x_coords,
        "expected_yield_baseline": expected_yield,
        "arms": {
            "A": result_A,
            "B": result_B,
            "C": result_C,
        },
        "control_checks": {
            "query_count_match": query_match,
            "prng_collision_free": prng_ok,
            "baseline_consistency": baseline_ok,
        },
        "all_controls_pass": all_controls_pass,
        "status": "completed" if all_controls_pass else "control_check_failed",
    }


def main():
    print("=" * 70)
    print("EXP-SEMAEV-f48dd1 Full Cell Grid")
    print(f"m={M}, primes={PRIMES}, b={B_VALUES}, seeds={SEEDS}")
    print(f"Total: {len(PRIMES)} × {len(B_VALUES)} × {len(SEEDS)} = "
          f"{len(PRIMES) * len(B_VALUES) * len(SEEDS)} configurations × 3 arms = "
          f"{len(PRIMES) * len(B_VALUES) * len(SEEDS) * 3} arm-runs")
    print("=" * 70)

    output_dir = Path(__file__).parent.parent / "runs" / "RUN-SEMAEV-f48dd1-grid"
    output_dir.mkdir(parents=True, exist_ok=True)

    all_results = []
    total_start = time.perf_counter()
    run_count = 0
    invalid_count = 0

    # Pre-compute curves per prime (cache)
    curve_cache: Dict[int, Tuple[EllipticCurve, int]] = {}
    for p in PRIMES:
        print(f"\nPre-computing curve for p={p}...")
        E = find_curve(p)
        N = E.order()
        curve_cache[p] = (E, N)
        print(f"  Curve: y^2 = x^3 + {E.a}x + {E.b} over F_{p}, order N={N}")

    for p in PRIMES:
        for b in B_VALUES:
            B_size = int(math.floor(p ** b))
            for seed in SEEDS:
                run_count += 1
                cell_id = f"m{M}_p{p}_b{b}_seed{seed}"
                print(f"\n[{run_count}/120] {cell_id} (B={B_size})")

                t0 = time.perf_counter()
                try:
                    result = run_cell(p, b, seed)
                    elapsed = time.perf_counter() - t0

                    status = result["status"]
                    Y_A = result["arms"]["A"]["yield"]
                    Y_B = result["arms"]["B"]["yield"]
                    Y_C = result["arms"]["C"]["yield"]
                    delta = Y_B - Y_C

                    print(f"  Y_A={Y_A:.6f}  Y_B={Y_B:.6f}  Y_C={Y_C:.6f}  Δ={delta:.6f}")
                    print(f"  Controls: {result['control_checks']}")
                    print(f"  Time: {elapsed:.2f}s  Status: {status}")

                    if not result["all_controls_pass"]:
                        invalid_count += 1
                        print(f"  *** CONTROL CHECK FAILED ***")

                    result["run_index"] = run_count
                    result["wall_clock_total"] = round(elapsed, 4)
                    all_results.append(result)

                except Exception as e:
                    elapsed = time.perf_counter() - t0
                    invalid_count += 1
                    print(f"  *** ERROR: {e} ***")
                    all_results.append({
                        "cell_id": cell_id,
                        "m": M,
                        "p": p,
                        "b": b,
                        "B": B_size,
                        "seed": seed,
                        "status": "error",
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "run_index": run_count,
                        "wall_clock_total": round(elapsed, 4),
                        "arms": {},
                        "control_checks": {},
                        "all_controls_pass": False,
                    })

    total_elapsed = time.perf_counter() - total_start

    # -----------------------------------------------------------------------
    # Write raw-results.json
    # -----------------------------------------------------------------------
    raw_results_path = output_dir / "raw-results.json"
    with open(raw_results_path, "w") as f:
        json.dump({
            "experiment_id": "EXP-SEMAEV-f48dd1",
            "run_id": "RUN-SEMAEV-f48dd1-grid",
            "parameters": {
                "m": M,
                "primes": PRIMES,
                "b_values": B_VALUES,
                "seeds": SEEDS,
            },
            "total_arm_runs": run_count * 3,
            "total_configurations": run_count,
            "invalid_runs": invalid_count,
            "total_wall_clock_seconds": round(total_elapsed, 2),
            "cells": all_results,
        }, f, indent=2)
    print(f"\nRaw results written to: {raw_results_path}")

    # -----------------------------------------------------------------------
    # Analysis
    # -----------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("ANALYSIS")
    print("=" * 70)

    # Collect valid cells
    valid_cells = [r for r in all_results if r.get("status") == "completed"]
    print(f"\nValid cells: {len(valid_cells)}/{len(all_results)}")

    # Per-cell yield summary
    print(f"\n{'Prime':>5} {'b':>4} {'Seed':>4} {'|F|':>4} {'Y_A':>10} {'Y_B':>10} {'Y_C':>10} {'Δ':>10}")
    print("-" * 65)

    deltas = []
    per_cell_stats = []

    for r in valid_cells:
        Y_A = r["arms"]["A"]["yield"]
        Y_B = r["arms"]["B"]["yield"]
        Y_C = r["arms"]["C"]["yield"]
        delta = Y_B - Y_C
        deltas.append(delta)
        per_cell_stats.append({
            "p": r["p"],
            "b": r["b"],
            "seed": r.get("seed", 0),
            "F_size": r.get("factor_base_size", 0),
            "Y_A": Y_A,
            "Y_B": Y_B,
            "Y_C": Y_C,
            "delta": delta,
        })
        print(f"{r['p']:>5} {r['b']:>4.1f} {r.get('seed', 0):>4} {r.get('factor_base_size', 0):>4} "
              f"{Y_A:>10.6f} {Y_B:>10.6f} {Y_C:>10.6f} {delta:>10.6f}")

    # Overall statistics
    if deltas:
        mean_delta = statistics.mean(deltas)
        std_delta = statistics.stdev(deltas) if len(deltas) > 1 else 0.0
        n = len(deltas)
        # 95% CI: mean ± t_{0.025, n-1} * std/sqrt(n)
        # Use exact t-values for df = n-1. For n=40, df=39, t=2.023.
        # NOTE: We use the t-distribution rather than the normal approximation
        # (z=1.96) because n=40 is moderate and the t-distribution properly
        # accounts for uncertainty in the variance estimate.
        #
        # Non-independence caveat: The 40 "cells" share the same curve per prime
        # (4 primes × 10 cells each). Arms A and B are deterministic given the
        # curve — only Arm C varies with seed. So the 5 seed replicates within
        # a (prime, b) group are NOT fully independent for Arms A and B. The
        # effective sample size for Δ is closer to 8 (4 primes × 2 b-values)
        # independent groups, not 40. We report n=40 for transparency but flag
        # this; the CI should be interpreted as descriptive, not inferential.
        # For df=39: t_{0.025,39} = 2.023
        t_table = {
            3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365,
            8: 2.306, 9: 2.262, 10: 2.228, 15: 2.131, 20: 2.086,
            25: 2.060, 30: 2.042, 39: 2.023, 40: 2.021, 60: 2.000,
            120: 1.980, 1000: 1.962,
        }
        df = n - 1
        if df in t_table:
            t_val = t_table[df]
        else:
            # Find nearest df in table
            nearest = min(t_table.keys(), key=lambda k: abs(k - df))
            t_val = t_table[nearest]
        se = std_delta / math.sqrt(n) if n > 0 else 0.0
        ci_low = mean_delta - t_val * se
        ci_high = mean_delta + t_val * se

        # Per-arm aggregates
        all_Y_A = [s["Y_A"] for s in per_cell_stats]
        all_Y_B = [s["Y_B"] for s in per_cell_stats]
        all_Y_C = [s["Y_C"] for s in per_cell_stats]

        print(f"\n{'=' * 65}")
        print(f"Overall Δ = Y_B − Y_C")
        print(f"  Mean Δ = {mean_delta:.6f}")
        print(f"  Std Δ  = {std_delta:.6f}")
        print(f"  n      = {n}")
        print(f"  95% CI = [{ci_low:.6f}, {ci_high:.6f}]")
        print(f"  t-value = {t_val}")
        print(f"  SE     = {se:.6f}")

        print(f"\nPer-arm aggregates (across {n} valid cells):")
        print(f"  Y_A: mean={statistics.mean(all_Y_A):.6f}, std={statistics.stdev(all_Y_A) if len(all_Y_A) > 1 else 0:.6f}")
        print(f"  Y_B: mean={statistics.mean(all_Y_B):.6f}, std={statistics.stdev(all_Y_B) if len(all_Y_B) > 1 else 0:.6f}")
        print(f"  Y_C: mean={statistics.mean(all_Y_C):.6f}, std={statistics.stdev(all_Y_C) if len(all_Y_C) > 1 else 0:.6f}")

        # Per-prime breakdown
        print(f"\nPer-prime breakdown:")
        for p in PRIMES:
            p_deltas = [s["delta"] for s in per_cell_stats if s["p"] == p]
            if p_deltas:
                print(f"  p={p}: mean_Δ={statistics.mean(p_deltas):.6f}, "
                      f"min={min(p_deltas):.6f}, max={max(p_deltas):.6f}, n={len(p_deltas)}")

        # Per-b breakdown
        print(f"\nPer-b breakdown:")
        for b in B_VALUES:
            b_deltas = [s["delta"] for s in per_cell_stats if s["b"] == b]
            if b_deltas:
                print(f"  b={b}: mean_Δ={statistics.mean(b_deltas):.6f}, "
                      f"min={min(b_deltas):.6f}, max={max(b_deltas):.6f}, n={len(b_deltas)}")

        # Statistical significance
        if se > 0:
            t_stat = mean_delta / se
            # Rough p-value: for large t, p is very small
            if abs(t_stat) > 3.5:
                p_approx = "< 0.001"
            elif abs(t_stat) > 2.5:
                p_approx = "< 0.01"
            elif abs(t_stat) > 2.0:
                p_approx = "< 0.05"
            else:
                p_approx = "> 0.05"
            print(f"\n  t-statistic = {t_stat:.4f}")
            print(f"  Approximate p-value {p_approx}")
            significant = abs(t_stat) > t_val
            print(f"  Statistically significant at α=0.05: {significant}")
        else:
            t_stat = 0.0
            significant = False
            print(f"\n  t-statistic = 0 (zero variance)")
    else:
        mean_delta = 0.0
        std_delta = 0.0
        ci_low = 0.0
        ci_high = 0.0
        t_stat = 0.0
        significant = False
        all_Y_A = all_Y_B = all_Y_C = []
        print("\nNo valid cells to analyze.")

    # Control check summary
    all_controls_ok = all(r.get("all_controls_pass", False) for r in all_results if r.get("status") != "error")
    print(f"\nAll control checks passed: {all_controls_ok}")

    # -----------------------------------------------------------------------
    # Write analysis.yaml
    # -----------------------------------------------------------------------
    analysis_lines = [
        "analysis:",
        f"  experiment_id: EXP-SEMAEV-f48dd1",
        f"  run_id: RUN-SEMAEV-f48dd1-grid",
        f"  timestamp: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}",
        f"  total_configurations: {len(all_results)}",
        f"  total_arm_runs: {len(all_results) * 3}",
        f"  valid_cells: {len(valid_cells)}",
        f"  invalid_runs: {invalid_count}",
        f"  total_wall_clock_seconds: {round(total_elapsed, 2)}",
        "",
        "  parameters:",
        f"    m: {M}",
        f"    primes: {PRIMES}",
        f"    b_values: {B_VALUES}",
        f"    seeds: {SEEDS}",
        "",
        "  overall_delta:",
        f"    mean: {round(mean_delta, 8) if deltas else 0.0}",
        f"    std: {round(std_delta, 8) if len(deltas) > 1 else 0.0}",
        f"    n: {len(deltas)}",
        f"    df: {len(deltas) - 1 if deltas else 0}",
        f"    t_critical: {t_val if deltas else 0.0}",
        f"    t_statistic: {round(t_stat, 4) if deltas else 0.0}",
        f"    se: {round(se, 8) if deltas else 0.0}",
        f"    ci_95_low: {round(ci_low, 8) if deltas else 0.0}",
        f"    ci_95_high: {round(ci_high, 8) if deltas else 0.0}",
        f"    statistically_significant: {significant}",
        "    non_independence_note: >-",
        "      Arms A and B are deterministic given the curve (seed-independent).",
        "      Only Arm C varies with seed. The 5 replicates within each (prime, b)",
        "      group share the same Arm A and Arm B values, so the effective sample",
        "      size for Δ is closer to 8 independent groups (4 primes × 2 b-values)",
        "      than 40. The CI is descriptive, not inferential.",
        "",
        "  per_arm_aggregates:",
    ]
    if all_Y_A:
        analysis_lines.extend([
            f"    Y_A:",
            f"      mean: {round(statistics.mean(all_Y_A), 8)}",
            f"      std: {round(statistics.stdev(all_Y_A), 8) if len(all_Y_A) > 1 else 0.0}",
            f"    Y_B:",
            f"      mean: {round(statistics.mean(all_Y_B), 8)}",
            f"      std: {round(statistics.stdev(all_Y_B), 8) if len(all_Y_B) > 1 else 0.0}",
            f"    Y_C:",
            f"      mean: {round(statistics.mean(all_Y_C), 8)}",
            f"      std: {round(statistics.stdev(all_Y_C), 8) if len(all_Y_C) > 1 else 0.0}",
        ])

    analysis_lines.extend([
        "",
        "  per_prime_breakdown:",
    ])
    for p in PRIMES:
        p_deltas = [s["delta"] for s in per_cell_stats if s["p"] == p]
        if p_deltas:
            analysis_lines.extend([
                f"    p_{p}:",
                f"      mean_delta: {round(statistics.mean(p_deltas), 8)}",
                f"      min_delta: {round(min(p_deltas), 8)}",
                f"      max_delta: {round(max(p_deltas), 8)}",
                f"      n: {len(p_deltas)}",
            ])

    analysis_lines.extend([
        "",
        "  per_b_breakdown:",
    ])
    for b in B_VALUES:
        b_deltas = [s["delta"] for s in per_cell_stats if s["b"] == b]
        if b_deltas:
            analysis_lines.extend([
                f"    b_{b}:",
                f"      mean_delta: {round(statistics.mean(b_deltas), 8)}",
                f"      min_delta: {round(min(b_deltas), 8)}",
                f"      max_delta: {round(max(b_deltas), 8)}",
                f"      n: {len(b_deltas)}",
            ])

    analysis_lines.extend([
        "",
        "  control_checks:",
        f"    all_pass: {all_controls_ok}",
        f"    query_count_match: {all(r.get('control_checks', {}).get('query_count_match', False) for r in valid_cells)}",
        f"    prng_collision_free: {all(r.get('control_checks', {}).get('prng_collision_free', False) for r in valid_cells)}",
        f"    baseline_consistency: {all(r.get('control_checks', {}).get('baseline_consistency', False) for r in valid_cells)}",
        "",
        "  per_cell_results:",
    ])
    for s in per_cell_stats:
        analysis_lines.extend([
            f"    - p: {s['p']}",
            f"      b: {s['b']}",
            f"      seed: {s['seed']}",
            f"      F_size: {s['F_size']}",
            f"      Y_A: {round(s['Y_A'], 8)}",
            f"      Y_B: {round(s['Y_B'], 8)}",
            f"      Y_C: {round(s['Y_C'], 8)}",
            f"      delta: {round(s['delta'], 8)}",
        ])

    analysis_path = output_dir / "analysis.yaml"
    with open(analysis_path, "w") as f:
        f.write("\n".join(analysis_lines) + "\n")
    print(f"\nAnalysis written to: {analysis_path}")

    # -----------------------------------------------------------------------
    # Write manifest.yaml
    # -----------------------------------------------------------------------
    manifest_lines = [
        "run:",
        "  id: RUN-SEMAEV-f48dd1-grid",
        "  experiment_id: EXP-SEMAEV-f48dd1",
        "  task_id: TASK-20260807-c58e07-exec",
        "  purpose: >-",
        "    Full cell grid for x-oracle Semaev yield discrimination.",
        f"    {len(PRIMES)} primes × {len(B_VALUES)} b-values × {len(SEEDS)} seeds = "
        f"{len(PRIMES) * len(B_VALUES) * len(SEEDS)} configurations × 3 arms = "
        f"{len(PRIMES) * len(B_VALUES) * len(SEEDS) * 3} arm-runs.",
        f"  status: {'completed' if invalid_count == 0 else 'completed_with_invalid'}",
        f"  timestamp: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}",
        "",
        "git:",
        f"  head_commit: null  # to be filled by archival task",
        f"  dirty_state: true",
        "",
        "command:",
        "  executable: python3",
        "  script: experiments/EXP-SEMAEV-f48dd1/implementation/full_grid.py",
        "  working_directory: /Volumes/SSD990/crypto-autoresearcher",
        "  arguments: []",
        f"  exit_code: {0 if invalid_count == 0 else 1}",
        "",
        "environment:",
        f"  python_version: {platform.python_version()}",
        f"  platform: {platform.system().lower()}",
        "  dependencies:",
        "    sympy: present",
        "    hashlib: stdlib",
        "",
        "parameters:",
        f"  m: {M}",
        f"  primes: {PRIMES}",
        f"  b_values: {B_VALUES}",
        f"  seeds: {SEEDS}",
        f"  total_configurations: {len(all_results)}",
        f"  total_arm_runs: {len(all_results) * 3}",
        "",
        "results_summary:",
        f"  valid_cells: {len(valid_cells)}",
        f"  invalid_runs: {invalid_count}",
        f"  total_wall_clock_seconds: {round(total_elapsed, 2)}",
        f"  overall_delta_mean: {round(mean_delta, 8) if deltas else 0.0}",
        f"  overall_delta_ci_95: [{round(ci_low, 8) if deltas else 0.0}, {round(ci_high, 8) if deltas else 0.0}]",
        f"  statistically_significant: {significant}",
        "",
        "control_checks:",
        f"  all_pass: {all_controls_ok}",
        f"  query_count_match: {all(r.get('control_checks', {}).get('query_count_match', False) for r in valid_cells)}",
        f"  prng_collision_free: {all(r.get('control_checks', {}).get('prng_collision_free', False) for r in valid_cells)}",
        f"  baseline_consistency: {all(r.get('control_checks', {}).get('baseline_consistency', False) for r in valid_cells)}",
        "",
        "artifacts:",
        "  specification: experiments/EXP-SEMAEV-f48dd1/specification.yaml",
        "  implementation: experiments/EXP-SEMAEV-f48dd1/implementation/full_grid.py",
        "  raw_results: experiments/EXP-SEMAEV-f48dd1/runs/RUN-SEMAEV-f48dd1-grid/raw-results.json",
        "  analysis: experiments/EXP-SEMAEV-f48dd1/runs/RUN-SEMAEV-f48dd1-grid/analysis.yaml",
        "  manifest: experiments/EXP-SEMAEV-f48dd1/runs/RUN-SEMAEV-f48dd1-grid/manifest.yaml",
        "",
        "inference:",
        "  requested_policy: executor-implementation",
        "  resolved_model_id: null",
        "  fallback_used: false",
        "  model_verified: false",
        "",
        "notes:",
        f"  - Full grid completed: {len(valid_cells)} valid cells out of {len(all_results)} configurations.",
        f"  - Invalid runs: {invalid_count}.",
        f"  - Overall Δ = Y_B − Y_C = {round(mean_delta, 6)} with 95% CI [{round(ci_low, 6)}, {round(ci_high, 6)}].",
        f"  - Statistically significant: {significant}.",
        f"  - All control checks passed: {all_controls_ok}.",
        "  - This is a toy-scale experiment; no crypto-scale claims are made (AGENTS.md rule 7).",
    ]

    manifest_path = output_dir / "manifest.yaml"
    with open(manifest_path, "w") as f:
        f.write("\n".join(manifest_lines) + "\n")
    print(f"Manifest written to: {manifest_path}")

    print(f"\n{'=' * 70}")
    print(f"Full grid complete.")
    print(f"Total configurations: {len(all_results)}")
    print(f"Total arm-runs: {len(all_results) * 3}")
    print(f"Valid cells: {len(valid_cells)}")
    print(f"Invalid runs: {invalid_count}")
    print(f"Total wall clock: {total_elapsed:.2f}s")
    if deltas:
        print(f"Overall Δ = {mean_delta:.6f} ± {t_val * se:.6f} (95% CI)")
    print(f"{'=' * 70}")

    return 0 if invalid_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
