"""Arm-free keyed control construction for the frozen ECTD v2 meter path.

The adapter creates one atomic same-curve/same-subseed triplet.  It materializes
the complete arm-independent draw rectangle before selecting targets, so retry
counts in one target cannot shift another.  It never computes a meter and never
accepts a metric, hit, success, expected-value, or validity field from a caller.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import sys
import types
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

ALGORITHM = "ECTD-SHAKE256-RANDBELOW-v1"
TRIPLET_SCHEMA = "crypto.autoresearch.ectd_v7_control_triplet.v1"
DRAW_PLAN_SCHEMA = "crypto.autoresearch.ectd_v7_draw_plan.v1"
DRAW_SCHEMA = "crypto.autoresearch.ectd_v7_randbelow_receipt.v1"
TARGET_BUNDLE_SCHEMA = "crypto.autoresearch.ectd_v7_target_bundle.v1"
COUNTS = {"m3": 6, "m4": 6, "fb_decomposition": 24, "solver": 1}
PLANTED_ARITY = {"m3": 2, "m4": 3, "fb_decomposition": 2, "solver": 2}
RANDOM_POINT_ATTEMPTS = 64
PLANTED_ATTEMPTS = 50
BOUND_METER_SHA256 = "8a90c94b5a2b7101b4266224c441f34552cb786ed51120c4396df87c22fe312f"


class ControlError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _exact_keys(value: Mapping[str, Any], expected: Iterable[str], code: str) -> None:
    actual, wanted = set(value), set(expected)
    if actual != wanted:
        raise ControlError(code, f"missing={sorted(wanted-actual)}, extra={sorted(actual-wanted)}")


def _jcs_bytes(value: Any) -> bytes:
    def walk(item: Any) -> None:
        if isinstance(item, Mapping):
            for key, child in item.items():
                if not isinstance(key, str) or not key.isascii():
                    raise ControlError("CONTROL_MEASUREMENT_INVALID", "non-ASCII key")
                walk(child)
        elif isinstance(item, list):
            for child in item:
                walk(child)
        elif isinstance(item, float):
            raise ControlError("CONTROL_MEASUREMENT_INVALID", "floats forbidden")
        elif isinstance(item, int) and abs(item) > 9_007_199_254_740_991:
            raise ControlError("CONTROL_MEASUREMENT_INVALID", "large integers require decimal text")

    walk(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def _sha(value: Any) -> str:
    return hashlib.sha256(_jcs_bytes(value)).hexdigest()


def _decimal(value: Any, name: str) -> int:
    if not isinstance(value, str) or not value or value != str(int(value)):
        raise ControlError("CONTROL_MEASUREMENT_INVALID", f"{name} must be canonical decimal text")
    return int(value)


def canonical_curve(curve: Mapping[str, Any]) -> dict[str, Any]:
    _exact_keys(curve, ("curve_id", "model", "p", "a", "b"), "CONTROL_MEASUREMENT_INVALID")
    if curve["model"] != "short-weierstrass-y2=x3+ax+b":
        raise ControlError("CONTROL_MEASUREMENT_INVALID", "wrong curve model")
    p = _decimal(curve["p"], "p")
    a = _decimal(curve["a"], "a")
    b = _decimal(curve["b"], "b")
    if p <= 3 or p % 2 == 0 or not 0 <= a < p or not 0 <= b < p:
        raise ControlError("CONTROL_MEASUREMENT_INVALID", "noncanonical curve parameters")
    if (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p == 0:
        raise ControlError("CONTROL_MEASUREMENT_INVALID", "singular curve")
    identity = {"model": curve["model"], "p": str(p), "a": str(a), "b": str(b)}
    expected_id = hashlib.sha256(_jcs_bytes(identity)).hexdigest()
    if curve["curve_id"] != expected_id:
        raise ControlError("CONTROL_MEASUREMENT_INVALID", "curve_id is not derived from exact identity")
    return {"curve_id": expected_id, **identity}


def _config(config: Mapping[str, Any]) -> dict[str, Any]:
    _exact_keys(
        config,
        ("fb_size", "gb_budget", "macaulay_cap", "random_point_attempts", "planted_attempts"),
        "CONTROL_MEASUREMENT_INVALID",
    )
    gb = config["gb_budget"]
    _exact_keys(gb, ("max_pairs", "max_degree", "wall_seconds"), "CONTROL_MEASUREMENT_INVALID")
    if config["random_point_attempts"] != RANDOM_POINT_ATTEMPTS or config["planted_attempts"] != PLANTED_ATTEMPTS:
        raise ControlError("CONTROL_MEASUREMENT_INVALID", "retry rectangle drift")
    for key in ("fb_size", "macaulay_cap"):
        if isinstance(config[key], bool) or not isinstance(config[key], int) or config[key] <= 0:
            raise ControlError("CONTROL_MEASUREMENT_INVALID", key)
    if any(isinstance(gb[key], bool) or not isinstance(gb[key], int) or gb[key] <= 0 for key in gb):
        raise ControlError("CONTROL_MEASUREMENT_INVALID", "GB budget must use positive integral bounds")
    return {
        "fb_size": config["fb_size"],
        "gb_budget": {key: gb[key] for key in ("max_pairs", "max_degree", "wall_seconds")},
        "macaulay_cap": config["macaulay_cap"],
        "random_point_attempts": RANDOM_POINT_ATTEMPTS,
        "planted_attempts": PLANTED_ATTEMPTS,
    }


def _logical_key(
    curve_id: str,
    meter_subseed: str,
    meter_id: str,
    sample_index: int,
    attempt_index: int,
    draw_index: int,
) -> dict[str, Any]:
    return {
        "domain": ALGORITHM,
        "curve_id": curve_id,
        "meter_subseed": meter_subseed,
        "meter_id": meter_id,
        "sample_index": sample_index,
        "attempt_index": attempt_index,
        "draw_index": draw_index,
    }


def randbelow_receipt(
    *,
    curve_id: str,
    meter_subseed: str,
    meter_id: str,
    sample_index: int,
    attempt_index: int,
    draw_index: int,
    modulus: int,
    consuming_predicate: str,
    maximum_blocks: int = 64,
) -> dict[str, Any]:
    if isinstance(modulus, bool) or not isinstance(modulus, int) or modulus <= 0:
        raise ControlError("CONTROL_MEASUREMENT_INVALID", "randbelow modulus must be positive")
    predicate_modulus = {
        "random_curve_point_x": None,
        "random_curve_point_y_sign": 2,
        "planted_factor_base_index": None,
    }
    if consuming_predicate not in predicate_modulus:
        raise ControlError("CONTROL_MEASUREMENT_INVALID", "unregistered consuming predicate")
    if predicate_modulus[consuming_predicate] is not None and modulus != predicate_modulus[consuming_predicate]:
        raise ControlError("CONTROL_MEASUREMENT_INVALID", "predicate/modulus mismatch")
    key = _logical_key(curve_id, meter_subseed, meter_id, sample_index, attempt_index, draw_index)
    key_bytes = _jcs_bytes(key)
    bound = 1 << 256
    limit = bound - bound % modulus
    attempts: list[dict[str, Any]] = []
    accepted_integer: int | None = None
    accepted_block_index: int | None = None
    for block_index in range(maximum_blocks):
        prefix = hashlib.shake_256(key_bytes).digest(32 * (block_index + 1))
        block = prefix[-32:]
        integer = int.from_bytes(block, "big")
        attempts.append({
            "block_index": block_index,
            "bytes32_hex": block.hex(),
            "integer": str(integer),
        })
        if integer < limit:
            accepted_integer = integer % modulus
            accepted_block_index = block_index
            break
    if accepted_integer is None or accepted_block_index is None:
        raise ControlError("RESOURCE_LIMIT", "SHAKE256 rejection sampling exhausted")
    return {
        "schema": DRAW_SCHEMA,
        "algorithm": ALGORITHM,
        "key": key,
        "modulus": str(modulus),
        "limit": str(limit),
        "attempts": attempts,
        "accepted_block_index": accepted_block_index,
        "accepted_integer": str(accepted_integer),
        "consuming_predicate": consuming_predicate,
    }


def verify_randbelow_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    _exact_keys(
        receipt,
        ("schema", "algorithm", "key", "modulus", "limit", "attempts", "accepted_block_index", "accepted_integer", "consuming_predicate"),
        "CONTROL_MEASUREMENT_INVALID",
    )
    if receipt["schema"] != DRAW_SCHEMA or receipt["algorithm"] != ALGORITHM:
        raise ControlError("CONTROL_MEASUREMENT_INVALID", "draw schema/algorithm")
    key = receipt["key"]
    _exact_keys(
        key,
        ("domain", "curve_id", "meter_subseed", "meter_id", "sample_index", "attempt_index", "draw_index"),
        "CONTROL_MEASUREMENT_INVALID",
    )
    if key["domain"] != ALGORITHM or "arm" in key:
        raise ControlError("CONTROL_MEASUREMENT_INVALID", "draw key domain/arm")
    modulus = _decimal(receipt["modulus"], "modulus")
    predicate = receipt["consuming_predicate"]
    meter_id = key["meter_id"]
    if meter_id not in COUNTS or key["sample_index"] not in range(COUNTS[meter_id]):
        raise ControlError("CONTROL_MEASUREMENT_INVALID", "logical meter/sample key")
    if isinstance(key["attempt_index"], bool) or not isinstance(key["attempt_index"], int) or key["attempt_index"] < 0:
        raise ControlError("CONTROL_MEASUREMENT_INVALID", "logical attempt key")
    if predicate == "random_curve_point_x":
        expected_draw_index = 0
    elif predicate == "random_curve_point_y_sign":
        expected_draw_index = 1
    elif predicate == "planted_factor_base_index":
        expected_draw_index = 2 + (key["draw_index"] - 2)
        if not 2 <= key["draw_index"] < 2 + PLANTED_ARITY[meter_id]:
            raise ControlError("CONTROL_MEASUREMENT_INVALID", "planted draw index")
    else:
        raise ControlError("CONTROL_MEASUREMENT_INVALID", "unregistered consuming predicate")
    if key["draw_index"] != expected_draw_index:
        raise ControlError("CONTROL_MEASUREMENT_INVALID", "predicate/draw-index mismatch")
    expected = randbelow_receipt(
        curve_id=key["curve_id"],
        meter_subseed=key["meter_subseed"],
        meter_id=key["meter_id"],
        sample_index=key["sample_index"],
        attempt_index=key["attempt_index"],
        draw_index=key["draw_index"],
        modulus=modulus,
        consuming_predicate=predicate,
        maximum_blocks=len(receipt["attempts"]),
    )
    if dict(receipt) != expected:
        raise ControlError("CONTROL_MEASUREMENT_INVALID", "draw receipt replay mismatch")
    return expected


def _target_specs() -> Iterable[tuple[str, int]]:
    for meter_id in ("m3", "m4", "fb_decomposition", "solver"):
        for sample_index in range(COUNTS[meter_id]):
            yield meter_id, sample_index


def _verify_draw_plan_receipts(
    plan: Mapping[str, Any],
    curve_record: Mapping[str, Any],
    meter_subseed: str,
    config: Mapping[str, Any],
) -> None:
    _exact_keys(
        plan,
        ("schema", "algorithm", "curve_id", "meter_subseed", "counts", "targets", "draw_plan_id"),
        "CONTROL_MEASUREMENT_INVALID",
    )
    body = {key: plan[key] for key in ("schema", "algorithm", "curve_id", "meter_subseed", "counts", "targets")}
    if plan["draw_plan_id"] != _sha(body):
        raise ControlError("CONTROL_MEASUREMENT_INVALID", "draw plan locator mismatch")
    if (
        plan["schema"] != DRAW_PLAN_SCHEMA
        or plan["algorithm"] != ALGORITHM
        or plan["curve_id"] != curve_record["curve_id"]
        or plan["meter_subseed"] != meter_subseed
        or plan["counts"] != COUNTS
    ):
        raise ControlError("CONTROL_MEASUREMENT_INVALID", "draw plan root binding")
    targets = plan["targets"]
    expected_specs = list(_target_specs())
    if not isinstance(targets, list) or len(targets) != len(expected_specs):
        raise ControlError("CONTROL_MEASUREMENT_INVALID", "draw target cardinality")
    p = curve_record["p"]
    fb_size = str(config["fb_size"])
    for target, (meter_id, sample_index) in zip(targets, expected_specs):
        _exact_keys(target, ("meter_id", "sample_index", "random_attempts", "planted_attempts"), "CONTROL_MEASUREMENT_INVALID")
        if target["meter_id"] != meter_id or target["sample_index"] != sample_index:
            raise ControlError("CONTROL_MEASUREMENT_INVALID", "draw target ordering")
        random_attempts = target["random_attempts"]
        planted_attempts = target["planted_attempts"]
        if not isinstance(random_attempts, list) or len(random_attempts) != RANDOM_POINT_ATTEMPTS:
            raise ControlError("CONTROL_MEASUREMENT_INVALID", "random draw rectangle")
        if not isinstance(planted_attempts, list) or len(planted_attempts) != PLANTED_ATTEMPTS:
            raise ControlError("CONTROL_MEASUREMENT_INVALID", "planted draw rectangle")
        for attempt_index, attempt in enumerate(random_attempts):
            _exact_keys(attempt, ("attempt_index", "x", "sign"), "CONTROL_MEASUREMENT_INVALID")
            if attempt["attempt_index"] != attempt_index:
                raise ControlError("CONTROL_MEASUREMENT_INVALID", "random attempt ordering")
            if attempt["x"].get("modulus") != p:
                raise ControlError("CONTROL_MEASUREMENT_INVALID", "random x modulus")
            if attempt["sign"].get("modulus") != "2":
                raise ControlError("CONTROL_MEASUREMENT_INVALID", "random sign modulus")
            verify_randbelow_receipt(attempt["x"])
            verify_randbelow_receipt(attempt["sign"])
        for attempt_index, attempt in enumerate(planted_attempts):
            _exact_keys(attempt, ("attempt_index", "factor_base_indices"), "CONTROL_MEASUREMENT_INVALID")
            if attempt["attempt_index"] != attempt_index:
                raise ControlError("CONTROL_MEASUREMENT_INVALID", "planted attempt ordering")
            draws = attempt["factor_base_indices"]
            if not isinstance(draws, list) or len(draws) != PLANTED_ARITY[meter_id]:
                raise ControlError("CONTROL_MEASUREMENT_INVALID", "planted arity")
            for receipt in draws:
                if receipt.get("modulus") != fb_size:
                    raise ControlError("CONTROL_MEASUREMENT_INVALID", "factor-base modulus")
                verify_randbelow_receipt(receipt)


def build_draw_plan(
    curve: Mapping[str, Any],
    meter_subseed: str,
    config: Mapping[str, Any],
) -> dict[str, Any]:
    curve_record = canonical_curve(curve)
    frozen_config = _config(config)
    if not isinstance(meter_subseed, str) or not meter_subseed or len(meter_subseed) > 128:
        raise ControlError("CONTROL_MEASUREMENT_INVALID", "meter_subseed text")
    p = int(curve_record["p"])
    fb_size = frozen_config["fb_size"]
    targets: list[dict[str, Any]] = []
    for meter_id, sample_index in _target_specs():
        random_attempts: list[dict[str, Any]] = []
        for attempt_index in range(RANDOM_POINT_ATTEMPTS):
            random_attempts.append({
                "attempt_index": attempt_index,
                "x": randbelow_receipt(
                    curve_id=curve_record["curve_id"], meter_subseed=meter_subseed,
                    meter_id=meter_id, sample_index=sample_index,
                    attempt_index=attempt_index, draw_index=0, modulus=p,
                    consuming_predicate="random_curve_point_x",
                ),
                "sign": randbelow_receipt(
                    curve_id=curve_record["curve_id"], meter_subseed=meter_subseed,
                    meter_id=meter_id, sample_index=sample_index,
                    attempt_index=attempt_index, draw_index=1, modulus=2,
                    consuming_predicate="random_curve_point_y_sign",
                ),
            })
        planted_attempts: list[dict[str, Any]] = []
        for attempt_index in range(PLANTED_ATTEMPTS):
            draws = [
                randbelow_receipt(
                    curve_id=curve_record["curve_id"], meter_subseed=meter_subseed,
                    meter_id=meter_id, sample_index=sample_index,
                    attempt_index=attempt_index, draw_index=2 + draw_index,
                    modulus=fb_size, consuming_predicate="planted_factor_base_index",
                )
                for draw_index in range(PLANTED_ARITY[meter_id])
            ]
            planted_attempts.append({"attempt_index": attempt_index, "factor_base_indices": draws})
        targets.append({
            "meter_id": meter_id,
            "sample_index": sample_index,
            "random_attempts": random_attempts,
            "planted_attempts": planted_attempts,
        })
    body = {
        "schema": DRAW_PLAN_SCHEMA,
        "algorithm": ALGORITHM,
        "curve_id": curve_record["curve_id"],
        "meter_subseed": meter_subseed,
        "counts": dict(COUNTS),
        "targets": targets,
    }
    return {**body, "draw_plan_id": _sha(body)}


def _load_bound_modules(repository_root: Path) -> Mapping[str, Any]:
    manifest_path = Path(__file__).resolve().parent / "arithmetic-input-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    bindings = {entry["role"]: entry for entry in manifest["bound_sources"]}
    required = {"fp", "curve", "semaev", "mvpoly", "groebner", "macaulay", "meters"}
    if not required.issubset(bindings):
        raise ControlError("SOURCE_GAP", f"missing bound roles: {sorted(required-set(bindings))}")
    for role in required:
        binding = bindings[role]
        data = (repository_root / binding["path"]).read_bytes()
        if len(data) != binding["size_bytes"] or hashlib.sha256(data).hexdigest() != binding["sha256"]:
            raise ControlError("CUSTODY_FAILURE", binding["path"])
    if bindings["meters"]["sha256"] != BOUND_METER_SHA256:
        raise ControlError("CUSTODY_FAILURE", "operative v2 meter hash drift")
    package_name = "_ectd_v7_bound_reused"
    package_dir = (repository_root / bindings["meters"]["path"]).parent
    package = types.ModuleType(package_name)
    package.__path__ = [str(package_dir)]
    package.__package__ = package_name
    sys.modules[package_name] = package
    old = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        loaded = {
            role: importlib.import_module(f"{package_name}.{role}")
            for role in ("fp", "curve", "semaev", "mvpoly", "groebner", "macaulay", "meters")
        }
    finally:
        sys.dont_write_bytecode = old
    return loaded


def _selected(receipt: Mapping[str, Any]) -> int:
    return int(verify_randbelow_receipt(receipt)["accepted_integer"])


def _build_targets(
    curve_record: Mapping[str, Any],
    config: Mapping[str, Any],
    draw_plan: Mapping[str, Any],
    repository_root: Path,
) -> dict[str, Any]:
    modules = _load_bound_modules(repository_root)
    fp, curve_mod, meters = modules["fp"], modules["curve"], modules["meters"]
    p, a, b = (int(curve_record[key]) for key in ("p", "a", "b"))
    fb = meters.get_fb(a, b, p, config["fb_size"])
    fb_points = [meters.fb_point(x, a, b, p) for x in fb]
    unplanted: list[dict[str, Any]] = []
    planted: list[dict[str, Any]] = []
    for target in draw_plan["targets"]:
        meter_id, sample_index = target["meter_id"], target["sample_index"]
        random_point = None
        random_attempt_index = None
        for attempt in target["random_attempts"]:
            x = _selected(attempt["x"])
            rhs = (pow(x, 3, p) + a * x + b) % p
            y = fp.sqrt_mod(rhs, p)
            if y is not None:
                sign = _selected(attempt["sign"])
                y = min(y, p - y) if sign == 0 else max(y, p - y)
                random_point = (x, y)
                random_attempt_index = attempt["attempt_index"]
                break
        if random_point is None:
            raise ControlError("RESOURCE_LIMIT", f"random point rectangle exhausted: {meter_id}/{sample_index}")
        planted_point = None
        planted_attempt_index = None
        for attempt in target["planted_attempts"]:
            indices = [_selected(receipt) for receipt in attempt["factor_base_indices"]]
            point = None
            for index in indices:
                point = curve_mod.add(point, fb_points[index], a, p)
            if point is not None:
                planted_point = point
                planted_attempt_index = attempt["attempt_index"]
                break
        if planted_point is None:
            raise ControlError("RESOURCE_LIMIT", f"planted rectangle exhausted: {meter_id}/{sample_index}")
        unplanted.append({
            "meter_id": meter_id,
            "sample_index": sample_index,
            "point": {"x": str(random_point[0]), "y": str(random_point[1])},
            "construction": "keyed-random-curve-point",
            "selected_attempt": random_attempt_index,
        })
        planted.append({
            "meter_id": meter_id,
            "sample_index": sample_index,
            "point": {"x": str(planted_point[0]), "y": str(planted_point[1])},
            "construction": "keyed-factor-base-sum",
            "selected_attempt": planted_attempt_index,
        })
    common = {
        "schema": TARGET_BUNDLE_SCHEMA,
        "curve_id": curve_record["curve_id"],
        "meter_subseed": draw_plan["meter_subseed"],
        "counts": dict(COUNTS),
        "factor_base": [str(x) for x in fb],
    }
    ordinary_body = {**common, "targets": unplanted}
    planted_body = {**common, "targets": planted}
    return {
        "unplanted": {**ordinary_body, "target_bundle_id": _sha(ordinary_body)},
        "planted": {**planted_body, "target_bundle_id": _sha(planted_body)},
    }


def build_atomic_triplet(
    curve: Mapping[str, Any],
    meter_subseed: str,
    config: Mapping[str, Any],
    repository_root: Path,
) -> dict[str, Any]:
    curve_record = canonical_curve(curve)
    frozen_config = _config(config)
    draw_plan = build_draw_plan(curve_record, meter_subseed, frozen_config)
    bundles = _build_targets(curve_record, frozen_config, draw_plan, repository_root)
    root_body = {
        "curve": curve_record,
        "meter_subseed": meter_subseed,
        "config": frozen_config,
        "draw_plan_id": draw_plan["draw_plan_id"],
    }
    root = {**root_body, "root_id": _sha(root_body)}
    arms = [
        {"arm": "ordinary", "plant_requested": False, "planting_code_enabled": True, "effective": False, "target_bundle_id": bundles["unplanted"]["target_bundle_id"]},
        {"arm": "planted", "plant_requested": True, "planting_code_enabled": True, "effective": True, "target_bundle_id": bundles["planted"]["target_bundle_id"]},
        {"arm": "disabled_negative", "plant_requested": True, "planting_code_enabled": False, "effective": False, "target_bundle_id": bundles["unplanted"]["target_bundle_id"]},
    ]
    body = {
        "schema": TRIPLET_SCHEMA,
        "root": root,
        "draw_plan": draw_plan,
        "target_bundles": bundles,
        "arms": arms,
    }
    return {**body, "triplet_id": _sha(body)}


def _scan_forbidden(value: Any, pointer: str = "") -> None:
    forbidden = {
        "metric", "metrics", "hit", "hits", "success", "expected", "valid",
        "semaev_m3_relation_density", "semaev_m4_relation_density",
        "fb_decomposition_probability", "groebner_solving_degree_d_reg",
        "macaulay_rank_defect_at_first_fall",
    }
    if isinstance(value, Mapping):
        found = forbidden.intersection(value)
        if found:
            raise ControlError("CONTROL_MEASUREMENT_INVALID", f"forbidden target truth at {pointer}: {sorted(found)}")
        for key, child in value.items():
            _scan_forbidden(child, f"{pointer}/{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_forbidden(child, f"{pointer}/{index}")


def verify_atomic_triplet(triplet: Mapping[str, Any], repository_root: Path) -> dict[str, Any]:
    _exact_keys(triplet, ("schema", "root", "draw_plan", "target_bundles", "arms", "triplet_id"), "CONTROL_MEASUREMENT_INVALID")
    if triplet["schema"] != TRIPLET_SCHEMA:
        raise ControlError("CONTROL_MEASUREMENT_INVALID", "triplet schema")
    body = {key: triplet[key] for key in ("schema", "root", "draw_plan", "target_bundles", "arms")}
    if triplet["triplet_id"] != _sha(body):
        raise ControlError("CONTROL_MEASUREMENT_INVALID", "triplet hash locator mismatch")
    root = triplet["root"]
    _exact_keys(root, ("curve", "meter_subseed", "config", "draw_plan_id", "root_id"), "CONTROL_MEASUREMENT_INVALID")
    curve_record = canonical_curve(root["curve"])
    config = _config(root["config"])
    root_body = {key: root[key] for key in ("curve", "meter_subseed", "config", "draw_plan_id")}
    if root["root_id"] != _sha(root_body):
        raise ControlError("CONTROL_MEASUREMENT_INVALID", "root locator mismatch")
    plan = triplet["draw_plan"]
    _verify_draw_plan_receipts(plan, curve_record, root["meter_subseed"], config)
    expected_plan = build_draw_plan(curve_record, root["meter_subseed"], config)
    if plan != expected_plan or root["draw_plan_id"] != plan["draw_plan_id"]:
        raise ControlError("CONTROL_MEASUREMENT_INVALID", "draw plan replay mismatch")
    _scan_forbidden(triplet["target_bundles"], "/target_bundles")
    bundles = triplet["target_bundles"]
    _exact_keys(bundles, ("unplanted", "planted"), "CONTROL_MEASUREMENT_INVALID")
    for bundle in bundles.values():
        if bundle.get("curve_id") != curve_record["curve_id"] or bundle.get("meter_subseed") != root["meter_subseed"]:
            raise ControlError("CONTROL_MEASUREMENT_INVALID", "target curve/subseed binding")
    expected_bundles = _build_targets(curve_record, config, plan, repository_root)
    if bundles != expected_bundles:
        raise ControlError("CONTROL_MEASUREMENT_INVALID", "target bundle replay mismatch")
    expected_arms = [
        {"arm": "ordinary", "plant_requested": False, "planting_code_enabled": True, "effective": False, "target_bundle_id": expected_bundles["unplanted"]["target_bundle_id"]},
        {"arm": "planted", "plant_requested": True, "planting_code_enabled": True, "effective": True, "target_bundle_id": expected_bundles["planted"]["target_bundle_id"]},
        {"arm": "disabled_negative", "plant_requested": True, "planting_code_enabled": False, "effective": False, "target_bundle_id": expected_bundles["unplanted"]["target_bundle_id"]},
    ]
    if triplet["arms"] != expected_arms:
        raise ControlError("CONTROL_MEASUREMENT_INVALID", "arm flag or bundle binding mismatch")
    if _jcs_bytes(expected_bundles["unplanted"]) != _jcs_bytes(triplet["target_bundles"]["unplanted"]):
        raise ControlError("CONTROL_MEASUREMENT_INVALID", "ordinary/disabled target bytes mismatch")
    return {
        "schema": "crypto.autoresearch.ectd_v7_control_replay.v1",
        "status": "accepted",
        "triplet_id": triplet["triplet_id"],
        "curve_id": curve_record["curve_id"],
        "meter_subseed": root["meter_subseed"],
        "counts": dict(COUNTS),
        "ordinary_disabled_target_bundle_id": expected_bundles["unplanted"]["target_bundle_id"],
    }


if __name__ == "__main__":
    raise SystemExit("static control adapter; downstream Executor owns conformance")
