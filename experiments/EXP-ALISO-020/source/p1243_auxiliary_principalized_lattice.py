#!/usr/bin/env python3
"""Exact principalization of the auxiliary Kani Tate lattices."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import sympy as sp
from sympy.matrices.normalforms import smith_normal_form


HERE = Path(__file__).resolve().parent
INPUT = HERE / "p1243_auxiliary_lattice_kani_result.json"
OUTPUT = HERE / "p1243_auxiliary_principalized_lattice_result.json"
CONTRACT = (
    HERE.parent.parent
    / "research"
    / "p1243_auxiliary_principalized_lattice_contract_20260729.md"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scientific_hash(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode(
        "ascii"
    )
    return hashlib.sha256(encoded).hexdigest()


def matrix_rows(matrix: sp.Matrix) -> list[list[int]]:
    return [
        [int(matrix[row, column]) for column in range(matrix.cols)]
        for row in range(matrix.rows)
    ]


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
    for bound in range(5):
        for first_shift in range(-bound, bound + 1):
            for second_shift in range(-bound, bound + 1):
                lifted = (
                    vector[0] + first_shift * prime,
                    vector[1] + second_shift * prime,
                )
                if math.gcd(abs(lifted[0]), abs(lifted[1])) == 1:
                    return lifted
    raise RuntimeError("could not find primitive kernel lift")


def alignment_matrix(vector: tuple[int, int]) -> sp.Matrix:
    v0, v1 = vector
    gcd_value, coefficient0, coefficient1 = sp.gcdex(v1, -v0)
    # SymPy versions disagree on gcdex tuple order. Verify and repair with
    # Python's extended Euclidean algorithm when necessary.
    candidates = [
        (int(coefficient0), int(coefficient1)),
        (int(gcd_value), int(coefficient0)),
    ]
    for w0, w1 in candidates:
        matrix = sp.Matrix([[w0, v0], [w1, v1]])
        if int(matrix.det()) == 1:
            return matrix

    def egcd(a: int, b: int) -> tuple[int, int, int]:
        if b == 0:
            return (abs(a), 1 if a >= 0 else -1, 0)
        g, x1, y1 = egcd(b, a % b)
        return (g, y1, x1 - (a // b) * y1)

    g, x, y = egcd(v1, -v0)
    if g != 1:
        raise RuntimeError("primitive lift did not have gcd one")
    matrix = sp.Matrix([[x, v0], [y, v1]])
    if int(matrix.det()) != 1:
        raise RuntimeError("failed to align primitive kernel vector")
    return matrix


def principalize(
    gram: sp.Matrix, prime: int
) -> tuple[sp.Matrix, sp.Matrix, sp.Matrix, tuple[int, int]]:
    symplectic2 = sp.Matrix([[0, 1], [-1, 0]])
    vector = primitive_lift(kernel_vector(gram, prime), prime)
    alignment = alignment_matrix(vector)
    quotient = sp.diag(1, 1, prime, 1) * sp.kronecker_product(
        alignment.inv(), sp.eye(2)
    )
    omega = sp.kronecker_product(gram, symplectic2)
    principal = quotient.inv().T * omega * quotient.inv()
    complement = prime * quotient.inv()
    return quotient, principal, complement, vector


def run_row(row: dict) -> dict:
    prime = int(row["auxiliary_delta"])
    norm = int(row["auxiliary_norm"])
    degree = int(row["degree_eta"])
    n = int(row["n"])
    inclusion = sp.Matrix(row["inclusion_matrix"])
    gram_a = sp.Matrix(row["gram_ideal"])
    gram_o = sp.Matrix(row["gram_order"])
    adjoint = sp.Matrix(row["ideal_adjoint_matrix"])

    pi_a, omega_a, comp_a, vector_a = principalize(gram_a, prime)
    pi_o, omega_o, comp_o, vector_o = principalize(gram_o, prime)
    inclusion_tate = sp.kronecker_product(inclusion, sp.eye(2))
    adjoint_tate = sp.kronecker_product(adjoint, sp.eye(2))
    abar = pi_o * inclusion_tate * pi_a.inv()
    abar_adjoint = pi_a * adjoint_tate * pi_o.inv()

    action = sp.diag(degree, 1)
    dual_action = sp.diag(1, degree)
    eta_a_old = sp.kronecker_product(sp.eye(2), action)
    eta_o_old = sp.kronecker_product(sp.eye(2), action)
    dual_eta_a_old = sp.kronecker_product(sp.eye(2), dual_action)
    dual_eta_o_old = sp.kronecker_product(sp.eye(2), dual_action)
    eta_a = pi_a * eta_a_old * pi_a.inv()
    eta_o = pi_o * eta_o_old * pi_o.inv()
    dual_eta_a = pi_a * dual_eta_a_old * pi_a.inv()
    dual_eta_o = pi_o * dual_eta_o_old * pi_o.inv()

    typed_top = abar.row_join(dual_eta_o)
    typed_bottom = eta_a.row_join(-abar_adjoint)
    principal_kani = typed_top.col_join(typed_bottom)
    omega_in = sp.diag(omega_a, omega_o)
    omega_out = sp.diag(omega_o, omega_a)

    old_top = inclusion_tate.row_join(dual_eta_o_old)
    old_bottom = eta_a_old.row_join(-adjoint_tate)
    old_kani = old_top.col_join(old_bottom)
    pi_in = sp.diag(pi_a, pi_o)
    pi_out = sp.diag(pi_o, pi_a)
    conjugated_kani = pi_out * old_kani * pi_in.inv()

    target_smith = [1, 1, 1, 1] + [n * n] * 4
    kani_smith = smith_diagonal(principal_kani)
    mutated_abar = sp.Matrix(abar)
    mutated_abar[0, 0] += 1
    mutated_degree = degree + 1
    mutated_eta = sp.Matrix(eta_a)
    mutated_eta[0, 0] += 1

    wrong_vector = (vector_a[0] + 1, vector_a[1])
    try:
        wrong_alignment = alignment_matrix(wrong_vector)
        wrong_quotient = sp.diag(1, 1, prime, 1) * sp.kronecker_product(
            wrong_alignment.inv(), sp.eye(2)
        )
        wrong_principal = (
            wrong_quotient.inv().T
            * sp.kronecker_product(
                gram_a, sp.Matrix([[0, 1], [-1, 0]])
            )
            * wrong_quotient.inv()
        )
        wrong_line_rejected = (
            not integral_matrix(wrong_principal)
            or abs(sp.det(wrong_principal)) != 1
        )
    except (RuntimeError, ZeroDivisionError):
        wrong_line_rejected = True

    wrong_degree_quotient = sp.diag(1, 1, prime + 1, 1) * sp.kronecker_product(
        alignment_matrix(vector_a).inv(), sp.eye(2)
    )
    wrong_degree_principal = (
        wrong_degree_quotient.inv().T
        * sp.kronecker_product(
            gram_a, sp.Matrix([[0, 1], [-1, 0]])
        )
        * wrong_degree_quotient.inv()
    )

    gates = {
        "pi_a_integral": integral_matrix(pi_a),
        "pi_o_integral": integral_matrix(pi_o),
        "pi_a_degree": abs(int(pi_a.det())) == prime,
        "pi_o_degree": abs(int(pi_o.det())) == prime,
        "complement_a_integral": integral_matrix(comp_a),
        "complement_o_integral": integral_matrix(comp_o),
        "complement_a_factor": comp_a * pi_a == prime * sp.eye(4),
        "complement_o_factor": comp_o * pi_o == prime * sp.eye(4),
        "omega_a_integral": integral_matrix(omega_a),
        "omega_o_integral": integral_matrix(omega_o),
        "omega_a_principal": abs(int(omega_a.det())) == 1,
        "omega_o_principal": abs(int(omega_o.det())) == 1,
        "abar_integral": integral_matrix(abar),
        "abar_adjoint_integral": integral_matrix(abar_adjoint),
        "abar_similitude": abar.T * omega_o * abar == norm * omega_a,
        "abar_adjoint_left": abar_adjoint * abar == norm * sp.eye(4),
        "abar_adjoint_right": abar * abar_adjoint == norm * sp.eye(4),
        "eta_a_integral": integral_matrix(eta_a),
        "eta_o_integral": integral_matrix(eta_o),
        "dual_eta_a_integral": integral_matrix(dual_eta_a),
        "dual_eta_o_integral": integral_matrix(dual_eta_o),
        "principal_kani_integral": integral_matrix(principal_kani),
        "principal_kani_polarization": (
            principal_kani.T * omega_out * principal_kani
            == n * n * omega_in
        ),
        "principal_kani_determinant": (
            abs(int(principal_kani.det())) == n**8
        ),
        "principal_kani_smith": kani_smith == target_smith,
        "direct_conjugation": principal_kani == conjugated_kani,
    }
    mutations = {
        "wrong_line_rejected": wrong_line_rejected,
        "wrong_quotient_degree_rejected": (
            not integral_matrix(wrong_degree_principal)
            or abs(sp.det(wrong_degree_principal)) != 1
        ),
        "abar_mutation_rejected": (
            mutated_abar.T * omega_o * mutated_abar != norm * omega_a
        ),
        "eta_mutation_rejected": (
            mutated_eta.T * omega_a * mutated_eta
            != mutated_degree * omega_a
        ),
    }
    return {
        "name": row["name"],
        "delta": prime,
        "source_kernel_lift": list(vector_a),
        "target_kernel_lift": list(vector_o),
        "pi_a": matrix_rows(pi_a),
        "pi_o": matrix_rows(pi_o),
        "principal_omega_a": matrix_rows(omega_a),
        "principal_omega_o": matrix_rows(omega_o),
        "descended_auxiliary": matrix_rows(abar),
        "principal_kani_smith": kani_smith,
        "gates": gates,
        "mutations": mutations,
        "pass": all(gates.values()) and all(mutations.values()),
    }


def main() -> None:
    source = json.loads(INPUT.read_text())
    rows = [run_row(row) for row in source["rows"]]
    scientific = {
        "claim_status": (
            "EXACT PRINCIPALIZED KANI LATTICE / "
            "NO GEOMETRIC QUOTIENT OR THETA EVALUATION"
        ),
        "rows": rows,
        "all_pass": all(row["pass"] for row in rows),
    }
    result = {
        "schema": "p1243-auxiliary-principalized-lattice-v1",
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
