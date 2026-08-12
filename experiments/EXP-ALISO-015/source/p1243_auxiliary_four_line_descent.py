#!/usr/bin/env python3
"""Exact four-line descent for principalized auxiliary Kani lattices."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import sympy as sp
from sympy.matrices.normalforms import smith_normal_form


HERE = Path(__file__).resolve().parent
INPUT = HERE / "p1243_auxiliary_lattice_kani_result.json"
OUTPUT = HERE / "p1243_auxiliary_four_line_descent_result.json"
CONTRACT = (
    HERE.parent.parent
    / "research"
    / "p1243_auxiliary_four_line_descent_contract_20260729.md"
)
ACTION_PARAMETERS = ((1, 1, 1), (2, 3, 2), (3, 2, 4))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scientific_hash(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode(
        "ascii"
    )
    return hashlib.sha256(encoded).hexdigest()


def integral_matrix(matrix: sp.Matrix) -> bool:
    return all(sp.denom(value) == 1 for value in matrix)


def smith_diagonal(matrix: sp.Matrix) -> list[int]:
    diagonal = smith_normal_form(matrix, domain=sp.ZZ)
    return [
        abs(int(diagonal[index, index]))
        for index in range(min(diagonal.rows, diagonal.cols))
    ]


def kernel_vector(gram: sp.Matrix, prime: int) -> tuple[int, int]:
    a = int(gram[0, 0]) % prime
    b = int(gram[0, 1]) % prime
    vector = (b, -a % prime)
    if vector == (0, 0):
        c = int(gram[1, 1]) % prime
        vector = (c, -b % prime)
    product = gram * sp.Matrix(vector)
    if vector == (0, 0) or any(int(value) % prime for value in product):
        raise RuntimeError("bad modular Gram-kernel vector")
    return vector


def primitive_lift(vector: tuple[int, int], prime: int) -> tuple[int, int]:
    reduced = (vector[0] % prime, vector[1] % prime)
    for bound in range(6):
        for first_shift in range(-bound, bound + 1):
            for second_shift in range(-bound, bound + 1):
                lifted = (
                    reduced[0] + first_shift * prime,
                    reduced[1] + second_shift * prime,
                )
                if math.gcd(abs(lifted[0]), abs(lifted[1])) == 1:
                    return lifted
    raise RuntimeError("could not find primitive lift")


def egcd(a: int, b: int) -> tuple[int, int, int]:
    if b == 0:
        return (abs(a), 1 if a >= 0 else -1, 0)
    gcd_value, x1, y1 = egcd(b, a % b)
    return (gcd_value, y1, x1 - (a // b) * y1)


def second_column_alignment(vector: tuple[int, int]) -> sp.Matrix:
    v0, v1 = vector
    gcd_value, x, y = egcd(v1, -v0)
    if gcd_value != 1:
        raise RuntimeError("vector is not primitive")
    matrix = sp.Matrix([[x, v0], [y, v1]])
    if matrix.det() != 1:
        raise RuntimeError("failed second-column alignment")
    return matrix


def first_column_alignment(vector: tuple[int, int]) -> sp.Matrix:
    v0, v1 = vector
    gcd_value, x, y = egcd(v0, v1)
    if gcd_value != 1:
        raise RuntimeError("vector is not primitive")
    matrix = sp.Matrix([[v0, -y], [v1, x]])
    if matrix.det() != 1:
        raise RuntimeError("failed first-column alignment")
    return matrix


def quotient_map(
    gram: sp.Matrix, prime: int, line: tuple[int, int]
) -> tuple[sp.Matrix, sp.Matrix]:
    symplectic = sp.Matrix([[0, 1], [-1, 0]])
    multiplicity = second_column_alignment(
        primitive_lift(kernel_vector(gram, prime), prime)
    )
    tate = first_column_alignment(primitive_lift(line, prime))
    cyclic = sp.diag(prime, 1) * tate.inv()
    quotient = sp.diag(sp.eye(2), cyclic) * sp.kronecker_product(
        multiplicity.inv(), sp.eye(2)
    )
    old_form = sp.kronecker_product(gram, symplectic)
    principal = quotient.inv().T * old_form * quotient.inv()
    return quotient, principal


def action_matrix(degree: int, left: int, right: int) -> sp.Matrix:
    lower = sp.Matrix([[1, 0], [left, 1]])
    diagonal = sp.diag(degree, 1)
    upper = sp.Matrix([[1, right], [0, 1]])
    return lower * diagonal * upper


def line_image(
    matrix: sp.Matrix, line: tuple[int, int], prime: int
) -> tuple[int, int]:
    image = matrix * sp.Matrix(line)
    reduced = (int(image[0]) % prime, int(image[1]) % prime)
    if reduced == (0, 0):
        raise RuntimeError("invertible action killed a line")
    return reduced


def run_case(row: dict, parameters: tuple[int, int, int]) -> dict:
    left, right, slope = parameters
    prime = int(row["auxiliary_delta"])
    norm = int(row["auxiliary_norm"])
    degree = int(row["degree_eta"])
    n = int(row["n"])
    gram_a = sp.Matrix(row["gram_ideal"])
    gram_o = sp.Matrix(row["gram_order"])
    inclusion = sp.kronecker_product(
        sp.Matrix(row["inclusion_matrix"]), sp.eye(2)
    )
    adjoint = sp.kronecker_product(
        sp.Matrix(row["ideal_adjoint_matrix"]), sp.eye(2)
    )

    action = action_matrix(degree, left, right)
    dual_action = sp.Matrix(
        [[action[1, 1], -action[0, 1]], [-action[1, 0], action[0, 0]]]
    )
    eta = sp.kronecker_product(sp.eye(2), action)
    dual_eta = sp.kronecker_product(sp.eye(2), dual_action)

    source_line = (1, slope % prime)
    target_line = line_image(action, source_line, prime)
    pi_0a, omega_0a = quotient_map(gram_a, prime, source_line)
    pi_0o, omega_0o = quotient_map(gram_o, prime, source_line)
    pi_1a, omega_1a = quotient_map(gram_a, prime, target_line)
    pi_1o, omega_1o = quotient_map(gram_o, prime, target_line)

    abar_0 = pi_0o * inclusion * pi_0a.inv()
    eta_a = pi_1a * eta * pi_0a.inv()
    dual_eta_o = pi_0o * dual_eta * pi_1o.inv()
    adjoint_1 = pi_1a * adjoint * pi_1o.inv()

    kani = abar_0.row_join(dual_eta_o).col_join(
        eta_a.row_join(-adjoint_1)
    )
    omega_in = sp.diag(omega_0a, omega_1o)
    omega_out = sp.diag(omega_0o, omega_1a)
    pi_in = sp.diag(pi_0a, pi_1o)
    pi_out = sp.diag(pi_0o, pi_1a)
    old_kani = inclusion.row_join(dual_eta).col_join(
        eta.row_join(-adjoint)
    )

    wrong_target = ((target_line[0] + 1) % prime, target_line[1])
    if wrong_target == (0, 0):
        wrong_target = (target_line[0], (target_line[1] + 1) % prime)
    wrong_pi_1a, _ = quotient_map(gram_a, prime, wrong_target)
    wrong_eta = wrong_pi_1a * eta * pi_0a.inv()

    wrong_o_line = ((target_line[0] + 2) % prime, target_line[1])
    if wrong_o_line == (0, 0):
        wrong_o_line = (target_line[0], (target_line[1] + 2) % prime)
    wrong_pi_1o, _ = quotient_map(gram_o, prime, wrong_o_line)
    wrong_dual = pi_0o * dual_eta * wrong_pi_1o.inv()
    wrong_adjoint = pi_1a * adjoint * wrong_pi_1o.inv()

    mutated_kani = sp.Matrix(kani)
    mutated_kani[0, 0] += 1
    target_smith = [1, 1, 1, 1] + [n * n] * 4
    gates = {
        "action_determinant": action.det() == degree,
        "action_nondiagonal": action[0, 1] != 0 and action[1, 0] != 0,
        "dual_left": dual_action * action == degree * sp.eye(2),
        "dual_right": action * dual_action == degree * sp.eye(2),
        "all_principal_forms_integral": all(
            integral_matrix(form)
            for form in (omega_0a, omega_0o, omega_1a, omega_1o)
        ),
        "all_principal_forms_unimodular": all(
            abs(int(form.det())) == 1
            for form in (omega_0a, omega_0o, omega_1a, omega_1o)
        ),
        "all_four_blocks_integral": all(
            integral_matrix(block)
            for block in (abar_0, eta_a, dual_eta_o, adjoint_1)
        ),
        "kani_integral": integral_matrix(kani),
        "kani_polarization": kani.T * omega_out * kani == n * n * omega_in,
        "kani_determinant": abs(int(kani.det())) == n**8,
        "kani_smith": smith_diagonal(kani) == target_smith,
        "direct_conjugation": kani == pi_out * old_kani * pi_in.inv(),
    }
    mutations = {
        "wrong_eta_line_rejected": not integral_matrix(wrong_eta),
        "wrong_o_line_rejected": (
            not integral_matrix(wrong_dual)
            or not integral_matrix(wrong_adjoint)
        ),
        "kani_mutation_rejected": (
            mutated_kani.T * omega_out * mutated_kani
            != n * n * omega_in
        ),
    }
    return {
        "name": row["name"],
        "parameters": list(parameters),
        "delta": prime,
        "degree": degree,
        "source_line": list(source_line),
        "target_line": list(target_line),
        "gates": gates,
        "mutations": mutations,
        "pass": all(gates.values()) and all(mutations.values()),
    }


def main() -> None:
    source = json.loads(INPUT.read_text())
    rows = [
        run_case(row, parameters)
        for row in source["rows"]
        for parameters in ACTION_PARAMETERS
    ]
    scientific = {
        "claim_status": (
            "EXACT FOUR-LINE TATE-LATTICE DESCENT / "
            "NO GEOMETRIC QUOTIENT OR THETA EVALUATION"
        ),
        "rows": rows,
        "all_pass": all(row["pass"] for row in rows),
    }
    result = {
        "schema": "p1243-auxiliary-four-line-descent-v1",
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
    if not scientific["all_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
