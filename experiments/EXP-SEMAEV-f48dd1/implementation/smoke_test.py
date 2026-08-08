#!/usr/bin/env python3
"""Smoke test for EXP-SEMAEV-f48dd1: x-oracle Semaev yield discrimination.

Single cell: m=3, p=101, b=0.4, seed=1, all three arms (A, B, C).

Arm A: no-oracle, exhaustive enumeration of all m-tuples
Arm B: x-oracle, MITM with true x-coordinate queries
Arm C: random predictor, MITM with PRNG queries (run-matched with B)

This is a smoke test to verify the implementation before the full cell grid.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from harness.toycurve import EllipticCurve, Point


def find_curve_p101() -> EllipticCurve:
    """Deterministic search for a nonsingular curve over F_101 with a point of order >= 5."""
    p = 101
    for A in range(p):
        for B in range(p):
            try:
                E = EllipticCurve(p, A, B)
            except ValueError:
                continue
            # Check for a point of order >= 5
            # Find any affine point
            for x in range(p):
                P = E.lift_x(x)
                if P is not None:
                    # Check order
                    Q = P
                    for k in range(2, 20):
                        Q = E.add(Q, P)
                        if Q is None:
                            # Order is k
                            if k >= 5:
                                return E
                            break
                    # If we didn't hit O, order is at least 20
                    return E
    raise RuntimeError("No suitable curve found over F_101")


def build_factor_base(E: EllipticCurve, B: int) -> List[Point]:
    """Build factor base: first B on-curve x-coordinates, then all points with those x-coords."""
    p = E.p
    x_coords = []
    for x in range(p):
        if E.lift_x(x) is not None:
            x_coords.append(x)
            if len(x_coords) == B:
                break
    
    if len(x_coords) < B:
        raise ValueError(f"Could not find {B} on-curve x-coordinates")
    
    # Collect all points with these x-coordinates
    points = []
    for x in x_coords:
        P = E.lift_x(x)
        if P is not None:
            points.append(P)
            neg_P = E.negate(P)
            if neg_P != P:  # Don't double-count if y=0
                points.append(neg_P)
    
    return points


def arm_a_no_oracle(E: EllipticCurve, F: List[Point], m: int, tuples_attempted: int) -> Dict:
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
                    field_ops += 2  # 2 additions
                    S = E.add(P1, P2)
                    S = E.add(S, P3)
                    if S is None:  # P1 + P2 + P3 = O
                        relations += 1
    
    wall_clock = time.perf_counter() - t0
    
    return {
        "tuples_enumerated": tuples_enumerated,
        "tuples_attempted": tuples_attempted,
        "relations_found": relations,
        "relations_verified": relations,
        "oracle_queries": 0,
        "hash_table_hits": 0,
        "false_positives": 0,
        "field_operations": field_ops,
        "wall_clock_seconds": round(wall_clock, 4),
    }


def arm_b_x_oracle(E: EllipticCurve, F: List[Point], m: int, tuples_attempted: int) -> Dict:
    """Arm B: x-oracle MITM."""
    t0 = time.perf_counter()
    
    if m != 3:
        raise NotImplementedError("Only m=3 implemented for smoke test")
    
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
            # Verify each candidate
            for P2, P3 in H[x_P1]:
                candidates_verified += 1
                field_ops += 2
                S = E.add(P1, P2)
                S = E.add(S, P3)
                if S is None:  # Verified relation
                    relations_found += 1
                else:
                    false_positives += 1
    
    wall_clock = time.perf_counter() - t0
    
    return {
        "tuples_enumerated": candidates_verified,  # Candidate tuples verified
        "tuples_attempted": tuples_attempted,
        "relations_found": relations_found,
        "relations_verified": relations_found,
        "oracle_queries": oracle_queries,
        "hash_table_hits": hash_table_hits,
        "false_positives": false_positives,
        "field_operations": field_ops,
        "wall_clock_seconds": round(wall_clock, 4),
        "right_half_pairs": right_pairs,
    }


def arm_c_random_predictor(E: EllipticCurve, F: List[Point], m: int, seed: int, tuples_attempted: int) -> Dict:
    """Arm C: random predictor MITM (run-matched with B)."""
    t0 = time.perf_counter()
    
    if m != 3:
        raise NotImplementedError("Only m=3 implemented for smoke test")
    
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
    
    for P1 in F:
        oracle_queries += 1
        # Deterministic PRNG keyed on (seed, P1)
        prng_key = f"{seed}:{P1[0]}:{P1[1]}"
        prng_hash = hashlib.sha256(prng_key.encode()).hexdigest()
        x_rand = int(prng_hash, 16) % E.p  # Pseudo-random field element
        
        # Check for collision (control check)
        if x_rand in prng_outputs:
            raise RuntimeError(f"PRNG collision detected: {x_rand}")
        prng_outputs.add(x_rand)
        
        if x_rand in H:
            hash_table_hits += 1
            # Verify each candidate
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
        "tuples_enumerated": candidates_verified,
        "tuples_attempted": tuples_attempted,
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


def main():
    print("=" * 70)
    print("EXP-SEMAEV-f48dd1 Smoke Test")
    print("m=3, p=101, b=0.4, seed=1")
    print("=" * 70)
    
    # Parameters
    m = 3
    p = 101
    b = 0.4
    seed = 1
    B = int(math.floor(p ** b))
    
    print(f"\nParameters: m={m}, p={p}, b={b}, B={B}, seed={seed}")
    
    # Find curve
    print("\n[1/4] Finding curve over F_101...")
    E = find_curve_p101()
    N = E.order()
    print(f"  Curve: y^2 = x^3 + {E.a}x + {E.b} over F_{p}")
    print(f"  Order N = {N}")
    
    # Build factor base
    print(f"\n[2/4] Building factor base (B={B} x-coordinates)...")
    F = build_factor_base(E, B)
    print(f"  Factor base size: |F| = {len(F)} points")
    print(f"  x-coordinates: {sorted(set(pt[0] for pt in F))}")
    
    # Expected relations baseline: |F|^m / N (random model)
    F_size = len(F)
    tuples_attempted = F_size ** m
    expected_relations = tuples_attempted / N
    expected_yield = 1.0 / N  # yield = relations / tuples = (|F|^m/N) / |F|^m
    print(f"  Expected relations: |F|^m/N = {F_size}^{m}/{N} ≈ {expected_relations:.4f}")
    print(f"  Expected yield: 1/N = 1/{N} ≈ {expected_yield:.6f}")
    
    # Run all three arms
    results = {}
    
    print("\n[3/4] Running Arm A (no-oracle, exhaustive)...")
    results["A"] = arm_a_no_oracle(E, F, m, tuples_attempted)
    results["A"]["arm"] = "A"
    results["A"]["oracle_type"] = "none"
    print(f"  Tuples attempted/verified: {results['A']['tuples_attempted']}/{results['A']['tuples_enumerated']}")
    print(f"  Relations: {results['A']['relations_found']}")
    print(f"  Yield: {results['A']['relations_found'] / results['A']['tuples_attempted']:.6f}")
    print(f"  Time: {results['A']['wall_clock_seconds']}s")
    
    print("\n[3/4] Running Arm B (x-oracle, MITM)...")
    results["B"] = arm_b_x_oracle(E, F, m, tuples_attempted)
    results["B"]["arm"] = "B"
    results["B"]["oracle_type"] = "x_coordinate"
    print(f"  Oracle queries: {results['B']['oracle_queries']}")
    print(f"  Hash table hits: {results['B']['hash_table_hits']}")
    print(f"  Relations: {results['B']['relations_found']}")
    print(f"  Tuples attempted/verified: {results['B']['tuples_attempted']}/{results['B']['tuples_enumerated']}")
    print(f"  Yield: {results['B']['relations_found'] / results['B']['tuples_attempted']:.6f}")
    print(f"  Time: {results['B']['wall_clock_seconds']}s")
    
    print("\n[3/4] Running Arm C (random predictor, MITM)...")
    results["C"] = arm_c_random_predictor(E, F, m, seed, tuples_attempted)
    results["C"]["arm"] = "C"
    results["C"]["oracle_type"] = "random_predictor"
    print(f"  Oracle queries: {results['C']['oracle_queries']}")
    print(f"  Hash table hits: {results['C']['hash_table_hits']}")
    print(f"  Relations: {results['C']['relations_found']}")
    print(f"  Tuples attempted/verified: {results['C']['tuples_attempted']}/{results['C']['tuples_enumerated']}")
    print(f"  Yield: {results['C']['relations_found'] / results['C']['tuples_attempted']:.6f}")
    print(f"  Time: {results['C']['wall_clock_seconds']}s")
    
    # Control checks
    print("\n[4/4] Running control checks...")
    
    # Check 1: query count match
    query_match = results["B"]["oracle_queries"] == results["C"]["oracle_queries"]
    print(f"  Query count match (B==C): {query_match}")
    
    # Check 2: PRNG collision free
    prng_ok = results["C"].get("prng_collision_free", False)
    print(f"  PRNG collision free: {prng_ok}")
    
    # Check 3: baseline consistency
    Y_A = results["A"]["relations_found"] / results["A"]["tuples_attempted"]
    baseline_ok = (Y_A >= expected_yield / 4) and (Y_A <= expected_yield * 4)
    print(f"  Baseline consistency (Y_A within factor 4 of B^m/N): {baseline_ok}")
    print(f"    Y_A = {Y_A:.6f}, expected ≈ {expected_yield:.6f}")
    
    all_controls_pass = query_match and prng_ok and baseline_ok
    print(f"\n  All controls pass: {all_controls_pass}")
    
    # Compute yields
    for arm in ["A", "B", "C"]:
        tuples = results[arm]["tuples_attempted"]
        rels = results[arm]["relations_found"]
        results[arm]["yield"] = rels / tuples if tuples > 0 else 0.0
    
    # Write raw-result.json
    output_dir = Path(__file__).parent.parent / "runs" / "RUN-SEMAEV-f48dd1-smoke"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    raw_result = {
        "cell_id": f"m{m}_p{p}_b{b}_seed{seed}",
        "m": m,
        "p": p,
        "b": b,
        "B": B,
        "N": N,
        "curve": {"a": E.a, "b": E.b},
        "factor_base_size": len(F),
        "factor_base_x_coords": sorted(set(pt[0] for pt in F)),
        "expected_yield_baseline": expected_yield,
        "arms": {
            "A": results["A"],
            "B": results["B"],
            "C": results["C"],
        },
        "control_checks": {
            "query_count_match": query_match,
            "prng_collision_free": prng_ok,
            "baseline_consistency": baseline_ok,
        },
        "all_controls_pass": all_controls_pass,
        "status": "completed" if all_controls_pass else "control_check_failed",
    }
    
    raw_result_path = output_dir / "raw-result.json"
    with open(raw_result_path, "w") as f:
        json.dump(raw_result, f, indent=2)
    
    print(f"\n{'=' * 70}")
    print(f"Smoke test complete.")
    print(f"Raw result written to: {raw_result_path}")
    print(f"Status: {raw_result['status']}")
    print(f"{'=' * 70}")
    
    return 0 if all_controls_pass else 1


if __name__ == "__main__":
    sys.exit(main())
