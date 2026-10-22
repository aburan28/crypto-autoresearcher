#!/usr/bin/env python3
"""Read-only C5 matrix replay against the three frozen core-cell outputs.

Independent of the archived Sage and checker imports. This validates exact
recorded matrices, factor kernels, and C5 flags, but is not a Lean refinement
proof of either implementation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from math import isqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2"
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "c5-matrix-replay.json"
CONFIG = {
    "FROB-SPLIT-q11n5": {
        "q": 11, "g": [1, 0, 0, 0, 2, 1], "g_string": "x^5 + 2*x^4 + 1",
        "factors": [[2, 1], [6, 1], [7, 1], [8, 1]],
        "factor_strings": ["x + 2", "x + 6", "x + 7", "x + 8"],
        "expected_dimensions": [1, 1, 1, 1],
    },
    "FROB-NOLATTICE-q13n5": {
        "q": 13, "g": [1, 0, 0, 0, 8, 1], "g_string": "x^5 + 8*x^4 + 1",
        "factors": [[1, 1, 1, 1, 1]],
        "factor_strings": ["x^4 + x^3 + x^2 + x + 1"],
        "expected_dimensions": [4],
    },
    "FROB-EQDEG-q19n5": {
        "q": 19, "g": [1, 0, 0, 0, 3, 1], "g_string": "x^5 + 3*x^4 + 1",
        "factors": [[1, 5, 1], [1, 15, 1]],
        "factor_strings": ["x^2 + 5*x + 1", "x^2 + 15*x + 1"],
        "expected_dimensions": [2, 2],
    },
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def polynomial_mul(a: list[int], b: list[int], q: int) -> list[int]:
    c = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            c[i + j] = (c[i + j] + x * y) % q
    return c


def quotient_product(a: list[int], b: list[int], g: list[int], q: int) -> list[int]:
    c = polynomial_mul(a, b, q)
    n = len(g) - 1
    for k in range(len(c) - 1, n - 1, -1):
        t = c[k]
        for j in range(n + 1):
            c[k - n + j] = (c[k - n + j] - t * g[j]) % q
    return (c[:n] + [0] * n)[:n]


def quotient_power(a: list[int], exponent: int, g: list[int], q: int) -> list[int]:
    n = len(g) - 1
    out = [1] + [0] * (n - 1)
    base = a
    while exponent:
        if exponent & 1:
            out = quotient_product(out, base, g, q)
        base = quotient_product(base, base, g, q)
        exponent >>= 1
    return out


def trim(a: list[int]) -> list[int]:
    while a and a[-1] == 0:
        a.pop()
    return a


def remainder(a: list[int], b: list[int], q: int) -> list[int]:
    a, b = trim([x % q for x in a]), trim([x % q for x in b])
    assert b
    while len(a) >= len(b):
        shift = len(a) - len(b)
        scale = a[-1] * pow(b[-1], -1, q) % q
        for i, coefficient in enumerate(b):
            a[shift + i] = (a[shift + i] - scale * coefficient) % q
        trim(a)
    return a


def gcd_monic(a: list[int], b: list[int], q: int) -> list[int]:
    a, b = trim(a[:]), trim(b[:])
    while b:
        a, b = b, remainder(a, b, q)
    return [x * pow(a[-1], -1, q) % q for x in a]


def irreducible_monic(f: list[int], q: int) -> bool:
    """Rabin's finite-field criterion, with explicit quotient arithmetic."""
    n = len(f) - 1
    assert n > 0 and f[-1] == 1
    x_mod = quotient_power([0, 1], 1, f, q)
    if quotient_power([0, 1], q ** n, f, q) != x_mod:
        return False
    prime_divisors = [p for p in range(2, n + 1)
                      if n % p == 0 and all(p % d for d in range(2, isqrt(p) + 1))]
    for p in prime_divisors:
        power = quotient_power([0, 1], q ** (n // p), f, q)
        diff = [(a - b) % q for a, b in zip(power, x_mod)]
        if gcd_monic(f, diff, q) != [1]:
            return False
    return True


def identity(n: int) -> list[list[int]]:
    return [[int(i == j) for j in range(n)] for i in range(n)]


def matmul(a: list[list[int]], b: list[list[int]], q: int) -> list[list[int]]:
    n = len(a)
    return [[sum(a[i][k] * b[k][j] for k in range(n)) % q
             for j in range(n)] for i in range(n)]


def matadd(a: list[list[int]], b: list[list[int]], q: int) -> list[list[int]]:
    return [[(x + y) % q for x, y in zip(row_a, row_b)]
            for row_a, row_b in zip(a, b)]


def matpoly(coefficients: list[int], m: list[list[int]], q: int) -> list[list[int]]:
    n = len(m)
    power = identity(n)
    out = [[0] * n for _ in range(n)]
    for coefficient in coefficients:
        out = matadd(out, [[coefficient * x % q for x in row] for row in power], q)
        power = matmul(power, m, q)
    return out


def kernel_basis(a: list[list[int]], q: int) -> list[list[int]]:
    rows = [row[:] for row in a]
    n = len(rows)
    pivots = []
    for col in range(n):
        pivot = next((i for i in range(len(pivots), n) if rows[i][col] % q), None)
        if pivot is None:
            continue
        rank = len(pivots)
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inverse = pow(rows[rank][col], -1, q)
        rows[rank] = [x * inverse % q for x in rows[rank]]
        for i in range(n):
            if i == rank:
                continue
            scale = rows[i][col]
            rows[i] = [(x - scale * y) % q for x, y in zip(rows[i], rows[rank])]
        pivots.append(col)
    basis = []
    for free in range(n):
        if free in pivots:
            continue
        v = [0] * n
        v[free] = 1
        for r, pivot in enumerate(pivots):
            v[pivot] = -rows[r][free] % q
        assert all(sum(x * y for x, y in zip(row, v)) % q == 0 for row in a)
        basis.append(v)
    return basis


def rank_vectors(vectors: list[list[int]], q: int) -> int:
    if not vectors:
        return 0
    n = len(vectors[0])
    rows = [v[:] for v in vectors]
    rank = 0
    for col in range(n):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][col] % q), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inverse = pow(rows[rank][col], -1, q)
        rows[rank] = [x * inverse % q for x in rows[rank]]
        for i in range(rank + 1, len(rows)):
            scale = rows[i][col]
            rows[i] = [(x - scale * y) % q for x, y in zip(rows[i], rows[rank])]
        rank += 1
    return rank


def matvec(a: list[list[int]], v: list[int], q: int) -> list[int]:
    return [sum(x * y for x, y in zip(row, v)) % q for row in a]


def read_archived(cell: str) -> tuple[dict, str]:
    path = RUN / "work" / (cell + ".out.json")
    text = path.read_text()
    payload = text.split("RESULT_JSON_BEGIN\n", 1)[1].split("\nRESULT_JSON_END", 1)[0]
    return json.loads(payload), digest(path)


def matrix_checks(frob: list[list[int]], q: int, factors: list[list[int]],
                  expected_dimensions: list[int]) -> tuple[dict, dict]:
    """Apply the C5 order, factor-kernel, trace, and fixed-line gates to a matrix."""
    n = len(frob)
    trace = matpoly([1] * n, frob, q)
    power = identity(n)
    for _ in range(n):
        power = matmul(power, frob, q)
    kernels = [kernel_basis(matpoly(f, frob, q), q) for f in factors]
    dimensions = [len(k) for k in kernels]
    vectors = [v for kernel in kernels for v in kernel]
    sum_dimension = rank_vectors(vectors, q)
    trace_dimension = len(kernel_basis(trace, q))
    fixed = kernel_basis(matpoly([q - 1, 1], frob, q), q)
    checks = {
        "fifth_power_identity": power == identity(n),
        "factor_kernel_dimensions": dimensions == expected_dimensions,
        "direct_sum": sum_dimension == sum(dimensions),
        "trace_kernel_dimension": trace_dimension == n - 1,
        "factor_sum_equals_trace_kernel": (
            sum_dimension == trace_dimension
            and all(matvec(trace, v, q) == [0] * n for v in vectors)
        ),
        "fixed_kernel_dimension": len(fixed) == 1,
        "fixed_line_exclusion": any(matvec(trace, v, q) != [0] * n for v in fixed),
    }
    return checks, {
        "dimensions": dimensions, "sum_dimension": sum_dimension,
        "trace_dimension": trace_dimension, "fixed_dimension": len(fixed),
    }


def check_cell(cell: str, config: dict) -> dict:
    q, g, factors = config["q"], config["g"], config["factors"]
    n = len(g) - 1
    archived, archived_hash = read_archived(cell)
    assert archived["cell"] == cell and archived["q"] == q and archived["n"] == n
    assert archived["field_modulus"] == config["g_string"]
    assert archived["factorisation"]["atomic_factors"] == config["factor_strings"]
    assert archived["factorisation"]["squarefree"] is True
    assert archived["factorisation"]["all_exponents_1"] is True
    assert irreducible_monic(g, q)
    # The archived selector enumerates coefficient tuples constant-first.
    # Every earlier tuple with zero constant term has the root zero.
    assert g[0] == 1 and g[1:4] == [0, 0, 0]
    assert all(not irreducible_monic([1, 0, 0, 0, b, 1], q)
               for b in range(g[4]))
    assert all(irreducible_monic(f, q) for f in factors)
    product = [1]
    for f in [[q - 1, 1], *factors]:
        product = polynomial_mul(product, f, q)
    assert product == [q - 1, 0, 0, 0, 0, 1]
    cols = [quotient_power([0] * i + [1], q, g, q) for i in range(n)]
    frob = [[cols[j][i] for j in range(n)] for i in range(n)]
    checks, measurements = matrix_checks(frob, q, factors, config["expected_dimensions"])
    assert all(checks.values()), checks
    dimensions = measurements["dimensions"]
    sum_dimension = measurements["sum_dimension"]
    trace_dimension = measurements["trace_dimension"]
    flags = archived["C5"]
    expected = {
        "T_equals_hM": True,
        "dim_sum_nontrivial_kernels": n - 1,
        "dim_sum_via_addition": n - 1,
        "direct_sum_certified": True,
        "dim_ker_T": n - 1,
        "set_equality_sum_eq_kerT": True,
        "expected_dim_n_minus_1": n - 1,
        "dim_matches_n_minus_1": True,
        "dim_ker_x1": 1,
        "ker_x1_subset_kerT": False,
        "p_divides_n": False,
    }
    assert flags == expected
    changed = [row[:] for row in frob]
    changed[1][0] = (changed[1][0] + 1) % q
    changed_checks, _ = matrix_checks(changed, q, factors, config["expected_dimensions"])
    failed_checks = sorted(name for name, passed in changed_checks.items() if not passed)
    mutation_rejected = changed != frob and bool(failed_checks)
    assert mutation_rejected
    assert any(name in failed_checks for name in (
        "factor_kernel_dimensions", "direct_sum", "factor_sum_equals_trace_kernel"
    )), failed_checks
    return {
        "cell": cell, "q": q, "n": n, "field_modulus": config["g_string"],
        "archived_output_sha256": archived_hash, "frobenius_matrix": frob,
        "factor_kernel_dimensions": dimensions, "sum_dimension": sum_dimension,
        "trace_kernel_dimension": trace_dimension,
        "fixed_kernel_dimension": measurements["fixed_dimension"],
        "field_modulus_irreducible": True,
        "lexicographically_first_irreducible": True,
        "factors_irreducible": True,
        "factor_product_exact": True, "frobenius_order_divides_five": True,
        "factor_sum_equals_trace_kernel": True, "direct_sum": True,
        "matrix_mutation_rejected": mutation_rejected,
        "matrix_mutation_failed_checks": failed_checks,
    }


def main() -> None:
    if not __debug__:
        raise RuntimeError("C5 matrix validation requires Python assertions")
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Compare against committed receipt")
    args = parser.parse_args()
    fixtures_path = RUN / "fixtures.json"
    fixtures = json.loads(fixtures_path.read_text())
    specification_path = ROOT / "experiments/EXP-FROB-91ee9c/specification.yaml"
    assert fixtures["specification_sha256"] == digest(specification_path)
    for cell, config in CONFIG.items():
        assert fixtures["cells"][cell] == {
            "q": config["q"], "n": len(config["g"]) - 1,
            "field_modulus": config["g_string"],
        }
    receipt = {
        "fixtures_sha256": digest(fixtures_path),
        "specification_sha256": digest(specification_path),
        "schema": "frob-c5-source-bound-matrix-replay/v1",
        "source_run": "RUN-FROB-91ee9c-7119f2",
        "scope": "three frozen core cells; plain-Python matrix replay, not a Lean code refinement",
        "source_sha256": digest(Path(__file__)),
        "sage_core_sha256": digest(RUN / "work/core.py"),
        "sage_lattice_sha256": digest(RUN / "work/lattice.py"),
        "sage_driver_sha256": digest(RUN / "implementation.py"),
        "archived_checker_sha256": digest(RUN / "checker.py"),
        "cells": [check_cell(cell, config) for cell, config in CONFIG.items()],
    }
    encoded = json.dumps(receipt, sort_keys=True, indent=2) + "\n"
    if args.check:
        assert OUTPUT.read_bytes() == encoded.encode("utf-8"), "matrix replay receipt differs"
        print("byte-exact C5 matrix receipt match")
    else:
        assert not OUTPUT.exists(), "refusing to overwrite an existing receipt"
        OUTPUT.write_bytes(encoded.encode("utf-8"))
        print(OUTPUT)


if __name__ == "__main__":
    main()
