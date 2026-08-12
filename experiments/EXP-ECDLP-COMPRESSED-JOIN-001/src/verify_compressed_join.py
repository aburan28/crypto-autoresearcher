#!/usr/bin/env python3
"""Replay and independently audit compressed-join development artifacts."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
GENERATOR_PATH = SCRIPT_PATH.with_name("compressed_join.py")
Point = tuple[int, int] | None


def load_generator() -> Any:
    spec = importlib.util.spec_from_file_location(
        "compressed_join_verifier_generator", GENERATOR_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load generator: {GENERATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


GENERATOR = load_generator()


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


def reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant is forbidden: {value}")


def reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json_strict(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=reject_duplicate_pairs,
        parse_constant=reject_constant,
    )


def compare_exact(actual: Any, expected: Any, path: str = "$") -> None:
    if type(actual) is not type(expected):
        raise AssertionError(
            f"type mismatch at {path}: {type(actual).__name__} != "
            f"{type(expected).__name__}"
        )
    if isinstance(expected, dict):
        if set(actual) != set(expected):
            raise AssertionError(f"mapping keys differ at {path}")
        for key in sorted(expected):
            compare_exact(actual[key], expected[key], f"{path}.{key}")
        return
    if isinstance(expected, list):
        if len(actual) != len(expected):
            raise AssertionError(f"list length differs at {path}")
        for index, (actual_item, expected_item) in enumerate(zip(actual, expected)):
            compare_exact(actual_item, expected_item, f"{path}[{index}]")
        return
    if isinstance(expected, float):
        if not math.isfinite(actual) or actual != expected:
            raise AssertionError(f"float differs at {path}: {actual!r} != {expected!r}")
        return
    if actual != expected:
        raise AssertionError(f"value differs at {path}: {actual!r} != {expected!r}")


def point_from_json(value: list[int] | None) -> Point:
    if value is None:
        return None
    if type(value) is not list or len(value) != 2:
        raise AssertionError("point must be null or an exact two-coordinate list")
    if any(type(coordinate) is not int for coordinate in value):
        raise AssertionError("point coordinates must be exact integers")
    return value[0], value[1]


class IndependentCurve:
    def __init__(self, p: int, a: int, b: int) -> None:
        self.p = p
        self.a = a
        self.b = b
        if (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p == 0:
            raise AssertionError("independent verifier received a singular curve")

    def on_curve(self, point: Point) -> bool:
        if point is None:
            return True
        x, y = point
        return 0 <= x < self.p and 0 <= y < self.p and (
            y * y - x * x * x - self.a * x - self.b
        ) % self.p == 0

    def neg(self, point: Point) -> Point:
        return None if point is None else (point[0], (-point[1]) % self.p)

    def add(self, left: Point, right: Point) -> Point:
        if left is None:
            return right
        if right is None:
            return left
        x1, y1 = left
        x2, y2 = right
        if x1 == x2 and (y1 + y2) % self.p == 0:
            return None
        if left == right:
            if y1 == 0:
                return None
            slope = (3 * x1 * x1 + self.a) * pow(2 * y1, -1, self.p) % self.p
        else:
            slope = (y2 - y1) * pow((x2 - x1) % self.p, -1, self.p) % self.p
        x3 = (slope * slope - x1 - x2) % self.p
        y3 = (slope * (x1 - x3) - y1) % self.p
        result = (x3, y3)
        if not self.on_curve(result):
            raise AssertionError("independent addition left the curve")
        return result

    def mul(self, scalar: int, point: Point) -> Point:
        if scalar < 0:
            return self.mul(-scalar, self.neg(point))
        result: Point = None
        addend = point
        while scalar:
            if scalar & 1:
                result = self.add(result, addend)
            addend = self.add(addend, addend)
            scalar >>= 1
        return result

    def order(self) -> int:
        total = 1
        exponent = (self.p - 1) // 2
        for x in range(self.p):
            rhs = (x * x * x + self.a * x + self.b) % self.p
            if rhs == 0:
                total += 1
                continue
            symbol = pow(rhs, exponent, self.p)
            if symbol == 1:
                total += 2
            elif symbol != self.p - 1:
                raise AssertionError("invalid independent Legendre symbol")
        return total


def independent_supports(
    curve: IndependentCurve,
    factor_points: list[Point],
) -> tuple[set[Point], set[Point], set[Point]]:
    d2 = {
        curve.add(factor_points[left], factor_points[right])
        for left in range(len(factor_points))
        for right in range(left, len(factor_points))
    }
    ordered_d2 = sorted(d2, key=lambda point: (-1, 0, 0) if point is None else (0, *point))
    d4 = {
        curve.add(ordered_d2[left], ordered_d2[right])
        for left in range(len(ordered_d2))
        for right in range(left, len(ordered_d2))
    }
    d5 = {
        curve.add(partial, point)
        for partial in d4
        for point in factor_points
    }
    return d2, d4, d5


def verify_witness(
    curve: IndependentCurve,
    factor_points: list[Point],
    witness: list[int],
    target: Point,
) -> None:
    total: Point = None
    for index in witness:
        if type(index) is not int or not 0 <= index < len(factor_points):
            raise AssertionError("factor witness index is out of range")
        total = curve.add(total, factor_points[index])
    if total != target:
        raise AssertionError("independent factor witness verification failed")


def verify_semantics(document: dict[str, Any]) -> dict[str, int]:
    verified_families = 0
    verified_rows = 0
    verified_witnesses = 0
    for instance in document["instances"]:
        curve_record = instance["curve"]
        curve = IndependentCurve(
            curve_record["p"], curve_record["a"], curve_record["b"]
        )
        if curve.order() != curve_record["q"]:
            raise AssertionError("independent curve order differs")
        generator = point_from_json(curve_record["generator"])
        if not curve.on_curve(generator) or curve.mul(curve_record["q"], generator) is not None:
            raise AssertionError("generator failed independent subgroup verification")

        for family in instance["families"]:
            verified_families += 1
            factor_points = [
                point_from_json(point) for point in family["factor_base"]["points"]
            ]
            if not all(curve.on_curve(point) for point in factor_points):
                raise AssertionError("factor base contains an off-curve point")
            d2, d4, d5 = independent_supports(curve, factor_points)
            for label, support, record in (
                ("d2", d2, family["d2"]),
                ("d4", d4, family["d4"]),
                ("d5", d5, family["d5"]),
            ):
                if len(support) != record["support_size"]:
                    raise AssertionError(f"independent {label} support size differs")
                ordered = sorted(
                    support,
                    key=lambda point: (-1, 0, 0) if point is None else (0, *point),
                )
                digest = stable_digest(
                    [None if point is None else [point[0], point[1]] for point in ordered]
                )
                if digest != record["support_digest"]:
                    raise AssertionError(f"independent {label} support digest differs")

            target_schedules: dict[str, tuple[str, ...]] = {}
            challenge_schedule: tuple[str, ...] | None = None
            for row in family["rows"]:
                verified_rows += 1
                if row["router"] == GENERATOR.POSITIVE_CONTROL:
                    if row["eligibility"] != "positive_control_only":
                        raise AssertionError("scalar router became eligible")
                for sample_name in ("supported_d4", "supported_d5", "random_d5"):
                    records = row["query_samples"][sample_name]["records"]
                    schedule = tuple(repr(record["target"]) for record in records)
                    previous = target_schedules.setdefault(sample_name, schedule)
                    if schedule != previous:
                        raise AssertionError("router target schedules differ")
                    for record in records:
                        if record["success"]:
                            target = point_from_json(record["target"])
                            verify_witness(curve, factor_points, record["witness"], target)
                            verified_witnesses += 1
                current_challenges = tuple(
                    repr(challenge["target"])
                    for challenge in row["descent"]["challenges"]
                )
                if challenge_schedule is None:
                    challenge_schedule = current_challenges
                elif current_challenges != challenge_schedule:
                    raise AssertionError("router descent target schedules differ")
                for challenge in row["descent"]["challenges"]:
                    recovered = challenge["recovered_scalar"]
                    target = point_from_json(challenge["target"])
                    if recovered is None or curve.mul(recovered, generator) != target:
                        raise AssertionError("independent descent scalar verification failed")
                    if recovered != challenge["known_scalar_private_audit"]:
                        raise AssertionError("private descent scalar differs")
    return {
        "verified_instances": len(document["instances"]),
        "verified_families": verified_families,
        "verified_rows": verified_rows,
        "verified_factor_witnesses": verified_witnesses,
    }


def verify_source_hashes(document: dict[str, Any]) -> None:
    expected = {
        "compressed_join_sha256": sha256_file(GENERATOR_PATH),
        "compressed_join_verifier_sha256": sha256_file(SCRIPT_PATH),
        "fixed_curve_compiler_sha256": sha256_file(GENERATOR.BASE_PATH),
        "coordinate_energy_sha256": sha256_file(GENERATOR.BASE.ENERGY_PATH),
        "contract_sha256": sha256_file(GENERATOR.CONTRACT_PATH),
        "hypothesis_sha256": sha256_file(GENERATOR.HYPOTHESIS_PATH),
        "theory_sha256": sha256_file(GENERATOR.THEORY_PATH),
        "literature_sha256": sha256_file(GENERATOR.LITERATURE_PATH),
    }
    compare_exact(document["source_hashes"], expected, "$.source_hashes")


def verify_document(
    document: dict[str, Any],
    enforce_frozen: bool = True,
) -> dict[str, Any]:
    if type(document) is not dict:
        raise AssertionError("top-level document must be a mapping")
    if document.get("protocol") != GENERATOR.PROTOCOL:
        raise AssertionError("protocol mismatch")
    verify_source_hashes(document)
    if enforce_frozen:
        compare_exact(document["configuration"], GENERATOR.FROZEN_CONFIG, "$.configuration")
        if not document["configuration_is_frozen"] or document["development_only"]:
            raise AssertionError("canonical verification requires frozen configuration")
    else:
        if document["configuration_is_frozen"] != (
            document["configuration"] == GENERATOR.FROZEN_CONFIG
        ):
            raise AssertionError("configuration freeze label is inconsistent")
    replayed = GENERATOR.run_experiment(document["configuration"])
    compare_exact(document, replayed)
    independent = verify_semantics(document)
    return {
        "status": "verified",
        "protocol": document["protocol"],
        "development_only": document["development_only"],
        "canonical_configuration": document["configuration_is_frozen"],
        "canonical_document_sha256": hashlib.sha256(
            stable_json_bytes(document)
        ).hexdigest(),
        "verifier_sha256": sha256_file(SCRIPT_PATH),
        "generator_sha256": sha256_file(GENERATOR_PATH),
        "routing_rows": document["routing_rows"],
        **independent,
        "boundary": (
            "Deterministic full replay plus independent affine/order/support/witness "
            "audit; a verified development artifact is not a canonical run or an "
            "ECDLP improvement."
        ),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--allow-development",
        action="store_true",
        help="verify a non-frozen development configuration",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    document = load_json_strict(args.input)
    certificate = verify_document(
        document, enforce_frozen=not args.allow_development
    )
    certificate["input_file_sha256"] = sha256_file(args.input)
    encoded = json.dumps(certificate, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if args.output is None:
        sys.stdout.write(encoded)
    else:
        args.output.write_text(encoded, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
