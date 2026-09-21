#!/usr/bin/env sage -python
"""Descend P1488 quadratic-closure S6 sources to rational factor rows."""

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

from sage.all import EllipticCurve, GF, matrix

import p1486_sparse_rectangular_s6_applicability as p1486


ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = ROOT / "ecdlp_index_calculus_state"
RESEARCH_DIR = ROOT / "research"
CONTRACT = STATE_DIR / "experiment_contract_p1489_quadratic_closure_rational_relation_descent.md"
P1488_SOURCE = STATE_DIR / "p1488_s6_tensor_cut_rank_compression.json"
OUT = STATE_DIR / "p1489_quadratic_closure_rational_relation_descent.json"
NOTE = RESEARCH_DIR / "p1489_quadratic_closure_rational_relation_descent.md"

SCHEMA = "ecdlp.p1489_quadratic_closure_rational_relation_descent.v1"
DIMENSION = 5
EXPECTED = {
    CONTRACT: "f573fa0c506c791c311c9b343e9d3f53d8acd10dbbcf310f3ba93f36d835023e",
    P1488_SOURCE: "2c2149292a94af7b3e731070f9980db8cec506596ecc7af091219dc472ae3349",
    STATE_DIR / "p1488_s6_tensor_cut_rank_compression_audit.json":
        "093dc2b2bbed033c619b99e4097c7f11e9be85df57cf784ff69574755b9530cb",
    STATE_DIR / "p1486_sparse_rectangular_s6_applicability.json":
        "32e97a7e1ffa124a5529592286fff3736a95dff9e8aa82971cadba246b8392c3",
    STATE_DIR / "p1486_sparse_rectangular_s6_applicability_audit.json":
        "06eec849df4c1f981b01625db8fd76227d36dbfd530d49d1058a42f95df589a8",
}
PRIMARY_FIXTURES = [
    *p1486.FIXTURES,
    {"L": 16, "p": 1048609, "order": 1047539, "a": 5, "b": 7},
]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prospective_target(context: dict[str, Any], nonce: int) -> tuple[Any, tuple[Any, ...]]:
    deck = p1486.signed_base_deck(context)
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


def setup_extension(context: dict[str, Any]) -> dict[str, Any]:
    fixture = context["fixture"]
    p = int(fixture["p"])
    L = int(fixture["L"])
    extension = GF(p**2, name=f"z1489_{L}")
    curve = EllipticCurve(extension, [fixture["a"], fixture["b"]])
    subgroup_x = []
    value = extension.one()
    h = extension(context["h"])
    for _ in range(L):
        subgroup_x.append(value)
        value *= h
    lifts = [
        sorted(curve.lift_x(x, all=True), key=p1486.extension_point_key)
        for x in subgroup_x
    ]
    if any(len(rows) != 2 or rows[0] != -rows[1] for rows in lifts):
        raise RuntimeError("P1489 extension-lift failure")
    rational_indices = [
        index
        for index, rows in enumerate(lifts)
        if rows[0][1] ** p == rows[0][1]
    ]
    rational_set = set(rational_indices)
    canonical_base_points = {}
    for index in rational_indices:
        point = lifts[index][0]
        canonical_base_points[index] = context["curve"](
            context["field"](int(point[0])),
            context["field"](int(point[1])),
        )
    pair_rows = {
        (first, second): [
            (lifts[first][sign_first] + lifts[second][sign_second], sign_first, sign_second)
            for sign_first in range(2)
            for sign_second in range(2)
        ]
        for first in range(L)
        for second in range(L)
    }
    triple_rows = {}
    identity = curve(0)
    for indices in itertools.product(range(L), repeat=3):
        rows = {}
        for signs in itertools.product(range(2), repeat=3):
            point = sum(
                (lifts[index][sign] for index, sign in zip(indices, signs)),
                identity,
            )
            rows.setdefault(p1486.extension_point_key(point), signs)
        triple_rows[indices] = rows
    frobenius_rational_exact = all(
        point[0] ** p == point[0] and point[1] ** p == point[1]
        for index in rational_indices
        for point in lifts[index]
    )
    frobenius_nonrational_negation_exact = all(
        point[0] ** p == point[0] and curve(point[0] ** p, point[1] ** p) == -point
        for index in range(L)
        if index not in rational_set
        for point in lifts[index]
    )
    return {
        "canonical_base_points": canonical_base_points,
        "curve": curve,
        "extension": extension,
        "frobenius_nonrational_negation_exact": frobenius_nonrational_negation_exact,
        "frobenius_rational_exact": frobenius_rational_exact,
        "identity": identity,
        "lifts": lifts,
        "pair_rows": pair_rows,
        "rational_indices": rational_indices,
        "rational_set": rational_set,
        "subgroup_x": subgroup_x,
        "triple_rows": triple_rows,
    }


def first_witness(
    setup: dict[str, Any],
    indices: tuple[int, ...],
    target: Any,
    counter: dict[str, int] | None = None,
) -> tuple[int, ...] | None:
    triples = setup["triple_rows"][indices[2:]]
    for pair_point, sign_first, sign_second in setup["pair_rows"][indices[:2]]:
        if counter is not None:
            counter["membership_probes"] += 1
        positive = p1486.extension_point_key(target - pair_point)
        if positive in triples:
            return sign_first, sign_second, *triples[positive], -1
        if counter is not None:
            counter["membership_probes"] += 1
        negative = p1486.extension_point_key(-target - pair_point)
        if negative in triples:
            return sign_first, sign_second, *triples[negative], 1
    return None


def support_orbits(setup: dict[str, Any], L: int, target: Any) -> tuple[list[tuple[int, ...]], dict[str, int]]:
    accepted = []
    counter = {"membership_probes": 0, "quotient_multisets": 0}
    for indices in itertools.combinations_with_replacement(range(L), DIMENSION):
        counter["quotient_multisets"] += 1
        if first_witness(setup, indices, target, counter) is not None:
            accepted.append(indices)
    return accepted, counter


def expanded_support(representatives: list[tuple[int, ...]]) -> list[tuple[int, ...]]:
    rows = set()
    for representative in representatives:
        rows.update(itertools.permutations(representative))
    return sorted(rows)


def p1486_witness_hash(setup: dict[str, Any], representatives: list[tuple[int, ...]], target: Any) -> str:
    witnesses = []
    for indices in expanded_support(representatives):
        witness = first_witness(setup, indices, target)
        if witness is None:
            raise RuntimeError("P1489 expanded support lost a witness")
        witnesses.append((indices, witness))
    return hashlib.sha256(
        b"\n".join(repr(row).encode("ascii") for row in witnesses)
    ).hexdigest()


def all_sign_witnesses(setup: dict[str, Any], indices: tuple[int, ...], target: Any) -> list[tuple[tuple[int, ...], int]]:
    rows = []
    for signs in itertools.product(range(2), repeat=DIMENSION):
        selected = [setup["lifts"][index][sign] for index, sign in zip(indices, signs)]
        total = sum(selected, setup["identity"])
        if total == target:
            rows.append((signs, -1))
        elif total == -target:
            rows.append((signs, 1))
    return rows


def signed_integer(value: int, order: int) -> int:
    value %= order
    return value - order if value > order // 2 else value


def relation_record(
    context: dict[str, Any],
    setup: dict[str, Any],
    indices: tuple[int, ...],
    signs: tuple[int, ...],
    target_sign: int,
    target_base: Any,
) -> dict[str, Any]:
    selected = [setup["lifts"][index][sign] for index, sign in zip(indices, signs)]
    rational_points = [
        point for index, point in zip(indices, selected) if index in setup["rational_set"]
    ]
    nonrational_points = [
        point for index, point in zip(indices, selected) if index not in setup["rational_set"]
    ]
    rational_subtotal = sum(rational_points, setup["identity"])
    nonrational_subtotal = sum(nonrational_points, setup["identity"])
    if not nonrational_subtotal.is_zero():
        raise RuntimeError("P1489 nonrational subtotal did not cancel")
    target_extension = setup["curve"](
        setup["extension"](target_base[0]),
        setup["extension"](target_base[1]),
    )
    if rational_subtotal + target_sign * target_extension != setup["identity"]:
        raise RuntimeError("P1489 rational subtotal does not replay target")

    column_by_index = {index: column for column, index in enumerate(setup["rational_indices"])}
    coefficients = [0] * len(setup["rational_indices"])
    for index, sign in zip(indices, signs):
        if index in column_by_index:
            coefficients[column_by_index[index]] += 1 if sign == 0 else -1
    order = int(context["fixture"]["order"])
    coefficients = [signed_integer(coefficient, order) for coefficient in coefficients]
    replay = sum(
        (
            coefficient * setup["canonical_base_points"][index]
            for coefficient, index in zip(coefficients, setup["rational_indices"])
        ),
        context["identity"],
    ) + target_sign * target_base
    if not replay.is_zero():
        raise RuntimeError("P1489 base-field relation replay failure")
    return {
        "coefficients": coefficients,
        "nonrational_endpoint_count": len(nonrational_points),
        "nonrational_subtotal_zero": True,
        "rational_endpoint_count": len(rational_points),
        "target_sign": target_sign,
    }


def matrix_rank(rows: list[list[int]], modulus: int, width: int) -> int:
    if not rows:
        return 0
    return int(matrix(GF(modulus), len(rows), width, [value for row in rows for value in row]).rank())


def target_cell(
    context: dict[str, Any],
    setup: dict[str, Any],
    target_base: Any,
    target_source: tuple[Any, ...],
    recorded: dict[str, Any],
    target_id: str,
) -> dict[str, Any]:
    started = time.perf_counter()
    target = setup["curve"](
        setup["extension"](target_base[0]),
        setup["extension"](target_base[1]),
    )
    L = int(context["fixture"]["L"])
    representatives, work = support_orbits(setup, L, target)
    expanded_count = sum(len(set(itertools.permutations(row))) for row in representatives)
    recorded_count = int(recorded["solution_tuple_count"])
    if expanded_count != recorded_count:
        raise RuntimeError(f"P1489 solution count mismatch for {target_id}: {expanded_count} != {recorded_count}")
    witness_hash = p1486_witness_hash(setup, representatives, target)
    if witness_hash != recorded["solution_witness_sha256"]:
        raise RuntimeError(f"P1489 witness hash mismatch for {target_id}")

    relation_records = []
    for representative in representatives:
        for signs, target_sign in all_sign_witnesses(setup, representative, target):
            relation_records.append(
                relation_record(context, setup, representative, signs, target_sign, target_base)
            )
    deduped = {}
    for record in relation_records:
        key = tuple(record["coefficients"]), int(record["target_sign"])
        deduped.setdefault(key, record)
    rows = list(deduped.values())
    factor_rows = [record["coefficients"] for record in rows]
    augmented_rows = [record["coefficients"] + [record["target_sign"]] for record in rows]
    order = int(context["fixture"]["order"])
    factor_width = len(setup["rational_indices"])
    factor_rank = matrix_rank(factor_rows, order, factor_width)
    augmented_rank = matrix_rank(augmented_rows, order, factor_width + 1)
    covered = sorted({column for row in factor_rows for column, value in enumerate(row) if value % order})
    rational_histogram = Counter(record["rational_endpoint_count"] for record in relation_records)
    nonrational_histogram = Counter(record["nonrational_endpoint_count"] for record in relation_records)

    planted_coefficients = [0] * factor_width
    index_by_x = {int(setup["subgroup_x"][index]): index for index in setup["rational_indices"]}
    column_by_index = {index: column for column, index in enumerate(setup["rational_indices"])}
    for point in target_source:
        index = index_by_x[int(point[0])]
        canonical = setup["canonical_base_points"][index]
        sign = 1 if point == canonical else -1
        planted_coefficients[column_by_index[index]] += sign
    planted_coefficients = [signed_integer(value, order) for value in planted_coefficients]
    planted_keys = {
        (tuple(planted_coefficients), -1),
        (tuple(-value for value in planted_coefficients), 1),
    }
    planted_row_present = any(
        (tuple(record["coefficients"]), int(record["target_sign"])) in planted_keys
        for record in rows
    )
    if not planted_row_present:
        raise RuntimeError(f"P1489 planted positive control absent for {target_id}")
    all_rows_planted_equivalent = all(
        (tuple(record["coefficients"]), int(record["target_sign"])) in planted_keys
        for record in rows
    )
    non_planted_row_count = sum(
        (tuple(record["coefficients"]), int(record["target_sign"])) not in planted_keys
        for record in rows
    )

    return {
        "L": L,
        "all_rows_planted_equivalent": all_rows_planted_equivalent,
        "all_nonrational_subtotals_zero": all(record["nonrational_subtotal_zero"] for record in relation_records),
        "augmented_rank": augmented_rank,
        "deduplicated_rational_row_count": len(rows),
        "expanded_solution_count": expanded_count,
        "factor_column_count": factor_width,
        "factor_column_coverage": covered,
        "factor_rank": factor_rank,
        "full_factor_rank": factor_rank == factor_width,
        "non_planted_rational_row_count": non_planted_row_count,
        "nonrational_sign_witness_count": sum(record["nonrational_endpoint_count"] > 0 for record in relation_records),
        "nonrational_endpoint_histogram": {str(key): value for key, value in sorted(nonrational_histogram.items())},
        "orbit_count": len(representatives),
        "planted_positive_control_present": planted_row_present,
        "quotient_scan": {
            **work,
            "quotient_multiset_log_L_exponent": math.log(work["quotient_multisets"], L),
        },
        "rational_endpoint_histogram": {str(key): value for key, value in sorted(rational_histogram.items())},
        "raw_sign_witness_count": len(relation_records),
        "target": p1486.point_json(target_base),
        "target_id": target_id,
        "target_is_planted": True,
        "wall_seconds": time.perf_counter() - started,
        "witness_sha256": witness_hash,
        "zero_factor_row_count": sum(not any(record["coefficients"]) for record in rows),
        "_factor_rows": factor_rows,
        "_augmented_rows": augmented_rows,
    }


def combined_L8(panel: list[dict[str, Any]], order: int) -> dict[str, Any]:
    factor_width = int(panel[0]["factor_column_count"])
    rows = []
    factor_rows = []
    for target_index, cell in enumerate(panel):
        for factor_row, augmented_row in zip(cell["_factor_rows"], cell["_augmented_rows"]):
            target_columns = [0] * len(panel)
            target_columns[target_index] = augmented_row[-1]
            factor_rows.append(factor_row)
            rows.append(factor_row + target_columns)
    return {
        "augmented_rank": matrix_rank(rows, order, factor_width + len(panel)),
        "factor_column_count": factor_width,
        "factor_rank": matrix_rank(factor_rows, order, factor_width),
        "full_factor_rank": matrix_rank(factor_rows, order, factor_width) == factor_width,
        "row_count": len(rows),
        "target_count": len(panel),
    }


def strip_internal(cell: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in cell.items() if not key.startswith("_")}


def write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def render_note(payload: dict[str, Any]) -> str:
    lines = [
        "# P1489 quadratic-closure rational-relation descent",
        "",
        "## Status",
        "",
        f"`{payload['status']}`",
        "",
        "| target | L | orbits | rational rows | factor rank | factor columns |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for cell in payload["target_cells"]:
        lines.append(
            f"| {cell['target_id']} | {cell['L']} | {cell['orbit_count']} | "
            f"{cell['deduplicated_rational_row_count']} | {cell['factor_rank']} | "
            f"{cell['factor_column_count']} |"
        )
    lines.extend(
        [
            "",
            "Every extension-only subtotal cancels exactly, so only the rational",
            "rows survive descent. These rows are still derived from planted targets",
            "and a quotient scan of exponent five; they do not constitute a relation",
            "generator or a faster-than-rho ECDLP algorithm.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    frozen = {}
    for path, expected in EXPECTED.items():
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"P1489 frozen hash mismatch for {path}: {actual} != {expected}")
        frozen[str(path.relative_to(ROOT))] = actual
    p1488 = json.loads(P1488_SOURCE.read_text(encoding="utf-8"))
    primary_recorded = {int(cell["L"]): cell for cell in p1488["primary_cells"]}

    target_cells = []
    setups = {}
    contexts = {}
    for fixture in PRIMARY_FIXTURES:
        L = int(fixture["L"])
        context = p1486.build_context(fixture)
        setup = setup_extension(context)
        contexts[L] = context
        setups[L] = setup
        target_base, target_source = p1486.planted_target(context)
        target_cells.append(
            target_cell(
                context,
                setup,
                target_base,
                target_source,
                primary_recorded[L],
                f"primary_L{L}",
            )
        )

    prospective_recorded = {int(cell["nonce"]): cell for cell in p1488["prospective_L8_targets"]}
    for nonce in range(8):
        target_base, target_source = prospective_target(contexts[8], nonce)
        target_cells.append(
            target_cell(
                contexts[8],
                setups[8],
                target_base,
                target_source,
                prospective_recorded[nonce],
                f"prospective_L8_nonce{nonce}",
            )
        )

    L8_panel = [cell for cell in target_cells if int(cell["L"]) == 8]
    combined = combined_L8(L8_panel, int(contexts[8]["fixture"]["order"]))
    all_frobenius = all(
        setup["frobenius_rational_exact"] and setup["frobenius_nonrational_negation_exact"]
        for setup in setups.values()
    )
    all_cancel = all(cell["all_nonrational_subtotals_zero"] for cell in target_cells)
    all_rows_replay = all(cell["planted_positive_control_present"] for cell in target_cells)
    any_nonrational = any(
        any(int(key) > 0 and value > 0 for key, value in cell["nonrational_endpoint_histogram"].items())
        for cell in target_cells
    )
    asymptotic_cells = [cell for cell in target_cells if int(cell["L"]) >= 8]
    asymptotic_rows_all_planted_equivalent = all(
        cell["all_rows_planted_equivalent"] and cell["non_planted_rational_row_count"] == 0
        for cell in asymptotic_cells
    )
    status = (
        "RESTRICTED_THEOREM_P1489_EXTENSION_ENDPOINTS_CANCEL_TO_PLANTED_RANK_ONE_ROWS"
        if all_frobenius and all_cancel and asymptotic_rows_all_planted_equivalent
        else "NEGATIVE_RESULT_P1489_RATIONAL_DESCENT_ROWS_RANK_DEFICIENT_OR_INVALID"
    )
    payload = {
        "boundary": {
            "candidate_vs_verified": "Frobenius cancellation and rational rows are exact, but all targets are source-planted controls.",
            "closed": "Treating nonrational quadratic lifts as independent factor-log columns.",
            "not_closed": "A public non-planted rational source generator over a different quotient or factor base.",
            "pollard_rho": "Quotient scan exponent is five and no complete relation/rank/descent pipeline beats rho.",
        },
        "combined_L8_panel": combined,
        "frozen_files": frozen,
        "gates": {
            "all_frobenius_actions_exact": all_frobenius,
            "all_nonrational_subtotals_cancel": all_cancel,
            "all_planted_controls_replay": all_rows_replay,
            "all_L8_L16_rows_planted_equivalent": asymptotic_rows_all_planted_equivalent,
            "any_witness_uses_nonrational_endpoints": any_nonrational,
            "combined_L8_full_factor_rank_is_planted_target_diversity_only": combined["full_factor_rank"]
            and asymptotic_rows_all_planted_equivalent,
            "complete_nonplanted_relation_backend": False,
            "public_source_generator_below_L_three_halves": False,
            "rational_descent_relation_signal": False,
        },
        "next_action": (
            "Do not use extension-only lifts as factor columns. If continuing this lane, freeze the rational-row incidence profiles and build a non-planted public source generator on the liftable-x deck; otherwise return to a different factor base."
        ),
        "schema": SCHEMA,
        "status": status,
        "target_cells": [strip_internal(cell) for cell in target_cells],
    }
    write_atomic(OUT, (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    write_atomic(NOTE, render_note(payload).encode("utf-8"))
    print(json.dumps({
        "status": status,
        "combined_L8_panel": combined,
        "targets": [
            {
                "target_id": cell["target_id"],
                "orbits": cell["orbit_count"],
                "rows": cell["deduplicated_rational_row_count"],
                "factor_rank": cell["factor_rank"],
                "factor_columns": cell["factor_column_count"],
                "nonrational_histogram": cell["nonrational_endpoint_histogram"],
            }
            for cell in target_cells
        ],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
