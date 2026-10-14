#!/usr/bin/env python3
"""Build the 2026-10-14 conductor-gap assessment from frozen repository data.

This is a deterministic evidence-reduction script, not an experiment runner.
It derives exact CM-order geometry and copies already archived measurements.
Missing maps, duals, costs, and certificates remain null/unknown.
"""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCHEMA = "crypto.conductor-gap-panel/v2"


def xy_power(m: int, mu: int) -> tuple[int, int]:
    """Return X,Y with tau^m=X+Y*tau and tau^2=mu*tau-2."""
    x0, y0 = 1, 0
    x1, y1 = 0, 1
    n = m
    while n:
        if n & 1:
            x0, y0 = x0 * x1 - 2 * y0 * y1, x0 * y1 + y0 * x1 + mu * y0 * y1
        x1, y1 = x1 * x1 - 2 * y1 * y1, 2 * x1 * y1 + mu * y1 * y1
        n >>= 1
    return x0, y0


def kronecker_minus_7(p: int) -> int:
    if p == 7:
        return 0
    v = pow((-7) % p, (p - 1) // 2, p)
    if v == 1:
        return 1
    if v == p - 1:
        return -1
    raise ValueError(f"non-prime or invalid conductor factor {p}")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def product(values: list[int] | tuple[int, ...]) -> int:
    answer = 1
    for value in values:
        answer *= value
    return answer


def distinct_prime_factors(value: int) -> list[int]:
    """Return the distinct prime divisors needed for exact-order witnesses."""
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


EXACT_WORKING_FIELD_KEYS = {
    ("nist-k163", 45641),
    ("nist-k283", 1697),
}
CONCRETE_KERNEL_X_ORBIT_KEYS = {
    ("nist-k163", 45641),
}


def build_working_field_certificate(
    class_id: str,
    ell: int,
    m: int,
    mu: int,
    scalar: int,
    relative_x_degree: int,
) -> dict[str, Any] | None:
    """Build the two explicitly admitted absolute-Frobenius orbit proofs.

    Generic ``m*k`` values remain ambient x-coordinate upper bounds.
    These two rows additionally certify the exact order of absolute Frobenius
    on one non-horizontal ell-torsion vector modulo sign.
    """
    if (class_id, ell) not in EXACT_WORKING_FIELD_KEYS:
        return None
    vector = [1, 0]
    matrix = [[0, -2], [1, mu]]
    absolute_degree = m * relative_x_degree
    if math.gcd(m, relative_x_degree) != 1:
        raise ValueError(f"non-coprime certificate degrees for {class_id}/{ell}")
    q_frobenius_matrix = matrix_power_mod(matrix, m, ell)
    if q_frobenius_matrix != [[scalar, 0], [0, scalar]]:
        raise ValueError(f"non-scalar q-Frobenius certificate for {class_id}/{ell}")
    line_return_image = matrix_vector_mod(q_frobenius_matrix, vector, ell)
    if line_return_image != [scalar, 0]:
        raise ValueError(f"bad line-return certificate for {class_id}/{ell}")
    line_exclusions = []
    for prime in distinct_prime_factors(m):
        exponent = m // prime
        image = matrix_vector_mod(matrix_power_mod(matrix, exponent, ell), vector, ell)
        if (image[0] * vector[1] - image[1] * vector[0]) % ell == 0:
            raise ValueError(f"nonminimal line orbit for {class_id}/{ell}")
        line_exclusions.append({
            "prime_divisor": str(prime),
            "exponent": str(exponent),
            "image": [str(value) for value in image],
        })
    full_matrix = matrix_power_mod(matrix, absolute_degree, ell)
    if full_matrix == [[1, 0], [0, 1]]:
        closure_sign = 1
    elif full_matrix == [[ell - 1, 0], [0, ell - 1]]:
        closure_sign = -1
    else:
        raise ValueError(f"bad absolute x-orbit closure for {class_id}/{ell}")
    full_image = matrix_vector_mod(full_matrix, vector, ell)
    exclusions = []
    for prime in distinct_prime_factors(absolute_degree):
        exponent = absolute_degree // prime
        image = matrix_vector_mod(matrix_power_mod(matrix, exponent, ell), vector, ell)
        if image in ([1, 0], [ell - 1, 0]):
            raise ValueError(f"nonminimal absolute x orbit for {class_id}/{ell}")
        exclusions.append({
            "prime_divisor": str(prime),
            "exponent": str(exponent),
            "image": [str(value) for value in image],
        })
    concrete_point_binding: dict[str, Any]
    if (class_id, ell) in CONCRETE_KERNEL_X_ORBIT_KEYS:
        concrete_point_binding = {
            "status": "certified_concrete_kernel_x_witness",
            "evidence_kind": "observed_fail_closed_probe",
            "evidence_path": (
                "research/ecc2k130_conductor_isogenies_20261007/analogues/"
                "probe163_45641_relative_tower.out"
            ),
            "retained_input_replay_path": (
                "research/ecc2k130_conductor_isogenies_20261007/analogues/"
                "verify163_45641_relative_witness.out"
            ),
            "arithmetic_independence": "not_independent_same_x_only_ladder_family",
            "probe_schema": "k163-degree45641-relative-tower-probe-v2",
            "absolute_x_orbit_degree": str(absolute_degree),
            "closure_status": "pass",
            "proper_divisor_exclusion_degrees": ["1630", "652", "20"],
            "all_nonzero_kernel_multiples_status": "derived",
            "descending_classification_basis": "derived_tau_eigenline_exclusion",
            "prime_line_scope_status": "derived",
            "scope": (
                "concrete x-coordinate witness in the retained relative tower; "
                "not a full point coordinate pair, kernel polynomial, or point map"
            ),
        }
    else:
        concrete_point_binding = {"status": "not_certified"}
    return {
        "certificate_kind": "derived_cm_line_orbit",
        "basis": ["1", "tau"],
        "vector_convention": "column [a,b] represents a+b*tau",
        "tau_relation": "tau^2-mu*tau+2=0",
        "mu": str(mu),
        "absolute_frobenius_matrix_mod_ell": [
            [str(entry % ell) for entry in row] for row in matrix
        ],
        "representative_vector": ["1", "0"],
        "representative_line_status": "non_horizontal",
        "line_orbit_degree": str(m),
        "line_factor_exclusion_images": line_exclusions,
        "q_frobenius_matrix_mod_ell": [
            [str(value) for value in row] for row in q_frobenius_matrix
        ],
        "line_return_image": [str(value) for value in line_return_image],
        "q_relative_x_orbit_degree": str(relative_x_degree),
        "line_and_relative_degrees_coprime": True,
        "absolute_x_orbit_degree": str(absolute_degree),
        "absolute_x_orbit_closure_sign": closure_sign,
        "absolute_x_orbit_matrix_mod_ell": [
            [str(value) for value in row] for row in full_matrix
        ],
        "exact_full_point_orbit_degree": (
            str(absolute_degree) if closure_sign == 1 else str(2 * absolute_degree)
        ),
        "full_orbit_image": [str(value) for value in full_image],
        "factor_exclusion_images": exclusions,
        "concrete_point_binding": concrete_point_binding,
        "scope": (
            "exact minimal absolute-Frobenius x-orbit degree for the stated "
            "abstract non-horizontal torsion vector; not explicit point coordinates, "
            "a concrete field representation, a map, or a construction-cost measurement"
        ),
    }


def rankdata(values: list[float]) -> list[float]:
    ordered = sorted(enumerate(values), key=lambda pair: pair[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(ordered):
        j = i + 1
        while j < len(ordered) and ordered[j][1] == ordered[i][1]:
            j += 1
        rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[ordered[k][0]] = rank
        i = j
    return ranks


def pearson(xs: list[float], ys: list[float]) -> float:
    xm = sum(xs) / len(xs)
    ym = sum(ys) / len(ys)
    numerator = sum((x - xm) * (y - ym) for x, y in zip(xs, ys))
    denominator = math.sqrt(
        sum((x - xm) ** 2 for x in xs) * sum((y - ym) ** 2 for y in ys)
    )
    return numerator / denominator


# Every class below is the maximal-order Koblitz crater
# y^2+xy=x^3+a*x^2+1 over F_(2^m), with D_K=-7 and squarefree f_pi.
CLASS_DEFS: list[dict[str, Any]] = [
    dict(id="koblitz-m37-a0", label="m=37 a=0", family="proxy", m=37, a=0,
         factors=[73, 2663], evidence="research/isogeny_volcano_rho_20261005/README.md"),
    dict(id="koblitz-m41-a0", label="m=41 a=0", family="proxy", m=41, a=0,
         factors=[409, 1721], evidence="research/isogeny_volcano_rho_m41_20261006/README.md"),
    dict(id="koblitz-m51-a0", label="m=51 a=0", family="survey", m=51, a=0,
         factors=[271, 120871], evidence="research/ecc2k130_conductor_isogenies_20261007/m51_m53/m5153.out"),
    dict(id="koblitz-m51-a1", label="m=51 a=1", family="survey", m=51, a=1,
         factors=[271, 120871], evidence="research/ecc2k130_conductor_isogenies_20261007/m51_m53/m5153.out"),
    dict(id="koblitz-m53-a0", label="m=53 a=0", family="survey", m=53, a=0,
         factors=[68476319], evidence="research/ecc2k130_conductor_isogenies_20261007/m51_m53/m5153.out"),
    dict(id="koblitz-m53-a1", label="m=53 a=1", family="survey", m=53, a=1,
         factors=[68476319], evidence="research/ecc2k130_conductor_isogenies_20261007/m51_m53/m5153.out"),
    dict(id="koblitz-m83-a0", label="m=83 a=0", family="survey", m=83, a=0,
         factors=[6473, 53676929], evidence="research/ecc2k130_conductor_isogenies_20261007/analogues/survey.out"),
    dict(id="koblitz-m97-a0", label="m=97 a=0", family="survey", m=97, a=0,
         factors=[751943, 352124743], evidence="research/ecc2k130_conductor_isogenies_20261007/analogues/survey.out"),
    dict(id="koblitz-m101-a1", label="m=101 a=1", family="survey", m=101, a=1,
         factors=[5857, 18583, 3996569], evidence="research/ecc2k130_conductor_isogenies_20261007/analogues/survey.out"),
    dict(id="koblitz-m103-a0", label="m=103 a=0", family="survey", m=103, a=0,
         factors=[11329, 188642399417], evidence="research/ecc2k130_conductor_isogenies_20261007/analogues/survey.out"),
    dict(id="koblitz-m107-a0", label="m=107 a=0", family="survey", m=107, a=0,
         factors=[3209, 1703265694433], evidence="research/ecc2k130_conductor_isogenies_20261007/analogues/survey.out"),
    dict(id="koblitz-m107-a1", label="m=107 a=1", family="survey", m=107, a=1,
         factors=[3209, 1703265694433], evidence="research/ecc2k130_conductor_isogenies_20261007/analogues/survey.out"),
    dict(id="koblitz-m109-a1", label="m=109 a=1", family="survey", m=109, a=1,
         factors=[3271, 699600307831], evidence="research/ecc2k130_conductor_isogenies_20261007/analogues/survey.out"),
    dict(id="koblitz-m113-a1", label="m=113 a=1", family="survey", m=113, a=1,
         factors=[77031318395801969], evidence="research/ecc2k130_conductor_isogenies_20261007/analogues/survey.out"),
    dict(id="ecc2k-130", label="ECC2K-130", family="challenge", m=131, a=0,
         factors=[263, 146505763881528721], evidence="research/ecc2k130_conductor_isogenies_20261007/README.md"),
    dict(id="nist-k163", label="NIST K-163", family="nist-k", m=163, a=1,
         factors=[45641, 82153, 8610311, 56498081], evidence="research/endosweep_nist_20261006/nist.json"),
    dict(id="nist-k233", label="NIST K-233", family="nist-k", m=233, a=0,
         factors=[5610641, 85310626991, 150532234816721999], evidence="research/endosweep_nist_20261006/nist.json"),
    dict(id="nist-k283", label="NIST K-283", family="nist-k", m=283, a=0,
         factors=[1697, 162254089, 1779143207551652584836995286271], evidence="research/endosweep_nist_20261006/nist.json"),
    dict(id="nist-k409", label="NIST K-409", family="nist-k", m=409, a=0,
         factors=[21262439877311, 22431439539154506863, 57030553306655053533734286593], evidence="research/endosweep_nist_20261006/nist.json"),
    dict(id="nist-k571", label="NIST K-571", family="nist-k", m=571, a=0,
         factors=[3952463, 9021184135396238924389891945192676814518993645089807769277009849103733654828039], evidence="research/endosweep_nist_20261006/nist.json"),
]


# k is the least positive exponent with c^k=+/-1 for q-Frobenius scalar c mod ell.
KERNEL_X_DEGREE: dict[tuple[str, int], int] = {
    ("koblitz-m37-a0", 73): 9, ("koblitz-m37-a0", 2663): 1331,
    ("koblitz-m41-a0", 409): 204, ("koblitz-m41-a0", 1721): 215,
    ("koblitz-m51-a0", 271): 45, ("koblitz-m51-a0", 120871): 1185,
    ("koblitz-m51-a1", 271): 45, ("koblitz-m51-a1", 120871): 1185,
    ("koblitz-m53-a0", 68476319): 646003, ("koblitz-m53-a1", 68476319): 646003,
    ("koblitz-m83-a0", 6473): 3236, ("koblitz-m83-a0", 53676929): 6709616,
    ("koblitz-m97-a0", 751943): 375971, ("koblitz-m97-a0", 352124743): 58687457,
    ("koblitz-m101-a1", 5857): 2928, ("koblitz-m101-a1", 18583): 3097,
    ("koblitz-m101-a1", 3996569): 1998284,
    ("koblitz-m103-a0", 11329): 472, ("koblitz-m103-a0", 188642399417): 94321199708,
    ("koblitz-m107-a0", 3209): 1604, ("koblitz-m107-a0", 1703265694433): 7959185488,
    ("koblitz-m107-a1", 3209): 1604, ("koblitz-m107-a1", 1703265694433): 7959185488,
    ("koblitz-m109-a1", 3271): 5, ("koblitz-m109-a1", 699600307831): 116600051305,
    ("koblitz-m113-a1", 77031318395801969): 38515659197900984,
    ("ecc2k-130", 263): 1, ("ecc2k-130", 146505763881528721): 6104406828397030,
    ("nist-k163", 45641): 20, ("nist-k163", 82153): 63,
    ("nist-k163", 8610311): 4305155, ("nist-k163", 56498081): 1765565,
    ("nist-k233", 5610641): 12040, ("nist-k233", 85310626991): 183070015,
    ("nist-k233", 150532234816721999): 75266117408360999,
    ("nist-k283", 1697): 848, ("nist-k283", 162254089): 143334,
    ("nist-k283", 1779143207551652584836995286271): 3143362557511753683457588845,
    ("nist-k409", 21262439877311): 2126243987731,
    ("nist-k409", 22431439539154506863): 27422297725127759,
    ("nist-k409", 57030553306655053533734286593): 3564409581665940845858392912,
    ("nist-k571", 3952463): 3461,
    ("nist-k571", 9021184135396238924389891945192676814518993645089807769277009849103733654828039): 4510592067698119462194945972596338407259496822544903884638504924551866827414019,
}


ENDPOINT_STATUS: dict[tuple[str, int], str] = {
    ("koblitz-m37-a0", 73): "complete_floor_census_explicit_kernel_endpoints",
    ("koblitz-m37-a0", 2663): "sampled_floor_random_scan",
    ("koblitz-m41-a0", 409): "complete_floor_census_from_one_kernel_endpoint",
    ("koblitz-m41-a0", 1721): "complete_floor_census_from_one_kernel_endpoint",
    ("koblitz-m51-a0", 271): "complete_floor_census_cm_and_kernel_routes",
    ("koblitz-m51-a0", 120871): "sampled_parent_and_bottom_levels_no_local_edge_map",
    ("koblitz-m83-a0", 6473): "complete_floor_census_cm_route",
    ("koblitz-m101-a1", 5857): "complete_floor_census_cm_route",
    ("koblitz-m101-a1", 18583): "complete_floor_census_cm_route",
    ("koblitz-m103-a0", 11329): "complete_floor_census_cm_route",
    ("koblitz-m107-a0", 3209): "complete_floor_census_cm_route",
    ("koblitz-m107-a1", 3209): "complete_floor_census_cm_route",
    ("koblitz-m109-a1", 3271): "six_kernel_endpoint_samples",
    ("ecc2k-130", 263): "complete_floor_census_explicit_kernel_endpoints",
    ("nist-k163", 45641): (
        "six_historical_plus_two_fresh_preflight_endpoint_samples_"
        "map_not_retained"
    ),
    ("nist-k163", 82153): "six_kernel_endpoint_samples_map_not_retained",
    ("nist-k283", 1697): "census_implementation_only_not_executed",
}


LEVEL_STATUS: dict[tuple[str, int], str] = {
    ("koblitz-m37-a0", 73): "complete_census",
    ("koblitz-m37-a0", 2663): "sampled_random_scan",
    ("koblitz-m37-a0", 73 * 2663): "sampled_random_scan",
    ("koblitz-m41-a0", 409): "complete_census",
    ("koblitz-m41-a0", 1721): "complete_census",
    ("koblitz-m41-a0", 409 * 1721): "sampled_random_scan",
    ("koblitz-m51-a0", 271): "complete_census",
    ("koblitz-m51-a0", 120871): "42_certified_parent_samples_32_selected_orbits",
    ("koblitz-m51-a0", 271 * 120871): "42_certified_bottom_samples_32_selected_orbits",
    ("koblitz-m83-a0", 6473): "complete_census_cm_route",
    ("koblitz-m101-a1", 5857): "complete_census_cm_route",
    ("koblitz-m101-a1", 18583): "complete_census_cm_route",
    ("koblitz-m103-a0", 11329): "complete_census_cm_route",
    ("koblitz-m107-a0", 3209): "complete_census_cm_route",
    ("koblitz-m107-a1", 3209): "complete_census_cm_route",
    ("koblitz-m109-a1", 3271): "six_endpoint_orbit_samples",
    ("ecc2k-130", 263): "complete_census",
    ("nist-k163", 45641): (
        "six_historical_plus_two_fresh_preflight_endpoint_orbit_samples"
    ),
    ("nist-k163", 82153): "six_endpoint_orbit_samples",
    ("nist-k163", 45641 * 82153): "six_endpoint_orbit_samples",
}


MATCHED_ADJACENCIES: dict[tuple[str, int, int], str] = {
    ("koblitz-m37-a0", 1, 73): "all_74_kernel_endpoints",
    ("koblitz-m41-a0", 1, 409): "one_kernel_endpoint_then_complete_horizontal_census",
    ("koblitz-m41-a0", 1, 1721): "one_kernel_endpoint_then_complete_horizontal_census",
    ("koblitz-m41-a0", 409, 1721): "two_kernel_endpoint_samples",
    ("koblitz-m51-a0", 1, 271): "40_kernel_endpoints_cross_checked_against_cm_census",
    ("koblitz-m51-a0", 120871, 271): (
        "42_certified_undirected_endpoint_pairs_observed_only_in_the_"
        "ascending_bottom_to_parent_direction"
    ),
    ("koblitz-m109-a1", 1, 3271): "six_kernel_endpoint_samples",
    ("ecc2k-130", 1, 263): "all_262_descending_kernel_endpoints",
    ("nist-k163", 1, 45641): (
        "six_historical_plus_two_fresh_preflight_kernel_endpoint_samples"
    ),
    ("nist-k163", 1, 82153): "six_kernel_endpoint_samples",
    ("nist-k163", 45641, 82153): "six_kernel_endpoint_samples",
}


NIST_ACTION_GAINS = {
    "nist-k163": 3.6743640771155386,
    "nist-k233": 3.9320930723271403,
    "nist-k283": 4.072329121415941,
    "nist-k409": 4.337978516470875,
    "nist-k571": 4.578673467681422,
}


def source_refs(*record_groups: Any) -> list[dict[str, str]]:
    paths = {item["evidence"] for item in CLASS_DEFS} | {
        "research/conductor_gap_panel_20261014/build_panel.py",
        "research/ecc2k130_conductor_isogenies_20261007/EXTENSIONS.md",
        "research/ecc2k130_conductor_isogenies_20261007/analogues/MAP163_45641_PROTOCOL.md",
        "research/ecc2k130_conductor_isogenies_20261007/analogues/check_char2_velu_function_identity_small.gp",
        "research/ecc2k130_conductor_isogenies_20261007/analogues/check_char2_velu_function_identity_small.out",
        "research/ecc2k130_conductor_isogenies_20261007/analogues/control163_45641_horizontal_endomorphism.gp",
        "research/ecc2k130_conductor_isogenies_20261007/analogues/kernel163_45641_map.gp",
        "research/ecc2k130_conductor_isogenies_20261007/analogues/kernel163_45641_map_relative.gp",
        "research/ecc2k130_conductor_isogenies_20261007/analogues/probe163_45641_seed.gp",
        "research/ecc2k130_conductor_isogenies_20261007/analogues/probe163_45641_seed_bounded.inc.gp",
        "research/ecc2k130_conductor_isogenies_20261007/analogues/probe163_45641_seed.out",
        "research/ecc2k130_conductor_isogenies_20261007/analogues/probe163_45641_relative_tower.gp",
        "research/ecc2k130_conductor_isogenies_20261007/analogues/rerun_provenance.json",
        "research/ecc2k130_conductor_isogenies_20261007/analogues/run163_45641_map.gp",
        "research/ecc2k130_conductor_isogenies_20261007/analogues/run163_45641_map_relative.gp",
        "research/ecc2k130_conductor_isogenies_20261007/analogues/run_check_char2_velu_function_identity_small.gp",
        "research/ecc2k130_conductor_isogenies_20261007/analogues/run_control163_45641_horizontal_endomorphism.gp",
        "research/ecc2k130_conductor_isogenies_20261007/analogues/run_probe163_45641_relative_tower.gp",
        "research/ecc2k130_conductor_isogenies_20261007/analogues/run_probe163_45641_seed.gp",
        "research/ecc2k130_conductor_isogenies_20261007/analogues/run_verify163_45641_seed_endpoint.gp",
        "research/ecc2k130_conductor_isogenies_20261007/analogues/verify163_45641_seed_endpoint.gp",
        "research/ecc2k130_conductor_isogenies_20261007/analogues/verify163_45641_seed_endpoint.out",
        "research/ecc2k130_conductor_isogenies_20261007/analogues/verify163_45641_relative_witness.gp",
        "research/ecc2k130_conductor_isogenies_20261007/analogues/verify163_45641_relative_witness.out",
        "research/ecc2k130_conductor_isogenies_20261007/k283/README.md",
        "research/ecc2k130_conductor_isogenies_20261007/second_level/down163b.out",
        "research/ecc2k130_conductor_isogenies_20261007/second_level/down163c.out",
        "research/ecc2k130_conductor_isogenies_20261007/second_level/down163_s1.out",
        "research/ecc2k130_conductor_isogenies_20261007/second_level/down163_s2.out",
        "research/ecc2k130_conductor_isogenies_20261007/second_level/down163_s3.out",
        "research/ecc2k130_conductor_isogenies_20261007/second_level/down163_s4.out",
        "research/isogeny_volcano_level_replication_20261013/results.json",
        "research/isogeny_volcano_m51_rho_20261013/analysis.json",
        "research/isogeny_volcano_m51_deep_scan_20261013/results/classification-receipt.json",
        "research/isogeny_volcano_m51_deep_scan_20261013/results/selection.json",
        "research/isogeny_volcano_m51_deep_scan_20261013/results/session.json",
        "research/isogeny_volcano_m51_deep_rho_20261013/analysis.json",
        "research/isogeny_volcano_rho_20261005/map73_dual_control.gp",
        "research/isogeny_volcano_rho_20261005/map73_dual_control.out",
        "docs/reports/koblitz-rho-transfer-20261013/audit.json",
        "problems/koblitz-vertical-isogeny-maps-not-persisted.md",
        "problems/p224-degree3-point-maps-not-certified.md",
    }

    def collect(value: Any) -> None:
        if isinstance(value, dict):
            evidence_path = value.get("evidence_path")
            if isinstance(evidence_path, str):
                paths.add(evidence_path)
            for nested in value.values():
                if isinstance(nested, (dict, list, tuple)):
                    collect(nested)
        elif isinstance(value, (list, tuple)):
            for nested in value:
                collect(nested)

    collect(record_groups)
    paths = sorted(paths)
    return [
        {"path": path, "sha256": sha256(ROOT / path)}
        for path in paths
    ]


def build_classes_and_gaps() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    nist = json.loads((ROOT / "research/endosweep_nist_20261006/nist.json").read_text())
    classes: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    nist_names = {
        "nist-k163": "nist/K-163", "nist-k233": "nist/K-233",
        "nist-k283": "nist/K-283", "nist-k409": "nist/K-409",
        "nist-k571": "nist/K-571",
    }
    for spec in CLASS_DEFS:
        m = spec["m"]
        mu = 1 if spec["a"] else -1
        x, y = xy_power(m, mu)
        f_pi = abs(y)
        assert product(spec["factors"]) == f_pi, (spec["id"], f_pi)
        trace = 2 * x + mu * y
        q = 1 << m
        order = q + 1 - trace
        if spec["id"] in nist_names:
            archived = nist["curves"][nist_names[spec["id"]]]
            assert int(archived["exact"]["f"]) == f_pi
            assert int(archived["t"]) == trace
            factorization_provenance = (
                "archived" if spec["id"] in {"nist-k163", "nist-k283"}
                else "derived_from_archived_f_pi_prime_checked_2026-10-14"
            )
        else:
            factorization_provenance = "archived"
        local_h = [p - kronecker_minus_7(p) for p in spec["factors"]]
        classes.append({
            "schema": SCHEMA,
            "class_id": spec["id"],
            "label": spec["label"],
            "family": spec["family"],
            "characteristic": 2,
            "extension_degree": m,
            "curve_model": f"y^2+xy=x^3+{spec['a']}*x^2+1",
            "q": str(q),
            "trace": str(trace),
            "ambient_order": str(order),
            "D_K": "-7",
            "source_f_E": "1",
            "f_pi": str(f_pi),
            "f_pi_factorization": [str(p) for p in spec["factors"]],
            "factorization_provenance": factorization_provenance,
            "prime_factor_count": len(spec["factors"]),
            "conductor_level_count": 1 << len(spec["factors"]),
            "conditional_adjacency_count": len(spec["factors"]) * (1 << (len(spec["factors"]) - 1)),
            "global_bottom_class_number": str(product(local_h)),
            "source_signed_tau_gain_vs_negation_bits": NIST_ACTION_GAINS.get(spec["id"]),
            "evidence_path": spec["evidence"],
        })
        for ell in spec["factors"]:
            chi = kronecker_minus_7(ell)
            split = {1: "split", -1: "inert", 0: "ramified"}[chi]
            k = KERNEL_X_DEGREE[(spec["id"], ell)]
            c = x % ell
            ck = pow(c, k, ell)
            assert ck in {1, ell - 1}, (spec["id"], ell, k, ck)
            scalar_order = k if ck == 1 else 2 * k
            kernel_degree = (ell - 1) // 2
            packed_bytes = (m * (kernel_degree + 1) + 7) // 8
            ambient_degree = m * k
            frobenius_matrix = [[0, -2], [1, mu]]
            q_frobenius_matrix = matrix_power_mod(frobenius_matrix, m, ell)
            if q_frobenius_matrix != [[c, 0], [0, c]]:
                raise ValueError(f"q-Frobenius is not scalar for {spec['id']}/{ell}")
            ambient_closure_matrix = matrix_power_mod(
                frobenius_matrix, ambient_degree, ell
            )
            if ambient_closure_matrix not in (
                [[1, 0], [0, 1]], [[ell - 1, 0], [0, ell - 1]]
            ):
                raise ValueError(
                    f"ambient absolute x-degree does not close for {spec['id']}/{ell}"
                )
            working_field_certificate = build_working_field_certificate(
                spec["id"], ell, m, mu, c, k
            )
            gaps.append({
                "schema": SCHEMA,
                "gap_id": f"{spec['id']}-ell-{ell}",
                "class_id": spec["id"],
                "class_label": spec["label"],
                "family": spec["family"],
                "m": m,
                "source_f_E": "1",
                "target_f_E": str(ell),
                "edge_degree": str(ell),
                "gap_log2": math.log2(ell),
                "valuation_in_f_pi": 1,
                "split_type": split,
                "kronecker_minus_7": chi,
                "q_frobenius_scalar_mod_ell": str(c),
                "scalar_order_mod_ell": str(scalar_order),
                "relative_kernel_x_field_degree": str(k),
                "ambient_absolute_x_degree_upper_bound": str(ambient_degree),
                "exact_abstract_cm_representative_x_orbit_degree": (
                    str(ambient_degree)
                    if working_field_certificate is not None else None
                ),
                "concrete_kernel_x_orbit_degree": (
                    str(ambient_degree)
                    if (spec["id"], ell) in CONCRETE_KERNEL_X_ORBIT_KEYS else None
                ),
                "concrete_kernel_x_orbit_status": (
                    "certified_retained_relative_tower_witness"
                    if (spec["id"], ell) in CONCRETE_KERNEL_X_ORBIT_KEYS
                    else "not_certified"
                ),
                "working_field_status": (
                    "exact_abstract_cm_representative_x_orbit"
                    if working_field_certificate is not None
                    else "certified_ambient_upper_bound_only"
                ),
                "working_field_certificate": working_field_certificate,
                "kernel_support": "source_curve" if ck == 1 else "quadratic_twist",
                "kernel_polynomial_degree": str(kernel_degree),
                "dense_packed_kernel_bytes": str(packed_bytes),
                "local_ring_class_number": str(ell - chi),
                "geometry_evidence_kind": "exact",
                "endpoint_status": ENDPOINT_STATUS.get((spec["id"], ell), "structural_only"),
                "point_map_status": "not_certified",
                "dual_status": "not_certified",
                "subgroup_certificate_status": "not_certified",
                "full_transfer_cost_status": "unmeasured",
                "weakness_eligible": False,
                "independence_cluster": spec["id"],
                "evidence_path": spec["evidence"],
            })
    return classes, gaps


def build_levels(classes: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    levels: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    for curve_class in classes:
        factors = [int(value) for value in curve_class["f_pi_factorization"]]
        chis = {p: kronecker_minus_7(p) for p in factors}
        for mask in range(1 << len(factors)):
            selected = [p for i, p in enumerate(factors) if mask & (1 << i)]
            f_e = product(selected)
            level_id = f"{curve_class['class_id']}-f-{f_e}"
            levels.append({
                "schema": SCHEMA,
                "level_id": level_id,
                "class_id": curve_class["class_id"],
                "f_E": str(f_e),
                "f_E_factorization": [str(p) for p in selected],
                "remaining_index": str(int(curve_class["f_pi"]) // f_e),
                "ring_discriminant": str(-7 * f_e * f_e),
                "distance_from_crater": len(selected),
                "ring_class_number": str(product([p - chis[p] for p in selected])),
                "identity_evidence_kind": "exact_lattice_derivation",
                "endpoint_census_status": (
                    "crater_source" if f_e == 1
                    else LEVEL_STATUS.get((curve_class["class_id"], f_e), "not_constructed_or_not_recorded")
                ),
            })
            for i, ell in enumerate(factors):
                if mask & (1 << i):
                    continue
                target = f_e * ell
                matched = MATCHED_ADJACENCIES.get((curve_class["class_id"], f_e, ell))
                edges.append({
                    "schema": SCHEMA,
                    "adjacency_id": f"{curve_class['class_id']}-f-{f_e}-to-{target}",
                    "class_id": curve_class["class_id"],
                    "source_level_id": level_id,
                    "target_level_id": f"{curve_class['class_id']}-f-{target}",
                    "source_f_E": str(f_e),
                    "target_f_E": str(target),
                    "edge_degree": str(ell),
                    "direction": "descending",
                    "relation_type": "conductor_lattice_adjacency",
                    "explicit_matched_edge": matched is not None,
                    "matched_endpoint_status": matched,
                    "point_map_status": "not_certified",
                    "dual_status": "not_certified",
                    "independence_cluster": curve_class["class_id"],
                    "note": "Exact order adjacency; not an executable point map unless separately certified.",
                })
    return levels, edges


def build_controls() -> list[dict[str, Any]]:
    nist = json.loads((ROOT / "research/endosweep_nist_20261006/nist.json").read_text())
    controls: list[dict[str, Any]] = []
    for name in ["P-192", "P-256", "P-384", "P-521", "B-163", "B-233", "B-283", "B-409"]:
        row = nist["curves"][f"nist/{name}"]
        assert row["exact"]["f"] == 1
        controls.append({
            "schema": SCHEMA,
            "curve": name,
            "control_type": "exact_zero_vertical_gap",
            "D_K": str(row["exact"]["D_K"]),
            "f_pi": "1",
            "vertical_conductor_prime_count": 0,
            "status": "exact",
            "evidence_path": "research/endosweep_nist_20261006/nist.json",
        })
    # sect113r1: #E=2n with the SEC2 subgroup order.  Its Frobenius
    # discriminant is fundamental, so f_pi=1.  The historical solve is a
    # subgroup-size/baseline fact, not an isogeny-conductor effect.
    m = 113
    q = 1 << m
    n = int("0100000000000000D9CCEC8A39E56F", 16)
    trace = q + 1 - 2 * n
    d_k = trace * trace - 4 * q
    controls.append({
        "schema": SCHEMA,
        "curve": "sect113r1",
        "control_type": "exact_zero_vertical_gap",
        "D_K": str(d_k),
        "f_pi": "1",
        "vertical_conductor_prime_count": 0,
        "status": "exact_from_standard_order_and_fundamental_discriminant",
        "evidence_path": (
            "research/conductor_gap_panel_20261014/"
            "sect113r1-openssl-parameters.txt"
        ),
    })
    b571 = nist["curves"]["nist/B-571"]
    controls.append({
        "schema": SCHEMA,
        "curve": "B-571",
        "control_type": "unresolved",
        "D_K": None,
        "f_pi": None,
        "vertical_conductor_prime_count": None,
        "status": "exact_conductor_unresolved",
        "abs_D_K_at_least": str(b571["bound"]["abs_D_K_at_least"]),
        "log2_abs_D_K_at_least": b571["bound"]["log2"],
        "min_nonscalar_degree_at_least": str(
            b571["bound"]["min_nonscalar_degree_at_least"]
        ),
        "evidence_path": "research/endosweep_nist_20261006/nist.json",
    })
    return controls


def build_p224_candidate() -> dict[str, Any]:
    nist = json.loads((ROOT / "research/endosweep_nist_20261006/nist.json").read_text())
    row = nist["curves"]["nist/P-224"]
    assert row["exact"]["f"] == 3
    return {
        "schema": SCHEMA,
        "gap_id": "nist-p224-ell-3-candidate",
        "class_id": "nist-p224",
        "class_label": "NIST P-224",
        "family": "nist-p",
        "edge_degree": "3",
        "gap_log2": math.log2(3),
        "split_type": "ramified",
        "f_pi": "3",
        "source_f_E": None,
        "target_f_E": None,
        "certified_vertical_gap": False,
        "endpoint_status": "four_rational_linear_kernels_and_codomains_enumerated",
        "point_map_status": "not_certified",
        "dual_status": "not_certified",
        "subgroup_certificate_status": "not_certified",
        "full_transfer_cost_status": "unmeasured",
        "weakness_eligible": False,
        "open_obligation": "certify named-curve f_E, directions, closure, map, and dual",
        "evidence_path": "problems/p224-degree3-point-maps-not-certified.md",
    }


def build_measured_effects() -> list[dict[str, Any]]:
    # Sign convention for every row: log2(child mean / parent mean).
    rows = [
        ("m37-73-other-absent", "koblitz-m37-a0", 73, "1", "73", 0.002917207431943878, -0.020484542223939986, 0.02658547098586555),
        ("m37-73-other-present", "koblitz-m37-a0", 73, "2663", str(73 * 2663), -0.017604865781105226, -0.038453274033975984, 0.003021671511841751),
        ("m37-2663-other-absent", "koblitz-m37-a0", 2663, "1", "2663", 0.008627215731904971, -0.018442988172839393, 0.03580119257446569),
        ("m37-2663-other-present", "koblitz-m37-a0", 2663, "73", str(73 * 2663), -0.011894857481144189, -0.027376875134620202, 0.003650041641619883),
        ("m41-409-other-absent", "koblitz-m41-a0", 409, "1", "409", -0.0014299949941272367, -0.04946159016758579, 0.04495625464468643),
        ("m41-409-other-present", "koblitz-m41-a0", 409, "1721", str(409 * 1721), -0.0022971307561496777, -0.040039248140534243, 0.036422685809812824),
        ("m41-1721-other-absent", "koblitz-m41-a0", 1721, "1", "1721", 0.016987683949480758, -0.03010023909076086, 0.06254745248130546),
        ("m41-1721-other-present", "koblitz-m41-a0", 1721, "409", str(409 * 1721), 0.016120548187458457, -0.022858497427897265, 0.05566328823004871),
    ]
    effects = [{
        "schema": SCHEMA,
        "comparison_id": row[0], "class_id": row[1], "edge_degree": str(row[2]),
        "source_f_E": row[3], "target_f_E": row[4],
        "metric": "log2_child_over_parent_mean_counted_ops",
        "estimate_bits": row[5], "ci_level": 0.95,
        "ci_lower_bits": row[6], "ci_upper_bits": row[7],
        "action": "native_negation", "evidence_kind": "observed",
        "inference_status": "admitted", "scope": "native_walk_not_transfer",
        "evidence_path": "research/isogeny_volcano_level_replication_20261013/results.json",
    } for row in rows]
    effects.append({
        "schema": SCHEMA,
        "comparison_id": "m51-271-same-tau17-accepted", "class_id": "koblitz-m51-a0",
        "edge_degree": "271", "source_f_E": "1", "target_f_E": "271",
        "metric": "log2_child_over_parent_mean_counted_ops",
        "estimate_bits": 0.005762506207455747, "ci_level": 0.95,
        "ci_lower_bits": -0.03217048281292999,
        "ci_upper_bits": 0.04337439078762456,
        "action": "signed_tau17_both_levels", "evidence_kind": "observed",
        "inference_status": "admitted_fixed_orbit", "scope": "native_walk_not_transfer",
        "evidence_path": "research/isogeny_volcano_m51_rho_20261013/analysis.json",
    })
    deep = [
        ("m51-deep-271-other-absent", 271, "1", "271",
         -0.013566257446779417, -0.07424275651083867, 0.047110241617279836),
        ("m51-deep-120871-other-absent", 120871, "1", "120871",
         -0.026350098089814367, -0.08155305661184845, 0.028852860432219712),
        ("m51-deep-120871-other-present", 120871, "271", str(271 * 120871),
         0.013542224192271135, -0.04532613436021843, 0.0724105827447607),
        ("m51-deep-271-other-present", 271, "120871", str(271 * 120871),
         0.026326064835306084, -0.03392253031491135, 0.08657465998552352),
    ]
    for comparison_id, ell, source, target, estimate, lo, hi in deep:
        effects.append({
            "schema": SCHEMA,
            "comparison_id": comparison_id, "class_id": "koblitz-m51-a0",
            "edge_degree": str(ell), "source_f_E": source, "target_f_E": target,
            "metric": "log2_child_over_parent_mean_walk_ops",
            "estimate_bits": estimate, "ci_level": 0.95,
            "ci_lower_bits": lo, "ci_upper_bits": hi,
            "action": "native_negation", "evidence_kind": "observed",
            "inference_status": "withheld_aa_gate_failed",
            "scope": "diagnostic_native_walk_not_transfer",
            "evidence_path": "research/isogeny_volcano_m51_deep_rho_20261013/analysis.json",
        })
    return effects


def build_construction_measurements() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    def add_series(
        measurement_id: str,
        class_id: str,
        ell: int,
        source_f: int,
        target_f: int,
        route: str,
        seconds: list[float],
        evidence_path: str,
        note: str = "",
        scope: str = "endpoint_or_census_construction_not_point_map",
        extra: dict[str, Any] | None = None,
    ) -> None:
        for index, value in enumerate(seconds, 1):
            row = {
                "schema": SCHEMA,
                "measurement_id": f"{measurement_id}-{index}",
                "class_id": class_id,
                "edge_degree": str(ell),
                "source_f_E": str(source_f),
                "target_f_E": str(target_f),
                "route": route,
                "elapsed_seconds": value,
                "sample_index": index,
                "sample_count": len(seconds),
                "evidence_kind": "observed",
                "scope": scope,
                "note": note,
                "evidence_path": evidence_path,
            }
            if extra is not None:
                row.update(extra)
            rows.append(row)

    add_series("m41-409", "koblitz-m41-a0", 409, 1, 409, "kernel_endpoint", [223],
               "research/isogeny_volcano_rho_m41_20261006/v409.out")
    add_series("m41-1721", "koblitz-m41-a0", 1721, 1, 1721, "kernel_endpoint", [105],
               "research/isogeny_volcano_rho_m41_20261006/v1721.out")
    add_series("m41-409floor-1721", "koblitz-m41-a0", 1721, 409, 409 * 1721,
               "kernel_endpoint", [149, 220],
               "research/ecc2k130_conductor_isogenies_20261007/second_level/down41.out",
               "inner isogeny timers; exclude the separately logged 5-second embedding")
    add_series("m83-6473-cm", "koblitz-m83-a0", 6473, 1, 6473, "cm_polclass", [20],
               "research/ecc2k130_conductor_isogenies_20261007/cm_route/cm83.out",
               "polclass phase only")
    add_series("m101-5857-cm", "koblitz-m101-a1", 5857, 1, 5857, "cm_polclass", [23],
               "research/ecc2k130_conductor_isogenies_20261007/survey/run_m101_a1_f5857.out",
               "polclass phase only")
    add_series("m101-18583-cm", "koblitz-m101-a1", 18583, 1, 18583, "cm_polclass", [313],
               "research/ecc2k130_conductor_isogenies_20261007/survey/run_m101_a1_f18583.out",
               "polclass phase only")
    add_series("m103-11329-cm", "koblitz-m103-a0", 11329, 1, 11329, "cm_polclass", [75],
               "research/ecc2k130_conductor_isogenies_20261007/survey/run_m103_a0_f11329.out",
               "polclass phase only")
    add_series("m107a0-3209-cm", "koblitz-m107-a0", 3209, 1, 3209, "cm_polclass", [6],
               "research/ecc2k130_conductor_isogenies_20261007/survey/run_m107_a0_f3209.out",
               "polclass phase only")
    add_series("m107a1-3209-cm", "koblitz-m107-a1", 3209, 1, 3209, "cm_polclass", [5],
               "research/ecc2k130_conductor_isogenies_20261007/survey/run_m107_a1_f3209.out",
               "polclass phase only")
    add_series("k163-45641", "nist-k163", 45641, 1, 45641, "kernel_endpoint",
               [62, 67, 68, 63, 87, 61],
               "research/ecc2k130_conductor_isogenies_20261007/analogues/run163_45641.out",
               "per-isogeny timers after field initialization; not cold-start wall time")
    add_series("k163-82153", "nist-k163", 82153, 1, 82153, "kernel_endpoint",
               [985, 877, 842, 939, 965, 989],
               "research/ecc2k130_conductor_isogenies_20261007/analogues/run163_82153.out",
               "per-isogeny timers after field initialization; not cold-start wall time")
    add_series("k163-level2-82153", "nist-k163", 82153, 45641, 45641 * 82153,
               "kernel_endpoint", [930, 835, 828, 829, 1019, 828],
               "research/ecc2k130_conductor_isogenies_20261007/EXTENSIONS.md",
               "six distinct endpoint orbits; one 930-second deterministic rerun plus five "
               "independently seeded starts; inner isogeny timers exclude each separately "
               "logged 29-second embedding")
    add_series(
        "k163-45641-relative-probe", "nist-k163", 45641, 1, 45641,
        "relative_tower_pre_map_probe", [56.65],
        "research/ecc2k130_conductor_isogenies_20261007/analogues/"
        "probe163_45641_relative_tower.out",
        "cold bounded probe; concrete exact absolute x-orbit certificate, "
        "exact-order descending witness, all 22,820 half-kernel x-values, "
        "and endpoint certificate; the 62 ms absolute-orbit timer is nested "
        "inside the 4,628 ms witness timer and must not be added to it; "
        "deliberately stopped before kernel polynomial and point map",
        "bounded_pre_map_probe_not_kernel_polynomial_or_point_map",
        {
            "max_rss_kib": 23724,
            "exit_status": 0,
            "certificate_status": (
                "concrete_exact_x_orbit_descending_witness_and_half_kernel_pass"
            ),
            "work_units": {"half_kernel_x_values": 22820, "inversion_batches": 90},
            "phase_elapsed_ms": {
                "field_setup": 17,
                "witness_including_absolute_orbit_and_classification": 4628,
                "absolute_orbit_nested": 62,
                "endpoint_and_half_kernel": 51995,
            },
            "phase_accounting": "absolute_orbit_nested_is_included_in_witness_timer",
            "absolute_x_orbit_certificate": {
                "degree": 3260,
                "closure": "pass",
                "excluded_degrees": [1630, 652, 20],
                "all_nonzero_kernel_multiples": "derived",
            },
            "stop_boundary": "before_kernel_polynomial_and_point_map",
        },
    )
    add_series(
        "k163-45641-horizontal-control", "nist-k163", 45641, 1, 1,
        "same_degree_horizontal_endomorphism_control", [6.86],
        "research/ecc2k130_conductor_isogenies_20261007/analogues/"
        "control163_45641_horizontal_endomorphism.out",
        "alpha=51-160*tau; 1,024 targets; both degree-45,641 composition "
        "identities pass; horizontal same-curve endomorphism, not a conductor transfer",
        "horizontal_endomorphism_control_not_conductor_transfer",
        {
            "max_rss_kib": 16140,
            "exit_status": 0,
            "certificate_status": "both_compositions_1024_targets_pass",
            "work_units": {"composition_targets": 1024},
            "phase_elapsed_ms": {"composition_checks": 6845},
            "stop_boundary": "same_degree_horizontal_control_not_conductor_transfer",
        },
    )
    add_series(
        "k163-45641-seed-preflight", "nist-k163", 45641, 1, 45641,
        "absolute_field_endpoint_preflight", [56.09],
        "research/ecc2k130_conductor_isogenies_20261007/analogues/"
        "probe163_45641_seed.out",
        "cold deterministic endpoint preflight; one fresh endpoint orbit "
        "distinct from the six historical samples; stops before a kernel "
        "polynomial or point map",
        "bounded_seed_preflight_endpoint_only_not_point_map",
        {
            "max_rss_kib": 45832,
            "exit_status": 0,
            "certificate_status": "fresh_endpoint_preflight_pass",
            "work_units": {"endpoint_orbits": 1},
            "stop_boundary": "before_kernel_polynomial_and_point_map",
        },
    )
    add_series(
        "k163-45641-endpoint-validator", "nist-k163", 45641, 1, 45641,
        "endpoint_floor_certificate", [90.66],
        "research/ecc2k130_conductor_isogenies_20261007/analogues/"
        "verify163_45641_seed_endpoint.out",
        "cold certificate replay for the fresh preflight endpoint; source and "
        "target orders, wrong-twist control, degree-11 cycle, and ring-class "
        "invariants pass; this does not construct or evaluate a point map",
        "endpoint_certificate_not_point_map_or_transfer",
        {
            "max_rss_kib": 33368,
            "exit_status": 0,
            "certificate_status": "endpoint_floor_certificate_pass",
            "work_units": {"endpoint_certificates": 1},
            "stop_boundary": "endpoint_certificate_not_point_map_or_transfer",
        },
    )
    add_series(
        "m37-73-map-dual-control", "koblitz-m37-a0", 73, 1, 73,
        "forward_map_dual_positive_control", [26.39],
        "research/isogeny_volcano_rho_20261005/map73_dual_control.out",
        "cold degree-73 positive control; explicit forward map and algebraic "
        "dual, both compositions, 1,024 inverse-degree recoveries, and planted "
        "recovery pass; this is not a NIST transfer measurement",
        "small_map_dual_and_recovery_positive_control_not_nist_transfer",
        {
            "max_rss_kib": 39708,
            "exit_status": 0,
            "certificate_status": "map_dual_compositions_and_recovery_pass",
            "work_units": {"targets": 1024, "planted_recoveries": 1},
            "phase_elapsed_ms": {
                "forward_construction": 530,
                "dual_construction": 24604,
                "target_checks": 556,
            },
            "stop_boundary": "small_degree_positive_control_not_nist_transfer",
        },
    )
    add_series("m51-deep-scan", "koblitz-m51-a0", 271, 271 * 120871, 120871,
               "bounded_endpoint_discovery_scan", [5280.943404762998],
               "research/isogeny_volcano_m51_deep_scan_20261013/README.md",
               "whole fixed 3.6-billion-rank scan yielding 42 certified ascending "
               "bottom-to-parent pairs; not a per-edge map time")
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    keys: list[str] = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=keys, extrasaction="raise", lineterminator="\n"
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(value, separators=(",", ":")) if isinstance(value, (list, dict)) else value for key, value in row.items()})


def plot_gaps(gaps: list[dict[str, Any]]) -> None:
    os.environ.setdefault("MPLCONFIGDIR", "/tmp/conductor-gap-panel-mpl")
    import matplotlib.pyplot as plt

    plt.rcParams["svg.hashsalt"] = "conductor-gap-panel-20261014"
    colors = {"split": "#2468b4", "inert": "#d35f2d", "ramified": "#7b4ab5"}
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.9), gridspec_kw={"width_ratios": [1.55, 1]})
    for ax in axes:
        for split in ("split", "inert"):
            rows = [row for row in gaps if row["split_type"] == split]
            ax.scatter(
                [row["gap_log2"] for row in rows],
                [math.log2(int(row["ambient_absolute_x_degree_upper_bound"])) for row in rows],
                s=[48 if row["family"] == "nist-k" else 28 for row in rows],
                c=colors[split], alpha=0.78, edgecolors="white", linewidths=0.45,
                label=f"{split} ({len(rows)})",
            )
        exact_rows = [
            row for row in gaps
            if row["working_field_status"]
            == "exact_abstract_cm_representative_x_orbit"
        ]
        ax.scatter(
            [row["gap_log2"] for row in exact_rows],
            [math.log2(int(row["ambient_absolute_x_degree_upper_bound"])) for row in exact_rows],
            s=120, facecolors="none", edgecolors="#111111", linewidths=1.2,
            marker="*", label="exact x-orbit (1 concrete, 1 abstract)",
        )
    by_id = {(row["class_id"], int(row["edge_degree"])): row for row in gaps}
    labels = [
        ("ecc2k-130", 263, "ECC2K-130 / 263", (7, -13)),
        ("koblitz-m109-a1", 3271, "m109 / 3,271", (8, 10)),
        ("nist-k163", 45641, "K-163 / 45,641", (9, -12)),
        ("nist-k283", 1697, "K-283 / 1,697", (-4, 13)),
        ("nist-k233", 5610641, "K-233 / 5.61M", (8, -13)),
        ("nist-k409", 21262439877311, "K-409 / 2.13e13", (7, 6)),
        ("nist-k571", 3952463, "K-571 / 3.95M", (8, 10)),
    ]
    ax = axes[0]
    for class_id, ell, label, offset in labels:
        row = by_id[(class_id, ell)]
        ax.annotate(
            label,
            (row["gap_log2"], math.log2(int(row["ambient_absolute_x_degree_upper_bound"]))),
            xytext=offset, textcoords="offset points", fontsize=7.2,
        )
    axes[0].set_xlim(0, 66)
    axes[0].set_ylim(0, 72)
    axes[0].set_title("Operational zoom")
    axes[1].set_title("Full range (three extreme directions retained)")
    for ax in axes:
        ax.set_xlabel("log2 prime gap degree [bits]")
        ax.grid(alpha=0.2)
    axes[0].set_ylabel("log2 derived ambient degree m*k [bits]")
    axes[1].legend(frameon=False, loc="upper left", fontsize=8)
    axes[1].text(
        0.995, 0.012,
        "43 rows: 2 exact minima / 41 ambient upper bounds",
        ha="right", va="bottom", transform=ax.transAxes, fontsize=7.5, color="#555555",
    )
    fig.suptitle("Conductor degree versus derived kernel-field ambient burden", fontsize=14)
    fig.tight_layout()
    metadata = {"Date": "2026-10-14"}
    svg_path = HERE / "gap-landscape.svg"
    fig.savefig(svg_path, metadata=metadata)
    svg_path.write_text(
        "\n".join(line.rstrip() for line in svg_path.read_text().splitlines()) + "\n"
    )
    fig.savefig(HERE / "gap-landscape.png", dpi=180, metadata=metadata)
    plt.close(fig)


def main() -> None:
    classes, gaps = build_classes_and_gaps()
    levels, adjacencies = build_levels(classes)
    controls = build_controls()
    effects = build_measured_effects()
    construction = build_construction_measurements()
    p224 = build_p224_candidate()
    xs = [row["gap_log2"] for row in gaps]
    ys = [math.log2(int(row["ambient_absolute_x_degree_upper_bound"])) for row in gaps]
    summary = {
        "schema": SCHEMA,
        "generated_date": "2026-10-14",
        "certified_prime_direction_rows": len(gaps),
        "vertical_direction_rows": len(gaps),
        "horizontal_direction_rows": 0,
        "horizontal_search_status": "not_assessed_in_this_panel",
        "distinct_prime_degrees": len({row["edge_degree"] for row in gaps}),
        "finite_field_trace_isogeny_classes": len(classes),
        "twist_deduplicated_geometry_families": len({
            (row["extension_degree"], tuple(row["f_pi_factorization"]))
            for row in classes
        }),
        "exact_conductor_levels": len(levels),
        "conditional_adjacent_level_rows": len(adjacencies),
        "nist_k_prime_direction_rows": sum(row["family"] == "nist-k" for row in gaps),
        "exact_absolute_x_orbit_rows": sum(
            row["working_field_status"]
            == "exact_abstract_cm_representative_x_orbit"
            for row in gaps
        ),
        "concrete_kernel_x_orbit_rows": sum(
            row["concrete_kernel_x_orbit_status"]
            == "certified_retained_relative_tower_witness"
            for row in gaps
        ),
        "ambient_upper_bound_working_field_rows": sum(
            row["working_field_status"]
            == "certified_ambient_upper_bound_only"
            for row in gaps
        ),
        "p224_potential_direction_rows": 1,
        "exact_zero_vertical_gap_controls": sum(row["control_type"] == "exact_zero_vertical_gap" for row in controls),
        "unresolved_controls": sum(row["control_type"] == "unresolved" for row in controls),
        "fully_charged_transfer_rows": 0,
        "weakness_eligible_rows": 0,
        "admitted_ecdlp_comparison_rows": 9,
        "withheld_ecdlp_comparison_rows": 4,
        "descriptive_association": {
            "metric": "Spearman(log2 ell, log2 derived m*k ambient degree)",
            "rho": pearson(rankdata(xs), rankdata(ys)),
            "n_rows": len(gaps),
            "inference": (
                "none; 41 of 43 m*k values are ambient upper bounds, and rows "
                "cluster within 20 trace/isogeny classes and 17 twist-deduplicated "
                "geometry families"
            ),
        },
    }
    payload = {
        "schema": SCHEMA,
        "summary": summary,
        "definitions": {
            "gap_row": "one maximal-order Koblitz class times one prime divisor of f_pi",
            "level_row": "one divisor f_E of squarefree f_pi",
            "adjacency_row": "one conditional f_E -> ell*f_E lattice placement",
            "kernel_x_degree": "least k with q-Frobenius scalar c satisfying c^k=+/-1 mod ell",
            "ambient_absolute_x_degree_upper_bound": (
                "m*k; a certified ambient upper bound for every ell-torsion "
                "x-coordinate, not a map-construction cost"
            ),
            "exact_abstract_cm_representative_x_orbit_degree": (
                "exact minimal absolute-Frobenius x-orbit degree for the "
                "certificate's abstract non-horizontal torsion vector; null "
                "without that certificate"
            ),
            "concrete_kernel_x_orbit_degree": (
                "exact minimal absolute-Frobenius x-orbit degree bound to a "
                "retained concrete kernel x-coordinate witness; null without "
                "that observed fail-closed certificate"
            ),
            "working_field_certificate": (
                "exact absolute-Frobenius order modulo sign on a stated "
                "non-horizontal ell-torsion vector; proves an x-orbit degree, "
                "not an explicit point, map, or runtime"
            ),
            "dense_packed_kernel_bytes": "ceil(((ell-1)/2+1)*m/8); payload proxy, not measured serialization",
            "measured_effect_sign": "log2(child mean / parent mean); positive means more child work",
        },
        "sources": source_refs(
            classes, gaps, levels, adjacencies, controls, p224, effects, construction
        ),
        "classes": classes,
        "gaps": gaps,
        "levels": levels,
        "adjacencies": adjacencies,
        "controls": controls,
        "p224_candidate": p224,
        "measured_effects": effects,
        "construction_measurements": construction,
    }
    (HERE / "panel.json").write_text(json.dumps(payload, indent=2) + "\n")
    write_csv(HERE / "gap-panel.csv", gaps)
    write_csv(HERE / "level-panel.csv", levels)
    write_csv(HERE / "adjacency-panel.csv", adjacencies)
    write_csv(HERE / "controls.csv", controls)
    write_csv(HERE / "measured-effects.csv", effects)
    write_csv(HERE / "construction-measurements.csv", construction)
    write_csv(HERE / "source-actions.csv", [
        {
            "schema": SCHEMA,
            "class_id": row["class_id"],
            "curve": row["label"],
            "m": row["extension_degree"],
            "signed_tau_orbit_size": 2 * row["extension_degree"],
            "ideal_gain_vs_negation_bits": row["source_signed_tau_gain_vs_negation_bits"],
            "evidence_kind": "exact_random_map_prediction",
            "scope": "source_action_not_transfer_or_wall_time",
            "evidence_path": "docs/reports/koblitz-rho-transfer-20261013/audit.json",
        }
        for row in classes if row["family"] == "nist-k"
    ])
    plot_gaps(gaps)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
