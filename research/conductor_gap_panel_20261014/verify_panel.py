#!/usr/bin/env python3
"""Independently verify the frozen conductor-gap panel.

This verifier intentionally does not import ``build_panel.py``.  It checks the
generated panel against exact arithmetic and the archived source records, and
writes a deterministic receipt.  It does not construct an isogeny, certify a
point map, or measure an ECDLP transfer.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

from sympy import __version__ as sympy_version
from sympy import factorint


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PANEL_PATH = HERE / "panel.json"
RECEIPT_PATH = HERE / "verification.json"
PANEL_SCHEMA = "crypto.conductor-gap-panel/v2"
RECEIPT_SCHEMA = "crypto.conductor-gap-panel-verification/v2"


class VerificationError(RuntimeError):
    """A deterministic panel verification failed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def require_equal(observed: Any, expected: Any, label: str) -> None:
    if observed != expected:
        raise VerificationError(
            f"{label}: observed {observed!r}, expected {expected!r}"
        )


def read_json(relative_path: str) -> dict[str, Any]:
    return json.loads((ROOT / relative_path).read_text())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def product(values: list[int]) -> int:
    answer = 1
    for value in values:
        answer *= value
    return answer


def distinct_prime_factors(value: int) -> list[int]:
    factors: list[int] = []
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            factors.append(divisor)
            while value % divisor == 0:
                value //= divisor
        divisor += 1 if divisor == 2 else 2
    if value > 1:
        factors.append(value)
    return factors


def matrix_multiply_mod(
    left: list[list[int]], right: list[list[int]], modulus: int
) -> list[list[int]]:
    return [
        [
            sum(left[i][k] * right[k][j] for k in range(2)) % modulus
            for j in range(2)
        ]
        for i in range(2)
    ]


def matrix_power_mod(
    matrix: list[list[int]], exponent: int, modulus: int
) -> list[list[int]]:
    answer = [[1, 0], [0, 1]]
    base = [[entry % modulus for entry in row] for row in matrix]
    while exponent:
        if exponent & 1:
            answer = matrix_multiply_mod(answer, base, modulus)
        base = matrix_multiply_mod(base, base, modulus)
        exponent >>= 1
    return answer


def matrix_vector_mod(
    matrix: list[list[int]], vector: list[int], modulus: int
) -> list[int]:
    return [
        sum(matrix[i][j] * vector[j] for j in range(2)) % modulus
        for i in range(2)
    ]


def projectively_equal(left: list[int], right: list[int], modulus: int) -> bool:
    return (left[0] * right[1] - left[1] * right[0]) % modulus == 0


EXACT_WORKING_FIELD_KEYS = {
    ("nist-k163", 45641),
    ("nist-k283", 1697),
}
CONCRETE_KERNEL_X_ORBIT_KEYS = {
    ("nist-k163", 45641),
}


def factor_pairs(value: int) -> list[tuple[int, int]]:
    factors = [(int(p), int(e)) for p, e in factorint(value).items()]
    factors.sort()
    require(product([p**e for p, e in factors]) == value,
            f"incomplete factorization of {value}")
    return factors


PRIME_CERTIFICATES: dict[int, dict[str, Any]] = {}


def prove_prime(n: int) -> None:
    """Build a recursive Lucas n-1 certificate for n.

    ``factorint`` proposes the factorization.  The recursive certificates and
    Lucas conditions establish primality; a probable-prime predicate is not
    used as the acceptance condition.
    """
    if n in PRIME_CERTIFICATES:
        return
    require(n >= 2, f"invalid prime candidate {n}")
    if n == 2:
        PRIME_CERTIFICATES[n] = {
            "n": "2", "n_minus_1_factorization": [], "witnesses": []
        }
        return
    require(n % 2 == 1, f"even composite prime candidate {n}")
    factors = factor_pairs(n - 1)
    for q, _ in factors:
        prove_prime(q)
    witnesses: list[tuple[str, int]] = []
    for q, _ in factors:
        witness = None
        for candidate in range(2, min(n, 10_000)):
            if (
                pow(candidate, n - 1, n) == 1
                and math.gcd(pow(candidate, (n - 1) // q, n) - 1, n) == 1
            ):
                witness = candidate
                break
        require(witness is not None,
                f"no Lucas n-1 witness below 10000 for n={n}, q={q}")
        witnesses.append((str(q), witness))
    PRIME_CERTIFICATES[n] = {
        "n": str(n),
        "n_minus_1_factorization": [[str(q), e] for q, e in factors],
        "witnesses": [[q, a] for q, a in witnesses],
    }


def verify_prime_certificate(n: int, active: set[int] | None = None) -> None:
    active = set() if active is None else active
    require(n not in active, f"cycle in primality certificate for {n}")
    node = PRIME_CERTIFICATES.get(n)
    require(node is not None, f"missing primality certificate for {n}")
    if n == 2:
        require_equal(node["n_minus_1_factorization"], [], "prime 2 factors")
        return
    active.add(n)
    factors = [(int(q), int(e)) for q, e in node["n_minus_1_factorization"]]
    require_equal(product([q**e for q, e in factors]), n - 1,
                  f"certificate product for {n}")
    witnesses = {int(q): int(a) for q, a in node["witnesses"]}
    require_equal(set(witnesses), {q for q, _ in factors},
                  f"certificate witnesses for {n}")
    for q, _ in factors:
        verify_prime_certificate(q, active)
        a = witnesses[q]
        require_equal(pow(a, n - 1, n), 1,
                      f"Lucas Fermat condition for n={n}, q={q}")
        require_equal(math.gcd(pow(a, (n - 1) // q, n) - 1, n), 1,
                      f"Lucas gcd condition for n={n}, q={q}")
    active.remove(n)


def kronecker_minus_7(p: int) -> int:
    if p == 7:
        return 0
    value = pow((-7) % p, (p - 1) // 2, p)
    require(value in {1, p - 1}, f"invalid Euler criterion result for {p}")
    return 1 if value == 1 else -1


def tau_power_linear(m: int, mu: int) -> tuple[int, int]:
    """Return x,y for tau^m=x+y*tau by a linear recurrence."""
    x, y = 1, 0
    for _ in range(m):
        x, y = -2 * y, x + mu * y
    return x, y


def exact_multiplicative_order(value: int, prime: int) -> int:
    factors = [
        (int(q), int(e))
        for q, e in PRIME_CERTIFICATES[prime]["n_minus_1_factorization"]
    ]
    order = prime - 1
    for q, exponent in factors:
        for _ in range(exponent):
            if order % q == 0 and pow(value, order // q, prime) == 1:
                order //= q
            else:
                break
    require_equal(pow(value, order, prime), 1,
                  f"multiplicative order terminal power modulo {prime}")
    for q, _ in factors:
        if order % q == 0:
            require(pow(value, order // q, prime) != 1,
                    f"multiplicative order not minimal modulo {prime}")
    return order


def verify_working_field_certificate(
    row: dict[str, Any],
    ell: int,
    m: int,
    mu: int,
    scalar: int,
    relative_x_degree: int,
) -> dict[str, Any]:
    """Verify the evidence status independently of the panel builder.

    For the two admitted rows, the companion matrix of absolute Frobenius is
    checked on an abstract non-horizontal torsion vector.  Exact order modulo
    sign proves that representative's minimal absolute x-coordinate orbit
    degree.  Every row also proves ``m*k`` as an ambient upper bound for all
    ell-torsion x-coordinates; neither statement constructs a point or map.
    """
    key = (row["class_id"], ell)
    absolute_degree = m * relative_x_degree
    matrix = [[0, -2], [1, mu]]
    normalized_matrix = [[entry % ell for entry in line] for line in matrix]
    determinant = (matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]) % ell
    require_equal(determinant, 2 % ell,
                  f"absolute Frobenius determinant for {row['gap_id']}")
    require(determinant != 0, f"singular Frobenius matrix for {row['gap_id']}")
    q_frobenius_matrix = matrix_power_mod(matrix, m, ell)
    require_equal(q_frobenius_matrix, [[scalar, 0], [0, scalar]],
                  f"scalar q-Frobenius matrix for {row['gap_id']}")
    ambient_closure_matrix = matrix_power_mod(matrix, absolute_degree, ell)
    identity = [[1, 0], [0, 1]]
    negative_identity = [[ell - 1, 0], [0, ell - 1]]
    require(ambient_closure_matrix in (identity, negative_identity),
            f"ambient absolute x-degree does not close for {row['gap_id']}")
    require_equal(int(row["ambient_absolute_x_degree_upper_bound"]), absolute_degree,
                  f"ambient absolute x-degree bound for {row['gap_id']}")
    if key not in EXACT_WORKING_FIELD_KEYS:
        require_equal(
            row["working_field_status"],
            "certified_ambient_upper_bound_only",
            f"ambient working-field status for {row['gap_id']}",
        )
        require(row["working_field_certificate"] is None,
                f"unsupported exact working-field certificate for {row['gap_id']}")
        require(row["exact_abstract_cm_representative_x_orbit_degree"] is None,
                f"unsupported exact abstract x-orbit for {row['gap_id']}")
        require(row["concrete_kernel_x_orbit_degree"] is None,
                f"unsupported concrete kernel x-orbit for {row['gap_id']}")
        require_equal(row["concrete_kernel_x_orbit_status"], "not_certified",
                      f"concrete kernel x-orbit status for {row['gap_id']}")
        return {
            "status": row["working_field_status"],
            "absolute_degree_interpretation": "ambient_upper_bound",
            "ambient_absolute_x_degree_upper_bound": str(absolute_degree),
            "concrete_kernel_x_orbit_status": "not_certified",
            "q_frobenius_matrix_mod_ell": [
                [str(value) for value in line] for line in q_frobenius_matrix
            ],
            "ambient_closure_matrix_mod_ell": [
                [str(value) for value in line] for line in ambient_closure_matrix
            ],
        }

    require_equal(
        row["working_field_status"],
        "exact_abstract_cm_representative_x_orbit",
        f"exact working-field status for {row['gap_id']}",
    )
    certificate = row["working_field_certificate"]
    require(isinstance(certificate, dict),
            f"missing working-field certificate for {row['gap_id']}")
    require_equal(
        int(row["exact_abstract_cm_representative_x_orbit_degree"]),
        absolute_degree,
        f"exact abstract x-orbit degree for {row['gap_id']}",
    )
    require_equal(certificate["certificate_kind"], "derived_cm_line_orbit",
                  f"certificate kind for {row['gap_id']}")
    require_equal(certificate["basis"], ["1", "tau"],
                  f"certificate basis for {row['gap_id']}")
    require_equal(certificate["vector_convention"],
                  "column [a,b] represents a+b*tau",
                  f"certificate vector convention for {row['gap_id']}")
    require_equal(certificate["tau_relation"], "tau^2-mu*tau+2=0",
                  f"certificate tau relation for {row['gap_id']}")
    require_equal(int(certificate["mu"]), mu,
                  f"certificate mu for {row['gap_id']}")
    concrete_binding = certificate["concrete_point_binding"]
    require(isinstance(concrete_binding, dict),
            f"concrete binding record for {row['gap_id']}")
    if key in CONCRETE_KERNEL_X_ORBIT_KEYS:
        require_equal(
            row["concrete_kernel_x_orbit_status"],
            "certified_retained_relative_tower_witness",
            f"concrete kernel x-orbit status for {row['gap_id']}",
        )
        require_equal(int(row["concrete_kernel_x_orbit_degree"]), absolute_degree,
                      f"concrete kernel x-orbit degree for {row['gap_id']}")
        require_equal(concrete_binding["status"],
                      "certified_concrete_kernel_x_witness",
                      f"concrete binding status for {row['gap_id']}")
        require_equal(concrete_binding["evidence_kind"],
                      "observed_fail_closed_probe",
                      f"concrete binding evidence kind for {row['gap_id']}")
        require_equal(
            concrete_binding["evidence_path"],
            "research/ecc2k130_conductor_isogenies_20261007/analogues/"
            "probe163_45641_relative_tower.out",
            f"concrete binding evidence path for {row['gap_id']}",
        )
        require_equal(
            concrete_binding["retained_input_replay_path"],
            "research/ecc2k130_conductor_isogenies_20261007/analogues/"
            "verify163_45641_relative_witness.out",
            f"concrete binding retained-input replay path for {row['gap_id']}",
        )
        require_equal(
            concrete_binding["arithmetic_independence"],
            "not_independent_same_x_only_ladder_family",
            f"concrete binding arithmetic independence for {row['gap_id']}",
        )
        require_equal(concrete_binding["probe_schema"],
                      "k163-degree45641-relative-tower-probe-v2",
                      f"concrete binding schema for {row['gap_id']}")
        require_equal(int(concrete_binding["absolute_x_orbit_degree"]),
                      absolute_degree,
                      f"concrete binding degree for {row['gap_id']}")
        require_equal(concrete_binding["closure_status"], "pass",
                      f"concrete binding closure for {row['gap_id']}")
        require_equal(
            [int(value) for value in
             concrete_binding["proper_divisor_exclusion_degrees"]],
            [absolute_degree // prime
             for prime in distinct_prime_factors(absolute_degree)],
            f"concrete binding exclusions for {row['gap_id']}",
        )
        require_equal(concrete_binding["all_nonzero_kernel_multiples_status"],
                      "derived", f"concrete binding scope for {row['gap_id']}")
        require_equal(concrete_binding["descending_classification_basis"],
                      "derived_tau_eigenline_exclusion",
                      f"concrete binding classification basis for {row['gap_id']}")
        require_equal(concrete_binding["prime_line_scope_status"], "derived",
                      f"concrete binding line-scope status for {row['gap_id']}")
    else:
        require_equal(row["concrete_kernel_x_orbit_status"], "not_certified",
                      f"concrete kernel x-orbit status for {row['gap_id']}")
        require(row["concrete_kernel_x_orbit_degree"] is None,
                f"unsupported concrete kernel x-orbit for {row['gap_id']}")
        require_equal(concrete_binding, {"status": "not_certified"},
                      f"concrete binding for {row['gap_id']}")
    require("abstract non-horizontal torsion vector" in certificate["scope"],
            f"abstract-vector scope missing for {row['gap_id']}")
    require("not explicit point coordinates" in certificate["scope"],
            f"concrete-point limitation missing for {row['gap_id']}")
    recorded_matrix = [
        [int(entry) for entry in line]
        for line in certificate["absolute_frobenius_matrix_mod_ell"]
    ]
    require_equal(recorded_matrix, normalized_matrix,
                  f"absolute Frobenius matrix for {row['gap_id']}")
    vector = [int(value) for value in certificate["representative_vector"]]
    require_equal(vector, [1, 0], f"representative vector for {row['gap_id']}")
    require(any(value % ell for value in vector),
            f"zero representative vector for {row['gap_id']}")
    first_image = matrix_vector_mod(matrix, vector, ell)
    require(not projectively_equal(first_image, vector, ell),
            f"representative line is horizontal for {row['gap_id']}")
    require_equal(certificate["representative_line_status"], "non_horizontal",
                  f"representative line status for {row['gap_id']}")
    require_equal(
        [[int(value) for value in line] for line in
         certificate["q_frobenius_matrix_mod_ell"]],
        q_frobenius_matrix,
        f"recorded q-Frobenius matrix for {row['gap_id']}",
    )
    line_return = matrix_vector_mod(q_frobenius_matrix, vector, ell)
    require_equal(line_return, [scalar, 0],
                  f"q-Frobenius line return for {row['gap_id']}")
    require(projectively_equal(line_return, vector, ell),
            f"line does not return after m for {row['gap_id']}")
    line_prime_divisors = distinct_prime_factors(m)
    line_items = certificate["line_factor_exclusion_images"]
    require_equal(len(line_items), len(line_prime_divisors),
                  f"line exclusion count for {row['gap_id']}")
    line_exclusions = {int(item["prime_divisor"]): item for item in line_items}
    require_equal(len(line_exclusions), len(line_items),
                  f"duplicate line exclusion for {row['gap_id']}")
    require_equal(set(line_exclusions), set(line_prime_divisors),
                  f"line exclusion primes for {row['gap_id']}")
    line_exclusion_receipts = []
    for prime in line_prime_divisors:
        earlier = matrix_vector_mod(
            matrix_power_mod(matrix, m // prime, ell), vector, ell
        )
        require(not projectively_equal(earlier, vector, ell),
                f"line orbit is not minimal for {row['gap_id']}, p={prime}")
        item = line_exclusions[prime]
        require_equal(int(item["exponent"]), m // prime,
                      f"line exclusion exponent for {row['gap_id']}, p={prime}")
        require_equal([int(value) for value in item["image"]], earlier,
                      f"line exclusion image for {row['gap_id']}, p={prime}")
        line_exclusion_receipts.append({
            "prime_divisor": str(prime),
            "exponent": str(m // prime),
            "image": [str(value) for value in earlier],
        })
    require_equal(int(certificate["line_orbit_degree"]), m,
                  f"line orbit degree for {row['gap_id']}")
    require_equal(
        [int(value) for value in certificate["line_return_image"]], line_return,
        f"line return witness for {row['gap_id']}",
    )
    require_equal(int(certificate["q_relative_x_orbit_degree"]), relative_x_degree,
                  f"relative x orbit degree for {row['gap_id']}")
    require_equal(math.gcd(m, relative_x_degree), 1,
                  f"line/relative degree gcd for {row['gap_id']}")
    require_equal(certificate["line_and_relative_degrees_coprime"], True,
                  f"coprime marker for {row['gap_id']}")
    require_equal(int(certificate["absolute_x_orbit_degree"]), absolute_degree,
                  f"absolute x orbit degree for {row['gap_id']}")

    full_image = matrix_vector_mod(ambient_closure_matrix, vector, ell)
    require(full_image in ([1, 0], [ell - 1, 0]),
            f"absolute orbit does not close modulo sign for {row['gap_id']}")
    require_equal(
        [int(value) for value in certificate["full_orbit_image"]], full_image,
        f"full absolute-orbit witness for {row['gap_id']}",
    )
    require_equal(
        [[int(value) for value in line] for line in
         certificate["absolute_x_orbit_matrix_mod_ell"]],
        ambient_closure_matrix,
        f"absolute x-orbit closure matrix for {row['gap_id']}",
    )
    closure_sign = 1 if ambient_closure_matrix == identity else -1
    require_equal(certificate["absolute_x_orbit_closure_sign"], closure_sign,
                  f"absolute x-orbit closure sign for {row['gap_id']}")
    require_equal(
        int(certificate["exact_full_point_orbit_degree"]),
        absolute_degree if closure_sign == 1 else 2 * absolute_degree,
        f"full point orbit degree for {row['gap_id']}",
    )
    exclusion_items = certificate["factor_exclusion_images"]
    exclusions = {int(item["prime_divisor"]): item for item in exclusion_items}
    prime_divisors = distinct_prime_factors(absolute_degree)
    require_equal(len(exclusion_items), len(prime_divisors),
                  f"absolute orbit exclusion count for {row['gap_id']}")
    require_equal(len(exclusions), len(exclusion_items),
                  f"duplicate absolute orbit exclusion for {row['gap_id']}")
    require_equal(set(exclusions), set(prime_divisors),
                  f"absolute orbit exclusion primes for {row['gap_id']}")
    exclusion_receipts = []
    for prime in prime_divisors:
        exponent = absolute_degree // prime
        image = matrix_vector_mod(matrix_power_mod(matrix, exponent, ell), vector, ell)
        require(image not in ([1, 0], [ell - 1, 0]),
                f"absolute orbit is not minimal for {row['gap_id']}, p={prime}")
        item = exclusions[prime]
        require_equal(int(item["exponent"]), exponent,
                      f"factor exclusion exponent for {row['gap_id']}, p={prime}")
        require_equal([int(value) for value in item["image"]], image,
                      f"factor exclusion image for {row['gap_id']}, p={prime}")
        exclusion_receipts.append({
            "prime_divisor": str(prime),
            "exponent": str(exponent),
            "image": [str(value) for value in image],
        })
    return {
        "status": row["working_field_status"],
        "certificate_kind": "derived_cm_line_orbit",
        "line_orbit_degree": str(m),
        "line_factor_exclusion_images": line_exclusion_receipts,
        "q_frobenius_matrix_mod_ell": [
            [str(value) for value in line] for line in q_frobenius_matrix
        ],
        "relative_x_orbit_degree": str(relative_x_degree),
        "absolute_x_orbit_degree": str(absolute_degree),
        "absolute_x_orbit_closure_sign": closure_sign,
        "exact_full_point_orbit_degree": (
            str(absolute_degree) if closure_sign == 1 else str(2 * absolute_degree)
        ),
        "line_return_image": [str(value) for value in line_return],
        "full_orbit_image": [str(value) for value in full_image],
        "factor_exclusion_images": exclusion_receipts,
        "concrete_kernel_x_orbit_status": row["concrete_kernel_x_orbit_status"],
        "concrete_kernel_x_orbit_degree": row["concrete_kernel_x_orbit_degree"],
    }


def rankdata(values: list[float]) -> list[float]:
    ordered = sorted(enumerate(values), key=lambda pair: pair[1])
    ranks = [0.0] * len(values)
    index = 0
    while index < len(ordered):
        end = index + 1
        while end < len(ordered) and ordered[end][1] == ordered[index][1]:
            end += 1
        rank = (index + 1 + end) / 2.0
        for cursor in range(index, end):
            ranks[ordered[cursor][0]] = rank
        index = end
    return ranks


def pearson(xs: list[float], ys: list[float]) -> float:
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    denominator = math.sqrt(
        sum((x - x_mean) ** 2 for x in xs)
        * sum((y - y_mean) ** 2 for y in ys)
    )
    return numerator / denominator


def expected_csv_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, dict)):
        return json.dumps(value, separators=(",", ":"))
    return str(value)


def verify_csv(relative_path: str, rows: list[dict[str, Any]]) -> None:
    path = HERE / relative_path
    require(path.is_file(), f"missing CSV {path}")
    expected_fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in expected_fields:
                expected_fields.append(key)
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream)
        require_equal(reader.fieldnames, expected_fields, f"{relative_path} header")
        observed_rows = list(reader)
    require_equal(len(observed_rows), len(rows), f"{relative_path} row count")
    for index, (observed, expected) in enumerate(zip(observed_rows, rows), 1):
        for key in expected_fields:
            require_equal(observed[key], expected_csv_cell(expected.get(key)),
                          f"{relative_path} row {index} field {key}")


def verify_source_hashes(panel: dict[str, Any]) -> int:
    source_rows = panel["sources"]
    source_paths = [row["path"] for row in source_rows]
    require_equal(len(source_paths), len(set(source_paths)), "source path uniqueness")
    for row in source_rows:
        path = ROOT / row["path"]
        require(path.is_file(), f"missing source {row['path']}")
        require_equal(sha256(path), row["sha256"], f"source hash {row['path']}")
    cited: set[str] = set()
    for section in (
        "classes", "gaps", "controls", "measured_effects",
        "construction_measurements",
    ):
        for row in panel[section]:
            if isinstance(row.get("evidence_path"), str):
                cited.add(row["evidence_path"])
    cited.add(panel["p224_candidate"]["evidence_path"])
    require(cited <= set(source_paths),
            f"unhashed cited evidence paths: {sorted(cited - set(source_paths))}")
    return len(source_rows)


def verify_rerun_provenance() -> dict[str, int]:
    relative_path = (
        "research/ecc2k130_conductor_isogenies_20261007/analogues/"
        "rerun_provenance.json"
    )
    provenance_path = ROOT / relative_path
    provenance = json.loads(provenance_path.read_text())
    require_equal(provenance["schema"],
                  "k163-conductor-gap-rerun-provenance-v1",
                  "K-163 rerun provenance schema")
    require_equal(
        provenance["repository_state"]["base_commit"],
        "7d793ffbdf0e63790c3bf7bd20900d5a965ef962",
        "K-163 rerun provenance base commit",
    )
    require_equal(provenance["repository_state"]["dirty"], True,
                  "K-163 rerun provenance dirty-tree disclosure")
    require_equal(provenance["environment"]["image"], "codex-pari-gp:2.15.2",
                  "K-163 rerun provenance container image")
    require_equal(
        provenance["environment"]["image_id"],
        "sha256:ebfb26b44c70c9fba2093729fadc4ff03c2532433d006b7c1ebb729c713cd650",
        "K-163 rerun provenance container image id",
    )
    require_equal(provenance["environment"]["pari_gp"], "2.15.2",
                  "K-163 rerun provenance PARI/GP version")
    require_equal(
        provenance["environment"]["pari_build"],
        "amd64 linux x86-64, GMP-6.2.1, gcc 12.2.0, pthread",
        "K-163 rerun provenance PARI/GP build",
    )

    timestamp_pattern = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")

    def verify_execution_metadata(row: dict[str, Any], label: str) -> None:
        require(isinstance(row.get("command"), str) and bool(row["command"].strip()),
                f"missing exact command for {label}")
        started = row.get("started_at_utc")
        ended = row.get("ended_at_utc")
        require(isinstance(started, str) and
                timestamp_pattern.fullmatch(started) is not None,
                f"invalid UTC start timestamp for {label}")
        require(isinstance(ended, str) and
                timestamp_pattern.fullmatch(ended) is not None,
                f"invalid UTC end timestamp for {label}")
        require(started <= ended, f"end timestamp precedes start for {label}")

    expected_source_files = {
        "check_char2_velu_function_identity_small.gp",
        "run_check_char2_velu_function_identity_small.gp",
        "control163_45641_horizontal_endomorphism.gp",
        "run_control163_45641_horizontal_endomorphism.gp",
        "probe163_45641_relative_tower.gp",
        "run_probe163_45641_relative_tower.gp",
        "probe163_45641_seed.gp",
        "probe163_45641_seed_bounded.inc.gp",
        "run_probe163_45641_seed.gp",
        "verify163_45641_seed_endpoint.gp",
        "run_verify163_45641_seed_endpoint.gp",
        "verify163_45641_relative_witness.gp",
        "kernel163_45641_map_relative.gp",
        "run163_45641_map_relative.gp",
        "../../isogeny_volcano_rho_20261005/map73_dual_control.gp",
    }
    source_files = provenance["source_files"]
    require_equal(set(source_files), expected_source_files,
                  "K-163 rerun provenance source-file set")
    for relative_source, expected_hash in source_files.items():
        source_path = (provenance_path.parent / relative_source).resolve()
        require(source_path.is_file(),
                f"missing rerun provenance source {relative_source}")
        require(re.fullmatch(r"[0-9a-f]{64}", expected_hash) is not None,
                f"invalid rerun provenance hash for {relative_source}")
        require_equal(sha256(source_path), expected_hash,
                      f"rerun provenance source hash {relative_source}")

    expected_runs = {
        "char2_velu_identity_fixture": ("admitted_control", "RESULT=PASS"),
        "k163_degree45641_horizontal_control": (
            "admitted_control", "RESULT=PASS"
        ),
        "k163_degree45641_relative_tower_probe": (
            "admitted_pre_map_probe", "STOP=before_kernel_polynomial_and_point_map"
        ),
        "k163_degree45641_absolute_seed_preflight": (
            "admitted_preflight",
            "SEED_PREFLIGHT expected=PASS historical_allow_list_match=0",
        ),
        "k163_degree45641_seed_endpoint_validator": (
            "admitted_endpoint_certificate", "ENDPOINT_FLOOR_CERTIFICATE PASS"
        ),
        "k163_degree45641_relative_witness_replay": (
            "admitted_retained_input_replay", "RESULT=PASS"
        ),
        "m37_degree73_map_dual_control": (
            "admitted_positive_control", "MAP73_DUAL_CONTROL PASS"
        ),
    }
    runs = {row["id"]: row for row in provenance["runs"]}
    require_equal(len(runs), len(provenance["runs"]),
                  "K-163 rerun provenance run-id uniqueness")
    require_equal(set(runs), set(expected_runs),
                  "K-163 rerun provenance retained-run set")
    output_hashes_checked = 0
    receipt_hashes_checked = 0
    for run_id, (expected_status, success_marker) in expected_runs.items():
        row = runs[run_id]
        verify_execution_metadata(row, f"retained run {run_id}")
        require_equal(row["validity"]["status"], expected_status,
                      f"rerun provenance validity status {run_id}")
        require_equal(row["resources"]["exit_status"], 0,
                      f"rerun provenance exit status {run_id}")
        require(row["source_set"], f"empty rerun provenance source set {run_id}")
        require(set(row["source_set"]) <= set(source_files),
                f"unhashed source in rerun provenance run {run_id}")
        stdout_stderr = row["stdout_stderr"]
        if "path" in stdout_stderr:
            output_path = (provenance_path.parent / stdout_stderr["path"]).resolve()
            require(output_path.is_file(),
                    f"missing rerun provenance output {stdout_stderr['path']}")
            require_equal(sha256(output_path), stdout_stderr["sha256"],
                          f"rerun provenance output hash {run_id}")
            output_text = output_path.read_text()
        else:
            output_text = stdout_stderr["combined_output"]
            embedded_hash = hashlib.sha256(output_text.encode()).hexdigest()
            require_equal(embedded_hash, stdout_stderr["sha256"],
                          f"rerun provenance embedded-output hash {run_id}")
        output_hashes_checked += 1
        require(success_marker in output_text,
                f"rerun provenance success marker missing for {run_id}")
        require("exit_status=0" in output_text,
                f"rerun provenance output exit marker missing for {run_id}")
        if "receipt" in row:
            receipt_path = (provenance_path.parent / row["receipt"]["path"]).resolve()
            require(receipt_path.is_file(),
                    f"missing rerun provenance receipt {row['receipt']['path']}")
            require_equal(sha256(receipt_path), row["receipt"]["sha256"],
                          f"rerun provenance receipt hash {run_id}")
            receipt_hashes_checked += 1

    expected_direct_markers = {
        "direct_small": "reason=use_run_check_char2_velu_function_identity_small_driver",
        "direct_horizontal": "reason=use_run_control163_45641_horizontal_endomorphism_driver",
        "direct_relative": "reason=use_run_probe163_45641_relative_tower_driver",
        "direct_seed": "reason=use_run_probe163_45641_seed_driver",
        "direct_endpoint": "reason=use_run_verify163_45641_seed_endpoint_driver",
    }
    expected_fault_ids = {f"fault_{suffix}" for suffix in (
        "small", "horizontal", "relative", "seed", "endpoint"
    )}
    expected_missing_ids = {f"missing_sentinel_{suffix}" for suffix in (
        "small", "horizontal", "relative", "seed", "endpoint"
    )}
    expected_check_ids = (
        set(expected_direct_markers) | expected_fault_ids |
        expected_missing_ids | {"shared_process_reset"}
    )
    checks = {row["id"]: row for row in provenance["fail_closed_checks"]}
    require_equal(len(checks), len(provenance["fail_closed_checks"]),
                  "K-163 rerun provenance fail-closed id uniqueness")
    require_equal(set(checks), expected_check_ids,
                  "K-163 rerun provenance fail-closed check set")
    for check_id, row in checks.items():
        verify_execution_metadata(row, f"fail-closed check {check_id}")
        output_text = row["combined_output"]
        require_equal(hashlib.sha256(output_text.encode()).hexdigest(),
                      row["output_sha256"],
                      f"rerun provenance fail-closed output hash {check_id}")
        output_hashes_checked += 1
        if check_id == "shared_process_reset":
            require_equal(row["exit_status"], 0,
                          "shared-process reset exit status")
            require_equal(row["validity"], "pass_driver_state_reset",
                          "shared-process reset validity")
            require("SHARED_PROCESS_RESET=PASS" in output_text,
                    "shared-process reset marker missing")
            require("exit_status=0" in output_text,
                    "shared-process reset output exit marker missing")
            continue
        require_equal(row["exit_status"], 1,
                      f"fail-closed exit status {check_id}")
        require_equal(row["validity"], "pass_expected_rejection",
                      f"fail-closed validity {check_id}")
        require("exit_status=1" in output_text,
                f"fail-closed output exit marker missing for {check_id}")
        if check_id in expected_direct_markers:
            require(expected_direct_markers[check_id] in output_text,
                    f"direct-execution rejection marker missing for {check_id}")
        elif check_id in expected_fault_ids:
            require("reason=uncaught_gp_exception" in output_text and
                    "injected fail-closed fault" in output_text,
                    f"injected-fault rejection marker missing for {check_id}")
        else:
            require("EARLY_RETURN_CONTROL=BODY_RETURNED_WITHOUT_SENTINEL" in
                    output_text and
                    "reason=implementation_returned_without_completion_sentinel" in
                    output_text,
                    f"missing-sentinel rejection marker missing for {check_id}")
        suffix = check_id.removeprefix("missing_sentinel_")
        suffix = suffix.removeprefix("direct_").removeprefix("fault_")
        forbidden_success_marker = {
            "small": "RESULT=PASS",
            "horizontal": "RESULT=PASS",
            "relative": "RESULT=PASS",
            "seed": "SEED_PREFLIGHT expected=PASS",
            "endpoint": "ENDPOINT_FLOOR_CERTIFICATE PASS",
        }[suffix]
        require(forbidden_success_marker not in output_text,
                f"success sentinel leaked into rejected check {check_id}")

    require_equal(
        provenance["claim_boundary"],
        "These receipts establish controls, endpoint and kernel-line preflight "
        "evidence. They do not establish a complete K-163 or K-283 vertical "
        "map-plus-dual transfer, a cheaper ECDLP, or a weak standardized curve.",
        "K-163 rerun provenance claim boundary",
    )
    return {
        "retained_runs": len(runs),
        "fail_closed_checks": len(checks),
        "source_hashes": len(source_files),
        "output_hashes": output_hashes_checked,
        "receipt_hashes": receipt_hashes_checked,
    }


def verify_measured_effects(panel: dict[str, Any]) -> dict[str, int]:
    effects = {row["comparison_id"]: row for row in panel["measured_effects"]}
    require_equal(len(effects), len(panel["measured_effects"]),
                  "measured-effect id uniqueness")

    level_source = read_json(
        "research/isogeny_volcano_level_replication_20261013/results.json"
    )
    level_index = {
        (row["study"], row["factor"], row["context"]): row
        for row in level_source["contrasts"]
        if row["kind"] == "vertical_edge" and row["metric"] == "ops"
    }
    level_specs = {
        "m37-73-other-absent": ("m37", "73", "other_factor_absent"),
        "m37-73-other-present": ("m37", "73", "other_factor_present"),
        "m37-2663-other-absent": ("m37", "2663", "other_factor_absent"),
        "m37-2663-other-present": ("m37", "2663", "other_factor_present"),
        "m41-409-other-absent": ("m41", "409", "other_factor_absent"),
        "m41-409-other-present": ("m41", "409", "other_factor_present"),
        "m41-1721-other-absent": ("m41", "1721", "other_factor_absent"),
        "m41-1721-other-present": ("m41", "1721", "other_factor_present"),
    }
    for comparison_id, key in level_specs.items():
        archived = level_index[key]
        row = effects[comparison_id]
        require_equal(row["estimate_bits"], archived["log2_ratio"],
                      f"{comparison_id} estimate")
        require_equal(row["ci_lower_bits"], archived["pointwise95_bits_lo"],
                      f"{comparison_id} lower CI")
        require_equal(row["ci_upper_bits"], archived["pointwise95_bits_hi"],
                      f"{comparison_id} upper CI")

    accepted_source = read_json(
        "research/isogeny_volcano_m51_rho_20261013/analysis.json"
    )
    require_equal(accepted_source["status"], "VALID_FOR_SCOPED_INFERENCE",
                  "m51 accepted source status")
    accepted = next(
        row for row in accepted_source["contrasts"]
        if row["contrast_id"] == "primary-floor-tau17-vs-crater-tau17"
    )
    row = effects["m51-271-same-tau17-accepted"]
    require_equal(row["estimate_bits"], accepted["observed_bits"],
                  "m51 accepted estimate")
    require_equal(row["ci_lower_bits"], accepted["ci95_low"],
                  "m51 accepted lower CI")
    require_equal(row["ci_upper_bits"], accepted["ci95_high"],
                  "m51 accepted upper CI")

    deep_source = read_json(
        "research/isogeny_volcano_m51_deep_rho_20261013/analysis.json"
    )
    require_equal(deep_source["status"], "aa_alert_labels_withheld",
                  "m51 deep source status")
    deep_index = {row["id"]: row for row in deep_source["contrasts"]}
    deep_specs = {
        "m51-deep-271-other-absent": "A-C",
        "m51-deep-120871-other-absent": "P-C",
        "m51-deep-120871-other-present": "B-A",
        "m51-deep-271-other-present": "B-P",
    }
    for comparison_id, source_id in deep_specs.items():
        archived = deep_index[source_id]
        row = effects[comparison_id]
        require_equal(row["estimate_bits"], archived["bits"],
                      f"{comparison_id} estimate")
        require_equal(row["ci_lower_bits"], archived["modeled_population_lower_bits"],
                      f"{comparison_id} lower CI")
        require_equal(row["ci_upper_bits"], archived["modeled_population_upper_bits"],
                      f"{comparison_id} upper CI")
        require_equal(row["inference_status"], "withheld_aa_gate_failed",
                      f"{comparison_id} inference gate")
    require_equal(set(effects), set(level_specs) | {
        "m51-271-same-tau17-accepted", *deep_specs
    }, "measured-effect row set")
    return {"admitted_rows": 9, "withheld_rows": 4}


def extract_seconds(path: str, pattern: str) -> list[int]:
    text = (ROOT / path).read_text()
    return [int(value) for value in re.findall(pattern, text, flags=re.MULTILINE)]


def extract_decimal_seconds(path: str, pattern: str) -> list[float]:
    text = (ROOT / path).read_text()
    return [float(value) for value in re.findall(pattern, text, flags=re.MULTILINE)]


def verify_construction_measurements(panel: dict[str, Any]) -> dict[str, int]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in panel["construction_measurements"]:
        stem, separator, suffix = row["measurement_id"].rpartition("-")
        require(separator == "-" and suffix.isdigit(),
                f"invalid measurement id {row['measurement_id']}")
        groups.setdefault(stem, []).append(row)
    for rows in groups.values():
        rows.sort(key=lambda row: row["sample_index"])
        require_equal(
            [row["sample_index"] for row in rows],
            list(range(1, len(rows) + 1)),
            f"sample indices for {rows[0]['measurement_id']}",
        )
        require(all(row["sample_count"] == len(rows) for row in rows),
                f"sample-count mismatch for {rows[0]['measurement_id']}")

    rerun_provenance = read_json(
        "research/ecc2k130_conductor_isogenies_20261007/analogues/"
        "rerun_provenance.json"
    )
    require_equal(
        rerun_provenance["schema"],
        "k163-conductor-gap-rerun-provenance-v1",
        "K-163 rerun provenance schema",
    )
    provenance_runs = {row["id"]: row for row in rerun_provenance["runs"]}
    require_equal(len(provenance_runs), len(rerun_provenance["runs"]),
                  "K-163 rerun provenance id uniqueness")

    expected: dict[str, list[float]] = {
        "m41-409": extract_seconds(
            "research/isogeny_volcano_rho_m41_20261006/v409.out",
            r"^VERT409 .* (\d+) s$",
        ),
        "m41-1721": extract_seconds(
            "research/isogeny_volcano_rho_m41_20261006/v1721.out",
            r"^VERT1721 .* (\d+) s$",
        ),
        "m41-409floor-1721": extract_seconds(
            "research/ecc2k130_conductor_isogenies_20261007/second_level/down41.out",
            r"isogeny \d+:.*\((\d+) s\)",
        ),
        "m83-6473-cm": extract_seconds(
            "research/ecc2k130_conductor_isogenies_20261007/cm_route/cm83.out",
            r"polclass.*?, (\d+) s$",
        ),
        "m101-5857-cm": extract_seconds(
            "research/ecc2k130_conductor_isogenies_20261007/survey/run_m101_a1_f5857.out",
            r"polclass.*?, (\d+) s$",
        ),
        "m101-18583-cm": extract_seconds(
            "research/ecc2k130_conductor_isogenies_20261007/survey/run_m101_a1_f18583.out",
            r"polclass.*?, (\d+) s$",
        ),
        "m103-11329-cm": extract_seconds(
            "research/ecc2k130_conductor_isogenies_20261007/survey/run_m103_a0_f11329.out",
            r"polclass.*?, (\d+) s$",
        ),
        "m107a0-3209-cm": extract_seconds(
            "research/ecc2k130_conductor_isogenies_20261007/survey/run_m107_a0_f3209.out",
            r"polclass.*?, (\d+) s$",
        ),
        "m107a1-3209-cm": extract_seconds(
            "research/ecc2k130_conductor_isogenies_20261007/survey/run_m107_a1_f3209.out",
            r"polclass.*?, (\d+) s$",
        ),
        "k163-45641": extract_seconds(
            "research/ecc2k130_conductor_isogenies_20261007/analogues/run163_45641.out",
            r"isogeny \d+:.*\((\d+) s\)",
        ),
        "k163-82153": extract_seconds(
            "research/ecc2k130_conductor_isogenies_20261007/analogues/run163_82153.out",
            r"isogeny \d+:.*\((\d+) s\)",
        ),
        "k163-45641-relative-probe": extract_decimal_seconds(
            "research/ecc2k130_conductor_isogenies_20261007/analogues/"
            "probe163_45641_relative_tower.out",
            r"^TIME .*wall_seconds=([0-9]+(?:\.[0-9]+)?) ",
        ),
        "k163-45641-horizontal-control": extract_decimal_seconds(
            "research/ecc2k130_conductor_isogenies_20261007/analogues/"
            "control163_45641_horizontal_endomorphism.out",
            r"^TIME .*wall_seconds=([0-9]+(?:\.[0-9]+)?) ",
        ),
        "k163-45641-seed-preflight": extract_decimal_seconds(
            "research/ecc2k130_conductor_isogenies_20261007/analogues/"
            "probe163_45641_seed.out",
            r"^TIME .*wall_seconds=([0-9]+(?:\.[0-9]+)?) ",
        ),
        "k163-45641-endpoint-validator": extract_decimal_seconds(
            "research/ecc2k130_conductor_isogenies_20261007/analogues/"
            "verify163_45641_seed_endpoint.out",
            r"^TIME .*wall_seconds=([0-9]+(?:\.[0-9]+)?) ",
        ),
        "m37-73-map-dual-control": [
            float(provenance_runs["m37_degree73_map_dual_control"]
                  ["resources"]["wall_seconds"])
        ],
    }
    level2_paths = [
        "down163b.out", "down163c.out", "down163_s1.out",
        "down163_s2.out", "down163_s3.out", "down163_s4.out",
    ]
    expected["k163-level2-82153"] = [
        extract_seconds(
            "research/ecc2k130_conductor_isogenies_20261007/second_level/" + path,
            r"isogeny \d+:.*\((\d+) s\)",
        )[0]
        for path in level2_paths
    ]
    scan_session = read_json(
        "research/isogeny_volcano_m51_deep_scan_20261013/results/session.json"
    )
    scan_receipt = read_json(
        "research/isogeny_volcano_m51_deep_scan_20261013/results/classification-receipt.json"
    )
    require_equal(scan_session["sieve_hits"], 42, "m51 deep scan hit count")
    require_equal(scan_receipt["certified_pairs"], 42,
                  "m51 deep scan certified-pair count")
    expected["m51-deep-scan"] = [scan_session["elapsed_seconds"]]
    require_equal(set(groups), set(expected), "construction measurement group set")
    for name, times in expected.items():
        require_equal([row["elapsed_seconds"] for row in groups[name]], times,
                      f"construction times for {name}")

    conditional = groups["m41-409floor-1721"]
    require(all("exclude the separately logged 5-second embedding" in row["note"]
                for row in conditional), "m41 embedding exclusion not disclosed")
    level2 = groups["k163-level2-82153"]
    require(all("exclude each separately logged 29-second embedding" in row["note"]
                for row in level2), "K163 embedding exclusion not disclosed")
    scan = groups["m51-deep-scan"][0]
    require_equal(scan["source_f_E"], str(271 * 120871),
                  "m51 scan observed source conductor")
    require_equal(scan["target_f_E"], "120871",
                  "m51 scan observed target conductor")
    require("ascending bottom-to-parent" in scan["note"],
            "m51 scan direction not disclosed")

    relative_path = (
        "research/ecc2k130_conductor_isogenies_20261007/analogues/"
        "probe163_45641_relative_tower.out"
    )
    relative_text = (ROOT / relative_path).read_text()
    for marker in (
        "SCHEMA=k163-degree45641-relative-tower-probe-v2",
        "setup_ms=17",
        "exact_order=45641 relative_x_degree=20",
        "witness_ms=4628",
        "ABSOLUTE_X_ORBIT degree=3260 closure=PASS "
        "excluded_degrees=[1630, 652, 20] exclusions=[1, 1, 1] "
        "all_nonzero_kernel_multiples=DERIVED orbit_ms=62",
        "classification=descending classification_basis=DERIVED "
        "target_conductor=45641",
        "point_count=PASS half_kernel_count=22820 inversion_batches=90 "
        "endpoint_ms=51995",
        "STOP=before_kernel_polynomial_and_point_map",
        "RESULT=PASS",
        "wall_seconds=56.65 max_rss_kib=23724 exit_status=0",
    ):
        require(marker in relative_text,
                f"K-163 relative-tower evidence missing {marker!r}")

    historical_text = (
        ROOT / "research/ecc2k130_conductor_isogenies_20261007/analogues/"
        "run163_45641.out"
    ).read_text()
    seed_text = (
        ROOT / "research/ecc2k130_conductor_isogenies_20261007/analogues/"
        "probe163_45641_seed.out"
    ).read_text()
    seed_endpoint_verifier_text = (
        ROOT / "research/ecc2k130_conductor_isogenies_20261007/analogues/"
        "verify163_45641_seed_endpoint.out"
    ).read_text()
    historical_minima = [
        int(value)
        for value in re.findall(r"Galois-orbit min\) = (\d+)", historical_text)
    ]
    require_equal(len(historical_minima), 6,
                  "K-163 historical degree-45,641 endpoint count")
    seed_match = re.search(r"Galois-orbit min\) = (\d+)", seed_text)
    relative_match = re.search(r"ENDPOINT .* orbit_min=(\d+)", relative_text)
    require(seed_match is not None, "K-163 seed endpoint minimum missing")
    require(relative_match is not None,
            "K-163 relative endpoint minimum missing")
    endpoint_minima = historical_minima + [
        int(seed_match.group(1)), int(relative_match.group(1))
    ]
    require_equal(len(set(endpoint_minima)), 8,
                  "K-163 distinct degree-45,641 endpoint minima")
    require("ENDPOINT_FLOOR_CERTIFICATE PASS" in seed_endpoint_verifier_text,
            "K-163 fresh seed endpoint certificate missing")
    endpoint_binding = re.search(r"^ENDPOINT_B (\d+)$",
                                 seed_endpoint_verifier_text, re.MULTILINE)
    require(endpoint_binding is not None,
            "K-163 seed endpoint verifier binding missing")
    require_equal(int(endpoint_binding.group(1)), int(seed_match.group(1)),
                  "K-163 seed endpoint verifier identity")
    require("SEED_PREFLIGHT expected=PASS historical_allow_list_match=0" in seed_text,
            "K-163 seed preflight status missing")
    require("wall_seconds=56.09 max_rss_kib=45832 exit_status=0" in seed_text,
            "K-163 seed preflight resource receipt missing")
    require("wall_seconds=90.66 max_rss_kib=33368 exit_status=0" in
            seed_endpoint_verifier_text,
            "K-163 seed endpoint verifier resource receipt missing")
    k163_gap = next(
        row for row in panel["gaps"]
        if row["class_id"] == "nist-k163" and int(row["edge_degree"]) == 45641
    )
    require_equal(
        k163_gap["endpoint_status"],
        "six_historical_plus_two_fresh_preflight_endpoint_samples_"
        "map_not_retained",
        "K-163 degree-45,641 endpoint status",
    )
    relative = groups["k163-45641-relative-probe"][0]
    require_equal(relative["class_id"], "nist-k163",
                  "K-163 relative probe class")
    require_equal(relative["edge_degree"], "45641",
                  "K-163 relative probe degree")
    require_equal((relative["source_f_E"], relative["target_f_E"]),
                  ("1", "45641"), "K-163 relative probe direction")
    require_equal(relative["route"], "relative_tower_pre_map_probe",
                  "K-163 relative probe route")
    require_equal(
        relative["scope"],
        "bounded_pre_map_probe_not_kernel_polynomial_or_point_map",
        "K-163 relative probe scope",
    )
    require_equal(relative["max_rss_kib"], 23724,
                  "K-163 relative probe peak RSS")
    require_equal(relative["exit_status"], 0,
                  "K-163 relative probe exit status")
    require_equal(
        relative["certificate_status"],
        "concrete_exact_x_orbit_descending_witness_and_half_kernel_pass",
        "K-163 relative probe certificate status",
    )
    require_equal(
        relative["work_units"],
        {"half_kernel_x_values": 22820, "inversion_batches": 90},
        "K-163 relative probe work units",
    )
    require_equal(
        relative["phase_elapsed_ms"],
        {
            "field_setup": 17,
            "witness_including_absolute_orbit_and_classification": 4628,
            "absolute_orbit_nested": 62,
            "endpoint_and_half_kernel": 51995,
        },
        "K-163 relative probe phase timings",
    )
    require_equal(
        relative["phase_accounting"],
        "absolute_orbit_nested_is_included_in_witness_timer",
        "K-163 relative probe nested phase accounting",
    )
    require_equal(
        relative["absolute_x_orbit_certificate"],
        {
            "degree": 3260,
            "closure": "pass",
            "excluded_degrees": [1630, 652, 20],
            "all_nonzero_kernel_multiples": "derived",
        },
        "K-163 concrete absolute x-orbit certificate",
    )
    require_equal(relative["stop_boundary"],
                  "before_kernel_polynomial_and_point_map",
                  "K-163 relative probe stop boundary")

    witness_verifier_path = (
        "research/ecc2k130_conductor_isogenies_20261007/analogues/"
        "verify163_45641_relative_witness.out"
    )
    witness_verifier_text = (ROOT / witness_verifier_path).read_text()
    for marker in (
        "SCHEMA=k163-degree45641-relative-witness-verifier-v1",
        "base_irreducible=PASS base_closure=PASS",
        "relative_irreducible_over_f2=PASS "
        "relative_irreducible_over_base=PASS relative_generator_degree=20",
        "coefficient_count=20 base_encoding=low_to_high_bits round_trip=PASS",
        "exact_x_order=45641 relative_x_degree=20 q_scalar=7196 "
        "q_scalar_action=PASS",
        "classification=descending classification_basis=DERIVED",
        "ABSOLUTE_X_DEGREE degree=3260 closure=PASS "
        "excluded_degrees=[1630, 652, 20] exclusions=[1, 1, 1]",
        "quantified_nonzero_multipliers=45640 inherited_absolute_x_degree=3260 "
        "status=DERIVED",
        "NEGATIVE_CONTROL kind=drop_u19_coefficient exact_order_gate=REJECT",
        "CLAIM_BOUNDARY=verifies_retained_kernel_line_not_isogeny_map_or_ecdlp_advantage",
        "setup_ms=29",
        "VERIFY_MS=321",
        "RESULT=PASS",
        "wall_seconds=0.36 max_rss_kib=21248 exit_status=0",
    ):
        require(marker in witness_verifier_text,
                f"K-163 retained-input witness replay missing {marker!r}")

    horizontal_path = (
        "research/ecc2k130_conductor_isogenies_20261007/analogues/"
        "control163_45641_horizontal_endomorphism.out"
    )
    horizontal_text = (ROOT / horizontal_path).read_text()
    for marker in (
        "SCHEMA=k163-degree45641-horizontal-control-v1",
        "alpha=[51,-160] dual=[-109,160] product=[45641, 0] degree=45641 "
        "direction=horizontal",
        "COMPOSITIONS samples=1024 left=PASS right=PASS elapsed_ms=6845",
        "CLAIM_BOUNDARY=same_degree_horizontal_control_not_conductor_transfer",
        "RESULT=PASS",
        "wall_seconds=6.86 max_rss_kib=16140 exit_status=0",
    ):
        require(marker in horizontal_text,
                f"K-163 horizontal-control evidence missing {marker!r}")
    horizontal = groups["k163-45641-horizontal-control"][0]
    require_equal(horizontal["class_id"], "nist-k163",
                  "K-163 horizontal control class")
    require_equal(horizontal["edge_degree"], "45641",
                  "K-163 horizontal control degree")
    require_equal((horizontal["source_f_E"], horizontal["target_f_E"]),
                  ("1", "1"), "K-163 horizontal control placement")
    require_equal(
        horizontal["route"], "same_degree_horizontal_endomorphism_control",
        "K-163 horizontal control route",
    )
    require_equal(
        horizontal["scope"],
        "horizontal_endomorphism_control_not_conductor_transfer",
        "K-163 horizontal control scope",
    )
    require_equal(horizontal["max_rss_kib"], 16140,
                  "K-163 horizontal control peak RSS")
    require_equal(horizontal["exit_status"], 0,
                  "K-163 horizontal control exit status")
    require_equal(horizontal["certificate_status"],
                  "both_compositions_1024_targets_pass",
                  "K-163 horizontal control certificate status")
    require_equal(horizontal["work_units"], {"composition_targets": 1024},
                  "K-163 horizontal control work units")
    require_equal(horizontal["phase_elapsed_ms"], {"composition_checks": 6845},
                  "K-163 horizontal control phase timing")
    require_equal(
        horizontal["stop_boundary"],
        "same_degree_horizontal_control_not_conductor_transfer",
        "K-163 horizontal control claim boundary",
    )

    seed_preflight = groups["k163-45641-seed-preflight"][0]
    require_equal(
        (seed_preflight["class_id"], seed_preflight["edge_degree"],
         seed_preflight["source_f_E"], seed_preflight["target_f_E"]),
        ("nist-k163", "45641", "1", "45641"),
        "K-163 seed preflight identity and direction",
    )
    require_equal(seed_preflight["route"], "absolute_field_endpoint_preflight",
                  "K-163 seed preflight route")
    require_equal(seed_preflight["scope"],
                  "bounded_seed_preflight_endpoint_only_not_point_map",
                  "K-163 seed preflight scope")
    require_equal(seed_preflight["max_rss_kib"], 45832,
                  "K-163 seed preflight peak RSS")
    require_equal(seed_preflight["certificate_status"],
                  "fresh_endpoint_preflight_pass",
                  "K-163 seed preflight certificate status")
    require_equal(seed_preflight["exit_status"], 0,
                  "K-163 seed preflight exit status")
    require_equal(seed_preflight["work_units"], {"endpoint_orbits": 1},
                  "K-163 seed preflight work units")
    require_equal(seed_preflight["stop_boundary"],
                  "before_kernel_polynomial_and_point_map",
                  "K-163 seed preflight stop boundary")

    endpoint_validator = groups["k163-45641-endpoint-validator"][0]
    require_equal(
        (endpoint_validator["class_id"], endpoint_validator["edge_degree"],
         endpoint_validator["source_f_E"], endpoint_validator["target_f_E"]),
        ("nist-k163", "45641", "1", "45641"),
        "K-163 endpoint-validator identity and direction",
    )
    require_equal(endpoint_validator["route"], "endpoint_floor_certificate",
                  "K-163 endpoint-validator route")
    require_equal(endpoint_validator["scope"],
                  "endpoint_certificate_not_point_map_or_transfer",
                  "K-163 endpoint-validator scope")
    require_equal(endpoint_validator["max_rss_kib"], 33368,
                  "K-163 endpoint-validator peak RSS")
    require_equal(endpoint_validator["certificate_status"],
                  "endpoint_floor_certificate_pass",
                  "K-163 endpoint-validator certificate status")
    require_equal(endpoint_validator["exit_status"], 0,
                  "K-163 endpoint-validator exit status")
    require_equal(endpoint_validator["work_units"], {"endpoint_certificates": 1},
                  "K-163 endpoint-validator work units")
    require_equal(endpoint_validator["stop_boundary"],
                  "endpoint_certificate_not_point_map_or_transfer",
                  "K-163 endpoint-validator stop boundary")

    map73_text = (
        ROOT / "research/isogeny_volcano_rho_20261005/map73_dual_control.out"
    ).read_text()
    for marker in (
        '\"m37-degree73-dual-control-v1\"',
        '[\"status\", \"PASS\"]',
        '[\"forward_kernel_degree\", 36]',
        '[\"dual_kernel_degree\", 36]',
        '[\"target_count\", 1024]',
        '[\"dual_o_forward_passes\", 1024]',
        '[\"forward_o_dual_passes\", 1024]',
        '[\"inverse_degree_recovery_passes\", 1024]',
        '[\"planted_recovery\", \"PASS\"]',
        '[\"forward_construction_ms\", 530]',
        '[\"dual_construction_ms\", 24604]',
        '[\"target_checks_ms\", 556]',
    ):
        require(marker in map73_text,
                f"degree-73 forward/dual control missing {marker!r}")
    map73 = groups["m37-73-map-dual-control"][0]
    require_equal((map73["class_id"], map73["edge_degree"]),
                  ("koblitz-m37-a0", "73"),
                  "degree-73 map/dual control identity")
    require_equal((map73["source_f_E"], map73["target_f_E"]), ("1", "73"),
                  "degree-73 map/dual control direction")
    require_equal(map73["route"], "forward_map_dual_positive_control",
                  "degree-73 map/dual control route")
    require_equal(
        map73["scope"],
        "small_map_dual_and_recovery_positive_control_not_nist_transfer",
        "degree-73 map/dual control scope",
    )
    require_equal(map73["max_rss_kib"], 39708,
                  "degree-73 map/dual control peak RSS")
    require_equal(map73["exit_status"], 0,
                  "degree-73 map/dual control exit status")
    require_equal(map73["certificate_status"],
                  "map_dual_compositions_and_recovery_pass",
                  "degree-73 map/dual control certificate status")
    require_equal(map73["work_units"], {"targets": 1024, "planted_recoveries": 1},
                  "degree-73 map/dual control work units")
    require_equal(map73["phase_elapsed_ms"], {
        "forward_construction": 530,
        "dual_construction": 24604,
        "target_checks": 556,
    }, "degree-73 map/dual control phase timings")
    require_equal(map73["stop_boundary"],
                  "small_degree_positive_control_not_nist_transfer",
                  "degree-73 map/dual control claim boundary")
    map73_provenance = provenance_runs["m37_degree73_map_dual_control"]
    require_equal(map73_provenance["resources"], {
        "user_seconds": 25.7,
        "system_seconds": 0.69,
        "wall_seconds": 26.39,
        "max_rss_kib": 39708,
        "exit_status": 0,
    }, "degree-73 map/dual provenance resources")
    require_equal(map73_provenance["validity"]["status"],
                  "admitted_positive_control",
                  "degree-73 map/dual provenance status")
    return {
        "series": len(groups),
        "rows": len(panel["construction_measurements"]),
        "proxy_map_dual_controls": 1,
    }


def verify_panel() -> dict[str, Any]:
    panel = json.loads(PANEL_PATH.read_text())
    require_equal(panel["schema"], PANEL_SCHEMA, "panel schema")
    source_count = verify_source_hashes(panel)
    provenance_receipt = verify_rerun_provenance()

    classes = panel["classes"]
    gaps = panel["gaps"]
    levels = panel["levels"]
    adjacencies = panel["adjacencies"]
    controls = panel["controls"]
    summary = panel["summary"]
    class_by_id = {row["class_id"]: row for row in classes}
    require_equal(len(class_by_id), len(classes), "class id uniqueness")

    top_level_primes = sorted({int(row["edge_degree"]) for row in gaps})
    for prime in top_level_primes:
        prove_prime(prime)

    nist = read_json("research/endosweep_nist_20261006/nist.json")
    nist_names = {
        "nist-k163": "nist/K-163", "nist-k233": "nist/K-233",
        "nist-k283": "nist/K-283", "nist-k409": "nist/K-409",
        "nist-k571": "nist/K-571",
    }
    class_receipts: list[dict[str, Any]] = []
    for row in classes:
        match = re.fullmatch(r"y\^2\+xy=x\^3\+([01])\*x\^2\+1", row["curve_model"])
        require(match is not None, f"unrecognized curve model {row['curve_model']}")
        a = int(match.group(1))
        mu = 1 if a else -1
        m = int(row["extension_degree"])
        x, y = tau_power_linear(m, mu)
        q = 1 << m
        trace = 2 * x + mu * y
        f_pi = abs(y)
        factors = [int(value) for value in row["f_pi_factorization"]]
        require_equal(len(factors), len(set(factors)),
                      f"squarefree factor list for {row['class_id']}")
        require_equal(product(factors), f_pi, f"factor product for {row['class_id']}")
        require_equal(int(row["q"]), q, f"q for {row['class_id']}")
        require_equal(int(row["trace"]), trace, f"trace for {row['class_id']}")
        require_equal(int(row["ambient_order"]), q + 1 - trace,
                      f"ambient order for {row['class_id']}")
        require_equal(int(row["f_pi"]), f_pi, f"f_pi for {row['class_id']}")
        require_equal(trace * trace - 4 * q, -7 * f_pi * f_pi,
                      f"CM discriminant identity for {row['class_id']}")
        require_equal(row["D_K"], "-7", f"D_K for {row['class_id']}")
        require_equal(row["source_f_E"], "1", f"source order for {row['class_id']}")
        require_equal(row["prime_factor_count"], len(factors),
                      f"factor count for {row['class_id']}")
        require_equal(row["conductor_level_count"], 1 << len(factors),
                      f"level count for {row['class_id']}")
        require_equal(row["conditional_adjacency_count"],
                      len(factors) * (1 << (len(factors) - 1)),
                      f"adjacency count for {row['class_id']}")
        expected_class_number = product(
            [prime - kronecker_minus_7(prime) for prime in factors]
        )
        require_equal(int(row["global_bottom_class_number"]), expected_class_number,
                      f"bottom class number for {row['class_id']}")
        if row["class_id"] in nist_names:
            archived = nist["curves"][nist_names[row["class_id"]]]
            require_equal(q, int(archived["q"]), f"NIST q for {row['class_id']}")
            require_equal(trace, int(archived["t"]), f"NIST trace for {row['class_id']}")
            require_equal(f_pi, int(archived["exact"]["f"]),
                          f"NIST f_pi for {row['class_id']}")
            require_equal(a, int(archived["a"]), f"NIST a for {row['class_id']}")
        class_receipts.append({
            "class_id": row["class_id"], "m": m, "trace": str(trace),
            "f_pi": str(f_pi), "factor_count": len(factors),
            "discriminant_identity": "t^2-4q=-7*f_pi^2",
        })

    gap_by_key: dict[tuple[str, int], dict[str, Any]] = {}
    gap_receipts: list[dict[str, Any]] = []
    working_field_receipts: list[dict[str, Any]] = []
    for row in gaps:
        key = (row["class_id"], int(row["edge_degree"]))
        require(key not in gap_by_key, f"duplicate gap row {key}")
        gap_by_key[key] = row
        curve_class = class_by_id[row["class_id"]]
        ell = key[1]
        require(ell in [int(value) for value in curve_class["f_pi_factorization"]],
                f"gap prime {ell} absent from {row['class_id']} conductor")
        chi = kronecker_minus_7(ell)
        split = {1: "split", -1: "inert", 0: "ramified"}[chi]
        require_equal(row["kronecker_minus_7"], chi, f"Kronecker for {row['gap_id']}")
        require_equal(row["split_type"], split, f"split type for {row['gap_id']}")
        m = int(curve_class["extension_degree"])
        a = int(re.search(r"x\^3\+([01])\*x\^2", curve_class["curve_model"]).group(1))
        x, _ = tau_power_linear(m, 1 if a else -1)
        scalar = x % ell
        require_equal(int(row["q_frobenius_scalar_mod_ell"]), scalar,
                      f"Frobenius scalar for {row['gap_id']}")
        scalar_order = exact_multiplicative_order(scalar, ell)
        k = scalar_order // 2 if scalar_order % 2 == 0 else scalar_order
        sign = pow(scalar, k, ell)
        require(sign in {1, ell - 1}, f"invalid +/-1 power for {row['gap_id']}")
        require_equal(int(row["scalar_order_mod_ell"]), scalar_order,
                      f"scalar order for {row['gap_id']}")
        require_equal(int(row["relative_kernel_x_field_degree"]), k,
                      f"minimal kernel x-field degree for {row['gap_id']}")
        require_equal(int(row["ambient_absolute_x_degree_upper_bound"]), m * k,
                      f"ambient absolute x-degree bound for {row['gap_id']}")
        working_field_receipt = verify_working_field_certificate(
            row, ell, m, 1 if a else -1, scalar, k
        )
        working_field_receipts.append({
            "gap_id": row["gap_id"],
            **working_field_receipt,
        })
        require_equal(row["kernel_support"],
                      "source_curve" if sign == 1 else "quadratic_twist",
                      f"kernel support for {row['gap_id']}")
        kernel_degree = (ell - 1) // 2
        require_equal(int(row["kernel_polynomial_degree"]), kernel_degree,
                      f"kernel degree for {row['gap_id']}")
        require_equal(int(row["dense_packed_kernel_bytes"]),
                      (m * (kernel_degree + 1) + 7) // 8,
                      f"packed-kernel proxy for {row['gap_id']}")
        require_equal(int(row["local_ring_class_number"]), ell - chi,
                      f"local class number for {row['gap_id']}")
        require(math.isclose(row["gap_log2"], math.log2(ell),
                             rel_tol=0.0, abs_tol=1e-15),
                f"gap log2 for {row['gap_id']}")
        require_equal(row["valuation_in_f_pi"], 1,
                      f"conductor valuation for {row['gap_id']}")
        gap_receipts.append({
            "gap_id": row["gap_id"], "ell": str(ell), "split_type": split,
            "scalar_order": str(scalar_order), "minimal_k": str(k),
            "working_field_status": row["working_field_status"],
        })

    expected_gaps = {
        (row["class_id"], int(prime))
        for row in classes for prime in row["f_pi_factorization"]
    }
    require_equal(set(gap_by_key), expected_gaps, "complete class-prime gap set")
    require(EXACT_WORKING_FIELD_KEYS <= set(gap_by_key),
            "exact working-field certificate key absent from gap panel")

    level_by_key: dict[tuple[str, int], dict[str, Any]] = {}
    expected_level_keys: set[tuple[str, int]] = set()
    expected_adjacency_keys: set[tuple[str, int, int, int]] = set()
    for curve_class in classes:
        class_id = curve_class["class_id"]
        factors = [int(value) for value in curve_class["f_pi_factorization"]]
        for mask in range(1 << len(factors)):
            selected = [p for index, p in enumerate(factors) if mask & (1 << index)]
            f_e = product(selected)
            expected_level_keys.add((class_id, f_e))
            for index, ell in enumerate(factors):
                if not mask & (1 << index):
                    expected_adjacency_keys.add((class_id, f_e, f_e * ell, ell))
    for row in levels:
        key = (row["class_id"], int(row["f_E"]))
        require(key not in level_by_key, f"duplicate level row {key}")
        level_by_key[key] = row
        curve_class = class_by_id[row["class_id"]]
        factors = [int(value) for value in curve_class["f_pi_factorization"]]
        selected = [int(value) for value in row["f_E_factorization"]]
        require_equal(product(selected), key[1], f"level factor product for {row['level_id']}")
        require(all(prime in factors for prime in selected),
                f"foreign prime in {row['level_id']}")
        require_equal(int(row["remaining_index"]), int(curve_class["f_pi"]) // key[1],
                      f"remaining index for {row['level_id']}")
        require_equal(int(row["ring_discriminant"]), -7 * key[1] * key[1],
                      f"ring discriminant for {row['level_id']}")
        require_equal(row["distance_from_crater"], len(selected),
                      f"level depth for {row['level_id']}")
        require_equal(int(row["ring_class_number"]), product(
            [prime - kronecker_minus_7(prime) for prime in selected]
        ), f"ring class number for {row['level_id']}")
    require_equal(set(level_by_key), expected_level_keys, "complete conductor-level set")

    observed_adjacency_keys: set[tuple[str, int, int, int]] = set()
    for row in adjacencies:
        key = (
            row["class_id"], int(row["source_f_E"]),
            int(row["target_f_E"]), int(row["edge_degree"]),
        )
        require(key not in observed_adjacency_keys, f"duplicate adjacency {key}")
        observed_adjacency_keys.add(key)
        require_equal(key[1] * key[3], key[2], f"adjacency multiplication for {key}")
        require_equal(row["direction"], "descending", f"adjacency direction for {key}")
        require((key[0], key[1]) in level_by_key and (key[0], key[2]) in level_by_key,
                f"adjacency endpoints absent for {key}")
    require_equal(observed_adjacency_keys, expected_adjacency_keys,
                  "complete conditional adjacency set")

    controls_by_name = {row["curve"]: row for row in controls}
    require_equal(len(controls_by_name), len(controls), "control name uniqueness")
    exact_control_names = {
        "P-192", "P-256", "P-384", "P-521",
        "B-163", "B-233", "B-283", "B-409",
    }
    for name in exact_control_names:
        archived = nist["curves"][f"nist/{name}"]
        row = controls_by_name[name]
        require_equal(archived["exact"]["f"], 1, f"NIST exact f for {name}")
        require_equal(row["f_pi"], "1", f"control f_pi for {name}")
        require_equal(int(row["D_K"]), int(archived["exact"]["D_K"]),
                      f"control D_K for {name}")
        require_equal(int(archived["t"]) ** 2 - 4 * int(archived["q"]),
                      int(row["D_K"]), f"control discriminant for {name}")

    parameter_receipt = (
        ROOT / "research/conductor_gap_panel_20261014/"
        "sect113r1-openssl-parameters.txt"
    ).read_text()
    order_match = re.search(r"Order:\s*\n\s*([0-9a-f:]+)", parameter_receipt)
    cofactor_match = re.search(r"Cofactor:\s+(\d+)", parameter_receipt)
    require(order_match is not None, "sect113r1 order absent from OpenSSL receipt")
    require(cofactor_match is not None,
            "sect113r1 cofactor absent from OpenSSL receipt")
    q113 = 1 << 113
    n113 = int(order_match.group(1).replace(":", ""), 16)
    require_equal(int(cofactor_match.group(1)), 2, "sect113r1 cofactor")
    trace113 = q113 + 1 - 2 * n113
    discriminant113 = trace113 * trace113 - 4 * q113
    factors113 = factor_pairs(abs(discriminant113))
    require_equal(discriminant113 % 4, 1, "sect113r1 discriminant residue")
    require(all(exponent == 1 for _, exponent in factors113),
            "sect113r1 discriminant is not squarefree")
    for prime, _ in factors113:
        prove_prime(prime)
    sect113 = controls_by_name["sect113r1"]
    require_equal(int(sect113["D_K"]), discriminant113, "sect113r1 D_K")
    require_equal(sect113["f_pi"], "1", "sect113r1 f_pi")
    require_equal(controls_by_name["B-571"]["status"], "exact_conductor_unresolved",
                  "B-571 unresolved status")
    require(controls_by_name["B-571"]["f_pi"] is None,
            "B-571 must not acquire an unsupported conductor")
    b571_bound = nist["curves"]["nist/B-571"]["bound"]
    require_equal(
        int(controls_by_name["B-571"]["abs_D_K_at_least"]),
        int(b571_bound["abs_D_K_at_least"]),
        "B-571 discriminant lower bound",
    )
    require_equal(
        controls_by_name["B-571"]["log2_abs_D_K_at_least"],
        b571_bound["log2"],
        "B-571 log2 discriminant lower bound",
    )
    require_equal(
        int(controls_by_name["B-571"]["min_nonscalar_degree_at_least"]),
        int(b571_bound["min_nonscalar_degree_at_least"]),
        "B-571 nonscalar-degree lower bound",
    )

    p224 = panel["p224_candidate"]
    nist_p224 = nist["curves"]["nist/P-224"]
    require_equal(nist_p224["exact"]["f"], 3, "P-224 f_pi")
    require_equal(p224["f_pi"], "3", "P-224 panel f_pi")
    require_equal(int(nist_p224["exact"]["D_K"]) % 3, 0,
                  "P-224 ramification")
    require_equal(p224["split_type"], "ramified", "P-224 split type")
    require_equal(p224["certified_vertical_gap"], False,
                  "P-224 vertical-gap certification gate")

    effects_receipt = verify_measured_effects(panel)
    construction_receipt = verify_construction_measurements(panel)

    action_audit = read_json("docs/reports/koblitz-rho-transfer-20261013/audit.json")
    action_index = {row["curve"]: row for row in action_audit["curves"]}
    source_action_rows: list[dict[str, Any]] = []
    for curve_class in classes:
        if curve_class["family"] != "nist-k":
            continue
        short_name = curve_class["label"].removeprefix("NIST ")
        archived = action_index[short_name]
        gain = archived["random_map_model"]["signed_tau_gain_vs_negation_bits"]
        require_equal(curve_class["source_signed_tau_gain_vs_negation_bits"], gain,
                      f"signed tau gain for {curve_class['class_id']}")
        require_equal(archived["tau"]["signed_action_order"],
                      2 * int(curve_class["extension_degree"]),
                      f"signed action order for {curve_class['class_id']}")
        source_action_rows.append({
            "schema": PANEL_SCHEMA,
            "class_id": curve_class["class_id"],
            "curve": curve_class["label"],
            "m": curve_class["extension_degree"],
            "signed_tau_orbit_size": 2 * curve_class["extension_degree"],
            "ideal_gain_vs_negation_bits": gain,
            "evidence_kind": "exact_random_map_prediction",
            "scope": "source_action_not_transfer_or_wall_time",
            "evidence_path": "docs/reports/koblitz-rho-transfer-20261013/audit.json",
        })

    csv_sections = {
        "gap-panel.csv": gaps,
        "level-panel.csv": levels,
        "adjacency-panel.csv": adjacencies,
        "controls.csv": controls,
        "measured-effects.csv": panel["measured_effects"],
        "construction-measurements.csv": panel["construction_measurements"],
        "source-actions.csv": source_action_rows,
    }
    for path, rows in csv_sections.items():
        verify_csv(path, rows)

    expected_twist_families = len({
        (row["extension_degree"], tuple(row["f_pi_factorization"]))
        for row in classes
    })
    expected_summary = {
        "certified_prime_direction_rows": len(gaps),
        "vertical_direction_rows": len(gaps),
        "horizontal_direction_rows": 0,
        "horizontal_search_status": "not_assessed_in_this_panel",
        "distinct_prime_degrees": len(top_level_primes),
        "finite_field_trace_isogeny_classes": len(classes),
        "twist_deduplicated_geometry_families": expected_twist_families,
        "exact_conductor_levels": len(levels),
        "conditional_adjacent_level_rows": len(adjacencies),
        "nist_k_prime_direction_rows": sum(row["family"] == "nist-k" for row in gaps),
        "exact_absolute_x_orbit_rows": len(EXACT_WORKING_FIELD_KEYS),
        "concrete_kernel_x_orbit_rows": len(CONCRETE_KERNEL_X_ORBIT_KEYS),
        "ambient_upper_bound_working_field_rows": (
            len(gaps) - len(EXACT_WORKING_FIELD_KEYS)
        ),
        "p224_potential_direction_rows": 1,
        "exact_zero_vertical_gap_controls": sum(
            row["control_type"] == "exact_zero_vertical_gap" for row in controls
        ),
        "unresolved_controls": sum(row["control_type"] == "unresolved" for row in controls),
        "fully_charged_transfer_rows": 0,
        "weakness_eligible_rows": 0,
        "admitted_ecdlp_comparison_rows": 9,
        "withheld_ecdlp_comparison_rows": 4,
    }
    for key, expected in expected_summary.items():
        require_equal(summary[key], expected, f"summary {key}")
    xs = [float(row["gap_log2"]) for row in gaps]
    ys = [math.log2(int(row["ambient_absolute_x_degree_upper_bound"])) for row in gaps]
    rho = pearson(rankdata(xs), rankdata(ys))
    require(math.isclose(summary["descriptive_association"]["rho"], rho,
                         rel_tol=0.0, abs_tol=1e-15),
            "descriptive Spearman association")
    require_equal(summary["descriptive_association"]["n_rows"], len(gaps),
                  "descriptive association row count")
    require_equal(
        summary["descriptive_association"]["metric"],
        "Spearman(log2 ell, log2 derived m*k ambient degree)",
        "descriptive association metric label",
    )
    require("41 of 43 m*k values are ambient upper bounds" in
            summary["descriptive_association"]["inference"],
            "descriptive association working-field limitation")

    require(all(row["point_map_status"] == "not_certified" for row in gaps),
            "a gap row unexpectedly claims a certified point map")
    require(all(row["dual_status"] == "not_certified" for row in gaps),
            "a gap row unexpectedly claims a certified dual")
    require(all(row["subgroup_certificate_status"] == "not_certified" for row in gaps),
            "a gap row unexpectedly claims a subgroup certificate")
    require(all(row["full_transfer_cost_status"] == "unmeasured" for row in gaps),
            "a gap row unexpectedly claims a full transfer measurement")
    require(not any(row["weakness_eligible"] for row in gaps),
            "a gap row unexpectedly claims weakness eligibility")

    for prime in list(PRIME_CERTIFICATES):
        verify_prime_certificate(prime)
    certificate_nodes = [PRIME_CERTIFICATES[n] for n in sorted(PRIME_CERTIFICATES)]
    certificate_digest = hashlib.sha256(json.dumps(
        certificate_nodes, sort_keys=True, separators=(",", ":")
    ).encode()).hexdigest()

    return {
        "schema": RECEIPT_SCHEMA,
        "panel_path": str(PANEL_PATH.relative_to(ROOT)),
        "panel_sha256": sha256(PANEL_PATH),
        "verifier_path": str(Path(__file__).resolve().relative_to(ROOT)),
        "verifier_sha256": sha256(Path(__file__).resolve()),
        "factorization_dependency": f"sympy {sympy_version}",
        "status": "pass",
        "checks": [
            {"id": "source_hashes", "status": "pass", "rows": source_count},
            {"id": "rerun_provenance", "status": "pass", **provenance_receipt},
            {"id": "recursive_lucas_primality", "status": "pass",
             "top_level_primes": len(top_level_primes),
             "certificate_nodes": len(certificate_nodes),
             "largest_top_level_prime_bits": max(n.bit_length() for n in top_level_primes),
             "certificate_graph_sha256": certificate_digest},
            {"id": "class_cm_arithmetic", "status": "pass", "rows": len(classes)},
            {"id": "minimal_kernel_field_orders", "status": "pass", "rows": len(gaps)},
            {"id": "working_field_evidence", "status": "pass",
             "exact_abstract_cm_representative_x_orbit_rows": len(EXACT_WORKING_FIELD_KEYS),
             "concrete_kernel_x_orbit_rows": len(CONCRETE_KERNEL_X_ORBIT_KEYS),
             "ambient_upper_bound_rows": len(gaps) - len(EXACT_WORKING_FIELD_KEYS)},
            {"id": "conductor_levels", "status": "pass", "rows": len(levels)},
            {"id": "conditional_adjacencies", "status": "pass",
             "rows": len(adjacencies)},
            {"id": "zero_gap_and_p224_controls", "status": "pass",
             "rows": len(controls) + 1},
            {"id": "measured_effect_sources", "status": "pass", **effects_receipt},
            {"id": "construction_sources", "status": "pass", **construction_receipt},
            {"id": "source_action_audit", "status": "pass",
             "rows": len(source_action_rows)},
            {"id": "csv_projections", "status": "pass", "files": len(csv_sections)},
            {"id": "claim_gates", "status": "pass",
             "fully_charged_transfer_rows": 0, "weakness_eligible_rows": 0},
        ],
        "class_receipts": class_receipts,
        "gap_receipts": gap_receipts,
        "working_field_receipts": working_field_receipts,
        "primality_certificate_nodes": certificate_nodes,
        "limitations": [
            "This receipt verifies exact arithmetic, source transcription, and status gates; it does not construct or evaluate an isogeny.",
            "No row has a certified point map, dual, subgroup-preservation certificate, or fully charged transfer cost.",
            "K-163/45641 has both a derived CM certificate and a retained concrete-kernel x-coordinate orbit certificate; K-283/1697 has the derived abstract CM certificate only; every other m*k value is an ambient upper bound.",
            "The Spearman coefficient is descriptive only because rows are clustered within trace/isogeny classes and twist-paired geometry families.",
        ],
    }


def main() -> int:
    try:
        receipt = verify_panel()
        exit_status = 0
    except (VerificationError, KeyError, StopIteration, ValueError) as error:
        receipt = {
            "schema": RECEIPT_SCHEMA,
            "panel_path": str(PANEL_PATH.relative_to(ROOT)),
            "panel_sha256": sha256(PANEL_PATH) if PANEL_PATH.is_file() else None,
            "verifier_path": str(Path(__file__).resolve().relative_to(ROOT)),
            "verifier_sha256": sha256(Path(__file__).resolve()),
            "factorization_dependency": f"sympy {sympy_version}",
            "status": "fail",
            "error": f"{type(error).__name__}: {error}",
        }
        exit_status = 1
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "status": receipt["status"],
        "receipt": str(RECEIPT_PATH.relative_to(ROOT)),
        "checks": len(receipt.get("checks", [])),
        "error": receipt.get("error"),
    }, indent=2))
    return exit_status


if __name__ == "__main__":
    raise SystemExit(main())
