#!/usr/bin/env python3
"""Permanent-blind replay for TASK-20260922-a5ab4c.

This implementation is intentionally self-contained.  It uses only the frozen
protocol, public inputs, public control artifacts, raw receipts, and raw-output
archive named in the task handoff.  It does not import or inspect experiment
source, the producer's checker, aggregate analysis, reports, or sibling review
artifacts.  Running it is review computation over saved public data; it does
not launch an experiment or benchmark.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
import statistics
import struct
import tarfile
from collections import Counter, defaultdict
from pathlib import Path


SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[3]
P9 = REPO / "research/pair_reuse_20260922"
R9 = REPO / "experiments/EXP-KIC-d9c828/runs/RUN-KIC-ba86d9"
OUT = P9 / "review/blind_results.json"


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(1 << 20)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def point(value):
    return None if value is None else (int(value[0]), int(value[1]))


def point_json(value):
    return None if value is None else [value[0], value[1]]


class Checks:
    def __init__(self):
        self.total = 0
        self.failed = 0
        self.failures: list[str] = []

    def expect(self, condition: bool, label: str):
        self.total += 1
        if not condition:
            self.failed += 1
            if len(self.failures) < 250:
                self.failures.append(label)

    def equal(self, actual, expected, label: str):
        self.expect(actual == expected, f"{label}: actual={actual!r} expected={expected!r}")


def polynomial_mod(dividend: int, divisor: int) -> int:
    degree = divisor.bit_length() - 1
    while dividend and dividend.bit_length() - 1 >= degree:
        dividend ^= divisor << (dividend.bit_length() - 1 - degree)
    return dividend


def polynomial_gcd(left: int, right: int) -> int:
    while right:
        left, right = right, polynomial_mod(left, right)
    return left


def prime_divisors(value: int) -> list[int]:
    result = []
    candidate = 2
    while candidate * candidate <= value:
        if value % candidate == 0:
            result.append(candidate)
            while value % candidate == 0:
                value //= candidate
        candidate += 1
    if value > 1:
        result.append(value)
    return result


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    if value % 2 == 0:
        return value == 2
    divisor = 3
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 2
    return True


class BinaryCurve:
    """GF(2^n) polynomial arithmetic and y^2+xy=x^3+a*x^2+b."""

    def __init__(self, n: int, modulus: int, a: int, b: int, r: int):
        self.n = n
        self.modulus = modulus
        self.a = a
        self.b = b
        self.r = r
        self.mask = (1 << n) - 1

    def mul(self, left: int, right: int) -> int:
        result = 0
        while right:
            if right & 1:
                result ^= left
            right >>= 1
            left <<= 1
            if left & (1 << self.n):
                left ^= self.modulus
        return result & self.mask

    def square(self, value: int) -> int:
        return self.mul(value, value)

    def pow(self, value: int, exponent: int) -> int:
        result = 1
        while exponent:
            if exponent & 1:
                result = self.mul(result, value)
            exponent >>= 1
            if exponent:
                value = self.square(value)
        return result

    def inv(self, value: int) -> int:
        if value == 0:
            raise ZeroDivisionError("zero has no field inverse")
        return self.pow(value, (1 << self.n) - 2)

    def div(self, numerator: int, denominator: int) -> int:
        return self.mul(numerator, self.inv(denominator))

    def irreducible(self) -> bool:
        x_poly = 2
        value = x_poly
        for _ in range(self.n):
            value = self.square(value)
        if value != x_poly:
            return False
        for divisor in prime_divisors(self.n):
            value = x_poly
            for _ in range(self.n // divisor):
                value = self.square(value)
            if polynomial_gcd(value ^ x_poly, self.modulus) != 1:
                return False
        return True

    def on_curve(self, p) -> bool:
        if p is None:
            return True
        x, y = p
        left = self.square(y) ^ self.mul(x, y)
        x2 = self.square(x)
        right = self.mul(x2, x) ^ self.mul(self.a, x2) ^ self.b
        return left == right

    def neg(self, p):
        if p is None:
            return None
        return (p[0], p[0] ^ p[1])

    def add(self, p, q):
        if p is None:
            return q
        if q is None:
            return p
        x1, y1 = p
        x2, y2 = q
        if x1 == x2:
            if (y1 ^ y2) == x1:
                return None
            if p != q:
                raise AssertionError("same x has neither equal nor inverse y")
            if x1 == 0:
                return None
            slope = x1 ^ self.div(y1, x1)
            x3 = self.square(slope) ^ slope ^ self.a
            y3 = self.square(x1) ^ self.mul(slope ^ 1, x3)
            return (x3, y3)
        slope = self.div(y1 ^ y2, x1 ^ x2)
        x3 = self.square(slope) ^ slope ^ x1 ^ x2 ^ self.a
        y3 = self.mul(slope, x1 ^ x3) ^ x3 ^ y1
        return (x3, y3)

    def scalar(self, multiple: int, p):
        result = None
        addend = p
        while multiple:
            if multiple & 1:
                result = self.add(result, addend)
            multiple >>= 1
            if multiple:
                addend = self.add(addend, addend)
        return result

    def frobenius(self, p, shift: int = 1):
        if p is None:
            return None
        shift %= self.n
        x, y = p
        for _ in range(shift):
            x = self.square(x)
            y = self.square(y)
        return (x, y)

    def halftrace(self, value: int) -> int:
        result = 0
        term = value
        for _ in range((self.n + 1) // 2):
            result ^= term
            term = self.square(self.square(term))
        return result

    def lift_x(self, x: int):
        if x == 0:
            return (0, 1)
        c = x ^ self.a ^ self.div(self.b, self.square(x))
        w = self.halftrace(c)
        if self.square(w) ^ w != c:
            return None
        y = self.mul(x, w)
        y_other = y ^ x
        return (x, min(y, y_other))

    def generator(self):
        for x in range(1, 4096):
            p = self.lift_x(x)
            if p is None:
                continue
            candidate = self.add(p, p)
            if candidate is not None and self.scalar(self.r, candidate) is None:
                return candidate
        raise AssertionError("generator scan exhausted")


def matrix_rank(columns: list[int], n: int) -> int:
    rows = list(columns)
    rank = 0
    for bit in range(n - 1, -1, -1):
        pivot = next((i for i in range(rank, len(rows)) if (rows[i] >> bit) & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(len(rows)):
            if i != rank and ((rows[i] >> bit) & 1):
                rows[i] ^= rows[rank]
        rank += 1
    return rank


def invert_binary_columns(columns: list[int], n: int) -> tuple[list[int], list[int]]:
    rows = []
    for output_bit in range(n):
        left = sum(((columns[column] >> output_bit) & 1) << column for column in range(n))
        rows.append(left | (1 << (n + output_bit)))
    for column in range(n):
        pivot = next((row for row in range(column, n) if (rows[row] >> column) & 1), None)
        if pivot is None:
            raise AssertionError("normal basis matrix is singular")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        for row in range(n):
            if row != column and ((rows[row] >> column) & 1):
                rows[row] ^= rows[column]
    inverse_rows = [(row >> n) & ((1 << n) - 1) for row in rows]
    inverse_columns = []
    for input_bit in range(n):
        inverse_columns.append(sum(((inverse_rows[row] >> input_bit) & 1) << row for row in range(n)))
    return inverse_rows, inverse_columns


def least_normal_basis(curve: BinaryCurve):
    for beta in range(1, 1 << curve.n):
        columns = []
        value = beta
        for _ in range(curve.n):
            columns.append(value)
            value = curve.square(value)
        if matrix_rank(columns, curve.n) == curve.n:
            inverse_rows, inverse_columns = invert_binary_columns(columns, curve.n)
            return beta, columns, inverse_rows, inverse_columns
    raise AssertionError("no normal element found")


def to_normal(value: int, inverse_rows: list[int]) -> int:
    result = 0
    for bit, row in enumerate(inverse_rows):
        result |= ((row & value).bit_count() & 1) << bit
    return result


def rotate_left(value: int, shift: int, width: int) -> int:
    shift %= width
    mask = (1 << width) - 1
    if shift == 0:
        return value & mask
    return ((value << shift) & mask) | (value >> (width - shift))


def canonical_frame(curve: BinaryCurve, inverse_rows: list[int], p):
    if p is None:
        return ("infinity", None), None, (0, 1)
    normal_x = to_normal(p[0], inverse_rows)
    key_value, shift = min((rotate_left(normal_x, k, curve.n), k) for k in range(curve.n))
    normalized = curve.frobenius(p, shift)
    # The frozen representation canonicalizes the x orbit only.  Its one row
    # per x orbit is then chosen by the lexicographically least unordered pair
    # below.  The opposite y branch is handled at query time as a sign match;
    # imposing a numeric-y convention here would be an extra, undeclared rule.
    return ("normal_x", key_value), normalized, (shift, 1)


def reconstruct_seed_points(curve: BinaryCurve, regime_id: str, n19_input: dict):
    if regime_id == "n19_k4":
        return [point(entry["point"]) for entry in n19_input["seed_points"]], [
            entry["pool_orbit_index"] for entry in n19_input["seed_points"]
        ]
    seeds = []
    candidate_indices = []
    labels = set()
    for index in range(4096):
        digest = hashlib.sha256(f"PAIR-REUSE-v1-base-n23-{index}".encode()).digest()
        x = int.from_bytes(digest[:8], "little") % (1 << curve.n)
        if x == 0:
            continue
        p = curve.lift_x(x)
        if p is None or curve.scalar(curve.r, p) is not None:
            continue
        orbit = [curve.frobenius(p, k) for k in range(curve.n)]
        label = min(value[0] for value in orbit)
        if label in labels:
            continue
        signed_orbit = {value for member in orbit for value in (member, curve.neg(member))}
        if len(signed_orbit) != 2 * curve.n:
            continue
        labels.add(label)
        seeds.append(p)
        candidate_indices.append(index)
        if len(seeds) == 16:
            return seeds, candidate_indices
    raise AssertionError("n23 seed scan exhausted before 16 orbits")


def expand_base(curve: BinaryCurve, seeds: list):
    expanded = {member for seed in seeds for k in range(curve.n)
                for member in (curve.frobenius(seed, k), curve.neg(curve.frobenius(seed, k)))}
    return sorted(expanded)


def build_pair_map(curve: BinaryCurve, base: list):
    mapping = {}
    additions = 0
    for i, left in enumerate(base):
        for j in range(i, len(base)):
            total = curve.add(left, base[j])
            additions += 1
            mapping.setdefault(total, (left, base[j]))
    return mapping, additions


def build_canonical_rows(curve: BinaryCurve, seeds: list, inverse_rows: list[int]):
    rows = {}
    additions = 0
    for i, left in enumerate(seeds):
        for j in range(i, len(seeds)):
            for relative_shift in range(curve.n):
                shifted = curve.frobenius(seeds[j], relative_shift)
                for anchor_sign in (1, -1):
                    right = shifted if anchor_sign == 1 else curve.neg(shifted)
                    total = curve.add(left, right)
                    additions += 1
                    key, normalized_sum, (frame_shift, frame_sign) = canonical_frame(
                        curve, inverse_rows, total
                    )
                    normalized_left = curve.frobenius(left, frame_shift)
                    normalized_right = curve.frobenius(right, frame_shift)
                    normalized_left, normalized_right = sorted((normalized_left, normalized_right))
                    candidate = {
                        "key": {"kind": key[0], "value": key[1]},
                        "normalized_endpoints": [point_json(normalized_left), point_json(normalized_right)],
                        "stored_sum": point_json(curve.add(normalized_left, normalized_right)),
                        "anchor": [i, j, relative_shift, anchor_sign],
                        "source_frame": [frame_shift, frame_sign],
                    }
                    previous = rows.get(key)
                    if previous is None or (normalized_left, normalized_right) < tuple(
                        point(value) for value in previous["normalized_endpoints"]
                    ):
                        rows[key] = candidate
    return rows, additions


def canonical_support(curve: BinaryCurve, rows: dict):
    support = set()
    for row in rows.values():
        stored_sum = point(row["stored_sum"])
        for shift in range(curve.n):
            moved = curve.frobenius(stored_sum, shift)
            support.add(moved)
            support.add(curve.neg(moved))
    return support


def recover_canonical_pair(curve: BinaryCurve, inverse_rows: list[int], rows: dict, total):
    key, normalized_sum, (frame_shift, frame_sign) = canonical_frame(curve, inverse_rows, total)
    row = rows.get(key)
    if row is None:
        return None
    stored_sum = point(row["stored_sum"])
    if stored_sum == normalized_sum:
        transport_sign = 1
    elif stored_sum == curve.neg(normalized_sum):
        transport_sign = -1
    else:
        return None
    recovered = []
    for endpoint_json in row["normalized_endpoints"]:
        endpoint = point(endpoint_json)
        if transport_sign == -1:
            endpoint = curve.neg(endpoint)
        endpoint = curve.frobenius(endpoint, (-frame_shift) % curve.n)
        recovered.append(endpoint)
    if curve.add(recovered[0], recovered[1]) != total:
        return None
    return tuple(recovered)


def direct_query(curve: BinaryCurve, base: list, pair_map: dict, canonical_rows: dict,
                 inverse_rows: list[int], q):
    for third_index, third in enumerate(base):
        residual = curve.add(q, curve.neg(third))
        pair = pair_map.get(residual)
        if pair is None:
            continue
        canonical_pair = recover_canonical_pair(curve, inverse_rows, canonical_rows, residual)
        if canonical_pair is None:
            raise AssertionError("expanded support member lacks canonical transport")
        return {
            "status": "SAT",
            "third_index": third_index,
            "probes": third_index + 1,
            "expanded_witness": [point_json(pair[0]), point_json(pair[1]), point_json(third)],
            "canonical_witness": [point_json(canonical_pair[0]), point_json(canonical_pair[1]), point_json(third)],
        }
    return {
        "status": "UNSAT",
        "third_index": -1,
        "probes": len(base),
        "expanded_witness": None,
        "canonical_witness": None,
    }


def arm_result(expected: dict, arm: str):
    hit = expected["status"] == "SAT"
    return {
        "status": expected["status"],
        "third_index": expected["third_index"],
        "probes": expected["probes"],
        "canonicalizations": expected["probes"] if arm == "canonical_normal_x" else 0,
        "transport_rows_examined": 1 if hit else 0,
        "witness": expected["canonical_witness"] if arm == "canonical_normal_x"
        else expected["expanded_witness"],
    }


def generate_panels(curve: BinaryCurve, regime_id: str, generator):
    panel_scalars = []
    panels = []
    for panel_index in range(8):
        scalars = []
        seen = set()
        counter = 0
        while len(scalars) < 512:
            digest = hashlib.sha256(
                f"PAIR-REUSE-v1-target-{regime_id}-{panel_index}-{counter}".encode()
            ).digest()
            scalar = 1 + int.from_bytes(digest[:8], "little") % (curve.r - 1)
            counter += 1
            if scalar in seen:
                continue
            seen.add(scalar)
            scalars.append(scalar)
        panel_scalars.append(scalars)
        panels.append([curve.scalar(scalar, generator) for scalar in scalars])
    return panel_scalars, panels


def membership_probe_points(curve: BinaryCurve, regime_id: str, generator):
    result = []
    for index in range(4096):
        digest = hashlib.sha256(f"PAIR-REUSE-v1-member-{regime_id}-{index}".encode()).digest()
        scalar = 1 + int.from_bytes(digest[:8], "little") % (curve.r - 1)
        result.append(curve.scalar(scalar, generator))
    return result


def packed_support_hashes(support: set, n: int):
    encodings = {}
    affine = [value for value in support if value is not None]
    for layout, shift, xy in (
        ("x_low_y_high_shift_n", n, True),
        ("y_low_x_high_shift_n", n, False),
        ("x_low_y_high_shift_32", 32, True),
        ("y_low_x_high_shift_32", 32, False),
    ):
        packed_affine = [
            (p[0] | (p[1] << shift)) if xy else (p[1] | (p[0] << shift))
            for p in affine
        ]
        for infinity_name, infinity_value in (
            ("u64_max", (1 << 64) - 1),
            ("high_bit", 1 << 63),
            ("after_affine_bits", 1 << (2 * n)),
            ("zero", 0),
        ):
            values = list(packed_affine)
            if None in support:
                values.append(infinity_value)
            payload = b"".join(struct.pack("<Q", value) for value in sorted(values))
            encodings[f"{layout}_infinity_{infinity_name}"] = sha256_bytes(payload)
    return encodings


def type7(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def summarize_numbers(values: list[float]):
    return {
        "count": len(values),
        "min": min(values),
        "median": statistics.median(values),
        "max": max(values),
        "sum": sum(values),
    }


def main():
    checks = Checks()
    protocol_path = P9 / "protocol.json"
    base_input_path = P9 / "inputs/n19_base.json"
    schedule_path = P9 / "inputs/schedule.json"
    bindings_path = P9 / "inputs/bindings.json"
    protocol = load_json(protocol_path)
    n19_input = load_json(base_input_path)
    schedule = load_json(schedule_path)
    bindings = load_json(bindings_path)

    checks.equal(protocol["experiment_id"], "EXP-KIC-d9c828", "protocol experiment id")
    checks.equal(protocol["run_id"], "RUN-KIC-ba86d9", "protocol run id")
    checks.equal(sha256_file(base_input_path), protocol["inputs"]["n19_base_sha256"], "n19 input hash")
    checks.equal(sha256_file(schedule_path), protocol["inputs"]["schedule_sha256"], "schedule hash")
    checks.equal(bindings["base_sha256"], protocol["inputs"]["n19_base_sha256"], "binding base hash")

    bases_doc = load_json(R9 / "bases.json")
    panels_doc = load_json(R9 / "public_panels.json")
    panel_files_doc = load_json(R9 / "panel_files.json")
    oracle_doc = load_json(R9 / "oracle_metadata.json")
    pair_tables_doc = load_json(R9 / "pair_tables.json")
    controls_doc = load_json(R9 / "control_queries.json")
    native_controls_doc = load_json(R9 / "native_controls.json")
    control_receipt = load_json(R9 / "control_receipt.json")
    checker_receipt = load_json(R9 / "checker_receipt.json")
    raw_manifest = load_json(R9 / "raw_manifest.json")

    saved_bases = {entry["id"]: entry for entry in bases_doc["regimes"]}
    saved_panels = {entry["id"]: entry["panels"] for entry in panels_doc["regimes"]}
    saved_oracles = {entry["id"]: entry for entry in oracle_doc["regimes"]}
    saved_tables = {entry["id"]: entry for entry in pair_tables_doc["regimes"]}
    saved_controls = {entry["id"]: entry for entry in controls_doc["regimes"]}
    saved_native = {entry["id"]: entry for entry in native_controls_doc["regimes"]}

    regime_state = {}
    regime_results = {}
    for regime_spec in protocol["regimes"]:
        regime_id = regime_spec["id"]
        curve = BinaryCurve(
            regime_spec["n"], regime_spec["modulus"], regime_spec["a"],
            regime_spec["b"], regime_spec["r"]
        )
        trace_previous, trace_current = 2, 1
        for _ in range(2, curve.n + 1):
            trace_previous, trace_current = trace_current, trace_current - 2 * trace_previous
        derived_order = (1 << curve.n) + 1 - trace_current
        checks.expect(curve.irreducible(), f"{regime_id} field polynomial irreducible")
        checks.expect(is_prime(curve.r), f"{regime_id} r prime")
        checks.equal(derived_order, regime_spec["curve_order"], f"{regime_id} trace-derived order")
        checks.equal(derived_order, 2 * curve.r, f"{regime_id} cofactor two order")

        generator = curve.generator()
        checks.equal(point_json(generator), saved_bases[regime_id]["generator"], f"{regime_id} public G")
        checks.expect(curve.on_curve(generator), f"{regime_id} G on curve")
        checks.expect(curve.scalar(curve.r, generator) is None, f"{regime_id} G r subgroup")

        seeds, candidate_indices = reconstruct_seed_points(curve, regime_id, n19_input)
        base = expand_base(curve, seeds)
        checks.equal([point_json(p) for p in seeds], saved_bases[regime_id]["seeds"], f"{regime_id} seeds")
        checks.equal(candidate_indices, saved_bases[regime_id]["candidate_indices"], f"{regime_id} candidate indices")
        checks.equal([point_json(p) for p in base], saved_bases[regime_id]["points"], f"{regime_id} expanded base")
        checks.equal(len(base), regime_spec["expected_points"], f"{regime_id} base size")
        checks.expect(all(curve.on_curve(p) and curve.scalar(curve.r, p) is None for p in base),
                      f"{regime_id} all base points valid subgroup points")
        checks.expect(all(curve.frobenius(p) in set(base) and curve.neg(p) in set(base) for p in base),
                      f"{regime_id} signed Frobenius closure")

        beta, columns, inverse_rows, inverse_columns = least_normal_basis(curve)
        saved_normal = saved_bases[regime_id]["normal"]
        checks.equal(beta, saved_normal["beta"], f"{regime_id} least normal beta")
        checks.equal(columns, saved_normal["columns"], f"{regime_id} normal columns")
        checks.equal(inverse_columns, saved_normal["inverse_columns"], f"{regime_id} inverse normal columns")
        checks.equal((curve.n + 3) // 4, saved_normal["nibble_chunks"], f"{regime_id} nibble chunks")
        for basis_bit in range(curve.n):
            polynomial_value = columns[basis_bit]
            checks.equal(to_normal(polynomial_value, inverse_rows), 1 << basis_bit,
                         f"{regime_id} normal roundtrip basis {basis_bit}")
        for sample in (0, 1, 2, 3, curve.mask, generator[0], generator[1]):
            normal = to_normal(sample, inverse_rows)
            checks.equal(to_normal(curve.square(sample), inverse_rows), rotate_left(normal, 1, curve.n),
                         f"{regime_id} Frobenius normal rotation sample {sample}")

        pair_map, unordered_pairs = build_pair_map(curve, base)
        canonical_rows, anchored_pairs = build_canonical_rows(curve, seeds, inverse_rows)
        support_from_rows = canonical_support(curve, canonical_rows)
        checks.equal(unordered_pairs, len(base) * (len(base) + 1) // 2,
                     f"{regime_id} unordered-pair enumeration")
        checks.equal(support_from_rows, set(pair_map), f"{regime_id} canonical orbit expansion support")

        saved_table = saved_tables[regime_id]
        checks.equal(len(pair_map), saved_table["expanded"]["stats"]["keys"],
                     f"{regime_id} expanded distinct key count")
        checks.equal(unordered_pairs, saved_table["expanded"]["stats"]["anchor_additions"],
                     f"{regime_id} expanded addition count")
        checks.equal(len(canonical_rows), saved_table["canonical_normal_x"]["stats"]["keys"],
                     f"{regime_id} canonical key count")
        checks.equal(anchored_pairs, saved_table["canonical_normal_x"]["stats"]["anchor_additions"],
                     f"{regime_id} anchored addition count")
        saved_rows = {
            (row["key"]["kind"], row["key"]["value"]): row
            for row in saved_table["canonical_normal_x"]["rows"]
        }
        checks.equal(set(saved_rows), set(canonical_rows), f"{regime_id} canonical row key set")
        for key, expected_row in canonical_rows.items():
            checks.equal(saved_rows.get(key), expected_row, f"{regime_id} canonical row {key}")
        hash_candidates = packed_support_hashes(set(pair_map), curve.n)
        expected_key_hash = saved_table["expanded"]["sorted_packed_keys_le64_sha256"]
        matching_encodings = [name for name, value in hash_candidates.items() if value == expected_key_hash]
        checks.expect(bool(matching_encodings), f"{regime_id} sorted packed expanded-key hash")

        panel_scalars, panels = generate_panels(curve, regime_id, generator)
        checks.equal(panel_scalars, saved_oracles[regime_id]["panel_scalars"], f"{regime_id} panel scalars")
        checks.equal([[point_json(p) for p in panel] for panel in panels], saved_panels[regime_id],
                     f"{regime_id} public panels")
        for panel_index, panel_values in enumerate(panels):
            panel_path = R9 / f"panels/{regime_id}_panel_{panel_index}.json"
            panel_doc = load_json(panel_path)
            checks.equal(panel_doc["regime"], regime_id, f"{regime_id} panel file regime {panel_index}")
            checks.equal(panel_doc["panel"], panel_index, f"{regime_id} panel file index {panel_index}")
            checks.equal(panel_doc["points"], [point_json(p) for p in panel_values],
                         f"{regime_id} panel file points {panel_index}")

        unique_query_results = []
        saved_control = saved_controls[regime_id]
        for panel_index, panel_values in enumerate(panels):
            saved_panel_queries = saved_control["panels"][panel_index]
            checks.equal(len(saved_panel_queries), 512, f"{regime_id} saved panel query count {panel_index}")
            for query_index, q in enumerate(panel_values):
                expected = direct_query(curve, base, pair_map, canonical_rows, inverse_rows, q)
                unique_query_results.append(expected)
                entry = saved_panel_queries[query_index]
                checks.equal(entry["index"], query_index, f"{regime_id} panel {panel_index} query index {query_index}")
                checks.equal(point(entry["Q"]), q, f"{regime_id} panel {panel_index} Q {query_index}")
                for arm in ("expanded", "canonical_normal_x"):
                    checks.equal(entry[arm], arm_result(expected, arm),
                                 f"{regime_id} panel {panel_index} query {query_index} {arm}")

        exception_targets = [None] + base
        checks.equal(len(saved_control["exceptions"]), len(exception_targets), f"{regime_id} exception count")
        for query_index, q in enumerate(exception_targets):
            expected = direct_query(curve, base, pair_map, canonical_rows, inverse_rows, q)
            entry = saved_control["exceptions"][query_index]
            checks.equal(entry["index"], query_index, f"{regime_id} exception index {query_index}")
            checks.equal(point(entry["Q"]), q, f"{regime_id} exception Q {query_index}")
            for arm in ("expanded", "canonical_normal_x"):
                checks.equal(entry[arm], arm_result(expected, arm),
                             f"{regime_id} exception {query_index} {arm}")

        probe_points = membership_probe_points(curve, regime_id, generator)
        saved_probes = saved_control["membership_probes"]
        checks.equal(len(saved_probes), 4096, f"{regime_id} membership probe count")
        membership_true = 0
        for index, q in enumerate(probe_points):
            entry = saved_probes[index]
            member = q in pair_map
            membership_true += int(member)
            expanded_pair = pair_map.get(q)
            canonical_pair = recover_canonical_pair(curve, inverse_rows, canonical_rows, q) if member else None
            checks.equal(entry["index"], index, f"{regime_id} membership index {index}")
            checks.equal(point(entry["Q"]), q, f"{regime_id} membership Q {index}")
            checks.equal(entry["member"], member, f"{regime_id} membership decision {index}")
            checks.equal(entry["expanded_witness"],
                         None if expanded_pair is None else [point_json(p) for p in expanded_pair],
                         f"{regime_id} expanded membership witness {index}")
            checks.equal(entry["canonical_witness"],
                         None if canonical_pair is None else [point_json(p) for p in canonical_pair],
                         f"{regime_id} canonical membership witness {index}")

        false_controls = saved_native[regime_id]["forgeries"]
        target = point(false_controls["target"])
        wrong_inverse = [point(p) for p in false_controls["wrong_inverse_endpoints"]]
        wrong_sign = [point(p) for p in false_controls["wrong_sign_endpoints"]]
        offcurve_q = point(false_controls["offcurve_Q"])
        replacement = point(false_controls["replacement"])
        genuine_key, _, _ = canonical_frame(curve, inverse_rows, target)
        checks.expect(curve.add(wrong_inverse[0], wrong_inverse[1]) != target,
                      f"{regime_id} wrong-inverse certificate is false")
        checks.expect(curve.add(wrong_sign[0], wrong_sign[1]) != target,
                      f"{regime_id} wrong-sign certificate is false")
        checks.expect(not curve.on_curve(offcurve_q), f"{regime_id} off-curve Q is off curve")
        checks.expect(curve.on_curve(replacement) and curve.scalar(curve.r, replacement) is None,
                      f"{regime_id} replacement is a valid subgroup point")
        checks.expect(replacement not in set(base), f"{regime_id} replacement lies outside B")
        checks.equal(genuine_key[1], false_controls["genuine_table_key"],
                     f"{regime_id} genuine table key")
        checks.expect(false_controls["wrong_table_key_value"] != false_controls["genuine_table_key"],
                      f"{regime_id} wrong table key differs")
        checks.expect(point(false_controls["wrong_stored_sum_value"]) != point(canonical_rows[genuine_key]["stored_sum"]),
                      f"{regime_id} wrong stored sum differs")
        for named_flag in (
            "wrong_inverse_shift_plus_one", "wrong_sign", "wrong_table_key", "wrong_stored_sum",
            "offcurve_Q_rejected", "one_point_removed_base", "same_cardinality_noninvariant_base",
        ):
            checks.expect(false_controls[named_flag] is True, f"{regime_id} recorded forgery flag {named_flag}")

        unique_status = Counter(result["status"] for result in unique_query_results)
        unique_probes = [result["probes"] for result in unique_query_results]
        cross_panel_scalars = [scalar for panel in panel_scalars for scalar in panel]
        regime_results[regime_id] = {
            "field": {
                "n": curve.n,
                "modulus": curve.modulus,
                "irreducible": True,
                "trace": trace_current,
                "curve_order": derived_order,
                "r": curve.r,
                "r_prime": True,
            },
            "public_generator": point_json(generator),
            "base": {
                "seed_count": len(seeds),
                "candidate_indices": candidate_indices,
                "signed_points": len(base),
                "frobenius_and_sign_closed": True,
            },
            "normal_basis": {
                "least_beta": beta,
                "rank": matrix_rank(columns, curve.n),
                "nibble_chunks": (curve.n + 3) // 4,
            },
            "pair_sets": {
                "unordered_pairs": unordered_pairs,
                "expanded_distinct_sums": len(pair_map),
                "anchored_pairs": anchored_pairs,
                "canonical_rows": len(canonical_rows),
                "canonical_orbit_expansion_distinct_sums": len(support_from_rows),
                "support_equal": support_from_rows == set(pair_map),
                "saved_rows_exact": set(saved_rows) == set(canonical_rows) and all(
                    saved_rows.get(key) == value for key, value in canonical_rows.items()
                ),
                "packed_hash_matching_encodings": matching_encodings,
            },
            "panels": {
                "count": len(panels),
                "length_each": len(panels[0]),
                "unique_scalars_within_each": [len(set(values)) for values in panel_scalars],
                "unique_scalars_across_all_panels": len(set(cross_panel_scalars)),
                "cross_panel_repetitions": len(cross_panel_scalars) - len(set(cross_panel_scalars)),
            },
            "unique_public_panel_queries": {
                "count": len(unique_query_results),
                "status_counts": dict(sorted(unique_status.items())),
                "probe_summary": summarize_numbers(unique_probes),
            },
            "membership_probes": {"count": 4096, "members": membership_true},
            "exception_queries": len(exception_targets),
            "false_certificate_math": {
                "wrong_inverse_sum_rejected_by_group_replay": curve.add(wrong_inverse[0], wrong_inverse[1]) != target,
                "wrong_sign_sum_rejected_by_group_replay": curve.add(wrong_sign[0], wrong_sign[1]) != target,
                "offcurve_Q_confirmed": not curve.on_curve(offcurve_q),
                "replacement_valid_subgroup_outside_B": (
                    curve.on_curve(replacement) and curve.scalar(curve.r, replacement) is None
                    and replacement not in set(base)
                ),
                "scope": "mathematical falsehood of saved public certificates; source-level rejection belongs to the separately assigned source joint",
            },
        }
        regime_state[regime_id] = {
            "curve": curve,
            "generator": generator,
            "base": base,
            "pair_map": pair_map,
            "canonical_rows": canonical_rows,
            "inverse_rows": inverse_rows,
            "panels": panels,
        }

    file_hashes = {
        name: sha256_file(R9 / name)
        for name in (
            "bases.json", "public_panels.json", "panel_files.json", "oracle_metadata.json",
            "pair_tables.json", "control_queries.json", "native_controls.json",
        )
    }
    for name, expected_hash in control_receipt["outputs"].items():
        checks.equal(sha256_file(R9 / name), expected_hash, f"control output hash {name}")
    panel_index_entries = {entry["path"]: entry["sha256"] for entry in panel_files_doc["files"]}
    checks.equal(len(panel_index_entries), 16, "panel-files index count")
    for relative, expected_hash in panel_index_entries.items():
        actual_hash = sha256_file(R9 / relative)
        checks.equal(actual_hash, expected_hash, f"panel-files hash {relative}")
        checks.equal(actual_hash, control_receipt["panel_outputs"].get(relative),
                     f"control receipt panel hash {relative}")
    checks.equal(file_hashes["public_panels.json"], oracle_doc["public_panels_sha256"],
                 "oracle public-panels binding")
    checks.equal(file_hashes["panel_files.json"], oracle_doc["panel_files_sha256"],
                 "oracle panel-files binding")
    checks.equal(file_hashes["control_queries.json"], oracle_doc["control_queries_sha256"],
                 "oracle control-query binding")
    checks.expect(control_receipt["valid"] is True and control_receipt["classification"] == "completed_valid"
                  and control_receipt["exit_code"] == 0 and not control_receipt["watchdog_reached"]
                  and not control_receipt["memory_cap_reached"] and control_receipt["telemetry_valid"] is True,
                  "native control receipt eligible")
    checks.expect(checker_receipt["valid"] is True and checker_receipt["classification"] == "completed_valid"
                  and checker_receipt["exit_code"] == 0 and not checker_receipt["watchdog_reached"]
                  and not checker_receipt["memory_cap_reached"] and checker_receipt["telemetry_valid"] is True,
                  "saved checker receipt eligible")
    checks.equal(native_controls_doc["status"], "passed", "native control status")

    blocks = schedule["blocks"]
    jobs = schedule["jobs"]
    checks.equal(len(blocks), 192, "schedule paired-block count")
    checks.equal(len(jobs), 384, "schedule job count")
    checks.equal([block["order_key"] for block in blocks], sorted(block["order_key"] for block in blocks),
                 "schedule blocks hash-sorted")
    derived_jobs = []
    for block_number, block in enumerate(blocks, 1):
        for arm in block["arms"]:
            derived_jobs.append({
                "ordinal": len(derived_jobs) + 1,
                "block": block_number,
                "regime": block["regime"],
                "M": block["M"],
                "panel": block["panel"],
                "repeat": block["repeat"],
                "arm": arm,
            })
    checks.equal(jobs, derived_jobs, "schedule jobs exact block expansion")
    expected_block_identities = {
        (regime, m_value, panel_index, repeat)
        for regime in ("n19_k4", "n23_k16")
        for m_value in (1, 32, 512)
        for panel_index in range(8)
        for repeat in range(4)
    }
    actual_block_identities = {
        (block["regime"], block["M"], block["panel"], block["repeat"]) for block in blocks
    }
    checks.equal(actual_block_identities, expected_block_identities, "schedule complete cell-panel-repeat coverage")
    arm_order_counts = defaultdict(Counter)
    for block in blocks:
        arm_order_counts[(block["regime"], block["M"], block["panel"])][tuple(block["arms"])] += 1
    for key, counts in arm_order_counts.items():
        checks.equal(counts, Counter({("expanded", "canonical_normal_x"): 2,
                                     ("canonical_normal_x", "expanded"): 2}),
                     f"schedule arm-order balance {key}")

    receipts = []
    with (R9 / "benchmark_receipts.jsonl").open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if line.strip():
                receipt = json.loads(line)
                receipt["_line_number"] = line_number
                receipts.append(receipt)
    checks.equal(len(receipts), 384, "benchmark receipt count")
    receipt_by_ordinal = {receipt["ordinal"]: receipt for receipt in receipts}
    checks.equal(set(receipt_by_ordinal), set(range(1, 385)), "benchmark receipt ordinal set")

    archive_path = R9 / "raw_outputs.tar.gz"
    archive_hash = sha256_file(archive_path)
    checks.equal(archive_hash, raw_manifest["archive_sha256"], "raw archive manifest hash")
    manifest_files = {entry["path"]: entry for entry in raw_manifest["files"]}
    checks.equal(len(manifest_files), len(raw_manifest["files"]), "raw manifest paths unique")
    raw_benchmark_members: dict[str, bytes] = {}
    archive_regular_names = []
    with tarfile.open(archive_path, "r:gz") as archive:
        for member in archive.getmembers():
            if member.isdir():
                continue
            checks.expect(member.isfile(), f"raw archive regular member {member.name}")
            archive_regular_names.append(member.name)
            extracted = archive.extractfile(member)
            if extracted is None:
                checks.expect(False, f"raw archive readable member {member.name}")
                continue
            data = extracted.read()
            expected = manifest_files.get(member.name)
            checks.expect(expected is not None, f"raw archive member declared {member.name}")
            if expected is not None:
                checks.equal(len(data), expected["bytes"], f"raw member bytes {member.name}")
                checks.equal(sha256_bytes(data), expected["sha256"], f"raw member hash {member.name}")
            if member.name.startswith("raw/benchmark/"):
                raw_benchmark_members[member.name] = data
    checks.equal(set(archive_regular_names), set(manifest_files), "raw archive and manifest member sets")
    checks.equal(len(archive_regular_names), len(set(archive_regular_names)), "raw archive paths unique")

    query_records_checked = 0
    receipt_faults = 0
    timings_by_group = defaultdict(list)
    repeated_outcomes = defaultdict(Counter)
    repeated_probes = defaultdict(list)
    for expected_job in jobs:
        ordinal = expected_job["ordinal"]
        receipt = receipt_by_ordinal.get(ordinal)
        if receipt is None:
            continue
        for field in ("ordinal", "block", "regime", "M", "panel", "repeat", "arm"):
            checks.equal(receipt[field], expected_job[field], f"receipt {ordinal} identity {field}")
        eligible = (
            receipt["valid"] is True and receipt["classification"] == "completed_valid"
            and receipt["exit_code"] == 0 and receipt["error"] is None
            and receipt["popen_error"] is None and receipt["wakeup_error"] is None
            and receipt["telemetry_valid"] is True and not receipt["watchdog_reached"]
            and not receipt["memory_cap_reached"]
        )
        checks.expect(eligible, f"receipt {ordinal} eligible")
        receipt_faults += int(not eligible)
        argv = receipt["argv"]
        checks.equal(len(argv), 9, f"receipt {ordinal} argv length")
        checks.equal(argv[1], "--job", f"receipt {ordinal} argv mode")
        checks.equal(argv[2], expected_job["regime"], f"receipt {ordinal} argv regime")
        checks.equal(Path(argv[3]).name, "n19_base.json", f"receipt {ordinal} argv frozen base")
        checks.equal(Path(argv[4]).name,
                     f"{expected_job['regime']}_panel_{expected_job['panel']}.json",
                     f"receipt {ordinal} argv panel file")
        checks.equal(int(argv[5]), expected_job["panel"], f"receipt {ordinal} argv panel")
        checks.equal(int(argv[6]), expected_job["M"], f"receipt {ordinal} argv M")
        checks.equal(argv[7], expected_job["arm"], f"receipt {ordinal} argv arm")
        try:
            result_relative = Path(argv[8]).resolve().relative_to(R9.resolve()).as_posix()
        except ValueError:
            result_relative = "OUTSIDE_RUN"
        checks.expect(result_relative.startswith("raw/benchmark/"), f"receipt {ordinal} output inside raw benchmark")
        raw_result = raw_benchmark_members.get(result_relative)
        checks.expect(raw_result is not None, f"receipt {ordinal} raw result archived")
        if raw_result is not None:
            checks.equal(sha256_bytes(raw_result), receipt["result_sha256"], f"receipt {ordinal} result hash")
            checks.equal(json.loads(raw_result), receipt["result"], f"receipt {ordinal} raw/nested result identity")
        timing_relative = result_relative + ".timing.json"
        raw_timing = raw_benchmark_members.get(timing_relative)
        checks.expect(raw_timing is not None, f"receipt {ordinal} timing archived")
        if raw_timing is not None:
            checks.equal(sha256_bytes(raw_timing), receipt["output_timing_sha256"],
                         f"receipt {ordinal} timing hash")
            checks.equal(json.loads(raw_timing), receipt["output_timing"],
                         f"receipt {ordinal} raw/nested timing identity")
        job_directory = str(Path(result_relative).parent)
        for stream in ("stdout", "stderr"):
            stream_relative = f"{job_directory}/{stream}.log"
            raw_stream = raw_benchmark_members.get(stream_relative)
            checks.expect(raw_stream is not None, f"receipt {ordinal} {stream} archived")
            if raw_stream is not None:
                checks.equal(sha256_bytes(raw_stream), receipt[f"{stream}_sha256"],
                             f"receipt {ordinal} {stream} hash")

        result = receipt["result"]
        for field in ("regime", "M", "panel", "arm"):
            checks.equal(result[field], expected_job[field], f"receipt {ordinal} result identity {field}")
        checks.equal(result["status"], "completed", f"receipt {ordinal} result completed")
        state = regime_state[expected_job["regime"]]
        expected_panel = state["panels"][expected_job["panel"]]
        checks.equal(len(result["queries"]), expected_job["M"], f"receipt {ordinal} query count")
        saved_panel_queries = saved_controls[expected_job["regime"]]["panels"][expected_job["panel"]]
        for query_index, query in enumerate(result["queries"]):
            query_records_checked += 1
            checks.equal(query["index"], query_index, f"receipt {ordinal} query index {query_index}")
            checks.equal(point(query["Q"]), expected_panel[query_index],
                         f"receipt {ordinal} query Q {query_index}")
            expected_arm_result = saved_panel_queries[query_index][expected_job["arm"]]
            checks.equal(query["result"], expected_arm_result,
                         f"receipt {ordinal} query result {query_index}")
            repeated_outcomes[(expected_job["regime"], expected_job["M"], expected_job["arm"])][
                query["result"]["status"]
            ] += 1
            repeated_probes[(expected_job["regime"], expected_job["M"], expected_job["arm"])].append(
                query["result"]["probes"]
            )
        expected_stats = saved_tables[expected_job["regime"]][expected_job["arm"]]["stats"]
        checks.equal(result["table"], expected_stats, f"receipt {ordinal} table metadata")
        checks.expect(all(value >= 0 for value in result["stages"].values()),
                      f"receipt {ordinal} nonnegative stage timings")
        timings_by_group[(expected_job["regime"], expected_job["M"], expected_job["panel"],
                          expected_job["arm"])].append(receipt)

    cells = []
    bootstrap_rng = random.Random("PAIR-REUSE-v1-bootstrap")
    for regime_id in ("n19_k4", "n23_k16"):
        for m_value in (1, 32, 512):
            panel_medians = {}
            panel_ratios = []
            for panel_index in range(8):
                panel_medians[panel_index] = {}
                for arm in ("expanded", "canonical_normal_x"):
                    group = timings_by_group[(regime_id, m_value, panel_index, arm)]
                    repeats = sorted(receipt["repeat"] for receipt in group)
                    checks.equal(repeats, [0, 1, 2, 3],
                                 f"timing repetitions {regime_id} M{m_value} panel{panel_index} {arm}")
                    panel_medians[panel_index][arm] = statistics.median(
                        receipt["wall_seconds"] for receipt in group
                    )
                panel_ratios.append(
                    panel_medians[panel_index]["canonical_normal_x"]
                    / panel_medians[panel_index]["expanded"]
                )
            bootstrap_values = []
            for _ in range(10000):
                resample = [panel_ratios[bootstrap_rng.randrange(8)] for _ in range(8)]
                bootstrap_values.append(statistics.median(resample))
            arms_summary = {}
            for arm in ("expanded", "canonical_normal_x"):
                group = [receipt for key, values in timings_by_group.items()
                         if key[0] == regime_id and key[1] == m_value and key[3] == arm
                         for receipt in values]
                stage_names = sorted({name for receipt in group for name in receipt["result"]["stages"]})
                output_names = sorted({name for receipt in group for name in receipt["output_timing"]
                                       if isinstance(receipt["output_timing"][name], (int, float))})
                arms_summary[arm] = {
                    "jobs": len(group),
                    "wall_seconds": summarize_numbers([receipt["wall_seconds"] for receipt in group]),
                    "cpu_seconds_sum": sum(
                        receipt["wait4"]["user_seconds"] + receipt["wait4"]["system_seconds"]
                        for receipt in group
                    ),
                    "peak_wait4_rss_bytes": max(receipt["wait4"]["peak_rss"] for receipt in group),
                    "continuous_rss_samples": sum(receipt["sampling"]["samples"] for receipt in group),
                    "stage_seconds": {
                        name: summarize_numbers([receipt["result"]["stages"][name] for receipt in group])
                        for name in stage_names
                    },
                    "output_timing_seconds": {
                        name: summarize_numbers([receipt["output_timing"][name] for receipt in group])
                        for name in output_names
                    },
                    "table": group[0]["result"]["table"],
                    "repeated_query_records": sum(repeated_outcomes[(regime_id, m_value, arm)].values()),
                    "repeated_status_counts": dict(sorted(repeated_outcomes[(regime_id, m_value, arm)].items())),
                    "repeated_probe_summary": summarize_numbers(repeated_probes[(regime_id, m_value, arm)]),
                }
            cells.append({
                "regime": regime_id,
                "M": m_value,
                "panel_median_wall_seconds": [
                    {"panel": panel_index, **panel_medians[panel_index]} for panel_index in range(8)
                ],
                "paired_panel_ratios_canonical_over_expanded": panel_ratios,
                "median_ratio": statistics.median(panel_ratios),
                "bootstrap": {
                    "resamples": 10000,
                    "seed": "PAIR-REUSE-v1-bootstrap",
                    "stream": "one Python Random v2 stream over cells in protocol regime/M order",
                    "resample_unit": "eight fixed panel indices with replacement",
                    "statistic": "median of eight paired panel ratios",
                    "quantile_method": "type 7: h=(N-1)p with linear interpolation",
                    "ci_95": [type7(bootstrap_values, 0.025), type7(bootstrap_values, 0.975)],
                },
                "arms": arms_summary,
            })

    primary = next(cell for cell in cells if cell["regime"] == "n23_k16" and cell["M"] == 512)
    controls_eligible = (
        control_receipt["valid"] is True and checker_receipt["valid"] is True
        and native_controls_doc["status"] == "passed"
    )
    all_jobs_eligible = len(receipts) == 384 and receipt_faults == 0
    primary_effect = (
        checks.failed == 0 and controls_eligible and all_jobs_eligible
        and primary["median_ratio"] <= 0.90 and primary["bootstrap"]["ci_95"][1] < 1.0
    )
    overall_wall = [receipt["wall_seconds"] for receipt in receipts]
    overall_cpu = [receipt["wait4"]["user_seconds"] + receipt["wait4"]["system_seconds"]
                   for receipt in receipts]

    result = {
        "schema": "crypto.autoresearch.pair_reuse_blind_review.v1",
        "task_id": "TASK-20260922-a5ab4c",
        "experiment_id": "EXP-KIC-d9c828",
        "run_id": "RUN-KIC-ba86d9",
        "scientific_snapshot": "43f937a8a08507affb7d4c15eab76977fa7c058e",
        "snapshot_parent": "8fc93f84761c646ebde6c3856f5bcba7fb581278",
        "method": {
            "kind": "permanently blind independent arithmetic, witness, receipt, and statistical replay",
            "experiment_reruns": 0,
            "benchmark_reruns": 0,
            "producer_source_imports": 0,
            "producer_checker_imports": 0,
            "private_or_imported_targets": 0,
            "scalar_log_recovery": 0,
        },
        "input_hashes": {
            "protocol.json": sha256_file(protocol_path),
            "inputs/n19_base.json": sha256_file(base_input_path),
            "inputs/schedule.json": sha256_file(schedule_path),
            "inputs/bindings.json": sha256_file(bindings_path),
            **file_hashes,
            "benchmark_receipts.jsonl": sha256_file(R9 / "benchmark_receipts.jsonl"),
            "raw_manifest.json": sha256_file(R9 / "raw_manifest.json"),
            "raw_outputs.tar.gz": archive_hash,
        },
        "checks": {
            "total": checks.total,
            "failed": checks.failed,
            "failures": checks.failures,
        },
        "regimes": regime_results,
        "control_and_checker_receipts": {
            "native_control": {
                "classification": control_receipt["classification"],
                "valid": control_receipt["valid"],
                "exit_code": control_receipt["exit_code"],
                "watchdog_reached": control_receipt["watchdog_reached"],
                "memory_cap_reached": control_receipt["memory_cap_reached"],
            },
            "saved_checker": {
                "classification": checker_receipt["classification"],
                "valid": checker_receipt["valid"],
                "exit_code": checker_receipt["exit_code"],
                "watchdog_reached": checker_receipt["watchdog_reached"],
                "memory_cap_reached": checker_receipt["memory_cap_reached"],
                "role_in_this_report": "eligibility receipt only; its implementation and result were not read or imported",
            },
        },
        "schedule_receipts_and_raw": {
            "paired_blocks": len(blocks),
            "scheduled_jobs": len(jobs),
            "receipt_count": len(receipts),
            "receipt_faults_or_censors": receipt_faults,
            "query_records_replayed": query_records_checked,
            "raw_manifest_files": len(manifest_files),
            "raw_archive_regular_files": len(archive_regular_names),
            "raw_archive_sha256": archive_hash,
            "raw_manifest_archive_sha256": raw_manifest["archive_sha256"],
            "all_raw_member_hashes_and_sizes_match": set(archive_regular_names) == set(manifest_files),
        },
        "statistics": {
            "aggregation": "median of four whole-cold-job wall times per panel/arm; canonical divided by expanded; median of eight panel ratios",
            "cells": cells,
            "primary": {
                "regime": "n23_k16",
                "M": 512,
                "arm_ratio": "canonical_normal_x/expanded",
                "median_ratio": primary["median_ratio"],
                "bootstrap_ci_95": primary["bootstrap"]["ci_95"],
                "thresholds": {"median_ratio_lte": 0.90, "ci_upper_lt": 1.0},
                "all_controls_checker_and_384_jobs_valid": controls_eligible and all_jobs_eligible,
                "effect_predicate": primary_effect,
            },
        },
        "cost_scope": {
            "primary_measure": "direct native Popen launch to sole wait4 reap",
            "whole_cold_job": "input read, fresh deterministic base construction and validation, arm-specific normal preparation, one pair-table build, all M ordered queries with witness replay, and result output",
            "construction_charged": "once per fresh job, never multiplied by M",
            "panel_file": "the common 512-point public panel file is read by both arms for every M; M selects the working prefix",
            "benchmark_jobs": {
                "wall_seconds": summarize_numbers(overall_wall),
                "cpu_seconds": summarize_numbers(overall_cpu),
                "peak_wait4_rss_bytes": max(receipt["wait4"]["peak_rss"] for receipt in receipts),
                "continuous_rss_samples": sum(receipt["sampling"]["samples"] for receipt in receipts),
                "parent_validation_seconds_sum_excluded_from_primary": sum(
                    receipt["parent_validation_seconds"] for receipt in receipts
                ),
            },
            "data_unit_note": "4096 unique public targets per regime; timing jobs repeatedly process nested prefixes of those fixed panels across M, arm, and four technical repetitions",
        },
        "limitations": [
            "Finite fixed public panels at n=19/K=4 and n=23/K=16 only.",
            "The eight-panel bootstrap is descriptive uncertainty over the fixed public lists, not population sampling or an asymptotic claim.",
            "Fields and base sizes change together across regimes, so cross-regime differences do not isolate a field-size effect.",
            "Job memory is wait4 peak RSS without continuous sampling; no stronger continuous-memory bound is inferred.",
            "No full index-calculus relation construction, rank, linear algebra, extraction, rho comparison, or generic-exponent effect is measured.",
            "Saved false certificates were checked mathematically; source-level rejection is owned by the separately assigned source joint.",
        ],
        "joint_verdict": "holds" if checks.failed == 0 else "breaks",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(OUT.relative_to(REPO)),
        "checks": result["checks"],
        "primary": result["statistics"]["primary"],
        "joint_verdict": result["joint_verdict"],
    }, indent=2))
    return 0 if checks.failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
