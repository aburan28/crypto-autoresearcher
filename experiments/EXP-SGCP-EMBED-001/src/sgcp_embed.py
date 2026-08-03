#!/usr/bin/env python3
"""Coordinate-only SGCP-EMBED-001 certificate builder.

The builder deliberately has no scalar-multiplication routine or scalar table.
It constructs every semantic object from affine coordinates and EC addition.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import math
import os
import subprocess
import sys
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence


SCHEMA = "sgcp-embed-001-certificate-v1"
EXPERIMENT_ID = "SGCP-EMBED-001"
LITERATURE_SHA256 = "169604e8e0c2bf13cfc2d14067868af2e8c41b8346395e160b2d9103f1e31a60"
SGGM_PDF_SHA256 = "82b40c277230d0603e5b87a3f6f5d045a7b3b8672f15f7e8ae983878296af66f"
CONTROL_REGISTRY_SHA256 = "cf07a4dedcc7d7895df7959aa809bee9fc8aefeff04a1ef643e7bf211173e5ca"
MATHEMATICAL_CONTRACT_SHA256 = "f2f7c897bfb240708055fc06e09f4bba68b2e35703e02585b564761474a71e73"
EXPERIMENT_CONTRACT_SHA256 = "36e624cc53d45e46fffcf520e18bd8f54e87275f86b71ef94d2d6af7ed4a69c4"
FIXTURE = {"bits": 5, "p": 19, "a": 2, "b": 9, "q": 23, "trace": -3, "generator": [0, 3]}
FROZEN_REVIEW_ROOT = Path("/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy")
SCRIPT_PATH = Path(__file__).resolve()
VERIFIER_PATH = SCRIPT_PATH.with_name("verify_sgcp_embed.py")
CONTROL_REGISTRY_PATH = SCRIPT_PATH.parents[1] / "control-registry-v2.json"
REPO_ROOT = SCRIPT_PATH.parents[3]
MATHEMATICAL_CONTRACT_PATH = REPO_ROOT / "notes" / "sgcp_embed_001_contract_20260717.md"
EXPERIMENT_CONTRACT_PATH = SCRIPT_PATH.parents[1] / "contract.md"
LITERATURE_PATH = REPO_ROOT / "notes" / "structured_group_coordinate_predicates_literature_20260717.md"
PREFLIGHT_DIR = SCRIPT_PATH.parents[1] / "preflight"
CERTIFICATE_PATH = PREFLIGHT_DIR / "sgcp-embed-001-5bit.json"
EXPECTED_BRANCH = "codex/sgcp-embed-001"
EXPECTED_BUILDER_OPERATIONS = {
    "point_add_calls": 1612220,
    "point_doublings": 302627,
    "field_inversions": 967579,
    "field_multiplications": 3205364,
    "multiset_evaluations": 664529,
    "injectivity_checks": 21161,
    "associativity_triples": 106863,
    "optimizer_nodes": 20736,
}

Point = tuple[int, int] | None
Multiset = tuple[int, ...]
Label = str


@dataclass
class BuildOps:
    point_add_calls: int = 0
    point_doublings: int = 0
    field_inversions: int = 0
    field_multiplications: int = 0
    multiset_evaluations: int = 0
    injectivity_checks: int = 0
    associativity_triples: int = 0
    optimizer_nodes: int = 0


class Curve:
    def __init__(self, p: int, a: int, b: int, ops: BuildOps | None = None) -> None:
        self.p = require_exact_int(p, "p", 5)
        self.a = require_exact_int(a, "a") % p
        self.b = require_exact_int(b, "b") % p
        self.ops = ops
        if (4 * pow(self.a, 3, p) + 27 * pow(self.b, 2, p)) % p == 0:
            raise ValueError("singular curve")

    def on_curve(self, point: Point) -> bool:
        if point is None:
            return True
        x, y = point
        return (y * y - (x * x * x + self.a * x + self.b)) % self.p == 0

    def neg(self, point: Point) -> Point:
        if point is None:
            return None
        return point[0], (-point[1]) % self.p

    def add(self, left: Point, right: Point) -> Point:
        if self.ops is not None:
            self.ops.point_add_calls += 1
        if left is None:
            return right
        if right is None:
            return left
        x1, y1 = left
        x2, y2 = right
        if x1 == x2 and (y1 + y2) % self.p == 0:
            return None
        if left == right:
            if self.ops is not None:
                self.ops.point_doublings += 1
                self.ops.field_inversions += 1
                self.ops.field_multiplications += 4
            numerator = (3 * x1 * x1 + self.a) % self.p
            denominator = (2 * y1) % self.p
        else:
            if self.ops is not None:
                self.ops.field_inversions += 1
                self.ops.field_multiplications += 3
            numerator = (y2 - y1) % self.p
            denominator = (x2 - x1) % self.p
        slope = numerator * pow(denominator, -1, self.p) % self.p
        x3 = (slope * slope - x1 - x2) % self.p
        y3 = (slope * (x1 - x3) - y1) % self.p
        result = (x3, y3)
        if not self.on_curve(result):
            raise AssertionError("affine addition left the curve")
        return result


def require_exact_int(value: Any, label: str, minimum: int | None = None) -> int:
    if type(value) is not int:
        raise TypeError(f"{label} must be an exact integer, got {type(value).__name__}")
    if minimum is not None and value < minimum:
        raise ValueError(f"{label} must be at least {minimum}")
    return value


def is_prime(value: int) -> bool:
    value = require_exact_int(value, "prime candidate")
    if value < 2:
        return False
    for divisor in range(2, math.isqrt(value) + 1):
        if value % divisor == 0:
            return False
    return True


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stable_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode("ascii")


def stable_digest(value: Any) -> str:
    return hashlib.sha256(stable_json(value)).hexdigest()


def set_fixed_point_json_size(record: dict[str, Any], field: str) -> None:
    if field in record:
        raise ValueError(f"fixed-point JSON size field already exists: {field}")
    candidate = 0
    for _ in range(32):
        record[field] = candidate
        observed = len(stable_json(record))
        if observed == candidate:
            return
        candidate = observed
    raise AssertionError(f"fixed-point JSON size did not converge for {field}")


def operation_delta(
    before: dict[str, int], after: dict[str, int]
) -> dict[str, int]:
    if set(before) != set(after):
        raise AssertionError("operation counter key set changed during row build")
    delta = {key: after[key] - before[key] for key in before}
    if any(value < 0 for value in delta.values()):
        raise AssertionError("operation counter decreased during row build")
    return delta


def loads_json_strict(text: str, source: str) -> Any:
    def object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"{source}: duplicate JSON key {key!r}")
            result[key] = value
        return result

    def bad_constant(value: str) -> Any:
        raise ValueError(f"{source}: non-finite JSON constant {value!r}")

    return json.loads(text, object_pairs_hook=object_pairs, parse_constant=bad_constant)


def require_bound_file(path: Path, expected: Path, expected_sha256: str, label: str) -> Path:
    resolved = path.resolve(strict=True)
    expected_resolved = expected.resolve(strict=True)
    if resolved != expected_resolved:
        raise AssertionError(
            f"{label} path mismatch: expected {expected_resolved}, observed {resolved}"
        )
    actual_sha256 = sha256_file(resolved)
    if actual_sha256 != expected_sha256:
        raise AssertionError(
            f"{label} hash mismatch: expected {expected_sha256}, observed {actual_sha256}"
        )
    return resolved


def git_text(*args: str) -> str:
    process = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return process.stdout.strip()


def launch_context() -> dict[str, Any]:
    return {
        "cwd": str(Path.cwd().resolve()),
        "branch": git_text("branch", "--show-current"),
        "git_commit": git_text("rev-parse", "HEAD"),
        "git_status_porcelain_v1": git_text(
            "status", "--porcelain=v1", "--untracked-files=all"
        ),
    }


def require_canonical_launch_context(output: Path) -> Path:
    resolved_output = output.resolve()
    if Path.cwd().resolve() != REPO_ROOT.resolve():
        raise AssertionError(f"canonical builder cwd must be {REPO_ROOT}")
    if git_text("branch", "--show-current") != EXPECTED_BRANCH:
        raise AssertionError(f"canonical builder branch must be {EXPECTED_BRANCH}")
    dirty = git_text("status", "--porcelain=v1", "--untracked-files=all")
    if dirty:
        raise AssertionError("canonical builder requires a clean Git worktree")
    if resolved_output != CERTIFICATE_PATH.resolve():
        raise ValueError(f"canonical output must be exactly {CERTIFICATE_PATH}")
    if resolved_output.exists():
        raise FileExistsError(f"canonical output already exists: {resolved_output}")
    return resolved_output


def require_locked_runner_runtime() -> None:
    if Path.cwd().resolve() != REPO_ROOT.resolve():
        raise AssertionError(f"locked runner cwd must be {REPO_ROOT}")
    observed = {
        "isolated": bool(sys.flags.isolated),
        "no_site": bool(sys.flags.no_site),
        "dont_write_bytecode": bool(sys.flags.dont_write_bytecode),
    }
    if observed != {"isolated": True, "no_site": True, "dont_write_bytecode": True}:
        raise AssertionError(
            "locked runner requires Python isolation flags -I -S -B; "
            f"observed {observed}"
        )


def load_control_registry() -> dict[str, Any]:
    actual = sha256_file(CONTROL_REGISTRY_PATH)
    if actual != CONTROL_REGISTRY_SHA256:
        raise AssertionError(
            f"control registry hash mismatch: expected {CONTROL_REGISTRY_SHA256}, observed {actual}"
        )
    value = loads_json_strict(
        CONTROL_REGISTRY_PATH.read_text(encoding="utf-8"), str(CONTROL_REGISTRY_PATH)
    )
    if value.get("registry", {}).get("schema") != "sgcp-embed-001-control-registry-v2":
        raise AssertionError("unexpected control registry schema")
    return value


def exact_ratio(numerator: int, denominator: int) -> dict[str, int]:
    numerator = require_exact_int(numerator, "ratio numerator", 0)
    denominator = require_exact_int(denominator, "ratio denominator", 1)
    divisor = math.gcd(numerator, denominator)
    return {"numerator": numerator // divisor, "denominator": denominator // divisor}


def deep_size(value: Any) -> int:
    seen: set[int] = set()

    def visit(item: Any) -> int:
        identity = id(item)
        if identity in seen:
            return 0
        seen.add(identity)
        total = sys.getsizeof(item)
        if isinstance(item, dict):
            total += sum(visit(key) + visit(child) for key, child in item.items())
        elif isinstance(item, (list, tuple, set, frozenset)):
            total += sum(visit(child) for child in item)
        return total

    return visit(value)


def point_key(point: Point) -> tuple[int, int, int]:
    return (-1, 0, 0) if point is None else (0, point[0], point[1])


def point_label(point: Point) -> Label:
    return "O" if point is None else f"{point[0]}:{point[1]}"


def label_point(label: Label) -> Point:
    if label == "O":
        return None
    x_text, y_text = label.split(":", 1)
    return int(x_text), int(y_text)


def encode_multiset(multiset: Multiset) -> list[int]:
    return list(multiset)


def enumerate_points(curve: Curve) -> list[Point]:
    points: list[Point] = [None]
    for x in range(curve.p):
        for y in range(curve.p):
            point = (x, y)
            if curve.on_curve(point):
                points.append(point)
    return sorted(points, key=point_key)


def j_invariant(curve: Curve) -> int:
    four_a3 = 4 * pow(curve.a, 3, curve.p) % curve.p
    denominator = (four_a3 + 27 * pow(curve.b, 2, curve.p)) % curve.p
    return 1728 * four_a3 * pow(denominator, -1, curve.p) % curve.p


def polynomial_from_roots(roots: Sequence[int], modulus: int) -> list[int]:
    coefficients = [1]
    for root in roots:
        updated = [0] * (len(coefficients) + 1)
        for degree, coefficient in enumerate(coefficients):
            updated[degree] = (updated[degree] - root * coefficient) % modulus
            updated[degree + 1] = (updated[degree + 1] + coefficient) % modulus
        coefficients = updated
    return coefficients


def make_factor_base(points: Sequence[Point], size: int) -> dict[str, Any]:
    size = require_exact_int(size, "factor-base size", 2)
    if size % 2:
        raise ValueError("factor-base size must be even")
    by_x: dict[int, list[Point]] = defaultdict(list)
    for point in points:
        if point is not None:
            by_x[point[0]].append(point)
    roots = sorted(x for x, fiber in by_x.items() if len(fiber) == 2)[: size // 2]
    factor_points = sorted(
        (point for x in roots for point in by_x[x]), key=point_key
    )
    if len(factor_points) != size:
        raise AssertionError(f"only found {len(factor_points)} factor-base points for B={size}")
    labels = [point_label(point) for point in factor_points]
    sources = []
    for index, point in enumerate(factor_points):
        if point is None:
            raise AssertionError("factor base unexpectedly contains the identity")
        x, y = point
        smaller_y = min(y, (-y) % FIXTURE["p"])
        sources.append(
            {
                "factor_index": index,
                "root_index": roots.index(x),
                "x": x,
                "sign_bit": 0 if y == smaller_y else 1,
                "y": y,
                "point": [x, y],
                "source_tag": f"x={x}|y={y}",
            }
        )
    return {
        "B": size,
        "L_roots": roots,
        "L_polynomial_coefficients_ascending_mod_p": polynomial_from_roots(
            roots, FIXTURE["p"]
        ),
        "labels": labels,
        "points": factor_points,
        "canonical_sources": sources,
        "discarded_source_tags": [],
    }


def evaluate_multiset(curve: Curve, factor_points: Sequence[Point], multiset: Multiset) -> Point:
    if curve.ops is not None:
        curve.ops.multiset_evaluations += 1
    result: Point = None
    for index in multiset:
        result = curve.add(result, factor_points[index])
    return result


def submultisets(multiset: Multiset) -> set[Multiset]:
    result: set[Multiset] = {()}
    for length in range(1, len(multiset) + 1):
        result.update(itertools.combinations(multiset, length))
    return result


def downward_family(size: int, maxima: Iterable[Multiset]) -> set[Multiset]:
    family: set[Multiset] = {(), *((index,) for index in range(size))}
    for maximum in maxima:
        family.update(submultisets(tuple(sorted(maximum))))
    return family


def collision_kind(left: Multiset, right: Multiset, point: Point) -> str:
    if point is None:
        return "nonempty_identity"
    if 1 in (len(left), len(right)):
        return "singleton_composite"
    if len(left) == len(right):
        return f"same_degree_{len(left)}"
    return f"cross_degree_{min(len(left), len(right))}_{max(len(left), len(right))}"


def evaluate_family(
    curve: Curve, factor_points: Sequence[Point], family: Iterable[Multiset]
) -> tuple[dict[Multiset, Point], list[dict[str, Any]]]:
    if curve.ops is not None:
        curve.ops.injectivity_checks += 1
    evaluations: dict[Multiset, Point] = {}
    by_point: dict[Point, list[Multiset]] = defaultdict(list)
    for multiset in sorted(set(family), key=lambda item: (len(item), item)):
        point = evaluate_multiset(curve, factor_points, multiset)
        evaluations[multiset] = point
        by_point[point].append(multiset)
    collisions: list[dict[str, Any]] = []
    for point in sorted(by_point, key=point_key):
        values = by_point[point]
        if len(values) < 2:
            continue
        for left, right in itertools.combinations(values, 2):
            collisions.append(
                {
                    "kind": collision_kind(left, right, point),
                    "left": encode_multiset(left),
                    "right": encode_multiset(right),
                    "point": point_label(point),
                }
            )
    return evaluations, collisions


def build_raw_witnesses(
    curve: Curve, factor_points: Sequence[Point]
) -> dict[str, Any]:
    degree2 = list(itertools.combinations_with_replacement(range(len(factor_points)), 2))
    degree2_by_point: dict[Point, list[Multiset]] = defaultdict(list)
    for multiset in degree2:
        degree2_by_point[evaluate_multiset(curve, factor_points, multiset)].append(multiset)

    canonical2: list[dict[str, Any]] = []
    for point in sorted(degree2_by_point, key=point_key):
        if point is None:
            continue
        witnesses = sorted(degree2_by_point[point])
        canonical2.append(
            {
                "point": point,
                "multiset": witnesses[0],
                "alternatives": witnesses[1:],
            }
        )

    raw4: list[dict[str, Any]] = []
    for left_index, right_index in itertools.combinations_with_replacement(
        range(len(canonical2)), 2
    ):
        left = canonical2[left_index]
        right = canonical2[right_index]
        multiset = tuple(sorted(left["multiset"] + right["multiset"]))
        point = curve.add(left["point"], right["point"])
        raw4.append(
            {
                "point": point,
                "multiset": multiset,
                "parents": tuple(sorted((left["multiset"], right["multiset"]))),
            }
        )

    degree4_by_point: dict[Point, list[dict[str, Any]]] = defaultdict(list)
    for witness in raw4:
        degree4_by_point[witness["point"]].append(witness)

    degree4_by_multiset: dict[Multiset, list[dict[str, Any]]] = defaultdict(list)
    for witness in raw4:
        degree4_by_multiset[witness["multiset"]].append(witness)
    balanced_candidates: list[dict[str, Any]] = []
    for multiset in sorted(degree4_by_multiset):
        witnesses = sorted(
            degree4_by_multiset[multiset], key=lambda item: item["parents"]
        )
        points = {witness["point"] for witness in witnesses}
        if len(points) != 1:
            raise AssertionError("one formal multiset has inconsistent EC evaluations")
        balanced_candidates.append(
            {
                "point": witnesses[0]["point"],
                "multiset": multiset,
                "parent_pairs": [witness["parents"] for witness in witnesses],
            }
        )

    canonical4: list[dict[str, Any]] = []
    for point in sorted(degree4_by_point, key=point_key):
        if point is None:
            continue
        witnesses = sorted(
            degree4_by_point[point], key=lambda item: (item["multiset"], item["parents"])
        )
        selected = witnesses[0]
        canonical4.append(
            {
                "point": point,
                "multiset": selected["multiset"],
                "parents": selected["parents"],
                "alternatives": witnesses[1:],
            }
        )

    raw_a4 = sorted({witness["point"] for witness in raw4}, key=point_key)
    return {
        "degree2": degree2,
        "degree2_by_point": degree2_by_point,
        "canonical2": canonical2,
        "raw4": raw4,
        "degree4_by_point": degree4_by_point,
        "degree4_by_multiset": degree4_by_multiset,
        "balanced_candidates": balanced_candidates,
        "canonical4": canonical4,
        "raw_a4": raw_a4,
    }


def support_and_histogram(
    curve: Curve, points: Sequence[Point]
) -> tuple[set[Point], Counter[Point], dict[Point, list[list[Label]]]]:
    support: set[Point] = set()
    histogram: Counter[Point] = Counter()
    witnesses: dict[Point, list[list[Label]]] = defaultdict(list)
    ordered_points = sorted(points, key=point_key)
    for left_index, left in enumerate(ordered_points):
        for right in ordered_points[left_index:]:
            output = curve.add(left, right)
            support.add(output)
            histogram[output] += 1
            witnesses[output].append([point_label(left), point_label(right)])
    return support, histogram, dict(witnesses)


def normalize_edges(
    labels: Sequence[Label], edges: Iterable[tuple[Label, Label, Label]]
) -> list[tuple[Label, Label, Label]]:
    order = {label: index for index, label in enumerate(labels)}
    normalized: set[tuple[Label, Label, Label]] = set()
    for left, right, output in edges:
        if order[left] > order[right]:
            left, right = right, left
        normalized.add((left, right, output))
    return sorted(normalized, key=lambda edge: (order[edge[0]], order[edge[1]], order[edge[2]]))


def closure_edges(
    labels: Sequence[Label], family: set[Multiset], evaluations: dict[Multiset, Point]
) -> list[tuple[Label, Label, Label]]:
    nonempty = sorted((item for item in family if item), key=lambda item: (len(item), item))
    edges: list[tuple[Label, Label, Label]] = []
    for left_index, left in enumerate(nonempty):
        for right in nonempty[left_index:]:
            union = tuple(sorted(left + right))
            if union not in family:
                continue
            edges.append(
                (
                    point_label(evaluations[left]),
                    point_label(evaluations[right]),
                    point_label(evaluations[union]),
                )
            )
    return normalize_edges(labels, edges)


def star_lookup(
    labels: Sequence[Label], identity: Label, edges: Sequence[tuple[Label, Label, Label]]
) -> Callable[[Label, Label], Label | None]:
    order = {label: index for index, label in enumerate(labels)}
    table: dict[tuple[Label, Label], Label] = {}
    for left, right, output in edges:
        key = (left, right) if order[left] <= order[right] else (right, left)
        previous = table.get(key)
        if previous is not None and previous != output:
            raise AssertionError(f"conflicting star outputs for {key}: {previous}, {output}")
        table[key] = output

    def star(left: Label, right: Label) -> Label | None:
        if left == identity:
            return right
        if right == identity:
            return left
        key = (left, right) if order[left] <= order[right] else (right, left)
        return table.get(key)

    return star


def associativity_check(
    labels: Sequence[Label],
    star: Callable[[Label, Label], Label | None],
    ops: BuildOps | None,
    sparse: bool = False,
    edges: Sequence[tuple[Label, Label, Label]] = (),
) -> dict[str, Any]:
    triples: Iterable[tuple[Label, Label, Label]]
    if sparse:
        directed: dict[tuple[Label, Label], Label] = {}
        for left, right, output in edges:
            directed[(left, right)] = output
            directed[(right, left)] = output
        candidate_triples: set[tuple[Label, Label, Label]] = set()
        by_left: dict[Label, list[tuple[Label, Label]]] = defaultdict(list)
        by_output: dict[Label, list[tuple[Label, Label]]] = defaultdict(list)
        for (left, right), output in directed.items():
            by_left[left].append((right, output))
            by_output[output].append((left, right))
        for middle, first_edges in by_output.items():
            for left, center in first_edges:
                for right, _ in by_left.get(middle, []):
                    candidate_triples.add((left, center, right))
        for middle, second_edges in by_left.items():
            for right, _ in second_edges:
                for left, center in by_output.get(middle, []):
                    candidate_triples.add((left, center, right))
        triples = sorted(candidate_triples)
        method = "exact_sparse_composable_chains"
    else:
        triples = itertools.product(labels, repeat=3)
        method = "literal_cubic"

    checked = 0
    for left, middle, right in triples:
        checked += 1
        if ops is not None:
            ops.associativity_triples += 1
        left_inner = star(left, middle)
        left_outer = None if left_inner is None else star(left_inner, right)
        right_inner = star(middle, right)
        right_outer = None if right_inner is None else star(left, right_inner)
        if (left_outer is None) != (right_outer is None) or (
            left_outer is not None and left_outer != right_outer
        ):
            return {
                "valid": False,
                "method": method,
                "checked_triples": checked,
                "counterexample": {
                    "triple": [left, middle, right],
                    "left_inner": left_inner,
                    "left_outer": left_outer,
                    "right_inner": right_inner,
                    "right_outer": right_outer,
                },
            }
    return {"valid": True, "method": method, "checked_triples": checked, "counterexample": None}


def factorization_check(
    labels: Sequence[Label], identity: Label, edges: Sequence[tuple[Label, Label, Label]]
) -> dict[str, Any]:
    parents: dict[Label, set[tuple[Label, Label]]] = defaultdict(set)
    for left, right, output in edges:
        if left != output and right != output:
            parents[output].add(tuple(sorted((left, right))))
    primes = sorted(label for label in labels if label != identity and not parents[label])
    factorizations: dict[Label, set[tuple[Label, ...]]] = {identity: {()}}
    for prime in primes:
        factorizations[prime] = {(prime,)}

    changed = True
    rounds = 0
    while changed and rounds <= len(labels):
        changed = False
        rounds += 1
        for output, pairs in parents.items():
            output_set = factorizations.setdefault(output, set())
            before = len(output_set)
            for left, right in pairs:
                for left_factors in factorizations.get(left, set()):
                    for right_factors in factorizations.get(right, set()):
                        output_set.add(tuple(sorted(left_factors + right_factors)))
                        if len(output_set) > 64:
                            break
                    if len(output_set) > 64:
                        break
                if len(output_set) > 64:
                    break
            changed |= len(output_set) != before

    failures = []
    for label in labels:
        values = factorizations.get(label, set())
        if len(values) != 1:
            failures.append(
                {
                    "label": label,
                    "factorization_count": len(values),
                    "prime_multisets": [list(value) for value in sorted(values)[:8]],
                    "truncated": len(values) > 8,
                }
            )
    return {
        "valid": not failures,
        "prime_labels": primes,
        "prime_count": len(primes),
        "failures": failures,
        "fixed_point_rounds": rounds,
    }


def acyclicity_check(
    labels: Sequence[Label], edges: Sequence[tuple[Label, Label, Label]]
) -> dict[str, Any]:
    adjacency: dict[Label, set[Label]] = defaultdict(set)
    for left, right, output in edges:
        adjacency[left].add(output)
        adjacency[right].add(output)
    visiting: set[Label] = set()
    visited: set[Label] = set()

    def visit(label: Label, path: list[Label]) -> list[Label] | None:
        if label in visiting:
            start = path.index(label)
            return path[start:] + [label]
        if label in visited:
            return None
        visiting.add(label)
        path.append(label)
        for child in sorted(adjacency[label]):
            cycle = visit(child, path)
            if cycle is not None:
                return cycle
        path.pop()
        visiting.remove(label)
        visited.add(label)
        return None

    for label in labels:
        cycle = visit(label, [])
        if cycle is not None:
            return {"valid": False, "cycle": cycle}
    return {"valid": True, "cycle": None}


def coordinate_compatibility(
    curve: Curve,
    labels: Sequence[Label],
    identity: Label,
    edges: Sequence[tuple[Label, Label, Label]],
) -> dict[str, Any]:
    checked = 2 * len(labels) - 1
    for left, right, output in edges:
        checked += 1
        expected = point_label(curve.add(label_point(left), label_point(right)))
        if output != expected:
            return {
                "valid": False,
                "checked_edges": checked,
                "counterexample": {
                    "left": left,
                    "right": right,
                    "stored_output": output,
                    "coordinate_output": expected,
                },
            }
    if identity != "O":
        raise AssertionError("coordinate label O must be the identity")
    return {"valid": True, "checked_edges": checked, "counterexample": None}


def constrained_labels(
    labels: Sequence[Label], identity: Label, edges: Sequence[tuple[Label, Label, Label]]
) -> list[Label]:
    constrained: set[Label] = set()
    if any(label != identity for label in labels):
        constrained.add(identity)
    for left, right, output in edges:
        constrained.add(left)
        constrained.add(right)
        if left != output and right != output:
            constrained.add(output)
    order = {label: index for index, label in enumerate(labels)}
    return sorted(constrained, key=order.__getitem__)


def check_star(
    labels: Sequence[Label],
    identity: Label,
    edges: Sequence[tuple[Label, Label, Label]],
    ops: BuildOps | None = None,
    curve: Curve | None = None,
    sparse_associativity: bool = False,
) -> dict[str, Any]:
    star = star_lookup(labels, identity, edges)
    identity_failures = []
    for label in labels:
        if star(identity, label) != label or star(label, identity) != label:
            identity_failures.append(label)
    nonidentity_to_identity = [list(edge) for edge in edges if edge[2] == identity]

    commutativity_failure = None
    for left in labels:
        for right in labels:
            if star(left, right) != star(right, left):
                commutativity_failure = [left, right]
                break
        if commutativity_failure is not None:
            break

    associativity = associativity_check(
        labels, star, ops, sparse=sparse_associativity, edges=edges
    )
    compatibility = (
        coordinate_compatibility(curve, labels, identity, edges)
        if curve is not None
        else {"valid": True, "checked_edges": len(edges), "counterexample": None}
    )
    factorization = factorization_check(labels, identity, edges)
    acyclic = acyclicity_check(labels, edges)
    return {
        "identity": {
            "valid": not identity_failures and not nonidentity_to_identity,
            "failed_labels": identity_failures,
            "nonidentity_products_to_identity": nonidentity_to_identity,
        },
        "commutativity": {
            "valid": commutativity_failure is None,
            "counterexample": commutativity_failure,
        },
        "associativity": associativity,
        "compatibility_coordinates": compatibility,
        "compatibility_scalars": {"status": "VERIFIER_ONLY"},
        "unique_prime_multiset_factorization": factorization,
        "binary_tree_multiplicity": {
            "immediate_parent_pairs": {
                label: sum(1 for edge in edges if edge[2] == label) for label in labels
            }
        },
        "acyclic": acyclic,
    }


def encoded_edges(edges: Sequence[tuple[Label, Label, Label]]) -> list[list[Label]]:
    return [list(edge) for edge in edges]


def final_boundary(
    edges: Sequence[tuple[Label, Label, Label]], a4_labels: set[Label]
) -> dict[str, Any]:
    forbidden = [list(edge) for edge in edges if edge[0] in a4_labels and edge[1] in a4_labels]
    return {"valid": not forbidden, "forbidden_edges": forbidden}


def formal_family_record(
    family: set[Multiset], evaluations: dict[Multiset, Point], collisions: list[dict[str, Any]]
) -> dict[str, Any]:
    by_degree: dict[str, list[list[int]]] = {}
    for degree in range(0, 5):
        by_degree[str(degree)] = [
            encode_multiset(item)
            for item in sorted(value for value in family if len(value) == degree)
        ]
    return {
        "downward_closure_by_degree": by_degree,
        "evaluation_map": [
            {"multiset": encode_multiset(item), "point": point_label(evaluations[item])}
            for item in sorted(family, key=lambda value: (len(value), value))
        ],
        "evaluation_injective": not collisions,
        "evaluation_collisions": collisions,
    }


def skipped_axioms(reason: str) -> dict[str, Any]:
    names = (
        "identity",
        "commutativity",
        "associativity",
        "compatibility_coordinates",
        "compatibility_scalars",
        "unique_prime_multiset_factorization",
        "binary_tree_multiplicity",
        "acyclic",
    )
    return {name: {"status": "NOT_APPLICABLE", "reason": reason} for name in names}


def ordered_domain_digest(
    labels: Sequence[Label], identity: Label, edges: Sequence[tuple[Label, Label, Label]]
) -> tuple[str, int]:
    star = star_lookup(labels, identity, edges)
    ordered = []
    for left in labels:
        for right in labels:
            output = star(left, right)
            if output is not None:
                ordered.append([left, right, output])
    return stable_digest(ordered), len(ordered)


def role_counts(
    constrained: Sequence[Label], evaluations: dict[Multiset, Point]
) -> dict[str, int]:
    represented = {point_label(point): len(multiset) for multiset, point in evaluations.items()}
    counts: Counter[str] = Counter()
    for label in constrained:
        degree = represented.get(label)
        counts["outside_formal_family" if degree is None else f"degree_{degree}"] += 1
    return dict(sorted(counts.items()))


def make_policy_record(
    name: str,
    curve: Curve,
    all_labels: Sequence[Label],
    factor_points: Sequence[Point],
    family: set[Multiset],
    maxima: Sequence[Multiset],
    raw_a4: Sequence[Point],
    retained_a4: Sequence[Point],
    ops: BuildOps,
    search: dict[str, Any] | None = None,
) -> dict[str, Any]:
    evaluations, collisions = evaluate_family(curve, factor_points, family)
    formal = formal_family_record(family, evaluations, collisions)
    formal["maximal_multisets"] = [encode_multiset(item) for item in sorted(set(maxima))]
    raw_support, raw_histogram, raw_witnesses = support_and_histogram(
        curve, raw_a4
    )
    retained_support, retained_histogram, retained_witnesses = (
        support_and_histogram(curve, retained_a4)
    )
    if collisions:
        return {
            "name": name,
            "embedding_defined": False,
            "formal_family": formal,
            "star": {
                "identity_rule_total": True,
                "unordered_nonidentity_edges": [],
                "ordered_domain_sha256": None,
                "ordered_domain_entries": 0,
                "description_bits": 0,
            },
            "axioms": skipped_axioms("evaluation map is not injective"),
            "constrained": None,
            "retention": retention_record(
                curve,
                raw_support,
                raw_histogram,
                raw_witnesses,
                retained_support,
                retained_histogram,
                retained_witnesses,
                len(all_labels),
            ),
            "search": search,
        }

    edges = closure_edges(all_labels, family, evaluations)
    axioms = check_star(all_labels, "O", edges, ops=ops, curve=curve)
    retained_labels = {point_label(point) for point in retained_a4}
    axioms["direct_final_edge_excluded"] = final_boundary(edges, retained_labels)
    constrained = constrained_labels(all_labels, "O", edges)
    domain_digest, domain_entries = ordered_domain_digest(all_labels, "O", edges)
    edge_count = len(edges)
    constrained_count = len(constrained)
    return {
        "name": name,
        "embedding_defined": True,
        "formal_family": formal,
        "star": {
            "identity_rule_total": True,
            "unordered_nonidentity_edges": encoded_edges(edges),
            "ordered_domain_sha256": domain_digest,
            "ordered_domain_entries": domain_entries,
            "description_bits": 8 * len(stable_json(encoded_edges(edges))),
        },
        "axioms": axioms,
        "constrained": {
            "labels": constrained,
            "count": constrained_count,
            "delta": exact_ratio(constrained_count, len(all_labels)),
            "role_counts": role_counts(constrained, evaluations),
            "edge_density": {
                "nonidentity_unordered_edges": edge_count,
                "edges_per_constrained_label": exact_ratio(edge_count, constrained_count),
                "normalized_against_unordered_label_pairs": exact_ratio(
                    edge_count, (len(all_labels) - 1) * len(all_labels) // 2
                ),
            },
        },
        "retention": retention_record(
            curve,
            raw_support,
            raw_histogram,
            raw_witnesses,
            retained_support,
            retained_histogram,
            retained_witnesses,
            len(all_labels),
        ),
        "search": search,
    }


def retention_record(
    curve: Curve,
    raw_support: set[Point],
    raw_histogram: Counter[Point],
    raw_witnesses: dict[Point, list[list[Label]]],
    retained_support: set[Point],
    retained_histogram: Counter[Point],
    retained_witnesses: dict[Point, list[list[Label]]],
    group_order: int,
) -> dict[str, Any]:
    denominator = len(raw_support)
    return {
        "pair_convention": "unordered_with_replacement",
        "raw_final_support": denominator,
        "retained_final_support": len(retained_support),
        "support_ratio": exact_ratio(len(retained_support), denominator or 1),
        "raw_absolute_group_coverage": exact_ratio(len(raw_support), group_order),
        "retained_absolute_group_coverage": exact_ratio(
            len(retained_support), group_order
        ),
        "raw_target_witness_histogram": {
            str(count): multiplicity
            for count, multiplicity in sorted(Counter(raw_histogram.values()).items())
        },
        "retained_target_witness_histogram": {
            str(count): multiplicity
            for count, multiplicity in sorted(Counter(retained_histogram.values()).items())
        },
        "raw_target_witness_counts": {
            point_label(point): raw_histogram[point]
            for point in sorted(raw_histogram, key=point_key)
        },
        "retained_target_witness_counts": {
            point_label(point): retained_histogram[point]
            for point in sorted(retained_histogram, key=point_key)
        },
        "raw_target_witness_map": {
            point_label(point): raw_witnesses[point]
            for point in sorted(raw_witnesses, key=point_key)
        },
        "retained_target_witness_map": {
            point_label(point): retained_witnesses[point]
            for point in sorted(retained_witnesses, key=point_key)
        },
        "raw_support_labels": [point_label(point) for point in sorted(raw_support, key=point_key)],
        "retained_support_labels": [
            point_label(point) for point in sorted(retained_support, key=point_key)
        ],
    }


def p0_balanced_only(
    curve: Curve,
    all_labels: Sequence[Label],
    factor_points: Sequence[Point],
    raw: dict[str, Any],
    ops: BuildOps,
) -> dict[str, Any]:
    family: set[Multiset] = {(), *((index,) for index in range(len(factor_points)))}
    family.update(item["multiset"] for item in raw["canonical2"])
    family.update(item["multiset"] for item in raw["canonical4"])
    evaluations, collisions = evaluate_family(curve, factor_points, family)
    formal = formal_family_record(family, evaluations, collisions)
    formal["maximal_multisets"] = [
        encode_multiset(item["multiset"]) for item in raw["canonical4"]
    ]

    edges: list[tuple[Label, Label, Label]] = []
    for item in raw["canonical2"]:
        left, right = item["multiset"]
        edges.append(
            (
                point_label(factor_points[left]),
                point_label(factor_points[right]),
                point_label(item["point"]),
            )
        )
    for item in raw["canonical4"]:
        left, right = item["parents"]
        edges.append(
            (
                point_label(evaluate_multiset(curve, factor_points, left)),
                point_label(evaluate_multiset(curve, factor_points, right)),
                point_label(item["point"]),
            )
        )
    edges = normalize_edges(all_labels, edges)
    axioms = check_star(all_labels, "O", edges, ops=ops, curve=curve)
    a4_points = [item["point"] for item in raw["canonical4"]]
    a4_labels = {point_label(point) for point in a4_points}
    axioms["direct_final_edge_excluded"] = final_boundary(edges, a4_labels)
    constrained = constrained_labels(all_labels, "O", edges)
    raw_support, raw_histogram, raw_witnesses = support_and_histogram(
        curve, raw["raw_a4"]
    )
    retained_support, retained_histogram, retained_witnesses = (
        support_and_histogram(curve, a4_points)
    )
    domain_digest, domain_entries = ordered_domain_digest(all_labels, "O", edges)
    return {
        "name": "P0-BALANCED-ONLY",
        "embedding_defined": True,
        "formal_family": formal,
        "star": {
            "identity_rule_total": True,
            "unordered_nonidentity_edges": encoded_edges(edges),
            "ordered_domain_sha256": domain_digest,
            "ordered_domain_entries": domain_entries,
            "description_bits": 8 * len(stable_json(encoded_edges(edges))),
        },
        "axioms": axioms,
        "constrained": {
            "labels": constrained,
            "count": len(constrained),
            "delta": exact_ratio(len(constrained), len(all_labels)),
            "role_counts": role_counts(constrained, evaluations),
            "edge_density": {
                "nonidentity_unordered_edges": len(edges),
                "edges_per_constrained_label": exact_ratio(len(edges), len(constrained)),
                "normalized_against_unordered_label_pairs": exact_ratio(
                    len(edges), (len(all_labels) - 1) * len(all_labels) // 2
                ),
            },
        },
        "retention": retention_record(
            curve,
            raw_support,
            raw_histogram,
            raw_witnesses,
            retained_support,
            retained_histogram,
            retained_witnesses,
            len(all_labels),
        ),
        "search": None,
    }


def optimize_p2(
    curve: Curve,
    labels: Sequence[Label],
    factor_points: Sequence[Point],
    balanced_candidates: Sequence[dict[str, Any]],
    raw_a4: Sequence[Point],
    ops: BuildOps,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    candidates = sorted(
        balanced_candidates, key=lambda item: (item["multiset"], point_key(item["point"]))
    )
    candidate_universe = [
        {
            "index": index,
            "multiset": encode_multiset(candidate["multiset"]),
            "point": point_label(candidate["point"]),
            "parent_pairs": [
                [encode_multiset(parent) for parent in pair]
                for pair in candidate["parent_pairs"]
            ],
        }
        for index, candidate in enumerate(candidates)
    ]
    eligible: list[dict[str, Any]] = []
    eligible_universe_indices: list[int] = []
    rejected: list[dict[str, Any]] = []
    closures: list[set[Multiset]] = []
    for universe_index, candidate in enumerate(candidates):
        family = downward_family(len(factor_points), [candidate["multiset"]])
        _, collisions = evaluate_family(curve, factor_points, family)
        if collisions:
            rejected.append(
                {
                    "universe_index": universe_index,
                    "multiset": encode_multiset(candidate["multiset"]),
                    "point": point_label(candidate["point"]),
                    "first_collision": collisions[0],
                    "collision_replayed": True,
                }
            )
        else:
            eligible.append(candidate)
            eligible_universe_indices.append(universe_index)
            closures.append(family)

    conflict_masks = [0] * len(eligible)
    conflicts: list[dict[str, Any]] = []
    for left in range(len(eligible)):
        for right in range(left + 1, len(eligible)):
            _, collisions = evaluate_family(
                curve, factor_points, closures[left] | closures[right]
            )
            if collisions:
                conflict_masks[left] |= 1 << right
                conflict_masks[right] |= 1 << left
                conflicts.append(
                    {
                        "left_universe_index": eligible_universe_indices[left],
                        "right_universe_index": eligible_universe_indices[right],
                        "left": encode_multiset(eligible[left]["multiset"]),
                        "right": encode_multiset(eligible[right]["multiset"]),
                        "first_collision": collisions[0],
                    }
                )

    raw_support, _, _ = support_and_histogram(curve, raw_a4)
    best_indices: tuple[int, ...] = ()
    empty_family = downward_family(len(factor_points), [])
    empty_evaluations, empty_collisions = evaluate_family(curve, factor_points, empty_family)
    if empty_collisions:
        raise AssertionError("factor-base singletons are not injective")
    empty_edges = closure_edges(labels, empty_family, empty_evaluations)
    empty_constrained = constrained_labels(labels, "O", empty_edges)
    best_key = (0, 0, -len(empty_constrained), -len(empty_edges))
    best_lex: tuple[Multiset, ...] = ()
    outcome_rows: list[dict[str, Any]] = []
    mismatches: list[dict[str, Any]] = []
    feasible_subsets = 0
    optimizer_start_nodes = ops.optimizer_nodes
    for mask in range(1 << len(eligible)):
        ops.optimizer_nodes += 1
        chosen = tuple(index for index in range(len(eligible)) if mask & (1 << index))
        graph_feasible = all(not (conflict_masks[index] & mask) for index in chosen)
        maxima = [eligible[index]["multiset"] for index in chosen]
        family = downward_family(len(factor_points), maxima)
        evaluations, collisions = evaluate_family(curve, factor_points, family)
        direct_feasible = not collisions
        row = {
            "subset_universe_indices": [eligible_universe_indices[index] for index in chosen],
            "graph_feasible": graph_feasible,
            "direct_feasible": direct_feasible,
        }
        outcome_rows.append(row)
        if graph_feasible != direct_feasible:
            mismatch = dict(row)
            mismatch["first_collision"] = collisions[:1]
            mismatches.append(mismatch)
            continue
        if not direct_feasible:
            continue
        feasible_subsets += 1
        edges = closure_edges(labels, family, evaluations)
        constrained = constrained_labels(labels, "O", edges)
        selected_points = [eligible[index]["point"] for index in chosen]
        retained_support, _, _ = support_and_histogram(curve, selected_points)
        key = (
            len(retained_support),
            len(chosen),
            -len(constrained),
            -len(edges),
        )
        lexical = tuple(eligible[index]["multiset"] for index in chosen)
        if key > best_key or (key == best_key and lexical < best_lex):
            best_indices = chosen
            best_key = key
            best_lex = lexical

    if mismatches:
        raise AssertionError(f"conflict-graph/direct-closure mismatch: {mismatches[0]!r}")
    outcome_rows.sort(key=lambda row: row["subset_universe_indices"])
    selected = [eligible[index] for index in best_indices]
    search = {
        "method": "invalid_witness_replay_plus_exhaustive_valid_vertex_subsets",
        "candidate_count": len(candidates),
        "candidate_universe": candidate_universe,
        "candidate_universe_sha256": stable_digest(candidate_universe),
        "eligible_candidate_count": len(eligible),
        "eligible_universe_indices": eligible_universe_indices,
        "individually_rejected": rejected,
        "invalid_witnesses_replayed": len(rejected),
        "supersets_rejected_by_invalid_vertex_monotonicity": (
            (1 << len(candidates)) - (1 << len(eligible))
        ),
        "conflict_count": len(conflicts),
        "conflicts": conflicts,
        "direct_subset_comparisons": 1 << len(eligible),
        "expected_direct_subset_comparisons": 1 << len(eligible),
        "feasible_subset_count": feasible_subsets,
        "graph_direct_mismatch_count": 0,
        "graph_direct_outcomes_order": "lexicographic_subset_universe_indices",
        "graph_direct_outcomes_sha256": stable_digest(outcome_rows),
        "explored_nodes": ops.optimizer_nodes - optimizer_start_nodes,
        "raw_final_support": len(raw_support),
        "optimal_objective": {
            "retained_final_support": best_key[0],
            "retained_degree4_formal_multisets": best_key[1],
            "constrained_count": -best_key[2],
            "unordered_nonidentity_edges": -best_key[3],
            "witness_list": [encode_multiset(item) for item in best_lex],
        },
        "completeness_argument": (
            "invalid-vertex collisions reject every containing superset by monotonicity; "
            "every subset of valid vertices is directly compared with graph independence"
        ),
    }
    return selected, search


def all_multisets(size: int, maximum_degree: int) -> set[Multiset]:
    family: set[Multiset] = {()}
    for degree in range(1, maximum_degree + 1):
        family.update(itertools.combinations_with_replacement(range(size), degree))
    return family


def abstract_edges(
    family: set[Multiset], evaluator: Callable[[Multiset], Label]
) -> tuple[list[Label], Label, list[tuple[Label, Label, Label]]]:
    ordered_family = sorted(family, key=lambda value: (len(value), value))
    labels = [evaluator(value) for value in ordered_family]
    if len(set(labels)) != len(labels):
        raise AssertionError("abstract evaluator is not injective")
    identity = evaluator(())
    nonempty = [value for value in ordered_family if value]
    edges = []
    for left_index, left in enumerate(nonempty):
        for right in nonempty[left_index:]:
            union = tuple(sorted(left + right))
            if union in family:
                edges.append((evaluator(left), evaluator(right), evaluator(union)))
    return labels, identity, normalize_edges(labels, edges)


def source_tag_gate(sources: Sequence[dict[str, Any]]) -> dict[str, Any]:
    seen: dict[tuple[int, int], str] = {}
    for source in sources:
        point_value = source["point"]
        point = (require_exact_int(point_value[0], "source x"), require_exact_int(point_value[1], "source y"))
        tag = str(source["source_tag"])
        previous = seen.get(point)
        if previous is not None:
            return {
                "valid": False,
                "counterexample": {
                    "point": list(point),
                    "first_tag": previous,
                    "second_tag": tag,
                },
            }
        seen[point] = tag
    return {"valid": True, "counterexample": None}


def predicate_vector(
    *,
    source_gate_value: str = "not-applicable",
    evaluation_injective: str = "not-applicable",
    identity: str = "not-applicable",
    commutativity: str = "not-applicable",
    associativity: str = "not-applicable",
    compatibility_coordinates: str = "not-applicable",
    compatibility_scalars: str = "not-applicable",
    unique_factorization: str = "not-applicable",
    acyclic_reduced: str = "not-applicable",
    direct_final_edge_excluded: str = "not-applicable",
    optimizer_exact: str = "not-applicable",
) -> dict[str, str]:
    return {
        "acyclic_reduced": acyclic_reduced,
        "associativity": associativity,
        "commutativity": commutativity,
        "compatibility_coordinates": compatibility_coordinates,
        "compatibility_scalars": compatibility_scalars,
        "direct_final_edge_excluded": direct_final_edge_excluded,
        "evaluation_injective": evaluation_injective,
        "identity": identity,
        "optimizer_exact": optimizer_exact,
        "source_gate": source_gate_value,
        "unique_factorization": unique_factorization,
    }


def truth(value: bool) -> str:
    return "true" if value else "false"


def predicates_from_checks(
    checks: dict[str, Any],
    *,
    evaluation_injective: bool,
    source_gate_value: str = "not-applicable",
    compatibility_coordinates: str = "not-applicable",
    compatibility_scalars: str = "not-applicable",
    direct_final_edge_excluded: bool = True,
) -> dict[str, str]:
    return predicate_vector(
        source_gate_value=source_gate_value,
        evaluation_injective=truth(evaluation_injective),
        identity=truth(checks["identity"]["valid"]),
        commutativity=truth(checks["commutativity"]["valid"]),
        associativity=truth(checks["associativity"]["valid"]),
        compatibility_coordinates=compatibility_coordinates,
        compatibility_scalars=compatibility_scalars,
        unique_factorization=truth(
            checks["unique_prime_multiset_factorization"]["valid"]
        ),
        acyclic_reduced=truth(checks["acyclic"]["valid"]),
        direct_final_edge_excluded=truth(direct_final_edge_excluded),
    )


def builder_expected(expected: dict[str, Any], deferred: Sequence[str]) -> dict[str, Any]:
    result = copy.deepcopy(expected)

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            predicates = value.get("predicates")
            if isinstance(predicates, dict):
                for name in deferred:
                    if name in predicates and predicates[name] != "not-applicable":
                        predicates[name] = "verifier-only"
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(result)
    return result


def registered_control(
    entry: dict[str, Any], observed: dict[str, Any], deferred: Sequence[str] = ()
) -> dict[str, Any]:
    expected = entry["expected"]
    expected_at_builder = builder_expected(expected, deferred)
    return {
        "name": entry["name"],
        "fixture_sha256": stable_digest(entry["fixture"]),
        "expected": expected,
        "observed": observed,
        "deferred_predicates": list(deferred),
        "builder_passed": observed == expected_at_builder,
    }


def run_controls(
    curve: Curve,
    points: Sequence[Point],
    ops: BuildOps,
    registry_document: dict[str, Any],
) -> list[dict[str, Any]]:
    registry = registry_document["registry"]
    entries = {entry["name"]: entry for entry in registry["controls"]}
    labels = [point_label(point) for point in points]
    controls: list[dict[str, Any]] = []

    free_family = all_multisets(3, 4)
    free_labels, free_identity, free_edges = abstract_edges(
        free_family, lambda value: "e" if not value else "m:" + ",".join(map(str, value))
    )
    free_checks = check_star(free_labels, free_identity, free_edges, ops=ops)
    free_observed = {
        "counterexample": None,
        "counts": {
            "constrained_labels": len(constrained_labels(free_labels, free_identity, free_edges)),
            "labels": len(free_labels),
            "unordered_nonidentity_edges": len(free_edges),
        },
        "predicates": predicates_from_checks(
            free_checks, evaluation_injective=True
        ),
    }
    controls.append(registered_control(entries["PC-FREE-MONOID"], free_observed))

    cyclic_q = 509
    cyclic_weights = (1, 5, 25, 125)
    cyclic_family = all_multisets(4, 4)

    def cyclic_evaluator(multiset: Multiset) -> Label:
        return str(sum(cyclic_weights[index] for index in multiset) % cyclic_q)

    represented, cyclic_identity, cyclic_edges = abstract_edges(
        cyclic_family, cyclic_evaluator
    )
    cyclic_labels = [str(value) for value in range(cyclic_q)]
    if not set(represented).issubset(cyclic_labels):
        raise AssertionError("cyclic control produced an invalid label")
    cyclic_edges = normalize_edges(cyclic_labels, cyclic_edges)
    cyclic_checks = check_star(
        cyclic_labels,
        cyclic_identity,
        cyclic_edges,
        ops=ops,
        sparse_associativity=True,
    )
    cyclic_scalar_compatible = all(
        int(output) == (int(left) + int(right)) % cyclic_q
        for left, right, output in cyclic_edges
    )
    cyclic_observed = {
        "counterexample": None,
        "counts": {
            "constrained_labels": len(
                constrained_labels(cyclic_labels, cyclic_identity, cyclic_edges)
            ),
            "labels": len(cyclic_labels),
            "maximum_unreduced_sum": 4 * max(cyclic_weights),
            "represented_labels": len(represented),
            "unordered_nonidentity_edges": len(cyclic_edges),
        },
        "delta": exact_ratio(
            len(constrained_labels(cyclic_labels, cyclic_identity, cyclic_edges)),
            cyclic_q,
        ),
        "predicates": predicates_from_checks(
            cyclic_checks,
            evaluation_injective=True,
            compatibility_scalars=truth(cyclic_scalar_compatible),
        ),
    }
    controls.append(
        registered_control(entries["PC-CYCLIC-NO-WRAP"], cyclic_observed)
    )

    factor_base8 = make_factor_base(points, 8)
    forest_maximum = (1, 6, 6, 6)
    forest_family = downward_family(8, [forest_maximum])
    forest_evaluations, forest_collisions = evaluate_family(
        curve, factor_base8["points"], forest_family
    )
    forest_edges = closure_edges(labels, forest_family, forest_evaluations)
    forest_checks = check_star(labels, "O", forest_edges, ops=ops, curve=curve)
    forest_constrained = constrained_labels(labels, "O", forest_edges)
    forest_boundary = final_boundary(
        forest_edges, {point_label(forest_evaluations[forest_maximum])}
    )
    forest_observed = {
        "counterexample": None,
        "counts": {
            "constrained_labels": len(forest_constrained),
            "formal_family_by_degree": {
                str(degree): sum(len(item) == degree for item in forest_family)
                for degree in range(5)
            },
            "formal_family_total": len(forest_family),
            "unordered_nonidentity_edges": len(forest_edges),
        },
        "predicates": predicates_from_checks(
            forest_checks,
            evaluation_injective=not forest_collisions,
            source_gate_value="true",
            compatibility_coordinates=truth(
                forest_checks["compatibility_coordinates"]["valid"]
            ),
            compatibility_scalars="verifier-only",
            direct_final_edge_excluded=forest_boundary["valid"],
        ),
        "selected_output": list(forest_evaluations[forest_maximum]),
    }
    controls.append(
        registered_control(
            entries["PC-EC-FOREST"],
            forest_observed,
            deferred=("compatibility_scalars",),
        )
    )

    repeated_family = all_multisets(1, 4)
    repeated_labels, repeated_identity, repeated_edges = abstract_edges(
        repeated_family, lambda value: f"d{len(value)}"
    )
    repeated_checks = check_star(
        repeated_labels, repeated_identity, repeated_edges, ops=ops
    )
    repeated_observed = {
        "counterexample": None,
        "counts": {
            "constrained_labels": len(
                constrained_labels(repeated_labels, repeated_identity, repeated_edges)
            ),
            "immediate_parent_pairs_by_degree": [
                sum(edge[2] == f"d{degree}" for edge in repeated_edges)
                for degree in range(5)
            ],
            "labels": len(repeated_labels),
            "unordered_nonidentity_edges": len(repeated_edges),
        },
        "predicates": predicates_from_checks(
            repeated_checks, evaluation_injective=True
        ),
    }
    controls.append(
        registered_control(entries["PC-REPEATED-PRIME"], repeated_observed)
    )

    balanced_entry = entries["NC-BALANCED-ONLY"]
    balanced_labels = balanced_entry["fixture"]["labels"]
    balanced_identity = balanced_entry["fixture"]["identity"]
    balanced_edges = [tuple(edge) for edge in balanced_entry["fixture"]["edges"]]
    balanced_edges = normalize_edges(balanced_labels, balanced_edges)
    balanced_checks = check_star(
        balanced_labels, balanced_identity, balanced_edges, ops=ops
    )
    balanced_observed = {
        "counterexample": balanced_checks["associativity"]["counterexample"],
        "counts": {
            "constrained_labels": len(
                constrained_labels(balanced_labels, balanced_identity, balanced_edges)
            ),
            "labels": len(balanced_labels),
            "unordered_nonidentity_edges": len(balanced_edges),
        },
        "predicates": predicates_from_checks(
            balanced_checks, evaluation_injective=True
        ),
    }
    controls.append(registered_control(balanced_entry, balanced_observed))

    factor_base4 = make_factor_base(points, 4)
    all_family = all_multisets(4, 4)
    _, all_collisions = evaluate_family(curve, factor_base4["points"], all_family)
    all_observed = {
        "counterexample": all_collisions[0],
        "counts": {
            "collision_pairs": len(all_collisions),
            "formal_family_total": len(all_family),
        },
        "predicates": predicate_vector(
            source_gate_value="true", evaluation_injective="false"
        ),
    }
    controls.append(
        registered_control(entries["NC-ALL-WITNESSES"], all_observed)
    )

    duplicate_sources = list(factor_base4["canonical_sources"])
    duplicate = dict(duplicate_sources[0])
    duplicate["source_tag"] += "|duplicate"
    duplicate_sources.append(duplicate)
    duplicate_result = source_tag_gate(duplicate_sources)
    duplicate_observed = {
        "counterexample": duplicate_result["counterexample"],
        "predicates": predicate_vector(source_gate_value=truth(duplicate_result["valid"])),
    }
    controls.append(
        registered_control(entries["NC-DUPLICATE-TAG"], duplicate_observed)
    )

    mutated_label = point_label(forest_evaluations[forest_maximum])
    mutated_decode = {label: label_point(label) for label in labels}
    mutated_decode[mutated_label] = (6, 16)
    mutation_compatible = all(
        mutated_decode[output]
        == curve.add(mutated_decode[left], mutated_decode[right])
        for left, right, output in forest_edges
    )
    mutation_observed = {
        "counterexample": {
            "formal_label": list(forest_maximum),
            "mutated_decode": [6, 16],
            "true_decode": list(forest_evaluations[forest_maximum]),
        },
        "predicates": predicates_from_checks(
            forest_checks,
            evaluation_injective=True,
            source_gate_value="true",
            compatibility_coordinates=truth(mutation_compatible),
            compatibility_scalars="verifier-only",
            direct_final_edge_excluded=forest_boundary["valid"],
        ),
    }
    controls.append(
        registered_control(
            entries["NC-COMPAT-MUTATION"],
            mutation_observed,
            deferred=("compatibility_scalars",),
        )
    )

    degree8_family = all_multisets(1, 8)
    degree8_labels, degree8_identity, degree8_edges = abstract_edges(
        degree8_family, lambda value: f"d{len(value)}"
    )
    degree8_checks = check_star(
        degree8_labels, degree8_identity, degree8_edges, ops=ops
    )
    degree8_boundary = final_boundary(degree8_edges, {"d4"})
    degree8_observed = {
        "counterexample": {"edge_degrees": [4, 4, 8]},
        "counts": {
            "constrained_labels": len(
                constrained_labels(degree8_labels, degree8_identity, degree8_edges)
            ),
            "labels": len(degree8_labels),
            "unordered_nonidentity_edges": len(degree8_edges),
        },
        "delta": exact_ratio(
            len(constrained_labels(degree8_labels, degree8_identity, degree8_edges)),
            len(degree8_labels),
        ),
        "predicates": predicates_from_checks(
            degree8_checks,
            evaluation_injective=True,
            direct_final_edge_excluded=degree8_boundary["valid"],
        ),
    }
    controls.append(registered_control(entries["NC-FINAL-EDGE"], degree8_observed))

    factor_base6 = make_factor_base(points, 6)
    b6_family = downward_family(6, [(0, 3)])
    _, b6_collisions = evaluate_family(curve, factor_base6["points"], b6_family)
    b6_observed = {
        "counterexample": b6_collisions[0],
        "predicates": predicate_vector(
            source_gate_value="true", evaluation_injective="false"
        ),
    }
    controls.append(
        registered_control(entries["NC-B6-D2-COLLISION"], b6_observed)
    )

    canonical = (0, 0, 0, 4)
    alternate = (1, 6, 6, 6)
    b8_universe = {
        item["multiset"]
        for item in build_raw_witnesses(curve, factor_base8["points"])[
            "balanced_candidates"
        ]
    }
    if canonical not in b8_universe or alternate not in b8_universe:
        raise AssertionError("B8 canonical-loss witnesses are not both in U4_BAL")
    canonical_family = downward_family(8, [canonical])
    canonical_evaluations, canonical_collisions = evaluate_family(
        curve, factor_base8["points"], canonical_family
    )
    alternate_family = downward_family(8, [alternate])
    alternate_evaluations, alternate_collisions = evaluate_family(
        curve, factor_base8["points"], alternate_family
    )
    alternate_edges = closure_edges(labels, alternate_family, alternate_evaluations)
    alternate_checks = check_star(labels, "O", alternate_edges, ops=ops, curve=curve)
    alternate_boundary = final_boundary(
        alternate_edges, {point_label(alternate_evaluations[alternate])}
    )
    b8_observed = {
        "cases": [
            {
                "counterexample": canonical_collisions[0],
                "formal_multiset": list(canonical),
                "predicates": predicate_vector(
                    source_gate_value="true", evaluation_injective="false"
                ),
            },
            {
                "counts": {
                    "constrained_labels": len(
                        constrained_labels(labels, "O", alternate_edges)
                    ),
                    "formal_family_total": len(alternate_family),
                    "unordered_nonidentity_edges": len(alternate_edges),
                },
                "counterexample": None,
                "formal_multiset": list(alternate),
                "predicates": predicates_from_checks(
                    alternate_checks,
                    evaluation_injective=not alternate_collisions,
                    source_gate_value="true",
                    compatibility_coordinates=truth(
                        alternate_checks["compatibility_coordinates"]["valid"]
                    ),
                    compatibility_scalars="verifier-only",
                    direct_final_edge_excluded=alternate_boundary["valid"],
                ),
            },
        ],
        "common_output": list(canonical_evaluations[canonical]),
    }
    if canonical_evaluations[canonical] != alternate_evaluations[alternate]:
        raise AssertionError("B8 canonical-loss control outputs differ")
    controls.append(
        registered_control(
            entries["NC-B8-CANONICAL-LOSS"],
            b8_observed,
            deferred=("compatibility_scalars",),
        )
    )

    optimizer_entry = entries["NC-OPTIMIZER-FIXTURE"]
    fixture = optimizer_entry["fixture"]
    conflicts = {tuple(edge) for edge in fixture["conflict_edges"]}
    rows = []
    best_subset: tuple[int, ...] | None = None
    best_key: tuple[int, int, int, int] | None = None
    for mask in range(1 << len(fixture["vertices"])):
        subset = tuple(index for index in fixture["vertices"] if mask & (1 << index))
        if any(left in subset and right in subset for left, right in conflicts):
            continue
        outputs = [fixture["outputs"][index] for index in subset]
        support = {
            (outputs[left] + outputs[right]) % 17
            for left in range(len(outputs))
            for right in range(left, len(outputs))
        }
        constrained_count = 1 if not subset else 4 * len(subset) + 1
        edge_count = 4 * len(subset)
        objective = [len(support), len(subset), constrained_count, edge_count]
        rows.append({"objective": objective, "subset": list(subset)})
        key = (objective[0], objective[1], -objective[2], -objective[3])
        if best_key is None or key > best_key or (
            key == best_key and (best_subset is None or subset < best_subset)
        ):
            best_key = key
            best_subset = subset
    rows.sort(key=lambda row: (len(row["subset"]), row["subset"]))
    optimizer_observed = {
        "counterexample": None,
        "feasible_subset_objectives": rows,
        "predicates": predicate_vector(optimizer_exact="true"),
        "winner": list(best_subset or ()),
    }
    controls.append(
        registered_control(entries["NC-OPTIMIZER-FIXTURE"], optimizer_observed)
    )

    if [control["name"] for control in controls] != [
        entry["name"] for entry in registry["controls"]
    ]:
        raise AssertionError("control output order differs from registry")
    return controls


def serialize_raw(raw: dict[str, Any]) -> dict[str, Any]:
    degree2_histogram = Counter(len(values) for values in raw["degree2_by_point"].values())
    degree4_histogram = Counter(len(values) for values in raw["degree4_by_point"].values())
    canonical2 = [
        {
            "point": point_label(item["point"]),
            "multiset": encode_multiset(item["multiset"]),
            "alternate_multisets": [encode_multiset(value) for value in item["alternatives"]],
        }
        for item in raw["canonical2"]
    ]
    canonical4 = []
    for item in raw["canonical4"]:
        canonical4.append(
            {
                "point": point_label(item["point"]),
                "multiset": encode_multiset(item["multiset"]),
                "parents": [encode_multiset(parent) for parent in item["parents"]],
                "alternate_witnesses": [
                    {
                        "multiset": encode_multiset(value["multiset"]),
                        "parents": [encode_multiset(parent) for parent in value["parents"]],
                    }
                    for value in item["alternatives"]
                ],
            }
        )
    balanced_universe = [
        {
            "index": index,
            "multiset": encode_multiset(item["multiset"]),
            "point": point_label(item["point"]),
            "parent_pairs": [
                [encode_multiset(parent) for parent in pair]
                for pair in item["parent_pairs"]
            ],
        }
        for index, item in enumerate(raw["balanced_candidates"])
    ]
    return {
        "degree2_count": len(raw["degree2"]),
        "degree4_count": len(raw["raw4"]),
        "canonical_degree2_count": len(raw["canonical2"]),
        "canonical_degree4_count": len(raw["canonical4"]),
        "balanced_degree4_candidate_count": len(raw["balanced_candidates"]),
        "multiplicity_histograms": {
            "degree2": {str(key): value for key, value in sorted(degree2_histogram.items())},
            "degree4": {str(key): value for key, value in sorted(degree4_histogram.items())},
        },
        "support_sizes": {
            "degree2_including_identity": len(raw["degree2_by_point"]),
            "degree2_nonidentity": len(raw["canonical2"]),
            "degree4_including_identity": len(raw["raw_a4"]),
            "degree4_nonidentity": sum(point is not None for point in raw["raw_a4"]),
        },
        "degree2_identity_witnesses": [
            encode_multiset(value)
            for value in sorted(raw["degree2_by_point"].get(None, []))
        ],
        "canonical_degree2": canonical2,
        "canonical_degree4": canonical4,
        "balanced_candidate_universe": balanced_universe,
        "balanced_candidate_universe_sha256": stable_digest(balanced_universe),
        "p1_alternate_degree2_discarded": sum(
            len(item["alternatives"]) for item in raw["canonical2"]
        ),
        "p1_alternate_degree4_witness_count": sum(
            len(item["alternatives"]) for item in raw["canonical4"]
        ),
        "balanced_parent_pair_count": len(raw["raw4"]),
        "balanced_parent_pair_multiplicity_histogram": {
            str(key): value
            for key, value in sorted(
                Counter(
                    len(item["parent_pairs"]) for item in raw["balanced_candidates"]
                ).items()
            )
        },
    }


def minimized_policy_failures(policies: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    for policy in policies:
        collisions = policy["formal_family"]["evaluation_collisions"]
        if collisions:
            failures.append(
                {
                    "policy": policy["name"],
                    "predicate": "evaluation_injective",
                    "counterexample": collisions[0],
                }
            )
        for name, record in policy["axioms"].items():
            if not isinstance(record, dict) or record.get("valid") is not False:
                continue
            witness = record.get("counterexample")
            if witness is None:
                for key in ("failures", "cycle", "forbidden_edges"):
                    values = record.get(key)
                    if values:
                        witness = values[0] if isinstance(values, list) else values
                        break
            failures.append(
                {
                    "policy": policy["name"],
                    "predicate": name,
                    "counterexample": witness,
                }
            )
    return failures


def build_row(
    curve: Curve,
    points: Sequence[Point],
    factor_base_size: int,
    ops: BuildOps,
    controls: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    operation_start = asdict(ops)
    labels = [point_label(point) for point in points]
    factor_base = make_factor_base(points, factor_base_size)
    source_gate = source_tag_gate(factor_base["canonical_sources"])
    if not source_gate["valid"]:
        raise AssertionError("canonical factor-base sources failed uniqueness")
    raw = build_raw_witnesses(curve, factor_base["points"])

    p0 = p0_balanced_only(curve, labels, factor_base["points"], raw, ops)
    p1_maxima = [
        *(item["multiset"] for item in raw["canonical2"]),
        *(item["multiset"] for item in raw["canonical4"]),
    ]
    p1_family = downward_family(factor_base_size, p1_maxima)
    p1 = make_policy_record(
        "P1-CANONICAL-CLOSURE",
        curve,
        labels,
        factor_base["points"],
        p1_family,
        p1_maxima,
        raw["raw_a4"],
        [item["point"] for item in raw["canonical4"]],
        ops,
    )

    selected, search = optimize_p2(
        curve,
        labels,
        factor_base["points"],
        raw["balanced_candidates"],
        raw["raw_a4"],
        ops,
    )
    p2_maxima = [item["multiset"] for item in selected]
    p2_family = downward_family(factor_base_size, p2_maxima)
    p2 = make_policy_record(
        "P2-BALANCED-UNIVERSE-OPTIMUM",
        curve,
        labels,
        factor_base["points"],
        p2_family,
        p2_maxima,
        raw["raw_a4"],
        [item["point"] for item in selected],
        ops,
        search=search,
    )
    serialized_factor_base = {
        "B": factor_base["B"],
        "L_roots": factor_base["L_roots"],
        "L_polynomial_coefficients_ascending_mod_p": factor_base[
            "L_polynomial_coefficients_ascending_mod_p"
        ],
        "labels": factor_base["labels"],
        "canonical_sources": factor_base["canonical_sources"],
        "discarded_source_tags": factor_base["discarded_source_tags"],
        "source_gate": source_gate,
    }
    unexpected_control_failures = [
        control["name"] for control in controls if not control["builder_passed"]
    ]
    public_model = {
        "labeling": {
            "label_order": labels,
            "identity_label": "O",
            "injective": len(labels) == len(set(labels)),
            "scalar_material_attestation": {
                "forbidden_named_fields_absent_by_construction": True,
                "covert_encoding_excluded": False,
            },
        },
        "selected_formal_family": p2["formal_family"],
        "star": p2["star"],
        "axioms": p2["axioms"],
        "constrained": p2["constrained"],
    }
    raw_witnesses = serialize_raw(raw)
    counterexamples = minimized_policy_failures([p0, p1, p2])
    charged_operations = operation_delta(operation_start, asdict(ops))
    private_audit = {
        "raw_witnesses": raw_witnesses,
        "baseline_policies": [p0, p1],
        "optimizer_proof": p2["search"],
        "retention": p2["retention"],
        "minimized_policy_counterexamples": counterexamples,
        "charged_operations": charged_operations,
    }
    set_fixed_point_json_size(private_audit, "charged_canonical_json_bytes")
    return {
        "factor_base": serialized_factor_base,
        "raw_witnesses": copy.deepcopy(raw_witnesses),
        "public_model": public_model,
        "private_audit": private_audit,
        "accounting": {
            "public_model_canonical_json_bytes": len(stable_json(public_model)),
            "source_witness_canonical_json_bytes": len(
                stable_json(serialized_factor_base["canonical_sources"])
            ),
            "distinct_balanced_candidates_per_constrained_label": exact_ratio(
                raw_witnesses["balanced_degree4_candidate_count"],
                p2["constrained"]["count"],
            ),
            "raw_balanced_parent_pairs_per_constrained_label": exact_ratio(
                raw_witnesses["balanced_parent_pair_count"],
                p2["constrained"]["count"],
            ),
            "source_tag_multiplicity_histogram": {
                "1": len(serialized_factor_base["canonical_sources"])
            },
            "discarded_source_tag_count": len(
                serialized_factor_base["discarded_source_tags"]
            ),
            "minimized_counterexample_sha256": stable_digest(counterexamples),
        },
        "controls": copy.deepcopy(list(controls)),
        "control_summary": {
            "all_registered_behaviors_observed": not unexpected_control_failures,
            "unexpected_failures": unexpected_control_failures,
        },
        "claim_boundary": (
            "five-bit implementation preflight only; no ECDLP, exponent, relation, "
            "rank, descent, or conventional-coordinate lower-bound claim"
        ),
    }


def git_commit(repo_root: Path) -> str:
    process = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return process.stdout.strip()


def deterministic_payload(document: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in document.items()
        if key not in {"implementation", "resource_metrics", "artifact_digests"}
    }


def build_document(
    contract_path: Path,
    literature_path: Path,
    factor_base_sizes: Sequence[int],
    command_argv: Sequence[str] | None = None,
    timestamp_utc: str | None = None,
    execution_mode: str = "development_direct",
) -> dict[str, Any]:
    started = time.perf_counter_ns()
    contract_path = require_bound_file(
        contract_path,
        MATHEMATICAL_CONTRACT_PATH,
        MATHEMATICAL_CONTRACT_SHA256,
        "mathematical contract",
    )
    experiment_contract_path = require_bound_file(
        EXPERIMENT_CONTRACT_PATH,
        EXPERIMENT_CONTRACT_PATH,
        EXPERIMENT_CONTRACT_SHA256,
        "experiment contract",
    )
    literature_path = require_bound_file(
        literature_path, LITERATURE_PATH, LITERATURE_SHA256, "literature note"
    )
    literature_hash = sha256_file(literature_path)
    if not VERIFIER_PATH.is_file():
        raise FileNotFoundError(f"independent verifier is missing: {VERIFIER_PATH}")

    ops = BuildOps()
    curve = Curve(FIXTURE["p"], FIXTURE["a"], FIXTURE["b"], ops)
    points = enumerate_points(curve)
    if len(points) != FIXTURE["q"]:
        raise AssertionError(f"fixture recount produced {len(points)} points, expected {FIXTURE['q']}")
    if not is_prime(len(points)):
        raise AssertionError("fixture group order is not prime")
    trace = curve.p + 1 - len(points)
    if trace != FIXTURE["trace"] or trace in (0, 1):
        raise AssertionError("fixture trace violates the preregistered curve gate")
    j_value = j_invariant(curve)
    if j_value in (0, 1728 % curve.p):
        raise AssertionError("fixture has a forbidden special j-invariant")
    generator = tuple(FIXTURE["generator"])
    if not curve.on_curve(generator):
        raise AssertionError("fixture generator is not on the curve")
    if points[1] != generator:
        raise AssertionError("fixture generator is not the lexicographically first affine point")
    labels = [point_label(point) for point in points]
    registry_document = load_control_registry()
    controls = run_controls(curve, points, ops, registry_document)
    rows = [
        build_row(curve, points, size, ops, controls) for size in factor_base_sizes
    ]
    if asdict(ops) != EXPECTED_BUILDER_OPERATIONS:
        raise AssertionError(
            "deterministic builder operation recount changed: "
            f"expected {EXPECTED_BUILDER_OPERATIONS}, observed {asdict(ops)}"
        )
    repo_root = REPO_ROOT
    if execution_mode == "locked_runner_stdout_json":
        context = {
            "cwd": str(Path.cwd().resolve()),
            "branch": None,
            "git_commit": None,
            "git_status_porcelain_v1": None,
        }
        provenance = "EXTERNAL_LOCKED_RUNNER_RECEIPT_ONLY"
    elif execution_mode == "development_direct":
        context = launch_context()
        provenance = "BUILDER_SELF_REPORTED_DEVELOPMENT_CONTEXT"
    else:
        raise ValueError(f"unsupported execution mode: {execution_mode}")
    document: dict[str, Any] = {
        "schema": SCHEMA,
        "experiment_id": EXPERIMENT_ID,
        "claim_status": "HYPOTHESIS",
        "bindings": {
            "contract_path": str(contract_path.relative_to(repo_root)),
            "contract_sha256": sha256_file(contract_path),
            "experiment_contract_path": str(
                experiment_contract_path.relative_to(repo_root)
            ),
            "experiment_contract_sha256": sha256_file(experiment_contract_path),
            "literature_path": str(literature_path.relative_to(repo_root)),
            "literature_sha256": literature_hash,
            "sggm_pdf_sha256": SGGM_PDF_SHA256,
            "control_registry_path": str(CONTROL_REGISTRY_PATH.relative_to(repo_root)),
            "control_registry_sha256": CONTROL_REGISTRY_SHA256,
        },
        "implementation": {
            "execution_mode": execution_mode,
            "provenance": provenance,
            "git_commit": context["git_commit"],
            "git_branch": context["branch"],
            "launch_cwd": context["cwd"],
            "tree_clean_before_launch": (
                None
                if context["git_status_porcelain_v1"] is None
                else context["git_status_porcelain_v1"] == ""
            ),
            "tree_status_porcelain_v1_before_launch": context[
                "git_status_porcelain_v1"
            ],
            "runtime_isolation": {
                "isolated": bool(sys.flags.isolated),
                "no_site": bool(sys.flags.no_site),
                "dont_write_bytecode": bool(sys.flags.dont_write_bytecode),
            },
            "builder_sha256": sha256_file(SCRIPT_PATH),
            "verifier_sha256": sha256_file(VERIFIER_PATH),
            "command_argv": list(command_argv or []),
            "timestamp_utc": timestamp_utc
            or datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        },
        "curve": {
            "bits": FIXTURE["bits"],
            "p": curve.p,
            "a": curve.a,
            "b": curve.b,
            "q": len(points),
            "trace": trace,
            "j_invariant": j_value,
            "generator": list(generator),
            "point_table_labels": labels,
            "point_table_sha256": stable_digest(labels),
            "group_order_proof": {
                "method": "exhaustive_affine_coordinate_enumeration",
                "affine_points": len(points) - 1,
                "identity_points": 1,
                "order_is_prime": True,
                "cofactor": 1,
            },
        },
        "rows": rows,
        "preflight_boundary": {
            "contract_version": "3a",
            "toy_bits": [5],
            "factor_base_sizes": list(factor_base_sizes),
            "larger_rows_executed": False,
            "canonical_run_authorized": False,
        },
    }
    elapsed = time.perf_counter_ns() - started
    document["resource_metrics"] = {
        "builder_operations": asdict(ops),
        "memory_measurement": {
            "kind": "deep_size_of_final_document_object_graph_before_resource_record",
            "bytes": deep_size(document),
            "is_peak_process_memory": False,
        },
        "wall_clock_ns": elapsed,
        "diagnostic_only": True,
        "attestation": "BUILDER_SELF_REPORTED_NOT_INDEPENDENTLY_VERIFIED",
    }
    document["artifact_digests"] = {
        "public_model_sha256": stable_digest([row["public_model"] for row in rows]),
        "private_audit_sha256": stable_digest([row["private_audit"] for row in rows]),
        "controls_sha256": stable_digest(controls),
        "deterministic_payload_sha256": stable_digest(deterministic_payload(document)),
        "execution_receipt_sha256": stable_digest(
            {
                "implementation": document["implementation"],
                "resource_metrics": document["resource_metrics"],
            }
        ),
        "builder_sha256": document["implementation"]["builder_sha256"],
        "verifier_sha256": document["implementation"]["verifier_sha256"],
    }
    return document


def ensure_output_path(output: Path, repo_root: Path) -> Path:
    resolved = output.resolve()
    if resolved != CERTIFICATE_PATH.resolve():
        raise ValueError(f"output must be exactly {CERTIFICATE_PATH}")
    if not resolved.is_relative_to(repo_root.resolve()) or resolved.is_relative_to(
        FROZEN_REVIEW_ROOT.resolve()
    ):
        raise ValueError("output resolves outside the SGCP evidence directory")
    if resolved.exists():
        raise FileExistsError(f"refusing to overwrite existing output: {resolved}")
    return resolved


def write_json_atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    if temporary.exists():
        raise FileExistsError(f"temporary output already exists: {temporary}")
    payload = (
        json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False)
        + "\n"
    ).encode("ascii")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--literature", type=Path, required=True)
    parser.add_argument("--toy-bits", nargs="+", type=int, required=True)
    parser.add_argument("--factor-base-sizes", nargs="+", type=int, required=True)
    destination = parser.add_mutually_exclusive_group(required=True)
    destination.add_argument("--output", type=Path)
    destination.add_argument("--runner-json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    invocation_arguments = list(sys.argv[1:] if argv is None else argv)
    invocation_script = sys.argv[0] if argv is None else str(SCRIPT_PATH)
    if args.toy_bits != [5]:
        raise ValueError("this implementation preflight permits only --toy-bits 5")
    if args.factor_base_sizes != [4, 6, 8]:
        raise ValueError("the preregistered preflight requires factor-base sizes 4 6 8")
    repo_root = REPO_ROOT
    execution_mode = (
        "locked_runner_stdout_json" if args.runner_json else "development_direct"
    )
    if args.runner_json:
        require_locked_runner_runtime()
        command_argv = [
            sys.executable,
            "-I",
            "-S",
            "-B",
            invocation_script,
            *invocation_arguments,
        ]
        output = None
    else:
        assert args.output is not None
        output = require_canonical_launch_context(args.output)
        command_argv = [sys.executable, invocation_script, *invocation_arguments]
    document = build_document(
        args.contract,
        args.literature,
        args.factor_base_sizes,
        command_argv=command_argv,
        execution_mode=execution_mode,
    )
    if args.runner_json:
        print(
            json.dumps(
                {
                    "valid": True,
                    "artifact_kind": "sgcp-embed-001-builder-certificate",
                    "certificate": document,
                    "summary": {
                        "curve_bits": 5,
                        "factor_base_rows": len(document["rows"]),
                        "builder_operation_count": sum(
                            document["resource_metrics"]["builder_operations"].values()
                        ),
                    },
                    "claim_boundary": document["rows"][0]["claim_boundary"],
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
                allow_nan=False,
            )
        )
    else:
        assert output is not None
        output = ensure_output_path(output, repo_root)
        write_json_atomic(output, document)
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
