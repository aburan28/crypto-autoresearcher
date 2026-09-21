from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = (
    Path(__file__).resolve().parents[1] / "src" / "typed_five_ec.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "typed_five_ec_under_test", SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load typed-five EC module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class TypedFiveEcTests(unittest.TestCase):
    def test_relation_coefficients_have_exact_gauge(self) -> None:
        full = MODULE.full_relation_coefficients(3, (0, 1, 1, 4), 5)
        self.assertEqual(full, [1, 3, 1, 2, 0, 0, 1])
        null = [-4, 0] + [1] * 5
        self.assertEqual(MODULE.dot_mod(full, null, 101), 0)
        quotient = MODULE.quotient_relation_coefficients(
            3, (0, 1, 1, 4), 5
        )
        self.assertEqual(quotient, [1, 3, 2, 0, 0, 1])

    def test_full_rank_solver(self) -> None:
        equations = [
            {"coefficients": [1, 0, 0], "rhs": 7},
            {"coefficients": [0, 1, 0], "rhs": 11},
            {"coefficients": [0, 0, 1], "rhs": 13},
        ]
        solution, _ = MODULE.solve_full_rank(equations, 3, 101)
        self.assertEqual(solution, [7, 11, 13])

    def test_nonzero_scalar_stream_is_a_permutation(self) -> None:
        values = list(MODULE.nonzero_scalar_stream(101, 12345))
        self.assertEqual(len(values), 100)
        self.assertEqual(set(values), set(range(1, 101)))

    def test_point_only_materialized_and_split_queries_agree(self) -> None:
        curve = MODULE.Curve(17, 2, 2)
        generator = (5, 1)
        r_points = [curve.mul(value, generator) for value in (1, 3, 7)]
        p0 = curve.mul(2, generator)
        d = curve.mul(5, generator)
        a_points = [p0]
        for _ in range(3):
            a_points.append(curve.add(a_points[-1], d))
        compiler = MODULE.compile_r_support(curve, r_points)
        target = a_points[2]
        for point in (r_points[0], r_points[1], r_points[1], r_points[2]):
            target = curve.add(target, point)
        d4 = MODULE.query_d4(
            curve,
            a_points,
            r_points,
            compiler["d4_internal"],
            target,
        )
        all_d4 = MODULE.query_d4_all(
            curve,
            a_points,
            r_points,
            compiler["d4_internal"],
            target,
        )
        split = MODULE.query_r_plus_d3(
            curve,
            a_points,
            r_points,
            compiler["d3_internal"],
            target,
        )
        self.assertTrue(d4["success"])
        self.assertTrue(all_d4["success"])
        self.assertGreaterEqual(len(all_d4["hits"]), 1)
        self.assertTrue(split["success"])

    def test_public_progression_is_distinct_and_disjoint(self) -> None:
        curve = MODULE.Curve(17, 2, 2)
        progression = MODULE.build_public_progression(
            curve, 19, 4, 12345, {(5, 1)}
        )
        points = [MODULE.point_from_json(point) for point in progression["points"]]
        self.assertEqual(len(points), len(set(points)))
        self.assertNotIn(None, points)
        self.assertNotIn((5, 1), points)
        d = MODULE.point_from_json(progression["d"])
        for index in range(1, len(points)):
            self.assertEqual(points[index], curve.add(points[index - 1], d))

    def test_tiny_generated_smoke_run(self) -> None:
        result = MODULE.run_experiment(
            bit_sizes=[8],
            seed=271828,
            families=["random_x"],
            occupancy_lambda=0.5,
            held_out_targets=8,
        )
        self.assertTrue(result["valid"])
        self.assertFalse(result["summary"]["breakthrough_claim"])
        row = result["instances"][0]["families"][0]
        self.assertEqual(
            row["relations"]["quotient_rank"],
            row["relations"]["quotient_width"],
        )
        self.assertTrue(row["diagnostic"]["quotient_solution_verified"])
        self.assertTrue(
            row["held_out_descent"]["all_supported_verified"]
        )


if __name__ == "__main__":
    unittest.main()
