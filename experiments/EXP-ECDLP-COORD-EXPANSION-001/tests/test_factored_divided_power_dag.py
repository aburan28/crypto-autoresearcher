from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "factored_divided_power_dag.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "factored_divided_power_dag_under_test", SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load divided-power DAG")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class FactoredDividedPowerDagTests(unittest.TestCase):
    def test_root_coefficients_match_canonical_oracle(self) -> None:
        points = [(3, 6), (80, 10), (80, 87)]
        counter = MODULE.BuildCounter()
        root = MODULE.build_tree(
            points, 0, len(points), 97, 2, counter
        )
        oracle = MODULE.direct_canonical(points, 97, 2)
        self.assertEqual(
            MODULE.coefficient_payload(root.cycles[4]),
            MODULE.coefficient_payload(oracle),
        )

    def test_query_returns_valid_sorted_route(self) -> None:
        points = [(3, 6), (80, 10), (80, 87)]
        root = MODULE.build_tree(
            points,
            0,
            len(points),
            97,
            2,
            MODULE.BuildCounter(),
        )
        target = next(iter(root.cycles[4]))
        route = MODULE.query(
            root,
            4,
            target,
            97,
            2,
            MODULE.QueryCounter(),
        )
        self.assertIsNotNone(route)
        assert route is not None
        self.assertEqual(tuple(sorted(route)), route)
        self.assertEqual(
            MODULE.sum_points(
                (points[index] for index in route), 97, 2
            ),
            target,
        )

    def test_reduced_d2_baseline_returns_source_route(self) -> None:
        points = [(3, 6), (80, 10), (80, 87)]
        root = MODULE.build_tree(
            points,
            0,
            len(points),
            97,
            2,
            MODULE.BuildCounter(),
        )
        positives = sorted(
            root.cycles[4], key=MODULE.point_key
        )[:4]
        baselines = MODULE.same_function_baselines(
            root.cycles[4],
            points,
            positives,
            [],
            positives,
            97,
            2,
        )
        self.assertTrue(
            baselines["reduced_d2_mitm"]["all_queries_valid"]
        )
        self.assertEqual(
            baselines["exact_support_hash"]["records"],
            len(root.cycles[4]),
        )

    def test_query_does_not_need_root_cycle(self) -> None:
        points = [(3, 6), (80, 10), (80, 87)]
        root = MODULE.build_tree(
            points,
            0,
            len(points),
            97,
            2,
            MODULE.BuildCounter(),
        )
        target = next(iter(root.cycles[4]))
        root_without_cycle = MODULE.Node(
            root.node_id,
            root.start,
            root.stop,
            root.left,
            root.right,
            {},
        )
        route = MODULE.query(
            root_without_cycle,
            4,
            target,
            97,
            2,
            MODULE.QueryCounter(),
            membership_prefilter=False,
        )
        self.assertIsNotNone(route)
        assert route is not None
        self.assertEqual(
            MODULE.sum_points(
                (points[index] for index in route), 97, 2
            ),
            target,
        )


if __name__ == "__main__":
    unittest.main()
