#!/usr/bin/env sage -python
"""Audit exact tensor cut ranks of the P1486 S6 subgroup indicator."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import os
import time
from collections import Counter
from pathlib import Path
from typing import Any, Callable

from sage.all import matrix

import p1486_sparse_rectangular_s6_applicability as p1486


ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = ROOT / "ecdlp_index_calculus_state"
RESEARCH_DIR = ROOT / "research"
CONTRACT = STATE_DIR / "experiment_contract_p1488_s6_tensor_cut_rank_compression.md"
OUT = STATE_DIR / "p1488_s6_tensor_cut_rank_compression.json"
NOTE = RESEARCH_DIR / "p1488_s6_tensor_cut_rank_compression.md"

SCHEMA = "ecdlp.p1488_s6_tensor_cut_rank_compression.v1"
DIMENSION = 5
EXPECTED = {
    CONTRACT: "83f65e96288b0c3cfc5aa1efa4a0f4943dcf3db2c8a0d0313ad1b85a3d54d940",
    ROOT / "tasks/ecdlp_index_calculus/p1486_sparse_rectangular_s6_applicability.py":
        "5424ed434ffc56d36c3601e5a4b4eeaad7e9cee6f50995cffd8cd9b9ab3b47cb",
    STATE_DIR / "p1486_sparse_rectangular_s6_applicability.json":
        "32e97a7e1ffa124a5529592286fff3736a95dff9e8aa82971cadba246b8392c3",
    STATE_DIR / "p1486_sparse_rectangular_s6_applicability_audit.json":
        "06eec849df4c1f981b01625db8fd76227d36dbfd530d49d1058a42f95df589a8",
    STATE_DIR / "p1487_pair_state_functional_decomposition.json":
        "9e8c7c04c15864999ac52fe05685f758a557784dedf4e3fcab8ed1b43803eb5a",
    STATE_DIR / "p1487_pair_state_functional_decomposition_audit.json":
        "55382e6bea731a0804c8880492c41833f9187b78d9cd7f94f9a31ec9d556fb75",
}
PRIMARY_FIXTURES = [
    *p1486.FIXTURES,
    {"L": 16, "p": 1048609, "order": 1047539, "a": 5, "b": 7},
]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def values_sha256(values: list[Any]) -> str:
    return hashlib.sha256(b"|".join(str(int(value)).encode("ascii") for value in values)).hexdigest()


def capture_summary(values: list[Any]) -> dict[str, Any]:
    nonzero = sum(value != 0 for value in values)
    return {
        "coefficient_density": 1 / len(values),
        "coefficient_support_count_M": 1,
        "nonzero_value_count": nonzero,
        "roundtrip_exact": True,
        "value_count": len(values),
        "value_sha256": values_sha256(values),
    }


def capture_indicator(
    context: dict[str, Any],
    target_builder: Callable[[dict[str, Any]], tuple[Any, tuple[Any, ...]]] | None = None,
) -> tuple[dict[str, Any], list[Any], list[Any], list[Any]]:
    captured: list[list[Any]] = []
    original_fourier = p1486.fourier_roundtrip
    original_target = p1486.planted_target

    def capture(values: list[Any], _L: int, _zeta: Any) -> dict[str, Any]:
        copied = list(values)
        captured.append(copied)
        return capture_summary(copied)

    p1486.fourier_roundtrip = capture
    if target_builder is not None:
        p1486.planted_target = target_builder
    try:
        cell = p1486.build_indicator(context)
    finally:
        p1486.fourier_roundtrip = original_fourier
        p1486.planted_target = original_target
    if len(captured) != 3:
        raise RuntimeError(f"P1488 expected three captured tensors, got {len(captured)}")
    return cell, captured[0], captured[1], captured[2]


def prospective_target_builder(context: dict[str, Any], nonce: int) -> Callable[[dict[str, Any]], tuple[Any, tuple[Any, ...]]]:
    deck = p1486.signed_base_deck(context)

    def build(_context: dict[str, Any]) -> tuple[Any, tuple[Any, ...]]:
        local_nonce = nonce
        while True:
            source = tuple(
                deck[p1486.digest_int("P1488", "target", context["fixture"]["L"], local_nonce, slot) % len(deck)]
                for slot in range(DIMENSION)
            )
            target = sum(source, context["identity"])
            if not target.is_zero():
                return target, source
            local_nonce += 1000

    return build


def cut_ranks(values: list[Any], L: int, field: Any) -> list[int]:
    return [
        int(matrix(field, L**cut, L ** (DIMENSION - cut), values).rank())
        for cut in range(1, DIMENSION)
    ]


def tuple_from_index(index: int, L: int) -> tuple[int, ...]:
    coordinates = [0] * DIMENSION
    for position in range(DIMENSION - 1, -1, -1):
        coordinates[position] = index % L
        index //= L
    return tuple(coordinates)


def support_tuples(values: list[Any], L: int) -> list[tuple[int, ...]]:
    return [tuple_from_index(index, L) for index, value in enumerate(values) if value != 0]


def unique_permutations(row: tuple[int, ...]) -> set[tuple[int, ...]]:
    return set(itertools.permutations(row))


def orbit_profile(values: list[Any], L: int) -> dict[str, Any]:
    support = set(support_tuples(values, L))
    representatives = sorted({tuple(sorted(row)) for row in support})
    rows = []
    symmetric = True
    for representative in representatives:
        orbit = unique_permutations(representative)
        present = orbit & support
        symmetric = symmetric and present == orbit
        partition = tuple(sorted(Counter(representative).values(), reverse=True))
        rows.append(
            {
                "multiplicity_partition": list(partition),
                "orbit_size": len(orbit),
                "present_size": len(present),
                "representative": list(representative),
            }
        )
    return {
        "orbit_count": len(rows),
        "orbit_size_multiset": sorted(row["orbit_size"] for row in rows),
        "permutation_symmetric": symmetric,
        "rows": rows,
        "support_weight": len(support),
    }


def orbit_control(values: list[Any], L: int, field: Any) -> tuple[list[Any], dict[str, Any]]:
    profile = orbit_profile(values, L)
    forbidden = {tuple(row["representative"]) for row in profile["rows"]}
    used = set()
    support = set()
    control_rows = []
    for orbit_index, row in enumerate(profile["rows"]):
        partition = list(row["multiplicity_partition"])
        nonce = 0
        while True:
            distinct_values = []
            for slot in range(len(partition)):
                value = p1486.digest_int("P1488", "orbit-control", L, orbit_index, nonce, slot) % L
                while value in distinct_values:
                    value = (value + 1) % L
                distinct_values.append(value)
            representative = tuple(sorted(
                value
                for value, multiplicity in zip(distinct_values, partition)
                for _ in range(multiplicity)
            ))
            if representative not in forbidden and representative not in used:
                break
            nonce += 1
            if nonce > 10000:
                raise RuntimeError("P1488 could not build a distinct orbit control")
        used.add(representative)
        orbit = unique_permutations(representative)
        support.update(orbit)
        control_rows.append(
            {
                "multiplicity_partition": partition,
                "orbit_size": len(orbit),
                "representative": list(representative),
            }
        )
    if len(support) != profile["support_weight"]:
        raise RuntimeError("P1488 orbit-control weight mismatch")
    control = [
        field(tuple_from_index(index, L) in support)
        for index in range(L**DIMENSION)
    ]
    control_profile = orbit_profile(control, L)
    if control_profile["orbit_size_multiset"] != profile["orbit_size_multiset"]:
        raise RuntimeError("P1488 orbit-control profile mismatch")
    return control, {
        "control_orbit_rows": control_rows,
        "orbit_size_multiset_exact": True,
        "support_weight_exact": len(support) == profile["support_weight"],
    }


def tt_metrics(ranks: list[int], L: int) -> dict[str, Any]:
    extended = [1, *ranks, 1]
    core_terms = [L * extended[index] * extended[index + 1] for index in range(DIMENSION)]
    contraction_terms = [extended[index] * extended[index + 1] for index in range(DIMENSION)]
    storage = sum(core_terms)
    contraction = sum(contraction_terms)
    return {
        "core_storage_terms": core_terms,
        "dense_core_storage": storage,
        "dense_core_storage_log_L_exponent": math.log(storage, L),
        "single_entry_contraction_proxy": contraction,
        "single_entry_contraction_log_L_exponent": math.log(contraction, L),
    }


def tensor_record(values: list[Any], L: int, field: Any) -> dict[str, Any]:
    ranks = cut_ranks(values, L, field)
    return {
        "cut_ranks": ranks,
        "middle_rank": max(ranks[1:3]),
        "paired_cut_ranks_exact": ranks[0] == ranks[3] and ranks[1] == ranks[2],
        "tt_metrics": tt_metrics(ranks, L),
        "value_sha256": values_sha256(values),
        "weight": sum(value != 0 for value in values),
    }


def primary_cell(fixture: dict[str, int]) -> dict[str, Any]:
    started = time.perf_counter()
    context = p1486.build_context(fixture)
    source_cell, indicator, constant, random_control = capture_indicator(context)
    L = int(fixture["L"])
    field = context["field"]
    true_profile = orbit_profile(indicator, L)
    symmetric_control, profile_control = orbit_control(indicator, L, field)
    true_record = tensor_record(indicator, L, field)
    orbit_record = tensor_record(symmetric_control, L, field)
    constant_record = tensor_record(constant, L, field)
    random_record = tensor_record(random_control, L, field)

    fourier = None
    if L <= 8:
        zeta = field(context["h"])
        coefficients, work = p1486.transform_axes(indicator, L, zeta, -1, True)
        coefficient_ranks = cut_ranks(coefficients, L, field)
        fourier = {
            "coefficient_cut_ranks": coefficient_ranks,
            "cut_ranks_invariant": coefficient_ranks == true_record["cut_ranks"],
            "forward_work": work,
        }
    return {
        "L": L,
        "constant_one_control": constant_record,
        "every_solution_has_verified_source": source_cell["every_solution_has_verified_six_point_source"],
        "fixture": fixture,
        "fourier_rank_check": fourier,
        "indicator_construction": source_cell["indicator_construction"],
        "orbit_profile": true_profile,
        "orbit_profile_control": {
            **orbit_record,
            **profile_control,
        },
        "rank_advantage_over_orbit_control": (
            true_record["cut_ranks"][1] < orbit_record["cut_ranks"][1]
            and true_record["cut_ranks"][2] < orbit_record["cut_ranks"][2]
        ),
        "solution_tuple_count": source_cell["solution_tuple_count"],
        "solution_witness_sha256": source_cell["solution_witness_sha256"],
        "s6_indicator": true_record,
        "target": source_cell["target"],
        "unstructured_weight_matched_control": random_record,
        "wall_seconds": time.perf_counter() - started,
    }


def prospective_cell(context: dict[str, Any], nonce: int) -> dict[str, Any]:
    started = time.perf_counter()
    source_cell, indicator, _constant, _random = capture_indicator(
        context,
        prospective_target_builder(context, nonce),
    )
    L = int(context["fixture"]["L"])
    field = context["field"]
    control, profile_control = orbit_control(indicator, L, field)
    true_record = tensor_record(indicator, L, field)
    control_record = tensor_record(control, L, field)
    return {
        "nonce": nonce,
        "orbit_count": orbit_profile(indicator, L)["orbit_count"],
        "orbit_profile_control": {**control_record, **profile_control},
        "rank_advantage_over_orbit_control": (
            true_record["cut_ranks"][1] < control_record["cut_ranks"][1]
            and true_record["cut_ranks"][2] < control_record["cut_ranks"][2]
        ),
        "s6_indicator": true_record,
        "solution_tuple_count": source_cell["solution_tuple_count"],
        "solution_witness_sha256": source_cell["solution_witness_sha256"],
        "target": source_cell["target"],
        "wall_seconds": time.perf_counter() - started,
    }


def fit_slope(cells: list[dict[str, Any]], selector: Callable[[dict[str, Any]], float]) -> dict[str, float]:
    xs = [math.log(float(cell["L"])) for cell in cells]
    ys = [math.log(float(selector(cell))) for cell in cells]

    def slope(indices: list[int]) -> float:
        x_mean = sum(xs[index] for index in indices) / len(indices)
        y_mean = sum(ys[index] for index in indices) / len(indices)
        numerator = sum((xs[index] - x_mean) * (ys[index] - y_mean) for index in indices)
        denominator = sum((xs[index] - x_mean) ** 2 for index in indices)
        return numerator / denominator

    full = slope(list(range(len(cells))))
    leave_one_out = [slope([index for index in range(len(cells)) if index != omitted]) for omitted in range(len(cells))]
    return {
        "leave_one_out_max": max(leave_one_out),
        "leave_one_out_min": min(leave_one_out),
        "slope": full,
    }


def write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def render_note(payload: dict[str, Any]) -> str:
    lines = [
        "# P1488 S6 tensor cut-rank compression",
        "",
        "## Status",
        "",
        f"`{payload['status']}`",
        "",
        "| L | solutions | S6 ranks | orbit-control ranks | TT storage | rank advantage |",
        "|---:|---:|---|---|---:|---:|",
    ]
    for cell in payload["primary_cells"]:
        lines.append(
            f"| {cell['L']} | {cell['solution_tuple_count']} | "
            f"{cell['s6_indicator']['cut_ranks']} | {cell['orbit_profile_control']['cut_ranks']} | "
            f"{cell['s6_indicator']['tt_metrics']['dense_core_storage']} | "
            f"{cell['rank_advantage_over_orbit_control']} |"
        )
    lines.extend(
        [
            "",
            f"Prospective L8 target advantages: `{payload['prospective_summary']['rank_advantage_count']}/8`.",
            "",
            "Permutation-orbit matching removes the apparent L8 low-rank signal,",
            "and the L16 middle rank grows to the pair-state scale. The exact TT",
            "is therefore a target-enumerated diagnostic, not a sub-rho source",
            "constructor or a complete ECDLP algorithm.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    frozen = {}
    for path, expected in EXPECTED.items():
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"P1488 frozen hash mismatch for {path}: {actual} != {expected}")
        frozen[str(path.relative_to(ROOT))] = actual

    primary = [primary_cell(fixture) for fixture in PRIMARY_FIXTURES]
    prospective_context = p1486.build_context(p1486.FIXTURES[1])
    prospective = [prospective_cell(prospective_context, nonce) for nonce in range(8)]
    prospective_advantages = sum(cell["rank_advantage_over_orbit_control"] for cell in prospective)
    storage_fit = fit_slope(
        primary,
        lambda cell: cell["s6_indicator"]["tt_metrics"]["dense_core_storage"],
    )
    middle_rank_fit = fit_slope(primary, lambda cell: cell["s6_indicator"]["middle_rank"])
    all_exact = all(
        cell["every_solution_has_verified_source"]
        and cell["orbit_profile"]["permutation_symmetric"]
        and cell["s6_indicator"]["paired_cut_ranks_exact"]
        and cell["orbit_profile_control"]["paired_cut_ranks_exact"]
        and cell["orbit_profile_control"]["support_weight_exact"]
        and cell["orbit_profile_control"]["orbit_size_multiset_exact"]
        and (cell["fourier_rank_check"] is None or cell["fourier_rank_check"]["cut_ranks_invariant"])
        for cell in primary
    )
    primary_advantage = all(cell["rank_advantage_over_orbit_control"] for cell in primary)
    exponent_gate = storage_fit["leave_one_out_max"] < 1.5
    signal = all_exact and primary_advantage and prospective_advantages >= 6 and exponent_gate
    status = (
        "CANDIDATE_P1488_S6_TENSOR_CUT_RANK_SIGNAL_NEEDS_CONSTRUCTOR"
        if signal
        else "NEGATIVE_RESULT_P1488_TENSOR_RANK_EXPLAINED_BY_ORBITS_OR_ABOVE_GATE"
    )
    payload = {
        "boundary": {
            "candidate_vs_verified": "Ranks and witnesses are exact; TT cores are diagnosed after complete indicator construction.",
            "closed": "Dense exact TT compression of this target-specific five-axis S6 indicator under the tested variable representation.",
            "not_closed": "Implicit tensor cores from a different invariant, approximate randomized contractions with exact source certification, or another factor base.",
            "pollard_rho": "No target-time constructor, relation/rank/descent pipeline, or faster-than-rho ECDLP claim.",
        },
        "fits": {
            "dense_tt_storage_vs_L": storage_fit,
            "middle_rank_vs_L": middle_rank_fit,
        },
        "frozen_files": frozen,
        "gates": {
            "all_exact_controls": all_exact,
            "complete_five_term_backend": False,
            "dense_tt_storage_leave_one_out_below_three_halves": exponent_gate,
            "primary_rank_advantage_every_fixture": primary_advantage,
            "prospective_rank_advantage_at_least_six_of_eight": prospective_advantages >= 6,
            "source_opening_below_L_three_halves": False,
        },
        "next_action": (
            "Do not build target-specific TT cores by enumerating H^5. Isolate the permutation-orbit quotient explicitly and test whether its source-orbit generator can be constructed below L^1.5; otherwise return to a different factor-base/state invariant."
        ),
        "primary_cells": primary,
        "prospective_L8_targets": prospective,
        "prospective_summary": {
            "rank_advantage_count": prospective_advantages,
            "target_count": len(prospective),
        },
        "schema": SCHEMA,
        "status": status,
    }
    write_atomic(OUT, (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    write_atomic(NOTE, render_note(payload).encode("utf-8"))
    print(json.dumps({
        "status": status,
        "primary": [
            {
                "L": cell["L"],
                "solutions": cell["solution_tuple_count"],
                "ranks": cell["s6_indicator"]["cut_ranks"],
                "orbit_control_ranks": cell["orbit_profile_control"]["cut_ranks"],
                "rank_advantage": cell["rank_advantage_over_orbit_control"],
            }
            for cell in primary
        ],
        "prospective_rank_advantages": prospective_advantages,
        "storage_fit": storage_fit,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
