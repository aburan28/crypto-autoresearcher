#!/usr/bin/env sage -python
"""Test two explicit IDEA-059 Cremona candidates before scaling."""

from __future__ import annotations

import hashlib
import json
import os
import random
from pathlib import Path
from typing import Any

from sage.all import EllipticCurve, FractionField, GF, Matrix, PolynomialRing, ZZ, matrix, prod, vector


ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "ecdlp_index_calculus_state"
RESEARCH = ROOT / "research"
CONTRACT = STATE / "experiment_contract_p1503_cremona_toric_derivation_gate.md"
P1490 = STATE / "p1490_rational_lift_selector_norm.json"
P1490_AUDIT = STATE / "p1490_rational_lift_selector_norm_audit.json"
P1492_CONTRACT = STATE / "experiment_contract_p1492_polyhedral_semaev_squareup.md"
P1492_SOURCE = ROOT / "tasks/ecdlp_index_calculus/p1492_polyhedral_semaev_squareup.py"
P1492 = STATE / "p1492_polyhedral_semaev_squareup.json"
P1492_AUDIT_SOURCE = ROOT / "tasks/ecdlp_index_calculus/p1492_polyhedral_semaev_squareup_audit.py"
P1492_AUDIT = STATE / "p1492_polyhedral_semaev_squareup_audit.json"
IDEA = Path(
    "/Volumes/Volume/crypto-autoresearcher/ideas/"
    "ECDLP-IDEA-059_cremona_shrunk_toric_decomposition_hypothesis.md"
)
IDEA_CONTRACT = Path(
    "/Volumes/Volume/crypto-autoresearcher/ideas/contracts/"
    "ECDLP-EXP-CONTRACT-059_cremona_toric_preflight.yaml"
)
DERIVATION = Path(
    "/Volumes/Volume/crypto-autoresearcher/ideas/artifacts/"
    "ECDLP-IDEA-059/cremona_map_derivation.md"
)
FOCUS_QUEUE = Path(
    "/Volumes/Volume/crypto-autoresearcher/focus/archive/focus_queue_idea059_active.json"
)
FOCUS_PLAN = Path(
    "/Volumes/Volume/crypto-autoresearcher/focus/archive/focus_plan_idea059_active.json"
)
OUT = STATE / "p1503_cremona_toric_derivation_gate.json"
NOTE = RESEARCH / "p1503_cremona_toric_derivation_gate.md"

SCHEMA = "ecdlp.p1503_cremona_toric_derivation_gate.v1"
EXPECTED = {
    CONTRACT: "2b908b61a2210ea3e2411105a98bbbd86989713e5ce13f5e8a0d271a965ef4f5",
    P1490: "1fbb457f642dab18cab43c69bf694f9a41b68c6ecefa365d7432e1ac7107cbab",
    P1490_AUDIT: "da5b6d4b194d9c03a29622ac03fe3e8c6dae33f1e99c788c46b82fb38f85fa7a",
    P1492_CONTRACT: "a3cefaca9bacdb3c590844e0d0ffe858dfac3eaaea566d18b73e0aea7158a600",
    P1492_SOURCE: "1d200bd68be8ea806652031e11415335e914bf8c8bd11ceabccabb002a00766f",
    P1492: "01240d8fb3ea1d0b53638daeca2ff7f7b5b9288e5bb47d3a564b4257304f4dc9",
    P1492_AUDIT_SOURCE: "4ed94be50b8f7164f17d9db8d401f3b8dd446be3f03b300f519fc61e9f4a375e",
    P1492_AUDIT: "5c9747b1cd88527a1f80d4d1abdb4b207eeef3bc7bd0952b4216594ca93f2c48",
    IDEA: "efda54f07e05effab4ad6a1f02ba25a60f44d2c7e49b53bc711bd6649066a3f9",
    IDEA_CONTRACT: "bb5116ac6982506f963a4e2f3259856bbbc683a19830b8f64584a07158a61e6c",
    DERIVATION: "21e8c1adfa5aa6d46dd5b4206ac63b5a8b0bea01e203bf902e9a6b34a11c25b1",
    FOCUS_QUEUE: "0bafc9aa565b2bae495dbe4c5edc8e73d6606c58753747c93a7b74f7dca5925d",
    FOCUS_PLAN: "0dd808bfa54fe27324be01408282f26c93a266373343302a3d758087328e916f",
}


def compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


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


def semaev_s3(u: Any, v: Any, w: Any, curve_a: Any, curve_b: Any) -> Any:
    return (
        (u - v) ** 2 * w**2
        - 2 * ((u + v) * (u * v + curve_a) + 2 * curve_b) * w
        + (u * v - curve_a) ** 2
        - 4 * curve_b * (u + v)
    )


def build_s4(field: Any, curve_a: Any, curve_b: Any, target_x: Any) -> tuple[Any, Any]:
    ambient = PolynomialRing(field, ("x1", "x2", "x3", "xq", "z"))
    x1, x2, x3, xq, z = ambient.gens()
    left = semaev_s3(x1, x2, z, curve_a, curve_b)
    right = semaev_s3(x3, xq, z, curve_a, curve_b)
    eliminated = ambient(left.resultant(right, z)).subs({xq: target_x})
    ring = PolynomialRing(field, ("x1", "x2", "x3"), order="degrevlex")
    generators = ring.gens()
    return ring(eliminated.subs({
        x1: generators[0],
        x2: generators[1],
        x3: generators[2],
    })), ring


def symmetric_rewrite(s4: Any, ring: Any, seed: int) -> tuple[Any, Any, str]:
    field = ring.base_ring()
    p = int(field.characteristic())
    symmetric_ring = PolynomialRing(field, ("e1", "e2", "e3"))
    e1, e2, e3 = symmetric_ring.gens()
    monomial_exponents = [
        (i, j, k)
        for i in range(13)
        for j in range(7)
        for k in range(5)
        if i + 2 * j + 3 * k <= 12
    ]
    rng = random.Random(seed)
    rows = []
    values = []
    required = len(monomial_exponents) + 32
    while len(rows) < required:
        xs = [field(rng.randrange(p)) for _ in range(3)]
        invariants = (
            sum(xs),
            xs[0] * xs[1] + xs[0] * xs[2] + xs[1] * xs[2],
            prod(xs),
        )
        rows.append([
            invariants[0] ** i * invariants[1] ** j * invariants[2] ** k
            for i, j, k in monomial_exponents
        ])
        values.append(s4(*xs))
    sample_matrix = matrix(field, rows)
    if sample_matrix.rank() != len(monomial_exponents):
        raise RuntimeError("symmetric interpolation matrix is rank deficient")
    coefficients = sample_matrix.solve_right(vector(field, values))
    rewritten = sum(
        coefficients[index] * e1**i * e2**j * e3**k
        for index, (i, j, k) in enumerate(monomial_exponents)
        if coefficients[index]
    )
    transcript = [
        [list(map(int, exponent)), int(coefficients[index])]
        for index, exponent in enumerate(monomial_exponents)
        if coefficients[index]
    ]
    return rewritten, symmetric_ring, hashlib.sha256(compact(transcript).encode("ascii")).hexdigest()


def generic_e3_factorization(rewritten: Any, symmetric_ring: Any) -> tuple[Any, list[list[int]]]:
    field = symmetric_ring.base_ring()
    e1, e2, e3 = symmetric_ring.gens()
    base = PolynomialRing(field, ("u", "v"))
    u, v = base.gens()
    specialization = symmetric_ring.hom([u, v, base(0)], base)
    fraction_field = FractionField(base)
    univariate = PolynomialRing(fraction_field, "T")
    T = univariate.gen()
    coefficients = rewritten.polynomial(e3).list()
    polynomial = sum(
        fraction_field(specialization(coefficients[index])) * T**index
        for index in range(len(coefficients))
    )
    factors = [[int(factor.degree()), int(multiplicity)] for factor, multiplicity in polynomial.factor()]
    return polynomial, factors


def point_tuple_record(points: tuple[Any, Any, Any, Any]) -> dict[str, Any]:
    def raw(point: Any) -> list[int] | None:
        if point.is_zero():
            return None
        return [int(point[0]), int(point[1])]
    return {"points": [raw(point) for point in points]}


def render_note(payload: dict[str, Any]) -> str:
    lines = [
        "# P1503 Cremona-Toric Derivation Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Candidate Decisions",
        "",
        f"The summation-coordinate map has generic inverse degree "
        f"`{payload['candidate_A_summation_coordinate']['generic_inverse_degree']}` and is not birational.",
        "",
        "The elliptic group-addition map is a determinant-one automorphism and all tuple/inverse controls pass, but its direct and transformed source-complete mixed volumes are equal:",
        "",
        "| L | r | direct | transformed | strict drop |",
        "|---:|---:|---:|---:|---:|",
    ]
    for record in payload["candidate_B_group_addition"]["fixture_volume_records"]:
        lines.append(
            f"| {record['L']} | {record['r']} | {record['direct_mixed_volume']} | "
            f"{record['transformed_mixed_volume']} | {str(record['strict_drop']).lower()} |"
        )
    lines.extend([
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
        raise RuntimeError(f"P1503 frozen hash mismatch: {hash_gates}")

    p1490 = json.loads(P1490.read_text(encoding="ascii"))
    p1490_audit = json.loads(P1490_AUDIT.read_text(encoding="ascii"))
    p1492 = json.loads(P1492.read_text(encoding="ascii"))
    p1492_audit = json.loads(P1492_AUDIT.read_text(encoding="ascii"))
    focus = json.loads(FOCUS_PLAN.read_text(encoding="ascii"))
    active = [item["id"] for item in focus["critical_experiments"]]

    fixture = p1490["selector_cells"][0]["fixture"]
    composition = next(
        cell for cell in p1490["composition_cells"]
        if cell["L"] == fixture["L"] and cell["nonce"] == 0
    )
    field = GF(fixture["p"])
    curve = EllipticCurve(field, [field(fixture["a"]), field(fixture["b"])])
    if int(curve.order()) != fixture["order"]:
        raise RuntimeError("frozen curve order mismatch")
    target = curve((composition["public_start"]["x"], composition["public_start"]["y"]))

    s4, x_ring = build_s4(field, field(fixture["a"]), field(fixture["b"]), target[0])
    rewritten, symmetric_ring, rewrite_hash = symmetric_rewrite(s4, x_ring, 2026071759)
    holdout_rng = random.Random(2026071760)
    holdout_matches = 0
    x1, x2, x3 = x_ring.gens()
    e1, e2, e3 = symmetric_ring.gens()
    for _ in range(64):
        xs = [field(holdout_rng.randrange(int(field.characteristic()))) for _ in range(3)]
        invariants = (
            sum(xs),
            xs[0] * xs[1] + xs[0] * xs[2] + xs[1] * xs[2],
            prod(xs),
        )
        if s4(*xs) == rewritten(*invariants):
            holdout_matches += 1
    generic_polynomial, factor_degrees = generic_e3_factorization(rewritten, symmetric_ring)

    transform_matrix = Matrix(ZZ, [
        [1, 0, 0, 0],
        [1, 1, 0, 0],
        [0, 0, 1, 0],
        [1, 1, 1, 1],
    ])
    expected_inverse = Matrix(ZZ, [
        [1, 0, 0, 0],
        [-1, 1, 0, 0],
        [0, 0, 1, 0],
        [0, -1, -1, 1],
    ])
    generator = curve.gens()[0]
    zero = curve(0)
    tuples = [
        (zero, zero, zero, zero),
        (generator, -generator, 2 * generator, -2 * generator),
        (generator, generator, generator, generator),
        (generator, 2 * generator, -generator, 3 * generator),
    ]
    tuple_rng = random.Random(2026071761)
    while len(tuples) < 68:
        scalars = [tuple_rng.randrange(fixture["order"]) for _ in range(4)]
        tuples.append(tuple(scalar * generator for scalar in scalars))

    replay_failures = 0
    mutated_inverse_rejects = 0
    sample_records = []
    for index, points in enumerate(tuples):
        p1, p2, p3, p4 = points
        transformed = (p1, p1 + p2, p3, p1 + p2 + p3 + p4)
        r1, r2, r3, r4 = transformed
        recovered = (r1, r2 - r1, r3, r4 - r2 - r3)
        mutated = (r1, r2 - r1, r3, r4 - r2 + r3)
        if recovered != points:
            replay_failures += 1
        if mutated != points:
            mutated_inverse_rejects += 1
        if index < 4:
            sample_records.append({
                "input": point_tuple_record(points),
                "transformed": point_tuple_record(transformed),
                "recovered": point_tuple_record(recovered),
            })

    fixture_volume_records = []
    for cell in p1492["fixture_mixed_volume_cells"]:
        direct = int(cell["direct_S6_squareup_mixed_volume"])
        transformed = int(cell["omit_and_filter_mixed_volume"])
        r = int(cell["selector_degree_r"])
        fixture_volume_records.append({
            "L": int(cell["L"]),
            "r": r,
            "formula_value": 16 * r**4,
            "direct_mixed_volume": direct,
            "transformed_mixed_volume": transformed,
            "strict_drop": transformed < direct,
            "source_complete": bool(cell["omit_equals_direct_S6"]),
        })
    synthetic_records = [
        {
            "r": int(cell["selector_degree_r"]),
            "direct": int(cell["direct_S6_squareup_mixed_volume"]),
            "transformed": int(cell["omit_and_filter_mixed_volume"]),
            "formula_value": 16 * int(cell["selector_degree_r"]) ** 4,
        }
        for cell in p1492["synthetic_sweep"]["cells"]
    ]

    gates = {
        "frozen_hashes_exact": all(hash_gates.values()),
        "idea059_is_sole_active_focus": active == ["ECDLP-IDEA-059"],
        "predecessor_audits_pass": (
            p1490_audit["passed_checks"] == p1490_audit["total_checks"] == 12
            and p1492_audit["passed_checks"] == p1492_audit["total_checks"] == 12
        ),
        "candidate_A_symmetric_rewrite_exact": holdout_matches == 64,
        "candidate_A_generic_inverse_degree_four": (
            int(generic_polynomial.degree()) == 4 and factor_degrees == [[4, 1]]
        ),
        "candidate_A_is_birational": False,
        "candidate_B_matrix_determinant_one": int(transform_matrix.det()) == 1,
        "candidate_B_inverse_matrix_exact": transform_matrix.inverse() == expected_inverse,
        "candidate_B_all_tuple_replays_exact": replay_failures == 0,
        "candidate_B_mutated_inverse_rejects": mutated_inverse_rejects > 0,
        "candidate_B_all_fixture_volumes_equal_16r4": all(
            record["direct_mixed_volume"]
            == record["transformed_mixed_volume"]
            == record["formula_value"]
            for record in fixture_volume_records
        ),
        "candidate_B_all_synthetic_volumes_equal_16r4": all(
            record["direct"] == record["transformed"] == record["formula_value"]
            for record in synthetic_records
        ),
        "candidate_B_all_sources_replay": (
            all(cell["path_count_equals_BKK_mixed_volume"] for cell in p1492["source_replay_cells"])
            and all(panel["all_sources_replay"] for panel in p1492["primary_relation_panels"])
        ),
        "candidate_B_strict_saturated_volume_drop": False,
        "any_frozen_map_passes_phase1": False,
        "phase2_scaling_contract_approved": False,
        "generic_shoup_breakthrough": False,
    }
    required_true = [
        "frozen_hashes_exact",
        "idea059_is_sole_active_focus",
        "predecessor_audits_pass",
        "candidate_A_symmetric_rewrite_exact",
        "candidate_A_generic_inverse_degree_four",
        "candidate_B_matrix_determinant_one",
        "candidate_B_inverse_matrix_exact",
        "candidate_B_all_tuple_replays_exact",
        "candidate_B_mutated_inverse_rejects",
        "candidate_B_all_fixture_volumes_equal_16r4",
        "candidate_B_all_synthetic_volumes_equal_16r4",
        "candidate_B_all_sources_replay",
    ]
    required_false = [
        "candidate_A_is_birational",
        "candidate_B_strict_saturated_volume_drop",
        "any_frozen_map_passes_phase1",
        "phase2_scaling_contract_approved",
        "generic_shoup_breakthrough",
    ]
    if not all(gates[name] for name in required_true) or any(gates[name] for name in required_false):
        raise RuntimeError(f"P1503 review gate inconsistency: {gates}")

    payload = {
        "schema": SCHEMA,
        "status": "NEGATIVE_RESULT_P1503_IDEA059_NATURAL_CREMONA_NO_SATURATED_VOLUME_DROP",
        "claim_status": "SUMMATION-COORDINATE NONBIRATIONAL / GROUP-ADDITION MAP EXACT / SOURCE-COMPLETE VOLUME INVARIANT / NO BREAKTHROUGH",
        "source": display_path(Path(__file__).resolve()),
        "source_sha256": sha256_file(Path(__file__).resolve()),
        "contract": display_path(CONTRACT),
        "contract_sha256": hashes[display_path(CONTRACT)],
        "frozen_hashes": hashes,
        "hash_gates": hash_gates,
        "focus_active_ids": active,
        "fixture": {
            "p": fixture["p"],
            "a": fixture["a"],
            "b": fixture["b"],
            "order": fixture["order"],
            "target": composition["public_start"],
        },
        "candidate_A_summation_coordinate": {
            "map": "(e1,e2,e3)->(e1,e2,S4_e)",
            "s4_x_total_degree": int(s4.total_degree()),
            "s4_x_degrees": [int(value) for value in s4.degrees()],
            "s4_x_term_count": len(s4.monomials()),
            "s4_e_total_degree": int(rewritten.total_degree()),
            "s4_e_degrees": [int(value) for value in rewritten.degrees()],
            "s4_e_term_count": len(rewritten.monomials()),
            "s4_e_coefficient_sha256": rewrite_hash,
            "holdout_matches": holdout_matches,
            "generic_inverse_degree": int(generic_polynomial.degree()),
            "generic_factor_degrees": factor_degrees,
            "generic_polynomial_irreducible": bool(generic_polynomial.is_irreducible()),
            "birational": False,
            "rejection": "four generic inverse branches",
        },
        "candidate_B_group_addition": {
            "map": "(P1,P2,P3,P4)->(P1,P1+P2,P3,P1+P2+P3+P4)",
            "matrix": [[int(value) for value in row] for row in transform_matrix.rows()],
            "determinant": int(transform_matrix.det()),
            "inverse": [[int(value) for value in row] for row in expected_inverse.rows()],
            "global_group_variety_automorphism": True,
            "affine_denominator_exceptions_discarded": False,
            "tuple_count": len(tuples),
            "tuple_replay_failures": replay_failures,
            "mutated_inverse_reject_count": mutated_inverse_rejects,
            "sample_records": sample_records,
            "fixture_volume_records": fixture_volume_records,
            "synthetic_volume_records": synthetic_records,
            "strict_source_complete_volume_drop": False,
        },
        "gates": gates,
        "interpretation": (
            "The map that directly replaces e3 by the symmetric S4 relation only looks attractive because it hides a four-sheet inverse and is not Cremona. The genuine target-independent elliptic group-addition automorphism has a complete inverse and preserves every source, but P1492's independently audited direct and serial systems both have source-complete mixed volume 16r^4 on every frozen and synthetic cell. IDEA-059 therefore has no passing map in its specified derivation grammar and must not enter scaling."
        ),
        "limitations": [
            "The negative closes the summation-coordinate map and the natural group-linear serial-addition map, not every nonlinear birational transformation.",
            "P1492 supplies an exact source-complete square-up comparison; this is not a general theorem that BKK mixed volume is invariant under all Cremona maps.",
            "A future non-group-linear map must be named before execution and must include every inverse branch, denominator chart, and saturated component.",
            "No rho or Shoup-bound improvement is claimed.",
        ],
        "next_action": (
            "Close IDEA-059 without running its 540-CPU-hour campaign. Generate a new representation hypothesis only if it supplies a concrete non-group-linear birational map before scoring; otherwise return to source-aware FFE mechanisms rather than coordinate-only rewrites."
        ),
    }
    write_atomic(OUT, (compact(payload) + "\n").encode("ascii"))
    write_atomic(NOTE, render_note(payload).encode("ascii"))
    print(compact({
        "status": payload["status"],
        "candidate_A_inverse_degree": int(generic_polynomial.degree()),
        "candidate_B_strict_drop": False,
        "phase2_approved": False,
        "out": str(OUT),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
