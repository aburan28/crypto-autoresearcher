#!/usr/bin/env python3
"""Test public x-coset routing in a source-resolving 16-list k-tree."""

from __future__ import annotations

import hashlib
import json
import math
import os
import statistics
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sage.all import EllipticCurve, GF, matrix, is_prime


ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = ROOT / "ecdlp_index_calculus_state"
RESEARCH_DIR = ROOT / "research"
CONTRACT = STATE_DIR / "experiment_contract_p1482_coordinate_routed_wagner_tree.md"
OUT = STATE_DIR / "p1482_coordinate_routed_wagner_tree.json"
NOTE = RESEARCH_DIR / "p1482_coordinate_routed_wagner_tree.md"

SCHEMA = "ecdlp.p1482_coordinate_routed_wagner_tree.v1"
SCHEDULE_COUNT = 32
EXPECTED = {
    CONTRACT: "fb581332d8cac0403d8ab287fc6ff7b493edd942ebcd31cc7a137f0e5b22bee1",
    STATE_DIR / "p1475_residual_character_support_concentration.json":
        "752245f0ee00f90d3a4cb1d3a1ed987e40e3f72a885e9967819e86d303382eb1",
    STATE_DIR / "p1475_residual_character_support_concentration_audit.json":
        "2e5f72b81f2e8a2578e5d1008a3c8beeb670896593ba020b8a5228fbb995d18b",
    STATE_DIR / "p1476_m_ary_sparse_deck_exponent_boundary.json":
        "c29426c61c687560b45e38cae1c50f18e89c2846a6d599c6f4583fc98ec70e5f",
    STATE_DIR / "p1476_m_ary_sparse_deck_exponent_boundary_audit.json":
        "752190e01263740ed8b0db73ae4fe3d092797ff1e1991a48438a8f66d2bcc138",
    STATE_DIR / "p1481_finite_field_serial_message_propagation.json":
        "5d646536365097faeaca843a26ba799e62fce941e4a2d9bf8ae3cb154e734977",
    STATE_DIR / "p1481_finite_field_serial_message_propagation_audit.json":
        "a63c529d43599d8e7fc888ac3649e0723496be3a940101cf3f055a40cf8f616d",
}
FIXTURES = [
    {"L": 4, "p": 1033, "order": 1061, "a": 1, "b": 1},
    {"L": 8, "p": 32801, "order": 32479, "a": 1, "b": 5},
    {"L": 16, "p": 1048609, "order": 1047539, "a": 5, "b": 7},
    {"L": 32, "p": 33554593, "order": 33563891, "a": 3, "b": 9},
]


@dataclass(frozen=True)
class Record:
    point: Any
    coefficients: tuple[int, ...]
    source: tuple[Any, ...]
    scalar: int | None


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_int(*parts: object) -> int:
    material = "|".join(str(part) for part in parts).encode("ascii")
    return int.from_bytes(hashlib.sha256(material).digest(), "big")


def point_key(point: Any) -> tuple[int, int] | tuple[str]:
    return ("O",) if point.is_zero() else (int(point[0]), int(point[1]))


def point_json(point: Any) -> dict[str, Any]:
    if point.is_zero():
        return {"infinity": True}
    return {"x": int(point[0]), "y": int(point[1])}


def build_context(fixture: dict[str, int]) -> dict[str, Any]:
    p, q, L = fixture["p"], fixture["order"], fixture["L"]
    if not is_prime(p) or not is_prime(q) or (p - 1) % L:
        raise RuntimeError("P1482 fixture arithmetic failure")
    field = GF(p)
    curve = EllipticCurve(field, [fixture["a"], fixture["b"]])
    if int(curve.cardinality()) != q or curve.is_supersingular():
        raise RuntimeError("P1482 curve failure")
    generator = None
    for x_integer in range(p):
        lifts = sorted(curve.lift_x(field(x_integer), all=True), key=lambda point: int(point[1]))
        if lifts:
            generator = lifts[0]
            break
    if generator is None or int(generator.order()) != q:
        raise RuntimeError("P1482 generator failure")
    h = field.multiplicative_generator() ** ((p - 1) // L)
    if int(h.multiplicative_order()) != L:
        raise RuntimeError("P1482 endpoint subgroup failure")
    zeta = field.multiplicative_generator() ** ((p - 1) // L)
    coset_table = {int(zeta**index): index for index in range(L)}
    if len(coset_table) != L:
        raise RuntimeError("P1482 quotient-label table failure")
    return {
        "fixture": fixture,
        "field": field,
        "curve": curve,
        "generator": generator,
        "identity": 0 * generator,
        "h": h,
        "coset_table": coset_table,
    }


def factor_roots(context: dict[str, Any]) -> list[int]:
    roots = []
    value = context["field"].one()
    for _ in range(context["fixture"]["L"]):
        if context["curve"].lift_x(value, all=True):
            roots.append(int(value))
        value *= context["h"]
    return sorted(set(roots))


def bsgs_logs(context: dict[str, Any], points: list[Any]) -> dict[Any, int]:
    q = context["fixture"]["order"]
    width = math.isqrt(q) + 1
    baby = {}
    value = context["identity"]
    for index in range(width):
        baby.setdefault(point_key(value), index)
        value += context["generator"]
    giant = width * context["generator"]
    output = {}
    for point in points:
        gamma = point
        found = None
        for step in range(width + 1):
            key = point_key(gamma)
            if key in baby:
                candidate = (step * width + baby[key]) % q
                if candidate * context["generator"] == point:
                    found = candidate
                    break
            gamma -= giant
        if found is None:
            raise RuntimeError("P1482 toy scalar recovery failure")
        output[point_key(point)] = found
    return output


def make_leaves(
    context: dict[str, Any], roots: list[int], scalar_logs: dict[Any, int] | None
) -> list[Record]:
    records = []
    dimension = len(roots)
    q = context["fixture"]["order"]
    for factor_index, root in enumerate(roots):
        lifts = sorted(
            context["curve"].lift_x(context["field"](root), all=True),
            key=lambda point: int(point[1]),
        )
        if len(lifts) != 2 or lifts[0] != -lifts[1]:
            raise RuntimeError("P1482 sign pair failure")
        for sign_index, point in enumerate(lifts):
            coefficients = [0] * dimension
            coefficients[factor_index] = 1 if sign_index == 0 else -1
            scalar = None if scalar_logs is None else scalar_logs[point_key(point)] % q
            records.append(Record(point, tuple(coefficients), (point,), scalar))
    return records


def coordinate_label(context: dict[str, Any], point: Any) -> int | None:
    if point.is_zero() or int(point[0]) == 0:
        return None
    fixture, field = context["fixture"], context["field"]
    residue = int(field(int(point[0])) ** ((fixture["p"] - 1) // fixture["L"]))
    if residue not in context["coset_table"]:
        raise RuntimeError("P1482 quotient-label lookup failure")
    return context["coset_table"][residue]


def coordinate_target(L: int, schedule: int, level: int, node: int) -> int:
    return digest_int("P1482", "coordinate", L, schedule, level, node) % L


def hash_accept(L: int, schedule: int, level: int, node: int, point: Any) -> bool:
    return digest_int("P1482", "hash", L, level, node, schedule, int(point[0])) % L == 0


def scalar_centers(fixture: dict[str, int], schedule: int, target_scalar: int = 0) -> dict[tuple[int, int], int]:
    q = fixture["order"]
    centers: dict[tuple[int, int], int] = {}
    running = 0
    for node in range(7):
        center = digest_int("P1482", "scalar-center", fixture["L"], schedule, node, target_scalar) % q
        centers[(1, node)] = center
        running = (running + center) % q
    centers[(1, 7)] = (target_scalar - running) % q
    for level, count in ((2, 4), (3, 2)):
        for node in range(count):
            centers[(level, node)] = (
                centers[(level - 1, 2 * node)] + centers[(level - 1, 2 * node + 1)]
            ) % q
    return centers


def scalar_accept(
    fixture: dict[str, int], scalar: int, center: int, level: int
) -> bool:
    q, L = fixture["order"], fixture["L"]
    residue = (scalar - center) % q
    distance = min(residue, q - residue)
    radius = math.ceil(q / (2 * (L**level)))
    return distance <= radius


def merge_node(
    context: dict[str, Any], left: list[Record], right: list[Record], lane: str,
    schedule: int, level: int, node: int, centers: dict[tuple[int, int], int] | None,
) -> tuple[list[Record], dict[str, Any]]:
    fixture = context["fixture"]
    output = []
    additions = 0
    filters = 0
    identity_rejections = 0
    for first in left:
        for second in right:
            additions += 1
            point = first.point + second.point
            if point.is_zero():
                identity_rejections += 1
                continue
            filters += 1
            scalar = None
            if lane == "coordinate":
                accepted = coordinate_label(context, point) == coordinate_target(
                    fixture["L"], schedule, level, node
                )
            elif lane == "hash":
                accepted = hash_accept(fixture["L"], schedule, level, node, point)
            elif lane == "scalar_control":
                if first.scalar is None or second.scalar is None or centers is None:
                    raise RuntimeError("P1482 missing scalar-control state")
                scalar = (first.scalar + second.scalar) % fixture["order"]
                accepted = scalar_accept(fixture, scalar, centers[(level, node)], level)
            else:
                raise ValueError(lane)
            if not accepted:
                continue
            coefficients = tuple(a + b for a, b in zip(first.coefficients, second.coefficients))
            output.append(Record(point, coefficients, first.source + second.source, scalar))
    distinct_points = len({point_key(record.point) for record in output})
    distinct_coefficients = len({record.coefficients for record in output})
    source_length = 2**level
    return output, {
        "level": level,
        "node": node,
        "left_records": len(left),
        "right_records": len(right),
        "cartesian_product": len(left) * len(right),
        "group_additions": additions,
        "filter_evaluations": filters,
        "identity_rejections": identity_rejections,
        "accepted_records": len(output),
        "distinct_point_count": distinct_points,
        "distinct_coefficient_count": distinct_coefficients,
        "source_reference_count": len(output) * source_length,
        "storage_units": len(output) * (2 + len(output[0].coefficients) + source_length) if output else 0,
    }


def canonical_row(coefficients: tuple[int, ...]) -> tuple[int, ...] | None:
    if not any(coefficients):
        return None
    first = next(value for value in coefficients if value)
    return tuple(-value for value in coefficients) if first < 0 else coefficients


def verify_relation(context: dict[str, Any], roots: list[int], record: Record) -> bool:
    if len(record.source) != 16 or not sum(record.source, context["identity"]).is_zero():
        return False
    canonical = [
        sorted(context["curve"].lift_x(context["field"](root), all=True), key=lambda point: int(point[1]))[0]
        for root in roots
    ]
    reconstructed = context["identity"]
    for coefficient, point in zip(record.coefficients, canonical):
        reconstructed += coefficient * point
    return reconstructed.is_zero()


def root_join_zero(
    context: dict[str, Any], roots: list[int], left: list[Record], right: list[Record]
) -> tuple[dict[tuple[int, ...], str], dict[str, Any]]:
    right_index: dict[Any, list[Record]] = {}
    for record in right:
        right_index.setdefault(point_key(record.point), []).append(record)
    rows: dict[tuple[int, ...], str] = {}
    probes = 0
    matches = 0
    zero_rejections = 0
    duplicate_rejections = 0
    invalid_sources = 0
    for first in left:
        probes += 1
        for second in right_index.get(point_key(-first.point), []):
            matches += 1
            coefficients = tuple(a + b for a, b in zip(first.coefficients, second.coefficients))
            row = canonical_row(coefficients)
            if row is None:
                zero_rejections += 1
                continue
            combined = Record(
                first.point + second.point,
                coefficients,
                first.source + second.source,
                None if first.scalar is None else (first.scalar + second.scalar) % context["fixture"]["order"],
            )
            if not verify_relation(context, roots, combined):
                invalid_sources += 1
                continue
            if row in rows:
                duplicate_rejections += 1
                continue
            source_material = b"|".join(
                repr(point_key(point)).encode("ascii") for point in combined.source
            )
            rows[row] = hashlib.sha256(source_material).hexdigest()
    return rows, {
        "right_hash_inserts": len(right),
        "left_hash_probes": probes,
        "inverse_match_count": matches,
        "zero_vector_rejections": zero_rejections,
        "duplicate_row_rejections": duplicate_rejections,
        "invalid_source_count": invalid_sources,
        "exact_unique_row_count": len(rows),
    }


def build_top_lists(
    context: dict[str, Any], leaves: list[Record], lane: str, schedule: int,
    target_scalar: int = 0,
) -> tuple[list[Record], list[Record], list[dict[str, Any]]]:
    centers = scalar_centers(context["fixture"], schedule, target_scalar) if lane == "scalar_control" else None
    current = [leaves for _ in range(16)]
    node_rows = []
    for level in range(1, 4):
        next_level = []
        for node in range(len(current) // 2):
            merged, metrics = merge_node(
                context, current[2 * node], current[2 * node + 1], lane,
                schedule, level, node, centers,
            )
            next_level.append(merged)
            node_rows.append(metrics)
        current = next_level
    return current[0], current[1], node_rows


def run_schedule(
    context: dict[str, Any], roots: list[int], leaves: list[Record], lane: str, schedule: int
) -> dict[str, Any]:
    started = time.perf_counter()
    left, right, nodes = build_top_lists(context, leaves, lane, schedule)
    rows, root = root_join_zero(context, roots, left, right)
    construction_work = sum(
        node["group_additions"] + node["filter_evaluations"] for node in nodes
    ) + root["right_hash_inserts"] + root["left_hash_probes"] + root["inverse_match_count"]
    return {
        "schedule": schedule,
        "nodes": nodes,
        "level3_left_records": len(left),
        "level3_right_records": len(right),
        "all_nonroot_nodes_nonempty": all(node["accepted_records"] > 0 for node in nodes),
        "root": root,
        "rows": rows,
        "construction_work": construction_work,
        "peak_node_records": max((node["accepted_records"] for node in nodes), default=0),
        "peak_node_storage_units": max((node["storage_units"] for node in nodes), default=0),
        "wall_seconds": time.perf_counter() - started,
    }


def lane_rank(context: dict[str, Any], rows: set[tuple[int, ...]]) -> int:
    if not rows:
        return 0
    return int(matrix(GF(context["fixture"]["order"]), [list(row) for row in sorted(rows)]).rank())


def run_lane(
    context: dict[str, Any], roots: list[int], leaves: list[Record], lane: str
) -> dict[str, Any]:
    schedules = []
    all_rows: set[tuple[int, ...]] = set()
    duplicate_across_schedules = 0
    for schedule in range(SCHEDULE_COUNT):
        result = run_schedule(context, roots, leaves, lane, schedule)
        for row in result.pop("rows"):
            if row in all_rows:
                duplicate_across_schedules += 1
            all_rows.add(row)
        schedules.append(result)
    rank = lane_rank(context, all_rows)
    total_work = sum(row["construction_work"] for row in schedules)
    return {
        "lane": lane,
        "schedule_count": SCHEDULE_COUNT,
        "schedules": schedules,
        "aggregate": {
            "total_construction_work": total_work,
            "peak_node_records": max(row["peak_node_records"] for row in schedules),
            "peak_node_storage_units": max(row["peak_node_storage_units"] for row in schedules),
            "nonempty_schedule_count": sum(row["all_nonroot_nodes_nonempty"] for row in schedules),
            "root_inverse_match_count": sum(row["root"]["inverse_match_count"] for row in schedules),
            "root_zero_vector_rejections": sum(row["root"]["zero_vector_rejections"] for row in schedules),
            "root_invalid_source_count": sum(row["root"]["invalid_source_count"] for row in schedules),
            "exact_unique_row_count": len(all_rows),
            "duplicate_rows_across_schedules": duplicate_across_schedules,
            "relation_rank": rank,
            "factor_dimension": len(roots),
            "work_per_independent_row": total_work / rank if rank else None,
            "row_sha256": hashlib.sha256(
                b"\n".join(repr(row).encode("ascii") for row in sorted(all_rows))
            ).hexdigest(),
        },
    }


def root_join_target(
    context: dict[str, Any], left: list[Record], right: list[Record], target: Any
) -> tuple[tuple[Any, ...] | None, dict[str, int]]:
    right_index: dict[Any, list[Record]] = {}
    for record in right:
        right_index.setdefault(point_key(record.point), []).append(record)
    probes = 0
    matches = 0
    invalid = 0
    source = None
    for first in left:
        probes += 1
        needed = target - first.point
        for second in right_index.get(point_key(needed), []):
            matches += 1
            candidate = first.source + second.source
            if len(candidate) != 16 or sum(candidate, context["identity"]) != target:
                invalid += 1
            elif source is None:
                source = candidate
    return source, {"right_hash_inserts": len(right), "left_hash_probes": probes,
                    "target_match_count": matches, "invalid_source_count": invalid}


def run_coordinate_descent(
    context: dict[str, Any], roots: list[int], leaves: list[Record]
) -> dict[str, Any]:
    queries = []
    all_success = True
    for target_index in range(8):
        scalar = 1 + digest_int("P1482", "descent", context["fixture"]["L"], target_index) % (
            context["fixture"]["order"] - 1
        )
        target = scalar * context["generator"]
        found = None
        schedule_rows = []
        total_work = 0
        for schedule in range(SCHEDULE_COUNT):
            left, right, nodes = build_top_lists(context, leaves, "coordinate", schedule)
            source, root = root_join_target(context, left, right, target)
            work = sum(node["group_additions"] + node["filter_evaluations"] for node in nodes)
            work += root["right_hash_inserts"] + root["left_hash_probes"] + root["target_match_count"]
            total_work += work
            schedule_rows.append({"schedule": schedule, "work": work, **root, "source_found": source is not None})
            if source is not None and found is None:
                found = source
        all_success &= found is not None
        queries.append({
            "target_index": target_index,
            "target_scalar": scalar,
            "target": point_json(target),
            "source_found": found is not None,
            "verified_source": [point_json(point) for point in found] if found else None,
            "total_work": total_work,
            "schedules": schedule_rows,
        })
    return {"executed": True, "all_targets_succeeded": all_success, "queries": queries}


def fit_slope(xs: list[float], ys: list[float]) -> dict[str, Any]:
    def slope(sub_x: list[float], sub_y: list[float]) -> float:
        lx, ly = [math.log(value) for value in sub_x], [math.log(value) for value in sub_y]
        mx, my = statistics.mean(lx), statistics.mean(ly)
        return sum((x - mx) * (y - my) for x, y in zip(lx, ly)) / sum((x - mx) ** 2 for x in lx)

    leave_one_out = [
        slope(
            [value for index, value in enumerate(xs) if index != omitted],
            [value for index, value in enumerate(ys) if index != omitted],
        )
        for omitted in range(len(xs))
    ]
    return {"slope": slope(xs, ys), "leave_one_out": leave_one_out,
            "leave_one_out_min": min(leave_one_out), "leave_one_out_max": max(leave_one_out)}


def write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    with temporary.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def render_note(payload: dict[str, Any]) -> str:
    return "\n".join([
        "# P1482 coordinate-routed Wagner tree",
        "",
        "## Status",
        "",
        f"`{payload['status']}`",
        "",
        f"Coordinate ranks: `{[cell['coordinate']['aggregate']['relation_rank'] for cell in payload['cells']]}`.",
        "",
        f"Hash-control ranks: `{[cell['hash']['aggregate']['relation_rank'] for cell in payload['cells']]}`.",
        "",
        f"Scalar-control ranks: `{[cell['scalar_control']['aggregate']['relation_rank'] for cell in payload['cells']]}`.",
        "",
        f"Coordinate descent executed on all fixtures: `{payload['gates']['coordinate_descent_all_fixtures_executed']}`.",
        "",
        "The scalar lane is a toy-log implementation control. Only the public",
        "coordinate lane can support an ECDLP claim.",
        "",
    ])


def main() -> int:
    os.chdir(ROOT)
    observed = {str(path.relative_to(ROOT)): sha256_file(path) for path in EXPECTED}
    expected = {str(path.relative_to(ROOT)): digest for path, digest in EXPECTED.items()}
    if observed != expected:
        raise RuntimeError("frozen P1482 input mismatch")

    cells = []
    for fixture in FIXTURES:
        context = build_context(fixture)
        roots = factor_roots(context)
        public_leaves = make_leaves(context, roots, None)
        coordinate = run_lane(context, roots, public_leaves, "coordinate")
        hash_control = run_lane(context, roots, public_leaves, "hash")
        public_phase_sealed_at = time.time_ns()
        point_logs = bsgs_logs(context, [record.point for record in public_leaves])
        scalar_leaves = make_leaves(context, roots, point_logs)
        scalar_control = run_lane(context, roots, scalar_leaves, "scalar_control")
        coordinate_rank = coordinate["aggregate"]["relation_rank"]
        descent = (
            run_coordinate_descent(context, roots, public_leaves)
            if coordinate_rank >= max(1, len(roots) - 1)
            else {"executed": False, "reason": "coordinate relation rank below N-1"}
        )
        cell = {
            "fixture": fixture,
            "generator": point_json(context["generator"]),
            "factor_root_count": len(roots),
            "signed_leaf_count": len(public_leaves),
            "factor_root_sha256": hashlib.sha256(
                b"|".join(str(root).encode("ascii") for root in roots)
            ).hexdigest(),
            "public_candidate_phase_sealed_at_ns": public_phase_sealed_at,
            "coordinate": coordinate,
            "hash": hash_control,
            "scalar_control": scalar_control,
            "coordinate_descent": descent,
        }
        cells.append(cell)
        print(json.dumps({
            "L": fixture["L"],
            "roots": len(roots),
            "coordinate": coordinate["aggregate"],
            "hash": hash_control["aggregate"],
            "scalar_control": scalar_control["aggregate"],
            "descent_executed": descent["executed"],
        }, sort_keys=True), flush=True)

    xs = [cell["fixture"]["L"] for cell in cells]
    coordinate_work = [cell["coordinate"]["aggregate"]["total_construction_work"] for cell in cells]
    coordinate_storage = [cell["coordinate"]["aggregate"]["peak_node_storage_units"] for cell in cells]
    fits = {
        "coordinate_total_construction_work": fit_slope(xs, coordinate_work),
        "coordinate_peak_storage": fit_slope(xs, [max(1, value) for value in coordinate_storage]),
    }
    scalar_pass = all(
        cell["scalar_control"]["aggregate"]["exact_unique_row_count"] > 0
        and cell["scalar_control"]["aggregate"]["root_invalid_source_count"] == 0
        for cell in cells
    )
    no_invalid = all(
        cell[lane]["aggregate"]["root_invalid_source_count"] == 0
        for cell in cells for lane in ("coordinate", "hash", "scalar_control")
    )
    coordinate_nonempty = all(
        cell["coordinate"]["aggregate"]["nonempty_schedule_count"] == SCHEDULE_COUNT
        for cell in cells
    )
    coordinate_beats_hash_holdout = all(
        cell["coordinate"]["aggregate"]["exact_unique_row_count"]
        > cell["hash"]["aggregate"]["exact_unique_row_count"]
        and cell["coordinate"]["aggregate"]["relation_rank"]
        > cell["hash"]["aggregate"]["relation_rank"]
        for cell in cells[2:]
    )
    rank_gate = all(
        cell["coordinate"]["aggregate"]["relation_rank"] >= max(1, cell["factor_root_count"] - 1)
        for cell in cells
    )
    work_fit = fits["coordinate_total_construction_work"]
    storage_fit = fits["coordinate_peak_storage"]
    work_gate = work_fit["slope"] <= 2 + 1e-12 and work_fit["leave_one_out_max"] <= 2 + 1e-12
    storage_gate = storage_fit["slope"] <= 2 + 1e-12 and storage_fit["leave_one_out_max"] <= 2 + 1e-12
    finite_work_per_row = all(
        cell["coordinate"]["aggregate"]["work_per_independent_row"] is not None for cell in cells
    )
    descent_executed = all(cell["coordinate_descent"]["executed"] for cell in cells)
    descent_pass = descent_executed and all(
        cell["coordinate_descent"]["all_targets_succeeded"] for cell in cells
    )
    signal = all((scalar_pass, no_invalid, coordinate_nonempty, coordinate_beats_hash_holdout,
                  rank_gate, work_gate, storage_gate, finite_work_per_row, descent_pass))
    status = (
        "OBSERVATION_P1482_COORDINATE_ROUTED_WAGNER_SIGNAL"
        if signal
        else "NEGATIVE_RESULT_P1482_X_COSET_ROUTING_NOT_ADDITIVELY_COMPATIBLE"
    )
    payload = {
        "schema": SCHEMA,
        "status": status,
        "schedule_count": SCHEDULE_COUNT,
        "cells": cells,
        "fits": fits,
        "gates": {
            "scalar_positive_control_exact_rows_every_fixture": scalar_pass,
            "zero_invalid_sources_all_lanes": no_invalid,
            "coordinate_all_nodes_nonempty_every_schedule": coordinate_nonempty,
            "coordinate_rows_and_rank_beat_hash_on_L16_L32": coordinate_beats_hash_holdout,
            "coordinate_rank_at_least_N_minus_one_every_fixture": rank_gate,
            "coordinate_total_work_all_slopes_at_most_two": work_gate,
            "coordinate_peak_storage_all_slopes_at_most_two": storage_gate,
            "coordinate_work_per_independent_row_finite": finite_work_per_row,
            "coordinate_descent_all_fixtures_executed": descent_executed,
            "coordinate_descent_all_targets_succeeded": descent_pass,
            "toy_scalars_opened_after_public_candidate_phase": True,
            "rho_and_full_pipeline_not_waived": True,
        },
        "coordinate_routed_wagner_signal": signal,
        "conditional_exponent_ledger": {
            "factor_base_scale": "L=q^(1/5)",
            "candidate_tree_if_gates_pass": "L^2=q^(2/5)",
            "linear_algebra_if_rank_passes": "L^2=q^(2/5)",
            "target_descent_requirement": "L^2=q^(2/5)",
            "status": "conditional; candidate must satisfy public routing, rank, and descent",
        },
        "frozen_files": observed,
        "boundary": (
            "Scalar-window routing is oracle-only. A coordinate/hash tie or empty root stream shows "
            "that public x labels did not reproduce compatible additive projections."
        ),
        "next_action": (
            "If coordinate routing fails while scalar control passes, close nonadaptive x-coset k-tree "
            "routing and require either an efficiently computable approximate homomorphism with source "
            "recovery or a different transfer. Do not tune bucket labels post hoc."
        ),
    }
    write_atomic(OUT, (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    write_atomic(NOTE, render_note(payload).encode("utf-8"))
    print(json.dumps({
        "output": str(OUT.relative_to(ROOT)),
        "note": str(NOTE.relative_to(ROOT)),
        "status": status,
        "coordinate_ranks": [cell["coordinate"]["aggregate"]["relation_rank"] for cell in cells],
        "hash_ranks": [cell["hash"]["aggregate"]["relation_rank"] for cell in cells],
        "scalar_ranks": [cell["scalar_control"]["aggregate"]["relation_rank"] for cell in cells],
        "fits": fits,
        "signal": signal,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
