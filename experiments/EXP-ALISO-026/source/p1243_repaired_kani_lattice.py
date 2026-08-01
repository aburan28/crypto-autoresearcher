#!/usr/bin/env python3
"""Exact integral Kani block for the parity-repaired construction."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import sympy as sp
from sympy.matrices.normalforms import smith_normal_form
from sympy.polys.domains import ZZ as SYMPY_ZZ


ROOT = Path(__file__).resolve().parents[2]
INPUT = (
    ROOT
    / "experiments"
    / "ecdlp_isogeny"
    / "p1243_parity_repaired_kani_probe_result.json"
)
CONTRACT = (
    ROOT
    / "research"
    / "p1243_repaired_kani_lattice_contract_20260729.md"
)
OUTPUT = (
    ROOT
    / "experiments"
    / "ecdlp_isogeny"
    / "p1243_repaired_kani_lattice_result.json"
)


def valuation(value: int, prime: int) -> int:
    exponent = 0
    while value % prime == 0:
        exponent += 1
        value //= prime
    return exponent


def prime_factors(value: int) -> list[int]:
    factors = []
    candidate = 2
    while candidate * candidate <= value:
        if value % candidate == 0:
            factors.append(candidate)
            while value % candidate == 0:
                value //= candidate
        candidate += 1 if candidate == 2 else 2
    if value > 1:
        factors.append(value)
    return factors


def symplectic_form(copies: int) -> sp.Matrix:
    J = sp.Matrix([[0, 1], [-1, 0]])
    return sp.diag(*([J] * copies))


def audit_family(row: dict[str, object]) -> dict[str, object]:
    m = int(row["m"])
    c = int(row["c3_repair"])
    d = int(row["d"])
    n1 = int(row["n1"])
    n = n1 * m
    degree = c * m * d
    x, y = map(int, row["difference_representation"])
    difference = n * n - degree

    A = sp.Matrix([[x, y], [-y, x]])
    identity2 = sp.eye(2)
    action = sp.diag(degree, 1)
    dual_action = sp.diag(1, degree)
    top_left = sp.kronecker_product(A, identity2)
    top_right = sp.kronecker_product(sp.eye(2), dual_action)
    bottom_left = sp.kronecker_product(sp.eye(2), action)
    bottom_right = -sp.kronecker_product(A.T, identity2)
    block = top_left.row_join(top_right).col_join(
        bottom_left.row_join(bottom_right)
    )
    omega = symplectic_form(4)
    adjoint = -omega * block.T * omega
    smith = smith_normal_form(block, domain=SYMPY_ZZ)
    smith_diagonal = [abs(int(smith[i, i])) for i in range(8)]
    expected_smith = [1] * 4 + [n * n] * 4

    mutated_A = A.copy()
    mutated_A[0, 0] += 1
    mutated_top_left = sp.kronecker_product(mutated_A, identity2)
    mutated_bottom_right = -sp.kronecker_product(
        mutated_A.T, identity2
    )
    mutated_block = mutated_top_left.row_join(top_right).col_join(
        bottom_left.row_join(mutated_bottom_right)
    )
    repair_primes = [
        prime
        for prime in prime_factors(c)
        if prime % 4 == 3
    ]
    valuation_rows = [
        {
            "ell": prime,
            "v_m": valuation(m, prime),
            "v_D": valuation(degree, prime),
            "v_n": valuation(n, prime),
            "v_n_squared": valuation(n * n, prime),
            "extra_valuation_absorbed": (
                valuation(degree, prime)
                == valuation(m, prime) + 1
                and valuation(degree, prime)
                <= valuation(n * n, prime)
            ),
        }
        for prime in repair_primes
    ]
    gates = {
        "norm_difference": x * x + y * y == difference,
        "action_dual_identity": (
            dual_action * action == degree * identity2
        ),
        "adjoint_similitude": (
            adjoint * block == n * n * sp.eye(8)
        ),
        "polarization_similitude": (
            block.T * omega * block == n * n * omega
        ),
        "determinant": abs(int(block.det())) == n**8,
        "smith_form": smith_diagonal == expected_smith,
        "torsion_action_kernel_size": math.gcd(degree, n) == m,
        "all_extra_valuations_absorbed": all(
            item["extra_valuation_absorbed"]
            for item in valuation_rows
        ),
        "mutated_A_rejected": (
            mutated_block.T * omega * mutated_block
            != n * n * omega
        ),
        "mutated_degree_rejected": (
            x * x + y * y != n * n - (degree + 1)
        ),
        "degree_noninvertible_mod_n": math.gcd(degree, n) > 1,
    }
    return {
        "name": row["name"],
        "m": m,
        "c": c,
        "d": d,
        "n1": n1,
        "n": n,
        "degree_D": degree,
        "difference": difference,
        "two_square_representation": [x, y],
        "gcd_D_n": math.gcd(degree, n),
        "determinant": str(abs(int(block.det()))),
        "expected_determinant": str(n**8),
        "smith_diagonal": smith_diagonal,
        "repair_valuations": valuation_rows,
        "gates": gates,
    }


def main() -> None:
    source = json.loads(INPUT.read_text())
    if not source.get("all_pass"):
        raise RuntimeError("arithmetic source result is not passing")
    rows = [audit_family(row) for row in source["families"]]
    scientific = {
        "schema": "p1243-repaired-kani-lattice-v1",
        "claim_status": (
            "RESTRICTED LATTICE THEOREM / EXACT COMPUTATIONAL CHECK / "
            "NO ABELIAN-VARIETY ISOGENY"
        ),
        "families": rows,
    }
    blob = json.dumps(
        scientific, sort_keys=True, separators=(",", ":")
    ).encode()
    result = {
        **scientific,
        "all_pass": all(
            all(row["gates"].values()) for row in rows
        ),
        "scientific_data_sha256": hashlib.sha256(blob).hexdigest(),
        "artifact_hashes": {
            "input_sha256": hashlib.sha256(INPUT.read_bytes()).hexdigest(),
            "contract_sha256": hashlib.sha256(
                CONTRACT.read_bytes()
            ).hexdigest(),
            "source_sha256": hashlib.sha256(
                Path(__file__).read_bytes()
            ).hexdigest(),
        },
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["all_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
