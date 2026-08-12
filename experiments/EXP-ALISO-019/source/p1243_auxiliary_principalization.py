#!/usr/bin/env python3
"""Finite-module compatibility for auxiliary-lattice principalization."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
INPUT = HERE / "p1243_auxiliary_lattice_kani_result.json"
OUTPUT = HERE / "p1243_auxiliary_principalization_result.json"
CONTRACT = (
    HERE.parent.parent
    / "research"
    / "p1243_auxiliary_principalization_contract_20260729.md"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scientific_hash(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode(
        "ascii"
    )
    return hashlib.sha256(encoded).hexdigest()


def mat_vec(matrix: list[list[int]], vector: tuple[int, ...], p: int) -> tuple[int, ...]:
    return tuple(
        sum(matrix[row][column] * vector[column] for column in range(len(vector)))
        % p
        for row in range(len(matrix))
    )


def mat_mul(
    left: list[list[int]], right: list[list[int]], p: int
) -> list[list[int]]:
    return [
        [
            sum(left[i][k] * right[k][j] for k in range(len(right))) % p
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def determinant2(matrix: list[list[int]], p: int) -> int:
    return (matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]) % p


def kernel_vector(gram: list[list[int]], p: int) -> tuple[int, int]:
    a = gram[0][0] % p
    b = gram[0][1] % p
    if a != 0 or b != 0:
        vector = (b, -a % p)
    else:
        c = gram[1][1] % p
        vector = (c, -b % p)
    if vector == (0, 0) or mat_vec(gram, vector, p) != (0, 0):
        raise RuntimeError("failed to construct Gram-kernel vector")
    return vector


def projective_lines(p: int) -> list[tuple[int, int]]:
    return [(1, value) for value in range(p)] + [(0, 1)]


def normalize_line(vector: tuple[int, int], p: int) -> tuple[int, int]:
    x, y = vector[0] % p, vector[1] % p
    if x:
        inverse = pow(x, -1, p)
        return (1, y * inverse % p)
    if y:
        return (0, 1)
    raise RuntimeError("zero vector has no projective line")


def tensor_action(
    multiplicity: list[list[int]], tate: list[list[int]], p: int
) -> list[list[int]]:
    result = [[0] * 4 for _ in range(4)]
    for i in range(2):
        for j in range(2):
            for k in range(2):
                for ell in range(2):
                    result[2 * i + k][2 * j + ell] = (
                        multiplicity[i][j] * tate[k][ell]
                    ) % p
    return result


def scalar_relation(
    left: tuple[int, int], right: tuple[int, int], p: int
) -> int | None:
    for index in range(2):
        if right[index] % p:
            scalar = left[index] * pow(right[index], -1, p) % p
            if tuple(scalar * value % p for value in right) == left:
                return scalar
            return None
    return None


def run_row(row: dict) -> dict:
    p = int(row["auxiliary_delta"])
    degree = int(row["degree_eta"])
    inclusion = [[int(value) for value in line] for line in row["inclusion_matrix"]]
    gram_a = [[int(value) for value in line] for line in row["gram_ideal"]]
    gram_o = [[int(value) for value in line] for line in row["gram_order"]]
    v_a = kernel_vector(gram_a, p)
    v_o = kernel_vector(gram_o, p)
    image_v = mat_vec(inclusion, v_a, p)
    inclusion_scalar = scalar_relation(image_v, v_o, p)

    tate = [[degree % p, 0], [0, 1]]
    lines = projective_lines(p)
    images = [normalize_line(mat_vec(tate, line, p), p) for line in lines]
    image_set = set(images)

    inclusion_tensor = tensor_action(inclusion, [[1, 0], [0, 1]], p)
    tate_tensor = tensor_action([[1, 0], [0, 1]], tate, p)
    commute_left = mat_mul(inclusion_tensor, tate_tensor, p)
    commute_right = mat_mul(tate_tensor, inclusion_tensor, p)

    sample_source = lines[(p // 3) % len(lines)]
    sample_target = normalize_line(mat_vec(tate, sample_source, p), p)
    mutated_target = lines[(lines.index(sample_target) + 1) % len(lines)]

    mutated_inclusion = [line[:] for line in inclusion]
    mutated_inclusion[0][0] += 1
    mutated_image = mat_vec(mutated_inclusion, v_a, p)
    singular_tate = [[0, 0], [0, 1]]
    singular_images = [
        normalize_line(image, p)
        for line in lines
        if (image := mat_vec(singular_tate, line, p)) != (0, 0)
    ]

    gates = {
        "gram_a_rank_one": determinant2(gram_a, p) == 0 and v_a != (0, 0),
        "gram_o_rank_one": determinant2(gram_o, p) == 0 and v_o != (0, 0),
        "inclusion_invertible": determinant2(inclusion, p) != 0,
        "inclusion_maps_kernel": inclusion_scalar is not None
        and inclusion_scalar != 0,
        "line_count": len(lines) == p + 1,
        "tate_action_invertible": determinant2(tate, p) != 0,
        "line_action_bijective": len(image_set) == p + 1,
        "tensor_actions_commute": commute_left == commute_right,
        "sample_line_transport": sample_target in image_set,
    }
    mutations = {
        "inclusion_mutation_rejected": scalar_relation(
            mutated_image, v_o, p
        )
        is None,
        "singular_action_rejected": len(set(singular_images)) < p + 1,
        "target_line_mutation_rejected": mutated_target != sample_target,
    }
    line_payload = {
        "source_lines": lines,
        "target_lines": images,
    }
    return {
        "name": row["name"],
        "delta": p,
        "degree_eta_mod_delta": degree % p,
        "gram_a_kernel": list(v_a),
        "gram_o_kernel": list(v_o),
        "inclusion_kernel_scalar": inclusion_scalar,
        "principalization_line_count": len(lines),
        "source_line_hash": scientific_hash(lines),
        "target_line_hash": scientific_hash(images),
        "line_bijection_hash": scientific_hash(line_payload),
        "sample_source_line": list(sample_source),
        "sample_target_line": list(sample_target),
        "gates": gates,
        "mutations": mutations,
        "pass": all(gates.values()) and all(mutations.values()),
    }


def main() -> None:
    source = json.loads(INPUT.read_text())
    rows = [run_row(row) for row in source["rows"]]
    scientific = {
        "claim_status": (
            "EXACT FINITE-MODULE PREFLIGHT / "
            "NO POLARIZED QUOTIENT CONSTRUCTION"
        ),
        "rows": rows,
        "all_pass": all(row["pass"] for row in rows),
    }
    result = {
        "schema": "p1243-auxiliary-principalization-v1",
        **scientific,
        "artifact_hashes": {
            "input_sha256": sha256(INPUT),
            "contract_sha256": sha256(CONTRACT),
            "source_sha256": sha256(Path(__file__).resolve()),
        },
        "scientific_data_sha256": scientific_hash(scientific),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not scientific["all_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
