#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
import resource
import sys
import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable


SCRIPT_PATH = Path(__file__).resolve()
Point = tuple[int, int] | None
Tree = int | tuple["Tree", "Tree"]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if platform.system() == "Darwin" else value * 1024)


def point_from_json(value: Any) -> Point:
    if value is None:
        return None
    return int(value[0]), int(value[1])


def point_json(point: Point) -> list[int] | None:
    return None if point is None else [point[0], point[1]]


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass
class OperationCounter:
    additions: int = 0
    doublings: int = 0
    identity_returns: int = 0
    inverse_returns: int = 0
    inversions: int = 0
    multiplications: int = 0

    def as_dict(self) -> dict[str, int]:
        return {
            "additions": self.additions,
            "doublings": self.doublings,
            "identity_returns": self.identity_returns,
            "inverse_returns": self.inverse_returns,
            "inversions": self.inversions,
            "multiplications": self.multiplications,
        }


def on_curve(point: Point, p: int, a: int, b: int) -> bool:
    if point is None:
        return True
    x, y = point
    return (y * y - (x * x * x + a * x + b)) % p == 0


def add(
    left: Point,
    right: Point,
    p: int,
    a: int,
    counter: OperationCounter | None = None,
) -> Point:
    if counter is not None:
        counter.additions += 1
    if left is None:
        if counter is not None:
            counter.identity_returns += 1
        return right
    if right is None:
        if counter is not None:
            counter.identity_returns += 1
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % p == 0:
        if counter is not None:
            counter.inverse_returns += 1
        return None
    if left == right:
        if counter is not None:
            counter.doublings += 1
            counter.multiplications += 4
    elif counter is not None:
        counter.multiplications += 2
    denominator = (2 * y1 if left == right else x2 - x1) % p
    numerator = (
        3 * x1 * x1 + a if left == right else y2 - y1
    ) % p
    if counter is not None:
        counter.inversions += 1
        counter.multiplications += 1
    slope = numerator * pow(denominator, -1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    if counter is not None:
        counter.multiplications += 3
    return x3, y3


def fold_add(
    points: Iterable[Point],
    p: int,
    a: int,
    counter: OperationCounter | None = None,
) -> Point:
    total: Point = None
    for point in points:
        total = add(total, point, p, a, counter)
    return total


@lru_cache(maxsize=None)
def full_binary_trees(start: int, count: int) -> tuple[Tree, ...]:
    if count == 1:
        return (start,)
    trees: list[Tree] = []
    for left_count in range(1, count):
        for left in full_binary_trees(start, left_count):
            for right in full_binary_trees(
                start + left_count, count - left_count
            ):
                trees.append((left, right))
    return tuple(trees)


def evaluate_tree(
    tree: Tree,
    leaves: tuple[Point, ...],
    p: int,
    a: int,
    counter: OperationCounter,
    cache: dict[Tree, Point],
) -> Point:
    if tree in cache:
        return cache[tree]
    if isinstance(tree, int):
        result = leaves[tree]
    else:
        result = add(
            evaluate_tree(tree[0], leaves, p, a, counter, cache),
            evaluate_tree(tree[1], leaves, p, a, counter, cache),
            p,
            a,
            counter,
        )
    cache[tree] = result
    return result


def projective(point: Point, scale: int, p: int) -> tuple[int, int, int]:
    if point is None:
        return 0, scale % p, 0
    return point[0] * scale % p, point[1] * scale % p, scale % p


def residual_pair(
    output: tuple[int, int, int],
    target: tuple[int, int, int],
    p: int,
) -> tuple[int, int]:
    x, y, z = output
    xq, yq, zq = target
    return (
        (zq * x - xq * z) % p,
        (zq * y - yq * z) % p,
    )


def canonical_pair(pair: tuple[int, int], p: int) -> tuple[int, int]:
    left, right = pair[0] % p, pair[1] % p
    if left == 0 and right == 0:
        return 0, 0
    pivot = left if left else right
    inverse = pow(pivot, -1, p)
    return left * inverse % p, right * inverse % p


def nonzero_scale(label: str, p: int) -> int:
    value = int.from_bytes(hashlib.sha256(label.encode("ascii")).digest(), "big")
    return 1 + value % (p - 1)


def update_digest(digest: Any, value: Any) -> None:
    digest.update(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("ascii")
    )
    digest.update(b"\n")


def curve_controls(
    generator: Point, p: int, a: int, b: int
) -> dict[str, bool]:
    if generator is None:
        raise AssertionError("generator cannot be infinity")
    inverse = (generator[0], (-generator[1]) % p)
    doubled = add(generator, generator, p, a)
    infinity_projective = projective(None, 7, p)
    finite_projective = projective(generator, 11, p)
    return {
        "generator_on_curve": on_curve(generator, p, a, b),
        "identity_left": add(None, generator, p, a) == generator,
        "identity_right": add(generator, None, p, a) == generator,
        "inverse_pair": add(generator, inverse, p, a) is None,
        "doubling_on_curve": on_curve(doubled, p, a, b),
        "infinity_self_zero": residual_pair(
            infinity_projective, projective(None, 13, p), p
        )
        == (0, 0),
        "finite_not_infinity": residual_pair(
            finite_projective, projective(None, 13, p), p
        )
        != (0, 0),
    }


def target_map(v1: dict[str, Any]) -> dict[tuple[str, str], dict[str, Point]]:
    result: dict[tuple[str, str], dict[str, Point]] = {}
    for row in v1["rows"]:
        targets = row["cuts"][0]["targets"]
        result[(row["curve_id"], row["family"])] = {
            name: point_from_json(record["target"])
            for name, record in targets.items()
        }
    return result


def run_family(
    curve: dict[str, Any],
    family: dict[str, Any],
    targets: dict[str, Point],
) -> dict[str, Any]:
    p, a, b = curve["p"], curve["a"], curve["b"]
    a_points = [
        point_from_json(value) for value in family["progression"]["points"]
    ]
    r_points = [
        point_from_json(value) for value in family["factor_base"]["points"]
    ]
    if not all(on_curve(point, p, a, b) for point in [*a_points, *r_points]):
        raise AssertionError("input point off curve")
    if any(target is None for target in targets.values()):
        raise AssertionError("recorded V1 targets must be affine")

    counter = OperationCounter()
    trees = full_binary_trees(0, 5)
    row_digest = hashlib.sha256()
    witness_digest = hashlib.sha256()
    tree_mismatches = 0
    cut2_mismatches = 0
    cut3_mismatches = 0
    zero_mismatches = 0
    scale_mismatches = 0
    mutation_control_failures = 0
    infinity_outputs = 0
    canonical_tuples = 0
    ordered_tuples = 0
    tree_evaluations = 0
    witness_counts = {name: 0 for name in targets}
    first_witness: dict[str, dict[str, Any] | None] = {
        name: None for name in targets
    }

    for r_multiset in itertools.combinations_with_replacement(
        range(len(r_points)), 4
    ):
        canonical_tuples += 1
        permutations = sorted(set(itertools.permutations(r_multiset)))
        for a_index, a_point in enumerate(a_points):
            for indices in permutations:
                ordered_tuples += 1
                leaves = (
                    a_point,
                    *(r_points[index] for index in indices),
                )
                reference = fold_add(leaves, p, a, counter)
                if reference is None:
                    infinity_outputs += 1

                cache: dict[Tree, Point] = {}
                for tree in trees:
                    tree_evaluations += 1
                    tree_mismatches += int(
                        evaluate_tree(
                            tree, leaves, p, a, counter, cache
                        )
                        != reference
                    )

                cut2 = add(
                    fold_add(leaves[:2], p, a, counter),
                    fold_add(leaves[2:], p, a, counter),
                    p,
                    a,
                    counter,
                )
                cut3 = add(
                    fold_add(leaves[:3], p, a, counter),
                    fold_add(leaves[3:], p, a, counter),
                    p,
                    a,
                    counter,
                )
                cut2_mismatches += int(cut2 != reference)
                cut3_mismatches += int(cut3 != reference)

                zero_flags: dict[str, bool] = {}
                for target_name, target in sorted(targets.items()):
                    assert target is not None
                    affine_pair = residual_pair(
                        projective(reference, 1, p),
                        projective(target, 1, p),
                        p,
                    )
                    zero = affine_pair == (0, 0)
                    zero_flags[target_name] = zero
                    zero_mismatches += int(zero != (reference == target))
                    if zero:
                        witness_counts[target_name] += 1
                        witness = {
                            "a_index": a_index,
                            "r_indices": list(indices),
                            "output": point_json(reference),
                        }
                        update_digest(
                            witness_digest,
                            [target_name, witness],
                        )
                        if first_witness[target_name] is None:
                            first_witness[target_name] = witness

                    label = (
                        f"{curve['id']}|{family['family']}|{a_index}|"
                        f"{','.join(map(str, indices))}|{target_name}"
                    )
                    output_scale = nonzero_scale(label + "|output", p)
                    target_scale = nonzero_scale(label + "|target", p)
                    scaled_pair = residual_pair(
                        projective(reference, output_scale, p),
                        projective(target, target_scale, p),
                        p,
                    )
                    scale_mismatches += int(
                        canonical_pair(scaled_pair, p)
                        != canonical_pair(affine_pair, p)
                    )
                    scale_mismatches += int(
                        (scaled_pair == (0, 0)) != zero
                    )

                update_digest(
                    row_digest,
                    [
                        a_index,
                        list(indices),
                        point_json(reference),
                        zero_flags,
                    ],
                )

    planted = targets["planted"]
    planted_witness = first_witness["planted"]
    if planted is None or planted_witness is None:
        mutation_control_failures += 1
    else:
        mutated_target = ((planted[0] + 1) % p, planted[1])
        planted_output = point_from_json(planted_witness["output"])
        mutation_control_failures += int(
            residual_pair(
                projective(planted_output, 1, p),
                projective(planted, 1, p),
                p,
            )
            != (0, 0)
        )
        mutation_control_failures += int(
            residual_pair(
                projective(planted_output, 1, p),
                projective(mutated_target, 1, p),
                p,
            )
            == (0, 0)
        )

    controls = curve_controls(
        point_from_json(curve["generator"]), p, a, b
    )
    all_valid = (
        len(trees) == 14
        and len(set(map(repr, trees))) == 14
        and all(controls.values())
        and tree_mismatches == 0
        and cut2_mismatches == 0
        and cut3_mismatches == 0
        and zero_mismatches == 0
        and scale_mismatches == 0
        and mutation_control_failures == 0
        and witness_counts["planted"] > 0
    )
    return {
        "curve_id": curve["id"],
        "p": p,
        "q": curve["q"],
        "family": family["family"],
        "a_size": len(a_points),
        "r_size": len(r_points),
        "tree_count": len(trees),
        "tree_digest": canonical_digest(trees),
        "canonical_tuple_count": canonical_tuples,
        "ordered_tuple_count": ordered_tuples,
        "tree_evaluations": tree_evaluations,
        "tree_mismatches": tree_mismatches,
        "cut2_mismatches": cut2_mismatches,
        "cut3_mismatches": cut3_mismatches,
        "zero_semantic_mismatches": zero_mismatches,
        "projective_scale_mismatches": scale_mismatches,
        "mutation_control_failures": mutation_control_failures,
        "infinity_outputs": infinity_outputs,
        "witness_counts": witness_counts,
        "first_witness": first_witness,
        "row_digest": row_digest.hexdigest(),
        "witness_digest": witness_digest.hexdigest(),
        "controls": controls,
        "operations": counter.as_dict(),
        "valid": all_valid,
        "peak_rss_bytes_after_family": rss_bytes(),
    }


def run(
    typed_path: Path,
    v1_path: Path,
    families: list[str],
) -> dict[str, Any]:
    typed = json.loads(typed_path.read_text(encoding="utf-8"))
    v1 = json.loads(v1_path.read_text(encoding="utf-8"))
    targets = target_map(v1)
    started = time.perf_counter()
    rows = []
    for instance in typed["instances"]:
        by_family = {
            record["family"]: record for record in instance["families"]
        }
        for family_name in families:
            key = (instance["curve"]["id"], family_name)
            row = run_family(
                instance["curve"],
                by_family[family_name],
                targets[key],
            )
            rows.append(row)
            print(
                f"checked {row['curve_id']} {family_name}: "
                f"{row['ordered_tuple_count']} ordered tuples",
                file=sys.stderr,
                flush=True,
            )
    return {
        "protocol": (
            "EXP-ECDLP-COORD-EXPANSION-001-"
            "direct-equality-pair-v2-independent-cross-tree"
        ),
        "claim_status": [
            "OBSERVATION",
            "TOY-EVIDENCE",
            "MODEL-BOUND",
        ],
        "source": {
            "generator_sha256": sha256_file(SCRIPT_PATH),
            "typed_input_sha256": sha256_file(typed_path),
            "v1_input_sha256": sha256_file(v1_path),
        },
        "config": {
            "typed_input": str(typed_path.resolve()),
            "v1_input": str(v1_path.resolve()),
            "families": families,
            "tree_scope": "all 14 ordered full binary trees on five leaves",
            "tuple_scope": (
                "every A point, every four-index multiset, and every "
                "distinct permutation"
            ),
        },
        "rows": rows,
        "summary": {
            "family_rows": len(rows),
            "all_rows_valid": all(row["valid"] for row in rows),
            "total_ordered_tuples": sum(
                row["ordered_tuple_count"] for row in rows
            ),
            "total_tree_evaluations": sum(
                row["tree_evaluations"] for row in rows
            ),
            "total_planted_witnesses": sum(
                row["witness_counts"]["planted"] for row in rows
            ),
            "total_held_out_witnesses": sum(
                row["witness_counts"]["held_out"] for row in rows
            ),
            "total_infinity_outputs": sum(
                row["infinity_outputs"] for row in rows
            ),
            "factor_polynomials_independently_verified": False,
            "succinct_index_constructed": False,
            "algorithm_promotion_gate": False,
            "breakthrough_claim": False,
            "boundary": (
                "Independent affine semantic audit only. It does not "
                "verify V1 polynomial factors or construct an index."
            ),
        },
        "peak_rss_bytes": rss_bytes(),
        "total_wall_seconds": time.perf_counter() - started,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("typed_result", type=Path)
    parser.add_argument("v1_result", type=Path)
    parser.add_argument("--families", nargs="+", required=True)
    args = parser.parse_args()
    result = run(args.typed_result, args.v1_result, args.families)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result["summary"]["all_rows_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
