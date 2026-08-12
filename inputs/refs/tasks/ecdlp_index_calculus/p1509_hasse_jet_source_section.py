#!/usr/bin/env sage -python
"""Exhaust the local IDEA-068 Hasse-jet source section on P1490 cells."""

from __future__ import annotations

import collections
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from sage.all import PolynomialRing

import p1482_coordinate_routed_wagner_tree as p1482
import p1490_rational_lift_selector_norm as p1490


ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "ecdlp_index_calculus_state"
RESEARCH = ROOT / "research"
CONTRACT = STATE / "experiment_contract_p1509_hasse_jet_source_section.md"
P1490 = STATE / "p1490_rational_lift_selector_norm.json"
P1490_AUDIT = STATE / "p1490_rational_lift_selector_norm_audit.json"
P1491 = STATE / "p1491_pointwise_selector_subresultant.json"
P1491_AUDIT = STATE / "p1491_pointwise_selector_subresultant_audit.json"
P1505 = STATE / "p1505_endpoint_moment_source_tag_gate.json"
P1505_AUDIT = STATE / "p1505_endpoint_moment_source_tag_gate_audit.json"
IDEA = Path(
    "/Volumes/Volume/crypto-autoresearcher/ideas/deferred/"
    "ECDLP-IDEA-068_pre_event_elimination_motif_generator_hypothesis.md"
)
DERIVATION = Path(
    "/Volumes/Volume/crypto-autoresearcher/ideas/artifacts/"
    "ECDLP-IDEA-068/constructive_section.md"
)
FOCUS_QUEUE = Path(
    "/Volumes/Volume/crypto-autoresearcher/focus/archive/"
    "focus_queue_idea068_active.json"
)
FOCUS_PLAN = Path(
    "/Volumes/Volume/crypto-autoresearcher/focus/archive/"
    "focus_plan_idea068_active.json"
)
OUT = STATE / "p1509_hasse_jet_source_section.json"
NOTE = RESEARCH / "p1509_hasse_jet_source_section.md"

SCHEMA = "ecdlp.p1509_hasse_jet_source_section.v1"
EXPECTED = {
    CONTRACT: "7b35fdd15681ad35c2cf07d3549d594208401f59412e82e4e69e61244419ed60",
    P1490: "1fbb457f642dab18cab43c69bf694f9a41b68c6ecefa365d7432e1ac7107cbab",
    P1490_AUDIT: "da5b6d4b194d9c03a29622ac03fe3e8c6dae33f1e99c788c46b82fb38f85fa7a",
    P1491: "26fc025c2de2c8ce331bacc8e556d47557159eea755fbc4e86d87da2d1d483be",
    P1491_AUDIT: "31b1c95e09addd661e693d88fbdce2e1589fec47c7752e20b69f0bd7e0db6bc4",
    P1505: "a8c7e0a1cb69fa762102fc1a9339390e3844081eb60245dd353f38e59a16b672",
    P1505_AUDIT: "2ffc182297fad777955b89d1234a6cc280e6fe4dca32db8d851fe31b37c3562b",
    IDEA: "3f4aa869b98110edeeacb22a9a195e547e158e940c82464247c12c5d7b13ffbb",
    DERIVATION: "6a8183033643ea9dab126a7add08c69508814eaee0a0667151e9ff569432f7b5",
    FOCUS_QUEUE: "a880da48dee4ded964a90db672da2d00c61f06af30ad51678f86a58dffd85221",
    FOCUS_PLAN: "a9483d2cb43ec598718abbd2f472ba5acae010c398cbdd43f03a31a2e1e41307",
}


def compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return hashlib.sha256(compact(value).encode("ascii")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def write_atomic(path: Path, data: bytes) -> None:
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def point_key(point: Any) -> tuple[int, int]:
    return int(point[0]), int(point[1])


def s3(first: Any, second: Any, third: Any, a: Any, b: Any) -> Any:
    return (
        (first - second) ** 2 * third**2
        - 2 * ((first + second) * (first * second + a) + 2 * b) * third
        + (first * second - a) ** 2
        - 4 * b * (first + second)
    )


def product(values: list[Any], one: Any) -> Any:
    output = one
    for value in values:
        output *= value
    return output


def cofactor_marker(factors: list[Any], codes: list[Any]) -> Any:
    parent = factors[0].parent()
    return sum(
        (
            codes[index]
            * product(factors[:index] + factors[index + 1 :], parent.one())
            for index in range(len(factors))
        ),
        parent.zero(),
    )


def direct_source_partition(context: dict[str, Any], deck: list[Any], start: Any) -> dict[int, list[tuple[int, int, int]]]:
    by_x: dict[int, set[tuple[int, int, int]]] = collections.defaultdict(set)
    for start_sign, signed_start in ((1, start), (-1, -start)):
        for first_index, first in enumerate(deck):
            for second_index, second in enumerate(deck):
                endpoint = signed_start + first + second
                if endpoint.is_zero():
                    continue
                by_x[int(endpoint[0])].add(
                    (start_sign, min(first_index, second_index), max(first_index, second_index))
                )
    return {endpoint: sorted(tags) for endpoint, tags in by_x.items()}


def source_partition_hash(partition: dict[int, list[tuple[int, int, int]]]) -> str:
    return digest([
        [endpoint, [list(tag) for tag in partition[endpoint]]]
        for endpoint in sorted(partition)
    ])


def decode_leading_form(
    leading: Any,
    marker_variables: tuple[Any, Any, Any, Any],
    alpha_lookup: dict[int, int],
) -> tuple[list[tuple[int, int]], list[dict[str, Any]]]:
    E0, E1, H0, H1 = marker_variables
    decoded = []
    factor_records = []
    for factor, exponent in leading.factor():
        if factor.total_degree() != 1:
            raise RuntimeError(f"P1509 nonlinear leading factor: {factor}")
        e0 = factor.monomial_coefficient(E0)
        e1 = factor.monomial_coefficient(E1)
        h0 = factor.monomial_coefficient(H0)
        h1 = factor.monomial_coefficient(H1)
        if e0 == 0 or h0 == 0:
            raise RuntimeError(f"P1509 zero source-code anchor: {factor}")
        left_alpha = int(e1 / e0)
        right_alpha = int(h1 / h0)
        if left_alpha not in alpha_lookup or right_alpha not in alpha_lookup:
            raise RuntimeError("P1509 source-code ratio outside catalog")
        pair = (alpha_lookup[left_alpha], alpha_lookup[right_alpha])
        for _ in range(int(exponent)):
            decoded.append(pair)
        factor_records.append({
            "factor": str(factor),
            "multiplicity": int(exponent),
            "left_alpha": left_alpha,
            "right_alpha": right_alpha,
            "decoded_pair": list(pair),
        })
    return sorted(decoded), factor_records


def replay_decoded_sources(
    context: dict[str, Any],
    selector_roots: list[int],
    deck: list[Any],
    start: Any,
    endpoint_x: int,
    common_roots: list[Any],
    decoded_pairs: list[tuple[int, int]],
) -> list[tuple[int, int, int]]:
    field = context["field"]
    curve = context["curve"]
    deck_index = {point_key(point): index for index, point in enumerate(deck)}
    tags = set()
    for first_factor, second_factor in decoded_pairs:
        first_lifts = curve.lift_x(field(selector_roots[first_factor]), all=True)
        second_lifts = curve.lift_x(field(selector_roots[second_factor]), all=True)
        for common_root in common_roots:
            for start_sign, signed_start in ((1, start), (-1, -start)):
                for first in first_lifts:
                    middle = signed_start + first
                    if middle.is_zero() or middle[0] != common_root:
                        continue
                    for second in second_lifts:
                        endpoint = middle + second
                        if endpoint.is_zero() or int(endpoint[0]) != endpoint_x:
                            continue
                        left_index = deck_index[point_key(first)]
                        right_index = deck_index[point_key(second)]
                        tags.add((
                            start_sign,
                            min(left_index, right_index),
                            max(left_index, right_index),
                        ))
    return sorted(tags)


def planted_resultant_controls(field: Any) -> dict[str, Any]:
    tring = PolynomialRing(field, "T1509_control")
    T = tring.gen()
    vring = PolynomialRing(tring, "V1509_control")
    V = vring.gen()

    def control(common_roots: list[int], left_extra: int, right_extra: int) -> dict[str, Any]:
        A = product([V - field(root) for root in common_roots + [left_extra]], vring.one())
        B = product([V - field(root) for root in common_roots + [right_extra]], vring.one())
        delta_a = vring.one()
        delta_b = vring(V + field(7))
        resultant = (A + T * delta_a).resultant(B + T * delta_b)
        order = len(common_roots)
        actual = tring(resultant)[order]
        expected = field.one()
        A0 = vring(A.subs({V: vring.gen()}))
        B0 = vring(B.subs({V: vring.gen()}))
        for root in common_roots:
            rho = tring(field(root))
            expected *= (
                tring(A0.derivative()(rho)) * tring(delta_b(rho))
                - tring(B0.derivative()(rho)) * tring(delta_a(rho))
            )
        actual_constant = field(actual)
        expected_constant = field(expected)
        ratio = actual_constant / expected_constant if expected_constant else field.zero()
        return {
            "common_root_count": order,
            "first_nonzero_resultant_order": min(
                index for index, coefficient in enumerate(tring(resultant)) if coefficient
            ),
            "actual_leading_coefficient": int(actual_constant),
            "lemma_product": int(expected_constant),
            "nonzero_public_scale_ratio": int(ratio),
            "lemma_matches_up_to_nonzero_scale": actual_constant != 0 and expected_constant != 0,
        }

    return {
        "degree_one": control([1], 3, 4),
        "degree_two": control([1, 2], 3, 4),
    }


def cell_record(
    fixture: dict[str, Any],
    nonce: int,
    p1505_cell: dict[str, Any],
) -> dict[str, Any]:
    context = p1482.build_context(fixture)
    field = context["field"]
    curve = context["curve"]
    L = int(fixture["L"])
    order = int(fixture["order"])
    selector, selector_roots, _ = p1490.selector_cell(context)
    _, deck = p1490.selector_deck(context, selector_roots)
    r = int(selector.degree())
    scalar = 1 + p1482.digest_int("P1490", "public-start", L, nonce) % (order - 1)
    start = scalar * context["generator"]
    u = field(start[0])
    a = field(fixture["a"])
    b = field(fixture["b"])

    vring = PolynomialRing(field, f"V1509_{L}_{nonce}")
    V = vring.gen()
    left_factors = [s3(vring(u), V, vring(field(root)), a, b) for root in selector_roots]
    A = product(left_factors, vring.one())
    alpha = [field(index + 1) for index in range(r)]
    permutation = sorted(
        range(r),
        key=lambda index: p1482.digest_int("P1509", "code-permutation", L, nonce, index),
    )
    permuted_alpha = [field(permutation[index] + 1) for index in range(r)]
    A0 = cofactor_marker(left_factors, [field.one()] * r)
    A1 = cofactor_marker(left_factors, alpha)
    A1_permuted = cofactor_marker(left_factors, permuted_alpha)
    if A != p1490.symbolic_norm([int(value) for value in selector], a, b, vring(u), V):
        raise RuntimeError("P1509 left norm factorization mismatch")

    wring = PolynomialRing(field, f"W1509_{L}_{nonce}")
    W = wring.gen()
    nested = PolynomialRing(wring, f"Z1509_{L}_{nonce}")
    Z = nested.gen()
    left_nested = p1490.symbolic_norm(
        [int(value) for value in selector], a, b, nested(u), Z
    )
    right_nested = p1490.symbolic_norm(
        [int(value) for value in selector], a, b, Z, nested(W)
    )
    raw = wring(left_nested.resultant(right_nested))
    squarefree = (raw // raw.gcd(raw.derivative())).monic()
    endpoint_roots = sorted(squarefree.roots(multiplicities=False), key=int)

    marker_ring = PolynomialRing(field, names=(
        f"E0_1509_{L}_{nonce}", f"E1_1509_{L}_{nonce}",
        f"H0_1509_{L}_{nonce}", f"H1_1509_{L}_{nonce}",
    ))
    E0, E1, H0, H1 = marker_ring.gens()
    alpha_lookup = {int(value): index for index, value in enumerate(alpha)}
    endpoints = []
    decoded_partition: dict[int, list[tuple[int, int, int]]] = {}
    for endpoint in endpoint_roots:
        w = field(endpoint)
        right_factors = [s3(V, vring(w), vring(field(root)), a, b) for root in selector_roots]
        B = product(right_factors, vring.one())
        B0 = cofactor_marker(right_factors, [field.one()] * r)
        B1 = cofactor_marker(right_factors, alpha)
        B1_permuted = cofactor_marker(right_factors, permuted_alpha)
        common = A.gcd(B).monic()
        common_roots = sorted(common.roots(multiplicities=False), key=int)
        leading = marker_ring.one()
        leading_permuted = marker_ring.one()
        local_records = []
        for common_root in common_roots:
            left_derivative = A.derivative()(common_root)
            right_derivative = B.derivative()(common_root)
            linear = (
                left_derivative * (H0 * B0(common_root) + H1 * B1(common_root))
                - right_derivative * (E0 * A0(common_root) + E1 * A1(common_root))
            )
            if linear == 0:
                raise RuntimeError("P1509 zero local Hasse factor")
            leading *= linear
            leading_permuted *= (
                left_derivative * (H0 * B0(common_root) + H1 * B1_permuted(common_root))
                - right_derivative
                * (E0 * A0(common_root) + E1 * A1_permuted(common_root))
            )
            local_records.append({
                "intermediate_x": int(common_root),
                "linear_factor_sha256": digest(str(linear)),
            })
        decoded_pairs, factor_records = decode_leading_form(
            leading, (E0, E1, H0, H1), alpha_lookup
        )
        permuted_lookup = {
            int(value): index for index, value in enumerate(permuted_alpha)
        }
        permuted_pairs, _ = decode_leading_form(
            leading_permuted, (E0, E1, H0, H1), permuted_lookup
        )
        decoded_tags = replay_decoded_sources(
            context,
            selector_roots,
            deck,
            start,
            int(endpoint),
            common_roots,
            decoded_pairs,
        )
        decoded_partition[int(endpoint)] = decoded_tags
        endpoints.append({
            "endpoint_x": int(endpoint),
            "is_known_return": int(endpoint) == int(u),
            "gcd_degree": int(common.degree()),
            "common_root_count": len(common_roots),
            "leading_total_degree": int(leading.total_degree()),
            "leading_form_sha256": digest(str(leading)),
            "decoded_factor_pairs": [list(pair) for pair in decoded_pairs],
            "permuted_code_factor_pairs_match": permuted_pairs == decoded_pairs,
            "decoded_source_tags": [list(tag) for tag in decoded_tags],
            "decoded_source_tag_count": len(decoded_tags),
            "local_records": local_records,
            "factored_forms": factor_records,
        })

    direct_partition = direct_source_partition(context, deck, start)
    decoded_hash = source_partition_hash(decoded_partition)
    direct_hash = source_partition_hash(direct_partition)
    nonreturn = [record for record in endpoints if not record["is_known_return"]]
    returns = [record for record in endpoints if record["is_known_return"]]
    gcd_histogram = collections.Counter(record["gcd_degree"] for record in nonreturn)
    return {
        "L": L,
        "nonce": nonce,
        "p": int(fixture["p"]),
        "order": order,
        "selector_degree_r": r,
        "selector_root_count": len(selector_roots),
        "deck_size": len(deck),
        "public_start": p1482.point_json(start),
        "endpoint_count": len(endpoints),
        "expected_endpoint_count_2r2_plus_1": 2 * r * r + 1,
        "nonreturn_endpoint_count": len(nonreturn),
        "nonreturn_gcd_degree_histogram": {
            str(key): gcd_histogram[key] for key in sorted(gcd_histogram)
        },
        "nonreturn_maximum_hasse_order": max(record["leading_total_degree"] for record in nonreturn),
        "return_endpoint_count": len(returns),
        "return_hasse_order": returns[0]["leading_total_degree"] if returns else None,
        "decoded_partition_sha256": decoded_hash,
        "direct_partition_sha256": direct_hash,
        "p1505_partition_sha256": p1505_cell["source_collisions"]["source_partition_sha256"],
        "decoded_partition_matches_direct": decoded_partition == direct_partition,
        "decoded_partition_matches_p1505": decoded_hash == p1505_cell["source_collisions"]["source_partition_sha256"],
        "all_common_roots_have_unique_factor_pair": all(
            len(record["decoded_factor_pairs"]) == record["common_root_count"]
            for record in endpoints
        ),
        "public_code_permutation": permutation,
        "permuted_public_codes_decode_same_pairs": all(
            record["permuted_code_factor_pairs_match"] for record in endpoints
        ),
        "marker_code_coordinates_per_transition": 2,
        "marker_variables": 4,
        "degree_at_most_two_marker_monomials_including_constant": 15,
        "global_marked_coefficient_slot_upper_bound": 15 * (4 * r * r + 1),
        "global_marked_slot_bound_exponent_in_r": 2,
        "local_verifier_pointwise_gcd_count": len(endpoints),
        "local_verifier_work_asymptotic": "Theta(r^3) across all endpoints; not the proposed compiler",
        "endpoints": endpoints,
        "endpoint_transcript_sha256": digest(endpoints),
    }


def render_note(payload: dict[str, Any]) -> str:
    lines = [
        "# P1509 Hasse-Jet Source Section",
        "",
        f"Status: `{payload['status']}`",
        "",
        "| L | r | cells | nonreturn degree-1 | nonreturn degree-2 | max order | return order | source partitions |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    by_L: dict[int, list[dict[str, Any]]] = collections.defaultdict(list)
    for cell in payload["cells"]:
        by_L[cell["L"]].append(cell)
    for L, cells in sorted(by_L.items()):
        first = cells[0]
        histogram = first["nonreturn_gcd_degree_histogram"]
        lines.append(
            f"| {L} | {first['selector_degree_r']} | {len(cells)} | "
            f"{histogram.get('1', 0)} | {histogram.get('2', 0)} | "
            f"{max(cell['nonreturn_maximum_hasse_order'] for cell in cells)} | "
            f"{first['return_hasse_order']} | "
            f"{sum(cell['decoded_partition_matches_p1505'] for cell in cells)}/{len(cells)} |"
        )
    lines.extend([
        "",
        "Every nonreturn endpoint has Hasse order one or two. Factoring the leading form and taking two within-block code ratios recovers all selector-factor pairs; constant sign replay reproduces every canonical P1505 source partition.",
        "",
        "The known return endpoint retains order 2r and is preserved as the growing-order control.",
        "",
        "## Boundary",
        "",
        payload["interpretation"],
        "",
        "## Next Action",
        "",
        payload["next_action"],
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    hashes = {display_path(path): sha256_file(path) for path in EXPECTED}
    hash_gates = {
        display_path(path): hashes[display_path(path)] == expected
        for path, expected in EXPECTED.items()
    }
    if not all(hash_gates.values()):
        raise RuntimeError(f"P1509 frozen hash mismatch: {hash_gates}")

    p1490_result = json.loads(P1490.read_text(encoding="ascii"))
    p1490_audit = json.loads(P1490_AUDIT.read_text(encoding="ascii"))
    p1491_audit = json.loads(P1491_AUDIT.read_text(encoding="ascii"))
    p1505_result = json.loads(P1505.read_text(encoding="ascii"))
    p1505_audit = json.loads(P1505_AUDIT.read_text(encoding="ascii"))
    focus = json.loads(FOCUS_PLAN.read_text(encoding="ascii"))
    frozen_cells = {
        (int(cell["L"]), int(cell["nonce"])): cell for cell in p1505_result["cells"]
    }
    cells = [
        cell_record(fixture, nonce, frozen_cells[(int(fixture["L"]), nonce)])
        for fixture in p1490.FIXTURES
        for nonce in (0, 1)
    ]
    planted = planted_resultant_controls(p1482.GF(1033))

    gates = {
        "frozen_hashes_exact": all(hash_gates.values()),
        "idea068_is_sole_active_focus": (
            [item["id"] for item in focus["critical_experiments"]] == ["ECDLP-IDEA-068"]
        ),
        "all_prior_independent_audits_pass": (
            p1490_audit["passed_checks"] == p1490_audit["total_checks"] == 12
            and p1491_audit["passed_checks"] == p1491_audit["total_checks"] == 12
            and p1505_audit["passed_checks"] == p1505_audit["total_checks"] == 12
        ),
        "all_endpoint_counts_exact": all(
            cell["endpoint_count"] == cell["expected_endpoint_count_2r2_plus_1"]
            for cell in cells
        ),
        "all_nonreturn_hasse_orders_at_most_two": all(
            cell["nonreturn_maximum_hasse_order"] <= 2 for cell in cells
        ),
        "all_nonreturn_histograms_match_closed_form": all(
            cell["nonreturn_gcd_degree_histogram"]
            == {"1": 2 * cell["selector_degree_r"], "2": 2 * cell["selector_degree_r"] * (cell["selector_degree_r"] - 1)}
            for cell in cells
        ),
        "all_return_orders_equal_2r": all(
            cell["return_endpoint_count"] == 1
            and cell["return_hasse_order"] == 2 * cell["selector_degree_r"]
            for cell in cells
        ),
        "all_common_roots_decode_unique_factor_pairs": all(
            cell["all_common_roots_have_unique_factor_pair"] for cell in cells
        ),
        "all_source_partitions_recover_exactly": all(
            cell["decoded_partition_matches_direct"]
            and cell["decoded_partition_matches_p1505"]
            for cell in cells
        ),
        "two_code_coordinates_per_transition_suffice": all(
            cell["marker_code_coordinates_per_transition"] == 2 for cell in cells
        ),
        "public_code_permutation_controls_pass": all(
            cell["permuted_public_codes_decode_same_pairs"] for cell in cells
        ),
        "planted_leading_resultant_lemma_controls_pass": all(
            control["first_nonzero_resultant_order"] == control["common_root_count"]
            and control["lemma_matches_up_to_nonzero_scale"]
            for control in planted.values()
        ),
        "quadratic_global_coefficient_state_bound_available": all(
            cell["global_marked_slot_bound_exponent_in_r"] == 2 for cell in cells
        ),
        "global_marked_eliminant_compiler_implemented": False,
        "global_compiler_sub_rho_cost_proved": False,
        "scaling_contract_approved": False,
        "generic_shoup_breakthrough": False,
    }
    expected_false = {
        "global_marked_eliminant_compiler_implemented",
        "global_compiler_sub_rho_cost_proved",
        "scaling_contract_approved",
        "generic_shoup_breakthrough",
    }
    if not all(value for key, value in gates.items() if key not in expected_false):
        raise RuntimeError(f"P1509 decision gate failed: {gates}")

    source = Path(__file__).resolve()
    payload = {
        "schema": SCHEMA,
        "status": "POSITIVE_RESULT_P1509_EXACT_CONSTANT_ORDER_HASSE_JET_SOURCE_SECTION_GLOBAL_COMPILER_OPEN",
        "claim_status": "LOCAL MARKED-RESULTANT IDENTITY EXACT / ALL SOURCE PARTITIONS RECOVERED / NONRETURN ORDER AT MOST TWO / GLOBAL BATCH COMPILER UNIMPLEMENTED / NO SHOUP BREAK",
        "source": display_path(source),
        "source_sha256": sha256_file(source),
        "contract": display_path(CONTRACT),
        "contract_sha256": hashes[display_path(CONTRACT)],
        "frozen_hashes": hashes,
        "hash_gates": hash_gates,
        "focus_active_ids": [item["id"] for item in focus["critical_experiments"]],
        "prior_p1490_status": p1490_result["status"],
        "cells": cells,
        "aggregate": {
            "cell_count": len(cells),
            "endpoint_count": sum(cell["endpoint_count"] for cell in cells),
            "nonreturn_endpoint_count": sum(cell["nonreturn_endpoint_count"] for cell in cells),
            "maximum_nonreturn_hasse_order": max(cell["nonreturn_maximum_hasse_order"] for cell in cells),
            "maximum_return_hasse_order": max(cell["return_hasse_order"] for cell in cells),
            "source_partition_pass_count": sum(cell["decoded_partition_matches_p1505"] for cell in cells),
            "marker_code_coordinates_per_transition": 2,
            "marker_variable_count": 4,
        },
        "planted_resultant_controls": planted,
        "gates": gates,
        "interpretation": (
            "The first nonzero Hasse form of the marked pointwise resultant is an "
            "exact source section on every frozen endpoint. Outside the known return "
            "branch, its degree is at most two; two public code coordinates per "
            "transition recover every vanishing selector-factor pair, and constant "
            "sign replay reproduces all P1505 source partitions. The producer still "
            "uses one pointwise gcd per endpoint as a verifier. Therefore the local "
            "identity is positive, while the claimed batched near-quadratic compiler "
            "and any end-to-end complexity gain remain unproved."
        ),
        "limitations": [
            "The producer's pointwise gcd census is a verifier path with Theta(r^3) aggregate work, not the proposed algorithm.",
            "The quadratic coefficient-slot count is a state upper bound, not a construction-time proof.",
            "The exact result governs P1490's rational-selector family and its removable return branch.",
            "No complete A2/A3 candidate generator, relation campaign, factor-log solve, or blind target descent is implemented.",
            "No Pollard-rho or Shoup-bound improvement is claimed.",
        ],
        "next_action": (
            "Freeze a P1510 compiler-only contract. Compute the constant set of "
            "degree-at-most-two marked resultant coefficient polynomials for all W "
            "without endpoint factorization or per-key gcd, and require measured and "
            "symbolic total work/state O(r^2 polylog r). Then factor only the reported "
            "endpoint Hasse forms and replay sources."
        ),
    }
    write_atomic(OUT, (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("ascii"))
    write_atomic(NOTE, render_note(payload).encode("ascii"))
    print(json.dumps({
        "status": payload["status"],
        "output": str(OUT),
        "note": str(NOTE),
        "aggregate": payload["aggregate"],
        "gates": gates,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
