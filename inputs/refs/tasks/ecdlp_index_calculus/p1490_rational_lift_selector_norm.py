#!/usr/bin/env sage -python
"""Test the rational liftable-x selector through relation rank and descent."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import os
import statistics
import time
from pathlib import Path
from typing import Any

from sage.all import GF, PolynomialRing, matrix, vector

import p1478_sparse_s3_subgroup_norm_composition as p1478
import p1482_coordinate_routed_wagner_tree as p1482


ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = ROOT / "ecdlp_index_calculus_state"
RESEARCH_DIR = ROOT / "research"
CONTRACT = STATE_DIR / "experiment_contract_p1490_rational_lift_selector_norm.md"
OUT = STATE_DIR / "p1490_rational_lift_selector_norm.json"
NOTE = RESEARCH_DIR / "p1490_rational_lift_selector_norm.md"

SCHEMA = "ecdlp.p1490_rational_lift_selector_norm.v1"
FIXTURES = list(p1482.FIXTURES)
PUBLIC_TARGET_COUNT = 256
DENSITY_EXTENSION_TARGET_COUNT = 8192
RELATIONS_PER_TARGET = 16
COMPOSITION_NONCES = range(2)
EXPECTED = {
    CONTRACT: "773a64b16170678762cfd226cd799515a4dcba2035171a18a3d576c5a193eeaf",
    STATE_DIR / "p1478_sparse_s3_subgroup_norm_composition.json":
        "287a08a131ce7b56bd4e8468eb6c443d7bcba4b7fb2ba13c860866c21902b8df",
    STATE_DIR / "p1478_sparse_s3_subgroup_norm_composition_audit.json":
        "d035cba39d08165c4b7dd336d4a095c1c99ff822f8db8c6cf5f3fca3b8c764f9",
    STATE_DIR / "p1489_quadratic_closure_rational_relation_descent.json":
        "dfc0ee8d9b3614f7c25260c04248349528aef1f344d66b34fa07d8d086df387e",
    STATE_DIR / "p1489_quadratic_closure_rational_relation_descent_audit.json":
        "7615c59f6f122d7599ba20f75a320ae0797e481484c0e432edca2cea775e959a",
    ROOT / "tasks/ecdlp_index_calculus/p1478_sparse_s3_subgroup_norm_composition.py":
        "829173bee652ac3f527dfba33c05c1f96d5bf0e32dd5580f800f2bec9065c86b",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scalar_power(value: Any, exponent: int) -> tuple[Any, int]:
    result = value.parent().one()
    multiplications = 0
    while exponent:
        if exponent & 1:
            result *= value
            multiplications += 1
        exponent >>= 1
        if exponent:
            value *= value
            multiplications += 1
    return result, multiplications


def polynomial_power_mod(base: Any, exponent: int, modulus: Any) -> tuple[Any, int]:
    result = base.parent().one()
    products = 0
    base %= modulus
    while exponent:
        if exponent & 1:
            result = (result * base) % modulus
            products += 1
        exponent >>= 1
        if exponent:
            base = (base * base) % modulus
            products += 1
    return result, products


def polynomial_hash(polynomial: Any) -> str:
    return hashlib.sha256(
        b"|".join(str(int(coefficient)).encode("ascii") for coefficient in polynomial)
    ).hexdigest()


def slope(xs: list[float], ys: list[float]) -> float:
    logs_x = [math.log(value) for value in xs]
    logs_y = [math.log(value) for value in ys]
    center_x = statistics.mean(logs_x)
    center_y = statistics.mean(logs_y)
    return sum(
        (x - center_x) * (y - center_y) for x, y in zip(logs_x, logs_y)
    ) / sum((x - center_x) ** 2 for x in logs_x)


def selector_cell(context: dict[str, Any]) -> tuple[Any, list[int], dict[str, Any]]:
    fixture = context["fixture"]
    field = context["field"]
    L = int(fixture["L"])
    p = int(fixture["p"])
    ring = PolynomialRing(field, f"X1490_{L}")
    X = ring.gen()
    modulus = X**L - 1
    cubic = X**3 + field(fixture["a"]) * X + field(fixture["b"])
    powered, modular_products = polynomial_power_mod(cubic, (p - 1) // 2, modulus)
    selector = modulus.gcd(powered - 1).monic()

    subgroup = []
    indicator = []
    legendre_multiplications = 0
    value = field.one()
    for _ in range(L):
        subgroup.append(value)
        curve_value = value**3 + field(fixture["a"]) * value + field(fixture["b"])
        character, products = scalar_power(curve_value, (p - 1) // 2)
        legendre_multiplications += products
        if curve_value == 0:
            raise RuntimeError("P1490 fixture unexpectedly has rational 2-torsion")
        indicator.append(int(character == 1))
        value *= context["h"]
    direct_roots = sorted(int(subgroup[index]) for index, bit in enumerate(indicator) if bit)
    product = ring.one()
    for root in direct_roots:
        product *= X - field(root)
    product = product.monic()
    gcd_roots = sorted(int(root) for root in selector.roots(multiplicities=False))
    if selector != product or gcd_roots != direct_roots:
        raise RuntimeError(f"P1490 selector mismatch at L={L}")
    if direct_roots != p1482.factor_roots(context):
        raise RuntimeError(f"P1490 selector/deck mismatch at L={L}")

    zeta = field(context["h"])
    fourier = []
    for frequency in range(L):
        coefficient = sum(
            (field(bit) * zeta ** (-frequency * index) for index, bit in enumerate(indicator)),
            field.zero(),
        )
        fourier.append(coefficient)
    coefficient_support = sum(coefficient != 0 for coefficient in selector)
    fourier_support = sum(coefficient != 0 for coefficient in fourier)
    selector_fft_proxy = max(1, L * int(math.log2(L)))
    construction_proxy = (
        3 * L + legendre_multiplications + 4 * selector_fft_proxy
    )
    cell = {
        "L": L,
        "fixture": fixture,
        "selector_degree": int(selector.degree()),
        "selector_root_count": len(direct_roots),
        "selector_sha256": polynomial_hash(selector),
        "selector_root_sha256": hashlib.sha256(
            b"|".join(str(root).encode("ascii") for root in direct_roots)
        ).hexdigest(),
        "selector_coefficients": [int(coefficient) for coefficient in selector],
        "selector_coefficient_support": coefficient_support,
        "selector_coefficient_density": coefficient_support / (int(selector.degree()) + 1),
        "indicator_weight": sum(indicator),
        "indicator_fourier_support": fourier_support,
        "indicator_fourier_density": fourier_support / L,
        "gcd_equals_direct_linear_factor_product": selector == product,
        "selector_roots_equal_exact_rational_liftable_deck": gcd_roots == direct_roots,
        "construction": {
            "subgroup_values_examined": L,
            "legendre_field_multiplications": legendre_multiplications,
            "cubic_evaluation_multiplication_proxy": 3 * L,
            "gcd_modular_polynomial_products": modular_products,
            "subproduct_and_transform_proxy": 4 * selector_fft_proxy,
            "complete_fast_field_operation_proxy": construction_proxy,
            "asymptotic_bound": "soft-O(L) field operations",
        },
    }
    return selector, direct_roots, cell


def selector_deck(context: dict[str, Any], roots: list[int]) -> tuple[list[Any], list[Any]]:
    canonical = []
    deck = []
    for root in roots:
        lifts = sorted(
            context["curve"].lift_x(context["field"](root), all=True),
            key=p1482.point_key,
        )
        if len(lifts) != 2 or lifts[0] != -lifts[1]:
            raise RuntimeError("P1490 rational selector lift failure")
        canonical.append(lifts[0])
        deck.extend(lifts)
    return canonical, sorted(deck, key=p1482.point_key)


def linear_norm_value(selector: Any, u: Any, v: Any, a: Any, b: Any) -> tuple[Any, dict[str, int]]:
    A, B, C = p1478.s3_coefficients(a, b, u, v)
    coefficients = list(selector)
    degree = int(selector.degree())
    additions = 0
    multiplications = 0
    if A != 0:
        s = B / A
        t = C / A
        multiplications += 2
        r0 = A.parent().zero()
        r1 = A.parent().zero()
        for coefficient in reversed(coefficients):
            r0, r1 = coefficient - t * r1, r0 - s * r1
            multiplications += 2
            additions += 2
        core = r0 * r0 - s * r0 * r1 + t * r1 * r1
        multiplications += 6
        additions += 2
        leading_power, products = scalar_power(A, degree)
        multiplications += products + 1
        value = leading_power * core
    elif B != 0:
        root = -C / B
        multiplications += 1
        evaluation = A.parent().zero()
        for coefficient in reversed(coefficients):
            evaluation = evaluation * root + coefficient
            multiplications += 1
            additions += 1
        leading_power, products = scalar_power(-B, degree)
        multiplications += products + 1
        value = leading_power * evaluation
    else:
        value, products = scalar_power(C, degree)
        multiplications += products
    return value, {
        "field_additions": additions,
        "field_multiplications": multiplications,
        "selector_degree": degree,
    }


def exact_norm_value(selector: Any, u: Any, v: Any, a: Any, b: Any) -> Any:
    X = selector.parent().gen()
    A, B, C = p1478.s3_coefficients(a, b, u, v)
    return selector.resultant(A * X**2 + B * X + C)


def direct_norm_value(selector: Any, roots: list[int], u: Any, v: Any, a: Any, b: Any) -> Any:
    A, B, C = p1478.s3_coefficients(a, b, u, v)
    value = A.parent().one()
    for root in roots:
        x = A.parent()(root)
        value *= A * x**2 + B * x + C
    return value


def endpoint_roots(selector: Any, u: Any, v: Any, a: Any, b: Any) -> set[int]:
    X = selector.parent().gen()
    A, B, C = p1478.s3_coefficients(a, b, u, v)
    common = selector.gcd(A * X**2 + B * X + C)
    return {int(root) for root in common.roots(multiplicities=False)}


def valid_endpoint_roots(context: dict[str, Any], P: Any, Q: Any, roots: set[int]) -> set[int]:
    valid = set()
    for root in roots:
        for endpoint in context["curve"].lift_x(context["field"](root), all=True):
            for start in (P, -P):
                if start + endpoint in (Q, -Q):
                    valid.add(root)
    return valid


def explicit_endpoint_roots(context: dict[str, Any], P: Any, Q: Any, deck: list[Any]) -> set[int]:
    roots = set()
    for endpoint in deck:
        for start in (P, -P):
            if start + endpoint in (Q, -Q):
                roots.add(int(endpoint[0]))
    return roots


def transition_record(
    context: dict[str, Any], selector: Any, roots: list[int], deck: list[Any], P: Any, Q: Any
) -> dict[str, Any]:
    fixture = context["fixture"]
    field = context["field"]
    a = field(fixture["a"])
    b = field(fixture["b"])
    u = field(P[0])
    v = field(Q[0])
    linear, counts = linear_norm_value(selector, u, v, a, b)
    exact = exact_norm_value(selector, u, v, a, b)
    direct = direct_norm_value(selector, roots, u, v, a, b)
    recovered = endpoint_roots(selector, u, v, a, b)
    valid = valid_endpoint_roots(context, P, Q, recovered)
    explicit = explicit_endpoint_roots(context, P, Q, deck)
    return {
        "linear_exact_direct_match": linear == exact == direct,
        "zero_decision_match": (linear == 0) == bool(explicit),
        "root_match": recovered == set(roots).intersection(recovered) and recovered == explicit,
        "valid_sign_match": valid == explicit,
        "accepted": bool(explicit),
        "raw_root_count": len(recovered),
        "valid_root_count": len(valid),
        "linear_counts": counts,
    }


def one_transition_cell(
    context: dict[str, Any], selector: Any, roots: list[int], deck: list[Any]
) -> dict[str, Any]:
    fixture = context["fixture"]
    q = int(fixture["order"])
    records = []
    for index in range(32):
        scalar = 1 + p1482.digest_int("P1490", "positive", fixture["L"], index) % (q - 1)
        P = scalar * context["generator"]
        endpoint = deck[p1482.digest_int("P1490", "endpoint", fixture["L"], index) % len(deck)]
        Q = P + endpoint
        if Q.is_zero():
            Q = P - endpoint
        record = transition_record(context, selector, roots, deck, P, Q)
        record["lane"] = "positive"
        records.append(record)
    for index in range(32):
        left = 1 + p1482.digest_int("P1490", "left", fixture["L"], index) % (q - 1)
        right = 1 + p1482.digest_int("P1490", "right", fixture["L"], index) % (q - 1)
        record = transition_record(
            context,
            selector,
            roots,
            deck,
            left * context["generator"],
            right * context["generator"],
        )
        record["lane"] = "unrestricted"
        records.append(record)
    return {
        "L": int(fixture["L"]),
        "transition_count": len(records),
        "positive_transition_count": 32,
        "positive_failure_count": sum(
            not row["accepted"] for row in records if row["lane"] == "positive"
        ),
        "linear_exact_direct_mismatch_count": sum(not row["linear_exact_direct_match"] for row in records),
        "zero_decision_mismatch_count": sum(not row["zero_decision_match"] for row in records),
        "endpoint_root_mismatch_count": sum(not row["root_match"] for row in records),
        "endpoint_sign_mismatch_count": sum(not row["valid_sign_match"] for row in records),
        "accepted_transition_count": sum(row["accepted"] for row in records),
        "false_query_count": sum(not row["accepted"] for row in records),
        "maximum_linear_field_multiplications": max(
            row["linear_counts"]["field_multiplications"] for row in records
        ),
        "maximum_linear_field_additions": max(
            row["linear_counts"]["field_additions"] for row in records
        ),
        "sample_records": records[:2] + records[32:34],
    }


def symbolic_norm(coefficients: list[int], a: Any, b: Any, u: Any, v: Any) -> Any:
    parent = v.parent()
    u = parent(u)
    a = parent(a)
    b = parent(b)
    xring = PolynomialRing(parent, "Z1490")
    Z = xring.gen()
    selector = xring([parent(coefficient) for coefficient in coefficients])
    A, B, C = p1478.s3_coefficients(a, b, u, parent(v))
    return parent(selector.resultant(A * Z**2 + B * Z + C))


def polynomial_metrics(polynomial: Any) -> dict[str, Any]:
    coefficients = list(polynomial)
    return {
        "degree": int(polynomial.degree()),
        "coefficient_count": len(coefficients),
        "nonzero_coefficient_count": sum(coefficient != 0 for coefficient in coefficients),
        "coefficient_density": sum(coefficient != 0 for coefficient in coefficients) / len(coefficients),
        "coefficient_sha256": hashlib.sha256(
            b"|".join(str(int(coefficient)).encode("ascii") for coefficient in coefficients)
        ).hexdigest(),
    }


def algebraic_two_step_source(
    context: dict[str, Any], selector: Any, coefficients: list[int], P: Any, w: int
) -> dict[str, Any] | None:
    fixture = context["fixture"]
    field = context["field"]
    ring = PolynomialRing(field, "V1490_source")
    V = ring.gen()
    a = field(fixture["a"])
    b = field(fixture["b"])
    u = field(P[0])
    left = symbolic_norm(coefficients, a, b, u, V)
    right = symbolic_norm(coefficients, a, b, V, ring(field(w)))
    for v in left.gcd(right).roots(multiplicities=False):
        first_roots = endpoint_roots(selector, u, field(v), a, b)
        second_roots = endpoint_roots(selector, field(v), field(w), a, b)
        for start in (P, -P):
            for first_root in sorted(first_roots):
                for first in context["curve"].lift_x(field(first_root), all=True):
                    middle = start + first
                    if middle.is_zero() or int(middle[0]) != int(v):
                        continue
                    for second_root in sorted(second_roots):
                        for second in context["curve"].lift_x(field(second_root), all=True):
                            end = middle + second
                            if not end.is_zero() and int(end[0]) == w:
                                return {
                                    "intermediate_x": int(v),
                                    "first_endpoint": p1482.point_json(first),
                                    "second_endpoint": p1482.point_json(second),
                                    "end": p1482.point_json(end),
                                    "verified": True,
                                }
    return None


def composition_cell(
    context: dict[str, Any], selector: Any, deck: list[Any], nonce: int
) -> dict[str, Any]:
    started = time.perf_counter()
    fixture = context["fixture"]
    field = context["field"]
    L = int(fixture["L"])
    q = int(fixture["order"])
    scalar = 1 + p1482.digest_int("P1490", "public-start", L, nonce) % (q - 1)
    P = scalar * context["generator"]
    u = field(P[0])
    coefficients = [int(coefficient) for coefficient in selector]
    Wring = PolynomialRing(field, f"W1490_{L}_{nonce}")
    W = Wring.gen()
    Vring = PolynomialRing(Wring, f"V1490_{L}_{nonce}")
    V = Vring.gen()
    a = field(fixture["a"])
    b = field(fixture["b"])
    left = symbolic_norm(coefficients, a, b, Vring(u), V)
    right = symbolic_norm(coefficients, a, b, V, Vring(W))
    resultant = Wring(left.resultant(right))
    repeated = resultant.gcd(resultant.derivative())
    squarefree = (resultant // repeated).monic()
    roots = {int(root) for root in squarefree.roots(multiplicities=False)}
    reachable = {}
    for start_sign, start in ((1, P), (-1, -P)):
        for first in deck:
            middle = start + first
            for second in deck:
                end = middle + second
                if not end.is_zero():
                    reachable.setdefault(
                        int(end[0]),
                        (start_sign, p1482.point_json(first), p1482.point_json(second)),
                    )
    reachable_roots = set(reachable)
    if roots != reachable_roots:
        raise RuntimeError(f"P1490 composition root mismatch at L={L}, nonce={nonce}")
    source_records = []
    for root in sorted(roots)[:8]:
        witness = algebraic_two_step_source(context, selector, coefficients, P, root)
        source_records.append({"root": root, "witness": witness})
    if any(row["witness"] is None for row in source_records):
        raise RuntimeError(f"P1490 composition source failure at L={L}, nonce={nonce}")
    known_return_present = squarefree(field(u)) == 0
    nonreturn = squarefree // (W - field(u)) if known_return_present else squarefree
    r = int(selector.degree())
    return {
        "L": L,
        "nonce": nonce,
        "public_target_constructed_before_source_search": True,
        "public_start": p1482.point_json(P),
        "public_start_scalar_sha256": hashlib.sha256(str(scalar).encode("ascii")).hexdigest(),
        "selector_degree_r": r,
        "one_transition_degree": int(left.degree()),
        "raw_resultant": polynomial_metrics(resultant),
        "squarefree_resultant": polynomial_metrics(squarefree),
        "nonreturn_resultant": polynomial_metrics(nonreturn),
        "known_return_root_present": known_return_present,
        "expected_generic_raw_degree_4r2": 4 * r * r,
        "expected_generic_squarefree_degree_2r2_plus_1": 2 * r * r + 1,
        "base_field_root_count": len(roots),
        "explicit_reachable_x_count": len(reachable_roots),
        "root_false_negative_count": len(reachable_roots - roots),
        "root_false_positive_count": len(roots - reachable_roots),
        "algebraic_source_recovery_count": sum(row["witness"] is not None for row in source_records),
        "algebraic_source_recovery_target_count": len(source_records),
        "source_records": source_records,
        "dense_pair_state_materialized": True,
        "candidate_backend_below_L_three_halves": False,
        "wall_seconds": time.perf_counter() - started,
    }


def coefficient_for_deck_point(point: Any, canonical: list[Any]) -> tuple[int, ...]:
    coefficients = [0] * len(canonical)
    for column, base in enumerate(canonical):
        if point == base:
            coefficients[column] = 1
            return tuple(coefficients)
        if point == -base:
            coefficients[column] = -1
            return tuple(coefficients)
    raise RuntimeError("P1490 deck point lacks a canonical factor column")


def source_table(
    context: dict[str, Any], canonical: list[Any], deck: list[Any], width: int
) -> tuple[list[tuple[Any, tuple[int, ...]]], dict[Any, list[tuple[int, ...]]]]:
    records = [(point, coefficient_for_deck_point(point, canonical)) for point in deck]
    rows = []
    table = {}
    for indices in itertools.combinations_with_replacement(range(len(records)), width):
        point = sum((records[index][0] for index in indices), context["identity"])
        coefficients = tuple(
            sum(records[index][1][column] for index in indices)
            for column in range(len(canonical))
        )
        rows.append((point, coefficients))
        table.setdefault(p1482.point_key(point), []).append(coefficients)
    return rows, table


def relation_control(
    context: dict[str, Any], canonical: list[Any], deck: list[Any], target_count: int, lane: str
) -> dict[str, Any]:
    started = time.perf_counter()
    fixture = context["fixture"]
    L = int(fixture["L"])
    q = int(fixture["order"])
    challenge_scalar = 1 + p1482.digest_int("P1490", "challenge", L) % (q - 1)
    challenge = challenge_scalar * context["generator"]
    pairs, _ = source_table(context, canonical, deck, 2)
    triples, triple_table = source_table(context, canonical, deck, 3)
    equations = {}
    target_hits = 0
    source_replay_failures = 0
    matched_source_candidates = 0
    for target_index in range(target_count):
        a = p1482.digest_int("P1490", "target-a", L, target_index) % q
        b = 1 + p1482.digest_int("P1490", "target-b", L, target_index) % (q - 1)
        target = a * context["generator"] + b * challenge
        target_relations = {}
        for pair_point, pair_coefficients in pairs:
            needed = p1482.point_key(target - pair_point)
            for triple_coefficients in triple_table.get(needed, []):
                matched_source_candidates += 1
                coefficients = tuple(
                    left + right for left, right in zip(pair_coefficients, triple_coefficients)
                )
                replay = sum(
                    (coefficient * point for coefficient, point in zip(coefficients, canonical)),
                    context["identity"],
                )
                if replay != target:
                    source_replay_failures += 1
                    continue
                target_relations.setdefault(coefficients, None)
                if len(target_relations) >= RELATIONS_PER_TARGET:
                    break
            if len(target_relations) >= RELATIONS_PER_TARGET:
                break
        if target_relations:
            target_hits += 1
        for coefficients in target_relations:
            row = tuple(value % q for value in coefficients) + ((-b) % q,)
            equations.setdefault((row, a % q), (target_index, coefficients, a, b))

    field = GF(q)
    rows = [list(key[0]) for key in equations]
    rhs = [key[1] for key in equations]
    column_count = len(canonical) + 1
    relation_matrix = matrix(field, rows) if rows else matrix(field, 0, column_count)
    relation_rank = int(relation_matrix.rank())
    expected_log_map = p1482.bsgs_logs(context, canonical)
    expected_solution = [expected_log_map[p1482.point_key(point)] for point in canonical]
    expected_solution.append(challenge_scalar)
    all_equations_match_expected = all(
        sum(value * expected for value, expected in zip(row, expected_solution)) % q == value
        for row, value in zip(rows, rhs)
    )
    recovered_solution = None
    recovered_matches = False
    if relation_rank == column_count:
        solution = relation_matrix.solve_right(vector(field, rhs))
        recovered_solution = [int(value) for value in solution]
        recovered_matches = recovered_solution == expected_solution
    encoded = b"\n".join(
        repr((key[0], key[1])).encode("ascii") for key in sorted(equations)
    )
    return {
        "L": L,
        "lane": lane,
        "public_challenge": p1482.point_json(challenge),
        "challenge_scalar_sha256": hashlib.sha256(str(challenge_scalar).encode("ascii")).hexdigest(),
        "target_count": target_count,
        "targets_fixed_before_source_search": True,
        "target_hit_count": target_hits,
        "target_split_rate": target_hits / target_count,
        "factor_column_count": len(canonical),
        "unknown_column_count_including_challenge": column_count,
        "deduplicated_relation_count": len(equations),
        "relation_rank": relation_rank,
        "full_relation_plus_challenge_rank": relation_rank == column_count,
        "all_sources_replay": source_replay_failures == 0,
        "source_replay_failure_count": source_replay_failures,
        "all_equations_match_verifier_logs": all_equations_match_expected,
        "relation_derived_challenge_recovery": recovered_matches,
        "recovered_challenge_matches_verifier_scalar": recovered_matches,
        "relation_row_sha256": hashlib.sha256(encoded).hexdigest(),
        "work": {
            "deck_size": len(deck),
            "pair_source_count": len(pairs),
            "triple_source_count": len(triples),
            "pair_lookup_count": target_count * len(pairs),
            "matched_source_candidate_count": matched_source_candidates,
            "precomputation_asymptotic": "Theta(L^3)",
            "per_target_asymptotic": "Theta(L^2)",
            "complete_relation_campaign_asymptotic": "Theta(L^3)=Theta(q^(3/5))",
            "complete_q_exponent": 0.6,
            "pollard_rho_q_exponent": 0.5,
        },
        "wall_seconds": time.perf_counter() - started,
    }


def write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def render_note(payload: dict[str, Any]) -> str:
    lines = [
        "# P1490 rational lift selector norm",
        "",
        "## Status",
        "",
        f"`{payload['status']}`",
        "",
        "| L | selector r | Fourier support | max norm mults | relation rank | columns |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    relation_by_L = {cell["L"]: cell for cell in payload["relation_controls"]}
    transition_by_L = {cell["L"]: cell for cell in payload["one_transition_cells"]}
    for cell in payload["selector_cells"]:
        relation = relation_by_L[cell["L"]]
        transition = transition_by_L[cell["L"]]
        lines.append(
            f"| {cell['L']} | {cell['selector_degree']} | {cell['indicator_fourier_support']} | "
            f"{transition['maximum_linear_field_multiplications']} | "
            f"{relation['relation_rank']} | {relation['unknown_column_count_including_challenge']} |"
        )
    lines.extend([
        "",
        "The rational selector and its one-transition norm are exact, and the",
        "non-planted toy relation controls recover the challenge scalar at full",
        "rank. The only implemented five-term source backend materializes a",
        "quadratic pair state and costs Theta(L^3)=Theta(q^(3/5)) over a full",
        "relation campaign. This is above rho, so the key recovery is a correctness",
        "control rather than a faster ECDLP algorithm.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    frozen = {}
    for path, expected in EXPECTED.items():
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"P1490 frozen hash mismatch for {path}: {actual} != {expected}")
        frozen[str(path.relative_to(ROOT))] = actual

    selector_cells = []
    one_transition_cells = []
    composition_cells = []
    relation_controls = []
    density_extension_controls = []
    construction_work = []
    for fixture in FIXTURES:
        context = p1482.build_context(fixture)
        selector, roots, selector_record = selector_cell(context)
        canonical, deck = selector_deck(context, roots)
        selector_cells.append(selector_record)
        construction_work.append(selector_record["construction"]["complete_fast_field_operation_proxy"])
        one_transition_cells.append(one_transition_cell(context, selector, roots, deck))
        for nonce in COMPOSITION_NONCES:
            composition_cells.append(composition_cell(context, selector, deck, nonce))
        relation_controls.append(
            relation_control(context, canonical, deck, PUBLIC_TARGET_COUNT, "frozen_256")
        )
        if int(fixture["L"]) >= 16:
            density_extension_controls.append(
                relation_control(
                    context,
                    canonical,
                    deck,
                    DENSITY_EXTENSION_TARGET_COUNT,
                    "post_panel_density_extension_8192",
                )
            )

    selector_exact = all(
        cell["gcd_equals_direct_linear_factor_product"]
        and cell["selector_roots_equal_exact_rational_liftable_deck"]
        for cell in selector_cells
    )
    transition_exact = all(
        cell["positive_failure_count"] == 0
        and cell["linear_exact_direct_mismatch_count"] == 0
        and cell["zero_decision_mismatch_count"] == 0
        and cell["endpoint_root_mismatch_count"] == 0
        and cell["endpoint_sign_mismatch_count"] == 0
        for cell in one_transition_cells
    )
    composition_exact = all(
        cell["root_false_negative_count"] == 0
        and cell["root_false_positive_count"] == 0
        and cell["algebraic_source_recovery_count"] == cell["algebraic_source_recovery_target_count"]
        for cell in composition_cells
    )
    generic_quadratic_degree = all(
        cell["raw_resultant"]["degree"] == cell["expected_generic_raw_degree_4r2"]
        and cell["squarefree_resultant"]["degree"]
        == cell["expected_generic_squarefree_degree_2r2_plus_1"]
        for cell in composition_cells
    )
    primary_relation_full_rank = all(
        cell["targets_fixed_before_source_search"]
        and cell["full_relation_plus_challenge_rank"]
        and cell["all_sources_replay"]
        and cell["all_equations_match_verifier_logs"]
        and cell["relation_derived_challenge_recovery"]
        for cell in relation_controls
    )
    extension_relation_exact = all(
        cell["targets_fixed_before_source_search"]
        and cell["full_relation_plus_challenge_rank"]
        and cell["all_sources_replay"]
        and cell["all_equations_match_verifier_logs"]
        and cell["relation_derived_challenge_recovery"]
        for cell in density_extension_controls
    )
    relation_pipeline_exact = all(
        cell["all_sources_replay"] and cell["all_equations_match_verifier_logs"]
        for cell in relation_controls
    ) and extension_relation_exact
    construction_exponent = slope(
        [float(cell["L"]) for cell in selector_cells],
        [float(cell["construction"]["complete_fast_field_operation_proxy"]) for cell in selector_cells],
    )
    nonreturn_degrees = [
        statistics.mean(
            cell["nonreturn_resultant"]["degree"]
            for cell in composition_cells if cell["L"] == selector_cell_record["L"]
        )
        for selector_cell_record in selector_cells
    ]
    composition_degree_exponent = slope(
        [float(cell["L"]) for cell in selector_cells],
        [float(value) for value in nonreturn_degrees],
    )
    unique_r_degrees = {}
    for cell in composition_cells:
        unique_r_degrees.setdefault(
            int(cell["selector_degree_r"]),
            int(cell["nonreturn_resultant"]["degree"]),
        )
    composition_degree_r_exponent = slope(
        [float(value) for value in sorted(unique_r_degrees)],
        [float(unique_r_degrees[value]) for value in sorted(unique_r_degrees)],
    )
    status = (
        "MIXED_RESULT_P1490_LINEAR_RATIONAL_SELECTOR_RELATION_CONTROL_QUADRATIC_COMPOSITION"
        if selector_exact
        and transition_exact
        and composition_exact
        and generic_quadratic_degree
        and relation_pipeline_exact
        else "NEGATIVE_RESULT_P1490_SELECTOR_NORM_OR_RELATION_CONTROL_FAILED"
    )
    payload = {
        "asymptotic_accounting": {
            "selector_construction": "soft-O(L)",
            "selector_construction_fitted_log_L_exponent": construction_exponent,
            "two_transition_nonreturn_degree_fitted_log_L_exponent": composition_degree_exponent,
            "two_transition_nonreturn_degree_fitted_log_r_exponent": composition_degree_r_exponent,
            "two_transition_representation": "Theta(r^2), with r=Theta(L) under ordinary lift density",
            "explicit_relation_backend": "Theta(L^3)=Theta(q^(3/5))",
            "explicit_relation_backend_q_exponent": 0.6,
            "pollard_rho_q_exponent": 0.5,
        },
        "boundary": {
            "candidate_vs_verified": (
                "Selectors, norms, public relations, and toy challenge recovery are exact. "
                "The only complete source backend is the verifier-charged pair/triple oracle."
            ),
            "closed": (
                "Using the rational lift selector alone to avoid P1478's quadratic two-transition state."
            ),
            "not_closed": (
                "An implicit modular intersection/source method that acts on the selector norm below L^1.5."
            ),
            "pollard_rho": (
                "The complete implemented campaign costs q^(3/5), above rho q^(1/2); no Shoup-lower-bound break."
            ),
        },
        "composition_cells": composition_cells,
        "density_extension_controls": density_extension_controls,
        "frozen_files": frozen,
        "gates": {
            "selector_exact": selector_exact,
            "one_transition_linear_norm_exact": transition_exact,
            "two_transition_roots_and_sources_exact": composition_exact,
            "generic_quadratic_composition_degree": generic_quadratic_degree,
            "frozen_256_relation_and_descent_control_full_rank": primary_relation_full_rank,
            "post_panel_density_extension_full_rank": extension_relation_exact,
            "nonplanted_relation_pipeline_exact": relation_pipeline_exact,
            "nonmaterializing_zero_source_extractor_below_L_three_halves": False,
            "complete_campaign_below_pollard_rho": False,
            "rational_selector_composition_signal": False,
        },
        "next_action": (
            "Keep the exact selector and linear norm, but do not materialize J. "
            "P1491 should test a transposed modular-subresultant/intersection operator against a frozen A3 product, "
            "with source opening and total work below L^1.5; otherwise leave this subgroup lane closed."
        ),
        "one_transition_cells": one_transition_cells,
        "relation_controls": relation_controls,
        "schema": SCHEMA,
        "selector_cells": selector_cells,
        "status": status,
    }
    write_atomic(OUT, (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    write_atomic(NOTE, render_note(payload).encode("utf-8"))
    print(json.dumps({
        "status": status,
        "gates": payload["gates"],
        "selector_degrees": [cell["selector_degree"] for cell in selector_cells],
        "composition_nonreturn_degrees": nonreturn_degrees,
        "relation_ranks": [
            [cell["relation_rank"], cell["unknown_column_count_including_challenge"]]
            for cell in relation_controls
        ],
        "density_extension_ranks": [
            [cell["L"], cell["relation_rank"], cell["unknown_column_count_including_challenge"]]
            for cell in density_extension_controls
        ],
        "asymptotic_accounting": payload["asymptotic_accounting"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
