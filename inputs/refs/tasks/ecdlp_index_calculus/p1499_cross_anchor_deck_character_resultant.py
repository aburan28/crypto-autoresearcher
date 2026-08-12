#!/usr/bin/env sage -python
"""Test nonhomomorphic deck-character resultants on the P1497 p271 stream."""

from __future__ import annotations

import hashlib
import json
import math
import os
import resource
import statistics
import time
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any

from sage.all import EllipticCurve, GF, Matrix, PolynomialRing, identity_matrix, vector

import p1496_root_free_quadratic_divisor as p1496


ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = ROOT / "ecdlp_index_calculus_state"
RESEARCH_DIR = ROOT / "research"
CONTRACT = STATE_DIR / "experiment_contract_p1499_cross_anchor_deck_character_resultant.md"
P1497 = STATE_DIR / "p1497_exception_complete_quadratic_divisor.json"
P1497_AUDIT = STATE_DIR / "p1497_exception_complete_quadratic_divisor_audit.json"
P1498 = STATE_DIR / "p1498_simple_prym_quotient_obstruction.json"
P1498_AUDIT = STATE_DIR / "p1498_simple_prym_quotient_obstruction_audit.json"
PO59 = ROOT / "experiments/ecdlp_isogeny/po_transfer_059_deck_character_predicate.json"
OUT = STATE_DIR / "p1499_cross_anchor_deck_character_resultant.json"
NOTE = RESEARCH_DIR / "p1499_cross_anchor_deck_character_resultant.md"

SCHEMA = "ecdlp.p1499_cross_anchor_deck_character_resultant.v1"
TARGET_P = 271
NULL_REPLICATES = 32
EXPECTED = {
    CONTRACT: "a32c04a3f67e662c3fbe7c5b649cef9eed7b874f5664959846baa176d9694304",
    P1497: "3da79142512eadbd2ec968ae9bdad29d97b5c6030ecd6305d7cd99e4bdaf6ad3",
    P1497_AUDIT: "965a08b8cb6b933e3caccb3e11fa432dcd479d0344cd2ae820540f2b71b218cc",
    P1498: "f39e4e4550725900d8bf23b4118fd8757aa38b9e4b009fa710d9475b7f4da571",
    P1498_AUDIT: "df6680776a3a3fa2942c62e625d06f7dc92e28db18f122e94cb2b5db2acb8685",
    PO59: "6a4973fc4420a0e5f82dc83b60353dc7b1977e694408c565b854298857200534",
    p1496.PO71_RESULT: "79579cbe2655287286e7c6ac099f530bd06744c95b8555ef13a296b04a9f3b05",
    p1496.PO71_WALK: "a3568a0a023c1bb8a6056c33ddef8cbce6c7c790d94e9fb11a55d5d1dc8ef092",
    p1496.PO70_SOURCE: "f30dd608f902009002cb9827c8bf873972f33ad4405fadd38d8051ec600c9109",
    p1496.PO70_DIRECT: "081898d59060c1c343d32275c4ed10759850c34f6caf07a3f7e3909e814e86a4",
    p1496.PO65_DIRECT: "97414a64b4f5b62a7a18dd12a014ad1bfa0df0164d2215b2fd5ceaace0659544",
    p1496.PO55_RESULT: "8584c70805314a4aeb6c6770a82936f0b7ac29e509ed2dd90805d59dd43a03ec",
    p1496.PO54_ORACLE: "80b8c550d162cfc722d01bf73655a2bbdf77599318ee006a2b4955f239dd76de",
}


def digest_int(*items: Any) -> int:
    payload = json.dumps(items, sort_keys=True, separators=(",", ":")).encode("ascii")
    return int.from_bytes(hashlib.sha256(payload).digest(), "big")


def weighted_orbit_label(
    values: tuple[Any, ...], weights: tuple[int, ...], omega: Any
) -> tuple[list[int], int]:
    candidates = []
    for exponent in range(3):
        candidate = tuple(
            int((omega ** (weight * exponent)) * value)
            for value, weight in zip(values, weights)
        )
        candidates.append((candidate, exponent))
    label, exponent = min(candidates)
    return list(label), int(exponent)


def catalog_labels(
    trace: Any,
    norm: Any,
    omega: Any,
    p: int,
    identity: list[int],
) -> dict[str, dict[str, Any]]:
    discriminant = trace**2 - 4 * norm
    trace_label, trace_exp = weighted_orbit_label((trace,), (1,), omega)
    norm_label, norm_exp = weighted_orbit_label((norm,), (2,), omega)
    disc_label, disc_exp = weighted_orbit_label((discriminant,), (2,), omega)
    trace_norm, trace_norm_exp = weighted_orbit_label((trace, norm), (1, 2), omega)
    trace_disc, trace_disc_exp = weighted_orbit_label(
        (trace, discriminant), (1, 2), omega
    )
    norm_disc, norm_disc_exp = weighted_orbit_label(
        (norm, discriminant), (2, 2), omega
    )
    if norm:
        ratio_label = [0, int(trace**2 / norm)]
    elif trace:
        ratio_label = [1, 0]
    else:
        ratio_label = [2, 0]
    random_scalar = [digest_int("p1499-random-scalar-v1", p, identity) % p]
    random_pair = [
        digest_int("p1499-random-pair-left-v1", p, identity) % p,
        digest_int("p1499-random-pair-right-v1", p, identity) % p,
    ]
    return {
        "full_trace_norm": {
            "label": trace_norm,
            "deck_exponent": trace_norm_exp,
            "coordinate_dimension": 2,
            "random_control": False,
        },
        "trace": {
            "label": trace_label,
            "deck_exponent": trace_exp,
            "coordinate_dimension": 1,
            "random_control": False,
        },
        "norm": {
            "label": norm_label,
            "deck_exponent": norm_exp,
            "coordinate_dimension": 1,
            "random_control": False,
        },
        "discriminant": {
            "label": disc_label,
            "deck_exponent": disc_exp,
            "coordinate_dimension": 1,
            "random_control": False,
        },
        "projective_trace2_over_norm": {
            "label": ratio_label,
            "deck_exponent": 0,
            "coordinate_dimension": 1,
            "random_control": False,
        },
        "trace_discriminant": {
            "label": trace_disc,
            "deck_exponent": trace_disc_exp,
            "coordinate_dimension": 2,
            "random_control": False,
        },
        "norm_discriminant": {
            "label": norm_disc,
            "deck_exponent": norm_disc_exp,
            "coordinate_dimension": 2,
            "random_control": False,
        },
        "random_scalar": {
            "label": random_scalar,
            "deck_exponent": 0,
            "coordinate_dimension": 1,
            "random_control": True,
        },
        "random_pair": {
            "label": random_pair,
            "deck_exponent": 0,
            "coordinate_dimension": 2,
            "random_control": True,
        },
    }


def derive_deck_record(
    root_record: dict[str, Any],
    first: Any,
    second: Any,
    parameter: int,
    field: Any,
    gamma: int,
    omega: Any,
) -> tuple[dict[str, Any] | None, str]:
    identity = list(root_record["identity"])
    ring = PolynomialRing(field, f"p1499_x_{identity[0]}_{identity[1]}")
    x = ring.gen()
    certificate = root_record["certificate"]
    u = ring([field(value) for value in certificate["u"]])
    v = ring([field(value) for value in certificate["v"]])
    coefficients = vector(
        field,
        [first[index] + field(parameter) * second[index] for index in range(9)],
    )
    r0 = (
        coefficients[0]
        + coefficients[1] * x
        + coefficients[2] * x**2
        + coefficients[3] * v
    ) % u
    r1 = (
        coefficients[4] + coefficients[5] * x + coefficients[6] * v
    ) % u
    r2 = (coefficients[7] + coefficients[8] * x) % u
    h = (v - field(gamma)) % u
    delta = (r1**2 - r0 * r2) % u
    try:
        inverse_delta = delta.inverse_mod(u)
    except (ArithmeticError, ZeroDivisionError, ValueError):
        return None, "noninvertible_delta"
    z = ((r2**2 * h - r0 * r1) * inverse_delta) % u
    z2 = ((r0**2 - r1 * r2 * h) * inverse_delta) % u
    function_zero = (r0 + r1 * z + r2 * z2) % u == 0
    square_consistent = (z**2 - z2) % u == 0
    cover_consistent = (z**3 - h) % u == 0
    if not (function_zero and square_consistent and cover_consistent):
        return None, "deck_algebra_failure"
    uc = list(u.list()) + [field.zero()] * 3
    zc = list(z.list()) + [field.zero()] * 2
    trace = 2 * zc[0] - zc[1] * uc[1]
    norm = zc[0] ** 2 - zc[0] * zc[1] * uc[1] + zc[1] ** 2 * uc[0]
    t_ring = PolynomialRing(field, f"p1499_T_{identity[0]}_{identity[1]}")
    T = t_ring.gen()
    tx_ring = PolynomialRing(t_ring, f"p1499_resultant_x_{identity[0]}_{identity[1]}")
    tx = tx_ring.gen()
    u_tx = tx**2 + t_ring(uc[1]) * tx + t_ring(uc[0])
    z_tx = t_ring(zc[0]) + t_ring(zc[1]) * tx
    resultant = u_tx.resultant(tx_ring(T) - z_tx)
    expected_resultant = T**2 - t_ring(trace) * T + t_ring(norm)
    if resultant != expected_resultant:
        return None, "character_resultant_failure"
    labels = catalog_labels(trace, norm, omega, int(field.order()), identity)
    return {
        "identity": identity,
        "anchor_index": int(root_record["anchor_index"]),
        "core_index": int(root_record["core_index"]),
        "variant_index": int(root_record["variant_index"]),
        "parameter": int(parameter),
        "support_hash": root_record["support_hash"],
        "row": list(root_record["row"]),
        "aggregate": list(root_record["class_point"]),
        "u": p1496.polynomial_coefficients(u, 3),
        "v": p1496.polynomial_coefficients(v, 2),
        "r0": p1496.polynomial_coefficients(r0, 2),
        "r1": p1496.polynomial_coefficients(r1, 2),
        "r2": p1496.polynomial_coefficients(r2, 2),
        "h": p1496.polynomial_coefficients(h, 2),
        "delta": p1496.polynomial_coefficients(delta, 2),
        "z": p1496.polynomial_coefficients(z, 2),
        "z2": p1496.polynomial_coefficients(z2, 2),
        "trace": int(trace),
        "norm": int(norm),
        "character_resultant": [int(norm), int(-trace), 1],
        "labels": labels,
        "checks": {
            "function_zero": bool(function_zero),
            "z_square_consistent": bool(square_consistent),
            "cover_equation": bool(cover_consistent),
            "resultant_exact": True,
        },
    }, "accepted"


def label_records(
    records: list[dict[str, Any]], name: str
) -> list[dict[str, Any]]:
    return [
        {
            "identity": list(record["identity"]),
            "support_hash": record["support_hash"],
            "label": list(record["labels"][name]["label"]),
            "row": list(record["row"]),
            "aggregate": list(record["aggregate"]),
        }
        for record in records
    ]


def analyze_label(
    records: list[dict[str, Any]],
    factor_base: list[Any],
    curve: Any,
    order: int,
    baseline_rows: list[list[int]],
) -> dict[str, Any]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        buckets[p1496.compact(record["label"])].append(record)
    raw_pairs = 0
    support_distinct_pairs = 0
    subtract_replay_failures = 0
    aggregate_equal_pairs = 0
    aggregate_negative_pairs = 0
    aggregate_mismatch_pairs = 0
    valid_rows = []
    valid_row_keys = set()
    collision_records = []
    collision_bucket_count = 0
    maximum_bucket = 0
    aggregate_images_per_label = []
    for label_key, bucket in sorted(buckets.items()):
        ordered = sorted(bucket, key=lambda item: tuple(item["identity"]))
        maximum_bucket = max(maximum_bucket, len(ordered))
        aggregate_images_per_label.append(
            len({tuple(item["aggregate"]) for item in ordered})
        )
        if len(ordered) >= 2:
            collision_bucket_count += 1
        for left, right in combinations(ordered, 2):
            raw_pairs += 1
            if left["support_hash"] == right["support_hash"]:
                continue
            support_distinct_pairs += 1
            row = [a - b for a, b in zip(left["row"], right["row"])]
            factor_replay = curve(0)
            for coefficient, point in zip(row, factor_base):
                if coefficient:
                    factor_replay += int(coefficient) * curve(
                        p1496.raw_point(point)
                    )
            factor_replay_zero = factor_replay.is_zero()
            left_aggregate = curve(tuple(left["aggregate"]))
            right_aggregate = curve(tuple(right["aggregate"]))
            aggregate_equal = left_aggregate == right_aggregate
            aggregate_negative = left_aggregate == -right_aggregate
            aggregate_equal_pairs += int(aggregate_equal)
            aggregate_negative_pairs += int(aggregate_negative)
            aggregate_mismatch_pairs += int(not aggregate_equal and not aggregate_negative)
            subtract_replay_failures += int(not factor_replay_zero)
            if factor_replay_zero:
                key = p1496.canonical_row(row, order)
                if any(key) and key not in valid_row_keys:
                    valid_row_keys.add(key)
                    valid_rows.append(row)
            collision_records.append({
                "label": json.loads(label_key),
                "left": list(left["identity"]),
                "right": list(right["identity"]),
                "factor_row_replay_zero": bool(factor_replay_zero),
                "aggregate_equal": bool(aggregate_equal),
                "aggregate_negative": bool(aggregate_negative),
            })
    baseline_rank = p1496.matrix_rank(baseline_rows, order, len(factor_base))
    combined_rank = p1496.matrix_rank(
        baseline_rows + valid_rows, order, len(factor_base)
    )
    return {
        "record_count": len(records),
        "image_size": len(buckets),
        "collision_bucket_count": collision_bucket_count,
        "maximum_bucket_size": maximum_bucket,
        "raw_collision_pairs": raw_pairs,
        "support_distinct_collision_pairs": support_distinct_pairs,
        "subtract_replay_failures": subtract_replay_failures,
        "aggregate_equal_pairs": aggregate_equal_pairs,
        "aggregate_negative_pairs": aggregate_negative_pairs,
        "aggregate_mismatch_pairs": aggregate_mismatch_pairs,
        "label_determines_exact_aggregate_on_sample": max(
            aggregate_images_per_label, default=0
        ) <= 1,
        "maximum_aggregate_images_per_label": max(
            aggregate_images_per_label, default=0
        ),
        "valid_rows": valid_rows,
        "valid_row_count": len(valid_rows),
        "valid_row_hash": p1496.relation_hash([{"row": row} for row in valid_rows]),
        "baseline_rank": baseline_rank,
        "combined_rank": combined_rank,
        "marginal_rank": combined_rank - baseline_rank,
        "zero_false_collision_rows": subtract_replay_failures == 0,
        "collision_records": collision_records,
    }


def cover_lift_table(
    points: list[Any], curve: Any, field: Any, gamma: int
) -> dict[tuple[int, int], list[Any]]:
    roots: dict[int, list[Any]] = defaultdict(list)
    for value in field:
        roots[int(value**3)].append(value)
    table = {}
    for point in points:
        curve_point = curve(p1496.raw_point(point))
        h = field(curve_point[1]) - field(gamma)
        available = sorted(roots[int(h)], key=int)
        if available:
            table[p1496.raw_point(curve_point)] = available
    return table


def null_deck_records(
    source_records: list[dict[str, Any]],
    replicate: int,
    lift_table: dict[tuple[int, int], list[Any]],
    curve: Any,
    field: Any,
    omega: Any,
    p: int,
) -> tuple[list[dict[str, Any]], int]:
    lift_points = [curve(point) for point in sorted(lift_table)]
    generated = []
    retries_total = 0
    for source in source_records:
        aggregate = curve(tuple(source["aggregate"]))
        start = digest_int(
            "p1499-null-start-v1", p, replicate, source["identity"]
        ) % len(lift_points)
        selected = None
        for retry in range(len(lift_points)):
            first = lift_points[(start + retry) % len(lift_points)]
            second = aggregate - first
            if second.is_zero() or first.is_zero() or first[0] == second[0]:
                continue
            second_key = p1496.raw_point(second)
            if second_key not in lift_table:
                continue
            selected = (first, second, retry)
            break
        if selected is None:
            raise RuntimeError("P1499 same-pushforward null has no liftable pair")
        first, second, retry = selected
        retries_total += retry
        first_roots = lift_table[p1496.raw_point(first)]
        second_roots = lift_table[p1496.raw_point(second)]
        z1 = first_roots[
            digest_int("p1499-null-z1-v1", p, replicate, source["identity"])
            % len(first_roots)
        ]
        z2 = second_roots[
            digest_int("p1499-null-z2-v1", p, replicate, source["identity"])
            % len(second_roots)
        ]
        trace = z1 + z2
        norm = z1 * z2
        generated.append({
            "identity": list(source["identity"]),
            "support_hash": source["support_hash"],
            "row": list(source["row"]),
            "aggregate": list(source["aggregate"]),
            "trace": int(trace),
            "norm": int(norm),
            "labels": catalog_labels(trace, norm, omega, p, source["identity"]),
        })
    return generated, retries_total


def render_note(payload: dict[str, Any]) -> str:
    lines = [
        "# P1499 Cross-Anchor Deck-Character Resultant",
        "",
        f"Status: `{payload['status']}`",
        "",
        "The deck lift is reconstructed exactly in the residual quadratic algebra. "
        "The table below separates label collisions from valid elliptic rows.",
        "",
        "| label | dim | image | pairs | false rows | valid rows/rank | aggregate images max |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, record in payload["catalog"].items():
        analysis = record["candidate"]
        lines.append(
            "| {name} | {dim} | {image} | {pairs} | {false} | {rows}/{rank} | {aggregates} |".format(
                name=name,
                dim=record["coordinate_dimension"],
                image=analysis["image_size"],
                pairs=analysis["support_distinct_collision_pairs"],
                false=analysis["subtract_replay_failures"],
                rows=analysis["valid_row_count"],
                rank=analysis["marginal_rank"],
                aggregates=analysis["maximum_aggregate_images_per_label"],
            )
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        payload["interpretation"],
        "",
        "No collision is credited after an aggregate-point filter; that path is "
        "classified as PO73 rather than a new character relation.",
        "",
        "## Next Action",
        "",
        payload["next_action"],
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    started = time.time()
    hashes = {str(path.relative_to(ROOT)): p1496.sha256_file(path) for path in EXPECTED}
    hash_gates = {
        str(path.relative_to(ROOT)): hashes[str(path.relative_to(ROOT))] == expected
        for path, expected in EXPECTED.items()
    }
    if not all(hash_gates.values()):
        raise RuntimeError(f"P1499 frozen hash mismatch: {hash_gates}")
    p1497 = json.loads(P1497.read_text(encoding="ascii"))
    p1497_audit = json.loads(P1497_AUDIT.read_text(encoding="ascii"))
    p1498 = json.loads(P1498.read_text(encoding="ascii"))
    p1498_audit = json.loads(P1498_AUDIT.read_text(encoding="ascii"))
    if not p1497_audit.get("verified") or not p1498_audit.get("verified"):
        raise RuntimeError("P1499 requires verified P1497 and P1498 inputs")
    po71_result = json.loads(p1496.PO71_RESULT.read_text(encoding="ascii"))
    po71_expected = next(
        record for record in po71_result["field_records"] if int(record["p"]) == TARGET_P
    )
    po55 = json.loads(p1496.PO55_RESULT.read_text(encoding="ascii"))
    frozen = next(record for record in po55["records"] if int(record["p"]) == TARGET_P)
    prior = next(record for record in p1497["field_records"] if int(record["p"]) == TARGET_P)
    po71 = p1496.load_module(p1496.PO71_WALK, "p1499_po71_walk")
    po70 = p1496.load_module(p1496.PO70_SOURCE, "p1499_po70_relations")
    direct = p1496.load_module(p1496.PO70_DIRECT, "p1499_po70_direct")
    independent = p1496.load_module(p1496.PO65_DIRECT, "p1499_po65_independent")
    oracle = p1496.load_module(p1496.PO54_ORACLE, "p1499_po54_oracle")
    independent.configure_oracle(oracle, frozen)
    p = TARGET_P
    order = int(frozen["order"])
    field = GF(p)
    curve = EllipticCurve(
        field, [field(frozen["curve_a"]), field(frozen["curve_b"])]
    )
    omega = next(value for value in field if value != 1 and value**3 == 1)
    points = oracle.finite_points(field)
    factor_base = oracle.factor_base_from(oracle.canonical_labels(field, points))
    core = po71.initial_core(factor_base)
    matrix, basis = direct.independent_core_basis(core, field, oracle)
    right_inverse = matrix.solve_right(identity_matrix(field, 6))
    usage = Counter(p1496.raw_label(label) for label in core)
    counters = Counter()
    full_records = []
    one_partials = []
    conventional_two = []
    root_records = []
    deck_records = []
    deck_rejections = []
    threshold_three_attempts = 0
    anchor_index = 0
    transitions = 0
    seen = set()

    while True:
        step = transitions
        transition = None
        if transitions < p1496.PASSES * len(factor_base):
            transition = po71.choose_transition(
                core,
                matrix,
                right_inverse,
                basis,
                transitions % 6,
                usage,
                factor_base,
                field,
                oracle,
                counters,
            )
        variants = po71.choose_variants(
            core,
            factor_base,
            p,
            step,
            transition["incoming"] if transition else None,
        )
        retained = None
        for variant_index, seventh in enumerate(variants):
            anchor = core + [seventh]
            anchor_key = tuple(sorted(p1496.raw_label(label) for label in anchor))
            retain = transition is not None and variant_index == 0
            duplicate = anchor_key in seen
            if duplicate and not retain:
                continue
            constraint = [oracle.evaluation_row(seventh, field) * item for item in basis]
            section = po71.counted_section(constraint, basis, field, counters)
            if section is None:
                raise RuntimeError("P1499 found an empty retained section")
            pivot, _, sections = section
            if duplicate:
                retained = {"pivot": pivot, "sections": sections}
                continue
            seen.add(anchor_key)
            bins, _ = direct.direct_bins(
                anchor,
                sections[0],
                sections[1],
                factor_base,
                field,
                omega,
                independent,
            )
            quotient = po70.build_quotient(
                sections[0], sections[1], anchor, field, frozen, oracle
            )
            classified = direct.classify_direct(
                anchor_index,
                anchor,
                sections[0],
                sections[1],
                bins,
                factor_base,
                points,
                curve,
                field,
                frozen,
                independent,
                oracle,
            )
            full_records.extend(classified["full_records"])
            one_partials.extend(classified["one_partials"])
            conventional_two.extend(classified["two_partials"])
            threshold3 = {parameter for parameter, support in bins.items() if len(support) >= 3}
            threshold4 = {parameter for parameter, support in bins.items() if len(support) >= 4}
            for parameter in sorted(threshold3 - threshold4):
                threshold_three_attempts += 1
                residual = set(bins[parameter])
                root_record, root_reason = p1496.root_free_record(
                    anchor_index,
                    step,
                    variant_index,
                    anchor,
                    int(parameter),
                    residual,
                    quotient,
                    sections[0],
                    sections[1],
                    factor_base,
                    curve,
                    field,
                    frozen,
                    oracle,
                    independent,
                )
                if root_record is None:
                    continue
                root_records.append(root_record)
                deck_record, deck_reason = derive_deck_record(
                    root_record,
                    sections[0],
                    sections[1],
                    int(parameter),
                    field,
                    int(frozen["gamma"]),
                    omega,
                )
                if deck_record is None:
                    deck_rejections.append({
                        "identity": list(root_record["identity"]),
                        "root_reason": root_reason,
                        "deck_reason": deck_reason,
                    })
                else:
                    deck_records.append(deck_record)
            if retain:
                retained = {"pivot": pivot, "sections": sections}
            anchor_index += 1
        if transitions == int(po71_expected["transition_count"]):
            break
        if transition is None or retained is None:
            raise RuntimeError("P1499 transition lost its retained section")
        right_inverse, basis = po71.apply_transition(
            transition,
            retained,
            basis,
            right_inverse,
            len(factor_base),
            field,
            counters,
        )
        core = list(core)
        core[transition["slot"]] = transition["incoming"]
        usage[p1496.raw_label(transition["incoming"])] += 1
        matrix = Matrix(field, matrix)
        matrix.set_row(transition["slot"], transition["new_row"])
        transitions += 1

    p1496.conventional_cross_checks(root_records, conventional_two, field, curve)
    root_hash = p1496.relation_hash(root_records)
    relation_gates = {
        "full_hash_match": p1496.relation_hash(full_records)
        == po71_expected["full_record_hash"],
        "one_lp_hash_match": p1496.relation_hash(one_partials)
        == po71_expected["one_lp_hash"],
        "two_lp_hash_match": p1496.relation_hash(conventional_two)
        == po71_expected["two_lp_hash"],
        "root_record_hash_match": root_hash == prior["graph_record_hash"],
        "root_record_count_match": len(root_records) == int(prior["graph_record_count"]),
        "attempt_count_match": threshold_three_attempts == 392,
    }
    if not all(relation_gates.values()):
        raise RuntimeError(f"P1499 frozen stream mismatch: {relation_gates}")

    conventional_ids = {
        (int(record["anchor_index"]), int(record["parameter"]))
        for record in conventional_two
    }
    rejected_ids = {tuple(record["identity"]) for record in deck_rejections}
    rejected_conventional = sorted(rejected_ids & conventional_ids)
    deck_algebra_exact = (
        all(all(record["checks"].values()) for record in deck_records)
        and not rejected_conventional
    )
    deck_invariance_failures = 0
    for record in deck_records:
        trace = field(record["trace"])
        norm = field(record["norm"])
        for exponent in (1, 2):
            transformed = catalog_labels(
                omega**exponent * trace,
                omega ** (2 * exponent) * norm,
                omega,
                p,
                record["identity"],
            )
            for name, label in record["labels"].items():
                deck_invariance_failures += int(
                    transformed[name]["label"] != label["label"]
                )

    one_rows, _, _ = independent.one_lp_closure(
        one_partials, factor_base, curve, order
    )
    vertical_rows = [
        list(record["row"]) for record in prior["vertical_records"]
    ]
    baseline_rows = [list(record["row"]) for record in full_records] + one_rows + vertical_rows
    baseline_rank = p1496.matrix_rank(baseline_rows, order, len(factor_base))
    if baseline_rank != int(prior["rank"]["exception_complete_baseline"]):
        raise RuntimeError("P1499 exception-complete baseline rank mismatch")

    catalog_names = list(deck_records[0]["labels"]) if deck_records else []
    candidate_catalog = {}
    for name in catalog_names:
        analysis = analyze_label(
            label_records(deck_records, name),
            factor_base,
            curve,
            order,
            baseline_rows,
        )
        candidate_catalog[name] = {
            "coordinate_dimension": int(deck_records[0]["labels"][name]["coordinate_dimension"]),
            "random_control": bool(deck_records[0]["labels"][name]["random_control"]),
            "candidate": analysis,
        }

    lift_table = cover_lift_table(points, curve, field, int(frozen["gamma"]))
    null_runs = {name: [] for name in catalog_names}
    null_retry_total = 0
    for replicate in range(NULL_REPLICATES):
        generated, retries = null_deck_records(
            deck_records,
            replicate,
            lift_table,
            curve,
            field,
            omega,
            p,
        )
        null_retry_total += retries
        for name in catalog_names:
            analysis = analyze_label(
                label_records(generated, name),
                factor_base,
                curve,
                order,
                baseline_rows,
            )
            null_runs[name].append({
                "replicate": replicate,
                "image_size": analysis["image_size"],
                "collision_pairs": analysis["support_distinct_collision_pairs"],
                "false_rows": analysis["subtract_replay_failures"],
                "valid_rows": analysis["valid_row_count"],
                "marginal_rank": analysis["marginal_rank"],
                "valid_row_hash": analysis["valid_row_hash"],
            })
    cap_records = int(math.floor(4 * math.sqrt(order)))
    source_below_rho = threshold_three_attempts <= math.sqrt(order)
    any_promotable = False
    for name, record in candidate_catalog.items():
        runs = null_runs[name]
        analysis = record["candidate"]
        record["same_pushforward_null"] = {
            "replicates": runs,
            "maximum_valid_rows": max(run["valid_rows"] for run in runs),
            "maximum_marginal_rank": max(run["marginal_rank"] for run in runs),
            "mean_collision_pairs": float(statistics.mean(run["collision_pairs"] for run in runs)),
            "mean_false_rows": float(statistics.mean(run["false_rows"] for run in runs)),
        }
        retained = analysis["image_size"] + analysis["valid_row_count"]
        record["retained_records"] = retained
        record["within_memory_cap"] = retained <= cap_records
        record["strictly_beats_all_nulls"] = (
            analysis["valid_row_count"]
            > record["same_pushforward_null"]["maximum_valid_rows"]
            and analysis["marginal_rank"]
            > record["same_pushforward_null"]["maximum_marginal_rank"]
        )
        record["promotable"] = (
            not record["random_control"]
            and analysis["support_distinct_collision_pairs"] > 0
            and analysis["zero_false_collision_rows"]
            and analysis["label_determines_exact_aggregate_on_sample"]
            and analysis["marginal_rank"] > 0
            and record["strictly_beats_all_nulls"]
            and record["within_memory_cap"]
            and record["coordinate_dimension"] < 2
            and source_below_rho
        )
        any_promotable |= record["promotable"]

    synthetic_source = deck_records[0]
    synthetic_relation = list(full_records[0]["row"])
    synthetic_pair = []
    for identity, support_hash, row in (
        ([-1, 0], "p1499-synthetic-left", synthetic_source["row"]),
        (
            [-1, 1],
            "p1499-synthetic-right",
            [a + b for a, b in zip(synthetic_source["row"], synthetic_relation)],
        ),
    ):
        synthetic_pair.append({
            "identity": identity,
            "support_hash": support_hash,
            "label": list(synthetic_source["labels"]["full_trace_norm"]["label"]),
            "row": row,
            "aggregate": list(synthetic_source["aggregate"]),
        })
    synthetic_analysis = analyze_label(
        synthetic_pair, factor_base, curve, order, baseline_rows
    )
    controls = {
        "deck_orbit_labels_invariant": deck_invariance_failures == 0,
        "deck_orbit_invariance_failures": deck_invariance_failures,
        "synthetic_planted_collision_replays": (
            synthetic_analysis["support_distinct_collision_pairs"] == 1
            and synthetic_analysis["subtract_replay_failures"] == 0
            and synthetic_analysis["valid_row_count"] == 1
        ),
        "trace_mutation_changes_full_label": (
            catalog_labels(
                field(synthetic_source["trace"]) + 1,
                field(synthetic_source["norm"]),
                omega,
                p,
                synthetic_source["identity"],
            )["full_trace_norm"]["label"]
            != synthetic_source["labels"]["full_trace_norm"]["label"]
        ),
        "random_catalog_present": all(
            name in candidate_catalog for name in ("random_scalar", "random_pair")
        ),
    }
    controls_exact = (
        controls["deck_orbit_labels_invariant"]
        and controls["deck_orbit_invariance_failures"] == 0
        and controls["synthetic_planted_collision_replays"]
        and controls["trace_mutation_changes_full_label"]
        and controls["random_catalog_present"]
    )
    correctness = (
        all(hash_gates.values())
        and all(relation_gates.values())
        and deck_algebra_exact
        and controls_exact
    )
    if not correctness:
        status = "REVIEW_REQUIRED_P1499_DECK_RESULTANT_REPLAY_MISMATCH"
        interpretation = "At least one frozen stream, deck algebra, or control gate failed; no cryptanalytic interpretation is licensed."
    elif any_promotable:
        status = "MIXED_RESULT_P1499_CHARACTER_RESULTANT_MULTIFIELD_JUSTIFIED"
        interpretation = "At least one preregistered character label clears the p271 applicability gates; a frozen multi-field run is justified, not yet a breakthrough."
    else:
        status = "NEGATIVE_RESULT_P1499_CHARACTER_LABELS_DO_NOT_EMIT_SUBRHO_ROWS"
        interpretation = (
            "The deck lift and character resultants are exact, but every frozen compressed label either emits false elliptic rows, collapses to aggregate equality, retains dimension/state at least two, fails matched nulls, or inherits a source stream already above rho."
        )
    payload = {
        "schema": SCHEMA,
        "status": status,
        "claim_status": "EXACT DECK-LIFT ALGEBRA / CHARACTER-RESULTANT APPLICABILITY TEST / NO GENERIC BREAKTHROUGH",
        "source": str(Path(__file__).resolve()),
        "source_sha256": p1496.sha256_file(Path(__file__).resolve()),
        "contract": str(CONTRACT),
        "contract_sha256": p1496.sha256_file(CONTRACT),
        "frozen_hashes": hashes,
        "hash_gates": hash_gates,
        "field": {
            "p": p,
            "order": order,
            "factor_base_size": len(factor_base),
            "omega": int(omega),
            "gamma": int(frozen["gamma"]),
        },
        "relation_gates": relation_gates,
        "deck_extraction": {
            "threshold_three_attempts": threshold_three_attempts,
            "root_record_count": len(root_records),
            "accepted_deck_records": len(deck_records),
            "rejections": deck_rejections,
            "rejected_conventional_identities": [list(identity) for identity in rejected_conventional],
            "all_algebra_checks_exact": bool(deck_algebra_exact),
            "candidate_root_calls": 0,
            "candidate_square_root_calls": 0,
            "quadratic_algebra_inversions": len(deck_records),
            "quadratic_algebra_multiplication_upper_per_record": 24,
            "record_hash": p1496.relation_hash(deck_records),
        },
        "deck_records": deck_records,
        "baseline": {
            "full_rows": [list(record["row"]) for record in full_records],
            "one_lp_rows": one_rows,
            "vertical_rows": vertical_rows,
            "rank": baseline_rank,
            "row_hash": p1496.relation_hash([{"row": row} for row in baseline_rows]),
        },
        "catalog": candidate_catalog,
        "same_pushforward_null": {
            "replicates": NULL_REPLICATES,
            "liftable_base_points": len(lift_table),
            "total_pair_search_retries": null_retry_total,
        },
        "controls": controls,
        "cost_boundary": {
            "source_attempts": threshold_three_attempts,
            "rho_scale_sqrt_order": float(math.sqrt(order)),
            "source_attempts_over_rho_scale": float(
                threshold_three_attempts / math.sqrt(order)
            ),
            "source_below_rho_scale": bool(source_below_rho),
            "memory_cap_records": cap_records,
        },
        "gates": {
            "all_hashes_and_relations_exact": bool(all(hash_gates.values()) and all(relation_gates.values())),
            "deck_algebra_exact": bool(deck_algebra_exact),
            "all_controls_exact": bool(controls_exact),
            "any_preregistered_label_promotable": bool(any_promotable),
            "p499_p787_p1009_run_justified": bool(any_promotable),
            "generic_shoup_breakthrough": False,
            "beats_pollard_rho": False,
        },
        "interpretation": interpretation,
        "next_action": (
            "If negative, close this trace/norm/discriminant deck-resultant catalog on the frozen cubic cover. The next candidate must change the cover or produce a relation-preserving non-resultant correspondence whose validity does not require the elliptic aggregate or full divisor state."
        ),
        "limitations": [
            "The primary run is p271 only by contract; no multi-field claim is licensed.",
            "Null cover divisors are same-pushforward statistical controls, not zeros of the frozen anchor functions.",
            "The result does not close different covers, nonsimple Pryms, or non-resultant character constructions.",
        ],
        "peak_rss_raw": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
        "wall_seconds": float(time.time() - started),
    }
    p1496.write_atomic(
        OUT, (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    )
    p1496.write_atomic(NOTE, render_note(payload).encode("utf-8"))
    print(json.dumps({
        "status": status,
        "gates": payload["gates"],
        "deck_extraction": payload["deck_extraction"],
        "catalog": {
            name: {
                "dimension": record["coordinate_dimension"],
                "image": record["candidate"]["image_size"],
                "pairs": record["candidate"]["support_distinct_collision_pairs"],
                "false": record["candidate"]["subtract_replay_failures"],
                "valid_rows": record["candidate"]["valid_row_count"],
                "rank": record["candidate"]["marginal_rank"],
                "promotable": record["promotable"],
            }
            for name, record in candidate_catalog.items()
        },
    }, indent=2, sort_keys=True))
    return 1 if status.startswith("REVIEW_REQUIRED") else 0


if __name__ == "__main__":
    raise SystemExit(main())
