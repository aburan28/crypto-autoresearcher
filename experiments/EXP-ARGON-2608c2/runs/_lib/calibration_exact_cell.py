#!/usr/bin/env python3
"""
Reproduction entry point for one EXP-ARGON-2608c2 calibration_exact_tier
cell: builds the named reference family at the given q, runs the frozen
greedy eps-depth-reducing-set heuristic and the independent exact ILP
solver, verifies the exact result from scratch, and prints the
calibration_error_ratio.

Usage:
  python3 calibration_exact_cell.py --family family_A_doubling_graph --q 64 \
      --time-limit-seconds 150
"""
import argparse
import json
import sys
import time

import graphs as G

FAMILIES = {
    "family_A_doubling_graph": G.family_A_doubling_graph,
    "family_B_pure_chain": G.family_B_pure_chain,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", required=True, choices=list(FAMILIES))
    ap.add_argument("--q", required=True, type=int)
    ap.add_argument("--time-limit-seconds", required=True, type=int)
    args = ap.parse_args()

    builder = FAMILIES[args.family]
    g = builder(args.q)
    nd = G.native_depth(args.q, g)
    target = nd // 2

    t0 = time.time()
    greedy_removed, greedy_depth, greedy_iters = G.greedy_reduce(args.q, g, target)
    greedy_time = time.time() - t0

    t0 = time.time()
    exact_removed, exact_size, exact_status, solver_log = G.exact_min_removal_ilp(
        args.q, g, target, time_limit_seconds=args.time_limit_seconds
    )
    exact_time = time.time() - t0
    verify_ok, verify_depth = G.verify_removal(args.q, g, exact_removed, target)

    ratio = len(greedy_removed) / exact_size if exact_size > 0 else float("inf")

    result = {
        "family": args.family,
        "q": args.q,
        "native_depth": nd,
        "target_depth": target,
        "greedy_removed_size": len(greedy_removed),
        "greedy_final_depth": greedy_depth,
        "greedy_iterations": greedy_iters,
        "greedy_wall_seconds": greedy_time,
        "exact_removed_size": exact_size,
        "exact_status": exact_status,
        "exact_verify_ok": verify_ok,
        "exact_verify_depth": verify_depth,
        "exact_wall_seconds": exact_time,
        "calibration_error_ratio": ratio,
        "calibration_error_ratio_certified": exact_status == "proven_optimal",
    }
    print(json.dumps(result, indent=2))
    print("---- CBC solver log ----", file=sys.stderr)
    print(solver_log, file=sys.stderr)


if __name__ == "__main__":
    main()
