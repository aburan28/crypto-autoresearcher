#!/usr/bin/env sage -python
"""Test pointwise selector resultants and charge candidate generation."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import os
import time
from pathlib import Path
from typing import Any

from sage.all import PolynomialRing, matrix, vector

import p1482_coordinate_routed_wagner_tree as p1482
import p1490_rational_lift_selector_norm as p1490


ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = ROOT / "ecdlp_index_calculus_state"
RESEARCH_DIR = ROOT / "research"
CONTRACT = STATE_DIR / "experiment_contract_p1491_pointwise_selector_subresultant.md"
P1490_SOURCE = STATE_DIR / "p1490_rational_lift_selector_norm.json"
OUT = STATE_DIR / "p1491_pointwise_selector_subresultant.json"
NOTE = RESEARCH_DIR / "p1491_pointwise_selector_subresultant.md"

SCHEMA = "ecdlp.p1491_pointwise_selector_subresultant.v1"
EXPECTED = {
    CONTRACT: "740d69b3a4fe18fac492fb6c34d9126286be1d305c60e8a1b25d5a853c3cc6ab",
    ROOT / "tasks/ecdlp_index_calculus/p1490_rational_lift_selector_norm.py":
        "c68dc09ec38f6a8b9200117d60b8c649a99ad443ef24f7ef5e0e14a126e8880b",
    P1490_SOURCE: "1fbb457f642dab18cab43c69bf694f9a41b68c6ecefa365d7432e1ac7107cbab",
    STATE_DIR / "p1490_rational_lift_selector_norm_audit.json":
        "da5b6d4b194d9c03a29622ac03fe3e8c6dae33f1e99c788c46b82fb38f85fa7a",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def displacement_ranks(coefficients: Any) -> dict[str, int]:
    field = coefficients.base_ring()
    n = coefficients.nrows()
    shift = matrix(field, n, n, lambda row, column: int(row == column + 1))
    return {
        "ordinary": int(coefficients.rank()),
        "C_minus_Z_C_Zt": int((coefficients - shift * coefficients * shift.transpose()).rank()),
        "C_minus_Z_C_Z": int((coefficients - shift * coefficients * shift).rank()),
        "C_minus_Zt_C_Z": int((coefficients - shift.transpose() * coefficients * shift).rank()),
        "C_minus_Zt_C_Zt": int(
            (coefficients - shift.transpose() * coefficients * shift.transpose()).rank()
        ),
    }


def structure_cell(context: dict[str, Any], selector: Any) -> dict[str, Any]:
    fixture = context["fixture"]
    field = context["field"]
    L = int(fixture["L"])
    r = int(selector.degree())
    n = 2 * r + 1
    ring = PolynomialRing(field, names=(f"U1491_{L}", f"V1491_{L}"))
    U, V = ring.gens()
    norm = p1490.symbolic_norm(
        [int(coefficient) for coefficient in selector],
        field(fixture["a"]),
        field(fixture["b"]),
        U,
        V,
    )
    coefficient_matrix = matrix(
        field,
        n,
        n,
        lambda row, column: norm.monomial_coefficient(U**row * V**column),
    )
    shift = matrix(field, n, n, lambda row, column: int(row == column + 1))
    toeplitz_values = [
        field(p1482.digest_int("P1491", "toeplitz", L, index) % int(fixture["p"]))
        for index in range(2 * n - 1)
    ]
    toeplitz = matrix(field, n, n, lambda row, column: toeplitz_values[n - 1 + row - column])
    hankel_values = [
        field(p1482.digest_int("P1491", "hankel", L, index) % int(fixture["p"]))
        for index in range(2 * n - 1)
    ]
    hankel = matrix(field, n, n, lambda row, column: hankel_values[row + column])
    left = vector(
        field,
        [field(p1482.digest_int("P1491", "rank1-left", L, index) % int(fixture["p"])) for index in range(n)],
    )
    right = vector(
        field,
        [field(p1482.digest_int("P1491", "rank1-right", L, index) % int(fixture["p"])) for index in range(n)],
    )
    rank_one = left.column() * right.row()
    controls = {
        "toeplitz_ordinary_rank": int(toeplitz.rank()),
        "toeplitz_displacement_rank": int((toeplitz - shift * toeplitz * shift.transpose()).rank()),
        "hankel_ordinary_rank": int(hankel.rank()),
        "hankel_displacement_rank": int((hankel - shift * hankel * shift).rank()),
        "outer_product_rank": int(rank_one.rank()),
    }
    return {
        "L": L,
        "selector_degree_r": r,
        "bidegree": [int(norm.degree(U)), int(norm.degree(V))],
        "coefficient_matrix_dimension": n,
        "coefficient_support": len(norm.dict()),
        "coefficient_density": len(norm.dict()) / (n * n),
        "coefficient_sha256": hashlib.sha256(
            b"\n".join(
                repr((tuple(exponents), int(coefficient))).encode("ascii")
                for exponents, coefficient in sorted(norm.dict().items())
            )
        ).hexdigest(),
        "symmetric": norm.subs({U: V, V: U}) == norm,
        "ranks": displacement_ranks(coefficient_matrix),
        "controls": controls,
        "all_tested_norm_ranks_full": all(
            rank == n for rank in displacement_ranks(coefficient_matrix).values()
        ),
        "positive_controls_valid": (
            controls["toeplitz_displacement_rank"] <= 2
            and controls["hankel_displacement_rank"] <= 2
            and controls["outer_product_rank"] == 1
        ),
    }


def materialized_composition(
    context: dict[str, Any], selector: Any, nonce: int
) -> tuple[Any, Any, Any, Any]:
    fixture = context["fixture"]
    field = context["field"]
    L = int(fixture["L"])
    q = int(fixture["order"])
    scalar = 1 + p1482.digest_int("P1490", "public-start", L, nonce) % (q - 1)
    P = scalar * context["generator"]
    Wring = PolynomialRing(field, f"W1491_{L}_{nonce}")
    W = Wring.gen()
    Vring = PolynomialRing(Wring, f"V1491_{L}_{nonce}")
    V = Vring.gen()
    coefficients = [int(coefficient) for coefficient in selector]
    left = p1490.symbolic_norm(
        coefficients,
        field(fixture["a"]),
        field(fixture["b"]),
        Vring(field(P[0])),
        V,
    )
    right = p1490.symbolic_norm(
        coefficients,
        field(fixture["a"]),
        field(fixture["b"]),
        V,
        Vring(W),
    )
    raw = Wring(left.resultant(right))
    squarefree = (raw // raw.gcd(raw.derivative())).monic()
    return P, W, raw, squarefree


def pointwise_cell(
    context: dict[str, Any], selector: Any, nonce: int
) -> dict[str, Any]:
    started = time.perf_counter()
    fixture = context["fixture"]
    field = context["field"]
    L = int(fixture["L"])
    r = int(selector.degree())
    P, _, raw, squarefree = materialized_composition(context, selector, nonce)
    roots = sorted(int(root) for root in squarefree.roots(multiplicities=False))
    unrestricted = []
    index = 0
    root_set = set(roots)
    while len(unrestricted) < 64:
        scalar = 1 + p1482.digest_int("P1491", "unrestricted-w", L, nonce, index) % (
            int(fixture["order"]) - 1
        )
        point = scalar * context["generator"]
        w = int(point[0])
        if w not in root_set and w not in unrestricted:
            unrestricted.append(w)
        index += 1

    Vring = PolynomialRing(field, f"Vp1491_{L}_{nonce}")
    V = Vring.gen()
    coefficients = [int(coefficient) for coefficient in selector]
    a = field(fixture["a"])
    b = field(fixture["b"])
    left = p1490.symbolic_norm(coefficients, a, b, field(P[0]), V)
    decisions = []
    opened = []
    for w in roots + unrestricted:
        right = p1490.symbolic_norm(coefficients, a, b, V, Vring(field(w)))
        value = left.resultant(right)
        expected_zero = raw(field(w)) == 0
        decisions.append((w, int(value), expected_zero))
        if expected_zero and len(opened) < 8:
            witness = p1490.algebraic_two_step_source(context, selector, coefficients, P, w)
            opened.append((w, witness is not None and witness["verified"]))
    log_r = max(1, math.ceil(math.log2(max(2, 2 * r))))
    half_gcd_proxy = 32 * (2 * r) * log_r * log_r
    return {
        "L": L,
        "nonce": nonce,
        "selector_degree_r": r,
        "positive_query_count": len(roots),
        "unrestricted_false_query_count": len(unrestricted),
        "query_count": len(decisions),
        "zero_decision_mismatch_count": sum((value == 0) != expected for _, value, expected in decisions),
        "all_requested_sources_open": all(valid for _, valid in opened) and len(opened) == min(8, len(roots)),
        "opened_source_count": sum(valid for _, valid in opened),
        "decision_sha256": hashlib.sha256(
            b"\n".join(repr(row).encode("ascii") for row in decisions)
        ).hexdigest(),
        "candidate_path_materializes_composition": False,
        "verifier_path_materialized_degree": int(squarefree.degree()),
        "fast_half_gcd_field_operation_proxy_per_query": half_gcd_proxy,
        "pointwise_asymptotic": "soft-O(r) field operations per supplied w",
        "wall_seconds": time.perf_counter() - started,
    }


def source_rows(
    context: dict[str, Any], deck: list[Any], width: int
) -> list[tuple[Any, tuple[int, ...]]]:
    output = []
    for indexes in itertools.combinations_with_replacement(range(len(deck)), width):
        point = sum((deck[index] for index in indexes), context["identity"])
        output.append((point, indexes))
    return output


def candidate_generation_cell(
    context: dict[str, Any], deck: list[Any], recorded_panel: dict[str, Any]
) -> dict[str, Any]:
    started = time.perf_counter()
    fixture = context["fixture"]
    L = int(fixture["L"])
    q = int(fixture["order"])
    r = len(deck) // 2
    challenge_scalar = 1 + p1482.digest_int("P1490", "challenge", L) % (q - 1)
    challenge = challenge_scalar * context["generator"]
    pairs = source_rows(context, deck, 2)
    triples = source_rows(context, deck, 3)
    triple_points = {}
    triple_x = {}
    for point, indexes in triples:
        triple_points.setdefault(p1482.point_key(point), indexes)
        if not point.is_zero():
            triple_x.setdefault(int(point[0]), indexes)

    target_hit_count = 0
    x_intersection_hit_count = 0
    five_source_replay_failures = 0
    total_x_intersections = 0
    for target_index in range(256):
        a = p1482.digest_int("P1490", "target-a", L, target_index) % q
        b = 1 + p1482.digest_int("P1490", "target-b", L, target_index) % (q - 1)
        target = a * context["generator"] + b * challenge
        witness = None
        for pair_point, pair_indexes in pairs:
            triple_indexes = triple_points.get(p1482.point_key(target - pair_point))
            if triple_indexes is not None:
                witness = pair_indexes, triple_indexes
                break
        if witness is not None:
            target_hit_count += 1
            pair_indexes, triple_indexes = witness
            replay = sum(
                (deck[index] for index in (*pair_indexes, *triple_indexes)),
                context["identity"],
            )
            five_source_replay_failures += int(replay != target)
        A2_x = set()
        for start in (target, -target):
            for pair_point, _ in pairs:
                point = start + pair_point
                if not point.is_zero():
                    A2_x.add(int(point[0]))
        intersections = A2_x.intersection(triple_x)
        total_x_intersections += len(intersections)
        x_intersection_hit_count += int(bool(intersections))

    average_A2_root_proxy = min(q, 2 * r * r + 1)
    sampling_tests_per_relation_proxy = q / average_A2_root_proxy
    pointwise_cost_per_relation_proxy = sampling_tests_per_relation_proxy * max(
        1, r * math.log2(max(2, r)) ** 2
    )
    return {
        "L": L,
        "selector_degree_r": r,
        "deck_size": len(deck),
        "pair_source_count": len(pairs),
        "triple_source_count": len(triples),
        "distinct_A3_point_count": len(triple_points),
        "distinct_A3_x_count": len(triple_x),
        "frozen_target_count": 256,
        "five_source_target_hit_count": target_hit_count,
        "x_support_intersection_hit_count": x_intersection_hit_count,
        "total_x_support_intersection_count": total_x_intersections,
        "matches_P1490_relation_hit_count": target_hit_count == int(recorded_panel["target_hit_count"]),
        "all_five_sources_replay": five_source_replay_failures == 0,
        "five_source_replay_failure_count": five_source_replay_failures,
        "sampling_strategy": {
            "A2_root_count_proxy": average_A2_root_proxy,
            "expected_A3_samples_per_relation_proxy": sampling_tests_per_relation_proxy,
            "pointwise_field_operation_proxy_per_relation": pointwise_cost_per_relation_proxy,
            "asymptotic": "soft-O(r^4) per relation when q=Theta(r^5)",
        },
        "exact_support_strategy": {
            "A3_precomputation_asymptotic": "Theta(r^3)",
            "A2_per_target_asymptotic": "Theta(r^2)",
            "complete_relation_campaign_asymptotic": "Theta(r^3)=Theta(q^(3/5))",
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
        "# P1491 pointwise selector subresultant",
        "",
        "## Status",
        "",
        f"`{payload['status']}`",
        "",
        "| L | r | norm rank | displacement ranks | A3 sources | P1490 hits |",
        "|---:|---:|---:|---|---:|---:|",
    ]
    candidates = {cell["L"]: cell for cell in payload["candidate_generation_cells"]}
    for cell in payload["structure_cells"]:
        ranks = cell["ranks"]
        displacement = [
            ranks["C_minus_Z_C_Zt"],
            ranks["C_minus_Z_C_Z"],
            ranks["C_minus_Zt_C_Z"],
            ranks["C_minus_Zt_C_Zt"],
        ]
        candidate = candidates[cell["L"]]
        lines.append(
            f"| {cell['L']} | {cell['selector_degree_r']} | {ranks['ordinary']} | "
            f"{displacement} | {candidate['triple_source_count']} | "
            f"{candidate['five_source_target_hit_count']} |"
        )
    lines.extend([
        "",
        "Every supplied composition point is decided exactly without materializing",
        "the dense composition polynomial, and zero sources open algebraically.",
        "The norm matrices and all four tested displacements are nevertheless full",
        "rank. Supplying complete candidates retains either a soft-O(r^4) sampling",
        "route or the exact Theta(r^3)=Theta(q^(3/5)) support route, both above rho.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    frozen = {}
    for path, expected in EXPECTED.items():
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"P1491 frozen hash mismatch for {path}: {actual} != {expected}")
        frozen[str(path.relative_to(ROOT))] = actual
    p1490_source = json.loads(P1490_SOURCE.read_text(encoding="utf-8"))
    recorded_panels = {int(cell["L"]): cell for cell in p1490_source["relation_controls"]}

    structure_cells = []
    pointwise_cells = []
    candidate_cells = []
    for fixture in p1482.FIXTURES:
        context = p1482.build_context(fixture)
        selector, roots, _ = p1490.selector_cell(context)
        _, deck = p1490.selector_deck(context, roots)
        structure_cells.append(structure_cell(context, selector))
        for nonce in range(2):
            pointwise_cells.append(pointwise_cell(context, selector, nonce))
        candidate_cells.append(candidate_generation_cell(context, deck, recorded_panels[int(fixture["L"])]))

    structure_full = all(
        cell["all_tested_norm_ranks_full"] and cell["positive_controls_valid"]
        for cell in structure_cells
    )
    pointwise_exact = all(
        cell["zero_decision_mismatch_count"] == 0 and cell["all_requested_sources_open"]
        for cell in pointwise_cells
    )
    candidates_exact = all(
        cell["matches_P1490_relation_hit_count"] and cell["all_five_sources_replay"]
        for cell in candidate_cells
    )
    status = (
        "MIXED_RESULT_P1491_SOFT_LINEAR_POINTWISE_RESULTANT_FULL_DISPLACEMENT_AND_CANDIDATE_FLOOR"
        if structure_full and pointwise_exact and candidates_exact
        else "NEGATIVE_RESULT_P1491_POINTWISE_OR_CANDIDATE_REPLAY_FAILED"
    )
    payload = {
        "boundary": {
            "candidate_vs_verified": (
                "The candidate computes only a supplied-w resultant/gcd. Materialized roots and A2/A3 supports are verifier-only."
            ),
            "closed": (
                "The exact rational-selector norm plus ordinary low-rank/displacement batching or supplied-w sampling as a complete below-rho relation backend."
            ),
            "not_closed": (
                "A different factor base or correspondence that supplies a smaller complete candidate set before the pointwise oracle."
            ),
            "pollard_rho": (
                "Exact support costs q^(3/5); sampling plus pointwise resultants is asymptotically worse."
            ),
        },
        "candidate_generation_cells": candidate_cells,
        "frozen_files": frozen,
        "gates": {
            "norm_coefficient_and_displacement_ranks_full": structure_full,
            "pointwise_zero_and_source_operator_exact": pointwise_exact,
            "candidate_support_replays_P1490": candidates_exact,
            "public_candidate_generator_complete_below_L_three_halves": False,
            "complete_campaign_below_pollard_rho": False,
            "pointwise_subresultant_relation_signal": False,
        },
        "next_action": (
            "Close this exact multiplicative-subgroup selector-norm representation. "
            "P1492 must change the factor-base geometry or correspondence so the complete candidate support is below quadratic before reusing the pointwise primitive."
        ),
        "pointwise_cells": pointwise_cells,
        "schema": SCHEMA,
        "status": status,
        "structure_cells": structure_cells,
    }
    write_atomic(OUT, (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    write_atomic(NOTE, render_note(payload).encode("utf-8"))
    print(json.dumps({
        "status": status,
        "gates": payload["gates"],
        "structure": [
            [cell["L"], cell["selector_degree_r"], cell["ranks"]]
            for cell in structure_cells
        ],
        "pointwise_queries": [
            [cell["L"], cell["nonce"], cell["query_count"], cell["zero_decision_mismatch_count"]]
            for cell in pointwise_cells
        ],
        "candidate_hits": [
            [cell["L"], cell["five_source_target_hit_count"], cell["triple_source_count"]]
            for cell in candidate_cells
        ],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
