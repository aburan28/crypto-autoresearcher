#!/usr/bin/env python3
"""Differentially test the m=51 C field arithmetic and x-only ladder.

This is a non-scientific implementation test.  It invokes only the scanner's
``reference-vectors`` mode; it never invokes ``scan`` and produces no research
observation.  The Python field backend uses direct bit-polynomial reduction
and polynomial extended Euclid, independently of the C CLMUL and Itoh--Tsujii
implementations.  The C x-only ladder is checked against lifted affine points
and an ordinary affine double-and-add scalar multiplication, not another
translation of the differential ladder.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import subprocess
import tempfile
from pathlib import Path


M = 51
FIELD_SIZE = 1 << M
FIELD_MASK = FIELD_SIZE - 1
FIELD_POLY = (1 << 51) | (1 << 6) | (1 << 3) | (1 << 1) | 1
NORD = 2_251_799_852_369_764
REFERENCE_HEADER = (
    "case_id",
    "mul_a",
    "mul_b",
    "inv_a",
    "curve_b",
    "x",
)
OUTPUT_HEADER = (
    "record_kind",
    "case_id",
    "mul_product",
    "inv_result",
    "kills_nord",
)
REFERENCE_BANNER = (
    b"REFERENCE-VECTORS ONLY: differential-test data, not scientific data\n"
)


class TestFailure(RuntimeError):
    """The C and independent Python implementations disagree."""


def poly_mod(value: int, modulus: int) -> int:
    modulus_degree = modulus.bit_length() - 1
    while value and value.bit_length() - 1 >= modulus_degree:
        value ^= modulus << (value.bit_length() - 1 - modulus_degree)
    return value


def poly_gcd(left: int, right: int) -> int:
    while right:
        left, right = right, poly_mod(left, right)
    return left


def gf_reduce(value: int) -> int:
    return poly_mod(value, FIELD_POLY)


def gf_mul(left: int, right: int) -> int:
    product = 0
    while right:
        if right & 1:
            product ^= left
        left <<= 1
        right >>= 1
    return gf_reduce(product)


def gf_square(value: int) -> int:
    return gf_mul(value, value)


def gf_inv(value: int) -> int:
    if value == 0:
        raise ValueError("zero has no field inverse")
    u, v = value, FIELD_POLY
    g_u, g_v = 1, 0
    while u != 1:
        shift = u.bit_length() - v.bit_length()
        if shift < 0:
            u, v = v, u
            g_u, g_v = g_v, g_u
            shift = -shift
        u ^= v << shift
        g_u ^= g_v << shift
    return gf_reduce(g_u)


def gf_trace(value: int) -> int:
    total = value
    power = value
    for _ in range(1, M):
        power = gf_square(power)
        total ^= power
    if total not in (0, 1):
        raise TestFailure("independent field trace did not land in GF(2)")
    return total


def verify_field_polynomial() -> None:
    """Rabin irreducibility test for the declared degree-51 modulus."""
    indeterminate = 0b10
    power = indeterminate
    for _ in range(M):
        power = gf_square(power)
    if power != indeterminate:
        raise TestFailure("field polynomial fails x^(2^m)-x Rabin check")
    for prime_divisor in (3, 17):
        power = indeterminate
        for _ in range(M // prime_divisor):
            power = gf_square(power)
        if poly_gcd(power ^ indeterminate, FIELD_POLY) != 1:
            raise TestFailure(
                f"field polynomial fails Rabin factor check {prime_divisor}"
            )


def gf_halftrace(value: int) -> int:
    result = value
    term = value
    for _ in range(1, (M - 1) // 2 + 1):
        term = gf_square(gf_square(term))
        result ^= term
    return result


def lift_point(curve_b: int, x: int) -> tuple[int, int]:
    if x == 0:
        y = curve_b
        for _ in range(M - 1):
            y = gf_square(y)
    else:
        rhs = x ^ gf_mul(curve_b, gf_inv(gf_square(x)))
        if gf_trace(rhs) != 0:
            raise TestFailure("fixed x has no point lift")
        z = gf_halftrace(rhs)
        if gf_square(z) ^ z != rhs:
            raise TestFailure("half-trace point lift failed")
        y = gf_mul(x, z)
    left = gf_square(y) ^ gf_mul(x, y)
    right = gf_mul(gf_square(x), x) ^ curve_b
    if left != right:
        raise TestFailure("lifted affine point is not on the curve")
    return x, y


def affine_double(point: tuple[int, int] | None) -> tuple[int, int] | None:
    if point is None or point[0] == 0:
        return None
    x, y = point
    slope = x ^ gf_mul(y, gf_inv(x))
    x_out = gf_square(slope) ^ slope
    y_out = gf_square(x) ^ gf_mul(slope ^ 1, x_out)
    return x_out, y_out


def affine_add(
    left: tuple[int, int] | None, right: tuple[int, int] | None
) -> tuple[int, int] | None:
    if left is None:
        return right
    if right is None:
        return left
    x_left, y_left = left
    x_right, y_right = right
    if x_left == x_right:
        if y_left == y_right:
            return affine_double(left)
        return None
    slope = gf_mul(y_left ^ y_right, gf_inv(x_left ^ x_right))
    x_out = gf_square(slope) ^ slope ^ x_left ^ x_right
    y_out = gf_mul(slope, x_left ^ x_out) ^ x_out ^ y_left
    return x_out, y_out


def affine_scalar_mul(
    point: tuple[int, int], scalar: int
) -> tuple[int, int] | None:
    result = None
    addend: tuple[int, int] | None = point
    while scalar:
        if scalar & 1:
            result = affine_add(result, addend)
        addend = affine_double(addend)
        scalar >>= 1
    return result


def affine_kills(curve_b: int, x: int) -> int:
    return int(affine_scalar_mul(lift_point(curve_b, x), NORD) is None)


def make_cases() -> list[dict[str, int]]:
    crater = 1
    floor_271 = 623_162_416_261
    curves = [
        (crater, 0),
        (crater, 1),
        (floor_271, 1),
        (2, 4),
        (3, 17),
        (5, 257),
        (0x12345, 65_539),
        (0x4ABCDE, 1_048_576),
        (0x123456789AB, 1_073_741_824),
        (FIELD_MASK, 1_099_511_627_776),
        (0x4000000000001, 562_949_953_421_315),
        (0x5555555555555, 1_125_899_906_842_633),
    ]
    multipliers = [
        (0, 0),
        (1, FIELD_MASK),
        (FIELD_MASK, FIELD_MASK),
        (1 << 50, 1 << 49),
        (0x123456789AB, 0x76543210FED),
        (0x4000000000001, 0x2000000000001),
        (0x5555555555555, 0x2AAAAAAAAAAAA),
        (0x7FFFFFFFFFFFF, 2),
        (0x1020304050607, 0x7010203040506),
        (17, NORD & FIELD_MASK),
        (271, 120_871),
        (FIELD_MASK - 1, FIELD_MASK - 2),
    ]
    inverses = [
        1,
        2,
        3,
        FIELD_MASK,
        0x123456789AB,
        0x4000000000001,
        0x5555555555555,
        17,
        271,
        120_871,
        1 << 50,
        FIELD_MASK - 1,
    ]
    cases = []
    for case_id, ((mul_a, mul_b), inv_a, (curve_b, x)) in enumerate(
        zip(multipliers, inverses, curves, strict=True)
    ):
        lift_point(curve_b, x)
        cases.append(
            {
                "case_id": case_id,
                "mul_a": mul_a,
                "mul_b": mul_b,
                "inv_a": inv_a,
                "curve_b": curve_b,
                "x": x,
            }
        )
    kill_values = {affine_kills(case["curve_b"], case["x"]) for case in cases}
    if kill_values != {0, 1}:
        raise TestFailure("fixed ladder vectors do not exercise both outcomes")
    return cases


def write_input(path: Path, cases: list[dict[str, int]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REFERENCE_HEADER, lineterminator="\n")
        writer.writeheader()
        writer.writerows(cases)


def canonical_uint(text: str) -> int:
    if not text or (text[0] == "0" and text != "0") or not text.isascii() or not text.isdigit():
        raise TestFailure(f"noncanonical output integer: {text!r}")
    return int(text)


def validate_output(path: Path, cases: list[dict[str, int]]) -> None:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != OUTPUT_HEADER:
            raise TestFailure("reference output header changed")
        rows = list(reader)
    if len(rows) != len(cases):
        raise TestFailure("reference output row count changed")
    for row, case in zip(rows, cases, strict=True):
        if None in row or any(value is None for value in row.values()):
            raise TestFailure("malformed reference output row")
        if row["record_kind"] != "REFERENCE_ONLY":
            raise TestFailure("reference-only tag is absent")
        observed = {
            field: canonical_uint(row[field])
            for field in ("case_id", "mul_product", "inv_result", "kills_nord")
        }
        expected = {
            "case_id": case["case_id"],
            "mul_product": gf_mul(case["mul_a"], case["mul_b"]),
            "inv_result": gf_inv(case["inv_a"]),
            "kills_nord": affine_kills(case["curve_b"], case["x"]),
        }
        if observed != expected:
            raise TestFailure(
                f"case {case['case_id']} differs: observed={observed}, expected={expected}"
            )
        if gf_mul(case["inv_a"], observed["inv_result"]) != 1:
            raise TestFailure(f"case {case['case_id']} inverse certificate failed")


def run_reference(binary: Path, input_path: Path, output_path: Path) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [str(binary), "reference-vectors", str(input_path), str(output_path)],
        check=False,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
    )


def test_malformed_inputs(binary: Path, directory: Path) -> None:
    header = ",".join(REFERENCE_HEADER) + "\n"
    malformed = {
        "bad_header": "wrong,header\n",
        "empty": header,
        "leading_zero": header + "00,1,1,1,1,1\n",
        "field_overflow": header + f"0,{FIELD_SIZE},1,1,1,1\n",
        "zero_inverse": header + "0,1,1,0,1,1\n",
        "singular_curve": header + "0,1,1,1,0,1\n",
        "extra_field": header + "0,1,1,1,1,1,1\n",
        "duplicate_id": header + "1,1,1,1,1,1\n1,2,2,2,2,2\n",
    }
    for name, content in malformed.items():
        input_path = directory / f"bad-{name}.csv"
        output_path = directory / f"bad-{name}-out.csv"
        input_path.write_text(content, encoding="ascii")
        result = run_reference(binary, input_path, output_path)
        if result.returncode == 0 or output_path.exists():
            raise TestFailure(f"malformed input {name} was accepted or retained output")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path, help="compiled search executable")
    args = parser.parse_args()
    binary = args.binary.resolve()
    if not binary.is_file():
        raise TestFailure(f"binary is not a regular file: {binary}")

    verify_field_polynomial()
    cases = make_cases()
    with tempfile.TemporaryDirectory(prefix="m51-sieve-reference-") as raw_dir:
        directory = Path(raw_dir)
        input_path = directory / "vectors.csv"
        output_path = directory / "results.csv"
        write_input(input_path, cases)
        result = run_reference(binary, input_path, output_path)
        if result.returncode != 0 or result.stdout or result.stderr != REFERENCE_BANNER:
            raise TestFailure(
                "reference invocation failed: "
                f"returncode={result.returncode}, stdout={result.stdout!r}, "
                f"stderr={result.stderr!r}"
            )
        validate_output(output_path, cases)

        original_hash = hashlib.sha256(output_path.read_bytes()).digest()
        repeated = run_reference(binary, input_path, output_path)
        if repeated.returncode == 0:
            raise TestFailure("reference output overwrite was accepted")
        if hashlib.sha256(output_path.read_bytes()).digest() != original_hash:
            raise TestFailure("failed overwrite changed the existing output")
        test_malformed_inputs(binary, directory)

    print(f"reference vectors ok: {len(cases)} cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
