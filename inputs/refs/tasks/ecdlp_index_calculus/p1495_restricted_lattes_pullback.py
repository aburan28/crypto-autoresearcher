#!/usr/bin/env sage -python
"""Test restricted rational correspondences and Lattes pullback costs."""

from __future__ import annotations

import hashlib
import json
import math
import os
import statistics
import time
from pathlib import Path
from typing import Any

from sage.all import PolynomialRing, is_prime

import p1482_coordinate_routed_wagner_tree as p1482
import p1490_rational_lift_selector_norm as p1490


ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = ROOT / "ecdlp_index_calculus_state"
RESEARCH_DIR = ROOT / "research"
CONTRACT = STATE_DIR / "experiment_contract_p1495_restricted_lattes_pullback.md"
P1493_SOURCE = STATE_DIR / "p1493_pair_support_resultant_reporter.json"
P1494_SOURCE = STATE_DIR / "p1494_translation_compatible_pair_feature.json"
OUT = STATE_DIR / "p1495_restricted_lattes_pullback.json"
NOTE = RESEARCH_DIR / "p1495_restricted_lattes_pullback.md"

SCHEMA = "ecdlp.p1495_restricted_lattes_pullback.v1"
SYNTHETIC_SIZES = [4, 8, 16, 32, 64, 128]
EXPECTED = {
    CONTRACT: "993b14e90a8592c73228a858c81ba9e6096a9f696398442532ace071088bbb39",
    ROOT / "tasks/ecdlp_index_calculus/p1490_rational_lift_selector_norm.py":
        "c68dc09ec38f6a8b9200117d60b8c649a99ad443ef24f7ef5e0e14a126e8880b",
    P1493_SOURCE: "cdfe2470ec5a9f231688b1d61d4bba5fb11dcb587982f892b21eee36b0e5ecf7",
    STATE_DIR / "p1493_pair_support_resultant_reporter_audit.json":
        "ab75dff4153657b55a12fd371fe56e0b029f984319d1a185c5a118274a179e49",
    P1494_SOURCE: "1a93e3b2ab3dc683acc9fcbce1689b466bd7470e4f759498c54b468569435510",
    STATE_DIR / "p1494_translation_compatible_pair_feature_audit.json":
        "44c5504f0079a9a442e568db5531debca3361c3dcae15b42ae5c88c5d557ee2e",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_items(items: list[Any]) -> str:
    return hashlib.sha256(
        b"\n".join(repr(item).encode("ascii") for item in sorted(items, key=repr))
    ).hexdigest()


def polynomial_hash(polynomial: Any) -> str:
    return hashlib.sha256(
        b"|".join(str(int(coefficient)).encode("ascii") for coefficient in polynomial)
    ).hexdigest()


def fit_slope(xs: list[int], ys: list[int]) -> float:
    lx = [math.log(value) for value in xs]
    ly = [math.log(value) for value in ys]
    cx = statistics.mean(lx)
    cy = statistics.mean(ly)
    return sum((x - cx) * (y - cy) for x, y in zip(lx, ly)) / sum(
        (x - cx) ** 2 for x in lx
    )


def add_rows(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(a + b for a, b in zip(left, right))


def point_row(point: Any, canonical: list[Any]) -> tuple[int, ...]:
    row = [0] * len(canonical)
    for column, base in enumerate(canonical):
        if point == base:
            row[column] = 1
            return tuple(row)
        if point == -base:
            row[column] = -1
            return tuple(row)
    raise RuntimeError("P1495 endpoint lacks a factor column")


def feature_order(L: int, r: int) -> int:
    return max(value for value in range(1, L + 1) if L % value == 0 and value <= r)


def pair_support(
    context: dict[str, Any], canonical: list[Any], deck: list[Any]
) -> tuple[dict[Any, dict[str, Any]], list[int], Any, dict[str, Any]]:
    records = [(point, point_row(point, canonical)) for point in deck]
    support: dict[Any, dict[str, Any]] = {}
    paths = 0
    for first_point, first_row in records:
        for second_point, second_row in records:
            paths += 1
            point = first_point + second_point
            bucket = support.setdefault(
                p1482.point_key(point), {"point": point, "rows": []}
            )
            row = add_rows(first_row, second_row)
            if row not in bucket["rows"]:
                bucket["rows"].append(row)
    roots = sorted({
        int(bucket["point"][0])
        for bucket in support.values() if not bucket["point"].is_zero()
    })
    ring = PolynomialRing(context["field"], f"X1495_support_{context['fixture']['L']}")
    X = ring.gen()
    G2 = ring.one()
    for root in roots:
        G2 *= X - context["field"](root)
    G2 = G2.monic()
    r = len(canonical)
    if paths != 4 * r**2 or len(support) != 2 * r**2 + 1 or len(roots) != r**2:
        raise RuntimeError("P1495 pair support formula mismatch")
    return support, roots, G2, {
        "ordered_pair_paths": paths,
        "full_point_count": len(support),
        "nonzero_x_count_N": len(roots),
        "G2_degree": int(G2.degree()),
        "G2_sha256": polynomial_hash(G2),
    }


def query_schedule(
    context: dict[str, Any], deck: list[Any], support: dict[Any, dict[str, Any]]
) -> list[dict[str, Any]]:
    fixture = context["fixture"]
    L = int(fixture["L"])
    q = int(fixture["order"])
    challenge_scalar = 1 + p1482.digest_int("P1490", "challenge", L) % (q - 1)
    challenge = challenge_scalar * context["generator"]
    queries = []
    public_index = 0
    for target_index in range(2):
        a = p1482.digest_int("P1490", "target-a", L, target_index) % q
        b = 1 + p1482.digest_int("P1490", "target-b", L, target_index) % (q - 1)
        target = a * context["generator"] + b * challenge
        for fifth in deck:
            queries.append({
                "lane": "public_nonplanted",
                "index": public_index,
                "point": target - fifth,
            })
            public_index += 1
    nonzero = [
        bucket["point"]
        for _, bucket in sorted(support.items(), key=lambda item: repr(item[0]))
        if not bucket["point"].is_zero()
    ]
    for index in range(16):
        left_index = p1482.digest_int("P1493", "positive-left", L, index) % len(nonzero)
        right_index = p1482.digest_int("P1493", "positive-right", L, index) % len(nonzero)
        point = nonzero[left_index] + nonzero[right_index]
        if point.is_zero():
            point = nonzero[left_index] + nonzero[(right_index + 1) % len(nonzero)]
        queries.append({"lane": "positive_control", "index": index, "point": point})
    for index in range(32):
        scalar = 1 + p1482.digest_int("P1493", "unrestricted", L, index) % (q - 1)
        queries.append({
            "lane": "unrestricted_fixed",
            "index": index,
            "point": scalar * context["generator"],
        })
    return queries


def dense_map_spec(
    name: str,
    kind: str,
    numerator: Any,
    denominator: Any,
    support_derived: bool,
    homomorphic_multiplier: int | None = None,
) -> dict[str, Any]:
    degree = max(int(numerator.degree()), int(denominator.degree()))
    return {
        "name": name,
        "kind": kind,
        "degree": degree,
        "numerator": numerator,
        "denominator": denominator,
        "numerator_degree": int(numerator.degree()),
        "denominator_degree": int(denominator.degree()),
        "numerator_nonzero_coefficients": sum(value != 0 for value in numerator),
        "denominator_nonzero_coefficients": sum(value != 0 for value in denominator),
        "numerator_sha256": polynomial_hash(numerator),
        "denominator_sha256": polynomial_hash(denominator),
        "support_derived": support_derived,
        "homomorphic_multiplier": homomorphic_multiplier,
    }


def monomial_map_spec(name: str, exponent: int, kind: str) -> dict[str, Any]:
    descriptor = f"X^{exponent}".encode("ascii")
    return {
        "name": name,
        "kind": kind,
        "degree": exponent,
        "exponent": exponent,
        "numerator_degree": exponent,
        "denominator_degree": 0,
        "numerator_nonzero_coefficients": 1,
        "denominator_nonzero_coefficients": 1,
        "numerator_sha256": hashlib.sha256(descriptor).hexdigest(),
        "denominator_sha256": hashlib.sha256(b"1").hexdigest(),
        "support_derived": False,
        "homomorphic_multiplier": None,
    }


def build_maps(
    context: dict[str, Any], roots: list[int], G2: Any, r: int, k: int
) -> list[dict[str, Any]]:
    ring = G2.parent()
    X = ring.gen()
    maps = [dense_map_spec("identity_x", "identity", X, ring.one(), False, 1)]
    for m in sorted({2, k, r}):
        rational = context["curve"].multiplication_by_m(m, x_only=True)
        numerator = ring(rational.numerator())
        denominator = ring(rational.denominator())
        maps.append(dense_map_spec(
            f"lattes_m{m}", "lattes", numerator, denominator, False, m
        ))
    maps.append(monomial_map_spec(f"power_k{k}", k, "power"))
    character_exponent = (int(context["fixture"]["p"]) - 1) // k
    maps.append(monomial_map_spec(
        f"character_k{k}", character_exponent, "character"
    ))
    bucket_count = math.ceil(math.sqrt(len(roots)))
    interpolation_points = [
        (context["field"](root), context["field"](index % bucket_count))
        for index, root in enumerate(roots)
    ]
    interpolation = ring.lagrange_polynomial(interpolation_points)
    maps.append(dense_map_spec(
        f"tailored_interpolation_s{bucket_count}",
        "tailored_interpolation",
        interpolation,
        ring.one(),
        True,
    ))
    maps.append(dense_map_spec(
        "pair_annihilator_G2", "annihilator", G2, ring.one(), True
    ))
    return maps


def evaluate_map(spec: dict[str, Any], context: dict[str, Any], point: Any) -> str:
    if point.is_zero():
        return "O"
    x = context["field"](point[0])
    if spec["kind"] in {"power", "character"}:
        value = x ** int(spec["exponent"])
    else:
        denominator = spec["denominator"](x)
        if denominator == 0:
            return "O"
        value = spec["numerator"](x) / denominator
    return f"F:{int(value)}"


def map_public_record(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in spec.items()
        if key not in {"numerator", "denominator"}
    }


def s3_value(context: dict[str, Any], x: Any, y: Any, z: Any) -> Any:
    field = context["field"]
    a = field(context["fixture"]["a"])
    b = field(context["fixture"]["b"])
    x, y, z = field(x), field(y), field(z)
    return (
        (x - y) ** 2 * z**2
        - 2 * ((x + y) * (x * y + a) + 2 * b) * z
        + (x * y - a) ** 2
        - 4 * b * (x + y)
    )


def image_and_addition_cell(
    spec: dict[str, Any], context: dict[str, Any], support: dict[Any, dict[str, Any]], N: int
) -> tuple[dict[Any, str], dict[str, Any]]:
    labels = {
        key: evaluate_map(spec, context, bucket["point"])
        for key, bucket in support.items()
    }
    fibers: dict[str, int] = {}
    for label in labels.values():
        fibers[label] = fibers.get(label, 0) + 1
    nonexceptional = {label for label in fibers if label != "O"}
    sizes = sorted(fibers.values(), reverse=True)
    entropy = -sum(
        (size / len(support)) * math.log2(size / len(support)) for size in sizes
    )
    pointwise_failures = 0
    inverse_failures = 0
    s3_failures = 0
    group_law_failures = 0
    s3_checks = 0
    relation: dict[tuple[str, str], set[str]] = {}
    multiplier = spec["homomorphic_multiplier"]
    q = int(context["fixture"]["order"])
    if multiplier is not None:
        inverse = pow(int(multiplier), -1, q)
        for key, bucket in support.items():
            point = bucket["point"]
            transformed = int(multiplier) * point
            expected = "O" if transformed.is_zero() else f"F:{int(transformed[0])}"
            pointwise_failures += int(labels[key] != expected)
            inverse_failures += int(inverse * transformed != point)
        buckets = list(support.values())
        for left in buckets:
            for right in buckets:
                A, B = left["point"], right["point"]
                C = A + B
                left_t = int(multiplier) * A
                right_t = int(multiplier) * B
                output_t = int(multiplier) * C
                group_law_failures += int(left_t + right_t != output_t)
                if not left_t.is_zero() and not right_t.is_zero() and not output_t.is_zero():
                    s3_checks += 1
                    s3_failures += int(
                        s3_value(context, left_t[0], right_t[0], output_t[0]) != 0
                    )
        addition = {
            "kind": "fixed_degree_S3_from_group_homomorphism",
            "materialized_relation_table_used_as_candidate_advice": False,
            "pointwise_rational_map_failure_count": pointwise_failures,
            "inverse_on_prime_subgroup_failure_count": inverse_failures,
            "group_law_failure_count": group_law_failures,
            "S3_nonexceptional_check_count": s3_checks,
            "S3_failure_count": s3_failures,
            "inverse_scalar_mod_q": inverse,
            "bounded_degree_addition_law": (
                pointwise_failures == inverse_failures == group_law_failures == s3_failures == 0
            ),
        }
    else:
        buckets = list(support.values())
        for left in buckets:
            left_key = p1482.point_key(left["point"])
            for right in buckets:
                right_key = p1482.point_key(right["point"])
                output_label = evaluate_map(spec, context, left["point"] + right["point"])
                relation.setdefault((labels[left_key], labels[right_key]), set()).add(output_label)
        ambiguities = [len(values) for values in relation.values()]
        addition = {
            "kind": "materialized_restricted_support_diagnostic",
            "materialized_relation_table_used_as_candidate_advice": False,
            "input_label_pair_count": len(relation),
            "attained_output_triple_count": sum(ambiguities),
            "maximum_output_label_ambiguity": max(ambiguities),
            "mean_output_label_ambiguity": statistics.mean(ambiguities),
            "relation_sha256": digest_items([
                (key, tuple(sorted(values))) for key, values in relation.items()
            ]),
            "bounded_degree_addition_law": False,
        }
    degree = int(spec["degree"])
    image_size = len(nonexceptional)
    return labels, {
        "image_size_including_infinity": len(fibers),
        "nonexceptional_image_size_s": image_size,
        "fiber_sizes_descending": sizes,
        "maximum_full_point_fiber_size": max(sizes),
        "mean_full_point_fiber_size": len(support) / len(fibers),
        "image_entropy_bits": entropy,
        "label_assignment_sha256": digest_items([(key, labels[key]) for key in labels]),
        "fiber_profile_sha256": digest_items(sorted(fibers.items())),
        "degree_times_nonexceptional_image": degree * image_size,
        "finite_support_fiber_bound_N_le_d_times_s": N <= degree * image_size,
        "collisions_beyond_Kummer_sign_count": max(0, N - image_size),
        "addition": addition,
    }


def query_cell(
    spec: dict[str, Any],
    context: dict[str, Any],
    support: dict[Any, dict[str, Any]],
    labels: dict[Any, str],
    queries: list[dict[str, Any]],
) -> dict[str, Any]:
    image = set(labels.values())
    records = []
    false_negatives = 0
    for query in queries:
        exact = 0
        survivors = 0
        for left in support.values():
            right_point = query["point"] - left["point"]
            hit = p1482.point_key(right_point) in support
            accepted = evaluate_map(spec, context, right_point) in image
            exact += int(hit)
            survivors += int(accepted)
            false_negatives += int(hit and not accepted)
        records.append({
            "lane": query["lane"],
            "index": int(query["index"]),
            "query_point_sha256": hashlib.sha256(
                repr(p1482.point_key(query["point"])).encode("ascii")
            ).hexdigest(),
            "exact_left_decomposition_count": exact,
            "image_membership_survivor_count": survivors,
            "false_survivor_count": survivors - exact,
            "mandatory_A2_probe_count": len(support),
            "complete_probe_plus_opening_work": len(support) + survivors,
        })
    return {
        "query_count": len(records),
        "false_negative_count": false_negatives,
        "maximum_image_membership_survivor_count": max(
            row["image_membership_survivor_count"] for row in records
        ),
        "maximum_complete_probe_plus_opening_work": max(
            row["complete_probe_plus_opening_work"] for row in records
        ),
        "sublinear_unknown_A_enumerator_exhibited": False,
        "records": records,
    }


def source_replay_control(
    context: dict[str, Any],
    canonical: list[Any],
    support: dict[Any, dict[str, Any]],
    queries: list[dict[str, Any]],
) -> dict[str, Any]:
    rows = set()
    failures = 0
    exact = 0
    for query in queries:
        for left in support.values():
            right = support.get(p1482.point_key(query["point"] - left["point"]))
            if right is None:
                continue
            exact += 1
            for left_row in left["rows"]:
                for right_row in right["rows"]:
                    row = add_rows(left_row, right_row)
                    replay = sum(
                        (coefficient * base for coefficient, base in zip(row, canonical)),
                        context["identity"],
                    )
                    if replay != query["point"]:
                        failures += 1
                    else:
                        rows.add((query["lane"], int(query["index"]), row))
    return {
        "exact_left_decomposition_count": exact,
        "deduplicated_source_row_count": len(rows),
        "source_row_sha256": digest_items(list(rows)),
        "source_replay_failure_count": failures,
        "all_sources_replay": failures == 0,
    }


def synthetic_sweep() -> dict[str, Any]:
    cells = []
    for r in SYNTHETIC_SIZES:
        N = r**2
        cells.append({
            "r": r,
            "support_size_N": N,
            "prime_group_bijection_image_size": N,
            "prime_group_bijection_query_work": N,
            "composite_quotient_kernel_size": r,
            "composite_quotient_image_size": r,
            "composite_quotient_all_fiber_opening_work": N,
            "degree_N_annihilator_image_size": 1,
            "degree_N_annihilator_composed_degree": N,
            "one_label_pullback_positive_control_work": r,
            "positive_control_passes_strict_r_three_halves": r < r**1.5,
        })
    return {
        "sizes": SYNTHETIC_SIZES,
        "cells": cells,
        "prime_bijection_query_fitted_exponent": fit_slope(
            SYNTHETIC_SIZES, [cell["prime_group_bijection_query_work"] for cell in cells]
        ),
        "composite_quotient_image_fitted_exponent": fit_slope(
            SYNTHETIC_SIZES, [cell["composite_quotient_image_size"] for cell in cells]
        ),
        "composite_quotient_opening_fitted_exponent": fit_slope(
            SYNTHETIC_SIZES, [cell["composite_quotient_all_fiber_opening_work"] for cell in cells]
        ),
        "annihilator_composed_degree_fitted_exponent": fit_slope(
            SYNTHETIC_SIZES, [cell["degree_N_annihilator_composed_degree"] for cell in cells]
        ),
        "one_label_pullback_positive_control_fitted_exponent": fit_slope(
            SYNTHETIC_SIZES, [cell["one_label_pullback_positive_control_work"] for cell in cells]
        ),
    }


def write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def render_note(payload: dict[str, Any]) -> str:
    lines = [
        "# P1495 restricted Lattes pullback",
        "",
        "## Status",
        "",
        f"`{payload['status']}`",
        "",
        "| L | r | map | degree | image | max query survivors | addition law |",
        "|---:|---:|---|---:|---:|---:|:---:|",
    ]
    for fixture in payload["fixture_cells"]:
        for cell in fixture["maps"]:
            lines.append(
                f"| {fixture['L']} | {fixture['selector_degree_r']} | {cell['map']['name']} | "
                f"{cell['map']['degree']} | {cell['image']['nonexceptional_image_size_s']} | "
                f"{cell['query']['maximum_image_membership_survivor_count']} | "
                f"{str(cell['image']['addition']['bounded_degree_addition_law']).lower()} |"
            )
    lines.extend([
        "",
        "The exact Lattes maps inherit the fixed-degree S3 addition law, but",
        "multiplication is a permutation of every prime-order fixture and leaves",
        "all r^2 Kummer support values distinct. Tailored interpolation and G2",
        "compress the image only by paying growing map degree and have no public",
        "bounded-degree addition law. Every complete query still probes A2.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    frozen = {}
    for path, expected in EXPECTED.items():
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"P1495 frozen hash mismatch for {path}: {actual} != {expected}")
        frozen[str(path.relative_to(ROOT))] = actual
    p1493 = json.loads(P1493_SOURCE.read_text(encoding="utf-8"))
    p1494 = json.loads(P1494_SOURCE.read_text(encoding="utf-8"))
    p1493_pairs = {int(cell["L"]): cell for cell in p1493["pair_support_cells"]}
    p1493_queries = {int(cell["L"]): cell for cell in p1493["query_panels"]}
    p1494_fixtures = {int(cell["L"]): cell for cell in p1494["fixture_cells"]}

    fixture_cells = []
    for fixture in p1482.FIXTURES:
        started = time.perf_counter()
        context = p1482.build_context(fixture)
        selector, roots, _ = p1490.selector_cell(context)
        canonical, deck = p1490.selector_deck(context, roots)
        r = len(canonical)
        L = int(fixture["L"])
        q = int(fixture["order"])
        k = feature_order(L, r)
        support, pair_roots, G2, support_metrics = pair_support(context, canonical, deck)
        queries = query_schedule(context, deck, support)
        maps = build_maps(context, pair_roots, G2, r, k)
        map_cells = []
        theorem_multipliers = []
        for spec in maps:
            labels, image = image_and_addition_cell(
                spec, context, support, support_metrics["nonzero_x_count_N"]
            )
            query = query_cell(spec, context, support, labels, queries)
            map_cells.append({
                "map": map_public_record(spec),
                "image": image,
                "query": query,
                "promotion_eligible": (
                    not spec["support_derived"]
                    and spec["kind"] not in {"character"}
                ),
            })
            if spec["homomorphic_multiplier"] is not None:
                m = int(spec["homomorphic_multiplier"])
                theorem_multipliers.append({
                    "m": m,
                    "gcd_m_q": math.gcd(m, q),
                    "q_divides_map_degree": int(spec["degree"]) % q == 0,
                    "prime_subgroup_restriction_injective": math.gcd(m, q) == 1,
                })
        replay = source_replay_control(context, canonical, support, queries)
        fixture_cells.append({
            "L": L,
            "selector_degree_r": r,
            "feature_order_k": k,
            "field_prime_p": int(fixture["p"]),
            "group_order_q": q,
            "q_is_prime": bool(is_prime(q)),
            "support": support_metrics,
            "matches_P1493_support": (
                support_metrics["full_point_count"]
                == int(p1493_pairs[L]["distinct_full_point_count_including_infinity"])
                and support_metrics["G2_sha256"] == p1493_pairs[L]["G2_coefficient_sha256"]
            ),
            "matches_P1493_query_count": len(queries) == int(p1493_queries[L]["query_count"]),
            "matches_P1494_feature_order": k == int(p1494_fixtures[L]["feature_order_k"]),
            "prime_order_theorem": {
                "subgroup_order_prime": bool(is_prime(q)),
                "homomorphism_kernel_possible_cardinalities": [1, q],
                "tested_multipliers": theorem_multipliers,
                "all_tested_homomorphisms_injective": all(
                    row["prime_subgroup_restriction_injective"] for row in theorem_multipliers
                ),
            },
            "source_replay_control": replay,
            "maps": map_cells,
            "wall_seconds": time.perf_counter() - started,
        })

    sweep = synthetic_sweep()
    support_exact = all(
        cell["matches_P1493_support"]
        and cell["matches_P1493_query_count"]
        and cell["matches_P1494_feature_order"]
        and cell["source_replay_control"]["all_sources_replay"]
        for cell in fixture_cells
    )
    theorem_exact = all(
        cell["q_is_prime"]
        and cell["prime_order_theorem"]["all_tested_homomorphisms_injective"]
        and all(row["gcd_m_q"] == 1 for row in cell["prime_order_theorem"]["tested_multipliers"])
        for cell in fixture_cells
    )
    lattes_exact = all(
        map_cell["image"]["nonexceptional_image_size_s"] == cell["support"]["nonzero_x_count_N"]
        and map_cell["image"]["collisions_beyond_Kummer_sign_count"] == 0
        and map_cell["image"]["addition"]["bounded_degree_addition_law"]
        and map_cell["image"]["addition"]["pointwise_rational_map_failure_count"] == 0
        and map_cell["query"]["false_negative_count"] == 0
        for cell in fixture_cells for map_cell in cell["maps"]
        if map_cell["map"]["kind"] in {"identity", "lattes"}
    )
    rational_degrees_exact = all(
        map_cell["map"]["numerator_degree"] == map_cell["map"]["homomorphic_multiplier"] ** 2
        and map_cell["map"]["denominator_degree"]
        == map_cell["map"]["homomorphic_multiplier"] ** 2 - 1
        for cell in fixture_cells for map_cell in cell["maps"]
        if map_cell["map"]["kind"] == "lattes"
    )
    tailored_boundary_exact = all(
        map_cell["image"]["finite_support_fiber_bound_N_le_d_times_s"]
        and not map_cell["image"]["addition"]["bounded_degree_addition_law"]
        and map_cell["query"]["false_negative_count"] == 0
        for cell in fixture_cells for map_cell in cell["maps"]
        if map_cell["map"]["support_derived"]
    )
    all_queries_r2 = all(
        map_cell["query"]["maximum_complete_probe_plus_opening_work"]
        >= cell["support"]["full_point_count"]
        and not map_cell["query"]["sublinear_unknown_A_enumerator_exhibited"]
        for cell in fixture_cells for map_cell in cell["maps"]
    )
    controls_exact = (
        abs(sweep["prime_bijection_query_fitted_exponent"] - 2.0) < 1e-12
        and abs(sweep["composite_quotient_image_fitted_exponent"] - 1.0) < 1e-12
        and abs(sweep["composite_quotient_opening_fitted_exponent"] - 2.0) < 1e-12
        and abs(sweep["annihilator_composed_degree_fitted_exponent"] - 2.0) < 1e-12
        and abs(sweep["one_label_pullback_positive_control_fitted_exponent"] - 1.0) < 1e-12
    )
    signal = any(
        map_cell["promotion_eligible"]
        and map_cell["image"]["nonexceptional_image_size_s"] < cell["selector_degree_r"] ** 1.5
        and map_cell["image"]["addition"]["bounded_degree_addition_law"]
        and map_cell["query"]["maximum_complete_probe_plus_opening_work"]
        < cell["selector_degree_r"] ** 1.5
        and map_cell["query"]["sublinear_unknown_A_enumerator_exhibited"]
        for cell in fixture_cells for map_cell in cell["maps"]
    )
    status = (
        "NEGATIVE_RESULT_P1495_LATTES_INJECTIVE_TAILORED_PULLBACK_R2"
        if support_exact and theorem_exact and lattes_exact and rational_degrees_exact
        and tailored_boundary_exact and all_queries_r2 and controls_exact and not signal
        else "REVIEW_REQUIRED_P1495_THEOREM_MAP_OR_PULLBACK_MISMATCH"
    )
    payload = {
        "boundary": {
            "candidate_vs_verified": (
                "Division-polynomial Lattes maps are public candidates. Balanced interpolation, G2, materialized addition tables, and relation/source hashes are tailored or verifier controls."
            ),
            "closed": (
                "Prime-subgroup homomorphic/isogeny quotients of degree coprime to q, tested multiplication-induced Lattes maps, monomial/character controls, balanced support interpolation, and G2 annihilation."
            ),
            "not_closed": (
                "A restricted algebraic correspondence that is not a global quotient and comes with a proved sublinear translated pullback enumerator plus bounded-degree addition relation."
            ),
            "pollard_rho": (
                "Every complete map query still consumes Theta(r^2) A2 probes before relation collection; no Shoup-bound break."
            ),
        },
        "fixture_cells": fixture_cells,
        "frozen_files": frozen,
        "gates": {
            "support_queries_and_sources_exact": support_exact,
            "prime_order_kernel_theorem_bound": theorem_exact,
            "all_Lattes_maps_exact_and_Kummer_injective": lattes_exact,
            "division_polynomial_rational_degrees_exact": rational_degrees_exact,
            "tailored_image_degree_and_addition_boundary_exact": tailored_boundary_exact,
            "every_complete_query_requires_r2_support_probes": all_queries_r2,
            "synthetic_quotient_and_pullback_controls_exact": controls_exact,
            "public_sublinear_pullback_exhibited": False,
            "complete_query_below_r_three_halves": False,
            "complete_campaign_below_pollard_rho": False,
            "restricted_correspondence_signal": signal,
        },
        "lineage_relation_controls": [
            {
                "L": int(cell["L"]),
                "target_count": int(cell["target_count"]),
                "target_hit_count": int(cell["target_hit_count"]),
                "relation_rank": int(cell["relation_rank"]),
                "unknown_column_count_including_challenge": int(cell["unknown_column_count_including_challenge"]),
                "relation_row_sha256": cell["relation_row_sha256"],
                "imported_frozen_control_only": True,
            }
            for cell in p1493["primary_relation_panels"]
        ],
        "next_action": (
            "Close global quotient/Lattes relabeling for this prime-order lane. P1496 should return to the representation-level frontier and test an aggregate divisor or non-scalar Jacobian correspondence whose relation does not retain the two missing EC points individually; charge an equal-attempt random baseline and sparse linear-algebra floor."
        ),
        "schema": SCHEMA,
        "status": status,
        "synthetic_sweep": sweep,
        "theorem": {
            "statement": (
                "On an order-q prime subgroup, a homomorphism kernel has cardinality 1 or q. An isogeny/multiplication map of degree coprime to q is injective on that subgroup; the x quotient adds only the unavoidable sign identification."
            ),
            "scope": (
                "Global homomorphisms and isogenies on the target subgroup only; arbitrary subset-tailored rational correspondences are outside the theorem."
            ),
            "references": [
                "https://math.mit.edu/classes/18.783/2025/LectureNotes6.pdf",
                "https://arxiv.org/abs/1509.05365",
            ],
        },
    }
    write_atomic(OUT, (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    write_atomic(NOTE, render_note(payload).encode("utf-8"))
    print(json.dumps({
        "status": status,
        "gates": payload["gates"],
        "fixtures": [
            {
                "L": cell["L"],
                "r": cell["selector_degree_r"],
                "maps": [
                    {
                        "name": map_cell["map"]["name"],
                        "degree": map_cell["map"]["degree"],
                        "image": map_cell["image"]["nonexceptional_image_size_s"],
                        "max_survivors": map_cell["query"]["maximum_image_membership_survivor_count"],
                        "addition": map_cell["image"]["addition"]["bounded_degree_addition_law"],
                    }
                    for map_cell in cell["maps"]
                ],
            }
            for cell in fixture_cells
        ],
        "synthetic_exponents": {
            key: value for key, value in sweep.items() if key not in {"sizes", "cells"}
        },
    }, indent=2, sort_keys=True))
    return 0 if status != "REVIEW_REQUIRED_P1495_THEOREM_MAP_OR_PULLBACK_MISMATCH" else 1


if __name__ == "__main__":
    raise SystemExit(main())
