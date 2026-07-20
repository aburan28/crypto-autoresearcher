from __future__ import annotations

import copy
import itertools
import runpy
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


class SgcpEmbedFamilyTests(unittest.TestCase):
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
                row = MODULE["build_row"](
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
        row = MODULE["build_row"](
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

    def test_main_refuses_canonical_mode(self) -> None:
        with self.assertRaises(PermissionError):
            MODULE["main"](["--output", str(DEVELOPMENT_SENTINEL)])


DEVELOPMENT_SENTINEL = (
    REPO_ROOT
    / "experiments"
    / "EXP-SGCP-EMBED-002"
    / "development"
    / "must-not-exist.json"
)


if __name__ == "__main__":
    unittest.main()
