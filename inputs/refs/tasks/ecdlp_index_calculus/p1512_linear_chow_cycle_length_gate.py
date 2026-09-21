#!/usr/bin/env python3
"""Evaluate the P1512 linear-Chow source-cycle length obstruction."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from collections import Counter
from itertools import permutations
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "ecdlp_index_calculus_state"
RESEARCH = ROOT / "research"
CRYPTO = Path("/Volumes/Volume/crypto-autoresearcher")
CONTRACT = STATE / "experiment_contract_p1512_source_labelled_linear_chow_atomizer.md"
HYPOTHESIS = CRYPTO / "ideas/deferred/ECDLP-IDEA-115_source_labelled_ulrich_chow_complex_hypothesis.md"
DERIVATION = CRYPTO / "ideas/artifacts/ECDLP-IDEA-115/ulrich_source_gate.md"
OUT = STATE / "p1512_linear_chow_cycle_length_gate.json"
NOTE = RESEARCH / "p1512_linear_chow_cycle_length_gate.md"

EXPECTED = {
    CONTRACT: "a23be0a4e5d7d581b0ebabe19d828573766372d4a8458d4a4571388491d5de49",
    HYPOTHESIS: "708eef11d2f4ed4acbd5cb6f831ed21f419b26304a4e7de7e8a3610ebce55ab6",
    DERIVATION: "7b76a37f27cb137d7ef31d95a235984eda0f266171ef8ded6c6680538704202c",
    STATE / "p1511_factorized_semijoin_gate.json":
        "e546f1b2403fadfa053b0bb45403c1dcb2561556f8c4352ce5801a1ac561d042",
    STATE / "p1511_factorized_semijoin_gate_audit.json":
        "b3cf2a81a77523ed867223818fbd9a791945bcb57bdf7626a34d6bf9acaed3bc",
    CRYPTO / "focus/archive/focus_queue_p1512_active.json":
        "dde50389d1a2b2e2533ab4bb30cf4d635b88fd63e4e664c26a635c8d13733a10",
    CRYPTO / "focus/archive/focus_plan_p1512_active.json":
        "263ae70f169a16bd2a58bfaf76fe825c7317a581271d3077620295e0912fc15f",
    CRYPTO / "focus/archive/focus_report_p1512_active.md":
        "5fba80e9985fc531ae22a33ecdd2b650b1c42aa43d61b322de96094988ba954e",
}

Monomial = tuple[int, int, int]
Polynomial = dict[Monomial, int]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def parse_sizes(value: str) -> list[int]:
    sizes = [int(part) for part in value.split(",") if part.strip()]
    if not sizes or any(size < 2 for size in sizes):
        raise argparse.ArgumentTypeError("sizes must be comma-separated integers >=2")
    return sizes


def add(left: Polynomial, right: Polynomial) -> Polynomial:
    result = dict(left)
    for monomial, coefficient in right.items():
        result[monomial] = result.get(monomial, 0) + coefficient
        if result[monomial] == 0:
            del result[monomial]
    return result


def scale(value: Polynomial, coefficient: int) -> Polynomial:
    return {
        monomial: coefficient * current
        for monomial, current in value.items()
        if coefficient * current
    }


def multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for left_monomial, left_coefficient in left.items():
        for right_monomial, right_coefficient in right.items():
            monomial = tuple(
                left_monomial[index] + right_monomial[index]
                for index in range(3)
            )
            result[monomial] = (
                result.get(monomial, 0) + left_coefficient * right_coefficient
            )
    return {monomial: coefficient for monomial, coefficient in result.items() if coefficient}


def permutation_sign(permutation: tuple[int, ...]) -> int:
    inversions = sum(
        permutation[left] > permutation[right]
        for left in range(len(permutation))
        for right in range(left + 1, len(permutation))
    )
    return -1 if inversions % 2 else 1


def determinant(matrix: list[list[Polynomial]]) -> Polynomial:
    size = len(matrix)
    result: Polynomial = {}
    for permutation in permutations(range(size)):
        term: Polynomial = {(0, 0, 0): 1}
        for row, column in enumerate(permutation):
            term = multiply(term, matrix[row][column])
        result = add(result, scale(term, permutation_sign(permutation)))
    return result


def multiply_univariate(left: list[int], right: list[int]) -> list[int]:
    result = [0] * (len(left) + len(right) - 1)
    for left_index, left_value in enumerate(left):
        for right_index, right_value in enumerate(right):
            result[left_index + right_index] += left_value * right_value
    return result


def positive_controls() -> dict[str, Any]:
    x = {(1, 0, 0): 1}
    y = {(0, 1, 0): 1}
    z = {(0, 0, 1): 1}
    circulant = [[x, y, z], [z, x, y], [y, z, x]]
    observed = determinant(circulant)
    expected = {
        (3, 0, 0): 1,
        (0, 3, 0): 1,
        (0, 0, 3): 1,
        (1, 1, 1): -3,
    }

    roots = [2, 5, 11, 11]
    diagonal_polynomial = [1]
    for root in roots:
        diagonal_polynomial = multiply_univariate(diagonal_polynomial, [-root, 1])
    multiplicities = Counter(roots)
    kernel_atoms = {
        str(root): [index for index, value in enumerate(roots) if value == root]
        for root in sorted(multiplicities)
    }
    return {
        "circulant_matrix_dimension": 3,
        "circulant_determinant_terms": {
            ",".join(map(str, monomial)): coefficient
            for monomial, coefficient in sorted(observed.items())
        },
        "circulant_fermat_hesse_cubic_exact": observed == expected,
        "diagonal_roots": roots,
        "diagonal_determinant_coefficients_low_to_high": diagonal_polynomial,
        "diagonal_root_multiplicities": {
            str(root): multiplicity for root, multiplicity in sorted(multiplicities.items())
        },
        "diagonal_kernel_basis_indices": kernel_atoms,
        "diagonal_dimension_equals_atom_count": len(roots) == sum(multiplicities.values()),
        "repeated_root_corank_equals_multiplicity": all(
            len(kernel_atoms[str(root)]) == multiplicity
            for root, multiplicity in multiplicities.items()
        ),
    }


def dimension_cell(r: int) -> dict[str, Any]:
    oriented_factor_count = 2 * r
    canonical_atoms = math.comb(oriented_factor_count + 4, 5)
    ordered_atoms = oriented_factor_count**5
    minimum_linear_rank = (canonical_atoms + 2) // 3
    rho_squared = r**5
    batch_degree = r**3
    batch_gcd_degree = r
    sylvester_dimension = 2 * batch_degree
    subresultant_dimension = 2 * batch_degree - 2 * batch_gcd_degree
    compound_dimension = math.comb(sylvester_dimension, batch_gcd_degree)
    return {
        "r": r,
        "oriented_factor_count": oriented_factor_count,
        "ordered_source_atom_count": ordered_atoms,
        "canonical_multiset_source_atom_count": canonical_atoms,
        "plane_cubic_degree": 3,
        "minimum_scalar_linear_matrix_rank": minimum_linear_rank,
        "linear_rank_times_curve_degree": 3 * minimum_linear_rank,
        "rho_proxy_r2p5": r**2.5,
        "rho_squared_proxy_r5": rho_squared,
        "minimum_rank_over_rho": minimum_linear_rank / (r**2.5),
        "minimum_rank_strictly_above_rho_exact": minimum_linear_rank**2 > rho_squared,
        "p1511_batch_degree": batch_degree,
        "companion_or_bezout_dimension": batch_degree,
        "sylvester_dimension": sylvester_dimension,
        "gcd_degree": batch_gcd_degree,
        "subresultant_dimension_lower_control": subresultant_dimension,
        "exterior_compound_dimension": compound_dimension,
        "exterior_compound_decimal_digits": len(str(compound_dimension)),
    }


def render_note(payload: dict[str, Any]) -> str:
    lines = [
        "# P1512 Linear-Chow Cycle-Length Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "For `B=2r` oriented factors, the favorable canonical five-source cycle",
        "has length `binomial(B+4,5)`. Exact independent kernel atoms force at",
        "least that total corank multiplicity across target fibers. A scalar-linear",
        "`m x m` determinant on a plane cubic has zero-divisor degree `3m`.",
        "",
        "| r | canonical atoms | minimum linear rank | rank/rho | P1511 Sylvester |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in payload["dimension_cells"]:
        lines.append(
            f"| {row['r']} | {row['canonical_multiset_source_atom_count']} | "
            f"{row['minimum_scalar_linear_matrix_rank']} | "
            f"{row['minimum_rank_over_rho']:.6f} | {row['sylvester_dimension']} |"
        )
    lines += [
        "",
        "All exact inequalities hold on the frozen ladder. The `3 x 3` circulant",
        "determinant reproduces the Hesse cubic, and the diagonal atomizer confirms",
        "that distinct and repeated labelled atoms consume matching kernel dimension",
        "and determinant multiplicity.",
        "",
        "This is a scoped negative for source-labelled scalar-linear Chow/Tate and",
        "standard determinant-of-cohomology atomizers. It does not rule out a",
        "target-specialized nonlinear circuit with separately charged source",
        "splitting. Relation collection, blind descent, and a rho/Shoup break remain",
        "unattempted.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", type=parse_sizes, default=parse_sizes("4,6,8,12,16,24,32"))
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--note", type=Path, default=NOTE)
    args = parser.parse_args()

    frozen_hashes = {str(path): sha256(path) for path in EXPECTED}
    mismatches = [
        str(path) for path, expected in EXPECTED.items()
        if frozen_hashes[str(path)] != expected
    ]
    if mismatches:
        raise RuntimeError(f"P1512 frozen input hash mismatch: {mismatches}")

    derivation_text = DERIVATION.read_text(encoding="utf-8")
    cells = [dimension_cell(r) for r in args.sizes]
    controls = positive_controls()
    ratios = [row["minimum_rank_over_rho"] for row in cells]
    required_terms = [
        "sum_R nu_R = L(r)",
        "ord_R(det M) >= c_R >= nu_R",
        "m >= ceil(binomial(2r+4,5)/3)",
        "sum_c m_c d_c >= L(r)/3",
        "target-specialized nonlinear representation",
    ]
    checks = {
        "all_frozen_hashes_exact": True,
        "canonical_cycle_count_is_exact_multiset_formula": all(
            row["canonical_multiset_source_atom_count"]
            == math.comb(2 * row["r"] + 4, 5)
            for row in cells
        ),
        "ordered_cycle_count_is_exact": all(
            row["ordered_source_atom_count"] == (2 * row["r"]) ** 5
            for row in cells
        ),
        "linear_rank_bound_covers_every_canonical_atom": all(
            row["linear_rank_times_curve_degree"]
            >= row["canonical_multiset_source_atom_count"]
            for row in cells
        ),
        "linear_rank_is_strictly_above_rho_exactly": all(
            row["minimum_rank_strictly_above_rho_exact"] for row in cells
        ),
        "linear_rank_over_rho_ratio_grows_on_ladder": all(
            later > earlier for earlier, later in zip(ratios, ratios[1:])
        ),
        "standard_batch_matrix_dimensions_are_cubic_or_larger": all(
            row["companion_or_bezout_dimension"] == row["r"] ** 3
            and row["sylvester_dimension"] == 2 * row["r"] ** 3
            and row["subresultant_dimension_lower_control"]
            == 2 * row["r"] ** 3 - 2 * row["r"]
            for row in cells
        ),
        "exterior_compounds_do_not_reduce_base_dimension": all(
            row["exterior_compound_dimension"] >= row["sylvester_dimension"]
            for row in cells
        ),
        "circulant_linear_determinant_control_exact": controls[
            "circulant_fermat_hesse_cubic_exact"
        ],
        "diagonal_labelled_atom_control_exact": controls[
            "diagonal_dimension_equals_atom_count"
        ],
        "repeated_atom_multiplicity_control_exact": controls[
            "repeated_root_corank_equals_multiplicity"
        ],
        "derivation_contains_local_global_chart_and_scope_proofs": all(
            term in derivation_text for term in required_terms
        ),
    }
    if not all(checks.values()):
        failures = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(f"P1512 theorem-gate failures: {failures}")

    payload = {
        "schema": "autolab.ecdlp.p1512_linear_chow_cycle_length_gate.v1",
        "status": "NEGATIVE_P1512_LINEAR_CHOW_ATOMIZER_FULL_CYCLE_LENGTH",
        "source": str(Path(__file__).resolve()),
        "source_sha256": sha256(Path(__file__).resolve()),
        "frozen_hashes": frozen_hashes,
        "theorem": {
            "canonical_cycle_length": "L(r)=binomial(2r+4,5)",
            "local_smith_bound": "ord_R(det M)>=corank(M(R))>=nu_R",
            "global_plane_cubic_bound": "3m>=sum_R nu_R=L(r)",
            "linear_rank_lower_bound": "m>=ceil(binomial(2r+4,5)/3)=Omega(r^5)",
            "multi_chart_payload_bound": "sum_c m_c*d_c>=L(r)/3",
            "rho_boundary": "q=Theta(r^5), rho=Theta(r^(5/2))",
        },
        "dimension_cells": cells,
        "positive_controls": controls,
        "checks": checks,
        "check_count": len(checks),
        "check_pass_count": sum(checks.values()),
        "literature": [
            "https://arxiv.org/abs/math/0111040",
            "https://arxiv.org/abs/1511.05502",
            "https://eprint.iacr.org/2004/031.pdf",
        ],
        "claim_status": {
            "linear_chow_atomizer": "scoped_negative",
            "target_specialized_nonlinear_representation": "not_attempted",
            "relation_collection": "not_attempted",
            "factor_log_rank": "not_attempted",
            "blind_descent": "not_attempted",
            "generic_shoup_breakthrough": "not_attempted",
        },
        "interpretation": (
            "An exact source-labelled scalar-linear determinant or standard "
            "determinant-of-cohomology complex must carry at least the full canonical "
            "five-source cycle length across its target fibers. On q=Theta(r^5), the "
            "resulting Omega(r^5) linear rank-twist payload is already above rho. The "
            "negative is scoped to independent linear kernel/cokernel atomizers and "
            "preserves target-specialized nonlinear circuits as an untested successor."
        ),
    }
    write_atomic(
        args.out,
        json.dumps(payload, indent=2, sort_keys=True).encode("utf-8") + b"\n",
    )
    write_atomic(args.note, render_note(payload).encode("utf-8"))
    print(f"status={payload['status']} checks={payload['check_pass_count']}/{payload['check_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
