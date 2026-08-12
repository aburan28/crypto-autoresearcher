#!/usr/bin/env sage -python
"""Derive IDEA-053 endpoint moments and test exact source-tag recovery."""

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
CONTRACT = STATE / "experiment_contract_p1505_endpoint_moment_source_tag_gate.md"
P1490_SOURCE = ROOT / "tasks/ecdlp_index_calculus/p1490_rational_lift_selector_norm.py"
P1490_RESULT = STATE / "p1490_rational_lift_selector_norm.json"
P1490_AUDIT = STATE / "p1490_rational_lift_selector_norm_audit.json"
P1491_SOURCE = ROOT / "tasks/ecdlp_index_calculus/p1491_pointwise_selector_subresultant.py"
P1491_RESULT = STATE / "p1491_pointwise_selector_subresultant.json"
P1491_AUDIT = STATE / "p1491_pointwise_selector_subresultant_audit.json"
IDEA = Path(
    "/Volumes/Volume/crypto-autoresearcher/ideas/deferred/"
    "ECDLP-IDEA-053_aggregate_moment_large_prime_decoder_hypothesis.md"
)
DERIVATION = Path(
    "/Volumes/Volume/crypto-autoresearcher/ideas/artifacts/"
    "ECDLP-IDEA-053/endpoint_moment_identity.md"
)
FOCUS_QUEUE = Path(
    "/Volumes/Volume/crypto-autoresearcher/focus/archive/"
    "focus_queue_idea053_active.json"
)
FOCUS_PLAN = Path(
    "/Volumes/Volume/crypto-autoresearcher/focus/archive/"
    "focus_plan_idea053_active.json"
)
OUT = STATE / "p1505_endpoint_moment_source_tag_gate.json"
NOTE = RESEARCH / "p1505_endpoint_moment_source_tag_gate.md"

SCHEMA = "ecdlp.p1505_endpoint_moment_source_tag_gate.v1"
EXPECTED = {
    CONTRACT: "b256508f9e08fa8d14bc0d4f266e1db55c55016fb4cdb7b95a7bf8e67f085979",
    P1490_SOURCE: "c68dc09ec38f6a8b9200117d60b8c649a99ad443ef24f7ef5e0e14a126e8880b",
    P1490_RESULT: "1fbb457f642dab18cab43c69bf694f9a41b68c6ecefa365d7432e1ac7107cbab",
    P1490_AUDIT: "da5b6d4b194d9c03a29622ac03fe3e8c6dae33f1e99c788c46b82fb38f85fa7a",
    P1491_SOURCE: "e1220bd3add9e1cd7dac61fdd26434fefc4c5273962283cb3564471a40fe80c0",
    P1491_RESULT: "26fc025c2de2c8ce331bacc8e556d47557159eea755fbc4e86d87da2d1d483be",
    P1491_AUDIT: "31b1c95e09addd661e693d88fbdce2e1589fec47c7752e20b69f0bd7e0db6bc4",
    IDEA: "9c6b48918bfbf2fe4aeb0c6a04cd93d97ec9856482d932e7531906a19c1e4d35",
    DERIVATION: "7268920899c4ce4c88a791dc19b317101ca3dcc711d593d1b7a51d802186ce4c",
    FOCUS_QUEUE: "0e32ed4c73bc5d74cfde27caa126737383b63604fb8d363e30aeb963b4ca7473",
    FOCUS_PLAN: "a97caa2c78518af1f823e971b7302b4c53bd57a0f77f1940409e8cf29a7f8cc5",
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


def coefficient_hash(polynomial: Any) -> str:
    return hashlib.sha256(
        b"|".join(str(int(coefficient)).encode("ascii") for coefficient in polynomial)
    ).hexdigest()


def newton_moments(polynomial: Any, count: int = 4) -> list[Any]:
    degree = int(polynomial.degree())
    if polynomial[degree] != 1:
        raise ValueError("Newton input must be monic")
    leading = [polynomial[degree - index] for index in range(1, count + 1)]
    moments = []
    for order in range(1, count + 1):
        recurrence = sum(
            leading[index - 1] * moments[order - index - 1]
            for index in range(1, order)
        )
        moments.append(-(recurrence + order * leading[order - 1]))
    return moments


def direct_moments(roots: list[Any], count: int = 4) -> list[Any]:
    return [sum(root**order for root in roots) for order in range(1, count + 1)]


def point_key(point: Any) -> tuple[int, int]:
    return (int(point[0]), int(point[1]))


def source_collision_record(context: dict[str, Any], deck: list[Any], start: Any) -> dict[str, Any]:
    by_x: dict[int, list[tuple[int, int, int]]] = collections.defaultdict(list)
    for start_sign, signed_start in ((1, start), (-1, -start)):
        for first_index, first in enumerate(deck):
            for second_index, second in enumerate(deck):
                endpoint = signed_start + first + second
                if endpoint.is_zero():
                    continue
                by_x[int(endpoint[0])].append((start_sign, first_index, second_index))

    canonical_by_x = {
        endpoint_x: sorted({
            (start_sign, min(first, second), max(first, second))
            for start_sign, first, second in sources
        })
        for endpoint_x, sources in by_x.items()
    }
    first_assignment = [
        [endpoint_x, list(canonical_by_x[endpoint_x][0])]
        for endpoint_x in sorted(canonical_by_x)
    ]
    last_assignment = [
        [endpoint_x, list(canonical_by_x[endpoint_x][-1])]
        for endpoint_x in sorted(canonical_by_x)
    ]
    raw_histogram = collections.Counter(len(sources) for sources in by_x.values())
    canonical_histogram = collections.Counter(len(sources) for sources in canonical_by_x.values())
    return {
        "deck_size": len(deck),
        "raw_signed_ordered_source_count": sum(len(sources) for sources in by_x.values()),
        "distinct_endpoint_x_count": len(by_x),
        "raw_multiplicity_histogram": {
            str(key): value for key, value in sorted(raw_histogram.items())
        },
        "raw_maximum_multiplicity": max(map(len, by_x.values())),
        "canonical_unordered_source_count": sum(map(len, canonical_by_x.values())),
        "canonical_multiplicity_histogram": {
            str(key): value for key, value in sorted(canonical_histogram.items())
        },
        "canonical_maximum_multiplicity": max(map(len, canonical_by_x.values())),
        "endpoint_x_with_multiple_canonical_sources": sum(
            len(sources) > 1 for sources in canonical_by_x.values()
        ),
        "all_endpoint_x_source_ambiguous": all(
            len(sources) > 1 for sources in canonical_by_x.values()
        ),
        "source_partition_sha256": digest([
            [endpoint_x, [list(tag) for tag in canonical_by_x[endpoint_x]]]
            for endpoint_x in sorted(canonical_by_x)
        ]),
        "first_assignment_sha256": digest(first_assignment),
        "last_assignment_sha256": digest(last_assignment),
        "assignment_difference_count": sum(
            first != last
            for first, last in zip(first_assignment, last_assignment)
        ),
        "assignments_have_identical_endpoint_keys": [
            row[0] for row in first_assignment
        ] == [row[0] for row in last_assignment],
        "endpoint_keys": sorted(by_x),
    }


def reconstruct_cell(
    fixture: dict[str, Any],
    nonce: int,
    frozen_record: dict[str, Any],
) -> dict[str, Any]:
    context = p1482.build_context(fixture)
    selector, roots, _ = p1490.selector_cell(context)
    _, deck = p1490.selector_deck(context, roots)
    field = context["field"]
    L = int(fixture["L"])
    order = int(fixture["order"])
    scalar = 1 + p1482.digest_int("P1490", "public-start", L, nonce) % (order - 1)
    start = scalar * context["generator"]
    u = field(start[0])
    coefficients = [int(coefficient) for coefficient in selector]
    wring = PolynomialRing(field, f"W1505_{L}_{nonce}")
    W = wring.gen()
    vring = PolynomialRing(wring, f"V1505_{L}_{nonce}")
    V = vring.gen()
    a = field(fixture["a"])
    b = field(fixture["b"])
    left = p1490.symbolic_norm(coefficients, a, b, vring(u), V)
    right = p1490.symbolic_norm(coefficients, a, b, V, vring(W))
    raw = wring(left.resultant(right))
    repeated = raw.gcd(raw.derivative())
    squarefree = (raw // repeated).monic()
    root_values = sorted(squarefree.roots(multiplicities=False), key=int)
    moments_from_coefficients = newton_moments(squarefree)
    moments_from_roots = direct_moments(root_values)
    collision = source_collision_record(context, deck, start)
    r = int(selector.degree())
    degree = int(squarefree.degree())
    coefficient_count = degree + 1
    nonzero_coefficient_count = sum(coefficient != 0 for coefficient in squarefree)
    return {
        "L": L,
        "nonce": nonce,
        "p": int(fixture["p"]),
        "order": order,
        "selector_degree_r": r,
        "public_start": p1482.point_json(start),
        "squarefree_degree": degree,
        "expected_squarefree_degree_2r2_plus_1": 2 * r * r + 1,
        "squarefree_coefficient_count": coefficient_count,
        "squarefree_nonzero_coefficient_count": nonzero_coefficient_count,
        "squarefree_dense": nonzero_coefficient_count == coefficient_count,
        "squarefree_coefficient_sha256": coefficient_hash(squarefree),
        "p1490_degree_matches": degree == frozen_record["squarefree_resultant"]["degree"],
        "p1490_coefficient_hash_matches": (
            coefficient_hash(squarefree)
            == frozen_record["squarefree_resultant"]["coefficient_sha256"]
        ),
        "root_count": len(root_values),
        "p1490_root_count_matches": len(root_values) == frozen_record["base_field_root_count"],
        "root_sha256": digest([int(root) for root in root_values]),
        "leading_coefficients_c1_through_c4": [
            int(squarefree[degree - index]) for index in range(1, 5)
        ],
        "moments_from_coefficients_s1_through_s4": [
            int(value) for value in moments_from_coefficients
        ],
        "moments_from_roots_s1_through_s4": [int(value) for value in moments_from_roots],
        "newton_moments_match_direct_roots": moments_from_coefficients == moments_from_roots,
        "source_collisions": collision,
        "endpoint_keys_match_polynomial_roots": collision["endpoint_keys"]
        == [int(root) for root in root_values],
        "source_opening_all_keys_r_times_d": r * degree,
        "source_opening_formula_matches": r * degree == 2 * r**3 + r,
        "dense_state_dimension": degree,
        "moment_route_avoids_dense_pair_state": False,
        "endpoint_moments_determine_source_assignment": False,
    }


def planted_control() -> dict[str, Any]:
    field = p1482.GF(1033)
    ring = PolynomialRing(field, "Z1505_control")
    Z = ring.gen()
    roots = [field(value) for value in (1, 2, 4, 8)]
    polynomial = ring.one()
    for root in roots:
        polynomial *= Z - root
    polynomial = polynomial.monic()
    coefficient_moments = newton_moments(polynomial)
    root_moments = direct_moments(roots)
    return {
        "p": 1033,
        "roots": [int(root) for root in roots],
        "polynomial_coefficients": [int(value) for value in polynomial],
        "moments_from_coefficients": [int(value) for value in coefficient_moments],
        "moments_from_roots": [int(value) for value in root_moments],
        "passes": coefficient_moments == root_moments,
    }


def render_note(payload: dict[str, Any]) -> str:
    lines = [
        "# P1505 Endpoint-Moment And Source-Tag Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Exact Cell Results",
        "",
        "| L | nonce | r | endpoint degree | coefficients | raw sources | canonical sources | ambiguous x | all-key opening |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for cell in payload["cells"]:
        collision = cell["source_collisions"]
        lines.append(
            f"| {cell['L']} | {cell['nonce']} | {cell['selector_degree_r']} | "
            f"{cell['squarefree_degree']} | {cell['squarefree_nonzero_coefficient_count']} | "
            f"{collision['raw_signed_ordered_source_count']} | "
            f"{collision['canonical_unordered_source_count']} | "
            f"{collision['endpoint_x_with_multiple_canonical_sources']} | "
            f"{cell['source_opening_all_keys_r_times_d']} |"
        )
    lines.extend([
        "",
        "The first four Newton moments equal direct root moments in every cell. The exact positive identity is retained, but it is computed from P1490's dense degree-2r^2+1 endpoint object.",
        "",
        "Every endpoint x-coordinate has multiple canonical source tags. Two deterministic complete source assignments differ at every key while sharing all endpoint moments, so untagged moments cannot emit relation rows.",
        "",
        "## Interpretation",
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
        raise RuntimeError(f"P1505 frozen hash mismatch: {hash_gates}")

    p1490_result = json.loads(P1490_RESULT.read_text(encoding="ascii"))
    p1490_audit = json.loads(P1490_AUDIT.read_text(encoding="ascii"))
    p1491_result = json.loads(P1491_RESULT.read_text(encoding="ascii"))
    p1491_audit = json.loads(P1491_AUDIT.read_text(encoding="ascii"))
    focus = json.loads(FOCUS_PLAN.read_text(encoding="ascii"))
    active_ids = [item["id"] for item in focus["critical_experiments"]]

    frozen_by_key = {
        (cell["L"], cell["nonce"]): cell
        for cell in p1490_result["composition_cells"]
    }
    cells = []
    for fixture in p1490.FIXTURES:
        for nonce in p1490.COMPOSITION_NONCES:
            cells.append(reconstruct_cell(
                fixture,
                nonce,
                frozen_by_key[(int(fixture["L"]), int(nonce))],
            ))

    control = planted_control()
    gates = {
        "frozen_hashes_exact": all(hash_gates.values()),
        "idea053_is_sole_active_focus": active_ids == ["ECDLP-IDEA-053"],
        "predecessor_audits_pass": (
            p1490_audit["passed_checks"] == p1490_audit["total_checks"] == 12
            and p1491_audit["passed_checks"] == p1491_audit["total_checks"] == 12
        ),
        "planted_newton_control_passes": control["passes"],
        "all_newton_moments_match_direct_roots": all(
            cell["newton_moments_match_direct_roots"] for cell in cells
        ),
        "all_p1490_endpoint_objects_replay": all(
            cell["p1490_degree_matches"]
            and cell["p1490_coefficient_hash_matches"]
            and cell["p1490_root_count_matches"]
            and cell["endpoint_keys_match_polynomial_roots"]
            for cell in cells
        ),
        "all_endpoint_objects_dense_degree_2r2_plus_1": all(
            cell["squarefree_degree"] == cell["expected_squarefree_degree_2r2_plus_1"]
            and cell["squarefree_dense"]
            for cell in cells
        ),
        "every_endpoint_x_has_multiple_canonical_sources": all(
            cell["source_collisions"]["all_endpoint_x_source_ambiguous"]
            for cell in cells
        ),
        "distinct_source_assignments_share_all_endpoint_keys": all(
            cell["source_collisions"]["assignment_difference_count"]
            == cell["squarefree_degree"]
            and cell["source_collisions"]["assignments_have_identical_endpoint_keys"]
            for cell in cells
        ),
        "all_key_opening_restores_exact_r3_formula": all(
            cell["source_opening_formula_matches"] for cell in cells
        ),
        "p1491_supplied_endpoint_primitive_exact_but_campaign_above_rho": (
            p1491_result["gates"]["pointwise_zero_and_source_operator_exact"]
            and not p1491_result["gates"]["complete_campaign_below_pollard_rho"]
        ),
        "implicit_source_tag_moment_oracle_established": False,
        "generic_shoup_breakthrough": False,
    }
    required_true = {
        key: value
        for key, value in gates.items()
        if key not in {"implicit_source_tag_moment_oracle_established", "generic_shoup_breakthrough"}
    }
    if not all(required_true.values()):
        raise RuntimeError(f"P1505 decision gate failed: {gates}")

    source = Path(__file__).resolve()
    payload = {
        "schema": SCHEMA,
        "status": "NEGATIVE_RESULT_P1505_EXACT_MOMENTS_DENSE_STATE_AND_SOURCE_TAG_COLLISION",
        "claim_status": "NEWTON MOMENTS EXACT / DENSE P1490 OBJECT REQUIRED / SOURCE TAGS ERASED / ALL-KEY OPENING R3 / NO BREAKTHROUGH",
        "source": display_path(source),
        "source_sha256": sha256_file(source),
        "contract": display_path(CONTRACT),
        "contract_sha256": hashes[display_path(CONTRACT)],
        "frozen_hashes": hashes,
        "hash_gates": hash_gates,
        "focus_active_ids": active_ids,
        "cells": cells,
        "controls": {"planted_newton_polynomial": control},
        "aggregate": {
            "cell_count": len(cells),
            "moment_orders_verified": [1, 2, 3, 4],
            "all_moment_identities_exact": all(
                cell["newton_moments_match_direct_roots"] for cell in cells
            ),
            "endpoint_degrees": [cell["squarefree_degree"] for cell in cells],
            "raw_source_counts": [
                cell["source_collisions"]["raw_signed_ordered_source_count"] for cell in cells
            ],
            "canonical_source_counts": [
                cell["source_collisions"]["canonical_unordered_source_count"] for cell in cells
            ],
            "ambiguous_endpoint_x_counts": [
                cell["source_collisions"]["endpoint_x_with_multiple_canonical_sources"]
                for cell in cells
            ],
            "all_key_opening_costs_r_times_d": [
                cell["source_opening_all_keys_r_times_d"] for cell in cells
            ],
            "asymptotic_endpoint_degree": "2*r^2+1",
            "asymptotic_raw_signed_ordered_sources": "8*r^2",
            "asymptotic_canonical_unordered_sources": "2*r*(2*r+1)",
            "asymptotic_existing_all_key_source_opening": "soft-O(r^3)=q^(3/5+o(1))",
        },
        "gates": gates,
        "interpretation": (
            "Newton identities provide exact endpoint moments without factoring after "
            "the polynomial is known, but the accepted FFE constructs that polynomial "
            "as P1490's dense degree-2r^2+1 pair object. Squarefree elimination retains "
            "endpoint x keys while erasing source multiplicity: every key has multiple "
            "canonical deck-pair sources, and different complete source assignments have "
            "identical endpoint moments. Opening all decoded keys with P1491's exact "
            "soft-linear supplied-w primitive restores soft-O(r^3)=q^(3/5+o(1)) work."
        ),
        "limitations": [
            "The exact Newton identities remain reusable if a new source-labelled factored algebra is found.",
            "The negative closes untagged moments of P1490's squarefree endpoint resultant, not all bivariate or module-valued moment constructions.",
            "The source collision certificate concerns endpoint x keys; an explicit collision-safe tag algebra could change the representation but must charge its state and decoder.",
            "No large-prime cycle, relation-rank, target-descent, rho, or Shoup improvement is claimed.",
        ],
        "next_action": (
            "Close IDEA-053's current untagged-resultant formulation. A successor is "
            "admissible only after naming a source-labelled factored algebra whose first "
            "2k moments are computed before quadratic pair materialization and whose "
            "decoder returns replayable source rows without per-key gcd opening."
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
