#!/usr/bin/env python3
"""Independent polynomial-quotient trace check for the frozen Frob C5 cells.

This is a successor *mathematical replay*. It does not identify the bytes loaded
by the original Sage process. The direct trace never uses a Frobenius matrix;
the matrix-polynomial side is computed only after that trace is complete.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


RUN = Path("experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2/work")
REPLAY = Path("docs/reports/2026-10-22-frob-c5-factor-kernels/c5-matrix-replay.json")
REPLAY_SHA256 = "22bcbdbdc6dd8c020456549cb1aa2edf887422cb10912105d9fa0508a6ee1005"
EXPECTED = {
    "FROB-SPLIT-q11n5": (11, 5, "x^5 + 2*x^4 + 1"),
    "FROB-NOLATTICE-q13n5": (13, 5, "x^5 + 8*x^4 + 1"),
    "FROB-EQDEG-q19n5": (19, 5, "x^5 + 3*x^4 + 1"),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def modulus_coeffs(text: str, q: int) -> list[int]:
    match = re.fullmatch(r"x\^5 \+ ([0-9]+)\*x\^4 \+ 1", text)
    if match is None:
        raise ValueError(f"unexpected modulus format: {text!r}")
    a = int(match.group(1))
    if not 0 < a < q:
        raise ValueError("invalid fourth-degree coefficient")
    return [1, 0, 0, 0, a, 1]


def product_mod(a: list[int], b: list[int], g: list[int], q: int) -> list[int]:
    """Convolve coefficient vectors, then perform ordinary monic long division."""
    n = len(g) - 1
    require(len(a) == len(b) == n and g[-1] == 1, "invalid quotient product inputs")
    coefficients = [0] * (2 * n - 1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            coefficients[i + j] = (coefficients[i + j] + ai * bj) % q
    for degree in range(2 * n - 2, n - 1, -1):
        lead = coefficients[degree]
        for j, gj in enumerate(g):
            coefficients[degree - n + j] = (
                coefficients[degree - n + j] - lead * gj
            ) % q
    return coefficients[:n]


def power_mod(a: list[int], exponent: int, g: list[int], q: int) -> list[int]:
    n = len(g) - 1
    result = [1] + [0] * (n - 1)
    while exponent:
        if exponent & 1:
            result = product_mod(result, a, g, q)
        a = product_mod(a, a, g, q)
        exponent >>= 1
    return result


def direct_trace_matrix(g: list[int], q: int) -> list[list[int]]:
    """Each column is the trace of one quotient basis element, via q powers."""
    n = len(g) - 1
    rows = [[0] * n for _ in range(n)]
    for col in range(n):
        term = [int(i == col) for i in range(n)]
        total = [0] * n
        for _ in range(n):
            total = [(x + y) % q for x, y in zip(total, term)]
            term = power_mod(term, q, g, q)
        for row in range(n):
            rows[row][col] = total[row]
    return rows


def mat_product(a: list[list[int]], b: list[list[int]], q: int) -> list[list[int]]:
    n = len(a)
    return [[sum(a[i][k] * b[k][j] for k in range(n)) % q
             for j in range(n)] for i in range(n)]


def mat_geometric_sum(m: list[list[int]], q: int) -> list[list[int]]:
    n = len(m)
    power = [[int(i == j) for j in range(n)] for i in range(n)]
    result = [[0] * n for _ in range(n)]
    for _ in range(n):
        result = [[(result[i][j] + power[i][j]) % q for j in range(n)]
                  for i in range(n)]
        power = mat_product(power, m, q)
    return result


def rank_mod(rows: list[list[int]], q: int) -> int:
    matrix = [row.copy() for row in rows]
    nrows, ncols = len(matrix), len(matrix[0])
    rank = 0
    for col in range(ncols):
        pivot = next((r for r in range(rank, nrows) if matrix[r][col] % q), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        inv = pow(matrix[rank][col], -1, q)
        matrix[rank] = [(inv * x) % q for x in matrix[rank]]
        for row in range(nrows):
            if row != rank:
                factor = matrix[row][col]
                matrix[row] = [(x - factor * y) % q for x, y in
                               zip(matrix[row], matrix[rank])]
        rank += 1
    return rank


def read_native(path: Path) -> dict:
    lines = path.read_text().splitlines()
    if len(lines) != 3 or lines[0] != "RESULT_JSON_BEGIN" or lines[2] != "RESULT_JSON_END":
        raise ValueError(f"unexpected native output envelope: {path}")
    return json.loads(lines[1])


def check_cell(root: Path, entry: dict) -> dict:
    cell = entry["cell"]
    q, n, modulus = EXPECTED[cell]
    require((entry["q"], entry["n"], entry["field_modulus"]) == (q, n, modulus),
            f"source-bound replay parameters changed: {cell}")
    native_path = root / RUN / f"{cell}.out.json"
    native_sha = sha256(native_path)
    require(native_sha == entry["archived_output_sha256"], f"native output hash changed: {cell}")
    native = read_native(native_path)
    require((native["cell"], native["q"], native["n"], native["field_modulus"]) ==
            (cell, q, n, modulus), f"native parameters changed: {cell}")
    g = modulus_coeffs(modulus, q)
    trace = direct_trace_matrix(g, q)
    matrix = entry["frobenius_matrix"]
    require(len(matrix) == n and all(len(row) == n for row in matrix),
            f"bad matrix shape: {cell}")
    require(all(0 <= v < q for row in matrix for v in row),
            f"bad matrix entry: {cell}")
    polynomial_trace = mat_geometric_sum(matrix, q)
    trace_rank = rank_mod(trace, q)
    require(trace == polynomial_trace, f"direct trace differs from h(M): {cell}")
    require(trace_rank == 1 and n - trace_rank == native["C5"]["dim_ker_T"],
            f"direct trace dimension disagrees: {cell}")
    require(all(all(v == 0 for v in row) for row in trace[1:]),
            f"direct trace does not land in the base field: {cell}")
    return {
        "cell": cell,
        "q": q,
        "n": n,
        "field_modulus": modulus,
        "native_output_sha256": native_sha,
        "direct_repeated_q_power_trace_rows": trace,
        "source_bound_matrix_polynomial_trace_rows": polynomial_trace,
        "direct_equals_h_of_source_bound_matrix": True,
        "direct_trace_rank": trace_rank,
        "direct_trace_nullity": n - trace_rank,
        "archived_T_equals_hM_flag": native["C5"]["T_equals_hM"],
    }


def run(root: Path) -> dict:
    replay_path = root / REPLAY
    require(sha256(replay_path) == REPLAY_SHA256, "source-bound replay hash changed")
    replay = json.loads(replay_path.read_text())
    entries = {entry["cell"]: entry for entry in replay["cells"]}
    require(set(entries) == set(EXPECTED), "source-bound replay cell set changed")
    results = [check_cell(root, entries[cell]) for cell in EXPECTED]
    q13 = entries["FROB-NOLATTICE-q13n5"]
    mutant = [row.copy() for row in q13["frobenius_matrix"]]
    require(mutant[1][1] == 2, "q13 mutation control lost its fixed original entry")
    mutant[1][1] = 3
    q13_trace = results[1]["direct_repeated_q_power_trace_rows"]
    require(mat_geometric_sum(mutant, 13) != q13_trace,
            "q13 matrix mutation was not detected by the independent trace")
    return {
        "schema": "crypto.validation.frob_c5_direct_trace.v1",
        "scope": "replacement mathematical replay; not original Sage process custody",
        "source_bound_replay_path": REPLAY.as_posix(),
        "source_bound_replay_sha256": sha256(replay_path),
        "cells": results,
        "q13_matrix_mutation": {
            "entry_zero_based": [1, 1],
            "original": 2,
            "mutated": 3,
            "direct_trace_equals_h_of_mutant": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.repo_root.resolve())
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("PASS: 3 exact frozen cells; direct repeated-q-power trace equals h(M); q13 mutation rejected")


if __name__ == "__main__":
    main()
