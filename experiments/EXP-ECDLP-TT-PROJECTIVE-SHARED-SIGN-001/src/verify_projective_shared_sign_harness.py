#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))
BASE_SOURCE = REPO_ROOT / "experiments" / "EXP-ECDLP-TT-SAMPLED-REPLICATION-001" / "src" / "run_fresh_replication_harness.py"
INPUT_SOURCE = REPO_ROOT / "experiments" / "EXP-ECDLP-TT-SAMPLED-SCALE-001" / "src" / "typed_tt_sampled_relation_input.py"
BASE_VERIFY_SOURCE = REPO_ROOT / "experiments" / "EXP-ECDLP-TT-SOURCE-ORBIT-QUOTIENT-001" / "src" / "verify_orbit_quotient_replication_harness.py"
ORBIT_SOURCE = REPO_ROOT / "experiments" / "EXP-ECDLP-TT-SOURCE-ORBIT-QUOTIENT-001" / "src" / "orbit_quotient_locator.py"
PROJECTIVE_SOURCE = SCRIPT_PATH.with_name("projective_shared_sign_locator.py")
GENERATOR_SOURCE = SCRIPT_PATH.with_name("run_projective_shared_sign_harness.py")


def load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load("projective_verifier_fresh_base", BASE_SOURCE)
INPUT = load("projective_verifier_relation_input", INPUT_SOURCE)
VERIFY = load("projective_verifier_affine_checks", BASE_VERIFY_SOURCE)
ORBIT = load("projective_verifier_affine_orbit", ORBIT_SOURCE)
PROJECTIVE = load("projective_verifier_locator", PROJECTIVE_SOURCE)
FRESH = BASE.FRESH
FAMILIES = BASE.FAMILIES
FRESH_SEEDS = [271828, 161803, 424242]
BUDGETS = ["32", "44", "full"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_fixture(value: dict[str, Any]) -> dict[str, Any]:
    def normalize(item: Any) -> Any:
        if isinstance(item, dict):
            return {key: normalize(child) for key, child in item.items() if key not in {"wall_seconds", "total_wall_seconds"}}
        if isinstance(item, list):
            return [normalize(child) for child in item]
        return item
    return normalize(value)


def independent_add(curve: dict[str, Any], left: tuple[int, int] | None, right: tuple[int, int] | None) -> tuple[int, int] | None:
    p = int(curve["p"])
    a = int(curve["a"]) % p
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if left == right:
        if y1 % p == 0:
            return None
        numerator = (3 * x1 * x1 + a) % p
        denominator = (2 * y1) % p
    else:
        numerator = (y2 - y1) % p
        denominator = (x2 - x1) % p
    slope = numerator * pow(denominator, -1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    return x3, (slope * (x1 - x3) - y1) % p


def independent_classes(curve: dict[str, Any], family: dict[str, Any]) -> list[dict[str, Any]]:
    points = [None if value is None else (int(value[0]), int(value[1])) for value in family["factor_base"]["points"]]
    grouped: dict[int | None, list[tuple[int, int]]] = {}
    for left in range(len(points)):
        for right in range(len(points)):
            point = independent_add(curve, points[left], points[right])
            grouped.setdefault(None if point is None else point[0], []).append((left, right))
    classes = []
    for index, key in enumerate(sorted(grouped, key=lambda value: (-1 if value is None else value))):
        members = sorted(grouped[key])
        representative = members[0]
        point = independent_add(curve, points[representative[0]], points[representative[1]])
        classes.append({"class_index": index, "x_orbit_key": key, "representative": list(representative), "members": [list(item) for item in members], "member_count": len(members), "representative_point": None if point is None else list(point)})
    return classes


def to_affine(point: tuple[int, int, int] | None, p: int) -> tuple[int, int] | None:
    if point is None:
        return None
    x, y, z = point
    if z % p == 0:
        return None
    inverse = pow(z, -1, p)
    return x * inverse * inverse % p, y * inverse * inverse * inverse % p


def affine_predicate(point: tuple[int, int] | None, target: tuple[int, int], p: int, nu: int) -> int:
    if point is None:
        return 1
    dx = (point[0] - target[0]) % p
    dy = (point[1] - target[1]) % p
    return (dx * dx - nu * dy * dy) % p


def projective_operator_checks(curve: dict[str, Any], family: dict[str, Any], targets: list[tuple[int, int]]) -> dict[str, Any]:
    advice = PROJECTIVE.ORBIT.STREAMING.StreamingSourceAdvice(curve, family)
    classes = independent_classes(curve, family)
    a_size = len(family["progression"]["points"])
    b_size = len(family["factor_base"]["points"])
    prefixes = PROJECTIVE.ORBIT.ADAPTIVE.SOURCE_AWARE.prefix_order(a_size, b_size)
    nu = PROJECTIVE.ORBIT.ORACLE.nonsquare(int(curve["p"]))
    checks = 0
    scale_checks = 0
    fallback_cases = 0
    for prefix in prefixes:
        point_prefix = advice.prefix_for(prefix, advice.ops)
        for item in classes:
            suffix = advice.suffix[tuple(item["representative"])]
            ops = PROJECTIVE.ORBIT.zero_ops()
            pair = PROJECTIVE.paired_projective_add(advice.curve, point_prefix, suffix, ops)
            expected_plus = independent_add(curve, point_prefix, suffix)
            expected_minus = independent_add(curve, point_prefix, None if suffix is None else (suffix[0], -suffix[1] % int(curve["p"])))
            actual_plus = to_affine(pair.plus, int(curve["p"]))
            actual_minus = to_affine(pair.minus, int(curve["p"]))
            if actual_plus != expected_plus or actual_minus != expected_minus:
                raise AssertionError(f"projective reconstruction mismatch at {prefix}/{item['class_index']}")
            if ops.get("paired_fallback_calls", 0) or ops.get("paired_identity_calls", 0):
                fallback_cases += 1
            for target in targets[:2]:
                affine_plus = affine_predicate(expected_plus, target, int(curve["p"]), nu)
                affine_minus = affine_predicate(expected_minus, target, int(curve["p"]), nu)
                projective_plus = PROJECTIVE.projective_predicate(pair.plus, pair.z2, pair.z3, target, int(curve["p"]), nu, PROJECTIVE.ORBIT.zero_ops())
                projective_minus = PROJECTIVE.projective_predicate(pair.minus, pair.z2, pair.z3, target, int(curve["p"]), nu, PROJECTIVE.ORBIT.zero_ops())
                affine_product = affine_plus * affine_minus % int(curve["p"])
                projective_product = projective_plus * projective_minus % int(curve["p"])
                expected_scale = pow(pair.plus[2], 12, int(curve["p"])) if pair.plus is not None else 1
                if (projective_product == 0) != (affine_product == 0):
                    raise AssertionError(f"zero-equivalence mismatch at {prefix}/{item['class_index']}")
                if affine_product != 0 and projective_product != affine_product * expected_scale % int(curve["p"]):
                    raise AssertionError(f"target-dependent homogeneous scale at {prefix}/{item['class_index']}")
                checks += 1
                scale_checks += int(affine_product != 0)
    return {"source_states": len(prefixes) * len(classes), "zero_equivalence_checks": checks, "nonzero_scale_checks": scale_checks, "exceptional_source_states": fallback_cases}


def verify_case(case: dict[str, Any], fixture: dict[str, Any], fixture_path: Path, relation_path: Path) -> dict[str, Any]:
    # Reuse the existing independent support/witness/class verifier, but keep
    # the affine locator only as its independent witness arithmetic oracle.
    old_locator = VERIFY.LOCATOR
    old_generator = VERIFY.GENERATOR_SOURCE
    old_locator_source = VERIFY.LOCATOR_SOURCE
    old_budgets = VERIFY.BUDGETS
    VERIFY.LOCATOR = ORBIT
    VERIFY.GENERATOR_SOURCE = GENERATOR_SOURCE
    VERIFY.LOCATOR_SOURCE = PROJECTIVE_SOURCE
    VERIFY.BUDGETS = BUDGETS
    transformed = copy.deepcopy(case)
    transformed["candidate"]["protocol"] = "EXP-ECDLP-TT-SOURCE-ORBIT-QUOTIENT-001-candidate-v1"
    base_checks = VERIFY.verify_case(transformed, fixture, fixture_path, relation_path)
    VERIFY.LOCATOR = old_locator
    VERIFY.GENERATOR_SOURCE = old_generator
    VERIFY.LOCATOR_SOURCE = old_locator_source
    VERIFY.BUDGETS = old_budgets
    instance = fixture["instances"][0]
    relation_input = INPUT.write_fixture_record(relation_path, fixture_path, instance["curve"]["id"], FAMILIES)
    families = {item["family"]: item for item in instance["families"]}
    arithmetic = {}
    for family in FAMILIES:
        targets = [tuple(int(value) for value in item["target"]) for item in next(row for row in relation_input["rows"] if row["family"] == family)["shared_candidate"]["transcripts"]]
        arithmetic[family] = projective_operator_checks(instance["curve"], families[family], targets)
    candidate = case["candidate"]
    hashes = {
        "projective_locator_hash": candidate.get("source", {}).get("projective_locator_sha256") == sha256(PROJECTIVE_SOURCE),
        "harness_hash": candidate.get("source", {}).get("harness_source_sha256") == sha256(GENERATOR_SOURCE),
        "comparators_present": set(case.get("comparisons", {})) == set(FAMILIES),
    }
    return {"base": base_checks, "hashes": hashes, "arithmetic": arithmetic}


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_projective_shared_sign_harness.py GENERATOR_RAW_RESULT")
    raw_path = Path(sys.argv[1]).resolve()
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    checks: dict[str, Any] = {
        "generator_valid": raw.get("valid") is True,
        "inputs": raw.get("inputs", {}).get("seeds") == FRESH_SEEDS and raw.get("inputs", {}).get("budgets") == BUDGETS and raw.get("inputs", {}).get("families") == FAMILIES,
        "case_count": len(raw.get("cases", [])) == len(FRESH_SEEDS),
    }
    with tempfile.TemporaryDirectory(prefix="tt-projective-shared-sign-verify-") as temp:
        root = Path(temp)
        for seed, case in zip(FRESH_SEEDS, raw.get("cases", [])):
            fixture = canonical_fixture(FRESH.run_experiment([14], seed, FAMILIES, 0.5, 32))
            fixture_path = root / f"fixture-{seed}.json"
            fixture_path.write_text(json.dumps(fixture, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
            relation_path = root / f"relation-{seed}.json"
            result = verify_case(case, fixture, fixture_path, relation_path)
            for name, value in result["base"].items():
                checks[f"{seed}_support_{name}"] = value
            for name, value in result["hashes"].items():
                checks[f"{seed}_{name}"] = value
            for family, metrics in result["arithmetic"].items():
                checks[f"{seed}_{family}_arithmetic"] = metrics["source_states"] > 0 and metrics["zero_equivalence_checks"] > 0 and metrics["zero_equivalence_checks"] == metrics["source_states"] * 2
                checks[f"{seed}_{family}_scale"] = metrics["nonzero_scale_checks"] >= 0
            checks[f"{seed}_curve_match"] = case.get("curve_id") == fixture["instances"][0]["curve"]["id"]
    checks["valid"] = all(value if isinstance(value, bool) else all(value.values()) if isinstance(value, dict) else True for value in checks.values())
    output = {"valid": checks["valid"], "protocol": "EXP-ECDLP-TT-PROJECTIVE-SHARED-SIGN-001-harness-verifier-v1", "input": {"sha256": sha256(raw_path), "path": str(raw_path)}, "checks": checks, "summary": {"accepted_subfull_budgets": raw.get("summary", {}).get("accepted_subfull_budgets"), "boundary": "Independent affine class/support verification plus full projective reconstruction and homogeneous zero-equivalence checks; no generic ECDLP or exponent claim."}}
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0 if output["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
