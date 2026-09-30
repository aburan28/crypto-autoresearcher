#!/usr/bin/env python3
"""Close the census gap exactly, for the only point counts that matter.

weil_census.py enumerates isogeny classes and validates at g = 1, 2 but finds
211 of the 215 known classes at g = 3, so a zero from it is "none found by an
enumerator with a gap". This script removes the dependence on that gap for the
question actually asked.

Method. Instead of enumerating every class and reading off point counts, enumerate
only the integer real Weil polynomials h of degree g whose point count
h(q + 1) = h(3) is EXACTLY one of the multiples of the modulus inside the Weil
range, then decide real-rootedness in [-2 sqrt q, 2 sqrt q] EXACTLY rather than
numerically. Pinning h(3) removes one coefficient, and exactness removes the
repeated-root fragility that the census's numeric filter has.

Exact test. All roots real and in the closed box iff, after dividing out the only
integer factor whose roots sit ON the boundary (x^2 - 8, roots +- 2 sqrt 2), the
remaining factor has degree-many real roots strictly inside. Root counting is by
Sturm sequence over the rationals (sympy Poly.count_roots), with the boundary
approached from a rational strictly inside 2 sqrt 2 = 2.8284271247461903 and a
rational strictly outside, so a root in the gap between them would show up as a
disagreement and is reported rather than silently classified.

Run: python3 exact_targets.py [--max-dim 4] [--modulus 131] [--json out.json]
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import sys

import sympy as sp

Q = 2
BOX = 2 * math.sqrt(Q)
X = sp.Symbol("x")
BOUNDARY = sp.Poly(X**2 - 4 * Q, X)          # roots exactly +- 2 sqrt q
INSIDE = sp.Rational(28284271, 10000000)     # < 2 sqrt 2
OUTSIDE = sp.Rational(28284272, 10000000)    # > 2 sqrt 2


def exact_real_rooted_in_box(coeffs: list[int]) -> tuple[bool, bool]:
    """(verdict, ambiguous). Ambiguous flags a root between INSIDE and OUTSIDE."""
    poly = sp.Poly([sp.Integer(c) for c in coeffs], X)
    # strip boundary factors, whose roots are legitimately at +- 2 sqrt q
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
    ceiling = (1 + math.sqrt(Q)) ** (2 * g)     # max #A(F_q) = prod (q + 1 - beta_i)
    return [k for k in range(modulus, math.floor(ceiling) + 1, modulus)]


def search(g: int, modulus: int) -> dict:
    bounds = [math.comb(g, k) * BOX**k for k in range(g + 1)]
    ranges = [range(-int(bounds[k]) - 1, int(bounds[k]) + 2) for k in range(1, g)]
    results, ambiguous, scanned = [], [], 0
    for target in targets_for(g, modulus):
        for head in itertools.product(*ranges) if g > 1 else [()]:
            # h(3) = sum a_i 3^{g-i} pins the last coefficient
            partial = [1] + list(head)
            pinned = target - sum(c * (Q + 1) ** (g - i) for i, c in enumerate(partial))
            if abs(pinned) > int(bounds[g]) + 1:
                continue
            coeffs = partial + [pinned]
            scanned += 1
            verdict, is_ambiguous = exact_real_rooted_in_box(coeffs)
            if is_ambiguous:
                ambiguous.append({"points": target, "h": coeffs})
            if verdict:
                results.append({"points": target, "h": coeffs})
    return {
        "dimension": g,
        "targets": targets_for(g, modulus),
        "candidates_scanned": scanned,
        "weil_polynomials_found": results,
        "ambiguous_near_boundary": ambiguous,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--max-dim", type=int, default=4)
    ap.add_argument("--modulus", type=int, default=131)
    ap.add_argument("--json", type=str, default=None)
    args = ap.parse_args()

    # self-test: the exact predicate must accept a known class and reject a non-class
    assert exact_real_rooted_in_box([1, 0])[0], "degree-1 h = x must be accepted"
    assert not exact_real_rooted_in_box([1, 0, -100])[0], "roots at +-10 must be rejected"
    assert exact_real_rooted_in_box([1, 0, -4 * Q])[0], "the boundary factor must be accepted"

    report = {"base_field": Q, "modulus": args.modulus, "searches": []}
    for g in range(1, args.max_dim + 1):
        row = search(g, args.modulus)
        report["searches"].append(row)
        print(
            f"g={g}: point counts {row['targets'] or '(none in Weil range)'}"
            f" | candidates scanned {row['candidates_scanned']}"
            f" | Weil polynomials found {len(row['weil_polynomials_found'])}"
            f" | ambiguous near boundary {len(row['ambiguous_near_boundary'])}",
            flush=True,
        )
        for hit in row["weil_polynomials_found"]:
            print(f"    FOUND #A(F_2) = {hit['points']}  h = {hit['h']}", flush=True)
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(report, fh, indent=2)
        print(f"wrote {args.json}")


if __name__ == "__main__":
    main()
