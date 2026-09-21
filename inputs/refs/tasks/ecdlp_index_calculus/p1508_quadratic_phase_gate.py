#!/usr/bin/env sage -python
"""Exact IDEA-058 phase decomposition and conditioned-source gate."""

from __future__ import annotations

import collections
import hashlib
import itertools
import json
import os
import random
from pathlib import Path
from typing import Any

from sage.all import Matrix, QQ, vector


ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "ecdlp_index_calculus_state"
RESEARCH = ROOT / "research"
CONTRACT = STATE / "experiment_contract_p1508_quadratic_phase_gate.md"
P1504 = STATE / "p1504_matchgate_shared_basis_obstruction.json"
P1504_AUDIT = STATE / "p1504_matchgate_shared_basis_obstruction_audit.json"
IDEA = Path(
    "/Volumes/Volume/crypto-autoresearcher/ideas/deferred/"
    "ECDLP-IDEA-058_quadratic_phase_stabilizer_witness_decomposition_hypothesis.md"
)
DERIVATION = Path(
    "/Volumes/Volume/crypto-autoresearcher/ideas/artifacts/"
    "ECDLP-IDEA-058/quadratic_phase_derivation.md"
)
FOCUS_QUEUE = Path(
    "/Volumes/Volume/crypto-autoresearcher/focus/archive/"
    "focus_queue_idea058_active.json"
)
FOCUS_PLAN = Path(
    "/Volumes/Volume/crypto-autoresearcher/focus/archive/"
    "focus_plan_idea058_active.json"
)
OUT = STATE / "p1508_quadratic_phase_gate.json"
NOTE = RESEARCH / "p1508_quadratic_phase_gate.md"

SCHEMA = "ecdlp.p1508_quadratic_phase_gate.v1"
EXPECTED = {
    CONTRACT: "a64dea9a9f3b66e6c3569bcaf3e936eb6cd12f8881f3108910ec30f2713b2f43",
    P1504: "4e65c8f59a601f17763a7d0fd92514c091d36547cdaac5f8fc29d157e332ba51",
    P1504_AUDIT: "4cb16dc9407b1c83146beab8dd5b0146ea1cd7de7d00db57d8869d45b2280033",
    IDEA: "7a82420e94d62797361203c2945599f6dd5ee19a2244fad8111dda1943afed3e",
    DERIVATION: "b064e82b08d39b68ca0ef3f9fc43a41033c1a2c51fbfdc89c0375d417176d010",
    FOCUS_QUEUE: "7ea76c597b3533005b88558325ea106bd662920b881052174e43f528dc96123e",
    FOCUS_PLAN: "7a3ec9c0ec61fa16f63e15f6a09893715192ea1fc4ad0394525c435c837b9cb4",
}

Point = tuple[int, int] | None
Phase = tuple[int, int, int, int, int, int, int]


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
    return x3, (slope * (x1 - x3) - y1) % p


def point_sum(points: list[Point], p: int, a: int) -> Point:
    total = None
    for point in points:
        total = point_add(total, point, p, a)
    return total


def decode_indices(mask: int) -> list[int]:
    return [(mask >> (2 * (3 - slot))) & 3 for slot in range(4)]


def tensor_from_curve(factor_base: list[Point], p: int, a: int) -> list[int]:
    return [
        int(point_sum([factor_base[index] for index in decode_indices(mask)], p, a) is None)
        for mask in range(256)
    ]


def tensor_from_scalar_weights() -> list[int]:
    weights = [1, -1, 2, -2]
    return [
        int(sum(weights[index] for index in decode_indices(mask)) == 0)
        for mask in range(256)
    ]


def bits(mask: int) -> tuple[int, ...]:
    return tuple((mask >> (7 - index)) & 1 for index in range(8))


def phase_value(parameters: Phase, mask: int) -> int:
    constant, linear_a, linear_b, within, pair_a, pair_b, cross = parameters
    word = bits(mask)
    a_bits = word[0::2]
    b_bits = word[1::2]
    exponent = constant
    exponent += linear_a * sum(a_bits) + linear_b * sum(b_bits)
    exponent += within * sum(left * right for left, right in zip(a_bits, b_bits))
    exponent += pair_a * sum(
        a_bits[i] * a_bits[j] for i in range(4) for j in range(i + 1, 4)
    )
    exponent += pair_b * sum(
        b_bits[i] * b_bits[j] for i in range(4) for j in range(i + 1, 4)
    )
    exponent += cross * sum(
        a_bits[i] * b_bits[j] for i in range(4) for j in range(4) if i != j
    )
    return 1 if exponent % 2 == 0 else -1


def parameter_catalog() -> list[Phase]:
    return [
        tuple((number >> (6 - index)) & 1 for index in range(7))  # type: ignore[misc]
        for number in range(128)
    ]


def rational_string(value: Any) -> str:
    return str(QQ(value))


def phase_decomposition(tensor: list[int]) -> tuple[Any, Any, list[dict[str, Any]]]:
    parameters = parameter_catalog()
    dictionary = Matrix(
        QQ,
        256,
        128,
        lambda row, column: phase_value(parameters[column], row),
    )
    coefficients = dictionary.solve_right(vector(QQ, tensor))
    terms = [
        {
            "parameter_bits": "".join(map(str, parameters[index])),
            "parameters": list(parameters[index]),
            "coefficient": rational_string(coefficient),
        }
        for index, coefficient in enumerate(coefficients)
        if coefficient
    ]
    return dictionary, coefficients, terms


def walsh_control(tensor: list[int]) -> dict[str, Any]:
    spectrum = [
        sum(
            tensor[word] * (1 if (frequency & word).bit_count() % 2 == 0 else -1)
            for word in range(256)
        )
        for frequency in range(256)
    ]
    counts = collections.Counter(spectrum)
    return {
        "unnormalized_spectrum_counts": {
            str(value): counts[value] for value in sorted(counts)
        },
        "nonzero_term_count": sum(value != 0 for value in spectrum),
        "spectrum_sha256": digest(spectrum),
        "exact_reconstruction": all(
            sum(
                spectrum[frequency]
                * (1 if (frequency & word).bit_count() % 2 == 0 else -1)
                for frequency in range(256)
            )
            == 256 * tensor[word]
            for word in range(256)
        ),
    }


def prefix_contractions(
    tensor: list[int], terms: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], int]:
    records = []
    mismatch_count = 0
    for prefix_length in range(9):
        for prefix in range(1 << prefix_length):
            suffixes = [
                mask
                for mask in range(256)
                if (mask >> (8 - prefix_length) if prefix_length else 0) == prefix
            ]
            direct = sum(tensor[mask] for mask in suffixes)
            contracted = sum(
                QQ(term["coefficient"])
                * sum(
                    phase_value(tuple(term["parameters"]), mask)  # type: ignore[arg-type]
                    for mask in suffixes
                )
                for term in terms
            )
            if contracted != direct:
                mismatch_count += 1
            records.append({
                "prefix_length": prefix_length,
                "prefix": prefix,
                "direct_count": direct,
                "phase_count": rational_string(contracted),
            })
    return records, mismatch_count


def recover_witness(terms: list[dict[str, Any]]) -> dict[str, Any]:
    prefix = 0
    transcript = []
    for prefix_length in range(1, 9):
        branch_counts = []
        for bit in (0, 1):
            candidate = (prefix << 1) | bit
            suffixes = [
                mask
                for mask in range(256)
                if mask >> (8 - prefix_length) == candidate
            ]
            count = sum(
                QQ(term["coefficient"])
                * sum(
                    phase_value(tuple(term["parameters"]), mask)  # type: ignore[arg-type]
                    for mask in suffixes
                )
                for term in terms
            )
            branch_counts.append(count)
        chosen = 0 if branch_counts[0] > 0 else 1
        prefix = (prefix << 1) | chosen
        transcript.append({
            "prefix_length": prefix_length,
            "zero_count": rational_string(branch_counts[0]),
            "one_count": rational_string(branch_counts[1]),
            "chosen_bit": chosen,
        })
    return {
        "mask": prefix,
        "source_indices": decode_indices(prefix),
        "transcript": transcript,
        "transcript_sha256": digest(transcript),
    }


def render_note(payload: dict[str, Any]) -> str:
    phase = payload["phase_decomposition"]
    conditions = payload["conditioned_source_recovery"]
    return "\n".join([
        "# P1508 Quadratic-Phase Witness Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Exact Result",
        "",
        f"The frozen 128-column invariant phase dictionary has exact rank {phase['dictionary_rank']}. Its deterministic Sage certificate uses {phase['nonzero_term_count']} rational terms and reconstructs all 256 entries. The complete Walsh control uses {payload['walsh_control']['nonzero_term_count']} nonzero terms.",
        "",
        f"All {conditions['prefix_condition_count']} conditioned prefix counts agree exactly, and mask {conditions['witness']['mask']} replays as a valid elliptic relation on all five fixtures.",
        "",
        "## Boundary",
        "",
        "All five curve tensors are identical and equal the known-weight predicate for [P,-P,2P,-2P]. The 20-term identity is therefore positive toy algebra, not a curve-specific public factor-base identity or an asymptotic algorithm.",
        "",
        "Five matched random 36-support tensors lie outside the invariant phase span. The generic cyclic-character identity uses N terms and requires scalar labels.",
        "",
        "## Next Action",
        "",
        payload["next_action"],
        "",
    ])


def main() -> int:
    hashes = {display_path(path): sha256_file(path) for path in EXPECTED}
    hash_gates = {
        display_path(path): hashes[display_path(path)] == expected
        for path, expected in EXPECTED.items()
    }
    if not all(hash_gates.values()):
        raise RuntimeError(f"P1508 frozen hash mismatch: {hash_gates}")

    p1504 = json.loads(P1504.read_text(encoding="ascii"))
    p1504_audit = json.loads(P1504_AUDIT.read_text(encoding="ascii"))
    focus = json.loads(FOCUS_PLAN.read_text(encoding="ascii"))
    active_ids = [item["id"] for item in focus["critical_experiments"]]
    scalar_tensor = tensor_from_scalar_weights()
    scalar_support = [index for index, value in enumerate(scalar_tensor) if value]

    fixture_replays = []
    curve_tensors = []
    for fixture in p1504["fixtures"]:
        factor_base = [
            tuple(point) if point is not None else None for point in fixture["factor_base"]
        ]
        curve_tensor = tensor_from_curve(factor_base, fixture["p"], fixture["a"])
        curve_support = [index for index, value in enumerate(curve_tensor) if value]
        curve_tensors.append(curve_tensor)
        fixture_replays.append({
            "p": fixture["p"],
            "order": fixture["order"],
            "curve_support_count": len(curve_support),
            "curve_support_sha256": digest(curve_support),
            "p1504_support_sha256": fixture["support_sha256"],
            "curve_support_matches_p1504": curve_support == fixture["support_masks"],
            "curve_tensor_matches_scalar_weights": curve_tensor == scalar_tensor,
        })

    dictionary, coefficients, terms = phase_decomposition(scalar_tensor)
    reconstructed = dictionary * coefficients
    expected_term_bits = [
        "0000000", "0000001", "0000010", "0000100", "0000110",
        "0001000", "0001001", "0001011", "0001101", "0001111",
        "0010000", "0010001", "0010010", "0010100", "0010110",
        "0100000", "0100001", "0100010", "0100100", "0100110",
    ]
    expected_coefficients = [
        "3/8", "-1/4", "-1/8", "1/8", "-1/8",
        "1/4", "-3/8", "1/8", "-1/8", "1/8",
        "3/8", "-1/4", "-1/8", "1/8", "-1/8",
        "3/8", "-1/4", "-1/8", "1/8", "-1/8",
    ]
    certificate_matches_derivation = (
        [term["parameter_bits"] for term in terms] == expected_term_bits
        and [term["coefficient"] for term in terms] == expected_coefficients
    )
    walsh = walsh_control(scalar_tensor)
    prefix_records, prefix_mismatches = prefix_contractions(scalar_tensor, terms)
    witness = recover_witness(terms)
    witness["tensor_entry"] = scalar_tensor[witness["mask"]]
    witness["elliptic_replays"] = [
        {
            "p": fixture["p"],
            "sum_is_identity": point_sum(
                [
                    tuple(fixture["factor_base"][index])
                    for index in witness["source_indices"]
                ],
                fixture["p"],
                fixture["a"],
            ) is None,
        }
        for fixture in p1504["fixtures"]
    ]

    random_controls = []
    for fixture in p1504["fixtures"]:
        seed = fixture["matched_random_control"]["seed"]
        support = sorted(random.Random(seed).sample(range(256), len(scalar_support)))
        random_tensor = vector(QQ, [int(index in set(support)) for index in range(256)])
        augmented_rank = dictionary.augment(Matrix(QQ, 256, 1, list(random_tensor))).rank()
        random_controls.append({
            "p": fixture["p"],
            "seed": seed,
            "support_count": len(support),
            "support_sha256": digest(support),
            "p1504_support_sha256": fixture["matched_random_control"]["support_sha256"],
            "augmented_rank": augmented_rank,
            "in_invariant_phase_span": augmented_rank == dictionary.rank(),
        })

    gates = {
        "frozen_hashes_exact": all(hash_gates.values()),
        "idea058_is_sole_active_focus": active_ids == ["ECDLP-IDEA-058"],
        "p1504_independent_audit_passed": (
            p1504_audit["passed_checks"] == p1504_audit["total_checks"] == 12
        ),
        "all_curve_tensors_replay_p1504": all(
            item["curve_support_matches_p1504"] for item in fixture_replays
        ),
        "all_curve_tensors_equal_scalar_control": all(
            item["curve_tensor_matches_scalar_weights"] for item in fixture_replays
        ) and all(tensor == curve_tensors[0] for tensor in curve_tensors),
        "invariant_phase_dictionary_rank_29": dictionary.rank() == 29,
        "sage_certificate_has_20_terms": len(terms) == 20,
        "certificate_matches_frozen_derivation": certificate_matches_derivation,
        "phase_reconstruction_exact_256": list(reconstructed) == scalar_tensor,
        "walsh_control_exact_with_64_terms": (
            walsh["exact_reconstruction"] and walsh["nonzero_term_count"] == 64
        ),
        "all_511_prefix_contractions_exact": (
            len(prefix_records) == 511 and prefix_mismatches == 0
        ),
        "conditioned_witness_replays_all_curves": (
            witness["tensor_entry"] == 1
            and all(item["sum_is_identity"] for item in witness["elliptic_replays"])
        ),
        "matched_random_controls_outside_invariant_span": all(
            not item["in_invariant_phase_span"] and item["augmented_rank"] == 30
            and item["support_sha256"] == item["p1504_support_sha256"]
            for item in random_controls
        ),
        "minimum_phase_support_certified": False,
        "public_coordinate_derived_phase_identity": False,
        "sub_rho_asymptotic_term_bound": False,
        "scaling_contract_approved": False,
        "generic_shoup_breakthrough": False,
    }
    expected_false = {
        "minimum_phase_support_certified",
        "public_coordinate_derived_phase_identity",
        "sub_rho_asymptotic_term_bound",
        "scaling_contract_approved",
        "generic_shoup_breakthrough",
    }
    if not all(value for key, value in gates.items() if key not in expected_false):
        raise RuntimeError(f"P1508 decision gate failed: {gates}")

    source = Path(__file__).resolve()
    payload = {
        "schema": SCHEMA,
        "status": "MIXED_RESULT_P1508_EXACT_20_PHASE_TOY_SCALAR_CONTROL_NO_PUBLIC_ELLIPTIC_IDENTITY",
        "claim_status": "EXACT TOY PHASE IDENTITY / ALL CONDITIONED COUNTS EXACT / SCALAR-LABEL CONTROL ONLY / NO ASYMPTOTIC OR SHOUP BREAK",
        "source": display_path(source),
        "source_sha256": sha256_file(source),
        "contract": display_path(CONTRACT),
        "contract_sha256": hashes[display_path(CONTRACT)],
        "frozen_hashes": hashes,
        "hash_gates": hash_gates,
        "focus_active_ids": active_ids,
        "tensor_replay": {
            "fixture_count": len(fixture_replays),
            "entries_per_fixture": 256,
            "support_count": len(scalar_support),
            "support_masks": scalar_support,
            "support_sha256": digest(scalar_support),
            "all_fixture_tensors_identical": all(
                tensor == curve_tensors[0] for tensor in curve_tensors
            ),
            "known_scalar_weights": [1, -1, 2, -2],
            "fixture_replays": fixture_replays,
        },
        "phase_decomposition": {
            "coefficient_ring": "QQ",
            "phase_value_set": [1, -1],
            "parameter_count": 7,
            "dictionary_column_count": dictionary.ncols(),
            "dictionary_rank": dictionary.rank(),
            "dictionary_sha256": digest([
                [int(dictionary[row, column]) for row in range(256)]
                for column in range(128)
            ]),
            "solver": "Sage Matrix(QQ).solve_right",
            "nonzero_term_count": len(terms),
            "minimum_support_certified": False,
            "coefficient_denominators": sorted({
                int(QQ(term["coefficient"]).denominator()) for term in terms
            }),
            "terms": terms,
            "terms_sha256": digest(terms),
            "all_256_entries_exact": list(reconstructed) == scalar_tensor,
        },
        "walsh_control": walsh,
        "conditioned_source_recovery": {
            "prefix_condition_count": len(prefix_records),
            "mismatch_count": prefix_mismatches,
            "prefix_transcript_sha256": digest(prefix_records),
            "witness": witness,
        },
        "matched_random_controls": random_controls,
        "cyclic_character_control": {
            "identity": "delta(sum s_i=0 mod N)=(1/N) sum_{k=0}^{N-1} zeta_N^(k sum s_i)",
            "term_count": "N",
            "term_count_exponent": 1,
            "requires_scalar_labels": True,
            "public_generic_factor_base_evaluation_available": False,
        },
        "gates": gates,
        "interpretation": (
            "The invariant Boolean grammar gives a genuine exact 20-term rational "
            "phase certificate and exact conditioned source recovery on the frozen "
            "tensor. However, the tensor is identical on all five curves because it "
            "is only the known integer-weight predicate for [P,-P,2P,-2P]. No curve "
            "coordinate or addition-law structure enters the identity. The result is "
            "therefore retained as positive toy algebra and a negative applicability "
            "gate for IDEA-058's current generic-ECDLP formulation."
        ),
        "limitations": [
            "The 20 terms are a certified upper bound, not a minimum phase-rank proof.",
            "The grammar is permutation-invariant and Boolean; other coordinate-derived phase families remain outside scope.",
            "The fixture has fixed arity and fixed eight-bit size, so 20 has no asymptotic exponent.",
            "The factor-base elements are manufactured known multiples rather than public coordinate-selected points with unknown logs.",
            "No relation collection, linear algebra, descent, rho, or Shoup-bound improvement is claimed.",
        ],
        "next_action": (
            "Return IDEA-058's present scalar-labelled formulation to deferred. A "
            "successor must start from a public coordinate-defined factor base and "
            "derive a scalable exact phase identity from complete elliptic addition "
            "equations, with a proved subcritical term bound and conditioned source lift."
        ),
    }
    write_atomic(OUT, (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("ascii"))
    write_atomic(NOTE, render_note(payload).encode("ascii"))
    print(json.dumps({
        "status": payload["status"],
        "output": str(OUT),
        "note": str(NOTE),
        "dictionary_rank": dictionary.rank(),
        "phase_terms": len(terms),
        "walsh_terms": walsh["nonzero_term_count"],
        "prefix_conditions": len(prefix_records),
        "prefix_mismatches": prefix_mismatches,
        "witness_mask": witness["mask"],
        "gates": gates,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
