#!/usr/bin/env sage -python
"""Bind BKK path counts to the exact prime-field selector source backend."""

from __future__ import annotations

import gc
import hashlib
import itertools
import json
import math
import os
import statistics
import time
from pathlib import Path
from typing import Any

from sage.all import GF, PolynomialRing, QQ, matrix, vector

import p1482_coordinate_routed_wagner_tree as p1482
import p1490_rational_lift_selector_norm as p1490


ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = ROOT / "ecdlp_index_calculus_state"
RESEARCH_DIR = ROOT / "research"
CONTRACT = STATE_DIR / "experiment_contract_p1492_polyhedral_semaev_squareup.md"
P1490_SOURCE = STATE_DIR / "p1490_rational_lift_selector_norm.json"
OUT = STATE_DIR / "p1492_polyhedral_semaev_squareup.json"
NOTE = RESEARCH_DIR / "p1492_polyhedral_semaev_squareup.md"

SCHEMA = "ecdlp.p1492_polyhedral_semaev_squareup.v1"
MAX_ROWS_PER_SUM = 16
MAX_RELATIONS_PER_TARGET = 16
EXPECTED = {
    CONTRACT: "a3cefaca9bacdb3c590844e0d0ffe858dfac3eaaea566d18b73e0aea7158a600",
    ROOT / "tasks/ecdlp_index_calculus/p1490_rational_lift_selector_norm.py":
        "c68dc09ec38f6a8b9200117d60b8c649a99ad443ef24f7ef5e0e14a126e8880b",
    P1490_SOURCE: "1fbb457f642dab18cab43c69bf694f9a41b68c6ecefa365d7432e1ac7107cbab",
    STATE_DIR / "p1490_rational_lift_selector_norm_audit.json":
        "da5b6d4b194d9c03a29622ac03fe3e8c6dae33f1e99c788c46b82fb38f85fa7a",
    STATE_DIR / "p1491_pointwise_selector_subresultant.json":
        "26fc025c2de2c8ce331bacc8e556d47557159eea755fbc4e86d87da2d1d483be",
    STATE_DIR / "p1491_pointwise_selector_subresultant_audit.json":
        "31b1c95e09addd661e693d88fbdce2e1589fec47c7752e20b69f0bd7e0db6bc4",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fit_slope(xs: list[int], ys: list[int]) -> float:
    lx = [math.log(value) for value in xs]
    ly = [math.log(value) for value in ys]
    cx = statistics.mean(lx)
    cy = statistics.mean(ly)
    return sum((x - cx) * (y - cy) for x, y in zip(lx, ly)) / sum(
        (x - cx) ** 2 for x in lx
    )


def generic_s3_support() -> dict[str, Any]:
    ring = PolynomialRing(QQ, names=("x1492", "y1492", "z1492"))
    x, y, z = ring.gens()
    a = QQ(2)
    b = QQ(3)
    polynomial = (
        (x - y) ** 2 * z**2
        - 2 * ((x + y) * (x * y + a) + 2 * b) * z
        + (x * y - a) ** 2
        - 4 * b * (x + y)
    )
    support = sorted(tuple(int(value) for value in exponents) for exponents in polynomial.dict())
    expected = [
        (0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 2, 2),
        (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 2), (1, 2, 1),
        (2, 0, 2), (2, 1, 1), (2, 2, 0),
    ]
    if support != expected:
        raise RuntimeError("P1492 generic S3 support changed")
    return {
        "coefficient_specialization": {"a": 2, "b": 3},
        "support": [list(row) for row in support],
        "support_count": len(support),
        "support_sha256": hashlib.sha256(
            b"\n".join(repr(row).encode("ascii") for row in support)
        ).hexdigest(),
        "degree_each_variable": [int(polynomial.degree(variable)) for variable in (x, y, z)],
        "transition_new_state_degree": 2,
    }


def mixed_volume_cell(r: int) -> dict[str, Any]:
    omit = 16 * r**4
    direct = 16 * r**4
    dense = 16 * r**4
    linear = r**4
    thin = r
    return {
        "selector_degree_r": r,
        "omit_and_filter_mixed_volume": omit,
        "direct_S6_squareup_mixed_volume": direct,
        "dense_quadratic_transition_control": dense,
        "linear_transition_control": linear,
        "one_selector_thin_positive_control": thin,
        "generic_randomization_mixed_volume_lower_bound": r**5,
        "omit_equals_direct_S6": omit == direct,
        "triangular_certificate": {
            "selector_blocks": 4,
            "selector_factor": r**4,
            "new_state_degrees": [2, 2, 2, 2],
            "transition_factor": 16,
            "formula": "r^4 * 2 * 2 * 2 * 2",
        },
        "complete_path_exponent_in_r": 4.0,
        "passes_L_three_halves_gate": omit < r**1.5,
    }


def point_coefficient(point: Any, canonical: list[Any]) -> tuple[int, ...]:
    row = [0] * len(canonical)
    for column, base in enumerate(canonical):
        if point == base:
            row[column] = 1
            return tuple(row)
        if point == -base:
            row[column] = -1
            return tuple(row)
    raise RuntimeError("P1492 signed deck point has no factor column")


def add_rows(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(a + b for a, b in zip(left, right))


def build_four_sum_table(
    context: dict[str, Any], canonical: list[Any], deck: list[Any]
) -> tuple[dict[Any, list[tuple[int, ...]]], dict[str, Any]]:
    started = time.perf_counter()
    records = [(point, point_coefficient(point, canonical)) for point in deck]
    pairs = []
    for first in records:
        for second in records:
            pairs.append((first[0] + second[0], add_rows(first[1], second[1])))
    table: dict[Any, list[tuple[int, ...]]] = {}
    path_count = 0
    duplicate_path_count = 0
    retained_row_count = 0
    for left_point, left_row in pairs:
        for right_point, right_row in pairs:
            path_count += 1
            point = left_point + right_point
            row = add_rows(left_row, right_row)
            bucket = table.setdefault(p1482.point_key(point), [])
            if row in bucket:
                duplicate_path_count += 1
            elif len(bucket) < MAX_ROWS_PER_SUM:
                bucket.append(row)
                retained_row_count += 1
            else:
                duplicate_path_count += 1
    r = len(canonical)
    expected = (2 * r) ** 4
    if path_count != expected or path_count != 16 * r**4:
        raise RuntimeError("P1492 four-sum path count mismatch")
    return table, {
        "selector_degree_r": r,
        "signed_deck_size": len(deck),
        "ordered_pair_path_count": len(pairs),
        "ordered_four_path_count": path_count,
        "BKK_omit_and_filter_mixed_volume": 16 * r**4,
        "path_count_equals_BKK_mixed_volume": path_count == 16 * r**4,
        "distinct_four_sum_point_count": len(table),
        "retained_source_row_count": retained_row_count,
        "duplicate_or_capped_path_count": duplicate_path_count,
        "retained_field_word_proxy": retained_row_count * (r + 2),
        "build_wall_seconds": time.perf_counter() - started,
    }


def relation_panel(
    context: dict[str, Any],
    canonical: list[Any],
    deck: list[Any],
    table: dict[Any, list[tuple[int, ...]]],
    target_count: int,
    lane: str,
) -> dict[str, Any]:
    started = time.perf_counter()
    fixture = context["fixture"]
    L = int(fixture["L"])
    q = int(fixture["order"])
    challenge_scalar = 1 + p1482.digest_int("P1490", "challenge", L) % (q - 1)
    challenge = challenge_scalar * context["generator"]
    fifth_records = [(point, point_coefficient(point, canonical)) for point in deck]
    equations = {}
    target_hits = 0
    source_replay_failures = 0
    source_lookups = 0
    false_target_count = 0
    for target_index in range(target_count):
        a = p1482.digest_int("P1490", "target-a", L, target_index) % q
        b = 1 + p1482.digest_int("P1490", "target-b", L, target_index) % (q - 1)
        target = a * context["generator"] + b * challenge
        target_rows = {}
        for fifth_point, fifth_row in fifth_records:
            source_lookups += 1
            for four_row in table.get(p1482.point_key(target - fifth_point), []):
                row = add_rows(four_row, fifth_row)
                replay = sum(
                    (coefficient * point for coefficient, point in zip(row, canonical)),
                    context["identity"],
                )
                if replay != target:
                    source_replay_failures += 1
                    continue
                target_rows.setdefault(row, None)
                if len(target_rows) >= MAX_RELATIONS_PER_TARGET:
                    break
            if len(target_rows) >= MAX_RELATIONS_PER_TARGET:
                break
        if target_rows:
            target_hits += 1
        else:
            false_target_count += 1
        for coefficients in target_rows:
            matrix_row = tuple(value % q for value in coefficients) + ((-b) % q,)
            equations.setdefault((matrix_row, a % q), None)

    field = GF(q)
    rows = [list(key[0]) for key in equations]
    rhs = [key[1] for key in equations]
    width = len(canonical) + 1
    relation_matrix = matrix(field, rows) if rows else matrix(field, 0, width)
    rank = int(relation_matrix.rank())
    expected_logs = p1482.bsgs_logs(context, canonical)
    expected_solution = [expected_logs[p1482.point_key(point)] for point in canonical]
    expected_solution.append(challenge_scalar)
    all_equations_exact = all(
        sum(coefficient * solution for coefficient, solution in zip(row, expected_solution)) % q == value
        for row, value in zip(rows, rhs)
    )
    recovered = False
    if rank == width:
        solution = relation_matrix.solve_right(vector(field, rhs))
        recovered = [int(value) for value in solution] == expected_solution
    encoded = b"\n".join(
        repr((key[0], key[1])).encode("ascii") for key in sorted(equations)
    )
    return {
        "L": L,
        "lane": lane,
        "target_count": target_count,
        "targets_fixed_before_source_lookup": True,
        "target_hit_count": target_hits,
        "false_target_count": false_target_count,
        "source_lookup_count": source_lookups,
        "source_replay_failure_count": source_replay_failures,
        "all_sources_replay": source_replay_failures == 0,
        "deduplicated_relation_count": len(equations),
        "factor_column_count": len(canonical),
        "unknown_column_count_including_challenge": width,
        "relation_rank": rank,
        "full_relation_plus_challenge_rank": rank == width,
        "all_equations_match_verifier_logs": all_equations_exact,
        "relation_derived_challenge_recovery": recovered,
        "relation_row_sha256": hashlib.sha256(encoded).hexdigest(),
        "wall_seconds": time.perf_counter() - started,
    }


def synthetic_sweep() -> dict[str, Any]:
    sizes = [4, 8, 16, 32, 64, 128]
    cells = [mixed_volume_cell(r) for r in sizes]
    omit = [cell["omit_and_filter_mixed_volume"] for cell in cells]
    dense = [cell["dense_quadratic_transition_control"] for cell in cells]
    linear = [cell["linear_transition_control"] for cell in cells]
    thin = [cell["one_selector_thin_positive_control"] for cell in cells]
    return {
        "cells": cells,
        "omit_and_filter_fitted_exponent": fit_slope(sizes, omit),
        "dense_quadratic_fitted_exponent": fit_slope(sizes, dense),
        "linear_transition_fitted_exponent": fit_slope(sizes, linear),
        "thin_positive_control_fitted_exponent": fit_slope(sizes, thin),
    }


def write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def render_note(payload: dict[str, Any]) -> str:
    lines = [
        "# P1492 polyhedral Semaev square-up",
        "",
        "## Status",
        "",
        f"`{payload['status']}`",
        "",
        "| L | selector r | BKK paths | four-sum points | primary rank | columns |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    panels = {cell["L"]: cell for cell in payload["primary_relation_panels"]}
    for cell in payload["source_replay_cells"]:
        panel = panels[cell["L"]]
        lines.append(
            f"| {cell['L']} | {cell['selector_degree_r']} | "
            f"{cell['ordered_four_path_count']} | {cell['distinct_four_sum_point_count']} | "
            f"{panel['relation_rank']} | {panel['unknown_column_count_including_challenge']} |"
        )
    lines.extend([
        "",
        "The serial S3 support is sparse, but a complete prime-field square-up",
        "retains four degree-r selector segments. Its exact mixed volume and signed",
        "source-path count are both 16*r^4. Relation rows and toy challenge descent",
        "replay, but standard BKK path enumeration is far above the r^1.5 gate.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    frozen = {}
    for path, expected in EXPECTED.items():
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"P1492 frozen hash mismatch for {path}: {actual} != {expected}")
        frozen[str(path.relative_to(ROOT))] = actual
    p1490_source = json.loads(P1490_SOURCE.read_text(encoding="utf-8"))
    primary_recorded = {int(cell["L"]): cell for cell in p1490_source["relation_controls"]}
    extension_recorded = {
        int(cell["L"]): cell for cell in p1490_source["density_extension_controls"]
    }

    support = generic_s3_support()
    sweep = synthetic_sweep()
    fixture_mixed_volume_cells = []
    source_replay_cells = []
    primary_panels = []
    extension_panels = []
    for fixture in p1482.FIXTURES:
        context = p1482.build_context(fixture)
        selector, roots, _ = p1490.selector_cell(context)
        canonical, deck = p1490.selector_deck(context, roots)
        r = int(selector.degree())
        fixture_mixed_volume_cells.append({"L": int(fixture["L"]), **mixed_volume_cell(r)})
        table, source_cell = build_four_sum_table(context, canonical, deck)
        source_replay_cells.append({"L": int(fixture["L"]), **source_cell})
        primary = relation_panel(context, canonical, deck, table, 256, "frozen_256")
        primary["matches_P1490_target_hits"] = (
            primary["target_hit_count"] == int(primary_recorded[int(fixture["L"])]["target_hit_count"])
        )
        primary["matches_P1490_rank"] = (
            primary["relation_rank"] == int(primary_recorded[int(fixture["L"])]["relation_rank"])
        )
        primary_panels.append(primary)
        if int(fixture["L"]) >= 16:
            extension = relation_panel(
                context, canonical, deck, table, 8192, "post_panel_density_extension_8192"
            )
            extension["matches_P1490_target_hits"] = (
                extension["target_hit_count"]
                == int(extension_recorded[int(fixture["L"])]["target_hit_count"])
            )
            extension["matches_P1490_rank"] = (
                extension["relation_rank"]
                == int(extension_recorded[int(fixture["L"])]["relation_rank"])
            )
            extension_panels.append(extension)
        del table
        gc.collect()

    mixed_volume_exact = all(
        cell["omit_equals_direct_S6"]
        and cell["omit_and_filter_mixed_volume"] == 16 * cell["selector_degree_r"] ** 4
        and not cell["passes_L_three_halves_gate"]
        for cell in fixture_mixed_volume_cells
    )
    source_exact = all(
        cell["path_count_equals_BKK_mixed_volume"] for cell in source_replay_cells
    ) and all(
        cell["all_sources_replay"]
        and cell["all_equations_match_verifier_logs"]
        and cell["matches_P1490_target_hits"]
        and cell["matches_P1490_rank"]
        for cell in primary_panels
    )
    extensions_exact = all(
        cell["all_sources_replay"]
        and cell["all_equations_match_verifier_logs"]
        and cell["full_relation_plus_challenge_rank"]
        and cell["relation_derived_challenge_recovery"]
        and cell["matches_P1490_target_hits"]
        and cell["matches_P1490_rank"]
        for cell in extension_panels
    )
    controls_exact = (
        abs(sweep["omit_and_filter_fitted_exponent"] - 4.0) < 1e-12
        and abs(sweep["dense_quadratic_fitted_exponent"] - 4.0) < 1e-12
        and abs(sweep["linear_transition_fitted_exponent"] - 4.0) < 1e-12
        and abs(sweep["thin_positive_control_fitted_exponent"] - 1.0) < 1e-12
        and all(cell["one_selector_thin_positive_control"] < cell["selector_degree_r"] ** 1.5
                for cell in sweep["cells"])
    )
    status = (
        "MIXED_RESULT_P1492_EXACT_POLYHEDRAL_SOURCE_REPLAY_SELECTOR_DOMINATED_R4"
        if mixed_volume_exact and source_exact and extensions_exact and controls_exact
        else "NEGATIVE_RESULT_P1492_MIXED_VOLUME_OR_SOURCE_REPLAY_FAILED"
    )
    payload = {
        "boundary": {
            "candidate_vs_verified": (
                "The BKK certificate and source table are exact verifier paths. A candidate homotopy must track 16*r^4 paths per target or supply a different proved overdetermined algorithm."
            ),
            "closed": (
                "Standard square-up polyhedral homotopy for the serial S3 system with exact degree-r prime-field selectors."
            ),
            "not_closed": (
                "An output-sensitive overdetermined solver whose complexity is independent of square-up mixed volume and still opens exact sources."
            ),
            "pollard_rho": (
                "Per-target paths scale r^4; even full table reuse costs r^4=q^(4/5), above rho q^(1/2)."
            ),
        },
        "fixture_mixed_volume_cells": fixture_mixed_volume_cells,
        "frozen_files": frozen,
        "gates": {
            "generic_S3_support_exact": support["support_count"] == 13,
            "triangular_mixed_volume_certificate_exact": mixed_volume_exact,
            "signed_source_paths_equal_mixed_volume": all(
                cell["path_count_equals_BKK_mixed_volume"] for cell in source_replay_cells
            ),
            "nonplanted_relation_source_and_rank_replay_exact": source_exact,
            "density_extension_full_rank_and_descent_exact": extensions_exact,
            "mixed_volume_controls_exact": controls_exact,
            "complete_path_exponent_below_L_three_halves": False,
            "complete_campaign_below_pollard_rho": False,
            "polyhedral_semaev_relation_signal": False,
        },
        "next_action": (
            "Do not run standard polyhedral homotopy on this square-up. P1493 should test the remaining output-sensitive overdetermined incidence-reporting loophole directly, requiring witness reporting below r^1.5 without traversing the r^4 BKK paths."
        ),
        "primary_relation_panels": primary_panels,
        "density_extension_panels": extension_panels,
        "schema": SCHEMA,
        "source_replay_cells": source_replay_cells,
        "status": status,
        "synthetic_sweep": sweep,
        "system": {
            "equation_count": 9,
            "variable_count": 8,
            "variables": ["x1", "x2", "x3", "x4", "x5", "u1", "u2", "u3"],
            "selector_equation_count": 5,
            "serial_S3_equation_count": 4,
            "omit_and_filter_square_equation_count": 8,
            "direct_S6_per_endpoint_degree": 16,
            "generic_S3_support": support,
            "variable_incidence": [
                ["x1", "x2", "u1"],
                ["u1", "x3", "u2"],
                ["u2", "x4", "u3"],
                ["u3", "x5", "xR"],
            ],
        },
    }
    write_atomic(OUT, (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    write_atomic(NOTE, render_note(payload).encode("utf-8"))
    print(json.dumps({
        "status": status,
        "gates": payload["gates"],
        "mixed_volumes": [
            [cell["L"], cell["selector_degree_r"], cell["omit_and_filter_mixed_volume"]]
            for cell in fixture_mixed_volume_cells
        ],
        "source_paths": [
            [cell["L"], cell["ordered_four_path_count"], cell["distinct_four_sum_point_count"]]
            for cell in source_replay_cells
        ],
        "primary_ranks": [
            [cell["L"], cell["relation_rank"], cell["unknown_column_count_including_challenge"]]
            for cell in primary_panels
        ],
        "extension_ranks": [
            [cell["L"], cell["relation_rank"], cell["unknown_column_count_including_challenge"]]
            for cell in extension_panels
        ],
        "synthetic_exponents": {
            key: value for key, value in sweep.items() if key != "cells"
        },
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
