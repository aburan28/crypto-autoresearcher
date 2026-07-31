#!/usr/bin/env python3
"""Repair k-tree occupancy and scalar calibration after P1482."""

from __future__ import annotations

import hashlib
import json
import math
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from p1482_coordinate_routed_wagner_tree import (
    Record,
    build_context,
    canonical_row,
    digest_int,
    factor_roots,
    fit_slope,
    lane_rank,
    make_leaves,
    point_json,
    point_key,
    root_join_target,
    verify_relation,
    write_atomic,
)


ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = ROOT / "ecdlp_index_calculus_state"
RESEARCH_DIR = ROOT / "research"
CONTRACT = STATE_DIR / "experiment_contract_p1483_occupancy_calibrated_wagner_routing.md"
OUT = STATE_DIR / "p1483_occupancy_calibrated_wagner_routing.json"
NOTE = RESEARCH_DIR / "p1483_occupancy_calibrated_wagner_routing.md"

SCHEMA = "ecdlp.p1483_occupancy_calibrated_wagner_routing.v1"
SCHEDULE_COUNT = 32
EXPECTED = {
    CONTRACT: "f232769c8a4056528ccdaf9bce296750fcd17531da94e2d4698cbdc943970afa",
    ROOT / "tasks/ecdlp_index_calculus/p1482_coordinate_routed_wagner_tree.py":
        "14e1255f095df4c1219d01d43042bc0e03c893504469e6430943dcfce3820bca",
    STATE_DIR / "p1481_finite_field_serial_message_propagation.json":
        "5d646536365097faeaca843a26ba799e62fce941e4a2d9bf8ae3cb154e734977",
    STATE_DIR / "p1481_finite_field_serial_message_propagation_audit.json":
        "a63c529d43599d8e7fc888ac3649e0723496be3a940101cf3f055a40cf8f616d",
    STATE_DIR / "p1482_coordinate_routed_wagner_tree.json":
        "e054ca2447bb251112a4edac63234241525b9add1b194ba2247bb79704ab9beb",
    STATE_DIR / "p1482_coordinate_routed_wagner_tree_audit.json":
        "e8c7348a044ad9313eefeda62f1d92d2f81721a76eca273593dcd56e267d9a0e",
}
FIXTURES = [
    {"L": 4, "p": 1033, "order": 1061, "a": 1, "b": 1},
    {"L": 8, "p": 32801, "order": 32479, "a": 1, "b": 5},
    {"L": 16, "p": 1048609, "order": 1047539, "a": 5, "b": 7},
    {"L": 32, "p": 33554593, "order": 33563891, "a": 3, "b": 9},
]


@dataclass(frozen=True)
class ScalarRecord:
    value: int
    source: tuple[tuple[int, int], ...]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def coordinate_label(context: dict[str, Any], point: Any) -> int | None:
    if point.is_zero() or int(point[0]) == 0:
        return None
    fixture, field = context["fixture"], context["field"]
    residue = int(field(int(point[0])) ** ((fixture["p"] - 1) // fixture["L"]))
    return context["coset_table"][residue]


def accepted_labels(
    lane: str, L: int, schedule: int, level: int, node: int, width: int
) -> set[int]:
    ranked = sorted(
        range(L),
        key=lambda label: (digest_int("P1483", lane, L, schedule, level, node, label), label),
    )
    return set(ranked[:width])


def calibrated_width(D: int, L: int, left_count: int, right_count: int) -> int:
    product = left_count * right_count
    if product == 0:
        return L
    return max(1, min(L, int(math.floor(D * L / product + 0.5))))


def public_merge(
    context: dict[str, Any], left: list[Record], right: list[Record], lane: str,
    schedule: int, level: int, node: int, D: int,
) -> tuple[list[Record], dict[str, Any]]:
    L = context["fixture"]["L"]
    width = calibrated_width(D, L, len(left), len(right))
    labels = accepted_labels(lane, L, schedule, level, node, width)
    output = []
    identity_rejections = 0
    filters = 0
    for first in left:
        for second in right:
            point = first.point + second.point
            if point.is_zero():
                identity_rejections += 1
                continue
            filters += 1
            if lane == "coordinate":
                label = coordinate_label(context, point)
            elif lane == "hash":
                label = digest_int(
                    "P1483", "hash-value", L, schedule, level, node, int(point[0])
                ) % L
            else:
                raise ValueError(lane)
            if label not in labels:
                continue
            output.append(Record(
                point,
                tuple(a + b for a, b in zip(first.coefficients, second.coefficients)),
                first.source + second.source,
                None,
            ))
    source_length = 2**level
    return output, {
        "level": level,
        "node": node,
        "left_records": len(left),
        "right_records": len(right),
        "cartesian_product": len(left) * len(right),
        "accepted_label_count": width,
        "accepted_label_sha256": hashlib.sha256(
            b"|".join(str(label).encode("ascii") for label in sorted(labels))
        ).hexdigest(),
        "group_additions": len(left) * len(right),
        "filter_evaluations": filters,
        "identity_rejections": identity_rejections,
        "accepted_records": len(output),
        "distinct_point_count": len({point_key(record.point) for record in output}),
        "distinct_coefficient_count": len({record.coefficients for record in output}),
        "source_reference_count": len(output) * source_length,
        "storage_units": len(output) * (2 + len(left[0].coefficients) + source_length) if output and left else 0,
    }


def public_top_lists(
    context: dict[str, Any], leaves: list[Record], lane: str, schedule: int
) -> tuple[list[Record], list[Record], list[dict[str, Any]]]:
    current = [leaves for _ in range(16)]
    rows = []
    D = len(leaves)
    for level in range(1, 4):
        next_level = []
        for node in range(len(current) // 2):
            merged, metrics = public_merge(
                context, current[2 * node], current[2 * node + 1], lane,
                schedule, level, node, D,
            )
            next_level.append(merged)
            rows.append(metrics)
        current = next_level
    return current[0], current[1], rows


def root_zero_join(
    context: dict[str, Any], roots: list[int], left: list[Record], right: list[Record]
) -> tuple[set[tuple[int, ...]], dict[str, int]]:
    right_index: dict[Any, list[Record]] = {}
    for record in right:
        right_index.setdefault(point_key(record.point), []).append(record)
    rows: set[tuple[int, ...]] = set()
    matches = zero = duplicate = invalid = 0
    for first in left:
        for second in right_index.get(point_key(-first.point), []):
            matches += 1
            coefficients = tuple(a + b for a, b in zip(first.coefficients, second.coefficients))
            row = canonical_row(coefficients)
            if row is None:
                zero += 1
                continue
            combined = Record(
                first.point + second.point,
                coefficients,
                first.source + second.source,
                None,
            )
            if not verify_relation(context, roots, combined):
                invalid += 1
            elif row in rows:
                duplicate += 1
            else:
                rows.add(row)
    return rows, {
        "right_hash_inserts": len(right),
        "left_hash_probes": len(left),
        "inverse_match_count": matches,
        "zero_vector_rejections": zero,
        "duplicate_row_rejections": duplicate,
        "invalid_source_count": invalid,
        "exact_unique_row_count": len(rows),
    }


def public_schedule(
    context: dict[str, Any], roots: list[int], leaves: list[Record], lane: str, schedule: int
) -> dict[str, Any]:
    started = time.perf_counter()
    left, right, nodes = public_top_lists(context, leaves, lane, schedule)
    rows, root = root_zero_join(context, roots, left, right)
    work = sum(node["group_additions"] + node["filter_evaluations"] for node in nodes)
    work += len(right) + len(left) + root["inverse_match_count"]
    return {
        "schedule": schedule,
        "nodes": nodes,
        "level3_left_records": len(left),
        "level3_right_records": len(right),
        "level3_survived": len(left) > 0 and len(right) > 0,
        "root": root,
        "rows": rows,
        "construction_work": work,
        "peak_node_records": max((node["accepted_records"] for node in nodes), default=0),
        "peak_node_storage_units": max((node["storage_units"] for node in nodes), default=0),
        "wall_seconds": time.perf_counter() - started,
    }


def public_lane(
    context: dict[str, Any], roots: list[int], leaves: list[Record], lane: str
) -> dict[str, Any]:
    schedules = []
    rows: set[tuple[int, ...]] = set()
    duplicate_across = 0
    for schedule in range(SCHEDULE_COUNT):
        result = public_schedule(context, roots, leaves, lane, schedule)
        for row in result.pop("rows"):
            duplicate_across += row in rows
            rows.add(row)
        schedules.append(result)
    rank = lane_rank(context, rows)
    total_work = sum(row["construction_work"] for row in schedules)
    aggregate = {
        "schedule_count": SCHEDULE_COUNT,
        "total_construction_work": total_work,
        "peak_node_records": max(row["peak_node_records"] for row in schedules),
        "peak_node_storage_units": max(row["peak_node_storage_units"] for row in schedules),
        "level3_survival_schedule_count": sum(row["level3_survived"] for row in schedules),
        "root_inverse_match_count": sum(row["root"]["inverse_match_count"] for row in schedules),
        "root_zero_vector_rejections": sum(row["root"]["zero_vector_rejections"] for row in schedules),
        "root_invalid_source_count": sum(row["root"]["invalid_source_count"] for row in schedules),
        "exact_unique_row_count": len(rows),
        "duplicate_rows_across_schedules": duplicate_across,
        "relation_rank": rank,
        "factor_dimension": len(roots),
        "work_per_independent_row": total_work / rank if rank else None,
        "row_sha256": hashlib.sha256(
            b"\n".join(repr(row).encode("ascii") for row in sorted(rows))
        ).hexdigest(),
    }
    return {"lane": lane, "schedules": schedules, "aggregate": aggregate}


def scalar_leaf_lists(fixture: dict[str, int]) -> list[list[ScalarRecord]]:
    return [
        [
            ScalarRecord(
                digest_int("P1483", "synthetic-scalar", fixture["L"], leaf, index) % fixture["order"],
                ((leaf, index),),
            )
            for index in range(fixture["L"])
        ]
        for leaf in range(16)
    ]


def scalar_centers(fixture: dict[str, int], schedule: int) -> dict[tuple[int, int], int]:
    q = fixture["order"]
    centers = {}
    running = 0
    for node in range(7):
        value = digest_int("P1483", "synthetic-center", fixture["L"], schedule, node) % q
        centers[(1, node)] = value
        running = (running + value) % q
    centers[(1, 7)] = (-running) % q
    for level, count in ((2, 4), (3, 2)):
        for node in range(count):
            centers[(level, node)] = (
                centers[(level - 1, 2 * node)] + centers[(level - 1, 2 * node + 1)]
            ) % q
    return centers


def centered_distance(value: int, center: int, modulus: int) -> int:
    residue = (value - center) % modulus
    return min(residue, modulus - residue)


def scalar_merge(
    fixture: dict[str, int], left: list[ScalarRecord], right: list[ScalarRecord],
    center: int, level: int, node: int,
) -> tuple[list[ScalarRecord], dict[str, int]]:
    q, L = fixture["order"], fixture["L"]
    candidates = [
        ScalarRecord((first.value + second.value) % q, first.source + second.source)
        for first in left for second in right
    ]
    candidates.sort(key=lambda row: (centered_distance(row.value, center, q), row.value, row.source))
    output = candidates[:L]
    sort_proxy = len(candidates) * max(1, math.ceil(math.log2(max(1, len(candidates)))))
    return output, {
        "level": level,
        "node": node,
        "left_records": len(left),
        "right_records": len(right),
        "pair_sums": len(candidates),
        "sort_comparison_proxy": sort_proxy,
        "retained_records": len(output),
        "distinct_scalar_count": len({row.value for row in output}),
        "source_reference_count": len(output) * (2**level),
    }


def scalar_schedule(fixture: dict[str, int], schedule: int) -> dict[str, Any]:
    centers = scalar_centers(fixture, schedule)
    current = scalar_leaf_lists(fixture)
    nodes = []
    for level in range(1, 4):
        next_level = []
        for node in range(len(current) // 2):
            output, metrics = scalar_merge(
                fixture, current[2 * node], current[2 * node + 1],
                centers[(level, node)], level, node,
            )
            next_level.append(output)
            nodes.append(metrics)
        current = next_level
    left, right = current
    right_index: dict[int, list[ScalarRecord]] = {}
    for row in right:
        right_index.setdefault(row.value, []).append(row)
    matches = invalid = 0
    source_hashes = set()
    for first in left:
        for second in right_index.get((-first.value) % fixture["order"], []):
            matches += 1
            source = first.source + second.source
            leaves = {leaf for leaf, _ in source}
            total = sum(
                digest_int("P1483", "synthetic-scalar", fixture["L"], leaf, index)
                % fixture["order"]
                for leaf, index in source
            ) % fixture["order"]
            if len(source) != 16 or leaves != set(range(16)) or total != 0:
                invalid += 1
            else:
                source_hashes.add(hashlib.sha256(repr(source).encode("ascii")).hexdigest())
    work = sum(node["pair_sums"] + node["sort_comparison_proxy"] for node in nodes)
    work += len(right) + len(left) + matches
    return {
        "schedule": schedule,
        "nodes": nodes,
        "root": {
            "right_hash_inserts": len(right),
            "left_hash_probes": len(left),
            "exact_match_count": matches,
            "invalid_source_count": invalid,
            "unique_source_count": len(source_hashes),
        },
        "total_work": work,
    }


def scalar_control(fixture: dict[str, int]) -> dict[str, Any]:
    schedules = [scalar_schedule(fixture, schedule) for schedule in range(SCHEDULE_COUNT)]
    return {
        "schedule_count": SCHEDULE_COUNT,
        "schedules": schedules,
        "aggregate": {
            "exact_match_count": sum(row["root"]["exact_match_count"] for row in schedules),
            "unique_source_count": sum(row["root"]["unique_source_count"] for row in schedules),
            "invalid_source_count": sum(row["root"]["invalid_source_count"] for row in schedules),
            "total_work": sum(row["total_work"] for row in schedules),
            "all_nodes_retain_L": all(
                node["retained_records"] == fixture["L"] for row in schedules for node in row["nodes"]
            ),
        },
    }


def coordinate_descent(
    context: dict[str, Any], leaves: list[Record]
) -> dict[str, Any]:
    queries = []
    for target_index in range(8):
        scalar = 1 + digest_int("P1483", "descent", context["fixture"]["L"], target_index) % (
            context["fixture"]["order"] - 1
        )
        target = scalar * context["generator"]
        found = None
        total_work = 0
        for schedule in range(SCHEDULE_COUNT):
            left, right, nodes = public_top_lists(context, leaves, "coordinate", schedule)
            source, root = root_join_target(context, left, right, target)
            total_work += sum(node["group_additions"] + node["filter_evaluations"] for node in nodes)
            total_work += root["right_hash_inserts"] + root["left_hash_probes"] + root["target_match_count"]
            if source is not None and found is None:
                found = source
        queries.append({
            "target_index": target_index,
            "target_scalar": scalar,
            "target": point_json(target),
            "source_found": found is not None,
            "verified_source": [point_json(point) for point in found] if found else None,
            "total_work": total_work,
        })
    return {"executed": True, "all_targets_succeeded": all(row["source_found"] for row in queries), "queries": queries}


def render_note(payload: dict[str, Any]) -> str:
    return "\n".join([
        "# P1483 occupancy-calibrated Wagner routing", "", "## Status", "",
        f"`{payload['status']}`", "",
        f"Coordinate ranks: `{[cell['coordinate']['aggregate']['relation_rank'] for cell in payload['cells']]}`.", "",
        f"Hash ranks: `{[cell['hash']['aggregate']['relation_rank'] for cell in payload['cells']]}`.", "",
        f"Synthetic scalar matches: `{[cell['scalar_control']['aggregate']['exact_match_count'] for cell in payload['cells']]}`.", "",
        "Adaptive width repairs occupancy only. Promotion requires public nonzero",
        "rank and target descent beyond the matched hash lane.", "",
    ])


def main() -> int:
    os.chdir(ROOT)
    observed = {str(path.relative_to(ROOT)): sha256_file(path) for path in EXPECTED}
    expected = {str(path.relative_to(ROOT)): digest for path, digest in EXPECTED.items()}
    if observed != expected:
        raise RuntimeError("frozen P1483 input mismatch")
    cells = []
    for fixture in FIXTURES:
        context = build_context(fixture)
        roots = factor_roots(context)
        leaves = make_leaves(context, roots, None)
        coordinate = public_lane(context, roots, leaves, "coordinate")
        hash_control = public_lane(context, roots, leaves, "hash")
        public_phase_sealed_at = time.time_ns()
        scalar = scalar_control(fixture)
        descent = (
            coordinate_descent(context, leaves)
            if coordinate["aggregate"]["relation_rank"] >= max(1, len(roots) - 1)
            else {"executed": False, "reason": "coordinate rank below N-1"}
        )
        cell = {
            "fixture": fixture,
            "factor_root_count": len(roots),
            "signed_leaf_count": len(leaves),
            "factor_root_sha256": hashlib.sha256(
                b"|".join(str(root).encode("ascii") for root in roots)
            ).hexdigest(),
            "public_phase_sealed_at_ns": public_phase_sealed_at,
            "coordinate": coordinate,
            "hash": hash_control,
            "scalar_control": scalar,
            "coordinate_descent": descent,
        }
        cells.append(cell)
        print(json.dumps({
            "L": fixture["L"], "D": len(leaves),
            "coordinate": coordinate["aggregate"], "hash": hash_control["aggregate"],
            "scalar": scalar["aggregate"], "descent_executed": descent["executed"],
        }, sort_keys=True), flush=True)

    xs = [cell["fixture"]["L"] for cell in cells]
    fits = {
        "coordinate_total_work": fit_slope(
            xs, [cell["coordinate"]["aggregate"]["total_construction_work"] for cell in cells]
        ),
        "coordinate_peak_storage": fit_slope(
            xs, [max(1, cell["coordinate"]["aggregate"]["peak_node_storage_units"]) for cell in cells]
        ),
    }
    scalar_pass = all(
        cell["scalar_control"]["aggregate"]["exact_match_count"] > 0
        and cell["scalar_control"]["aggregate"]["invalid_source_count"] == 0
        and cell["scalar_control"]["aggregate"]["all_nodes_retain_L"]
        for cell in cells
    )
    public_exact = all(
        cell[lane]["aggregate"]["root_invalid_source_count"] == 0
        for cell in cells for lane in ("coordinate", "hash")
    )
    coordinate_survives = all(
        cell["coordinate"]["aggregate"]["level3_survival_schedule_count"] > 0 for cell in cells
    )
    coordinate_beats_hash = all(
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
    work_gate = fits["coordinate_total_work"]["slope"] <= 2 + 1e-12 and fits["coordinate_total_work"]["leave_one_out_max"] <= 2 + 1e-12
    storage_gate = fits["coordinate_peak_storage"]["slope"] <= 2 + 1e-12 and fits["coordinate_peak_storage"]["leave_one_out_max"] <= 2 + 1e-12
    finite_rows = all(cell["coordinate"]["aggregate"]["work_per_independent_row"] is not None for cell in cells)
    all_descent_executed = all(cell["coordinate_descent"]["executed"] for cell in cells)
    descent_pass = all_descent_executed and all(cell["coordinate_descent"]["all_targets_succeeded"] for cell in cells)
    signal = all((scalar_pass, public_exact, coordinate_survives, coordinate_beats_hash,
                  rank_gate, work_gate, storage_gate, finite_rows, descent_pass))
    status = (
        "OBSERVATION_P1483_OCCUPANCY_CALIBRATED_WAGNER_SIGNAL"
        if signal
        else "NEGATIVE_RESULT_P1483_CALIBRATED_X_COSET_ROUTING_NO_RANK_ADVANTAGE"
    )
    payload = {
        "schema": SCHEMA,
        "status": status,
        "schedule_count": SCHEDULE_COUNT,
        "cells": cells,
        "fits": fits,
        "gates": {
            "independent_scalar_control_exact_matches_every_fixture": scalar_pass,
            "all_public_sources_and_rows_exact": public_exact,
            "coordinate_level3_survives_every_fixture": coordinate_survives,
            "coordinate_rows_and_rank_beat_hash_L16_L32": coordinate_beats_hash,
            "coordinate_rank_at_least_N_minus_one_every_fixture": rank_gate,
            "coordinate_total_work_all_slopes_at_most_two": work_gate,
            "coordinate_peak_storage_all_slopes_at_most_two": storage_gate,
            "coordinate_work_per_independent_row_finite": finite_rows,
            "coordinate_descent_all_fixtures_executed": all_descent_executed,
            "coordinate_descent_all_targets_succeeded": descent_pass,
            "synthetic_scalars_isolated_after_public_phase": True,
            "rho_and_full_pipeline_not_waived": True,
        },
        "occupancy_calibrated_wagner_signal": signal,
        "conditional_exponent_ledger": {
            "factor_base": "L=q^(1/5)", "tree_if_rank_passes": "L^2=q^(2/5)",
            "linear_algebra_if_rank_passes": "L^2=q^(2/5)",
            "descent_requirement": "L^2=q^(2/5)",
            "boundary": "conditional on public rank and descent; synthetic scalar lane excluded",
        },
        "frozen_files": observed,
        "boundary": (
            "Adaptive width repairs finite occupancy but not additive compatibility. A scalar pass with "
            "coordinate/hash rank tie closes this public x-coset routing family only."
        ),
        "next_action": (
            "If scalar calibration passes and coordinate rank does not beat hash, stop bucket tuning. "
            "Require an efficiently computable additive projection, approximate homomorphism with exact "
            "source correction, or a source-preserving transfer before another k-tree lane."
        ),
    }
    write_atomic(OUT, (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    write_atomic(NOTE, render_note(payload).encode("utf-8"))
    print(json.dumps({
        "output": str(OUT.relative_to(ROOT)), "note": str(NOTE.relative_to(ROOT)),
        "status": status,
        "coordinate_ranks": [cell["coordinate"]["aggregate"]["relation_rank"] for cell in cells],
        "hash_ranks": [cell["hash"]["aggregate"]["relation_rank"] for cell in cells],
        "scalar_matches": [cell["scalar_control"]["aggregate"]["exact_match_count"] for cell in cells],
        "fits": fits, "signal": signal,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
