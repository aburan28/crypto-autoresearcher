#!/usr/bin/env python3
"""Exact finite triangular-lattice accounting for Semaev small-root shifts.

This is an instrument audit and a finite candidate construction, not an optimal
shift solver, root extractor, or ECDLP algorithm. Historical smallroot_reach.py
outputs are retained unchanged. A determinant condition does not imply enough
independent short polynomials, successful root extraction, or an IC improvement.

For N rows, all evaluating to multiples of p**t, let q be the sum of row
modulus exponents and s_i the column scaling exponents. The determinant is
p**q * product(X_i**s_i). The determinant-level budget is therefore
sum(beta_i*s_i) < t*N-q, BEFORE charging LLL/norm factors. It is not q.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
from itertools import product
import json
from math import comb
from pathlib import Path


def _add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def _order(a):
    return sum(a), a


def _multiply(f, g):
    out = {}
    for a, ca in f.items():
        for b, cb in g.items():
            e = _add(a, b)
            out[e] = out.get(e, 0) + ca * cb
    return {e: c for e, c in out.items() if c}


def _support_product(a, b):
    return {_add(x, y) for x in a for y in b}


def s3(a=2, b=3):
    """S3 over the integers in (x,y,z); no field or root is chosen."""
    terms = {
        (2, 0, 2): 1, (1, 1, 2): -2, (0, 2, 2): 1,
        (2, 1, 1): -2, (1, 2, 1): -2,
        (1, 0, 1): -2*a, (0, 1, 1): -2*a, (0, 0, 1): -4*b,
        (2, 2, 0): 1, (1, 1, 0): -2*a,
        (1, 0, 0): -4*b, (0, 1, 0): -4*b, (0, 0, 0): a*a,
    }
    return {e: c for e, c in terms.items() if c}


def _embed(poly, positions, n, fixed=None):
    out = {}
    for powers, coefficient in poly.items():
        target = [0]*n
        for power, position in zip(powers, positions):
            if position is None:
                coefficient *= fixed**power
            else:
                target[position] += power
        e = tuple(target)
        out[e] = out.get(e, 0) + coefficient
    return {e: c for e, c in out.items() if c}


def joint_system(a=2, b=3, xq=5):
    """Coordinate order x1,x2,x3,x4,u,v; xq is a fixed integer coefficient."""
    f = s3(a, b)
    return [
        _embed(f, (0, 1, 4), 6),
        _embed(f, (2, 3, 5), 6),
        _embed(f, (4, 5, None), 6, xq),
    ]


def _record(t, n, equations, columns, choices, row_support_sizes):
    dimension = len(columns)
    q = sum(t - sum(k) for k in choices)
    coordinate_sums = [sum(a[i] for a in columns) for i in range(n)]
    rhs = t*dimension-q
    beta = Fraction(rhs, sum(coordinate_sums))
    return {
        "multiplicity": t,
        "equations": equations,
        "dimension": dimension,
        "row_modulus_exponent": q,
        "divisibility_exponent": t*dimension,
        "budget": rhs,
        "coordinate_exponents": coordinate_sums,
        "equal_beta": str(beta),
        "equal_bound_volume_per_equation": str(n*beta/equations),
        "legacy_q_as_budget_volume_per_equation": str(
            Fraction(n*q, equations*sum(coordinate_sums))),
        "dense_matrix_entries": dimension*dimension,
        "nonzero_entries_upper_bound": sum(row_support_sizes),
        "row_power_histogram": {
            str(power): sum(sum(k) == power for k in choices)
            for power in range(t+1)
        },
        "lll_and_norm_factors_charged": False,
        "root_extraction_implemented": False,
        "optimality_claimed": False,
    }


def single_lattice(poly, t):
    """Build row descriptors for the historical shift family with exact budgets."""
    if t < 1:
        raise ValueError("multiplicity must be positive")
    n = len(next(iter(poly)))
    lead = max(poly, key=_order)
    if poly[lead] != 1:
        raise ValueError("the leading coefficient must be one")
    supports = [{(0,)*n}]
    for _ in range(t):
        supports.append(_support_product(supports[-1], set(poly)))
    sets = [{_add(a, tuple(k*x for x in lead)) for a in supports[t-k]}
            for k in range(t+1)]
    sets.append(set())
    for small, large in zip(sets[1:], sets):
        if not small <= large:
            raise ValueError("shift sets are not nested")
    columns = sorted(sets[0], key=_order)
    choices = []
    sizes = []
    descriptors = []
    for a in columns:
        k = max(j for j in range(t+1) if a in sets[j])
        shift = tuple(x-k*y for x, y in zip(a, lead))
        if min(shift) < 0:
            raise AssertionError("negative multiplier")
        support = {_add(shift, e) for e in supports[k]}
        if not support <= sets[0] or max(support, key=_order) != a:
            raise AssertionError("row is not supported and triangular")
        descriptors.append((shift, (k,)))
        choices.append((k,))
        sizes.append(len(support))
    return _record(t, n, 1, columns, choices, sizes), columns, descriptors


def joint_lattice(polys, t):
    """Finite union-support candidate, greedy ONLY within declared triangular rows.

    The column set is the t-fold Minkowski sum of the union of input supports.
    For each column choose the largest total polynomial power whose shifted
    support stays in that set. No assertion of global shift optimality follows.
    """
    if not 1 <= t <= 3:
        raise ValueError("this finite audit implements multiplicities 1..3")
    n = len(next(iter(polys[0])))
    zero = (0,)*n
    supports = [set(f) for f in polys]
    leads = [max(f, key=_order) for f in polys]
    if any(f[lead] != 1 for f, lead in zip(polys, leads)):
        raise ValueError("leading coefficients must be one")
    union = set.union(*supports)
    universe = {zero}
    for _ in range(t):
        universe = _support_product(universe, union)
    candidates = []
    for powers in product(range(t+1), repeat=len(polys)):
        if sum(powers) > t:
            continue
        support = {zero}
        leading = zero
        for power, base, lead in zip(powers, supports, leads):
            for _ in range(power):
                support = _support_product(support, base)
                leading = _add(leading, lead)
        candidates.append((powers, leading, support))
    candidates.sort(key=lambda row: (sum(row[0]), row[0]), reverse=True)
    columns = sorted(universe, key=_order)
    descriptors = []
    choices = []
    sizes = []
    for a in columns:
        for powers, leading, support in candidates:
            shift = tuple(x-y for x, y in zip(a, leading))
            if min(shift) < 0:
                continue
            shifted = {_add(shift, e) for e in support}
            if shifted <= universe:
                if max(shifted, key=_order) != a:
                    raise AssertionError("row is not triangular")
                descriptors.append((shift, powers))
                choices.append(powers)
                sizes.append(len(support))
                break
        else:
            raise AssertionError("the p^t monomial row must always exist")
    return _record(t, n, len(polys), columns, choices, sizes), columns, descriptors


def coefficient_matrix(polys, t, columns, descriptors, p, bounds):
    """Materialize exact integer rows for a small diagnostic lattice."""
    if len(columns) > 400:
        raise ValueError("exact dense fixture capped at 400 columns")
    n = len(bounds)
    rows = []
    for shift, powers in descriptors:
        row_poly = {(0,)*n: p**(t-sum(powers))}
        for f, power in zip(polys, powers):
            for _ in range(power):
                row_poly = _multiply(row_poly, f)
        row_poly = {_add(shift, e): c for e, c in row_poly.items()}
        if not set(row_poly) <= set(columns):
            raise AssertionError("materialized row escapes the columns")
        rows.append([
            row_poly.get(e, 0) * _scale(e, bounds) for e in columns
        ])
    return rows


def _scale(e, bounds):
    value = 1
    for exponent, bound in zip(e, bounds):
        value *= bound**exponent
    return value


def predicted_determinant(record, p, bounds):
    value = p**record["row_modulus_exponent"]
    return value*_scale(record["coordinate_exponents"], bounds)


def full_box_budget(n, d, t):
    if min(n, d, t) < 1:
        raise ValueError("n,d,t must be positive")
    counts = [(d*(t-k)+1)**n for k in range(t+1)] + [0]
    rhs = sum(k*(counts[k]-counts[k+1]) for k in range(t+1))
    s = n*(t*d)*(t*d+1)**n//2
    return Fraction(rhs, s)


def full_box_limit(n, d):
    """Equal-beta determinant limit for this family; not root-extraction reach."""
    if min(n, d) < 1:
        raise ValueError("n,d must be positive")
    return Fraction(2, n*d*(n+1))


def total_degree_joint_budget(t):
    """A second, explicit joint shift family on monomials of degree <=4t.

    The leading monomials x1^2*x2^2, x3^2*x4^2, u^2*v^2 are disjoint.
    Count powers of their monomial ideal via its generating series. This is
    a candidate family, not an optimum over arbitrary joint lattices.
    """
    if t < 1:
        raise ValueError("multiplicity must be positive")
    degree = 4*t
    dimension = comb(degree+6, 6)
    budget = 3*sum(comb(degree-4*j+6, 6) for j in range(1, t+1))
    s_i = comb(degree+6, 7)
    return {"multiplicity": t, "dimension": dimension,
            "budget": budget, "coordinate_exponents": [s_i]*6,
            "equal_bound_volume_per_equation": str(Fraction(budget, 3*s_i)),
            "dense_matrix_entries": dimension*dimension}


def audit():
    sparse = [single_lattice(s3(), t)[0] for t in (1, 2, 4, 6, 8, 10)]
    joint = [joint_lattice(joint_system(), t)[0] for t in (1, 2, 3)]
    return {
        "schema": "joint-smallroot-finite-audit-v1",
        "scope": "deterministic software accounting; no scientific trial or DLP solve",
        "single_s3": sparse, "joint_union_support": joint,
        "joint_total_degree": [total_degree_joint_budget(t) for t in (1, 2, 3, 8, 16)],
        "full_box_limits": [
            {"n": n, "d": d, "equal_beta": str(full_box_limit(n,d)),
             "volume_exponent": str(n*full_box_limit(n,d))}
            for n,d in ((1,2),(2,2),(3,2),(3,4))
        ],
        "pipeline_improvement_demonstrated": False,
        "independent_review_completed": False,
        "root_recovery_success_rate": None,
        "end_to_end_ic_cost": None,
        "limitations": [
            "Finite determinant statistics exclude LLL and norm factors.",
            "No algebraic-independence or root-extraction guarantee.",
            "Equal-bound volume is one slice, not a weighted-region certificate.",
            "No optimal shifts or rank-two GAP substitution implemented.",
            "The fixed xQ fixture is algebraic input, not a subgroup instance.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = audit()
    # Audit outputs are write-once, so replays never overwrite prior observations.
    with args.out.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(f"Finite audit written to {args.out}; no pipeline improvement claimed.")


if __name__ == "__main__":
    main()
