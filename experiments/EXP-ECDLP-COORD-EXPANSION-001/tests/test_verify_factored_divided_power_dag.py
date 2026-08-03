from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "verify_factored_divided_power_dag.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "verify_factored_divided_power_dag_under_test", SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load divided-power DAG verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class VerifyFactoredDividedPowerDagTests(unittest.TestCase):
    def test_rebuilt_root_matches_direct_cycle(self) -> None:
        points = [(3, 6), (80, 10), (80, 87)]
        counts = MODULE.BuildCounts()
        root = MODULE.rebuild(
            points, 0, len(points), 97, 2, counts
        )
        oracle = MODULE.direct_cycle(points, 97, 2)
        self.assertEqual(
            MODULE.coefficient_payload(root.cycles[4]),
            MODULE.coefficient_payload(oracle),
        )
        self.assertTrue(
            all(
                MODULE.route_valid(
                    record.route,
                    image,
                    degree,
                    node.start,
                    node.stop,
                    points,
                    97,
                    2,
                )
                for node in MODULE.flatten(root)
                for degree, cycle in node.cycles.items()
                for image, record in cycle.items()
            )
        )

    def test_descent_replays_every_root_support_point(self) -> None:
        points = [(3, 6), (80, 10), (80, 87)]
        root = MODULE.rebuild(
            points,
            0,
            len(points),
            97,
            2,
            MODULE.BuildCounts(),
        )
        for target in root.cycles[4]:
            route = MODULE.descend(
                root,
                4,
                target,
                97,
                2,
                MODULE.QueryCounts(),
            )
            self.assertIsNotNone(route)
            assert route is not None
            self.assertTrue(
                MODULE.route_valid(
                    route,
                    target,
                    4,
                    0,
                    len(points),
                    points,
                    97,
                    2,
                )
            )

    def test_independent_d2_baseline_replays(self) -> None:
        points = [(3, 6), (80, 10), (80, 87)]
        root = MODULE.rebuild(
            points,
            0,
            len(points),
            97,
            2,
            MODULE.BuildCounts(),
        )
        positives = sorted(root.cycles[4], key=MODULE.point_key)
        baselines = MODULE.reconstruct_baselines(
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
        self.assertLessEqual(
            baselines["reduced_d2_mitm"][
                "exhaustive_worst_online_point_scans"
            ],
            baselines["reduced_d2_mitm"]["records"],
        )

    def test_rootless_descent_replays(self) -> None:
        points = [(3, 6), (80, 10), (80, 87)]
        root = MODULE.rebuild(
            points,
            0,
            len(points),
            97,
            2,
            MODULE.BuildCounts(),
        )
        target = next(iter(root.cycles[4]))
        query_root = MODULE.VerifiedNode(
            root.node_id,
            root.start,
            root.stop,
            root.left,
            root.right,
            {},
        )
        route = MODULE.descend(
            query_root,
            4,
            target,
            97,
            2,
            MODULE.QueryCounts(),
            membership_prefilter=False,
        )
        self.assertIsNotNone(route)
        assert route is not None
        self.assertTrue(
            MODULE.route_valid(
                route,
                target,
                4,
                0,
                len(points),
                points,
                97,
                2,
            )
        )


if __name__ == "__main__":
    unittest.main()
