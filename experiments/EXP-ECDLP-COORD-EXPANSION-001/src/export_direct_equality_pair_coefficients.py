#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import platform
import resource
import sys
import time
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
V1_SOURCE = SCRIPT_PATH.with_name("direct_equality_pair.py")


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


V1 = load_module("direct_equality_pair_for_export", V1_SOURCE)
DIRECT = V1.DIRECT
NORM = V1.NORM
TT = V1.TT
Point = V1.Point


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def digest(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if platform.system() == "Darwin" else value * 1024)


def v1_rows(raw: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (row["curve_id"], row["family"]): row for row in raw["rows"]
    }


def v2_rows(raw: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (row["curve_id"], row["family"]): row for row in raw["rows"]
    }


def coordinate_vectors(
    suffix_indices: list[tuple[int, ...]],
    r_points: list[Point],
    p: int,
    a: int,
    b: int,
    monomials: list[tuple[int, int, int]],
) -> list[list[list[int]]]:
    rows = []
    for indices in suffix_indices:
        coordinates = V1.derive_suffix_coordinates(
            [r_points[index] for index in indices], p, a, b
        )
        rows.append(
            [
                DIRECT.coefficient_vector(poly, monomials)
                for poly in coordinates
            ]
        )
    return rows


def mutation_control(
    vectors: list[list[list[int]]],
    monomials: list[tuple[int, int, int]],
    a_points: list[Point],
    p: int,
) -> dict[str, Any]:
    mutated = [
        [list(vector) for vector in coordinate]
        for coordinate in vectors[:1]
    ]
    coordinate_index = 0
    coefficient_index = next(
        (
            index
            for index, value in enumerate(mutated[0][coordinate_index])
            if value
        ),
        0,
    )
    before = digest(mutated)
    mutated[0][coordinate_index][coefficient_index] = (
        mutated[0][coordinate_index][coefficient_index] + 1
    ) % p
    after = digest(mutated)
    evaluation_changed = any(
        sum(
            coefficient * basis_value
            for coefficient, basis_value in zip(
                vectors[0][coordinate_index],
                DIRECT.evaluate_basis(
                    monomials, NORM.affine_to_projective(point), p
                ),
            )
        )
        % p
        != sum(
            coefficient * basis_value
            for coefficient, basis_value in zip(
                mutated[0][coordinate_index],
                DIRECT.evaluate_basis(
                    monomials, NORM.affine_to_projective(point), p
                ),
            )
        )
        % p
        for point in a_points
    )
    return {
        "coordinate_index": coordinate_index,
        "coefficient_index": coefficient_index,
        "before_digest": before,
        "after_digest": after,
        "digest_changed": before != after,
        "evaluation_changed": evaluation_changed,
    }


def witness_checks(
    cut: int,
    monomials: list[tuple[int, int, int]],
    vectors: list[list[list[int]]],
    a_points: list[Point],
    r_points: list[Point],
    targets: dict[str, Point],
    first_witness: dict[str, dict[str, Any] | None],
    p: int,
    a: int,
    b: int,
) -> dict[str, Any]:
    checks: dict[str, Any] = {}
    suffix_size = len(r_points)
    for target_name, witness in first_witness.items():
        if witness is None:
            checks[target_name] = {
                "present": False,
                "residual_zero": None,
                "affine_output_matches": None,
            }
            continue
        indices = [int(value) for value in witness["r_indices"]]
        prefix_points = [
            a_points[int(witness["a_index"])],
            *(r_points[index] for index in indices[: cut - 1]),
        ]
        suffix = tuple(indices[cut - 1 :])
        suffix_flat_index = 0
        for index in suffix:
            suffix_flat_index = suffix_flat_index * suffix_size + index
        prefix = DIRECT.prefix_projective(
            prefix_points, p, a, b
        )
        basis_values = DIRECT.evaluate_basis(monomials, prefix, p)
        output = tuple(
            sum(
                coefficient * value
                for coefficient, value in zip(vector, basis_values)
            )
            % p
            for vector in vectors[suffix_flat_index]
        )
        target = targets[target_name]
        residual = V1.residual_pair(output, target, p)
        affine_output = TT.projective_to_affine(output, p)
        mutated_target = ((target[0] + 1) % p, target[1])
        checks[target_name] = {
            "present": True,
            "a_index": int(witness["a_index"]),
            "r_indices": indices,
            "suffix_flat_index": suffix_flat_index,
            "output": list(output),
            "affine_output": V1.TYPED.point_json(affine_output),
            "residual": list(residual),
            "residual_zero": residual == (0, 0),
            "affine_output_matches": affine_output == target,
            "mutated_target_residual_nonzero": (
                V1.residual_pair(output, mutated_target, p) != (0, 0)
            ),
        }
    return checks


def run_cut(
    cut: int,
    curve: dict[str, Any],
    family: dict[str, Any],
    v1_cut: dict[str, Any],
    v2_row: dict[str, Any],
    chunk_size: int,
) -> dict[str, Any]:
    p, a, b = curve["p"], curve["a"], curve["b"]
    a_points = [
        NORM.point_from_json(value)
        for value in family["progression"]["points"]
    ]
    r_points = [
        NORM.point_from_json(value)
        for value in family["factor_base"]["points"]
    ]
    targets = {
        name: NORM.point_from_json(record["target"])
        for name, record in v1_cut["targets"].items()
    }
    degree = 2 ** (5 - cut)
    monomials = DIRECT.basis(degree)
    suffix_axes = 5 - cut
    suffix_indices = list(
        itertools.product(
            *(range(len(r_points)) for _ in range(suffix_axes))
        )
    )
    vectors = coordinate_vectors(
        suffix_indices, r_points, p, a, b, monomials
    )
    chunks = []
    for start in range(0, len(vectors), chunk_size):
        stop = min(len(vectors), start + chunk_size)
        chunks.append(
            {
                "start": start,
                "stop": stop,
                "sha256": digest(vectors[start:stop]),
            }
        )
    samples = {
        str(index): vectors[index]
        for index in sorted({0, len(vectors) // 2, len(vectors) - 1})
    }
    target_rows = {}
    for target_name, target in targets.items():
        vx, vy = V1.specialize_vectors(vectors, target, p)
        recorded = v1_cut["targets"][target_name]
        target_rows[target_name] = {
            "vx_digest": digest(vx),
            "vy_digest": digest(vy),
            "vx_rank": DIRECT.vector_rank(vx, p),
            "vy_rank": DIRECT.vector_rank(vy, p),
            "combined_rank": DIRECT.vector_rank(
                [[*left, *right] for left, right in zip(vx, vy)], p
            ),
            "matches_v1": (
                digest(vx) == recorded["vx_digest"]
                and digest(vy) == recorded["vy_digest"]
                and DIRECT.vector_rank(vx, p) == recorded["vx_rank"]
                and DIRECT.vector_rank(vy, p) == recorded["vy_rank"]
                and DIRECT.vector_rank(
                    [[*left, *right] for left, right in zip(vx, vy)], p
                )
                == recorded["combined_v_rank"]
            ),
        }
    coordinate_ranks = [
        DIRECT.vector_rank(
            [coordinate[index] for coordinate in vectors], p
        )
        for index in range(3)
    ]
    nnz = sum(
        value != 0
        for coordinate in vectors
        for vector in coordinate
        for value in vector
    )
    return {
        "cut": cut,
        "degree": degree,
        "basis": [list(monomial) for monomial in monomials],
        "basis_dimension": len(monomials),
        "suffix_count": len(vectors),
        "chunk_size": chunk_size,
        "chunks": chunks,
        "coordinate_digest": digest(vectors),
        "coordinate_digest_matches_v1": (
            digest(vectors) == v1_cut["coordinate_digest"]
        ),
        "coordinate_ranks": coordinate_ranks,
        "coefficient_field_elements": (
            len(vectors) * 3 * len(monomials)
        ),
        "coefficient_nonzeros": nnz,
        "samples": samples,
        "targets": target_rows,
        "witness_checks": witness_checks(
            cut,
            monomials,
            vectors,
            a_points,
            r_points,
            targets,
            v2_row["first_witness"],
            p,
            a,
            b,
        ),
        "coefficient_mutation_control": mutation_control(
            vectors, monomials, a_points, p
        ),
    }


def run(
    typed_path: Path,
    v1_path: Path,
    v2_path: Path,
    families: list[str],
    chunk_size: int,
) -> dict[str, Any]:
    typed = json.loads(typed_path.read_text(encoding="utf-8"))
    v1_raw = json.loads(v1_path.read_text(encoding="utf-8"))
    v2_raw = json.loads(v2_path.read_text(encoding="utf-8"))
    old_rows = v1_rows(v1_raw)
    semantic_rows = v2_rows(v2_raw)
    started = time.perf_counter()
    rows = []
    for instance in typed["instances"]:
        by_family = {
            record["family"]: record for record in instance["families"]
        }
        for family_name in families:
            key = (instance["curve"]["id"], family_name)
            old_row = old_rows[key]
            cuts = [
                run_cut(
                    cut,
                    instance["curve"],
                    by_family[family_name],
                    next(item for item in old_row["cuts"] if item["cut"] == cut),
                    semantic_rows[key],
                    chunk_size,
                )
                for cut in (2, 3)
            ]
            valid = all(
                cut["coordinate_digest_matches_v1"]
                and cut["basis_dimension"] == 3 * cut["degree"]
                and all(target["matches_v1"] for target in cut["targets"].values())
                and all(
                    (
                        not witness["present"]
                        or (
                            witness["residual_zero"]
                            and witness["affine_output_matches"]
                            and witness["mutated_target_residual_nonzero"]
                        )
                    )
                    for witness in cut["witness_checks"].values()
                )
                and cut["coefficient_mutation_control"]["digest_changed"]
                and cut["coefficient_mutation_control"]["evaluation_changed"]
                for cut in cuts
            )
            rows.append(
                {
                    "curve_id": key[0],
                    "p": instance["curve"]["p"],
                    "q": instance["curve"]["q"],
                    "family": family_name,
                    "cuts": cuts,
                    "valid": valid,
                    "peak_rss_bytes_after_family": rss_bytes(),
                }
            )
            print(
                f"exported {key[0]} {family_name}",
                file=sys.stderr,
                flush=True,
            )
    return {
        "protocol": (
            "EXP-ECDLP-COORD-EXPANSION-001-"
            "direct-equality-pair-v3-independent-coefficients"
        ),
        "claim_status": [
            "OBSERVATION",
            "TOY-EVIDENCE",
            "MODEL-BOUND",
        ],
        "source": {
            "exporter_sha256": file_hash(SCRIPT_PATH),
            "v1_source_sha256": file_hash(V1_SOURCE),
            "typed_input_sha256": file_hash(typed_path),
            "v1_input_sha256": file_hash(v1_path),
            "v2_input_sha256": file_hash(v2_path),
        },
        "config": {
            "typed_input": str(typed_path.resolve()),
            "v1_input": str(v1_path.resolve()),
            "v2_input": str(v2_path.resolve()),
            "families": families,
            "chunk_size": chunk_size,
        },
        "rows": rows,
        "summary": {
            "family_rows": len(rows),
            "all_exports_valid": all(row["valid"] for row in rows),
            "coefficient_chunks_emitted": sum(
                len(cut["chunks"]) for row in rows for cut in row["cuts"]
            ),
            "coefficient_field_elements": sum(
                cut["coefficient_field_elements"]
                for row in rows
                for cut in row["cuts"]
            ),
            "independent_coefficient_verification_complete": False,
            "succinct_index_constructed": False,
            "algorithm_promotion_gate": False,
            "breakthrough_claim": False,
        },
        "peak_rss_bytes": rss_bytes(),
        "total_wall_seconds": time.perf_counter() - started,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("typed_result", type=Path)
    parser.add_argument("v1_result", type=Path)
    parser.add_argument("v2_result", type=Path)
    parser.add_argument("--families", nargs="+", required=True)
    parser.add_argument("--chunk-size", type=int, default=64)
    args = parser.parse_args()
    result = run(
        args.typed_result,
        args.v1_result,
        args.v2_result,
        args.families,
        args.chunk_size,
    )
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result["summary"]["all_exports_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
