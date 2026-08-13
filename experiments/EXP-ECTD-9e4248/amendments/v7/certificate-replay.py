"""Exact typed replay for the sole ECTD v7 non-target micro-certificate.

The admitted positive domain is intentionally tiny (base prime at most 257,
extension degree at most three, and division primes two and three).  Within that
declared domain every mathematical assertion is recomputed: field
irreducibility and arithmetic, curve/twist identity, point count and order-N
point, division-polynomial factorization into every cyclic line, Frobenius
orbits, canonical stable kernels, Velu maps/codomains, dual compositions, and
maximal endomorphism orders/whole conductors.  Hashes are emitted only after
these checks and never establish acceptance.

This is protocol conformance infrastructure, not a scheduled 40--60-bit curve
constructor and not an experiment runner.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

CERTIFICATE_SCHEMA = "crypto.autoresearch.ectd_v7_certificate.v1"
REPLAY_SCHEMA = "crypto.autoresearch.ectd_v7_certificate_replay.v1"
SCOPE = "sole-fixed-tiny-protocol-neutral-non-target-known-answer"
MAX_BASE_PRIME = 257
MAX_EXTENSION_DEGREE = 3


class CertificateError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _exact_keys(value: Mapping[str, Any], expected: Iterable[str], code: str) -> None:
    actual = set(value)
    wanted = set(expected)
    if actual != wanted:
        raise CertificateError(
            code,
            f"keys differ: missing={sorted(wanted - actual)}, extra={sorted(actual - wanted)}",
        )


def _reject_opaque_authority(value: Any, pointer: str = "") -> None:
    forbidden = {"replay_check", "verified", "valid", "success", "receipt_sha256"}
    if isinstance(value, Mapping):
        found = forbidden.intersection(value)
        if found:
            raise CertificateError("FALSE_RECEIPT", f"opaque authority at {pointer}: {sorted(found)}")
        for key, child in value.items():
            _reject_opaque_authority(child, f"{pointer}/{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_opaque_authority(child, f"{pointer}/{index}")


def _jcs_bytes(value: Any) -> bytes:
    def walk(item: Any) -> None:
        if isinstance(item, Mapping):
            for key, child in item.items():
                if not isinstance(key, str) or not key.isascii():
                    raise CertificateError("FALSE_RECEIPT", "non-ASCII JSON property")
                walk(child)
        elif isinstance(item, list):
            for child in item:
                walk(child)
        elif isinstance(item, float):
            raise CertificateError("FALSE_RECEIPT", "floating point is not authoritative")
        elif isinstance(item, int) and abs(item) > 9_007_199_254_740_991:
            raise CertificateError("FALSE_RECEIPT", "unsafe JSON integer")

    walk(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def _sha(value: Any) -> str:
    return hashlib.sha256(_jcs_bytes(value)).hexdigest()


def _prime(value: int) -> bool:
    if isinstance(value, bool) or not isinstance(value, int) or value < 2:
        return False
    for divisor in range(2, math.isqrt(value) + 1):
        if value % divisor == 0:
            return False
    return True


def _trim(poly: Sequence[int], p: int) -> list[int]:
    out = [coefficient % p for coefficient in poly]
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out or [0]


def _poly_sub(left: Sequence[int], right: Sequence[int], p: int) -> list[int]:
    size = max(len(left), len(right))
    return _trim(
        [
            (left[index] if index < len(left) else 0)
            - (right[index] if index < len(right) else 0)
            for index in range(size)
        ],
        p,
    )


def _poly_mul(left: Sequence[int], right: Sequence[int], p: int) -> list[int]:
    out = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            out[i + j] = (out[i + j] + a * b) % p
    return _trim(out, p)


def _poly_divmod(
    numerator: Sequence[int], denominator: Sequence[int], p: int
) -> tuple[list[int], list[int]]:
    top = _trim(numerator, p)
    bottom = _trim(denominator, p)
    if bottom == [0]:
        raise ZeroDivisionError("zero polynomial")
    quotient = [0] * max(1, len(top) - len(bottom) + 1)
    inverse_lead = pow(bottom[-1], -1, p)
    while top != [0] and len(top) >= len(bottom):
        degree = len(top) - len(bottom)
        factor = top[-1] * inverse_lead % p
        quotient[degree] = factor
        subtract = [0] * degree + [(factor * c) % p for c in bottom]
        top = _poly_sub(top, subtract, p)
    return _trim(quotient, p), _trim(top, p)


def _poly_mod(poly: Sequence[int], modulus: Sequence[int], p: int) -> list[int]:
    return _poly_divmod(poly, modulus, p)[1]


def _poly_gcd(left: Sequence[int], right: Sequence[int], p: int) -> list[int]:
    a, b = _trim(left, p), _trim(right, p)
    while b != [0]:
        a, b = b, _poly_mod(a, b, p)
    inverse = pow(a[-1], -1, p)
    return [(coefficient * inverse) % p for coefficient in a]


def _poly_powmod(
    base: Sequence[int], exponent: int, modulus: Sequence[int], p: int
) -> list[int]:
    result = [1]
    current = _poly_mod(base, modulus, p)
    while exponent:
        if exponent & 1:
            result = _poly_mod(_poly_mul(result, current, p), modulus, p)
        current = _poly_mod(_poly_mul(current, current, p), modulus, p)
        exponent >>= 1
    return result


def _prime_divisors(value: int) -> list[int]:
    out: list[int] = []
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            out.append(divisor)
            while value % divisor == 0:
                value //= divisor
        divisor += 1
    if value > 1:
        out.append(value)
    return out


def _irreducible(modulus: Sequence[int], p: int) -> bool:
    polynomial = _trim(modulus, p)
    degree = len(polynomial) - 1
    if degree < 1 or polynomial[-1] != 1:
        return False
    if degree == 1:
        return True
    x = [0, 1]
    for divisor in _prime_divisors(degree):
        probe = _poly_sub(_poly_powmod(x, p ** (degree // divisor), polynomial, p), x, p)
        if _poly_gcd(polynomial, probe, p) != [1]:
            return False
    final = _poly_sub(_poly_powmod(x, p**degree, polynomial, p), x, p)
    return _poly_mod(final, polynomial, p) == [0]


@dataclass(frozen=True)
class Field:
    field_id: str
    p: int
    degree: int
    modulus: tuple[int, ...]

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "Field":
        _exact_keys(record, ("field_id", "p", "degree", "modulus"), "FIELD_CONSTRUCTION_FAILURE")
        p = record["p"]
        degree = record["degree"]
        modulus = record["modulus"]
        if not _prime(p) or not 5 <= p <= MAX_BASE_PRIME:
            raise CertificateError("FIELD_CONSTRUCTION_FAILURE", "base prime outside tiny exact domain")
        if isinstance(degree, bool) or not isinstance(degree, int) or not 1 <= degree <= MAX_EXTENSION_DEGREE:
            raise CertificateError("FIELD_CONSTRUCTION_FAILURE", "extension degree outside domain")
        if (
            not isinstance(modulus, list)
            or len(modulus) != degree + 1
            or any(isinstance(x, bool) or not isinstance(x, int) or not 0 <= x < p for x in modulus)
            or modulus[-1] != 1
            or not _irreducible(modulus, p)
        ):
            raise CertificateError("FIELD_CONSTRUCTION_FAILURE", "modulus is not canonical irreducible monic")
        return cls(str(record["field_id"]), p, degree, tuple(modulus))

    @property
    def zero(self) -> tuple[int, ...]:
        return (0,) * self.degree

    @property
    def one(self) -> tuple[int, ...]:
        return (1,) + (0,) * (self.degree - 1)

    def decode(self, value: Any) -> tuple[int, ...]:
        if (
            not isinstance(value, list)
            or len(value) != self.degree
            or any(isinstance(x, bool) or not isinstance(x, int) or not 0 <= x < self.p for x in value)
        ):
            raise CertificateError("FIELD_CONSTRUCTION_FAILURE", f"noncanonical {self.field_id} element")
        return tuple(value)

    def encode(self, value: tuple[int, ...]) -> list[int]:
        return list(value)

    def embed(self, integer: int) -> tuple[int, ...]:
        return (integer % self.p,) + (0,) * (self.degree - 1)

    def add(self, left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
        return tuple((a + b) % self.p for a, b in zip(left, right))

    def neg(self, value: tuple[int, ...]) -> tuple[int, ...]:
        return tuple((-x) % self.p for x in value)

    def sub(self, left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
        return self.add(left, self.neg(right))

    def mul(self, left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
        work = [0] * (2 * self.degree - 1)
        for i, a in enumerate(left):
            for j, b in enumerate(right):
                work[i + j] = (work[i + j] + a * b) % self.p
        for power in range(len(work) - 1, self.degree - 1, -1):
            coefficient = work[power] % self.p
            if coefficient:
                for index in range(self.degree):
                    work[power - self.degree + index] = (
                        work[power - self.degree + index]
                        - coefficient * self.modulus[index]
                    ) % self.p
        return tuple(work[: self.degree])

    def pow(self, value: tuple[int, ...], exponent: int) -> tuple[int, ...]:
        result, current = self.one, value
        while exponent:
            if exponent & 1:
                result = self.mul(result, current)
            current = self.mul(current, current)
            exponent >>= 1
        return result

    def inv(self, value: tuple[int, ...]) -> tuple[int, ...]:
        if value == self.zero:
            raise ZeroDivisionError("zero field element")
        inverse = self.pow(value, self.p**self.degree - 2)
        if self.mul(value, inverse) != self.one:
            raise CertificateError("FIELD_CONSTRUCTION_FAILURE", "inverse check failed")
        return inverse

    def div(self, left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
        return self.mul(left, self.inv(right))

    def all_elements(self) -> Iterable[tuple[int, ...]]:
        for index in range(self.p**self.degree):
            value = index
            coefficients: list[int] = []
            for _ in range(self.degree):
                value, residue = divmod(value, self.p)
                coefficients.append(residue)
            yield tuple(coefficients)


Point = tuple[tuple[int, ...], tuple[int, ...]] | None


@dataclass(frozen=True)
class Curve:
    curve_id: str
    field: Field
    a: tuple[int, ...]
    b: tuple[int, ...]

    @classmethod
    def from_record(cls, record: Mapping[str, Any], fields: Mapping[str, Field]) -> "Curve":
        _exact_keys(record, ("curve_id", "field_id", "a", "b"), "CM_MODEL_ABSENT")
        field = fields.get(record["field_id"])
        if field is None:
            raise CertificateError("CM_MODEL_ABSENT", "curve names unknown field")
        curve = cls(str(record["curve_id"]), field, field.decode(record["a"]), field.decode(record["b"]))
        four_a3 = field.mul(field.embed(4), field.pow(curve.a, 3))
        twenty_seven_b2 = field.mul(field.embed(27), field.pow(curve.b, 2))
        if field.add(four_a3, twenty_seven_b2) == field.zero:
            raise CertificateError("CM_MODEL_ABSENT", "singular curve")
        return curve

    def encode_point(self, point: Point) -> Any:
        if point is None:
            return None
        return {"x": self.field.encode(point[0]), "y": self.field.encode(point[1])}

    def decode_point(self, value: Any) -> Point:
        if value is None:
            return None
        if not isinstance(value, Mapping):
            raise CertificateError("ORDER_N_POINT_CERTIFICATE_FAILURE", "point object required")
        _exact_keys(value, ("x", "y"), "ORDER_N_POINT_CERTIFICATE_FAILURE")
        point = (self.field.decode(value["x"]), self.field.decode(value["y"]))
        if not self.on_curve(point):
            raise CertificateError("ORDER_N_POINT_CERTIFICATE_FAILURE", "point is off curve")
        return point

    def on_curve(self, point: Point) -> bool:
        if point is None:
            return True
        x, y = point
        left = self.field.pow(y, 2)
        right = self.field.add(
            self.field.add(self.field.pow(x, 3), self.field.mul(self.a, x)), self.b
        )
        return left == right

    def neg(self, point: Point) -> Point:
        return None if point is None else (point[0], self.field.neg(point[1]))

    def add(self, left: Point, right: Point) -> Point:
        if left is None:
            return right
        if right is None:
            return left
        x1, y1 = left
        x2, y2 = right
        if x1 == x2 and self.field.add(y1, y2) == self.field.zero:
            return None
        if left == right:
            if y1 == self.field.zero:
                return None
            slope = self.field.div(
                self.field.add(self.field.mul(self.field.embed(3), self.field.pow(x1, 2)), self.a),
                self.field.mul(self.field.embed(2), y1),
            )
        else:
            slope = self.field.div(self.field.sub(y2, y1), self.field.sub(x2, x1))
        x3 = self.field.sub(self.field.sub(self.field.pow(slope, 2), x1), x2)
        y3 = self.field.sub(self.field.mul(slope, self.field.sub(x1, x3)), y1)
        point = (x3, y3)
        if not self.on_curve(point):
            raise CertificateError("FALSE_RECEIPT", "group law produced off-curve point")
        return point

    def mul(self, scalar: int, point: Point) -> Point:
        if scalar < 0:
            return self.mul(-scalar, self.neg(point))
        result, current = None, point
        while scalar:
            if scalar & 1:
                result = self.add(result, current)
            current = self.add(current, current)
            scalar >>= 1
        return result

    def enumerate_points(self) -> list[Point]:
        if self.field.degree != 1:
            raise CertificateError("ORDER_CERTIFICATE_FAILURE", "only base-field enumeration admitted")
        points: list[Point] = [None]
        for x in self.field.all_elements():
            for y in self.field.all_elements():
                point = (x, y)
                if self.on_curve(point):
                    points.append(point)
        return points


def _point_key(curve: Curve, point: Point) -> bytes:
    return _jcs_bytes(curve.encode_point(point))


def _division_polynomial(curve: Curve, prime: int) -> list[tuple[int, ...]]:
    field = curve.field
    if prime == 2:
        return [curve.b, curve.a, field.zero, field.one]
    if prime == 3:
        return [
            field.neg(field.pow(curve.a, 2)),
            field.mul(field.embed(12), curve.b),
            field.mul(field.embed(6), curve.a),
            field.zero,
            field.embed(3),
        ]
    raise CertificateError("Q_DIVISION_POLYNOMIAL_FAILURE", "tiny exact domain admits primes 2 and 3")


def _poly_eval_field(
    coefficients: Sequence[tuple[int, ...]], value: tuple[int, ...], field: Field
) -> tuple[int, ...]:
    result = field.zero
    for coefficient in reversed(coefficients):
        result = field.add(field.mul(result, value), coefficient)
    return result


def _monic_field_poly(
    coefficients: Sequence[tuple[int, ...]], field: Field
) -> list[tuple[int, ...]]:
    out = list(coefficients)
    while len(out) > 1 and out[-1] == field.zero:
        out.pop()
    inverse = field.inv(out[-1])
    return [field.mul(coefficient, inverse) for coefficient in out]


def _mul_field_poly(
    left: Sequence[tuple[int, ...]], right: Sequence[tuple[int, ...]], field: Field
) -> list[tuple[int, ...]]:
    out = [field.zero] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            out[i + j] = field.add(out[i + j], field.mul(a, b))
    return out


def _embedded_curve(curve: Curve, field: Field, curve_id: str) -> Curve:
    if curve.field.p != field.p or curve.field.degree != 1:
        raise CertificateError("FIELD_CONSTRUCTION_FAILURE", "invalid base-field embedding")
    return Curve(curve_id, field, field.embed(curve.a[0]), field.embed(curve.b[0]))


def _verify_division_certificate(
    record: Mapping[str, Any],
    source: Curve,
    fields: Mapping[str, Field],
) -> dict[str, Any]:
    _exact_keys(
        record,
        ("label", "prime", "splitting_field_id", "division_polynomial", "lines", "canonical_kernel_line_id"),
        "CYCLIC_LINE_ENUMERATION_FAILURE",
    )
    label, prime = record["label"], record["prime"]
    failure = "Q_DIVISION_POLYNOMIAL_FAILURE" if label == "q" else "ELL_DIVISION_POLYNOMIAL_FAILURE"
    if label not in {"q", "ell"} or prime not in {2, 3}:
        raise CertificateError(failure, "unknown label or division prime")
    split = fields.get(record["splitting_field_id"])
    if split is None or split.p != source.field.p:
        raise CertificateError(failure, "unknown splitting field")
    lifted = _embedded_curve(source, split, f"{source.curve_id}@{split.field_id}")
    expected_base = _division_polynomial(source, prime)
    claimed = record["division_polynomial"]
    encoded_expected = [coefficient[0] for coefficient in expected_base]
    if claimed != encoded_expected:
        raise CertificateError(failure, "division polynomial coefficients mismatch")
    expected_poly = [split.embed(coefficient[0]) for coefficient in expected_base]
    lines = record["lines"]
    if not isinstance(lines, list) or len(lines) != prime + 1:
        raise CertificateError("CYCLIC_LINE_ENUMERATION_FAILURE", "line count mismatch")
    line_points: dict[str, tuple[Point, ...]] = {}
    seen_sets: set[tuple[bytes, ...]] = set()
    root_product = [split.one]
    image_by_id: dict[str, str] = {}
    stable_ids: list[str] = []
    for line in lines:
        _exact_keys(line, ("line_id", "generator", "points", "frobenius_image_line_id"), "CYCLIC_LINE_ENUMERATION_FAILURE")
        line_id = line["line_id"]
        if line_id in line_points:
            raise CertificateError("CYCLIC_LINE_ENUMERATION_FAILURE", "duplicate line id")
        generator = lifted.decode_point(line["generator"])
        if generator is None or lifted.mul(prime, generator) is not None:
            raise CertificateError("CYCLIC_LINE_ENUMERATION_FAILURE", "generator has wrong order")
        points = tuple(lifted.mul(multiplier, generator) for multiplier in range(1, prime))
        encoded_points = [lifted.encode_point(point) for point in points]
        if line["points"] != encoded_points:
            raise CertificateError("CYCLIC_LINE_ENUMERATION_FAILURE", "line is not generated cyclically")
        canonical_set = tuple(sorted((_point_key(lifted, point) for point in points)))
        if canonical_set in seen_sets:
            raise CertificateError("CYCLIC_LINE_ENUMERATION_FAILURE", "duplicate cyclic subgroup")
        seen_sets.add(canonical_set)
        line_points[line_id] = points
        image_by_id[line_id] = line["frobenius_image_line_id"]
        x = generator[0]
        if _poly_eval_field(expected_poly, x, split) != split.zero:
            raise CertificateError(failure, "line x-coordinate is not a division root")
        root_product = _mul_field_poly(root_product, [split.neg(x), split.one], split)
    point_sets = {
        line_id: tuple(sorted(_point_key(lifted, point) for point in points))
        for line_id, points in line_points.items()
    }
    for line_id, points in line_points.items():
        frobenius = tuple(
            sorted(
                _point_key(
                    lifted,
                    None
                    if point is None
                    else (split.pow(point[0], split.p), split.pow(point[1], split.p)),
                )
                for point in points
            )
        )
        matches = [candidate for candidate, point_set in point_sets.items() if point_set == frobenius]
        if len(matches) != 1 or image_by_id[line_id] != matches[0]:
            raise CertificateError("FROBENIUS_STABILITY_FAILURE", f"bad Frobenius image for {line_id}")
        if matches[0] == line_id:
            stable_ids.append(line_id)
    if _monic_field_poly(root_product, split) != _monic_field_poly(expected_poly, split):
        raise CertificateError("CYCLIC_LINE_ENUMERATION_FAILURE", "lines do not exhaust division polynomial")
    if not stable_ids:
        raise CertificateError("FROBENIUS_STABILITY_FAILURE", "no rational stable line")
    canonical = min(stable_ids, key=lambda item: _jcs_bytes([lifted.encode_point(p) for p in line_points[item]]))
    if record["canonical_kernel_line_id"] != canonical:
        raise CertificateError("KERNEL_CANONICALIZATION_FAILURE", "canonical stable kernel mismatch")
    selected = line_points[canonical]
    if any(any(coefficient != 0 for coefficient in coordinate[1:]) for point in selected if point for coordinate in point):
        raise CertificateError("KERNEL_CANONICALIZATION_FAILURE", "selected kernel is not base-rational")
    base_points: tuple[Point, ...] = tuple(
        None if point is None else ((point[0][0],), (point[1][0],)) for point in selected
    )
    return {
        "label": label,
        "prime": prime,
        "line_count": len(lines),
        "stable_line_ids": stable_ids,
        "canonical_line_id": canonical,
        "kernel_nonzero": base_points,
        "division_polynomial_sha256": _sha(claimed),
    }


def _velu_coefficients(curve: Curve, kernel_nonzero: Sequence[Point]) -> tuple[tuple[int, ...], tuple[int, ...]]:
    field = curve.field
    remaining = {(_point_key(curve, point), point) for point in kernel_nonzero}
    total_t, total_w = field.zero, field.zero
    while remaining:
        _, point = min(remaining, key=lambda pair: pair[0])
        assert point is not None
        neg = curve.neg(point)
        remaining.discard((_point_key(curve, point), point))
        remaining.discard((_point_key(curve, neg), neg))
        x, y = point
        g = field.add(field.mul(field.embed(3), field.pow(x, 2)), curve.a)
        if neg == point:
            t, u = g, field.zero
        else:
            t = field.mul(field.embed(2), g)
            u = field.pow(field.mul(field.embed(2), y), 2)
        total_t = field.add(total_t, t)
        total_w = field.add(total_w, field.add(u, field.mul(x, t)))
    return (
        field.sub(curve.a, field.mul(field.embed(5), total_t)),
        field.sub(curve.b, field.mul(field.embed(7), total_w)),
    )


def _velu_map(curve: Curve, kernel_nonzero: Sequence[Point], point: Point) -> Point:
    if point is None or point in kernel_nonzero:
        return None
    field = curve.field
    x_sum, y_sum = point
    for kernel_point in kernel_nonzero:
        assert kernel_point is not None
        translated = curve.add(point, kernel_point)
        if translated is None:
            raise CertificateError("VELU_CODOMAIN_FAILURE", "unexpected pole outside kernel")
        x_sum = field.add(x_sum, field.sub(translated[0], kernel_point[0]))
        y_sum = field.add(y_sum, field.sub(translated[1], kernel_point[1]))
    return x_sum, y_sum


def _isomorphic_point(field: Field, point: Point, u: tuple[int, ...]) -> Point:
    if point is None:
        return None
    return field.mul(field.pow(u, 2), point[0]), field.mul(field.pow(u, 3), point[1])


def _verify_isogeny(
    record: Mapping[str, Any],
    curves: Mapping[str, Curve],
    division: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    _exact_keys(
        record,
        ("isogeny_id", "label", "degree", "source_curve_id", "kernel_line_id", "codomain_curve_id", "velu_images", "dual"),
        "VELU_CODOMAIN_FAILURE",
    )
    label = record["label"]
    certificate = division.get(label)
    if certificate is None or record["degree"] != certificate["prime"] or record["kernel_line_id"] != certificate["canonical_line_id"]:
        raise CertificateError("KERNEL_CANONICALIZATION_FAILURE", "isogeny kernel binding mismatch")
    source = curves.get(record["source_curve_id"])
    codomain = curves.get(record["codomain_curve_id"])
    if source is None or codomain is None or source.field != codomain.field:
        raise CertificateError("VELU_CODOMAIN_FAILURE", "unknown or incompatible curve")
    kernel_nonzero = certificate["kernel_nonzero"]
    expected_a, expected_b = _velu_coefficients(source, kernel_nonzero)
    if (codomain.a, codomain.b) != (expected_a, expected_b):
        raise CertificateError("VELU_CODOMAIN_FAILURE", "Velu codomain coefficients mismatch")
    source_points = source.enumerate_points()
    expected_images = [
        {"source": source.encode_point(point), "image": codomain.encode_point(_velu_map(source, kernel_nonzero, point))}
        for point in source_points
    ]
    if record["velu_images"] != expected_images:
        raise CertificateError("VELU_CODOMAIN_FAILURE", "full Velu image table mismatch")
    if any(not codomain.on_curve(_velu_map(source, kernel_nonzero, point)) for point in source_points):
        raise CertificateError("VELU_CODOMAIN_FAILURE", "Velu image off codomain")
    dual = record["dual"]
    _exact_keys(dual, ("kernel_generator", "velu_codomain", "isomorphism_u"), "DUAL_COMPOSITION_FAILURE")
    generator = codomain.decode_point(dual["kernel_generator"])
    degree = record["degree"]
    if generator is None or codomain.mul(degree, generator) is not None:
        raise CertificateError("DUAL_COMPOSITION_FAILURE", "dual kernel generator order mismatch")
    dual_kernel = tuple(codomain.mul(multiplier, generator) for multiplier in range(1, degree))
    dual_a, dual_b = _velu_coefficients(codomain, dual_kernel)
    if dual["velu_codomain"] != {"a": codomain.field.encode(dual_a), "b": codomain.field.encode(dual_b)}:
        raise CertificateError("DUAL_COMPOSITION_FAILURE", "dual Velu codomain mismatch")
    intermediate = Curve(f"{record['isogeny_id']}:dual-codomain", source.field, dual_a, dual_b)
    u = source.field.decode(dual["isomorphism_u"])
    if u == source.field.zero:
        raise CertificateError("DUAL_COMPOSITION_FAILURE", "zero isomorphism scale")
    if source.field.mul(source.field.pow(u, 4), intermediate.a) != source.a or source.field.mul(source.field.pow(u, 6), intermediate.b) != source.b:
        raise CertificateError("DUAL_COMPOSITION_FAILURE", "dual codomain isomorphism mismatch")

    def forward(point: Point) -> Point:
        return _velu_map(source, kernel_nonzero, point)

    def backward(point: Point) -> Point:
        return _isomorphic_point(source.field, _velu_map(codomain, dual_kernel, point), u)

    for point in source_points:
        if backward(forward(point)) != source.mul(degree, point):
            raise CertificateError("DUAL_COMPOSITION_FAILURE", "dual o phi != [degree]")
    for point in codomain.enumerate_points():
        if forward(backward(point)) != codomain.mul(degree, point):
            raise CertificateError("DUAL_COMPOSITION_FAILURE", "phi o dual != [degree]")
    return {
        "isogeny_id": record["isogeny_id"],
        "label": label,
        "degree": degree,
        "source_curve_id": source.curve_id,
        "codomain_curve_id": codomain.curve_id,
        "velu_map_sha256": _sha(expected_images),
        "dual_compositions_checked": len(source_points) + len(codomain.enumerate_points()),
    }


def _fundamental_discriminant(discriminant: int) -> bool:
    if discriminant >= 0:
        return False

    def squarefree(value: int) -> bool:
        value = abs(value)
        for divisor in range(2, math.isqrt(value) + 1):
            if value % (divisor * divisor) == 0:
                return False
        return True

    if discriminant % 4 == 1:
        return squarefree(discriminant)
    if discriminant % 4 == 0:
        quotient = discriminant // 4
        return quotient % 4 in {2, 3} and squarefree(quotient)
    return False


def _valuation(value: int, prime: int) -> int:
    exponent = 0
    while value and value % prime == 0:
        exponent += 1
        value //= prime
    return exponent


def _verify_endomorphism_order(
    record: Mapping[str, Any], curve: Curve, order: int
) -> dict[str, Any]:
    _exact_keys(
        record,
        ("endpoint_id", "curve_id", "p", "trace", "frobenius_polynomial", "basis_matrix", "order_discriminant", "quadratic_field_discriminant", "conductor"),
        "END_RING_CERTIFICATE_FAILURE",
    )
    p = curve.field.p
    trace = p + 1 - order
    discriminant = trace * trace - 4 * p
    if record["endpoint_id"] != curve.curve_id or record["curve_id"] != curve.curve_id:
        raise CertificateError("END_RING_CERTIFICATE_FAILURE", "endpoint identity mismatch")
    if record["p"] != p or record["trace"] != trace or record["frobenius_polynomial"] != [p, -trace, 1]:
        raise CertificateError("END_RING_CERTIFICATE_FAILURE", "Frobenius polynomial mismatch")
    if record["basis_matrix"] != [[1, 0], [0, 1]]:
        raise CertificateError("END_RING_CERTIFICATE_FAILURE", "micro proof requires explicit Z[pi] basis")
    if record["order_discriminant"] != discriminant or not _fundamental_discriminant(discriminant):
        raise CertificateError("END_RING_CERTIFICATE_FAILURE", "Z[pi] is not verified maximal")
    if record["quadratic_field_discriminant"] != discriminant or record["conductor"] != 1:
        raise CertificateError("ENDPOINT_CONDUCTOR_FAILURE", "maximal-order conductor mismatch")
    return {
        "endpoint_id": curve.curve_id,
        "trace": trace,
        "order_discriminant": discriminant,
        "quadratic_field_discriminant": discriminant,
        "conductor": 1,
        "proof": "Z[pi]-basis-and-fundamental-discriminant",
    }


def _verify_whole_conductor(
    record: Mapping[str, Any],
    end_orders: Mapping[str, Mapping[str, Any]],
    isogenies: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    _exact_keys(record, ("q", "horizontal_ell", "f_pi", "endpoints", "correspondences"), "ENDPOINT_CONDUCTOR_FAILURE")
    q, ell = record["q"], record["horizontal_ell"]
    if q != 3 or ell != 2 or record["f_pi"] != 1:
        raise CertificateError("ENDPOINT_CONDUCTOR_FAILURE", "tiny fixture conductor parameters mismatch")
    endpoints = record["endpoints"]
    if not isinstance(endpoints, list) or {item.get("endpoint_id") for item in endpoints} != set(end_orders):
        raise CertificateError("ENDPOINT_CONDUCTOR_FAILURE", "endpoint set mismatch")
    local: dict[str, dict[int, int]] = {}
    for endpoint in endpoints:
        _exact_keys(endpoint, ("endpoint_id", "reported_conductor", "local_obligations"), "ENDPOINT_CONDUCTOR_FAILURE")
        endpoint_id = endpoint["endpoint_id"]
        conductor = end_orders[endpoint_id]["conductor"]
        if endpoint["reported_conductor"] != conductor:
            raise CertificateError("ENDPOINT_CONDUCTOR_FAILURE", endpoint_id)
        obligations = endpoint["local_obligations"]
        if not isinstance(obligations, list) or len(obligations) != 2:
            raise CertificateError("ENDPOINT_CONDUCTOR_FAILURE", "exact 2/q obligations required")
        observed: dict[int, int] = {}
        for obligation in obligations:
            _exact_keys(obligation, ("prime", "valuation"), "ENDPOINT_CONDUCTOR_FAILURE")
            prime = obligation["prime"]
            if prime in observed or prime not in {2, q}:
                raise CertificateError("ENDPOINT_CONDUCTOR_FAILURE", "duplicate or unknown local prime")
            value = _valuation(conductor, prime)
            if obligation["valuation"] != value:
                code = "D7_TWO_ADIC_CERTIFICATE_FAILURE" if prime == 2 else "D7_Q_ADIC_CERTIFICATE_FAILURE"
                raise CertificateError(code, endpoint_id)
            observed[prime] = value
        if set(observed) != {2, q}:
            raise CertificateError("ENDPOINT_CONDUCTOR_FAILURE", "missing 2/q obligation")
        local[endpoint_id] = observed
    correspondences = record["correspondences"]
    if not isinstance(correspondences, list) or len(correspondences) != len(isogenies):
        raise CertificateError("HORIZONTAL_WHOLE_CONDUCTOR_FAILURE", "correspondence count")
    seen: set[str] = set()
    for correspondence in correspondences:
        _exact_keys(correspondence, ("isogeny_id", "prime", "kind", "source_conductor", "codomain_conductor"), "HORIZONTAL_WHOLE_CONDUCTOR_FAILURE")
        isogeny = isogenies.get(correspondence["isogeny_id"])
        if isogeny is None or correspondence["isogeny_id"] in seen:
            raise CertificateError("HORIZONTAL_WHOLE_CONDUCTOR_FAILURE", "unknown or duplicate isogeny")
        seen.add(correspondence["isogeny_id"])
        source = end_orders[isogeny["source_curve_id"]]["conductor"]
        target = end_orders[isogeny["codomain_curve_id"]]["conductor"]
        expected_kind = "horizontal" if source == target else "vertical"
        if correspondence != {
            "isogeny_id": correspondence["isogeny_id"],
            "prime": isogeny["degree"],
            "kind": expected_kind,
            "source_conductor": source,
            "codomain_conductor": target,
        }:
            raise CertificateError("HORIZONTAL_WHOLE_CONDUCTOR_FAILURE", correspondence["isogeny_id"])
    return {"f_pi": 1, "endpoint_conductors": {key: 1 for key in sorted(end_orders)}, "local_valuations": local}


def verify_certificate(certificate: Mapping[str, Any]) -> dict[str, Any]:
    """Public total verifier: accept or raise a stable registered first failure."""
    if not isinstance(certificate, Mapping):
        raise CertificateError("FALSE_RECEIPT", "certificate object required")
    _reject_opaque_authority(certificate)
    _exact_keys(
        certificate,
        (
            "schema", "scope", "certificate_id", "exclusions", "fields", "curves",
            "order_certificate", "division_certificates", "isogenies",
            "endomorphism_orders", "whole_conductor",
        ),
        "FALSE_RECEIPT",
    )
    if certificate["schema"] != CERTIFICATE_SCHEMA or certificate["scope"] != SCOPE:
        raise CertificateError("FALSE_RECEIPT", "wrong certificate schema or scope")
    required_exclusions = {
        "scheduled-row", "40-60-bit-N", "target-access", "production-meter",
        "arithmetic-search", "GLV-rho-BSGS", "scientific-status",
    }
    if set(certificate["exclusions"]) != required_exclusions:
        raise CertificateError("POST_TARGET_GATE_FAILURE", "microfixture exclusion set mismatch")
    field_records = certificate["fields"]
    if not isinstance(field_records, list) or len(field_records) != 3:
        raise CertificateError("FIELD_CONSTRUCTION_FAILURE", "exact F7/F49/F343 fields required")
    fields: dict[str, Field] = {}
    for record in field_records:
        field = Field.from_record(record)
        if field.field_id in fields:
            raise CertificateError("FIELD_CONSTRUCTION_FAILURE", "duplicate field id")
        fields[field.field_id] = field
    if {(f.p, f.degree) for f in fields.values()} != {(7, 1), (7, 2), (7, 3)}:
        raise CertificateError("FIELD_CONSTRUCTION_FAILURE", "wrong tiny field tower")
    curve_records = certificate["curves"]
    if not isinstance(curve_records, list) or len(curve_records) != 4:
        raise CertificateError("CM_MODEL_ABSENT", "exact source/twist/two-codomain set required")
    curves: dict[str, Curve] = {}
    for record in curve_records:
        curve = Curve.from_record(record, fields)
        if curve.curve_id in curves:
            raise CertificateError("CM_MODEL_AMBIGUOUS", "duplicate curve id")
        curves[curve.curve_id] = curve
    order_record = certificate["order_certificate"]
    if isinstance(order_record, Mapping) and "order_N_point" not in order_record:
        raise CertificateError("ORDER_N_POINT_CERTIFICATE_FAILURE", "missing order-N point certificate")
    _exact_keys(
        order_record,
        ("source_curve_id", "model_identity", "method", "M", "trace", "N", "h", "order_N_point", "twist_curve_id", "twist_nonsquare", "twist_order"),
        "ORDER_CERTIFICATE_FAILURE",
    )
    source = curves.get(order_record["source_curve_id"])
    twist = curves.get(order_record["twist_curve_id"])
    if source is None or twist is None or source.field.degree != 1 or twist.field != source.field:
        raise CertificateError("ORDER_CERTIFICATE_FAILURE", "unknown source/twist")
    if order_record["method"] != "exhaustive-base-field-enumeration-v1":
        raise CertificateError("ORDER_CERTIFICATE_FAILURE", "unregistered order method")
    source_points = source.enumerate_points()
    M = len(source_points)
    trace = source.field.p + 1 - M
    if order_record["M"] != M or order_record["trace"] != trace:
        raise CertificateError("ORDER_CERTIFICATE_FAILURE", "point count/trace mismatch")
    model_identity = order_record["model_identity"]
    _exact_keys(model_identity, ("curve_id", "a", "b", "j_invariant"), "CM_MODEL_ABSENT")
    denominator = source.field.add(
        source.field.mul(source.field.embed(4), source.field.pow(source.a, 3)),
        source.field.mul(source.field.embed(27), source.field.pow(source.b, 2)),
    )
    j = source.field.div(
        source.field.mul(source.field.embed(1728 * 4), source.field.pow(source.a, 3)),
        denominator,
    )
    if model_identity != {"curve_id": source.curve_id, "a": source.field.encode(source.a), "b": source.field.encode(source.b), "j_invariant": source.field.encode(j)}:
        raise CertificateError("CM_MODEL_ABSENT", "curve/model identity mismatch")
    N, h = order_record["N"], order_record["h"]
    if not _prime(N) or M != h * N:
        raise CertificateError("ORDER_N_POINT_CERTIFICATE_FAILURE", "M=hN with prime N failed")
    point_n = source.decode_point(order_record["order_N_point"])
    if point_n is None or source.mul(N, point_n) is not None:
        raise CertificateError("ORDER_N_POINT_CERTIFICATE_FAILURE", "point does not have order N")
    d = source.field.decode(order_record["twist_nonsquare"])
    if d == source.field.zero or source.field.pow(d, (source.field.p - 1) // 2) != source.field.neg(source.field.one):
        raise CertificateError("TWIST_ORDER_MISMATCH", "twist scale is not a nonsquare")
    expected_twist = (
        source.field.mul(source.a, source.field.pow(d, 2)),
        source.field.mul(source.b, source.field.pow(d, 3)),
    )
    twist_order = len(twist.enumerate_points())
    if (twist.a, twist.b) != expected_twist or twist_order != 2 * source.field.p + 2 - M or order_record["twist_order"] != twist_order:
        raise CertificateError("TWIST_ORDER_MISMATCH", "twist identity/order mismatch")
    division_records = certificate["division_certificates"]
    if not isinstance(division_records, list) or len(division_records) != 2:
        raise CertificateError("CYCLIC_LINE_ENUMERATION_FAILURE", "exact q/ell certificates required")
    division: dict[str, Mapping[str, Any]] = {}
    for record in division_records:
        receipt = _verify_division_certificate(record, source, fields)
        if receipt["label"] in division:
            raise CertificateError("CYCLIC_LINE_ENUMERATION_FAILURE", "duplicate division label")
        division[receipt["label"]] = receipt
    if {label: receipt["prime"] for label, receipt in division.items()} != {"q": 3, "ell": 2}:
        raise CertificateError("CYCLIC_LINE_ENUMERATION_FAILURE", "q/ell labels mismatch")
    isogeny_records = certificate["isogenies"]
    if not isinstance(isogeny_records, list) or len(isogeny_records) != 2:
        raise CertificateError("VELU_CODOMAIN_FAILURE", "exact q/ell isogenies required")
    isogenies: dict[str, Mapping[str, Any]] = {}
    for record in isogeny_records:
        receipt = _verify_isogeny(record, curves, division)
        if receipt["isogeny_id"] in isogenies:
            raise CertificateError("VELU_CODOMAIN_FAILURE", "duplicate isogeny id")
        isogenies[receipt["isogeny_id"]] = receipt
    if {receipt["label"] for receipt in isogenies.values()} != {"q", "ell"}:
        raise CertificateError("VELU_CODOMAIN_FAILURE", "missing q/ell isogeny")
    endpoint_ids = {source.curve_id} | {receipt["codomain_curve_id"] for receipt in isogenies.values()}
    end_records = certificate["endomorphism_orders"]
    if not isinstance(end_records, list) or {record.get("endpoint_id") for record in end_records} != endpoint_ids:
        raise CertificateError("END_RING_CERTIFICATE_FAILURE", "endomorphism endpoint set mismatch")
    end_orders: dict[str, Mapping[str, Any]] = {}
    for record in end_records:
        curve = curves.get(record["curve_id"])
        if curve is None:
            raise CertificateError("END_RING_CERTIFICATE_FAILURE", "unknown endpoint curve")
        receipt = _verify_endomorphism_order(record, curve, len(curve.enumerate_points()))
        end_orders[receipt["endpoint_id"]] = receipt
    conductor = _verify_whole_conductor(certificate["whole_conductor"], end_orders, isogenies)
    return {
        "schema": REPLAY_SCHEMA,
        "certificate_id": certificate["certificate_id"],
        "status": "accepted",
        "scope": SCOPE,
        "field_ids": sorted(fields),
        "curve_ids": sorted(curves),
        "source_order": M,
        "source_trace": trace,
        "division": {key: {k: v for k, v in value.items() if k != "kernel_nonzero"} for key, value in sorted(division.items())},
        "isogenies": [isogenies[key] for key in sorted(isogenies)],
        "endomorphism_orders": [end_orders[key] for key in sorted(end_orders)],
        "whole_conductor": conductor,
        "certificate_sha256": _sha(certificate),
    }


def load_known_answer(path: Path | None = None) -> Mapping[str, Any]:
    fixture_path = path or Path(__file__).resolve().parent / "known-answer-fixtures.json"
    raw = json.loads(fixture_path.read_text(encoding="utf-8"))
    positives = raw.get("positive")
    if not isinstance(positives, list) or len(positives) != 1:
        raise CertificateError("FALSE_RECEIPT", "exactly one positive certificate required")
    return positives[0]["certificate"]


if __name__ == "__main__":
    raise SystemExit("static certificate library; downstream Executor owns conformance")
