#!/usr/bin/env python3
"""EXP-FROB-720a77: extend the exact Weil-census exclusion at n=131, q=2 to dimensions 5 and 6.

Contract: experiments/EXP-FROB-720a77/specification.yaml (DEC-20261005-0f460b).
Hypothesis H-FROB-ff99bf. PROVENANCE: exact_real_rooted_in_box, targets_for and
the pin/box arithmetic are copied from analysis/couveignes-lercier-131/exact_targets.py
(origin/main), which excluded dimensions 1-4 (104 exact tests at g=3, 234,220 at
g=4, zero hits). Added here, per the frozen contract: (i) the feasibility gate --
candidates are COUNTED exactly by a DP over the head-coefficient boxes (no Sturm)
before any exact test, and a dimension whose count exceeds FEASIBILITY_LIMIT stops
as an impediment with the count reported; (ii) C1 assertions that the recorded
g=3 (104) and g=4 (234,220) figures reproduce; (iii) C3 candidate counts per
multiple; (iv) a wall-clock guard that stops a dimension at TIME_LIMIT_SECONDS as
an infrastructure impediment, never evidence; (v) run-receipt fields. The exact
search enumerates each head tuple once and tests the (few) multiples whose pin
window it lands in -- algebraically identical to the original target-outer loop.

Every reported number is produced by this run. Deterministic, seed-free.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import platform
import subprocess
import sys
import time

import numpy as np
import sympy as sp

Q = 2
BOX = 2 * math.sqrt(Q)
X = sp.Symbol("x")
BOUNDARY = sp.Poly(X**2 - 4 * Q, X)
INSIDE = sp.Rational(28284271, 10000000)
OUTSIDE = sp.Rational(28284272, 10000000)
FEASIBILITY_LIMIT = 50_000_000
TIME_LIMIT_SECONDS = 14_400  # contract budget.wall_clock_seconds; guard, not a claim input
C1_EXPECTED = {3: 104, 4: 234220}


def exact_real_rooted_in_box(coeffs: list[int]) -> tuple[bool, bool]:
    """(verdict, ambiguous). Copied verbatim from exact_targets.py (C2 boundary logic)."""
    poly = sp.Poly([sp.Integer(c) for c in coeffs], X)
    while poly.degree() >= 2:
        quotient, remainder = sp.div(poly, BOUNDARY, X)
        if sp.Poly(remainder, X).is_zero:
            poly = sp.Poly(quotient, X)
        else:
            break
    if poly.degree() <= 0:
        return True, False
    total_real = poly.count_roots()
    if total_real != poly.degree():
        return False, False
    inside = poly.count_roots(-INSIDE, INSIDE)
    outside = poly.count_roots(-OUTSIDE, OUTSIDE)
    if inside != outside:
        return outside == poly.degree(), True
    return inside == poly.degree(), False


def targets_for(g: int, modulus: int) -> list[int]:
    ceiling = (1 + math.sqrt(Q)) ** (2 * g)
    return [k for k in range(modulus, math.floor(ceiling) + 1, modulus)]


def head_box(g: int):
    """(per-k integer ranges, pin cap) exactly as exact_targets.search builds them."""
    bounds = [math.comb(g, k) * BOX**k for k in range(g + 1)]
    ranges = [range(-int(bounds[k]) - 1, int(bounds[k]) + 2) for k in range(1, g)]
    cap = int(bounds[g]) + 1
    return ranges, cap


def count_candidates_dp(g: int, modulus: int) -> tuple[int, dict]:
    """Exact candidate count per multiple via DP over the head-coefficient boxes.

    E(head) = 3^g + sum_{k=1}^{g-1} v_k * 3^(g-k); candidate for target t iff
    |t - E| <= cap. DP convolves the uniform boxes; result is exact integer
    arithmetic, no Sturm.
    """
    ranges, cap = head_box(g)
    weights = [(Q + 1) ** (g - k) for k in range(1, g)]  # k = 1..g-1
    # distribution of E over its achievable integer values
    lo = (Q + 1) ** g - sum((r.stop - 1) * w for r, w in zip(ranges, weights))
    hi = (Q + 1) ** g + sum((r.stop - 1) * w for r, w in zip(ranges, weights))
    size = hi - lo + 1
    dist = np.zeros(size, dtype=np.int64)
    dist[(Q + 1) ** g - lo] = 1
    for r, w in zip(ranges, weights):
        nd = np.zeros_like(dist)
        for v in r:
            shift = v * w
            nd[max(0, shift):size + min(0, shift)] += dist[max(0, -shift):size - max(0, shift)]
        dist = nd
    per_multiple = {}
    total = 0
    for t in targets_for(g, modulus):
        a, b = t - cap, t + cap
        i0, i1 = max(0, a - lo), min(size - 1, b - lo)
        c = int(dist[i0 : i1 + 1].sum()) if i1 >= i0 else 0
        per_multiple[t] = c
        total += c
    return total, per_multiple


def exact_search(g: int, modulus: int, deadline: float) -> dict:
    ranges, cap = head_box(g)
    targets = targets_for(g, modulus)
    tmin, tmax = targets[0], targets[-1]
    results, ambiguous, scanned = [], [], 0
    per_multiple = {t: 0 for t in targets}
    t0 = time.time()
    for head in itertools.product(*ranges) if g > 1 else [()]:
        E = (Q + 1) ** g + sum(v * (Q + 1) ** (g - 1 - i) for i, v in enumerate(head))
        lo_t = max(tmin, E - cap)
        hi_t = min(tmax, E + cap)
        if lo_t > hi_t:
            continue
        k0 = -(-(lo_t) // modulus) * modulus  # first multiple of modulus >= lo_t
        coeffs_head = [1] + list(head)
        for t in range(k0, hi_t + 1, modulus):
            pinned = t - E
            scanned += 1
            per_multiple[t] += 1
            verdict, is_ambiguous = exact_real_rooted_in_box(coeffs_head + [pinned])
            if is_ambiguous:
                ambiguous.append({"points": t, "h": coeffs_head + [pinned]})
            if verdict:
                results.append({"points": t, "h": coeffs_head + [pinned]})
        if scanned % 100000 == 0 and time.time() > deadline:
            return {
                "dimension": g,
                "targets": targets,
                "candidates_per_multiple": per_multiple,
                "candidates_scanned": scanned,
                "weil_polynomials_found": results,
                "ambiguous_near_boundary": ambiguous,
                "wall_clock_seconds": time.time() - t0,
                "impediment": f"wall-clock guard {TIME_LIMIT_SECONDS}s reached mid-dimension",
            }
    return {
        "dimension": g,
        "targets": targets,
        "candidates_per_multiple": per_multiple,
        "candidates_scanned": scanned,
        "weil_polynomials_found": results,
        "ambiguous_near_boundary": ambiguous,
        "wall_clock_seconds": time.time() - t0,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--modulus", type=int, default=131)
    ap.add_argument("--json", type=str, required=True)
    args = ap.parse_args()
    t_start = time.time()

    assert exact_real_rooted_in_box([1, 0, -4 * Q])[0], "the boundary factor must be accepted"
    out = {
        "experiment_id": "EXP-FROB-720a77",
        "hypothesis_id": "H-FROB-ff99bf",
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "sympy": sp.__version__,
        "platform": platform.platform(),
        "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "feasibility_limit_exact_tests": FEASIBILITY_LIMIT,
        "time_limit_seconds": TIME_LIMIT_SECONDS,
        "dimensions": [],
    }
    print(json.dumps({k: out[k] for k in ("experiment_id", "started_utc", "feasibility_limit_exact_tests")}), flush=True)

    for g in (1, 2, 3, 4, 5, 6):
        total, per_multiple = count_candidates_dp(g, args.modulus)
        print(f"g={g}: candidates (DP, exact, no Sturm) = {total}", flush=True)
        if g in C1_EXPECTED and total != C1_EXPECTED[g]:
            out["dimensions"].append({
                "dimension": g, "candidates_per_multiple": per_multiple,
                "candidates_scanned": 0, "weil_polynomials_found": [],
                "ambiguous_near_boundary": [], "c1_reproduction": "FAIL",
                "c1_expected": C1_EXPECTED[g]})
            print(f"g={g}: C1 FAIL (expected {C1_EXPECTED[g]}, counted {total}); stopping.", flush=True)
            json.dump(out, open(args.json, "w"), indent=1)
            sys.exit(2)
        if total == 0:
            out["dimensions"].append({"dimension": g, "candidates_per_multiple": per_multiple,
                "candidates_scanned": 0, "weil_polynomials_found": [],
                "ambiguous_near_boundary": [],
                "note": "no candidate: no multiple of 131 in Weil range (g<=2) or empty pin window"})
            json.dump(out, open(args.json, "w"), indent=1)
            continue
        if total > FEASIBILITY_LIMIT:
            out["dimensions"].append({
                "dimension": g, "candidates_per_multiple": per_multiple,
                "candidates_scanned": 0, "weil_polynomials_found": [],
                "ambiguous_near_boundary": [],
                "impediment": f"feasibility gate: {total} > {FEASIBILITY_LIMIT} exact tests"})
            print(f"g={g}: FEASIBILITY GATE fires ({total} > {FEASIBILITY_LIMIT}); impediment, not evidence.", flush=True)
            json.dump(out, open(args.json, "w"), indent=1)
            continue
        row = exact_search(g, args.modulus, t_start + TIME_LIMIT_SECONDS)
        if g in C1_EXPECTED:
            row["c1_reproduction"] = ("PASS" if row["candidates_scanned"] == C1_EXPECTED[g]
                                      and not row["weil_polynomials_found"] else "FAIL")
        out["dimensions"].append(row)
        print(f"g={g}: exact tests {row['candidates_scanned']}, hits {len(row['weil_polynomials_found'])}, "
              f"ambiguous {len(row['ambiguous_near_boundary'])}, wall {row['wall_clock_seconds']:.1f}s"
              + (" [IMPEDIMENT: time guard]" if "impediment" in row else ""), flush=True)
        json.dump(out, open(args.json, "w"), indent=1)
        if "impediment" in row:
            break
    out["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    json.dump(out, open(args.json, "w"), indent=1)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
