from __future__ import annotations

import copy
import itertools
import math
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


def standalone_frozen_b4_oracle(row):
    """Rebuild the B4 object without producer or verifier semantic helpers."""
    p = row["curve"]["p"]
    a = row["curve"]["a"]
    b = row["curve"]["b"]
    B = row["B"]
    affine = [
        (x, y)
        for x in range(p)
        for y in range(p)
        if (y * y - (x * x * x + a * x + b)) % p == 0
    ]
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

    degree2_by_point = {}
    for formal in itertools.combinations_with_replacement(range(B), 2):
        point = standalone_eval(p, a, factors, formal)
        degree2_by_point.setdefault(point, []).append(formal)
    representatives = [
        (point, min(degree2_by_point[point]))
        for point in sorted(degree2_by_point, key=standalone_point_order)
        if point is not None
    ]

    candidate_points = {}
    for left, right in itertools.combinations_with_replacement(
        range(len(representatives)), 2
    ):
        left_point, left_formal = representatives[left]
        right_point, right_formal = representatives[right]
        formal = tuple(sorted(left_formal + right_formal))
        point = standalone_add(p, a, left_point, right_point)
        if formal in candidate_points:
            assert candidate_points[formal] == point
        candidate_points[formal] = point
    candidates = [
        {"formal": formal, "point": candidate_points[formal]}
        for formal in sorted(candidate_points)
    ]

    eligible = []
    closure_maps = []
    for candidate in candidates:
        family = standalone_ideal(B, [candidate["formal"]])
        point_to_formal = {}
        collision = False
        for formal in sorted(family, key=lambda item: (len(item), item)):
            point = standalone_eval(p, a, factors, formal)
            if point in point_to_formal:
                collision = True
                break
            point_to_formal[point] = formal
        if not collision:
            eligible.append(candidate)
            closure_maps.append(point_to_formal)

    conflicts = [0] * len(eligible)
    conflict_count = 0
    for left in range(len(eligible)):
        for right in range(left + 1, len(eligible)):
            conflict = any(
                closure_maps[left][point] != closure_maps[right][point]
                for point in set(closure_maps[left]).intersection(closure_maps[right])
            )
            if conflict:
                conflicts[left] |= 1 << right
                conflicts[right] |= 1 << left
                conflict_count += 1

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
        edge_count = 0
        for position, left in enumerate(nonempty):
            for right in nonempty[position:]:
                union = tuple(sorted(left + right))
                if union not in family:
                    continue
                edge_count += 1
                constrained.update(
                    (evaluations[left], evaluations[right], evaluations[union])
                )
        selected_points = [eligible[index]["point"] for index in selected_indices]
        support = {
            standalone_add(p, a, left, right)
            for position, left in enumerate(selected_points)
            for right in selected_points[position:]
        }
        objective = (len(support), -len(constrained), -edge_count, len(maxima))
        witness = tuple(sorted(maxima))
        candidate = {
            "objective": objective,
            "witness": witness,
            "selected_indices": selected_indices,
            "constrained_count": len(constrained),
            "public_edge_count": edge_count,
        }
        for cap in row["public_model"]["constrained_budget_caps"]:
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
        "candidate_count": len(candidates),
        "eligible_count": len(eligible),
        "conflict_count": conflict_count,
        "winners": winners,
    }


def configure_gate_rows(null_supports=(8, 10, 10, 12)):
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
            cell["optimizer"]["retained_support_lower_bound"] = 10 + difference
            cell["optimizer"]["retained_support_upper_bound"] = 10 + difference


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
                curve, points, record = MODULE["generated_curve"](bits, seed, ops)
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

        generated_globals = MODULE["generated_curve"].__globals__
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
            _, _, record = MODULE["generated_curve"](5, 999)
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
        _, _, record = MODULE["generated_curve"](5, 101, ops)
        VERIFIER["verify_curve_provenance"](record)
        mutated = copy.deepcopy(record)
        mutated["rejection_digest"] = "0" * 64
        with self.assertRaises(AssertionError):
            VERIFIER["verify_curve_provenance"](mutated)

    def test_predicates_are_matched_and_deterministic(self) -> None:
        ops = MODULE["OperationCounts"]()
        curve, points, record = MODULE["generated_curve"](6, 101, ops)
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

        row = MODULE["build_density_row"](
            curve, points, record, 4, "mobius_interval", None, 100000, ops
        )
        self.assertTrue(VERIFIER["verify_density_row"](row, 100000)["valid"])
        mutated = copy.deepcopy(row)
        mutated["public_model"]["factor_base"]["parameters"]["map"]["nonce"] += 1
        resign_factor_base(mutated)
        refresh_density_accounting(mutated)
        report = VERIFIER["verify_density_row"](mutated, 100000)
        self.assertFalse(report["valid"])
        self.assertTrue(
            any(
                "Mobius derivation transcript mismatch" in error
                for error in report["errors"]
            )
        )

        illegal = copy.deepcopy(self.frozen_density_row)
        illegal["null_replicate"] = 999
        illegal["public_model"]["factor_base"]["null_replicate"] = 999
        resign_factor_base(illegal)
        refresh_density_accounting(illegal)
        report = VERIFIER["verify_density_row"](illegal, 100000)
        self.assertFalse(report["valid"])
        self.assertTrue(
            any(
                "coordinate family carries a null replicate" in error
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

    def test_independent_verifier_reconstructs_row_and_rejects_expansion_mutation(self) -> None:
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
        report = VERIFIER["verify_row"](row, 100000)
        self.assertTrue(report["valid"], report["errors"])

        mutated = copy.deepcopy(row)
        mutated["private_audit"]["expansion"]["8"]["support"] -= 1
        digest_payload = dict(mutated)
        digest_payload.pop("row_sha256")
        mutated["row_sha256"] = VERIFIER["digest"](digest_payload)
        mutation_report = VERIFIER["verify_row"](mutated, 100000)
        self.assertFalse(mutation_report["valid"])
        self.assertIn("additive expansion mismatch", mutation_report["errors"])

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

    def test_frozen_b4_matches_standalone_semantic_oracle(self) -> None:
        row = self.frozen_density_row
        oracle = standalone_frozen_b4_oracle(row)
        expected_factors = [
            tuple(point) for point in row["public_model"]["factor_base"]["points"]
        ]
        self.assertEqual(oracle["factors"], expected_factors)
        graph = row["private_audit"]["graph"]
        self.assertEqual(oracle["candidate_count"], graph["candidate_count"])
        self.assertEqual(oracle["eligible_count"], graph["eligible_candidate_count"])
        self.assertEqual(oracle["conflict_count"], graph["conflict_count"])
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
            self.assertEqual(winner["constrained_count"], public["constrained_count"])
            self.assertEqual(winner["public_edge_count"], public["public_edge_count"])

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
            self.assertEqual(
                private["retention"]["eight_fold_support"],
                row["private_audit"]["expansion"]["8"]["support"],
            )
        verification = VERIFIER["verify_density_row"](row, 100000)
        self.assertTrue(verification["valid"], verification["errors"])
        self.assertEqual(len(verification["cap_reports"]), 4)
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
        mutation_report = VERIFIER["verify_density_row"](mutated, 100000)
        self.assertFalse(mutation_report["valid"])
        self.assertIn("cost-accounting byte receipt mismatch", mutation_report["errors"])

        mutated = copy.deepcopy(row)
        mutated["structural_work"]["pair_output_cells"] += 1
        refresh_density_accounting(mutated)
        mutation_report = VERIFIER["verify_density_row"](mutated, 100000)
        self.assertFalse(mutation_report["valid"])
        self.assertIn("row structural-work receipt mismatch", mutation_report["errors"])

    def test_closed_schema_rejects_scalar_material_and_nested_graph_extras(self) -> None:
        scalar = copy.deepcopy(self.frozen_density_row)
        scalar["scalar_table"] = []
        refresh_density_accounting(scalar)
        report = VERIFIER["verify_density_row"](scalar, 100000)
        self.assertFalse(report["valid"])
        self.assertTrue(any("closed row schema" in error for error in report["errors"]))
        self.assertTrue(
            any("forbidden material key" in error for error in report["errors"])
        )

        nested = copy.deepcopy(self.frozen_density_row)
        nested["private_audit"]["individually_rejected"][0]["note"] = "extra"
        refresh_density_accounting(nested)
        report = VERIFIER["verify_density_row"](nested, 100000)
        self.assertFalse(report["valid"])
        self.assertTrue(any("closed row schema" in error for error in report["errors"]))

    def test_semantic_mutations_are_rejected_after_receipts_are_refreshed(self) -> None:
        representative = copy.deepcopy(self.frozen_density_row)
        compiler = representative["public_model"]["representative_compiler"]
        compiler["representatives"][0]["formal"] = [3, 3]
        compiler["representatives_sha256"] = VERIFIER["digest"](
            compiler["representatives"]
        )
        refresh_density_accounting(representative)
        report = VERIFIER["verify_density_row"](representative, 100000)
        self.assertFalse(report["valid"])
        self.assertIn("representative compiler mismatch", report["errors"])

        objective = copy.deepcopy(self.frozen_density_row)
        objective["private_audit"]["density_frontier"][0]["optimizer"][
            "objective_order"
        ][0:2] = ["constrained_count:min", "retained_support:max"]
        refresh_density_accounting(objective)
        report = VERIFIER["verify_density_row"](objective, 100000)
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
        report = VERIFIER["verify_density_row"](source, 100000)
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
        report = VERIFIER["verify_density_row"](unresolved, 100000)
        self.assertFalse(report["valid"])
        self.assertTrue(
            any(
                "V5 requires an exhausted exact optimizer cell" in error
                for error in report["errors"]
            )
        )

    def test_v5_exact_types_reject_json_equality_aliases(self) -> None:
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
                report = VERIFIER["verify_density_row"](mutated, 100000)
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
        report = VERIFIER["verify_density_row"](receipt, 100000)
        self.assertFalse(report["valid"])
        self.assertTrue(
            any("exact type mismatch" in error for error in report["errors"]),
            report["errors"],
        )

    def test_v5_type_checker_rejects_every_frozen_scalar_type_substitution(self) -> None:
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
            errors = VERIFIER["v5_row_type_errors"](mutated)
            self.assertTrue(errors, path)
            checked += 1
        self.assertGreater(checked, 1000)

    def test_v5_preflight_returns_invalid_receipts_for_red_team_crash_cases(self) -> None:
        mutations = []

        truncated_caps = copy.deepcopy(self.frozen_density_row)
        truncated_caps["public_model"]["constrained_budget_caps"].pop()
        refresh_density_accounting(truncated_caps)
        mutations.append(("truncated_caps", truncated_caps, "frontier length"))

        invalid_formal = copy.deepcopy(self.frozen_density_row)
        invalid_formal["public_model"]["density_frontier"][0]["selected_maxima"] = [
            [999]
        ]
        refresh_density_accounting(invalid_formal)
        mutations.append(("invalid_formal", invalid_formal, "out of range"))

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
                first = VERIFIER["verify_density_row"](mutated, 100000)
                second = VERIFIER["verify_density_row"](mutated, 100000)
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
                    "verify_v5_document_value"
                ](document, 100000)
                self.assertTrue(document_errors)
                self.assertEqual(len(document_reports), 1)
                self.assertFalse(document_reports[0]["valid"])

    def test_v5_verifier_entrypoints_are_total_with_explicit_ceilings(self) -> None:
        for maximum_nodes in (False, -1, VERIFIER["MAXIMUM_PRIMARY_NODES"] + 1):
            with self.subTest(maximum_nodes=maximum_nodes):
                row_report = VERIFIER["verify_density_row"](
                    self.frozen_density_row, maximum_nodes
                )
                self.assertFalse(row_report["valid"])
                document = MODULE["build_document"](
                    [self.frozen_density_row],
                    "frozen_fixture",
                    MODULE["frozen_parameters"](100000),
                )
                errors, reports = VERIFIER["verify_v5_document_value"](
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
            self.assertTrue(any("input load failure" in error for error in report["errors"]))

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

    def test_v5_ordering_contract_is_independently_frozen(self) -> None:
        mutated = copy.deepcopy(self.frozen_density_row)
        mutated["public_model"]["ordering_contract"]["point_labels"] = (
            "affine labels may contain leading zeroes"
        )
        refresh_density_accounting(mutated)
        report = VERIFIER["verify_density_row"](mutated, 100000)
        self.assertFalse(report["valid"])
        self.assertIn("ordering contract mismatch", report["errors"])

    def test_frozen_document_verifies_and_empty_canonical_document_is_rejected(self) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        errors, reports = VERIFIER["verify_v5_document_value"](document, 100000)
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
        errors, _ = VERIFIER["verify_v5_document_value"](empty, 100000)
        self.assertTrue(errors)
        self.assertIn("canonical row grid/order mismatch", errors)

    def test_v5_document_exact_types_are_closed(self) -> None:
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
                errors, _ = VERIFIER["verify_v5_document_value"](
                    document, 100000
                )
                self.assertTrue(errors)

    def test_document_router_uses_v5_strict_path_and_rejects_every_legacy_schema(
        self,
    ) -> None:
        document = MODULE["build_document"](
            [self.frozen_density_row],
            "frozen_fixture",
            MODULE["frozen_parameters"](100000),
        )
        verifier_globals = VERIFIER["verify_document"].__globals__
        original_load = verifier_globals["strict_load"]
        original_file_digest = verifier_globals["file_digest"]

        def route(value):
            verifier_globals["strict_load"] = lambda _: value
            verifier_globals["file_digest"] = lambda _: "0" * 64
            try:
                return VERIFIER["verify_document"](
                    Path("synthetic-document.json"), 100000
                )
            finally:
                verifier_globals["strict_load"] = original_load
                verifier_globals["file_digest"] = original_file_digest

        strict_report = route(document)
        self.assertTrue(strict_report["valid"], strict_report["errors"])
        self.assertTrue(
            any(
                "closed V5 row/document schemas" in check
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
            any("schema is not a string" in error for error in malformed_report["errors"])
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
            full_cap["retention"]["retained_to_balanced_raw"] = {
                "numerator": 1,
                "denominator": 20,
            }
        collapse_gate = VERIFIER["independent_family_gate"](collapsed)
        self.assertEqual(collapse_gate, MODULE["evaluate_family_gate"](collapsed))
        self.assertEqual(collapse_gate["status"], "FAIL")
        self.assertEqual(collapse_gate["negative_outcome"], "COLLAPSE")
        self.assertTrue(
            all(
                report["full_cap_collapse"]
                and report["full_cap_collapse_strata"] == 4
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
