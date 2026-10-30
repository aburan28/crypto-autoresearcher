#!/usr/bin/env python3
"""Independent exact arithmetic of an isolated quotient-ring statement.

No third-party libraries, repository imports, randomized trials, or external
executables. Vectors are columns, coefficients in ascending powers of x.
"""
import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

EXPECTED_SHA256 = "17ba164feb8a59ba91346448befaf8ca56e8318de2cc53d6f950a377cbff45e2"


def trim(a):
    a = list(a)
    while a and a[-1] == 0:
        a.pop()
    return a


def remainder(a, b, q):
    a, b = trim(a), trim(b)
    assert b
    inv = pow(b[-1], -1, q)
    while len(a) >= len(b):
        shift = len(a) - len(b)
        scale = a[-1] * inv % q
        for j, coefficient in enumerate(b):
            a[shift + j] = (a[shift + j] - scale * coefficient) % q
        a = trim(a)
    return a


def gcd_polynomial(a, b, q):
    a, b = trim(a), trim(b)
    while b:
        a, b = b, remainder(a, b, q)
    if not a:
        return []
    scale = pow(a[-1], -1, q)
    return [(scale * coefficient) % q for coefficient in a]


class Quotient:
    def __init__(self, q, g):
        self.q, self.g, self.n = q, g, len(g) - 1
        assert g[-1] == 1

    def add(self, a, b):
        return [(x + y) % self.q for x, y in zip(a, b)]

    def subtract(self, a, b):
        return [(x - y) % self.q for x, y in zip(a, b)]

    def multiply(self, a, b):
        # Schoolbook polynomial multiplication followed by monic reduction.
        c = [0] * (2 * self.n - 1)
        for i, ai in enumerate(a):
            for j, bj in enumerate(b):
                c[i + j] = (c[i + j] + ai * bj) % self.q
        for degree in range(len(c) - 1, self.n - 1, -1):
            scale = c[degree]
            for k in range(self.n + 1):
                at = degree - self.n + k
                c[at] = (c[at] - scale * self.g[k]) % self.q
        assert not any(c[self.n:])
        return c[:self.n]

    def power(self, a, exponent):
        result = [1] + [0] * (self.n - 1)
        while exponent:
            if exponent & 1:
                result = self.multiply(result, a)
            a = self.multiply(a, a)
            exponent >>= 1
        return result


def columns_to_rows(columns):
    return [list(row) for row in zip(*columns)]


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def matrix_add(a, b, q):
    return [[(x + y) % q for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def matrix_multiply(a, b, q):
    n = len(a)
    return [[sum(a[i][k] * b[k][j] for k in range(n)) % q
             for j in range(n)] for i in range(n)]


def matrix_rank(a, q):
    a = [row[:] for row in a]
    pivot_row = 0
    for column in range(len(a[0])):
        pivot = next((i for i in range(pivot_row, len(a)) if a[i][column]), None)
        if pivot is None:
            continue
        a[pivot_row], a[pivot] = a[pivot], a[pivot_row]
        inv = pow(a[pivot_row][column], -1, q)
        a[pivot_row] = [v * inv % q for v in a[pivot_row]]
        for i in range(len(a)):
            if i != pivot_row:
                scale = a[i][column]
                a[i] = [(x - scale * y) % q
                        for x, y in zip(a[i], a[pivot_row])]
        pivot_row += 1
        if pivot_row == len(a):
            break
    return pivot_row, a


def analyze(matrix, q):
    rank, rref = matrix_rank(matrix, q)
    in_base_line = not any(value for row in matrix[1:] for value in row)
    return {"matrix_rows": matrix, "rank": rank, "nullity": len(matrix) - rank,
            "image_in_base_field_line": in_base_line,
            "image_equals_base_field_line": in_base_line and rank == 1,
            "rref_rows": rref}


def direct_trace(ring, terms):
    # Each column is independently exponentiated at exponents 1,q,...,q^(m-1).
    columns = []
    for j in range(ring.n):
        basis = [int(k == j) for k in range(ring.n)]
        column = [0] * ring.n
        for i in range(terms):
            column = ring.add(column, ring.power(basis, ring.q ** i))
        columns.append(column)
    return columns_to_rows(columns)


def is_prime(q):
    return q >= 2 and all(q % d for d in range(2, int(q ** 0.5) + 1))


def review_cell(cell):
    q, n, g = cell["q"], cell["n"], cell["modulus_coefficients_low_to_high"]
    assert is_prime(q) and n == 5 and len(g) == n + 1
    ring = Quotient(q, g)
    x = [0, 1, 0, 0, 0]
    one = [1, 0, 0, 0, 0]

    # Frobenius columns use successive ordinary powers of x^q, a different
    # assembly from independent exponentiation of each trace basis column.
    xq = ring.power(x, q)
    f_columns = [one]
    for _ in range(1, n):
        f_columns.append(ring.multiply(f_columns[-1], xq))
    f = columns_to_rows(f_columns)
    assert f == columns_to_rows([ring.power([int(k == j) for k in range(n)], q)
                                for j in range(n)])
    f_powers = [identity(n)]
    for _ in range(n):
        f_powers.append(matrix_multiply(f_powers[-1], f, q))
    five_sum = [[0] * n for _ in range(n)]
    for power in f_powers[:n]:
        five_sum = matrix_add(five_sum, power, q)
    five_direct = direct_trace(ring, n)

    # Rabin irreducibility criterion for prime degree 5: x^(q^5)=x mod g
    # and gcd(g, x^q-x)=1. No irreducibility assumption is used above.
    xq_minus_x = ring.subtract(xq, x)
    xq5_minus_x = ring.subtract(ring.power(x, q ** n), x)
    gcd = gcd_polynomial(g, xq_minus_x, q)
    irreducible = gcd == [1] and not any(xq5_minus_x)
    assert five_direct == five_sum
    result = {"id": cell["id"], "q": q, "n": n,
              "modulus_coefficients_low_to_high": g,
              "frobenius": analyze(f, q),
              "frobenius_powers_rows_0_through_5": f_powers,
              "five_term_direct": analyze(five_direct, q),
              "five_term_matrix_sum_rows": five_sum,
              "direct_equals_matrix_sum": five_direct == five_sum,
              "frobenius_fifth_power_is_identity": f_powers[5] == identity(n),
              "rabin_irreducibility": {"gcd_g_xq_minus_x": gcd,
                                       "xq5_minus_x_mod_g": xq5_minus_x,
                                       "irreducible": irreducible}}
    if q == 13:
        four_sum = [[0] * n for _ in range(n)]
        for power in f_powers[:4]:
            four_sum = matrix_add(four_sum, power, q)
        four_direct = direct_trace(ring, 4)
        assert four_direct == four_sum
        witness_column = next(j for j in range(n)
                              if any(four_direct[i][j] for i in range(1, n)))
        result["wrong_length_four_term_control"] = {
            **analyze(four_direct, q), "matrix_sum_rows": four_sum,
            "direct_equals_matrix_sum": four_direct == four_sum,
            "nonconstant_witness_basis_index": witness_column,
            "nonconstant_witness_image_coefficients": [row[witness_column]
                                                       for row in four_direct],
            "same_rank_and_image_claims_hold": False}
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--statement", required=True)
    parser.add_argument("--results", required=True)
    parser.add_argument("--runtime", required=True)
    args = parser.parse_args()
    started = time.time()
    start_counter = time.perf_counter()
    raw = Path(args.statement).read_bytes()
    actual_hash = hashlib.sha256(raw).hexdigest()
    if actual_hash != EXPECTED_SHA256:
        raise SystemExit("Statement hash mismatch")
    statement = json.loads(raw)
    assert statement["schema"] == "frob.c5.blind_statement.v1"
    result = {"schema": "frob.c5.blind_exact_review.v1",
              "statement_path": args.statement, "statement_sha256": actual_hash,
              "matrix_convention": "Rows printed; input and output coefficient vectors are columns in (1,x,x^2,x^3,x^4).",
              "method": "Exact modular polynomial arithmetic and Gaussian elimination; deterministic finite checks, no scientific trials.",
              "cells": [review_cell(cell) for cell in statement["cells"]]}
    result["verdict"] = "PASS five-term arithmetic; REJECT wrong-length four-term q=13 control"
    for cell in result["cells"]:
        assert cell["five_term_direct"]["rank"] == 1
        assert cell["five_term_direct"]["nullity"] == 4
        assert cell["five_term_direct"]["image_equals_base_field_line"]
        assert cell["rabin_irreducibility"]["irreducible"]
        if cell["q"] == 13:
            assert cell["wrong_length_four_term_control"]["rank"] == 5
            assert not cell["wrong_length_four_term_control"]["image_in_base_field_line"]
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    Path(args.results).write_text(encoded)
    print(encoded, end="")
    runtime = {"schema": "frob.c5.blind_runtime.v1", "argv": sys.argv,
               "python": sys.version, "platform": platform.platform(),
               "started_unix_seconds": started,
               "finished_unix_seconds": time.time(),
               "wall_seconds": time.perf_counter() - start_counter,
               "classification": "Local exact arithmetic runtime only; no performance claim or comparison."}
    Path(args.runtime).write_text(json.dumps(runtime, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
