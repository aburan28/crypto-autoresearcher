from __future__ import annotations

import copy
import hashlib
import itertools
import json
import math
import os
import runpy
import tempfile
import unittest
from pathlib import Path

from crypto_autoresearcher.records import find_repo_root


REPO_ROOT = find_repo_root(Path(__file__).parent)
SOURCE = (
    REPO_ROOT
    / "experiments"
    / "EXP-SGCP-EMBED-002"
    / "src"
    / "sgcp_embed_family.py"
)
MODULE = runpy.run_path(str(SOURCE))
VERIFIER_SOURCE = SOURCE.with_name("verify_sgcp_embed_family.py")
VERIFIER = runpy.run_path(str(VERIFIER_SOURCE))


def exhaustive_graph(
    pair_outputs: list[list[int]], conflicts: list[int]
) -> tuple[int, int]:
    best = (0, 0)
    for mask in range(1 << len(conflicts)):
        if any(conflicts[index] & mask for index in MODULE["iter_mask"](mask)):
            continue
        support = MODULE["support_mask_for_selection"](mask, pair_outputs).bit_count()
        best = max(best, (support, mask.bit_count()))
    return best


def resign_density_row(row: dict[str, object]) -> None:
    payload = dict(row)
    payload.pop("row_sha256", None)
    row["row_sha256"] = VERIFIER["digest"](payload)


def refresh_density_accounting(row: dict[str, object]) -> None:
    public_model = row["public_model"]
    private_audit = row["private_audit"]
    public_caps = public_model["density_frontier"]
    private_caps = private_audit["density_frontier"]
    row_payload = dict(row)
    row_payload.pop("row_sha256", None)
    row_payload.pop("accounting", None)
    row["accounting"] = {
        "scope": "nested canonical-JSON byte measures; fields are nonadditive",
        "public_model_json_bytes": len(VERIFIER["stable_bytes"](public_model)),
        "private_audit_json_bytes": len(VERIFIER["stable_bytes"](private_audit)),
        "row_payload_without_accounting_or_digest_json_bytes": len(
            VERIFIER["stable_bytes"](row_payload)
        ),
        "nested_per_cap_json_bytes": [
            {
                "constrained_cap": public["constrained_cap"],
                "public_embedding_json_bytes": len(VERIFIER["stable_bytes"](public)),
                "private_cap_json_bytes": len(VERIFIER["stable_bytes"](private)),
            }
            for public, private in zip(public_caps, private_caps)
        ],
    }
    resign_density_row(row)


def resign_factor_base(row: dict[str, object]) -> None:
    record = row["public_model"]["factor_base"]
    payload = dict(record)
    payload.pop("selection_sha256", None)
    record["selection_sha256"] = VERIFIER["digest"](payload)


def resign_document(document: dict[str, object]) -> None:
    payload = dict(document)
    payload.pop("document_sha256", None)
    document["document_sha256"] = VERIFIER["digest"](payload)


def synthetic_gate_rows() -> list[dict[str, object]]:
    group_sizes = {5: 23, 6: 47, 7: 97, 8: 193}
    rows = []
    for bits, seed, B, family, replicate in MODULE["canonical_row_keys"]():
        q = group_sizes[bits]
        caps = sorted({max(1, q // 4), max(1, q // 2), max(1, 3 * q // 4), q})
        if family == MODULE["NULL_FAMILY"]:
            support = (1, 2, 2, 3)[replicate]
        else:
            support = q // 2
        public_caps = [{"constrained_cap": cap} for cap in caps]
        private_caps = [
            {
                "constrained_cap": cap,
                "optimizer": {
                    "retained_support_lower_bound": support,
                    "retained_support_upper_bound": support,
                    "primary_exact": True,
                    "full_objective_exact": True,
                    "absolute_gap": 0,
                    "remaining_frontier_nodes": 0,
                    "frontier_states": [],
                    "frontier_sha256": VERIFIER["digest"]([]),
                    "termination_reason": "full_objective_proved",
                    "node_cap": MODULE["CANONICAL_NODE_CAP"],
                },
                "retention": {
                    "retained_to_balanced_raw": {
                        "numerator": 1,
                        "denominator": 2,
                    }
                },
            }
            for cap in caps
        ]
        rows.append(
            {
                "curve": {
                    "bits": bits,
                    "seed": seed,
                    "p": 10_000 * bits + seed,
                    "a": bits,
                    "b": seed,
                    "q": q,
                },
                "B": B,
                "family": family,
                "null_replicate": replicate,
                "public_model": {
                    "constrained_budget_caps": caps,
                    "density_frontier": public_caps,
                },
                "private_audit": {"density_frontier": private_caps},
            }
        )
    return rows


def standalone_point_order(point):
    return (0, 0, 0) if point is None else (1, point[0], point[1])


def standalone_stable_bytes(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode("ascii")


def standalone_digest(value):
    return hashlib.sha256(standalone_stable_bytes(value)).hexdigest()


def standalone_point_record(point):
    return "O" if point is None else [point[0], point[1]]


def standalone_label(point):
    return "O" if point is None else f"{point[0]}:{point[1]}"


def standalone_add(p, a, left, right):
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if left == right:
        slope = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        slope = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    return x3, (slope * (x1 - x3) - y1) % p


def standalone_eval(p, a, factors, formal):
    point = None
    for index in formal:
        point = standalone_add(p, a, point, factors[index])
    return point


def standalone_submultisets(formal):
    values = {()}
    for degree in range(1, len(formal) + 1):
        values.update(itertools.combinations(formal, degree))
    return values


def standalone_ideal(B, maxima):
    values = {(), *((index,) for index in range(B))}
    for maximum in maxima:
        values.update(standalone_submultisets(tuple(sorted(maximum))))
    return values


def standalone_polynomial(roots, p):
    coefficients = [1]
    for root in roots:
        updated = [0] * (len(coefficients) + 1)
        for index, coefficient in enumerate(coefficients):
            updated[index] = (updated[index] - root * coefficient) % p
            updated[index + 1] = (updated[index + 1] + coefficient) % p
        coefficients = updated
    return coefficients


def standalone_graph_metrics(conflicts):
    count = len(conflicts)
    degrees = [mask.bit_count() for mask in conflicts]
    unseen = set(range(count))
    components = []
    while unseen:
        stack = [min(unseen)]
        unseen.remove(stack[0])
        component = []
        while stack:
            vertex = stack.pop()
            component.append(vertex)
            neighbors = {
                index for index in unseen if conflicts[vertex] & (1 << index)
            }
            unseen.difference_update(neighbors)
            stack.extend(sorted(neighbors, reverse=True))
        components.append(sorted(component))
    remaining = set(range(count))
    degeneracy = 0
    while remaining:
        vertex = min(
            remaining,
            key=lambda index: (
                sum(bool(conflicts[index] & (1 << other)) for other in remaining),
                index,
            ),
        )
        degree = sum(
            bool(conflicts[vertex] & (1 << other)) for other in remaining
        )
        degeneracy = max(degeneracy, degree)
        remaining.remove(vertex)
    histogram = {str(degree): degrees.count(degree) for degree in sorted(set(degrees))}
    return {
        "vertices": count,
        "edges": sum(degrees) // 2,
        "components": sorted(len(component) for component in components),
        "component_count": len(components),
        "degree_min": min(degrees, default=0),
        "degree_max": max(degrees, default=0),
        "degree_histogram": histogram,
        "degeneracy": degeneracy,
    }


def standalone_frozen_b4_oracle():
    """Rebuild the B4 object without producer or verifier semantic helpers."""
    p = 19
    a = 2
    b = 9
    B = 4
    affine = [
        (x, y)
        for x in range(p)
        for y in range(p)
        if (y * y - (x * x * x + a * x + b)) % p == 0
    ]
    q = len(affine) + 1
    fibers = {}
    for point in affine:
        fibers.setdefault(point[0], []).append(point)
    admissible = [
        x
        for x in sorted(fibers)
        if len(fibers[x]) == 2
        and (fibers[x][0][1] + fibers[x][1][1]) % p == 0
    ]
    roots = admissible[: B // 2]
    factors = sorted(
        [point for x in roots for point in fibers[x]], key=standalone_point_order
    )
    factor_base = {
        "family": "least_x_interval",
        "null_replicate": None,
        "B": B,
        "admissible_root_count": len(admissible),
        "selected_roots": roots,
        "selected_root_count": len(roots),
        "excluded_poles": [],
        "parameters": {},
        "root_polynomial_coefficients_ascending_mod_p": standalone_polynomial(
            roots, p
        ),
        "points": [standalone_point_record(point) for point in factors],
        "negation_symmetric": True,
    }
    factor_base["selection_sha256"] = standalone_digest(factor_base)

    degree2_by_point = {}
    for formal in itertools.combinations_with_replacement(range(B), 2):
        point = standalone_eval(p, a, factors, formal)
        degree2_by_point.setdefault(point, []).append(formal)
    representatives = [
        (point, min(degree2_by_point[point]))
        for point in sorted(degree2_by_point, key=standalone_point_order)
        if point is not None
    ]
    representative_records = [
        {"point": standalone_point_record(point), "formal": list(formal)}
        for point, formal in representatives
    ]
    representative_compiler = {
        "id": "lexicographically_least_formal_per_nonidentity_2F_output_v2",
        "identity_output_excluded": True,
        "representative_count": len(representative_records),
        "representatives": representative_records,
        "representatives_sha256": standalone_digest(representative_records),
    }

    candidate_points = {}
    candidate_parent_pairs = {}
    for left, right in itertools.combinations_with_replacement(
        range(len(representatives)), 2
    ):
        left_point, left_formal = representatives[left]
        right_point, right_formal = representatives[right]
        formal = tuple(sorted(left_formal + right_formal))
        point = standalone_add(p, a, left_point, right_point)
        parent_pair = tuple(sorted((left_formal, right_formal)))
        if formal in candidate_points:
            assert candidate_points[formal] == point
        candidate_points[formal] = point
        candidate_parent_pairs.setdefault(formal, []).append(parent_pair)
    candidates = [
        {
            "formal": formal,
            "point": candidate_points[formal],
            "parent_pairs": sorted(candidate_parent_pairs[formal]),
        }
        for formal in sorted(candidate_points)
    ]

    eligible = []
    eligible_universe_indices = []
    rejected = []
    closure_maps = []
    for universe_index, candidate in enumerate(candidates):
        family = standalone_ideal(B, [candidate["formal"]])
        point_to_formal = {}
        first_collision = None
        for formal in sorted(family, key=lambda item: (len(item), item)):
            point = standalone_eval(p, a, factors, formal)
            if point in point_to_formal:
                first_collision = (point_to_formal[point], formal, point)
                break
            point_to_formal[point] = formal
        if first_collision is None:
            eligible.append(candidate)
            eligible_universe_indices.append(universe_index)
            closure_maps.append(point_to_formal)
        else:
            left, right, point = first_collision
            rejected.append(
                {
                    "universe_index": universe_index,
                    "formal": list(candidate["formal"]),
                    "point": standalone_point_record(candidate["point"]),
                    "first_collision": {
                        "left": list(left),
                        "right": list(right),
                        "point": standalone_point_record(point),
                    },
                }
            )

    conflicts = [0] * len(eligible)
    conflict_records = []
    for left in range(len(eligible)):
        for right in range(left + 1, len(eligible)):
            first_collision = next(
                (
                    (
                        closure_maps[left][point],
                        closure_maps[right][point],
                        point,
                    )
                    for point in sorted(
                        set(closure_maps[left]).intersection(closure_maps[right]),
                        key=standalone_point_order,
                    )
                    if closure_maps[left][point] != closure_maps[right][point]
                ),
                None,
            )
            if first_collision is not None:
                conflicts[left] |= 1 << right
                conflicts[right] |= 1 << left
                left_formal, right_formal, point = first_collision
                conflict_records.append(
                    {
                        "left": left,
                        "right": right,
                        "left_universe_index": eligible_universe_indices[left],
                        "right_universe_index": eligible_universe_indices[right],
                        "first_collision": {
                            "left": list(left_formal),
                            "right": list(right_formal),
                            "point": standalone_point_record(point),
                        },
                    }
                )

    candidates_by_cap = {}
    for mask in range(1 << len(eligible)):
        selected_indices = [
            index for index in range(len(eligible)) if mask & (1 << index)
        ]
        if any(conflicts[index] & mask for index in selected_indices):
            continue
        maxima = [eligible[index]["formal"] for index in selected_indices]
        family = standalone_ideal(B, maxima)
        evaluations = {
            formal: standalone_eval(p, a, factors, formal) for formal in family
        }
        assert len(set(evaluations.values())) == len(evaluations)
        nonempty = sorted(
            (formal for formal in family if formal), key=lambda item: (len(item), item)
        )
        constrained = {None}
        edges = []
        for position, left in enumerate(nonempty):
            for right in nonempty[position:]:
                union = tuple(sorted(left + right))
                if union not in family:
                    continue
                edges.append((left, right, union))
                constrained.update(
                    (evaluations[left], evaluations[right], evaluations[union])
                )
        selected_points = [eligible[index]["point"] for index in selected_indices]
        support = {
            standalone_add(p, a, left, right)
            for position, left in enumerate(selected_points)
            for right in selected_points[position:]
        }
        objective = (len(support), -len(constrained), -len(edges), len(maxima))
        witness = tuple(sorted(maxima))
        public_edges = [
            {
                "left": standalone_label(evaluations[left]),
                "right": standalone_label(evaluations[right]),
                "output": standalone_label(evaluations[output]),
            }
            for left, right, output in edges
        ]
        source_table = [
            {"label": standalone_label(point), "formal": list(formal)}
            for point, formal in sorted(
                (
                    (point, formal)
                    for formal, point in evaluations.items()
                    if point in constrained
                ),
                key=lambda item: standalone_point_order(item[0]),
            )
        ]
        degree_histogram = {
            str(degree): sum(len(formal) == degree for formal in family)
            for degree in sorted({len(formal) for formal in family})
        }
        forbidden_final_edges = sum(
            len(left) == 4 and len(right) == 4 for left, right, _ in edges
        )
        axioms = {
            "identity": True,
            "commutativity": True,
            "associativity": all(
                standalone_submultisets(formal).issubset(family)
                for formal in family
            ),
            "associativity_method": "downward-closed formal multiset union",
            "compatibility_coordinates": all(
                standalone_add(
                    p, a, evaluations[left], evaluations[right]
                )
                == evaluations[output]
                for left, right, output in edges
            ),
            "injective_evaluation": len(set(evaluations.values())) == len(evaluations),
            "unique_prime_multiset_factorization": len(set(evaluations.values()))
            == len(evaluations),
            "acyclic_by_formal_degree": all(
                len(output) > max(len(left), len(right))
                for left, right, output in edges
            ),
            "source_recovery": all(tuple(sorted(formal)) == formal for formal in family),
            "source_recovery_via_public_table": len(source_table) == len(constrained),
            "direct_final_edge_excluded": forbidden_final_edges == 0,
            "direct_final_edge_absent_by_construction": forbidden_final_edges == 0,
            "forbidden_final_edge_count": forbidden_final_edges,
        }
        divisor = math.gcd(len(constrained), q)
        candidate = {
            "objective": objective,
            "witness": witness,
            "selected_indices": selected_indices,
            "selected_mask_hex": hex(sum(1 << index for index in selected_indices)),
            "formal_family_count": len(family),
            "formal_degree_histogram": degree_histogram,
            "constrained_count": len(constrained),
            "delta": {
                "numerator": len(constrained) // divisor,
                "denominator": q // divisor,
            },
            "constrained_labels": [
                standalone_label(point)
                for point in sorted(constrained, key=standalone_point_order)
            ],
            "public_edge_count": len(edges),
            "public_edges": public_edges,
            "public_edges_sha256": standalone_digest(public_edges),
            "source_table": source_table,
            "source_table_sha256": standalone_digest(source_table),
            "axioms": axioms,
        }
        caps = sorted({max(1, q // 4), max(1, q // 2), max(1, 3 * q // 4), q})
        for cap in caps:
            if len(constrained) <= cap:
                candidates_by_cap.setdefault(cap, []).append(candidate)

    winners = {}
    for cap, values in candidates_by_cap.items():
        best_objective = max(value["objective"] for value in values)
        best_witness = min(
            value["witness"]
            for value in values
            if value["objective"] == best_objective
        )
        winners[cap] = next(
            value
            for value in values
            if value["objective"] == best_objective
            and value["witness"] == best_witness
        )
    return {
        "factors": factors,
        "factor_base": factor_base,
        "representatives": representative_records,
        "representative_compiler": representative_compiler,
        "candidates": candidates,
        "eligible": eligible,
        "candidate_count": len(candidates),
        "eligible_count": len(eligible),
        "eligible_universe_indices": eligible_universe_indices,
        "individually_rejected": rejected,
        "conflicts": conflict_records,
        "conflict_count": len(conflict_records),
        "graph_metrics": standalone_graph_metrics(conflicts),
        "caps": caps,
        "winners": winners,
    }


def configure_gate_rows(null_supports=(8, 8, 10, 12)):
    rows = synthetic_gate_rows()
    for row in rows:
        support = null_supports[row["null_replicate"]] if row["family"] == MODULE["NULL_FAMILY"] else 10
        for private in row["private_audit"]["density_frontier"]:
            private["optimizer"]["retained_support_lower_bound"] = support
            private["optimizer"]["retained_support_upper_bound"] = support
    return rows


def set_gate_differences(rows, family, cap_fraction, differences_by_bits):
    for bits in MODULE["CANONICAL_BITS"]:
        coordinate_rows = [
            row
            for row in rows
            if row["curve"]["bits"] == bits
            and row["family"] == family
            and row["null_replicate"] is None
        ]
        coordinate_rows.sort(key=lambda row: (row["curve"]["seed"], row["B"]))
        for row, difference in zip(coordinate_rows, differences_by_bits[bits]):
            q = row["curve"]["q"]
            cap = q // 2 if cap_fraction == "1/2" else 3 * q // 4
            cell = next(
                value
                for value in row["private_audit"]["density_frontier"]
                if value["constrained_cap"] == cap
            )
            cell["optimizer"]["retained_support_lower_bound"] = 9 + difference
            cell["optimizer"]["retained_support_upper_bound"] = 9 + difference


def gate_cap_report(gate, family, cap_fraction):
    family_report = next(value for value in gate["families"] if value["family"] == family)
    return next(
        value
        for value in family_report["matched_null_cap_tests"]
        if value["cap_fraction"] == cap_fraction
    )


class SgcpEmbedFamilyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        ops = MODULE["OperationCounts"]()
        curve, points, record = MODULE["frozen_curve"](ops)
        cls.frozen_density_row = MODULE["build_density_row"](
            curve,
            points,
            record,
            4,
            "least_x_interval",
            None,
            100000,
            ops,
        )

    def test_curve_sampler_enforces_registered_filters(self) -> None:
        for bits, seed in itertools.product((5, 6, 7, 8), (101, 211)):
            with self.subTest(bits=bits, seed=seed):
                ops = MODULE["OperationCounts"]()
                curve, points, record = MODULE["_generated_curve_for_controls"](
                    bits, seed, ops
                )
                self.assertEqual(len(points), record["q"])
                self.assertEqual(record["q"].bit_length(), bits)
                self.assertTrue(MODULE["is_prime"](record["q"]))
                self.assertNotIn(record["trace"], (0, 1))
                self.assertNotIn(record["j"], (0, 1728 % curve.p))
                self.assertTrue(all(curve.on_curve(point) for point in points))
                self.assertEqual(
                    MODULE["stable_digest"](record["rejected_draws"]),
                    record["rejection_digest"],
                )
                verified_curve = VERIFIER["verify_curve_provenance"](record)
                self.assertEqual(
                    (verified_curve.p, verified_curve.a, verified_curve.b),
                    (curve.p, curve.a, curve.b),
                )

    def test_v9_public_generated_construction_is_gated_before_row_math(self) -> None:
        producer_globals = MODULE["build_density_row"].__globals__
        original_generated_control = producer_globals["_generated_curve_for_controls"]
        original_factor_base = producer_globals["factor_base"]
        calls = []

        def forbidden_generated_control(*_args, **_kwargs):
            calls.append("generated_curve")
            raise AssertionError("public gate must precede generated-curve control")

        def forbidden_factor_base(*_args, **_kwargs):
            calls.append("factor_base")
            raise AssertionError("public gate must precede factor-base work")

        producer_globals["_generated_curve_for_controls"] = forbidden_generated_control
        try:
            with self.assertRaisesRegex(PermissionError, "public generated-curve"):
                MODULE["generated_curve"](5, 101)

            ops = MODULE["OperationCounts"]()
            curve, points, record = MODULE["frozen_curve"](ops)
            non_frozen_association = copy.deepcopy(record)
            non_frozen_association["draw"] = 0
            producer_globals["factor_base"] = forbidden_factor_base
            cases = (
                (points, non_frozen_association, 100000),
                (points[:-1] + [points[-2]], record, 100000),
                ([points[0], (False, 3), *points[2:]], record, 100000),
                (points, record, 100000.0),
            )
            for candidate_points, candidate_record, node_cap in cases:
                with self.subTest(node_cap=node_cap, record=candidate_record):
                    with self.assertRaisesRegex(
                        PermissionError, "density-row construction"
                    ):
                        MODULE["build_density_row"](
                            curve,
                            candidate_points,
                            candidate_record,
                            4,
                            "least_x_interval",
                            None,
                            node_cap,
                            ops,
                        )
        finally:
            producer_globals["_generated_curve_for_controls"] = original_generated_control
            producer_globals["factor_base"] = original_factor_base
        self.assertEqual(calls, [])

    def test_curve_rejection_transcript_records_duplicates_and_complete_reasons(
        self,
    ) -> None:
        fixtures = [
            ((17, 0, 0), "singular"),
            ((17, 0, 1), "trace_zero"),
            ((17, 1, 3), "anomalous_trace_one"),
            ((19, 0, 2), "j_zero"),
            ((17, 1, 0), "j_1728"),
        ]
        for (p, a, b), expected_reason in fixtures:
            with self.subTest(reason=expected_reason):
                reasons, _ = MODULE["curve_rejection_reasons"](p, a, b, 5)
                self.assertIn(expected_reason, reasons)
                for duplicate in (False, True):
                    produced = MODULE["ordered_curve_rejection_reasons"](
                        p, a, b, 5, duplicate
                    )
                    independently_reconstructed = VERIFIER[
                        "ordered_independent_rejection_reasons"
                    ](p, a, b, 5, duplicate)
                    self.assertEqual(produced, independently_reconstructed)
                    if duplicate:
                        self.assertEqual(produced[0][0], "duplicate_candidate")

        multi_reason = MODULE["ordered_curve_rejection_reasons"](
            5, 0, 1, 4, True
        )
        self.assertEqual(
            multi_reason,
            VERIFIER["ordered_independent_rejection_reasons"](
                5, 0, 1, 4, True
            ),
        )
        self.assertEqual(
            multi_reason[0],
            [
                "duplicate_candidate",
                "wrong_q_bit_length",
                "nonprime_group_order",
                "trace_zero",
                "j_zero",
            ],
        )

        generated_globals = MODULE["_generated_curve_for_controls"].__globals__
        original_hash = generated_globals["hash_int"]

        def scripted_hash(domain, fields, modulus, ops=None):
            draw = fields[2]
            if domain == "sgcp-002-curve-p":
                return 1
            if domain == "sgcp-002-curve-a":
                return (0, 0, 2)[draw] % modulus
            if domain == "sgcp-002-curve-b":
                return (0, 0, 9)[draw] % modulus
            raise AssertionError(domain)

        generated_globals["hash_int"] = scripted_hash
        try:
            _, _, record = MODULE["_generated_curve_for_controls"](5, 999)
        finally:
            generated_globals["hash_int"] = original_hash
        self.assertEqual(record["draw"], 2)
        self.assertEqual(record["rejected_draws"][0]["reasons"], ["singular"])
        self.assertEqual(
            record["rejected_draws"][1]["reasons"],
            ["duplicate_candidate", "singular"],
        )

    def test_generated_curve_provenance_mutation_is_rejected(self) -> None:
        ops = MODULE["OperationCounts"]()
        _, _, record = MODULE["_generated_curve_for_controls"](5, 101, ops)
        VERIFIER["verify_curve_provenance"](record)
        mutated = copy.deepcopy(record)
        mutated["rejection_digest"] = "0" * 64
        with self.assertRaises(AssertionError):
            VERIFIER["verify_curve_provenance"](mutated)

    def test_predicates_are_matched_and_deterministic(self) -> None:
        ops = MODULE["OperationCounts"]()
        curve, points, record = MODULE["_generated_curve_for_controls"](6, 101, ops)
        jobs = [
            ("least_x_interval", None),
            ("mobius_interval", None),
            ("two_mobius_union", None),
            ("hash_x_null", 0),
            ("hash_x_null", 1),
        ]
        for family, replicate in jobs:
            with self.subTest(family=family, replicate=replicate):
                factors, first = MODULE["factor_base"](
                    curve, points, record, 8, family, replicate, ops
                )
                repeated_factors, second = MODULE["factor_base"](
                    curve, points, record, 8, family, replicate, ops
                )
                self.assertEqual(factors, repeated_factors)
                self.assertEqual(first, second)
                self.assertEqual(len(factors), 8)
                self.assertEqual(first["selected_root_count"], 4)
                self.assertTrue(first["negation_symmetric"])
                for point in factors:
                    self.assertIn(curve.neg(point), factors)

    def test_predicate_replicate_rules_and_mobius_transcript_are_enforced(self) -> None:
        ops = MODULE["OperationCounts"]()
        curve, points, record = MODULE["frozen_curve"](ops)
        with self.assertRaises(ValueError):
            MODULE["factor_base"](
                curve, points, record, 4, "least_x_interval", 999, ops
            )
        with self.assertRaises(ValueError):
            MODULE["factor_base"](curve, points, record, 4, "hash_x_null", 4, ops)

        curve, points, record = MODULE["_generated_curve_for_controls"](6, 101, ops)
        _, factor_record = MODULE["factor_base"](
            curve, points, record, 4, "mobius_interval", None, ops
        )
        row = {
            "curve": record,
            "B": 4,
            "family": "mobius_interval",
            "null_replicate": None,
            "public_model": {"factor_base": factor_record},
        }
        verifier_curve = VERIFIER["Curve"](
            record["p"], record["a"], record["b"]
        )
        verifier_group = verifier_curve.points()
        VERIFIER["verify_factor_base"](verifier_curve, verifier_group, row)
        mutated = copy.deepcopy(row)
        mutated["public_model"]["factor_base"]["parameters"]["map"]["nonce"] += 1
        resign_factor_base(mutated)
        with self.assertRaisesRegex(
            AssertionError, "Mobius derivation transcript mismatch"
        ):
            VERIFIER["verify_factor_base"](
                verifier_curve, verifier_group, mutated
            )

        illegal = copy.deepcopy(self.frozen_density_row)
        illegal["null_replicate"] = 999
        illegal["public_model"]["factor_base"]["null_replicate"] = 999
        resign_factor_base(illegal)
        refresh_density_accounting(illegal)
        report = VERIFIER["_verify_density_row_for_tests"](
            illegal, 100000, "frozen_fixture"
        )
        self.assertFalse(report["valid"])
        self.assertTrue(
            any(
                "frozen row grid association mismatch" in error
                for error in report["errors"]
            )
        )

    def test_branch_and_bound_matches_exhaustive_graph_fixtures(self) -> None:
        fixtures = [
            [0, 0, 0, 0, 0],
            [0b11110, 0b11101, 0b11011, 0b10111, 0b01111],
            [0b00010, 0b00101, 0b01010, 0b10100, 0b01000],
            [0b10010, 0b00101, 0b01010, 0b10100, 0b01001],
        ]
        point_count = 11
        pair_outputs = [
            [((left + 1) * (right + 2) + left + right) % point_count for right in range(5)]
            for left in range(5)
        ]
        for conflicts in fixtures:
            for left in range(5):
                for right in range(5):
                    pair_outputs[right][left] = pair_outputs[left][right]
            with self.subTest(conflicts=conflicts):
                expected = exhaustive_graph(pair_outputs, conflicts)
                observed = MODULE["optimize_coverage_graph"](
                    pair_outputs, point_count, conflicts, 100000
                )
                self.assertTrue(observed["primary_exact"])
                self.assertTrue(observed["full_objective_exact"])
                self.assertEqual(
                    (
                        observed["retained_support_lower_bound"],
                        observed["selected_count"],
                    ),
                    expected,
                )

    def test_forced_cap_returns_interval_containing_exact_optimum(self) -> None:
        candidate_count = 9
        point_count = 17
        pair_outputs = [
            [((left + 3) * (right + 5) + left) % point_count for right in range(candidate_count)]
            for left in range(candidate_count)
        ]
        for left in range(candidate_count):
            for right in range(candidate_count):
                pair_outputs[right][left] = pair_outputs[left][right]
        conflicts = [0] * candidate_count
        for left, right in ((0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8)):
            conflicts[left] |= 1 << right
            conflicts[right] |= 1 << left
        optimum, _ = exhaustive_graph(pair_outputs, conflicts)
        capped = MODULE["optimize_coverage_graph"](
            pair_outputs, point_count, conflicts, 0
        )
        self.assertLessEqual(capped["retained_support_lower_bound"], optimum)
        self.assertGreaterEqual(capped["retained_support_upper_bound"], optimum)
        self.assertEqual(capped["termination_reason"], "node_cap")
        self.assertTrue(capped["frontier_states"])
        self.assertGreater(capped["absolute_gap"], 0)
        self.assertFalse(capped["primary_exact"])
        self.assertFalse(capped["full_objective_exact"])
        self.assertEqual(
            VERIFIER["verify_frontier_certificate"](
                pair_outputs, point_count, conflicts, capped
            ),
            [],
        )

    def test_frozen_fixture_reproduces_predecessor_optima(self) -> None:
        expected = {
            4: (31, 12, 20, 13, 5, 20, 26),
            6: (68, 8, 4, 7, 4, 17, 20),
            8: (124, 14, 53, 7, 4, 14, 21),
        }
        ops = MODULE["OperationCounts"]()
        curve, points, record = MODULE["frozen_curve"](ops)
        for B, values in expected.items():
            with self.subTest(B=B):
                row = MODULE["build_legacy_row"](
                    curve,
                    points,
                    record,
                    B,
                    "least_x_interval",
                    None,
                    200000,
                    ops,
                )
                graph = row["private_audit"]["graph"]
                optimizer = row["private_audit"]["optimizer"]
                self.assertEqual(
                    (
                        graph["candidate_count"],
                        graph["eligible_candidate_count"],
                        graph["conflict_count"],
                        optimizer["retained_support_lower_bound"],
                        optimizer["selected_count"],
                        optimizer["constrained_count"],
                        optimizer["public_edge_count"],
                    ),
                    values,
                )
                self.assertTrue(optimizer["primary_exact"])
                self.assertTrue(optimizer["full_objective_exact"])
                self.assertTrue(
                    all(
                        value
                        for key, value in row["public_model"]["axioms"].items()
                        if key not in {"associativity_method", "forbidden_final_edge_count"}
                    )
                )

    def test_pairwise_conflict_graph_matches_full_closure_on_frozen_B4(self) -> None:
        ops = MODULE["OperationCounts"]()
        curve, points, record = MODULE["frozen_curve"](ops)
        factors, _ = MODULE["factor_base"](
            curve, points, record, 4, "least_x_interval", None, ops
        )
        universe = MODULE["balanced_universe"](curve, factors)
        graph = MODULE["candidate_graph"](curve, factors, universe["candidates"])
        eligible = graph["eligible"]
        conflicts = graph["conflict_masks"]
        for mask in range(1 << len(eligible)):
            graph_feasible = not any(
                conflicts[index] & mask for index in MODULE["iter_mask"](mask)
            )
            maxima = [eligible[index]["formal"] for index in MODULE["iter_mask"](mask)]
            family = MODULE["order_ideal"](4, maxima)
            _, collisions = MODULE["evaluate_family"](curve, factors, family)
            self.assertEqual(graph_feasible, not collisions)

    def test_v9_legacy_direct_row_api_is_disabled_before_math(self) -> None:
        ops = MODULE["OperationCounts"]()
        curve, points, record = MODULE["frozen_curve"](ops)
        row = MODULE["build_legacy_row"](
            curve,
            points,
            record,
            4,
            "least_x_interval",
            None,
            100000,
            ops,
        )
        bad_digest = copy.deepcopy(row)
        bad_digest["row_sha256"] = "0" * 64
        huge_prime = copy.deepcopy(row)
        huge_prime["curve"]["p"] = 10**1000 + 7

        verifier_globals = VERIFIER["verify_row"].__globals__
        guarded = ("Curve", "reconstruct_graph", "independent_primary_optimum")
        originals = {name: verifier_globals[name] for name in guarded}
        calls = []

        def forbidden(name):
            def reject(*_args, **_kwargs):
                calls.append(name)
                raise AssertionError(f"legacy rejection must precede {name}")

            return reject

        for name in guarded:
            verifier_globals[name] = forbidden(name)
        try:
            for candidate in (row, bad_digest, huge_prime):
                report = VERIFIER["verify_row"](candidate, 100000)
                self.assertFalse(report["valid"])
                self.assertIn("legacy direct-row API is disabled", report["errors"][-1])
                self.assertEqual(report["primary_nodes"], 0)
            density_report = VERIFIER["verify_density_row"](
                self.frozen_density_row, 100000, "frozen_fixture"
            )
            self.assertFalse(density_report["valid"])
            self.assertIn(
                "direct density-row API is non-evidence and disabled",
                density_report["errors"][-1],
            )
            self.assertIsNone(density_report["resource_reservation"])
            self.assertEqual(density_report["primary_nodes"], 0)
        finally:
            verifier_globals.update(originals)
        self.assertEqual(calls, [])

    def test_density_objective_matches_exhaustive_caps(self) -> None:
        point_count = 13
        pair_outputs = [
            [((left + 2) * (right + 3) + left + right) % point_count for right in range(6)]
            for left in range(6)
        ]
        for left in range(6):
            for right in range(6):
                pair_outputs[right][left] = pair_outputs[left][right]
        conflicts = [0] * 6
        for left, right in ((0, 1), (1, 2), (2, 3), (3, 4), (4, 5)):
            conflicts[left] |= 1 << right
            conflicts[right] |= 1 << left
        weights = [2, 2, 3, 3, 4, 4]

        def metrics(mask: int) -> dict[str, object]:
            selected = list(MODULE["iter_mask"](mask))
            return {
                "constrained_count": 1 + sum(weights[index] for index in selected),
                "public_edge_count": sum(index + 1 for index in selected),
                "witness_list": selected,
            }

        for cap in (1, 5, 9, 17):
            with self.subTest(cap=cap):
                best_key = None
                best_witness = None
                for mask in range(1 << len(conflicts)):
                    if any(conflicts[index] & mask for index in MODULE["iter_mask"](mask)):
                        continue
                    row_metrics = metrics(mask)
                    if row_metrics["constrained_count"] > cap:
                        continue
                    support = MODULE["support_mask_for_selection"](
                        mask, pair_outputs
                    ).bit_count()
                    key = (
                        support,
                        -row_metrics["constrained_count"],
                        -row_metrics["public_edge_count"],
                        mask.bit_count(),
                    )
                    witness = tuple(row_metrics["witness_list"])
                    if best_key is None or key > best_key or (
                        key == best_key and witness < best_witness
                    ):
                        best_key = key
                        best_witness = witness
                observed = MODULE["optimize_coverage_graph"](
                    pair_outputs,
                    point_count,
                    conflicts,
                    100000,
                    metrics,
                    max_constrained=cap,
                    objective_mode="density",
                )
                self.assertTrue(observed["full_objective_exact"])
                self.assertEqual(
                    (
                        observed["retained_support_lower_bound"],
                        -observed["constrained_count"],
                        -observed["public_edge_count"],
                        observed["selected_count"],
                    ),
                    best_key,
                )
                self.assertEqual(tuple(observed["witness_list"]), best_witness)
                self.assertLessEqual(observed["constrained_count"], cap)

    def test_frozen_full_objective_matches_third_exhaustive_oracle(self) -> None:
        row = self.frozen_density_row
        curve = VERIFIER["verify_curve_provenance"](row["curve"])
        group = curve.points()
        factors = VERIFIER["verify_factor_base"](curve, group, row)
        eligible, conflicts, *_ = VERIFIER["reconstruct_graph"](curve, factors)

        candidates = []
        for mask in range(1 << len(conflicts)):
            selected_indices = list(VERIFIER["bits"](mask))
            if any(conflicts[index] & mask for index in selected_indices):
                continue
            maxima = [eligible[index]["formal"] for index in selected_indices]
            constrained, edge_count, _, _, _, _ = VERIFIER["retained_model"](
                curve, factors, maxima
            )
            selected_points = [eligible[index]["point"] for index in selected_indices]
            support = len(VERIFIER["support_counter"](curve, selected_points))
            witness = tuple(tuple(formal) for formal in sorted(maxima))
            objective = (
                support,
                -constrained,
                -edge_count,
                len(selected_indices),
            )
            candidates.append(
                (
                    constrained,
                    objective,
                    witness,
                    selected_indices,
                    edge_count,
                )
            )

        for public, private in zip(
            row["public_model"]["density_frontier"],
            row["private_audit"]["density_frontier"],
        ):
            cap = public["constrained_cap"]
            feasible = [candidate for candidate in candidates if candidate[0] <= cap]
            best_objective = max(candidate[1] for candidate in feasible)
            best_witness = min(
                candidate[2]
                for candidate in feasible
                if candidate[1] == best_objective
            )
            winner = next(
                candidate
                for candidate in feasible
                if candidate[1] == best_objective and candidate[2] == best_witness
            )
            optimizer = private["optimizer"]
            self.assertEqual(
                (
                    optimizer["retained_support_lower_bound"],
                    -optimizer["constrained_count"],
                    -optimizer["public_edge_count"],
                    optimizer["selected_count"],
                ),
                best_objective,
            )
            self.assertEqual(
                tuple(tuple(formal) for formal in optimizer["witness_list"]),
                best_witness,
            )
            self.assertEqual(optimizer["selected_indices"], winner[3])
            self.assertEqual(public["constrained_count"], winner[0])
            self.assertEqual(public["public_edge_count"], winner[4])

    def test_frozen_b4_matches_full_standalone_transcript(self) -> None:
        row = self.frozen_density_row
        oracle = standalone_frozen_b4_oracle()
        expected_factors = [
            tuple(point) for point in row["public_model"]["factor_base"]["points"]
        ]
        self.assertEqual(oracle["factors"], expected_factors)
        verifier_curve = VERIFIER["Curve"](19, 2, 9)
        reconstructed = VERIFIER["reconstruct_graph"](
            verifier_curve, expected_factors
        )
        self.assertEqual(oracle["candidates"], reconstructed[-1])
        self.assertEqual(oracle["eligible"], reconstructed[0])
        self.assertEqual(oracle["factor_base"], row["public_model"]["factor_base"])
        compiler = row["public_model"]["representative_compiler"]
        self.assertEqual(oracle["representative_compiler"], compiler)
        self.assertEqual(
            oracle["caps"], row["public_model"]["constrained_budget_caps"]
        )
        graph = row["private_audit"]["graph"]
        self.assertEqual(oracle["candidate_count"], graph["candidate_count"])
        self.assertEqual(oracle["eligible_count"], graph["eligible_candidate_count"])
        self.assertEqual(oracle["conflict_count"], graph["conflict_count"])
        self.assertEqual(
            {
                "candidate_count": oracle["candidate_count"],
                "eligible_candidate_count": oracle["eligible_count"],
                "individually_rejected_count": len(oracle["individually_rejected"]),
                "conflict_count": oracle["conflict_count"],
                **oracle["graph_metrics"],
            },
            graph,
        )
        self.assertEqual(
            oracle["eligible_universe_indices"],
            row["private_audit"]["eligible_universe_indices"],
        )
        self.assertEqual(
            oracle["individually_rejected"],
            row["private_audit"]["individually_rejected"],
        )
        self.assertEqual(oracle["conflicts"], row["private_audit"]["conflicts"])
        for public, private in zip(
            row["public_model"]["density_frontier"],
            row["private_audit"]["density_frontier"],
        ):
            winner = oracle["winners"][public["constrained_cap"]]
            optimizer = private["optimizer"]
            self.assertEqual(
                winner["objective"],
                (
                    optimizer["retained_support_lower_bound"],
                    -optimizer["constrained_count"],
                    -optimizer["public_edge_count"],
                    optimizer["selected_count"],
                ),
            )
            self.assertEqual(
                winner["witness"],
                tuple(tuple(formal) for formal in optimizer["witness_list"]),
            )
            self.assertEqual(winner["selected_indices"], optimizer["selected_indices"])
            self.assertEqual(winner["selected_mask_hex"], optimizer["selected_mask_hex"])
            self.assertEqual(winner["constrained_count"], public["constrained_count"])
            self.assertEqual(
                winner["formal_family_count"], public["formal_family_count"]
            )
            self.assertEqual(
                winner["formal_degree_histogram"], public["formal_degree_histogram"]
            )
            self.assertEqual(winner["delta"], public["delta"])
            self.assertEqual(winner["axioms"], public["axioms"])
            self.assertEqual(winner["public_edge_count"], public["public_edge_count"])
            self.assertEqual(winner["public_edges"], public["public_edges"])
            self.assertEqual(
                winner["public_edges_sha256"], public["public_edges_sha256"]
            )
            self.assertEqual(winner["source_table"], public["source_table"])
            self.assertEqual(
                winner["source_table_sha256"], public["source_table_sha256"]
            )
            self.assertEqual(
                winner["constrained_labels"],
                [entry["label"] for entry in public["source_table"]],
            )

    def test_corrected_energy_matches_ordered_and_multiset_recounts(self) -> None:
        ops = MODULE["OperationCounts"]()
        curve, points, record = MODULE["frozen_curve"](ops)
        factors, _ = MODULE["factor_base"](
            curve, points, record, 4, "least_x_interval", None, ops
        )
        observed = MODULE["degree_expansion"](curve, factors, (2,))["2"]
        formal_counts = {}
        for formal in itertools.combinations_with_replacement(range(4), 2):
            point = MODULE["evaluate_formal"](curve, factors, formal)
            formal_counts[point] = formal_counts.get(point, 0) + 1
        ordered_counts = {}
        for ordered in itertools.product(range(4), repeat=2):
            point = MODULE["evaluate_formal"](curve, factors, ordered)
            ordered_counts[point] = ordered_counts.get(point, 0) + 1
        self.assertEqual(observed["formal_multiset_witness_count"], 10)
        self.assertEqual(observed["ordered_tuple_witness_count"], 16)
        self.assertEqual(
            observed["formal_multiset_collision_energy"],
            sum(value * value for value in formal_counts.values()),
        )
        self.assertEqual(
            observed["ordered_tuple_additive_energy"],
            sum(value * value for value in ordered_counts.values()),
        )
        all_degrees = MODULE["degree_expansion"](curve, factors)
        self.assertEqual(
            all_degrees,
            VERIFIER["expansion_metrics"](
                VERIFIER["Curve"](curve.p, curve.a, curve.b),
                factors,
            ),
        )
        for degree in (1, 2, 4, 8):
            with self.subTest(degree=degree):
                metrics = all_degrees[str(degree)]
                self.assertEqual(
                    metrics["formal_multiset_witness_count"],
                    math.comb(len(factors) + degree - 1, degree),
                )
                self.assertEqual(
                    metrics["ordered_tuple_witness_count"], len(factors) ** degree
                )

    def test_density_gap_frontier_replays_from_root(self) -> None:
        point_count = 19
        candidate_count = 8
        pair_outputs = [
            [((left + 5) * (right + 7) + right) % point_count for right in range(candidate_count)]
            for left in range(candidate_count)
        ]
        for left in range(candidate_count):
            for right in range(candidate_count):
                pair_outputs[right][left] = pair_outputs[left][right]
        conflicts = [0] * candidate_count
        for left, right in ((0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7)):
            conflicts[left] |= 1 << right
            conflicts[right] |= 1 << left

        def metrics(mask: int) -> dict[str, object]:
            selected = list(MODULE["iter_mask"](mask))
            return {
                "constrained_count": 1 + 2 * len(selected),
                "public_edge_count": sum(selected),
                "witness_list": selected,
            }

        producer = MODULE["optimize_coverage_graph"](
            pair_outputs,
            point_count,
            conflicts,
            0,
            metrics,
            max_constrained=9,
            objective_mode="density",
        )
        replay = VERIFIER["replay_density_search"](
            pair_outputs, point_count, conflicts, 0, 9, metrics
        )
        self.assertTrue(producer["frontier_states"])
        for key in replay:
            if key == "metric_cache_entries":
                continue
            self.assertEqual(replay[key], producer[key], key)
        self.assertEqual(
            VERIFIER["verify_frontier_certificate"](
                pair_outputs, point_count, conflicts, producer
            ),
            [],
        )

    def test_frozen_density_frontier_is_exact_and_within_every_cap(self) -> None:
        row = self.frozen_density_row
        self.assertEqual(row["public_model"]["constrained_budget_caps"], [5, 11, 17, 23])
        for public, private in zip(
            row["public_model"]["density_frontier"],
            row["private_audit"]["density_frontier"],
        ):
            self.assertEqual(public["constrained_cap"], private["constrained_cap"])
            self.assertLessEqual(public["constrained_count"], public["constrained_cap"])
            self.assertTrue(private["optimizer"]["primary_exact"])
            self.assertTrue(private["optimizer"]["full_objective_exact"])
            self.assertEqual(private["optimizer"]["frontier_states"], [])
            cache_limit = (
                private["optimizer"]["node_cap"]
                + row["private_audit"]["graph"]["eligible_candidate_count"] ** 2
                + 64
            )
            self.assertLessEqual(
                private["optimizer"]["metric_cache_entries"], cache_limit
            )
            self.assertEqual(
                private["structural_work"]["optimizer_metric_cache_entries"],
                private["optimizer"]["metric_cache_entries"],
            )
            self.assertEqual(
                private["structural_work"]["full_model_cache_entries"],
                private["optimizer"]["metric_cache_entries"],
            )
            self.assertEqual(
                private["retention"]["eight_fold_support"],
                row["private_audit"]["expansion"]["8"]["support"],
            )
        verification = VERIFIER["_verify_density_row_for_tests"](
            row, 100000, "frozen_fixture"
        )
        self.assertTrue(verification["valid"], verification["errors"])
        self.assertEqual(len(verification["cap_reports"]), 4)
        self.assertEqual(
            verification["actual_work"]["replay_nodes"],
            verification["replay_nodes"],
        )
        self.assertEqual(
            verification["actual_work"]["independent_primary_nodes"],
            verification["primary_nodes"],
        )
        self.assertGreater(
            verification["actual_work"]["primary_support_cache_entries"], 0
        )
        self.assertNotIn("operation_counts", row)
        self.assertEqual(
            row["structural_work"]["degree_multiset_evaluations"],
            sum(
                row["private_audit"]["expansion"][str(degree)][
                    "formal_multiset_witness_count"
                ]
                for degree in (1, 2, 4, 8)
            ),
        )

        mutated = copy.deepcopy(row)
        mutated["accounting"]["public_model_json_bytes"] += 1
        resign_density_row(mutated)
        mutation_report = VERIFIER["_verify_density_row_for_tests"](
            mutated, 100000, "frozen_fixture"
        )
        self.assertFalse(mutation_report["valid"])
        self.assertTrue(
            any(
                "cost-accounting byte receipt mismatch" in error
                for error in mutation_report["errors"]
            )
        )

        mutated = copy.deepcopy(row)
        mutated["structural_work"]["pair_output_cells"] += 1
        refresh_density_accounting(mutated)
        mutation_report = VERIFIER["_verify_density_row_for_tests"](
            mutated, 100000, "frozen_fixture"
        )
        self.assertFalse(mutation_report["valid"])
        self.assertIn("row structural-work receipt mismatch", mutation_report["errors"])

    def test_closed_schema_rejects_scalar_material_and_nested_graph_extras(self) -> None:
        scalar = copy.deepcopy(self.frozen_density_row)
        scalar["scalar_table"] = []
        refresh_density_accounting(scalar)
        report = VERIFIER["_verify_density_row_for_tests"](
            scalar, 100000, "frozen_fixture"
        )
        self.assertFalse(report["valid"])
        self.assertTrue(
            any("more keys than the V9 source schema" in error for error in report["errors"])
        )

        nested = copy.deepcopy(self.frozen_density_row)
        nested["private_audit"]["individually_rejected"][0]["note"] = "extra"
        refresh_density_accounting(nested)
        report = VERIFIER["_verify_density_row_for_tests"](
            nested, 100000, "frozen_fixture"
        )
        self.assertFalse(report["valid"])
        self.assertTrue(
            any(
                "individual rejection[0] has more keys than the V9 source schema"
                in error
                for error in report["errors"]
            )
        )

    def test_semantic_mutations_are_rejected_after_receipts_are_refreshed(self) -> None:
        representative = copy.deepcopy(self.frozen_density_row)
        compiler = representative["public_model"]["representative_compiler"]
        compiler["representatives"][0]["formal"] = [3, 3]
        compiler["representatives_sha256"] = VERIFIER["digest"](
            compiler["representatives"]
        )
        refresh_density_accounting(representative)
        report = VERIFIER["_verify_density_row_for_tests"](
            representative, 100000, "frozen_fixture"
        )
        self.assertFalse(report["valid"])
        self.assertIn("representative compiler mismatch", report["errors"])

        objective = copy.deepcopy(self.frozen_density_row)
        objective["private_audit"]["density_frontier"][0]["optimizer"][
            "objective_order"
        ][0:2] = ["constrained_count:min", "retained_support:max"]
        refresh_density_accounting(objective)
        report = VERIFIER["_verify_density_row_for_tests"](
            objective, 100000, "frozen_fixture"
        )
        self.assertFalse(report["valid"])
        self.assertTrue(
            any("optimizer objective-order mismatch" in error for error in report["errors"])
        )

        source = copy.deepcopy(self.frozen_density_row)
        source_cap = source["public_model"]["density_frontier"][0]
        source_cap["source_table"][0]["formal"] = [0]
        source_cap["source_table_sha256"] = VERIFIER["digest"](
            source_cap["source_table"]
        )
        refresh_density_accounting(source)
        report = VERIFIER["_verify_density_row_for_tests"](
            source, 100000, "frozen_fixture"
        )
        self.assertFalse(report["valid"])
        self.assertTrue(
            any("public source table/digest mismatch" in error for error in report["errors"])
        )

        unresolved = copy.deepcopy(self.frozen_density_row)
        optimizer = unresolved["private_audit"]["density_frontier"][0]["optimizer"]
        optimizer["primary_exact"] = False
        optimizer["retained_support_upper_bound"] += 1
        optimizer["absolute_gap"] = 1
        refresh_density_accounting(unresolved)
        report = VERIFIER["_verify_density_row_for_tests"](
            unresolved, 100000, "frozen_fixture"
        )
        self.assertFalse(report["valid"])
        self.assertTrue(
            any(
                "optimizer exactness" in error
                for error in report["errors"]
            )
        )

    def test_v9_exact_types_reject_json_equality_aliases(self) -> None:
        mutations = (
            (
                "zero_to_false",
                ("private_audit", "density_frontier", 0, "optimizer", "absolute_gap"),
                False,
            ),
            (
                "zero_to_negative_float_zero",
                (
                    "private_audit",
                    "density_frontier",
                    0,
                    "optimizer",
                    "remaining_frontier_nodes",
                ),
                -0.0,
            ),
            (
                "integer_count_to_float",
                ("private_audit", "graph", "candidate_count"),
                float(self.frozen_density_row["private_audit"]["graph"]["candidate_count"]),
            ),
            (
                "boolean_to_integer",
                ("public_model", "density_frontier", 0, "axioms", "identity"),
                1,
            ),
            (
                "ratio_integer_to_float",
                ("public_model", "density_frontier", 0, "delta", "numerator"),
                float(
                    self.frozen_density_row["public_model"]["density_frontier"][0][
                        "delta"
                    ]["numerator"]
                ),
            ),
            (
                "node_cap_to_float",
                ("private_audit", "density_frontier", 0, "optimizer", "node_cap"),
                100000.0,
            ),
            ("wall_time_to_integer", ("wall_time_seconds",), 0),
            (
                "mask_to_integer",
                (
                    "private_audit",
                    "density_frontier",
                    0,
                    "optimizer",
                    "selected_mask_hex",
                ),
                0,
            ),
        )
        for label, path, replacement in mutations:
            with self.subTest(label=label):
                mutated = copy.deepcopy(self.frozen_density_row)
                target = mutated
                for component in path[:-1]:
                    target = target[component]
                target[path[-1]] = replacement
                refresh_density_accounting(mutated)
                report = VERIFIER["_verify_density_row_for_tests"](
                    mutated, 100000, "frozen_fixture"
                )
                self.assertFalse(report["valid"])
                self.assertTrue(
                    any("exact type mismatch" in error for error in report["errors"]),
                    report["errors"],
                )

        receipt = copy.deepcopy(self.frozen_density_row)
        byte_receipt = receipt["accounting"]["nested_per_cap_json_bytes"][0]
        byte_receipt["public_embedding_json_bytes"] = float(
            byte_receipt["public_embedding_json_bytes"]
        )
        resign_density_row(receipt)
        report = VERIFIER["_verify_density_row_for_tests"](
            receipt, 100000, "frozen_fixture"
        )
        self.assertFalse(report["valid"])
        self.assertTrue(
            any("exact type mismatch" in error for error in report["errors"]),
            report["errors"],
        )

    def test_v9_type_checker_rejects_every_frozen_scalar_type_substitution(self) -> None:
        scalar_paths = []

        def visit(value, path=()):
            if isinstance(value, dict):
                for key, child in value.items():
                    visit(child, path + (key,))
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    visit(child, path + (index,))
            else:
                scalar_paths.append(path)

        visit(self.frozen_density_row)
        checked = 0
        for path in scalar_paths:
            mutated = copy.deepcopy(self.frozen_density_row)
            target = mutated
            for component in path[:-1]:
                target = target[component]
            original = target[path[-1]]
            if type(original) is bool:
                replacement = int(original)
            elif type(original) is int:
                replacement = float(original)
            elif type(original) is float:
                replacement = int(original)
            elif type(original) is str:
                replacement = 0
            elif original is None:
                replacement = False
            else:
                continue
            target[path[-1]] = replacement
            errors = VERIFIER["v9_row_type_errors"](mutated)
            self.assertTrue(errors, path)
            checked += 1
        self.assertGreater(checked, 1000)

    def test_v9_preflight_returns_invalid_receipts_for_red_team_crash_cases(self) -> None:
        mutations = []

        truncated_caps = copy.deepcopy(self.frozen_density_row)
        truncated_caps["public_model"]["constrained_budget_caps"].pop()
        refresh_density_accounting(truncated_caps)
        mutations.append(("truncated_caps", truncated_caps, "must contain exactly 4"))

        invalid_formal = copy.deepcopy(self.frozen_density_row)
        invalid_formal["public_model"]["density_frontier"][0]["selected_maxima"] = [
            [999]
        ]
        refresh_density_accounting(invalid_formal)
        mutations.append(("invalid_formal", invalid_formal, "must contain exactly 4"))

        duplicate_formal = copy.deepcopy(self.frozen_density_row)
        duplicate_cell = next(
            cell
            for cell in duplicate_formal["public_model"]["density_frontier"]
            if cell["selected_maxima"]
        )
        duplicate_cell["selected_maxima"].append(
            copy.deepcopy(duplicate_cell["selected_maxima"][0])
        )
        refresh_density_accounting(duplicate_formal)
        mutations.append(("duplicate_formal", duplicate_formal, "not unique"))

        negative_cap = copy.deepcopy(self.frozen_density_row)
        negative_cap["public_model"]["constrained_budget_caps"][0] = -1
        negative_cap["public_model"]["density_frontier"][0]["constrained_cap"] = -1
        negative_cap["private_audit"]["density_frontier"][0]["constrained_cap"] = -1
        negative_cap["private_audit"]["density_frontier"][0]["optimizer"][
            "max_constrained"
        ] = -1
        refresh_density_accounting(negative_cap)
        mutations.append(("negative_cap", negative_cap, "outside 1..q"))

        for label, mutated, expected in mutations:
            with self.subTest(label=label):
                first = VERIFIER["_verify_density_row_for_tests"](
                    mutated, 100000, "frozen_fixture"
                )
                second = VERIFIER["_verify_density_row_for_tests"](
                    mutated, 100000, "frozen_fixture"
                )
                self.assertFalse(first["valid"])
                self.assertEqual(first, second)
                self.assertEqual(first["primary_nodes"], 0)
                self.assertTrue(
                    any(expected in error for error in first["errors"]), first["errors"]
                )
                self.assertFalse(
                    any("verifier failure" in error for error in first["errors"]),
                    first["errors"],
                )
                document = MODULE["build_document"](
                    [self.frozen_density_row],
                    "frozen_fixture",
                    MODULE["frozen_parameters"](100000),
                )
                document["rows"] = [mutated]
                resign_document(document)
                document_errors, document_reports = VERIFIER[
                    "_verify_v9_document_value_for_tests"
                ](document, 100000)
                self.assertTrue(document_errors)
                self.assertEqual(document_reports, [])
                self.assertTrue(
                    any(expected in error for error in document_errors),
                    document_errors,
                )

    def test_v9_verifier_entrypoints_are_total_with_explicit_ceilings(self) -> None:
        missing_scope = VERIFIER["_verify_density_row_for_tests"](
            self.frozen_density_row, 100000
        )
        self.assertFalse(missing_scope["valid"])
        self.assertIn(
            "density row scope must be explicitly registered",
            missing_scope["errors"],
        )

        bad_digest = copy.deepcopy(self.frozen_density_row)
        bad_digest["row_sha256"] = "0" * 64
        verifier_globals = VERIFIER["_verify_density_row_for_tests"].__globals__
        original_curve_verifier = verifier_globals["verify_curve_provenance"]
        original_frozen_curve = verifier_globals["frozen_curve_record"]
        original_registered_curve = verifier_globals["registered_curve_bundle"]
        curve_calls = []

        def forbidden_curve_verifier(_):
            curve_calls.append("provenance")
            raise AssertionError("digest failure must precede curve work")

        def forbidden_frozen_curve():
            curve_calls.append("frozen")
            raise AssertionError("digest failure must precede frozen curve work")

        def forbidden_registered_curve(*_args):
            curve_calls.append("registered")
            raise AssertionError("digest failure must precede registered curve work")

        verifier_globals["verify_curve_provenance"] = forbidden_curve_verifier
        verifier_globals["frozen_curve_record"] = forbidden_frozen_curve
        verifier_globals["registered_curve_bundle"] = forbidden_registered_curve
        try:
            digest_report = VERIFIER["_verify_density_row_for_tests"](
                bad_digest, 100000, "frozen_fixture"
            )
        finally:
            verifier_globals["verify_curve_provenance"] = original_curve_verifier
            verifier_globals["frozen_curve_record"] = original_frozen_curve
            verifier_globals["registered_curve_bundle"] = original_registered_curve
        self.assertFalse(digest_report["valid"])
        self.assertTrue(
            any("row digest mismatch" in error for error in digest_report["errors"])
        )
        self.assertEqual(curve_calls, [])

        for maximum_nodes in (False, -1, VERIFIER["MAXIMUM_PRIMARY_NODES"] + 1):
            with self.subTest(maximum_nodes=maximum_nodes):
                row_report = VERIFIER["_verify_density_row_for_tests"](
                    self.frozen_density_row, maximum_nodes, "frozen_fixture"
                )
                self.assertFalse(row_report["valid"])
                document = MODULE["build_document"](
                    [self.frozen_density_row],
                    "frozen_fixture",
                    MODULE["frozen_parameters"](100000),
                )
                errors, reports = VERIFIER["_verify_v9_document_value_for_tests"](
                    document, maximum_nodes
                )
                self.assertTrue(errors)
                self.assertEqual(reports, [])

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            malformed = root / "malformed.json"
            malformed.write_text('{"schema":', encoding="ascii")
            report = VERIFIER["verify_document"](malformed, 100000)
            self.assertFalse(report["valid"])
            self.assertTrue(
                any("strict JSON parse failure" in error for error in report["errors"])
            )

            non_object = root / "non-object.json"
            non_object.write_text("[]", encoding="ascii")
            report = VERIFIER["verify_document"](non_object, 100000)
            self.assertFalse(report["valid"])
            self.assertIn("input document is not an object", report["errors"])

            duplicate = root / "duplicate.json"
            duplicate.write_text('{"schema":"x","schema":"y"}', encoding="ascii")
            report = VERIFIER["verify_document"](duplicate, 100000)
            self.assertFalse(report["valid"])
            self.assertTrue(any("duplicate key" in error for error in report["errors"]))

    def test_v9_overlong_reflected_path_returns_bounded_invalid_report(self) -> None:
        path = Path("x" * (VERIFIER["MAXIMUM_VERIFICATION_REPORT_BYTES"] + 1))
        report = VERIFIER["verify_document"](path, False)
        self.assertFalse(report["valid"])
        self.assertTrue(report["input_path"].startswith("<input path omitted:"))
        self.assertLessEqual(
            len(VERIFIER["stable_bytes"](report)),
            VERIFIER["MAXIMUM_VERIFICATION_REPORT_BYTES"],
        )

    def test_v9_snapshot_hash_and_parse_are_bound_to_the_same_bytes(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        original_bytes = VERIFIER["stable_bytes"](document)
        verifier_globals = VERIFIER["verify_document"].__globals__
        original_snapshot = verifier_globals["read_input_snapshot"]

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "changing.json"
            path.write_bytes(original_bytes)

            def snapshot_then_change(snapshot_path):
                raw, receipt = original_snapshot(snapshot_path)
                snapshot_path.write_bytes(b'{"schema":"changed-after-snapshot"}')
                return raw, receipt

            verifier_globals["read_input_snapshot"] = snapshot_then_change
            try:
                report = VERIFIER["verify_document"](path, 100000)
            finally:
                verifier_globals["read_input_snapshot"] = original_snapshot

            self.assertTrue(report["valid"], report["errors"])
            self.assertEqual(
                report["input_file_sha256"], hashlib.sha256(original_bytes).hexdigest()
            )
            self.assertNotEqual(
                report["input_file_sha256"], hashlib.sha256(path.read_bytes()).hexdigest()
            )
            self.assertEqual(report["input_document_sha256"], document["document_sha256"])

    def test_v9_source_hash_is_diagnostic_and_not_reopened_for_reporting(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        verifier_globals = VERIFIER["verify_document"].__globals__
        original_file_digest = verifier_globals["file_digest"]

        def forbidden_file_digest(_path):
            raise AssertionError("reporting must not reopen the verifier source")

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            path.write_bytes(VERIFIER["stable_bytes"](document))
            verifier_globals["file_digest"] = forbidden_file_digest
            try:
                report = VERIFIER["verify_document"](path, 100000)
            finally:
                verifier_globals["file_digest"] = original_file_digest
        self.assertTrue(report["valid"], report["errors"])
        self.assertEqual(
            report["verifier_source_sha256"],
            VERIFIER["VERIFIER_SOURCE_DIAGNOSTIC_SHA256"],
        )
        self.assertFalse(report["verifier_source_attested"])
        self.assertIn("not executed-code attestation", report["verifier_source_hash_scope"])
        self.assertIn("parent path components", report["input_symlink_policy"])

    def test_v9_diagnostics_are_count_and_byte_bounded(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        for index in range(1000):
            document[f"secret_{index:04d}"] = "x" * 4096
        resign_document(document)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "amplified.json"
            path.write_bytes(VERIFIER["stable_bytes"](document))
            report = VERIFIER["verify_document"](path, 100000)
        observed = report["diagnostic_observed"]
        limits = report["diagnostic_limits"]
        self.assertFalse(report["valid"])
        self.assertLessEqual(observed["count"], limits["maximum_count"])
        self.assertLessEqual(observed["bytes"], limits["maximum_bytes"])
        self.assertFalse(observed["truncated"])
        self.assertTrue(
            all(
                len(error.encode("ascii")) <= limits["maximum_item_bytes"]
                for error in report["errors"]
            )
        )
        report_bytes = VERIFIER["stable_bytes"](report)
        self.assertLessEqual(
            len(report_bytes), VERIFIER["MAXIMUM_VERIFICATION_REPORT_BYTES"]
        )
        self.assertNotIn(b"secret_", report_bytes)

    def test_v9_reflected_document_digest_is_sanitized_before_reporting(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        document["document_sha256"] = {"secret": "not-a-digest"}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid-digest.json"
            path.write_bytes(VERIFIER["stable_bytes"](document))
            report = VERIFIER["verify_document"](path, 100000)
        self.assertFalse(report["valid"])
        self.assertIsNone(report["input_document_sha256"])
        self.assertEqual(
            report["phases"][-1],
            {"name": "source_collection_bounds", "status": "failed"},
        )
        self.assertNotIn(b"secret", VERIFIER["stable_bytes"](report))

    def test_v9_serialized_report_ceiling_covers_integrity_fields(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        verifier_globals = VERIFIER["verify_document"].__globals__
        original_limit = verifier_globals["MAXIMUM_VERIFICATION_REPORT_BYTES"]
        verifier_globals["MAXIMUM_VERIFICATION_REPORT_BYTES"] = 5050
        try:
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "bounded-report.json"
                path.write_bytes(VERIFIER["stable_bytes"](document))
                report = VERIFIER["verify_document"](path, 100000)
        finally:
            verifier_globals["MAXIMUM_VERIFICATION_REPORT_BYTES"] = original_limit

        self.assertFalse(report["valid"])
        self.assertEqual(report["rows"], [])
        self.assertLessEqual(len(VERIFIER["stable_bytes"](report)), 5050)
        signed_payload = dict(report)
        supplied_hash = signed_payload.pop("verification_sha256")
        self.assertEqual(supplied_hash, VERIFIER["digest"](signed_payload))
        pre_integrity_payload = dict(signed_payload)
        supplied_size = pre_integrity_payload.pop(
            "serialized_report_bytes_before_size_field_and_hash"
        )
        self.assertEqual(supplied_size, len(VERIFIER["stable_bytes"](pre_integrity_payload)))

    def test_v9_source_collection_bounds_precede_generic_traversal(self) -> None:
        baseline = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        mutations = []

        polynomial = copy.deepcopy(baseline)
        polynomial["rows"][0]["public_model"]["factor_base"][
            "root_polynomial_coefficients_ascending_mod_p"
        ].append(0)
        mutations.append((polynomial, "factor root polynomial must contain exactly 3"))

        maps = copy.deepcopy(baseline)
        maps["rows"][0]["family"] = "two_mobius_union"
        maps["rows"][0]["public_model"]["factor_base"]["parameters"] = {
            "maps": [{}, {}, {}],
            "alternating_positions": [0, 1],
        }
        mutations.append((maps, "two-Mobius maps must contain exactly 2"))

        alternating = copy.deepcopy(baseline)
        alternating["rows"][0]["family"] = "two_mobius_union"
        alternating["rows"][0]["public_model"]["factor_base"]["parameters"] = {
            "maps": [{}, {}],
            "alternating_positions": [0, 1, 2],
        }
        mutations.append(
            (
                alternating,
                "two-Mobius alternating positions must contain exactly 2",
            )
        )

        reasons = copy.deepcopy(baseline)
        reasons["rows"][0]["curve"]["rejected_draws"] = [
            {
                "draw": 0,
                "p": 5,
                "a": 0,
                "b": 1,
                "reasons": list(VERIFIER["REJECTION_REASON_ORDER"]) + ["extra"],
            }
        ]
        mutations.append(
            (reasons, "curve rejection[0] reasons exceeds its source-derived length bound")
        )

        accounting = copy.deepcopy(baseline)
        accounting["rows"][0]["accounting"]["nested_per_cap_json_bytes"].append(
            copy.deepcopy(
                accounting["rows"][0]["accounting"]["nested_per_cap_json_bytes"][0]
            )
        )
        mutations.append(
            (accounting, "nested per-cap byte receipts must contain exactly 4")
        )

        nested_dictionary = copy.deepcopy(baseline)
        nested_dictionary["rows"][0]["public_model"]["factor_base"].update(
            {f"extra_{index}": index for index in range(1000)}
        )
        mutations.append(
            (
                nested_dictionary,
                "factor-base record has more keys than the V9 source schema",
            )
        )

        invalid_B = copy.deepcopy(baseline)
        invalid_B["rows"][0]["B"] = 3
        invalid_B["rows"][0]["private_audit"]["expansion"] = {
            "nested": [[0] * 1000]
        }
        mutations.append((invalid_B, "row.B is outside the V9 source range"))

        canonical_gate = copy.deepcopy(baseline)
        canonical_gate["scope"] = "canonical"
        canonical_gate["canonical"] = True
        canonical_gate["parameters"] = VERIFIER["expected_canonical_parameters"]()
        canonical_gate["family_gate"] = VERIFIER["independent_family_gate"](
            synthetic_gate_rows()
        )
        canonical_gate["family_gate"]["families"][0]["matched_null_cap_tests"][0][
            "strata"
        ].append(
            copy.deepcopy(
                canonical_gate["family_gate"]["families"][0][
                    "matched_null_cap_tests"
                ][0]["strata"][0]
            )
        )
        mutations.append(
            (
                canonical_gate,
                "family gate[0].matched_null_cap_tests[0].strata must contain exactly 4",
            )
        )

        verifier_globals = VERIFIER["verify_document"].__globals__
        originals = {
            name: verifier_globals[name]
            for name in ("bounded_json_errors", "_verify_v9_document_value_unchecked")
        }
        calls = []

        def forbidden(name):
            def reject(*_args, **_kwargs):
                calls.append(name)
                raise AssertionError(f"collection rejection must precede {name}")

            return reject

        for name in originals:
            verifier_globals[name] = forbidden(name)
        try:
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "bounded.json"
                for document, expected in mutations:
                    with self.subTest(expected=expected):
                        path.write_bytes(VERIFIER["stable_bytes"](document))
                        report = VERIFIER["verify_document"](path, 100000)
                        self.assertFalse(report["valid"])
                        self.assertTrue(
                            any(expected in error for error in report["errors"]),
                            report["errors"],
                        )
                        self.assertEqual(
                            report["phases"][-1],
                            {"name": "source_collection_bounds", "status": "failed"},
                        )
        finally:
            verifier_globals.update(originals)
        self.assertEqual(calls, [])

    def test_v9_rejects_nonregular_and_symlink_inputs_before_parsing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            regular = root / "regular.json"
            regular.write_text("{}", encoding="ascii")
            symlink = root / "link.json"
            symlink.symlink_to(regular)
            fifo = root / "input.fifo"
            os.mkfifo(fifo)
            for path in (root, symlink, fifo):
                with self.subTest(path=path.name):
                    report = VERIFIER["verify_document"](path, 100000)
                    self.assertFalse(report["valid"])
                    self.assertEqual(
                        report["phases"],
                        [
                            {"name": "verifier_budget_preflight", "status": "passed"},
                            {"name": "single_regular_file_snapshot", "status": "failed"},
                        ],
                    )
                    self.assertEqual(
                        report["independent_checks"], ["verifier_budget_preflight"]
                    )

            oversized = root / "oversized.json"
            oversized.touch()
            os.truncate(oversized, VERIFIER["MAXIMUM_INPUT_BYTES"] + 1)
            snapshot_globals = VERIFIER["read_input_snapshot"].__globals__
            original_read = snapshot_globals["os"].read
            read_calls = 0

            def forbidden_read(*_args, **_kwargs):
                nonlocal read_calls
                read_calls += 1
                raise AssertionError("oversized input must be rejected before reading")

            snapshot_globals["os"].read = forbidden_read
            try:
                with self.assertRaisesRegex(ValueError, "input byte ceiling exceeded"):
                    VERIFIER["read_input_snapshot"](oversized)
            finally:
                snapshot_globals["os"].read = original_read
            self.assertEqual(read_calls, 0)

            real_parent = root / "real-parent"
            real_parent.mkdir()
            parent_target = real_parent / "input.json"
            parent_target.write_text("{}", encoding="ascii")
            linked_parent = root / "linked-parent"
            linked_parent.symlink_to(real_parent, target_is_directory=True)
            raw, _ = VERIFIER["read_input_snapshot"](
                linked_parent / "input.json"
            )
            self.assertEqual(raw, b"{}")

    def test_v9_registered_preflight_blocks_huge_bits_and_row_amplification(self) -> None:
        mutated = copy.deepcopy(self.frozen_density_row)
        mutated["curve"]["bits"] = 40
        refresh_density_accounting(mutated)

        verifier_globals = VERIFIER["_verify_density_row_for_tests"].__globals__
        original_curve_verifier = verifier_globals["verify_curve_provenance"]
        curve_calls = 0

        def forbidden_curve_verifier(_):
            nonlocal curve_calls
            curve_calls += 1
            raise AssertionError("semantic curve verification must not run")

        verifier_globals["verify_curve_provenance"] = forbidden_curve_verifier
        try:
            row_report = VERIFIER["_verify_density_row_for_tests"](
                mutated, 100000, "frozen_fixture"
            )
        finally:
            verifier_globals["verify_curve_provenance"] = original_curve_verifier
        self.assertFalse(row_report["valid"])
        self.assertEqual(curve_calls, 0)
        self.assertEqual(row_report["primary_nodes"], 0)
        self.assertTrue(
            any("registered fixture" in error for error in row_report["errors"])
        )

        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        document["rows"] = [mutated]
        resign_document(document)
        document_globals = VERIFIER["_verify_v9_document_value_for_tests"].__globals__
        original_row_verifier = document_globals["_verify_density_row_unchecked"]
        row_calls = 0

        def forbidden_row_verifier(*_args, **_kwargs):
            nonlocal row_calls
            row_calls += 1
            raise AssertionError("row semantics must not run")

        document_globals["_verify_density_row_unchecked"] = forbidden_row_verifier
        try:
            errors, reports = VERIFIER["_verify_v9_document_value_for_tests"](document, 100000)
            amplified = copy.deepcopy(document)
            amplified["rows"] = [copy.deepcopy(mutated) for _ in range(12)]
            resign_document(amplified)
            amplified_errors, amplified_reports = VERIFIER[
                "_verify_v9_document_value_for_tests"
            ](amplified, 100000)
        finally:
            document_globals["_verify_density_row_unchecked"] = original_row_verifier
        self.assertTrue(errors)
        self.assertEqual(reports, [])
        self.assertTrue(amplified_errors)
        self.assertEqual(amplified_reports, [])
        self.assertEqual(row_calls, 0)

    def test_v9_static_optimizer_admission_precedes_curve_and_solver_work(self) -> None:
        mutations = []

        wrong_objective = copy.deepcopy(self.frozen_density_row)
        wrong_objective["private_audit"]["density_frontier"][0]["optimizer"][
            "objective_mode"
        ] = "legacy"
        refresh_density_accounting(wrong_objective)
        mutations.append((wrong_objective, "objective mode mismatch"))

        nonempty_frontier = copy.deepcopy(self.frozen_density_row)
        optimizer = nonempty_frontier["private_audit"]["density_frontier"][0][
            "optimizer"
        ]
        optimizer["full_objective_exact"] = False
        optimizer["remaining_frontier_nodes"] = 1
        optimizer["termination_reason"] = "node_cap"
        optimizer["frontier_states"] = [
            {
                "selected_mask_hex": "0x0",
                "available_mask_hex": "0x0",
                "selected_support_mask_hex": "0x0",
                "support_upper_bound": 0,
                "selected_count_upper_bound": 0,
            }
        ]
        optimizer["frontier_sha256"] = VERIFIER["digest"](
            optimizer["frontier_states"]
        )
        refresh_density_accounting(nonempty_frontier)
        mutations.append((nonempty_frontier, "exact frontier must contain exactly 0"))

        oversized_mask = copy.deepcopy(self.frozen_density_row)
        oversized_mask["private_audit"]["density_frontier"][0]["optimizer"][
            "selected_mask_hex"
        ] = "0x" + "f" * 128
        refresh_density_accounting(oversized_mask)
        mutations.append((oversized_mask, "optimizer mask"))

        oversized_edges = copy.deepcopy(self.frozen_density_row)
        public = oversized_edges["public_model"]["density_frontier"][0]
        formal_bound = sum(math.comb(4 + degree - 1, degree) for degree in range(5))
        public["public_edges"] = [
            {"left": "O", "right": "O", "output": "O"}
            for _ in range(formal_bound * (formal_bound + 1) // 2 + 1)
        ]
        public["public_edges_sha256"] = VERIFIER["digest"](public["public_edges"])
        refresh_density_accounting(oversized_edges)
        mutations.append((oversized_edges, "edge table exceeds its source-derived length bound"))

        verifier_globals = VERIFIER["_verify_density_row_for_tests"].__globals__
        guarded = (
            "verify_curve_provenance",
            "frozen_curve_record",
            "registered_curve_bundle",
            "replay_density_search",
            "independent_density_primary_optimum",
        )
        originals = {name: verifier_globals[name] for name in guarded}
        calls = []

        def forbidden(name):
            def reject(*_args, **_kwargs):
                calls.append(name)
                raise AssertionError(f"static admission must precede {name}")

            return reject

        for name in guarded:
            verifier_globals[name] = forbidden(name)
        try:
            for mutated, expected in mutations:
                with self.subTest(expected=expected):
                    report = VERIFIER["_verify_density_row_for_tests"](
                        mutated, 100000, "frozen_fixture"
                    )
                    self.assertFalse(report["valid"])
                    self.assertIsNone(report["resource_reservation"])
                    self.assertTrue(
                        any(expected in error for error in report["errors"]),
                        report["errors"],
                    )
        finally:
            verifier_globals.update(originals)
        self.assertEqual(calls, [])

    def test_v9_claims_and_nested_integrity_precede_reservation_and_math(self) -> None:
        baseline = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        mutations = []

        summary = copy.deepcopy(baseline)
        summary["summary"]["row_count"] += 1
        resign_document(summary)
        mutations.append((summary, "document summary mismatch"))

        gate = copy.deepcopy(baseline)
        gate["family_gate"]["status"] = "PASS"
        resign_document(gate)
        mutations.append((gate, "frozen family gate is not the exact registered object"))

        nested_digest = copy.deepcopy(baseline)
        nested_digest["rows"][0]["public_model"]["factor_base"][
            "selection_sha256"
        ] = "0" * 64
        refresh_density_accounting(nested_digest["rows"][0])
        resign_document(nested_digest)
        mutations.append((nested_digest, "factor-base selection digest mismatch"))

        nested_accounting = copy.deepcopy(baseline)
        nested_accounting["rows"][0]["accounting"]["public_model_json_bytes"] += 1
        resign_density_row(nested_accounting["rows"][0])
        resign_document(nested_accounting)
        mutations.append((nested_accounting, "cost-accounting byte receipt mismatch"))

        verifier_globals = VERIFIER["verify_document"].__globals__
        originals = {
            name: verifier_globals[name]
            for name in ("resource_envelope", "_verify_density_row_unchecked")
        }
        calls = []

        def forbidden(name):
            def reject(*_args, **_kwargs):
                calls.append(name)
                raise AssertionError(f"static admission must precede {name}")

            return reject

        for name in originals:
            verifier_globals[name] = forbidden(name)
        try:
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "static-preflight.json"
                for document, expected in mutations:
                    with self.subTest(expected=expected):
                        path.write_bytes(VERIFIER["stable_bytes"](document))
                        report = VERIFIER["verify_document"](path, 100000)
                        self.assertFalse(report["valid"])
                        self.assertIsNone(report["resource_reservation"])
                        self.assertTrue(
                            any(expected in error for error in report["errors"]),
                            report["errors"],
                        )
        finally:
            verifier_globals.update(originals)
        self.assertEqual(calls, [])

    def test_v9_replay_budget_and_actual_phase_receipts_fail_closed(self) -> None:
        over_budget = copy.deepcopy(self.frozen_density_row)
        for cell in over_budget["private_audit"]["density_frontier"]:
            cell["optimizer"]["node_cap"] = 100001
        refresh_density_accounting(over_budget)
        verifier_globals = VERIFIER["_verify_density_row_for_tests"].__globals__
        original_replay = verifier_globals["replay_density_search"]
        replay_calls = 0

        def forbidden_replay(*_args, **_kwargs):
            nonlocal replay_calls
            replay_calls += 1
            raise AssertionError("replay must not run")

        verifier_globals["replay_density_search"] = forbidden_replay
        try:
            report = VERIFIER["_verify_density_row_for_tests"](
                over_budget, 100000, "frozen_fixture"
            )
        finally:
            verifier_globals["replay_density_search"] = original_replay
        self.assertFalse(report["valid"])
        self.assertEqual(replay_calls, 0)
        self.assertEqual(report["primary_nodes"], 0)
        self.assertTrue(
            any("trusted verifier limit" in error for error in report["errors"])
        )

        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        document_globals = VERIFIER["_verify_v9_document_value_for_tests"].__globals__
        original_total_replay = document_globals["MAXIMUM_TOTAL_REPLAY_NODES"]
        original_row_verifier = document_globals["_verify_density_row_unchecked"]
        aggregate_row_calls = 0

        def forbidden_aggregate_row(*_args, **_kwargs):
            nonlocal aggregate_row_calls
            aggregate_row_calls += 1
            raise AssertionError("aggregate-budget rejection must precede row semantics")

        document_globals["MAXIMUM_TOTAL_REPLAY_NODES"] = 399999
        document_globals["_verify_density_row_unchecked"] = forbidden_aggregate_row
        try:
            aggregate_errors, aggregate_reports = VERIFIER[
                "_verify_v9_document_value_for_tests"
            ](document, 100000)
        finally:
            document_globals["MAXIMUM_TOTAL_REPLAY_NODES"] = original_total_replay
            document_globals["_verify_density_row_unchecked"] = original_row_verifier
        self.assertIn(
            "replay-node bound exceeds the trusted verifier limit", aggregate_errors
        )
        self.assertEqual(aggregate_reports, [])
        self.assertEqual(aggregate_row_calls, 0)

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "valid.json"
            path.write_bytes(VERIFIER["stable_bytes"](document))
            valid = VERIFIER["verify_document"](path, 100000)
            self.assertTrue(valid["valid"], valid["errors"])
            standalone = standalone_frozen_b4_oracle()
            standalone_candidate_count = standalone["candidate_count"]
            standalone_eligible_count = standalone["eligible_count"]
            self.assertEqual(
                valid["actual_work"],
                {
                    "actual_work_complete": True,
                    "registered_curve_cache_hits": 0,
                    "registered_curve_cache_misses": 0,
                    "registered_curve_draws": 0,
                    "registered_curve_hash_calls": 0,
                    "registered_prime_candidates": 0,
                    "predicate_hash_calls": 0,
                    "registered_curve_point_enumerations": 0,
                    "frozen_curve_point_enumerations": 1,
                    "semantic_curve_point_enumerations": 1,
                    "primary_curve_point_enumerations": 4,
                    "expansion_cells": 214,
                    "graph_candidate_evaluations": standalone_candidate_count,
                    "graph_eligible_conflict_checks": math.comb(
                        standalone_eligible_count, 2
                    ),
                    "graph_eligible_pair_output_cells": (
                        standalone_eligible_count**2
                    ),
                    "replay_nodes": 218,
                    "replay_metric_cache_entries": 268,
                    "retained_model_replay_cache_entries": 268,
                    "independent_primary_nodes": 250,
                    "primary_support_cache_entries": 56,
                    "primary_constrained_cache_entries": 129,
                    "retained_model_calls": 401,
                    "retained_model_cells": 41404,
                    "registered_curve_cache_entries": 0,
                },
            )
            self.assertEqual(
                valid["resource_reservation"],
                {
                    "row_count": 1,
                    "cap_cell_count": 4,
                    "registered_curve_cache_entries": 0,
                    "registered_curve_cache_lookups_upper_bound": 0,
                    "registered_curve_cache_misses_upper_bound": 0,
                    "registered_prime_candidates_upper_bound": 0,
                    "registered_curve_draws_upper_bound": 0,
                    "registered_curve_hash_calls_upper_bound": 0,
                    "registered_curve_point_enumerations_upper_bound": 0,
                    "frozen_curve_point_enumerations_upper_bound": 1,
                    "predicate_hash_calls_upper_bound": 0,
                    "semantic_curve_point_enumerations_upper_bound": 1,
                    "primary_curve_point_enumerations_upper_bound": 4,
                    "expansion_cells_upper_bound": 214,
                    "graph_candidate_evaluations_upper_bound": 35,
                    "graph_eligible_conflict_checks_upper_bound": 595,
                    "graph_eligible_pair_output_cells_upper_bound": 1225,
                    "replay_nodes_upper_bound": 400000,
                    "independent_primary_nodes_upper_bound": 400000,
                    "metric_cache_entries_upper_bound": 1610320,
                    "retained_model_calls_upper_bound": 805164,
                    "retained_model_cells_upper_bound": 2000832540,
                },
            )
            self.assertEqual(valid["resource_reservation"]["row_count"], 1)
            self.assertEqual(valid["resource_reservation"]["cap_cell_count"], 4)
            self.assertEqual(
                valid["resource_reservation"]["replay_nodes_upper_bound"], 400000
            )
            self.assertEqual(
                valid["resource_reservation"]["independent_primary_nodes_upper_bound"],
                400000,
            )
            self.assertLessEqual(
                valid["actual_work"]["replay_nodes"],
                valid["resource_reservation"]["replay_nodes_upper_bound"],
            )
            self.assertLessEqual(
                valid["actual_work"]["independent_primary_nodes"],
                valid["resource_reservation"]["independent_primary_nodes_upper_bound"],
            )
            observed_cache_entries = sum(
                valid["actual_work"][name]
                for name in (
                    "replay_metric_cache_entries",
                    "retained_model_replay_cache_entries",
                    "primary_support_cache_entries",
                    "primary_constrained_cache_entries",
                )
            )
            self.assertLessEqual(
                observed_cache_entries,
                valid["resource_reservation"]["metric_cache_entries_upper_bound"],
            )
            self.assertLessEqual(
                valid["actual_work"]["retained_model_calls"],
                valid["resource_reservation"]["retained_model_calls_upper_bound"],
            )
            self.assertLessEqual(
                valid["actual_work"]["retained_model_cells"],
                valid["resource_reservation"]["retained_model_cells_upper_bound"],
            )
            self.assertLessEqual(
                valid["actual_work"]["semantic_curve_point_enumerations"],
                valid["resource_reservation"][
                    "semantic_curve_point_enumerations_upper_bound"
                ],
            )
            self.assertLessEqual(
                valid["actual_work"]["primary_curve_point_enumerations"],
                valid["resource_reservation"][
                    "primary_curve_point_enumerations_upper_bound"
                ],
            )
            self.assertLessEqual(
                valid["actual_work"]["registered_prime_candidates"],
                valid["resource_reservation"][
                    "registered_prime_candidates_upper_bound"
                ],
            )
            self.assertLessEqual(
                valid["actual_work"]["predicate_hash_calls"],
                valid["resource_reservation"][
                    "predicate_hash_calls_upper_bound"
                ],
            )
            self.assertTrue(valid["actual_work"]["actual_work_complete"])

            extra = copy.deepcopy(document)
            extra["unexpected"] = True
            resign_document(extra)
            path.write_bytes(VERIFIER["stable_bytes"](extra))
            invalid = VERIFIER["verify_document"](path, 100000)
            self.assertFalse(invalid["valid"])
            self.assertEqual(
                invalid["phases"][-1],
                {"name": "source_collection_bounds", "status": "failed"},
            )
            self.assertFalse(
                any(
                    phase["name"] == "bounded_json_shape"
                    for phase in invalid["phases"]
                )
            )

            budget_invalid = VERIFIER["verify_document"](path, False)
            self.assertEqual(
                budget_invalid["phases"],
                [{"name": "verifier_budget_preflight", "status": "failed"}],
            )

    def test_v9_phase_receipts_match_executed_control_flow(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"

            path.write_bytes(VERIFIER["stable_bytes"](document))
            valid = VERIFIER["verify_document"](path, 100000)
            self.assertTrue(valid["valid"], valid["errors"])
            self.assertEqual(
                valid["phases"],
                [
                    {"name": "verifier_budget_preflight", "status": "passed"},
                    {"name": "single_regular_file_snapshot", "status": "passed"},
                    {"name": "strict_json_parse", "status": "passed"},
                    {"name": "source_collection_bounds", "status": "passed"},
                    {"name": "bounded_json_shape", "status": "passed"},
                    {"name": "exact_schema_routing", "status": "passed"},
                    {"name": "closed_document_schema", "status": "passed"},
                    {"name": "exact_document_types", "status": "passed"},
                    {
                        "name": "document_digest_and_protocol_identity",
                        "status": "passed",
                    },
                    {"name": "registered_document_envelope", "status": "passed"},
                    {"name": "closed_registered_row_preflight", "status": "passed"},
                    {"name": "registered_matrix_preflight", "status": "passed"},
                    {
                        "name": "document_summary_and_family_gate_preflight",
                        "status": "passed",
                    },
                    {"name": "trusted_resource_reservation", "status": "passed"},
                    {
                        "name": "curve_factor_graph_and_expansion_reconstruction",
                        "status": "passed",
                        "expected_units": 1,
                        "completed_units": 1,
                        "failed_units": 0,
                    },
                    {
                        "name": "deterministic_optimizer_replay",
                        "status": "passed",
                        "expected_units": 4,
                        "completed_units": 4,
                        "failed_units": 0,
                    },
                    {
                        "name": "retained_model_transcript_reconstruction",
                        "status": "passed",
                        "expected_units": 4,
                        "completed_units": 4,
                        "failed_units": 0,
                    },
                    {
                        "name": "independent_primary_proof",
                        "status": "passed",
                        "expected_units": 4,
                        "completed_units": 4,
                        "failed_units": 0,
                    },
                    {"name": "row_semantic_verification", "status": "passed"},
                    {
                        "name": "actual_work_reservation_dominance",
                        "status": "passed",
                    },
                    {
                        "name": "successful_phase_closure_validity",
                        "status": "passed",
                    },
                ],
            )

            path.write_text('{"schema":', encoding="ascii")
            malformed = VERIFIER["verify_document"](path, 100000)
            self.assertEqual(
                malformed["phases"][-1],
                {"name": "strict_json_parse", "status": "failed"},
            )
            self.assertFalse(
                any(phase["name"] == "bounded_json_shape" for phase in malformed["phases"])
            )

            legacy = copy.deepcopy(document)
            legacy["schema"] = "sgcp-embed-002-density-frontier-candidate-v5"
            resign_document(legacy)
            path.write_bytes(VERIFIER["stable_bytes"](legacy))
            legacy_report = VERIFIER["verify_document"](path, 100000)
            self.assertEqual(
                legacy_report["phases"][-2:],
                [
                    {"name": "exact_schema_routing", "status": "passed"},
                    {"name": "unsupported_legacy_rejection", "status": "passed"},
                ],
            )

            invalid_envelope = copy.deepcopy(document)
            invalid_envelope["parameters"]["node_cap_per_cap"] = 99999
            resign_document(invalid_envelope)
            path.write_bytes(VERIFIER["stable_bytes"](invalid_envelope))
            envelope_report = VERIFIER["verify_document"](path, 100000)
            self.assertEqual(
                envelope_report["phases"][-1],
                {"name": "registered_document_envelope", "status": "failed"},
            )
            self.assertFalse(
                any(
                    phase["name"] == "closed_registered_row_preflight"
                    for phase in envelope_report["phases"]
                )
            )

    def test_v9_success_requires_complete_unit_phase_receipts(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        verifier_globals = VERIFIER["verify_document"].__globals__
        original_record = verifier_globals["record_phase_unit"]
        suppressed = False

        def suppress_one_primary_receipt(phases, name, status):
            nonlocal suppressed
            if (
                not suppressed
                and name == "independent_primary_proof"
                and status == "passed"
            ):
                suppressed = True
                return
            original_record(phases, name, status)

        verifier_globals["record_phase_unit"] = suppress_one_primary_receipt
        try:
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "suppressed-phase.json"
                path.write_bytes(VERIFIER["stable_bytes"](document))
                report = VERIFIER["verify_document"](path, 100000)
        finally:
            verifier_globals["record_phase_unit"] = original_record

        self.assertTrue(suppressed)
        self.assertFalse(report["valid"])
        primary_phase = next(
            phase
            for phase in report["phases"]
            if phase["name"] == "independent_primary_proof"
        )
        self.assertEqual(
            primary_phase,
            {
                "name": "independent_primary_proof",
                "status": "incomplete",
                "expected_units": 4,
                "completed_units": 3,
                "failed_units": 0,
            },
        )
        self.assertEqual(
            report["phases"][-1],
            {"name": "successful_phase_closure_validity", "status": "failed"},
        )
        self.assertIn(
            "successful phase 'independent_primary_proof' is not passed",
            report["errors"],
        )

    def test_v9_second_cap_exceptions_preserve_partial_work_and_reservation(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        cases = (
            ("replay_density_search", "deterministic_optimizer_replay"),
            ("independent_density_primary_optimum", "independent_primary_proof"),
        )
        verifier_globals = VERIFIER["verify_document"].__globals__
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            path.write_bytes(VERIFIER["stable_bytes"](document))
            for function_name, phase_name in cases:
                with self.subTest(function_name=function_name):
                    original = verifier_globals[function_name]
                    calls = 0

                    def fail_on_second(*args, **kwargs):
                        nonlocal calls
                        calls += 1
                        if calls == 2:
                            raise RuntimeError("injected second-cap failure")
                        return original(*args, **kwargs)

                    verifier_globals[function_name] = fail_on_second
                    try:
                        report = VERIFIER["verify_document"](path, 100000)
                    finally:
                        verifier_globals[function_name] = original

                    self.assertFalse(report["valid"])
                    self.assertIsNotNone(report["resource_reservation"])
                    self.assertEqual(
                        report["resource_reservation"]["cap_cell_count"], 4
                    )
                    self.assertEqual(report["row_count"], 1)
                    self.assertEqual(len(report["rows"][0]["cap_reports"]), 2)
                    first_cap = report["rows"][0]["cap_reports"][0]
                    self.assertGreater(
                        first_cap["replay_nodes"] + first_cap["primary_nodes"], 0
                    )
                    self.assertFalse(report["actual_work"]["actual_work_complete"])
                    self.assertEqual(
                        next(
                            phase["status"]
                            for phase in report["phases"]
                            if phase["name"] == phase_name
                        ),
                        "failed",
                    )
                    self.assertTrue(
                        any(
                            "injected second-cap failure" in error
                            for error in report["errors"]
                        ),
                        report["errors"],
                    )

    def test_v9_mid_function_failures_preserve_failing_cap_work(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        cases = (
            ("replay_nodes", "deterministic_optimizer_replay"),
            ("independent_primary_nodes", "independent_primary_proof"),
        )
        verifier_globals = VERIFIER["verify_document"].__globals__
        original_charge = verifier_globals["charge_actual_work"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            path.write_bytes(VERIFIER["stable_bytes"](document))
            for counter_name, phase_name in cases:
                with self.subTest(counter_name=counter_name):
                    observed = 0

                    def fail_after_charge(name, amount=1):
                        nonlocal observed
                        original_charge(name, amount)
                        if name == counter_name:
                            observed += amount
                            if observed >= 2:
                                raise RuntimeError("injected mid-function failure")

                    verifier_globals["charge_actual_work"] = fail_after_charge
                    try:
                        report = VERIFIER["verify_document"](path, 100000)
                    finally:
                        verifier_globals["charge_actual_work"] = original_charge

                    self.assertFalse(report["valid"])
                    self.assertFalse(report["actual_work"]["actual_work_complete"])
                    self.assertEqual(report["actual_work"][counter_name], 2)
                    cap_counter_name = (
                        "primary_nodes"
                        if counter_name == "independent_primary_nodes"
                        else counter_name
                    )
                    self.assertEqual(
                        report["rows"][0]["cap_reports"][0][cap_counter_name], 2
                    )
                    phase = next(
                        value for value in report["phases"] if value["name"] == phase_name
                    )
                    self.assertEqual(
                        phase,
                        {
                            "name": phase_name,
                            "status": "failed",
                            "expected_units": 4,
                            "completed_units": 1,
                            "failed_units": 1,
                        },
                    )
                    self.assertTrue(
                        any(
                            "injected mid-function failure" in error
                            for error in report["errors"]
                        ),
                        report["errors"],
                    )

    def test_v9_graph_and_expansion_failures_preserve_partial_work(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        counters = (
            "graph_candidate_evaluations",
            "graph_eligible_conflict_checks",
            "expansion_cells",
            "graph_eligible_pair_output_cells",
        )
        verifier_globals = VERIFIER["verify_document"].__globals__
        original_charge = verifier_globals["charge_actual_work"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "graph-partial-work.json"
            path.write_bytes(VERIFIER["stable_bytes"](document))
            for counter_name in counters:
                with self.subTest(counter_name=counter_name):
                    observed = 0

                    def fail_after_second_charge(name, amount=1):
                        nonlocal observed
                        original_charge(name, amount)
                        if name == counter_name:
                            observed += amount
                            if observed >= 2:
                                raise RuntimeError("injected graph/expansion failure")

                    verifier_globals["charge_actual_work"] = fail_after_second_charge
                    try:
                        report = VERIFIER["verify_document"](path, 100000)
                    finally:
                        verifier_globals["charge_actual_work"] = original_charge

                    self.assertFalse(report["valid"])
                    self.assertFalse(report["actual_work"]["actual_work_complete"])
                    self.assertEqual(report["actual_work"][counter_name], 2)
                    phase = next(
                        value
                        for value in report["phases"]
                        if value["name"]
                        == "curve_factor_graph_and_expansion_reconstruction"
                    )
                    self.assertEqual(
                        phase,
                        {
                            "name": "curve_factor_graph_and_expansion_reconstruction",
                            "status": "failed",
                            "expected_units": 1,
                            "completed_units": 1,
                            "failed_units": 1,
                        },
                    )
                    self.assertTrue(
                        any(
                            "injected graph/expansion failure" in error
                            for error in report["errors"]
                        ),
                        report["errors"],
                    )

    def test_v9_point_enumeration_calls_are_charged_before_failure(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        curve_class = VERIFIER["Curve"]
        original_points = curve_class.points
        expected_counts = (
            (
                1,
                1,
                0,
                0,
                "curve_factor_graph_and_expansion_reconstruction",
                1,
            ),
            (
                2,
                1,
                1,
                0,
                "curve_factor_graph_and_expansion_reconstruction",
                1,
            ),
            (3, 1, 1, 1, "independent_primary_proof", 4),
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "enumeration.json"
            path.write_bytes(VERIFIER["stable_bytes"](document))
            for (
                fail_call,
                frozen_count,
                semantic_count,
                primary_count,
                phase_name,
                expected_units,
            ) in expected_counts:
                with self.subTest(fail_call=fail_call):
                    calls = 0

                    def injected_points(instance):
                        nonlocal calls
                        calls += 1
                        if calls == fail_call:
                            raise RuntimeError("injected point-enumeration failure")
                        return original_points(instance)

                    curve_class.points = injected_points
                    try:
                        report = VERIFIER["verify_document"](path, 100000)
                    finally:
                        curve_class.points = original_points

                    self.assertFalse(report["valid"])
                    self.assertFalse(report["actual_work"]["actual_work_complete"])
                    self.assertEqual(
                        report["actual_work"]["frozen_curve_point_enumerations"],
                        frozen_count,
                    )
                    self.assertEqual(
                        report["actual_work"]["semantic_curve_point_enumerations"],
                        semantic_count,
                    )
                    self.assertEqual(
                        report["actual_work"]["primary_curve_point_enumerations"],
                        primary_count,
                    )
                    phase = next(
                        value
                        for value in report["phases"]
                        if value["name"] == phase_name
                    )
                    self.assertEqual(
                        phase,
                        {
                            "name": phase_name,
                            "status": "failed",
                            "expected_units": expected_units,
                            "completed_units": 1,
                            "failed_units": 1,
                        },
                    )
                    self.assertTrue(
                        any(
                            "injected point-enumeration failure" in error
                            for error in report["errors"]
                        ),
                        report["errors"],
                    )

    def test_v9_actual_work_overage_invalidates_an_otherwise_valid_document(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        verifier_globals = VERIFIER["verify_document"].__globals__
        original_envelope = verifier_globals["resource_envelope"]

        def under_reserve(rows, maximum_nodes, scope):
            receipt, errors = original_envelope(rows, maximum_nodes, scope)
            receipt["replay_nodes_upper_bound"] = 0
            return receipt, errors

        verifier_globals["resource_envelope"] = under_reserve
        try:
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "under-reserved.json"
                path.write_bytes(VERIFIER["stable_bytes"](document))
                report = VERIFIER["verify_document"](path, 100000)
        finally:
            verifier_globals["resource_envelope"] = original_envelope

        self.assertFalse(report["valid"])
        self.assertTrue(report["actual_work"]["actual_work_complete"])
        self.assertEqual(report["actual_work"]["replay_nodes"], 218)
        self.assertEqual(report["resource_reservation"]["replay_nodes_upper_bound"], 0)
        self.assertIn(
            "actual work exceeds reservation: replay_nodes=218 > "
            "replay_nodes_upper_bound=0",
            report["errors"],
        )
        self.assertEqual(
            report["phases"][-1],
            {"name": "actual_work_reservation_dominance", "status": "failed"},
        )

    def test_v9_completed_work_rejects_exact_enumeration_undercharge(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        verifier_globals = VERIFIER["verify_document"].__globals__
        original_charge = verifier_globals["charge_actual_work"]

        def suppress_primary_enumeration(name, amount=1):
            if name != "primary_curve_point_enumerations":
                original_charge(name, amount)

        verifier_globals["charge_actual_work"] = suppress_primary_enumeration
        try:
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "undercharged.json"
                path.write_bytes(VERIFIER["stable_bytes"](document))
                report = VERIFIER["verify_document"](path, 100000)
        finally:
            verifier_globals["charge_actual_work"] = original_charge

        self.assertFalse(report["valid"])
        self.assertTrue(report["actual_work"]["actual_work_complete"])
        self.assertTrue(report["rows"][0]["valid"], report["rows"][0]["errors"])
        self.assertEqual(report["actual_work"]["primary_curve_point_enumerations"], 0)
        self.assertEqual(
            report["resource_reservation"][
                "primary_curve_point_enumerations_upper_bound"
            ],
            4,
        )
        self.assertIn(
            "actual work exact-count mismatch: "
            "primary_curve_point_enumerations=0 != "
            "primary_curve_point_enumerations_upper_bound=4",
            report["errors"],
        )
        self.assertEqual(
            report["phases"][-1],
            {"name": "actual_work_reservation_dominance", "status": "failed"},
        )

    def test_v9_ordering_contract_is_independently_frozen(self) -> None:
        mutated = copy.deepcopy(self.frozen_density_row)
        mutated["public_model"]["ordering_contract"]["point_labels"] = (
            "affine labels may contain leading zeroes"
        )
        refresh_density_accounting(mutated)
        report = VERIFIER["_verify_density_row_for_tests"](
            mutated, 100000, "frozen_fixture"
        )
        self.assertFalse(report["valid"])
        self.assertTrue(
            any("ordering contract mismatch" in error for error in report["errors"])
        )

    def test_frozen_document_verifies_and_empty_canonical_document_is_rejected(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        errors, reports = VERIFIER["_verify_v9_document_value_for_tests"](document, 100000)
        self.assertEqual(errors, [])
        self.assertTrue(reports[0]["valid"])

        with self.assertRaises(ValueError):
            MODULE["build_document"]([], "canonical", MODULE["canonical_parameters"]())

        empty = copy.deepcopy(document)
        empty.update(
            {
                "scope": "canonical",
                "canonical": True,
                "interpretation": "canonical candidate; coordinator interpretation still required",
                "parameters": MODULE["canonical_parameters"](),
                "rows": [],
                "summary": MODULE["document_summary"]([]),
                "family_gate": {"status": "PASS"},
            }
        )
        resign_document(empty)
        errors, _ = VERIFIER["_verify_v9_document_value_for_tests"](empty, 100000)
        self.assertTrue(errors)
        self.assertIn("canonical document must contain exactly 168 rows", errors)

    def test_v9_document_exact_types_are_closed(self) -> None:
        baseline = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        mutations = (
            (("protocol_version",), 5.0),
            (("canonical",), 0),
            (("claim_status", 0), 1),
            (("summary", "row_count"), False),
            (("family_gate", "status"), False),
        )
        for path, replacement in mutations:
            with self.subTest(path=path):
                document = copy.deepcopy(baseline)
                target = document
                for component in path[:-1]:
                    target = target[component]
                target[path[-1]] = replacement
                resign_document(document)
                errors, _ = VERIFIER["_verify_v9_document_value_for_tests"](
                    document, 100000
                )
                self.assertTrue(errors)

    def test_document_router_uses_v9_strict_path_and_rejects_every_legacy_schema(
        self,
    ) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        def route(value):
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "synthetic-document.json"
                path.write_bytes(VERIFIER["stable_bytes"](value))
                return VERIFIER["verify_document"](
                    path, 100000
                )

        strict_report = route(document)
        self.assertTrue(strict_report["valid"], strict_report["errors"])
        self.assertTrue(
            any(
                "closed_document_schema" in check
                for check in strict_report["independent_checks"]
            )
        )

        for legacy_schema in sorted(VERIFIER["LEGACY_SCHEMAS"]):
            with self.subTest(legacy_schema=legacy_schema):
                downgraded = copy.deepcopy(document)
                downgraded["schema"] = legacy_schema
                resign_document(downgraded)
                legacy_report = route(downgraded)
                self.assertFalse(legacy_report["valid"])
                self.assertTrue(
                    any(
                        "unsupported legacy document schema" in error
                        for error in legacy_report["errors"]
                    ),
                    legacy_report["errors"],
                )
                self.assertEqual(legacy_report["row_count"], 0)
                self.assertFalse(
                    any("graph" in check for check in legacy_report["independent_checks"])
                )

        empty_v3 = {
            "schema": "sgcp-embed-002-density-frontier-candidate-v3",
            "canonical": False,
            "rows": [],
        }
        empty_v3["document_sha256"] = VERIFIER["digest"](empty_v3)
        empty_report = route(empty_v3)
        self.assertFalse(empty_report["valid"])
        self.assertEqual(empty_report["row_count"], 0)

        malformed_schema = copy.deepcopy(document)
        malformed_schema["schema"] = []
        resign_document(malformed_schema)
        malformed_report = route(malformed_schema)
        self.assertFalse(malformed_report["valid"])
        self.assertTrue(
            any(
                "document.schema has a non-source container/scalar type" in error
                for error in malformed_report["errors"]
            )
        )

    def test_canonical_matrix_envelope_rejects_every_grid_mutation(self) -> None:
        rows = synthetic_gate_rows()
        self.assertEqual(VERIFIER["canonical_matrix_errors"](rows), [])
        MODULE["validate_canonical_rows"](rows)

        cases = []
        missing = copy.deepcopy(rows[:-1])
        cases.append(("missing", missing, "grid/order"))
        extra = copy.deepcopy(rows)
        extra.append(copy.deepcopy(rows[-1]))
        cases.append(("extra", extra, "grid/order"))
        duplicate = copy.deepcopy(rows)
        duplicate[1] = copy.deepcopy(duplicate[0])
        cases.append(("duplicate", duplicate, "grid/order"))
        reordered = copy.deepcopy(rows)
        reordered[0], reordered[1] = reordered[1], reordered[0]
        cases.append(("reordered", reordered, "grid/order"))
        wrong_public_cap = copy.deepcopy(rows)
        wrong_public_cap[0]["public_model"]["constrained_budget_caps"][0] += 1
        cases.append(("public_cap", wrong_public_cap, "cap schedule"))
        wrong_private_cap = copy.deepcopy(rows)
        wrong_private_cap[0]["private_audit"]["density_frontier"][0][
            "constrained_cap"
        ] += 1
        cases.append(("private_cap", wrong_private_cap, "cap-cell"))
        wrong_node_cap = copy.deepcopy(rows)
        wrong_node_cap[0]["private_audit"]["density_frontier"][0]["optimizer"][
            "node_cap"
        ] = MODULE["CANONICAL_NODE_CAP"] - 1
        cases.append(("node_cap", wrong_node_cap, "node-cap"))
        inconsistent_curve = copy.deepcopy(rows)
        inconsistent_curve[1]["curve"]["p"] += 2
        cases.append(("inconsistent_curve", inconsistent_curve, "inconsistent curve"))
        cross_seed_duplicate = copy.deepcopy(rows)
        source_curve = rows[0]["curve"]
        for row in cross_seed_duplicate:
            if row["curve"]["bits"] == 5 and row["curve"]["seed"] == 211:
                for name in ("p", "a", "b", "q"):
                    row["curve"][name] = source_curve[name]
        cases.append(
            ("cross_seed_duplicate", cross_seed_duplicate, "cross-seed duplicate")
        )

        for label, mutated, expected_fragment in cases:
            with self.subTest(label=label):
                errors = VERIFIER["canonical_matrix_errors"](mutated)
                self.assertTrue(
                    any(expected_fragment in error for error in errors), errors
                )
                with self.assertRaises(ValueError):
                    MODULE["validate_canonical_rows"](mutated)

    def test_family_gate_matches_independent_evaluator_and_refuses_gaps(self) -> None:
        rows = synthetic_gate_rows()
        producer = MODULE["evaluate_family_gate"](rows)
        independent = VERIFIER["independent_family_gate"](rows)
        self.assertEqual(producer, independent)
        self.assertEqual(producer["status"], "PASS")
        self.assertEqual(len(producer["passing_family_cap_pairs"]), 6)

        incomplete = rows[:-1]
        with self.assertRaises(KeyError):
            MODULE["evaluate_family_gate"](incomplete)
        with self.assertRaises(KeyError):
            VERIFIER["independent_family_gate"](incomplete)

        unresolved = copy.deepcopy(rows)
        unresolved[0]["private_audit"]["density_frontier"][0]["optimizer"][
            "primary_exact"
        ] = False
        with self.assertRaises(ValueError):
            MODULE["evaluate_family_gate"](unresolved)
        with self.assertRaises(AssertionError):
            VERIFIER["independent_family_gate"](unresolved)

        gate_mutations = (
            ("primary_exact", False),
            ("full_objective_exact", False),
            ("retained_support_upper_bound", "increment"),
            ("absolute_gap", 1),
            ("absolute_gap", False),
            ("remaining_frontier_nodes", 1),
            ("frontier_states", [{"residual": True}]),
            ("frontier_sha256", "0" * 64),
            ("termination_reason", "node_cap"),
        )
        for field, value in gate_mutations:
            with self.subTest(field=field, value=value):
                mutated = copy.deepcopy(rows)
                optimizer = mutated[0]["private_audit"]["density_frontier"][0][
                    "optimizer"
                ]
                if value == "increment":
                    optimizer[field] += 1
                else:
                    optimizer[field] = value
                if field == "frontier_states":
                    optimizer["frontier_sha256"] = VERIFIER["digest"](value)
                with self.assertRaises(ValueError):
                    MODULE["evaluate_family_gate"](mutated)
                with self.assertRaises(AssertionError):
                    VERIFIER["independent_family_gate"](mutated)

    def test_family_gate_duplicate_null_median_preserves_multiplicity(self) -> None:
        values = [
            VERIFIER["Fraction"](value, 1) for value in (8, 8, 10, 12)
        ]
        self.assertEqual(VERIFIER["independent_median"](values), 9)
        self.assertEqual(
            VERIFIER["independent_median"](sorted(set(values))), 10
        )
        rows = configure_gate_rows()
        gate = VERIFIER["independent_family_gate"](rows)
        self.assertEqual(gate, MODULE["evaluate_family_gate"](rows))
        for family in MODULE["COORDINATE_FAMILIES"]:
            for cap_fraction in ("1/2", "3/4"):
                report = gate_cap_report(gate, family, cap_fraction)
                self.assertEqual(report["positive_comparisons"], 24)

    def test_family_gate_persistence_accepts_one_quarter_and_rejects_one_step_below(
        self,
    ) -> None:
        family = "least_x_interval"
        exact = configure_gate_rows()
        for row in exact:
            if row["family"] != family:
                continue
            full_cap = next(
                value
                for value in row["private_audit"]["density_frontier"]
                if value["constrained_cap"] == row["curve"]["q"]
            )
            full_cap["retention"]["retained_to_balanced_raw"] = {
                "numerator": 1,
                "denominator": 4,
            }
        exact_gate = VERIFIER["independent_family_gate"](exact)
        self.assertEqual(exact_gate, MODULE["evaluate_family_gate"](exact))
        exact_report = next(
            report for report in exact_gate["families"] if report["family"] == family
        )
        self.assertTrue(exact_report["full_cap_persistence_pass"])

        below = copy.deepcopy(exact)
        for row in below:
            if row["family"] != family or row["curve"]["bits"] != 8:
                continue
            full_cap = next(
                value
                for value in row["private_audit"]["density_frontier"]
                if value["constrained_cap"] == row["curve"]["q"]
            )
            full_cap["retention"]["retained_to_balanced_raw"] = {
                "numerator": 999,
                "denominator": 4000,
            }
        below_gate = VERIFIER["independent_family_gate"](below)
        self.assertEqual(below_gate, MODULE["evaluate_family_gate"](below))
        below_report = next(
            report for report in below_gate["families"] if report["family"] == family
        )
        self.assertFalse(below_report["full_cap_persistence_pass"])

    def test_family_gate_collapse_threshold_is_strictly_below_one_tenth(self) -> None:
        rows = configure_gate_rows()
        for row in rows:
            if row["family"] == MODULE["NULL_FAMILY"]:
                continue
            full_cap = next(
                value
                for value in row["private_audit"]["density_frontier"]
                if value["constrained_cap"] == row["curve"]["q"]
            )
            full_cap["retention"]["retained_to_balanced_raw"] = {
                "numerator": 1,
                "denominator": 10,
            }
        gate = VERIFIER["independent_family_gate"](rows)
        self.assertEqual(gate, MODULE["evaluate_family_gate"](rows))
        self.assertEqual(gate["negative_outcome"], "WEAKEN_OR_REJECT")
        self.assertTrue(
            all(
                report["full_cap_collapse_strata"] == 0
                and not report["full_cap_collapse"]
                for report in gate["families"]
            )
        )

    def test_family_gate_collapse_requires_every_coordinate_family(self) -> None:
        rows = configure_gate_rows()
        collapsing = set(MODULE["COORDINATE_FAMILIES"][:2])
        for row in rows:
            if row["family"] == MODULE["NULL_FAMILY"]:
                continue
            full_cap = next(
                value
                for value in row["private_audit"]["density_frontier"]
                if value["constrained_cap"] == row["curve"]["q"]
            )
            below = row["family"] in collapsing and row["curve"]["bits"] in (5, 6, 7)
            full_cap["retention"]["retained_to_balanced_raw"] = (
                {"numerator": 1, "denominator": 11}
                if below
                else {"numerator": 1, "denominator": 10}
            )
        gate = VERIFIER["independent_family_gate"](rows)
        self.assertEqual(gate, MODULE["evaluate_family_gate"](rows))
        self.assertEqual(gate["negative_outcome"], "WEAKEN_OR_REJECT")
        collapsed = {
            report["family"]
            for report in gate["families"]
            if report["full_cap_collapse"]
        }
        self.assertEqual(collapsed, collapsing)

    def test_family_gate_hand_derived_18_of_24_and_three_strata_boundary(self) -> None:
        rows = configure_gate_rows()
        family = "least_x_interval"
        thresholds = {5: 2, 6: 3, 7: 5, 8: 10}
        differences = {
            bits: [thresholds[bits]] * 6 if bits in (5, 6, 7) else [0] * 6
            for bits in MODULE["CANONICAL_BITS"]
        }
        set_gate_differences(rows, family, "1/2", differences)
        producer = MODULE["evaluate_family_gate"](rows)
        independent = VERIFIER["independent_family_gate"](rows)
        self.assertEqual(producer, independent)
        report = gate_cap_report(producer, family, "1/2")
        self.assertEqual(report["positive_comparisons"], 18)
        self.assertEqual(report["passing_bit_strata"], 3)
        self.assertTrue(report["pass"])
        self.assertEqual(
            producer["passing_family_cap_pairs"],
            [{"family": family, "cap_fraction": "1/2"}],
        )
        self.assertEqual(producer["negative_outcome"], "NOT_APPLICABLE")

    def test_family_gate_hand_derived_17_of_24_fails_with_three_strata(self) -> None:
        rows = configure_gate_rows()
        family = "least_x_interval"
        differences = {
            5: [2] * 6,
            6: [3] * 6,
            7: [5] * 5 + [0],
            8: [0] * 6,
        }
        set_gate_differences(rows, family, "1/2", differences)
        gate = VERIFIER["independent_family_gate"](rows)
        self.assertEqual(gate, MODULE["evaluate_family_gate"](rows))
        report = gate_cap_report(gate, family, "1/2")
        self.assertEqual(report["positive_comparisons"], 17)
        self.assertEqual(report["passing_bit_strata"], 3)
        self.assertFalse(report["pass"])
        self.assertEqual(gate["status"], "FAIL")

    def test_family_gate_hand_derived_18_of_24_fails_with_two_strata(self) -> None:
        rows = configure_gate_rows()
        family = "least_x_interval"
        differences = {
            5: [2] * 6,
            6: [3] * 6,
            7: [1, 1, 1, 0, 0, 0],
            8: [1, 1, 1, 0, 0, 0],
        }
        set_gate_differences(rows, family, "1/2", differences)
        gate = VERIFIER["independent_family_gate"](rows)
        self.assertEqual(gate, MODULE["evaluate_family_gate"](rows))
        report = gate_cap_report(gate, family, "1/2")
        self.assertEqual(report["positive_comparisons"], 18)
        self.assertEqual(report["passing_bit_strata"], 2)
        self.assertFalse(report["pass"])
        self.assertEqual(gate["status"], "FAIL")

    def test_family_gate_forbids_cross_cap_splicing_and_classifies_collapse(self) -> None:
        rows = configure_gate_rows()
        family = "least_x_interval"
        set_gate_differences(
            rows,
            family,
            "1/2",
            {
                5: [2] * 6,
                6: [3] * 6,
                7: [1, 1, 1, 0, 0, 0],
                8: [1, 1, 1, 0, 0, 0],
            },
        )
        set_gate_differences(
            rows,
            family,
            "3/4",
            {5: [2] * 6, 6: [3] * 6, 7: [5] * 5 + [0], 8: [0] * 6},
        )
        gate = VERIFIER["independent_family_gate"](rows)
        self.assertEqual(gate, MODULE["evaluate_family_gate"](rows))
        half = gate_cap_report(gate, family, "1/2")
        three_quarters = gate_cap_report(gate, family, "3/4")
        self.assertEqual(
            (half["positive_comparisons"], half["passing_bit_strata"]), (18, 2)
        )
        self.assertEqual(
            (
                three_quarters["positive_comparisons"],
                three_quarters["passing_bit_strata"],
            ),
            (17, 3),
        )
        self.assertEqual(gate["passing_family_cap_pairs"], [])
        self.assertEqual(gate["negative_outcome"], "WEAKEN_OR_REJECT")

        collapsed = configure_gate_rows()
        for row in collapsed:
            if row["family"] == MODULE["NULL_FAMILY"]:
                continue
            full_cap = next(
                value
                for value in row["private_audit"]["density_frontier"]
                if value["constrained_cap"] == row["curve"]["q"]
            )
            full_cap["retention"]["retained_to_balanced_raw"] = (
                {"numerator": 1, "denominator": 10}
                if row["curve"]["bits"] == 8
                else {"numerator": 1, "denominator": 20}
            )
        collapse_gate = VERIFIER["independent_family_gate"](collapsed)
        self.assertEqual(collapse_gate, MODULE["evaluate_family_gate"](collapsed))
        self.assertEqual(collapse_gate["status"], "FAIL")
        self.assertEqual(collapse_gate["negative_outcome"], "COLLAPSE")
        self.assertTrue(
            all(
                report["full_cap_collapse"]
                and report["full_cap_collapse_strata"] == 3
                for report in collapse_gate["families"]
            )
        )

    def test_main_refuses_canonical_mode(self) -> None:
        with self.assertRaises(PermissionError):
            MODULE["main"](["--output", str(DEVELOPMENT_SENTINEL)])
        with self.assertRaises(PermissionError):
            MODULE["main"](
                ["--development", "--output", str(DEVELOPMENT_SENTINEL)]
            )


DEVELOPMENT_SENTINEL = (
    REPO_ROOT
    / "experiments"
    / "EXP-SGCP-EMBED-002"
    / "development"
    / "must-not-exist.json"
)


if __name__ == "__main__":
    unittest.main()
