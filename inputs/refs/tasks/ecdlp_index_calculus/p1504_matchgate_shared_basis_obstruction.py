#!/usr/bin/env python3
"""Exhaust the IDEA-050 shared binary basis on exact elliptic source tensors."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import os
import random
from pathlib import Path
from typing import Any, Iterator


ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "ecdlp_index_calculus_state"
RESEARCH = ROOT / "research"
CONTRACT = STATE / "experiment_contract_p1504_matchgate_shared_basis_obstruction.md"
IDEA = Path(
    "/Volumes/Volume/crypto-autoresearcher/ideas/"
    "ECDLP-IDEA-050_spinor_matchgate_addition_transform_hypothesis.md"
)
IDEA_CONTRACT = Path(
    "/Volumes/Volume/crypto-autoresearcher/ideas/contracts/"
    "ECDLP-EXP-CONTRACT-050_matchgate_identity_preflight.yaml"
)
DERIVATION = Path(
    "/Volumes/Volume/crypto-autoresearcher/ideas/artifacts/"
    "ECDLP-IDEA-050/shared_basis_matchgate_derivation.md"
)
FOCUS_QUEUE = Path(
    "/Volumes/Volume/crypto-autoresearcher/focus/archive/"
    "focus_queue_idea050_active.json"
)
FOCUS_PLAN = Path(
    "/Volumes/Volume/crypto-autoresearcher/focus/archive/"
    "focus_plan_idea050_active.json"
)
OUT = STATE / "p1504_matchgate_shared_basis_obstruction.json"
NOTE = RESEARCH / "p1504_matchgate_shared_basis_obstruction.md"

SCHEMA = "ecdlp.p1504_matchgate_shared_basis_obstruction.v1"
FIXTURES = [
    {"p": 11, "a": 1, "b": 5, "order": 11},
    {"p": 13, "a": 0, "b": 2, "order": 19},
    {"p": 17, "a": 1, "b": 3, "order": 17},
    {"p": 19, "a": 0, "b": 2, "order": 13},
    {"p": 23, "a": 1, "b": 4, "order": 29},
]
EXPECTED = {
    CONTRACT: "158b8efaa5470d33033cbbf1f5d5b02a9b2ab24e8aab3aed32b6b313c612995c",
    IDEA: "4b8734dd70ff8d5fb392dae4c26c962bf2db02d73bb35591a55f2d104814df6e",
    IDEA_CONTRACT: "5d7a3fc2a2f364ea6ee3d26dea2c29c6f1b1cae66cb76f06bc5737bc9414fb02",
    DERIVATION: "5059de6ae5e67acf73759e61b53bf57174cc95bbdf4c1f29d51dd2fc6cf82e0c",
    FOCUS_QUEUE: "157793174822cc122aa44682391b8105654c111409141b24984c65c3b164c782",
    FOCUS_PLAN: "58c1a8ec2af93aa43ca84a48b623f945c921bb867e6f6efec35e28c015f9baa1",
}

Point = tuple[int, int] | None
Matrix2 = tuple[int, int, int, int]


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


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    for divisor in range(2, math.isqrt(value) + 1):
        if value % divisor == 0:
            return False
    return True


def curve_points(p: int, a: int, b: int) -> list[tuple[int, int]]:
    return [
        (x, y)
        for x in range(p)
        for y in range(p)
        if (y * y - x * x * x - a * x - b) % p == 0
    ]


def point_add(left: Point, right: Point, p: int, a: int) -> Point:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if left == right:
        slope = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        slope = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return (x3, y3)


def point_mul(scalar: int, point: Point, p: int, a: int) -> Point:
    result = None
    addend = point
    while scalar:
        if scalar & 1:
            result = point_add(result, addend, p, a)
        addend = point_add(addend, addend, p, a)
        scalar >>= 1
    return result


def point_sum(points: list[Point], p: int, a: int) -> Point:
    result = None
    for point in points:
        result = point_add(result, point, p, a)
    return result


def build_source_tensor(factor_base: list[Point], p: int, a: int) -> tuple[list[int], list[int]]:
    tensor = [0] * 256
    support = []
    for indices in itertools.product(range(4), repeat=4):
        mask = 0
        for index in indices:
            mask = (mask << 2) | index
        if point_sum([factor_base[index] for index in indices], p, a) is None:
            tensor[mask] = 1
            support.append(mask)
    return tensor, support


def projective_bases(p: int) -> Iterator[Matrix2]:
    for matrix in itertools.product(range(p), repeat=4):
        first_nonzero = next((entry for entry in matrix if entry), None)
        if first_nonzero != 1:
            continue
        a, b, c, d = matrix
        if (a * d - b * c) % p:
            yield matrix


def apply_shared_basis(tensor: list[int], matrix: Matrix2, p: int) -> list[int]:
    bit_count = (len(tensor) - 1).bit_length()
    if len(tensor) != 1 << bit_count:
        raise ValueError("tensor length is not a power of two")
    a, b, c, d = matrix
    transformed = tensor[:]
    for bit_index in range(bit_count):
        stride = 1 << (bit_count - 1 - bit_index)
        updated = transformed[:]
        for base in range(0, len(tensor), 2 * stride):
            for offset in range(stride):
                zero_index = base + offset
                one_index = zero_index + stride
                zero = transformed[zero_index]
                one = transformed[one_index]
                updated[zero_index] = (a * zero + b * one) % p
                updated[one_index] = (c * zero + d * one) % p
        transformed = updated
    return transformed


def parity_label(tensor: list[int]) -> str | None:
    present = [False, False]
    for index, value in enumerate(tensor):
        if value:
            present[index.bit_count() & 1] = True
    if present == [True, False]:
        return "even"
    if present == [False, True]:
        return "odd"
    return None


def first_matchgate_failure(tensor: list[int], p: int) -> dict[str, int] | None:
    bit_count = (len(tensor) - 1).bit_length()
    for alpha in range(len(tensor)):
        for beta in range(len(tensor)):
            difference = alpha ^ beta
            residual = 0
            term_index = 0
            for bit_position in range(bit_count - 1, -1, -1):
                bit = 1 << bit_position
                if not difference & bit:
                    continue
                term_index += 1
                sign = -1 if term_index & 1 else 1
                residual += sign * tensor[alpha ^ bit] * tensor[beta ^ bit]
            if residual % p:
                return {
                    "alpha": alpha,
                    "beta": beta,
                    "residual": residual % p,
                }
    return None


def scan_tensor(tensor: list[int], p: int) -> dict[str, Any]:
    parity_candidates = []
    matchgate_bases = []
    transcript = hashlib.sha256()
    basis_count = 0
    for matrix in projective_bases(p):
        basis_count += 1
        transformed = apply_shared_basis(tensor, matrix, p)
        parity = parity_label(transformed)
        failure = None
        if parity is not None:
            failure = first_matchgate_failure(transformed, p)
            record = {
                "basis": list(matrix),
                "parity": parity,
                "first_failure": failure,
                "transformed_sha256": digest(transformed),
            }
            parity_candidates.append(record)
            if failure is None:
                matchgate_bases.append(list(matrix))
        transcript.update(
            compact([list(matrix), parity or "mixed", failure]).encode("ascii")
        )
        transcript.update(b"\n")
    return {
        "projective_basis_count": basis_count,
        "expected_projective_basis_count": p * (p * p - 1),
        "parity_basis_count": len(parity_candidates),
        "matchgate_basis_count": len(matchgate_bases),
        "matchgate_bases": matchgate_bases,
        "parity_candidates": parity_candidates,
        "decision_transcript_sha256": transcript.hexdigest(),
    }


def pfaffian(matrix: list[list[int]], indices: tuple[int, ...], p: int) -> int:
    if not indices:
        return 1
    first = indices[0]
    total = 0
    for offset in range(1, len(indices)):
        second = indices[offset]
        remainder = indices[1:offset] + indices[offset + 1 :]
        sign = 1 if (offset + 1) % 2 == 0 else -1
        total += sign * matrix[first][second] * pfaffian(matrix, remainder, p)
    return total % p


def pfaffian_signature(p: int, bit_count: int = 8) -> list[int]:
    matrix = [[0] * bit_count for _ in range(bit_count)]
    for row in range(bit_count):
        for column in range(row + 1, bit_count):
            value = (3 * (row + 1) + 5 * (column + 1) + 1) % p
            matrix[row][column] = value
            matrix[column][row] = -value % p
    signature = []
    for mask in range(1 << bit_count):
        indices = tuple(
            index
            for index in range(bit_count)
            if mask & (1 << (bit_count - 1 - index))
        )
        signature.append(pfaffian(matrix, indices, p) if len(indices) % 2 == 0 else 0)
    return signature


def inverse_matrix(matrix: Matrix2, p: int) -> Matrix2:
    a, b, c, d = matrix
    inverse_determinant = pow((a * d - b * c) % p, -1, p)
    return (
        d * inverse_determinant % p,
        -b * inverse_determinant % p,
        -c * inverse_determinant % p,
        a * inverse_determinant % p,
    )


def render_note(payload: dict[str, Any]) -> str:
    lines = [
        "# P1504 Shared-Basis Matchgate Obstruction",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Complete Elliptic Tensor Results",
        "",
        "| p | #E | support | projective GL2 | parity bases | matchgate bases |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for fixture in payload["fixtures"]:
        scan = fixture["elliptic_scan"]
        lines.append(
            f"| {fixture['p']} | {fixture['order']} | {fixture['support_count']} | "
            f"{scan['projective_basis_count']} | {scan['parity_basis_count']} | "
            f"{scan['matchgate_basis_count']} |"
        )
    lines.extend([
        "",
        "Every source tuple was included in the arity-eight tensor. Some shared bases pass the necessary parity gate, but none passes all matchgate identities.",
        "",
        "## Controls",
        "",
        "The transported Pfaffian signature and source-incomplete sign-only GHZ instrumentation controls pass. Every matched random control has zero matchgate bases.",
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
        raise RuntimeError(f"P1504 frozen hash mismatch: {hash_gates}")

    focus = json.loads(FOCUS_PLAN.read_text(encoding="ascii"))
    active_ids = [item["id"] for item in focus["critical_experiments"]]
    fixture_results = []
    for fixture in FIXTURES:
        p = fixture["p"]
        a = fixture["a"]
        b = fixture["b"]
        order = fixture["order"]
        points = curve_points(p, a, b)
        generator = points[0]
        factor_base = [
            generator,
            point_mul(order - 1, generator, p, a),
            point_mul(2, generator, p, a),
            point_mul(order - 2, generator, p, a),
        ]
        tensor, support = build_source_tensor(factor_base, p, a)
        scalar_support = [
            mask
            for mask in range(256)
            if sum(
                [1, order - 1, 2, order - 2][(mask >> (2 * (3 - slot))) & 3]
                for slot in range(4)
            )
            % order
            == 0
        ]
        elliptic_scan = scan_tensor(tensor, p)

        random_tensor = [0] * 256
        random_support = random.Random(2026071504 + p).sample(range(256), len(support))
        for mask in random_support:
            random_tensor[mask] = 1
        random_scan = scan_tensor(random_tensor, p)

        fixture_results.append({
            **fixture,
            "discriminant_nonzero": (4 * a * a * a + 27 * b * b) % p != 0,
            "point_count": len(points) + 1,
            "group_order_prime": is_prime(order),
            "trace": p + 1 - order,
            "ordinary": (p + 1 - order) % p != 0,
            "generator": list(generator),
            "generator_order_exact": (
                point_mul(order, generator, p, a) is None
                and point_mul(1, generator, p, a) is not None
            ),
            "factor_base": [list(point) if point is not None else None for point in factor_base],
            "support_count": len(support),
            "support_masks": support,
            "support_sha256": digest(support),
            "scalar_support_matches_curve_arithmetic": support == scalar_support,
            "elliptic_scan": elliptic_scan,
            "matched_random_control": {
                "seed": 2026071504 + p,
                "support_count": len(random_support),
                "support_sha256": digest(sorted(random_support)),
                "scan": random_scan,
            },
        })

    control_p = 11
    hadamard = (1, 1, 1, control_p - 1)
    pfaffian = pfaffian_signature(control_p)
    transported = apply_shared_basis(pfaffian, inverse_matrix(hadamard, control_p), control_p)
    recovered = apply_shared_basis(transported, hadamard, control_p)
    transported_scan = scan_tensor(transported, control_p)

    sign_only = [0] * 16
    sign_only[0] = 1
    sign_only[-1] = 1
    transformed_sign_only = apply_shared_basis(sign_only, hadamard, control_p)
    sign_failure = first_matchgate_failure(transformed_sign_only, control_p)

    all_fixture_gates = [
        fixture["discriminant_nonzero"]
        and fixture["point_count"] == fixture["order"]
        and fixture["group_order_prime"]
        and fixture["ordinary"]
        and fixture["generator_order_exact"]
        and fixture["support_count"] == 36
        and fixture["scalar_support_matches_curve_arithmetic"]
        and fixture["elliptic_scan"]["projective_basis_count"]
        == fixture["elliptic_scan"]["expected_projective_basis_count"]
        and fixture["elliptic_scan"]["parity_basis_count"] > 0
        and fixture["elliptic_scan"]["matchgate_basis_count"] == 0
        for fixture in fixture_results
    ]
    random_gates = [
        fixture["matched_random_control"]["scan"]["matchgate_basis_count"] == 0
        for fixture in fixture_results
    ]
    controls = {
        "transported_pfaffian": {
            "p": control_p,
            "basis": list(hadamard),
            "recovered_exactly": recovered == pfaffian,
            "recovered_parity": parity_label(recovered),
            "recovered_first_matchgate_failure": first_matchgate_failure(recovered, control_p),
            "enumerated_matchgate_basis_count": transported_scan["matchgate_basis_count"],
            "enumerated_hadamard_recovered": list(hadamard) in transported_scan["matchgate_bases"],
            "signature_sha256": digest(pfaffian),
            "transported_sha256": digest(transported),
        },
        "sign_only_preselected_x": {
            "p": control_p,
            "basis": list(hadamard),
            "input_support": [0, 15],
            "transformed_parity": parity_label(transformed_sign_only),
            "first_matchgate_failure": sign_failure,
            "passes_matchgate": parity_label(transformed_sign_only) is not None and sign_failure is None,
            "source_choice_count_encoded": 16,
            "complete_factor_choice_count_required": 256,
            "source_complete": False,
        },
    }
    gates = {
        "frozen_hashes_exact": all(hash_gates.values()),
        "idea050_is_sole_active_focus": active_ids == ["ECDLP-IDEA-050"],
        "all_curve_and_source_checks_pass": all(all_fixture_gates),
        "all_elliptic_basis_catalogs_exhaustive": all(
            fixture["elliptic_scan"]["projective_basis_count"]
            == fixture["elliptic_scan"]["expected_projective_basis_count"]
            for fixture in fixture_results
        ),
        "every_elliptic_tensor_has_parity_survivors": all(
            fixture["elliptic_scan"]["parity_basis_count"] > 0
            for fixture in fixture_results
        ),
        "every_elliptic_tensor_has_zero_matchgate_bases": all(
            fixture["elliptic_scan"]["matchgate_basis_count"] == 0
            for fixture in fixture_results
        ),
        "matched_random_controls_have_zero_matchgate_bases": all(random_gates),
        "transported_pfaffian_control_passes": (
            controls["transported_pfaffian"]["recovered_exactly"]
            and controls["transported_pfaffian"]["recovered_first_matchgate_failure"] is None
            and controls["transported_pfaffian"]["enumerated_hadamard_recovered"]
        ),
        "sign_only_instrumentation_passes_but_is_source_incomplete": (
            controls["sign_only_preselected_x"]["passes_matchgate"]
            and not controls["sign_only_preselected_x"]["source_complete"]
        ),
        "phase2_scaling_contract_approved": False,
        "generic_shoup_breakthrough": False,
    }
    if not all(value for key, value in gates.items() if key not in {
        "phase2_scaling_contract_approved", "generic_shoup_breakthrough"
    }):
        raise RuntimeError(f"P1504 decision gate failed: {gates}")

    source = Path(__file__).resolve()
    payload = {
        "schema": SCHEMA,
        "status": "NEGATIVE_RESULT_P1504_IDEA050_SHARED_BINARY_BASIS_MATCHGATE_OBSTRUCTION",
        "claim_status": "SOURCE-COMPLETE BOOLEANIZATION EXACT / SHARED GL2 EXHAUSTED / MATCHGATE IDENTITIES FAIL / NO BREAKTHROUGH",
        "source": display_path(source),
        "source_sha256": sha256_file(source),
        "contract": display_path(CONTRACT),
        "contract_sha256": hashes[display_path(CONTRACT)],
        "frozen_hashes": hashes,
        "hash_gates": hash_gates,
        "focus_active_ids": active_ids,
        "fixtures": fixture_results,
        "controls": controls,
        "aggregate": {
            "fixture_count": len(fixture_results),
            "complete_source_tuples_per_fixture": 256,
            "valid_source_tuples_per_fixture": [item["support_count"] for item in fixture_results],
            "total_projective_bases_exhausted": sum(
                item["elliptic_scan"]["projective_basis_count"] for item in fixture_results
            ),
            "total_parity_bases": sum(
                item["elliptic_scan"]["parity_basis_count"] for item in fixture_results
            ),
            "total_matchgate_bases": sum(
                item["elliptic_scan"]["matchgate_basis_count"] for item in fixture_results
            ),
        },
        "gates": gates,
        "interpretation": (
            "Once the four factor-base choices are included rather than preselected, "
            "the exact arity-eight elliptic relation tensor lies outside the Boolean "
            "matchgate variety after every shared base-field 2x2 basis on all five "
            "ordinary prime-order fixtures. Parity alone is not the obstruction: "
            "surviving bases exist, but each has a nonzero exact matchgate residual. "
            "The sign-only tensor passes and is therefore confirmed as an inadequate "
            "instrumentation shortcut that omits the hard source choices."
        ),
        "limitations": [
            "The negative governs a shared 2x2 base-field basis on the canonical bit encoding, not independent per-leg transformations.",
            "The panel is finite and toy-scale; it rejects a generic universal identity in this grammar but is not an algebraic no-go theorem for every curve.",
            "Nonbinary matchgates, extension-field bases, and different source-complete planar networks remain outside scope.",
            "A matchgate partition value would still require charged exact source self-reduction, relation rank, target descent, and end-to-end rho accounting.",
            "No rho or Shoup-bound improvement is claimed.",
        ],
        "next_action": (
            "Close IDEA-050's shared-binary-basis scaling contract. Any successor must "
            "supply a concrete source-complete higher-domain or independently transformed "
            "network and an exact witness self-reduction before scoring; otherwise rerank "
            "to a mechanism that changes source reporting rather than only tensor coordinates."
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
