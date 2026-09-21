#!/usr/bin/env sage -python
"""Test IDEA-049's complete affine integral lift before any lattice run."""

from __future__ import annotations

import collections
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any

from sage.all import EllipticCurve, GF, PolynomialRing, ZZ


ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "ecdlp_index_calculus_state"
RESEARCH = ROOT / "research"
CONTRACT = STATE / "experiment_contract_p1507_integral_transducer_height_gate.md"
P1504 = STATE / "p1504_matchgate_shared_basis_obstruction.json"
P1504_AUDIT = STATE / "p1504_matchgate_shared_basis_obstruction_audit.json"
IDEA = Path(
    "/Volumes/Volume/crypto-autoresearcher/ideas/deferred/"
    "ECDLP-IDEA-049_bounded_root_decomposition_transducer_hypothesis.md"
)
DERIVATION = Path(
    "/Volumes/Volume/crypto-autoresearcher/ideas/artifacts/"
    "ECDLP-IDEA-049/integral_addition_transducer_derivation.md"
)
FOCUS_QUEUE = Path(
    "/Volumes/Volume/crypto-autoresearcher/focus/archive/"
    "focus_queue_idea049_active.json"
)
FOCUS_PLAN = Path(
    "/Volumes/Volume/crypto-autoresearcher/focus/archive/"
    "focus_plan_idea049_active.json"
)
OUT = STATE / "p1507_integral_transducer_height_gate.json"
NOTE = RESEARCH / "p1507_integral_transducer_height_gate.md"

SCHEMA = "ecdlp.p1507_integral_transducer_height_gate.v1"
EXPECTED = {
    CONTRACT: "0ee907a91d7fdc6f9ef91a544305602f3e5d027ae43291104d1cc7895d25c08f",
    P1504: "4e65c8f59a601f17763a7d0fd92514c091d36547cdaac5f8fc29d157e332ba51",
    P1504_AUDIT: "4cb16dc9407b1c83146beab8dd5b0146ea1cd7de7d00db57d8869d45b2280033",
    IDEA: "1a58addced8c2bb14590eb9a74252707409d01e7acb6fbab206dc12af974b1e0",
    DERIVATION: "cbbe0f83426067fefde0a1f440afafad3d856ad49540469219df78da5a716b4d",
    FOCUS_QUEUE: "c31dc53061d550d05aa510f0a950234e6b29570f8811408c8cd5ccfe75a17e53",
    FOCUS_PLAN: "7537a3ed1925fa98406361427bc21370fcb058a47d92a2e8b6285667067790f9",
}


def compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return hashlib.sha256(compact(value).encode("ascii")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def write_atomic(path: Path, data: bytes) -> None:
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def point_json(point: Any) -> list[int] | None:
    if point.is_zero():
        return None
    return [int(point[0]), int(point[1])]


def generic_integral_record(curve: Any, left: Any, right: Any) -> dict[str, Any]:
    p = int(curve.base_field().characteristic())
    x1, y1 = int(left[0]), int(left[1])
    x2, y2 = int(right[0]), int(right[1])
    slope = int((right[1] - left[1]) / (right[0] - left[0]))
    result = left + right
    if result.is_zero():
        raise ValueError("generic secant unexpectedly produced infinity")
    x3, y3 = int(result[0]), int(result[1])
    slope_numerator = slope * (x2 - x1) - (y2 - y1)
    x_numerator = slope * slope - x1 - x2 - x3
    y_numerator = slope * (x1 - x3) - y1 - y3
    if slope_numerator % p or x_numerator % p or y_numerator % p:
        raise RuntimeError("P1507 nonintegral quotient")
    k_s = slope_numerator // p
    k_x = x_numerator // p
    k_y = y_numerator // p
    return {
        "right": point_json(right),
        "result": point_json(result),
        "lambda": slope,
        "lambda_centered_abs": min(slope, p - slope),
        "k_s": k_s,
        "k_x": k_x,
        "k_y": k_y,
        "integer_equations_exact": (
            slope * (x2 - x1) - (y2 - y1) == k_s * p
            and slope * slope - x1 - x2 - x3 == k_x * p
            and slope * (x1 - x3) - y1 - y3 == k_y * p
        ),
    }


def complete_slope_cell(fixture: dict[str, int]) -> dict[str, Any]:
    p = fixture["p"]
    field = GF(p)
    curve = EllipticCurve(field, [field(fixture["a"]), field(fixture["b"])])
    points = list(curve.points())
    affine = sorted(
        (point for point in points if not point.is_zero()),
        key=lambda point: (int(point[0]), int(point[1])),
    )
    left = affine[0]
    chart_counts = collections.Counter()
    generic_records = []
    slope_fibers: dict[int, list[list[int]]] = collections.defaultdict(list)
    for right in points:
        if right.is_zero():
            chart_counts["identity"] += 1
        elif right == -left:
            chart_counts["vertical"] += 1
        elif right == left:
            chart_counts["doubling"] += 1
        else:
            chart_counts["generic_secant"] += 1
            record = generic_integral_record(curve, left, right)
            generic_records.append(record)
            slope_fibers[record["lambda"]].append(record["right"])
    distinct_slopes = len(slope_fibers)
    generic_count = len(generic_records)
    fiber_lower_bound = math.ceil(generic_count / 2)
    centered_lower_bound = math.ceil((distinct_slopes - 1) / 2)
    centered_radius = max(record["lambda_centered_abs"] for record in generic_records)
    return {
        **fixture,
        "point_count": int(curve.order()),
        "ordinary": (p + 1 - int(curve.order())) % p != 0,
        "left": point_json(left),
        "chart_counts": dict(sorted(chart_counts.items())),
        "chart_count_total": sum(chart_counts.values()),
        "generic_secant_count": generic_count,
        "distinct_slope_count": distinct_slopes,
        "fiber_two_distinct_slope_lower_bound": fiber_lower_bound,
        "maximum_slope_fiber": max(map(len, slope_fibers.values())),
        "centered_slope_covering_radius": centered_radius,
        "centered_radius_counting_lower_bound": centered_lower_bound,
        "centered_radius_over_p": centered_radius / p,
        "finite_root_height_exponent_log_N": math.log(max(1, centered_radius), fixture["order"]),
        "k_s_range": [min(record["k_s"] for record in generic_records), max(record["k_s"] for record in generic_records)],
        "k_x_range": [min(record["k_x"] for record in generic_records), max(record["k_x"] for record in generic_records)],
        "k_y_range": [min(record["k_y"] for record in generic_records), max(record["k_y"] for record in generic_records)],
        "all_integer_equations_exact": all(record["integer_equations_exact"] for record in generic_records),
        "generic_transcript_sha256": digest(generic_records),
        "slope_fiber_sha256": digest([
            [slope, sorted(points)] for slope, points in sorted(slope_fibers.items())
        ]),
        "complete_slope_box_submodulus_asymptotically": False,
    }


def small_x_factor_base_control() -> dict[str, Any]:
    p = 1033
    field = GF(p)
    curve = EllipticCurve(field, [field(1), field(1)])
    factor_base = []
    for x in range(128):
        lifts = sorted(curve.lift_x(field(x), all=True), key=lambda point: int(point[1]))
        if lifts:
            factor_base.append(lifts[0])
    records = []
    chart_counts = collections.Counter()
    for left in factor_base:
        for right in factor_base:
            if right == -left:
                chart_counts["vertical"] += 1
            elif right == left:
                chart_counts["doubling"] += 1
            else:
                chart_counts["generic_secant"] += 1
                records.append(generic_integral_record(curve, left, right))
    return {
        "p": p,
        "a": 1,
        "b": 1,
        "order": int(curve.order()),
        "x_cutoff_exclusive": 128,
        "factor_base_size": len(factor_base),
        "maximum_factor_base_x": max(int(point[0]) for point in factor_base),
        "maximum_centered_factor_base_y": max(
            min(int(point[1]), p - int(point[1])) for point in factor_base
        ),
        "chart_counts": dict(sorted(chart_counts.items())),
        "generic_pair_count": len(records),
        "distinct_slope_count": len({record["lambda"] for record in records}),
        "centered_slope_covering_radius": max(record["lambda_centered_abs"] for record in records),
        "k_s_range": [min(record["k_s"] for record in records), max(record["k_s"] for record in records)],
        "k_x_range": [min(record["k_x"] for record in records), max(record["k_x"] for record in records)],
        "k_y_range": [min(record["k_y"] for record in records), max(record["k_y"] for record in records)],
        "all_integer_equations_exact": all(record["integer_equations_exact"] for record in records),
        "small_x_forces_small_slope_and_carries": False,
        "transcript_sha256": digest(records),
    }


def symbolic_elimination_control() -> dict[str, Any]:
    ring = PolynomialRing(ZZ, ("lambda", "x1", "x2", "x3", "y1", "y2", "a", "b"))
    lam, x1, x2, x3, y1, y2, a, b = ring.gens()
    slope_equation = lam * (x2 - x1) - (y2 - y1)
    x_equation = lam**2 - x1 - x2 - x3
    eliminated = slope_equation.resultant(x_equation, lam)
    denominator_free = (y2 - y1) ** 2 - (x2 - x1) ** 2 * (x1 + x2 + x3)

    xring = PolynomialRing(ZZ, ("X1", "X2", "X3", "A", "B"))
    X1, X2, X3, A, B = xring.gens()
    curve1 = X1**3 + A * X1 + B
    curve2 = X2**3 + A * X2 + B
    denominator_term = (X2 - X1) ** 2 * (X1 + X2 + X3)
    y_eliminated = 4 * curve1 * curve2 - (curve1 + curve2 - denominator_term) ** 2
    s3 = (
        (X1 - X2) ** 2 * X3**2
        - 2 * ((X1 + X2) * (X1 * X2 + A) + 2 * B) * X3
        + (X1 * X2 - A) ** 2
        - 4 * B * (X1 + X2)
    )
    quotient, remainder = y_eliminated.quo_rem(s3)
    expected_exceptional_factor = -(X1 - X2) ** 2
    return {
        "lambda_resultant_equals_denominator_free_addition": eliminated == denominator_free,
        "lambda_resultant_sha256": digest(str(eliminated)),
        "y_elimination_divisible_by_s3": remainder == 0,
        "y_elimination_quotient": str(quotient),
        "exceptional_factor_exact": quotient == expected_exceptional_factor,
        "s3_sha256": digest(str(s3)),
        "saturation_returns_standard_s3": remainder == 0 and quotient == expected_exceptional_factor,
    }


def render_note(payload: dict[str, Any]) -> str:
    lines = [
        "# P1507 Integral Transducer Height Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Complete Slope Cells",
        "",
        "| p | #E | generic Q | slopes | max fiber | centered radius | k_s | k_x | k_y |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for cell in payload["complete_slope_cells"]:
        lines.append(
            f"| {cell['p']} | {cell['order']} | {cell['generic_secant_count']} | "
            f"{cell['distinct_slope_count']} | {cell['maximum_slope_fiber']} | "
            f"{cell['centered_slope_covering_radius']} | {cell['k_s_range']} | "
            f"{cell['k_x_range']} | {cell['k_y_range']} |"
        )
    lines.extend([
        "",
        "The line-fiber theorem gives a target-independent complete slope radius Omega(p), so the natural lift has no sub-modulus root box. The small-x F1033 control also exhibits near-half-field slopes and modulus-scale quotients.",
        "",
        "Eliminating lambda gives the denominator-free addition equation; eliminating y and saturating the exceptional denominator factor gives standard S3 exactly.",
        "",
        "## Interpretation",
        "",
        payload["interpretation"],
        "",
        "## Next Action",
        "",
        payload["next_action"],
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    hashes = {display_path(path): sha256_file(path) for path in EXPECTED}
    hash_gates = {
        display_path(path): hashes[display_path(path)] == expected
        for path, expected in EXPECTED.items()
    }
    if not all(hash_gates.values()):
        raise RuntimeError(f"P1507 frozen hash mismatch: {hash_gates}")

    p1504 = json.loads(P1504.read_text(encoding="ascii"))
    p1504_audit = json.loads(P1504_AUDIT.read_text(encoding="ascii"))
    focus = json.loads(FOCUS_PLAN.read_text(encoding="ascii"))
    active_ids = [item["id"] for item in focus["critical_experiments"]]
    fixtures = [
        {key: fixture[key] for key in ("p", "a", "b", "order")}
        for fixture in p1504["fixtures"]
    ]
    cells = [complete_slope_cell(fixture) for fixture in fixtures]
    small_x = small_x_factor_base_control()
    elimination = symbolic_elimination_control()
    gates = {
        "frozen_hashes_exact": all(hash_gates.values()),
        "idea049_is_sole_active_focus": active_ids == ["ECDLP-IDEA-049"],
        "p1504_curve_panel_independently_audited": (
            p1504_audit["passed_checks"] == p1504_audit["total_checks"] == 12
        ),
        "all_curve_orders_and_chart_partitions_exact": all(
            cell["point_count"] == cell["order"]
            and cell["chart_count_total"] == cell["order"]
            and cell["ordinary"]
            for cell in cells
        ),
        "all_generic_integer_lifts_exact": all(cell["all_integer_equations_exact"] for cell in cells),
        "line_slope_fibers_at_most_two": all(cell["maximum_slope_fiber"] <= 2 for cell in cells),
        "fiber_two_counting_lower_bound_exact": all(
            cell["distinct_slope_count"] >= cell["fiber_two_distinct_slope_lower_bound"]
            and cell["centered_slope_covering_radius"] >= cell["centered_radius_counting_lower_bound"]
            for cell in cells
        ),
        "complete_target_independent_slope_bound_submodulus": False,
        "small_x_control_integer_lifts_exact": small_x["all_integer_equations_exact"],
        "small_x_control_has_full_scale_hidden_variables": (
            small_x["centered_slope_covering_radius"] >= 0.45 * small_x["p"]
            and max(map(abs, small_x["k_x_range"])) >= 0.8 * small_x["p"]
            and max(map(abs, small_x["k_y_range"])) >= 0.8 * small_x["p"]
        ),
        "lambda_elimination_returns_denominator_free_addition": elimination["lambda_resultant_equals_denominator_free_addition"],
        "saturation_returns_standard_s3": elimination["saturation_returns_standard_s3"],
        "bounded_integral_transducer_established": False,
        "lattice_execution_approved": False,
        "generic_shoup_breakthrough": False,
    }
    required_true = {
        key: value
        for key, value in gates.items()
        if key not in {
            "complete_target_independent_slope_bound_submodulus",
            "bounded_integral_transducer_established",
            "lattice_execution_approved",
            "generic_shoup_breakthrough",
        }
    }
    if not all(required_true.values()):
        raise RuntimeError(f"P1507 decision gate failed: {gates}")

    source = Path(__file__).resolve()
    payload = {
        "schema": SCHEMA,
        "status": "NEGATIVE_RESULT_P1507_COMPLETE_AFFINE_LIFT_HAS_MODULUS_SCALE_ROOTS",
        "claim_status": "INTEGER LIFT EXACT / COMPLETE SLOPE HEIGHT OMEGA-P / CARRIES MODULUS-SCALE / ELIMINATION RETURNS S3 / NO BREAKTHROUGH",
        "source": display_path(source),
        "source_sha256": sha256_file(source),
        "contract": display_path(CONTRACT),
        "contract_sha256": hashes[display_path(CONTRACT)],
        "frozen_hashes": hashes,
        "hash_gates": hash_gates,
        "focus_active_ids": active_ids,
        "complete_slope_cells": cells,
        "small_x_factor_base_control": small_x,
        "symbolic_elimination_control": elimination,
        "theorem_certificate": {
            "statement": "For fixed P, each secant slope has at most two other curve points; a complete centered slope box has radius at least (N-O(1))/4=Omega(p).",
            "fiber_bound": 2,
            "distinct_slopes_lower_bound": "ceil(generic_affine_Q/2)",
            "centered_radius_lower_bound": "ceil((distinct_slopes-1)/2)",
            "ordinary_curve_order": "N=p+O(sqrt(p))",
            "root_height_exponent": 1,
            "idea049_required_exponent_strictly_below_one": True,
            "required_root_region_satisfied": False,
        },
        "gates": gates,
        "interpretation": (
            "The standard complete affine transducer is arithmetically exact, but a "
            "fixed-point line-fiber count forces Omega(p) centered slope height on "
            "ordinary curves. Its x/y update quotients also reach modulus scale. A "
            "declared p^eta root box with eta<1 therefore excludes valid additions "
            "before any lattice determinant is considered. Eliminating the full-size "
            "variables reproduces the denominator-free addition law and, after "
            "saturation, standard Semaev S3."
        ),
        "limitations": [
            "The theorem governs complete standard affine addition, not every specially designed factor base or non-affine integral model.",
            "The small-x F1033 panel is diagnostic only; the complete-slope theorem carries the asymptotic statement.",
            "No general multivariate Coppersmith impossibility theorem is claimed; the proposed root region fails its necessary completeness premise.",
            "A special low-height addition circuit would require a new target-independent construction and complete exceptional-chart proof.",
            "No rho or Shoup-bound improvement is claimed.",
        ],
        "next_action": (
            "Close IDEA-049's natural complete affine lift without running LLL. A "
            "successor is admissible only after proving a special source family or "
            "integral model in which every hidden slope, denominator, coordinate, and "
            "carry has a complete sub-modulus bound and an explicit determinant region."
        ),
    }
    write_atomic(OUT, (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("ascii"))
    write_atomic(NOTE, render_note(payload).encode("ascii"))
    print(json.dumps({
        "status": payload["status"],
        "output": str(OUT),
        "note": str(NOTE),
        "gates": gates,
        "small_x_control": {
            "factor_base_size": small_x["factor_base_size"],
            "centered_slope_radius": small_x["centered_slope_covering_radius"],
            "k_x_range": small_x["k_x_range"],
            "k_y_range": small_x["k_y_range"],
        },
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
