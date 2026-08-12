#!/usr/bin/env sage -python
"""Repair P1496 vertical divisor exceptions and rerun frozen decision gates."""

from __future__ import annotations

import json
import math
import resource
import statistics
import time
from collections import Counter
from pathlib import Path
from typing import Any

from sage.all import EllipticCurve, GF, Matrix, PolynomialRing, identity_matrix, vector

import p1496_root_free_quadratic_divisor as p1496


ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = ROOT / "ecdlp_index_calculus_state"
RESEARCH_DIR = ROOT / "research"
CONTRACT = STATE_DIR / "experiment_contract_p1497_exception_complete_quadratic_divisor.md"
P1496_SOURCE = ROOT / "tasks/ecdlp_index_calculus/p1496_root_free_quadratic_divisor.py"
P1496_RESULT = STATE_DIR / "p1496_root_free_quadratic_divisor.json"
OUT = STATE_DIR / "p1497_exception_complete_quadratic_divisor.json"
NOTE = RESEARCH_DIR / "p1497_exception_complete_quadratic_divisor.md"

SCHEMA = "ecdlp.p1497_exception_complete_quadratic_divisor.v1"
EXPECTED = {
    CONTRACT: "41ac083f59581ae41e028d6abfab3e2503ee9f884b3b2ef623e04a094bd5d83f",
    p1496.CONTRACT: "c19d39d45a196e6c9cd7212ed28eadad705ff35dce1329e323327903ee0c485f",
    P1496_SOURCE: "294bfb38487c6e0640ff2d7df1bdb2ac821f4ff4ee8e00d28ff0a7c73505c407",
    P1496_RESULT: "f568a711118263a53905d9f76d32f5bcfc6ce209fd7103583c7e80e0fa2917b5",
    p1496.PO71_RESULT: "79579cbe2655287286e7c6ac099f530bd06744c95b8555ef13a296b04a9f3b05",
    p1496.PO71_WALK: "a3568a0a023c1bb8a6056c33ddef8cbce6c7c790d94e9fb11a55d5d1dc8ef092",
    p1496.PO70_SOURCE: "f30dd608f902009002cb9827c8bf873972f33ad4405fadd38d8051ec600c9109",
    p1496.PO70_DIRECT: "081898d59060c1c343d32275c4ed10759850c34f6caf07a3f7e3909e814e86a4",
    p1496.PO65_DIRECT: "97414a64b4f5b62a7a18dd12a014ad1bfa0df0164d2215b2fd5ceaace0659544",
    p1496.PO55_RESULT: "8584c70805314a4aeb6c6770a82936f0b7ac29e509ed2dd90805d59dd43a03ec",
    p1496.PO54_ORACLE: "80b8c550d162cfc722d01bf73655a2bbdf77599318ee006a2b4955f239dd76de",
}


def vertical_exception(
    anchor_index: int,
    core_index: int,
    variant_index: int,
    anchor: list[Any],
    parameter: int,
    residual: set[tuple[int, int]],
    quotient: Any,
    first: Any,
    second: Any,
    conventional: dict[str, Any],
    factor_base: list[Any],
    curve: Any,
    field: Any,
    frozen: dict[str, Any],
    oracle: Any,
    independent: Any,
) -> dict[str, Any]:
    anchor_points = {p1496.raw_point(label) for label in anchor}
    known = anchor_points | residual
    if len(residual) != 3 or len(known) != 10:
        raise RuntimeError("P1497 vertical exception lacks ten known points")
    ring = PolynomialRing(field, f"p1497_vertical_x_{field.order()}_{anchor_index}_{parameter}")
    x = ring.gen()
    specialized = oracle.specialize(quotient, field(parameter), ring)
    known_product = ring.one()
    for point in sorted(residual):
        known_product *= x - field(point[0])
    remaining, remainder = specialized.quo_rem(known_product)
    if remainder or remaining.degree() != 2:
        raise RuntimeError("P1497 vertical exception is not residual-quadratic")
    u = remaining.monic()
    coefficients = vector(
        field,
        [first[index] + field(parameter) * second[index] for index in range(9)],
    )
    curve_polynomial = x**3 + curve.a4() * x + curve.a6()
    norm_a, norm_b = oracle.norm_pair(
        coefficients,
        field,
        ring,
        curve_polynomial,
        field(frozen["gamma"]),
    )
    a_mod = norm_a % u
    b_mod = norm_b % u
    common = b_mod.gcd(u).monic()
    if common.degree() != 1 or a_mod % common != 0:
        raise RuntimeError("P1497 exception lacks the required singular linear norm branch")
    root = -common[0] / common[1]
    if any(field(point[0]) == root for point in known):
        raise RuntimeError("P1497 exception root already has a known point")
    rhs = root**3 + curve.a4() * root + curve.a6()
    if not rhs.is_square():
        raise RuntimeError("P1497 vertical root has no curve points")
    points = sorted(
        [curve((root, y_value)) for y_value in rhs.sqrt(all=True)],
        key=p1496.raw_point,
    )
    if len(points) != 2 or points[0] != -points[1] or points[0] + points[1] != curve(0):
        raise RuntimeError("P1497 exception is not an exact vertical pair")
    conventional_points = sorted(
        [curve(tuple(point)) for point in conventional["missing_points"]],
        key=p1496.raw_point,
    )
    if [p1496.raw_point(point) for point in conventional_points] != [
        p1496.raw_point(point) for point in points
    ]:
        raise RuntimeError("P1497 vertical pair does not match the conventional record")
    known_sum = curve(0)
    for point in sorted(known):
        known_sum += curve(point)
    if not known_sum.is_zero():
        raise RuntimeError("P1497 vertical exception known row is not aggregate-zero")
    factor_index = {
        p1496.raw_point(label): index for index, label in enumerate(factor_base)
    }
    row = independent.row_from_points(known, factor_index, len(factor_base))
    if not independent.row_sum(row, factor_base, curve).is_zero():
        raise RuntimeError("P1497 vertical exception row replay failed")
    support_points = [list(point) for point in sorted(known)]
    return {
        "anchor_index": int(anchor_index),
        "core_index": int(core_index),
        "variant_index": int(variant_index),
        "parameter": int(parameter),
        "identity": [int(anchor_index), int(parameter)],
        "support_hash": p1496.digest(p1496.compact(support_points).encode("ascii")),
        "support_points": support_points,
        "vertical_x": int(root),
        "missing_points": [list(p1496.raw_point(point)) for point in points],
        "row": [int(value) for value in row],
        "certificate": {
            "u": p1496.polynomial_coefficients(u, 3),
            "a_mod_u": p1496.polynomial_coefficients(a_mod, 2),
            "b_mod_u": p1496.polynomial_coefficients(b_mod, 2),
            "gcd_b_u": p1496.polynomial_coefficients(common, 2),
            "known_sum_zero": True,
            "vertical_points_are_negatives": True,
            "conventional_pair_match": True,
            "row_replay_zero": True,
        },
    }


def deduplicate_vertical_rows(
    records: list[dict[str, Any]], order: int
) -> tuple[list[list[int]], str]:
    rows = []
    keys = set()
    for record in sorted(records, key=lambda item: tuple(item["identity"])):
        key = p1496.canonical_row(record["row"], order)
        if not any(key) or key in keys:
            continue
        keys.add(key)
        rows.append(record["row"])
    return rows, p1496.relation_hash([{"row": row} for row in rows])


def render_note(payload: dict[str, Any]) -> str:
    lines = [
        "# P1497 Exception-Complete Quadratic Divisor",
        "",
        f"Status: `{payload['status']}`",
        "",
        "P1497 preserves P1496 and repairs its two vertical-pair exceptions by "
        "promoting their aggregate-zero rows into the common baseline.",
        "",
        "| p | graph records | vertical rows | collisions | marginal rank | null max rows/rank | retained/cap |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for record in payload["field_records"]:
        lines.append(
            "| {p} | {graph} | {vertical} | {collisions} | {rank} | {null_rows}/{null_rank} | {retained}/{cap} |".format(
                p=record["p"],
                graph=record["graph_record_count"],
                vertical=len(record["vertical_records"]),
                collisions=record["candidate"]["usable_collision_rows"],
                rank=record["rank"]["candidate_marginal"],
                null_rows=record["same_class_null"]["maximum_collision_rows"],
                null_rank=record["same_class_null"]["maximum_marginal_rank"],
                retained=record["memory"]["retained_records"],
                cap=record["memory"]["cap_records"],
            )
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        payload["interpretation"],
        "",
        "The vertical promotions are ordinary aggregate-zero group relations. They "
        "do not count as cover-specific concentration or a generic ECDLP gain.",
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
        raise RuntimeError(f"P1497 frozen hash mismatch: {hash_gates}")
    prior = json.loads(P1496_RESULT.read_text(encoding="ascii"))
    if prior["status"] != "REVIEW_REQUIRED_P1496_ROOT_FREE_DIVISOR_REPLAY_MISMATCH":
        raise RuntimeError("P1497 requires the frozen P1496 review result")
    prior_by_p = {int(record["p"]): record for record in prior["field_records"]}
    po71_result = json.loads(p1496.PO71_RESULT.read_text(encoding="ascii"))
    po71_by_p = {int(record["p"]): record for record in po71_result["field_records"]}
    po55 = json.loads(p1496.PO55_RESULT.read_text(encoding="ascii"))
    po71 = p1496.load_module(p1496.PO71_WALK, "p1497_po71_walk")
    po70 = p1496.load_module(p1496.PO70_SOURCE, "p1497_po70_relations")
    direct = p1496.load_module(p1496.PO70_DIRECT, "p1497_po70_direct")
    independent = p1496.load_module(p1496.PO65_DIRECT, "p1497_po65_independent")
    oracle = p1496.load_module(p1496.PO54_ORACLE, "p1497_po54_oracle")
    field_records = []

    for frozen in po55["records"]:
        field_started = time.perf_counter()
        independent.configure_oracle(oracle, frozen)
        p = int(frozen["p"])
        order = int(frozen["order"])
        field = GF(p)
        curve = EllipticCurve(field, [field(frozen["curve_a"]), field(frozen["curve_b"])])
        generator = curve.gens()[0]
        omega = next(value for value in field if value != 1 and value**3 == 1)
        points = oracle.finite_points(field)
        factor_base = oracle.factor_base_from(oracle.canonical_labels(field, points))
        expected = po71_by_p[p]
        prior_field = prior_by_p[p]
        prior_rejections = {
            tuple(record["identity"]): record["reason"]
            for record in prior_field["extraction_rejections"]
        }
        core = po71.initial_core(factor_base)
        matrix, basis = direct.independent_core_basis(core, field, oracle)
        right_inverse = matrix.solve_right(identity_matrix(field, 6))
        usage = Counter(p1496.raw_label(label) for label in core)
        counters = Counter()
        full_records = []
        one_partials = []
        conventional_two = []
        graph_records = []
        vertical_records = []
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
                    raise RuntimeError("P1497 found an empty retained section")
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
                conventional_by_parameter = {
                    int(record["parameter"]): record
                    for record in classified["two_partials"]
                }
                threshold3 = {parameter for parameter, support in bins.items() if len(support) >= 3}
                threshold4 = {parameter for parameter, support in bins.items() if len(support) >= 4}
                for parameter in sorted(threshold3 - threshold4):
                    residual = set(bins[parameter])
                    record, reason = p1496.root_free_record(
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
                    if record is not None:
                        graph_records.append(record)
                        continue
                    identity = (int(anchor_index), int(parameter))
                    conventional = conventional_by_parameter.get(int(parameter))
                    if conventional is None:
                        continue
                    if reason != "singular_branch_missing_known_root" or prior_rejections.get(identity) != reason:
                        raise RuntimeError(
                            f"P1497 unclassified conventional record p={p} identity={identity} reason={reason}"
                        )
                    vertical_records.append(vertical_exception(
                        anchor_index,
                        step,
                        variant_index,
                        anchor,
                        int(parameter),
                        residual,
                        quotient,
                        sections[0],
                        sections[1],
                        conventional,
                        factor_base,
                        curve,
                        field,
                        frozen,
                        oracle,
                        independent,
                    ))
                if retain:
                    retained = {"pivot": pivot, "sections": sections}
                anchor_index += 1
            if transitions == int(expected["transition_count"]):
                break
            if transition is None or retained is None:
                raise RuntimeError("P1497 transition lost its retained section")
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

        cross = p1496.conventional_cross_checks(graph_records, conventional_two, field, curve)
        graph_ids = {tuple(record["identity"]) for record in graph_records}
        vertical_ids = {tuple(record["identity"]) for record in vertical_records}
        conventional_ids = {
            (int(record["anchor_index"]), int(record["parameter"]))
            for record in conventional_two
        }
        conventional_graph_ids = graph_ids & conventional_ids
        classification_exact = (
            not (conventional_graph_ids & vertical_ids)
            and conventional_graph_ids | vertical_ids == conventional_ids
            and cross["label_mismatches"] == 0
            and cross["sign_mismatches"] == 0
            and set(map(tuple, cross["missing_root_identities"])) == vertical_ids
        )
        graph_hash = p1496.relation_hash(graph_records)
        candidate = p1496.close_divisor_labels(
            graph_records, factor_base, curve, order, independent
        )
        vertical_rows, vertical_row_hash = deduplicate_vertical_rows(vertical_records, order)
        one_rows, _, _ = independent.one_lp_closure(
            one_partials, factor_base, curve, order
        )
        original_baseline = [list(record["row"]) for record in full_records] + one_rows
        baseline_rows = original_baseline + vertical_rows
        baseline_rank = p1496.matrix_rank(baseline_rows, order, len(factor_base))
        candidate_rank = p1496.matrix_rank(
            baseline_rows + candidate["rows"], order, len(factor_base)
        )
        candidate_marginal = candidate_rank - baseline_rank
        null_stats = []
        for replicate in range(p1496.NULL_REPLICATES):
            generated, generation = p1496.same_class_null_records(
                graph_records,
                p,
                replicate,
                order,
                generator,
                curve,
                field,
            )
            closed = p1496.close_divisor_labels(
                generated, factor_base, curve, order, independent
            )
            null_rank = p1496.matrix_rank(
                baseline_rows + closed["rows"], order, len(factor_base)
            )
            null_stats.append({
                "replicate": replicate,
                "collision_rows": int(closed["usable_collision_rows"]),
                "marginal_rank": int(null_rank - baseline_rank),
                "replay_failures": int(closed["replay_failures"]),
                "row_hash": closed["row_hash"],
                **generation,
            })
        null_collision = [record["collision_rows"] for record in null_stats]
        null_rank = [record["marginal_rank"] for record in null_stats]
        same_class_null = {
            "replicates": null_stats,
            "maximum_collision_rows": max(null_collision, default=0),
            "mean_collision_rows": statistics.mean(null_collision) if null_collision else 0.0,
            "maximum_marginal_rank": max(null_rank, default=0),
            "mean_marginal_rank": statistics.mean(null_rank) if null_rank else 0.0,
            "candidate_collision_plus_one_tail": float(
                (1 + sum(value >= candidate["usable_collision_rows"] for value in null_collision))
                / (p1496.NULL_REPLICATES + 1)
            ),
            "candidate_rank_plus_one_tail": float(
                (1 + sum(value >= candidate_marginal for value in null_rank))
                / (p1496.NULL_REPLICATES + 1)
            ),
            "candidate_strictly_beats_all_collision_controls": bool(
                candidate["usable_collision_rows"] > max(null_collision, default=-1)
            ),
            "candidate_strictly_beats_all_rank_controls": bool(
                candidate_marginal > max(null_rank, default=-1)
            ),
        }
        relation_gates = {
            "full_hash_match": p1496.relation_hash(full_records) == expected["full_record_hash"],
            "one_lp_hash_match": p1496.relation_hash(one_partials) == expected["one_lp_hash"],
            "two_lp_hash_match": p1496.relation_hash(conventional_two) == expected["two_lp_hash"],
            "graph_record_hash_unchanged": graph_hash == prior_field["root_free_record_hash"],
            "graph_closure_hash_unchanged": candidate["row_hash"] == prior_field["candidate"]["row_hash"],
            "original_baseline_hash_unchanged": p1496.relation_hash(
                [{"row": row} for row in original_baseline]
            ) == prior_field["baseline"]["row_hash"],
        }
        cap_records = int(math.floor(4 * math.sqrt(order)))
        retained_records = int(
            candidate["label_count"]
            + candidate["usable_collision_rows"]
            + len(vertical_rows)
        )
        field_records.append({
            "p": p,
            "order": order,
            "holdout": p == 1009,
            "factor_base_size": len(factor_base),
            "graph_record_count": len(graph_records),
            "graph_record_hash": graph_hash,
            "vertical_records": vertical_records,
            "vertical_row_hash": vertical_row_hash,
            "candidate": candidate,
            "rank": {
                "original_baseline": p1496.matrix_rank(
                    original_baseline, order, len(factor_base)
                ),
                "exception_complete_baseline": baseline_rank,
                "candidate": candidate_rank,
                "candidate_marginal": candidate_marginal,
                "target": len(factor_base) - 1,
            },
            "same_class_null": same_class_null,
            "relation_gates": relation_gates,
            "classification": {
                "conventional_count": len(conventional_ids),
                "graph_count": len(graph_ids),
                "conventional_graph_count": len(conventional_graph_ids),
                "vertical_count": len(vertical_ids),
                "exact_partition": bool(classification_exact),
                "graph_cross_check": cross,
            },
            "memory": {
                "retained_records": retained_records,
                "cap_records": cap_records,
                "within_cap": retained_records <= cap_records,
            },
            "wall_seconds": float(time.perf_counter() - field_started),
        })

    tuning = [record for record in field_records if not record["holdout"]]
    correctness = all(
        all(record["relation_gates"].values())
        and record["classification"]["exact_partition"]
        and all(
            all(value for value in vertical["certificate"].values())
            for vertical in record["vertical_records"]
        )
        and record["candidate"]["replay_failures"] == 0
        and all(item["replay_failures"] == 0 for item in record["same_class_null"]["replicates"])
        for record in field_records
    )
    positive_rank = all(record["rank"]["candidate_marginal"] > 0 for record in tuning)
    beats_null = all(
        record["same_class_null"]["candidate_strictly_beats_all_collision_controls"]
        and record["same_class_null"]["candidate_strictly_beats_all_rank_controls"]
        for record in tuning
    )
    memory = all(record["memory"]["within_cap"] for record in tuning)
    if not correctness:
        status = "REVIEW_REQUIRED_P1497_EXCEPTION_REPAIR_MISMATCH"
        interpretation = "The versioned vertical repair failed at least one exact partition or replay check."
    elif not beats_null:
        status = "NEGATIVE_RESULT_P1497_EXACT_DIVISOR_NO_COVER_CONCENTRATION"
        interpretation = "The exception-complete representation is exact, but nonvertical collisions and rank do not beat every same-class control on the tuning fields."
    elif not positive_rank:
        status = "NEGATIVE_RESULT_P1497_EXACT_DIVISOR_NO_TUNING_RANK"
        interpretation = "The exception-complete representation is exact but lacks positive nonvertical marginal rank on a tuning field."
    elif not memory:
        status = "NEGATIVE_RESULT_P1497_EXACT_DIVISOR_MEMORY_GATE"
        interpretation = "The exception-complete representation clears algebra and concentration but exceeds the frozen memory cap."
    else:
        status = "MIXED_RESULT_P1497_EXCEPTION_COMPLETE_FOLLOW_ON_JUSTIFIED"
        interpretation = "The repaired preflight clears its follow-on gates, but no generic or rho improvement has been established."
    payload = {
        "schema": SCHEMA,
        "status": status,
        "claim_status": "VERSIONED CORRECTNESS REPAIR / TOY PREFLIGHT / NO GENERIC BREAKTHROUGH",
        "source": str(Path(__file__).resolve()),
        "source_sha256": p1496.sha256_file(Path(__file__).resolve()),
        "contract": str(CONTRACT),
        "contract_sha256": p1496.sha256_file(CONTRACT),
        "frozen_hashes": hashes,
        "hash_gates": hash_gates,
        "field_records": field_records,
        "gates": {
            "all_hashes_match": all(hash_gates.values()),
            "exception_complete_correctness": correctness,
            "positive_nonvertical_rank_all_tuning_fields": positive_rank,
            "beats_all_same_class_nulls_all_tuning_fields": beats_null,
            "within_memory_cap_all_tuning_fields": memory,
            "generic_shoup_breakthrough": False,
            "beats_pollard_rho": False,
        },
        "interpretation": interpretation,
        "next_action": (
            "Close exact degree-two divisor fingerprints on the frozen PO71 stream. Move to a genuinely non-scalar auxiliary-Jacobian or quotient invariant with a lower-dimensional collision label; preregister equal-class nulls and a streaming memory bound before implementation."
        ),
        "limitations": [
            "All fields are toy-scale and reuse the frozen PO71 source stream.",
            "Vertical aggregate-zero promotions are generic group-law relations, not cover-specific evidence.",
            "The result closes this exact divisor label only; it does not close higher-genus auxiliary Jacobians or non-scalar correspondences.",
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
        "fields": [
            {
                "p": record["p"],
                "graph": record["graph_record_count"],
                "vertical": len(record["vertical_records"]),
                "collisions": record["candidate"]["usable_collision_rows"],
                "marginal_rank": record["rank"]["candidate_marginal"],
                "null_max_rows": record["same_class_null"]["maximum_collision_rows"],
                "null_max_rank": record["same_class_null"]["maximum_marginal_rank"],
            }
            for record in field_records
        ],
    }, indent=2, sort_keys=True))
    return 1 if status.startswith("REVIEW_REQUIRED") else 0


if __name__ == "__main__":
    raise SystemExit(main())
