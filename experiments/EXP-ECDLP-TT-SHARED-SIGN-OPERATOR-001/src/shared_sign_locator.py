#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[3]
ORBIT_SOURCE = REPO_ROOT / "experiments" / "EXP-ECDLP-TT-SOURCE-ORBIT-QUOTIENT-001" / "src" / "orbit_quotient_locator.py"


def load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ORBIT = load("shared_sign_orbit_base", ORBIT_SOURCE)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def paired_affine_add(curve: Any, left: tuple[int, int] | None, right: tuple[int, int] | None, ops: dict[str, int]) -> tuple[tuple[int, int] | None, tuple[int, int] | None]:
    """Compute left+right and left-right with one inversion off the diagonal."""
    ops["paired_source_calls"] = ops.get("paired_source_calls", 0) + 1
    if left is None:
        ops["paired_identity_calls"] = ops.get("paired_identity_calls", 0) + 1
        return right, right
    if right is None:
        ops["paired_identity_calls"] = ops.get("paired_identity_calls", 0) + 1
        return left, left
    p = curve.p
    x1, y1 = left
    x2, y2 = right
    if x1 == x2:
        ops["paired_fallback_calls"] = ops.get("paired_fallback_calls", 0) + 1
        plus = curve.add(left, right, ops)
        minus = curve.add(left, ORBIT.neg_point(right, p, ops), ops)
        return plus, minus
    denominator = (x2 - x1) % p
    inverse = pow(denominator, -1, p)
    plus_slope = ((y2 - y1) % p) * inverse % p
    minus_slope = ((-y2 - y1) % p) * inverse % p
    plus_x = (plus_slope * plus_slope - x1 - x2) % p
    minus_x = (minus_slope * minus_slope - x1 - x2) % p
    plus_y = (plus_slope * (x1 - plus_x) - y1) % p
    minus_y = (minus_slope * (x1 - minus_x) - y1) % p
    ops["point_add_calls"] = ops.get("point_add_calls", 0) + 2
    ops["field_inversions"] = ops.get("field_inversions", 0) + 1
    ops["field_multiplications"] = ops.get("field_multiplications", 0) + 6
    ops["field_subtractions"] = ops.get("field_subtractions", 0) + 8
    ops["paired_shared_inversions"] = ops.get("paired_shared_inversions", 0) + 1
    return (plus_x, plus_y), (minus_x, minus_y)


class SharedSignPredicates(ORBIT.OrbitPredicates):
    def source_pair(self, prefix: tuple[int, int, int], class_index: int) -> tuple[tuple[int, int] | None, tuple[int, int] | None]:
        key = (prefix, class_index)
        if key in self.source_cache:
            self.source_ops["cache_hits"] += 1
            return self.source_cache[key]
        point_prefix = self.advice.prefix_for(prefix, self.source_ops)
        representative = tuple(self.classes[class_index]["representative"])
        suffix = self.advice.suffix[representative]
        pair = paired_affine_add(self.advice.curve, point_prefix, suffix, self.source_ops)
        self.source_ops["unique_queries"] += 1
        self.source_cache[key] = pair
        return pair


ORBIT.OrbitPredicates = SharedSignPredicates


def run(relation_inputs: list[Path], fixture_path: Path, families: list[str], budget_labels: list[str]) -> dict[str, Any]:
    result = ORBIT.run(relation_inputs, fixture_path, families, budget_labels)
    result["protocol"] = "EXP-ECDLP-TT-SHARED-SIGN-OPERATOR-001-locator-v1"
    result["source"]["producer_sha256"] = sha256_file(SCRIPT_PATH)
    result["source"]["orbit_source_sha256"] = sha256_file(ORBIT_SOURCE)
    result["config"].update({
        "locator": "paired affine shared-sign P+S/P-S source-state operator",
        "operator": "one denominator inversion for generic P,S; exact affine fallback when x(P)=x(S)",
        "selection_uses_targets": False,
        "selection_uses_relations": False,
    })
    result["summary"]["boundary"] = "Two fresh 14-bit paired shared-sign source-state replications with exact member lift and committed naive/original comparators; no generic ECDLP or exponent claim."
    return result
