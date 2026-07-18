#!/usr/bin/env python3
"""Outer-aware exact floors and coordinate elimination for toy prime-field ECDLP."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import random
import statistics
import sys
import time
from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable


PROTOCOL = "EXP-ECDLP-OUTER-TRANSLATOR-001-development-v1"
CLAIM_STATUS = ["HYPOTHESIS", "TOY-EVIDENCE", "HEURISTIC", "MODEL-BOUND"]
SCRIPT_PATH = Path(__file__).resolve()
EXPERIMENT_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = SCRIPT_PATH.parents[3]
SOURCE_TAG_PATH = (
    REPO_ROOT
    / "experiments"
    / "EXP-ECDLP-SOURCE-TAG-JOIN-001"
    / "src"
    / "source_tag_join.py"
)
COMPRESSED_JOIN_PATH = (
    REPO_ROOT
    / "experiments"
    / "EXP-ECDLP-COMPRESSED-JOIN-001"
    / "src"
    / "compressed_join.py"
)
FIXED_COMPILER_PATH = (
    REPO_ROOT
    / "experiments"
    / "EXP-ECDLP-FIXED-COMPILER-001"
    / "src"
    / "fixed_curve_compiler.py"
)
COORDINATE_ENERGY_PATH = (
    REPO_ROOT
    / "experiments"
    / "EXP-ECDLP-ENERGY-001"
    / "src"
    / "coordinate_energy.py"
)
EXACT_FLOOR_PATH = SCRIPT_PATH.with_name("exact_floor.py")
POLYNOMIAL_PATH = SCRIPT_PATH.with_name("polynomial_engine.py")
VERIFIER_PATH = SCRIPT_PATH.with_name("verify_outer_translator.py")
RUN_WRAPPER_PATH = SCRIPT_PATH.with_name("run_development.py")
CONTRACT_PATH = EXPERIMENT_ROOT / "contract.md"
HYPOTHESIS_PATH = EXPERIMENT_ROOT / "hypothesis.json"
QUESTION_PATH = EXPERIMENT_ROOT / "research-question.json"
THEORY_PATH = EXPERIMENT_ROOT / "theory.md"
IMPLEMENTATION_PATH = EXPERIMENT_ROOT / "implementation.md"
LITERATURE_PATH = EXPERIMENT_ROOT / "literature-refresh-2026-07-17.md"
PRE_RUN_THEORY_V1_PATH = EXPERIMENT_ROOT / "pre-run-theory-review-v1.md"
PRE_RUN_THEORY_V2_PATH = EXPERIMENT_ROOT / "pre-run-theory-review-v2.md"
PRE_RUN_THEORY_V3_PATH = EXPERIMENT_ROOT / "pre-run-theory-review-v3.md"
PRE_RUN_THEORY_V4_PATH = EXPERIMENT_ROOT / "pre-run-theory-review-v4.md"
PRE_RUN_RED_TEAM_V1_PATH = EXPERIMENT_ROOT / "pre-run-red-team-v1.md"
PRE_RUN_RED_TEAM_V2_PATH = EXPERIMENT_ROOT / "pre-run-red-team-v2.md"
PRE_RUN_RED_TEAM_V3_PATH = EXPERIMENT_ROOT / "pre-run-red-team-v3.md"
MOV_EMBEDDING_DEGREE_THRESHOLD = 20
LOADED_GENERATOR_SHA256 = hashlib.sha256(SCRIPT_PATH.read_bytes()).hexdigest()
LOADED_SOURCE_TAG_SHA256 = hashlib.sha256(SOURCE_TAG_PATH.read_bytes()).hexdigest()

FLOOR_FAMILIES = [
    "x_interval",
    "square_map",
    "rational_union",
    "random_x",
    "random_scalar",
    "scalar_progression",
]
TRANSLATOR_FAMILIES = [
    "x_interval",
    "square_map",
    "rational_union",
    "random_x",
]
INVERSION_WEIGHTS = [10, 50, 100]
FROZEN_CONFIG = {
    "bit_sizes": [10, 12, 14],
    "seeds": [3317584535, 2246822507, 8],
    "floor_families": FLOOR_FAMILIES,
    "translator_families": TRANSLATOR_FAMILIES,
    "partial_d3_fractions": [[1, 8], [1, 4], [1, 2]],
    "batch_multipliers": [1, 16],
    "batch_replicates": 4,
    "coordinate_targets": 4,
    "occupancy_lambda": 0.5,
    "rho_trials": 3,
}

Point = tuple[int, int] | None


@dataclass
class SymmetryD3Codec:
    entries: dict[int, tuple[int, int, int]]
    identity_witness: tuple[int, int, int] | None
    record: dict[str, Any]


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


SOURCE = load_module("outer_translator_source_tag", SOURCE_TAG_PATH)
BASE = SOURCE.BASE
Curve = SOURCE.Curve
Ops = SOURCE.Ops


def load_exact_floor() -> Any:
    return load_module("outer_translator_exact_floor", EXACT_FLOOR_PATH)


def load_polynomial_engine() -> Any:
    return load_module("outer_translator_polynomial_engine", POLYNOMIAL_PATH)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def stable_digest(value: Any) -> str:
    return hashlib.sha256(stable_json_bytes(value)).hexdigest()


def json_native(value: Any) -> Any:
    if value is None or type(value) in {bool, int, float, str}:
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("nonfinite value cannot enter an artifact")
        return value
    if isinstance(value, dict):
        return {str(key): json_native(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_native(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return [json_native(item) for item in sorted(value, key=repr)]
    if hasattr(value, "to_record") and callable(value.to_record):
        return json_native(value.to_record())
    if is_dataclass(value):
        return json_native(asdict(value))
    try:
        public = {
            key: item
            for key, item in vars(value).items()
            if not key.startswith("_") and type(item) is int
        }
    except TypeError:
        public = {}
    if public:
        return json_native(public)
    raise TypeError(f"value is not JSON serializable: {type(value).__name__}")


def bound_source_hashes() -> dict[str, str]:
    paths = {
        "generator_sha256": SCRIPT_PATH,
        "verifier_sha256": VERIFIER_PATH,
        "run_wrapper_sha256": RUN_WRAPPER_PATH,
        "exact_floor_sha256": EXACT_FLOOR_PATH,
        "polynomial_engine_sha256": POLYNOMIAL_PATH,
        "source_tag_predecessor_sha256": SOURCE_TAG_PATH,
        "compressed_join_predecessor_sha256": COMPRESSED_JOIN_PATH,
        "fixed_compiler_predecessor_sha256": FIXED_COMPILER_PATH,
        "coordinate_energy_predecessor_sha256": COORDINATE_ENERGY_PATH,
        "contract_sha256": CONTRACT_PATH,
        "hypothesis_sha256": HYPOTHESIS_PATH,
        "research_question_sha256": QUESTION_PATH,
        "theory_sha256": THEORY_PATH,
        "implementation_sha256": IMPLEMENTATION_PATH,
        "literature_sha256": LITERATURE_PATH,
        "pre_run_theory_v1_sha256": PRE_RUN_THEORY_V1_PATH,
        "pre_run_theory_v2_sha256": PRE_RUN_THEORY_V2_PATH,
        "pre_run_theory_v3_sha256": PRE_RUN_THEORY_V3_PATH,
        "pre_run_theory_v4_sha256": PRE_RUN_THEORY_V4_PATH,
        "pre_run_red_team_v1_sha256": PRE_RUN_RED_TEAM_V1_PATH,
        "pre_run_red_team_v2_sha256": PRE_RUN_RED_TEAM_V2_PATH,
        "pre_run_red_team_v3_sha256": PRE_RUN_RED_TEAM_V3_PATH,
    }
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"source-bound prerequisite is missing: {missing}")
    return {name: sha256_file(path) for name, path in paths.items()}


def exact_int(value: Any, label: str, minimum: int | None = None) -> int:
    if type(value) is not int:
        raise TypeError(f"{label} must be an exact integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"{label} must be at least {minimum}")
    return value


def exact_int_list(values: Iterable[int], label: str, minimum: int) -> list[int]:
    result = [
        exact_int(value, f"{label}[{index}]", minimum)
        for index, value in enumerate(values)
    ]
    if not result:
        raise ValueError(f"{label} must not be empty")
    if len(result) != len(set(result)):
        raise ValueError(f"{label} must not contain duplicates")
    return result


def exact_probability(value: Any, label: str) -> float:
    if type(value) not in {int, float}:
        raise TypeError(f"{label} must be numeric")
    result = float(value)
    if not 0.0 < result <= 1.0 or not math.isfinite(result):
        raise ValueError(f"{label} must lie in (0,1]")
    return result


def point_bytes(curve: Any) -> int:
    return math.ceil((2 + curve.p.bit_length()) / 8)


def factor_index_bytes(factor_count: int) -> int:
    return max(1, math.ceil(max(1, (factor_count - 1).bit_length()) / 8))


def point_to_json(point: Point) -> list[int] | None:
    return BASE.point_json(point)


def weighted_field_work(record: dict[str, int]) -> dict[str, int]:
    multiplications = record.get("field_multiplications", 0)
    inversions = record.get("field_inversions", 0)
    return {
        str(weight): multiplications + weight * inversions
        for weight in INVERSION_WEIGHTS
    }


def sum_operation_records(*records: dict[str, int]) -> dict[str, int]:
    keys = set().union(*(record.keys() for record in records))
    return {key: sum(record.get(key, 0) for record in records) for key in sorted(keys)}


def fit_log_slope(rows: list[tuple[int, float]]) -> float | None:
    if len(rows) < 3 or any(value <= 0 for _, value in rows):
        return None
    xs = [math.log(q) for q, _ in rows]
    ys = [math.log(value) for _, value in rows]
    x_mean = statistics.fmean(xs)
    y_mean = statistics.fmean(ys)
    denominator = sum((value - x_mean) ** 2 for value in xs)
    if denominator == 0:
        return None
    return sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / denominator


def target_cardinality_record(requested: int, available: int) -> dict[str, Any]:
    requested = exact_int(requested, "requested target cardinality", 1)
    available = exact_int(available, "available target cardinality", 0)
    realized = min(requested, available)
    exact = realized == requested
    return {
        "requested_count": requested,
        "available_count": available,
        "realized_count": realized,
        "count_was_clamped": not exact,
        "cardinality_status": "EXACT" if exact else "INSUFFICIENT_SUPPORT",
        "cardinality_gate": exact,
    }


def map_source_value(map_kind: str, t: int, params: dict[str, int], p: int) -> int:
    if map_kind == "identity":
        return t % p
    if map_kind == "square":
        return (t * t + params["c"]) % p
    if map_kind == "mobius":
        denominator = (t + params["e"]) % p
        if denominator == 0:
            raise AssertionError("accepted Mobius source has zero denominator")
        return (t + params["d"]) * pow(denominator, -1, p) % p
    raise ValueError(f"unsupported source map: {map_kind}")


def extract_source_branches(
    factor_base: dict[str, Any],
    curve: Any,
) -> list[dict[str, Any]]:
    family = factor_base["name"]
    if family not in TRANSLATOR_FAMILIES:
        raise ValueError(f"family has no eligible coordinate source map: {family}")
    grouped: dict[tuple[str, tuple[tuple[str, int], ...]], list[dict[str, int]]] = {}
    for ordinal, fiber in enumerate(factor_base["fibers"]):
        points = [BASE.point_from_json(value) for value in fiber["points"]]
        if len(points) != 2 or points[0] is None or curve.neg(points[0]) != points[1]:
            raise AssertionError("factor source is not one finite sign-complete fiber")
        source = dict(fiber["source"])
        x_value = points[0][0]
        if source.get("ordinal") != ordinal:
            raise AssertionError("factor source ordinal mismatch")
        if family in {"x_interval", "random_x"}:
            map_kind = "identity"
            params: dict[str, int] = {}
            parameter = x_value
        elif family == "square_map":
            map_kind = "square"
            params = {"c": exact_int(source["c"], "square c", 0) % curve.p}
            parameter = exact_int(source["t"], "square t", 0) % curve.p
        elif family == "rational_union":
            map_name = source.get("map")
            if map_name == "square":
                map_kind = "square"
                params = {"c": exact_int(source["c"], "union c", 0) % curve.p}
            elif map_name == "mobius":
                map_kind = "mobius"
                params = {
                    "d": exact_int(source["d"], "union d", 0) % curve.p,
                    "e": exact_int(source["e"], "union e", 0) % curve.p,
                }
            else:
                raise AssertionError("unknown rational-union branch")
            parameter = exact_int(source["t"], "union t", 0) % curve.p
        else:
            raise AssertionError("unreachable source family")
        if map_source_value(map_kind, parameter, params, curve.p) != x_value:
            raise AssertionError("public source map does not reproduce factor x")
        key = (map_kind, tuple(sorted(params.items())))
        grouped.setdefault(key, []).append(
            {"ordinal": ordinal, "t": parameter, "x": x_value}
        )

    branches: list[dict[str, Any]] = []
    all_x: set[int] = set()
    for branch_index, ((map_kind, param_items), records) in enumerate(
        sorted(grouped.items())
    ):
        records.sort(key=lambda row: (row["t"], row["ordinal"]))
        roots = [row["t"] for row in records]
        x_values = [row["x"] for row in records]
        if len(roots) != len(set(roots)):
            raise AssertionError("accepted source roots collide modulo p")
        if any(x in all_x for x in x_values):
            raise AssertionError("factor x-coordinate appears in multiple branches")
        all_x.update(x_values)
        branches.append(
            {
                "branch_index": branch_index,
                "map_kind": map_kind,
                "params": dict(param_items),
                "source_roots": roots,
                "x_values": x_values,
                "factor_ordinals": [row["ordinal"] for row in records],
            }
        )
    if len(all_x) * 2 != len(factor_base["points"]):
        raise AssertionError("source branches do not cover the factor base")
    return branches


def d2_x_orbits(d2: Any) -> dict[int, list[int]]:
    result: dict[int, list[int]] = {}
    for index, point in enumerate(d2.points):
        if point is not None:
            result.setdefault(point[0], []).append(index)
    for x_value, indices in result.items():
        if len(indices) != 2:
            raise AssertionError(f"D2 x-orbit {x_value} is not sign complete")
    return {key: result[key] for key in sorted(result)}


def serialize_d2(d2: Any, curve: Any, factor_count: int) -> dict[str, Any]:
    payload = {
        "points": [point_to_json(point) for point in d2.points],
        "witnesses": [list(witness) for witness in d2.witnesses],
    }
    key_bits = 2 + curve.p.bit_length()
    index_bits = max(1, (factor_count - 1).bit_length())
    logical_bits = len(d2.points) * (key_bits + 2 * index_bits)
    return {
        **payload,
        "point_count": len(d2.points),
        "x_orbit_count": len(d2_x_orbits(d2)),
        "multiplicities": list(d2.multiplicities),
        "attempts": d2.attempts,
        "build_ops": asdict(d2.build_ops),
        "logical_advice_bits": logical_bits,
        "canonical_payload_bytes": len(stable_json_bytes(payload)),
        "python_deep_bytes": BASE.deep_size(payload),
        "digest": stable_digest(payload),
    }


def serialize_factor_base(factor_base: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "name",
        "seed",
        "size",
        "symmetry_mode",
        "points",
        "fibers",
        "build_ops",
        "build_diagnostics",
        "charged_build_diagnostics",
        "scalar_source_metadata_emitted",
        "solver_input_fields",
        "digest",
    }
    record = {key: factor_base[key] for key in sorted(allowed)}
    for fiber in record["fibers"]:
        source = fiber["source"]
        forbidden = {"sampled_scalar", "canonical_scalar"}.intersection(source)
        if forbidden:
            raise AssertionError("factor-base record leaked constructor scalar metadata")
    return record


def serialize_d3(d3: Any, curve: Any, factor_count: int) -> dict[str, Any]:
    payload = {
        "points": [point_to_json(point) for point in d3.points],
        "witnesses": [list(witness) for witness in d3.witnesses],
    }
    key_bits = 2 + curve.p.bit_length()
    index_bits = max(1, (factor_count - 1).bit_length())
    logical_bits = len(d3.points) * (key_bits + 3 * index_bits)
    return {
        **payload,
        "point_count": len(d3.points),
        "multiplicities": list(d3.multiplicities),
        "attempts": d3.attempts,
        "build_ops": asdict(d3.build_ops),
        "logical_advice_bits": logical_bits,
        "canonical_payload_bytes": len(stable_json_bytes(payload)),
        "python_deep_bytes": BASE.deep_size(payload),
        "digest": stable_digest(payload),
    }


def build_symmetry_d3_codec(
    curve: Any,
    factor_points: list[Point],
    d3: Any,
) -> SymmetryD3Codec:
    point_to_index = {point: index for index, point in enumerate(d3.points)}
    entries: dict[int, tuple[int, int, int]] = {}
    artifact: list[dict[str, Any]] = []
    identity_witness: tuple[int, int, int] | None = None
    for index, point in enumerate(d3.points):
        witness = tuple(d3.witnesses[index])
        if point is None:
            identity_witness = witness
            continue
        negative = curve.neg(point)
        if negative not in point_to_index:
            raise AssertionError("D3 is not sign complete")
        canonical = min((point, negative), key=BASE.point_sort_key)
        if point != canonical or point[0] in entries:
            continue
        canonical_index = point_to_index[canonical]
        canonical_witness = tuple(d3.witnesses[canonical_index])
        negated_witness = tuple(sorted(index_value ^ 1 for index_value in canonical_witness))
        verified_canonical, _ = verify_factor_witness(
            curve, factor_points, canonical_witness, canonical
        )
        verified_negative, _ = verify_factor_witness(
            curve, factor_points, negated_witness, curve.neg(canonical)
        )
        if not verified_canonical or not verified_negative:
            raise AssertionError("orientation-bound D3 witness failed")
        entries[canonical[0]] = canonical_witness
        artifact.append(
            {
                "x": canonical[0],
                "canonical_witness": list(canonical_witness),
            }
        )
    if identity_witness is not None:
        verified, _ = verify_factor_witness(
            curve, factor_points, identity_witness, None
        )
        if not verified:
            raise AssertionError("D3 identity witness failed")
    artifact.sort(key=lambda row: row["x"])
    index_bits = max(1, (len(factor_points) - 1).bit_length())
    logical_bits = len(entries) * (curve.p.bit_length() + 3 * index_bits)
    if identity_witness is not None:
        logical_bits += 1 + 3 * index_bits
    payload = {
        "entries": artifact,
        "identity_witness": (
            list(identity_witness) if identity_witness is not None else None
        ),
    }
    record = {
        "kind": "symmetry_compressed_d3_x_orbits",
        "x_orbit_count": len(entries),
        "full_point_count": len(d3.points),
        "identity_present": identity_witness is not None,
        "point_x_bits": curve.p.bit_length(),
        "factor_index_bits": index_bits,
        "logical_advice_bits": logical_bits,
        "canonical_payload_bytes": len(stable_json_bytes(payload)),
        "python_deep_bytes": BASE.deep_size(payload),
        "digest": stable_digest(payload),
        "first_entries": artifact[: min(8, len(artifact))],
        "orientation_rule": (
            "canonical point is minimum affine (x,y); negative witness is "
            "derived by adjacent factor-index xor 1"
        ),
    }
    return SymmetryD3Codec(entries, identity_witness, record)


def query_symmetry_d3(
    curve: Any,
    target: Point,
    factor_points: list[Point],
    d2: Any,
    codec: SymmetryD3Codec,
) -> dict[str, Any]:
    ops = Ops()
    probes = 0
    d2_point_reads = 0
    witness_reads = 0
    witness: list[int] | None = None
    d2_index: int | None = None
    for index, partial in enumerate(d2.points):
        d2_point_reads += 1
        probes += 1
        complement = curve.add(target, curve.neg(partial), ops)
        if complement is None:
            d3_witness = codec.identity_witness
        else:
            canonical_witness = codec.entries.get(complement[0])
            if canonical_witness is None:
                d3_witness = None
            else:
                canonical = (
                    complement[0],
                    min(complement[1], (-complement[1]) % curve.p),
                )
                if complement == canonical:
                    d3_witness = canonical_witness
                elif complement == curve.neg(canonical):
                    d3_witness = tuple(
                        sorted(value ^ 1 for value in canonical_witness)
                    )
                else:
                    raise AssertionError("D3 x key returned an inconsistent point")
        if d3_witness is None:
            continue
        witness_reads = 2
        witness = list(d2.witnesses[index]) + list(d3_witness)
        verified, verification_ops = verify_factor_witness(
            curve, factor_points, witness, target
        )
        if not verified:
            raise AssertionError("symmetry-compressed D3 query witness failed")
        d2_index = index
        break
    if witness is None:
        verification_ops = asdict(Ops())
    key_bytes = math.ceil(curve.p.bit_length() / 8)
    compressed_point_bytes = point_bytes(curve)
    index_bytes = factor_index_bytes(len(factor_points))
    operation_record = asdict(ops)
    return {
        "success": witness is not None,
        "witness": witness,
        "d2_index": d2_index,
        "dictionary_probes": probes,
        "d2_point_reads": d2_point_reads,
        "witness_reads": witness_reads,
        "logical_bytes_read": (
            d2_point_reads * compressed_point_bytes
            + probes * key_bytes
            + (5 * index_bytes if witness is not None else 0)
        ),
        "operation_record": operation_record,
        "weighted_field_work": weighted_field_work(operation_record),
        "witness_verification_audit_ops": verification_ops,
    }


def verify_factor_witness(
    curve: Any,
    factor_points: list[Point],
    witness: list[int] | tuple[int, ...],
    target: Point,
) -> tuple[bool, dict[str, int]]:
    ops = Ops()
    recovered: Point = None
    for index in witness:
        if not 0 <= index < len(factor_points):
            return False, asdict(ops)
        recovered = curve.add(recovered, factor_points[index], ops)
    return recovered == target, asdict(ops)


def brute_s3_compatibility(
    curve: Any,
    target: Point,
    d2: Any,
) -> dict[str, Any]:
    ops = Ops()
    roots: dict[int, tuple[int, int]] = {}
    identity_pair: tuple[int, int] | None = None
    probes = 0
    for left, left_point in enumerate(d2.points):
        probes += 1
        complement = curve.add(target, curve.neg(left_point), ops)
        right = d2.point_to_index.get(complement)
        if right is None:
            continue
        if left_point is None:
            identity_pair = (left, right)
        else:
            roots.setdefault(left_point[0], (left, right))
    return {
        "roots": sorted(roots),
        "root_pairs": {str(root): list(pair) for root, pair in sorted(roots.items())},
        "identity_pair": list(identity_pair) if identity_pair is not None else None,
        "ops": asdict(ops),
        "point_probes": probes,
    }


def s3_identity_target_control(
    curve: Any,
    factor_points: list[Point],
    d2: Any,
) -> dict[str, Any]:
    orbit_indices = d2_x_orbits(d2)
    recovery_rows: list[dict[str, Any]] = []
    verification_ops = Ops()
    for root, indices in orbit_indices.items():
        left = indices[0]
        right = d2.point_to_index.get(curve.neg(d2.points[left]))
        if right is None:
            raise AssertionError("identity-target S3 control lost a negative D2 point")
        witness = list(d2.witnesses[left]) + list(d2.witnesses[right])
        recovered: Point = None
        for factor_index in witness:
            recovered = curve.add(
                recovered,
                factor_points[factor_index],
                verification_ops,
            )
        if recovered is not None:
            raise AssertionError("identity-target finite S3 witness is invalid")
        recovery_rows.append(
            {
                "root": root,
                "route": [left, right],
                "witness": witness,
            }
        )

    identity_index = d2.point_to_index.get(None)
    identity_row: dict[str, Any] | None = None
    if identity_index is not None:
        witness = list(d2.witnesses[identity_index]) * 2
        recovered = None
        for factor_index in witness:
            recovered = curve.add(
                recovered,
                factor_points[factor_index],
                verification_ops,
            )
        if recovered is not None:
            raise AssertionError("identity-target S3 sentinel witness is invalid")
        identity_row = {
            "route": [identity_index, identity_index],
            "witness": witness,
        }

    roots = sorted(orbit_indices)
    return {
        "target": None,
        "mode": "explicit_identity_target_branch",
        "polynomial_input_defined": False,
        "root_product_remainder_mod_m2": [0],
        "polynomial_roots_by_identity_branch": roots,
        "independent_expected_roots": roots,
        "identity_sentinel": identity_row,
        "recovered_finite_roots": recovery_rows,
        "verification_ops": asdict(verification_ops),
        "functional_gate": (
            len(recovery_rows) == len(roots) and identity_row is not None
        ),
        "boundary": (
            "x(Q) is undefined for Q=O; every finite D2 orbit is compatible "
            "through A+(-A), and O+O is recorded as a separate sentinel"
        ),
    }


def brute_s4_compatibility(
    curve: Any,
    target: Point,
    factor_points: list[Point],
    d2: Any,
) -> dict[str, Any]:
    ops = Ops()
    roots: dict[int, tuple[int, int, int]] = {}
    identity_route: tuple[int, int, int] | None = None
    probes = 0
    for left, left_point in enumerate(d2.points):
        for factor_index, factor_point in enumerate(factor_points):
            probes += 1
            partial = curve.add(target, curve.neg(left_point), ops)
            complement = curve.add(partial, curve.neg(factor_point), ops)
            right = d2.point_to_index.get(complement)
            if right is None:
                continue
            route = (left, factor_index, right)
            if left_point is None:
                identity_route = identity_route or route
            else:
                roots.setdefault(left_point[0], route)
    return {
        "roots": sorted(roots),
        "root_routes": {
            str(root): list(route) for root, route in sorted(roots.items())
        },
        "identity_route": list(identity_route) if identity_route is not None else None,
        "ops": asdict(ops),
        "point_probes": probes,
    }


def recover_s4_roots(
    curve: Any,
    target: Point,
    factor_points: list[Point],
    d2: Any,
    roots: list[int],
    stop_after_first: bool,
) -> dict[str, Any]:
    orbit_indices = d2_x_orbits(d2)
    ops = Ops()
    probes = 0
    point_reads = 0
    witness_reads = 0
    recovered_rows: list[dict[str, Any]] = []
    for root in roots:
        route: tuple[int, int, int] | None = None
        for left in orbit_indices.get(root, []):
            left_point = d2.points[left]
            point_reads += 1
            partial = curve.add(target, curve.neg(left_point), ops)
            for factor_index, factor_point in enumerate(factor_points):
                probes += 1
                point_reads += 1
                complement = curve.add(partial, curve.neg(factor_point), ops)
                right = d2.point_to_index.get(complement)
                if right is not None:
                    route = (left, factor_index, right)
                    break
            if route is not None:
                break
        if route is None:
            recovered_rows.append({"root": root, "route": None, "witness": None})
            continue
        left, factor_index, right = route
        witness_reads += 2
        witness = list(d2.witnesses[left]) + [factor_index] + list(d2.witnesses[right])
        verified, verification_ops = verify_factor_witness(
            curve, factor_points, witness, target
        )
        if not verified:
            raise AssertionError("S4 root recovery returned an invalid witness")
        recovered_rows.append(
            {
                "root": root,
                "route": list(route),
                "witness": witness,
                "verification_ops": verification_ops,
            }
        )
        if stop_after_first:
            break

    has_finite_witness = any(
        row["witness"] is not None for row in recovered_rows
    )
    identity_index = d2.point_to_index.get(None)
    identity_row: dict[str, Any] | None = None
    if identity_index is not None and (not stop_after_first or not has_finite_witness):
        for factor_index, factor_point in enumerate(factor_points):
            probes += 1
            point_reads += 1
            complement = curve.add(target, curve.neg(factor_point), ops)
            right = d2.point_to_index.get(complement)
            if right is None:
                continue
            witness_reads += 2
            witness = (
                list(d2.witnesses[identity_index])
                + [factor_index]
                + list(d2.witnesses[right])
            )
            verified, verification_ops = verify_factor_witness(
                curve, factor_points, witness, target
            )
            if not verified:
                raise AssertionError("identity route returned an invalid witness")
            identity_row = {
                "route": [identity_index, factor_index, right],
                "witness": witness,
                "verification_ops": verification_ops,
            }
            break

    successful = [row for row in recovered_rows if row["witness"] is not None]
    if identity_row is not None:
        successful.append(identity_row)
    compressed_point_bytes = point_bytes(curve)
    index_bytes = factor_index_bytes(len(factor_points))
    successful_witnesses = len(successful)
    return {
        "success": bool(successful),
        "recovered_roots": recovered_rows,
        "identity": identity_row,
        "ops": asdict(ops),
        "point_probes": probes,
        "point_reads": point_reads,
        "witness_reads": witness_reads,
        "factor_index_reads": 5 * successful_witnesses,
        "logical_bytes_read": (
            point_reads * compressed_point_bytes
            + 5 * successful_witnesses * index_bytes
        ),
        "all_requested_roots_recovered": all(
            row["witness"] is not None for row in recovered_rows
        ),
    }


def polynomial_summary(polynomial: Any, include_terms: bool = False) -> dict[str, Any]:
    record = polynomial.to_record()
    terms = record.pop("terms")
    summary = {
        **record,
        "term_count": polynomial.term_count(),
        "degrees": list(polynomial.degrees()),
        "dense_coefficient_count": polynomial.dense_coefficient_count(),
        "density": polynomial.density(),
        "canonical_terms_bytes": len(stable_json_bytes(terms)),
        "python_deep_bytes": BASE.deep_size(terms),
        "terms_digest": stable_digest(terms),
        "first_terms": terms[: min(8, len(terms))],
    }
    if include_terms:
        summary["terms"] = terms
    return summary


def polynomial_counter_field_vector(record: dict[str, Any]) -> dict[str, int]:
    return {
        "field_additions": exact_int(
            record["coefficient_additions"], "coefficient_additions", 0
        ),
        "field_multiplications": exact_int(
            record["coefficient_multiplications"],
            "coefficient_multiplications",
            0,
        ),
        "field_inversions": exact_int(
            record["coefficient_inversions"], "coefficient_inversions", 0
        ),
        "field_zero_tests": exact_int(
            record["coefficient_zero_tests"], "coefficient_zero_tests", 0
        ),
    }


def build_translator_preprocessing(
    polynomial: Any,
    curve: Any,
    factor_base: dict[str, Any],
    d2: Any,
    d2_record: dict[str, Any],
    d3_record: dict[str, Any],
    symmetry_d3_record: dict[str, Any],
) -> dict[str, Any]:
    counter = polynomial.OperationCounter()
    start = time.perf_counter()
    branches = extract_source_branches(factor_base, curve)
    roots = list(d2_x_orbits(d2))
    m2 = polynomial.build_m2(roots, curve.p, counter)
    branch_records: list[dict[str, Any]] = []
    for branch in branches:
        source_polynomial = polynomial.univariate_product_from_roots(
            branch["source_roots"], curve.p, counter
        )
        branch_records.append(
            {
                **branch,
                "source_polynomial": list(source_polynomial),
                "source_polynomial_degree": len(source_polynomial) - 1,
                "source_polynomial_nonzero_coefficients": sum(
                    coefficient % curve.p != 0 for coefficient in source_polynomial
                ),
            }
        )
    wall_seconds = time.perf_counter() - start
    coefficient_bits = curve.p.bit_length()
    map_parameter_count = sum(len(branch["params"]) for branch in branches)
    source_root_count = sum(len(branch["source_roots"]) for branch in branches)
    source_coefficient_count = sum(
        len(branch["source_polynomial"]) for branch in branch_records
    )
    incremental_coefficients = (
        len(roots)
        + len(m2)
        + source_root_count
        + map_parameter_count
    )
    incremental_bits = incremental_coefficients * coefficient_bits
    executable_branches = [
        {
            "branch_index": branch["branch_index"],
            "map_kind": branch["map_kind"],
            "params": branch["params"],
            "source_roots": branch["source_roots"],
        }
        for branch in branch_records
    ]
    executable_payload = {
        "d2_x_roots": roots,
        "m2": list(m2),
        "branches": executable_branches,
    }
    diagnostic_payload = {
        "source_polynomials": [
            branch["source_polynomial"] for branch in branch_records
        ],
        "x_values": [branch["x_values"] for branch in branch_records],
        "factor_ordinals": [
            branch["factor_ordinals"] for branch in branch_records
        ],
    }
    return {
        "d2_x_roots": roots,
        "m2": list(m2),
        "branches": branch_records,
        "operations": counter.to_record(),
        "wall_seconds": wall_seconds,
        "coefficient_bits": coefficient_bits,
        "incremental_coefficient_count": incremental_coefficients,
        "incremental_logical_bits": incremental_bits,
        "executable_source_root_count": source_root_count,
        "diagnostic_source_polynomial_coefficient_count": source_coefficient_count,
        "diagnostic_source_polynomial_logical_bits": (
            source_coefficient_count * coefficient_bits
        ),
        "source_extraction_traffic": {
            "factor_fiber_reads": len(factor_base["fibers"]),
            "source_scalar_reads": source_root_count + map_parameter_count,
            "source_root_writes": source_root_count,
            "d2_root_reads": len(roots),
            "boundary": "integer/list traffic; no field-operation claim",
        },
        "total_logical_bits_including_d2": (
            d2_record["logical_advice_bits"] + incremental_bits
        ),
        "full_signed_d3_total_logical_bits": (
            d2_record["logical_advice_bits"] + d3_record["logical_advice_bits"]
        ),
        "symmetry_d3_total_logical_bits": (
            d2_record["logical_advice_bits"]
            + symmetry_d3_record["logical_advice_bits"]
        ),
        "advice_ratio_to_symmetry_d3": (
            (d2_record["logical_advice_bits"] + incremental_bits)
            / (
                d2_record["logical_advice_bits"]
                + symmetry_d3_record["logical_advice_bits"]
            )
        ),
        "canonical_payload_bytes": len(stable_json_bytes(executable_payload)),
        "python_deep_bytes": BASE.deep_size(executable_payload),
        "digest": stable_digest(executable_payload),
        "diagnostic_payload_canonical_bytes": len(
            stable_json_bytes(diagnostic_payload)
        ),
        "diagnostic_payload_python_bytes": BASE.deep_size(diagnostic_payload),
        "diagnostic_payload_digest": stable_digest(diagnostic_payload),
        "boundary": (
            "executable advice is D2 roots, M2, accepted source roots, and public "
            "map parameters; source polynomials/x-values/ordinals are segregated "
            "diagnostics; explicit-root rational_union is not compositional L"
        ),
    }


def scalar_f3_coefficients_in_z(
    polynomial: Any,
    p: int,
    a: int,
    b: int,
    x1: int,
    x2: int,
    counter: Any,
) -> tuple[int, int, int]:
    difference = polynomial.fp_subtract(x1, x2, p, counter)
    leading = polynomial.fp_multiply(difference, difference, p, counter)
    x_sum = polynomial.fp_add(x1, x2, p, counter)
    x_product = polynomial.fp_multiply(x1, x2, p, counter)
    product_plus_a = polynomial.fp_add(x_product, a, p, counter)
    middle_inner = polynomial.fp_multiply(x_sum, product_plus_a, p, counter)
    two_b = polynomial.fp_multiply(2, b, p, counter)
    middle_inner = polynomial.fp_add(middle_inner, two_b, p, counter)
    middle = polynomial.fp_multiply(-2, middle_inner, p, counter)
    product_minus_a = polynomial.fp_subtract(x_product, a, p, counter)
    constant = polynomial.fp_multiply(
        product_minus_a,
        product_minus_a,
        p,
        counter,
    )
    four_b = polynomial.fp_multiply(4, b, p, counter)
    tail = polynomial.fp_multiply(four_b, x_sum, p, counter)
    constant = polynomial.fp_subtract(constant, tail, p, counter)
    return leading, middle, constant


def scalar_quadratic_resultant(
    polynomial: Any,
    p: int,
    left: tuple[int, int, int],
    right: tuple[int, int, int],
    counter: Any,
) -> int:
    a2, a1, a0 = left
    b2, b1, b0 = right
    first = polynomial.fp_subtract(
        polynomial.fp_multiply(a2, b0, p, counter),
        polynomial.fp_multiply(a0, b2, p, counter),
        p,
        counter,
    )
    second = polynomial.fp_subtract(
        polynomial.fp_multiply(a2, b1, p, counter),
        polynomial.fp_multiply(a1, b2, p, counter),
        p,
        counter,
    )
    third = polynomial.fp_subtract(
        polynomial.fp_multiply(a1, b0, p, counter),
        polynomial.fp_multiply(a0, b1, p, counter),
        p,
        counter,
    )
    return polynomial.fp_subtract(
        polynomial.fp_multiply(first, first, p, counter),
        polynomial.fp_multiply(second, third, p, counter),
        p,
        counter,
    )


def direct_scalar_f4_tuple_roots(
    polynomial: Any,
    p: int,
    a: int,
    b: int,
    target_x: int,
    factor_x_roots: list[int],
    d2_x_roots: list[int],
    stop_after_first: bool,
) -> dict[str, Any]:
    counter = polynomial.OperationCounter()
    roots: set[int] = set()
    left_cache: dict[tuple[int, int], tuple[int, int, int]] = {}
    right_cache: dict[int, tuple[int, int, int]] = {}
    tuple_tests = 0
    start = time.perf_counter()
    for factor_x in factor_x_roots:
        for d2_x in d2_x_roots:
            for right_x in d2_x_roots:
                tuple_tests += 1
                left_key = (factor_x, d2_x)
                left = left_cache.get(left_key)
                if left is None:
                    left = scalar_f3_coefficients_in_z(
                        polynomial,
                        p,
                        a,
                        b,
                        factor_x,
                        d2_x,
                        counter,
                    )
                    left_cache[left_key] = left
                right = right_cache.get(right_x)
                if right is None:
                    right = scalar_f3_coefficients_in_z(
                        polynomial,
                        p,
                        a,
                        b,
                        right_x,
                        target_x,
                        counter,
                    )
                    right_cache[right_x] = right
                value = scalar_quadratic_resultant(
                    polynomial,
                    p,
                    left,
                    right,
                    counter,
                )
                if polynomial.fp_is_zero(value, p, counter):
                    roots.add(d2_x)
                    if stop_after_first:
                        return {
                            "roots": sorted(roots),
                            "tuple_tests": tuple_tests,
                            "left_cache_entries": len(left_cache),
                            "right_cache_entries": len(right_cache),
                            "cache_hits": (
                                2 * tuple_tests - len(left_cache) - len(right_cache)
                            ),
                            "operations": counter.to_record(),
                            "wall_seconds": time.perf_counter() - start,
                            "mode": (
                                "cached_direct_scalar_quadratic_resultant_per_tuple"
                            ),
                        }
    return {
        "roots": sorted(roots),
        "tuple_tests": tuple_tests,
        "left_cache_entries": len(left_cache),
        "right_cache_entries": len(right_cache),
        "cache_hits": 2 * tuple_tests - len(left_cache) - len(right_cache),
        "operations": counter.to_record(),
        "wall_seconds": time.perf_counter() - start,
        "mode": "cached_direct_scalar_quadratic_resultant_per_tuple",
    }


def direct_f4_tuple_roots(
    polynomial: Any,
    f4_fixed: Any,
    factor_x_roots: list[int],
    d2_x_roots: list[int],
    stop_after_first: bool,
) -> dict[str, Any]:
    counter = polynomial.OperationCounter()
    roots: set[int] = set()
    tuple_tests = 0
    coefficient_writes = 0
    start = time.perf_counter()
    for factor_x in factor_x_roots:
        f4_factor = f4_fixed.evaluate_one_variable(0, factor_x, counter)
        for d2_x in d2_x_roots:
            f4_pair = f4_factor.evaluate_one_variable(0, d2_x, counter)
            for right_x in d2_x_roots:
                tuple_tests += 1
                value = f4_pair.evaluate_one_variable(0, right_x, counter)
                coefficient_writes += 1
                if value.is_zero():
                    roots.add(d2_x)
                    if stop_after_first:
                        return {
                            "roots": sorted(roots),
                            "tuple_tests": tuple_tests,
                            "coefficient_writes": coefficient_writes,
                            "operations": counter.to_record(),
                            "wall_seconds": time.perf_counter() - start,
                            "mode": "sparse_symbolic_f4_evaluation",
                        }
    return {
        "roots": sorted(roots),
        "tuple_tests": tuple_tests,
        "coefficient_writes": coefficient_writes,
        "operations": counter.to_record(),
        "wall_seconds": time.perf_counter() - start,
        "mode": "sparse_symbolic_f4_evaluation",
    }


def run_translator_target(
    polynomial: Any,
    curve: Any,
    factor_points: list[Point],
    d2: Any,
    preprocessing: dict[str, Any],
    target: Point,
) -> dict[str, Any]:
    if target is None:
        raise ValueError("coordinate translator requires a nonidentity target")
    p = curve.p
    d2_roots = list(preprocessing["d2_x_roots"])
    m2 = tuple(preprocessing["m2"])
    factor_x_roots = sorted({point[0] for point in factor_points if point is not None})

    s3_counter = polynomial.OperationCounter()
    s3_start = time.perf_counter()
    s3_relation = polynomial.build_f3_fixed_x(
        p, curve.a, curve.b, target[0], s3_counter
    )
    s3_remainder = polynomial.s3_identity_corrected_root_product_mod_m2(
        s3_relation,
        target[0],
        d2_roots,
        m2=m2,
        counter=s3_counter,
    )
    s3_gcd, s3_roots = polynomial.gcd_roots_against_m2(
        s3_remainder, m2, d2_roots, p, s3_counter
    )
    s3_wall = time.perf_counter() - s3_start
    brute_s3 = brute_s3_compatibility(curve, target, d2)
    if list(s3_roots) != brute_s3["roots"]:
        raise AssertionError("S3 positive-control roots differ from brute routes")

    candidate_counter = polynomial.OperationCounter()
    candidate_start = time.perf_counter()
    f4_fixed = polynomial.build_f4_fixed_x(
        p, curve.a, curve.b, target[0], candidate_counter
    )
    candidate_workspace_coefficient_upper_bound = (
        f4_fixed.dense_coefficient_count()
    )
    branch_rows: list[dict[str, Any]] = []
    combined = polynomial.SparsePolynomial.constant(p, 2, 1)
    equivalence_counter = polynomial.OperationCounter()
    for branch in preprocessing["branches"]:
        params = branch["params"]
        source_template = polynomial.substitute_source_map(
            f4_fixed,
            branch["map_kind"],
            c=params.get("c", 0),
            d=params.get("d", 0),
            e=params.get("e", 0),
            counter=candidate_counter,
        )
        source_product = polynomial.source_root_elimination(
            source_template,
            branch["source_roots"],
            candidate_counter,
        )
        previous_combined_dense = combined.dense_coefficient_count()
        combined = combined.multiply(source_product, candidate_counter)
        candidate_workspace_coefficient_upper_bound = max(
            candidate_workspace_coefficient_upper_bound,
            f4_fixed.dense_coefficient_count()
            + previous_combined_dense
            + source_template.dense_coefficient_count()
            + 3 * source_product.dense_coefficient_count()
            + combined.dense_coefficient_count(),
        )

        direct_product = polynomial.direct_factor_root_product(
            f4_fixed, branch["x_values"], equivalence_counter
        )
        denominator_scalar = polynomial.source_denominator_scalar(
            p,
            branch["map_kind"],
            branch["source_roots"],
            c=params.get("c", 0),
            d=params.get("d", 0),
            e=params.get("e", 0),
            counter=equivalence_counter,
        )
        scaled_direct = direct_product.scale(
            denominator_scalar, equivalence_counter
        )
        equivalent = source_product.sorted_terms() == scaled_direct.sorted_terms()
        if not equivalent:
            raise AssertionError("source elimination differs from direct factor product")
        branch_rows.append(
            {
                "branch_index": branch["branch_index"],
                "map_kind": branch["map_kind"],
                "params": params,
                "source_root_count": len(branch["source_roots"]),
                "denominator_scalar": denominator_scalar,
                "source_template": polynomial_summary(source_template),
                "source_product": polynomial_summary(source_product),
                "combined_after": polynomial_summary(combined),
                "direct_product": polynomial_summary(direct_product),
                "equivalent_up_to_expected_scalar": equivalent,
            }
        )

    root_remainder = polynomial.s4_root_product_mod_m2(
        combined, d2_roots, m2=m2, counter=candidate_counter
    )
    reduced_degree_bound = max(1, len(m2) - 1)
    combined_v_degree = max(0, combined.degree(0))
    candidate_workspace_coefficient_upper_bound = max(
        candidate_workspace_coefficient_upper_bound,
        f4_fixed.dense_coefficient_count()
        + combined.dense_coefficient_count()
        + len(m2)
        + 3 * reduced_degree_bound
        + 2 * (combined_v_degree + 1),
    )
    common, polynomial_roots = polynomial.gcd_roots_against_m2(
        root_remainder,
        m2,
        d2_roots,
        p,
        candidate_counter,
    )
    candidate_wall = time.perf_counter() - candidate_start
    brute_s4 = brute_s4_compatibility(curve, target, factor_points, d2)
    if list(polynomial_roots) != brute_s4["roots"]:
        raise AssertionError("S4 polynomial roots differ from brute point routes")
    solver_recovery = recover_s4_roots(
        curve,
        target,
        factor_points,
        d2,
        list(polynomial_roots),
        stop_after_first=True,
    )
    all_root_recovery_audit = recover_s4_roots(
        curve,
        target,
        factor_points,
        d2,
        list(polynomial_roots),
        stop_after_first=False,
    )
    if not all_root_recovery_audit["all_requested_roots_recovered"]:
        raise AssertionError("not every S4 root recovered an exact witness")
    if bool(all_root_recovery_audit["identity"]) != bool(
        brute_s4["identity_route"]
    ):
        raise AssertionError("S4 identity-route audit differs from brute point routes")

    symbolic_first_tuple = direct_f4_tuple_roots(
        polynomial,
        f4_fixed,
        factor_x_roots,
        d2_roots,
        True,
    )
    symbolic_full_tuples = direct_f4_tuple_roots(
        polynomial,
        f4_fixed,
        factor_x_roots,
        d2_roots,
        False,
    )
    direct_first_tuple = direct_scalar_f4_tuple_roots(
        polynomial,
        p,
        curve.a,
        curve.b,
        target[0],
        factor_x_roots,
        d2_roots,
        True,
    )
    direct_full_tuples = direct_scalar_f4_tuple_roots(
        polynomial,
        p,
        curve.a,
        curve.b,
        target[0],
        factor_x_roots,
        d2_roots,
        False,
    )
    if (
        symbolic_full_tuples["roots"] != brute_s4["roots"]
        or direct_full_tuples["roots"] != brute_s4["roots"]
    ):
        raise AssertionError("direct/symbolic f4 roots differ from brute point routes")

    candidate_poly_vector = polynomial_counter_field_vector(
        candidate_counter.to_record()
    )
    candidate_poly_record = candidate_counter.to_record()
    candidate_total_vector = sum_operation_records(
        candidate_poly_vector,
        solver_recovery["ops"],
    )
    factor_count = len(factor_x_roots)
    d2_root_count = len(d2_roots)
    coefficient_bytes = math.ceil(p.bit_length() / 8)
    coefficient_reads_lower_bound = (
        2
        * (
            candidate_poly_record["coefficient_additions"]
            + candidate_poly_record["coefficient_multiplications"]
        )
        + candidate_poly_record["coefficient_zero_tests"]
        + candidate_poly_record["coefficient_inversions"]
    )
    coefficient_writes_lower_bound = (
        candidate_poly_record["coefficient_additions"]
        + candidate_poly_record["coefficient_multiplications"]
        + candidate_poly_record["coefficient_inversions"]
    )
    explicit_root_scalar_reads = (
        factor_count + 2 * d2_root_count + len(polynomial_roots)
    )
    logical_memory_traffic_lower_bound_bytes = (
        coefficient_reads_lower_bound
        + coefficient_writes_lower_bound
        + explicit_root_scalar_reads
    ) * coefficient_bytes + solver_recovery["logical_bytes_read"]
    live_records = [
        polynomial_summary(f4_fixed),
        polynomial_summary(combined),
    ]
    workspace_canonical_bytes = max(
        [len(stable_json_bytes(record)) for record in live_records]
        + [len(stable_json_bytes(root_remainder)), len(stable_json_bytes(common))]
    )
    retained_workspace_logical_bytes = max(
        [record["term_count"] * coefficient_bytes for record in live_records]
        + [
            len(root_remainder) * coefficient_bytes,
            len(common) * coefficient_bytes,
        ]
    )
    retained_workspace_python_bytes = max(
        [record["python_deep_bytes"] for record in live_records]
        + [BASE.deep_size(root_remainder), BASE.deep_size(common)]
    )
    workspace_logical_upper_bound_bytes = (
        candidate_workspace_coefficient_upper_bound * coefficient_bytes
        + len(polynomial_roots) * coefficient_bytes
    )
    target_symbolic_degree_bound = 4 * factor_count * d2_root_count
    target_symbolic_dense_coefficient_bound = (
        d2_root_count * (target_symbolic_degree_bound + 1)
    )
    return {
        "target": point_to_json(target),
        "s3": {
            "relation": polynomial_summary(s3_relation),
            "root_product_remainder": list(s3_remainder),
            "gcd": list(s3_gcd),
            "operations": s3_counter.to_record(),
            "wall_seconds": s3_wall,
        },
        "polynomial_s3_roots": list(s3_roots),
        "brute_s3": brute_s3,
        "f4": polynomial_summary(f4_fixed),
        "branches": branch_rows,
        "combined_g": polynomial_summary(combined),
        "root_product_remainder": list(root_remainder),
        "root_product_remainder_degree": len(root_remainder) - 1,
        "root_product_remainder_nonzero_coefficients": sum(
            coefficient % p != 0 for coefficient in root_remainder
        ),
        "gcd": list(common),
        "polynomial_s4_roots": list(polynomial_roots),
        "brute_s4": brute_s4,
        "solver_recovery": solver_recovery,
        "all_root_recovery_audit": all_root_recovery_audit,
        "candidate_polynomial_operations": candidate_poly_record,
        "candidate_equivalence_audit_operations": equivalence_counter.to_record(),
        "candidate_total_field_vector": candidate_total_vector,
        "candidate_weighted_field_work": weighted_field_work(candidate_total_vector),
        "candidate_memory_traffic_lower_bound": {
            "coefficient_reads": coefficient_reads_lower_bound,
            "coefficient_writes": coefficient_writes_lower_bound,
            "explicit_source_and_d2_root_scalar_reads": explicit_root_scalar_reads,
            "witness_recovery_logical_bytes": solver_recovery[
                "logical_bytes_read"
            ],
            "logical_bytes": logical_memory_traffic_lower_bound_bytes,
            "boundary": (
                "operation-derived logical lower bound; excludes interpreter, "
                "dictionary, cache-line, allocator, and audit-only traffic"
            ),
        },
        "candidate_wall_seconds": candidate_wall,
        "direct_scalar_f4_first_root": direct_first_tuple,
        "direct_scalar_f4_full_root_set": direct_full_tuples,
        "symbolic_sparse_f4_first_root": symbolic_first_tuple,
        "symbolic_sparse_f4_full_root_set": symbolic_full_tuples,
        "h_representation": "explicit dense coefficient tuple after modular reduction",
        "h_coefficient_writes": len(root_remainder),
        "peak_target_workspace_logical_bytes": workspace_logical_upper_bound_bytes,
        "peak_target_workspace_coefficient_upper_bound": (
            candidate_workspace_coefficient_upper_bound
        ),
        "retained_object_workspace_logical_bytes": (
            retained_workspace_logical_bytes
        ),
        "peak_target_workspace_canonical_bytes": workspace_canonical_bytes,
        "peak_target_workspace_python_bytes": retained_workspace_python_bytes,
        "workspace_bound_model": (
            "conservative live dense-coefficient slots for f4, source template, "
            "source product, combined product, M2, root-product multiply/reduce, "
            "and extracted roots; canonical/Python fields are retained-object "
            "snapshots and are diagnostic rather than measured RSS peaks"
        ),
        "target_symbolic_degree_bound": target_symbolic_degree_bound,
        "target_symbolic_dense_coefficient_bound": (
            target_symbolic_dense_coefficient_bound
        ),
        "target_symbolic_dense_bytes_bound": (
            target_symbolic_dense_coefficient_bound * coefficient_bytes
        ),
        "boundary": (
            "exact specialized root-product census; brute sets and direct-product "
            "equivalence are audit/comparator costs, not candidate advice"
        ),
    }


def make_exact_d2_fallback(
    curve: Any,
    factor_points: list[Point],
    d2: Any,
) -> Callable[[Point], dict[str, Any]]:
    def fallback(target: Point) -> dict[str, Any]:
        result = SOURCE.query_d2_complement_d5(
            curve, target, factor_points, d2
        )
        operations = dict(result["ops"])
        counters = {
            "group_operations": operations.get("group_operations", 0),
            "point_additions": operations.get("point_additions", 0),
            "point_doublings": operations.get("point_doublings", 0),
            "field_multiplications": operations.get("field_multiplications", 0),
            "field_inversions": operations.get("field_inversions", 0),
            "complement_tests": result["route_probes"],
            "dictionary_probes": result["route_probes"],
            "d2_point_reads": max(
                0, result["point_reads"] - result["outer_factor_point_reads"]
            ),
            "d3_key_reads": 0,
            "d2_witness_reads": result["witness_reads"],
            "d3_witness_reads": 0,
            "target_point_reads": result["outer_factor_point_reads"],
            "logical_d2_point_bytes_read": max(
                0,
                result["logical_point_bytes_read"]
                - result["outer_factor_logical_bytes_read"],
            ),
            "logical_d3_key_bytes_read": 0,
            "logical_d2_witness_bytes_read": result[
                "logical_witness_bytes_read"
            ],
            "logical_d3_witness_bytes_read": 0,
            "logical_target_point_bytes_read": result[
                "outer_factor_logical_bytes_read"
            ],
            "logical_total_bytes_read": (
                result["logical_point_bytes_read"]
                + result["logical_witness_bytes_read"]
            ),
        }
        return {
            "kind": "complete_exact_d2_outer_scan",
            "success": result["success"],
            "witness": result["witness"],
            "counters": counters,
            "operation_record": operations,
            "weighted_field_work": weighted_field_work(operations),
            "source_record": result,
        }

    return fallback


def batch_comparison_record(
    target_major: dict[str, Any],
    d2_major: dict[str, Any],
    field_bytes: int,
    cardinality_complete: bool,
) -> dict[str, Any]:
    target_counters = target_major["counters"]
    batch_counters = d2_major["counters"]

    def ratio_value(numerator: int | float, denominator: int | float) -> float | None:
        return None if denominator == 0 else numerator / denominator

    solved_equal = target_major["solved_indices"] == d2_major["solved_indices"]
    witnesses_equal = [
        row["witness"] for row in target_major["per_target"]
    ] == [row["witness"] for row in d2_major["per_target"]]
    inversion_ratio = ratio_value(
        batch_counters["field_inversions"],
        target_counters["field_inversions"],
    )
    d2_read_ratio = ratio_value(
        batch_counters["d2_point_reads"],
        target_counters["d2_point_reads"],
    )
    multiplication_ratio = ratio_value(
        batch_counters["field_multiplications"],
        target_counters["field_multiplications"],
    )
    wall_ratio = ratio_value(
        d2_major["wall_time_seconds"], target_major["wall_time_seconds"]
    )
    disclosed_extra_multiplications = (
        batch_counters["prefix_multiplications"]
        + batch_counters["backward_multiplications"]
    )
    observed_extra_multiplications = max(
        0,
        batch_counters["field_multiplications"]
        - target_counters["field_multiplications"],
    )
    multiplication_tradeoff_pass = (
        observed_extra_multiplications <= disclosed_extra_multiplications
    )
    target_count = exact_int(d2_major["target_count"], "batch target count", 1)
    target_index_bytes = max(
        1,
        math.ceil(max(1, (target_count - 1).bit_length()) / 8),
    )
    workspace_upper_bound = target_count * (
        8 * field_bytes + 2 * target_index_bytes
    )
    observed_workspace = batch_counters[
        "peak_batch_workspace_logical_bytes"
    ]
    workspace_tradeoff_pass = 0 <= observed_workspace <= workspace_upper_bound
    deterministic_operation_signal = (
        cardinality_complete
        and solved_equal
        and witnesses_equal
        and inversion_ratio is not None
        and inversion_ratio <= 0.8
        and d2_read_ratio is not None
        and d2_read_ratio <= 0.8
        and multiplication_tradeoff_pass
        and workspace_tradeoff_pass
    )
    return {
        "cardinality_status": (
            "EXACT" if cardinality_complete else "INSUFFICIENT_SUPPORT"
        ),
        "cardinality_gate": cardinality_complete,
        "solved_set_equal": solved_equal,
        "witnesses_equal": witnesses_equal,
        "inversion_ratio": inversion_ratio,
        "d2_point_read_ratio": d2_read_ratio,
        "field_multiplication_ratio": multiplication_ratio,
        "observed_extra_field_multiplications": observed_extra_multiplications,
        "disclosed_batch_inversion_multiplications": (
            disclosed_extra_multiplications
        ),
        "multiplication_within_disclosed_tradeoff": multiplication_tradeoff_pass,
        "peak_batch_pending_entries": batch_counters[
            "peak_batch_pending_entries"
        ],
        "peak_batch_workspace_logical_bytes": observed_workspace,
        "batch_workspace_logical_upper_bound_bytes": workspace_upper_bound,
        "workspace_within_disclosed_tradeoff": workspace_tradeoff_pass,
        "batch_workspace_model": (
            "per pending affine denominator: five live affine/formula field "
            "elements plus denominator/prefix/inverse arrays; two target-index "
            "arrays; shared input and output points excluded"
        ),
        "wall_time_ratio": wall_ratio,
        "wall_time_improved_diagnostic": (
            wall_ratio is not None and wall_ratio < 1.0
        ),
        "timing_status": "UNVERIFIED_DIAGNOSTIC",
        "timing_attested": False,
        "deterministic_operation_signal_gate": deterministic_operation_signal,
        "practical_signal_gate": False,
        "boundary": (
            "constant-factor operation/read diagnostic; wall time is unattested "
            "and cannot enter a verified practical signal or exponent claim"
        ),
    }


def run_floor_batches(
    exact_floor: Any,
    curve: Any,
    q: int,
    generator: Point,
    factor_points: list[Point],
    d2: Any,
    d3: Any,
    d5_support: Any,
    factor_count: int,
    schedule_seed: int,
    batch_multipliers: list[int],
    batch_replicates: int,
) -> list[dict[str, Any]]:
    requested_sizes = sorted(
        {1, factor_count, *(multiplier * factor_count for multiplier in batch_multipliers)}
    )
    nonidentity_support = sum(point is not None for point in d5_support.points)
    rows: list[dict[str, Any]] = []
    for kind_index, kind in enumerate(("supported", "uniform")):
        for requested_count in requested_sizes:
            if kind == "supported":
                realized_count = min(requested_count, nonidentity_support)
            else:
                realized_count = min(requested_count, q - 1)
            for replicate in range(batch_replicates):
                if requested_count == 1:
                    batch_scale = "1"
                elif requested_count == factor_count:
                    batch_scale = "B"
                elif requested_count == 16 * factor_count:
                    batch_scale = "16B"
                else:
                    batch_scale = f"{requested_count}/B"
                label = f"{kind}-k{requested_count}-r{replicate}"
                seed = (
                    schedule_seed
                    ^ kind_index * 0x9E3779B1
                    ^ requested_count * 0x85EBCA6B
                    ^ replicate * 0xC2B2AE35
                ) & ((1 << 63) - 1)
                if kind == "supported":
                    schedule = exact_floor.make_target_schedule(
                        kind,
                        realized_count,
                        seed,
                        d5_support=d5_support,
                        label=label,
                    )
                else:
                    schedule = exact_floor.make_target_schedule(
                        kind,
                        realized_count,
                        seed,
                        curve=curve,
                        q=q,
                        generator=generator,
                        ops_factory=Ops,
                        label=label,
                    )
                def run_target_kernel() -> dict[str, Any]:
                    return exact_floor.run_target_major_batch(
                        curve,
                        schedule,
                        factor_points,
                        d2,
                        d3,
                        Ops,
                        verify_witness=False,
                    )

                def run_d2_kernel() -> dict[str, Any]:
                    return exact_floor.run_d2_major_batch(
                        curve,
                        schedule,
                        factor_points,
                        d2,
                        d3,
                        Ops,
                        verify_witness=False,
                        verify_affine=False,
                    )

                if replicate % 2 == 0:
                    execution_order = ["target_major", "d2_major"]
                    target_major = run_target_kernel()
                    d2_major = run_d2_kernel()
                else:
                    execution_order = ["d2_major", "target_major"]
                    d2_major = run_d2_kernel()
                    target_major = run_target_kernel()
                target_major_audit = exact_floor.run_target_major_batch(
                    curve,
                    schedule,
                    factor_points,
                    d2,
                    d3,
                    Ops,
                    verify_witness=True,
                )
                d2_major_audit = exact_floor.run_d2_major_batch(
                    curve,
                    schedule,
                    factor_points,
                    d2,
                    d3,
                    Ops,
                    verify_witness=True,
                    verify_affine=True,
                )
                def stable_outcomes(result: dict[str, Any]) -> list[dict[str, Any]]:
                    return [
                        {
                            key: query.get(key)
                            for key in (
                                "success",
                                "witness",
                                "d2_index",
                                "d3_index",
                                "complement",
                            )
                        }
                        for query in result["per_target"]
                    ]

                if (
                    stable_outcomes(target_major)
                    != stable_outcomes(target_major_audit)
                    or stable_outcomes(d2_major) != stable_outcomes(d2_major_audit)
                ):
                    raise AssertionError("timed kernel output differs from audit rerun")
                comparison = batch_comparison_record(
                    target_major,
                    d2_major,
                    max(1, math.ceil(curve.p.bit_length() / 8)),
                    realized_count == requested_count,
                )
                rows.append(
                    {
                        "kind": kind,
                        "batch_scale": batch_scale,
                        "requested_count": requested_count,
                        "realized_count": realized_count,
                        "count_was_clamped": realized_count != requested_count,
                        "replicate": replicate,
                        "kernel_execution_order": execution_order,
                        "schedule": schedule.record,
                        "targets": [point_to_json(point) for point in schedule.points],
                        "target_major": target_major,
                        "d2_major": d2_major,
                        "correctness_audit": {
                            "target_major": target_major_audit,
                            "d2_major": d2_major_audit,
                            "kernel_outputs_equal": True,
                            "timing_excluded": True,
                        },
                        "comparison": comparison,
                    }
                )
    return rows


def run_partial_comparators(
    exact_floor: Any,
    curve: Any,
    q: int,
    generator: Point,
    factor_points: list[Point],
    d2: Any,
    d3: Any,
    d5_support: Any,
    fractions: list[list[int]],
    schedule_seed: int,
) -> dict[str, Any]:
    count = min(4, q - 1, sum(point is not None for point in d5_support.points))
    supported = exact_floor.make_target_schedule(
        "supported",
        count,
        schedule_seed ^ 0x243F6A88,
        d5_support=d5_support,
        label="partial-supported",
    )
    uniform = exact_floor.make_target_schedule(
        "uniform",
        count,
        schedule_seed ^ 0x85A308D3,
        curve=curve,
        q=q,
        generator=generator,
        ops_factory=Ops,
        label="partial-uniform",
    )
    targets = list(supported.points) + list(uniform.points)
    fallback = make_exact_d2_fallback(curve, factor_points, d2)
    cache_rows: list[dict[str, Any]] = []
    for index, (numerator, denominator) in enumerate(fractions):
        cache_seed = (schedule_seed ^ index * 0x13198A2E) & ((1 << 63) - 1)
        cache = exact_floor.build_partial_d3(
            d3,
            numerator,
            denominator,
            cache_seed,
            label=f"partial-{numerator}-{denominator}",
        )
        queries = [
            exact_floor.query_partial_d3(
                curve,
                target,
                factor_points,
                d2,
                cache,
                fallback,
                Ops,
                verify_witness=True,
            )
            for target in targets
        ]
        cache_rows.append(
            {
                "cache": cache.record,
                "queries": queries,
                "success_count": sum(query["success"] for query in queries),
                "cache_hit_count": sum(query["cache_hit"] for query in queries),
                "fallback_count": sum(query["fallback_used"] for query in queries),
            }
        )
    return {
        "targets": [point_to_json(point) for point in targets],
        "target_kinds": ["supported"] * len(supported) + ["uniform"] * len(uniform),
        "caches": cache_rows,
    }


def translator_target_gates(
    target_row: dict[str, Any],
    exact_query: dict[str, Any],
    preprocessing: dict[str, Any],
    d3_record: dict[str, Any],
    symmetry_d3_record: dict[str, Any],
    factor_count: int,
) -> dict[str, Any]:
    online_ratios: dict[str, float | None] = {}
    for weight in INVERSION_WEIGHTS:
        denominator = exact_query["weighted_field_work"][str(weight)]
        numerator = target_row["candidate_weighted_field_work"][str(weight)]
        online_ratios[str(weight)] = None if denominator == 0 else numerator / denominator
    workspace_logical_baseline = max(
        1, math.ceil(symmetry_d3_record["logical_advice_bits"] / 8)
    )
    workspace_python_baseline = max(1, symmetry_d3_record["python_deep_bytes"])
    workspace_logical_ratio = (
        target_row["peak_target_workspace_logical_bytes"]
        / workspace_logical_baseline
    )
    retained_python_ratio = (
        target_row["peak_target_workspace_python_bytes"]
        / workspace_python_baseline
    )
    preprocessing_vector = polynomial_counter_field_vector(
        preprocessing["operations"]
    )
    preprocessing_weights = weighted_field_work(preprocessing_vector)
    comparator_preprocessing_weights = weighted_field_work(
        d3_record["build_ops"]
    )
    crossovers: dict[str, int | None] = {}
    for weight in INVERSION_WEIGHTS:
        exact_online = exact_query["weighted_field_work"][str(weight)]
        candidate_online = target_row["candidate_weighted_field_work"][str(weight)]
        if candidate_online >= exact_online:
            crossovers[str(weight)] = None
            continue
        extra_preprocessing = max(
            0,
            preprocessing_weights[str(weight)]
            - comparator_preprocessing_weights[str(weight)],
        )
        crossovers[str(weight)] = math.ceil(
            extra_preprocessing / (exact_online - candidate_online)
        )
    functional = (
        target_row["polynomial_s3_roots"] == target_row["brute_s3"]["roots"]
        and target_row["polynomial_s4_roots"] == target_row["brute_s4"]["roots"]
        and target_row["all_root_recovery_audit"]["all_requested_roots_recovered"]
        and all(
            branch["equivalent_up_to_expected_scalar"]
            for branch in target_row["branches"]
        )
        and exact_query["success"] == target_row["solver_recovery"]["success"]
    )
    advice_pass = preprocessing["advice_ratio_to_symmetry_d3"] <= 0.8
    workspace_pass = workspace_logical_ratio <= 0.8
    online_pass = all(
        ratio is not None and ratio <= 0.8 for ratio in online_ratios.values()
    )
    amortization_pass = all(
        value is not None and value <= factor_count for value in crossovers.values()
    )
    return {
        "functional_gate": functional,
        "advice_ratio_to_symmetry_d3": preprocessing[
            "advice_ratio_to_symmetry_d3"
        ],
        "advice_gate": advice_pass,
        "workspace_logical_ratio_to_symmetry_d3": workspace_logical_ratio,
        "retained_python_ratio_to_symmetry_d3": retained_python_ratio,
        "workspace_gate": workspace_pass,
        "workspace_gate_boundary": (
            "gated on the conservative logical live-coefficient upper bound; "
            "retained Python deep-size ratio is diagnostic, not a peak-RSS claim"
        ),
        "online_weighted_ratios_to_exact_d2_d3": online_ratios,
        "online_gate": online_pass,
        "preprocessing_crossover_targets": crossovers,
        "translator_preprocessing_weighted_work": preprocessing_weights,
        "comparator_d3_preprocessing_weighted_work": (
            comparator_preprocessing_weights
        ),
        "crossover_preprocessing_differential": {
            str(weight): max(
                0,
                preprocessing_weights[str(weight)]
                - comparator_preprocessing_weights[str(weight)],
            )
            for weight in INVERSION_WEIGHTS
        },
        "amortization_within_b_gate": amortization_pass,
        "pre_matched_coordinate_gate": (
            functional and advice_pass and workspace_pass and online_pass and amortization_pass
        ),
    }


def translator_amortized_projection(
    target_rows: list[dict[str, Any]],
    preprocessing: dict[str, Any],
    d3_record: dict[str, Any],
    factor_count: int,
) -> dict[str, Any]:
    if not target_rows:
        raise ValueError("translator projection requires at least one target row")
    translator_preprocessing = weighted_field_work(
        polynomial_counter_field_vector(preprocessing["operations"])
    )
    comparator_preprocessing = weighted_field_work(d3_record["build_ops"])
    support_count = sum(
        row["exact_d2_d3_query"]["success"] for row in target_rows
    )
    support_rate = support_count / len(target_rows)
    rows: list[dict[str, Any]] = []
    for target_count in sorted({1, factor_count, 16 * factor_count}):
        weighted_rows: dict[str, dict[str, float | None]] = {}
        for weight in INVERSION_WEIGHTS:
            candidate_online = statistics.fmean(
                row["candidate_weighted_field_work"][str(weight)]
                for row in target_rows
            )
            comparator_online = statistics.fmean(
                row["exact_d2_d3_query"]["weighted_field_work"][str(weight)]
                for row in target_rows
            )
            candidate_total = (
                translator_preprocessing[str(weight)]
                + target_count * candidate_online
            )
            comparator_total = (
                comparator_preprocessing[str(weight)]
                + target_count * comparator_online
            )
            weighted_rows[str(weight)] = {
                "candidate_mean_online": candidate_online,
                "comparator_mean_online": comparator_online,
                "candidate_projected_total": candidate_total,
                "comparator_projected_total": comparator_total,
                "candidate_to_comparator_total_ratio": (
                    None
                    if comparator_total == 0
                    else candidate_total / comparator_total
                ),
            }
        rows.append(
            {
                "target_count": target_count,
                "sample_target_count": len(target_rows),
                "sample_supported_count": support_count,
                "sample_support_rate": support_rate,
                "projected_supported_targets": target_count * support_rate,
                "weighted_field_work": weighted_rows,
            }
        )
    return {
        "mode": "independent_target_projection_without_shared_batch_work",
        "translator_preprocessing_weighted_work": translator_preprocessing,
        "comparator_d3_preprocessing_weighted_work": comparator_preprocessing,
        "rows": rows,
        "boundary": (
            "preprocessing plus K times mean online work on the shared uniform "
            "sample; this is amortization accounting, not an implemented batch "
            "translator or evidence of an amortized exponent reduction"
        ),
    }


def compile_family(
    exact_floor: Any,
    polynomial: Any,
    curve_record: dict[str, Any],
    family: str,
    factor_count: int,
    factor_seed: int,
    schedule_seed: int,
    matched_target_seed: int,
    config: dict[str, Any],
) -> dict[str, Any]:
    curve = Curve(curve_record["p"], curve_record["a"], curve_record["b"])
    q = curve_record["q"]
    generator = BASE.point_from_json(curve_record["generator"])
    factor_base = BASE.make_factor_base(
        family, curve, q, generator, factor_count, factor_seed
    )
    factor_points = [BASE.point_from_json(value) for value in factor_base["points"]]
    d2 = SOURCE.build_source_d2(
        curve,
        factor_points,
        "symmetry_lex",
        schedule_seed ^ 0xA4093822,
    )
    d3 = exact_floor.build_d3(curve, factor_points, d2, Ops)
    d5_support = exact_floor.build_d5_audit_support(
        curve, factor_points, d2, d3, Ops
    )
    d2_record = serialize_d2(d2, curve, len(factor_points))
    d3_record = serialize_d3(d3, curve, len(factor_points))
    d3_record["build_record"] = d3.record
    symmetry_codec = build_symmetry_d3_codec(curve, factor_points, d3)
    d3_record["symmetry_codec"] = symmetry_codec.record

    floor_batches = run_floor_batches(
        exact_floor,
        curve,
        q,
        generator,
        factor_points,
        d2,
        d3,
        d5_support,
        factor_count,
        schedule_seed,
        config["batch_multipliers"],
        config["batch_replicates"],
    )
    partial = run_partial_comparators(
        exact_floor,
        curve,
        q,
        generator,
        factor_points,
        d2,
        d3,
        d5_support,
        config["partial_d3_fractions"],
        schedule_seed,
    )

    materialized = BASE.compile_four_sum_advice(curve, factor_points, 1)
    materialized_queries = [
        SOURCE.materialized_query_d5(
            curve,
            factor_points,
            materialized.mapping,
            BASE.point_from_json(target),
        )
        for target in partial["targets"]
    ]
    advice_budget_bits = d2_record["logical_advice_bits"] + symmetry_codec.record[
        "logical_advice_bits"
    ]
    bsgs = BASE.run_matched_bsgs_preprocessing(
        curve,
        q,
        generator,
        advice_budget_bits,
        schedule_seed,
        2,
    )

    translator: dict[str, Any] | None = None
    if family in config["translator_families"]:
        preprocessing = build_translator_preprocessing(
            polynomial,
            curve,
            factor_base,
            d2,
            d2_record,
            d3_record,
            symmetry_codec.record,
        )
        identity_target_control = s3_identity_target_control(
            curve,
            factor_points,
            d2,
        )
        coordinate_cardinality = target_cardinality_record(
            config["coordinate_targets"],
            sum(point is not None for point in d5_support.points),
        )
        coordinate_count = coordinate_cardinality["realized_count"]
        if coordinate_count == 0:
            raise AssertionError("coordinate schedule has no supported affine target")
        coordinate_schedule = exact_floor.make_target_schedule(
            "supported",
            coordinate_count,
            schedule_seed ^ 0x299F31D0,
            d5_support=d5_support,
            label="coordinate-supported",
        )
        def evaluate_coordinate_target(target: Point) -> dict[str, Any]:
            target_row = run_translator_target(
                polynomial,
                curve,
                factor_points,
                d2,
                preprocessing,
                target,
            )
            exact_query = exact_floor.query_d2_d3(
                curve, target, factor_points, d2, d3, Ops, verify_witness=True
            )
            symmetry_query = query_symmetry_d3(
                curve, target, factor_points, d2, symmetry_codec
            )
            if exact_query["success"] != symmetry_query["success"]:
                raise AssertionError("full and symmetry D3 comparators disagree")
            target_row["exact_d2_d3_query"] = exact_query
            target_row["symmetry_d3_query"] = symmetry_query
            target_row["gates"] = translator_target_gates(
                target_row,
                exact_query,
                preprocessing,
                d3_record,
                symmetry_codec.record,
                factor_count,
            )
            return target_row

        target_rows = [
            evaluate_coordinate_target(target)
            for target in coordinate_schedule.points
        ]
        matched_cardinality = target_cardinality_record(
            config["coordinate_targets"], q - 1
        )
        matched_count = matched_cardinality["realized_count"]
        if matched_count == 0:
            raise AssertionError("matched schedule has no affine group target")
        matched_schedule = exact_floor.make_target_schedule(
            "uniform",
            matched_count,
            matched_target_seed,
            curve=curve,
            q=q,
            generator=generator,
            ops_factory=Ops,
            label="coordinate-matched-uniform",
        )
        matched_target_rows = [
            evaluate_coordinate_target(target)
            for target in matched_schedule.points
        ]
        amortized_projection = translator_amortized_projection(
            matched_target_rows,
            preprocessing,
            d3_record,
            factor_count,
        )
        translator = {
            "preprocessing": preprocessing,
            "s3_identity_target_control": identity_target_control,
            "coordinate_target_cardinality": coordinate_cardinality,
            "schedule": coordinate_schedule.record,
            "targets": target_rows,
            "matched_uniform_target_cardinality": matched_cardinality,
            "matched_uniform_schedule": matched_schedule.record,
            "matched_uniform_targets": matched_target_rows,
            "amortized_projection": amortized_projection,
            "functional_gate": (
                coordinate_cardinality["cardinality_gate"]
                and matched_cardinality["cardinality_gate"]
                and identity_target_control["functional_gate"]
                and all(row["gates"]["functional_gate"] for row in target_rows)
                and all(
                    row["gates"]["functional_gate"]
                    for row in matched_target_rows
                )
            ),
            "pre_matched_coordinate_gate": (
                coordinate_cardinality["cardinality_gate"]
                and matched_cardinality["cardinality_gate"]
                and identity_target_control["functional_gate"]
                and all(
                    row["gates"]["pre_matched_coordinate_gate"]
                    for row in target_rows + matched_target_rows
                )
            ),
        }

    row = {
        "family": family,
        "factor_base": serialize_factor_base(factor_base),
        "d2": d2_record,
        "d3": d3_record,
        "d5_audit": d5_support.record,
        "floor": {
            "name": "complete exact D2+D3 meet-in-the-middle comparator",
            "batches": floor_batches,
            "partial_d3": partial,
            "materialized_d4": {
                "record": materialized.record,
                "queries": materialized_queries,
            },
            "matched_bsgs": bsgs,
        },
        "translator": translator,
    }
    return json_native(row)


def attach_random_x_comparisons(instance: dict[str, Any]) -> None:
    random_row = next(row for row in instance["rows"] if row["family"] == "random_x")
    if random_row["translator"] is None:
        raise AssertionError("random_x translator control is missing")
    random_targets = random_row["translator"]["matched_uniform_targets"]
    random_target_points = [target["target"] for target in random_targets]
    random_work = {
        str(weight): statistics.fmean(
            target["candidate_weighted_field_work"][str(weight)]
            for target in random_targets
        )
        for weight in INVERSION_WEIGHTS
    }
    random_density = statistics.fmean(
        target["combined_g"]["density"] for target in random_targets
    )
    random_support_count = sum(
        target["exact_d2_d3_query"]["success"] for target in random_targets
    )
    for row in instance["rows"]:
        translator = row["translator"]
        if translator is None:
            continue
        matched_targets = translator["matched_uniform_targets"]
        if [target["target"] for target in matched_targets] != random_target_points:
            raise AssertionError("coordinate/random_x comparison targets are not identical")
        work_ratios: dict[str, float | None] = {}
        for weight in INVERSION_WEIGHTS:
            candidate = statistics.fmean(
                target["candidate_weighted_field_work"][str(weight)]
                for target in matched_targets
            )
            denominator = random_work[str(weight)]
            work_ratios[str(weight)] = None if denominator == 0 else candidate / denominator
        density = statistics.fmean(
            target["combined_g"]["density"] for target in matched_targets
        )
        density_ratio = None if random_density == 0 else density / random_density
        support_count = sum(
            target["exact_d2_d3_query"]["success"] for target in matched_targets
        )
        support_not_worse = support_count >= random_support_count
        same_map_null_available = row["family"] == "x_interval"
        matched_pass = (
            same_map_null_available
            and support_not_worse
            and (
                all(ratio is not None and ratio <= 0.8 for ratio in work_ratios.values())
                or (density_ratio is not None and density_ratio <= 0.8)
            )
        )
        translator["matched_random_x"] = {
            "weighted_work_ratios": work_ratios,
            "combined_g_density_ratio": density_ratio,
            "shared_target_count": len(matched_targets),
            "shared_target_digest": translator["matched_uniform_schedule"][
                "target_digest"
            ],
            "coordinate_support_count": support_count,
            "random_x_support_count": random_support_count,
            "support_not_worse": support_not_worse,
            "same_map_null_available": same_map_null_available,
            "comparison_status": (
                "ELIGIBLE_IDENTITY_MAP_NULL"
                if same_map_null_available
                else "MAP_CONFOUNDED_NO_CONTINUATION"
            ),
            "matched_coordinate_gate": matched_pass,
            "boundary": (
                "same family-independent uniform points; support is measured, "
                "not conditioned on either factor base; square/Mobius families "
                "cannot continue without a randomized same-map null"
            ),
        }
        translator["coordinate_instance_gate"] = (
            translator["functional_gate"]
            and translator["pre_matched_coordinate_gate"]
            and translator["coordinate_target_cardinality"]["cardinality_gate"]
            and translator["matched_uniform_target_cardinality"][
                "cardinality_gate"
            ]
            and matched_pass
        )


def aggregate_results(instances: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]:
    translator_rows = [
        (instance, row)
        for instance in instances
        for row in instance["rows"]
        if row["translator"] is not None
    ]
    expected_instance_count = len(config["bit_sizes"]) * len(config["seeds"])
    family_slopes: dict[str, dict[str, float | None]] = {}
    family_trend_rows: list[dict[str, Any]] = []
    for family in config["translator_families"]:
        contexts = [
            (instance, row)
            for instance, row in translator_rows
            if row["family"] == family
        ]
        slopes: dict[str, float | None] = {
            f"candidate_weighted_{weight}": fit_log_slope(
                [
                    (
                        instance["curve"]["q"],
                        statistics.fmean(
                            target["candidate_weighted_field_work"][str(weight)]
                            for target in (
                                row["translator"]["targets"]
                                + row["translator"]["matched_uniform_targets"]
                            )
                        ),
                    )
                    for instance, row in contexts
                ]
            )
            for weight in INVERSION_WEIGHTS
        }
        slopes.update(
            {
                "combined_g_max_variable_degree": fit_log_slope(
                    [
                        (
                            instance["curve"]["q"],
                            statistics.fmean(
                                max(target["combined_g"]["degrees"])
                                for target in (
                                    row["translator"]["targets"]
                                    + row["translator"][
                                        "matched_uniform_targets"
                                    ]
                                )
                            ),
                        )
                        for instance, row in contexts
                    ]
                ),
                "combined_g_term_count": fit_log_slope(
                    [
                        (
                            instance["curve"]["q"],
                            statistics.fmean(
                                target["combined_g"]["term_count"]
                                for target in (
                                    row["translator"]["targets"]
                                    + row["translator"][
                                        "matched_uniform_targets"
                                    ]
                                )
                            ),
                        )
                        for instance, row in contexts
                    ]
                ),
                "combined_g_density": fit_log_slope(
                    [
                        (
                            instance["curve"]["q"],
                            statistics.fmean(
                                target["combined_g"]["density"]
                                for target in (
                                    row["translator"]["targets"]
                                    + row["translator"][
                                        "matched_uniform_targets"
                                    ]
                                )
                            ),
                        )
                        for instance, row in contexts
                    ]
                ),
            "explicit_h_coefficients": fit_log_slope(
                [
                    (
                            instance["curve"]["q"],
                        statistics.fmean(
                            target["h_coefficient_writes"]
                                for target in (
                                    row["translator"]["targets"]
                                    + row["translator"][
                                        "matched_uniform_targets"
                                    ]
                                )
                        ),
                    )
                        for instance, row in contexts
                ]
            ),
            "symmetry_d3_advice_bits": fit_log_slope(
                [
                        (
                            instance["curve"]["q"],
                            row["d3"]["symmetry_codec"][
                                "logical_advice_bits"
                            ],
                        )
                        for instance, row in contexts
                ]
            ),
            }
        )
        family_slopes[family] = slopes
        materialization_slope = slopes["symmetry_d3_advice_bits"]
        bounded_metric_names = [
            *(f"candidate_weighted_{weight}" for weight in INVERSION_WEIGHTS),
            "combined_g_max_variable_degree",
            "combined_g_term_count",
            "explicit_h_coefficients",
        ]
        bounded_results = {
            name: {
                "slope": slopes[name],
                "materialization_slope": materialization_slope,
                "pass": (
                    slopes[name] is not None
                    and materialization_slope is not None
                    and slopes[name] <= materialization_slope
                ),
            }
            for name in bounded_metric_names
        }
        coverage_gate = (
            len(contexts) == expected_instance_count
            and sorted({instance["bits"] for instance, _ in contexts})
            == sorted(config["bit_sizes"])
            and all(
                {
                    instance["seed"]
                    for instance, _ in contexts
                    if instance["bits"] == bits
                }
                == set(config["seeds"])
                for bits in config["bit_sizes"]
            )
        )
        density_slope = slopes["combined_g_density"]
        density_nonincreasing = density_slope is not None and density_slope <= 0
        all_slopes_defined = all(value is not None for value in slopes.values())
        trend_gate = (
            coverage_gate
            and all_slopes_defined
            and density_nonincreasing
            and all(result["pass"] for result in bounded_results.values())
        )
        family_trend_rows.append(
            {
                "family": family,
                "observed_instance_count": len(contexts),
                "expected_instance_count": expected_instance_count,
                "observed_bit_sizes": sorted(
                    {instance["bits"] for instance, _ in contexts}
                ),
                "expected_bit_sizes": sorted(config["bit_sizes"]),
                "coverage_gate": coverage_gate,
                "all_slopes_defined": all_slopes_defined,
                "bounded_by_d3_materialization": bounded_results,
                "density_slope": density_slope,
                "density_nonincreasing_gate": density_nonincreasing,
                "trend_gate": trend_gate,
                "status": "PASS" if trend_gate else "FAIL_CLOSED",
            }
        )
    trend_by_family = {row["family"]: row for row in family_trend_rows}
    for _, row in translator_rows:
        translator = row["translator"]
        trend_gate = trend_by_family[row["family"]]["trend_gate"]
        translator["family_trend_gate"] = trend_gate
        translator["coordinate_continuation_gate"] = (
            translator["coordinate_instance_gate"] and trend_gate
        )
    batch_rows = [
        batch
        for instance in instances
        for row in instance["rows"]
        for batch in row["floor"]["batches"]
    ]
    batch_context_rows = [
        (row["family"], batch)
        for instance in instances
        for row in instance["rows"]
        for batch in row["floor"]["batches"]
    ]
    continuation_family_rows: list[dict[str, Any]] = []
    for family in config["translator_families"]:
        family_rows = [
            row["translator"]
            for _, row in translator_rows
            if row["family"] == family
        ]
        continuation_family_rows.append(
            {
                "family": family,
                "observed_instance_count": len(family_rows),
                "expected_instance_count": expected_instance_count,
                "trend_gate": trend_by_family[family]["trend_gate"],
                "all_instances_pass": (
                    family != "random_x"
                    and len(family_rows) == expected_instance_count
                    and all(
                        translator["coordinate_continuation_gate"]
                        for translator in family_rows
                    )
                ),
            }
        )
    batch_group_rows: list[dict[str, Any]] = []
    expected_batch_rows = expected_instance_count * config["batch_replicates"]
    for family in config["floor_families"]:
        for kind in ("supported", "uniform"):
            scales = sorted(
                {
                    batch["batch_scale"]
                    for row_family, batch in batch_context_rows
                    if row_family == family and batch["kind"] == kind
                }
            )
            for scale in scales:
                grouped = [
                    batch
                    for row_family, batch in batch_context_rows
                    if row_family == family
                    and batch["kind"] == kind
                    and batch["batch_scale"] == scale
                ]
                batch_group_rows.append(
                    {
                        "family": family,
                        "target_kind": kind,
                        "batch_scale": scale,
                        "observed_row_count": len(grouped),
                        "expected_row_count": expected_batch_rows,
                        "required_scale_for_practical_signal": scale in {"B", "16B"},
                        "all_operation_rows_pass": (
                            len(grouped) == expected_batch_rows
                            and all(
                                batch["comparison"][
                                    "deterministic_operation_signal_gate"
                                ]
                                for batch in grouped
                            )
                        ),
                        "all_timing_rows_pass": (
                            len(grouped) == expected_batch_rows
                            and all(
                                batch["comparison"]["practical_signal_gate"]
                                for batch in grouped
                            )
                        ),
                    }
                )
    return {
        "verified_functional_translator_rows": sum(
            row["translator"]["functional_gate"] for _, row in translator_rows
        ),
        "translator_row_count": len(translator_rows),
        "coordinate_continuation_rows": [
            {
                "curve_id": instance["curve"]["id"],
                "family": row["family"],
            }
            for instance, row in translator_rows
            if row["translator"]["coordinate_continuation_gate"]
        ],
        "coordinate_continuation_families": continuation_family_rows,
        "conjunctive_continuation_families": [
            row["family"]
            for row in continuation_family_rows
            if row["all_instances_pass"]
        ],
        "trend_gates": family_trend_rows,
        "batch_practical_signal_count": sum(
            batch["comparison"]["practical_signal_gate"] for batch in batch_rows
        ),
        "batch_row_count": len(batch_rows),
        "batch_practical_signal_groups": batch_group_rows,
        "conjunctive_batch_operation_signals": [
            {
                "family": row["family"],
                "target_kind": row["target_kind"],
                "batch_scale": row["batch_scale"],
            }
            for row in batch_group_rows
            if row["required_scale_for_practical_signal"]
            and row["all_operation_rows_pass"]
        ],
        "conjunctive_batch_practical_signals": [
            {
                "family": row["family"],
                "target_kind": row["target_kind"],
                "batch_scale": row["batch_scale"],
            }
            for row in batch_group_rows
            if row["required_scale_for_practical_signal"]
            and row["all_timing_rows_pass"]
        ],
        "exploratory_slopes": family_slopes,
        "boundary": (
            "three-size/two-seed trend gates fail closed and remain toy "
            "diagnostics; no exponent or ECDLP promotion follows"
        ),
    }


def embedding_degree(p: int, q: int) -> int:
    residue = p % q
    if residue == 0:
        raise ValueError("field characteristic is not invertible modulo q")
    value = 1
    for degree in range(1, q):
        value = value * residue % q
        if value == 1:
            return degree
    raise AssertionError("failed to find the finite-field embedding degree")


def preflight_curve_schedule(config: dict[str, Any]) -> list[dict[str, Any]]:
    scheduled: list[dict[str, Any]] = []
    used_primes: set[int] = set()
    for bits in config["bit_sizes"]:
        for seed in config["seeds"]:
            curve = BASE.generate_clean_curve(bits, seed + bits * 1009)
            if curve["p"] in used_primes:
                raise AssertionError(
                    "preflight rejected a repeated field modulus; choose a "
                    "collision-free seed schedule before compilation"
                )
            used_primes.add(curve["p"])
            if curve["p"] % 4 != 3:
                raise AssertionError("development field left the p mod 4 = 3 family")
            if curve["trace"] in {0, 1} or curve["j_invariant"] in {
                0,
                1728 % curve["p"],
            }:
                raise AssertionError("curve preflight accepted an excluded curve")
            degree = embedding_degree(curve["p"], curve["q"])
            if degree <= MOV_EMBEDDING_DEGREE_THRESHOLD:
                raise AssertionError("curve preflight found an exceptional MOV degree")
            curve = {
                **curve,
                "embedding_degree": degree,
                "mov_exclusion_threshold": MOV_EMBEDDING_DEGREE_THRESHOLD,
                "mov_exceptional": False,
                "field_family_restriction": "p mod 4 = 3",
            }
            scheduled.append({"bits": bits, "seed": seed, "curve": curve})
    return scheduled


def run_experiment(
    config: dict[str, Any],
    frozen: bool,
    *,
    bind_sources: bool = True,
) -> dict[str, Any]:
    source_hashes_at_start = bound_source_hashes() if bind_sources else {}
    if bind_sources and (
        source_hashes_at_start["generator_sha256"] != LOADED_GENERATOR_SHA256
        or source_hashes_at_start["source_tag_predecessor_sha256"]
        != LOADED_SOURCE_TAG_SHA256
    ):
        raise RuntimeError("loaded source differs from the source-bound start state")
    exact_floor = load_exact_floor()
    polynomial = load_polynomial_engine()
    scheduled_curves = preflight_curve_schedule(config)
    instances: list[dict[str, Any]] = []
    for scheduled in scheduled_curves:
        bits = scheduled["bits"]
        seed = scheduled["seed"]
        curve_record = scheduled["curve"]
        factor_count = BASE.choose_factor_base_size(
            curve_record["q"], config["occupancy_lambda"]
        )
        matched_target_seed = (
            seed ^ bits * 0xD1B54A32 ^ 0x94D049BB
        ) & ((1 << 63) - 1)
        rows: list[dict[str, Any]] = []
        for family_index, family in enumerate(config["floor_families"]):
            factor_seed = (
                seed ^ bits * 0x45D9F3B ^ family_index * 0x9E3779B1
            ) & ((1 << 63) - 1)
            schedule_seed = (
                seed ^ bits * 0x7FEB352D ^ family_index * 0x846CA68B
            ) & ((1 << 63) - 1)
            rows.append(
                compile_family(
                    exact_floor,
                    polynomial,
                    curve_record,
                    family,
                    factor_count,
                    factor_seed,
                    schedule_seed,
                    matched_target_seed,
                    config,
                )
            )
        instance = {
            "bits": bits,
            "seed": seed,
            "curve": curve_record,
            "factor_base_size": factor_count,
            "rho": BASE.run_rho_baseline(curve_record, seed, config["rho_trials"]),
            "rows": rows,
        }
        attach_random_x_comparisons(instance)
        instances.append(json_native(instance))
    aggregate = aggregate_results(instances, config)
    promotion_rows = (
        aggregate["conjunctive_continuation_families"] if frozen else []
    )
    source_hashes_at_end = bound_source_hashes() if bind_sources else {}
    if source_hashes_at_end != source_hashes_at_start:
        raise RuntimeError("source-bound files changed during experiment execution")
    preflight_record = {
        "curve_count": len(scheduled_curves),
        "unique_field_modulus_count": len(
            {row["curve"]["p"] for row in scheduled_curves}
        ),
        "mov_embedding_degree_threshold": MOV_EMBEDDING_DEGREE_THRESHOLD,
        "field_family_restriction": "p mod 4 = 3",
        "curves": [
            {
                "bits": row["bits"],
                "seed": row["seed"],
                "curve_id": row["curve"]["id"],
                "p": row["curve"]["p"],
                "q": row["curve"]["q"],
                "embedding_degree": row["curve"]["embedding_degree"],
            }
            for row in scheduled_curves
        ],
    }
    preflight_record["digest"] = stable_digest(preflight_record["curves"])
    result = {
        "protocol": PROTOCOL,
        "claim_status": CLAIM_STATUS,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "configuration": config,
        "configuration_is_frozen": frozen,
        "development_only": not frozen,
        "source_hashes": source_hashes_at_start,
        "source_hash_recheck": {
            "performed": bind_sources,
            "stable": source_hashes_at_end == source_hashes_at_start,
            "end_digest": stable_digest(source_hashes_at_end),
        },
        "curve_schedule_preflight": preflight_record,
        "instances": instances,
        "aggregate": aggregate,
        "promotion_rows": promotion_rows,
        "boundary": (
            "authorized generated toy curves only; functional or continuation "
            "gates are not an exponent result, deployed-key break, or ECDLP claim"
        ),
    }
    return json_native(result)


def parse_fraction_pairs(
    numerators: list[int], denominators: list[int]
) -> list[list[int]]:
    if len(numerators) != len(denominators) or not numerators:
        raise ValueError("partial-D3 numerator/denominator lists must align")
    pairs: list[list[int]] = []
    values: set[tuple[int, int]] = set()
    for index, (numerator, denominator) in enumerate(zip(numerators, denominators)):
        numerator = exact_int(numerator, f"partial numerator[{index}]", 1)
        denominator = exact_int(denominator, f"partial denominator[{index}]", 1)
        divisor = math.gcd(numerator, denominator)
        pair = (numerator // divisor, denominator // divisor)
        if not pair[0] < pair[1]:
            raise ValueError("partial-D3 fractions must lie strictly between zero and one")
        if pair in values:
            raise ValueError("partial-D3 fractions must be distinct")
        values.add(pair)
        pairs.append(list(pair))
    return pairs


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bit-sizes", nargs="+", type=int, default=[8, 10, 12])
    parser.add_argument(
        "--seeds", nargs="+", type=int, default=[3317584535, 2246822507]
    )
    parser.add_argument(
        "--floor-families", nargs="+", default=FLOOR_FAMILIES
    )
    parser.add_argument(
        "--translator-families", nargs="+", default=TRANSLATOR_FAMILIES
    )
    parser.add_argument(
        "--partial-d3-numerators", nargs="+", type=int, default=[1, 1, 1]
    )
    parser.add_argument(
        "--partial-d3-denominators", nargs="+", type=int, default=[8, 4, 2]
    )
    parser.add_argument("--batch-multipliers", nargs="+", type=int, default=[1, 16])
    parser.add_argument("--batch-replicates", type=int, default=2)
    parser.add_argument("--coordinate-targets", type=int, default=2)
    parser.add_argument("--occupancy-lambda", type=float, default=0.5)
    parser.add_argument("--rho-trials", type=int, default=2)
    parser.add_argument("--allow-development", action="store_true")
    parser.add_argument("--authorize-canonical", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def config_from_args(args: argparse.Namespace) -> dict[str, Any]:
    config = {
        "bit_sizes": exact_int_list(args.bit_sizes, "bit_sizes", 5),
        "seeds": exact_int_list(args.seeds, "seeds", 0),
        "floor_families": list(args.floor_families),
        "translator_families": list(args.translator_families),
        "partial_d3_fractions": parse_fraction_pairs(
            args.partial_d3_numerators, args.partial_d3_denominators
        ),
        "batch_multipliers": exact_int_list(
            args.batch_multipliers, "batch_multipliers", 1
        ),
        "batch_replicates": exact_int(
            args.batch_replicates, "batch_replicates", 1
        ),
        "coordinate_targets": exact_int(
            args.coordinate_targets, "coordinate_targets", 1
        ),
        "occupancy_lambda": exact_probability(
            args.occupancy_lambda, "occupancy_lambda"
        ),
        "rho_trials": exact_int(args.rho_trials, "rho_trials", 1),
    }
    if config["floor_families"] != list(dict.fromkeys(config["floor_families"])):
        raise ValueError("floor families must be distinct")
    if any(family not in FLOOR_FAMILIES for family in config["floor_families"]):
        raise ValueError("unsupported floor family")
    if config["translator_families"] != list(
        dict.fromkeys(config["translator_families"])
    ):
        raise ValueError("translator families must be distinct")
    if any(
        family not in TRANSLATOR_FAMILIES
        for family in config["translator_families"]
    ):
        raise ValueError("unsupported translator family")
    if not set(config["translator_families"]).issubset(config["floor_families"]):
        raise ValueError("translator families must be included in floor families")
    if "random_x" not in config["translator_families"]:
        raise ValueError("random_x is mandatory as the coordinate null")
    return config


def enforce_authorization(
    config: dict[str, Any],
    allow_development: bool,
    authorize_canonical: bool,
) -> bool:
    frozen = config == FROZEN_CONFIG
    if frozen:
        if allow_development:
            raise ValueError("a frozen canonical configuration cannot use --allow-development")
        if not authorize_canonical:
            raise ValueError("canonical configuration requires --authorize-canonical")
    else:
        if authorize_canonical:
            raise ValueError("--authorize-canonical is invalid for a nonfrozen configuration")
        if not allow_development:
            raise ValueError("nonfrozen configuration requires --allow-development")
    return frozen


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config = config_from_args(args)
    frozen = enforce_authorization(
        config, args.allow_development, args.authorize_canonical
    )
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite existing artifact: {args.output}")
    result = run_experiment(config, frozen)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
