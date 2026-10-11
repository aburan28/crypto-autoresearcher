#!/usr/bin/env python3
"""Independent source/custody/cost re-derivation for TASK-20260922-a0c874.

This is review code.  It never launches the experiment binary, runner, checker,
or analyzer, and it imports none of their modules.  It reads the frozen public
artifacts, independently reconstructs the finite bases and pair supports, and
prints one JSON summary.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import random
import statistics
import subprocess
import tarfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
CONTROL = ROOT / "research/pair_reuse_20260922"
RUN = ROOT / "experiments/EXP-KIC-d9c828/runs/RUN-KIC-ba86d9"
CODE = ROOT / "experiments/EXP-KIC-d9c828/code"
EMPTY_SHA = hashlib.sha256(b"").hexdigest()
SNAPSHOT = "43f937a8a08507affb7d4c15eab76977fa7c058e"
SNAPSHOT_PARENT = "8fc93f84761c646ebde6c3856f5bcba7fb581278"
BINDING = "ebe1ff5e7f1f1531376706d1442324a687027d1a"
ADMISSION = "d89e6a7403394b93880faa31c34afce969b8a70d"
CLAIM = "a3628f2cb97458835d146dd9657392ea448b90c3"
ARMS = ("expanded", "canonical_normal_x")
REGIMES = ("n19_k4", "n23_k16")
MS = (1, 32, 512)
Point = tuple[int, int] | None


def need(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text())


def jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


class Curve:
    def __init__(self, regime: str):
        self.regime = regime
        if regime == "n19_k4":
            self.n, self.poly, self.r, self.order, self.orbits = (
                19,
                (1 << 19) | 39,
                262543,
                525086,
                4,
            )
        elif regime == "n23_k16":
            self.n, self.poly, self.r, self.order, self.orbits = (
                23,
                (1 << 23) | 33,
                4196903,
                8393806,
                16,
            )
        else:
            raise ValueError(regime)
        self.field = 1 << self.n
        self.mask = self.field - 1
        self.base_points = 2 * self.n * self.orbits

    def mul(self, a: int, b: int) -> int:
        raw = 0
        for bit in range(self.n):
            if (b >> bit) & 1:
                raw ^= a << bit
        for bit in range(2 * self.n - 2, self.n - 1, -1):
            if (raw >> bit) & 1:
                raw ^= self.poly << (bit - self.n)
        return raw

    def sq(self, a: int) -> int:
        return self.mul(a, a)

    def inv(self, a: int) -> int:
        need(a != 0, "zero inverse")
        u, v, g, h = a, self.poly, 1, 0
        while u != 1:
            need(u != 0, "noninvertible field value")
            shift = u.bit_length() - v.bit_length()
            if shift < 0:
                u, v, g, h = v, u, h, g
                shift = -shift
            u ^= v << shift
            g ^= h << shift
        while g.bit_length() > self.n:
            g ^= self.poly << (g.bit_length() - self.n - 1)
        return g

    def neg(self, point: Point) -> Point:
        return None if point is None else (point[0], point[1] ^ point[0])

    def oncurve(self, point: Point) -> bool:
        if point is None:
            return True
        x, y = point
        return (
            0 <= x < self.field
            and 0 <= y < self.field
            and self.sq(y) ^ self.mul(x, y)
            == self.mul(self.sq(x), x) ^ self.sq(x) ^ 1
        )

    def add(self, left: Point, right: Point) -> Point:
        if left is None:
            return right
        if right is None:
            return left
        x, y = left
        u, v = right
        if x == u:
            if y ^ v == x:
                return None
            need(left == right and x != 0, "invalid equal-x pair")
            slope = x ^ self.mul(y, self.inv(x))
            z = self.sq(slope) ^ slope ^ 1
            return z, self.sq(x) ^ self.mul(slope ^ 1, z)
        slope = self.mul(y ^ v, self.inv(x ^ u))
        z = self.sq(slope) ^ slope ^ x ^ u ^ 1
        return z, self.mul(slope, x ^ z) ^ z ^ y

    def times(self, point: Point, scalar: int) -> Point:
        out = None
        while scalar:
            if scalar & 1:
                out = self.add(out, point)
            point = self.add(point, point)
            scalar >>= 1
        return out

    def frob(self, point: Point) -> Point:
        return None if point is None else (self.sq(point[0]), self.sq(point[1]))

    def shift(self, point: Point, amount: int) -> Point:
        for _ in range(amount % self.n):
            point = self.frob(point)
        return point

    def halftrace(self, value: int) -> int:
        out, term = 0, value
        for _ in range((self.n + 1) // 2):
            out ^= term
            term = self.sq(self.sq(term))
        return out

    def lift_x(self, x: int) -> Point:
        if x == 0:
            return None
        inverse = self.inv(x)
        c = x ^ 1 ^ self.sq(inverse)
        w = self.halftrace(c)
        if self.sq(w) ^ w != c:
            return None
        y = self.mul(x, w)
        point = (x, min(y, y ^ x))
        need(self.oncurve(point), "halftrace lift off curve")
        return point

    def generator(self) -> Point:
        for x in range(1, 4096):
            point = self.lift_x(x)
            if point is None:
                continue
            doubled = self.add(point, point)
            if doubled is not None and self.times(doubled, self.r) is None:
                return doubled
        raise AssertionError("generator scan exhausted")

    def append_orbit(self, seed: Point, points: list[Point], seen: set[Point]) -> None:
        need(seed is not None and seed[0] != 0, "invalid seed")
        need(self.oncurve(seed) and self.times(seed, self.r) is None, "seed subgroup")
        start, point = seed, seed
        own: set[Point] = set()
        for _ in range(self.n):
            for item in (point, self.neg(point)):
                need(item not in seen and item not in own, "signed orbit overlap")
                own.add(item)
                seen.add(item)
                points.append(item)
            point = self.frob(point)
        need(point == start and len(own) == 2 * self.n, "short seed orbit")

    def base(self, n19_recipe: dict[str, Any]) -> tuple[list[Point], list[Point], list[int]]:
        points: list[Point] = []
        seeds: list[Point] = []
        indices: list[int] = []
        seen: set[Point] = set()
        if self.regime == "n19_k4":
            need(
                (
                    n19_recipe["n"],
                    n19_recipe["modulus"],
                    n19_recipe["a"],
                    n19_recipe["b"],
                    n19_recipe["r"],
                    n19_recipe["cofactor"],
                )
                == (self.n, self.poly, 1, 1, self.r, 2),
                "n19 parameter recipe",
            )
            for row in n19_recipe["seed_points"]:
                point = tuple(row["point"])
                seeds.append(point)
                indices.append(row["pool_orbit_index"])
                self.append_orbit(point, points, seen)
            need(sorted(point[0] for point in seeds if point) == n19_recipe["plane_key"], "n19 plane")
        else:
            labels: set[int] = set()
            for index in range(4096):
                if len(seeds) == self.orbits:
                    break
                digest = hashlib.sha256(f"PAIR-REUSE-v1-base-n23-{index}".encode()).digest()
                x = int.from_bytes(digest[:8], "little") % self.field
                point = self.lift_x(x)
                if point is None or self.times(point, self.r) is not None:
                    continue
                label = min(self.shift(point, j)[0] for j in range(self.n))
                if label in labels:
                    continue
                labels.add(label)
                seeds.append(point)
                indices.append(index)
                self.append_orbit(point, points, seen)
        points.sort()
        need(len(seeds) == self.orbits, "orbit count")
        need(len(points) == self.base_points == len(seen), "base cardinality")
        need(len({point[0] for point in points if point}) == self.base_points // 2, "base x count")
        need(all(self.neg(p) in seen and self.frob(p) in seen for p in points), "base invariance")
        return points, seeds, indices


def rank(values: list[int]) -> int:
    pivots: dict[int, int] = {}
    for value in values:
        while value:
            bit = value.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = value
                break
            value ^= pivots[bit]
    return len(pivots)


def normal_basis(curve: Curve) -> tuple[int, tuple[int, ...], tuple[int, ...]]:
    for beta in range(1, curve.field):
        columns = []
        value = beta
        for _ in range(curve.n):
            columns.append(value)
            value = curve.sq(value)
        if rank(columns) == curve.n:
            break
    else:
        raise AssertionError("normal basis absent")
    pivots: dict[int, tuple[int, int]] = {}
    for bit, column in enumerate(columns):
        row, mask = column, 1 << bit
        while row:
            lead = row.bit_length() - 1
            if lead not in pivots:
                pivots[lead] = row, mask
                break
            prior, prior_mask = pivots[lead]
            row ^= prior
            mask ^= prior_mask
        need(row != 0, "dependent normal basis")
    inverse = []
    for bit in range(curve.n):
        value, mask = 1 << bit, 0
        while value:
            row, part = pivots[value.bit_length() - 1]
            value ^= row
            mask ^= part
        inverse.append(mask)
    return beta, tuple(columns), tuple(inverse)


def to_normal(value: int, inverse: tuple[int, ...]) -> int:
    out = 0
    bit = 0
    while value:
        if value & 1:
            out ^= inverse[bit]
        value >>= 1
        bit += 1
    return out


def rotate(value: int, amount: int, n: int) -> int:
    if amount == 0:
        return value
    return ((value << amount) | (value >> (n - amount))) & ((1 << n) - 1)


def canonical(curve: Curve, point: Point, inverse: tuple[int, ...]) -> tuple[int | None, int]:
    if point is None:
        return None, 0
    mask = to_normal(point[0], inverse)
    choices = [(rotate(mask, j, curve.n), j) for j in range(curve.n)]
    return min(choices)


def point_key(point: Point) -> tuple[int, int]:
    return ((1 << 32) - 1, 0) if point is None else point


def packed(curve: Curve, point: Point) -> int:
    return (1 << 64) - 1 if point is None else (point[0] << curve.n) | point[1]


def decode(value: Any) -> Point:
    return None if value is None else (int(value[0]), int(value[1]))


def verify_archive(archive: Path, manifest: dict[str, Any]) -> int:
    need(sha(archive) == manifest["archive_sha256"], f"archive hash {archive.name}")
    expected = {row["path"]: row for row in manifest["files"]}
    observed: set[str] = set()
    with tarfile.open(archive, "r:gz") as handle:
        for member in handle.getmembers():
            need(member.isfile(), f"non-regular archive member {member.name}")
            need(member.name in expected and member.name not in observed, f"unexpected archive member {member.name}")
            stream = handle.extractfile(member)
            need(stream is not None, f"unreadable archive member {member.name}")
            value = stream.read()
            row = expected[member.name]
            need(len(value) == row["bytes"] and sha_bytes(value) == row["sha256"], f"archive member hash {member.name}")
            observed.add(member.name)
    need(observed == set(expected), f"archive members differ {archive.name}")
    return len(observed)


def expected_rows(
    curve: Curve, seeds: list[Point], inverse: tuple[int, ...]
) -> dict[int | None, tuple[Any, ...]]:
    rows: dict[int | None, tuple[tuple[Any, ...], tuple[Any, ...]]] = {}
    for first in range(curve.orbits):
        for second in range(first, curve.orbits):
            for offset in range(curve.n):
                positive = curve.shift(seeds[second], offset)
                for sign, right in ((1, positive), (-1, curve.neg(positive))):
                    total = curve.add(seeds[first], right)
                    key, frame = canonical(curve, total, inverse)
                    left2 = curve.shift(seeds[first], frame)
                    right2 = curve.shift(right, frame)
                    left2, right2 = sorted((left2, right2), key=point_key)
                    sum2 = curve.shift(total, frame)
                    row = (left2, right2, sum2, first, second, offset, sign, frame, 1)
                    order = (*point_key(left2), *point_key(right2), *point_key(sum2), first, second, offset, sign)
                    prior = rows.get(key)
                    if prior is None or order < prior[1]:
                        rows[key] = row, order
    return {key: value[0] for key, value in rows.items()}


def verify_regime(
    regime: str,
    recipe: dict[str, Any],
    bases: dict[str, Any],
    tables: dict[str, Any],
    controls: dict[str, Any],
    panels: dict[str, Any],
) -> tuple[dict[str, Any], dict[tuple[int, int], tuple[bool, int]], list[Point], set[Point]]:
    curve = Curve(regime)
    points, seeds, indices = curve.base(recipe)
    pointset = set(points)
    saved_base = bases[regime]
    need(saved_base["n"] == curve.n and saved_base["modulus"] == curve.poly, "saved field")
    need(saved_base["r"] == curve.r and saved_base["curve_order"] == curve.order, "saved order")
    need(saved_base["candidate_indices"] == indices, "candidate indices")
    need([decode(value) for value in saved_base["seeds"]] == seeds, "saved seeds")
    need([decode(value) for value in saved_base["points"]] == points, "saved base points")
    generator = curve.generator()
    need(decode(saved_base["generator"]) == generator, "public generator")
    beta, columns, inverse = normal_basis(curve)
    normal = saved_base["normal"]
    need(normal["beta"] == beta == 3, "least normal beta")
    need(tuple(normal["columns"]) == columns and tuple(normal["inverse_columns"]) == inverse, "normal matrices")
    need(normal["nibble_chunks"] == math.ceil(curve.n / 4), "nibble chunk count")
    for bit, column in enumerate(columns):
        need(to_normal(column, inverse) == 1 << bit, "normal inverse column")
        need(to_normal(curve.sq(column), inverse) == rotate(1 << bit, 1, curve.n), "normal Frobenius rotation")
    torsion = (0, 1)
    need(curve.oncurve(torsion) and curve.add(torsion, torsion) is None, "torsion control")
    need(curve.neg(torsion) == torsion and curve.frob(torsion) == torsion, "torsion orbit")
    need(canonical(curve, None, inverse) == (None, 0), "O canonical")
    need(canonical(curve, torsion, inverse) == (0, 0), "T canonical")

    expanded_first: dict[Point, tuple[Point, Point]] = {}
    for i, left in enumerate(points):
        for right in points[i:]:
            total = curve.add(left, right)
            expanded_first.setdefault(total, (left, right))
    expanded_set = set(expanded_first)
    key_bytes = b"".join(
        packed(curve, point).to_bytes(8, "little")
        for point in sorted(expanded_set, key=lambda value: packed(curve, value))
    )
    saved_table = tables[regime]
    expanded_stats = saved_table["expanded"]["stats"]
    need(expanded_stats["anchor_additions"] == len(points) * (len(points) + 1) // 2, "expanded anchors")
    need(expanded_stats["keys"] == len(expanded_set), "expanded keys")
    need(saved_table["expanded"]["sorted_packed_keys_le64_sha256"] == sha_bytes(key_bytes), "expanded support digest")

    want_rows = expected_rows(curve, seeds, inverse)
    saved_rows: dict[int | None, tuple[Any, ...]] = {}
    for record in saved_table["canonical_normal_x"]["rows"]:
        key = record["key"]["value"]
        left, right = map(decode, record["normalized_endpoints"])
        total = decode(record["stored_sum"])
        need(left in pointset and right in pointset, "canonical endpoint outside B")
        need(curve.add(left, right) == total, "canonical row sum")
        need(canonical(curve, total, inverse)[0] == key, "canonical row key")
        value = (left, right, total, *record["anchor"], *record["source_frame"])
        need(key not in saved_rows, "duplicate canonical key")
        saved_rows[key] = value
    need(saved_rows == want_rows, "canonical retained rows are not exact lex rows")
    canonical_stats = saved_table["canonical_normal_x"]["stats"]
    need(canonical_stats["anchor_additions"] == curve.orbits * (curve.orbits + 1) // 2 * (2 * curve.n), "canonical anchors")
    need(canonical_stats["keys"] == len(saved_rows), "canonical keys")
    expansion: set[Point] = set()
    for row in saved_rows.values():
        total = row[2]
        for shift in range(curve.n):
            moved = curve.shift(total, shift)
            expansion.add(moved)
            expansion.add(curve.neg(moved))
    need(expansion == expanded_set, "canonical expansion differs from exact full pair support")

    saved_control = controls[regime]
    trace_a, trace_b = 2, 1
    for _ in range(2, curve.n + 1):
        trace_a, trace_b = trace_b, trace_b - 2 * trace_a
    need(saved_control["trace"] == trace_b and curve.field + 1 - trace_b == curve.order, "trace/order")
    need(saved_control["curve_order"] == curve.order and saved_control["r_prime"] is True, "order receipt")
    need(saved_control["normal_all_field_values"] == curve.field, "exhaustive normal count")
    need(saved_control["base_points"] == len(points), "control base count")
    need(saved_control["expanded_keys"] == len(expanded_set), "control expanded count")
    need(saved_control["canonical_keys"] == len(saved_rows), "control canonical count")

    forged = saved_control["forgeries"]
    target = decode(forged["target"])
    key, frame = canonical(curve, target, inverse)
    row = saved_rows[key]
    left, right, stored_sum = row[:3]
    aligned = curve.shift(target, frame)
    sign = 1 if aligned == stored_sum else -1
    inverse_transport = lambda p, j, s: curve.shift(p, curve.n - j) if s == 1 else curve.neg(curve.shift(p, curve.n - j))
    wrong_inverse = (
        inverse_transport(left, (frame + 1) % curve.n, sign),
        inverse_transport(right, (frame + 1) % curve.n, sign),
    )
    wrong_sign = (inverse_transport(left, frame, -sign), inverse_transport(right, frame, -sign))
    need(tuple(map(decode, forged["wrong_inverse_endpoints"])) == wrong_inverse, "wrong-inverse certificate bytes")
    need(tuple(map(decode, forged["wrong_sign_endpoints"])) == wrong_sign, "wrong-sign certificate bytes")
    need(curve.add(*wrong_inverse) != target and curve.add(*wrong_sign) != target, "false transport accepted")
    need(forged["frame_shift"] == frame and forged["frame_sign"] == sign, "forgery frame")
    need(forged["genuine_table_key"] == key and forged["wrong_table_key_value"] == (key ^ 1), "wrong key")
    wrong_sum = decode(forged["wrong_stored_sum_value"])
    need(wrong_sum == curve.add(stored_sum, generator) and curve.add(left, right) != wrong_sum, "wrong sum")
    offcurve = decode(forged["offcurve_Q"])
    need(offcurve is not None and not curve.oncurve(offcurve), "offcurve certificate")
    need(not all(curve.neg(p) in set(points[:-1]) and curve.frob(p) in set(points[:-1]) for p in points[:-1]), "removed base invariant")
    replacement = next(curve.times(generator, d) for d in range(1, curve.r) if curve.times(generator, d) not in pointset and curve.times(generator, d) is not None)
    need(decode(forged["replacement"]) == replacement, "replacement point")
    replaced = points.copy()
    replaced[0] = replacement
    replaced_set = set(replaced)
    need(len(replaced_set) == len(points), "replacement cardinality")
    need(not all(curve.neg(p) in replaced_set and curve.frob(p) in replaced_set for p in replaced), "replacement unexpectedly invariant")
    for flag in (
        "wrong_inverse_shift_plus_one",
        "wrong_sign",
        "wrong_table_key",
        "wrong_stored_sum",
        "offcurve_Q_rejected",
        "one_point_removed_base",
        "same_cardinality_noninvariant_base",
    ):
        need(forged[flag] is True, f"forgery flag {flag}")

    query_truth: dict[tuple[int, int], tuple[bool, int]] = {}
    panel_rows = panels[regime]
    need(len(panel_rows) == 8 and all(len(row) == 512 for row in panel_rows), "panel dimensions")
    for panel, row in enumerate(panel_rows):
        for index, q in enumerate(row):
            need(q is not None and curve.oncurve(q) and curve.times(q, curve.r) is None, "panel subgroup point")
            hit_index = -1
            for third_index, third in enumerate(points):
                difference = curve.add(q, curve.neg(third))
                if difference in expanded_set:
                    hit_index = third_index
                    break
            query_truth[(panel, index)] = (hit_index >= 0, hit_index)
    return (
        {
            "n": curve.n,
            "modulus": curve.poly,
            "r": curve.r,
            "curve_order": curve.order,
            "candidate_indices": indices,
            "generator": list(generator),
            "base_points": len(points),
            "unordered_pairs": len(points) * (len(points) + 1) // 2,
            "expanded_keys": len(expanded_set),
            "canonical_keys": len(saved_rows),
            "normal_beta": beta,
            "normal_columns": len(columns),
            "nibble_chunks": math.ceil(curve.n / 4),
            "forgeries_independently_false": True,
            "exact_support_equal": True,
            "panel_queries_independently_classified": len(query_truth),
            "panel_sat": sum(value[0] for value in query_truth.values()),
            "panel_unsat": sum(not value[0] for value in query_truth.values()),
        },
        query_truth,
        points,
        pointset,
    )


def quantile_type7(values: list[float], probability: float) -> float:
    values = sorted(values)
    position = (len(values) - 1) * probability
    low, high = int(position), math.ceil(position)
    if low == high:
        return values[low]
    return values[low] * (high - position) + values[high] * (position - low)


def bootstrap(values: list[float]) -> dict[str, Any]:
    rng = random.Random("PAIR-REUSE-v1-bootstrap")
    draws = sorted(statistics.median(values[rng.randrange(8)] for _ in range(8)) for _ in range(10000))
    encoded = json.dumps(draws, separators=(",", ":")).encode()
    return {
        "lower": quantile_type7(draws, 0.025),
        "upper": quantile_type7(draws, 0.975),
        "draws_sha256": sha_bytes(encoded),
    }


def main() -> None:
    protocol = load(CONTROL / "protocol.json")
    schedule = load(CONTROL / "inputs/schedule.json")
    recipe = load(CONTROL / "inputs/n19_base.json")
    source_closure = load(RUN / "source_closure.json")
    bases_doc = load(RUN / "bases.json")
    tables_doc = load(RUN / "pair_tables.json")
    controls_doc = load(RUN / "native_controls.json")
    public_doc = load(RUN / "public_panels.json")
    panel_manifest = load(RUN / "panel_files.json")
    science_receipt = load(CONTROL / "science_snapshot_receipt.json")

    need(protocol["experiment_id"] == "EXP-KIC-d9c828" and protocol["run_id"] == "RUN-KIC-ba86d9", "protocol ids")
    frozen = {
        "protocol": "3de8d70ae219cd2aad2c6ccf67156fdc3d1c6591729efad9e9822224a4d844de",
        "schedule": "a1cfbbf5053318c6b568948723abf613d991039c35152d524ee5909ece6387cb",
        "base": "f00b5c5710d041bf862525b5f8d1baf15328e4a9bd6a11f659d300b5ca62cfb1",
    }
    need(sha(CONTROL / "protocol.json") == frozen["protocol"], "protocol hash")
    need(sha(CONTROL / "inputs/schedule.json") == frozen["schedule"], "schedule hash")
    need(sha(CONTROL / "inputs/n19_base.json") == frozen["base"], "base hash")
    for name, expected in source_closure["source_sha256"].items():
        need(sha(CODE / name) == expected, f"source closure {name}")
    need(sha(RUN / "build/native") == source_closure["binary_sha256"], "binary closure")
    need(source_closure["binary_sha256"] == "ab068745747b213532ed766ca0819bccdbdfe3ccd447ea31f95cc49406840fce", "binary frozen hash")
    need(os.stat(RUN / "build/native").st_mode & 0o777 == 0o755, "binary mode")
    installation = load(CONTROL / "native_installation_receipt.json")
    need(installation["binary_sha256"] == source_closure["binary_sha256"], "installation bytes")
    need(installation["mode_before"] == "0o644" and installation["mode_after"] == "0o755", "installation mode correction")
    need(installation["scientific_processes_before_correction"] == 0, "pre-correction process count")
    need(git("ls-tree", SNAPSHOT, "experiments/EXP-KIC-d9c828/runs/RUN-KIC-ba86d9/build/native").split()[0] == "100755", "snapshot executable mode")

    bases = {row["id"]: row for row in bases_doc["regimes"]}
    tables = {row["id"]: row for row in tables_doc["regimes"]}
    controls = {row["id"]: row for row in controls_doc["regimes"]}
    public = {
        row["id"]: [[decode(point) for point in panel] for panel in row["panels"]]
        for row in public_doc["regimes"]
    }
    need(set(bases) == set(tables) == set(controls) == set(public) == set(REGIMES), "regime sets")
    panel_files = {row["path"]: row["sha256"] for row in panel_manifest["files"]}
    need(len(panel_files) == 16, "Q-only file count")
    for regime in REGIMES:
        for panel in range(8):
            relative = f"panels/{regime}_panel_{panel}.json"
            path = RUN / relative
            one = load(path)
            need(set(one) == {"schema", "regime", "panel", "points"}, "Q-only schema")
            need(one["regime"] == regime and one["panel"] == panel, "Q-only identity")
            need([decode(point) for point in one["points"]] == public[regime][panel], "Q-only content")
            need(panel_files[relative] == sha(path), "Q-only hash")

    regime_results: dict[str, Any] = {}
    truth: dict[str, dict[tuple[int, int], tuple[bool, int]]] = {}
    points: dict[str, list[Point]] = {}
    pointsets: dict[str, set[Point]] = {}
    for regime in REGIMES:
        result, classifications, base_points, pointset = verify_regime(
            regime, recipe, bases, tables, controls, public
        )
        regime_results[regime] = result
        truth[regime] = classifications
        points[regime] = base_points
        pointsets[regime] = pointset

    jobs = schedule["jobs"]
    need(len(schedule["blocks"]) == 192 and len(jobs) == 384, "schedule size")
    need([row["ordinal"] for row in jobs] == list(range(1, 385)), "schedule ordinals")
    expected_cases = {
        (regime, m, panel, repeat, arm)
        for regime in REGIMES
        for m in MS
        for panel in range(8)
        for repeat in range(4)
        for arm in ARMS
    }
    need({(row["regime"], row["M"], row["panel"], row["repeat"], row["arm"]) for row in jobs} == expected_cases, "schedule factorial")
    for regime in REGIMES:
        for m in MS:
            orders = []
            for block in schedule["blocks"]:
                if block["regime"] == regime and block["M"] == m:
                    orders.append(tuple(block["arms"]))
            need(orders.count(ARMS) == 16 and orders.count(tuple(reversed(ARMS))) == 16, "balanced arm order")

    receipts = jsonl(RUN / "benchmark_receipts.jsonl")
    need(len(receipts) == 384, "receipt count")
    total_queries = 0
    total_witnesses = 0
    stage_totals = {
        key: 0.0
        for key in (
            "input_read_seconds",
            "base_construction_validation_seconds",
            "public_Q_validation_seconds",
            "normal_basis_and_nibble_prep_seconds",
            "table_build_seconds",
            "all_queries_transport_replay_seconds",
            "serialization_seconds",
            "result_write_seconds",
            "parent_validation_seconds",
        )
    }
    cell_rows: dict[tuple[str, int, int, str], list[float]] = {}
    raw_manifest = load(RUN / "raw_manifest.json")
    raw_index = {row["path"]: row for row in raw_manifest["files"]}
    need(len(raw_index) == 1567, "aggregate raw member count")
    for want, receipt in zip(jobs, receipts, strict=True):
        for key in ("ordinal", "block", "regime", "M", "panel", "repeat", "arm"):
            need(receipt[key] == want[key], f"receipt schedule {receipt['ordinal']} {key}")
        need(receipt["valid"] is True and receipt["classification"] == "completed_valid", "receipt validity")
        need(receipt["error"] is None and receipt["exit_code"] == 0, "receipt process status")
        need(receipt["popen_error"] is None and receipt["wakeup_error"] is None, "receipt launch/wakeup")
        need(not receipt["watchdog_reached"] and not receipt["memory_cap_reached"], "receipt censor")
        need(receipt["telemetry_valid"] is True and receipt["wall_seconds"] > 0, "receipt telemetry")
        need(receipt["wakeup_method"] == "Darwin kqueue NOTE_EXIT with ESRCH fast-exit wait4 recovery", "wakeup method")
        need(receipt["wait4"]["rss_unit"] == "bytes" and receipt["wait4"]["peak_rss"] > 0, "wait4 memory")
        need(receipt["stdout_sha256"] == EMPTY_SHA and receipt["stderr_sha256"] == EMPTY_SHA, "job streams")
        argv = receipt["argv"]
        regime, m, panel, arm = receipt["regime"], receipt["M"], receipt["panel"], receipt["arm"]
        need(len(argv) == 9 and argv[1] == "--job", "worker argv shape")
        need(Path(argv[0]).name == "native" and argv[2] == regime, "worker binary/regime")
        need(Path(argv[3]).resolve() == (CONTROL / "inputs/n19_base.json").resolve(), "worker base input")
        need(Path(argv[4]).resolve() == (RUN / "panels" / f"{regime}_panel_{panel}.json").resolve(), "worker Q-only input")
        need(argv[5:8] == [str(panel), str(m), arm], "worker panel/M/arm")
        forbidden = ("oracle", "scalar", "expected", "control_queries", "pair_tables", "status")
        need(not any(token in " ".join(argv).lower() for token in forbidden), "worker advice in argv")
        result = receipt["result"]
        need(result["status"] == "completed", "native result status")
        need((result["regime"], result["M"], result["panel"], result["arm"]) == (regime, m, panel, arm), "native result identity")
        need(len(result["queries"]) == m, "exact M queries")
        need(result["table"]["keys"] == regime_results[regime]["expanded_keys" if arm == "expanded" else "canonical_keys"], "table key count")
        expected_anchors = regime_results[regime]["unordered_pairs"] if arm == "expanded" else Curve(regime).orbits * (Curve(regime).orbits + 1) // 2 * (2 * Curve(regime).n)
        need(result["table"]["anchor_additions"] == expected_anchors, "table construction count")
        need(result["table"]["value_type"] == ("inline_pair_indices" if arm == "expanded" else "inline_canonical_row"), "table representation")
        for key in (
            "input_read_seconds",
            "base_construction_validation_seconds",
            "public_Q_validation_seconds",
            "normal_basis_and_nibble_prep_seconds",
            "table_build_seconds",
            "all_queries_transport_replay_seconds",
        ):
            value = result["stages"][key]
            need(isinstance(value, (int, float)) and math.isfinite(value) and value >= 0, f"stage {key}")
            stage_totals[key] += value
        for key in ("serialization_seconds", "result_write_seconds"):
            value = receipt["output_timing"][key]
            need(isinstance(value, (int, float)) and math.isfinite(value) and value >= 0, f"output {key}")
            stage_totals[key] += value
        need(receipt["wall_seconds"] >= receipt["output_timing"]["process_observed_until_timing_file_seconds"], "Popen wall excludes timing file")
        stage_totals["parent_validation_seconds"] += receipt["parent_validation_seconds"]
        sat_count = 0
        for index, query in enumerate(result["queries"]):
            q = decode(query["Q"])
            need(query["index"] == index and q == public[regime][panel][index], "query identity/prefix")
            expected_sat, expected_third = truth[regime][(panel, index)]
            answer = query["result"]
            need(answer["status"] == ("SAT" if expected_sat else "UNSAT"), "independent status")
            need(answer["third_index"] == expected_third, "independent first hit")
            need(answer["probes"] == (expected_third + 1 if expected_sat else len(points[regime])), "probe count")
            need(answer["canonicalizations"] == (answer["probes"] if arm == "canonical_normal_x" else 0), "canonicalization count")
            if expected_sat:
                witness = tuple(decode(value) for value in answer["witness"])
                need(len(witness) == 3 and all(value in pointsets[regime] for value in witness), "witness membership")
                need(witness[2] == points[regime][expected_third], "witness first-hit third")
                curve = Curve(regime)
                need(curve.add(curve.add(witness[0], witness[1]), witness[2]) == q, "witness group replay")
                sat_count += 1
                total_witnesses += 1
            else:
                need(answer["witness"] is None, "UNSAT witness")
        need(result["counters"]["inverse_transport"] == (2 * sat_count if arm == "canonical_normal_x" else 0), "transport count")
        total_queries += m
        key = (regime, m, panel, arm)
        cell_rows.setdefault(key, []).append(receipt["wall_seconds"])
        folder = f"{receipt['ordinal']:03d}_{regime}_M{m}_p{panel}_r{receipt['repeat']}_{arm}"
        result_path = f"raw/benchmark/{folder}/result.json"
        timing_path = result_path + ".timing.json"
        need(raw_index[result_path]["sha256"] == receipt["result_sha256"], "raw result receipt hash")
        need(raw_index[timing_path]["sha256"] == receipt["output_timing_sha256"], "raw timing receipt hash")

    command_lines = [json.loads(line) for line in (RUN / "command.txt").read_text().splitlines() if line]
    need(len(command_lines) == 389 and command_lines[-384:] == [row["argv"] for row in receipts], "command transcript")
    need(len({(row["regime"], row["M"], row["panel"], row["repeat"], row["arm"]) for row in receipts}) == 384, "receipt uniqueness")

    cells = []
    for regime in REGIMES:
        for m in MS:
            ratios = []
            panel_values = []
            for panel in range(8):
                expanded = statistics.median(cell_rows[(regime, m, panel, "expanded")])
                canonical_wall = statistics.median(cell_rows[(regime, m, panel, "canonical_normal_x")])
                ratio = canonical_wall / expanded
                ratios.append(ratio)
                panel_values.append({"panel": panel, "expanded_median": expanded, "canonical_median": canonical_wall, "ratio": ratio})
            interval = bootstrap(ratios)
            cells.append(
                {
                    "regime": regime,
                    "M": m,
                    "panels": panel_values,
                    "median_ratio": statistics.median(ratios),
                    "bootstrap_95": interval,
                }
            )
    analysis = load(RUN / "analysis.json")
    for independent, recorded in zip(cells, analysis["cells"], strict=True):
        need((independent["regime"], independent["M"]) == (recorded["regime"], recorded["M"]), "analysis cell identity")
        need(independent["median_ratio"] == recorded["median_of_8_paired_ratios"], "analysis median")
        need(independent["bootstrap_95"]["lower"] == recorded["bootstrap_95"]["lower"], "analysis lower")
        need(independent["bootstrap_95"]["upper"] == recorded["bootstrap_95"]["upper"], "analysis upper")
        need(independent["bootstrap_95"]["draws_sha256"] == recorded["bootstrap_95"]["draws_sha256"], "analysis draws")
    primary = next(row for row in cells if row["regime"] == "n23_k16" and row["M"] == 512)

    aggregate_count = verify_archive(RUN / "raw_outputs.tar.gz", raw_manifest)
    phase_counts = {}
    union: set[str] = set()
    for phase in ("control", "checker", "benchmark"):
        manifest = load(RUN / f"raw_{phase}_manifest.json")
        count = verify_archive(RUN / f"raw_{phase}_outputs.tar.gz", manifest)
        phase_counts[phase] = count
        current = {row["path"] for row in manifest["files"]}
        need(not union.intersection(current), "phase archive overlap")
        union.update(current)
    need(union == set(raw_index), "phase/aggregate member sets")

    raw_result = load(RUN / "raw-result.json")
    need(raw_result["launched"] == raw_result["valid"] == 384 and raw_result["all384_valid"] is True, "raw result counts")
    need(raw_result["analysis_sha256"] == sha(RUN / "analysis.json"), "raw result analysis binding")
    need(raw_result["benchmark_receipts_sha256"] == sha(RUN / "benchmark_receipts.jsonl"), "raw result receipt binding")
    control_receipt = load(RUN / "control_receipt.json")
    checker_receipt = load(RUN / "checker_receipt.json")
    for receipt, label in ((control_receipt, "control"), (checker_receipt, "checker")):
        need(receipt["valid"] is True and receipt["classification"] == "completed_valid", f"{label} receipt")
        need(receipt["exit_code"] == 0 and receipt["telemetry_valid"] is True, f"{label} telemetry")
        need(not receipt["watchdog_reached"] and not receipt["memory_cap_reached"], f"{label} censor")
    independent_replay = load(RUN / "independent_replay.json")
    need(independent_replay["status"] == "passed" and len(independent_replay["regimes"]) == 2, "checker replay")

    manifest_original = load(RUN / "manifest.yaml")
    manifest_v2 = load(RUN / "manifest_v2.yaml")
    need(manifest_original["run"]["result"]["certificate"]["kind"] == "finite point decomposition replay", "original invalid enum history")
    need(manifest_v2["run"]["result"]["certificate"]["kind"] == "decomposition", "corrected enum")
    reduced = copy.deepcopy(manifest_v2)
    reduced["run"].pop("supersedes")
    reduced["run"].pop("supersession_note")
    reduced["run"]["result"]["certificate"]["kind"] = manifest_original["run"]["result"]["certificate"]["kind"]
    need(reduced == manifest_original, "manifest correction changed undeclared fields")
    need(sha(RUN / "manifest.yaml") == "5526c489d1158d98efbf9466f62bd07c2cf21ef20e048aae239db56a37bd4fee", "original manifest hash")
    need(sha(RUN / "manifest_v2.yaml") == "91b2fc619c75ab9f66e1f7ef0934dee991793654e8c56e0d2bf21175dbb835a8", "v2 manifest hash")
    registry_text = (ROOT / "tools/run_supersession_registry.yaml").read_text()
    need(registry_text.count("run_id: RUN-KIC-ba86d9") == 1, "registry row count")
    for value in (sha(RUN / "manifest.yaml"), sha(RUN / "manifest_v2.yaml")):
        need(value in registry_text, "registry manifest hash")
    correction = load(CONTROL / "manifest_correction_check.json")
    need(correction["original_manifest_unchanged"] is True and correction["measurements_repeated"] == 0, "correction receipt")

    attempt = load(RUN / "stage_a_attempt_01_manifest.json")
    interruption = load(CONTROL / "runtime_interruption_01.json")
    need(attempt["scientific_processes"] == 0 and interruption["scientific_processes_launched"] == 0, "prior interruptions as observations")
    need(sha(RUN / "stage_a_attempt_01_preserved.tar.gz") == attempt["archive_sha256"], "prior attempt archive")

    need(git("show", "-s", "--format=%P", SNAPSHOT) == SNAPSHOT_PARENT, "snapshot parent")
    need(git("show", "-s", "--format=%P", BINDING) == SNAPSHOT, "binding parent")
    need(git("show", "-s", "--format=%P", ADMISSION) != "", "admission commit")
    need(git("show", "-s", "--format=%P", CLAIM) == BINDING, "claim parent")
    published_ref = "origin/codex/pair-reuse-20260922"
    for commit in (SNAPSHOT, BINDING, ADMISSION, CLAIM):
        remote_refs = git("branch", "-r", "--contains", commit).splitlines()
        need(any(row.strip() == published_ref for row in remote_refs), f"unpublished commit {commit}")
    snapshot_hashes = science_receipt["artifact_sha256_excluding_this_receipt"]
    need(len(snapshot_hashes) + 1 == 112, "snapshot bound path count")
    protected = (
        "research/pair_reuse_20260922/blind_review_handoff.json",
        "research/pair_reuse_20260922/review/blind_admission.json",
        "research/pair_reuse_20260922/claims/TASK-20260922-a5ab4c",
        "research/pair_reuse_20260922/WORKSTATE.json",
        "research/pair_reuse_20260922/dispatch_",
        "research/pair_reuse_20260922/focus_",
    )
    checked_snapshot_paths = 0
    for relative, expected_hash in snapshot_hashes.items():
        if relative.startswith(protected):
            continue
        need(sha(ROOT / relative) == expected_hash, f"snapshot current hash {relative}")
        blob = subprocess.run(
            ["git", "show", f"{SNAPSHOT}:{relative}"], cwd=ROOT, check=True, capture_output=True
        ).stdout
        need(sha_bytes(blob) == expected_hash, f"snapshot blob hash {relative}")
        checked_snapshot_paths += 1
    snapshot_blob = subprocess.run(
        ["git", "show", f"{SNAPSHOT}:research/pair_reuse_20260922/science_snapshot_receipt.json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout
    need(snapshot_blob == (CONTROL / "science_snapshot_receipt.json").read_bytes(), "snapshot receipt blob")

    source = (CODE / "native.cpp").read_text()
    runner = (CODE / "runner.py").read_text()
    need('root.at("generator")' not in source and "oracle_metadata" not in source[source.index("static vector<Point> read_panel"):], "worker reads advice")
    need("Base base=construct_base(n19_path)" in source and "Table table=build_table" in source, "fresh base/table")
    need("for(Point p:q)answers.push_back" in source, "all-query loop")
    need("subprocess.Popen(argv,cwd=raw,env=env" in runner, "direct child Popen")
    need("KQ_NOTE_EXIT" in runner and "os.wait4(p.pid" in runner, "kqueue/wait4 boundary")
    need('"HOME":str(home),"TMPDIR":str(temp)' in runner, "fresh HOME/TMPDIR")

    benchmark_supervisor = load(CONTROL / "supervisor/benchmark.receipt.json")
    output = {
        "schema": "crypto.autoresearch.pair_reuse_source_rederive.v1",
        "task_id": "TASK-20260922-a0c874",
        "experiment_id": "EXP-KIC-d9c828",
        "run_id": "RUN-KIC-ba86d9",
        "experiment_processes_launched": 0,
        "producer_modules_imported": [],
        "frozen_hashes": frozen,
        "source_binary_custody": {
            "source_hashes": source_closure["source_sha256"],
            "binary_sha256": source_closure["binary_sha256"],
            "binary_mode": "0755",
            "pre_control_mode_correction": "0644_to_0755_content_unchanged",
            "scientific_snapshot": SNAPSHOT,
            "snapshot_parent": SNAPSHOT_PARENT,
            "snapshot_bound_paths": 112,
            "snapshot_paths_checked_without_sibling_lane": checked_snapshot_paths + 1,
            "binding_commit": BINDING,
            "review_admission_commit": ADMISSION,
            "exclusive_claim_commit": CLAIM,
            "published_remote_ref": published_ref,
        },
        "finite_rederivation": regime_results,
        "proves_too_much": {
            "wrong_inverse_sign_key_sum": "rejected",
            "noninvariant_same_cardinality_base": "rejected",
            "worker_advice_interface": "Q_only_512_point_file_plus_public_base_recipe",
            "construction_gain_multiplied_by_M": False,
        },
        "process_accounting": {
            "control_processes": 1,
            "checker_processes": 1,
            "benchmark_jobs": len(receipts),
            "benchmark_queries_replayed": total_queries,
            "benchmark_positive_witnesses_replayed": total_witnesses,
            "benchmark_child_wall_seconds_sum": sum(row["wall_seconds"] for row in receipts),
            "benchmark_child_user_seconds_sum": sum(row["wait4"]["user_seconds"] for row in receipts),
            "benchmark_child_system_seconds_sum": sum(row["wait4"]["system_seconds"] for row in receipts),
            "benchmark_max_wait4_rss_bytes": max(row["wait4"]["peak_rss"] for row in receipts),
            "benchmark_max_sampled_footprint_bytes": max(row["sampling"]["peak_bytes"] or 0 for row in receipts),
            "benchmark_parent_validation_seconds_sum": stage_totals["parent_validation_seconds"],
            "benchmark_outer_supervisor_wall_seconds": benchmark_supervisor["wall_seconds"],
            "benchmark_outer_wait4_user_seconds": benchmark_supervisor["wait4"]["user_seconds"],
            "benchmark_outer_wait4_system_seconds": benchmark_supervisor["wait4"]["system_seconds"],
            "benchmark_outer_wait4_rss_highwater_bytes": benchmark_supervisor["wait4"]["maximum_rss_bytes"],
            "host_load_average_before": benchmark_supervisor["host_load_average_before"],
            "host_load_average_after": benchmark_supervisor["host_load_average_after"],
            "logical_cpu_count": benchmark_supervisor["logical_cpu_count"],
            "native_stage_totals_seconds": stage_totals,
            "raw_archive_members": aggregate_count,
            "phase_archive_members": phase_counts,
            "raw_archive_sha256": raw_manifest["archive_sha256"],
        },
        "paired_statistics": cells,
        "primary": {
            "regime": "n23_k16",
            "M": 512,
            "median_ratio": primary["median_ratio"],
            "bootstrap_95": primary["bootstrap_95"],
            "predicate_median_at_most_0_90": primary["median_ratio"] <= 0.90,
            "predicate_upper_below_one": primary["bootstrap_95"]["upper"] < 1,
        },
        "manifest_correction": {
            "original_sha256": sha(RUN / "manifest.yaml"),
            "replacement_sha256": sha(RUN / "manifest_v2.yaml"),
            "undeclared_field_differences": 0,
            "measurements_repeated": 0,
            "registry_entries": 1,
        },
        "prior_attempts": {
            "stage_a_attempt_01_scientific_processes": 0,
            "inference_capacity_interruption_scientific_processes": 0,
            "scientific_observations": 0,
        },
        "claim_boundary": "finite public-synthetic point decomposition and cold-job cost only; no full index-calculus or rho improvement established",
        "status": "passed",
    }
    print(json.dumps(output, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
