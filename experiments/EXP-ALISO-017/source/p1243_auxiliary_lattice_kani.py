#!/usr/bin/env python3
"""Exact auxiliary-lattice Kani preflight over binary ideal norm forms."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import sympy as sp
from sympy.matrices.normalforms import smith_normal_form
from sympy.ntheory.modular import crt
from sympy.ntheory.residue_ntheory import sqrt_mod


HERE = Path(__file__).resolve().parent
INPUT = HERE / "p1243_parity_repaired_kani_probe_result.json"
OUTPUT = HERE / "p1243_auxiliary_lattice_kani_result.json"
CONTRACT = (
    HERE.parent.parent
    / "research"
    / "p1243_auxiliary_lattice_kani_contract_20260729.md"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def factor(n: int) -> dict[int, int]:
    return {int(p): int(e) for p, e in sp.factorint(int(n)).items()}


def is_sum_two_squares(n: int) -> bool:
    return all(
        p % 4 != 3 or e % 2 == 0 for p, e in factor(n).items()
    )


def smith_diagonal(matrix: sp.Matrix) -> list[int]:
    diagonal = smith_normal_form(matrix, domain=sp.ZZ)
    return [
        abs(int(diagonal[index, index]))
        for index in range(min(diagonal.rows, diagonal.cols))
    ]


def block_diag(*blocks: sp.Matrix) -> sp.Matrix:
    return sp.diag(*blocks)


def matrix_rows(matrix: sp.Matrix) -> list[list[int]]:
    return [
        [int(matrix[row, column]) for column in range(matrix.cols)]
        for row in range(matrix.rows)
    ]


def split_discriminant(delta: int, primes: list[int]) -> bool:
    discriminant = -int(delta)
    for prime in primes:
        if prime == 2:
            if discriminant % 8 != 1:
                return False
        elif int(sp.kronecker_symbol(discriminant, prime)) != 1:
            return False
    return True


def find_auxiliary_delta(
    n: int, degree: int, norm: int, maximum: int = 200_000
) -> tuple[int, int]:
    primes = sorted(factor(norm))
    trials = 0
    for delta in range(7, maximum + 1, 8):
        if sp.isprime(delta):
            if math.gcd(delta, n * degree * norm) != 1:
                continue
            trials += 1
            if split_discriminant(delta, primes):
                return delta, trials
    raise RuntimeError("no auxiliary splitting discriminant in search range")


def root_order_polynomial(
    discriminant: int, norm: int
) -> tuple[int, list[dict[str, int]]]:
    c = (1 - discriminant) // 4
    moduli = []
    roots = []
    reports = []
    for prime, exponent in sorted(factor(norm).items()):
        modulus = prime**exponent
        if prime == 2:
            candidates = [
                value
                for value in range(modulus)
                if (value * value - value + c) % modulus == 0
            ]
        else:
            square_roots = sqrt_mod(
                discriminant % modulus, modulus, all_roots=True
            )
            inverse_two = pow(2, -1, modulus)
            candidates = sorted(
                {
                    int((1 + int(root)) * inverse_two % modulus)
                    for root in square_roots
                }
            )
        if not candidates:
            raise RuntimeError(
                f"order polynomial has no root modulo {prime}^{exponent}"
            )
        root = int(candidates[0])
        moduli.append(modulus)
        roots.append(root)
        reports.append(
            {
                "prime": prime,
                "exponent": exponent,
                "modulus": modulus,
                "root": root,
                "root_count": len(candidates),
                "polynomial_zero": (
                    (root * root - root + c) % modulus == 0
                ),
            }
        )
    combined, combined_modulus = crt(moduli, roots)
    if int(combined_modulus) != norm:
        raise RuntimeError("CRT modulus does not equal ideal norm")
    return int(combined), reports


def exact_divide_matrix(matrix: sp.Matrix, divisor: int) -> sp.Matrix:
    entries = []
    for value in matrix:
        numerator = int(value)
        if numerator % divisor:
            raise RuntimeError("nonintegral normalized ideal Gram matrix")
        entries.append(numerator // divisor)
    return sp.Matrix(matrix.rows, matrix.cols, entries)


def scientific_hash(payload: dict) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(
        "ascii"
    )
    return hashlib.sha256(encoded).hexdigest()


def run_family(family: dict) -> dict:
    m = int(family["m"])
    d = int(family["d"])
    n1 = int(family["n1"])
    n = n1 * m
    degree = m * d
    norm = n * n - degree
    delta, trials = find_auxiliary_delta(n, degree, norm)
    discriminant = -delta
    root, split_reports = root_order_polynomial(discriminant, norm)
    coefficient_c = (1 - discriminant) // 4

    inclusion = sp.Matrix([[norm, -root], [0, 1]])
    gram_order = sp.Matrix([[2, 1], [1, 2 * coefficient_c]])
    gram_ideal = exact_divide_matrix(
        inclusion.T * gram_order * inclusion, norm
    )
    adjoint = exact_divide_matrix(
        gram_ideal.adjugate()
        * inclusion.T
        * gram_order,
        int(gram_ideal.det()),
    )

    identity2 = sp.eye(2)
    symplectic2 = sp.Matrix([[0, 1], [-1, 0]])
    action = sp.diag(degree, 1)
    dual_action = sp.diag(1, degree)

    top_left = sp.kronecker_product(inclusion, identity2)
    top_right = sp.kronecker_product(identity2, dual_action)
    bottom_left = sp.kronecker_product(identity2, action)
    bottom_right = -sp.kronecker_product(adjoint, identity2)
    kani = top_left.row_join(top_right).col_join(
        bottom_left.row_join(bottom_right)
    )

    omega_in = block_diag(
        sp.kronecker_product(gram_ideal, symplectic2),
        sp.kronecker_product(gram_order, symplectic2),
    )
    omega_out = block_diag(
        sp.kronecker_product(gram_order, symplectic2),
        sp.kronecker_product(gram_ideal, symplectic2),
    )

    target_smith = [1, 1, 1, 1] + [n * n] * 4
    kani_smith = smith_diagonal(kani)
    gram_order_smith = smith_diagonal(gram_order)
    gram_ideal_smith = smith_diagonal(gram_ideal)

    local_kernel_reports = []
    for prime in sorted(factor(n)):
        modular_matrix = sp.polys.matrices.DomainMatrix.from_Matrix(kani).convert_to(
            sp.GF(prime)
        )
        modular_rank = int(modular_matrix.rank())
        local_kernel_reports.append(
            {
                "prime": prime,
                "modular_rank": modular_rank,
                "kernel_dimension": 8 - modular_rank,
            }
        )

    mutated_inclusion = inclusion.copy()
    mutated_inclusion[0, 0] += 1
    mutated_gram = gram_ideal.copy()
    mutated_gram[0, 0] += 1
    mutated_degree = degree + 1
    mutated_action = sp.diag(mutated_degree, 1)
    mutated_bottom_left = sp.kronecker_product(identity2, mutated_action)
    mutated_kani = top_left.row_join(top_right).col_join(
        mutated_bottom_left.row_join(bottom_right)
    )

    gates = {
        "positive_norm": norm > 0,
        "auxiliary_discriminant_fundamental": (
            delta % 8 == 7 and bool(sp.isprime(delta))
        ),
        "auxiliary_discriminant_coprime": (
            math.gcd(delta, n * degree * norm) == 1
        ),
        "all_prime_powers_split": all(
            report["polynomial_zero"] for report in split_reports
        ),
        "ideal_norm": abs(int(inclusion.det())) == norm,
        "gram_order_integral": all(value.q == 1 for value in gram_order),
        "gram_ideal_integral": all(value.q == 1 for value in gram_ideal),
        "gram_determinants": (
            int(gram_order.det()) == delta
            and int(gram_ideal.det()) == delta
        ),
        "gram_order_type": gram_order_smith == [1, delta],
        "gram_ideal_type": gram_ideal_smith == [1, delta],
        "ideal_similitude": (
            inclusion.T * gram_order * inclusion == norm * gram_ideal
        ),
        "adjoint_integral": all(value.q == 1 for value in adjoint),
        "adjoint_left": adjoint * inclusion == norm * identity2,
        "adjoint_right": inclusion * adjoint == norm * identity2,
        "typed_polarization": (
            kani.T * omega_out * kani == n * n * omega_in
        ),
        "determinant": abs(int(kani.det())) == n**8,
        "smith_form": kani_smith == target_smith,
    }
    mutations = {
        "inclusion_mutation_rejected": (
            mutated_inclusion.T * gram_order * mutated_inclusion
            != norm * gram_ideal
        ),
        "gram_mutation_rejected": (
            kani.T
            * block_diag(
                sp.kronecker_product(gram_order, symplectic2),
                sp.kronecker_product(mutated_gram, symplectic2),
            )
            * kani
            != n * n * omega_in
        ),
        "degree_mutation_rejected": (
            mutated_kani.T * omega_out * mutated_kani != n * n * omega_in
        ),
        "inert_discriminant_rejected": not split_discriminant(
            3,
            [
                prime
                for prime in sorted(factor(norm))
                if prime != 3
            ],
        )
        if any(
            int(sp.kronecker_symbol(-3, prime)) != 1
            for prime in factor(norm)
            if prime not in (2, 3)
        )
        else True,
    }
    return {
        "name": family["name"],
        "m": m,
        "d": d,
        "n1": n1,
        "n": n,
        "degree_eta": degree,
        "auxiliary_norm": norm,
        "integer_sum_two_squares": is_sum_two_squares(norm),
        "auxiliary_delta": delta,
        "auxiliary_discriminant": discriminant,
        "auxiliary_search_trials": trials,
        "ideal_root": root,
        "split_prime_powers": split_reports,
        "inclusion_matrix": matrix_rows(inclusion),
        "ideal_adjoint_matrix": matrix_rows(adjoint),
        "gram_order": matrix_rows(gram_order),
        "gram_ideal": matrix_rows(gram_ideal),
        "gram_order_smith": gram_order_smith,
        "gram_ideal_smith": gram_ideal_smith,
        "kani_smith": kani_smith,
        "local_kernel_reports": local_kernel_reports,
        "gates": gates,
        "mutations": mutations,
        "pass": all(gates.values()) and all(mutations.values()),
    }


def main() -> None:
    source = json.loads(INPUT.read_text())
    rows = [run_family(family) for family in source["families"]]
    rescued = [
        row["name"]
        for row in rows
        if not row["integer_sum_two_squares"] and row["pass"]
    ]
    all_pass = all(row["pass"] for row in rows) and bool(rescued)
    scientific = {
        "claim_status": (
            "EXACT AUXILIARY-LATTICE PREFLIGHT / "
            "NO PRINCIPALIZATION THEOREM / NO GEOMETRIC ISOGENY"
        ),
        "rows": rows,
        "rescued_integer_two_square_failures": rescued,
        "all_pass": all_pass,
    }
    result = {
        "schema": "p1243-auxiliary-lattice-kani-v1",
        **scientific,
        "artifact_hashes": {
            "input_sha256": sha256(INPUT),
            "contract_sha256": sha256(CONTRACT),
            "source_sha256": sha256(Path(__file__).resolve()),
        },
        "scientific_data_sha256": scientific_hash(scientific),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not all_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
