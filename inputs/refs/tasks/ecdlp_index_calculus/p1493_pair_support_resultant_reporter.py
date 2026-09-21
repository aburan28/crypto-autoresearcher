#!/usr/bin/env sage -python
"""Test an exact algebraic reporter for pair-support translated products."""

from __future__ import annotations

import gc
import hashlib
import json
import math
import os
import statistics
import time
from pathlib import Path
from typing import Any

from sage.all import GF, PolynomialRing, matrix, vector

import p1482_coordinate_routed_wagner_tree as p1482
import p1490_rational_lift_selector_norm as p1490


ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = ROOT / "ecdlp_index_calculus_state"
RESEARCH_DIR = ROOT / "research"
CONTRACT = STATE_DIR / "experiment_contract_p1493_pair_support_resultant_reporter.md"
P1490_SOURCE = STATE_DIR / "p1490_rational_lift_selector_norm.json"
P1492_SOURCE = STATE_DIR / "p1492_polyhedral_semaev_squareup.json"
OUT = STATE_DIR / "p1493_pair_support_resultant_reporter.json"
NOTE = RESEARCH_DIR / "p1493_pair_support_resultant_reporter.md"

SCHEMA = "ecdlp.p1493_pair_support_resultant_reporter.v1"
PUBLIC_TARGET_COUNT = 256
MAX_RELATIONS_PER_TARGET = 16
SYNTHETIC_SIZES = [4, 8, 16, 32, 64, 128]
EXPECTED = {
    CONTRACT: "146ef1e52bd4f6e38b0a3b3ba969aadb56a2d72730a3402ab6f8362f3928837b",
    ROOT / "tasks/ecdlp_index_calculus/p1490_rational_lift_selector_norm.py":
        "c68dc09ec38f6a8b9200117d60b8c649a99ad443ef24f7ef5e0e14a126e8880b",
    P1490_SOURCE: "1fbb457f642dab18cab43c69bf694f9a41b68c6ecefa365d7432e1ac7107cbab",
    STATE_DIR / "p1490_rational_lift_selector_norm_audit.json":
        "da5b6d4b194d9c03a29622ac03fe3e8c6dae33f1e99c788c46b82fb38f85fa7a",
    STATE_DIR / "p1491_pointwise_selector_subresultant.json":
        "26fc025c2de2c8ce331bacc8e556d47557159eea755fbc4e86d87da2d1d483be",
    STATE_DIR / "p1491_pointwise_selector_subresultant_audit.json":
        "31b1c95e09addd661e693d88fbdce2e1589fec47c7752e20b69f0bd7e0db6bc4",
    P1492_SOURCE: "01240d8fb3ea1d0b53638daeca2ff7f7b5b9288e5bb47d3a564b4257304f4dc9",
    STATE_DIR / "p1492_polyhedral_semaev_squareup_audit.json":
        "5c9747b1cd88527a1f80d4d1abdb4b207eeef3bc7bd0952b4216594ca93f2c48",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_rows(rows: list[tuple[int, ...]]) -> str:
    return hashlib.sha256(
        b"\n".join(repr(row).encode("ascii") for row in sorted(set(rows)))
    ).hexdigest()


def digest_integers(values: list[int]) -> str:
    return hashlib.sha256(
        b"|".join(str(value).encode("ascii") for value in sorted(values))
    ).hexdigest()


def fit_slope(xs: list[int], ys: list[int]) -> float:
    lx = [math.log(value) for value in xs]
    ly = [math.log(value) for value in ys]
    cx = statistics.mean(lx)
    cy = statistics.mean(ly)
    return sum((x - cx) * (y - cy) for x, y in zip(lx, ly)) / sum(
        (x - cx) ** 2 for x in lx
    )


def point_coefficient(point: Any, canonical: list[Any]) -> tuple[int, ...]:
    row = [0] * len(canonical)
    for column, base in enumerate(canonical):
        if point == base:
            row[column] = 1
            return tuple(row)
        if point == -base:
            row[column] = -1
            return tuple(row)
    raise RuntimeError("P1493 signed deck point has no factor column")


def add_rows(*rows: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sum(values) for values in zip(*rows))


def pair_support(
    context: dict[str, Any], canonical: list[Any], deck: list[Any]
) -> tuple[Any, dict[Any, dict[str, Any]], dict[str, Any]]:
    started = time.perf_counter()
    records = [(point, point_coefficient(point, canonical)) for point in deck]
    support: dict[Any, dict[str, Any]] = {}
    path_count = 0
    duplicate_source_count = 0
    for first_point, first_row in records:
        for second_point, second_row in records:
            path_count += 1
            point = first_point + second_point
            key = p1482.point_key(point)
            bucket = support.setdefault(key, {"point": point, "rows": []})
            row = add_rows(first_row, second_row)
            if row in bucket["rows"]:
                duplicate_source_count += 1
            else:
                bucket["rows"].append(row)

    nonzero_points = [bucket["point"] for bucket in support.values() if not bucket["point"].is_zero()]
    x_roots = sorted({int(point[0]) for point in nonzero_points})
    ring = PolynomialRing(context["field"], f"X1493_support_{context['fixture']['L']}")
    X = ring.gen()
    polynomial = ring.one()
    for root in x_roots:
        polynomial *= X - context["field"](root)
    polynomial = polynomial.monic()
    recovered_roots = sorted(int(root) for root in polynomial.roots(multiplicities=False))
    if recovered_roots != x_roots:
        raise RuntimeError("P1493 pair-support polynomial root mismatch")

    r = len(canonical)
    retained_rows = [row for bucket in support.values() for row in bucket["rows"]]
    cell = {
        "L": int(context["fixture"]["L"]),
        "selector_degree_r": r,
        "signed_deck_size": len(deck),
        "ordered_pair_path_count": path_count,
        "expected_ordered_pair_path_count_4r2": 4 * r**2,
        "distinct_full_point_count_including_infinity": len(support),
        "expected_distinct_full_point_count_2r2_plus_1": 2 * r**2 + 1,
        "distinct_nonzero_x_count": len(x_roots),
        "expected_distinct_nonzero_x_count_r2": r**2,
        "G2_degree": int(polynomial.degree()),
        "G2_coefficient_count": len(list(polynomial)),
        "G2_nonzero_coefficient_count": sum(coefficient != 0 for coefficient in polynomial),
        "G2_coefficient_sha256": p1490.polynomial_hash(polynomial),
        "G2_root_sha256": digest_integers(x_roots),
        "retained_pair_source_row_count": len(retained_rows),
        "pair_source_row_sha256": digest_rows(retained_rows),
        "duplicate_ordered_source_count": duplicate_source_count,
        "retained_field_word_proxy": len(retained_rows) * (r + 2),
        "construction_path_exponent_in_r": 2.0,
        "build_wall_seconds": time.perf_counter() - started,
    }
    return polynomial, support, cell


def polynomial_metrics(polynomial: Any) -> dict[str, Any]:
    coefficients = list(polynomial)
    return {
        "degree": int(polynomial.degree()),
        "coefficient_count": len(coefficients),
        "nonzero_coefficient_count": sum(coefficient != 0 for coefficient in coefficients),
        "coefficient_sha256": p1490.polynomial_hash(polynomial),
    }


def quadratic_resultant(selector: Any, A: Any, B: Any, C: Any) -> tuple[Any, dict[str, int]]:
    """Return Res_Y(selector(Y), A*Y^2+B*Y+C) without a Sylvester matrix."""
    degree = int(selector.degree())
    if degree < 1 or A == 0:
        raise RuntimeError("P1493 quadratic resultant received a degenerate input")
    powers = [A.parent().one()]
    for _ in range(degree):
        powers.append(powers[-1] * A)

    coefficients = list(selector)
    remainder_y = A.parent().zero()
    remainder_constant = coefficients[0] * powers[degree - 1]
    U = A.parent().one()
    V = A.parent().zero()
    for exponent in range(1, degree + 1):
        if exponent > 1:
            U, V = A * V - B * U, -C * U
        scale = powers[degree - exponent]
        remainder_y += coefficients[exponent] * scale * U
        remainder_constant += coefficients[exponent] * scale * V

    numerator = (
        A * remainder_constant**2
        - B * remainder_constant * remainder_y
        + C * remainder_y**2
    )
    denominator = powers[degree - 1]
    quotient, remainder = numerator.quo_rem(denominator)
    if remainder != 0:
        raise RuntimeError("P1493 quadratic resultant exact division failed")
    return quotient, {
        "selector_degree": degree,
        "quadratic_recurrence_steps": degree,
        "exact_division_remainder_degree": -1,
    }


def exact_source_opening(
    context: dict[str, Any],
    canonical: list[Any],
    support: dict[Any, dict[str, Any]],
    query: Any,
    roots: list[int],
) -> tuple[list[dict[str, Any]], list[tuple[int, ...]], list[tuple[int, ...]], int]:
    root_set = set(roots)
    root_witnesses: dict[int, dict[str, Any]] = {}
    algebraic_rows: set[tuple[int, ...]] = set()
    infinity_rows: set[tuple[int, ...]] = set()
    replay_failures = 0

    for bucket in support.values():
        left = bucket["point"]
        if left.is_zero() or int(left[0]) not in root_set:
            continue
        right_bucket = support.get(p1482.point_key(query - left))
        if right_bucket is None or right_bucket["point"].is_zero():
            continue
        root = int(left[0])
        for left_row in bucket["rows"]:
            for right_row in right_bucket["rows"]:
                row = add_rows(left_row, right_row)
                replay = sum(
                    (coefficient * point for coefficient, point in zip(row, canonical)),
                    context["identity"],
                )
                if replay != query:
                    replay_failures += 1
                    continue
                algebraic_rows.add(row)
                root_witnesses.setdefault(root, {
                    "root": root,
                    "left_pair_point": p1482.point_json(left),
                    "right_pair_point": p1482.point_json(right_bucket["point"]),
                    "left_pair_row": list(left_row),
                    "right_pair_row": list(right_row),
                    "four_endpoint_row": list(row),
                })

    infinity_bucket = support.get(("O",))
    query_bucket = support.get(p1482.point_key(query))
    if infinity_bucket is not None and query_bucket is not None:
        for left_row in infinity_bucket["rows"]:
            for right_row in query_bucket["rows"]:
                row = add_rows(left_row, right_row)
                replay = sum(
                    (coefficient * point for coefficient, point in zip(row, canonical)),
                    context["identity"],
                )
                if replay != query:
                    replay_failures += 1
                else:
                    infinity_rows.add(row)

    return (
        [root_witnesses[root] for root in sorted(root_witnesses)],
        sorted(algebraic_rows),
        sorted(infinity_rows),
        replay_failures,
    )


def algebraic_query(
    context: dict[str, Any],
    canonical: list[Any],
    G2: Any,
    support: dict[Any, dict[str, Any]],
    query: Any,
    lane: str,
    index: int,
) -> dict[str, Any]:
    started = time.perf_counter()
    if query.is_zero():
        raise RuntimeError("P1493 query panel unexpectedly contains infinity")

    expected_roots = set()
    full_point_scan_count = 0
    for bucket in support.values():
        left = bucket["point"]
        if left.is_zero():
            continue
        full_point_scan_count += 1
        right_bucket = support.get(p1482.point_key(query - left))
        if right_bucket is not None and not right_bucket["point"].is_zero():
            expected_roots.add(int(left[0]))

    field = context["field"]
    xring = PolynomialRing(field, f"X1493_query_{context['fixture']['L']}_{lane}_{index}")
    X = xring.gen()
    yring = PolynomialRing(xring, f"Y1493_query_{context['fixture']['L']}_{lane}_{index}")
    Y = yring.gen()
    G2X = xring([field(coefficient) for coefficient in G2])
    a = xring(field(context["fixture"]["a"]))
    b = xring(field(context["fixture"]["b"]))
    qx = xring(field(query[0]))
    s3 = (
        (X - Y) ** 2 * qx**2
        - 2 * ((X + Y) * (X * Y + a) + 2 * b) * qx
        + (X * Y - a) ** 2
        - 4 * b * (X + Y)
    )
    if int(s3.degree(Y)) != 2:
        raise RuntimeError("P1493 S3 specialization is not quadratic in Y")
    resultant, recurrence = quadratic_resultant(G2X, xring(s3[2]), xring(s3[1]), xring(s3[0]))
    common = G2X.gcd(resultant).monic()
    roots = sorted(int(root) for root in common.roots(multiplicities=False))
    witnesses, source_rows, infinity_rows, replay_failures = exact_source_opening(
        context, canonical, support, query, roots
    )
    expected = sorted(expected_roots)
    all_source_rows = sorted(set(source_rows + infinity_rows))
    return {
        "lane": lane,
        "index": index,
        "query_point": p1482.point_json(query),
        "query_point_sha256": hashlib.sha256(repr(p1482.point_key(query)).encode("ascii")).hexdigest(),
        "G2_degree_M": int(G2.degree()),
        "resultant": polynomial_metrics(resultant),
        "quadratic_resultant_recurrence": recurrence,
        "gcd": polynomial_metrics(common),
        "reported_x_roots": roots,
        "reported_x_root_sha256": digest_integers(roots),
        "full_point_expected_x_roots": expected,
        "full_point_expected_x_root_sha256": digest_integers(expected),
        "root_false_negative_count": len(set(expected) - set(roots)),
        "root_false_positive_count": len(set(roots) - set(expected)),
        "root_witness_count": len(witnesses),
        "root_witnesses": witnesses,
        "algebraic_source_row_count": len(source_rows),
        "infinity_branch_source_row_count": len(infinity_rows),
        "all_source_row_count": len(all_source_rows),
        "all_source_row_sha256": digest_rows(all_source_rows),
        "source_replay_failure_count": replay_failures,
        "accepted": bool(all_source_rows),
        "candidate_path": {
            "uses_G2_coefficients_and_S3_quadratic_resultant_gcd": True,
            "uses_full_point_hash_scan": False,
            "soft_field_word_proxy": int(G2.degree()),
            "source_opening_is_output_sensitive": True,
        },
        "verifier_path": {
            "full_point_scan_count": full_point_scan_count,
            "uses_pair_support_hash": True,
        },
        "wall_seconds": time.perf_counter() - started,
    }


def query_panel(
    context: dict[str, Any],
    canonical: list[Any],
    deck: list[Any],
    G2: Any,
    support: dict[Any, dict[str, Any]],
) -> dict[str, Any]:
    fixture = context["fixture"]
    L = int(fixture["L"])
    q = int(fixture["order"])
    challenge_scalar = 1 + p1482.digest_int("P1490", "challenge", L) % (q - 1)
    challenge = challenge_scalar * context["generator"]
    queries: list[tuple[str, int, Any]] = []

    public_index = 0
    for target_index in range(2):
        a = p1482.digest_int("P1490", "target-a", L, target_index) % q
        b = 1 + p1482.digest_int("P1490", "target-b", L, target_index) % (q - 1)
        target = a * context["generator"] + b * challenge
        for fifth in deck:
            query = target - fifth
            if query.is_zero():
                raise RuntimeError("P1493 public query unexpectedly equals infinity")
            queries.append(("public_nonplanted", public_index, query))
            public_index += 1

    nonzero_support = [
        bucket["point"] for key, bucket in sorted(support.items(), key=lambda item: repr(item[0]))
        if not bucket["point"].is_zero()
    ]
    for index in range(16):
        left_index = p1482.digest_int("P1493", "positive-left", L, index) % len(nonzero_support)
        right_index = p1482.digest_int("P1493", "positive-right", L, index) % len(nonzero_support)
        query = nonzero_support[left_index] + nonzero_support[right_index]
        if query.is_zero():
            right_index = (right_index + 1) % len(nonzero_support)
            query = nonzero_support[left_index] + nonzero_support[right_index]
        if query.is_zero():
            raise RuntimeError("P1493 could not make a nonzero positive query")
        queries.append(("positive_control", index, query))

    for index in range(32):
        scalar = 1 + p1482.digest_int("P1493", "unrestricted", L, index) % (q - 1)
        queries.append(("unrestricted_fixed", index, scalar * context["generator"]))

    records = [
        algebraic_query(context, canonical, G2, support, query, lane, index)
        for lane, index, query in queries
    ]
    lanes = sorted({record["lane"] for record in records})
    return {
        "L": L,
        "query_count": len(records),
        "public_nonplanted_query_count": sum(row["lane"] == "public_nonplanted" for row in records),
        "positive_control_query_count": sum(row["lane"] == "positive_control" for row in records),
        "unrestricted_fixed_query_count": sum(row["lane"] == "unrestricted_fixed" for row in records),
        "accepted_query_count": sum(row["accepted"] for row in records),
        "false_query_count": sum(not row["accepted"] for row in records),
        "positive_control_failure_count": sum(
            not row["accepted"] for row in records if row["lane"] == "positive_control"
        ),
        "root_false_negative_count": sum(row["root_false_negative_count"] for row in records),
        "root_false_positive_count": sum(row["root_false_positive_count"] for row in records),
        "source_replay_failure_count": sum(row["source_replay_failure_count"] for row in records),
        "maximum_resultant_degree": max(row["resultant"]["degree"] for row in records),
        "maximum_gcd_degree": max(row["gcd"]["degree"] for row in records),
        "total_reported_root_count": sum(len(row["reported_x_roots"]) for row in records),
        "total_source_row_count": sum(row["all_source_row_count"] for row in records),
        "lane_accept_counts": {
            lane: sum(row["accepted"] for row in records if row["lane"] == lane)
            for lane in lanes
        },
        "records": records,
    }


def relation_panel(
    context: dict[str, Any],
    canonical: list[Any],
    deck: list[Any],
    support: dict[Any, dict[str, Any]],
) -> dict[str, Any]:
    started = time.perf_counter()
    fixture = context["fixture"]
    L = int(fixture["L"])
    q = int(fixture["order"])
    challenge_scalar = 1 + p1482.digest_int("P1490", "challenge", L) % (q - 1)
    challenge = challenge_scalar * context["generator"]
    fifth_records = [(point, point_coefficient(point, canonical)) for point in deck]
    pair_entries = list(support.values())
    equations: dict[tuple[tuple[int, ...], int], None] = {}
    target_hits = 0
    source_replay_failures = 0
    pair_point_probes = 0
    matched_pair_source_products = 0

    for target_index in range(PUBLIC_TARGET_COUNT):
        a = p1482.digest_int("P1490", "target-a", L, target_index) % q
        b = 1 + p1482.digest_int("P1490", "target-b", L, target_index) % (q - 1)
        target = a * context["generator"] + b * challenge
        target_rows: dict[tuple[int, ...], None] = {}
        for fifth, fifth_row in fifth_records:
            query = target - fifth
            for left_bucket in pair_entries:
                pair_point_probes += 1
                right_bucket = support.get(p1482.point_key(query - left_bucket["point"]))
                if right_bucket is None:
                    continue
                for left_row in left_bucket["rows"]:
                    for right_row in right_bucket["rows"]:
                        matched_pair_source_products += 1
                        row = add_rows(left_row, right_row, fifth_row)
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
                if len(target_rows) >= MAX_RELATIONS_PER_TARGET:
                    break
            if len(target_rows) >= MAX_RELATIONS_PER_TARGET:
                break
        if target_rows:
            target_hits += 1
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
        "lane": "frozen_256_full_point_reporter",
        "target_count": PUBLIC_TARGET_COUNT,
        "targets_fixed_before_source_search": True,
        "target_hit_count": target_hits,
        "false_target_count": PUBLIC_TARGET_COUNT - target_hits,
        "deduplicated_relation_count": len(equations),
        "factor_column_count": len(canonical),
        "unknown_column_count_including_challenge": width,
        "relation_rank": rank,
        "full_relation_plus_challenge_rank": rank == width,
        "all_sources_replay": source_replay_failures == 0,
        "source_replay_failure_count": source_replay_failures,
        "all_equations_match_verifier_logs": all_equations_exact,
        "relation_derived_challenge_recovery": recovered,
        "relation_row_sha256": hashlib.sha256(encoded).hexdigest(),
        "work": {
            "pair_point_probe_count": pair_point_probes,
            "matched_pair_source_product_count": matched_pair_source_products,
            "pair_support_precomputation_asymptotic": "Theta(r^2)",
            "full_point_verifier_per_supplied_Q_asymptotic": "Theta(r^2)",
            "full_point_verifier_per_target_asymptotic": "Theta(r^3)",
            "candidate_resultant_per_supplied_Q_asymptotic": "soft-O(r^2)",
        },
        "wall_seconds": time.perf_counter() - started,
    }


def synthetic_sweep() -> dict[str, Any]:
    cells = []
    for r in SYNTHETIC_SIZES:
        M = r**2
        cells.append({
            "selector_degree_r": r,
            "pair_support_degree_M": M,
            "pair_support_build_word_proxy": 4 * r**2,
            "supplied_Q_resultant_gcd_word_proxy": M,
            "one_target_product_algebra_word_traffic": 2 * r * M,
            "r_target_campaign_word_traffic": 2 * r**2 * M,
            "degree_r_thin_control_query_word_proxy": r,
            "random_degree_r2_control_query_word_proxy": r**2,
            "constant_degree_incidence_surface_membership_complete": False,
            "supplied_Q_passes_r_three_halves_gate": M < r**1.5,
            "target_passes_r_two_and_a_half_gate": 2 * r * M < r**2.5,
        })
    return {
        "sizes": SYNTHETIC_SIZES,
        "cells": cells,
        "pair_support_build_fitted_exponent": fit_slope(
            SYNTHETIC_SIZES, [cell["pair_support_build_word_proxy"] for cell in cells]
        ),
        "supplied_Q_resultant_gcd_fitted_exponent": fit_slope(
            SYNTHETIC_SIZES, [cell["supplied_Q_resultant_gcd_word_proxy"] for cell in cells]
        ),
        "one_target_batch_fitted_exponent": fit_slope(
            SYNTHETIC_SIZES, [cell["one_target_product_algebra_word_traffic"] for cell in cells]
        ),
        "r_target_campaign_fitted_exponent": fit_slope(
            SYNTHETIC_SIZES, [cell["r_target_campaign_word_traffic"] for cell in cells]
        ),
        "thin_positive_control_fitted_exponent": fit_slope(
            SYNTHETIC_SIZES, [cell["degree_r_thin_control_query_word_proxy"] for cell in cells]
        ),
        "random_degree_r2_control_fitted_exponent": fit_slope(
            SYNTHETIC_SIZES, [cell["random_degree_r2_control_query_word_proxy"] for cell in cells]
        ),
    }


def write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def render_note(payload: dict[str, Any]) -> str:
    panels = {cell["L"]: cell for cell in payload["primary_relation_panels"]}
    query_panels = {cell["L"]: cell for cell in payload["query_panels"]}
    lines = [
        "# P1493 pair-support resultant reporter",
        "",
        "## Status",
        "",
        f"`{payload['status']}`",
        "",
        "| L | r | deg G2 | queries | roots | primary rank | columns |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for cell in payload["pair_support_cells"]:
        panel = panels[cell["L"]]
        query = query_panels[cell["L"]]
        lines.append(
            f"| {cell['L']} | {cell['selector_degree_r']} | {cell['G2_degree']} | "
            f"{query['query_count']} | {query['total_reported_root_count']} | "
            f"{panel['relation_rank']} | {panel['unknown_column_count_including_challenge']} |"
        )
    lines.extend([
        "",
        "The resultant/gcd reporter is exact and opens signed four-endpoint",
        "sources, while the full-point five-term panel reproduces the frozen",
        "target-hit and rank boundary. Its exact membership polynomial has degree",
        "r^2, however, so supplied-Q work remains soft-O(r^2), target batching",
        "costs soft-O(r^3), and an r-row campaign costs soft-O(r^4). The shared",
        "translated-product representation therefore does not cross the r^1.5",
        "query gate or the rho-scale r^2.5 relation budget.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    frozen = {}
    for path, expected in EXPECTED.items():
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"P1493 frozen hash mismatch for {path}: {actual} != {expected}")
        frozen[str(path.relative_to(ROOT))] = actual

    p1490_source = json.loads(P1490_SOURCE.read_text(encoding="utf-8"))
    p1492_source = json.loads(P1492_SOURCE.read_text(encoding="utf-8"))
    p1490_primary = {int(cell["L"]): cell for cell in p1490_source["relation_controls"]}
    p1492_primary = {int(cell["L"]): cell for cell in p1492_source["primary_relation_panels"]}

    pair_cells = []
    query_panels = []
    relation_panels = []
    for fixture in p1482.FIXTURES:
        context = p1482.build_context(fixture)
        selector, roots, _ = p1490.selector_cell(context)
        canonical, deck = p1490.selector_deck(context, roots)
        G2, support, pair_cell = pair_support(context, canonical, deck)
        pair_cells.append(pair_cell)
        query_panels.append(query_panel(context, canonical, deck, G2, support))
        relation = relation_panel(context, canonical, deck, support)
        recorded_1490 = p1490_primary[int(fixture["L"])]
        recorded_1492 = p1492_primary[int(fixture["L"])]
        relation.update({
            "matches_P1490_target_hits": relation["target_hit_count"] == recorded_1490["target_hit_count"],
            "matches_P1490_rank": relation["relation_rank"] == recorded_1490["relation_rank"],
            "matches_P1492_target_hits": relation["target_hit_count"] == recorded_1492["target_hit_count"],
            "matches_P1492_rank": relation["relation_rank"] == recorded_1492["relation_rank"],
        })
        relation_panels.append(relation)
        del support, G2
        gc.collect()

    sweep = synthetic_sweep()
    pair_support_exact = all(
        cell["ordered_pair_path_count"] == cell["expected_ordered_pair_path_count_4r2"]
        and cell["distinct_full_point_count_including_infinity"]
        == cell["expected_distinct_full_point_count_2r2_plus_1"]
        and cell["distinct_nonzero_x_count"] == cell["expected_distinct_nonzero_x_count_r2"]
        and cell["G2_degree"] == cell["selector_degree_r"] ** 2
        for cell in pair_cells
    )
    algebraic_reporter_exact = all(
        cell["positive_control_failure_count"] == 0
        and cell["root_false_negative_count"] == 0
        and cell["root_false_positive_count"] == 0
        and cell["source_replay_failure_count"] == 0
        for cell in query_panels
    )
    relation_replay_exact = all(
        cell["all_sources_replay"]
        and cell["all_equations_match_verifier_logs"]
        and cell["matches_P1490_target_hits"]
        and cell["matches_P1490_rank"]
        and cell["matches_P1492_target_hits"]
        and cell["matches_P1492_rank"]
        for cell in relation_panels
    )
    controls_exact = (
        abs(sweep["pair_support_build_fitted_exponent"] - 2.0) < 1e-12
        and abs(sweep["supplied_Q_resultant_gcd_fitted_exponent"] - 2.0) < 1e-12
        and abs(sweep["one_target_batch_fitted_exponent"] - 3.0) < 1e-12
        and abs(sweep["r_target_campaign_fitted_exponent"] - 4.0) < 1e-12
        and abs(sweep["thin_positive_control_fitted_exponent"] - 1.0) < 1e-12
        and abs(sweep["random_degree_r2_control_fitted_exponent"] - 2.0) < 1e-12
        and all(not cell["constant_degree_incidence_surface_membership_complete"] for cell in sweep["cells"])
    )
    status = (
        "MIXED_RESULT_P1493_EXACT_PAIR_RESULTANT_REPORTER_DEGREE_R2_BATCH_R3"
        if pair_support_exact and algebraic_reporter_exact and relation_replay_exact and controls_exact
        else "NEGATIVE_RESULT_P1493_PAIR_RESULTANT_OR_SOURCE_REPORTER_FAILED"
    )
    payload = {
        "asymptotic_accounting": {
            "pair_support_build": "Theta(r^2)",
            "exact_membership_degree": "M=r^2",
            "supplied_Q_fast_resultant_and_gcd": "soft-O(M)=soft-O(r^2)",
            "one_target_r_complements_product_CRT_batch": "soft-O(M*r)=soft-O(r^3)",
            "r_target_relation_campaign": "soft-O(M*r^2)=soft-O(r^4)",
            "rho_scale_relation_budget": "r^2.5 under the frozen r=q^(1/5) calibration",
            "incidence_membership_degree": "r^2, not constant independently of r",
        },
        "boundary": {
            "candidate_vs_verified": (
                "The candidate path uses only G2 plus S3 resultant/gcd arithmetic. Full-point scans and hidden logs are verifier paths; every reported root opens to signed factor rows."
            ),
            "closed": (
                "The x-coordinate pair-support translated-product reporter G2=0 with ordinary fast resultant/gcd and product/CRT batching."
            ),
            "not_closed": (
                "A new coordinate feature whose exact pair-support description has degree below r^1.5 while retaining random-like five-sum supply."
            ),
            "incidence_applicability": (
                "S3 has fixed degree, but exact A2 membership has degree r^2. Fixed-degree partition/incidence bounds cannot be imported with constants independent of r; this is not a universal data-structure lower bound."
            ),
            "pollard_rho": (
                "The exact reporter costs r^2 per supplied Q, r^3 per target, and r^4 per r-row campaign, above the r^2.5 rho-scale relation budget."
            ),
        },
        "density_extension_controls": [
            {
                "L": int(cell["L"]),
                "lane": cell["lane"],
                "target_count": int(cell["target_count"]),
                "target_hit_count": int(cell["target_hit_count"]),
                "relation_rank": int(cell["relation_rank"]),
                "unknown_column_count_including_challenge": int(cell["unknown_column_count_including_challenge"]),
                "full_relation_plus_challenge_rank": bool(cell["full_relation_plus_challenge_rank"]),
                "relation_derived_challenge_recovery": bool(cell["relation_derived_challenge_recovery"]),
                "relation_row_sha256": cell["relation_row_sha256"],
                "imported_frozen_control_only": True,
                "verifier_source_table_used_as_candidate_advice": False,
            }
            for cell in p1492_source["density_extension_panels"]
        ],
        "frozen_files": frozen,
        "gates": {
            "pair_support_formulas_and_G2_exact": pair_support_exact,
            "algebraic_roots_signs_sources_and_replay_exact": algebraic_reporter_exact,
            "nonplanted_full_relation_source_and_rank_replay_exact": relation_replay_exact,
            "density_extension_full_rank_descent_control_imported": all(
                cell["full_relation_plus_challenge_rank"] and cell["relation_derived_challenge_recovery"]
                for cell in p1492_source["density_extension_panels"]
            ),
            "synthetic_exponent_controls_exact": controls_exact,
            "pair_support_build_at_most_r2": pair_support_exact,
            "worst_supplied_Q_query_exponent_strictly_below_r_three_halves": False,
            "complete_target_processing_below_r_two_and_a_half": False,
            "complete_campaign_below_pollard_rho": False,
            "pair_support_reporting_signal": False,
        },
        "next_action": (
            "Preserve G2 as an exact negative baseline. P1494 should search for a compressed pair feature Phi(A2) with exact membership degree below r^1.5 and preregister a collision/supply test before any resultant implementation; reject features that merely hide r^2 advice in fibers."
        ),
        "pair_support_cells": pair_cells,
        "primary_relation_panels": relation_panels,
        "query_panels": query_panels,
        "schema": SCHEMA,
        "status": status,
        "synthetic_sweep": sweep,
    }
    write_atomic(OUT, (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    write_atomic(NOTE, render_note(payload).encode("utf-8"))
    print(json.dumps({
        "status": status,
        "gates": payload["gates"],
        "pair_support": [
            [cell["L"], cell["selector_degree_r"], cell["G2_degree"], cell["distinct_full_point_count_including_infinity"]]
            for cell in pair_cells
        ],
        "queries": [
            [cell["L"], cell["query_count"], cell["accepted_query_count"], cell["total_reported_root_count"]]
            for cell in query_panels
        ],
        "primary_ranks": [
            [cell["L"], cell["relation_rank"], cell["unknown_column_count_including_challenge"]]
            for cell in relation_panels
        ],
        "synthetic_exponents": {
            key: value for key, value in sweep.items() if key not in {"sizes", "cells"}
        },
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
