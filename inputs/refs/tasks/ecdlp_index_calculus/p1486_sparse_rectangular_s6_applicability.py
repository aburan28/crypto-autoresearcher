#!/usr/bin/env python3
"""Apply sparse rectangular equation-solving bounds to the S6 subgroup domain."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import os
import time
from pathlib import Path
from typing import Any

from sage.all import EllipticCurve, GF

from p1482_coordinate_routed_wagner_tree import (
    build_context,
    digest_int,
    factor_roots,
    point_json,
    point_key,
    write_atomic,
)


ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = ROOT / "ecdlp_index_calculus_state"
RESEARCH_DIR = ROOT / "research"
CONTRACT = STATE_DIR / "experiment_contract_p1486_sparse_rectangular_s6_applicability.md"
OUT = STATE_DIR / "p1486_sparse_rectangular_s6_applicability.json"
NOTE = RESEARCH_DIR / "p1486_sparse_rectangular_s6_applicability.md"

SCHEMA = "ecdlp.p1486_sparse_rectangular_s6_applicability.v1"
DIMENSION = 5
EXPECTED = {
    CONTRACT: "eb4546cc555f0b3e9998552336f4c8b5ba5a9e20b6acc0f829c4c5cf444b164f",
    ROOT / "tasks/ecdlp_index_calculus/p1482_coordinate_routed_wagner_tree.py":
        "14e1255f095df4c1219d01d43042bc0e03c893504469e6430943dcfce3820bca",
    STATE_DIR / "p1476_m_ary_sparse_deck_exponent_boundary.json":
        "c29426c61c687560b45e38cae1c50f18e89c2846a6d599c6f4583fc98ec70e5f",
    STATE_DIR / "p1478_sparse_s3_subgroup_norm_composition.json":
        "287a08a131ce7b56bd4e8468eb6c443d7bcba4b7fb2ba13c860866c21902b8df",
    STATE_DIR / "p1485_kummer_differential_pair_fiber.json":
        "c8b47ff4f086726651b1d020b72cf20a3b23522c71db713533d159a2d8651ead",
    STATE_DIR / "p1485_kummer_differential_pair_fiber_audit.json":
        "c93098d5a76d19fd32fe9aa2d79f767df5edab846ed4146029bb18fce356ccef",
}
FIXTURES = [
    {"L": 4, "p": 1033, "order": 1061, "a": 1, "b": 1},
    {"L": 8, "p": 32801, "order": 32479, "a": 1, "b": 5},
]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extension_element_key(value: Any, degree: int = 2) -> tuple[int, ...]:
    coefficients = list(value.polynomial())
    return tuple(int(coefficients[index]) if index < len(coefficients) else 0 for index in range(degree))


def extension_point_key(point: Any) -> tuple[Any, ...]:
    if point.is_zero():
        return ("O",)
    return extension_element_key(point[0]), extension_element_key(point[1])


def signed_base_deck(context: dict[str, Any]) -> list[Any]:
    points = []
    for root in factor_roots(context):
        lifts = sorted(
            context["curve"].lift_x(context["field"](root), all=True),
            key=point_key,
        )
        points.extend(lifts)
    return sorted(points, key=point_key)


def planted_target(context: dict[str, Any]) -> tuple[Any, tuple[Any, ...]]:
    deck = signed_base_deck(context)
    nonce = 0
    while True:
        source = tuple(
            deck[digest_int("P1486", "target", context["fixture"]["L"], nonce, slot) % len(deck)]
            for slot in range(DIMENSION)
        )
        target = sum(source, context["identity"])
        if not target.is_zero():
            return target, source
        nonce += 1


def transform_axes(
    values: list[Any], L: int, zeta: Any, exponent_sign: int, normalize: bool
) -> tuple[list[Any], dict[str, int]]:
    field = zeta.parent()
    total = L**DIMENSION
    data = list(values)
    table = [
        [zeta ** (exponent_sign * frequency * index) for index in range(L)]
        for frequency in range(L)
    ]
    for axis in range(DIMENSION):
        stride = L ** (DIMENSION - axis - 1)
        block = stride * L
        output = [field.zero()] * total
        for start in range(0, total, block):
            for offset in range(stride):
                vector = [data[start + index * stride + offset] for index in range(L)]
                for frequency in range(L):
                    output[start + frequency * stride + offset] = sum(
                        (table[frequency][index] * vector[index] for index in range(L)),
                        field.zero(),
                    )
        data = output
    scale_multiplications = 0
    if normalize:
        scale = field(total) ** -1
        data = [scale * value for value in data]
        scale_multiplications = total
    return data, {
        "axis_count": DIMENSION,
        "butterfly_multiplication_proxy": DIMENSION * L ** (DIMENSION + 1),
        "butterfly_addition_proxy": DIMENSION * (L - 1) * L**DIMENSION,
        "normalization_multiplications": scale_multiplications,
        "total_field_operation_proxy": (
            DIMENSION * L ** (DIMENSION + 1)
            + DIMENSION * (L - 1) * L**DIMENSION
            + scale_multiplications
        ),
    }


def fourier_roundtrip(values: list[Any], L: int, zeta: Any) -> dict[str, Any]:
    started = time.perf_counter()
    coefficients, forward_work = transform_axes(values, L, zeta, -1, True)
    recovered, inverse_work = transform_axes(coefficients, L, zeta, 1, False)
    support = [(index, int(value)) for index, value in enumerate(coefficients) if value != 0]
    return {
        "value_count": len(values),
        "nonzero_value_count": sum(value != 0 for value in values),
        "value_sha256": hashlib.sha256(
            b"|".join(str(int(value)).encode("ascii") for value in values)
        ).hexdigest(),
        "coefficient_support_count_M": len(support),
        "coefficient_density": len(support) / len(values),
        "coefficient_support_sha256": hashlib.sha256(
            b"\n".join(repr(row).encode("ascii") for row in support)
        ).hexdigest(),
        "forward_work": forward_work,
        "inverse_work": inverse_work,
        "roundtrip_exact": recovered == values,
        "roundtrip_mismatch_count": sum(first != second for first, second in zip(recovered, values)),
        "wall_seconds": time.perf_counter() - started,
    }


def sphere_size(L: int, radius: int) -> int:
    return sum(math.comb(DIMENSION, index) * (L - 1) ** index for index in range(radius + 1))


def paper_bounds(p: int, L: int, monomials: int) -> dict[str, Any]:
    log_t_denominator = math.log1p(1 / (p - 2))
    general_radius_M2_raw = math.log(2) / log_t_denominator
    general_radius_actual_raw = math.log(max(1, monomials)) / log_t_denominator
    general_radius_M2 = min(DIMENSION, math.floor(general_radius_M2_raw))
    general_radius_actual = min(DIMENSION, math.floor(general_radius_actual_raw))
    bounded_radius_raw = math.log2(max(1, monomials))
    bounded_radius = min(DIMENSION, math.floor(bounded_radius_raw))
    bounded_sphere = sphere_size(L, bounded_radius)
    general_sphere = sphere_size(L, general_radius_M2)
    return {
        "t_definition": "(p-1)/(p-2)",
        "log_t_M2_raw": general_radius_M2_raw,
        "general_radius_from_optimistic_M2_clamped": general_radius_M2,
        "log_t_actual_M_raw": general_radius_actual_raw,
        "general_radius_from_actual_M_clamped": general_radius_actual,
        "general_M2_sphere_size": general_sphere,
        "general_M2_sphere_log_L_exponent": math.log(general_sphere, L),
        "bounded_degree_log2_M_raw": bounded_radius_raw,
        "bounded_degree_radius_clamped": bounded_radius,
        "bounded_degree_sphere_size": bounded_sphere,
        "bounded_degree_sphere_log_L_exponent": math.log(bounded_sphere, L),
        "M_below_32_avoids_full_dimension": monomials < 32,
        "M_below_4_meets_integer_radius_at_most_one": monomials < 4,
        "strict_P1476_query_exponent_below_three_halves": (
            math.log(bounded_sphere, L) < 1.5
            and math.log(general_sphere, L) < 1.5
        ),
    }


def build_indicator(context: dict[str, Any]) -> dict[str, Any]:
    started = time.perf_counter()
    fixture = context["fixture"]
    p, L = fixture["p"], fixture["L"]
    extension = GF(p**2, name=f"z{L}")
    curve = EllipticCurve(extension, [fixture["a"], fixture["b"]])
    h = extension(context["h"])
    subgroup_x = []
    value = extension.one()
    for _ in range(L):
        subgroup_x.append(value)
        value *= h
    lifts = [
        sorted(curve.lift_x(x, all=True), key=extension_point_key)
        for x in subgroup_x
    ]
    if any(len(rows) != 2 or rows[0] != -rows[1] for rows in lifts):
        raise RuntimeError("P1486 quadratic-closure lift failure")

    target_base, planted_source = planted_target(context)
    target = curve(extension(target_base[0]), extension(target_base[1]))
    pair_rows = {
        (first, second): [
            (lifts[first][sign_first] + lifts[second][sign_second], sign_first, sign_second)
            for sign_first in range(2) for sign_second in range(2)
        ]
        for first in range(L) for second in range(L)
    }
    triple_rows = {}
    for indices in itertools.product(range(L), repeat=3):
        rows = {}
        for signs in itertools.product(range(2), repeat=3):
            point = sum(
                (lifts[index][sign] for index, sign in zip(indices, signs)),
                0 * target,
            )
            rows.setdefault(extension_point_key(point), signs)
        triple_rows[indices] = rows

    indicator = []
    witnesses = []
    actual_membership_probes = 0
    for indices in itertools.product(range(L), repeat=DIMENSION):
        triples = triple_rows[indices[2:]]
        witness = None
        for pair_point, sign_first, sign_second in pair_rows[indices[:2]]:
            actual_membership_probes += 1
            positive_needed = extension_point_key(target - pair_point)
            if positive_needed in triples:
                witness = (sign_first, sign_second, *triples[positive_needed], -1)
                break
            actual_membership_probes += 1
            negative_needed = extension_point_key(-target - pair_point)
            if negative_needed in triples:
                witness = (sign_first, sign_second, *triples[negative_needed], 1)
                break
        indicator.append(context["field"](witness is not None))
        if witness is not None:
            selected = [
                lifts[index][sign] for index, sign in zip(indices, witness[:DIMENSION])
            ]
            total = sum(selected, 0 * target) + witness[DIMENSION] * target
            if not total.is_zero():
                raise RuntimeError("P1486 source witness replay failure")
            witnesses.append((indices, witness))

    expected_planted_indices = []
    for point in planted_source:
        expected_planted_indices.append(next(
            index for index, x in enumerate(subgroup_x) if int(x) == int(point[0])
        ))
    if indicator[sum(index * L ** (DIMENSION - position - 1)
                     for position, index in enumerate(expected_planted_indices))] == 0:
        raise RuntimeError("P1486 planted target is absent from indicator")

    indicator_wall_seconds = time.perf_counter() - started
    zeta = context["field"](context["h"])
    s6_transform = fourier_roundtrip(indicator, L, zeta)
    constant = [context["field"].one()] * (L**DIMENSION)
    constant_transform = fourier_roundtrip(constant, L, zeta)
    ranked = sorted(
        range(L**DIMENSION),
        key=lambda index: (digest_int("P1486", "random-control", L, index), index),
    )
    random_support = set(ranked[:len(witnesses)])
    random_values = [context["field"](index in random_support) for index in range(L**DIMENSION)]
    random_transform = fourier_roundtrip(random_values, L, zeta)
    bounds = paper_bounds(p, L, s6_transform["coefficient_support_count_M"])
    return {
        "fixture": fixture,
        "domain_dimension_N": DIMENSION,
        "domain_size_L_to_N": L**DIMENSION,
        "extension_degree": 2,
        "target": point_json(target_base),
        "planted_source": [point_json(point) for point in planted_source],
        "planted_x_exponents": expected_planted_indices,
        "solution_tuple_count": len(witnesses),
        "solution_density": len(witnesses) / L**DIMENSION,
        "solution_witness_sha256": hashlib.sha256(
            b"\n".join(repr(row).encode("ascii") for row in witnesses)
        ).hexdigest(),
        "every_solution_has_verified_six_point_source": len(witnesses) == sum(value != 0 for value in indicator),
        "indicator_construction": {
            "pair_sign_sums": 4 * L**2,
            "pair_group_additions": 4 * L**2,
            "triple_sign_sums": 8 * L**3,
            "triple_group_additions": 16 * L**3,
            "actual_membership_probes": actual_membership_probes,
            "complete_membership_probe_bound": 8 * L**DIMENSION,
            "indicator_words": L**DIMENSION,
            "wall_seconds": indicator_wall_seconds,
        },
        "s6_equation_indicator": s6_transform,
        "constant_one_control": constant_transform,
        "weight_matched_random_control": random_transform,
        "paper_bounds": bounds,
    }


def render_note(payload: dict[str, Any]) -> str:
    lines = [
        "# P1486 sparse rectangular S6 applicability", "", "## Status", "",
        f"`{payload['status']}`", "",
        "| L | solutions | reduced M | density | bounded radius | sphere exponent |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for cell in payload["cells"]:
        transform = cell["s6_equation_indicator"]
        bounds = cell["paper_bounds"]
        lines.append(
            f"| {cell['fixture']['L']} | {cell['solution_tuple_count']} | "
            f"{transform['coefficient_support_count_M']} | {transform['coefficient_density']:.6f} | "
            f"{bounds['bounded_degree_radius_clamped']} | "
            f"{bounds['bounded_degree_sphere_log_L_exponent']:.6f} |"
        )
    lines.extend([
        "", "The paper remains valid; its direct testing-set strategy reaches the full",
        "five-coordinate subgroup domain on these exact equation indicators.", "",
    ])
    return "\n".join(lines)


def main() -> int:
    os.chdir(ROOT)
    observed = {str(path.relative_to(ROOT)): sha256_file(path) for path in EXPECTED}
    expected = {str(path.relative_to(ROOT)): digest for path, digest in EXPECTED.items()}
    if observed != expected:
        raise RuntimeError("frozen P1486 input mismatch")
    cells = []
    for fixture in FIXTURES:
        cell = build_indicator(build_context(fixture))
        cells.append(cell)
        print(json.dumps({
            "L": fixture["L"],
            "solutions": cell["solution_tuple_count"],
            "M": cell["s6_equation_indicator"]["coefficient_support_count_M"],
            "density": cell["s6_equation_indicator"]["coefficient_density"],
            "radius": cell["paper_bounds"]["bounded_degree_radius_clamped"],
            "sphere": cell["paper_bounds"]["bounded_degree_sphere_size"],
            "exponent": cell["paper_bounds"]["bounded_degree_sphere_log_L_exponent"],
        }, sort_keys=True), flush=True)

    exact = all(
        cell["solution_tuple_count"] > 0
        and cell["every_solution_has_verified_six_point_source"]
        and cell["s6_equation_indicator"]["roundtrip_exact"]
        for cell in cells
    )
    controls = all(
        cell["constant_one_control"]["roundtrip_exact"]
        and cell["constant_one_control"]["coefficient_support_count_M"] == 1
        and cell["weight_matched_random_control"]["roundtrip_exact"]
        and cell["weight_matched_random_control"]["nonzero_value_count"] == cell["solution_tuple_count"]
        for cell in cells
    )
    full_sphere = all(
        cell["paper_bounds"]["bounded_degree_radius_clamped"] == DIMENSION
        and cell["paper_bounds"]["bounded_degree_sphere_size"] == cell["domain_size_L_to_N"]
        and cell["paper_bounds"]["general_radius_from_optimistic_M2_clamped"] == DIMENSION
        and cell["paper_bounds"]["general_M2_sphere_size"] == cell["domain_size_L_to_N"]
        for cell in cells
    )
    reduced_sparse_gate = all(
        cell["s6_equation_indicator"]["coefficient_support_count_M"] < 4 for cell in cells
    )
    exponent_gate = all(
        cell["paper_bounds"]["strict_P1476_query_exponent_below_three_halves"]
        for cell in cells
    )
    signal = all((exact, controls, reduced_sparse_gate, exponent_gate))
    status = (
        "OBSERVATION_P1486_SPARSE_RECTANGULAR_S6_SIGNAL"
        if signal else
        "NEGATIVE_RESULT_P1486_RECTANGULAR_SPARSE_SOLVER_FULL_SPHERE_ON_S6"
    )
    payload = {
        "schema": SCHEMA,
        "status": status,
        "paper": {
            "title": "Zero testing and equation solving for sparse polynomials on rectangular domains",
            "authors": ["Erhard Aichinger", "Simon Grunbacher", "Paul Hametner"],
            "revision": "2026-03-22",
            "url": "https://arxiv.org/abs/2305.19669",
            "validity_boundary": "P1486 tests direct applicability and does not challenge the theorem.",
        },
        "cells": cells,
        "gates": {
            "all_indicators_and_six_point_sources_exact": exact,
            "all_transform_roundtrips_and_controls_exact": controls,
            "reduced_indicator_M_below_four_every_fixture": reduced_sparse_gate,
            "general_and_bounded_sphere_exponents_below_three_halves": exponent_gate,
            "full_H_to_the_fifth_sphere_reproduced": full_sphere,
            "source_opening_and_conversion_cost_not_waived": True,
            "P1476_relation_rank_descent_not_waived": True,
        },
        "sparse_rectangular_s6_signal": signal,
        "frozen_files": observed,
        "boundary": (
            "The direct rectangular testing-set strategy reaches H^5 for the tested reduced "
            "S6 equation indicators. This does not rule out a different encoding with fewer "
            "than four reduced characters or a variable-reducing compact-norm solver."
        ),
        "next_action": (
            "Return to P1478. A successor must specify a variable-reducing common-root/source "
            "algorithm on the compact transition norm; do not apply sparse zero testing to "
            "the same five-variable equation indicator again."
        ),
    }
    write_atomic(OUT, (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    write_atomic(NOTE, render_note(payload).encode("utf-8"))
    print(json.dumps({
        "output": str(OUT.relative_to(ROOT)),
        "note": str(NOTE.relative_to(ROOT)),
        "status": status,
        "M": [cell["s6_equation_indicator"]["coefficient_support_count_M"] for cell in cells],
        "sphere_exponents": [cell["paper_bounds"]["bounded_degree_sphere_log_L_exponent"] for cell in cells],
        "signal": signal,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
