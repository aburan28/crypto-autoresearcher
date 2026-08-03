#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
from typing import Any, NamedTuple


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[3]
ORBIT_SOURCE = SCRIPT_PATH.with_name("streaming_orbit_quotient_locator.py")


def load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ORBIT = load("streaming_projective_orbit_base", ORBIT_SOURCE)
ProjectivePoint = tuple[int, int, int] | None


class ProjectivePair(NamedTuple):
    plus: ProjectivePoint
    minus: ProjectivePoint
    z2: int
    z3: int


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def affine_projective(point: tuple[int, int] | None) -> ProjectivePoint:
    if point is None:
        return None
    return point[0], point[1], 1


def paired_projective_add(
    curve: Any,
    left: tuple[int, int] | None,
    right: tuple[int, int] | None,
    ops: dict[str, int],
) -> ProjectivePair:
    """Compute P+S and P-S in shared-Z Jacobian coordinates.

    For affine inputs the generic branch shares H, 4H^2, J, V, and Z across
    the two sign branches. No field inversion is used until a caller chooses
    to materialize an affine witness.
    """
    ops["paired_source_calls"] = ops.get("paired_source_calls", 0) + 1
    if left is None:
        ops["paired_identity_calls"] = ops.get("paired_identity_calls", 0) + 1
        plus = affine_projective(right)
        minus = affine_projective(ORBIT.neg_point(right, curve.p, ops))
        return ProjectivePair(plus, minus, 1, 1)
    if right is None:
        ops["paired_identity_calls"] = ops.get("paired_identity_calls", 0) + 1
        point = affine_projective(left)
        return ProjectivePair(point, point, 1, 1)

    p = curve.p
    x1, y1 = left
    x2, y2 = right
    if x1 == x2:
        ops["paired_fallback_calls"] = ops.get("paired_fallback_calls", 0) + 1
        plus = curve.add(left, right, ops)
        minus = curve.add(left, ORBIT.neg_point(right, p, ops), ops)
        return ProjectivePair(affine_projective(plus), affine_projective(minus), 1, 1)

    # Jacobian addition for affine P=(x1,y1,1) and Q=(x2,y2,1),
    # specialized so H, J, V, and Z are shared by Q and -Q.
    h = (x2 - x1) % p
    h2 = h * h % p
    four_h2 = (4 * h2) % p
    j = h * four_h2 % p
    v = x1 * four_h2 % p
    z = (2 * h) % p
    r_plus = (2 * (y2 - y1)) % p
    r_minus = (2 * (-y2 - y1)) % p
    x_plus = (r_plus * r_plus - j - 2 * v) % p
    x_minus = (r_minus * r_minus - j - 2 * v) % p
    common_y = (2 * y1 * j) % p
    y_plus = (r_plus * (v - x_plus) - common_y) % p
    y_minus = (r_minus * (v - x_minus) - common_y) % p
    z2 = z * z % p
    z3 = z2 * z % p

    ops["point_add_calls"] = ops.get("point_add_calls", 0) + 2
    ops["field_multiplications"] = ops.get("field_multiplications", 0) + 10
    ops["field_subtractions"] = ops.get("field_subtractions", 0) + 10
    ops["paired_projective_calls"] = ops.get("paired_projective_calls", 0) + 1
    ops["projective_shared_z_powers"] = ops.get("projective_shared_z_powers", 0) + 2
    return ProjectivePair((x_plus, y_plus, z), (x_minus, y_minus, z), z2, z3)


def projective_predicate(
    point: ProjectivePoint,
    z2: int,
    z3: int,
    target: tuple[int, int],
    p: int,
    nu: int,
    ops: dict[str, int],
) -> int:
    """Evaluate the affine norm predicate after clearing Z^6."""
    if point is None:
        return 1
    x, y, z = point
    if z == 0:
        return 1
    tx, ty = target
    dx = (x - tx * z2) % p
    dy = (y - ty * z3) % p
    x_term = z2 * dx * dx % p
    y_term = nu * dy * dy % p
    ops["projective_predicate_field_multiplications"] = ops.get("projective_predicate_field_multiplications", 0) + 6
    ops["projective_predicate_field_subtractions"] = ops.get("projective_predicate_field_subtractions", 0) + 2
    return (x_term - y_term) % p


class ProjectivePredicates(ORBIT.OrbitPredicates):
    def source_pair(self, prefix: tuple[int, int, int], class_index: int) -> ProjectivePair:
        key = (prefix, class_index)
        if key in self.source_cache:
            self.source_ops["cache_hits"] += 1
            return self.source_cache[key]
        point_prefix = self.advice.prefix_for(prefix, self.source_ops)
        representative = tuple(self.classes[class_index]["representative"])
        suffix = self.advice.suffix[representative]
        pair = paired_projective_add(self.advice.curve, point_prefix, suffix, self.source_ops)
        self.source_ops["unique_queries"] += 1
        self.source_cache[key] = pair
        return pair

    def value(self, target_index: int, prefix: tuple[int, int, int], class_index: int) -> int:
        key = prefix + (class_index,)
        cache = self.cache[target_index]
        if key in cache:
            self.ops[target_index]["cache_hits"] += 1
            return cache[key]
        ops = self.ops[target_index]
        pair = self.source_pair(prefix, class_index)
        target = self.targets[target_index]
        first = projective_predicate(pair.plus, pair.z2, pair.z3, target, self.p, self.nu, ops)
        second = projective_predicate(pair.minus, pair.z2, pair.z3, target, self.p, self.nu, ops)
        result = (first * second) % self.p
        ops["projective_predicate_field_multiplications"] = ops.get("projective_predicate_field_multiplications", 0) + 1
        ops["unique_queries"] += 1
        ops["zero_hits"] += int(result == 0)
        cache[key] = result
        return result


ORBIT.OrbitPredicates = ProjectivePredicates
ORBIT.BASE.OrbitPredicates = ProjectivePredicates


def run(relation_inputs: list[Path], fixture_path: Path, families: list[str], budget_labels: list[str]) -> dict[str, Any]:
    result = ORBIT.run(relation_inputs, fixture_path, families, budget_labels)
    result["protocol"] = "EXP-ECDLP-TT-PROJECTIVE-TARGET-STREAM-001-locator-v1"
    result["source"]["producer_sha256"] = sha256_file(SCRIPT_PATH)
    result["source"]["orbit_source_sha256"] = sha256_file(ORBIT_SOURCE)
    result["config"].update({
        "locator": "shared-Z Jacobian P+S/P-S source-state operator",
        "operator": "shared H/J/V/Z Jacobian formulas, no generic source inversion; exact affine fallback when x(P)=x(S)",
        "predicate": "affine norm predicate cleared by Z^6",
        "selection_uses_targets": False,
        "selection_uses_relations": False,
        "target_cache_mode": "streaming-one-target-at-a-time",
    })
    result["summary"]["boundary"] = "Streaming target-local cache over shared-Z projective source states with exact lift and affine/orbit comparators; no generic ECDLP or exponent claim."
    return result
