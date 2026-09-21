#!/usr/bin/env python3
"""Test IDEA-052's canonical source-labelled wedge before scaling."""

from __future__ import annotations

import collections
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "ecdlp_index_calculus_state"
RESEARCH = ROOT / "research"
CONTRACT = STATE / "experiment_contract_p1506_wedge_source_label_gate.md"
PO004_CONTRACT = RESEARCH / "PO_transfer_004_contract.md"
PO004_RESULT = ROOT / "experiments/ecdlp_isogeny/po_transfer_004_result.json"
PO004_VERIFY = ROOT / "experiments/ecdlp_isogeny/po_transfer_004_verify.json"
IDEA = Path(
    "/Volumes/Volume/crypto-autoresearcher/ideas/deferred/"
    "ECDLP-IDEA-052_elliptic_wedge_witness_identity_hypothesis.md"
)
DERIVATION = Path(
    "/Volumes/Volume/crypto-autoresearcher/ideas/artifacts/"
    "ECDLP-IDEA-052/source_labelled_wedge_derivation.md"
)
FOCUS_QUEUE = Path(
    "/Volumes/Volume/crypto-autoresearcher/focus/archive/"
    "focus_queue_idea052_active.json"
)
FOCUS_PLAN = Path(
    "/Volumes/Volume/crypto-autoresearcher/focus/archive/"
    "focus_plan_idea052_active.json"
)
OUT = STATE / "p1506_wedge_source_label_gate.json"
NOTE = RESEARCH / "p1506_wedge_source_label_gate.md"

SCHEMA = "ecdlp.p1506_wedge_source_label_gate.v1"
EXPECTED = {
    CONTRACT: "3b0616cf0b8b539878dce9ab7db175077bd8fa53482a4448810d01d01c8b5ab5",
    PO004_CONTRACT: "a616bd5d58042a0a736f3d7e03cf470e869f9964a467297e436dee35ab6e3ff9",
    PO004_RESULT: "2fc7b3b3e0fdca7a451c92defe870e100a945a21ecaccacc53f7dfe30841177c",
    PO004_VERIFY: "2b32b382a2b820d35743c2a60ad02581c7bc5f7446ef477019b0840499cd3fe4",
    IDEA: "7f16d0c18548de91e2ec6ad2f909d36bbea2012854bceee0a85c0957be29669e",
    DERIVATION: "a0e4d797513a60a8d71ef00a7fb3dbd133acf2f74b1308533562d99d84a1b969",
    FOCUS_QUEUE: "d1183c5d8d5e735d54f3a544f8628dc6b2e0731b417f96d7f2cfc9afb8a76f56",
    FOCUS_PLAN: "bb9ccefcfe0c171bcb1548d30ff631a558a8c7732158608bafa53d8602e44c66",
}

Point = tuple[int, int] | None


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


def formal_wedge_cell(base_size: int, p: int = 11) -> dict[str, Any]:
    coefficients: dict[tuple[int, int], int] = collections.defaultdict(int)
    diagonal_terms = 0
    ordered_nonzero_terms = 0
    for left in range(base_size):
        for right in range(base_size):
            if left == right:
                diagonal_terms += 1
                continue
            ordered_nonzero_terms += 1
            pair = (min(left, right), max(left, right))
            source_sign = 1 if left < right else -1
            evaluation_sign = source_sign
            coefficients[pair] = (
                coefficients[pair] + source_sign * evaluation_sign
            ) % p
    expected_dimension = math.comb(base_size, 2)
    rows = [[left, right, coefficients[(left, right)]] for left, right in sorted(coefficients)]
    return {
        "B": base_size,
        "ordered_input_term_count": base_size * base_size,
        "diagonal_terms_annihilated": diagonal_terms,
        "ordered_nonzero_terms": ordered_nonzero_terms,
        "source_label_dimension": len(coefficients),
        "expected_binomial_B_choose_2": expected_dimension,
        "explicit_unordered_pair_table_size": expected_dimension,
        "all_coefficients_equal_two": all(value == 2 % p for value in coefficients.values()),
        "source_labels_unique": len(coefficients) == len(set(coefficients)),
        "coefficient_transcript_sha256": digest(rows),
        "strictly_below_pair_surface": len(coefficients) < expected_dimension,
    }


def point_add(left: Point, right: Point, p: int = 11, a: int = 1) -> Point:
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


def point_mul(scalar: int, point: Point) -> Point:
    scalar %= 11
    result = None
    addend = point
    while scalar:
        if scalar & 1:
            result = point_add(result, addend)
        addend = point_add(addend, addend)
        scalar >>= 1
    return result


def point_sum(points: list[Point]) -> Point:
    result = None
    for point in points:
        result = point_add(result, point)
    return result


PAIRINGS = [
    ((0, 1), (2, 3)),
    ((0, 2), (1, 3)),
    ((0, 3), (1, 2)),
]


def chart_accepts(indices: tuple[int, int, int, int], pairing: Any) -> bool:
    (a, b), (c, d) = pairing
    return indices[a] != indices[b] and indices[c] != indices[d]


def factor_base_cell(name: str, scalars: list[int]) -> dict[str, Any]:
    generator = (0, 4)
    factor_base = [point_mul(scalar, generator) for scalar in scalars]
    relations = []
    for indices in itertools.product(range(4), repeat=4):
        points = [factor_base[index] for index in indices]
        scalar_relation = sum(scalars[index] for index in indices) % 11 == 0
        curve_relation = point_sum(points) is None
        if scalar_relation != curve_relation:
            raise RuntimeError("P1506 scalar/curve relation mismatch")
        if not curve_relation:
            continue
        multiplicities = sorted(collections.Counter(indices).values(), reverse=True)
        charts = [chart_accepts(indices, pairing) for pairing in PAIRINGS]
        relations.append({
            "indices": list(indices),
            "multiplicity_pattern": multiplicities,
            "fixed_chart_accepts": charts[0],
            "chart_acceptance": charts,
            "any_pair_chart_accepts": any(charts),
        })
    missed = [record for record in relations if not record["any_pair_chart_accepts"]]
    return {
        "name": name,
        "scalars_mod_11": [value % 11 for value in scalars],
        "factor_base": [list(point) if point is not None else None for point in factor_base],
        "relation_count": len(relations),
        "fixed_chart_accepted_count": sum(record["fixed_chart_accepts"] for record in relations),
        "all_three_charts_accepted_count": sum(record["any_pair_chart_accepts"] for record in relations),
        "fixed_chart_missed_count": sum(not record["fixed_chart_accepts"] for record in relations),
        "all_three_charts_missed_count": len(missed),
        "multiplicity_histogram": {
            "+".join(map(str, pattern)): count
            for pattern, count in sorted(collections.Counter(
                tuple(record["multiplicity_pattern"]) for record in relations
            ).items())
        },
        "missed_relations": missed,
        "relation_transcript_sha256": digest(relations),
        "all_relations_curve_replay": True,
    }


def render_note(payload: dict[str, Any]) -> str:
    lines = [
        "# P1506 Wedge Source-Label Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Exact Label State",
        "",
        "| B | source wedge labels | explicit unordered pairs | strict drop |",
        "|---:|---:|---:|---:|",
    ]
    for cell in payload["formal_wedge_cells"]:
        lines.append(
            f"| {cell['B']} | {cell['source_label_dimension']} | "
            f"{cell['explicit_unordered_pair_table_size']} | "
            f"{str(cell['strictly_below_pair_surface']).lower()} |"
        )
    lines.extend([
        "",
        "## Repeated Sources",
        "",
        "The symmetric control has 36 relations; cycling all three pair charts covers them. The repeat-stress factor base has 14 relations, and all eight 3+1 rows vanish in every chart.",
        "",
        "PO-transfer-004 remains an independently verified exact Pluecker certificate, but it supplies neither a concrete sub-pair-pair query structure nor a below-rho cost trend.",
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
        raise RuntimeError(f"P1506 frozen hash mismatch: {hash_gates}")

    focus = json.loads(FOCUS_PLAN.read_text(encoding="ascii"))
    active_ids = [item["id"] for item in focus["critical_experiments"]]
    po004 = json.loads(PO004_RESULT.read_text(encoding="ascii"))
    po004_verify = json.loads(PO004_VERIFY.read_text(encoding="ascii"))

    formal_cells = [formal_wedge_cell(base_size) for base_size in (4, 8, 16, 32, 64, 128)]
    symmetric = factor_base_cell("symmetric", [1, -1, 2, -2])
    repeat_stress = factor_base_cell("repeat_stress", [1, -3, 2, -2])
    planted = next(
        record for record in (
            {
                "indices": list(indices),
                "curve_sum_identity": point_sum([
                    point_mul([1, -1, 2, -2][index], (0, 4)) for index in indices
                ]) is None,
                "all_distinct": len(set(indices)) == 4,
                "chart_acceptance": [chart_accepts(indices, pairing) for pairing in PAIRINGS],
            }
            for indices in [(0, 1, 2, 3)]
        )
    )
    po004_binding = {
        "status": po004["status"],
        "formal_predicate": po004["formal_predicate"],
        "controls_pass": po004["controls_pass"],
        "planted_production_all_configs": po004["gate"]["planted_production_all_configs"],
        "random_control_all_targets_all_configs": po004["gate"]["random_control_all_targets_all_configs"],
        "concrete_sub_pair_pair_query_structure": po004["gate"]["structural_criteria"]["concrete_sub_pair_pair_query_structure"],
        "memory_below_four_sqrt_n": po004["gate"]["structural_criteria"]["memory_below_four_sqrt_n"],
        "charged_toy_exponent": po004["fits"]["charged_actual_ops"]["slope"],
        "ideal_oracle_toy_exponent": po004["fits"]["ideal_oracle_ops"]["slope"],
        "algorithmic_success": po004["gate"]["algorithmic_success"],
        "verifier_status": po004_verify["status"],
        "primitive_witnesses_verified": po004_verify["primitive_witnesses_verified"],
        "public_relations_verified": po004_verify["public_relations_verified"],
        "cells_verified": po004_verify["cells_verified"],
    }
    gates = {
        "frozen_hashes_exact": all(hash_gates.values()),
        "idea052_is_sole_active_focus": active_ids == ["ECDLP-IDEA-052"],
        "formal_antisymmetrized_expansion_exact": all(
            cell["all_coefficients_equal_two"] and cell["source_labels_unique"]
            for cell in formal_cells
        ),
        "source_label_dimension_equals_full_pair_surface": all(
            cell["source_label_dimension"] == cell["expected_binomial_B_choose_2"]
            == cell["explicit_unordered_pair_table_size"]
            for cell in formal_cells
        ),
        "source_label_state_strictly_below_pair_surface": any(
            cell["strictly_below_pair_surface"] for cell in formal_cells
        ),
        "symmetric_chart_union_complete": (
            symmetric["relation_count"] == 36
            and symmetric["all_three_charts_missed_count"] == 0
            and symmetric["fixed_chart_missed_count"] == 4
        ),
        "repeat_stress_has_complete_chart_failures": (
            repeat_stress["relation_count"] == 14
            and repeat_stress["all_three_charts_missed_count"] == 8
            and all(
                record["multiplicity_pattern"] == [3, 1]
                for record in repeat_stress["missed_relations"]
            )
        ),
        "all_distinct_planted_source_control_passes": (
            planted["curve_sum_identity"]
            and planted["all_distinct"]
            and all(planted["chart_acceptance"])
        ),
        "po004_exact_pluecker_control_verified": (
            po004_binding["status"] == "NEGATIVE RESULT"
            and po004_binding["controls_pass"]
            and po004_binding["planted_production_all_configs"]
            and po004_binding["random_control_all_targets_all_configs"]
            and po004_binding["verifier_status"] == "VERIFIED"
            and po004_binding["primitive_witnesses_verified"] == 2973
            and po004_binding["public_relations_verified"] == 1603
        ),
        "po004_subpair_query_and_algorithmic_gates_fail": (
            not po004_binding["concrete_sub_pair_pair_query_structure"]
            and not po004_binding["memory_below_four_sqrt_n"]
            and not po004_binding["algorithmic_success"]
            and po004_binding["ideal_oracle_toy_exponent"] > 0.5
        ),
        "complete_subquadratic_wedge_reporter_established": False,
        "generic_shoup_breakthrough": False,
    }
    required_true = {
        key: value
        for key, value in gates.items()
        if key not in {
            "source_label_state_strictly_below_pair_surface",
            "complete_subquadratic_wedge_reporter_established",
            "generic_shoup_breakthrough",
        }
    }
    if not all(required_true.values()) or gates["source_label_state_strictly_below_pair_surface"]:
        raise RuntimeError(f"P1506 decision gate failed: {gates}")

    source = Path(__file__).resolve()
    payload = {
        "schema": SCHEMA,
        "status": "NEGATIVE_RESULT_P1506_NATURAL_WEDGE_IS_PAIR_SURFACE_AND_REPEAT_INCOMPLETE",
        "claim_status": "WEDGE EXPANSION EXACT / SOURCE LABELS BINOMIAL-B2 / PLUCKER DUPLICATE / 3+1 SOURCES LOST / NO BREAKTHROUGH",
        "source": display_path(source),
        "source_sha256": sha256_file(source),
        "contract": display_path(CONTRACT),
        "contract_sha256": hashes[display_path(CONTRACT)],
        "frozen_hashes": hashes,
        "hash_gates": hash_gates,
        "focus_active_ids": active_ids,
        "formal_wedge_cells": formal_cells,
        "tiny_curve": {
            "p": 11,
            "a": 1,
            "b": 5,
            "order": 11,
            "generator": [0, 4],
            "symmetric": symmetric,
            "repeat_stress": repeat_stress,
        },
        "controls": {
            "all_distinct_planted_source": planted,
            "po_transfer_004": po004_binding,
        },
        "gates": gates,
        "interpretation": (
            "The canonical source-labelled exterior expansion is exact, but its "
            "coefficients are precisely the B choose 2 unordered pair labels. The "
            "second-addition predicate is the already-tested generic Pluecker pairing. "
            "Cycling all pair charts repairs 2+2 repeats but cannot represent valid "
            "3+1 relations because an equal-label wedge is unavoidable. The natural "
            "IDEA-052 construction is therefore neither subquadratic in pair labels nor "
            "complete as a source reporter."
        ),
        "limitations": [
            "The negative governs the canonical pair wedge and generic Pluecker pairing, not every curve-specific exterior syzygy.",
            "Occurrence colouring or divided powers could cover repeats but changes the representation and must charge its enlarged state.",
            "Evaluation-space rank compression does not by itself preserve decodable source coefficients.",
            "PO-transfer-004's toy fits are diagnostics, not asymptotic lower bounds.",
            "No rho or Shoup-bound improvement is claimed.",
        ],
        "next_action": (
            "Close IDEA-052's natural pair-wedge formulation. A successor is admissible "
            "only after supplying an explicit curve-specific source-labelled identity "
            "outside generic Pluecker incidence, with repeated-source coverage and state "
            "strictly below the pair surface proved before execution."
        ),
    }
    write_atomic(OUT, (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("ascii"))
    write_atomic(NOTE, render_note(payload).encode("ascii"))
    print(json.dumps({
        "status": payload["status"],
        "output": str(OUT),
        "note": str(NOTE),
        "gates": gates,
        "repeat_stress": {
            "relations": repeat_stress["relation_count"],
            "missed_all_charts": repeat_stress["all_three_charts_missed_count"],
        },
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
